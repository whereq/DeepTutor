"""
Visualize Capability
====================

Unified visualization capability. AnalysisAgent picks one of six render
types — svg / chartjs / mermaid / html (text-emitting, three-stage pipeline)
or manim_video / manim_image (Manim subprocess pipeline). The result
envelope carries ``render_type`` as the discriminator so the frontend can
delegate to the right viewer.
"""

from __future__ import annotations

from typing import Any

from deeptutor.capabilities._i18n import StatusI18n
from deeptutor.capabilities._shared import emit_capability_result
from deeptutor.capabilities.request_contracts import (
    VisualizeRequestConfig,
    get_capability_request_schema,
    validate_visualize_request_config,
)
from deeptutor.core.agentic.usage import UsageTracker
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import merge_trace_metadata

# Stages exposed in the manifest. The first three cover the text-emitting
# path (svg/chartjs/mermaid/html); the rest cover the manim subprocess
# path. A given turn only streams a subset of these.
_VISUALIZE_STAGES = [
    "analyzing",
    "generating",
    "reviewing",
    "concept_analysis",
    "concept_design",
    "code_generation",
    "code_retry",
    "summary",
    "render_output",
]

_MANIM_RENDER_TYPES = {"manim_video", "manim_image"}


class VisualizeCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="visualize",
        description=(
            "Generate SVG, Chart.js, Mermaid, interactive HTML, or Manim "
            "animation/storyboard visualizations."
        ),
        stages=_VISUALIZE_STAGES,
        tools_used=[],
        cli_aliases=["visualize", "viz"],
        request_schema=get_capability_request_schema("visualize"),
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        from deeptutor.agents.visualize.pipeline import VisualizePipeline
        from deeptutor.agents.visualize.utils import (
            build_fallback_html,
            is_valid_html_document,
        )
        from deeptutor.capabilities._answer_now import extract_answer_now_context
        from deeptutor.services.llm.config import get_llm_config

        request_config = validate_visualize_request_config(context.config_overrides)
        render_mode = request_config.render_mode
        i18n = StatusI18n(self.name, context.language)

        llm_config_for_usage = get_llm_config()
        usage = UsageTracker(model=getattr(llm_config_for_usage, "model", None))

        answer_now_payload = extract_answer_now_context(context)
        if answer_now_payload is not None:
            # Manim takes ~30-90s even on the fast path; answer-now's point is
            # to skip slow analysis when the user is impatient, so we redirect
            # explicit manim answer-now requests to the full path. The text
            # paths keep their dedicated fast-path implementation.
            if render_mode in _MANIM_RENDER_TYPES:
                pass  # fall through to the full manim path below
            else:
                await self._run_answer_now(
                    context, stream, answer_now_payload, usage=usage, i18n=i18n
                )
                return

        llm_config = get_llm_config()
        history_context = str(context.metadata.get("conversation_context_text", "") or "").strip()

        pipeline = VisualizePipeline(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=llm_config.api_version,
            language=context.language,
            trace_callback=self._build_trace_bridge(stream, i18n=i18n),
        )

        # Stage 1: Analyze (routing decision)
        async with stream.stage("analyzing", source=self.name):
            await stream.thinking(
                i18n.t("analyzing", "Analyzing visualization requirements..."),
                source=self.name,
                stage="analyzing",
            )
            analysis = await pipeline.run_analysis(
                user_input=context.user_message,
                history_context=history_context,
                render_mode=render_mode,
                attachments=context.attachments,
            )
            await stream.progress(
                message=i18n.t(
                    "render_type_detected",
                    f"Render type: {analysis.render_type} — {analysis.description}",
                    render_type=analysis.render_type,
                    description=analysis.description,
                ),
                source=self.name,
                stage="analyzing",
            )

        # Branch: manim path takes over completely after the analysis stage,
        # using its own multi-agent pipeline + Manim subprocess.
        if analysis.render_type in _MANIM_RENDER_TYPES:
            await self._run_manim_path(
                context=context,
                stream=stream,
                render_type=analysis.render_type,
                visualize_config=request_config,
                history_context=history_context,
                usage=usage,
                i18n=i18n,
            )
            return

        # Stage 2: Generate code
        async with stream.stage("generating", source=self.name):
            await stream.thinking(
                i18n.t("generating", "Generating visualization code..."),
                source=self.name,
                stage="generating",
            )
            code = await pipeline.run_code_generation(
                user_input=context.user_message,
                history_context=history_context,
                analysis=analysis,
            )
            await stream.progress(
                message=i18n.t("code_generated", "Code generated."),
                source=self.name,
                stage="generating",
            )

        # Stage 3: Review & optimise
        async with stream.stage("reviewing", source=self.name):
            if analysis.render_type == "html":
                # Skip the LLM review pass for html — it would cost another
                # 30-60s on a 10k-token document with negligible quality gain.
                # Instead, do a local sanity check and fall back to a minimal
                # template if the model returned something unrenderable.
                from deeptutor.agents.visualize.models import ReviewResult

                if is_valid_html_document(code):
                    final_code = code
                    review = ReviewResult(
                        optimized_code=final_code,
                        changed=False,
                        review_notes="Skipped LLM review for html render_type.",
                    )
                    await stream.progress(
                        message=i18n.t(
                            "html_ready_review_skipped",
                            "HTML page ready (review skipped).",
                        ),
                        source=self.name,
                        stage="reviewing",
                    )
                else:
                    final_code = build_fallback_html(
                        title=analysis.description or "Visualization",
                        summary=analysis.data_description,
                        note="The model did not return a renderable HTML document.",
                    )
                    review = ReviewResult(
                        optimized_code=final_code,
                        changed=True,
                        review_notes="Used fallback HTML template.",
                    )
                    await stream.progress(
                        message=i18n.t(
                            "html_invalid_fallback",
                            "HTML did not validate; using fallback template.",
                        ),
                        source=self.name,
                        stage="reviewing",
                    )
            else:
                await stream.thinking(
                    i18n.t("reviewing", "Reviewing and optimizing code..."),
                    source=self.name,
                    stage="reviewing",
                )
                review = await pipeline.run_review(
                    user_input=context.user_message,
                    analysis=analysis,
                    code=code,
                )
                final_code = review.optimized_code
                if review.changed:
                    await stream.progress(
                        message=i18n.t(
                            "code_optimized",
                            f"Code optimized: {review.review_notes}",
                            notes=review.review_notes,
                        ),
                        source=self.name,
                        stage="reviewing",
                    )
                else:
                    await stream.progress(
                        message=i18n.t(
                            "code_no_changes",
                            "Code looks good — no changes needed.",
                        ),
                        source=self.name,
                        stage="reviewing",
                    )

        # Emit final content as a fenced code block for the chat area
        if analysis.render_type == "svg":
            lang_tag = "svg"
        elif analysis.render_type == "mermaid":
            lang_tag = "mermaid"
        elif analysis.render_type == "html":
            lang_tag = "html"
        else:
            lang_tag = "javascript"
        content_md = f"```{lang_tag}\n{final_code}\n```"
        await stream.content(content_md, source=self.name, stage="reviewing")

        # Structured result for the frontend viewer
        await emit_capability_result(
            stream,
            {
                "response": content_md,
                "render_type": analysis.render_type,
                "code": {
                    "language": lang_tag,
                    "content": final_code,
                },
                "analysis": analysis.model_dump(),
                "review": review.model_dump(),
            },
            source=self.name,
            usage=usage,
        )

    async def _run_manim_path(
        self,
        *,
        context: UnifiedContext,
        stream: StreamBus,
        render_type: str,
        visualize_config: VisualizeRequestConfig,
        history_context: str,
        usage: UsageTracker | None = None,
        i18n: StatusI18n | None = None,
    ) -> None:
        """
        Manim sub-pipeline. Mirrors ``MathAnimatorCapability.run`` but emits
        the final result with ``render_type`` as the discriminator so the
        unified frontend dispatcher can route to ``MathAnimatorViewer``.
        """
        import importlib.util
        import time

        if importlib.util.find_spec("manim") is None:
            raise RuntimeError(
                "Manim rendering requires optional dependencies. "
                "Install with `pip install 'deeptutor[math-animator]'` "
                "or `pip install -r requirements/math-animator.txt`."
            )

        from deeptutor.agents.math_animator.pipeline import MathAnimatorPipeline
        from deeptutor.agents.math_animator.request_config import MathAnimatorRequestConfig
        from deeptutor.core.trace import build_trace_metadata, new_call_id
        from deeptutor.services.llm.config import get_llm_config

        if i18n is None:
            i18n = StatusI18n(self.name, context.language)
        output_mode = "image" if render_type == "manim_image" else "video"
        request_config = MathAnimatorRequestConfig(
            output_mode=output_mode,  # type: ignore[arg-type]
            quality=visualize_config.quality,
            style_hint=visualize_config.style_hint,
        )

        llm_config = get_llm_config()
        pipeline = MathAnimatorPipeline(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=llm_config.api_version,
            language=context.language,
            trace_callback=self._build_trace_bridge(stream, i18n=i18n),
        )

        timings: dict[str, float] = {}
        turn_id = str(
            context.metadata.get("turn_id", "") or context.session_id or "visualize-manim"
        )
        render_call_meta = build_trace_metadata(
            call_id=new_call_id("manim-render"),
            phase="render_output",
            label="Render output",
            call_kind="math_render_output",
            trace_role="render",
            trace_kind="progress",
            output_mode=request_config.output_mode,
            quality=request_config.quality,
        )

        stage_start = time.perf_counter()
        async with stream.stage("concept_analysis", source=self.name):
            analysis = await pipeline.run_analysis(
                user_input=context.user_message,
                history_context=history_context,
                request_config=request_config,
                attachments=context.attachments,
            )
        timings["concept_analysis"] = round(time.perf_counter() - stage_start, 3)

        stage_start = time.perf_counter()
        async with stream.stage("concept_design", source=self.name):
            design = await pipeline.run_design(
                user_input=context.user_message,
                request_config=request_config,
                analysis=analysis,
            )
        timings["concept_design"] = round(time.perf_counter() - stage_start, 3)

        stage_start = time.perf_counter()
        async with stream.stage("code_generation", source=self.name):
            generated = await pipeline.run_code_generation(
                user_input=context.user_message,
                request_config=request_config,
                analysis=analysis,
                design=design,
            )
            await stream.progress(
                message=i18n.t("manim_code_prepared", "Manim code prepared."),
                source=self.name,
                stage="code_generation",
            )
        timings["code_generation"] = round(time.perf_counter() - stage_start, 3)

        async def _on_retry(retry_attempt) -> None:
            await stream.progress(
                message=i18n.t(
                    "manim_retry",
                    f"Retry {retry_attempt.attempt}: {retry_attempt.error}",
                    attempt=retry_attempt.attempt,
                    error=retry_attempt.error,
                ),
                source=self.name,
                stage="code_retry",
                metadata={**render_call_meta, "trace_layer": "raw"},
            )

        async def _on_render_progress(message: str, raw: bool) -> None:
            await stream.progress(
                message=message,
                source=self.name,
                stage="render_output",
                metadata={
                    **render_call_meta,
                    "trace_layer": "raw" if raw else "summary",
                },
            )

        async def _on_retry_status(message: str) -> None:
            await stream.progress(
                message=message,
                source=self.name,
                stage="code_retry",
                metadata={"trace_layer": "summary"},
            )

        stage_start = time.perf_counter()
        async with stream.stage("code_retry", source=self.name):
            await stream.progress(
                message=i18n.t(
                    "manim_rendering",
                    (
                        f"Rendering {request_config.output_mode} "
                        f"with quality={request_config.quality}."
                    ),
                    mode=request_config.output_mode,
                    quality=request_config.quality,
                ),
                source=self.name,
                stage="code_retry",
                metadata={**render_call_meta, "call_state": "running"},
            )
            final_code, render_result = await pipeline.run_render(
                turn_id=turn_id,
                user_input=context.user_message,
                request_config=request_config,
                initial_code=generated.code,
                on_retry=_on_retry,
                on_render_progress=_on_render_progress,
                on_retry_status=_on_retry_status,
            )
        timings["code_retry"] = round(time.perf_counter() - stage_start, 3)

        stage_start = time.perf_counter()
        async with stream.stage("summary", source=self.name):
            summary = await pipeline.run_summary(
                user_input=context.user_message,
                request_config=request_config,
                analysis=analysis,
                design=design,
                render_result=render_result,
            )
            if summary.summary_text:
                await stream.content(summary.summary_text, source=self.name, stage="summary")
        timings["summary"] = round(time.perf_counter() - stage_start, 3)

        async with stream.stage("render_output", source=self.name):
            artifact_count = len(render_result.artifacts)
            artifact_key = "manim_artifacts_one" if artifact_count == 1 else "manim_artifacts_many"
            await stream.progress(
                message=i18n.t(
                    artifact_key,
                    (
                        f"Prepared {artifact_count} "
                        f"{'artifact' if artifact_count == 1 else 'artifacts'}."
                    ),
                    count=artifact_count,
                ),
                source=self.name,
                stage="render_output",
                metadata={**render_call_meta, "call_state": "complete"},
            )
        timings["render_output"] = 0.0
        visual_review = getattr(render_result, "visual_review", None)

        await emit_capability_result(
            stream,
            {
                "response": summary.summary_text,
                "render_type": render_type,
                "summary": summary.model_dump(),
                "code": {
                    "language": "python",
                    "content": final_code,
                },
                "output_mode": request_config.output_mode,
                "artifacts": [artifact.model_dump() for artifact in render_result.artifacts],
                "timings": timings,
                "render": {
                    "quality": request_config.quality,
                    "retry_attempts": render_result.retry_attempts,
                    "retry_history": [item.model_dump() for item in render_result.retry_history],
                    "source_code_path": render_result.source_code_path,
                    "visual_review": visual_review.model_dump() if visual_review else None,
                },
                "analysis": analysis.model_dump(),
                "design": design.model_dump(),
            },
            source=self.name,
            usage=usage,
        )

    async def _run_answer_now(
        self,
        context: UnifiedContext,
        stream: StreamBus,
        payload: dict[str, Any],
        *,
        usage: UsageTracker | None = None,
        i18n: StatusI18n | None = None,
    ) -> None:
        """
        Fast-path for ``visualize``: skip analysis + review and emit final
        code in a single structured LLM call. The result envelope mirrors
        the standard pipeline so ``VisualizationViewer`` renders it
        directly.
        """
        import json
        import re

        from deeptutor.capabilities._answer_now import (
            build_answer_now_trace_metadata,
            format_trace_summary,
            join_chunks,
            labeled_block,
            load_answer_now_prompts,
            make_skip_notice,
            stream_synthesis,
        )

        if i18n is None:
            i18n = StatusI18n(self.name, context.language)
        original = str(payload.get("original_user_message") or context.user_message).strip()
        partial = str(payload.get("partial_response") or "").strip()
        trace_summary = format_trace_summary(payload.get("events"), language=context.language)

        render_mode = (
            str(context.config_overrides.get("render_mode", "auto") or "auto").strip().lower()
        )

        prompts = load_answer_now_prompts("visualize", context.language)
        system_prompt = str(prompts.get("system", "")).strip()
        user_prompt = str(prompts.get("user_template", "")).format(
            original=original,
            render_mode=render_mode,
            current_draft=labeled_block("Current Draft", partial),
            execution_trace=labeled_block("Execution Trace", trace_summary),
        )

        trace_meta = build_answer_now_trace_metadata(
            capability=self.name, phase="generating", label="Answer now"
        )
        notice = make_skip_notice(
            capability=self.name,
            language=context.language,
            stages_skipped=["analyzing", "reviewing"],
        )

        # html pages are larger; bump the answer-now budget for that mode.
        is_html_mode = render_mode == "html"
        max_tokens = 16000 if is_html_mode else 2400

        chunks: list[str] = []
        async with stream.stage("generating", source=self.name, metadata=trace_meta):
            async for chunk in stream_synthesis(
                stream=stream,
                source=self.name,
                stage="generating",
                trace_meta=trace_meta,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                push_content=False,
                response_format={"type": "json_object"},
            ):
                chunks.append(chunk)

        raw = join_chunks(chunks).strip()
        # Strip optional code fences for resilience.
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
            if raw.endswith("```"):
                raw = raw[:-3].rstrip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"render_type": "html" if is_html_mode else "svg", "code": raw}
        if not isinstance(parsed, dict):
            parsed = {
                "render_type": "html" if is_html_mode else "svg",
                "code": str(parsed),
            }

        default_type = "html" if is_html_mode else "svg"
        render_type = str(parsed.get("render_type") or default_type).strip().lower()
        if render_type not in {"svg", "chartjs", "mermaid", "html"}:
            render_type = default_type
        final_code = str(parsed.get("code") or "").strip()

        if render_type == "html":
            lang_tag = "html"
        elif render_type == "svg":
            lang_tag = "svg"
        elif render_type == "mermaid":
            lang_tag = "mermaid"
        else:
            lang_tag = "javascript"
        content_md = f"```{lang_tag}\n{final_code}\n```"
        body = (notice + "\n\n" + content_md).strip() if notice else content_md
        await stream.content(body, source=self.name, stage="generating")

        await emit_capability_result(
            stream,
            {
                "response": body,
                "render_type": render_type,
                "code": {
                    "language": lang_tag,
                    "content": final_code,
                },
                "analysis": {
                    "render_type": render_type,
                    "description": i18n.t(
                        "answer_now_skipped_analysis",
                        "Answer-now: skipped analysis stage.",
                    ),
                    "data_description": "",
                    "chart_type": "",
                    "visual_elements": [],
                    "rationale": "",
                },
                "review": {
                    "optimized_code": final_code,
                    "changed": False,
                    "review_notes": i18n.t(
                        "answer_now_skipped_review",
                        "Answer-now: skipped review stage.",
                    ),
                },
                "metadata": {"answer_now": True},
            },
            source=self.name,
            usage=usage,
        )

    def _build_trace_bridge(self, stream: StreamBus, i18n: StatusI18n | None = None):
        async def _trace_bridge(update: dict[str, Any]) -> None:
            event = str(update.get("event", "") or "")
            stage = str(update.get("phase") or update.get("stage") or "analyzing")
            base_metadata = {
                key: value
                for key, value in update.items()
                if key
                not in {"event", "state", "response", "chunk", "result", "tool_name", "tool_args"}
            }

            if event != "llm_call":
                return

            state = str(update.get("state", "running"))
            label = str(base_metadata.get("label", "") or stage.replace("_", " ").title())
            if state == "running":
                await stream.progress(
                    message=label,
                    source=self.name,
                    stage=stage,
                    metadata=merge_trace_metadata(
                        base_metadata,
                        {"trace_kind": "call_status", "call_state": "running"},
                    ),
                )
                return
            if state == "streaming":
                chunk = str(update.get("chunk", "") or "")
                if chunk:
                    await stream.thinking(
                        chunk,
                        source=self.name,
                        stage=stage,
                        metadata=merge_trace_metadata(
                            base_metadata,
                            {"trace_kind": "llm_chunk"},
                        ),
                    )
                return
            if state == "complete":
                was_streaming = update.get("streaming", False)
                if not was_streaming:
                    response = str(update.get("response", "") or "")
                    if response:
                        await stream.thinking(
                            response,
                            source=self.name,
                            stage=stage,
                            metadata=merge_trace_metadata(
                                base_metadata,
                                {"trace_kind": "llm_output"},
                            ),
                        )
                await stream.progress(
                    message=label,
                    source=self.name,
                    stage=stage,
                    metadata=merge_trace_metadata(
                        base_metadata,
                        {"trace_kind": "call_status", "call_state": "complete"},
                    ),
                )
                return
            if state == "error":
                fallback = (
                    i18n.t("llm_call_failed", "LLM call failed.")
                    if i18n is not None
                    else "LLM call failed."
                )
                await stream.error(
                    str(update.get("response", "") or fallback),
                    source=self.name,
                    stage=stage,
                    metadata=merge_trace_metadata(
                        base_metadata,
                        {"trace_kind": "call_status", "call_state": "error"},
                    ),
                )

        return _trace_bridge
