"""Sub-capability delegation + atomic tool dispatch for the Auto pipeline.

The Auto pipeline is the first place in the codebase where one capability
invokes another in-process. All complexity of (1) constructing a child
``UnifiedContext``, (2) running the sub-capability against a child
``StreamBus``, (3) forwarding child events to the parent stream with proper
metadata, and (4) retrying transient failures lives here.

Conversation-history non-pollution invariant: every CONTENT event forwarded
from a sub-capability gets ``metadata.call_id`` injected (if absent) so the
existing ``_should_capture_assistant_content`` filter in turn_runtime drops it
from persisted assistant content. Auto's own final synthesis emits CONTENT
without ``call_id`` (or with ``call_kind="llm_final_response"``), so it alone
reaches conversation_history.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field, replace
import logging
from typing import Any

from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream import StreamEvent, StreamEventType
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import merge_trace_metadata, new_call_id
from deeptutor.runtime.registry.capability_registry import get_capability_registry
from deeptutor.runtime.registry.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Result types                                                                 #
# --------------------------------------------------------------------------- #


@dataclass
class DelegationResult:
    """Outcome of a single sub-capability invocation."""

    capability: str
    delegation_call_id: str
    attempt: int
    succeeded: bool
    error_message: str | None = None
    # Last RESULT event metadata emitted by the sub-capability, if any.
    # The router consumes this as the "observation" of what happened.
    result_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AtomicToolResult:
    """Outcome of executing an atomic tool via ToolRegistry."""

    tool_name: str
    succeeded: bool
    content: str = ""
    error_message: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Child-context construction                                                   #
# --------------------------------------------------------------------------- #


def build_child_context(
    parent: UnifiedContext,
    *,
    cap_name: str,
    config: dict[str, Any],
    delegation_call_id: str,
    enabled_tools: list[str] | None = None,
    knowledge_bases: list[str] | None = None,
) -> UnifiedContext:
    """Derive an immutable child context for a sub-capability invocation.

    Uses ``dataclasses.replace`` so the parent context is never mutated. Adds
    ``is_sub_invocation`` and ``parent_delegation_call_id`` to ``metadata`` so
    sub-capabilities can recognize they're being invoked by Auto.
    """
    child_metadata = {
        **(parent.metadata or {}),
        "is_sub_invocation": True,
        "parent_delegation_call_id": delegation_call_id,
    }
    return replace(
        parent,
        active_capability=cap_name,
        config_overrides=dict(config or {}),
        enabled_tools=(
            list(enabled_tools)
            if enabled_tools is not None
            else (list(parent.enabled_tools) if parent.enabled_tools is not None else None)
        ),
        knowledge_bases=(
            list(knowledge_bases) if knowledge_bases else list(parent.knowledge_bases or [])
        ),
        metadata=child_metadata,
    )


# --------------------------------------------------------------------------- #
# Event forwarding                                                             #
# --------------------------------------------------------------------------- #


async def _forward_one(
    event: StreamEvent,
    parent_stream: StreamBus,
    *,
    cap_name: str,
    delegation_call_id: str,
    attempt: int,
) -> None:
    injected: dict[str, Any] = {
        "parent_call_id": delegation_call_id,
        "delegated_capability": cap_name,
        "delegated_from": "auto",
        "delegation_attempt": attempt,
    }
    # CONTENT events without call_id would pollute conversation_history. Inject
    # one so turn_runtime's _should_capture_assistant_content filter drops them.
    if event.type == StreamEventType.CONTENT:
        existing_meta = event.metadata or {}
        if not existing_meta.get("call_id"):
            injected["call_id"] = delegation_call_id

    merged = merge_trace_metadata(event.metadata, injected)
    await parent_stream.emit(
        StreamEvent(
            type=event.type,
            source=event.source or cap_name,
            stage=event.stage,
            content=event.content,
            metadata=merged,
            session_id=event.session_id,
            turn_id=event.turn_id,
            seq=event.seq,
            timestamp=event.timestamp,
        )
    )


# --------------------------------------------------------------------------- #
# Single-attempt capability delegation                                         #
# --------------------------------------------------------------------------- #


async def _run_one_attempt(
    *,
    cap_name: str,
    config: dict[str, Any],
    parent_context: UnifiedContext,
    parent_stream: StreamBus,
    enabled_tools: list[str] | None = None,
    knowledge_bases: list[str] | None = None,
    attempt: int = 1,
) -> DelegationResult:
    """Run a sub-capability once and forward its events.

    No retry. Caller decides whether to call again on failure. Always returns
    a DelegationResult; never raises on sub-capability error (except for
    ``CancelledError``, which propagates).
    """
    delegation_call_id = new_call_id("auto-delegation")
    registry = get_capability_registry()
    capability = registry.get(cap_name)
    if capability is None:
        await parent_stream.error(
            f"Unknown capability for auto delegation: {cap_name}",
            source="auto",
            stage="delegating",
            metadata={
                "delegated_capability": cap_name,
                "delegation_call_id": delegation_call_id,
                "delegation_attempt": attempt,
            },
        )
        return DelegationResult(
            capability=cap_name,
            delegation_call_id=delegation_call_id,
            attempt=attempt,
            succeeded=False,
            error_message=f"unknown_capability: {cap_name}",
        )

    child_context = build_child_context(
        parent_context,
        cap_name=cap_name,
        config=config,
        delegation_call_id=delegation_call_id,
        enabled_tools=enabled_tools,
        knowledge_bases=knowledge_bases,
    )
    child_bus = StreamBus()

    async def _runner() -> Exception | None:
        try:
            await capability.run(child_context, child_bus)
            return None
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 -- we report the error verbatim
            logger.exception("Auto delegation to %s raised", cap_name)
            return exc
        finally:
            await child_bus.close()

    last_result_metadata: dict[str, Any] = {}
    saw_error_event = False

    async def _forwarder() -> None:
        nonlocal last_result_metadata, saw_error_event
        async for event in child_bus.subscribe():
            if event.type == StreamEventType.RESULT:
                last_result_metadata = dict(event.metadata or {})
            elif event.type == StreamEventType.ERROR:
                saw_error_event = True
            await _forward_one(
                event,
                parent_stream,
                cap_name=cap_name,
                delegation_call_id=delegation_call_id,
                attempt=attempt,
            )

    runner_task = asyncio.create_task(_runner())
    forwarder_task = asyncio.create_task(_forwarder())
    runner_exc, _ = await asyncio.gather(runner_task, forwarder_task)

    if runner_exc is not None:
        return DelegationResult(
            capability=cap_name,
            delegation_call_id=delegation_call_id,
            attempt=attempt,
            succeeded=False,
            error_message=f"{type(runner_exc).__name__}: {runner_exc}",
            result_metadata=last_result_metadata,
        )
    if saw_error_event:
        return DelegationResult(
            capability=cap_name,
            delegation_call_id=delegation_call_id,
            attempt=attempt,
            succeeded=False,
            error_message="sub_capability_emitted_error",
            result_metadata=last_result_metadata,
        )
    return DelegationResult(
        capability=cap_name,
        delegation_call_id=delegation_call_id,
        attempt=attempt,
        succeeded=True,
        result_metadata=last_result_metadata,
    )


# Public alias for callers who only want one attempt (e.g. PR 1 tests).
delegate_to_capability = _run_one_attempt


async def delegate_with_retry(
    *,
    cap_name: str,
    config: dict[str, Any],
    parent_context: UnifiedContext,
    parent_stream: StreamBus,
    max_retries: int = 3,
    enabled_tools: list[str] | None = None,
    knowledge_bases: list[str] | None = None,
) -> DelegationResult:
    """Run a sub-capability with up to ``max_retries`` attempts.

    Attempts are numbered 1..max_retries. Between attempts we emit a visible
    retry-marker ERROR event so the frontend can render a "Retry K/N" badge.
    Returns the final DelegationResult (success on first ok attempt, or the
    last failure if all attempts fail). Never raises except on cancellation.
    """
    last: DelegationResult | None = None
    for attempt in range(1, max_retries + 1):
        result = await _run_one_attempt(
            cap_name=cap_name,
            config=config,
            parent_context=parent_context,
            parent_stream=parent_stream,
            enabled_tools=enabled_tools,
            knowledge_bases=knowledge_bases,
            attempt=attempt,
        )
        last = result
        if result.succeeded:
            return result
        # Failure: emit a retry-marker so the UI can render "🔄 Retry K/N".
        # Only emit when more attempts remain.
        if attempt < max_retries:
            await parent_stream.error(
                f"{cap_name} attempt {attempt}/{max_retries} failed: "
                f"{result.error_message or 'unknown error'}",
                source="auto",
                stage="delegating",
                metadata={
                    "delegated_capability": cap_name,
                    "delegation_call_id": result.delegation_call_id,
                    "retry_count": attempt,
                    "max_retries": max_retries,
                    "trace_kind": "delegation_retry",
                },
            )
    # ``last`` is guaranteed non-None because max_retries >= 1.
    assert last is not None
    return last


# --------------------------------------------------------------------------- #
# Atomic tool dispatch                                                         #
# --------------------------------------------------------------------------- #


def _augment_atomic_args(
    tool_name: str,
    args: dict[str, Any],
    parent_context: UnifiedContext,
) -> dict[str, Any]:
    """Inject trusted UI/session values that the LLM does not see.

    Currently only RAG: ``kb_name`` is a server-side value chosen by the user,
    not an LLM argument. Mirrors AgenticChatPipeline's _augment_tool_kwargs.
    """
    augmented = dict(args or {})
    if tool_name == "rag":
        if parent_context.knowledge_bases:
            augmented.setdefault("kb_name", parent_context.knowledge_bases[0])
    return augmented


async def execute_atomic_tool(
    tool_name: str,
    raw_args: dict[str, Any],
    parent_context: UnifiedContext,
    parent_stream: StreamBus,
    tool_registry: ToolRegistry,
    *,
    call_id: str | None = None,
) -> AtomicToolResult:
    """Execute one atomic tool and emit corresponding stream events.

    The router LLM calls these by name (e.g. ``rag``, ``web_search``). On
    failure we return a structured result instead of raising — the caller
    feeds the error back to the router as a tool message so it can recover.
    """
    call_id = call_id or new_call_id("auto-atomic")
    metadata_base = {
        "delegated_from": "auto",
        "call_id": call_id,
        "tool_kind": "atomic",
    }

    await parent_stream.tool_call(
        tool_name=tool_name,
        args=raw_args,
        source="auto",
        stage="delegating",
        metadata=metadata_base,
    )

    augmented = _augment_atomic_args(tool_name, raw_args, parent_context)
    try:
        result = await tool_registry.execute(tool_name, **augmented)
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Atomic tool %s raised", tool_name)
        await parent_stream.error(
            f"Atomic tool {tool_name} failed: {exc}",
            source="auto",
            stage="delegating",
            metadata={**metadata_base, "trace_kind": "atomic_tool_error"},
        )
        return AtomicToolResult(
            tool_name=tool_name,
            succeeded=False,
            error_message=f"{type(exc).__name__}: {exc}",
        )

    success = bool(getattr(result, "success", True))
    content = str(getattr(result, "content", "") or "")
    sources = list(getattr(result, "sources", []) or [])
    meta = dict(getattr(result, "metadata", {}) or {})

    await parent_stream.tool_result(
        tool_name=tool_name,
        result=content,
        source="auto",
        stage="delegating",
        metadata={**metadata_base, "success": success},
    )
    return AtomicToolResult(
        tool_name=tool_name,
        succeeded=success,
        content=content,
        error_message=None if success else "tool_reported_failure",
        sources=sources,
        metadata=meta,
    )
