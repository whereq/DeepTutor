"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  BrainCircuit,
  ChevronDown,
  Database,
  Loader2,
  MessageSquare,
  PenLine,
  Sparkles,
  Terminal,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import type { StreamEvent } from "@/lib/unified-ws";

type TraceMetadata = {
  call_id?: string;
  phase?: string;
  label?: string;
  call_kind?: string;
  trace_role?: string;
  trace_group?: string;
  trace_kind?: string;
  trace_id?: string;
  call_state?: string;
  step_id?: string;
  round?: number;
  query?: string;
  tool_name?: string;
  trace_layer?: string;
  output_mode?: string;
  quality?: string;
  sources?: Array<Record<string, unknown>>;
};

type ResearchStageId = "understand" | "decompose" | "evidence" | "result";

type ResearchStageCard = {
  id: ResearchStageId;
  title: string;
  hint: string;
  events: StreamEvent[];
};

// `title` and `hint` are i18n keys resolved via `t(...)` at render time so the
// stage banner follows the active UI language instead of being locked to one.
const RESEARCH_STAGE_SPECS: Array<{
  id: ResearchStageId;
  titleKey: string;
  hintKey: string;
}> = [
  {
    id: "understand",
    titleKey: "research.stage.understand.title",
    hintKey: "research.stage.understand.hint",
  },
  {
    id: "decompose",
    titleKey: "research.stage.decompose.title",
    hintKey: "research.stage.decompose.hint",
  },
  {
    id: "evidence",
    titleKey: "research.stage.evidence.title",
    hintKey: "research.stage.evidence.hint",
  },
  {
    id: "result",
    titleKey: "research.stage.result.title",
    hintKey: "research.stage.result.hint",
  },
];

