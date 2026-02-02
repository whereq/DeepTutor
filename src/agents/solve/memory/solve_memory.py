#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SolveMemory - Todo-list based solving memory system

Manages the todo-list milestones and solve outputs for the problem-solving process.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


def _now() -> str:
    return datetime.utcnow().isoformat()


# ========================================================================== #
# Data Structures
# ========================================================================== #


@dataclass
class TodoItem:
    """Single item in the todo-list (milestone)"""

    todo_id: str  # e.g., "T1", "T2"
    description: str  # Milestone description
    status: str = "pending"  # pending | in_progress | completed | skipped
    completed_at: Optional[str] = None
    completed_by_output_id: Optional[str] = None  # Which output completed this todo
    completed_by_iteration_id: Optional[str] = None  # Which iteration completed this todo
    evidence: Optional[str] = None  # Evidence for completion
    parent_id: Optional[str] = None  # Parent todo ID if this was split from another
    iteration_evidence: List[str] = field(default_factory=list)  # cite_ids that support completion
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoItem":
        data.setdefault("status", "pending")
        data.setdefault("completed_at", None)
        data.setdefault("completed_by_output_id", None)
        data.setdefault("completed_by_iteration_id", None)
        data.setdefault("evidence", None)
        data.setdefault("parent_id", None)
        data.setdefault("iteration_evidence", [])
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return cls(**data)

    def mark_completed(
        self,
        output_id: str = "",
        evidence: str = "",
        iteration_id: str = "",
        cite_ids: Optional[List[str]] = None,
    ):
        self.status = "completed"
        self.completed_at = _now()
        self.completed_by_output_id = output_id
        self.completed_by_iteration_id = iteration_id
        self.evidence = evidence
        if cite_ids:
            self.iteration_evidence = cite_ids
        self.updated_at = _now()

    def mark_in_progress(self):
        self.status = "in_progress"
        self.updated_at = _now()

    def mark_skipped(self, reason: str = ""):
        self.status = "skipped"
        self.evidence = reason
        self.updated_at = _now()


@dataclass
class NoteAction:
    """Single action from note_agent to edit todo-list"""

    pre_id: int  # Position reference: 0 means before T1, 1 means after T1, etc.
    action: str  # done | edit | add | delete
    content: Optional[str] = None  # Required for edit/add, null for done/delete
    target_todo_id: Optional[str] = None  # Resolved todo_id after processing

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoteAction":
        data.setdefault("content", None)
        data.setdefault("target_todo_id", None)
        return cls(**data)


