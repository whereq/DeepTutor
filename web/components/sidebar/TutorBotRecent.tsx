"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch, apiUrl } from "@/lib/api";
import { formatRelativeTime } from "@/lib/relative-time";

interface RecentBot {
  bot_id: string;
  name: string;
  running: boolean;
  last_message: string;
  updated_at: string;
}

export function TutorBotRecent({ collapsed = false }: { collapsed?: boolean }) {
  const { i18n } = useTranslation();
  const [bots, setBots] = useState<RecentBot[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch(apiUrl("/api/v1/tutorbot/recent?limit=3"));
        if (!res.ok) return;
        const data = await res.json();
        if (!cancelled) setBots(data);
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (bots.length === 0) return null;

  if (collapsed) return null;

  return (
    <div className="ml-5 border-l border-[var(--border)]/30 py-1">
      {bots.map((bot) => (
        <Link
          key={bot.bot_id}
          href={`/agents/${bot.bot_id}/chat`}
          className="group flex items-center gap-2 rounded-r-lg py-1 pl-3 pr-2 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background)]/40 hover:text-[var(--foreground)]"
        >
          <div className="relative shrink-0">
            {bot.running ? (
              <span className="block h-1.5 w-1.5 rounded-full bg-emerald-400" />
            ) : (
              <span className="block h-1.5 w-1.5 rounded-full bg-[var(--muted-foreground)]/25" />
            )}
          </div>
          <span className="min-w-0 flex-1 truncate text-[13px]">
            {bot.name}
          </span>
          <span className="shrink-0 text-[10px] tabular-nums text-[var(--muted-foreground)]/40">
            {formatRelativeTime(
              Math.floor(new Date(bot.updated_at).getTime() / 1000),
              i18n.language,
            )}
          </span>
        </Link>
      ))}
    </div>
  );
}
