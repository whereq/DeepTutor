"""Compatibility re-export for the shared notebook service."""

from deeptutor.services.notebook import (
    Notebook,
    NotebookManager,
    NotebookRecord,
    RecordType,
    get_notebook_manager,
    notebook_manager,
)

__all__ = [
    "Notebook",
    "NotebookManager",
    "NotebookRecord",
    "RecordType",
    "get_notebook_manager",
    "notebook_manager",
]
