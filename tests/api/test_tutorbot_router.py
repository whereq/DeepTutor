"""Tests for the TutorBot API router."""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover
    FastAPI = None
    TestClient = None

pytestmark = pytest.mark.skipif(
    FastAPI is None or TestClient is None, reason="fastapi not installed"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_manager(existing_channels: dict | None = None):
    """Return a (manager, saved) pair.

    manager   — fake TutorBotManager whose start_bot captures the final config
    saved     — dict populated with {"config": BotConfig} after start_bot runs
    """
    from deeptutor.services.tutorbot.manager import BotConfig

    saved: dict = {}

    class FakeManager:
        def _load_bot_config(self, bot_id: str) -> BotConfig | None:
            if existing_channels is not None:
                return BotConfig(
                    name=bot_id,
                    description="existing description",
                    persona="existing persona",
                    channels=existing_channels,
                )
            return None

        async def start_bot(self, bot_id: str, config: BotConfig):
            saved["config"] = config
            instance = MagicMock()
            instance.to_dict.return_value = {
                "bot_id": bot_id,
                "name": config.name,
                "channels": list(config.channels.keys()),
                "running": True,
            }
            return instance

    return FakeManager(), saved


def _make_client(monkeypatch, existing_channels: dict | None = None):
    """Build a TestClient with the tutorbot router and a patched manager."""
    manager, saved = _make_fake_manager(existing_channels)

    tutorbot_router_mod = importlib.import_module("deeptutor.api.routers.tutorbot")
    monkeypatch.setattr(tutorbot_router_mod, "get_tutorbot_manager", lambda: manager)

    app = FastAPI()
    app.include_router(tutorbot_router_mod.router, prefix="/api/v1/tutorbot")
    return TestClient(app), saved


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateBotPreservesExistingConfig:
    """Regression tests for the config-wipe bug.

    When the web UI starts a bot via POST /api/v1/tutorbot without supplying
    channel config, the previously saved channels must be kept — not wiped.
    """

    def test_channels_preserved_when_payload_has_no_channels(self, monkeypatch):
        """Existing channels on disk must not be wiped when payload omits channels."""
        existing_channels = {
            "telegram": {
                "enabled": True,
                "token": "123:ABC",
                "allow_from": ["999"],
            }
        }
        client, saved = _make_client(monkeypatch, existing_channels=existing_channels)

        resp = client.post("/api/v1/tutorbot", json={"bot_id": "my-bot"})

        assert resp.status_code == 200
        assert saved["config"].channels == existing_channels, (
            "Channels were wiped even though none were provided in the payload"
        )

    def test_payload_channels_override_existing(self, monkeypatch):
        """Explicitly provided channels in payload must take precedence over disk."""
        existing_channels = {"telegram": {"enabled": True, "token": "old"}}
        new_channels = {"slack": {"enabled": True, "token": "new-slack-token"}}

        client, saved = _make_client(monkeypatch, existing_channels=existing_channels)

        resp = client.post(
            "/api/v1/tutorbot",
            json={"bot_id": "my-bot", "channels": new_channels},
        )

        assert resp.status_code == 200
        assert saved["config"].channels == new_channels, (
            "Explicitly provided channels should override existing disk config"
        )

    def test_fresh_bot_with_no_existing_config(self, monkeypatch):
        """A brand-new bot with no existing config should start without error."""
        client, saved = _make_client(monkeypatch, existing_channels=None)

        resp = client.post(
            "/api/v1/tutorbot",
            json={"bot_id": "new-bot", "name": "New Bot"},
        )

        assert resp.status_code == 200
        assert saved["config"].channels == {}
        assert saved["config"].name == "New Bot"

    def test_existing_name_and_persona_preserved(self, monkeypatch):
        """Other fields (description, persona) from disk must also survive when not in payload."""
        existing_channels = {"telegram": {"enabled": True, "token": "tok"}}
        client, saved = _make_client(monkeypatch, existing_channels=existing_channels)

        resp = client.post("/api/v1/tutorbot", json={"bot_id": "my-bot"})

        assert resp.status_code == 200
        assert saved["config"].description == "existing description"
        assert saved["config"].persona == "existing persona"
