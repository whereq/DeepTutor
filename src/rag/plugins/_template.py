"""
RAG Plugin Template
Copy this file and implement these functions to create a new RAG plugin.
No inheritance needed - just implement these 3 functions!

Example:
    cp _template.py my_rag.py
    # Fill in the functions below
    # Done! Plugin auto-discovered
"""

from typing import Dict, List


async def initialize_rag(kb_name: str, documents: List[str]) -> bool:
    """
    Process and store documents in the knowledge base.
    
    Args:
        kb_name: Name of the knowledge base
        documents: List of document contents to index
    
    Returns:
        True if successful, False otherwise
    
    Example:
        Initialize your RAG system, process documents, create indexes, etc.
    """
    # TODO: Implement your initialization logic
    raise NotImplementedError("initialize_rag not implemented")


async def search_rag(query: str, kb_name: str, mode: str = "hybrid") -> Dict:
    """
    Search for relevant information in the knowledge base.
    
    Args:
        query: Search query string
        kb_name: Name of the knowledge base to search
        mode: Search mode (e.g., "hybrid", "vector", "semantic")
    
    Returns:
        Dictionary with at least:
        {
            "content": str,  # Retrieved content
            "mode": str,     # Mode used
            "provider": str  # Your plugin name
        }
    
    Example:
        Perform semantic/vector/graph search and return results
    """
    # TODO: Implement your search logic
    raise NotImplementedError("search_rag not implemented")


async def delete_rag(kb_name: str) -> bool:
    """
    Delete a knowledge base and all associated data.
    
    Args:
        kb_name: Name of the knowledge base to delete
    
    Returns:
        True if successful, False otherwise
    
    Example:
        Clean up indexes, delete files, free resources, etc.
    """
    # TODO: Implement your deletion logic
    raise NotImplementedError("delete_rag not implemented")


# Optional: Plugin metadata (recommended)
CONFIG = {
    "name": "My RAG Plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "Brief description of what this RAG does",
    "supported_modes": ["hybrid", "vector"],  # List of supported search modes
    "requires": ["package1", "package2"],     # Python dependencies
}
