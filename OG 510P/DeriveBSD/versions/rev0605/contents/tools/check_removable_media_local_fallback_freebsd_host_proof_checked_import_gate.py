#!/usr/bin/env python3
"""Audit the live checked-in FreeBSD host-proof import root.

rev0546 added an import-root auditor, but release-critical still only exercised
that auditor on temporary test roots.  This guard wires the live cube location
(`validation/freebsd-host-proof-imports`) into release validation so future
checked-in real host proof cannot silently go stale, become a symlink, or retain
checker-simulation imports.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
FREEBSD_TOOLS = TOOLS / "freebsd"
for path in [TOOLS, FREEBSD_TOOLS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import audit_removable_media_local_fallback_host_proof_imports as import_auditor  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import report_removable_media_local_fallback_host_proof_imports as import_reporter  # noqa: E402

DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
START_REL = "docs/current/start-here-now.md"
HYGIENE_REL = "docs/current/hygiene-run-ledger.md"
REPORTER_REL = "tools/freebsd/report_removable_media_local_fallback_host_proof_imports.py"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def live_import_root_errors() -> list[str]:
    import_root = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
    if not import_root.exists():
        return [f"live checked-in import root does not exist: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    if import_root.is_symlink():
        return [f"live checked-in import root must not be a symlink: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    if not import_root.is_dir():
        return [f"live checked-in import root is not a directory: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    return import_auditor.audit_import_root(import_root, allow_checker_simulation=False, require_primary_target=True)


def surface_errors() -> list[str]:
    errors: list[str] = []
    reporter = ROOT / REPORTER_REL
    require(errors, reporter.exists(), f"missing {REPORTER_REL}")
    if reporter.exists():
        reporter_text = reporter.read_text(encoding="utf-8", errors="replace")
        for token in [
            "summarize_import_root",
            "STATUS_BLOCKED_EMPTY",
            "STATUS_COMPLETE_PRIMARY",
            "--fail-if-incomplete",
            "primary_production_real_host_proof",
            "blocked-no-real-host-proof-import",
        ]:
            require(errors, token in reporter_text, f"{REPORTER_REL} missing proof-status reporter token {token!r}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "DEFAULT_IMPORT_ROOT_REL",
        contract.DEFAULT_IMPORT_ROOT_REL,
        "IMPORT_RECEIPT_KIND",
        "IMPORT_RECEIPT_SCHEMA_VERSION",
        "HOST_TARGET_PRIMARY_TIER",
    ]:
        require(errors, token in contract_text, f"host proof contract missing shared import-root/import-receipt token {token!r}")
    for rel in [
        "tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py",
        "tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        require(errors, "contract.DEFAULT_IMPORT_ROOT_REL" in text, f"{rel} must use shared default import-root constant")
        require(errors, "contract.IMPORT_RECEIPT_KIND" in text, f"{rel} must use shared import receipt kind")
        require(errors, "contract.IMPORT_RECEIPT_SCHEMA_VERSION" in text, f"{rel} must use shared import receipt schema version")
        if rel.endswith("audit_removable_media_local_fallback_host_proof_imports.py"):
            require(errors, "--require-primary-target" in text, f"{rel} must expose checked-in primary-target audit flag")
    for rel in [DOC_REL, START_REL, HYGIENE_REL]:
        doc = ROOT / rel
        require(errors, doc.exists(), f"missing {rel}")
        if doc.exists():
            text = doc.read_text(encoding="utf-8", errors="replace")
            for token in [
                contract.DEFAULT_IMPORT_ROOT_REL,
                "live checked-in import root",
                "default audit accepts only `real-host-proof`",
                "primary-production target tier",
                "proof status",
                "blocked-no-real-host-proof-import",
            ]:
                require(errors, token in text, f"{rel} missing checked-import gate token {token!r}")
    return errors


def main() -> int:
    errors = [f"{contract.DEFAULT_IMPORT_ROOT_REL}: {err}" for err in live_import_root_errors()]
    errors.extend(surface_errors())
    status_report = import_reporter.summarize_import_root(ROOT / contract.DEFAULT_IMPORT_ROOT_REL)
    if status_report.get("import_root_state") != "present":
        errors.append(f"{contract.DEFAULT_IMPORT_ROOT_REL}: proof status reporter did not observe a present import root")
    if errors:
        print("FreeBSD checked host-proof import-root gate FAILED.")
        for error in errors:
            print("-", error)
        return 1
    counts = status_report.get("counts", {}) if isinstance(status_report.get("counts"), dict) else {}
    print("FreeBSD checked host-proof import-root gate OK")
    print(f"Live checked-in import root audited in default strict primary-target mode: {contract.DEFAULT_IMPORT_ROOT_REL}")
    print(
        "proof_status="
        f"{status_report.get('status')} "
        f"proof_complete={str(status_report.get('proof_complete')).lower()} "
        f"primary_production_real_host_proof={counts.get('primary_production_real_host_proof', 0)} "
        f"real_host_proof={counts.get('real_host_proof', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
