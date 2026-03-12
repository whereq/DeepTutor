# -*- coding: utf-8 -*-
"""
RAG Service
===========

Unified RAG service providing a single entry point for all RAG operations.
"""

import json
import os
from pathlib import Path
import shutil
import logging
from typing import Any, Dict, List, Optional

from src.logging import get_logger

from .factory import get_pipeline, has_pipeline, list_pipelines

class _RAGRawLogHandler(logging.Handler):
    def __init__(self, event_sink, loop) -> None:
        super().__init__(level=logging.DEBUG)
        self._event_sink = event_sink
        self._loop = loop

    def emit(self, record: logging.LogRecord) -> None:
        if self._event_sink is None:
            return
        try:
            module_name = getattr(record, "module_name", record.name.split(".")[-1])
            level_name = getattr(record, "display_level", record.levelname)
            message = record.getMessage()
            if message.strip() == "LightRAG log forwarding enabled":
                return
            line = f"[{module_name}] {level_name}: {message}".strip()
            if not line:
                return

            async def _emit() -> None:
                await self._event_sink(
                    "raw_log",
                    line,
                    {
                        "trace_layer": "raw",
                        "logger_name": record.name,
                        "log_level": level_name,
                        "module_name": module_name,
                    },
                )

            self._loop.create_task(_emit())
        except Exception:
            pass


# Default knowledge base directory
DEFAULT_KB_BASE_DIR = str(
    Path(__file__).resolve().parent.parent.parent.parent / "data" / "knowledge_bases"
)


