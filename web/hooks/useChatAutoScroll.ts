"use client";

import { useCallback, useEffect, useRef } from "react";

interface AutoScrollOptions {
  hasMessages: boolean;
  isStreaming: boolean;
  composerHeight: number;
  messageCount: number;
  lastMessageContent?: string;
  lastEventCount?: number;
}

export function useChatAutoScroll({
  hasMessages,
  isStreaming,
  composerHeight,
  messageCount,
  lastMessageContent,
  lastEventCount,
}: AutoScrollOptions) {
  const containerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);

  const scrollToBottom = useCallback((behavior: ScrollBehavior) => {
    const container = containerRef.current;
    const anchor = endRef.current;
    if (!container) return;
    if (anchor) {
      anchor.scrollIntoView({ block: "end", behavior });
      return;
    }
    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    });
  }, []);

  useEffect(() => {
    if (!shouldAutoScrollRef.current) return;
    let raf1 = 0;
    let raf2 = 0;
    raf1 = window.requestAnimationFrame(() => {
      scrollToBottom(isStreaming ? "auto" : "smooth");
      if (isStreaming) {
        raf2 = window.requestAnimationFrame(() => {
          scrollToBottom("auto");
        });
      }
    });
    return () => {
      window.cancelAnimationFrame(raf1);
      window.cancelAnimationFrame(raf2);
    };
  }, [isStreaming, lastEventCount, lastMessageContent, messageCount, scrollToBottom]);

  useEffect(() => {
    if (!hasMessages || !shouldAutoScrollRef.current) return;
    const raf = window.requestAnimationFrame(() => {
      scrollToBottom("auto");
    });
    return () => window.cancelAnimationFrame(raf);
  }, [composerHeight, hasMessages, scrollToBottom]);

  const handleScroll = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;
    shouldAutoScrollRef.current = distanceFromBottom < 80;
  }, []);

  return {
    containerRef,
    endRef,
    shouldAutoScrollRef,
    scrollToBottom,
    handleScroll,
  };
}
