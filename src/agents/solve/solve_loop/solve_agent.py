#!/usr/bin/env python
"""
SolveAgent - Iterative information collector

For a given todo item, iteratively decides which tool to call to gather information.
Outputs {tool_type, query} per iteration until tool_type == "none" signals completion.
"""

from pathlib import Path
import sys
from typing import Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent

from ..memory import (
    InvestigateMemory,
    IterationRecord,
    SolveMemory,
    TodoItem,
    ToolCallRecord,
)
from ..utils.json_utils import extract_json_from_text


class SolveAgent(BaseAgent):
    """
    Solve Agent - Information collector for solving todos.
    
    For each todo, this agent iteratively decides what information to gather.
    Each call returns a single {tool_type, query} decision.
    When tool_type == "none", the iteration ends.
    """

    SUPPORTED_TOOL_TYPES = {
        "none",       # End iteration - information is sufficient
        "rag_naive",  # Precise formula/definition lookup
        "rag_hybrid", # Conceptual understanding/comparison
        "web_search", # External/latest information
        "code_execution",  # Calculations, plotting, derivations
    }

    def __init__(
        self,
        config: dict[str, Any],
        api_key: str,
        base_url: str,
        api_version: str | None = None,
        token_tracker=None,
    ):
        language = config.get("system", {}).get("language", "zh")
        super().__init__(
            module_name="solve",
            agent_name="solve_agent",
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            language=language,
            config=config,
            token_tracker=token_tracker,
        )
        # Max iterations per todo to prevent infinite loops
        self.max_iterations = config.get("solve", {}).get("max_inner_iterations", 5)

    async def process(
        self,
        current_todo: TodoItem,
        iteration_history: List[ToolCallRecord],
        knowledge_chain: List[Any],
        question: str,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Process a single iteration step for the current todo.

        Decides whether to call a tool or end the iteration.

        Args:
            current_todo: The todo item being worked on
            iteration_history: Previous tool calls in this iteration
            knowledge_chain: Knowledge from investigate phase
            question: Original user question
            verbose: Whether to print detailed information

        Returns:
            dict: {
                "tool_type": str,  # "none" to end iteration
                "query": str,      # Query/intent for the tool
                "should_stop": bool  # True if tool_type is "none"
            }
        """
        # Check iteration limit
        if len(iteration_history) >= self.max_iterations:
            self.logger.warning(
                f"[SolveAgent] Max iterations ({self.max_iterations}) reached for {current_todo.todo_id}"
            )
            return {
                "tool_type": "none",
                "query": "",
                "should_stop": True,
                "reason": "max_iterations_reached",
            }

        # Build context
        context = self._build_context(
            current_todo=current_todo,
            iteration_history=iteration_history,
            knowledge_chain=knowledge_chain,
            question=question,
        )

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        response = await self.call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            verbose=verbose,
            response_format={"type": "json_object"},
        )

        # Parse the decision
        decision = self._parse_decision(response)
        if not decision:
            self.logger.warning(
                f"SolveAgent JSON parsing failed, defaulting to none. Raw: {response[:200]}..."
            )
            return {
                "tool_type": "none",
                "query": "",
                "should_stop": True,
                "reason": "parse_error",
            }

        tool_type = decision["tool_type"]
        query = decision["query"]
        should_stop = tool_type == "none"

        return {
            "tool_type": tool_type,
            "query": query,
            "should_stop": should_stop,
            "raw_response": response,
        }

    # ------------------------------------------------------------------ #
    # Context Building
    # ------------------------------------------------------------------ #
    def _build_context(
        self,
        current_todo: TodoItem,
        iteration_history: List[ToolCallRecord],
        knowledge_chain: List[Any],
        question: str,
    ) -> dict[str, Any]:
        """Build context for LLM call"""
        # Format current todo
        todo_text = f"{current_todo.todo_id}: {current_todo.description}"

        # Format iteration history
        history_text = self._format_iteration_history(iteration_history)

        # Format knowledge chain from investigate phase
        knowledge_text = self._format_knowledge_chain(knowledge_chain)

        return {
            "question": question,
            "current_todo": todo_text,
            "iteration_history": history_text,
            "knowledge_chain": knowledge_text,
            "iteration_count": len(iteration_history),
            "max_iterations": self.max_iterations,
        }

    def _format_iteration_history(self, history: List[ToolCallRecord]) -> str:
        """Format the iteration history for context"""
        if not history:
            return "(No previous tool calls in this iteration)"

        lines = []
        for idx, record in enumerate(history, 1):
            summary = record.summary or "(pending)"
            if record.raw_answer and not record.summary:
                summary = record.raw_answer[:300] + "..."
            
            lines.append(
                f"[{idx}] {record.tool_type}\n"
                f"    Query: {record.query}\n"
                f"    cite_id: {record.cite_id or 'N/A'}\n"
                f"    Summary: {summary}"
            )
        return "\n\n".join(lines)

    def _format_knowledge_chain(self, knowledge_chain: List[Any]) -> str:
        """Format knowledge chain from investigate phase"""
        if not knowledge_chain:
            return "(No prior knowledge from investigation)"

        lines = []
        for knowledge in knowledge_chain:
            cite_id = getattr(knowledge, "cite_id", "")
            tool_type = getattr(knowledge, "tool_type", "")
            query = getattr(knowledge, "query", "")
            summary = getattr(knowledge, "summary", "") or getattr(knowledge, "raw_result", "")[:300]
            
            lines.append(
                f"{cite_id} [{tool_type}]\n"
                f"  Query: {query}\n"
                f"  Summary: {summary}"
            )
        return "\n\n".join(lines) if lines else "(No prior knowledge)"

    # ------------------------------------------------------------------ #
    # Prompt Building
    # ------------------------------------------------------------------ #
    def _build_system_prompt(self) -> str:
        prompt = self.get_prompt("system") if self.has_prompts() else None
        if not prompt:
            # Fallback prompt
            prompt = """# Role Definition
You are the **Solve Agent**, responsible for gathering information to complete the current todo.

## Task
Decide what tool to call next to collect information for the current todo.
Output ONE tool call decision per response.

## Output Format (STRICT JSON)
{
  "tool_type": "rag_naive | rag_hybrid | web_search | code_execution | none",
  "query": "Your query or intent description"
}

## Tool Types
- `rag_naive`: Precise definition/formula lookup from knowledge base
- `rag_hybrid`: Conceptual understanding, comparison, or broader search
- `web_search`: External information, latest news, or resources not in KB
- `code_execution`: Calculations, derivations, plotting, data processing
- `none`: No more information needed, end this iteration

## Rules
1. Output exactly ONE tool call per response
2. Use `none` when you have sufficient information to complete the todo
3. Do NOT generate answer content - only decide what information to gather
4. Consider what's already been collected in iteration_history
"""
        return prompt

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.get_prompt("user_template") if self.has_prompts() else None
        if not template:
            # Fallback template
            template = """## User Question
{question}

## Current Todo
{current_todo}

## Prior Knowledge (from investigation phase)
{knowledge_chain}

## This Iteration's Tool Calls ({iteration_count}/{max_iterations})
{iteration_history}

## Task
Decide the next tool call to gather information for the current todo.
Output "none" as tool_type if information is sufficient.
Output valid JSON only."""
        return template.format(**context)

    # ------------------------------------------------------------------ #
    # Response Parsing
    # ------------------------------------------------------------------ #
    def _parse_decision(self, response: str) -> Optional[dict[str, Any]]:
        """Parse the LLM decision - simplified output format"""
        parsed_data = extract_json_from_text(response)

        if not parsed_data or not isinstance(parsed_data, dict):
            return None

        tool_type = str(parsed_data.get("tool_type", "none")).strip().lower()
        query = str(parsed_data.get("query", "")).strip()

        # Normalize tool_type
        if tool_type not in self.SUPPORTED_TOOL_TYPES:
            # Try to map common variations
            if tool_type in {"finish", "stop", "end", "done"}:
                tool_type = "none"
            elif tool_type in {"rag", "search", "kb"}:
                tool_type = "rag_hybrid"
            elif tool_type in {"web", "internet"}:
                tool_type = "web_search"
            elif tool_type in {"code", "python", "execute"}:
                tool_type = "code_execution"
            else:
                self.logger.warning(f"[SolveAgent] Unknown tool_type '{tool_type}', defaulting to none")
                tool_type = "none"

        return {
            "tool_type": tool_type,
            "query": query,
        }


# Legacy compatibility - keep old process signature as alternative
class SolveAgentLegacy(SolveAgent):
    """Legacy wrapper for backward compatibility with old API"""

    async def process_legacy(
        self,
        question: str,
        solve_memory: SolveMemory,
        investigate_memory: InvestigateMemory,
        citation_memory: Any,
        kb_name: str = "ai_textbook",
        output_dir: str | None = None,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Legacy process method - wraps new API for backward compatibility.
        """
        current_todo = solve_memory.get_next_pending_todo()
        if not current_todo:
            return {
                "tool_type": "none",
                "query": "",
                "should_stop": True,
                "reason": "no_pending_todo",
            }

        # Get current iteration or empty history
        current_iter = solve_memory.get_current_iteration()
        iteration_history = current_iter.tool_calls if current_iter else []

        return await self.process(
            current_todo=current_todo,
            iteration_history=iteration_history,
            knowledge_chain=investigate_memory.knowledge_chain,
            question=question,
            verbose=verbose,
        )
