#!/usr/bin/env python
"""
Benchmark Evaluator - Independent metric evaluation (no weighted merge)

Metrics (turn-level):
1) Gap tracking (LLM, per tutor turn): mentioned vs newly resolved gaps
2) Source faithfulness (LLM, per tutor turn): 1-5 score against source text
3) Teaching quality (LLM, per tutor turn): insightfulness + applicability (1-5)
4) Turn count (non-LLM): student/tutor interaction counts

Metrics (practice questions, session-level):
5) Practice question evaluation (LLM):
   - gap_coverage (set-level, 1-5)
   - difficulty_fit_delta (per-question, -5 to +5)
   - groundedness (per-question, 1-5)
   - diversity (set-level, 1-5)
   - distractor_quality (per-question, 1-5)

Supports:
- Single-session transcript: {"transcript": [...], "entry": {...}}
- Multi-session transcript: {"sessions": [{"transcript": [...], "entry": {...}, ...}, ...]}
"""

import json
import logging
from pathlib import Path

from benchmark.data_generation.llm_utils import call_llm_json, extract_json, load_prompt

logger = logging.getLogger("benchmark.evaluation")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RECENT_CONTEXT_WINDOW = 8  # messages (student+tutor) to provide around each turn


def _format_profile(profile: dict) -> str:
    """Format student profile for prompt."""
    parts = []
    if profile.get("personality"):
        parts.append(f"Personality: {profile['personality']}")
    if profile.get("education_background"):
        parts.append(f"Background: {profile['education_background']}")
    if profile.get("learning_purpose"):
        parts.append(f"Purpose: {profile['learning_purpose']}")
    ks = profile.get("knowledge_state", {})
    if ks.get("known_well"):
        parts.append(f"Known well: {', '.join(ks['known_well'][:5])}")
    if ks.get("partially_known"):
        parts.append(f"Partially known: {', '.join(ks['partially_known'][:5])}")
    if ks.get("unknown"):
        parts.append(f"Unknown: {', '.join(ks['unknown'][:5])}")
    if profile.get("beliefs"):
        parts.append(f"Beliefs (may be misconceptions): {profile['beliefs']}")
    return "\n".join(parts) if parts else "(no profile)"


def _format_task(task: dict) -> str:
    """Format task for prompt."""
    parts = []
    if task.get("title"):
        parts.append(f"Title: {task['title']}")
    if task.get("description"):
        parts.append(f"Description: {task['description']}")
    if task.get("success_criteria"):
        parts.append(f"Success criteria: {task['success_criteria']}")
    if task.get("target_gaps"):
        parts.append(f"Target gaps: {task['target_gaps']}")
    return "\n".join(parts) if parts else "(no task)"


def _normalize_source_by_page(source_content: dict | None) -> dict[int, str]:
    """Normalize source_content keys to int (JSON may have str page keys)."""
    if not source_content:
        return {}
    out = {}
    for k, v in source_content.items():
        pk = int(k) if isinstance(k, str) and k.isdigit() else k
        if isinstance(pk, int):
            out[pk] = v or ""
    return out


def _format_transcript(transcript: list[dict]) -> str:
    """Format transcript for prompt."""
    lines = []
    for i, msg in enumerate(transcript, 1):
        role = msg.get("role", "?")
        content = (msg.get("content", "") or "")[:900]
        if len((msg.get("content") or "")) > 900:
            content += "..."
        lines.append(f"[{i}] {role.upper()}: {content}")
    return "\n\n".join(lines) if lines else "(empty)"


def _filter_dialog_messages(transcript: list[dict]) -> list[dict]:
    """Keep only student/tutor messages for evaluation scope."""
    return [m for m in transcript if m.get("role") in {"student", "tutor"}]


def _extract_turn_pairs(dialog_msgs: list[dict]) -> list[dict]:
    """
    Build per-turn student->tutor pairs.

    Returns list of:
      {
        "turn_index": int,
        "student_message": str,
        "tutor_response": str,
        "student_msg_index": int,   # index in dialog_msgs
      }
    """
    turns: list[dict] = []
    turn_index = 0
    for i in range(len(dialog_msgs) - 1):
        a, b = dialog_msgs[i], dialog_msgs[i + 1]
        if a.get("role") == "student" and b.get("role") == "tutor":
            turn_index += 1
            turns.append(
                {
                    "turn_index": turn_index,
                    "student_message": a.get("content", ""),
                    "tutor_response": b.get("content", ""),
                    "student_msg_index": i,
                }
            )
    return turns


def _get_recent_context(dialog_msgs: list[dict], student_msg_index: int, window: int = RECENT_CONTEXT_WINDOW) -> str:
    """
    Return recent context ending at current student message.

    This intentionally provides more than just current turn for metric-1 robustness.
    """
    start = max(0, student_msg_index - window + 1)
    snippet = dialog_msgs[start : student_msg_index + 1]
    return _format_transcript(snippet)


