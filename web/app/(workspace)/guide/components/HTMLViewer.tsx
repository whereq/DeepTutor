"use client";

import { useRef, useEffect } from "react";
import { Bug, Loader2 } from "lucide-react";
import { useKaTeXInjection } from "../hooks";
import { useTranslation } from "react-i18next";

interface HTMLViewerProps {
  html: string;
  currentIndex: number;
  loadingMessage: string;
  onOpenDebugModal: () => void;
}

/**
 * Regex that matches common LaTeX patterns NOT already wrapped in $..$ or $$..$$.
 * Used to detect bare LaTeX commands in text nodes.
 */
const BARE_LATEX_RE =
  /(?<![\\$])(?:\\(?:underbrace|mathbb|frac|text|sqrt|subseteq|supseteq|notsubset|mid|pmod|leq|geq|Rightarrow|Leftarrow|Rightarrow|neq|approx|infty|partial|nabla|forall|exists|emptyset|varnothing|in|notin|alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|vec|hat|bar|dot|tilde|overline|overbrace|boldsymbol|mathrm|mathit|mathbf|mathcal|mathfrak|mathscr|mathsf|mathtt|quad|qquad|ldots|cdots|vdots|ddots|prime|limits|sum|int|prod|oint|bigcup|bigcap|bigvee|bigwedge|bigoplus|bigotimes|binom|choose)[\s{])|\{[^}]*\\(?:underbrace|mathbb|frac|text|sqrt)/;

export default function HTMLViewer({
  html,
  currentIndex,
  loadingMessage,
  onOpenDebugModal,
}: HTMLViewerProps) {
  const { t } = useTranslation();
  const htmlFrameRef = useRef<HTMLIFrameElement>(null);
  const lastWrittenRef = useRef<string>("");
  const lastIndexRef = useRef<number>(currentIndex);
  const { injectKaTeX } = useKaTeXInjection();

  const sanitizeHtml = (rawHtml: string) =>
    rawHtml
      .replace(/<script(?![^>]*katex)[\s\S]*?>[\s\S]*?<\/script>/gi, "")
      .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, (match) => {
        if (/onload\s*=\s*(['"])renderMathInElement/i.test(match)) return match;
        return "";
      })
      .replace(/\s(href|src)\s*=\s*(['"])javascript:[\s\S]*?\2/gi, "");

  useEffect(() => {
    if (currentIndex !== lastIndexRef.current) {
      lastWrittenRef.current = "";
      lastIndexRef.current = currentIndex;
    }
  }, [currentIndex]);

  useEffect(() => {
    if (!html) return;

    const injected = injectKaTeX(html);
    const htmlWithKaTeX = sanitizeHtml(injected);

    if (lastWrittenRef.current === htmlWithKaTeX) {
      return;
    }

    const timer = setTimeout(() => {
      if (htmlFrameRef.current) {
        const iframe = htmlFrameRef.current;
        // Set srcdoc
        iframe.srcdoc = htmlWithKaTeX;
        lastWrittenRef.current = htmlWithKaTeX;

        /**
         * Fallback rendering strategy:
         * 1. Wait for CDN scripts to load
         * 2. Find text nodes with bare LaTeX (no $ wrapping)
         * 3. Wrap them in $...$ delimiters
         * 4. Call renderMathInElement to render everything
         */
        const fallbackDelays = [1500, 3000];
        const fallbackTimers = fallbackDelays.map((delay) =>
          setTimeout(() => {
            try {
              const doc = iframe.contentDocument;
              if (!doc || !doc.body) return;
              const win = doc.defaultView as Window & {
                renderMathInElement?: (el: HTMLElement, opts: Record<string, unknown>) => void;
              };
              if (typeof win?.renderMathInElement !== "function") return;

              let wrappedCount = 0;

              // Step 1: Find text nodes with bare LaTeX and fix them
              const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
              const nodesToProcess: Text[] = [];
              let node: Text | null;
              while ((node = walker.nextNode() as Text | null)) {
                // Skip if inside a .katex element (already rendered)
                const parent = node.parentElement;
                if (parent && parent.closest(".katex")) continue;

                const text = node.textContent || "";
                // Check for bare LaTeX patterns not already delimited
                if (BARE_LATEX_RE.test(text) && !/^\$.*\$$/.test(text.trim())) {
                  nodesToProcess.push(node);
                }
              }

              // Process each bare LaTeX text node
              for (const textNode of nodesToProcess) {
                const originalText = textNode.textContent || "";
                const trimmed = originalText.trim();
                // Skip already-delimited content
                if (
                  trimmed.startsWith("$") ||
                  trimmed.endsWith("$") ||
                  trimmed.startsWith("\\(") ||
                  trimmed.startsWith("\\[")
                )
                  continue;

                // Wrap the entire text node content in $...$
                // KaTeX handles non-math parts gracefully (renders them as \text{})
                const span = doc.createElement("span");
                span.textContent = `$${originalText}$`;
                textNode.parentNode?.replaceChild(span, textNode);
                wrappedCount++;
              }

              // Step 2: Render all math (including newly wrapped)
              win.renderMathInElement(doc.body, {
                delimiters: [
                  { left: "$$", right: "$$", display: true },
                  { left: "$", right: "$", display: false },
                  { left: "\\(", right: "\\)", display: false },
                  { left: "\\[", right: "\\]", display: true },
                ],
                throwOnError: false,
              });

              if (wrappedCount > 0) {
                console.log(`[KaTeX] Auto-wrapped ${wrappedCount} bare LaTeX nodes`);
              }
            } catch (_e) {
              // Silently ignore fallback errors
            }
          }, delay),
        );

        // Store cleanup refs
        (iframe as unknown as Record<string, unknown>).__fallbackTimers = fallbackTimers;
      }
    }, 100);

    return () => {
      clearTimeout(timer);
      // Clear any pending fallback timers from previous render
      const prev = htmlFrameRef.current as unknown as Record<string, unknown> | null;
      if (prev?.__fallbackTimers) {
        (prev.__fallbackTimers as ReturnType<typeof setTimeout>[]).forEach(clearTimeout);
      }
    };
  }, [html, currentIndex, injectKaTeX]);

  if (!html) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-white dark:bg-slate-800 rounded-b-2xl border border-t-0 border-slate-200 dark:border-slate-700">
        <Loader2 className="w-12 h-12 text-indigo-400 dark:text-indigo-500 animate-spin mb-4" />
        <p className="text-slate-500 dark:text-slate-400">
          {loadingMessage || t("Loading learning content...")}
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-white dark:bg-slate-800 rounded-b-2xl shadow-sm border border-t-0 border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden relative">
      <button
        onClick={onOpenDebugModal}
        className="absolute top-4 right-4 z-10 p-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors shadow-sm"
        title={t("Fix HTML")}
      >
        <Bug className="w-4 h-4 text-slate-600 dark:text-slate-300" />
      </button>

      <iframe
        ref={htmlFrameRef}
        className="w-full flex-1 border-0"
        title={t("Interactive Learning Content")}
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}
