#!/usr/bin/env python
"""Stop processes recorded by scripts/start_web.py."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from start_web import stop_recorded_processes  # noqa: E402


def main() -> None:
    stop_recorded_processes()


if __name__ == "__main__":
    main()
