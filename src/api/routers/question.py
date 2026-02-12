from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agents.question import AgentCoordinator
from src.api.utils.task_id_manager import TaskIDManager
from src.logging import get_logger
from src.services.config import load_config_with_main
from src.services.llm.config import get_llm_config
from src.services.path_service import get_path_service
from src.services.settings.interface_settings import get_ui_language
from src.utils.document_validator import DocumentValidator
from src.utils.error_utils import format_exception_message

router = APIRouter()

project_root = Path(__file__).parent.parent.parent.parent
config = load_config_with_main("question_config.yaml", project_root)
log_dir = config.get("paths", {}).get("user_log_dir") or config.get("logging", {}).get("log_dir")
logger = get_logger("QuestionAPI", log_dir=log_dir)

path_service = get_path_service()
QUESTION_OUTPUT_DIR = path_service.get_question_dir()
MIMIC_OUTPUT_DIR = QUESTION_OUTPUT_DIR / "mimic_papers"


def _build_coordinator(kb_name: str) -> AgentCoordinator:
    try:
        llm_config = get_llm_config()
        return AgentCoordinator(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            api_version=getattr(llm_config, "api_version", None),
            kb_name=kb_name,
            output_dir=str(QUESTION_OUTPUT_DIR),
            language=get_ui_language(default=config.get("system", {}).get("language", "en")),
        )
    except Exception:
        return AgentCoordinator(
            kb_name=kb_name,
            output_dir=str(QUESTION_OUTPUT_DIR),
            language=get_ui_language(default=config.get("system", {}).get("language", "en")),
        )


@router.websocket("/generate")
async def websocket_question_generate(websocket: WebSocket) -> None:
    await websocket.accept()
    task_manager = TaskIDManager.get_instance()
    try:
        data = await websocket.receive_json()
        requirement = data.get("requirement") or {}
        kb_name = data.get("kb_name", "ai_textbook")
        count = int(data.get("count", 1))

        user_topic = str(requirement.get("knowledge_point", "")).strip()
        preference = str(requirement.get("additional_requirements", "")).strip()
        difficulty = str(requirement.get("difficulty", "")).strip()
        question_type = str(requirement.get("question_type", "")).strip()
        if not user_topic:
            await websocket.send_json({"type": "error", "content": "knowledge_point is required"})
            return

        task_key = f"question_{kb_name}_{hash(str(requirement))}"
        task_id = task_manager.generate_task_id("question_gen", task_key)
        await websocket.send_json({"type": "task_id", "task_id": task_id})

        coordinator = _build_coordinator(kb_name)

        async def ws_callback(data: dict) -> None:
            await websocket.send_json(data)

        coordinator.set_ws_callback(ws_callback)
        await websocket.send_json({"type": "status", "content": "started"})

        summary = await coordinator.generate_from_topic(
            user_topic=user_topic,
            preference=preference,
            num_questions=count,
            difficulty=difficulty,
            question_type=question_type,
        )

        await websocket.send_json(
            {
                "type": "batch_summary",
                "requested": summary.get("requested", count),
                "completed": summary.get("completed", 0),
                "failed": summary.get("failed", 0),
                "templates": summary.get("templates", []),
            }
        )
        await websocket.send_json({"type": "complete"})
        task_manager.update_task_status(task_id, "completed")
    except WebSocketDisconnect:
        logger.debug("Client disconnected from /question/generate")
    except Exception as exc:
        logger.error(f"/question/generate failed: {exc}\n{traceback.format_exc()}")
        error_msg = format_exception_message(exc)
        try:
            await websocket.send_json({"type": "error", "content": error_msg})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/mimic")
async def websocket_mimic_generate(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        mode = data.get("mode", "parsed")  # upload | parsed
        kb_name = data.get("kb_name", "ai_textbook")
        max_questions = int(data.get("max_questions", 10))

        coordinator = _build_coordinator(kb_name)

        async def ws_callback(data: dict) -> None:
            await websocket.send_json(data)

        coordinator.set_ws_callback(ws_callback)

        paper_mode = "parsed"
        exam_path = ""

        if mode == "upload":
            pdf_data = data.get("pdf_data")
            pdf_name = data.get("pdf_name", "exam.pdf")
            if not pdf_data:
                await websocket.send_json({"type": "error", "content": "pdf_data is required"})
                return

            try:
                pdf_bytes = base64.b64decode(pdf_data)
            except Exception as exc:
                await websocket.send_json({"type": "error", "content": f"Invalid PDF encoding: {exc}"})
                return

            safe_name = DocumentValidator.validate_upload_safety(pdf_name, len(pdf_bytes), {".pdf"})
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_dir = MIMIC_OUTPUT_DIR / f"mimic_{ts}_{Path(safe_name).stem}"
            batch_dir.mkdir(parents=True, exist_ok=True)

            pdf_path = batch_dir / safe_name
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            DocumentValidator.validate_file(pdf_path)

            paper_mode = "upload"
            exam_path = str(pdf_path)
        elif mode == "parsed":
            paper_path = str(data.get("paper_path", "")).strip()
            if not paper_path:
                await websocket.send_json({"type": "error", "content": "paper_path is required"})
                return
            paper_mode = "parsed"
            exam_path = paper_path
        else:
            await websocket.send_json({"type": "error", "content": f"Unknown mode: {mode}"})
            return

        await websocket.send_json({"type": "status", "content": "started"})
        summary = await coordinator.generate_from_exam(
            exam_paper_path=exam_path,
            max_questions=max_questions,
            paper_mode=paper_mode,
        )

        await websocket.send_json(
            {
                "type": "batch_summary",
                "requested": max_questions,
                "completed": summary.get("completed", 0),
                "failed": summary.get("failed", 0),
                "templates": summary.get("templates", []),
            }
        )
        await websocket.send_json({"type": "complete"})
    except WebSocketDisconnect:
        logger.debug("Client disconnected from /question/mimic")
    except Exception as exc:
        logger.error(f"/question/mimic failed: {exc}\n{traceback.format_exc()}")
        try:
            await websocket.send_json({"type": "error", "content": format_exception_message(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
