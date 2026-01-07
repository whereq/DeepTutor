"""
Adapters Package
================

Embedding adapters for different providers.
"""

from .base import BaseEmbeddingAdapter, EmbeddingRequest, EmbeddingResponse
from .openai_compatible import OpenAICompatibleEmbeddingAdapter
from .jina import JinaEmbeddingAdapter
from .cohere import CohereEmbeddingAdapter
from .ollama import OllamaEmbeddingAdapter

__all__ = [
    "BaseEmbeddingAdapter",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "OpenAICompatibleEmbeddingAdapter",
    "JinaEmbeddingAdapter",
    "CohereEmbeddingAdapter",
    "OllamaEmbeddingAdapter",
]
