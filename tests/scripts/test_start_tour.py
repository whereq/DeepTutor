from __future__ import annotations

import importlib.util
import locale
from pathlib import Path
import sys
import types


def _load_start_tour_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "start_tour.py"

    cli_kit = types.ModuleType("_cli_kit")
    for name in (
        "accent",
        "banner",
        "bold",
        "confirm",
        "countdown",
        "dim",
        "log_error",
        "log_info",
        "log_success",
        "log_warn",
        "select",
        "step",
        "text_input",
    ):
        setattr(cli_kit, name, lambda *args, **kwargs: None)

    deeptutor_pkg = types.ModuleType("deeptutor")
    services_pkg = types.ModuleType("deeptutor.services")
    config_module = types.ModuleType("deeptutor.services.config")
    config_module.get_config_test_runner = lambda: None
    config_module.get_env_store = lambda: None
    config_module.get_model_catalog_service = lambda: None

    original_modules = {
        "_cli_kit": sys.modules.get("_cli_kit"),
        "deeptutor": sys.modules.get("deeptutor"),
        "deeptutor.services": sys.modules.get("deeptutor.services"),
        "deeptutor.services.config": sys.modules.get("deeptutor.services.config"),
    }

    services_pkg.config = config_module
    deeptutor_pkg.services = services_pkg
    sys.modules["_cli_kit"] = cli_kit
    sys.modules["deeptutor"] = deeptutor_pkg
    sys.modules["deeptutor.services"] = services_pkg
    sys.modules["deeptutor.services.config"] = config_module

    try:
        spec = importlib.util.spec_from_file_location("start_tour_under_test", module_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for module_name, original_module in original_modules.items():
            if original_module is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = original_module


def test_stream_text_kwargs_use_best_effort_decoding() -> None:
    start_tour = _load_start_tour_module()

    kwargs = start_tour._stream_text_kwargs()

    assert kwargs["text"] is True
    assert kwargs["errors"] == "replace"
    assert kwargs["encoding"] == locale.getpreferredencoding(False)
