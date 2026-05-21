"""OpenAI-compatible client factory and completion kwargs.

Lifted from chat's pipeline so any capability that wants a streaming LLM call
with tools can construct the same client + kwargs without re-implementing
provider gating, Azure detection, SSL bypass, or per-model token caps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from openai import AsyncAzureOpenAI, AsyncOpenAI

from deeptutor.services.config import load_system_settings
from deeptutor.services.llm import get_token_limit_kwargs, supports_tools

# Providers that don't reliably support OpenAI function-calling. The loop
# still runs without tool schemas — the model just produces prose.
_NATIVE_TOOL_BLOCKED_BINDINGS: frozenset[str] = frozenset(
    {"anthropic", "claude", "ollama", "lm_studio", "vllm", "llama_cpp"}
)


@dataclass(frozen=True)
class LLMClientConfig:
    """Provider-neutral handle for constructing an OpenAI-compatible client."""

    binding: str
    model: str | None
    api_key: str | None
    base_url: str | None
    api_version: str | None = None
    extra_headers: dict[str, str] | None = None


def build_openai_client(config: LLMClientConfig) -> Any:
    """Construct an ``AsyncOpenAI`` / ``AsyncAzureOpenAI`` client."""
    http_client = None
    if load_system_settings()["disable_ssl_verify"]:
        http_client = httpx.AsyncClient(verify=False)  # nosec B501
    default_headers = config.extra_headers or None
    if config.binding == "azure_openai" or (
        config.binding == "openai" and config.api_version
    ):
        return AsyncAzureOpenAI(
            api_key=config.api_key or "sk-no-key-required",
            azure_endpoint=config.base_url,
            api_version=config.api_version,
            http_client=http_client,
            default_headers=default_headers,
        )
    return AsyncOpenAI(
        api_key=config.api_key or "sk-no-key-required",
        base_url=config.base_url or None,
        http_client=http_client,
        default_headers=default_headers,
    )


def build_completion_kwargs(
    *,
    temperature: float,
    model: str | None,
    max_tokens: int,
) -> dict[str, Any]:
    """Compose temperature + per-model token-limit kwargs into one dict."""
    kwargs: dict[str, Any] = {"temperature": temperature}
    if model:
        kwargs.update(get_token_limit_kwargs(model, max_tokens))
    return kwargs


def can_use_native_tool_calling(*, binding: str, model: str | None) -> bool:
    """Whether the current provider supports OpenAI-style function calling."""
    if not supports_tools(binding, model):
        return False
    return binding not in _NATIVE_TOOL_BLOCKED_BINDINGS
