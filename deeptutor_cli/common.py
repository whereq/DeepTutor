"""Shared CLI helpers."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from deeptutor.app import DeepTutorApp, TurnRequest

from ._tool_result import ToolResultBuffer, ToolResultEntry

console = Console()

# Process-wide buffer that backs the ``/show`` REPL command. The buffer
# lives at module scope so a single ``deeptutor chat`` session shares one
# ring across turns; ``deeptutor run`` doesn't read it (single-shot mode),
# but populating it is harmless.
tool_results = ToolResultBuffer()


def parse_config_items(items: list[str]) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for item in items:
        key, sep, raw_value = item.partition("=")
        if not sep or not key.strip():
            raise ValueError(f"Invalid --config item `{item}`. Expected KEY=VALUE.")
        config[key.strip()] = _parse_scalar_value(raw_value.strip())
    return config


def parse_json_object(raw: str | None) -> dict[str, Any]:
    normalized = (raw or "").strip()
    if not normalized:
        return {}
    try:
        value = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON config: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON config must be an object.")
    return value


def parse_notebook_references(items: list[str]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for item in items:
        notebook_id, _, record_part = item.partition(":")
        resolved_notebook_id = notebook_id.strip()
        if not resolved_notebook_id:
            raise ValueError(f"Invalid notebook reference `{item}`.")
        record_ids = [
            record_id.strip() for record_id in record_part.split(",") if record_id.strip()
        ]
        refs.append({"notebook_id": resolved_notebook_id, "record_ids": record_ids})
    return refs


async def run_turn_and_render(
    *,
    app: DeepTutorApp,
    request: TurnRequest,
    fmt: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    session, turn = await app.start_turn(request)

    if fmt == "json":
        async for item in app.stream_turn(turn["id"]):
            console.print(json.dumps(item, ensure_ascii=False))
        return session, turn

    await render_turn_stream(app=app, turn_id=turn["id"])
    console.print(
        f"[dim]session={session['id']} turn={turn['id']} capability={request.capability}[/]",
        highlight=False,
    )
    return session, turn


async def regenerate_and_render(
    *,
    app: DeepTutorApp,
    session_id: str,
    capability: str = "chat",
    fmt: str = "rich",
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    try:
        session, turn = await app.regenerate_last_turn(session_id)
    except RuntimeError as exc:
        reason = str(exc)
        if reason == "regenerate_busy":
            console.print(
                "[yellow]Cannot regenerate while another turn is running. "
                "Wait for it to finish or cancel it first.[/]"
            )
        elif reason == "nothing_to_regenerate":
            console.print("[yellow]Nothing to regenerate yet — send a message first.[/]")
        else:
            console.print(f"[red]Regenerate failed:[/] {reason}")
        return None

    if fmt == "json":
        async for item in app.stream_turn(turn["id"]):
            console.print(json.dumps(item, ensure_ascii=False))
        return session, turn

    await render_turn_stream(app=app, turn_id=turn["id"])
    console.print(
        f"[dim]session={session['id']} turn={turn['id']} capability={capability} (regenerated)[/]",
        highlight=False,
    )
    return session, turn


async def render_turn_stream(*, app: DeepTutorApp, turn_id: str) -> None:
    content_buf = ""
    current_stage = ""
    async for item in app.stream_turn(turn_id):
        event_type = str(item.get("type", ""))
        if event_type == "stage_start":
            if content_buf:
                console.print(Markdown(content_buf))
                content_buf = ""
            current_stage = str(item.get("stage", "") or "")
            console.print(f"\n[bold cyan]▶ {current_stage or 'working'}[/]", highlight=False)
        elif event_type == "stage_end":
            if content_buf:
                console.print(Markdown(content_buf))
                content_buf = ""
            current_stage = ""
        elif event_type == "thinking":
            console.print(f"  [dim]{item.get('content', '')}[/]", highlight=False)
        elif event_type == "progress":
            console.print(f"  [dim]{item.get('content', '')}[/]", highlight=False)
        elif event_type == "content":
            content_buf += str(item.get("content", "") or "")
        elif event_type == "tool_call":
            _render_tool_call(item)
        elif event_type == "tool_result":
            _render_tool_result(item)
        elif event_type == "error":
            console.print(f"[bold red]Error:[/] {item.get('content', '')}")
        elif event_type == "done":
            if content_buf:
                console.print(Markdown(content_buf))
                content_buf = ""


def _render_tool_call(item: dict[str, Any]) -> None:
    """Print a one-line tool-call header. Long arg payloads are summarised
    so the call stays scannable; the full body lands in tool_result if the
    tool echoes it back, or in the stream metadata for debug tooling."""

    tool_name = str(item.get("content", "") or "tool")
    metadata = item.get("metadata", {}) or {}
    args = metadata.get("args", {})
    # Budget the args summary so the whole header — "  ● <name>(<args>)" —
    # fits the current terminal width on one line. We pick a soft floor so
    # very narrow terminals still get something useful.
    overhead = len(f"  ● {tool_name}()")
    budget = max(20, (console.width or 100) - overhead)
    summary = _summarize_call_args(args, max_len=budget)
    if summary:
        console.print(f"  [yellow]●[/] {tool_name}([dim]{summary}[/])", highlight=False)
    else:
        console.print(f"  [yellow]●[/] {tool_name}", highlight=False)


def _render_tool_result(item: dict[str, Any]) -> None:
    """Print a truncated preview of a tool result, stashing the full text
    in the shared :data:`tool_results` buffer so ``/show`` can expand it."""

    body = str(item.get("content", "") or "")
    metadata = item.get("metadata", {}) or {}
    label = str(metadata.get("tool") or "tool")
    entry = tool_results.remember(label, body)
    head, hidden = tool_results.truncate(body)

    # Empty result still gets a marker so the user can see the call closed.
    if not head.strip() and not hidden:
        console.print(
            f"  [green]└[/] [dim]#{entry.index} {label} → (empty result)[/]", highlight=False
        )
        return

    if head:
        for line in head.split("\n"):
            console.print(f"  [green]│[/] {line}", highlight=False)
    if hidden:
        console.print(
            f"  [green]└[/] [dim]#{entry.index} {label} — +{hidden} more line"
            f"{'s' if hidden != 1 else ''}; "
            f"run [bold]/show {entry.index}[/] (or [bold]/show last[/]) to expand[/]",
            highlight=False,
        )
    else:
        console.print(f"  [green]└[/] [dim]#{entry.index} {label}[/]", highlight=False)


def _summarize_call_args(args: Any, max_len: int = 120) -> str:
    """Render call args as a short ``key=value, …`` string.

    The full rendering is assembled first, then a single trailing-ellipsis
    clip is applied so we never leave a dangling ``", "`` at the end when
    the last key's value runs over the budget.
    """

    if isinstance(args, dict) and args:
        rendered = ", ".join(f"{key}={_one_line(value)}" for key, value in args.items())
    elif args:
        rendered = _one_line(args)
    else:
        return ""
    if len(rendered) > max_len:
        return rendered[: max_len - 1].rstrip(", ") + "…"
    return rendered


def _one_line(value: Any) -> str:
    """Compact one-line repr for a single arg value. No truncation here —
    the caller's overall budget handles that uniformly so we don't double-
    clip a dict and end up with a half-finished key=value pair."""

    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            text = repr(value)
    return text.replace("\n", " ")


def render_tool_result_entry(entry: ToolResultEntry) -> None:
    """Fully print a stored tool result. Backs the ``/show`` REPL command."""

    from rich.panel import Panel

    console.print(
        Panel(
            entry.body or "[dim](empty result)[/]",
            title=f"#{entry.index} {entry.label}",
            border_style="green",
        ),
        highlight=False,
    )


def build_turn_request(
    *,
    content: str,
    capability: str,
    session_id: str | None,
    tools: list[str],
    knowledge_bases: list[str],
    language: str,
    config_items: list[str],
    config_json: str | None,
    notebook_refs: list[str],
    history_refs: list[str],
) -> TurnRequest:
    config = parse_json_object(config_json)
    config.update(parse_config_items(config_items))
    return TurnRequest(
        content=content,
        capability=capability,
        session_id=session_id,
        tools=tools,
        knowledge_bases=knowledge_bases,
        language=language,
        config=config,
        notebook_references=parse_notebook_references(notebook_refs),
        history_references=[item.strip() for item in history_refs if item.strip()],
    )


def maybe_run(coro):  # noqa: ANN001
    return asyncio.run(coro)


def print_session_table(sessions: list[dict[str, Any]]) -> None:
    table = Table(title="Sessions")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Capability")
    table.add_column("Status")
    table.add_column("Messages", justify="right")
    for session in sessions:
        table.add_row(
            str(session.get("id", "")),
            str(session.get("title", "")),
            str(session.get("capability", "") or "chat"),
            str(session.get("status", "")),
            str(session.get("message_count", 0)),
        )
    console.print(table)


def print_notebook_table(notebooks: list[dict[str, Any]]) -> None:
    table = Table(title="Notebooks")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Records", justify="right")
    table.add_column("Description")
    for notebook in notebooks:
        table.add_row(
            str(notebook.get("id", "")),
            str(notebook.get("name", "")),
            str(notebook.get("record_count", 0)),
            str(notebook.get("description", "")),
        )
    console.print(table)


def print_path_result(path: str | Path) -> None:
    console.print(f"[dim]{Path(path).resolve()}[/]")


def _parse_scalar_value(raw_value: str) -> Any:
    lowered = raw_value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value
