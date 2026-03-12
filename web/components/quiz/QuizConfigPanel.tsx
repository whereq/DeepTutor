"use client";

import { useRef, useState } from "react";
import { FileText, Upload, X } from "lucide-react";
import type { DeepQuestionFormConfig, DeepQuestionMode } from "@/lib/quiz-types";

interface QuizConfigPanelProps {
  value: DeepQuestionFormConfig;
  onChange: (next: DeepQuestionFormConfig) => void;
  uploadedPdf: File | null;
  onUploadPdf: (file: File | null) => void;
}

const INPUT_CLS =
  "h-[32px] rounded-md border border-[var(--border)]/30 bg-[var(--background)]/50 px-2.5 text-[12px] text-[var(--foreground)] outline-none transition-colors hover:border-[var(--border)]/50 focus:border-[var(--primary)]/35 placeholder:text-[var(--muted-foreground)]/40";

export default function QuizConfigPanel({
  value,
  onChange,
  uploadedPdf,
  onUploadPdf,
}: QuizConfigPanelProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const update = <K extends keyof DeepQuestionFormConfig>(
    key: K,
    val: DeepQuestionFormConfig[K],
  ) => onChange({ ...value, [key]: val });

  const setMode = (m: DeepQuestionMode) => update("mode", m);

  return (
    <div className="px-3.5 py-2.5 space-y-2.5">
      {/* Mode tabs — baseline-aligned */}
      <div className="flex items-baseline gap-4">
        {(["custom", "mimic"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`pb-0.5 text-[11px] font-medium transition-colors border-b ${
              value.mode === m
                ? "border-[var(--foreground)]/30 text-[var(--foreground)]"
                : "border-transparent text-[var(--muted-foreground)]/45 hover:text-[var(--muted-foreground)]"
            }`}
          >
            {m === "custom" ? "Custom" : "Mimic Paper"}
          </button>
        ))}
      </div>

      {value.mode === "custom" ? (
        <div className="flex flex-wrap items-end gap-x-3 gap-y-2">
          <Field label="Count" width="w-[60px]">
            <input
              type="number"
              min={1}
              max={50}
              value={value.num_questions}
              onChange={(e) =>
                update("num_questions", Math.max(1, Number(e.target.value) || 1))
              }
              className={`${INPUT_CLS} w-full`}
            />
          </Field>

          <Field label="Difficulty" width="w-[100px]">
            <select
              value={value.difficulty}
              onChange={(e) => update("difficulty", e.target.value)}
              className={`${INPUT_CLS} w-full`}
            >
              <option value="auto">Auto</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </Field>

          <Field label="Type" width="w-[110px]">
            <select
              value={value.question_type}
              onChange={(e) => update("question_type", e.target.value)}
              className={`${INPUT_CLS} w-full`}
            >
              <option value="auto">Auto</option>
              <option value="choice">Multiple Choice</option>
              <option value="written">Written</option>
              <option value="coding">Coding</option>
            </select>
          </Field>

          <Field label="Preference" width="min-w-[140px] flex-1">
            <input
              type="text"
              value={value.preference}
              onChange={(e) => update("preference", e.target.value)}
              placeholder="Extra constraints..."
              className={`${INPUT_CLS} w-full`}
            />
          </Field>
        </div>
      ) : (
        <div className="flex flex-wrap items-end gap-x-3 gap-y-2">
          <Field label="Paper" width="min-w-[180px] flex-[1.3]">
            {uploadedPdf ? (
              <div className="flex h-[32px] items-center gap-2 rounded-md border border-[var(--border)]/30 bg-[var(--background)]/50 px-2.5 text-[12px]">
                <FileText size={12} className="shrink-0 text-[var(--primary)]/60" />
                <span className="min-w-0 truncate text-[var(--foreground)]">{uploadedPdf.name}</span>
                <button
                  type="button"
                  onClick={() => onUploadPdf(null)}
                  className="ml-auto shrink-0 text-[var(--muted-foreground)]/40 transition-colors hover:text-[var(--foreground)]"
                  aria-label="Remove PDF"
                >
                  <X size={11} />
                </button>
              </div>
            ) : (
              <label
                className={`flex h-[32px] cursor-pointer items-center justify-center gap-1.5 rounded-md border border-dashed px-2.5 text-[12px] transition-colors ${
                  dragOver
                    ? "border-[var(--primary)]/35 text-[var(--primary)]"
                    : "border-[var(--border)]/35 text-[var(--muted-foreground)]/50 hover:border-[var(--border)]/55 hover:text-[var(--foreground)]"
                }`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragOver(false);
                  const f = e.dataTransfer.files[0];
                  if (f?.type === "application/pdf") {
                    onUploadPdf(f);
                    update("paper_path", "");
                  }
                }}
              >
                <Upload size={11} />
                <span>Upload PDF</span>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0] ?? null;
                    if (f) {
                      onUploadPdf(f);
                      update("paper_path", "");
                    }
                    e.target.value = "";
                  }}
                />
              </label>
            )}
          </Field>

          <Field label="Parsed Dir" width="min-w-[120px] flex-1">
            <input
              type="text"
              value={value.paper_path}
              onChange={(e) => {
                onUploadPdf(null);
                update("paper_path", e.target.value);
              }}
              placeholder="e.g. 2211asm1"
              className={`${INPUT_CLS} w-full`}
            />
          </Field>

          <Field label="Max" width="w-[60px]">
            <input
              type="number"
              min={1}
              max={100}
              value={value.max_questions}
              onChange={(e) =>
                update("max_questions", Math.max(1, Number(e.target.value) || 1))
              }
              className={`${INPUT_CLS} w-full`}
            />
          </Field>
        </div>
      )}
    </div>
  );
}

function Field({
  label,
  width,
  children,
}: {
  label: string;
  width?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={width}>
      <div className="mb-1 text-[9px] font-medium uppercase tracking-[0.08em] text-[var(--muted-foreground)]/40">
        {label}
      </div>
      {children}
    </div>
  );
}
