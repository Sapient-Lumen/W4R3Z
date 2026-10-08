#!/usr/bin/env python3
"""Validate rev0846 intermediate-symlink closure in publication_rights_gate.py."""
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
    "def _first_symlink_component",
    "symlink_archive_path",
    "local rights targets are rejected if any intermediate archive",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-intermediate-symlink-rev0846: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_ready_ledger(root: Path, declared_missing_count: int = 0) -> None:
    write_json(
        root / "RIGHTS" / "component_license_ledger.json",
        {
            "status": "publication_ready_for_validator_probe",
            "decision_required_before_publication": False,
            "blocking_findings": [],
            "root_license_or_notice_file_present": True,
            "missing_or_outside_local_license_reference_count": declared_missing_count,
        },
    )


def make_root() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="ev-rev0846-rights-intermediate-link-")
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    (root / "sources" / "pkg").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
    write_ready_ledger(root)
    return tmp


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_clean_nested_local_license_reference_still_passes() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        nested = root / "sources" / "pkg" / "nested"
        nested.mkdir()
        (nested / "LICENSE").write_text("nested license sentinel\n", encoding="utf-8")
        (root / "sources" / "pkg" / "README.md").write_text("See [license](nested/LICENSE).\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"clean nested local license reference unexpectedly blocked: {status.get('blocked_reasons')}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_ok") != 1:
            fail(f"clean nested local license reference not counted as OK: {scan}")


def assert_intermediate_symlink_target_blocks_even_when_resolved_inside_archive() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        real = root / "sources" / "pkg" / "real-rights"
        real.mkdir()
        (real / "LICENSE").write_text("real local license sentinel\n", encoding="utf-8")
        os.symlink(real, root / "sources" / "pkg" / "linked-rights")
        (root / "sources" / "pkg" / "README.md").write_text(
            "See [license](linked-rights/LICENSE).\n",
            encoding="utf-8",
        )
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("intermediate symlink target did not block a rights-ready ledger")
        reasons = set(status.get("blocked_reasons", []))
        if "fresh_local_license_reference_target_symlink" not in reasons:
            fail(f"intermediate symlink reason absent: {sorted(reasons)}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_target_symlink_rejected") != 1:
            fail(f"intermediate symlink target not counted as rejected: {scan}")
        refs = scan.get("blocking_local_license_references", [])
        if not refs:
            fail(f"intermediate symlink reference not recorded: {scan}")
        row = refs[0]
        if row.get("status") != "target_symlink_rejected":
            fail(f"intermediate symlink reference has wrong status: {row}")
        if row.get("symlink_archive_path") != "sources/pkg/linked-rights":
            fail(f"first symlink component not reported: {row}")
        if row.get("resolved_archive_path") != "sources/pkg/real-rights/LICENSE":
            fail(f"resolved archive target not reported correctly: {row}")


def assert_intermediate_symlink_target_blocks_when_resolved_outside_archive() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        outside = Path(tmp_name) / "outside-rights"
        outside.mkdir()
        (outside / "LICENSE").write_text("outside license sentinel\n", encoding="utf-8")
        os.symlink(outside, root / "sources" / "pkg" / "outside-rights")
        (root / "sources" / "pkg" / "README.md").write_text("See [license](outside-rights/LICENSE).\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("outside intermediate symlink target did not block")
        reasons = set(status.get("blocked_reasons", []))
        if "fresh_local_license_reference_target_symlink" not in reasons and "fresh_local_license_reference_missing_or_outside" not in reasons:
            fail(f"outside symlink target reason absent: {sorted(reasons)}")
        scan = status.get("fresh_local_license_reference_scan", {})
        refs = scan.get("blocking_local_license_references", [])
        if not refs or refs[0].get("status") not in {"target_symlink_rejected", "outside_archive"}:
            fail(f"outside intermediate symlink not captured as blocking: {refs}")


def main() -> int:
    assert_static_contract()
    assert_clean_nested_local_license_reference_still_passes()
    assert_intermediate_symlink_target_blocks_even_when_resolved_inside_archive()
    assert_intermediate_symlink_target_blocks_when_resolved_outside_archive()
    print("publication-rights-gate-intermediate-symlink-rev0846: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
