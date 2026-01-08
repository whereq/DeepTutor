from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.llm_factory import llm_complete, llm_fetch_models
from src.services.llm.provider import LLMProvider, provider_manager

router = APIRouter()


class TestConnectionRequest(BaseModel):
    binding: str
    base_url: str
    api_key: str
    model: str
    requires_key: bool = True  # Default to True for backward compatibility


@router.get("/", response_model=List[LLMProvider])
async def list_providers():
    """List all configured LLM providers."""
    return provider_manager.list_providers()


@router.post("/", response_model=LLMProvider)
async def add_provider(provider: LLMProvider):
    """Add a new LLM provider."""
    try:
        return provider_manager.add_provider(provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{name}/", response_model=LLMProvider)
async def update_provider(name: str, updates: Dict[str, Any]):
    """Update an existing LLM provider."""
    provider = provider_manager.update_provider(name, updates)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.delete("/")
async def delete_provider_by_query(name: str):
    """Delete an LLM provider (query param version)."""
    success = provider_manager.delete_provider(name)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted"}


@router.delete("/{name}/")
async def delete_provider(name: str):
    """Delete an LLM provider."""
    success = provider_manager.delete_provider(name)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted"}


@router.post("/active/", response_model=LLMProvider)
async def set_active_provider(name_payload: Dict[str, str]):
    """Set the active LLM provider."""
    name = name_payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    provider = provider_manager.set_active_provider(name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/test/", response_model=Dict[str, Any])
async def test_connection(request: TestConnectionRequest):
    """Test connection to an LLM provider."""
    try:
        # Sanitize Base URL
        # Users often paste full endpoints like http://.../v1/chat/completions
        # OpenAI client needs just the base (e.g., http://.../v1)
        base_url = request.base_url.rstrip("/")
        
        # Special handling for Ollama: if it ends in /api, it's likely wrong for completion but ok for tags
        # But here we want the completion base.
        if "/api" in base_url and not base_url.endswith("/v1"):
            # If user has http://localhost:11434/api -> change to http://localhost:11434/v1
            if ":11434" in base_url or "ollama" in base_url.lower():
                base_url = base_url.replace("/api", "/v1")

        for suffix in ["/chat/completions", "/completions"]:
            if base_url.endswith(suffix):
                base_url = base_url[: -len(suffix)]

        # Simple test prompt
        if not request.requires_key and not request.api_key:
            # Inject dummy key if not required and not provided
            # This satisfies the OpenAI client library which demands a key
            api_key_to_use = "sk-no-key-required"
        else:
            api_key_to_use = request.api_key

        response = await llm_complete(
            model=request.model,
            prompt="Hello, are you working?",
            system_prompt="You are a helpful assistant. Reply with 'Yes'.",
            api_key=api_key_to_use,
            base_url=base_url,
            binding=request.binding,
            max_tokens=200,
        )
        return {"success": True, "message": "Connection successful", "response": response}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


@router.post("/models/", response_model=Dict[str, Any])
async def fetch_available_models(request: TestConnectionRequest):
    """Fetch available models from the provider."""
    try:
        # Sanitize Base URL (same as test_connection)
        base_url = request.base_url.rstrip("/")
        if "/api" in base_url and not base_url.endswith("/v1"):
             if ":11434" in base_url or "ollama" in base_url.lower():
                 base_url = base_url.replace("/api", "/v1")
        
        for suffix in ["/chat/completions", "/completions"]:
             if base_url.endswith(suffix):
                 base_url = base_url[: -len(suffix)]

        models = await llm_fetch_models(
            binding=request.binding,
            base_url=base_url,
            api_key=request.api_key if request.requires_key else None
        )
        return {"success": True, "models": models}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch models: {str(e)}"}
