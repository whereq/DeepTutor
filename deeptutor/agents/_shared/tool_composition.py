"""Per-turn tool composition policy shared by chat / quiz pipelines.

Owns the rule "given the user's composer toggles + the turn's context
flags, what tools should be enabled?". Lives outside any single pipeline
so chat and quiz can't disagree about which tools the user controls vs.
which the pipeline auto-mounts.

Two pieces:

* :data:`AUTO_MOUNTED_TOOLS` — tools whose mounting is owned by the
  pipeline (auto-on under specific conditions), not by user toggles.
  Membership here hides the tool from the user's composer / settings UI.
* :func:`compose_enabled_tools` — pure function that takes the user's
  toggled list + a :class:`ToolMountFlags` and returns the final, ordered
  enabled-tool list for one turn.

Callers resolve their own flags (chat checks selected KBs / source index
/ memory / notebooks; quiz reuses chat's policy verbatim).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, USER_TOGGLEABLE_TOOL_NAMES

# Tools whose mounting is owned by the pipeline (auto-on under specific
# context conditions), not by the user's composer toggles. Adding a tool
# here hides it from ``{tool_list}`` until its corresponding condition
# fires in :func:`compose_enabled_tools`.
AUTO_MOUNTED_TOOLS: frozenset[str] = frozenset(
    {
        "rag",
        "read_source",
        "read_memory",
        "write_memory",
        "list_notebook",
        "write_note",
        "ask_user",
        "web_fetch",
        "github",
    }
)


def default_optional_tools(excluded: Iterable[str] = ()) -> list[str]:
    """Return the user-toggleable tool list (chat's default set).

    Sourced from :mod:`deeptutor.tools.builtin` so the /settings/tools UI
    and the pipelines can never disagree about which tools the user
    actually controls.
    """
    excluded_set = frozenset(excluded)
    return [
        name
        for name in USER_TOGGLEABLE_TOOL_NAMES
        if name in BUILTIN_TOOL_NAMES
        and name not in excluded_set
        and name not in AUTO_MOUNTED_TOOLS
    ]


@dataclass(frozen=True)
class ToolMountFlags:
    """Per-turn flags that drive the auto-mount policy.

    Each capability resolves these from its own context (chat inspects
    ``UnifiedContext.knowledge_bases``, the source index, the memory
    service, the notebook manager; quiz reuses the same checks).
    """

    has_kb: bool = False
    has_sources: bool = False
    has_memory: bool = False
    has_notebooks: bool = False


def compose_enabled_tools(
    *,
    registry: Any,
    requested_tools: list[str] | None,
    optional_whitelist: list[str],
    mount_flags: ToolMountFlags,
) -> list[str]:
    """Compose the per-turn enabled-tool list.

    Order:

    1. User-toggled tools (filtered through the registry's ``get_enabled``
       so disabled tools never sneak in, and intersected with
       ``optional_whitelist`` so only legitimate composer toggles are
       respected).
    2. Conditional auto-mounts (``rag`` if a KB is attached, ``read_source``
       if a source index exists, ``read_memory`` if memory has content,
       ``list_notebook`` + ``write_note`` if notebooks exist).
    3. Always-on auto-mounts (``web_fetch``, ``github``, ``ask_user``).

    The result is ordered (no dedup is applied — caller's prerequisite is
    that ``optional_whitelist`` excludes ``AUTO_MOUNTED_TOOLS``, which
    :func:`default_optional_tools` guarantees).
    """
    composed: list[str] = [
        tool.name
        for tool in registry.get_enabled(requested_tools or [])
        if tool.name in optional_whitelist
    ]
    if mount_flags.has_kb:
        composed.append("rag")
    if mount_flags.has_sources:
        composed.append("read_source")
    if mount_flags.has_memory:
        composed.append("read_memory")
    if mount_flags.has_notebooks:
        composed.append("list_notebook")
        composed.append("write_note")
    composed.append("write_memory")
    composed.append("web_fetch")
    composed.append("github")
    composed.append("ask_user")
    return composed


def user_has_memory() -> bool:
    """Whether the active user has any L3 memory content.

    Drives the auto-mount of ``read_memory``. Per-user paths resolve via
    the multi-user ContextVars the runtime sets up. Fails closed (returns
    ``False``) on any error so a broken memory directory doesn't surface
    a tool with no payload to read.
    """
    try:
        from deeptutor.services.memory import get_memory_store

        store = get_memory_store()
        return any(
            store.read_raw("L3", slot).strip()
            for slot in ("recent", "profile", "scope", "preferences")
        )
    except Exception:
        return False


def user_has_notebooks() -> bool:
    """Whether the active user has at least one notebook.

    Auto-mount gate for ``list_notebook`` + ``write_note``. Same
    fail-closed posture as :func:`user_has_memory`.
    """
    try:
        from deeptutor.services.notebook import get_notebook_manager

        notebooks = get_notebook_manager().list_notebooks()
        return isinstance(notebooks, list) and any(
            nb for nb in notebooks if str(nb.get("id") or "").strip()
        )
    except Exception:
        return False


__all__ = [
    "AUTO_MOUNTED_TOOLS",
    "ToolMountFlags",
    "compose_enabled_tools",
    "default_optional_tools",
    "user_has_memory",
    "user_has_notebooks",
]
