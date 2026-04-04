"""Tests for provider-backed execution in llm.factory."""

from __future__ import annotations

import pytest

from deeptutor.services.llm.config import LLMConfig
from deeptutor.services.llm.factory import complete, stream


@pytest.mark.asyncio
async def test_factory_complete_uses_litellm(monkeypatch) -> None:
    cfg = LLMConfig(
        model="google/gemini-2.5-pro",
        api_key="sk-or-test",
        base_url="https://openrouter.ai/api/v1",
        binding="openrouter",
        provider_name="openrouter",
        provider_mode="gateway",
    )
    captured: dict[str, object] = {}

    async def _fake_litellm_complete(**kwargs):
        captured.update(kwargs)
        return "ok"

    monkeypatch.setattr("deeptutor.services.llm.factory.get_llm_config", lambda: cfg)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_available", lambda: True)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_complete", _fake_litellm_complete)

    result = await complete("hello")
    assert result == "ok"
    assert captured["provider_name"] == "openrouter"
    assert captured["model"] == "google/gemini-2.5-pro"


@pytest.mark.asyncio
async def test_factory_complete_uses_direct_azure(monkeypatch) -> None:
    cfg = LLMConfig(
        model="gpt-4o-mini",
        api_key="azure-key",
        base_url="https://example.openai.azure.com/openai/deployments/demo",
        binding="azure_openai",
        provider_name="azure_openai",
        provider_mode="direct",
        api_version="2024-10-21",
    )
    captured: dict[str, object] = {}

    async def _fake_cloud_complete(**kwargs):
        captured.update(kwargs)
        return "ok"

    monkeypatch.setattr("deeptutor.services.llm.factory.get_llm_config", lambda: cfg)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_available", lambda: False)
    monkeypatch.setattr("deeptutor.services.llm.cloud_provider.complete", _fake_cloud_complete)

    result = await complete("hello")
    assert result == "ok"
    assert captured["binding"] == "azure_openai"


@pytest.mark.asyncio
async def test_factory_complete_openai_codex_requires_oauth(monkeypatch) -> None:
    cfg = LLMConfig(
        model="openai_codex/codex-mini-latest",
        api_key="",
        base_url="https://chatgpt.com/backend-api",
        binding="openai_codex",
        provider_name="openai_codex",
        provider_mode="oauth",
    )
    monkeypatch.setattr("deeptutor.services.llm.factory.get_llm_config", lambda: cfg)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_available", lambda: False)

    with pytest.raises(Exception):
        await complete("hello", max_retries=0)


@pytest.mark.asyncio
async def test_factory_stream_uses_litellm(monkeypatch) -> None:
    cfg = LLMConfig(
        model="deepseek-chat",
        api_key="deep-key",
        base_url="https://api.deepseek.com/v1",
        binding="deepseek",
        provider_name="deepseek",
        provider_mode="standard",
    )

    async def _fake_litellm_stream(**kwargs):
        _ = kwargs
        yield "a"
        yield "b"

    monkeypatch.setattr("deeptutor.services.llm.factory.get_llm_config", lambda: cfg)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_available", lambda: True)
    monkeypatch.setattr("deeptutor.services.llm.factory.litellm_stream", _fake_litellm_stream)

    chunks = []
    async for item in stream("hello"):
        chunks.append(item)
    assert "".join(chunks) == "ab"
