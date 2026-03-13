"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const MONOSPACE =
  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';

export default function RichCodeBlock({
  raw,
  lang,
  className,
}: {
  raw: string;
  lang: string;
  className?: string;
}) {
  return (
    <div
      className={`md-code-block overflow-hidden rounded-xl border border-[var(--border)] bg-[#1f2937] ${
        className || ""
      }`}
    >
      <div className="border-b border-white/10 px-3 py-2 text-[11px] font-medium uppercase tracking-wider text-[#9ca3af]">
        {lang}
      </div>
      <SyntaxHighlighter
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
