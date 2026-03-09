#!/usr/bin/env python3
"""
Step 2: Run simulations per profile, backend serially.

Input:
  <output_root>/entries/<kb_name>/profiles/<profile_id>/entries.jsonl

Output:
  <output_root>/transcripts/<kb_name>/<backend>/<profile_id>.json
  <output_root>/workspaces/<kb_name>/<backend>/<profile_id>/

Manifest:
  <output_root>/manifests/step2_manifest.json
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import io
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.simulation.profile_evolver import evolve_profile as evolve_profile_fn

logger = logging.getLogger("benchmark.pipeline.step2")

DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "benchmark" / "data" / "bench_pipeline"


def _parse_names(raw: str) -> list[str]:
    return sorted(set(n.strip() for n in raw.split(",") if n.strip()))


def _load_entries(entries_jsonl: Path) -> list[dict]:
    entries: list[dict] = []
    with open(entries_jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


async def _simulate_profile_backend(
    *,
    kb_name: str,
    profile_id: str,
    entries: list[dict],
    backend: Literal["deep_tutor", "mock"],
    output_root: Path,
    max_turns: int,
    language: str,
    evolve_profile: bool,
    verbose: bool,
) -> dict:
    from benchmark.simulation.conversation import (
        _run_single_session,
        _summarize_session,
    )

    if not entries:
        logger.warning("[%s/%s] %s has 0 entries, skipping", kb_name, backend, profile_id)
        return {
            "status": "skipped",
            "backend": backend,
            "profile_id": profile_id,
            "kb_name": kb_name,
            "num_sessions": 0,
            "transcript_path": "",
            "error": "0 entries",
        }

    workspace = str(output_root / "workspaces" / kb_name / backend / profile_id)
    prior_sessions_summary: list[str] = []
    current_profile = entries[0].get("profile", {})
    sessions_results: list[dict] = []

    for i, base_entry in enumerate(entries):
        session_num = i + 1
        entry = dict(base_entry)

        if evolve_profile and i > 0:
            prev_profile = entries[i - 1].get("profile", {})
            resolved = entries[i - 1].get("gaps", [])
            current_profile = evolve_profile_fn(prev_profile, resolved)
        entry["profile"] = current_profile

        prior_ctx = "\n".join(prior_sessions_summary) if prior_sessions_summary else None
        logger.info(
            "[%s/%s] %s session %d/%d",
            kb_name,
            backend,
            profile_id,
            session_num,
            len(entries),
        )

        try:
            if verbose:
                result = await _run_single_session(
                    entry=entry,
                    max_turns=max_turns,
                    auto=True,
                    use_editor=False,
                    auto_backend=backend,
                    deeptutor_workspace=workspace,
                    deeptutor_language=language,
                    prior_sessions_summary=prior_ctx,
                )
            else:
                with contextlib.redirect_stdout(io.StringIO()):
                    result = await _run_single_session(
                        entry=entry,
                        max_turns=max_turns,
                        auto=True,
                        use_editor=False,
                        auto_backend=backend,
                        deeptutor_workspace=workspace,
                        deeptutor_language=language,
                        prior_sessions_summary=prior_ctx,
                    )
        except Exception as e:
            logger.error(
                "[%s/%s] %s session %d failed: %s",
                kb_name,
                backend,
                profile_id,
                session_num,
                e,
            )
            result = {
                "entry_id": entry.get("entry_id", f"session_{session_num}"),
                "transcript": [],
                "entry": entry,
                "actual_turns": 0,
                "practice_questions": [],
                "error": str(e),
            }

        summary = _summarize_session(result.get("transcript", []), entry.get("task", {}), session_num)
        prior_sessions_summary.append(summary)
        sessions_results.append(result)

    combined = {
        "kb_name": kb_name,
        "profile_id": profile_id,
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "mode": "auto",
        "evolve_profile": evolve_profile,
        "num_sessions": len(sessions_results),
        "sessions": [
            {
                "entry_id": r["entry_id"],
                "actual_turns": r["actual_turns"],
                "transcript": r.get("transcript", []),
                "entry": r["entry"],
                "practice_questions": r.get("practice_questions", []),
            }
            for r in sessions_results
        ],
    }

    transcript_path = output_root / "transcripts" / kb_name / backend / f"{profile_id}.json"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "backend": backend,
        "profile_id": profile_id,
        "kb_name": kb_name,
        "num_sessions": combined.get("num_sessions", 0),
        "transcript_path": str(transcript_path),
        "error": None,
    }


async def _process_profile(
    *,
    kb_name: str,
    profile_id: str,
    entries: list[dict],
    backends: list[str],
    output_root: Path,
    semaphore: asyncio.Semaphore,
    max_turns: int,
    language: str,
    evolve_profile: bool,
    verbose: bool,
) -> dict:
    async with semaphore:
        record = {
            "kb_name": kb_name,
            "profile_id": profile_id,
            "status": "ok",
            "num_entries": len(entries),
            "backends": {},
            "error": None,
        }
        for backend in backends:
            try:
                result = await _simulate_profile_backend(
                    kb_name=kb_name,
                    profile_id=profile_id,
                    entries=entries,
                    backend=backend,  # type: ignore[arg-type]
                    output_root=output_root,
                    max_turns=max_turns,
                    language=language,
                    evolve_profile=evolve_profile,
                    verbose=verbose,
                )
                record["backends"][backend] = result
            except Exception as e:
                record["status"] = "error"
                record["backends"][backend] = {
                    "status": "error",
                    "error": str(e),
                }
                logger.error("[%s] %s backend=%s failed: %s", kb_name, profile_id, backend, e)
        return record


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Step2: run simulations to generate transcripts")
    parser.add_argument("--kb-names", required=True, help="Comma-separated KB names to process")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Pipeline output root (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--backends",
        default="mock,deep_tutor",
        help="Comma-separated backends (executed serially per profile)",
    )
    parser.add_argument("--concurrency", type=int, default=6, help="Max parallel profiles")
    parser.add_argument("--max-turns", type=int, default=30, help="Max student turns per session")
    parser.add_argument("--language", default="en", help="DeepTutor language")
    parser.add_argument(
        "--model",
        default="",
        help="Override LLM model for step2 simulation. If set, ignores env LLM_MODEL.",
    )
    parser.add_argument("--no-evolve", action="store_true", help="Disable profile evolution")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-turn output")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Accepted for compatibility; transcripts are overwritten by default.",
    )
    args = parser.parse_args()

    if args.model:
        # Force model override for this process.
        os.environ["LLM_MODEL"] = args.model
        try:
            from src.services.llm.config import clear_llm_config_cache

            clear_llm_config_cache()
        except Exception:
            pass

    # Suppress noisy logs from RAG/LLM internals during auto simulation
    from benchmark.simulation.conversation import _suppress_noisy_auto_logs

    _suppress_noisy_auto_logs()
    logging.getLogger("benchmark.pipeline.step2").setLevel(logging.INFO)
    logging.getLogger("benchmark.conversation").setLevel(logging.INFO)

    kb_names = _parse_names(args.kb_names)
    backends = _parse_names(args.backends)
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (PROJECT_ROOT / output_root).resolve()
    entries_root = output_root / "entries"
    manifests_root = output_root / "manifests"
    manifests_root.mkdir(parents=True, exist_ok=True)

    print(f"KBs: {len(kb_names)} | Concurrency(profile): {args.concurrency}")
    print(f"Backends(serial/profile): {backends}")
    print(f"Output root: {output_root}")

    sem = asyncio.Semaphore(args.concurrency)
    tasks = []
    pre_errors: list[dict] = []
    for kb_name in kb_names:
        kb_profiles_root = entries_root / kb_name / "profiles"
        if not kb_profiles_root.exists():
            pre_errors.append(
                {
                    "kb_name": kb_name,
                    "profile_id": None,
                    "status": "error",
                    "error": f"Missing entries directory: {kb_profiles_root}",
                }
            )
            logger.error("[%s] missing entries directory: %s", kb_name, kb_profiles_root)
            continue
        for profile_dir in sorted(p for p in kb_profiles_root.iterdir() if p.is_dir()):
            profile_id = profile_dir.name
            entries_path = profile_dir / "entries.jsonl"
            if not entries_path.exists():
                pre_errors.append(
                    {
                        "kb_name": kb_name,
                        "profile_id": profile_id,
                        "status": "error",
                        "error": f"Missing entries.jsonl: {entries_path}",
                    }
                )
                logger.error("[%s] %s missing entries.jsonl", kb_name, profile_id)
                continue
            try:
                entries = _load_entries(entries_path)
            except Exception as e:
                pre_errors.append(
                    {
                        "kb_name": kb_name,
                        "profile_id": profile_id,
                        "status": "error",
                        "error": f"Failed to load entries.jsonl: {e}",
                    }
                )
                continue
            if not entries:
                pre_errors.append(
                    {
                        "kb_name": kb_name,
                        "profile_id": profile_id,
                        "status": "error",
                        "error": f"entries.jsonl is empty (0 entries): {entries_path}",
                    }
                )
                logger.error("[%s] %s has 0 entries, skipping", kb_name, profile_id)
                continue
            tasks.append(
                _process_profile(
                    kb_name=kb_name,
                    profile_id=profile_id,
                    entries=entries,
                    backends=backends,
                    output_root=output_root,
                    semaphore=sem,
                    max_turns=args.max_turns,
                    language=args.language,
                    evolve_profile=not args.no_evolve,
                    verbose=args.verbose,
                )
            )

    logger.info("Launching %d profile simulation tasks", len(tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    profile_results = []
    task_errors = 0
    for r in results:
        if isinstance(r, Exception):
            task_errors += 1
            profile_results.append({"status": "error", "error": str(r)})
        else:
            profile_results.append(r)
            if r.get("status") != "ok":
                task_errors += 1

    manifest = {
        "step": "step2_generate_transcripts",
        "timestamp": datetime.now().isoformat(),
        "kb_names": kb_names,
        "backends": backends,
        "model": (args.model or os.getenv("LLM_MODEL", "")),
        "output_root": str(output_root),
        "concurrency_profile": args.concurrency,
        "backend_execution": "serial_per_profile",
        "overwrite": True,
        "pre_errors": pre_errors,
        "results": profile_results,
        "num_profiles": len(profile_results),
        "num_errors": len(pre_errors) + task_errors,
    }
    manifest_path = manifests_root / "step2_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nManifest: {manifest_path}")
    print(f"Done. Profile tasks: {len(profile_results)} | Errors: {manifest['num_errors']}")
    if manifest["num_errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
