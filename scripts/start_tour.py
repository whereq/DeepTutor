#!/usr/bin/env python
"""DeepTutor Setup Tour - simplified CLI configuration wizard."""

from __future__ import annotations

import json
import locale
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"
INTERFACE_SETTINGS_PATH = PROJECT_ROOT / "data" / "user" / "settings" / "interface.json"
LEGACY_TOUR_CACHE_PATH = PROJECT_ROOT / "data" / "user" / "settings" / ".tour_cache.json"


def _resolve_python() -> str:
    """Return a validated path to the current Python interpreter."""
    exe = sys.executable
    if exe:
        if Path(exe).exists():
            return exe
        resolved = str(Path(exe).resolve())
        if Path(resolved).exists():
            return resolved
    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found
    return exe or "python3"


_PYTHON: str = _resolve_python()

_BOOTSTRAP_PACKAGES = [
    ("yaml", "PyYAML>=6.0"),
]


def _can_import(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False



def _bootstrap() -> None:
    missing = [pip for imp, pip in _BOOTSTRAP_PACKAGES if not _can_import(imp)]
    if not missing:
        return
    print(f"  Installing bootstrap dependencies: {', '.join(missing)} ...")
    subprocess.check_call(
        [_PYTHON, "-m", "pip", "install", *missing, "-q"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


_bootstrap()



def _load_runtime_deps():
    from _cli_kit import (
        accent,
        banner,
        bold,
        confirm,
        countdown,
        dim,
        log_error,
        log_info,
        log_success,
        log_warn,
        select,
        step,
        text_input,
    )

    from deeptutor.services.config import get_env_store

    return (
        accent,
        banner,
        bold,
        confirm,
        countdown,
        dim,
        log_error,
        log_info,
        log_success,
        log_warn,
        select,
        step,
        text_input,
        get_env_store,
    )


(
    accent,
    banner,
    bold,
    confirm,
    countdown,
    dim,
    log_error,
    log_info,
    log_success,
    log_warn,
    select,
    step,
    text_input,
    get_env_store,
) = _load_runtime_deps()

# ---------------------------------------------------------------------------
# Legacy install helpers kept for compatibility and tests
# ---------------------------------------------------------------------------

PROFILE_COMMANDS: dict[str, list[str]] = {
    "cli-core": ["requirements/cli.txt"],
    "cli-rag": ["requirements/cli.txt"],
    "web-basic": ["requirements/server.txt"],
    "web-rag": ["requirements/server.txt"],
}

PROFILE_ALIASES: dict[str, str] = {
    "cli-rag-lite": "cli-rag",
    "cli-rag-full": "cli-rag",
    "web-rag-lite": "web-rag",
    "web-rag-full": "web-rag",
}

MATH_ANIMATOR_REQUIREMENTS = "requirements/math-animator.txt"


MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "banner_line_1": "Configure DeepTutor from the terminal.",
        "banner_line_2": "We will write ports and provider settings directly into .env.",
        "env_created": "Created `.env` from `.env.example`.",
        "env_exists": "Using existing `.env` file.",
        "env_missing_template": "`.env.example` was not found. Creating an empty `.env` instead.",
        "platform": "Platform",
        "python": "Python",
        "node": "Node",
        "env_path": ".env",
        "language_step": "Choose language",
        "language_prompt": "Choose your language",
        "language_en_desc": "Run the setup wizard in English",
        "language_zh_desc": "Run the setup wizard in Chinese",
        "language_saved": "Saved interface language to `{path}`.",
        "ports_step": "Configure ports",
        "backend_port": "Backend port",
        "frontend_port": "Frontend port",
        "llm_step": "Configure LLM",
        "embedding_step": "Configure embedding",
        "search_step": "Configure search",
        "review_step": "Write configuration",
        "provider_prompt": "Choose a provider",
        "search_provider_prompt": "Choose a search provider",
        "profile_binding": "Provider / binding",
        "base_url": "Base URL",
        "api_key": "API key",
        "api_version": "API version",
        "model_id": "Model ID",
        "dimension": "Dimension",
        "send_dimensions": "Send `dimensions` parameter",
        "send_dimensions_auto": "auto",
        "send_dimensions_yes": "yes",
        "send_dimensions_no": "no",
        "search_enable": "Configure web search?",
        "search_base_url": "Search base URL",
        "search_proxy": "Search proxy",
        "keep_secret": "Press Enter to keep the existing secret value.",
        "optional": "Optional",
        "none": "None",
        "write_confirm": "Write these settings into `.env` now?",
        "write_success": "Updated `.env` successfully.",
        "no_changes": "No files changed.",
        "next_steps": "Setup complete. You can now start DeepTutor with:",
        "next_command": "python scripts/start_web.py",
        "summary_ports": "Ports",
        "summary_llm": "LLM",
        "summary_embedding": "Embedding",
        "summary_search": "Search",
        "search_disabled": "disabled",
        "tour_cache_removed": "Removed legacy setup-tour cache.",
        "interrupt": "Setup interrupted.",
        "manual_desc": "Enter a custom provider name",
        "custom_desc": "Any OpenAI-compatible endpoint",
        "local_desc": "Local model endpoint",
        "search_none_desc": "Disable web search integration",
        "search_proxy_placeholder": "http://127.0.0.1:7890",
        "searxng_default": "http://localhost:8080",
    },
    "zh": {
        "banner_line_1": "在命令行中完成 DeepTutor 配置。",
        "banner_line_2": "我们会把端口和提供商配置直接写入 .env。",
        "env_created": "已根据 `.env.example` 创建 `.env`。",
        "env_exists": "检测到现有 `.env` 文件。",
        "env_missing_template": "未找到 `.env.example`，将创建一个空的 `.env`。",
        "platform": "平台",
        "python": "Python",
        "node": "Node",
        "env_path": ".env",
        "language_step": "选择语言",
        "language_prompt": "选择界面语言",
        "language_en_desc": "使用英文完成配置",
        "language_zh_desc": "使用中文完成配置",
        "language_saved": "已将界面语言写入 `{path}`。",
        "ports_step": "配置端口",
        "backend_port": "后端端口",
        "frontend_port": "前端端口",
        "llm_step": "配置 LLM",
        "embedding_step": "配置 Embedding",
        "search_step": "配置 Search",
        "review_step": "写入配置",
        "provider_prompt": "选择提供商",
        "search_provider_prompt": "选择搜索提供商",
        "profile_binding": "提供商 / 绑定",
        "base_url": "Base URL",
        "api_key": "API Key",
        "api_version": "API 版本",
        "model_id": "模型 ID",
        "dimension": "维度",
        "send_dimensions": "是否发送 `dimensions` 参数",
        "send_dimensions_auto": "自动",
        "send_dimensions_yes": "是",
        "send_dimensions_no": "否",
        "search_enable": "是否配置联网搜索？",
        "search_base_url": "搜索服务 Base URL",
        "search_proxy": "搜索代理",
        "keep_secret": "直接回车即可保留当前密钥。",
        "optional": "可选",
        "none": "不配置",
        "write_confirm": "现在将这些设置写入 `.env` 吗？",
        "write_success": "已成功更新 `.env`。",
        "no_changes": "未修改任何文件。",
        "next_steps": "配置完成。你现在可以用下面的命令启动 DeepTutor：",
        "next_command": "python scripts/start_web.py",
        "summary_ports": "端口",
        "summary_llm": "LLM",
        "summary_embedding": "Embedding",
        "summary_search": "Search",
        "search_disabled": "未启用",
        "tour_cache_removed": "已移除旧版 setup-tour 缓存。",
        "interrupt": "配置已中断。",
        "manual_desc": "手动输入自定义提供商名称",
        "custom_desc": "任意兼容 OpenAI 的接口",
        "local_desc": "本地模型服务",
        "search_none_desc": "关闭联网搜索集成",
        "search_proxy_placeholder": "http://127.0.0.1:7890",
        "searxng_default": "http://localhost:8080",
    },
}

_LANG = "en"

LLM_MODEL_SUGGESTIONS = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "dashscope": "qwen-max",
    "gemini": "gemini-2.5-flash",
    "groq": "llama-3.3-70b-versatile",
    "zhipu": "glm-4.5",
    "ollama": "qwen3:8b",
    "vllm": "Qwen/Qwen3-8B",
}

