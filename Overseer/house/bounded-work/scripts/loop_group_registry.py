#!/usr/bin/env python3
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


STATE_ROOT = Path(
    os.environ.get("OVERSEER_LOOP_GROUP_ROOT", "/home/overseer/state/loop-groups")
)
GROUPS_DIR = STATE_ROOT / "groups"
RECEIPTS_DIR = STATE_ROOT / "receipts"
CHECKPOINTS_DIR = STATE_ROOT / "checkpoints"
RECOVERY_DIR = STATE_ROOT / "recovery"
EVENTS_PATH = STATE_ROOT / "events.jsonl"
INDEX_PATH = STATE_ROOT / "index.json"
LATEST_PATH = STATE_ROOT / "latest.json"
SPEC_PATH = Path("/home/overseer/specs/loop-groups.json")
FINITE_LOOP_ROOT = Path(
    os.environ.get("OVERSEER_FINITE_LOOP_ROOT", "/home/overseer/state/finite-loops")
)
FINITE_LINEAGES_DIR = FINITE_LOOP_ROOT / "lineages"
TERMINAL_STATES = {"retired", "cancelled"}
LOOP_TERMINAL_STATES = {"completed", "blocked", "failed", "abandoned", "cancelled"}
NON_TERMINAL_STATES = {"planned", "active", "paused"}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs() -> None:
    for path in (STATE_ROOT, GROUPS_DIR, RECEIPTS_DIR, CHECKPOINTS_DIR, RECOVERY_DIR):
        path.mkdir(parents=True, exist_ok=True)


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


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"missing {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid json {path}: {exc}")


def group_path(group_id: str) -> Path:
    return GROUPS_DIR / f"{group_id}.json"


def load_group(group_id: str) -> dict:
    return load_json(group_path(group_id))


def record_event(group_id: str, event_type: str, payload: dict) -> None:
    event = {
        "group_id": group_id,
        "event_type": event_type,
        "written_at": now_utc(),
        **payload,
    }
    append_jsonl(EVENTS_PATH, event)


def finite_loop_status(loop_id: str) -> dict | None:
    status_path = FINITE_LOOP_ROOT / "runs" / loop_id / "status.json"
    if not status_path.exists():
        return None
    return load_json(status_path)


def all_finite_loop_statuses() -> list[dict]:
    runs_dir = FINITE_LOOP_ROOT / "runs"
    if not runs_dir.exists():
        return []
    statuses = []
    for path in sorted(runs_dir.glob("*/status.json")):
        statuses.append(load_json(path))
    return statuses


def existing_path_str(path: Path) -> str | None:
    return str(path) if path.exists() else None


def latest_turn_artifact(loop_id: str) -> Path | None:
    turns_dir = FINITE_LOOP_ROOT / "runs" / loop_id / "turns"
    if not turns_dir.exists():
        return None
    artifacts = sorted(
        path for path in turns_dir.glob("turn-*.json") if path.stem.count(".") == 0
    )
    return artifacts[-1] if artifacts else None


def normalized_lineage_root(status: dict) -> str:
    return status.get("lineage_root") or status["loop_id"]


def normalized_lineage_depth(status: dict) -> int:
    depth = status.get("lineage_depth")
    if depth is None:
        return 0 if not status.get("followup_of") else 1
    return depth


def member_summary(loop_id: str) -> dict:
    status = finite_loop_status(loop_id)
    if status is None:
        fail(f"unknown finite loop {loop_id}")
    return {
        "loop_id": loop_id,
        "state": status["state"],
        "phase": status["phase"],
        "hold": status.get("hold"),
        "task_summary": status["task_summary"],
        "updated_at": status["updated_at"],
        "followup_of": status.get("followup_of"),
        "lineage_root": normalized_lineage_root(status),
        "lineage_depth": normalized_lineage_depth(status),
    }


