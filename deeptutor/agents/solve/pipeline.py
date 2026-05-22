"""SolvePipeline — agentic-engine-based replacement for ``MainSolver``.

Phase shape:

* **Phase 0 (Pre-retrieve)** — only when a KB is attached: one ``QUERIES``
  labeled step generates N queries, ``rag`` runs them in parallel, then one
  ``SUMMARY`` labeled step aggregates the results into a knowledge note.
* **Phase 1 (Plan)** — one ``PLAN`` labeled step emits a JSON plan. On
  ``REPLAN`` from Phase 2 the planner is re-entered with the previous
  attempt + replan reason as additional context.
* **Phase 2 (Solve)** — for each step, one agentic loop over the four
  ``THINK`` / ``TOOL`` / ``FINISH`` / ``REPLAN`` labels (see
  :mod:`deeptutor.core.agentic`). Each ``FINISH`` text is streamed as a
  user-facing section that flows into the next step's prompt context so
  the sections read as one continuous answer.
* **Phase 3 (Synthesize)** — one ``FINISH`` labeled step emits the precise
  final answer + a short recap.

The orchestrator owns control flow (replan back-edge, exhaustion handling)
and per-step prompt assembly; everything else is delegated to the engine
primitives.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from dataclasses import dataclass, field
import logging
from typing import Any

from deeptutor.capabilities._shared import emit_capability_result
from deeptutor.core.agentic import (
    DispatchOutcome,
    LabeledStepResult,
    LabelProtocol,
    LLMClientConfig,
    LoopOutcome,
    UsageTracker,
    build_completion_kwargs,
    build_openai_client,
    can_use_native_tool_calling,
    dispatch_tool_calls,
    run_agentic_loop,
    run_labeled_step,
)
from deeptutor.core.agentic.labels import find_inline_labels
from deeptutor.core.agentic.tool_dispatch import (
    MAX_PARALLEL_TOOL_CALLS,
    execute_tool_call,
)
from deeptutor.core.context import Attachment, UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import (
    build_trace_metadata,
    derive_trace_metadata,
    merge_trace_metadata,
    new_call_id,
)
from deeptutor.runtime.registry.tool_registry import get_tool_registry
from deeptutor.services.config import parse_language
from deeptutor.services.llm import get_llm_config, prepare_multimodal_messages
from deeptutor.services.path_service import get_path_service
from deeptutor.services.prompt import get_prompt_manager
from deeptutor.services.prompt.language import append_language_directive
from deeptutor.utils.json_parser import parse_json_response

logger = logging.getLogger(__name__)


SOURCE = "deep_solve"

# Labels each phase emits — must match what the YAML prompts instruct the LLM
# to produce.
LABEL_QUERIES = "QUERIES"
LABEL_SUMMARY = "SUMMARY"
LABEL_PLAN = "PLAN"
LABEL_THINK = "THINK"
LABEL_TOOL = "TOOL"
LABEL_FINISH = "FINISH"
LABEL_REPLAN = "REPLAN"
LABEL_EXPLAIN = "EXPLAIN"
LABEL_SKIP = "SKIP"

_PROTOCOL_QUERIES = LabelProtocol(
    allowed=(LABEL_QUERIES,),
    terminal=frozenset({LABEL_QUERIES}),
    intermediate=frozenset(),
    final=frozenset(),
    tool_label=None,
)
_PROTOCOL_SUMMARY = LabelProtocol(
    allowed=(LABEL_SUMMARY,),
    terminal=frozenset({LABEL_SUMMARY}),
    intermediate=frozenset(),
    final=frozenset(),
    tool_label=None,
)
_PROTOCOL_PLAN = LabelProtocol(
    allowed=(LABEL_PLAN,),
    terminal=frozenset({LABEL_PLAN}),
    intermediate=frozenset(),
    final=frozenset(),
    tool_label=None,
)
_PROTOCOL_STEP = LabelProtocol(
    allowed=(LABEL_THINK, LABEL_TOOL, LABEL_FINISH, LABEL_REPLAN),
    terminal=frozenset({LABEL_FINISH, LABEL_REPLAN}),
    intermediate=frozenset({LABEL_THINK}),
    final=frozenset({LABEL_FINISH}),
    tool_label=LABEL_TOOL,
)
_PROTOCOL_SYNTHESIZE = LabelProtocol(
    allowed=(LABEL_FINISH,),
    terminal=frozenset({LABEL_FINISH}),
    intermediate=frozenset(),
    final=frozenset({LABEL_FINISH}),
    tool_label=None,
)
_PROTOCOL_EXPLAIN_JUDGE = LabelProtocol(
    allowed=(LABEL_EXPLAIN, LABEL_SKIP),
    terminal=frozenset({LABEL_EXPLAIN, LABEL_SKIP}),
    intermediate=frozenset(),
    final=frozenset(),
    tool_label=None,
)
_PROTOCOL_EXPLAIN = LabelProtocol(
    allowed=(LABEL_FINISH,),
    terminal=frozenset({LABEL_FINISH}),
    intermediate=frozenset(),
    final=frozenset({LABEL_FINISH}),
    tool_label=None,
)

# Per-step iteration ceiling (Frank's choice: 7). Total replans across one
# turn are bounded separately by :attr:`SolvePipeline.max_replans`.
DEFAULT_MAX_ITERATIONS_PER_STEP = 7
DEFAULT_MAX_REPLANS = 2
DEFAULT_NUM_QUERIES = 3
DEFAULT_MAX_TOKENS = 8000
SYNTHESIZE_MAX_TOKENS = 2000
PRE_RETRIEVE_MAX_TOKENS = 2000
EXPLAIN_JUDGE_MAX_TOKENS = 500
EXPLAIN_MAX_TOKENS = 8000

# Caps that match the legacy planner's pre-retrieve sub-DAG so we don't
# blow up the aggregation call when retrieval pulls a lot of text.
MAX_CHARS_PER_RETRIEVAL = 2000
MAX_AGGREGATE_INPUT_CHARS = 6000

FINALIZATION_REPAIR_ATTEMPTS = 3


def _load_solve_settings() -> dict[str, Any]:
    """Read ``capabilities.solve`` from main.yaml. Missing → empty dict.

    Kept narrow on purpose: only the iteration knobs are settings-driven
    today (``max_iterations_per_step`` and ``max_replans``). Other budgets
    remain code-level constants because they're prompt-engineering-coupled.
    """
    try:
        from deeptutor.services.config import load_config_with_main

        cfg = load_config_with_main("main.yaml") or {}
        capabilities = cfg.get("capabilities") or {}
        solve_cfg = capabilities.get("solve") or {}
        return solve_cfg if isinstance(solve_cfg, dict) else {}
    except Exception:
        logger.debug("Failed to load solve settings; using hardcoded defaults", exc_info=True)
        return {}


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanStep:
    id: str
    goal: str


@dataclass(frozen=True)
class Plan:
    analysis: str
    steps: list[PlanStep] = field(default_factory=list)


@dataclass(frozen=True)
class StepFinish:
    step: PlanStep
    text: str


# ---------------------------------------------------------------------------
# SolvePipeline
# ---------------------------------------------------------------------------


class SolvePipeline:
    """One-shot orchestrator: instantiate per turn, call :meth:`run` once."""

    def __init__(
        self,
        *,
        language: str = "en",
        kb_name: str | None = None,
        enabled_tools: list[str] | None = None,
        max_iterations_per_step: int | None = None,
        max_replans: int | None = None,
        num_queries: int = DEFAULT_NUM_QUERIES,
    ) -> None:
        self.language = parse_language(language)
        self.kb_name = (kb_name or "").strip() or None
        self.enabled_tools = list(enabled_tools or [])
        # Iteration limits are settings-driven (capabilities.solve in
        # main.yaml). Explicit constructor args still win so tests can
        # pin a tight loop; ``None`` (the default) means "read settings".
        solve_settings = _load_solve_settings()
        self.max_iterations_per_step = max(
            1,
            int(
                max_iterations_per_step
                if max_iterations_per_step is not None
                else solve_settings.get("max_iterations_per_step", DEFAULT_MAX_ITERATIONS_PER_STEP)
            ),
        )
        self.max_replans = max(
            0,
            int(
                max_replans
                if max_replans is not None
                else solve_settings.get("max_replans", DEFAULT_MAX_REPLANS)
            ),
        )
        self.num_queries = max(1, int(num_queries))

        self.llm_config = get_llm_config()
        self.binding = getattr(self.llm_config, "binding", None) or "openai"
        self.model = getattr(self.llm_config, "model", None)
        self.api_key = getattr(self.llm_config, "api_key", None)
        self.base_url = getattr(self.llm_config, "base_url", None)
        self.api_version = getattr(self.llm_config, "api_version", None)
        self.extra_headers = getattr(self.llm_config, "extra_headers", None) or {}
        self.reasoning_effort = getattr(self.llm_config, "reasoning_effort", None)
        self.client_config = LLMClientConfig(
            binding=self.binding,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            api_version=self.api_version,
            extra_headers=self.extra_headers or None,
            reasoning_effort=self.reasoning_effort,
        )

        self.registry = get_tool_registry()
        self.usage = UsageTracker(model=self.model)

        self._temperature = 0.2
        try:
            self._prompts: dict[str, Any] = (
                get_prompt_manager().load_prompts(
                    module_name="solve",
                    agent_name="pipeline",
                    language=self.language,
                )
                or {}
            )
        except Exception as exc:
            logger.warning("Failed to load solve pipeline prompts: %s", exc)
            self._prompts = {}

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    async def run(
        self,
        *,
        context: UnifiedContext,
        question: str,
        attachments: list[Attachment] | None = None,
        conversation_context: str = "",
        memory_context: str = "",
        stream: StreamBus,
    ) -> dict[str, Any]:
        """Drive the four phases. Streams content + trace events; returns the
        final-answer payload for the capability to forward into
        ``stream.result``.

        Wraps each phase transition in a ``_visible_failure`` guard so any
        runtime exception surfaces in the trace UI as a labeled error card
        (a bare ``bus.error`` without ``call_id`` is not rendered by the
        frontend's ``TracePanels`` and would look like a silent termination).
        """
        attachments = list(attachments or [])
        conversation_context = conversation_context.strip()
        memory_context = memory_context.strip()

        client = self._build_client()
        image_attachments = [a for a in attachments if getattr(a, "type", "") == "image"]

        try:
            return await self._run_inner(
                context=context,
                question=question,
                conversation_context=conversation_context,
                memory_context=memory_context,
                image_attachments=image_attachments,
                stream=stream,
                client=client,
            )
        except Exception as exc:
            logger.exception("SolvePipeline.run failed: %s", exc)
            await self._emit_visible_failure(stream, exc)
            raise

    async def _emit_visible_failure(self, stream: StreamBus, exc: BaseException) -> None:
        """Make a runtime failure visible to the user.

        Emits a trace card (so the panel shows up next to the plan card) plus
        a content event (so the chat bubble shows the error inline). The
        capability layer / orchestrator still gets the exception via
        ``re-raise`` so logs and DONE events fire normally.
        """
        call_id = new_call_id("solve-failure")
        meta = build_trace_metadata(
            call_id=call_id,
            phase="reasoning",
            label=self._t("labels.solve_step", default="Solve step"),
            call_kind="llm_final_response",
            trace_id=call_id,
            trace_role="response",
            trace_group="stage",
        )
        message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        await stream.error(
            message,
            source=SOURCE,
            stage="reasoning",
            metadata=merge_trace_metadata(meta, {"trace_kind": "error"}),
        )
        # A bare ``bus.error`` isn't rendered by the chat bubble; pipe the
        # same text through ``content`` so the user actually sees what went
        # wrong instead of an empty assistant message.
        prefix = "⚠️ " if self.language == "zh" else "⚠ "
        await stream.content(
            f"{prefix}{message}",
            source=SOURCE,
            stage="reasoning",
            metadata=merge_trace_metadata(meta, {"trace_kind": "llm_output"}),
        )

    async def _run_inner(
        self,
        *,
        context: UnifiedContext,
        question: str,
        conversation_context: str,
        memory_context: str,
        image_attachments: list[Attachment],
        stream: StreamBus,
        client: Any,
    ) -> dict[str, Any]:
        logger.info(
            "SolvePipeline.run start: lang=%s kb=%s tools=%s max_iter/step=%d max_replans=%d",
            self.language,
            self.kb_name,
            self.enabled_tools,
            self.max_iterations_per_step,
            self.max_replans,
        )

        # ----- Phase 0 + Phase 1 (planning umbrella) -----
        async with stream.stage("planning", source=SOURCE):
            retrieved_context = await self._pre_retrieve(
                question=question,
                stream=stream,
                client=client,
                context=context,
            )
            plan = await self._plan(
                question=question,
                retrieved_context=retrieved_context,
                memory_context=memory_context,
                conversation_context=conversation_context,
                replan_reason=None,
                previous_attempt=[],
                attempt_index=0,
                image_attachments=image_attachments,
                stream=stream,
                client=client,
            )
        logger.info(
            "SolvePipeline plan: analysis=%r steps=%d",
            plan.analysis[:80],
            len(plan.steps),
        )

        # ----- Phase 2 (solve steps) -----
        step_finishes: list[StepFinish] = []
        replan_count = 0
        plan_attempt = 0
        async with stream.stage("reasoning", source=SOURCE):
            while True:
                plan_attempt += 1
                replanned = False
                attempt_finishes: list[StepFinish] = []
                for step_index, step in enumerate(plan.steps):
                    logger.info(
                        "SolvePipeline step %s (%d/%d, attempt %d)",
                        step.id,
                        step_index + 1,
                        len(plan.steps),
                        plan_attempt,
                    )
                    outcome = await self._solve_step(
                        step=step,
                        step_index=step_index,
                        total_steps=len(plan.steps),
                        plan=plan,
                        question=question,
                        retrieved_context=retrieved_context,
                        previous_finishes=attempt_finishes,
                        memory_context=memory_context,
                        conversation_context=conversation_context,
                        image_attachments=image_attachments,
                        context=context,
                        stream=stream,
                        client=client,
                    )
                    if outcome.final_label == LABEL_REPLAN:
                        if replan_count >= self.max_replans:
                            await stream.progress(
                                self._t("notices.replan_budget_exhausted"),
                                source=SOURCE,
                                stage="reasoning",
                                metadata={"trace_kind": "warning"},
                            )
                            # Accept the replan reason as the step's content
                            # so the synthesize phase still has something to
                            # work with.
                            attempt_finishes.append(
                                StepFinish(step=step, text=outcome.final_text.strip())
                            )
                            continue
                        replan_count += 1
                        plan = await self._plan(
                            question=question,
                            retrieved_context=retrieved_context,
                            memory_context=memory_context,
                            conversation_context=conversation_context,
                            replan_reason=outcome.final_text.strip(),
                            previous_attempt=attempt_finishes,
                            attempt_index=plan_attempt,
                            image_attachments=image_attachments,
                            stream=stream,
                            client=client,
                        )
                        replanned = True
                        break
                    # FINISH (or exhaustion-forced FINISH). After the step's
                    # section has streamed to the user, optionally ask the
                    # model whether a deeper explanation is worth appending,
                    # and if so stream it live under the FINISH content.
                    finish_text = outcome.final_text.strip()
                    # Force a markdown block break before whatever streams
                    # next (the explain expansion if EXPLAIN, otherwise the
                    # next step's FINISH or the synthesize section). Without
                    # this the next chunk would glue onto the last sentence
                    # of this step.
                    await self._emit_section_break(stream)
                    explanation = await self._maybe_explain_step(
                        step=step,
                        question=question,
                        finish_text=finish_text,
                        image_attachments=image_attachments,
                        stream=stream,
                        client=client,
                    )
                    combined_text = (
                        f"{finish_text}\n\n{explanation}" if explanation else finish_text
                    )
                    attempt_finishes.append(StepFinish(step=step, text=combined_text))
                if not replanned:
                    step_finishes = attempt_finishes
                    break

        # ----- Phase 3 (synthesize) -----
        logger.info("SolvePipeline synthesize: %d completed steps", len(step_finishes))
        final_text = ""
        async with stream.stage("writing", source=SOURCE):
            final_text = await self._synthesize(
                question=question,
                step_finishes=step_finishes,
                conversation_context=conversation_context,
                stream=stream,
                client=client,
            )

        result_payload: dict[str, Any] = {
            "response": self._compose_full_response(step_finishes, final_text),
            "step_count": len(plan.steps),
            "completed_steps": len(step_finishes),
            "plan_revisions": replan_count,
            "metadata": {
                "mode": "agentic_solve",
                "step_count": len(plan.steps),
                "plan_revisions": replan_count,
            },
        }
        await emit_capability_result(stream, result_payload, source=SOURCE, usage=self.usage)
        return result_payload

    # ------------------------------------------------------------------
    # Phase 0: pre-retrieve
    # ------------------------------------------------------------------
    async def _pre_retrieve(
        self,
        *,
        question: str,
        stream: StreamBus,
        client: Any,
        context: UnifiedContext,
    ) -> str:
        if not self.kb_name or not self._tool_in_registry("rag"):
            await stream.progress(
                self._t("notices.pre_retrieve_unavailable"),
                source=SOURCE,
                stage="planning",
                metadata={"trace_kind": "info"},
            )
            return self._t("empty.no_kb_retrieved")

        try:
            queries = await self._generate_search_queries(
                question=question, stream=stream, client=client
            )
            retrievals = await self._parallel_retrieve(
                queries=queries, stream=stream, context=context
            )
            if not any(item.get("answer") for item in retrievals):
                return self._t("empty.no_kb_retrieved")
            return await self._aggregate_retrieval_results(
                retrievals=retrievals, stream=stream, client=client
            )
        except Exception as exc:
            logger.warning("Pre-retrieval pipeline failed: %s", exc)
            return self._t("empty.no_kb_retrieved")

    async def _generate_search_queries(
        self,
        *,
        question: str,
        stream: StreamBus,
        client: Any,
    ) -> list[str]:
        system_prompt = self._t("pre_retrieve.gen_queries.system")
        user_prompt = self._t(
            "pre_retrieve.gen_queries.user_template",
            num_queries=self.num_queries,
            question=question,
        )
        messages = self._build_system_user_messages(system_prompt, user_prompt)
        iter_meta = self._build_simple_trace_meta(
            call_id_root="solve-queries",
            label=self._t("labels.gen_queries", default="Generate queries"),
            stage="planning",
            call_kind="llm_planning",
            trace_role="plan",
            trace_group="plan",
        )
        step = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_QUERIES,
            stream=stream,
            stage="planning",
            iter_meta=iter_meta,
        )
        payload = parse_json_response(step.text, logger_instance=logger, fallback={})
        if isinstance(payload, list):
            queries = payload
        elif isinstance(payload, dict):
            queries = payload.get("queries", [])
        else:
            queries = []
        cleaned = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
        return cleaned[: self.num_queries] or [question]

    async def _parallel_retrieve(
        self,
        *,
        queries: list[str],
        stream: StreamBus,
        context: UnifiedContext,
    ) -> list[dict[str, Any]]:
        async def _one(query: str, index: int) -> dict[str, Any]:
            trace_call_id = new_call_id(f"solve-retrieve-{index}")
            retrieve_meta = build_trace_metadata(
                call_id=trace_call_id,
                phase="planning",
                label=f"{self._t('labels.retrieve', default='Retrieve')} {index}",
                call_kind="rag_retrieval",
                trace_id=trace_call_id,
                trace_role="retrieve",
                trace_group="retrieve",
                query=query,
                tool_name="rag",
            )
            try:
                result = await execute_tool_call(
                    registry=self.registry,
                    tool_name="rag",
                    tool_args={"query": query, "kb_name": self.kb_name, "mode": "hybrid"},
                    stream=stream,
                    source=SOURCE,
                    stage="planning",
                    retrieve_meta=retrieve_meta,
                    empty_tool_result_message=self._t("notices.empty_tool_result"),
                    start_retrieval_message=self._t(
                        "notices.start_retrieval", default="Starting retrieval"
                    ),
                    retrieve_label=self._t("labels.retrieve", default="Retrieve"),
                    unknown_error_message_factory=lambda tn: self._t(
                        "notices.tool_unknown_error",
                        tool=tn,
                        default=f"Error executing {tn}.",
                    ),
                )
                return {"query": query, "answer": result.get("result_text", "")}
            except Exception as exc:
                logger.warning("Retrieval failed for query %r: %s", query[:60], exc)
                return {"query": query, "answer": ""}

        return await asyncio.gather(*[_one(q, i + 1) for i, q in enumerate(queries)])

    async def _aggregate_retrieval_results(
        self,
        *,
        retrievals: list[dict[str, Any]],
        stream: StreamBus,
        client: Any,
    ) -> str:
        sections: list[str] = []
        total_chars = 0
        for item in retrievals:
            answer = (item.get("answer") or "").strip()
            if not answer:
                continue
            clipped = answer[:MAX_CHARS_PER_RETRIEVAL]
            if total_chars + len(clipped) > MAX_AGGREGATE_INPUT_CHARS:
                clipped = clipped[: max(0, MAX_AGGREGATE_INPUT_CHARS - total_chars)]
            if clipped:
                sections.append(f"=== Source: {item.get('query', '?')} ===\n{clipped}")
                total_chars += len(clipped)
        if not sections:
            return self._t("empty.no_kb_retrieved")
        raw_text = "\n\n".join(sections)

        system_prompt = self._t("pre_retrieve.aggregate.system")
        user_prompt = self._t(
            "pre_retrieve.aggregate.user_template",
            raw_retrieval_text=raw_text,
        )
        messages = self._build_system_user_messages(system_prompt, user_prompt)
        iter_meta = self._build_simple_trace_meta(
            call_id_root="solve-aggregate",
            label=self._t("labels.aggregate", default="Aggregate knowledge"),
            stage="planning",
            call_kind="llm_planning",
            trace_role="plan",
            trace_group="plan",
        )
        step = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_SUMMARY,
            stream=stream,
            stage="planning",
            iter_meta=iter_meta,
            max_tokens=PRE_RETRIEVE_MAX_TOKENS,
        )
        return step.text.strip() or raw_text

    # ------------------------------------------------------------------
    # Phase 1: plan
    # ------------------------------------------------------------------
    async def _plan(
        self,
        *,
        question: str,
        retrieved_context: str,
        memory_context: str,
        conversation_context: str,
        replan_reason: str | None,
        previous_attempt: list[StepFinish],
        attempt_index: int,
        image_attachments: list[Attachment],
        stream: StreamBus,
        client: Any,
    ) -> Plan:
        system_prompt = self._t("plan.system")
        user_prompt = self._t(
            "plan.user_template",
            question=question,
            retrieved_context=retrieved_context or self._t("empty.no_kb_retrieved"),
            memory_context=memory_context or self._t("empty.no_memory"),
            conversation_context=conversation_context or self._t("empty.no_conversation"),
            previous_attempt=self._render_step_finishes(previous_attempt)
            if previous_attempt
            else self._t("empty.no_previous_attempt"),
            replan_reason=(replan_reason or "").strip() or self._t("empty.no_previous_attempt"),
        )
        messages = self._build_system_user_messages(
            system_prompt, user_prompt, image_attachments=image_attachments
        )
        is_replan = replan_reason is not None
        label = self._t(
            "labels.replan" if is_replan else "labels.plan",
            default="Replan" if is_replan else "Plan",
        )
        # ``call_kind=llm_planning`` + ``trace_role=plan`` is what the
        # frontend's TracePanels.tsx renders as the "Plan / 计划" card; the
        # default ``llm_reasoning`` / ``thought`` pair would show "Thought /
        # 思考" which misreads the phase.
        iter_meta = self._build_simple_trace_meta(
            call_id_root=f"solve-plan-{attempt_index}",
            label=label,
            stage="planning",
            call_kind="llm_planning",
            trace_role="plan",
            trace_group="plan",
        )
        step = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_PLAN,
            stream=stream,
            stage="planning",
            iter_meta=iter_meta,
            max_tokens=PRE_RETRIEVE_MAX_TOKENS,
        )
        return self._parse_plan(step.text)

    def _parse_plan(self, raw: str) -> Plan:
        data = parse_json_response(raw, logger_instance=logger, fallback={})
        if not isinstance(data, dict) or not data:
            return Plan(
                analysis="Failed to parse plan; using single-step fallback.",
                steps=[PlanStep(id="S1", goal="Answer the question directly")],
            )
        analysis = str(data.get("analysis", "") or "")
        steps: list[PlanStep] = []
        for i, raw_step in enumerate(data.get("steps") or []):
            if not isinstance(raw_step, dict):
                continue
            step_id = str(raw_step.get("id") or f"S{i + 1}").strip() or f"S{i + 1}"
            goal = str(raw_step.get("goal") or "").strip()
            if not goal:
                continue
            steps.append(PlanStep(id=step_id, goal=goal))
        if not steps:
            steps = [PlanStep(id="S1", goal="Answer the question")]
        return Plan(analysis=analysis, steps=steps)

    # ------------------------------------------------------------------
    # Phase 2: solve one step
    # ------------------------------------------------------------------
    async def _solve_step(
        self,
        *,
        step: PlanStep,
        step_index: int,
        total_steps: int,
        plan: Plan,
        question: str,
        retrieved_context: str,
        previous_finishes: list[StepFinish],
        memory_context: str,
        conversation_context: str,
        image_attachments: list[Attachment],
        context: UnifiedContext,
        stream: StreamBus,
        client: Any,
    ) -> LoopOutcome:
        tool_schemas = self._build_llm_tool_schemas() if self._use_native_tools() else None
        system_prompt = self._build_step_system_prompt(
            step=step,
            step_index=step_index,
            total_steps=total_steps,
        )
        user_prompt = self._t(
            "solve_step.user_template",
            question=question,
            plan_summary=self._render_plan_summary(plan),
            step_id=step.id,
            step_goal=step.goal,
            previous_finishes=self._render_step_finishes(previous_finishes)
            if previous_finishes
            else self._t("empty.no_step_sections"),
            memory_context=memory_context or self._t("empty.no_memory"),
            conversation_context=conversation_context or self._t("empty.no_conversation"),
        )
        messages = self._build_system_user_messages(
            system_prompt, user_prompt, image_attachments=image_attachments
        )

        host = _StepLoopHost(
            pipeline=self,
            step=step,
            stream=stream,
            context=context,
            client=client,
        )
        return await run_agentic_loop(
            initial_messages=messages,
            protocol=_PROTOCOL_STEP,
            client=client,
            model=self.model,
            completion_kwargs=self._completion_kwargs(DEFAULT_MAX_TOKENS),
            binding=self.binding,
            tool_schemas=tool_schemas,
            stream=stream,
            source=SOURCE,
            stage="reasoning",
            max_iterations=self.max_iterations_per_step,
            host=host,
            usage=self.usage,
            stream_body_live=True,
            eager_sub_trace=True,
        )

    def _build_step_system_prompt(
        self,
        *,
        step: PlanStep,
        step_index: int,
        total_steps: int,
    ) -> str:
        tone_key = self._tone_key(step_index, total_steps)
        tone_guidance = self._t(f"solve_step.tone.{tone_key}")
        tool_list = (
            self.registry.build_prompt_text(
                self._resolved_tools(),
                format="list_with_usage",
                language=self.language,
            )
            or self._fallback_empty_tool_list()
        )
        kb_note = self._kb_system_note()
        system = self._t(
            "solve_step.system",
            step_index_human=step_index + 1,
            total_steps=total_steps,
            tone_guidance=tone_guidance,
            kb_note=kb_note,
            tool_list=tool_list,
        )
        return append_language_directive(system, self.language)

    @staticmethod
    def _tone_key(step_index: int, total_steps: int) -> str:
        if total_steps <= 1:
            return "only"
        if step_index == 0:
            return "first"
        if step_index == total_steps - 1:
            return "last"
        return "middle"

    # ------------------------------------------------------------------
    # Forced-finish per step (host hook for max-iter exhaustion)
    # ------------------------------------------------------------------
    async def _force_finish_step(
        self,
        *,
        client: Any,
        messages: list[dict[str, Any]],
        stream: StreamBus,
        start_iteration: int,
        step: PlanStep,
    ) -> tuple[str, bool, int]:
        calls = 0
        messages.append({"role": "user", "content": self._t("protocol.force_finish")})
        await stream.progress(
            self._t("notices.max_iterations_reached"),
            source=SOURCE,
            stage="reasoning",
            metadata={"trace_kind": "warning"},
        )
        for attempt in range(FINALIZATION_REPAIR_ATTEMPTS):
            iter_meta = self._build_simple_trace_meta(
                call_id_root=f"solve-{step.id}-force-{start_iteration + attempt}",
                label=self._t("labels.reasoning", default="Reasoning"),
                stage="reasoning",
                step_id=step.id,
            )
            step_result = await self._run_labeled_step(
                client=client,
                messages=messages,
                tool_schemas=None,
                protocol=LabelProtocol(
                    allowed=(LABEL_FINISH,),
                    terminal=frozenset({LABEL_FINISH}),
                    intermediate=frozenset(),
                    final=frozenset({LABEL_FINISH}),
                    tool_label=None,
                ),
                stream=stream,
                stage="reasoning",
                iter_meta=iter_meta,
            )
            calls += 1
            if step_result.label == LABEL_FINISH and not find_inline_labels(
                step_result.text, allowed_labels=_PROTOCOL_STEP.allowed
            ):
                final_meta = build_trace_metadata(
                    call_id=new_call_id(f"solve-{step.id}-final"),
                    phase="reasoning",
                    label=self._t("labels.solve_step", default="Solve step") + f" {step.id}",
                    call_kind="llm_final_response",
                    trace_id=f"solve-{step.id}-final",
                    trace_role="response",
                    trace_group="stage",
                    step_id=step.id,
                )
                await self._emit_step_final(stream, step_result.text, final_meta)
                return step_result.text, True, calls
            messages.append({"role": "assistant", "content": step_result.text[:500]})
            messages.append({"role": "user", "content": self._t("protocol.force_finish_repair")})
        return self._t("protocol.fallback_final"), False, calls

    async def _emit_step_final(
        self,
        stream: StreamBus,
        text: str,
        final_meta: dict[str, Any],
    ) -> None:
        if not text:
            return
        await stream.content(
            text,
            source=SOURCE,
            stage="reasoning",
            metadata=merge_trace_metadata(final_meta, {"trace_kind": "llm_output"}),
        )

    async def _emit_section_break(self, stream: StreamBus) -> None:
        """Emit a blank-line content event between live-streamed sections.

        Without this, the next section's first streamed chunk concatenates
        directly onto the previous section's last chunk in the chat bubble
        — a leading ``##`` would render as inline text instead of a heading,
        and consecutive paragraphs would collapse into one. Emitted after
        every step FINISH (before the explain triage) and after every
        deep-explain expansion.

        ``section_break: True`` rides on the metadata so the frontend (and
        tests) can distinguish this housekeeping event from real model
        output.
        """
        break_id = new_call_id("solve-section-break")
        meta = build_trace_metadata(
            call_id=break_id,
            phase="reasoning",
            label="",
            call_kind="llm_final_response",
            trace_id=break_id,
            trace_role="response",
            trace_group="stage",
        )
        await stream.content(
            "\n\n",
            source=SOURCE,
            stage="reasoning",
            metadata=merge_trace_metadata(
                meta, {"trace_kind": "llm_output", "section_break": True}
            ),
        )

    # ------------------------------------------------------------------
    # Phase 2.5: explain judge + deep explain
    # ------------------------------------------------------------------
    async def _maybe_explain_step(
        self,
        *,
        step: PlanStep,
        question: str,
        finish_text: str,
        image_attachments: list[Attachment],
        stream: StreamBus,
        client: Any,
    ) -> str:
        """After a step's FINISH content has streamed, decide whether to
        append a deeper explanation, and if so stream it live under the
        FINISH section. Returns the explain text (empty when SKIPped or
        when something fails)."""
        if not finish_text:
            return ""
        try:
            should_explain, explain_focus = await self._judge_explain(
                step=step,
                question=question,
                finish_text=finish_text,
                image_attachments=image_attachments,
                stream=stream,
                client=client,
            )
        except Exception as exc:
            logger.warning("Explain triage failed for step %s: %s", step.id, exc)
            return ""
        if not should_explain:
            return ""
        try:
            return await self._run_explain(
                step=step,
                question=question,
                finish_text=finish_text,
                explain_focus=explain_focus,
                image_attachments=image_attachments,
                stream=stream,
                client=client,
            )
        except Exception as exc:
            logger.warning("Deep explain failed for step %s: %s", step.id, exc)
            return ""

    async def _judge_explain(
        self,
        *,
        step: PlanStep,
        question: str,
        finish_text: str,
        image_attachments: list[Attachment],
        stream: StreamBus,
        client: Any,
    ) -> tuple[bool, str]:
        """Run the triage LLM call. Returns ``(should_explain, focus)``;
        ``focus`` is a one-sentence hint of what to deepen, empty when
        the triage says SKIP."""
        system_prompt = self._t("explain_judge.system")
        user_prompt = self._t(
            "explain_judge.user_template",
            question=question,
            step_id=step.id,
            step_goal=step.goal,
            finish_text=finish_text,
        )
        if not system_prompt or not user_prompt:
            return False, ""
        messages = self._build_system_user_messages(
            system_prompt, user_prompt, image_attachments=image_attachments
        )
        iter_meta = self._build_simple_trace_meta(
            call_id_root=f"solve-{step.id}-explain-judge",
            label=self._t("labels.explain_judge", default="Explain check"),
            stage="reasoning",
            call_kind="llm_planning",
            trace_role="plan",
            trace_group="stage",
            step_id=step.id,
        )
        result = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_EXPLAIN_JUDGE,
            stream=stream,
            stage="reasoning",
            iter_meta=iter_meta,
            max_tokens=EXPLAIN_JUDGE_MAX_TOKENS,
        )
        if result.label == LABEL_EXPLAIN:
            focus = result.text.strip()
            return True, focus
        # SKIP or LABEL_UNKNOWN both fall back to "no explanation" so a
        # protocol miss never adds dubious content under the step.
        return False, ""

    async def _run_explain(
        self,
        *,
        step: PlanStep,
        question: str,
        finish_text: str,
        explain_focus: str,
        image_attachments: list[Attachment],
        stream: StreamBus,
        client: Any,
    ) -> str:
        """Stream a deeper explanation directly under the step's FINISH
        content. Returns the explain text so the caller can fold it into
        ``StepFinish.text`` for downstream context + final-response join."""
        system_prompt = self._t("explain.system")
        user_prompt = self._t(
            "explain.user_template",
            question=question,
            step_id=step.id,
            step_goal=step.goal,
            finish_text=finish_text,
            explain_focus=explain_focus
            or self._t(
                "empty.no_explain_focus", default="(no specific focus — pick the most useful angle)"
            ),
        )
        if not system_prompt or not user_prompt:
            return ""
        messages = self._build_system_user_messages(
            system_prompt, user_prompt, image_attachments=image_attachments
        )
        iter_meta = self._build_simple_trace_meta(
            call_id_root=f"solve-{step.id}-explain",
            label=self._t("labels.explain", default="Deep explain"),
            stage="reasoning",
            call_kind="llm_final_response",
            trace_role="response",
            trace_group="stage",
            step_id=step.id,
        )
        final_call_id = new_call_id(f"solve-{step.id}-explain-final")
        final_meta = build_trace_metadata(
            call_id=final_call_id,
            phase="reasoning",
            label=self._t("labels.explain", default="Deep explain"),
            call_kind="llm_final_response",
            trace_id=final_call_id,
            trace_role="response",
            trace_group="stage",
            step_id=step.id,
        )
        # Wrap the deep-explain section in a default-open <details> block so
        # the user can fold it away once they've absorbed the FINISH content.
        # The opening + closing tags are emitted as their own content events
        # (so the live stream sees them in order with the LLM body in between)
        # AND folded into the returned text (so the persisted response /
        # downstream synthesize input keeps the same collapsible structure).
        summary_label = self._t("labels.explain_summary", default="Deep explanation")
        summary_text = f"{summary_label}: {explain_focus}" if explain_focus else summary_label
        details_open = f"<details open>\n<summary>{summary_text}</summary>\n\n"
        details_close = "\n\n</details>"
        wrapper_meta = merge_trace_metadata(
            final_meta,
            {"trace_kind": "llm_output", "details_wrapper": True},
        )
        await stream.content(
            details_open,
            source=SOURCE,
            stage="reasoning",
            metadata=wrapper_meta,
        )
        result = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_EXPLAIN,
            stream=stream,
            stage="reasoning",
            iter_meta=iter_meta,
            max_tokens=EXPLAIN_MAX_TOKENS,
            final_meta=final_meta,
        )
        await stream.content(
            details_close,
            source=SOURCE,
            stage="reasoning",
            metadata=wrapper_meta,
        )
        # Section break so the next streamed section (next step's FINISH
        # or synthesize) starts on a fresh markdown block.
        await self._emit_section_break(stream)
        return f"{details_open}{result.text.strip()}{details_close}"

    # ------------------------------------------------------------------
    # Phase 3: synthesize
    # ------------------------------------------------------------------
    async def _synthesize(
        self,
        *,
        question: str,
        step_finishes: list[StepFinish],
        conversation_context: str,
        stream: StreamBus,
        client: Any,
    ) -> str:
        system_prompt = self._t("synthesize.system")
        user_prompt = self._t(
            "synthesize.user_template",
            question=question,
            step_finishes=self._render_step_finishes(step_finishes)
            if step_finishes
            else self._t("empty.no_step_sections"),
            conversation_context=conversation_context or self._t("empty.no_conversation"),
        )
        messages = self._build_system_user_messages(system_prompt, user_prompt)
        # Two metadata bundles: ``iter_meta`` would scope a reasoning
        # sub-trace card (synthesize doesn't open one — its label is in
        # ``final_labels``), and ``final_meta`` scopes the body content
        # so the chat bubble streams chunk-by-chunk via
        # :func:`run_labeled_step` (``stream_body_live`` semantics).
        synth_label = self._t("labels.synthesize", default="Synthesize")
        iter_meta = self._build_simple_trace_meta(
            call_id_root="solve-synthesize",
            label=synth_label,
            stage="writing",
            call_kind="llm_final_response",
            trace_role="response",
            trace_group="stage",
        )
        final_call_id = new_call_id("solve-synthesize-final")
        final_meta = build_trace_metadata(
            call_id=final_call_id,
            phase="writing",
            label=synth_label,
            call_kind="llm_final_response",
            trace_id=final_call_id,
            trace_role="response",
            trace_group="stage",
        )
        step = await self._run_labeled_step(
            client=client,
            messages=messages,
            tool_schemas=None,
            protocol=_PROTOCOL_SYNTHESIZE,
            stream=stream,
            stage="writing",
            iter_meta=iter_meta,
            max_tokens=SYNTHESIZE_MAX_TOKENS,
            final_meta=final_meta,
        )
        return step.text.strip()

    # ------------------------------------------------------------------
    # Tool integration (mirrors chat's pattern)
    # ------------------------------------------------------------------
    def _resolved_tools(self) -> list[str]:
        """Filter the user's enabled_tools by what the registry actually has,
        and ensure ``rag`` is mounted when a KB is attached."""
        resolved: list[str] = []
        for tool in self.registry.get_enabled(self.enabled_tools):
            if tool.name in resolved:
                continue
            resolved.append(tool.name)
        if self.kb_name and self._tool_in_registry("rag") and "rag" not in resolved:
            resolved.append("rag")
        return resolved

    def _build_llm_tool_schemas(self) -> list[dict[str, Any]]:
        schemas = self.registry.build_openai_schemas(self._resolved_tools())
        kb_choices = [self.kb_name] if self.kb_name else []
        for schema in schemas:
            function = schema.get("function") if isinstance(schema, dict) else None
            if not isinstance(function, dict):
                continue
            parameters = function.get("parameters")
            if not isinstance(parameters, dict):
                continue
            properties = parameters.get("properties") or {}
            if function.get("name") == "rag" and isinstance(properties, dict):
                if isinstance(properties.get("query"), dict):
                    properties["query"].setdefault("minLength", 1)
                kb_schema = properties.get("kb_name")
                if isinstance(kb_schema, dict) and kb_choices:
                    kb_schema["enum"] = kb_choices
            parameters["additionalProperties"] = False
        return schemas

    def _augment_tool_kwargs(
        self,
        tool_name: str,
        args: dict[str, Any],
        context: UnifiedContext,
    ) -> dict[str, Any]:
        kwargs = dict(args)
        turn_id = str(context.metadata.get("turn_id", "") or "").strip()
        task_dir = None
        if turn_id:
            task_dir = get_path_service().get_task_workspace("deep_solve", turn_id)
        if tool_name == "rag":
            kwargs.setdefault("mode", "hybrid")
            if self.kb_name:
                kwargs.setdefault("kb_name", self.kb_name)
        elif tool_name == "code_execution":
            kwargs.setdefault("intent", context.user_message)
            kwargs.setdefault("timeout", 30)
            kwargs.setdefault("feature", "deep_solve")
            kwargs.setdefault("session_id", context.session_id)
            kwargs.setdefault("turn_id", turn_id)
            if task_dir is not None:
                kwargs.setdefault("workspace_dir", str(task_dir / "code_runs"))
        elif tool_name in {"reason", "brainstorm"}:
            kwargs.setdefault("context", context.user_message)
        elif tool_name == "web_search":
            kwargs.setdefault("query", context.user_message)
            if task_dir is not None:
                kwargs.setdefault("output_dir", str(task_dir / "web_search"))
        return kwargs

    def _retrieve_trace_metadata(
        self,
        tool_meta: dict[str, Any],
        *,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> dict[str, Any] | None:
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

    def _use_native_tools(self) -> bool:
        return bool(self._resolved_tools()) and can_use_native_tool_calling(
            binding=self.binding, model=self.model
        )

    def _tool_in_registry(self, name: str) -> bool:
        try:
            return self.registry.get(name) is not None
        except Exception:
            return False

    # ------------------------------------------------------------------
    # LLM call helpers
    # ------------------------------------------------------------------
    def _build_client(self) -> Any:
        return build_openai_client(self.client_config)

    def _completion_kwargs(self, max_tokens: int) -> dict[str, Any]:
        return build_completion_kwargs(
            temperature=self._temperature,
            model=self.model,
            max_tokens=max_tokens,
            binding=self.binding,
            reasoning_effort=self.reasoning_effort,
        )

    async def _run_labeled_step(
        self,
        *,
        client: Any,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]] | None,
        protocol: LabelProtocol,
        stream: StreamBus,
        stage: str,
        iter_meta: dict[str, Any],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        final_meta: dict[str, Any] | None = None,
        eager_sub_trace: bool = True,
    ) -> LabeledStepResult:
        """Solve-flavored thin wrapper over :func:`run_labeled_step`.

        Pass ``final_meta`` (a trace-metadata dict) to make a final-label
        body stream chunk-by-chunk into ``stream.content``. This is how
        :meth:`_synthesize` makes its ``FINISH`` answer feel typewriter-y
        instead of slamming the whole text into the bubble at once.

        ``eager_sub_trace`` defaults to ``True`` for solve so each phase's
        trace card appears immediately when the LLM call begins, closing
        the visual gap during time-to-first-token between calls.
        """
        return await run_labeled_step(
            client=client,
            model=self.model,
            messages=messages,
            completion_kwargs=self._completion_kwargs(max_tokens),
            tool_schemas=tool_schemas,
            allowed_labels=protocol.allowed,
            final_labels=protocol.final,
            tool_label=protocol.tool_label,
            stream=stream,
            source=SOURCE,
            stage=stage,
            iter_meta=iter_meta,
            binding=self.binding,
            usage=self.usage,
            final_meta=final_meta,
            eager_sub_trace=eager_sub_trace,
        )

    # ------------------------------------------------------------------
    # Message + trace assembly
    # ------------------------------------------------------------------
    def _build_system_user_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        image_attachments: list[Attachment] | None = None,
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if image_attachments:
            mm_result = prepare_multimodal_messages(
                messages, image_attachments, binding=self.binding, model=self.model
            )
            return mm_result.messages
        return messages

    def _build_simple_trace_meta(
        self,
        *,
        call_id_root: str,
        label: str,
        stage: str,
        call_kind: str = "llm_reasoning",
        trace_role: str = "thought",
        trace_group: str = "stage",
        **extra: Any,
    ) -> dict[str, Any]:
        """Construct trace metadata for a sub-trace card.

        ``call_kind`` + ``trace_role`` drive the frontend's panel title (see
        ``web/components/chat/home/TracePanels.tsx``). Defaults emit a generic
        "Reasoning / 思考" card; callers override for ``Plan``, ``Retrieve``,
        etc.
        """
        call_id = new_call_id(call_id_root)
        return build_trace_metadata(
            call_id=call_id,
            phase=stage,
            label=label,
            call_kind=call_kind,
            trace_id=call_id,
            trace_role=trace_role,
            trace_group=trace_group,
            **extra,
        )

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _render_plan_summary(self, plan: Plan) -> str:
        if not plan.steps:
            return "(empty plan)"
        lines = []
        if plan.analysis:
            lines.append(f"Analysis: {plan.analysis}")
        for step in plan.steps:
            lines.append(f"  - [{step.id}] {step.goal}")
        return "\n".join(lines)

    def _render_step_finishes(self, finishes: list[StepFinish]) -> str:
        if not finishes:
            return self._t("empty.no_step_sections")
        blocks = []
        for finish in finishes:
            blocks.append(f"### [{finish.step.id}] {finish.step.goal}\n\n{finish.text}")
        return "\n\n".join(blocks)

    def _compose_full_response(
        self,
        step_finishes: list[StepFinish],
        synthesis_text: str,
    ) -> str:
        """Join the step sections + synthesis into one string for the
        ``stream.result.response`` payload (the per-section content already
        streamed live as ``stream.content`` events)."""
        parts = [finish.text.strip() for finish in step_finishes if finish.text.strip()]
        synthesis = (synthesis_text or "").strip()
        if synthesis:
            parts.append(synthesis)
        return "\n\n".join(parts)

    def _kb_system_note(self) -> str:
        if not self.kb_name:
            return ""
        if self.language == "zh":
            return f"用户已挂载知识库：{self.kb_name}。调用 rag 时，kb_name 必须填这个名称。"
        return (
            f"Attached knowledge bases: {self.kb_name}. When calling rag, kb_name "
            f"must be {self.kb_name!r}."
        )

    def _fallback_empty_tool_list(self) -> str:
        return "- 无" if self.language == "zh" else "- none"

    # ------------------------------------------------------------------
    # YAML lookup
    # ------------------------------------------------------------------
    def _t(self, key: str, default: str = "", **kwargs: Any) -> str:
        """Look up a YAML-loaded prompt by dotted key (same contract as the
        chat pipeline's ``_t``)."""
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


# ---------------------------------------------------------------------------
# Per-step LoopHost
# ---------------------------------------------------------------------------


class _StepLoopHost:
    """Binds a ``SolvePipeline`` + current step + stream/context/client so the
    generic loop primitive can call back for chat-style hooks scoped to one
    solve step."""

    def __init__(
        self,
        *,
        pipeline: SolvePipeline,
        step: PlanStep,
        stream: StreamBus,
        context: UnifiedContext,
        client: Any,
    ) -> None:
        self._pipeline = pipeline
        self._step = step
        self._stream = stream
        self._context = context
        self._client = client

    async def guard_context_window(self, messages: list[dict[str, Any]]) -> None:
        # Solve doesn't run its own context-window guard for v1 — each step's
        # loop is bounded by ``max_iterations_per_step`` and the messages
        # buffer is reset per step, so it never grows like chat's.
        return

    def build_iteration_trace_meta(self, iteration: int) -> tuple[dict[str, Any], dict[str, Any]]:
        iter_call_id = new_call_id(f"solve-{self._step.id}-iter-{iteration}")
        iter_meta = build_trace_metadata(
            call_id=iter_call_id,
            phase="reasoning",
            label=self._pipeline._t("labels.reasoning", default="Reasoning"),
            call_kind="llm_reasoning",
            trace_id=iter_call_id,
            trace_role="thought",
            trace_group="stage",
            step_id=self._step.id,
        )
        final_call_id = new_call_id(f"solve-{self._step.id}-final")
        final_meta = build_trace_metadata(
            call_id=final_call_id,
            phase="reasoning",
            label=f"{self._pipeline._t('labels.solve_step', default='Solve step')} {self._step.id}",
            call_kind="llm_final_response",
            trace_id=final_call_id,
            trace_role="response",
            trace_group="stage",
            step_id=self._step.id,
        )
        return iter_meta, final_meta

    async def dispatch_tools(
        self,
        *,
        iteration: int,
        tool_calls: list[dict[str, Any]],
    ) -> DispatchOutcome:
        too_many = None
        if len(tool_calls) > MAX_PARALLEL_TOOL_CALLS:
            too_many = self._pipeline._t(
                "notices.too_many_tool_calls",
                requested=len(tool_calls),
                limit=MAX_PARALLEL_TOOL_CALLS,
            )
        return await dispatch_tool_calls(
            tool_calls=tool_calls,
            context=self._context,
            stream=self._stream,
            source=SOURCE,
            stage="reasoning",
            iteration_index=iteration,
            registry=self._pipeline.registry,
            kwarg_augmenter=self._pipeline._augment_tool_kwargs,
            retrieve_meta_factory=lambda meta, tn, ta: self._pipeline._retrieve_trace_metadata(
                meta, tool_name=tn, tool_args=ta
            ),
            tool_call_label=self._pipeline._t("labels.tool_call", default="Tool call"),
            retrieve_label=self._pipeline._t("labels.retrieve", default="Retrieve"),
            empty_tool_result_message=self._pipeline._t("notices.empty_tool_result"),
            start_retrieval_message=self._pipeline._t(
                "notices.start_retrieval", default="Starting retrieval"
            ),
            too_many_tool_calls_message=too_many,
            unknown_error_message_factory=lambda tn: self._pipeline._t(
                "notices.tool_unknown_error",
                tool=tn,
                default=f"Error executing {tn}.",
            ),
            trace_id_prefix=f"solve-{self._step.id}-iter",
        )

    async def resolve_pause(self, dispatch: DispatchOutcome) -> bool:
        # Solve does not currently surface ask_user. If a tool ever requests
        # pause we fall through to terminate so the turn cleanly closes.
        return False

    async def emit_terminator(self, payload: dict[str, Any] | None) -> None:
        if not payload:
            return
        content = str(payload.get("content") or "").strip()
        if not content:
            return
        final_meta = build_trace_metadata(
            call_id=new_call_id(f"solve-{self._step.id}-final"),
            phase="reasoning",
            label=f"{self._pipeline._t('labels.solve_step', default='Solve step')} {self._step.id}",
            call_kind="llm_final_response",
            trace_id=f"solve-{self._step.id}-final",
            trace_role="response",
            trace_group="stage",
            step_id=self._step.id,
        )
        await self._stream.content(
            content,
            source=SOURCE,
            stage="reasoning",
            metadata=merge_trace_metadata(final_meta, {"trace_kind": "llm_output"}),
        )

    async def emit_final(self, text: str, final_meta: dict[str, Any]) -> None:
        await self._pipeline._emit_step_final(self._stream, text, final_meta)

    def assistant_message_with_tool_calls(
        self,
        *,
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

    def protocol_retry_notice(self) -> str:
        return self._pipeline._t(
            "notices.protocol_retry",
            default="The model violated the action-label protocol; retrying.",
        )

    def protocol_repair_message(self, violation: str) -> str:
        return self._pipeline._t(
            f"protocol.{violation}",
            default=f"Protocol violation: {violation}.",
        )

    async def force_finalize(
        self,
        *,
        messages: list[dict[str, Any]],
        start_iteration: int,
    ) -> tuple[str, bool, int]:
        return await self._pipeline._force_finish_step(
            client=self._client,
            messages=messages,
            stream=self._stream,
            start_iteration=start_iteration,
            step=self._step,
        )


# Awaitable re-export so the host's force_finalize / dispatch_tools return
# types resolve cleanly when callers type-check this module in isolation.
_ = Awaitable  # type: ignore[assignment]
