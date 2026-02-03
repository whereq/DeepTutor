# -*- coding: utf-8 -*-
"""
Personalization Module
======================

Provides personalized learning experience through memory management and
event-driven updates.

Components:
- LearningMemory: Markdown-based memory storage for user preferences and notes
- MemoryAgent: LLM-powered agent for memory analysis and updates
- PersonalizationService: Service layer for memory management
"""

from .memory import LearningMemory, get_learning_memory
from .memory_agent import MemoryAgent, MemoryDecision
from .service import PersonalizationService, get_personalization_service

__all__ = [
    "LearningMemory",
    "get_learning_memory",
    "MemoryAgent",
    "MemoryDecision",
    "PersonalizationService",
    "get_personalization_service",
]
