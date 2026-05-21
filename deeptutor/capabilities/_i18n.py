"""Shared i18n helper for capability status / UI strings.

Capability ``run()`` methods stream short status messages to the chat UI
(``stream.thinking``, ``stream.progress``, ``stream.error``). Those strings
must respect the user's locale. This module wires them into the existing
``PromptManager`` so each capability can keep its UI copy alongside its
LLM prompts under ``deeptutor/capabilities/prompts/{en,zh}/<name>.yaml``.

Conventions:

* YAML files contain a single top-level ``status:`` mapping, key → string.
* Strings may use ``{name}`` placeholders rendered via ``str.format``.
* Missing keys / files fall back to the ``default`` argument so a new
  hardcoded string still works while its translation is being added.
"""

from __future__ import annotations

from typing import Any

from deeptutor.services.prompt import get_prompt_manager


class StatusI18n:
    """Per-capability localized status-string lookup.

    Construct once at the top of ``run()`` with the capability name and
    ``context.language``, then call ``t(key, default, **kwargs)`` wherever
    a hardcoded English string was previously emitted.
    """

    __slots__ = ("_strings",)

    def __init__(self, capability_name: str, language: str) -> None:
        prompts = get_prompt_manager().load_prompts(
            module_name="capabilities",
            agent_name=capability_name,
            language=language,
        )
        raw = prompts.get("status") if isinstance(prompts, dict) else None
        self._strings: dict[str, Any] = raw if isinstance(raw, dict) else {}

    def t(self, key: str, default: str = "", /, **kwargs: Any) -> str:
        value = self._strings.get(key)
        text = value if isinstance(value, str) and value else default
        if kwargs and text:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return text
        return text


__all__ = ["StatusI18n"]
