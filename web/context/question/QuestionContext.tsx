"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from "react";
import { wsUrl } from "@/lib/api";
import {
  DEFAULT_QUESTION_AGENT_STATUS,
  DEFAULT_QUESTION_TOKEN_STATS,
  INITIAL_QUESTION_CONTEXT_STATE,
  QuestionContextState,
} from "@/types/question";
import { LogEntry } from "@/types/common";

interface QuestionContextType {
  questionState: QuestionContextState;
  setQuestionState: React.Dispatch<React.SetStateAction<QuestionContextState>>;
  startQuestionGen: (
    topic: string,
    diff: string,
    type: string,
    count: number,
    kb: string,
  ) => void;
  startMimicQuestionGen: (
    file: File | null,
    paperPath: string,
    kb: string,
    maxQuestions?: number,
  ) => void;
  resetQuestionGen: () => void;
}

const QuestionContext = createContext<QuestionContextType | undefined>(undefined);

export function QuestionProvider({ children }: { children: React.ReactNode }) {
  const [questionState, setQuestionState] = useState<QuestionContextState>(
    INITIAL_QUESTION_CONTEXT_STATE,
  );
  const questionWs = useRef<WebSocket | null>(null);

  const addQuestionLog = useCallback((log: LogEntry) => {
    setQuestionState((prev) => ({ ...prev, logs: [...prev.logs, log] }));
  }, []);

  const handleCommonWsMessage = useCallback(
    (data: any, ws: WebSocket) => {
      if (data.type === "log") {
        addQuestionLog(data);
        return;
      }

      if (data.type === "status") {
        addQuestionLog({ type: "system", content: data.content || "Started" });
        return;
      }

      if (data.type === "progress") {
        const stage = data.stage || "generating";
        setQuestionState((prev) => ({
          ...prev,
          progress: {
            ...prev.progress,
            stage,
            progress: {
              ...prev.progress.progress,
              current:
                data.current ?? data.progress?.current ?? prev.progress.progress.current,
              total: data.total ?? data.progress?.total ?? prev.progress.progress.total,
              status: data.status ?? data.progress?.status,
              round:
                data.current_round ??
                data.round ??
                data.progress?.round ??
                prev.progress.progress.round,
              max_rounds:
                data.max_rounds ??
                data.maxRounds ??
                data.progress?.max_rounds ??
                prev.progress.progress.max_rounds,
            },
            completedQuestions:
              data.completed ?? prev.progress.completedQuestions ?? prev.results.length,
            failedQuestions: data.failed ?? prev.progress.failedQuestions,
          },
        }));
        if (data.message) {
          addQuestionLog({ type: "system", content: data.message });
        }
        return;
      }

      if (data.type === "templates_ready") {
        const templates = data.templates || [];
        const subFocuses = templates.map((t: any, i: number) => ({
          id: t.question_id || `q_${i + 1}`,
          focus: t.concentration || "",
        }));
        setQuestionState((prev) => ({
          ...prev,
          progress: {
            ...prev.progress,
            stage: "templates_ready",
            subFocuses,
            progress: {
              ...prev.progress.progress,
              total: data.count || templates.length || prev.progress.progress.total,
            },
          },
        }));
        addQuestionLog({
          type: "success",
          content: `Templates ready: ${data.count || templates.length}`,
        });
        return;
      }

      if (data.type === "idea_round") {
        addQuestionLog({
          type: "system",
          content: `Idea round ${data.round || "?"} complete${data.feedback ? `: ${data.feedback}` : ""}`,
        });
        setQuestionState((prev) => ({
          ...prev,
          progress: {
            ...prev.progress,
            stage: "idea_loop",
          },
        }));
        return;
      }

      if (data.type === "question_update") {
        addQuestionLog({
          type: data.status === "error" ? "warning" : "system",
          content: `[${data.question_id}] ${data.status || "updating"}`,
        });
        return;
      }

      if (data.type === "validating") {
        setQuestionState((prev) => ({
          ...prev,
          progress: { ...prev.progress, stage: "validating" },
        }));
        addQuestionLog({
          type: "system",
          content: `[${data.question_id}] validating (attempt ${data.attempt || 1})`,
        });
        return;
      }

      if (data.type === "result") {
        const incomingQuestion = data.question || {};
        const question = {
          ...incomingQuestion,
          type: incomingQuestion.type || incomingQuestion.question_type,
          question_type: incomingQuestion.question_type || incomingQuestion.type,
          concentration: incomingQuestion.concentration || "",
          difficulty: incomingQuestion.difficulty || "",
          metadata: incomingQuestion.metadata || {},
        };
        const validation = data.validation || {};
        addQuestionLog({
          type: "success",
          content: `[${data.question_id || "q"}] generated`,
        });
        setQuestionState((prev) => ({
          ...prev,
          results: [
            ...prev.results,
            {
              success: true,
              question_id: data.question_id || `q_${prev.results.length + 1}`,
              question,
              validation,
              rounds: data.attempts || data.rounds || 1,
            },
          ],
          progress: {
            ...prev.progress,
            stage: "generating",
            completedQuestions: prev.results.length + 1,
            progress: {
              ...prev.progress.progress,
              current: prev.results.length + 1,
              total: data.total ?? prev.progress.progress.total ?? prev.count,
            },
          },
        }));
        return;
      }

      if (data.type === "batch_summary") {
        addQuestionLog({
          type: "success",
          content: `Batch summary: ${data.completed || 0}/${data.requested || 0}`,
        });
        setQuestionState((prev) => ({
          ...prev,
          progress: {
            ...prev.progress,
            completedQuestions: data.completed ?? prev.progress.completedQuestions,
            failedQuestions: data.failed ?? prev.progress.failedQuestions,
            progress: {
              ...prev.progress.progress,
              current: data.completed ?? prev.progress.progress.current,
              total: data.requested ?? prev.progress.progress.total,
            },
          },
        }));
        return;
      }

      if (data.type === "complete") {
        addQuestionLog({ type: "success", content: "Generation complete" });
        setQuestionState((prev) => ({
          ...prev,
          step: "result",
          progress: {
            ...prev.progress,
            stage: "complete",
            completedQuestions: prev.results.length,
          },
        }));
        ws.close();
        return;
      }

      if (data.type === "error") {
        addQuestionLog({
          type: "error",
          content: data.content || data.message || "Unknown error",
        });
        setQuestionState((prev) => ({
          ...prev,
          step: "config",
          progress: { stage: null, progress: {} },
        }));
      }
    },
    [addQuestionLog],
  );

  const startQuestionGen = useCallback(
    (topic: string, diff: string, type: string, count: number, kb: string) => {
      if (questionWs.current) questionWs.current.close();
      const normalizedDiff =
        (diff || "").trim().toLowerCase() === "auto" ? "" : (diff || "").trim();
      const normalizedType =
        (type || "").trim().toLowerCase() === "auto" ? "" : (type || "").trim();

      setQuestionState((prev) => ({
        ...prev,
        step: "generating",
        mode: "knowledge",
        logs: [],
        results: [],
        topic,
        difficulty: diff,
        type,
        count,
        selectedKb: kb,
        progress: {
          stage: "idea_loop",
          progress: { current: 0, total: count },
          subFocuses: [],
          activeQuestions: [],
          completedQuestions: 0,
          failedQuestions: 0,
        },
        agentStatus: { ...DEFAULT_QUESTION_AGENT_STATUS },
        tokenStats: { ...DEFAULT_QUESTION_TOKEN_STATS },
      }));

      const ws = new WebSocket(wsUrl("/api/v1/question/generate"));
      questionWs.current = ws;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            requirement: {
              knowledge_point: topic,
              difficulty: normalizedDiff,
              question_type: normalizedType,
              additional_requirements: "Ensure clarity and academic rigor.",
            },
            count,
            kb_name: kb,
          }),
        );
        addQuestionLog({ type: "system", content: "Initializing Generator..." });
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleCommonWsMessage(data, ws);
      };

      ws.onerror = () => {
        addQuestionLog({ type: "error", content: "WebSocket connection error" });
        setQuestionState((prev) => ({
          ...prev,
          step: "config",
          progress: { stage: null, progress: {} },
          agentStatus: { ...DEFAULT_QUESTION_AGENT_STATUS },
        }));
      };

      ws.onclose = () => {
        if (questionWs.current === ws) questionWs.current = null;
      };
    },
    [addQuestionLog, handleCommonWsMessage],
  );

  const startMimicQuestionGen = useCallback(
    async (file: File | null, paperPath: string, kb: string, maxQuestions?: number) => {
      if (questionWs.current) questionWs.current.close();

      const hasFile = file !== null;
      const hasParsedPath = paperPath && paperPath.trim() !== "";
      if (!hasFile && !hasParsedPath) {
        addQuestionLog({
          type: "error",
          content: "Please upload a PDF file or provide a parsed exam directory",
        });
        return;
      }

      setQuestionState((prev) => ({
        ...prev,
        step: "generating",
        mode: "mimic",
        logs: [],
        results: [],
        selectedKb: kb,
        uploadedFile: file,
        paperPath,
        progress: {
          stage: hasFile ? "uploading" : "parsing",
          progress: { current: 0, total: maxQuestions || 1 },
          subFocuses: [],
          activeQuestions: [],
          completedQuestions: 0,
          failedQuestions: 0,
        },
        agentStatus: { ...DEFAULT_QUESTION_AGENT_STATUS },
        tokenStats: { ...DEFAULT_QUESTION_TOKEN_STATS },
      }));

      const ws = new WebSocket(wsUrl("/api/v1/question/mimic"));
      questionWs.current = ws;

      ws.onopen = async () => {
        if (hasFile && file) {
          const reader = new FileReader();
          reader.onload = () => {
            const base64Data = (reader.result as string).split(",")[1];
            ws.send(
              JSON.stringify({
                mode: "upload",
                pdf_data: base64Data,
                pdf_name: file.name,
                kb_name: kb,
                max_questions: maxQuestions,
              }),
            );
          };
          reader.readAsDataURL(file);
        } else {
          ws.send(
            JSON.stringify({
              mode: "parsed",
              paper_path: paperPath,
              kb_name: kb,
              max_questions: maxQuestions,
            }),
          );
        }
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleCommonWsMessage(data, ws);
      };

      ws.onerror = () => {
        addQuestionLog({ type: "error", content: "WebSocket connection error" });
        setQuestionState((prev) => ({ ...prev, step: "config" }));
      };
    },
    [addQuestionLog, handleCommonWsMessage],
  );

  const resetQuestionGen = useCallback(() => {
    setQuestionState((prev) => ({
      ...prev,
      step: "config",
      results: [],
      logs: [],
      progress: {
        stage: null,
        progress: {},
        subFocuses: [],
        activeQuestions: [],
        completedQuestions: 0,
        failedQuestions: 0,
      },
      agentStatus: { ...DEFAULT_QUESTION_AGENT_STATUS },
      tokenStats: { ...DEFAULT_QUESTION_TOKEN_STATS },
      uploadedFile: null,
      paperPath: "",
    }));
  }, []);

  return (
    <QuestionContext.Provider
      value={{
        questionState,
        setQuestionState,
        startQuestionGen,
        startMimicQuestionGen,
        resetQuestionGen,
      }}
    >
      {children}
    </QuestionContext.Provider>
  );
}

export const useQuestion = () => {
  const context = useContext(QuestionContext);
  if (!context) throw new Error("useQuestion must be used within QuestionProvider");
  return context;
};
