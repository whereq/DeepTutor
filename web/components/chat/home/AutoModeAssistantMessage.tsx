"use client";

import dynamic from "next/dynamic";
import { memo, useMemo } from "react";
import {
  ChevronRight,
  CircleCheck,
  CircleX,
  Loader2,
  RotateCcw,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import AssistantResponse from "@/components/common/AssistantResponse";
import { extractMathAnimatorResult } from "@/lib/math-animator-types";
import { extractQuizQuestions } from "@/lib/quiz-types";
import type { StreamEvent } from "@/lib/unified-ws";
import { extractVisualizeResult } from "@/lib/visualize-types";
import AutoErrorBlock from "./AutoErrorBlock";
import { CallTracePanel } from "./TracePanels";

const MathAnimatorViewer = dynamic(
  () => import("@/components/math-animator/MathAnimatorViewer"),
  { ssr: false },
);
const QuizViewer = dynamic(() => import("@/components/quiz/QuizViewer"), {
  ssr: false,
});
const VisualizationViewer = dynamic(
  () => import("@/components/visualize/VisualizationViewer"),
  { ssr: false },
);

/* -------------------------------------------------------------------------- */
/* Event partitioning                                                           */
/* -------------------------------------------------------------------------- */

/**
 * Layout block as it appears in the rendered message, top to bottom.
 *
 * Auto turns interleave three streams of events on the wire:
 *  - Top-level THINKING (router reasoning before/between/after delegations)
 *  - Sub-capability events (everything with a ``parent_call_id`` from the
 *    delegation forwarder)
 *  - Auto's final CONTENT and RESULT (no ``parent_call_id``)
 *
 * The frontend renders them as:
 *  - Inline ``thought`` blocks between collapsible delegation cards
 *  - Collapsible ``delegation`` cards (one per sub-capability invocation)
 *  - A prominent final synthesis block at the bottom
 *  - An ``AutoErrorBlock`` if the turn ended in a terminal failure
 */

type Block =
  | { kind: "thought"; text: string }
  | {
      kind: "delegation";
      callId: string;
      capability: string;
      events: StreamEvent[];
    }
  | { kind: "final"; text: string };

/**
 * ``trace_kind``s we treat as internal retry / pivot markers, NOT as
 * user-visible errors. Anything else surfaces in the error list so a
 * silent backend failure (orchestrator-level exception, etc.) can't leave
 * the chat stuck on an empty user bubble.
 */
const TRANSIENT_ERROR_TRACE_KINDS = new Set([
  "router_api_error",
  "router_format_error",
  "delegation_retry",
  "same_cap_exhausted",
  "validation_error",
  "atomic_tool_error",
]);

interface PartitionResult {
  blocks: Block[];
  terminalError: {
    failureReason: string;
    failureMessage: string;
    iteration?: number;
    routerRetries?: number;
  } | null;
  /** Non-terminal top-level error messages (e.g. an uncaught capability
   *  exception bubbled up by the orchestrator). Always rendered. */
  surfacedErrors: string[];
  /** True while events for a delegation are still arriving. */
  hasOpenDelegation: boolean;
}

function partitionEvents(events: StreamEvent[]): PartitionResult {
  const blocks: Block[] = [];
  let terminalError: PartitionResult["terminalError"] = null;
  const surfacedErrors: string[] = [];
  let routerRetries = 0;
  const knownDelegations = new Map<string, Block & { kind: "delegation" }>();
  let openDelegationId: string | null = null;
  let thoughtBuffer: string[] = [];

  const flushThought = () => {
    if (thoughtBuffer.length === 0) return;
    const text = thoughtBuffer.join("").trim();
    thoughtBuffer = [];
    if (text) blocks.push({ kind: "thought", text });
  };

  for (const event of events) {
    const meta = event.metadata ?? {};
    const parentCallId = meta.parent_call_id as string | undefined;

    // Sub-capability event: route into its delegation card.
    if (parentCallId) {
      flushThought();
      let card = knownDelegations.get(parentCallId);
      if (!card) {
        const capName = (meta.delegated_capability as string | undefined) ?? "";
        card = {
          kind: "delegation",
          callId: parentCallId,
          capability: capName,
          events: [],
        };
        knownDelegations.set(parentCallId, card);
        blocks.push(card);
        openDelegationId = parentCallId;
      }
      card.events.push(event);
      // A RESULT event signals the delegation finished.
      if (event.type === "result") {
        openDelegationId = null;
      }
      continue;
    }

    // Top-level event.
    if (event.type === "error" && meta.terminal === true) {
      terminalError = {
        failureReason: String(meta.failure_reason ?? "unknown"),
        failureMessage: event.content || "",
        iteration: meta.iteration as number | undefined,
        routerRetries,
      };
      continue;
    }

    if (event.type === "error") {
      // Router retry counters live in error metadata on transient failures.
      if (
        typeof meta.retry_count === "number" &&
        meta.trace_kind === "router_api_error"
      ) {
        routerRetries = Math.max(routerRetries, meta.retry_count as number);
      }
      // Any error that is NOT an expected internal retry/pivot marker must be
      // surfaced — otherwise an uncaught backend exception (or a misconfigured
      // LLM) leaves the user staring at a silent chat bubble forever.
      const traceKind = typeof meta.trace_kind === "string" ? meta.trace_kind : "";
      if (!traceKind || !TRANSIENT_ERROR_TRACE_KINDS.has(traceKind)) {
        const msg = (event.content || "").trim();
        if (msg) surfacedErrors.push(msg);
      }
      continue;
    }

    // Auto's final synthesis CONTENT (with call_kind="llm_final_response").
    if (
      event.type === "content" &&
      meta.call_kind === "llm_final_response"
    ) {
      flushThought();
      const text = event.content || "";
      if (text) blocks.push({ kind: "final", text });
      continue;
    }

    // Inline thinking / observation text that should appear between blocks.
    // We deliberately skip ``stage === "synthesizing"`` events: the
    // synthesizer streams its chunks as THINKING for live-progress UX, but
    // the same text is then emitted as the prominent final CONTENT block
    // immediately after. Without this skip the user sees the synthesis twice
    // (once muted/italic, once prominent).
    if (event.type === "thinking" || event.type === "observation") {
      if (event.stage === "synthesizing") continue;
      const text = event.content || "";
      if (text) thoughtBuffer.push(text);
      continue;
    }
    // Other top-level event types (progress, stage markers) are silent for the
    // user-facing layout but still useful for CallTracePanel debugging — we
    // don't render them here.
  }
  flushThought();

  if (terminalError) {
    terminalError.routerRetries = routerRetries;
  }

  return {
    blocks,
    terminalError,
    surfacedErrors,
    hasOpenDelegation: openDelegationId !== null,
  };
}

/* -------------------------------------------------------------------------- */
/* Delegation card                                                              */
/* -------------------------------------------------------------------------- */

interface DelegationCardProps {
  capability: string;
  events: StreamEvent[];
  isStreaming?: boolean;
  sessionId?: string | null;
  language?: string;
}

function delegationStatus(events: StreamEvent[]): {
  label: "running" | "success" | "failed" | "retried";
  icon: LucideIcon;
  className: string;
} {
  const hasError = events.some((e) => e.type === "error");
  const hasResult = events.some((e) => e.type === "result");
  const hasRetry = events.some(
    (e) => e.metadata?.trace_kind === "delegation_retry",
  );
  if (!hasResult && !hasError) {
    return { label: "running", icon: Loader2, className: "text-amber-500 animate-spin" };
  }
  if (hasResult && !hasError) {
    return { label: "success", icon: CircleCheck, className: "text-emerald-500" };
  }
  if (hasResult && hasRetry) {
    return { label: "retried", icon: RotateCcw, className: "text-amber-500" };
  }
  return { label: "failed", icon: CircleX, className: "text-red-500" };
}

const DelegationCard = memo(function DelegationCard({
  capability,
  events,
  isStreaming,
  sessionId,
  language,
}: DelegationCardProps) {
  const { t } = useTranslation();
  const status = delegationStatus(events);
  const StatusIcon = status.icon;

  // The final RESULT event holds the rich payload we feed the per-capability
  // viewer. We render the typed viewer (QuizViewer / MathAnimatorViewer / ...)
  // inside the collapsed panel so the user can inspect the actual output.
  const resultEvent = useMemo(
    () => events.find((e) => e.type === "result") ?? null,
    [events],
  );

  const quizQuestions = useMemo(() => {
    if (capability !== "deep_question" || !resultEvent) return null;
    return extractQuizQuestions(resultEvent.metadata);
  }, [capability, resultEvent]);
  const mathAnimatorResult = useMemo(() => {
    if (capability !== "math_animator" || !resultEvent) return null;
    return extractMathAnimatorResult(resultEvent.metadata);
  }, [capability, resultEvent]);
  const visualizeResult = useMemo(() => {
    if (capability !== "visualize" || !resultEvent) return null;
    return extractVisualizeResult(resultEvent.metadata);
  }, [capability, resultEvent]);

  // Markdown content from sub-capabilities that ship a final ``response``
  // string (deep_solve, deep_research) is rendered as plain assistant text.
  const markdownContent = useMemo(() => {
    if (!resultEvent) return "";
    if (quizQuestions || mathAnimatorResult || visualizeResult) return "";
    const meta = resultEvent.metadata as Record<string, unknown> | undefined;
    const response = meta?.response;
    return typeof response === "string" ? response : "";
  }, [resultEvent, quizQuestions, mathAnimatorResult, visualizeResult]);

  // Only the sub-capability's *internal* progress/thinking events belong in
  // the trace panel. CONTENT and RESULT are the user-facing payload — they
  // already render via the dedicated viewer / markdown below. Including them
  // would cause big code blocks to appear twice (once in the trace card, once
  // in the viewer).
  const traceableEvents = useMemo(
    () =>
      events.filter(
        (e) => e.type !== "content" && e.type !== "result",
      ),
    [events],
  );
  const hasNestedTrace = useMemo(
    () => traceableEvents.some((e) => Boolean(e.metadata?.call_id)),
    [traceableEvents],
  );

  return (
    <details
      // ``open`` defaults to false (collapsed). User clicks the summary to
      // expand. We do NOT auto-open while streaming so the chat stays compact.
      className="group mt-2 rounded-lg border border-[var(--border)]/55 bg-[var(--muted)]/30 transition-colors"
    >
      <summary className="flex cursor-pointer items-center gap-2 px-3 py-2 text-[12px] text-[var(--foreground)] outline-none [&::-webkit-details-marker]:hidden">
        <ChevronRight
          size={12}
          strokeWidth={2}
          className="shrink-0 text-[var(--muted-foreground)] transition-transform group-open:rotate-90"
        />
        <StatusIcon size={13} strokeWidth={1.8} className={status.className} />
        <span className="font-medium">{capability || t("(unknown)")}</span>
        <span className="text-[11px] text-[var(--muted-foreground)]">
          {status.label === "running"
            ? t("running…")
            : status.label === "retried"
            ? t("retried")
            : status.label === "failed"
            ? t("failed")
            : t("done")}
        </span>
      </summary>
      <div className="space-y-2 border-t border-[var(--border)]/40 px-3 py-3">
        {/* Sub-capability's internal trace (planning / reasoning / writing /
            tool calls / etc.). Rendered with ``nested`` so it doesn't clash
            with the parent shell. This is where the user can drill into the
            sub-capability's progress instead of seeing it scattered at the
            top of the auto turn. */}
        {hasNestedTrace ? (
          <CallTracePanel
            events={traceableEvents}
            isStreaming={isStreaming}
            nested
          />
        ) : null}

        {/* The sub-capability's final user-facing output. Typed viewer when
            we recognize the result shape, otherwise plain markdown. */}
        {quizQuestions && quizQuestions.length > 0 ? (
          <QuizViewer
            questions={quizQuestions}
            sessionId={sessionId}
            language={language}
          />
        ) : mathAnimatorResult ? (
          <MathAnimatorViewer result={mathAnimatorResult} />
        ) : visualizeResult ? (
          <VisualizationViewer result={visualizeResult} />
        ) : markdownContent ? (
          <AssistantResponse content={markdownContent} />
        ) : isStreaming ? (
          <div className="text-[12px] text-[var(--muted-foreground)]">
            {t("Working…")}
          </div>
        ) : null}
      </div>
    </details>
  );
});

DelegationCard.displayName = "DelegationCard";

/* -------------------------------------------------------------------------- */
/* AutoModeAssistantMessage                                                     */
/* -------------------------------------------------------------------------- */

interface AutoModeAssistantMessageProps {
  msg: { content: string; capability?: string; events?: StreamEvent[] };
  isStreaming?: boolean;
  sessionId?: string | null;
  language?: string;
  onRetry?: () => void;
  onSwitchToManual?: () => void;
}

const AutoModeAssistantMessage = memo(function AutoModeAssistantMessage({
  msg,
  isStreaming,
  sessionId,
  language,
  onRetry,
  onSwitchToManual,
}: AutoModeAssistantMessageProps) {
  const { t } = useTranslation();
  const events = useMemo(() => msg.events ?? [], [msg.events]);
  const partition = useMemo(() => partitionEvents(events), [events]);

  return (
    <div className="space-y-1.5">
      {partition.blocks.map((block, idx) => {
        if (block.kind === "thought") {
          // Inline reasoning between delegations. Use a subtle left accent
          // instead of a boxed/italic treatment so it reads as prose, not
          // as a trace-metadata chunk.
          return (
            <div
              key={`t-${idx}`}
              className="whitespace-pre-wrap border-l-2 border-[var(--primary)]/25 pl-3 py-0.5 text-[13px] leading-relaxed text-[var(--muted-foreground)]"
            >
              {block.text}
            </div>
          );
        }
        if (block.kind === "delegation") {
          return (
            <DelegationCard
              key={block.callId}
              capability={block.capability}
              events={block.events}
              isStreaming={isStreaming && partition.hasOpenDelegation}
              sessionId={sessionId}
              language={language}
            />
          );
        }
        // Final synthesis — rendered prominently as the canonical reply.
        return <AssistantResponse key={`f-${idx}`} content={block.text} />;
      })}

      {/* Non-terminal but user-visible errors (typically an uncaught
          orchestrator exception). Don't suppress these — without them the
          user sees nothing when the backend fails silently. */}
      {partition.surfacedErrors.length > 0 ? (
        <div className="space-y-1.5">
          {partition.surfacedErrors.map((msg, idx) => (
            <div
              key={`err-${idx}`}
              className="whitespace-pre-wrap rounded-md border border-red-300/60 bg-red-50/60 px-3 py-2 text-[12.5px] text-red-700 dark:border-red-500/40 dark:bg-red-950/30 dark:text-red-200"
            >
              ✗ {msg}
            </div>
          ))}
        </div>
      ) : null}

      {/* Streaming placeholder: while the turn is in flight but the backend
          has not emitted anything user-visible yet, render a subtle
          "thinking" dot so the message bubble doesn't look frozen. */}
      {isStreaming &&
      partition.blocks.length === 0 &&
      partition.surfacedErrors.length === 0 &&
      !partition.terminalError ? (
        <div className="flex items-center gap-2 px-3 py-2 text-[12.5px] text-[var(--muted-foreground)]">
          <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-[var(--primary)]/60" />
          <span>{t("Thinking…")}</span>
        </div>
      ) : null}

      {partition.terminalError ? (
        <AutoErrorBlock
          reason={partition.terminalError.failureReason}
          failureMessage={partition.terminalError.failureMessage}
          iteration={partition.terminalError.iteration}
          routerRetries={partition.terminalError.routerRetries}
          onRetry={onRetry}
          onSwitchToManual={onSwitchToManual}
        />
      ) : null}
    </div>
  );
});

AutoModeAssistantMessage.displayName = "AutoModeAssistantMessage";

export default AutoModeAssistantMessage;
