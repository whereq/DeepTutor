"""Interactive runtime settings initializer."""

from __future__ import annotations

from pathlib import Path

import typer

from deeptutor.runtime.home import DEEPTUTOR_HOME_ENV, get_runtime_home


def _reset_runtime_singletons() -> None:
    try:
        from deeptutor.services.path_service import PathService

        PathService.reset_instance()
    except Exception:
        pass
    try:
        from deeptutor.services.config.runtime_settings import RuntimeSettingsService

        RuntimeSettingsService._instances.clear()
    except Exception:
        pass
    try:
        from deeptutor.services.config.model_catalog import ModelCatalogService

        ModelCatalogService._instances.clear()
    except Exception:
        pass


def _prompt(default: str, label: str, *, hide: bool = False) -> str:
    value = typer.prompt(label, default=default or "", hide_input=hide, show_default=bool(default))
    return str(value or "").strip()


def _ensure_model_service(catalog: dict, service_name: str, profile_id: str, model_id: str):
    services = catalog.setdefault("services", {})
    service = services.setdefault(
        service_name,
        {"active_profile_id": profile_id, "active_model_id": model_id, "profiles": []},
    )
    profiles = service.setdefault("profiles", [])
    profile = next(
        (item for item in profiles if item.get("id") == service.get("active_profile_id")), None
    )
    if profile is None:
        profile = {
            "id": profile_id,
            "name": "Default LLM Endpoint"
            if service_name == "llm"
            else "Default Embedding Endpoint",
            "binding": "openai",
            "base_url": "",
            "api_key": "",
            "api_version": "",
            "extra_headers": {},
            "models": [],
        }
        profiles.append(profile)
        service["active_profile_id"] = profile_id
    models = profile.setdefault("models", [])
    model = next(
        (item for item in models if item.get("id") == service.get("active_model_id")), None
    )
    if model is None:
        model = {"id": model_id, "name": "Default Model", "model": ""}
        models.append(model)
        service["active_model_id"] = model_id
    return profile, model


def run_init(*, cli_only: bool = False, home: str | Path | None = None) -> None:
    runtime_home = get_runtime_home(home)
    runtime_home.mkdir(parents=True, exist_ok=True)
    import os

    os.environ[DEEPTUTOR_HOME_ENV] = str(runtime_home)
    _reset_runtime_singletons()

    from deeptutor.runtime.banner import labels_for, print_banner, resolve_language
    from deeptutor.services.config import get_model_catalog_service, get_runtime_settings_service
    from deeptutor.services.setup import init_user_directories

    init_user_directories(runtime_home)

    language = resolve_language()
    strings = labels_for(language)

    print_banner(language=language, mode_key="init.mode")
    typer.echo(f"{strings['init.workspace']}: {runtime_home}")
    typer.echo(strings["init.note_settings_dir"])

    runtime = get_runtime_settings_service()
    system = runtime.load_system(include_process_overrides=False)
    if not cli_only:
        system["backend_port"] = int(
            _prompt(str(system.get("backend_port") or 8001), strings["init.backend_port"])
        )
        system["frontend_port"] = int(
            _prompt(str(system.get("frontend_port") or 3782), strings["init.frontend_port"])
        )
        runtime.save_system(system)

    catalog_service = get_model_catalog_service()
    catalog = catalog_service.load()
    llm_profile, llm_model = _ensure_model_service(
        catalog,
        "llm",
        "llm-profile-default",
        "llm-model-default",
    )
    typer.echo(f"\n{strings['init.llm_section']}")
    llm_profile["binding"] = _prompt(
        str(llm_profile.get("binding") or "openai"), strings["init.binding"]
    )
    llm_profile["base_url"] = _prompt(
        str(llm_profile.get("base_url") or "https://api.openai.com/v1"),
        strings["init.base_url"],
    )
    llm_profile["api_key"] = _prompt(
        str(llm_profile.get("api_key") or ""), strings["init.api_key"], hide=True
    )
    llm_model["model"] = _prompt(
        str(llm_model.get("model") or "gpt-4o-mini"), strings["init.model"]
    )
    llm_model["name"] = llm_model["model"] or "Default Model"

    if typer.confirm(strings["init.confirm_embedding"], default=not cli_only):
        emb_profile, emb_model = _ensure_model_service(
            catalog,
            "embedding",
            "embedding-profile-default",
            "embedding-model-default",
        )
        typer.echo(f"\n{strings['init.embedding_section']}")
        emb_profile["binding"] = _prompt(
            str(emb_profile.get("binding") or "openai"), strings["init.binding"]
        )
        emb_profile["base_url"] = _prompt(
            str(emb_profile.get("base_url") or "https://api.openai.com/v1/embeddings"),
            strings["init.embedding_endpoint"],
        )
        emb_profile["api_key"] = _prompt(
            str(emb_profile.get("api_key") or ""),
            strings["init.embedding_api_key"],
            hide=True,
        )
        emb_model["model"] = _prompt(
            str(emb_model.get("model") or "text-embedding-3-large"),
            strings["init.embedding_model"],
        )
        emb_model["name"] = emb_model["model"] or "Default Embedding Model"
        emb_model["dimension"] = _prompt(
            str(emb_model.get("dimension") or ""), strings["init.embedding_dimension"]
        )

    catalog_service.save(catalog)
    typer.echo(f"\n{strings['init.saved']}")


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_command(
        cli: bool = typer.Option(False, "--cli", help="Initialize for CLI-only use."),
        home: Path | None = typer.Option(None, "--home", help="Runtime workspace root."),
    ) -> None:
        """Create or update data/user/settings for this workspace."""

        run_init(cli_only=cli, home=home)
