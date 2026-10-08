#!/usr/bin/env python3
"""Validate rev0842 fresh local-license-reference hardening in publication gate."""
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


def fail(message: str) -> None:
    print(f"publication-rights-gate-fresh-scan-rev0842: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_ready_ledger(root: Path, *, declared_missing_count: int | None = 0) -> None:
    ledger = {
        "status": "publication_ready_for_validator_probe",
        "decision_required_before_publication": False,
        "blocking_findings": [],
        "root_license_or_notice_file_present": True,
    }
    if declared_missing_count is not None:
        ledger["missing_or_outside_local_license_reference_count"] = declared_missing_count
    write_json(root / "RIGHTS" / "component_license_ledger.json", ledger)


def make_root() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="ev-rev0842-rights-gate-")
    root = Path(tmp.name) / "EvidenceVault-rev9999"
    root.mkdir()
    (root / "LICENSE").write_text("temporary validator root license sentinel\n", encoding="utf-8")
    (root / "sources" / "pkg").mkdir(parents=True)
    (root / "papers").mkdir()
    return tmp


def assert_missing_local_reference_blocks() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=0)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Licensed under Apache-2.0; see the [LICENSE](LICENSE) file for details.\n",
            encoding="utf-8",
        )
        status = publication_rights_gate_status(root)
        if not status["blocked"]:
            fail("missing local LICENSE reference did not block a rights-ready ledger")
        reasons = set(status.get("blocked_reasons", []))
        if "fresh_local_license_reference_missing_or_outside" not in reasons:
            fail(f"fresh missing-reference reason absent: {sorted(reasons)}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("missing_or_outside_local_license_reference_count") != 1:
            fail(f"fresh scan did not report exactly one missing reference: {scan}")


def assert_resolved_local_reference_allows_ready_ledger() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=0)
        (root / "sources" / "pkg" / "README.md").write_text(
            "Licensed under Apache-2.0; see the [LICENSE](LICENSE) file for details.\n",
            encoding="utf-8",
        )
        (root / "sources" / "pkg" / "LICENSE").write_text("temporary component license sentinel\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if status["blocked"]:
            fail(f"resolved local LICENSE reference unexpectedly blocked: {status.get('blocked_reasons')}")
        scan = status.get("fresh_local_license_reference_scan", {})
        if scan.get("local_references_ok") != 1 or scan.get("missing_or_outside_local_license_reference_count") != 0:
            fail(f"fresh scan did not classify resolved reference correctly: {scan}")


def assert_stale_ledger_count_blocks_when_comparable() -> None:
    with make_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        write_ready_ledger(root, declared_missing_count=1)
        (root / "sources" / "pkg" / "README.md").write_text("No local license links here.\n", encoding="utf-8")
        status = publication_rights_gate_status(root)
        if not status["blocked"]:
            fail("stale nonzero ledger missing-count did not block comparable canonical-scope scan")
        if "license_reference_ledger_stale" not in set(status.get("blocked_reasons", [])):
            fail(f"stale-count reason absent: {status.get('blocked_reasons')}")


def assert_partial_scope_blocks_when_ledger_count_is_claimed() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0842-rights-gate-partial-") as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        root.mkdir()
        (root / "LICENSE").write_text("temporary validator root license sentinel\n", encoding="utf-8")
        (root / "README.md").write_text("Partial overlay fixture.\n", encoding="utf-8")
        write_ready_ledger(root, declared_missing_count=1)
        status = publication_rights_gate_status(root)
        if not status["blocked"]:
            fail("partial scan scope with a claimed ledger reference count did not fail closed")
        if "license_reference_scan_scope_partial" not in set(status.get("blocked_reasons", [])):
            fail(f"partial-scope reason absent: {status.get('blocked_reasons')}")


def assert_no_bytecode_from_cli_probe() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0842-rights-gate-cli-") as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-rev9999"
        root.mkdir()
        (root / "LICENSE").write_text("temporary validator root license sentinel\n", encoding="utf-8")
        (root / "sources").mkdir()
        (root / "papers").mkdir()
        write_ready_ledger(root, declared_missing_count=0)
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
            fail(f"CLI ready-root probe failed: stdout={result.stdout!r} stderr={result.stderr!r}")
        try:
            data = json.loads(result.stdout)
        except Exception as exc:
            fail(f"CLI --json did not emit JSON: {exc}; stdout={result.stdout!r}")
        if data.get("blocked"):
            fail(f"CLI --json ready-root probe returned blocked status: {data}")
        offenders = [path for path in root.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
        if offenders:
            fail("CLI probe emitted bytecode: " + ", ".join(str(p.relative_to(root)) for p in offenders[:5]))


def main() -> int:
    assert_missing_local_reference_blocks()
    assert_resolved_local_reference_allows_ready_ledger()
    assert_stale_ledger_count_blocks_when_comparable()
    assert_partial_scope_blocks_when_ledger_count_is_claimed()
    assert_no_bytecode_from_cli_probe()
    print("publication-rights-gate-fresh-scan-rev0842: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
