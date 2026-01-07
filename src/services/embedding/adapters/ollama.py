"""
Ollama Embedding Adapter
=========================

Adapter for Ollama local embeddings.
No authentication required, runs on localhost.
"""

import httpx
from typing import Dict, Any
import logging

from .base import BaseEmbeddingAdapter, EmbeddingRequest, EmbeddingResponse

logger = logging.getLogger(__name__)


class OllamaEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Adapter for Ollama embeddings (local deployment).
    
    Ollama runs locally without authentication.
    
    API format:
        POST /api/embed
        {
            "model": "all-minilm",
            "input": ["text1", "text2", ...],
            "dimensions": 384  # optional
        }
    
    Default URL: http://localhost:11434
    """
    
    # Known Ollama embedding models with their dimensions
    MODELS_INFO = {
        "all-minilm": 384,
        "all-mpnet-base-v2": 768,
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "snowflake-arctic-embed": 1024,
    }
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate embeddings using Ollama API.
        
        Args:
            request: EmbeddingRequest with texts to embed
            
        Returns:
            EmbeddingResponse with embeddings and metadata
            
        Raises:
            httpx.HTTPError: If the API request fails
        """
        payload = {
            "model": request.model or self.model,
            "input": request.texts,
        }
        
        # Add dimensions if specified (supported in newer Ollama versions)
        if request.dimensions or self.dimensions:
            payload["dimensions"] = request.dimensions or self.dimensions
        
        # Truncate parameter
        if request.truncate is not None:
            payload["truncate"] = request.truncate
        
        # Keep alive parameter (keeps model loaded in memory)
        # Format: duration string like "5m", "1h", or -1 to keep indefinitely
        payload["keep_alive"] = "5m"  # Default: keep model for 5 minutes
        
        url = f"{self.base_url}/api/embed"
        
        logger.debug(f"Sending embedding request to {url} with {len(request.texts)} texts")
        
        # Ollama doesn't require authentication
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        
        embeddings = data["embeddings"]
        
        logger.info(
            f"Successfully generated {len(embeddings)} embeddings "
            f"(model: {data.get('model', self.model)}, dimensions: {len(embeddings[0])})"
        )
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=data.get("model", self.model),
            dimensions=len(embeddings[0]),
            usage={
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "total_duration": data.get("total_duration", 0),
            }
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return information about the configured model."""
        return {
            "model": self.model,
            "dimensions": self.MODELS_INFO.get(self.model, self.dimensions),
            "local": True,
            "provider": "ollama",
        }
