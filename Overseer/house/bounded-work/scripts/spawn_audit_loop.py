#!/usr/bin/env python3
"""Create and optionally execute the first-class audit-loop room."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
import uuid
from typing import Any


ROOT = pathlib.Path("/home/overseer")
FINITE_ROOT = pathlib.Path(os.environ.get("OVERSEER_FINITE_LOOP_ROOT", str(ROOT / "state/finite-loops")))
AUDIT_ROOT = pathlib.Path(os.environ.get("OVERSEER_AUDIT_LOOP_ROOT", str(ROOT / "state/audit-loop")))
LOOP_REGISTRY = ROOT / "scripts" / "finite_loop_registry.py"
EXECUTOR = ROOT / "scripts" / "finite_loop_executor.py"
AUDIT_BRIEF = ROOT / "scripts" / "compile_audit_loop_brief.py"
PYTHON_BIN = pathlib.Path("/run/current-system/sw/bin/overseer-python3")
if not PYTHON_BIN.exists():
    PYTHON_BIN = pathlib.Path(sys.executable)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dirs() -> None:
    for path in (
        AUDIT_ROOT,
        AUDIT_ROOT / "missions",
        AUDIT_ROOT / "findings",
        AUDIT_ROOT / "launches",
    ):
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_json_command(args: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["OVERSEER_FINITE_LOOP_ROOT"] = str(FINITE_ROOT)
    result = subprocess.run(args, check=False, text=True, capture_output=True, env=env)
    if result.returncode != 0:
        fail((result.stderr or result.stdout or f"command failed: {' '.join(args)}").strip())
    return json.loads(result.stdout)


def finite_registry(args: list[str]) -> dict[str, Any]:
    return run_json_command([str(PYTHON_BIN), str(LOOP_REGISTRY), *args])


def build_task_summary(mission_path: pathlib.Path) -> str:
    return (
        "You are the house audit-loop. Start from the mission contract at "
        f"{mission_path}, then reopen WAKE.md, CURRENT-FRONTIER.md, OPENING-CONTRACT.json, "
        "and the most relevant rooms named in the mission. Read deeply enough to understand "
        "the current house posture before judging. Search for hidden problems, weak assumptions, "
        "stale doctrine, contradictory surfaces, missing tests, or looming failure modes. "
        "Do not fix by default. Write a severity-ordered findings note to the findings path named "
        "in the mission contract so the rest of the house can hear you. If no substantive findings "
        "exist, say so explicitly in that note. Then answer the executor JSON schema honestly."
    )


def build_mission(mode: str, mission_path: pathlib.Path) -> dict[str, Any]:
    start_paths = [
        "/home/overseer/WAKE.md",
        "/home/overseer/CURRENT-FRONTIER.md",
        "/home/overseer/OPENING-CONTRACT.json",
        "/home/overseer/docs/recovery-kernel.md",
    ]
    if mode == "looper-bootstrap":
        start_paths.extend(
            [
                "/home/overseer/docs/loop-construction-plan.md",
                "/home/overseer/docs/loop-prompt-sequences.md",
                "/home/overseer/docs/looper-bootstrap-ecology.md",
                "/home/overseer/docs/looper-stage-gates.md",
                "/home/overseer/docs/delegation-power-model.md",
            ]
        )
        scope = "audit the looping ecology, stage gates, and delegation doctrine"
    else:
        start_paths.extend(
            [
                "/home/overseer/ALLOCATION.md",
                "/home/overseer/ATTENTION.md",
                "/home/overseer/SCIENCE.md",
                "/home/overseer/AUTH.md",
                "/home/overseer/COREDUMPS.md",
                "/home/overseer/DEADMAN.md",
                "/home/overseer/docs/system-alerts.md",
                "/home/overseer/docs/codex-load-balancer.md",
            ]
        )
        scope = "serious broad house audit for hidden problems and skeptical review"
    return {
        "mission_id": mission_path.stem,
        "written_at": utc_now_iso(),
        "loop_class": "audit-loop",
        "audit_mode": mode,
        "scope_summary": scope,
        "read_first_paths": start_paths,
        "non_goals": [
            "do not silently repair by default",
            "do not widen into multiple unrelated missions",
            "do not normalize your own findings without evidence",
        ],
        "stop_rule": (
            "stop early if the truthful next move is to hand back sharper judgment rather than spend more turns"
        ),
    }


def write_findings_placeholder(path: pathlib.Path, mission: dict[str, Any], loop_id: str) -> None:
    text = (
        f"# Audit Findings for {loop_id}\n\n"
        f"- mission_id: {mission['mission_id']}\n"
        f"- audit_mode: {mission['audit_mode']}\n"
        f"- status: pending execution\n\n"
        "<!-- audit findings pending -->\n"
    )
    write_text(path, text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["serious-house-audit", "looper-bootstrap"], default="serious-house-audit")
    parser.add_argument("--turn-budget", type=int, default=10)
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--requested-profile")
    parser.add_argument("--search", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--no-execute", action="store_true")
    parser.add_argument("--meta-out")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    mission_id = f"audit-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:6]}"
    mission_path = AUDIT_ROOT / "missions" / f"{mission_id}.json"
    mission = build_mission(args.mode, mission_path)
    write_json(mission_path, mission)

    created_loop = finite_registry(
        [
            "create",
            "--task-summary",
            build_task_summary(mission_path),
            "--turn-budget",
            str(args.turn_budget),
            "--loop-class",
            "audit-loop",
            "--mission-path",
            str(mission_path),
            "--session-policy",
            "separate-session",
        ]
    )
    loop_id = created_loop["loop_id"]
    findings_path = AUDIT_ROOT / "findings" / f"{loop_id}.md"
    mission.update(
        {
            "loop_id": loop_id,
            "consumer_id": created_loop["consumer_id"],
            "loop_status_path": f"/home/overseer/state/finite-loops/runs/{loop_id}/status.json",
            "findings_path": str(findings_path),
        }
    )
    write_json(mission_path, mission)
    write_findings_placeholder(findings_path, mission, loop_id)

    latest_status = finite_registry(["status", "--loop-id", loop_id])
    run_root = FINITE_ROOT / "runs" / loop_id
    launch_payload: dict[str, Any] = {
        "written_at": utc_now_iso(),
        "loop_id": loop_id,
        "loop_class": "audit-loop",
        "audit_mode": args.mode,
        "mission_path": str(mission_path),
        "findings_path": str(findings_path),
        "workspace": str(pathlib.Path(args.workspace)),
        "turn_budget": args.turn_budget,
        "max_turns": args.max_turns,
        "wait_seconds": args.wait_seconds,
        "search": args.search,
        "executed": not args.no_execute,
        "executor_exit_code": None,
        "executor_stdout_tail": [],
        "executor_stderr_tail": [],
        "loop_status": latest_status,
    }
    launch_path = AUDIT_ROOT / "launches" / f"{loop_id}.json"
    launch_payload["launch_path"] = str(launch_path)
    write_json(launch_path, launch_payload)
    write_json(AUDIT_ROOT / "launches" / "latest.json", launch_payload)
    write_json(run_root / "spawn.json", launch_payload)
    subprocess.run([str(PYTHON_BIN), str(AUDIT_BRIEF)], check=False, capture_output=True, text=True)

    result = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    if not args.no_execute:
        command = [
            str(PYTHON_BIN),
            str(EXECUTOR),
            "--loop-id",
            loop_id,
            "--workspace",
            str(pathlib.Path(args.workspace)),
            "--max-turns",
            str(args.max_turns),
            "--wait-seconds",
            str(args.wait_seconds),
        ]
        if args.requested_profile:
            command.extend(["--requested-profile", args.requested_profile])
        command.append("--search" if args.search else "--no-search")
        result = subprocess.run(command, check=False, text=True, capture_output=True)

    latest_status = finite_registry(["status", "--loop-id", loop_id])
    launch_payload.update(
        {
            "executor_exit_code": result.returncode,
            "executor_stdout_tail": [line for line in result.stdout.splitlines()[-20:] if line.strip()],
            "executor_stderr_tail": [line for line in result.stderr.splitlines()[-20:] if line.strip()],
            "loop_status": latest_status,
        }
    )
    write_json(launch_path, launch_payload)
    write_json(AUDIT_ROOT / "launches" / "latest.json", launch_payload)
    write_json(run_root / "spawn.json", launch_payload)
    subprocess.run([str(PYTHON_BIN), str(AUDIT_BRIEF)], check=False, capture_output=True, text=True)

    if args.meta_out:
        write_json(pathlib.Path(args.meta_out), launch_payload)
    print(json.dumps(launch_payload, indent=2, sort_keys=True))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
