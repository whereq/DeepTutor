"use client";

import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  Play,
  RotateCcw,
  Sparkles,
  XCircle,
} from "lucide-react";
import { SessionState } from "../types";
import { useTranslation } from "react-i18next";

interface ProgressPanelProps {
  sessionState: SessionState;
  isLoading: boolean;
  canStart: boolean;
  readyCount: number;
  allPagesReady: boolean;
  onStartLearning: () => void;
  onNavigate: (knowledgeIndex: number) => void;
  onRetryPage: (knowledgeIndex: number) => void;
  onCompleteLearning: () => void;
  onResetSession: () => void;
}

export default function ProgressPanel({
  sessionState,
  isLoading,
  canStart,
  readyCount,
  allPagesReady,
  onStartLearning,
  onNavigate,
  onRetryPage,
  onCompleteLearning,
  onResetSession,
}: ProgressPanelProps) {
  const { t } = useTranslation();

  const totalCount = sessionState.knowledge_points.length;

  const renderStatusIcon = (knowledgeIndex: number) => {
    const status = sessionState.page_statuses[knowledgeIndex];

    if (status === "ready") {
      return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
    }
    if (status === "generating") {
      return <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />;
    }
    if (status === "failed") {
      return <XCircle className="w-4 h-4 text-rose-500" />;
    }
    return <AlertCircle className="w-4 h-4 text-slate-400" />;
  };

  return (
    <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
      <div className="flex items-center justify-between mb-2 gap-3">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          {t("Learning Progress")}
        </span>
        <span className="text-xs text-slate-400 dark:text-slate-500">
          {readyCount}/{totalCount} {t("pages ready")}
        </span>
      </div>
      <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
          style={{ width: `${sessionState.progress}%` }}
        />
      </div>
      {totalCount > 0 && (
        <p className="text-xs text-slate-400 dark:text-slate-500 mb-4">
          {t("Open any page once it is ready. Early stages are prioritized.")}
        </p>
      )}

      <div className="space-y-2 mb-4">
        {sessionState.knowledge_points.map((knowledge, index) => {
          const status = sessionState.page_statuses[index] || "pending";
          const isCurrent = sessionState.current_index === index;
          const isReady = status === "ready";
          const isFailed = status === "failed";

          return (
            <div
              key={`${knowledge.knowledge_title}-${index}`}
              className={`rounded-xl border px-3 py-3 transition ${
                isCurrent
                  ? "border-indigo-300 bg-indigo-50 dark:border-indigo-600 dark:bg-indigo-950/30"
                  : "border-slate-200 bg-slate-50/70 dark:border-slate-700 dark:bg-slate-900/50"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <button
                  onClick={() => onNavigate(index)}
                  className="flex-1 text-left"
                >
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-800 dark:text-slate-100">
                    {renderStatusIcon(index)}
                    <span>{index + 1}.</span>
                    <span className="line-clamp-2">{knowledge.knowledge_title}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {status === "ready"
                      ? t("Ready to open")
                      : status === "generating"
                        ? t("Generating interactive page...")
                        : status === "failed"
                          ? t("Generation failed")
                          : t("Waiting in queue")}
                  </p>
                </button>

                {isFailed && (
                  <button
                    onClick={() => onRetryPage(index)}
                    className="inline-flex items-center gap-1 rounded-lg border border-rose-200 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50 dark:border-rose-800 dark:text-rose-300 dark:hover:bg-rose-950/30"
                  >
                    <RotateCcw className="w-3 h-3" />
                    {t("Retry")}
                  </button>
                )}
                {isReady && (
                  <button
                    onClick={() => onNavigate(index)}
                    className="inline-flex items-center gap-1 rounded-lg border border-emerald-200 px-2 py-1 text-xs text-emerald-600 hover:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-300 dark:hover:bg-emerald-950/30"
                  >
                    <Sparkles className="w-3 h-3" />
                    {t("Open")}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex flex-wrap gap-2">
        {canStart && (
          <button
            onClick={onStartLearning}
            disabled={isLoading}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                {t("Starting...")}
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                {t("Start Learning")}
              </>
            )}
          </button>
        )}

        {!canStart && (
          <button
            onClick={onResetSession}
            className="flex-1 px-4 py-2 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300 transition-colors flex items-center justify-center gap-2 text-sm font-medium dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
          >
            <RotateCcw className="w-4 h-4" />
            {t("New Session")}
          </button>
        )}

        {!canStart && sessionState.status !== "completed" && (
          <button
            onClick={onCompleteLearning}
            disabled={isLoading || !allPagesReady}
            className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                {t("Generating Summary...")}
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                {t("Complete Learning")}
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