def lineage_members(lineage_root: str) -> list[dict]:
    members = [
        status
        for status in all_finite_loop_statuses()
        if normalized_lineage_root(status) == lineage_root
    ]
    return sorted(
        members,
        key=lambda item: (
            normalized_lineage_depth(item),
            item["updated_at"],
            item["loop_id"],
        ),
    )


def derive_member_lineage(loop_id: str) -> dict:
    focus_status = finite_loop_status(loop_id)
    if focus_status is None:
        fail(f"unknown finite loop {loop_id}")
    lineage_root = normalized_lineage_root(focus_status)
    members = lineage_members(lineage_root)
    if not members:
        fail(f"no lineage members found for {loop_id}")

    tip_member = members[-1]
    active_members = [item for item in members if item["state"] not in LOOP_TERMINAL_STATES]
    tip_loop_id = tip_member["loop_id"]
    tip_run_root = FINITE_LOOP_ROOT / "runs" / tip_loop_id
    tip_latest_turn_path = latest_turn_artifact(tip_loop_id)
    tip_latest_turn_payload = load_json(tip_latest_turn_path) if tip_latest_turn_path else None
    tip_recovery_path = tip_run_root / "recovery.json"
    tip_receipt_path = tip_run_root / "receipt.json"
    tip_checkpoint_path = tip_run_root / "checkpoint.json"
    tip_followup_candidate = None
    if tip_recovery_path.exists():
        try:
            tip_followup_candidate = load_json(tip_recovery_path).get("followup_candidate")
        except SystemExit:
            tip_followup_candidate = None

    running_members = [item for item in active_members if item["state"] == "running"]
    planned_members = [item for item in active_members if item["state"] == "planned"]
    held_members = [
        item
        for item in active_members
        if isinstance(item.get("hold"), dict) and item["hold"].get("hold_status") == "held"
    ]

    if running_members:
        derived_state = "active"
        lineage_summary = (
            f"lineage has {len(active_members)} nonterminal member loops and "
            f"{len(members) - len(active_members)} terminal member loops"
        )
        lineage_resume_hint = (
            f"reopen the current lineage tip {tip_loop_id} before modifying this chain"
        )
        suggested_action = "reopen-active-lineage"
    elif planned_members:
        derived_state = "planned"
        lineage_summary = (
            f"lineage has {len(planned_members)} planned member loops awaiting execution or capacity"
        )
        if held_members:
            held_reasons = sorted(
                {
                    item.get("hold", {}).get("hold_reason")
                    for item in held_members
                    if item.get("hold", {}).get("hold_reason")
                }
            )
            lineage_summary += f"; {len(held_members)} are explicitly held"
            if held_reasons:
                lineage_summary += f" ({', '.join(held_reasons)})"
        lineage_resume_hint = (
            f"reopen the current lineage tip {tip_loop_id} and retry when capacity or conditions change"
        )
        suggested_action = "reopen-planned-lineage"
    elif tip_followup_candidate:
        derived_state = "paused"
        lineage_summary = (
            f"lineage is terminal at {tip_loop_id} but the latest recovery packet recommends a bounded successor"
        )
        lineage_resume_hint = (
            f"spawn the suggested successor for terminal lineage tip {tip_loop_id}"
        )
        suggested_action = "spawn-lineage-successor"
    else:
        derived_state = "paused"
        lineage_summary = f"all {len(members)} lineage member loops are terminal"
        lineage_resume_hint = (
            f"inspect the terminal lineage tip {tip_loop_id} before attaching or spawning new work"
        )
        suggested_action = "inspect-terminal-lineage"

    lineage_packet_path = FINITE_LINEAGES_DIR / f"{lineage_root}.json"
    reopen_order = [
        str(tip_run_root / "status.json"),
        *( [str(lineage_packet_path)] if lineage_packet_path.exists() else [] ),
        *( [str(tip_recovery_path)] if tip_recovery_path.exists() else [] ),
        *( [str(tip_checkpoint_path)] if tip_checkpoint_path.exists() else [] ),
        *( [str(tip_receipt_path)] if tip_receipt_path.exists() else [] ),
    ]

    return {
        "lineage_root": lineage_root,
        "focus_loop_id": loop_id,
        "tip_loop_id": tip_loop_id,
        "derived_state": derived_state,
        "member_count": len(members),
        "active_member_count": len(active_members),
        "member_loop_ids": [item["loop_id"] for item in members],
        "attached_loop_ids": [],
        "tip_state": tip_member["state"],
        "tip_phase": tip_member["phase"],
        "tip_updated_at": tip_member["updated_at"],
        "tip_continuity_status": tip_member.get("continuity_status"),
        "tip_last_execution_mode": (
            tip_latest_turn_payload.get("execution_mode")
            if isinstance(tip_latest_turn_payload, dict)
            else None
        ),
        "tip_last_execution_mode_reason": (
            tip_latest_turn_payload.get("execution_mode_reason")
            if isinstance(tip_latest_turn_payload, dict)
            else None
        ),
        "tip_last_resume_demoted_reason": (
            tip_latest_turn_payload.get("resume_demoted_reason")
            if isinstance(tip_latest_turn_payload, dict)
            else None
        ),
        "lineage_packet_path": existing_path_str(lineage_packet_path),
        "tip_recovery_path": existing_path_str(tip_recovery_path),
        "tip_checkpoint_path": existing_path_str(tip_checkpoint_path),
        "tip_receipt_path": existing_path_str(tip_receipt_path),
        "lineage_summary": lineage_summary,
        "lineage_resume_hint": lineage_resume_hint,
        "suggested_action": suggested_action,
        "reopen_order": reopen_order,
    }


