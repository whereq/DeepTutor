#!/usr/bin/env python
"""
Memory System - Memory storage for solving process

Provides implementations of InvestigateMemory and SolveMemory.
"""

from .citation_memory import (
    CitationItem,
    CitationMemory,
)
from .investigate_memory import (
    InvestigateMemory,
    KnowledgeItem,
    Reflections,
)
from .solve_memory import (
    # Core data structures
    IterationRecord,
    NoteAction,
    SolveChainStep,
    SolveMemory,
    SolveOutput,
    TodoItem,
    ToolCallRecord,
)

__all__ = [
    # Investigate Memory
    "InvestigateMemory",
    "KnowledgeItem",
    "Reflections",
    # Solve Memory - Core
    "SolveMemory",
    "TodoItem",
    "ToolCallRecord",
    # Solve Memory - New iteration architecture
    "IterationRecord",
    "NoteAction",
    # Solve Memory - Legacy/Backward compatibility
    "SolveOutput",
    "SolveChainStep",
    # Citation Memory
    "CitationMemory",
    "CitationItem",
]
