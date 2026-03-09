"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { wsUrl } from "@/lib/api";

export interface GGBCommand {
  sequence: number;
  command: string;
  description: string;
}

/** GeoGebra block parsed from content */
export interface GGBBlock {
  pageId: string;
  title: string;
  content: string;
  commands: GGBCommand[];
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  image?: string;
  /** GGB commands for image reconstruction (analysis message) */
  ggbCommands?: GGBCommand[];
  /** GGB blocks parsed from answer content (for solution visualization) */
  ggbBlocks?: GGBBlock[];
  /** Message type: analysis or answer */
  messageType?: "analysis" | "answer";
}

export interface AnalysisStages {
  bbox?: {
    elements_count: number;
    elements?: Array<{ type: string; label: string }>;
  };
  analysis?: {
    constraints_count: number;
    relations_count: number;
    image_is_reference: boolean;
    constraints?: string[];
  };
  ggbscript?: {
    commands_count: number;
    commands?: Array<{ command: string; description: string }>;
  };
  reflection?: {
    issues_count: number;
    commands_count: number;
    final_commands?: GGBCommand[];
  };
}

export interface VisionSolverState {
  messages: Message[];
  isProcessing: boolean;
  currentStage: string | null;
  sessionId: string | null;
  analysisStages: AnalysisStages;
  error: string | null;
  /** Base GGB commands from image reconstruction (used as environment for solution blocks) */
  baseGGBCommands: GGBCommand[];
}

const initialState: VisionSolverState = {
  messages: [],
  isProcessing: false,
  currentStage: null,
  sessionId: null,
  analysisStages: {},
  error: null,
  baseGGBCommands: [],
};

export function useVisionSolver() {
  const [state, setState] = useState<VisionSolverState>(initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const pendingMessageRef = useRef<{ question: string; image?: string } | null>(
    null,
  );

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Handle WebSocket messages - defined before sendMessage to avoid access before declaration
  const handleWebSocketMessage = useCallback((data: any) => {
    const { type, data: eventData } = data;

    switch (type) {
      case "session":
        setState((prev) => ({
          ...prev,
          sessionId: eventData?.session_id || data.session_id,
        }));
        break;

      case "analysis_start":
        setState((prev) => ({
          ...prev,
          currentStage: "bbox",
        }));
        break;

      case "bbox_complete":
        setState((prev) => ({
          ...prev,
          currentStage: "analysis",
          analysisStages: {
            ...prev.analysisStages,
            bbox: eventData,
          },
        }));
        break;

      case "analysis_complete":
        setState((prev) => ({
          ...prev,
          currentStage: "ggbscript",
          analysisStages: {
            ...prev.analysisStages,
            analysis: eventData,
          },
        }));
        break;

      case "ggbscript_complete":
        setState((prev) => ({
          ...prev,
          currentStage: "reflection",
          analysisStages: {
            ...prev.analysisStages,
            ggbscript: eventData,
          },
        }));
        break;

      case "reflection_complete":
        setState((prev) => ({
          ...prev,
          currentStage: "complete",
          analysisStages: {
            ...prev.analysisStages,
            reflection: eventData,
          },
        }));
        break;

      case "analysis_message_complete":
        // Add assistant message with GGB commands (for image reconstruction)
        // Also save these commands as base environment for solution blocks
        if (eventData?.ggb_block) {
          const ggbCommands = parseGGBCommands(eventData.ggb_block.content);
          setState((prev) => ({
            ...prev,
            // Save base commands for solution blocks to inherit
            baseGGBCommands: ggbCommands,
            messages: [
              ...prev.messages,
              {
                role: "assistant",
                content: "",
                ggbCommands,
                messageType: "analysis",
              },
            ],
          }));
        }
        break;

      case "answer_start":
        // Start the tutor response phase - create a new answer message
        setState((prev) => {
          const messages = [...prev.messages];
          // Always create a new answer message separate from analysis message
          messages.push({
            role: "assistant",
            content: "",
            messageType: "answer",
            ggbBlocks: [],
          });

          return {
            ...prev,
            currentStage: "answering",
            messages,
          };
        });
        break;

      case "text":
        // Append text content to last assistant message
        setState((prev) => {
          const messages = [...prev.messages];
          const lastMsg = messages[messages.length - 1];
          if (lastMsg && lastMsg.role === "assistant") {
            messages[messages.length - 1] = {
              ...lastMsg,
              content:
                lastMsg.content + (eventData?.content || data.content || ""),
            };
          } else {
            // Create new assistant message if none exists
            messages.push({
              role: "assistant",
              content: eventData?.content || data.content || "",
            });
          }
          return { ...prev, messages };
        });
        break;

      case "done":
        // Parse GGB blocks from answer message content when done
        setState((prev) => {
          const messages = prev.messages.map((msg) => {
            // Only parse GGB blocks for answer messages
            if (
              msg.role === "assistant" &&
              msg.messageType === "answer" &&
              msg.content
            ) {
              const ggbBlocks = parseGGBBlocks(msg.content);
              return {
                ...msg,
                ggbBlocks,
              };
            }
            return msg;
          });

          return {
            ...prev,
            messages,
            isProcessing: false,
            currentStage: null,
          };
        });
        break;

      case "error":
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          error: eventData?.content || data.content || "Unknown error",
        }));
        break;

      case "no_image":
        // No image provided, just continue without analysis
        break;

      default:
        console.log("Unknown message type:", type, data);
    }
  }, []);

  const sendMessage = useCallback(
    (question: string, image_base64?: string) => {
      // Add user message immediately
      const userMessage: Message = {
        role: "user",
        content: question,
        image: image_base64,
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isProcessing: true,
        currentStage: "connecting",
        analysisStages: {},
        error: null,
      }));

      // Store pending message for WebSocket
      pendingMessageRef.current = { question, image: image_base64 };

      // Create WebSocket connection
      const ws = new WebSocket(wsUrl("/api/v1/vision/solve"));
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("Vision solver WebSocket connected");
        if (pendingMessageRef.current) {
          ws.send(
            JSON.stringify({
              question: pendingMessageRef.current.question,
              image_base64: pendingMessageRef.current.image,
            }),
          );
          pendingMessageRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          error: "Connection error",
        }));
      };

      ws.onclose = () => {
        console.log("Vision solver WebSocket closed");
        wsRef.current = null;
      };
    },
    [handleWebSocketMessage],
  );

  const reset = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setState(initialState);
  }, []);

  return {
    state,
    sendMessage,
    reset,
  };
}

