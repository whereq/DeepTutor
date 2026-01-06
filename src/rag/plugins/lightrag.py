"""
LightRAG Plugin
Graph-based RAG with entity extraction and knowledge graph
"""

from pathlib import Path
from typing import Dict, List
import sys

# Add raganything module path
project_root = Path(__file__).parent.parent.parent.parent
raganything_path = project_root.parent / "raganything" / "RAG-Anything"
if raganything_path.exists():
    sys.path.insert(0, str(raganything_path))

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig

from src.core.core import get_embedding_config, get_llm_config
from src.core.logging import LightRAGLogContext
from src.knowledge.manager import KnowledgeBaseManager

# Cache RAG instances to avoid reloading
_rag_instances = {}


def _get_rag_instance(working_dir: str) -> RAGAnything:
    """Get or create RAG instance for a working directory"""
    if working_dir in _rag_instances:
        return _rag_instances[working_dir]
    
    # Get configurations
    llm_config = get_llm_config()
    embedding_config = get_embedding_config()
    
    # LLM function
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            llm_config["model"],
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            **kwargs,
        )
    
    # Embedding function
    embedding_func = EmbeddingFunc(
        embedding_dim=embedding_config["dim"],
        max_token_size=embedding_config["max_tokens"],
        func=lambda texts: openai_embed(
            texts,
            model=embedding_config["model"],
            api_key=embedding_config["api_key"],
            base_url=embedding_config["base_url"],
        ),
    )
    
    # Create RAG instance
    config = RAGAnythingConfig(
        working_dir=working_dir,
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
    )
    
    _rag_instances[working_dir] = rag
    return rag


def _get_working_dir(kb_name: str, kb_base_dir: str = None) -> str:
    """Get RAG storage working directory for a knowledge base"""
    if kb_base_dir is None:
        project_root = Path(__file__).parent.parent.parent.parent
        kb_base_dir = str(project_root / "data" / "knowledge_bases")
    
    if kb_name:
        kb_dir = Path(kb_base_dir) / kb_name
    else:
        # Use default KB if no name provided
        from src.knowledge.manager import KnowledgeBaseManager
        kb_manager = KnowledgeBaseManager(kb_base_dir)
        kb_dir = Path(kb_base_dir) / kb_manager.get_default()
    
    working_dir = str(kb_dir / "rag_storage")
    
    # Create directory if it doesn't exist
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    
    return working_dir


async def initialize_rag(kb_name: str, documents: List[str]) -> bool:
    """
    Initialize LightRAG with documents.
    
    Args:
        kb_name: Knowledge base name
        documents: List of document contents to index
    
    Returns:
        True if successful
    """
    try:
        working_dir = _get_working_dir(kb_name)
        rag = _get_rag_instance(working_dir)
        
        # Ensure initialization
        await rag._ensure_lightrag_initialized()
        
        # Insert documents
        for doc in documents:
            await rag.ainsert(doc)
        
        return True
    except Exception as e:
        raise Exception(f"LightRAG initialization failed: {e}")


async def search_rag(query: str, kb_name: str, mode: str = "hybrid", only_need_context: bool = False, **kwargs) -> Dict:
    """
    Search using LightRAG.
    
    Args:
        query: Search query
        kb_name: Knowledge base name
        mode: Search mode (hybrid, local, global, naive)
        only_need_context: If True, only return context without generating answer
        **kwargs: Additional parameters (ignored for compatibility)
    
    Returns:
        Dictionary with search results
    """
    try:
        working_dir = _get_working_dir(kb_name)
        rag = _get_rag_instance(working_dir)
        
        # Use log forwarding context
        with LightRAGLogContext(scene="rag_search"):
            # Ensure initialization
            await rag._ensure_lightrag_initialized()
            
            # Execute query
            answer = await rag.aquery(query, mode=mode, only_need_context=only_need_context)
            answer_str = answer if isinstance(answer, str) else str(answer)
            
            return {
                "query": query,
                "answer": answer_str,
                "content": answer_str,
                "mode": mode,
                "provider": "lightrag"
            }
    except Exception as e:
        raise Exception(f"LightRAG search failed: {e}")


async def delete_rag(kb_name: str) -> bool:
    """
    Delete LightRAG knowledge base.
    
    Args:
        kb_name: Knowledge base name
    
    Returns:
        True if successful
    """
    try:
        working_dir = _get_working_dir(kb_name)
        
        # Remove from cache
        if working_dir in _rag_instances:
            del _rag_instances[working_dir]
        
        # Delete storage directory
        storage_path = Path(working_dir)
        if storage_path.exists():
            import shutil
            shutil.rmtree(storage_path)
        
        return True
    except Exception as e:
        raise Exception(f"LightRAG deletion failed: {e}")


# Plugin metadata
CONFIG = {
    "name": "LightRAG",
    "version": "1.0.0",
    "author": "DeepTutor Team",
    "description": "Graph-based RAG with entity extraction and knowledge graph",
    "supported_modes": ["hybrid", "local", "global", "naive"],
    "requires": ["lightrag", "raganything", "networkx"]
}
