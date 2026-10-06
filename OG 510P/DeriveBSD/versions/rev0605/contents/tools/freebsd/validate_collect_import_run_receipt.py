#!/usr/bin/env python3
"""Validate strict collect/import run receipts.

Run receipts are recovery evidence for scarce real-host proof attempts.  This
validator keeps them small, deterministic, and mode-safe: the stage list must be
an exact prefix for the selected normal/resume path, the proof mode must remain
strict real-host proof, and successful receipts must show the full
collect/resume -> verify -> import -> audit chain.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cube_digest_lib import CanonicalJsonError, load_json_strict_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402

KIND = "removable.media.local.freebsd.host.proof.collect_import.run.receipt"
SCHEMA_VERSION = "0.1"
WRITE_POLICY = "atomic-tempfile-fsync-osreplace-symlink-destination-and-ancestor-refused"
PROOF_MODE = "strict-real-host-proof-default-only"
NORMAL_STAGE_ORDER = ["collect", "verify_handoff", "import_handoff", "audit_import_root"]
RESUME_STAGE_ORDER = ["resume_handoff", "verify_handoff", "import_handoff", "audit_import_root"]
TERMINAL_STAGES = {"initializing", "complete"}
ALL_STAGES = set(NORMAL_STAGE_ORDER) | set(RESUME_STAGE_ORDER) | TERMINAL_STAGES
REQUIRED_TOP_LEVEL_KEYS = {
    "auto_handoff_dir",
    "cube_cut_version",
    "current_stage",
    "exit_status",
    "generated_at_utc",
    "generated_for_version",
    "handoff_dir",
    "handoff_retention_result",
    "import_root",
    "invariants",
    "keep_handoff_requested",
    "kind",
    "proof_mode",
    "replace_requested",
    "result",
    "resume_mode",
    "run_receipt_write_policy",
    "run_receipt_writer",
    "schema_version",
    "stage_order",
    "stages_completed",
    "wrapper",
}
REQUIRED_TRUE_INVARIANTS = {
    "wrapper_exposes_no_non_proof_flags",
    "run_receipt_written_from_exit_trap",
    "run_receipt_records_current_stage",
    "run_receipt_records_handoff_retention_result",
    "resume_mode_skips_collection_only",
    "default_verifier_importer_auditor_modes_only",
    "run_receipt_writer_bound_by_proof_tool_contract",
    "run_receipt_written_with_atomic_replace",
    "run_receipt_refuses_symlink_destination",
    "run_receipt_refuses_symlink_ancestors",
    "run_receipt_payload_self_validated_before_write",
    "run_receipt_exact_key_set_enforced",
}
BANNED_KEYS = {"proof_status"}
ALLOWED_RETENTION_RESULTS = {
    "not-decided",
    "resume-handoff-reused",
    "preserved-by-request",
    "removed-after-success",
    "preserved-on-failure",
    "user-supplied-handoff-not-deleted",
    "no-handoff-directory-selected",
    "preserved-after-run-receipt-write-failure",
}


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _contains_banned_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key in BANNED_KEYS or _contains_banned_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_banned_key(child) for child in value)
    return False


def _iso_utc(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _expected_prefix(current_stage: str, stage_order: list[str]) -> list[str] | None:
    if current_stage == "initializing":
        return []
    if current_stage == "complete":
        return stage_order
    if current_stage in stage_order:
        return stage_order[: stage_order.index(current_stage)]
    return None


def validate_run_receipt(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed_keys = set(obj.keys())
    _require(errors, observed_keys == REQUIRED_TOP_LEVEL_KEYS, "run receipt top-level keys must match the exact supported key set")
    _require(errors, not _contains_banned_key(obj), "run receipt must not contain banned proof-claim keys such as proof_status")
    _require(errors, obj.get("kind") == KIND, "wrong collect/import run receipt kind")
    _require(errors, obj.get("schema_version") == SCHEMA_VERSION, "wrong collect/import run receipt schema_version")
    _require(errors, obj.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "run receipt generated_for_version must bind current cube cut")
    _require(errors, obj.get("cube_cut_version") == contract.CURRENT_CUBE_CUT_VERSION, "run receipt cube_cut_version must bind current cube cut")
    _require(errors, obj.get("generated_for_version") == obj.get("cube_cut_version"), "run receipt generated_for_version and cube_cut_version must agree")
    _require(errors, _iso_utc(obj.get("generated_at_utc")), "run receipt generated_at_utc must be an ISO UTC timestamp ending in Z")
    _require(errors, obj.get("wrapper") == contract.HOST_PROOF_COLLECT_IMPORT_REL, "run receipt must name the strict collect/import wrapper")
    _require(errors, obj.get("run_receipt_writer") == contract.HOST_PROOF_RUN_RECEIPT_WRITER_REL, "run receipt must name the bound writer")
    _require(errors, obj.get("run_receipt_write_policy") == WRITE_POLICY, "run receipt must name the atomic symlink-refusing write policy")
    _require(errors, obj.get("proof_mode") == PROOF_MODE, "run receipt proof_mode must remain strict real-host proof only")
    _require(errors, obj.get("result") in {"passed", "failed"}, "run receipt result must be passed or failed")
    _require(errors, isinstance(obj.get("exit_status"), int), "run receipt exit_status must be an integer")
    _require(errors, isinstance(obj.get("resume_mode"), bool), "run receipt resume_mode must be a boolean")
    _require(errors, isinstance(obj.get("replace_requested"), bool), "run receipt replace_requested must be a boolean")
    _require(errors, isinstance(obj.get("auto_handoff_dir"), bool), "run receipt auto_handoff_dir must be a boolean")
    _require(errors, isinstance(obj.get("keep_handoff_requested"), bool), "run receipt keep_handoff_requested must be a boolean")
    _require(errors, isinstance(obj.get("handoff_dir"), str) and bool(obj.get("handoff_dir")), "run receipt must record a non-empty handoff_dir")
    _require(errors, isinstance(obj.get("import_root"), str) and bool(obj.get("import_root")), "run receipt must record a non-empty import_root")
    _require(errors, obj.get("handoff_retention_result") in ALLOWED_RETENTION_RESULTS, "run receipt handoff_retention_result is not a supported value")

    resume_mode = obj.get("resume_mode") is True
    expected_order = RESUME_STAGE_ORDER if resume_mode else NORMAL_STAGE_ORDER
    stage_order = obj.get("stage_order")
    stages_completed = obj.get("stages_completed")
    current_stage = obj.get("current_stage")
    _require(errors, stage_order == expected_order, "run receipt stage_order must match normal/resume mode")
    _require(errors, isinstance(stages_completed, list) and all(isinstance(stage, str) for stage in stages_completed), "run receipt stages_completed must be a string list")
    _require(errors, isinstance(current_stage, str) and current_stage in ALL_STAGES, "run receipt current_stage must be in the supported stage vocabulary")
    if isinstance(current_stage, str) and isinstance(stages_completed, list):
        prefix = _expected_prefix(current_stage, expected_order)
        _require(errors, prefix is not None, "run receipt current_stage is invalid for its mode")
        if prefix is not None:
            _require(errors, stages_completed == prefix, "run receipt stages_completed must be the exact prefix before current_stage")
    if resume_mode:
        _require(errors, "collect" not in stages_completed if isinstance(stages_completed, list) else False, "resume run receipt must not report collect as completed")
    else:
        _require(errors, "resume_handoff" not in stages_completed if isinstance(stages_completed, list) else False, "normal run receipt must not report resume_handoff as completed")

    exit_status = obj.get("exit_status")
    if obj.get("result") == "passed":
        _require(errors, exit_status == 0, "passed run receipt must have exit_status 0")
        _require(errors, current_stage == "complete", "passed run receipt must end at complete")
        _require(errors, stages_completed == expected_order, "passed run receipt must complete every stage")
        if obj.get("auto_handoff_dir") is True and obj.get("keep_handoff_requested") is False:
            _require(errors, obj.get("handoff_retention_result") == "removed-after-success", "passed auto-handoff run must report removal unless keep was requested")
    elif obj.get("result") == "failed":
        _require(errors, isinstance(exit_status, int) and exit_status != 0, "failed run receipt must have a nonzero exit_status")
        _require(errors, current_stage != "complete", "failed run receipt must not end at complete")

    invariants = _dict(obj.get("invariants"))
    _require(errors, set(invariants.keys()) == REQUIRED_TRUE_INVARIANTS, "run receipt invariants must match the exact supported key set")
    for key in REQUIRED_TRUE_INVARIANTS:
        _require(errors, invariants.get(key) is True, f"run receipt invariant {key} must be true")
    for banned in ("allow_checker_simulation", "allow_refusal", "allow_failed", "checker_simulation"):
        _require(errors, banned not in json.dumps(obj, sort_keys=True), f"run receipt must not contain non-proof token {banned!r}")
    return errors


def _load(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="validate a strict collect/import run receipt")
    parser.add_argument("receipt", type=Path, help="run receipt JSON to validate")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        obj = _load(args.receipt)
    except (OSError, CanonicalJsonError) as exc:
        print(f"collect/import run receipt validation FAILED: {exc}", file=sys.stderr)
        return 1
    if not isinstance(obj, dict):
        print("collect/import run receipt validation FAILED: root must be a JSON object", file=sys.stderr)
        return 1
    errors = validate_run_receipt(obj)
    if errors:
        print("collect/import run receipt validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("collect/import run receipt validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
