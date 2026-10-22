#!/usr/bin/env python3
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


STATE_ROOT = Path(
    os.environ.get("OVERSEER_FINITE_LOOP_ROOT", "/home/overseer/state/finite-loops")
)
RUNS_DIR = STATE_ROOT / "runs"
RECEIPTS_DIR = STATE_ROOT / "receipts"
CHECKPOINTS_DIR = STATE_ROOT / "checkpoints"
RECOVERY_DIR = STATE_ROOT / "recovery"
FOLLOWUPS_DIR = STATE_ROOT / "followups"
LINEAGES_DIR = STATE_ROOT / "lineages"
EVENTS_PATH = STATE_ROOT / "events.jsonl"
INDEX_PATH = STATE_ROOT / "index.json"
LATEST_PATH = STATE_ROOT / "latest.json"
SPEC_PATH = Path("/home/overseer/specs/finite-loops.json")
TERMINAL_STATES = {"completed", "blocked", "failed", "abandoned", "cancelled"}
HOLD_REASONS = {
    "capacity",
    "operator",
    "allocation",
    "dependency",
    "cooldown",
    "auth",
    "investigation",
    "policy",
    "human_review",
}
HOLD_STATUSES = {"none", "requested", "held", "released"}
HOLD_SCOPES = {"loop", "group", "lineage"}
HOLD_RESUME_AUTHORITIES = {"interactive", "self", "deadman", "policy", "human"}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs() -> None:
    for path in (
        STATE_ROOT,
        RUNS_DIR,
        RECEIPTS_DIR,
        CHECKPOINTS_DIR,
        RECOVERY_DIR,
        FOLLOWUPS_DIR,
        LINEAGES_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def default_hold_record() -> dict:
    return {
        "hold_status": "none",
        "hold_reason": None,
        "hold_scope": "loop",
        "requested_by": None,
        "requested_at": None,
        "resume_authority": None,
        "resume_preconditions": [],
        "review_paths": [],
        "summary": None,
        "expires_at": None,
        "released_at": None,
        "release_reason": None,
    }


def normalize_hold_record(payload: dict | None) -> dict:
    record = default_hold_record()
    if isinstance(payload, dict):
        for key in record:
            if key in payload:
                record[key] = payload[key]
    if record["resume_preconditions"] is None:
        record["resume_preconditions"] = []
    if record["review_paths"] is None:
        record["review_paths"] = []
    if record["hold_status"] not in HOLD_STATUSES:
        record["hold_status"] = "none"
    if record["hold_scope"] not in HOLD_SCOPES:
        record["hold_scope"] = "loop"
    if record["hold_reason"] not in HOLD_REASONS:
        record["hold_reason"] = None
    if record["resume_authority"] not in HOLD_RESUME_AUTHORITIES:
        record["resume_authority"] = None
    return record


def hold_is_active(payload: dict | None) -> bool:
    return normalize_hold_record(payload).get("hold_status") == "held"


def build_hold_record(
    *,
    reason: str,
    requested_by: str,
    requested_at: str,
    resume_authority: str,
    scope: str = "loop",
    resume_preconditions: list[str] | None = None,
    review_paths: list[str] | None = None,
    summary: str | None = None,
    expires_at: str | None = None,
) -> dict:
    record = default_hold_record()
    record.update(
        {
            "hold_status": "held",
            "hold_reason": reason,
            "hold_scope": scope,
            "requested_by": requested_by,
            "requested_at": requested_at,
            "resume_authority": resume_authority,
            "resume_preconditions": list(resume_preconditions or []),
            "review_paths": list(review_paths or []),
            "summary": summary,
            "expires_at": expires_at,
        }
    )
    return record


def release_hold_record(payload: dict | None, *, released_at: str, release_reason: str) -> dict:
    record = normalize_hold_record(payload)
    if record["hold_status"] == "none":
        return record
    record["hold_status"] = "released"
    record["released_at"] = released_at
    record["release_reason"] = release_reason
    return record


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text())


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def loop_dir(loop_id: str) -> Path:
    return RUNS_DIR / loop_id


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"missing {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid json {path}: {exc}")


