#!/usr/bin/env python3
"""Compile a compact tiered loop observability brief for the house."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import tempfile
from datetime import datetime, timezone
from typing import Any


ROOT = pathlib.Path("/home/overseer")
LOOP_OBSERVABILITY_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_LOOP_OBSERVABILITY_ROOT", str(ROOT / "state" / "loop-observability"))
)
FINITE_LOOPS_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_FINITE_LOOPS_ROOT", str(ROOT / "state" / "finite-loops"))
)
LOOP_GROUPS_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_LOOP_GROUPS_ROOT", str(ROOT / "state" / "loop-groups"))
)
AUDIT_LOOP_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_AUDIT_LOOP_ROOT", str(ROOT / "state" / "audit-loop"))
)
HELD_LOOP_LAUNCHER_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_HELD_LOOP_LAUNCHER_ROOT", str(ROOT / "state" / "held-loop-launcher"))
)
AUDIT_LOOP_CADENCE_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_AUDIT_LOOP_CADENCE_ROOT", str(ROOT / "state" / "audit-loop-cadence"))
)
LOAD_BALANCER_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_CODEX_LOAD_BALANCER_ROOT", str(ROOT / "state" / "codex-load-balancer"))
)
LOOP_CONTROL_ROOT = pathlib.Path(
    os.environ.get("OVERSEER_LOOP_CONTROL_ROOT", str(ROOT / "state" / "loop-control"))
)
LOOP_CLASS_MATURITY_PATH = pathlib.Path(
    os.environ.get(
        "OVERSEER_LOOP_CLASS_MATURITY_PATH",
        str(ROOT / "docs" / "registries" / "loop-class-maturity.json"),
    )
)
CHECKPOINTS_ROOT = LOAD_BALANCER_ROOT / "checkpoints"
HOT_FAILURE_WINDOW_SECONDS = 2 * 60 * 60


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def iso_sort_key(raw: str | None) -> tuple[int, str]:
    stamp = parse_iso(raw)
    if stamp is None:
        return (0, "")
    return (1, stamp.isoformat())


def load_json(path: pathlib.Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def age_seconds(raw: str | None) -> int | None:
    stamp = parse_iso(raw)
    if stamp is None:
        return None
    return max(0, int((utc_now() - stamp).total_seconds()))


def atomic_write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        pathlib.Path(tmp_name).replace(path)
    finally:
        tmp_path = pathlib.Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()


def append_jsonl(path: pathlib.Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, sort_keys=True) + "\n")


def shorten(text: str | None, limit: int = 160) -> str | None:
    if not text:
        return None
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def load_loop_class_registry() -> dict[str, Any]:
    payload = load_json(LOOP_CLASS_MATURITY_PATH, {})
    classes = payload.get("classes")
    if isinstance(classes, dict):
        return classes
    return {}


def loop_class_meta(loop_class: str | None, registry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(loop_class, str) or not loop_class:
        return {"maturity": "unknown", "trust_tier": "unknown"}
    payload = registry.get(loop_class)
    if not isinstance(payload, dict):
        return {"maturity": "unknown", "trust_tier": "unknown"}
    return {
        "maturity": payload.get("maturity") or "unknown",
        "trust_tier": payload.get("trust_tier") or "unknown",
    }


def loop_record(loop: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    loop_id = loop.get("loop_id")
    status_path = FINITE_LOOPS_ROOT / "runs" / str(loop_id) / "status.json"
    receipt_path = FINITE_LOOPS_ROOT / "runs" / str(loop_id) / "receipt.json"
    recovery_path = FINITE_LOOPS_ROOT / "runs" / str(loop_id) / "recovery.json"
    status_payload = load_json(status_path, {}) if status_path.exists() else {}
    merged = dict(status_payload)
    merged.update({key: value for key, value in loop.items() if value is not None})
    mission_path = pathlib.Path(merged["mission_path"]) if merged.get("mission_path") else None
    findings_path = (
        AUDIT_LOOP_ROOT / "findings" / f"{loop_id}.md"
        if merged.get("loop_class") == "audit-loop"
        else None
    )
    active_run_path = LOAD_BALANCER_ROOT / "runs" / str(loop_id) / "active.json"
    active_run = load_json(active_run_path, {}) if active_run_path.exists() else {}
    checkpoint_path = CHECKPOINTS_ROOT / str(loop_id) / "latest.json"
    checkpoint = load_json(checkpoint_path, {}) if checkpoint_path.exists() else {}
    meta = loop_class_meta(merged.get("loop_class"), registry)
    record = {
        "loop_id": loop_id,
        "loop_class": merged.get("loop_class"),
        "loop_class_maturity": meta["maturity"],
        "trust_tier": meta["trust_tier"],
        "state": merged.get("state"),
        "phase": merged.get("phase"),
        "hold_status": ((merged.get("hold") or {}).get("hold_status") or "none"),
        "hold_reason": (merged.get("hold") or {}).get("hold_reason"),
        "updated_at": merged.get("updated_at"),
        "turn_count": merged.get("turn_count"),
        "turn_budget_total": merged.get("turn_budget_total"),
        "turn_budget_remaining": merged.get("turn_budget_remaining"),
        "last_profile": merged.get("last_profile"),
        "last_turn_outcome": merged.get("last_turn_outcome"),
        "runtime_workspace_mode": merged.get("runtime_workspace_mode"),
        "runtime_workspace_path": merged.get("runtime_workspace_path"),
        "task_summary": shorten(merged.get("task_summary")),
        "status_path": str(status_path) if status_path.exists() else None,
        "receipt_path": str(receipt_path) if receipt_path.exists() else None,
        "recovery_path": str(recovery_path) if recovery_path.exists() else None,
        "mission_path": str(mission_path) if mission_path and mission_path.exists() else None,
        "findings_path": str(findings_path) if findings_path and findings_path.exists() else None,
        "active_run_state": active_run.get("state") if active_run else None,
        "active_profile": active_run.get("selected_profile") if active_run else None,
        "active_process_id": active_run.get("pid") if active_run else None,
        "active_run_age_seconds": age_seconds(
            active_run.get("updated_at") or active_run.get("last_heartbeat_at") or active_run.get("started_at")
            if active_run
            else None
        ),
        "checkpoint_phase": checkpoint.get("phase") if checkpoint else None,
        "checkpoint_age_seconds": age_seconds(checkpoint.get("written_at") if checkpoint else None),
        "checkpoint_path": str(checkpoint_path) if checkpoint_path.exists() else None,
    }
    return record


def sorted_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda item: iso_sort_key(item.get("updated_at")), reverse=True)


def completed_success_markers(records: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    markers: dict[tuple[str, str], str] = {}
    for item in records:
        if item.get("state") != "completed":
            continue
        key = (item.get("loop_class") or "unknown", item.get("trust_tier") or "unknown")
        freshness = item.get("updated_at") or ""
        if freshness > (markers.get(key) or ""):
            markers[key] = freshness
    return markers


def load_priority_note() -> dict[str, Any] | None:
    latest = AUDIT_LOOP_ROOT / "priority-note.json"
    if not latest.exists():
        return None
    payload = load_json(latest, {})
    if not payload or payload.get("status") != "active":
        return None
    return {
        "status": payload.get("status"),
        "summary": payload.get("summary"),
        "scope": payload.get("scope"),
        "priority": payload.get("priority"),
        "updated_at": payload.get("updated_at"),
        "path": str(latest),
        "markdown_path": str(AUDIT_LOOP_ROOT / "priority-note.md"),
    }


def load_active_control_notes() -> list[dict[str, Any]]:
    notes_root = LOOP_CONTROL_ROOT / "notes"
    notes: list[dict[str, Any]] = []
    for path in sorted(notes_root.glob("*.json")):
        payload = load_json(path, {})
        if not payload or payload.get("status") != "active":
            continue
        notes.append(
            {
                "loop_id": payload.get("loop_id") or path.stem,
                "action": payload.get("action"),
                "priority": payload.get("priority"),
                "summary": payload.get("summary"),
                "requested_by": payload.get("requested_by"),
                "updated_at": payload.get("updated_at"),
                "path": str(path),
                "markdown_path": str(path.with_suffix(".md")),
            }
        )
    return sorted(notes, key=lambda item: iso_sort_key(item.get("updated_at")), reverse=True)


def build_snapshot() -> dict[str, Any]:
    loop_class_registry = load_loop_class_registry()
    finite_index = load_json(FINITE_LOOPS_ROOT / "index.json", {})
    loop_groups = load_json(LOOP_GROUPS_ROOT / "index.json", {})
    audit_brief = load_json(AUDIT_LOOP_ROOT / "latest.json", {})
    held_loop_launcher = load_json(HELD_LOOP_LAUNCHER_ROOT / "latest.json", {})
    audit_loop_cadence = load_json(AUDIT_LOOP_CADENCE_ROOT / "latest.json", {})
    priority_note = load_priority_note()
    control_notes = load_active_control_notes()

    active = [loop_record(item, loop_class_registry) for item in finite_index.get("active") or []]
    terminal = [loop_record(item, loop_class_registry) for item in finite_index.get("terminal") or []]

    running = sorted_records([item for item in active if item.get("state") == "running"])
    held = sorted_records([item for item in active if item.get("hold_status") == "held"])
    waiting = sorted_records(
        [item for item in active if item.get("phase") == "waiting_for_capacity" and item.get("hold_status") != "held"]
    )
    planned = sorted_records(
        [
            item
            for item in active
            if item.get("state") == "planned"
            and item.get("phase") != "waiting_for_capacity"
            and item.get("hold_status") != "held"
        ]
    )
    stale_failed_all = sorted_records(
        [
            item
            for item in terminal
            if item.get("state") in {"failed", "blocked", "abandoned"}
            and (
                item.get("updated_at") is None
                or (age_seconds(item.get("updated_at")) or 0) > HOT_FAILURE_WINDOW_SECONDS
            )
        ]
    )
    success_markers = completed_success_markers(terminal)
    superseded_failed = sorted_records(
        [
            item
            for item in stale_failed_all
            if (success_markers.get((item.get("loop_class") or "unknown", item.get("trust_tier") or "unknown")) or "")
            > (item.get("updated_at") or "")
        ]
    )
    stale_failed = sorted_records([item for item in stale_failed_all if item not in superseded_failed])
    residue_stale_failed = [item for item in stale_failed if item.get("trust_tier") == "residue"]
    trusted_stale_failed = [item for item in stale_failed if item.get("trust_tier") == "trusted-worker"]
    failed_recent = sorted_records(
        [
            item
            for item in terminal
            if item.get("state") in {"failed", "blocked", "abandoned"}
            and item.get("updated_at") is not None
            and (age_seconds(item.get("updated_at")) or 0) <= HOT_FAILURE_WINDOW_SECONDS
        ]
    )[:3]
    residue_failed_recent = [item for item in failed_recent if item.get("trust_tier") == "residue"]
    trusted_failed_recent = [item for item in failed_recent if item.get("trust_tier") == "trusted-worker"]
    completed_recent = sorted_records(
        [item for item in terminal if item.get("state") == "completed"]
    )[:3]
    trusted_completed_recent = [item for item in completed_recent if item.get("trust_tier") == "trusted-worker"]
    audit_completed = next((item for item in completed_recent if item.get("loop_class") == "audit-loop"), None)

    paused_groups = list(loop_groups.get("paused") or [])
    active_groups = list(loop_groups.get("active") or [])

    observability_level = "ok"
    held_launcher_status = held_loop_launcher.get("status")
    audit_cadence_status = audit_loop_cadence.get("status")

    launcher_error = held_launcher_status in {"runner_failed"}
    launcher_watch = held_launcher_status in {"active_lease_present", "runtime_busy", "queue_busy", "capacity_still_busy"}
    cadence_error = audit_cadence_status in {"launch_failed", "command_failed", "invalid_json"}

    if failed_recent or launcher_error or cadence_error:
        observability_level = "error"
    elif held or waiting or priority_note or control_notes or launcher_watch:
        observability_level = "watch"
    elif trusted_stale_failed:
        observability_level = "watch"

    recommended_actions: list[str] = []
    if failed_recent:
        recommended_actions.append("inspect-failed-loops")
    if stale_failed:
        recommended_actions.append("review-stale-failed-loops")
    if superseded_failed:
        recommended_actions.append("review-superseded-loop-failures")
    if residue_stale_failed or residue_failed_recent:
        recommended_actions.append("review-prototype-loop-residue")
    if held or waiting:
        recommended_actions.append("review-held-or-waiting-loops")
    if priority_note:
        recommended_actions.append("read-audit-priority-note")
    if control_notes:
        recommended_actions.append("read-loop-control-notes")
    if launcher_error or launcher_watch:
        recommended_actions.append("review-held-loop-launcher")
    if cadence_error:
        recommended_actions.append("review-audit-loop-cadence")
    if paused_groups:
        recommended_actions.append("review-paused-loop-groups")
    if audit_completed:
        recommended_actions.append("review-audit-findings")

    recommended_read_order = [
        str(ROOT / "OBSERVABILITY.md"),
        str(ROOT / "docs" / "loop-observability.md"),
    ]
    if priority_note:
        recommended_read_order.append(priority_note["path"])
    for note in control_notes[:2]:
        if note["path"] not in recommended_read_order:
            recommended_read_order.append(note["path"])
    if audit_brief.get("findings_path"):
        recommended_read_order.append(audit_brief["findings_path"])
    for item in running[:1] + held[:1] + failed_recent[:1]:
        for path_key in ("status_path", "receipt_path", "recovery_path", "checkpoint_path"):
            path = item.get(path_key)
            if path and path not in recommended_read_order:
                recommended_read_order.append(path)

    snapshot = {
        "generated_at": utc_now_iso(),
        "observability_level": observability_level,
        "summary": {
            "running_loop_count": len(running),
            "trusted_running_loop_count": sum(1 for item in running if item.get("trust_tier") == "trusted-worker"),
            "held_loop_count": len(held),
            "trusted_held_loop_count": sum(1 for item in held if item.get("trust_tier") == "trusted-worker"),
            "waiting_loop_count": len(waiting),
            "trusted_waiting_loop_count": sum(1 for item in waiting if item.get("trust_tier") == "trusted-worker"),
            "planned_loop_count": len(planned),
            "failed_recent_count": len(failed_recent),
            "trusted_failed_recent_count": len(trusted_failed_recent),
            "prototype_failed_recent_count": len(residue_failed_recent),
            "stale_failed_count": len(stale_failed),
            "superseded_failed_count": len(superseded_failed),
            "trusted_stale_failed_count": len(trusted_stale_failed),
            "prototype_stale_failed_count": len(residue_stale_failed),
            "completed_recent_count": len(completed_recent),
            "trusted_completed_recent_count": len(trusted_completed_recent),
            "active_group_count": len(active_groups),
            "paused_group_count": len(paused_groups),
            "audit_status": audit_brief.get("status"),
            "held_loop_launcher_status": held_launcher_status,
            "audit_loop_cadence_status": audit_cadence_status,
            "priority_note_status": priority_note.get("status") if priority_note else "none",
            "priority_note_priority": priority_note.get("priority") if priority_note else None,
            "active_control_note_count": len(control_notes),
        },
        "hot": {
            "running": running[:3],
            "held": held[:3],
            "failed_recent": failed_recent,
            "priority_note": priority_note,
            "control_notes": control_notes[:5],
        },
        "warm": {
            "waiting": waiting[:5],
            "planned": planned[:5],
            "stale_failed": stale_failed[:5],
            "superseded_failed": superseded_failed[:5],
            "prototype_residue": {
                "failed_recent": residue_failed_recent[:5],
                "stale_failed": residue_stale_failed[:5],
            },
            "active_groups": active_groups[:5],
            "paused_groups": paused_groups[:5],
            "audit_room": {
                "status": audit_brief.get("status"),
                "summary": audit_brief.get("summary"),
                "loop_id": audit_brief.get("loop_id"),
                "findings_path": audit_brief.get("findings_path"),
                "priority_note_path": priority_note.get("path") if priority_note else None,
                "held_loop_launcher_status": held_launcher_status,
                "audit_loop_cadence_status": audit_cadence_status,
            },
        },
        "cold": {
            "completed_recent": completed_recent,
            "audit_completed": audit_completed,
        },
        "recommended_actions": recommended_actions,
        "recommended_read_order": recommended_read_order,
    }
    return snapshot


def render_markdown(snapshot: dict[str, Any]) -> str:
    summary = snapshot["summary"]
    lines = [
        "# Loop Observability Brief",
        "",
        f"- generated_at: {snapshot['generated_at']}",
        f"- observability_level: {snapshot['observability_level']}",
        f"- running_loop_count: {summary['running_loop_count']}",
        f"- trusted_running_loop_count: {summary['trusted_running_loop_count']}",
        f"- held_loop_count: {summary['held_loop_count']}",
        f"- trusted_held_loop_count: {summary['trusted_held_loop_count']}",
        f"- waiting_loop_count: {summary['waiting_loop_count']}",
        f"- failed_recent_count: {summary['failed_recent_count']}",
        f"- trusted_failed_recent_count: {summary['trusted_failed_recent_count']}",
        f"- prototype_failed_recent_count: {summary['prototype_failed_recent_count']}",
        f"- stale_failed_count: {summary['stale_failed_count']}",
        f"- superseded_failed_count: {summary['superseded_failed_count']}",
        f"- trusted_stale_failed_count: {summary['trusted_stale_failed_count']}",
        f"- prototype_stale_failed_count: {summary['prototype_stale_failed_count']}",
        f"- paused_group_count: {summary['paused_group_count']}",
        f"- audit_status: {summary['audit_status'] or '(none)'}",
        f"- held_loop_launcher_status: {summary['held_loop_launcher_status'] or '(none)'}",
        f"- audit_loop_cadence_status: {summary['audit_loop_cadence_status'] or '(none)'}",
        f"- priority_note_status: {summary['priority_note_status']}",
        f"- active_control_note_count: {summary['active_control_note_count']}",
        f"- recommended_actions: {', '.join(snapshot['recommended_actions']) or 'no_action'}",
        "",
        "## Hot",
        "",
    ]
    if snapshot["hot"]["priority_note"]:
        note = snapshot["hot"]["priority_note"]
        lines.append(
            f"- audit-priority-note priority={note.get('priority') or 'normal'} scope={note.get('scope') or 'house'} summary={note.get('summary') or '(none)'}"
        )
    for note in snapshot["hot"]["control_notes"]:
        lines.append(
            f"- loop-control-note loop={note.get('loop_id') or 'unknown'} action={note.get('action') or 'unknown'} "
            f"priority={note.get('priority') or 'normal'} summary={note.get('summary') or '(none)'}"
        )
    for bucket_name in ("running", "held", "failed_recent"):
        entries = snapshot["hot"][bucket_name]
        if not entries:
            continue
        lines.append(f"- {bucket_name}:")
        for item in entries:
            lines.append(
                f"  - {item['loop_id']} class={item.get('loop_class') or 'generic'} state={item.get('state')} phase={item.get('phase')} "
                f"trust={item.get('trust_tier') or 'unknown'} "
                f"profile={item.get('active_profile') or item.get('last_profile') or 'unknown'} "
                f"active_age={item.get('active_run_age_seconds') if item.get('active_run_age_seconds') is not None else '(none)'}s "
                f"checkpoint={item.get('checkpoint_phase') or '(none)'} "
                f"checkpoint_age={item.get('checkpoint_age_seconds') if item.get('checkpoint_age_seconds') is not None else '(none)'}s"
            )
    lines.extend(["", "## Warm", ""])
    for bucket_name in ("waiting", "planned", "stale_failed", "superseded_failed"):
        entries = snapshot["warm"][bucket_name]
        if not entries:
            continue
        lines.append(f"- {bucket_name}:")
        for item in entries:
            lines.append(
                f"  - {item['loop_id']} class={item.get('loop_class') or 'generic'} trust={item.get('trust_tier') or 'unknown'} state={item.get('state')} phase={item.get('phase')}"
            )
    prototype_residue = snapshot["warm"]["prototype_residue"]
    if prototype_residue["failed_recent"] or prototype_residue["stale_failed"]:
        lines.append("- prototype_residue:")
        for item in prototype_residue["failed_recent"] + prototype_residue["stale_failed"]:
            lines.append(
                f"  - {item['loop_id']} class={item.get('loop_class') or 'generic'} state={item.get('state')} phase={item.get('phase')}"
            )
    if snapshot["warm"]["paused_groups"]:
        lines.append(f"- paused_groups: {len(snapshot['warm']['paused_groups'])}")
    if snapshot["warm"]["active_groups"]:
        lines.append(f"- active_groups: {len(snapshot['warm']['active_groups'])}")
    lines.extend(["", "## Cold", ""])
    for item in snapshot["cold"]["completed_recent"]:
        lines.append(
            f"- completed: {item['loop_id']} class={item.get('loop_class') or 'generic'} updated_at={item.get('updated_at') or 'unknown'}"
        )
    lines.extend(["", "## Read Order"])
    for path in snapshot["recommended_read_order"]:
        lines.append(f"- {path}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", default=str(LOOP_OBSERVABILITY_ROOT))
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_root = pathlib.Path(args.state_root)
    snapshot = build_snapshot()
    if args.stdout or args.json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
        return 0
    latest_json = state_root / "latest.json"
    latest_md = state_root / "latest.md"
    history = state_root / "history.jsonl"
    atomic_write_text(latest_json, json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    atomic_write_text(latest_md, render_markdown(snapshot))
    append_jsonl(history, snapshot)
    print(f"OK   wrote {latest_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
