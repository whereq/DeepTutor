from __future__ import annotations

import json
from pathlib import Path

from deeptutor.services.config.launch_settings import load_launch_settings


def _settings_dir(root: Path) -> Path:
    path = root / "data" / "user" / "settings"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_launch_settings_prefer_runtime_settings(monkeypatch, tmp_path: Path) -> None:
    for key in ("BACKEND_PORT", "FRONTEND_PORT", "UI_LANGUAGE", "LANGUAGE"):
        monkeypatch.delenv(key, raising=False)

    (tmp_path / ".env").write_text(
        "BACKEND_PORT=9001\nFRONTEND_PORT=4000\nUI_LANGUAGE=en\n",
        encoding="utf-8",
    )
    settings_dir = _settings_dir(tmp_path)
    (settings_dir / "env.json").write_text(
        json.dumps({"ports": {"backend": 8101, "frontend": 4100}}),
        encoding="utf-8",
    )
    (settings_dir / "interface.json").write_text(
        json.dumps({"language": "zh"}),
        encoding="utf-8",
    )

    settings = load_launch_settings(tmp_path)

    assert settings.backend_port == 8101
    assert settings.frontend_port == 4100
    assert settings.language == "zh"
    assert "env.json" in settings.source
    assert "interface.json" in settings.source


def test_launch_settings_fall_back_to_env_when_settings_missing(
    monkeypatch, tmp_path: Path
) -> None:
    for key in ("BACKEND_PORT", "FRONTEND_PORT", "UI_LANGUAGE", "LANGUAGE"):
        monkeypatch.delenv(key, raising=False)

    (tmp_path / ".env").write_text(
        "BACKEND_PORT=9101\nFRONTEND_PORT=4200\nUI_LANGUAGE=zh\n",
        encoding="utf-8",
    )

    settings = load_launch_settings(tmp_path)

    assert settings.backend_port == 9101
    assert settings.frontend_port == 4200
    assert settings.source == ".env"
    assert settings.language == "zh"
    assert settings.source == ".env"


def test_launch_settings_fall_back_per_invalid_port(monkeypatch, tmp_path: Path) -> None:
    for key in ("BACKEND_PORT", "FRONTEND_PORT", "UI_LANGUAGE", "LANGUAGE"):
        monkeypatch.delenv(key, raising=False)

    (tmp_path / ".env").write_text(
        "BACKEND_PORT=9101\nFRONTEND_PORT=4200\n",
        encoding="utf-8",
    )
    settings_dir = _settings_dir(tmp_path)
    (settings_dir / "env.json").write_text(
        json.dumps({"ports": {"backend": "not-a-port", "frontend": 70000}}),
        encoding="utf-8",
    )

    settings = load_launch_settings(tmp_path)

    assert settings.backend_port == 9101
    assert settings.frontend_port == 4200
