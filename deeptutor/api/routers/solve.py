"""
Solve API Router
================

WebSocket endpoint for real-time problem solving with streaming logs.
"""

import asyncio
import logging
from pathlib import Path
import re
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from deeptutor.agents.solve import MainSolver, SolverSessionManager
from deeptutor.api.utils.task_id_manager import TaskIDManager
from deeptutor.capabilities.deep_solve import DeepSolveCapability
from deeptutor.logging import bind_log_context, capture_process_logs
from deeptutor.services.config import PROJECT_ROOT, load_config_with_main
from deeptutor.services.llm import get_llm_config
from deeptutor.services.path_service import get_path_service
from deeptutor.services.settings.interface_settings import get_ui_language

config = load_config_with_main("main.yaml", PROJECT_ROOT)
log_dir = config.get("paths", {}).get("user_log_dir") or config.get("logging", {}).get("log_dir")
logger = logging.getLogger(__name__)

router = APIRouter()


def _get_session_manager() -> SolverSessionManager:
    return SolverSessionManager()


# =============================================================================
# REST Endpoints for Session Management
# =============================================================================


@router.get("/solve/sessions")
async def list_solver_sessions(limit: int = 20):
    return _get_session_manager().list_sessions(limit=limit, include_messages=False)


@router.get("/solve/sessions/{session_id}")
async def get_solver_session(session_id: str):
    session = _get_session_manager().get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/solve/sessions/{session_id}")
async def delete_solver_session(session_id: str):
    if _get_session_manager().delete_session(session_id):
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")


# =============================================================================
# WebSocket Endpoint for Solving
# =============================================================================


