#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Data Migration Script
===========================

Migrates user data from old directory structure to new structure:

Old structure:
data/user/
├── solver_sessions.json
├── chat_sessions.json
├── user_history.json (deprecated, to be deleted)
├── settings.json (deprecated, to be deleted)
├── llm_providers.json (deprecated, to be deleted)
├── embedding_providers.json (deprecated, to be deleted)
├── solve/
├── question/
├── research/
├── co-writer/
├── guide/
├── notebook/
├── run_code_workspace/
├── logs/
└── settings/

New structure:
data/user/
├── agent/
│   ├── solve/
│   │   ├── sessions.json
│   │   └── {task_id}/
│   ├── chat/
│   │   └── sessions.json
│   ├── question/
│   ├── research/
│   ├── co-writer/
│   ├── guide/
│   ├── run_code_workspace/
│   └── logs/
├── workspace/
│   └── notebook/
└── settings/

Usage:
    python scripts/migrate_user_data.py
"""

import json
import shutil
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_banner(title: str):
    """Print a section banner."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(message: str, status: str = ""):
    """Print a step message."""
    if status:
        print(f"  [OK] {message} - {status}")
    else:
        print(f"  ... {message}")


def move_directory(src: Path, dst: Path) -> bool:
    """
    Move a directory from src to dst.
    If dst already exists, merge contents.
    """
    if not src.exists():
        return False
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if dst.exists():
        # Merge contents
        for item in src.iterdir():
            dst_item = dst / item.name
            if item.is_dir():
                if dst_item.exists():
                    # Recursively merge
                    move_directory(item, dst_item)
                else:
                    shutil.move(str(item), str(dst_item))
            else:
                if not dst_item.exists():
                    shutil.move(str(item), str(dst_item))
        # Remove empty src directory
        if src.exists() and not any(src.iterdir()):
            src.rmdir()
    else:
        shutil.move(str(src), str(dst))
    
    return True


def move_file(src: Path, dst: Path) -> bool:
    """Move a file from src to dst."""
    if not src.exists():
        return False
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if dst.exists():
        # Backup existing file
        backup = dst.with_suffix(dst.suffix + ".backup")
        shutil.move(str(dst), str(backup))
        print_step(f"Backed up existing {dst.name}", f"-> {backup.name}")
    
    shutil.move(str(src), str(dst))
    return True


def delete_file(path: Path) -> bool:
    """Delete a file if it exists."""
    if path.exists():
        path.unlink()
        return True
    return False


