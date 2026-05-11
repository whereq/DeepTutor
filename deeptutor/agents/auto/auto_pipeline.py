"""Auto pipeline: three-stage agent loop that routes between capabilities.

Stages
------
1. **ANALYZING** — one LLM call (no tools) that acknowledges the user's intent.
   Streamed as THINKING events.
2. **DELEGATING LOOP** — up to ``max_iterations`` iterations. Each iteration:
     * Call the router LLM with capability + atomic tool schemas. Retries on
       transient API/format errors up to ``max_retries_per_step`` (using the
       ``router_llm_retries`` budget). Streams thinking inline.
     * If the LLM returns plain text → that's the final answer, break.
     * If it returns ``tool_call``(s) → dispatch each sequentially:
        - ``delegate_to_<cap>``: validate args, enforce same_cap quota (max
          ``max_same_capability_calls``), run sub-capability with per-step
          retry (``per_delegation_retries`` budget). The error of a failed
          delegation is fed back to the router as the tool result so the loop
          continues.
        - atomic tool name: dispatch via ToolRegistry with kb_name auto-inject.
3. **SYNTHESIZING** — if the loop exited via natural text we emit that.
   Otherwise (loop ran out of iterations) we make one synthesizer LLM call to
   produce a final inline answer from the accumulated trace.

Failure semantics
-----------------
* Three independent retry budgets, all defaulting to 3 (configurable via
  ``AutoRequestConfig.max_retries_per_step``): ``router_llm_retries`` (API/
  network), ``per_delegation_retries`` (sub-capability raise / ERROR event).
  Args-validation errors are NOT counted — the router gets the validation
  message back and self-corrects on the next iteration.
* ``same_cap_calls`` only increments on a successfully completed delegation.
* Cancellation propagates via ``asyncio.CancelledError`` — every awaited
  sub-task lives under ``run()`` so cleanup is automatic.
* ``answer_now`` triggers a fast-path: skip analyzing + delegating and produce
  an immediate inline message.

Conversation-history non-pollution
----------------------------------
Sub-capability events flow through ``delegation.forward_events`` which injects
``metadata.call_id`` on every CONTENT event. The existing
``_should_capture_assistant_content`` filter in turn_runtime drops those.
Auto's own synthesis CONTENT is emitted **without** ``call_id`` (or with
``call_kind="llm_final_response"``) so it alone reaches conversation_history.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
import json
import logging
from typing import Any

import httpx
from openai import APIError, AsyncAzureOpenAI, AsyncOpenAI

from deeptutor.agents.auto.delegation import (
    AtomicToolResult,
    DelegationResult,
    delegate_with_retry,
    execute_atomic_tool,
)
from deeptutor.agents.auto.prompts import (
    analyzer_system_prompt,
    pick_language,
    router_system_prompt,
    synthesizer_system_prompt,
)
from deeptutor.agents.auto.schemas import (
    build_all_tool_schemas,
    extract_capability_name,
    is_delegate_tool,
)
from deeptutor.capabilities._answer_now import extract_answer_now_context
from deeptutor.capabilities.request_contracts import (
    AutoRequestConfig,
    validate_auto_request_config,
    validate_capability_config,
)
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import build_trace_metadata, new_call_id
from deeptutor.runtime.registry.capability_registry import get_capability_registry
from deeptutor.runtime.registry.tool_registry import get_tool_registry
from deeptutor.services.config import load_system_settings
from deeptutor.services.llm import get_llm_config, get_token_limit_kwargs

logger = logging.getLogger(__name__)

ROUTER_MAX_TOKENS = 2000
ANALYZER_MAX_TOKENS = 400
SYNTHESIZER_MAX_TOKENS = 800

_ROUTER_TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (APIError, asyncio.TimeoutError)


# --------------------------------------------------------------------------- #
# Loop state                                                                   #
# --------------------------------------------------------------------------- #


@dataclass
class _LoopState:
    """State carried through the delegating loop.

    Keeping it in a single dataclass makes it easy to test and to pass to the
    synthesizer, and removes the need to thread half a dozen parameters
    through every helper.
    """

    messages: list[dict[str, Any]] = field(default_factory=list)
    same_cap_calls: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    delegations: list[DelegationResult] = field(default_factory=list)
    atomic_results: list[AtomicToolResult] = field(default_factory=list)
    router_llm_retries: int = 0
    iteration: int = 0
    final_text: str | None = None
    terminal_failure_reason: str | None = None

    def increment_iteration(self) -> int:
        self.iteration += 1
        return self.iteration


# --------------------------------------------------------------------------- #
# AutoPipeline                                                                 #
# --------------------------------------------------------------------------- #


class AutoPipeline:
    """Three-stage agent loop for the ``auto`` capability."""

    def __init__(self, language: str = "en") -> None:
        self.language = pick_language(language)
        self.llm_config = get_llm_config()
        self.binding = getattr(self.llm_config, "binding", None) or "openai"
        self.model = getattr(self.llm_config, "model", None)
        self.api_key = getattr(self.llm_config, "api_key", None)
        self.base_url = getattr(self.llm_config, "base_url", None)
        self.api_version = getattr(self.llm_config, "api_version", None)
        self.extra_headers = getattr(self.llm_config, "extra_headers", None) or {}
        self.cap_registry = get_capability_registry()
        self.tool_registry = get_tool_registry()

    # ====================================================================== #
    # Entry point                                                              #
    # ====================================================================== #

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        auto_config = validate_auto_request_config(_strip_runtime_keys(context.config_overrides))

        # Fast-path: user clicked "Answer Now" mid-turn.
        answer_now_payload = extract_answer_now_context(context)
        if answer_now_payload is not None:
            await self._run_answer_now(context, stream, answer_now_payload)
            return

        await self._stage_analyzing(context, stream)
        loop_state = await self._stage_delegating(context, stream, auto_config)
        await self._stage_synthesizing(context, stream, loop_state, auto_config)

    # ====================================================================== #
    # Stage 1: ANALYZING                                                       #
    # ====================================================================== #

    async def _stage_analyzing(self, context: UnifiedContext, stream: StreamBus) -> None:
        trace_meta = build_trace_metadata(
            call_id=new_call_id("auto-analyzing"),
            phase="analyzing",
            label="Analyzing request",
            call_kind="llm_analysis",
            trace_id="auto-analyzing",
            trace_role="auto",
            trace_group="auto_analyzer",
        )
        async with stream.stage("analyzing", source="auto"):
            await stream.progress(
                "Analyzing request",
                source="auto",
                stage="analyzing",
                metadata={**trace_meta, "trace_kind": "call_status", "call_state": "running"},
            )
            messages = [
                {"role": "system", "content": analyzer_system_prompt(self.language)},
                {"role": "user", "content": context.user_message or ""},
            ]
            # ``_call_llm_text`` already streams each delta as a THINKING event
            # so the user sees the analyzer's text live. We deliberately do NOT
            # re-emit a "consolidated" THINKING after the stream — that would
            # double the text in the UI's thought block.
            await self._call_llm_text(
                messages=messages,
                max_tokens=ANALYZER_MAX_TOKENS,
                stream=stream,
                stage="analyzing",
                trace_meta=trace_meta,
            )
            await stream.progress(
                "",
                source="auto",
                stage="analyzing",
                metadata={**trace_meta, "trace_kind": "call_status", "call_state": "complete"},
            )

    # ====================================================================== #
    # Stage 2: DELEGATING LOOP                                                 #
    # ====================================================================== #

    async def _stage_delegating(
        self,
        context: UnifiedContext,
        stream: StreamBus,
        auto_config: AutoRequestConfig,
    ) -> _LoopState:
        state = _LoopState()
        state.messages = self._build_initial_router_messages(context)
        tool_schemas = build_all_tool_schemas(
            self.cap_registry,
            self.tool_registry,
            enabled_capabilities=auto_config.enabled_capabilities or None,
            enabled_tools_hint=context.enabled_tools,
        )

        while state.iteration < auto_config.max_iterations:
            iter_no = state.increment_iteration()
            async with stream.stage(
                "delegating",
                source="auto",
                metadata={"iteration": iter_no},
            ):
                router_outcome = await self._router_call_with_retry(
                    messages=state.messages,
                    tool_schemas=tool_schemas,
                    stream=stream,
                    state=state,
                    max_retries=auto_config.max_retries_per_step,
                    iteration=iter_no,
                )
                if router_outcome.terminal_failure:
                    state.terminal_failure_reason = "router_llm_exhausted"
                    return state

                # Append the assistant turn (whether it had text, tool_calls, or both)
                # so subsequent iterations see the full history.
                state.messages.append(router_outcome.assistant_message)

                if not router_outcome.tool_calls:
                    state.final_text = router_outcome.assistant_text
                    return state

                await self._dispatch_tool_calls(
                    context=context,
                    stream=stream,
                    state=state,
                    tool_calls=router_outcome.tool_calls,
                    auto_config=auto_config,
                )

        return state

    def _build_initial_router_messages(self, context: UnifiedContext) -> list[dict[str, Any]]:
        """Compose the initial system + history + user messages for the router."""
        system_msgs: list[dict[str, Any]] = [
            {"role": "system", "content": router_system_prompt(self.language)},
        ]
        history = list(context.conversation_history or [])
        user_blob = context.user_message or ""
        hints = self._render_context_hints(context)
        if hints:
            user_blob = f"{user_blob}\n\n[available context]\n{hints}"
        return [*system_msgs, *history, {"role": "user", "content": user_blob}]

    def _render_context_hints(self, context: UnifiedContext) -> str:
        parts: list[str] = []
        if context.knowledge_bases:
            parts.append(f"User-selected KB(s): {', '.join(context.knowledge_bases)}")
        if context.enabled_tools:
            parts.append(f"User-selected tool(s): {', '.join(context.enabled_tools)}")
        if context.attachments:
            atts = [f"{a.type}:{a.filename or '(unnamed)'}" for a in context.attachments]
            parts.append(f"Attachments: {', '.join(atts)}")
        return "\n".join(parts)

    # --- Router LLM call with retry on transient errors ------------------- #

    async def _router_call_with_retry(
        self,
        *,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
        stream: StreamBus,
        state: _LoopState,
        max_retries: int,
        iteration: int,
    ) -> _RouterOutcome:
        """Call the router LLM, retrying up to ``max_retries - state.router_llm_retries`` times.

        Retries consume the ``router_llm_retries`` budget. When the budget is
        exhausted we return ``terminal_failure=True`` and the caller bails out
        with a visible ERROR event.
        """
        local_messages = list(messages)
        while True:
            remaining = max_retries - state.router_llm_retries
            if remaining <= 0:
                await stream.error(
                    f"Auto routing failed: router LLM exhausted {max_retries} retries.",
                    source="auto",
                    stage="delegating",
                    metadata={
                        "terminal": True,
                        "failure_reason": "router_llm_exhausted",
                        "iteration": iteration,
                    },
                )
                return _RouterOutcome.terminal_failure_outcome()
            try:
                outcome = await self._router_call_once(
                    messages=local_messages,
                    tool_schemas=tool_schemas,
                    stream=stream,
                    iteration=iteration,
                )
                return outcome
            except asyncio.CancelledError:
                raise
            except _RouterFormatError as exc:
                # The LLM returned something we couldn't parse (bad JSON in
                # tool_call arguments etc). Feed the error back and retry.
                state.router_llm_retries += 1
                await stream.error(
                    f"Router output unparseable: {exc}",
                    source="auto",
                    stage="delegating",
                    metadata={
                        "trace_kind": "router_format_error",
                        "retry_count": state.router_llm_retries,
                        "max_retries": max_retries,
                    },
                )
                local_messages = local_messages + [
                    {
                        "role": "user",
                        "content": (
                            f"Your previous response could not be parsed: {exc}. "
                            "Please try again, ensuring tool call arguments are valid JSON."
                        ),
                    }
                ]
            except _ROUTER_TRANSIENT_EXCEPTIONS as exc:
                state.router_llm_retries += 1
                await stream.error(
                    f"Router LLM error (attempt {state.router_llm_retries}/{max_retries}): {exc}",
                    source="auto",
                    stage="delegating",
                    metadata={
                        "trace_kind": "router_api_error",
                        "retry_count": state.router_llm_retries,
                        "max_retries": max_retries,
                    },
                )
                local_messages = local_messages + [
                    {
                        "role": "user",
                        "content": (
                            f"The previous LLM call failed transiently: {exc}. "
                            "Please retry the same decision."
                        ),
                    }
                ]

    async def _router_call_once(
        self,
        *,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
        stream: StreamBus,
        iteration: int,
    ) -> _RouterOutcome:
        """One non-retrying router LLM call. Streams thinking; parses tool_calls.

        Raises ``_RouterFormatError`` on malformed tool_call arguments so the
        caller can decide to retry.
        """
        trace_meta = build_trace_metadata(
            call_id=new_call_id("auto-routing"),
            phase="delegating",
            label="Auto routing",
            call_kind="tool_planning",
            trace_id="auto-routing",
            trace_role="tool",
            trace_group="auto_routing",
            iteration=iteration,
        )
        await stream.progress(
            "Auto routing",
            source="auto",
            stage="delegating",
            metadata={**trace_meta, "trace_kind": "call_status", "call_state": "running"},
        )

        text, tool_calls_raw = await self._stream_router_completion(
            messages=messages,
            tool_schemas=tool_schemas,
            stream=stream,
            trace_meta=trace_meta,
        )

        await stream.progress(
            "",
            source="auto",
            stage="delegating",
            metadata={**trace_meta, "trace_kind": "call_status", "call_state": "complete"},
        )

        # Parse tool_calls.
        parsed_calls: list[_ParsedToolCall] = []
        for entry in tool_calls_raw:
            name = entry.get("name") or ""
            args_str = entry.get("arguments") or "{}"
            try:
                args = json.loads(args_str) if args_str.strip() else {}
            except json.JSONDecodeError as exc:
                raise _RouterFormatError(
                    f"tool_call '{name}' has invalid JSON arguments: {exc}"
                ) from exc
            if not isinstance(args, dict):
                args = {}
            parsed_calls.append(
                _ParsedToolCall(id=entry.get("id") or "", name=name, args=args, raw_args=args_str)
            )

        # Build the assistant message we'll re-feed in the next iteration.
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": text or None,
        }
        if parsed_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.raw_args},
                }
                for tc in parsed_calls
            ]

        return _RouterOutcome(
            assistant_text=text,
            tool_calls=parsed_calls,
            assistant_message=assistant_message,
        )

    async def _stream_router_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
        stream: StreamBus,
        trace_meta: dict[str, Any],
    ) -> tuple[str, list[dict[str, Any]]]:
        """Make the streaming LLM call and accumulate content + tool_calls.

        Emits each text chunk as a THINKING event so the user sees router
        reasoning live. Tool_call deltas are accumulated silently (streaming
        partial JSON args is noisy and not user-meaningful).
        """
        client = self._build_openai_client()
        api_stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tool_schemas or None,
            tool_choice="auto" if tool_schemas else None,
            stream=True,
            **self._completion_kwargs(ROUTER_MAX_TOKENS),
        )

        content_chunks: list[str] = []
        tool_calls_accum: dict[int, dict[str, str]] = {}

        async for chunk in api_stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if delta is None:
                continue

            delta_content = getattr(delta, "content", None)
            if delta_content:
                content_chunks.append(delta_content)
                await stream.thinking(
                    delta_content,
                    source="auto",
                    stage="delegating",
                    metadata={**trace_meta, "trace_kind": "llm_chunk"},
                )

            delta_tool_calls = getattr(delta, "tool_calls", None) or []
            for tc in delta_tool_calls:
                idx = getattr(tc, "index", 0) or 0
                bucket = tool_calls_accum.setdefault(
                    idx, {"id": "", "name": "", "arguments": ""}
                )
                if getattr(tc, "id", None):
                    bucket["id"] = tc.id
                func = getattr(tc, "function", None)
                if func is not None:
                    if getattr(func, "name", None):
                        bucket["name"] += func.name
                    if getattr(func, "arguments", None):
                        bucket["arguments"] += func.arguments

        full_text = "".join(content_chunks).strip()
        tool_calls_ordered = [tool_calls_accum[idx] for idx in sorted(tool_calls_accum.keys())]
        return full_text, tool_calls_ordered

    # --- Tool-call dispatch ----------------------------------------------- #

    async def _dispatch_tool_calls(
        self,
        *,
        context: UnifiedContext,
        stream: StreamBus,
        state: _LoopState,
        tool_calls: list[_ParsedToolCall],
        auto_config: AutoRequestConfig,
    ) -> None:
        for call in tool_calls:
            tool_message = await self._handle_one_tool_call(
                context=context,
                stream=stream,
                state=state,
                call=call,
                auto_config=auto_config,
            )
            state.messages.append(tool_message)

    async def _handle_one_tool_call(
        self,
        *,
        context: UnifiedContext,
        stream: StreamBus,
        state: _LoopState,
        call: _ParsedToolCall,
        auto_config: AutoRequestConfig,
    ) -> dict[str, Any]:
        """Dispatch a single tool_call. Returns the OpenAI ``role=tool`` reply message."""
        if is_delegate_tool(call.name):
            cap_name = extract_capability_name(call.name) or ""
            return await self._handle_capability_delegation(
                context=context,
                stream=stream,
                state=state,
                call=call,
                cap_name=cap_name,
                auto_config=auto_config,
            )
        # Atomic tool path.
        result = await execute_atomic_tool(
            tool_name=call.name,
            raw_args=call.args,
            parent_context=context,
            parent_stream=stream,
            tool_registry=self.tool_registry,
        )
        state.atomic_results.append(result)
        if result.succeeded:
            payload = result.content or "(empty result)"
        else:
            payload = f"Atomic tool {call.name} failed: {result.error_message}"
        return {
            "role": "tool",
            "tool_call_id": call.id,
            "name": call.name,
            "content": payload,
        }

    async def _handle_capability_delegation(
        self,
        *,
        context: UnifiedContext,
        stream: StreamBus,
        state: _LoopState,
        call: _ParsedToolCall,
        cap_name: str,
        auto_config: AutoRequestConfig,
    ) -> dict[str, Any]:
        """Validate args, enforce quotas, run sub-cap with retry. Returns tool-role message."""
        # Same-capability quota: only counts successful completions.
        if state.same_cap_calls[cap_name] >= auto_config.max_same_capability_calls:
            payload = (
                f"Cannot call {cap_name} again — already used "
                f"{auto_config.max_same_capability_calls}/"
                f"{auto_config.max_same_capability_calls} allowed times. "
                "Choose a different capability or finalize a text answer."
            )
            await stream.error(
                payload,
                source="auto",
                stage="delegating",
                metadata={
                    "trace_kind": "same_cap_exhausted",
                    "delegated_capability": cap_name,
                },
            )
            return {"role": "tool", "tool_call_id": call.id, "name": call.name, "content": payload}

        # Args validation: NOT counted against per_delegation_retries; the
        # router sees the error and self-corrects.
        config_payload = call.args.get("config") if isinstance(call.args.get("config"), dict) else {}
        try:
            validated_config = validate_capability_config(cap_name, config_payload)
        except ValueError as exc:
            await stream.error(
                f"Invalid args for {cap_name}: {exc}",
                source="auto",
                stage="delegating",
                metadata={
                    "trace_kind": "validation_error",
                    "delegated_capability": cap_name,
                },
            )
            payload = (
                f"Invalid args for {cap_name}: {exc}. "
                "Re-issue the call with corrected arguments."
            )
            return {"role": "tool", "tool_call_id": call.id, "name": call.name, "content": payload}

        # Allow the LLM to override per-delegation tool/KB scope.
        enabled_tools_override = _coerce_str_list(call.args.get("enabled_tools"))
        kbs_override = _coerce_str_list(call.args.get("knowledge_bases"))

        result = await delegate_with_retry(
            cap_name=cap_name,
            config=validated_config,
            parent_context=context,
            parent_stream=stream,
            max_retries=auto_config.max_retries_per_step,
            enabled_tools=enabled_tools_override,
            knowledge_bases=kbs_override,
        )
        state.delegations.append(result)
        # Count BOTH successes and failures toward the same-cap quota.
        # Otherwise a buggy capability can be retried indefinitely by the
        # router (each "retry" being a fresh router decision that costs
        # latency / tokens / sub-cap attempts).
        state.same_cap_calls[cap_name] += 1
        if result.succeeded:
            summary = _summarize_delegation_success(cap_name, result)
        else:
            summary = (
                f"Sub-capability {cap_name} failed after {auto_config.max_retries_per_step} "
                f"retries: {result.error_message or 'unknown error'}. "
                "Pick a different capability or finalize a text answer."
            )
        return {"role": "tool", "tool_call_id": call.id, "name": call.name, "content": summary}

    # ====================================================================== #
    # Stage 3: SYNTHESIZING                                                    #
    # ====================================================================== #

    async def _stage_synthesizing(
        self,
        context: UnifiedContext,
        stream: StreamBus,
        state: _LoopState,
        auto_config: AutoRequestConfig,
    ) -> None:
        trace_meta = build_trace_metadata(
            call_id=new_call_id("auto-synthesizing"),
            phase="synthesizing",
            label="Final synthesis",
            call_kind="llm_final_response",
            trace_id="auto-synthesizing",
            trace_role="auto",
            trace_group="auto_synthesizer",
        )
        async with stream.stage("synthesizing", source="auto"):
            if state.terminal_failure_reason:
                # Don't make another LLM call after a terminal failure; emit a
                # short factual message + result envelope.
                fail_text = self._terminal_failure_text(state.terminal_failure_reason)
                await stream.content(
                    fail_text,
                    source="auto",
                    stage="synthesizing",
                    metadata={"call_kind": "llm_final_response"},
                )
                await stream.result(
                    {
                        "response": fail_text,
                        "auto_summary": _build_auto_summary(state),
                    },
                    source="auto",
                )
                return

            if state.final_text is not None and state.final_text.strip():
                # The router gave us a finished text reply; use it verbatim.
                text = state.final_text.strip()
            else:
                # Loop ran out of iterations or only made tool calls. Compose
                # one final synthesis from the trace.
                text = await self._call_llm_text(
                    messages=[
                        {"role": "system", "content": synthesizer_system_prompt(self.language)},
                        {
                            "role": "user",
                            "content": _render_synthesizer_user_blob(context, state),
                        },
                    ],
                    max_tokens=SYNTHESIZER_MAX_TOKENS,
                    stream=stream,
                    stage="synthesizing",
                    trace_meta=trace_meta,
                )
                if not text:
                    text = self._fallback_text(state)

            await stream.content(
                text,
                source="auto",
                stage="synthesizing",
                metadata={"call_kind": "llm_final_response"},
            )
            await stream.result(
                {
                    "response": text,
                    "auto_summary": _build_auto_summary(state),
                },
                source="auto",
            )

    def _terminal_failure_text(self, reason: str) -> str:
        if self.language == "zh":
            return (
                "Auto 路由失败，已经多次重试仍未恢复。"
                "建议切到 Manual 模式手动选择 capability，或重试当前消息。"
            )
        return (
            "Auto routing failed after exhausting retries. "
            "Switch to Manual mode and pick a capability, or try the message again."
        )

    def _fallback_text(self, state: _LoopState) -> str:
        if not state.delegations and not state.atomic_results:
            return self._t(
                en="I couldn't decide on a tool to use. Try rephrasing the question.",
                zh="无法判断该用哪个工具。请尝试换个说法。",
            )
        bits: list[str] = []
        for d in state.delegations:
            if d.succeeded:
                bits.append(f"`{d.capability}` ran successfully")
            else:
                bits.append(f"`{d.capability}` failed")
        if state.atomic_results:
            bits.append(f"{len(state.atomic_results)} atomic tool call(s) ran")
        joined = "; ".join(bits)
        return self._t(
            en=f"Done: {joined}.",
            zh=f"已完成：{joined}。",
        )

    # ====================================================================== #
    # Answer Now fast-path                                                     #
    # ====================================================================== #

    async def _run_answer_now(
        self,
        context: UnifiedContext,
        stream: StreamBus,
        payload: dict[str, Any],
    ) -> None:
        """Fast-path when the user clicks 'Answer Now' mid-turn.

        We don't try to re-run any sub-capabilities — just emit a brief inline
        message based on whatever the frontend already has. The cancelled
        sub-task in the previous attempt (if any) will be GC'd; this turn is
        independent.
        """
        async with stream.stage(
            "synthesizing",
            source="auto",
            metadata={"trace_kind": "auto_answer_now"},
        ):
            original = str(payload.get("original_user_message") or "").strip()
            partial = str(payload.get("partial_response") or "").strip()
            text = self._answer_now_text(original=original, partial=partial)
            await stream.content(
                text,
                source="auto",
                stage="synthesizing",
                metadata={"call_kind": "llm_final_response", "answer_now": True},
            )
            await stream.result(
                {
                    "response": text,
                    "metadata": {"answer_now": True},
                    "auto_summary": {
                        "iterations": 0,
                        "delegations": [],
                        "router_retries": 0,
                        "terminal_failure_reason": None,
                        "final_path": "answer_now",
                    },
                },
                source="auto",
            )

    def _answer_now_text(self, *, original: str, partial: str) -> str:
        if partial:
            return self._t(
                en=(
                    f"You requested an immediate answer. Here's what I have so far based on "
                    f"the partial trace: {partial}"
                ),
                zh=f"已根据当前进度生成回答：{partial}",
            )
        if self.language == "zh":
            return (
                "已停止 Auto 路由。请切到 Manual 模式直接选择 capability "
                "或重新发送消息以获得更完整的结果。"
            )
        return (
            "Auto routing was interrupted before any result was produced. Switch to Manual "
            "and pick a capability, or resend the message for a fresh attempt."
        )

    # ====================================================================== #
    # LLM plumbing                                                             #
    # ====================================================================== #

    async def _call_llm_text(
        self,
        *,
        messages: list[dict[str, Any]],
        max_tokens: int,
        stream: StreamBus,
        stage: str,
        trace_meta: dict[str, Any],
    ) -> str:
        """Streaming LLM call with no tools. Emits THINKING chunks; returns full text."""
        client = self._build_openai_client()
        api_stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **self._completion_kwargs(max_tokens),
        )
        chunks: list[str] = []
        async for chunk in api_stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if delta is None:
                continue
            delta_content = getattr(delta, "content", None)
            if delta_content:
                chunks.append(delta_content)
                await stream.thinking(
                    delta_content,
                    source="auto",
                    stage=stage,
                    metadata={**trace_meta, "trace_kind": "llm_chunk"},
                )
        return "".join(chunks).strip()

    def _build_openai_client(self):
        http_client = None
        if load_system_settings()["disable_ssl_verify"]:
            http_client = httpx.AsyncClient(verify=False)  # nosec B501

        default_headers = self.extra_headers or None
        if self.binding == "azure_openai" or (self.binding == "openai" and self.api_version):
            return AsyncAzureOpenAI(
                api_key=self.api_key or "sk-no-key-required",
                azure_endpoint=self.base_url,
                api_version=self.api_version,
                http_client=http_client,
                default_headers=default_headers,
            )
        return AsyncOpenAI(
            api_key=self.api_key or "sk-no-key-required",
            base_url=self.base_url or None,
            http_client=http_client,
            default_headers=default_headers,
        )

    def _completion_kwargs(self, max_tokens: int) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"temperature": 0.2}
        if self.model:
            kwargs.update(get_token_limit_kwargs(self.model, max_tokens))
        return kwargs

    def _t(self, *, en: str, zh: str) -> str:
        return zh if self.language == "zh" else en


# --------------------------------------------------------------------------- #
# Module-level helpers                                                         #
# --------------------------------------------------------------------------- #


class _RouterFormatError(Exception):
    """Raised when the router LLM emits a tool_call we can't parse."""


