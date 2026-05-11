from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable

from deeptutor.services.path_service import get_path_service

DEFAULT_SYSTEM_SETTINGS: dict[str, Any] = {
    "version": 1,
    "backend_port": 8001,
    "frontend_port": 3782,
    "next_public_api_base_external": "",
    "next_public_api_base": "",
    "cors_origin": "",
    "cors_origins": [],
    "disable_ssl_verify": False,
    "chat_attachment_dir": "",
}

DEFAULT_AUTH_SETTINGS: dict[str, Any] = {
    "version": 1,
    "enabled": False,
    "username": "admin",
    "password_hash": "",
    "token_expire_hours": 24,
    "cookie_secure": False,
}

DEFAULT_INTEGRATIONS_SETTINGS: dict[str, Any] = {
    "version": 1,
    "pocketbase_url": "",
    "pocketbase_port": 8090,
    "pocketbase_external_url": "",
    "pocketbase_admin_email": "",
    "pocketbase_admin_password": "",
}

IGNORE_PROCESS_OVERRIDES_ENV = "DEEPTUTOR_IGNORE_PROCESS_ENV_OVERRIDES"
TRUTHY = {"1", "true", "yes", "on"}
FALSY = {"0", "false", "no", "off"}


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in TRUTHY:
        return True
    if text in FALSY:
        return False
    return default


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _coerce_port(value: Any, default: int) -> int:
    port = _coerce_int(value, default)
    return port if 1 <= port <= 65535 else default


def _coerce_origins(value: Any) -> list[str]:
    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = str(value or "").replace("\n", ",").split(",")
    origins: list[str] = []
    seen: set[str] = set()
    for raw in raw_items:
        origin = str(raw).strip().rstrip("/")
        if origin and origin not in seen:
            origins.append(origin)
            seen.add(origin)
    return origins


