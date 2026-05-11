from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


def _load_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "docker_compose.py"
    spec = importlib.util.spec_from_file_location("docker_compose_under_test", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def test_render_docker_env_reads_json_only(tmp_path: Path) -> None:
    module = _load_module()
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    (settings_dir / "system.json").write_text(
        json.dumps({"backend_port": 9001, "frontend_port": 4000}),
        encoding="utf-8",
    )
    (settings_dir / "integrations.json").write_text(
        json.dumps({"pocketbase_port": 19090}),
        encoding="utf-8",
    )
    output_path = tmp_path / "docker.env"

    values = module.render_docker_env(settings_dir, output_path)

    assert values == {
        "DEEPTUTOR_DOCKER_BACKEND_PORT": "9001",
        "DEEPTUTOR_DOCKER_FRONTEND_PORT": "4000",
        "DEEPTUTOR_DOCKER_POCKETBASE_PORT": "19090",
    }
    saved = output_path.read_text(encoding="utf-8")
    assert "\nBACKEND_PORT=" not in saved
    assert "DEEPTUTOR_DOCKER_BACKEND_PORT=9001" in saved


def test_render_docker_env_uses_defaults_for_missing_or_invalid_json(tmp_path: Path) -> None:
    module = _load_module()
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    (settings_dir / "system.json").write_text(
        json.dumps({"backend_port": "bad", "frontend_port": 70000}),
        encoding="utf-8",
    )
    output_path = tmp_path / "docker.env"

    values = module.render_docker_env(settings_dir, output_path)

    assert values["DEEPTUTOR_DOCKER_BACKEND_PORT"] == "8001"
    assert values["DEEPTUTOR_DOCKER_FRONTEND_PORT"] == "3782"
    assert values["DEEPTUTOR_DOCKER_POCKETBASE_PORT"] == "8090"


def test_compose_files_do_not_consume_legacy_env_names() -> None:
    root = Path(__file__).resolve().parents[2]
    for name in ("docker-compose.yml", "docker-compose.ghcr.yml"):
        content = (root / name).read_text(encoding="utf-8")
        assert "${BACKEND_PORT" not in content
        assert "${FRONTEND_PORT" not in content
        assert "\n      - BACKEND_PORT" not in content
        assert "\n      - AUTH_ENABLED" not in content
        assert "DEEPTUTOR_DOCKER_BACKEND_PORT" in content


def test_dockerfile_uses_runtime_auth_placeholder() -> None:
    root = Path(__file__).resolve().parents[2]
    content = (root / "Dockerfile").read_text(encoding="utf-8")
    assert "__NEXT_PUBLIC_API_BASE_PLACEHOLDER__" in content
    assert "__NEXT_PUBLIC_AUTH_ENABLED_PLACEHOLDER__" in content
    assert "DEEPTUTOR_IGNORE_PROCESS_ENV_OVERRIDES=1" in content
    assert 'unset "$key"' in content
