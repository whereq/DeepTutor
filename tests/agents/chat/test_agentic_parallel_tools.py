from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from deeptutor.agents.chat.agentic_pipeline import AgenticChatPipeline
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.tool_protocol import ToolResult
from deeptutor.core.trace import build_trace_metadata


async def _collect_bus_events(bus: StreamBus) -> tuple[list[StreamEvent], asyncio.Task[Any]]:
    events: list[StreamEvent] = []

    async def _consume() -> None:
        async for event in bus.subscribe():
            events.append(event)

    consumer = asyncio.create_task(_consume())
    await asyncio.sleep(0)
    return events, consumer  # type: ignore[return-value]

@pytest.mark.asyncio
async def test_execute_tool_call_streams_retrieve_progress_for_rag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
        lambda: SimpleNamespace(
            binding="openai", model="gpt-test", api_key="k", base_url="u", api_version=None
        ),
    )

    class FakeRegistry:
        def get_enabled(self, selected):
            return [SimpleNamespace(name=name) for name in selected]

        async def execute(self, name: str, **kwargs):
            event_sink = kwargs.get("event_sink")
            if event_sink is not None:
                await event_sink(
                    "status", "Selecting provider: llamaindex", {"provider": "llamaindex"}
                )
                await event_sink("status", "Retrieving chunks...", {"mode": "hybrid"})
            return ToolResult(
                content=f"{name} => grounded answer",
                sources=[{"tool": name}],
                metadata={"tool": name},
                success=True,
            )

    registry = FakeRegistry()
    monkeypatch.setattr(
        "deeptutor.agents.chat.agentic_pipeline.get_tool_registry", lambda: registry
    )

    pipeline = AgenticChatPipeline(language="en")
    pipeline.registry = registry

    bus = StreamBus()
    events, consumer = await _collect_bus_events(bus)
    context = UnifiedContext(
        session_id="session-1",
        user_message="what is a transformer",
        enabled_tools=["rag"],
        knowledge_bases=["demo-kb"],
        language="en",
        metadata={"turn_id": "turn-1"},
    )
    trace_meta = build_trace_metadata(
        call_id="chat-react-1",
        phase="acting",
        label="Round 1",
        call_kind="react_round",
        trace_id="chat-react-1",
        trace_role="thought",
        trace_group="react_round",
        round=1,
    )
    retrieve_meta = pipeline._retrieve_trace_metadata(
        trace_meta,
        context=context,
        tool_name="rag",
        tool_args={"query": "transformer model", "kb_name": "demo-kb"},
    )

    result = await pipeline._execute_tool_call(
        "rag",
        {"query": "transformer model", "kb_name": "demo-kb"},
        stream=bus,
        retrieve_meta=retrieve_meta,
    )
    await asyncio.sleep(0)
    await bus.close()
    await consumer

    assert result["success"] is True
    retrieve_events = [
        event
        for event in events
        if event.type == StreamEventType.PROGRESS and event.metadata.get("trace_role") == "retrieve"
    ]
    assert [event.content for event in retrieve_events] == [
        "Query: transformer model",
        "Selecting provider: llamaindex",
        "Retrieving chunks...",
        "Retrieve complete (22 chars)",
    ]


def test_compose_enabled_tools_injects_rag_when_kb_selected() -> None:
    pipeline = AgenticChatPipeline.__new__(AgenticChatPipeline)
    pipeline.registry = SimpleNamespace(
        get_enabled=lambda selected: [SimpleNamespace(name=n) for n in selected]
    )
    context = UnifiedContext(
        user_message="hi",
        enabled_tools=["web_search"],
        knowledge_bases=["kb-a"],
    )
    assert pipeline._compose_enabled_tools(context) == ["web_search", "rag"]


def test_compose_enabled_tools_omits_rag_when_no_kb() -> None:
    pipeline = AgenticChatPipeline.__new__(AgenticChatPipeline)
    pipeline.registry = SimpleNamespace(
        get_enabled=lambda selected: [SimpleNamespace(name=n) for n in selected]
    )
    # Legacy callers may still send "rag" in enabled_tools — it gets stripped.
    context = UnifiedContext(
        user_message="hi",
        enabled_tools=["rag", "web_search"],
        knowledge_bases=[],
    )
    assert pipeline._compose_enabled_tools(context) == ["web_search"]


def test_kb_note_lists_attached_knowledge_bases() -> None:
    pipeline = AgenticChatPipeline.__new__(AgenticChatPipeline)
    pipeline.language = "en"
    context = UnifiedContext(
        user_message="hi",
        enabled_tools=["rag"],
        knowledge_bases=["kb-a", "kb-b"],
    )
    note = pipeline._kb_system_note(context)
    assert "kb-a" in note and "kb-b" in note
    assert "kb_name must" in note


def test_build_llm_tool_schemas_kb_name_enum_matches_attached() -> None:
    pipeline = AgenticChatPipeline.__new__(AgenticChatPipeline)

    class FakeRegistry:
        def build_openai_schemas(self, _enabled_tools):
            return [
                {
                    "type": "function",
                    "function": {
                        "name": "rag",
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
            ]

    pipeline.registry = FakeRegistry()

    context = UnifiedContext(
        user_message="hi",
        enabled_tools=["rag"],
        knowledge_bases=["kb-a", "kb-b"],
    )
    [schema] = pipeline._build_llm_tool_schemas(["rag"], context)
    parameters = schema["function"]["parameters"]
    assert parameters["properties"]["kb_name"]["enum"] == ["kb-a", "kb-b"]
    assert parameters["properties"]["query"].get("minLength") == 1
    assert parameters["required"] == ["query", "kb_name"]
    assert parameters["additionalProperties"] is False

