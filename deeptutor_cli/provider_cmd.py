"""CLI commands for provider auth (OAuth-first providers)."""

from __future__ import annotations

import typer

from .common import maybe_run


def register(app: typer.Typer) -> None:
    @app.command("login")
    def provider_login(
        provider: str = typer.Argument(
            ...,
            help="OAuth provider: openai-codex | github-copilot",
        ),
    ) -> None:
        """Authenticate an OAuth-backed provider."""
        key = provider.strip().lower().replace("-", "_")
        if key == "openai_codex":
            _login_openai_codex()
            return
        if key == "github_copilot":
            maybe_run(_login_github_copilot())
            return
        raise typer.BadParameter(
            f"Unknown provider `{provider}`. Supported: openai-codex, github-copilot"
        )


def _login_openai_codex() -> None:
    try:
        from oauth_cli_kit import get_token, login_oauth_interactive
    except ImportError:
        typer.echo(
            "oauth_cli_kit is not installed. Install CLI deps: "
            "pip install -r requirements/cli.txt"
        )
        raise typer.Exit(code=1)

    token = None
    try:
        token = get_token()
    except Exception:
        token = None
    if not (token and getattr(token, "access", None)):
        token = login_oauth_interactive(
            print_fn=typer.echo,
            prompt_fn=typer.prompt,
        )
    if not (token and getattr(token, "access", None)):
        typer.echo("OpenAI Codex OAuth authentication failed.")
        raise typer.Exit(code=1)
    typer.echo("OpenAI Codex OAuth authentication succeeded.")


async def _login_github_copilot() -> None:
    try:
        from litellm import acompletion
    except ImportError:
        typer.echo("litellm is not installed. Install CLI deps: pip install -r requirements/cli.txt")
        raise typer.Exit(code=1)
    try:
        await acompletion(
            model="github_copilot/gpt-4o",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
    except Exception as exc:
        typer.echo(f"GitHub Copilot OAuth authentication failed: {exc}")
        raise typer.Exit(code=1) from exc
    typer.echo("GitHub Copilot OAuth authentication succeeded.")
