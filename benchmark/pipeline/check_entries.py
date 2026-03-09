#!/usr/bin/env python3
"""
Check entry health across all KBs in the bench_pipeline output.
With --fix, automatically regenerate unhealthy entries via LLM.

Usage:
    python3 -m benchmark.pipeline.check_entries
    python3 -m benchmark.pipeline.check_entries --kb-names kb1,kb2
    python3 -m benchmark.pipeline.check_entries --fix
    python3 -m benchmark.pipeline.check_entries --fix --concurrency 4
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

import yaml

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_CONFIG = PROJECT_ROOT / "benchmark" / "config" / "benchmark_config.yaml"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "benchmark" / "data" / "bench_pipeline"

ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_DIM = "\033[2m"
ANSI_BOLD = "\033[1m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"

FIX_RETRY_ATTEMPTS = 3
FIX_RETRY_DELAY_SEC = 3.0
EXPECTED_ENTRIES_PER_PROFILE = 3


def _load_entries_jsonl(path: Path) -> list[dict]:
    entries: list[dict] = []
    if not path.exists():
        return entries
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _extract_task_index(entry_id: str) -> int:
    marker = "_task_"
    if marker not in entry_id:
        return 0
    try:
        return int(entry_id.rsplit(marker, 1)[-1])
    except Exception:
        return 0


def _next_task_index(entries: list[dict]) -> int:
    max_idx = 0
    for e in entries:
        max_idx = max(max_idx, _extract_task_index(str(e.get("entry_id", ""))))
    return max_idx + 1


def _count_jsonl(path: Path) -> int:
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def _check_entry_quality(entry: dict) -> list[str]:
    warnings = []
    if not entry.get("gaps"):
        warnings.append("no gaps")
    if not entry.get("task"):
        warnings.append("no task")
    task = entry.get("task", {})
    if not task.get("target_gaps"):
        warnings.append("task has no target_gaps")
    if not task.get("title") and not task.get("description"):
        warnings.append("task has no title/description")
    profile = entry.get("profile", {})
    if not profile.get("profile_id"):
        warnings.append("no profile_id in entry")
    return warnings


def _classify_profile(
    profile_dir: Path,
) -> tuple[str, int, list[str]]:
    """Classify a profile as ok / warn / empty / missing. Returns (status, n_entries, warnings)."""
    entries_jsonl = profile_dir / "entries.jsonl"
    if not entries_jsonl.exists():
        return "missing", 0, []

    n_entries = _count_jsonl(entries_jsonl)
    if n_entries == 0:
        return "empty", 0, []

    entry_warnings: list[str] = []
    try:
        with open(entries_jsonl, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                ws = _check_entry_quality(entry)
                entry_warnings.extend(
                    f"{entry.get('entry_id', '?')}: {w}" for w in ws
                )
    except Exception as e:
        entry_warnings.append(f"parse error: {e}")

    if n_entries != EXPECTED_ENTRIES_PER_PROFILE:
        entry_warnings.append(
            f"entry count mismatch: expected {EXPECTED_ENTRIES_PER_PROFILE}, got {n_entries}"
        )

    if entry_warnings:
        return "warn", n_entries, entry_warnings
    return "ok", n_entries, []


def _save_profile_entries(entries: list[dict], profile_dir: Path) -> None:
    entries_dir = profile_dir / "entries"
    if entries_dir.exists():
        shutil.rmtree(entries_dir)
    entries_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = profile_dir / "entries.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    for entry in entries:
        entry_id = entry.get("entry_id", "unknown")
        out = entries_dir / f"{entry_id}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)


async def _fix_one_profile(
    *,
    kb_name: str,
    profile_id: str,
    profile: dict,
    scope: dict,
    cfg: dict,
    kb_base_dir: str,
    profile_dir: Path,
    semaphore: asyncio.Semaphore,
) -> dict:
    from benchmark.simulation.batch_simulation import _generate_entries_for_profile

    async with semaphore:
        result = {
            "kb_name": kb_name,
            "profile_id": profile_id,
            "status": "ok",
            "num_entries": 0,
            "error": None,
        }

        entries: list[dict] = []
        last_error: str | None = None
        entries_jsonl = profile_dir / "entries.jsonl"

        try:
            current_entries = _load_entries_jsonl(entries_jsonl)
        except Exception:
            current_entries = []

        def _sort_entries(xs: list[dict]) -> list[dict]:
            return sorted(
                xs,
                key=lambda e: _extract_task_index(str(e.get("entry_id", ""))),
            )

        def _normalize_new_entry(e: dict, task_idx: int) -> dict:
            e = dict(e)
            e["kb_name"] = kb_name
            e["profile"] = profile
            e["entry_id"] = f"{kb_name}_{profile_id}_task_{task_idx:03d}"
            return e

        # If there are too many entries, keep the first N and rewrite files.
        if len(current_entries) > EXPECTED_ENTRIES_PER_PROFILE:
            trimmed = _sort_entries(current_entries)[:EXPECTED_ENTRIES_PER_PROFILE]
            _save_profile_entries(trimmed, profile_dir)
            if not (profile_dir / "profile.json").exists():
                with open(profile_dir / "profile.json", "w", encoding="utf-8") as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
            result["num_entries"] = len(trimmed)
            print(
                f"    {ANSI_GREEN}✓ fixed: trimmed to {len(trimmed)} entries{ANSI_RESET}"
            )
            return result

        # If entries exist but are fewer than expected, supplement missing ones.
        if 0 < len(current_entries) < EXPECTED_ENTRIES_PER_PROFILE:
            merged = _sort_entries(current_entries)
            needed = EXPECTED_ENTRIES_PER_PROFILE - len(merged)
            print(
                f"    {ANSI_CYAN}supplementing {needed} missing entries for {profile_id}{ANSI_RESET}"
            )
            seen_signatures = {
                (
                    str((e.get("task") or {}).get("title", "")).strip().lower(),
                    str((e.get("task") or {}).get("description", "")).strip().lower(),
                )
                for e in merged
            }
            next_idx = _next_task_index(merged)
            for attempt in range(1, FIX_RETRY_ATTEMPTS + 1):
                try:
                    candidates = await _generate_entries_for_profile(
                        kb_name=kb_name,
                        profile=profile,
                        knowledge_scope=scope,
                        cfg=cfg,
                        kb_base_dir=kb_base_dir,
                    )
                except Exception as e:
                    last_error = str(e)
                    print(
                        f"    {ANSI_YELLOW}supplement attempt {attempt}/{FIX_RETRY_ATTEMPTS} "
                        f"failed: {e}{ANSI_RESET}"
                    )
                    if attempt < FIX_RETRY_ATTEMPTS:
                        await asyncio.sleep(FIX_RETRY_DELAY_SEC * attempt)
                    continue

                added_this_round = 0
                for c in candidates:
                    sig = (
                        str((c.get("task") or {}).get("title", "")).strip().lower(),
                        str((c.get("task") or {}).get("description", "")).strip().lower(),
                    )
                    if sig in seen_signatures:
                        continue
                    merged.append(_normalize_new_entry(c, next_idx))
                    seen_signatures.add(sig)
                    next_idx += 1
                    added_this_round += 1
                    if len(merged) >= EXPECTED_ENTRIES_PER_PROFILE:
                        break

                if len(merged) >= EXPECTED_ENTRIES_PER_PROFILE:
                    _save_profile_entries(merged[:EXPECTED_ENTRIES_PER_PROFILE], profile_dir)
                    if not (profile_dir / "profile.json").exists():
                        with open(profile_dir / "profile.json", "w", encoding="utf-8") as f:
                            json.dump(profile, f, ensure_ascii=False, indent=2)
                    result["num_entries"] = EXPECTED_ENTRIES_PER_PROFILE
                    print(
                        f"    {ANSI_GREEN}✓ fixed: supplemented to {EXPECTED_ENTRIES_PER_PROFILE} entries{ANSI_RESET}"
                    )
                    return result

                print(
                    f"    {ANSI_YELLOW}supplement attempt {attempt}/{FIX_RETRY_ATTEMPTS} "
                    f"added {added_this_round}, still missing "
                    f"{EXPECTED_ENTRIES_PER_PROFILE - len(merged)}{ANSI_RESET}"
                )
                if attempt < FIX_RETRY_ATTEMPTS:
                    await asyncio.sleep(FIX_RETRY_DELAY_SEC * attempt)

        # Full regeneration (for empty/missing or supplement fallback).
        for attempt in range(1, FIX_RETRY_ATTEMPTS + 1):
            try:
                entries = await _generate_entries_for_profile(
                    kb_name=kb_name,
                    profile=profile,
                    knowledge_scope=scope,
                    cfg=cfg,
                    kb_base_dir=kb_base_dir,
                )
            except Exception as e:
                last_error = str(e)
                print(
                    f"    {ANSI_YELLOW}attempt {attempt}/{FIX_RETRY_ATTEMPTS} "
                    f"failed: {e}{ANSI_RESET}"
                )
                if attempt < FIX_RETRY_ATTEMPTS:
                    await asyncio.sleep(FIX_RETRY_DELAY_SEC * attempt)
                continue

            if entries:
                break

            print(
                f"    {ANSI_YELLOW}attempt {attempt}/{FIX_RETRY_ATTEMPTS} "
                f"returned 0 entries{ANSI_RESET}"
            )
            last_error = "0 entries"
            if attempt < FIX_RETRY_ATTEMPTS:
                await asyncio.sleep(FIX_RETRY_DELAY_SEC * attempt)

        if entries:
            entries = _sort_entries(entries)[:EXPECTED_ENTRIES_PER_PROFILE]
            _save_profile_entries(entries, profile_dir)
            if not (profile_dir / "profile.json").exists():
                with open(profile_dir / "profile.json", "w", encoding="utf-8") as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
            result["num_entries"] = len(entries)
            print(
                f"    {ANSI_GREEN}✓ fixed: {len(entries)} entries{ANSI_RESET}"
            )
        else:
            result["status"] = "error"
            result["error"] = last_error
            print(
                f"    {ANSI_RED}✗ fix failed after {FIX_RETRY_ATTEMPTS} "
                f"attempts: {last_error}{ANSI_RESET}"
            )

        return result


def _load_profile_data(
    kb_name: str, profile_id: str, entries_root: Path
) -> dict | None:
    """Load profile dict from profile.json or profiles.json."""
    profile_json = entries_root / kb_name / "profiles" / profile_id / "profile.json"
    if profile_json.exists():
        with open(profile_json, encoding="utf-8") as f:
            return json.load(f)

    profiles_json = entries_root / kb_name / "profiles.json"
    if profiles_json.exists():
        with open(profiles_json, encoding="utf-8") as f:
            profiles = json.load(f)
        for p in profiles:
            if p.get("profile_id") == profile_id:
                return p

    return None


def _load_scope(kb_name: str, entries_root: Path) -> dict | None:
    scope_path = entries_root / kb_name / "knowledge_scope.json"
    if not scope_path.exists():
        return None
    with open(scope_path, encoding="utf-8") as f:
        return json.load(f)


def scan_entries(
    entries_root: Path, kb_names: list[str]
) -> tuple[
    list[str], list[str], list[str], list[str], list[str],
    dict[str, list[str]], int, int
]:
    """Scan and classify all profiles.

    Returns (ok, warn, empty, missing, count_mismatch, kb_details, total_profiles, total_entries).
    """
    ok_profiles: list[str] = []
    warn_profiles: list[str] = []
    empty_profiles: list[str] = []
    missing_profiles: list[str] = []
    count_mismatch_profiles: list[str] = []
    kb_details: dict[str, list[str]] = {}
    total_profiles = 0
    total_entries = 0

    for kb_name in kb_names:
        kb_dir = entries_root / kb_name
        kb_lines: list[str] = []
        if not kb_dir.exists():
            kb_lines.append(f"  {ANSI_RED}directory not found{ANSI_RESET}")
            kb_details[kb_name] = kb_lines
            continue

        scope_path = kb_dir / "knowledge_scope.json"
        if scope_path.exists():
            try:
                with open(scope_path, encoding="utf-8") as f:
                    scope = json.load(f)
                topic = scope.get("topic", scope.get("title", "?"))
                n_concepts = len(scope.get("concepts", []))
                kb_lines.append(f"  {ANSI_DIM}scope: {topic} ({n_concepts} concepts){ANSI_RESET}")
            except Exception:
                kb_lines.append(f"  {ANSI_YELLOW}scope: parse error{ANSI_RESET}")

        profiles_root = kb_dir / "profiles"
        if not profiles_root.exists():
            kb_lines.append(f"  {ANSI_RED}no profiles/ directory{ANSI_RESET}")
            kb_details[kb_name] = kb_lines
            continue

        profile_dirs = sorted(p for p in profiles_root.iterdir() if p.is_dir())
        for profile_dir in profile_dirs:
            total_profiles += 1
            profile_id = profile_dir.name
            full_id = f"{kb_name}/{profile_id}"
            has_profile_json = (profile_dir / "profile.json").exists()

            status, n_entries, warnings = _classify_profile(profile_dir)
            total_entries += n_entries

            if status == "missing":
                missing_profiles.append(full_id)
                kb_lines.append(
                    f"    {ANSI_RED}✗{ANSI_RESET} {profile_id}  "
                    f"{ANSI_RED}entries.jsonl missing{ANSI_RESET}"
                )
            elif status == "empty":
                empty_profiles.append(full_id)
                kb_lines.append(
                    f"    {ANSI_RED}✗{ANSI_RESET} {profile_id}  "
                    f"{ANSI_RED}0 entries{ANSI_RESET}"
                )
            elif status == "warn":
                warn_profiles.append(full_id)
                if any(w.startswith("entry count mismatch:") for w in warnings):
                    count_mismatch_profiles.append(full_id)
                kb_lines.append(
                    f"    {ANSI_YELLOW}⚠{ANSI_RESET} {profile_id}  "
                    f"{n_entries} entries  "
                    f"{ANSI_YELLOW}{len(warnings)} warnings{ANSI_RESET}  "
                    f"profile.json:{'✓' if has_profile_json else '✗'}"
                )
                for w in warnings[:5]:
                    kb_lines.append(f"      {ANSI_DIM}└ {w}{ANSI_RESET}")
                if len(warnings) > 5:
                    kb_lines.append(
                        f"      {ANSI_DIM}└ ...and {len(warnings) - 5} more{ANSI_RESET}"
                    )
            else:
                ok_profiles.append(full_id)
                kb_lines.append(
                    f"    {ANSI_GREEN}✓{ANSI_RESET} {profile_id}  "
                    f"{n_entries} entries  "
                    f"profile.json:{'✓' if has_profile_json else '✗'}"
                )

        kb_details[kb_name] = kb_lines

    return (
        ok_profiles,
        warn_profiles,
        empty_profiles,
        missing_profiles,
        count_mismatch_profiles,
        kb_details,
        total_profiles,
        total_entries,
    )


def print_report(
    kb_names: list[str],
    entries_root: Path,
    ok_profiles: list[str],
    warn_profiles: list[str],
    empty_profiles: list[str],
    missing_profiles: list[str],
    count_mismatch_profiles: list[str],
    kb_details: dict[str, list[str]],
    total_profiles: int,
    total_entries: int,
) -> None:
    print(f"\n{ANSI_BOLD}Entry Health Check{ANSI_RESET}")
    print(f"Root: {entries_root}")
    print(f"KBs:  {len(kb_names)}\n")
    print("=" * 80)

    for kb_name in kb_names:
        lines = kb_details.get(kb_name, [])
        has_error = any(
            f.startswith(kb_name + "/") for f in empty_profiles + missing_profiles
        )
        has_warn = any(f.startswith(kb_name + "/") for f in warn_profiles)
        if has_error:
            icon = f"{ANSI_RED}✗{ANSI_RESET}"
        elif has_warn:
            icon = f"{ANSI_YELLOW}⚠{ANSI_RESET}"
        else:
            icon = f"{ANSI_GREEN}✓{ANSI_RESET}"
        print(f"\n{icon} {ANSI_BOLD}{kb_name}{ANSI_RESET}")
        for line in lines:
            print(line)

    print("\n" + "=" * 80)
    print(f"\n{ANSI_BOLD}Summary{ANSI_RESET}")
    print(f"  KBs:       {len(kb_names)}")
    print(f"  Profiles:  {total_profiles}")
    print(f"  Entries:   {total_entries}")

    print(f"\n  {ANSI_GREEN}OK{ANSI_RESET}:      {len(ok_profiles)}")
    for p in ok_profiles:
        print(f"    {ANSI_DIM}{p}{ANSI_RESET}")

    print(f"  {ANSI_YELLOW}WARN{ANSI_RESET}:    {len(warn_profiles)}")
    for p in warn_profiles:
        print(f"    {ANSI_DIM}{p}{ANSI_RESET}")

    print(f"  {ANSI_RED}EMPTY{ANSI_RESET}:   {len(empty_profiles)}")
    for p in empty_profiles:
        print(f"    {ANSI_DIM}{p}{ANSI_RESET}")

    print(f"  {ANSI_RED}MISSING{ANSI_RESET}: {len(missing_profiles)}")
    for p in missing_profiles:
        print(f"    {ANSI_DIM}{p}{ANSI_RESET}")

    print(
        f"  {ANSI_YELLOW}COUNT_MISMATCH{ANSI_RESET}: {len(count_mismatch_profiles)} "
        f"(expected {EXPECTED_ENTRIES_PER_PROFILE})"
    )
    for p in count_mismatch_profiles:
        print(f"    {ANSI_DIM}{p}{ANSI_RESET}")

    print()


async def run(args: argparse.Namespace) -> None:
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (PROJECT_ROOT / output_root).resolve()
    entries_root = output_root / "entries"

    if not entries_root.exists():
        print(f"{ANSI_RED}Entries root not found: {entries_root}{ANSI_RESET}")
        sys.exit(1)

    if args.kb_names:
        kb_names = sorted(set(n.strip() for n in args.kb_names.split(",") if n.strip()))
    else:
        kb_names = sorted(d.name for d in entries_root.iterdir() if d.is_dir())

    if not kb_names:
        print(f"{ANSI_RED}No KBs found in {entries_root}{ANSI_RESET}")
        sys.exit(1)

    # --- First pass: scan ---
    (
        ok,
        warn,
        empty,
        missing,
        count_mismatch,
        details,
        total_profiles,
        total_entries,
    ) = scan_entries(entries_root, kb_names)
    print_report(
        kb_names, entries_root, ok, warn, empty, missing, count_mismatch, details,
        total_profiles, total_entries,
    )

    unhealthy = empty + missing + count_mismatch
    if not args.fix or not unhealthy:
        if unhealthy:
            print(
                f"Run with {ANSI_CYAN}--fix{ANSI_RESET} to regenerate/fix unhealthy entries.\n"
            )
            sys.exit(1)
        return

    # --- Fix pass ---
    kb_base_dir = Path(args.kb_dir)
    if not kb_base_dir.is_absolute():
        kb_base_dir = (PROJECT_ROOT / kb_base_dir).resolve()

    cfg_path = Path(args.config)
    if not cfg_path.is_absolute():
        cfg_path = (PROJECT_ROOT / cfg_path).resolve()
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    print(f"\n{ANSI_BOLD}Fixing {len(unhealthy)} unhealthy profiles...{ANSI_RESET}\n")

    sem = asyncio.Semaphore(args.concurrency)
    fix_tasks = []
    skipped: list[str] = []

    for full_id in unhealthy:
        kb_name, profile_id = full_id.split("/", 1)

        scope = _load_scope(kb_name, entries_root)
        if not scope:
            print(
                f"  {ANSI_RED}✗ {full_id}: no knowledge_scope.json, cannot fix{ANSI_RESET}"
            )
            skipped.append(full_id)
            continue

        profile = _load_profile_data(kb_name, profile_id, entries_root)
        if not profile:
            print(
                f"  {ANSI_RED}✗ {full_id}: no profile data found, cannot fix{ANSI_RESET}"
            )
            skipped.append(full_id)
            continue

        profile_dir = entries_root / kb_name / "profiles" / profile_id
        profile_dir.mkdir(parents=True, exist_ok=True)

        print(f"  {ANSI_CYAN}→ fixing {full_id}...{ANSI_RESET}")
        fix_tasks.append(
            _fix_one_profile(
                kb_name=kb_name,
                profile_id=profile_id,
                profile=profile,
                scope=scope,
                cfg=cfg,
                kb_base_dir=str(kb_base_dir),
                profile_dir=profile_dir,
                semaphore=sem,
            )
        )

    if fix_tasks:
        results = await asyncio.gather(*fix_tasks, return_exceptions=True)
        fixed = sum(
            1
            for r in results
            if not isinstance(r, Exception) and r.get("status") == "ok"
        )
        failed = len(results) - fixed
    else:
        fixed = 0
        failed = 0

    # --- Second pass: re-scan ---
    print(f"\n{'=' * 80}")
    print(f"{ANSI_BOLD}Post-fix re-scan{ANSI_RESET}")
    ok2, warn2, empty2, missing2, count_mismatch2, details2, tp2, te2 = scan_entries(
        entries_root, kb_names
    )
    print_report(
        kb_names,
        entries_root,
        ok2,
        warn2,
        empty2,
        missing2,
        count_mismatch2,
        details2,
        tp2,
        te2,
    )

    print(f"{ANSI_BOLD}Fix summary{ANSI_RESET}")
    print(f"  Fixed:   {ANSI_GREEN}{fixed}{ANSI_RESET}")
    print(f"  Failed:  {ANSI_RED}{failed}{ANSI_RESET}")
    print(f"  Skipped: {ANSI_YELLOW}{len(skipped)}{ANSI_RESET}")
    if skipped:
        for s in skipped:
            print(f"    {ANSI_DIM}{s}{ANSI_RESET}")
    print()

    if empty2 or missing2 or count_mismatch2:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check & fix entry health")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Pipeline output root (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--kb-names",
        default=None,
        help="Comma-separated KB names to check (default: all)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help=(
            "Fix unhealthy profiles: regenerate empty/missing, "
            "supplement <3 entries, trim >3 entries"
        ),
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
        "--concurrency",
        type=int,
        default=6,
        help="Max parallel fix tasks (default: 6)",
    )
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