EMBEDDING_MODEL_SUGGESTIONS = {
    "openai": "text-embedding-3-large",
    "cohere": "embed-v4.0",
    "jina": "jina-embeddings-v3",
    "ollama": "nomic-embed-text",
}

SEARCH_PROVIDERS = (
    ("none", "None", "Disable web search integration"),
    ("brave", "Brave", "API key required"),
    ("tavily", "Tavily", "API key required"),
    ("jina", "Jina", "API key required"),
    ("searxng", "SearXNG", "Self-hosted or public instance"),
    ("duckduckgo", "DuckDuckGo", "No API key required"),
    ("perplexity", "Perplexity", "API key required"),
)


# ---------------------------------------------------------------------------
# Compatibility helpers
# ---------------------------------------------------------------------------


def _node_strategy() -> str:
    if shutil.which("node") and shutil.which("npm"):
        return "installed"
    system = platform.system().lower()
    if system == "darwin":
        return "brew"
    if system == "windows":
        return "winget"
    for pm in ("apt", "dnf", "yum"):
        if shutil.which(pm):
            return pm
    return "manual"



def _get_npm_command() -> str:
    if platform.system().lower() == "windows":
        return "npm.cmd"
    npm = shutil.which("npm")
    if npm:
        return npm
    return "npm"



