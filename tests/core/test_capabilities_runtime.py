"""Runtime tests for built-in capabilities under the unified framework."""

from __future__ import annotations

import asyncio
import sys
import types
from types import SimpleNamespace
from typing import Any

import pytest

import deeptutor.agents.visualize.pipeline as visualize_pipeline
from deeptutor.capabilities.chat import ChatCapability
from deeptutor.capabilities.deep_question import DeepQuestionCapability
from deeptutor.capabilities.deep_research import DeepResearchCapability
from deeptutor.capabilities.deep_solve import DeepSolveCapability
from deeptutor.capabilities.visualize import VisualizeCapability
from deeptutor.core.context import Attachment, UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus


def _install_module(
    monkeypatch: pytest.MonkeyPatch, fullname: str, **attrs: Any
) -> types.ModuleType:
    parts = fullname.split(".")
    for idx in range(1, len(parts)):
        pkg_name = ".".join(parts[:idx])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = []  # type: ignore[attr-defined]
            monkeypatch.setitem(sys.modules, pkg_name, pkg)
            if idx > 1:
                parent = sys.modules[".".join(parts[: idx - 1])]
                setattr(parent, parts[idx - 1], pkg)

    module = types.ModuleType(fullname)
    for key, value in attrs.items():
        setattr(module, key, value)
    monkeypatch.setitem(sys.modules, fullname, module)
    if len(parts) > 1:
        parent = sys.modules[".".join(parts[:-1])]
        setattr(parent, parts[-1], module)
    return module


async def _collect_events(run_coro) -> list[StreamEvent]:
    bus = StreamBus()
    events: list[StreamEvent] = []

    async def _consume() -> None:
        async for event in bus.subscribe():
            events.append(event)

    consumer = asyncio.create_task(_consume())
    await asyncio.sleep(0)
    await run_coro(bus)
    await asyncio.sleep(0)
    await bus.close()
    await consumer
    return events


@pytest.mark.asyncio
async def test_chat_capability_streams_content_and_geogebra_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakePipeline:
        def __init__(self, language: str = "en") -> None:
            captured["pipeline_init"] = {"language": language}

        async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
            captured["process"] = {
                "message": f"{context.user_message}\nGGB commands",
                "enabled_tools": list(context.enabled_tools or []),
            }
            await stream.tool_call(
                "geogebra_analysis",
                {"image_name": "img.png"},
                source="chat",
                stage="acting",
            )
            await stream.sources(
                [
                    {"type": "rag", "kb_name": "demo-kb", "content": "grounding"},
                    {"type": "web", "url": "https://example.com", "title": "Example"},
                ],
                source="chat",
                stage="responding",
            )
            await stream.content("assistant output", source="chat", stage="responding")

    monkeypatch.setattr("deeptutor.capabilities.chat.AgenticChatPipeline", FakePipeline)

    context = UnifiedContext(
        user_message="analyze triangle",
        enabled_tools=["rag", "web_search", "geogebra_analysis"],
        knowledge_bases=["demo-kb"],
        language="en",
        attachments=[Attachment(type="image", base64="ZmFrZQ==", filename="img.png")],
    )

    capability = ChatCapability()
    events = await _collect_events(lambda bus: capability.run(context, bus))

    assert any(event.type == StreamEventType.TOOL_CALL for event in events)
    assert any(event.type == StreamEventType.SOURCES for event in events)
    assert any(
        event.type == StreamEventType.CONTENT and "assistant output" in event.content
        for event in events
    )
    assert "GGB commands" in captured["process"]["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("enabled_tools", "knowledge_bases", "expected_kb"),
    [
        # Non-rag tools + attached KB → kb_name forwarded; pipeline mounts rag.
        (["code_execution"], ["algebra"], "algebra"),
        # Default tool set (manifest) flows through; rag absent from the
        # forwarded toggle list because the pipeline owns mounting.
        (None, ["algebra"], "algebra"),
        # Legacy callers that still pass "rag" without attaching a KB get
        # rag stripped at the capability boundary, and kb_name stays None.
        (["rag", "web_search"], [], None),
    ],
)
async def test_deep_solve_capability_forwards_to_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    enabled_tools: list[str] | None,
    knowledge_bases: list[str],
    expected_kb: str | None,
) -> None:
    """The deep_solve capability is a thin shim over ``SolvePipeline``:
    it strips ``rag`` from the enabled-tools list (the pipeline mounts rag
    itself based on ``kb_name``) and forwards everything else."""
    captured: dict[str, Any] = {}

    class FakePipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured["pipeline_init"] = kwargs

        async def run(self, *, stream: StreamBus, **kwargs: Any) -> dict[str, Any]:
            captured["pipeline_run"] = kwargs
            await stream.content("final solution", source="deep_solve", stage="writing")
            payload = {
                "response": "final solution",
                "metadata": {"steps": 2},
            }
            await stream.result(payload, source="deep_solve")
            return payload

    monkeypatch.setattr("deeptutor.capabilities.deep_solve.SolvePipeline", FakePipeline)

    context = UnifiedContext(
        user_message="solve x^2=4",
        enabled_tools=enabled_tools,
        knowledge_bases=knowledge_bases,
        language="en",
        attachments=[Attachment(type="image", base64="ZmFrZQ==", filename="graph.png")],
    )
    capability = DeepSolveCapability()
    events = await _collect_events(lambda bus: capability.run(context, bus))

    init = captured["pipeline_init"]
    assert init["kb_name"] == expected_kb
    assert "rag" not in init["enabled_tools"]
    # Attachments flow through unmodified.
    assert captured["pipeline_run"]["attachments"][0].filename == "graph.png"
    assert any(
        event.type == StreamEventType.CONTENT and "final solution" in event.content
        for event in events
    )
    result_event = next(event for event in events if event.type == StreamEventType.RESULT)
    assert result_event.metadata["response"] == "final solution"


