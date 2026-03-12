"""
CLI Knowledge Base Command
===========================

Manage knowledge bases from the command line.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def register(app: typer.Typer) -> None:

    @app.command("list")
    def kb_list() -> None:
        """List all knowledge bases."""
        from src.knowledge.manager import KnowledgeBaseManager

        mgr = KnowledgeBaseManager()
        kbs = mgr.list_knowledge_bases()
        if not kbs:
            console.print("[dim]No knowledge bases found.[/]")
            return
        table = Table(title="Knowledge Bases")
        table.add_column("Name", style="bold")
        table.add_column("Status")
        table.add_column("Documents")
        table.add_column("RAG Provider")
        for kb in kbs:
            name = kb.get("name", "?")
            status = kb.get("status", "?")
            docs = str(kb.get("document_count", "?"))
            provider = kb.get("rag_provider", "?")
            table.add_row(name, status, docs, provider)
        console.print(table)

    @app.command("info")
    def kb_info(name: str = typer.Argument(..., help="Knowledge base name.")) -> None:
        """Show details of a knowledge base."""
        from src.knowledge.manager import KnowledgeBaseManager

        mgr = KnowledgeBaseManager()
        info = mgr.get_kb_info(name)
        if info is None:
            console.print(f"[red]Knowledge base '{name}' not found.[/]")
            raise typer.Exit(code=1)
        import json

        console.print_json(json.dumps(info, indent=2, ensure_ascii=False, default=str))

    @app.command("create")
    def kb_create(
        name: str = typer.Argument(..., help="New KB name."),
        docs: list[str] = typer.Option([], "--doc", "-d", help="Document paths."),
        docs_dir: Optional[str] = typer.Option(None, "--docs-dir", help="Directory of documents."),
    ) -> None:
        """Initialize a new knowledge base from documents."""
        from src.knowledge.initializer import initialize_knowledge_base

        doc_paths = list(docs)
        if docs_dir:
            p = Path(docs_dir)
            doc_paths.extend(str(f) for f in p.iterdir() if f.is_file())

        if not doc_paths:
            console.print("[red]Provide at least one document (--doc or --docs-dir).[/]")
            raise typer.Exit(code=1)

        console.print(f"Creating KB [bold]{name}[/] with {len(doc_paths)} document(s)...")
        asyncio.run(initialize_knowledge_base(name, doc_paths))
        console.print("[green]Done.[/]")

    @app.command("add")
    def kb_add(
        name: str = typer.Argument(..., help="KB name."),
        docs: list[str] = typer.Option([], "--doc", "-d", help="Document paths to add."),
        docs_dir: Optional[str] = typer.Option(None, "--docs-dir", help="Directory of documents."),
    ) -> None:
        """Add documents to an existing knowledge base."""
        from src.knowledge.add_documents import add_documents

        doc_paths = list(docs)
        if docs_dir:
            p = Path(docs_dir)
            doc_paths.extend(str(f) for f in p.iterdir() if f.is_file())

        if not doc_paths:
            console.print("[red]Provide at least one document.[/]")
            raise typer.Exit(code=1)

        console.print(f"Adding {len(doc_paths)} document(s) to [bold]{name}[/]...")
        asyncio.run(add_documents(name, doc_paths))
        console.print("[green]Done.[/]")

    @app.command("delete")
    def kb_delete(
        name: str = typer.Argument(..., help="KB name."),
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation."),
    ) -> None:
        """Delete a knowledge base."""
        if not force:
            confirm = typer.confirm(f"Delete knowledge base '{name}'?")
            if not confirm:
                raise typer.Abort()

        from src.knowledge.manager import KnowledgeBaseManager

        mgr = KnowledgeBaseManager()
        mgr.delete_kb(name)
        console.print(f"[green]Deleted '{name}'.[/]")

    @app.command("search")
    def kb_search(
        name: str = typer.Argument(..., help="KB name."),
        query: str = typer.Argument(..., help="Search query."),
        mode: str = typer.Option("hybrid", help="Search mode."),
        fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
    ) -> None:
        """Search a knowledge base."""
        from src.tools.rag_tool import rag_search

        result = asyncio.run(rag_search(query=query, kb_name=name, mode=mode))
        if fmt == "json":
            import json

            console.print_json(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            answer = result.get("answer") or result.get("content", "")
            console.print(f"[bold]Answer:[/]\n{answer}")
