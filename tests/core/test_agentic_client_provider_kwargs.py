from __future__ import annotations

from deeptutor.core.agentic.client import build_completion_kwargs


def test_agentic_kwargs_disable_deepseek_flash_thinking_by_default() -> None:
    kwargs = build_completion_kwargs(
        temperature=0.7,
        model="deepseek-v4-flash",
        max_tokens=1024,
        binding="deepseek",
    )

    assert kwargs["max_tokens"] == 1024
    assert "reasoning_effort" not in kwargs
    assert kwargs["extra_body"] == {"thinking": {"type": "disabled"}}


def test_agentic_kwargs_enable_deepseek_pro_thinking_by_default() -> None:
    kwargs = build_completion_kwargs(
        temperature=0.7,
        model="deepseek-v4-pro",
        max_tokens=1024,
        binding="deepseek",
    )

    assert kwargs["reasoning_effort"] == "high"
    assert kwargs["extra_body"] == {"thinking": {"type": "enabled"}}


def test_agentic_kwargs_use_provider_minimal_thinking_without_top_level_effort() -> None:
    kwargs = build_completion_kwargs(
        temperature=0.7,
        model="deepseek-v4-pro",
        max_tokens=1024,
        binding="deepseek",
        reasoning_effort="minimal",
    )

    assert "reasoning_effort" not in kwargs
    assert kwargs["extra_body"] == {"thinking": {"type": "disabled"}}


def test_agentic_kwargs_preserve_legacy_shape_without_binding() -> None:
    kwargs = build_completion_kwargs(
        temperature=0.2,
        model="plain-model",
        max_tokens=256,
    )

    assert kwargs == {"temperature": 0.2, "max_tokens": 256}
