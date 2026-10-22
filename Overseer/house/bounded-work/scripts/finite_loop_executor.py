#!/usr/bin/env python3
"""Execute a bounded finite loop through the shared Codex load balancer."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = pathlib.Path("/home/overseer")
FINITE_ROOT = pathlib.Path(os.environ.get("OVERSEER_FINITE_LOOP_ROOT", str(ROOT / "state/finite-loops")))
GROUP_ROOT = pathlib.Path(os.environ.get("OVERSEER_LOOP_GROUP_ROOT", str(ROOT / "state/loop-groups")))
LOOP_CONTROL_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_LOOP_CONTROL_ROOT", str(ROOT / "state/loop-control"))
)
LOOP_REGISTRY = ROOT / "scripts" / "finite_loop_registry.py"
GROUP_REGISTRY = ROOT / "scripts" / "loop_group_registry.py"
RUNNER = ROOT / "scripts" / "codex_exec_with_load_balancer.py"
RUNTIME_PREPARER = ROOT / "scripts" / "prepare_loop_runtime.py"
PYTHON_BIN = pathlib.Path("/run/current-system/sw/bin/overseer-python3")
if not PYTHON_BIN.exists():
    PYTHON_BIN = pathlib.Path(sys.executable)

TURN_OUTCOMES = {"continue", "completed", "blocked", "failed", "cancelled"}
CONTROL_ACTIONS = {
    "inform",
    "focus-next-turn",
    "stop-after-turn",
    "hold-after-turn",
    "cancel-before-turn",
}


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


def control_note_paths(loop_id: str) -> tuple[pathlib.Path, pathlib.Path]:
    return (
        LOOP_CONTROL_ROOT / "notes" / f"{loop_id}.json",
        LOOP_CONTROL_ROOT / "notes" / f"{loop_id}.md",
    )


def render_control_note_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Loop Control Note",
        "",
        f"- status: {payload.get('status') or 'unknown'}",
        f"- loop_id: {payload.get('loop_id') or '(none)'}",
        f"- updated_at: {payload.get('updated_at') or '(none)'}",
        f"- action: {payload.get('action') or '(none)'}",
        f"- priority: {payload.get('priority') or 'normal'}",
        f"- requested_by: {payload.get('requested_by') or 'interactive'}",
        f"- summary: {payload.get('summary') or '(none)'}",
        "",
    ]
    body = str(payload.get("body") or "").strip()
    if body:
        lines.extend(["## Body", "", body, ""])
    if payload.get("status") == "consumed":
        lines.extend(
            [
                "## Consumption",
                "",
                f"- consumed_at: {payload.get('consumed_at') or '(none)'}",
                f"- consumed_by: {payload.get('consumed_by') or '(none)'}",
                f"- consumed_reason: {payload.get('consumed_reason') or '(none)'}",
                f"- consumed_turn: {payload.get('consumed_turn') or '(none)'}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def load_active_control_note(loop_id: str) -> dict[str, Any] | None:
    json_path, _ = control_note_paths(loop_id)
    if not json_path.exists():
        return None
    payload = load_json(json_path)
    if payload.get("status") != "active":
        return None
    if payload.get("action") not in CONTROL_ACTIONS:
        return None
    return payload


def consume_control_note(
    loop_id: str,
    *,
    consumed_turn: int | None,
    consumed_reason: str,
    consumed_by: str = "finite-loop-executor",
) -> None:
    json_path, md_path = control_note_paths(loop_id)
    if not json_path.exists():
        return
    payload = load_json(json_path)
    if payload.get("status") != "active":
        return
    payload["status"] = "consumed"
    payload["updated_at"] = utc_now_iso()
    payload["consumed_at"] = payload["updated_at"]
    payload["consumed_by"] = consumed_by
    payload["consumed_reason"] = consumed_reason
    payload["consumed_turn"] = consumed_turn
    write_json(json_path, payload)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_control_note_markdown(payload), encoding="utf-8")


def loop_run_root(loop_id: str) -> pathlib.Path:
    return FINITE_ROOT / "runs" / loop_id


def load_loop_status(loop_id: str) -> dict[str, Any]:
    path = loop_run_root(loop_id) / "status.json"
    if not path.exists():
        fail(f"missing loop status: {path}")
    return load_json(path)


def annotate_loop_status(loop_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    path = loop_run_root(loop_id) / "status.json"
    status = load_json(path)
    status.update(updates)
    write_json(path, status)
    return status


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


def prepare_runtime(loop_id: str, workspace: pathlib.Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["OVERSEER_FINITE_LOOP_ROOT"] = str(FINITE_ROOT)
    return run_json_command(
        [
            str(PYTHON_BIN),
            str(RUNTIME_PREPARER),
            "--loop-id",
            loop_id,
            "--workspace",
            str(workspace),
        ],
        env=env,
    )


def build_turn_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "outcome",
            "summary",
            "resume_hint",
            "next_turn_prompt",
            "task_state",
            "needs_human",
            "confidence",
            "evidence_paths",
        ],
        "properties": {
            "outcome": {"type": "string", "enum": sorted(TURN_OUTCOMES)},
            "summary": {"type": "string", "minLength": 1},
            "resume_hint": {"type": "string", "minLength": 1},
            "next_turn_prompt": {"type": "string"},
            "task_state": {"type": "string", "minLength": 1},
            "needs_human": {"type": "boolean"},
            "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
            "evidence_paths": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }


def validate_turn_response(payload: dict[str, Any]) -> None:
    required = {
        "outcome",
        "summary",
        "resume_hint",
        "next_turn_prompt",
        "task_state",
        "needs_human",
        "confidence",
        "evidence_paths",
    }
    missing = sorted(required - payload.keys())
    if missing:
        fail(f"turn response missing keys: {', '.join(missing)}")
    if payload["outcome"] not in TURN_OUTCOMES:
        fail(f"invalid turn outcome: {payload['outcome']}")
    if payload["confidence"] not in {"low", "medium", "high"}:
        fail(f"invalid confidence: {payload['confidence']}")
    if not isinstance(payload["needs_human"], bool):
        fail("needs_human must be boolean")
    if not isinstance(payload["evidence_paths"], list):
        fail("evidence_paths must be a list")


def build_prompt(
    loop_status: dict[str, Any],
    group: dict[str, Any] | None,
    current_turn: int,
    control_note: dict[str, Any] | None = None,
) -> str:
    lines = [
        "You are executing one bounded Overseer delegate loop turn.",
        "",
        "Task:",
        loop_status["task_summary"],
        "",
        f"Loop id: {loop_status['loop_id']}",
        f"Loop class: {loop_status.get('loop_class', 'generic')}",
        f"Consumer id: {loop_status['consumer_id']}",
        f"Current turn number: {current_turn}",
        f"Turn budget total: {loop_status['turn_budget_total']}",
        f"Turn budget remaining before this turn: {loop_status['turn_budget_remaining']}",
        f"Session policy: {loop_status['session_policy']}",
        "",
        "Constraints:",
        "- Interactive human work outranks this delegate.",
        "- Make real progress if possible.",
        "- Research online whenever it would improve judgment, diagnosis, verification, or repair legitimacy.",
        "- Leave the repo and machine in a truthful state.",
        "- Your final response must match the required JSON schema exactly.",
        "",
        "Outcome meanings:",
        "- continue: more bounded turns are warranted",
        "- completed: the task is finished",
        "- blocked: truthful progress now requires changed conditions or input",
        "- failed: this turn ended in a suspect or unsuccessful state",
        "- cancelled: stop without claiming completion",
        "",
        "Required response fields:",
        "- summary: what you actually accomplished this turn",
        "- resume_hint: the next truthful opening move",
        "- next_turn_prompt: the best next-turn prompt if another turn is warranted",
        "- task_state: concise current state of the task",
        "- needs_human: whether the operator must intervene now",
        "- confidence: low, medium, or high",
        "- evidence_paths: files or artifacts worth reopening",
    ]
    if loop_status.get("mission_path"):
        lines.extend(["", "Mission contract:", f"- mission_path: {loop_status['mission_path']}"])
    last_summary = loop_status.get("last_summary")
    last_resume_hint = loop_status.get("last_resume_hint")
    if last_summary or last_resume_hint:
        lines.extend(["", "Previous loop state:"])
        if last_summary:
            lines.append(f"- last_summary: {last_summary}")
        if last_resume_hint:
            lines.append(f"- last_resume_hint: {last_resume_hint}")
    if group:
        lines.extend(
            [
                "",
                "Group context:",
                f"- group_id: {group['group_id']}",
                f"- purpose: {group['purpose']}",
                f"- stability_class: {group['stability_class']}",
                f"- coordination_mode: {group['coordination_mode']}",
                f"- member_count: {group['member_count']}",
                f"- group_state: {group['state']}",
            ]
        )
        if group.get("summary"):
            lines.append(f"- group_summary: {group['summary']}")
        if group.get("resume_hint"):
            lines.append(f"- group_resume_hint: {group['resume_hint']}")
    if control_note:
        lines.extend(
            [
                "",
                "Loop control note:",
                f"- action: {control_note.get('action')}",
                f"- priority: {control_note.get('priority') or 'normal'}",
                f"- requested_by: {control_note.get('requested_by') or 'interactive'}",
                f"- summary: {control_note.get('summary') or '(none)'}",
            ]
        )
        body = str(control_note.get("body") or "").strip()
        if body:
            lines.extend(["", "Control note body:", body])
    return "\n".join(lines) + "\n"


def build_turn_artifact(
    *,
    loop_status_before: dict[str, Any],
    loop_status_after: dict[str, Any],
    group_id: str | None,
    local_turn_index: int,
    meta: dict[str, Any],
    turn_response: dict[str, Any] | None,
    runner_exit_code: int,
    schema_path: pathlib.Path,
    message_path: pathlib.Path,
    meta_path: pathlib.Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "written_at": utc_now_iso(),
        "loop_id": loop_status_before["loop_id"],
        "group_id": group_id,
        "consumer_id": loop_status_before["consumer_id"],
        "local_turn_index": local_turn_index,
        "turn_count_before": loop_status_before["turn_count"],
        "turn_count_after": loop_status_after["turn_count"],
        "turn_budget_remaining_before": loop_status_before["turn_budget_remaining"],
        "turn_budget_remaining_after": loop_status_after["turn_budget_remaining"],
        "runner_exit_code": runner_exit_code,
        "selected_profile": meta.get("selected_profile"),
        "completed_session": meta.get("completed_session"),
        "execution_mode": meta.get("execution_mode"),
        "execution_mode_reason": meta.get("execution_mode_reason"),
        "resume_demoted_reason": meta.get("resume_demoted_reason"),
        "turn_response": turn_response,
        "run_receipt": meta.get("run_receipt"),
        "latest_checkpoint": meta.get("latest_checkpoint"),
        "evidence_packet": meta.get("evidence_packet"),
        "meta_path": str(meta_path),
        "message_path": str(message_path),
        "schema_path": str(schema_path),
    }


def parse_turn_response(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing turn response output: {path}")
    payload = load_json(path)
    validate_turn_response(payload)
    return payload


def maybe_attach_group(group_id: str | None, loop_id: str) -> dict[str, Any] | None:
    if not group_id:
        return None
    group_registry(["attach-loop", "--group-id", group_id, "--loop-id", loop_id])
    return group_registry(["status", "--group-id", group_id])


def checkpoint_group(
    group_id: str | None,
    loop_id: str,
    loop_status: dict[str, Any],
    summary: str,
    resume_hint: str,
    *,
    group_state: str = "active",
) -> None:
    if not group_id:
        return
    group_registry(
        [
            "checkpoint",
            "--group-id",
            group_id,
            "--state",
            group_state,
            "--summary",
            f"{loop_id}: {summary}",
            "--resume-hint",
            resume_hint,
        ]
    )


def reconcile_group(group_id: str | None) -> dict[str, Any] | None:
    if not group_id:
        return None
    return group_registry(["reconcile", "--group-id", group_id])


def start_loop_turn(loop_id: str, current_turn: int, group_id: str | None) -> dict[str, Any]:
    loop_status = finite_registry(
        [
            "checkpoint",
            "--loop-id",
            loop_id,
            "--phase",
            f"turn-{current_turn}-starting",
            "--summary",
            f"bounded loop turn {current_turn} is starting through the shared load balancer",
            "--resume-hint",
            "reopen the loop status, executor-latest.json, and daemon checkpoint surfaces if this turn is interrupted",
        ]
    )
    updates: dict[str, Any] = {
        "state": "running",
        "executor_state": "running",
        "last_group_id": group_id,
    }
    if not loop_status.get("started_at"):
        updates["started_at"] = utc_now_iso()
    return annotate_loop_status(loop_id, updates)


def maybe_cancel_before_turn(
    *,
    loop_id: str,
    loop_status_before: dict[str, Any],
    control_note: dict[str, Any] | None,
    group_id: str | None,
) -> dict[str, Any] | None:
    if not control_note or control_note.get("action") != "cancel-before-turn":
        return None
    summary = f"loop cancelled before turn by control note: {control_note.get('summary') or 'no summary'}"
    loop_status_after = finite_registry(
        [
            "complete",
            "--loop-id",
            loop_id,
            "--outcome",
            "cancelled",
            "--summary",
            summary,
            "--remaining-turns",
            str(loop_status_before["turn_budget_remaining"]),
            "--turns-consumed",
            "0",
        ]
    )
    loop_status_after = annotate_loop_status(
        loop_id,
        {
            "executor_state": "terminal",
            "last_group_id": group_id,
            "last_turn_outcome": "cancelled",
            "last_task_state": "cancelled before next turn by control note",
        },
    )
    checkpoint_group(
        group_id,
        loop_id,
        loop_status_after,
        summary,
        "inspect the control note and decide whether to relaunch the loop",
    )
    reconcile_group(group_id)
    consume_control_note(
        loop_id,
        consumed_turn=loop_status_before.get("turn_count"),
        consumed_reason="cancel-before-turn",
    )
    return loop_status_after


def run_runner(
    *,
    loop_status: dict[str, Any],
    runtime: dict[str, Any],
    prompt: str,
    schema_path: pathlib.Path,
    message_path: pathlib.Path,
    meta_path: pathlib.Path,
    requested_profile: str | None,
    wait_seconds: int,
    enable_search: bool,
) -> int:
    command = [
        str(PYTHON_BIN),
        str(RUNNER),
        "--consumer-id",
        loop_status["consumer_id"],
        "--workspace",
        runtime["workspace_path"],
        "--codex-home",
        runtime["codex_home"],
        "--active-auth-path",
        runtime["active_auth_path"],
        "--runtime-lock-root",
        runtime["runtime_lock_root"],
        "--meta-out",
        str(meta_path),
        "--mode",
        "finite-loop-turn",
        "--wait-seconds",
        str(wait_seconds),
    ]
    session_id = loop_status.get("last_session_id")
    if session_id:
        command.extend(["--session-id", session_id])
    profile = requested_profile or loop_status.get("requested_profile")
    if profile:
        command.extend(["--requested-profile", profile])
    command.append("--")
    command.extend(["--output-schema", str(schema_path), "-o", str(message_path), prompt])
    result = subprocess.run(command, check=False)
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-id", required=True)
    parser.add_argument("--group-id")
    parser.add_argument("--workspace", default=str(ROOT))
    parser.add_argument("--requested-profile")
    parser.add_argument("--max-turns", type=int, default=1)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--search", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--meta-out")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_turns < 1:
        fail("--max-turns must be positive")

    workspace = pathlib.Path(args.workspace)
    loop_id = args.loop_id
    run_root = loop_run_root(loop_id)
    turns_root = run_root / "turns"
    turns_root.mkdir(parents=True, exist_ok=True)

    overall_meta: dict[str, Any] = {
        "loop_id": loop_id,
        "group_id": args.group_id,
        "started_at": utc_now_iso(),
        "workspace": str(workspace),
        "requested_profile": args.requested_profile,
        "max_turns": args.max_turns,
        "search": args.search,
        "turns": [],
    }

    exit_code = 0
    group = maybe_attach_group(args.group_id, loop_id)
    runtime = prepare_runtime(loop_id, workspace)
    annotate_loop_status(
        loop_id,
        {
            "runtime_root": runtime["runtime_root"],
            "runtime_codex_home": runtime["codex_home"],
            "runtime_workspace_path": runtime["workspace_path"],
            "runtime_workspace_mode": runtime["workspace_mode"],
            "runtime_lock_scope": runtime["runtime_lock_scope"],
            "source_workspace": runtime["source_workspace"],
        },
    )
    overall_meta["runtime"] = runtime
    for local_turn_index in range(1, args.max_turns + 1):
        loop_status_before = load_loop_status(loop_id)
        if loop_status_before["state"] in {"completed", "blocked", "failed", "abandoned", "cancelled"}:
            break
        if loop_status_before["turn_budget_remaining"] <= 0:
            loop_status_after = finite_registry(
                [
                    "complete",
                    "--loop-id",
                    loop_id,
                    "--outcome",
                    "blocked",
                    "--summary",
                    "turn budget exhausted before another truthful turn could begin",
                ]
            )
            checkpoint_group(args.group_id, loop_id, loop_status_after, loop_status_after["final_summary"], "increase turn budget or retire the loop")
            reconcile_group(args.group_id)
            overall_meta["terminal_outcome"] = loop_status_after["state"]
            break

        control_note_before = load_active_control_note(loop_id)
        cancelled_before_turn = maybe_cancel_before_turn(
            loop_id=loop_id,
            loop_status_before=loop_status_before,
            control_note=control_note_before,
            group_id=args.group_id,
        )
        if cancelled_before_turn is not None:
            overall_meta["terminal_outcome"] = "cancelled"
            overall_meta.setdefault("control_notes", []).append(
                {
                    "stage": "pre-turn",
                    "loop_id": loop_id,
                    "action": control_note_before.get("action"),
                    "summary": control_note_before.get("summary"),
                }
            )
            break

        current_turn = loop_status_before["turn_count"] + 1
        loop_status_current = start_loop_turn(loop_id, current_turn, args.group_id)
        schema_path = turns_root / f"turn-{current_turn:04d}.schema.json"
        message_path = turns_root / f"turn-{current_turn:04d}.response.json"
        meta_path = turns_root / f"turn-{current_turn:04d}.meta.json"
        write_json(schema_path, build_turn_schema())
        prompt = build_prompt(loop_status_current, group, current_turn, control_note_before)

        runner_exit_code = run_runner(
            loop_status=loop_status_current,
            runtime=runtime,
            prompt=prompt,
            schema_path=schema_path,
            message_path=message_path,
            meta_path=meta_path,
            requested_profile=args.requested_profile,
            wait_seconds=args.wait_seconds,
            enable_search=args.search,
        )
        meta = load_json(meta_path) if meta_path.exists() else {"runner_exit_code": runner_exit_code}

        if runner_exit_code == 30:
            loop_status_after = finite_registry(
                [
                    "checkpoint",
                    "--loop-id",
                    loop_id,
                    "--state",
                    "planned",
                    "--phase",
                    "waiting_for_capacity",
                    "--summary",
                    "loop turn deferred under interactive or queue pressure",
                    "--resume-hint",
                    "retry through the shared load balancer when pressure changes",
                ]
            )
            loop_status_after = finite_registry(
                [
                    "hold",
                    "--loop-id",
                    loop_id,
                    "--hold-reason",
                    "capacity",
                    "--requested-by",
                    "finite-loop-executor",
                    "--resume-authority",
                    "interactive",
                    "--resume-precondition",
                    "interactive lease released or daemon queue pressure reduced",
                    "--review-path",
                    str(ROOT / "state" / "codex-load-balancer" / "leases.json"),
                    "--review-path",
                    str(ROOT / "state" / "codex-load-balancer" / "queue.json"),
                    "--summary",
                    "loop turn deferred under interactive or queue pressure",
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "executor_state": "waiting_for_capacity",
                    "last_group_id": args.group_id,
                },
            )
            checkpoint_group(
                args.group_id,
                loop_id,
                loop_status_after,
                "loop turn deferred under interactive or queue pressure",
                "retry when the load balancer admits daemon work",
                group_state="planned",
            )
            reconcile_group(args.group_id)
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=None,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            overall_meta["terminal_outcome"] = "deferred"
            exit_code = 30
            break

        if runner_exit_code != 0:
            turns_consumed = 1 if meta.get("selected_profile") else 0
            summary = f"loop executor saw daemon runner failure rc={runner_exit_code}"
            if meta.get("runner_exception"):
                summary = f"loop executor saw runner exception {meta['runner_exception']['type']}"
            loop_status_after = finite_registry(
                [
                    "complete",
                    "--loop-id",
                    loop_id,
                    "--outcome",
                    "failed",
                    "--summary",
                    summary,
                    "--turns-consumed",
                    str(turns_consumed),
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                    "last_profile": meta.get("selected_profile"),
                    "last_group_id": args.group_id,
                    "last_run_receipt": meta.get("run_receipt"),
                    "last_executor_meta": str(meta_path),
                    "last_message_path": str(message_path),
                    "executor_state": "failed",
                },
            )
            checkpoint_group(args.group_id, loop_id, loop_status_after, summary, "inspect the daemon receipt and latest checkpoint before retrying")
            reconcile_group(args.group_id)
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=None,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            overall_meta["terminal_outcome"] = "failed"
            exit_code = runner_exit_code
            break

        try:
            turn_response = parse_turn_response(message_path)
        except SystemExit as exc:
            summary = f"loop executor could not parse structured turn output: {exc}"
            loop_status_after = finite_registry(
                [
                    "complete",
                    "--loop-id",
                    loop_id,
                    "--outcome",
                    "failed",
                    "--summary",
                    summary,
                    "--turns-consumed",
                    "1",
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                    "last_profile": meta.get("selected_profile"),
                    "last_group_id": args.group_id,
                    "last_run_receipt": meta.get("run_receipt"),
                    "last_executor_meta": str(meta_path),
                    "last_message_path": str(message_path),
                    "executor_state": "failed",
                },
            )
            checkpoint_group(args.group_id, loop_id, loop_status_after, summary, "inspect the last message, daemon receipt, and schema before retrying")
            reconcile_group(args.group_id)
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=None,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            overall_meta["terminal_outcome"] = "failed"
            exit_code = 41
            break
        control_note_after = load_active_control_note(loop_id)
        if control_note_before and control_note_before.get("action") == "focus-next-turn":
            consume_control_note(
                loop_id,
                consumed_turn=current_turn,
                consumed_reason=f"focus-applied-to-turn-{current_turn}",
            )
        outcome = turn_response["outcome"]
        remaining_after = max(0, loop_status_before["turn_budget_remaining"] - 1)
        continuity_status = (meta.get("selection") or {}).get("continuity_status")

        if control_note_after and control_note_after.get("action") == "hold-after-turn":
            hold_summary = (
                f"{turn_response['summary']} (loop held after turn by control note: "
                f"{control_note_after.get('summary') or 'no summary'})"
            )
            loop_status_after = finite_registry(
                [
                    "checkpoint",
                    "--loop-id",
                    loop_id,
                    "--state",
                    "planned",
                    "--phase",
                    "held_by_control_note",
                    "--summary",
                    hold_summary,
                    "--resume-hint",
                    turn_response["resume_hint"] or turn_response["next_turn_prompt"],
                    "--turns-consumed",
                    "1",
                    "--remaining-turns",
                    str(remaining_after),
                    *(["--continuity-status", continuity_status] if continuity_status else []),
                ]
            )
            loop_status_after = finite_registry(
                [
                    "hold",
                    "--loop-id",
                    loop_id,
                    "--hold-reason",
                    "operator",
                    "--requested-by",
                    str(control_note_after.get("requested_by") or "interactive"),
                    "--resume-authority",
                    "interactive",
                    "--resume-precondition",
                    "review the loop control note before resuming bounded work",
                    "--review-path",
                    str(control_note_paths(loop_id)[0]),
                    "--summary",
                    str(control_note_after.get("summary") or "loop held after current turn by control note"),
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                    "last_profile": meta.get("selected_profile"),
                    "last_group_id": args.group_id,
                    "last_run_receipt": meta.get("run_receipt"),
                    "last_executor_meta": str(meta_path),
                    "last_message_path": str(message_path),
                    "last_turn_outcome": "held",
                    "last_task_state": turn_response["task_state"],
                    "executor_state": "held",
                },
            )
            checkpoint_group(
                args.group_id,
                loop_id,
                loop_status_after,
                hold_summary,
                turn_response["resume_hint"] or turn_response["next_turn_prompt"],
                group_state="planned",
            )
            reconcile_group(args.group_id)
            consume_control_note(
                loop_id,
                consumed_turn=current_turn,
                consumed_reason="hold-after-turn",
            )
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=turn_response,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            overall_meta["terminal_outcome"] = "held"
            exit_code = 0
            break

        if control_note_after and control_note_after.get("action") == "stop-after-turn":
            terminal_summary = (
                f"{turn_response['summary']} (loop stopped after turn by control note: "
                f"{control_note_after.get('summary') or 'no summary'})"
            )
            loop_status_after = finite_registry(
                [
                    "complete",
                    "--loop-id",
                    loop_id,
                    "--outcome",
                    "cancelled",
                    "--summary",
                    terminal_summary,
                    "--remaining-turns",
                    str(remaining_after),
                    "--turns-consumed",
                    "1",
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                    "last_profile": meta.get("selected_profile"),
                    "last_group_id": args.group_id,
                    "last_run_receipt": meta.get("run_receipt"),
                    "last_executor_meta": str(meta_path),
                    "last_message_path": str(message_path),
                    "last_turn_outcome": "cancelled",
                    "last_task_state": turn_response["task_state"],
                    "executor_state": "terminal",
                },
            )
            checkpoint_group(
                args.group_id,
                loop_id,
                loop_status_after,
                terminal_summary,
                turn_response["resume_hint"] or turn_response["next_turn_prompt"],
            )
            reconcile_group(args.group_id)
            consume_control_note(
                loop_id,
                consumed_turn=current_turn,
                consumed_reason="stop-after-turn",
            )
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=turn_response,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            overall_meta["terminal_outcome"] = "cancelled"
            exit_code = 0
            break

        if outcome == "continue" and remaining_after > 0:
            loop_status_after = finite_registry(
                [
                    "checkpoint",
                    "--loop-id",
                    loop_id,
                    "--phase",
                    f"turn-{current_turn}",
                    "--summary",
                    turn_response["summary"],
                    "--resume-hint",
                    turn_response["resume_hint"] or turn_response["next_turn_prompt"],
                    "--turns-consumed",
                    "1",
                    "--remaining-turns",
                    str(remaining_after),
                    *(["--continuity-status", continuity_status] if continuity_status else []),
                ]
            )
            loop_status_after = annotate_loop_status(
                loop_id,
                {
                    "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                    "last_profile": meta.get("selected_profile"),
                    "last_group_id": args.group_id,
                    "last_run_receipt": meta.get("run_receipt"),
                    "last_executor_meta": str(meta_path),
                    "last_message_path": str(message_path),
                    "last_turn_outcome": outcome,
                    "last_task_state": turn_response["task_state"],
                    "executor_state": "running",
                },
            )
            checkpoint_group(args.group_id, loop_id, loop_status_after, turn_response["summary"], turn_response["resume_hint"] or turn_response["next_turn_prompt"])
            reconcile_group(args.group_id)
            artifact = build_turn_artifact(
                loop_status_before=loop_status_before,
                loop_status_after=loop_status_after,
                group_id=args.group_id,
                local_turn_index=local_turn_index,
                meta=meta,
                turn_response=turn_response,
                runner_exit_code=runner_exit_code,
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
            )
            turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
            write_json(turn_artifact_path, artifact)
            overall_meta["turns"].append(artifact)
            continue

        terminal_outcome = outcome
        terminal_summary = turn_response["summary"]
        if outcome == "continue" and remaining_after == 0:
            terminal_outcome = "blocked"
            terminal_summary = f"{turn_response['summary']} (no remaining turn budget for continuation)"
        loop_status_after = finite_registry(
            [
                "complete",
                "--loop-id",
                loop_id,
                "--outcome",
                terminal_outcome,
                "--summary",
                terminal_summary,
                "--remaining-turns",
                str(remaining_after),
                "--turns-consumed",
                "1",
            ]
        )
        loop_status_after = annotate_loop_status(
            loop_id,
            {
                "last_session_id": meta.get("completed_session") or loop_status_before.get("last_session_id"),
                "last_profile": meta.get("selected_profile"),
                "last_group_id": args.group_id,
                "last_run_receipt": meta.get("run_receipt"),
                "last_executor_meta": str(meta_path),
                "last_message_path": str(message_path),
                "last_turn_outcome": terminal_outcome,
                "last_task_state": turn_response["task_state"],
                "executor_state": "terminal",
            },
        )
        checkpoint_group(args.group_id, loop_id, loop_status_after, terminal_summary, turn_response["resume_hint"] or turn_response["next_turn_prompt"])
        reconcile_group(args.group_id)
        artifact = build_turn_artifact(
            loop_status_before=loop_status_before,
            loop_status_after=loop_status_after,
            group_id=args.group_id,
            local_turn_index=local_turn_index,
            meta=meta,
            turn_response=turn_response,
            runner_exit_code=runner_exit_code,
            schema_path=schema_path,
            message_path=message_path,
            meta_path=meta_path,
        )
        turn_artifact_path = turns_root / f"turn-{current_turn:04d}.json"
        write_json(turn_artifact_path, artifact)
        overall_meta["turns"].append(artifact)
        overall_meta["terminal_outcome"] = terminal_outcome
        exit_code = 0 if terminal_outcome in {"completed", "blocked", "cancelled"} else 40
        break

    overall_meta["completed_at"] = utc_now_iso()
    latest_status = load_loop_status(loop_id)
    overall_meta["loop_status"] = latest_status
    if args.group_id:
        overall_meta["group_status"] = group_registry(["status", "--group-id", args.group_id])
    executor_latest = run_root / "executor-latest.json"
    write_json(executor_latest, overall_meta)
    if args.meta_out:
        write_json(pathlib.Path(args.meta_out), overall_meta)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
