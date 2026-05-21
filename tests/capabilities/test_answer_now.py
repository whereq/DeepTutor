"""
Tests for the per-capability ``answer_now`` fast-paths.

Each capability now owns its own answer-now branch (instead of every
turn being re-routed to ``chat``). These tests pin the contract:

* Detection — the shared ``extract_answer_now_context`` correctly gates
  the branch on a non-empty ``original_user_message``.
* Trace formatting — long event lists are summarised, truncation
  applied, empty inputs fall back to a sentinel string.
* Skip notice — i18n-aware, omits when no stages were skipped.
* Per-capability flow — for each registered capability we mock the
  underlying LLM stream and assert the result envelope shape that the
  frontend depends on (``response`` always, plus capability-specific
  keys like ``summary.results`` for ``deep_question`` or ``code`` for
  ``visualize``).

The tests deliberately avoid touching the real LLM stack: we patch
``deeptutor.capabilities._answer_now.llm_stream`` (the alias the helper
imports) and ``deeptutor.capabilities._answer_now.get_llm_config`` so
the fast-paths run end-to-end without network or API keys.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deeptutor.capabilities import _answer_now
from deeptutor.capabilities._answer_now import (
    extract_answer_now_context,
    format_trace_summary,
    join_chunks,
    labeled_block,
    make_skip_notice,
)
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


async def _drain(bus: StreamBus, task) -> list[StreamEvent]:
    """Run ``task`` to completion, then return everything emitted on ``bus``."""
    await task
    await bus.close()
    return [event async for event in bus.subscribe()]


def _fake_llm_config(model: str = "gpt-4o-mini") -> MagicMock:
    cfg = MagicMock()
    cfg.binding = "openai"
    cfg.model = model
    cfg.api_key = "sk-test"
    cfg.base_url = None
    cfg.api_version = None
    return cfg


def _make_stream_factory(chunks: list[str]):
    """Return an async generator factory that yields the given chunks once."""

    async def _stream(*_args: Any, **_kwargs: Any) -> AsyncIterator[str]:
        for chunk in chunks:
            yield chunk

    return _stream


def _build_context(
    *,
    capability: str,
    payload: dict[str, Any] | None,
    user_message: str = "What is a Fourier transform?",
    config_overrides: dict[str, Any] | None = None,
    language: str = "en",
) -> UnifiedContext:
    overrides: dict[str, Any] = dict(config_overrides or {})
    if payload is not None:
        overrides["answer_now_context"] = payload
    return UnifiedContext(
        session_id="sess-test",
        user_message=user_message,
        active_capability=capability,
        config_overrides=overrides,
        language=language,
        metadata={"turn_id": "turn-test"},
    )


def _result_event(events: list[StreamEvent]) -> StreamEvent:
    """Return the single ``RESULT`` event; raise if absent."""
    matches = [e for e in events if e.type == StreamEventType.RESULT]
    assert len(matches) == 1, f"expected 1 RESULT event, got {len(matches)}"
    return matches[0]


def _content_text(events: list[StreamEvent]) -> str:
    return "".join(e.content for e in events if e.type == StreamEventType.CONTENT)


# ---------------------------------------------------------------------------
# 1. Shared helpers — pure functions
# ---------------------------------------------------------------------------


class TestExtractAnswerNowContext:
    def test_returns_payload_when_present(self) -> None:
        ctx = _build_context(
            capability="chat",
            payload={"original_user_message": "hi", "events": []},
        )
        assert extract_answer_now_context(ctx) == {
            "original_user_message": "hi",
            "events": [],
        }

    def test_returns_none_when_missing(self) -> None:
        ctx = _build_context(capability="chat", payload=None)
        assert extract_answer_now_context(ctx) is None

    def test_returns_none_when_not_dict(self) -> None:
        ctx = UnifiedContext(
            user_message="x",
            config_overrides={"answer_now_context": "not-a-dict"},
        )
        assert extract_answer_now_context(ctx) is None

    def test_returns_none_when_original_user_message_empty(self) -> None:
        ctx = _build_context(
            capability="chat",
            payload={"original_user_message": "   "},
        )
        assert extract_answer_now_context(ctx) is None


class TestFormatTraceSummary:
    def test_empty_events_returns_fallback_en(self) -> None:
        assert "No intermediate" in format_trace_summary([], language="en")

    def test_empty_events_returns_fallback_zh(self) -> None:
        assert "没有可用" in format_trace_summary([], language="zh")

    def test_non_list_returns_fallback(self) -> None:
        assert "No intermediate" in format_trace_summary("nope", language="en")

    def test_renders_event_with_stage_and_tool(self) -> None:
        events = [
            {
                "type": "tool_call",
                "stage": "acting",
                "content": "rag.query",
                "metadata": {"tool_name": "rag"},
            }
        ]
        out = format_trace_summary(events, language="en")
        assert "1. tool_call / acting" in out
        assert "rag.query" in out
        assert "[tool=rag]" in out

    def test_truncates_long_event_content(self) -> None:
        events = [
            {
                "type": "thinking",
                "stage": "planning",
                "content": "x" * 5000,
            }
        ]
        out = format_trace_summary(events, language="en")
        assert out.endswith("...")
        # The per-event cap is 800 chars; the rendered line stays bounded.
        assert len(out) < 1000

    def test_truncates_overall_transcript(self) -> None:
        events = [{"type": "thinking", "stage": "s", "content": "a" * 700} for _ in range(20)]
        out = format_trace_summary(events, language="en")
        assert len(out) <= 6000
        assert out.endswith("...")

    def test_skips_non_dict_entries(self) -> None:
        events = ["bad", 42, {"type": "thinking", "content": "good"}]
        out = format_trace_summary(events, language="en")
        assert "good" in out
        assert "bad" not in out


class TestMakeSkipNotice:
    def test_empty_when_no_stages(self) -> None:
        assert make_skip_notice(capability="chat", language="en", stages_skipped=[]) == ""

    def test_english_lists_stages(self) -> None:
        notice = make_skip_notice(
            capability="deep_solve",
            language="en",
            stages_skipped=["planning", "reasoning"],
        )
        assert "planning, reasoning" in notice
        assert "`deep_solve`" in notice

    def test_chinese_uses_full_width_separator(self) -> None:
        notice = make_skip_notice(
            capability="deep_solve",
            language="zh",
            stages_skipped=["planning", "reasoning"],
        )
        assert "planning、reasoning" in notice
        assert "已跳过" in notice


class TestLabeledBlock:
    def test_renders_label_and_content(self) -> None:
        assert labeled_block("X", "hello") == "[X]\nhello"

    def test_uses_sentinel_for_empty_content(self) -> None:
        assert labeled_block("X", "   ") == "[X]\n(empty)"


class TestJoinChunks:
    def test_joins_and_strips_thinking_tags(self) -> None:
        with patch.object(_answer_now, "get_llm_config", return_value=_fake_llm_config()):
            text = join_chunks(["<think>private</think>", "Answer."])
            # ``clean_thinking_tags`` for the openai binding is a no-op, but
            # we still want to make sure the function does not blow up.
            assert "Answer." in text


# ---------------------------------------------------------------------------
# 2. Per-capability fast paths
# ---------------------------------------------------------------------------


class TestChatAnswerNow:
    """``chat`` keeps its existing synthesizer; we only assert the high-
    level behavior so a future refactor of ``_stage_answer_now`` doesn't
    silently change the contract."""

    @pytest.mark.asyncio
    async def test_chat_synthesises_final_answer_from_partial_trace(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("Hello", " ", "world"):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain Fourier",
                    "partial_response": "We had begun to think about ...",
                    "events": [{"type": "thinking", "stage": "thinking", "content": "warming up"}],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert "Hello" in text
            result = _result_event(events)
            assert result.metadata.get("answer_now") is True
            assert "Hello world" in str(result.metadata.get("response", ""))

    @pytest.mark.asyncio
    async def test_chat_answer_now_strips_protocol_label(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("``FI", "NISH``\n", "Hello now"):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain Fourier",
                    "partial_response": "Partial trace",
                    "events": [],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert "FINISH" not in text
            assert text == "Hello now"
            result = _result_event(events)
            assert result.metadata.get("response") == "Hello now"

    @pytest.mark.asyncio
    async def test_chat_answer_now_strips_bare_protocol_label(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("FI", "NISH\n", "Hello bare"):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain Fourier",
                    "partial_response": "",
                    "events": [],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert "FINISH" not in text
            assert text == "Hello bare"
            result = _result_event(events)
            assert result.metadata.get("response") == "Hello bare"

    @pytest.mark.asyncio
    async def test_chat_answer_now_strips_variable_backtick_protocol_label(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("```FI", "NISH```\n", "Hello fenced"):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain Fourier",
                    "partial_response": "",
                    "events": [],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert "FINISH" not in text
            assert text == "Hello fenced"
            result = _result_event(events)
            assert result.metadata.get("response") == "Hello fenced"

    @pytest.mark.asyncio
    async def test_chat_answer_now_strips_spaced_protocol_label(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("\u200b`` FI", "NISH ``\n", "Hello spaced"):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain Fourier",
                    "partial_response": "",
                    "events": [],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert "FINISH" not in text
            assert text == "Hello spaced"
            result = _result_event(events)
            assert result.metadata.get("response") == "Hello spaced"

    @pytest.mark.asyncio
    async def test_chat_answer_now_preserves_normal_word_prefix(self) -> None:
        from deeptutor.agents.chat import agentic_pipeline as ap_module

        async def _fake_stream(self: Any, _messages: Any, **_kwargs: Any):
            for chunk in ("FIN", "ISHED tasks stay visible."):
                yield chunk

        cfg = _fake_llm_config()

        with (
            patch.object(
                ap_module.AgenticChatPipeline,
                "_stream_messages",
                _fake_stream,
            ),
            patch(
                "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
                return_value=cfg,
            ),
        ):
            from deeptutor.capabilities.chat import ChatCapability

            ctx = _build_context(
                capability="chat",
                payload={
                    "original_user_message": "Explain finished states",
                    "partial_response": "",
                    "events": [],
                },
            )
            bus = StreamBus()
            cap = ChatCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            text = _content_text(events)
            assert text == "FINISHED tasks stay visible."
            result = _result_event(events)
            assert result.metadata.get("response") == "FINISHED tasks stay visible."


class TestVisualizeAnswerNow:
    @pytest.mark.asyncio
    async def test_emits_renderable_code_envelope(self) -> None:
        cfg = _fake_llm_config()
        payload_json = json.dumps(
            {
                "render_type": "svg",
                "code": "<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'/>",
            }
        )
        with (
            patch.object(_answer_now, "get_llm_config", return_value=cfg),
            patch.object(_answer_now, "llm_stream", _make_stream_factory([payload_json])),
        ):
            from deeptutor.capabilities.visualize import VisualizeCapability

            ctx = _build_context(
                capability="visualize",
                payload={
                    "original_user_message": "Draw a circle",
                    "events": [],
                },
                config_overrides={"render_mode": "svg"},
            )
            bus = StreamBus()
            cap = VisualizeCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            result = _result_event(events)
            assert result.metadata.get("render_type") == "svg"
            code = result.metadata.get("code") or {}
            assert code.get("language") == "svg"
            assert "<svg" in code.get("content", "")
            assert result.metadata.get("metadata", {}).get("answer_now") is True

            content = _content_text(events)
            assert "```svg" in content

    @pytest.mark.asyncio
    async def test_falls_back_to_svg_when_render_type_invalid(self) -> None:
        cfg = _fake_llm_config()
        payload_json = json.dumps({"render_type": "totally-bogus", "code": "x"})
        with (
            patch.object(_answer_now, "get_llm_config", return_value=cfg),
            patch.object(_answer_now, "llm_stream", _make_stream_factory([payload_json])),
        ):
            from deeptutor.capabilities.visualize import VisualizeCapability

            ctx = _build_context(
                capability="visualize",
                payload={"original_user_message": "x", "events": []},
            )
            bus = StreamBus()
            cap = VisualizeCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            result = _result_event(events)
            assert result.metadata.get("render_type") == "svg"

    @pytest.mark.asyncio
    async def test_strips_code_fences_around_json(self) -> None:
        cfg = _fake_llm_config()
        fenced = '```json\n{"render_type": "mermaid", "code": "graph TD;A-->B"}\n```'
        with (
            patch.object(_answer_now, "get_llm_config", return_value=cfg),
            patch.object(_answer_now, "llm_stream", _make_stream_factory([fenced])),
        ):
            from deeptutor.capabilities.visualize import VisualizeCapability

            ctx = _build_context(
                capability="visualize",
                payload={"original_user_message": "diagram", "events": []},
            )
            bus = StreamBus()
            cap = VisualizeCapability()
            events = await _drain(bus, cap.run(ctx, bus))

            result = _result_event(events)
            assert result.metadata.get("render_type") == "mermaid"
            assert "graph TD" in (result.metadata.get("code") or {}).get("content", "")


class TestMathAnimatorAnswerNow:
    """Math animator's fast-path keeps the real ``code_generation`` +
    ``render`` stages — those are the whole point of the capability —
    while skipping ``concept_analysis``, ``concept_design`` and
    ``summary``. We verify dispatch and result envelope by mocking the
    pipeline's two retained stages so we don't actually invoke Manim."""

    @pytest.mark.asyncio
    async def test_skips_analysis_design_summary_but_calls_codegen_and_render(
        self,
    ) -> None:
        # Skip the whole test cleanly when manim isn't available, since
        # math_animator.run() short-circuits before we can patch anything.
        import importlib.util as _ilu

        from deeptutor.agents.math_animator.models import (
            GeneratedCode,
            RenderResult,
        )

        if _ilu.find_spec("manim") is None:
            pytest.skip("manim not installed; math_animator answer-now test skipped")

        from deeptutor.capabilities.math_animator import MathAnimatorCapability

        analysis_agent_calls: list[Any] = []
        design_agent_calls: list[Any] = []
        summary_agent_calls: list[Any] = []

        with patch("deeptutor.agents.math_animator.pipeline.MathAnimatorPipeline") as PipelineCls:
            pipeline_instance = PipelineCls.return_value
            pipeline_instance.run_analysis = AsyncMock(
                side_effect=lambda *a, **k: analysis_agent_calls.append(("a",))
            )
            pipeline_instance.run_design = AsyncMock(
                side_effect=lambda *a, **k: design_agent_calls.append(("d",))
            )
            pipeline_instance.run_summary = AsyncMock(
                side_effect=lambda *a, **k: summary_agent_calls.append(("s",))
            )
            pipeline_instance.run_code_generation = AsyncMock(
                return_value=GeneratedCode(code="from manim import *\nclass S(Scene): pass")
            )
            pipeline_instance.run_render = AsyncMock(
                return_value=(
                    "from manim import *\nclass S(Scene): pass",
                    RenderResult(
                        output_mode="video",
                        artifacts=[],
                        public_code_path="",
                        source_code_path="/tmp/scene.py",
                        quality="medium",
                        retry_attempts=0,
                        retry_history=[],
                        visual_review=None,
                    ),
                )
            )

            cap = MathAnimatorCapability()
            ctx = _build_context(
                capability="math_animator",
                payload={
                    "original_user_message": "Animate a sine wave",
                    "events": [],
                },
                config_overrides={"output_mode": "video", "quality": "medium"},
            )
            bus = StreamBus()
            events = await _drain(bus, cap.run(ctx, bus))

            # Skipped stages must NOT have been invoked.
            assert pipeline_instance.run_analysis.await_count == 0
            assert pipeline_instance.run_design.await_count == 0
            assert pipeline_instance.run_summary.await_count == 0
            # Retained stages MUST have been invoked exactly once.
            assert pipeline_instance.run_code_generation.await_count == 1
            assert pipeline_instance.run_render.await_count == 1

            result = _result_event(events)
            assert result.metadata.get("metadata", {}).get("answer_now") is True
            assert result.metadata.get("output_mode") == "video"
            assert result.metadata.get("code", {}).get("language") == "python"


# ---------------------------------------------------------------------------
# 3. Bypass — when no payload is set, the normal path runs
# ---------------------------------------------------------------------------


class TestNormalPathWhenNoAnswerNow:
    """A defensive check: capabilities must NOT enter the fast-path
    when ``answer_now_context`` is absent. If they did, the regular
    pipeline would be silently shadowed."""

    @pytest.mark.asyncio
    async def test_deep_solve_without_payload_calls_pipeline(self) -> None:
        from deeptutor.capabilities.deep_solve import DeepSolveCapability

        # Without an answer_now payload the capability must go through the
        # normal SolvePipeline path (not the fast-path), and forward its
        # ``stream.result`` payload to the consumer.
        with (
            patch("deeptutor.capabilities.deep_solve.SolvePipeline") as PipelineCls,
            patch("deeptutor.services.llm.config.get_llm_config", return_value=_fake_llm_config()),
        ):
            pipeline = PipelineCls.return_value

            async def _run(*, stream: StreamBus, **_kwargs: Any) -> dict[str, Any]:
                payload = {"response": "from pipeline", "metadata": {}}
                await stream.result(payload, source="deep_solve")
                return payload

            pipeline.run = AsyncMock(side_effect=_run)

            cap = DeepSolveCapability()
            ctx = _build_context(
                capability="deep_solve",
                payload=None,
                user_message="topic",
            )
            bus = StreamBus()
            events = await _drain(bus, cap.run(ctx, bus))

            pipeline.run.assert_awaited_once()
            result = _result_event(events)
            assert "from pipeline" in str(result.metadata.get("response", ""))
