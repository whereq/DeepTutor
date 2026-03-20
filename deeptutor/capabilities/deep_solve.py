"""
Deep Solve Capability
=====================

Multi-agent problem solving pipeline: Plan -> ReAct -> Write.
Wraps the existing ``MainSolver``.
"""

from __future__ import annotations

import asyncio
from deeptutor.capabilities.request_contracts import get_capability_request_schema
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.core.trace import derive_trace_metadata, merge_trace_metadata


class DeepSolveCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="deep_solve",
        description="Multi-agent problem solving (Plan -> ReAct -> Write).",
        stages=["planning", "reasoning", "writing"],
        tools_used=["rag", "web_search", "code_execution", "reason"],
        cli_aliases=["solve"],
        request_schema=get_capability_request_schema("deep_solve"),
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        from deeptutor.agents.solve.main_solver import MainSolver
        from deeptutor.services.llm.config import get_llm_config

        llm_config = get_llm_config()
        detailed = context.config_overrides.get("detailed_answer", True)
        enabled_tools = (
            self.manifest.tools_used
            if context.enabled_tools is None
            else context.enabled_tools
        )
        rag_enabled = "rag" in enabled_tools
        kb_name = (
            context.knowledge_bases[0]
            if rag_enabled and context.knowledge_bases
            else None
        )

        solver = MainSolver(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=llm_config.api_version,
            kb_name=kb_name,
            language=context.language,
            enabled_tools=list(enabled_tools),
            disable_planner_retrieve=not (rag_enabled and kb_name),
        )
        await solver.ainit()

        # Also bridge the explicit progress callback
        def _normalize_stage(stage: str) -> str:
            mapping = {
                "plan": "planning",
                "planning": "planning",
                "solve": "reasoning",
                "solving": "reasoning",
                "reasoning": "reasoning",
                "write": "writing",
                "writing": "writing",
            }
            return mapping.get(stage, stage or "reasoning")

        async def _trace_bridge(update: dict) -> None:
            event = str(update.get("event", "") or "")
            stage = str(update.get("phase") or update.get("stage") or "reasoning")
            stage = _normalize_stage(stage)
            base_metadata = {
                key: value
                for key, value in update.items()
                if key
                not in {"event", "state", "response", "chunk", "result", "tool_args", "tool_name"}
            }

            if event == "llm_call":
                state = str(update.get("state", "running"))
                label = str(update.get("label", "") or "")
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
                        message="",
                        source=self.name,
                        stage=stage,
                        metadata=merge_trace_metadata(
                            base_metadata,
                            {"trace_kind": "call_status", "call_state": "complete"},
                        ),
                    )
                    return
                if state == "error":
                    await stream.error(
                        str(update.get("response", "") or "LLM call failed."),
                        source=self.name,
                        stage=stage,
                        metadata=merge_trace_metadata(
                            base_metadata,
                            {"trace_kind": "call_status", "call_state": "error"},
                        ),
                    )
                    return

            if event == "llm_observation":
                response = str(update.get("response", "") or "")
                if response:
                    await stream.observation(
                        response,
                        source=self.name,
                        stage=stage,
                        metadata=derive_trace_metadata(
                            base_metadata,
                            trace_role="observe",
                            trace_kind="observation",
                        ),
                    )
                return

            if event == "tool_call":
                await stream.tool_call(
                    tool_name=str(update.get("tool_name", "") or "tool"),
                    args=update.get("tool_args", {}) or {},
                    source=self.name,
                    stage=stage,
                    metadata=derive_trace_metadata(
                        base_metadata,
                        trace_role="tool",
                        trace_kind="tool_call",
                    ),
                )
                return

            if event == "tool_result":
                await stream.tool_result(
                    tool_name=str(update.get("tool_name", "") or "tool"),
                    result=str(update.get("result", "") or ""),
                    source=self.name,
                    stage=stage,
                    metadata=derive_trace_metadata(
                        base_metadata,
                        trace_role="tool",
                        trace_kind="tool_result",
                        sources=update.get("sources", []) or [],
                    ),
                )
                return

            if event == "tool_log":
                message = str(update.get("message", "") or "")
                if not message:
                    return
                await stream.progress(
                    message=message,
                    source=self.name,
                    stage=stage,
                    metadata=derive_trace_metadata(
                        base_metadata,
                        trace_role="retrieve",
                        trace_group="retrieve",
                        trace_kind=str(update.get("trace_kind", "tool_log") or "tool_log"),
                    ),
                )
                return

        def _progress_bridge(stage: str, progress: dict):
            async def _emit() -> None:
                status = str(progress.get("status", stage))
                detail_parts = []
                if "step_id" in progress:
                    detail_parts.append(f"[{progress['step_id']}]")
                if "step_target" in progress:
                    detail_parts.append(str(progress["step_target"])[:80])
                detail = " ".join(detail_parts)
                msg = f"{status}: {detail}" if detail else status
                await stream.progress(
                    message=msg,
                    source=self.name,
                    stage=_normalize_stage(stage),
                )

            try:
                asyncio.get_running_loop().create_task(_emit())
            except RuntimeError:
                pass

        solver._send_progress_update = _progress_bridge
        if hasattr(solver, "set_trace_callback"):
            solver.set_trace_callback(_trace_bridge)

        # Content callback — streams writer tokens to the main chat area
        content_streamed = False

        async def _content_sink(chunk: str) -> None:
            nonlocal content_streamed
            content_streamed = True
            await stream.content(
                chunk,
                source=self.name,
                stage="writing",
            )

        solver._content_callback = _content_sink

        result = await solver.solve(
            question=context.user_message,
            verbose=False,
            detailed=detailed,
            conversation_context=str(
                context.metadata.get("conversation_context_text", "") or ""
            ).strip(),
        )

        final_answer = result.get("final_answer", "")

        if final_answer and not content_streamed:
            async with stream.stage("writing", source=self.name):
                await stream.content(final_answer, source=self.name, stage="writing")

        await stream.result(
            {
                "response": final_answer,
                "output_dir": result.get("output_dir", ""),
                "metadata": result.get("metadata", {}),
            },
            source=self.name,
        )
