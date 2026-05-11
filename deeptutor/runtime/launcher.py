"""Local Web launcher for the installed DeepTutor app."""

from __future__ import annotations

import atexit
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Callable
from urllib import error as urlerror
from urllib import request as urlrequest

from deeptutor.runtime.banner import labels_for, print_banner, resolve_language
from deeptutor.runtime.home import DEEPTUTOR_HOME_ENV, PACKAGE_ROOT, get_runtime_home

BACKEND_READY_TIMEOUT = 60
FRONTEND_READY_TIMEOUT = 120
KILL_SIGNAL = getattr(signal, "SIGKILL", signal.SIGTERM)
WEB_CACHE_DIR = Path("data") / "user" / "runtime" / "web"

# Mutable holder so module-level helpers can format messages in the active
# UI language without threading the labels through every function.
_ACTIVE_LABELS: dict[str, str] = labels_for("en")


def _t(key: str, **kwargs: object) -> str:
    template = _ACTIVE_LABELS.get(key) or labels_for("en").get(key, key)
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template


@dataclass(slots=True)
class ManagedProcess:
    name: str
    process: subprocess.Popen[str]
    pgid: int | None


@dataclass(frozen=True, slots=True)
class FrontendRuntime:
    kind: str
    command: list[str]
    cwd: Path


def _log(message: str) -> None:
    print(message, flush=True)


def _reset_runtime_singletons() -> None:
    """Make a just-selected DEEPTUTOR_HOME visible to path/config singletons."""
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


def _get_pgid(pid: int | None) -> int | None:
    if pid is None or os.name == "nt":
        return None
    try:
        return os.getpgid(pid)
    except OSError:
        return None


def _is_pid_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _send_tree_signal(pid: int | None, pgid: int | None, sig: signal.Signals | int) -> None:
    if pid is None:
        return
    if os.name == "nt":
        cmd = ["taskkill", "/PID", str(pid), "/T"]
        if sig == KILL_SIGNAL:
            cmd.append("/F")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return
    if os.name != "nt" and pgid is not None:
        os.killpg(pgid, sig)
    else:
        os.kill(pid, sig)


def _terminate(proc: ManagedProcess | None) -> None:
    if proc is None or proc.process.poll() is not None:
        return
    _log(_t("start.stopping", name=proc.name, pid=proc.process.pid))
    try:
        _send_tree_signal(proc.process.pid, proc.pgid, signal.SIGTERM)
    except Exception:
        pass
    try:
        proc.process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            _send_tree_signal(proc.process.pid, proc.pgid, KILL_SIGNAL)
        except Exception:
            pass


def _stream_output(prefix: str, process: subprocess.Popen[str]) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        print(f"  {prefix:<8} {line.rstrip()}", flush=True)


def _spawn(command: list[str], *, cwd: Path, env: dict[str, str], name: str) -> ManagedProcess:
    kwargs: dict[str, object] = {
        "cwd": str(cwd),
        "env": env,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "bufsize": 1,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)  # type: ignore[arg-type,call-overload]
    thread = threading.Thread(target=_stream_output, args=(name, process), daemon=True)
    thread.start()
    return ManagedProcess(name=name, process=process, pgid=_get_pgid(process.pid))


