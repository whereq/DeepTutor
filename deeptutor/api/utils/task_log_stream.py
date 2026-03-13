import asyncio
import contextlib
import json
import threading
from collections import deque
from collections.abc import AsyncGenerator
from typing import Any


def _format_sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"


class KnowledgeTaskStreamManager:
    _instance: "KnowledgeTaskStreamManager | None" = None
    _instance_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._buffers: dict[str, deque[dict[str, Any]]] = {}
        self._subscribers: dict[str, list[tuple[asyncio.Queue, asyncio.AbstractEventLoop]]] = {}

    @classmethod
    def get_instance(cls) -> "KnowledgeTaskStreamManager":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def ensure_task(self, task_id: str):
        with self._lock:
            self._buffers.setdefault(task_id, deque(maxlen=500))
            self._subscribers.setdefault(task_id, [])

    def emit(self, task_id: str, event: str, payload: dict[str, Any]):
        event_payload = {"event": event, "payload": payload}
        with self._lock:
            self._buffers.setdefault(task_id, deque(maxlen=500)).append(event_payload)
            subscribers = list(self._subscribers.get(task_id, []))

        for queue, loop in subscribers:
            try:
                loop.call_soon_threadsafe(self._queue_event, queue, event_payload)
            except RuntimeError:
                continue

    def emit_log(self, task_id: str, line: str):
        self.emit(task_id, "log", {"line": line, "task_id": task_id})

    def emit_complete(self, task_id: str, detail: str = "Task completed"):
        self.emit(task_id, "complete", {"detail": detail, "task_id": task_id})

    def emit_failed(self, task_id: str, detail: str):
        self.emit(task_id, "failed", {"detail": detail, "task_id": task_id})

    def subscribe(
        self, task_id: str
    ) -> tuple[asyncio.Queue[dict[str, Any]], list[dict[str, Any]], asyncio.AbstractEventLoop]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=200)
        loop = asyncio.get_running_loop()
        with self._lock:
            self._buffers.setdefault(task_id, deque(maxlen=500))
            self._subscribers.setdefault(task_id, []).append((queue, loop))
            backlog = list(self._buffers[task_id])
        return queue, backlog, loop

    def unsubscribe(self, task_id: str, queue: asyncio.Queue[dict[str, Any]], loop: asyncio.AbstractEventLoop):
        with self._lock:
            subscribers = self._subscribers.get(task_id, [])
            self._subscribers[task_id] = [
                (subscriber_queue, subscriber_loop)
                for subscriber_queue, subscriber_loop in subscribers
                if subscriber_queue is not queue or subscriber_loop is not loop
            ]

    async def stream(self, task_id: str) -> AsyncGenerator[str, None]:
        queue, backlog, loop = self.subscribe(task_id)
        try:
            for item in backlog:
                yield _format_sse(item["event"], item["payload"])

            if backlog and backlog[-1]["event"] in {"complete", "failed"}:
                return

            while True:
                item = await queue.get()
                yield _format_sse(item["event"], item["payload"])
                if item["event"] in {"complete", "failed"}:
                    break
        finally:
            self.unsubscribe(task_id, queue, loop)

    @staticmethod
    def _queue_event(queue: asyncio.Queue[dict[str, Any]], payload: dict[str, Any]):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            pass


@contextlib.contextmanager
def capture_task_logs(task_id: str):
    """Compatibility context manager.

    We intentionally avoid capturing global stdout/stderr or root loggers here
    to prevent unrelated concurrent request logs from leaking into a task's SSE
    stream. Task producers should emit task logs explicitly through
    ``KnowledgeTaskStreamManager.emit_log``.
    """
    manager = KnowledgeTaskStreamManager.get_instance()
    manager.ensure_task(task_id)
    yield


def get_task_stream_manager() -> KnowledgeTaskStreamManager:
    return KnowledgeTaskStreamManager.get_instance()
