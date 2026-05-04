"""Reasoning-content handling for OpenAI-compatible providers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from deeptutor.services.llm.provider_core.openai_compat_provider import (
    OpenAICompatProvider as ServicesOpenAICompatProvider,
)
from deeptutor.tutorbot.providers.openai_compat_provider import (
    OpenAICompatProvider as TutorBotOpenAICompatProvider,
)


def _response_with_reasoning_only():
    message = SimpleNamespace(
        content=None,
        reasoning_content="internal reasoning",
        reasoning=None,
        tool_calls=None,
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message, finish_reason="stop")],
    )


def _reasoning_only_chunk():
    delta = SimpleNamespace(
        content=None,
        reasoning_content="internal reasoning",
        reasoning=None,
        tool_calls=[],
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(delta=delta, finish_reason="stop")],
    )


@pytest.mark.parametrize(
    "provider_cls",
    [ServicesOpenAICompatProvider, TutorBotOpenAICompatProvider],
)
def test_parse_keeps_reasoning_content_out_of_visible_content(provider_cls) -> None:
    provider = provider_cls.__new__(provider_cls)

    response = provider._parse(_response_with_reasoning_only())

    assert response.content is None
    assert response.reasoning_content == "internal reasoning"


@pytest.mark.parametrize(
    "provider_cls",
    [ServicesOpenAICompatProvider, TutorBotOpenAICompatProvider],
)
def test_parse_chunks_keeps_reasoning_content_out_of_visible_content(provider_cls) -> None:
    response = provider_cls._parse_chunks([_reasoning_only_chunk()])

    assert response.content is None
    assert response.reasoning_content == "internal reasoning"
