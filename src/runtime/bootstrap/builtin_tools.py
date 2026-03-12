"""Built-in tool class paths and alias metadata."""

from __future__ import annotations

from typing import Any

BUILTIN_TOOL_CLASSES: dict[str, str] = {
    "brainstorm": "src.tools.builtin.brainstorm:BrainstormTool",
    "rag": "src.tools.builtin.rag:RAGTool",
    "web_search": "src.tools.builtin.web:WebSearchTool",
    "code_execution": "src.tools.builtin.code_execution:CodeExecutionTool",
    "reason": "src.tools.builtin.reason:ReasonTool",
    "paper_search": "src.tools.builtin.paper_search:PaperSearchToolWrapper",
    "geogebra_analysis": "src.tools.builtin.geogebra_analysis:GeoGebraAnalysisTool",
}

TOOL_ALIASES: dict[str, tuple[str, dict[str, Any]]] = {
    "rag_hybrid": ("rag", {"mode": "hybrid"}),
    "rag_naive": ("rag", {"mode": "naive"}),
    "rag_search": ("rag", {}),
    "code_execute": ("code_execution", {}),
    "run_code": ("code_execution", {}),
}
