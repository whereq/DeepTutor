from __future__ import annotations

import importlib
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

FastAPI = pytest.importorskip("fastapi").FastAPI
TestClient = pytest.importorskip("fastapi.testclient").TestClient
wrong_answers_router = importlib.import_module(
    "deeptutor.api.routers.wrong_answers"
).router
sessions_router = importlib.import_module("deeptutor.api.routers.sessions").router

from deeptutor.services.session.sqlite_store import SQLiteSessionStore


def _build_app(store: SQLiteSessionStore) -> FastAPI:
    app = FastAPI()
    app.include_router(wrong_answers_router, prefix="/api/v1/wrong-answers")
    app.include_router(sessions_router, prefix="/api/v1/sessions")
    return app


@pytest.fixture
def store(tmp_path: Path, monkeypatch) -> SQLiteSessionStore:
    instance = SQLiteSessionStore(db_path=tmp_path / "router-test.db")
    monkeypatch.setattr(
        "deeptutor.api.routers.wrong_answers.get_sqlite_session_store",
        lambda: instance,
    )
    monkeypatch.setattr(
        "deeptutor.api.routers.sessions.get_sqlite_session_store",
        lambda: instance,
    )
    return instance


def test_list_wrong_answers_empty(store: SQLiteSessionStore) -> None:
    with TestClient(_build_app(store)) as client:
        response = client.get("/api/v1/wrong-answers")
        assert response.status_code == 200
        payload = response.json()
        assert payload == {"items": [], "total": 0}


def test_record_quiz_results_populates_wrong_answers(
    store: SQLiteSessionStore,
) -> None:
    import asyncio

    session = asyncio.run(store.create_session(title="Quiz Session"))
    session_id = session["id"]

    with TestClient(_build_app(store)) as client:

        resp = client.post(
            f"/api/v1/sessions/{session_id}/quiz-results",
            json={
                "answers": [
                    {
                        "question_id": "q1",
                        "question": "Capital of France?",
                        "user_answer": "Berlin",
                        "correct_answer": "Paris",
                        "is_correct": False,
                    },
                    {
                        "question_id": "q2",
                        "question": "2+2?",
                        "user_answer": "4",
                        "correct_answer": "4",
                        "is_correct": True,
                    },
                ]
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["recorded"] is True
        assert body["answer_count"] == 2
        assert body["wrong_answer_count"] == 1
        # Regression: the formatted text message is still added.
        assert "[Quiz Performance]" in body["content"]

        listing = client.get("/api/v1/wrong-answers")
        assert listing.status_code == 200
        items = listing.json()["items"]
        assert len(items) == 1
        assert items[0]["question_id"] == "q1"
        assert items[0]["resolved"] is False
        assert items[0]["session_title"] == "Quiz Session"


def test_update_wrong_answer_resolved_endpoint(
    store: SQLiteSessionStore,
) -> None:
    import asyncio

    session = asyncio.run(store.create_session())
    asyncio.run(
        store.add_wrong_answers(
            session["id"],
            [{"question": "Q?", "is_correct": False}],
        )
    )
    rows = asyncio.run(store.list_wrong_answers())
    row_id = rows[0]["id"]

    with TestClient(_build_app(store)) as client:
        resp = client.patch(
            f"/api/v1/wrong-answers/{row_id}",
            json={"resolved": True},
        )
        assert resp.status_code == 200
        assert resp.json() == {
            "updated": True,
            "id": row_id,
            "resolved": True,
        }

        listing = client.get(
            "/api/v1/wrong-answers", params={"resolved": "false"}
        )
        assert listing.json()["items"] == []

        not_found = client.patch(
            "/api/v1/wrong-answers/99999",
            json={"resolved": True},
        )
        assert not_found.status_code == 404


def test_delete_wrong_answer_endpoint(store: SQLiteSessionStore) -> None:
    import asyncio

    session = asyncio.run(store.create_session())
    asyncio.run(
        store.add_wrong_answers(
            session["id"],
            [{"question": "Q?", "is_correct": False}],
        )
    )
    row_id = asyncio.run(store.list_wrong_answers())[0]["id"]

    with TestClient(_build_app(store)) as client:
        resp = client.delete(f"/api/v1/wrong-answers/{row_id}")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": True, "id": row_id}

        missing = client.delete(f"/api/v1/wrong-answers/{row_id}")
        assert missing.status_code == 404


def test_list_wrong_answers_filter_by_resolved(
    store: SQLiteSessionStore,
) -> None:
    import asyncio

    session = asyncio.run(store.create_session())
    asyncio.run(
        store.add_wrong_answers(
            session["id"],
            [
                {"question": "Q1", "is_correct": False},
                {"question": "Q2", "is_correct": False},
            ],
        )
    )
    rows = asyncio.run(store.list_wrong_answers())
    asyncio.run(store.update_wrong_answer_resolved(rows[0]["id"], True))

    with TestClient(_build_app(store)) as client:
        all_resp = client.get("/api/v1/wrong-answers").json()
        assert all_resp["total"] == 2
        assert len(all_resp["items"]) == 2

        unresolved = client.get(
            "/api/v1/wrong-answers", params={"resolved": "false"}
        ).json()
        assert unresolved["total"] == 1
        assert len(unresolved["items"]) == 1
        assert unresolved["items"][0]["resolved"] is False

        resolved = client.get(
            "/api/v1/wrong-answers", params={"resolved": "true"}
        ).json()
        assert resolved["total"] == 1
        assert resolved["items"][0]["resolved"] is True
