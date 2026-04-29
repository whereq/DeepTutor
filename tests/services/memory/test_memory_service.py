from __future__ import annotations

from deeptutor.services.memory.service import MemoryService
from deeptutor.services.session.sqlite_store import SQLiteSessionStore


def _make_service(tmp_path):
    store = SQLiteSessionStore(tmp_path / "chat_history.db")
    return MemoryService(
        path_service=type(
            "PathServiceStub",
            (),
            {"get_memory_dir": lambda self: tmp_path / "memory"},
        )(),
        store=store,
    )


def test_memory_service_snapshot_is_empty_without_file(tmp_path) -> None:
    service = _make_service(tmp_path)
    snapshot = service.read_snapshot()

    assert snapshot.summary == ""
    assert snapshot.profile == ""
    assert snapshot.summary_updated_at is None
    assert snapshot.profile_updated_at is None


async def _no_change_stream(**_kwargs):
    yield "NO_CHANGE"


async def _rewrite_stream(**_kwargs):
    yield "## Preferences\n- Prefer concise answers.\n\n## Context\n- Working on DeepTutor memory."


async def _thinking_rewrite_stream(**_kwargs):
    yield "<think>private reasoning</think>\n## Preferences\n- Prefer concise answers."


async def _unclosed_thinking_stream(**_kwargs):
    yield "## Current Focus\n- Algebra\n<think>unfinished private reasoning"


def test_memory_service_refresh_turn_writes_rewritten_document(monkeypatch, tmp_path) -> None:
    service = _make_service(tmp_path)
    monkeypatch.setattr("deeptutor.services.memory.service.llm_stream", _rewrite_stream)

    import asyncio

    result = asyncio.run(
        service.refresh_from_turn(
            user_message="Please remember that I like concise answers.",
            assistant_message="Sure, I'll keep answers concise.",
            session_id="s1",
            capability="chat",
            language="en",
        )
    )

    assert result.changed is True
    assert "concise answers" in result.content
    assert service._path("profile").exists() or service._path("summary").exists()


def test_memory_service_refresh_turn_skips_when_model_returns_no_change(
    monkeypatch,
    tmp_path,
) -> None:
    service = _make_service(tmp_path)
    monkeypatch.setattr("deeptutor.services.memory.service.llm_stream", _no_change_stream)

    import asyncio

    result = asyncio.run(
        service.refresh_from_turn(
            user_message="What is 2+2?",
            assistant_message="4",
            session_id="s1",
            capability="chat",
            language="en",
        )
    )

    assert result.changed is False
    assert result.content == ""
    assert not service._path("profile").exists()
    assert not service._path("summary").exists()


def test_memory_service_refresh_strips_thinking_tags(monkeypatch, tmp_path) -> None:
    service = _make_service(tmp_path)
    monkeypatch.setattr("deeptutor.services.memory.service.llm_stream", _thinking_rewrite_stream)

    import asyncio

    result = asyncio.run(
        service.refresh_from_turn(
            user_message="Please remember that I like concise answers.",
            assistant_message="Sure.",
            session_id="s1",
            capability="chat",
            language="en",
        )
    )

    assert result.changed is True
    profile = service.read_profile()
    summary = service.read_summary()
    assert "Prefer concise answers" in profile
    assert "<think" not in profile.lower()
    assert "private reasoning" not in profile
    assert "<think" not in summary.lower()
    assert "private reasoning" not in summary


def test_memory_service_refresh_strips_unclosed_thinking_tags(monkeypatch, tmp_path) -> None:
    service = _make_service(tmp_path)
    monkeypatch.setattr("deeptutor.services.memory.service.llm_stream", _unclosed_thinking_stream)

    import asyncio

    asyncio.run(
        service.refresh_from_turn(
            user_message="Study algebra.",
            assistant_message="Done.",
            session_id="s1",
            capability="chat",
            language="en",
        )
    )

    assert service.read_profile() == "## Current Focus\n- Algebra"
    assert "<think" not in service.read_summary().lower()


def test_memory_service_repairs_existing_thinking_tags_on_read(tmp_path) -> None:
    service = _make_service(tmp_path)
    service._path("summary").parent.mkdir(parents=True, exist_ok=True)
    service._path("summary").write_text(
        "## Current Focus\n- Algebra\n<think>old private reasoning</think>",
        encoding="utf-8",
    )

    assert service.read_summary() == "## Current Focus\n- Algebra"
    persisted = service._path("summary").read_text(encoding="utf-8")
    assert "<think" not in persisted.lower()
    assert "old private reasoning" not in persisted
