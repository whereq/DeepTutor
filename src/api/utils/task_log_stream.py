import asyncio
import contextlib
import json
import logging
import re
import sys
import threading
from collections import deque
from collections.abc import AsyncGenerator
from typing import Any

from src.logging import ConsoleFormatter

ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


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


class _TaskLogHandler(logging.Handler):
    def __init__(self, task_id: str, manager: KnowledgeTaskStreamManager):
        super().__init__(level=logging.DEBUG)
        self._task_id = task_id
        self._manager = manager
        formatter = ConsoleFormatter(service_prefix=None)
        formatter.use_colors = False
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord):
        try:
            if record.name == "uvicorn.access":
                message = record.getMessage()
                if "/api/v1/knowledge" not in message or "/tasks/" in message:
                    return

            line = ANSI_ESCAPE_RE.sub("", self.format(record)).strip()
            if line:
                self._manager.emit_log(self._task_id, line)
        except Exception:
            self.handleError(record)


class _TaskTextStream:
    def __init__(self, task_id: str, manager: KnowledgeTaskStreamManager, stream):
        self._task_id = task_id
        self._manager = manager
        self._stream = stream
        self._buffer = ""

    def write(self, text: str) -> int:
        if self._stream is not None:
            self._stream.write(text)
            self._stream.flush()

        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = ANSI_ESCAPE_RE.sub("", line.rstrip("\r")).strip()
            if line:
                self._manager.emit_log(self._task_id, line)
        return len(text)

    def flush(self):
        if self._stream is not None:
            self._stream.flush()

    def flush_buffer(self):
        line = ANSI_ESCAPE_RE.sub("", self._buffer.rstrip("\r")).strip()
        self._buffer = ""
        if line:
            self._manager.emit_log(self._task_id, line)

    def isatty(self) -> bool:
        return False


def _collect_target_loggers() -> list[logging.Logger]:
    candidates: list[logging.Logger] = [logging.getLogger()]

    parent_logger = logging.getLogger("deeptutor")
    if isinstance(parent_logger, logging.Logger):
        candidates.append(parent_logger)

    for name, logger_obj in logging.root.manager.loggerDict.items():
        if not isinstance(logger_obj, logging.Logger):
            continue
        if name.startswith("deeptutor") or name.startswith("llama_index"):
            candidates.append(logger_obj)

    unique: list[logging.Logger] = []
    seen: set[int] = set()
    for logger_obj in candidates:
        key = id(logger_obj)
        if key in seen:
            continue
        seen.add(key)
        unique.append(logger_obj)
    return unique


@contextlib.contextmanager
def capture_task_logs(task_id: str):
    manager = KnowledgeTaskStreamManager.get_instance()
    manager.ensure_task(task_id)

    handler = _TaskLogHandler(task_id, manager)
    stdout_stream = _TaskTextStream(task_id, manager, stream=sys.stdout)
    stderr_stream = _TaskTextStream(task_id, manager, stream=sys.stderr)
    attached_loggers = _collect_target_loggers()

    for logger_obj in attached_loggers:
        logger_obj.addHandler(handler)

    try:
        with contextlib.redirect_stdout(stdout_stream), contextlib.redirect_stderr(stderr_stream):
            yield
    finally:
        stdout_stream.flush_buffer()
        stderr_stream.flush_buffer()
        for logger_obj in attached_loggers:
            if handler in logger_obj.handlers:
                logger_obj.removeHandler(handler)


def get_task_stream_manager() -> KnowledgeTaskStreamManager:
    return KnowledgeTaskStreamManager.get_instance()
