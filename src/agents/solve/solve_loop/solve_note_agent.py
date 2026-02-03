#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SolveNoteAgent - Todo-list manager

Responsible for reviewing the iteration results and managing the todo-list.
Can mark todos as done, edit their content, add new todos, or delete existing ones.

This agent enables dynamic todo-list management based on what was discovered during solving.
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
    IterationRecord,
    NoteAction,
    SolveMemory,
    TodoItem,
    ToolCallRecord,
)
from ..utils.json_utils import extract_json_from_text


class SolveNoteAgent(BaseAgent):
    """
    Note Agent - Manages todo-list based on iteration results.
    
    Capabilities:
    - Mark todos as done (completed)
    - Edit todo content (for partial completion or refinement)
    - Add new todos (for split tasks or discovered subtasks)
    - Delete todos (if no longer needed or merged)
    """

    VALID_ACTIONS = {"done", "edit", "add", "delete"}

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
            agent_name="solve_note_agent",
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            language=language,
            config=config,
            token_tracker=token_tracker,
        )

    async def process(
        self,
        solve_memory: SolveMemory,
        iteration_record: IterationRecord,
        target_todo: TodoItem,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Review iteration results and manage the todo-list.

        Args:
            solve_memory: Solve memory containing todo-list
            iteration_record: The iteration record with tool call history
            target_todo: The todo that was being worked on
            verbose: Whether to print detailed information

        Returns:
            dict: {
                "success": bool,
                "actions": List[NoteAction],
                "completed_todos": List[str],  # todo_ids that were marked done
                "raw_response": str
            }
        """
        # Build context
        context = self._build_context(
            solve_memory=solve_memory,
            iteration_record=iteration_record,
            target_todo=target_todo,
        )

        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        # Call LLM
        response = await self.call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            verbose=verbose,
            response_format={"type": "json_object"},
        )

        # Parse actions
        actions = self._parse_actions(response)

        # Convert to NoteAction objects
        note_actions = [
            NoteAction(
                pre_id=action["pre_id"],
                action=action["action"],
                content=action.get("content"),
            )
            for action in actions
        ]

        # Get cite_ids from iteration for evidence
        cite_ids = iteration_record.get_all_cite_ids()

        # Apply actions to solve_memory
        completed_todos = solve_memory.apply_note_actions(
            actions=note_actions,
            iteration_id=iteration_record.iteration_id,
            cite_ids=cite_ids,
        )

        # Update iteration record
        iteration_record.set_note_actions(note_actions)
        iteration_record.set_completed_todos(completed_todos)

        # Save memory
        solve_memory.save()

        return {
            "success": True,
            "actions": [a.to_dict() for a in note_actions],
            "completed_todos": completed_todos,
            "total_actions": len(note_actions),
            "raw_response": response,
        }

    # ------------------------------------------------------------------ #
    # Context Building
    # ------------------------------------------------------------------ #
    def _build_context(
        self,
        solve_memory: SolveMemory,
        iteration_record: IterationRecord,
        target_todo: TodoItem,
    ) -> dict[str, Any]:
        """Build context for the note agent"""
        # Format todo list with positions
        todo_list_text = self._format_todo_list_with_positions(solve_memory.todo_list)

        # Format iteration tool call history
        tool_call_history = self._format_tool_call_history(iteration_record.tool_calls)

        # Target todo info
        target_todo_text = f"{target_todo.todo_id}: {target_todo.description}"

        return {
            "todo_list": todo_list_text,
            "target_todo": target_todo_text,
            "target_todo_id": target_todo.todo_id,
            "tool_call_history": tool_call_history,
            "total_todos": len(solve_memory.todo_list),
        }

    def _format_todo_list_with_positions(self, todo_list: List[TodoItem]) -> str:
        """Format todo-list with position numbers for reference"""
        if not todo_list:
            return "(Empty todo-list)"

        lines = []
        for idx, todo in enumerate(todo_list, 1):
            status_marker = {
                "pending": "[ ]",
                "in_progress": "[~]",
                "completed": "[x]",
                "skipped": "[-]",
            }.get(todo.status, "[ ]")
            # Position is 1-indexed, pre_id for this todo would be idx
            lines.append(f"[pos={idx}] {status_marker} {todo.todo_id}: {todo.description}")
        return "\n".join(lines)

    def _format_tool_call_history(self, tool_calls: List[ToolCallRecord]) -> str:
        """Format tool call history"""
        if not tool_calls:
            return "(No tool calls in this iteration)"

        lines = []
        for idx, call in enumerate(tool_calls, 1):
            summary = call.summary or "(No summary)"
            if call.raw_answer and not call.summary:
                summary = call.raw_answer[:500] + "..."
            
            lines.append(
                f"[{idx}] {call.tool_type} (cite: {call.cite_id or 'N/A'})\n"
                f"    Query: {call.query}\n"
                f"    Summary: {summary}"
            )
        return "\n\n".join(lines)

    # ------------------------------------------------------------------ #
    # Prompt Building
    # ------------------------------------------------------------------ #
    def _build_system_prompt(self) -> str:
        """Build system prompt"""
        prompt = self.get_prompt("system") if self.has_prompts() else None
        if not prompt:
            prompt = """# Role Definition
You are the **Todo Manager** for a problem-solving system.

Your task is to review the iteration results (tool call history) and update the todo-list accordingly.

## Capabilities
You can perform these actions on the todo-list:
- `done`: Mark a todo as completed
- `edit`: Change the content of a todo
- `add`: Insert a new todo at a specific position
- `delete`: Remove a todo from the list

## Output Format (STRICT JSON)
```json
{
  "actions": [
    {
      "pre_id": 1,
      "action": "done",
      "content": null
    },
    {
      "pre_id": 1,
      "action": "add",
      "content": "New subtask that needs investigation"
    }
  ]
}
```

## pre_id Explanation
- `pre_id` indicates the position BEFORE which to operate
- `pre_id=1` means operate on position 1 (first todo)
- `pre_id=2` means operate on position 2 (second todo)
- For `add`, the new item is inserted AFTER the pre_id position

## Action Details
- `done`: Mark the todo at position pre_id as completed. content can be evidence or null.
- `edit`: Replace the content of todo at position pre_id with new content.
- `add`: Insert a new todo AFTER position pre_id. content is required.
- `delete`: Remove the todo at position pre_id. content is null.

## Guidelines
1. **At minimum**: Mark the target todo as done if the iteration provided sufficient information
2. **Partial completion**: If a todo is only partially answered, split it:
   - Edit the original to reflect what was completed
   - Mark it as done
   - Add a new todo for the remaining part
3. **Discovered coverage**: If iteration results also cover other todos, mark them too
4. **Conservative**: Only mark as done if there's clear evidence from tool calls
"""
        return prompt

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        """Build user prompt"""
        template = self.get_prompt("user_template") if self.has_prompts() else None
        if not template:
            template = """## Current Todo-list
{todo_list}

## Target Todo (being worked on)
{target_todo}

## This Iteration's Tool Call Results
{tool_call_history}

## Task
Based on the tool call results from this iteration:
1. Determine if the target todo ({target_todo_id}) can be marked as done
2. Check if the results also complete or affect other todos
3. If a todo is partially complete, consider splitting it

Output a JSON object with an "actions" array.
Each action must have: pre_id (position), action (done/edit/add/delete), content (if needed).
If no changes needed, return empty actions array: {{"actions": []}}
"""
        return template.format(**context)

    # ------------------------------------------------------------------ #
    # Response Parsing
    # ------------------------------------------------------------------ #
    def _parse_actions(self, response: str) -> List[dict[str, Any]]:
        """Parse the actions from LLM response"""
        parsed_data = extract_json_from_text(response)

        if not parsed_data or not isinstance(parsed_data, dict):
            self.logger.warning("[SolveNoteAgent] Failed to parse JSON response")
            return []

        actions = parsed_data.get("actions", [])
        if not isinstance(actions, list):
            return []

        valid_actions = []
        for action in actions:
            if not isinstance(action, dict):
                continue

            pre_id = action.get("pre_id")
            action_type = str(action.get("action", "")).strip().lower()
            content = action.get("content")

            # Validate pre_id
            if pre_id is None:
                self.logger.warning("[SolveNoteAgent] Missing pre_id in action")
                continue
            
            try:
                pre_id = int(pre_id)
            except (TypeError, ValueError):
                self.logger.warning(f"[SolveNoteAgent] Invalid pre_id: {pre_id}")
                continue

            # Validate action type
            if action_type not in self.VALID_ACTIONS:
                self.logger.warning(f"[SolveNoteAgent] Invalid action: {action_type}")
                continue

            # Validate content for actions that need it
            if action_type in {"edit", "add"} and not content:
                self.logger.warning(f"[SolveNoteAgent] {action_type} requires content")
                continue

            # Normalize content
            if content is not None:
                content = str(content).strip()
                if not content:
                    content = None

            valid_actions.append({
                "pre_id": pre_id,
                "action": action_type,
                "content": content,
            })

        return valid_actions


# Legacy compatibility wrapper
class SolveNoteAgentLegacy(SolveNoteAgent):
    """Legacy wrapper for backward compatibility"""

    async def process_legacy(
        self,
        solve_memory: SolveMemory,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """
        Legacy process method - gets context from solve_memory.
        """
        current_iter = solve_memory.get_current_iteration()
        if not current_iter:
            return {
                "success": False,
                "reason": "No current iteration",
                "actions": [],
                "completed_todos": [],
            }

        target_todo = solve_memory.get_todo(current_iter.target_todo_id)
        if not target_todo:
            return {
                "success": False,
                "reason": f"Target todo {current_iter.target_todo_id} not found",
                "actions": [],
                "completed_todos": [],
            }

        return await self.process(
            solve_memory=solve_memory,
            iteration_record=current_iter,
            target_todo=target_todo,
            verbose=verbose,
        )
