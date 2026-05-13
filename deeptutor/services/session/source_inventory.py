"""Branch-isolated, cumulative source inventory for the chat capability.

The chat pipeline shows the LLM an "Attached Sources" manifest each turn so
it can decide whether to call ``read_source(id)`` for full text. Historically
this manifest only listed sources the user attached in the *current* turn —
so the model forgot anything uploaded in earlier turns unless re-attached.

This module materialises the manifest as a **session-cumulative inventory**:

* Sources attached in the current turn (the "fresh" set) get a full preview
  in the manifest, just like before.
* Sources attached in *prior* turns on the active branch's ancestor chain
  (the "historical" set) get a compact one-line row: id, name, kind, size,
  and the turn ordinal where they first appeared. The LLM can call
  ``read_source(id)`` to load full text when the question warrants it.

Both sets dedupe by source id; fresh always wins on collision. Branch
isolation is enforced by walking ``parent_message_id`` from the active
branch's leaf, so sibling branches never leak sources into each other.

The output is decoupled from the rest of ``turn_runtime``:

    inventory = await build_inventory(store, ..., fresh_*=...)
    manifest_text, source_index = render_manifest(inventory)

``source_index`` is the per-turn ``{source_id: full_text}`` map handed to
``ReadSourceTool`` via tool-call kwargs injection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

from deeptutor.services.session.protocol import SessionStoreProtocol

logger = logging.getLogger(__name__)

# Per-source text-preview caps. Fresh sources get a meaningful preview so
# the model can answer simple "is this the right one?" questions without
# read_source. Historical sources surface only their identity — the model
# pays the read_source cost only when it actually needs them.
MANIFEST_PREVIEW_CHARS_FRESH = 2000
# Image attachments flow through the multimodal block path; never list them.
_IMAGE_MIME_PREFIX = "image/"


@dataclass(frozen=True)
class SourceEntry:
    """One row in the per-turn Attached Sources manifest."""

    sid: str
    kind: str  # "notebook" | "book" | "history" | "question" | "attachment"
    name: str
    full_text: str
    fresh: bool
    # 1-indexed ordinal of the user turn this source first appeared in,
    # within the active branch's lineage. Fresh sources use the **current**
    # turn's ordinal so the manifest can label them consistently.
    first_seen_turn: int

    @property
    def char_count(self) -> int:
        return len(self.full_text)


@dataclass
class SourceInventory:
    """Ordered set of ``SourceEntry`` keyed by ``sid``.

    ``add`` is the only mutator. On duplicate ``sid`` the existing entry is
    upgraded to ``fresh=True`` if the incoming entry is fresh — so a source
    attached in the current turn always renders with a preview even if it
    was also attached in a prior turn.
    """

    entries: list[SourceEntry] = field(default_factory=list)
    _index: dict[str, int] = field(default_factory=dict, repr=False)

    def add(self, entry: SourceEntry) -> None:
        if not entry.sid:
            return
        if not entry.full_text.strip():
            return
        existing_pos = self._index.get(entry.sid)
        if existing_pos is None:
            self._index[entry.sid] = len(self.entries)
            self.entries.append(entry)
            return
        existing = self.entries[existing_pos]
        # Fresh always wins; otherwise keep the earlier registration.
        if entry.fresh and not existing.fresh:
            self.entries[existing_pos] = entry

    def is_empty(self) -> bool:
        return not self.entries

    def __contains__(self, sid: str) -> bool:
        return sid in self._index


# ---------------------------------------------------------------------------
# Public API: build + render
# ---------------------------------------------------------------------------


async def build_inventory(
    store: SessionStoreProtocol,
    *,
    session_id: str,
    leaf_message_id: int | None,
    current_turn_ordinal: int,
    fresh_attachment_records: Sequence[dict[str, Any]],
    fresh_notebook_records: Sequence[dict[str, Any]],
    fresh_book_context_text: str,
    fresh_book_references: Sequence[dict[str, Any]],
    fresh_history_session_ids: Sequence[Any],
    fresh_question_entry_ids: Sequence[Any],
) -> SourceInventory:
    """Compose the session-cumulative inventory for one chat turn.

    Fresh refs are added first (so they shadow historical entries on the
    same sid); historical refs are then collected from the active branch's
    ancestor messages. The caller passes already-resolved notebook records
    and the already-rendered book context — keeping side-effects (LLM
    summarisation, file I/O) under the caller's control rather than buried
    inside this module.
    """
    inv = SourceInventory()
    _add_fresh(
        inv,
        current_turn_ordinal=current_turn_ordinal,
        attachment_records=fresh_attachment_records,
        notebook_records=fresh_notebook_records,
        book_context_text=fresh_book_context_text,
        book_references=fresh_book_references,
    )
    # History + question entries are async (per-id store fetches), keep them
    # in a separate phase so the sync fresh additions don't block.
    await _add_fresh_history(
        inv,
        store=store,
        history_session_ids=fresh_history_session_ids,
        current_turn_ordinal=current_turn_ordinal,
    )
    await _add_fresh_questions(
        inv,
        store=store,
        question_entry_ids=fresh_question_entry_ids,
        current_turn_ordinal=current_turn_ordinal,
    )
    await _add_historical(
        inv, store=store, session_id=session_id, leaf_message_id=leaf_message_id
    )
    return inv


def render_manifest(inv: SourceInventory) -> tuple[str, dict[str, str]]:
    """Render the inventory into (manifest_text, source_index).

    ``manifest_text`` is the human/LLM-readable block injected at the tail
    of the chat system prompt. ``source_index`` maps each source id to its
    full extracted text and is handed to ``ReadSourceTool`` so the LLM can
    read on demand.
    """
    if inv.is_empty():
        return "", {}

    source_index: dict[str, str] = {sid: e.full_text for sid, e in _iter_sid_entries(inv)}
    rendered_rows: list[str] = []
    for entry in inv.entries:
        rendered_rows.append(_render_row(entry))

    header = (
        "[Attached Sources]\n"
        "Sources the user has attached in this conversation. Rows marked "
        "`previously attached (turn N)` were uploaded in earlier turns and "
        "show only their identity — call `read_source(source_id)` to load "
        "their full text when the question warrants it. Rows with a "
        "`preview` field were attached **this turn** and the preview is "
        "often enough to answer without another tool call. Never invent "
        "source ids."
    )
    return header + "\n\n" + "\n\n".join(rendered_rows), source_index


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _iter_sid_entries(inv: SourceInventory):
    seen: set[str] = set()
    for e in inv.entries:
        if e.sid in seen:
            continue
        seen.add(e.sid)
        yield e.sid, e


def _clip_preview(text: str, limit: int = MANIFEST_PREVIEW_CHARS_FRESH) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "…"


def _format_size(char_count: int) -> str:
    """Compact size hint for historical rows ('~3 KB', '~120 chars')."""
    if char_count >= 1024:
        return f"~{round(char_count / 1024)} KB"
    return f"~{char_count} chars"


def _render_row(entry: SourceEntry) -> str:
    if entry.fresh:
        preview = _clip_preview(entry.full_text)
        return (
            f"- id={entry.sid}  type={entry.kind}  name={entry.name!r}\n"
            f"  preview: {preview!r}"
        )
    return (
        f"- id={entry.sid}  type={entry.kind}  name={entry.name!r}"
        f"  size={_format_size(entry.char_count)}  "
        f"source: previously attached (turn {entry.first_seen_turn})"
    )


# ----- Fresh source addition (current-turn payload) -----------------------


def _add_fresh(
    inv: SourceInventory,
    *,
    current_turn_ordinal: int,
    attachment_records: Sequence[dict[str, Any]],
    notebook_records: Sequence[dict[str, Any]],
    book_context_text: str,
    book_references: Sequence[dict[str, Any]],
) -> None:
    """Add the synchronously-available fresh sources (notebook records,
    book pages, attachments)."""
    for rec in notebook_records:
        rid = str(rec.get("id", "") or "").strip()
        full = str(rec.get("output", "") or "")
        if not rid or not full.strip():
            continue
        inv.add(
            SourceEntry(
                sid=f"nb-{rid}",
                kind="notebook",
                name=str(rec.get("title") or rec.get("name") or "Untitled record"),
                full_text=full,
                fresh=True,
                first_seen_turn=current_turn_ordinal,
            )
        )

    # Books: split the cumulative ``build_book_context`` output by the
    # ``---`` section separator so each book gets its own ``bk-{book_id}``
    # sid. The order in ``book_references`` matches the order
    # ``build_book_context`` produces sections in, so we can zip them.
    book_sections = _split_book_sections(book_context_text)
    for ref, section in zip(book_references, book_sections, strict=False):
        book_id = str(ref.get("book_id") or "").strip()
        if not book_id or not section.strip():
            continue
        inv.add(
            SourceEntry(
                sid=f"bk-{book_id}",
                kind="book",
                name=_extract_book_title(section, fallback=f"Book {book_id}"),
                full_text=section,
                fresh=True,
                first_seen_turn=current_turn_ordinal,
            )
        )

    for record in attachment_records:
        if str(record.get("type", "")).lower() == "image":
            continue
        mime = str(record.get("mime_type", "")).lower()
        if mime.startswith(_IMAGE_MIME_PREFIX):
            continue
        text = str(record.get("extracted_text", "") or "")
        att_id = str(record.get("id", "") or "").strip()
        if not text.strip() or not att_id:
            continue
        inv.add(
            SourceEntry(
                sid=f"at-{att_id}",
                kind="attachment",
                name=str(record.get("filename") or "Untitled file"),
                full_text=text,
                fresh=True,
                first_seen_turn=current_turn_ordinal,
            )
        )


async def _add_fresh_history(
    inv: SourceInventory,
    *,
    store: SessionStoreProtocol,
    history_session_ids: Sequence[Any],
    current_turn_ordinal: int,
) -> None:
    for raw in history_session_ids:
        hs_id = str(raw or "").strip()
        if not hs_id:
            continue
        text, name = await _load_history_session(store, hs_id)
        if not text:
            continue
        inv.add(
            SourceEntry(
                sid=f"hs-{hs_id}",
                kind="history",
                name=name,
                full_text=text,
                fresh=True,
                first_seen_turn=current_turn_ordinal,
            )
        )


async def _add_fresh_questions(
    inv: SourceInventory,
    *,
    store: SessionStoreProtocol,
    question_entry_ids: Sequence[Any],
    current_turn_ordinal: int,
) -> None:
    get_entry = getattr(store, "get_notebook_entry", None)
    if not callable(get_entry):
        return
    for raw in question_entry_ids:
        try:
            eid = int(raw)
        except (TypeError, ValueError):
            continue
        block, stem = await _load_question_entry(store, eid)
        if not block:
            continue
        inv.add(
            SourceEntry(
                sid=f"qb-{eid}",
                kind="question",
                name=stem,
                full_text=block,
                fresh=True,
                first_seen_turn=current_turn_ordinal,
            )
        )


# ----- Historical source collection ---------------------------------------


async def _add_historical(
    inv: SourceInventory,
    *,
    store: SessionStoreProtocol,
    session_id: str,
    leaf_message_id: int | None,
) -> None:
    """Walk the active branch's ancestor user messages and pull in
    references they carried. Sources already in ``inv`` (i.e. fresh
    duplicates) are skipped — fresh entries always win."""
    lineage = await _load_lineage(store, session_id, leaf_message_id)
    user_turn_ordinal = 0
    for msg in lineage:
        if msg.get("role") != "user":
            continue
        user_turn_ordinal += 1
        await _collect_from_user_message(
            inv, store=store, msg=msg, turn_ordinal=user_turn_ordinal
        )


async def _collect_from_user_message(
    inv: SourceInventory,
    *,
    store: SessionStoreProtocol,
    msg: dict[str, Any],
    turn_ordinal: int,
) -> None:
    """Drain one prior user message into the inventory as historical
    entries. Attachments are pulled from the persisted ``attachments``
    JSON; space refs are pulled from ``metadata.request_snapshot`` and
    re-resolved through their respective services so the historical
    full text always reflects the current state of the referenced object.
    """
    # Attachments — extracted_text was persisted at upload time, no
    # external lookup needed.
    for att in msg.get("attachments") or []:
        att_id = str(att.get("id", "") or "").strip()
        if not att_id:
            continue
        sid = f"at-{att_id}"
        if sid in inv:
            continue
        mime = str(att.get("mime_type", "")).lower()
        if mime.startswith(_IMAGE_MIME_PREFIX):
            continue
        text = str(att.get("extracted_text") or "")
        if not text.strip():
            continue
        inv.add(
            SourceEntry(
                sid=sid,
                kind="attachment",
                name=str(att.get("filename") or "Untitled file"),
                full_text=text,
                fresh=False,
                first_seen_turn=turn_ordinal,
            )
        )

    snap = (msg.get("metadata") or {}).get("request_snapshot") or {}
    if not isinstance(snap, dict):
        return

    # Notebook records — re-resolve through the notebook service.
    notebook_refs = snap.get("notebookReferences") or []
    if notebook_refs:
        from deeptutor.services.notebook import get_notebook_manager

        try:
            records = get_notebook_manager().get_records_by_references(list(notebook_refs))
        except Exception:
            records = []
        for rec in records:
            rid = str(rec.get("id", "") or "").strip()
            if not rid:
                continue
            sid = f"nb-{rid}"
            if sid in inv:
                continue
            full = str(rec.get("output", "") or "")
            if not full.strip():
                continue
            inv.add(
                SourceEntry(
                    sid=sid,
                    kind="notebook",
                    name=str(rec.get("title") or rec.get("name") or "Untitled record"),
                    full_text=full,
                    fresh=False,
                    first_seen_turn=turn_ordinal,
                )
            )

    # Books — one source per book_id (union of page ranges across all
    # turns is implicit because we always pull the *current* book reference
    # to render).
    for ref in snap.get("bookReferences") or []:
        book_id = str((ref or {}).get("book_id") or "").strip()
        if not book_id:
            continue
        sid = f"bk-{book_id}"
        if sid in inv:
            continue
        section_text, name = _resolve_book_section(ref)
        if not section_text.strip():
            continue
        inv.add(
            SourceEntry(
                sid=sid,
                kind="book",
                name=name,
                full_text=section_text,
                fresh=False,
                first_seen_turn=turn_ordinal,
            )
        )

    # History sessions — async, one store fetch per id.
    for raw in snap.get("historyReferences") or []:
        hs_id = str(raw or "").strip()
        if not hs_id:
            continue
        sid = f"hs-{hs_id}"
        if sid in inv:
            continue
        text, name = await _load_history_session(store, hs_id)
        if not text:
            continue
        inv.add(
            SourceEntry(
                sid=sid,
                kind="history",
                name=name,
                full_text=text,
                fresh=False,
                first_seen_turn=turn_ordinal,
            )
        )

    # Question-bank entries.
    for raw in snap.get("questionNotebookReferences") or []:
        try:
            eid = int(raw)
        except (TypeError, ValueError):
            continue
        sid = f"qb-{eid}"
        if sid in inv:
            continue
        block, stem = await _load_question_entry(store, eid)
        if not block:
            continue
        inv.add(
            SourceEntry(
                sid=sid,
                kind="question",
                name=stem,
                full_text=block,
                fresh=False,
                first_seen_turn=turn_ordinal,
            )
        )


# ----- Lineage walker (branch-safe, store-protocol-compatible) ------------


async def _load_lineage(
    store: SessionStoreProtocol,
    session_id: str,
    leaf_message_id: int | None,
) -> list[dict[str, Any]]:
    """Return the active branch's ancestor user/assistant messages in
    chronological order. When ``leaf_message_id`` is ``None`` (legacy
    linear append), returns every message in the session. When it's set
    (branched edit), walks the ``parent_message_id`` chain up from that
    leaf so sibling branches are excluded. Uses ``get_messages`` (which
    every store implements) plus a Python-side parent walk, avoiding a
    sqlite-only ``get_message_path``.
    """
    all_msgs = await store.get_messages(session_id)
    if leaf_message_id is None:
        return all_msgs
    by_id: dict[int, dict[str, Any]] = {}
    for m in all_msgs:
        mid = m.get("id")
        if mid is not None:
            by_id[int(mid)] = m
    chain: list[dict[str, Any]] = []
    current: int | None = int(leaf_message_id)
    safety = 10_000
    while current is not None and safety > 0:
        m = by_id.get(int(current))
        if m is None:
            break
        chain.append(m)
        parent = m.get("parent_message_id")
        current = int(parent) if parent is not None else None
        safety -= 1
    chain.reverse()
    return chain


# ----- Per-type resolvers shared by fresh + historical paths --------------


def _split_book_sections(book_context_text: str) -> list[str]:
    """Split the output of ``build_book_context`` back into per-book
    sections. ``build_book_context`` joins sections with ``"\\n\\n---\\n\\n"``;
    we split on the same separator. Returns an empty list when input is
    empty."""
    if not book_context_text.strip():
        return []
    return [seg for seg in book_context_text.split("\n\n---\n\n") if seg.strip()]


def _extract_book_title(section: str, *, fallback: str) -> str:
    """``_serialize_book_header`` prefixes every section with
    ``# Book: <title>`` — extract that here for the manifest's name field."""
    first_line = section.lstrip().split("\n", 1)[0]
    prefix = "# Book: "
    if first_line.startswith(prefix):
        return first_line[len(prefix):].strip() or fallback
    return fallback


