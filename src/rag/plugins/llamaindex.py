"""
LlamaIndex Plugin - Simple and fast RAG system
Best for general documents and Q&A - much faster than graph-based approaches
"""

from pathlib import Path
from typing import Dict, List
import os

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        Settings,
        Document,
    )
    from llama_index.core import load_index_from_storage
    from llama_index.embeddings.openai import OpenAIEmbedding
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False

from src.core.core import get_embedding_config, get_llm_config

# Cache indices to avoid reloading
_indices = {}


def _get_storage_dir(kb_name: str) -> Path:
    """Get storage directory for a knowledge base"""
    project_root = Path(__file__).parent.parent.parent.parent
    storage_dir = project_root / "data" / "knowledge_bases" / kb_name / "llamaindex_storage"
    
    # Create directory if it doesn't exist
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    return storage_dir


def _configure_settings():
    """Configure LlamaIndex with embedding settings"""
    if not LLAMAINDEX_AVAILABLE:
        raise ImportError("LlamaIndex not installed. Run: pip install llama-index llama-index-embeddings-openai")
    
    try:
        embedding_config = get_embedding_config()
        
        # Configure embedding model
        Settings.embed_model = OpenAIEmbedding(
            api_key=embedding_config["api_key"],
            api_base=embedding_config["base_url"],
            model=embedding_config["model"],
            embed_batch_size=10,
        )
        
        # Set chunk size and overlap
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
    except Exception as e:
        raise Exception(f"Failed to configure LlamaIndex settings: {e}")


async def initialize_rag(kb_name: str, documents: List[str]) -> bool:
    """
    Initialize LlamaIndex with documents.
    
    Args:
        kb_name: Knowledge base name
        documents: List of document contents to index
    
    Returns:
        True if successful
    """
    if not LLAMAINDEX_AVAILABLE:
        raise ImportError("LlamaIndex not installed. Run: pip install llama-index llama-index-embeddings-openai")
    
    try:
        # Configure settings
        _configure_settings()
        
        # Get storage directory
        storage_dir = _get_storage_dir(kb_name)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary directory for documents
        temp_dir = storage_dir / "temp_docs"
        temp_dir.mkdir(exist_ok=True)
        
        # Save documents to temporary files
        doc_files = []
        for idx, doc_content in enumerate(documents):
            doc_file = temp_dir / f"doc_{idx}.txt"
            doc_file.write_text(doc_content, encoding='utf-8')
            doc_files.append(str(doc_file))
        
        # Load documents using SimpleDirectoryReader
        reader = SimpleDirectoryReader(input_dir=str(temp_dir))
        loaded_docs = reader.load_data()
        
        # Create index from documents
        index = VectorStoreIndex.from_documents(
            loaded_docs,
            show_progress=True
        )
        
        # Persist to disk
        index.storage_context.persist(persist_dir=str(storage_dir))
        
        # Cache in memory
        _indices[kb_name] = index
        
        # Cleanup temporary files
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        raise Exception(f"LlamaIndex initialization failed: {e}")


async def search_rag(query: str, kb_name: str, mode: str = "semantic", only_need_context: bool = False, **kwargs) -> Dict:
    """
    Search using LlamaIndex.
    
    Args:
        query: Search query
        kb_name: Knowledge base name
        mode: Search mode (semantic, hybrid)
        only_need_context: If True, only return context without generating answer
        **kwargs: Additional parameters (ignored for compatibility)
    
    Returns:
        Dictionary with search results
    """
    if not LLAMAINDEX_AVAILABLE:
        raise ImportError("LlamaIndex not installed. Run: pip install llama-index llama-index-embeddings-openai")
    
    try:
        # Configure settings
        _configure_settings()
        
        # Get or load index
        if kb_name not in _indices:
            storage_dir = _get_storage_dir(kb_name)
            
            if not storage_dir.exists():
                raise ValueError(
                    f"Knowledge base '{kb_name}' not initialized. "
                    "Please initialize it first."
                )
            
            # Load from disk
            storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
            _indices[kb_name] = load_index_from_storage(storage_context)
        
        index = _indices[kb_name]
        
        # Determine query parameters based on mode
        if mode == "hybrid":
            # Tree summarize for better synthesis
            response_mode = "tree_summarize"
            similarity_top_k = 5
        else:  # semantic
            # Compact for faster responses
            response_mode = "compact"
            similarity_top_k = 3
        
        # If only context needed, use retriever instead of query engine
        if only_need_context:
            # Get retriever for raw context
            retriever = index.as_retriever(similarity_top_k=similarity_top_k)
            nodes = retriever.retrieve(query)
            
            # Combine context from all nodes
            context_parts = [node.text for node in nodes]
            context_text = "\n\n".join(context_parts)
            
            return {
                "query": query,
                "answer": context_text,
                "content": context_text,
                "mode": mode,
                "provider": "llamaindex",
                "sources": len(nodes)
            }
        
        # Create query engine for full answer generation
        query_engine = index.as_query_engine(
            similarity_top_k=similarity_top_k,
            response_mode=response_mode,
        )
        
        # Execute query
        response = query_engine.query(query)
        
        # Extract response text
        response_text = str(response)
        
        # Get source information if available
        source_count = 0
        if hasattr(response, 'source_nodes'):
            source_count = len(response.source_nodes)
        
        return {
            "query": query,
            "answer": response_text,
            "content": response_text,
            "mode": mode,
            "provider": "llamaindex",
            "sources": source_count
        }
        
    except Exception as e:
        raise Exception(f"LlamaIndex search failed: {e}")


async def delete_rag(kb_name: str) -> bool:
    """
    Delete LlamaIndex knowledge base.
    
    Args:
        kb_name: Knowledge base name
    
    Returns:
        True if successful
    """
    try:
        # Remove from cache
        if kb_name in _indices:
            del _indices[kb_name]
        
        # Delete storage directory
        storage_dir = _get_storage_dir(kb_name)
        if storage_dir.exists():
            import shutil
            shutil.rmtree(storage_dir)
        
        return True
        
    except Exception as e:
        raise Exception(f"LlamaIndex deletion failed: {e}")


# Plugin metadata
CONFIG = {
    "name": "LlamaIndex",
    "version": "1.0.0",
    "author": "DeepTutor Team",
    "description": "Simple and fast vector-based RAG - great for general documents and Q&A",
    "supported_modes": ["semantic", "hybrid"],
    "requires": ["llama-index", "llama-index-embeddings-openai"]
}
