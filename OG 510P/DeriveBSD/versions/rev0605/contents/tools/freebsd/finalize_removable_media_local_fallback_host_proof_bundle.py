#!/usr/bin/env python3
"""Finalize a validated FreeBSD host-smoke receipt into an importable proof bundle.

Default mode is strict real-proof mode.  It accepts only a non-simulated passed
receipt that the host-smoke validator accepts with no non-proof flags.  The
``--allow-checker-simulation`` flag exists only so the Linux checker can build a
non-proof bundle example from the checked-in success simulation; operators should
not use it for release evidence.
"""
from __future__ import annotations

import argparse
import hashlib
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

from cube_digest_lib import canonical_digest, load_json_strict_text, write_pretty_json  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import validate_removable_media_local_fallback_host_smoke_receipt as host_validator  # noqa: E402

BUNDLE_KIND = contract.BUNDLE_KIND
SCHEMA_VERSION = contract.BUNDLE_SCHEMA_VERSION
GENERATED_FOR_VERSION = contract.CURRENT_CUBE_CUT_VERSION
CUBE_CUT_VERSION = contract.CURRENT_CUBE_CUT_VERSION
BUNDLE_ID = contract.BUNDLE_ID
DEFAULT_OUTPUT = ROOT / "validation" / "removable-media-local-freebsd-host-proof.bundle.json"
DEFAULT_GENERATED_AT = "2026-06-12T23:00:00Z"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def repo_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _bool(value: Any) -> bool:
    return value is True


