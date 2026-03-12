"""Validated request config and intent-to-policy mapping for deep research."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


ResearchMode = Literal["notes", "report", "comparison", "learning_path"]
ResearchDepth = Literal["quick", "standard", "deep"]
ResearchSource = Literal["kb", "web", "papers"]


class DeepResearchRequestConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: ResearchMode
    depth: ResearchDepth
    sources: list[ResearchSource]

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, value: list[ResearchSource]) -> list[ResearchSource]:
        deduped = list(dict.fromkeys(value))
        return deduped


def validate_research_request_config(raw_config: dict[str, Any] | None) -> DeepResearchRequestConfig:
    if not isinstance(raw_config, dict):
        raise ValueError("Deep research requires an explicit config object.")
    try:
        return DeepResearchRequestConfig.model_validate(raw_config)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise ValueError(f"Invalid deep research config: {details}") from exc


def build_research_execution_policy(
    *,
    request_config: DeepResearchRequestConfig,
    enabled_tools: set[str],
) -> dict[str, Any]:
    depth_policy = _build_depth_policy(request_config.depth)
    mode_policy = _build_mode_policy(request_config.mode, request_config.depth)

    source_tools: set[str] = set()
    if "kb" in request_config.sources:
        source_tools.add("rag")
    if "web" in request_config.sources:
        source_tools.add("web_search")
    if "papers" in request_config.sources:
        source_tools.add("paper_search")

    allow_code_execution = (
        bool(request_config.sources)
        and "code_execution" in enabled_tools
        and request_config.mode == "comparison"
        and request_config.depth == "deep"
    )
    effective_tools = sorted(source_tools | ({"code_execution"} if allow_code_execution else set()))

    planning = {
        "rephrase": {
            "enabled": mode_policy["rephrase_enabled"],
            "max_iterations": mode_policy["rephrase_iterations"],
        },
        "decompose": {
            "mode": mode_policy["decompose_mode"],
            "initial_subtopics": mode_policy["initial_subtopics"],
            "auto_max_subtopics": mode_policy["auto_max_subtopics"],
        },
    }
    researching = {
        "max_iterations": depth_policy["max_iterations"],
        "iteration_mode": depth_policy["iteration_mode"],
        "execution_mode": depth_policy["execution_mode"],
        "max_parallel_topics": depth_policy["max_parallel_topics"],
        "new_topic_min_score": depth_policy["new_topic_min_score"],
        "enable_rag_hybrid": "rag" in source_tools,
        "enable_rag_naive": "rag" in source_tools,
        "enable_web_search": "web_search" in source_tools,
        "enable_paper_search": "paper_search" in source_tools,
        "enable_run_code": allow_code_execution,
        "enabled_tools": effective_tools,
    }
    reporting = {
        "min_section_length": mode_policy["min_section_length"],
        "report_single_pass_threshold": mode_policy["report_single_pass_threshold"],
        "enable_citation_list": mode_policy["enable_citation_list"],
        "enable_inline_citations": mode_policy["enable_inline_citations"],
        "deduplicate_enabled": mode_policy["deduplicate_enabled"],
        "style": mode_policy["style"],
        "mode": request_config.mode,
        "depth": request_config.depth,
    }
    queue = {"max_length": depth_policy["queue_max_length"]}

    return {
        "planning": planning,
        "researching": researching,
        "reporting": reporting,
        "queue": queue,
        "intent": request_config.model_dump(),
    }


def build_research_runtime_config(
    *,
    base_config: dict[str, Any],
    request_config: DeepResearchRequestConfig,
    enabled_tools: set[str],
    kb_name: str | None,
) -> dict[str, Any]:
    research_root = base_config.get("research", {}) if isinstance(base_config.get("research"), dict) else {}
    researching_root = (
        research_root.get("researching", {})
        if isinstance(research_root.get("researching"), dict)
        else {}
    )
    reporting_root = (
        research_root.get("reporting", {})
        if isinstance(research_root.get("reporting"), dict)
        else {}
    )
    rag_root = research_root.get("rag", {}) if isinstance(research_root.get("rag"), dict) else {}
    policy = build_research_execution_policy(
        request_config=request_config,
        enabled_tools=enabled_tools,
    )

    runtime_config = dict(base_config)
    runtime_config["planning"] = policy["planning"]
    runtime_config["researching"] = {
        **{
            key: researching_root[key]
            for key in ("note_agent_mode", "tool_timeout", "tool_max_retries", "paper_search_years_limit")
            if key in researching_root
        },
        **policy["researching"],
    }
    runtime_config["reporting"] = {
        **{
            key: reporting_root[key]
            for key in ()
            if key in reporting_root
        },
        **policy["reporting"],
    }
    runtime_config["queue"] = policy["queue"]
    runtime_config["rag"] = {
        **rag_root,
        "kb_name": kb_name or rag_root.get("kb_name"),
    }
    runtime_config["intent"] = policy["intent"]

    system_cfg = dict(runtime_config.get("system", {}) or {})
    paths_cfg = dict(runtime_config.get("paths", {}) or {})
    system_cfg["output_base_dir"] = paths_cfg.get(
        "research_output_dir",
        "./data/user/workspace/chat/deep_research",
    )
    system_cfg["reports_dir"] = paths_cfg.get(
        "research_reports_dir",
        "./data/user/workspace/chat/deep_research/reports",
    )
    runtime_config["system"] = system_cfg

    tools_cfg = dict(runtime_config.get("tools", {}) or {})
    web_cfg = dict(tools_cfg.get("web_search", {}) or {})
    web_cfg["enabled"] = bool(runtime_config["researching"].get("enable_web_search"))
    tools_cfg["web_search"] = web_cfg
    runtime_config["tools"] = tools_cfg

    return runtime_config


def _build_depth_policy(depth: ResearchDepth) -> dict[str, Any]:
    policies: dict[ResearchDepth, dict[str, Any]] = {
        "quick": {
            "max_iterations": 1,
            "iteration_mode": "fixed",
            "execution_mode": "series",
            "max_parallel_topics": 1,
            "new_topic_min_score": 0.95,
            "queue_max_length": 2,
        },
        "standard": {
            "max_iterations": 3,
            "iteration_mode": "fixed",
            "execution_mode": "series",
            "max_parallel_topics": 1,
            "new_topic_min_score": 0.88,
            "queue_max_length": 5,
        },
        "deep": {
            "max_iterations": 5,
            "iteration_mode": "flexible",
            "execution_mode": "parallel",
            "max_parallel_topics": 3,
            "new_topic_min_score": 0.78,
            "queue_max_length": 8,
        },
    }
    return dict(policies[depth])


def _build_mode_policy(mode: ResearchMode, depth: ResearchDepth) -> dict[str, Any]:
    manual_subtopics_by_depth: dict[ResearchDepth, int] = {
        "quick": 2,
        "standard": 3,
        "deep": 4,
    }
    auto_subtopics_by_depth: dict[ResearchDepth, int] = {
        "quick": 2,
        "standard": 4,
        "deep": 6,
    }
    policies: dict[ResearchMode, dict[str, Any]] = {
        "notes": {
            "rephrase_enabled": False,
            "rephrase_iterations": 1,
            "decompose_mode": "manual",
            "initial_subtopics": manual_subtopics_by_depth[depth],
            "auto_max_subtopics": None,
            "min_section_length": 260,
            "report_single_pass_threshold": 99,
            "enable_citation_list": True,
            "enable_inline_citations": False,
            "deduplicate_enabled": False,
            "style": "study_notes",
        },
        "report": {
            "rephrase_enabled": False,
            "rephrase_iterations": 1,
            "decompose_mode": "auto",
            "initial_subtopics": None,
            "auto_max_subtopics": auto_subtopics_by_depth[depth],
            "min_section_length": 650,
            "report_single_pass_threshold": 2,
            "enable_citation_list": True,
            "enable_inline_citations": False,
            "deduplicate_enabled": False,
            "style": "report",
        },
        "comparison": {
            "rephrase_enabled": True,
            "rephrase_iterations": 1 if depth != "deep" else 2,
            "decompose_mode": "manual",
            "initial_subtopics": max(2, manual_subtopics_by_depth[depth]),
            "auto_max_subtopics": None,
            "min_section_length": 520,
            "report_single_pass_threshold": 2,
            "enable_citation_list": True,
            "enable_inline_citations": False,
            "deduplicate_enabled": False,
            "style": "comparison",
        },
        "learning_path": {
            "rephrase_enabled": True,
            "rephrase_iterations": 1,
            "decompose_mode": "auto",
            "initial_subtopics": None,
            "auto_max_subtopics": auto_subtopics_by_depth[depth],
            "min_section_length": 420,
            "report_single_pass_threshold": 99,
            "enable_citation_list": True,
            "enable_inline_citations": False,
            "deduplicate_enabled": False,
            "style": "learning_path",
        },
    }
    return dict(policies[mode])


__all__ = [
    "DeepResearchRequestConfig",
    "build_research_execution_policy",
    "build_research_runtime_config",
    "validate_research_request_config",
]
