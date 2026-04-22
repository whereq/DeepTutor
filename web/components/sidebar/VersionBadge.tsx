"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

interface VersionPayload {
  tag: string | null;
  name: string | null;
  url: string | null;
  publishedAt: string | null;
  source: "github" | "fallback";
}

interface VersionBadgeProps {
  /** Render the compact variant for the collapsed sidebar (currently hidden). */
  collapsed?: boolean;
}

let _cache: VersionPayload | null = null;
let _inflight: Promise<VersionPayload | null> | null = null;

async function loadVersion(): Promise<VersionPayload | null> {
  if (_cache) return _cache;
  if (_inflight) return _inflight;
  _inflight = (async () => {
    try {
      const res = await fetch("/api/version", { cache: "force-cache" });
      if (!res.ok) return null;
      const data = (await res.json()) as VersionPayload;
      _cache = data;
      return data;
    } catch {
      return null;
    } finally {
      _inflight = null;
    }
  })();
  return _inflight;
}

interface ParsedBuild {
  /** Clean tag if exactly on a release commit, else null. */
  tag: string | null;
  /** True if `git describe` shows commits past the tag, or a dirty worktree. */
  isDev: boolean;
  /** True if the worktree was dirty at build time. */
  isDirty: boolean;
  /** Human-readable display ("v1.2.3", "v1.2.3+5", "v1.2.3+5·dev"). */
  display: string;
  /** Original raw value, for tooltip. */
  raw: string;
}

// Parse `git describe --tags --always --dirty=-dev` style output.
// Examples we want to handle:
//   "v1.2.3"                    → exactly on tag
//   "v1.2.3-5-gabc1234"         → 5 commits past v1.2.3
//   "v1.2.3-5-gabc1234-dev"     → 5 commits past v1.2.3 + dirty
//   "v1.2.3-dev"                → on tag but dirty
//   "abc1234"                   → no tag yet (shouldn't happen here)
function parseBuild(raw: string): ParsedBuild | null {
  if (!raw) return null;
  const isDirty = raw.endsWith("-dev");
  const stripped = isDirty ? raw.slice(0, -4) : raw;

  const cleanTag = stripped.match(/^v?(\d+\.\d+\.\d+)$/);
  if (cleanTag) {
    const tag = `v${cleanTag[1]}`;
    return {
      tag,
      isDev: isDirty,
      isDirty,
      display: isDirty ? `${tag}·dev` : tag,
      raw,
    };
  }

  const ahead = stripped.match(/^v?(\d+\.\d+\.\d+)-(\d+)-g[0-9a-f]+$/);
  if (ahead) {
    const tag = `v${ahead[1]}`;
    const display = `${tag}+${ahead[2]}${isDirty ? "·dev" : ""}`;
    return { tag, isDev: true, isDirty, display, raw };
  }

  return { tag: null, isDev: true, isDirty, display: "dev", raw };
}

// Strict normalization for the GitHub release tag (always "v1.2.3" form).
function normalizeStrict(raw: string | null | undefined): string | null {
  if (!raw) return null;
  const m = raw.match(/^v?(\d+\.\d+\.\d+)$/);
  return m ? `v${m[1]}` : null;
}

type Status = "latest" | "outdated" | "dev" | "unknown";

export function VersionBadge({ collapsed = false }: VersionBadgeProps) {
  const { t } = useTranslation();
  const [data, setData] = useState<VersionPayload | null>(_cache);

  useEffect(() => {
    let cancelled = false;
    if (!_cache) {
      loadVersion().then((v) => {
        if (!cancelled) setData(v);
      });
    }
    return () => {
      cancelled = true;
    };
  }, []);

  const buildRaw = process.env.NEXT_PUBLIC_APP_VERSION || "";
  const build = parseBuild(buildRaw);
  const latestNorm = normalizeStrict(data?.tag);

  const { status, displayTag, href, tooltip } = useMemo(() => {
    let status: Status = "unknown";
    if (build?.isDev) {
      status = "dev";
    } else if (build?.tag && latestNorm) {
      status = build.tag === latestNorm ? "latest" : "outdated";
    }

    // Display: prefer the running build (most accurate), fall back to the
    // latest GitHub release as an informational placeholder.
    const displayTag = build?.display ?? latestNorm ?? null;

    const href =
      data?.url ??
      (latestNorm
        ? `https://github.com/HKUDS/DeepTutor/releases/tag/${latestNorm}`
        : "https://github.com/HKUDS/DeepTutor/releases");

    let tooltip: string;
    if (status === "latest" && displayTag) {
      tooltip = `${displayTag} · ${t("Up to date")}`;
    } else if (status === "outdated" && build?.tag && latestNorm) {
      tooltip = `${build.tag} · ${t("Update available")}: ${latestNorm}`;
    } else if (status === "dev") {
      const base = `${t("Development build")}: ${build?.raw ?? ""}`;
      tooltip = latestNorm
        ? `${base} · ${t("Latest release")}: ${latestNorm}`
        : base;
    } else if (displayTag) {
      tooltip = `${t("Latest release")}: ${displayTag}`;
    } else {
      tooltip = t("Loading...");
    }

    return { status, displayTag, href, tooltip };
  }, [build, latestNorm, data?.url, t]);

  // Keep the collapsed sidebar entirely free of version chrome.
  if (collapsed) return null;

  const dotClass =
    status === "latest"
      ? "bg-emerald-500/45"
      : status === "outdated"
        ? "bg-amber-500/55"
        : status === "dev"
          ? "bg-sky-500/45"
          : "bg-[var(--muted-foreground)]/25";

  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer noopener"
      title={tooltip}
      className="group/ver flex min-w-0 flex-1 items-center gap-2 rounded-lg px-3 py-1.5 text-[11px] font-mono tabular-nums tracking-tight text-[var(--muted-foreground)]/55 transition-colors hover:bg-[var(--background)]/50 hover:text-[var(--muted-foreground)]"
    >
      <span
        className={`h-1.5 w-1.5 shrink-0 rounded-full transition-colors ${dotClass}`}
        aria-hidden="true"
      />
      <span className="truncate leading-none decoration-[var(--muted-foreground)]/40 decoration-dotted underline-offset-[3px] group-hover/ver:underline">
        {displayTag ?? "—"}
      </span>
    </a>
  );
}
