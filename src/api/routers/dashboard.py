"""
Dashboard API Router
====================

Provides endpoints for retrieving recent activities aggregated from various
agent modules (solve, chat, question, research).

Activities are aggregated from:
- Solve sessions (data/user/agent/solve/sessions.json)
- Chat sessions (data/user/agent/chat/sessions.json)
- Question batches (data/user/agent/question/*/summary.json)
- Research reports (data/user/agent/research/reports/*_metadata.json)
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from src.agents.chat import SessionManager
from src.agents.solve import SolverSessionManager
from src.services.path_service import get_path_service

router = APIRouter()

# Initialize session managers
_solve_session_manager: SolverSessionManager | None = None
_chat_session_manager: SessionManager | None = None


def _get_solve_session_manager() -> SolverSessionManager:
    """Lazy initialization of solve session manager."""
    global _solve_session_manager
    if _solve_session_manager is None:
        _solve_session_manager = SolverSessionManager()
    return _solve_session_manager


def _get_chat_session_manager() -> SessionManager:
    """Lazy initialization of chat session manager."""
    global _chat_session_manager
    if _chat_session_manager is None:
        _chat_session_manager = SessionManager()
    return _chat_session_manager


def _get_question_activities(limit: int = 50) -> list[dict[str, Any]]:
    """
    Get recent question generation activities from batch directories.
    
    Reads summary.json from each batch directory to extract activity info.
    """
    activities = []
    path_service = get_path_service()
    question_dir = path_service.get_question_dir()
    
    if not question_dir.exists():
        return activities
    
    # Find all batch directories
    batch_dirs = sorted(
        [d for d in question_dir.iterdir() if d.is_dir() and d.name.startswith("batch_")],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )[:limit]
    
    for batch_dir in batch_dirs:
        summary_file = batch_dir / "summary.json"
        if summary_file.exists():
            try:
                with open(summary_file, encoding="utf-8") as f:
                    summary = json.load(f)
                
                activities.append({
                    "id": batch_dir.name,
                    "type": "question",
                    "title": summary.get("knowledge_point", batch_dir.name),
                    "timestamp": batch_dir.stat().st_mtime,
                    "summary": f"Generated {summary.get('generated', 0)} question(s)",
                    "session_ref": f"question/{batch_dir.name}",
                })
            except (json.JSONDecodeError, OSError):
                # Skip invalid files
                pass
    
    return activities


def _get_research_activities(limit: int = 50) -> list[dict[str, Any]]:
    """
    Get recent research activities from reports directory.
    
    Reads metadata files from the reports directory.
    """
    activities = []
    path_service = get_path_service()
    reports_dir = path_service.get_research_reports_dir()
    
    if not reports_dir.exists():
        return activities
    
    # Find all metadata files
    metadata_files = sorted(
        [f for f in reports_dir.iterdir() if f.name.endswith("_metadata.json")],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )[:limit]
    
    for meta_file in metadata_files:
        try:
            with open(meta_file, encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Extract research_id from filename (research_YYYYMMDD_HHMMSS_id_metadata.json)
            research_id = meta_file.stem.replace("_metadata", "")
            
            activities.append({
                "id": research_id,
                "type": "research",
                "title": metadata.get("topic", research_id),
                "timestamp": meta_file.stat().st_mtime,
                "summary": f"Word count: {metadata.get('report_word_count', 0)}",
                "session_ref": f"research/{research_id}",
            })
        except (json.JSONDecodeError, OSError):
            # Skip invalid files
            pass
    
    return activities


@router.get("/recent")
async def get_recent_activities(limit: int = 50, type: str | None = None):
    """
    Get recent activities aggregated from all agent modules.
    
    Args:
        limit: Maximum number of activities to return
        type: Optional filter by activity type (solve, chat, question, research)
    
    Returns:
        List of activity entries sorted by timestamp (newest first)
    """
    activities: list[dict[str, Any]] = []
    
    # Aggregate from solve sessions
    if type is None or type == "solve":
        solve_manager = _get_solve_session_manager()
        solve_sessions = solve_manager.list_sessions(limit=limit, include_messages=False)
        for s in solve_sessions:
            activities.append({
                "id": s.get("session_id"),
                "type": "solve",
                "title": s.get("title", "Untitled"),
                "timestamp": s.get("updated_at", s.get("created_at", 0)),
                "summary": s.get("last_message", "")[:100] if s.get("last_message") else "",
                "session_ref": f"solve/{s.get('session_id')}",
                "message_count": s.get("message_count", 0),
                "kb_name": s.get("kb_name"),
                "token_stats": s.get("token_stats"),
            })
    
    # Aggregate from chat sessions
    if type is None or type == "chat":
        chat_manager = _get_chat_session_manager()
        chat_sessions = chat_manager.list_sessions(limit=limit, include_messages=False)
        for s in chat_sessions:
            activities.append({
                "id": s.get("session_id"),
                "type": "chat",
                "title": s.get("title", "Untitled"),
                "timestamp": s.get("updated_at", s.get("created_at", 0)),
                "summary": s.get("last_message", "")[:100] if s.get("last_message") else "",
                "session_ref": f"chat/{s.get('session_id')}",
                "message_count": s.get("message_count", 0),
                "settings": s.get("settings"),
            })
    
    # Aggregate from question batches
    if type is None or type == "question":
        question_activities = _get_question_activities(limit)
        activities.extend(question_activities)
    
    # Aggregate from research reports
    if type is None or type == "research":
        research_activities = _get_research_activities(limit)
        activities.extend(research_activities)
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return activities[:limit]


@router.get("/{entry_id}")
async def get_activity_entry(entry_id: str):
    """
    Get a specific activity entry by ID.
    
    Args:
        entry_id: The activity/session ID
    
    Returns:
        The full activity entry
    
    Raises:
        HTTPException: If entry not found
    """
    # Try to find in solve sessions
    if entry_id.startswith("solve_"):
        solve_manager = _get_solve_session_manager()
        session = solve_manager.get_session(entry_id)
        if session:
            return {
                "id": session.get("session_id"),
                "type": "solve",
                "title": session.get("title"),
                "timestamp": session.get("updated_at", session.get("created_at")),
                "content": {
                    "messages": session.get("messages", []),
                    "kb_name": session.get("kb_name"),
                    "token_stats": session.get("token_stats"),
                },
            }
    
    # Try to find in chat sessions
    if entry_id.startswith("chat_"):
        chat_manager = _get_chat_session_manager()
        session = chat_manager.get_session(entry_id)
        if session:
            return {
                "id": session.get("session_id"),
                "type": "chat",
                "title": session.get("title"),
                "timestamp": session.get("updated_at", session.get("created_at")),
                "content": {
                    "messages": session.get("messages", []),
                    "settings": session.get("settings"),
                },
            }
    
    # Try to find in question batches
    if entry_id.startswith("batch_"):
        path_service = get_path_service()
        batch_dir = path_service.get_question_dir() / entry_id
        summary_file = batch_dir / "summary.json"
        if summary_file.exists():
            try:
                with open(summary_file, encoding="utf-8") as f:
                    summary = json.load(f)
                return {
                    "id": entry_id,
                    "type": "question",
                    "title": summary.get("knowledge_point", entry_id),
                    "timestamp": batch_dir.stat().st_mtime,
                    "content": summary,
                }
            except (json.JSONDecodeError, OSError):
                pass
    
    # Try to find in research reports
    if entry_id.startswith("research_"):
        path_service = get_path_service()
        reports_dir = path_service.get_research_reports_dir()
        meta_file = reports_dir / f"{entry_id}_metadata.json"
        report_file = reports_dir / f"{entry_id}.md"
        
        if meta_file.exists():
            try:
                with open(meta_file, encoding="utf-8") as f:
                    metadata = json.load(f)
                
                report_content = ""
                if report_file.exists():
                    with open(report_file, encoding="utf-8") as f:
                        report_content = f.read()
                
                return {
                    "id": entry_id,
                    "type": "research",
                    "title": metadata.get("topic", entry_id),
                    "timestamp": meta_file.stat().st_mtime,
                    "content": {
                        "metadata": metadata,
                        "report": report_content,
                    },
                }
            except (json.JSONDecodeError, OSError):
                pass
    
    raise HTTPException(status_code=404, detail="Entry not found")
