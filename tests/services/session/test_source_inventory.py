"""Unit tests for the cumulative source inventory used by the chat capability."""

from __future__ import annotations

from typing import Any

import pytest

from deeptutor.services.session.source_inventory import (
    SourceEntry,
    SourceInventory,
    build_inventory,
    render_manifest,
)


class FakeStore:
    """Minimal store fake covering the protocol methods source_inventory
    actually calls: get_messages, get_session, get_messages_for_context,
    get_notebook_entry. Tests inject the data they want via constructor."""

    def __init__(
        self,
        *,
        messages: list[dict[str, Any]] | None = None,
        sessions: dict[str, dict[str, Any]] | None = None,
        session_messages: dict[str, list[dict[str, Any]]] | None = None,
        notebook_entries: dict[int, dict[str, Any]] | None = None,
    ) -> None:
        self._messages = messages or []
        self._sessions = sessions or {}
        self._session_messages = session_messages or {}
        self._notebook_entries = notebook_entries or {}

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        return self._messages

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    async def get_messages_for_context(
        self, session_id: str, leaf_message_id: int | None = None
    ) -> list[dict[str, Any]]:
        return self._session_messages.get(session_id, [])

    async def get_notebook_entry(self, entry_id: int) -> dict[str, Any] | None:
        return self._notebook_entries.get(entry_id)


# ---------------------------------------------------------------------------
# SourceInventory dataclass
# ---------------------------------------------------------------------------


def test_inventory_dedupe_fresh_wins() -> None:
    inv = SourceInventory()
    inv.add(SourceEntry(sid="at-foo", kind="attachment", name="old", full_text="old text", fresh=False, first_seen_turn=1))
    inv.add(SourceEntry(sid="at-foo", kind="attachment", name="fresh", full_text="fresh text", fresh=True, first_seen_turn=2))
    assert len(inv.entries) == 1
    assert inv.entries[0].fresh is True
    assert inv.entries[0].name == "fresh"


def test_inventory_skips_empty_text() -> None:
    inv = SourceInventory()
    inv.add(SourceEntry(sid="at-foo", kind="attachment", name="empty", full_text="   ", fresh=True, first_seen_turn=1))
    assert inv.is_empty()


def test_inventory_preserves_insertion_order() -> None:
    inv = SourceInventory()
    inv.add(SourceEntry(sid="a", kind="attachment", name="A", full_text="A", fresh=True, first_seen_turn=1))
    inv.add(SourceEntry(sid="b", kind="attachment", name="B", full_text="B", fresh=False, first_seen_turn=1))
    inv.add(SourceEntry(sid="c", kind="notebook", name="C", full_text="C", fresh=True, first_seen_turn=1))
    assert [e.sid for e in inv.entries] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# render_manifest
# ---------------------------------------------------------------------------


def test_render_manifest_empty() -> None:
    text, idx = render_manifest(SourceInventory())
    assert text == ""
    assert idx == {}


def test_render_manifest_distinguishes_fresh_vs_historical() -> None:
    inv = SourceInventory()
    inv.add(SourceEntry(sid="at-fresh", kind="attachment", name="new.pdf", full_text="hello world", fresh=True, first_seen_turn=3))
    inv.add(SourceEntry(sid="at-old", kind="attachment", name="old.pdf", full_text="x" * 5000, fresh=False, first_seen_turn=1))
    text, idx = render_manifest(inv)
    # Fresh row carries a preview field
    assert "preview:" in text
    assert "'hello world'" in text
    # Historical row carries "previously attached (turn 1)" with no preview
    assert "previously attached (turn 1)" in text
    assert "size=" in text
    # source_index has full text for both
    assert idx["at-fresh"] == "hello world"
    assert idx["at-old"] == "x" * 5000


# ---------------------------------------------------------------------------
# build_inventory
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_inventory_fresh_attachments_only() -> None:
    store = FakeStore()
    inv = await build_inventory(
        store,
        session_id="s1",
        leaf_message_id=None,
        current_turn_ordinal=1,
        fresh_attachment_records=[
            {"id": "a1", "type": "pdf", "filename": "x.pdf", "extracted_text": "PDF body"},
            {"id": "img", "type": "image", "filename": "p.png", "extracted_text": ""},  # skipped
        ],
        fresh_notebook_records=[],
        fresh_book_context_text="",
        fresh_book_references=[],
        fresh_history_session_ids=[],
        fresh_question_entry_ids=[],
    )
    assert [e.sid for e in inv.entries] == ["at-a1"]
    assert inv.entries[0].fresh is True


