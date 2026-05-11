"use client";

import { AlertTriangle, RefreshCcw, SlidersHorizontal } from "lucide-react";
import { memo } from "react";
import { useTranslation } from "react-i18next";

interface AutoErrorBlockProps {
  reason: string;
  failureMessage?: string;
  iteration?: number;
  routerRetries?: number;
  onRetry?: () => void;
  onSwitchToManual?: () => void;
}

/**
 * Prominent terminal-error block for auto-mode turns.
 *
 * Shown when the auto pipeline gave up after exhausting all retries. It
 * surfaces:
 *  - the failure reason (router LLM exhausted, terminal error, etc.)
 *  - the failure location (iteration, retry counts)
 *  - two recovery actions: switch to manual mode, or retry the message
 *
 * Partial successes (capability calls that completed before the failure) are
 * still rendered in the regular ``AutoModeAssistantMessage`` blocks above this
 * one — we deliberately do not duplicate them here.
 */
const AutoErrorBlock = memo(function AutoErrorBlock({
  reason,
  failureMessage,
  iteration,
  routerRetries,
  onRetry,
  onSwitchToManual,
}: AutoErrorBlockProps) {
  const { t } = useTranslation();
  const headline = (() => {
    if (reason === "router_llm_exhausted") {
      return t("Auto routing failed: router LLM exhausted retries.");
    }
    return t("Auto routing failed: {{reason}}", { reason });
  })();

  const subtitle = (() => {
    const parts: string[] = [];
    if (iteration != null) {
      parts.push(t("at iteration {{n}}", { n: iteration }));
    }
    if (routerRetries != null) {
      parts.push(t("after {{n}} router retries", { n: routerRetries }));
    }
    return parts.join(" · ");
  })();

  return (
    <div className="mt-3 overflow-hidden rounded-xl border-2 border-red-300/70 bg-red-50/60 text-[13px] shadow-sm dark:border-red-500/40 dark:bg-red-950/30">
      <div className="flex items-start gap-2.5 px-4 pt-3">
        <AlertTriangle
          size={16}
          strokeWidth={2}
          className="mt-0.5 shrink-0 text-red-600 dark:text-red-400"
        />
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-red-700 dark:text-red-300">
            {headline}
          </div>
          {subtitle ? (
            <div className="mt-0.5 text-[11px] text-red-700/80 dark:text-red-300/80">
              {subtitle}
            </div>
          ) : null}
          {failureMessage ? (
            <div className="mt-2 whitespace-pre-wrap text-[12px] text-red-900/85 dark:text-red-200/85">
              {failureMessage}
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-red-200/60 bg-red-100/40 px-4 py-2 dark:border-red-500/25 dark:bg-red-900/20">
        {onSwitchToManual ? (
          <button
            type="button"
            onClick={onSwitchToManual}
            className="inline-flex items-center gap-1.5 rounded-md border border-red-300/60 bg-white px-2.5 py-1 text-[12px] font-medium text-red-700 transition-colors hover:bg-red-50 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-200 dark:hover:bg-red-900/40"
          >
            <SlidersHorizontal size={12} strokeWidth={1.8} />
            {t("Switch to Manual")}
          </button>
        ) : null}
        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 rounded-md border border-red-300/60 bg-white px-2.5 py-1 text-[12px] font-medium text-red-700 transition-colors hover:bg-red-50 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-200 dark:hover:bg-red-900/40"
          >
            <RefreshCcw size={12} strokeWidth={1.8} />
            {t("Try Again")}
          </button>
        ) : null}
      </div>
    </div>
  );
});

AutoErrorBlock.displayName = "AutoErrorBlock";

export default AutoErrorBlock;
