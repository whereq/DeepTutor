"""
Lightweight memory API router.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from deeptutor.services.memory import get_memory_service
from deeptutor.services.session import get_sqlite_session_store

router = APIRouter()


class MemoryRefreshRequest(BaseModel):
    session_id: str | None = None
    language: str = "en"


class MemoryUpdateRequest(BaseModel):
    content: str = ""


@router.get("")
async def get_memory():
    snapshot = get_memory_service().read_snapshot()
    return {
        "content": snapshot.content,
        "exists": snapshot.exists,
        "updated_at": snapshot.updated_at,
    }


@router.put("")
async def update_memory(payload: MemoryUpdateRequest):
    snapshot = get_memory_service().write_memory(payload.content)
    return {
        "content": snapshot.content,
        "exists": snapshot.exists,
        "updated_at": snapshot.updated_at,
        "saved": True,
    }


@router.post("/refresh")
async def refresh_memory(payload: MemoryRefreshRequest):
    store = get_sqlite_session_store()
    session_id = str(payload.session_id or "").strip()
    if session_id:
        session = await store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

    result = await get_memory_service().refresh_from_session(
        session_id or None,
        language=payload.language,
    )
    return {
        "content": result.content,
        "exists": bool(result.content.strip()),
        "updated_at": result.updated_at,
        "changed": result.changed,
    }


@router.post("/clear")
async def clear_memory():
    snapshot = get_memory_service().clear_memory()
    return {
        "content": snapshot.content,
        "exists": snapshot.exists,
        "updated_at": snapshot.updated_at,
        "cleared": True,
    }
