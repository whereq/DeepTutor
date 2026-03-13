"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState } from "react";
import { Brain, Eraser, Loader2, RefreshCw, Save } from "lucide-react";
import { useAppShell } from "@/context/AppShellContext";
import { apiUrl } from "@/lib/api";

const MarkdownRenderer = dynamic(() => import("@/components/common/MarkdownRenderer"), {
  ssr: false,
});

interface MemoryPayload {
  content: string;
  exists: boolean;
  updated_at: string | null;
}

function formatUpdatedAt(value: string | null): string {
  if (!value) return "Not updated yet";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return date.toLocaleString();
}

export default function MemoryPage() {
  const { activeSessionId, language } = useAppShell();
  const [memory, setMemory] = useState<MemoryPayload>({
    content: "",
    exists: false,
    updated_at: null,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editorValue, setEditorValue] = useState("");
  const [activeView, setActiveView] = useState<"edit" | "preview">("edit");
  const [toast, setToast] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const hasChanges = editorValue !== memory.content;

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 3500);
    return () => clearTimeout(timer);
  }, [toast]);

  const loadMemory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/v1/memory"));
      const data = await res.json();
      setMemory({
        content: data.content || "",
        exists: Boolean(data.exists),
        updated_at: data.updated_at || null,
      });
      setEditorValue(data.content || "");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadMemory();
  }, [loadMemory]);

  const refreshMemory = useCallback(async () => {
    setRefreshing(true);
    try {
      const res = await fetch(apiUrl("/api/v1/memory/refresh"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: activeSessionId || undefined,
          language,
        }),
      });
      const data = await res.json();
      setMemory({
        content: data.content || "",
        exists: Boolean(data.exists),
        updated_at: data.updated_at || null,
      });
      setEditorValue(data.content || "");
      setToast("Memory refreshed");
    } finally {
      setRefreshing(false);
    }
  }, [activeSessionId, language]);

  const clearMemory = useCallback(async () => {
    if (!window.confirm("Clear memory.md?")) return;
    setClearing(true);
    try {
      const res = await fetch(apiUrl("/api/v1/memory/clear"), { method: "POST" });
      const data = await res.json();
      setMemory({
        content: data.content || "",
        exists: Boolean(data.exists),
        updated_at: data.updated_at || null,
      });
      setEditorValue(data.content || "");
      setToast("Memory cleared");
    } finally {
      setClearing(false);
    }
  }, []);

  const saveMemory = useCallback(async () => {
    setSaving(true);
    try {
      const res = await fetch(apiUrl("/api/v1/memory"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: editorValue }),
      });
      const data = await res.json();
      setMemory({
        content: data.content || "",
        exists: Boolean(data.exists),
        updated_at: data.updated_at || null,
      });
      setEditorValue(data.content || "");
      setToast("Memory saved");
    } finally {
      setSaving(false);
    }
  }, [editorValue]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        void saveMemory();
      }
    },
    [saveMemory],
  );

  return (
    <div className="h-full overflow-y-auto [scrollbar-gutter:stable]">
      <div className="mx-auto max-w-[960px] px-6 py-8">

        {/* ── Header ── */}
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-[24px] font-semibold tracking-tight text-[var(--foreground)]">
              Memory
            </h1>
            {toast ? (
              <p className="mt-1 text-[13px] text-[var(--primary)] animate-fade-in">
                {toast}
              </p>
            ) : (
              <p className="mt-1 text-[13px] text-[var(--muted-foreground)]">
                {hasChanges ? "Unsaved changes" : "All changes saved"}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={saveMemory}
              disabled={saving}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)]/50 px-3 py-1.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:opacity-40"
            >
              {saving ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="h-3 w-3" />}
              Save
            </button>
            <button
              onClick={refreshMemory}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)]/50 px-3 py-1.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:opacity-40"
            >
              {refreshing ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
              Refresh
            </button>
            <button
              onClick={clearMemory}
              disabled={clearing}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)]/50 px-3 py-1.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:opacity-40"
            >
              {clearing ? <Loader2 className="h-3 w-3 animate-spin" /> : <Eraser className="h-3 w-3" />}
              Clear
            </button>
          </div>
        </div>

        {/* ── Meta & View toggle ── */}
        <div className="mb-8 flex items-center justify-between border-b border-[var(--border)]/50 pb-6">
          <div className="flex items-center gap-1">
            {(["edit", "preview"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setActiveView(v)}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[13px] transition-colors ${
                  activeView === v
                    ? "bg-[var(--muted)] font-medium text-[var(--foreground)]"
                    : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                }`}
              >
                {v === "edit" ? "Edit" : "Preview"}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4 text-[12px] text-[var(--muted-foreground)]">
            <span>
              Updated: {formatUpdatedAt(memory.updated_at)}
            </span>
            <span className="text-[var(--border)]">·</span>
            <span>
              Source: {activeSessionId ? "current session" : "latest session"}
            </span>
          </div>
        </div>

        {/* ── Content ── */}
        {loading ? (
          <div className="flex min-h-[420px] items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-[var(--muted-foreground)]" />
          </div>
        ) : activeView === "edit" ? (
          <div>
            <textarea
              ref={textareaRef}
              value={editorValue}
              onChange={(e) => setEditorValue(e.target.value)}
              onKeyDown={handleKeyDown}
              spellCheck={false}
              className="min-h-[480px] w-full resize-none rounded-xl border border-[var(--border)] bg-transparent px-5 py-4 font-mono text-[13px] leading-7 text-[var(--foreground)] outline-none transition-colors focus:border-[var(--ring)] placeholder:text-[var(--muted-foreground)]/40"
              placeholder={"## Preferences\n- ...\n\n## Context\n- ..."}
            />
            <p className="mt-2 text-[11px] text-[var(--muted-foreground)]/40">
              Cmd+S to save · Markdown supported
            </p>
          </div>
        ) : editorValue.trim() ? (
          <div className="rounded-xl border border-[var(--border)] px-6 py-5">
            <MarkdownRenderer
              content={editorValue}
              variant="prose"
              className="text-[14px] leading-relaxed"
            />
          </div>
        ) : (
          <div className="flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-dashed border-[var(--border)] text-center">
            <div className="mb-3 rounded-xl bg-[var(--muted)] p-2.5 text-[var(--muted-foreground)]">
              <Brain size={18} />
            </div>
            <p className="text-[14px] font-medium text-[var(--foreground)]">No memory yet</p>
            <p className="mt-1.5 max-w-xs text-[13px] text-[var(--muted-foreground)]">
              Refresh from a session or write directly in the editor.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