def build_bundle(receipt_path: Path, *, generated_at_utc: str, allow_checker_simulation: bool = False) -> dict[str, Any]:
    receipt_text = receipt_path.read_text(encoding="utf-8")
    receipt = load_json_strict_text(receipt_text)
    if not isinstance(receipt, dict):
        raise ValueError("receipt root must be a JSON object")

    errors = host_validator.validate_receipt(
        receipt,
        allow_refusal=False,
        allow_failed=False,
        allow_checker_simulation=allow_checker_simulation,
    )
    if errors:
        raise ValueError("host-smoke receipt is not acceptable for this bundle: " + "; ".join(errors[:10]))

    simulation = _dict(receipt.get("simulation"))
    host = _dict(receipt.get("host"))
    host_smoke = _dict(receipt.get("host_smoke"))
    worker = _dict(host_smoke.get("worker"))
    report = _dict(worker.get("output_report"))
    checker_sim = _bool(simulation.get("checker_only_host_command_simulation"))
    proof_status = "checker-simulation-non-proof" if checker_sim else "real-host-proof"
    if checker_sim and not allow_checker_simulation:
        raise ValueError("checker-only simulation cannot be finalized as real host proof")
    if not checker_sim and allow_checker_simulation:
        proof_status = "real-host-proof"

    tool_paths = list(contract.REQUIRED_PROOF_TOOL_PATHS)
    tools = [
        {
            "path": rel,
            "sha256": sha256_file(ROOT / rel),
            "executable": bool((ROOT / rel).stat().st_mode & 0o111),
        }
        for rel in tool_paths
    ]

    invariants = {
        "default_validator_mode_required_for_real_proof": not allow_checker_simulation,
        "receipt_result_passed": receipt.get("result") == "passed",
        "refusal_and_failed_receipts_not_bundle_inputs": receipt.get("refusal_reason") is None and receipt.get("failure") is None,
        "checker_simulation_explicitly_non_proof": checker_sim == (proof_status == "checker-simulation-non-proof"),
        "real_proof_requires_non_simulated_receipt": (not checker_sim) if proof_status == "real-host-proof" else True,
        "host_probe_observed_freebsd": host.get("host_probe_observed_system") == "FreeBSD",
        "host_probe_observed_root_uid": host.get("host_probe_effective_uid") == "0",
        "host_probe_capsicum_features_enabled": host.get("host_probe_capsicum_capability_mode") == "1" and host.get("host_probe_capsicum_capabilities") == "1",
        "host_target_tier_recorded": host.get("host_target_tier") in {contract.HOST_TARGET_PRIMARY_TIER, contract.HOST_TARGET_LEGACY_TIER},
        "worker_launched_after_detach": host_smoke.get("worker_launched") is True and host_smoke.get("umounted_before_worker") is True and host_smoke.get("mdconfig_detached_before_worker") is True,
        "worker_reported_capsicum_mode": report.get("capsicum_mode_entered") is True,
        "worker_input_digest_matches_capture_digest": report.get("input_sha256") == host_smoke.get("capture_digest"),
        "bundle_binds_tool_digests": all(str(row.get("sha256", "")).startswith("sha256:") for row in tools),
        "receipt_canonical_digest_recomputed_by_finalizer": True,
        "receipt_runner_contract_version_matches_generated_for_version": receipt.get("runner_contract_version") == receipt.get("generated_for_version"),
        "bundle_cube_cut_version_not_runner_contract_version": CUBE_CUT_VERSION != receipt.get("runner_contract_version"),
    }

    return {
        "kind": BUNDLE_KIND,
        "schema_version": SCHEMA_VERSION,
        "bundle_id": BUNDLE_ID,
        "generated_for_version": GENERATED_FOR_VERSION,
        "cube_cut_version": CUBE_CUT_VERSION,
        "generated_at_utc": generated_at_utc,
        "proof_status": proof_status,
        "receipt": {
            "path": repo_label(receipt_path),
            "byte_sha256": sha256_bytes(receipt_text.encode("utf-8")),
            "canonical_sha256": canonical_digest(receipt),
            "kind": receipt.get("kind"),
            "schema_version": receipt.get("schema_version"),
            "smoke_id": receipt.get("smoke_id"),
            "generated_for_version": receipt.get("generated_for_version"),
            "runner_contract_version": receipt.get("runner_contract_version"),
            "cube_cut_version": receipt.get("cube_cut_version"),
            "generated_at_utc": receipt.get("generated_at_utc"),
            "result": receipt.get("result"),
            "checker_only_host_command_simulation": checker_sim,
            "observed_system": host.get("observed_system"),
            "host_probe_observed_system": host.get("host_probe_observed_system"),
            "host_probe_uname_release": host.get("host_probe_uname_release"),
            "host_probe_uname_machine": host.get("host_probe_uname_machine"),
            "host_probe_effective_uid": host.get("host_probe_effective_uid"),
            "host_probe_osreldate": host.get("host_probe_osreldate"),
            "host_target_matrix_id": host_smoke.get("host_target_matrix_id"),
            "host_target_tier": host.get("host_target_tier"),
            "host_probe_capsicum_capability_mode": host.get("host_probe_capsicum_capability_mode"),
            "host_probe_capsicum_capabilities": host.get("host_probe_capsicum_capabilities"),
            "capture_digest": host_smoke.get("capture_digest"),
            "worker_binary_sha256": host_smoke.get("worker_binary_sha256"),
        },
        "tools": tools,
        "invariants": invariants,
        "operator_next_step": "attach-this-bundle-plus-original-receipt-to-the-session-review-only-when-proof_status-is-real-host-proof",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path, help="host-smoke receipt JSON to finalize")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="bundle JSON output path")
    parser.add_argument("--generated-at", default=DEFAULT_GENERATED_AT, help="UTC timestamp for deterministic checked examples")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="write a checker-simulation non-proof bundle for tests/examples only")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        bundle = build_bundle(
            args.receipt,
            generated_at_utc=args.generated_at,
            allow_checker_simulation=args.allow_checker_simulation,
        )
        write_pretty_json(args.output, bundle)
    except Exception as exc:  # noqa: BLE001 - operator-facing proof finalizer
        print("FreeBSD host-proof bundle finalization FAILED")
        print(f"- {exc}")
        return 1
    print(f"FreeBSD host-proof bundle written: {args.output}")
    print(f"proof_status={bundle['proof_status']}")
    print(f"receipt_canonical_sha256={bundle['receipt']['canonical_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