def _build_gap_map(gaps: list[dict]) -> dict[str, dict]:
    """Build gap_id -> gap dict mapping."""
    out = {}
    for g in gaps:
        gid = str(g.get("gap_id", "")).strip()
        if gid:
            out[gid] = g
    return out


def _format_gap_catalog(gaps: list[dict]) -> str:
    """Format full gap catalog for metric-1 prompt."""
    if not gaps:
        return "(no gaps)"
    lines = []
    for g in gaps:
        gid = g.get("gap_id", "unknown")
        concept = g.get("target_concept", "?")
        desc = (g.get("description", "") or "")[:350]
        mani = (g.get("manifestation", "") or "")[:240]
        corr = (g.get("correct_understanding", "") or "")[:320]
        lines.append(
            f"- gap_id: {gid}\n"
            f"  concept: {concept}\n"
            f"  description: {desc}\n"
            f"  manifestation: {mani}\n"
            f"  expected_correct_understanding: {corr}"
        )
    return "\n".join(lines)


def _format_mentioned_gaps_with_source(mentioned_gap_ids: list[str], gap_by_id: dict[str, dict], source_content: dict | None) -> str:
    """Format only mentioned gaps and their source excerpts for metric-2."""
    if not mentioned_gap_ids:
        return "(no mentioned gaps)"

    src_by_page = _normalize_source_by_page(source_content)
    lines = []
    for gid in mentioned_gap_ids:
        gap = gap_by_id.get(gid)
        if not gap:
            continue
        concept = gap.get("target_concept", "?")
        desc = (gap.get("description", "") or "")[:260]
        lines.append(f"### {gid} - {concept}")
        lines.append(f"Description: {desc}")
        pages = sorted(set(gap.get("source_pages", [])))
        if pages:
            lines.append(f"Source pages: {pages}")
        for p in pages:
            text = src_by_page.get(p, "")
            if text:
                excerpt = text[:1800] + ("..." if len(text) > 1800 else "")
                lines.append(f"Source page {p}:\n{excerpt}")
        lines.append("")
    return "\n".join(lines).strip() or "(no source excerpt for mentioned gaps)"


async def evaluate_gap_tracking_turn(
    *,
    entry: dict,
    turn_index: int,
    student_message: str,
    tutor_response: str,
    recent_context: str,
    previously_mentioned_gap_ids: list[str],
    previously_resolved_gap_ids: list[str],
    temperature: float,
) -> dict:
    """
    Metric-1 (LLM): detect mentioned gaps and newly resolved gaps on this tutor turn.

    Strict resolution is enforced in prompt:
      - "resolved" requires clear correction + concrete closure evidence, not a casual mention.
    """
    prompt_cfg = load_prompt("eval_gap_tracking_turn")
    profile = entry.get("profile", {})
    gaps = entry.get("gaps", [])
    task = entry.get("task", {})
    gap_by_id = _build_gap_map(gaps)
    valid_gap_ids = set(gap_by_id.keys())
    unresolved = valid_gap_ids - set(previously_resolved_gap_ids)

    user_prompt = prompt_cfg["user_template"].format(
        profile_summary=_format_profile(profile),
        task_summary=_format_task(task),
        gap_catalog=_format_gap_catalog(gaps),
        recent_context=recent_context,
        student_message=student_message,
        tutor_response=tutor_response,
        turn_index=turn_index,
        previously_mentioned_gap_ids=sorted(set(previously_mentioned_gap_ids)),
        previously_resolved_gap_ids=sorted(set(previously_resolved_gap_ids)),
    )

    try:
        result = await call_llm_json(
            user_prompt=user_prompt,
            system_prompt=prompt_cfg["system"],
            temperature=temperature,
            max_tokens=1024,
        )
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Gap tracking failed at turn %d: %s", turn_index, e)
        return {
            "turn_index": turn_index,
            "mentioned_gap_ids": [],
            "resolved_gap_ids_new": [],
            "rationale": f"Evaluation failed: {e}",
            "error": str(e),
        }

    mentioned = [gid for gid in result.get("mentioned_gap_ids", []) if gid in valid_gap_ids]
    mentioned = sorted(set(mentioned))

    resolved_new_raw = [gid for gid in result.get("resolved_gap_ids_new", []) if gid in unresolved]
    resolved_new = sorted(set(resolved_new_raw))
    # Resolved should be a subset of mentioned on this turn for consistency.
    resolved_new = [gid for gid in resolved_new if gid in mentioned]

    return {
        "turn_index": turn_index,
        "mentioned_gap_ids": mentioned,
        "resolved_gap_ids_new": resolved_new,
        "rationale": result.get("rationale", ""),
    }


