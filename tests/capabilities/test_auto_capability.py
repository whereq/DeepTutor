"""Integration tests for the ``auto`` capability.

End-to-end tests of ``AutoPipeline`` with the OpenAI client mocked. They cover:

PR 1
* ``auto`` registered in capability registry, ``AutoRequestConfig`` validates
* Happy path: router picks one capability, pipeline delegates, events stamped
* Plain-text router response → no delegation, text becomes the final answer
* ``enabled_capabilities`` filter restricts what the router sees
* ``_should_capture_assistant_content`` filters sub-cap CONTENT correctly

PR 2
* Router LLM API error retried up to ``max_retries_per_step`` then terminates
* Sub-capability raise retried then succeeds
* Sub-capability fails all retries → loop continues with error observation
* Same-capability quota enforced
* Iteration cap triggers synthesizer fallback
* Atomic tool dispatch (rag with kb_name auto-injection)
* Cancellation propagates from parent into in-flight sub-cap
* ``answer_now`` payload triggers fast-path synthesis
"""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deeptutor.capabilities.auto import AutoCapability
from deeptutor.capabilities.request_contracts import (
    AutoRequestConfig,
    validate_auto_request_config,
)
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus
from deeptutor.runtime.registry.capability_registry import get_capability_registry
from deeptutor.services.session.turn_runtime import _should_capture_assistant_content

# =========================================================================== #
# Streaming-response helpers                                                    #
# =========================================================================== #


