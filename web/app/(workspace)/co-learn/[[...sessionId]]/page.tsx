"use client";

import {
  BarChart3,
  BrainCircuit,
  Clapperboard,
  Microscope,
  PenLine,
  type LucideIcon,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useTranslation } from "react-i18next";

import ChatComposer from "@/components/chat/home/ChatComposer";
import { ChatMessageList } from "@/components/chat/home/ChatMessages";
import FilePreviewDrawer from "@/components/chat/preview/FilePreviewDrawer";
import type { FilePreviewSource } from "@/components/chat/preview/previewerFor";
import { useAppShell } from "@/context/AppShellContext";
import {
  type MessageAttachment,
  type MessageRequestSnapshot,
  useUnifiedChat,
} from "@/context/UnifiedChatContext";
import { useChatAutoScroll } from "@/hooks/useChatAutoScroll";
import { useMeasuredHeight } from "@/hooks/useMeasuredHeight";
import {
  MAX_ATTACHMENT_BYTES,
  MAX_TOTAL_ATTACHMENT_BYTES,
  classifyFile,
  isSvgFilename,
} from "@/lib/doc-attachments";
import {
  extractBase64FromDataUrl,
  readFileAsDataUrl,
} from "@/lib/file-attachments";
import { listKnowledgeBases } from "@/lib/knowledge-api";
import { listLLMOptions, type LLMOption } from "@/lib/llm-options";
import { SURFACES } from "@/lib/session-surfaces";
import {
  DEFAULT_MATH_ANIMATOR_CONFIG,
  type MathAnimatorFormConfig,
} from "@/lib/math-animator-types";
import {
  DEFAULT_QUIZ_CONFIG,
  type DeepQuestionFormConfig,
} from "@/lib/quiz-types";
import {
  createEmptyResearchConfig,
  type DeepResearchFormConfig,
  type ResearchSource,
} from "@/lib/research-types";
import type { LLMSelection } from "@/lib/unified-ws";
import {
  DEFAULT_VISUALIZE_CONFIG,
  type VisualizeFormConfig,
} from "@/lib/visualize-types";

/* -------------------------------------------------------------------------- */
/* Module-level constants                                                       */
/* -------------------------------------------------------------------------- */

interface CoLearnCapability {
  value: string;
  label: string;
  description: string;
  icon: LucideIcon;
  /** Tools the router *may* enable per-sub-capability. Pure UI hint. */
  allowedTools: string[];
}

/**
 * Sub-capabilities the Auto router is allowed to delegate to. Order here is
 * how they appear in the multi-select popover. The "auto" capability itself
 * and the bare "chat" mode are intentionally excluded — auto routes to
 * specialized capabilities or atomic tools.
 */
const CO_LEARN_CAPABILITIES: CoLearnCapability[] = [
  {
    value: "deep_solve",
    label: "Deep Solve",
    description: "Multi-step reasoning & problem solving",
    icon: BrainCircuit,
    allowedTools: ["rag", "web_search", "code_execution", "reason"],
  },
  {
    value: "deep_question",
    label: "Quiz Generation",
    description: "Auto-validated question generation",
    icon: PenLine,
    allowedTools: ["rag", "web_search", "code_execution"],
  },
  {
    value: "deep_research",
    label: "Deep Research",
    description: "Comprehensive multi-agent research",
    icon: Microscope,
    allowedTools: [],
  },
  {
    value: "math_animator",
    label: "Math Animator",
    description: "Generate math videos or storyboard images",
    icon: Clapperboard,
    allowedTools: [],
  },
  {
    value: "visualize",
    label: "Visualize",
    description: "Generate SVG, Chart.js, or Mermaid visualizations",
    icon: BarChart3,
    allowedTools: [],
  },
];

const DEFAULT_AUTO_ENABLED = new Set(
  CO_LEARN_CAPABILITIES.map((c) => c.value),
);

interface PendingAttachment {
  type: string;
  filename: string;
  base64?: string;
  previewUrl?: string;
  size?: number;
  mimeType?: string;
}