@pytest.mark.asyncio
async def test_build_inventory_historical_attachment_visible_to_next_turn() -> None:
    """Attachment uploaded in turn 1 must appear as 'previously attached
    (turn 1)' in turn 2's manifest, even though turn 2's payload is empty."""
    past = [
        {
            "id": 1,
            "role": "user",
            "content": "first message",
            "parent_message_id": None,
            "attachments": [
                {"id": "att-1", "filename": "year1-1.pdf", "extracted_text": "lecture notes", "mime_type": "application/pdf"}
            ],
            "metadata": {"request_snapshot": {}},
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "ok",
            "parent_message_id": 1,
            "attachments": [],
            "metadata": {},
        },
    ]
    store = FakeStore(messages=past)
    inv = await build_inventory(
        store,
        session_id="s1",
        leaf_message_id=None,  # legacy linear; lineage walker returns all
        current_turn_ordinal=2,
        fresh_attachment_records=[],
        fresh_notebook_records=[],
        fresh_book_context_text="",
        fresh_book_references=[],
        fresh_history_session_ids=[],
        fresh_question_entry_ids=[],
    )
    assert [e.sid for e in inv.entries] == ["at-att-1"]
    e = inv.entries[0]
    assert e.fresh is False
    assert e.first_seen_turn == 1
    assert e.full_text == "lecture notes"


@pytest.mark.asyncio
async def test_build_inventory_branch_isolated() -> None:
    """Branch B should not see attachments uploaded in a sibling branch A."""
    # Layout:
    #   1 (user, root) → 2 (assistant) → 3 (user, branch A, attaches X.pdf)
    #                                  → 4 (user, branch B, attaches Y.pdf)
    # When we ask for branch B (leaf=4), only 1, 2, 4 are in lineage.
    msgs = [
        {"id": 1, "role": "user", "content": "q1", "parent_message_id": None,
         "attachments": [], "metadata": {"request_snapshot": {}}},
        {"id": 2, "role": "assistant", "content": "a1", "parent_message_id": 1,
         "attachments": [], "metadata": {}},
        {"id": 3, "role": "user", "content": "branch A", "parent_message_id": 2,
         "attachments": [{"id": "X", "filename": "X.pdf", "extracted_text": "branchA only", "mime_type": "application/pdf"}],
         "metadata": {"request_snapshot": {}}},
        {"id": 4, "role": "user", "content": "branch B", "parent_message_id": 2,
         "attachments": [{"id": "Y", "filename": "Y.pdf", "extracted_text": "branchB only", "mime_type": "application/pdf"}],
         "metadata": {"request_snapshot": {}}},
    ]
    store = FakeStore(messages=msgs)
    # Render branch B's inventory (leaf=4) — should see Y, not X.
    inv = await build_inventory(
        store,
        session_id="s1",
        leaf_message_id=4,
        current_turn_ordinal=3,
        fresh_attachment_records=[],
        fresh_notebook_records=[],
        fresh_book_context_text="",
        fresh_book_references=[],
        fresh_history_session_ids=[],
        fresh_question_entry_ids=[],
    )
    sids = [e.sid for e in inv.entries]
    assert "at-Y" in sids, sids
    assert "at-X" not in sids, sids


@pytest.mark.asyncio
async def test_build_inventory_fresh_shadows_historical_on_same_sid() -> None:
    """If a notebook record is referenced both in a past turn and this
    turn, the manifest shows it as fresh (with preview), not historical."""
    msgs = [
        {"id": 1, "role": "user", "content": "earlier",
         "parent_message_id": None, "attachments": [],
         "metadata": {"request_snapshot": {}}},
    ]
    store = FakeStore(messages=msgs)
    # Fresh record matching what historical *would have* added if it had
    # one — but historical lineage has empty snap, so only fresh is added.
    inv = await build_inventory(
        store,
        session_id="s1",
        leaf_message_id=None,
        current_turn_ordinal=2,
        fresh_attachment_records=[
            {"id": "att-1", "filename": "f.pdf", "extracted_text": "fresh body", "mime_type": "application/pdf"}
        ],
        fresh_notebook_records=[],
        fresh_book_context_text="",
        fresh_book_references=[],
        fresh_history_session_ids=[],
        fresh_question_entry_ids=[],
    )
    assert inv.entries[0].fresh is True
    assert inv.entries[0].full_text == "fresh body"
