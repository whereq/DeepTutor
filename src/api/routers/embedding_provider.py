"""
Embedding Provider API Router
==============================

Manages embedding provider configurations via REST API.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.embedding.provider_config import (
    EmbeddingProvider,
    embedding_provider_config_manager,
)

router = APIRouter()


class TestConnectionRequest(BaseModel):
    """Request model for testing embedding provider connection."""
    binding: str
    base_url: str
    api_key: str = ""  # Optional for local providers
    model: str
    dimensions: int = 1024
    requires_key: bool = True


@router.get("/", response_model=List[EmbeddingProvider])
async def list_providers():
    """
    List all configured embedding providers.
    If no providers exist, auto-create one from current .env configuration.
    """
    providers = embedding_provider_config_manager.list_providers()
    
    if not providers:
        try:
            from src.services.embedding import get_embedding_config
            
            current_config = get_embedding_config()
            
            default_provider = EmbeddingProvider(
                name=f"Current ({current_config.binding})",
                binding=current_config.binding,
                base_url=current_config.base_url or "",
                api_key=current_config.api_key or "",
                model=current_config.model,
                dimensions=current_config.dim,
                is_active=True,
                input_type=current_config.input_type,
                normalized=current_config.normalized,
                truncate=current_config.truncate,
            )
            
            embedding_provider_config_manager.add_provider(default_provider)
            providers = [default_provider]
        except Exception as e:
            print(f"Warning: Could not auto-create provider from .env: {e}")
    
    return providers


@router.post("/", response_model=EmbeddingProvider)
async def add_provider(provider: EmbeddingProvider):
    """Add a new embedding provider."""
    try:
        return embedding_provider_config_manager.add_provider(provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{name}", response_model=EmbeddingProvider)
async def update_provider(name: str, updates: Dict[str, Any]):
    """Update an existing embedding provider."""
    provider = embedding_provider_config_manager.update_provider(name, updates)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.delete("/{name}")
async def delete_provider(name: str):
    """Delete an embedding provider."""
    success = embedding_provider_config_manager.delete_provider(name)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted"}


@router.post("/active", response_model=EmbeddingProvider)
async def set_active_provider(name_payload: Dict[str, str]):
    """Set the active embedding provider."""
    name = name_payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    provider = embedding_provider_config_manager.set_active_provider(name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/test", response_model=Dict[str, Any])
async def test_connection(request: TestConnectionRequest):
    """Test connection to an embedding provider."""
    try:
        # Import here to avoid circular dependency
        from src.services.embedding import get_embedding_client, reset_embedding_client
        from src.services.embedding.config import EmbeddingConfig
        
        # Sanitize base URL
        base_url = request.base_url.rstrip("/")
        
        # Handle API key requirement
        api_key_to_use = request.api_key
        if not request.requires_key and not api_key_to_use:
            api_key_to_use = "no-key-required"  # Dummy key for local providers
        
        # Create temporary config for testing
        test_config = EmbeddingConfig(
            binding=request.binding,
            model=request.model,
            api_key=api_key_to_use,
            base_url=base_url,
            dim=request.dimensions,
        )
        
        # Reset and create new client with test config
        reset_embedding_client()
        
        # Test with a simple embedding
        from src.services.embedding.client import EmbeddingClient
        test_client = EmbeddingClient(config=test_config)
        
        embeddings = await test_client.embed(["Hello, testing embedding service"])
        
        if not embeddings or not embeddings[0]:
            return {
                "success": False,
                "message": "Connection succeeded but received empty embeddings"
            }
        
        # Reset to default config after test
        reset_embedding_client()
        
        return {
            "success": True,
            "message": "Connection successful",
            "dimensions": len(embeddings[0]),
            "expected_dimensions": request.dimensions,
        }
        
    except Exception as e:
        # Reset to default config on error
        from src.services.embedding import reset_embedding_client
        reset_embedding_client()
        
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}"
        }