interface KnowledgeBase {
  name: string;
  is_default?: boolean;
}

// Empty constants passed to ChatComposer for picker/skill props the lean
// /co-learn surface intentionally does not expose. Keeping them stable (top-level
// constants) prevents unnecessary ChatComposer re-renders.
const EMPTY_NOTEBOOKS: never[] = [];
const EMPTY_BOOKS: never[] = [];
const EMPTY_HISTORY: never[] = [];
const EMPTY_QUESTIONS: never[] = [];
const EMPTY_SKILLS: string[] = [];
const EMPTY_MEMORY: never[] = [];
const EMPTY_TOOL_SET = new Set<string>();
const EMPTY_NOTEBOOK_GROUPS: never[] = [];
const EMPTY_RESEARCH_SOURCES: { name: ResearchSource; label: string; icon: LucideIcon }[] = [];
const EMPTY_RESEARCH_SOURCE_LIST: ResearchSource[] = [];
const NOOP = () => undefined;
const NOOP_ASYNC = async () => undefined;

/* -------------------------------------------------------------------------- */
/* Page                                                                         */
/* -------------------------------------------------------------------------- */

export default function CoLearnPage() {
  const params = useParams<{ sessionId?: string[] }>();
  const router = useRouter();
  const { t } = useTranslation();
  const sessionIdParam = params.sessionId?.[0] ?? null;
  const { setActiveSessionId, language: appLanguage } = useAppShell();

  const {
    state,
    setCapability,
    setKBs,
    setLLMSelection,
    sendMessage,
    cancelStreamingTurn,
    regenerateLastMessage,
    newSession,
    loadSession,
  } = useUnifiedChat();

  /* ---------------- Local state ---------------- */

  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [llmOptions, setLLMOptions] = useState<LLMOption[]>([]);
  const [activeLLMDefault, setActiveLLMDefault] = useState<LLMSelection | null>(
    null,
  );
  const [llmOptionsLoading, setLLMOptionsLoading] = useState(true);
  const [llmOptionsError, setLLMOptionsError] = useState(false);
  const [attachments, setAttachments] = useState<PendingAttachment[]>([]);
  const [dragging, setDragging] = useState(false);
  const [attachmentError, setAttachmentError] = useState<string | null>(null);
  const [previewSource, setPreviewSource] = useState<FilePreviewSource | null>(
    null,
  );
  const attachmentErrorTimer = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  const [autoEnabledCaps, setAutoEnabledCaps] = useState<Set<string>>(
    () => new Set(DEFAULT_AUTO_ENABLED),
  );

  // Capability popover (multi-select for auto-enabled caps)
  const [capMenuOpen, setCapMenuOpen] = useState(false);
  const [kbMenuOpen, setKbMenuOpen] = useState(false);

  /* ---------------- Refs ---------------- */

  const dragCounter = useRef(0);
  const capMenuRef = useRef<HTMLDivElement>(null);
  const capBtnRef = useRef<HTMLButtonElement>(null);
  const toolMenuRef = useRef<HTMLDivElement>(null);
  const toolBtnRef = useRef<HTMLButtonElement>(null);
  const spaceMenuRef = useRef<HTMLDivElement>(null);
  const spaceBtnRef = useRef<HTMLButtonElement>(null);
  const kbMenuRef = useRef<HTMLDivElement>(null);
  const kbBtnRef = useRef<HTMLButtonElement>(null);
  const initialLoadRef = useRef(false);

  /* ---------------- Composed values ---------------- */

  const hasMessages = state.messages.length > 0;
  const { ref: composerRef } = useMeasuredHeight<HTMLDivElement>();

  // ``activeCap`` is just a placeholder for ChatComposer's prop schema; the
  // composer never renders it in auto mode (capability label area is replaced
  // by the multi-select trigger).
  const activeCap = useMemo<CoLearnCapability>(
    () => ({
      value: "auto",
      label: "Auto",
      description: "Auto routing",
      icon: PenLine,
      allowedTools: [],
    }),
    [],
  );

  /* ---------------- Session bootstrap ---------------- */

  // Force capability="auto" once on mount and keep it pinned. Co-learn is a
  // single-capability surface; the user never picks a manual capability here.
  useEffect(() => {
    setCapability("auto");
  }, [setCapability]);

  useEffect(() => {
    setActiveSessionId(sessionIdParam);
  }, [sessionIdParam, setActiveSessionId]);

  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;
    if (sessionIdParam) {
      void loadSession(sessionIdParam);
    } else {
      newSession();
    }
  }, [loadSession, newSession, sessionIdParam]);

  /* ---------------- KB load ---------------- */

  const loadKBs = useCallback(async (options?: { force?: boolean }) => {
    try {
      const list = await listKnowledgeBases({ force: options?.force });
      const mapped: KnowledgeBase[] = list.map((kb) => ({
        name: kb.name,
        is_default: kb.is_default,
      }));
      setKnowledgeBases(mapped);
      if (state.knowledgeBases.length === 0 && mapped.length > 0) {
        const def = mapped.find((kb) => kb.is_default) ?? mapped[0];
        setKBs([def.name]);
      }
    } catch (err) {
      console.error("Failed to load knowledge bases", err);
    }
  }, [setKBs, state.knowledgeBases.length]);

  useEffect(() => {
    void loadKBs();
  }, [loadKBs]);

  /* ---------------- LLM options ---------------- */

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLLMOptionsLoading(true);
      try {
        const payload = await listLLMOptions();
        if (cancelled) return;
        setLLMOptions(payload.options);
        setActiveLLMDefault(payload.active);
        setLLMOptionsError(false);
      } catch (err) {
        if (cancelled) return;
        console.error("Failed to load LLM options", err);
        setLLMOptions([]);
        setActiveLLMDefault(null);
        setLLMOptionsError(true);
      } finally {
        if (!cancelled) setLLMOptionsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  /* ---------------- Auto scroll ---------------- */

  const lastMsg = state.messages[state.messages.length - 1];
  const {
    containerRef: messagesContainerRef,
    endRef: messagesEndRef,
    shouldAutoScrollRef,
    handleScroll: handleMessagesScroll,
  } = useChatAutoScroll({
    hasMessages,
    isStreaming: state.isStreaming,
    composerHeight: 0,
    messageCount: state.messages.length,
    lastMessageContent: lastMsg?.content,
    lastEventCount: lastMsg?.events?.length,
  });

  /* ---------------- Attachment helpers ---------------- */

  const flashAttachmentError = useCallback((msg: string) => {
    setAttachmentError(msg);
    if (attachmentErrorTimer.current) {
      clearTimeout(attachmentErrorTimer.current);
    }
    attachmentErrorTimer.current = setTimeout(() => {
      setAttachmentError(null);
    }, 4000);
  }, []);

  // Mirrors the chat page's filter + classify logic (see fileToAttachment in
  // app/(workspace)/chat/.../page.tsx). Kept compact: we only need it for the
  // composer's drag/drop/paste paths.
  const fileToAttachment = useCallback(
    (f: File): Promise<PendingAttachment> =>
      new Promise((resolve, reject) => {
        readFileAsDataUrl(f)
          .then((raw) => {
            const svg = isSvgFilename(f.name) || f.type === "image/svg+xml";
            const isImage = !svg && f.type.startsWith("image/");
            resolve({
              type: isImage ? "image" : "file",
              filename: f.name,
              base64: extractBase64FromDataUrl(raw),
              previewUrl: isImage || svg ? raw : undefined,
              size: f.size,
              mimeType: f.type || undefined,
            });
          })
          .catch(reject);
      }),
    [],
  );

  const filterFiles = useCallback(
    (files: File[]): File[] => {
      let running = attachments.reduce((s, a) => s + (a.size ?? 0), 0);
      const accepted: File[] = [];
      let firstReject: { name: string; reason: "unsupported" | "too_large" | "quota" } | null = null;
      for (const f of files) {
        if (!classifyFile(f)) {
          if (!firstReject) firstReject = { name: f.name, reason: "unsupported" };
          continue;
        }
        if (f.size > MAX_ATTACHMENT_BYTES) {
          if (!firstReject) firstReject = { name: f.name, reason: "too_large" };
          continue;
        }
        if (running + f.size > MAX_TOTAL_ATTACHMENT_BYTES) {
          if (!firstReject) firstReject = { name: f.name, reason: "quota" };
          break;
        }
        running += f.size;
        accepted.push(f);
      }
      if (firstReject) {
        const msg =
          firstReject.reason === "too_large"
            ? t("File too large: {{name}}", { name: firstReject.name })
            : firstReject.reason === "quota"
            ? t("Too many files, skipped some")
            : t("Unsupported file type: {{name}}", { name: firstReject.name });
        flashAttachmentError(msg);
      }
      return accepted;
    },
    [attachments, flashAttachmentError, t],
  );

  const handleAddFiles = useCallback(
    async (files: File[]) => {
      const accepted = filterFiles(files);
      if (!accepted.length) return;
      const next = await Promise.all(accepted.map(fileToAttachment));
      setAttachments((prev) => [...prev, ...next]);
    },
    [filterFiles, fileToAttachment],
  );

  const removeAttachment = useCallback((index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  }, []);

  /* ---------------- Drag/drop/paste ---------------- */

  const handleDragEnter = useCallback((event: React.DragEvent) => {
    if (event.dataTransfer.types.includes("Files")) {
      event.preventDefault();
      dragCounter.current += 1;
      setDragging(true);
    }
  }, []);
  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    dragCounter.current = Math.max(0, dragCounter.current - 1);
    if (dragCounter.current === 0) setDragging(false);
  }, []);
  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
  }, []);
  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      dragCounter.current = 0;
      setDragging(false);
      const files = Array.from(event.dataTransfer.files || []);
      if (files.length) void handleAddFiles(files);
    },
    [handleAddFiles],
  );
  const handlePaste = useCallback(
    (event: React.ClipboardEvent) => {
      const files = Array.from(event.clipboardData?.files || []);
      if (files.length) {
        event.preventDefault();
        void handleAddFiles(files);
      }
    },
    [handleAddFiles],
  );

  /* ---------------- KB select ---------------- */

  const handleToggleKB = useCallback(
    (name: string) => {
      const current = state.knowledgeBases;
      setKBs(
        current.includes(name)
          ? current.filter((kb) => kb !== name)
          : [...current, name],
      );
    },
    [setKBs, state.knowledgeBases],
  );

  /* ---------------- Capability multi-select ---------------- */

  const handleToggleAutoCap = useCallback((cap: string) => {
    setAutoEnabledCaps((current) => {
      const next = new Set(current);
      if (next.has(cap)) {
        next.delete(cap);
      } else {
        next.add(cap);
      }
      return next;
    });
  }, []);

  /* ---------------- Send ---------------- */

  const handleSend = useCallback(
    async (content: string) => {
      if ((!content && !attachments.length) || state.isStreaming) return;
      const extraAttachments = attachments.map((a) => ({
        type: a.type,
        filename: a.filename,
        base64: a.base64,
        mime_type: a.mimeType,
      }));
      const config: Record<string, unknown> = {
        enabled_capabilities: Array.from(autoEnabledCaps),
      };
      const messageContent =
        content ||
        (attachments.some((a) => a.type === "image")
          ? t("Please analyze the attached image(s).")
          : "");
      // ``kind: "co_learn"`` tags the backend session row so the chat sidebar
      // / history page never mixes auto-routing sessions into the /chat view.
      // Only matters on the first send (when ``ensure_session`` creates the
      // row); subsequent sends in the same session are no-ops kind-wise.
      sendMessage(
        messageContent,
        extraAttachments,
        config,
        undefined,
        undefined,
        { kind: "co_learn" },
      );
      shouldAutoScrollRef.current = true;
      setAttachments([]);
    },
    [
      attachments,
      autoEnabledCaps,
      sendMessage,
      shouldAutoScrollRef,
      state.isStreaming,
      t,
    ],
  );

  /* ---------------- Preview / answer-now / copy / regenerate ---------------- */

  const handlePreviewMessageAttachment = useCallback((a: MessageAttachment) => {
    setPreviewSource({
      filename: a.filename || "",
      mimeType: a.mime_type,
      type: a.type,
      url: a.url,
      base64: a.base64,
    });
  }, []);
  const handlePreviewPendingAttachment = useCallback(
    (index: number) => {
      const att = attachments[index];
      if (!att) return;
      setPreviewSource({
        filename: att.filename,
        mimeType: att.mimeType,
        type: att.type,
        base64: att.base64,
        size: att.size,
      });
    },
    [attachments],
  );
  const handleClosePreview = useCallback(() => setPreviewSource(null), []);

  const copyAssistantMessage = useCallback(async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (e) {
      console.warn("Copy failed", e);
    }
  }, []);

  const handleAnswerNow = useCallback(
    (
      snapshot?: MessageRequestSnapshot,
      assistantMsg?: { content: string; events?: unknown[] },
    ) => {
      if (!snapshot) {
        cancelStreamingTurn();
        return;
      }
      cancelStreamingTurn();
      // Re-send same request with answer_now_context to trigger fast-path.
      sendMessage(
        snapshot.content,
        snapshot.attachments,
        {
          ...(snapshot.config ?? {}),
          answer_now_context: {
            original_user_message: snapshot.content,
            partial_response: assistantMsg?.content ?? "",
            events: assistantMsg?.events ?? [],
          },
        },
        snapshot.notebookReferences,
        snapshot.historyReferences,
        { bookReferences: snapshot.bookReferences },
        snapshot.questionNotebookReferences,
        snapshot.skills,
        snapshot.memoryReferences,
      );
    },
    [cancelStreamingTurn, sendMessage],
  );

  const handleRegenerateMessage = useCallback(() => {
    regenerateLastMessage();
  }, [regenerateLastMessage]);

  /* ---------------- Outside-click close popovers ---------------- */

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const t = e.target as Node;
      if (
        capMenuRef.current &&
        !capMenuRef.current.contains(t) &&
        capBtnRef.current &&
        !capBtnRef.current.contains(t)
      )
        setCapMenuOpen(false);
      if (
        kbMenuRef.current &&
        !kbMenuRef.current.contains(t) &&
        kbBtnRef.current &&
        !kbBtnRef.current.contains(t)
      )
        setKbMenuOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  /* ---------------- Render ---------------- */

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="mx-auto flex w-full max-w-[960px] flex-1 min-h-0 flex-col overflow-hidden px-6">
        {!hasMessages ? (
          <div className="flex flex-1 min-h-0 flex-col items-center justify-center animate-fade-in">
            <div className="text-center">
              <h1 className="font-serif text-[36px] font-medium tracking-[-0.01em] text-[var(--foreground)]">
                {t("Co-Learn")}
              </h1>
              <p className="mt-4 text-[15px] text-[var(--muted-foreground)]">
                {t(
                  "Just ask — I'll pick the right tool for the job and walk you through it.",
                )}
              </p>
            </div>
          </div>
        ) : (
          <div
            ref={messagesContainerRef}
            data-chat-scroll-root="true"
            onScroll={handleMessagesScroll}
            className="mx-auto w-full flex-1 min-h-0 space-y-7 overflow-y-auto pr-4 [scrollbar-gutter:stable] pt-0"
            style={{
              paddingBottom: "4px",
              WebkitMaskImage:
                "linear-gradient(to bottom, transparent 0px, #000 32px, #000 calc(100% - 40px), transparent 100%)",
              maskImage:
                "linear-gradient(to bottom, transparent 0px, #000 32px, #000 calc(100% - 40px), transparent 100%)",
            }}
          >
            <ChatMessageList
              messages={state.messages}
              isStreaming={state.isStreaming}
              sessionId={state.sessionId}
              language={state.language ?? appLanguage}
              onAnswerNow={handleAnswerNow}
              onCopyAssistantMessage={copyAssistantMessage}
              onRegenerateMessage={handleRegenerateMessage}
              onPreviewAttachment={handlePreviewMessageAttachment}
              onSwitchToManualMode={() => router.push(SURFACES.chat.basePath)}
            />
            <div ref={messagesEndRef} className="h-px w-full shrink-0" />
          </div>
        )}

        <ChatComposer
          composerRef={composerRef}
          capMenuRef={capMenuRef}
          capBtnRef={capBtnRef}
          toolMenuRef={toolMenuRef}
          toolBtnRef={toolBtnRef}
          spaceMenuRef={spaceMenuRef}
          spaceBtnRef={spaceBtnRef}
          kbMenuRef={kbMenuRef}
          kbBtnRef={kbBtnRef}
          dragCounter={dragCounter}
          dragging={dragging}
          capMenuOpen={capMenuOpen}
          toolMenuOpen={false}
          spaceMenuOpen={false}
          kbMenuOpen={kbMenuOpen}
          hasMessages={hasMessages}
          attachments={attachments}
          attachmentError={attachmentError}
          activeCap={activeCap}
          visibleTools={[]}
          selectedTools={EMPTY_TOOL_SET}
          knowledgeBases={knowledgeBases}
          llmOptions={llmOptions}
          activeLLMDefault={activeLLMDefault}
          llmSelection={state.llmSelection}
          llmOptionsLoading={llmOptionsLoading}
          llmOptionsError={llmOptionsError}
          selectedBookReferences={EMPTY_BOOKS}
          selectedNotebookRecords={EMPTY_NOTEBOOKS}
          selectedHistorySessions={EMPTY_HISTORY}
          selectedQuestionEntries={EMPTY_QUESTIONS}
          notebookReferenceGroups={EMPTY_NOTEBOOK_GROUPS}
          selectedSkills={EMPTY_SKILLS}
          skillsAutoMode={false}
          selectedMemoryFiles={EMPTY_MEMORY}
          selectedKnowledgeBases={state.knowledgeBases}
          isStreaming={state.isStreaming}
          isResearchMode={false}
          isMathAnimatorMode={false}
          isVisualizeMode={false}
          isAutoMode={true}
          autoEnabledCaps={autoEnabledCaps}
          researchConfigSources={EMPTY_RESEARCH_SOURCE_LIST}
          capabilityNeedsConfig={false}
          capabilityConfigConfirmed={true}
          onRequestConfigConfirm={NOOP}
          capabilities={CO_LEARN_CAPABILITIES}
          researchSources={EMPTY_RESEARCH_SOURCES}
          onSetCapMenuOpen={setCapMenuOpen}
          onSetToolMenuOpen={NOOP}
          onSetSpaceMenuOpen={NOOP}
          onSetKbMenuOpen={setKbMenuOpen}
          onToggleAutoCap={handleToggleAutoCap}
          onToggleKB={handleToggleKB}
          onSelectLLM={setLLMSelection}
          onSelectNotebookPicker={NOOP}
          onSelectBookPicker={NOOP}
          onSelectHistoryPicker={NOOP}
          onSelectQuestionBankPicker={NOOP}
          onSelectSkillsPicker={NOOP}
          onSelectMemoryPicker={NOOP}
          onToggleTool={NOOP}
          onToggleSkill={NOOP}
          onSetSkillsAuto={NOOP}
          onToggleMemoryFile={NOOP}
          onToggleResearchSource={NOOP}
          onSend={handleSend}
          onRemoveAttachment={removeAttachment}
          onPreviewAttachment={handlePreviewPendingAttachment}
          onRemoveHistory={NOOP}
          onRemoveBookReference={NOOP}
          onRemoveNotebook={NOOP}
          onRemoveQuestion={NOOP}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onPaste={handlePaste}
          onAddFiles={(files) => void handleAddFiles(files)}
          onSelectCapability={NOOP}
          onCancelStreaming={cancelStreamingTurn}
        />
      </div>
      <FilePreviewDrawer
        open={previewSource !== null}
        source={previewSource}
        onClose={handleClosePreview}
      />
    </div>
  );
}
