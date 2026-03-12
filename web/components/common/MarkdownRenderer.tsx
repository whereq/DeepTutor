"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import Mermaid from "@/components/Mermaid";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import "katex/dist/katex.min.css";
import { processMarkdownContent } from "@/lib/latex";
import { normalizeMarkdownForDisplay } from "@/lib/markdown-display";

interface MarkdownRendererProps {
  content: string;
  className?: string;
  variant?: "default" | "compact" | "prose" | "trace";
}

const MONOSPACE =
  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';

function extractText(children: React.ReactNode): string {
  return React.Children.toArray(children)
    .map((child) => {
      if (typeof child === "string" || typeof child === "number") {
        return String(child);
      }

      if (React.isValidElement<{ children?: React.ReactNode }>(child)) {
        return extractText(child.props.children);
      }

      return "";
    })
    .join("");
}

function headingId(children: React.ReactNode): string | undefined {
  const text = extractText(children)
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
  return text || undefined;
}

function hasRenderableChildren(children: React.ReactNode): boolean {
  return extractText(children).replace(/[\s\u200B-\u200D\uFEFF]/g, "").length > 0;
}

export default function MarkdownRenderer({
  content,
  className = "",
  variant = "default",
}: MarkdownRendererProps) {
  const normalizedContent = normalizeMarkdownForDisplay(content);
  const isTrace = variant === "trace";
  const gap = isTrace ? "my-1" : variant === "compact" ? "my-2" : "my-4";
  const cellPad = isTrace ? "px-1.5 py-1" : variant === "compact" ? "px-2 py-1.5" : "px-3 py-2";
  const headingSpacing = variant === "compact" ? "mt-4 mb-2" : "mt-6 mb-3";
  const textColor = "text-[var(--foreground)]";

  /* ── Trace-mode components: almost plain text, only tables + math survive ── */
  const traceComponents: Record<string, React.ComponentType<any>> = {
    p:          ({ node, ...p }: any) => <p className="mb-1.5 last:mb-0" {...p} />,
    h1:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h2:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h3:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h4:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h5:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h6:         ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    strong:     ({ node, children }: any) => <strong className="font-semibold text-[var(--foreground)]/92">{children}</strong>,
    em:         ({ node, children }: any) => <em className="italic">{children}</em>,
    a:          ({ node, children }: any) => <span className="underline underline-offset-2">{children}</span>,
    blockquote: ({ node, children }: any) => <div className="border-l border-current/20 pl-3 opacity-80">{children}</div>,
    pre:        ({ children }: any) => <>{children}</>,
    code:       ({ node, children }: any) => (
      <code className="rounded bg-[var(--muted)] px-1 py-0.5 font-mono text-[0.95em] text-[var(--foreground)]/90">
        {String(children).replace(/\n$/, "")}
      </code>
    ),
    img:        () => null,
    hr:         () => <div className="my-1 h-px bg-current opacity-10" />,
    ul:         ({ node, ...p }: any) => <ul className="my-1 ml-4 list-disc" {...p} />,
    ol:         ({ node, ...p }: any) => <ol className="my-1 ml-4 list-decimal" {...p} />,
    li:         ({ node, ...p }: any) => <li className="my-0.5 pl-0" {...p} />,
    table:      ({ node, children, ...p }: any) => hasRenderableChildren(children) ? (
      <div className="my-1 overflow-x-auto rounded border border-[var(--border)]/50">
        <table className="min-w-full text-[inherit]" {...p} />
      </div>
    ) : null,
    thead:      ({ node, ...p }: any) => <thead className="bg-[var(--muted)]/50" {...p} />,
    th:         ({ node, ...p }: any) => <th className="px-1.5 py-0.5 text-left font-medium border-b border-[var(--border)]/50" {...p} />,
    tbody:      ({ node, ...p }: any) => <tbody {...p} />,
    td:         ({ node, ...p }: any) => <td className="px-1.5 py-0.5 border-b border-[var(--border)]/30" {...p} />,
    tr:         ({ node, ...p }: any) => <tr {...p} />,
    input:      ({ node, type, ...p }: any) => type === "checkbox" ? <input type="checkbox" readOnly className="mr-1 align-middle" {...p} /> : null,
    details:    ({ node, children }: any) => hasRenderableChildren(children) ? <div>{children}</div> : null,
    summary:    ({ node, children }: any) => hasRenderableChildren(children) ? <span>{children}</span> : null,
  };

  const headingComponents = {
    h1: ({ node, children, className, ...p }: any) => (
      <h1
        id={headingId(children)}
        className={`scroll-mt-20 text-3xl font-bold tracking-tight ${textColor} ${headingSpacing} ${className || ""}`}
        {...p}
      >
        {children}
      </h1>
    ),
    h2: ({ node, children, className, ...p }: any) => (
      <h2
        id={headingId(children)}
        className={`scroll-mt-20 text-2xl font-semibold tracking-tight ${textColor} ${headingSpacing} ${className || ""}`}
        {...p}
      >
        {children}
      </h2>
    ),
    h3: ({ node, children, className, ...p }: any) => (
      <h3
        id={headingId(children)}
        className={`scroll-mt-20 text-xl font-semibold tracking-tight ${textColor} ${headingSpacing} ${className || ""}`}
        {...p}
      >
        {children}
      </h3>
    ),
    h4: ({ node, children, className, ...p }: any) => (
      <h4
        id={headingId(children)}
        className={`scroll-mt-20 text-lg font-semibold ${textColor} ${variant === "compact" ? "mt-3 mb-1.5" : "mt-5 mb-2"} ${className || ""}`}
        {...p}
      >
        {children}
      </h4>
    ),
    h5: ({ node, children, className, ...p }: any) => (
      <h5
        id={headingId(children)}
        className={`scroll-mt-20 text-base font-semibold ${textColor} ${variant === "compact" ? "mt-3 mb-1.5" : "mt-4 mb-2"} ${className || ""}`}
        {...p}
      >
        {children}
      </h5>
    ),
    h6: ({ node, children, className, ...p }: any) => (
      <h6
        id={headingId(children)}
        className={`scroll-mt-20 text-sm font-semibold uppercase tracking-wide text-[var(--muted-foreground)] ${variant === "compact" ? "mt-3 mb-1.5" : "mt-4 mb-2"} ${className || ""}`}
        {...p}
      >
        {children}
      </h6>
    ),
  };

  /* ── Normal-mode components ── */
  const normalComponents: Record<string, React.ComponentType<any>> = {
    ...headingComponents,

    table: ({ node, children, ...p }: any) => hasRenderableChildren(children) ? (
      <div className={`overflow-x-auto rounded-lg border border-[var(--border)] shadow-sm ${gap}`}>
        <table className="min-w-full divide-y divide-[var(--border)] text-sm" {...p} />
      </div>
    ) : null,
    thead: ({ node, ...p }: any) => <thead className="bg-[var(--muted)]" {...p} />,
    th: ({ node, ...p }: any) => (
      <th className={`whitespace-nowrap border-b border-[var(--border)] text-left font-semibold text-[var(--foreground)] ${cellPad}`} {...p} />
    ),
    tbody: ({ node, ...p }: any) => (
      <tbody className="divide-y divide-[var(--border)] bg-[var(--card)]" {...p} />
    ),
    td: ({ node, ...p }: any) => (
      <td className={`border-b border-[var(--border)] text-[var(--muted-foreground)] ${cellPad}`} {...p} />
    ),
    tr: ({ node, ...p }: any) => (
      <tr className="transition-colors hover:bg-[var(--muted)]/60" {...p} />
    ),

    pre: ({ children }: any) => <>{children}</>,

    code: ({ node, className: cls, children, ...props }: any) => {
      const raw = String(children).replace(/\n$/, "");
      const langMatch = /language-([A-Za-z0-9_+#.-]+)/.exec(cls || "");
      const lang = langMatch?.[1]?.toLowerCase() || "";

      if (lang) {
        if (lang === "mermaid") return <Mermaid chart={raw} className={gap} />;

        return (
          <div className={`md-code-block ${gap} overflow-hidden rounded-xl border border-[var(--border)] bg-[#1f2937]`}>
            <div className="border-b border-white/10 px-3 py-2 text-[11px] font-medium uppercase tracking-wider text-[#9ca3af]">
              {lang}
            </div>
            <SyntaxHighlighter
              {...props}
              language={lang}
              style={oneDark}
              PreTag="pre"
              customStyle={{
                margin: 0,
                borderRadius: 0,
                background: "#1f2937",
                padding: "1rem",
                fontSize: "0.875rem",
                lineHeight: "1.7",
              }}
              codeTagProps={{
                className: "md-code-block__code",
                style: { fontFamily: MONOSPACE },
              }}
              wrapLongLines={false}
            >
              {raw}
            </SyntaxHighlighter>
          </div>
        );
      }

      if (raw.includes("\n")) {
        return (
          <div className={`md-code-block ${gap} overflow-hidden rounded-xl border border-[var(--border)] bg-[#1f2937]`}>
            <pre
              className="md-code-block__pre overflow-x-auto p-4 text-sm leading-relaxed"
              style={{ margin: 0, background: "#1f2937", color: "#d1d5db", fontFamily: MONOSPACE }}
            >
              <code className="md-code-block__code">{raw}</code>
            </pre>
          </div>
        );
      }

      return (
        <code
          className="md-inline-code rounded bg-[var(--muted)] px-1.5 py-0.5 font-mono text-[0.875em] text-[var(--foreground)]"
          {...props}
        >
          {children}
        </code>
      );
    },

    a: ({ node, href, children, ...p }: any) => {
      const isHashLink = href?.startsWith("#");
      const external = href?.startsWith("http://") || href?.startsWith("https://");
      return (
        <a
          href={href}
          {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
          onClick={(event) => {
            if (!isHashLink || !href) return;

            event.preventDefault();
            const targetId = decodeURIComponent(href.slice(1));
            if (!targetId) return;

            const target = document.getElementById(targetId);
            target?.scrollIntoView({ block: "start", behavior: "smooth" });
          }}
          className="text-[var(--primary)] underline underline-offset-2 decoration-[var(--primary)]/40 hover:decoration-[var(--primary)] transition-colors"
          {...p}
        >
          {children}
        </a>
      );
    },

    img: ({ node, src, alt, ...p }: any) => (
      <img
        src={src}
        alt={alt || ""}
        loading="lazy"
        className={`${gap} inline-block max-w-full rounded-lg border border-[var(--border)]`}
        {...p}
      />
    ),

    blockquote: ({ node, ...p }: any) => (
      <blockquote
        className={`${gap} border-l-[3px] border-[var(--primary)] pl-4 italic text-[var(--muted-foreground)] [&>p]:mb-1`}
        {...p}
      />
    ),

    hr: ({ node, ...p }: any) => (
      <hr className={`${gap} border-none h-px bg-[var(--border)]`} {...p} />
    ),

    input: ({ node, type, checked, ...p }: any) => {
      if (type === "checkbox") {
        return (
          <input
            type="checkbox"
            checked={checked}
            readOnly
            className="mr-2 h-4 w-4 rounded border-[var(--border)] accent-[var(--primary)] align-middle"
            {...p}
          />
        );
      }
      return null;
    },

    details: ({ node, children, ...p }: any) => {
      if (!hasRenderableChildren(children)) return null;
      return (
        <details
          className={`${gap} rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2`}
          {...p}
        >
          {children}
        </details>
      );
    },
    summary: ({ node, children, ...p }: any) => {
      if (!hasRenderableChildren(children)) return null;
      return (
        <summary
          className="cursor-pointer font-medium text-[var(--foreground)] select-none"
          {...p}
        >
          {children}
        </summary>
      );
    },
  };

  const components = isTrace ? traceComponents : normalComponents;

  const rootClasses = isTrace
    ? "md-renderer max-w-none text-[12px] leading-[1.7] text-[var(--muted-foreground)]/82"
    : variant === "prose"
      ? "md-renderer prose max-w-none"
      : "md-renderer prose prose-sm max-w-none";

  return (
    <div className={`${rootClasses} ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeRaw, rehypeKatex]}
        components={components}
      >
        {processMarkdownContent(normalizedContent)}
      </ReactMarkdown>
    </div>
  );
}
