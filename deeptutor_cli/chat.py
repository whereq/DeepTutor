"""Chat and capability execution commands."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

import typer
from rich.panel import Panel

from deeptutor.app import DeepTutorApp, TurnRequest

from .common import build_turn_request, console, maybe_run, run_turn_and_render


@dataclass
class ChatState:
    session_id: str | None = None
    capability: str = "chat"
    tools: list[str] = field(default_factory=list)
    knowledge_bases: list[str] = field(default_factory=list)
    language: str = "en"
    notebook_references: list[dict[str, Any]] = field(default_factory=list)
    history_references: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


def register(app: typer.Typer) -> None:
    @app.callback(invoke_without_command=True)
    def chat(
        ctx: typer.Context,
        message: str | None = typer.Argument(None, help="Message to send."),
        tool: list[str] = typer.Option([], "--tool", "-t", help="Enable tool(s)."),
        capability: str = typer.Option("chat", "--capability", "-c", help="Capability name or alias."),
        kb: list[str] = typer.Option([], "--kb", help="Knowledge base name."),
        session: str | None = typer.Option(None, "--session", help="Existing session id."),
        notebook_ref: list[str] = typer.Option(
            [],
            "--notebook-ref",
            help="Notebook reference in NOTEBOOK_ID[:record_id,record_id] format.",
        ),
        history_ref: list[str] = typer.Option([], "--history-ref", help="Referenced session ids."),
        language: str = typer.Option("en", "--language", "-l", help="Response language."),
        config: list[str] = typer.Option([], "--config", help="Capability config key=value."),
        config_json: str | None = typer.Option(None, "--config-json", help="Capability config as JSON."),
        once: bool = typer.Option(False, "--once", help="Single-shot mode."),
        fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
    ) -> None:
        """Chat with DeepTutor through the unified turn runtime."""
        if ctx.invoked_subcommand is not None:
            return

        if message or once:
            if not message:
                console.print("[red]Provide a message for single-shot mode.[/]")
                raise typer.Exit(code=1)
            request = build_turn_request(
                content=message,
                capability=capability,
                session_id=session,
                tools=tool,
                knowledge_bases=kb,
                language=language,
                config_items=config,
                config_json=config_json,
                notebook_refs=notebook_ref,
                history_refs=history_ref,
            )
            maybe_run(_run_single_turn(request=request, fmt=fmt))
            return

        state = ChatState(
            session_id=session,
            capability=capability,
            tools=list(tool),
            knowledge_bases=list(kb),
            language=language,
            notebook_references=_parse_notebook_refs(notebook_ref),
            history_references=[item.strip() for item in history_ref if item.strip()],
            config=_merge_config(config, config_json),
        )
        maybe_run(_chat_repl(state))


async def _run_single_turn(*, request: TurnRequest, fmt: str) -> tuple[dict[str, Any], dict[str, Any]]:
    client = DeepTutorApp()
    return await run_turn_and_render(app=client, request=request, fmt=fmt)


async def _chat_repl(state: ChatState) -> None:
    client = DeepTutorApp()
    if state.session_id:
        existing = await client.get_session(state.session_id)
        if existing is None:
            console.print(f"[red]Session not found:[/] {state.session_id}")
            raise typer.Exit(code=1)
        preferences = existing.get("preferences", {}) or {}
        state.capability = str(preferences.get("capability") or state.capability or "chat")
        state.tools = list(preferences.get("tools") or state.tools)
        state.knowledge_bases = list(preferences.get("knowledge_bases") or state.knowledge_bases)
        state.language = str(preferences.get("language") or state.language)
        state.notebook_references = list(
            preferences.get("notebook_references") or state.notebook_references
        )
        state.history_references = list(
            preferences.get("history_references") or state.history_references
        )

    console.print(
        Panel(
            "[bold]DeepTutor CLI[/]\n"
            "直接输入消息即可继续对话。\n"
            "Commands:\n"
            "  /quit\n"
            "  /session\n"
            "  /new\n"
            "  /tool on <name> | /tool off <name>\n"
            "  /cap <name>\n"
            "  /kb <name>|none\n"
            "  /history add <session_id> | /history clear\n"
            "  /notebook add <id[:record1,record2]> | /notebook clear\n"
            "  /refs\n"
            "  /config show | /config set key=value | /config clear",
            title="deeptutor chat",
        )
    )
    _print_state(state)

    while True:
        try:
            user_input = console.input("[bold green]You>[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not user_input:
            continue
        if user_input.startswith("/"):
            should_continue = _apply_command(user_input, state)
            if should_continue:
                continue
            break

        request = TurnRequest(
            content=user_input,
            capability=state.capability,
            session_id=state.session_id,
            tools=list(state.tools),
            knowledge_bases=list(state.knowledge_bases),
            language=state.language,
            config=dict(state.config),
            notebook_references=list(state.notebook_references),
            history_references=list(state.history_references),
        )
        session, _turn = await run_turn_and_render(app=client, request=request, fmt="rich")
        state.session_id = str(session["id"])


def _apply_command(raw: str, state: ChatState) -> bool:
    parts = raw.split()
    command = parts[0].lower()
    if command == "/quit":
        return False
    if command == "/session":
        console.print(f"session={state.session_id or '(new)'}")
        return True
    if command == "/new":
        state.session_id = None
        console.print("[dim]Started a new chat context.[/]")
        return True
    if command == "/refs":
        _print_state(state)
        return True
    if command == "/tool" and len(parts) >= 3:
        action, tool_name = parts[1], parts[2]
        if action == "on" and tool_name not in state.tools:
            state.tools.append(tool_name)
        elif action == "off" and tool_name in state.tools:
            state.tools.remove(tool_name)
        _print_state(state)
        return True
    if command == "/cap" and len(parts) >= 2:
        state.capability = parts[1]
        _print_state(state)
        return True
    if command == "/kb" and len(parts) >= 2:
        value = parts[1]
        state.knowledge_bases = [] if value == "none" else [value]
        _print_state(state)
        return True
    if command == "/history" and len(parts) >= 2:
        if parts[1] == "clear":
            state.history_references = []
        elif parts[1] == "add" and len(parts) >= 3:
            state.history_references.append(parts[2])
        _print_state(state)
        return True
    if command == "/notebook" and len(parts) >= 2:
        if parts[1] == "clear":
            state.notebook_references = []
        elif parts[1] == "add" and len(parts) >= 3:
            state.notebook_references.extend(_parse_notebook_refs([parts[2]]))
        _print_state(state)
        return True
    if command == "/config" and len(parts) >= 2:
        subcommand = parts[1]
        if subcommand == "show":
            console.print_json(json.dumps(state.config, ensure_ascii=False))
        elif subcommand == "clear":
            state.config = {}
        elif subcommand == "set" and len(parts) >= 3:
            key, _, value = parts[2].partition("=")
            if key and value:
                state.config[key] = _parse_config_value(value)
        _print_state(state)
        return True

    console.print("[dim]Unknown command.[/]")
    return True


def _print_state(state: ChatState) -> None:
    console.print(
        "[dim]"
        f"session={state.session_id or '(new)'} "
        f"capability={state.capability} "
        f"tools={state.tools or '[]'} "
        f"kb={state.knowledge_bases or '[]'} "
        f"history={state.history_references or '[]'} "
        f"notebook_refs={state.notebook_references or '[]'}"
        "[/]",
        highlight=False,
    )


def _merge_config(config_items: list[str], config_json: str | None) -> dict[str, Any]:
    base = {}
    if config_json:
        parsed = json.loads(config_json)
        if not isinstance(parsed, dict):
            raise typer.BadParameter("--config-json must be a JSON object.")
        base.update(parsed)
    for item in config_items:
        key, sep, raw_value = item.partition("=")
        if not sep:
            raise typer.BadParameter(f"Invalid --config item `{item}`.")
        base[key.strip()] = _parse_config_value(raw_value.strip())
    return base


def _parse_notebook_refs(values: list[str]) -> list[dict[str, Any]]:
    refs = []
    for value in values:
        notebook_id, _, record_ids_part = value.partition(":")
        notebook_id = notebook_id.strip()
        if not notebook_id:
            raise typer.BadParameter(f"Invalid notebook reference `{value}`.")
        record_ids = [item.strip() for item in record_ids_part.split(",") if item.strip()]
        refs.append({"notebook_id": notebook_id, "record_ids": record_ids})
    return refs


def _parse_config_value(raw_value: str) -> Any:
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        lowered = raw_value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "none"}:
            return None
        return raw_value
