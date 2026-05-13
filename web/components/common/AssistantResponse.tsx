"use client";

import { Fragment, useMemo } from "react";

import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import ModelThinkingCard from "@/components/common/ModelThinkingCard";
import { hasVisibleMarkdownContent } from "@/lib/markdown-display";
import { parseModelThinkingSegments } from "@/lib/think-segments";

interface AssistantResponseProps {
  content: string;
  className?: string;
}

export default function AssistantResponse({
  content,
  className = "text-[14px] leading-[1.75]",
}: AssistantResponseProps) {
  const segments = useMemo(
    () => parseModelThinkingSegments(content),
    [content],
  );

  // Decide whether the message has anything worth rendering. We consider both
  // ordinary markdown segments and model-thinking blocks: a turn that only
  // ever produced a <think> scratchpad should still render the collapsed card
  // instead of dropping the assistant bubble entirely.
  const hasRenderableSegment = useMemo(() => {
    return segments.some((segment) => {
      if (segment.kind === "think") return segment.content.trim().length > 0;
      return hasVisibleMarkdownContent(segment.content);
    });
  }, [segments]);

  if (!hasRenderableSegment) return null;

  // role="article" lets screen-reader users locate each assistant turn as a
  // structured landmark. aria-live="polite" + aria-atomic="false" announces
  // streamed-in content as the user pauses, without re-reading the whole
  // bubble each token. Together this is the minimal pattern that turns a
  // silent stream into an audible one.
  return (
    <div
      role="article"
      aria-live="polite"
      aria-atomic="false"
      className={className}
    >
      {segments.map((segment, index) => {
        if (segment.kind === "think") {
          return (
            <ModelThinkingCard
              key={`think-${index}`}
              content={segment.content}
              closed={segment.closed}
            />
          );
        }

        if (!hasVisibleMarkdownContent(segment.content)) {
          return <Fragment key={`text-${index}`} />;
        }

        return (
          <MarkdownRenderer
            key={`text-${index}`}
            content={segment.content}
            variant="prose"
            className="text-[var(--foreground)]"
          />
        );
      })}
    </div>
  );
}
