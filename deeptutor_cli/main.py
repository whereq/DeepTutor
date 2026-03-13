"""CLI entry point for the standalone ``deeptutor-cli`` package."""

from __future__ import annotations

import json

import typer

from deeptutor.runtime.mode import RunMode, set_mode
from deeptutor.services.setup import get_backend_port

from .chat import register as register_chat
from .common import build_turn_request, console, maybe_run
from .config_cmd import register as register_config
from .kb import register as register_kb
from .memory import register as register_memory
from .notebook import register as register_notebook
from .plugin import register as register_plugin
from .provider_cmd import register as register_provider
from .session_cmd import register as register_session

set_mode(RunMode.CLI)

app = typer.Typer(
    name="deeptutor",
    help="DeepTutor CLI – fully usable without starting the web server.",
    no_args_is_help=True,
    add_completion=False,
)

chat_app = typer.Typer(help="Interactive chat and one-shot turns.")
kb_app = typer.Typer(help="Manage knowledge bases.")
memory_app = typer.Typer(help="View and manage lightweight memory.")
plugin_app = typer.Typer(help="List plugins.")
config_app = typer.Typer(help="Inspect configuration.")
session_app = typer.Typer(help="Manage shared sessions.")
notebook_app = typer.Typer(help="Manage notebooks and imported markdown records.")
provider_app = typer.Typer(help="Manage provider OAuth login.")

app.add_typer(chat_app, name="chat")
app.add_typer(kb_app, name="kb")
app.add_typer(memory_app, name="memory")
app.add_typer(plugin_app, name="plugin")
app.add_typer(config_app, name="config")
app.add_typer(session_app, name="session")
app.add_typer(notebook_app, name="notebook")
app.add_typer(provider_app, name="provider")

register_chat(chat_app)
register_kb(kb_app)
register_memory(memory_app)
register_plugin(plugin_app)
register_config(config_app)
register_session(session_app)
register_notebook(notebook_app)
register_provider(provider_app)


@app.command("run")
def run_capability(
    capability: str = typer.Argument(..., help="Capability name or CLI alias."),
    message: str = typer.Argument(..., help="Message to send."),
    session: str | None = typer.Option(None, "--session", help="Existing session id."),
    tool: list[str] = typer.Option([], "--tool", "-t", help="Enabled tool(s)."),
    kb: list[str] = typer.Option([], "--kb", help="Knowledge base name."),
    notebook_ref: list[str] = typer.Option([], "--notebook-ref", help="Notebook references."),
    history_ref: list[str] = typer.Option([], "--history-ref", help="Referenced session ids."),
    language: str = typer.Option("en", "--language", "-l", help="Response language."),
    config: list[str] = typer.Option([], "--config", help="Capability config key=value."),
    config_json: str | None = typer.Option(None, "--config-json", help="Capability config as JSON."),
    fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
) -> None:
    """Run any capability through the unified turn runtime."""
    from deeptutor.app import DeepTutorApp
    from .common import run_turn_and_render

    request = build_turn_request(
        content=message,
        capability=capability,
        session_id=session,
        tools=tool,
        knowledge_bases=kb,
        language=language,
        config_items=config,
        config_json=config_json,
        notebook_refs=notebook_ref,
        history_refs=history_ref,
    )
    maybe_run(run_turn_and_render(app=DeepTutorApp(), request=request, fmt=fmt))


@app.command("solve")
def solve(
    message: str = typer.Argument(..., help="Problem to solve."),
    session: str | None = typer.Option(None, "--session", help="Existing session id."),
    tool: list[str] = typer.Option([], "--tool", "-t", help="Enabled tool(s)."),
    kb: list[str] = typer.Option([], "--kb", help="Knowledge base name."),
    notebook_ref: list[str] = typer.Option([], "--notebook-ref", help="Notebook references."),
    history_ref: list[str] = typer.Option([], "--history-ref", help="Referenced session ids."),
    language: str = typer.Option("en", "--language", "-l", help="Response language."),
    detailed_answer: bool = typer.Option(True, "--detailed-answer/--brief-answer", help="Control deep solve detail."),
    fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
) -> None:
    """Alias for ``run deep_solve``."""
    _run_alias(
        capability="deep_solve",
        message=message,
        session=session,
        tool=tool,
        kb=kb,
        notebook_ref=notebook_ref,
        history_ref=history_ref,
        language=language,
        fmt=fmt,
        config_items=[f"detailed_answer={str(detailed_answer).lower()}"],
        config_json=None,
    )


