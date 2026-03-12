"""
Question generation package.

Exports are resolved lazily so lightweight imports such as
``src.agents.question.models`` do not eagerly pull in optional RAG dependencies.
"""

from importlib import import_module
from typing import Any

__all__ = [
    "IdeaAgent",
    "Generator",
    "FollowupAgent",
    "QuestionTemplate",
    "QAPair",
    "AgentCoordinator",
]


def __getattr__(name: str) -> Any:
    if name in {"IdeaAgent", "Generator", "FollowupAgent"}:
        module = import_module("src.agents.question.agents")
        return getattr(module, name)
    if name == "AgentCoordinator":
        module = import_module("src.agents.question.coordinator")
        return getattr(module, name)
    if name in {"QuestionTemplate", "QAPair"}:
        module = import_module("src.agents.question.models")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
