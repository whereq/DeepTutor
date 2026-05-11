/**
 * Single source of truth for "what surface am I on?"
 *
 * The product has two top-level surfaces whose chat history must stay
 * isolated:
 *
 *   • ``chat``     — manual capability picker (``/chat``, ``/space/chat-history``)
 *   • ``co_learn`` — auto router            (``/co-learn``, ``/space/co-learn-history``)
 *
 * The backend tags each session row with the surface that created it;
 * the frontend filters by surface in every sidebar and history page.
 * If a third surface is ever added, edit this file ONLY — every sidebar
 * derives from ``surfaceForPath``.
 */

export type SurfaceKind = "chat" | "co_learn";

export interface Surface {
  readonly kind: SurfaceKind;
  /** Route prefix used to build session URLs and "new chat" buttons. */
  readonly basePath: "/chat" | "/co-learn";
}

const CHAT: Surface = { kind: "chat", basePath: "/chat" };
const CO_LEARN: Surface = { kind: "co_learn", basePath: "/co-learn" };

// Path *prefixes* (exact match OR followed by ``/``) that map to each
// surface. ``startsWith(prefix)`` alone would over-match (e.g. ``/co-learn``
// would swallow a hypothetical ``/co-learn-archive``), so we enforce a
// path-segment boundary instead.
const PREFIXES: ReadonlyArray<readonly [Surface, readonly string[]]> = [
  [CO_LEARN, ["/co-learn", "/space/co-learn-history"]],
  [CHAT, ["/chat", "/space/chat-history"]],
];

function pathMatches(pathname: string, prefix: string): boolean {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

/**
 * Return the surface owning ``pathname``. Falls back to ``chat`` for any
 * route that doesn't explicitly belong elsewhere (knowledge, settings, …) —
 * the chat surface is the safe default since it's the legacy/manual mode.
 */
export function surfaceForPath(
  pathname: string | null | undefined,
): Surface {
  if (!pathname) return CHAT;
  for (const [surface, prefixes] of PREFIXES) {
    if (prefixes.some((p) => pathMatches(pathname, p))) return surface;
  }
  return CHAT;
}

export const SURFACES = { chat: CHAT, co_learn: CO_LEARN } as const;
