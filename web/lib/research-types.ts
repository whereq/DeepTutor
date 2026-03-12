export type ResearchMode = "" | "notes" | "report" | "comparison" | "learning_path";
export type ResearchDepth = "" | "quick" | "standard" | "deep";
export type ResearchSource = "kb" | "web" | "papers";

export interface DeepResearchFormConfig {
  mode: ResearchMode;
  depth: ResearchDepth;
  sources: ResearchSource[];
}

export interface ResearchConfigValidationResult {
  valid: boolean;
  errors: Record<string, string>;
}

export function createEmptyResearchConfig(): DeepResearchFormConfig {
  return {
    mode: "",
    depth: "",
    sources: [],
  };
}

export function normalizeResearchConfig(
  raw: Record<string, unknown> | undefined,
): DeepResearchFormConfig {
  const empty = createEmptyResearchConfig();
  return {
    mode:
      raw?.mode === "notes" ||
      raw?.mode === "report" ||
      raw?.mode === "comparison" ||
      raw?.mode === "learning_path"
        ? raw.mode
        : empty.mode,
    depth:
      raw?.depth === "quick" || raw?.depth === "standard" || raw?.depth === "deep"
        ? raw.depth
        : empty.depth,
    sources: Array.isArray(raw?.sources)
      ? raw.sources.filter(
          (source): source is ResearchSource =>
            source === "kb" || source === "web" || source === "papers",
        )
      : empty.sources,
  };
}

export function validateResearchConfig(
  cfg: DeepResearchFormConfig,
): ResearchConfigValidationResult {
  const errors: Record<string, string> = {};

  if (!cfg.mode) {
    errors.mode = "Required";
  }
  if (!cfg.depth) {
    errors.depth = "Required";
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

export function buildResearchWSConfig(
  cfg: DeepResearchFormConfig,
): Record<string, unknown> {
  const validation = validateResearchConfig(cfg);
  if (!validation.valid) {
    throw new Error("Deep research settings are incomplete.");
  }

  return {
    mode: cfg.mode,
    depth: cfg.depth,
    sources: [...cfg.sources],
  };
}

export function summarizeResearchConfig(cfg: DeepResearchFormConfig): string {
  const validation = validateResearchConfig(cfg);
  if (!validation.valid) return "Incomplete settings";
  const sourceSummary = cfg.sources.length ? cfg.sources.join("+") : "llm-only";
  return [
    cfg.mode.replace("_", " "),
    cfg.depth,
    sourceSummary,
  ].join(" · ");
}
