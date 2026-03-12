"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
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
import { useCallback, useEffect, useRef, useState } from "react";
import { useUnifiedChat } from "@/context/UnifiedChatContext";
import SessionList from "@/components/SessionList";
import {
  deleteSession,
  listSessions,
  updateSessionTitle,
  type SessionSummary,
} from "@/lib/session-api";

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

const SECONDARY_NAV: NavEntry[] = [
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { newSession, loadSession, selectedSessionId, sessionStatuses, sidebarRefreshToken } =
    useUnifiedChat();
  const [collapsed, setCollapsed] = useState(false);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const hasLoadedSessionsRef = useRef(false);

  const refreshSessions = useCallback(async () => {
    if (!hasLoadedSessionsRef.current) {
      setLoadingSessions(true);
    }
    try {
      setSessions(await listSessions());
      hasLoadedSessionsRef.current = true;
    } catch (error) {
      console.error("Failed to load sessions", error);
    } finally {
      setLoadingSessions(false);
    }
  }, []);

  useEffect(() => {
    void refreshSessions();
  }, [refreshSessions, sidebarRefreshToken]);

  const mergedSessions = sessions.map((session) => {
    const runtime = sessionStatuses[session.session_id];
    if (!runtime) return session;
    return {
      ...session,
      status: runtime.status,
      active_turn_id: runtime.activeTurnId || session.active_turn_id,
    };
  });
  const orderedSessions = mergedSessions
    .map((session, index) => ({ session, index }))
    .sort((a, b) => {
      const aPriority = a.session.status === "running" ? 0 : 1;
      const bPriority = b.session.status === "running" ? 0 : 1;
      if (aPriority !== bPriority) return aPriority - bPriority;
      return a.index - b.index;
    })
    .map(({ session }) => session);

  const handleNewChat = () => {
    newSession();
    if (pathname !== "/") router.push("/");
  };

  const handleSelectSession = useCallback(
    async (sessionId: string) => {
      await loadSession(sessionId);
      if (pathname !== "/") router.push("/");
    },
    [loadSession, pathname, router],
  );

  const handleRenameSession = useCallback(
    async (sessionId: string, title: string) => {
      const updated = await updateSessionTitle(sessionId, title);
      setSessions((prev) =>
        prev.map((session) =>
          session.session_id === sessionId
            ? { ...session, title: updated.title, updated_at: updated.updated_at }
            : session,
        ),
      );
    },
    [],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      if (!window.confirm("Delete this chat history?")) return;
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((session) => session.session_id !== sessionId));
      if (selectedSessionId === sessionId) {
        newSession();
        if (pathname !== "/") router.push("/");
      }
    },
    [newSession, pathname, router, selectedSessionId],
  );

  return (
    <aside
      className={`${collapsed ? "w-[56px]" : "w-[216px]"} flex h-screen shrink-0 flex-col bg-[var(--accent)] transition-all duration-200 dark:bg-[var(--card)]`}
    >
      {/* Logo & collapse */}
      <div className={`flex h-14 items-center ${collapsed ? "justify-center px-2" : "justify-between px-4"}`}>
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

      {/* New chat */}
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

      {!collapsed && (
        <div className="px-2 pb-2">
          <div className="max-h-[38vh] overflow-y-auto">
            <SessionList
              sessions={orderedSessions}
              activeSessionId={selectedSessionId}
              loading={loadingSessions}
              onSelect={handleSelectSession}
              onRename={handleRenameSession}
              onDelete={handleDeleteSession}
            />
          </div>
        </div>
      )}

      {/* Nav */}
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

      {/* Footer */}
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

        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            className="mt-1 flex w-full items-center justify-center rounded-lg py-[7px] text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
            aria-label="Expand sidebar"
          >
            <PanelLeftOpen size={15} />
          </button>
        )}
      </div>
    </aside>
  );
}
