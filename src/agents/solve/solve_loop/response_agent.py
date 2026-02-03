#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ResponseAgent - Step response generator

Based on completed todos and tool call chain from an iteration,
generates a formal, professional response for the completed work.
"""

from pathlib import Path
import re
import sys
from typing import Any, List, Optional

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent

from ..memory import (
    CitationMemory,
    InvestigateMemory,
    IterationRecord,
    SolveChainStep,
    SolveMemory,
    TodoItem,
    ToolCallRecord,
)


class ResponseAgent(BaseAgent):
    """
    Response generator Agent.
    
    Generates professional step_response content based on:
    - Completed todos from an iteration
    - Tool call chain with summaries
    - Knowledge from investigation phase
    """

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
            agent_name="response_agent",
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            language=language,
            config=config,
            token_tracker=token_tracker,
        )
        # Store citation configuration
        self.enable_citations = config.get("system", {}).get("enable_citations", True)

    async def process(
        self,
        question: str,
        iteration_record: IterationRecord,
        completed_todos: List[TodoItem],
        citation_memory: CitationMemory,
        knowledge_chain: List[Any],
        output_dir: str | None = None,
        accumulated_response: str = "",
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Generate step_response for completed todos based on iteration results.

        Args:
            question: Original user question
            iteration_record: The iteration record with tool call history
            completed_todos: List of TodoItem objects that were completed
            citation_memory: Citation memory for source tracking
            knowledge_chain: Knowledge from investigation phase
            output_dir: Output directory path
            accumulated_response: Previous step responses for context
            verbose: Whether to print detailed information

        Returns:
            dict: {
                "step_response": str,
                "used_citations": List[str],
                "iteration_id": str
            }
        """
        if not completed_todos:
            return {
                "step_response": "",
                "used_citations": [],
                "iteration_id": iteration_record.iteration_id,
                "skipped": True,
                "reason": "No completed todos to respond to",
            }

        # Build context
        context = self._build_context(
            question=question,
            iteration_record=iteration_record,
            completed_todos=completed_todos,
            citation_memory=citation_memory,
            knowledge_chain=knowledge_chain,
            output_dir=output_dir,
            accumulated_response=accumulated_response,
        )

        system_prompt = self._build_system_prompt(context["image_materials"])
        user_prompt = self._build_user_prompt(context)

        response = await self.call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            verbose=verbose,
        )

        # Process response
        step_response = response.strip() if response else ""
        used_citations = self._extract_used_citations(
            content=step_response,
            tool_calls=iteration_record.tool_calls,
            knowledge_chain=knowledge_chain,
        )

        # Update iteration record
        iteration_record.set_step_response(step_response, used_citations)

        return {
            "step_response": step_response,
            "used_citations": used_citations,
            "iteration_id": iteration_record.iteration_id,
            "completed_todo_ids": [t.todo_id for t in completed_todos],
            "raw_response": response,
        }

    # ------------------------------------------------------------------ #
    # Context Building
    # ------------------------------------------------------------------ #
    def _build_context(
        self,
        question: str,
        iteration_record: IterationRecord,
        completed_todos: List[TodoItem],
        citation_memory: CitationMemory,
        knowledge_chain: List[Any],
        output_dir: str | None,
        accumulated_response: str = "",
    ) -> dict[str, Any]:
        """Build context for LLM call"""
        # Format completed todos
        completed_todos_text = self._format_completed_todos(completed_todos)

        # Format tool call chain
        tool_materials, image_materials = self._format_tool_call_chain(
            iteration_record.tool_calls, output_dir
        )

        # Format knowledge chain
        knowledge_text = self._format_knowledge_chain(knowledge_chain)

        # Format citation details
        citation_details = self._format_citation_details(
            iteration_record.tool_calls, citation_memory
        )

        # Get user preference from personalization service
        preference = self._get_user_preference()

        return {
            "question": question,
            "iteration_id": iteration_record.iteration_id,
            "completed_todos": completed_todos_text,
            "completed_todos_count": len(completed_todos),
            "tool_materials": tool_materials,
            "knowledge_chain": knowledge_text,
            "citation_details": citation_details,
            "image_materials": image_materials,
            "previous_context": accumulated_response
            or "(No previous content, this is the first step)",
            "preference": preference,
        }

    def _get_user_preference(self) -> str:
        """Get user preference from personalization service."""
        try:
            from src.personalization.service import get_personalization_service
            
            service = get_personalization_service()
            preference = service.get_preference_for_prompt()
            return preference if preference else "(No user preference recorded)"
        except Exception as e:
            self.logger.debug(f"Failed to get user preference: {e}")
            return "(No user preference recorded)"

    def _format_completed_todos(self, todos: List[TodoItem]) -> str:
        """Format completed todos for context"""
        if not todos:
            return "(No todos completed)"

        lines = []
        for todo in todos:
            lines.append(f"- {todo.todo_id}: {todo.description}")
        return "\n".join(lines)

    def _format_tool_call_chain(
        self,
        tool_calls: List[ToolCallRecord],
        output_dir: str | None,
    ) -> tuple[str, list[str]]:
        """Format tool call chain and extract images"""
        if not tool_calls:
            return "(No tool calls in this iteration)", []

        lines: list[str] = []
        images: list[str] = []
        seen_images: set[str] = set()

        def _append_image(path_str: str):
            normalized = str(path_str).replace("\\", "/")
            if normalized and normalized not in seen_images:
                images.append(normalized)
                seen_images.add(normalized)

        for idx, call in enumerate(tool_calls, 1):
            summary = call.summary or "(Summary pending)"
            raw_preview = (call.raw_answer or "")[:500]
            lines.append(
                f"[{idx}] {call.tool_type} | cite_id={call.cite_id or 'N/A'} | Status={call.status}\n"
                f"Query: {call.query}\n"
                f"Summary: {summary}\n"
                f"Raw excerpt: {raw_preview}"
            )

            # Extract images from metadata
            if call.metadata:
                artifact_rel_paths = call.metadata.get("artifact_rel_paths", [])
                artifact_paths = call.metadata.get("artifact_paths", [])
                artifacts = call.metadata.get("artifacts", [])

                if artifact_rel_paths:
                    for rel_path in artifact_rel_paths:
                        _append_image(rel_path)

                if artifact_paths:
                    for abs_path in artifact_paths:
                        path = Path(abs_path)
                        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp"}:
                            if output_dir:
                                try:
                                    rel_path = path.relative_to(Path(output_dir))
                                    _append_image(str(rel_path))
                                except ValueError:
                                    _append_image(path.name)
                            else:
                                _append_image(path.name)
                elif artifacts:
                    for artifact in artifacts:
                        path = Path(artifact)
                        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp"}:
                            rel_path = Path("artifacts") / path.name
                            _append_image(str(rel_path))

        return "\n\n".join(lines), images

    def _format_knowledge_chain(self, knowledge_chain: List[Any]) -> str:
        """Format knowledge chain from investigation phase"""
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

    def _format_citation_details(
        self,
        tool_calls: List[ToolCallRecord],
        citation_memory: CitationMemory,
    ) -> str:
        """Format citation details from tool calls"""
        if not self.enable_citations:
            return "(Citations disabled)"

        cite_ids = [tc.cite_id for tc in tool_calls if tc.cite_id]
        if not cite_ids:
            return "(No citations)"

        lines: list[str] = []
        for cite_id in cite_ids:
            citation = citation_memory.get_citation(cite_id)
            if not citation:
                continue
            summary = citation.content or citation.raw_result[:200]
            lines.append(f"- {cite_id} [{citation.tool_type}] Query: {citation.query}")
            if summary:
                lines.append(f"  Summary: {summary[:300]}")
        return "\n".join(lines) if lines else "(Citation information missing)"

    # ------------------------------------------------------------------ #
    # Prompt Building
    # ------------------------------------------------------------------ #
    def _build_system_prompt(self, image_materials: list[str]) -> str:
        base_prompt = self.get_prompt("system") if self.has_prompts() else None
        if not base_prompt:
            # Fallback system prompt
            base_prompt = """# Role Definition
You are a professional teaching assistant. Generate a high-quality response based on the completed todos and tool call results.

## Core Principles
1. **Continuity**: Follow directly after previous_context, maintaining smooth flow
2. **Evidence-based**: All conclusions must be based on the provided materials
3. **Professional format**: Well-structured with proper headings and formatting

## Key Norms

### Citation Format
- Cite sources using: `[cite_id]` (e.g., `[rag-1]`, `[code-2]`)
- Place immediately after the cited content

### Mathematical Formulas (LaTeX)
- Inline: `$x$`, `$E = mc^2$`
- Block: `$$` on separate lines
- Never use bare math variables in text

### Output Structure
- Use Markdown headings (## or ###)
- Include explanations for concepts
- Show logical derivation steps
- Summarize key points at the end
"""

        # Add citation disable instruction if needed
        citation_instruction = ""
        if not self.enable_citations:
            citation_instruction_yaml = self.get_prompt("citation_instruction_disabled")
            if citation_instruction_yaml:
                citation_instruction = citation_instruction_yaml
            else:
                citation_instruction = "\n\n**Important: Citation Feature Disabled**\n"

        # Add image instructions if there are images
        if image_materials:
            image_list = "\n".join([f"  - {img}" for img in image_materials])
            image_instruction_template = self.get_prompt("image_instruction")
            if image_instruction_template:
                image_instruction = image_instruction_template.format(image_list=image_list)
            else:
                image_instruction = f"\n\n**Image files to insert**:\n{image_list}\n"
            return base_prompt + citation_instruction + image_instruction

        return base_prompt + citation_instruction

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        template = self.get_prompt("user_template") if self.has_prompts() else None
        if not template:
            # Fallback user template
            template = """## User Preference
{preference}

## User Question
{question}

## Previous Context (Completed Steps)
{previous_context}

## Completed Todos This Iteration ({completed_todos_count} items)
{completed_todos}

## Tool Call Results
{tool_materials}

## Prior Knowledge (from investigation)
{knowledge_chain}

## Citation Details
{citation_details}

## Images to Insert
{image_materials}

## Task
Generate a professional response for the completed todos listed above.
The response should:
1. Address each completed todo with appropriate depth
2. Use evidence from tool call results
3. Include proper citations where applicable
4. Follow the formatting guidelines
"""

        # Format image_materials as text
        image_materials = context.get("image_materials", [])
        if isinstance(image_materials, list):
            if image_materials:
                image_text = "\n".join([f"- {img}" for img in image_materials])
            else:
                image_text = "(No image files)"
        else:
            image_text = str(image_materials)

        formatted_context = context.copy()
        formatted_context["image_materials"] = image_text

        return template.format(**formatted_context)

    # ------------------------------------------------------------------ #
    # Citation Extraction
    # ------------------------------------------------------------------ #
    def _extract_used_citations(
        self,
        content: str,
        tool_calls: List[ToolCallRecord],
        knowledge_chain: List[Any],
    ) -> list[str]:
        """Extract citation IDs used in the response"""
        if not self.enable_citations:
            return []

        if not content:
            return []

        # Pattern to match citations
        pattern = re.compile(r"\[([^\]\[]+)\](?!\()|【([^】\[]+)】")
        matches = pattern.findall(content)

        normalized: list[str] = []
        for match in matches:
            candidate = match[0] or match[1]
            if not candidate:
                continue
            normalized.append(f"[{candidate.strip()}]")

        # Build set of allowed citations
        allowed = set()
        for tc in tool_calls:
            if tc.cite_id:
                allowed.add(tc.cite_id)
        for k in knowledge_chain:
            cite_id = getattr(k, "cite_id", "")
            if cite_id:
                allowed.add(cite_id)

        # Filter to only allowed citations, preserving order
        ordered: list[str] = []
        for cite in normalized:
            if cite in allowed and cite not in ordered:
                ordered.append(cite)

        return ordered


