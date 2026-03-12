"""GeoGebra Analysis tool – full vision analysis pipeline as a single atomic tool."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult
from src.tools.prompting.prompt_hints import load_prompt_hints

logger = logging.getLogger(__name__)


class GeoGebraAnalysisTool(BaseTool):
    """Analyze a math-problem image and generate GeoGebra visualization commands."""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="geogebra_analysis",
            description=(
                "Analyze a math problem image, detect geometric elements, "
                "and generate validated GeoGebra commands for visualization. "
                "Requires an attached image."
            ),
            parameters=[
                ToolParameter(
                    name="question",
                    type="string",
                    description="The math problem text to analyze.",
                ),
                ToolParameter(
                    name="image_base64",
                    type="string",
                    description="Base64-encoded image (data URI or raw). Injected from attachments when called via function-calling.",
                    required=False,
                    default="",
                ),
                ToolParameter(
                    name="language",
                    type="string",
                    description="Output language: 'zh' or 'en'.",
                    required=False,
                    default="zh",
                    enum=["zh", "en"],
                ),
            ],
        )

    def get_prompt_hints(self, language: str = "en"):
        return load_prompt_hints(self.name, language=language)

    async def execute(self, **kwargs: Any) -> ToolResult:
        from src.agents.vision_solver.vision_solver_agent import VisionSolverAgent
        from src.services.llm.config import get_llm_config

        question: str = kwargs.get("question", "")
        image_base64: str = kwargs.get("image_base64", "")
        language: str = kwargs.get("language", "zh")

        if not image_base64:
            return ToolResult(
                content="No image provided. This tool requires an image attachment.",
                success=False,
            )

        llm_config = get_llm_config()

        agent = VisionSolverAgent(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            language=language,
        )

        try:
            result = await agent.process(
                question_text=question,
                image_base64=image_base64,
            )
        except Exception as exc:
            logger.exception("GeoGebra analysis pipeline failed")
            return ToolResult(
                content=f"Analysis pipeline error: {exc}",
                success=False,
            )

        if not result.get("has_image"):
            return ToolResult(
                content="No image was processed.",
                success=False,
            )

        final_commands = result.get("final_ggb_commands", [])
        ggb_block = agent.format_ggb_block(final_commands)

        summary_parts: list[str] = []
        analysis = result.get("analysis_output") or {}
        constraints = analysis.get("constraints", [])
        relations = analysis.get("geometric_relations", [])
        if constraints:
            summary_parts.append(f"Constraints ({len(constraints)}): {json.dumps(constraints[:5], ensure_ascii=False)}")
        if relations:
            descs = [
                relation.get("description", str(relation))
                if isinstance(relation, dict) else str(relation)
                for relation in relations[:5]
            ]
            summary_parts.append(f"Relations ({len(relations)}): {json.dumps(descs, ensure_ascii=False)}")

        content_parts = []
        if summary_parts:
            content_parts.append("\n".join(summary_parts))
        if ggb_block:
            content_parts.append(ggb_block)
        else:
            content_parts.append("(No GeoGebra commands generated.)")

        return ToolResult(
            content="\n\n".join(content_parts),
            metadata={
                "has_image": True,
                "commands_count": len(final_commands),
                "final_ggb_commands": final_commands,
                "image_is_reference": result.get("image_is_reference", False),
                "bbox_elements": len((result.get("bbox_output") or {}).get("elements", [])),
                "constraints_count": len(constraints),
                "relations_count": len(relations),
                "reflection_issues": len(
                    (result.get("reflection_output") or {}).get("issues_found", [])
                ),
            },
        )
