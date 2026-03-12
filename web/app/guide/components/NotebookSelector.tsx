"use client";

import {
  Loader2,
  ChevronRight,
  ChevronDown,
  Check,
} from "lucide-react";
import {
  Notebook,
  NotebookRecord,
  SelectedRecord,
  getTypeColor,
} from "../types";
import { useTranslation } from "react-i18next";

interface NotebookSelectorProps {
  notebooks: Notebook[];
  expandedNotebooks: Set<string>;
  notebookRecordsMap: Map<string, NotebookRecord[]>;
  selectedRecords: Map<string, SelectedRecord>;
  loadingNotebooks: boolean;
  loadingRecordsFor: Set<string>;
  isLoading: boolean;
  onToggleExpanded: (notebookId: string) => void;
  onToggleRecord: (
    record: NotebookRecord,
    notebookId: string,
    notebookName: string,
  ) => void;
  onSelectAll: (notebookId: string, notebookName: string) => void;
  onDeselectAll: (notebookId: string) => void;
  onClearAll: () => void;
  onCreateSession: () => void;
  actionLabel?: string;
}

export default function NotebookSelector({
  notebooks,
  expandedNotebooks,
  notebookRecordsMap,
  selectedRecords,
  loadingNotebooks,
  loadingRecordsFor,
  isLoading,
  onToggleExpanded,
  onToggleRecord,
  onSelectAll,
  onDeselectAll,
  onClearAll,
  onCreateSession,
  actionLabel,
}: NotebookSelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between border-b border-slate-100 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-900">
        <h2 className="flex items-center gap-2 font-bold text-slate-900 dark:text-slate-100">
          {t("Select Source (Cross-Notebook)")}
        </h2>
        {selectedRecords.size > 0 && (
          <button
            onClick={onClearAll}
            className="text-xs text-slate-500 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400"
          >
            {t("Clear")} ({selectedRecords.size})
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto max-h-[460px] px-2 py-2">
        {loadingNotebooks ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
          </div>
        ) : notebooks.length === 0 ? (
          <div className="p-4 text-center text-sm text-slate-400 dark:text-slate-500">
            {t("No notebooks with records found")}
          </div>
        ) : (
          <div className="space-y-2">
            {notebooks.map((notebook) => {
              const isExpanded = expandedNotebooks.has(notebook.id);
              const records = notebookRecordsMap.get(notebook.id) || [];
              const isLoadingRecords = loadingRecordsFor.has(notebook.id);
              const selectedFromThis = records.filter((r) =>
                selectedRecords.has(r.id),
              ).length;

              return (
                <div
                  key={notebook.id}
                  className="overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"
                >
                  {/* Notebook Header */}
                  <div
                    className="flex cursor-pointer items-center gap-2 px-3 py-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/70"
                    onClick={() => onToggleExpanded(notebook.id)}
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-400 dark:text-slate-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400 dark:text-slate-500" />
                    )}
                    <span className="flex-1 text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                      {notebook.name}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      {selectedFromThis > 0 && (
                        <span className="font-medium text-slate-700 dark:text-slate-300">
                          {selectedFromThis}/
                        </span>
                      )}
                      {notebook.record_count}
                    </span>
                  </div>

                  {/* Records List */}
                  {isExpanded && (
                    <div className="bg-slate-50/70 pb-3 pl-6 pr-3 dark:bg-slate-950/30">
                      {isLoadingRecords ? (
                        <div className="flex items-center justify-center py-4">
                          <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
                        </div>
                      ) : records.length === 0 ? (
                        <div className="py-2 text-xs text-slate-400 dark:text-slate-500 text-center">
                          {t("No records")}
                        </div>
                      ) : (
                        <>
                          <div className="flex gap-2 mb-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectAll(notebook.id, notebook.name);
                              }}
                              className="text-xs text-slate-600 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
                            >
                              {t("Select All")}
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onDeselectAll(notebook.id);
                              }}
                              className="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
                            >
                              {t("Deselect")}
                            </button>
                          </div>
                          <div className="space-y-2">
                            {records.map((record) => (
                              <div
                                key={record.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onToggleRecord(
                                    record,
                                    notebook.id,
                                    notebook.name,
                                  );
                                }}
                                className={`cursor-pointer rounded-lg border p-3 transition-all ${
                                  selectedRecords.has(record.id)
                                    ? "border-slate-300 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/60"
                                    : "border-transparent hover:border-slate-200 hover:bg-white dark:hover:border-slate-700 dark:hover:bg-slate-800/75"
                                }`}
                              >
                                <div className="flex items-center gap-2">
                                  <div
                                    className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${
                                      selectedRecords.has(record.id)
                                        ? "border-slate-700 bg-slate-700 text-white dark:border-slate-200 dark:bg-slate-200 dark:text-slate-900"
                                        : "border-slate-300 dark:border-slate-500"
                                    }`}
                                  >
                                    {selectedRecords.has(record.id) && (
                                      <Check className="w-2.5 h-2.5" />
                                    )}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <span
                                      className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase ${getTypeColor(record.type)}`}
                                    >
                                      {record.type}
                                    </span>
                                    <span className="ml-2 truncate text-xs text-slate-700 dark:text-slate-200">
                                      {record.title}
                                    </span>
                                    {record.summary && (
                                      <p className="mt-2 line-clamp-2 text-[11px] leading-5 text-slate-500 dark:text-slate-400">
                                        {record.summary}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Generate Button */}
      <div className="border-t border-slate-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <button
          onClick={onCreateSession}
          disabled={isLoading || selectedRecords.size === 0}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-4 py-2.5 font-medium text-[var(--primary-foreground)] transition disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              {t("Generating...")}
            </>
          ) : (
            (actionLabel || t("Generate Learning Plan ({n} items)")).replace(
              "{n}",
              String(selectedRecords.size),
            )
          )}
        </button>
      </div>
    </div>
  );
}