// Parse GGB commands from content string
export function parseGGBCommands(content: string): GGBCommand[] {
  if (!content) return [];

  const lines = content.split("\n").filter((line) => line.trim());
  const commands: GGBCommand[] = [];
  let sequence = 0;
  let currentDescription = "";

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("#")) {
      // Comment line, use as description for next command
      currentDescription = trimmed.slice(1).trim();
    } else if (trimmed) {
      sequence++;
      commands.push({
        sequence,
        command: trimmed,
        description: currentDescription,
      });
      currentDescription = "";
    }
  }

  return commands;
}

/**
 * Parse GGBScript blocks from message content
 * Matches: ```ggbscript[page-id;optional-title] or ```geogebra[page-id;optional-title]
 */
export function parseGGBBlocks(content: string): GGBBlock[] {
  if (!content) return [];

  const blocks: GGBBlock[] = [];
  const blockPattern =
    /```\s*(ggbscript|geogebra)\s*\[([^\]\s;]+)(?:;([^\]]*))?\]\s*\n?([\s\S]*?)```/gi;

  let match;
  while ((match = blockPattern.exec(content)) !== null) {
    const blockContent = match[4].trim();
    blocks.push({
      pageId: match[2],
      title: (match[3] || "GeoGebra").trim(),
      content: blockContent,
      commands: parseGGBCommands(blockContent),
    });
  }

  return blocks;
}

/**
 * Remove GGBScript blocks from content to get plain text
 */
export function stripGGBBlocks(content: string): string {
  if (!content) return "";
  return content
    .replace(/```\s*(ggbscript|geogebra)\s*\[[^\]]*\]\s*\n?[\s\S]*?```/gi, "")
    .trim();
}
