"""Tests for RAG/KB consistency at the capability layer.

After the refactor, RAG is no longer a user-selectable tool — its availability
is derived from whether any knowledge bases are attached for the turn.
These tests pin the contract that:

* ``deep_solve`` *adds* ``rag`` to the effective tool set iff a knowledge
  base is attached, and disables planner-side retrieval otherwise.
* ``deep_research`` still strips ``kb`` from the user-selected sources list
  when no knowledge base is attached (its sources picker is a separate,
  research-specific concept), and surfaces a clear error if every source is
  unusable.
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

    class _FakeSolver:
        def __init__(self, **kwargs: Any) -> None:
            captured_kwargs.update(kwargs)

        async def ainit(self) -> None:
            return None

        def set_trace_callback(self, _cb: Any) -> None:
            return None

        async def solve(self, **_kwargs: Any) -> dict[str, Any]:
            return {"final_answer": "ok", "metadata": {}}

    capability = DeepSolveCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="solve x^2 = 4",
        active_capability="deep_solve",
        # A legacy caller passing "rag" should be ignored — KBs are the signal.
        enabled_tools=["rag", "web_search"],
        knowledge_bases=[],
        language="en",
    )

    with (
        patch(
            "deeptutor.agents.solve.main_solver.MainSolver",
            new=_FakeSolver,
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
    assert captured_kwargs["disable_planner_retrieve"] is True


@pytest.mark.asyncio
async def test_deep_solve_adds_rag_when_knowledge_base_attached() -> None:
    from deeptutor.capabilities.deep_solve import DeepSolveCapability

    captured_kwargs: dict[str, Any] = {}

    class _FakeSolver:
        def __init__(self, **kwargs: Any) -> None:
            captured_kwargs.update(kwargs)

        async def ainit(self) -> None:
            return None

        def set_trace_callback(self, _cb: Any) -> None:
            return None

        async def solve(self, **_kwargs: Any) -> dict[str, Any]:
            return {"final_answer": "ok", "metadata": {}}

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
            "deeptutor.agents.solve.main_solver.MainSolver",
            new=_FakeSolver,
        ),
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
    ):
        await _drain(bus, capability.run(context, bus))

    assert "rag" in captured_kwargs["enabled_tools"]
    assert captured_kwargs["kb_name"] == "my-kb"
    assert captured_kwargs["disable_planner_retrieve"] is False


# ---------------------------------------------------------------------------
# deep_research: kb in sources without KB → kb dropped or hard error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deep_research_drops_kb_source_when_no_knowledge_base() -> None:
    from deeptutor.capabilities.deep_research import DeepResearchCapability

    captured_config: dict[str, Any] = {}

    async def _fake_outline(self, **kwargs: Any):  # noqa: ARG001
        captured_config.update(kwargs.get("config") or {})
        return [{"title": "Subtopic 1", "overview": "Overview 1"}]

    capability = DeepResearchCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="A topic to research",
        active_capability="deep_research",
        enabled_tools=["web_search"],
        knowledge_bases=[],
        config_overrides={
            "mode": "report",
            "depth": "standard",
            "sources": ["kb", "web"],
        },
        language="en",
    )

    with (
        patch.object(
            DeepResearchCapability,
            "_generate_outline_preview",
            new=_fake_outline,
        ),
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
        patch(
            "deeptutor.services.config.load_config_with_main",
            return_value={},
        ),
    ):
        events = await _drain(bus, capability.run(context, bus))

    researching = captured_config.get("researching", {})
    assert researching.get("enable_rag") is False
    assert researching.get("enable_web_search") is True
    assert captured_config["intent"]["sources"] == ["web"]

    warnings = [
        e
        for e in events
        if e.type == StreamEventType.PROGRESS
        and (e.metadata or {}).get("reason") == "kb_without_kb_name"
    ]
    assert warnings, "expected a kb_without_kb_name warning event"


@pytest.mark.asyncio
async def test_deep_research_errors_when_only_kb_source_and_no_knowledge_base() -> None:
    from deeptutor.capabilities.deep_research import DeepResearchCapability

    capability = DeepResearchCapability()
    bus = StreamBus()
    context = UnifiedContext(
        user_message="topic",
        active_capability="deep_research",
        enabled_tools=[],
        knowledge_bases=[],
        config_overrides={
            "mode": "report",
            "depth": "standard",
            "sources": ["kb"],
        },
        language="en",
    )

    with (
        patch(
            "deeptutor.services.llm.config.get_llm_config",
            return_value=_fake_llm_config(),
        ),
        patch(
            "deeptutor.services.config.load_config_with_main",
            return_value={},
        ),
    ):
        events = await _drain(bus, capability.run(context, bus))

    errors = [e for e in events if e.type == StreamEventType.ERROR]
    assert errors, "expected an error event when no usable source remains"
    assert "source" in errors[0].content.lower()
