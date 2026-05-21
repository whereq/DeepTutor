"""Path resolution for the three-layer memory subsystem.

Layout under the per-user memory root::

    trace/<surface>/<YYYY-MM-DD>.jsonl    (L1, append-only)
    L2/<surface>.md                       (L2, per-surface summaries)
    L3/<recent|profile|scope|preferences>.md  (L3, cross-surface)
    backup/<timestamp>/...                (v1 migration archive)

The root itself is resolved via :class:`PathService` so the multi-user
context (workspace_root) is picked up at call time, not import time.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal, get_args

from deeptutor.services.path_service import get_path_service

Surface = Literal[
    "chat",
    "notebook",
    "quiz",
    "kb",
    "book",
    "tutorbot",
    "cowriter",
]
L3Slot = Literal["recent", "profile", "scope", "preferences"]

SURFACES: tuple[Surface, ...] = get_args(Surface)
L3_SLOTS: tuple[L3Slot, ...] = get_args(L3Slot)


def memory_root() -> Path:
    return get_path_service().get_memory_dir()


def trace_dir(surface: Surface) -> Path:
    return memory_root() / "trace" / surface


def trace_file(surface: Surface, day: date) -> Path:
    return trace_dir(surface) / f"{day.isoformat()}.jsonl"


def l2_dir() -> Path:
    return memory_root() / "L2"


def l2_file(surface: Surface) -> Path:
    return l2_dir() / f"{surface}.md"


def l3_dir() -> Path:
    return memory_root() / "L3"


def l3_file(slot: L3Slot) -> Path:
    return l3_dir() / f"{slot}.md"


def backup_root() -> Path:
    return memory_root() / "backup"


def ensure_dirs() -> None:
    """Create the directory skeleton. Idempotent."""
    root = memory_root()
    root.mkdir(parents=True, exist_ok=True)
    l2_dir().mkdir(parents=True, exist_ok=True)
    l3_dir().mkdir(parents=True, exist_ok=True)
    for surface in SURFACES:
        trace_dir(surface).mkdir(parents=True, exist_ok=True)
