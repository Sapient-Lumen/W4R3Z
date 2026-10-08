#!/usr/bin/env python3
"""Validate rev0849 fresh rights scan coverage for HTML/XML docs roots."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publication_rights_gate import publication_rights_gate_status  # noqa: E402

REQUIRED_SNIPPETS = [
    '"docs/"',
    '"documentation/"',
    '".html"',
    '".xhtml"',
    '".xml"',
    "rev0849 hardening",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-html-docs-scan-rev0849: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_ready_ledger(root: Path, declared_missing_count: int) -> None:
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


def make_root(prefix: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    (root / "sources").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
    return tmp, root


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_docs_html_missing_license_blocks() -> None:
    tmp, root = make_root("ev-rev0849-rights-html-missing-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=1)
        page = root / "docs" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text('<p>Terms: <a href="LICENSES/Apache-2.0.txt">Apache-2.0</a></p>\n', encoding="utf-8")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("missing docs/index.html LICENSES reference did not block publication")
        scan = status.get("fresh_local_license_reference_scan", {})
        refs = scan.get("missing_or_outside_local_license_references", [])
        if scan.get("missing_or_outside_local_license_reference_count") != 1 or not refs:
            fail(f"expected one missing HTML docs reference, scan={scan}")
        row = refs[0]
        if row.get("source_path") != "docs/index.html" or row.get("reference_kind") != "html_href":
            fail(f"unexpected HTML docs reference row: {row}")


def assert_docs_html_resolved_license_passes() -> None:
    tmp, root = make_root("ev-rev0849-rights-html-ok-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=0)
        page = root / "docs" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text('<p>Terms: <a href="LICENSES/Apache-2.0.txt">Apache-2.0</a></p>\n', encoding="utf-8")
        target = root / "docs" / "LICENSES" / "Apache-2.0.txt"
        target.parent.mkdir(parents=True)
        target.write_text("component license sentinel\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"resolved docs HTML license reference unexpectedly blocked: {status.get('blocked_reasons')}")


def assert_documentation_xml_missing_notice_blocks() -> None:
    tmp, root = make_root("ev-rev0849-rights-xml-missing-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=1)
        page = root / "documentation" / "feed.xml"
        page.parent.mkdir(parents=True)
        page.write_text('<doc><a href="notices/THIRD-PARTY.txt">third-party notice</a></doc>\n', encoding="utf-8")
        status = publication_rights_gate_status(root)
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("missing_or_outside_local_license_reference_count") != 1:
            fail(f"documentation/feed.xml notice reference was not checked: {scan}")


def main() -> int:
    assert_static_contract()
    assert_docs_html_missing_license_blocks()
    assert_docs_html_resolved_license_passes()
    assert_documentation_xml_missing_notice_blocks()
    print("publication-rights-gate-html-docs-scan-rev0849: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
