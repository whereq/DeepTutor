#!/usr/bin/env python
"""
DeepTutor CLI Launcher

Unified entry point for:
1. Solver system  (same logic as ``python -m src.agents.solve.cli``)
2. Question generation system  (same logic as ``python src/agents/question/cli.py``)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / "DeepTutor.env", override=False)
load_dotenv(PROJECT_ROOT / ".env", override=False)

from src.knowledge.manager import KnowledgeBaseManager
from src.logging import get_logger
from src.services.llm.config import get_llm_config

logger = get_logger("CLI", console_output=True, file_output=True)

# ── ANSI helpers (reused from question CLI) ──────────────────────────

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


# ── Shared infrastructure ────────────────────────────────────────────


def _list_knowledge_bases() -> list[str]:
    try:
        mgr = KnowledgeBaseManager()
        return mgr.list_knowledge_bases()
    except Exception:
        kb_dir = PROJECT_ROOT / "data" / "knowledge_bases"
        if kb_dir.exists():
            return [d.name for d in kb_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        return []


def _select_kb(current: str = "ai-textbook") -> str:
    kbs = _list_knowledge_bases()
    if not kbs:
        print(f"  {YELLOW}未找到知识库，使用默认: {current}{RESET}")
        return current

    print(f"\n  {BOLD}可用知识库:{RESET}")
    for i, name in enumerate(kbs, 1):
        marker = f" {CYAN}<-{RESET}" if name == current else ""
        print(f"    {CYAN}{i}{RESET}) {name}{marker}")
    print(f"    {CYAN}0{RESET}) 保持当前 ({current})")

    while True:
        raw = input(f"  选择 [{DIM}1{RESET}]: ").strip()
        if not raw:
            return kbs[0]
        if raw == "0":
            return current
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(kbs):
                return kbs[idx]
        except ValueError:
            if raw in kbs:
                return raw
        print(f"  {RED}无效选择，请重试。{RESET}")


async def _ensure_personalization() -> bool:
    """Start EventBus and PersonalizationService for in-process memory."""
    ok = True
    try:
        from src.core.event_bus import get_event_bus

        bus = get_event_bus()
        await bus.start()
    except Exception as exc:
        print(f"\n  {RED}WARNING: EventBus failed to start: {exc}{RESET}")
        ok = False
    try:
        from src.personalization.service import get_personalization_service

        svc = get_personalization_service()
        await svc.start()
    except Exception as exc:
        print(f"\n  {RED}WARNING: PersonalizationService failed to start: {exc}{RESET}")
        ok = False
    return ok


async def _flush_events() -> None:
    """Wait for EventBus to finish processing all pending events."""
    try:
        from src.core.event_bus import get_event_bus

        bus = get_event_bus()
        await bus.flush(timeout=60.0)
    except Exception:
        pass


# ── Solve mode ───────────────────────────────────────────────────────


async def run_solve_mode(kb_name: str) -> None:
    """Solve a question — mirrors ``src.agents.solve.cli`` logic."""
    _header("解题系统 (Solver)")

    kb_name = _select_kb(current=kb_name)
    print(f"  {CHECK} 知识库: {BOLD}{kb_name}{RESET}")

    language = input(f"  语言 (en/zh) [{DIM}en{RESET}]: ").strip().lower() or "en"
    if language not in {"en", "zh"}:
        language = "en"

    print(f"\n  请输入问题 (多行输入，空行结束):")
    print(_hr())

    lines: list[str] = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    if not lines:
        print(f"  {YELLOW}未输入问题，返回主菜单{RESET}")
        return

    question = "\n".join(lines)

    print(f"\n  {ARROW} 模式: Plan → ReAct → Write")
    print(f"  {DIM}正在初始化 Solver...{RESET}")

    try:
        from src.agents.solve import MainSolver

        solver = MainSolver(kb_name=kb_name, language=language)
        await solver.ainit()

        result = await solver.solve(question)

        _header("解题完成")
        print(f"  输出目录:  {CYAN}{result['output_dir']}{RESET}")
        print(f"  步骤完成:  {result.get('completed_steps', '?')}/{result.get('total_steps', '?')}")
        print(f"  ReAct 条目: {result.get('total_react_entries', '?')}")
        print(f"  计划修订:  {result.get('plan_revisions', 0)}")

        final_answer = result.get("final_answer", "")
        if final_answer:
            print(f"\n  {BOLD}答案预览:{RESET}")
            print(_hr())
            preview_lines = final_answer.split("\n")[:20]
            preview = "\n".join(preview_lines)
            if len(final_answer.split("\n")) > 20:
                preview += f"\n\n  {DIM}... (完整内容见输出文件) ...{RESET}"
            print(preview)
            print(_hr())

    except Exception as e:
        _header("解题失败")
        print(f"  {RED}{e}{RESET}")
        import traceback
        traceback.print_exc()

    print(f"  {DIM}同步记忆...{RESET}", end="", flush=True)
    await _flush_events()
    print(f" {CHECK}")


# ── Question generation mode ─────────────────────────────────────────


async def _cli_progress(data: dict) -> None:
    """Real-time progress callback for question generation."""
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
        cont = data.get("continue_loop", False)
        status = "继续改进" if cont else "已确定"
        print(f"    {MAGENTA}💡 创意第 {rd} 轮{RESET} → {status}")
    elif msg_type == "question_update":
        qid = data.get("question_id", "")
        attempt = data.get("attempt", 1)
        max_att = data.get("max_attempts", "?")
        print(f"    {CYAN}⚙  {qid}{RESET} 生成 (尝试 {attempt}/{max_att})")
    elif msg_type == "validating":
        qid = data.get("question_id", "")
        decision = data.get("validation", {}).get("decision", "?")
        icon = CHECK if decision == "approve" else CROSS
        print(f"    {YELLOW}🔍 {qid}{RESET} 验证 → {icon} {decision}")
    elif msg_type == "result":
        qid = data.get("question_id", "")
        approved = data.get("validation", {}).get("approved", False)
        attempts = data.get("attempts", 1)
        icon = CHECK if approved else CROSS
        print(f"    {icon} {BOLD}{qid}{RESET} ({attempts} 次尝试)")


def _print_question_summary(summary: dict) -> None:
    _header("出题结果摘要")
    success = summary.get("success", False)
    status_icon = f"{GREEN}SUCCESS{RESET}" if success else f"{RED}FAILED{RESET}"
    print(f"  状态:     {status_icon}")
    print(f"  来源:     {summary.get('source', '?')}")
    print(f"  请求:     {summary.get('requested', '?')} 道")
    print(f"  成功:     {GREEN}{summary.get('completed', 0)}{RESET}")
    print(f"  失败:     {RED}{summary.get('failed', 0)}{RESET}")

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
            print(f"  {icon} {i}. [{q_type}] {DIM}({attempts}次){RESET}")
            print(f"     {question}...")
    print()


def _prompt_non_empty(message: str, default: str | None = None) -> str:
    suffix = f" [{DIM}{default}{RESET}]" if default else ""
    while True:
        raw = input(f"  {message}{suffix}: ").strip()
        if raw:
            return raw
        if default is not None:
            return default
        print(f"  {RED}输入不能为空，请重试。{RESET}")


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


# ── Interactive answering session ─────────────────────────────────────


def _display_question(idx: int, qa: dict) -> None:
    q_type = qa.get("question_type", "written")
    question_text = qa.get("question", "")
    options = qa.get("options") or {}

    print(f"\n  {BOLD}题目 {idx}{RESET}  [{q_type}]")
    print(_hr())
    print(f"  {question_text}")

    if options:
        print()
        for key in sorted(options.keys()):
            print(f"    {CYAN}{key}{RESET}. {options[key]}")
    print(_hr())


def _judge_answer(user_answer: str, correct_answer: str, q_type: str) -> str:
    ua = user_answer.strip().lower()
    ca = correct_answer.strip().lower()
    if not ua:
        return "skipped"
    if q_type == "choice":
        ua_letter = ua.strip("().）（ ").upper()
        ca_letter = ca.strip("().）（ ").upper()
        if ua_letter and ca_letter:
            return "correct" if ua_letter == ca_letter else "wrong"
    if ua == ca:
        return "correct"
    if ua in ca or ca in ua:
        return "partial"
    return "pending"


async def _run_answer_session(summary: dict) -> None:
    results = summary.get("results", []) or []
    approved_results = [r for r in results if r.get("success")]
    if not approved_results:
        print(f"  {YELLOW}没有可用的题目进行作答。{RESET}")
        return

    batch_dir = summary.get("batch_dir", "")
    trace_id = Path(batch_dir).name if batch_dir else ""

    _header(f"答题环节 ({len(approved_results)} 道题)")
    print(f"  {DIM}直接回车可跳过该题，输入 /quit 退出答题{RESET}\n")

    answers_recorded = 0
    correct_count = 0
    wrong_count = 0
    skipped_count = 0

    for i, item in enumerate(approved_results, 1):
        qa = item.get("qa_pair", {})
        question_id = qa.get("question_id", f"q_{i}")
        q_type = qa.get("question_type", "written")
        correct_answer = str(qa.get("correct_answer", ""))

        _display_question(i, qa)

        try:
            user_input = input(f"  {ARROW} 你的回答: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {YELLOW}答题中断。{RESET}")
            break

        if user_input.lower() in ("/quit", "/exit", "/q"):
            print(f"  {DIM}退出答题。{RESET}")
            break

        if not user_input:
            skipped_count += 1
            print(f"  {DIM}(已跳过){RESET}")
            continue

        judged = _judge_answer(user_input, correct_answer, q_type)

        if judged == "correct":
            print(f"  {CHECK} {GREEN}正确！{RESET}")
            correct_count += 1
        elif judged == "wrong":
            print(f"  {CROSS} {RED}错误{RESET}  正确答案: {GREEN}{correct_answer}{RESET}")
            wrong_count += 1
        elif judged == "partial":
            print(f"  {YELLOW}~ 部分匹配{RESET}  参考答案: {correct_answer}")
        elif judged == "skipped":
            skipped_count += 1
            print(f"  {DIM}(已跳过){RESET}")
            continue
        else:
            print(f"  {YELLOW}? 待判定{RESET}  参考答案: {correct_answer}")

        explanation = qa.get("explanation", "")
        if explanation:
            short_exp = explanation[:200]
            if len(explanation) > 200:
                short_exp += "..."
            print(f"  {DIM}解析: {short_exp}{RESET}")

        if trace_id:
            try:
                from src.personalization.service import get_personalization_service

                svc = get_personalization_service()
                ok = await svc.record_user_answer(
                    trace_id=trace_id,
                    question_id=question_id,
                    user_answer=user_input,
                    judged_result=judged,
                )
                if ok:
                    answers_recorded += 1
            except Exception:
                pass

    if answers_recorded > 0 and trace_id:
        print(f"\n  {DIM}同步答题记忆...{RESET}", end="", flush=True)
        await _flush_events()
        try:
            from src.personalization.service import get_personalization_service

            svc = get_personalization_service()
            await svc.flush_memory_agents(trace_id)
        except Exception:
            pass
        print(f" {CHECK}")

    _header("答题结果")
    total = correct_count + wrong_count + skipped_count
    print(f"  总计:   {total} 题")
    print(f"  正确:   {GREEN}{correct_count}{RESET}")
    print(f"  错误:   {RED}{wrong_count}{RESET}")
    print(f"  跳过:   {DIM}{skipped_count}{RESET}")
    if answers_recorded > 0:
        print(f"  {CHECK} 已记录 {answers_recorded} 条答题记录到记忆系统")
    print()


# ── Coordinator builder ──────────────────────────────────────────────


def _build_coordinator(kb_name: str, output_dir: str, language: str):
    from src.agents.question import AgentCoordinator
    from src.services.llm.config import get_llm_config as _get_llm

    try:
        cfg = _get_llm()
        return AgentCoordinator(
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            api_version=getattr(cfg, "api_version", None),
            kb_name=kb_name,
            output_dir=output_dir,
            language=language,
        )
    except Exception:
        return AgentCoordinator(
            kb_name=kb_name, output_dir=output_dir, language=language,
        )


async def run_question_mode(kb_name: str) -> None:
    """Generate questions — mirrors ``src/agents/question/cli.py`` logic."""
    _header("出题系统 (Question Generator)")

    kb_name = _select_kb(current=kb_name)
    print(f"  {CHECK} 知识库: {BOLD}{kb_name}{RESET}")

    language = input(f"  语言 (en/zh) [{DIM}zh{RESET}]: ").strip().lower() or "zh"
    if language not in {"en", "zh"}:
        language = "zh"

    default_output = str(PROJECT_ROOT / "data" / "user" / "question")
    output_dir = _prompt_non_empty("输出目录", default_output)

    coordinator = _build_coordinator(kb_name=kb_name, output_dir=output_dir, language=language)

    print(f"\n  {BOLD}请选择模式:{RESET}")
    print(f"    {CYAN}1{RESET}) Topic 模式 — 基于主题生成")
    print(f"    {CYAN}2{RESET}) Mimic 模式 — 基于试卷仿题")

    mode_choice = input(f"  {ARROW} ").strip()

    if mode_choice == "2":
        await _run_mimic_submode(coordinator)
    else:
        await _run_topic_submode(coordinator)


async def _run_topic_submode(coordinator) -> None:
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

    print(f"  {DIM}同步记忆系统...{RESET}", end="", flush=True)
    await _flush_events()
    print(f" {CHECK}")

    _print_question_summary(summary)

    approved = [r for r in (summary.get("results") or []) if r.get("success")]
    if approved:
        try:
            ans_choice = input(f"  {ARROW} 是否开始答题? (y/n) [{DIM}y{RESET}]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans_choice = "n"
        if ans_choice != "n":
            await _run_answer_session(summary)


async def _run_mimic_submode(coordinator) -> None:
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

    print(f"  {DIM}同步记忆系统...{RESET}", end="", flush=True)
    await _flush_events()
    print(f" {CHECK}")

    _print_question_summary(summary)

    approved = [r for r in (summary.get("results") or []) if r.get("success")]
    if approved:
        try:
            ans_choice = input(f"  {ARROW} 是否开始答题? (y/n) [{DIM}y{RESET}]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans_choice = "n"
        if ans_choice != "n":
            await _run_answer_session(summary)


# ── Settings ─────────────────────────────────────────────────────────


def show_settings() -> None:
    _header("系统设置")

    try:
        llm_config = get_llm_config()
        print(f"  {BOLD}LLM 配置:{RESET}")
        print(f"    模型:     {llm_config.model or 'N/A'}")
        print(f"    端点:     {llm_config.base_url or 'N/A'}")
        print(f"    API Key:  {'已配置' if llm_config.api_key else '未配置'}")
    except Exception as e:
        print(f"  {RED}加载失败: {e}{RESET}")

    kbs = _list_knowledge_bases()
    print(f"\n  {BOLD}可用知识库:{RESET}")
    for i, kb in enumerate(kbs, 1):
        print(f"    {i}. {kb}")

    print(f"\n  {BOLD}配置文件:{RESET}")
    for name in [".env", "DeepTutor.env"]:
        p = PROJECT_ROOT / name
        status = f"{GREEN}✓{RESET}" if p.exists() else f"{RED}✗{RESET}"
        print(f"    {status} {p}")

    print(f"\n  {DIM}提示: 直接编辑 .env 文件即可修改配置{RESET}")
    input(f"\n  按回车返回主菜单...")


# ── Main loop ────────────────────────────────────────────────────────


async def run() -> None:
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"  {BOLD}{CYAN}DeepTutor Evaluation System{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}")

    try:
        from src.services.setup import init_user_directories

        init_user_directories(PROJECT_ROOT)
    except Exception as e:
        print(f"  {YELLOW}WARNING: 初始化用户目录失败: {e}{RESET}")

    try:
        llm_config = get_llm_config()
        if not llm_config.api_key:
            print(f"  {RED}ERROR: 未配置 API Key，请检查 .env 文件{RESET}")
            sys.exit(1)
    except ValueError as e:
        print(f"  {RED}ERROR: {e}{RESET}")
        sys.exit(1)

    print(f"  {DIM}正在初始化记忆系统...{RESET}", end="", flush=True)
    mem_ok = await _ensure_personalization()
    print(f" {CHECK}" if mem_ok else f" {CROSS}")

    default_kb = "ai-textbook"

    while True:
        try:
            print(f"\n  {BOLD}请选择功能:{RESET}")
            print(f"    {CYAN}1{RESET}) 解题系统 (Solver)")
            print(f"    {CYAN}2{RESET}) 出题系统 (Question Generator)")
            print(f"    {CYAN}3{RESET}) 系统设置 (Settings)")
            print(f"    {CYAN}q{RESET}) 退出")
            choice = input(f"  {ARROW} ").strip().lower()

            if choice == "1":
                await run_solve_mode(default_kb)
            elif choice == "2":
                await run_question_mode(default_kb)
            elif choice == "3":
                show_settings()
                continue
            elif choice in {"q", "quit", "exit", "4"}:
                print(f"\n  {DIM}感谢使用 DeepTutor!{RESET}\n")
                break
            else:
                print(f"  {RED}无效选项，请重试。{RESET}")
                continue

            cont = input(f"\n  继续使用? (y/n) [{DIM}y{RESET}]: ").strip().lower()
            if cont == "n":
                print(f"\n  {DIM}感谢使用 DeepTutor!{RESET}\n")
                break

        except KeyboardInterrupt:
            print(f"\n\n  {YELLOW}程序中断。{RESET}\n")
            break
        except Exception as e:
            print(f"\n  {RED}错误: {e}{RESET}")
            import traceback
            traceback.print_exc()

    # Cleanup EventBus
    try:
        from src.core.event_bus import get_event_bus

        await get_event_bus().stop()
    except Exception:
        pass


def main():
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"  {RED}启动失败: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
