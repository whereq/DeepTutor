#!/usr/bin/env python
"""
BaseGuideAgent - Base class for Guided Learning Agents
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import sys
from typing import Any

# Add project root to path for logs import
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.core.core import get_agent_params, load_config_with_main
from src.core.logging import LLMStats, get_logger


class BaseGuideAgent(ABC):
    """Base class for Guided Learning Agents."""

    # Shared stats tracker for all guide agents
    _shared_stats: LLMStats | None = None

    def __init__(self, api_key: str, base_url: str, agent_name: str, language: str = "zh"):
        """
        Initialize base Agent.

        Args:
            api_key: API key
            base_url: API endpoint
            agent_name: Agent name
            language: Language setting ('zh' | 'en')
        """
        self.api_key = api_key
        self.base_url = base_url
        self.agent_name = agent_name
        self.language = language

        # Load agent parameters from unified config (agents.yaml)
        self._agent_params = get_agent_params("guide")

        # Initialize logger (from config)
        try:
            config = load_config_with_main("guide_config.yaml", _project_root)
            log_dir = config.get("paths", {}).get("user_log_dir") or config.get("logging", {}).get(
                "log_dir"
            )
            self.logger = get_logger(f"Guide.{agent_name}", log_dir=log_dir)
        except Exception:
            # Fallback logger
            self.logger = get_logger(f"Guide.{agent_name}")

        # Load prompts
        self.prompts = self._load_prompts()

    @classmethod
    def get_stats(cls) -> LLMStats:
        """Get or create shared stats tracker."""
        if cls._shared_stats is None:
            cls._shared_stats = LLMStats(module_name="GuidedLearning")
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

    def _load_prompts(self) -> dict[str, str] | None:
        """Load Agent's prompt configuration."""
        import yaml

        # Get prompts directory: from agents/base_guide_agent.py -> guide/prompts/
        prompts_dir = Path(__file__).parent.parent / "prompts"

        # Map language to directory: 'en' or 'english' -> 'en', otherwise -> 'zh'
        if self.language.lower() in ["en", "english"]:
            lang_dir = "en"
        else:
            lang_dir = "zh"

        prompt_file = prompts_dir / lang_dir / f"{self.agent_name}.yaml"

        if prompt_file.exists():
            try:
                with open(prompt_file, encoding="utf-8") as f:
                    prompts = yaml.safe_load(f)
                    self.logger.info(f"Loaded prompts: {self.agent_name} ({self.language})")
                    return prompts
            except Exception as e:
                self.logger.warning(f"Failed to load prompts {prompt_file}: {e}")
                return None
        else:
            self.logger.warning(f"Prompt file not found: {prompt_file}")
            return None

    def get_model(self) -> str:
        """Get model name."""
        model = os.getenv("LLM_MODEL")
        if not model:
            raise ValueError("Environment variable LLM_MODEL not set")
        return model

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
            response_format: Response format
            temperature: Temperature parameter (uses config default if None)
            max_tokens: Maximum tokens (uses config default if None)

        Returns:
            LLM response text
        """
        from lightrag.llm.openai import openai_complete_if_cache

        model = self.get_model()

        # Use parameters from unified config (agents.yaml) if not explicitly provided
        if temperature is None:
            temperature = self._agent_params["temperature"]
        if max_tokens is None:
            max_tokens = self._agent_params["max_tokens"]

        kwargs = {
            "model": model,
            "prompt": user_prompt,
            "system_prompt": system_prompt,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = await openai_complete_if_cache(**kwargs)

        # Track token usage
        stats = self.get_stats()
        stats.add_call(
            model=model, system_prompt=system_prompt, user_prompt=user_prompt, response=response
        )

        return response

    def get_prompt(self, prompt_type: str = "system") -> str | None:
        """Get prompt"""
        if self.prompts and prompt_type in self.prompts:
            return self.prompts[prompt_type]
        return None

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Main processing logic of the agent (must be implemented by subclasses)"""
