#!/usr/bin/env python3
"""Prepare isolated Codex/runtime surfaces for a bounded finite loop."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = pathlib.Path("/home/overseer")
FINITE_ROOT = pathlib.Path(os.environ.get("OVERSEER_FINITE_LOOP_ROOT", str(ROOT / "state/finite-loops")))
CANON_CODEX_HOME = ROOT / ".codex"
RUNTIME_ROOT = FINITE_ROOT / "runtime"
WORKTREES_ROOT = FINITE_ROOT / "worktrees"
TASKS_ROOT = FINITE_ROOT / "tasks"
LATEST_PATH = RUNTIME_ROOT / "latest.json"


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def repo_toplevel(path: pathlib.Path) -> pathlib.Path | None:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    return pathlib.Path(raw).resolve() if raw else None


def ensure_codex_home(loop_root: pathlib.Path) -> dict[str, str]:
    codex_home = loop_root / "codex-home"
    sessions = codex_home / "sessions"
    history = codex_home / "history.jsonl"
    auth = codex_home / "auth.json"
    sessions.mkdir(parents=True, exist_ok=True)
    history.parent.mkdir(parents=True, exist_ok=True)
    if not history.exists():
        history.write_text("", encoding="utf-8")
    canon_config = CANON_CODEX_HOME / "config.toml"
    runtime_config = codex_home / "config.toml"
    if canon_config.exists():
        shutil.copyfile(canon_config, runtime_config)
        os.chmod(runtime_config, 0o600)
    return {
        "codex_home": str(codex_home),
        "config_path": str(runtime_config),
        "sessions_root": str(sessions),
        "history_path": str(history),
        "active_auth_path": str(auth),
    }


def ensure_worktree(loop_id: str, source_workspace: pathlib.Path) -> dict[str, Any]:
    source_workspace = source_workspace.resolve()
    repo_root = repo_toplevel(source_workspace)
    if repo_root is None:
        task_root = TASKS_ROOT / loop_id
        task_root.mkdir(parents=True, exist_ok=True)
        return {
            "workspace_mode": "shared-workspace",
            "workspace_root": str(source_workspace),
            "workspace_path": str(source_workspace),
            "task_root": str(task_root),
            "repo_root": None,
            "worktree_path": None,
        }

    relative = source_workspace.relative_to(repo_root)
    worktree_path = WORKTREES_ROOT / loop_id
    if not worktree_path.exists():
        worktree_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "-C", str(repo_root), "worktree", "add", "--detach", str(worktree_path), "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "git worktree add failed").strip())
    workspace_path = worktree_path / relative
    workspace_path.mkdir(parents=True, exist_ok=True)
    return {
        "workspace_mode": "git-worktree",
        "workspace_root": str(worktree_path),
        "workspace_path": str(workspace_path),
        "task_root": None,
        "repo_root": str(repo_root),
        "worktree_path": str(worktree_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-id", required=True)
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--json-only", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    loop_root = RUNTIME_ROOT / args.loop_id
    loop_root.mkdir(parents=True, exist_ok=True)
    source_workspace = pathlib.Path(args.workspace)
    prepared_at = utc_now_iso()

    codex_payload = ensure_codex_home(loop_root)
    workspace_payload = ensure_worktree(args.loop_id, source_workspace)
    runtime_lock_root = ROOT / "state" / "codex-load-balancer" / "runtime-locks"
    runtime_lock_root.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "loop_id": args.loop_id,
        "prepared_at": prepared_at,
        "runtime_root": str(loop_root),
        "source_workspace": str(source_workspace.resolve()),
        "runtime_lock_scope": "profile",
        "runtime_lock_root": str(runtime_lock_root),
        **codex_payload,
        **workspace_payload,
    }
    write_json(loop_root / "runtime.json", payload)
    write_json(LATEST_PATH, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