def _chunk(
    *,
    content: str | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> SimpleNamespace:
    """Build a single ChatCompletionChunk-shaped object."""
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
    return SimpleNamespace(
        choices=[SimpleNamespace(delta=SimpleNamespace(**delta_fields))]
    )


async def _async_iter(chunks: list[SimpleNamespace]):
    for chunk in chunks:
        yield chunk


def _stream_for_text(text: str) -> list[SimpleNamespace]:
    """Stream that emits a single text response, no tool calls."""
    return [_chunk(content=text)]


def _stream_for_tool_call(cap_name: str, config: dict[str, Any]) -> list[SimpleNamespace]:
    """Stream that yields one complete tool_call (delegate_to_<cap>)."""
    return [
        _chunk(
            tool_calls=[
                {
                    "index": 0,
                    "id": "call-1",
                    "name": f"delegate_to_{cap_name}",
                    "arguments": json.dumps({"config": config, "rationale": "test"}),
                }
            ]
        )
    ]


def _stream_for_atomic_tool(tool_name: str, args: dict[str, Any]) -> list[SimpleNamespace]:
    return [
        _chunk(
            tool_calls=[
                {
                    "index": 0,
                    "id": "call-atomic",
                    "name": tool_name,
                    "arguments": json.dumps(args),
                }
            ]
        )
    ]


class _ScriptedClient:
    """Mock OpenAI client whose ``chat.completions.create`` returns a scripted

    sequence of streaming responses. Each call consumes the next entry; if the
    entry is an Exception subclass instance, it is raised instead of returned.
    """

    def __init__(self, scripted: list[Any]) -> None:
        self._script: list[Any] = list(scripted)
        self.call_count = 0
        self.last_kwargs: dict[str, Any] | None = None

        class _Completions:
            def __init__(self, parent: _ScriptedClient) -> None:
                self.parent = parent

            async def create(self, **kwargs):  # noqa: D401
                self.parent.last_kwargs = kwargs
                self.parent.call_count += 1
                if not self.parent._script:
                    raise RuntimeError("Scripted client exhausted")
                item = self.parent._script.pop(0)
                if isinstance(item, BaseException):
                    raise item
                # item is a list of chunks for streaming.
                return _async_iter(item)

        class _Chat:
            def __init__(self, parent: _ScriptedClient) -> None:
                self.completions = _Completions(parent)

        self.chat = _Chat(self)


def _fake_llm_config() -> MagicMock:
    cfg = MagicMock()
    cfg.binding = "openai"
    cfg.model = "gpt-4o-mini"
    cfg.api_key = "sk-test"
    cfg.base_url = None
    cfg.api_version = None
    cfg.extra_headers = None
    return cfg


class _StubSubCapability(BaseCapability):
    """Configurable fake sub-capability for integration tests."""

    def __init__(
        self,
        name: str,
        response_text: str = "sub-output",
        raise_on_attempts: tuple[int, ...] = (),
    ) -> None:
        self.manifest = CapabilityManifest(
            name=name,
            description=f"stub for {name}",
            stages=["go"],
            request_schema={"type": "object", "properties": {}},
        )
        self.response_text = response_text
        self.run_count = 0
        self._raise_on = set(raise_on_attempts)
        self.received_contexts: list[UnifiedContext] = []

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        self.run_count += 1
        self.received_contexts.append(context)
        if self.run_count in self._raise_on:
            raise RuntimeError(f"{self.name} fail attempt {self.run_count}")
        await stream.thinking("sub-thinking", source=self.name, stage="go")
        await stream.content(f"{self.response_text} (run {self.run_count})", source=self.name, stage="go")
        await stream.result(
            {"response": f"{self.response_text} (run {self.run_count})"},
            source=self.name,
        )


@pytest.fixture
def fake_registry():
    """Fresh CapabilityRegistry preloaded with builtins; tests register stubs."""
    from deeptutor.runtime.registry.capability_registry import CapabilityRegistry

    reg = CapabilityRegistry()
    reg.load_builtins()
    return reg


@pytest.fixture
def mock_llm():
    """Patch get_llm_config + LLM client at the AutoPipeline level."""
    with patch(
        "deeptutor.agents.auto.auto_pipeline.get_llm_config",
        return_value=_fake_llm_config(),
    ):
        yield


def _drained_events(bus: StreamBus) -> list[StreamEvent]:
    return list(bus._history)


def _install_scripted_client(client: _ScriptedClient):
    return patch.object(
        __import__("deeptutor.agents.auto.auto_pipeline", fromlist=["AutoPipeline"]).AutoPipeline,
        "_build_openai_client",
        return_value=client,
    )


# =========================================================================== #
# Smoke / config tests                                                          #
# =========================================================================== #


def test_auto_capability_is_registered():
    reg = get_capability_registry()
    assert "auto" in reg.list_capabilities()
    cap = reg.get("auto")
    assert isinstance(cap, AutoCapability)
    assert cap.manifest.stages == ["analyzing", "delegating", "synthesizing"]


def test_auto_request_config_defaults():
    cfg = validate_auto_request_config(None)
    assert isinstance(cfg, AutoRequestConfig)
    assert cfg.max_iterations == 4
    assert cfg.max_retries_per_step == 3
    assert cfg.max_same_capability_calls == 2
    assert cfg.enabled_capabilities == []


def test_auto_request_config_rejects_unknown_field():
    with pytest.raises(ValueError):
        validate_auto_request_config({"not_a_field": 1})


def test_auto_request_config_enforces_bounds():
    with pytest.raises(ValueError):
        validate_auto_request_config({"max_iterations": 99})


def test_history_capture_filter_drops_subcap_content():
    """Sub-cap CONTENT with call_id is filtered; auto's final synth is kept."""
    sub_event = StreamEvent(
        type=StreamEventType.CONTENT,
        content="from sub-capability",
        metadata={"call_id": "auto-delegation-abc"},
    )
    auto_final = StreamEvent(
        type=StreamEventType.CONTENT,
        content="final synthesis",
        metadata={"call_kind": "llm_final_response"},
    )
    auto_plain = StreamEvent(
        type=StreamEventType.CONTENT,
        content="plain content with no metadata",
        metadata={},
    )

    assert _should_capture_assistant_content(sub_event) is False
    assert _should_capture_assistant_content(auto_final) is True
    assert _should_capture_assistant_content(auto_plain) is True


# =========================================================================== #
# Full-pipeline integration tests                                               #
# =========================================================================== #


@pytest.mark.asyncio
async def test_single_delegation_happy_path(fake_registry, mock_llm):
    """Router picks deep_question; pipeline delegates; events stamped; final synthesis emitted."""
    stub = _StubSubCapability("deep_question", response_text="generated 5 quizzes")
    fake_registry.register(stub)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s1",
        user_message="make 5 linear algebra MCQs",
        config_overrides={},
        language="en",
    )
    bus = StreamBus()

    # Script: analyzer text, router picks deep_question, synth not needed
    # because the router never gave a text response — but we DID delegate and
    # the router will be re-called for the next iteration. To exit cleanly we
    # script the second router call to give a plain-text answer.
    client = _ScriptedClient(
        [
            _stream_for_text("Acknowledging your quiz request."),  # analyzer
            _stream_for_tool_call(
                "deep_question",
                {"num_questions": 5, "topic": "linear algebra"},
            ),
            _stream_for_text("Generated your quiz."),  # iteration-2 router final text
        ]
    )

    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    events = _drained_events(bus)

    # Three LLM calls: analyzer, router-iter1 (tool_call), router-iter2 (text).
    assert client.call_count == 3

    # The sub-capability ran and saw is_sub_invocation=True.
    assert stub.run_count == 1
    assert stub.received_contexts[0].metadata.get("is_sub_invocation") is True
    assert stub.received_contexts[0].active_capability == "deep_question"
    assert stub.received_contexts[0].config_overrides.get("num_questions") == 5
    assert stub.received_contexts[0].config_overrides.get("topic") == "linear algebra"

    # Sub-events tagged with delegation metadata.
    sub_events = [ev for ev in events if ev.metadata.get("delegated_capability") == "deep_question"]
    assert len(sub_events) >= 2
    for ev in sub_events:
        assert ev.metadata.get("delegated_from") == "auto"
        assert ev.metadata.get("parent_call_id", "").startswith("auto-delegation-")

    # Sub-cap CONTENT carries call_id (prevents history pollution).
    sub_content = [ev for ev in sub_events if ev.type == StreamEventType.CONTENT]
    assert all(ev.metadata.get("call_id") for ev in sub_content)

    # Auto's final synthesis CONTENT has llm_final_response marker.
    final_events = [
        ev
        for ev in events
        if ev.type == StreamEventType.CONTENT
        and ev.metadata.get("call_kind") == "llm_final_response"
    ]
    assert len(final_events) == 1
    assert final_events[0].content == "Generated your quiz."

    result_events = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"]
    summary = result_events[0].metadata.get("auto_summary")
    assert summary["delegations"][0]["capability"] == "deep_question"
    assert summary["delegations"][0]["succeeded"] is True