@dataclass
class IterationRecord:
    """Record of a single solve iteration (inner loop)"""

    iteration_id: str  # e.g., "iter_1", "iter_2"
    target_todo_id: str  # The todo being worked on
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    note_actions: List[NoteAction] = field(default_factory=list)
    completed_todos: List[str] = field(default_factory=list)  # todo_ids completed this iteration
    step_response: Optional[str] = None  # Response generated for this iteration
    used_citations: List[str] = field(default_factory=list)
    status: str = "in_progress"  # in_progress | completed | failed
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        data["note_actions"] = [na.to_dict() for na in self.note_actions]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IterationRecord":
        tool_calls = [ToolCallRecord.from_dict(tc) for tc in data.get("tool_calls", [])]
        note_actions = [NoteAction.from_dict(na) for na in data.get("note_actions", [])]
        data.setdefault("completed_todos", [])
        data.setdefault("step_response", None)
        data.setdefault("used_citations", [])
        data.setdefault("status", "in_progress")
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return cls(
            iteration_id=data["iteration_id"],
            target_todo_id=data["target_todo_id"],
            tool_calls=tool_calls,
            note_actions=note_actions,
            completed_todos=data["completed_todos"],
            step_response=data["step_response"],
            used_citations=data["used_citations"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def append_tool_call(self, tool_call: ToolCallRecord):
        """Add a tool call to this iteration"""
        self.tool_calls.append(tool_call)
        self.updated_at = _now()

    def set_note_actions(self, actions: List[NoteAction]):
        """Set the note actions from note_agent"""
        self.note_actions = actions
        self.updated_at = _now()

    def set_completed_todos(self, todo_ids: List[str]):
        """Set the list of completed todos"""
        self.completed_todos = todo_ids
        self.updated_at = _now()

    def set_step_response(self, response: str, used_citations: Optional[List[str]] = None):
        """Set the step response and mark iteration as completed"""
        self.step_response = response
        self.used_citations = used_citations or []
        self.status = "completed"
        self.updated_at = _now()

    def get_all_cite_ids(self) -> List[str]:
        """Get all cite_ids from tool calls"""
        return [tc.cite_id for tc in self.tool_calls if tc.cite_id]

    def format_tool_call_chain(self) -> str:
        """Format tool call chain for context"""
        if not self.tool_calls:
            return "(No tool calls)"
        lines = []
        for tc in self.tool_calls:
            summary = tc.summary or tc.raw_answer[:200] if tc.raw_answer else "(pending)"
            lines.append(
                f"- [{tc.tool_type}] {tc.query}\n"
                f"  cite_id: {tc.cite_id or 'N/A'}\n"
                f"  summary: {summary}"
            )
        return "\n".join(lines)


@dataclass
class ToolCallRecord:
    """Single tool call record"""

    tool_type: str
    query: str
    cite_id: Optional[str] = None
    raw_answer: Optional[str] = None
    summary: Optional[str] = None
    status: str = "pending"  # pending | running | success | failed | none | finish
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    call_id: str = field(default_factory=lambda: f"tc_{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCallRecord":
        data.setdefault("metadata", {})
        data.setdefault("status", "pending")
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        data.setdefault("call_id", f"tc_{uuid.uuid4().hex[:8]}")
        return cls(**data)

    def mark_running(self):
        self.status = "running"
        self.updated_at = _now()

    def mark_result(
        self,
        raw_answer: str,
        summary: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.raw_answer = raw_answer
        self.summary = summary
        self.status = status
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = _now()


@dataclass
class SolveOutput:
    """Single output from a solve iteration"""

    output_id: str  # e.g., "O1", "O2"
    selected_todo_id: str  # Which todo item was selected
    reasoning: str  # Why this todo was selected
    action_type: str  # tool_call | direct_answer | skip
    content: str = ""  # The actual content/answer generated
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    used_citations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolveOutput":
        tool_calls = [ToolCallRecord.from_dict(tc) for tc in data.get("tool_calls", [])]
        data.setdefault("content", "")
        data.setdefault("used_citations", [])
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return cls(
            output_id=data["output_id"],
            selected_todo_id=data["selected_todo_id"],
            reasoning=data.get("reasoning", ""),
            action_type=data.get("action_type", "direct_answer"),
            content=data["content"],
            tool_calls=tool_calls,
            used_citations=data["used_citations"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def append_tool_call(self, tool_call: ToolCallRecord):
        self.tool_calls.append(tool_call)
        self.updated_at = _now()

    def set_content(self, content: str, used_citations: Optional[List[str]] = None):
        self.content = content
        if used_citations:
            self.used_citations = used_citations
        self.updated_at = _now()


# ========================================================================== #
# SolveChainStep (kept for backward compatibility with ResponseAgent)
# ========================================================================== #


@dataclass
class SolveChainStep:
    """Single step structure in solve-chain (kept for backward compatibility)"""

    step_id: str
    step_target: str
    available_cite: List[str] = field(default_factory=list)
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    step_response: Optional[str] = None
    status: str = "undone"  # undone | in_progress | waiting_response | done | failed
    used_citations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolveChainStep":
        tool_calls = [ToolCallRecord.from_dict(tc) for tc in data.get("tool_calls", [])]
        data.setdefault("available_cite", [])
        data.setdefault("used_citations", [])
        data.setdefault("status", "undone")
        data.setdefault("step_response", None)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return cls(
            step_id=data["step_id"],
            step_target=data.get("step_target", data.get("plan", "")),
            available_cite=data["available_cite"],
            tool_calls=tool_calls,
            step_response=data.get("step_response", data.get("content")),
            status=data["status"],
            used_citations=data.get("used_citations", []),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def append_tool_call(self, tool_call: ToolCallRecord):
        self.tool_calls.append(tool_call)
        self.updated_at = _now()
        if self.status == "undone":
            self.status = "in_progress"

    def update_response(self, response: str, used_citations: Optional[List[str]] = None):
        self.step_response = response
        self.status = "done"
        self.used_citations = used_citations or []
        self.updated_at = _now()

    def mark_waiting_response(self):
        self.status = "waiting_response"
        self.updated_at = _now()


# ========================================================================== #
# SolveMemory
# ========================================================================== #


class SolveMemory:
    """Todo-list based solving memory storage"""

    def __init__(
        self,
        task_id: Optional[str] = None,
        user_question: str = "",
        output_dir: Optional[str] = None,
    ):
        self.task_id = task_id or f"solve_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.user_question = user_question
        self.output_dir = output_dir

        self.version = "solve_chain_v2"  # Updated version for new architecture
        self.created_at = _now()
        self.updated_at = _now()

        # Todo-list based solving
        self.todo_list: List[TodoItem] = []
        self.solve_outputs: List[SolveOutput] = []  # Kept for backward compatibility
        self.iteration_records: List[IterationRecord] = []  # New: iteration-based tracking

        self.metadata: Dict[str, Any] = {
            "total_todos": 0,
            "completed_todos": 0,
            "total_outputs": 0,
            "total_tool_calls": 0,
            "total_iterations": 0,
        }

        self.file_path = Path(output_dir) / "solve_chain.json" if output_dir else None
        self.iteration_file_path = (
            Path(output_dir) / "iteration_records.json" if output_dir else None
        )

    # ------------------------------------------------------------------ #
    # Load/Save
    # ------------------------------------------------------------------ #
    @classmethod
    def load_or_create(
        cls,
        output_dir: str,
        user_question: str = "",
        task_id: Optional[str] = None,
    ) -> "SolveMemory":
        file_path = Path(output_dir) / "solve_chain.json"
        if not file_path.exists():
            return cls(
                task_id=task_id,
                user_question=user_question,
                output_dir=output_dir,
            )

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        memory = cls(
            task_id=data.get("task_id", task_id),
            user_question=data.get("user_question", user_question),
            output_dir=output_dir,
        )

        memory.version = data.get("version", "solve_chain_v2")
        memory.created_at = data.get("created_at", memory.created_at)
        memory.updated_at = data.get("updated_at", memory.updated_at)
        memory.metadata = data.get("metadata", memory.metadata)

        # Load todo-list data
        memory.todo_list = [
            TodoItem.from_dict(todo) for todo in data.get("todo_list", [])
        ]
        memory.solve_outputs = [
            SolveOutput.from_dict(output) for output in data.get("solve_outputs", [])
        ]

        # Load iteration records (from separate file or inline)
        iteration_file_path = Path(output_dir) / "iteration_records.json"
        if iteration_file_path.exists():
            with open(iteration_file_path, "r", encoding="utf-8") as f:
                iter_data = json.load(f)
            memory.iteration_records = [
                IterationRecord.from_dict(rec) for rec in iter_data.get("iterations", [])
            ]
        else:
            # Try loading from inline data (backward compatibility)
            memory.iteration_records = [
                IterationRecord.from_dict(rec)
                for rec in data.get("iteration_records", [])
            ]

        return memory

    def save(self):
        if not self.file_path:
            raise ValueError("output_dir not set, cannot save solve-chain")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = _now()
        payload = self.to_dict()
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        # Also save iteration records to separate file
        self.save_iteration_records()

    def save_iteration_records(self):
        """Save iteration records to a separate JSON file"""
        if not self.iteration_file_path:
            return
        self.iteration_file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "task_id": self.task_id,
            "created_at": self.created_at,
            "updated_at": _now(),
            "iterations": [rec.to_dict() for rec in self.iteration_records],
        }
        with open(self.iteration_file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "task_id": self.task_id,
            "user_question": self.user_question,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "todo_list": [todo.to_dict() for todo in self.todo_list],
            "solve_outputs": [output.to_dict() for output in self.solve_outputs],
            # iteration_records saved to separate file, but keep reference
            "iteration_records_file": "iteration_records.json",
        }

    # ------------------------------------------------------------------ #
    # Todo-list Management
    # ------------------------------------------------------------------ #
    def create_todo_list(self, todos: List[TodoItem]):
        """Initialize the todo-list"""
        self.todo_list = todos
        self.metadata["total_todos"] = len(todos)
        self.metadata["completed_todos"] = sum(1 for t in todos if t.status == "completed")
        self.updated_at = _now()

    def get_todo(self, todo_id: str) -> Optional[TodoItem]:
        """Get a todo item by ID"""
        return next((todo for todo in self.todo_list if todo.todo_id == todo_id), None)

    def get_pending_todos(self) -> List[TodoItem]:
        """Get all pending todo items"""
        return [todo for todo in self.todo_list if todo.status in {"pending", "in_progress"}]

    def get_completed_todos(self) -> List[TodoItem]:
        """Get all completed todo items"""
        return [todo for todo in self.todo_list if todo.status == "completed"]

    def is_all_completed(self) -> bool:
        """Check if all required todos are completed (completed or skipped)"""
        if not self.todo_list:
            return False
        return all(todo.status in {"completed", "skipped"} for todo in self.todo_list)

    def mark_todo_completed(self, todo_id: str, output_id: str, evidence: str = ""):
        """Mark a todo item as completed"""
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")
        todo.mark_completed(output_id=output_id, evidence=evidence)
        self.metadata["completed_todos"] = sum(1 for t in self.todo_list if t.status == "completed")
        self.updated_at = _now()

    def mark_todo_in_progress(self, todo_id: str):
        """Mark a todo item as in progress"""
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")
        todo.mark_in_progress()
        self.updated_at = _now()

    def mark_todo_skipped(self, todo_id: str, reason: str = ""):
        """Mark a todo item as skipped"""
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")
        todo.mark_skipped(reason=reason)
        self.updated_at = _now()

    def get_todo_list_with_status(self) -> str:
        """Get formatted todo-list with status markers"""
        lines = []
        for todo in self.todo_list:
            status_marker = {
                "pending": "[ ]",
                "in_progress": "[~]",
                "completed": "[x]",
                "skipped": "[-]",
            }.get(todo.status, "[ ]")
            lines.append(f"{status_marker} {todo.todo_id}: {todo.description}")
        return "\n".join(lines)

    def get_next_pending_todo(self) -> Optional[TodoItem]:
        """Get the first pending todo item"""
        for todo in self.todo_list:
            if todo.status == "pending":
                return todo
        return None

    # ------------------------------------------------------------------ #
    # Todo-list Editing (for NoteAgent)
    # ------------------------------------------------------------------ #
    def insert_todo_after(
        self,
        pre_id: int,
        content: str,
        parent_id: Optional[str] = None,
    ) -> TodoItem:
        """
        Insert a new todo after the specified position.

        Args:
            pre_id: Position reference (0 = before first, 1 = after first, etc.)
            content: Description of the new todo
            parent_id: Optional parent todo ID if this is a split

        Returns:
            The newly created TodoItem
        """
        # Create new todo with temporary ID
        new_todo = TodoItem(
            todo_id=f"T{pre_id + 1}_new",  # Temporary, will be renumbered
            description=content,
            status="pending",
            parent_id=parent_id,
        )

        # Insert at the correct position
        insert_pos = min(pre_id, len(self.todo_list))
        self.todo_list.insert(insert_pos, new_todo)

        # Renumber all todos
        self._renumber_todos()

        self.metadata["total_todos"] = len(self.todo_list)
        self.updated_at = _now()
        return new_todo

    def edit_todo(self, todo_id: str, new_content: str) -> TodoItem:
        """
        Edit the content of a todo item.

        Args:
            todo_id: ID of the todo to edit
            new_content: New description

        Returns:
            The updated TodoItem
        """
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")

        todo.description = new_content
        todo.updated_at = _now()
        self.updated_at = _now()
        return todo

    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a todo item.

        Args:
            todo_id: ID of the todo to delete

        Returns:
            True if deleted, False if not found
        """
        todo = self.get_todo(todo_id)
        if not todo:
            return False

        self.todo_list.remove(todo)
        self._renumber_todos()

        self.metadata["total_todos"] = len(self.todo_list)
        self.updated_at = _now()
        return True

    def _renumber_todos(self):
        """Renumber all todos to ensure sequential IDs (T1, T2, T3, ...)"""
        for idx, todo in enumerate(self.todo_list, 1):
            todo.todo_id = f"T{idx}"

    def apply_note_actions(
        self,
        actions: List[NoteAction],
        iteration_id: str = "",
        cite_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Apply a list of note actions to modify the todo-list.

        Args:
            actions: List of NoteAction objects
            iteration_id: Current iteration ID for tracking
            cite_ids: Citation IDs from this iteration

        Returns:
            List of todo_ids that were marked as completed
        """
        completed_todos: List[str] = []

        # Sort actions by pre_id in reverse order for insertions
        # This ensures earlier insertions don't affect later positions
        sorted_actions = sorted(actions, key=lambda a: a.pre_id, reverse=True)

        for action in sorted_actions:
            pre_id = action.pre_id
            action_type = action.action.lower()

            if action_type == "done":
                # Mark the todo at position pre_id as completed
                if 0 < pre_id <= len(self.todo_list):
                    todo = self.todo_list[pre_id - 1]
                    todo.mark_completed(
                        output_id="",
                        evidence=action.content or "",
                        iteration_id=iteration_id,
                        cite_ids=cite_ids,
                    )
                    completed_todos.append(todo.todo_id)
                    action.target_todo_id = todo.todo_id

            elif action_type == "edit":
                if action.content and 0 < pre_id <= len(self.todo_list):
                    todo = self.todo_list[pre_id - 1]
                    todo.description = action.content
                    todo.updated_at = _now()
                    action.target_todo_id = todo.todo_id

            elif action_type == "add":
                if action.content:
                    # Determine parent_id from the previous todo
                    parent_id = None
                    if 0 < pre_id <= len(self.todo_list):
                        parent_id = self.todo_list[pre_id - 1].todo_id

                    new_todo = TodoItem(
                        todo_id=f"T_new_{pre_id}",
                        description=action.content,
                        status="pending",
                        parent_id=parent_id,
                    )
                    # Insert after pre_id position
                    insert_pos = min(pre_id, len(self.todo_list))
                    self.todo_list.insert(insert_pos, new_todo)
                    action.target_todo_id = new_todo.todo_id

            elif action_type == "delete":
                if 0 < pre_id <= len(self.todo_list):
                    todo = self.todo_list[pre_id - 1]
                    action.target_todo_id = todo.todo_id
                    self.todo_list.remove(todo)

        # Renumber todos after all actions
        self._renumber_todos()

        # Update metadata
        self.metadata["total_todos"] = len(self.todo_list)
        self.metadata["completed_todos"] = sum(
            1 for t in self.todo_list if t.status == "completed"
        )
        self.updated_at = _now()

        return completed_todos

    def get_todo_by_position(self, position: int) -> Optional[TodoItem]:
        """Get todo by 1-based position"""
        if 0 < position <= len(self.todo_list):
            return self.todo_list[position - 1]
        return None

    # ------------------------------------------------------------------ #
    # Iteration Management
    # ------------------------------------------------------------------ #
    def create_iteration(self, target_todo_id: str) -> IterationRecord:
        """
        Create a new iteration record.

        Args:
            target_todo_id: The todo being worked on

        Returns:
            New IterationRecord
        """
        iteration_id = f"iter_{len(self.iteration_records) + 1}"
        record = IterationRecord(
            iteration_id=iteration_id,
            target_todo_id=target_todo_id,
        )
        self.iteration_records.append(record)
        self.metadata["total_iterations"] = len(self.iteration_records)
        self.updated_at = _now()
        return record

    def get_iteration(self, iteration_id: str) -> Optional[IterationRecord]:
        """Get an iteration record by ID"""
        return next(
            (rec for rec in self.iteration_records if rec.iteration_id == iteration_id),
            None,
        )

    def get_current_iteration(self) -> Optional[IterationRecord]:
        """Get the most recent iteration record"""
        return self.iteration_records[-1] if self.iteration_records else None

    def get_current_iteration_id(self) -> str:
        """Get the current iteration ID or generate new one"""
        if self.iteration_records:
            return self.iteration_records[-1].iteration_id
        return f"iter_{len(self.iteration_records) + 1}"

    def get_all_step_responses(self) -> List[str]:
        """Get all step responses from completed iterations"""
        return [
            rec.step_response
            for rec in self.iteration_records
            if rec.step_response and rec.status == "completed"
        ]

    def get_all_iteration_citations(self) -> List[str]:
        """Get all unique citations from all iterations"""
        citations = []
        for rec in self.iteration_records:
            for cite in rec.used_citations:
                if cite not in citations:
                    citations.append(cite)
        return citations

    # ------------------------------------------------------------------ #
    # Solve Output Management
    # ------------------------------------------------------------------ #
    def append_solve_output(self, output: SolveOutput):
        """Add a new solve output"""
        self.solve_outputs.append(output)
        self.metadata["total_outputs"] = len(self.solve_outputs)
        self.metadata["total_tool_calls"] = sum(
            len(o.tool_calls) for o in self.solve_outputs
        )
        self.updated_at = _now()

    def get_solve_output(self, output_id: str) -> Optional[SolveOutput]:
        """Get a solve output by ID"""
        return next((o for o in self.solve_outputs if o.output_id == output_id), None)

    def get_latest_output(self) -> Optional[SolveOutput]:
        """Get the most recent solve output"""
        return self.solve_outputs[-1] if self.solve_outputs else None

    def get_next_output_id(self) -> str:
        """Generate the next output ID"""
        return f"O{len(self.solve_outputs) + 1}"

    def get_all_output_contents(self) -> List[str]:
        """Get all output contents for final answer compilation"""
        return [o.content for o in self.solve_outputs if o.content]

    def get_all_used_citations(self) -> List[str]:
        """Get all unique citations used across all outputs"""
        citations = []
        for output in self.solve_outputs:
            for cite in output.used_citations:
                if cite not in citations:
                    citations.append(cite)
        return citations

    def update_output_content(
        self,
        output_id: str,
        content: str,
        used_citations: Optional[List[str]] = None,
    ):
        """Update the content of a solve output"""
        output = self.get_solve_output(output_id)
        if not output:
            raise ValueError(f"Output {output_id} not found")
        output.set_content(content=content, used_citations=used_citations)
        self.updated_at = _now()

    def append_tool_call_to_output(
        self,
        output_id: str,
        tool_type: str,
        query: str,
        cite_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolCallRecord:
        """Append a tool call to a solve output"""
        output = self.get_solve_output(output_id)
        if not output:
            raise ValueError(f"Output {output_id} not found")
        record = ToolCallRecord(
            tool_type=tool_type,
            query=query,
            cite_id=cite_id,
            metadata=metadata or {},
        )
        output.append_tool_call(record)
        self.metadata["total_tool_calls"] = sum(
            len(o.tool_calls) for o in self.solve_outputs
        )
        self.updated_at = _now()
        return record

    def update_tool_call_in_output(
        self,
        output_id: str,
        call_id: str,
        raw_answer: str,
        summary: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update a tool call result in a solve output"""
        output = self.get_solve_output(output_id)
        if not output:
            raise ValueError(f"Output {output_id} not found")
        record = next((tc for tc in output.tool_calls if tc.call_id == call_id), None)
        if not record:
            raise ValueError(f"Tool call {call_id} not found in output {output_id}")
        record.mark_result(raw_answer=raw_answer, summary=summary, status=status, metadata=metadata)
        self.updated_at = _now()

    # ------------------------------------------------------------------ #
    # Summary and History
    # ------------------------------------------------------------------ #
    def get_summary(self) -> str:
        """Get a summary of the current state"""
        lines = [
            f"Task ID: {self.task_id}",
            f"Question: {self.user_question}",
            f"Total Todos: {self.metadata.get('total_todos', len(self.todo_list))}",
            f"Completed Todos: {self.metadata.get('completed_todos', 0)}",
            f"Total Outputs: {len(self.solve_outputs)}",
        ]
        for todo in self.todo_list:
            status_icon = {
                "pending": "[ ]",
                "in_progress": "[~]",
                "completed": "[x]",
                "skipped": "[-]",
            }.get(todo.status, "[ ]")
            lines.append(f"{status_icon} {todo.todo_id}: {todo.description[:60]}...")
        return "\n".join(lines)

    def format_todo_list_for_log(self) -> str:
        """Format todo-list for logging output"""
        if not self.todo_list:
            return "(No todo-list generated)"

        lines = [
            "=" * 60,
            "Generated Todo-list:",
            "-" * 60,
        ]
        for todo in self.todo_list:
            status_icon = {
                "pending": "[ ]",
                "in_progress": "[~]",
                "completed": "[x]",
                "skipped": "[-]",
            }.get(todo.status, "[ ]")
            lines.append(f"  {status_icon} {todo.todo_id}: {todo.description}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def save_todo_history(self, output_dir: str) -> Path:
        """
        Save todo-list execution history to a markdown file.

        Args:
            output_dir: Output directory path

        Returns:
            Path to the saved history file
        """
        history_file = Path(output_dir) / "todo_history.md"

        with open(history_file, "w", encoding="utf-8") as f:
            f.write("# Todo-list Execution History\n\n")
            f.write(f"**Question:** {self.user_question}\n\n")
            f.write(f"**Task ID:** {self.task_id}\n\n")
            f.write(f"**Created:** {self.created_at}\n\n")

            # Write todo-list section
            f.write("## Todo-list\n\n")
            f.write("| Status | ID | Description | Completed By |\n")
            f.write("|--------|----|-----------|--------------|\n")
            for todo in self.todo_list:
                status_icon = {
                    "pending": "⬜",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "skipped": "⏭️",
                }.get(todo.status, "⬜")
                completed_by = todo.completed_by_output_id or "-"
                # Escape pipe characters in description
                desc = todo.description.replace("|", "\\|")
                f.write(f"| {status_icon} | {todo.todo_id} | {desc} | {completed_by} |\n")

            # Write execution outputs section
            if self.solve_outputs:
                f.write("\n## Execution Outputs\n\n")
                for output in self.solve_outputs:
                    f.write(f"### {output.output_id} → {output.selected_todo_id}\n\n")
                    f.write(f"- **Action Type:** {output.action_type}\n")
                    f.write(f"- **Reasoning:** {output.reasoning}\n")

                    if output.tool_calls:
                        f.write(f"- **Tool Calls:** {len(output.tool_calls)}\n")
                        for tc in output.tool_calls:
                            f.write(f"  - `{tc.tool_type}`: {tc.query[:80]}...\n")

                    if output.content:
                        # Truncate long content
                        content_preview = output.content[:500]
                        if len(output.content) > 500:
                            content_preview += "..."
                        f.write(f"\n**Content:**\n\n{content_preview}\n")

                    f.write("\n---\n\n")

            # Write completion evidence section
            completed_todos = [t for t in self.todo_list if t.status == "completed" and t.evidence]
            if completed_todos:
                f.write("## Completion Evidence\n\n")
                for todo in completed_todos:
                    f.write(f"### {todo.todo_id}\n\n")
                    f.write(f"{todo.evidence}\n\n")

            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Todos:** {len(self.todo_list)}\n")
            f.write(f"- **Completed:** {len([t for t in self.todo_list if t.status == 'completed'])}\n")
            f.write(f"- **Skipped:** {len([t for t in self.todo_list if t.status == 'skipped'])}\n")
            f.write(f"- **Total Outputs:** {len(self.solve_outputs)}\n")

        return history_file
