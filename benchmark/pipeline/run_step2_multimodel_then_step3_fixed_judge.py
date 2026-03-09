#!/usr/bin/env python3
"""
Run Step2 with multiple generation models, then Step3 with one fixed judge model.

Example:
  python -m benchmark.pipeline.run_step2_multimodel_then_step3_fixed_judge \
    --kb-names kb_a,kb_b \
    --step2-models qwen3.5-plus,deepseek-v3 \
    --judge-model qwen3.5-plus \
    --base-output-root benchmark/data/bench_pipeline_multimodel
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[2]


def _parse_names(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def _safe_model_key(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", model).strip("_") or "model"


def _run(cmd: list[str], env: dict[str, str]) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env, check=True)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run step2 (multi models) then step3 (fixed judge model)."
    )
    parser.add_argument("--kb-names", required=True, help="Comma-separated KB names")
    parser.add_argument(
        "--step2-models",
        required=True,
        help="Comma-separated models for step2 generation (e.g. a,b,c)",
    )
    parser.add_argument(
        "--judge-model",
        required=True,
        help="Model used for all step3 evaluations",
    )
    parser.add_argument(
        "--base-output-root",
        default=str(PROJECT_ROOT / "benchmark" / "data" / "bench_pipeline_multimodel"),
        help="Base output root; each model writes to a subdir",
    )
    parser.add_argument("--backends", default="mock,deep_tutor")
    parser.add_argument("--step2-concurrency", type=int, default=6)
    parser.add_argument("--step2-max-turns", type=int, default=30)
    parser.add_argument("--step2-language", default="en")
    parser.add_argument("--step2-no-evolve", action="store_true")
    parser.add_argument("--step2-verbose", action="store_true")
    parser.add_argument("--step3-concurrency", type=int, default=6)
    parser.add_argument("--step3-temperature", type=float, default=0.2)
    parser.add_argument("--step3-skip-turns", action="store_true")
    args = parser.parse_args()

    kb_names = ",".join(_parse_names(args.kb_names))
    models = _parse_names(args.step2_models)
    if not models:
        raise ValueError("No step2 models provided.")

    base_output_root = Path(args.base_output_root)
    if not base_output_root.is_absolute():
        base_output_root = (PROJECT_ROOT / base_output_root).resolve()
    base_output_root.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, Any]] = []

    for model in models:
        model_key = _safe_model_key(model)
        output_root = base_output_root / model_key
        output_root.mkdir(parents=True, exist_ok=True)

        env_step2 = os.environ.copy()
        env_step2["LLM_MODEL"] = model

        step2_cmd = [
            sys.executable,
            str(PROJECT_ROOT / "benchmark" / "pipeline" / "step2_generate_transcripts.py"),
            "--kb-names",
            kb_names,
            "--output-root",
            str(output_root),
            "--backends",
            args.backends,
            "--concurrency",
            str(args.step2_concurrency),
            "--max-turns",
            str(args.step2_max_turns),
            "--language",
            args.step2_language,
            "--model",
            model,
        ]
        if args.step2_no_evolve:
            step2_cmd.append("--no-evolve")
        if args.step2_verbose:
            step2_cmd.append("--verbose")
        _run(step2_cmd, env_step2)

        env_step3 = os.environ.copy()
        env_step3["LLM_MODEL"] = args.judge_model

        step3_cmd = [
            sys.executable,
            str(PROJECT_ROOT / "benchmark" / "pipeline" / "step3_evaluate_transcripts.py"),
            "--kb-names",
            kb_names,
            "--output-root",
            str(output_root),
            "--backends",
            args.backends,
            "--concurrency",
            str(args.step3_concurrency),
            "--temperature",
            str(args.step3_temperature),
        ]
        if args.step3_skip_turns:
            step3_cmd.append("--skip-turns")
        _run(step3_cmd, env_step3)

        runs.append(
            {
                "step2_model": model,
                "step2_model_key": model_key,
                "judge_model": args.judge_model,
                "output_root": str(output_root),
                "step2_manifest": str(output_root / "manifests" / "step2_manifest.json"),
                "step3_manifest": str(output_root / "manifests" / "step3_manifest.json"),
                "step3_summary": str(output_root / "manifests" / "step3_summary.json"),
                "step3_summary_data": _load_json(output_root / "manifests" / "step3_summary.json"),
            }
        )

    summary = {
        "timestamp": datetime.now().isoformat(),
        "kb_names": _parse_names(args.kb_names),
        "backends": _parse_names(args.backends),
        "judge_model": args.judge_model,
        "base_output_root": str(base_output_root),
        "runs": runs,
    }

    manifests_dir = base_output_root / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    out_path = manifests_dir / "multimodel_step2_then_step3_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nSummary: {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()