def _install_commands(
    profile: str,
    catalog: dict[str, Any],
    *,
    include_math_animator: bool = False,
) -> list[tuple[list[str], Path]]:
    del catalog
    profile = PROFILE_ALIASES.get(profile, profile)
    if profile not in PROFILE_COMMANDS:
        raise ValueError(f"Unknown install profile: {profile}")

    cmds: list[tuple[list[str], Path]] = []
    for req in PROFILE_COMMANDS[profile]:
        cmds.append(([_PYTHON, "-m", "pip", "install", "-r", req], PROJECT_ROOT))
    if include_math_animator:
        cmds.append(
            ([_PYTHON, "-m", "pip", "install", "-r", MATH_ANIMATOR_REQUIREMENTS], PROJECT_ROOT)
        )
    cmds.append(([_PYTHON, "-m", "pip", "install", "-e", ".", "--no-deps"], PROJECT_ROOT))
    if profile.startswith("web"):
        cmds.append(([_get_npm_command(), "install"], PROJECT_ROOT / "web"))
    return cmds



def _run_cmd(cmd: list[str], cwd: Path) -> None:
    log_info(f"{dim(str(cwd))}  {' '.join(cmd)}")
    use_shell = platform.system().lower() == "windows"
    result = subprocess.run(cmd, cwd=str(cwd), check=False, shell=use_shell)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed (exit {result.returncode}): {' '.join(cmd)}")



def _stream_text_kwargs() -> dict[str, object]:
    """Best-effort text decoding for subprocess output."""
    encoding = locale.getpreferredencoding(False) or "utf-8"
    return {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": encoding,
        "errors": "replace",
        "bufsize": 1,
    }


# ---------------------------------------------------------------------------
# Localized prompt helpers
# ---------------------------------------------------------------------------


def _set_language(language: str) -> None:
    global _LANG
    _LANG = "zh" if str(language).strip().lower().startswith("zh") else "en"



def _t(key: str, **kwargs: Any) -> str:
    template = MESSAGES[_LANG].get(key, MESSAGES["en"].get(key, key))
    return template.format(**kwargs)



def _secret_mask(value: str) -> str:
    if not value:
        return "-"
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"



def _save_ui_language(language: str, path: Path = INTERFACE_SETTINGS_PATH) -> None:
    payload: dict[str, Any] = {"theme": "light", "language": language}
    if path.exists():
        try:
            payload.update(json.loads(path.read_text(encoding="utf-8")) or {})
        except Exception:
            pass
    payload["language"] = "zh" if language == "zh" else "en"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")



def _ensure_env_file(env_path: Path = ENV_PATH, template_path: Path = ENV_EXAMPLE_PATH) -> bool:
    if env_path.exists():
        return False
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if template_path.exists():
        shutil.copyfile(template_path, env_path)
        return True
    env_path.write_text("", encoding="utf-8")
    return True



def _cleanup_legacy_tour_cache(path: Path = LEGACY_TOUR_CACHE_PATH) -> bool:
    if not path.exists():
        return False
    path.unlink(missing_ok=True)
    return True



