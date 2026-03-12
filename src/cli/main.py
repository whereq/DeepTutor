"""
CLI Main Entry Point
====================

Typer application that registers all sub-commands.
Run via ``python -m deeptutor`` or ``deeptutor``.
"""

from __future__ import annotations

import typer

from src.runtime.mode import RunMode, set_mode
from src.services.setup import get_backend_port

set_mode(RunMode.CLI)

app = typer.Typer(
    name="deeptutor",
    help="DeepTutor – an agent-native intelligent learning companion.",
    no_args_is_help=True,
    add_completion=False,
)

# ---- sub-command groups ----

chat_app = typer.Typer(help="Chat with DeepTutor (tools & capabilities).")
kb_app = typer.Typer(help="Manage knowledge bases.")
memory_app = typer.Typer(help="View and manage learner memory.")
plugin_app = typer.Typer(help="List and inspect plugins.")
config_app = typer.Typer(help="View or update configuration.")

app.add_typer(chat_app, name="chat")
app.add_typer(kb_app, name="kb")
app.add_typer(memory_app, name="memory")
app.add_typer(plugin_app, name="plugin")
app.add_typer(config_app, name="config")

# ---- register sub-commands from modules ----

from src.cli.chat import register as _reg_chat
from src.cli.config_cmd import register as _reg_config
from src.cli.kb import register as _reg_kb
from src.cli.memory import register as _reg_memory
from src.cli.plugin import register as _reg_plugin

_reg_chat(chat_app)
_reg_kb(kb_app)
_reg_memory(memory_app)
_reg_plugin(plugin_app)
_reg_config(config_app)


# ---- top-level serve command ----


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind address."),
    port: int = typer.Option(get_backend_port(), help="Port number."),
    reload: bool = typer.Option(False, help="Enable auto-reload for development."),
) -> None:
    """Start the DeepTutor API server (requires server dependencies)."""
    set_mode(RunMode.SERVER)
    try:
        import uvicorn
    except ImportError:
        from rich.console import Console

        Console().print(
            "[bold red]Error:[/] API server dependencies not installed.\n"
            "Run: pip install -r requirements/server.txt",
        )
        raise typer.Exit(code=1)

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_excludes=["web/*", "data/*"] if reload else None,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
