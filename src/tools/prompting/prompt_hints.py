from __future__ import annotations

from pathlib import Path

import yaml

from src.core.tool_protocol import ToolAlias, ToolPromptHints


def load_prompt_hints(tool_name: str, language: str = "en") -> ToolPromptHints:
    """Load per-tool prompt hints from YAML with zh/en fallback."""
    normalized_language = language.lower()
    if normalized_language.startswith("zh"):
        normalized_language = "zh"
    elif normalized_language.startswith("en"):
        normalized_language = "en"

    base_dir = Path(__file__).parent / "hints"
    candidates = [base_dir / normalized_language / f"{tool_name}.yaml"]
    if normalized_language != "en":
        candidates.append(base_dir / "en" / f"{tool_name}.yaml")

    for path in candidates:
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        aliases = [
            ToolAlias(
                name=str(item.get("name", "")).strip(),
                description=str(item.get("description", "")).strip(),
                input_format=str(item.get("input_format", "")).strip(),
                when_to_use=str(item.get("when_to_use", "")).strip(),
                phase=str(item.get("phase", "")).strip(),
            )
            for item in data.get("aliases", [])
            if str(item.get("name", "")).strip()
        ]
        return ToolPromptHints(
            short_description=str(data.get("short_description", "")).strip(),
            when_to_use=str(data.get("when_to_use", "")).strip(),
            input_format=str(data.get("input_format", "")).strip(),
            guideline=str(data.get("guideline", "")).strip(),
            note=str(data.get("note", "")).strip(),
            phase=str(data.get("phase", "")).strip(),
            aliases=aliases,
        )

    return ToolPromptHints()
