import type { ReactNode } from "react";

export const INPUT_CLS =
  "h-[30px] rounded-lg border border-[var(--border)]/30 bg-[var(--background)]/50 px-2.5 text-[12px] text-[var(--foreground)] outline-none transition-colors hover:border-[var(--border)]/50 focus:border-[var(--primary)]/35 placeholder:text-[var(--muted-foreground)]/40";

export function Field({
  label,
  width,
  children,
}: {
  label: string;
  width?: string;
  children: ReactNode;
}) {
  return (
    <label className={`flex min-w-0 flex-col ${width || ""}`}>
      <span className="mb-0.5 text-[10px] font-medium text-[var(--muted-foreground)]/60">
        {label}
      </span>
      {children}
    </label>
  );
}
