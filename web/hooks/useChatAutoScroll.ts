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

const THROTTLE_MS = 80;

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
  const lastScrollTimeRef = useRef(0);
  const pendingRafRef = useRef(0);

  const scrollToBottom = useCallback((behavior: ScrollBehavior) => {
    const container = containerRef.current;
    if (!container) return;
    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    });
  }, []);

  useEffect(() => {
    if (!shouldAutoScrollRef.current) return;

    const now = performance.now();
    const elapsed = now - lastScrollTimeRef.current;

    if (isStreaming && elapsed < THROTTLE_MS) {
      if (pendingRafRef.current) return;
      pendingRafRef.current = window.setTimeout(() => {
        pendingRafRef.current = 0;
        if (shouldAutoScrollRef.current) {
          scrollToBottom("instant");
          lastScrollTimeRef.current = performance.now();
        }
      }, THROTTLE_MS - elapsed);
      return;
    }

    const raf = window.requestAnimationFrame(() => {
      scrollToBottom(isStreaming ? "instant" : "smooth");
      lastScrollTimeRef.current = performance.now();
    });

    return () => {
      window.cancelAnimationFrame(raf);
      if (pendingRafRef.current) {
        clearTimeout(pendingRafRef.current);
        pendingRafRef.current = 0;
      }
    };
  }, [isStreaming, lastEventCount, lastMessageContent, messageCount, scrollToBottom]);

  useEffect(() => {
    if (!hasMessages || !shouldAutoScrollRef.current) return;
    const raf = window.requestAnimationFrame(() => {
      scrollToBottom("instant");
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