def _prompt_int(prompt: str, default: int) -> int:
    while True:
        value = text_input(prompt, str(default)).strip()
        try:
            return int(value)
        except ValueError:
            log_warn(f"{prompt}: {value!r} is not a valid integer.")



def _prompt_secret(prompt: str, default: str) -> str:
    if default:
        log_info(dim(_t("keep_secret")))
    return text_input(prompt, default, secret=True)



def _enum_options(options: list[tuple[str, str, str]], current: str | None = None) -> list[tuple[str, str, str]]:
    normalized_current = str(current or "").strip()
    if not normalized_current:
        return options
    seen = {value for value, _, _ in options}
    if normalized_current in seen:
        return options
    current_label = normalized_current
    current_desc = "current value" if _LANG == "en" else "当前值"
    return [(normalized_current, current_label, current_desc)] + options



def _load_provider_metadata():
    from deeptutor.services.config.provider_runtime import EMBEDDING_PROVIDERS
    from deeptutor.services.provider_registry import find_by_name

    return EMBEDDING_PROVIDERS, find_by_name



def _llm_provider_options(current: str | None) -> list[tuple[str, str, str]]:
    _, find_by_name = _load_provider_metadata()
    common = [
        "openai",
        "anthropic",
        "deepseek",
        "gemini",
        "dashscope",
        "zhipu",
        "groq",
        "ollama",
        "lm_studio",
        "azure_openai",
        "custom",
    ]
    options: list[tuple[str, str, str]] = []
    for name in common:
        spec = find_by_name(name)
        label = spec.label if spec else name
        if name == "custom":
            desc = _t("custom_desc")
        elif spec and spec.is_local:
            desc = _t("local_desc")
        else:
            desc = spec.default_api_base if spec and spec.default_api_base else ""
        options.append((name, label, desc))
    return _enum_options(options, current)



def _embedding_provider_options(current: str | None) -> list[tuple[str, str, str]]:
    embedding_providers, _ = _load_provider_metadata()
    common = ["openai", "jina", "cohere", "ollama", "vllm", "azure_openai", "custom"]
    options: list[tuple[str, str, str]] = []
    for name in common:
        spec = embedding_providers.get(name)
        label = spec.label if spec else name
        if name == "custom":
            desc = _t("custom_desc")
        elif spec and spec.is_local:
            desc = _t("local_desc")
        else:
            desc = spec.default_api_base if spec and spec.default_api_base else ""
        options.append((name, label, desc))
    return _enum_options(options, current)



def _search_provider_options(current: str | None) -> list[tuple[str, str, str]]:
    options = [
        (value, label, _t("search_none_desc") if value == "none" else desc)
        for value, label, desc in SEARCH_PROVIDERS
    ]
    return _enum_options(options, current)



def _default_base_url(binding: str, current_binding: str, current_value: str, fallback: str = "") -> str:
    if current_value and binding == current_binding:
        return current_value
    embedding_providers, find_by_name = _load_provider_metadata()
    if binding in embedding_providers:
        return embedding_providers[binding].default_api_base or fallback
    spec = find_by_name(binding)
    if spec and spec.default_api_base:
        return spec.default_api_base
    return fallback



def _default_llm_model(binding: str, current_binding: str, current_model: str) -> str:
    if current_model and binding == current_binding:
        return current_model
    return LLM_MODEL_SUGGESTIONS.get(binding, current_model)



def _default_embedding_model(binding: str, current_binding: str, current_model: str) -> str:
    if current_model and binding == current_binding:
        return current_model
    embedding_providers, _ = _load_provider_metadata()
    spec = embedding_providers.get(binding)
    if spec and spec.default_model:
        return spec.default_model
    return EMBEDDING_MODEL_SUGGESTIONS.get(binding, current_model)



def _default_embedding_dimension(binding: str, current_binding: str, current_value: str) -> str:
    if current_value and binding == current_binding:
        return current_value
    embedding_providers, _ = _load_provider_metadata()
    spec = embedding_providers.get(binding)
    if spec and spec.default_dim:
        return str(spec.default_dim)
    return current_value or "3072"



