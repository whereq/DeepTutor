"""
Wrong answer notebook API — persists and exposes quiz mistakes for review.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from deeptutor.services.session import get_sqlite_session_store

router = APIRouter()


class WrongAnswerItem(BaseModel):
    id: int
    session_id: str
    session_title: str = ""
    question_id: str = ""
    question: str
    user_answer: str = ""
    correct_answer: str = ""
    resolved: bool
    created_at: float
    resolved_at: float | None = None


class WrongAnswerListResponse(BaseModel):
    items: list[WrongAnswerItem]
    total: int


class WrongAnswerResolveRequest(BaseModel):
    resolved: bool


@router.get("", response_model=WrongAnswerListResponse)
async def list_wrong_answers(
    resolved: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> WrongAnswerListResponse:
    store = get_sqlite_session_store()
    items = await store.list_wrong_answers(
        resolved=resolved, limit=limit, offset=offset
    )
    total = await store.count_wrong_answers(resolved=resolved)
    return WrongAnswerListResponse(
        items=[WrongAnswerItem(**item) for item in items],
        total=total,
    )


@router.patch("/{wrong_answer_id}")
async def update_wrong_answer(
    wrong_answer_id: int,
    payload: WrongAnswerResolveRequest,
):
    store = get_sqlite_session_store()
    updated = await store.update_wrong_answer_resolved(
        wrong_answer_id, payload.resolved
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Wrong answer not found")
    return {"updated": True, "id": wrong_answer_id, "resolved": payload.resolved}


@router.delete("/{wrong_answer_id}")
async def delete_wrong_answer(wrong_answer_id: int):
    store = get_sqlite_session_store()
    deleted = await store.delete_wrong_answer(wrong_answer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wrong answer not found")
    return {"deleted": True, "id": wrong_answer_id}
