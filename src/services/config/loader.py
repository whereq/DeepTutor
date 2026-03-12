#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration Loader
====================

Unified configuration loading for all DeepTutor modules.
Provides YAML configuration loading, path resolution, and language parsing.
"""

import asyncio
from pathlib import Path
import shutil
from typing import Any

import yaml

# PROJECT_ROOT points to the actual project root directory (DeepTutor/)
# Path(__file__) = src/services/config/loader.py
# .parent = src/services/config/
# .parent.parent = src/services/
# .parent.parent.parent = src/
# .parent.parent.parent.parent = DeepTutor/ (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def get_runtime_settings_dir(project_root: Path | None = None) -> Path:
    """Return the canonical runtime settings directory under ``data/user/settings``."""
    root = project_root or PROJECT_ROOT
    return root / "data" / "user" / "settings"


def _legacy_config_dir(project_root: Path | None = None) -> Path:
    root = project_root or PROJECT_ROOT
    return root / "config"


def _bootstrap_runtime_config_file(config_file: str, project_root: Path | None = None) -> Path:
    """
    Ensure a runtime YAML config exists under ``data/user/settings``.

    Runtime settings are the only supported live source. If the file is missing,
    bootstrap it once from the legacy ``config/`` directory for compatibility.
    """
    root = project_root or PROJECT_ROOT
    settings_dir = get_runtime_settings_dir(root)
    settings_dir.mkdir(parents=True, exist_ok=True)

    runtime_path = settings_dir / config_file
    if runtime_path.exists():
        return runtime_path

    legacy_path = _legacy_config_dir(root) / config_file
    if legacy_path.exists():
        shutil.copy2(legacy_path, runtime_path)
        return runtime_path

    raise FileNotFoundError(
        f"Configuration file not found: {config_file} "
        f"(runtime settings dir: {settings_dir})"
    )


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries, values in override will override values in base

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Direct override
            result[key] = value

    return result


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _normalize_runtime_paths(config: dict[str, Any], project_root: Path | None = None) -> dict[str, Any]:
    """Force all runtime path config values into the canonical ``data/user`` layout."""
    root = project_root or PROJECT_ROOT
    normalized = dict(config or {})
    paths = dict(normalized.get("paths", {}) or {})
    tools = dict(normalized.get("tools", {}) or {})
    run_code = dict(tools.get("run_code", {}) or {})

    user_root = root / "data" / "user"
    workspace_root = user_root / "workspace"
    chat_root = workspace_root / "chat"

    paths.update(
        {
            "user_data_dir": "./data/user",
            "knowledge_bases_dir": "./data/knowledge_bases",
            "user_log_dir": str(user_root / "logs"),
            "performance_log_dir": str(user_root / "logs" / "performance"),
            "guide_output_dir": str(workspace_root / "guide"),
            "question_output_dir": str(chat_root / "deep_question"),
            "research_output_dir": str(chat_root / "deep_research" / "cache"),
            "research_reports_dir": str(chat_root / "deep_research" / "reports"),
            "solve_output_dir": str(chat_root / "deep_solve"),
        }
    )

    run_code["workspace"] = str(chat_root / "_detached_code_execution")
    tools["run_code"] = run_code

    normalized["paths"] = paths
    normalized["tools"] = tools
    return normalized


async def _load_yaml_file_async(file_path: Path) -> dict[str, Any]:
    """Async version of _load_yaml_file."""
    return await asyncio.to_thread(_load_yaml_file, file_path)


def resolve_config_path(
    config_file: str,
    project_root: Path | None = None,
) -> tuple[Path, bool]:
    """
    Resolve *config_file* inside ``data/user/settings/``.

    Returns:
        ``(path, False)``

    Raises:
        FileNotFoundError: If the requested config does not exist.
    """
    if project_root is None:
        project_root = PROJECT_ROOT

    return _bootstrap_runtime_config_file(config_file, project_root), False


def load_config_with_main(config_file: str, project_root: Path | None = None) -> dict[str, Any]:
    """
    Load configuration file, automatically merge with main.yaml common configuration

    Args:
        config_file: Configuration file name (e.g., "main.yaml")
        project_root: Project root directory (if None, will try to auto-detect)

    Returns:
        Merged configuration dictionary
    """
    if project_root is None:
        project_root = PROJECT_ROOT

    # 1. Load main.yaml (common configuration)
    main_config = {}
    try:
        main_config_path = _bootstrap_runtime_config_file("main.yaml", project_root)
        main_config = _load_yaml_file(main_config_path)
    except Exception as e:
        print(f"⚠️ Failed to load runtime main.yaml: {e}")

    # 2. Load sub-module configuration file
    module_config = {}
    if config_file != "main.yaml":
        try:
            module_config_path, _ = resolve_config_path(config_file, project_root)
            if module_config_path.name != "main.yaml":
                module_config = _load_yaml_file(module_config_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{e}. Add the file under data/user/settings/.") from e
        except Exception as e:
            print(f"⚠️ Failed to load {config_file}: {e}")

    # 3. Merge configurations: main.yaml as base, sub-module config overrides
    merged_config = _deep_merge(main_config, module_config)

    return _normalize_runtime_paths(merged_config, project_root)


async def load_config_with_main_async(
    config_file: str, project_root: Path | None = None
) -> dict[str, Any]:
    """
    Async version of load_config_with_main for non-blocking file operations.

    Load configuration file, automatically merge with main.yaml common configuration

    Args:
        config_file: Configuration file name (e.g., "main.yaml")
        project_root: Project root directory (if None, will try to auto-detect)

    Returns:
        Merged configuration dictionary
    """
    if project_root is None:
        project_root = PROJECT_ROOT

    # 1. Load main.yaml (common configuration)
    main_config = {}
    try:
        main_config_path = _bootstrap_runtime_config_file("main.yaml", project_root)
        main_config = await _load_yaml_file_async(main_config_path)
    except Exception as e:
        print(f"⚠️ Failed to load runtime main.yaml: {e}")

    # 2. Load sub-module configuration file
    module_config = {}
    if config_file != "main.yaml":
        try:
            module_config_path, _ = resolve_config_path(config_file, project_root)
            if module_config_path.name != "main.yaml":
                module_config = await _load_yaml_file_async(module_config_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{e}. Add the file under data/user/settings/.") from e
        except Exception as e:
            print(f"⚠️ Failed to load {config_file}: {e}")

    # 3. Merge configurations: main.yaml as base, sub-module config overrides
    merged_config = _deep_merge(main_config, module_config)

    return _normalize_runtime_paths(merged_config, project_root)


def get_path_from_config(config: dict[str, Any], path_key: str, default: str = None) -> str:
    """
    Get path from configuration.

    Args:
        config: Configuration dictionary
        path_key: Path key name (e.g., "log_dir", "workspace")
        default: Default value

    Returns:
        Path string
    """
    # Priority: search in paths
    if "paths" in config and path_key in config["paths"]:
        return config["paths"][path_key]

    # Search in tools (e.g., run_code.workspace)
    if "tools" in config:
        if path_key == "workspace" and "run_code" in config["tools"]:
            return config["tools"]["run_code"].get("workspace", default)

    return default


def parse_language(language: Any) -> str:
    """
    Unified language configuration parser, supports multiple input formats

    Supported language representations:
    - English: "en", "english", "English"
    - Chinese: "zh", "chinese", "Chinese"

    Args:
        language: Language configuration value (can be "zh"/"en"/"Chinese"/"English" etc.)

    Returns:
        Standardized language code: 'zh' or 'en', defaults to 'zh'
    """
    if not language:
        return "zh"

    if isinstance(language, str):
        lang_lower = language.lower()
        if lang_lower in ["en", "english"]:
            return "en"
        if lang_lower in ["zh", "chinese", "cn"]:
            return "zh"

    return "zh"  # Default Chinese


def get_agent_params(module_name: str) -> dict:
    """
    Get agent parameters (temperature, max_tokens) for a specific module.

    This function loads parameters from config/agents.yaml which serves as the
    SINGLE source of truth for all agent temperature and max_tokens settings.

    Args:
        module_name: Module name, one of:
            - "guide": Guide module agents
            - "solve": Solve module agents
            - "research": Research module agents
            - "question": Question module agents
            - "brainstorm": Brainstorm tool settings
            - "co_writer": CoWriter module agents
            - "narrator": Narrator agent (independent, for TTS)

    Returns:
        dict: Dictionary containing:
            - temperature: float, default 0.5
            - max_tokens: int, default 4096

    Example:
        >>> params = get_agent_params("guide")
        >>> params["temperature"]  # 0.5
        >>> params["max_tokens"]   # 8192
    """
    # Default values
    defaults = {
        "temperature": 0.5,
        "max_tokens": 4096,
    }

    # Try to load from runtime agents.yaml
    try:
        config_path = _bootstrap_runtime_config_file("agents.yaml", PROJECT_ROOT)

        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                agents_config = yaml.safe_load(f) or {}

            if module_name in agents_config:
                module_config = agents_config[module_name]
                return {
                    "temperature": module_config.get("temperature", defaults["temperature"]),
                    "max_tokens": module_config.get("max_tokens", defaults["max_tokens"]),
                }
    except Exception as e:
        print(f"⚠️ Failed to load agents.yaml: {e}, using defaults")

    return defaults


__all__ = [
    "PROJECT_ROOT",
    "get_runtime_settings_dir",
    "load_config_with_main",
    "get_path_from_config",
    "parse_language",
    "get_agent_params",
    "_deep_merge",
]