async def evaluate_source_faithfulness_turn(
    *,
    turn_index: int,
    student_message: str,
    tutor_response: str,
    recent_context: str,
    mentioned_gap_ids: list[str],
    gap_by_id: dict[str, dict],
    source_content: dict | None,
    temperature: float,
) -> dict:
    """
    Metric-2 (LLM): faithfulness (1-5) against source text of mentioned gaps only.
    """
    if not mentioned_gap_ids:
        return {
            "turn_index": turn_index,
            "mentioned_gap_ids": [],
            "not_applicable": True,
            "reason": "No mentioned gaps on this turn.",
        }

    prompt_cfg = load_prompt("eval_source_faithfulness_turn")
    source_for_mentioned = _format_mentioned_gaps_with_source(mentioned_gap_ids, gap_by_id, source_content)
    if source_for_mentioned.startswith("(no source excerpt"):
        return {
            "turn_index": turn_index,
            "mentioned_gap_ids": mentioned_gap_ids,
            "not_applicable": True,
            "reason": "Mentioned gaps have no usable source excerpts.",
        }

    user_prompt = prompt_cfg["user_template"].format(
        turn_index=turn_index,
        recent_context=recent_context,
        student_message=student_message,
        tutor_response=tutor_response,
        mentioned_gap_ids=mentioned_gap_ids,
        source_content_for_mentioned_gaps=source_for_mentioned,
    )

    try:
        result = await call_llm_json(
            user_prompt=user_prompt,
            system_prompt=prompt_cfg["system"],
            temperature=temperature,
            max_tokens=900,
        )
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Source faithfulness failed at turn %d: %s", turn_index, e)
        return {
            "turn_index": turn_index,
            "mentioned_gap_ids": mentioned_gap_ids,
            "not_applicable": True,
            "reason": f"Evaluation failed: {e}",
            "error": str(e),
        }

    score = result.get("faithfulness_score")
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = None
    if score is not None:
        score = max(1, min(5, score))

    return {
        "turn_index": turn_index,
        "mentioned_gap_ids": mentioned_gap_ids,
        "faithfulness_score": score,
        "rationale": result.get("rationale", ""),
        "contradictions": result.get("contradictions", result.get("unsupported_claims", [])),
        "not_applicable": score is None,
    }


def _build_source_faithfulness_summary(per_turn: list[dict]) -> dict:
    """Aggregate metric-2 stats: min/max/avg over scored turns only."""
    scored = [t["faithfulness_score"] for t in per_turn if not t.get("not_applicable") and t.get("faithfulness_score") is not None]
    if not scored:
        return {
            "scale": "1-5",
            "num_scored_turns": 0,
            "max_score": None,
            "min_score": None,
            "avg_score": None,
            "per_turn": per_turn,
        }
    return {
        "scale": "1-5",
        "num_scored_turns": len(scored),
        "max_score": max(scored),
        "min_score": min(scored),
        "avg_score": round(sum(scored) / len(scored), 2),
        "per_turn": per_turn,
    }


async def evaluate_teaching_quality_turn(
    *,
    turn_index: int,
    student_message: str,
    tutor_response: str,
    recent_context: str,
    temperature: float,
) -> dict:
    """
    Metric-3 (LLM): turn-level teaching quality on two dimensions:
      - insightfulness (1-5)
      - applicability (1-5)
    """
    prompt_cfg = load_prompt("eval_teaching_quality_turn")
    user_prompt = prompt_cfg["user_template"].format(
        turn_index=turn_index,
        recent_context=recent_context,
        student_message=student_message,
        tutor_response=tutor_response,
    )

    try:
        result = await call_llm_json(
            user_prompt=user_prompt,
            system_prompt=prompt_cfg["system"],
            temperature=temperature,
            max_tokens=700,
        )
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Teaching quality failed at turn %d: %s", turn_index, e)
        return {
            "turn_index": turn_index,
            "insightfulness_score": None,
            "applicability_score": None,
            "rationale": f"Evaluation failed: {e}",
            "not_applicable": True,
            "error": str(e),
        }

    insight = result.get("insightfulness_score")
    applicability = result.get("applicability_score")
    try:
        insight = int(insight) if insight is not None else None
    except (TypeError, ValueError):
        insight = None
    try:
        applicability = int(applicability) if applicability is not None else None
    except (TypeError, ValueError):
        applicability = None

    if insight is not None:
        insight = max(1, min(5, insight))
    if applicability is not None:
        applicability = max(1, min(5, applicability))

    return {
        "turn_index": turn_index,
        "insightfulness_score": insight,
        "applicability_score": applicability,
        "rationale": result.get("rationale", ""),
        "evidence": result.get("evidence", []),
        "not_applicable": insight is None and applicability is None,
    }


