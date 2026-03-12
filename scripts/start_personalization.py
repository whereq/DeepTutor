#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Personalization Service Launcher
================================

Standalone script to run the personalization service in a separate process.
This service:
1. Polls the event queue for learning events from the main application
2. Processes events with the MemoryAgent to extract insights
3. Updates user memory (preferences, weak points, milestones)

Usage:
    python scripts/start_personalization.py

The service runs independently and only outputs personalization-related logs.
Press Ctrl+C to stop.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / "DeepTutor.env", override=False)
load_dotenv(project_root / ".env", override=False)

# Force unbuffered output
os.environ["PYTHONUNBUFFERED"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


def setup_personalization_logging() -> logging.Logger:
    """
    Set up dedicated logging for personalization service.
    
    Only shows logs from personalization-related modules.
    """
    # Create a dedicated logger for personalization
    logger = logging.getLogger("personalization")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # Console handler with custom format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Also capture logs from related modules
    related_modules = [
        "src.personalization",
        "src.personalization.service",
        "src.personalization.memory",
        "src.personalization.memory_agent",
        "src.personalization.event_queue",
    ]
    
    for module_name in related_modules:
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(logging.DEBUG)
        module_logger.handlers.clear()
        module_logger.addHandler(console_handler)
        module_logger.propagate = False
    
    # Suppress other loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger


def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("  DeepTutor Personalization Service")
    print("=" * 60)
    print()
    print("  This service processes learning events and maintains")
    print("  user memory for personalized learning experience.")
    print()
    print("  Press Ctrl+C to stop.")
    print()
    print("=" * 60)
    print()


class PersonalizationRunner:
    """
    Standalone runner for the personalization service.
    
    Polls the event queue and processes events using MemoryAgent.
    """
    
    def __init__(self, poll_interval: float = 2.0):
        """
        Initialize the runner.
        
        Args:
            poll_interval: Seconds between queue polls
        """
        self.poll_interval = poll_interval
        self._running = False
        self._logger = logging.getLogger("personalization")
        self._service = None
        self._event_queue = None
    
    async def start(self) -> None:
        """Start the personalization service."""
        from src.events.event_bus import Event, EventType
        from src.personalization import get_personalization_service
        from src.personalization.event_queue import QueuedEvent, get_event_queue
        
        self._running = True
        self._service = get_personalization_service()
        self._event_queue = get_event_queue()
        
        # Start the service (initializes memory and agent)
        await self._service.start()
        
        self._logger.info("Personalization service started")
        self._logger.info(f"Polling event queue every {self.poll_interval}s")
        self._logger.info(f"Auto-update: {self._service.auto_update}")
        
        # Check for pending events
        pending = self._event_queue.pending_count()
        if pending > 0:
            self._logger.info(f"Found {pending} pending events in queue")
        
        # Main event loop
        while self._running:
            try:
                await self._process_queue()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in event loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
        
        self._logger.info("Personalization service stopping...")
    
    async def _process_queue(self) -> None:
        """Process events from the queue."""
        from src.events.event_bus import Event, EventType
        from src.personalization.event_queue import QueuedEvent
        
        # Consume events from the queue
        events_processed = 0
        
        for queued_event in self._event_queue.consume(batch_size=10):
            try:
                self._logger.info(
                    f"Processing event: {queued_event.event_type} "
                    f"(task_id={queued_event.task_id})"
                )
                
                # Convert QueuedEvent to Event
                event = Event(
                    type=EventType(queued_event.event_type),
                    task_id=queued_event.task_id,
                    user_input=queued_event.user_input,
                    agent_output=queued_event.agent_output,
                    tools_used=queued_event.tools_used,
                    success=queued_event.success,
                    metadata=queued_event.metadata,
                    event_id=queued_event.event_id,
                )
                
                # Process with the service's handler
                await self._service._handle_event(event)
                
                events_processed += 1
                self._logger.info(
                    f"Event processed: {queued_event.event_type} "
                    f"(task_id={queued_event.task_id})"
                )
                
            except Exception as e:
                self._logger.error(
                    f"Failed to process event {queued_event.event_id}: {e}",
                    exc_info=True
                )
        
        if events_processed > 0:
            self._logger.info(f"Batch completed: {events_processed} events processed")
    
    async def stop(self) -> None:
        """Stop the personalization service."""
        self._running = False
        
        if self._service:
            await self._service.stop()
        
        self._logger.info("Personalization service stopped")
    
    def request_stop(self) -> None:
        """Request graceful shutdown (called from signal handler)."""
        self._running = False


async def main():
    """Main entry point."""
    # Set up logging
    logger = setup_personalization_logging()
    
    # Print banner
    print_banner()
    
    # Create runner
    runner = PersonalizationRunner(poll_interval=2.0)
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Shutdown signal received")
        runner.request_stop()
    
    # Handle SIGINT (Ctrl+C) and SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass
    
    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await runner.stop()
    
    print()
    print("=" * 60)
    print("  Personalization service stopped.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
