"use client";

import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import type {
  DeepResearchFormConfig,
  ResearchDepth,
  ResearchMode,
} from "@/lib/research-types";
import { summarizeResearchConfig } from "@/lib/research-types";

interface ResearchConfigPanelProps {
  value: DeepResearchFormConfig;
  errors: Record<string, string>;
  collapsed: boolean;
  onChange: (next: DeepResearchFormConfig) => void;
  onToggleCollapsed: () => void;
}

const INPUT_CLS =
  "h-[32px] rounded-md border border-[var(--border)]/30 bg-[var(--background)]/50 px-2.5 text-[12px] text-[var(--foreground)] outline-none transition-colors hover:border-[var(--border)]/50 focus:border-[var(--primary)]/35";

const MODE_OPTIONS: Array<{ value: Exclude<ResearchMode, "">; label: string }> = [
  { value: "notes", label: "Study Notes" },
  { value: "report", label: "Report" },
  { value: "comparison", label: "Comparison" },
  { value: "learning_path", label: "Learning Path" },
];

const DEPTH_OPTIONS: Array<{ value: Exclude<ResearchDepth, "">; label: string }> = [
  { value: "quick", label: "Quick" },
  { value: "standard", label: "Standard" },
  { value: "deep", label: "Deep" },
];

export default function ResearchConfigPanel({
  value,
  errors: _errors,
  collapsed,
  onChange,
  onToggleCollapsed,
}: ResearchConfigPanelProps) {
  const update = <K extends keyof DeepResearchFormConfig>(
    key: K,
    next: DeepResearchFormConfig[K],
  ) => onChange({ ...value, [key]: next });

  const summary = summarizeResearchConfig(value);

  return (
    <div>
      <button
        type="button"
        onClick={onToggleCollapsed}
        className="flex w-full items-center gap-2 px-3.5 py-2 text-left transition-colors hover:opacity-80"
      >
        <span className="text-[11px] font-medium text-[var(--muted-foreground)]/55">Settings</span>
        {collapsed && summary !== "Incomplete settings" && (
          <span className="min-w-0 truncate text-[10px] text-[var(--muted-foreground)]/35">{summary}</span>
        )}
        <ChevronDown
          size={11}
          className={`ml-auto shrink-0 text-[var(--muted-foreground)]/40 transition-transform ${collapsed ? "" : "rotate-180"}`}
        />
      </button>

      {!collapsed && (
        <div className="flex flex-wrap items-end gap-x-3 gap-y-2 px-3.5 pb-2.5">
          <Field label="Mode" width="min-w-[130px] flex-1">
            <select
              value={value.mode}
              onChange={(e) => update("mode", e.target.value as ResearchMode)}
              className={`${INPUT_CLS} w-full`}
            >
              <option value="">Select...</option>
              {MODE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Depth" width="min-w-[130px] flex-1">
            <select
              value={value.depth}
              onChange={(e) => update("depth", e.target.value as ResearchDepth)}
              className={`${INPUT_CLS} w-full`}
            >
              <option value="">Select...</option>
              {DEPTH_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </Field>
        </div>
      )}
    </div>
  );
}

function Field({
  label,
  width,
  children,
}: {
  label: string;
  width?: string;
  children: ReactNode;
}) {
  return (
    <div className={width}>
      <div className="mb-1 text-[9px] font-medium uppercase tracking-[0.08em] text-[var(--muted-foreground)]/40">
        {label}
      </div>
      {children}
    </div>
  );
}
