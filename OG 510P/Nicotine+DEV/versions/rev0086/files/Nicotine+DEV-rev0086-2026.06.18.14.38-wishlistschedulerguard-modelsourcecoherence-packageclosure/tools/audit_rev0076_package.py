#!/usr/bin/env python3
"""Fail-closed rev0076 package audit, suitable for a clean extraction."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0076"
MANIFEST = Path("handoff/rev0076/MANIFEST.sha256")
OUTPUT = Path("data/rev0076_package_audit.json")
EVIDENCE = Path("evidence/rev0076-package-validation.md")
REQUIRED = (
    "README.md",
    "REVISION.txt",
    "docs/START-HERE.md",
    "docs/SEARCH-RESP-01B-CURRENT-DISPOSITION-REV0076.md",
    "docs/SEARCH-RESP-01B-IDENTITY-AND-EPOCH-AUDIT-REV0076.md",
    "docs/REQUEST-EPOCH-DESIGN-NOTES-REV0076.md",
    "docs/SEARCH-RESP-BUDDY-ARTIFACT-REFACTOR-REV0076.md",
    "docs/PACKET-DISPOSITION-LEDGER-REV0076.md",
    "docs/SUPERSEDED-PACKET-INDEX-REV0076.md",
    "data/current_packet_dispositions.json",
    "data/current_packet_dispositions.schema.json",
    "data/rev0076_packet_dispositions.json",
    "data/rev0076_packet_disposition_validation.json",
    "data/rev0076_status_authority_audit.json",
    "data/rev0076_search_resp_buddy_summary.json",
    "data/rev0076_delta_inventory.json",
    "maintainer_artifacts/search-resp-01/buddy_search_harness.py",
    "maintainer_artifacts/search-resp-01/test_search_resp_buddy_master_resend_epoch.py",
    "tools/probe_rev0076_search_resp_buddy_disposition.py",
    "tools/validate_current_packet_dispositions_rev0076.py",
    "tools/audit_rev0076_status_authority.py",
    "handoff/rev0076/REVISION-SUMMARY.md",
)
FORBIDDEN_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
ARCHIVE = Path("docs/archive/rev0075-active-search-resp-buddy/test_search_response_buddy_scope_fixed_regression.py")
ARCHIVE_SHA256 = "6b4d9ae5e246e70bcbce34790938ba252fbdd970f0f06382279bb3e328935c86"
ALLOWED_FIXTURE_ARCHIVES = {
    "evidence/rev0063-cleanroom-contract-gate/negative-controls/wrong-source.zip":
        "d93224fe1f4c1c266c649bc09a327aa81f079b87eb013228e7291c828990346c",
    "evidence/rev0064-inherited-rev0063-contract-rerun/negative-controls/wrong-source.zip":
        "9a49a7657d6b91436f8d000d271b365e7f08145cb3edb225fa6715451a324dbe",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def audit(root: Path, allow_missing_manifest: bool) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("revision marker", (root / "REVISION.txt").is_file() and (root / "REVISION.txt").read_text().strip() == REVISION)
    for relative in REQUIRED:
        add(f"required path: {relative}", (root / relative).is_file())

    files = [path for path in sorted(root.rglob("*")) if path.is_file()]
    symlinks = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_symlink()]
    unsafe = []
    cache_paths = []
    embedded_archives = []
    embedded_source = []
    for path in files:
        relative = path.relative_to(root)
        rel = relative.as_posix()
        if not safe_relative(rel):
            unsafe.append(rel)
        if any(part in FORBIDDEN_PARTS for part in relative.parts) or path.suffix in {".pyc", ".pyo"}:
            cache_paths.append(rel)
        if (
            path.suffix.lower() in {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz"}
            and rel not in ALLOWED_FIXTURE_ARCHIVES
        ):
            embedded_archives.append(rel)
        if relative.parts[:1] == ("pynicotine",) or rel.startswith("nicotine-plus/"):
            embedded_source.append(rel)
    add("no symlinks", not symlinks, symlinks[:10])
    add("no unsafe paths", not unsafe, unsafe[:10])
    add("no Git/cache artifacts", not cache_paths, cache_paths[:10])
    fixture_errors = [
        rel for rel, expected in ALLOWED_FIXTURE_ARCHIVES.items()
        if not (root / rel).is_file() or digest(root / rel) != expected
    ]
    add("approved negative-control archives intact", not fixture_errors, fixture_errors)
    add("no unapproved embedded archives/source ZIP", not embedded_archives, embedded_archives[:10])
    add("no embedded upstream source tree", not embedded_source, embedded_source[:10])

    python_paths = sorted({
        path for path in files
        if path.suffix == ".py" and (
            "rev0076" in path.name
            or path.parent == root / "maintainer_artifacts/search-resp-01"
        )
    })
    compile_errors = []
    for path in python_paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            compile_errors.append(f"{path.relative_to(root)}: {exc}")
    add("revision Python compiles", not compile_errors, compile_errors)
    add("revision Python coverage", len(python_paths) >= 13, len(python_paths))

    archive = root / ARCHIVE
    add("archived monolith hash", archive.is_file() and digest(archive) == ARCHIVE_SHA256)
    add("old monolith absent active", not (root / "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py").exists())

    try:
        summary = load(root, "data/rev0076_search_resp_buddy_summary.json")
        add("probe status", summary.get("status") == "pass", summary.get("errors"))
        add("probe source invariants", (summary.get("source_invariants_passed"), summary.get("source_invariants_total")) == (12, 12))
        add("probe classified expectations", (summary.get("test_expectations_passed"), summary.get("test_expectations_total")) == (26, 26))
        add("probe compile checks", (summary.get("compile_checks_passed"), summary.get("compile_checks_total")) == (10, 10))
        add("probe no selected patch", summary.get("selected_patch") is None)
        add("probe security route", summary.get("security_route") == "not supported by current evidence")
        units = summary.get("upstream_units", [])
        add("two supported unit states", len(units) == 2, len(units))
        add("unit result parity", len({(row.get("passed"), row.get("failed"), row.get("skipped")) for row in units}) == 1)
        add("units 58 pass 1 skip", all((row.get("passed"), row.get("failed"), row.get("skipped"), row.get("status")) == (58, 0, 1, "pass") for row in units))
        refactor = summary.get("artifact_refactor", {})
        add("artifact refactor line reduction", int(refactor.get("line_delta", 0)) < 0, refactor)
        add("artifact refactor byte nonincrease", int(refactor.get("byte_delta", 1)) <= 0, refactor)
    except Exception as exc:
        add("probe summary readable", False, exc)

    try:
        validation = load(root, "data/rev0076_packet_disposition_validation.json")
        add("ledger validation pass", validation.get("status") == "pass", validation.get("errors"))
        add("ledger validation no buddy patch", validation.get("buddy_selected_patch") is None)
        ledger = load(root, "data/current_packet_dispositions.json")
        snapshot = load(root, "data/rev0076_packet_dispositions.json")
        add("ledger snapshot equality", ledger == snapshot)
        buddy = {row.get("packet_id"): row for row in ledger.get("packets", [])}.get("SEARCH-RESP-01B/U-163B", {})
        add("ledger buddy status", buddy.get("status") == "open-request-epoch-design-research", buddy.get("status"))
        add("ledger buddy no patch", buddy.get("selected_patch") is None)
    except Exception as exc:
        add("ledger artifacts readable", False, exc)

    try:
        status = load(root, "data/rev0076_status_authority_audit.json")
        add("status authority pass", status.get("status") == "pass", status.get("errors"))
        add("status authority stable", status.get("self_reference_stability") == "pass")
        add("status active metrics", status.get("active_metrics") == {
            "files": 6, "lines": 167, "bytes": 6504, "lines_over_100": 0,
        }, status.get("active_metrics"))
    except Exception as exc:
        add("status authority readable", False, exc)

    try:
        delta = load(root, "data/rev0076_delta_inventory.json")
        add("delta revision", delta.get("revision") == REVISION)
        add("delta previous rev0075", "rev0075" in str(delta.get("previous_archive", "")))
        add("delta has changes", int(delta.get("changed_rows", 0)) > 0)
    except Exception as exc:
        add("delta readable", False, exc)

    manifest_path = root / MANIFEST
    manifest_rows = 0
    if not manifest_path.exists():
        add("manifest allowed missing", allow_missing_manifest, MANIFEST)
    else:
        listed: dict[str, str] = {}
        malformed = []
        for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if not match or not safe_relative(match.group(2)):
                malformed.append(f"{line_no}:{line}")
                continue
            if match.group(2) in listed:
                malformed.append(f"duplicate:{match.group(2)}")
            listed[match.group(2)] = match.group(1)
        expected = {
            path.relative_to(root).as_posix()
            for path in files
            if path.relative_to(root) != MANIFEST and not path.is_symlink()
        }
        actual = set(listed)
        mismatches = [rel for rel in sorted(expected & actual) if digest(root / rel) != listed[rel]]
        add("manifest syntax", not malformed, malformed[:10])
        add("manifest coverage", expected == actual, {"missing": sorted(expected - actual)[:10], "extra": sorted(actual - expected)[:10]})
        add("manifest hashes", not mismatches, mismatches[:10])
        manifest_rows = len(listed)

    return {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "package_files": len(files),
        "compiled_python_files": len(python_paths),
        "manifest_rows": manifest_rows,
        "symlinks": len(symlinks),
        "cache_paths": len(cache_paths),
        "approved_fixture_archives": len(ALLOWED_FIXTURE_ARCHIVES),
        "embedded_archives": len(embedded_archives),
        "embedded_source_paths": len(embedded_source),
        "checks": checks,
        "errors": errors,
    }


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--allow-missing-manifest", action="store_true")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root, args.allow_missing_manifest)
    if args.write_data:
        (root / OUTPUT).write_text(canonical(result), encoding="utf-8")
        lines = [
            "# rev0076 package validation",
            "",
            f"Status: **{result['status']}**",
            "",
            "```text",
            f"checks: {result['checks_passed']}/{result['checks_total']}",
            f"files: {result['package_files']}",
            f"compiled revision Python files: {result['compiled_python_files']}",
            f"manifest rows: {result['manifest_rows']}",
            f"symlinks: {result['symlinks']}",
            f"cache paths: {result['cache_paths']}",
            f"approved negative-control archives: {result['approved_fixture_archives']}",
            f"unapproved embedded archives: {result['embedded_archives']}",
            f"embedded source paths: {result['embedded_source_paths']}",
            "```",
            "",
        ]
        if result["errors"]:
            lines.extend(["## Errors", ""] + [f"- {item}" for item in result["errors"]])
        (root / EVIDENCE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(canonical(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
