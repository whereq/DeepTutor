"""Single-loop agentic chat pipeline.

The chat capability used to run four sequential LLM calls (thinking → acting
→ observing → responding) regardless of question complexity. Simple questions
paid for three unnecessary calls; complex questions couldn't iterate because
``acting`` was a single-shot tool call.

This module replaces that with one iterative LLM loop. Each iteration:

* Streams an LLM call (with native tool schemas attached when applicable).
* If the model emitted tool calls, dispatches them, appends the tool
  messages, and continues to the next iteration.
* Otherwise the iteration's text is the final answer and the loop exits.

The chat-only ``read_source`` tool is auto-included whenever the turn has a
non-empty ``source_manifest`` (the manifest itself is appended to the
system prompt by :py:meth:`_build_system_prompt`). The per-turn
``{source_id: full_text}`` map flows in via ``context.metadata['source_index']``.

History compression (branch-safe) is handled upstream by
``ContextBuilder.build`` so it does not appear here.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx
from openai import AsyncAzureOpenAI, AsyncOpenAI

from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import (
    build_trace_metadata,
    derive_trace_metadata,
    merge_trace_metadata,
    new_call_id,
)
from deeptutor.runtime.registry.tool_registry import get_tool_registry
from deeptutor.services.config import get_chat_params, load_system_settings
from deeptutor.services.llm import (
    clean_thinking_tags,
    get_llm_config,
    get_token_limit_kwargs,
    prepare_multimodal_messages,
    supports_tools,
)
from deeptutor.services.llm import (
    stream as llm_stream,
)
from deeptutor.services.llm.context_window import resolve_effective_context_window
from deeptutor.services.prompt import get_prompt_manager
from deeptutor.services.prompt.language import append_language_directive
from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES
from deeptutor.utils.json_parser import parse_json_response

logger = logging.getLogger(__name__)

CHAT_EXCLUDED_TOOLS = {"geogebra_analysis"}
# Optional tools the user can toggle from the composer. ``read_source`` is
# intentionally excluded — it is auto-enabled by the pipeline when sources
# are attached and is invisible in the frontend tool list.
CHAT_OPTIONAL_TOOLS = [
    name
    for name in BUILTIN_TOOL_NAMES
    if name not in CHAT_EXCLUDED_TOOLS and name != "read_source"
]
MAX_PARALLEL_TOOL_CALLS = 8
MAX_TOOL_RESULT_CHARS = 4000
# Tool-iteration ceiling: small enough to prevent runaway loops, large
# enough for genuinely multi-step retrieval. The default mirrors common
# agent-framework defaults and is overridable via capabilities.chat.max_iterations.
DEFAULT_MAX_ITERATIONS = 8
# When messages exceed this fraction of the model's effective context
# window, the in-turn guard replaces the largest stale tool-result with a
# snip marker. Keeps headroom for the next LLM call without aborting.
CONTEXT_WINDOW_GUARD_RATIO = 0.9
TOOL_RESULT_SNIP_MARKER = (
    "[earlier tool result snipped to stay within context window — "
    "call the same tool again if the content is still needed]"
)

# Output protocol labels. The system prompt instructs the model to emit
# exactly one of these as the FIRST line of every reply, wrapped in two
# backticks each side, e.g. ``FINISH``. The pipeline parses this label
# upfront and routes the rest of the stream accordingly:
#   FINISH → content events go straight to the answer body (llm_final_response)
#   TOOL   → reply will use native tool_calls; prose goes to a reasoning sub-trace
#   THINK  → intermediate reasoning only, no tools; loop continues; prose goes to a sub-trace
# UNKNOWN is the parser's fallback when no valid label is detected within
# LABEL_PROBE_MAX_CHARS — the pipeline then uses the legacy absorb-into-final
# mechanism based on whether tool_calls came in.
LABEL_FINISH = "FINISH"
LABEL_TOOL = "TOOL"
LABEL_THINK = "THINK"
LABEL_UNKNOWN = "UNKNOWN"
LABEL_OPTIONS: tuple[str, ...] = (LABEL_FINISH, LABEL_TOOL, LABEL_THINK)
LABEL_PROBE_MAX_CHARS = 64


def _classify_label(buffer: str) -> tuple[str, str] | None:
    r"""Inspect a content buffer for a protocol label at the start.

    Returns ``(label, after_text)`` once a valid ``\`\`FINISH\`\```/
    ``\`\`TOOL\`\```/``\`\`THINK\`\``` prefix is detected (after any leading
    whitespace) — caller routes ``after_text`` and all subsequent chunks
    accordingly.

    Returns ``None`` while the buffer is too short or still a partial prefix
    match. Caller keeps buffering and tries again on the next chunk. The
    caller is responsible for falling back to ``LABEL_UNKNOWN`` once
    ``len(buffer) > LABEL_PROBE_MAX_CHARS``.
    """
    stripped = buffer.lstrip()
    for label in LABEL_OPTIONS:
        prefix = f"``{label}``"
        if stripped.startswith(prefix):
            after = stripped[len(prefix):]
            # Eat the single separating newline / spaces after the label so
            # the answer body / reasoning text doesn't start with stray
            # blank lines.
            return label, after.lstrip("\n\r ")
    # Could still match — return None to keep buffering.
    return None


class AgenticChatPipeline:
    """Run chat as a single iterative LLM loop with native tool calling."""

    def __init__(self, language: str = "en") -> None:
        self.language = "zh" if language.lower().startswith("zh") else "en"
        self.llm_config = get_llm_config()
        self.binding = getattr(self.llm_config, "binding", None) or "openai"
        self.model = getattr(self.llm_config, "model", None)
        self.api_key = getattr(self.llm_config, "api_key", None)
        self.base_url = getattr(self.llm_config, "base_url", None)
        self.api_version = getattr(self.llm_config, "api_version", None)
        self.extra_headers = getattr(self.llm_config, "extra_headers", None) or {}
        self.registry = get_tool_registry()
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0}

        try:
            chat_cfg = get_chat_params()
        except Exception as exc:
            logger.warning("Failed to load chat params, using defaults: %s", exc)
            chat_cfg = {}
        try:
            self._chat_temperature = float(chat_cfg.get("temperature", 0.2))
        except (TypeError, ValueError):
            self._chat_temperature = 0.2
        # Token budgets for the two LLM call shapes used by this pipeline.
        # ``responding`` caps each loop iteration; ``answer_now`` caps the
        # single-shot fallback when the user clicks "Answer now" mid-stream.
        self._responding_max_tokens = _read_int(
            chat_cfg.get("responding"), key="max_tokens", default=8000
        )
        self._answer_now_max_tokens = _read_int(
            chat_cfg.get("answer_now"), key="max_tokens", default=8000
        )
        self._max_iterations = _read_int(
            chat_cfg, key="max_iterations", default=DEFAULT_MAX_ITERATIONS
        )

        try:
            self._prompts: dict[str, Any] = (
                get_prompt_manager().load_prompts(
                    module_name="chat",
                    agent_name="agentic_chat",
                    language=self.language,
                )
                or {}
            )
        except Exception as exc:
            logger.warning("Failed to load agentic_chat prompts: %s", exc)
            self._prompts = {}

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        answer_now_context = self._extract_answer_now_context(context)
        if answer_now_context is not None:
            await self._run_answer_now(context, answer_now_context, stream)
            return

        enabled_tools = self._compose_enabled_tools(context)
        use_native_tools = bool(enabled_tools) and self._can_use_native_tool_calling()
        tool_schemas = (
            self._build_llm_tool_schemas(enabled_tools, context)
            if use_native_tools
            else None
        )

        system_prompt = self._build_system_prompt(enabled_tools, context)
        user_content = self._t(
            "user_template",
            default=context.user_message,
            user_message=context.user_message,
        )
        messages = self._build_messages(
            context=context,
            system_prompt=system_prompt,
            user_content=user_content,
        )
        messages, images_stripped = self._prepare_messages_with_attachments(messages, context)

        if images_stripped:
            # ``images_stripped`` is a transient warning, not a sub-trace, so
            # it carries no call_id (frontend ``CallTracePanel`` groups by
            # call_id and would otherwise spawn an empty sub-trace row).
            await stream.thinking(
                self._t("notices.images_stripped", model=self.model or ""),
                source="chat",
                stage="responding",
                metadata={"trace_kind": "warning"},
            )

        aggregated_sources: list[dict[str, Any]] = []
        final_text = ""
        max_iter = max(1, self._max_iterations)
        completed = False
        iteration = 0
        # Outer ``stage("responding")`` only drives the frontend's
        # ``currentStage`` indicator ("DeepTutor responding…"). It carries no
        # call_id so it does NOT spawn its own sub-trace; each LLM iteration
        # and each tool call below allocate their own call_id and surface as
        # individual sub-traces in CallTracePanel.
        async with stream.stage("responding", source="chat"):
            for iteration in range(max_iter):
                await self._guard_context_window(messages, stream)

                # Per-iter sub-trace identity. Created up front but ONLY
                # opened by ``_stream_one_iteration`` when the resolved
                # label is THINK / TOOL / UNKNOWN. A FINISH iter never
                # opens it, so no empty sub-trace appears in the trace box.
                iter_call_id = new_call_id(f"chat-iter-{iteration}")
                iter_meta = build_trace_metadata(
                    call_id=iter_call_id,
                    phase="responding",
                    label=self._t("labels.reasoning", default="Reasoning"),
                    call_kind="llm_reasoning",
                    trace_id=iter_call_id,
                    trace_role="thought",
                    trace_group="stage",
                )
                # Fresh final-response trace id per iter — FINISH path uses
                # it to scope the body content events; intermediate iters
                # never touch it.
                final_call_id = new_call_id("chat-final-response")
                final_meta = build_trace_metadata(
                    call_id=final_call_id,
                    phase="responding",
                    label=self._t("labels.final_response", default="Final response"),
                    call_kind="llm_final_response",
                    trace_id=final_call_id,
                    trace_role="response",
                    trace_group="stage",
                )

                label, iteration_text, tool_calls = await self._stream_one_iteration(
                    messages=messages,
                    tool_schemas=tool_schemas,
                    stream=stream,
                    iter_meta=iter_meta,
                    final_meta=final_meta,
                )

                # Reconcile contradictions between the declared label and
                # actual stream signals, then dispatch on the resolved
                # action.
                if label == LABEL_TOOL and not tool_calls:
                    # Model said TOOL but never emitted calls — fall back
                    # to a THINK iteration (the prose was reasoning).
                    label = LABEL_THINK
                if label == LABEL_FINISH and tool_calls:
                    # Model said FINISH but still emitted tool_calls. Trust
                    # the tool intent — those calls happened mid-stream and
                    # the body already received the prose chunks before the
                    # calls appeared. Promote to TOOL so we dispatch.
                    label = LABEL_TOOL

                if label == LABEL_FINISH:
                    # Content already streamed live to the answer body via
                    # the ``stream.content(call_kind=llm_final_response)``
                    # path inside ``_stream_one_iteration``. Nothing more
                    # to do — just record and exit.
                    final_text += iteration_text
                    completed = True
                    break

                if label == LABEL_TOOL:
                    messages.append(
                        self._assistant_message_with_tool_calls(
                            content=iteration_text,
                            tool_calls=tool_calls,
                        )
                    )
                    iter_sources, tool_messages = await self._dispatch_tool_calls(
                        tool_calls=tool_calls,
                        context=context,
                        stream=stream,
                        iteration_index=iteration,
                    )
                    aggregated_sources.extend(iter_sources)
                    messages.extend(tool_messages)
                    continue

                if label == LABEL_THINK:
                    # Intermediate reasoning — no tools, no answer yet.
                    # Persist the prose into the conversation so the next
                    # iteration's LLM call can build on it.
                    if iteration_text:
                        messages.append(
                            {"role": "assistant", "content": iteration_text}
                        )
                    continue

                # LABEL_UNKNOWN — protocol violation fallback. Behave like
                # the legacy "absorb-into-final" logic: if tool_calls came,
                # treat as TOOL; otherwise treat as FINISH by emitting one
                # synthetic content event and marking the existing sub-trace
                # as absorbed so it doesn't visually duplicate the answer.
                if tool_calls:
                    messages.append(
                        self._assistant_message_with_tool_calls(
                            content=iteration_text,
                            tool_calls=tool_calls,
                        )
                    )
                    iter_sources, tool_messages = await self._dispatch_tool_calls(
                        tool_calls=tool_calls,
                        context=context,
                        stream=stream,
                        iteration_index=iteration,
                    )
                    aggregated_sources.extend(iter_sources)
                    messages.extend(tool_messages)
                    continue

                # No tool_calls + no valid label → treat as FINISH-fallback.
                # The sub-trace was already opened during streaming; mark it
                # absorbed so the frontend hides it, then emit the answer
                # body content.
                await stream.progress(
                    "",
                    source="chat",
                    stage="responding",
                    metadata=merge_trace_metadata(
                        iter_meta,
                        {
                            "trace_kind": "call_status",
                            "call_state": "complete",
                            "absorbed_into_final": True,
                        },
                    ),
                )
                await stream.content(
                    iteration_text,
                    source="chat",
                    stage="responding",
                    metadata=merge_trace_metadata(
                        final_meta, {"trace_kind": "llm_output"}
                    ),
                )
                final_text += iteration_text
                completed = True
                break
            else:
                # Loop exhausted without a clean final response. Emit a
                # one-off warning event (no call_id — not a sub-trace).
                await stream.progress(
                    self._t("notices.max_iterations_reached"),
                    source="chat",
                    stage="responding",
                    metadata={"trace_kind": "warning"},
                )

        if aggregated_sources:
            await stream.sources(
                aggregated_sources,
                source="chat",
                stage="responding",
                metadata={"trace_kind": "sources"},
            )

        result_payload: dict[str, Any] = {
            "response": final_text,
            "iterations": iteration + 1,
            "completed": completed,
        }
        cs = self._get_cost_summary()
        if cs:
            result_payload["metadata"] = {"cost_summary": cs}
        await stream.result(result_payload, source="chat")

    # ------------------------------------------------------------------
    # Iteration core: one streaming LLM call with tools
    # ------------------------------------------------------------------
    async def _stream_one_iteration(
        self,
        *,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]] | None,
        stream: StreamBus,
        iter_meta: dict[str, Any],
        final_meta: dict[str, Any],
    ) -> tuple[str, str, list[dict[str, Any]]]:
        r"""Run one LLM streaming call. Parses the protocol label
        (``\`\`FINISH\`\``` / ``\`\`TOOL\`\``` / ``\`\`THINK\`\```) from the FIRST chunks of
        the content stream, then routes subsequent chunks accordingly:

        * ``FINISH``: post-label chunks stream **directly to the answer body**
          via ``stream.content(call_kind="llm_final_response")``. No iteration
          sub-trace is ever opened — there's nothing intermediate to show.
        * ``TOOL`` / ``THINK``: post-label chunks stream as ``stream.thinking``
          events scoped to ``iter_meta.call_id`` so they fill a single
          "Reasoning" sub-trace in CallTracePanel.

        ``UNKNOWN`` is returned if the buffer exceeds ``LABEL_PROBE_MAX_CHARS``
        without a valid label — the caller falls back to the legacy
        absorb-into-final mechanism.

        Returns ``(label, accumulated_post_label_text, parsed_tool_calls)``.
        For ``FINISH`` the text reflects only what was streamed to the body;
        for ``TOOL``/``THINK`` it's the reasoning prose that the next
        iteration will see as the assistant's previous message.
        """
        client = self._build_openai_client()
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **self._completion_kwargs(max_tokens=self._responding_max_tokens),
        }
        if tool_schemas:
            kwargs["tools"] = tool_schemas
            kwargs["tool_choice"] = "auto"

        label: str | None = None
        label_buf = ""
        sub_trace_opened = False
        content_acc: list[str] = []
        tc_acc: dict[int, dict[str, Any]] = {}
        usage_seen: Any = None

        async def _open_sub_trace() -> None:
            nonlocal sub_trace_opened
            if sub_trace_opened:
                return
            await stream.progress(
                iter_meta["label"],
                source="chat",
                stage="responding",
                metadata=merge_trace_metadata(
                    iter_meta,
                    {"trace_kind": "call_status", "call_state": "running"},
                ),
            )
            sub_trace_opened = True

        async def _emit_text(text: str) -> None:
            """Route a post-label text fragment to body or sub-trace."""
            if not text:
                return
            content_acc.append(text)
            if label == LABEL_FINISH:
                await stream.content(
                    text,
                    source="chat",
                    stage="responding",
                    metadata=merge_trace_metadata(final_meta, {"trace_kind": "llm_chunk"}),
                )
            else:
                # THINK / TOOL / UNKNOWN — all surface as reasoning sub-trace.
                await _open_sub_trace()
                await stream.thinking(
                    text,
                    source="chat",
                    stage="responding",
                    metadata=merge_trace_metadata(iter_meta, {"trace_kind": "llm_chunk"}),
                )

        response_stream = await client.chat.completions.create(**kwargs)
        try:
            async for chunk in response_stream:
                if getattr(chunk, "usage", None):
                    usage_seen = chunk.usage
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta is None:
                    continue

                if delta.content:
                    text = delta.content
                    if label is None:
                        label_buf += text
                        parsed = _classify_label(label_buf)
                        if parsed is not None:
                            label, after_label = parsed
                            label_buf = ""
                            await _emit_text(after_label)
                        elif len(label_buf) > LABEL_PROBE_MAX_CHARS:
                            # Model didn't follow the protocol. Fall back —
                            # stream what we've buffered as reasoning and
                            # let the caller decide based on tool_calls.
                            label = LABEL_UNKNOWN
                            flushed = label_buf
                            label_buf = ""
                            await _emit_text(flushed)
                    else:
                        await _emit_text(text)

                for tc_delta in getattr(delta, "tool_calls", None) or []:
                    # Tool-call delta is authoritative for the TOOL path.
                    # If we're still buffering a label, force-resolve as TOOL
                    # so the buffered prose flushes into the reasoning sub-
                    # trace and subsequent prose continues there.
                    if label is None:
                        label = LABEL_TOOL
                        flushed = label_buf
                        label_buf = ""
                        if flushed:
                            await _emit_text(flushed)
                    idx = getattr(tc_delta, "index", 0)
                    entry = tc_acc.setdefault(
                        idx, {"id": "", "name": "", "arguments": ""}
                    )
                    if getattr(tc_delta, "id", None):
                        entry["id"] = tc_delta.id
                    fn = getattr(tc_delta, "function", None)
                    if fn is not None:
                        if getattr(fn, "name", None):
                            entry["name"] = entry["name"] + fn.name
                        if getattr(fn, "arguments", None):
                            entry["arguments"] = entry["arguments"] + fn.arguments
        finally:
            close = getattr(response_stream, "close", None)
            if callable(close):
                with self._suppress_close_errors():
                    await close()

        if usage_seen is not None:
            self._accumulate_usage(_UsageShim(usage_seen))

        # Stream ended while still buffering a label (very short reply that
        # never reached LABEL_PROBE_MAX_CHARS and never matched). Flush as
        # UNKNOWN — the caller will decide based on tool_calls.
        if label is None:
            label = LABEL_UNKNOWN
            if label_buf:
                await _emit_text(label_buf)
                label_buf = ""

        # Close the sub-trace if it was opened (THINK / TOOL / UNKNOWN
        # paths). FINISH never opened one — its content went straight to
        # the body.
        if sub_trace_opened:
            await stream.progress(
                "",
                source="chat",
                stage="responding",
                metadata=merge_trace_metadata(
                    iter_meta,
                    {"trace_kind": "call_status", "call_state": "complete"},
                ),
            )

        text = clean_thinking_tags("".join(content_acc), self.binding, self.model)
        ordered_tool_calls = [tc_acc[k] for k in sorted(tc_acc.keys())]
        # Filter out empty / malformed deltas that some providers emit.
        ordered_tool_calls = [tc for tc in ordered_tool_calls if tc.get("name")]
        return label, text, ordered_tool_calls

    # ------------------------------------------------------------------
    # Tool dispatch
    # ------------------------------------------------------------------
    async def _dispatch_tool_calls(
        self,
        *,
        tool_calls: list[dict[str, Any]],
        context: UnifiedContext,
        stream: StreamBus,
        iteration_index: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Execute one iteration's tool calls in parallel.

        Each individual tool call is given its own trace ``call_id`` so
        ``CallTracePanel`` renders each as a separate sub-trace row
        (e.g. "Tool call · code_execution" + "Retrieve" + …) — matching the
        user's "one LLM call or one tool call = one sub-trace" expectation.

        Returns ``(aggregated_sources, tool_role_messages)``. Tool messages
        are formatted for the OpenAI ``role=tool`` protocol so the next
        iteration's LLM call sees them.
        """
        if len(tool_calls) > MAX_PARALLEL_TOOL_CALLS:
            # Capped truncation notice carries no call_id — it's a one-off
            # warning, not a sub-trace.
            await stream.progress(
                self._t(
                    "notices.too_many_tool_calls",
                    requested=len(tool_calls),
                    limit=MAX_PARALLEL_TOOL_CALLS,
                ),
                source="chat",
                stage="acting",
                metadata={"trace_kind": "warning"},
            )
            tool_calls = tool_calls[:MAX_PARALLEL_TOOL_CALLS]

        prepared: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
        for tc in tool_calls:
            tool_name = str(tc.get("name") or "").strip()
            tool_call_id = str(tc.get("id") or "").strip()
            tool_args = parse_json_response(
                tc.get("arguments") or "{}",
                logger_instance=logger,
                fallback={},
            )
            if not isinstance(tool_args, dict):
                tool_args = {}
            execution_args = self._augment_tool_kwargs(tool_name, tool_args, context)
            prepared.append((tool_call_id, tool_name, dict(execution_args), execution_args))

        # Allocate a fresh trace call_id per tool call so each shows as its
        # own sub-trace in CallTracePanel. The OpenAI ``tool_call_id`` (used
        # for the role=tool message protocol) is separate from this trace id.
        per_tool_trace_meta: list[dict[str, Any]] = []
        for tool_index, (tool_call_id, tool_name, _display, _exec_args) in enumerate(prepared):
            trace_call_id = new_call_id(f"chat-iter-{iteration_index}-tool-{tool_index}")
            base_meta = build_trace_metadata(
                call_id=trace_call_id,
                phase="acting",
                label=self._t("labels.tool_call", default="Tool call"),
                call_kind="tool_planning",
                trace_id=trace_call_id,
                trace_role="tool",
                trace_group="tool_call",
            )
            per_tool_trace_meta.append(
                merge_trace_metadata(
                    base_meta,
                    {
                        "tool_call_id": tool_call_id,
                        "tool_name": tool_name,
                        "tool_index": tool_index,
                        "iteration_index": iteration_index,
                        "session_id": context.session_id,
                        "turn_id": str(context.metadata.get("turn_id", "")),
                    },
                )
            )

        for tool_index, (tool_call_id, tool_name, display_args, _exec_args) in enumerate(prepared):
            tool_meta = per_tool_trace_meta[tool_index]
            await stream.tool_call(
                tool_name=tool_name,
                args=display_args,
                source="chat",
                stage="acting",
                metadata=merge_trace_metadata(tool_meta, {"trace_kind": "tool_call"}),
            )

        results = await asyncio.gather(
            *[
                self._execute_tool_call(
                    tool_name,
                    exec_args,
                    stream=stream,
                    retrieve_meta=self._retrieve_trace_metadata(
                        per_tool_trace_meta[tool_index],
                        context=context,
                        tool_name=tool_name,
                        tool_args=exec_args,
                    ),
                )
                for tool_index, (_tool_call_id, tool_name, _display, exec_args) in enumerate(
                    prepared
                )
            ]
        )

        aggregated_sources: list[dict[str, Any]] = []
        tool_messages: list[dict[str, Any]] = []
        for tool_index, ((tool_call_id, tool_name, display_args, _exec_args), result) in enumerate(
            zip(prepared, results, strict=False)
        ):
            result_text = str(result["result_text"])
            tool_meta = per_tool_trace_meta[tool_index]
            await stream.tool_result(
                tool_name=tool_name,
                result=result_text,
                source="chat",
                stage="acting",
                metadata=merge_trace_metadata(tool_meta, {"trace_kind": "tool_result"}),
            )
            aggregated_sources.extend(result.get("sources") or [])
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": result_text,
                }
            )
        return aggregated_sources, tool_messages

    # ------------------------------------------------------------------
    # Answer-now: cancel mid-stream and produce a final answer from what's
    # already been generated. Single LLM call, tools disabled, partial draft
    # injected as a fake assistant message so the model continues naturally.
    # ------------------------------------------------------------------
    async def _run_answer_now(
        self,
        context: UnifiedContext,
        answer_now_context: dict[str, Any],
        stream: StreamBus,
    ) -> None:
        partial_response = str(answer_now_context.get("partial_response") or "").strip()
        original_user_message = str(
            answer_now_context.get("original_user_message") or context.user_message
        ).strip()

        trace_meta = build_trace_metadata(
            call_id=new_call_id("chat-answer-now"),
            phase="responding",
            label=self._t("labels.answer_now", default="Answer now"),
            call_kind="llm_final_response",
            trace_id="chat-answer-now",
            trace_role="response",
            trace_group="stage",
        )
        async with stream.stage("responding", source="chat", metadata=trace_meta):
            await stream.progress(
                trace_meta["label"],
                source="chat",
                stage="responding",
                metadata=merge_trace_metadata(
                    trace_meta, {"trace_kind": "call_status", "call_state": "running"}
                ),
            )

            system_prompt = self._build_system_prompt(enabled_tools=[], context=context)
            messages = self._build_messages(
                context=context,
                system_prompt=system_prompt,
                user_content=original_user_message,
            )
            messages, _ = self._prepare_messages_with_attachments(messages, context)
            if partial_response:
                messages.append({"role": "assistant", "content": partial_response})
            messages.append(
                {"role": "user", "content": self._t("answer_now.user", default="Finalize now.")}
            )

            chunks: list[str] = []
            async for chunk in self._stream_messages(
                messages, max_tokens=self._answer_now_max_tokens
            ):
                if not chunk:
                    continue
                chunks.append(chunk)
                await stream.content(
                    chunk,
                    source="chat",
                    stage="responding",
                    metadata=merge_trace_metadata(trace_meta, {"trace_kind": "llm_chunk"}),
                )
            await stream.progress(
                "",
                source="chat",
                stage="responding",
                metadata=merge_trace_metadata(
                    trace_meta, {"trace_kind": "call_status", "call_state": "complete"}
                ),
            )
            final_text = clean_thinking_tags("".join(chunks), self.binding, self.model)

        result_payload: dict[str, Any] = {
            "response": final_text,
            "answer_now": True,
            "source_trace": trace_meta.get("label", "Answer now"),
        }
        cs = self._get_cost_summary()
        if cs:
            result_payload["metadata"] = {"cost_summary": cs}
        await stream.result(result_payload, source="chat")

    # ------------------------------------------------------------------
    # In-turn context-window guard
    # ------------------------------------------------------------------
    async def _guard_context_window(
        self,
        messages: list[dict[str, Any]],
        stream: StreamBus,
    ) -> None:
        """Replace oldest tool-result contents with a snip marker until total
        token count fits under ``CONTEXT_WINDOW_GUARD_RATIO`` of the model's
        effective window. Never touches the system message or the original
        user message — only ``role == 'tool'`` payloads. Cross-turn history
        compression is handled separately by ``ContextBuilder``.
        """
        try:
            window = resolve_effective_context_window(
                context_window=getattr(self.llm_config, "context_window", None),
                model=str(self.model or ""),
                max_tokens=getattr(self.llm_config, "max_tokens", None),
            )
        except Exception:
            return
        if not window or window <= 0:
            return
        budget = int(window * CONTEXT_WINDOW_GUARD_RATIO)
        if self._estimate_messages_tokens(messages) <= budget:
            return
        snipped = False
        for msg in messages:
            if msg.get("role") != "tool":
                continue
            current_content = msg.get("content")
            if current_content == TOOL_RESULT_SNIP_MARKER:
                continue
            msg["content"] = TOOL_RESULT_SNIP_MARKER
            snipped = True
            if self._estimate_messages_tokens(messages) <= budget:
                break
        if snipped:
            # Warning is not a sub-trace — emit without a call_id.
            await stream.progress(
                self._t("notices.context_window_guard"),
                source="chat",
                stage="responding",
                metadata={"trace_kind": "warning"},
            )

    @staticmethod
    def _estimate_messages_tokens(messages: list[dict[str, Any]]) -> int:
        # Local import to break the agents.chat ↔ services.session
        # import cycle (context_builder pulls in agents.base_agent which
        # re-enters this module during package init).
        from deeptutor.services.session.context_builder import count_tokens

        total = 0
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                total += count_tokens(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        total += count_tokens(str(part.get("text") or ""))
        return total

    # ------------------------------------------------------------------
    # System prompt + message construction
    # ------------------------------------------------------------------
    def _build_system_prompt(
        self,
        enabled_tools: list[str],
        context: UnifiedContext,
    ) -> str:
        # ``list_with_usage`` renders one bullet per tool including the tool's
        # ``when_to_use`` and ``input_format`` — pulled from per-tool YAML
        # under ``deeptutor/tools/prompting/hints/{lang}/{tool}.yaml``. This
        # is the only place per-tool guidance enters the chat persona prompt:
        # disabled tools contribute nothing, so the model never sees
        # instructions for tools it cannot call.
        tool_list = self.registry.build_prompt_text(
            enabled_tools,
            format="list_with_usage",
            language=self.language,
        )
        system = self._t(
            "system",
            tool_list=tool_list or self._fallback_empty_tool_list(),
            kb_note=self._kb_system_note(context),
        )
        return append_language_directive(system, self.language)

    def _build_messages(
        self,
        *,
        context: UnifiedContext,
        system_prompt: str,
        user_content: str,
    ) -> list[dict[str, Any]]:
        """Assemble ``[system] + history + user``.

        ``memory_context``, ``skills_context``, and ``source_manifest`` are
        appended as separate ``---``-delimited sections after the main
        system prompt so prompt caching stays effective when only the
        manifest tail changes between turns.
        """
        system_parts = [system_prompt]
        if context.memory_context:
            system_parts.append(context.memory_context)
        if context.skills_context:
            system_parts.append(context.skills_context)
        if context.source_manifest:
            system_parts.append(context.source_manifest)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "\n\n---\n\n".join(system_parts)}
        ]
        for item in context.conversation_history:
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, (str, list)):
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_content})
        return messages

    def _prepare_messages_with_attachments(
        self,
        messages: list[dict[str, Any]],
        context: UnifiedContext,
    ) -> tuple[list[dict[str, Any]], bool]:
        mm_result = prepare_multimodal_messages(
            messages,
            context.attachments,
            binding=self.binding,
            model=self.model,
        )
        return mm_result.messages, mm_result.images_stripped

    # ------------------------------------------------------------------
    # Tool selection + scheme construction
    # ------------------------------------------------------------------
    def _compose_enabled_tools(self, context: UnifiedContext) -> list[str]:
        """Resolve the tool set for this turn.

        - User-toggled tools come from ``context.enabled_tools``, filtered
          by ``CHAT_OPTIONAL_TOOLS`` (so ``geogebra_analysis`` and
          ``read_source`` are never user-toggleable here).
        - ``rag`` is auto-included iff the user attached any KB.
        - ``read_source`` is auto-included iff the turn has a non-empty
          source index (notebook / book / history / question / attachment).
        """
        requested = [tool for tool in (context.enabled_tools or []) if tool != "rag"]
        normalized = [
            tool.name
            for tool in self.registry.get_enabled(requested)
            if tool.name in CHAT_OPTIONAL_TOOLS
        ]
        if self._selected_kbs(context):
            normalized.append("rag")
        if self._source_index(context):
            normalized.append("read_source")
        return normalized

    def _build_llm_tool_schemas(
        self,
        enabled_tools: list[str],
        context: UnifiedContext,
    ) -> list[dict[str, Any]]:
        """Return per-turn OpenAI tool schemas, with per-tool constraints.

        - ``rag.kb_name`` is restricted to the attached KBs as an enum.
        - ``read_source.source_id`` is restricted to the attached source
          ids as an enum (this makes the LLM less likely to hallucinate
          ids and lets the OpenAI SDK validate the call client-side).
        """
        schemas = self.registry.build_openai_schemas(enabled_tools)
        kb_choices = self._selected_kbs(context)
        source_ids = sorted((self._source_index(context) or {}).keys())
        for schema in schemas:
            function = schema.get("function") if isinstance(schema, dict) else None
            if not isinstance(function, dict):
                continue
            parameters = function.get("parameters")
            if not isinstance(parameters, dict):
                continue
            properties = parameters.get("properties") or {}
            if function.get("name") == "rag" and isinstance(properties, dict):
                query_schema = properties.get("query")
                if isinstance(query_schema, dict):
                    query_schema.setdefault("minLength", 1)
                kb_schema = properties.get("kb_name")
                if isinstance(kb_schema, dict):
                    kb_schema["enum"] = kb_choices
            if function.get("name") == "read_source" and isinstance(properties, dict):
                sid_schema = properties.get("source_id")
                if isinstance(sid_schema, dict) and source_ids:
                    sid_schema["enum"] = source_ids
            parameters["additionalProperties"] = False
        return schemas

    @staticmethod
    def _extract_answer_now_context(context: UnifiedContext) -> dict[str, Any] | None:
        from deeptutor.capabilities._answer_now import extract_answer_now_context

        return extract_answer_now_context(context)

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------
    async def _execute_tool_call(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        *,
        stream: StreamBus | None = None,
        retrieve_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async def _event_sink(
            event_type: str,
            message: str = "",
            metadata: dict[str, Any] | None = None,
        ) -> None:
            if stream is None or retrieve_meta is None or not message:
                return
            await stream.progress(
                message,
                source="chat",
                stage="acting",
                metadata=derive_trace_metadata(
                    retrieve_meta,
                    trace_kind=str(event_type or "tool_log"),
                    **(metadata or {}),
                ),
            )

        if stream is not None and retrieve_meta is not None:
            query = str(retrieve_meta.get("query") or tool_args.get("query") or "").strip()
            await stream.progress(
                f"Query: {query}" if query else self._t("notices.start_retrieval"),
                source="chat",
                stage="acting",
                metadata=derive_trace_metadata(
                    retrieve_meta,
                    trace_kind="call_status",
                    call_state="running",
                ),
            )
        try:
            result = await self.registry.execute(
                tool_name,
                event_sink=_event_sink if retrieve_meta is not None else None,
                **tool_args,
            )
            if stream is not None and retrieve_meta is not None:
                await stream.progress(
                    f"Retrieve complete ({len(result.content)} chars)",
                    source="chat",
                    stage="acting",
                    metadata=derive_trace_metadata(
                        retrieve_meta,
                        trace_kind="call_status",
                        call_state="complete",
                    ),
                )
            return {
                "result_text": result.content or self._t("notices.empty_tool_result"),
                "success": result.success,
                "sources": result.sources,
                "metadata": result.metadata,
            }
        except Exception as exc:
            logger.error("Tool %s failed", tool_name, exc_info=True)
            if stream is not None and retrieve_meta is not None:
                await stream.error(
                    f"Retrieve failed: {exc}",
                    source="chat",
                    stage="acting",
                    metadata=derive_trace_metadata(
                        retrieve_meta,
                        trace_kind="call_status",
                        call_state="error",
                        error=str(exc),
                    ),
                )
            return {
                "result_text": f"Error executing {tool_name}: {exc}",
                "success": False,
                "sources": [],
                "metadata": {"error": str(exc)},
            }

    def _augment_tool_kwargs(
        self,
        tool_name: str,
        args: dict[str, Any],
        context: UnifiedContext,
    ) -> dict[str, Any]:
        from deeptutor.services.path_service import get_path_service

        kwargs = dict(args)
        turn_id = str(context.metadata.get("turn_id", "") or "").strip()
        task_dir = None
        if turn_id:
            task_dir = get_path_service().get_task_workspace("chat", turn_id)
        if tool_name == "rag":
            kwargs.setdefault("mode", "hybrid")
        elif tool_name == "code_execution":
            kwargs.setdefault("intent", context.user_message)
            kwargs.setdefault("timeout", 30)
            kwargs.setdefault("feature", "chat")
            kwargs.setdefault("session_id", context.session_id)
            kwargs.setdefault("turn_id", turn_id)
            if task_dir is not None:
                kwargs.setdefault("workspace_dir", str(task_dir / "code_runs"))
        elif tool_name in {"reason", "brainstorm"}:
            kwargs.setdefault("context", context.user_message)
        elif tool_name == "paper_search":
            kwargs.setdefault("max_results", 3)
            kwargs.setdefault("years_limit", 3)
            kwargs.setdefault("sort_by", "relevance")
        elif tool_name == "web_search":
            kwargs.setdefault("query", context.user_message)
            if task_dir is not None:
                kwargs.setdefault("output_dir", str(task_dir / "web_search"))
        elif tool_name == "read_source":
            # ReadSourceTool reads from this per-turn map rather than from
            # any shared state, so each turn's sources stay isolated.
            kwargs["source_index"] = self._source_index(context)
        return kwargs

    # ------------------------------------------------------------------
    # Tool / KB metadata helpers
    # ------------------------------------------------------------------
    def _retrieve_trace_metadata(
        self,
        tool_meta: dict[str, Any],
        *,
        context: UnifiedContext,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Build the retrieve-flavoured metadata for ``rag`` progress events.

        Each RAG call already has its own ``tool_meta`` (with its own
        ``call_id``) allocated by :py:meth:`_dispatch_tool_calls`; we
        derive a "retrieve" variant of it so the in-tool progress events
        (provider selection, chunk retrieval, etc.) stay attached to the
        same sub-trace but show as ``trace_role=retrieve`` for the
        chevron icon. For non-rag tools we return ``None`` so the
        executor skips the retrieve-progress surface.
        """
        if tool_name != "rag":
            return None
        return derive_trace_metadata(
            tool_meta,
            label=self._t("labels.retrieve", default="Retrieve"),
            call_kind="rag_retrieval",
            trace_role="retrieve",
            trace_group="retrieve",
            query=str(tool_args.get("query", "") or ""),
        )

    @staticmethod
    def _selected_kbs(context: UnifiedContext) -> list[str]:
        return [str(kb).strip() for kb in context.knowledge_bases if str(kb).strip()]

    @staticmethod
    def _source_index(context: UnifiedContext) -> dict[str, str]:
        idx = context.metadata.get("source_index")
        if isinstance(idx, dict) and idx:
            return idx
        return {}

    def _kb_system_note(self, context: UnifiedContext) -> str:
        kbs = self._selected_kbs(context)
        if not kbs:
            return ""
        joined = ", ".join(kbs)
        if self.language == "zh":
            return f"用户已挂载知识库：{joined}。调用 rag 时，kb_name 必须从其中选一个。"
        return (
            f"Attached knowledge bases: {joined}. When calling rag, kb_name must "
            "be one of these names."
        )

    def _fallback_empty_tool_list(self) -> str:
        return "- 无" if self.language == "zh" else "- none"

    # ------------------------------------------------------------------
    # LLM call helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _assistant_message_with_tool_calls(
        content: str,
        tool_calls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": content or None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc.get("arguments") or "{}",
                    },
                }
                for tc in tool_calls
            ],
        }

    async def _stream_messages(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int,
    ):
        """Stream a single tool-less LLM call. Used by answer-now."""
        output_chars = 0
        async for chunk in llm_stream(
            prompt="",
            system_prompt="",
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            api_version=self.api_version,
            binding=self.binding,
            messages=messages,
            extra_headers=self.extra_headers or None,
            **self._completion_kwargs(max_tokens=max_tokens),
        ):
            output_chars += len(chunk)
            yield chunk
        input_chars = sum(len(str(m.get("content", ""))) for m in messages)
        est_input = int(input_chars / 3.5)
        est_output = int(output_chars / 3.5)
        self._usage["prompt_tokens"] += est_input
        self._usage["completion_tokens"] += est_output
        self._usage["total_tokens"] += est_input + est_output
        self._usage["calls"] += 1

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
        kwargs: dict[str, Any] = {"temperature": self._chat_temperature}
        if self.model:
            kwargs.update(get_token_limit_kwargs(self.model, max_tokens))
        return kwargs

    def _can_use_native_tool_calling(self) -> bool:
        # Same gating as before: providers we know reliably support OpenAI
        # function-calling. For other bindings the loop still runs but
        # without tool schemas — the model just chats.
        if not supports_tools(self.binding, self.model):
            return False
        return self.binding not in {
            "anthropic",
            "claude",
            "ollama",
            "lm_studio",
            "vllm",
            "llama_cpp",
        }

    # ------------------------------------------------------------------
    # Usage tracking
    # ------------------------------------------------------------------
    def _accumulate_usage(self, response: Any) -> None:
        usage = getattr(response, "usage", None) or response
        prompt = getattr(usage, "prompt_tokens", 0) or 0
        completion = getattr(usage, "completion_tokens", 0) or 0
        total = getattr(usage, "total_tokens", prompt + completion) or 0
        if prompt or completion or total:
            self._usage["prompt_tokens"] += int(prompt)
            self._usage["completion_tokens"] += int(completion)
            self._usage["total_tokens"] += int(total)
            self._usage["calls"] += 1

    def _get_cost_summary(self) -> dict[str, Any] | None:
        if self._usage["calls"] == 0:
            return None
        return {
            "total_cost_usd": 0,
            "total_tokens": self._usage["total_tokens"],
            "total_calls": self._usage["calls"],
            "prompt_tokens": self._usage["prompt_tokens"],
            "completion_tokens": self._usage["completion_tokens"],
        }

    # ------------------------------------------------------------------
    # YAML prompt lookup
    # ------------------------------------------------------------------
    def _t(self, key: str, default: str = "", **kwargs: Any) -> str:
        """Look up a YAML-loaded prompt by dotted key. Returns ``default``
        when missing. Renders via ``str.format`` when ``kwargs`` are
        provided; missing placeholders leave the template unrendered
        instead of crashing the pipeline."""
        value: Any = self._prompts
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        if not isinstance(value, str):
            return default
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return value
        return value

    # ------------------------------------------------------------------
    # Misc small helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _suppress_close_errors():
        from contextlib import suppress

        return suppress(Exception)


class _UsageShim:
    """Adapt OpenAI streaming ``CompletionUsage`` into the shape
    ``_accumulate_usage`` expects (it walks ``response.usage`` fields)."""

    def __init__(self, raw: Any) -> None:
        self.usage = raw


def _read_int(cfg: Any, *, key: str, default: int) -> int:
    """Pull an integer from a nested YAML dict, falling back to ``default``."""
    if isinstance(cfg, dict):
        value = cfg.get(key, default)
    else:
        value = default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
