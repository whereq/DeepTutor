from __future__ import annotations

import json
from pathlib import Path

from deeptutor.services.config.runtime_settings import (
    RuntimeSettingsService,
    ensure_runtime_settings_files,
)

RUNTIME_ENV_KEYS = (
    "BACKEND_PORT",
    "FRONTEND_PORT",
    "NEXT_PUBLIC_API_BASE_EXTERNAL",
    "NEXT_PUBLIC_API_BASE",
    "CORS_ORIGIN",
    "CORS_ORIGINS",
    "DISABLE_SSL_VERIFY",
    "CHAT_ATTACHMENT_DIR",
    "AUTH_ENABLED",
    "NEXT_PUBLIC_AUTH_ENABLED",
    "AUTH_USERNAME",
    "AUTH_PASSWORD_HASH",
    "AUTH_TOKEN_EXPIRE_HOURS",
    "AUTH_COOKIE_SECURE",
    "POCKETBASE_URL",
    "POCKETBASE_PORT",
    "POCKETBASE_EXTERNAL_URL",
    "POCKETBASE_ADMIN_EMAIL",
    "POCKETBASE_ADMIN_PASSWORD",
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _clear_runtime_env(monkeypatch) -> None:
    for key in RUNTIME_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_runtime_settings_creates_defaults_without_reading_dotenv(tmp_path: Path) -> None:
    legacy_env = tmp_path / ".env"
    legacy_env.write_text(
        "BACKEND_PORT=9001\nAUTH_ENABLED=true\nPOCKETBASE_URL=http://legacy.invalid\n",
        encoding="utf-8",
    )
    service = RuntimeSettingsService(tmp_path / "settings")

    assert service.load_system(include_process_overrides=False)["backend_port"] == 8001
    assert service.load_auth(include_process_overrides=False)["enabled"] is False
    assert service.load_integrations(include_process_overrides=False)["pocketbase_url"] == ""

    assert _read_json(service.path_for("system"))["backend_port"] == 8001
    assert _read_json(service.path_for("auth"))["enabled"] is False


def test_runtime_process_env_is_explicit_override(tmp_path: Path) -> None:
    service = RuntimeSettingsService(
        tmp_path / "settings",
        process_env={
            "BACKEND_PORT": "9100",
            "AUTH_ENABLED": "true",
            "POCKETBASE_PORT": "9090",
        },
    )
    service.save_system({"backend_port": 8001, "frontend_port": 3782})
    service.save_auth({"enabled": False, "username": "admin"})
    service.save_integrations({"pocketbase_port": 8090})

    assert service.load_system()["backend_port"] == 9100
    assert service.load_auth()["enabled"] is True
    assert service.load_integrations()["pocketbase_port"] == 9090
    assert _read_json(service.path_for("system"))["backend_port"] == 8001
    assert _read_json(service.path_for("auth"))["enabled"] is False
    assert _read_json(service.path_for("integrations"))["pocketbase_port"] == 8090


def test_render_environment_uses_json_backed_runtime_names(monkeypatch, tmp_path: Path) -> None:
    _clear_runtime_env(monkeypatch)
    service = RuntimeSettingsService(tmp_path / "settings")
    service.save_system(
        {
            "backend_port": 8010,
            "frontend_port": 3790,
            "cors_origins": ["https://app.example"],
            "disable_ssl_verify": True,
        }
    )
    service.save_auth({"enabled": True, "username": "admin", "token_expire_hours": 12})
    service.save_integrations(
        {
            "pocketbase_url": "http://pocketbase:8090",
            "pocketbase_admin_email": "admin@example.com",
        }
    )

    env = service.render_environment()

    assert env["BACKEND_PORT"] == "8010"
    assert env["FRONTEND_PORT"] == "3790"
    assert env["CORS_ORIGINS"] == "https://app.example"
    assert env["DISABLE_SSL_VERIFY"] == "true"
    assert env["AUTH_ENABLED"] == "true"
    assert env["NEXT_PUBLIC_AUTH_ENABLED"] == "true"
    assert env["AUTH_TOKEN_EXPIRE_HOURS"] == "12"
    assert env["POCKETBASE_URL"] == "http://pocketbase:8090"
    assert "AUTH_SECRET" not in env


def test_exported_environment_does_not_become_runtime_override(monkeypatch, tmp_path: Path) -> None:
    _clear_runtime_env(monkeypatch)

    service = RuntimeSettingsService(tmp_path / "settings")
    service.save_system({"backend_port": 8010})
    service.save_auth({"enabled": False})

    service.export_environment(overwrite=True)
    assert service.load_system()["backend_port"] == 8010
    assert service.load_auth()["enabled"] is False

    service.save_system({"backend_port": 8020})
    service.save_auth({"enabled": True})

    assert service.load_system()["backend_port"] == 8020
    assert service.load_auth()["enabled"] is True


def test_existing_process_environment_remains_deployment_override(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("BACKEND_PORT", "9100")
    service = RuntimeSettingsService(tmp_path / "settings")
    service.save_system({"backend_port": 8010})

    service.export_environment(overwrite=True)
    service.save_system({"backend_port": 8020})

    assert service.load_system()["backend_port"] == 9100


def test_startup_ensure_creates_missing_runtime_jsons_with_defaults(
    monkeypatch, tmp_path: Path
) -> None:
    _clear_runtime_env(monkeypatch)
    settings_dir = tmp_path / "settings"

    from deeptutor.services.config import model_catalog as model_catalog_module
    from deeptutor.services.config import runtime_settings as runtime_settings_module

    runtime_settings_module.RuntimeSettingsService._instances.clear()
    model_catalog_module.ModelCatalogService._instances.clear()
    monkeypatch.setattr(runtime_settings_module, "_global_settings_dir", lambda: settings_dir)
    monkeypatch.setattr(
        model_catalog_module.get_path_service(),
        "get_settings_file",
        lambda name: settings_dir / f"{name}.json",
    )

    ensure_runtime_settings_files()

    assert (settings_dir / "system.json").exists()
    assert (settings_dir / "auth.json").exists()
    assert (settings_dir / "integrations.json").exists()
    assert (settings_dir / "model_catalog.json").exists()
    assert _read_json(settings_dir / "system.json")["backend_port"] == 8001
    assert _read_json(settings_dir / "auth.json")["enabled"] is False
    assert _read_json(settings_dir / "integrations.json")["pocketbase_url"] == ""
    assert set(_read_json(settings_dir / "model_catalog.json")["services"]) == {
        "llm",
        "embedding",
        "search",
    }


def test_runtime_settings_can_ignore_process_overrides(tmp_path: Path) -> None:
    service = RuntimeSettingsService(
        tmp_path / "settings",
        process_env={
            "DEEPTUTOR_IGNORE_PROCESS_ENV_OVERRIDES": "1",
            "BACKEND_PORT": "9901",
            "AUTH_ENABLED": "true",
        },
    )
    service.save_system({"backend_port": 8001})
    service.save_auth({"enabled": False})

    assert service.load_system()["backend_port"] == 8001
    assert service.load_auth()["enabled"] is False