type TraceItem = { callId: string; events: StreamEvent[] };
type DisplayItem =
  | { kind: "trace"; trace: TraceItem }
  | { kind: "step"; stepId: string; traces: TraceItem[] };

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function titleCase(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function humanizeQuestionId(
  value: string,
  t?: (key: string, opts?: Record<string, unknown>) => string,
) {
  return value.replace(/\bq_(\d+)\b/gi, (_match, n) =>
    t ? t("Question {{n}}", { n }) : `Question ${n}`,
  );
}

export function getTraceMeta(event: StreamEvent): TraceMetadata {
  return (event.metadata ?? {}) as TraceMetadata;
}

function getTraceLabel(
  events: StreamEvent[],
  t?: (key: string, opts?: Record<string, unknown>) => string,
) {
  for (const event of events) {
    const meta = getTraceMeta(event);
    if (meta.label) return humanizeQuestionId(String(meta.label), t);
  }
  const fallback = events[0]?.stage || "trace";
  return humanizeQuestionId(titleCase(fallback), t);
}

function getTraceCallKind(events: StreamEvent[]) {
  for (const event of events) {
    const meta = getTraceMeta(event);
    if (meta.call_kind) return String(meta.call_kind);
  }
  return "";
}

function getTraceRole(events: StreamEvent[]) {
  for (const event of events) {
    const meta = getTraceMeta(event);
    if (meta.trace_role) return String(meta.trace_role);
  }
  return "";
}

function getTraceGroup(events: StreamEvent[]) {
  for (const event of events) {
    const meta = getTraceMeta(event);
    if (meta.trace_group) return String(meta.trace_group);
  }
  return "";
}

function getTraceDurationLabel(events: StreamEvent[]) {
  let start: number | null = null;
  let end: number | null = null;
  for (const event of events) {
    const state = String(getTraceMeta(event).call_state || "");
    if (state === "running" && start === null) start = event.timestamp;
    if ((state === "complete" || state === "error") && end === null)
      end = event.timestamp;
  }
  if (start === null || end === null) return "";
  const seconds = Math.max(1, Math.round(end - start));
  return `${seconds}s`;
}

function getTraceStartTimestamp(events: StreamEvent[]) {
  for (const event of events) {
    const state = String(getTraceMeta(event).call_state || "");
    if (state === "running") return event.timestamp;
  }
  return null;
}

function getActiveTraceDurationSeconds(
  events: StreamEvent[],
  nowSeconds: number,
) {
  const start = getTraceStartTimestamp(events);
  if (start === null) return null;
  return Math.max(1, Math.round(nowSeconds - start));
}

function isTracePending(events: StreamEvent[]) {
  let hasRunning = false;
  let hasTerminal = false;
  for (const event of events) {
    const state = String(getTraceMeta(event).call_state || "");
    if (state === "running") hasRunning = true;
    if (state === "complete" || state === "error") hasTerminal = true;
  }
  return hasRunning && !hasTerminal;
}

function getTraceHeader(
  events: StreamEvent[],
  nowSeconds?: number,
  nested?: boolean,
  t: (key: string, opts?: Record<string, unknown>) => string = (k) => k,
) {
  const label = getTraceLabel(events, t);
  const role = getTraceRole(events);
  const group = getTraceGroup(events);
  const kind = getTraceCallKind(events);
  const meta = getTraceMeta(events[0]);
  const duration =
    kind === "math_render_output" && isTracePending(events) && nowSeconds
      ? `${getActiveTraceDurationSeconds(events, nowSeconds) ?? 1}s`
      : getTraceDurationLabel(events);

  let title = label;
  if (
    [
      "math_concept_analysis",
      "math_concept_design",
      "math_code_generation",
      "math_code_retry",
      "math_summary",
      "math_render_output",
    ].includes(kind)
  ) {
    title = label;
  } else if (role === "retrieve") {
    title = t("Retrieve");
  } else if (kind === "tool_planning") {
    title = t("Tool call");
  } else if (group === "react_round") {
    if (nested) {
      title = meta.round ? t("Round {{n}}", { n: meta.round }) : label;
    } else {
      const step = meta.step_id ? t("Step {{n}}", { n: meta.step_id }) : "";
      const round = meta.round ? t("Round {{n}}", { n: meta.round }) : label;
      title = [step, round].filter(Boolean).join(" · ");
    }
  } else if (role === "plan" && kind === "llm_planning") {
    title = t("Plan");
  } else if (role === "observe" || kind === "llm_observation") {
    title = t("Observe");
  } else if (role === "response" || kind === "llm_final_response") {
    title = t("Response");
  } else if (role === "thought" || kind === "llm_reasoning") {
    title = t("Thought");
  } else if (kind === "llm_generation") {
    if (/^generate\s+/i.test(label)) {
      title = t("Generating {{label}}", {
        label: label.replace(/^generate\s+/i, ""),
      });
    } else if (/^write\s+/i.test(label)) {
      title = t("Writing {{label}}", {
        label: label.replace(/^write\s+/i, ""),
      });
    }
  }

  return duration
    ? t("{{title}} for {{duration}}", { title, duration })
    : title;
}

function getTraceText(
  events: StreamEvent[],
  eventTypes: Array<StreamEvent["type"]>,
) {
  const textEvents = events.filter(
    (event) =>
      eventTypes.includes(event.type) && event.content.trim().length > 0,
  );
  if (!textEvents.length) return "";

  const explicitOutputs = textEvents.filter(
    (event) => String(getTraceMeta(event).trace_kind || "") === "llm_output",
  );
  if (explicitOutputs.length > 0) {
    return explicitOutputs[explicitOutputs.length - 1].content;
  }

  return textEvents.map((event) => event.content).join("");
}

function formatTraceArgs(args: unknown) {
  if (args == null) return "";
  try {
    return JSON.stringify(args, null, 2);
  } catch {
    return String(args);
  }
}

/* ------------------------------------------------------------------ */
/*  Display-item grouping (step-level)                                 */
/* ------------------------------------------------------------------ */

function buildDisplayItems(traceGroups: TraceItem[]): DisplayItem[] {
  const items: DisplayItem[] = [];
  let stepId_: string | null = null;
  let stepTraces: TraceItem[] = [];

  function flushStep() {
    if (stepId_ !== null && stepTraces.length > 0) {
      items.push({ kind: "step", stepId: stepId_, traces: stepTraces });
    }
    stepId_ = null;
    stepTraces = [];
  }

  for (const group of traceGroups) {
    const meta = getTraceMeta(group.events[0]);
    const groupType = getTraceGroup(group.events);
    const stepId = meta.step_id ? String(meta.step_id) : "";
    const kind = getTraceCallKind(group.events);

    if (kind === "llm_final_response") continue;

    if (groupType === "react_round" && stepId) {
      if (stepId_ === stepId) {
        stepTraces.push(group);
      } else {
        flushStep();
        stepId_ = stepId;
        stepTraces = [group];
      }
    } else if (stepId_ !== null && kind !== "llm_generation") {
      stepTraces.push(group);
    } else {
      flushStep();
      items.push({ kind: "trace", trace: group });
    }
  }
  flushStep();
  return items;
}

function getStepGroupDuration(traces: TraceItem[]): string {
  let start: number | null = null;
  let end: number | null = null;
  for (const trace of traces) {
    for (const event of trace.events) {
      const state = String(getTraceMeta(event).call_state || "");
      if (state === "running" && (start === null || event.timestamp < start))
        start = event.timestamp;
      if (
        (state === "complete" || state === "error") &&
        (end === null || event.timestamp > end)
      )
        end = event.timestamp;
    }
  }
  if (start === null || end === null) return "";
  return `${Math.max(1, Math.round(end - start))}s`;
}

/* ------------------------------------------------------------------ */
/*  Primitive UI pieces                                                */
/* ------------------------------------------------------------------ */

function ScrollableTraceBody({
  children,
  autoScroll,
  className = "ml-5 mr-3 mt-0.5 max-h-[180px] overflow-y-auto px-3 py-1",
}: {
  children: React.ReactNode;
  autoScroll?: boolean;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true);

  useEffect(() => {
    if (!autoScroll || !stickRef.current) return;
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
  });

  useEffect(() => {
    if (autoScroll) stickRef.current = true;
  }, [autoScroll]);

  const handleScroll = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 30;
  }, []);

  return (
    <div ref={ref} onScroll={handleScroll} className={className}>
      {children}
    </div>
  );
}

/**
 * Persistently-expanded ``<details>`` wrapper. Initialises ``open`` to
 * ``true`` so the panel renders expanded from the first paint, and tracks
 * subsequent toggles purely from user clicks — we never re-close it as a
 * side-effect of the trace finishing (per product direction: all traces stay
 * open by default).
 */
