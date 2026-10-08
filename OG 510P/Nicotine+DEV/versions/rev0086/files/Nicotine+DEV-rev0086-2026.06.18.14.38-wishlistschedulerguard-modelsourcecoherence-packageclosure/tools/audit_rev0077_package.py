#!/usr/bin/env python3
"""Fail-closed rev0077 package audit, suitable for a clean extraction."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0077"
MANIFEST = Path("handoff/rev0077/MANIFEST.sha256")
OUTPUT = Path("data/rev0077_package_audit.json")
EVIDENCE = Path("evidence/rev0077-package-validation.md")
REQUIRED = (
    "README.md",
    "REVISION.txt",
    "docs/START-HERE.md",
    "docs/SEARCH-AGAIN-SELF-01-CURRENT-DISPOSITION-REV0077.md",
    "docs/SEARCH-AGAIN-REFRESH-EPOCH-AUDIT-REV0077.md",
    "docs/CURRENT-PUBLIC-CONTEXT-REV0077.md",
    "docs/AUTHORITY-ENGINE-REFACTOR-REV0077.md",
    "docs/PROBE-RUNTIME-AND-ISOLATION-REFACTOR-REV0077.md",
    "docs/PACKET-DISPOSITION-LEDGER-REV0077.md",
    "docs/SUPERSEDED-PACKET-INDEX-REV0077.md",
    "data/current_packet_dispositions.json",
    "data/current_packet_dispositions.schema.json",
    "data/current_packet_disposition_contract.json",
    "data/rev0077_packet_dispositions.json",
    "data/rev0077_packet_disposition_validation.json",
    "data/rev0077_authority_engine_audit.json",
    "data/rev0077_search_again_summary.json",
    "data/rev0077_search_again_test_matrix.csv",
    "data/rev0077_delta_inventory.json",
    "maintainer_artifacts/search-again-01/README.md",
    "maintainer_artifacts/search-again-01/master-search-again-self-token.patch",
    "maintainer_artifacts/search-again-01/search_again_harness.py",
    "maintainer_artifacts/search-again-01/test_search_again_epoch_models.py",
    "maintainer_artifacts/search-again-01/test_search_again_epoch_source_semantics.py",
    "maintainer_artifacts/search-again-01/test_search_again_self_token_current_behavior.py",
    "maintainer_artifacts/search-again-01/test_search_again_self_token_selected_policy.py",
    "tools/probe_rev0077_search_again.py",
    "tools/validate_current_packet_dispositions.py",
    "tools/audit_rev0077_authority_engine.py",
    "tools/build_rev0077_delta_inventory.py",
    "handoff/rev0077/REVISION-SUMMARY.md",
)
FORBIDDEN_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
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


def as_bool(value: object) -> bool:
    return str(value).lower() == "true"


def audit(root: Path, allow_missing_manifest: bool) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("revision marker", (root / "REVISION.txt").is_file() and (root / "REVISION.txt").read_text(encoding="utf-8").strip() == REVISION)
    for relative in REQUIRED:
        add(f"required path: {relative}", (root / relative).is_file())

    files = [path for path in sorted(root.rglob("*")) if path.is_file()]
    symlinks = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_symlink()]
    unsafe: list[str] = []
    cache_paths: list[str] = []
    embedded_archives: list[str] = []
    embedded_source: list[str] = []
    for path in files:
        relative = path.relative_to(root)
        rel = relative.as_posix()
        if not safe_relative(rel):
            unsafe.append(rel)
        if any(part in FORBIDDEN_PARTS for part in relative.parts) or path.suffix in {".pyc", ".pyo"}:
            cache_paths.append(rel)
        if path.suffix.lower() in {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz"} and rel not in ALLOWED_FIXTURE_ARCHIVES:
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

    artifact_dir = root / "maintainer_artifacts/search-again-01"
    python_paths = sorted({
        path for path in files
        if path.suffix == ".py" and (
            "rev0077" in path.name
            or path == root / "tools/validate_current_packet_dispositions.py"
            or path.parent == artifact_dir
        )
    })
    compile_errors: list[str] = []
    for path in python_paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            compile_errors.append(f"{path.relative_to(root)}: {exc}")
    add("revision Python compiles", not compile_errors, compile_errors)
    add("revision Python coverage", len(python_paths) >= 10, len(python_paths))

    try:
        summary = load(root, "data/rev0077_search_again_summary.json")
        add("search probe status", summary.get("status") == "pass", summary.get("errors"))
        add("search source invariants", (summary.get("source_invariants_passed"), summary.get("source_invariants_total")) == (12, 12))
        add("search classified expectations", (summary.get("test_expectations_passed"), summary.get("test_expectations_total")) == (26, 26))
        add("search compile checks", (summary.get("compile_checks_passed"), summary.get("compile_checks_total")) == (14, 14))
        add("search patch selected", summary.get("selected_patch") == "maintainer_artifacts/search-again-01/master-search-again-self-token.patch")
        add("search source hash", summary.get("source_bundle", {}).get("sha256") == "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b")
        add("search executable proxy", summary.get("executable_source", {}).get("ref") == "f4e17d59783dbc48ea31d2e899a681e2dd1ed500")
        add("search visible head", summary.get("visible_master_context", {}).get("head") == "a96406e7aa285a3fb2a3e35900686d164a22bf02")
        classified = summary.get("classified_runs", [])
        add("two grouped classified runs", len(classified) == 2 and all(row.get("collection_complete") and row.get("collected_tests") == 13 for row in classified), classified)
        units = summary.get("upstream_units", [])
        add("two unit states", len(units) == 2)
        add("unit parity 60/0/1", len(units) == 2 and all((row.get("passed"), row.get("failed"), row.get("skipped"), row.get("status")) == (60, 0, 1, "pass") for row in units), units)
    except Exception as exc:
        add("search summary readable", False, exc)

    try:
        with (root / "data/rev0077_search_again_test_matrix.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        add("test matrix rows", len(rows) == 26, len(rows))
        add("test matrix expectations", all(as_bool(row.get("expectation_match")) for row in rows))
        add("test matrix two states", {row.get("source_state") for row in rows} == {"bundled-master-baseline", "bundled-master-selected"})
        add("test matrix four roles", len({row.get("role") for row in rows}) == 4)
    except Exception as exc:
        add("test matrix readable", False, exc)

    try:
        validation = load(root, "data/rev0077_packet_disposition_validation.json")
        add("ledger validation pass", validation.get("status") == "pass", validation.get("errors"))
        add("ledger validation full", (validation.get("checks_passed"), validation.get("checks_total")) == (162, 162))
        ledger = load(root, "data/current_packet_dispositions.json")
        snapshot = load(root, "data/rev0077_packet_dispositions.json")
        contract = load(root, "data/current_packet_disposition_contract.json")
        add("ledger snapshot equality", ledger == snapshot)
        add("ledger revision", ledger.get("revision") == REVISION)
        by_id = {row.get("packet_id"): row for row in ledger.get("packets", [])}
        packet = by_id.get("SEARCH-AGAIN-SELF-01", {})
        add("new packet present", bool(packet))
        add("new packet selected patch", packet.get("selected_patch") == "maintainer_artifacts/search-again-01/master-search-again-self-token.patch")
        add("new packet master source", packet.get("source_ref") == "a96406e7aa285a3fb2a3e35900686d164a22bf02")
        add("contract covers exact packet set", set(contract.get("required_packet_ids", [])) == set(by_id))
    except Exception as exc:
        add("ledger artifacts readable", False, exc)

    try:
        authority = load(root, "data/rev0077_authority_engine_audit.json")
        add("authority audit pass", authority.get("status") == "pass", authority.get("errors"))
        add("authority mutants rejected", (authority.get("mutations_rejected"), authority.get("mutations_total")) == (7, 7))
        add("generic engine packet agnostic", authority.get("leaked_packet_ids") == [])
        add("generic engine revision neutral", authority.get("concrete_revision_literals") == [])
    except Exception as exc:
        add("authority audit readable", False, exc)

    try:
        delta = load(root, "data/rev0077_delta_inventory.json")
        add("delta revision", delta.get("revision") == REVISION)
        add("delta previous rev0076", "rev0076" in str(delta.get("previous_archive", "")))
        add("delta has changes", int(delta.get("changed_rows", 0)) > 0)
    except Exception as exc:
        add("delta readable", False, exc)

    probe_source = (root / "tools/probe_rev0077_search_again.py").read_text(encoding="utf-8")
    add("classified probe grouped", "def run_state_tests(" in probe_source and "--junitxml=" in probe_source)
    add("per-test process runner removed", "def run_test(" not in probe_source)
    add("multiprocessing output uses file", "def run_logged(" in probe_source and "regular-file output" in probe_source)

    patch_text = (artifact_dir / "master-search-again-self-token.patch").read_text(encoding="utf-8")
    add("patch one removed line", sum(line.startswith("-") and not line.startswith("---") for line in patch_text.splitlines()) == 1)
    add("patch one added line", sum(line.startswith("+") and not line.startswith("+++") for line in patch_text.splitlines()) == 1)
    add("patch binds search token", "self._own_tokens.add(search.token)" in patch_text)

    manifest_path = root / MANIFEST
    manifest_rows = 0
    if not manifest_path.exists():
        add("manifest allowed missing", allow_missing_manifest, MANIFEST)
    else:
        listed: dict[str, str] = {}
        malformed: list[str] = []
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
            "# rev0077 package validation",
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
