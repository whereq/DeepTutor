from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any

from .env_store import EnvStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_BACKEND_PORT = 8001
DEFAULT_FRONTEND_PORT = 3782
DEFAULT_LANGUAGE = "en"


@dataclass(frozen=True, slots=True)
class LaunchSettings:
    backend_port: int
    frontend_port: int
    language: str
    source: str
    settings_dir: Path
    env_json_path: Path
    interface_json_path: Path
    env_path: Path


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _coerce_port(value: Any) -> int | None:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    if 1 <= port <= 65535:
        return port
    return None


def _normalize_language(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    language = value.strip().lower()
    if language in {"en", "english"} or language.startswith("en_"):
        return "en"
    if language in {"zh", "cn", "chinese"} or language.startswith("zh_"):
        return "zh"
    return None


def load_launch_settings(project_root: Path | None = None) -> LaunchSettings:
    """Load ports and UI language for launcher-style entry points.

    Runtime settings under ``data/user/settings`` are preferred because they
    reflect the web Settings flow.  When that directory or the relevant files
    are absent/empty/invalid, the project ``.env`` remains the compatibility
    fallback used by older installs and manual setups.
    """

    root = project_root or PROJECT_ROOT
    settings_dir = root / "data" / "user" / "settings"
    env_json_path = settings_dir / "env.json"
    interface_json_path = settings_dir / "interface.json"
    env_path = root / ".env"

    settings_env = _load_json_object(env_json_path)
    interface_settings = _load_json_object(interface_json_path)
    env_store = EnvStore(env_path)
    env_values = env_store.load()

    settings_ports = settings_env.get("ports") if isinstance(settings_env.get("ports"), dict) else {}
    settings_backend_port = _coerce_port(settings_ports.get("backend"))
    settings_frontend_port = _coerce_port(settings_ports.get("frontend"))
    interface_language = _normalize_language(interface_settings.get("language"))
    backend_port = (
        settings_backend_port
        or _coerce_port(env_values.get("BACKEND_PORT"))
        or _coerce_port(os.getenv("BACKEND_PORT"))
        or DEFAULT_BACKEND_PORT
    )
    frontend_port = (
        settings_frontend_port
        or _coerce_port(env_values.get("FRONTEND_PORT"))
        or _coerce_port(os.getenv("FRONTEND_PORT"))
        or DEFAULT_FRONTEND_PORT
    )
    language = (
        interface_language
        or _normalize_language(env_values.get("UI_LANGUAGE"))
        or _normalize_language(env_values.get("LANGUAGE"))
        or _normalize_language(os.getenv("UI_LANGUAGE"))
        or _normalize_language(os.getenv("LANGUAGE"))
        or DEFAULT_LANGUAGE
    )

    sources: list[str] = []
    if settings_backend_port is not None or settings_frontend_port is not None:
        sources.append("data/user/settings/env.json")
    if interface_language is not None:
        sources.append("data/user/settings/interface.json")
    if not sources:
        sources.append(".env")

    return LaunchSettings(
        backend_port=backend_port,
        frontend_port=frontend_port,
        language=language,
        source=" + ".join(sources),
        settings_dir=settings_dir,
        env_json_path=env_json_path,
        interface_json_path=interface_json_path,
        env_path=env_path,
    )


__all__ = [
    "DEFAULT_BACKEND_PORT",
    "DEFAULT_FRONTEND_PORT",
    "DEFAULT_LANGUAGE",
    "LaunchSettings",
    "load_launch_settings",
]