def _build_teaching_quality_summary(per_turn: list[dict]) -> dict:
    """Aggregate metric-3 stats over scored turns only."""
    insight_scores = [
        t.get("insightfulness_score")
        for t in per_turn
        if t.get("insightfulness_score") is not None and not t.get("not_applicable")
    ]
    applicability_scores = [
        t.get("applicability_score")
        for t in per_turn
        if t.get("applicability_score") is not None and not t.get("not_applicable")
    ]
    return {
        "scale": "1-5",
        "num_scored_turns_insightfulness": len(insight_scores),
        "num_scored_turns_applicability": len(applicability_scores),
        "avg_insightfulness": (
            round(sum(insight_scores) / len(insight_scores), 2)
            if insight_scores
            else None
        ),
        "avg_applicability": (
            round(sum(applicability_scores) / len(applicability_scores), 2)
            if applicability_scores
            else None
        ),
        "max_insightfulness": max(insight_scores) if insight_scores else None,
        "min_insightfulness": min(insight_scores) if insight_scores else None,
        "max_applicability": max(applicability_scores) if applicability_scores else None,
        "min_applicability": min(applicability_scores) if applicability_scores else None,
        "per_turn": per_turn,
    }


# ======================================================================
# Practice question evaluation (session-level, 5 metrics)
# ======================================================================

def _format_gaps_with_source_for_pq(gaps: list[dict], source_content: dict | None) -> str:
    """Format gaps + their source pages for practice question groundedness evaluation."""
    src_by_page = _normalize_source_by_page(source_content)
    lines = []
    for g in gaps:
        gid = g.get("gap_id", "?")
        concept = g.get("target_concept", "?")
        desc = (g.get("description", "") or "")[:300]
        correct = (g.get("correct_understanding", "") or "")[:300]
        lines.append(f"### {gid} - {concept}")
        lines.append(f"Description: {desc}")
        if correct:
            lines.append(f"Correct understanding: {correct}")
        pages = sorted(set(g.get("source_pages", [])))
        for p in pages:
            text = src_by_page.get(p, "")
            if text:
                excerpt = text[:1500] + ("..." if len(text) > 1500 else "")
                lines.append(f"Source page {p}:\n{excerpt}")
        lines.append("")
    return "\n".join(lines).strip() or "(no source content)"


def _clamp_score(raw, lo: int = 1, hi: int = 5) -> int | None:
    if raw is None:
        return None
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, v))


async def _eval_pq_gap_coverage(
    questions_block: str,
    gaps: list[dict],
    temperature: float,
) -> dict:
    """Set-level: how well the full question set covers each gap (1-5)."""
    from src.services.llm import factory

    gap_view = [
        {"gap_id": g.get("gap_id", ""), "type": g.get("type", ""),
         "target_concept": g.get("target_concept", ""), "description": g.get("description", "")}
        for g in gaps
    ]
    prompt = (
        "Evaluate the following PRACTICE QUESTION SET as a whole.\n\n"
        f"Question set:\n{questions_block}\n\n"
        f"Knowledge gaps:\n{json.dumps(gap_view, ensure_ascii=False, indent=2)}\n\n"
        "Return strict JSON only:\n"
        '{"gap_scores": {"gap_id": 1-5, "...": 1-5}, "rationale": "short reason"}\n\n'
        "Scoring guide:\n"
        "- For EACH gap, score how well the FULL question set covers that gap.\n"
        "- 1 means almost no coverage; 5 means strong and explicit coverage.\n"
    )
    try:
        raw = await factory.complete(prompt=prompt,
            system_prompt="You are a strict education evaluator. Output valid JSON only, no markdown.",
            temperature=temperature, max_tokens=1000)
        parsed = extract_json(raw)
    except Exception as e:
        logger.warning("Practice gap-coverage eval failed: %s", e)
        parsed = {"gap_scores": {g.get("gap_id", f"gap_{i}"): 1 for i, g in enumerate(gaps)},
                  "rationale": f"fallback: {e}"}

    scores: dict[str, int] = {}
    for g in gap_view:
        gid = g.get("gap_id", "")
        scores[gid] = _clamp_score((parsed.get("gap_scores") or {}).get(gid, 1)) or 1
    avg = round(sum(scores.values()) / len(scores), 2) if scores else None
    return {"gap_scores": scores, "avg": avg, "rationale": parsed.get("rationale", "")}


