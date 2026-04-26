"""
Skills API Router
=================

CRUD endpoints for user-authored SKILL.md files stored under
``data/user/workspace/skills/<name>/SKILL.md``.

Mounted at ``/api/v1/skills``.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from deeptutor.services.skill import get_skill_service
from deeptutor.services.skill.service import (
    InvalidSkillNameError,
    SkillExistsError,
    SkillNotFoundError,
)

router = APIRouter()


class CreateSkillRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = ""
    content: str = ""


class UpdateSkillRequest(BaseModel):
    description: str | None = None
    content: str | None = None
    rename_to: str | None = None


@router.get("/list")
async def list_skills() -> dict[str, list[dict[str, str]]]:
    service = get_skill_service()
    items = [info.to_dict() for info in service.list_skills()]
    return {"skills": items}


@router.get("/{name}")
async def get_skill(name: str) -> dict[str, str]:
    service = get_skill_service()
    try:
        return service.get_detail(name).to_dict()
    except SkillNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill not found: {name}")
    except InvalidSkillNameError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/create")
async def create_skill(payload: CreateSkillRequest) -> dict[str, str]:
    service = get_skill_service()
    try:
        info = service.create(
            name=payload.name,
            description=payload.description,
            content=payload.content,
        )
        return info.to_dict()
    except SkillExistsError:
        raise HTTPException(status_code=409, detail=f"Skill already exists: {payload.name}")
    except InvalidSkillNameError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{name}")
async def update_skill(name: str, payload: UpdateSkillRequest) -> dict[str, str]:
    service = get_skill_service()
    try:
        info = service.update(
            name,
            description=payload.description,
            content=payload.content,
            rename_to=payload.rename_to,
        )
        return info.to_dict()
    except SkillNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill not found: {name}")
    except SkillExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidSkillNameError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{name}")
async def delete_skill(name: str) -> dict[str, str]:
    service = get_skill_service()
    try:
        service.delete(name)
        return {"status": "deleted", "name": name}
    except SkillNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill not found: {name}")
    except InvalidSkillNameError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
