#!/usr/bin/env python3
"""Create and execute a bounded finite loop as one coherent house action."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any


ROOT = pathlib.Path("/home/overseer")
FINITE_ROOT = pathlib.Path(os.environ.get("OVERSEER_FINITE_LOOP_ROOT", str(ROOT / "state/finite-loops")))
GROUP_ROOT = pathlib.Path(os.environ.get("OVERSEER_LOOP_GROUP_ROOT", str(ROOT / "state/loop-groups")))
LOOP_REGISTRY = ROOT / "scripts" / "finite_loop_registry.py"
GROUP_REGISTRY = ROOT / "scripts" / "loop_group_registry.py"
EXECUTOR = ROOT / "scripts" / "finite_loop_executor.py"
PYTHON_BIN = pathlib.Path("/run/current-system/sw/bin/overseer-python3")
if not PYTHON_BIN.exists():
    PYTHON_BIN = pathlib.Path(sys.executable)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_json_command(args: list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    result = subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        fail((result.stderr or result.stdout or f"command failed: {' '.join(args)}").strip())
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON from {' '.join(args)}: {exc}")


def finite_registry(args: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["OVERSEER_FINITE_LOOP_ROOT"] = str(FINITE_ROOT)
    return run_json_command([str(PYTHON_BIN), str(LOOP_REGISTRY), *args], env=env)


def group_registry(args: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["OVERSEER_LOOP_GROUP_ROOT"] = str(GROUP_ROOT)
    env["OVERSEER_FINITE_LOOP_ROOT"] = str(FINITE_ROOT)
    return run_json_command([str(PYTHON_BIN), str(GROUP_REGISTRY), *args], env=env)


def prepare_group(args: argparse.Namespace) -> tuple[str | None, dict[str, Any] | None]:
    if args.group_id and args.group_purpose:
        fail("choose either --group-id or --group-purpose, not both")
    if args.group_id:
        return args.group_id, group_registry(["status", "--group-id", args.group_id])
    if not args.group_purpose:
        return None, None
    created = group_registry(
        [
            "create",
            "--purpose",
            args.group_purpose,
            "--stability-class",
            args.group_stability_class,
            "--coordination-mode",
            args.group_coordination_mode,
            *(["--summary", args.group_summary] if args.group_summary else []),
            *(["--resume-hint", args.group_resume_hint] if args.group_resume_hint else []),
        ]
    )
    return created["group_id"], created


def tail_text(text: str | None, limit: int = 40) -> list[str]:
    if not text:
        return []
    lines = [line for line in text.splitlines() if line.strip()]
    clipped = [line if len(line) <= 240 else f"{line[:237]}..." for line in lines]
    return clipped[-limit:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-summary", required=True)
    parser.add_argument("--turn-budget", type=int, required=True)
    parser.add_argument("--loop-class", default="generic")
    parser.add_argument("--mission-path")
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--requested-profile")
    parser.add_argument("--session-policy", default="separate-session", choices=["separate-session", "shared-risky"])
    parser.add_argument("--parent-session-id")
    parser.add_argument("--consumer-id")
    parser.add_argument("--note")
    parser.add_argument("--group-id")
    parser.add_argument("--group-purpose")
    parser.add_argument("--group-stability-class", default="experimental", choices=["stable", "unstable", "experimental"])
    parser.add_argument("--group-coordination-mode", default="serial", choices=["serial", "parallel", "rolling", "advisory"])
    parser.add_argument("--group-summary")
    parser.add_argument("--group-resume-hint")
    parser.add_argument("--max-turns", type=int, default=1)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--search", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--meta-out")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.turn_budget < 1:
        fail("--turn-budget must be positive")
    if args.max_turns < 1:
        fail("--max-turns must be positive")

    workspace = pathlib.Path(args.workspace)
    started_at = utc_now_iso()
    group_id, prepared_group = prepare_group(args)
    created_loop = finite_registry(
        [
            "create",
            "--task-summary",
            args.task_summary,
            "--turn-budget",
            str(args.turn_budget),
            "--loop-class",
            args.loop_class,
            *(["--mission-path", args.mission_path] if args.mission_path else []),
            "--session-policy",
            args.session_policy,
            *(["--requested-profile", args.requested_profile] if args.requested_profile else []),
            *(["--parent-session-id", args.parent_session_id] if args.parent_session_id else []),
            *(["--consumer-id", args.consumer_id] if args.consumer_id else []),
            *(["--note", args.note] if args.note else []),
        ]
    )
    loop_id = created_loop["loop_id"]
    run_root = FINITE_ROOT / "runs" / loop_id
    executor_latest = run_root / "executor-latest.json"

    command = [
        str(PYTHON_BIN),
        str(EXECUTOR),
        "--loop-id",
        loop_id,
        "--workspace",
        str(workspace),
        "--max-turns",
        str(args.max_turns),
        "--wait-seconds",
        str(args.wait_seconds),
    ]
    if group_id:
        command.extend(["--group-id", group_id])
    if args.requested_profile:
        command.extend(["--requested-profile", args.requested_profile])
    command.append("--search" if args.search else "--no-search")

    result = subprocess.run(command, check=False, capture_output=True, text=True)

    latest_loop_status = finite_registry(["status", "--loop-id", loop_id])
    latest_group_status = group_registry(["status", "--group-id", group_id]) if group_id else None
    completed_at = utc_now_iso()
    payload: dict[str, Any] = {
        "started_at": started_at,
        "completed_at": completed_at,
        "loop_id": loop_id,
        "group_id": group_id,
        "workspace": str(workspace),
        "task_summary": args.task_summary,
        "loop_class": args.loop_class,
        "mission_path": args.mission_path,
        "turn_budget": args.turn_budget,
        "max_turns": args.max_turns,
        "requested_profile": args.requested_profile,
        "search": args.search,
        "executor_exit_code": result.returncode,
        "executor_stdout_tail": tail_text(result.stdout),
        "executor_stderr_tail": tail_text(result.stderr) if result.returncode != 0 else [],
        "create_result": created_loop,
        "prepared_group": prepared_group,
        "loop_status": latest_loop_status,
        "group_status": latest_group_status,
        "executor_latest_path": str(executor_latest) if executor_latest.exists() else None,
        "receipt_fanout_complete": executor_latest.exists(),
    }
    if executor_latest.exists():
        payload["executor_latest"] = load_json(executor_latest)

    write_json(run_root / "spawn.json", payload)
    write_json(FINITE_ROOT / "spawn-latest.json", payload)
    if args.meta_out:
        write_json(pathlib.Path(args.meta_out), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
