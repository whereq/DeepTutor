#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools Package - Unified tool collection

Includes:
- rag_tool: RAG retrieval tool
- web_search: Web search tool
- paper_search_tool: Paper search tool
- tex_downloader: LaTeX source download tool
- tex_chunker: LaTeX text chunking tool
- question: Question generation tools (pdf_parser, question_extractor, exam_mimic)
"""

# Patch lightrag.utils BEFORE any imports that use lightrag
import importlib
import importlib.util
import sys

def _patch_lightrag_utils() -> None:
    try:
        if importlib.util.find_spec("lightrag") is None:
            return

        spec = importlib.util.find_spec("lightrag.utils")
        if not spec or not spec.origin or spec.loader is None:
            return

        utils = importlib.util.module_from_spec(spec)
        sys.modules["lightrag.utils"] = utils
        spec.loader.exec_module(utils)

        for key, value in {
            "verbose_debug": lambda *args, **kwargs: None,
            "VERBOSE_DEBUG": False,
            "get_env_value": lambda key, default=None: default,
            "safe_unicode_decode": lambda text: (
                text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else text
            ),
        }.items():
            if not hasattr(utils, key):
                setattr(utils, key, value)

        if not hasattr(utils, "wrap_embedding_func_with_attrs"):

            def _wrap(**attrs):
                def dec(func):
                    for key, value in attrs.items():
                        setattr(func, key, value)
                    return func

                return dec

            utils.wrap_embedding_func_with_attrs = _wrap
    except Exception as exc:
        print(f"Warning: Failed to patch lightrag.utils: {exc}")


_patch_lightrag_utils()

_LAZY_EXPORTS = {
    "brainstorm": (".brainstorm", "brainstorm"),
    "run_code": (".code_executor", "run_code"),
    "run_code_sync": (".code_executor", "run_code_sync"),
    "rag_search": (".rag_tool", "rag_search"),
    "reason": (".reason", "reason"),
    "web_search": (".web_search", "web_search"),
    "PaperSearchTool": (".paper_search_tool", "PaperSearchTool"),
    "TexChunker": (".tex_chunker", "TexChunker"),
    "TexDownloader": (".tex_downloader", "TexDownloader"),
    "read_tex_file": (".tex_downloader", "read_tex_file"),
    "BrainstormTool": (".builtin", "BrainstormTool"),
    "CodeExecutionTool": (".builtin", "CodeExecutionTool"),
    "GeoGebraAnalysisTool": (".builtin", "GeoGebraAnalysisTool"),
    "PaperSearchToolWrapper": (".builtin", "PaperSearchToolWrapper"),
    "RAGTool": (".builtin", "RAGTool"),
    "ReasonTool": (".builtin", "ReasonTool"),
    "WebSearchTool": (".builtin", "WebSearchTool"),
    "ToolPromptComposer": (".prompting", "ToolPromptComposer"),
    "load_prompt_hints": (".prompting", "load_prompt_hints"),
}

__all__ = sorted(_LAZY_EXPORTS)


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value

# Question generation tools (lazy import to avoid circular dependencies)
# Access via: from src.tools.question import parse_pdf_with_mineru, etc.
