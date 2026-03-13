"""Compatibility helpers for third-party tool dependencies."""

from __future__ import annotations

import importlib.util
import logging
import sys

logger = logging.getLogger(__name__)

_PATCHED = False


def ensure_lightrag_compat() -> None:
    """Patch older ``lightrag.utils`` builds with missing helper symbols."""
    global _PATCHED
    if _PATCHED:
        return

    try:
        if importlib.util.find_spec("lightrag") is None:
            _PATCHED = True
            return

        spec = importlib.util.find_spec("lightrag.utils")
        if not spec or not spec.origin or spec.loader is None:
            _PATCHED = True
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
                    for attr_name, attr_value in attrs.items():
                        setattr(func, attr_name, attr_value)
                    return func

                return dec

            utils.wrap_embedding_func_with_attrs = _wrap
    except Exception:
        logger.warning("Failed to patch lightrag.utils compatibility helpers", exc_info=True)
    finally:
        _PATCHED = True
