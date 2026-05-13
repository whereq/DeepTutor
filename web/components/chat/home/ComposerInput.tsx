"use client";

import {
  forwardRef,
  memo,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  type RefObject,
} from "react";
import { useTranslation } from "react-i18next";
import ChatSpaceMenu, {
  type ChatSpaceSelectionCounts,
} from "@/components/chat/space/ChatSpaceMenu";
import { shouldSubmitOnEnter } from "@/lib/composer-keyboard";
import { useAutoSizedTextarea } from "@/lib/use-auto-sized-textarea";

interface ComposerInputProps {
  textareaRef: RefObject<HTMLTextAreaElement | null>;
  isMathAnimatorMode: boolean;
  isVisualizeMode: boolean;
  // When true, parent has attachments/references queued and will accept a
  // send even if the text body is empty. Without this, Enter would silently
  // do nothing for an attachment-only message.
  canSendEmpty: boolean;
  onSend: (content: string) => void;
  onInputChange: (content: string) => void;
  onPaste: (e: React.ClipboardEvent) => void;
  selectedCounts: ChatSpaceSelectionCounts;
  onSelectNotebookPicker: () => void;
  onSelectBookPicker: () => void;
  onSelectHistoryPicker: () => void;
  onSelectQuestionBankPicker: () => void;
  onSelectSkillsPicker: () => void;
  onSelectMemoryPicker: () => void;
}

export interface ComposerInputHandle {
  clear: () => void;
  getValue: () => string;
}

export function shouldOpenAtPopup(value: string, cursorPos: number): boolean {
  const prefix = value.slice(0, cursorPos);
  return /(^|\s)@[^\s]*$/.test(prefix);
}

export function stripTrailingAtMention(value: string): string {
  return value.replace(/(^|\s)@[^\s]*$/, "$1").replace(/\s+$/, "");
}

