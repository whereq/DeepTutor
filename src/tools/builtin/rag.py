"""RAG search tool – wraps ``src.tools.rag_tool.rag_search``."""

from __future__ import annotations

from typing import Any

from src.core.tool_protocol import BaseTool, ToolDefinition, ToolParameter, ToolResult
from src.tools.prompting.prompt_hints import load_prompt_hints


class RAGTool(BaseTool):
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="rag",
            description=(
                "Search a knowledge base using Retrieval-Augmented Generation. "
                "Returns relevant passages and an LLM-synthesised answer."
            ),
            parameters=[
                ToolParameter(name="query", type="string", description="Search query."),
                ToolParameter(
                    name="kb_name",
                    type="string",
                    description="Knowledge base to search.",
                    required=False,
                ),
                ToolParameter(
                    name="mode",
                    type="string",
                    description="Search mode.",
                    required=False,
                    default="hybrid",
                    enum=["naive", "local", "global", "hybrid"],
                ),
            ],
        )

    def get_prompt_hints(self, language: str = "en"):
        return load_prompt_hints(self.name, language=language)

    async def execute(self, **kwargs: Any) -> ToolResult:
        from src.tools.rag_tool import rag_search

        query = kwargs.get("query", "")
        kb_name = kwargs.get("kb_name")
        mode = kwargs.get("mode", "hybrid")
        event_sink = kwargs.get("event_sink")
        extra_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"query", "kb_name", "mode", "event_sink"}
        }

        result = await rag_search(
            query=query,
            kb_name=kb_name,
            mode=mode,
            event_sink=event_sink,
            **extra_kwargs,
        )
        content = result.get("answer") or result.get("content", "")
        return ToolResult(
            content=content,
            sources=[{"type": "rag", "query": query, "kb_name": kb_name, "mode": mode}],
            metadata=result,
        )
