"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";
import {
  Blocks,
  BookOpen,
  Brain,
  GraduationCap,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  PenLine,
  Plus,
  Settings,
  type LucideIcon,
} from "lucide-react";
import SessionList from "@/components/SessionList";
import type { SessionSummary } from "@/lib/session-api";

interface NavEntry {
  href: string;
  label: string;
  icon: LucideIcon;
}

const PRIMARY_NAV: NavEntry[] = [
  { href: "/", label: "Chat", icon: MessageSquare },
  { href: "/co-writer", label: "Co-Writer", icon: PenLine },
  { href: "/guide", label: "Guided Learning", icon: GraduationCap },
  { href: "/knowledge", label: "Knowledge", icon: BookOpen },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/playground", label: "Playground", icon: Blocks },
];

const SECONDARY_NAV: NavEntry[] = [{ href: "/settings", label: "Settings", icon: Settings }];
const DEFAULT_SESSION_VIEWPORT_CLASS_NAME = "max-h-[220px]";

interface SidebarShellProps {
  sessions?: SessionSummary[];
  activeSessionId?: string | null;
  loadingSessions?: boolean;
  showSessions?: boolean;
  sessionViewportClassName?: string;
  onNewChat?: () => void;
  onSelectSession?: (sessionId: string) => void | Promise<void>;
  onRenameSession?: (sessionId: string, title: string) => void | Promise<void>;
  onDeleteSession?: (sessionId: string) => void | Promise<void>;
  footerSlot?: ReactNode;
}

export function SidebarShell({
  sessions = [],
  activeSessionId = null,
  loadingSessions = false,
  showSessions = false,
  sessionViewportClassName = DEFAULT_SESSION_VIEWPORT_CLASS_NAME,
  onNewChat,
  onSelectSession,
  onRenameSession,
  onDeleteSession,
  footerSlot,
}: SidebarShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
      return;
    }
    router.push("/");
  };

  return (
    <aside
      className={`${
        collapsed ? "w-[56px]" : "w-[216px]"
      } flex h-screen shrink-0 flex-col bg-[var(--accent)] transition-all duration-200 dark:bg-[var(--card)]`}
    >
      <div
        className={`flex h-14 items-center ${
          collapsed ? "justify-center px-2" : "justify-between px-4"
        }`}
      >
        {collapsed ? (
          <Link href="/">
            <Image src="/logo-ver2.png" alt="DeepTutor" width={22} height={22} />
          </Link>
        ) : (
          <>
            <Link href="/" className="flex items-center gap-2">
              <Image src="/logo-ver2.png" alt="DeepTutor" width={22} height={22} />
              <span className="text-[13px] font-semibold text-[var(--foreground)]">
                DeepTutor
              </span>
            </Link>
            <button
              onClick={() => setCollapsed(true)}
              className="rounded-md p-1 text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
              aria-label="Collapse sidebar"
            >
              <PanelLeftClose size={15} />
            </button>
          </>
        )}
      </div>

      <div className={`${collapsed ? "px-1.5" : "px-2"} pb-1`}>
        <button
          onClick={handleNewChat}
          className={`flex w-full items-center gap-2 rounded-lg px-3 py-[7px] text-[13px] text-[var(--foreground)] transition-colors hover:bg-[var(--muted)] ${
            collapsed ? "justify-center px-0" : ""
          }`}
        >
          <Plus size={15} strokeWidth={2} />
          {!collapsed && <span>New chat</span>}
        </button>
      </div>

      {!collapsed && showSessions && onSelectSession && onRenameSession && onDeleteSession ? (
        <div className="px-2 pb-2">
          <div className={`${sessionViewportClassName} overflow-y-auto`}>
            <SessionList
              sessions={sessions}
              activeSessionId={activeSessionId}
              loading={loadingSessions}
              onSelect={onSelectSession}
              onRename={onRenameSession}
              onDelete={onDeleteSession}
            />
          </div>
        </div>
      ) : null}

      <nav className={`flex-1 ${collapsed ? "px-1.5" : "px-2"} pt-2`}>
        <div className="space-y-px">
          {PRIMARY_NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-[7px] text-[13px] transition-colors ${
                  active
                    ? "bg-[var(--muted)] font-medium text-[var(--foreground)]"
                    : "text-[var(--muted-foreground)] hover:bg-[var(--muted)]/60 hover:text-[var(--foreground)]"
                } ${collapsed ? "justify-center px-0" : ""}`}
              >
                <item.icon size={16} strokeWidth={active ? 1.9 : 1.5} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </div>
      </nav>

      <div className={`${collapsed ? "px-1.5" : "px-2"} pb-3`}>
        {SECONDARY_NAV.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 rounded-lg px-3 py-[7px] text-[13px] transition-colors ${
                active
                  ? "bg-[var(--muted)] font-medium text-[var(--foreground)]"
                  : "text-[var(--muted-foreground)] hover:bg-[var(--muted)]/60 hover:text-[var(--foreground)]"
              } ${collapsed ? "justify-center px-0" : ""}`}
            >
              <item.icon size={16} strokeWidth={active ? 1.9 : 1.5} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}

        {footerSlot}

        {collapsed ? (
          <button
            onClick={() => setCollapsed(false)}
            className="mt-1 flex w-full items-center justify-center rounded-lg py-[7px] text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
            aria-label="Expand sidebar"
          >
            <PanelLeftOpen size={15} />
          </button>
        ) : null}
      </div>
    </aside>
  );
}