def _resolve_book_section(book_reference: dict[str, Any]) -> tuple[str, str]:
    """Resolve a single book reference into its serialized section + title.

    Used by the historical-collection path where each past turn's book
    reference is rendered independently (so the per-book ``bk-{book_id}``
    source id stays stable). Returns ``("", "")`` on failure.
    """
    from deeptutor.book.context import build_book_context

    try:
        result = build_book_context([book_reference])
    except Exception:
        logger.debug("Failed to resolve historical book reference", exc_info=True)
        return "", ""
    text = (result.text or "").strip()
    if not text:
        return "", ""
    name = _extract_book_title(
        text, fallback=f"Book {book_reference.get('book_id', '?')}"
    )
    return text, name


async def _load_history_session(
    store: SessionStoreProtocol, history_session_id: str
) -> tuple[str, str]:
    """Fetch and serialize a referenced history session into transcript +
    title. Returns ``("", "")`` when the session is empty or missing.
    """
    try:
        meta = await store.get_session(history_session_id)
    except Exception:
        meta = None
    if not meta:
        return "", ""
    try:
        messages_in_hs = await store.get_messages_for_context(history_session_id)
    except Exception:
        messages_in_hs = []
    transcript_lines = [
        f"## {str(m.get('role', '')).title()}\n{m.get('content', '')}"
        for m in messages_in_hs
        if str(m.get("content", "") or "").strip()
    ]
    if not transcript_lines:
        return "", ""
    name = str(meta.get("title", "") or "Untitled session")
    return "\n\n".join(transcript_lines), name


async def _load_question_entry(
    store: SessionStoreProtocol, entry_id: int
) -> tuple[str, str]:
    """Fetch and render one question-bank entry into a markdown block +
    short stem (used as the manifest name). Returns ``("", "")`` on
    missing entry. Imports the renderer lazily to avoid pulling
    ``turn_runtime``'s import surface into modules that consume this one."""
    get_entry = getattr(store, "get_notebook_entry", None)
    if not callable(get_entry):
        return "", ""
    try:
        entry = await get_entry(entry_id)
    except Exception:
        entry = None
    if not entry:
        return "", ""
    # Use the existing turn_runtime helper for consistency with fresh-path
    # formatting. Imported here to keep this module's static deps minimal.
    from deeptutor.services.session.turn_runtime import _format_question_bank_entry

    block = _format_question_bank_entry(entry)
    if not block.strip():
        return "", ""
    stem_source = str(entry.get("question", "") or "Untitled question")
    stem = stem_source[:60].rstrip() or "Untitled question"
    return block, stem


__all__ = [
    "MANIFEST_PREVIEW_CHARS_FRESH",
    "SourceEntry",
    "SourceInventory",
    "build_inventory",
    "render_manifest",
]
