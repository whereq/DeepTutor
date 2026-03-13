"""
CLI Config Command
==================

View and update DeepTutor configuration.
"""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def register(app: typer.Typer) -> None:

    @app.command("show")
    def config_show() -> None:
        """Show current configuration."""
        import json

        from deeptutor.services.config import get_env_store, load_config_with_main

        summary = get_env_store().as_summary()
        llm_info = {
            "binding": summary.llm["binding"],
            "model": summary.llm["model"],
            "base_url": summary.llm["host"],
            "api_key": "***" if summary.llm["api_key"] else "(not set)",
        }

        try:
            main_cfg = load_config_with_main("main.yaml")
        except Exception:
            main_cfg = {}

        console.print_json(
            json.dumps(
                {
                    "ports": {
                        "backend": summary.backend_port,
                        "frontend": summary.frontend_port,
                    },
                    "llm": llm_info,
                    "embedding": {
                        "binding": summary.embedding["binding"],
                        "model": summary.embedding["model"],
                        "host": summary.embedding["host"],
                        "api_key": "***" if summary.embedding["api_key"] else "(not set)",
                        "dimension": summary.embedding["dimension"],
                    },
                    "search": {
                        "provider": summary.search["provider"] or "(optional)",
                        "base_url": summary.search["base_url"],
                        "api_key": "***" if summary.search["api_key"] else "(not set)",
                    },
                    "language": main_cfg.get("system", {}).get("language", "en"),
                    "tools": list(main_cfg.get("tools", {}).keys()),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
