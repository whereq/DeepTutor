"""
SkillService
============

Loads user-authored SKILL.md files from ``data/user/workspace/skills/``.

Each skill lives in its own directory:

    data/user/workspace/skills/<name>/SKILL.md

The file starts with a YAML frontmatter block holding ``name`` and
``description`` (optionally ``triggers``), followed by Markdown body that
is injected verbatim into the chat system prompt when the skill is active.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from typing import Any

import yaml

from deeptutor.services.path_service import get_path_service

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


@dataclass(slots=True)
class SkillInfo:
    name: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "description": self.description}


@dataclass(slots=True)
class SkillDetail:
    name: str
    description: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "content": self.content,
        }


class SkillNotFoundError(Exception):
    pass


class SkillExistsError(Exception):
    pass


class InvalidSkillNameError(Exception):
    pass


class SkillService:
    """CRUD + selection for SKILL.md files under the user workspace."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or (get_path_service().get_workspace_dir() / "skills")

    @property
    def root(self) -> Path:
        return self._root

    # ── path helpers ────────────────────────────────────────────────────

    def _validate_name(self, name: str) -> str:
        candidate = (name or "").strip().lower()
        if not _NAME_RE.match(candidate):
            raise InvalidSkillNameError("Skill name must match ^[a-z0-9][a-z0-9-]{0,63}$")
        return candidate

    def _skill_dir(self, name: str) -> Path:
        return self._root / self._validate_name(name)

    def _skill_file(self, name: str) -> Path:
        return self._skill_dir(name) / "SKILL.md"

    # ── parsing ─────────────────────────────────────────────────────────

    @staticmethod
    def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
        match = _FRONTMATTER_RE.match(content)
        if not match:
            return {}, content
        raw = match.group(1)
        body = content[match.end() :]
        try:
            data = yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        return data, body

    def _load_info(self, name: str) -> SkillInfo | None:
        file = self._skill_file(name)
        if not file.exists():
            return None
        try:
            text = file.read_text(encoding="utf-8")
        except OSError:
            return None
        meta, _ = self._parse_frontmatter(text)
        description = str(meta.get("description") or "").strip()
        return SkillInfo(name=name, description=description)

    # ── public read API ─────────────────────────────────────────────────

    def list_skills(self) -> list[SkillInfo]:
        if not self._root.exists():
            return []
        out: list[SkillInfo] = []
        for entry in sorted(self._root.iterdir()):
            if not entry.is_dir():
                continue
            try:
                info = self._load_info(entry.name)
            except InvalidSkillNameError:
                continue
            if info is not None:
                out.append(info)
        return out

    def get_detail(self, name: str) -> SkillDetail:
        file = self._skill_file(name)
        if not file.exists():
            raise SkillNotFoundError(name)
        text = file.read_text(encoding="utf-8")
        meta, _ = self._parse_frontmatter(text)
        description = str(meta.get("description") or "").strip()
        return SkillDetail(name=name, description=description, content=text)

    def load_for_context(self, names: list[str]) -> str:
        """Render selected skills into a single system-prompt block.

        Frontmatter is stripped; body is concatenated under a shared header
        so the LLM treats the section as authoritative behavior guidance.
        """
        if not names:
            return ""
        parts: list[str] = []
        for name in names:
            try:
                detail = self.get_detail(name)
            except (SkillNotFoundError, InvalidSkillNameError):
                continue
            _, body = self._parse_frontmatter(detail.content)
            body = body.strip()
            if not body:
                continue
            parts.append(f"### Skill: {detail.name}\n\n{body}")
        if not parts:
            return ""
        return (
            "## Active Skills\n"
            "Follow the playbooks below. They override generic defaults.\n\n"
            + "\n\n---\n\n".join(parts)
        )

    # ── auto-select (keyword based, no LLM) ─────────────────────────────

    def auto_select(self, user_message: str, limit: int = 1) -> list[str]:
        """Pick the most relevant skill(s) for the message via keyword scoring.

        Scoring rules (cheap and predictable):
          - +3 for each frontmatter ``triggers`` term that appears in the message.
          - +1 for each non-stopword token from ``description`` that appears.
        """
        message = (user_message or "").lower()
        if not message.strip():
            return []
        scored: list[tuple[int, str]] = []
        for entry in sorted((self._root.iterdir() if self._root.exists() else [])):
            if not entry.is_dir():
                continue
            try:
                detail = self.get_detail(entry.name)
            except (SkillNotFoundError, InvalidSkillNameError):
                continue
            meta, _ = self._parse_frontmatter(detail.content)
            score = 0
            for trig in meta.get("triggers") or []:
                term = str(trig).strip().lower()
                if term and term in message:
                    score += 3
            for token in re.findall(r"[\w\u4e00-\u9fff]{3,}", detail.description.lower()):
                if token in message:
                    score += 1
            if score > 0:
                scored.append((score, detail.name))
        scored.sort(reverse=True)
        return [name for _, name in scored[: max(0, limit)]]

    # ── public write API ────────────────────────────────────────────────

    def create(self, name: str, description: str, content: str) -> SkillInfo:
        slug = self._validate_name(name)
        target_dir = self._skill_dir(slug)
        if target_dir.exists():
            raise SkillExistsError(slug)
        body = self._normalize_content(slug, description, content)
        target_dir.mkdir(parents=True, exist_ok=False)
        self._skill_file(slug).write_text(body, encoding="utf-8")
        return SkillInfo(name=slug, description=description.strip())

    def update(
        self,
        name: str,
        *,
        description: str | None = None,
        content: str | None = None,
        rename_to: str | None = None,
    ) -> SkillInfo:
        slug = self._validate_name(name)
        target_dir = self._skill_dir(slug)
        if not target_dir.exists():
            raise SkillNotFoundError(slug)

        if content is not None:
            text = content
        else:
            text = self._skill_file(slug).read_text(encoding="utf-8")

        if description is not None:
            text = self._rewrite_frontmatter(text, description=description.strip())

        meta, _ = self._parse_frontmatter(text)
        final_description = str(meta.get("description") or "").strip()

        if rename_to and rename_to != slug:
            new_slug = self._validate_name(rename_to)
            new_dir = self._skill_dir(new_slug)
            if new_dir.exists():
                raise SkillExistsError(new_slug)
            text = self._rewrite_frontmatter(text, name=new_slug)
            target_dir.rename(new_dir)
            slug = new_slug
            target_dir = new_dir

        self._skill_file(slug).write_text(text, encoding="utf-8")
        return SkillInfo(name=slug, description=final_description)

    def delete(self, name: str) -> None:
        slug = self._validate_name(name)
        target_dir = self._skill_dir(slug)
        if not target_dir.exists():
            raise SkillNotFoundError(slug)
        shutil.rmtree(target_dir)

    # ── content helpers ────────────────────────────────────────────────

    def _normalize_content(self, name: str, description: str, content: str) -> str:
        """Ensure the saved file has a valid frontmatter block with ``name``/``description``.

        If the user-provided ``content`` already has frontmatter we patch the
        ``name`` and ``description`` fields; otherwise we synthesise a header.
        """
        text = content if content is not None else ""
        if _FRONTMATTER_RE.match(text):
            text = self._rewrite_frontmatter(text, name=name, description=description.strip())
            return text
        header = yaml.safe_dump(
            {"name": name, "description": description.strip()},
            sort_keys=False,
            allow_unicode=True,
        ).strip()
        body = text.lstrip()
        return f"---\n{header}\n---\n\n{body}".rstrip() + "\n"

    def _rewrite_frontmatter(
        self,
        text: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> str:
        meta, body = self._parse_frontmatter(text)
        if name is not None:
            meta["name"] = name
        if description is not None:
            meta["description"] = description
        if not meta:
            return text
        header = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
        return f"---\n{header}\n---\n\n{body.lstrip()}".rstrip() + "\n"


_singleton: SkillService | None = None


def get_skill_service() -> SkillService:
    global _singleton
    if _singleton is None:
        _singleton = SkillService()
    return _singleton


__all__ = [
    "InvalidSkillNameError",
    "SkillDetail",
    "SkillExistsError",
    "SkillInfo",
    "SkillNotFoundError",
    "SkillService",
    "get_skill_service",
]
