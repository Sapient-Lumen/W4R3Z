#!/usr/bin/env python3
"""Create an explicit follow-up finite loop from an existing loop or recovery packet."""

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

FOLLOWUPS_DIR = FINITE_ROOT / "followups"
TERMINAL_STATES = {"completed", "blocked", "failed", "abandoned", "cancelled"}
GROUP_TERMINAL_STATES = {"retired", "cancelled"}


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


def tail_text(text: str | None, limit: int = 40) -> list[str]:
    if not text:
        return []
    lines = [line for line in text.splitlines() if line.strip()]
    clipped = [line if len(line) <= 240 else f"{line[:237]}..." for line in lines]
    return clipped[-limit:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-id")
    parser.add_argument("--recovery-path")
    parser.add_argument("--task-summary")
    parser.add_argument("--turn-budget", type=int, default=1)
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--requested-profile")
    parser.add_argument("--session-policy", choices=["separate-session", "shared-risky"])
    parser.add_argument("--consumer-id")
    parser.add_argument("--note")
    parser.add_argument("--group-id")
    parser.add_argument("--inherit-group", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--allow-nonterminal-source", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--run-now", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--max-turns", type=int, default=1)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--search", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--meta-out")
    return parser.parse_args()


def load_source_packet(args: argparse.Namespace) -> dict[str, Any]:
    if bool(args.loop_id) == bool(args.recovery_path):
        fail("choose exactly one of --loop-id or --recovery-path")
    if args.recovery_path:
        return load_json(pathlib.Path(args.recovery_path))
    return finite_registry(["reconstruct", "--loop-id", args.loop_id])


def load_source_status(packet: dict[str, Any]) -> dict[str, Any]:
    return load_json(pathlib.Path(packet["status_path"]))


def load_latest_turn_response(packet: dict[str, Any]) -> dict[str, Any] | None:
    latest_turn_path = packet.get("latest_turn_artifact_path")
    if not latest_turn_path:
        return None
    latest_turn = load_json(pathlib.Path(latest_turn_path))
    response = latest_turn.get("turn_response")
    return response if isinstance(response, dict) else None


def load_latest_turn_artifact(packet: dict[str, Any]) -> dict[str, Any] | None:
    latest_turn_path = packet.get("latest_turn_artifact_path")
    if not latest_turn_path:
        return None
    return load_json(pathlib.Path(latest_turn_path))


def derive_task_summary(
    *,
    args: argparse.Namespace,
    packet: dict[str, Any],
    source_status: dict[str, Any],
    latest_turn_response: dict[str, Any] | None,
) -> tuple[str, str]:
    if args.task_summary:
        return args.task_summary, "explicit-task-summary"
    candidate = packet.get("followup_candidate") or {}
    if candidate.get("derived_task_summary"):
        return candidate["derived_task_summary"], "recovery-followup-candidate"
    if latest_turn_response:
        next_turn_prompt = (latest_turn_response.get("next_turn_prompt") or "").strip()
        if next_turn_prompt:
            return next_turn_prompt, "latest-turn-next-turn-prompt"
        resume_hint = (latest_turn_response.get("resume_hint") or "").strip()
        if resume_hint:
            return resume_hint, "latest-turn-resume-hint"
    if packet.get("recovery_resume_hint"):
        return packet["recovery_resume_hint"], "recovery-resume-hint"
    if source_status.get("last_task_state"):
        return source_status["last_task_state"], "last-task-state"
    return source_status["task_summary"], "source-task-summary"


def build_note(
    *,
    args: argparse.Namespace,
    packet: dict[str, Any],
    source_status: dict[str, Any],
    task_summary_source: str,
) -> str:
    pieces = [
        f"Follow-up spawned from {packet['loop_id']}.",
        f"Source state: {source_status['state']}.",
        f"Source phase: {source_status['phase']}.",
        f"Derived task source: {task_summary_source}.",
    ]
    if source_status.get("last_turn_outcome"):
        pieces.append(f"Last turn outcome: {source_status['last_turn_outcome']}.")
    if source_status.get("last_task_state"):
        pieces.append(f"Last task state: {source_status['last_task_state']}.")
    if packet.get("recovery_resume_hint"):
        pieces.append(f"Recovery resume hint: {packet['recovery_resume_hint']}")
    if args.note:
        pieces.append(args.note)
    return "\n".join(pieces)


def resolve_group(
    *,
    args: argparse.Namespace,
    packet: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None, str]:
    if args.group_id:
        group = group_registry(["status", "--group-id", args.group_id])
        if group["state"] in GROUP_TERMINAL_STATES:
            fail(f"cannot attach follow-up loop to terminal group {args.group_id}")
        return args.group_id, group, "explicit-group"
    if not args.inherit_group or not packet.get("group_id"):
        return None, None, "no-group"
    group = group_registry(["status", "--group-id", packet["group_id"]])
    if group["state"] in GROUP_TERMINAL_STATES:
        return None, group, "source-group-terminal"
    return packet["group_id"], group, "inherited-source-group"


def attach_group(group_id: str | None, loop_id: str) -> dict[str, Any] | None:
    if not group_id:
        return None
    group_registry(["attach-loop", "--group-id", group_id, "--loop-id", loop_id])
    return group_registry(["reconcile", "--group-id", group_id])


def maybe_run_executor(
    *,
    args: argparse.Namespace,
    loop_id: str,
    group_id: str | None,
    workspace: pathlib.Path,
) -> subprocess.CompletedProcess[str] | None:
    if not args.run_now:
        return None
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
    return subprocess.run(command, check=False, capture_output=True, text=True)


def main() -> int:
    args = parse_args()
    if args.turn_budget < 1:
        fail("--turn-budget must be positive")
    if args.max_turns < 1:
        fail("--max-turns must be positive")

    packet = load_source_packet(args)
    source_status = load_source_status(packet)
    if source_status["state"] not in TERMINAL_STATES and not args.allow_nonterminal_source:
        fail(
            f"source loop {packet['loop_id']} is nonterminal ({source_status['state']}); "
            "use --allow-nonterminal-source to override"
        )

    latest_turn_artifact = load_latest_turn_artifact(packet)
    latest_turn_response = (
        latest_turn_artifact.get("turn_response")
        if isinstance(latest_turn_artifact, dict)
        and isinstance(latest_turn_artifact.get("turn_response"), dict)
        else None
    )
    task_summary, task_summary_source = derive_task_summary(
        args=args,
        packet=packet,
        source_status=source_status,
        latest_turn_response=latest_turn_response,
    )
    note = build_note(
        args=args,
        packet=packet,
        source_status=source_status,
        task_summary_source=task_summary_source,
    )
    session_policy = args.session_policy or source_status["session_policy"]
    lineage_root = source_status.get("lineage_root") or packet.get("lineage_root") or packet["loop_id"]
    lineage_depth = int(source_status.get("lineage_depth") or packet.get("lineage_depth") or 0) + 1
    workspace = pathlib.Path(args.workspace)
    source_recovery_path = (
        pathlib.Path(args.recovery_path)
        if args.recovery_path
        else pathlib.Path(packet["status_path"]).parent / "recovery.json"
    )
    group_id, source_group_status, group_resolution = resolve_group(args=args, packet=packet)

    created_loop = finite_registry(
        [
            "create",
            "--task-summary",
            task_summary,
            "--turn-budget",
            str(args.turn_budget),
            "--session-policy",
            session_policy,
            "--followup-of",
            packet["loop_id"],
            "--lineage-root",
            lineage_root,
            "--lineage-depth",
            str(lineage_depth),
            "--source-recovery-path",
            str(source_recovery_path),
            "--spawn-reason",
            "explicit-followup",
            *(["--requested-profile", args.requested_profile] if args.requested_profile else []),
            *(["--consumer-id", args.consumer_id] if args.consumer_id else []),
            *(["--note", note] if note else []),
        ]
    )
    loop_id = created_loop["loop_id"]
    run_root = FINITE_ROOT / "runs" / loop_id
    attached_group_status = attach_group(group_id, loop_id)
    executor_result = maybe_run_executor(
        args=args,
        loop_id=loop_id,
        group_id=group_id,
        workspace=workspace,
    )
    latest_loop_status = finite_registry(["status", "--loop-id", loop_id])
    latest_group_status = group_registry(["status", "--group-id", group_id]) if group_id else None
    executor_latest = run_root / "executor-latest.json"

    FOLLOWUPS_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "spawned_at": utc_now_iso(),
        "source_loop_id": packet["loop_id"],
        "source_state": source_status["state"],
        "source_phase": source_status["phase"],
        "source_last_turn_outcome": source_status.get("last_turn_outcome"),
        "source_continuity_status": source_status.get("continuity_status"),
        "source_last_execution_mode": (
            latest_turn_artifact.get("execution_mode")
            if isinstance(latest_turn_artifact, dict)
            else None
        ),
        "source_last_execution_mode_reason": (
            latest_turn_artifact.get("execution_mode_reason")
            if isinstance(latest_turn_artifact, dict)
            else None
        ),
        "source_last_resume_demoted_reason": (
            latest_turn_artifact.get("resume_demoted_reason")
            if isinstance(latest_turn_artifact, dict)
            else None
        ),
        "source_recovery_path": str(source_recovery_path),
        "source_group_id": packet.get("group_id"),
        "group_resolution": group_resolution,
        "group_id": group_id,
        "task_summary": task_summary,
        "task_summary_source": task_summary_source,
        "turn_budget": args.turn_budget,
        "lineage_root": lineage_root,
        "lineage_depth": lineage_depth,
        "session_policy": session_policy,
        "run_now": args.run_now,
        "workspace": str(workspace),
        "create_result": created_loop,
        "attached_group_status": attached_group_status,
        "source_group_status": source_group_status,
        "loop_status": latest_loop_status,
        "group_status": latest_group_status,
        "executor_exit_code": executor_result.returncode if executor_result else None,
        "executor_stdout_tail": tail_text(executor_result.stdout) if executor_result else [],
        "executor_stderr_tail": tail_text(executor_result.stderr) if executor_result and executor_result.returncode != 0 else [],
        "executor_latest_path": str(executor_latest) if executor_latest.exists() else None,
        "receipt_fanout_complete": executor_latest.exists() if args.run_now else True,
    }
    if executor_latest.exists():
        payload["executor_latest"] = load_json(executor_latest)

    write_json(run_root / "followup.json", payload)
    write_json(FOLLOWUPS_DIR / f"{loop_id}.json", payload)
    write_json(FOLLOWUPS_DIR / "latest.json", payload)
    if args.meta_out:
        write_json(pathlib.Path(args.meta_out), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return executor_result.returncode if executor_result else 0


if __name__ == "__main__":
    raise SystemExit(main())
