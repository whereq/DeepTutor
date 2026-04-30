"use client";

import { memo } from "react";
import { useTranslation } from "react-i18next";
import { SPACE_ITEMS, type SpaceItemKey } from "@/lib/space-items";

type SelectableSpaceKey = Extract<
  SpaceItemKey,
  "chat_history" | "notebooks" | "question_bank" | "skills" | "memory"
>;

export interface ChatSpaceSelectionCounts {
  chatHistory: number;
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

  // Render the items in a fixed, hand-tuned order so the menu always reads
  // the same regardless of how SPACE_ITEMS may be reordered for navigation.
  const items = ITEM_ORDER.map(
    (key) => SPACE_ITEMS.find((it) => it.key === key)!,
  ).filter(Boolean);

  return (
    <div
      className={`rounded-xl border border-[var(--border)] bg-[var(--popover)] shadow-lg backdrop-blur-md ${
        compact ? "w-[260px] py-1.5" : "w-64 p-2"
      }`}
    >
      <div className={compact ? "space-y-0.5" : "space-y-1"}>
        {items.map(({ key, label, description, icon: Icon }) => {
          const count = countFor(key as SelectableSpaceKey, selectedCounts);
          return (
            <button
              key={key}
              type="button"
              onClick={() => onSelectItem(key as SelectableSpaceKey)}
              className={`flex w-full items-center gap-2.5 text-left transition-colors hover:bg-[var(--muted)]/40 ${
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
