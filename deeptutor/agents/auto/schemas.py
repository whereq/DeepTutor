"""Construct OpenAI tool schemas for the Auto router LLM.

The router LLM sees two kinds of tools:

* ``delegate_to_<capability>`` — one per enabled capability. Parameters wrap
  the capability's own ``request_schema`` under a ``config`` field plus a
  free-form ``rationale`` string.
* Atomic tools (``rag``, ``web_search``, ``code_execution``, ``reason``,
  ``brainstorm``, ``paper_search``) — exposed verbatim from
  ``ToolRegistry.build_openai_schemas`` with the same RAG ``kb_name`` stripping
  that the chat pipeline already applies.

Auto never offers itself, ``chat``, or ``geogebra_analysis`` to the router.
"""

from __future__ import annotations

from typing import Any

from deeptutor.runtime.registry.capability_registry import CapabilityRegistry
from deeptutor.runtime.registry.tool_registry import ToolRegistry

# Auto must not recurse into itself; chat is a generic tool-using capability
# whose value-add (autonomous tool selection) is already what the router does,
# so excluding it avoids redundant LLM hops.
EXCLUDED_CAPABILITIES = {"auto", "chat"}

# Mirrors AgenticChatPipeline.CHAT_EXCLUDED_TOOLS — geogebra_analysis is a
# vision-pipeline tool that needs a specific UI surface.
EXCLUDED_ATOMIC_TOOLS = {"geogebra_analysis"}

_DELEGATE_PREFIX = "delegate_to_"


def _capability_tool_name(cap_name: str) -> str:
    return f"{_DELEGATE_PREFIX}{cap_name}"


def _ensure_object_schema(schema: dict[str, Any] | None) -> dict[str, Any]:
    """Coerce a possibly-empty pydantic schema into a valid JSON Schema object."""
    if not isinstance(schema, dict):
        return {"type": "object", "properties": {}}
    cleaned = dict(schema)
    cleaned.setdefault("type", "object")
    cleaned.setdefault("properties", {})
    cleaned.pop("title", None)
    return cleaned


def _wrap_capability_params(request_schema: dict[str, Any]) -> dict[str, Any]:
    """Wrap a capability's request_schema as the parameters of delegate_to_*."""
    return {
        "type": "object",
        "properties": {
            "config": _ensure_object_schema(request_schema),
            "rationale": {
                "type": "string",
                "description": (
                    "One short sentence explaining why this capability is the best "
                    "fit for the user's request."
                ),
            },
        },
        "required": ["config"],
        "additionalProperties": False,
    }


def build_capability_tool_schemas(
    registry: CapabilityRegistry,
    enabled_capabilities: list[str] | None,
) -> list[dict[str, Any]]:
    """Build ``delegate_to_<cap>`` function schemas for enabled capabilities.

    Empty/None ``enabled_capabilities`` means "all registered capabilities".
    """
    candidate_names = enabled_capabilities or registry.list_capabilities()
    schemas: list[dict[str, Any]] = []
    for cap_name in candidate_names:
        if cap_name in EXCLUDED_CAPABILITIES:
            continue
        capability = registry.get(cap_name)
        if capability is None:
            continue
        manifest = capability.manifest
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": _capability_tool_name(cap_name),
                    "description": manifest.description,
                    "parameters": _wrap_capability_params(manifest.request_schema),
                },
            }
        )
    return schemas


def build_atomic_tool_schemas(
    tool_registry: ToolRegistry,
    enabled_tools: list[str] | None,
) -> list[dict[str, Any]]:
    """Expose atomic tools to the router LLM.

    ``enabled_tools`` is a hint from the user's manual-mode selection. If
    provided, only those tools are exposed; otherwise all builtin tools
    (minus ``EXCLUDED_ATOMIC_TOOLS``) are. The RAG schema has ``kb_name``
    stripped because that's a server-side / trusted UI value, not an LLM arg.
    """
    candidate_names: list[str] = list(enabled_tools) if enabled_tools else [
        name for name in tool_registry.list_tools() if name not in EXCLUDED_ATOMIC_TOOLS
    ]
    candidate_names = [n for n in candidate_names if n not in EXCLUDED_ATOMIC_TOOLS]
    schemas = tool_registry.build_openai_schemas(candidate_names)
    for schema in schemas:
        function = schema.get("function") if isinstance(schema, dict) else None
        if not isinstance(function, dict) or function.get("name") != "rag":
            continue
        params = function.get("parameters")
        if not isinstance(params, dict):
            continue
        properties = params.get("properties")
        if isinstance(properties, dict):
            properties.pop("kb_name", None)
        required = params.get("required")
        if isinstance(required, list):
            params["required"] = [name for name in required if name != "kb_name"]
        params["additionalProperties"] = False
    return schemas


def build_all_tool_schemas(
    capability_registry: CapabilityRegistry,
    tool_registry: ToolRegistry,
    enabled_capabilities: list[str] | None,
    enabled_tools_hint: list[str] | None,
) -> list[dict[str, Any]]:
    """Build the full list of tools the router LLM sees in one call."""
    return [
        *build_capability_tool_schemas(capability_registry, enabled_capabilities),
        *build_atomic_tool_schemas(tool_registry, enabled_tools_hint),
    ]


def extract_capability_name(tool_name: str) -> str | None:
    """Reverse of ``_capability_tool_name``; returns None if not a delegate tool."""
    if tool_name.startswith(_DELEGATE_PREFIX):
        return tool_name[len(_DELEGATE_PREFIX):] or None
    return None


def is_delegate_tool(tool_name: str) -> bool:
    return tool_name.startswith(_DELEGATE_PREFIX)
