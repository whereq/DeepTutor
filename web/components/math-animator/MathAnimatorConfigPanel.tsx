"use client";

import type { MathAnimatorFormConfig } from "@/lib/math-animator-types";

interface MathAnimatorConfigPanelProps {
  value: MathAnimatorFormConfig;
  onChange: (next: MathAnimatorFormConfig) => void;
}

const INPUT_CLS =
  "h-[32px] rounded-md border border-[var(--border)]/30 bg-[var(--background)]/50 px-2.5 text-[12px] text-[var(--foreground)] outline-none transition-colors hover:border-[var(--border)]/50 focus:border-[var(--primary)]/35 placeholder:text-[var(--muted-foreground)]/40";

export default function MathAnimatorConfigPanel({
  value,
  onChange,
}: MathAnimatorConfigPanelProps) {
  const update = <K extends keyof MathAnimatorFormConfig>(
    key: K,
    val: MathAnimatorFormConfig[K],
  ) => onChange({ ...value, [key]: val });

  return (
    <div className="flex flex-wrap items-end gap-x-3 gap-y-2 px-3.5 py-2.5">
      <Field label="Output" width="w-[100px]">
        <select
          value={value.output_mode}
          onChange={(e) => update("output_mode", e.target.value as MathAnimatorFormConfig["output_mode"])}
          className={`${INPUT_CLS} w-full`}
        >
          <option value="video">Video</option>
          <option value="image">Image</option>
        </select>
      </Field>

      <Field label="Quality" width="w-[100px]">
        <select
          value={value.quality}
          onChange={(e) => update("quality", e.target.value as MathAnimatorFormConfig["quality"])}
          className={`${INPUT_CLS} w-full`}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </Field>

      <Field label="Style Hint" width="min-w-[160px] flex-1">
        <input
          type="text"
          value={value.style_hint}
          onChange={(e) => update("style_hint", e.target.value)}
          placeholder="Style, pacing, color..."
          className={`${INPUT_CLS} w-full`}
        />
      </Field>
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
  children: React.ReactNode;
}) {
  return (
    <label className={`flex min-w-0 flex-col ${width || ""}`}>
      <span className="mb-1 text-[9px] font-medium uppercase tracking-[0.08em] text-[var(--muted-foreground)]/40">
        {label}
      </span>
      {children}
    </label>
  );
}
