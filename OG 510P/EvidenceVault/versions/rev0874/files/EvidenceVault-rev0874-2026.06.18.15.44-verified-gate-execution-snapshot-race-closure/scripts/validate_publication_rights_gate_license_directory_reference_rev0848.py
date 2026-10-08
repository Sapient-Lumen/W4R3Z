#!/usr/bin/env python3
"""Validate rev0848 LICENSES-directory local-rights reference coverage."""
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
    "LICENSE_TARGET_COMPONENT_RE = re.compile",
    "def _target_path_is_license_like",
    "LICENSES/Apache-2.0.txt",
    "PurePosixPath",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-license-dir-rev0848: FAIL: {message}", file=sys.stderr)
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
    (root / "sources" / "pkg").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
    return tmp, root


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_missing_license_directory_target_blocks() -> None:
    tmp, root = make_root("ev-rev0848-rights-dir-missing-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=1)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Component SPDX text: [Apache-2.0](LICENSES/Apache-2.0.txt).\n",
            encoding="utf-8",
        )
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail("LICENSES/Apache-2.0.txt missing reference did not block publication")
        scan = status.get("fresh_local_license_reference_scan", {})
        refs = scan.get("missing_or_outside_local_license_references", [])
        if scan.get("missing_or_outside_local_license_reference_count") != 1 or not refs:
            fail(f"expected one missing LICENSES-directory reference, scan={scan}")
        row = refs[0]
        if row.get("target_text") != "LICENSES/Apache-2.0.txt" or row.get("reference_kind") != "markdown_link":
            fail(f"unexpected missing reference row: {row}")
        if "fresh_local_license_reference_missing_or_outside" not in set(status.get("blocked_reasons", [])):
            fail(f"missing-reference block reason absent: {status.get('blocked_reasons')}")


def assert_resolved_license_directory_target_passes() -> None:
    tmp, root = make_root("ev-rev0848-rights-dir-ok-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=0)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Component SPDX text: [Apache-2.0](LICENSES/Apache-2.0.txt).\n",
            encoding="utf-8",
        )
        target = root / "sources" / "pkg" / "LICENSES" / "Apache-2.0.txt"
        target.parent.mkdir()
        target.write_text("component license sentinel\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"resolved LICENSES-directory reference unexpectedly blocked: {status.get('blocked_reasons')}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_ok") != 1 or scan.get("missing_or_outside_local_license_reference_count") != 0:
            fail(f"resolved LICENSES-directory reference was not classified ok: {scan}")


def assert_british_licences_directory_is_checked() -> None:
    tmp, root = make_root("ev-rev0848-rights-licences-missing-")
    with tmp:
        write_ready_ledger(root, declared_missing_count=1)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Component terms: [MPL-2.0](licences/MPL-2.0.txt).\n",
            encoding="utf-8",
        )
        status = publication_rights_gate_status(root)
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("missing_or_outside_local_license_reference_count") != 1:
            fail(f"licences/ directory target was not checked as local rights reference: {scan}")


def main() -> int:
    assert_static_contract()
    assert_missing_license_directory_target_blocks()
    assert_resolved_license_directory_target_passes()
    assert_british_licences_directory_is_checked()
    print("publication-rights-gate-license-dir-rev0848: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
