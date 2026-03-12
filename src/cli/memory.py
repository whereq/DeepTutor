"""
CLI Memory Command
==================

View and manage learner memory (reflection, summary, weakness).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

MEMORY_FILES = {
    "summary": "memory.md",
    "weakness": "weakness.md",
    "reflection": "reflection.md",
}


def _get_memory_dir() -> Path:
    from src.services.path_service import get_path_service

    ps = get_path_service()
    return Path(ps.get_user_data_dir()) / "memory"


def register(app: typer.Typer) -> None:

    @app.command("show")
    def memory_show(
        type_: Optional[str] = typer.Option(
            None, "--type", "-t", help="Memory type: summary | weakness | reflection"
        ),
    ) -> None:
        """Display learner memory contents."""
        mem_dir = _get_memory_dir()
        files = {type_: MEMORY_FILES[type_]} if type_ and type_ in MEMORY_FILES else MEMORY_FILES

        for label, filename in files.items():
            path = mem_dir / filename
            if path.exists():
                content = path.read_text(encoding="utf-8")
                console.print(Panel(Markdown(content), title=f"[bold]{label}[/]"))
            else:
                console.print(f"[dim]{label}: (empty)[/]")

    @app.command("clear")
    def memory_clear(
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation."),
    ) -> None:
        """Clear all memory files."""
        if not force:
            confirm = typer.confirm("Clear all learner memory?")
            if not confirm:
                raise typer.Abort()

        mem_dir = _get_memory_dir()
        for filename in MEMORY_FILES.values():
            path = mem_dir / filename
            if path.exists():
                path.unlink()
                console.print(f"[green]Deleted {path.name}[/]")

        console.print("[green]Memory cleared.[/]")

    @app.command("export")
    def memory_export(
        dest: str = typer.Argument(..., help="Destination directory."),
    ) -> None:
        """Export memory files to a directory."""
        import shutil

        dest_path = Path(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        mem_dir = _get_memory_dir()

        exported = 0
        for filename in MEMORY_FILES.values():
            src = mem_dir / filename
            if src.exists():
                shutil.copy2(src, dest_path / filename)
                exported += 1

        console.print(f"[green]Exported {exported} file(s) to {dest_path}[/]")
