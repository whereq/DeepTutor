"use client";

import dynamic from "next/dynamic";
import SimpleMarkdownRenderer from "./SimpleMarkdownRenderer";

const RichMarkdownRenderer = dynamic(() => import("./RichMarkdownRenderer"), {
  ssr: false,
});

export interface MarkdownRendererProps {
  content: string;
  className?: string;
  variant?: "default" | "compact" | "prose" | "trace";
  enableMath?: boolean;
  enableCode?: boolean;
  enableMermaid?: boolean;
  allowHtml?: boolean;
}

function detectMathContent(content: string): boolean {
  if (/(^|[^\\])\$\$[\s\S]+?\$\$/.test(content)) return true;
  if (/\\\(|\\\[/.test(content)) return true;
  // Single-dollar inline math containing LaTeX commands (\cmd) or math operators ({}_^)
  if (/(?:^|[^$\\])\$(?!\$|\s)(?:[^$\n]*(?:\\[a-zA-Z]+|[{}_^]))[^$\n]*\$(?!\$)/m.test(content))
    return true;
  return false;
}

function detectCodeContent(content: string): boolean {
  return /```[A-Za-z0-9_+#.-]+/.test(content);
}

function detectMermaidContent(content: string): boolean {
  return /```mermaid/i.test(content);
}

function detectHtmlContent(content: string): boolean {
  return /<\/?[A-Za-z][\w:-]*(\s|>)/.test(content);
}

export default function MarkdownRenderer({
  content,
  className = "",
  variant = "default",
  enableMath,
  enableCode,
  enableMermaid,
  allowHtml,
}: MarkdownRendererProps) {
  const resolvedEnableMath = enableMath ?? detectMathContent(content);
  const resolvedEnableCode = enableCode ?? detectCodeContent(content);
  const resolvedEnableMermaid = enableMermaid ?? detectMermaidContent(content);
  const resolvedAllowHtml = allowHtml ?? detectHtmlContent(content);
  const shouldUseRich =
    variant !== "trace" &&
    (resolvedEnableMath || resolvedEnableCode || resolvedEnableMermaid || resolvedAllowHtml);

  if (!shouldUseRich) {
    return <SimpleMarkdownRenderer content={content} className={className} variant={variant} />;
  }

  return (
    <RichMarkdownRenderer
      content={content}
      className={className}
      variant={variant}
      enableMath={resolvedEnableMath}
      enableCode={resolvedEnableCode}
      enableMermaid={resolvedEnableMermaid}
      allowHtml={resolvedAllowHtml}
    />
  );
}
