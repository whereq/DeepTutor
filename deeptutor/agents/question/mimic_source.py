"""Exam-paper → QuizTemplate adapter for mimic mode.

Wraps the (sync, IO-heavy) MinerU PDF parser + the rule-based question
extractor so the capability layer can hand mimic templates to
:class:`QuestionPipeline` via its ``templates_override`` entry.

This module is intentionally narrow: it ONLY converts a PDF (or a
previously-parsed working directory) into a list of
:class:`QuizTemplate`. Streaming progress, prompt assembly, LLM calls,
and result emission all stay in the pipeline / capability layers.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from deeptutor.agents.question.pipeline import QuizTemplate
from deeptutor.tools.question.pdf_parser import parse_pdf_with_mineru
from deeptutor.tools.question.question_extractor import extract_questions_from_paper

logger = logging.getLogger(__name__)


_DEFAULT_DIFFICULTY = "medium"
_DEFAULT_QUESTION_TYPE = "written"
_TOPIC_CLIP_CHARS = 240


async def parse_exam_paper_to_templates(
    paper_path: str | Path,
    *,
    max_questions: int,
    paper_mode: str,
    output_dir: str | Path,
) -> tuple[list[QuizTemplate], dict[str, str]]:
    """Resolve an exam paper into a list of mimic-mode ``QuizTemplate``\\ s.

    ``paper_mode``:

    * ``"upload"``  — ``paper_path`` is a freshly-uploaded PDF; MinerU
      parses it under ``output_dir`` and we pick the newest subdir.
    * ``"parsed"``  — ``paper_path`` is a previously-parsed working dir
      (already contains the MinerU output); skip the parse step.

    Returns ``(templates, trace)``. ``trace`` carries paths + counts for
    inclusion in the final ``stream.result`` envelope. Raises
    ``RuntimeError`` when parsing or extraction fails — the caller emits
    a user-facing error.
    """
    return await asyncio.to_thread(
        _parse_sync,
        Path(paper_path),
        int(max_questions),
        str(paper_mode),
        Path(output_dir),
    )


def _parse_sync(
    paper_path: Path,
    max_questions: int,
    paper_mode: str,
    output_base: Path,
) -> tuple[list[QuizTemplate], dict[str, str]]:
    output_base.mkdir(parents=True, exist_ok=True)

    if paper_mode == "parsed":
        working_dir = paper_path
    else:
        ok = parse_pdf_with_mineru(str(paper_path), str(output_base))
        if not ok:
            raise RuntimeError("Failed to parse exam paper with MinerU")
        subdirs = sorted(
            [d for d in output_base.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        if not subdirs:
            raise RuntimeError("No parsed exam directory found after MinerU parsing")
        working_dir = subdirs[0]

    json_files = list(working_dir.glob("*_questions.json"))
    if not json_files:
        ok = extract_questions_from_paper(str(working_dir), output_dir=None)
        if not ok:
            raise RuntimeError("Failed to extract questions from parsed exam")
        json_files = list(working_dir.glob("*_questions.json"))
    if not json_files:
        raise RuntimeError("Question extraction output not found")

    with json_files[0].open(encoding="utf-8") as fh:
        payload = json.load(fh)
    questions = payload.get("questions") or []
    if max_questions > 0:
        questions = questions[:max_questions]

    templates: list[QuizTemplate] = []
    for idx, item in enumerate(questions, 1):
        if not isinstance(item, dict):
            continue
        q_text = str(item.get("question_text") or "").strip()
        if not q_text:
            continue
        templates.append(
            QuizTemplate(
                question_id=f"q_{idx}",
                topic=q_text[:_TOPIC_CLIP_CHARS],
                question_type=str(item.get("question_type") or _DEFAULT_QUESTION_TYPE).lower(),
                difficulty=_DEFAULT_DIFFICULTY,
                source="mimic",
                reference_question=q_text,
                reference_answer=str(item.get("answer") or "").strip() or None,
            )
        )

    trace = {
        "paper_dir": str(working_dir),
        "question_file": str(json_files[0]),
        "template_count": str(len(templates)),
    }
    return templates, trace


__all__ = ["parse_exam_paper_to_templates"]
