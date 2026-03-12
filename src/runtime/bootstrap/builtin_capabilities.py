"""Built-in capability class paths."""

BUILTIN_CAPABILITY_CLASSES: dict[str, str] = {
    "chat": "src.capabilities.chat:ChatCapability",
    "deep_solve": "src.capabilities.deep_solve:DeepSolveCapability",
    "deep_question": "src.capabilities.deep_question:DeepQuestionCapability",
    "deep_research": "src.capabilities.deep_research:DeepResearchCapability",
    "math_animator": "src.capabilities.math_animator:MathAnimatorCapability",
}