@dataclass
class _ParsedToolCall:
    id: str
    name: str
    args: dict[str, Any]
    raw_args: str


@dataclass
class _RouterOutcome:
    assistant_text: str = ""
    tool_calls: list[_ParsedToolCall] = field(default_factory=list)
    assistant_message: dict[str, Any] = field(default_factory=dict)
    terminal_failure: bool = False

    @classmethod
    def terminal_failure_outcome(cls) -> _RouterOutcome:
        return cls(terminal_failure=True)


def _coerce_str_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        out = [str(v) for v in value if isinstance(v, (str, int)) and str(v)]
        return out or None
    return None


def _strip_runtime_keys(config_overrides: dict[str, Any] | None) -> dict[str, Any]:
    """Strip keys that belong on the runtime side, not on AutoRequestConfig itself."""
    if not isinstance(config_overrides, dict):
        return {}
    cleaned = dict(config_overrides)
    cleaned.pop("answer_now_context", None)
    return cleaned


def _summarize_delegation_success(cap_name: str, result: DelegationResult) -> str:
    """Compact summary fed to the router as the tool-role result."""
    meta = result.result_metadata or {}
    response_snippet = str(meta.get("response") or "").strip()
    if response_snippet:
        clipped = response_snippet[:600] + ("..." if len(response_snippet) > 600 else "")
        return (
            f"`{cap_name}` completed successfully. Result preview: {clipped}. "
            "The user can see the full output above; you do not need to repeat it."
        )
    return f"`{cap_name}` completed successfully."


