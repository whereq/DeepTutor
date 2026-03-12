"use client";

import { useEffect, useMemo, useState } from "react";
import { Brain, Eraser, Loader2 } from "lucide-react";
import { apiUrl } from "@/lib/api";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";

interface MemoryFile {
  type: string;
  label: string;
  content: string;
}

const TABS = [
  { type: "summary", label: "Summary" },
  { type: "weakness", label: "Weaknesses" },
  { type: "reflection", label: "Reflection" },
];

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryFile[]>([]);
  const [activeTab, setActiveTab] = useState("summary");
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  const loadMemory = async () => {
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/v1/memory/list"));
      const data = await res.json();
      setMemories(data.memories || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemory();
  }, []);

  const active = useMemo(
    () => memories.find((item) => item.type === activeTab),
    [activeTab, memories],
  );

  const clearMemory = async () => {
    if (!window.confirm("Clear all memory files?")) return;
    setClearing(true);
    try {
      await fetch(apiUrl("/api/v1/memory/clear"), { method: "POST" });
      await loadMemory();
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-3xl px-6 py-8">
        {/* Header */}
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--foreground)]">
              Memory
            </h1>
            <p className="mt-1 text-[13px] text-[var(--muted-foreground)]">
              Read the learner profile derived from your activity history.
            </p>
          </div>
          <button
            onClick={clearMemory}
            disabled={clearing}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-[13px] text-[var(--foreground)] transition-colors hover:bg-[var(--muted)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            {clearing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Eraser size={14} />}
            Clear memory
          </button>
        </div>

        {/* Tab bar */}
        <div className="mb-5 inline-flex w-full rounded-lg border border-[var(--border)] bg-[var(--muted)] p-0.5">
          {TABS.map((tab) => (
            <button
              key={tab.type}
              onClick={() => setActiveTab(tab.type)}
              className={`flex-1 rounded-md px-4 py-1.5 text-[13px] font-medium transition-all ${
                activeTab === tab.type
                  ? "bg-[var(--card)] text-[var(--foreground)] shadow-sm"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] shadow-sm">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-5 w-5 animate-spin text-[var(--muted-foreground)]" />
            </div>
          ) : active?.content ? (
            <div className="p-5">
              <MarkdownRenderer
                content={active.content}
                variant="prose"
                className="text-[14px] leading-relaxed"
              />
            </div>
          ) : (
            <div className="flex min-h-[280px] flex-col items-center justify-center p-8 text-center">
              <div className="mb-3 rounded-xl bg-[var(--muted)] p-3 text-[var(--muted-foreground)]">
                <Brain size={20} />
              </div>
              <p className="text-[15px] font-medium text-[var(--foreground)]">No memory yet</p>
              <p className="mt-1.5 max-w-sm text-[13px] leading-relaxed text-[var(--muted-foreground)]">
                Memory files will appear here once DeepTutor has enough interaction history.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
