from __future__ import annotations

from pathlib import Path

from deeptutor.runtime import launcher


def test_packaged_web_cache_replaces_next_public_placeholders(tmp_path: Path) -> None:
    packaged = tmp_path / "pkg"
    (packaged / ".next" / "static").mkdir(parents=True)
    (packaged / "server.js").write_text(
        "const api='__NEXT_PUBLIC_API_BASE_PLACEHOLDER__';",
        encoding="utf-8",
    )
    (packaged / ".next" / "static" / "app.js").write_text(
        "auth='__NEXT_PUBLIC_AUTH_ENABLED_PLACEHOLDER__'",
        encoding="utf-8",
    )

    runtime = launcher._copy_packaged_web_if_needed(
        packaged,
        home=tmp_path / "home",
        api_base="http://localhost:8001",
        auth_enabled=True,
    )

    assert (runtime / "server.js").read_text(encoding="utf-8") == (
        "const api='http://localhost:8001';"
    )
    assert "auth='true'" in (runtime / ".next" / "static" / "app.js").read_text(
        encoding="utf-8"
    )


def test_packaged_web_cache_refreshes_when_public_settings_change(tmp_path: Path) -> None:
    packaged = tmp_path / "pkg"
    (packaged / ".next").mkdir(parents=True)
    (packaged / "server.js").write_text(
        "const api='__NEXT_PUBLIC_API_BASE_PLACEHOLDER__';",
        encoding="utf-8",
    )
    home = tmp_path / "home"

    first = launcher._copy_packaged_web_if_needed(
        packaged,
        home=home,
        api_base="http://localhost:8001",
        auth_enabled=False,
    )
    second = launcher._copy_packaged_web_if_needed(
        packaged,
        home=home,
        api_base="https://api.example",
        auth_enabled=False,
    )

    assert first == second
    assert "https://api.example" in (second / "server.js").read_text(encoding="utf-8")