# ------------------------------------------------------------------ #
# Legacy compatibility
# ------------------------------------------------------------------ #
class ResponseAgentLegacy(ResponseAgent):
    """Legacy wrapper for backward compatibility with SolveChainStep API"""

    async def process_legacy(
        self,
        question: str,
        step: SolveChainStep,
        solve_memory: SolveMemory,
        investigate_memory: InvestigateMemory,
        citation_memory: CitationMemory,
        output_dir: str | None = None,
        verbose: bool = True,
        accumulated_response: str = "",
    ) -> dict[str, Any]:
        """Legacy process method using SolveChainStep"""
        if not step:
            return {"step_response": "(No pending step)"}

        # Convert SolveChainStep to IterationRecord format
        iteration_record = IterationRecord(
            iteration_id=step.step_id,
            target_todo_id=step.step_id,
            tool_calls=step.tool_calls,
        )

        # Create a pseudo TodoItem for the step
        completed_todo = TodoItem(
            todo_id=step.step_id,
            description=step.step_target,
            status="completed",
        )

        result = await self.process(
            question=question,
            iteration_record=iteration_record,
            completed_todos=[completed_todo],
            citation_memory=citation_memory,
            knowledge_chain=investigate_memory.knowledge_chain,
            output_dir=output_dir,
            accumulated_response=accumulated_response,
            verbose=verbose,
        )

        # Update legacy memory structures
        if result.get("step_response"):
            step.update_response(
                response=result["step_response"],
                used_citations=result.get("used_citations", []),
            )
            solve_memory.save()

        return {
            "step_id": step.step_id,
            "step_response": result.get("step_response", ""),
            "used_citations": result.get("used_citations", []),
            "raw_response": result.get("raw_response", ""),
        }
