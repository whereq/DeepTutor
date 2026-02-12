# -*- coding: utf-8 -*-
"""
Event Queue for Inter-Process Communication
============================================

File-based event queue that enables the main application to pass events
to the personalization service running in a separate process.

The queue uses a simple JSON Lines format where each line is a complete
event. Events are appended atomically and consumed in order.
"""

import fcntl
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from src.services.path_service import get_path_service

logger = logging.getLogger(__name__)


@dataclass
class QueuedEvent:
    """
    Event stored in the file queue.
    
    This is a simplified event format for cross-process communication.
    """
    event_id: str
    event_type: str
    task_id: str
    user_input: str
    agent_output: str
    tools_used: List[str]
    success: bool
    metadata: Dict[str, Any]
    timestamp: str  # ISO format string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueuedEvent":
        """Create from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            task_id=data["task_id"],
            user_input=data["user_input"],
            agent_output=data["agent_output"],
            tools_used=data.get("tools_used", []),
            success=data.get("success", True),
            metadata=data.get("metadata", {}),
            timestamp=data["timestamp"],
        )


class EventFileQueue:
    """
    File-based event queue for inter-process communication.
    
    Features:
    - Atomic append operations with file locking
    - FIFO ordering with offset tracking
    - Automatic cleanup of processed events
    
    Usage:
        # Producer (main application)
        queue = EventFileQueue()
        queue.push(event)
        
        # Consumer (personalization service)
        queue = EventFileQueue()
        for event in queue.consume():
            process(event)
    """
    
    _instance: Optional["EventFileQueue"] = None
    
    def __new__(cls) -> "EventFileQueue":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        path_service = get_path_service()
        self._queue_dir = path_service.get_memory_dir() / "event_queue"
        self._queue_file = self._queue_dir / "events.jsonl"
        self._offset_file = self._queue_dir / "offset.txt"
        self._lock_file = self._queue_dir / ".lock"
        
        # Ensure directory exists
        self._queue_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialized = True
        logger.debug(f"EventFileQueue initialized at {self._queue_dir}")
    
    def push(self, event: QueuedEvent) -> None:
        """
        Push an event to the queue.
        
        Thread-safe and process-safe with file locking.
        
        Args:
            event: The event to enqueue
        """
        try:
            with open(self._lock_file, "w") as lock_f:
                # Acquire exclusive lock
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                try:
                    # Append event as JSON line
                    with open(self._queue_file, "a", encoding="utf-8") as f:
                        line = json.dumps(event.to_dict(), ensure_ascii=False)
                        f.write(line + "\n")
                        f.flush()
                        os.fsync(f.fileno())
                    
                    logger.debug(f"Event pushed to queue: {event.event_type} ({event.event_id})")
                finally:
                    # Release lock
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to push event to queue: {e}")
            raise
    
    def _get_offset(self) -> int:
        """Get the current read offset."""
        if not self._offset_file.exists():
            return 0
        try:
            return int(self._offset_file.read_text().strip())
        except (ValueError, IOError):
            return 0
    
    def _set_offset(self, offset: int) -> None:
        """Set the current read offset."""
        self._offset_file.write_text(str(offset))
    
    def consume(self, batch_size: int = 10) -> Iterator[QueuedEvent]:
        """
        Consume events from the queue.
        
        Yields events starting from the current offset and updates
        the offset as events are consumed.
        
        Args:
            batch_size: Maximum number of events to consume at once
            
        Yields:
            QueuedEvent instances
        """
        if not self._queue_file.exists():
            return
        
        try:
            with open(self._lock_file, "w") as lock_f:
                # Acquire shared lock for reading
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_SH)
                try:
                    offset = self._get_offset()
                    count = 0
                    
                    with open(self._queue_file, "r", encoding="utf-8") as f:
                        # Seek to current offset
                        f.seek(offset)
                        
                        # Use readline() instead of for-loop iteration
                        # because for-loop disables f.tell()
                        while count < batch_size:
                            line = f.readline()
                            if not line:
                                # End of file
                                break
                            
                            line = line.strip()
                            if not line:
                                continue
                            
                            try:
                                data = json.loads(line)
                                event = QueuedEvent.from_dict(data)
                                count += 1
                                
                                # Update offset before yielding
                                # (in case consumer crashes mid-processing)
                                new_offset = f.tell()
                                
                                yield event
                                
                                # Only update offset after successful processing
                                self._set_offset(new_offset)
                                
                            except json.JSONDecodeError as e:
                                logger.warning(f"Invalid JSON in queue file: {e}")
                                continue
                            except Exception as e:
                                logger.error(f"Error processing queued event: {e}")
                                continue
                finally:
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to consume events from queue: {e}")
    
    def peek(self) -> Optional[QueuedEvent]:
        """
        Peek at the next event without consuming it.
        
        Returns:
            The next event, or None if queue is empty
        """
        if not self._queue_file.exists():
            return None
        
        try:
            offset = self._get_offset()
            
            with open(self._queue_file, "r", encoding="utf-8") as f:
                f.seek(offset)
                line = f.readline().strip()
                
                if not line:
                    return None
                
                data = json.loads(line)
                return QueuedEvent.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to peek event: {e}")
            return None
    
    def pending_count(self) -> int:
        """
        Get the approximate number of pending events.
        
        Returns:
            Number of unprocessed events (approximate)
        """
        if not self._queue_file.exists():
            return 0
        
        try:
            offset = self._get_offset()
            count = 0
            
            with open(self._queue_file, "r", encoding="utf-8") as f:
                f.seek(offset)
                for line in f:
                    if line.strip():
                        count += 1
            
            return count
        except Exception as e:
            logger.error(f"Failed to count pending events: {e}")
            return 0
    
    def cleanup(self, max_age_days: int = 7) -> None:
        """
        Clean up old events from the queue file.
        
        This compacts the queue by removing already-processed events.
        
        Args:
            max_age_days: Remove events older than this many days
        """
        if not self._queue_file.exists():
            return
        
        try:
            with open(self._lock_file, "w") as lock_f:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                try:
                    offset = self._get_offset()
                    
                    # Read remaining events
                    remaining = []
                    with open(self._queue_file, "r", encoding="utf-8") as f:
                        f.seek(offset)
                        remaining = f.readlines()
                    
                    # Rewrite file with only remaining events
                    with open(self._queue_file, "w", encoding="utf-8") as f:
                        f.writelines(remaining)
                    
                    # Reset offset
                    self._set_offset(0)
                    
                    logger.info(f"Queue cleaned up, {len(remaining)} events remaining")
                finally:
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to cleanup queue: {e}")
    
    def clear(self) -> None:
        """Clear all events from the queue."""
        try:
            if self._queue_file.exists():
                self._queue_file.unlink()
            self._set_offset(0)
            logger.info("Queue cleared")
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None


# Module-level singleton accessor
_event_queue: Optional[EventFileQueue] = None


def get_event_queue() -> EventFileQueue:
    """
    Get the singleton EventFileQueue instance.
    
    Returns:
        The global EventFileQueue instance.
    """
    global _event_queue
    if _event_queue is None:
        _event_queue = EventFileQueue()
    return _event_queue
