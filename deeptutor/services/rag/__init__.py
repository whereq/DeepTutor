"""RAG service exports."""

from .factory import (
    DEFAULT_PROVIDER,
    get_pipeline,
    has_pipeline,
    list_pipelines,
    normalize_provider_name,
    register_pipeline,
)
from .pipeline import RAGPipeline
from .service import RAGService
from .types import Chunk, Document, SearchResult


def __getattr__(name: str):
    """Lazy import pipeline implementation classes."""
    if name == "LlamaIndexPipeline":
        from .pipelines.llamaindex import LlamaIndexPipeline

        return LlamaIndexPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "RAGService",
    "Document",
    "Chunk",
    "SearchResult",
    "RAGPipeline",
    "get_pipeline",
    "list_pipelines",
    "register_pipeline",
    "has_pipeline",
    "normalize_provider_name",
    "DEFAULT_PROVIDER",
    "LlamaIndexPipeline",
]
