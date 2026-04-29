"""Embedding endpoint URL helpers.

Embedding adapters post to the configured URL exactly. These helpers keep the
user-visible Settings value aligned with provider-specific endpoint paths.
"""

from __future__ import annotations

from urllib.parse import urlparse

EMBEDDING_PROVIDER_ALIASES = {
    "google": "openai",
    "gemini": "openai",
    "huggingface": "custom",
    "lm_studio": "vllm",
    "llama_cpp": "vllm",
    "openai_compatible": "custom",
}

EMBEDDING_PROVIDER_LABELS = {
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "jina": "Jina",
    "vllm": "vLLM / LM Studio",
    "siliconflow": "SiliconFlow",
    "ollama": "Ollama",
    "cohere": "Cohere",
}

EMBEDDING_PROVIDER_DEFAULT_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/embeddings",
    "openrouter": "https://openrouter.ai/api/v1/embeddings",
    "cohere": "https://api.cohere.com/v2/embed",
    "jina": "https://api.jina.ai/v1/embeddings",
    "ollama": "http://localhost:11434/api/embed",
    "vllm": "http://localhost:8000/v1/embeddings",
    "siliconflow": "https://api.siliconflow.cn/v1/embeddings",
    "aliyun": (
        "https://dashscope.aliyuncs.com/api/v1/services/embeddings/"
        "multimodal-embedding/multimodal-embedding"
    ),
}

EMBEDDING_PROVIDERS_REQUIRING_EMBEDDINGS_PATH = {
    "openai",
    "openrouter",
    "jina",
    "vllm",
    "siliconflow",
}


def canonical_embedding_provider_name(name: str | None) -> str:
    value = str(name or "").strip().lower().replace("-", "_")
    return EMBEDDING_PROVIDER_ALIASES.get(value, value)


def _same_origin_url(url: str, path: str) -> str:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    return url.rstrip("/") + path


def normalize_embedding_endpoint_for_display(provider: str | None, base_url: str | None) -> str:
    """Return the full endpoint URL that should be shown and saved in Settings."""
    provider_name = canonical_embedding_provider_name(provider)
    url = str(base_url or "").strip()
    if not url:
        return EMBEDDING_PROVIDER_DEFAULT_ENDPOINTS.get(provider_name, "")

    trimmed = url.rstrip("/")
    if provider_name in EMBEDDING_PROVIDERS_REQUIRING_EMBEDDINGS_PATH:
        if trimmed.endswith("/embeddings"):
            return trimmed
        if trimmed.endswith("/v1"):
            return f"{trimmed}/embeddings"
    if provider_name == "ollama":
        if trimmed.endswith("/api/embed"):
            return trimmed
        if trimmed.endswith("/api"):
            return f"{trimmed}/embed"
        parsed = urlparse(trimmed if "://" in trimmed else f"http://{trimmed}")
        if parsed.scheme and parsed.netloc and parsed.path in {"", "/"}:
            return _same_origin_url(trimmed, "/api/embed")
    if provider_name == "cohere":
        if trimmed.endswith("/embed"):
            return trimmed
        if trimmed.endswith("/v2"):
            return f"{trimmed}/embed"
    return url


def embedding_endpoint_validation_error(provider: str | None, base_url: str | None) -> str | None:
    """Validate that known providers use the exact endpoint path shown to users."""
    provider_name = canonical_embedding_provider_name(provider)
    url = str(base_url or "").strip()
    if not url:
        return "Embedding endpoint URL is empty."

    parsed = urlparse(url if "://" in url else f"http://{url}")
    path = parsed.path.rstrip("/")
    label = EMBEDDING_PROVIDER_LABELS.get(provider_name, provider_name or "Embedding provider")

    if provider_name in EMBEDDING_PROVIDERS_REQUIRING_EMBEDDINGS_PATH:
        if not path.endswith("/embeddings"):
            return f"{label} embedding endpoint must end with /embeddings."
    elif provider_name == "ollama":
        if path != "/api/embed":
            return "Ollama embedding endpoint must be the full /api/embed URL."
    elif provider_name == "cohere":
        if not path.endswith("/embed"):
            return "Cohere embedding endpoint must end with /embed."

    return None
