#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Solve Loop - Problem-solving workflow

Pipeline: Manager → [Solve → Tool → Note]* → PrecisionAnswer

Based on Analysis output, plan and execute problem-solving process, generate high-quality answers.
"""

from .citation_manager import CitationManager
from .manager_agent import ManagerAgent
from .precision_answer_agent import PrecisionAnswerAgent
from .response_agent import ResponseAgent
from .solve_agent import SolveAgent
from .solve_note_agent import SolveNoteAgent
from .tool_agent import ToolAgent

__all__ = [
    # Core agents
    "ManagerAgent",
    "SolveAgent",
    "ToolAgent",
    "SolveNoteAgent",
    "ResponseAgent",
    "PrecisionAnswerAgent",
    # Utils
    "CitationManager",
]