async def _eval_pq_per_question(
    questions: list[str],
    gaps: list[dict],
    source_content: dict | None,
    profile: dict,
    temperature: float,
) -> list[dict]:
    """Per-question: difficulty_fit_delta, groundedness, distractor_quality."""
    from src.services.llm import factory

    gap_source_block = _format_gaps_with_source_for_pq(gaps, source_content)
    profile_view = json.dumps({
        "profile_id": profile.get("profile_id", ""),
        "learning_purpose": profile.get("learning_purpose", ""),
        "knowledge_state": profile.get("knowledge_state", {}),
    }, ensure_ascii=False, indent=2)

    results = []
    for i, q in enumerate(questions, start=1):
        prompt = (
            f"Evaluate this multiple-choice practice question (Q{i}) on three dimensions.\n\n"
            f"Question:\n{q}\n\n"
            f"Student profile:\n{profile_view}\n\n"
            f"Knowledge gaps and source content:\n{gap_source_block}\n\n"
            "Return strict JSON only:\n"
            "{\n"
            '  "difficulty_fit_delta": -5_to_5,\n'
            '  "groundedness": 1-5,\n'
            '  "distractor_quality": 1-5,\n'
            '  "rationale": "short reason"\n'
            "}\n\n"
            "Scoring guide:\n"
            "- difficulty_fit_delta: -5 = much too easy for this student, "
            "+5 = much too hard, 0 = ideal fit.\n"
            "- groundedness (1-5): Are the question's claims, terminology, and "
            "correct answer consistent with the source content? "
            "Check THREE aspects:\n"
            "  (a) Factual consistency: do factual claims align with and not "
            "contradict the source?\n"
            "  (b) Terminological consistency: does the question use the same "
            "definitions, terminology, and framing as the source? Different "
            "textbooks may define concepts differently; the question should follow "
            "the source's conventions, not introduce alternative definitions.\n"
            "  (c) Source grounding: does the question draw on specific details, "
            "examples, or structures from the source material? A question that "
            "references concrete content from the source (even paraphrased) is "
            "better grounded than one based on generic knowledge alone.\n"
            "A question that goes beyond the source (e.g. applies concepts to new "
            "scenarios) is fine as long as it doesn't distort or contradict the source. "
            "5 = all claims are accurate, terminology matches, AND the question "
            "clearly draws on specific source content; "
            "4 = mostly consistent, some evidence of source grounding, minor "
            "imprecision in wording; "
            "3 = some claims or definitions deviate from the source, or the question "
            "appears largely generic with weak connection to source material; "
            "2 = multiple claims contradict the source, or key terms use different "
            "definitions, or no evidence of consulting the source; "
            "1 = core claims are wrong or hallucinated, or terminology directly "
            "conflicts with the source's definitions.\n"
            "- distractor_quality (1-5): Quality of wrong answer options. "
            "5 = distractors target common misconceptions, are plausible but clearly wrong; "
            "1 = distractors are obviously absurd or trivially eliminable. "
            "If the question has no options/distractors, score 1.\n"
        )
        try:
            raw = await factory.complete(prompt=prompt,
                system_prompt="You are a strict education evaluator. Output valid JSON only.",
                temperature=temperature, max_tokens=800)
            parsed = extract_json(raw)
        except Exception as e:
            logger.warning("Practice Q%d per-question eval failed: %s", i, e)
            parsed = {"difficulty_fit_delta": 0, "groundedness": 1, "distractor_quality": 1,
                      "rationale": f"fallback: {e}"}

        diff_delta = _clamp_score(parsed.get("difficulty_fit_delta"), -5, 5) or 0
        results.append({
            "question_index": i,
            "question_preview": q[:200],
            "difficulty_fit_delta": diff_delta,
            "difficulty_abs": abs(diff_delta),
            "groundedness": _clamp_score(parsed.get("groundedness")) or 1,
            "distractor_quality": _clamp_score(parsed.get("distractor_quality")) or 1,
            "rationale": parsed.get("rationale", ""),
        })
    return results


async def _eval_pq_diversity(questions_block: str, temperature: float) -> dict:
    """Set-level: diversity among questions (1-5)."""
    from src.services.llm import factory

    prompt = (
        "Evaluate the DIVERSITY of the following practice question set.\n\n"
        f"Question set:\n{questions_block}\n\n"
        "Return strict JSON only:\n"
        '{"diversity_score": 1-5, "rationale": "short reason"}\n\n'
        "Scoring guide:\n"
        "- 5 = questions cover different knowledge points, cognitive levels "
        "(recall, understanding, application, analysis), and problem setups. "
        "No redundancy.\n"
        "- 1 = questions are near-duplicates or all test the same narrow concept "
        "at the same level.\n"
    )
    try:
        raw = await factory.complete(prompt=prompt,
            system_prompt="You are a strict education evaluator. Output valid JSON only.",
            temperature=temperature, max_tokens=500)
        parsed = extract_json(raw)
    except Exception as e:
        logger.warning("Practice diversity eval failed: %s", e)
        parsed = {"diversity_score": 1, "rationale": f"fallback: {e}"}

    return {
        "diversity_score": _clamp_score(parsed.get("diversity_score")) or 1,
        "rationale": parsed.get("rationale", ""),
    }