def derive_member_reopen_order(group: dict, member_details: list[dict]) -> list[dict]:
    ordered = sorted(
        member_details,
        key=lambda item: (
            item["state"] in LOOP_TERMINAL_STATES,
            item["updated_at"],
        ),
        reverse=False,
    )
    result = []
    for item in ordered:
        loop_id = item["loop_id"]
        run_root = FINITE_LOOP_ROOT / "runs" / loop_id
        status_path = run_root / "status.json"
        recovery_path = run_root / "recovery.json"
        checkpoint_path = run_root / "checkpoint.json"
        receipt_path = run_root / "receipt.json"
        result.append(
            {
                "loop_id": loop_id,
                "state": item["state"],
                "phase": item["phase"],
                "hold": item.get("hold"),
                "updated_at": item["updated_at"],
                "status_path": str(status_path),
                "recovery_path": existing_path_str(recovery_path),
                "checkpoint_path": existing_path_str(checkpoint_path),
                "receipt_path": existing_path_str(receipt_path),
            }
        )
    return result


def derive_lineage_reopen_order(member_lineages: list[dict]) -> list[dict]:
    ordered = sorted(
        member_lineages,
        key=lambda item: (
            item["derived_state"] != "active",
            item["tip_updated_at"],
            item["tip_loop_id"],
        ),
    )
    return [
        {
            "lineage_root": item["lineage_root"],
            "focus_loop_id": item["focus_loop_id"],
            "tip_loop_id": item["tip_loop_id"],
            "derived_state": item["derived_state"],
            "tip_state": item["tip_state"],
            "tip_phase": item["tip_phase"],
            "tip_updated_at": item["tip_updated_at"],
            "tip_continuity_status": item.get("tip_continuity_status"),
            "tip_last_execution_mode": item.get("tip_last_execution_mode"),
            "tip_last_execution_mode_reason": item.get("tip_last_execution_mode_reason"),
            "tip_last_resume_demoted_reason": item.get("tip_last_resume_demoted_reason"),
            "attached_loop_ids": item["attached_loop_ids"],
            "reopen_order": item["reopen_order"],
            "lineage_packet_path": item["lineage_packet_path"],
            "lineage_summary": item["lineage_summary"],
            "lineage_resume_hint": item["lineage_resume_hint"],
            "suggested_action": item["suggested_action"],
        }
        for item in ordered
    ]


