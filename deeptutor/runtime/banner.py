"""Branded banner + localized labels for ``deeptutor start`` / ``deeptutor init``.

Both commands read the user's language preference from
``data/user/settings/interface.json`` (default ``en``) so their startup
output matches the UI language the user has chosen.
"""

from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from deeptutor.__version__ import __version__

_ASCII_LOGO = r""" ____                  _____      _
|  _ \  ___  ___ _ __ |_   _|   _| |_ ___  _ __
| | | |/ _ \/ _ \ '_ \  | || | | | __/ _ \| '__|
| |_| |  __/  __/ |_) | | || |_| | || (_) | |
|____/ \___|\___| .__/  |_| \__,_|\__\___/|_|
                |_|"""


LABELS: dict[str, dict[str, str]] = {
    "en": {
        "tagline": "Agent-Native Personalized Tutoring",
        "lab": "Data Intelligence Lab @ HKU",
        # init
        "init.mode": "Workspace initializer",
        "init.workspace": "Workspace",
        "init.note_settings_dir": "Settings will be written under data/user/settings.",
        "init.backend_port": "Backend port",
        "init.frontend_port": "Frontend port",
        "init.llm_section": "LLM provider",
        "init.binding": "Binding",
        "init.base_url": "Base URL",
        "init.api_key": "API key",
        "init.model": "Model",
        "init.confirm_embedding": "Configure embedding for Knowledge Base/RAG now?",
        "init.embedding_section": "Embedding provider",
        "init.embedding_endpoint": "Embedding endpoint URL",
        "init.embedding_api_key": "Embedding API key",
        "init.embedding_model": "Embedding model",
        "init.embedding_dimension": "Embedding dimension (blank for auto)",
        "init.saved": "Settings saved. You can edit them later in the Web Settings page or data/user/settings/.",
        # start (launcher)
        "start.mode": "Launching backend + frontend",
        "start.backend": "Backend",
        "start.browser_api": "Browser API",
        "start.frontend": "Frontend",
        "start.workspace": "Workspace",
        "start.frontend_runtime": "Frontend runtime",
        "start.press_ctrl_c": "Press Ctrl+C to stop.",
        "start.starting_backend": "Starting backend ...",
        "start.starting_frontend": "Starting frontend ...",
        "start.waiting_for": "Waiting for {name} at {url} ...",
        "start.ready": "{name} is ready.",
        "start.open_in_browser": "Open {url} in your browser.",
        "start.received_signal": "Received {signal}; shutting down ...",
        "start.stopping": "Stopping {name} (PID {pid})",
        "start.exited": "{name} exited with code {code}",
        "start.not_ready": "{name} did not become ready within {timeout}s",
        "start.port_in_use": (
            "DeepTutor cannot start because port(s) already in use: {ports}. "
            "Stop the existing process or change data/user/settings/system.json."
        ),
    },
    "zh": {
        "tagline": "智能体原生的个性化辅导",
        "lab": "香港大学数据智能实验室",
        # init
        "init.mode": "工作目录初始化",
        "init.workspace": "工作目录",
        "init.note_settings_dir": "配置文件将写入 data/user/settings 目录。",
        "init.backend_port": "后端端口",
        "init.frontend_port": "前端端口",
        "init.llm_section": "大模型服务",
        "init.binding": "服务类型",
        "init.base_url": "Base URL",
        "init.api_key": "API Key",
        "init.model": "模型",
        "init.confirm_embedding": "现在配置知识库 / RAG 所用的向量模型?",
        "init.embedding_section": "向量模型服务",
        "init.embedding_endpoint": "向量服务地址",
        "init.embedding_api_key": "向量服务 API Key",
        "init.embedding_model": "向量模型",
        "init.embedding_dimension": "向量维度 (留空自动检测)",
        "init.saved": "配置已保存。后续可在 Web 设置页或 data/user/settings/ 中修改。",
        # start (launcher)
        "start.mode": "启动后端 + 前端",
        "start.backend": "后端",
        "start.browser_api": "前端 API",
        "start.frontend": "前端",
        "start.workspace": "工作目录",
        "start.frontend_runtime": "前端运行模式",
        "start.press_ctrl_c": "按 Ctrl+C 停止。",
        "start.starting_backend": "正在启动后端服务 ...",
        "start.starting_frontend": "正在启动前端服务 ...",
        "start.waiting_for": "正在等待 {name} ({url}) ...",
        "start.ready": "{name} 已就绪。",
        "start.open_in_browser": "请在浏览器中打开 {url}。",
        "start.received_signal": "收到 {signal} 信号,正在关闭 ...",
        "start.stopping": "正在停止 {name} (PID {pid})",
        "start.exited": "{name} 已退出 (退出码 {code})",
        "start.not_ready": "{name} 在 {timeout} 秒内未就绪",
        "start.port_in_use": (
            "无法启动 DeepTutor,端口已被占用: {ports}。"
            "请先停止占用进程,或修改 data/user/settings/system.json 中的端口设置。"
        ),
    },
}


def _pick_language(language: str | None) -> str:
    if not language:
        return "en"
    code = str(language).lower().strip()
    if code in {"zh", "zh-cn", "zh-hans", "chinese", "cn"}:
        return "zh"
    return "en"


def resolve_language(default: str = "en") -> str:
    """Read the saved UI language, falling back to ``default``.

    Safe to call before the runtime is fully initialized; any failure
    silently falls back to the default.
    """
    try:
        from deeptutor.services.settings.interface_settings import get_ui_language

        return _pick_language(get_ui_language(default))
    except Exception:
        return _pick_language(default)


def labels_for(language: str | None) -> dict[str, str]:
    return LABELS[_pick_language(language)]


def render_banner(language: str | None, *, mode_key: str | None = None) -> Panel:
    """Build the branded banner panel.

    Parameters
    ----------
    language:
        Language code (``"en"``/``"zh"``). Unknown values fall back to English.
    mode_key:
        Optional key into ``LABELS[lang]`` to display under the tagline
        (e.g. ``"start.mode"``, ``"init.mode"``).
    """

    lang = _pick_language(language)
    strings = LABELS[lang]

    logo = Text(_ASCII_LOGO, style="bold bright_cyan")
    tagline_line = f"{strings['tagline']}  ·  v{__version__}"

    body = Text()
    body.append(logo)
    body.append("\n\n")
    body.append(tagline_line, style="bold white")
    body.append("\n")
    body.append(strings["lab"], style="dim")
    if mode_key and mode_key in strings:
        body.append("\n")
        body.append(strings[mode_key], style="italic bright_magenta")

    return Panel(
        Align.left(body),
        title="[bold bright_cyan]DeepTutor[/]",
        border_style="bright_cyan",
        padding=(1, 2),
    )


def print_banner(
    console: Console | None = None,
    *,
    language: str | None = None,
    mode_key: str | None = None,
) -> None:
    """Print the branded banner to ``console`` (creates one if omitted)."""

    target = console or Console()
    target.print(render_banner(language, mode_key=mode_key))


__all__: tuple[str, ...] = (
    "LABELS",
    "labels_for",
    "print_banner",
    "render_banner",
    "resolve_language",
)
