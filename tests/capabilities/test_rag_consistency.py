"""Tests for RAG/KB consistency at the capability layer.

After the refactor, RAG is no longer a user-selectable tool — its availability
is derived from whether any knowledge bases are attached for the turn.
These tests pin the contract that:

* ``deep_solve`` forwards the right ``kb_name`` to the pipeline (``None`` when
  no KB is attached, the KB name when one is), and strips a legacy ``rag``
  toggle from the enabled-tools list because the pipeline owns rag mounting.
* ``deep_research`` uses the same tool-composition policy as chat
  (``compose_enabled_tools``): the user's composer toggles flow through
  to the pipeline unchanged, ``rag`` auto-mounts iff a KB is attached.
  The legacy per-source gating (``sources: ["kb", "web", "papers"]``)
  has been removed.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus


async def _drain(bus: StreamBus, task) -> list[StreamEvent]:
    await task
    await bus.close()
    return [event async for event in bus.subscribe()]


def _fake_llm_config() -> MagicMock:
    cfg = MagicMock()
    cfg.api_key = "sk-test"
    cfg.base_url = None
    cfg.api_version = None
    return cfg


# ---------------------------------------------------------------------------
# deep_solve: rag presence is keyed on attached KB
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deep_solve_omits_rag_when_no_knowledge_base() -> None:
    from deeptutor.capabilities.deep_solve import DeepSolveCapability

    captured_kwargs: dict[str, Any] = {}

    class _FakePipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured_kwargs.update(kwargs)

        async def run(self, *, stream: StreamBus, **_kwargs: Any) -> dict[str, Any]:
            payload = {"response": "ok", "metadata": {}}
            await stream.result(payload, source="deep_solve")
            return payload

    capability = DeepSolveCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="solve x^2 = 4",
        active_capability="deep_solve",
        # A legacy caller passing "rag" should be dropped — the pipeline owns
        # rag mounting based on whether a KB is attached.
        enabled_tools=["rag", "web_search"],
        knowledge_bases=[],
        language="en",
    )

    with (
        patch(
            "deeptutor.capabilities.deep_solve.SolvePipeline",
            new=_FakePipeline,
        ),
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
    ):
        await _drain(bus, capability.run(context, bus))

    assert "rag" not in captured_kwargs["enabled_tools"]
    assert "web_search" in captured_kwargs["enabled_tools"]
    assert captured_kwargs["kb_name"] is None


@pytest.mark.asyncio
async def test_deep_solve_forwards_kb_when_knowledge_base_attached() -> None:
    from deeptutor.capabilities.deep_solve import DeepSolveCapability

    captured_kwargs: dict[str, Any] = {}

    class _FakePipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured_kwargs.update(kwargs)

        async def run(self, *, stream: StreamBus, **_kwargs: Any) -> dict[str, Any]:
            payload = {"response": "ok", "metadata": {}}
            await stream.result(payload, source="deep_solve")
            return payload

    capability = DeepSolveCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="solve x^2 = 4",
        active_capability="deep_solve",
        enabled_tools=["web_search"],
        knowledge_bases=["my-kb"],
        language="en",
    )

    with (
        patch(
            "deeptutor.capabilities.deep_solve.SolvePipeline",
            new=_FakePipeline,
        ),
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
    ):
        await _drain(bus, capability.run(context, bus))

    # The capability strips ``rag`` from the LLM-visible toggle list; the
    # pipeline auto-mounts it internally based on ``kb_name``.
    assert "rag" not in captured_kwargs["enabled_tools"]
    assert "web_search" in captured_kwargs["enabled_tools"]
    assert captured_kwargs["kb_name"] == "my-kb"


# ---------------------------------------------------------------------------
# deep_research: tool composition matches chat (no sources gating)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deep_research_forwards_enabled_tools_and_kb_unchanged() -> None:
    """The capability passes the user's composer toggles (``enabled_tools``)
    and the attached KB (``kb_name``) through to the pipeline as-is. There
    is no per-source gating: ``compose_enabled_tools`` (run inside the
    pipeline) is the single arbiter of what the block loop sees."""
    from deeptutor.capabilities.deep_research import DeepResearchCapability

    captured_kwargs: dict[str, Any] = {}

    class _FakePipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured_kwargs.update(kwargs)

        async def run(self, *, stream: StreamBus, **_kwargs: Any) -> dict[str, Any]:
            return {
                "response": "",
                "output_dir": "",
                "outline_preview": True,
                "topic": "topic",
                "sub_topics": [{"title": "Subtopic 1", "overview": "Overview 1"}],
            }

    capability = DeepResearchCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="A topic to research",
        active_capability="deep_research",
        enabled_tools=["web_search", "paper_search"],
        knowledge_bases=["my-kb"],
        config_overrides={
            "mode": "report",
            "depth": "standard",
        },
        language="en",
    )

    with (
        patch(
            "deeptutor.capabilities.deep_research.ResearchPipeline",
            new=_FakePipeline,
        ),
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
        patch(
            "deeptutor.capabilities.deep_research.load_config_with_main",
            return_value={},
        ),
    ):
        await _drain(bus, capability.run(context, bus))

    assert captured_kwargs["enabled_tools"] == ["web_search", "paper_search"]
    assert captured_kwargs["kb_name"] == "my-kb"
    runtime_config = captured_kwargs.get("runtime_config") or {}
    researching = runtime_config.get("researching", {})
    # The legacy per-source enable_* flags must not appear in the
    # runtime config — composition is the pipeline's job.
    assert "enable_rag" not in researching
    assert "enable_web_search" not in researching
    assert "enable_paper_search" not in researching
    assert "enable_run_code" not in researching
    assert "sources" not in runtime_config.get("intent", {})
