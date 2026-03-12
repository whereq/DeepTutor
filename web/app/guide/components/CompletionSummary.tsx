"use client";

import { CheckCircle2 } from "lucide-react";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import "katex/dist/katex.min.css";
import { useTranslation } from "react-i18next";

interface CompletionSummaryProps {
  summary: string;
}

export default function CompletionSummary({ summary }: CompletionSummaryProps) {
  const { t } = useTranslation();

  return (
    <div className="flex-1 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden relative">
      <div className="p-4 border-b border-slate-100 dark:border-slate-700 bg-gradient-to-r from-emerald-50 to-indigo-50 dark:from-emerald-900/20 dark:to-indigo-900/20 flex items-center justify-between shrink-0">
        <h2 className="font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          {t("Learning Summary")}
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto p-8 bg-white dark:bg-slate-800">
        <MarkdownRenderer
          content={summary || ""}
          variant="prose"
          className="prose-slate dark:prose-invert"
        />
      </div>
    </div>
  );
}
