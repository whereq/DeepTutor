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
- EventFileQueue: File-based event queue for cross-process communication

Running Modes:
1. In-process mode (default): Service runs within the main application
2. External mode: Service runs as a separate process via start_personalization.py
   - Enable file queue with: from src.core.event_bus import enable_file_queue
   - Run: python scripts/start_personalization.py
"""

from .event_queue import EventFileQueue, QueuedEvent, get_event_queue
from .memory import LearningMemory, get_learning_memory
from .memory_agent import MemoryAgent, MemoryDecision
from .service import PersonalizationService, get_personalization_service

__all__ = [
    # Memory
    "LearningMemory",
    "get_learning_memory",
    # Agent
    "MemoryAgent",
    "MemoryDecision",
    # Service
    "PersonalizationService",
    "get_personalization_service",
    # Event Queue (for external mode)
    "EventFileQueue",
    "QueuedEvent",
    "get_event_queue",
]
