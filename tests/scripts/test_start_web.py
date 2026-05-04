from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types


def _load_start_web_module():
    project_root = Path(__file__).resolve().parents[2]
    scripts_dir = project_root / "scripts"
    module_path = scripts_dir / "start_web.py"
    sys.path.insert(0, str(scripts_dir))
    try:
        spec = importlib.util.spec_from_file_location("start_web_under_test", module_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop("start_web_under_test", None)
        try:
            sys.path.remove(str(scripts_dir))
        except ValueError:
            pass


def test_start_web_translation_uses_interface_language() -> None:
    start_web = _load_start_web_module()

    assert start_web._t("zh", "backend") == "后端"
    assert start_web._t("en", "frontend") == "Frontend"


def test_state_round_trip(tmp_path: Path) -> None:
    start_web = _load_start_web_module()
    state_path = tmp_path / "start_web_state.json"
    fake_process = types.SimpleNamespace(pid=12345)
    managed = start_web.ManagedProcess(name="backend", process=fake_process, pgid=67890)

    start_web._write_state(
        [managed],
        backend_port=8101,
        frontend_port=4100,
        path=state_path,
    )

    state = start_web._read_state(state_path)
    assert state["backend_port"] == 8101
    assert state["frontend_port"] == 4100
    assert state["processes"]["backend"]["pid"] == 12345
    assert state["processes"]["backend"]["pgid"] == 67890


def test_conflict_matches_recorded_state_by_pid() -> None:
    start_web = _load_start_web_module()
    state = {"processes": {"backend": {"pid": 12345, "pgid": None}}}
    conflict = start_web.PortConflict(
        name="Backend",
        port=8101,
        owners=[start_web.PortOwner(command="python", pid=12345)],
    )

    assert start_web._conflicts_match_state([conflict], state) is True
