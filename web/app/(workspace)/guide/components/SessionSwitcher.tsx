"use client";

import { useState, useRef, useEffect } from "react";
import {
  ChevronDown,
  Plus,
  Clock,
  CheckCircle2,
  BookOpen,
  FileText,
} from "lucide-react";
import { SessionSummary } from "../types";
import { useTranslation } from "react-i18next";

interface SessionSwitcherProps {
  currentSessionId: string | null;
  currentTopic: string;
  currentStatus: string;
  sessions: SessionSummary[];
  onLoadSession: (sessionId: string) => void;
  onNewSession: () => void;
}

function StatusBadge({ status }: { status: string }) {
  const { t } = useTranslation();
  if (status === "completed") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
        <CheckCircle2 className="w-3 h-3" />
        {t("Completed")}
      </span>
    );
  }
  if (status === "learning") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
        <BookOpen className="w-3 h-3" />
        {t("In Progress")}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
      <FileText className="w-3 h-3" />
      {t("Planned")}
    </span>
  );
}

export default function SessionSwitcher({
  currentSessionId,
  currentTopic,
  currentStatus,
  sessions,
  onLoadSession,
  onNewSession,
}: SessionSwitcherProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const otherSessions = sessions.filter(
    (s) => s.session_id !== currentSessionId,
  );

  return (
    <div ref={containerRef} className="relative shrink-0">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-left transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:bg-slate-750"
      >
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">
            {currentTopic || t("Untitled Session")}
          </p>
          <StatusBadge status={currentStatus} />
        </div>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="absolute left-0 right-0 top-full mt-1 z-30 rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800 max-h-64 overflow-y-auto">
          {otherSessions.length > 0 && (
            <div className="py-1">
              {otherSessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => {
                    onLoadSession(session.session_id);
                    setOpen(false);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-700 dark:text-slate-200 truncate">
                      {session.topic || t("Untitled")}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <StatusBadge status={session.status} />
                      <span className="text-[10px] text-slate-400 flex items-center gap-0.5">
                        <Clock className="w-3 h-3" />
                        {new Date(session.created_at * 1000).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
          <div className="border-t border-slate-200 dark:border-slate-700 p-2">
            <button
              onClick={() => {
                onNewSession();
                setOpen(false);
              }}
              className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-2 text-xs font-medium text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-300 dark:hover:bg-indigo-900/50 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              {t("New Session")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
