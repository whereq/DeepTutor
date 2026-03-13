"""CLI smoke tests for the standalone ``deeptutor-cli`` package."""

from __future__ import annotations

import json
from typing import Any

from typer.testing import CliRunner

from deeptutor.app import TurnRequest
from deeptutor_cli.main import app

runner = CliRunner()


def _install_fake_runtime(monkeypatch, captured_requests: list[TurnRequest]) -> None:
    async def _start_turn(self, request):  # noqa: ANN001
        if isinstance(request, dict):
            request = TurnRequest(**request)
        captured_requests.append(request)
        return {"id": request.session_id or "session-1"}, {"id": "turn-1"}

    async def _stream_turn(self, turn_id: str, after_seq: int = 0):  # noqa: ANN001
        yield {"type": "session", "turn_id": turn_id, "seq": after_seq}
        yield {"type": "stage_start", "stage": "responding"}
        yield {"type": "content", "content": "response body"}
        yield {"type": "result", "metadata": {"response": "response body"}}
        yield {"type": "done"}

    monkeypatch.setattr("deeptutor.app.facade.DeepTutorApp.start_turn", _start_turn)
    monkeypatch.setattr("deeptutor.app.facade.DeepTutorApp.stream_turn", _stream_turn)


def test_chat_cli_json_mode_supports_runtime_payloads(monkeypatch) -> None:
    captured_requests: list[TurnRequest] = []
    _install_fake_runtime(monkeypatch, captured_requests)

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
                "--history-ref",
                "session-old",
                "--notebook-ref",
                "nb1:rec1,rec2",
                *extra_args,
                "hello world",
            ],
        )

        assert result.exit_code == 0, result.output
        lines = [json.loads(line) for line in result.output.splitlines() if line.strip()]
        assert any(line["type"] == "result" for line in lines)

    assert len(captured_requests) == 5
    assert captured_requests[0].tools == ["rag"]
    assert captured_requests[0].knowledge_bases == ["demo-kb"]
    assert captured_requests[0].history_references == ["session-old"]
    assert captured_requests[0].notebook_references == [{"notebook_id": "nb1", "record_ids": ["rec1", "rec2"]}]
    assert captured_requests[-1].capability == "deep_research"


def test_chat_cli_rich_single_shot_mode_uses_turn_runtime(monkeypatch) -> None:
    captured_requests: list[TurnRequest] = []
    _install_fake_runtime(monkeypatch, captured_requests)

    result = runner.invoke(app, ["chat", "--once", "hello rich"])

    assert result.exit_code == 0, result.output
    assert "response body" in result.output
    assert captured_requests[0].capability == "chat"


def test_research_alias_maps_flags_to_typed_config(monkeypatch) -> None:
    captured_requests: list[TurnRequest] = []
    _install_fake_runtime(monkeypatch, captured_requests)

    result = runner.invoke(
        app,
        [
            "research",
            "--mode",
            "report",
            "--depth",
            "deep",
            "--source",
            "web",
            "--source",
            "papers",
            "compare retrieval stacks",
        ],
    )

    assert result.exit_code == 0, result.output
    request = captured_requests[0]
    assert request.capability == "deep_research"
    assert request.config == {
        "mode": "report",
        "depth": "deep",
        "sources": ["web", "papers"],
    }


def test_session_list_command_uses_shared_store(monkeypatch) -> None:
    async def _list_sessions(self, limit: int = 50, offset: int = 0):  # noqa: ANN001
        return [
            {
                "id": "session-1",
                "title": "Algebra",
                "capability": "chat",
                "status": "completed",
                "message_count": 4,
            }
        ]

    monkeypatch.setattr("deeptutor.app.facade.DeepTutorApp.list_sessions", _list_sessions)

    result = runner.invoke(app, ["session", "list"])

    assert result.exit_code == 0, result.output
    assert "session-1" in result.output
    assert "Algebra" in result.output