def _render_synthesizer_user_blob(context: UnifiedContext, state: _LoopState) -> str:
    """Compose the user-message blob for the synthesizer LLM call."""
    parts: list[str] = []
    parts.append(f"Original request: {context.user_message or ''}")
    if state.delegations:
        lines = []
        for d in state.delegations:
            status = "OK" if d.succeeded else f"FAIL ({d.error_message})"
            lines.append(f"- {d.capability}: {status}")
        parts.append("Capability calls:\n" + "\n".join(lines))
    if state.atomic_results:
        lines = []
        for r in state.atomic_results:
            status = "OK" if r.succeeded else f"FAIL ({r.error_message})"
            lines.append(f"- {r.tool_name}: {status}")
        parts.append("Atomic tool calls:\n" + "\n".join(lines))
    if state.iteration:
        parts.append(f"Iterations used: {state.iteration}")
    return "\n\n".join(parts)


def _build_auto_summary(state: _LoopState) -> dict[str, Any]:
    """Telemetry payload attached to the final RESULT event.

    Stable shape — frontend / analytics consumers depend on these keys.
    """
    final_path: str
    if state.terminal_failure_reason:
        final_path = "terminal_error"
    elif state.final_text is not None:
        final_path = "text_response"
    else:
        final_path = "synthesis"
    return {
        "iterations": state.iteration,
        "delegations": [
            {
                "capability": d.capability,
                "attempts": d.attempt,
                "succeeded": d.succeeded,
                "error": d.error_message,
            }
            for d in state.delegations
        ],
        "atomic_calls": [
            {
                "tool": r.tool_name,
                "succeeded": r.succeeded,
                "error": r.error_message,
            }
            for r in state.atomic_results
        ],
        "router_retries": state.router_llm_retries,
        "terminal_failure_reason": state.terminal_failure_reason,
        "final_path": final_path,
    }
