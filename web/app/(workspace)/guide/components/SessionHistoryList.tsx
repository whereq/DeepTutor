"use client";

import {
  BookOpen,
  CheckCircle2,
  Clock,
  FileText,
  GraduationCap,
  Loader2,
} from "lucide-react";
import { SessionSummary } from "../types";
import { useTranslation } from "react-i18next";

interface SessionHistoryListProps {
  sessions: SessionSummary[];
  loading: boolean;
  onLoadSession: (sessionId: string) => void;
}

function StatusBadge({ status }: { status: string }) {
  const { t } = useTranslation();
  if (status === "completed") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
        <CheckCircle2 className="w-3 h-3" />
        {t("Completed")}
      </span>
    );
  }
  if (status === "learning") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-semibold text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
        <BookOpen className="w-3 h-3" />
        {t("In Progress")}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
      <FileText className="w-3 h-3" />
      {t("Planned")}
    </span>
  );
}

export default function SessionHistoryList({
  sessions,
  loading,
  onLoadSession,
}: SessionHistoryListProps) {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 p-8">
        <Loader2 className="w-8 h-8 animate-spin mb-3" />
        <p className="text-sm">{t("Loading history...")}</p>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-slate-300 dark:text-slate-600 p-8">
        <GraduationCap className="w-20 h-20 mb-4" />
        <h3 className="text-base font-medium text-slate-500 dark:text-slate-400 mb-1">
          {t("No learning history yet")}
        </h3>
        <p className="text-sm text-slate-400 dark:text-slate-500 text-center max-w-sm">
          {t(
            "Describe what you want to learn on the left, and your guided learning sessions will appear here.",
          )}
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
        {t("Learning History")}
      </h3>
      <div className="grid gap-3 grid-cols-1 sm:grid-cols-2">
        {sessions.map((session) => (
          <button
            key={session.session_id}
            onClick={() => onLoadSession(session.session_id)}
            className="text-left rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md hover:border-indigo-200 transition dark:border-slate-700 dark:bg-slate-800 dark:hover:border-indigo-700"
          >
            <p className="text-sm font-medium text-slate-800 dark:text-slate-100 line-clamp-2 mb-2">
              {session.topic || t("Untitled")}
            </p>
            <div className="flex items-center gap-2 mb-2">
              <StatusBadge status={session.status} />
              <span className="text-[10px] text-slate-400 dark:text-slate-500 flex items-center gap-0.5">
                <Clock className="w-3 h-3" />
                {new Date(session.created_at * 1000).toLocaleDateString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                  style={{ width: `${session.progress}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-400 dark:text-slate-500 shrink-0">
                {session.ready_count}/{session.total_points}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
