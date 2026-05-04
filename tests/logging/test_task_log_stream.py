import json

import pytest

from deeptutor.api.utils.task_log_stream import KnowledgeTaskStreamManager


@pytest.mark.asyncio
async def test_knowledge_task_stream_emits_process_log_sse_event():
    manager = KnowledgeTaskStreamManager()
    manager.ensure_task("task-1")
    manager.emit_log("task-1", "Indexing started")

    stream = manager.stream("task-1")
    try:
        chunk = await anext(stream)
    finally:
        await stream.aclose()

    lines = chunk.splitlines()
    header, data_line = lines[:2]
    assert header == "event: process_log"
    payload = json.loads(data_line.removeprefix("data: "))
    assert payload["type"] == "process_log"
    assert payload["message"] == "Indexing started"
    assert payload["context"]["task_id"] == "task-1"
