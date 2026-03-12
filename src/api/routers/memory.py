"""
Memory API Router
=================

Expose learner memory files stored in user-data.
"""

from pathlib import Path

from fastapi import APIRouter

from src.services.path_service import get_path_service

router = APIRouter()

MEMORY_FILES = {
    "summary": ("Summary", "memory.md"),
    "weakness": ("Weaknesses", "weakness.md"),
    "reflection": ("Reflection", "reflection.md"),
}


def _get_memory_dir() -> Path:
    return get_path_service().get_memory_dir()


@router.get("/list")
async def list_memory():
    memory_dir = _get_memory_dir()
    memories = []

    for memory_type, (label, filename) in MEMORY_FILES.items():
        path = memory_dir / filename
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        memories.append(
            {
                "type": memory_type,
                "label": label,
                "content": content,
            }
        )

    return {"memories": memories}


@router.post("/clear")
async def clear_memory():
    memory_dir = _get_memory_dir()
    deleted = []

    for _, (_, filename) in MEMORY_FILES.items():
        path = memory_dir / filename
        if path.exists():
            path.unlink()
            deleted.append(filename)

    return {"deleted": deleted}
