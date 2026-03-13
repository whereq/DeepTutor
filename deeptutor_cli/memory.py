"""
CLI memory command.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from deeptutor.services.memory import get_memory_service

console = Console()


def _get_memory_path() -> Path:
    return get_memory_service().memory_path


def register(app: typer.Typer) -> None:
    @app.command("show")
    def memory_show() -> None:
        """Display the current long-term memory."""
        snapshot = get_memory_service().read_snapshot()
        if snapshot.content:
            console.print(Panel(Markdown(snapshot.content), title="[bold]memory.md[/]"))
        else:
            console.print("[dim]memory.md: (empty)[/]")

    @app.command("clear")
    def memory_clear(
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation."),
    ) -> None:
        """Clear the long-term memory file."""
        if not force:
            confirm = typer.confirm("Clear memory.md?")
            if not confirm:
                raise typer.Abort()

        path = _get_memory_path()
        get_memory_service().clear_memory()
        console.print(f"[green]Cleared {path.name}.[/]")

    @app.command("export")
    def memory_export(
        dest: str = typer.Argument(..., help="Destination directory."),
    ) -> None:
        """Export memory.md to a directory."""
        import shutil

        source = _get_memory_path()
        if not source.exists():
            console.print("[yellow]memory.md is empty.[/]")
            return

        dest_path = Path(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_path / source.name)
        console.print(f"[green]Exported {source.name} to {dest_path}[/]")
