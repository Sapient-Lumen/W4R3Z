#!/usr/bin/env python3
"""Validate rev0845 symlink and HTML/reST hardening in publication_rights_gate.py."""
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
    "HTML_HREF_RE = re.compile(",
    "RST_INLINE_LINK_RE = re.compile(",
    "files_symlink_rejected",
    "target_symlink_rejected",
    "fresh_license_reference_scan_symlink_rejected",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-symlink-boundary-rev0845: FAIL: {message}", file=sys.stderr)
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
    tmp = tempfile.TemporaryDirectory(prefix="ev-rev0845-rights-boundary-")
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    (root / "sources" / "pkg").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
    write_ready_ledger(root, declared_missing_count=0)
    return tmp


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_scan_input_symlink_blocks_without_reading_target() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        outside = Path(tmp_name) / "outside-readme.md"
        outside.write_text("This outside file should never be scanned through the archive symlink.\n", encoding="utf-8")
        os.symlink(outside, root / "sources" / "pkg" / "README.md")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("symlinked scan input did not block a rights-ready ledger")
        reasons = set(status.get("blocked_reasons", []))
        if "fresh_license_reference_scan_symlink_rejected" not in reasons:
            fail(f"symlink scan-input reason absent: {sorted(reasons)}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("files_symlink_rejected") != 1:
            fail(f"scan did not report exactly one rejected symlink input: {scan}")
        if "sources/pkg/README.md" not in scan.get("symlink_paths_rejected", []):
            fail(f"rejected symlink path not reported: {scan.get('symlink_paths_rejected')}")


def assert_symlinked_local_rights_target_blocks() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        (root / "sources" / "pkg" / "README.md").write_text("See the [LICENSE](LICENSE) file.\n", encoding="utf-8")
        os.symlink(root / "LICENSE", root / "sources" / "pkg" / "LICENSE")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("symlinked local LICENSE target did not block a rights-ready ledger")
        reasons = set(status.get("blocked_reasons", []))
        if "fresh_local_license_reference_target_symlink" not in reasons:
            fail(f"symlink target reason absent: {sorted(reasons)}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_target_symlink_rejected") != 1:
            fail(f"scan did not classify symlinked target correctly: {scan}")
        refs = scan.get("blocking_local_license_references", [])
        if not refs or refs[0].get("status") != "target_symlink_rejected":
            fail(f"blocking symlink reference not captured: {refs}")


def assert_html_and_rst_license_links_are_checked() -> None:
    fixtures = [
        ("<a href=\"NOTICE\">License notice</a>\n", "html_href", "NOTICE"),
        ("`License <LICENSE>`_\n", "rst_inline_link", "LICENSE"),
        (".. _License: COPYING\n", "rst_reference_definition", "COPYING"),
    ]
    for text, expected_kind, expected_target in fixtures:
        with make_root() as tmp_name:
            root = Path(tmp_name) / "EvidenceVault-rev9999"
            write_ready_ledger(root, declared_missing_count=1)
            (root / "sources" / "pkg" / "README.md").write_text(text, encoding="utf-8")
            status = publication_rights_gate_status(root)
            scan = status.get("fresh_local_license_reference_scan", {})
            refs = scan.get("missing_or_outside_local_license_references", [])
            if not refs:
                fail(f"{expected_kind} fixture did not produce a missing local rights reference: {scan}")
            if refs[0].get("reference_kind") != expected_kind or refs[0].get("target_text") != expected_target:
                fail(f"{expected_kind} fixture misclassified: {refs[0]}")


def assert_in_document_anchor_does_not_block() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        (root / "sources" / "pkg" / "README.md").write_text("See [License](#license) below.\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"in-document license anchor unexpectedly blocked publication: {status.get('blocked_reasons')}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("references_total") != 0:
            fail(f"in-document anchor should not be treated as a local file reference: {scan}")


def main() -> int:
    assert_static_contract()
    assert_scan_input_symlink_blocks_without_reading_target()
    assert_symlinked_local_rights_target_blocks()
    assert_html_and_rst_license_links_are_checked()
    assert_in_document_anchor_does_not_block()
    print("publication-rights-gate-symlink-boundary-rev0845: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
