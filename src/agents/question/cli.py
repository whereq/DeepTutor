#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive CLI for testing the refactored question module.

Usage:
    python src/agents/question/cli.py

Features:
- Real-time progress display during generation
- Saves all intermediate files (templates, traces, per-question results)
  to a per-batch directory under the output folder
- Detailed summary with question previews at the end
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Any

# Ensure project root import works when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.question import AgentCoordinator
from src.knowledge.config import KNOWLEDGE_BASES_DIR
from src.knowledge.manager import KnowledgeBaseManager
from src.services.llm.config import get_llm_config


# ── Formatting helpers ────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
CHECK = f"{GREEN}✓{RESET}"
CROSS = f"{RED}✗{RESET}"
ARROW = f"{CYAN}→{RESET}"


def _hr(char: str = "─", width: int = 70) -> str:
    return f"{DIM}{char * width}{RESET}"


def _header(title: str) -> None:
    print(f"\n{_hr('━')}")
    print(f"  {BOLD}{title}{RESET}")
    print(_hr("━"))


def _prompt_non_empty(message: str, default: str | None = None) -> str:
    suffix = f" [{DIM}{default}{RESET}]" if default else ""
    while True:
        raw = input(f"  {message}{suffix}: ").strip()
        if raw:
            return raw
        if default is not None:
            return default
        print(f"  {RED}输入不能为空，请重试。{RESET}")


def _list_kbs() -> list[str]:
    """Fetch available knowledge bases from the local KB manager."""
    try:
        manager = KnowledgeBaseManager(str(KNOWLEDGE_BASES_DIR))
        return manager.list_knowledge_bases()
    except Exception:
        return []


def _select_kb() -> str:
    """Show a numbered list of KBs and let the user pick one."""
    kbs = _list_kbs()
    if not kbs:
        print(f"  {YELLOW}未找到已有知识库，请手动输入名称。{RESET}")
        return _prompt_non_empty("KB 名称", "ai_textbook")

    print(f"\n  {BOLD}可用知识库:{RESET}")
    for i, name in enumerate(kbs, 1):
        print(f"    {CYAN}{i}{RESET}) {name}")
    print(f"    {CYAN}0{RESET}) 手动输入")

    while True:
        raw = input(f"  选择 [{DIM}1{RESET}]: ").strip()
        if not raw:
            return kbs[0]
        if raw == "0":
            return _prompt_non_empty("KB 名称")
        try:
            idx = int(raw)
            if 1 <= idx <= len(kbs):
                return kbs[idx - 1]
        except ValueError:
            # Allow typing a name directly
            if raw in kbs:
                return raw
        print(f"  {RED}无效选择，请重试。{RESET}")


