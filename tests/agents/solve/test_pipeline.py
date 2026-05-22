"""Unit + integration tests for ``SolvePipeline``.

Covers:

* JSON plan parsing (valid / empty / malformed)
* Tone-key selection by step position
* Step-finish rendering (empty / non-empty)
* One-step happy path: pre-retrieve skipped, plan, ``FINISH`` per step,
  synthesize, ``stream.result`` payload
* Multi-step ``REPLAN`` back-edge: step 1 emits ``REPLAN``, plan re-runs,
  new plan completes
* Replan budget exhaustion: ``REPLAN`` fallback becomes step content
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from deeptutor.agents.solve.pipeline import (
    _PROTOCOL_STEP,
    Plan,
    PlanStep,
    SolvePipeline,
    StepFinish,
)
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus

# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


async def _collect_bus_events(bus: StreamBus) -> tuple[list[StreamEvent], asyncio.Task[Any]]:
    events: list[StreamEvent] = []

    async def _consume() -> None:
        async for event in bus.subscribe():
            events.append(event)

    consumer = asyncio.create_task(_consume())
    await asyncio.sleep(0)
    return events, consumer  # type: ignore[return-value]


def _llm_chunk(
    *,
    content: str | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> SimpleNamespace:
    delta_fields: dict[str, Any] = {"content": content}
    if tool_calls is not None:
        delta_fields["tool_calls"] = [
            SimpleNamespace(
                index=tc.get("index", i),
                id=tc.get("id"),
                function=SimpleNamespace(
                    name=tc.get("name"),
                    arguments=tc.get("arguments"),
                ),
            )
            for i, tc in enumerate(tool_calls)
        ]
    else:
        delta_fields["tool_calls"] = None
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(**delta_fields))])


async def _async_stream(chunks: list[SimpleNamespace]):
    for chunk in chunks:
        yield chunk


class _ScriptedChatClient:
    """Plays back a queue of scripted streams. Each call to
    ``chat.completions.create`` pops one stream from ``script``."""

    def __init__(self, scripted: list[list[SimpleNamespace]]) -> None:
        self._script = list(scripted)
        self.calls: list[dict[str, Any]] = []

        outer = self

        class _Completions:
            async def create(self, **kwargs: Any):
                outer.calls.append({**kwargs, "messages": list(kwargs.get("messages") or [])})
                if not outer._script:
                    raise RuntimeError("Scripted client exhausted")
                return _async_stream(outer._script.pop(0))

        class _Chat:
            completions = _Completions()

        self.chat = _Chat()


def _stub_llm_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "deeptutor.agents.solve.pipeline.get_llm_config",
        lambda: SimpleNamespace(
            binding="openai",
            model="gpt-test",
            api_key="k",
            base_url="https://x.test",
            api_version=None,
            extra_headers=None,
        ),
    )


def _stub_empty_tool_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = SimpleNamespace(
        get_enabled=lambda selected: [],
        get=lambda name: None,
        build_openai_schemas=lambda names: [],
        build_prompt_text=lambda *_args, **_kwargs: "",
    )
    monkeypatch.setattr(
        "deeptutor.agents.solve.pipeline.get_tool_registry",
        lambda: registry,
    )


def _make_pipeline(monkeypatch: pytest.MonkeyPatch, **overrides: Any) -> SolvePipeline:
    _stub_llm_config(monkeypatch)
    _stub_empty_tool_registry(monkeypatch)
    return SolvePipeline(**overrides)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_parse_plan_valid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    raw = '{"analysis": "two-part", "steps": [{"id":"S1","goal":"first"},{"id":"S2","goal":"second"}]}'
    plan = pipeline._parse_plan(raw)
    assert plan.analysis == "two-part"
    assert [s.id for s in plan.steps] == ["S1", "S2"]
    assert [s.goal for s in plan.steps] == ["first", "second"]


def test_parse_plan_empty_steps_falls_back_to_single_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = _make_pipeline(monkeypatch)
    plan = pipeline._parse_plan('{"analysis": "x", "steps": []}')
    assert len(plan.steps) == 1
    assert plan.steps[0].id == "S1"


def test_parse_plan_malformed_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    plan = pipeline._parse_plan("not json at all")
    assert len(plan.steps) == 1
    assert "Failed to parse" in plan.analysis


def test_parse_plan_skips_step_without_goal(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    raw = '{"analysis":"a","steps":[{"id":"S1","goal":""},{"id":"S2","goal":"keeper"}]}'
    plan = pipeline._parse_plan(raw)
    assert [s.id for s in plan.steps] == ["S2"]


def test_tone_key_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    assert pipeline._tone_key(0, 1) == "only"
    assert pipeline._tone_key(0, 3) == "first"
    assert pipeline._tone_key(1, 3) == "middle"
    assert pipeline._tone_key(2, 3) == "last"


def test_render_step_finishes_renders_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    finishes = [
        StepFinish(step=PlanStep(id="S1", goal="setup"), text="Let's first ..."),
        StepFinish(step=PlanStep(id="S2", goal="wrap"), text="Finally ..."),
    ]
    rendered = pipeline._render_step_finishes(finishes)
    assert "[S1]" in rendered and "setup" in rendered
    assert "[S2]" in rendered and "wrap" in rendered
    assert "Let's first ..." in rendered
    assert "Finally ..." in rendered


def test_render_step_finishes_empty_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    rendered = pipeline._render_step_finishes([])
    # YAML "empty.no_step_sections" — checks the fallback string is non-empty.
    assert rendered.strip() != ""


def test_resolved_tools_auto_mounts_rag_with_kb(monkeypatch: pytest.MonkeyPatch) -> None:
    """When a KB is attached and ``rag`` is registry-resident, it gets
    auto-mounted even if the caller didn't request it."""
    _stub_llm_config(monkeypatch)
    rag_tool = SimpleNamespace(name="rag")
    registry = SimpleNamespace(
        get_enabled=lambda selected: [],
        get=lambda name: rag_tool if name == "rag" else None,
        build_openai_schemas=lambda names: [],
        build_prompt_text=lambda *_a, **_k: "",
    )
    monkeypatch.setattr(
        "deeptutor.agents.solve.pipeline.get_tool_registry",
        lambda: registry,
    )
    pipeline = SolvePipeline(kb_name="course-kb", enabled_tools=[])
    assert "rag" in pipeline._resolved_tools()