def _send_dimensions_choice(current_value: str) -> str:
    normalized = str(current_value or "").strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        default = "true"
    elif normalized in {"false", "0", "no", "off"}:
        default = "false"
    else:
        default = "auto"
    return select(
        _t("send_dimensions"),
        [
            ("auto", _t("send_dimensions_auto"), ""),
            ("true", _t("send_dimensions_yes"), ""),
            ("false", _t("send_dimensions_no"), ""),
        ],
    ) or default


# ---------------------------------------------------------------------------
# Wizard steps
# ---------------------------------------------------------------------------


def _choose_language() -> str:
    step(1, 6, "Language")
    language = select(
        "Choose language / 选择语言",
        [
            ("en", "English", "Run the setup wizard in English"),
            ("zh", "中文", "使用中文完成配置"),
        ],
    )
    _set_language(language)
    _save_ui_language(language)
    log_success(_t("language_saved", path=INTERFACE_SETTINGS_PATH.relative_to(PROJECT_ROOT)))
    print()
    return language



def _configure_ports() -> dict[str, str]:
    step(2, 6, _t("ports_step"))
    summary = get_env_store().as_summary()
    backend_port = _prompt_int(_t("backend_port"), summary.backend_port)
    frontend_port = _prompt_int(_t("frontend_port"), summary.frontend_port)
    print()
    return {
        "BACKEND_PORT": str(backend_port),
        "FRONTEND_PORT": str(frontend_port),
    }



def _configure_llm() -> dict[str, str]:
    step(3, 6, _t("llm_step"))
    summary = get_env_store().as_summary()
    current_binding = summary.llm["binding"] or "openai"
    binding = select(_t("provider_prompt"), _llm_provider_options(current_binding))
    base_url = text_input(
        _t("base_url"),
        _default_base_url(binding, current_binding, summary.llm["host"]),
    )
    api_key = _prompt_secret(_t("api_key"), summary.llm["api_key"])
    model_id = text_input(
        _t("model_id"),
        _default_llm_model(binding, current_binding, summary.llm["model"]),
    )
    api_version_default = summary.llm["api_version"] if binding == current_binding else ""
    api_version = text_input(_t("api_version"), api_version_default)
    print()
    return {
        "LLM_BINDING": binding,
        "LLM_HOST": base_url,
        "LLM_API_KEY": api_key,
        "LLM_MODEL": model_id,
        "LLM_API_VERSION": api_version,
    }



def _configure_embedding() -> dict[str, str]:
    step(4, 6, _t("embedding_step"))
    summary = get_env_store().as_summary()
    current_binding = summary.embedding["binding"] or "openai"
    binding = select(_t("provider_prompt"), _embedding_provider_options(current_binding))
    base_url = text_input(
        _t("base_url"),
        _default_base_url(binding, current_binding, summary.embedding["host"]),
    )
    api_key = _prompt_secret(_t("api_key"), summary.embedding["api_key"])
    model_id = text_input(
        _t("model_id"),
        _default_embedding_model(binding, current_binding, summary.embedding["model"]),
    )
    dimension = text_input(
        _t("dimension"),
        _default_embedding_dimension(binding, current_binding, summary.embedding["dimension"]),
    )
    send_dimensions = _send_dimensions_choice(summary.embedding["send_dimensions"])
    api_version_default = summary.embedding["api_version"] if binding == current_binding else ""
    api_version = text_input(_t("api_version"), api_version_default)
    print()
    return {
        "EMBEDDING_BINDING": binding,
        "EMBEDDING_HOST": base_url,
        "EMBEDDING_API_KEY": api_key,
        "EMBEDDING_MODEL": model_id,
        "EMBEDDING_DIMENSION": dimension,
        "EMBEDDING_SEND_DIMENSIONS": "" if send_dimensions == "auto" else send_dimensions,
        "EMBEDDING_API_VERSION": api_version,
    }



