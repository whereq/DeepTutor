"""Web search tool – wraps ``src.tools.web_search.web_search``."""

from __future__ import annotations

import asyncio
from typing import Any

from src.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult
from src.tools.prompting.prompt_hints import load_prompt_hints


class WebSearchTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="web_search",
            description="Search the web and return summarised results with citations.",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query."),
            ],
        )

    def get_prompt_hints(self, language: str = "en"):
        return load_prompt_hints(self.name, language=language)

    async def execute(self, **kwargs: Any) -> ToolResult:
        from src.tools.web_search import web_search

        query = kwargs.get("query", "")
        output_dir = kwargs.get("output_dir")
        verbose = kwargs.get("verbose", False)
        result = await asyncio.to_thread(
            web_search,
            query=query,
            output_dir=output_dir,
            verbose=verbose,
        )

        if isinstance(result, dict):
            answer = result.get("answer", "")
            citations = result.get("citations", [])
        else:
            answer = str(result)
            citations = []

        return ToolResult(
            content=answer,
            sources=[
                {"type": "web", "url": c.get("url", ""), "title": c.get("title", "")}
                for c in citations
            ],
            metadata=result if isinstance(result, dict) else {"raw": answer},
        )
