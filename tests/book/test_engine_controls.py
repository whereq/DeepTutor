from __future__ import annotations

from deeptutor.book.engine import BookEngine
from deeptutor.book.models import Block, BlockStatus, BlockType, Page, PageStatus


def test_force_compile_reset_preserves_user_notes() -> None:
    generated = Block(
        type=BlockType.CODE,
        status=BlockStatus.READY,
        payload={"code": "print(1)"},
        source_anchors=[],
        metadata={"generation_ms": 10, "transition_in": "bridge"},
    )
    note = Block(
        type=BlockType.USER_NOTE,
        status=BlockStatus.READY,
        payload={"body": "keep me"},
    )
    page = Page(status=PageStatus.READY, error="", blocks=[generated, note])

    BookEngine._reset_page_for_force_compile(page)

    assert page.status == PageStatus.PENDING
    assert generated.status == BlockStatus.PENDING
    assert generated.payload == {}
    assert generated.error == ""
    assert generated.metadata == {"transition_in": "bridge"}
    assert note.status == BlockStatus.READY
    assert note.payload == {"body": "keep me"}
