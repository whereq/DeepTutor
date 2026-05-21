"""Unit tests for TutorBot channel dispatch behavior."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from deeptutor.tutorbot.bus.events import OutboundMessage
from deeptutor.tutorbot.channels.manager import ChannelManager
from deeptutor.tutorbot.config.schema import ChannelsConfig


class _OneShotBus:
    def __init__(self, msg: OutboundMessage):
        self._msg = msg
        self._calls = 0

    async def consume_outbound(self) -> OutboundMessage:
        self._calls += 1
        if self._calls == 1:
            return self._msg
        raise asyncio.CancelledError


class _DummyChannel:
    def __init__(self):
        self.send = AsyncMock()


async def _dispatch_one(msg: OutboundMessage, config: ChannelsConfig) -> _DummyChannel:
    channel = _DummyChannel()
    manager = ChannelManager(config, _OneShotBus(msg))  # type: ignore[arg-type]
    manager.channels = {msg.channel: channel}  # type: ignore[dict-item]

    await manager._dispatch_outbound()
    return channel


class TestChannelManagerToolHints:
    @pytest.mark.asyncio
    async def test_tool_hint_progress_skipped_by_default(self):
        msg = OutboundMessage(
            channel="zulip",
            chat_id="pm:42",
            content='message("Hello")',
            metadata={"_progress": True, "_tool_hint": True},
        )

        channel = await _dispatch_one(msg, ChannelsConfig(send_tool_hints=False))

        channel.send.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_tool_hint_progress_dispatched_when_enabled(self):
        msg = OutboundMessage(
            channel="zulip",
            chat_id="pm:42",
            content='message("Hello")',
            metadata={"_progress": True, "_tool_hint": True},
        )

        channel = await _dispatch_one(msg, ChannelsConfig(send_tool_hints=True))

        channel.send.assert_awaited_once_with(msg)
