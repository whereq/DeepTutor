"use client";

/**
 * SessionViewerPanel — full right-side sidebar with browser-style tabs that
 * can hold (a) attachment previews and (b) embedded web pages clicked from
 * assistant messages.
 *
 * - Tabs across the top of the panel; each closeable.
 * - File tabs use the same lazy previewer set as FilePreviewDrawer.
 * - Web tabs render an iframe of the URL. Cross-origin frames may refuse
 *   to load — we expose an "Open in browser" affordance so the user can
 *   always fall back. The user's network ultimately decides what loads.
 * - Imperative API via ref: openFileTab(att), openWebTab(url).
 */

import {
  forwardRef,
  memo,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import dynamic from "next/dynamic";
import {
  AlertCircle,
  ArrowRight,
  ExternalLink,
  FileUp,
  Globe,
  Loader2,
  Paperclip,
  X,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  previewKindFor,
  resolveSourceUrl,
  type FilePreviewSource,
} from "@/components/chat/preview/previewerFor";
import { apiUrl } from "@/lib/api";
import { docIconFor } from "@/lib/doc-attachments";
import type { MessageAttachment } from "@/context/UnifiedChatContext";

const PdfPreview = dynamic(() => import("@/components/chat/preview/previewers/PdfPreview"));
const ImagePreview = dynamic(() => import("@/components/chat/preview/previewers/ImagePreview"));
const SvgPreview = dynamic(() => import("@/components/chat/preview/previewers/SvgPreview"));
const MarkdownPreview = dynamic(() => import("@/components/chat/preview/previewers/MarkdownPreview"));
const TextPreview = dynamic(() => import("@/components/chat/preview/previewers/TextPreview"));
const OfficeTextPreview = dynamic(() => import("@/components/chat/preview/previewers/OfficeTextPreview"));
const FallbackPreview = dynamic(() => import("@/components/chat/preview/previewers/FallbackPreview"));

const ANIM_MS = 220;

/* ------------------------------------------------------------------ */
/*  Tab types                                                          */
/* ------------------------------------------------------------------ */

type ViewerTab =
  | { kind: "file"; id: string; label: string; source: FilePreviewSource }
  | { kind: "web"; id: string; label: string; url: string };

export interface SessionViewerPanelHandle {
  openFileTab(a: MessageAttachment): void;
  openWebTab(url: string): void;
}

interface SessionViewerPanelProps {
  open: boolean;
  sessionId: string | null;
  onClose: () => void;
  onAutoOpen: () => void;
}

function fileTabIdFor(a: MessageAttachment, fallback: number): string {
  return `file:${a.id ?? a.filename ?? `idx-${fallback}`}`;
}

function webTabIdFor(url: string): string {
  return `web:${url}`;
}

function hostnameFor(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url.slice(0, 32);
  }
}

function attachmentToPreviewSource(a: MessageAttachment): FilePreviewSource {
  return {
    filename: a.filename || "",
    mimeType: a.mime_type,
    type: a.type,
    url: a.url,
    base64: a.base64,
    extractedText: a.extracted_text,
    id: a.id,
  };
}

/* ------------------------------------------------------------------ */
/*  Panel                                                              */
/* ------------------------------------------------------------------ */