def test_compose_full_response_concatenates(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _make_pipeline(monkeypatch)
    finishes = [
        StepFinish(step=PlanStep(id="S1", goal="g"), text="first section"),
        StepFinish(step=PlanStep(id="S2", goal="g"), text="second section"),
    ]
    body = pipeline._compose_full_response(finishes, "final wrap-up")
    assert body == "first section\n\nsecond section\n\nfinal wrap-up"


# ---------------------------------------------------------------------------
# Integration: one-step happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_one_step_happy_path_emits_plan_finish_synthesize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end: no KB, one-step plan, one ``FINISH`` iteration, then the
    synthesize ``FINISH``. Verifies the orchestrator drives the three phases
    and the result payload reflects the full conversation."""
    pipeline = _make_pipeline(monkeypatch)
    client = _ScriptedChatClient(
        [
            # Phase 1: planner emits ``PLAN`` + JSON
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"single","steps":[{"id":"S1","goal":"answer"}]}'),
            ],
            # Phase 2: step S1 emits ``FINISH`` directly
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="The answer to the question is 42."),
            ],
            # Phase 2.5: explain triage decides this is too simple → SKIP
            [
                _llm_chunk(content="``SKIP``\n"),
            ],
            # Phase 3: synthesize emits ``FINISH`` with the precise answer
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Final: 42. Briefly: we computed 42."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-1",
        user_message="what is the answer?",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-1"},
    )
    payload = await pipeline.run(
        context=context,
        question=context.user_message,
        attachments=None,
        conversation_context="",
        memory_context="",
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    # Four LLM calls: plan, step S1, explain-judge (SKIP), synthesize.
    assert len(client.calls) == 4
    # The step FINISH and synthesize FINISH both streamed as content events.
    content_events = [
        e for e in events if e.type == StreamEventType.CONTENT and e.source == "deep_solve"
    ]
    bodies = "".join(e.content for e in content_events)
    assert "The answer to the question is 42." in bodies
    assert "Final: 42" in bodies
    # Result payload reflects step count + synthesis.
    assert payload["step_count"] == 1
    assert payload["completed_steps"] == 1
    assert payload["plan_revisions"] == 0
    assert "The answer to the question is 42." in payload["response"]
    assert "Final: 42" in payload["response"]


# ---------------------------------------------------------------------------
# Integration: multi-step happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_two_step_happy_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end: 2-step plan, each step's loop closes with ``FINISH`` on the
    first iteration, then synthesize. Verifies the per-step loop actually
    advances to the next step (the bug Frank saw was Phase 2 silently stopping
    after the first plan)."""
    pipeline = _make_pipeline(monkeypatch)
    client = _ScriptedChatClient(
        [
            # Phase 1: planner emits a 2-step plan
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(
                    content='{"analysis":"two parts","steps":[{"id":"S1","goal":"explore"},{"id":"S2","goal":"conclude"}]}'
                ),
            ],
            # Phase 2 / step S1: FINISH directly
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Let's first explore the concept."),
            ],
            # Step S1 explain triage → SKIP
            [
                _llm_chunk(content="``SKIP``\n"),
            ],
            # Phase 2 / step S2: FINISH directly
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Finally, we conclude with the answer."),
            ],
            # Step S2 explain triage → SKIP
            [
                _llm_chunk(content="``SKIP``\n"),
            ],
            # Phase 3: synthesize
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Overall: explored and concluded."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-multi",
        user_message="what is agentic rag?",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-multi"},
    )
    payload = await pipeline.run(
        context=context,
        question=context.user_message,
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    # Six LLM calls: plan + step1 + judge1 + step2 + judge2 + synthesize.
    assert len(client.calls) == 6, (
        f"Expected 6 LLM calls (plan + 2 steps + 2 explain-judges + synthesize), got {len(client.calls)}"
    )
    assert payload["step_count"] == 2
    assert payload["completed_steps"] == 2
    assert payload["plan_revisions"] == 0
    # All three FINISH bodies stream to user as content.
    body = payload["response"]
    assert "Let's first explore" in body
    assert "Finally, we conclude" in body
    assert "Overall: explored and concluded" in body


# ---------------------------------------------------------------------------
# Integration: REPLAN back-edge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replan_back_edge_reruns_planner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step 1 of the first plan emits ``REPLAN``; the orchestrator re-enters
    the planner, the new plan's step 1 emits ``FINISH``, synthesis runs."""
    pipeline = _make_pipeline(monkeypatch, max_replans=2)
    client = _ScriptedChatClient(
        [
            # First plan
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"v1","steps":[{"id":"S1","goal":"old approach"}]}'),
            ],
            # Step S1 of plan v1: REPLAN
            [
                _llm_chunk(content="``REPLAN``\n"),
                _llm_chunk(content="The plan misses an upstream dependency."),
            ],
            # Plan v2 (with replan reason in prompt)
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"v2","steps":[{"id":"S1","goal":"new approach"}]}'),
            ],
            # Step S1 of plan v2: FINISH
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Revised section."),
            ],
            # Explain triage for the FINISHed step → SKIP
            [
                _llm_chunk(content="``SKIP``\n"),
            ],
            # Synthesize
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="All wrapped up."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    _events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-2",
        user_message="something complex",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-2"},
    )
    payload = await pipeline.run(
        context=context,
        question=context.user_message,
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    assert payload["plan_revisions"] == 1
    assert payload["step_count"] == 1  # final plan had one step
    assert "Revised section." in payload["response"]
    assert "All wrapped up." in payload["response"]
    # 6 LLM calls: plan v1, REPLAN, plan v2, FINISH, explain-judge (SKIP), synthesize.
    # REPLAN does NOT trigger explain triage — only true FINISH does.
    assert len(client.calls) == 6


# ---------------------------------------------------------------------------
# Integration: replan budget exhaustion
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replan_budget_exhausted_keeps_reason_as_step_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ``max_replans=0`` and the step emits ``REPLAN``, the orchestrator
    accepts the REPLAN reason text as the step's section so synthesis still
    has something to anchor on."""
    pipeline = _make_pipeline(monkeypatch, max_replans=0)
    client = _ScriptedChatClient(
        [
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"a","steps":[{"id":"S1","goal":"go"}]}'),
            ],
            [
                _llm_chunk(content="``REPLAN``\n"),
                _llm_chunk(content="The plan is bad, but we have no budget."),
            ],
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Best-effort synthesis."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    _events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-3",
        user_message="hi",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-3"},
    )
    payload = await pipeline.run(
        context=context,
        question=context.user_message,
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    assert payload["plan_revisions"] == 0  # no successful replan
    assert "The plan is bad" in payload["response"]
    assert "Best-effort synthesis." in payload["response"]


# ---------------------------------------------------------------------------
# Integration: FINISH content streams chunk-by-chunk
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_step_finish_streams_chunks_live(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each step's ``FINISH`` text must arrive as multiple ``content`` events
    (one per upstream chunk) so the chat bubble fills typewriter-style,
    rather than landing in a single buffered event at the end."""
    pipeline = _make_pipeline(monkeypatch)
    finish_chunks = ["Let's first ", "explore ", "the topic. ", "Done."]
    client = _ScriptedChatClient(
        [
            # Plan: 1 step
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"a","steps":[{"id":"S1","goal":"go"}]}'),
            ],
            # Step S1 FINISH streamed in 4 separate chunks
            [_llm_chunk(content="``FINISH``\n"), *(_llm_chunk(content=c) for c in finish_chunks)],
            # Explain triage → SKIP
            [_llm_chunk(content="``SKIP``\n")],
            # Synthesize: also chunked
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Wrap "),
                _llm_chunk(content="up."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-stream",
        user_message="q",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "t-stream"},
    )
    await pipeline.run(
        context=context,
        question=context.user_message,
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    body_content_events = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT
        and (e.metadata or {}).get("call_kind") == "llm_final_response"
    ]
    body_texts = [e.content for e in body_content_events]
    # Per-step FINISH chunks land as separate events (live streaming):
    for piece in finish_chunks:
        assert piece in body_texts, (
            f"expected chunk {piece!r} to appear as its own content event; got {body_texts!r}"
        )
    # Synthesize chunks also stream live (separate events).
    assert "Wrap " in body_texts and "up." in body_texts


