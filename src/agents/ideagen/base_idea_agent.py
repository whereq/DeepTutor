"""
Idea Generation Agent Base Class
Provides unified LLM call interface and base functionality.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import sys
from typing import Any

# Add project root to path for logs import
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from lightrag.llm.openai import openai_complete_if_cache

from src.core.core import (
    get_agent_params,
    get_llm_config,
    get_token_limit_kwargs,
    load_config_with_main,
)
from src.core.logging import LLMStats, get_logger


class BaseIdeaAgent(ABC):
    """Base class for Idea Generation Agents."""

    # Shared stats tracker for all ideagen agents
    _shared_stats: LLMStats | None = None

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        """
        Initialize Agent.

        Args:
            api_key: API key
            base_url: API endpoint
            model: Model name
        """
        # Load agent parameters from unified config (agents.yaml)
        self._agent_params = get_agent_params("ideagen")

        # Get config from environment
        try:
            llm_config = get_llm_config()
            self.api_key = api_key or llm_config["api_key"]
            self.base_url = base_url or llm_config["base_url"]
            self.model = model or llm_config["model"]
        except ValueError as e:
            raise ValueError(f"LLM config error: {e!s}")

        # Initialize logger (from config)
        try:
            config = load_config_with_main(
                "solve_config.yaml", _project_root
            )  # Use any config to get main.yaml
            log_dir = config.get("paths", {}).get("user_log_dir") or config.get("logging", {}).get(
                "log_dir"
            )
            self.logger = get_logger("IdeaGen", log_dir=log_dir)
        except Exception:
            # Fallback logger
            self.logger = get_logger("IdeaGen")

    @classmethod
    def get_stats(cls) -> LLMStats:
        """Get or create shared stats tracker."""
        if cls._shared_stats is None:
            cls._shared_stats = LLMStats(module_name="IdeaGen")
        return cls._shared_stats

    @classmethod
    def reset_stats(cls):
        """Reset shared stats."""
        if cls._shared_stats:
            cls._shared_stats.reset()

    @classmethod
    def print_stats(cls):
        """Print stats summary."""
        if cls._shared_stats:
            cls._shared_stats.print_summary()

    async def call_llm(
        self,
        user_prompt: str,
        system_prompt: str,
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Unified LLM call interface.

        Args:
            user_prompt: User prompt
            system_prompt: System prompt
            response_format: Response format (e.g., {"type": "json_object"})
            temperature: Temperature parameter (uses config default if None)
            max_tokens: Maximum tokens (uses config default if None)

        Returns:
            LLM response text
        """
        # Use parameters from unified config (agents.yaml) if not explicitly provided
        if temperature is None:
            temperature = self._agent_params["temperature"]
        if max_tokens is None:
            max_tokens = self._agent_params["max_tokens"]

        kwargs = {
            "model": self.model,
            "prompt": user_prompt,
            "system_prompt": system_prompt,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": temperature,
        }

        if max_tokens:
            kwargs.update(get_token_limit_kwargs(self.model, max_tokens))

        if response_format:
            kwargs["response_format"] = response_format

        response = await openai_complete_if_cache(**kwargs)

        # Track token usage
        stats = self.get_stats()
        stats.add_call(
            model=self.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response=response,
        )

        return response

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Main processing logic of the agent (must be implemented by subclasses)"""
