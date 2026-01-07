"""Jina AI embedding adapter with task-aware embeddings and late chunking."""

import httpx
from typing import Dict, Any
import logging

from .base import BaseEmbeddingAdapter, EmbeddingRequest, EmbeddingResponse

logger = logging.getLogger(__name__)


class JinaEmbeddingAdapter(BaseEmbeddingAdapter):
    """Adapter for Jina AI embeddings (v3/v4)."""
    
    MODELS_INFO = {
        "jina-embeddings-v3": 1024,
        "jina-embeddings-v4": 1024,
    }
    
    INPUT_TYPE_TO_TASK = {
        "search_document": "retrieval.passage",
        "search_query": "retrieval.query",
        "classification": "classification",
        "clustering": "separation",
        "text-matching": "text-matching",
    }
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "input": request.texts,
            "model": request.model or self.model,
        }
        
        if request.input_type:
            task = self.INPUT_TYPE_TO_TASK.get(
                request.input_type,
                request.input_type
            )
            payload["task"] = task
            logger.debug(f"Using Jina task: {task}")
        
        if request.normalized is not None:
            payload["normalized"] = request.normalized
        
        if "jina-embeddings-v3" in (request.model or self.model) and request.late_chunking:
            payload["late_chunking"] = request.late_chunking
        
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
        """Return information about the configured model."""
        return {
            "model": self.model,
            "dimensions": self.MODELS_INFO.get(self.model, self.dimensions),
            "provider": "jina",
        }
