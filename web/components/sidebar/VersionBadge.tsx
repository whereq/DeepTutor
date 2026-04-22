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

// Normalize a version-like string ("v1.2.3", "v1.2.3-3-gabc", "1.2.3-dev")
// down to its canonical "v1.2.3" form for equality comparison.
function normalize(raw: string | null | undefined): string | null {
  if (!raw) return null;
  const m = raw.match(/v?(\d+\.\d+\.\d+)/);
  return m ? `v${m[1]}` : null;
}

type Status = "latest" | "outdated" | "unknown";

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
  const buildNorm = normalize(buildRaw);
  const latestNorm = normalize(data?.tag);

  const { status, displayTag, href, tooltip } = useMemo(() => {
    let status: Status = "unknown";
    if (buildNorm && latestNorm) {
      status = buildNorm === latestNorm ? "latest" : "outdated";
    }

    // Show what the user is actually running when we know it; otherwise
    // fall back to the latest release as a passive informational display.
    const displayTag = buildNorm ?? latestNorm ?? null;

    const href =
      data?.url ??
      (latestNorm
        ? `https://github.com/HKUDS/DeepTutor/releases/tag/${latestNorm}`
        : "https://github.com/HKUDS/DeepTutor/releases");

    let tooltip: string;
    if (status === "latest" && displayTag) {
      tooltip = `${displayTag} · ${t("Up to date")}`;
    } else if (status === "outdated" && displayTag && latestNorm) {
      tooltip = `${displayTag} · ${t("Update available")}: ${latestNorm}`;
    } else if (displayTag) {
      tooltip = `${t("Latest release")}: ${displayTag}`;
    } else {
      tooltip = t("Loading...");
    }

    return { status, displayTag, href, tooltip };
  }, [buildNorm, latestNorm, data?.url, t]);

  // Keep the collapsed sidebar entirely free of version chrome.
  if (collapsed) return null;

  const dotClass =
    status === "latest"
      ? "bg-emerald-500/45"
      : status === "outdated"
        ? "bg-amber-500/55"
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
