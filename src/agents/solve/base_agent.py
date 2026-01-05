#!/usr/bin/env python
"""
BaseAgent - Base class for all Agents, providing unified initialization, configuration handling, and LLM calling interface
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import sys
from typing import Any

from lightrag.llm.openai import openai_complete_if_cache

from .utils import PromptLoader
from .utils.token_tracker import TokenTracker

# Add project root to path for logs import
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
from src.core.core import get_agent_params
from src.core.logging import get_logger


class BaseAgent(ABC):
    """Base class for Agents, providing unified configuration and LLM calling interface"""

    def __init__(
        self,
        config: dict[str, Any],
        api_key: str,
        base_url: str,
        agent_name: str,
        use_prompt_loader: bool = True,  # Enable Prompt Loader by default
        token_tracker: TokenTracker | None = None,  # Token tracker
    ):
        """
        Initialize base Agent

        Args:
            config: Complete configuration dictionary
            api_key: API key
            base_url: API endpoint
            agent_name: Agent name, used to read dedicated configuration from config
            use_prompt_loader: Whether to use PromptLoader to load Prompts (default True, for backward compatibility)
        """
        self.config = config
        self.api_key = api_key
        self.base_url = base_url
        self.agent_name = agent_name

        # Initialize logger, used uniformly by all subclasses
        self.logger = get_logger(name=agent_name)

        # Load agent parameters from unified config (agents.yaml)
        self._agent_params = get_agent_params("solve")

        # Get dedicated configuration for this Agent
        self.agent_config = config.get("agents", {}).get(agent_name, {})

        # Get general LLM configuration
        self.llm_config = config.get("llm", {})

        # Agent status (enabled by default)
        self.enabled = True  # All agents are enabled by default, no configuration needed

        # Token tracker
        self.token_tracker = token_tracker

        # Prompt management
        self.use_prompt_loader = use_prompt_loader
        self.prompts = None

        if use_prompt_loader:
            # Initialize PromptLoader - read language setting from config
            # Language config is now unified in config/main.yaml system.language
            from src.core.core import parse_language

            language = config.get("system", {}).get("language", "zh")
            lang_code = parse_language(language)

            # Prompts are in src/agents/solve/prompts/
            prompts_dir = Path(__file__).parent / "prompts"
            self.prompt_loader = PromptLoader(base_dir=prompts_dir, language=lang_code)

            # Try to load Prompts for this Agent
            try:
                self.prompts = self.prompt_loader.load(agent_name)
                # Successfully loaded, log it
                if hasattr(self, "logger"):
                    self.logger.debug(f"[{agent_name}] Prompt configuration loaded from YAML")
            except FileNotFoundError as e:
                # If config file not found, log error but don't raise, allow Agent to use hardcoded Prompt
                self.prompts = None
                if hasattr(self, "logger"):
                    self.logger.warning(
                        f"[{agent_name}] Prompt config file not found: {e!s}, will use hardcoded Prompt"
                    )
            except Exception as e:
                # Other errors, log detailed error information
                self.prompts = None
                error_msg = f"[{agent_name}] Failed to load Prompt configuration: {e!s}, will use hardcoded Prompt"
                if hasattr(self, "logger"):
                    self.logger.error(error_msg, exc_info=True)
                else:
                    print(f"Error: {error_msg}")

    def get_model(self, key: str = "model") -> str:
        """
        Get model name

        Must be read from environment variable LLM_MODEL, raise error if not configured

        Args:
            key: Configuration key name (deprecated, kept for backward compatibility)

        Returns:
            Model name

        Raises:
            ValueError: If environment variable LLM_MODEL is not set
        """
        # 1. Try to get from agent's specific config
        if hasattr(self, "agent_config") and self.agent_config.get("model"):
            return self.agent_config["model"]
            
        # 2. Try to get from general LLM config (injected from MainSolver)
        if hasattr(self, "llm_config") and self.llm_config.get("model"):
            return self.llm_config["model"]

        # 3. Fallback to environment variable (for backward compatibility)
        env_model = os.getenv("LLM_MODEL")
        if env_model:
            return env_model
            
        raise ValueError(
            f"Error: Model not configured for agent {self.agent_name}\n"
            f"Please configure LLM_MODEL in .env OR activate a provider."
        )

    def get_temperature(self) -> float:
        """
        Get temperature parameter from unified config (agents.yaml)

        Returns:
            Temperature value from agents.yaml
        """
        return self._agent_params["temperature"]

    def get_max_tokens(self) -> int:
        """
        Get maximum token count from unified config (agents.yaml)

        Returns:
            Maximum token count from agents.yaml
        """
        return self._agent_params["max_tokens"]

    def get_max_retries(self) -> int:
        """
        Get maximum retry count

        Returns:
            Retry count
        """
        return self.agent_config.get("max_retries", self.llm_config.get("max_retries", 3))

    async def call_llm(
        self,
        user_prompt: str,
        system_prompt: str,
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
        model: str | None = None,
        verbose: bool = True,
        stage: str | None = None,
    ) -> str:
        """
        Unified interface for calling LLM

        Args:
            user_prompt: User prompt
            system_prompt: System prompt
            response_format: Response format (e.g., {"type": "json_object"})
            temperature: Temperature parameter (optional, uses config by default)
            model: Model name (optional, uses config by default)
            verbose: Whether to print raw LLM output (default True)

        Returns:
            LLM response text
        """
        model = model or self.get_model()
        temperature = temperature if temperature is not None else self.get_temperature()
        max_tokens = self.get_max_tokens()

        kwargs = {
            "model": model,
            "prompt": user_prompt,
            "system_prompt": system_prompt,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": temperature,
        }

        if response_format:
            kwargs["response_format"] = response_format

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        stage_label = stage or self.agent_name
        if hasattr(self.logger, "log_llm_input"):
            self.logger.log_llm_input(
                agent_name=self.agent_name,
                stage=stage_label,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={"model": model, "temperature": temperature, "max_tokens": max_tokens},
            )

        # Create TokenTracker wrapper (if token_tracker is provided)
        token_tracker_wrapper = None
        if self.token_tracker:

            class TokenTrackerWrapper:
                def __init__(self, tracker, agent_name, stage):
                    self.tracker = tracker
                    self.agent_name = agent_name
                    self.stage = stage
                    self.usage = None

                def add_usage(self, token_counts):
                    self.usage = token_counts
                    self.tracker.add_usage(
                        agent_name=self.agent_name,
                        stage=self.stage,
                        model=model,
                        token_counts=token_counts,
                    )

            token_tracker_wrapper = TokenTrackerWrapper(
                self.token_tracker, self.agent_name, stage_label
            )
            kwargs["token_tracker"] = token_tracker_wrapper

        response = await openai_complete_if_cache(**kwargs)

        # If token_tracker exists but didn't get usage info from API, try using more precise method
        if self.token_tracker and token_tracker_wrapper and not token_tracker_wrapper.usage:
            # Check if advanced tracking is supported (using tiktoken or litellm)
            if (
                hasattr(self.token_tracker, "add_usage")
                and len(self.token_tracker.add_usage.__code__.co_varnames) > 6
            ):
                # Advanced tracker: supports system_prompt, user_prompt, response_text parameters
                self.token_tracker.add_usage(
                    agent_name=self.agent_name,
                    stage=stage_label,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_text=response,
                )
            else:
                # Basic tracker: use estimation method
                estimated_prompt_tokens = len(system_prompt.split()) + len(user_prompt.split())
                estimated_completion_tokens = len(response.split())
                self.token_tracker.add_usage(
                    agent_name=self.agent_name,
                    stage=stage_label,
                    model=model,
                    prompt_tokens=int(estimated_prompt_tokens * 1.3),
                    completion_tokens=int(estimated_completion_tokens * 1.3),
                )

        if hasattr(self.logger, "log_llm_output"):
            self.logger.log_llm_output(
                agent_name=self.agent_name,
                stage=stage_label,
                response=response,
                metadata={"length": len(response)},
            )

        return response

    def is_enabled(self) -> bool:
        """
        Check if Agent is enabled

        Returns:
            Whether enabled
        """
        return self.enabled

    def get_prompt(self, prompt_type: str = "system") -> str | None:
        """
        Get Prompt (if using PromptLoader)

        Args:
            prompt_type: Prompt type ('system' | 'user_template' | 'output_format')

        Returns:
            Prompt content, returns None if not found
        """
        if self.prompts and prompt_type in self.prompts:
            return self.prompts[prompt_type]
        return None

    def has_prompts(self) -> bool:
        """
        Check if Prompts have been loaded

        Returns:
            Whether loaded
        """
        return self.prompts is not None

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """
        Main processing logic of Agent (must be implemented by subclasses)

        Returns:
            Processing result
        """

    def __repr__(self) -> str:
        """String representation of Agent"""
        return f"{self.__class__.__name__}(name={self.agent_name}, enabled={self.enabled})"
