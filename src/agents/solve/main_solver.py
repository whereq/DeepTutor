#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Solver - Problem-Solving System Controller

Based on Dual-Loop Architecture: Analysis Loop + Solve Loop
"""

import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import traceback
from typing import Any

import yaml

from ...services.config import parse_language
from ...services.path_service import get_path_service
from .analysis_loop import InvestigateAgent, NoteAgent

# Dual-Loop Architecture
from .memory import (
    CitationMemory,
    InvestigateMemory,
    SolveMemory,
    SolveOutput,
)
from .solve_loop import (
    ManagerAgent,
    PrecisionAnswerAgent,
    ResponseAgent,
    SolveAgent,
    SolveNoteAgent,
    ToolAgent,
)
from .utils import ConfigValidator, PerformanceMonitor, SolveAgentLogger
from .utils.display_manager import get_display_manager
from .utils.token_tracker import TokenTracker


class MainSolver:
    """Problem-Solving System Controller"""

    def __init__(
        self,
        config_path: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        api_version: str | None = None,
        language: str | None = None,
        kb_name: str = "ai_textbook",
        output_base_dir: str | None = None,
    ):
        """
        Initialize MainSolver with lightweight setup.
        Call ainit() to complete async initialization.

        Args:
            config_path: Config file path (default: config.yaml in current directory)
            api_key: API key (if not provided, read from environment)
            base_url: API URL (if not provided, read from environment)
            api_version: API version (if not provided, read from environment)
            language: Preferred language for prompts ("en"/"zh"/"cn")
            kb_name: Knowledge base name
            output_base_dir: Output base directory (optional, overrides config)
        """
        # Store initialization parameters
        self._config_path = config_path
        self._api_key = api_key
        self._base_url = base_url
        self._api_version = api_version
        self._language = language
        self._kb_name = kb_name
        self._output_base_dir = output_base_dir

        # Initialize with None - will be set in ainit()
        self.config = None
        self.api_key = None
        self.base_url = None
        self.api_version = None
        self.kb_name = kb_name
        self.logger = None
        self.monitor = None
        self.token_tracker = None

    async def ainit(self) -> None:
        """
        Complete the asynchronous second phase of MainSolver initialization.

        This class uses a two-phase initialization pattern:

        1. ``__init__`` performs only lightweight, synchronous setup and stores
           constructor arguments. Attributes such as ``config``, ``api_key``,
           ``base_url``, ``api_version``, ``logger``, ``monitor``, and
           ``token_tracker`` are intentionally left as ``None``.
        2. :meth:`ainit` performs all I/O-bound and asynchronous work required to
           make the instance fully usable (e.g., loading configuration, wiring up
           logging/monitoring, and preparing external-service clients).

        You **must** call and await this method exactly once after constructing
        ``MainSolver`` and **before** invoking any other methods that rely on
        configuration, logging, metrics, or API access. Using the object prior
        to calling :meth:`ainit` may result in attributes still being ``None``,
        which can lead to confusing runtime errors such as ``AttributeError``,
        misconfigured API calls, missing logs/metrics, or incorrect output paths.

        This async initialization pattern is used instead of performing all setup
        in ``__init__`` so that object construction remains fast and synchronous,
        while allowing potentially slow operations (disk I/O, network requests,
        validation) to be awaited explicitly by the caller in an async context.
        """
        config_path = self._config_path
        api_key = self._api_key
        base_url = self._base_url
        api_version = self._api_version
        kb_name = self._kb_name
        output_base_dir = self._output_base_dir
        language = self._language

        # Load config from config directory (main.yaml unified config)
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            # Load main.yaml (solve_config.yaml is optional and will be merged if exists)
            from ...services.config.loader import load_config_with_main_async

            full_config = await load_config_with_main_async("main.yaml", project_root)

            # Extract solve-specific config and build validator-compatible structure
            solve_config = full_config.get("solve", {})
            paths_config = full_config.get("paths", {})

            # Build config structure expected by ConfigValidator
            path_service = get_path_service()
            default_solve_dir = str(path_service.get_solve_dir())
            self.config = {
                "system": {
                    "output_base_dir": paths_config.get("solve_output_dir", default_solve_dir),
                    "save_intermediate_results": solve_config.get(
                        "save_intermediate_results", True
                    ),
                    "language": full_config.get("system", {}).get("language", "en"),
                },
                "agents": solve_config.get("agents", {}),
                "logging": full_config.get("logging", {}),
                "tools": full_config.get("tools", {}),
                "paths": paths_config,
                # Keep solve-specific settings accessible
                "solve": solve_config,
            }
        else:
            # If custom config path provided, load it directly (for backward compatibility)
            local_config = {}
            if Path(config_path).exists():
                try:

                    def load_local_config(path: str) -> dict:
                        with open(path, encoding="utf-8") as f:
                            return yaml.safe_load(f) or {}

                    local_config = await asyncio.to_thread(load_local_config, config_path)
                except Exception:
                    # Config loading warning will be handled by config_loader
                    pass
            self.config = local_config if isinstance(local_config, dict) else {}

        if self.config is None or not isinstance(self.config, dict):
            self.config = {}

        # Override system language from UI if provided
        if language:
            self.config.setdefault("system", {})
            self.config["system"]["language"] = parse_language(language)

        # Override output directory config
        if output_base_dir:
            if "system" not in self.config:
                self.config["system"] = {}
            self.config["system"]["output_base_dir"] = str(output_base_dir)

            # Note: log_dir and performance_log_dir are now in paths section from main.yaml
            # Only override if explicitly needed

        # Validate config
        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate(self.config)
        if not is_valid:
            raise ValueError(f"Config validation failed: {errors}")

        # API config
        if api_key is None or base_url is None or "llm" not in self.config:
            try:
                from ...services.llm.config import get_llm_config_async

                llm_config = await get_llm_config_async()
                if api_key is None:
                    api_key = llm_config.api_key
                if base_url is None:
                    base_url = llm_config.base_url
                if api_version is None:
                    api_version = getattr(llm_config, "api_version", None)

                # Ensure LLM config is populated in self.config for agents
                if "llm" not in self.config:
                    self.config["llm"] = {}

                # Update config with complete details (binding, model, etc.)
                from dataclasses import asdict

                self.config["llm"].update(asdict(llm_config))

            except ValueError as e:
                raise ValueError(f"LLM config error: {e!s}")

        # Check if API key is required
        # Local LLM servers (Ollama, LM Studio, etc.) don't need API keys
        from src.services.llm import is_local_llm_server

        if not api_key and not is_local_llm_server(base_url):
            raise ValueError("API key not set. Provide api_key param or set LLM_API_KEY in .env")

        # For local servers, use a placeholder key if none provided
        if not api_key and is_local_llm_server(base_url):
            api_key = "sk-no-key-required"

        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version
        self.kb_name = kb_name

        # Initialize logging system
        logging_config = self.config.get("logging", {})
        # Get log_dir from paths (user_log_dir from main.yaml) or logging config
        log_dir = (
            self.config.get("paths", {}).get("user_log_dir")
            or self.config.get("paths", {}).get("log_dir")
            or logging_config.get("log_dir")
        )
        self.logger = SolveAgentLogger(
            name="Solver",
            level=logging_config.get("level", "INFO"),
            log_dir=log_dir,
            console_output=logging_config.get("console_output", True),
            file_output=logging_config.get("save_to_file", True),
        )

        # Attach display manager for TUI and frontend status updates
        self.logger.display_manager = get_display_manager()

        # Initialize performance monitor (disabled by default - performance logging is deprecated)
        monitoring_config = self.config.get("monitoring", {})
        # Disable performance monitor by default to avoid creating performance directory
        self.monitor = PerformanceMonitor(
            enabled=False,
            save_dir=None,  # Disabled - performance logging is deprecated
        )

        # Initialize Token tracker
        self.token_tracker = TokenTracker(prefer_tiktoken=True)

        # Connect token_tracker to display_manager for real-time updates
        if self.logger.display_manager:
            self.token_tracker.set_on_usage_added_callback(
                self.logger.display_manager.update_token_stats
            )

        self.logger.section("Dual-Loop Solver Initializing")
        self.logger.info(f"Knowledge Base: {kb_name}")

        # Initialize Agents
        self._init_agents()

        self.logger.success("Solver ready")

    def _deep_merge(self, base: dict, update: dict) -> dict:
        """Deep merge two dictionaries"""
        if base is None:
            base = {}
        if update is None:
            update = {}

        result = base.copy() if base else {}
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _init_agents(self):
        """Initialize all Agents - Dual-Loop Architecture"""
        self.logger.progress("Initializing agents...")

        # Analysis Loop Agents
        self.investigate_agent = InvestigateAgent(
            config=self.config,
            api_key=self.api_key,
            base_url=self.base_url,
            api_version=self.api_version,
            token_tracker=self.token_tracker,
        )
        self.logger.info("  InvestigateAgent initialized")

        self.note_agent = NoteAgent(
            config=self.config,
            api_key=self.api_key,
            base_url=self.base_url,
            api_version=self.api_version,
            token_tracker=self.token_tracker,
        )
        self.logger.info("  NoteAgent initialized")

        # Solve Loop Agents (lazy initialization)
        self.manager_agent = None
        self.solve_agent = None
        self.tool_agent = None
        self.response_agent = None
        self.solve_note_agent = None
        self.precision_answer_agent = None
        self.logger.info("  Solve Loop agents (lazy init)")

    async def solve(self, question: str, verbose: bool = True) -> dict[str, Any]:
        """
        Main solving process - Dual-Loop Architecture

        Args:
            question: User question
            verbose: Whether to print detailed info

        Returns:
            dict: Solving result
        """
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path_service = get_path_service()
        output_base_dir = self.config.get("system", {}).get("output_base_dir", str(path_service.get_solve_dir()))
        output_dir = os.path.join(output_base_dir, f"solve_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

        # Add task log file handler
        task_log_file = os.path.join(output_dir, "task.log")
        self.logger.add_task_log_handler(task_log_file)

        self.logger.section("Problem Solving Started")
        self.logger.info(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
        self.logger.info(f"Output: {output_dir}")

        try:
            # Execute dual-loop pipeline
            result = await self._run_dual_loop_pipeline(question, output_dir)

            # Add metadata
            result["metadata"] = {
                "mode": "dual_loop",
                "timestamp": timestamp,
                "output_dir": output_dir,
            }

            # Save performance report
            if self.config.get("monitoring", {}).get("enabled", True):
                perf_report = self.monitor.generate_report()
                perf_file = os.path.join(output_dir, "performance_report.json")
                with open(perf_file, "w", encoding="utf-8") as f:
                    json.dump(perf_report, f, ensure_ascii=False, indent=2)
                self.logger.debug(f"Performance report saved: {perf_file}")

            # Output cost report
            if self.token_tracker:
                cost_summary = self.token_tracker.get_summary()
                if cost_summary["total_calls"] > 0:
                    cost_text = self.token_tracker.format_summary()
                    self.logger.info(f"\n{cost_text}")

                    cost_file = os.path.join(output_dir, "cost_report.json")
                    self.token_tracker.save(cost_file)
                    self.logger.debug(f"Cost report saved: {cost_file}")

                    self.token_tracker.reset()

            self.logger.success("Problem solving completed")
            self.logger.remove_task_log_handlers()

            return result

        except Exception as e:
            self.logger.error(f"Solving failed: {e!s}")
            self.logger.error(traceback.format_exc())
            self.logger.remove_task_log_handlers()
            raise

        finally:
            if hasattr(self, "logger"):
                self.logger.shutdown()

    async def _run_dual_loop_pipeline(self, question: str, output_dir: str) -> dict[str, Any]:
        """
        Dual-Loop Pipeline:
        1) Analysis Loop: Investigate → Note
        2) Solve Loop: Plan → Solve → Note → Format
        """

        self.logger.info("Pipeline: Analysis Loop → Solve Loop")

        # ========== Analysis Loop ==========
        self.logger.stage("Analysis Loop", "start", "Understanding the question")

        investigate_memory = InvestigateMemory.load_or_create(
            output_dir=output_dir, user_question=question
        )

        citation_memory = CitationMemory.load_or_create(output_dir=output_dir)

        # Read max_iterations from solve.agents.investigate_agent config (authoritative source)
        agent_config = self.config.get("solve", {}).get("agents", {}).get("investigate_agent", {})
        max_analysis_iterations = agent_config.get("max_iterations", 5)
        self.logger.log_stage_progress(
            "AnalysisLoop", "start", f"max_iterations={max_analysis_iterations}"
        )

        analysis_completed = False

        # Analysis Loop iterations
        for i in range(max_analysis_iterations):
            self.logger.log_stage_progress("AnalysisLoop", "running", f"round={i + 1}")

            # 1. Investigate: Generate queries and call tools
            with self.monitor.track(f"analysis_investigate_{i + 1}"):
                investigate_result = await self.investigate_agent.process(
                    question=question,
                    memory=investigate_memory,
                    citation_memory=citation_memory,
                    kb_name=self.kb_name,
                    output_dir=output_dir,
                    verbose=False,
                )

            knowledge_ids: list[str] = investigate_result.get("knowledge_item_ids", [])
            should_stop = investigate_result.get("should_stop", False)
            reasoning = investigate_result.get("reasoning", "")
            actions = investigate_result.get("actions", [])

            self.logger.debug(f"  [Investigate] Reasoning: {reasoning or 'N/A'}")

            if hasattr(self, "_send_progress_update"):
                queries = [action.get("query", "") for action in actions if action.get("query")]
                self._send_progress_update("investigate", {"round": i + 1, "queries": queries})

            if actions:
                for action in actions:
                    tool_label = action["tool_type"]
                    query = action.get("query") or ""
                    cite_id = action.get("cite_id")
                    suffix = f" → cite_id={cite_id}" if cite_id else ""
                    self.logger.info(f"  Tool: {tool_label} | {query[:50]}{suffix}")
            else:
                self.logger.debug("  No queries generated this round")

            # 2. Note: Generate notes (if new knowledge exists)
            if knowledge_ids:
                self.logger.log_stage_progress("Note", "start")

                with self.monitor.track(f"analysis_note_{i + 1}"):
                    note_result = await self.note_agent.process(
                        question=question,
                        memory=investigate_memory,
                        new_knowledge_ids=knowledge_ids,
                        citation_memory=citation_memory,
                        output_dir=output_dir,
                        verbose=False,
                    )

                if note_result.get("success"):
                    processed = note_result.get("processed_items", 0)
                    self.logger.info(f"  Note: {processed} items processed")
                    self.logger.log_stage_progress("Note", "complete")
                else:
                    self.logger.warning(f"  Note failed: {note_result.get('reason', 'unknown')}")
                    self.logger.log_stage_progress("Note", "error")

            # Update Token stats
            self.logger.update_token_stats(self.token_tracker.get_summary())

            # 3. Check stop condition
            if should_stop:
                analysis_completed = True
                self.logger.log_stage_progress(
                    "AnalysisLoop",
                    "complete",
                    f"rounds={i + 1}, knowledge={len(investigate_memory.knowledge_chain)}",
                )
                break

        if not analysis_completed:
            self.logger.log_stage_progress(
                "AnalysisLoop",
                "warning",
                f"max_iterations({max_analysis_iterations}) reached, knowledge={len(investigate_memory.knowledge_chain)}",
            )

        # Update investigate_memory metadata
        investigate_memory.metadata["total_iterations"] = i + 1
        investigate_memory.metadata["total_knowledge_items"] = len(
            investigate_memory.knowledge_chain
        )
        investigate_memory.reflections.remaining_questions = []

        if analysis_completed:
            investigate_memory.metadata["coverage_rate"] = 1.0
            investigate_memory.metadata["avg_confidence"] = 0.9
        else:
            coverage = min(
                1.0, len(investigate_memory.knowledge_chain) / max(1, max_analysis_iterations)
            )
            investigate_memory.metadata["coverage_rate"] = coverage
            investigate_memory.metadata["avg_confidence"] = 0.6

        investigate_memory.save()

        # ========== Solve Loop ==========
        self.logger.stage("Solve Loop", "start", "Generating solution")

        solve_memory = SolveMemory.load_or_create(
            output_dir=output_dir,
            user_question=question,
        )

        # Initialize Solve Loop Agents (if not yet initialized)
        if self.manager_agent is None:
            self.logger.progress("Initializing Solve Loop agents...")
            self.manager_agent = ManagerAgent(
                self.config,
                self.api_key,
                self.base_url,
                api_version=self.api_version,
                token_tracker=self.token_tracker,
            )
            self.solve_agent = SolveAgent(
                self.config,
                self.api_key,
                self.base_url,
                api_version=self.api_version,
                token_tracker=self.token_tracker,
            )
            self.tool_agent = ToolAgent(
                self.config,
                self.api_key,
                self.base_url,
                api_version=self.api_version,
                token_tracker=self.token_tracker,
            )
            self.response_agent = ResponseAgent(
                self.config,
                self.api_key,
                self.base_url,
                api_version=self.api_version,
                token_tracker=self.token_tracker,
            )
            self.solve_note_agent = SolveNoteAgent(
                self.config,
                self.api_key,
                self.base_url,
                api_version=self.api_version,
                token_tracker=self.token_tracker,
            )

            precision_enabled = (
                self.config.get("agents", {})
                .get("precision_answer_agent", {})
                .get("enabled", False)
            )
            if precision_enabled:
                self.precision_answer_agent = PrecisionAnswerAgent(
                    self.config,
                    self.api_key,
                    self.base_url,
                    api_version=self.api_version,
                    token_tracker=self.token_tracker,
                )

        # 1. Plan: Generate todo-list
        self.logger.info("Plan: Generating todo-list...")

        plan_result = None
        for attempt in range(2):
            try:
                with self.monitor.track(f"solve_plan_attempt_{attempt + 1}"):
                    plan_result = await self.manager_agent.process(
                        question=question,
                        investigate_memory=investigate_memory,
                        solve_memory=solve_memory,
                        verbose=(attempt > 0),
                    )
                num_items = plan_result.get("num_todos") or plan_result.get("todos_count", 0)
                self.logger.log_stage_progress("Plan", "complete", f"todos={num_items}")
                self.logger.update_token_stats(self.token_tracker.get_summary())
                break
            except Exception as e:
                if attempt == 0:
                    self.logger.error(f"ManagerAgent attempt {attempt + 1} failed: {e!s}")
                    self.logger.warning("Retrying plan generation...")
                    solve_memory = SolveMemory.load_or_create(
                        output_dir=output_dir,
                        user_question=question,
                    )
                else:
                    self.logger.error(f"ManagerAgent attempt {attempt + 1} also failed")
                    raise ValueError(f"ManagerAgent failed after retry: {e!s}")

        if plan_result is None:
            raise ValueError("ManagerAgent failed to generate plan")

        # 2. Solve-Note Loop
        return await self._run_solve_loop(
            question=question,
            solve_memory=solve_memory,
            investigate_memory=investigate_memory,
            citation_memory=citation_memory,
            output_dir=output_dir,
        )

    async def _run_solve_loop(
        self,
        question: str,
        solve_memory: SolveMemory,
        investigate_memory: InvestigateMemory,
        citation_memory: CitationMemory,
        output_dir: str,
    ) -> dict[str, Any]:
        """
        Execute the solve loop with the new architecture:
        
        Outer Loop (per todo):
            Inner Loop (solve_agent iterates until tool_type == "none")
            -> note_agent (update todo-list)
            -> response_agent (generate step_response)
        """
        from .memory import IterationRecord, ToolCallRecord

        self.logger.info("Solve: Executing new iteration-based solve loop...")
        max_outer_iterations = self.config.get("solve", {}).get("max_solve_iterations", 10)
        max_inner_iterations = self.config.get("solve", {}).get("max_inner_iterations", 5)
        total_todos = len(solve_memory.todo_list)
        
        self.logger.log_stage_progress(
            "SolveLoop",
            "start",
            f"todos={total_todos}, max_outer={max_outer_iterations}",
        )

        step_responses = []
        accumulated_response = ""

        for outer_iter in range(max_outer_iterations):
            # Check if all todos are completed
            if solve_memory.is_all_completed():
                self.logger.log_stage_progress(
                    "SolveLoop",
                    "complete",
                    f"All todos completed after {outer_iter} outer iterations",
                )
                break

            # Get next pending todo
            current_todo = solve_memory.get_next_pending_todo()
            if not current_todo:
                self.logger.warning("No pending todo found, but not all completed")
                break

            self.logger.info(f"  Outer Iteration {outer_iter + 1}: {current_todo.todo_id}")
            self.logger.log_stage_progress(
                "SolveLoop", "running", f"outer={outer_iter + 1}, todo={current_todo.todo_id}"
            )

            # Mark todo as in progress
            solve_memory.mark_todo_in_progress(current_todo.todo_id)

            # Create iteration record
            iteration_record = solve_memory.create_iteration(current_todo.todo_id)

            # ================================================================
            # Inner Loop: solve_agent iterates until tool_type == "none"
            # ================================================================
            tool_call_history: list[ToolCallRecord] = []

            for inner_iter in range(max_inner_iterations):
                self.logger.info(f"    Inner {inner_iter + 1}: Calling solve_agent...")

                with self.monitor.track(f"solve_inner_{outer_iter + 1}_{inner_iter + 1}"):
                    solve_result = await self.solve_agent.process(
                        current_todo=current_todo,
                        iteration_history=tool_call_history,
                        knowledge_chain=investigate_memory.knowledge_chain,
                        question=question,
                        verbose=False,
                    )

                tool_type = solve_result.get("tool_type", "none")
                query = solve_result.get("query", "")

                self.logger.info(f"      tool_type={tool_type}, query={query[:50]}...")

                # Check for termination
                if tool_type == "none" or solve_result.get("should_stop"):
                    self.logger.info(f"    Inner loop ended: {solve_result.get('reason', 'tool_type=none')}")
                    break

                # Execute the tool call
                tool_record = await self._execute_single_tool_call(
                    tool_type=tool_type,
                    query=query,
                    iteration_record=iteration_record,
                    citation_memory=citation_memory,
                    output_dir=output_dir,
                )

                if tool_record:
                    tool_call_history.append(tool_record)
                    iteration_record.append_tool_call(tool_record)

                self.logger.update_token_stats(self.token_tracker.get_summary())

            # ================================================================
            # Note Agent: Update todo-list based on iteration results
            # ================================================================
            self.logger.info(f"    Calling note_agent...")

            with self.monitor.track(f"note_{outer_iter + 1}"):
                note_result = await self.solve_note_agent.process(
                    solve_memory=solve_memory,
                    iteration_record=iteration_record,
                    target_todo=current_todo,
                    verbose=False,
                )

            completed_todos = note_result.get("completed_todos", [])
            if completed_todos:
                self.logger.info(f"    Completed: {completed_todos}")
            if note_result.get("actions"):
                for action in note_result["actions"]:
                    self.logger.info(f"      Action: {action}")

            # ================================================================
            # Fallback: If no tool calls and note_agent didn't mark complete,
            # auto-complete the todo (solve_agent deemed info sufficient)
            # ================================================================
            if not tool_call_history and current_todo.todo_id not in completed_todos:
                self.logger.info(
                    f"    Auto-completing {current_todo.todo_id} (no tool calls needed)"
                )
                solve_memory.mark_todo_completed(
                    todo_id=current_todo.todo_id,
                    output_id="",
                    evidence="Completed using existing knowledge (no additional tools needed)",
                )
                completed_todos.append(current_todo.todo_id)
                iteration_record.set_completed_todos(completed_todos)

            # ================================================================
            # Response Agent: Generate step_response for completed todos
            # ================================================================
            if completed_todos:
                self.logger.info(f"    Calling response_agent...")

                # Get the completed TodoItem objects
                completed_todo_items = [
                    solve_memory.get_todo(tid)
                    for tid in completed_todos
                    if solve_memory.get_todo(tid)
                ]

                with self.monitor.track(f"response_{outer_iter + 1}"):
                    response_result = await self.response_agent.process(
                        question=question,
                        iteration_record=iteration_record,
                        completed_todos=completed_todo_items,
                        citation_memory=citation_memory,
                        knowledge_chain=investigate_memory.knowledge_chain,
                        output_dir=output_dir,
                        accumulated_response=accumulated_response,
                        verbose=False,
                    )

                step_response = response_result.get("step_response", "")
                if step_response:
                    step_responses.append(step_response)
                    accumulated_response = "\n\n".join(step_responses)
                    self.logger.info(f"    Step response: {len(step_response)} chars")

            # Save progress
            solve_memory.save()
            self.logger.update_token_stats(self.token_tracker.get_summary())

        else:
            self.logger.warning(f"Max outer iterations ({max_outer_iterations}) reached")

        # ================================================================
        # Finalize: Compile final answer
        # ================================================================
        completed_count = len(solve_memory.get_completed_todos())
        self.logger.log_stage_progress(
            "SolveLoop",
            "complete",
            f"completed={completed_count}/{total_todos}",
        )

        # Save todo-list execution history
        try:
            history_file = solve_memory.save_todo_history(output_dir)
            self.logger.info(f"Todo history saved: {history_file}")
        except Exception as e:
            self.logger.warning(f"Failed to save todo history: {e}")

        self.logger.info("Finalize: Compiling final answer...")
        self.logger.log_stage_progress("Finalize", "start", "Compiling step responses")

        # Compile step responses into final answer
        final_answer = "\n\n".join(step_responses) if step_responses else ""

        # Add citations section
        used_cite_ids = solve_memory.get_all_iteration_citations()
        language = self.config.get("system", {}).get("language", "zh")
        lang_code = parse_language(language)
        enable_citations = self.config.get("system", {}).get("enable_citations", True)

        citations_section = ""
        if enable_citations and citation_memory and used_cite_ids:
            citations_section = citation_memory.format_citations_markdown(
                used_cite_ids=used_cite_ids, language=lang_code
            )
            if citations_section:
                final_answer = f"{final_answer}\n\n---\n\n{citations_section}"

        self.logger.info(f"  Final answer: {len(final_answer)} chars")
        self.logger.info(f"  Citations: {len(used_cite_ids)}")

        # Precision Answer (if enabled)
        final_answer_content = final_answer.strip()
        precision_answer_enabled = (
            self.config.get("agents", {}).get("precision_answer_agent", {}).get("enabled", False)
        )

        if precision_answer_enabled and self.precision_answer_agent and final_answer_content:
            self.logger.info("PrecisionAnswer: Generating concise answer...")
            with self.monitor.track("precision_answer"):
                precision_result = await self.precision_answer_agent.process(
                    question=question,
                    detailed_answer=final_answer_content,
                    verbose=False,
                )
            if precision_result.get("needs_precision"):
                precision_answer = precision_result.get("precision_answer", "")
                self.logger.info(f"  Precision answer: {len(precision_answer)} chars")
                final_answer_content = (
                    f"## Concise Answer\n\n{precision_answer}\n\n---\n\n"
                    f"## Detailed Answer\n\n{final_answer_content}"
                )

        # Save final answer
        final_answer_file = Path(output_dir) / "final_answer.md"
        with open(final_answer_file, "w", encoding="utf-8") as f:
            f.write(final_answer_content)

        self.logger.success(f"Final answer saved: {final_answer_file}")
        self.logger.log_stage_progress("Format", "complete", f"output={final_answer_file}")

        # Publish SOLVE_COMPLETE event for personalization
        try:
            from src.core.event_bus import Event, EventType, get_event_bus

            # Collect tools used during the solve process
            tools_used = list(set(
                tc.tool_type 
                for ir in solve_memory.iteration_records 
                for tc in ir.tool_calls
            ))

            event = Event(
                type=EventType.SOLVE_COMPLETE,
                task_id=task_id,
                user_input=question,
                agent_output=final_answer_content[:2000],  # Truncate for efficiency
                tools_used=tools_used,
                success=True,
                metadata={
                    "total_todos": total_todos,
                    "completed_todos": completed_count,
                    "citations_count": len(used_cite_ids),
                },
            )
            await get_event_bus().publish(event)
            self.logger.debug("Published SOLVE_COMPLETE event")
        except Exception as e:
            self.logger.debug(f"Failed to publish SOLVE_COMPLETE event: {e}")

        return {
            "question": question,
            "output_dir": output_dir,
            "final_answer": final_answer_content,
            "output_md": str(final_answer_file),
            "output_json": str(Path(output_dir) / "solve_chain.json"),
            "formatted_solution": final_answer_content,
            "citations": used_cite_ids,
            "pipeline": "iteration_mode",
            "total_todos": total_todos,
            "completed_todos": completed_count,
            "total_iterations": len(solve_memory.iteration_records),
            "total_step_responses": len(step_responses),
            "analysis_iterations": investigate_memory.metadata.get("total_iterations", 0),
            "metadata": {
                "coverage_rate": investigate_memory.metadata.get("coverage_rate", 0.0),
                "avg_confidence": investigate_memory.metadata.get("avg_confidence", 0.0),
                "total_todos": total_todos,
                "completed_todos": completed_count,
            },
        }

    async def _execute_single_tool_call(
        self,
        tool_type: str,
        query: str,
        iteration_record,
        citation_memory: CitationMemory,
        output_dir: str | None,
    ):
        """Execute a single tool call and return the ToolCallRecord"""
        from .memory import ToolCallRecord

        base_dir = Path(output_dir).resolve() if output_dir else Path().resolve()
        artifacts_dir = base_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Create citation
        cite_id = citation_memory.add_citation(
            tool_type=tool_type,
            query=query,
            raw_result="",
            content="",
            stage="solve",
            step_id=iteration_record.iteration_id,
        )

        # Create tool call record
        record = ToolCallRecord(
            tool_type=tool_type,
            query=query,
            cite_id=cite_id,
            metadata={"kb_name": self.kb_name},
        )

        try:
            # Execute the tool call
            raw_answer, metadata = await self.tool_agent._execute_single_call(
                record=record,
                kb_name=self.kb_name,
                output_dir=output_dir,
                artifacts_dir=str(artifacts_dir),
                verbose=False,
            )

            # Generate summary
            summary = await self.tool_agent._summarize_tool_result(
                tool_type=tool_type,
                query=query,
                raw_answer=raw_answer,
            )

            # Update the record
            record.mark_result(
                raw_answer=raw_answer,
                summary=summary,
                status="success",
                metadata=metadata,
            )

            # Update citation
            citation_memory.update_citation(
                cite_id=cite_id,
                raw_result=raw_answer,
                content=summary,
                metadata=metadata,
                step_id=iteration_record.iteration_id,
            )

            self.logger.info(f"      Tool executed: {tool_type} -> {summary[:80]}...")

        except Exception as e:
            error_msg = str(e)
            record.mark_result(
                raw_answer=error_msg,
                summary=f"Error: {error_msg[:200]}",
                status="failed",
                metadata={"error": True},
            )
            self.logger.warning(f"      Tool failed: {tool_type} -> {error_msg[:100]}")

        citation_memory.save()
        return record

    async def _execute_output_tool_calls(
        self,
        output: SolveOutput,
        solve_memory: SolveMemory,
        citation_memory: CitationMemory,
        output_dir: str | None,
    ) -> dict[str, Any]:
        """Execute tool calls for a SolveOutput"""

        # Get pending tool calls
        pending_calls = [
            call for call in output.tool_calls
            if call.status in {"pending", "running"}
        ]

        if not pending_calls:
            return {"executed": [], "status": "idle"}

        logs = []
        base_dir = Path(output_dir).resolve() if output_dir else Path().resolve()
        artifacts_dir = base_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        for record in pending_calls:
            import time
            start_ts = time.time()
            try:
                # Execute the tool call using ToolAgent's internal method
                raw_answer, metadata = await self.tool_agent._execute_single_call(
                    record=record,
                    kb_name=self.kb_name,
                    output_dir=output_dir,
                    artifacts_dir=str(artifacts_dir),
                    verbose=False,
                )

                # Generate summary
                summary = await self.tool_agent._summarize_tool_result(
                    tool_type=record.tool_type,
                    query=record.query,
                    raw_answer=raw_answer,
                )

                # Update the record
                record.mark_result(
                    raw_answer=raw_answer,
                    summary=summary,
                    status="success",
                    metadata=metadata,
                )

                # Update citation
                if record.cite_id:
                    citation_memory.update_citation(
                        cite_id=record.cite_id,
                        raw_result=raw_answer,
                        content=summary,
                        metadata=metadata,
                        step_id=output.output_id,
                    )

                logs.append({
                    "call_id": record.call_id,
                    "tool_type": record.tool_type,
                    "status": "success",
                    "summary": summary,
                })

            except Exception as e:
                error_msg = str(e)
                record.mark_result(
                    raw_answer=error_msg,
                    summary=error_msg[:200],
                    status="failed",
                    metadata={"error": True},
                )
                logs.append({
                    "call_id": record.call_id,
                    "tool_type": record.tool_type,
                    "status": "failed",
                    "error": error_msg,
                })

        # Update output content with tool results
        if logs:
            content_parts = []
            for call in output.tool_calls:
                if call.summary:
                    content_parts.append(call.summary)
            if content_parts:
                output.set_content("\n\n".join(content_parts))

        solve_memory.save()
        citation_memory.save()

        return {"executed": logs, "status": "completed"}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    async def test():
        solver = MainSolver(kb_name="ai_textbook")
        result = await solver.solve(question="What is linear convolution?", verbose=True)
        print(f"Output file: {result['output_md']}")

    asyncio.run(test())
