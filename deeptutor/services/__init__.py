# -*- coding: utf-8 -*-
"""
Services Layer
==============

Unified service layer for DeepTutor providing:
- LLM client and configuration
- Embedding client and configuration
- RAG pipelines and components
- Prompt management
- Web Search providers
- System setup utilities
- Configuration loading

Usage:
    from deeptutor.services.llm import get_llm_client
    from deeptutor.services.embedding import get_embedding_client
    from deeptutor.services.rag import get_pipeline
    from deeptutor.services.prompt import get_prompt_manager
    from deeptutor.services.search import web_search
    from deeptutor.services.setup import init_user_directories
    from deeptutor.services.config import load_config_with_main

    # LLM
    llm = get_llm_client()
    response = await llm.complete("Hello, world!")

    # Embedding
    embed = get_embedding_client()
    vectors = await embed.embed(["text1", "text2"])

    # RAG
    pipeline = get_pipeline("raganything")
    result = await pipeline.search("query", "kb_name")

    # Prompt
    pm = get_prompt_manager()
    prompts = pm.load_prompts("guide", "tutor_agent")

    # Search
    result = web_search("What is AI?")
"""

# Note: rag and embedding modules are lazy-loaded via __getattr__
# to avoid importing heavy dependencies (lightrag, llama_index) at module load time
from . import config, llm, prompt, search, session, setup
from .path_service import PathService, get_path_service
from .session import BaseSessionManager

__all__ = [
    "llm",
    "embedding",
    "rag",
    "prompt",
    "search",
    "setup",
    "session",
    "config",
    "PathService",
    "get_path_service",
    "BaseSessionManager",
]


def __getattr__(name: str):
    """Lazy import for modules that depend on heavy libraries."""
    if name == "rag":
        from . import rag

        return rag
    if name == "embedding":
        from . import embedding

        return embedding
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
