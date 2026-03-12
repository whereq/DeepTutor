"""
Deep Research Capability
========================

Multi-agent deep research with report generation.
Wraps ``ResearchPipeline`` as a first-class built-in capability.
"""

from __future__ import annotations

from typing import Any

from src.core.capability_protocol import BaseCapability, CapabilityManifest
from src.core.context import UnifiedContext
from src.core.stream_bus import StreamBus
from src.core.trace import derive_trace_metadata, merge_trace_metadata, new_call_id


class DeepResearchCapability(BaseCapability):
    manifest = CapabilityManifest(
        name="deep_research",
        description="Multi-agent deep research with report generation.",
        stages=["rephrasing", "decomposing", "researching", "reporting"],
        tools_used=["rag", "web_search", "paper_search", "code_execution"],
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        from src.agents.research.research_pipeline import ResearchPipeline
        from src.agents.research.request_config import (
            build_research_runtime_config,
            validate_research_request_config,
        )
        from src.services.config import load_config_with_main
        from src.services.llm.config import get_llm_config

        llm_config = get_llm_config()
        kb_name = context.knowledge_bases[0] if context.knowledge_bases else None
        topic = context.user_message
        enabled_tools = set(
            self.manifest.tools_used
            if context.enabled_tools is None
            else context.enabled_tools
        )
        request_config = validate_research_request_config(context.config_overrides)
        config = build_research_runtime_config(
            base_config=load_config_with_main("main.yaml"),
            request_config=request_config,
            enabled_tools=enabled_tools,
            kb_name=kb_name,
        )

        def _normalize_stage(stage: str) -> str:
            mapping = {
                "rephrase": "rephrasing",
                "check_satisfaction": "rephrasing",
                "decompose": "decomposing",
                "decompose_no_rag": "decomposing",
                "check_sufficiency": "researching",
                "generate_query_plan": "researching",
                "plan_next_step": "researching",
                "generate_summary": "researching",
                "deduplicate": "reporting",
                "generate_outline": "reporting",
                "write_introduction": "reporting",
                "write_section_body": "reporting",
                "write_conclusion": "reporting",
                "write_full_report": "reporting",
            }
            return mapping.get(stage, stage or "researching")

        def _stage_card(stage: str, status: str = "") -> str:
            if stage in {"rephrasing"} or status.startswith(("planning_started", "rephrase")):
                return "understand"
            if stage in {"decomposing"} or status.startswith(("decompose", "queue_")):
                return "decompose"
            if stage == "reporting":
                return "result"
            return "evidence"

        def _progress_message(data: dict[str, Any]) -> str:
            status = str(data.get("status") or data.get("type") or "").strip()
            pretty_map = {
                "planning_started": "Clarifying the research question",
                "rephrase_completed": "Refined the research focus",
                "rephrase_skipped": "Using the original topic directly",
                "decompose_started": "Breaking the topic into subtopics",
                "decompose_completed": "Prepared subtopics for investigation",
                "queue_seeded": "Queued a research subtopic",
                "researching_started": "Searching for evidence",
                "block_started": "Investigating a subtopic",
                "block_completed": "Completed one evidence block",
                "researching_completed": "Evidence gathering finished",
                "reporting_started": "Drafting the final result",
                "reporting_completed": "Final result is ready",
            }
            return pretty_map.get(
                status,
                str(data.get("message") or status or data.get("type") or "").strip(),
            )

        async def _progress_cb(data: dict[str, Any]) -> None:
            raw_stage = str(data.get("stage") or "researching")
            stage = _normalize_stage(raw_stage)
            status = str(data.get("status") or data.get("type") or "")
            message = _progress_message(data)
            if not message:
                return
            await stream.progress(
                message=message,
                source=self.name,
                stage=stage,
                metadata={
                    key: value
                    for key, value in data.items()
                    if key not in {"message", "status", "type", "stage"}
                }
                | {
                    "research_stage_card": _stage_card(stage, status),
                    "research_status": status,
                },
            )

        def _label_from_update(update: dict[str, Any], stage: str) -> str:
            agent_name = str(update.get("agent_name") or "")
            raw_stage = str(update.get("stage") or "")
            block_id = str(update.get("block_id") or "")
            iteration = update.get("iteration")

            if agent_name == "rephrase_agent":
                return "Rephrase topic"
            if agent_name == "decompose_agent":
                return "Decompose topic"
            if agent_name == "note_agent":
                return "Summarize evidence"
            if stage == "reporting":
                if raw_stage == "generate_outline":
                    return "Generate outline"
                if raw_stage.startswith("write_"):
                    return "Write report"
                return "Reporting"
            if block_id and isinstance(iteration, int):
                return f"{block_id.replace('_', ' ').title()} · Round {iteration}"
            if block_id:
                return block_id.replace("_", " ").title()
            return "Research step"

        async def _trace_cb(update: dict[str, Any]) -> None:
            event = str(update.get("event", "") or "")
            stage = _normalize_stage(str(update.get("phase") or update.get("stage") or "researching"))
            raw_stage = str(update.get("stage") or "")
            base_metadata = {
                key: value
                for key, value in update.items()
                if key
                not in {"event", "state", "response", "chunk", "result", "tool_name", "tool_args"}
            }
            call_id = str(base_metadata.get("call_id") or new_call_id("research"))
            base_metadata.setdefault("call_id", call_id)
            base_metadata.setdefault("phase", stage)
            base_metadata.setdefault("label", _label_from_update(update, stage))
            base_metadata.setdefault("research_stage_card", _stage_card(stage, raw_stage))

            if event == "llm_call":
                state = str(update.get("state", "running"))
                label = str(base_metadata.get("label", "") or "")
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
                state = str(update.get("state", "complete") or "complete")
                result = str(update.get("result", "") or "")
                if state == "error":
                    await stream.error(
                        result,
                        source=self.name,
                        stage=stage,
                        metadata=derive_trace_metadata(
                            base_metadata,
                            trace_role="tool",
                            trace_kind="tool_result",
                        ),
                    )
                    return
                await stream.tool_result(
                    tool_name=str(update.get("tool_name", "") or "tool"),
                    result=result,
                    source=self.name,
                    stage=stage,
                    metadata=derive_trace_metadata(
                        base_metadata,
                        trace_role="tool",
                        trace_kind="tool_result",
                    ),
                )
                return

        pipeline = ResearchPipeline(
            config=config,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=llm_config.api_version,
            kb_name=kb_name,
            progress_callback=_progress_cb,
            trace_callback=_trace_cb,
        )

        async with stream.stage("researching", source=self.name):
            await stream.thinking(f"Researching topic: {topic}", source=self.name, stage="researching")
            result = await pipeline.run(topic=topic)

        report = result.get("report", "")
        if report:
            async with stream.stage("reporting", source=self.name):
                await stream.content(report, source=self.name, stage="reporting")

        await stream.result(
            {"response": report, "metadata": result.get("metadata", {})},
            source=self.name,
        )
