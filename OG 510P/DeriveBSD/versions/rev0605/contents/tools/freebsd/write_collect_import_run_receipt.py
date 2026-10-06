#!/usr/bin/env python3
"""Write the strict collect/import wrapper run receipt atomically.

The root-running shell wrapper should not own JSON construction or direct receipt
writes.  This helper consumes the wrapper's stage environment, validates the
stage vocabulary, refuses symlink destinations, writes a same-directory temporary
file with O_EXCL, fsyncs it, and publishes with os.replace.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import host_proof_contract as contract
from validate_collect_import_run_receipt import validate_run_receipt

KIND = "removable.media.local.freebsd.host.proof.collect_import.run.receipt"
SCHEMA_VERSION = "0.1"
WRITER_REL = "tools/freebsd/write_collect_import_run_receipt.py"
WRITE_POLICY = "atomic-tempfile-fsync-osreplace-symlink-destination-and-ancestor-refused"

NORMAL_STAGE_ORDER = ["collect", "verify_handoff", "import_handoff", "audit_import_root"]
RESUME_STAGE_ORDER = ["resume_handoff", "verify_handoff", "import_handoff", "audit_import_root"]
TERMINAL_STAGES = {"initializing", "complete"}
ALL_STAGES = set(NORMAL_STAGE_ORDER) | set(RESUME_STAGE_ORDER) | TERMINAL_STAGES


def env_bool(name: str) -> bool:
    return os.environ.get(name) == "1"


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, observed {raw!r}") from exc


def stage_list(raw: str | None) -> list[str]:
    stages = [stage for stage in (raw or "").split() if stage]
    unknown = [stage for stage in stages if stage not in ALL_STAGES]
    if unknown:
        raise ValueError(f"unknown completed stage(s): {unknown!r}")
    return stages


def validate_stage_state(current_stage: str, stages_completed: list[str], resume_mode: bool) -> list[str]:
    if current_stage not in ALL_STAGES:
        raise ValueError(f"unknown current stage: {current_stage!r}")
    order = RESUME_STAGE_ORDER if resume_mode else NORMAL_STAGE_ORDER
    if current_stage == "initializing":
        expected_prefix: list[str] = []
    elif current_stage == "complete":
        expected_prefix = order
    elif current_stage in order:
        expected_prefix = order[: order.index(current_stage)]
    else:
        # A normal run may not report resume_handoff, and a resume run may not
        # report collect as the current stage.
        raise ValueError(f"stage {current_stage!r} is invalid for {'resume' if resume_mode else 'normal'} mode")
    if stages_completed != expected_prefix:
        raise ValueError(
            "completed stages are not the expected prefix for the current stage: "
            f"observed={stages_completed!r} expected={expected_prefix!r} current={current_stage!r}"
        )
    return order


def build_payload() -> dict[str, Any]:
    exit_status = env_int("EXIT_STATUS", 1)
    collect_import_ok = env_bool("COLLECT_IMPORT_OK")
    passed = exit_status == 0 and collect_import_ok
    resume_mode = env_bool("RESUME_MODE")
    current_stage = os.environ.get("CURRENT_STAGE", "unknown")
    stages_completed = stage_list(os.environ.get("STAGES_COMPLETED"))
    stage_order = validate_stage_state(current_stage, stages_completed, resume_mode)
    cube_cut = os.environ.get("CUBE_CUT_VERSION", "unknown")

    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "generated_for_version": cube_cut,
        "cube_cut_version": cube_cut,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "wrapper": os.environ.get("WRAPPER_REL"),
        "run_receipt_writer": WRITER_REL,
        "run_receipt_write_policy": WRITE_POLICY,
        "proof_mode": "strict-real-host-proof-default-only",
        "result": "passed" if passed else "failed",
        "exit_status": exit_status,
        "current_stage": current_stage,
        "stages_completed": stages_completed,
        "stage_order": stage_order,
        "resume_mode": resume_mode,
        "replace_requested": env_bool("REPLACE"),
        "handoff_dir": os.environ.get("HANDOFF_DIR"),
        "import_root": os.environ.get("IMPORT_ROOT"),
        "auto_handoff_dir": env_bool("AUTO_HANDOFF"),
        "keep_handoff_requested": env_bool("KEEP_HANDOFF"),
        "handoff_retention_result": os.environ.get("HANDOFF_RETENTION_RESULT"),
        "invariants": {
            "wrapper_exposes_no_non_proof_flags": True,
            "run_receipt_written_from_exit_trap": True,
            "run_receipt_records_current_stage": True,
            "run_receipt_records_handoff_retention_result": True,
            "resume_mode_skips_collection_only": True,
            "default_verifier_importer_auditor_modes_only": True,
            "run_receipt_writer_bound_by_proof_tool_contract": True,
            "run_receipt_written_with_atomic_replace": True,
            "run_receipt_refuses_symlink_destination": True,
            "run_receipt_refuses_symlink_ancestors": True,
            "run_receipt_payload_self_validated_before_write": True,
            "run_receipt_exact_key_set_enforced": True,
        },
    }


def atomic_write_text(path: Path, text: str) -> None:
    if path.name in {"", ".", ".."}:
        raise ValueError(f"invalid output file name: {path}")
    contract.require_no_existing_symlink_component(path, "run receipt output")
    path.parent.mkdir(parents=True, exist_ok=True)
    contract.require_no_existing_symlink_component(path, "run receipt output")
    if path.exists() and path.is_dir():
        raise ValueError(f"run receipt output is a directory: {path}")
    if path.is_symlink():
        raise ValueError(f"run receipt output must not be a symlink: {path}")

    tmp = path.parent / f".{path.name}.tmp.{os.getpid()}"
    fd: int | None = None
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        data = text.encode("utf-8")
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
        os.close(fd)
        fd = None
        os.replace(tmp, path)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            dir_fd = None
        if dir_fd is not None:
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        if fd is not None:
            os.close(fd)
        try:
            if tmp.exists() or tmp.is_symlink():
                tmp.unlink()
        except FileNotFoundError:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="write a strict collect/import run receipt atomically")
    parser.add_argument("output", type=Path, help="run receipt JSON output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload()
        errors = validate_run_receipt(payload)
        if errors:
            raise ValueError("run receipt payload failed self-validation: " + "; ".join(errors))
        atomic_write_text(args.output, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    except Exception as exc:  # noqa: BLE001 - operator-facing receipt writer
        print("host-proof run receipt write FAILED")
        print(f"- {exc}")
        return 1
    print(f"host-proof run receipt written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