@app.command("quiz")
def quiz(
    message: str = typer.Argument(..., help="Topic or instruction for quiz generation."),
    session: str | None = typer.Option(None, "--session", help="Existing session id."),
    tool: list[str] = typer.Option([], "--tool", "-t", help="Enabled tool(s)."),
    kb: list[str] = typer.Option([], "--kb", help="Knowledge base name."),
    notebook_ref: list[str] = typer.Option([], "--notebook-ref", help="Notebook references."),
    history_ref: list[str] = typer.Option([], "--history-ref", help="Referenced session ids."),
    language: str = typer.Option("en", "--language", "-l", help="Response language."),
    mode: str = typer.Option("custom", "--mode", help="Quiz mode: custom | mimic."),
    num_questions: int = typer.Option(1, "--num-questions", help="Number of questions."),
    difficulty: str = typer.Option("", "--difficulty", help="Difficulty hint."),
    question_type: str = typer.Option("", "--question-type", help="Question type hint."),
    preference: str = typer.Option("", "--preference", help="Preference hint."),
    paper_path: str = typer.Option("", "--paper-path", help="Parsed exam paper path."),
    max_questions: int = typer.Option(10, "--max-questions", help="Question limit for mimic mode."),
    fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
) -> None:
    """Alias for ``run deep_question``."""
    _run_alias(
        capability="deep_question",
        message=message,
        session=session,
        tool=tool,
        kb=kb,
        notebook_ref=notebook_ref,
        history_ref=history_ref,
        language=language,
        fmt=fmt,
        config_items=[
            f"mode={mode}",
            f"num_questions={num_questions}",
            f"difficulty={difficulty}",
            f"question_type={question_type}",
            f"preference={preference}",
            f"paper_path={paper_path}",
            f"max_questions={max_questions}",
        ],
        config_json=None,
    )


@app.command("research")
def research(
    message: str = typer.Argument(..., help="Research prompt."),
    session: str | None = typer.Option(None, "--session", help="Existing session id."),
    tool: list[str] = typer.Option([], "--tool", "-t", help="Additional tools."),
    kb: list[str] = typer.Option([], "--kb", help="Knowledge base name."),
    notebook_ref: list[str] = typer.Option([], "--notebook-ref", help="Notebook references."),
    history_ref: list[str] = typer.Option([], "--history-ref", help="Referenced session ids."),
    language: str = typer.Option("en", "--language", "-l", help="Response language."),
    mode: str = typer.Option(..., "--mode", help="Research mode: notes | report | comparison | learning_path."),
    depth: str = typer.Option(..., "--depth", help="Research depth: quick | standard | deep."),
    source: list[str] = typer.Option(..., "--source", help="Research source(s): kb | web | papers."),
    fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
) -> None:
    """Alias for ``run deep_research``."""
    config_json = {
        "mode": mode,
        "depth": depth,
        "sources": source,
    }
    _run_alias(
        capability="deep_research",
        message=message,
        session=session,
        tool=tool,
        kb=kb,
        notebook_ref=notebook_ref,
        history_ref=history_ref,
        language=language,
        fmt=fmt,
        config_items=[],
        config_json=json.dumps(config_json, ensure_ascii=False),
    )


@app.command("animate")
def animate(
    message: str = typer.Argument(..., help="Animation prompt."),
    session: str | None = typer.Option(None, "--session", help="Existing session id."),
    language: str = typer.Option("en", "--language", "-l", help="Response language."),
    output_mode: str = typer.Option("video", "--output-mode", help="video | frames | storyboard"),
    quality: str = typer.Option("medium", "--quality", help="low | medium | high"),
    style_hint: str = typer.Option("", "--style-hint", help="Visual style hint."),
    fmt: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json."),
) -> None:
    """Alias for ``run math_animator``."""
    _run_alias(
        capability="math_animator",
        message=message,
        session=session,
        tool=[],
        kb=[],
        notebook_ref=[],
        history_ref=[],
        language=language,
        fmt=fmt,
        config_items=[
            f"output_mode={output_mode}",
            f"quality={quality}",
            f"style_hint={style_hint}",
        ],
        config_json=None,
    )


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind address."),
    port: int = typer.Option(get_backend_port(), help="Port number."),
    reload: bool = typer.Option(False, help="Enable auto-reload for development."),
) -> None:
    """Start the DeepTutor API server."""
    set_mode(RunMode.SERVER)
    try:
        import uvicorn
    except ImportError:
        console.print(
            "[bold red]Error:[/] API server dependencies not installed.\n"
            "Run: pip install 'deeptutor[server]' or pip install -r requirements/server.txt"
        )
        raise typer.Exit(code=1)

    uvicorn.run(
        "deeptutor.api.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_excludes=["web/*", "data/*"] if reload else None,
    )


def _run_alias(
    *,
    capability: str,
    message: str,
    session: str | None,
    tool: list[str],
    kb: list[str],
    notebook_ref: list[str],
    history_ref: list[str],
    language: str,
    fmt: str,
    config_items: list[str],
    config_json: str | None,
) -> None:
    from deeptutor.app import DeepTutorApp
    from .common import run_turn_and_render

    request = build_turn_request(
        content=message,
        capability=capability,
        session_id=session,
        tools=tool,
        knowledge_bases=kb,
        language=language,
        config_items=config_items,
        config_json=config_json,
        notebook_refs=notebook_ref,
        history_refs=history_ref,
    )
    maybe_run(run_turn_and_render(app=DeepTutorApp(), request=request, fmt=fmt))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