@pytest.mark.asyncio
async def test_router_text_response_no_delegation(fake_registry, mock_llm):
    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(session_id="s2", user_message="hi", language="en")
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("Acknowledging."),
            _stream_for_text("Hello! How can I help?"),
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    events = _drained_events(bus)
    final_events = [
        ev
        for ev in events
        if ev.type == StreamEventType.CONTENT
        and ev.metadata.get("call_kind") == "llm_final_response"
    ]
    assert len(final_events) == 1
    assert final_events[0].content == "Hello! How can I help?"

    # No sub-capability events.
    sub_events = [ev for ev in events if ev.metadata.get("delegated_from") == "auto"]
    assert sub_events == []

    result_events = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"]
    assert result_events[0].metadata["auto_summary"]["final_path"] == "text_response"


@pytest.mark.asyncio
async def test_enabled_capabilities_filter_visible_to_router(fake_registry, mock_llm):
    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(
        session_id="s3",
        user_message="anything",
        config_overrides={"enabled_capabilities": ["visualize"]},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("Analyzer ack."),
            _stream_for_text("Final text."),
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    # The second LLM call is the router; we want to inspect the tools list.
    # The scripted client recorded last_kwargs of the LAST call (synthesizer is
    # not invoked because router gave text). The last call IS the router.
    tools = client.last_kwargs["tools"]
    cap_tools = [t["function"]["name"] for t in tools if t["function"]["name"].startswith("delegate_to_")]
    assert cap_tools == ["delegate_to_visualize"]


# =========================================================================== #
# PR 2 — retry, quotas, iteration cap, atomic tools                             #
# =========================================================================== #


@pytest.mark.asyncio
async def test_router_api_error_retry_then_success(fake_registry, mock_llm):
    """Router LLM transient error → retried (state.router_llm_retries++) → eventual success."""
    from openai import APIError

    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(session_id="s4", user_message="hello", language="en")
    bus = StreamBus()

    transient = APIError(message="transient", request=MagicMock(), body=None)
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            transient,                  # router iter 1 fails
            _stream_for_text("Hi!"),  # router iter 1 retry succeeds (text)
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    events = _drained_events(bus)
    result = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"][0]
    summary = result.metadata["auto_summary"]
    assert summary["router_retries"] == 1
    assert summary["final_path"] == "text_response"


@pytest.mark.asyncio
async def test_router_api_error_max_retries_terminates(fake_registry, mock_llm):
    """3 consecutive transient errors → terminal failure, no fallback to chat."""
    from openai import APIError

    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(
        session_id="s5",
        user_message="hello",
        config_overrides={"max_retries_per_step": 3},
        language="en",
    )
    bus = StreamBus()

    def _transient_error() -> APIError:
        return APIError(message="boom", request=MagicMock(), body=None)

    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            _transient_error(),         # router fail 1
            _transient_error(),         # router fail 2
            _transient_error(),         # router fail 3 -> terminal
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    events = _drained_events(bus)
    error_events = [ev for ev in events if ev.type == StreamEventType.ERROR]
    terminal = [ev for ev in error_events if ev.metadata.get("terminal") is True]
    assert len(terminal) == 1
    assert terminal[0].metadata.get("failure_reason") == "router_llm_exhausted"

    result = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"][0]
    assert result.metadata["auto_summary"]["final_path"] == "terminal_error"


@pytest.mark.asyncio
async def test_subcap_raises_then_succeeds_on_retry(fake_registry, mock_llm):
    """Sub-cap fails first attempt, succeeds second."""
    stub = _StubSubCapability("deep_question", raise_on_attempts=(1,))
    fake_registry.register(stub)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s6",
        user_message="quiz me",
        config_overrides={"max_retries_per_step": 3},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            _stream_for_tool_call("deep_question", {"num_questions": 1}),
            _stream_for_text("Done."),  # iter 2 final text
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    # Sub-cap ran twice (1st raised, 2nd succeeded).
    assert stub.run_count == 2

    events = _drained_events(bus)
    # A retry-marker error should be present (attempt 1 fail visible).
    retry_events = [
        ev
        for ev in events
        if ev.type == StreamEventType.ERROR
        and ev.metadata.get("trace_kind") == "delegation_retry"
    ]
    assert len(retry_events) >= 1


@pytest.mark.asyncio
async def test_subcap_fails_all_retries_loop_continues(fake_registry, mock_llm):
    """3 sub-cap failures → loop continues, router pivots to text response."""
    stub = _StubSubCapability("deep_question", raise_on_attempts=(1, 2, 3))
    fake_registry.register(stub)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s7",
        user_message="quiz me",
        config_overrides={"max_retries_per_step": 3},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            _stream_for_tool_call("deep_question", {}),  # router iter 1 — fails all 3
            _stream_for_text("Sorry, that capability is unavailable."),  # iter 2 final
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    assert stub.run_count == 3

    events = _drained_events(bus)
    result = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"][0]
    summary = result.metadata["auto_summary"]
    # Loop did NOT terminate; final path is text_response from iter 2.
    assert summary["final_path"] == "text_response"
    assert summary["delegations"][0]["succeeded"] is False
    assert summary["delegations"][0]["attempts"] == 3


@pytest.mark.asyncio
async def test_same_capability_limit_enforced(fake_registry, mock_llm):
    """Same cap called twice (allowed), third call rejected with quota message."""
    stub = _StubSubCapability("visualize")
    fake_registry.register(stub)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s8",
        user_message="visualize",
        config_overrides={"max_same_capability_calls": 2, "max_iterations": 5},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            _stream_for_tool_call("visualize", {"render_mode": "svg"}),  # iter 1 ok
            _stream_for_tool_call("visualize", {"render_mode": "svg"}),  # iter 2 ok
            _stream_for_tool_call("visualize", {"render_mode": "svg"}),  # iter 3 rejected
            _stream_for_text("Final."),  # iter 4 text
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    # Only 2 actual runs (3rd call was rejected before delegation).
    assert stub.run_count == 2

    events = _drained_events(bus)
    quota_errors = [
        ev
        for ev in events
        if ev.type == StreamEventType.ERROR
        and ev.metadata.get("trace_kind") == "same_cap_exhausted"
    ]
    assert len(quota_errors) == 1


@pytest.mark.asyncio
async def test_iteration_cap_falls_to_synthesizer(fake_registry, mock_llm):
    """Loop hits max_iterations without natural text → synthesizer composes final."""
    stub = _StubSubCapability("visualize")
    fake_registry.register(stub)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s9",
        user_message="visualize",
        config_overrides={"max_iterations": 2, "max_same_capability_calls": 4},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),  # analyzer
            _stream_for_tool_call("visualize", {}),  # iter 1
            _stream_for_tool_call("visualize", {}),  # iter 2 — hits cap
            _stream_for_text("Wrapping up."),  # synthesizer
        ]
    )
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    events = _drained_events(bus)
    final = [
        ev
        for ev in events
        if ev.type == StreamEventType.CONTENT
        and ev.metadata.get("call_kind") == "llm_final_response"
    ]
    assert len(final) == 1
    assert final[0].content == "Wrapping up."

    result = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"][0]
    assert result.metadata["auto_summary"]["final_path"] == "synthesis"
    assert result.metadata["auto_summary"]["iterations"] == 2


