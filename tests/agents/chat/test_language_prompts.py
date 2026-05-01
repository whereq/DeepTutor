from __future__ import annotations

from types import SimpleNamespace

import pytest

from deeptutor.agents.chat.agentic_pipeline import AgenticChatPipeline
from deeptutor.agents.chat.chat_agent import ChatAgent


@pytest.fixture(autouse=True)
def _fake_llm_config(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = SimpleNamespace(
        binding="openai",
        model="gpt-test",
        api_key="sk-test",
        base_url="https://example.test/v1",
        api_version=None,
    )
    monkeypatch.setattr(
        "deeptutor.agents.chat.agentic_pipeline.get_llm_config",
        lambda: cfg,
    )
    monkeypatch.setattr("deeptutor.agents.base_agent.get_llm_config", lambda: cfg)


def test_agentic_chat_final_prompt_uses_selected_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeRegistry:
        def build_prompt_text(self, *_args, **_kwargs) -> str:
            return "- tool"

    monkeypatch.setattr(
        "deeptutor.agents.chat.agentic_pipeline.get_tool_registry",
        lambda: FakeRegistry(),
    )

    zh_prompt = AgenticChatPipeline(language="zh")._responding_system_prompt([])
    en_prompt = AgenticChatPipeline(language="en")._responding_system_prompt([])

    assert "你是 DeepTutor 的最终回答阶段" in zh_prompt
    assert "请严格使用中文" in zh_prompt
    assert "You are DeepTutor's final response stage" in en_prompt
    assert "Write ALL reader-facing text" in en_prompt


def test_legacy_chat_agent_system_prompt_uses_selected_language() -> None:
    zh_messages = ChatAgent(language="zh", config={}).build_messages(
        message="解释梯度下降",
        history=[],
    )
    en_messages = ChatAgent(language="en", config={}).build_messages(
        message="Explain gradient descent",
        history=[],
    )

    assert "你是 DeepTutor" in zh_messages[0]["content"]
    assert "请严格使用中文" in zh_messages[0]["content"]
    assert "You are DeepTutor" in en_messages[0]["content"]
    assert "Write ALL reader-facing text" in en_messages[0]["content"]
