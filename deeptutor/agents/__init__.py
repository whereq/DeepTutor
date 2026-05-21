"""
Agents Module - Unified agent system for OpenTutor.

This module provides a unified BaseAgent class and module-specific agents:
- solve: Multi-step problem solving (``SolvePipeline`` on the agentic engine)
- research: Deep research agents (DecomposeAgent, ResearchAgent, etc.)
- question: Question generation agents (ReAct architecture, separate base)
- chat: ``AgenticChatPipeline`` — single-loop chat on the agentic engine

Note: ``co_writer`` and ``book`` are independent top-level modules under
``deeptutor/`` (e.g. ``deeptutor.co_writer``, ``deeptutor.book``). They
still inherit from :class:`BaseAgent` defined here but are not part of
the ``deeptutor.agents`` package.

Usage:
    from deeptutor.agents.base_agent import BaseAgent

    class MyAgent(BaseAgent):
        async def process(self, *args, **kwargs):
            ...
"""

from .base_agent import BaseAgent
from .chat import ChatAgent, SessionManager

__all__ = ["BaseAgent", "ChatAgent", "SessionManager"]