def rebuild_index() -> dict:
    planned = []
    active = []
    paused = []
    terminal = []
    for path in sorted(
        candidate for candidate in GROUPS_DIR.glob("*.json") if candidate.stem.count(".") == 0
    ):
        group = load_json(path)
        summary = {
            "group_id": group["group_id"],
            "state": group["state"],
            "stability_class": group["stability_class"],
            "coordination_mode": group["coordination_mode"],
            "purpose": group["purpose"],
            "member_count": group["member_count"],
            "updated_at": group["updated_at"],
        }
        if group["state"] in TERMINAL_STATES:
            terminal.append(summary)
        elif group["state"] == "paused":
            paused.append(summary)
        elif group["state"] == "planned":
            planned.append(summary)
        else:
            active.append(summary)
    payload = {
        "updated_at": now_utc(),
        "planned": sorted(planned, key=lambda item: item["updated_at"], reverse=True),
        "active": sorted(active, key=lambda item: item["updated_at"], reverse=True),
        "paused": sorted(paused, key=lambda item: item["updated_at"], reverse=True),
        "terminal": sorted(terminal, key=lambda item: item["updated_at"], reverse=True),
    }
    write_json(INDEX_PATH, payload)
    latest = (
        payload["active"][0]
        if payload["active"]
        else (
            payload["paused"][0]
            if payload["paused"]
            else (
                payload["planned"][0]
                if payload["planned"]
                else (payload["terminal"][0] if payload["terminal"] else None)
            )
        )
    )
    if latest:
        write_json(LATEST_PATH, latest)
    return payload


def create_group(args: argparse.Namespace) -> int:
    ensure_dirs()
    spec = load_spec()
    written_at = now_utc()
    group_id = f"group-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
    payload = {
        "group_id": group_id,
        "created_at": written_at,
        "updated_at": written_at,
        "state": "planned",
        "stability_class": args.stability_class,
        "coordination_mode": args.coordination_mode,
        "purpose": args.purpose,
        "summary": args.summary or None,
        "resume_hint": args.resume_hint or None,
        "member_loop_ids": [],
        "member_count": 0,
        "interactive_priority": True,
        "executor_state": spec.get("current_executor_state", "ledger-only"),
    }
    write_json(group_path(group_id), payload)
    record_event(group_id, "create", {"group": payload})
    rebuild_index()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def attach_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    if group["state"] in TERMINAL_STATES:
        fail(f"group {args.group_id} is already terminal")
    summary = member_summary(args.loop_id)
    members = list(group["member_loop_ids"])
    if args.loop_id not in members:
        members.append(args.loop_id)
    written_at = now_utc()
    group.update(
        {
            "updated_at": written_at,
            "state": "active" if members else group["state"],
            "member_loop_ids": members,
            "member_count": len(members),
            "last_member_change": {
                "action": "attach",
                "loop_id": args.loop_id,
                "written_at": written_at,
            },
        }
    )
    write_json(group_path(args.group_id), group)
    record_event(
        args.group_id,
        "attach-loop",
        {"loop": summary, "member_count": group["member_count"]},
    )
    rebuild_index()
    print(json.dumps(group, indent=2, sort_keys=True))
    return 0


