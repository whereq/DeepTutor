#!/usr/bin/env python3
"""
Step 1: Generate benchmark entries grouped by KB.

For each KB:
1) Generate knowledge scope
2) Generate profiles
3) For each profile, generate entries (gaps + tasks) in parallel

Output layout (stable, KB-separated):
  <output_root>/entries/<kb_name>/knowledge_scope.json
  <output_root>/entries/<kb_name>/profiles.json
  <output_root>/entries/<kb_name>/profiles/<profile_id>/profile.json
  <output_root>/entries/<kb_name>/profiles/<profile_id>/entries.jsonl
  <output_root>/entries/<kb_name>/profiles/<profile_id>/entries/<entry_id>.json

Manifest:
  <output_root>/manifests/step1_manifest.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.data_generation.profile_generator import generate_profiles_for_kb
from benchmark.data_generation.scope_generator import generate_knowledge_scope
from benchmark.simulation.batch_simulation import _generate_entries_for_profile

logger = logging.getLogger("benchmark.pipeline.step1")

DEFAULT_CONFIG = PROJECT_ROOT / "benchmark" / "config" / "benchmark_config.yaml"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "benchmark" / "data" / "bench_pipeline"


def _parse_kb_names(raw: str) -> list[str]:
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return sorted(set(names))


def _save_profile_entries(entries: list[dict], profile_dir: Path) -> None:
    if profile_dir.exists():
        shutil.rmtree(profile_dir)
    (profile_dir / "entries").mkdir(parents=True, exist_ok=True)

    jsonl_path = profile_dir / "entries.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    for entry in entries:
        entry_id = entry.get("entry_id", "unknown")
        out = profile_dir / "entries" / f"{entry_id}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)


async def _generate_entries_for_one_profile(
    *,
    kb_name: str,
    profile: dict,
    scope: dict,
    cfg: dict,
    kb_base_dir: str,
    kb_entries_dir: Path,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        profile_id = profile.get("profile_id", "unknown")
        profile_dir = kb_entries_dir / "profiles" / profile_id
        result = {
            "kb_name": kb_name,
            "profile_id": profile_id,
            "status": "ok",
            "num_entries": 0,
            "error": None,
            "entries_path": str(profile_dir / "entries.jsonl"),
        }
        try:
            entries = await _generate_entries_for_profile(
                kb_name=kb_name,
                profile=profile,
                knowledge_scope=scope,
                cfg=cfg,
                kb_base_dir=kb_base_dir,
            )
            _save_profile_entries(entries, profile_dir)
            with open(profile_dir / "profile.json", "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            result["num_entries"] = len(entries)
            logger.info("[%s] %s -> %d entries", kb_name, profile_id, len(entries))
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error("[%s] %s failed: %s", kb_name, profile_id, e)
        return result


async def _process_one_kb(
    *,
    kb_name: str,
    kb_base_dir: Path,
    entries_root: Path,
    profile_cfg: dict,
    rag_cfg: dict,
    cfg: dict,
    profile_semaphore: asyncio.Semaphore,
    kb_semaphore: asyncio.Semaphore,
) -> tuple[dict, int]:
    """Process one KB: scope -> profiles -> entries (profiles in parallel)."""
    async with kb_semaphore:
        kb_dir = kb_base_dir / kb_name
        kb_entry_root = entries_root / kb_name
        kb_entry_root.mkdir(parents=True, exist_ok=True)

        kb_record = {
            "kb_name": kb_name,
            "status": "ok",
            "error": None,
            "num_profiles": 0,
            "profiles": [],
        }
        profile_errors = 0

        if not kb_dir.exists():
            kb_record["status"] = "error"
            kb_record["error"] = f"KB directory not found: {kb_dir}"
            logger.error("[%s] KB directory not found", kb_name)
            return kb_record, profile_errors

        try:
            scope = await generate_knowledge_scope(
                kb_name=kb_name,
                seed_queries=rag_cfg.get("seed_queries"),
                mode=rag_cfg.get("mode", "naive"),
                kb_base_dir=str(kb_base_dir),
            )
            kb_entry_root.mkdir(parents=True, exist_ok=True)
            with open(kb_entry_root / "knowledge_scope.json", "w", encoding="utf-8") as f:
                json.dump(scope, f, ensure_ascii=False, indent=2)
        except Exception as e:
            kb_record["status"] = "error"
            kb_record["error"] = f"knowledge_scope generation failed: {e}"
            logger.error("[%s] knowledge_scope failed: %s", kb_name, e)
            return kb_record, profile_errors

        try:
            profiles = await generate_profiles_for_kb(
                knowledge_scope=scope,
                background_types=profile_cfg.get(
                    "background_types", ["beginner", "intermediate", "advanced"]
                ),
                profiles_per_kb=profile_cfg.get("profiles_per_subtopic", 3),
            )
            with open(kb_entry_root / "profiles.json", "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            kb_record["num_profiles"] = len(profiles)
        except Exception as e:
            kb_record["status"] = "error"
            kb_record["error"] = f"profile generation failed: {e}"
            logger.error("[%s] profile generation failed: %s", kb_name, e)
            return kb_record, profile_errors

        tasks = [
            _generate_entries_for_one_profile(
                kb_name=kb_name,
                profile=p,
                scope=scope,
                cfg=cfg,
                kb_base_dir=str(kb_base_dir),
                kb_entries_dir=kb_entry_root,
                semaphore=profile_semaphore,
            )
            for p in profiles
        ]
        profile_results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in profile_results:
            if isinstance(r, Exception):
                profile_errors += 1
                kb_record["profiles"].append(
                    {
                        "status": "error",
                        "error": str(r),
                    }
                )
                continue
            kb_record["profiles"].append(r)
            if r.get("status") != "ok":
                profile_errors += 1

        return kb_record, profile_errors


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Step1: generate profiles + entries for KBs"
    )
    parser.add_argument(
        "--kb-names",
        required=True,
        help="Comma-separated KB names to process",
    )
    parser.add_argument(
        "--kb-dir",
        default="data/knowledge_bases",
        help="Knowledge base directory (default: data/knowledge_bases)",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help=f"Benchmark config path (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Pipeline output root (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help="Max parallel profile entry-generation tasks (default: 6)",
    )
    parser.add_argument(
        "--kb-concurrency",
        type=int,
        default=6,
        help="Max parallel KB tasks (default: 6)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Accepted for compatibility; output is overwritten by default.",
    )
    args = parser.parse_args()

    kb_names = _parse_kb_names(args.kb_names)
    kb_base_dir = Path(args.kb_dir)
    if not kb_base_dir.is_absolute():
        kb_base_dir = (PROJECT_ROOT / kb_base_dir).resolve()

    cfg_path = Path(args.config)
    if not cfg_path.is_absolute():
        cfg_path = (PROJECT_ROOT / cfg_path).resolve()
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (PROJECT_ROOT / output_root).resolve()
    entries_root = output_root / "entries"
    manifests_root = output_root / "manifests"
    entries_root.mkdir(parents=True, exist_ok=True)
    manifests_root.mkdir(parents=True, exist_ok=True)

    profile_cfg = cfg.get("profile_generation", {})
    rag_cfg = cfg.get("rag_query", {})

    kb_parallel = max(1, args.kb_concurrency)
    print(
        f"KBs: {len(kb_names)} | Concurrency(profile): {args.concurrency} | "
        f"Concurrency(kb): {kb_parallel}"
    )
    print(f"Output root: {output_root}")
    for kb in kb_names:
        print(f"  - {kb}")

    profile_sem = asyncio.Semaphore(args.concurrency)
    # Keep KB-level parallelism moderate to avoid overloading RAG/LLM services.
    kb_sem = asyncio.Semaphore(kb_parallel)
    logger.info(
        "Step1 parallelism: kb_concurrency=%d, profile_concurrency=%d",
        kb_parallel,
        args.concurrency,
    )

    kb_tasks = [
        _process_one_kb(
            kb_name=kb_name,
            kb_base_dir=kb_base_dir,
            entries_root=entries_root,
            profile_cfg=profile_cfg,
            rag_cfg=rag_cfg,
            cfg=cfg,
            profile_semaphore=profile_sem,
            kb_semaphore=kb_sem,
        )
        for kb_name in kb_names
    ]
    raw_results = await asyncio.gather(*kb_tasks, return_exceptions=True)

    kb_records: list[dict] = []
    total_profile_errors = 0
    for i, item in enumerate(raw_results):
        if isinstance(item, Exception):
            kb_name = kb_names[i]
            kb_records.append(
                {
                    "kb_name": kb_name,
                    "status": "error",
                    "error": str(item),
                    "num_profiles": 0,
                    "profiles": [],
                }
            )
            logger.error("[%s] unexpected failure: %s", kb_name, item)
            continue
        kb_record, profile_errors = item
        kb_records.append(kb_record)
        total_profile_errors += profile_errors

    manifest = {
        "step": "step1_generate_entries",
        "timestamp": datetime.now().isoformat(),
        "kb_names": kb_names,
        "output_root": str(output_root),
        "concurrency_profile": args.concurrency,
        "concurrency_kb": kb_parallel,
        "overwrite": True,
        "results": kb_records,
        "num_kbs": len(kb_names),
        "num_kb_errors": sum(1 for r in kb_records if r.get("status") != "ok"),
        "num_profile_errors": total_profile_errors,
    }
    manifest_path = manifests_root / "step1_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nManifest: {manifest_path}")
    print(
        f"Done. KB errors: {manifest['num_kb_errors']} | "
        f"Profile errors: {manifest['num_profile_errors']}"
    )
    if manifest["num_kb_errors"] > 0 or manifest["num_profile_errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
