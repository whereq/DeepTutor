#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ManagerAgent - Milestone Planner

Based on user question and knowledge chain, generates a coarse-grained todo-list
for the solve phase to iterate over.
"""

from pathlib import Path
import sys
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent

from ..memory import InvestigateMemory, SolveMemory, TodoItem
from ..utils.json_utils import extract_json_from_text


class ManagerAgent(BaseAgent):
    """Manager Agent - Generates todo-list milestones for solving"""

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
            agent_name="manager_agent",
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            language=language,
            config=config,
            token_tracker=token_tracker,
        )

    async def process(
        self,
        question: str,
        investigate_memory: InvestigateMemory,
        solve_memory: SolveMemory,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Process management workflow - generate todo-list milestones

        Args:
            question: User question
            investigate_memory: Investigation memory (contains knowledge chain)
            solve_memory: Solve memory
            verbose: Whether to print detailed information

        Returns:
            dict: Management result with todo-list info
        """
        stage_label = "Plan"
        self.logger.log_stage_progress(
            stage_label, "start", f"question={question[:60]}{'...' if len(question) > 60 else ''}"
        )

        # 1. Check if todo-list already exists
        if solve_memory.todo_list:
            todos_count = len(solve_memory.todo_list)
            self.logger.log_stage_progress(stage_label, "skip", f"Already has {todos_count} todos")
            return {
                "has_todos": True,
                "todos_count": todos_count,
                "num_todos": todos_count,
                "message": "Todo-list already exists, skipping planning",
            }

        # 2. Build context
        context = self._build_context(question=question, investigate_memory=investigate_memory)

        # 3. Build Prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        # 4. Call LLM (requires JSON format output)
        response = await self.call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            verbose=verbose,
            stage=stage_label,
            response_format={"type": "json_object"},  # Force JSON
        )

        # 5. Parse output and create TodoItems
        todos = self._parse_todo_response(response)

        # 6. Add todos to solve_memory
        solve_memory.create_todo_list(todos)
        solve_memory.save()

        # 7. Log todo-list details
        todo_list_log = solve_memory.format_todo_list_for_log()
        for line in todo_list_log.split("\n"):
            self.logger.info(line)

        todos_count = len(todos)
        self.logger.log_stage_progress(stage_label, "complete", f"Generated {todos_count} todos")
        return {
            "has_todos": True,
            "todos_count": todos_count,
            "num_todos": todos_count,
            "message": f"Generated {todos_count} todos",
        }

    def _build_context(
        self, question: str, investigate_memory: InvestigateMemory
    ) -> dict[str, Any]:
        """Build context for LLM call"""
        # Get knowledge chain information (cite_id + summary)
        knowledge_info = []
        for knowledge in investigate_memory.knowledge_chain:
            if knowledge.summary:  # Only use knowledge with summary
                knowledge_info.append(
                    {
                        "cite_id": knowledge.cite_id,
                        "tool_type": knowledge.tool_type,
                        "query": knowledge.query,
                        "summary": knowledge.summary,
                    }
                )

        knowledge_text = ""
        for info in knowledge_info:
            knowledge_text += f"\n{info['cite_id']} [{info['tool_type']}]\n"
            knowledge_text += f"  Query: {info['query']}\n"
            knowledge_text += f"  Summary: {info['summary']}\n"

        remaining_questions = []
        if investigate_memory and getattr(investigate_memory, "reflections", None):
            remaining_questions = investigate_memory.reflections.remaining_questions or []

        reflections_summary = (
            "\n".join(f"- {q}" for q in remaining_questions)
            if remaining_questions
            else "(No remaining questions)"
        )

        knowledge_summary_text = knowledge_text if knowledge_text else "(No research information)"

        return {
            "question": question,
            "knowledge_info": knowledge_info,
            "knowledge_text": knowledge_summary_text,
            "knowledge_chain_summary": knowledge_summary_text,
            "reflections_summary": reflections_summary,
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt"""
        prompt = self.get_prompt("system") if self.has_prompts() else None
        if not prompt:
            raise ValueError(
                "ManagerAgent missing system prompt, please configure system section in prompts/zh/solve_loop/manager_agent.yaml."
            )
        return prompt

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        """Build user prompt"""
        template = self.get_prompt("user_template") if self.has_prompts() else None
        if not template:
            raise ValueError(
                "ManagerAgent missing user prompt template, please configure user_template in prompts/zh/solve_loop/manager_agent.yaml."
            )
        return template.format(**context)

    def _parse_todo_response(self, response: str) -> list[TodoItem]:
        """Parse LLM output (JSON format), create todo-list items"""
        todos: list[TodoItem] = []

        # Use json_utils to extract JSON
        parsed_data = extract_json_from_text(response)

        if not parsed_data or not isinstance(parsed_data, dict):
            raise ValueError(
                f"Failed to parse valid JSON object from LLM output. Original output: {response[:200]}..."
            )

        todos_data = parsed_data.get("todos", [])
        if not isinstance(todos_data, list):
            raise ValueError(f"'todos' field in JSON is not an array. Parsed result: {parsed_data}")

        if not todos_data:
            raise ValueError("'todos' array in JSON is empty, please check LLM output")

        # Parse each todo
        for idx, todo_data in enumerate(todos_data, 1):
            if not isinstance(todo_data, dict):
                self.logger.warning(
                    f"[ManagerAgent] Skipping invalid todo data (index {idx}): {todo_data}"
                )
                continue

            # Get todo_id
            todo_id = todo_data.get("todo_id", "").strip()
            if not todo_id:
                todo_id = f"T{idx}"
            elif not todo_id.upper().startswith("T"):
                todo_id = f"T{todo_id}"

            # Get description
            description = todo_data.get("description", "").strip()
            if not description:
                self.logger.warning(f"[ManagerAgent] Skipping todo {todo_id} with empty description")
                continue

            # Create todo item
            todos.append(
                TodoItem(
                    todo_id=todo_id,
                    description=description,
                    status="pending",
                )
            )

        if not todos:
            raise ValueError("Failed to parse any valid todos, please check LLM output format")

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.info(f"[ManagerAgent._parse_todo_response] Parsed {len(todos)} todo items")
            for todo in todos:
                logger.info(f"  - {todo.todo_id}: {todo.description}")

        return todos