async def evaluate_practice_questions(
    *,
    practice_questions: list[str],
    entry: dict,
    temperature: float,
) -> dict:
    """Full practice question evaluation with 5 metrics.

    Returns dict with keys: per_question, gap_coverage, diversity, summary.
    """
    if not practice_questions:
        return {
            "per_question": [],
            "gap_coverage": None,
            "diversity": None,
            "summary": {
                "num_questions": 0,
                "avg_gap_coverage": None,
                "avg_difficulty_abs": None,
                "avg_groundedness": None,
                "avg_distractor_quality": None,
                "diversity_score": None,
            },
        }

    gaps = entry.get("gaps", [])
    profile = entry.get("profile", {})
    source_content = entry.get("source_content")

    questions_block = "\n\n".join(f"Q{i}. {q}" for i, q in enumerate(practice_questions, 1))

    coverage_result = await _eval_pq_gap_coverage(questions_block, gaps, temperature)
    per_question = await _eval_pq_per_question(
        practice_questions, gaps, source_content, profile, temperature)
    diversity_result = await _eval_pq_diversity(questions_block, temperature)

    diff_abs = [pq["difficulty_abs"] for pq in per_question]
    ground_scores = [pq["groundedness"] for pq in per_question]
    distractor_scores = [pq["distractor_quality"] for pq in per_question]

    return {
        "per_question": per_question,
        "gap_coverage": coverage_result,
        "diversity": diversity_result,
        "summary": {
            "num_questions": len(per_question),
            "avg_gap_coverage": coverage_result.get("avg"),
            "avg_difficulty_abs": round(sum(diff_abs) / len(diff_abs), 2) if diff_abs else None,
            "avg_groundedness": round(sum(ground_scores) / len(ground_scores), 2) if ground_scores else None,
            "avg_distractor_quality": round(sum(distractor_scores) / len(distractor_scores), 2) if distractor_scores else None,
            "diversity_score": diversity_result.get("diversity_score"),
        },
    }


def _load_entry_by_id(entry_id: str) -> dict | None:
    """
    Try to load entry by entry_id from generated JSONL files.
    Supports nested benchmark_<timestamp>/_all_entries.jsonl layout.
    """
    generated_dir = PROJECT_ROOT / "benchmark" / "data" / "generated"
    candidates = sorted(generated_dir.glob("**/*.jsonl"))
    for jsonl_path in candidates:
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get("entry_id") == entry_id:
                    return entry
    return None