@pytest.mark.asyncio
async def test_step_finish_streams_many_small_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real LLMs typically emit FINISH content as 20–100 small chunks. Confirm
    each one lands as its own ``content`` event so the chat bubble fills
    character-by-character, not in one buffered burst."""
    pipeline = _make_pipeline(monkeypatch)
    # 20 chunks of 1–4 chars each.
    step_chunks = [
        "L",
        "et",
        "'s ",
        "f",
        "irst",
        " ex",
        "pl",
        "ore",
        " the",
        " co",
        "n",
        "ce",
        "pt",
        ".",
        " ",
        "T",
        "h",
        "en",
        ":",
        " done.",
    ]
    expected_full_text = "".join(step_chunks)

    client = _ScriptedChatClient(
        [
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"x","steps":[{"id":"S1","goal":"g"}]}'),
            ],
            [_llm_chunk(content="``FINISH``\n"), *(_llm_chunk(content=c) for c in step_chunks)],
            # Explain triage → SKIP (so the step's FINISH chunks are still the only
            # llm_final_response events in stage=reasoning).
            [_llm_chunk(content="``SKIP``\n")],
            [_llm_chunk(content="``FINISH``\n"), _llm_chunk(content="done.")],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-many",
        user_message="q",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "t-many"},
    )
    payload = await pipeline.run(context=context, question=context.user_message, stream=bus)
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    # Find the per-step FINISH chunks (stage=reasoning). Filter out
    # section-break events the pipeline injects between sections so they
    # don't inflate the per-chunk count.
    step_body_events = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT
        and e.stage == "reasoning"
        and (e.metadata or {}).get("call_kind") == "llm_final_response"
        and not (e.metadata or {}).get("section_break")
    ]
    # Each scripted chunk produces its own event — exactly 20 events for
    # the step's FINISH content (one per upstream chunk).
    assert len(step_body_events) == len(step_chunks), (
        f"expected {len(step_chunks)} per-chunk events, got {len(step_body_events)}"
    )
    # Concatenation matches the original text — nothing dropped or reordered.
    assert "".join(e.content for e in step_body_events) == expected_full_text
    assert expected_full_text in payload["response"]
    # A section break must be emitted between the step's FINISH and the
    # synthesize phase — otherwise '## Header' in the next section would
    # glue onto the prior paragraph's last chunk and collapse.
    section_breaks = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT and (e.metadata or {}).get("section_break")
    ]
    assert section_breaks, "expected at least one section-break event between sections"
    assert all(e.content == "\n\n" for e in section_breaks)


# ---------------------------------------------------------------------------
# Integration: deep-explain triage triggers explain expansion under FINISH
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_explain_triage_explain_path_streams_under_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the triage call returns ``EXPLAIN``, the pipeline runs a deeper
    explanation pass whose text streams as additional ``content`` events
    under the step's FINISH and is folded into the final response payload."""
    pipeline = _make_pipeline(monkeypatch)
    client = _ScriptedChatClient(
        [
            # Plan: 1 step
            [
                _llm_chunk(content="``PLAN``\n"),
                _llm_chunk(content='{"analysis":"a","steps":[{"id":"S1","goal":"derive"}]}'),
            ],
            # Step S1: FINISH with a non-trivial concept
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="By symmetry, the integral vanishes."),
            ],
            # Explain triage → EXPLAIN with a focus sentence
            [
                _llm_chunk(content="``EXPLAIN``\n"),
                _llm_chunk(content="the parity argument behind the vanishing integral."),
            ],
            # Deep explain → FINISH with the expansion
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(
                    content="**Intuition:** odd integrand over a symmetric domain integrates to zero."
                ),
            ],
            # Synthesize
            [
                _llm_chunk(content="``FINISH``\n"),
                _llm_chunk(content="Wrap-up."),
            ],
        ]
    )
    monkeypatch.setattr(pipeline, "_build_client", lambda: client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-explain",
        user_message="why does this integral vanish?",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-explain"},
    )
    payload = await pipeline.run(
        context=context,
        question=context.user_message,
        stream=bus,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    # Five LLM calls: plan + step + judge (EXPLAIN) + deep-explain + synthesize.
    assert len(client.calls) == 5, (
        f"Expected 5 LLM calls, got {len(client.calls)}: judge must trigger deep-explain"
    )
    # Both the FINISH text and the deep-explain text appear in the final response.
    body = payload["response"]
    assert "By symmetry, the integral vanishes." in body
    assert "odd integrand over a symmetric domain" in body
    # Both should also have streamed as user-visible content events.
    content_events = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT
        and (e.metadata or {}).get("call_kind") == "llm_final_response"
    ]
    bodies = "".join(e.content for e in content_events)
    assert "By symmetry" in bodies
    assert "odd integrand over a symmetric domain" in bodies
    # The EXPLAIN content is wrapped in a <details open> block so the user
    # can fold it. Both the live stream and the persisted response payload
    # must contain the wrapping tags (with the triage focus in the summary).
    assert "<details open>" in bodies
    assert "</details>" in bodies
    assert "<summary>" in bodies
    assert "parity argument behind the vanishing integral" in bodies  # focus
    assert "<details open>" in body
    assert "</details>" in body
    # The wrapping events carry a ``details_wrapper`` flag so the frontend
    # / tests can distinguish them from the LLM body.
    wrapper_events = [e for e in events if (e.metadata or {}).get("details_wrapper")]
    assert len(wrapper_events) == 2, (
        f"Expected exactly 2 details-wrapper events (open + close), got {len(wrapper_events)}"
    )
    # Two section breaks must fire on the EXPLAIN path: one after the step
    # FINISH (before the explain expansion starts) and one after the deep
    # explain (before the synthesize section starts). Without them the
    # next chunk would glue onto the prior sentence and break markdown
    # block rendering (e.g. a leading ``##`` would no longer be a heading).
    section_breaks = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT and (e.metadata or {}).get("section_break")
    ]
    assert len(section_breaks) == 2, (
        f"Expected 2 section breaks (after FINISH, after EXPLAIN), got {len(section_breaks)}"
    )
    assert all(e.content == "\n\n" for e in section_breaks)