function SessionViewerPanelInner(
  { open, sessionId, onClose, onAutoOpen }: SessionViewerPanelProps,
  ref: React.Ref<SessionViewerPanelHandle>,
) {
  const { t } = useTranslation();
  const [tabs, setTabs] = useState<ViewerTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);

  // Wipe tabs whenever the session changes — preview/web state belongs to
  // the conversation that triggered it.
  const [trackedSessionId, setTrackedSessionId] = useState<string | null>(
    sessionId,
  );
  if (trackedSessionId !== sessionId) {
    setTrackedSessionId(sessionId);
    setTabs([]);
    setActiveTabId(null);
  }

  const openFileTab = useCallback(
    (a: MessageAttachment) => {
      setTabs((prev) => {
        const id = fileTabIdFor(a, prev.length);
        const existingIdx = prev.findIndex((tab) => tab.id === id);
        if (existingIdx >= 0) {
          setActiveTabId(id);
          return prev;
        }
        const label = a.filename || "Attachment";
        const next: ViewerTab = {
          kind: "file",
          id,
          label,
          source: attachmentToPreviewSource(a),
        };
        setActiveTabId(id);
        return [...prev, next];
      });
      onAutoOpen();
    },
    [onAutoOpen],
  );

  const openWebTab = useCallback(
    (url: string) => {
      setTabs((prev) => {
        const id = webTabIdFor(url);
        const existingIdx = prev.findIndex((tab) => tab.id === id);
        if (existingIdx >= 0) {
          setActiveTabId(id);
          return prev;
        }
        const next: ViewerTab = {
          kind: "web",
          id,
          label: hostnameFor(url),
          url,
        };
        setActiveTabId(id);
        return [...prev, next];
      });
      onAutoOpen();
    },
    [onAutoOpen],
  );

  useImperativeHandle(
    ref,
    () => ({ openFileTab, openWebTab }),
    [openFileTab, openWebTab],
  );

  const closeTab = useCallback(
    (id: string) => {
      setTabs((prev) => {
        const idx = prev.findIndex((tab) => tab.id === id);
        if (idx === -1) return prev;
        const next = prev.filter((tab) => tab.id !== id);
        if (activeTabId === id) {
          if (next.length === 0) {
            setActiveTabId(null);
            // Closing the last tab also closes the panel — there's nothing
            // useful left to look at.
            onClose();
          } else {
            const fallback = next[Math.max(0, idx - 1)] ?? next[0];
            setActiveTabId(fallback.id);
          }
        }
        return next;
      });
    },
    [activeTabId, onClose],
  );

  // ESC closes the panel.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  // The viewer is visible whenever it's open — even with no tabs. The
  // tabs.length === 0 case renders a "Landing" page where the user can
  // paste a URL or pick a local file to open as the first tab.
  const visible = open;
  const activeTab = tabs.find((tab) => tab.id === activeTabId) ?? null;

  const openLocalFile = useCallback(
    (file: File) => {
      const url = URL.createObjectURL(file);
      openFileTab({
        type: file.type.startsWith("image/") ? "image" : "file",
        filename: file.name,
        mime_type: file.type,
        url,
      });
    },
    [openFileTab],
  );

  return (
    <div
      role="dialog"
      aria-hidden={!visible}
      className={`fixed right-0 top-0 z-[30] flex h-full w-[min(620px,92vw)] flex-col border-l border-[var(--border)] bg-[var(--card)] shadow-2xl transition-transform ease-out ${
        visible ? "translate-x-0" : "translate-x-full"
      }`}
      style={{
        willChange: "transform",
        transitionDuration: `${ANIM_MS}ms`,
        pointerEvents: visible ? "auto" : "none",
      }}
    >
      <TabBar
        tabs={tabs}
        activeTabId={activeTabId}
        onSelect={setActiveTabId}
        onCloseTab={closeTab}
        onClosePanel={onClose}
      />
      <div className="relative flex-1 overflow-hidden bg-[var(--card)]">
        {activeTab?.kind === "file" ? (
          <FileTabBody source={activeTab.source} />
        ) : activeTab?.kind === "web" ? (
          <WebTabBody url={activeTab.url} />
        ) : (
          <ViewerLanding
            onOpenWebTab={openWebTab}
            onOpenLocalFile={openLocalFile}
          />
        )}
      </div>
    </div>
  );
}

const SessionViewerPanel = memo(forwardRef(SessionViewerPanelInner));
export default SessionViewerPanel;

/* ------------------------------------------------------------------ */
/*  Tab bar                                                            */
/* ------------------------------------------------------------------ */

/**
 * Chrome-style tab bar. The strip itself is a muted band; the active tab
 * "lifts" out of it in the page-body colour with rounded top corners — so
 * the active tab and the body underneath read as one continuous surface,
 * exactly like a browser tab. No coloured top stripe; inactive tabs stay
 * transparent over the strip.
 */
