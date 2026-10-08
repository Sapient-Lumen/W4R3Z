#!/usr/bin/env python3
"""Validate rev0844 Markdown reference-form coverage in the publication rights gate."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publication_rights_gate import publication_rights_gate_status  # noqa: E402

REQUIRED_SNIPPETS = [
    "MARKDOWN_LINK_RE = re.compile(",
    "MARKDOWN_REFERENCE_DEF_RE = re.compile(",
    "markdown_reference_definition",
    "reference_def = MARKDOWN_REFERENCE_DEF_RE.match(line)",
]


def fail(message: str) -> None:
    print(f"publication-rights-gate-markdown-forms-rev0844: FAIL: {message}", file=sys.stderr)
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


def make_root() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="ev-rev0844-rights-markdown-")
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    (root / "sources" / "pkg").mkdir(parents=True)
    (root / "papers").mkdir(parents=True)
    (root / "LICENSE").write_text("temporary root license sentinel\n", encoding="utf-8")
    return tmp


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publication_rights_gate.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing parser snippets: " + ", ".join(missing))


def scan_single_readme(readme_text: str, expected_kind: str, expected_target: str) -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=1)
        (root / "sources" / "pkg" / "README.md").write_text(readme_text, encoding="utf-8")
        status = publication_rights_gate_status(root)
        if not status.get("blocked"):
            fail(f"{expected_kind} missing local reference did not block publication")
        scan = status.get("fresh_local_license_reference_scan", {})
        refs = scan.get("missing_or_outside_local_license_references", [])
        if scan.get("missing_or_outside_local_license_reference_count") != 1:
            fail(f"{expected_kind} expected exactly one missing reference, scan={scan}")
        row = refs[0]
        if row.get("reference_kind") != expected_kind:
            fail(f"expected reference kind {expected_kind}, got {row}")
        if row.get("target_text") != expected_target:
            fail(f"expected target {expected_target!r}, got {row}")
        if "fresh_local_license_reference_missing_or_outside" not in set(status.get("blocked_reasons", [])):
            fail(f"fresh missing-reference reason absent for {expected_kind}: {status.get('blocked_reasons')}")


def assert_inline_link_with_title_is_checked() -> None:
    scan_single_readme(
        "Component terms: [license](LICENSE \"component license\").\n",
        "markdown_link",
        "LICENSE",
    )


def assert_angle_wrapped_notice_link_is_checked() -> None:
    scan_single_readme(
        "Required notice: [NOTICE](<NOTICE.md> \"component notice\").\n",
        "markdown_link",
        "NOTICE.md",
    )


def assert_reference_definition_is_checked() -> None:
    scan_single_readme(
        "Component terms use a reference link.\n\n[lic]: COPYING \"copying terms\"\n",
        "markdown_reference_definition",
        "COPYING",
    )


def assert_resolved_reference_definition_allows_ready_ledger() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=0)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Component terms use a reference link.\n\n[component-license]: LICENSE \"component license\"\n",
            encoding="utf-8",
        )
        (root / "sources" / "pkg" / "LICENSE").write_text("component license sentinel\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status.get("blocked"):
            fail(f"resolved reference definition unexpectedly blocked: {status.get('blocked_reasons')}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_ok") != 1 or scan.get("missing_or_outside_local_license_reference_count") != 0:
            fail(f"resolved reference definition was not classified as ok: {scan}")


def assert_cli_no_bytecode_for_extended_parser() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=0)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Component terms: [license](LICENSE \"component license\").\n",
            encoding="utf-8",
        )
        (root / "sources" / "pkg" / "LICENSE").write_text("component license sentinel\n", encoding="utf-8")
        scripts = root / "scripts"
        scripts.mkdir()
        shutil.copy2(ROOT / "scripts" / "publication_rights_gate.py", scripts / "publication_rights_gate.py")
        result = subprocess.run(
            [sys.executable, str(scripts / "publication_rights_gate.py"), "--root", str(root), "--json"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            fail(f"extended-parser CLI ready-root probe failed: stdout={result.stdout!r} stderr={result.stderr!r}")
        try:
            data = json.loads(result.stdout)
        except Exception as exc:
            fail(f"extended-parser CLI did not emit JSON: {exc}; stdout={result.stdout!r}")
        if data.get("blocked"):
            fail(f"extended-parser CLI returned blocked status for resolved fixture: {data}")
        offenders = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
        if offenders:
            fail("CLI emitted bytecode: " + ", ".join(offenders[:5]))


def main() -> int:
    assert_static_contract()
    assert_inline_link_with_title_is_checked()
    assert_angle_wrapped_notice_link_is_checked()
    assert_reference_definition_is_checked()
    assert_resolved_reference_definition_allows_ready_ledger()
    assert_cli_no_bytecode_for_extended_parser()
    print("publication-rights-gate-markdown-forms-rev0844: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