@router.websocket("/solve")
async def websocket_solve(websocket: WebSocket):
    from deeptutor.multi_user.context import reset_current_user, set_current_user
    from deeptutor.multi_user.context import user_from_token_payload
    from deeptutor.multi_user.paths import local_admin_user
    from deeptutor.services.auth import AUTH_ENABLED, decode_token

    user_token = None
    if AUTH_ENABLED:
        token = websocket.query_params.get("token") or websocket.cookies.get("dt_token")
        payload = decode_token(token) if token else None
        if not payload:
            await websocket.close(code=4001)
            return
        user_token = set_current_user(user_from_token_payload(payload))
    else:
        user_token = set_current_user(local_admin_user())

    await websocket.accept()

    task_manager = TaskIDManager.get_instance()
    connection_closed = asyncio.Event()
    log_queue = asyncio.Queue()
    pusher_task = None

    async def safe_send_json(data: dict[str, Any]):
        if connection_closed.is_set():
            return False
        try:
            await websocket.send_json(data)
            return True
        except (WebSocketDisconnect, RuntimeError, ConnectionError) as e:
            logger.debug(f"WebSocket connection closed: {e}")
            connection_closed.set()
            return False
        except Exception as e:
            logger.debug(f"Error sending WebSocket message: {e}")
            return False

    async def log_pusher():
        while not connection_closed.is_set():
            try:
                entry = await asyncio.wait_for(log_queue.get(), timeout=0.5)
                try:
                    await websocket.send_json(entry)
                except (WebSocketDisconnect, RuntimeError, ConnectionError) as e:
                    logger.debug(f"WebSocket connection closed in log_pusher: {e}")
                    connection_closed.set()
                    log_queue.task_done()
                    break
                except Exception as e:
                    logger.debug(f"Error sending log entry: {e}")
                log_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.debug(f"Error in log_pusher: {e}")
                break

    session_id = None

    try:
        data = await websocket.receive_json()
        question = data.get("question")
        tools = data.get("tools")
        enabled_tools = (
            list(DeepSolveCapability.manifest.tools_used)
            if tools is None
            else [str(name) for name in tools]
        )
        rag_enabled = "rag" in enabled_tools
        kb_name = data.get("kb_name", "ai-textbook") if rag_enabled else None
        session_id = data.get("session_id")
        detailed_answer = data.get("detailed_answer", False)

        if not question:
            await websocket.send_json({"type": "error", "content": "Question is required"})
            return

        sm = _get_session_manager()

        if session_id:
            session = sm.get_session(session_id)
            if not session:
                session = sm.create_session(
                    title=question[:50] + ("..." if len(question) > 50 else ""),
                    kb_name=kb_name or "",
                )
                session_id = session["session_id"]
        else:
            session = sm.create_session(
                title=question[:50] + ("..." if len(question) > 50 else ""),
                kb_name=kb_name or "",
            )
            session_id = session["session_id"]

        await websocket.send_json({"type": "session", "session_id": session_id})

        sm.add_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        task_key = f"solve_{kb_name}_{hash(str(question))}"
        task_id = task_manager.generate_task_id("solve", task_key)

        await websocket.send_json({"type": "task_id", "task_id": task_id})

        path_service = get_path_service()
        output_base = path_service.get_solve_dir()

        try:
            llm_config = get_llm_config()
            api_key = llm_config.api_key
            base_url = llm_config.base_url
            api_version = getattr(llm_config, "api_version", None)
        except Exception as e:
            logger.error(f"Failed to get LLM config: {e}", exc_info=True)
            await websocket.send_json({"type": "error", "content": f"LLM configuration error: {e}"})
            return

        ui_language = get_ui_language(default=config.get("system", {}).get("language", "en"))
        solver = MainSolver(
            kb_name=kb_name,
            output_base_dir=str(output_base),
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            language=ui_language,
            enabled_tools=enabled_tools,
            disable_planner_retrieve=not (rag_enabled and kb_name),
        )

        await solver.ainit()

        logger.info(f"[{task_id}] Solving: {question[:50]}...")

        display_manager = getattr(solver, "display_manager", None)
        if display_manager:
            original_set_status = display_manager.set_agent_status

            def wrapped_set_status(agent_name: str, status: str):
                original_set_status(agent_name, status)
                try:
                    log_queue.put_nowait(
                        {
                            "type": "agent_status",
                            "agent": agent_name,
                            "status": status,
                            "all_agents": display_manager.agents_status.copy(),
                        }
                    )
                except Exception:
                    pass

            display_manager.set_agent_status = wrapped_set_status

            original_update_stats = display_manager.update_token_stats

            def wrapped_update_stats(summary: dict[str, Any]):
                original_update_stats(summary)
                try:
                    stats_copy = display_manager.stats.copy()
                    logger.debug(
                        f"Sending token_stats: model={stats_copy.get('model')}, calls={stats_copy.get('calls')}, cost={stats_copy.get('cost')}"
                    )
                    log_queue.put_nowait({"type": "token_stats", "stats": stats_copy})
                except Exception as e:
                    logger.debug(f"Failed to send token_stats: {e}")

            display_manager.update_token_stats = wrapped_update_stats

            if hasattr(solver, "token_tracker") and solver.token_tracker:
                solver.token_tracker.set_on_usage_added_callback(wrapped_update_stats)

        def send_progress_update(stage: str, progress: dict[str, Any]):
            try:
                log_queue.put_nowait({"type": "progress", "stage": stage, "progress": progress})
            except Exception:
                pass

        solver._send_progress_update = send_progress_update

        pusher_task = asyncio.create_task(log_pusher())

        loop = asyncio.get_running_loop()

        def emit_process_log(event):
            loop.call_soon_threadsafe(log_queue.put_nowait, event.to_dict())

        with bind_log_context(
            task_id=task_id,
            session_id=session_id,
            capability="deep_solve",
            sink="ui",
        ):
            process_logs = capture_process_logs(emit_process_log, task_id=task_id)
            with process_logs:
                await safe_send_json({"type": "status", "content": "started"})

                if display_manager:
                    await safe_send_json(
                        {
                            "type": "agent_status",
                            "agent": "all",
                            "status": "initial",
                            "all_agents": display_manager.agents_status.copy(),
                        }
                    )
                    await safe_send_json(
                        {"type": "token_stats", "stats": display_manager.stats.copy()}
                    )

                logger.info(f"[{task_id}] Solving started")

                result = await solver.solve(question, verbose=True, detailed=detailed_answer)

                logger.info(f"[{task_id}] Solving completed")
                task_manager.update_task_status(task_id, "completed")

            final_answer = result.get("final_answer", "")
            output_dir_str = result.get("output_dir", "")

            if output_dir_str and final_answer:
                try:
                    output_dir = Path(output_dir_str)

                    if not output_dir.is_absolute():
                        output_dir = output_dir.resolve()

                    path_str = str(output_dir).replace("\\", "/")
                    parts = path_str.split("/")

                    if "user" in parts:
                        idx = parts.index("user")
                        rel_path = "/".join(parts[idx + 1 :])
                        base_url = f"/api/outputs/{rel_path}"

                        pattern = r"\]\(artifacts/([^)]+)\)"
                        replacement = rf"]({base_url}/artifacts/\1)"
                        final_answer = re.sub(pattern, replacement, final_answer)
                except Exception as e:
                    logger.debug(f"Error processing image paths: {e}")

            if display_manager:
                final_agent_status = dict.fromkeys(display_manager.agents_status.keys(), "done")
                await safe_send_json(
                    {
                        "type": "agent_status",
                        "agent": "all",
                        "status": "complete",
                        "all_agents": final_agent_status,
                    }
                )

            dir_name = ""
            if output_dir_str:
                parts = output_dir_str.replace("\\", "/").split("/")
                dir_name = parts[-1] if parts else ""

            final_res = {
                "type": "result",
                "session_id": session_id,
                "final_answer": final_answer,
                "output_dir": output_dir_str,
                "output_dir_name": dir_name,
                "metadata": result.get("metadata"),
            }
            await safe_send_json(final_res)

            if session_id:
                sm.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=final_answer,
                    output_dir=dir_name,
                )
                if display_manager:
                    sm.update_token_stats(
                        session_id=session_id,
                        token_stats=display_manager.stats.copy(),
                    )

    except Exception as e:
        connection_closed.set()
        await safe_send_json({"type": "error", "content": str(e)})
        logger.error(f"[{task_id if 'task_id' in locals() else 'unknown'}] Solving failed: {e}")
        if "task_id" in locals():
            task_manager.update_task_status(task_id, "error", error=str(e))
    finally:
        connection_closed.set()
        if pusher_task:
            pusher_task.cancel()
            try:
                await pusher_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"Error waiting for pusher task: {e}")

        try:
            if hasattr(websocket, "client_state"):
                state = websocket.client_state
                if hasattr(state, "name") and state.name != "DISCONNECTED":
                    await websocket.close()
            else:
                await websocket.close()
        except (WebSocketDisconnect, RuntimeError, ConnectionError):
            pass
        except Exception as e:
            logger.debug(f"Error closing WebSocket: {e}")

        if user_token is not None:
            try:
                reset_current_user(user_token)
            except Exception:
                pass
