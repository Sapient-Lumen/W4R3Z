#!/usr/bin/env python3
"""Watch a live or finished three-writer Sandwurm sync soak proof root.

This is a small operator wrapper around ``inspect-sync-three-writer-soak.py``.
It keeps the inspector as the single parser, writes optional JSONL snapshots,
and exits when the proof reaches a terminal health state unless told to keep
watching.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
INSPECTOR_PATH = SCRIPT_DIR / "inspect-sync-three-writer-soak.py"


def load_inspector() -> Any:
    spec = importlib.util.spec_from_file_location(
        "iotox_inspect_sync_three_writer_soak", INSPECTOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load inspector: {INSPECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSPECTOR = load_inspector()


TERMINAL_HEALTH = {
    "passed",
    "rejected",
    "failed",
    "inactive-no-receipt",
    "receipt-unknown",
    "stale",
}


def iso_now(now: float | None = None) -> str:
    value = datetime.fromtimestamp(time.time() if now is None else now, UTC)
    return value.isoformat().replace("+00:00", "Z")


def compact_line(summary: dict[str, Any]) -> str:
    last = summary.get("last_event") or {}
    receipt = summary.get("receipt_summary") or {}
    fields: list[tuple[str, object]] = [
        ("ts", iso_now(float(summary["observed_at"]))),
        ("health", summary.get("health")),
        ("phase", summary.get("phase")),
        ("vmm", summary.get("vmm_state")),
        ("shadow", summary.get("shadow_cycle")),
        ("soak", summary.get("soak_cycle")),
        ("min_cycles", summary.get("soak_minimum_cycles")),
        ("cycle_remaining", summary.get("soak_cycle_remaining")),
        (
            "elapsed",
            INSPECTOR.format_duration(
                summary.get("estimated_soak_wall_elapsed_seconds")
            ),
        ),
        (
            "wall_remaining",
            INSPECTOR.format_duration(
                summary.get("estimated_soak_wall_remaining_seconds")
            ),
        ),
        (
            "acceptance_remaining",
            INSPECTOR.format_duration(
                summary.get("estimated_soak_acceptance_remaining_seconds")
            ),
        ),
        (
            "age",
            INSPECTOR.format_duration(summary.get("last_progress_age_seconds")),
        ),
        (
            "stale_after",
            INSPECTOR.format_duration(summary.get("progress_stale_seconds")),
        ),
    ]
    if summary.get("soak_last_restart_node") is not None:
        fields.append(("last_restart_node", summary.get("soak_last_restart_node")))
    if summary.get("soak_last_restart_cycle") is not None:
        fields.append(("last_restart_cycle", summary.get("soak_last_restart_cycle")))
    if summary.get("soak_restart_settle_policy") is not None:
        fields.append(
            (
                "restart_settle_policy",
                summary.get("soak_restart_settle_policy"),
            )
        )
    if summary.get("soak_final_boundary_restart_policy") is not None:
        fields.append(
            (
                "final_boundary_restart_policy",
                summary.get("soak_final_boundary_restart_policy"),
            )
        )
    if summary.get("soak_restart_settle_passes"):
        fields.append(
            ("restart_settle_passes", summary.get("soak_restart_settle_passes"))
        )
    if summary.get("soak_restart_skipped_final_boundary"):
        fields.append(
            (
                "final_boundary_restarts_skipped",
                summary.get("soak_restart_skipped_final_boundary"),
            )
        )
    if summary.get("soak_last_restart_settle_cycle") is not None:
        fields.append(
            (
                "last_restart_settle",
                f"{summary.get('soak_last_restart_settle_state')}@"
                f"{summary.get('soak_last_restart_settle_cycle')}",
            )
        )
    if summary.get("soak_repair_restart_policy") is not None:
        fields.append(("repair_policy", summary.get("soak_repair_restart_policy")))
    if summary.get("sync_repair_control_timeout_ms") is not None:
        fields.append(("repair_timeout_ms", summary.get("sync_repair_control_timeout_ms")))
    if summary.get("soak_repair_deferrals"):
        fields.append(("repair_deferrals", summary.get("soak_repair_deferrals")))
    if summary.get("soak_last_repair_cycle") is not None:
        fields.append(
            (
                "last_repair",
                f"{summary.get('soak_last_repair_kind')}:"
                f"{summary.get('soak_last_repair_state')}@"
                f"{summary.get('soak_last_repair_cycle')}",
            )
        )
    if receipt:
        fields.append(("receipt", receipt.get("status")))
        if "soak_cycles" in receipt:
            fields.append(("receipt_soak", receipt.get("soak_cycles")))
    fields.append(("stage", last.get("message", "none")))
    return " ".join(f"{key}={value}" for key, value in fields)


def change_signature(summary: dict[str, Any]) -> tuple[object, ...]:
    last = summary.get("last_event") or {}
    receipt = summary.get("receipt_summary") or {}
    return (
        summary.get("health"),
        summary.get("phase"),
        summary.get("vmm_state"),
        summary.get("shadow_cycle"),
        summary.get("soak_cycle"),
        summary.get("soak_cycle_remaining"),
        summary.get("estimated_soak_acceptance_remaining_seconds"),
        summary.get("soak_last_restart_node"),
        summary.get("soak_last_restart_cycle"),
        summary.get("soak_restart_settle_policy"),
        summary.get("soak_final_boundary_restart_policy"),
        summary.get("soak_restart_settle_passes"),
        summary.get("soak_restart_skipped_final_boundary"),
        tuple(summary.get("soak_restart_skipped_cycles") or []),
        summary.get("soak_last_restart_settle_state"),
        summary.get("soak_last_restart_settle_cycle"),
        summary.get("soak_repair_restart_policy"),
        summary.get("sync_repair_control_timeout_ms"),
        summary.get("soak_repair_deferrals"),
        summary.get("soak_last_repair_kind"),
        summary.get("soak_last_repair_state"),
        summary.get("soak_last_repair_cycle"),
        receipt.get("status"),
        receipt.get("soak_cycles"),
        last.get("message"),
    )


def append_jsonl(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as target:
        target.write(json.dumps(summary, sort_keys=True, separators=(",", ":")))
        target.write("\n")


def exit_code_for(health: str) -> int:
    if health == "passed":
        return 0
    if health == "running":
        return 0
    return 1


def watch(args: argparse.Namespace) -> int:
    proof_root = args.proof_root.resolve()
    samples = 0
    last_signature: tuple[object, ...] | None = None
    last_printed_sample = 0
    while True:
        now = time.time()
        summary = INSPECTOR.summarize(
            proof_root, stale_seconds=args.stale_seconds, now=now
        )
        samples += 1
        signature = change_signature(summary)
        health = str(summary.get("health", "unknown"))
        should_print = args.print_mode == "all"
        if args.print_mode == "changes":
            should_print = last_signature is None or signature != last_signature
            if args.heartbeat_samples:
                should_print = should_print or (
                    samples - last_printed_sample >= args.heartbeat_samples
                )
            should_print = should_print or health in TERMINAL_HEALTH
        if should_print:
            if args.json:
                print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
            else:
                print(compact_line(summary), flush=True)
            last_printed_sample = samples
        last_signature = signature
        if args.jsonl is not None:
            append_jsonl(args.jsonl, summary)

        if not args.keep_going and health in TERMINAL_HEALTH:
            return exit_code_for(health)
        if args.max_samples and samples >= args.max_samples:
            return exit_code_for(health)
        time.sleep(args.interval_seconds)


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-soak-watch-test-") as raw:
        root = Path(raw)
        console = root / "console.log"
        console.write_text(
            "[  10.000000] iotox-three-writer-start[620]: stage elapsed=6.0s "
            "writable soak started seconds=86400.000 minimum-cycles=288 "
            "cycle-delay=240.000 timeout=900 stalled-restart-after=0.000 "
            "restart-settle-policy=repair-before-edit "
            "final-boundary-restart-policy=skip-if-floor-satisfied "
            "repair-policy=defer repair-control-timeout-ms=120000\n"
            "[  11.000000] iotox-three-writer-start[620]: stage elapsed=7.0s "
            "writable soak cycle 1 converged\n"
            "[  12.000000] iotox-three-writer-start[620]: stage elapsed=8.0s "
            "writable soak cycle 2 restart-settle sync-repair completed\n"
            "[  13.000000] iotox-three-writer-start[620]: stage elapsed=9.0s "
            "writable soak cycle 2 sync-repair deferred after scheduled restart\n",
            encoding="utf-8",
        )
        live = root / "live"
        live.mkdir()
        (live / "ch-remote-info.json").write_text(
            json.dumps(
                {
                    "state": "Running",
                    "config": {"console": {"file": str(console)}},
                }
            ),
            encoding="utf-8",
        )
        jsonl = root / "watch.jsonl"
        namespace = argparse.Namespace(
            proof_root=root,
            interval_seconds=1,
            stale_seconds=1200,
            json=False,
            jsonl=jsonl,
            print_mode="all",
            heartbeat_samples=0,
            keep_going=True,
            max_samples=1,
        )
        rc = watch(namespace)
        if rc != 1:
            raise AssertionError(f"unexpected rc from inactive fake VM: {rc}")
        records = [json.loads(line) for line in jsonl.read_text().splitlines()]
        if len(records) != 1 or records[0].get("soak_cycle") != 1:
            raise AssertionError("watch JSONL did not capture the fake soak cycle")
        if records[0].get("soak_repair_deferrals") != 1:
            raise AssertionError("watch JSONL did not capture the repair deferral")
        if records[0].get("soak_restart_settle_passes") != 1:
            raise AssertionError("watch JSONL did not capture restart settle")
        if (
            records[0].get("soak_final_boundary_restart_policy")
            != "skip-if-floor-satisfied"
        ):
            raise AssertionError("watch JSONL did not capture final-boundary policy")
    print("sync-three-writer soak watch self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--stale-seconds", type=int, default=1200)
    parser.add_argument("--json", action="store_true", help="print full JSON snapshots")
    parser.add_argument("--jsonl", type=Path, help="append compact JSON snapshots to PATH")
    parser.add_argument(
        "--print-mode",
        choices=("all", "changes"),
        default="all",
        help="print every sample or only content-free state changes",
    )
    parser.add_argument(
        "--heartbeat-samples",
        type=int,
        default=0,
        help="with --print-mode changes, also print every N unchanged samples",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="continue after terminal health states",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="stop after N samples; zero means unlimited",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.proof_root is None:
        parser.error("proof_root is required unless --self-test is used")
    if args.interval_seconds < 1 or args.interval_seconds > 60:
        parser.error("--interval-seconds must be between 1 and 60")
    if args.stale_seconds < 1:
        parser.error("--stale-seconds must be positive")
    if args.max_samples < 0:
        parser.error("--max-samples must be non-negative")
    if args.heartbeat_samples < 0:
        parser.error("--heartbeat-samples must be non-negative")
    return watch(args)


if __name__ == "__main__":
    raise SystemExit(main())