function TabBar({
  tabs,
  activeTabId,
  onSelect,
  onCloseTab,
  onClosePanel,
}: {
  tabs: ViewerTab[];
  activeTabId: string | null;
  onSelect: (id: string) => void;
  onCloseTab: (id: string) => void;
  onClosePanel: () => void;
}) {
  const { t } = useTranslation();
  return (
    <div className="flex shrink-0 items-end gap-2 bg-[color-mix(in_srgb,var(--muted)_40%,var(--background))] px-2 pt-2 pb-0">
      <div className="flex min-w-0 flex-1 items-end gap-[2px] overflow-x-auto">
        {tabs.map((tab) => {
          const active = tab.id === activeTabId;
          const Icon = tab.kind === "web" ? Globe : Paperclip;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onSelect(tab.id)}
              className={`group inline-flex max-w-[180px] shrink-0 items-center gap-1.5 rounded-t-md px-2.5 py-1.5 text-[11.5px] font-medium transition-colors ${
                active
                  ? "bg-[var(--card)] text-[var(--foreground)]"
                  : "bg-transparent text-[var(--muted-foreground)] hover:bg-[color-mix(in_srgb,var(--card)_70%,transparent)] hover:text-[var(--foreground)]"
              }`}
              title={tab.label}
            >
              <Icon size={11} strokeWidth={1.9} className="shrink-0" />
              <span className="truncate">{tab.label}</span>
              <span
                role="button"
                tabIndex={-1}
                onClick={(e) => {
                  e.stopPropagation();
                  onCloseTab(tab.id);
                }}
                className="-mr-0.5 ml-0.5 rounded-sm p-[1px] text-[var(--muted-foreground)] opacity-60 transition-opacity hover:bg-[var(--muted)]/70 hover:text-[var(--foreground)] hover:opacity-100"
                aria-label={t("Close tab")}
              >
                <X size={10} />
              </span>
            </button>
          );
        })}
      </div>
      <button
        type="button"
        onClick={onClosePanel}
        className="mb-1 shrink-0 rounded-md p-1.5 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)]/45 hover:text-[var(--foreground)]"
        aria-label={t("Close viewer")}
        title={t("Close viewer")}
      >
        <X size={14} />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Landing state — shown when no tabs are open                        */
/* ------------------------------------------------------------------ */

function ViewerLanding({
  onOpenWebTab,
  onOpenLocalFile,
}: {
  onOpenWebTab: (url: string) => void;
  onOpenLocalFile: (file: File) => void;
}) {
  const { t } = useTranslation();
  const [urlInput, setUrlInput] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const submitUrl = useCallback(() => {
    const trimmed = urlInput.trim();
    if (!trimmed) return;
    const href = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    onOpenWebTab(href);
    setUrlInput("");
  }, [urlInput, onOpenWebTab]);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onOpenLocalFile(file);
      e.target.value = "";
    },
    [onOpenLocalFile],
  );

  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 px-8 py-10">
      <div className="text-center">
        <h2 className="text-[15px] font-semibold tracking-[-0.005em] text-[var(--foreground)]">
          {t("Viewer")}
        </h2>
        <p className="mt-1.5 text-[12px] text-[var(--muted-foreground)]">
          {t(
            "Paste a URL or open a local file. Attachments from chat will also land here.",
          )}
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submitUrl();
        }}
        className="flex w-full max-w-[420px] items-center gap-2 rounded-full border border-[var(--border)]/55 bg-[var(--background)] px-3 py-1.5 transition-colors focus-within:border-[var(--primary)]/40"
      >
        <Globe
          size={14}
          strokeWidth={1.8}
          className="shrink-0 text-[var(--muted-foreground)]"
        />
        <input
          type="text"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          placeholder={t("https://example.com")}
          className="min-w-0 flex-1 bg-transparent text-[13px] text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]/60"
        />
        <button
          type="submit"
          disabled={!urlInput.trim()}
          className="inline-flex shrink-0 items-center gap-1 rounded-full bg-[var(--primary)] px-3 py-1 text-[11px] font-medium text-white transition-opacity disabled:opacity-30"
          aria-label={t("Open URL")}
        >
          <ArrowRight size={11} strokeWidth={2.2} />
        </button>
      </form>

      <div className="flex items-center gap-2 text-[11px] text-[var(--muted-foreground)]/70">
        <span className="h-px w-12 bg-[var(--border)]/50" />
        <span>{t("or")}</span>
        <span className="h-px w-12 bg-[var(--border)]/50" />
      </div>

      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="inline-flex items-center gap-2 rounded-lg border border-[var(--border)]/55 bg-[var(--background)] px-3.5 py-2 text-[12px] font-medium text-[var(--foreground)] transition-colors hover:border-[var(--primary)]/35 hover:text-[var(--primary)]"
      >
        <FileUp size={13} strokeWidth={1.8} />
        {t("Open a local file")}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileSelect}
        aria-hidden="true"
        tabIndex={-1}
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  File tab body                                                      */
/* ------------------------------------------------------------------ */

