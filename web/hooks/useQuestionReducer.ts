import { useReducer } from "react";
import {
  QuestionState,
  QuestionEvent,
  QuestionTask,
  QuestionLogEntry,
  QuestionResult,
  QuestionFailure,
  QuestionTemplate,
} from "../types/question";

export const initialQuestionState: QuestionState = {
  global: {
    stage: "idle",
    startTime: 0,
    totalQuestions: 0,
    completedQuestions: 0,
    failedQuestions: 0,
    extendedQuestions: 0,
  },
  planning: {
    topic: "",
    difficulty: "",
    questionType: "",
    queries: [],
    progress: "",
  },
  tasks: {},
  activeTaskIds: [],
  results: [],
  failures: [],
  subFocuses: [],
  logs: [],
};

const createLog = (
  content: string,
  type: QuestionLogEntry["type"] = "info",
): QuestionLogEntry => ({
  id: Math.random().toString(36).substring(7),
  timestamp: Date.now(),
  type,
  content,
});

const ensureTask = (
  state: QuestionState,
  taskId: string,
  focus = "",
): QuestionTask => {
  if (state.tasks[taskId]) return state.tasks[taskId];
  return {
    id: taskId,
    focus,
    status: "pending",
    round: 0,
    lastUpdate: Date.now(),
  };
};

const templatesToFocuses = (templates: QuestionTemplate[] | undefined) => {
  if (!templates || templates.length === 0) return [];
  return templates.map((t) => ({
    id: t.question_id,
    focus: t.concentration,
  }));
};

export const questionReducer = (
  state: QuestionState,
  event: QuestionEvent,
): QuestionState => {
  const newLog = event.type === "log" ? createLog(event.content || "") : null;
  const logs = newLog ? [...state.logs, newLog] : state.logs;

  switch (event.type) {
    case "status": {
      if (event.content === "started") {
        return {
          ...state,
          global: { ...state.global, stage: "idea_loop", startTime: Date.now() },
          logs: [...logs, createLog("Question generation started")],
        };
      }
      return state;
    }

    case "progress": {
      const stage = event.stage as QuestionState["global"]["stage"];
      if (!stage) return state;
      return {
        ...state,
        global: {
          ...state.global,
          stage,
          totalQuestions: event.total || state.global.totalQuestions,
          completedQuestions: event.completed ?? state.global.completedQuestions,
          failedQuestions: event.failed ?? state.global.failedQuestions,
        },
        logs: [
          ...logs,
          createLog(
            event.message || `${stage}${event.status ? `: ${event.status}` : ""}`,
            "system",
          ),
        ],
      };
    }

    case "templates_ready": {
      const focuses = templatesToFocuses(event.templates);
      const newTasks: Record<string, QuestionTask> = {};
      focuses.forEach((f) => {
        newTasks[f.id] = ensureTask(state, f.id, f.focus);
      });

      return {
        ...state,
        global: {
          ...state.global,
          stage: "templates_ready",
          totalQuestions: event.count || focuses.length || state.global.totalQuestions,
        },
        subFocuses: focuses,
        tasks: { ...state.tasks, ...newTasks },
        logs: [
          ...logs,
          createLog(`Templates ready: ${focuses.length} question templates`, "success"),
        ],
      };
    }

    case "idea_round": {
      return {
        ...state,
        global: { ...state.global, stage: "idea_loop" },
        logs: [
          ...logs,
          createLog(
            `Idea round ${event.round || "?"} completed${event.feedback ? `: ${event.feedback}` : ""}`,
            "system",
          ),
        ],
      };
    }

    case "question_update": {
      const questionId = event.question_id;
      if (!questionId) return state;
      const existingTask = ensureTask(state, questionId);
      const statusMap: Record<string, QuestionTask["status"]> = {
        generating: "generating",
        validating: "validating",
        done: "done",
        error: "error",
      };
      const nextStatus = statusMap[event.status || ""] || existingTask.status;
      let activeTaskIds = [...state.activeTaskIds];
      if (nextStatus === "generating" || nextStatus === "validating") {
        if (!activeTaskIds.includes(questionId)) activeTaskIds.push(questionId);
      } else {
        activeTaskIds = activeTaskIds.filter((id) => id !== questionId);
      }
      return {
        ...state,
        tasks: {
          ...state.tasks,
          [questionId]: {
            ...existingTask,
            status: nextStatus,
            lastUpdate: Date.now(),
          },
        },
        activeTaskIds,
      };
    }

    case "validating": {
      const questionId = event.question_id;
      if (!questionId) return state;
      const existingTask = ensureTask(state, questionId);
      return {
        ...state,
        global: { ...state.global, stage: "validating" },
        tasks: {
          ...state.tasks,
          [questionId]: {
            ...existingTask,
            status: "validating",
            lastUpdate: Date.now(),
          },
        },
      };
    }

    case "result":
    case "question_result": {
      const questionId = event.question_id || `q_${(event.index || 0) + 1}`;
      const isExtended = event.extended || event.validation?.decision === "extended";
      const result: QuestionResult = {
        success: true,
        question_id: questionId,
        question: event.question || {
          question: "",
          correct_answer: "",
          explanation: "",
        },
        validation: event.validation || {},
        rounds: event.rounds || event.attempts || 1,
        extended: isExtended,
      };
      return {
        ...state,
        global: {
          ...state.global,
          stage: "generating",
          completedQuestions: state.global.completedQuestions + 1,
          extendedQuestions: state.global.extendedQuestions + (isExtended ? 1 : 0),
        },
        tasks: {
          ...state.tasks,
          [questionId]: {
            ...ensureTask(state, questionId),
            status: "done",
            result,
            lastUpdate: Date.now(),
          },
        },
        activeTaskIds: state.activeTaskIds.filter((id) => id !== questionId),
        results: [...state.results, result],
        logs: [...logs, createLog(`Question ${questionId} generated`, "success")],
      };
    }

    case "question_error":
    case "error": {
      const questionId = event.question_id || "unknown";
      const failure: QuestionFailure = {
        question_id: questionId,
        error: event.error || event.content || "Unknown error",
      };
      return {
        ...state,
        global: { ...state.global, failedQuestions: state.global.failedQuestions + 1 },
        tasks: {
          ...state.tasks,
          [questionId]: {
            ...ensureTask(state, questionId),
            status: "error",
            error: failure.error,
            lastUpdate: Date.now(),
          },
        },
        failures: [...state.failures, failure],
        logs: [...logs, createLog(failure.error, "error")],
      };
    }

    case "batch_summary": {
      return {
        ...state,
        global: {
          ...state.global,
          totalQuestions: event.requested || state.global.totalQuestions,
          completedQuestions: event.completed || state.global.completedQuestions,
          failedQuestions: event.failed || state.global.failedQuestions,
        },
        logs: [
          ...logs,
          createLog(
            `Batch summary: ${event.completed || 0}/${event.requested || 0} completed`,
          ),
        ],
      };
    }

    case "complete": {
      return {
        ...state,
        global: { ...state.global, stage: "complete" },
        logs: [...logs, createLog("Question generation completed", "success")],
      };
    }

    case "log":
      return { ...state, logs };

    default:
      return { ...state, logs };
  }
};

export const useQuestionReducer = () => {
  return useReducer(questionReducer, initialQuestionState);
};

export const resetQuestionState = (): QuestionState => ({
  ...initialQuestionState,
  logs: [],
});
