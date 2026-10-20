#!/usr/bin/env python3
"""Summarize a live or finished three-writer Sandwurm sync soak proof root.

The 24-hour three-writer gate intentionally writes its final JSON evidence only
after the guest service exits or cleanly rejects.  While the VM is still alive,
the safest available live signal is the guest console.  This tool discovers that
console from the proof root, parses the content-free stage messages emitted by
``run-sync-three-writer.py``, and prints a small operator-facing status summary.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any


SYNC_RECEIPT = Path("live/workspace-export/guest-receipts/iotox/sync-three-writer.json")
CH_REMOTE_INFO = Path("live/ch-remote-info.json")
PLANNED_LAUNCH = Path("prelaunch/launch/cloud-hypervisor-launch.json")

STAGE_RE = re.compile(
    r"\[\s*(?P<boot_seconds>[0-9]+(?:\.[0-9]+)?)\]\s+"
    r"iotox-three-writer-start\[[0-9]+\]:\s+stage\s+"
    r"elapsed=(?P<elapsed_seconds>[0-9]+(?:\.[0-9]+)?)s\s+"
    r"(?P<message>.*)$"
)
SHADOW_RE = re.compile(r"\bshadow cycle (?P<cycle>[0-9]+) converged\b")
SOAK_START_RE = re.compile(
    r"\bwritable soak started seconds=(?P<seconds>[0-9]+(?:\.[0-9]+)?) "
    r"minimum-cycles=(?P<cycles>[0-9]+)"
    r"(?: cycle-delay=(?P<cycle_delay>[0-9]+(?:\.[0-9]+)?)"
    r" timeout=(?P<timeout>[0-9]+)"
    r" stalled-restart-after=(?P<stalled_restart_after>[0-9]+(?:\.[0-9]+)?)"
    r"(?: restart-settle-policy=(?P<restart_settle_policy>[A-Za-z0-9_-]+))?"
    r"(?: final-boundary-restart-policy="
    r"(?P<final_boundary_restart_policy>[A-Za-z0-9_-]+))?"
    r"(?: repair-policy=(?P<repair_policy>[A-Za-z0-9_-]+)"
    r" repair-control-timeout-ms=(?P<repair_control_timeout_ms>[0-9]+))?)?\b"
)
SOAK_CYCLE_RE = re.compile(r"\bwritable soak cycle (?P<cycle>[0-9]+) converged\b")
SOAK_RESTART_RE = re.compile(
    r"\bwritable soak(?: cycle (?P<cycle>[0-9]+))? restarting node "
    r"(?P<node>[A-Za-z0-9_-]+)\b"
)
SOAK_REPAIR_DEFERRED_RE = re.compile(
    r"\bwritable soak cycle (?P<cycle>[0-9]+) "
    r"sync-repair deferred after scheduled restart\b"
)
SOAK_RESTART_SETTLE_RE = re.compile(
    r"\bwritable soak cycle (?P<cycle>[0-9]+) restart-settle sync-repair "
    r"(?P<state>started|completed)\b"
)
SOAK_FINAL_BOUNDARY_RESTART_SKIP_RE = re.compile(
    r"\bwritable soak cycle (?P<cycle>[0-9]+) scheduled restart skipped "
    r"at final boundary\b"
)
SOAK_REPAIR_RUN_RE = re.compile(
    r"\bwritable soak cycle (?P<cycle>[0-9]+) sync-repair "
    r"(?P<kind>scheduled|deferred) (?P<state>started|completed)\b"
)
SOAK_DONE_RE = re.compile(
    r"\bwritable soak completed cycles=(?P<cycles>[0-9]+) "
    r"elapsed-ms=(?P<elapsed_ms>[0-9]+)\b"
)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def discover_console(proof_root: Path) -> Path | None:
    info = read_json(proof_root / CH_REMOTE_INFO)
    if info:
        console = (
            info.get("config", {})
            .get("console", {})
            .get("file")
        )
        if isinstance(console, str) and console:
            path = Path(console)
            if path.is_file():
                return path

    launch = read_json(proof_root / PLANNED_LAUNCH)
    if launch:
        console = launch.get("vmm", {}).get("console")
        if isinstance(console, str) and console:
            path = Path(console)
            if path.is_file():
                return path

    return None


def console_tail_text(path: Path, limit_bytes: int = 8 * 1024 * 1024) -> str:
    size = path.stat().st_size
    with path.open("rb") as source:
        if size > limit_bytes:
            source.seek(size - limit_bytes)
        return source.read().decode("utf-8", errors="replace")


def parse_console(path: Path, now: float) -> dict[str, Any]:
    text = console_tail_text(path)
    stat = path.stat()
    events: list[dict[str, Any]] = []
    shadow_cycle = 0
    soak_requested_seconds: float | None = None
    soak_minimum_cycles: int | None = None
    soak_start_elapsed_seconds: float | None = None
    soak_cycle_delay_seconds: float | None = None
    soak_timeout_seconds: int | None = None
    soak_stalled_restart_after_seconds: float | None = None
    soak_restart_settle_policy: str | None = None
    soak_final_boundary_restart_policy: str | None = None
    soak_restart_settle_passes = 0
    soak_restart_skipped_final_boundary = 0
    soak_restart_skipped_cycles: list[int] = []
    soak_last_restart_settle_cycle: int | None = None
    soak_last_restart_settle_state: str | None = None
    soak_repair_restart_policy: str | None = None
    sync_repair_control_timeout_ms: int | None = None
    soak_cycle = 0
    soak_last_restart_cycle: int | None = None
    soak_last_restart_node: str | None = None
    soak_repair_deferrals = 0
    soak_last_repair_cycle: int | None = None
    soak_last_repair_kind: str | None = None
    soak_last_repair_state: str | None = None
    soak_completed_cycles: int | None = None
    soak_completed_elapsed_ms: int | None = None
    saw_failure = False

    for raw_line in text.splitlines():
        if "three-writer qualification failed:" in raw_line:
            saw_failure = True
        match = STAGE_RE.search(raw_line)
        if not match:
            continue
        message = match.group("message").strip()
        elapsed_seconds = float(match.group("elapsed_seconds"))
        event = {
            "boot_seconds": float(match.group("boot_seconds")),
            "elapsed_seconds": elapsed_seconds,
            "message": message,
        }
        events.append(event)

        shadow_match = SHADOW_RE.search(message)
        if shadow_match:
            shadow_cycle = max(shadow_cycle, int(shadow_match.group("cycle")))

        start_match = SOAK_START_RE.search(message)
        if start_match:
            soak_requested_seconds = float(start_match.group("seconds"))
            soak_minimum_cycles = int(start_match.group("cycles"))
            soak_start_elapsed_seconds = elapsed_seconds
            if start_match.group("cycle_delay") is not None:
                soak_cycle_delay_seconds = float(start_match.group("cycle_delay"))
            if start_match.group("timeout") is not None:
                soak_timeout_seconds = int(start_match.group("timeout"))
            if start_match.group("stalled_restart_after") is not None:
                soak_stalled_restart_after_seconds = float(
                    start_match.group("stalled_restart_after")
                )
            if start_match.group("restart_settle_policy") is not None:
                soak_restart_settle_policy = start_match.group(
                    "restart_settle_policy"
                )
            if start_match.group("final_boundary_restart_policy") is not None:
                soak_final_boundary_restart_policy = start_match.group(
                    "final_boundary_restart_policy"
                )
            if start_match.group("repair_policy") is not None:
                soak_repair_restart_policy = start_match.group("repair_policy")
            if start_match.group("repair_control_timeout_ms") is not None:
                sync_repair_control_timeout_ms = int(
                    start_match.group("repair_control_timeout_ms")
                )

        cycle_match = SOAK_CYCLE_RE.search(message)
        if cycle_match:
            soak_cycle = max(soak_cycle, int(cycle_match.group("cycle")))

        restart_match = SOAK_RESTART_RE.search(message)
        if restart_match:
            cycle_text = restart_match.group("cycle")
            if cycle_text is not None:
                soak_last_restart_cycle = int(cycle_text)
            soak_cycle = max(soak_cycle, soak_last_restart_cycle)
            soak_last_restart_node = restart_match.group("node")

        restart_settle_match = SOAK_RESTART_SETTLE_RE.search(message)
        if restart_settle_match:
            soak_last_restart_settle_cycle = int(
                restart_settle_match.group("cycle")
            )
            soak_last_restart_settle_state = restart_settle_match.group("state")
            if soak_last_restart_settle_state == "completed":
                soak_restart_settle_passes += 1

        restart_skip_match = SOAK_FINAL_BOUNDARY_RESTART_SKIP_RE.search(message)
        if restart_skip_match:
            skip_cycle = int(restart_skip_match.group("cycle"))
            soak_restart_skipped_final_boundary += 1
            soak_restart_skipped_cycles.append(skip_cycle)
            soak_cycle = max(soak_cycle, skip_cycle)

        repair_deferred_match = SOAK_REPAIR_DEFERRED_RE.search(message)
        if repair_deferred_match:
            soak_repair_deferrals += 1
            soak_last_repair_cycle = int(repair_deferred_match.group("cycle"))
            soak_last_repair_kind = "deferred"
            soak_last_repair_state = "deferred"

        repair_run_match = SOAK_REPAIR_RUN_RE.search(message)
        if repair_run_match:
            soak_last_repair_cycle = int(repair_run_match.group("cycle"))
            soak_last_repair_kind = repair_run_match.group("kind")
            soak_last_repair_state = repair_run_match.group("state")

        done_match = SOAK_DONE_RE.search(message)
        if done_match:
            soak_completed_cycles = int(done_match.group("cycles"))
            soak_completed_elapsed_ms = int(done_match.group("elapsed_ms"))

    last_event = events[-1] if events else None
    estimate: dict[str, Any] = {}
    if last_event is not None:
        last_event_elapsed = float(last_event["elapsed_seconds"])
        estimated_start_wall = stat.st_mtime - last_event_elapsed
        estimate["estimated_script_start_wall"] = int(estimated_start_wall)
        estimate["last_progress_age_seconds"] = max(0, int(now - stat.st_mtime))
        if soak_start_elapsed_seconds is not None:
            soak_started_wall = estimated_start_wall + soak_start_elapsed_seconds
            soak_wall_elapsed = max(0, int(now - soak_started_wall))
            estimate["estimated_soak_started_wall"] = int(soak_started_wall)
            estimate["estimated_soak_wall_elapsed_seconds"] = soak_wall_elapsed
            if soak_requested_seconds is not None:
                wall_remaining = max(
                    0, int(soak_requested_seconds - soak_wall_elapsed)
                )
                estimate["estimated_soak_wall_remaining_seconds"] = wall_remaining
            if soak_minimum_cycles is not None:
                cycle_remaining = max(0, soak_minimum_cycles - soak_cycle)
                estimate["soak_cycle_remaining"] = cycle_remaining
                if soak_cycle > 0 and cycle_remaining > 0:
                    average_cycle_seconds = max(
                        1, int(math.ceil(soak_wall_elapsed / soak_cycle))
                    )
                    estimate["estimated_soak_average_cycle_seconds"] = (
                        average_cycle_seconds
                    )
                    estimate[
                        "estimated_soak_cycle_floor_remaining_seconds"
                    ] = cycle_remaining * average_cycle_seconds
                elif cycle_remaining == 0:
                    estimate["estimated_soak_cycle_floor_remaining_seconds"] = 0
                wall_remaining = estimate.get("estimated_soak_wall_remaining_seconds")
                cycle_floor_remaining = estimate.get(
                    "estimated_soak_cycle_floor_remaining_seconds"
                )
                if isinstance(wall_remaining, int) and isinstance(
                    cycle_floor_remaining, int
                ):
                    estimate["estimated_soak_acceptance_remaining_seconds"] = max(
                        wall_remaining, cycle_floor_remaining
                    )

    return {
        "console": str(path),
        "console_size_bytes": stat.st_size,
        "stage_event_count": len(events),
        "last_event": last_event,
        "shadow_cycle": shadow_cycle,
        "soak_started": soak_start_elapsed_seconds is not None,
        "soak_requested_seconds": (
            int(soak_requested_seconds)
            if soak_requested_seconds is not None
            else None
        ),
        "soak_minimum_cycles": soak_minimum_cycles,
        "soak_cycle_delay_seconds": soak_cycle_delay_seconds,
        "soak_timeout_seconds": soak_timeout_seconds,
        "soak_stalled_restart_after_seconds": soak_stalled_restart_after_seconds,
        "soak_restart_settle_policy": soak_restart_settle_policy,
        "soak_final_boundary_restart_policy": soak_final_boundary_restart_policy,
        "soak_restart_settle_passes": soak_restart_settle_passes,
        "soak_restart_skipped_final_boundary": (
            soak_restart_skipped_final_boundary
        ),
        "soak_restart_skipped_cycles": soak_restart_skipped_cycles,
        "soak_last_restart_settle_cycle": soak_last_restart_settle_cycle,
        "soak_last_restart_settle_state": soak_last_restart_settle_state,
        "soak_repair_restart_policy": soak_repair_restart_policy,
        "sync_repair_control_timeout_ms": sync_repair_control_timeout_ms,
        "soak_cycle": soak_cycle,
        "soak_last_restart_cycle": soak_last_restart_cycle,
        "soak_last_restart_node": soak_last_restart_node,
        "soak_repair_deferrals": soak_repair_deferrals,
        "soak_last_repair_cycle": soak_last_repair_cycle,
        "soak_last_repair_kind": soak_last_repair_kind,
        "soak_last_repair_state": soak_last_repair_state,
        "soak_completed_cycles": soak_completed_cycles,
        "soak_completed_elapsed_ms": soak_completed_elapsed_ms,
        "console_failure_seen": saw_failure,
        **estimate,
    }


def receipt_summary(proof_root: Path) -> dict[str, Any]:
    path = proof_root / SYNC_RECEIPT
    record = read_json(path)
    if record is None:
        return {"receipt_present": False, "receipt": str(path)}
    keys = [
        "schema",
        "status",
        "elapsed_ms",
        "soak_campaign",
        "soak_completed",
        "soak_requested_seconds",
        "soak_minimum_cycles",
        "soak_cycles",
        "soak_elapsed_ms",
        "soak_daemon_restarts",
        "soak_restart_settle_policy",
        "soak_restart_settle_passes",
        "soak_final_boundary_restart_policy",
        "soak_restart_skipped_final_boundary",
        "soak_restart_skipped_cycles",
        "soak_repair_passes",
        "soak_delete_cycles",
        "maintenance_lifecycle",
        "recovery_rehearsal",
        "storage_fault_rehearsal",
        "contains_secrets",
        "soak_contains_secrets",
    ]
    return {
        "receipt_present": True,
        "receipt": str(path),
        "receipt_summary": {key: record.get(key) for key in keys if key in record},
    }


def cloud_hypervisor_process_observed(
    proof_root: Path, console_path: Path | None
) -> bool:
    needles = [str(proof_root)]
    if console_path is not None:
        needles.append(str(console_path))
    proc = Path("/proc")
    if not proc.is_dir():
        return False
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            raw = (entry / "cmdline").read_bytes()
        except OSError:
            continue
        if not raw:
            continue
        cmdline = raw.replace(b"\0", b" ").decode("utf-8", errors="replace")
        if "cloud-hypervisor" not in cmdline:
            continue
        if any(needle in cmdline for needle in needles):
            return True
    return False


def vmm_summary(proof_root: Path, console_path: Path | None) -> dict[str, Any]:
    info = read_json(proof_root / CH_REMOTE_INFO)
    process_seen = cloud_hypervisor_process_observed(proof_root, console_path)
    if not info:
        return {
            "vmm_state": "unknown",
            "vmm_reported_state": "unknown",
            "vmm_process_observed": process_seen,
        }
    reported = info.get("state", "unknown")
    state = reported
    if reported == "Running" and not process_seen:
        state = "stale-running-no-process"
    return {
        "vmm_state": state,
        "vmm_reported_state": reported,
        "vmm_process_observed": process_seen,
        "vmm_memory_bytes": info.get("memory_actual_size"),
        "vmm_boot_vcpus": info.get("config", {}).get("cpus", {}).get("boot_vcpus"),
    }


def phase_from(console: dict[str, Any], receipt: dict[str, Any]) -> str:
    if receipt.get("receipt_present"):
        status = receipt.get("receipt_summary", {}).get("status", "unknown")
        return f"receipt-{status}"
    if console.get("console_failure_seen"):
        return "failed-no-receipt"
    if console.get("soak_completed_cycles") is not None:
        return "post-soak-followups"
    if console.get("soak_started"):
        return "soak-running"
    if console.get("shadow_cycle", 0):
        return "shadow-running"
    if console.get("last_event"):
        return "startup-running"
    return "unknown"


def health_from(
    phase: str,
    console: dict[str, Any],
    receipt: dict[str, Any],
    vmm: dict[str, Any],
    stale_seconds: int,
) -> str:
    if receipt.get("receipt_present"):
        status = receipt.get("receipt_summary", {}).get("status")
        if status == "passed":
            return "passed"
        if status == "rejected":
            return "rejected"
        return "receipt-unknown"
    if phase == "failed-no-receipt":
        return "failed"
    if vmm.get("vmm_state") not in {"Running", "unknown"}:
        return "inactive-no-receipt"
    age = console.get("last_progress_age_seconds")
    progress_stale_seconds = console.get("progress_stale_seconds")
    if not isinstance(progress_stale_seconds, int):
        progress_stale_seconds = stale_seconds
    if isinstance(age, int) and age > progress_stale_seconds:
        return "stale"
    return "running"


def progress_stale_seconds_for(
    phase: str,
    console: dict[str, Any],
    stale_seconds: int,
) -> int:
    if phase != "soak-running":
        return stale_seconds
    requested_seconds = console.get("soak_requested_seconds")
    minimum_cycles = console.get("soak_minimum_cycles")
    if not (
        isinstance(requested_seconds, int)
        and isinstance(minimum_cycles, int)
        and minimum_cycles > 0
    ):
        return stale_seconds
    # The long soak deliberately logs normal progress at cycle 1 and then every
    # tenth cycle.  Derive an operator stale window from the requested soak
    # duration and minimum cycles so status stays truthful when the experiment is
    # intentionally quiet, while still bounding real "no progress" states.
    per_cycle_seconds = max(1, requested_seconds // minimum_cycles)
    cycle_delay_seconds = console.get("soak_cycle_delay_seconds")
    timeout_seconds = console.get("soak_timeout_seconds")
    stalled_restart_after_seconds = console.get(
        "soak_stalled_restart_after_seconds"
    )
    if (
        isinstance(cycle_delay_seconds, float)
        and isinstance(timeout_seconds, int)
        and isinstance(stalled_restart_after_seconds, float)
    ):
        bounded_wait = (
            stalled_restart_after_seconds
            if stalled_restart_after_seconds > 0.0
            else float(timeout_seconds)
        )
        per_cycle_seconds = int(cycle_delay_seconds + bounded_wait)
    soak_progress_seconds = min(7200, max(stale_seconds, per_cycle_seconds * 12))
    return soak_progress_seconds


def summarize(proof_root: Path, stale_seconds: int, now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    proof_root = proof_root.resolve()
    receipt = receipt_summary(proof_root)
    console_path = discover_console(proof_root)
    vmm = vmm_summary(proof_root, console_path)
    console = (
        parse_console(console_path, now)
        if console_path is not None
        else {"console": None, "stage_event_count": 0}
    )
    phase = phase_from(console, receipt)
    console["progress_stale_seconds"] = progress_stale_seconds_for(
        phase, console, stale_seconds
    )
    health = health_from(phase, console, receipt, vmm, stale_seconds)
    return {
        "schema": "iotox.sync-three-writer-soak-status.v1",
        "proof_root": str(proof_root),
        "observed_at": int(now),
        "phase": phase,
        "health": health,
        **vmm,
        **console,
        **receipt,
    }


def format_duration(seconds: Any) -> str:
    if not isinstance(seconds, int):
        return "unknown"
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def print_human(summary: dict[str, Any]) -> None:
    last = summary.get("last_event") or {}
    receipt = summary.get("receipt_summary") or {}
    pairs: list[tuple[str, Any]] = [
        ("health", summary.get("health")),
        ("phase", summary.get("phase")),
        ("vmm", summary.get("vmm_state")),
        ("vmm-process", "present" if summary.get("vmm_process_observed") else "absent"),
        ("shadow-cycle", summary.get("shadow_cycle")),
        ("soak-cycle", summary.get("soak_cycle")),
        ("soak-minimum-cycles", summary.get("soak_minimum_cycles")),
        ("soak-cycle-remaining", summary.get("soak_cycle_remaining")),
        ("soak-elapsed", format_duration(summary.get("estimated_soak_wall_elapsed_seconds"))),
        ("soak-wall-remaining", format_duration(summary.get("estimated_soak_wall_remaining_seconds"))),
        (
            "soak-cycle-floor-remaining",
            format_duration(summary.get("estimated_soak_cycle_floor_remaining_seconds")),
        ),
        (
            "soak-acceptance-remaining",
            format_duration(summary.get("estimated_soak_acceptance_remaining_seconds")),
        ),
        ("last-progress-age", format_duration(summary.get("last_progress_age_seconds"))),
        ("stale-after", format_duration(summary.get("progress_stale_seconds"))),
        ("last-stage", last.get("message", "none")),
    ]
    if summary.get("soak_last_repair_cycle") is not None:
        pairs.insert(
            6,
            (
                "last-repair",
                f"{summary.get('soak_last_repair_kind')}:"
                f"{summary.get('soak_last_repair_state')}@"
                f"{summary.get('soak_last_repair_cycle')}",
            ),
        )
    if summary.get("soak_last_restart_settle_cycle") is not None:
        pairs.insert(
            6,
            (
                "last-restart-settle",
                f"{summary.get('soak_last_restart_settle_state')}@"
                f"{summary.get('soak_last_restart_settle_cycle')}",
            ),
        )
    if summary.get("soak_restart_settle_passes"):
        pairs.insert(
            6,
            ("restart-settle-passes", summary.get("soak_restart_settle_passes")),
        )
    if summary.get("soak_restart_settle_policy") is not None:
        pairs.insert(
            6,
            ("restart-settle-policy", summary.get("soak_restart_settle_policy")),
        )
    if summary.get("soak_final_boundary_restart_policy") is not None:
        pairs.insert(
            6,
            (
                "final-boundary-restart-policy",
                summary.get("soak_final_boundary_restart_policy"),
            ),
        )
    if summary.get("soak_restart_skipped_final_boundary"):
        pairs.insert(
            6,
            (
                "final-boundary-restarts-skipped",
                summary.get("soak_restart_skipped_final_boundary"),
            ),
        )
    if summary.get("soak_repair_deferrals"):
        pairs.insert(6, ("repair-deferrals", summary.get("soak_repair_deferrals")))
    if summary.get("sync_repair_control_timeout_ms") is not None:
        pairs.insert(
            6,
            (
                "repair-control-timeout-ms",
                summary.get("sync_repair_control_timeout_ms"),
            ),
        )
    if summary.get("soak_repair_restart_policy") is not None:
        pairs.insert(6, ("repair-policy", summary.get("soak_repair_restart_policy")))
    if summary.get("soak_last_restart_cycle") is not None:
        pairs.insert(6, ("last-restart-cycle", summary.get("soak_last_restart_cycle")))
    if summary.get("soak_last_restart_node") is not None:
        pairs.insert(6, ("last-restart-node", summary.get("soak_last_restart_node")))
    if receipt:
        pairs.append(("receipt-status", receipt.get("status")))
        if "soak_cycles" in receipt:
            pairs.append(("receipt-soak-cycles", receipt.get("soak_cycles")))
        if "soak_elapsed_ms" in receipt:
            pairs.append(("receipt-soak-elapsed", format_duration(receipt["soak_elapsed_ms"] // 1000)))
    for key, value in pairs:
        print(f"{key}={value}")
    print(f"proof-root={summary.get('proof_root')}")
    print(f"console={summary.get('console')}")
    print(f"receipt={summary.get('receipt')}")


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="iotox-soak-status-test-") as raw:
        root = Path(raw)
        console = root / "console.log"
        console.write_text(
            "[  10.000000] iotox-three-writer-start[620]: stage elapsed=6.0s "
            "three friendship edges confirmed\n"
            "[ 182.223457] iotox-three-writer-start[620]: stage elapsed=178.3s "
            "writable soak started seconds=86400.000 minimum-cycles=288 "
            "cycle-delay=240.000 timeout=900 stalled-restart-after=0.000 "
            "restart-settle-policy=repair-before-edit "
            "final-boundary-restart-policy=skip-if-floor-satisfied "
            "repair-policy=defer repair-control-timeout-ms=120000\n"
            "[ 219.828764] iotox-three-writer-start[620]: stage elapsed=216.0s "
            "writable soak cycle 1 converged\n"
            "[ 700.000000] iotox-three-writer-start[620]: stage elapsed=696.0s "
            "writable soak cycle 10 converged\n"
            "[ 900.000000] iotox-three-writer-start[620]: stage elapsed=896.0s "
            "writable soak cycle 24 restarting node a\n"
            "[ 901.000000] iotox-three-writer-start[620]: stage elapsed=897.0s "
            "writable soak cycle 24 restart-settle sync-repair started\n"
            "[ 901.500000] iotox-three-writer-start[620]: stage elapsed=897.5s "
            "writable soak cycle 24 restart-settle sync-repair completed\n"
            "[ 902.000000] iotox-three-writer-start[620]: stage elapsed=898.0s "
            "writable soak cycle 24 sync-repair deferred after scheduled restart\n"
            "[ 903.000000] iotox-three-writer-start[620]: stage elapsed=899.0s "
            "writable soak cycle 25 sync-repair deferred started\n"
            "[ 904.000000] iotox-three-writer-start[620]: stage elapsed=900.0s "
            "writable soak cycle 25 sync-repair deferred completed\n",
            encoding="utf-8",
        )
        live = root / "live"
        live.mkdir()
        (live / "ch-remote-info.json").write_text(
            json.dumps(
                {
                    "state": "Running",
                    "memory_actual_size": 2147483648,
                    "config": {
                        "cpus": {"boot_vcpus": 2},
                        "console": {"file": str(console)},
                    },
                }
            ),
            encoding="utf-8",
        )
        os.utime(console, (2000, 2000))
        summary = summarize(root, stale_seconds=1200, now=2100)
        assert summary["phase"] == "soak-running"
        assert summary["health"] == "inactive-no-receipt"
        assert summary["vmm_state"] == "stale-running-no-process"
        assert summary["soak_cycle"] == 24
        assert summary["soak_minimum_cycles"] == 288
        assert summary["soak_cycle_remaining"] == 264
        assert summary["estimated_soak_cycle_floor_remaining_seconds"] == 9240
        assert summary["estimated_soak_acceptance_remaining_seconds"] == 85579
        assert summary["soak_last_restart_cycle"] == 24
        assert summary["soak_last_restart_node"] == "a"
        assert summary["soak_requested_seconds"] == 86400
        assert summary["soak_cycle_delay_seconds"] == 240.0
        assert summary["soak_timeout_seconds"] == 900
        assert summary["soak_stalled_restart_after_seconds"] == 0.0
        assert summary["soak_restart_settle_policy"] == "repair-before-edit"
        assert summary["soak_final_boundary_restart_policy"] == "skip-if-floor-satisfied"
        assert summary["soak_restart_settle_passes"] == 1
        assert summary["soak_last_restart_settle_cycle"] == 24
        assert summary["soak_last_restart_settle_state"] == "completed"
        assert summary["soak_repair_restart_policy"] == "defer"
        assert summary["sync_repair_control_timeout_ms"] == 120000
        assert summary["soak_repair_deferrals"] == 1
        assert summary["soak_last_repair_cycle"] == 25
        assert summary["soak_last_repair_kind"] == "deferred"
        assert summary["soak_last_repair_state"] == "completed"
        assert summary["progress_stale_seconds"] == 7200

        receipt_path = root / SYNC_RECEIPT
        receipt_path.parent.mkdir(parents=True)
        receipt_path.write_text(
            json.dumps(
                {
                    "schema": "iotox.sync-three-writer.v1",
                    "status": "passed",
                    "soak_campaign": True,
                    "soak_completed": True,
                    "soak_cycles": 1234,
                    "soak_elapsed_ms": 86401000,
                    "contains_secrets": False,
                    "soak_contains_secrets": False,
                }
            ),
            encoding="utf-8",
        )
        summary = summarize(root, stale_seconds=1200, now=2100)
        assert summary["phase"] == "receipt-passed"
        assert summary["health"] == "passed"
        assert summary["receipt_summary"]["soak_cycles"] == 1234

    print("sync-three-writer soak status self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--stale-seconds", type=int, default=1200)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.proof_root is None:
        parser.error("proof_root is required unless --self-test is used")
    if args.stale_seconds < 1:
        parser.error("--stale-seconds must be positive")

    summary = summarize(args.proof_root, args.stale_seconds)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary)
    return 0 if summary["health"] in {"running", "passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
