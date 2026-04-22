import { NextResponse } from "next/server";

/**
 * Returns the latest GitHub release for the project, used by the sidebar
 * version badge. The response is cached on the server side (ISR) so that
 * each visit doesn't hit GitHub directly — at most one upstream request
 * per `revalidate` window across all clients.
 */

// Refresh at most once per hour. Tune via env if needed.
export const revalidate = 3600;

const DEFAULT_REPO = "HKUDS/DeepTutor";

interface GithubRelease {
  tag_name: string;
  html_url: string;
  name: string | null;
  published_at: string | null;
  prerelease: boolean;
  draft: boolean;
}

interface VersionPayload {
  tag: string | null;
  name: string | null;
  url: string | null;
  publishedAt: string | null;
  source: "github" | "fallback";
}

const FALLBACK: VersionPayload = {
  tag: null,
  name: null,
  url: `https://github.com/${DEFAULT_REPO}/releases`,
  publishedAt: null,
  source: "fallback",
};

export async function GET() {
  const repo = process.env.NEXT_PUBLIC_GITHUB_REPO || DEFAULT_REPO;
  const url = `https://api.github.com/repos/${repo}/releases/latest`;

  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "deeptutor-web",
  };
  if (process.env.GITHUB_TOKEN) {
    headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }

  try {
    const res = await fetch(url, {
      headers,
      next: { revalidate },
    });
    if (!res.ok) {
      return NextResponse.json(
        { ...FALLBACK, url: `https://github.com/${repo}/releases` },
        { status: 200 },
      );
    }
    const data = (await res.json()) as GithubRelease;
    const payload: VersionPayload = {
      tag: data.tag_name ?? null,
      name: data.name ?? null,
      url: data.html_url ?? `https://github.com/${repo}/releases`,
      publishedAt: data.published_at ?? null,
      source: "github",
    };
    return NextResponse.json(payload, {
      status: 200,
      headers: {
        // Browser-side cache hint; server-side caching already handled by ISR.
        "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
      },
    });
  } catch {
    return NextResponse.json(
      { ...FALLBACK, url: `https://github.com/${repo}/releases` },
      { status: 200 },
    );
  }
}
