"""Configuration helpers for DeepTutor's LlamaIndex RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import os


VECTOR_PROFILE = "vector"
HYBRID_PROFILE = "hybrid"
SUPPORTED_RETRIEVAL_PROFILES = {VECTOR_PROFILE, HYBRID_PROFILE}


@dataclass(frozen=True)
class RetrievalConfig:
    """Runtime retrieval knobs for the LlamaIndex pipeline."""

    profile: str = HYBRID_PROFILE
    vector_top_k_multiplier: int = 2
    bm25_top_k_multiplier: int = 2
    fusion_num_queries: int = 1

    def candidate_top_k(self, top_k: int, multiplier: int) -> int:
        """Return the number of candidates to ask a child retriever for."""
        requested = max(1, int(top_k))
        return max(requested, requested * max(1, int(multiplier)))


def normalize_retrieval_profile(value: str | None) -> str:
    """Return a supported retrieval profile, defaulting to hybrid."""
    profile = (value or "").strip().lower()
    if profile in SUPPORTED_RETRIEVAL_PROFILES:
        return profile
    return HYBRID_PROFILE


def retrieval_config_from_env() -> RetrievalConfig:
    """Build retrieval config from environment variables.

    The default is intentionally ``hybrid``. If the optional LlamaIndex BM25
    integration is not installed, the retriever builder transparently falls
    back to plain vector retrieval.
    """

    return RetrievalConfig(
        profile=normalize_retrieval_profile(
            os.getenv("DEEPTUTOR_RAG_RETRIEVAL_PROFILE")
            or os.getenv("RAG_RETRIEVAL_PROFILE")
        )
    )


__all__ = [
    "HYBRID_PROFILE",
    "RetrievalConfig",
    "SUPPORTED_RETRIEVAL_PROFILES",
    "VECTOR_PROFILE",
    "normalize_retrieval_profile",
    "retrieval_config_from_env",
]