function FileTabBody({ source }: { source: FilePreviewSource }) {
  const { t } = useTranslation();
  const previewUrl = useMemo(
    () => resolveSourceUrl(source, apiUrl),
    [source],
  );
  const kind = previewKindFor(source);
  const filename = source.filename || t("Attachment");
  const spec = docIconFor(filename);

  const openInBrowser = useCallback(() => {
    if (previewUrl) {
      window.open(previewUrl, "_blank", "noopener,noreferrer");
      return;
    }
    if (source.base64) {
      const mime = source.mimeType || "application/octet-stream";
      const url = `data:${mime};base64,${source.base64}`;
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }, [previewUrl, source]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 items-center gap-2 border-b border-[var(--border)]/40 bg-[var(--card)] px-4 py-2.5">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-[var(--muted)]/55">
          <spec.Icon size={14} strokeWidth={1.6} className={spec.tint} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[12.5px] font-semibold text-[var(--foreground)]">
            {filename}
          </div>
          <div className="truncate text-[10px] uppercase tracking-wide text-[var(--muted-foreground)]">
            {spec.label}
          </div>
        </div>
        <button
          type="button"
          onClick={openInBrowser}
          className="inline-flex shrink-0 items-center gap-1 rounded-md border border-[var(--border)]/55 px-2 py-1 text-[11px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--primary)]/35 hover:text-[var(--primary)]"
        >
          <ExternalLink size={11} strokeWidth={1.8} />
          {t("Open in browser")}
        </button>
      </div>
      <div className="relative flex-1 overflow-hidden">
        <PreviewBody source={source} previewUrl={previewUrl} kind={kind} />
      </div>
    </div>
  );
}

const PreviewBody = memo(function PreviewBody({
  source,
  previewUrl,
  kind,
}: {
  source: FilePreviewSource;
  previewUrl: string | null;
  kind: ReturnType<typeof previewKindFor> | null;
}) {
  const filename = source.filename;

  if (kind === "office-text") {
    return (
      <OfficeTextPreview
        filename={filename}
        extractedText={source.extractedText}
        url={previewUrl}
      />
    );
  }

  if (!previewUrl) {
    return <FallbackPreview filename={filename} url={null} reason="legacy" />;
  }

  switch (kind) {
    case "pdf":
      return <PdfPreview url={previewUrl} filename={filename} />;
    case "image":
      return <ImagePreview url={previewUrl} filename={filename} />;
    case "svg":
      return <SvgPreview url={previewUrl} filename={filename} />;
    case "markdown":
      return (
        <div className="h-full overflow-y-auto">
          <MarkdownPreview url={previewUrl} />
        </div>
      );
    case "code":
    case "text":
      return (
        <div className="h-full overflow-y-auto">
          <TextPreview url={previewUrl} filename={filename} />
        </div>
      );
    case "fallback":
    default:
      return <FallbackPreview filename={filename} url={previewUrl} />;
  }
});

/* ------------------------------------------------------------------ */
/*  Web tab body — iframe with safety fallback                         */
/* ------------------------------------------------------------------ */

/**
 * Web preview tab. Many sites set `X-Frame-Options: DENY` or a CSP
 * `frame-ancestors` directive that flat-out refuses iframe embedding — a
 * browser-enforced anti-clickjacking measure we can't bypass from the
 * frontend. We can't *detect* the failure reliably either (cross-origin
 * iframes are opaque to JS), so we lean on UX honesty:
 *
 *  • A persistent info banner at the top tells the user upfront that some
 *    sites won't load, and exposes "Open in browser" as a big primary
 *    action right next to it.
 *  • A loading spinner is overlaid until either `onLoad` fires or a soft
 *    timeout (4.5 s) elapses. After the timeout we switch the banner copy
 *    to a more explicit "site likely refused embedding" warning so the
 *    user knows the spinner isn't a real load-in-progress.
 */
function WebTabBody({ url }: { url: string }) {
  const { t } = useTranslation();
  const [loaded, setLoaded] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const host = hostnameFor(url);

  const openInBrowser = useCallback(() => {
    window.open(url, "_blank", "noopener,noreferrer");
  }, [url]);

  useEffect(() => {
    setLoaded(false);
    setTimedOut(false);
    const timer = window.setTimeout(() => setTimedOut(true), 4500);
    return () => window.clearTimeout(timer);
  }, [url]);

  const blocked = timedOut && !loaded;

  return (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 items-center gap-2 border-b border-[var(--border)]/40 bg-[var(--card)] px-4 py-2.5">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-[var(--muted)]/55">
          <Globe
            size={14}
            strokeWidth={1.7}
            className="text-[var(--muted-foreground)]"
          />
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[12.5px] font-semibold text-[var(--foreground)]">
            {host}
          </div>
          <div className="truncate text-[10px] text-[var(--muted-foreground)]">
            {url}
          </div>
        </div>
        <button
          type="button"
          onClick={openInBrowser}
          className={`inline-flex shrink-0 items-center gap-1 rounded-md px-2.5 py-1 text-[11px] font-semibold transition-colors ${
            blocked
              ? "bg-[var(--primary)] text-white hover:bg-[var(--primary)]/90"
              : "border border-[var(--border)]/55 text-[var(--muted-foreground)] hover:border-[var(--primary)]/35 hover:text-[var(--primary)]"
          }`}
        >
          <ExternalLink size={11} strokeWidth={1.9} />
          {t("Open in browser")}
        </button>
      </div>

      {/* Persistent info banner — explains the iframe limitation. Swaps to
          a louder warning once we suspect the site has refused to embed. */}
      <div
        className={`flex shrink-0 items-start gap-2 border-b border-[var(--border)]/30 px-4 py-2 text-[11px] leading-snug ${
          blocked
            ? "bg-[color-mix(in_srgb,var(--primary)_8%,var(--card))] text-[var(--foreground)]"
            : "bg-[color-mix(in_srgb,var(--muted)_45%,var(--card))] text-[var(--muted-foreground)]"
        }`}
      >
        <AlertCircle
          size={12}
          strokeWidth={1.9}
          className={`mt-[1px] shrink-0 ${
            blocked
              ? "text-[var(--primary)]"
              : "text-[var(--muted-foreground)]"
          }`}
        />
        <span>
          {blocked
            ? t(
                "This site looks like it refused to embed (its security headers block iframes). Use “Open in browser” to view it in a real tab.",
              )
            : t(
                "Many sites refuse to embed for security reasons. If the page below stays blank, use “Open in browser”.",
              )}
        </span>
      </div>

      <div className="relative flex-1 overflow-hidden bg-[var(--background)]">
        <iframe
          key={url}
          src={url}
          title={host}
          onLoad={() => setLoaded(true)}
          className="h-full w-full border-0"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          referrerPolicy="no-referrer"
        />
        {!loaded && !timedOut ? (
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-2 bg-[var(--card)]/70 text-[12px] text-[var(--muted-foreground)] backdrop-blur-sm">
            <Loader2
              size={18}
              strokeWidth={1.7}
              className="animate-spin text-[var(--primary)]/80"
            />
            <span>{t("Loading {{host}}…", { host })}</span>
          </div>
        ) : null}
      </div>
    </div>
  );
}
