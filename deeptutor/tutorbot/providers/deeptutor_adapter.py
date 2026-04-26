"""LLM provider adapter that reuses DeepTutor's LLM configuration.

When TutorBot runs in-process inside the DeepTutor server, this provider
reads api_key / model / base_url from DeepTutor's unified config and
delegates to the appropriate provider (OpenAICompat or Anthropic).
"""

from __future__ import annotations

from deeptutor.services.llm.provider_core.base import LLMProvider


def create_deeptutor_provider() -> LLMProvider:
    """Build a provider pre-configured from DeepTutor's LLMConfig."""
    from deeptutor.services.llm.provider_factory import get_runtime_provider

    return get_runtime_provider()