function ExpandableDetails({
  summary,
  className,
  children,
}: {
  summary: ReactNode;
  className?: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(true);
  return (
    <details
      open={open}
      onToggle={(event) => setOpen((event.target as HTMLDetailsElement).open)}
      className={className}
    >
      <summary className="list-none cursor-pointer hover:text-[var(--foreground)] [&::-webkit-details-marker]:hidden">
        {summary}
      </summary>
      {children}
    </details>
  );
}

function TraceIcon({ kind, phase }: { kind: string; phase: string }) {
  const Icon =
    kind === "rag_retrieval"
      ? Database
      : kind === "llm_final_response"
        ? MessageSquare
        : kind === "llm_observation"
          ? BrainCircuit
          : kind === "llm_generation"
            ? PenLine
            : phase === "writing"
              ? PenLine
              : phase === "planning"
                ? Sparkles
                : phase === "acting"
                  ? Terminal
                  : BrainCircuit;
  return <Icon size={12} strokeWidth={1.6} className="shrink-0" />;
}

function TraceSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  if (!children) return null;
  return (
    <div className="space-y-0.5">
      <div className="not-italic text-[10px] font-semibold tracking-[0.04em] text-[var(--muted-foreground)]/70">
        {title}
      </div>
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Per-trace rendering                                                */
/* ------------------------------------------------------------------ */

function TraceRowBody({
  callId,
  callEvents,
  group,
  role,
  kind,
  t,
}: {
  callId: string;
  callEvents: StreamEvent[];
  group: string;
  role: string;
  kind: string;
  t: (key: string) => string;
}) {
  const progressEvents = callEvents.filter((event) => {
    if (event.type !== "progress") return false;
    const traceKind = String(getTraceMeta(event).trace_kind || "");
    if (traceKind === "call_status") return false;
    return event.content.trim().length > 0;
  });
  const toolEvents = callEvents.filter(
    (event) => event.type === "tool_call" || event.type === "tool_result",
  );
  const summaryProgressEvents = progressEvents.filter(
    (event) => String(getTraceMeta(event).trace_layer || "summary") !== "raw",
  );
  const rawProgressEvents = progressEvents.filter(
    (event) => String(getTraceMeta(event).trace_layer || "") === "raw",
  );
  const errorEvents = callEvents.filter(
    (event) => event.type === "error" && event.content.trim().length > 0,
  );
  const thoughtText = getTraceText(callEvents, ["thinking"]);
  const observationText = getTraceText(callEvents, ["observation"]);
  const contentText = getTraceText(callEvents, ["content"]);
  const genericBodyText =
    role === "observe"
      ? observationText
      : role === "retrieve"
        ? ""
        : thoughtText || contentText;
  const inlineSources = callEvents.flatMap(
    (event) => getTraceMeta(event).sources ?? [],
  );

  return (
    <div className="text-[11px] italic leading-[1.6] text-[var(--muted-foreground)]">
      {group === "react_round" ? (
        <div className="space-y-2">
          <TraceSection title={t("Thought")}>
            {thoughtText ? (
              <MarkdownRenderer content={thoughtText} variant="trace" />
            ) : null}
          </TraceSection>
          <TraceSection title={t("Tool")}>
            {toolEvents.length > 0 ? (
              <div className="space-y-0.5">
                {toolEvents.map((event, idx) => {
                  if (event.type === "tool_call") {
                    const formattedArgs = formatTraceArgs(event.metadata?.args);
                    return (
                      <div key={`${callId}-tool-call-${idx}`}>
                        <span className="opacity-50">→ </span>
                        <span>{event.content}</span>
                        {formattedArgs && (
                          <pre className="ml-3 mt-0.5 whitespace-pre-wrap break-words rounded-md bg-[var(--muted)] px-2 py-1 font-mono text-[10px] not-italic leading-[1.5] text-[var(--muted-foreground)]">
                            {formattedArgs}
                          </pre>
                        )}
                      </div>
                    );
                  }
                  return (
                    <div key={`${callId}-tool-result-${idx}`}>
                      <span className="opacity-50">✓ </span>
                      <span>{String(event.metadata?.tool ?? "result")}</span>
                      {event.content && (
                        <div className="ml-3 mt-0.5">
                          <MarkdownRenderer
                            content={event.content}
                            variant="trace"
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : null}
          </TraceSection>
          <TraceSection title={t("Observe")}>
            {observationText ? (
              <MarkdownRenderer content={observationText} variant="trace" />
            ) : null}
          </TraceSection>
        </div>
      ) : (
        <div className="space-y-1">
          {summaryProgressEvents.length > 0 && (
            <div className="space-y-0.5">
              {summaryProgressEvents.map((event, idx) => (
                <div key={`${callId}-progress-${idx}`} className="opacity-70">
                  {event.content}
                </div>
              ))}
            </div>
          )}

          {(role === "retrieve" || kind === "math_render_output") &&
            rawProgressEvents.length > 0 && (
              <div className="space-y-0.5">
                <div className="not-italic text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
                  {t("Raw logs")}
                </div>
                <div className="max-h-[200px] overflow-y-auto rounded-md border border-[var(--border)] bg-[#292524] px-3 py-2 font-mono text-[10px] leading-[1.55] text-[#D6D3D1] shadow-inner">
                  {rawProgressEvents.map((event, idx) => (
                    <div
                      key={`${callId}-raw-${idx}`}
                      className="whitespace-pre-wrap break-words"
                    >
                      {event.content}
                    </div>
                  ))}
                </div>
              </div>
            )}

          {toolEvents.length > 0 && (
            <div className="space-y-0.5">
              {toolEvents.map((event, idx) => {
                if (event.type === "tool_call") {
                  const formattedArgs = formatTraceArgs(event.metadata?.args);
                  return (
                    <div key={`${callId}-tool-call-${idx}`}>
                      <span className="opacity-50">→ </span>
                      <span>{event.content}</span>
                      {formattedArgs && (
                        <pre className="ml-3 mt-0.5 whitespace-pre-wrap break-words rounded-md bg-[var(--muted)] px-2 py-1 font-mono text-[10px] not-italic leading-[1.5] text-[var(--muted-foreground)]">
                          {formattedArgs}
                        </pre>
                      )}
                    </div>
                  );
                }
                return (
                  <div key={`${callId}-tool-result-${idx}`}>
                    <span className="opacity-50">✓ </span>
                    <span>{String(event.metadata?.tool ?? "result")}</span>
                    {event.content && (
                      <div className="ml-3 mt-0.5">
                        <MarkdownRenderer
                          content={event.content}
                          variant="trace"
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {genericBodyText && (
            <div className="mt-1">
              <MarkdownRenderer content={genericBodyText} variant="trace" />
            </div>
          )}
        </div>
      )}

      {inlineSources.length > 0 && (
        <div className="mt-1 opacity-50">
          {t("Sources")}:{" "}
          {inlineSources.map((source, idx) => (
            <span key={`${callId}-source-${idx}`}>
              {idx > 0 && " · "}
              {String(source.title || source.query || source.type || "source")}
            </span>
          ))}
        </div>
      )}

      {errorEvents.length > 0 && (
        <div className="mt-1 space-y-0.5">
          {errorEvents.map((event, idx) => (
            <div key={`${callId}-error-${idx}`} className="text-red-400/80">
              ✗ {event.content}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function hasExpandableContent(
  callEvents: StreamEvent[],
  group: string,
  role: string,
) {
  const progressEvents = callEvents.filter((event) => {
    if (event.type !== "progress") return false;
    const traceKind = String(getTraceMeta(event).trace_kind || "");
    if (traceKind === "call_status") return false;
    return event.content.trim().length > 0;
  });
  const toolEvents = callEvents.filter(
    (event) => event.type === "tool_call" || event.type === "tool_result",
  );
  const summaryProgressEvents = progressEvents.filter(
    (event) => String(getTraceMeta(event).trace_layer || "summary") !== "raw",
  );
  const rawProgressEvents = progressEvents.filter(
    (event) => String(getTraceMeta(event).trace_layer || "") === "raw",
  );
  const errorEvents = callEvents.filter(
    (event) => event.type === "error" && event.content.trim().length > 0,
  );
  const thoughtText = getTraceText(callEvents, ["thinking"]);
  const observationText = getTraceText(callEvents, ["observation"]);
  const contentText = getTraceText(callEvents, ["content"]);
  const genericBodyText =
    role === "observe"
      ? observationText
      : role === "retrieve"
        ? ""
        : thoughtText || contentText;
  const inlineSources = callEvents.flatMap(
    (event) => getTraceMeta(event).sources ?? [],
  );

  return (
    toolEvents.length > 0 ||
    summaryProgressEvents.length > 0 ||
    rawProgressEvents.length > 0 ||
    errorEvents.length > 0 ||
    Boolean(genericBodyText) ||
    inlineSources.length > 0 ||
    (group === "react_round" &&
      (Boolean(thoughtText) || Boolean(observationText)))
  );
}

/* ------------------------------------------------------------------ */
/*  CallTracePanel                                                     */
/* ------------------------------------------------------------------ */

export function CallTracePanel({
  events,
  isStreaming,
  nested = false,
}: {
  events: StreamEvent[];
  isStreaming?: boolean;
  // When the panel is rendered inside another shell that already supplies its
  // own framing (e.g. the auto-mode DelegationCard), pass ``nested`` to skip
  // the card wrapper so we don't end up with card-in-card visuals.
  nested?: boolean;
}) {
  const { t } = useTranslation();
  const [nowSeconds, setNowSeconds] = useState(() => Date.now() / 1000);

  // Sticky-bottom auto-scroll for the outer trace card. While the user is
  // pinned near the bottom we keep them there as new trace events stream in;
  // the moment they scroll up we release the stick so they can browse earlier
  // trace rows without being yanked back. New streaming turns re-arm the
  // stick so the next assistant response starts pinned at the bottom again.
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true);

  useEffect(() => {
    if (!isStreaming || nested || !stickRef.current) return;
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  });

  useEffect(() => {
    if (isStreaming) stickRef.current = true;
  }, [isStreaming]);

  const handleOuterScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 30;
  }, []);

  useEffect(() => {
    if (!isStreaming) return;
    const timer = window.setInterval(
      () => setNowSeconds(Date.now() / 1000),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [isStreaming]);

  const traceGroups = useMemo(() => {
    const groups: TraceItem[] = [];
    const indexById = new Map<string, number>();

    for (const event of events) {
      const callId = String(getTraceMeta(event).call_id || "");
      if (!callId) continue;
      const existingIndex = indexById.get(callId);
      if (existingIndex === undefined) {
        indexById.set(callId, groups.length);
        groups.push({ callId, events: [event] });
      } else {
        groups[existingIndex].events.push(event);
      }
    }

    return groups;
  }, [events]);

  const displayItems = useMemo(
    () => buildDisplayItems(traceGroups),
    [traceGroups],
  );

  if (!traceGroups.length) return null;

  function renderTraceRow(
    { callId, events: callEvents }: TraceItem,
    isGloballyLast: boolean,
    nested: boolean,
  ) {
    const first = callEvents[0];
    const meta = getTraceMeta(first);
    const phase = String(meta.phase || first.stage || "");
    const role = getTraceRole(callEvents);
    const group = getTraceGroup(callEvents);
    const kind = getTraceCallKind(callEvents);
    const header = getTraceHeader(callEvents, nowSeconds, nested, t);
    const active =
      Boolean(isStreaming) && isGloballyLast && isTracePending(callEvents);
    const isFinalResponse = kind === "llm_final_response";

    if (isFinalResponse) return null;

    const expandable = hasExpandableContent(callEvents, group, role);
    if (!expandable && !active) return null;

    const summaryRow = (
      <div className="flex list-none items-center gap-2 py-0.5 not-italic text-[12px] font-medium text-[var(--muted-foreground)]">
        {expandable ? (
          <ChevronDown
            size={12}
            className="shrink-0 transition-transform group-open:rotate-180"
          />
        ) : (
          // Pending row with no content yet — a faint dot preserves the
          // chevron's column width and keeps the icon + label from sliding
          // left every time a trace starts.
          <span className="flex w-3 shrink-0 items-center justify-center">
            <span className="h-[3px] w-[3px] rounded-full bg-current opacity-45" />
          </span>
        )}
        <TraceIcon kind={kind} phase={phase} />
        <span>{header}</span>
        {active && <Loader2 size={11} className="animate-spin" />}
      </div>
    );

    if (!expandable) {
      return <div key={callId}>{summaryRow}</div>;
    }

    return (
      <ExpandableDetails key={callId} className="group" summary={summaryRow}>
        {nested ? (
          <div className="ml-5 mr-3 mt-0.5 px-3 py-1">
            <TraceRowBody
              callId={callId}
              callEvents={callEvents}
              group={group}
              role={role}
              kind={kind}
              t={t}
            />
          </div>
        ) : (
          <ScrollableTraceBody autoScroll={active}>
            <TraceRowBody
              callId={callId}
              callEvents={callEvents}
              group={group}
              role={role}
              kind={kind}
              t={t}
            />
          </ScrollableTraceBody>
        )}
      </ExpandableDetails>
    );
  }

  // Cap the trace card height so a long sequence of expanded traces becomes
  // a self-contained scroll region instead of pushing the rest of the page
  // (and the composer) off-screen. Nested panels live inside their parent's
  // own scroll area, so we only constrain the standalone card.
  const rootClassName = nested
    ? "mb-3 space-y-0.5"
    : "mb-3 max-h-[240px] space-y-0.5 overflow-y-auto rounded-xl border border-[var(--border)]/50 bg-[var(--card)]/50 px-3 py-2";

  return (
    <div
      ref={nested ? undefined : scrollRef}
      onScroll={nested ? undefined : handleOuterScroll}
      className={rootClassName}
    >
      {displayItems.map((item, displayIdx) => {
        const isLastDisplayItem = displayIdx === displayItems.length - 1;

        if (item.kind === "step") {
          const roundCount = item.traces.filter(
            (tr) => getTraceGroup(tr.events) === "react_round",
          ).length;
          const lastTrace = item.traces[item.traces.length - 1];
          const isActiveStep =
            Boolean(isStreaming) &&
            isLastDisplayItem &&
            isTracePending(lastTrace.events);
          const stepDuration = isActiveStep
            ? ""
            : getStepGroupDuration(item.traces);

          return (
            <ExpandableDetails
              key={item.stepId}
              className="group/step"
              summary={
                <div className="flex items-center gap-2 py-0.5 not-italic text-[12px] font-medium text-[var(--muted-foreground)]">
                  <ChevronDown
                    size={12}
                    className="shrink-0 transition-transform group-open/step:rotate-180"
                  />
                  <Sparkles size={12} strokeWidth={1.6} className="shrink-0" />
                  <span>Step {item.stepId}</span>
                  <span className="text-[11px] opacity-60">
                    {roundCount} {roundCount === 1 ? "round" : "rounds"}
                    {stepDuration ? ` · ${stepDuration}` : ""}
                  </span>
                  {isActiveStep && (
                    <Loader2 size={11} className="animate-spin" />
                  )}
                </div>
              }
            >
              <ScrollableTraceBody
                autoScroll={isActiveStep}
                className="ml-5 mr-3 mt-0.5 max-h-[280px] overflow-y-auto px-3 py-1"
              >
                <div className="text-[11px] italic leading-[1.6] text-[var(--muted-foreground)]">
                  {item.traces.map((trace, idx) => {
                    const trGroup = getTraceGroup(trace.events);
                    const trKind = getTraceCallKind(trace.events);
                    const trRole = getTraceRole(trace.events);
                    const trMeta = getTraceMeta(trace.events[0]);

                    if (trKind === "llm_final_response") return null;

                    if (trGroup === "react_round") {
                      const roundNum = trMeta.round;
                      const duration = getTraceDurationLabel(trace.events);
                      const thoughtText = getTraceText(trace.events, [
                        "thinking",
                      ]);
                      const observationText = getTraceText(trace.events, [
                        "observation",
                      ]);
                      const traceToolEvents = trace.events.filter(
                        (e) =>
                          e.type === "tool_call" || e.type === "tool_result",
                      );
                      const isLastInStep = idx === item.traces.length - 1;
                      const roundActive =
                        Boolean(isStreaming) &&
                        isLastDisplayItem &&
                        isLastInStep &&
                        isTracePending(trace.events);

                      return (
                        <div key={trace.callId}>
                          {idx > 0 && (
                            <div className="my-1.5 h-px bg-[var(--border)]/30" />
                          )}
                          <div className="mb-1 flex items-center gap-1.5 not-italic text-[11px]">
                            <span className="font-bold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
                              Round {roundNum}
                            </span>
                            {duration && (
                              <span className="font-normal text-[var(--muted-foreground)]/40">
                                {duration}
                              </span>
                            )}
                            {roundActive && (
                              <Loader2 size={10} className="animate-spin" />
                            )}
                          </div>
                          <div className="space-y-1.5 pl-0.5">
                            <TraceSection title={t("Thought")}>
                              {thoughtText ? (
                                <MarkdownRenderer
                                  content={thoughtText}
                                  variant="trace"
                                />
                              ) : null}
                            </TraceSection>
                            <TraceSection title={t("Tool")}>
                              {traceToolEvents.length > 0 ? (
                                <div className="space-y-0.5">
                                  {traceToolEvents.map((ev, ei) => {
                                    if (ev.type === "tool_call") {
                                      const fa = formatTraceArgs(
                                        ev.metadata?.args,
                                      );
                                      return (
                                        <div key={`${trace.callId}-tc-${ei}`}>
                                          <span className="opacity-50">→ </span>
                                          <span>{ev.content}</span>
                                          {fa && (
                                            <pre className="ml-3 mt-0.5 whitespace-pre-wrap break-words rounded-md bg-[var(--muted)] px-2 py-1 font-mono text-[10px] not-italic leading-[1.5] text-[var(--muted-foreground)]">
                                              {fa}
                                            </pre>
                                          )}
                                        </div>
                                      );
                                    }
                                    return (
                                      <div key={`${trace.callId}-tr-${ei}`}>
                                        <span className="opacity-50">✓ </span>
                                        <span>
                                          {String(
                                            ev.metadata?.tool ?? "result",
                                          )}
                                        </span>
                                        {ev.content && (
                                          <div className="ml-3 mt-0.5">
                                            <MarkdownRenderer
                                              content={ev.content}
                                              variant="trace"
                                            />
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              ) : null}
                            </TraceSection>
                            <TraceSection title={t("Observe")}>
                              {observationText ? (
                                <MarkdownRenderer
                                  content={observationText}
                                  variant="trace"
                                />
                              ) : null}
                            </TraceSection>
                          </div>
                        </div>
                      );
                    }

                    /* Non-round trace (retrieve, tool, etc.) — inline within the step */
                    const inlineHeader = getTraceHeader(
                      trace.events,
                      nowSeconds,
                      true,
                      t,
                    );
                    const progressEvts = trace.events.filter(
                      (e) =>
                        e.type === "progress" &&
                        String(getTraceMeta(e).trace_kind || "") !==
                          "call_status" &&
                        e.content.trim().length > 0,
                    );
                    const rawEvts = progressEvts.filter(
                      (e) =>
                        String(getTraceMeta(e).trace_layer || "") === "raw",
                    );
                    const summaryEvts = progressEvts.filter(
                      (e) =>
                        String(getTraceMeta(e).trace_layer || "summary") !==
                        "raw",
                    );
                    const inlineToolEvts = trace.events.filter(
                      (e) => e.type === "tool_call" || e.type === "tool_result",
                    );
                    const genericText =
                      trRole === "observe"
                        ? getTraceText(trace.events, ["observation"])
                        : trRole === "retrieve"
                          ? ""
                          : getTraceText(trace.events, ["thinking"]) ||
                            getTraceText(trace.events, ["content"]);

                    const hasContent =
                      summaryEvts.length > 0 ||
                      rawEvts.length > 0 ||
                      inlineToolEvts.length > 0 ||
                      Boolean(genericText);
                    if (!hasContent) return null;

                    return (
                      <div key={trace.callId} className="mt-1.5 pl-0.5">
                        <div className="not-italic text-[11px] font-bold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
                          {inlineHeader}
                        </div>
                        <div className="mt-0.5 space-y-0.5">
                          {summaryEvts.map((ev, ei) => (
                            <div
                              key={`${trace.callId}-sp-${ei}`}
                              className="opacity-70"
                            >
                              {ev.content}
                            </div>
                          ))}
                          {(trRole === "retrieve" ||
                            trKind === "math_render_output") &&
                            rawEvts.length > 0 && (
                              <div className="max-h-[160px] overflow-y-auto rounded-md border border-[var(--border)] bg-[#292524] px-3 py-2 font-mono text-[10px] not-italic leading-[1.55] text-[#D6D3D1] shadow-inner">
                                {rawEvts.map((ev, ei) => (
                                  <div
                                    key={`${trace.callId}-rw-${ei}`}
                                    className="whitespace-pre-wrap break-words"
                                  >
                                    {ev.content}
                                  </div>
                                ))}
                              </div>
                            )}
                          {inlineToolEvts.map((ev, ei) => (
                            <div key={`${trace.callId}-it-${ei}`}>
                              <span className="opacity-50">
                                {ev.type === "tool_call" ? "→ " : "✓ "}
                              </span>
                              <span>
                                {ev.type === "tool_call"
                                  ? ev.content
                                  : String(ev.metadata?.tool ?? "result")}
                              </span>
                            </div>
                          ))}
                          {genericText && (
                            <div className="mt-0.5">
                              <MarkdownRenderer
                                content={genericText}
                                variant="trace"
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollableTraceBody>
            </ExpandableDetails>
          );
        }

        return renderTraceRow(item.trace, isLastDisplayItem, false);
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  StreamingStatus — breathing "reasoning" / "tool using" indicator   */
/* ------------------------------------------------------------------ */

type MarkProps = {
  size?: number;
  className?: string;
  strokeWidth?: number;
};

function MarkSvg({
  size = 16,
  className,
  strokeWidth = 1.5,
  children,
}: MarkProps & { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

/**
 * Reasoning — asymmetric 12-ray radial burst. Tilted ~12° so it reads as
 * hand-sketched rather than geometric; long cardinal rays + medium diagonals
 * + short accent rays in between for an organic sparkle.
 */
function ReasoningMark(props: MarkProps) {
  return (
    <MarkSvg {...props}>
      <g transform="rotate(12 12 12)">
        <path d="M12 2 L12 7.5" />
        <path d="M12 22 L12 16.5" />
        <path d="M2 12 L7.5 12" />
        <path d="M22 12 L16.5 12" />
        <path d="M4.6 4.6 L8.4 8.4" />
        <path d="M19.4 19.4 L15.6 15.6" />
        <path d="M4.2 19.8 L8.2 15.8" />
        <path d="M19.8 4.2 L15.8 8.2" />
        <path d="M7.6 2.3 L9 5.8" />
        <path d="M16.4 2.3 L15 5.8" />
        <path d="M7.6 21.7 L9 18.2" />
        <path d="M16.4 21.7 L15 18.2" />
      </g>
    </MarkSvg>
  );
}

/**
 * Tool using — an off-axis orbital motif: a soft elliptical orbit arc with
 * a small filled satellite riding it and two stray sparks. Reads as something
 * "in motion / being operated" without being a literal wrench.
 */
function ToolMark(props: MarkProps) {
  return (
    <MarkSvg {...props}>
      {/* Central node */}
      <circle cx="12" cy="13" r="2.4" />
      {/* Open orbital arc on a slight tilt */}
      <path d="M3.5 9.5 A 10.5 8 -18 0 1 20.5 14" />
      {/* Filled satellite riding the orbit */}
      <circle cx="20.5" cy="14" r="1.5" fill="currentColor" stroke="none" />
      {/* Stray accent sparks */}
      <path d="M5 19 L7.2 17.5" />
      <path d="M18 4 L19.5 6" />
    </MarkSvg>
  );
}

/**
 * Responding — a flowing ink-stroke that swoops up to the right, terminating
 * in a small dot, like a quill marking paper. Suggests "writing out an
 * answer" without being a literal pen icon.
 */
function RespondingMark(props: MarkProps) {
  return (
    <MarkSvg {...props}>
      {/* Sweeping brush curve */}
      <path d="M3 18 Q 8 7 14 11 T 21 6.5" />
      {/* Quill tip — short tick + filled dot */}
      <circle cx="21" cy="6.5" r="1.4" fill="currentColor" stroke="none" />
      {/* Ink drop accent below */}
      <circle cx="5.5" cy="20.5" r="0.9" fill="currentColor" stroke="none" />
    </MarkSvg>
  );
}

/**
 * Responded — a settled, slightly softer mark: a compact 4-ray bloom with
 * a filled inner dot. Conveys "thought captured, complete" without echoing
 * the reasoning burst.
 */
function RespondedMark(props: MarkProps) {
  return (
    <MarkSvg {...props}>
      <g transform="rotate(8 12 12)">
        {/* Inner anchor */}
        <circle cx="12" cy="12" r="1.8" fill="currentColor" stroke="none" />
        {/* 4 short cardinal rays */}
        <path d="M12 4.5 L12 8" />
        <path d="M12 19.5 L12 16" />
        <path d="M4.5 12 L8 12" />
        <path d="M19.5 12 L16 12" />
        {/* 2 longer diagonal accents — asymmetric for character */}
        <path d="M6 6 L8.6 8.6" />
        <path d="M18 18 L15.4 15.4" />
      </g>
    </MarkSvg>
  );
}

type StreamingMode = "reasoning" | "tool_using" | "responding" | "responded";

/**
 * Picks the status label shown above the trace card. We scan in reverse so a
 * tool finishing mid-turn cleanly flips the label back to reasoning for the
 * next LLM round. Final-answer streaming is detected by user-visible content
 * arriving on the assistant message itself — ``content`` is non-empty.
 */
function detectStreamingMode(
  events: StreamEvent[],
  hasFinalContent: boolean,
  isStreaming: boolean,
): StreamingMode {
  if (!isStreaming) return "responded";
  if (hasFinalContent) return "responding";
  for (let idx = events.length - 1; idx >= 0; idx -= 1) {
    const event = events[idx];
    if (event.type === "tool_result") return "reasoning";
    if (event.type === "tool_call") return "tool_using";
  }
  return "reasoning";
}

export function StreamingStatus({
  events,
  isStreaming,
  content,
  collapsible,
  expanded,
  onToggle,
}: {
  events: StreamEvent[];
  isStreaming?: boolean;
  content?: string;
  // When set, the status row becomes a clickable toggle for the trace card
  // sibling below. ``expanded`` controls the chevron rotation.
  collapsible?: boolean;
  expanded?: boolean;
  onToggle?: () => void;
}) {
  const { t } = useTranslation();
  const hasFinalContent = Boolean(content && content.trim().length > 0);
  // Only render once we either have a streaming turn OR a completed turn that
  // produced visible content — empty placeholders (e.g. system message
  // shells) shouldn't show a status row.
  if (!isStreaming && !hasFinalContent) return null;
  const mode = detectStreamingMode(
    events,
    hasFinalContent,
    Boolean(isStreaming),
  );

  const label =
    mode === "tool_using"
      ? t("Tool using…")
      : mode === "responding"
        ? t("DeepTutor responding…")
        : mode === "responded"
          ? t("DeepTutor responded.")
          : t("DeepTutor reasoning…");
  // Static label after the answer is done — no breathing animation. The other
  // three states are live so they pulse to signal ongoing work. The icon also
  // stretches/contracts on its own cycle (out of phase with the opacity fade)
  // so the mark feels alive rather than just dimming with the label.
  const breathingClass = mode === "responded" ? "" : "dt-breathing-text";
  const markPulseClass = mode === "responded" ? "" : "dt-mark-pulse";
  const textColor =
    mode === "responded"
      ? "text-[var(--muted-foreground)]/70"
      : "text-[var(--muted-foreground)]";
  const Mark =
    mode === "tool_using"
      ? ToolMark
      : mode === "responding"
        ? RespondingMark
        : mode === "responded"
          ? RespondedMark
          : ReasoningMark;

  const rowContent = (
    <>
      <Mark
        size={22}
        strokeWidth={1.5}
        className={`${breathingClass} ${markPulseClass} shrink-0 text-[var(--primary)]/90`}
      />
      <span className={breathingClass}>{label}</span>
      {collapsible ? (
        <ChevronDown
          size={14}
          strokeWidth={2}
          className={`ml-1 shrink-0 opacity-60 transition-transform ${
            expanded ? "" : "-rotate-90"
          }`}
        />
      ) : null}
    </>
  );

  if (collapsible && onToggle) {
    return (
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={expanded ? "true" : "false"}
        className={`mb-3 -ml-1 flex items-center gap-2.5 rounded-md px-1 py-0.5 text-[14px] font-semibold leading-none transition-colors hover:bg-[var(--muted)]/40 ${textColor}`}
      >
        {rowContent}
      </button>
    );
  }

  return (
    <div
      className={`mb-3 flex items-center gap-2.5 text-[14px] font-semibold leading-none ${textColor}`}
    >
      {rowContent}
    </div>
  );
}

/**
 * Combined surface that renders the streaming-status row above a collapsible
 * trace card. The chevron on the status row folds the card while leaving the
 * status itself (and the assistant response below it) untouched. Defaults to
 * open per product direction; user toggles persist across event updates.
 */
export function TraceSurface({
  events,
  isStreaming,
  content,
}: {
  events: StreamEvent[];
  isStreaming?: boolean;
  content?: string;
}) {
  const hasCallTrace = useMemo(
    () => events.some((event) => Boolean(event.metadata?.call_id)),
    [events],
  );
  const [expanded, setExpanded] = useState(true);
  const toggle = useCallback(() => setExpanded((prev) => !prev), []);

  return (
    <>
      <StreamingStatus
        events={events}
        isStreaming={isStreaming}
        content={content}
        collapsible={hasCallTrace}
        expanded={expanded}
        onToggle={toggle}
      />
      {hasCallTrace && expanded ? (
        <CallTracePanel events={events} isStreaming={isStreaming} />
      ) : null}
    </>
  );
}

/* ------------------------------------------------------------------ */
/*  ResearchStagePanel                                                 */
/* ------------------------------------------------------------------ */

function getResearchStageId(event: StreamEvent): ResearchStageCard["id"] {
  const meta = getTraceMeta(event);
  const explicitStage = String(
    (event.metadata as Record<string, unknown> | undefined)
      ?.research_stage_card || "",
  );
  if (
    explicitStage === "understand" ||
    explicitStage === "decompose" ||
    explicitStage === "evidence" ||
    explicitStage === "result"
  ) {
    return explicitStage;
  }
  const stage = String(event.stage || meta.phase || "");
  const text = String(event.content || "").toLowerCase();
  const agent = String(
    (event.metadata as Record<string, unknown> | undefined)?.agent_name || "",
  );

  if (stage === "reporting") return "result";
  if (stage === "decomposing" || agent === "decompose_agent")
    return "decompose";
  if (stage === "rephrasing" || agent === "rephrase_agent") return "understand";
  if (stage === "planning") {
    if (text.includes("decompose") || text.includes("queue"))
      return "decompose";
    return "understand";
  }
  return "evidence";
}

function formatResearchStageSummary(events: StreamEvent[], fallback: string) {
  const progressEvents = events.filter(
    (event) => event.type === "progress" && event.content.trim().length > 0,
  );
  const lastProgress = progressEvents.at(-1)?.content.trim();
  if (lastProgress) {
    return humanizeQuestionId(titleCase(lastProgress.replaceAll("-", "_")));
  }

  const thought = getTraceText(events, ["thinking"]);
  if (thought) return thought.slice(0, 120);

  const content = getTraceText(events, ["content"]);
  if (content) return content.slice(0, 120);

  return fallback;
}

export function ResearchStagePanel({
  events,
  isStreaming,
}: {
  events: StreamEvent[];
  isStreaming?: boolean;
}) {
  const { t } = useTranslation();
  const cards = useMemo<ResearchStageCard[]>(() => {
    return RESEARCH_STAGE_SPECS.map((spec) => ({
      id: spec.id,
      title: t(spec.titleKey),
      hint: t(spec.hintKey),
      events: events.filter((event) => getResearchStageId(event) === spec.id),
    })).filter((card) => card.events.length > 0);
  }, [events, t]);

  if (!cards.length) return null;

  return (
    <div className="mb-3 space-y-0.5">
      {cards.map((card, index) => {
        const hasTrace = card.events.some((event) =>
          Boolean(getTraceMeta(event).call_id),
        );
        const active =
          Boolean(isStreaming) &&
          index === cards.length - 1 &&
          card.events.some(
            (event) => isTracePending([event]) || event.type === "progress",
          );
        const summary = formatResearchStageSummary(card.events, card.hint);

        return (
          <div key={card.id}>
            <div className="flex items-center gap-2 py-1 text-[12px] text-[var(--muted-foreground)]">
              <span className="font-semibold">{card.title}</span>
              <span className="text-[11px] opacity-60">{summary}</span>
              {active && (
                <Loader2
                  size={11}
                  className="animate-spin text-[var(--primary)]"
                />
              )}
            </div>
            {hasTrace ? (
              <CallTracePanel events={card.events} isStreaming={isStreaming} />
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