# Legacy tests for the AgentCoordinator-based custom + mimic paths were
# removed when those code paths were deleted in the Phase A → C quiz
# refactor. New-pipeline coverage lives in
# ``tests/agents/question/test_pipeline.py`` (plan parsing, payload
# normalization, templates_override / mimic flow, structured emission,
# tool wiring, history loader, etc.).


@pytest.mark.asyncio
async def test_deep_question_capability_uses_single_call_followup_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeCoordinator:
        def __init__(self, **_kwargs: Any) -> None:
            raise AssertionError("Coordinator should not be constructed for follow-up mode")

    class FakeFollowupAgent:
        def __init__(self, **kwargs: Any) -> None:
            captured["init"] = kwargs
            self._trace_callback = None

        def set_trace_callback(self, callback) -> None:
            self._trace_callback = callback

        async def process(self, **kwargs: Any) -> str:
            captured["process"] = kwargs
            assert self._trace_callback is not None
            await self._trace_callback(
                {
                    "event": "llm_call",
                    "state": "running",
                    "label": "Answer follow-up for Question 3",
                    "phase": "generation",
                    "call_id": "quiz-followup-q_3",
                }
            )
            await self._trace_callback(
                {
                    "event": "llm_call",
                    "state": "complete",
                    "response": "You missed the key distinction between density and coverage.",
                    "phase": "generation",
                    "call_id": "quiz-followup-q_3",
                }
            )
            return "You missed the key distinction between density and coverage."

    _install_module(
        monkeypatch,
        "deeptutor.agents.question.coordinator",
        AgentCoordinator=FakeCoordinator,
    )
    _install_module(
        monkeypatch,
        "deeptutor.agents.question.agents.followup_agent",
        FollowupAgent=FakeFollowupAgent,
    )
    _install_module(
        monkeypatch,
        "deeptutor.services.llm.config",
        get_llm_config=lambda: SimpleNamespace(api_key="k", base_url="u", api_version="v1"),
    )

    context = UnifiedContext(
        user_message="Why was my answer wrong?",
        language="en",
        metadata={
            "conversation_context_text": "User previously asked for a simpler explanation.",
            "question_followup_context": {
                "question_id": "q_3",
                "question": "What does density mean in win-rate comparison?",
                "question_type": "written",
                "user_answer": "coverage",
                "correct_answer": "relevant information without redundancy",
                "is_correct": False,
                "explanation": "Density is about relevant content without redundancy.",
            },
        },
    )
    capability = DeepQuestionCapability()
    events = await _collect_events(lambda bus: capability.run(context, bus))

    assert captured["process"]["user_message"] == "Why was my answer wrong?"
    assert (
        captured["process"]["history_context"] == "User previously asked for a simpler explanation."
    )
    assert captured["process"]["question_context"]["question_id"] == "q_3"
    assert any(
        event.type == StreamEventType.CONTENT
        and "key distinction between density and coverage" in event.content
        for event in events
    )
    result_event = next(event for event in events if event.type == StreamEventType.RESULT)
    assert result_event.metadata["mode"] == "followup"
    assert result_event.metadata["question_id"] == "q_3"