@pytest.mark.asyncio
async def test_atomic_tool_dispatch_with_rag_kb_injection(fake_registry, mock_llm):
    """Router calls atomic rag → kb_name is injected from context."""
    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(
        session_id="s10",
        user_message="what does the doc say about gradients?",
        knowledge_bases=["my-kb"],
        language="en",
    )
    bus = StreamBus()

    captured_kwargs: dict[str, Any] = {}

    async def _fake_execute(name: str, **kwargs: Any):
        captured_kwargs.update(kwargs)
        return SimpleNamespace(
            content="rag-snippet",
            success=True,
            sources=[],
            metadata={},
        )

    client = _ScriptedClient(
        [
            _stream_for_text("ack"),
            _stream_for_atomic_tool("rag", {"query": "gradients"}),
            _stream_for_text("Based on the docs, gradients ..."),
        ]
    )

    mock_tool_registry = SimpleNamespace(
        execute=_fake_execute,
        list_tools=lambda: ["rag"],
        build_openai_schemas=lambda names=None: [
            {
                "type": "function",
                "function": {
                    "name": "rag",
                    "description": "rag",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "kb_name": {"type": "string"},
                        },
                        "required": ["query", "kb_name"],
                    },
                },
            }
        ],
    )

    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_tool_registry",
            return_value=mock_tool_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    assert captured_kwargs.get("kb_name") == "my-kb"
    assert captured_kwargs.get("query") == "gradients"


