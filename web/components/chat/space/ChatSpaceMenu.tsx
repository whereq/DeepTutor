"use client";

import { memo, useEffect, useRef, useState } from "react";
import { BookOpen } from "lucide-react";
import { useTranslation } from "react-i18next";
import { SPACE_ITEMS } from "@/lib/space-items";

type SelectableSpaceKey =
  | "chat_history"
  | "books"
  | "notebooks"
  | "question_bank"
  | "skills"
  | "memory";

export interface ChatSpaceSelectionCounts {
  chatHistory: number;
  books: number;
  notebooks: number;
  questionBank: number;
  skills: number;
  memory: number;
}

interface ChatSpaceMenuProps {
  variant: "toolbar" | "mention";
  selectedCounts: ChatSpaceSelectionCounts;
  onSelectItem: (key: SelectableSpaceKey) => void;
}

const ITEM_ORDER: SelectableSpaceKey[] = [
  "chat_history",
  "books",
  "notebooks",
  "question_bank",
  "skills",
  "memory",
];

function countFor(
  key: SelectableSpaceKey,
  counts: ChatSpaceSelectionCounts,
): number {
  switch (key) {
    case "chat_history":
      return counts.chatHistory;
    case "books":
      return counts.books;
    case "notebooks":
      return counts.notebooks;
    case "question_bank":
      return counts.questionBank;
    case "skills":
      return counts.skills;
    case "memory":
      return counts.memory;
    default:
      return 0;
  }
}

export default memo(function ChatSpaceMenu({
  variant,
  selectedCounts,
  onSelectItem,
}: ChatSpaceMenuProps) {
  const { t } = useTranslation();
  const compact = variant === "toolbar";
  const isMention = variant === "mention";

  // Render the items in a fixed, hand-tuned order so the menu always reads
  // the same regardless of how SPACE_ITEMS may be reordered for navigation.
  const items = ITEM_ORDER.map((key) =>
    key === "books"
      ? {
          key,
          label: "Books",
          description: "Reference generated book chapters in chat.",
          icon: BookOpen,
        }
      : SPACE_ITEMS.find((it) => it.key === key)!,
  ).filter(Boolean);

  // Active row index for keyboard navigation. Only meaningful in the
  // mention variant — the toolbar variant is mouse/click driven.
  const [activeIdx, setActiveIdx] = useState(0);
  // The keydown handler closes over `activeIdx`/`items`/`onSelectItem`;
  // stash them in refs so the document-level listener identity stays
  // stable and we don't re-attach it on every render. Refs are synced
  // in an effect (not during render) to satisfy `react-hooks/refs`.
  const activeIdxRef = useRef(activeIdx);
  const itemsRef = useRef(items);
  const onSelectItemRef = useRef(onSelectItem);
  useEffect(() => {
    activeIdxRef.current = activeIdx;
  }, [activeIdx]);
  useEffect(() => {
    itemsRef.current = items;
  }, [items]);
  useEffect(() => {
    onSelectItemRef.current = onSelectItem;
  }, [onSelectItem]);

  // Reset to the top whenever the menu first mounts (i.e. user typed `@`
  // and the popup appeared). The parent unmounts/remounts this component
  // on each open, so a fresh `useState(0)` initial value already gives us
  // the right behavior — no extra effect needed.

  // Attach a document-level keydown so Arrow/Enter while the textarea
  // still has focus drive the menu. The textarea's own handleKeyDown
  // continues to handle Escape and submit.
  useEffect(() => {
    if (!isMention) return;
    const handler = (e: KeyboardEvent) => {
      const list = itemsRef.current;
      if (list.length === 0) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIdx((i) => (i + 1) % list.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIdx((i) => (i - 1 + list.length) % list.length);
      } else if (e.key === "Enter") {
        const item = list[activeIdxRef.current];
        if (!item) return;
        e.preventDefault();
        onSelectItemRef.current(item.key as SelectableSpaceKey);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isMention]);

  return (
    <div
      role={isMention ? "listbox" : undefined}
      aria-label={isMention ? t("Reference space") : undefined}
      className={`rounded-xl border border-[var(--border)] bg-[var(--popover)] shadow-lg backdrop-blur-md ${
        compact ? "w-[260px] py-1.5" : "w-64 p-2"
      }`}
    >
      <div className={compact ? "space-y-0.5" : "space-y-1"}>
        {items.map(({ key, label, description, icon: Icon }, idx) => {
          const count = countFor(key as SelectableSpaceKey, selectedCounts);
          const isActive = isMention && idx === activeIdx;
          return (
            <button
              key={key}
              type="button"
              role={isMention ? "option" : undefined}
              aria-selected={isMention ? isActive : undefined}
              onMouseEnter={
                isMention ? () => setActiveIdx(idx) : undefined
              }
              onClick={() => onSelectItem(key as SelectableSpaceKey)}
              className={`flex w-full items-center gap-2.5 text-left transition-colors ${
                isActive ? "bg-[var(--muted)]/60" : "hover:bg-[var(--muted)]/40"
              } ${
                compact
                  ? "px-3 py-1.5 text-[12px]"
                  : "rounded-xl px-3 py-2.5 text-[13px]"
              }`}
            >
              <Icon
                size={compact ? 13 : 14}
                strokeWidth={1.7}
                className="shrink-0 text-[var(--muted-foreground)]"
              />
              <span className="min-w-0 flex-1">
                <span className="block truncate font-medium text-[var(--foreground)]">
                  {t(label)}
                </span>
                {!compact && (
                  <span className="mt-0.5 block truncate text-[11px] text-[var(--muted-foreground)]">
                    {t(description)}
                  </span>
                )}
              </span>
              {count > 0 && (
                <span className="rounded-full bg-[var(--primary)]/10 px-1.5 py-px text-[9px] font-semibold text-[var(--primary)]">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
});
