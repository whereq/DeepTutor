"use client";

import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { VisionSolverState } from "../hooks/useVisionSolver";

interface AnalysisProgressProps {
  state: VisionSolverState;
}

const STAGES = [
  { key: "bbox", label: "Element Detection" },
  { key: "analysis", label: "Geometric Analysis" },
  { key: "ggbscript", label: "Command Generation" },
  { key: "reflection", label: "Validation" },
  { key: "answering", label: "Solving Problem" },
] as const;

export function AnalysisProgress({ state }: AnalysisProgressProps) {
  const { t } = useTranslation();
  const { currentStage, analysisStages } = state;

  const getStageStatus = (
    stageKey: string,
  ): "pending" | "active" | "complete" => {
    const stageOrder = STAGES.map((s) => s.key);
    const currentIndex = stageOrder.indexOf(currentStage || "");
    const stageIndex = stageOrder.indexOf(stageKey);

    // Check if stage has data (completed) - for analysis stages
    if (
      stageKey !== "answering" &&
      analysisStages[stageKey as keyof typeof analysisStages]
    ) {
      return "complete";
    }

    // Check if this is current stage
    if (currentStage === stageKey) {
      return "active";
    }

    // If current stage is after this stage, it's complete
    if (currentIndex > stageIndex && currentIndex !== -1) {
      return "complete";
    }

    // If we're not processing and all previous stages are done, answering is complete
    if (
      stageKey === "answering" &&
      !state.isProcessing &&
      analysisStages.reflection
    ) {
      return "complete";
    }

    return "pending";
  };

  return (
    <div className="bg-white dark:bg-slate-800 px-5 py-4 rounded-2xl rounded-tl-none border border-slate-100 dark:border-slate-700 shadow-sm">
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
          {t("Analyzing Image")}
        </h4>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {t("Extracting geometric elements and generating visualization...")}
        </p>
      </div>

      <div className="space-y-3">
        {STAGES.map((stage, index) => {
          const status = getStageStatus(stage.key);

          return (
            <div
              key={stage.key}
              className={`flex items-center gap-3 ${
                status === "pending" ? "opacity-50" : ""
              }`}
            >
              {/* Status Icon */}
              <div className="shrink-0">
                {status === "complete" ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : status === "active" ? (
                  <Loader2 className="w-5 h-5 text-indigo-500 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-300 dark:text-slate-600" />
                )}
              </div>

              {/* Label */}
              <div className="flex-1">
                <span
                  className={`text-sm ${
                    status === "active"
                      ? "font-medium text-indigo-600 dark:text-indigo-400"
                      : status === "complete"
                        ? "text-slate-700 dark:text-slate-300"
                        : "text-slate-400 dark:text-slate-500"
                  }`}
                >
                  {t(stage.label)}
                </span>

                {/* Stage Details */}
                {status === "complete" &&
                  stage.key === "bbox" &&
                  analysisStages.bbox && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {t("Found")} {analysisStages.bbox.elements_count}{" "}
                      {t("elements")}
                    </p>
                  )}
                {status === "complete" &&
                  stage.key === "analysis" &&
                  analysisStages.analysis && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {analysisStages.analysis.constraints_count}{" "}
                      {t("constraints")},{" "}
                      {analysisStages.analysis.relations_count} {t("relations")}
                    </p>
                  )}
                {status === "complete" &&
                  stage.key === "ggbscript" &&
                  analysisStages.ggbscript && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {analysisStages.ggbscript.commands_count} {t("commands")}
                    </p>
                  )}
                {status === "complete" &&
                  stage.key === "reflection" &&
                  analysisStages.reflection && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {analysisStages.reflection.issues_count === 0
                        ? t("No issues found")
                        : `${analysisStages.reflection.issues_count} ${t("issues fixed")}`}
                    </p>
                  )}
              </div>

              {/* Progress Line */}
              {index < STAGES.length - 1 && (
                <div className="absolute left-[26px] top-[28px] w-0.5 h-6 bg-slate-200 dark:bg-slate-600" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
