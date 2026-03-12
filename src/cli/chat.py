"""
CLI Chat Command
================

Interactive REPL and single-shot chat with tool/capability selection.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from src.core.context import Attachment, UnifiedContext
from src.core.stream import StreamEvent, StreamEventType

console = Console()

# ---- helpers ----


async def _run_once(
    message: str,
    tools: list[str],
    capability: str | None,
    kb: str | None,
    language: str,
    fmt: str,
) -> None:
    from src.runtime.orchestrator import ChatOrchestrator

    orch = ChatOrchestrator()
    ctx = UnifiedContext(
        user_message=message,
        enabled_tools=tools,
        active_capability=capability,
        knowledge_bases=[kb] if kb else [],
        language=language,
    )

    if fmt == "json":
        async for event in orch.handle(ctx):
            sys.stdout.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
            sys.stdout.flush()
    else:
        await _render_stream(orch, ctx)


async def _render_stream(orch, ctx: UnifiedContext) -> None:
    """Rich console renderer for streaming events."""
    current_stage = ""
    content_buf = ""

    async for event in orch.handle(ctx):
        if event.type == StreamEventType.STAGE_START:
            current_stage = event.stage
            console.print(f"\n[bold cyan]▶ {event.stage}[/]", highlight=False)
        elif event.type == StreamEventType.STAGE_END:
            if content_buf:
                console.print(Markdown(content_buf))
                content_buf = ""
            current_stage = ""
        elif event.type == StreamEventType.THINKING:
            console.print(f"  [dim]{event.content}[/]", highlight=False)
        elif event.type == StreamEventType.CONTENT:
            content_buf += event.content
        elif event.type == StreamEventType.TOOL_CALL:
            console.print(f"  [yellow]🔧 {event.content}[/]({event.metadata.get('args',{})})", highlight=False)
        elif event.type == StreamEventType.TOOL_RESULT:
            snippet = event.content[:200]
            console.print(f"  [green]← {event.metadata.get('tool','')}[/]: {snippet}", highlight=False)
        elif event.type == StreamEventType.PROGRESS:
            console.print(f"  [dim]{event.content}[/]", highlight=False)
        elif event.type == StreamEventType.SOURCES:
            srcs = event.metadata.get("sources", [])
            if srcs:
                console.print(f"  [dim]Sources: {len(srcs)} items[/]", highlight=False)
        elif event.type == StreamEventType.ERROR:
            console.print(f"[bold red]Error:[/] {event.content}")
        elif event.type == StreamEventType.RESULT:
            pass  # final result, content already streamed
        elif event.type == StreamEventType.DONE:
            if content_buf:
                console.print(Markdown(content_buf))
                content_buf = ""


async def _repl(
    tools: list[str],
    capability: str | None,
    kb: str | None,
    language: str,
) -> None:
    """Interactive Read-Eval-Print Loop."""
    from src.runtime.orchestrator import ChatOrchestrator

    orch = ChatOrchestrator()
    history: list[dict] = []

    console.print(Panel(
        "[bold]DeepTutor Chat[/]\n"
        "Type a message to chat. Commands:\n"
        "  /tool on <name>    – enable a tool\n"
        "  /tool off <name>   – disable a tool\n"
        "  /cap <name|none>   – switch capability\n"
        "  /kb <name>         – select knowledge base\n"
        "  /tools             – list available tools\n"
        "  /caps              – list capabilities\n"
        "  /quit              – exit",
        title="deeptutor chat",
    ))

    console.print(f"  Tools: {tools}  Capability: {capability or 'chat'}  KB: {kb or 'none'}\n")

    while True:
        try:
            user_input = console.input("[bold green]You>[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        # Slash commands
        if user_input.startswith("/"):
            parts = user_input.split()
            cmd = parts[0].lower()

            if cmd == "/quit":
                break
            elif cmd == "/tools":
                console.print(f"Available: {orch.list_tools()}")
                console.print(f"Enabled:   {tools}")
                continue
            elif cmd == "/caps":
                console.print(f"Available: {orch.list_capabilities()}")
                console.print(f"Active:    {capability or 'chat'}")
                continue
            elif cmd == "/tool" and len(parts) >= 3:
                action, name = parts[1], parts[2]
                if action == "on" and name not in tools:
                    tools.append(name)
                elif action == "off" and name in tools:
                    tools.remove(name)
                console.print(f"Tools: {tools}")
                continue
            elif cmd == "/cap" and len(parts) >= 2:
                val = parts[1]
                capability = None if val == "none" else val
                console.print(f"Capability: {capability or 'chat'}")
                continue
            elif cmd == "/kb" and len(parts) >= 2:
                kb = parts[1] if parts[1] != "none" else None
                console.print(f"KB: {kb or 'none'}")
                continue
            else:
                console.print("[dim]Unknown command.[/]")
                continue

        ctx = UnifiedContext(
            user_message=user_input,
            conversation_history=history[-20:],
            enabled_tools=tools,
            active_capability=capability,
            knowledge_bases=[kb] if kb else [],
            language=language,
        )

        content_buf = ""
        async for event in orch.handle(ctx):
            if event.type == StreamEventType.STAGE_START:
                console.print(f"\n[bold cyan]▶ {event.stage}[/]", highlight=False)
            elif event.type == StreamEventType.THINKING:
                console.print(f"  [dim]{event.content}[/]", highlight=False)
            elif event.type == StreamEventType.CONTENT:
                content_buf += event.content
            elif event.type == StreamEventType.ERROR:
                console.print(f"[bold red]Error:[/] {event.content}")
            elif event.type in (StreamEventType.DONE, StreamEventType.STAGE_END):
                if content_buf:
                    console.print()
                    console.print(Markdown(content_buf))
                    content_buf = ""
            elif event.type == StreamEventType.PROGRESS:
                console.print(f"  [dim]{event.content}[/]", highlight=False)

        history.append({"role": "user", "content": user_input})
        if content_buf:
            history.append({"role": "assistant", "content": content_buf})

        console.print()


# ---- Typer command registration (called from main.py) ----


def register(app: typer.Typer) -> None:
    @app.callback(invoke_without_command=True)
    def chat(
        ctx: typer.Context,
        message: Optional[str] = typer.Argument(None, help="Message (single-shot mode)."),
        tool: list[str] = typer.Option([], "--tool", "-t", help="Enable tool(s)."),
        capability: Optional[str] = typer.Option(None, "--capability", "-c", help="Activate a capability."),
        kb: Optional[str] = typer.Option(None, "--kb", help="Knowledge base name."),
        language: str = typer.Option("en", "--language", "-l", help="Response language."),
        once: bool = typer.Option(False, "--once", help="Single-shot mode (no REPL)."),
        fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
    ) -> None:
        """Chat with DeepTutor."""
        if ctx.invoked_subcommand is not None:
            return

        if message or once:
            if not message:
                console.print("[red]Provide a message for single-shot mode.[/]")
                raise typer.Exit(code=1)
            asyncio.run(_run_once(message, tool, capability, kb, language, fmt))
        else:
            asyncio.run(_repl(tool, capability, kb, language))
