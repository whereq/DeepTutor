"""OpenAI-compatible embedding adapter for OpenAI, Azure, HuggingFace, etc."""

import httpx
from typing import Dict, Any
import logging

from .base import BaseEmbeddingAdapter, EmbeddingRequest, EmbeddingResponse

logger = logging.getLogger(__name__)


class OpenAICompatibleEmbeddingAdapter(BaseEmbeddingAdapter):
    """Adapter for OpenAI-compatible APIs: OpenAI, Azure, HuggingFace."""
    
    MODELS_INFO = {
        "text-embedding-3-large": 3072,
        "text-embedding-3-small": 1536,
        "text-embedding-ada-002": 1536,
    }
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "input": request.texts,
            "model": request.model or self.model,
            "encoding_format": request.encoding_format or "float",
        }
        
        if request.dimensions or self.dimensions:
            payload["dimensions"] = request.dimensions or self.dimensions
        
        url = f"{self.base_url}/embeddings"
        
        logger.debug(f"Sending embedding request to {url} with {len(request.texts)} texts")
        
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"HTTP {response.status_code} response body: {response.text}")
            
            response.raise_for_status()
            data = response.json()
        
        embeddings = [item["embedding"] for item in data["data"]]
        
        logger.info(
            f"Successfully generated {len(embeddings)} embeddings "
            f"(model: {data['model']}, dimensions: {len(embeddings[0])})"
        )
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=data["model"],
            dimensions=len(embeddings[0]),
            usage=data.get("usage", {})
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "dimensions": self.MODELS_INFO.get(self.model, self.dimensions),
            "provider": "openai_compatible",
        }