def _prompt_int(message: str, default: int) -> int:
    while True:
        raw = input(f"  {message} [{DIM}{default}{RESET}]: ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print(f"  {RED}请输入正整数。{RESET}")


# ── Progress callback ────────────────────────────────────────────────

async def _cli_progress(data: dict[str, Any]) -> None:
    """Real-time progress callback printed to terminal."""
    msg_type = data.get("type", "")

    if msg_type == "progress":
        stage = data.get("stage", "")
        if stage == "idea_loop":
            rd = data.get("current_round", "")
            mx = data.get("max_rounds", "")
            if rd:
                print(f"    {MAGENTA}🔄 创意循环{RESET} 第 {rd}/{mx} 轮")
        elif stage == "generating":
            cur = data.get("current", "")
            tot = data.get("total", "")
            qid = data.get("question_id", "")
            if cur and tot:
                print(f"    {CYAN}📝 生成中{RESET} {cur}/{tot}  {DIM}{qid}{RESET}")
        elif stage == "complete":
            comp = data.get("completed", "?")
            tot = data.get("total", "?")
            print(f"    {GREEN}✅ 完成{RESET} {comp}/{tot}")
        elif stage in ("parsing", "extracting", "uploading"):
            status = data.get("status", "")
            print(f"    {YELLOW}📄 {stage}{RESET} {status}")

    elif msg_type == "templates_ready":
        count = data.get("count", 0)
        print(f"    {GREEN}📋 模板就绪{RESET} {count} 个")

    elif msg_type == "idea_round":
        rd = data.get("round", "?")
        fb = data.get("feedback", "")
        cont = data.get("continue_loop", False)
        status = "继续改进" if cont else "已确定"
        print(f"    {MAGENTA}💡 创意第 {rd} 轮{RESET} → {status}")
        if fb:
            print(f"       {DIM}反馈: {fb[:100]}{RESET}")

    elif msg_type == "question_update":
        qid = data.get("question_id", "")
        attempt = data.get("attempt", 1)
        max_att = data.get("max_attempts", "?")
        print(f"    {CYAN}⚙  {qid}{RESET} 生成 (尝试 {attempt}/{max_att})")

    elif msg_type == "validating":
        qid = data.get("question_id", "")
        attempt = data.get("attempt", 1)
        validation = data.get("validation", {})
        decision = validation.get("decision", "?")
        icon = CHECK if decision == "approve" else CROSS
        print(f"    {YELLOW}🔍 {qid}{RESET} 验证 → {icon} {decision}")

    elif msg_type == "result":
        qid = data.get("question_id", "")
        validation = data.get("validation", {})
        approved = validation.get("approved", False)
        attempts = data.get("attempts", 1)
        icon = CHECK if approved else CROSS
        print(f"    {icon} {BOLD}{qid}{RESET} ({attempts} 次尝试)")


# ── Result display ────────────────────────────────────────────────────

def _print_summary(summary: dict[str, Any]) -> None:
    _header("结果摘要")
    success = summary.get("success", False)
    status_icon = f"{GREEN}SUCCESS{RESET}" if success else f"{RED}FAILED{RESET}"
    print(f"  状态:     {status_icon}")
    print(f"  来源:     {summary.get('source', '?')}")
    print(f"  请求:     {summary.get('requested', '?')} 道")
    print(f"  成功:     {GREEN}{summary.get('completed', 0)}{RESET}")
    print(f"  失败:     {RED}{summary.get('failed', 0)}{RESET}")
    print(f"  模板数:   {summary.get('template_count', '?')}")

    batch_dir = summary.get("batch_dir")
    if batch_dir:
        print(f"  输出目录: {CYAN}{batch_dir}{RESET}")

    results = summary.get("results", []) or []
    if results:
        print(f"\n  {BOLD}题目预览:{RESET}")
        for i, item in enumerate(results, 1):
            qa = item.get("qa_pair", {})
            approved = item.get("success", False)
            icon = CHECK if approved else CROSS
            q_type = qa.get("question_type", "unknown")
            question = str(qa.get("question", "")).replace("\n", " ")[:100]
            attempts = len(item.get("attempts", []))

            # Tool usage info
            tool_plan = qa.get("metadata", {}).get("tool_plan", {})
            tools_used = []
            if tool_plan.get("use_rag"):
                tools_used.append("rag")
            if tool_plan.get("use_web"):
                tools_used.append("web")
            if tool_plan.get("use_code"):
                tools_used.append("code")
            tool_str = f" {DIM}[{', '.join(tools_used)}]{RESET}" if tools_used else ""

            print(f"  {icon} {i}. [{q_type}]{tool_str} {DIM}({attempts}次){RESET}")
            print(f"     {question}...")

    print()


# ── Coordinator builder ───────────────────────────────────────────────

def _build_coordinator(
    kb_name: str, output_dir: str, language: str
) -> AgentCoordinator:
    try:
        llm_config = get_llm_config()
        return AgentCoordinator(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=getattr(llm_config, "api_version", None),
            kb_name=kb_name,
            output_dir=output_dir,
            language=language,
        )
    except Exception:
        return AgentCoordinator(
            kb_name=kb_name, output_dir=output_dir, language=language
        )


# ── Mode runners ──────────────────────────────────────────────────────

async def _run_topic_mode(coordinator: AgentCoordinator) -> None:
    _header("Topic 模式")
    user_topic = _prompt_non_empty("主题 (如: Lagrange multipliers)")
    preference = input(f"  偏好 (可留空): ").strip()
    num_questions = _prompt_int("题目数量", 3)

    print(f"\n  {ARROW} 开始生成 {BOLD}{num_questions}{RESET} 道题...")
    print(_hr())

    coordinator.set_ws_callback(_cli_progress)
    summary = await coordinator.generate_from_topic(
        user_topic=user_topic,
        preference=preference,
        num_questions=num_questions,
    )
    _print_summary(summary)


async def _run_mimic_mode(coordinator: AgentCoordinator) -> None:
    _header("Mimic 模式")
    mode = _prompt_non_empty("输入模式 [upload/parsed]", "parsed").lower()
    if mode not in {"upload", "parsed"}:
        print(f"  {YELLOW}无效模式，使用 parsed。{RESET}")
        mode = "parsed"

    if mode == "upload":
        exam_path = _prompt_non_empty("PDF 路径")
    else:
        exam_path = _prompt_non_empty("已解析试卷目录路径")

    max_questions = _prompt_int("最大题目数", 5)

    print(f"\n  {ARROW} 开始解析并生成...")
    print(_hr())

    coordinator.set_ws_callback(_cli_progress)
    summary = await coordinator.generate_from_exam(
        exam_paper_path=exam_path,
        max_questions=max_questions,
        paper_mode=mode,
    )
    _print_summary(summary)


# ── Main ──────────────────────────────────────────────────────────────

async def main() -> None:
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"  {BOLD}{CYAN}DeepTutor Question Module CLI{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}")

    kb_name = _select_kb()
    language = _prompt_non_empty("语言 [en/zh]", "zh").lower()
    if language not in {"en", "zh"}:
        print(f"  {YELLOW}语言无效，使用 zh。{RESET}")
        language = "zh"

    default_output = str(PROJECT_ROOT / "data" / "user" / "question")
    output_dir = _prompt_non_empty(f"输出目录", default_output)

    coordinator = _build_coordinator(
        kb_name=kb_name,
        output_dir=output_dir,
        language=language,
    )

    print(f"\n  {DIM}配置: KB={kb_name}, 语言={language}, 输出={output_dir}{RESET}")

    while True:
        print(f"\n  {BOLD}请选择模式:{RESET}")
        print(f"    {CYAN}1{RESET}) Topic 模式 — 基于主题生成")
        print(f"    {CYAN}2{RESET}) Mimic 模式 — 基于试卷仿题")
        print(f"    {CYAN}q{RESET}) 退出")
        choice = input(f"  {ARROW} ").strip().lower()

        try:
            if choice == "1":
                await _run_topic_mode(coordinator)
            elif choice == "2":
                await _run_mimic_mode(coordinator)
            elif choice in {"q", "quit", "exit"}:
                print(f"\n  {DIM}已退出。{RESET}\n")
                break
            else:
                print(f"  {RED}无效输入，请重试。{RESET}")
        except KeyboardInterrupt:
            print(f"\n  {YELLOW}已中断当前任务。{RESET}")
        except Exception as exc:
            print(f"\n  {RED}运行失败: {exc}{RESET}")


if __name__ == "__main__":
    asyncio.run(main())
