"use client";

import {
  memo,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type RefObject,
} from "react";
import Image from "next/image";
import {
  ArrowUp,
  AtSign,
  ChevronDown,
  Database,
  Paperclip,
  Square,
  X,
  type LucideIcon,
} from "lucide-react";
import {
  ATTACHMENT_ACCEPT,
  docIconFor,
  formatBytes,
  isSvgFilename,
} from "@/lib/doc-attachments";
import { useTranslation } from "react-i18next";
import type { SelectedHistorySession } from "@/components/chat/HistorySessionPicker";
import type { SelectedQuestionEntry } from "@/components/chat/QuestionBankPicker";
import type { SelectedRecord } from "@/lib/notebook-selection-types";
import type { LLMSelection } from "@/lib/unified-ws";
import type { LLMOption } from "@/lib/llm-options";
import ChatSpaceMenu from "@/components/chat/space/ChatSpaceMenu";
import type { SpaceMemoryFile } from "@/lib/space-items";
import type { SelectedBookReference } from "@/lib/book-references";
import ModelSelector from "./ModelSelector";

type SpaceSelectionCounts = {
  chatHistory: number;
  books: number;
  notebooks: number;
  questionBank: number;
  skills: number;
  memory: number;
};
import { SpaceContextChips } from "./ChatMessages";
import { ComposerInput, type ComposerInputHandle } from "./ComposerInput";

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
}

interface CapabilityDef {
  value: string;
  label: string;
  description: string;
  icon: LucideIcon;
  allowedTools: string[];
}

