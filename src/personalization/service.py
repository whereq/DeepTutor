# -*- coding: utf-8 -*-
"""
Personalization Service
=======================

Service layer that coordinates personalization memory management.
Listens to events, invokes MemoryAgent, and provides preference access.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.core.event_bus import Event, EventType, get_event_bus
from src.services.path_service import get_path_service

from .memory import LearningMemory, get_learning_memory
from .memory_agent import MemoryAgent, MemoryDecision

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Service for managing personalization memory.

    Responsibilities:
    1. Subscribe to EventBus events (SOLVE_COMPLETE, QUESTION_COMPLETE)
    2. Invoke MemoryAgent to analyze events
    3. Write memory updates to storage
    4. Provide preference context for prompt injection

    Usage:
        # Get singleton instance
        service = get_personalization_service()

        # Start the service (call during app startup)
        await service.start()

        # Get preference for prompt injection
        preference = service.get_preference_for_prompt()

        # Stop the service (call during app shutdown)
        await service.stop()
    """

    _instance: Optional["PersonalizationService"] = None
    _initialized: bool = False

    def __new__(cls) -> "PersonalizationService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if PersonalizationService._initialized:
            return

        self._running = False
        self._memory: Optional[LearningMemory] = None
        self._agent: Optional[MemoryAgent] = None
        self._config: Dict[str, Any] = {}
        self._language = "en"

        # Load configuration
        self._load_config()

        PersonalizationService._initialized = True
        logger.debug("PersonalizationService initialized")

    def _load_config(self) -> None:
        """Load configuration from config/memory.yaml."""
        config_path = get_path_service().project_root / "config" / "memory.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
                logger.debug(f"Loaded memory config: {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load memory config: {e}")
                self._config = {}
        else:
            logger.debug("No memory config found, using defaults")
            self._config = {}

    @property
    def auto_update(self) -> bool:
        """Check if auto-update is enabled."""
        return self._config.get("memory", {}).get("auto_update", True)

    @property
    def recent_days(self) -> int:
        """Get number of recent days for context."""
        return self._config.get("memory", {}).get("recent_days", 7)

    @property
    def max_preference_length(self) -> int:
        """Get maximum preference length for prompt injection."""
        return self._config.get("memory", {}).get("max_preference_length", 2000)

    async def start(self) -> None:
        """
        Start the personalization service.

        This should be called during application startup.
        Subscribes to EventBus and initializes components.
        """
        if self._running:
            logger.debug("PersonalizationService already running")
            return

        self._running = True

        # Initialize memory
        self._memory = get_learning_memory()

        # Initialize agent
        llm_config = self._config.get("llm", {})
        temperature = llm_config.get("temperature", 0.3)
        self._agent = MemoryAgent(
            language=self._language,
            temperature=temperature,
        )

        # Subscribe to events
        if self.auto_update:
            event_bus = get_event_bus()
            event_bus.subscribe(EventType.SOLVE_COMPLETE, self._handle_event)
            event_bus.subscribe(EventType.QUESTION_COMPLETE, self._handle_event)
            logger.info("PersonalizationService started, subscribed to events")
        else:
            logger.info("PersonalizationService started (auto-update disabled)")

    async def stop(self) -> None:
        """
        Stop the personalization service.

        This should be called during application shutdown.
        """
        if not self._running:
            return

        self._running = False

        # Unsubscribe from events
        if self.auto_update:
            event_bus = get_event_bus()
            event_bus.unsubscribe(EventType.SOLVE_COMPLETE, self._handle_event)
            event_bus.unsubscribe(EventType.QUESTION_COMPLETE, self._handle_event)

        logger.info("PersonalizationService stopped")

    async def _handle_event(self, event: Event) -> None:
        """
        Handle a learning event from EventBus.

        This is called asynchronously when SOLVE_COMPLETE or QUESTION_COMPLETE
        events are published. It analyzes the event and updates memory as needed.

        Args:
            event: The event to process
        """
        if not self._running or not self._agent or not self._memory:
            return

        try:
            logger.debug(f"Processing event: {event.type} (task_id={event.task_id})")

            # Get current context
            current_memory = self._memory.read_memory()
            recent_notes = self._format_recent_notes()

            # Analyze event with MemoryAgent
            decision = await self._agent.process(
                event=event,
                current_memory=current_memory,
                recent_notes=recent_notes,
            )

            # Apply decision
            await self._apply_decision(decision)

            logger.debug(f"Event processed: action={decision.action}")

        except Exception as e:
            logger.error(f"Failed to process event: {e}", exc_info=True)

    async def _apply_decision(self, decision: MemoryDecision) -> None:
        """
        Apply a MemoryDecision to storage.

        Args:
            decision: The decision from MemoryAgent
        """
        if decision.action == "skip":
            return

        if not self._memory:
            return

        # Write daily note
        if decision.action in ("write_daily", "both") and decision.daily_content:
            self._memory.append_to_daily_note(decision.daily_content)
            logger.debug("Daily note updated")

        # Update long-term memory
        if decision.action in ("update_memory", "both") and decision.memory_updates:
            updates = decision.memory_updates

            if updates.get("preferences"):
                self._memory.append_to_section("preferences", updates["preferences"])
                logger.debug(f"Added {len(updates['preferences'])} preferences")

            if updates.get("weak_points"):
                self._memory.append_to_section("weak_points", updates["weak_points"])
                logger.debug(f"Added {len(updates['weak_points'])} weak points")

            if updates.get("milestones"):
                self._memory.append_to_section("milestones", updates["milestones"])
                logger.debug(f"Added {len(updates['milestones'])} milestones")

    def _format_recent_notes(self) -> str:
        """Format recent notes for context."""
        if not self._memory:
            return ""

        notes = self._memory.get_recent_notes(self.recent_days)
        if not notes:
            return ""

        parts = []
        for date_str, content in notes.items():
            # Truncate each note
            summary = content[:300].replace("\n", " ")
            if len(content) > 300:
                summary += "..."
            parts.append(f"[{date_str}]: {summary}")

        return "\n".join(parts)

    # =========================================================================
    # Public Interface for Preference Access
    # =========================================================================

    def get_preference_for_prompt(self) -> str:
        """
        Get formatted preference context for prompt injection.

        This method is called by agents (ResponseAgent, GenerateAgent) to get
        user preferences for inclusion in prompts.

        Returns:
            Formatted preference string, or empty string if no preferences.
        """
        if not self._memory:
            self._memory = get_learning_memory()

        return self._memory.get_preference_context(self.max_preference_length)

    def get_full_context(self) -> str:
        """
        Get full context including preferences and recent notes.

        Returns:
            Full context string for advanced personalization.
        """
        if not self._memory:
            self._memory = get_learning_memory()

        return self._memory.get_full_context(
            recent_days=self.recent_days,
            max_length=self.max_preference_length * 2,
        )

    def set_language(self, language: str) -> None:
        """
        Set the language for the service.

        Args:
            language: Language code ('en' or 'zh')
        """
        self._language = language
        if self._agent:
            self._agent.language = language

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        if cls._instance is not None:
            cls._instance._running = False
        cls._instance = None
        cls._initialized = False


# Module-level singleton accessor
_personalization_service: Optional[PersonalizationService] = None


def get_personalization_service() -> PersonalizationService:
    """
    Get the singleton PersonalizationService instance.

    Returns:
        The global PersonalizationService instance.
    """
    global _personalization_service
    if _personalization_service is None:
        _personalization_service = PersonalizationService()
    return _personalization_service
