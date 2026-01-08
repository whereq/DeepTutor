#!/usr/bin/env python
"""
Unified Configuration Management
Combines environment variable configuration and YAML configuration loading.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import yaml
from settings import settings

# PROJECT_ROOT points to the actual project root directory (DeepTutor/)
# Path(__file__) = src/core/core.py
# .parent = src/core/
# .parent.parent = src/
# .parent.parent.parent = DeepTutor/ (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load .env from project root directory
# DeepTutor.env takes precedence, then fallback to .env
load_dotenv(PROJECT_ROOT / "DeepTutor.env", override=False)
load_dotenv(PROJECT_ROOT / ".env", override=False)


# ============================================================================
# Environment Variable Configuration (from config.py)
# ============================================================================


def _to_int(value: str | None, default: int) -> int:
    """Convert environment variable to int, fallback to default value on failure."""
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _strip_value(value: str | None) -> str | None:
    """Remove leading/trailing whitespace and quotes from string."""
    if value is None:
        return None
    return value.strip().strip("\"'")


def get_llm_config() -> dict:
    """
    Return complete configuration for LLM.
    Uses centralized settings singleton.
    """
    # 1. Try to get active provider from new system
    try:
        from src.core.llm_provider import provider_manager
        active_provider = provider_manager.get_active_provider()
        if active_provider:
            return {
                "binding": active_provider.binding,
                "model": active_provider.model,
                "api_key": active_provider.api_key,
                "base_url": active_provider.base_url,
            }
    except Exception as e:
        print(f"⚠️ Failed to load active provider: {e}")

    # 2. Fallback to centralized settings
    llm = settings.llm
    return {
        "binding": llm.binding,
        "model": llm.model,
        "api_key": llm.api_key,
        "base_url": llm.host,
        "disable_ssl_verify": llm.disable_ssl_verify
    }


def get_tts_config() -> dict:
    """
    Return complete configuration for TTS (Text-to-Speech).
    """
    tts = settings.tts
    return {
        "model": tts.model,
        "api_key": tts.api_key,
        "base_url": tts.url,
        "voice": os.getenv("TTS_VOICE", "alloy"), # Still allowing voice from env if not in settings
    }


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
            - "ideagen": IdeaGen module agents
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

    # Try to load from agents.yaml
    try:
        # PROJECT_ROOT is the project root directory, so config is at PROJECT_ROOT/config/
        config_path = PROJECT_ROOT / "config" / "agents.yaml"

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


def get_embedding_config() -> dict:
    """
    Return complete configuration for embedding models.
    """
    emb = settings.embedding
    return {
        "binding": emb.binding,
        "model": emb.model,
        "api_key": emb.api_key,
        "base_url": emb.host,
        "dim": emb.dimension,
        "max_tokens": 8192, # Default
    }


# ============================================================================
# YAML Configuration Loading (from config_loader.py)
# ============================================================================


def load_config_with_main(config_file: str, project_root: Path | None = None) -> dict[str, Any]:
    """
    Load configuration file, automatically merge with main.yaml common configuration

    Args:
        config_file: Sub-module configuration file name (e.g., "solve_config.yaml")
        project_root: Project root directory (if None, will try to auto-detect)

    Returns:
        Merged configuration dictionary
    """
    if project_root is None:
        # Try to infer project root from current file location
        # From src/core/core.py -> project root
        project_root = Path(__file__).parent.parent.parent

    config_dir = project_root / "config"

    # 1. Load main.yaml (common configuration)
    main_config = {}
    main_config_path = config_dir / "main.yaml"
    if main_config_path.exists():
        try:
            with open(main_config_path, encoding="utf-8") as f:
                main_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Failed to load main.yaml: {e}")

    # 2. Load sub-module configuration file
    module_config = {}
    module_config_path = config_dir / config_file
    if module_config_path.exists():
        try:
            with open(module_config_path, encoding="utf-8") as f:
                module_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Failed to load {config_file}: {e}")

    # 3. Merge configurations: main.yaml as base, sub-module config overrides
    merged_config = _deep_merge(main_config, module_config)

    return merged_config


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


def get_path_from_config(config: dict[str, Any], path_key: str, default: str = None) -> str:
    """
    Get path from configuration, supports searching in paths and system

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

    # Search in system (backward compatibility)
    if "system" in config and path_key in config["system"]:
        return config["system"][path_key]

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
        if lang_lower in ["zh", "chinese"]:
            return "zh"

    return "zh"  # Default Chinese


__all__ = [
    # Environment variable configuration
    "get_llm_config",
    "get_embedding_config",
    "get_tts_config",
    # Agent parameters
    "get_agent_params",
    # YAML configuration loading
    "load_config_with_main",
    "get_path_from_config",
    "_deep_merge",
    # Language parsing
    "parse_language",
]