export default memo(function ChatComposer({
  composerRef,
  capMenuRef,
  capBtnRef,
  spaceMenuRef,
  spaceBtnRef,
  kbMenuRef,
  kbBtnRef,
  dragCounter,
  dragging,
  capMenuOpen,
  spaceMenuOpen,
  kbMenuOpen,
  hasMessages,
  attachments,
  attachmentError,
  activeCap,
  knowledgeBases,
  llmOptions,
  activeLLMDefault,
  llmSelection,
  llmOptionsLoading,
  llmOptionsError,
  selectedNotebookRecords,
  selectedBookReferences,
  selectedHistorySessions,
  selectedQuestionEntries,
  notebookReferenceGroups,
  selectedSkills,
  skillsAutoMode,
  selectedMemoryFiles,
  selectedKnowledgeBases,
  isStreaming,
  isVisualizeMode,
  capabilityNeedsConfig,
  capabilityConfigConfirmed,
  onRequestConfigConfirm,
  capabilities,
  onSetCapMenuOpen,
  onSetSpaceMenuOpen,
  onSetKbMenuOpen,
  onToggleKB,
  onSelectLLM,
  onSelectNotebookPicker,
  onSelectBookPicker,
  onSelectHistoryPicker,
  onSelectQuestionBankPicker,
  onSelectSkillsPicker,
  onSelectMemoryPicker,
  onToggleSkill,
  onSetSkillsAuto,
  onToggleMemoryFile,
  onSend,
  onRemoveAttachment,
  onPreviewAttachment,
  onRemoveHistory,
  onRemoveBookReference,
  onRemoveNotebook,
  onRemoveQuestion,
  onDragEnter,
  onDragLeave,
  onDragOver,
  onDrop,
  onPaste,
  onAddFiles,
  onSelectCapability,
  onCancelStreaming,
  prefillInputRef,
  inputPlaceholder,
}: {
  composerRef: RefObject<HTMLDivElement | null>;
  capMenuRef: RefObject<HTMLDivElement | null>;
  capBtnRef: RefObject<HTMLButtonElement | null>;
  spaceMenuRef: RefObject<HTMLDivElement | null>;
  spaceBtnRef: RefObject<HTMLButtonElement | null>;
  kbMenuRef: RefObject<HTMLDivElement | null>;
  kbBtnRef: RefObject<HTMLButtonElement | null>;
  dragCounter: RefObject<number>;
  dragging: boolean;
  capMenuOpen: boolean;
  spaceMenuOpen: boolean;
  kbMenuOpen: boolean;
  hasMessages: boolean;
  attachments: PendingAttachment[];
  attachmentError: string | null;
  activeCap: CapabilityDef;
  knowledgeBases: KnowledgeBase[];
  llmOptions: LLMOption[];
  activeLLMDefault: LLMSelection | null;
  llmSelection: LLMSelection | null;
  llmOptionsLoading: boolean;
  llmOptionsError: boolean;
  selectedNotebookRecords: SelectedRecord[];
  selectedBookReferences: SelectedBookReference[];
  selectedHistorySessions: SelectedHistorySession[];
  selectedQuestionEntries: SelectedQuestionEntry[];
  notebookReferenceGroups: Array<{
    notebookId: string;
    notebookName: string;
    count: number;
  }>;
  selectedSkills: string[];
  skillsAutoMode: boolean;
  selectedMemoryFiles: SpaceMemoryFile[];
  selectedKnowledgeBases: string[];
  isStreaming: boolean;
  isVisualizeMode: boolean;
  /**
   * True when the active capability (e.g. Quiz / Visualize / Research)
   * requires explicit configuration before sending. When true, `canSend`
   * is gated on `capabilityConfigConfirmed`.
   */
  capabilityNeedsConfig: boolean;
  capabilityConfigConfirmed: boolean;
  /**
   * Called when the user clicks the send button while config is required
   * but not yet confirmed. The page uses this to surface the config card
   * (open the Activity panel, scroll to it, etc.).
   */
  onRequestConfigConfirm: () => void;
  capabilities: CapabilityDef[];
  onSetCapMenuOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  onSetSpaceMenuOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  onSetKbMenuOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  onToggleKB: (name: string) => void;
  onSelectLLM: (selection: LLMSelection | null) => void;
  onSelectNotebookPicker: () => void;
  onSelectBookPicker: () => void;
  onSelectHistoryPicker: () => void;
  onSelectQuestionBankPicker: () => void;
  onSelectSkillsPicker: () => void;
  onSelectMemoryPicker: () => void;
  onToggleSkill: (skill: string) => void;
  onSetSkillsAuto: (auto: boolean) => void;
  onToggleMemoryFile: (file: SpaceMemoryFile) => void;
  onSend: (content: string) => void;
  onRemoveAttachment: (index: number) => void;
  onPreviewAttachment?: (index: number) => void;
  onRemoveHistory: (sessionId: string) => void;
  onRemoveBookReference: (bookId: string) => void;
  onRemoveNotebook: (notebookId: string) => void;
  onRemoveQuestion: (entryId: number) => void;
  onDragEnter: (event: React.DragEvent) => void;
  onDragLeave: (event: React.DragEvent) => void;
  onDragOver: (event: React.DragEvent) => void;
  onDrop: (event: React.DragEvent) => void;
  onPaste: (event: React.ClipboardEvent) => void;
  onAddFiles: (files: File[]) => void;
  onSelectCapability: (value: string) => void;
  onCancelStreaming: () => void;
  /**
   * Optional ref the composer writes its ``prefillInput`` function into
   * once mounted, so the message-list side (specifically
   * ``AskUserOptions`` chips) can drop a string into the textarea
   * without owning the composer's imperative handle directly.
   */
  prefillInputRef?: React.MutableRefObject<((text: string) => void) | null>;
  /** Override the composer placeholder (e.g. quiz follow-up). */
  inputPlaceholder?: string;
}) {
  const { t } = useTranslation();
  const CapIcon = activeCap.icon;

  const [hasContent, setHasContent] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const inputHandleRef = useRef<ComposerInputHandle>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!prefillInputRef) return;
    prefillInputRef.current = (text: string) => {
      inputHandleRef.current?.setValue(text);
    };
    return () => {
      if (prefillInputRef) prefillInputRef.current = null;
    };
  }, [prefillInputRef]);

  // Composer-row compaction: when the available width drops below ~620 px
  // (e.g. the Viewer panel is open or the user is on a narrow viewport),
  // the cap chip + Tools/Attach/Space labels collide. We measure the
  // composer itself and flip those labels to icon-only below the
  // threshold. Count-badges stay visible so users still see how many
  // things are selected.
  const [composerCompact, setComposerCompact] = useState(false);
  useEffect(() => {
    const el = composerRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    setComposerCompact(el.getBoundingClientRect().width < 620);
    const observer = new ResizeObserver(() => {
      if (composerRef.current) {
        setComposerCompact(
          composerRef.current.getBoundingClientRect().width < 620,
        );
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [composerRef]);

  const handlePickFiles = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const picked = Array.from(event.target.files ?? []);
      if (picked.length) onAddFiles(picked);
      // Reset so picking the same file twice still triggers `change`.
      event.target.value = "";
    },
    [onAddFiles],
  );

  useEffect(() => {
    if (!hasMessages) textareaRef.current?.focus();
  }, [hasMessages]);

  // Functional-update form keeps `handleInputChange` identity stable across
  // every keystroke (no `hasContent` in deps), so the memoized ComposerInput
  // doesn't get re-rendered just because we observed a content-empty toggle.
  const handleInputChange = useCallback((val: string) => {
    const next = !!val.trim();
    setHasContent((prev) => (prev === next ? prev : next));
  }, []);

  const doSend = useCallback(
    (content: string) => {
      onSend(content);
      setHasContent(false);
      inputHandleRef.current?.clear();
    },
    [onSend],
  );

  const hasReferences =
    !!attachments.length ||
    !!selectedBookReferences.length ||
    !!selectedNotebookRecords.length ||
    !!selectedHistorySessions.length ||
    !!selectedQuestionEntries.length ||
    !!selectedSkills.length ||
    skillsAutoMode ||
    !!selectedMemoryFiles.length;

  // `capabilityNeedsConfig && !capabilityConfigConfirmed` blocks send so the
  // user has to click *Confirm* in the right-side Activity panel first.
  // Clicking the send button while in this state surfaces the config card
  // (via `onRequestConfigConfirm`) instead of silently doing nothing.
  const isConfigBlocked = capabilityNeedsConfig && !capabilityConfigConfirmed;
  const canSend =
    (hasContent || hasReferences) && !isStreaming && !isConfigBlocked;

  const skillsCount = skillsAutoMode ? 1 : selectedSkills.length;
  const spaceSelectionCounts: SpaceSelectionCounts = {
    chatHistory: selectedHistorySessions.length,
    books: selectedBookReferences.reduce(
      (total, ref) => total + ref.pages.length,
      0,
    ),
    notebooks: selectedNotebookRecords.length,
    questionBank: selectedQuestionEntries.length,
    skills: skillsCount,
    memory: selectedMemoryFiles.length,
  };
  const spaceSelectionCount =
    spaceSelectionCounts.chatHistory +
    spaceSelectionCounts.books +
    spaceSelectionCounts.notebooks +
    spaceSelectionCounts.questionBank +
    spaceSelectionCounts.skills +
    spaceSelectionCounts.memory;

  const handleManualSend = useCallback(() => {
    if (isConfigBlocked) {
      // Don't silently fail — surface the config card so the user knows
      // they need to confirm settings first.
      onRequestConfigConfirm();
      return;
    }
    if (!canSend) return;
    const content = inputHandleRef.current?.getValue() || "";
    doSend(content);
  }, [canSend, doSend, isConfigBlocked, onRequestConfigConfirm]);

  return (
    <div
      ref={composerRef}
      className={`relative z-20 mx-auto w-full shrink-0 pb-5 ${hasMessages ? "pt-1 max-w-[960px]" : "max-w-[720px]"}`}
      style={{
        transition: "max-width 650ms cubic-bezier(0.16, 1, 0.3, 1)",
      }}
    >
      {hasMessages && (
        <div className="pointer-events-none absolute inset-x-0 top-0 h-6 bg-gradient-to-b from-transparent to-[var(--background)]/72" />
      )}

      <div className="relative">
        <div
          className={`relative rounded-[26px] border bg-[var(--card)] shadow-[0_1px_2px_rgba(0,0,0,0.025),0_10px_28px_-10px_rgba(0,0,0,0.08)] transition-colors ${
            dragging
              ? "border-[var(--primary)] bg-[var(--primary)]/[0.03]"
              : "border-[var(--border)]/55"
          }`}
          onDragEnter={onDragEnter}
          onDragLeave={onDragLeave}
          onDragOver={onDragOver}
          onDrop={onDrop}
          data-drag-counter={dragCounter.current}
        >
          {dragging && (
            <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center rounded-[26px] border-2 border-dashed border-[var(--primary)]/50 bg-[var(--primary)]/[0.04]">
              <div className="flex flex-col items-center gap-1 text-[var(--primary)]">
                <Paperclip size={22} strokeWidth={1.6} />
                <span className="text-[13px] font-medium">
                  {t("Drop files here")}
                </span>
                <span className="text-[11px] text-[var(--primary)]/70">
                  {t("Images, Office docs, code & text")}
                </span>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ATTACHMENT_ACCEPT}
            onChange={handleFileInputChange}
            className="hidden"
            aria-hidden="true"
            tabIndex={-1}
          />

          {hasReferences && (
            <div className="px-4 pt-3.5 [&>div]:mb-0">
              <SpaceContextChips
                historySessions={selectedHistorySessions}
                bookReferences={selectedBookReferences}
                notebookGroups={notebookReferenceGroups}
                questionEntries={selectedQuestionEntries}
                selectedSkills={selectedSkills}
                skillsAutoMode={skillsAutoMode}
                memoryFiles={selectedMemoryFiles}
                onRemoveHistory={onRemoveHistory}
                onRemoveBookReference={onRemoveBookReference}
                onRemoveNotebook={onRemoveNotebook}
                onRemoveQuestion={onRemoveQuestion}
                onRemoveSkill={onToggleSkill}
                onClearSkillsAuto={() => onSetSkillsAuto(false)}
                onRemoveMemoryFile={onToggleMemoryFile}
              />
            </div>
          )}
          <ComposerInput
            ref={inputHandleRef}
            textareaRef={textareaRef}
            isVisualizeMode={isVisualizeMode}
            canSendEmpty={hasReferences}
            onSend={doSend}
            onInputChange={handleInputChange}
            onPaste={onPaste}
            selectedCounts={spaceSelectionCounts}
            onSelectNotebookPicker={onSelectNotebookPicker}
            onSelectBookPicker={onSelectBookPicker}
            onSelectHistoryPicker={onSelectHistoryPicker}
            onSelectQuestionBankPicker={onSelectQuestionBankPicker}
            onSelectSkillsPicker={onSelectSkillsPicker}
            onSelectMemoryPicker={onSelectMemoryPicker}
            placeholder={inputPlaceholder}
            minHeight={hasMessages ? 28 : 88}
          />

          {!!attachments.length && (
            <div className="flex flex-wrap gap-2 px-4 pb-2">
              {attachments.map((a, i) => {
                const previewLabel = t("Preview");
                const removeLabel = t("Remove attachment");
                if (a.type === "image" && a.previewUrl) {
                  return (
                    <div key={`${a.filename}-${i}`} className="group relative">
                      <button
                        type="button"
                        onClick={() => onPreviewAttachment?.(i)}
                        title={a.filename || previewLabel}
                        aria-label={previewLabel}
                        className="relative block h-16 w-16 overflow-hidden rounded-lg border border-[var(--border)] transition-shadow hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]/40"
                      >
                        <Image
                          src={a.previewUrl}
                          alt={a.filename || t("Attachment preview")}
                          fill
                          unoptimized
                          className="object-cover"
                        />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveAttachment(i);
                        }}
                        aria-label={removeLabel}
                        className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--foreground)] text-[var(--background)] opacity-0 shadow-sm transition-opacity group-hover:opacity-100"
                      >
                        <X size={10} />
                      </button>
                    </div>
                  );
                }
                if (isSvgFilename(a.filename) && a.previewUrl) {
                  return (
                    <div
                      key={`${a.filename}-${i}`}
                      className="group relative"
                      title={a.filename}
                    >
                      <button
                        type="button"
                        onClick={() => onPreviewAttachment?.(i)}
                        aria-label={previewLabel}
                        className="relative block h-16 w-16 overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--card)] transition-shadow hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]/40"
                      >
                        {/* Native <img> is safe for SVG: scripts inside an
                            SVG don't execute under <img> context. Next.js
                            <Image> rejects SVG by default. */}
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={a.previewUrl}
                          alt={a.filename || t("Attachment preview")}
                          className="h-full w-full object-contain p-1"
                        />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveAttachment(i);
                        }}
                        aria-label={removeLabel}
                        className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--foreground)] text-[var(--background)] opacity-0 shadow-sm transition-opacity group-hover:opacity-100"
                      >
                        <X size={10} />
                      </button>
                    </div>
                  );
                }
                const spec = docIconFor(a.filename);
                const Icon = spec.Icon;
                const sizeLabel = a.size ? formatBytes(a.size) : "";
                return (
                  <div
                    key={`${a.filename}-${i}`}
                    className="group relative"
                    title={a.filename}
                  >
                    <button
                      type="button"
                      onClick={() => onPreviewAttachment?.(i)}
                      aria-label={previewLabel}
                      className="flex h-16 w-[160px] items-center gap-2.5 rounded-lg border border-[var(--border)] bg-[var(--card)] px-2.5 text-left transition-colors hover:border-[var(--primary)]/40 hover:bg-[var(--muted)]/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]/40"
                    >
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-[var(--muted)]/60">
                        <Icon
                          size={22}
                          strokeWidth={1.5}
                          className={spec.tint}
                        />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-[12px] font-medium text-[var(--foreground)]">
                          {a.filename}
                        </div>
                        <div className="truncate text-[10px] uppercase tracking-wide text-[var(--muted-foreground)]">
                          {sizeLabel
                            ? `${spec.label} · ${sizeLabel}`
                            : spec.label}
                        </div>
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveAttachment(i);
                      }}
                      aria-label={removeLabel}
                      className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--foreground)] text-[var(--background)] opacity-0 shadow-sm transition-opacity group-hover:opacity-100"
                    >
                      <X size={10} />
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {attachmentError && (
            <div className="px-4 pb-2 text-[11px] text-red-600">
              {attachmentError}
            </div>
          )}

          <div className="border-t border-[var(--border)]/35 px-3 py-2">
            <div className="flex items-center gap-2">
              <div className="relative">
                <button
                  ref={capBtnRef}
                  onClick={() => onSetCapMenuOpen((v) => !v)}
                  className={`inline-flex ${composerCompact ? "" : "min-w-[118px]"} shrink-0 items-center justify-between gap-1.5 rounded-full border bg-[var(--card)] px-3 py-[6px] text-[13px] font-medium text-[var(--foreground)] shadow-[0_1px_2px_color-mix(in_srgb,var(--foreground)_4%,transparent)] transition-[background-color,border-color,color,box-shadow] duration-150 ${
                    capMenuOpen
                      ? "border-[var(--primary)]/45 bg-[color-mix(in_srgb,var(--primary)_7%,var(--card))] text-[var(--primary)] shadow-[0_4px_14px_color-mix(in_srgb,var(--primary)_22%,transparent)]"
                      : "border-[var(--border)]/65 hover:border-[var(--primary)]/30 hover:bg-[color-mix(in_srgb,var(--primary)_3%,var(--card))] hover:text-[var(--primary)]"
                  }`}
                >
                  <span className="flex min-w-0 items-center gap-1.5">
                    <CapIcon size={15} strokeWidth={1.7} className="shrink-0" />
                    {composerCompact ? null : (
                      <span className="truncate">{t(activeCap.label)}</span>
                    )}
                  </span>
                  <ChevronDown
                    size={12}
                    strokeWidth={2}
                    className={`-mr-0.5 shrink-0 transition-transform duration-200 ${capMenuOpen ? "rotate-180" : ""}`}
                  />
                </button>

                {capMenuOpen && (
                  <div
                    ref={capMenuRef}
                    className="dt-popup-up absolute bottom-full left-0 z-50 mb-2 w-[280px] rounded-2xl border border-[var(--border)]/70 bg-[var(--popover)] py-1.5 shadow-[0_8px_30px_color-mix(in_srgb,var(--foreground)_18%,transparent)] backdrop-blur-md"
                  >
                    {capabilities.map((cap) => {
                      const Icon = cap.icon;
                      const selected = activeCap.value === cap.value;
                      return (
                        <button
                          key={cap.value}
                          onClick={() => onSelectCapability(cap.value)}
                          className={`flex w-full items-center gap-3 px-3.5 py-2 text-left transition-colors ${
                            selected
                              ? "bg-[var(--muted)]"
                              : "hover:bg-[var(--muted)]/50"
                          }`}
                        >
                          <Icon
                            size={16}
                            strokeWidth={1.6}
                            className={`shrink-0 ${selected ? "text-[var(--primary)]" : "text-[var(--muted-foreground)]"}`}
                          />
                          <div className="min-w-0 flex-1">
                            <div className="text-[13px] font-medium text-[var(--foreground)]">
                              {t(cap.label)}
                            </div>
                            <div className="truncate text-[11px] text-[var(--muted-foreground)]">
                              {t(cap.description)}
                            </div>
                          </div>
                          {selected ? (
                            <div className="h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--primary)]" />
                          ) : null}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="flex min-w-0 flex-1 items-center gap-1">
                <button
                  type="button"
                  onClick={handlePickFiles}
                  title={t("Attach files")}
                  aria-label={t("Attach files")}
                  className="inline-flex shrink-0 items-center gap-1 py-1 px-1.5 text-[11px] font-medium text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
                >
                  <Paperclip size={12} strokeWidth={1.7} />
                  <span className="inline-flex items-baseline">
                    {composerCompact ? null : t("Attach")}
                    {attachments.length > 0 && (
                      <span className="ml-1 flex h-[13px] min-w-[13px] translate-y-[3px] items-center justify-center rounded-full bg-[var(--primary)] px-[3px] text-[8px] font-semibold leading-none text-[var(--primary-foreground)] shadow-[0_1px_3px_color-mix(in_srgb,var(--primary)_35%,transparent)] ring-[1.5px] ring-[var(--card)]">
                        {attachments.length}
                      </span>
                    )}
                  </span>
                </button>

                <div className="relative flex items-center gap-0.5">
                  <button
                    ref={kbBtnRef}
                    type="button"
                    onClick={() => onSetKbMenuOpen((v) => !v)}
                    disabled={knowledgeBases.length === 0}
                    title={
                      knowledgeBases.length === 0
                        ? t("No knowledge bases available")
                        : t("Attach knowledge bases")
                    }
                    className={`inline-flex shrink-0 items-center gap-1 py-1 px-1.5 text-[11px] font-medium transition-colors ${
                      knowledgeBases.length === 0
                        ? "cursor-not-allowed text-[var(--border)]"
                        : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    <Database size={12} strokeWidth={1.7} />
                    <span className="inline-flex items-baseline">
                      {composerCompact ? null : t("Knowledge")}
                      {selectedKnowledgeBases.length > 0 && (
                        <span className="ml-1 flex h-[13px] min-w-[13px] translate-y-[3px] items-center justify-center rounded-full bg-[var(--primary)] px-[3px] text-[8px] font-semibold leading-none text-[var(--primary-foreground)] shadow-[0_1px_3px_color-mix(in_srgb,var(--primary)_35%,transparent)] ring-[1.5px] ring-[var(--card)]">
                          {selectedKnowledgeBases.length}
                        </span>
                      )}
                    </span>
                    <ChevronDown
                      size={10}
                      className={`transition-transform ${kbMenuOpen ? "rotate-180" : ""}`}
                    />
                  </button>
                  {kbMenuOpen && knowledgeBases.length > 0 && (
                    <div
                      ref={kbMenuRef}
                      className="absolute bottom-full left-0 z-50 mb-1.5 max-h-[260px] min-w-[200px] max-w-[280px] overflow-y-auto rounded-lg border border-[var(--border)] bg-[var(--popover)] py-1 shadow-lg backdrop-blur-md"
                    >
                      {knowledgeBases.map((kb) => {
                        const active = selectedKnowledgeBases.includes(kb.name);
                        return (
                          <button
                            key={kb.name}
                            type="button"
                            onClick={() => onToggleKB(kb.name)}
                            className={`flex w-full items-center gap-2.5 px-3 py-1.5 text-left text-[12px] transition-colors ${
                              active
                                ? "text-[var(--primary)]"
                                : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                            } hover:bg-[var(--muted)]/40`}
                          >
                            <Database size={13} strokeWidth={1.7} />
                            <span className="flex-1 truncate font-medium">
                              {kb.name}
                            </span>
                            {active && (
                              <div className="h-1.5 w-1.5 rounded-full bg-[var(--primary)]" />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                <div className="relative flex items-center gap-0.5">
                  <button
                    ref={spaceBtnRef}
                    type="button"
                    onClick={() => onSetSpaceMenuOpen((v) => !v)}
                    title={t("Space")}
                    aria-label={t("Space")}
                    className="inline-flex shrink-0 items-center gap-1 py-1 px-1.5 text-[11px] font-medium text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
                  >
                    <AtSign size={12} strokeWidth={1.7} />
                    <span className="inline-flex items-baseline">
                      {composerCompact ? null : t("Space")}
                      {spaceSelectionCount > 0 && (
                        <span className="ml-1 flex h-[13px] min-w-[13px] translate-y-[3px] items-center justify-center rounded-full bg-[var(--primary)] px-[3px] text-[8px] font-semibold leading-none text-[var(--primary-foreground)] shadow-[0_1px_3px_color-mix(in_srgb,var(--primary)_35%,transparent)] ring-[1.5px] ring-[var(--card)]">
                          {spaceSelectionCount}
                        </span>
                      )}
                    </span>
                    <ChevronDown
                      size={10}
                      className={`transition-transform ${spaceMenuOpen ? "rotate-180" : ""}`}
                    />
                  </button>
                  {spaceMenuOpen && (
                    <div
                      ref={spaceMenuRef}
                      className="absolute bottom-full left-0 z-50 mb-1.5"
                    >
                      <ChatSpaceMenu
                        variant="toolbar"
                        selectedCounts={spaceSelectionCounts}
                        onSelectItem={(key) => {
                          onSetSpaceMenuOpen(false);
                          if (key === "chat_history") onSelectHistoryPicker();
                          else if (key === "books") onSelectBookPicker();
                          else if (key === "notebooks")
                            onSelectNotebookPicker();
                          else if (key === "question_bank")
                            onSelectQuestionBankPicker();
                          else if (key === "skills") onSelectSkillsPicker();
                          else if (key === "memory") onSelectMemoryPicker();
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="ml-auto flex shrink-0 items-center gap-1.5">
                <ModelSelector
                  options={llmOptions}
                  activeDefault={activeLLMDefault}
                  value={llmSelection}
                  loading={llmOptionsLoading}
                  error={llmOptionsError}
                  onChange={onSelectLLM}
                />

                {isStreaming ? (
                  <button
                    type="button"
                    onClick={onCancelStreaming}
                    className="group relative inline-flex h-[29px] w-[29px] shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[0_4px_12px_color-mix(in_srgb,var(--primary)_18%,transparent)] transition-[background-color,box-shadow] hover:bg-[var(--primary)]/90 hover:shadow-[0_6px_16px_color-mix(in_srgb,var(--primary)_28%,transparent)]"
                    aria-label={t("Stop generating")}
                    title={t("Stop generating")}
                  >
                    {/* A faint ring slowly rotates around the rim while
                        streaming, signalling "still working — click to
                        cancel". The white square sits front-and-center so
                        the click target is always obvious. */}
                    <span className="pointer-events-none absolute inset-0 rounded-full border-[1.5px] border-white/30 border-t-white/85 animate-spin opacity-90 transition-opacity group-hover:opacity-40" />
                    <Square
                      size={9}
                      strokeWidth={2.6}
                      className="relative z-10 fill-current"
                    />
                  </button>
                ) : (
                  // When the active capability needs an unconfirmed config,
                  // we keep the button clickable (so a click can surface
                  // the Activity-panel config card via
                  // `onRequestConfigConfirm`) but only once the user has
                  // *intent* (typed text or queued references). Without
                  // intent, the button stays disabled so an empty-state
                  // composer doesn't have a "live" send button.
                  <button
                    type="button"
                    onClick={handleManualSend}
                    disabled={!(hasContent || hasReferences) || isStreaming}
                    title={
                      isConfigBlocked
                        ? t("Confirm settings on the right to send.")
                        : undefined
                    }
                    aria-disabled={!canSend}
                    className={`rounded-full p-[7px] shadow-[0_4px_12px_color-mix(in_srgb,var(--primary)_15%,transparent)] transition-[transform,opacity,box-shadow] disabled:opacity-25 disabled:shadow-none ${
                      isConfigBlocked
                        ? "bg-[var(--muted-foreground)]/30 text-[var(--primary-foreground)] hover:bg-[var(--muted-foreground)]/45"
                        : "bg-[var(--primary)] text-[var(--primary-foreground)] hover:shadow-[0_6px_16px_color-mix(in_srgb,var(--primary)_22%,transparent)]"
                    }`}
                    aria-label={t("Send")}
                  >
                    <ArrowUp size={15} strokeWidth={2.5} />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});
