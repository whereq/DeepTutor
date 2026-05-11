"""Unit tests for ``deeptutor/agents/auto/delegation.py``.

Covers:
* ``build_child_context`` correctly derives a child UnifiedContext via
  ``dataclasses.replace`` without mutating the parent (assumption A1).
* ``forward_events`` injects required metadata fields and protects
  conversation_history from sub-capability CONTENT pollution by ensuring
  every forwarded CONTENT carries a ``call_id`` (assumption A3 integration).
* ``delegate_to_capability`` happy path + raise/error-event paths.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from deeptutor.agents.auto.delegation import (
    build_child_context,
    delegate_to_capability,
)
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import Attachment, UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus

# --------------------------------------------------------------------------- #
# Test fixtures                                                                #
# --------------------------------------------------------------------------- #


class _FakeCapability(BaseCapability):
    """Configurable fake capability for delegation tests."""

    def __init__(
        self,
        name: str = "fake",
        events: list[StreamEvent] | None = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self.manifest = CapabilityManifest(
            name=name,
            description="fake test capability",
            stages=["only"],
        )
        self._scripted_events = events or []
        self._raise = raise_exc
        self.received_context: UnifiedContext | None = None

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        self.received_context = context
        for event in self._scripted_events:
            await stream.emit(event)
        if self._raise is not None:
            raise self._raise


def _ctx(**overrides: Any) -> UnifiedContext:
    return UnifiedContext(
        session_id="sess-1",
        user_message="hello",
        knowledge_bases=["kb-a"],
        enabled_tools=["rag"],
        attachments=[Attachment(type="pdf", filename="paper.pdf")],
        metadata={"shared": "x"},
        **overrides,
    )


# --------------------------------------------------------------------------- #
# build_child_context                                                          #
# --------------------------------------------------------------------------- #


def test_build_child_context_overrides_capability_and_config():
    parent = _ctx()
    child = build_child_context(
        parent,
        cap_name="deep_solve",
        config={"detailed_answer": False},
        delegation_call_id="del-1",
    )
    assert child.active_capability == "deep_solve"
    assert child.config_overrides == {"detailed_answer": False}
    assert child.metadata["is_sub_invocation"] is True
    assert child.metadata["parent_delegation_call_id"] == "del-1"
    # Shared metadata key is preserved.
    assert child.metadata["shared"] == "x"


def test_build_child_context_does_not_mutate_parent():
    parent = _ctx()
    parent_metadata_before = dict(parent.metadata)
    parent_kbs_before = list(parent.knowledge_bases)

    build_child_context(
        parent,
        cap_name="deep_solve",
        config={},
        delegation_call_id="del-2",
        knowledge_bases=["kb-other"],
        enabled_tools=["web_search"],
    )

    # Parent fields unchanged.
    assert parent.metadata == parent_metadata_before
    assert parent.knowledge_bases == parent_kbs_before
    assert parent.active_capability is None


def test_build_child_context_inherits_when_args_missing():
    parent = _ctx()
    child = build_child_context(
        parent,
        cap_name="deep_solve",
        config={},
        delegation_call_id="del-3",
        enabled_tools=None,
        knowledge_bases=None,
    )
    assert child.enabled_tools == ["rag"]
    assert child.knowledge_bases == ["kb-a"]
    assert child.attachments == parent.attachments  # passed through


def test_build_child_context_accepts_explicit_overrides():
    parent = _ctx()
    child = build_child_context(
        parent,
        cap_name="visualize",
        config={"render_mode": "svg"},
        delegation_call_id="del-4",
        enabled_tools=["code_execution"],
        knowledge_bases=["kb-other"],
    )
    assert child.enabled_tools == ["code_execution"]
    assert child.knowledge_bases == ["kb-other"]


# --------------------------------------------------------------------------- #
# delegate_to_capability — full forwarder + runner flow                        #
# --------------------------------------------------------------------------- #


def _evt(
    event_type: StreamEventType,
    *,
    content: str = "",
    metadata: dict[str, Any] | None = None,
) -> StreamEvent:
    return StreamEvent(
        type=event_type,
        source="fake",
        stage="only",
        content=content,
        metadata=metadata or {},
    )


def _collect_events(parent_bus: StreamBus) -> list[StreamEvent]:
    return list(parent_bus._history)


@pytest.mark.asyncio
async def test_delegate_happy_path_forwards_events_with_metadata():
    parent_bus = StreamBus()
    fake = _FakeCapability(
        name="visualize",
        events=[
            _evt(StreamEventType.THINKING, content="thinking..."),
            _evt(StreamEventType.CONTENT, content="result body"),
            _evt(StreamEventType.RESULT, metadata={"response": "ok"}),
        ],
    )
    with patch(
        "deeptutor.agents.auto.delegation.get_capability_registry"
    ) as mock_get_reg:
        mock_get_reg.return_value.get.return_value = fake

        result = await delegate_to_capability(
            cap_name="visualize",
            config={"render_mode": "svg"},
            parent_context=_ctx(),
            parent_stream=parent_bus,
        )

    assert result.succeeded is True
    assert result.capability == "visualize"
    assert result.delegation_call_id.startswith("auto-delegation-")
    assert result.result_metadata == {"response": "ok"}

    events = _collect_events(parent_bus)
    # All forwarded events should have the auto metadata stamped.
    assert len(events) == 3
    for ev in events:
        assert ev.metadata["delegated_capability"] == "visualize"
        assert ev.metadata["delegated_from"] == "auto"
        assert ev.metadata["parent_call_id"] == result.delegation_call_id
        assert ev.metadata["delegation_attempt"] == 1


@pytest.mark.asyncio
async def test_delegate_injects_call_id_into_content_without_one():
    """Critical: prevents sub-capability CONTENT from polluting history."""
    parent_bus = StreamBus()
    fake = _FakeCapability(
        name="deep_solve",
        events=[
            # CONTENT without any call_id — this is the dangerous case.
            _evt(StreamEventType.CONTENT, content="body 1"),
            # CONTENT with an existing call_id — should be preserved as-is.
            _evt(
                StreamEventType.CONTENT,
                content="body 2",
                metadata={"call_id": "existing-call", "call_kind": "intermediate"},
            ),
        ],
    )
    with patch(
        "deeptutor.agents.auto.delegation.get_capability_registry"
    ) as mock_get_reg:
        mock_get_reg.return_value.get.return_value = fake
        result = await delegate_to_capability(
            cap_name="deep_solve",
            config={},
            parent_context=_ctx(),
            parent_stream=parent_bus,
        )

    forwarded = _collect_events(parent_bus)
    assert len(forwarded) == 2

    # First event got an injected call_id.
    assert forwarded[0].metadata.get("call_id") == result.delegation_call_id

    # Second event preserved its original call_id.
    assert forwarded[1].metadata.get("call_id") == "existing-call"


@pytest.mark.asyncio
async def test_delegate_captures_raise_as_failure():
    parent_bus = StreamBus()
    fake = _FakeCapability(name="boom", raise_exc=RuntimeError("kaboom"))
    with patch(
        "deeptutor.agents.auto.delegation.get_capability_registry"
    ) as mock_get_reg:
        mock_get_reg.return_value.get.return_value = fake
        result = await delegate_to_capability(
            cap_name="boom",
            config={},
            parent_context=_ctx(),
            parent_stream=parent_bus,
        )

    assert result.succeeded is False
    assert result.error_message and "kaboom" in result.error_message


@pytest.mark.asyncio
async def test_delegate_marks_failure_on_error_event():
    """A capability that emits ERROR (instead of raising) should count as failure."""
    parent_bus = StreamBus()
    fake = _FakeCapability(
        name="errorful",
        events=[_evt(StreamEventType.ERROR, content="problem")],
    )
    with patch(
        "deeptutor.agents.auto.delegation.get_capability_registry"
    ) as mock_get_reg:
        mock_get_reg.return_value.get.return_value = fake
        result = await delegate_to_capability(
            cap_name="errorful",
            config={},
            parent_context=_ctx(),
            parent_stream=parent_bus,
        )

    assert result.succeeded is False
    assert result.error_message == "sub_capability_emitted_error"


@pytest.mark.asyncio
async def test_delegate_unknown_capability_returns_failure():
    parent_bus = StreamBus()
    with patch(
        "deeptutor.agents.auto.delegation.get_capability_registry"
    ) as mock_get_reg:
        mock_get_reg.return_value.get.return_value = None
        result = await delegate_to_capability(
            cap_name="nonexistent",
            config={},
            parent_context=_ctx(),
            parent_stream=parent_bus,
        )

    assert result.succeeded is False
    assert result.error_message and "unknown_capability" in result.error_message
