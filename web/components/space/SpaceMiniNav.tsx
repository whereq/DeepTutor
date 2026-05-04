"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "react-i18next";
import { LayoutGrid } from "lucide-react";
import { SPACE_ITEMS } from "@/lib/space-items";

export default function SpaceMiniNav() {
  const pathname = usePathname();
  const { t } = useTranslation();

  return (
    <aside className="flex h-full w-[224px] shrink-0 flex-col border-r border-[var(--border)] bg-[var(--card)]">
      <div className="flex items-center gap-2.5 border-b border-[var(--border)]/60 px-4 py-4">
        <span
          aria-hidden
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[var(--border)]/70 bg-[var(--background)] text-[var(--foreground)]"
        >
          <LayoutGrid size={14} strokeWidth={1.7} />
        </span>
        <div className="min-w-0">
          <h1 className="text-[15px] font-semibold leading-tight tracking-tight text-[var(--foreground)]">
            {t("Space")}
          </h1>
          <p className="mt-0.5 line-clamp-1 text-[10.5px] leading-snug text-[var(--muted-foreground)]/80">
            {t("Your personal learning library.")}
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 px-2 py-3">
        {SPACE_ITEMS.map(({ href, label, description, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              title={t(description)}
              className={`group flex h-12 items-center gap-2.5 rounded-lg px-2.5 transition-colors ${
                active
                  ? "bg-[var(--muted)]/60 text-[var(--foreground)]"
                  : "text-[var(--muted-foreground)] hover:bg-[var(--muted)]/40 hover:text-[var(--foreground)]"
              }`}
            >
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border transition-colors ${
                  active
                    ? "border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] shadow-sm"
                    : "border-[var(--border)]/50 bg-[var(--background)]/40 text-[var(--muted-foreground)] group-hover:border-[var(--border)]/80 group-hover:text-[var(--foreground)]"
                }`}
              >
                <Icon size={13} strokeWidth={active ? 1.9 : 1.6} />
              </span>
              <span
                className={`min-w-0 flex-1 truncate text-[13px] leading-tight tracking-tight ${
                  active ? "font-semibold" : "font-medium"
                }`}
              >
                {t(label)}
              </span>
              {active && (
                <span
                  aria-hidden
                  className="h-4 w-[2px] shrink-0 rounded-full bg-[var(--foreground)]/60"
                />
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
