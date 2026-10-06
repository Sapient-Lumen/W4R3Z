#!/usr/bin/env python3
"""Guard the scarce-host real FreeBSD operator packet.

The riskiest unfinished work is not another schema family; it is getting a real
FreeBSD handoff back into the cube without manual choreography or proof-theatre
flags.  This check keeps the generated operator packet short, constant-bound,
and default-real-proof-only.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
PACKET_REL = "tools/freebsd/print_real_host_proof_operator_packet.py"
PACKET_DOC_REL = "docs/current/freebsd-real-host-proof-operator-packet.md"
SMOKE_DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
START_REL = "docs/current/start-here-now.md"
README_REL = "README.md"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def run_packet(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-S", str(ROOT / PACKET_REL), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def surface_errors() -> list[str]:
    errors: list[str] = []
    packet = ROOT / PACKET_REL
    require(errors, packet.exists(), f"missing {PACKET_REL}")
    if packet.exists():
        require(errors, bool(packet.stat().st_mode & 0o111), f"{PACKET_REL} must be executable")
        text = packet.read_text(encoding="utf-8", errors="replace")
        for token in [
            "host_proof_contract",
            "CURRENT_CUBE_CUT_VERSION",
            "SUPPORTED_FREEBSD_RELEASE_FLOOR",
            "MIN_FREEBSD_OSRELDATE",
            "PRIMARY_FREEBSD_RELEASE",
            "PRIMARY_FREEBSD_OSRELDATE_MINIMUM",
            "HOST_TARGET_MATRIX_ID",
            "HOST_TARGET_PRIMARY_TIER",
            "HOST_TARGET_LEGACY_TIER",
            "DEFAULT_IMPORT_ROOT_REL",
            "HANDOFF_REQUIRED_NAMES",
            "HANDOFF_REPLACE_ENV",
            "handoff overwrite guard",
            "collect_removable_media_local_fallback_host_proof.sh",
            "verify_removable_media_local_fallback_host_proof_handoff.py",
            "HOST_PROOF_HANDOFF_SEALER_REL",
            "HOST_PROOF_HANDOFF_UNSEALER_REL",
            "HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL",
            "import_removable_media_local_fallback_host_proof_handoff.py",
            "audit_removable_media_local_fallback_host_proof_imports.py",
            "collect_import_removable_media_local_fallback_host_proof.sh",
            "validate_collect_import_run_receipt.py",
        "report_removable_media_local_fallback_host_proof_imports.py",
        "blocked-no-real-host-proof-import",
        "--fail-if-incomplete",
            "report_removable_media_local_fallback_host_proof_imports.py",
            "IMPORT_STATUS_REPORTER_REL",
        ]:
            require(errors, token in text, f"{PACKET_REL} missing token {token!r}")
        for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
            require(errors, banned not in text, f"{PACKET_REL} must not contain non-proof flag {banned!r}")
    return errors


def output_errors() -> list[str]:
    errors: list[str] = []
    proc = run_packet()
    require(errors, proc.returncode == 0, f"packet generator should pass: {proc.stdout} {proc.stderr}")
    out = proc.stdout
    for token in [
        "DeriveBSD FreeBSD real-host proof operator packet",
        contract.CURRENT_CUBE_CUT_VERSION,
        contract.PRIMARY_FREEBSD_RELEASE,
        str(contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM),
        contract.SUPPORTED_FREEBSD_RELEASE_FLOOR,
        str(contract.MIN_FREEBSD_OSRELDATE),
        contract.HOST_TARGET_MATRIX_ID,
        contract.HOST_TARGET_PRIMARY_TIER,
        contract.HOST_TARGET_LEGACY_TIER,
        contract.DEFAULT_IMPORT_ROOT_REL,
        "Preferred cloudtainer handoff path",
        "Cloudtainer import commands",
        "Same-host one-command path",
        "Refusal boundary",
        "receipt.json",
        "bundle.json",
        "SHA256SUMS",
        "deterministic sealed handoff archive",
        "exactly the required files",
        "Do not add loose notes",
        "handoff overwrite guard",
        contract.HANDOFF_REPLACE_ENV,
        "verify_removable_media_local_fallback_host_proof_handoff.py",
        "seal_removable_media_local_fallback_host_proof_handoff.py",
        "unseal_removable_media_local_fallback_host_proof_handoff.py",
        "import_sealed_removable_media_local_fallback_host_proof_handoff.py",
        "sealed one-command importer",
        "import_removable_media_local_fallback_host_proof_handoff.py",
        "audit_removable_media_local_fallback_host_proof_imports.py",
        "check_freebsd_real_host_proof_theatre_gate.py",
        "validate_collect_import_run_receipt.py",
        "report_removable_media_local_fallback_host_proof_imports.py",
        "blocked-no-real-host-proof-import",
        "--fail-if-incomplete",
    ]:
        require(errors, token in out, f"operator packet output missing token {token!r}")
    for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
        require(errors, banned not in out, f"operator packet output must not include non-proof flag {banned!r}")
    terse = run_packet("--mode", "terse")
    require(errors, terse.returncode == 0, "terse packet mode should pass")
    require(errors, "Preferred cloudtainer handoff path" in terse.stdout, "terse packet must keep the preferred handoff path")
    return errors


def doc_errors() -> list[str]:
    errors: list[str] = []
    docs = [PACKET_DOC_REL, SMOKE_DOC_REL, START_REL, README_REL]
    for rel in docs:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in [PACKET_REL, "operator packet", "host_target_tier", "15.1-RELEASE"]:
            require(errors, token in text, f"{rel} missing operator-packet token {token!r}")
    packet_doc = (ROOT / PACKET_DOC_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        contract.DEFAULT_IMPORT_ROOT_REL,
        "receipt.json",
        "bundle.json",
        "SHA256SUMS",
        "deterministic sealed handoff archive",
        "handoff-first",
        "default-mode",
        "not an importable `real-host-proof`",
        "host_target_tier",
        "host_target_matrix_id",
        "primary-production",
        "supported-legacy-floor",
        "import_sealed_removable_media_local_fallback_host_proof_handoff.py",
        "Do not reuse a handoff directory",
        "proof status reporter",
        "blocked-no-real-host-proof-import",
    ]:
        require(errors, token in packet_doc, f"{PACKET_DOC_REL} missing packet-doc token {token!r}")
    return errors


def refactor_guard_errors() -> list[str]:
    """Keep the collect/import checker from duplicating run-receipt constants."""
    errors: list[str] = []
    rel = "tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py"
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    for token in [
        "validate_collect_import_run_receipt as run_receipt_validator",
        "run_receipt_validator.KIND",
        "run_receipt_validator.REQUIRED_TRUE_INVARIANTS",
        "run_receipt_validator.WRITE_POLICY",
    ]:
        require(errors, token in text, f"{rel} must use run receipt validator constant {token!r}")
    return errors


def main() -> int:
    errors = surface_errors() + output_errors() + doc_errors() + refactor_guard_errors()
    if errors:
        print("FreeBSD real-host operator packet check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD real-host operator packet check OK")
    print("Operator packet is constant-bound, handoff-first, and default-real-proof-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
