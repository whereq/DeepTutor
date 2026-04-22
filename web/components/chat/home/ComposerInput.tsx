"use client";

import { forwardRef, memo, useCallback, useImperativeHandle, useLayoutEffect, useState, type RefObject } from "react";
import { useTranslation } from "react-i18next";
import AtMentionPopup from "@/components/chat/AtMentionPopup";

interface ComposerInputProps {
  textareaRef: RefObject<HTMLTextAreaElement | null>;
  activeCapabilityKey: string;
  isMathAnimatorMode: boolean;
  isVisualizeMode: boolean;
  onSend: (content: string) => void;
  onInputChange: (content: string) => void;
  onPaste: (e: React.ClipboardEvent) => void;
  onSelectNotebookPicker: () => void;
  onSelectHistoryPicker: () => void;
  onSelectQuestionBankPicker: () => void;
}

export interface ComposerInputHandle {
  clear: () => void;
  getValue: () => string;
}

function shouldOpenAtPopup(value: string, cursorPos: number): boolean {
  const prefix = value.slice(0, cursorPos);
  return /(^|\s)@[^\s]*$/.test(prefix);
}

function stripTrailingAtMention(value: string): string {
  return value.replace(/(^|\s)@[^\s]*$/, "$1").replace(/\s+$/, "");
}

export const ComposerInput = memo(forwardRef<ComposerInputHandle, ComposerInputProps>(function ComposerInput({
  textareaRef,
  activeCapabilityKey,
  isMathAnimatorMode,
  isVisualizeMode,
  onSend,
  onInputChange,
  onPaste,
  onSelectNotebookPicker,
  onSelectHistoryPicker,
  onSelectQuestionBankPicker,
}, ref) {
  const { t } = useTranslation();
  const [input, setInput] = useState("");
  const [showAtPopup, setShowAtPopup] = useState(false);

  useImperativeHandle(ref, () => ({
    clear: () => {
      setInput("");
      onInputChange("");
    },
    getValue: () => input,
  }));


  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "28px";
    const next = Math.max(el.scrollHeight, 28);
    const bounded = Math.min(next, 200);
    el.style.height = `${bounded}px`;
    el.style.overflowY = next > 200 ? "auto" : "hidden";
  }, [input, activeCapabilityKey, textareaRef]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPos = e.target.selectionStart ?? value.length;
    setInput(value);
    onInputChange(value);
    setShowAtPopup(shouldOpenAtPopup(value, cursorPos));
  }, [onInputChange]);

  const handleTextareaClick = useCallback((e: React.MouseEvent<HTMLTextAreaElement>) => {
    const target = e.currentTarget;
    setShowAtPopup(shouldOpenAtPopup(target.value, target.selectionStart ?? target.value.length));
  }, []);

  const doSend = useCallback(() => {
    const content = input.trim();
    if (!content) return;
    onSend(content);
    setInput("");
    onInputChange("");
    setShowAtPopup(false);
  }, [input, onSend, onInputChange]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      doSend();
    } else if (e.key === "Escape") {
      setShowAtPopup(false);
    }
  }, [doSend]);

  const handleSelectNotebook = useCallback(() => {
    const next = stripTrailingAtMention(input);
    setInput(next);
    onInputChange(next);
    setShowAtPopup(false);
    onSelectNotebookPicker();
  }, [input, onInputChange, onSelectNotebookPicker]);

  const handleSelectHistory = useCallback(() => {
    const next = stripTrailingAtMention(input);
    setInput(next);
    onInputChange(next);
    setShowAtPopup(false);
    onSelectHistoryPicker();
  }, [input, onInputChange, onSelectHistoryPicker]);

  const handleSelectQuestionBank = useCallback(() => {
    const next = stripTrailingAtMention(input);
    setInput(next);
    onInputChange(next);
    setShowAtPopup(false);
    onSelectQuestionBankPicker();
  }, [input, onInputChange, onSelectQuestionBankPicker]);

  return (
    <div className="px-4 pt-3.5 pb-2">
      <AtMentionPopup
        open={showAtPopup}
        onSelectNotebook={handleSelectNotebook}
        onSelectHistory={handleSelectHistory}
        onSelectQuestionBank={handleSelectQuestionBank}
      />
      <textarea
        ref={textareaRef}
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onClick={handleTextareaClick}
        onPaste={onPaste}
        rows={1}
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
}));
