"use client";

import { ReactNode } from "react";

interface TooltipProps {
  label: string;
  description?: string;
  children: ReactNode;
  side?: "right" | "bottom";
}

export function Tooltip({
  label,
  description,
  children,
  side = "right",
}: TooltipProps) {
  const sideStyles = {
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
  };

  return (
    <div className="group relative inline-flex">
      {children}
      <div
        className={`
          absolute z-50 whitespace-nowrap rounded-lg bg-[var(--popover)] px-3 py-1.5 text-xs text-[var(--popover-foreground)] shadow-md
          opacity-0 group-hover:opacity-100 transition-opacity duration-200
          pointer-events-none
          ${sideStyles[side]}
        `}
      >
        <div className="font-medium">{label}</div>
        {description && (
          <div className="mt-0.5 text-[var(--muted-foreground)] text-[11px]">
            {description}
          </div>
        )}
      </div>
    </div>
  );
}