def load_status(loop_id: str) -> dict:
    return load_json(loop_dir(loop_id) / "status.json")


def existing_path_str(path: Path) -> str | None:
    return str(path) if path.exists() else None


def latest_turn_artifact(loop_id: str) -> Path | None:
    turns_dir = loop_dir(loop_id) / "turns"
    artifacts = sorted(
        path for path in turns_dir.glob("turn-*.json") if path.stem.count(".") == 0
    )
    return artifacts[-1] if artifacts else None


def all_statuses() -> list[dict]:
    return [load_json(path) for path in sorted(RUNS_DIR.glob("*/status.json"))]


def load_optional_json(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    return load_json(path)


def derive_loop_recovery(status: dict) -> dict:
    loop_id = status["loop_id"]
    hold = normalize_hold_record(status.get("hold"))
    normalized_lineage_root = status.get("lineage_root") or loop_id
    normalized_lineage_depth = status.get("lineage_depth")
    if normalized_lineage_depth is None:
        normalized_lineage_depth = 0 if not status.get("followup_of") else 1
    run_root = loop_dir(loop_id)
    checkpoint_path = run_root / "checkpoint.json"
    global_checkpoint_path = CHECKPOINTS_DIR / f"{loop_id}.json"
    receipt_path = run_root / "receipt.json"
    request_path = run_root / "request.json"
    executor_latest_path = run_root / "executor-latest.json"
    spawn_path = run_root / "spawn.json"
    latest_turn_path = latest_turn_artifact(loop_id)
    latest_turn_payload = load_optional_json(latest_turn_path)
    latest_turn_response = (
        latest_turn_payload.get("turn_response")
        if latest_turn_payload and isinstance(latest_turn_payload.get("turn_response"), dict)
        else None
    )
    last_message_path = Path(status["last_message_path"]) if status.get("last_message_path") else None
    last_executor_meta_path = Path(status["last_executor_meta"]) if status.get("last_executor_meta") else None
    last_run_receipt = Path(status["last_run_receipt"]) if status.get("last_run_receipt") else None
    followup_prompt = None
    if latest_turn_response:
        followup_prompt = (
            (latest_turn_response.get("next_turn_prompt") or "").strip()
            or (latest_turn_response.get("resume_hint") or "").strip()
        )
    followup_candidate = None
    if followup_prompt:
        followup_candidate = {
            "recommended": status["state"] in TERMINAL_STATES
            or latest_turn_response.get("outcome") == "continue",
            "source_loop_id": loop_id,
            "source_state": status["state"],
            "source_outcome": status.get("last_turn_outcome") or latest_turn_response.get("outcome"),
            "derived_task_summary": followup_prompt,
            "resume_hint": (latest_turn_response.get("resume_hint") or "").strip()
            or status.get("last_resume_hint"),
            "task_state": latest_turn_response.get("task_state"),
            "latest_turn_artifact_path": str(latest_turn_path),
        }

    if status["state"] in TERMINAL_STATES:
        recovery_summary = (
            f"loop is terminal with outcome {status['state']} after {status['turn_count']} turns"
        )
        recovery_resume_hint = (
            status.get("last_resume_hint")
            or f"inspect the terminal receipt and decide whether to spawn a follow-up loop for {loop_id}"
        )
        suggested_action = "inspect-terminal"
    elif status["state"] == "running":
        recovery_summary = (
            f"loop is running in phase {status['phase']} with "
            f"{status['turn_budget_remaining']} turns remaining"
        )
        recovery_resume_hint = (
            status.get("last_resume_hint")
            or f"reopen the latest checkpoint and turn artifacts before resuming {loop_id}"
        )
        suggested_action = "resume-loop"
    elif hold_is_active(hold):
        hold_summary = hold.get("summary") or f"loop is held for {hold['hold_reason']}"
        recovery_summary = (
            f"{hold_summary} with {status['turn_budget_remaining']} turns available"
        )
        resume_preconditions = hold.get("resume_preconditions") or []
        review_paths = hold.get("review_paths") or []
        hold_resume_hint = status.get("last_resume_hint") or f"review the hold and release it when the preconditions are satisfied for {loop_id}"
        if resume_preconditions:
            hold_resume_hint = (
                f"{hold_resume_hint}; preconditions: {', '.join(resume_preconditions)}"
            )
        recovery_resume_hint = hold_resume_hint
        suggested_action = (
            "retry-when-capacity-allows"
            if hold.get("hold_reason") == "capacity"
            else "review-hold"
        )
    elif status["phase"] == "waiting_for_capacity":
        recovery_summary = (
            f"loop is planned and waiting for capacity with {status['turn_budget_remaining']} turns available"
        )
        recovery_resume_hint = (
            status.get("last_resume_hint")
            or f"retry {loop_id} through the shared load balancer when interactive or queue pressure changes"
        )
        suggested_action = "retry-when-capacity-allows"
    else:
        recovery_summary = (
            f"loop is planned with {status['turn_budget_remaining']} turns available and "
            "has not yet reached terminal state"
        )
        recovery_resume_hint = (
            status.get("last_resume_hint")
            or f"start execution for {loop_id} through the finite-loop executor or spawn surface"
        )
        suggested_action = "start-loop"

    reopen_order = [
        str(run_root / "status.json"),
        *( [str(checkpoint_path)] if checkpoint_path.exists() else [] ),
        *( [str(request_path)] if request_path.exists() else [] ),
        *( [str(latest_turn_path)] if latest_turn_path else [] ),
        *( [str(last_message_path)] if last_message_path and last_message_path.exists() else [] ),
        *( [str(last_executor_meta_path)] if last_executor_meta_path and last_executor_meta_path.exists() else [] ),
        *( [str(executor_latest_path)] if executor_latest_path.exists() else [] ),
        *( [str(spawn_path)] if spawn_path.exists() else [] ),
        *( [str(receipt_path)] if receipt_path.exists() else [] ),
        *( [str(last_run_receipt)] if last_run_receipt and last_run_receipt.exists() else [] ),
    ]

    return {
        "loop_id": loop_id,
        "reconstructed_at": now_utc(),
        "state": status["state"],
        "phase": status["phase"],
        "task_summary": status["task_summary"],
        "loop_class": status.get("loop_class", "generic"),
        "mission_path": status.get("mission_path"),
        "session_policy": status["session_policy"],
        "continuity_status": status["continuity_status"],
        "consumer_id": status["consumer_id"],
        "requested_profile": status.get("requested_profile"),
        "group_id": status.get("last_group_id"),
        "followup_of": status.get("followup_of"),
        "lineage_root": normalized_lineage_root,
        "lineage_depth": normalized_lineage_depth,
        "hold": hold,
        "spawn_reason": status.get("spawn_reason"),
        "source_recovery_path": status.get("source_recovery_path"),
        "turn_budget_total": status["turn_budget_total"],
        "turn_budget_remaining": status["turn_budget_remaining"],
        "turn_count": status["turn_count"],
        "status_path": str(run_root / "status.json"),
        "checkpoint_path": existing_path_str(checkpoint_path),
        "global_checkpoint_path": existing_path_str(global_checkpoint_path),
        "request_path": existing_path_str(request_path),
        "receipt_path": existing_path_str(receipt_path),
        "executor_latest_path": existing_path_str(executor_latest_path),
        "spawn_path": existing_path_str(spawn_path),
        "latest_turn_artifact_path": str(latest_turn_path) if latest_turn_path else None,
        "last_message_path": str(last_message_path) if last_message_path and last_message_path.exists() else None,
        "last_executor_meta_path": str(last_executor_meta_path) if last_executor_meta_path and last_executor_meta_path.exists() else None,
        "last_run_receipt_path": str(last_run_receipt) if last_run_receipt and last_run_receipt.exists() else None,
        "last_task_state": status.get("last_task_state"),
        "last_turn_outcome": status.get("last_turn_outcome"),
        "followup_candidate": followup_candidate,
        "lineage_packet_path": existing_path_str(LINEAGES_DIR / f"{normalized_lineage_root}.json"),
        "recovery_summary": recovery_summary,
        "recovery_resume_hint": recovery_resume_hint,
        "suggested_action": suggested_action,
        "reopen_order": reopen_order,
    }


def loop_member_packet(status: dict) -> dict:
    loop_id = status["loop_id"]
    hold = normalize_hold_record(status.get("hold"))
    normalized_lineage_root = status.get("lineage_root") or loop_id
    normalized_lineage_depth = status.get("lineage_depth")
    if normalized_lineage_depth is None:
        normalized_lineage_depth = 0 if not status.get("followup_of") else 1
    run_root = loop_dir(loop_id)
    checkpoint_path = run_root / "checkpoint.json"
    receipt_path = run_root / "receipt.json"
    request_path = run_root / "request.json"
    recovery_path = run_root / "recovery.json"
    executor_latest_path = run_root / "executor-latest.json"
    latest_turn_path = latest_turn_artifact(loop_id)
    latest_turn_payload = load_optional_json(latest_turn_path) if latest_turn_path else {}
    return {
        "loop_id": loop_id,
        "state": status["state"],
        "phase": status["phase"],
        "hold": hold,
        "task_summary": status["task_summary"],
        "loop_class": status.get("loop_class", "generic"),
        "followup_of": status.get("followup_of"),
        "lineage_root": normalized_lineage_root,
        "lineage_depth": normalized_lineage_depth,
        "group_id": status.get("last_group_id"),
        "requested_profile": status.get("requested_profile"),
        "last_turn_outcome": status.get("last_turn_outcome"),
        "last_execution_mode": latest_turn_payload.get("execution_mode"),
        "last_execution_mode_reason": latest_turn_payload.get("execution_mode_reason"),
        "last_resume_demoted_reason": latest_turn_payload.get("resume_demoted_reason"),
        "updated_at": status["updated_at"],
        "status_path": str(run_root / "status.json"),
        "request_path": existing_path_str(request_path),
        "checkpoint_path": existing_path_str(checkpoint_path),
        "receipt_path": existing_path_str(receipt_path),
        "recovery_path": existing_path_str(recovery_path),
        "executor_latest_path": existing_path_str(executor_latest_path),
        "latest_turn_artifact_path": str(latest_turn_path) if latest_turn_path else None,
    }


def lineage_members(lineage_root: str) -> list[dict]:
    members = [
        status for status in all_statuses()
        if (status.get("lineage_root") or status["loop_id"]) == lineage_root
    ]
    return sorted(
        members,
        key=lambda item: (
            item.get("lineage_depth") if item.get("lineage_depth") is not None else 0,
            item.get("created_at", ""),
            item["loop_id"],
        ),
    )


def derive_lineage_packet(focus_status: dict) -> dict:
    focus_loop_id = focus_status["loop_id"]
    lineage_root = focus_status.get("lineage_root") or focus_loop_id
    members = lineage_members(lineage_root)
    if not members:
        fail(f"no lineage members found for {focus_loop_id}")

    member_packets = [loop_member_packet(status) for status in members]
    state_counts: dict[str, int] = {}
    for item in member_packets:
        state_counts[item["state"]] = state_counts.get(item["state"], 0) + 1

    active_members = [item for item in member_packets if item["state"] not in TERMINAL_STATES]
    held_members = [item for item in active_members if hold_is_active(item.get("hold"))]
    focus_member = next(item for item in member_packets if item["loop_id"] == focus_loop_id)
    tip_member = max(
        member_packets,
        key=lambda item: (
            item.get("lineage_depth") if item.get("lineage_depth") is not None else 0,
            item["updated_at"],
        ),
    )

    if active_members:
        active_tip = max(
            active_members,
            key=lambda item: (
                item.get("lineage_depth") if item.get("lineage_depth") is not None else 0,
                item["updated_at"],
            ),
        )
        lineage_summary = (
            f"lineage has {len(active_members)} nonterminal member loops and "
            f"{len(member_packets) - len(active_members)} terminal member loops"
        )
        if held_members:
            held_reasons = sorted(
                {
                    item.get("hold", {}).get("hold_reason")
                    for item in held_members
                    if item.get("hold", {}).get("hold_reason")
                }
            )
            lineage_summary += (
                f"; {len(held_members)} nonterminal member loops are currently held"
            )
            if held_reasons:
                lineage_summary += f" ({', '.join(held_reasons)})"
        lineage_resume_hint = (
            f"reopen {active_tip['loop_id']} first, then walk backward through its predecessors if more context is needed"
        )
        suggested_action = "reopen-active-lineage"
        reopen_order = [active_tip["status_path"]]
    else:
        tip_recovery = load_optional_json(pathlib_path(tip_member.get("recovery_path")))
        followup_candidate = tip_recovery.get("followup_candidate") if tip_recovery else None
        if isinstance(followup_candidate, dict) and followup_candidate.get("recommended"):
            lineage_summary = (
                f"lineage is terminal at {tip_member['loop_id']} but the latest recovery packet recommends a bounded successor"
            )
            lineage_resume_hint = (
                followup_candidate.get("resume_hint")
                or f"spawn an explicit follow-up from {tip_member['loop_id']}"
            )
            suggested_action = "spawn-successor"
        else:
            lineage_summary = (
                f"all {len(member_packets)} lineage member loops are terminal"
            )
            lineage_resume_hint = (
                f"inspect the terminal tip {tip_member['loop_id']} and decide whether the lineage should stay closed"
            )
            suggested_action = "inspect-terminal-lineage"
        reopen_order = [tip_member["status_path"]]

    if focus_member["status_path"] not in reopen_order:
        reopen_order.append(focus_member["status_path"])
    for item in reversed(member_packets):
        if item["status_path"] not in reopen_order:
            reopen_order.append(item["status_path"])

    return {
        "lineage_root": lineage_root,
        "focus_loop_id": focus_loop_id,
        "tip_loop_id": tip_member["loop_id"],
        "reconstructed_at": now_utc(),
        "member_count": len(member_packets),
        "active_member_count": len(active_members),
        "terminal_member_count": len(member_packets) - len(active_members),
        "state_counts": state_counts,
        "lineage_summary": lineage_summary,
        "lineage_resume_hint": lineage_resume_hint,
        "suggested_action": suggested_action,
        "members": member_packets,
        "reopen_order": reopen_order,
    }


def pathlib_path(path_str: str | None) -> Path | None:
    return Path(path_str) if path_str else None


def rebuild_index() -> dict:
    active = []
    terminal = []
    for status_path in sorted(RUNS_DIR.glob("*/status.json")):
        status = load_json(status_path)
        normalized_lineage_root = status.get("lineage_root") or status["loop_id"]
        normalized_lineage_depth = status.get("lineage_depth")
        if normalized_lineage_depth is None:
            normalized_lineage_depth = 0 if not status.get("followup_of") else 1
        summary = {
            "loop_id": status["loop_id"],
            "state": status["state"],
            "phase": status["phase"],
            "hold": normalize_hold_record(status.get("hold")),
            "task_summary": status["task_summary"],
            "loop_class": status.get("loop_class", "generic"),
            "turn_budget_remaining": status["turn_budget_remaining"],
            "turn_count": status["turn_count"],
            "session_policy": status["session_policy"],
            "followup_of": status.get("followup_of"),
            "lineage_root": normalized_lineage_root,
            "lineage_depth": normalized_lineage_depth,
            "updated_at": status["updated_at"],
        }
        if status["state"] in TERMINAL_STATES:
            terminal.append(summary)
        else:
            active.append(summary)
    payload = {
        "updated_at": now_utc(),
        "active": sorted(active, key=lambda item: item["updated_at"], reverse=True),
        "terminal": sorted(terminal, key=lambda item: item["updated_at"], reverse=True),
    }
    write_json(INDEX_PATH, payload)
    latest = payload["active"][0] if payload["active"] else (payload["terminal"][0] if payload["terminal"] else None)
    if latest:
        write_json(LATEST_PATH, latest)
    return payload


def record_event(loop_id: str, event_type: str, payload: dict) -> None:
    event = {
        "loop_id": loop_id,
        "event_type": event_type,
        "written_at": now_utc(),
        **payload,
    }
    append_jsonl(EVENTS_PATH, event)
    append_jsonl(loop_dir(loop_id) / "events.jsonl", event)


def create_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    spec = load_spec()
    written_at = now_utc()
    loop_id = f"loop-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
    consumer_id = args.consumer_id or loop_id
    lineage_root = args.lineage_root or args.followup_of or loop_id
    lineage_depth = (
        args.lineage_depth
        if args.lineage_depth is not None
        else (1 if args.followup_of else 0)
    )
    spawn_reason = args.spawn_reason or ("followup" if args.followup_of else "direct-create")
    run_root = loop_dir(loop_id)
    run_root.mkdir(parents=True, exist_ok=True)

    request = {
        "loop_id": loop_id,
        "written_at": written_at,
        "task_summary": args.task_summary,
        "loop_class": args.loop_class,
        "mission_path": args.mission_path,
        "turn_budget_total": args.turn_budget,
        "session_policy": args.session_policy,
        "requested_profile": args.requested_profile,
        "parent_session_id": args.parent_session_id,
        "consumer_id": consumer_id,
        "consumer_class": "daemon",
        "interactive_priority": True,
        "followup_of": args.followup_of,
        "lineage_root": lineage_root,
        "lineage_depth": lineage_depth,
        "spawn_reason": spawn_reason,
        "source_recovery_path": args.source_recovery_path,
        "notes": args.note or None,
        "hold": default_hold_record(),
    }
    status = {
        "loop_id": loop_id,
        "created_at": written_at,
        "updated_at": written_at,
        "state": "planned",
        "phase": "planned",
        "task_summary": args.task_summary,
        "loop_class": args.loop_class,
        "mission_path": args.mission_path,
        "turn_budget_total": args.turn_budget,
        "turn_budget_remaining": args.turn_budget,
        "turn_count": 0,
        "session_policy": args.session_policy,
        "continuity_status": "cold-required",
        "consumer_id": consumer_id,
        "consumer_class": "daemon",
        "interactive_priority": True,
        "requested_profile": args.requested_profile,
        "parent_session_id": args.parent_session_id,
        "followup_of": args.followup_of,
        "lineage_root": lineage_root,
        "lineage_depth": lineage_depth,
        "spawn_reason": spawn_reason,
        "source_recovery_path": args.source_recovery_path,
        "coordination_note": "interactive sessions outrank finite loops",
        "executor_state": spec.get("current_executor_state", "ledger-only"),
        "hold": default_hold_record(),
    }
    write_json(run_root / "request.json", request)
    write_json(run_root / "status.json", status)
    record_event(loop_id, "create", {"status": status})
    rebuild_index()
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def checkpoint_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    status = load_status(args.loop_id)
    if status["state"] in TERMINAL_STATES:
        fail(f"loop {args.loop_id} is already terminal")
    written_at = now_utc()
    turns_consumed = args.turns_consumed or 0
    remaining = status["turn_budget_remaining"]
    if args.remaining_turns is not None:
        remaining = args.remaining_turns
    elif turns_consumed:
        remaining = max(0, remaining - turns_consumed)

    status.update(
        {
            "updated_at": written_at,
            "state": args.state,
            "phase": args.phase,
            "turn_budget_remaining": remaining,
            "turn_count": status["turn_count"] + turns_consumed,
            "continuity_status": args.continuity_status or status["continuity_status"],
            "last_summary": args.summary,
            "last_resume_hint": args.resume_hint,
        }
    )
    if args.state == "running" and hold_is_active(status.get("hold")):
        status["hold"] = release_hold_record(
            status.get("hold"),
            released_at=written_at,
            release_reason=args.release_hold_reason or "execution_resumed",
        )
    checkpoint = {
        "loop_id": args.loop_id,
        "written_at": written_at,
        "phase": args.phase,
        "summary": args.summary,
        "resume_hint": args.resume_hint,
        "turn_budget_remaining": remaining,
        "continuity_status": status["continuity_status"],
        "hold": normalize_hold_record(status.get("hold")),
    }
    write_json(loop_dir(args.loop_id) / "status.json", status)
    write_json(loop_dir(args.loop_id) / "checkpoint.json", checkpoint)
    write_json(CHECKPOINTS_DIR / f"{args.loop_id}.json", checkpoint)
    record_event(args.loop_id, "checkpoint", checkpoint)
    rebuild_index()
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def complete_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    status = load_status(args.loop_id)
    written_at = now_utc()
    turns_consumed = args.turns_consumed or 0
    remaining = status["turn_budget_remaining"] if args.remaining_turns is None else args.remaining_turns
    if args.remaining_turns is None and turns_consumed:
        remaining = max(0, remaining - turns_consumed)
    status.update(
        {
            "updated_at": written_at,
            "state": args.outcome,
            "phase": "terminal",
            "turn_budget_remaining": remaining,
            "turn_count": status["turn_count"] + turns_consumed,
            "final_summary": args.summary,
            "completed_at": written_at,
        }
    )
    if hold_is_active(status.get("hold")):
        status["hold"] = release_hold_record(
            status.get("hold"),
            released_at=written_at,
            release_reason="terminal_completion",
        )
    receipt = {
        "loop_id": args.loop_id,
        "written_at": written_at,
        "outcome": args.outcome,
        "summary": args.summary,
        "turn_budget_remaining": remaining,
        "turn_count": status["turn_count"],
        "session_policy": status["session_policy"],
        "continuity_status": status["continuity_status"],
        "hold": normalize_hold_record(status.get("hold")),
    }
    write_json(loop_dir(args.loop_id) / "status.json", status)
    write_json(loop_dir(args.loop_id) / "receipt.json", receipt)
    write_json(RECEIPTS_DIR / f"{args.loop_id}.json", receipt)
    record_event(args.loop_id, "complete", receipt)
    rebuild_index()
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def hold_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    status = load_status(args.loop_id)
    if status["state"] in TERMINAL_STATES:
        fail(f"loop {args.loop_id} is already terminal")
    written_at = now_utc()
    hold = build_hold_record(
        reason=args.hold_reason,
        requested_by=args.requested_by,
        requested_at=written_at,
        resume_authority=args.resume_authority,
        scope=args.hold_scope,
        resume_preconditions=args.resume_precondition,
        review_paths=args.review_path,
        summary=args.summary,
        expires_at=args.expires_at,
    )
    status.update(
        {
            "updated_at": written_at,
            "hold": hold,
        }
    )
    write_json(loop_dir(args.loop_id) / "status.json", status)
    record_event(
        args.loop_id,
        "hold",
        {
            "hold": hold,
            "phase": status["phase"],
            "state": status["state"],
        },
    )
    rebuild_index()
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def release_hold(args: argparse.Namespace) -> int:
    ensure_dirs()
    status = load_status(args.loop_id)
    written_at = now_utc()
    status["updated_at"] = written_at
    status["hold"] = release_hold_record(
        status.get("hold"),
        released_at=written_at,
        release_reason=args.reason,
    )
    write_json(loop_dir(args.loop_id) / "status.json", status)
    record_event(
        args.loop_id,
        "release_hold",
        {
            "hold": normalize_hold_record(status.get("hold")),
            "phase": status["phase"],
            "state": status["state"],
        },
    )
    rebuild_index()
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def reconstruct_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    status = load_status(args.loop_id)
    packet = derive_loop_recovery(status)
    run_root = loop_dir(args.loop_id)
    write_json(run_root / "recovery.json", packet)
    write_json(RECOVERY_DIR / f"{args.loop_id}.json", packet)
    write_json(RECOVERY_DIR / "latest.json", packet)
    record_event(
        args.loop_id,
        "reconstruct",
        {
            "state": status["state"],
            "phase": status["phase"],
            "recovery_summary": packet["recovery_summary"],
        },
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


def lineage_cmd(args: argparse.Namespace) -> int:
    ensure_dirs()
    focus_status = load_status(args.loop_id)
    packet = derive_lineage_packet(focus_status)
    lineage_root = packet["lineage_root"]
    run_root = loop_dir(args.loop_id)
    write_json(run_root / "lineage.json", packet)
    write_json(LINEAGES_DIR / f"{lineage_root}.json", packet)
    write_json(LINEAGES_DIR / "latest.json", packet)
    record_event(
        args.loop_id,
        "lineage",
        {
            "lineage_root": lineage_root,
            "member_count": packet["member_count"],
            "suggested_action": packet["suggested_action"],
        },
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


def status_cmd(args: argparse.Namespace) -> int:
    ensure_dirs()
    if args.loop_id:
        print(json.dumps(load_status(args.loop_id), indent=2, sort_keys=True))
    else:
        print(json.dumps(rebuild_index(), indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage finite self-stopping loop records")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a finite loop record")
    create.add_argument("--task-summary", required=True)
    create.add_argument("--turn-budget", type=int, required=True)
    create.add_argument("--loop-class", default="generic")
    create.add_argument("--mission-path")
    create.add_argument("--requested-profile")
    create.add_argument("--parent-session-id")
    create.add_argument("--consumer-id")
    create.add_argument("--note")
    create.add_argument("--followup-of")
    create.add_argument("--lineage-root")
    create.add_argument("--lineage-depth", type=int)
    create.add_argument("--source-recovery-path")
    create.add_argument("--spawn-reason")
    create.add_argument(
        "--session-policy",
        default="separate-session",
        choices=["separate-session", "shared-risky"],
    )
    create.set_defaults(func=create_loop)

    checkpoint = sub.add_parser("checkpoint", help="Update loop progress")
    checkpoint.add_argument("--loop-id", required=True)
    checkpoint.add_argument("--state", choices=["planned", "running"], default="running")
    checkpoint.add_argument("--phase", required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--resume-hint")
    checkpoint.add_argument("--remaining-turns", type=int)
    checkpoint.add_argument("--turns-consumed", type=int, default=0)
    checkpoint.add_argument(
        "--continuity-status",
        choices=["warm-resume", "warm-with-risk", "cold-required", "split-detected", "cache-low", "cache-unknown"],
    )
    checkpoint.add_argument("--release-hold-reason")
    checkpoint.set_defaults(func=checkpoint_loop)

    hold = sub.add_parser("hold", help="Mark a loop explicitly held")
    hold.add_argument("--loop-id", required=True)
    hold.add_argument("--hold-reason", required=True, choices=sorted(HOLD_REASONS))
    hold.add_argument("--requested-by", required=True)
    hold.add_argument("--resume-authority", required=True, choices=sorted(HOLD_RESUME_AUTHORITIES))
    hold.add_argument("--hold-scope", default="loop", choices=sorted(HOLD_SCOPES))
    hold.add_argument("--resume-precondition", action="append", default=[])
    hold.add_argument("--review-path", action="append", default=[])
    hold.add_argument("--summary")
    hold.add_argument("--expires-at")
    hold.set_defaults(func=hold_loop)

    release_hold_parser = sub.add_parser("release-hold", help="Release an explicit loop hold")
    release_hold_parser.add_argument("--loop-id", required=True)
    release_hold_parser.add_argument("--reason", required=True)
    release_hold_parser.set_defaults(func=release_hold)

    complete = sub.add_parser("complete", help="Mark loop terminal")
    complete.add_argument("--loop-id", required=True)
    complete.add_argument("--outcome", required=True, choices=sorted(TERMINAL_STATES))
    complete.add_argument("--summary", required=True)
    complete.add_argument("--remaining-turns", type=int)
    complete.add_argument("--turns-consumed", type=int, default=0)
    complete.set_defaults(func=complete_loop)

    reconstruct = sub.add_parser("reconstruct", help="Write a recovery packet for a loop")
    reconstruct.add_argument("--loop-id", required=True)
    reconstruct.set_defaults(func=reconstruct_loop)

    lineage = sub.add_parser("lineage", help="Write a lineage packet for a loop chain")
    lineage.add_argument("--loop-id", required=True)
    lineage.set_defaults(func=lineage_cmd)

    status = sub.add_parser("status", help="Show loop status")
    status.add_argument("--loop-id")
    status.set_defaults(func=status_cmd)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "turn_budget", 1) < 1:
        fail("--turn-budget must be positive")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