export const ComposerInput = memo(
  forwardRef<ComposerInputHandle, ComposerInputProps>(function ComposerInput(
    {
      textareaRef,
      isMathAnimatorMode,
      isVisualizeMode,
      canSendEmpty,
      onSend,
      onInputChange,
      onPaste,
      selectedCounts,
      onSelectNotebookPicker,
      onSelectBookPicker,
      onSelectHistoryPicker,
      onSelectQuestionBankPicker,
      onSelectSkillsPicker,
      onSelectMemoryPicker,
    },
    ref,
  ) {
    const { t } = useTranslation();
    const [input, setInput] = useState("");
    const [showAtPopup, setShowAtPopup] = useState(false);

    // Latest text mirrored into a ref by the change handlers (never updated
    // during render). The @space handlers and the imperative handle read
    // from this ref so their identities stay stable across keystrokes,
    // letting `memo` on ChatSpaceMenu actually skip re-renders when
    // `showAtPopup` doesn't change.
    const inputRef = useRef("");
    const isComposingRef = useRef(false);
    // Helper that always updates state and ref together so they can't drift.
    const setInputBoth = useCallback((value: string) => {
      inputRef.current = value;
      setInput(value);
    }, []);

    useImperativeHandle(
      ref,
      () => ({
        clear: () => {
          setInputBoth("");
          onInputChange("");
        },
        getValue: () => inputRef.current,
      }),
      [setInputBoth, onInputChange],
    );

    useAutoSizedTextarea(textareaRef, input, { min: 28, max: 200 });

    const handleInputChange = useCallback(
      (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        const cursorPos = e.target.selectionStart ?? value.length;
        setInputBoth(value);
        onInputChange(value);
        setShowAtPopup(shouldOpenAtPopup(value, cursorPos));
      },
      [setInputBoth, onInputChange],
    );

    const handleTextareaClick = useCallback(
      (e: React.MouseEvent<HTMLTextAreaElement>) => {
        const target = e.currentTarget;
        setShowAtPopup(
          shouldOpenAtPopup(
            target.value,
            target.selectionStart ?? target.value.length,
          ),
        );
      },
      [],
    );

    const doSend = useCallback(() => {
      const content = inputRef.current.trim();
      // Allow sending when text is empty but the parent has attachments or
      // references queued (canSendEmpty). This matches the send-button's
      // own enablement logic in ChatComposer (`canSend`).
      if (!content && !canSendEmpty) return;
      onSend(content);
      setInputBoth("");
      onInputChange("");
      setShowAtPopup(false);
    }, [canSendEmpty, onSend, setInputBoth, onInputChange]);

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (shouldSubmitOnEnter(e, isComposingRef.current)) {
          e.preventDefault();
          doSend();
        } else if (e.key === "Escape") {
          setShowAtPopup(false);
        }
      },
      [doSend],
    );

    const handleCompositionStart = useCallback(() => {
      isComposingRef.current = true;
    }, []);

    const handleCompositionEnd = useCallback(() => {
      // Some IMEs fire compositionend before the Enter keydown that confirms
      // a candidate, so keep the guard through the current event turn.
      setTimeout(() => {
        isComposingRef.current = false;
      }, 0);
    }, []);

    const clearTrailingMention = useCallback(() => {
      const next = stripTrailingAtMention(inputRef.current);
      setInputBoth(next);
      onInputChange(next);
    }, [setInputBoth, onInputChange]);

    const handleSelectSpaceItem = useCallback(
      (
        key:
          | "chat_history"
          | "books"
          | "notebooks"
          | "question_bank"
          | "skills"
          | "memory",
      ) => {
        clearTrailingMention();
        setShowAtPopup(false);
        if (key === "chat_history") onSelectHistoryPicker();
        else if (key === "books") onSelectBookPicker();
        else if (key === "notebooks") onSelectNotebookPicker();
        else if (key === "question_bank") onSelectQuestionBankPicker();
        else if (key === "skills") onSelectSkillsPicker();
        else if (key === "memory") onSelectMemoryPicker();
      },
      [
        clearTrailingMention,
        onSelectHistoryPicker,
        onSelectBookPicker,
        onSelectNotebookPicker,
        onSelectQuestionBankPicker,
        onSelectSkillsPicker,
        onSelectMemoryPicker,
      ],
    );

    // Close the @-popup on outside click. Without this, clicking anywhere
    // outside the popup or textarea left the menu hovering indefinitely.
    // We bind on mousedown so the close fires before a synthetic click on
    // a sibling button (e.g. the Tools menu) can re-open something else.
    const popupRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
      if (!showAtPopup) return;
      const handler = (e: MouseEvent) => {
        const target = e.target as Node | null;
        if (!target) return;
        if (popupRef.current?.contains(target)) return;
        if (textareaRef.current?.contains(target)) return;
        setShowAtPopup(false);
      };
      document.addEventListener("mousedown", handler);
      return () => document.removeEventListener("mousedown", handler);
    }, [showAtPopup, textareaRef]);

    return (
      <div className="px-4 pt-3.5 pb-2">
        {showAtPopup && (
          <div
            ref={popupRef}
            className="absolute bottom-full left-0 z-[70] mb-2"
          >
            <ChatSpaceMenu
              variant="mention"
              selectedCounts={selectedCounts}
              onSelectItem={handleSelectSpaceItem}
            />
          </div>
        )}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          onClick={handleTextareaClick}
          onPaste={onPaste}
          rows={1}
          // Cap input at 32k chars. A bigger paste (e.g. an entire textbook
          // dumped via Cmd+V) would force a layout reflow on every keystroke
          // and lock the page; the cap is a defensive guard, not a real
          // product limit. Users hit by this cap should be using the
          // attachment path, not the composer body.
          maxLength={32000}
          suppressHydrationWarning
          placeholder={
            isMathAnimatorMode
              ? t("Describe the math animation or storyboard you want...")
              : isVisualizeMode
                ? t("Describe the chart or diagram you want to visualize...")
                : t("How can I help you today?")
          }
          className="w-full resize-none overflow-hidden bg-transparent text-[15px] leading-relaxed text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]"
          style={{ transition: "height 0.15s ease-out", minHeight: 28 }}
        />
      </div>
    );
  }),
);
