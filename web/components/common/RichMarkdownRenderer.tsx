"use client";

import React, { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "katex/dist/katex.min.css";
import { processMarkdownContent } from "@/lib/latex";
import { normalizeMarkdownForDisplay } from "@/lib/markdown-display";
import type { MarkdownRendererProps } from "./MarkdownRenderer";

const LazyMermaid = dynamic(() => import("@/components/Mermaid"), {
  ssr: false,
  loading: () => (
    <div className="my-4 rounded-xl border border-[var(--border)] bg-[var(--muted)]/50 px-4 py-3 text-sm text-[var(--muted-foreground)]">
      Rendering diagram...
    </div>
  ),
});

const LazyCodeBlock = dynamic(() => import("./RichCodeBlock"), {
  ssr: false,
  loading: () => null,
});

type PluginBundle = {
  remarkMath?: unknown;
  rehypeKatex?: unknown;
  rehypeRaw?: unknown;
};

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

export default function RichMarkdownRenderer({
  content,
  className = "",
  variant = "default",
  enableMath = false,
  enableCode = false,
  enableMermaid = false,
  allowHtml = false,
}: MarkdownRendererProps) {
  const normalizedContent = normalizeMarkdownForDisplay(content);
  const [plugins, setPlugins] = useState<PluginBundle>({});
  const isTrace = variant === "trace";
  const gap = isTrace ? "my-1" : variant === "compact" ? "my-2" : "my-4";
  const cellPad =
    isTrace ? "px-1.5 py-1" : variant === "compact" ? "px-2 py-1.5" : "px-3 py-2";
  const headingSpacing = variant === "compact" ? "mt-4 mb-2" : "mt-6 mb-3";
  const textColor = "text-[var(--foreground)]";

  useEffect(() => {
    let cancelled = false;

    async function loadPlugins() {
      const nextPlugins: PluginBundle = {};

      if (enableMath) {
        const [remarkMathModule, rehypeKatexModule] = await Promise.all([
          import("remark-math"),
          import("rehype-katex"),
        ]);
        nextPlugins.remarkMath = remarkMathModule.default;
        nextPlugins.rehypeKatex = rehypeKatexModule.default;
      }

      if (allowHtml) {
        const rehypeRawModule = await import("rehype-raw");
        nextPlugins.rehypeRaw = rehypeRawModule.default;
      }

      if (!cancelled) {
        setPlugins(nextPlugins);
      }
    }

    void loadPlugins();

    return () => {
      cancelled = true;
    };
  }, [allowHtml, enableMath]);

  const processedContent = useMemo(() => {
    return enableMath || enableMermaid ? processMarkdownContent(normalizedContent) : normalizedContent;
  }, [enableMath, enableMermaid, normalizedContent]);

  const traceComponents: Record<string, React.ComponentType<any>> = {
    p: ({ node, ...props }: any) => <p className="mb-1.5 last:mb-0" {...props} />,
    h1: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h2: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h3: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h4: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h5: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    h6: ({ node, children }: any) => <p className="mb-1.5 font-semibold">{children}</p>,
    strong: ({ node, children }: any) => (
      <strong className="font-semibold text-[var(--foreground)]/92">{children}</strong>
    ),
    em: ({ node, children }: any) => <em className="italic">{children}</em>,
    a: ({ node, children }: any) => (
      <span className="underline underline-offset-2">{children}</span>
    ),
    blockquote: ({ node, children }: any) => (
      <div className="border-l border-current/20 pl-3 opacity-80">{children}</div>
    ),
    pre: ({ children }: any) => <>{children}</>,
    code: ({ node, children }: any) => (
      <code className="rounded bg-[var(--muted)] px-1 py-0.5 font-mono text-[0.95em] text-[var(--foreground)]/90">
        {String(children).replace(/\n$/, "")}
      </code>
    ),
    img: () => null,
    hr: () => <div className="my-1 h-px bg-current opacity-10" />,
    ul: ({ node, ...props }: any) => <ul className="my-1 ml-4 list-disc" {...props} />,
    ol: ({ node, ...props }: any) => <ol className="my-1 ml-4 list-decimal" {...props} />,
    li: ({ node, ...props }: any) => <li className="my-0.5 pl-0" {...props} />,
    table: ({ node, children, ...props }: any) =>
      hasRenderableChildren(children) ? (
        <div className="my-1 overflow-x-auto rounded border border-[var(--border)]/50">
          <table className="min-w-full text-[inherit]" {...props} />
        </div>
      ) : null,
    thead: ({ node, ...props }: any) => <thead className="bg-[var(--muted)]/50" {...props} />,
    th: ({ node, ...props }: any) => (
      <th
        className="border-b border-[var(--border)]/50 px-1.5 py-0.5 text-left font-medium"
        {...props}
      />
    ),
    tbody: ({ node, ...props }: any) => <tbody {...props} />,
    td: ({ node, ...props }: any) => (
      <td className="border-b border-[var(--border)]/30 px-1.5 py-0.5" {...props} />
    ),
    tr: ({ node, ...props }: any) => <tr {...props} />,
    input: ({ node, type, ...props }: any) =>
      type === "checkbox" ? (
        <input type="checkbox" readOnly className="mr-1 align-middle" {...props} />
      ) : null,
    details: ({ node, children }: any) =>
      hasRenderableChildren(children) ? <div>{children}</div> : null,
    summary: ({ node, children }: any) =>
      hasRenderableChildren(children) ? <span>{children}</span> : null,
  };

  const headingComponents = {
    h1: ({ node, children, className: headingClassName, ...props }: any) => (
      <h1
        id={headingId(children)}
        className={`scroll-mt-20 text-3xl font-bold tracking-tight ${textColor} ${headingSpacing} ${
          headingClassName || ""
        }`}
        {...props}
      >
        {children}
      </h1>
    ),
    h2: ({ node, children, className: headingClassName, ...props }: any) => (
      <h2
        id={headingId(children)}
        className={`scroll-mt-20 text-2xl font-semibold tracking-tight ${textColor} ${headingSpacing} ${
          headingClassName || ""
        }`}
        {...props}
      >
        {children}
      </h2>
    ),
    h3: ({ node, children, className: headingClassName, ...props }: any) => (
      <h3
        id={headingId(children)}
        className={`scroll-mt-20 text-xl font-semibold tracking-tight ${textColor} ${headingSpacing} ${
          headingClassName || ""
        }`}
        {...props}
      >
        {children}
      </h3>
    ),
    h4: ({ node, children, className: headingClassName, ...props }: any) => (
      <h4
        id={headingId(children)}
        className={`scroll-mt-20 text-lg font-semibold ${textColor} ${
          variant === "compact" ? "mt-3 mb-1.5" : "mt-5 mb-2"
        } ${headingClassName || ""}`}
        {...props}
      >
        {children}
      </h4>
    ),
    h5: ({ node, children, className: headingClassName, ...props }: any) => (
      <h5
        id={headingId(children)}
        className={`scroll-mt-20 text-base font-semibold ${textColor} ${
          variant === "compact" ? "mt-3 mb-1.5" : "mt-4 mb-2"
        } ${headingClassName || ""}`}
        {...props}
      >
        {children}
      </h5>
    ),
    h6: ({ node, children, className: headingClassName, ...props }: any) => (
      <h6
        id={headingId(children)}
        className={`scroll-mt-20 text-sm font-semibold uppercase tracking-wide text-[var(--muted-foreground)] ${
          variant === "compact" ? "mt-3 mb-1.5" : "mt-4 mb-2"
        } ${headingClassName || ""}`}
        {...props}
      >
        {children}
      </h6>
    ),
  };

  const normalComponents: Record<string, React.ComponentType<any>> = {
    ...headingComponents,
    table: ({ node, children, ...props }: any) =>
      hasRenderableChildren(children) ? (
        <div className={`overflow-x-auto rounded-lg border border-[var(--border)] shadow-sm ${gap}`}>
          <table className="min-w-full divide-y divide-[var(--border)] text-sm" {...props} />
        </div>
      ) : null,
    thead: ({ node, ...props }: any) => <thead className="bg-[var(--muted)]" {...props} />,
    th: ({ node, ...props }: any) => (
      <th
        className={`whitespace-nowrap border-b border-[var(--border)] text-left font-semibold text-[var(--foreground)] ${cellPad}`}
        {...props}
      />
    ),
    tbody: ({ node, ...props }: any) => (
      <tbody className="divide-y divide-[var(--border)] bg-[var(--card)]" {...props} />
    ),
    td: ({ node, ...props }: any) => (
      <td
        className={`border-b border-[var(--border)] text-[var(--muted-foreground)] ${cellPad}`}
        {...props}
      />
    ),
    tr: ({ node, ...props }: any) => (
      <tr className="transition-colors hover:bg-[var(--muted)]/60" {...props} />
    ),
    pre: ({ children }: any) => <>{children}</>,
    code: ({ node, className: blockClassName, children, ...props }: any) => {
      const raw = String(children).replace(/\n$/, "");
      const langMatch = /language-([A-Za-z0-9_+#.-]+)/.exec(blockClassName || "");
      const lang = langMatch?.[1]?.toLowerCase() || "";

      if (lang === "mermaid" && enableMermaid) {
        return <LazyMermaid chart={raw} className={gap} />;
      }

      if (lang && enableCode) {
        return <LazyCodeBlock raw={raw} lang={lang} className={gap} />;
      }

      if (raw.includes("\n")) {
        return (
          <div
            className={`md-code-block ${gap} overflow-hidden rounded-xl border border-[var(--border)] bg-[#1f2937]`}
          >
            <pre className="overflow-x-auto p-4 text-sm leading-relaxed text-[#d1d5db]">
              <code {...props}>{raw}</code>
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
    a: ({ node, href, children, ...props }: any) => {
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
            const target = document.getElementById(targetId);
            target?.scrollIntoView({ block: "start", behavior: "smooth" });
          }}
          className="text-[var(--primary)] underline decoration-[var(--primary)]/40 underline-offset-2 transition-colors hover:decoration-[var(--primary)]"
          {...props}
        >
          {children}
        </a>
      );
    },
    img: ({ node, src, alt, ...props }: any) => (
      <img
        src={src}
        alt={alt || ""}
        loading="lazy"
        className={`${gap} inline-block max-w-full rounded-lg border border-[var(--border)]`}
        {...props}
      />
    ),
    blockquote: ({ node, ...props }: any) => (
      <blockquote
        className={`${gap} border-l-[3px] border-[var(--primary)] pl-4 italic text-[var(--muted-foreground)] [&>p]:mb-1`}
        {...props}
      />
    ),
    hr: ({ node, ...props }: any) => (
      <hr className={`${gap} h-px border-none bg-[var(--border)]`} {...props} />
    ),
    input: ({ node, type, checked, ...props }: any) =>
      type === "checkbox" ? (
        <input
          type="checkbox"
          checked={checked}
          readOnly
          className="mr-2 h-4 w-4 rounded border-[var(--border)] align-middle accent-[var(--primary)]"
          {...props}
        />
      ) : null,
    details: ({ node, children, ...props }: any) =>
      hasRenderableChildren(children) ? (
        <details
          className={`${gap} rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2`}
          {...props}
        >
          {children}
        </details>
      ) : null,
    summary: ({ node, children, ...props }: any) =>
      hasRenderableChildren(children) ? (
        <summary
          className="cursor-pointer select-none font-medium text-[var(--foreground)]"
          {...props}
        >
          {children}
        </summary>
      ) : null,
  };

  const components = isTrace ? traceComponents : normalComponents;
  const rootClasses = isTrace
    ? "md-renderer max-w-none text-[12px] leading-[1.7] text-[var(--muted-foreground)]/82"
    : variant === "prose"
      ? "md-renderer prose max-w-none"
      : "md-renderer prose prose-sm max-w-none";

  const remarkPlugins: Array<any> = [remarkGfm];
  if (plugins.remarkMath) {
    remarkPlugins.push(plugins.remarkMath as never);
  }

  const rehypePlugins: Array<any> = [];
  if (allowHtml && plugins.rehypeRaw) {
    rehypePlugins.push(plugins.rehypeRaw as never);
  }
  if (enableMath && plugins.rehypeKatex) {
    rehypePlugins.push(plugins.rehypeKatex as never);
  }

  return (
    <div className={`${rootClasses} ${className}`}>
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        rehypePlugins={rehypePlugins}
        components={components}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}
