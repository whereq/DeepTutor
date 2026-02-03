# -*- coding: utf-8 -*-
"""
Memory Agent
============

LLM-powered agent for analyzing learning events and deciding what to record
in the personalization memory.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent
from src.core.event_bus import Event

logger = logging.getLogger(__name__)


@dataclass
class MemoryDecision:
    """
    Decision made by MemoryAgent about what to record.

    Attributes:
        action: One of "write_daily", "update_memory", "both", or "skip"
        daily_content: Content to write to daily note (if action includes daily)
        memory_updates: Updates to apply to long-term memory
        reasoning: Agent's reasoning for the decision
    """

    action: str  # "write_daily" | "update_memory" | "both" | "skip"
    daily_content: str = ""
    memory_updates: Dict[str, List[str]] = None
    reasoning: str = ""

    def __post_init__(self):
        if self.memory_updates is None:
            self.memory_updates = {
                "preferences": [],
                "weak_points": [],
                "milestones": [],
            }

    @classmethod
    def skip(cls, reasoning: str = "") -> "MemoryDecision":
        """Create a skip decision."""
        return cls(action="skip", reasoning=reasoning)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryDecision":
        """Create from dictionary (parsed JSON)."""
        return cls(
            action=data.get("action", "skip"),
            daily_content=data.get("daily_content", ""),
            memory_updates=data.get("memory_updates", {}),
            reasoning=data.get("reasoning", ""),
        )


class MemoryAgent(BaseAgent):
    """
    Agent that analyzes learning events and decides what to record.

    This agent is called after SOLVE_COMPLETE or QUESTION_COMPLETE events
    to analyze the interaction and decide:
    1. Whether to write a daily note entry
    2. Whether to update long-term memory (preferences, weak points, milestones)
    3. What content to write

    The agent uses an LLM to make intelligent decisions about what's worth
    remembering for personalization purposes.
    """

    def __init__(
        self,
        language: str = "en",
        temperature: float = 0.3,
        **kwargs,
    ):
        """
        Initialize MemoryAgent.

        Args:
            language: Language setting ('en' or 'zh')
            temperature: LLM temperature for analysis
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            module_name="personalization",
            agent_name="memory_agent",
            language=language,
            **kwargs,
        )
        self._temperature = temperature

    def get_temperature(self) -> float:
        """Override to use custom temperature."""
        return self._temperature

    async def process(
        self,
        event: Event,
        current_memory: str = "",
        recent_notes: str = "",
    ) -> MemoryDecision:
        """
        Analyze an event and decide what to record.

        Args:
            event: The learning event to analyze
            current_memory: Current content of MEMORY.md
            recent_notes: Recent daily notes for context

        Returns:
            MemoryDecision with action and content to record
        """
        # Build the analysis prompt
        system_prompt = self.get_prompt("system", "")
        if not system_prompt:
            logger.warning("No system prompt found for MemoryAgent")
            return MemoryDecision.skip("No prompt configured")

        # Format the event data
        event_context = self._format_event(event)

        # Build user prompt
        user_template = self.get_prompt("analyze", "")
        if not user_template:
            logger.warning("No analyze prompt found for MemoryAgent")
            return MemoryDecision.skip("No analyze prompt configured")

        user_prompt = user_template.format(
            event_type=event.type.value if hasattr(event.type, "value") else event.type,
            event_context=event_context,
            current_memory=current_memory or "(No existing memory)",
            recent_notes=recent_notes or "(No recent notes)",
        )

        try:
            # Call LLM
            response = await self.call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                verbose=False,
                stage="memory_analysis",
            )

            # Parse response
            decision = self._parse_response(response)
            return decision

        except Exception as e:
            logger.error(f"MemoryAgent processing failed: {e}")
            return MemoryDecision.skip(f"Processing error: {str(e)}")

    def _format_event(self, event: Event) -> str:
        """Format event data for the prompt."""
        parts = [
            f"Task ID: {event.task_id}",
            f"User Input: {event.user_input[:500]}..." if len(event.user_input) > 500 else f"User Input: {event.user_input}",
            f"Agent Output: {event.agent_output[:1000]}..." if len(event.agent_output) > 1000 else f"Agent Output: {event.agent_output}",
            f"Tools Used: {', '.join(event.tools_used) if event.tools_used else 'None'}",
            f"Success: {event.success}",
        ]

        if event.metadata:
            # Add selected metadata
            if "difficulty" in event.metadata:
                parts.append(f"Difficulty: {event.metadata['difficulty']}")
            if "topic" in event.metadata:
                parts.append(f"Topic: {event.metadata['topic']}")

        return "\n".join(parts)

    def _parse_response(self, response: str) -> MemoryDecision:
        """Parse LLM response into MemoryDecision."""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            return MemoryDecision.from_dict(data)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse MemoryAgent response as JSON: {e}")
            # Try to extract action from text
            response_lower = response.lower()
            if "skip" in response_lower:
                return MemoryDecision.skip("Unparseable response, defaulting to skip")
            elif "write_daily" in response_lower:
                return MemoryDecision(
                    action="write_daily",
                    daily_content=response,
                    reasoning="Extracted from unparseable response",
                )
            else:
                return MemoryDecision.skip("Could not parse response")

    async def analyze_for_preferences(
        self,
        user_input: str,
        agent_output: str,
    ) -> Optional[List[str]]:
        """
        Quick analysis to extract potential user preferences.

        Args:
            user_input: User's question or request
            agent_output: Agent's response

        Returns:
            List of detected preferences, or None if none detected
        """
        system_prompt = self.get_prompt("preferences_extraction", "")
        if not system_prompt:
            return None

        user_prompt = f"""Analyze this interaction and extract any user preferences:

User: {user_input[:500]}
Response: {agent_output[:500]}

Return a JSON array of detected preferences, or empty array if none."""

        try:
            response = await self.call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                verbose=False,
            )
            data = json.loads(response)
            return data.get("preferences", [])
        except Exception as e:
            logger.debug(f"Preference extraction failed: {e}")
            return None
