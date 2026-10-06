#!/usr/bin/env python3
"""Validate the FreeBSD host-smoke proof bundle finalizer.

This keeps the future real-host receipt from becoming a loose JSON blob: the
operator collector must validate the receipt in default real-proof mode, finalize
it into a digest-bound bundle, and refuse checker-only simulations unless the
checker explicitly requests non-proof example mode.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import load_json, write_pretty_json
from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
FINALIZER_REL = "tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py"
BUNDLE_VALIDATOR_REL = "tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py"
COLLECTOR_REL = "tools/freebsd/collect_removable_media_local_fallback_host_proof.sh"
SCHEMA_REL = "spec/removable.media.local.freebsd.host.proof.bundle.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.freebsd.host.proof.bundle.json"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
REFUSAL_REL = "validation/removable-media-local-freebsd-host-smoke.refusal.json"
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
GENERATED_AT = "2026-06-12T23:00:00Z"
CURRENT_CUBE_CUT_VERSION = contract.CURRENT_CUBE_CUT_VERSION
RUNNER_CONTRACT_VERSION = contract.RUNNER_CONTRACT_VERSION
REQUIRED_TOOL_PATHS = contract.REQUIRED_PROOF_TOOL_PATH_SET
HOST_TARGET_PRIMARY_TIER = contract.HOST_TARGET_PRIMARY_TIER


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def run_finalizer(args: list[str], output: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-B", "-S", FINALIZER_REL, *args]
    if output is not None:
        cmd.extend(["--output", str(output)])
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def run_bundle_validator(args: list[str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-B", "-S", BUNDLE_VALIDATOR_REL, *args]
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def schema_errors(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA_REL)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.proof.bundle", "wrong proof-bundle kind")
    require(errors, obj.get("proof_status") == "checker-simulation-non-proof", "checked example must remain explicit non-proof")
    require(errors, obj.get("generated_for_version") == CURRENT_CUBE_CUT_VERSION, "checked example must identify current cube cut")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "checked example cube_cut_version must identify current cube cut")
    receipt = obj.get("receipt", {}) if isinstance(obj.get("receipt"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    tools = obj.get("tools", []) if isinstance(obj.get("tools"), list) else []
    require(errors, receipt.get("result") == "passed", "bundle may only summarize a passed host-smoke receipt")
    require(errors, receipt.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "bundle receipt summary must identify the runner contract version")
    require(errors, receipt.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "bundle receipt legacy generated_for_version must remain runner-contract alias")
    require(errors, receipt.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "bundle receipt summary must identify current cube cut")
    require(errors, receipt.get("checker_only_host_command_simulation") is True, "checked example must identify checker-only receipt")
    require(errors, receipt.get("host_probe_observed_system") == "FreeBSD", "bundle must carry uname -s host probe summary")
    require(errors, receipt.get("host_probe_effective_uid") == "0", "bundle must carry root uid host probe summary")
    require(errors, receipt.get("host_probe_capsicum_capability_mode") == "1", "bundle must carry Capsicum capability-mode sysctl summary")
    require(errors, receipt.get("host_probe_capsicum_capabilities") == "1", "bundle must carry Capsicum capabilities sysctl summary")
    require(errors, receipt.get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID, "bundle must record the host target matrix id for the checked simulation")
    require(errors, receipt.get("host_target_tier") == HOST_TARGET_PRIMARY_TIER, "bundle must record the primary production host target tier for the checked simulation")
    for key in [
        "checker_simulation_explicitly_non_proof",
        "receipt_result_passed",
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
    ]:
        require(errors, inv.get(key) is True, f"invariant {key} must be true")
    require(errors, inv.get("default_validator_mode_required_for_real_proof") is False, "non-proof example must show default real-proof mode was not used")
    tool_paths = [row.get("path") for row in tools if isinstance(row, dict)]
    require(errors, set(tool_paths) == REQUIRED_TOOL_PATHS, "bundle must bind exactly the shared FreeBSD proof-tool contract digest set")
    require(errors, len(tool_paths) == len(REQUIRED_TOOL_PATHS), "bundle must not duplicate tool digest rows")
    for row in tools:
        if isinstance(row, dict):
            require(errors, isinstance(row.get("sha256"), str) and row["sha256"].startswith("sha256:"), f"tool {row.get('path')} must carry sha256")
    return errors


def finalizer_mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        default_success = run_finalizer([SUCCESS_SIM_REL, "--generated-at", GENERATED_AT], tmp / "default-success.json")
        require(errors, default_success.returncode != 0, "default finalizer must reject checker-only success simulation")
        default_refusal = run_finalizer([REFUSAL_REL, "--generated-at", GENERATED_AT], tmp / "refusal.json")
        require(errors, default_refusal.returncode != 0, "default finalizer must reject cloudtainer refusal receipt")
        example_out = tmp / "example.json"
        allowed = run_finalizer([SUCCESS_SIM_REL, "--allow-checker-simulation", "--generated-at", GENERATED_AT], example_out)
        require(errors, allowed.returncode == 0, f"allow-checker-simulation finalizer should pass: {allowed.stdout} {allowed.stderr}")
        if allowed.returncode == 0:
            observed = load_json(ROOT, EXAMPLE_REL)
            generated = load_json(tmp, "example.json")
            require(errors, generated == observed, "checked proof-bundle example must be regenerated by finalizer")
            default_validator = run_bundle_validator([str(example_out)])
            require(errors, default_validator.returncode != 0, "default proof-bundle validator must reject checker-simulation bundle")
            allowed_validator = run_bundle_validator([str(example_out), "--allow-checker-simulation"])
            require(errors, allowed_validator.returncode == 0, f"proof-bundle validator should accept explicit checker simulation: {allowed_validator.stdout} {allowed_validator.stderr}")
            tampered = tmp / "tampered-byte-digest.json"
            generated["receipt"]["byte_sha256"] = "sha256:" + "0" * 64
            write_pretty_json(tampered, generated)
            tampered_validator = run_bundle_validator([str(tampered), "--allow-checker-simulation"])
            require(errors, tampered_validator.returncode != 0, "proof-bundle validator must reject tampered receipt byte digest")

            version_tampered = load_json(tmp, "example.json")
            version_tampered["receipt"]["cube_cut_version"] = version_tampered["receipt"].get("runner_contract_version")
            version_tampered_path = tmp / "tampered-version-confusion.json"
            write_pretty_json(version_tampered_path, version_tampered)
            version_tampered_validator = run_bundle_validator([str(version_tampered_path), "--allow-checker-simulation", "--allow-current-tool-drift"])
            require(errors, version_tampered_validator.returncode != 0, "proof-bundle validator must reject receipt cube cut / runner contract confusion")

            duplicate_tool = load_json(tmp, "example.json")
            duplicate_tool["tools"].append(dict(duplicate_tool["tools"][0]))
            duplicate_path = tmp / "duplicate-tool-row.json"
            write_pretty_json(duplicate_path, duplicate_tool)
            duplicate_validator = run_bundle_validator([str(duplicate_path), "--allow-checker-simulation"])
            require(errors, duplicate_validator.returncode != 0, "proof-bundle validator must reject duplicate tool digest rows")

            unexpected_tool = load_json(tmp, "example.json")
            unexpected_tool["tools"] = unexpected_tool["tools"][:-1] + [{
                "path": "tools/freebsd/unexpected-proof-helper.py",
                "sha256": "sha256:" + "1" * 64,
                "executable": True,
            }]
            unexpected_path = tmp / "unexpected-tool-row.json"
            write_pretty_json(unexpected_path, unexpected_tool)
            unexpected_validator = run_bundle_validator([str(unexpected_path), "--allow-checker-simulation", "--allow-current-tool-drift"])
            require(errors, unexpected_validator.returncode != 0, "proof-bundle validator must reject unexpected tool digest rows")
    return errors


def collector_doc_errors() -> list[str]:
    errors: list[str] = []
    collector = (ROOT / COLLECTOR_REL).read_text(encoding="utf-8", errors="replace")
    for token in [FINALIZER_REL, BUNDLE_VALIDATOR_REL, "bundle_sha256", "receipt_sha256", "--generated-at"]:
        require(errors, token in collector, f"collector missing finalizer token {token!r}")
    doc = (ROOT / DOC_REL).read_text(encoding="utf-8", errors="replace")
    for token in [FINALIZER_REL, BUNDLE_VALIDATOR_REL, "proof_status", "checker-simulation-non-proof", "real-host-proof", "host_target_tier", "host_target_matrix_id", f"exactly {len(REQUIRED_TOOL_PATHS)} tool digest rows", "runner_contract_version", "cube_cut_version"]:
        require(errors, token in doc, f"{DOC_REL} missing proof-bundle token {token!r}")
    return errors


def stale_tool_count_errors() -> list[str]:
    """Reject stale prose counts for the live FreeBSD proof-tool digest set.

    Earlier cuts left old `exactly 12 tool digest rows` claims beside the
    current count, so a contains-token doc check stayed green while misleading
    the scarce-host operator.  Scan current operator-facing surfaces for any
    exact proof-tool row count and require it to match the shared contract.
    """
    errors: list[str] = []
    expected = len(REQUIRED_TOOL_PATHS)
    count_re = re.compile(r"exactly (?P<count>[0-9]+|twelve|thirteen|fourteen|fifteen|sixteen)(?: FreeBSD)? proof-tool(?: digest)? rows|exactly (?P<count2>[0-9]+|twelve|thirteen|fourteen|fifteen|sixteen) tool digest rows")
    words = {"twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16}
    for rel in [DOC_REL, "docs/current/start-here-now.md", "docs/current/freebsd-real-host-proof-operator-packet.md"]:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in count_re.finditer(text):
            raw = match.group("count") or match.group("count2")
            observed = words.get(raw, int(raw) if raw.isdigit() else -1)
            require(errors, observed == expected, f"{rel} has stale proof-tool digest row count {raw!r}; expected {expected}")
    return errors


def main() -> int:
    obj = load_json(ROOT, EXAMPLE_REL)
    errors = schema_errors(obj) + semantic_errors(obj) + finalizer_mode_errors() + collector_doc_errors() + stale_tool_count_errors()
    if errors:
        print("FreeBSD host proof bundle check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof bundle check OK")
    print("Default finalizer/validator reject non-proof simulations; explicit checker mode regenerates and validates the non-proof example")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
