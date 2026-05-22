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
from deeptutor.services.provider_registry import find_by_name

# Providers that don't reliably support OpenAI function-calling. The loop
# still runs without tool schemas — the model just produces prose.
_NATIVE_TOOL_BLOCKED_BINDINGS: frozenset[str] = frozenset(
    {"anthropic", "claude", "ollama", "lm_studio", "vllm", "llama_cpp"}
)
_THINKING_STYLE_MAP = {
    "thinking_type": lambda enabled: {"thinking": {"type": "enabled" if enabled else "disabled"}},
    "enable_thinking": lambda enabled: {"enable_thinking": enabled},
    "reasoning_split": lambda enabled: {"reasoning_split": enabled},
}
_THINKING_DISABLED_BY_DEFAULT: tuple[tuple[str, str], ...] = (("deepseek", "deepseek-v4-flash"),)


@dataclass(frozen=True)
class LLMClientConfig:
    """Provider-neutral handle for constructing an OpenAI-compatible client."""

    binding: str
    model: str | None
    api_key: str | None
    base_url: str | None
    api_version: str | None = None
    extra_headers: dict[str, str] | None = None
    reasoning_effort: str | None = None


def build_openai_client(config: LLMClientConfig) -> Any:
    """Construct an ``AsyncOpenAI`` / ``AsyncAzureOpenAI`` client."""
    http_client = None
    if load_system_settings()["disable_ssl_verify"]:
        http_client = httpx.AsyncClient(verify=False)  # nosec B501
    default_headers = config.extra_headers or None
    if config.binding == "azure_openai" or (config.binding == "openai" and config.api_version):
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
    binding: str | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Compose temperature + per-model token-limit kwargs into one dict."""
    kwargs: dict[str, Any] = {"temperature": temperature}
    if model:
        kwargs.update(get_token_limit_kwargs(model, max_tokens))
    kwargs.update(
        build_provider_extra_kwargs(
            binding=binding,
            model=model,
            reasoning_effort=reasoning_effort,
        )
    )
    return kwargs


def _disable_thinking_by_default(binding: str | None, model: str | None) -> bool:
    normalized_model = (model or "").strip().lower()
    normalized_binding = (binding or "").strip().lower()
    return any(
        normalized_binding == provider and pattern in normalized_model
        for provider, pattern in _THINKING_DISABLED_BY_DEFAULT
    )


def build_provider_extra_kwargs(
    *,
    binding: str | None,
    model: str | None,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    """Return provider-specific kwargs for raw OpenAI-compatible agent calls.

    Agentic pipelines stream directly through ``AsyncOpenAI`` so tests can
    inject scripted clients. This helper mirrors the small provider-normalized
    subset that is required before those raw calls: reasoning effort and
    provider-specific thinking flags.
    """
    spec = find_by_name(binding)
    model_name = model or ""
    resolved_effort = reasoning_effort
    if resolved_effort is None and spec and spec.reasoning_model_patterns:
        model_lower = model_name.lower()
        if any(pattern.lower() in model_lower for pattern in spec.reasoning_model_patterns):
            resolved_effort = "high"

    semantic_effort: str | None = None
    if isinstance(resolved_effort, str):
        semantic_effort = resolved_effort.lower()
        if semantic_effort == "minimum":
            semantic_effort = "minimal"

    wire_effort = resolved_effort
    if spec and spec.name == "dashscope" and semantic_effort == "minimal":
        wire_effort = "minimum"

    kwargs: dict[str, Any] = {}
    if wire_effort and not (spec and spec.thinking_style and semantic_effort == "minimal"):
        kwargs["reasoning_effort"] = wire_effort

    if spec and spec.thinking_style and resolved_effort is not None:
        thinking_enabled = semantic_effort != "minimal"
        extra = _THINKING_STYLE_MAP.get(spec.thinking_style, lambda _enabled: None)(
            thinking_enabled
        )
        if extra:
            kwargs.setdefault("extra_body", {}).update(extra)
    elif spec and spec.thinking_style and _disable_thinking_by_default(spec.name, model_name):
        extra = _THINKING_STYLE_MAP.get(spec.thinking_style, lambda _enabled: None)(False)
        if extra:
            kwargs.setdefault("extra_body", {}).update(extra)
    return kwargs


def can_use_native_tool_calling(*, binding: str, model: str | None) -> bool:
    """Whether the current provider supports OpenAI-style function calling."""
    if not supports_tools(binding, model):
        return False
    return binding not in _NATIVE_TOOL_BLOCKED_BINDINGS