@pytest.mark.asyncio
async def test_answer_now_fast_path(fake_registry, mock_llm):
    """answer_now_context in config triggers fast-path with no LLM call."""
    auto_cap = fake_registry.get("auto")
    context = UnifiedContext(
        session_id="s11",
        user_message="anything",
        config_overrides={
            "answer_now_context": {
                "original_user_message": "what is X",
                "partial_response": "some partial work",
                "events": [],
            }
        },
        language="en",
    )
    bus = StreamBus()
    # Empty script — no LLM call should happen.
    client = _ScriptedClient([])
    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        await auto_cap.run(context, bus)

    assert client.call_count == 0

    events = _drained_events(bus)
    final = [
        ev
        for ev in events
        if ev.type == StreamEventType.CONTENT
        and ev.metadata.get("call_kind") == "llm_final_response"
    ]
    assert len(final) == 1
    assert final[0].metadata.get("answer_now") is True

    result = [ev for ev in events if ev.type == StreamEventType.RESULT and ev.source == "auto"][0]
    assert result.metadata["auto_summary"]["final_path"] == "answer_now"


@pytest.mark.asyncio
async def test_cancel_propagates_into_subcap(fake_registry, mock_llm):
    """asyncio.CancelledError from parent propagates into sub-capability."""

    class _SlowCapability(BaseCapability):
        def __init__(self) -> None:
            self.manifest = CapabilityManifest(
                name="slowcap",
                description="slow",
                stages=["wait"],
                request_schema={"type": "object", "properties": {}},
            )
            self.cancelled_during_run = False

        async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                self.cancelled_during_run = True
                raise

    slow = _SlowCapability()
    fake_registry.register(slow)
    auto_cap = fake_registry.get("auto")

    context = UnifiedContext(
        session_id="s12",
        user_message="x",
        config_overrides={"enabled_capabilities": ["slowcap"]},
        language="en",
    )
    bus = StreamBus()
    client = _ScriptedClient(
        [
            _stream_for_text("ack"),
            _stream_for_tool_call("slowcap", {}),
        ]
    )

    with (
        _install_scripted_client(client),
        patch(
            "deeptutor.agents.auto.auto_pipeline.get_capability_registry",
            return_value=fake_registry,
        ),
        patch(
            "deeptutor.agents.auto.delegation.get_capability_registry",
            return_value=fake_registry,
        ),
    ):
        task = asyncio.create_task(auto_cap.run(context, bus))
        await asyncio.sleep(0.05)  # let it start
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert slow.cancelled_during_run is True
