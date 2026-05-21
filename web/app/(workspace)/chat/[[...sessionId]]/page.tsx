"use client";

import dynamic from "next/dynamic";
import {
  type KeyboardEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useParams, useRouter } from "next/navigation";

import {
  BarChart3,
  BrainCircuit,
  Code2,
  Compass,
  Database,
  FileSearch,
  Globe,
  Lightbulb,
  MessageSquare,
  Microscope,
  PenLine,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import type { SelectedRecord } from "@/lib/notebook-selection-types";
import type { SelectedHistorySession } from "@/components/chat/HistorySessionPicker";
import type { SelectedQuestionEntry } from "@/components/chat/QuestionBankPicker";
import ChatComposer from "@/components/chat/home/ChatComposer";
import { ChatMessageList } from "@/components/chat/home/ChatMessages";
// Imported eagerly so the drawer shell is always mounted off-screen —
// clicking a chip becomes a single CSS class flip, no chunk fetch + double
// render. The heavy renderers inside still load lazily.
import FilePreviewDrawer from "@/components/chat/preview/FilePreviewDrawer";
import SessionActivityPanel, {
  buildSessionActivity,
} from "@/components/chat/home/SessionActivityPanel";
import SessionViewerPanel, {
  type SessionViewerPanelHandle,
} from "@/components/chat/home/SessionViewerPanel";
import {
  QuizFollowupProvider,
  useQuizFollowupController,
} from "@/context/QuizFollowupContext";
import {
  GeogebraTabProvider,
  useGeogebraTabOpener,
} from "@/context/GeogebraTabContext";
import {
  BookmarkPlus,
  BookOpen,
  Download,
  PanelRight,
  SquarePen,
} from "lucide-react";
import {
  useUnifiedChat,
  type MessageAttachment,
  type MessageRequestSnapshot,
} from "@/context/UnifiedChatContext";
import { useAppShell } from "@/context/AppShellContext";
import type { FilePreviewSource } from "@/components/chat/preview/previewerFor";
import type { LLMSelection, StreamEvent } from "@/lib/unified-ws";
import {
  extractBase64FromDataUrl,
  readFileAsDataUrl,
} from "@/lib/file-attachments";
import {
  classifyFile,
  isSvgFilename,
  MAX_ATTACHMENT_BYTES,
  MAX_TOTAL_ATTACHMENT_BYTES,
} from "@/lib/doc-attachments";
import { useChatAutoScroll } from "@/hooks/useChatAutoScroll";
import { useMeasuredHeight } from "@/hooks/useMeasuredHeight";
import {
  loadCapabilityPlaygroundConfigs,
  resolveCapabilityPlaygroundConfig,
  type CapabilityPlaygroundConfigMap,
} from "@/lib/playground-config";
import {
  DEFAULT_QUIZ_CONFIG,
  buildQuizWSConfig,
  type DeepQuestionFormConfig,
} from "@/lib/quiz-types";
import {
  DEFAULT_VISUALIZE_CONFIG,
  buildVisualizeWSConfig,
  type VisualizeFormConfig,
} from "@/lib/visualize-types";
import {
  buildResearchWSConfig,
  createEmptyResearchConfig,
  validateResearchConfig,
  type DeepResearchFormConfig,
  type OutlineItem,
} from "@/lib/research-types";
import { listKnowledgeBases } from "@/lib/knowledge-api";
import { listLLMOptions, type LLMOption } from "@/lib/llm-options";
import {
  getEnabledOptionalTools,
  invalidateEnabledOptionalToolsCache,
} from "@/lib/tools-settings";
import { downloadChatMarkdown } from "@/lib/chat-export";
import type { SpaceMemoryFile } from "@/lib/space-items";
import {
  selectedBooksToPayload,
  type SelectedBookReference,
} from "@/lib/book-references";

const NotebookRecordPicker = dynamic(
  () => import("@/components/notebook/NotebookRecordPicker"),
  {
    ssr: false,
  },
);
const HistorySessionPicker = dynamic(
  () => import("@/components/chat/HistorySessionPicker"),
  {
    ssr: false,
  },
);
const QuestionBankPicker = dynamic(
  () => import("@/components/chat/QuestionBankPicker"),
  {
    ssr: false,
  },
);
const SkillsPicker = dynamic(() => import("@/components/chat/SkillsPicker"), {
  ssr: false,
});
const MemoryPicker = dynamic(() => import("@/components/chat/MemoryPicker"), {
  ssr: false,
});
const BookReferencePicker = dynamic(
  () => import("@/components/chat/BookReferencePicker"),
  {
    ssr: false,
  },
);
const SaveToNotebookModal = dynamic(
  () => import("@/components/notebook/SaveToNotebookModal"),
  {
    ssr: false,
  },
);
// Activity-panel config card hosts the capability-specific form (Quiz /
// Animator / Visualize / Research). Lazy-loaded so capabilities that
// don't need a form (Chat / Solve) don't ship the form JS.
const CapabilityConfigCard = dynamic(
  () => import("@/components/chat/home/CapabilityConfigCard"),
  { ssr: false },
);
const QuizConfigPanel = dynamic(
  () => import("@/components/quiz/QuizConfigPanel"),
  { ssr: false },
);
const VisualizeConfigPanel = dynamic(
  () => import("@/components/visualize/VisualizeConfigPanel"),
  { ssr: false },
);
const ResearchConfigPanel = dynamic(
  () => import("@/components/research/ResearchConfigPanel"),
  { ssr: false },
);

/* ------------------------------------------------------------------ */
/*  Type & data definitions                                           */
/* ------------------------------------------------------------------ */

type ToolName =
  | "brainstorm"
  | "geogebra_analysis"
  | "web_search"
  | "code_execution"
  | "reason"
  | "paper_search";

interface ToolDef {
  name: ToolName;
  label: string;
  icon: LucideIcon;
}

const ALL_TOOLS: ToolDef[] = [
  { name: "brainstorm", label: "Brainstorm", icon: Lightbulb },
  { name: "geogebra_analysis", label: "GeoGebra", icon: Compass },
  { name: "web_search", label: "Web Search", icon: Globe },
  { name: "code_execution", label: "Code", icon: Code2 },
  { name: "reason", label: "Reason", icon: Sparkles },
  { name: "paper_search", label: "Arxiv Search", icon: FileSearch },
];

interface CapabilityDef {
  value: string;
  label: string;
  description: string;
  icon: LucideIcon;
  allowedTools: ToolName[];
  defaultTools: ToolName[];
}

const CAPABILITIES: CapabilityDef[] = [
  {
    value: "",
    label: "Chat",
    description: "Flexible conversation with any tool",
    icon: MessageSquare,
    allowedTools: [
      "brainstorm",
      "geogebra_analysis",
      "web_search",
      "code_execution",
      "reason",
      "paper_search",
    ],
    defaultTools: [],
  },
  {
    value: "deep_solve",
    label: "Solve",
    description: "Multi-step reasoning & problem solving",
    icon: BrainCircuit,
    allowedTools: ["web_search", "code_execution", "reason"],
    defaultTools: ["web_search", "code_execution", "reason"],
  },
  {
    value: "deep_question",
    label: "Quiz",
    description: "Auto-validated question generation",
    icon: PenLine,
    allowedTools: ["web_search", "code_execution"],
    defaultTools: ["web_search", "code_execution"],
  },
  {
    value: "deep_research",
    label: "Research",
    description: "Comprehensive multi-agent research",
    icon: Microscope,
    allowedTools: ["web_search", "paper_search", "code_execution"],
    defaultTools: ["web_search", "paper_search", "code_execution"],
  },
  {
    value: "visualize",
    label: "Visualize",
    description:
      "Generate charts, diagrams, interactive pages, or math animations",
    icon: BarChart3,
    allowedTools: [],
    defaultTools: [],
  },
];

interface KnowledgeBase {
  name: string;
  is_default?: boolean;
}

interface PendingAttachment {
  type: string;
  filename: string;
  base64?: string;
  previewUrl?: string;
  size?: number;
  mimeType?: string;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function getCapability(value: string | null): CapabilityDef {
  return CAPABILITIES.find((c) => c.value === (value || "")) ?? CAPABILITIES[0];
}

/* ------------------------------------------------------------------ */
/*  Chat page                                                         */
/* ------------------------------------------------------------------ */

export default function ChatPage() {
  const params = useParams<{ sessionId?: string[] }>();
  const router = useRouter();
  const { t } = useTranslation();
  const sessionIdParam = params.sessionId?.[0] ?? null;
  const { setActiveSessionId, language: appLanguage } = useAppShell();

  const {
    state,
    setTools,
    setCapability,
    setKBs,
    setLLMSelection,
    sendMessage,
    cancelStreamingTurn,
    submitUserReply,
    regenerateLastMessage,
    deleteTurn,
    editMessage,
    switchBranch,
    newSession,
    loadSession,
    renameSessionTitle,
  } = useUnifiedChat();

  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [llmOptions, setLLMOptions] = useState<LLMOption[]>([]);
  const [activeLLMDefault, setActiveLLMDefault] = useState<LLMSelection | null>(
    null,
  );
  const [llmOptionsLoading, setLLMOptionsLoading] = useState(true);
  const [llmOptionsError, setLLMOptionsError] = useState(false);
  const [capabilityConfigs, setCapabilityConfigs] =
    useState<CapabilityPlaygroundConfigMap>({});
  // User-toggleable tools the user has enabled in /settings/tools. This is
  // the single source of truth for which optional tools the chat agent may
  // use; the chat composer no longer exposes a picker.
  const [userEnabledTools, setUserEnabledTools] = useState<string[] | null>(
    null,
  );
  const [attachments, setAttachments] = useState<PendingAttachment[]>([]);
  const [dragging, setDragging] = useState(false);
  const [attachmentError, setAttachmentError] = useState<string | null>(null);
  const [previewSource, setPreviewSource] = useState<FilePreviewSource | null>(
    null,
  );
  // When the chat column squeezes (e.g. the Viewer panel opens), the header
  // action labels can collide. We measure the actual header width and flip
  // to icon-only buttons below a threshold so the row never overflows.
  // Important: read full border-box width via getBoundingClientRect — the
  // ResizeObserverEntry.contentRect excludes the header's px-6 padding
  // (48 px), which makes a "naive" threshold land 48 px below where labels
  // actually start colliding.
  const headerRef = useRef<HTMLDivElement | null>(null);
  const [headerMeasuredWidth, setHeaderMeasuredWidth] = useState<number>(
    Number.POSITIVE_INFINITY,
  );
  useEffect(() => {
    const el = headerRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    setHeaderMeasuredWidth(el.getBoundingClientRect().width);
    const observer = new ResizeObserver(() => {
      // entry.contentRect drops padding; the visual collision happens at
      // border-box width, so read it directly off the element.
      if (headerRef.current) {
        setHeaderMeasuredWidth(headerRef.current.getBoundingClientRect().width);
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  // Right-side panels — Activity (floating cards) and Viewer (full sidebar
  // with tabs for file previews + web pages). Each independently togglable
  // and persisted across reloads.
  //
  // We initialise both to `false` so the SSR-rendered HTML matches the
  // first client render exactly (no hydration mismatch). The persisted
  // preference is then applied in a post-mount effect below.
  const [activityPanelOpen, setActivityPanelOpen] = useState(false);
  const [viewerPanelOpen, setViewerPanelOpen] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.localStorage.getItem("dt:chat:activity-panel") === "1") {
      setActivityPanelOpen(true);
    }
    if (window.localStorage.getItem("dt:chat:viewer-panel") === "1") {
      setViewerPanelOpen(true);
    }
  }, []);
  const toggleActivityPanel = useCallback(() => {
    setActivityPanelOpen((prev) => {
      const next = !prev;
      if (typeof window !== "undefined") {
        window.localStorage.setItem("dt:chat:activity-panel", next ? "1" : "0");
      }
      return next;
    });
  }, []);
  /**
   * Force the Activity panel open. Used by the send-gate when the user
   * tries to send while the active capability still needs its config
   * confirmed — we surface the right-side panel so the Confirm button is
   * visible. Persisted to localStorage so subsequent reloads remember the
   * preference. Also used by the capability-switch auto-open effect below.
   */
  const ensureActivityPanelOpen = useCallback(() => {
    setActivityPanelOpen((prev) => {
      if (prev) return prev;
      if (typeof window !== "undefined") {
        window.localStorage.setItem("dt:chat:activity-panel", "1");
      }
      return true;
    });
  }, []);
  const setViewerOpen = useCallback((next: boolean) => {
    setViewerPanelOpen(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("dt:chat:viewer-panel", next ? "1" : "0");
    }
  }, []);
  const toggleViewerPanel = useCallback(() => {
    setViewerPanelOpen((prev) => {
      const next = !prev;
      if (typeof window !== "undefined") {
        window.localStorage.setItem("dt:chat:viewer-panel", next ? "1" : "0");
      }
      return next;
    });
  }, []);
  // The header's five labelled actions ("Save to Notebook" / "Download
  // Markdown" / "New chat" / "Activity" / "Viewer") need roughly 720 px
  // (label widths + gaps + the capability title) to fit on one row without
  // colliding. Below that we collapse all five to icon-only. We also
  // force-collapse whenever the Viewer panel is open — its squeeze is
  // aggressive enough that labels are guaranteed to overflow.
  const headerCompact = viewerPanelOpen || headerMeasuredWidth < 720;
  const attachmentErrorTimer = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );
  const [capMenuOpen, setCapMenuOpen] = useState(false);
  const [quizConfig, setQuizConfig] = useState<DeepQuestionFormConfig>({
    ...DEFAULT_QUIZ_CONFIG,
  });
  const [quizPdf, setQuizPdf] = useState<File | null>(null);
  const [visualizeConfig, setVisualizeConfig] = useState<VisualizeFormConfig>({
    ...DEFAULT_VISUALIZE_CONFIG,
  });
  const [researchConfig, setResearchConfig] = useState<DeepResearchFormConfig>(
    createEmptyResearchConfig(),
  );
  // Capability-config confirmation gate.
  //
  // For capabilities that need explicit configuration (Quiz, Visualize,
  // Research), the user must click *Confirm* in the right-side Activity
  // panel before sending. Any subsequent edit to the underlying config
  // invalidates the confirmation, so the user re-confirms once they've
  // adjusted settings. Capability switches also reset this flag.
  const [capabilityConfigConfirmed, setCapabilityConfigConfirmed] =
    useState(false);
  // Per-session persistence of the capability-config form. The form lives
  // in local React state, so anything that remounts the page (browser
  // back/forward to /chat/<id>, URL-driven session swap, etc.) would
  // otherwise wipe a confirmed-and-already-sent setup back to defaults.
  // Storing the form by sessionId in localStorage keeps the selections —
  // and the Confirmed badge — stable for the rest of the session.
  const capabilityConfigStorageKey = useMemo(() => {
    const sid = state.sessionId || sessionIdParam || "";
    return sid ? `dt:chat:capability-config:${sid}` : null;
  }, [state.sessionId, sessionIdParam]);
  const lastHydratedConfigKeyRef = useRef<string | null>(null);
  // Hydrate the form configs on first encounter of each session id, so
  // the user's prior selections come back when they return to a session.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!capabilityConfigStorageKey) return;
    if (lastHydratedConfigKeyRef.current === capabilityConfigStorageKey) return;
    lastHydratedConfigKeyRef.current = capabilityConfigStorageKey;
    const raw = window.localStorage.getItem(capabilityConfigStorageKey);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw) as {
        quizConfig?: DeepQuestionFormConfig;
        visualizeConfig?: VisualizeFormConfig;
        researchConfig?: DeepResearchFormConfig;
        capabilityConfigConfirmed?: boolean;
      };
      if (parsed.quizConfig) setQuizConfig(parsed.quizConfig);
      if (parsed.visualizeConfig) setVisualizeConfig(parsed.visualizeConfig);
      if (parsed.researchConfig) setResearchConfig(parsed.researchConfig);
      if (typeof parsed.capabilityConfigConfirmed === "boolean") {
        setCapabilityConfigConfirmed(parsed.capabilityConfigConfirmed);
      }
    } catch {
      /* corrupted entry — ignore */
    }
  }, [capabilityConfigStorageKey]);
  // Persist on every change. Write is synchronous and small, and
  // localStorage already de-dupes identical writes at the browser level.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!capabilityConfigStorageKey) return;
    window.localStorage.setItem(
      capabilityConfigStorageKey,
      JSON.stringify({
        quizConfig,
        visualizeConfig,
        researchConfig,
        capabilityConfigConfirmed,
      }),
    );
  }, [
    capabilityConfigStorageKey,
    quizConfig,
    visualizeConfig,
    researchConfig,
    capabilityConfigConfirmed,
  ]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showNotebookPicker, setShowNotebookPicker] = useState(false);
  const [showBookPicker, setShowBookPicker] = useState(false);
  const [showHistoryPicker, setShowHistoryPicker] = useState(false);
  const [showQuestionBankPicker, setShowQuestionBankPicker] = useState(false);
  const [showSkillsPicker, setShowSkillsPicker] = useState(false);
  const [showMemoryPicker, setShowMemoryPicker] = useState(false);
  const [spaceMenuOpen, setSpaceMenuOpen] = useState(false);
  const [kbMenuOpen, setKbMenuOpen] = useState(false);
  const [selectedNotebookRecords, setSelectedNotebookRecords] = useState<
    SelectedRecord[]
  >([]);
  const [selectedBookReferences, setSelectedBookReferences] = useState<
    SelectedBookReference[]
  >([]);
  const [selectedHistorySessions, setSelectedHistorySessions] = useState<
    SelectedHistorySession[]
  >([]);
  const [selectedQuestionEntries, setSelectedQuestionEntries] = useState<
    SelectedQuestionEntry[]
  >([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [skillsAutoMode, setSkillsAutoMode] = useState(false);
  const [selectedMemoryFiles, setSelectedMemoryFiles] = useState<
    SpaceMemoryFile[]
  >([]);
  const dragCounter = useRef(0);
  const capMenuRef = useRef<HTMLDivElement>(null);
  const capBtnRef = useRef<HTMLButtonElement>(null);
  const spaceMenuRef = useRef<HTMLDivElement>(null);
  const spaceBtnRef = useRef<HTMLButtonElement>(null);
  const kbMenuRef = useRef<HTMLDivElement>(null);
  const kbBtnRef = useRef<HTMLButtonElement>(null);
  const initialLoadRef = useRef(false);
  // Bridge ref: ``ChatComposer`` writes a prefill function into this on
  // mount; ``ChatMessageList`` reads it via ``handlePrefillComposer`` so an
  // ``AskUserOptions`` chip click can drop text into the composer textarea.
  const prefillInputRef = useRef<((text: string) => void) | null>(null);
  const handlePrefillComposer = useCallback((text: string) => {
    prefillInputRef.current?.(text);
  }, []);

  const activeCap = useMemo(
    () => getCapability(state.activeCapability),
    [state.activeCapability],
  );
  const isQuizMode = activeCap.value === "deep_question";
  const isVisualizeMode = activeCap.value === "visualize";
  const isResearchMode = activeCap.value === "deep_research";
  const capabilityNeedsConfig = isQuizMode || isVisualizeMode || isResearchMode;

  // Edit-invalidates-confirm wrappers — flipping any field after the user
  // hit *Confirm* should restore the gate so they re-confirm intentionally.
  // `useCallback` keeps identities stable so the memoized ChatComposer /
  // CapabilityConfigCard don't churn on every keystroke.
  const handleChangeQuizConfig = useCallback((next: DeepQuestionFormConfig) => {
    setQuizConfig(next);
    setCapabilityConfigConfirmed(false);
  }, []);
  const handleUploadQuizPdf = useCallback((file: File | null) => {
    setQuizPdf(file);
    setCapabilityConfigConfirmed(false);
  }, []);
  const handleChangeVisualizeConfig = useCallback(
    (next: VisualizeFormConfig) => {
      setVisualizeConfig(next);
      setCapabilityConfigConfirmed(false);
    },
    [],
  );
  const handleChangeResearchConfig = useCallback(
    (next: DeepResearchFormConfig) => {
      setResearchConfig(next);
      setCapabilityConfigConfirmed(false);
    },
    [],
  );
  const handleConfirmCapabilityConfig = useCallback(() => {
    setCapabilityConfigConfirmed(true);
  }, []);

  /**
   * Auto-open the right-side Activity panel when the user switches into a
   * capability that requires manual configuration (Quiz / Animator /
   * Visualize / Research). We only fire on the transition from "doesn't
   * need config" → "needs config" so we don't fight the user if they
   * close the panel themselves while still in a config-needing mode.
   *
   * Tracking via a ref (instead of deps) avoids re-firing whenever the
   * panel toggles — the open-state flip should be one-shot per cap
   * transition.
   */
  const lastCapabilityNeedsConfigRef = useRef(capabilityNeedsConfig);
  useEffect(() => {
    const prev = lastCapabilityNeedsConfigRef.current;
    lastCapabilityNeedsConfigRef.current = capabilityNeedsConfig;
    if (!prev && capabilityNeedsConfig) {
      ensureActivityPanelOpen();
    }
  }, [capabilityNeedsConfig, ensureActivityPanelOpen]);
  const hasMessages = state.messages.length > 0;
  // Time-of-day greeting: seeded once on mount from the user's local clock so
  // the heading stays stable while they're on the page. State (not useMemo)
  // because the random pick would otherwise mismatch SSR ↔ client hydration.
  const [welcomeGreeting, setWelcomeGreeting] = useState<string>(
    "What would you like to learn?",
  );
  useEffect(() => {
    const hour = new Date().getHours();
    let bucket: string[];
    if (hour >= 5 && hour < 12) {
      bucket = [
        "Good morning.",
        "Morning — let's learn something.",
        "What would you like to learn?",
      ];
    } else if (hour >= 12 && hour < 17) {
      bucket = [
        "Good afternoon.",
        "Afternoon — what's on your mind?",
        "What would you like to learn?",
      ];
    } else if (hour >= 17 && hour < 22) {
      bucket = [
        "Good evening.",
        "Evening — what shall we explore?",
        "What would you like to learn?",
      ];
    } else {
      bucket = [
        "It's late today.",
        "Burning the midnight oil?",
        "What would you like to learn?",
      ];
    }
    setWelcomeGreeting(bucket[Math.floor(Math.random() * bucket.length)]);
  }, []);
  const firstUserTitle = useMemo(
    () =>
      state.messages
        .find((msg) => msg.role === "user")
        ?.content.trim()
        .replace(/\s+/g, " ")
        .slice(0, 80) || "",
    [state.messages],
  );
  const persistedSessionTitle = state.sessionTitle.trim();
  const displaySessionTitle =
    persistedSessionTitle || firstUserTitle || t("New chat");
  const canRenameSession = Boolean(state.sessionId);
  const titleInputRef = useRef<HTMLInputElement | null>(null);
  const skipTitleCommitRef = useRef(false);
  const [sessionTitleDraft, setSessionTitleDraft] =
    useState(displaySessionTitle);
  const [sessionTitleEditing, setSessionTitleEditing] = useState(false);
  const [sessionTitleSaving, setSessionTitleSaving] = useState(false);
  const [sessionTitleError, setSessionTitleError] = useState<string | null>(
    null,
  );
  useEffect(() => {
    if (sessionTitleEditing) return;
    setSessionTitleDraft(displaySessionTitle);
  }, [displaySessionTitle, sessionTitleEditing]);
  useEffect(() => {
    if (!sessionTitleEditing) return;
    window.requestAnimationFrame(() => {
      titleInputRef.current?.focus();
      titleInputRef.current?.select();
    });
  }, [sessionTitleEditing]);
  const startSessionTitleEdit = useCallback(() => {
    if (!canRenameSession) return;
    skipTitleCommitRef.current = false;
    setSessionTitleError(null);
    setSessionTitleDraft(displaySessionTitle);
    setSessionTitleEditing(true);
  }, [canRenameSession, displaySessionTitle]);
  const cancelSessionTitleEdit = useCallback(() => {
    skipTitleCommitRef.current = true;
    setSessionTitleDraft(displaySessionTitle);
    setSessionTitleError(null);
    setSessionTitleEditing(false);
  }, [displaySessionTitle]);
  const commitSessionTitleEdit = useCallback(async () => {
    if (skipTitleCommitRef.current) {
      skipTitleCommitRef.current = false;
      return;
    }
    const next = sessionTitleDraft.trim();
    if (!next) {
      setSessionTitleDraft(displaySessionTitle);
      setSessionTitleEditing(false);
      return;
    }
    if (!canRenameSession || next === persistedSessionTitle) {
      setSessionTitleDraft(next || displaySessionTitle);
      setSessionTitleEditing(false);
      return;
    }
    setSessionTitleSaving(true);
    setSessionTitleError(null);
    try {
      await renameSessionTitle(next);
      setSessionTitleEditing(false);
    } catch (error) {
      console.error("Failed to rename session:", error);
      setSessionTitleError(t("Rename failed"));
      titleInputRef.current?.focus();
    } finally {
      setSessionTitleSaving(false);
    }
  }, [
    canRenameSession,
    displaySessionTitle,
    persistedSessionTitle,
    renameSessionTitle,
    sessionTitleDraft,
    t,
  ]);
  const handleSessionTitleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === "Enter") {
        event.preventDefault();
        void commitSessionTitleEdit();
      } else if (event.key === "Escape") {
        event.preventDefault();
        cancelSessionTitleEdit();
      }
    },
    [cancelSessionTitleEdit, commitSessionTitleEdit],
  );
  const { ref: composerRef, height: composerHeight } =
    useMeasuredHeight<HTMLDivElement>();
  const researchValidation = useMemo(
    () => validateResearchConfig(researchConfig),
    [researchConfig],
  );
  const notebookReferenceGroups = useMemo(() => {
    const groups = new Map<string, { notebookName: string; count: number }>();
    selectedNotebookRecords.forEach((record) => {
      const existing = groups.get(record.notebookId);
      if (existing) {
        existing.count += 1;
      } else {
        groups.set(record.notebookId, {
          notebookName: record.notebookName,
          count: 1,
        });
      }
    });
    return Array.from(groups.entries()).map(([notebookId, value]) => ({
      notebookId,
      ...value,
    }));
  }, [selectedNotebookRecords]);
  const notebookReferencesPayload = useMemo(() => {
    const grouped = new Map<string, string[]>();
    selectedNotebookRecords.forEach((record) => {
      const current = grouped.get(record.notebookId) || [];
      current.push(record.id);
      grouped.set(record.notebookId, current);
    });
    return Array.from(grouped.entries()).map(([notebook_id, record_ids]) => ({
      notebook_id,
      record_ids,
    }));
  }, [selectedNotebookRecords]);
  const bookReferencesPayload = useMemo(
    () => selectedBooksToPayload(selectedBookReferences),
    [selectedBookReferences],
  );
  const historyReferencesPayload = useMemo(
    () => selectedHistorySessions.map((session) => session.sessionId),
    [selectedHistorySessions],
  );
  const questionNotebookReferencesPayload = useMemo(
    () => selectedQuestionEntries.map((entry) => entry.id),
    [selectedQuestionEntries],
  );
  const memoryReferencesPayload = useMemo(
    () => [...selectedMemoryFiles],
    [selectedMemoryFiles],
  );
  const chatSaveMessages = useMemo(
    () =>
      state.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        capability: msg.capability,
      })),
    [state.messages],
  );
  const chatSavePayload = useMemo(() => {
    if (!state.messages.length) return null;
    const title =
      state.messages
        .find((msg) => msg.role === "user")
        ?.content.trim()
        .slice(0, 80) || "Chat Session";
    return {
      recordType: "chat" as const,
      title,
      // The actual transcript / userQuery are rebuilt inside SaveToNotebookModal
      // from the user's selected subset of messages. We still provide a
      // sensible fallback for non-selection callers.
      userQuery: "",
      output: "",
      metadata: {
        source: "chat",
        capability: state.activeCapability || "chat",
        ui_language: state.language,
        session_id: state.sessionId,
        total_message_count: state.messages.length,
      },
    };
  }, [state.activeCapability, state.language, state.messages, state.sessionId]);
  const lastMessage = state.messages[state.messages.length - 1];
  const {
    containerRef: messagesContainerRef,
    endRef: messagesEndRef,
    shouldAutoScrollRef,
    handleScroll: handleMessagesScroll,
  } = useChatAutoScroll({
    hasMessages,
    isStreaming: state.isStreaming,
    composerHeight,
    messageCount: state.messages.length,
    lastMessageContent: lastMessage?.content,
    lastEventCount: lastMessage?.events?.length,
  });
  const copyAssistantMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;
    try {
      await navigator.clipboard.writeText(content);
    } catch (error) {
      console.error("Failed to copy assistant message:", error);
    }
  }, []);
  const handleAnswerNow = useCallback(
    (
      snapshot?: MessageRequestSnapshot,
      assistantMsg?: { content: string; events?: StreamEvent[] },
    ) => {
      if (!snapshot || !state.isStreaming) return;
      const answerNowEvents = (assistantMsg?.events ?? []).map((event) => ({
        type: event.type,
        stage: event.stage,
        content: event.content,
        metadata: event.metadata ?? {},
      }));
      cancelStreamingTurn();
      // Preserve the original capability — chat / visualize / math_animator
      // each own an answer-now fast-path. The backend orchestrator only
      // falls back to ``chat`` if the requested capability is missing.
      // Solve / Quiz / Research no longer expose Answer Now (their UI
      // gate filters the button out), so we never reach here for them.
      const answerNowSnapshot: MessageRequestSnapshot = {
        ...snapshot,
        language: appLanguage,
        config: {
          ...(snapshot.config || {}),
          answer_now_context: {
            original_user_message: snapshot.content,
            partial_response: assistantMsg?.content || "",
            events: answerNowEvents,
          },
        },
      };
      window.setTimeout(() => {
        sendMessage(
          answerNowSnapshot.content,
          answerNowSnapshot.attachments,
          answerNowSnapshot.config,
          answerNowSnapshot.notebookReferences,
          answerNowSnapshot.historyReferences,
          {
            displayUserMessage: false,
            persistUserMessage: false,
            requestSnapshotOverride: answerNowSnapshot,
            bookReferences: answerNowSnapshot.bookReferences,
          },
          answerNowSnapshot.questionNotebookReferences,
          answerNowSnapshot.skills,
          answerNowSnapshot.memoryReferences,
        );
        shouldAutoScrollRef.current = true;
      }, 0);
    },
    [
      appLanguage,
      cancelStreamingTurn,
      sendMessage,
      shouldAutoScrollRef,
      state.isStreaming,
    ],
  );

  /* ---- URL-driven session loading ---- */
  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;
    if (sessionIdParam) {
      void loadSession(sessionIdParam).catch(() => {
        router.replace("/chat", { scroll: false });
      });
    } else {
      newSession();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // When URL param changes (sidebar navigation), load the corresponding session
  const prevSessionIdParam = useRef(sessionIdParam);
  useEffect(() => {
    if (sessionIdParam === prevSessionIdParam.current) return;
    prevSessionIdParam.current = sessionIdParam;
    if (sessionIdParam) {
      if (sessionIdParam === state.sessionId) return;
      void loadSession(sessionIdParam).catch(() => {
        router.replace("/chat", { scroll: false });
      });
    } else {
      newSession();
    }
  }, [sessionIdParam, loadSession, newSession, router, state.sessionId]);

  // When a new session_id is assigned by the server, update the URL
  useEffect(() => {
    if (state.sessionId && !sessionIdParam) {
      router.replace(`/chat/${state.sessionId}`, { scroll: false });
    }
  }, [state.sessionId, sessionIdParam, router]);

  useEffect(() => {
    setActiveSessionId(state.sessionId || sessionIdParam || null);
  }, [state.sessionId, sessionIdParam, setActiveSessionId]);

  const refreshKnowledgeBases = useCallback(
    async (options?: { force?: boolean }) => {
      try {
        const list = await listKnowledgeBases({ force: options?.force });
        setKnowledgeBases(list);
      } catch {
        setKnowledgeBases([]);
      }
    },
    [],
  );

  /* Load KBs */
  useEffect(() => {
    void refreshKnowledgeBases({ force: true });
  }, [refreshKnowledgeBases]);

  const refreshUserEnabledTools = useCallback(
    async (options?: { force?: boolean }) => {
      try {
        const list = await getEnabledOptionalTools({ force: options?.force });
        setUserEnabledTools(list);
      } catch {
        setUserEnabledTools([]);
      }
    },
    [],
  );

  /* Load user tool prefs */
  useEffect(() => {
    void refreshUserEnabledTools({ force: true });
  }, [refreshUserEnabledTools]);

  const refreshLLMOptions = useCallback(async () => {
    setLLMOptionsLoading(true);
    try {
      const payload = await listLLMOptions();
      setLLMOptions(payload.options);
      setActiveLLMDefault(payload.active);
      setLLMOptionsError(false);
    } catch {
      setLLMOptionsError(true);
      setLLMOptions([]);
      setActiveLLMDefault(null);
    } finally {
      setLLMOptionsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshLLMOptions();
  }, [refreshLLMOptions]);

  useEffect(() => {
    if (state.llmSelection || !activeLLMDefault) return;
    setLLMSelection(activeLLMDefault);
  }, [activeLLMDefault, setLLMSelection, state.llmSelection]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const refresh = () => {
      void refreshKnowledgeBases({ force: true });
      void refreshLLMOptions();
      // Picks up toggles the user changed in another tab (/settings/tools).
      invalidateEnabledOptionalToolsCache();
      void refreshUserEnabledTools({ force: true });
    };
    const refreshWhenVisible = () => {
      if (document.visibilityState === "visible") refresh();
    };
    window.addEventListener("focus", refresh);
    window.addEventListener("pageshow", refresh);
    document.addEventListener("visibilitychange", refreshWhenVisible);
    return () => {
      window.removeEventListener("focus", refresh);
      window.removeEventListener("pageshow", refresh);
      document.removeEventListener("visibilitychange", refreshWhenVisible);
    };
  }, [refreshKnowledgeBases, refreshLLMOptions, refreshUserEnabledTools]);

  useEffect(() => {
    setCapabilityConfigs(loadCapabilityPlaygroundConfigs());
  }, []);

  /* URL query params (capability, tool) */
  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = new URLSearchParams(window.location.search);
    const qc = p.get("capability");
    const qt = p.getAll("tool");
    if (qc !== null) handleSelectCapability(qc || "");
    else if (qt.length) {
      const valid = qt.filter((t): t is ToolName =>
        ALL_TOOLS.some((d) => d.name === t),
      );
      if (valid.length) setTools(Array.from(new Set(valid)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
        spaceMenuRef.current &&
        !spaceMenuRef.current.contains(t) &&
        spaceBtnRef.current &&
        !spaceBtnRef.current.contains(t)
      )
        setSpaceMenuOpen(false);
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

  // Keep state.enabledTools = (user's toggleable set) ∩ (capability's allowed
  // set). Re-runs when the user flips a toggle in /settings/tools or when
  // the active capability changes. The composer no longer owns this — the
  // /settings/tools page is the single switchboard.
  useEffect(() => {
    if (userEnabledTools === null) return;
    const allowed = new Set(activeCap.allowedTools);
    const next = userEnabledTools.filter((tool) =>
      allowed.has(tool as ToolName),
    );
    const current = state.enabledTools;
    const same =
      current.length === next.length &&
      current.every((tool, idx) => tool === next[idx]);
    if (!same) setTools(next);
  }, [activeCap.allowedTools, setTools, state.enabledTools, userEnabledTools]);

  /* ---- handlers ---- */

  const handleSelectCapability = useCallback(
    (value: string) => {
      const cap =
        CAPABILITIES.find((c) => c.value === value) ?? CAPABILITIES[0];
      const storageKey = cap.value || "chat";
      const config = resolveCapabilityPlaygroundConfig(
        capabilityConfigs,
        storageKey,
        cap.allowedTools,
      );
      setCapability(cap.value || null);
      // Per-capability tool selection now derives from the user's saved
      // settings (/settings/tools) intersected with the capability's
      // allow-list. Playground-saved configs still override when the user
      // explicitly pinned tools in the playground for this capability.
      const baseline =
        userEnabledTools === null ? cap.allowedTools : userEnabledTools;
      const enabledToolsForCap = capabilityConfigs[storageKey]
        ? [...config.enabledTools]
        : baseline.filter((tool) =>
            cap.allowedTools.includes(tool as ToolName),
          );
      setTools(enabledToolsForCap);
      if (config.knowledgeBase) setKBs([config.knowledgeBase]);
      // Switching capability invalidates any prior config confirmation —
      // the new capability has its own form that needs explicit confirm.
      setCapabilityConfigConfirmed(false);
      setCapMenuOpen(false);
    },
    [capabilityConfigs, setCapability, setKBs, setTools, userEnabledTools],
  );

  const fileToAttachment = useCallback(
    (f: File): Promise<PendingAttachment> =>
      new Promise((resolve, reject) => {
        readFileAsDataUrl(f)
          .then((raw) => {
            // SVG: treat as file (text extraction on server, vision models
            // reject SVG) but keep the data URL so the chip can render a
            // thumbnail via a raw <img> tag.
            const svg = isSvgFilename(f.name) || f.type === "image/svg+xml";
            const isImage = !svg && f.type.startsWith("image/");
            const b64 = extractBase64FromDataUrl(raw);
            resolve({
              type: isImage ? "image" : "file",
              filename: f.name,
              base64: b64,
              previewUrl: isImage || svg ? raw : undefined,
              size: f.size,
              mimeType: f.type || undefined,
            });
          })
          .catch(reject);
      }),
    [],
  );

  const showAttachmentError = useCallback((message: string) => {
    setAttachmentError(message);
    if (attachmentErrorTimer.current) {
      clearTimeout(attachmentErrorTimer.current);
    }
    attachmentErrorTimer.current = setTimeout(() => {
      setAttachmentError(null);
      attachmentErrorTimer.current = null;
    }, 4000);
  }, []);

  const filterAndReportFiles = useCallback(
    (files: File[]): File[] => {
      let runningTotal = attachments.reduce((s, a) => s + (a.size ?? 0), 0);
      const accepted: File[] = [];
      const rejected: {
        name: string;
        reason: "unsupported" | "too_large" | "quota";
      }[] = [];
      for (const f of files) {
        const kind = classifyFile(f);
        if (!kind) {
          rejected.push({ name: f.name, reason: "unsupported" });
          continue;
        }
        if (f.size > MAX_ATTACHMENT_BYTES) {
          rejected.push({ name: f.name, reason: "too_large" });
          continue;
        }
        if (runningTotal + f.size > MAX_TOTAL_ATTACHMENT_BYTES) {
          rejected.push({ name: f.name, reason: "quota" });
          break;
        }
        runningTotal += f.size;
        accepted.push(f);
      }
      if (rejected.length) {
        const first = rejected[0];
        let msg: string;
        if (first.reason === "too_large") {
          msg = t("File too large: {{name}}", { name: first.name });
        } else if (first.reason === "quota") {
          msg = t("Too many files, skipped some");
        } else {
          msg = t("Unsupported file type: {{name}}", { name: first.name });
        }
        showAttachmentError(msg);
      }
      return accepted;
    },
    [attachments, showAttachmentError, t],
  );

  const handlePaste = useCallback(
    async (event: React.ClipboardEvent) => {
      const items = Array.from(event.clipboardData.items);
      const files = items
        .filter((item) => item.kind === "file")
        .map((item) => item.getAsFile())
        .filter((f): f is File => f !== null);
      const accepted = filterAndReportFiles(files);
      if (!accepted.length) return;
      event.preventDefault();
      const next = await Promise.all(accepted.map(fileToAttachment));
      setAttachments((prev) => [...prev, ...next]);
    },
    [fileToAttachment, filterAndReportFiles],
  );

  const removeAttachment = useCallback((index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handlePreviewPendingAttachment = useCallback(
    (index: number) => {
      const a = attachments[index];
      if (!a) return;
      setPreviewSource({
        filename: a.filename,
        mimeType: a.mimeType,
        type: a.type,
        base64: a.base64,
        size: a.size,
      });
    },
    [attachments],
  );

  // Fold all messages once per state.messages change to power the
  // SessionActivityPanel on the right (tools, KBs, space refs, attachments).
  const sessionActivity = useMemo(
    () => buildSessionActivity(state.messages),
    [state.messages],
  );

  /**
   * Capability-config card rendered at the bottom of the Activity panel.
   *
   * Returns null for capabilities that don't need explicit configuration
   * (Chat / Solve) — the Activity panel falls back to its standard
   * sections (tools, KBs, space, attachments) plus the empty-state card.
   *
   * For Quiz / Animator / Visualize / Research, we wrap the matching bare
   * ConfigPanel in a `CapabilityConfigCard` that provides the header,
   * Confirm button, and validation-error display. The Confirm gate is
   * wired through `capabilityConfigConfirmed` / `handleConfirmCapabilityConfig`.
   */
  const capabilityConfigSection = useMemo(() => {
    if (!capabilityNeedsConfig) return null;
    if (isQuizMode) {
      return (
        <CapabilityConfigCard
          capability="deep_question"
          confirmed={capabilityConfigConfirmed}
          canConfirm
          onConfirm={handleConfirmCapabilityConfig}
        >
          <QuizConfigPanel
            value={quizConfig}
            onChange={handleChangeQuizConfig}
            uploadedPdf={quizPdf}
            onUploadPdf={handleUploadQuizPdf}
          />
        </CapabilityConfigCard>
      );
    }
    if (isVisualizeMode) {
      return (
        <CapabilityConfigCard
          capability="visualize"
          confirmed={capabilityConfigConfirmed}
          canConfirm
          onConfirm={handleConfirmCapabilityConfig}
        >
          <VisualizeConfigPanel
            value={visualizeConfig}
            onChange={handleChangeVisualizeConfig}
          />
        </CapabilityConfigCard>
      );
    }
    // Research: forward validation errors so the user sees what's missing
    // before they hit Confirm. `canConfirm` only flips false when there's
    // an actual error (e.g. mode/depth not selected).
    const researchErrorMessages = Object.values(researchValidation.errors);
    return (
      <CapabilityConfigCard
        capability="deep_research"
        confirmed={capabilityConfigConfirmed}
        canConfirm={researchErrorMessages.length === 0}
        validationErrors={researchErrorMessages}
        onConfirm={handleConfirmCapabilityConfig}
      >
        <ResearchConfigPanel
          value={researchConfig}
          errors={researchValidation.errors}
          onChange={handleChangeResearchConfig}
        />
      </CapabilityConfigCard>
    );
  }, [
    capabilityNeedsConfig,
    isQuizMode,
    isVisualizeMode,
    capabilityConfigConfirmed,
    handleConfirmCapabilityConfig,
    quizConfig,
    quizPdf,
    handleChangeQuizConfig,
    handleUploadQuizPdf,
    visualizeConfig,
    handleChangeVisualizeConfig,
    researchConfig,
    researchValidation.errors,
    handleChangeResearchConfig,
  ]);

  const viewerPanelRef = useRef<SessionViewerPanelHandle | null>(null);
  // Clicking an attachment (from the Activity panel or from a chat message)
  // routes into the Viewer panel as a new file tab. The viewer auto-opens
  // and the preference is persisted so a follow-up click feels instant.
  const handlePreviewMessageAttachment = useCallback((a: MessageAttachment) => {
    viewerPanelRef.current?.openFileTab(a);
  }, []);

  // Event-delegated link interception inside the messages container. When
  // the user clicks an http(s) link in an assistant message, we open it as
  // a Viewer tab instead of letting the browser navigate / open a new tab.
  // Cmd/ctrl/shift + click keep their standard meaning (open in browser).
  const handleMessagesClick = useCallback((event: React.MouseEvent) => {
    if (event.defaultPrevented) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)
      return;
    if (event.button !== 0) return;
    const target = event.target as HTMLElement | null;
    if (!target) return;
    const anchor = target.closest<HTMLAnchorElement>("a[href]");
    if (!anchor) return;
    const href = anchor.getAttribute("href");
    if (!href) return;
    if (!/^https?:\/\//i.test(href)) return;
    event.preventDefault();
    viewerPanelRef.current?.openWebTab(href);
  }, []);

  const handleClosePreview = useCallback(() => {
    setPreviewSource(null);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current += 1;
    if (e.dataTransfer.types.includes("Files")) setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current -= 1;
    if (dragCounter.current === 0) setDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);
      dragCounter.current = 0;
      const accepted = filterAndReportFiles(Array.from(e.dataTransfer.files));
      if (!accepted.length) return;
      const next = await Promise.all(accepted.map(fileToAttachment));
      setAttachments((prev) => [...prev, ...next]);
    },
    [fileToAttachment, filterAndReportFiles],
  );

  const handleAddFiles = useCallback(
    async (files: File[]) => {
      const accepted = filterAndReportFiles(files);
      if (!accepted.length) return;
      const next = await Promise.all(accepted.map(fileToAttachment));
      setAttachments((prev) => [...prev, ...next]);
    },
    [fileToAttachment, filterAndReportFiles],
  );

  const handleSend = useCallback(
    async (content: string) => {
      if (
        (!content &&
          !attachments.length &&
          !selectedBookReferences.length &&
          !selectedNotebookRecords.length &&
          !selectedHistorySessions.length &&
          !selectedQuestionEntries.length &&
          !selectedSkills.length &&
          !skillsAutoMode &&
          !selectedMemoryFiles.length) ||
        state.isStreaming
      )
        return;

      let extraAttachments = attachments.map((a) => ({
        type: a.type,
        filename: a.filename,
        base64: a.base64,
        mime_type: a.mimeType,
      }));
      let config: Record<string, unknown> | undefined;

      if (isQuizMode) {
        config = buildQuizWSConfig(quizConfig);
        if (quizConfig.mode === "mimic" && quizPdf) {
          const b64 = extractBase64FromDataUrl(
            await readFileAsDataUrl(quizPdf),
          );
          extraAttachments = [
            ...extraAttachments,
            {
              type: "pdf",
              filename: quizPdf.name,
              base64: b64,
              mime_type: "application/pdf",
            },
          ];
        }
      }
      if (isVisualizeMode) config = buildVisualizeWSConfig(visualizeConfig);
      if (isResearchMode) config = buildResearchWSConfig(researchConfig);

      const skillsPayload = skillsAutoMode ? ["auto"] : [...selectedSkills];
      const memoryPayload = [...memoryReferencesPayload];
      const messageContent =
        content ||
        (selectedNotebookRecords.length ||
        selectedBookReferences.length ||
        selectedHistorySessions.length ||
        selectedQuestionEntries.length ||
        skillsPayload.length ||
        memoryPayload.length
          ? t("Please use the selected context to help with this request.")
          : "") ||
        (attachments.some((a) => a.type === "image")
          ? t("Please analyze the attached image(s).")
          : "");
      sendMessage(
        messageContent,
        extraAttachments,
        config,
        notebookReferencesPayload,
        historyReferencesPayload,
        { bookReferences: bookReferencesPayload },
        questionNotebookReferencesPayload,
        skillsPayload,
        memoryPayload,
      );
      shouldAutoScrollRef.current = true;
      setAttachments([]);
      setSelectedBookReferences([]);
      setSelectedNotebookRecords([]);
      setSelectedHistorySessions([]);
      setSelectedQuestionEntries([]);
      setSelectedSkills([]);
      setSkillsAutoMode(false);
      setSelectedMemoryFiles([]);
    },
    [
      attachments,
      bookReferencesPayload,
      historyReferencesPayload,
      isQuizMode,
      isResearchMode,
      isVisualizeMode,
      memoryReferencesPayload,
      notebookReferencesPayload,
      questionNotebookReferencesPayload,
      quizConfig,
      quizPdf,
      researchConfig,
      selectedHistorySessions.length,
      selectedMemoryFiles.length,
      selectedBookReferences.length,
      selectedNotebookRecords.length,
      selectedQuestionEntries.length,
      selectedSkills,
      skillsAutoMode,
      sendMessage,
      shouldAutoScrollRef,
      state.isStreaming,
      t,
      visualizeConfig,
    ],
  );

  const handleConfirmOutline = useCallback(
    (
      outline: OutlineItem[],
      _topic: string,
      originalConfig?: Record<string, unknown> | null,
      originalSnapshot?: MessageRequestSnapshot | null,
    ) => {
      const config: Record<string, unknown> = {
        ...(originalConfig ?? {
          mode: researchConfig.mode,
          depth: researchConfig.depth,
        }),
        confirmed_outline: outline,
      };
      const requestSnapshotOverride: MessageRequestSnapshot | undefined =
        originalSnapshot
          ? {
              ...originalSnapshot,
              content: _topic,
              capability: "deep_research",
              config,
            }
          : undefined;
      sendMessage(
        _topic,
        originalSnapshot?.attachments ?? [],
        config,
        originalSnapshot?.notebookReferences,
        originalSnapshot?.historyReferences,
        {
          displayUserMessage: false,
          persistUserMessage: false,
          requestSnapshotOverride,
          bookReferences: originalSnapshot?.bookReferences,
        },
        originalSnapshot?.questionNotebookReferences,
        originalSnapshot?.skills,
        originalSnapshot?.memoryReferences,
      );
      shouldAutoScrollRef.current = true;
    },
    [researchConfig, sendMessage, shouldAutoScrollRef],
  );

  const handleRegenerateMessage = useCallback(() => {
    regenerateLastMessage();
  }, [regenerateLastMessage]);

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
  const handleSelectNotebookPicker = useCallback(() => {
    setShowNotebookPicker(true);
  }, []);
  const handleSelectBookPicker = useCallback(() => {
    setShowBookPicker(true);
  }, []);
  const handleSelectHistoryPicker = useCallback(() => {
    setShowHistoryPicker(true);
  }, []);
  const handleSelectQuestionBankPicker = useCallback(() => {
    setShowQuestionBankPicker(true);
  }, []);
  const handleSelectSkillsPicker = useCallback(() => {
    setShowSkillsPicker(true);
  }, []);
  const handleSelectMemoryPicker = useCallback(() => {
    setShowMemoryPicker(true);
  }, []);
  const handleRemoveHistory = useCallback((sessionId: string) => {
    setSelectedHistorySessions((prev) =>
      prev.filter((item) => item.sessionId !== sessionId),
    );
  }, []);
  const handleRemoveNotebook = useCallback((notebookId: string) => {
    setSelectedNotebookRecords((prev) =>
      prev.filter((record) => record.notebookId !== notebookId),
    );
  }, []);
  const handleRemoveBookReference = useCallback((bookId: string) => {
    setSelectedBookReferences((prev) =>
      prev.filter((record) => record.bookId !== bookId),
    );
  }, []);
  const handleRemoveQuestion = useCallback((entryId: number) => {
    setSelectedQuestionEntries((prev) =>
      prev.filter((entry) => entry.id !== entryId),
    );
  }, []);
  const handleToggleSkill = useCallback((name: string) => {
    setSkillsAutoMode(false);
    setSelectedSkills((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name],
    );
  }, []);

  const handleSetSkillsAuto = useCallback((auto: boolean) => {
    setSkillsAutoMode(auto);
    if (auto) setSelectedSkills([]);
  }, []);

  const handleToggleMemoryFile = useCallback((file: SpaceMemoryFile) => {
    setSelectedMemoryFiles((prev) =>
      prev.includes(file)
        ? prev.filter((item) => item !== file)
        : [...prev, file],
    );
  }, []);

  const handleCloseNotebookPicker = useCallback(() => {
    setShowNotebookPicker(false);
  }, []);
  const handleCloseBookPicker = useCallback(() => {
    setShowBookPicker(false);
  }, []);
  const handleApplyBookReferences = useCallback(
    (references: SelectedBookReference[]) => {
      setSelectedBookReferences(references);
    },
    [],
  );
  const handleApplyNotebookRecords = useCallback(
    (records: SelectedRecord[]) => {
      setSelectedNotebookRecords(records);
    },
    [],
  );
  const handleCloseHistoryPicker = useCallback(() => {
    setShowHistoryPicker(false);
  }, []);
  const handleApplyHistorySessions = useCallback(
    (sessions: SelectedHistorySession[]) => {
      setSelectedHistorySessions(sessions);
    },
    [],
  );
  const handleCloseQuestionBankPicker = useCallback(() => {
    setShowQuestionBankPicker(false);
  }, []);
  const handleApplyQuestionEntries = useCallback(
    (entries: SelectedQuestionEntry[]) => {
      setSelectedQuestionEntries(entries);
    },
    [],
  );
  const handleCloseSkillsPicker = useCallback(() => {
    setShowSkillsPicker(false);
  }, []);
  const handleApplySkillsSelection = useCallback(
    (selection: { auto: boolean; skills: string[] }) => {
      setSkillsAutoMode(selection.auto);
      setSelectedSkills(selection.auto ? [] : selection.skills);
    },
    [],
  );
  const handleCloseMemoryPicker = useCallback(() => {
    setShowMemoryPicker(false);
  }, []);
  const handleApplyMemoryFiles = useCallback((files: SpaceMemoryFile[]) => {
    setSelectedMemoryFiles(files);
  }, []);
  const handleCloseSaveModal = useCallback(() => {
    setShowSaveModal(false);
  }, []);

  const handleNewChat = useCallback(() => {
    router.push("/chat");
  }, [router]);

  const handleDownloadMarkdown = useCallback(() => {
    if (!state.messages.length) return;
    const title =
      state.messages
        .find((msg) => msg.role === "user")
        ?.content.trim()
        .slice(0, 80) || "Chat Session";
    downloadChatMarkdown(state.messages, { title });
  }, [state.messages]);

  return (
    <QuizFollowupProvider>
      <GeogebraTabProvider>
        <QuizFollowupBridge viewerPanelRef={viewerPanelRef} />
        <GeogebraTabBridge viewerPanelRef={viewerPanelRef} />
        <div
          // When the preview drawer is open AND the viewport is wide enough,
          // push the chat content to the left by the drawer's width so the two
          // panels live side-by-side (matches Claude desktop). On smaller
          // screens the drawer overlays — squeezing a phone-width chat into
          // the remaining ~30 px would be useless. The actual padding +
          // transition lives in `chat-preview-shell` (globals.css) so we can
          // hand-tune it without fighting Tailwind's arbitrary-value parser.
          data-preview-open={previewSource ? "true" : "false"}
          data-activity-open={activityPanelOpen ? "true" : "false"}
          data-viewer-open={viewerPanelOpen ? "true" : "false"}
          className="chat-preview-shell flex h-full flex-col overflow-hidden bg-[var(--background)]"
        >
          <div
            ref={headerRef}
            className="mx-auto flex w-full max-w-[960px] flex-wrap items-center justify-between gap-x-3 gap-y-1.5 px-6 pt-3 pb-0"
          >
            <div className="group/title min-w-0 flex flex-1 items-center gap-2">
              {sessionTitleEditing ? (
                <input
                  ref={titleInputRef}
                  value={sessionTitleDraft}
                  onChange={(event) => setSessionTitleDraft(event.target.value)}
                  onBlur={() => void commitSessionTitleEdit()}
                  onKeyDown={handleSessionTitleKeyDown}
                  disabled={sessionTitleSaving}
                  aria-label={t("Session title")}
                  className="min-w-0 flex-1 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-[15px] font-semibold tracking-[-0.01em] text-[var(--foreground)] shadow-sm outline-none transition focus:border-[var(--ring)] focus:ring-2 focus:ring-[var(--ring)]/20 disabled:opacity-60"
                  maxLength={100}
                />
              ) : (
                <button
                  type="button"
                  onClick={startSessionTitleEdit}
                  disabled={!canRenameSession}
                  title={
                    canRenameSession
                      ? t("Click to rename session")
                      : t("Start a conversation to rename")
                  }
                  className="inline-flex min-w-0 max-w-full items-center gap-2 rounded-xl px-2 py-1 text-left text-[15px] font-semibold tracking-[-0.01em] text-[var(--foreground)] transition hover:bg-[var(--muted)]/55 disabled:cursor-default disabled:hover:bg-transparent"
                >
                  <span className="truncate">{displaySessionTitle}</span>
                  {canRenameSession ? (
                    <PenLine className="h-3.5 w-3.5 shrink-0 text-[var(--muted-foreground)] opacity-0 transition-opacity group-hover/title:opacity-100" />
                  ) : null}
                </button>
              )}
              {sessionTitleSaving ? (
                <span className="shrink-0 text-xs text-[var(--muted-foreground)]">
                  {t("Saving...")}
                </span>
              ) : null}
              {sessionTitleError ? (
                <span className="shrink-0 text-xs text-[var(--destructive)]">
                  {sessionTitleError}
                </span>
              ) : null}
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-1.5">
              <HeaderActionButton
                compact={headerCompact}
                onClick={() => setShowSaveModal(true)}
                disabled={!chatSavePayload}
                icon={BookmarkPlus}
                label={t("Save to Notebook")}
              />
              <HeaderActionButton
                compact={headerCompact}
                onClick={handleDownloadMarkdown}
                disabled={!state.messages.length}
                icon={Download}
                label={t("Download Markdown")}
                title={t("Download chat history as Markdown")}
              />
              <HeaderActionButton
                compact={headerCompact}
                onClick={handleNewChat}
                icon={SquarePen}
                label={t("New chat")}
              />
              <HeaderActionButton
                compact={headerCompact}
                onClick={toggleActivityPanel}
                active={activityPanelOpen}
                icon={PanelRight}
                label={t("Activity")}
                title={t("Session activity")}
              />
              <HeaderActionButton
                compact={headerCompact}
                onClick={toggleViewerPanel}
                active={viewerPanelOpen}
                icon={BookOpen}
                label={t("Viewer")}
                title={t("Open viewer")}
              />
            </div>
          </div>
          <div className="mx-auto flex w-full max-w-[960px] flex-1 min-h-0 flex-col overflow-hidden px-6">
            {!hasMessages ? (
              <div className="flex flex-1 min-h-0 flex-col items-center justify-end pb-14 animate-fade-in">
                <div className="flex items-center justify-center gap-4">
                  <img
                    src="/logo_black.png"
                    alt="DeepTutor"
                    width={40}
                    height={40}
                    className="h-10 w-10 select-none"
                    draggable={false}
                  />
                  <h1 className="font-serif text-[44px] font-medium leading-[1.1] tracking-[-0.015em] text-[var(--foreground)]">
                    {t(welcomeGreeting)}
                  </h1>
                </div>
              </div>
            ) : (
              <div
                ref={messagesContainerRef}
                data-chat-scroll-root="true"
                onScroll={handleMessagesScroll}
                onClick={handleMessagesClick}
                className={`mx-auto w-full flex-1 min-h-0 space-y-7 overflow-y-auto pr-4 [scrollbar-gutter:stable] ${hasMessages ? "pt-6" : "pt-2 pb-6"}`}
                style={
                  hasMessages
                    ? (() => {
                        // The bottom 40 px of the messages area fades to
                        // transparent so content "dissolves" into the composer
                        // gutter. Without enough bottom padding, the fade
                        // overlaps the last assistant paragraph and looks like
                        // a stuck scroll — the user reaches scrollHeight but
                        // can still see only a faded sliver of text. paddingBottom
                        // is sized so the fade falls over empty space.
                        const maskImage =
                          "linear-gradient(to bottom, transparent 0px, #000 32px, #000 calc(100% - 40px), transparent 100%)";
                        return {
                          paddingBottom: "48px",
                          WebkitMaskImage: maskImage,
                          maskImage,
                        };
                      })()
                    : undefined
                }
              >
                <ChatMessageList
                  messages={state.messages}
                  isStreaming={state.isStreaming}
                  sessionId={state.sessionId}
                  language={state.language}
                  onAnswerNow={handleAnswerNow}
                  onCopyAssistantMessage={copyAssistantMessage}
                  onRegenerateMessage={handleRegenerateMessage}
                  onConfirmOutline={handleConfirmOutline}
                  onPreviewAttachment={handlePreviewMessageAttachment}
                  onDeleteTurn={deleteTurn}
                  selectedBranches={state.selectedBranches}
                  onEditMessage={editMessage}
                  onSwitchBranch={switchBranch}
                  onSubmitUserReply={submitUserReply}
                />
                <div ref={messagesEndRef} className="h-px w-full shrink-0" />
              </div>
            )}

            <ChatComposer
              composerRef={composerRef}
              capMenuRef={capMenuRef}
              capBtnRef={capBtnRef}
              spaceMenuRef={spaceMenuRef}
              spaceBtnRef={spaceBtnRef}
              kbMenuRef={kbMenuRef}
              kbBtnRef={kbBtnRef}
              dragCounter={dragCounter}
              dragging={dragging}
              capMenuOpen={capMenuOpen}
              spaceMenuOpen={spaceMenuOpen}
              kbMenuOpen={kbMenuOpen}
              hasMessages={hasMessages}
              attachments={attachments}
              attachmentError={attachmentError}
              activeCap={activeCap}
              knowledgeBases={knowledgeBases}
              llmOptions={llmOptions}
              activeLLMDefault={activeLLMDefault}
              llmSelection={state.llmSelection}
              llmOptionsLoading={llmOptionsLoading}
              llmOptionsError={llmOptionsError}
              selectedBookReferences={selectedBookReferences}
              selectedNotebookRecords={selectedNotebookRecords}
              selectedHistorySessions={selectedHistorySessions}
              selectedQuestionEntries={selectedQuestionEntries}
              notebookReferenceGroups={notebookReferenceGroups}
              selectedSkills={selectedSkills}
              skillsAutoMode={skillsAutoMode}
              selectedMemoryFiles={selectedMemoryFiles}
              selectedKnowledgeBases={state.knowledgeBases}
              isStreaming={state.isStreaming}
              isVisualizeMode={isVisualizeMode}
              capabilityNeedsConfig={capabilityNeedsConfig}
              capabilityConfigConfirmed={capabilityConfigConfirmed}
              onRequestConfigConfirm={ensureActivityPanelOpen}
              capabilities={CAPABILITIES}
              onSetCapMenuOpen={setCapMenuOpen}
              onSetSpaceMenuOpen={setSpaceMenuOpen}
              onSetKbMenuOpen={setKbMenuOpen}
              onToggleKB={handleToggleKB}
              onSelectLLM={setLLMSelection}
              onSelectNotebookPicker={handleSelectNotebookPicker}
              onSelectBookPicker={handleSelectBookPicker}
              onSelectHistoryPicker={handleSelectHistoryPicker}
              onSelectQuestionBankPicker={handleSelectQuestionBankPicker}
              onSelectSkillsPicker={handleSelectSkillsPicker}
              onSelectMemoryPicker={handleSelectMemoryPicker}
              onToggleSkill={handleToggleSkill}
              onSetSkillsAuto={handleSetSkillsAuto}
              onToggleMemoryFile={handleToggleMemoryFile}
              onSend={handleSend}
              onRemoveAttachment={removeAttachment}
              onPreviewAttachment={handlePreviewPendingAttachment}
              onRemoveHistory={handleRemoveHistory}
              onRemoveBookReference={handleRemoveBookReference}
              onRemoveNotebook={handleRemoveNotebook}
              onRemoveQuestion={handleRemoveQuestion}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onPaste={handlePaste}
              onAddFiles={handleAddFiles}
              onSelectCapability={handleSelectCapability}
              onCancelStreaming={cancelStreamingTurn}
              prefillInputRef={prefillInputRef}
            />
            <div
              aria-hidden="true"
              className="shrink-0"
              style={{
                flexGrow: hasMessages ? 0 : 1.4,
                transition: "flex-grow 650ms cubic-bezier(0.16, 1, 0.3, 1)",
              }}
            />
          </div>
          <NotebookRecordPicker
            open={showNotebookPicker}
            onClose={handleCloseNotebookPicker}
            onApply={handleApplyNotebookRecords}
          />
          <BookReferencePicker
            open={showBookPicker}
            initialReferences={selectedBookReferences}
            onClose={handleCloseBookPicker}
            onApply={handleApplyBookReferences}
          />
          <HistorySessionPicker
            open={showHistoryPicker}
            onClose={handleCloseHistoryPicker}
            onApply={handleApplyHistorySessions}
          />
          <QuestionBankPicker
            open={showQuestionBankPicker}
            onClose={handleCloseQuestionBankPicker}
            onApply={handleApplyQuestionEntries}
          />
          <SkillsPicker
            open={showSkillsPicker}
            initialAuto={skillsAutoMode}
            initialSkills={selectedSkills}
            onClose={handleCloseSkillsPicker}
            onApply={handleApplySkillsSelection}
          />
          <MemoryPicker
            open={showMemoryPicker}
            initialFiles={selectedMemoryFiles}
            onClose={handleCloseMemoryPicker}
            onApply={handleApplyMemoryFiles}
          />
          <SaveToNotebookModal
            open={showSaveModal}
            payload={chatSavePayload}
            messages={chatSaveMessages}
            onClose={handleCloseSaveModal}
          />
          <FilePreviewDrawer
            open={previewSource !== null}
            source={previewSource}
            onClose={handleClosePreview}
          />
          <SessionActivityPanel
            open={
              activityPanelOpen && previewSource === null && !viewerPanelOpen
            }
            activity={sessionActivity}
            onOpenAttachment={handlePreviewMessageAttachment}
            configSection={capabilityConfigSection}
          />
          <SessionViewerPanel
            ref={viewerPanelRef}
            open={viewerPanelOpen && previewSource === null}
            sessionId={state.sessionId}
            onClose={() => setViewerOpen(false)}
            onAutoOpen={() => setViewerOpen(true)}
          />
        </div>
      </GeogebraTabProvider>
    </QuizFollowupProvider>
  );
}

/**
 * Bridges the SessionViewerPanel's imperative ``openQuizFollowupTab`` into
 * the QuizFollowupController so descendants (QuizViewer) can call
 * ``controller.openFollowupTab(...)`` without prop-drilling the panel ref
 * through several layers of components.
 */
function QuizFollowupBridge({
  viewerPanelRef,
}: {
  viewerPanelRef: React.MutableRefObject<SessionViewerPanelHandle | null>;
}) {
  const controller = useQuizFollowupController();
  useEffect(() => {
    controller.setOpenTabHandler((ctx) => {
      viewerPanelRef.current?.openQuizFollowupTab(ctx);
    });
    return () => controller.setOpenTabHandler(null);
  }, [controller, viewerPanelRef]);
  return null;
}

/**
 * Same shape as QuizFollowupBridge, for the GeoGebra-tab opener exposed
 * to in-message CTAs (the ``ggbscript`` markdown fence becomes a card
 * that calls ``controller.openTab(...)`` here).
 */
function GeogebraTabBridge({
  viewerPanelRef,
}: {
  viewerPanelRef: React.MutableRefObject<SessionViewerPanelHandle | null>;
}) {
  const controller = useGeogebraTabOpener();
  useEffect(() => {
    if (!controller) return;
    controller.setOpenHandler((payload) => {
      viewerPanelRef.current?.openGeogebraTab(payload);
    });
    return () => controller.setOpenHandler(null);
  }, [controller, viewerPanelRef]);
  return null;
}

/**
 * Header action button that auto-collapses to icon-only when the chat
 * column gets squeezed (Viewer panel open, narrow viewport, etc.). The
 * label stays as the button's `title` so hovering an icon still reveals
 * what it does. Optional `active` flag paints the button with a primary
 * tint, used by the panel-toggle buttons to surface their on/off state.
 */
function HeaderActionButton({
  compact,
  onClick,
  disabled,
  active,
  icon: Icon,
  label,
  title,
}: {
  compact: boolean;
  onClick: () => void;
  disabled?: boolean;
  active?: boolean;
  icon: LucideIcon;
  label: string;
  title?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title ?? label}
      aria-label={label}
      aria-pressed={active}
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-lg border text-[12px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
        compact ? "px-2 py-1.5" : "px-3 py-1.5"
      } ${
        active
          ? "border-[var(--primary)]/40 bg-[color-mix(in_srgb,var(--primary)_8%,var(--card))] text-[var(--primary)] hover:border-[var(--primary)]/55"
          : "border-[var(--border)]/50 text-[var(--muted-foreground)] hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:hover:border-[var(--border)]/50 disabled:hover:text-[var(--muted-foreground)]"
      }`}
    >
      <Icon size={14} strokeWidth={1.7} className="shrink-0" />
      {compact ? null : <span>{label}</span>}
    </button>
  );
}
