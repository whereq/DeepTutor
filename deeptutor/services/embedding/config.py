# -*- coding: utf-8 -*-
"""
Embedding Configuration
=======================

Configuration management for embedding services backed by the project `.env`.
"""

from dataclasses import dataclass
import logging
import os
from typing import Optional

from deeptutor.services.config import get_env_store

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Embedding configuration dataclass."""

    model: str
    api_key: str
    base_url: Optional[str] = None
    binding: str = "openai"
    api_version: Optional[str] = None
    dim: int = 3072
    max_tokens: int = 8192
    request_timeout: int = 60
    batch_size: int = 10
    input_type: Optional[str] = None  # For task-aware embeddings (Cohere, Jina)

    # Optional provider-specific settings
    encoding_format: str = "float"
    normalized: bool = True
    truncate: bool = True
    late_chunking: bool = False


def _strip_value(value: Optional[str]) -> Optional[str]:
    """Remove leading/trailing whitespace and quotes from string."""
    if value is None:
        return None
    return value.strip().strip("\"'")


def _to_int(value: Optional[str], default: int) -> int:
    """Convert environment variable to int, fallback to default value on failure."""
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _to_bool(value: Optional[str], default: bool) -> bool:
    """Convert environment variable to bool."""
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def get_embedding_config() -> EmbeddingConfig:
    """
    Load embedding configuration.

    Returns:
        EmbeddingConfig: Configuration dataclass

    Raises:
        ValueError: If required configuration is missing
    """
    env_store = get_env_store()
    binding = _strip_value(env_store.get("EMBEDDING_BINDING", "openai"))
    model = _strip_value(env_store.get("EMBEDDING_MODEL"))
    api_key = _strip_value(env_store.get("EMBEDDING_API_KEY"))
    base_url = _strip_value(env_store.get("EMBEDDING_HOST"))
    api_version = _strip_value(env_store.get("EMBEDDING_API_VERSION"))
    dim_str = _strip_value(env_store.get("EMBEDDING_DIMENSION"))

    # Strict mode: Model is required
    if not model:
        raise ValueError(
            "EMBEDDING_MODEL not set. Please configure it in .env file or add a configuration in Settings"
        )

    # Check if API key is required
    # Local providers (Ollama, LM Studio) don't need API keys
    providers_without_key = ["ollama", "lm_studio"]
    requires_key = binding not in providers_without_key

    if requires_key and not api_key:
        raise ValueError(
            "EMBEDDING_API_KEY not set. Please configure it in .env file or add a configuration in Settings"
        )
    if not base_url:
        raise ValueError(
            "EMBEDDING_HOST not set. Please configure it in .env file or add a configuration in Settings"
        )

    # Get optional configuration
    dim = _to_int(dim_str, 3072)
    max_tokens = _to_int(_strip_value(os.getenv("EMBEDDING_MAX_TOKENS")), 8192)
    request_timeout = _to_int(_strip_value(os.getenv("EMBEDDING_REQUEST_TIMEOUT")), 60)
    batch_size = _to_int(_strip_value(os.getenv("EMBEDDING_BATCH_SIZE")), 10)
    input_type = _strip_value(os.getenv("EMBEDDING_INPUT_TYPE"))  # Optional

    # Provider-specific optional settings
    encoding_format = _strip_value(os.getenv("EMBEDDING_ENCODING_FORMAT")) or "float"
    normalized = _to_bool(_strip_value(os.getenv("EMBEDDING_NORMALIZED")), True)
    truncate = _to_bool(_strip_value(os.getenv("EMBEDDING_TRUNCATE")), True)
    late_chunking = _to_bool(_strip_value(os.getenv("EMBEDDING_LATE_CHUNKING")), False)

    return EmbeddingConfig(
        binding=binding,
        model=model,
        api_key=api_key or "",
        base_url=base_url,
        api_version=api_version,
        dim=dim,
        max_tokens=max_tokens,
        request_timeout=request_timeout,
        batch_size=max(1, batch_size),
        input_type=input_type,
        encoding_format=encoding_format,
        normalized=normalized,
        truncate=truncate,
        late_chunking=late_chunking,
    )
