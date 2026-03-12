"""Reason tool – wraps ``src.tools.reason.reason``."""

from __future__ import annotations

from typing import Any

from src.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult
from src.tools.prompting.prompt_hints import load_prompt_hints


class ReasonTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reason",
            description=(
                "Perform deep reasoning on a complex sub-problem using a dedicated LLM call. "
                "Use when the current context is insufficient for a confident answer."
            ),
            parameters=[
                ToolParameter(
                    name="query", type="string", description="The sub-problem to reason about."
                ),
                ToolParameter(
                    name="context",
                    type="string",
                    description="Supporting context for reasoning.",
                    required=False,
                ),
            ],
        )

    def get_prompt_hints(self, language: str = "en"):
        return load_prompt_hints(self.name, language=language)

    async def execute(self, **kwargs: Any) -> ToolResult:
        from src.tools.reason import reason

        query = kwargs.get("query", "")
        context = kwargs.get("context", "")
        api_key = kwargs.get("api_key")
        base_url = kwargs.get("base_url")
        model = kwargs.get("model")
        max_tokens = kwargs.get("max_tokens")
        temperature = kwargs.get("temperature")

        result = await reason(
            query=query,
            context=context,
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return ToolResult(content=result.get("answer", ""), metadata=result)