async def _evaluate_single_session(
    *,
    transcript: list[dict],
    entry: dict,
    entry_id: str,
    skip_turns: bool,
    temperature: float,
    practice_questions: list[str] | None = None,
) -> dict:
    """Evaluate one session with turn-level + practice-question metrics."""
    dialog_msgs = _filter_dialog_messages(transcript)
    turns = _extract_turn_pairs(dialog_msgs)
    gaps = entry.get("gaps", [])
    gap_by_id = _build_gap_map(gaps)
    source_content = entry.get("source_content")

    has_pq = bool(practice_questions)
    eval_turns = turns
    if has_pq and eval_turns:
        eval_turns = turns[:-1]
        logger.info("Excluding last turn (practice questions) from turn-level evaluation")

    logger.info(
        "Metrics: gap_tracking, faithfulness%s, teaching_quality, turn_count | practice_questions=%s",
        " [source present]" if source_content else "",
        f"{len(practice_questions)} Qs" if has_pq else "none",
    )

    student_turns = sum(1 for m in dialog_msgs if m.get("role") == "student")
    tutor_turns = sum(1 for m in dialog_msgs if m.get("role") == "tutor")
    turn_count_metric = {
        "student_turns": student_turns,
        "tutor_turns": tutor_turns,
        "paired_turns": len(eval_turns),
    }

    gap_tracking_per_turn: list[dict] = []
    source_faithfulness_per_turn: list[dict] = []
    teaching_quality_per_turn: list[dict] = []
    mentioned_so_far: set[str] = set()
    resolved_so_far: set[str] = set()

    if not skip_turns:
        for t in eval_turns:
            turn_index = t["turn_index"]
            student_message = t["student_message"]
            tutor_response = t["tutor_response"]
            recent_context = _get_recent_context(dialog_msgs, t["student_msg_index"])

            gap_turn = await evaluate_gap_tracking_turn(
                entry=entry,
                turn_index=turn_index,
                student_message=student_message,
                tutor_response=tutor_response,
                recent_context=recent_context,
                previously_mentioned_gap_ids=sorted(mentioned_so_far),
                previously_resolved_gap_ids=sorted(resolved_so_far),
                temperature=temperature,
            )
            mentioned_turn = set(gap_turn.get("mentioned_gap_ids", []))
            resolved_turn_new = set(gap_turn.get("resolved_gap_ids_new", []))

            mentioned_so_far |= mentioned_turn
            resolved_so_far |= resolved_turn_new

            gap_turn["resolved_gap_ids_total"] = sorted(resolved_so_far)
            gap_turn["mentioned_count_turn"] = len(mentioned_turn)
            gap_turn["resolved_count_turn_new"] = len(resolved_turn_new)
            gap_turn["resolved_count_total"] = len(resolved_so_far)
            gap_tracking_per_turn.append(gap_turn)

            faith_turn = await evaluate_source_faithfulness_turn(
                turn_index=turn_index,
                student_message=student_message,
                tutor_response=tutor_response,
                recent_context=recent_context,
                mentioned_gap_ids=sorted(mentioned_turn),
                gap_by_id=gap_by_id,
                source_content=source_content,
                temperature=temperature,
            )
            source_faithfulness_per_turn.append(faith_turn)

            quality_turn = await evaluate_teaching_quality_turn(
                turn_index=turn_index,
                student_message=student_message,
                tutor_response=tutor_response,
                recent_context=recent_context,
                temperature=temperature,
            )
            teaching_quality_per_turn.append(quality_turn)

            logger.info(
                "Turn %d: mentioned=%d, resolved_new=%d, resolved_total=%d, faith=%s, insight=%s, applic=%s",
                turn_index, len(mentioned_turn), len(resolved_turn_new), len(resolved_so_far),
                faith_turn.get("faithfulness_score", "N/A"),
                quality_turn.get("insightfulness_score", "N/A"),
                quality_turn.get("applicability_score", "N/A"),
            )

    gap_tracking_metric = {
        "total_gaps": len(gap_by_id),
        "mentioned_gap_ids_final": sorted(mentioned_so_far),
        "resolved_gap_ids_final": sorted(resolved_so_far),
        "resolved_gaps_final_count": len(resolved_so_far),
        "per_turn": gap_tracking_per_turn,
    }
    source_faithfulness_metric = _build_source_faithfulness_summary(source_faithfulness_per_turn)
    teaching_quality_metric = _build_teaching_quality_summary(teaching_quality_per_turn)

    result: dict = {
        "entry_id": entry_id,
        "actual_turns": len(eval_turns),
        "metrics": {
            "gap_tracking": gap_tracking_metric,
            "source_faithfulness": source_faithfulness_metric,
            "teaching_quality": teaching_quality_metric,
            "turn_count": turn_count_metric,
        },
    }

    if has_pq and not skip_turns:
        logger.info("Evaluating %d practice questions...", len(practice_questions))
        pq_eval = await evaluate_practice_questions(
            practice_questions=practice_questions,
            entry=entry,
            temperature=temperature,
        )
        result["metrics"]["practice_questions"] = pq_eval
        s = pq_eval.get("summary", {})
        logger.info(
            "Practice Q: gap_cov=%.2f ground=%.2f distractor=%.2f diversity=%s diff_abs=%.2f",
            s.get("avg_gap_coverage") or 0, s.get("avg_groundedness") or 0,
            s.get("avg_distractor_quality") or 0, s.get("diversity_score", "N/A"),
            s.get("avg_difficulty_abs") or 0,
        )
    elif has_pq and skip_turns:
        result["metrics"]["practice_questions"] = {
            "num_questions": len(practice_questions),
            "note": "skipped (--skip-turns)",
        }

    return result


def _safe_avg(vals: list[float]) -> float | None:
    return round(sum(vals) / len(vals), 2) if vals else None


