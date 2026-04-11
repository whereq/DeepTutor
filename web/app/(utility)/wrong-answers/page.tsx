"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  CheckCircle2,
  Circle,
  Loader2,
  NotebookPen,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  deleteWrongAnswer,
  listWrongAnswers,
  updateWrongAnswerResolved,
  type WrongAnswer,
} from "@/lib/wrong-answer-api";

const MarkdownRenderer = dynamic(
  () => import("@/components/common/MarkdownRenderer"),
  { ssr: false },
);

type FilterMode = "unresolved" | "all";

function formatDate(value: number): string {
  const date = new Date(value * 1000);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString();
}

export default function WrongAnswersPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<WrongAnswer[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<FilterMode>("unresolved");
  const [pendingId, setPendingId] = useState<number | null>(null);

  const loadItems = useCallback(
    async (mode: FilterMode) => {
      setRefreshing(true);
      try {
        const response = await listWrongAnswers({
          resolved: mode === "unresolved" ? false : undefined,
          limit: 200,
        });
        setItems(response.items);
        setTotal(response.total);
      } catch (error) {
        console.error("Failed to load wrong answers", error);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [],
  );

  useEffect(() => {
    void loadItems(filter);
  }, [filter, loadItems]);

  const handleToggleResolved = useCallback(
    async (item: WrongAnswer) => {
      const nextResolved = !item.resolved;
      setPendingId(item.id);
      try {
        await updateWrongAnswerResolved(item.id, nextResolved);
        setItems((prev) =>
          filter === "unresolved" && nextResolved
            ? prev.filter((entry) => entry.id !== item.id)
            : prev.map((entry) =>
                entry.id === item.id
                  ? { ...entry, resolved: nextResolved }
                  : entry,
              ),
        );
        if (filter === "unresolved" && nextResolved) {
          setTotal((prev) => Math.max(0, prev - 1));
        }
      } catch (error) {
        console.error("Failed to update wrong answer", error);
      } finally {
        setPendingId(null);
      }
    },
    [filter],
  );

  const handleDelete = useCallback(
    async (item: WrongAnswer) => {
      if (!window.confirm(t("Delete this wrong answer?"))) return;
      setPendingId(item.id);
      try {
        await deleteWrongAnswer(item.id);
        setItems((prev) => prev.filter((entry) => entry.id !== item.id));
        setTotal((prev) => Math.max(0, prev - 1));
      } catch (error) {
        console.error("Failed to delete wrong answer", error);
      } finally {
        setPendingId(null);
      }
    },
    [t],
  );

  return (
    <div className="h-full overflow-y-auto [scrollbar-gutter:stable]">
      <div className="mx-auto max-w-[960px] px-6 py-8">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-[24px] font-semibold tracking-tight text-[var(--foreground)]">
              {t("Wrong Answer Note")}
            </h1>
            <p className="mt-1 text-[13px] text-[var(--muted-foreground)]">
              {t("Review mistakes from past quizzes across sessions.")}
            </p>
          </div>
          <button
            onClick={() => void loadItems(filter)}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)]/50 px-3 py-1.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:opacity-40"
          >
            {refreshing ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <RefreshCw className="h-3 w-3" />
            )}
            {t("Refresh")}
          </button>
        </div>

        <div className="mb-5 flex items-center justify-between border-b border-[var(--border)]/50 pb-3">
          <div className="flex items-center gap-1">
            {(["unresolved", "all"] as const).map((mode) => {
              const active = filter === mode;
              return (
                <button
                  key={mode}
                  onClick={() => setFilter(mode)}
                  className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[13px] transition-colors ${
                    active
                      ? "bg-[var(--muted)] font-medium text-[var(--foreground)]"
                      : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {mode === "unresolved" ? t("Unresolved") : t("All")}
                </button>
              );
            })}
          </div>
          <span className="text-[12px] text-[var(--muted-foreground)]">
            {t("Total")}: {total}
          </span>
        </div>

        {loading ? (
          <div className="flex min-h-[420px] items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-[var(--muted-foreground)]" />
          </div>
        ) : items.length === 0 ? (
          <div className="flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-dashed border-[var(--border)] text-center">
            <div className="mb-3 rounded-xl bg-[var(--muted)] p-2.5 text-[var(--muted-foreground)]">
              <NotebookPen size={18} />
            </div>
            <p className="text-[14px] font-medium text-[var(--foreground)]">
              {t("No wrong answers yet")}
            </p>
            <p className="mt-1.5 max-w-xs text-[13px] text-[var(--muted-foreground)]">
              {t("Mistakes from your quizzes will appear here for review.")}
            </p>
          </div>
        ) : (
          <ul className="flex flex-col gap-3">
            {items.map((item) => {
              const disabled = pendingId === item.id;
              return (
                <li
                  key={item.id}
                  className={`rounded-xl border border-[var(--border)] px-5 py-4 transition-opacity ${
                    disabled ? "opacity-60" : ""
                  } ${item.resolved ? "bg-[var(--muted)]/30" : ""}`}
                >
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="text-[14px] font-medium text-[var(--foreground)]">
                        <MarkdownRenderer
                          content={item.question}
                          variant="prose"
                          className="text-[14px] leading-relaxed"
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => void handleToggleResolved(item)}
                        disabled={disabled}
                        title={
                          item.resolved
                            ? t("Mark as Unresolved")
                            : t("Mark as Resolved")
                        }
                        className="rounded-lg p-1.5 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] disabled:opacity-40"
                      >
                        {item.resolved ? (
                          <CheckCircle2 className="h-4 w-4 text-[var(--primary)]" />
                        ) : (
                          <Circle className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={() => void handleDelete(item)}
                        disabled={disabled}
                        title={t("Delete")}
                        className="rounded-lg p-1.5 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)] disabled:opacity-40"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div className="grid gap-2 text-[13px] sm:grid-cols-2">
                    <div className="rounded-lg bg-[var(--muted)]/40 px-3 py-2">
                      <div className="text-[11px] uppercase tracking-wide text-[var(--muted-foreground)]">
                        {t("Your Answer")}
                      </div>
                      <div className="mt-1 text-[var(--foreground)]">
                        {item.user_answer || <span className="text-[var(--muted-foreground)]">—</span>}
                      </div>
                    </div>
                    <div className="rounded-lg bg-[var(--muted)]/40 px-3 py-2">
                      <div className="text-[11px] uppercase tracking-wide text-[var(--muted-foreground)]">
                        {t("Correct Answer")}
                      </div>
                      <div className="mt-1 text-[var(--foreground)]">
                        {item.correct_answer || <span className="text-[var(--muted-foreground)]">—</span>}
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-[11px] text-[var(--muted-foreground)]">
                    <Link
                      href={`/?session=${encodeURIComponent(item.session_id)}`}
                      className="truncate hover:text-[var(--foreground)] hover:underline"
                    >
                      {t("From session")}: {item.session_title || item.session_id}
                    </Link>
                    <span>{formatDate(item.created_at)}</span>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
