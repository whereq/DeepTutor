"use client";

import {
  Brain,
  ClipboardList,
  History,
  NotebookPen,
  Wand2,
  type LucideIcon,
} from "lucide-react";

export type SpaceItemKey =
  | "chat_history"
  | "notebooks"
  | "question_bank"
  | "skills"
  | "memory";

export type SpaceMemoryFile = "summary" | "profile";

export interface SpaceItem {
  key: SpaceItemKey;
  href: string;
  label: string;
  description: string;
  icon: LucideIcon;
}

export const SPACE_ITEMS: SpaceItem[] = [
  {
    key: "chat_history",
    href: "/space/chat-history",
    label: "Chat History",
    description: "Review and reopen previous conversations.",
    icon: History,
  },
  {
    key: "notebooks",
    href: "/space/notebooks",
    label: "Notebooks",
    description:
      "Organize saved outputs from chat, research, Co-Writer, and more.",
    icon: NotebookPen,
  },
  {
    key: "question_bank",
    href: "/space/questions",
    label: "Question Bank",
    description: "Review and organize quiz questions across sessions.",
    icon: ClipboardList,
  },
  {
    key: "skills",
    href: "/space/skills",
    label: "Skills",
    description: "Behavior playbooks that guide chat responses.",
    icon: Wand2,
  },
  {
    key: "memory",
    href: "/space/memory",
    label: "Memory",
    description: "Long-form memory the assistant carries across sessions.",
    icon: Brain,
  },
];