def _aggregate_multi_session(session_results: list[dict]) -> dict:
    """Build lightweight aggregate view; each session gap stats stay independent."""
    if not session_results:
        return {}

    total_student_turns = 0
    total_tutor_turns = 0
    total_paired_turns = 0
    faith_scores: list[float] = []
    insight_scores: list[float] = []
    applicability_scores: list[float] = []
    resolved_counts: list[int] = []
    total_gaps_counts: list[int] = []

    pq_total_questions = 0
    pq_coverage: list[float] = []
    pq_diff_abs: list[float] = []
    pq_ground: list[float] = []
    pq_distractor: list[float] = []
    pq_diversity: list[float] = []

    for s in session_results:
        tc = s.get("metrics", {}).get("turn_count", {})
        total_student_turns += tc.get("student_turns", 0)
        total_tutor_turns += tc.get("tutor_turns", 0)
        total_paired_turns += tc.get("paired_turns", 0)

        gt = s.get("metrics", {}).get("gap_tracking", {})
        resolved_counts.append(gt.get("resolved_gaps_final_count", 0))
        total_gaps_counts.append(gt.get("total_gaps", 0))

        sf = s.get("metrics", {}).get("source_faithfulness", {})
        for t in sf.get("per_turn", []):
            score = t.get("faithfulness_score")
            if score is not None and not t.get("not_applicable"):
                faith_scores.append(float(score))

        tq = s.get("metrics", {}).get("teaching_quality", {})
        for t in tq.get("per_turn", []):
            ins = t.get("insightfulness_score")
            app = t.get("applicability_score")
            if ins is not None and not t.get("not_applicable"):
                insight_scores.append(float(ins))
            if app is not None and not t.get("not_applicable"):
                applicability_scores.append(float(app))

        pq = s.get("metrics", {}).get("practice_questions")
        if pq and pq.get("summary"):
            sm = pq["summary"]
            pq_total_questions += sm.get("num_questions", 0)
            for key, lst in [("avg_gap_coverage", pq_coverage), ("avg_difficulty_abs", pq_diff_abs),
                             ("avg_groundedness", pq_ground), ("avg_distractor_quality", pq_distractor),
                             ("diversity_score", pq_diversity)]:
                v = sm.get(key)
                if isinstance(v, (int, float)):
                    lst.append(float(v))

    total_resolved = sum(resolved_counts)
    total_gaps = sum(total_gaps_counts)
    gap_resolution_rate = round(total_resolved / total_gaps, 3) if total_gaps else None
    gap_efficiency = (
        round(total_resolved / total_paired_turns, 3) if total_paired_turns else None
    )

    result: dict = {
        "turn_count": {
            "student_turns_total": total_student_turns,
            "tutor_turns_total": total_tutor_turns,
            "paired_turns_total": total_paired_turns,
        },
        "gap_tracking": {
            "resolved_gaps_per_session": resolved_counts,
            "total_gaps_per_session": total_gaps_counts,
            "total_resolved": total_resolved,
            "total_gaps": total_gaps,
            "gap_resolution_rate": gap_resolution_rate,
            "gap_resolution_efficiency": gap_efficiency,
        },
        "source_faithfulness": {
            "scale": "1-5",
            "num_scored_turns_total": len(faith_scores),
            "max_score_overall": max(faith_scores) if faith_scores else None,
            "min_score_overall": min(faith_scores) if faith_scores else None,
            "avg_score_overall": _safe_avg(faith_scores),
        },
        "teaching_quality": {
            "scale": "1-5",
            "num_scored_turns_insightfulness_total": len(insight_scores),
            "num_scored_turns_applicability_total": len(applicability_scores),
            "avg_insightfulness_overall": _safe_avg(insight_scores),
            "avg_applicability_overall": _safe_avg(applicability_scores),
        },
    }

    if pq_total_questions > 0:
        result["practice_questions"] = {
            "total_questions_across_sessions": pq_total_questions,
            "avg_gap_coverage": _safe_avg(pq_coverage),
            "avg_difficulty_abs": _safe_avg(pq_diff_abs),
            "avg_groundedness": _safe_avg(pq_ground),
            "avg_distractor_quality": _safe_avg(pq_distractor),
            "avg_diversity": _safe_avg(pq_diversity),
        }

    return result


async def evaluate_transcript(
    transcript_path: str | Path,
    skip_turns: bool = False,
    temperature: float = 0.2,
) -> dict:
    """
    Evaluate transcript using independent metrics (no weighted merge).

    Args:
        transcript_path: Path to transcript JSON
        skip_turns: If True, skip LLM per-turn metrics and keep only turn_count
        temperature: LLM temperature for metric-1 and metric-2
    """
    path = Path(transcript_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Multi-session format
    if "sessions" in data:
        sessions = data["sessions"]
        profile_id = data.get("profile_id", "unknown")
        session_results = []

        for i, sess in enumerate(sessions):
            transcript = sess.get("transcript", [])
            entry = sess.get("entry")
            entry_id = sess.get("entry_id", f"session_{i+1}")

            if not entry:
                entry = _load_entry_by_id(entry_id)
            if not entry:
                logger.warning(
                    "Session %s has no entry; skipping (run multi-session again to save entry)",
                    entry_id,
                )
                continue

            logger.info("Evaluating session %d/%d: %s", i + 1, len(sessions), entry_id)
            sess_result = await _evaluate_single_session(
                transcript=transcript,
                entry=entry,
                entry_id=entry_id,
                skip_turns=skip_turns,
                temperature=temperature,
                practice_questions=sess.get("practice_questions"),
            )
            session_results.append(sess_result)

        if not session_results:
            raise ValueError(
                "No sessions could be evaluated (missing 'entry' in each session; "
                "re-run multi-session to save entries)"
            )

        return {
            "profile_id": profile_id,
            "transcript_path": str(path),
            "num_sessions": len(session_results),
            "sessions": session_results,
            "aggregate": _aggregate_multi_session(session_results),
        }

    # Single-session format
    transcript = data.get("transcript", [])
    entry = data.get("entry", {})
    if not entry:
        raise ValueError("Transcript must contain 'entry' (benchmark entry with profile, gaps, task)")

    result = await _evaluate_single_session(
        transcript=transcript,
        entry=entry,
        entry_id=data.get("entry_id", "unknown"),
        skip_turns=skip_turns,
        temperature=temperature,
        practice_questions=data.get("practice_questions"),
    )
    result["transcript_path"] = str(path)
    return result
