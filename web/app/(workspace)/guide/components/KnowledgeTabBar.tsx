"use client";

import { useRef, useEffect } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  Play,
  RotateCcw,
  XCircle,
} from "lucide-react";
import { SessionState } from "../types";
import { useTranslation } from "react-i18next";

interface KnowledgeTabBarProps {
  sessionState: SessionState;
  isLoading: boolean;
  canStart: boolean;
  readyCount: number;
  allPagesReady: boolean;
  isCompleted: boolean;
  onStartLearning: () => void;
  onNavigate: (knowledgeIndex: number) => void;
  onRetryPage: (knowledgeIndex: number) => void;
  onCompleteLearning: () => void;
  onResetSession: () => void;
  onShowSummary: () => void;
}

export default function KnowledgeTabBar({
  sessionState,
  isLoading,
  canStart,
  readyCount,
  allPagesReady,
  isCompleted,
  onStartLearning,
  onNavigate,
  onRetryPage,
  onCompleteLearning,
  onResetSession,
  onShowSummary,
}: KnowledgeTabBarProps) {
  const { t } = useTranslation();
  const scrollRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLButtonElement>(null);
  const totalCount = sessionState.knowledge_points.length;

  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "center",
      });
    }
  }, [sessionState.current_index]);

  const renderStatusIcon = (index: number) => {
    const status = sessionState.page_statuses[index];
    if (status === "ready")
      return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />;
    if (status === "generating")
      return <Loader2 className="w-3.5 h-3.5 text-indigo-500 animate-spin" />;
    if (status === "failed")
      return <XCircle className="w-3.5 h-3.5 text-rose-500" />;
    return <AlertCircle className="w-3.5 h-3.5 text-slate-400" />;
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-t-2xl border border-b-0 border-slate-200 dark:border-slate-700 flex flex-col shrink-0">
      <div className="flex items-center gap-2 px-3 pt-2 pb-1">
        <div
          ref={scrollRef}
          className="flex-1 flex items-center gap-1 overflow-x-auto scrollbar-hide"
        >
          {sessionState.knowledge_points.map((knowledge, index) => {
            const isCurrent = sessionState.current_index === index;
            const status = sessionState.page_statuses[index] || "pending";
            const isReady = status === "ready";
            const isFailed = status === "failed";

            return (
              <button
                key={`tab-${index}`}
                ref={isCurrent && !isCompleted ? activeRef : null}
                onClick={() => {
                  if (isFailed) {
                    onRetryPage(index);
                  } else {
                    onNavigate(index);
                  }
                }}
                disabled={!isReady && !isFailed}
                title={knowledge.knowledge_title}
                className={`shrink-0 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition whitespace-nowrap ${
                  isCurrent && !isCompleted
                    ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-200"
                    : isReady
                      ? "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
                      : "bg-slate-50 text-slate-400 dark:bg-slate-800 dark:text-slate-500 cursor-default"
                }`}
              >
                {renderStatusIcon(index)}
                <span>{index + 1}</span>
              </button>
            );
          })}
          {sessionState.status === "completed" && (
            <button
              ref={isCompleted ? activeRef : null}
              onClick={onShowSummary}
              className={`shrink-0 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition whitespace-nowrap ${
                isCompleted
                  ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              <span>{t("Summary")}</span>
            </button>
          )}
        </div>

        <div className="shrink-0 flex items-center gap-1.5 pl-2 border-l border-slate-200 dark:border-slate-700">
          {canStart && (
            <button
              onClick={onStartLearning}
              disabled={isLoading}
              className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {isLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5" />
              )}
              {t("Start")}
            </button>
          )}

          {!canStart && sessionState.status !== "completed" && (
            <button
              onClick={onCompleteLearning}
              disabled={isLoading || !allPagesReady}
              className="inline-flex items-center gap-1 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50 transition"
            >
              {isLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <CheckCircle2 className="w-3.5 h-3.5" />
              )}
              {t("Complete")}
            </button>
          )}

          <button
            onClick={onResetSession}
            className="inline-flex items-center gap-1 rounded-lg bg-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="h-1 bg-slate-100 dark:bg-slate-700 mx-3 mb-1 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
          style={{
            width: `${totalCount > 0 ? (readyCount / totalCount) * 100 : 0}%`,
          }}
        />
      </div>
    </div>
  );
}