@pytest.mark.asyncio
async def test_deep_research_capability_delegates_to_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The capability shim validates the request config, normalises
    KB-without-KB, builds a runtime config, and hands the heavy lifting
    to :class:`ResearchPipeline`. We mock the pipeline at its import site
    in the capability module so we can assert what it was called with
    without spinning up real LLM I/O.
    """
    import deeptutor.agents.research.request_config  # noqa: F401
    import deeptutor.capabilities.deep_research as deep_research_mod

    captured: dict[str, Any] = {}

    class FakeResearchPipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured["pipeline_init"] = kwargs

        async def run(self, **kwargs: Any) -> dict[str, Any]:
            captured["pipeline_run"] = kwargs
            return {
                "response": f"Report about {kwargs['topic']}",
                "metadata": {"mode": "agentic_research", "block_count": 2},
            }

    def fake_load_config_with_main(_: str) -> dict[str, Any]:
        return {
            "capabilities": {
                "research": {
                    "researching": {
                        "note_agent_mode": "auto",
                        "tool_timeout": 60,
                        "tool_max_retries": 2,
                        "paper_search_years_limit": 3,
                    },
                }
            },
        }

    monkeypatch.setattr(deep_research_mod, "ResearchPipeline", FakeResearchPipeline)
    monkeypatch.setattr(deep_research_mod, "load_config_with_main", fake_load_config_with_main)

    context = UnifiedContext(
        user_message="agent-native tutoring",
        enabled_tools=["rag", "web_search", "paper_search"],
        knowledge_bases=["research-kb"],
        attachments=[Attachment(type="image", base64="ZmFrZQ==", filename="brief.png")],
        config_overrides={
            "mode": "report",
            "depth": "standard",
            # Provide a confirmed outline so the capability skips the
            # outline-preview short-circuit and drives the full
            # research + reporting flow on the pipeline.
            "confirmed_outline": [
                {"title": "Background", "overview": "Why this topic matters"},
                {"title": "Approaches", "overview": "How to do it"},
            ],
        },
        language="en",
    )
    capability = DeepResearchCapability()
    await _collect_events(lambda bus: capability.run(context, bus))

    init_kwargs = captured["pipeline_init"]
    runtime_cfg = init_kwargs["runtime_config"]
    assert init_kwargs["kb_name"] == "research-kb"
    assert init_kwargs["language"] == "en"
    # ``enabled_tools`` is the user's composer toggles forwarded
    # unchanged. The pipeline's per-block ``compose_enabled_tools`` call
    # is what decides what the block loop actually exposes.
    assert init_kwargs["enabled_tools"] == ["rag", "web_search", "paper_search"]
    # Runtime config carries the structured policy sub-dicts the
    # pipeline reads at init time. We only assert the keys the runtime
    # config builder is contractually responsible for producing.
    assert "planning" in runtime_cfg
    assert "researching" in runtime_cfg
    assert "reporting" in runtime_cfg
    # Source-derived enable_* flags were removed; the block loop now
    # composes tools the same way chat does (user toggles + auto-mounts).
    assert "enable_rag" not in runtime_cfg["researching"]
    assert "enable_web_search" not in runtime_cfg["researching"]
    assert "enable_paper_search" not in runtime_cfg["researching"]
    assert "enable_run_code" not in runtime_cfg["researching"]

    run_kwargs = captured["pipeline_run"]
    assert run_kwargs["topic"] == "agent-native tutoring"
    assert run_kwargs["confirmed_outline"] is not None
    assert [item.title for item in run_kwargs["confirmed_outline"]] == [
        "Background",
        "Approaches",
    ]
    # Attachments are forwarded verbatim so the rephrase / decompose
    # prompts can see image evidence.
    assert run_kwargs["attachments"][0].filename == "brief.png"


@pytest.mark.asyncio
async def test_visualize_capability_passes_attachments_to_analysis_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeAnalysis:
        render_type = "svg"
        description = "A diagram"
        data_description = "diagram data"

        def model_dump(self) -> dict[str, Any]:
            return {
                "render_type": self.render_type,
                "description": self.description,
                "data_description": self.data_description,
            }

    class FakeReview:
        optimized_code = "<svg></svg>"
        changed = False
        review_notes = "ok"

        def model_dump(self) -> dict[str, Any]:
            return {
                "optimized_code": self.optimized_code,
                "changed": self.changed,
                "review_notes": self.review_notes,
            }

    class FakeVisualizePipeline:
        def __init__(self, **kwargs: Any) -> None:
            captured["init"] = kwargs

        async def run_analysis(self, **kwargs: Any) -> FakeAnalysis:
            captured["analysis"] = kwargs
            return FakeAnalysis()

        async def run_code_generation(self, **kwargs: Any) -> str:
            captured["code_generation"] = kwargs
            return "<svg></svg>"

        async def run_review(self, **kwargs: Any) -> FakeReview:
            captured["review"] = kwargs
            return FakeReview()

    monkeypatch.setattr(
        visualize_pipeline,
        "VisualizePipeline",
        FakeVisualizePipeline,
    )
    _install_module(
        monkeypatch,
        "deeptutor.services.llm.config",
        get_llm_config=lambda: SimpleNamespace(api_key="k", base_url="u", api_version="v1"),
    )

    context = UnifiedContext(
        user_message="make a figure",
        active_capability="visualize",
        config_overrides={"render_mode": "svg"},
        language="en",
        attachments=[Attachment(type="image", base64="ZmFrZQ==", filename="figure.png")],
    )

    capability = VisualizeCapability()
    events = await _collect_events(lambda bus: capability.run(context, bus))

    assert captured["analysis"]["attachments"][0].filename == "figure.png"
    result_event = next(event for event in events if event.type == StreamEventType.RESULT)
    assert result_event.metadata["render_type"] == "svg"