# ---------------------------------------------------------------------------
# Visible failure: pipeline exceptions surface as ERROR + CONTENT
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pipeline_failure_surfaces_visible_error_and_reraises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If an LLM call raises (network error, bad arg, ...) the pipeline must
    emit a labeled ERROR card + a CONTENT event so the chat bubble shows the
    problem instead of looking like a silent termination — then re-raise so
    the orchestrator's normal error path runs."""
    pipeline = _make_pipeline(monkeypatch)

    class _FailingCompletions:
        async def create(self, **kwargs: Any):
            raise RuntimeError("simulated upstream failure")

    failing_client = SimpleNamespace(chat=SimpleNamespace(completions=_FailingCompletions()))
    monkeypatch.setattr(pipeline, "_build_client", lambda: failing_client)

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="s-fail",
        user_message="hi",
        knowledge_bases=[],
        language="en",
        metadata={"turn_id": "turn-fail"},
    )

    with pytest.raises(RuntimeError, match="simulated upstream failure"):
        await pipeline.run(
            context=context,
            question=context.user_message,
            stream=bus,
        )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    error_events = [e for e in events if e.type == StreamEventType.ERROR]
    content_events = [
        e
        for e in events
        if e.type == StreamEventType.CONTENT
        and (e.metadata or {}).get("call_kind") == "llm_final_response"
    ]
    assert error_events, "pipeline must emit a visible ERROR event on failure"
    assert any("simulated upstream failure" in e.content for e in error_events)
    assert content_events, "pipeline must also emit a CONTENT event so the chat bubble renders"
    assert any("simulated upstream failure" in e.content for e in content_events)
    # The error card has a call_id so TracePanels groups it under a real card
    # (a bare bus.error without call_id is invisible in the chat-bubble UI).
    err = error_events[0]
    assert (err.metadata or {}).get("call_id"), "error event must carry call_id"


# ---------------------------------------------------------------------------
# Smoke: protocol constants are wired correctly
# ---------------------------------------------------------------------------


def test_protocol_step_label_set() -> None:
    assert _PROTOCOL_STEP.allowed == ("THINK", "TOOL", "FINISH", "REPLAN")
    assert _PROTOCOL_STEP.terminal == frozenset({"FINISH", "REPLAN"})
    assert _PROTOCOL_STEP.final == frozenset({"FINISH"})
    assert _PROTOCOL_STEP.intermediate == frozenset({"THINK"})
    assert _PROTOCOL_STEP.tool_label == "TOOL"
