# -*- coding: utf-8 -*-
"""
Event Bus
=========

Asynchronous event bus for inter-module communication.
Supports publish/subscribe pattern with non-blocking event delivery.

Also supports writing events to a file queue for cross-process communication
with external services like the standalone personalization service.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Global flag to enable/disable file queue for external personalization service
_file_queue_enabled: bool = False


class EventType(str, Enum):
    """Supported event types."""

    SOLVE_COMPLETE = "SOLVE_COMPLETE"
    QUESTION_COMPLETE = "QUESTION_COMPLETE"


@dataclass
class Event:
    """
    Event data structure for the event bus.

    Attributes:
        type: Event type identifier
        task_id: Unique task identifier
        user_input: Original user input/question
        agent_output: Agent's response/output
        tools_used: List of tools used during the task
        success: Whether the task completed successfully
        metadata: Additional event-specific data
        event_id: Unique event identifier (auto-generated)
        timestamp: Event creation timestamp (auto-generated)
    """

    type: EventType
    task_id: str
    user_input: str
    agent_output: str
    tools_used: List[str] = field(default_factory=list)
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "task_id": self.task_id,
            "user_input": self.user_input,
            "agent_output": self.agent_output,
            "tools_used": self.tools_used,
            "success": self.success,
            "metadata": self.metadata,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
        }


# Type alias for event handlers
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Singleton asynchronous event bus.

    Provides publish/subscribe functionality with non-blocking event delivery.
    Events are processed in the background without blocking the publisher.

    Usage:
        # Get the singleton instance
        bus = get_event_bus()

        # Subscribe to events
        async def handle_solve(event: Event):
            print(f"Solve completed: {event.task_id}")

        bus.subscribe(EventType.SOLVE_COMPLETE, handle_solve)

        # Publish events (non-blocking)
        await bus.publish(Event(
            type=EventType.SOLVE_COMPLETE,
            task_id="task-123",
            user_input="What is 2+2?",
            agent_output="The answer is 4.",
        ))
    """

    _instance: Optional["EventBus"] = None
    _initialized: bool = False

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if EventBus._initialized:
            return

        self._subscribers: Dict[EventType, List[EventHandler]] = {
            event_type: [] for event_type in EventType
        }
        self._task_queue: asyncio.Queue[Event] = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None
        self._running: bool = False

        EventBus._initialized = True
        logger.debug("EventBus initialized")

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: Async function to call when event is published
        """
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Handler subscribed to {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler to remove
        """
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.debug(f"Handler unsubscribed from {event_type.value}")

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers (non-blocking).

        The event is queued for background processing, allowing the publisher
        to continue immediately without waiting for handlers to complete.

        If file queue is enabled (for external personalization service),
        the event is also written to the file queue for cross-process delivery.

        Args:
            event: The event to publish
        """
        await self._task_queue.put(event)
        logger.debug(f"Event published: {event.type.value} (task_id={event.task_id})")

        # Write to file queue if enabled (for external personalization service)
        if _file_queue_enabled:
            try:
                _write_event_to_file_queue(event)
            except Exception as e:
                logger.warning(f"Failed to write event to file queue: {e}")

        # Start processor if not running
        if not self._running:
            await self.start()

    async def _process_events(self) -> None:
        """Background task that processes queued events."""
        while self._running:
            try:
                # Wait for an event with timeout to allow clean shutdown
                try:
                    event = await asyncio.wait_for(
                        self._task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Get handlers for this event type
                handlers = self._subscribers.get(event.type, [])

                if not handlers:
                    logger.debug(f"No handlers for event type: {event.type.value}")
                    self._task_queue.task_done()
                    continue

                # Execute all handlers concurrently
                for handler in handlers:
                    try:
                        await handler(event)
                        logger.debug(
                            f"Handler completed for {event.type.value} "
                            f"(task_id={event.task_id})"
                        )
                    except Exception as e:
                        logger.error(
                            f"Handler error for {event.type.value}: {e}",
                            exc_info=True,
                        )

                self._task_queue.task_done()

            except asyncio.CancelledError:
                logger.debug("Event processor cancelled")
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}", exc_info=True)

    async def start(self) -> None:
        """Start the event processor."""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")

    async def stop(self) -> None:
        """Stop the event processor and wait for pending events."""
        if not self._running:
            return

        self._running = False

        # Wait for queue to drain (with timeout)
        try:
            await asyncio.wait_for(self._task_queue.join(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("EventBus shutdown timeout - some events may be lost")

        # Cancel processor task
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        logger.info("EventBus stopped")

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        if cls._instance is not None:
            cls._instance._running = False
            if cls._instance._processor_task:
                cls._instance._processor_task.cancel()
        cls._instance = None
        cls._initialized = False


# Module-level singleton accessor
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get the singleton EventBus instance.

    Returns:
        The global EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# ============================================================================
# File Queue Integration for External Personalization Service
# ============================================================================


def enable_file_queue() -> None:
    """
    Enable writing events to file queue for external personalization service.
    
    Call this during application startup if you want to run the personalization
    service in a separate process.
    
    Usage:
        from src.core.event_bus import enable_file_queue
        enable_file_queue()
    """
    global _file_queue_enabled
    _file_queue_enabled = True
    logger.info("File queue enabled for external personalization service")


def disable_file_queue() -> None:
    """
    Disable writing events to file queue.
    
    Use this when running personalization in-process (default behavior).
    """
    global _file_queue_enabled
    _file_queue_enabled = False
    logger.debug("File queue disabled")


def is_file_queue_enabled() -> bool:
    """Check if file queue is enabled."""
    return _file_queue_enabled


def _write_event_to_file_queue(event: Event) -> None:
    """
    Write an event to the file queue for cross-process delivery.
    
    This is called automatically when file queue is enabled and an event
    is published. The event will be picked up by the standalone
    personalization service.
    
    Args:
        event: The event to write
    """
    try:
        from src.personalization.event_queue import QueuedEvent, get_event_queue
        
        # Convert Event to QueuedEvent
        queued_event = QueuedEvent(
            event_id=event.event_id,
            event_type=event.type.value if isinstance(event.type, EventType) else event.type,
            task_id=event.task_id,
            user_input=event.user_input,
            agent_output=event.agent_output,
            tools_used=event.tools_used,
            success=event.success,
            metadata=event.metadata,
            timestamp=event.timestamp.isoformat(),
        )
        
        # Push to file queue
        queue = get_event_queue()
        queue.push(queued_event)
        
        logger.debug(f"Event written to file queue: {event.type.value} ({event.event_id})")
        
    except ImportError:
        logger.warning("personalization.event_queue not available, skipping file queue")
    except Exception as e:
        logger.error(f"Failed to write event to file queue: {e}")
