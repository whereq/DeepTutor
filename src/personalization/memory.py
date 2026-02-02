# -*- coding: utf-8 -*-
"""
Learning Memory
===============

Markdown-based memory storage for personalization.
Manages long-term memory (MEMORY.md) and daily notes (YYYY-MM-DD.md).
"""

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.services.path_service import get_path_service

logger = logging.getLogger(__name__)


class LearningMemory:
    """
    Manages personalization memory stored in Markdown files.

    Memory Structure:
        data/user/workspace/memory/
        ├── MEMORY.md              # Long-term memory (preferences, weak points, milestones)
        └── YYYY-MM-DD.md          # Daily notes (learning records for each day)

    MEMORY.md Format:
        ## 用户偏好 / User Preferences
        - Preference item 1
        - Preference item 2

        ## 知识薄弱点 / Knowledge Weak Points
        - Weak point 1
        - Weak point 2

        ## 里程碑 / Milestones
        - YYYY-MM-DD: Milestone description
    """

    _instance: Optional["LearningMemory"] = None
    _initialized: bool = False

    MEMORY_FILE = "MEMORY.md"
    SECTIONS = {
        "preferences": "## 用户偏好 / User Preferences",
        "weak_points": "## 知识薄弱点 / Knowledge Weak Points",
        "milestones": "## 里程碑 / Milestones",
    }

    def __new__(cls) -> "LearningMemory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if LearningMemory._initialized:
            return

        self._path_service = get_path_service()
        self._memory_dir = self._path_service.get_memory_dir()
        self._memory_file = self._memory_dir / self.MEMORY_FILE

        # Ensure memory directory exists
        self._memory_dir.mkdir(parents=True, exist_ok=True)

        LearningMemory._initialized = True
        logger.debug(f"LearningMemory initialized at {self._memory_dir}")

    @property
    def memory_dir(self) -> Path:
        """Get the memory directory path."""
        return self._memory_dir

    @property
    def memory_file(self) -> Path:
        """Get the main memory file path (MEMORY.md)."""
        return self._memory_file

    # =========================================================================
    # Long-term Memory (MEMORY.md)
    # =========================================================================

    def read_memory(self) -> str:
        """
        Read the entire MEMORY.md content.

        Returns:
            Content of MEMORY.md, or empty string if file doesn't exist.
        """
        if not self._memory_file.exists():
            return ""

        try:
            return self._memory_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read memory file: {e}")
            return ""

    def write_memory(self, content: str) -> bool:
        """
        Write content to MEMORY.md (overwrites entire file).

        Args:
            content: The complete content to write.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._memory_file.write_text(content, encoding="utf-8")
            logger.debug("Memory file updated")
            return True
        except Exception as e:
            logger.error(f"Failed to write memory file: {e}")
            return False

    def get_section(self, section_name: str) -> List[str]:
        """
        Get items from a specific section of MEMORY.md.

        Args:
            section_name: One of 'preferences', 'weak_points', 'milestones'

        Returns:
            List of items in the section.
        """
        if section_name not in self.SECTIONS:
            logger.warning(f"Unknown section: {section_name}")
            return []

        content = self.read_memory()
        if not content:
            return []

        section_header = self.SECTIONS[section_name]
        items = []

        # Find the section
        lines = content.split("\n")
        in_section = False

        for line in lines:
            if line.strip().startswith("## "):
                if section_header in line:
                    in_section = True
                elif in_section:
                    # Hit next section, stop
                    break
            elif in_section and line.strip().startswith("- "):
                items.append(line.strip()[2:])  # Remove "- " prefix

        return items

    def update_section(self, section_name: str, items: List[str]) -> bool:
        """
        Update a specific section in MEMORY.md.

        Args:
            section_name: One of 'preferences', 'weak_points', 'milestones'
            items: List of items to set in the section

        Returns:
            True if successful, False otherwise.
        """
        if section_name not in self.SECTIONS:
            logger.warning(f"Unknown section: {section_name}")
            return False

        content = self.read_memory()
        section_header = self.SECTIONS[section_name]

        # Build new section content
        new_section_content = f"{section_header}\n"
        for item in items:
            new_section_content += f"- {item}\n"

        if not content:
            # Create new file with all sections
            content = self._create_empty_memory()

        # Replace or append section
        if section_header in content:
            # Find and replace section
            pattern = rf"({re.escape(section_header)})\n(?:- [^\n]*\n)*"
            content = re.sub(pattern, new_section_content, content)
        else:
            # Append new section
            content += f"\n{new_section_content}"

        return self.write_memory(content)

    def append_to_section(self, section_name: str, items: List[str]) -> bool:
        """
        Append items to a specific section in MEMORY.md.

        Args:
            section_name: One of 'preferences', 'weak_points', 'milestones'
            items: List of items to append

        Returns:
            True if successful, False otherwise.
        """
        existing_items = self.get_section(section_name)
        # Avoid duplicates
        new_items = existing_items + [item for item in items if item not in existing_items]
        return self.update_section(section_name, new_items)

    def _create_empty_memory(self) -> str:
        """Create an empty MEMORY.md template."""
        return f"""# 学习记忆 / Learning Memory