def _port_accepts_connection(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def _ensure_ports_available(*ports: int) -> None:
    occupied = [port for port in ports if _port_accepts_connection(port)]
    if occupied:
        joined = ", ".join(str(port) for port in occupied)
        raise SystemExit(_t("start.port_in_use", ports=joined))


def _wait_for_http(
    *,
    name: str,
    url: str,
    process: ManagedProcess,
    timeout: int,
    should_stop: Callable[[], bool],
) -> None:
    _log(_t("start.waiting_for", name=name, url=url))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if should_stop():
            return
        if process.process.poll() is not None:
            raise RuntimeError(_t("start.exited", name=name, code=process.process.returncode))
        try:
            with urlrequest.urlopen(url, timeout=1):  # noqa: S310  # nosec B310 - http(s) health-check URL constructed by caller
                _log(_t("start.ready", name=name))
                return
        except (urlerror.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    raise RuntimeError(_t("start.not_ready", name=name, timeout=timeout))


def _packaged_web_dir() -> Path | None:
    try:
        import deeptutor_web
    except ImportError:
        return None
    path = Path(deeptutor_web.__file__).resolve().parent
    return path if (path / "server.js").exists() else None


def _copy_packaged_web_if_needed(
    packaged: Path,
    *,
    home: Path,
    api_base: str,
    auth_enabled: bool,
) -> Path:
    """Copy packaged Next.js standalone files into a writable runtime cache.

    Next public variables are inlined at build time, so placeholders must be
    replaced before ``server.js`` starts. The installed package may live in a
    read-only site-packages directory; the cache keeps mutation local to the
    active workspace.
    """

    cache = home / WEB_CACHE_DIR
    marker = cache / ".deeptutor-web-runtime.json"
    source_server = packaged / "server.js"
    marker_payload = {
        "source": str(packaged),
        "source_mtime_ns": source_server.stat().st_mtime_ns,
        "api_base": api_base,
        "auth_enabled": bool(auth_enabled),
    }
    if (cache / "server.js").exists():
        try:
            if json.loads(marker.read_text(encoding="utf-8")) == marker_payload:
                return cache
        except Exception:
            pass

    if cache.exists():
        shutil.rmtree(cache)
    shutil.copytree(packaged, cache)
    _patch_packaged_web_placeholders(
        cache,
        api_base=api_base,
        auth_enabled="true" if auth_enabled else "false",
    )
    marker.write_text(json.dumps(marker_payload, indent=2), encoding="utf-8")
    return cache


def _patch_packaged_web_placeholders(
    web_dir: Path,
    *,
    api_base: str,
    auth_enabled: str,
) -> None:
    replacements = {
        "__NEXT_PUBLIC_API_BASE_PLACEHOLDER__": api_base,
        "__NEXT_PUBLIC_AUTH_ENABLED_PLACEHOLDER__": auth_enabled,
    }
    roots = [web_dir / ".next", web_dir / "server.js"]
    for root in roots:
        paths = [root] if root.is_file() else root.rglob("*") if root.exists() else []
        for path in paths:
            if not path.is_file() or path.suffix not in {".js", ".json", ".html", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            updated = text
            for placeholder, value in replacements.items():
                updated = updated.replace(placeholder, value)
            if updated != text:
                path.write_text(updated, encoding="utf-8")


def _source_web_dir(home: Path) -> Path | None:
    candidates = [home / "web", PACKAGE_ROOT / "web"]
    for path in candidates:
        if (path / "package.json").exists():
            return path
    return None


def _resolve_frontend(
    home: Path,
    frontend_port: int,
    *,
    api_base: str,
    auth_enabled: bool,
) -> FrontendRuntime:
    packaged = _packaged_web_dir()
    node = shutil.which("node")
    if packaged is not None:
        if not node:
            raise SystemExit("Node.js 20+ is required to run the packaged DeepTutor Web app.")
        runtime_web = _copy_packaged_web_if_needed(
            packaged,
            home=home,
            api_base=api_base,
            auth_enabled=auth_enabled,
        )
        return FrontendRuntime("packaged", [node, str(runtime_web / "server.js")], runtime_web)

    source = _source_web_dir(home)
    if source is not None:
        npm = shutil.which("npm")
        if not npm:
            raise SystemExit(
                "npm not found. Source installs require Node.js/npm and `cd web && npm install`."
            )
        return FrontendRuntime(
            "source", [npm, "run", "dev", "--", "--port", str(frontend_port)], source
        )

    raise SystemExit(
        "DeepTutor Web assets are not installed. Install the full app with `pip install -U deeptutor`, "
        "or run from a source checkout that contains `web/`."
    )


def _install_signal_handlers(request_shutdown: Callable[[str | None], None]) -> None:
    def _handler(signum: int, _frame) -> None:
        try:
            signal_name = signal.Signals(signum).name
        except ValueError:
            signal_name = str(signum)
        request_shutdown(signal_name)

    for sig_name in ("SIGINT", "SIGTERM", "SIGHUP", "SIGBREAK"):
        sig = getattr(signal, sig_name, None)
        if sig is None:
            continue
        try:
            signal.signal(sig, _handler)
        except (OSError, ValueError):
            continue


def start(home: str | Path | None = None) -> None:
    runtime_home = get_runtime_home(home)
    runtime_home.mkdir(parents=True, exist_ok=True)
    os.environ[DEEPTUTOR_HOME_ENV] = str(runtime_home)
    _reset_runtime_singletons()

    from deeptutor.services.config import (
        ensure_runtime_settings_files,
        export_runtime_settings_to_env,
        load_auth_settings,
        load_launch_settings,
    )
    from deeptutor.services.setup import init_user_directories

    init_user_directories(runtime_home)
    ensure_runtime_settings_files()
    settings = load_launch_settings(runtime_home)
    runtime_env = export_runtime_settings_to_env(overwrite=True)
    auth_enabled = bool(load_auth_settings()["enabled"])

    global _ACTIVE_LABELS
    language = resolve_language()
    _ACTIVE_LABELS = labels_for(language)

    backend_port = settings.backend_port
    frontend_port = settings.frontend_port
    backend_url = f"http://localhost:{backend_port}"
    api_base = (
        runtime_env.get("NEXT_PUBLIC_API_BASE_EXTERNAL")
        or runtime_env.get("NEXT_PUBLIC_API_BASE")
        or backend_url
    )
    frontend = _resolve_frontend(
        runtime_home,
        frontend_port,
        api_base=api_base,
        auth_enabled=auth_enabled,
    )

    print_banner(language=language, mode_key="start.mode")
    _log(f"{_t('start.backend'):<10} {backend_url}")
    if api_base != backend_url:
        _log(f"{_t('start.browser_api'):<10} {api_base}")
    _log(f"{_t('start.frontend'):<10} http://localhost:{frontend_port}")
    _log(f"{_t('start.workspace'):<10} {runtime_home}")
    _log(f"{_t('start.frontend_runtime')}: {frontend.kind}")
    _log(_t("start.press_ctrl_c"))

    _ensure_ports_available(backend_port, frontend_port)

    common_env = os.environ.copy()
    common_env.update(runtime_env)
    common_env[DEEPTUTOR_HOME_ENV] = str(runtime_home)
    common_env["BACKEND_PORT"] = str(backend_port)
    common_env["FRONTEND_PORT"] = str(frontend_port)
    common_env["PORT"] = str(frontend_port)
    common_env["HOSTNAME"] = "0.0.0.0"
    common_env["NEXT_PUBLIC_API_BASE"] = api_base
    common_env["NEXT_PUBLIC_AUTH_ENABLED"] = "true" if auth_enabled else "false"
    common_env["PYTHONUNBUFFERED"] = "1"
    common_env["PYTHONIOENCODING"] = "utf-8:replace"

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "deeptutor.api.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(backend_port),
        "--log-level",
        "info",
    ]

    processes: list[ManagedProcess] = []
    backend: ManagedProcess | None = None
    web: ManagedProcess | None = None
    shutdown_requested = False
    cleanup_started = False
    exit_code = 0

    def request_shutdown(signal_name: str | None = None) -> None:
        nonlocal shutdown_requested
        if shutdown_requested:
            return
        shutdown_requested = True
        if signal_name:
            _log(_t("start.received_signal", signal=signal_name))

    def cleanup() -> None:
        nonlocal cleanup_started
        if cleanup_started:
            return
        cleanup_started = True
        _terminate(web)
        _terminate(backend)

    _install_signal_handlers(request_shutdown)
    atexit.register(cleanup)

    try:
        _log(_t("start.starting_backend"))
        backend = _spawn(backend_cmd, cwd=runtime_home, env=common_env, name="backend")
        processes.append(backend)
        _wait_for_http(
            name=_t("start.backend"),
            url=f"http://127.0.0.1:{backend_port}/",
            process=backend,
            timeout=BACKEND_READY_TIMEOUT,
            should_stop=lambda: shutdown_requested,
        )

        _log(_t("start.starting_frontend"))
        web = _spawn(frontend.command, cwd=frontend.cwd, env=common_env, name="frontend")
        processes.append(web)
        _wait_for_http(
            name=_t("start.frontend"),
            url=f"http://127.0.0.1:{frontend_port}/",
            process=web,
            timeout=FRONTEND_READY_TIMEOUT,
            should_stop=lambda: shutdown_requested,
        )
        _log(_t("start.open_in_browser", url=f"http://localhost:{frontend_port}"))

        while not shutdown_requested:
            for proc in processes:
                if proc.process.poll() is not None:
                    _log(_t("start.exited", name=proc.name, code=proc.process.returncode))
                    exit_code = 1
                    shutdown_requested = True
                    break
            time.sleep(1)
    except KeyboardInterrupt:
        request_shutdown("SIGINT")
    finally:
        cleanup()

    if exit_code:
        raise SystemExit(exit_code)


__all__ = ["start"]
