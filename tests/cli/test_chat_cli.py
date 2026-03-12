"""CLI smoke tests for the unified chat entrypoint."""

from __future__ import annotations

import json
from typing import Any

from typer.testing import CliRunner

from src.cli.main import app
from src.core.stream import StreamEvent, StreamEventType

runner = CliRunner()


def _fake_handle_factory(captured_contexts: list[tuple[str | None, Any]]):
    async def _handle(self, ctx):  # noqa: ANN001
        captured_contexts.append((ctx.active_capability, ctx))
        label = ctx.active_capability or "chat"
        yield StreamEvent(type=StreamEventType.SESSION, source="orchestrator")
        yield StreamEvent(type=StreamEventType.STAGE_START, source=label, stage="responding")
        yield StreamEvent(
            type=StreamEventType.CONTENT,
            source=label,
            stage="responding",
            content=f"response for {label}",
        )
        yield StreamEvent(
            type=StreamEventType.RESULT,
            source=label,
            metadata={"response": f"response for {label}"},
        )
        yield StreamEvent(type=StreamEventType.DONE, source=label)

    return _handle


def test_chat_cli_json_mode_supports_all_capabilities(monkeypatch) -> None:
    captured_contexts: list[tuple[str | None, Any]] = []
    monkeypatch.setattr(
        "src.runtime.orchestrator.ChatOrchestrator.handle",
        _fake_handle_factory(captured_contexts),
    )

    capability_args = [
        [],
        ["--capability", "chat"],
        ["--capability", "deep_solve"],
        ["--capability", "deep_question"],
        ["--capability", "deep_research"],
    ]

    for extra_args in capability_args:
        result = runner.invoke(
            app,
            [
                "chat",
                "--once",
                "--format",
                "json",
                "--tool",
                "rag",
                "--kb",
                "demo-kb",
                *extra_args,
                "hello world",
            ],
        )

        assert result.exit_code == 0, result.output
        lines = [json.loads(line) for line in result.output.splitlines() if line.strip()]
        assert any(line["type"] == "result" for line in lines)

    assert len(captured_contexts) == 5
    assert captured_contexts[0][1].enabled_tools == ["rag"]
    assert captured_contexts[0][1].knowledge_bases == ["demo-kb"]
    assert captured_contexts[-1][0] == "deep_research"


def test_chat_cli_rich_single_shot_mode_no_longer_nests_event_loop(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.runtime.orchestrator.ChatOrchestrator.handle",
        _fake_handle_factory([]),
    )

    result = runner.invoke(app, ["chat", "--once", "hello rich"])

    assert result.exit_code == 0, result.output
    assert "response for chat" in result.output