{self.SECTIONS['preferences']}

{self.SECTIONS['weak_points']}

{self.SECTIONS['milestones']}
"""

    # =========================================================================
    # Daily Notes (YYYY-MM-DD.md)
    # =========================================================================

    def get_daily_note_path(self, date: Optional[datetime] = None) -> Path:
        """
        Get the path for a daily note file.

        Args:
            date: The date for the note (default: today)

        Returns:
            Path to the daily note file.
        """
        if date is None:
            date = datetime.now()
        filename = date.strftime("%Y-%m-%d") + ".md"
        return self._memory_dir / filename

    def read_daily_note(self, date: Optional[datetime] = None) -> str:
        """
        Read a daily note.

        Args:
            date: The date for the note (default: today)

        Returns:
            Content of the daily note, or empty string if not exists.
        """
        note_path = self.get_daily_note_path(date)
        if not note_path.exists():
            return ""

        try:
            return note_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read daily note: {e}")
            return ""

    def write_daily_note(self, content: str, date: Optional[datetime] = None) -> bool:
        """
        Write content to a daily note (overwrites).

        Args:
            content: The content to write
            date: The date for the note (default: today)

        Returns:
            True if successful, False otherwise.
        """
        note_path = self.get_daily_note_path(date)
        try:
            note_path.write_text(content, encoding="utf-8")
            logger.debug(f"Daily note updated: {note_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to write daily note: {e}")
            return False

    def append_to_daily_note(self, content: str, date: Optional[datetime] = None) -> bool:
        """
        Append content to a daily note.

        Args:
            content: The content to append
            date: The date for the note (default: today)

        Returns:
            True if successful, False otherwise.
        """
        existing = self.read_daily_note(date)
        if existing:
            new_content = existing.rstrip() + "\n\n" + content
        else:
            # Create new daily note with header
            date_obj = date or datetime.now()
            date_str = date_obj.strftime("%Y-%m-%d")
            new_content = f"# 学习笔记 / Daily Notes - {date_str}\n\n{content}"

        return self.write_daily_note(new_content, date)

    def get_recent_notes(self, days: int = 7) -> Dict[str, str]:
        """
        Get daily notes from the recent N days.

        Args:
            days: Number of recent days to retrieve (default: 7)

        Returns:
            Dictionary mapping date strings to note contents.
        """
        notes = {}
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            content = self.read_daily_note(date)
            if content:
                notes[date_str] = content

        return notes

    # =========================================================================
    # Preference Context for Prompt Injection
    # =========================================================================

    def get_preference_context(self, max_length: int = 2000) -> str:
        """
        Get formatted preference context for prompt injection.

        Reads MEMORY.md and formats it for inclusion in agent prompts.
        Returns empty string if no memory exists.

        Args:
            max_length: Maximum length of the context string

        Returns:
            Formatted preference context, or empty string.
        """
        memory_content = self.read_memory()
        if not memory_content:
            return ""

        # Extract relevant sections
        preferences = self.get_section("preferences")
        weak_points = self.get_section("weak_points")

        if not preferences and not weak_points:
            return ""

        # Build context
        context_parts = []

        if preferences:
            context_parts.append("User Preferences:")
            for pref in preferences[:5]:  # Limit to top 5
                context_parts.append(f"  - {pref}")

        if weak_points:
            context_parts.append("Knowledge Weak Points:")
            for wp in weak_points[:5]:  # Limit to top 5
                context_parts.append(f"  - {wp}")

        context = "\n".join(context_parts)

        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length - 3] + "..."

        return context

    def get_full_context(self, recent_days: int = 7, max_length: int = 4000) -> str:
        """
        Get full context including memory and recent notes.

        Args:
            recent_days: Number of recent days to include
            max_length: Maximum total length

        Returns:
            Full formatted context string.
        """
        parts = []

        # Add preference context
        pref_context = self.get_preference_context(max_length // 2)
        if pref_context:
            parts.append(pref_context)

        # Add recent notes summary
        recent_notes = self.get_recent_notes(recent_days)
        if recent_notes:
            parts.append("\nRecent Learning Activity:")
            for date_str, content in list(recent_notes.items())[:3]:
                # Take first 200 chars of each note
                summary = content[:200].replace("\n", " ")
                if len(content) > 200:
                    summary += "..."
                parts.append(f"  [{date_str}]: {summary}")

        context = "\n".join(parts)

        if len(context) > max_length:
            context = context[:max_length - 3] + "..."

        return context

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._initialized = False


# Module-level singleton accessor
_learning_memory: Optional[LearningMemory] = None


def get_learning_memory() -> LearningMemory:
    """
    Get the singleton LearningMemory instance.

    Returns:
        The global LearningMemory instance.
    """
    global _learning_memory
    if _learning_memory is None:
        _learning_memory = LearningMemory()
    return _learning_memory
