"""Solve agent — agentic-engine-based pipeline.

Public surface: :class:`SolvePipeline`. The legacy ``MainSolver`` +
``SolverSessionManager`` + three-agent (planner / solver / writer) stack
has been replaced by a single label-driven pipeline that runs on top of
:mod:`deeptutor.core.agentic`.
"""

from .pipeline import (
    Plan,
    PlanStep,
    SolvePipeline,
    StepFinish,
)

__all__ = [
    "Plan",
    "PlanStep",
    "SolvePipeline",
    "StepFinish",
]