class RAGService:
    """
    Unified RAG service entry point.

    Provides a clean interface for RAG operations:
    - Knowledge base initialization
    - Search/retrieval
    - Knowledge base deletion

    Usage:
        # Default configuration
        service = RAGService()
        await service.initialize("my_kb", ["doc1.pdf"])
        result = await service.search("query", "my_kb")

        # Custom configuration for testing
        service = RAGService(kb_base_dir="/tmp/test_kb", provider="llamaindex")
        await service.initialize("test", ["test.txt"])
    """

    def __init__(
        self,
        kb_base_dir: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize RAG service.

        Args:
            kb_base_dir: Base directory for knowledge bases.
                         Defaults to data/knowledge_bases.
            provider: RAG pipeline provider to use.
                      Defaults to RAG_PROVIDER env var or "raganything".
        """
        self.logger = get_logger("RAGService")
        self.kb_base_dir = kb_base_dir or DEFAULT_KB_BASE_DIR
        self.provider = provider or os.getenv("RAG_PROVIDER", "raganything")
        self._pipeline = None

    def _get_pipeline(self):
        """Get or create pipeline instance."""
        if self._pipeline is None:
            self._pipeline = get_pipeline(self.provider, kb_base_dir=self.kb_base_dir)
        return self._pipeline

    async def initialize(self, kb_name: str, file_paths: List[str], **kwargs) -> bool:
        """
        Initialize a knowledge base with documents.

        Args:
            kb_name: Knowledge base name
            file_paths: List of file paths to process
            **kwargs: Additional arguments passed to pipeline

        Returns:
            True if successful

        Example:
            service = RAGService()
            success = await service.initialize("my_kb", ["doc1.pdf", "doc2.txt"])
        """
        self.logger.info(f"Initializing KB '{kb_name}' with provider '{self.provider}'")
        pipeline = self._get_pipeline()
        return await pipeline.initialize(kb_name=kb_name, file_paths=file_paths, **kwargs)

    async def search(
        self,
        query: str,
        kb_name: str,
        mode: str = "hybrid",
        event_sink=None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Search a knowledge base.

        Args:
            query: Search query
            kb_name: Knowledge base name
            mode: Search mode (hybrid, local, global, naive)
            **kwargs: Additional arguments passed to pipeline

        Returns:
            Search results dictionary with keys:
            - query: Original query
            - answer: Generated answer
            - content: Retrieved content
            - mode: Search mode used
            - provider: Pipeline provider used

        Example:
            service = RAGService()
            result = await service.search("What is ML?", "textbook")
            print(result["answer"])
        """
        # Get the provider from KB metadata, fallback to instance provider
        provider = self._get_provider_for_kb(kb_name)
        with self._capture_raw_logs(event_sink, provider):
            await self._emit_tool_event(
                event_sink,
                "status",
                f"Query: {query}",
                {"query": query, "kb_name": kb_name, "mode": mode, "trace_layer": "summary"},
            )
            await self._emit_tool_event(
                event_sink,
                "status",
                f"Selecting provider: {provider}",
                {"provider": provider, "trace_layer": "summary"},
            )

            self.logger.info(
                f"Searching KB '{kb_name}' with provider '{provider}' and query: {query[:50]}..."
            )

            # Get pipeline for the specific provider
            pipeline = get_pipeline(provider, kb_base_dir=self.kb_base_dir)

            await self._emit_tool_event(
                event_sink,
                "status",
                f"Retrieving from knowledge base '{kb_name}'...",
                {"provider": provider, "mode": mode, "trace_layer": "summary"},
            )

            result = await pipeline.search(query=query, kb_name=kb_name, mode=mode, **kwargs)

            # Ensure consistent return format
            if "query" not in result:
                result["query"] = query
            if "answer" not in result and "content" in result:
                result["answer"] = result["content"]
            if "content" not in result and "answer" in result:
                result["content"] = result["answer"]
            if "provider" not in result:
                result["provider"] = provider
            if "mode" not in result:
                result["mode"] = mode

            answer = result.get("answer") or result.get("content") or ""
            await self._emit_tool_event(
                event_sink,
                "status",
                f"Retrieved {len(answer)} characters of grounded context.",
                {"provider": provider, "mode": mode, "kb_name": kb_name, "trace_layer": "summary"},
            )

            return result

    async def _emit_tool_event(
        self,
        event_sink,
        event_type: str,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        if event_sink is None:
            return
        await event_sink(event_type, message, metadata or {})

    def _capture_raw_logs(self, event_sink, provider: str):
        from contextlib import ExitStack, contextmanager
        import asyncio

        @contextmanager
        def _manager():
            if event_sink is None:
                yield
                return

            loop = asyncio.get_running_loop()
            handler = _RAGRawLogHandler(event_sink, loop)
            handler.setLevel(logging.DEBUG)
            targets = self._iter_rag_loggers(provider)
            with ExitStack() as stack:
                for logger in targets:
                    logger.addHandler(handler)
                    stack.callback(logger.removeHandler, handler)
                try:
                    yield
                finally:
                    handler.close()

        return _manager()

    def _iter_rag_loggers(self, provider: str) -> list[logging.Logger]:
        provider_name = (provider or "").lower()
        names = {
            "lightrag",
            "deeptutor.RAGService",
            "deeptutor.RAGForward",
        }
        if provider_name == "raganything":
            names.update(
                {
                    "deeptutor.RAGAnythingPipeline",
                    "deeptutor.RAGAnythingDoclingPipeline",
                    "deeptutor.ImageMigration",
                }
            )
        elif provider_name == "llamaindex":
            names.add("deeptutor.LlamaIndexPipeline")
        return [logging.getLogger(name) for name in sorted(names)]

    def _get_provider_for_kb(self, kb_name: str) -> str:
        """
        Get the RAG provider for a specific knowledge base.
        
        Priority:
        1. kb_config.json (authoritative source)
        2. Instance provider

        Args:
            kb_name: Knowledge base name

        Returns:
            Provider name (e.g., 'llamaindex', 'lightrag', 'raganything')
        """
        try:
            # First, try kb_config.json (authoritative source)
            kb_config_file = Path(self.kb_base_dir) / "kb_config.json"
            if kb_config_file.exists():
                with open(kb_config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    kb_config = config.get("knowledge_bases", {}).get(kb_name, {})
                    provider = kb_config.get("rag_provider")
                    if provider:
                        self.logger.info(f"Using provider '{provider}' from kb_config.json")
                        return provider

            # Fall back to the provider configured on the service instance.
            self.logger.info(f"No provider in config, using instance provider: {self.provider}")
            return self.provider

        except Exception as e:
            self.logger.warning(
                f"Error reading provider from config: {e}, using instance provider"
            )
            return self.provider

    async def delete(self, kb_name: str) -> bool:
        """
        Delete a knowledge base.

        Args:
            kb_name: Knowledge base name

        Returns:
            True if successful

        Example:
            service = RAGService()
            success = await service.delete("old_kb")
        """
        self.logger.info(f"Deleting KB '{kb_name}'")
        pipeline = self._get_pipeline()

        if hasattr(pipeline, "delete"):
            return await pipeline.delete(kb_name=kb_name)

        # Fallback: delete directory manually
        kb_dir = Path(self.kb_base_dir) / kb_name
        if kb_dir.exists():
            shutil.rmtree(kb_dir)
            self.logger.info(f"Deleted KB directory: {kb_dir}")
            return True
        return False

    async def smart_retrieve(
        self,
        context: str,
        kb_name: str,
        query_hints: Optional[List[str]] = None,
        mode: str = "hybrid",
        max_queries: int = 3,
    ) -> Dict[str, Any]:
        """
        High-level retrieval: generate multiple queries, search in parallel, aggregate.

        This consolidates the query-generation + parallel-search + LLM-aggregation
        pattern previously duplicated in PlannerAgent._pre_retrieve and
        IdeaAgent._retrieve_context.

        Args:
            context: Text that describes the information need (question, topic, etc.).
            kb_name: Knowledge base to search.
            query_hints: Optional explicit queries. If not provided, the LLM
                         generates ``max_queries`` queries from *context*.
            mode: RAG search mode.
            max_queries: How many queries to generate when *query_hints* is empty.

        Returns:
            A dict with ``answer`` (aggregated text) and ``sources`` (list of dicts).
        """
        import asyncio

        if query_hints:
            queries = query_hints
        else:
            queries = await self._generate_queries(context, max_queries)

        # parallel search
        tasks = [self.search(query=q, kb_name=kb_name, mode=mode) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        passages: list[str] = []
        all_sources: list[dict] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            content = r.get("content") or r.get("answer") or ""
            if content:
                passages.append(content)
                all_sources.append({"query": r.get("query", ""), "provider": r.get("provider", "")})

        if not passages:
            return {"answer": "", "sources": []}

        aggregated = await self._aggregate(context, passages)
        return {"answer": aggregated, "sources": all_sources}

    async def _generate_queries(self, context: str, n: int) -> list[str]:
        """Use LLM to generate *n* diverse search queries from *context*."""
        try:
            from src.services.llm import complete

            prompt = (
                f"Generate {n} diverse search queries to retrieve information relevant "
                f"to the following context. Return ONLY the queries, one per line.\n\n"
                f"Context:\n{context[:2000]}"
            )
            raw = await complete(prompt, system_prompt="You are a search query generator.")
            lines = [l.strip().lstrip("0123456789.-) ") for l in raw.strip().split("\n") if l.strip()]
            return lines[:n] if lines else [context[:200]]
        except Exception:
            return [context[:200]]

    async def _aggregate(self, context: str, passages: list[str]) -> str:
        """LLM-aggregate multiple retrieved passages into a single answer."""
        try:
            from src.services.llm import complete

            combined = "\n---\n".join(passages)
            prompt = (
                "Synthesise the following retrieved passages into a concise, "
                "relevant summary for the given context.\n\n"
                f"Context:\n{context[:1000]}\n\n"
                f"Passages:\n{combined[:6000]}"
            )
            return await complete(prompt, system_prompt="You are a knowledge synthesiser.")
        except Exception:
            return "\n\n".join(passages)

    @staticmethod
    def list_providers() -> List[Dict[str, str]]:
        """
        List available RAG pipeline providers.

        Returns:
            List of provider info dictionaries

        Example:
            providers = RAGService.list_providers()
            for p in providers:
                print(f"{p['id']}: {p['description']}")
        """
        return list_pipelines()

    @staticmethod
    def get_current_provider() -> str:
        """
        Get the currently configured default provider.

        Returns:
            Provider name from RAG_PROVIDER env var or default
        """
        return os.getenv("RAG_PROVIDER", "raganything")

    @staticmethod
    def has_provider(name: str) -> bool:
        """
        Check if a provider is available.

        Args:
            name: Provider name

        Returns:
            True if provider exists
        """
        return has_pipeline(name)
