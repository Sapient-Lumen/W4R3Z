#!/usr/bin/env python3
"""Validate an importable FreeBSD removable-media host-proof bundle.

Default mode is strict real-proof mode.  It accepts only a real-host-proof bundle,
verifies the original receipt byte/canonical digests, re-runs the host-smoke
receipt validator in its default non-simulation mode, and checks that the bundle
binds the current collector/runner/validator/finalizer/worker tool digests.

The ``--allow-checker-simulation`` flag exists only for checked-in examples and
Linux release-critical checks; it must not be used for release host proof.
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

from cube_digest_lib import CanonicalJsonError, canonical_digest, load_json_strict_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import validate_removable_media_local_fallback_host_smoke_receipt as host_validator  # noqa: E402

KIND = contract.BUNDLE_KIND
SCHEMA_VERSION = contract.BUNDLE_SCHEMA_VERSION
CURRENT_CUBE_CUT_VERSION = contract.CURRENT_CUBE_CUT_VERSION
RUNNER_CONTRACT_VERSION = contract.RUNNER_CONTRACT_VERSION
MIN_FREEBSD_OSRELDATE = contract.MIN_FREEBSD_OSRELDATE
HOST_TARGET_MATRIX_ID = contract.HOST_TARGET_MATRIX_ID
HOST_TARGET_PRIMARY_TIER = contract.HOST_TARGET_PRIMARY_TIER
HOST_TARGET_LEGACY_TIER = contract.HOST_TARGET_LEGACY_TIER
SUPPORTED_HOST_TARGET_TIERS = {HOST_TARGET_PRIMARY_TIER, HOST_TARGET_LEGACY_TIER}
REQUIRED_TOOL_PATHS = contract.REQUIRED_PROOF_TOOL_PATH_SET
REQUIRED_TRUE_INVARIANTS = {
    "receipt_result_passed",
    "refusal_and_failed_receipts_not_bundle_inputs",
    "host_probe_observed_freebsd",
    "host_probe_observed_root_uid",
    "host_probe_capsicum_features_enabled",
    "host_target_tier_recorded",
    "worker_launched_after_detach",
    "worker_reported_capsicum_mode",
    "worker_input_digest_matches_capture_digest",
    "bundle_binds_tool_digests",
    "receipt_canonical_digest_recomputed_by_finalizer",
    "receipt_runner_contract_version_matches_generated_for_version",
    "bundle_cube_cut_version_not_runner_contract_version",
}


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _list(obj: Any) -> list[Any]:
    return obj if isinstance(obj, list) else []


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _load_path(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def _resolve_receipt_path(bundle: dict[str, Any], bundle_path: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    receipt_path = _dict(bundle.get("receipt")).get("path")
    if not isinstance(receipt_path, str) or not receipt_path:
        raise ValueError("bundle receipt.path must be present when --receipt is omitted")
    candidate = Path(receipt_path)
    if candidate.is_absolute():
        return candidate
    repo_candidate = ROOT / candidate
    if repo_candidate.exists():
        return repo_candidate
    return bundle_path.parent / candidate


def _tool_errors(bundle: dict[str, Any], *, allow_current_tool_drift: bool) -> list[str]:
    errors: list[str] = []
    rows = _list(bundle.get("tools"))
    paths = [row.get("path") for row in rows if isinstance(row, dict)]
    duplicate_paths = sorted({path for path in paths if paths.count(path) > 1})
    _require(errors, not duplicate_paths, f"proof bundle has duplicate tool digest rows: {duplicate_paths!r}")
    by_path = {row.get("path"): row for row in rows if isinstance(row, dict)}
    missing = sorted(REQUIRED_TOOL_PATHS - set(by_path))
    unexpected = sorted(path for path in set(by_path) - REQUIRED_TOOL_PATHS if isinstance(path, str))
    _require(errors, not missing, f"proof bundle is missing required tool digest rows: {missing!r}")
    _require(errors, not unexpected, f"proof bundle has unexpected tool digest rows: {unexpected!r}")
    _require(errors, len(rows) == len(REQUIRED_TOOL_PATHS), f"proof bundle must bind exactly {len(REQUIRED_TOOL_PATHS)} tool digest rows")
    for rel, row in sorted(by_path.items()):
        if not isinstance(rel, str):
            errors.append("tool row path must be a string")
            continue
        if not rel.startswith("tools/freebsd/"):
            errors.append(f"tool row must stay under tools/freebsd/: {rel}")
            continue
        digest = row.get("sha256")
        _require(errors, isinstance(digest, str) and digest.startswith("sha256:"), f"tool {rel} must carry sha256")
        path = ROOT / rel
        if not path.exists():
            errors.append(f"tool {rel} does not exist in this cube")
            continue
        expected_digest = sha256_bytes(path.read_bytes())
        if not allow_current_tool_drift:
            _require(errors, digest == expected_digest, f"tool {rel} digest drifted: bundle {digest} != current {expected_digest}")
        executable = bool(path.stat().st_mode & 0o111)
        _require(errors, row.get("executable") is executable, f"tool {rel} executable bit summary is stale")
    return errors


def _receipt_errors(
    bundle: dict[str, Any],
    bundle_path: Path,
    *,
    explicit_receipt: Path | None,
    allow_checker_simulation: bool,
) -> list[str]:
    errors: list[str] = []
    summary = _dict(bundle.get("receipt"))
    try:
        receipt_path = _resolve_receipt_path(bundle, bundle_path, explicit_receipt)
    except ValueError as exc:
        return [str(exc)]
    if not receipt_path.exists():
        return [f"receipt file does not exist: {receipt_path}"]
    receipt_text = receipt_path.read_text(encoding="utf-8")
    try:
        receipt = load_json_strict_text(receipt_text)
    except CanonicalJsonError as exc:
        return [f"receipt JSON rejected by strict parser: {exc}"]
    if not isinstance(receipt, dict):
        return ["receipt root must be a JSON object"]

    _require(errors, summary.get("byte_sha256") == sha256_bytes(receipt_text.encode("utf-8")), "bundle receipt.byte_sha256 must match original receipt bytes")
    _require(errors, summary.get("canonical_sha256") == canonical_digest(receipt), "bundle receipt.canonical_sha256 must match original receipt canonical digest")

    validator_errors = host_validator.validate_receipt(
        receipt,
        allow_refusal=False,
        allow_failed=False,
        allow_checker_simulation=allow_checker_simulation,
    )
    for err in validator_errors[:10]:
        errors.append(f"original receipt rejected by host-smoke validator: {err}")
    if len(validator_errors) > 10:
        errors.append(f"original receipt had {len(validator_errors) - 10} additional validator errors")

    host = _dict(receipt.get("host"))
    host_smoke = _dict(receipt.get("host_smoke"))
    sim = _dict(receipt.get("simulation"))
    _require(errors, summary.get("kind") == receipt.get("kind"), "receipt kind summary must match original receipt")
    _require(errors, summary.get("schema_version") == receipt.get("schema_version"), "receipt schema_version summary must match original receipt")
    _require(errors, summary.get("smoke_id") == receipt.get("smoke_id"), "receipt smoke_id summary must match original receipt")
    _require(errors, summary.get("generated_for_version") == receipt.get("generated_for_version"), "receipt generated_for_version summary must match original receipt")
    _require(errors, summary.get("runner_contract_version") == receipt.get("runner_contract_version"), "receipt runner_contract_version summary must match original receipt")
    _require(errors, summary.get("cube_cut_version") == receipt.get("cube_cut_version"), "receipt cube_cut_version summary must match original receipt")
    _require(errors, summary.get("generated_at_utc") == receipt.get("generated_at_utc"), "receipt generated_at_utc summary must match original receipt")
    _require(errors, summary.get("result") == receipt.get("result"), "receipt result summary must match original receipt")
    _require(errors, summary.get("checker_only_host_command_simulation") == sim.get("checker_only_host_command_simulation"), "receipt simulation summary must match original receipt")
    _require(errors, summary.get("observed_system") == host.get("observed_system"), "receipt observed_system summary must match original receipt")
    for key in [
        "host_probe_observed_system",
        "host_probe_uname_release",
        "host_probe_uname_machine",
        "host_probe_effective_uid",
        "host_probe_osreldate",
        "host_target_tier",
        "host_probe_capsicum_capability_mode",
        "host_probe_capsicum_capabilities",
    ]:
        _require(errors, summary.get(key) == host.get(key), f"receipt {key} summary must match original receipt")
    _require(errors, summary.get("host_target_matrix_id") == host_smoke.get("host_target_matrix_id"), "receipt host_target_matrix_id summary must match original receipt")
    _require(errors, summary.get("capture_digest") == host_smoke.get("capture_digest"), "receipt capture_digest summary must match original receipt")
    _require(errors, summary.get("worker_binary_sha256") == host_smoke.get("worker_binary_sha256"), "receipt worker_binary_sha256 summary must match original receipt")
    return errors


def validate_bundle(
    bundle: dict[str, Any],
    bundle_path: Path,
    *,
    receipt_path: Path | None = None,
    allow_checker_simulation: bool = False,
    allow_current_tool_drift: bool = False,
) -> list[str]:
    errors: list[str] = []
    _require(errors, bundle.get("kind") == KIND, "wrong proof-bundle kind")
    _require(errors, bundle.get("schema_version") == SCHEMA_VERSION, "wrong proof-bundle schema_version")
    _require(errors, bundle.get("generated_for_version") == CURRENT_CUBE_CUT_VERSION, "proof bundle generated_for_version must identify the current cube cut")
    _require(errors, bundle.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "proof bundle cube_cut_version must identify the current cube cut")
    _require(errors, bundle.get("cube_cut_version") == bundle.get("generated_for_version"), "proof bundle generated_for_version and cube_cut_version must agree")
    status = bundle.get("proof_status")
    _require(errors, status in {"real-host-proof", "checker-simulation-non-proof"}, "proof_status must be real-host-proof or checker-simulation-non-proof")
    if not allow_checker_simulation:
        _require(errors, status == "real-host-proof", "default mode accepts only real-host-proof bundles")
    receipt = _dict(bundle.get("receipt"))
    invariants = _dict(bundle.get("invariants"))
    for key in REQUIRED_TRUE_INVARIANTS:
        _require(errors, invariants.get(key) is True, f"invariant {key} must be true")
    if status == "real-host-proof":
        _require(errors, invariants.get("default_validator_mode_required_for_real_proof") is True, "real proof must require default validator mode")
        _require(errors, invariants.get("real_proof_requires_non_simulated_receipt") is True, "real proof must require non-simulated receipt")
        _require(errors, receipt.get("checker_only_host_command_simulation") is False, "real proof summary must not be checker simulation")
        _require(errors, receipt.get("observed_system") == "FreeBSD", "real proof summary must observe FreeBSD")
        _require(errors, receipt.get("host_probe_observed_system") == "FreeBSD", "real proof host probe must observe FreeBSD")
        _require(errors, receipt.get("host_probe_effective_uid") == "0", "real proof host probe must observe uid 0")
        if isinstance(receipt.get("host_probe_osreldate"), str) and receipt.get("host_probe_osreldate", "").isdigit():
            _require(errors, int(receipt.get("host_probe_osreldate")) >= MIN_FREEBSD_OSRELDATE, "real proof host probe must meet the supported FreeBSD release floor")
        else:
            errors.append("real proof host probe must carry numeric kern.osreldate")
        _require(errors, receipt.get("host_probe_capsicum_capability_mode") == "1", "real proof must observe Capsicum capability mode feature")
        _require(errors, receipt.get("host_probe_capsicum_capabilities") == "1", "real proof must observe Capsicum capabilities feature")
        _require(errors, receipt.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "real proof must record the host target matrix id")
        _require(errors, receipt.get("host_target_tier") in SUPPORTED_HOST_TARGET_TIERS, "real proof must record a supported host target tier")
        _require(errors, receipt.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "real proof summary must identify the runner contract version")
        _require(errors, receipt.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "real proof summary must identify the emitting cube cut")
    elif status == "checker-simulation-non-proof":
        _require(errors, invariants.get("checker_simulation_explicitly_non_proof") is True, "checker simulation must be explicit non-proof")
        _require(errors, invariants.get("default_validator_mode_required_for_real_proof") is False, "checker simulation must show default real-proof mode was not used")
        _require(errors, receipt.get("checker_only_host_command_simulation") is True, "checker simulation summary must mark checker-only receipt")
        _require(errors, receipt.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "checker simulation summary must record the host target matrix id")
        _require(errors, receipt.get("host_target_tier") in SUPPORTED_HOST_TARGET_TIERS, "checker simulation summary must record a supported host target tier")
        _require(errors, receipt.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "checker simulation summary must identify the runner contract version")
        _require(errors, receipt.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "checker simulation summary must identify the emitting cube cut")
    errors.extend(_receipt_errors(bundle, bundle_path, explicit_receipt=receipt_path, allow_checker_simulation=allow_checker_simulation))
    errors.extend(_tool_errors(bundle, allow_current_tool_drift=allow_current_tool_drift))
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path, help="host-proof bundle JSON to validate")
    parser.add_argument("--receipt", type=Path, help="original host-smoke receipt JSON; defaults to bundle receipt.path")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="accept the checked non-proof simulation bundle")
    parser.add_argument("--allow-current-tool-drift", action="store_true", help="do not compare tool digests against the current checkout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        bundle = _load_path(args.bundle)
    except (OSError, CanonicalJsonError) as exc:
        print(f"host-proof bundle validation FAILED: {exc}", file=sys.stderr)
        return 1
    if not isinstance(bundle, dict):
        print("host-proof bundle validation FAILED: bundle root must be a JSON object", file=sys.stderr)
        return 1
    errors = validate_bundle(
        bundle,
        args.bundle,
        receipt_path=args.receipt,
        allow_checker_simulation=args.allow_checker_simulation,
        allow_current_tool_drift=args.allow_current_tool_drift,
    )
    if errors:
        print("host-proof bundle validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("host-proof bundle validation OK")
    print(f"bundle_canonical_sha256:{canonical_digest(bundle)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
