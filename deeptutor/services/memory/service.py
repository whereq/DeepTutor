from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Any

from deeptutor.services.llm import complete as llm_complete
from deeptutor.services.path_service import PathService, get_path_service
from deeptutor.services.session.sqlite_store import SQLiteSessionStore, get_sqlite_session_store


_NO_CHANGE_SENTINEL = "NO_CHANGE"


@dataclass
class MemorySnapshot:
    content: str
    exists: bool
    updated_at: str | None


@dataclass
class MemoryUpdateResult:
    content: str
    changed: bool
    updated_at: str | None


class MemoryService:
    """Lightweight Nanobot-style long-term memory for preferences and context."""

    def __init__(
        self,
        path_service: PathService | None = None,
        store: SQLiteSessionStore | None = None,
    ) -> None:
        self._path_service = path_service or get_path_service()
        self._store = store or get_sqlite_session_store()

    @property
    def memory_path(self) -> Path:
        return self._path_service.get_memory_dir() / "memory.md"

    def read_memory(self) -> str:
        path = self.memory_path
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8").strip()
        except Exception:
            return ""

    def read_snapshot(self) -> MemorySnapshot:
        path = self.memory_path
        content = self.read_memory()
        updated_at = None
        if path.exists():
            try:
                updated_at = datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()
            except Exception:
                updated_at = None
        return MemorySnapshot(
            content=content,
            exists=bool(content) and path.exists(),
            updated_at=updated_at,
        )

    def build_memory_context(self, max_chars: int = 4000) -> str:
        content = self.read_memory()
        if not content:
            return ""
        if len(content) > max_chars:
            content = content[:max_chars].rstrip() + "\n...[truncated]"
        return (
            "## Background Memory\n"
            "Use this memory sparingly.\n"
            "- Only use it when it is directly relevant to the user's current request.\n"
            "- Do not proactively mention, summarize, or connect the request to memory unless that clearly improves the answer.\n"
            "- If the memory is not relevant, ignore it.\n\n"
            f"{content}"
        )

    def get_preferences_text(self) -> str:
        preferences, _context = self._extract_sections(self.read_memory())
        if not preferences:
            return ""
        return "## Preferences\n" + preferences

    def clear_memory(self) -> MemorySnapshot:
        path = self.memory_path
        if path.exists():
            path.unlink()
        return self.read_snapshot()

    def write_memory(self, content: str) -> MemorySnapshot:
        normalized = str(content or "").strip()
        if not normalized:
            return self.clear_memory()
        self._write_memory(normalized)
        return self.read_snapshot()

    async def refresh_from_turn(
        self,
        *,
        user_message: str,
        assistant_message: str,
        session_id: str = "",
        capability: str = "",
        language: str = "en",
        timestamp: str = "",
    ) -> MemoryUpdateResult:
        if not user_message.strip() or not assistant_message.strip():
            snapshot = self.read_snapshot()
            return MemoryUpdateResult(
                content=snapshot.content,
                changed=False,
                updated_at=snapshot.updated_at,
            )

        source_text = (
            f"[Session]\n{session_id or '(unknown)'}\n\n"
            f"[Capability]\n{capability or 'chat'}\n\n"
            f"[Timestamp]\n{timestamp or datetime.now().isoformat()}\n\n"
            f"[User]\n{user_message.strip()}\n\n"
            f"[Assistant]\n{assistant_message.strip()}"
        )
        return await self._rewrite_memory(source_text=source_text, language=language)

    async def refresh_from_session(
        self,
        session_id: str | None = None,
        *,
        language: str = "en",
        max_messages: int = 10,
    ) -> MemoryUpdateResult:
        target_session_id = (session_id or "").strip()
        if not target_session_id:
            sessions = await self._store.list_sessions(limit=1)
            if sessions:
                target_session_id = str(sessions[0].get("session_id", "") or "")

        if not target_session_id:
            snapshot = self.read_snapshot()
            return MemoryUpdateResult(
                content=snapshot.content,
                changed=False,
                updated_at=snapshot.updated_at,
            )

        messages = await self._store.get_messages_for_context(target_session_id)
        relevant = [
            item for item in messages
            if str(item.get("role", "") or "") in {"user", "assistant"}
            and str(item.get("content", "") or "").strip()
        ]
        relevant = relevant[-max_messages:]
        if not relevant:
            snapshot = self.read_snapshot()
            return MemoryUpdateResult(
                content=snapshot.content,
                changed=False,
                updated_at=snapshot.updated_at,
            )

        transcript = []
        for item in relevant:
            role = "User" if item.get("role") == "user" else "Assistant"
            transcript.append(f"{role}: {str(item.get('content', '') or '').strip()}")

        capability = ""
        session = await self._store.get_session(target_session_id)
        if session is not None:
            capability = str(session.get("capability", "") or "")

        source_text = (
            f"[Session]\n{target_session_id}\n\n"
            f"[Capability]\n{capability or 'chat'}\n\n"
            f"[Recent Transcript]\n" + "\n\n".join(transcript)
        )
        return await self._rewrite_memory(source_text=source_text, language=language)

    async def _rewrite_memory(
        self,
        *,
        source_text: str,
        language: str,
    ) -> MemoryUpdateResult:
        current_memory = self.read_memory()
        system_prompt = (
            "You maintain a lightweight long-term memory document for an AI assistant. "
            "Only preserve stable user preferences and durable ongoing context. "
            "Do not store transient chatter, one-off questions, or exhaustive history. "
            f"If nothing should change, return exactly { _NO_CHANGE_SENTINEL }."
        )
        if str(language).lower().startswith("zh"):
            system_prompt = (
                "你负责维护一份轻量长期记忆文档。"
                "只保留稳定的用户偏好和持续性的上下文。"
                "不要记录瞬时闲聊、一次性问题或完整流水账。"
                f"如果无需修改，请只返回 {_NO_CHANGE_SENTINEL}。"
            )

        user_prompt = (
            "Rewrite the full memory document when needed using exactly these sections:\n"
            "## Preferences\n"
            "- ...\n\n"
            "## Context\n"
            "- ...\n\n"
            "Rules:\n"
            "- Keep it short and readable.\n"
            "- Preferences: stable habits, format preferences, recurring ways of working.\n"
            "- Context: ongoing projects, repeated focus areas, open loops that remain relevant.\n"
            "- Remove stale or contradicted items.\n"
            "- If the new interaction adds nothing durable, return NO_CHANGE.\n\n"
            f"[Current memory]\n{current_memory or '(empty)'}\n\n"
            f"[New material]\n{source_text}"
        )
        if str(language).lower().startswith("zh"):
            user_prompt = (
                "如果需要更新，请重写整份 memory 文档，并严格使用下面两个标题：\n"
                "## Preferences\n"
                "- ...\n\n"
                "## Context\n"
                "- ...\n\n"
                "规则：\n"
                "- 文档保持简短、清晰。\n"
                "- Preferences 只写稳定偏好、习惯、长期工作方式。\n"
                "- Context 只写持续性的项目、关注主题、仍然相关的待继续事项。\n"
                "- 过时或被新信息推翻的内容要删除。\n"
                f"- 如果这次没有新增持久信息，请只返回 {_NO_CHANGE_SENTINEL}。\n\n"
                f"[当前 memory]\n{current_memory or '(empty)'}\n\n"
                f"[新增材料]\n{source_text}"
            )

        response = await llm_complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=900,
        )
        normalized = self._normalize_memory_response(response, current_memory)
        changed = normalized != current_memory
        if changed:
            self._write_memory(normalized)
        snapshot = self.read_snapshot()
        return MemoryUpdateResult(
            content=snapshot.content,
            changed=changed,
            updated_at=snapshot.updated_at,
        )

    def _write_memory(self, content: str) -> None:
        path = self.memory_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip(), encoding="utf-8")

    def _normalize_memory_response(self, response: str, current_memory: str) -> str:
        cleaned = self._strip_code_fence(response).strip()
        if not cleaned or cleaned == _NO_CHANGE_SENTINEL:
            return current_memory

        preferences, context = self._extract_sections(cleaned)
        if not preferences and not context:
            return current_memory

        parts = ["## Preferences"]
        parts.append(preferences or "- None recorded yet.")
        parts.append("")
        parts.append("## Context")
        parts.append(context or "- None recorded yet.")
        return "\n".join(parts).strip()

    @staticmethod
    def _strip_code_fence(content: str) -> str:
        cleaned = str(content or "").strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
        return cleaned.strip()

    @staticmethod
    def _extract_sections(content: str) -> tuple[str, str]:
        text = str(content or "").replace("\r\n", "\n").strip()
        preferences = ""
        context = ""

        pref_match = re.search(
            r"##\s*Preferences\s*(.*?)(?=\n##\s*Context\b|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        ctx_match = re.search(
            r"##\s*Context\s*(.*)$",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if pref_match:
            preferences = pref_match.group(1).strip()
        if ctx_match:
            context = ctx_match.group(1).strip()
        return preferences, context


_memory_service: MemoryService | None = None


def get_memory_service() -> MemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service


__all__ = [
    "MemoryService",
    "MemorySnapshot",
    "MemoryUpdateResult",
    "get_memory_service",
]
