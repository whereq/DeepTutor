"""Tests for chat capability per-stage token configuration via agents.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from deeptutor.services.config import loader as loader_module
from deeptutor.services.config.loader import (
    DEFAULT_CHAT_PARAMS,
    get_chat_params,
)


def _write_agents_yaml(tmp_path: Path, content: dict[str, Any]) -> Path:
    settings_dir = tmp_path / "data" / "user" / "settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    agents_file = settings_dir / "agents.yaml"
    agents_file.write_text(yaml.dump(content), encoding="utf-8")
    return tmp_path


class TestGetChatParams:
    """Verify get_chat_params() correctly resolves capabilities.chat."""

    def test_returns_defaults_when_file_missing(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(loader_module, "PROJECT_ROOT", tmp_path)
        params = get_chat_params()
        assert params == DEFAULT_CHAT_PARAMS

    def test_returns_defaults_when_chat_section_absent(self, tmp_path: Path, monkeypatch):
        project_root = _write_agents_yaml(
            tmp_path,
            {
                "capabilities": {"solve": {"temperature": 0.3}},
            },
        )
        monkeypatch.setattr(loader_module, "PROJECT_ROOT", project_root)
        params = get_chat_params()
        assert params["temperature"] == DEFAULT_CHAT_PARAMS["temperature"]
        assert params["responding"]["max_tokens"] == 8000
        assert params["thinking"]["max_tokens"] == 2000

    def test_overrides_specific_stage_only(self, tmp_path: Path, monkeypatch):
        project_root = _write_agents_yaml(
            tmp_path,
            {
                "capabilities": {
                    "chat": {
                        "responding": {"max_tokens": 12000},
                    },
                },
            },
        )
        monkeypatch.setattr(loader_module, "PROJECT_ROOT", project_root)
        params = get_chat_params()
        assert params["responding"]["max_tokens"] == 12000
        assert params["answer_now"]["max_tokens"] == 8000
        assert params["thinking"]["max_tokens"] == 2000
        assert params["temperature"] == 0.2

    def test_overrides_temperature(self, tmp_path: Path, monkeypatch):
        project_root = _write_agents_yaml(
            tmp_path,
            {
                "capabilities": {"chat": {"temperature": 0.7}},
            },
        )
        monkeypatch.setattr(loader_module, "PROJECT_ROOT", project_root)
        params = get_chat_params()
        assert params["temperature"] == 0.7
        assert params["responding"]["max_tokens"] == 8000

    def test_full_chat_block_round_trip(self, tmp_path: Path, monkeypatch):
        project_root = _write_agents_yaml(
            tmp_path,
            {
                "capabilities": {
                    "chat": {
                        "temperature": 0.4,
                        "responding": {"max_tokens": 16000},
                        "answer_now": {"max_tokens": 16000},
                        "thinking": {"max_tokens": 3000},
                        "observing": {"max_tokens": 3000},
                        "acting": {"max_tokens": 3000},
                        "react_fallback": {"max_tokens": 2500},
                    },
                },
            },
        )
        monkeypatch.setattr(loader_module, "PROJECT_ROOT", project_root)
        params = get_chat_params()
        assert params["temperature"] == 0.4
        assert params["responding"]["max_tokens"] == 16000
        assert params["answer_now"]["max_tokens"] == 16000
        assert params["thinking"]["max_tokens"] == 3000
        assert params["observing"]["max_tokens"] == 3000
        assert params["acting"]["max_tokens"] == 3000
        assert params["react_fallback"]["max_tokens"] == 2500


class TestReadIntHelper:
    """Verify ``_read_int`` gracefully resolves the two chat token budgets
    the single-loop pipeline still uses (``responding`` and ``answer_now``).

    The legacy four-stage budgets (``thinking``/``acting``/``observing``/
    ``react_fallback``) are no longer consumed by the pipeline — they remain
    valid keys in ``agents.yaml`` for forward/backward compatibility but
    have no behavioral effect here.
    """

    def test_empty_dict_falls_back_to_default(self):
        from deeptutor.agents.chat.agentic_pipeline import _read_int

        assert _read_int({}, key="max_tokens", default=8000) == 8000

    def test_resolves_nested_max_tokens(self):
        from deeptutor.agents.chat.agentic_pipeline import _read_int

        cfg = {"max_tokens": 5000}
        assert _read_int(cfg, key="max_tokens", default=8000) == 5000

    def test_coerces_string_numbers(self):
        from deeptutor.agents.chat.agentic_pipeline import _read_int

        cfg = {"max_tokens": "5000"}
        assert _read_int(cfg, key="max_tokens", default=8000) == 5000

    def test_falls_back_on_garbage(self):
        from deeptutor.agents.chat.agentic_pipeline import _read_int

        cfg = {"max_tokens": "abc"}
        assert _read_int(cfg, key="max_tokens", default=8000) == 8000

    def test_non_dict_input_falls_back(self):
        from deeptutor.agents.chat.agentic_pipeline import _read_int

        assert _read_int(12345, key="max_tokens", default=8000) == 8000
        assert _read_int(None, key="max_tokens", default=8000) == 8000