def detach_loop(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    if group["state"] in TERMINAL_STATES:
        fail(f"group {args.group_id} is already terminal")
    members = [loop_id for loop_id in group["member_loop_ids"] if loop_id != args.loop_id]
    written_at = now_utc()
    group.update(
        {
            "updated_at": written_at,
            "member_loop_ids": members,
            "member_count": len(members),
            "last_member_change": {
                "action": "detach",
                "loop_id": args.loop_id,
                "written_at": written_at,
            },
        }
    )
    write_json(group_path(args.group_id), group)
    record_event(
        args.group_id,
        "detach-loop",
        {"loop_id": args.loop_id, "member_count": group["member_count"]},
    )
    rebuild_index()
    print(json.dumps(group, indent=2, sort_keys=True))
    return 0


def checkpoint_group(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    if group["state"] in TERMINAL_STATES:
        fail(f"group {args.group_id} is already terminal")
    written_at = now_utc()
    if args.state:
        group["state"] = args.state
    if args.stability_class:
        group["stability_class"] = args.stability_class
    group.update(
        {
            "updated_at": written_at,
            "summary": args.summary,
            "resume_hint": args.resume_hint or group.get("resume_hint"),
        }
    )
    checkpoint = {
        "group_id": args.group_id,
        "written_at": written_at,
        "state": group["state"],
        "stability_class": group["stability_class"],
        "summary": args.summary,
        "resume_hint": group.get("resume_hint"),
        "member_count": group["member_count"],
    }
    write_json(group_path(args.group_id), group)
    write_json(CHECKPOINTS_DIR / f"{args.group_id}.json", checkpoint)
    record_event(args.group_id, "checkpoint", checkpoint)
    rebuild_index()
    print(json.dumps(group, indent=2, sort_keys=True))
    return 0


def derive_group_reconstruction(group: dict) -> dict:
    member_details = [member_summary(loop_id) for loop_id in group["member_loop_ids"]]
    member_state_counts: dict[str, int] = {}
    for item in member_details:
        member_state_counts[item["state"]] = member_state_counts.get(item["state"], 0) + 1

    member_lineages_by_root: dict[str, dict] = {}
    for item in member_details:
        lineage = member_lineages_by_root.get(item["lineage_root"])
        if lineage is None:
            lineage = derive_member_lineage(item["loop_id"])
            member_lineages_by_root[item["lineage_root"]] = lineage
        lineage["attached_loop_ids"].append(item["loop_id"])

    member_lineages = list(member_lineages_by_root.values())
    lineage_state_counts: dict[str, int] = {}
    for item in member_lineages:
        lineage_state_counts[item["derived_state"]] = lineage_state_counts.get(item["derived_state"], 0) + 1

    active_members = [item for item in member_details if item["state"] not in LOOP_TERMINAL_STATES]
    active_lineages = [item for item in member_lineages if item["derived_state"] == "active"]
    planned_lineages = [item for item in member_lineages if item["derived_state"] == "planned"]
    successor_lineages = [
        item for item in member_lineages if item["suggested_action"] == "spawn-lineage-successor"
    ]
    if not member_details:
        derived_state = "planned"
        reconstruction_summary = "group has no member loops yet"
        reconstruction_resume_hint = "attach or spawn the first loop for this group"
    elif active_lineages:
        derived_state = "active"
        reconstruction_summary = (
            f"group has {len(active_lineages)} active member lineages across "
            f"{len(member_details)} attached loops"
        )
        reconstruction_resume_hint = (
            "reopen active lineage tips and their latest loop artifacts before changing group structure"
        )
    elif planned_lineages:
        derived_state = "planned"
        reconstruction_summary = (
            f"group has {len(planned_lineages)} planned member lineages waiting for execution or capacity"
        )
        reconstruction_resume_hint = (
            "reopen planned lineage tips and retry them when capacity or conditions change"
        )
    elif successor_lineages:
        derived_state = "paused"
        reconstruction_summary = (
            f"group has {len(successor_lineages)} terminal member lineages that already recommend bounded successors"
        )
        reconstruction_resume_hint = (
            "spawn the suggested successor from the newest terminal lineage before attaching unrelated work"
        )
    else:
        derived_state = "paused"
        reconstruction_summary = f"all {len(member_details)} member loops are terminal; the group is paused until new work is attached"
        reconstruction_resume_hint = "spawn or attach a new loop if this group should continue"
    return {
        "derived_state": derived_state,
        "member_state_counts": member_state_counts,
        "member_summaries": member_details,
        "member_reopen_order": derive_member_reopen_order(group, member_details),
        "lineage_count": len(member_lineages),
        "lineage_state_counts": lineage_state_counts,
        "member_lineages": member_lineages,
        "lineage_reopen_order": derive_lineage_reopen_order(member_lineages),
        "reconstruction_summary": reconstruction_summary,
        "reconstruction_resume_hint": reconstruction_resume_hint,
    }


def reconcile_group(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    if group["state"] in TERMINAL_STATES:
        fail(f"group {args.group_id} is already terminal")
    written_at = now_utc()
    derived = derive_group_reconstruction(group)
    group.update(
        {
            "updated_at": written_at,
            "state": derived["derived_state"],
            "last_reconciled_at": written_at,
            "member_state_counts": derived["member_state_counts"],
            "member_summaries": derived["member_summaries"],
            "member_reopen_order": derived["member_reopen_order"],
            "lineage_count": derived["lineage_count"],
            "lineage_state_counts": derived["lineage_state_counts"],
            "member_lineages": derived["member_lineages"],
            "lineage_reopen_order": derived["lineage_reopen_order"],
            "reconstruction_summary": derived["reconstruction_summary"],
            "reconstruction_resume_hint": derived["reconstruction_resume_hint"],
        }
    )
    checkpoint = {
        "group_id": args.group_id,
        "written_at": written_at,
        "state": group["state"],
        "summary": derived["reconstruction_summary"],
        "resume_hint": derived["reconstruction_resume_hint"],
        "member_count": group["member_count"],
        "member_state_counts": derived["member_state_counts"],
        "lineage_count": derived["lineage_count"],
        "lineage_state_counts": derived["lineage_state_counts"],
    }
    write_json(group_path(args.group_id), group)
    write_json(CHECKPOINTS_DIR / f"{args.group_id}.json", checkpoint)
    record_event(args.group_id, "reconcile", checkpoint)
    rebuild_index()
    print(json.dumps(group, indent=2, sort_keys=True))
    return 0


def reconstruct_group(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    derived = derive_group_reconstruction(group)
    checkpoint_path = CHECKPOINTS_DIR / f"{args.group_id}.json"
    receipt_path = RECEIPTS_DIR / f"{args.group_id}.json"
    if group["state"] in TERMINAL_STATES:
        reconstruction_summary = (
            f"group is terminal with outcome {group['state']} and should be inspected before reuse"
        )
        reconstruction_resume_hint = (
            group.get("resume_hint")
            or f"inspect the group receipt and decide whether a successor group should be created for {args.group_id}"
        )
        suggested_action = "inspect-terminal-group"
    else:
        reconstruction_summary = derived["reconstruction_summary"]
        reconstruction_resume_hint = derived["reconstruction_resume_hint"]
        suggested_action = (
            "reopen-active-lineages"
            if derived["derived_state"] == "active"
            else (
                "spawn-lineage-successor"
                if any(item["suggested_action"] == "spawn-lineage-successor" for item in derived["member_lineages"])
                else (
                    "reopen-planned-lineages"
                    if derived["derived_state"] == "planned"
                    else ("spawn-or-attach-member" if derived["derived_state"] == "paused" else "inspect-terminal-group")
                )
            )
        )
    packet = {
        "group_id": args.group_id,
        "reconstructed_at": now_utc(),
        "state": group["state"],
        "purpose": group["purpose"],
        "stability_class": group["stability_class"],
        "coordination_mode": group["coordination_mode"],
        "member_count": group["member_count"],
        "group_path": str(group_path(args.group_id)),
        "checkpoint_path": existing_path_str(checkpoint_path),
        "receipt_path": existing_path_str(receipt_path),
        "summary": group.get("summary"),
        "resume_hint": group.get("resume_hint"),
        "reconstruction_summary": reconstruction_summary,
        "reconstruction_resume_hint": reconstruction_resume_hint,
        "member_state_counts": derived["member_state_counts"],
        "member_summaries": derived["member_summaries"],
        "member_reopen_order": derived["member_reopen_order"],
        "lineage_count": derived["lineage_count"],
        "lineage_state_counts": derived["lineage_state_counts"],
        "member_lineages": derived["member_lineages"],
        "lineage_reopen_order": derived["lineage_reopen_order"],
        "suggested_action": suggested_action,
        "reopen_order": [
            str(group_path(args.group_id)),
            *( [str(checkpoint_path)] if checkpoint_path.exists() else [] ),
            *( [str(receipt_path)] if receipt_path.exists() else [] ),
            *[
                path
                for item in derived["lineage_reopen_order"]
                for path in item["reopen_order"]
            ],
        ],
    }
    write_json(RECOVERY_DIR / f"{args.group_id}.json", packet)
    write_json(RECOVERY_DIR / "latest.json", packet)
    record_event(
        args.group_id,
        "reconstruct",
        {
            "state": group["state"],
            "reconstruction_summary": packet["reconstruction_summary"],
        },
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


def retire_group(args: argparse.Namespace) -> int:
    ensure_dirs()
    group = load_group(args.group_id)
    written_at = now_utc()
    group.update(
        {
            "updated_at": written_at,
            "state": args.outcome,
            "summary": args.summary,
            "completed_at": written_at,
        }
    )
    receipt = {
        "group_id": args.group_id,
        "written_at": written_at,
        "outcome": args.outcome,
        "summary": args.summary,
        "stability_class": group["stability_class"],
        "coordination_mode": group["coordination_mode"],
        "member_loop_ids": group["member_loop_ids"],
        "member_count": group["member_count"],
    }
    write_json(group_path(args.group_id), group)
    write_json(RECEIPTS_DIR / f"{args.group_id}.json", receipt)
    record_event(args.group_id, "retire", receipt)
    rebuild_index()
    print(json.dumps(group, indent=2, sort_keys=True))
    return 0


def status_cmd(args: argparse.Namespace) -> int:
    ensure_dirs()
    if args.group_id:
        print(json.dumps(load_group(args.group_id), indent=2, sort_keys=True))
    else:
        print(json.dumps(rebuild_index(), indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    spec = load_spec()
    parser = argparse.ArgumentParser(description="Manage loop-group records")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a loop-group record")
    create.add_argument("--purpose", required=True)
    create.add_argument(
        "--stability-class",
        required=True,
        choices=spec["stability_classes"],
    )
    create.add_argument(
        "--coordination-mode",
        required=True,
        choices=spec["coordination_modes"],
    )
    create.add_argument("--summary")
    create.add_argument("--resume-hint")
    create.set_defaults(func=create_group)

    attach = sub.add_parser("attach-loop", help="Attach a finite loop to a group")
    attach.add_argument("--group-id", required=True)
    attach.add_argument("--loop-id", required=True)
    attach.set_defaults(func=attach_loop)

    detach = sub.add_parser("detach-loop", help="Detach a finite loop from a group")
    detach.add_argument("--group-id", required=True)
    detach.add_argument("--loop-id", required=True)
    detach.set_defaults(func=detach_loop)

    checkpoint = sub.add_parser("checkpoint", help="Update group progress")
    checkpoint.add_argument("--group-id", required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--resume-hint")
    checkpoint.add_argument("--state", choices=sorted(NON_TERMINAL_STATES))
    checkpoint.add_argument("--stability-class", choices=spec["stability_classes"])
    checkpoint.set_defaults(func=checkpoint_group)

    reconcile = sub.add_parser("reconcile", help="Reconcile group state from current member loops")
    reconcile.add_argument("--group-id", required=True)
    reconcile.set_defaults(func=reconcile_group)

    reconstruct = sub.add_parser("reconstruct", help="Write a recovery packet for a loop group")
    reconstruct.add_argument("--group-id", required=True)
    reconstruct.set_defaults(func=reconstruct_group)

    retire = sub.add_parser("retire", help="Retire a loop group")
    retire.add_argument("--group-id", required=True)
    retire.add_argument("--outcome", required=True, choices=sorted(TERMINAL_STATES))
    retire.add_argument("--summary", required=True)
    retire.set_defaults(func=retire_group)

    status = sub.add_parser("status", help="Show group status")
    status.add_argument("--group-id")
    status.set_defaults(func=status_cmd)

    return parser


def main() -> int:
    ensure_dirs()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