def _deepcopy_default(defaults: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(defaults)


def _json_object(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        delete=False,
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        tmp_path = Path(handle.name)
    tmp_path.replace(path)


def _string(value: Any) -> str:
    return "" if value is None else str(value).strip()


class RuntimeSettingsService:
    """JSON-backed runtime settings rooted in data/user/settings.

    Process environment values are explicit deployment overrides and are applied
    centrally here rather than scattered through the application. Project-root
    ``.env`` files are intentionally ignored.
    """

    _instances: dict[str, "RuntimeSettingsService"] = {}

    def __init__(
        self,
        settings_dir: Path,
        *,
        process_env: dict[str, str] | None = None,
    ) -> None:
        self.settings_dir = settings_dir
        self.process_env = process_env if process_env is not None else os.environ
        self._external_process_keys: set[str] = set()
        self._internal_exported_values: dict[str, str] = {}

    @classmethod
    def get_instance(
        cls,
        settings_dir: Path | None = None,
        *,
        process_env: dict[str, str] | None = None,
    ) -> "RuntimeSettingsService":
        resolved = (settings_dir or _global_settings_dir()).resolve()
        key = str(resolved)
        if process_env is not None:
            return cls(resolved, process_env=process_env)
        if key not in cls._instances:
            cls._instances[key] = cls(resolved)
        return cls._instances[key]

    def path_for(self, name: str) -> Path:
        if not name.endswith(".json"):
            name = f"{name}.json"
        return self.settings_dir / name

    def load_system(self, *, include_process_overrides: bool = True) -> dict[str, Any]:
        payload = self._load_or_create(
            "system",
            DEFAULT_SYSTEM_SETTINGS,
            self._normalize_system,
        )
        if include_process_overrides:
            payload = self._apply_system_process_overrides(payload)
        return payload

    def save_system(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_system({**DEFAULT_SYSTEM_SETTINGS, **settings})
        _atomic_write_json(self.path_for("system"), payload)
        return payload

    def load_auth(self, *, include_process_overrides: bool = True) -> dict[str, Any]:
        payload = self._load_or_create(
            "auth",
            DEFAULT_AUTH_SETTINGS,
            self._normalize_auth,
        )
        if include_process_overrides:
            payload = self._apply_auth_process_overrides(payload)
        return payload

    def save_auth(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_auth({**DEFAULT_AUTH_SETTINGS, **settings})
        _atomic_write_json(self.path_for("auth"), payload)
        return payload

    def load_integrations(self, *, include_process_overrides: bool = True) -> dict[str, Any]:
        payload = self._load_or_create(
            "integrations",
            DEFAULT_INTEGRATIONS_SETTINGS,
            self._normalize_integrations,
        )
        if include_process_overrides:
            payload = self._apply_integrations_process_overrides(payload)
        return payload

    def save_integrations(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_integrations({**DEFAULT_INTEGRATIONS_SETTINGS, **settings})
        _atomic_write_json(self.path_for("integrations"), payload)
        return payload

    def ensure_defaults(self) -> None:
        self.load_system(include_process_overrides=False)
        self.load_auth(include_process_overrides=False)
        self.load_integrations(include_process_overrides=False)

    def render_environment(self) -> dict[str, str]:
        """Render non-model settings into process env names for subprocesses."""
        system = self.load_system()
        auth = self.load_auth()
        integrations = self.load_integrations()
        return {
            "BACKEND_PORT": str(system["backend_port"]),
            "FRONTEND_PORT": str(system["frontend_port"]),
            "NEXT_PUBLIC_API_BASE_EXTERNAL": system["next_public_api_base_external"],
            "NEXT_PUBLIC_API_BASE": system["next_public_api_base"],
            "CORS_ORIGIN": system["cors_origin"],
            "CORS_ORIGINS": ",".join(system["cors_origins"]),
            "DISABLE_SSL_VERIFY": _bool_env(system["disable_ssl_verify"]),
            "CHAT_ATTACHMENT_DIR": system["chat_attachment_dir"],
            "AUTH_ENABLED": _bool_env(auth["enabled"]),
            "AUTH_USERNAME": auth["username"],
            "AUTH_PASSWORD_HASH": auth["password_hash"],
            "AUTH_TOKEN_EXPIRE_HOURS": str(auth["token_expire_hours"]),
            "AUTH_COOKIE_SECURE": _bool_env(auth["cookie_secure"]),
            "NEXT_PUBLIC_AUTH_ENABLED": _bool_env(auth["enabled"]),
            "POCKETBASE_URL": integrations["pocketbase_url"],
            "POCKETBASE_PORT": str(integrations["pocketbase_port"]),
            "POCKETBASE_EXTERNAL_URL": integrations["pocketbase_external_url"],
            "POCKETBASE_ADMIN_EMAIL": integrations["pocketbase_admin_email"],
            "POCKETBASE_ADMIN_PASSWORD": integrations["pocketbase_admin_password"],
        }

    def export_environment(self, *, overwrite: bool = True) -> dict[str, str]:
        env = self.render_environment()
        for key, value in env.items():
            current = os.environ.get(key)
            if current and self._internal_exported_values.get(key) != current:
                self._external_process_keys.add(key)
            if overwrite or key not in os.environ:
                os.environ[key] = value
                if key not in self._external_process_keys:
                    self._internal_exported_values[key] = value
        return env

    def _process_env_value(self, key: str) -> str:
        if self._ignore_process_overrides():
            return ""
        value = self.process_env.get(key, "")
        if not value:
            return ""
        if key in self._external_process_keys:
            return value
        internal_value = self._internal_exported_values.get(key)
        if internal_value is not None and value == internal_value:
            return ""
        return value

    def _load_or_create(
        self,
        name: str,
        defaults: dict[str, Any],
        normalizer: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        path = self.path_for(name)
        loaded = _json_object(path)
        if loaded:
            normalized = normalizer({**defaults, **loaded})
            if normalized != loaded:
                _atomic_write_json(path, normalized)
            return normalized

        normalized = normalizer(_deepcopy_default(defaults))
        _atomic_write_json(path, normalized)
        return normalized

    def _ignore_process_overrides(self) -> bool:
        return _coerce_bool(self.process_env.get(IGNORE_PROCESS_OVERRIDES_ENV), False)

    def _apply_system_process_overrides(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = dict(settings)
        if value := self._process_env_value("BACKEND_PORT"):
            payload["backend_port"] = value
        if value := self._process_env_value("FRONTEND_PORT"):
            payload["frontend_port"] = value
        if value := self._process_env_value("NEXT_PUBLIC_API_BASE_EXTERNAL"):
            payload["next_public_api_base_external"] = value
        if value := self._process_env_value("NEXT_PUBLIC_API_BASE"):
            payload["next_public_api_base"] = value
        if value := self._process_env_value("CORS_ORIGIN"):
            payload["cors_origin"] = value
        if value := self._process_env_value("CORS_ORIGINS"):
            payload["cors_origins"] = value
        if value := self._process_env_value("DISABLE_SSL_VERIFY"):
            payload["disable_ssl_verify"] = value
        if value := self._process_env_value("CHAT_ATTACHMENT_DIR"):
            payload["chat_attachment_dir"] = value
        return self._normalize_system(payload)

    def _apply_auth_process_overrides(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = dict(settings)
        if value := (
            self._process_env_value("AUTH_ENABLED")
            or self._process_env_value("NEXT_PUBLIC_AUTH_ENABLED")
        ):
            payload["enabled"] = value
        if value := self._process_env_value("AUTH_USERNAME"):
            payload["username"] = value
        if value := self._process_env_value("AUTH_PASSWORD_HASH"):
            payload["password_hash"] = value
        if value := self._process_env_value("AUTH_TOKEN_EXPIRE_HOURS"):
            payload["token_expire_hours"] = value
        if value := self._process_env_value("AUTH_COOKIE_SECURE"):
            payload["cookie_secure"] = value
        return self._normalize_auth(payload)

    def _apply_integrations_process_overrides(self, settings: dict[str, Any]) -> dict[str, Any]:
        payload = dict(settings)
        if value := self._process_env_value("POCKETBASE_URL"):
            payload["pocketbase_url"] = value
        if value := self._process_env_value("POCKETBASE_PORT"):
            payload["pocketbase_port"] = value
        if value := self._process_env_value("POCKETBASE_EXTERNAL_URL"):
            payload["pocketbase_external_url"] = value
        if value := self._process_env_value("POCKETBASE_ADMIN_EMAIL"):
            payload["pocketbase_admin_email"] = value
        if value := self._process_env_value("POCKETBASE_ADMIN_PASSWORD"):
            payload["pocketbase_admin_password"] = value
        return self._normalize_integrations(payload)

    def _normalize_system(self, settings: dict[str, Any]) -> dict[str, Any]:
        return {
            "version": 1,
            "backend_port": _coerce_port(settings.get("backend_port"), 8001),
            "frontend_port": _coerce_port(settings.get("frontend_port"), 3782),
            "next_public_api_base_external": _string(settings.get("next_public_api_base_external")),
            "next_public_api_base": _string(settings.get("next_public_api_base")),
            "cors_origin": _string(settings.get("cors_origin")),
            "cors_origins": _coerce_origins(settings.get("cors_origins")),
            "disable_ssl_verify": _coerce_bool(settings.get("disable_ssl_verify"), False),
            "chat_attachment_dir": _string(settings.get("chat_attachment_dir")),
        }

    def _normalize_auth(self, settings: dict[str, Any]) -> dict[str, Any]:
        return {
            "version": 1,
            "enabled": _coerce_bool(settings.get("enabled"), False),
            "username": _string(settings.get("username")) or "admin",
            "password_hash": _string(settings.get("password_hash")),
            "token_expire_hours": max(1, _coerce_int(settings.get("token_expire_hours"), 24)),
            "cookie_secure": _coerce_bool(settings.get("cookie_secure"), False),
        }

    def _normalize_integrations(self, settings: dict[str, Any]) -> dict[str, Any]:
        return {
            "version": 1,
            "pocketbase_url": _string(settings.get("pocketbase_url")).rstrip("/"),
            "pocketbase_port": _coerce_port(settings.get("pocketbase_port"), 8090),
            "pocketbase_external_url": _string(settings.get("pocketbase_external_url")).rstrip("/"),
            "pocketbase_admin_email": _string(settings.get("pocketbase_admin_email")),
            "pocketbase_admin_password": _string(settings.get("pocketbase_admin_password")),
        }


def _bool_env(value: Any) -> str:
    return "true" if _coerce_bool(value, False) else "false"


def _global_settings_dir() -> Path:
    try:
        from deeptutor.multi_user.paths import get_admin_path_service

        return get_admin_path_service().get_settings_dir()
    except Exception:
        return get_path_service().get_settings_dir()


def get_runtime_settings_service() -> RuntimeSettingsService:
    return RuntimeSettingsService.get_instance(_global_settings_dir())


def ensure_runtime_settings_files() -> None:
    """Create missing JSON settings files using migration/default rules.

    Startup callers use this as the single "settings bootstrap" hook:
    missing runtime files are created with safe defaults. Process
    environment variables remain deployment overrides and are intentionally
    not persisted into the JSON files.
    """
    get_runtime_settings_service().ensure_defaults()
    from .model_catalog import get_model_catalog_service

    get_model_catalog_service().load()


def load_system_settings() -> dict[str, Any]:
    return get_runtime_settings_service().load_system()


def load_auth_settings() -> dict[str, Any]:
    return get_runtime_settings_service().load_auth()


def load_integrations_settings() -> dict[str, Any]:
    return get_runtime_settings_service().load_integrations()


def export_runtime_settings_to_env(*, overwrite: bool = True) -> dict[str, str]:
    return get_runtime_settings_service().export_environment(overwrite=overwrite)


__all__ = [
    "DEFAULT_AUTH_SETTINGS",
    "DEFAULT_INTEGRATIONS_SETTINGS",
    "DEFAULT_SYSTEM_SETTINGS",
    "RuntimeSettingsService",
    "ensure_runtime_settings_files",
    "export_runtime_settings_to_env",
    "get_runtime_settings_service",
    "load_auth_settings",
    "load_integrations_settings",
    "load_system_settings",
]