def migrate():
    """Run the migration."""
    user_dir = project_root / "data" / "user"
    
    if not user_dir.exists():
        print("No user data directory found. Nothing to migrate.")
        return
    
    print_banner("User Data Migration")
    print(f"Source directory: {user_dir}")
    
    # =========================================================================
    # Step 1: Create new directory structure
    # =========================================================================
    print_banner("Step 1: Creating New Directory Structure")
    
    agent_dir = user_dir / "agent"
    workspace_dir = user_dir / "workspace"
    
    agent_modules = ["solve", "chat", "question", "research", "co-writer", "guide", "run_code_workspace", "logs"]
    
    for module in agent_modules:
        module_dir = agent_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        print_step(f"Created agent/{module}/")
    
    # Co-writer subdirectories
    (agent_dir / "co-writer" / "audio").mkdir(parents=True, exist_ok=True)
    (agent_dir / "co-writer" / "tool_calls").mkdir(parents=True, exist_ok=True)
    print_step("Created agent/co-writer/audio/ and tool_calls/")
    
    # Research reports directory
    (agent_dir / "research" / "reports").mkdir(parents=True, exist_ok=True)
    print_step("Created agent/research/reports/")
    
    # Workspace/notebook
    (workspace_dir / "notebook").mkdir(parents=True, exist_ok=True)
    print_step("Created workspace/notebook/")
    
    # =========================================================================
    # Step 2: Move session files
    # =========================================================================
    print_banner("Step 2: Moving Session Files")
    
    # Move solver_sessions.json -> agent/solve/sessions.json
    src = user_dir / "solver_sessions.json"
    dst = agent_dir / "solve" / "sessions.json"
    if move_file(src, dst):
        print_step("Moved solver_sessions.json", "-> agent/solve/sessions.json")
    else:
        print_step("solver_sessions.json not found", "skipped")
    
    # Move chat_sessions.json -> agent/chat/sessions.json
    src = user_dir / "chat_sessions.json"
    dst = agent_dir / "chat" / "sessions.json"
    if move_file(src, dst):
        print_step("Moved chat_sessions.json", "-> agent/chat/sessions.json")
    else:
        print_step("chat_sessions.json not found", "skipped")
    
    # =========================================================================
    # Step 3: Move module directories
    # =========================================================================
    print_banner("Step 3: Moving Module Directories")
    
    moves = [
        ("solve", "agent/solve"),
        ("question", "agent/question"),
        ("research", "agent/research"),
        ("co-writer", "agent/co-writer"),
        ("guide", "agent/guide"),
        ("run_code_workspace", "agent/run_code_workspace"),
        ("logs", "agent/logs"),
        ("notebook", "workspace/notebook"),
    ]
    
    for src_name, dst_name in moves:
        src = user_dir / src_name
        dst = user_dir / dst_name
        
        # Skip if same path (already in correct location)
        if src == dst:
            print_step(f"{src_name}/", "already in correct location")
            continue
        
        if src.exists():
            if move_directory(src, dst):
                print_step(f"Moved {src_name}/", f"-> {dst_name}/")
        else:
            print_step(f"{src_name}/", "not found, skipped")
    
    # =========================================================================
    # Step 4: Delete deprecated files
    # =========================================================================
    print_banner("Step 4: Deleting Deprecated Files")
    
    deprecated_files = [
        "user_history.json",
        "settings.json",
        "llm_providers.json",
        "embedding_providers.json",
    ]
    
    for filename in deprecated_files:
        path = user_dir / filename
        if delete_file(path):
            print_step(f"Deleted {filename}")
        else:
            print_step(f"{filename}", "not found, skipped")
    
    # =========================================================================
    # Step 5: Clean up empty directories
    # =========================================================================
    print_banner("Step 5: Cleaning Up Empty Directories")
    
    # Try to remove any empty old directories
    old_dirs = ["solve", "question", "research", "co-writer", "guide", "notebook", "run_code_workspace", "logs"]
    for dir_name in old_dirs:
        old_dir = user_dir / dir_name
        if old_dir.exists() and old_dir.is_dir():
            try:
                if not any(old_dir.iterdir()):
                    old_dir.rmdir()
                    print_step(f"Removed empty {dir_name}/")
            except OSError:
                pass  # Directory not empty
    
    # =========================================================================
    # Done
    # =========================================================================
    print_banner("Migration Complete")
    print("""
New structure:
data/user/
├── agent/
│   ├── solve/sessions.json + task directories
│   ├── chat/sessions.json
│   ├── question/batch directories
│   ├── research/reports/
│   ├── co-writer/audio/ + tool_calls/
│   ├── guide/session files
│   ├── run_code_workspace/
│   └── logs/
├── workspace/
│   └── notebook/
└── settings/
    """)


def verify_migration():
    """Verify the migration was successful."""
    print_banner("Verification")
    
    user_dir = project_root / "data" / "user"
    
    # Check required directories exist
    required = [
        "agent/solve",
        "agent/chat",
        "agent/question",
        "agent/research/reports",
        "agent/co-writer/audio",
        "agent/co-writer/tool_calls",
        "agent/guide",
        "agent/run_code_workspace",
        "agent/logs",
        "workspace/notebook",
        "settings",
    ]
    
    all_ok = True
    for path in required:
        full_path = user_dir / path
        if full_path.exists():
            print_step(f"{path}/", "OK")
        else:
            print_step(f"{path}/", "MISSING!")
            all_ok = False
    
    # Check no deprecated files remain
    deprecated = ["user_history.json", "settings.json", "llm_providers.json", "embedding_providers.json"]
    for filename in deprecated:
        path = user_dir / filename
        if path.exists():
            print_step(f"{filename}", "STILL EXISTS (should be deleted)")
            all_ok = False
    
    if all_ok:
        print("\n  [OK] All verifications passed!")
    else:
        print("\n  [FAIL] Some issues found. Please check above.")
    
    return all_ok


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate user data to new directory structure")
    parser.add_argument("--verify", action="store_true", help="Only verify migration status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    elif args.dry_run:
        print("DRY RUN - No changes will be made")
        print_banner("Would perform the following actions:")
        
        user_dir = project_root / "data" / "user"
        
        print("\n  Session files to move:")
        if (user_dir / "solver_sessions.json").exists():
            print("    solver_sessions.json -> agent/solve/sessions.json")
        if (user_dir / "chat_sessions.json").exists():
            print("    chat_sessions.json -> agent/chat/sessions.json")
        
        print("\n  Directories to move:")
        for name in ["solve", "question", "research", "co-writer", "guide", "notebook", "run_code_workspace", "logs"]:
            src = user_dir / name
            if src.exists():
                if name == "notebook":
                    print(f"    {name}/ -> workspace/notebook/")
                else:
                    print(f"    {name}/ -> agent/{name}/")
        
        print("\n  Files to delete:")
        for name in ["user_history.json", "settings.json", "llm_providers.json", "embedding_providers.json"]:
            if (user_dir / name).exists():
                print(f"    {name}")
    else:
        migrate()
        verify_migration()
