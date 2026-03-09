"use client";

import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import {
  Send,
  Loader2,
  Bot,
  User,
  Image as ImageIcon,
  CheckCircle2,
  Trash2,
  X,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { useTranslation } from "react-i18next";

import { ImageUpload } from "./components/ImageUpload";
import { GeoGebraCanvas } from "./components/GeoGebraCanvas";
import { AnalysisProgress } from "./components/AnalysisProgress";
import {
  useVisionSolver,
  VisionSolverState,
  parseGGBBlocks,
  stripGGBBlocks,
  GGBBlock,
} from "./hooks/useVisionSolver";

/**
 * Answer message content component with real-time GGB block filtering and rendering.
 * This component filters out GGB code blocks from the content and renders them as GeoGebra canvases.
 */
interface AnswerMessageContentProps {
  content: string;
  baseGGBCommands: Array<{
    sequence: number;
    command: string;
    description: string;
  }>;
  messageIdx: number;
  isProcessing: boolean;
  t: (key: string) => string;
}

function AnswerMessageContent({
  content,
  baseGGBCommands,
  messageIdx,
  isProcessing,
  t,
}: AnswerMessageContentProps) {
  // Real-time parsing: filter out GGB blocks and parse them for rendering
  const { strippedContent, ggbBlocks } = useMemo(() => {
    return {
      strippedContent: stripGGBBlocks(content),
      ggbBlocks: parseGGBBlocks(content),
    };
  }, [content]);

  return (
    <>
      {/* Render filtered text content (without GGB code blocks) */}
      {strippedContent && (
        <div className="bg-white dark:bg-slate-800 px-6 py-5 rounded-2xl rounded-tl-none border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="prose prose-slate dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
            >
              {strippedContent}
            </ReactMarkdown>
          </div>
          {/* Show verification badge only when processing is complete */}
          {!isProcessing && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center gap-2 text-xs text-green-600 dark:text-green-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              {t("Verified by DeepTutor Vision Engine")}
            </div>
          )}
        </div>
      )}

      {/* Real-time render GGB blocks as GeoGebra canvases */}
      {ggbBlocks.length > 0 && (
        <div className="space-y-4">
          {ggbBlocks.map((block, blockIdx) => {
            // Merge base commands (from image reconstruction) with solution block commands
            // This ensures points A, B etc. from reconstruction are available
            const mergedCommands = [
              ...baseGGBCommands.map((cmd, i) => ({
                ...cmd,
                sequence: i + 1,
              })),
              ...block.commands.map((cmd, i) => ({
                ...cmd,
                sequence: baseGGBCommands.length + i + 1,
              })),
            ];

            return (
              <div key={block.pageId || blockIdx}>
                <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium flex items-center gap-2">
                  <span className="w-5 h-5 bg-orange-100 dark:bg-orange-900/50 text-orange-600 dark:text-orange-400 rounded flex items-center justify-center text-[10px] font-bold">
                    {blockIdx + 1}
                  </span>
                  {block.title}
                </div>
                <GeoGebraCanvas
                  commands={mergedCommands}
                  pageId={`solution-${messageIdx}-${block.pageId}`}
                  title={block.title}
                  height={280}
                />
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

export default function VisionSolverPage() {
  const { t } = useTranslation();
  const [inputQuestion, setInputQuestion] = useState("");
  const [imageData, setImageData] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const { state, sendMessage, reset } = useVisionSolver();

  // Auto-scroll chat - use scrollTop instead of scrollIntoView to prevent page scroll
  useEffect(() => {
    if (state.messages.length > 0 && chatContainerRef.current) {
      const container = chatContainerRef.current;
      // Smooth scroll to the bottom of the chat container
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [state.messages, state.isProcessing, state.currentStage]);

  const handleImageUpload = useCallback((base64: string) => {
    setImageData(base64);
  }, []);

  const handleRemoveImage = useCallback(() => {
    setImageData(null);
  }, []);

  const handleSubmit = useCallback(() => {
    if (!inputQuestion.trim()) return;
    sendMessage(inputQuestion, imageData || undefined);
    setInputQuestion("");
    setImageData(null);
  }, [inputQuestion, imageData, sendMessage]);

  return (
    <div className="h-screen flex gap-0 animate-fade-in overflow-hidden">
      {/* Left Panel: Chat Interface */}
      <div className="flex-1 flex flex-col bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 overflow-hidden min-h-0">
        {/* Header */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 flex justify-between items-center backdrop-blur-sm shrink-0">
          <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200 font-semibold">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            {t("Vision Solver")}
          </div>
          <div className="flex items-center gap-2">
            {state.messages.length > 0 && (
              <button
                onClick={reset}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                title={t("New Session")}
              >
                <Trash2 className="w-3.5 h-3.5" />
                {t("New")}
              </button>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30 dark:bg-slate-900/30 min-h-0"
        >
          {/* Initial State */}
          {state.messages.length === 0 && !state.isProcessing && (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto">
              <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                <ImageIcon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                {t("Upload a Math Problem Image")}
              </h3>
              <p className="text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
                {t(
                  "Upload an image of a geometry problem and I'll analyze it, recreate the figure in GeoGebra, and help you solve it.",
                )}
              </p>
            </div>
          )}

          {/* Messages */}
          {state.messages.map((msg, idx) => (
            <div
              key={idx}
              className="flex gap-4 w-full transition-opacity duration-300"
            >
              {msg.role === "user" ? (
                <>
                  <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5 text-slate-500 dark:text-slate-400" />
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="bg-slate-100 dark:bg-slate-700 px-5 py-3.5 rounded-2xl rounded-tl-none text-slate-800 dark:text-slate-200">
                      {msg.content}
                    </div>
                    {msg.image && (
                      <div className="max-w-xs">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={msg.image}
                          alt="Uploaded problem"
                          className="rounded-lg border border-slate-200 dark:border-slate-600"
                        />
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/30">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 space-y-4">
                    {/* Analysis Message: GeoGebra Canvas for figure reconstruction */}
                    {msg.messageType === "analysis" &&
                      msg.ggbCommands &&
                      msg.ggbCommands.length > 0 && (
                        <div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
                            {t("Figure Reconstruction")}
                          </div>
                          <GeoGebraCanvas
                            commands={msg.ggbCommands}
                            pageId={`analysis-${idx}`}
                            title={t("Figure Reconstruction")}
                          />
                        </div>
                      )}

                    {/* Legacy support: ggbCommands without messageType */}
                    {!msg.messageType &&
                      msg.ggbCommands &&
                      msg.ggbCommands.length > 0 && (
                        <GeoGebraCanvas
                          commands={msg.ggbCommands}
                          pageId={`msg-${idx}`}
                          title={t("Figure Reconstruction")}
                        />
                      )}

                    {/* Answer Message: Text Content with real-time GGB block filtering */}
                    {msg.messageType === "answer" && msg.content && (
                      <AnswerMessageContent
                        content={msg.content}
                        baseGGBCommands={state.baseGGBCommands}
                        messageIdx={idx}
                        isProcessing={state.isProcessing}
                        t={t}
                      />
                    )}

                    {/* Non-answer messages: render content as-is */}
                    {msg.messageType !== "answer" && msg.content && (
                      <div className="bg-white dark:bg-slate-800 px-6 py-5 rounded-2xl rounded-tl-none border border-slate-200 dark:border-slate-700 shadow-sm">
                        <div className="prose prose-slate dark:prose-invert max-w-none">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}

          {/* Processing State */}
          {state.isProcessing && (
            <div className="flex gap-4 w-full transition-opacity duration-200">
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/30">
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              </div>
              <div className="flex-1">
                <AnalysisProgress state={state} />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700 shrink-0">
          {/* Image Preview */}
          {imageData && (
            <div className="mb-3 flex items-start gap-2">
              <div className="relative inline-block">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imageData}
                  alt="Preview"
                  className="h-20 rounded-lg border border-slate-200 dark:border-slate-600"
                />
                <button
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}

          <div className="w-full relative">
            <div className="flex gap-2">
              <ImageUpload
                onImageUpload={handleImageUpload}
                disabled={state.isProcessing}
              />
              <div className="flex-1 relative">
                <input
                  type="text"
                  className="w-full px-5 py-4 pr-14 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500 text-slate-700 dark:text-slate-200 shadow-inner"
                  placeholder={t("Describe the problem or ask a question...")}
                  value={inputQuestion}
                  onChange={(e) => setInputQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  disabled={state.isProcessing}
                />
                <button
                  onClick={handleSubmit}
                  disabled={state.isProcessing || !inputQuestion.trim()}
                  className="absolute right-2 top-2 bottom-2 aspect-square bg-indigo-600 text-white rounded-lg flex items-center justify-center hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-all shadow-md shadow-indigo-500/20"
                >
                  {state.isProcessing ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-slate-400 dark:text-slate-500 mt-2">
            {t(
              "Upload a geometry problem image for visual analysis and GeoGebra visualization.",
            )}
          </div>
        </div>
      </div>

      {/* Right Panel: Analysis Details */}
      <div className="w-[400px] flex-shrink-0 bg-white dark:bg-slate-800 flex flex-col overflow-hidden border-l border-slate-200 dark:border-slate-700 h-full">
        {/* Header */}
        <div className="px-4 py-3 bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
            <ImageIcon className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
            {t("Analysis Details")}
          </div>
        </div>

        {/* Analysis Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {state.analysisStages.bbox && (
            <div className="space-y-4">
              <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">
                <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  {t("Detected Elements")}
                </h4>
                <div className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
                  <p>
                    {t("Elements")}: {state.analysisStages.bbox.elements_count}
                  </p>
                  {state.analysisStages.bbox.elements?.map((el, i) => (
                    <div
                      key={i}
                      className="pl-2 border-l-2 border-indigo-200 dark:border-indigo-600"
                    >
                      {el.label} ({el.type})
                    </div>
                  ))}
                </div>
              </div>

              {state.analysisStages.analysis && (
                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    {t("Geometric Analysis")}
                  </h4>
                  <div className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
                    <p>
                      {t("Constraints")}:{" "}
                      {state.analysisStages.analysis.constraints_count}
                    </p>
                    <p>
                      {t("Relations")}:{" "}
                      {state.analysisStages.analysis.relations_count}
                    </p>
                    {state.analysisStages.analysis.image_is_reference && (
                      <p className="text-indigo-600 dark:text-indigo-400">
                        {t("Image is reference for problem")}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {state.analysisStages.ggbscript && (
                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    {t("GeoGebra Commands")}
                  </h4>
                  <div className="text-xs text-slate-600 dark:text-slate-400">
                    <p>
                      {t("Commands generated")}:{" "}
                      {state.analysisStages.ggbscript.commands_count}
                    </p>
                  </div>
                </div>
              )}

              {state.analysisStages.reflection && (
                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    {t("Validation")}
                  </h4>
                  <div className="text-xs text-slate-600 dark:text-slate-400">
                    <p>
                      {t("Issues found")}:{" "}
                      {state.analysisStages.reflection.issues_count}
                    </p>
                    <p>
                      {t("Final commands")}:{" "}
                      {state.analysisStages.reflection.commands_count}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {!state.analysisStages.bbox && !state.isProcessing && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-3 py-12">
              <ImageIcon className="w-10 h-10 opacity-20" />
              <p className="text-sm text-center">
                {t("Upload an image to see analysis details")}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
