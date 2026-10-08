#!/usr/bin/env python3
"""Validate rev0850 rights-ledger/root-rights symlink boundary hardening."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publication_rights_gate import publication_rights_gate_status  # noqa: E402

REQUIRED_SNIPPETS = [
    "rev0850 hardening",
    "_archive_regular_file_error",
    "_root_rights_file_audit",
    "root_license_or_notice_symlink_rejected",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-ledger-root-rights-boundary-rev0850: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ready_ledger() -> dict:
    return {
        "status": "publication_ready_for_validator_probe",
        "decision_required_before_publication": False,
        "blocking_findings": [],
        "root_license_or_notice_file_present": True,
        "missing_or_outside_local_license_reference_count": 0,
    }


def make_root(prefix: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    (root / "sources").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "RIGHTS").mkdir(parents=True)
    return tmp, root


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_ready_regular_files_pass() -> None:
    tmp, root = make_root("ev-rev0850-rights-regular-pass-")
    with tmp:
        (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
        write_json(root / "RIGHTS" / "component_license_ledger.json", ready_ledger())
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"regular ready ledger/root license unexpectedly blocked: {status.get('blocked_reasons')}")


def assert_symlinked_ledger_blocks() -> None:
    tmp, root = make_root("ev-rev0850-rights-ledger-symlink-")
    with tmp:
        (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
        outside = Path(tmp.name) / "outside-ledger.json"
        write_json(outside, ready_ledger())
        os.symlink(outside, root / "RIGHTS" / "component_license_ledger.json")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("symlinked rights ledger did not block publication")
        if "rights_ledger_load_error" not in status.get("blocked_reasons", []):
            fail(f"symlinked rights ledger did not surface as load error: {status}")
        if "symlink component" not in str(status.get("load_error")):
            fail(f"symlinked rights ledger load_error lost boundary detail: {status.get('load_error')}")


def assert_symlinked_rights_directory_blocks() -> None:
    tmp, root = make_root("ev-rev0850-rights-dir-symlink-")
    with tmp:
        (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
        external_rights = Path(tmp.name) / "external-rights"
        external_rights.mkdir()
        write_json(external_rights / "component_license_ledger.json", ready_ledger())
        (root / "RIGHTS").rmdir()
        os.symlink(external_rights, root / "RIGHTS")
        status = publication_rights_gate_status(root)
        if "rights_ledger_load_error" not in status.get("blocked_reasons", []):
            fail(f"symlinked RIGHTS directory did not block ledger read: {status}")


def assert_symlinked_root_license_blocks() -> None:
    tmp, root = make_root("ev-rev0850-root-license-symlink-")
    with tmp:
        outside = Path(tmp.name) / "outside-LICENSE"
        outside.write_text("outside license sentinel\n", encoding="utf-8")
        os.symlink(outside, root / "LICENSE")
        write_json(root / "RIGHTS" / "component_license_ledger.json", ready_ledger())
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("symlinked root LICENSE did not block publication")
        reasons = status.get("blocked_reasons", [])
        if "root_license_or_notice_symlink_rejected" not in reasons:
            fail(f"symlinked root LICENSE did not surface expected reason: {status}")
        rejected = status.get("root_license_or_notice_symlink_rejected") or []
        if not rejected or rejected[0].get("path") != "LICENSE":
            fail(f"symlinked root LICENSE audit row missing: {rejected}")


def assert_root_license_directory_blocks() -> None:
    tmp, root = make_root("ev-rev0850-root-license-dir-")
    with tmp:
        (root / "LICENSE").mkdir()
        write_json(root / "RIGHTS" / "component_license_ledger.json", ready_ledger())
        status = publication_rights_gate_status(root)
        if "root_license_or_notice_non_regular_rejected" not in status.get("blocked_reasons", []):
            fail(f"non-regular root LICENSE did not block: {status}")


def main() -> int:
    assert_static_contract()
    assert_ready_regular_files_pass()
    assert_symlinked_ledger_blocks()
    assert_symlinked_rights_directory_blocks()
    assert_symlinked_root_license_blocks()
    assert_root_license_directory_blocks()
    print("publication-rights-gate-ledger-root-rights-boundary-rev0850: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