def _configure_search() -> dict[str, str]:
    step(5, 6, _t("search_step"))
    summary = get_env_store().as_summary()
    current_provider = summary.search["provider"] or "none"
    provider = select(_t("search_provider_prompt"), _search_provider_options(current_provider))

    if provider == "none":
        print()
        return {
            "SEARCH_PROVIDER": "",
            "SEARCH_API_KEY": "",
            "SEARCH_BASE_URL": "",
            "SEARCH_PROXY": "",
        }

    base_url_default = summary.search["base_url"] if provider == current_provider else ""
    if provider == "searxng" and not base_url_default:
        base_url_default = _t("searxng_default")
    api_key_default = summary.search["api_key"] if provider == current_provider else ""
    proxy_default = summary.search["proxy"] if provider == current_provider else ""

    base_url = base_url_default
    if provider == "searxng" or base_url_default:
        base_url = text_input(_t("search_base_url"), base_url_default)

    api_key = ""
    if provider in {"brave", "tavily", "jina", "perplexity"} or api_key_default:
        api_key = _prompt_secret(_t("api_key"), api_key_default)

    proxy = text_input(_t("search_proxy"), proxy_default or _t("search_proxy_placeholder"))
    if proxy == _t("search_proxy_placeholder") and not proxy_default:
        proxy = ""

    print()
    return {
        "SEARCH_PROVIDER": provider,
        "SEARCH_API_KEY": api_key,
        "SEARCH_BASE_URL": base_url,
        "SEARCH_PROXY": proxy,
    }



def _print_review(values: dict[str, str]) -> None:
    step(6, 6, _t("review_step"))
    log_info(
        f"{_t('summary_ports')}  {bold(values['BACKEND_PORT'])} / {bold(values['FRONTEND_PORT'])}"
    )
    log_info(
        "{}  {}  {}  {}".format(
            _t("summary_llm"),
            bold(values["LLM_BINDING"] or "-"),
            dim(values["LLM_MODEL"] or "-"),
            dim(values["LLM_HOST"] or "-"),
        )
    )
    log_info(
        "{}  {}  {}  {}".format(
            _t("summary_embedding"),
            bold(values["EMBEDDING_BINDING"] or "-"),
            dim(values["EMBEDDING_MODEL"] or "-"),
            dim(values["EMBEDDING_HOST"] or "-"),
        )
    )
    search_summary = values["SEARCH_PROVIDER"] or _t("search_disabled")
    log_info(f"{_t('summary_search')}  {bold(search_summary)}")
    log_info(f"LLM key  {dim(_secret_mask(values['LLM_API_KEY']))}")
    log_info(f"Emb key  {dim(_secret_mask(values['EMBEDDING_API_KEY']))}")
    if values["SEARCH_PROVIDER"]:
        log_info(f"Search key  {dim(_secret_mask(values['SEARCH_API_KEY']))}")
    print()



def _write_env(values: dict[str, str]) -> None:
    get_env_store().write(values)



def _tour_banner() -> None:
    banner(
        "DeepTutor Setup Tour / DeepTutor 配置向导",
        [
            "CLI-first setup wizard.",
            "命令行配置向导。",
        ],
    )



def run_tour() -> None:
    _tour_banner()

    created_env = _ensure_env_file()
    removed_cache = _cleanup_legacy_tour_cache()

    _choose_language()

    if created_env:
        if ENV_EXAMPLE_PATH.exists():
            log_success(_t("env_created"))
        else:
            log_warn(_t("env_missing_template"))
    else:
        log_info(_t("env_exists"))
    if removed_cache:
        log_info(_t("tour_cache_removed"))

    log_info(f"{_t('platform')}  {dim(f'{platform.system()} {platform.release()}')}")
    log_info(f"{_t('python')}    {dim(_resolve_python())}")
    log_info(f"{_t('node')}      {dim(_node_strategy())}")
    log_info(f"{_t('env_path')}       {dim(str(ENV_PATH.relative_to(PROJECT_ROOT)))}")
    print()

    values: dict[str, str] = {}
    values.update(_configure_ports())
    values.update(_configure_llm())
    values.update(_configure_embedding())
    values.update(_configure_search())

    _print_review(values)
    if not confirm(_t("write_confirm"), default=True):
        log_warn(_t("no_changes"))
        return

    _write_env(values)
    log_success(_t("write_success"))
    print()
    log_success(_t("next_steps"))
    print()
    print(f"  {dim('$')} {_t('next_command')}")
    print()



def main() -> None:
    try:
        run_tour()
    except KeyboardInterrupt:
        print()
        log_warn(_t("interrupt"))
        raise SystemExit(130)


if __name__ == "__main__":
    main()
