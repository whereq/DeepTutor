"""Brainstorm tool wrapper."""

from __future__ import annotations

from typing import Any

from src.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult
from src.tools.prompting.prompt_hints import load_prompt_hints


class BrainstormTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="brainstorm",
            description="Broadly explore multiple possibilities for a topic and give a short rationale for each.",
            parameters=[
                ToolParameter(
                    name="topic",
                    type="string",
                    description="The topic, goal, or problem to brainstorm about.",
                ),
                ToolParameter(
                    name="context",
                    type="string",
                    description="Optional supporting context, constraints, or background.",
                    required=False,
                ),
            ],
        )

    def get_prompt_hints(self, language: str = "en"):
        return load_prompt_hints(self.name, language=language)

    async def execute(self, **kwargs: Any) -> ToolResult:
        from src.tools.brainstorm import brainstorm

        topic = kwargs.get("topic", "")
        context = kwargs.get("context", "")
        api_key = kwargs.get("api_key")
        base_url = kwargs.get("base_url")
        model = kwargs.get("model")
        max_tokens = kwargs.get("max_tokens")
        temperature = kwargs.get("temperature")

        result = await brainstorm(
            topic=topic,
            context=context,
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return ToolResult(content=result.get("answer", ""), metadata=result)
