#!/usr/bin/env python
"""
RAG Query Tool - Plugin-based RAG system
Supports multiple RAG implementations through a simple plugin system
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / "DeepTutor.env", override=False)
load_dotenv(project_root / ".env", override=False)

from src.rag.plugin_loader import get_plugin, list_plugins, has_plugin


from src.rag.plugin_loader import get_plugin, list_plugins, has_plugin


# Default RAG provider (can be overridden via environment variable)
DEFAULT_RAG_PROVIDER = os.getenv("RAG_PROVIDER", "lightrag")


async def rag_search(
    query: str,
    kb_name: str | None = None,
    mode: str = "hybrid",
    provider: str | None = None,
    **kwargs,
) -> dict:
    """
    Query knowledge base using configurable RAG provider.

    Args:
        query: Query question
        kb_name: Knowledge base name (optional, defaults to default knowledge base)
        mode: Query mode (e.g., "hybrid", "local", "global", "naive")
        provider: RAG provider to use (defaults to RAG_PROVIDER env var or "lightrag")
        **kwargs: Additional parameters passed to the RAG provider

    Returns:
        dict: Dictionary containing query results
            {
                "query": str,
                "answer": str,
                "content": str,
                "mode": str,
                "provider": str
            }
            
    Raises:
        ValueError: If the specified RAG provider is not found
        Exception: If the query fails
    
    Example:
        # Use default provider (from .env)
        result = await rag_search("What is machine learning?", kb_name="textbook")
        
        # Override provider
        result = await rag_search("What is ML?", kb_name="textbook", provider="chromadb")
    """
    # Determine which provider to use
    provider_name = provider or DEFAULT_RAG_PROVIDER
    
    # Validate provider exists
    if not has_plugin(provider_name):
        available = [p["id"] for p in list_plugins()]
        raise ValueError(
            f"RAG provider '{provider_name}' not found. "
            f"Available providers: {available}. "
            f"Set RAG_PROVIDER in .env or pass provider parameter."
        )
    
    # Get the plugin
    plugin = get_plugin(provider_name)
    
    # Execute search using the plugin
    try:
        result = await plugin["search"](
            query=query,
            kb_name=kb_name,
            mode=mode,
            **kwargs
        )
        
        # Ensure consistent return format
        if "query" not in result:
            result["query"] = query
        if "answer" not in result and "content" in result:
            result["answer"] = result["content"]
        if "content" not in result and "answer" in result:
            result["content"] = result["answer"]
        
        return result
        
    except Exception as e:
        raise Exception(f"RAG search failed with provider '{provider_name}': {e}")


async def initialize_rag(
    kb_name: str,
    documents: List[str],
    provider: str | None = None
) -> bool:
    """
    Initialize RAG with documents.
    
    Args:
        kb_name: Knowledge base name
        documents: List of document contents to index
        provider: RAG provider to use (defaults to RAG_PROVIDER env var)
    
    Returns:
        True if successful
    
    Example:
        documents = ["Document 1 content", "Document 2 content"]
        success = await initialize_rag("my_kb", documents)
    """
    provider_name = provider or DEFAULT_RAG_PROVIDER
    
    if not has_plugin(provider_name):
        raise ValueError(f"RAG provider '{provider_name}' not found")
    
    plugin = get_plugin(provider_name)
    return await plugin["initialize"](kb_name=kb_name, documents=documents)


async def delete_rag(kb_name: str, provider: str | None = None) -> bool:
    """
    Delete a knowledge base.
    
    Args:
        kb_name: Knowledge base name
        provider: RAG provider to use (defaults to RAG_PROVIDER env var)
    
    Returns:
        True if successful
    
    Example:
        success = await delete_rag("old_kb")
    """
    provider_name = provider or DEFAULT_RAG_PROVIDER
    
    if not has_plugin(provider_name):
        raise ValueError(f"RAG provider '{provider_name}' not found")
    
    plugin = get_plugin(provider_name)
    return await plugin["delete"](kb_name=kb_name)


def get_available_providers() -> List[Dict]:
    """
    Get list of available RAG providers.
    
    Returns:
        List of provider information dictionaries
    
    Example:
        providers = get_available_providers()
        for p in providers:
            print(f"{p['name']}: {p['description']}")
    """
    return list_plugins()


def get_current_provider() -> str:
    """Get the currently configured RAG provider"""
    # Read directly from environment to get the latest value (not cached)
    return os.getenv("RAG_PROVIDER", "lightrag")


if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # List available providers
    print("Available RAG Providers:")
    for provider in get_available_providers():
        print(f"  - {provider['id']}: {provider['description']}")
    print(f"\nCurrent provider: {get_current_provider()}\n")

    # Test search
    result = asyncio.run(
        rag_search(
            "What is the lookup table (LUT) in FPGA?",
            kb_name="DE-all",
            mode="naive",
        )
    )

    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer']}")
    print(f"Provider: {result.get('provider', 'unknown')}")
