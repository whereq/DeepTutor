"""
SQLite-backed unified chat session store.
"""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from deeptutor.services.path_service import get_path_service


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


@dataclass
class TurnRecord:
    id: str
    session_id: str
    capability: str
    status: str
    error: str
    created_at: float
    updated_at: float
    finished_at: float | None
    last_seq: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "turn_id": self.id,
            "session_id": self.session_id,
            "capability": self.capability,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "finished_at": self.finished_at,
            "last_seq": self.last_seq,
        }


class SQLiteSessionStore:
    """Persist unified chat sessions and messages in a SQLite database."""

    def __init__(self, db_path: Path | None = None) -> None:
        path_service = get_path_service()
        self.db_path = db_path or path_service.get_chat_history_db()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_db(path_service)
        self._lock = asyncio.Lock()
        self._initialize()

    def _migrate_legacy_db(self, path_service) -> None:
        """Move the legacy ``data/chat_history.db`` into ``data/user/`` once."""
        legacy_path = path_service.project_root / "data" / "chat_history.db"
        if self.db_path.exists() or not legacy_path.exists() or legacy_path == self.db_path:
            return
        try:
            os.replace(legacy_path, self.db_path)
        except OSError:
            # Fall back to leaving the legacy DB in place if an OS-level move
            # is not possible; the new DB path will be initialized empty.
            pass

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT 'New conversation',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    compressed_summary TEXT DEFAULT '',
                    summary_up_to_msg_id INTEGER DEFAULT 0,
                    preferences_json TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL DEFAULT '',
                    capability TEXT DEFAULT '',
                    events_json TEXT DEFAULT '',
                    attachments_json TEXT DEFAULT '',
                    created_at REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session_created
                    ON messages(session_id, created_at, id);

                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
                    ON sessions(updated_at DESC);

                CREATE TABLE IF NOT EXISTS turns (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    capability TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'running',
                    error TEXT DEFAULT '',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    finished_at REAL
                );

                CREATE INDEX IF NOT EXISTS idx_turns_session_updated
                    ON turns(session_id, updated_at DESC);

                CREATE INDEX IF NOT EXISTS idx_turns_session_status
                    ON turns(session_id, status, updated_at DESC);

                CREATE TABLE IF NOT EXISTS turn_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turn_id TEXT NOT NULL REFERENCES turns(id) ON DELETE CASCADE,
                    seq INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT DEFAULT '',
                    stage TEXT DEFAULT '',
                    content TEXT DEFAULT '',
                    metadata_json TEXT DEFAULT '',
                    timestamp REAL NOT NULL,
                    created_at REAL NOT NULL,
                    UNIQUE(turn_id, seq)
                );

                CREATE INDEX IF NOT EXISTS idx_turn_events_turn_seq
                    ON turn_events(turn_id, seq);

                CREATE TABLE IF NOT EXISTS wrong_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    question_id TEXT DEFAULT '',
                    question TEXT NOT NULL,
                    user_answer TEXT DEFAULT '',
                    correct_answer TEXT DEFAULT '',
                    resolved INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    resolved_at REAL
                );

                CREATE INDEX IF NOT EXISTS idx_wrong_answers_session
                    ON wrong_answers(session_id, created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_wrong_answers_resolved
                    ON wrong_answers(resolved, created_at DESC);
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
            if "preferences_json" not in columns:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN preferences_json TEXT DEFAULT '{}'"
                )
            conn.commit()

    async def _run(self, fn, *args):
        async with self._lock:
            return await asyncio.to_thread(fn, *args)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_session_sync(self, title: str | None = None, session_id: str | None = None) -> dict[str, Any]:
        now = time.time()
        resolved_id = session_id or f"unified_{int(now * 1000)}_{uuid.uuid4().hex[:8]}"
        resolved_title = (title or "New conversation").strip() or "New conversation"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, compressed_summary, summary_up_to_msg_id)
                VALUES (?, ?, ?, ?, '', 0)
                """,
                (resolved_id, resolved_title[:100], now, now),
            )
            conn.commit()
        return {
            "id": resolved_id,
            "session_id": resolved_id,
            "title": resolved_title[:100],
            "created_at": now,
            "updated_at": now,
            "compressed_summary": "",
            "summary_up_to_msg_id": 0,
        }

    async def create_session(self, title: str | None = None, session_id: str | None = None) -> dict[str, Any]:
        return await self._run(self._create_session_sync, title, session_id)

    def _get_session_sync(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    s.id,
                    s.title,
                    s.created_at,
                    s.updated_at,
                    s.compressed_summary,
                    s.summary_up_to_msg_id,
                    s.preferences_json,
                    COALESCE(
                        (
                            SELECT t.status
                            FROM turns t
                            WHERE t.session_id = s.id
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        'idle'
                    ) AS status,
                    COALESCE(
                        (
                            SELECT t.id
                            FROM turns t
                            WHERE t.session_id = s.id AND t.status = 'running'
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS active_turn_id,
                    COALESCE(
                        (
                            SELECT t.capability
                            FROM turns t
                            WHERE t.session_id = s.id
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS capability
                FROM sessions
                s
                WHERE s.id = ?
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["session_id"] = payload["id"]
        payload["preferences"] = _json_loads(payload.pop("preferences_json", ""), {})
        return payload

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        return await self._run(self._get_session_sync, session_id)

    async def ensure_session(self, session_id: str | None = None) -> dict[str, Any]:
        if session_id:
            session = await self.get_session(session_id)
            if session is not None:
                return session
        return await self.create_session()

    @staticmethod
    def _serialize_turn(row: sqlite3.Row) -> dict[str, Any]:
        return TurnRecord(
            id=row["id"],
            session_id=row["session_id"],
            capability=row["capability"] or "",
            status=row["status"] or "running",
            error=row["error"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            finished_at=row["finished_at"],
            last_seq=row["last_seq"] if "last_seq" in row.keys() else 0,
        ).to_dict()

    def _create_turn_sync(self, session_id: str, capability: str = "") -> dict[str, Any]:
        now = time.time()
        turn_id = f"turn_{int(now * 1000)}_{uuid.uuid4().hex[:10]}"
        with self._connect() as conn:
            session = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if session is None:
                raise ValueError(f"Session not found: {session_id}")
            active = conn.execute(
                """
                SELECT id
                FROM turns
                WHERE session_id = ? AND status = 'running'
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
            if active is not None:
                raise RuntimeError(f"Session already has an active turn: {active['id']}")
            conn.execute(
                """
                INSERT INTO turns (id, session_id, capability, status, error, created_at, updated_at, finished_at)
                VALUES (?, ?, ?, 'running', '', ?, ?, NULL)
                """,
                (turn_id, session_id, capability or "", now, now),
            )
            conn.commit()
        return {
            "id": turn_id,
            "turn_id": turn_id,
            "session_id": session_id,
            "capability": capability or "",
            "status": "running",
            "error": "",
            "created_at": now,
            "updated_at": now,
            "finished_at": None,
            "last_seq": 0,
        }

    async def create_turn(self, session_id: str, capability: str = "") -> dict[str, Any]:
        return await self._run(self._create_turn_sync, session_id, capability)

    def _get_turn_sync(self, turn_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    t.*,
                    COALESCE((SELECT MAX(seq) FROM turn_events te WHERE te.turn_id = t.id), 0) AS last_seq
                FROM turns t
                WHERE t.id = ?
                """,
                (turn_id,),
            ).fetchone()
        if row is None:
            return None
        return self._serialize_turn(row)

    async def get_turn(self, turn_id: str) -> dict[str, Any] | None:
        return await self._run(self._get_turn_sync, turn_id)

    def _get_active_turn_sync(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    t.*,
                    COALESCE((SELECT MAX(seq) FROM turn_events te WHERE te.turn_id = t.id), 0) AS last_seq
                FROM turns t
                WHERE t.session_id = ? AND t.status = 'running'
                ORDER BY t.updated_at DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return self._serialize_turn(row)

    async def get_active_turn(self, session_id: str) -> dict[str, Any] | None:
        return await self._run(self._get_active_turn_sync, session_id)

    def _list_active_turns_sync(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    t.*,
                    COALESCE((SELECT MAX(seq) FROM turn_events te WHERE te.turn_id = t.id), 0) AS last_seq
                FROM turns t
                WHERE t.session_id = ? AND t.status = 'running'
                ORDER BY t.updated_at DESC
                """,
                (session_id,),
            ).fetchall()
        return [self._serialize_turn(row) for row in rows]

    async def list_active_turns(self, session_id: str) -> list[dict[str, Any]]:
        return await self._run(self._list_active_turns_sync, session_id)

    def _update_turn_status_sync(self, turn_id: str, status: str, error: str = "") -> bool:
        now = time.time()
        finished_at = now if status in {"completed", "failed", "cancelled"} else None
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE turns
                SET status = ?, error = ?, updated_at = ?, finished_at = ?
                WHERE id = ?
                """,
                (status, error or "", now, finished_at, turn_id),
            )
            conn.commit()
        return cur.rowcount > 0

    async def update_turn_status(self, turn_id: str, status: str, error: str = "") -> bool:
        return await self._run(self._update_turn_status_sync, turn_id, status, error)

    def _append_turn_event_sync(self, turn_id: str, event: dict[str, Any]) -> dict[str, Any]:
        now = time.time()
        with self._connect() as conn:
            turn = conn.execute("SELECT id, session_id FROM turns WHERE id = ?", (turn_id,)).fetchone()
            if turn is None:
                raise ValueError(f"Turn not found: {turn_id}")
            provided_seq = int(event.get("seq") or 0)
            if provided_seq > 0:
                seq = provided_seq
            else:
                row = conn.execute(
                    "SELECT COALESCE(MAX(seq), 0) AS last_seq FROM turn_events WHERE turn_id = ?",
                    (turn_id,),
                ).fetchone()
                seq = int(row["last_seq"]) + 1 if row else 1
            payload = dict(event)
            payload["seq"] = seq
            payload["turn_id"] = payload.get("turn_id") or turn_id
            payload["session_id"] = payload.get("session_id") or turn["session_id"]
            conn.execute(
                """
                INSERT OR REPLACE INTO turn_events (
                    turn_id, seq, type, source, stage, content, metadata_json, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn_id,
                    seq,
                    payload.get("type", ""),
                    payload.get("source", ""),
                    payload.get("stage", ""),
                    payload.get("content", "") or "",
                    _json_dumps(payload.get("metadata", {})),
                    float(payload.get("timestamp") or now),
                    now,
                ),
            )
            conn.execute(
                "UPDATE turns SET updated_at = ? WHERE id = ?",
                (now, turn_id),
            )
            conn.commit()
        return payload

    async def append_turn_event(self, turn_id: str, event: dict[str, Any]) -> dict[str, Any]:
        return await self._run(self._append_turn_event_sync, turn_id, event)

    def _get_turn_events_sync(self, turn_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT turn_id, seq, type, source, stage, content, metadata_json, timestamp
                FROM turn_events
                WHERE turn_id = ? AND seq > ?
                ORDER BY seq ASC
                """,
                (turn_id, max(0, int(after_seq))),
            ).fetchall()
            turn = conn.execute("SELECT session_id FROM turns WHERE id = ?", (turn_id,)).fetchone()
        session_id = turn["session_id"] if turn else ""
        return [
            {
                "type": row["type"],
                "source": row["source"] or "",
                "stage": row["stage"] or "",
                "content": row["content"] or "",
                "metadata": _json_loads(row["metadata_json"], {}),
                "session_id": session_id,
                "turn_id": row["turn_id"],
                "seq": row["seq"],
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    async def get_turn_events(self, turn_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        return await self._run(self._get_turn_events_sync, turn_id, after_seq)

    def _update_session_title_sync(self, session_id: str, title: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE sessions
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                ((title.strip() or "New conversation")[:100], time.time(), session_id),
            )
            conn.commit()
        return cur.rowcount > 0

    async def update_session_title(self, session_id: str, title: str) -> bool:
        return await self._run(self._update_session_title_sync, session_id, title)

    def _delete_session_sync(self, session_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
        return cur.rowcount > 0

    async def delete_session(self, session_id: str) -> bool:
        return await self._run(self._delete_session_sync, session_id)

    def _add_message_sync(
        self,
        session_id: str,
        role: str,
        content: str,
        capability: str = "",
        events: list[dict[str, Any]] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> int:
        now = time.time()
        with self._connect() as conn:
            session = conn.execute("SELECT id, title FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if session is None:
                raise ValueError(f"Session not found: {session_id}")

            cur = conn.execute(
                """
                INSERT INTO messages (
                    session_id, role, content, capability, events_json, attachments_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content or "",
                    capability or "",
                    _json_dumps(events or []),
                    _json_dumps(attachments or []),
                    now,
                ),
            )

            title = None
            if session["title"] == "New conversation" and role == "user":
                trimmed = (content or "").strip()
                if trimmed:
                    title = trimmed[:50] + ("..." if len(trimmed) > 50 else "")

            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )
            if title:
                conn.execute(
                    "UPDATE sessions SET title = ? WHERE id = ?",
                    (title, session_id),
                )
            conn.commit()
            return int(cur.lastrowid)

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        capability: str = "",
        events: list[dict[str, Any]] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> int:
        return await self._run(
            self._add_message_sync,
            session_id,
            role,
            content,
            capability,
            events,
            attachments,
        )

    def _serialize_message(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "role": row["role"],
            "content": row["content"],
            "capability": row["capability"] or "",
            "events": _json_loads(row["events_json"], []),
            "attachments": _json_loads(row["attachments_json"], []),
            "created_at": row["created_at"],
        }

    def _get_messages_sync(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, capability, events_json, attachments_json, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return [self._serialize_message(row) for row in rows]

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        return await self._run(self._get_messages_sync, session_id)

    def _get_messages_for_context_sync(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role, content
                FROM messages
                WHERE session_id = ?
                  AND role IN ('user', 'assistant', 'system')
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            {"id": row["id"], "role": row["role"], "content": row["content"] or ""}
            for row in rows
        ]

    async def get_messages_for_context(self, session_id: str) -> list[dict[str, Any]]:
        return await self._run(self._get_messages_for_context_sync, session_id)

    def _list_sessions_sync(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    s.id,
                    s.title,
                    s.created_at,
                    s.updated_at,
                    s.compressed_summary,
                    s.summary_up_to_msg_id,
                    s.preferences_json,
                    COUNT(m.id) AS message_count,
                    COALESCE(
                        (
                            SELECT t.status
                            FROM turns t
                            WHERE t.session_id = s.id
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        'idle'
                    ) AS status,
                    COALESCE(
                        (
                            SELECT t.id
                            FROM turns t
                            WHERE t.session_id = s.id AND t.status = 'running'
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS active_turn_id,
                    COALESCE(
                        (
                            SELECT t.capability
                            FROM turns t
                            WHERE t.session_id = s.id
                            ORDER BY t.updated_at DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS capability,
                    COALESCE(
                        (
                            SELECT m2.content
                            FROM messages m2
                            WHERE m2.session_id = s.id
                              AND TRIM(COALESCE(m2.content, '')) != ''
                            ORDER BY m2.id DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS last_message
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.id
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
        sessions = []
        for row in rows:
            payload = dict(row)
            payload["session_id"] = payload["id"]
            payload["preferences"] = _json_loads(payload.pop("preferences_json", ""), {})
            sessions.append(payload)
        return sessions

    async def list_sessions(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return await self._run(self._list_sessions_sync, limit, offset)

    def _update_summary_sync(self, session_id: str, summary: str, up_to_msg_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE sessions
                SET compressed_summary = ?, summary_up_to_msg_id = ?, updated_at = updated_at
                WHERE id = ?
                """,
                (summary, max(0, int(up_to_msg_id)), session_id),
            )
            conn.commit()
        return cur.rowcount > 0

    async def update_summary(self, session_id: str, summary: str, up_to_msg_id: int) -> bool:
        return await self._run(self._update_summary_sync, session_id, summary, up_to_msg_id)

    def _update_session_preferences_sync(self, session_id: str, preferences: dict[str, Any]) -> bool:
        with self._connect() as conn:
            current = conn.execute(
                "SELECT preferences_json FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if current is None:
                return False
            merged = {
                **_json_loads(current["preferences_json"], {}),
                **(preferences or {}),
            }
            cur = conn.execute(
                """
                UPDATE sessions
                SET preferences_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (_json_dumps(merged), time.time(), session_id),
            )
            conn.commit()
        return cur.rowcount > 0

    async def update_session_preferences(self, session_id: str, preferences: dict[str, Any]) -> bool:
        return await self._run(self._update_session_preferences_sync, session_id, preferences)

    async def get_session_with_messages(self, session_id: str) -> dict[str, Any] | None:
        session = await self.get_session(session_id)
        if session is None:
            return None
        session["messages"] = await self.get_messages(session_id)
        session["active_turns"] = await self.list_active_turns(session_id)
        return session

    def _add_wrong_answers_sync(
        self,
        session_id: str,
        items: list[dict[str, Any]],
    ) -> int:
        if not items:
            return 0
        now = time.time()
        with self._connect() as conn:
            session = conn.execute(
                "SELECT id FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if session is None:
                raise ValueError(f"Session not found: {session_id}")
            inserted = 0
            for item in items:
                if item.get("is_correct"):
                    continue
                question = (item.get("question") or "").strip()
                if not question:
                    continue
                conn.execute(
                    """
                    INSERT INTO wrong_answers (
                        session_id, question_id, question, user_answer,
                        correct_answer, resolved, created_at, resolved_at
                    ) VALUES (?, ?, ?, ?, ?, 0, ?, NULL)
                    """,
                    (
                        session_id,
                        item.get("question_id") or "",
                        question,
                        item.get("user_answer") or "",
                        item.get("correct_answer") or "",
                        now,
                    ),
                )
                inserted += 1
            conn.commit()
        return inserted

    async def add_wrong_answers(
        self,
        session_id: str,
        items: list[dict[str, Any]],
    ) -> int:
        return await self._run(self._add_wrong_answers_sync, session_id, items)

    def _list_wrong_answers_sync(
        self,
        resolved: bool | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                w.id,
                w.session_id,
                COALESCE(s.title, '') AS session_title,
                w.question_id,
                w.question,
                w.user_answer,
                w.correct_answer,
                w.resolved,
                w.created_at,
                w.resolved_at
            FROM wrong_answers w
            LEFT JOIN sessions s ON s.id = w.session_id
        """
        params: list[Any] = []
        if resolved is not None:
            query += " WHERE w.resolved = ?"
            params.append(1 if resolved else 0)
        query += " ORDER BY w.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [
            {
                "id": int(row["id"]),
                "session_id": row["session_id"],
                "session_title": row["session_title"] or "",
                "question_id": row["question_id"] or "",
                "question": row["question"],
                "user_answer": row["user_answer"] or "",
                "correct_answer": row["correct_answer"] or "",
                "resolved": bool(row["resolved"]),
                "created_at": float(row["created_at"]),
                "resolved_at": (
                    float(row["resolved_at"]) if row["resolved_at"] is not None else None
                ),
            }
            for row in rows
        ]

    async def list_wrong_answers(
        self,
        resolved: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return await self._run(
            self._list_wrong_answers_sync, resolved, limit, offset
        )

    def _count_wrong_answers_sync(self, resolved: bool | None) -> int:
        query = "SELECT COUNT(*) AS count FROM wrong_answers"
        params: tuple[Any, ...] = ()
        if resolved is not None:
            query += " WHERE resolved = ?"
            params = (1 if resolved else 0,)
        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["count"]) if row else 0

    async def count_wrong_answers(self, resolved: bool | None = None) -> int:
        return await self._run(self._count_wrong_answers_sync, resolved)

    def _update_wrong_answer_resolved_sync(
        self,
        wrong_answer_id: int,
        resolved: bool,
    ) -> bool:
        now = time.time() if resolved else None
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE wrong_answers
                SET resolved = ?, resolved_at = ?
                WHERE id = ?
                """,
                (1 if resolved else 0, now, wrong_answer_id),
            )
            conn.commit()
        return cur.rowcount > 0

    async def update_wrong_answer_resolved(
        self,
        wrong_answer_id: int,
        resolved: bool,
    ) -> bool:
        return await self._run(
            self._update_wrong_answer_resolved_sync, wrong_answer_id, resolved
        )

    def _delete_wrong_answer_sync(self, wrong_answer_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM wrong_answers WHERE id = ?",
                (wrong_answer_id,),
            )
            conn.commit()
        return cur.rowcount > 0

    async def delete_wrong_answer(self, wrong_answer_id: int) -> bool:
        return await self._run(self._delete_wrong_answer_sync, wrong_answer_id)


_instance: SQLiteSessionStore | None = None


def get_sqlite_session_store() -> SQLiteSessionStore:
    global _instance
    if _instance is None:
        _instance = SQLiteSessionStore()
    return _instance


__all__ = ["SQLiteSessionStore", "get_sqlite_session_store"]
