"use client";

import { memo, useMemo } from "react";
import Image from "next/image";
import {
  BookOpen,
  Copy,
  MessageSquare,
  RotateCcw,
  Square,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import type { SelectedHistorySession } from "@/components/chat/HistorySessionPicker";
import AssistantResponse from "@/components/common/AssistantResponse";
import MathAnimatorViewer from "@/components/math-animator/MathAnimatorViewer";
import QuizViewer from "@/components/quiz/QuizViewer";
import type { MessageRequestSnapshot } from "@/context/UnifiedChatContext";
import { extractMathAnimatorResult } from "@/lib/math-animator-types";
import { extractQuizQuestions } from "@/lib/quiz-types";
import type { StreamEvent } from "@/lib/unified-ws";
import { hasVisibleMarkdownContent } from "@/lib/markdown-display";
import { CallTracePanel, ResearchStagePanel } from "./TracePanels";

interface ChatMessageItem {
  role: "user" | "assistant" | "system";
  content: string;
  capability?: string;
  events?: StreamEvent[];
  attachments?: Array<{
    type: string;
    filename?: string;
    base64?: string;
  }>;
  requestSnapshot?: MessageRequestSnapshot;
}

interface NotebookReferenceGroup {
  notebookId: string;
  notebookName: string;
  count: number;
}

function getModeBadgeLabel(capability?: string | null) {
  if (!capability || capability === "chat") return "Chat";
  if (capability === "deep_solve") return "Deep Solve";
  if (capability === "deep_question") return "Quiz Generation";
  if (capability === "deep_research") return "Deep Research";
  if (capability === "math_animator") return "Math Animator";
  return capability;
}

const AssistantMessage = memo(function AssistantMessage({
  msg,
  isStreaming,
  sessionId,
  language,
}: {
  msg: { content: string; capability?: string; events?: StreamEvent[] };
  isStreaming?: boolean;
  sessionId?: string | null;
  language?: string;
}) {
  const events = useMemo(() => msg.events ?? [], [msg.events]);
  const hasCallTrace = useMemo(
    () => events.some((event) => Boolean(event.metadata?.call_id)),
    [events],
  );
  const hasResearchTrace = msg.capability === "deep_research" && events.length > 0;

  const quizQuestions = useMemo(() => {
    const resultEv = msg.events?.find((e) => e.type === "result");
    if (!resultEv) return null;
    return extractQuizQuestions(resultEv.metadata);
  }, [msg.events]);
  const mathAnimatorResult = useMemo(() => {
    const resultEv = msg.events?.find((e) => e.type === "result");
    if (!resultEv) return null;
    return extractMathAnimatorResult(resultEv.metadata);
  }, [msg.events]);

  return (
    <>
      {hasResearchTrace ? (
        <ResearchStagePanel events={events} isStreaming={isStreaming} />
      ) : hasCallTrace ? (
        <CallTracePanel events={events} isStreaming={isStreaming} />
      ) : null}
      {mathAnimatorResult ? <MathAnimatorViewer result={mathAnimatorResult} /> : null}
      {quizQuestions && quizQuestions.length > 0 ? (
        <QuizViewer questions={quizQuestions} sessionId={sessionId} language={language} />
      ) : (
        <AssistantResponse content={msg.content} />
      )}
    </>
  );
});

AssistantMessage.displayName = "AssistantMessage";

function RoughActionButton({
  icon: Icon,
  label,
  onClick,
  disabled,
}: {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-1 px-0.5 py-0.5 text-[11px] text-[var(--muted-foreground)]/45 transition-colors hover:text-[var(--foreground)] disabled:cursor-not-allowed disabled:opacity-35"
    >
      <Icon size={11} strokeWidth={1.5} />
      <span>{label}</span>
    </button>
  );
}

export function ReferenceChips({
  historySessions,
  notebookGroups,
  onRemoveHistory,
  onRemoveNotebook,
}: {
  historySessions: SelectedHistorySession[];
  notebookGroups: NotebookReferenceGroup[];
  onRemoveHistory: (sessionId: string) => void;
  onRemoveNotebook: (notebookId: string) => void;
}) {
  const { t } = useTranslation();
  if (historySessions.length === 0 && notebookGroups.length === 0) return null;

  return (
    <div className="mb-3 flex flex-wrap gap-2">
      {historySessions.map((session) => (
        <span
          key={session.sessionId}
          className="inline-flex max-w-full items-center gap-2 rounded-xl border border-sky-200 bg-sky-50 px-3 py-1.5 text-[12px] text-sky-800 shadow-sm dark:border-sky-900/60 dark:bg-sky-950/30 dark:text-sky-200"
        >
          <MessageSquare size={12} strokeWidth={1.8} className="shrink-0" />
          <span className="shrink-0 font-medium">{t("Chat History")}</span>
          <span className="truncate text-sky-700/90 dark:text-sky-200/90">{session.title}</span>
          <button
            onClick={() => onRemoveHistory(session.sessionId)}
            className="shrink-0 opacity-60 transition hover:opacity-100"
          >
            <X size={12} />
          </button>
        </span>
      ))}
      {notebookGroups.map((group) => (
        <span
          key={group.notebookId}
          className="inline-flex max-w-full items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-[12px] text-[var(--foreground)] shadow-sm"
        >
          <BookOpen size={12} strokeWidth={1.8} className="shrink-0" />
          <span className="shrink-0 font-medium">{t("Notebook")}</span>
          <span className="truncate text-[var(--muted-foreground)]">
            {group.notebookName} ({group.count})
          </span>
          <button
            onClick={() => onRemoveNotebook(group.notebookId)}
            className="shrink-0 opacity-60 transition hover:opacity-100"
          >
            <X size={12} />
          </button>
        </span>
      ))}
    </div>
  );
}

export function ChatMessageList({
  messages,
  isStreaming,
  activeUserIndex,
  activeAssistantMessage,
  sessionId,
  language,
  onCancelStreaming,
  onAnswerNow,
  onCopyAssistantMessage,
  onRetryMessage,
}: {
  messages: ChatMessageItem[];
  isStreaming: boolean;
  activeUserIndex: number;
  activeAssistantMessage: ChatMessageItem | null;
  sessionId?: string | null;
  language?: string;
  onCancelStreaming: () => void;
  onAnswerNow: (
    snapshot?: MessageRequestSnapshot,
    assistantMsg?: { content: string; events?: StreamEvent[] },
  ) => void;
  onCopyAssistantMessage: (content: string) => void | Promise<void>;
  onRetryMessage: (snapshot?: MessageRequestSnapshot) => void;
}) {
  const { t } = useTranslation();
  const messageRows = useMemo(() => {
    return messages.map((msg, index) => {
      if (msg.role === "user") {
        return { msg, pairedUserMessage: null as ChatMessageItem | null };
      }
      const pairedUserMessage =
        [...messages.slice(0, index)].reverse().find((previous) => previous.role === "user") ?? null;
      return { msg, pairedUserMessage };
    });
  }, [messages]);

  return (
    <>
      {messageRows.map(({ msg, pairedUserMessage }, i) => {
        if (msg.role === "user") {
          const showInlineControls =
            i === activeUserIndex &&
            (!msg.capability || msg.capability === "chat") &&
            Boolean(msg.requestSnapshot) &&
            activeAssistantMessage?.role === "assistant";
          return (
            <div key={`${msg.role}-${i}`} className="flex justify-end">
              <div className="max-w-[75%] space-y-1.5">
                <div className="flex justify-end pr-1">
                  <span className="text-[10px] tracking-wide text-[var(--muted-foreground)]/40">
                    {getModeBadgeLabel(msg.capability)}
                  </span>
                </div>
                {msg.attachments?.some((a) => a.type === "image") && (
                  <div className="flex flex-wrap justify-end gap-2">
                    {msg.attachments
                      .filter((a) => a.type === "image" && a.base64)
                      .map((a, ai) => (
                        <div key={`img-${ai}`} className="overflow-hidden rounded-2xl border border-[var(--border)]">
                          <Image
                            src={`data:image/png;base64,${a.base64}`}
                            alt={a.filename || t("image")}
                            width={280}
                            height={192}
                            unoptimized
                            className="max-h-48 max-w-[280px] rounded-2xl object-contain"
                          />
                        </div>
                      ))}
                  </div>
                )}
                <div className="rounded-2xl rounded-br-lg bg-[var(--primary)] px-4 py-2.5 text-[14px] leading-relaxed text-white shadow-sm">
                  {(() => {
                    const snap = msg.requestSnapshot;
                    const hasNotebook = Boolean(snap?.notebookReferences?.length);
                    const hasHistory = Boolean(snap?.historyReferences?.length);
                    if (!hasNotebook && !hasHistory) return null;
                    return (
                      <div className="mb-2 flex flex-wrap gap-1.5">
                        {snap?.notebookReferences?.map((ref) => (
                          <span
                            key={ref.notebook_id}
                            className="inline-flex items-center gap-1.5 rounded-md border border-white/18 bg-white/12 px-2 py-1 text-[11px] font-medium text-white"
                          >
                            <BookOpen size={11} strokeWidth={1.8} />
                            {t("Notebook")} · {ref.record_ids.length} {t("records")}
                          </span>
                        ))}
                        {snap?.historyReferences?.map((sid) => (
                          <span
                            key={sid}
                            className="inline-flex items-center gap-1.5 rounded-md border border-white/18 bg-white/12 px-2 py-1 text-[11px] font-medium text-white"
                          >
                            <MessageSquare size={11} strokeWidth={1.8} />
                            {t("Chat History")}
                          </span>
                        ))}
                      </div>
                    );
                  })()}
                  <div>{msg.content}</div>
                </div>
                {showInlineControls ? (
                  <div className="flex justify-end gap-2">
                    <RoughActionButton
                      icon={Square}
                      label="Stop"
                      onClick={onCancelStreaming}
                    />
                    <RoughActionButton
                      icon={Zap}
                      label="Answer now"
                      onClick={() =>
                        onAnswerNow(
                          msg.requestSnapshot,
                          activeAssistantMessage?.role === "assistant"
                            ? {
                                content: activeAssistantMessage.content,
                                events: activeAssistantMessage.events,
                              }
                            : undefined,
                        )
                      }
                    />
                  </div>
                ) : null}
              </div>
            </div>
          );
        }

        const showAssistantActions =
          !isStreaming &&
          (!pairedUserMessage?.capability || pairedUserMessage?.capability === "chat") &&
          Boolean(pairedUserMessage?.requestSnapshot) &&
          hasVisibleMarkdownContent(msg.content);
        return (
          <div key={`${msg.role}-${i}`} className="w-full">
            <AssistantMessage
              msg={msg}
              isStreaming={isStreaming && i === messages.length - 1}
              sessionId={sessionId}
              language={language}
            />
            {showAssistantActions ? (
              <div className="mt-3 flex gap-2">
                <RoughActionButton
                  icon={Copy}
                  label="Copy"
                  onClick={() => void onCopyAssistantMessage(msg.content)}
                />
                <RoughActionButton
                  icon={RotateCcw}
                  label="Retry"
                  onClick={() => onRetryMessage(pairedUserMessage?.requestSnapshot)}
                />
              </div>
            ) : null}
          </div>
        );
      })}
    </>
  );
}
