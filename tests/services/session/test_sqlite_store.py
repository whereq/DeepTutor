from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path

import pytest

from deeptutor.services.path_service import PathService
from deeptutor.services.session.sqlite_store import SQLiteSessionStore


def test_sqlite_store_defaults_to_data_user_chat_history_db(tmp_path: Path) -> None:
    service = PathService.get_instance()
    original_root = service._project_root
    original_user_dir = service._user_data_dir

    try:
        service._project_root = tmp_path
        service._user_data_dir = tmp_path / "data" / "user"

        store = SQLiteSessionStore()

        assert store.db_path == tmp_path / "data" / "user" / "chat_history.db"
        assert store.db_path.exists()
    finally:
        service._project_root = original_root
        service._user_data_dir = original_user_dir


def test_sqlite_store_migrates_legacy_chat_history_db(tmp_path: Path) -> None:
    service = PathService.get_instance()
    original_root = service._project_root
    original_user_dir = service._user_data_dir

    try:
        service._project_root = tmp_path
        service._user_data_dir = tmp_path / "data" / "user"
        legacy_db = tmp_path / "data" / "chat_history.db"
        legacy_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(legacy_db) as conn:
            conn.execute("CREATE TABLE legacy (id INTEGER PRIMARY KEY)")
            conn.commit()

        store = SQLiteSessionStore()

        assert store.db_path.exists()
        assert not legacy_db.exists()
    finally:
        service._project_root = original_root
        service._user_data_dir = original_user_dir


@pytest.fixture
def store(tmp_path: Path) -> SQLiteSessionStore:
    return SQLiteSessionStore(db_path=tmp_path / "test.db")


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


def test_add_wrong_answers_only_persists_incorrect(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session(title="Test"))
    session_id = session["id"]

    items = [
        {
            "question_id": "q1",
            "question": "What is 2+2?",
            "user_answer": "5",
            "correct_answer": "4",
            "is_correct": False,
        },
        {
            "question_id": "q2",
            "question": "What is 3+3?",
            "user_answer": "6",
            "correct_answer": "6",
            "is_correct": True,
        },
        {
            "question_id": "q3",
            "question": "What is 5+5?",
            "user_answer": "9",
            "correct_answer": "10",
            "is_correct": False,
        },
    ]

    inserted = _run(store.add_wrong_answers(session_id, items))
    assert inserted == 2

    listed = _run(store.list_wrong_answers())
    assert len(listed) == 2
    question_ids = {row["question_id"] for row in listed}
    assert question_ids == {"q1", "q3"}
    assert all(row["resolved"] is False for row in listed)
    assert all(row["session_title"] == "Test" for row in listed)


def test_add_wrong_answers_skips_blank_questions(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    items = [
        {"question": "", "is_correct": False},
        {"question": "   ", "is_correct": False},
        {"question": "Valid?", "is_correct": False},
    ]
    inserted = _run(store.add_wrong_answers(session["id"], items))
    assert inserted == 1


def test_add_wrong_answers_unknown_session_raises(store: SQLiteSessionStore) -> None:
    with pytest.raises(ValueError, match="Session not found"):
        _run(
            store.add_wrong_answers(
                "does_not_exist",
                [{"question": "Q?", "is_correct": False}],
            )
        )


def test_list_wrong_answers_filters_by_resolved(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    session_id = session["id"]
    _run(
        store.add_wrong_answers(
            session_id,
            [
                {"question": "Q1", "is_correct": False},
                {"question": "Q2", "is_correct": False},
            ],
        )
    )
    listed = _run(store.list_wrong_answers())
    first_id = listed[0]["id"]
    _run(store.update_wrong_answer_resolved(first_id, True))

    unresolved = _run(store.list_wrong_answers(resolved=False))
    resolved = _run(store.list_wrong_answers(resolved=True))
    all_rows = _run(store.list_wrong_answers())

    assert len(unresolved) == 1
    assert unresolved[0]["id"] != first_id
    assert len(resolved) == 1
    assert resolved[0]["id"] == first_id
    assert resolved[0]["resolved"] is True
    assert resolved[0]["resolved_at"] is not None
    assert len(all_rows) == 2


def test_count_wrong_answers(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    _run(
        store.add_wrong_answers(
            session["id"],
            [
                {"question": "Q1", "is_correct": False},
                {"question": "Q2", "is_correct": False},
                {"question": "Q3", "is_correct": True},
            ],
        )
    )
    assert _run(store.count_wrong_answers()) == 2
    assert _run(store.count_wrong_answers(resolved=False)) == 2
    assert _run(store.count_wrong_answers(resolved=True)) == 0


def test_update_wrong_answer_resolved_roundtrip(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    _run(
        store.add_wrong_answers(
            session["id"],
            [{"question": "Q?", "is_correct": False}],
        )
    )
    rows = _run(store.list_wrong_answers())
    row_id = rows[0]["id"]

    assert _run(store.update_wrong_answer_resolved(row_id, True)) is True
    assert _run(store.list_wrong_answers())[0]["resolved"] is True

    assert _run(store.update_wrong_answer_resolved(row_id, False)) is True
    resurrected = _run(store.list_wrong_answers())[0]
    assert resurrected["resolved"] is False
    assert resurrected["resolved_at"] is None

    assert _run(store.update_wrong_answer_resolved(99999, True)) is False


def test_delete_wrong_answer(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    _run(
        store.add_wrong_answers(
            session["id"],
            [
                {"question": "Q1", "is_correct": False},
                {"question": "Q2", "is_correct": False},
            ],
        )
    )
    rows = _run(store.list_wrong_answers())
    first_id = rows[0]["id"]
    assert _run(store.delete_wrong_answer(first_id)) is True
    assert len(_run(store.list_wrong_answers())) == 1
    assert _run(store.delete_wrong_answer(99999)) is False


def test_wrong_answers_cascade_on_session_delete(store: SQLiteSessionStore) -> None:
    session = _run(store.create_session())
    _run(
        store.add_wrong_answers(
            session["id"],
            [{"question": "Q?", "is_correct": False}],
        )
    )
    assert len(_run(store.list_wrong_answers())) == 1
    _run(store.delete_session(session["id"]))
    assert _run(store.list_wrong_answers()) == []
