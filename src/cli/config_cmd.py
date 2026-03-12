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
        import os

        from dotenv import dotenv_values

        from src.services.config import load_config_with_main

        env_file = os.path.join(os.getcwd(), ".env")
        env_vars = dotenv_values(env_file) if os.path.exists(env_file) else {}

        llm_info = {
            "model": env_vars.get("LLM_MODEL", os.getenv("LLM_MODEL", "")),
            "base_url": env_vars.get("LLM_HOST", os.getenv("LLM_HOST", "")),
            "api_key": "***" if env_vars.get("LLM_API_KEY") or os.getenv("LLM_API_KEY") else "(not set)",
        }

        try:
            main_cfg = load_config_with_main("main.yaml")
        except Exception:
            main_cfg = {}

        console.print_json(json.dumps({
            "llm": llm_info,
            "language": main_cfg.get("system", {}).get("language", "en"),
            "tools": list(main_cfg.get("tools", {}).keys()),
        }, indent=2, ensure_ascii=False))
