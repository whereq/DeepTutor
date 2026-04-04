"use client";

import { useRef, useEffect, useState } from "react";
import { MessageSquare, Send, Loader2 } from "lucide-react";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import "katex/dist/katex.min.css";
import { useTranslation } from "react-i18next";
import { ChatMessage } from "../types";

interface ChatPanelProps {
  messages: ChatMessage[];
  isLearning: boolean;
  currentKnowledgeTitle?: string;
  currentKnowledgeIndex?: number;
  onSendMessage: (message: string) => void;
}

export default function ChatPanel({
  messages,
  isLearning,
  currentKnowledgeTitle,
  currentKnowledgeIndex,
  onSendMessage,
}: ChatPanelProps) {
  const { t } = useTranslation();
  const [inputMessage, setInputMessage] = useState("");
  const [sendingMessage, setSendingMessage] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || sendingMessage) return;

    setSendingMessage(true);
    const message = inputMessage;
    setInputMessage("");

    try {
      await onSendMessage(message);
    } finally {
      setSendingMessage(false);
    }
  };

  return (
    <div className="flex-1 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-2">
        <MessageSquare className="w-4 h-4" />
        {t("Learning Assistant")}
      </div>

      {isLearning && currentKnowledgeTitle && (
        <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-700 bg-indigo-50/60 text-xs text-indigo-700 dark:bg-indigo-950/30 dark:text-indigo-200">
          {t("Current page")}: {currentKnowledgeIndex !== undefined ? currentKnowledgeIndex + 1 : ""}
          {currentKnowledgeIndex !== undefined ? ". " : ""}
          {currentKnowledgeTitle}
        </div>
      )}

      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30 dark:bg-slate-800/30"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-500/20"
                  : msg.role === "system" && msg.content.includes("⏳")
                    ? "bg-amber-50 border border-amber-200 text-amber-900 rounded-tl-none"
                    : msg.role === "system"
                      ? "bg-blue-50 border border-blue-200 text-blue-900 rounded-tl-none"
                      : "bg-white border border-slate-200 text-slate-700 rounded-tl-none shadow-sm"
              }`}
            >
              {typeof msg.knowledge_index === "number" && (
                <div className="mb-2 text-[11px] font-semibold opacity-70">
                  {t("Knowledge Point")} {msg.knowledge_index + 1}
                </div>
              )}
              {msg.role === "system" || msg.role === "assistant" ? (
                <MarkdownRenderer
                  content={msg.content}
                  variant="compact"
                  className="prose-slate text-sm"
                />
              ) : (
                <p>{msg.content}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {isLearning && (
        <div className="p-3 bg-white dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700">
          <div className="relative flex items-center gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !e.shiftKey && handleSendMessage()
              }
              placeholder={t("Have any questions? Feel free to ask...")}
              disabled={sendingMessage}
              className="flex-1 pl-4 pr-10 py-2.5 bg-slate-100 dark:bg-slate-700 border-transparent focus:bg-white dark:focus:bg-slate-600 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 rounded-xl text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || sendingMessage}
              className="p-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20"
            >
              {sendingMessage ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
