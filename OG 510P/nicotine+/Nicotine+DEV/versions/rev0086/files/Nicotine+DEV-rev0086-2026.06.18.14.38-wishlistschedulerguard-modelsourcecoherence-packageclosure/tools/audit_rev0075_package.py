#!/usr/bin/env python3
"""Fail-closed package coherence audit for rev0075."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
REVISION = "rev0075"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
MANIFEST = Path("handoff/rev0075/MANIFEST.sha256")
SELF_OUTPUTS = {
    Path("data/rev0075_package_preflight.json"),
    Path("evidence/rev0075-package-validation.md"),
}
REQUIRED = (
    Path("README.md"),
    Path("REVISION.txt"),
    Path("docs/START-HERE.md"),
    Path("docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md"),
    Path("docs/SEARCH-RESP-01A-IDENTITY-AND-REACHABILITY-AUDIT-REV0075.md"),
    Path("docs/SEARCH-RESP-ARTIFACT-COHERENCE-REFACTOR-REV0075.md"),
    Path("docs/CLAIM-EVIDENCE-LADDER-REV0075.md"),
    Path("docs/PACKET-DISPOSITION-LEDGER-REV0075.md"),
    Path("docs/SUPERSEDED-PACKET-INDEX-REV0075.md"),
    Path("docs/PACKAGE-COHERENCE-GATE-REV0075.md"),
    Path("data/current_packet_dispositions.json"),
    Path("data/rev0075_packet_dispositions.json"),
    Path("data/rev0075_search_resp_disposition_summary.json"),
    Path("data/rev0075_search_resp_test_matrix.csv"),
    Path("data/rev0075_search_resp_source_invariants.csv"),
    Path("data/rev0075_search_resp_reachability_matrix.csv"),
    Path("data/rev0075_search_resp_compile_matrix.csv"),
    Path("data/rev0075_search_resp_artifact_inventory.csv"),
    Path("data/rev0075_search_resp_duplicate_groups.csv"),
    Path("data/rev0075_packet_status_audit.json"),
    Path("data/rev0075_delta_inventory.csv"),
    Path("data/rev0075_delta_inventory.json"),
    Path("data/rev0075_package_preflight.json"),
    Path("evidence/rev0075-package-validation.md"),
    Path("evidence/rev0075-search-resp-upstream-history.md"),
    Path("evidence/rev0075-search-resp-public-overlap.md"),
    Path("evidence/rev0075-packet-status-audit.md"),
    Path("report_drafts/SEARCH-RESP-01A-CURRENT-STATUS-REV0075.md"),
    Path("maintainer_artifacts/search-resp-01/search_resp_harness.py"),
    Path("maintainer_artifacts/search-resp-01/test_search_resp_current_behavior.py"),
    Path("maintainer_artifacts/search-resp-01/test_search_resp_rev0039_policy.py"),
    Path("maintainer_artifacts/search-resp-01/test_search_resp_identity_counterexample.py"),
    Path("maintainer_artifacts/search-resp-01/test_search_resp_token_model.py"),
    Path("tools/probe_rev0075_search_resp_disposition.py"),
    Path("tools/audit_rev0075_packet_status.py"),
    Path("tools/build_rev0075_delta_inventory.py"),
    Path("tools/build_rev0075_manifest.py"),
    Path("tools/audit_rev0075_package.py"),
    Path("handoff/rev0075/README.md"),
    Path("handoff/rev0075/REVISION-SUMMARY.md"),
    Path("handoff/rev0075/SEARCH-RESP-01A-RESEARCH-DISPOSITION.md"),
)
ARCHIVE_HASHES = {
    Path("docs/archive/rev0074-active-search-resp-01/test_search_response_scope_and_parse_order_reproducer.py"):
        "d7f98b7fca31085e10df98782ebd824e4d10e950567b5826079a4fa2f6507e6e",
    Path("docs/archive/rev0074-active-search-resp-01/test_search_response_user_scope_fixed_regression.py"):
        "fc91da0e93f9086f0193e7d2903b56f06e0d5978c730c9295b02989a3966a9c1",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def package_files(root: Path) -> list[Path]:
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and path.relative_to(root) != MANIFEST
    )


def check_manifest(root: Path, errors: list[str]) -> dict[str, Any]:
    path = root / MANIFEST
    if not path.is_file():
        errors.append(f"missing manifest: {MANIFEST}")
        return {"status": "missing", "rows": 0}
    rows: dict[Path, str] = {}
    malformed: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            value, relative = line.split("  ", 1)
        except ValueError:
            malformed.append(f"line {lineno}")
            continue
        item = Path(relative)
        if item in rows:
            malformed.append(f"duplicate {relative}")
        if not re_full_sha256(value):
            malformed.append(f"digest {lineno}")
        rows[item] = value
    actual = set(package_files(root))
    listed = set(rows)
    missing = sorted(actual - listed)
    extra = sorted(listed - actual)
    mismatched = sorted(item for item in actual & listed if digest(root / item) != rows[item])
    if malformed:
        errors.append(f"malformed manifest: {malformed[:5]}")
    if missing:
        errors.append(f"manifest missing {len(missing)} paths: {missing[:5]}")
    if extra:
        errors.append(f"manifest extra {len(extra)} paths: {extra[:5]}")
    if mismatched:
        errors.append(f"manifest mismatches {len(mismatched)} paths: {mismatched[:5]}")
    ok = not (malformed or missing or extra or mismatched)
    return {
        "status": "pass" if ok else "fail",
        "rows": len(rows),
        "missing": [str(item) for item in missing],
        "extra": [str(item) for item in extra],
        "mismatched": [str(item) for item in mismatched],
    }


def re_full_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allow-missing-manifest", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    missing_required = [str(path) for path in REQUIRED if not (root / path).is_file()]
    if missing_required:
        errors.append(f"missing required paths: {missing_required}")
    revision = (root / "REVISION.txt").read_text(encoding="utf-8").strip() if (root / "REVISION.txt").is_file() else ""
    if revision != REVISION:
        errors.append(f"revision {revision!r} != {REVISION!r}")

    forbidden: list[str] = []
    symlinks: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            symlinks.append(str(relative))
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in relative.parts):
            forbidden.append(str(relative))
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            forbidden.append(str(relative))
        elif path.is_dir() and path.name == "pynicotine":
            forbidden.append(str(relative))
        elif path.is_file() and "nicotine-source" in path.name.lower():
            forbidden.append(str(relative))
    if forbidden:
        errors.append(f"forbidden cache/source paths: {forbidden[:10]}")
    if symlinks:
        errors.append(f"symlinks: {symlinks[:10]}")

    compile_rows: list[dict[str, str]] = []
    candidates = set(root.glob("tools/*rev0075*.py")) | set(root.glob("maintainer_artifacts/search-resp-01/*.py"))
    for path in sorted(candidates):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        try:
            compile(path.read_text(encoding="utf-8"), str(relative), "exec")
            status, message = "pass", ""
        except Exception as exc:
            status, message = "fail", f"{type(exc).__name__}: {exc}"
            errors.append(f"compile {relative}: {message}")
        compile_rows.append({"path": str(relative), "status": status, "error": message})

    checks: list[dict[str, Any]] = []

    def add(name: str, value: bool) -> None:
        checks.append({"check": name, "pass": bool(value)})
        if not value:
            errors.append(f"failed check: {name}")

    try:
        summary = load(root, "data/rev0075_search_resp_disposition_summary.json")
        add("search_resp_summary_pass", summary.get("status") == "pass")
        add("exact_current_ref", summary.get("exact_current_ref_match") is True)
        add("expected_ref", summary.get("expected_ref") == EXPECTED_REF)
        add("classified_8_of_8", (summary.get("test_expectations_passed"), summary.get("test_expectations_total")) == (8, 8))
        add("source_invariants_8_of_8", (summary.get("source_invariants_passed"), summary.get("source_invariants_total")) == (8, 8))
        add("compile_6_of_6", (summary.get("compile_checks_passed"), summary.get("compile_checks_total")) == (6, 6))
        add("selected_patch_null", summary.get("selected_patch") is None)
        add("security_route_unsupported", summary.get("security_route") == "not supported by current evidence")
        add("upstream_unit_parity", summary.get("upstream_unit_parity") is True)
        units = summary.get("upstream_units", [])
        add("two_unit_states", len(units) == 2)
        add(
            "units_58_pass_1_skip",
            all((row.get("passed"), row.get("skipped"), row.get("failed"), row.get("status")) == (58, 1, 0, "pass") for row in units),
        )
        add(
            "i18n_exclusion_recorded",
            all(row.get("i18n_excluded") is True and row.get("msgfmt_available") is False for row in units),
        )
        experiment = summary.get("experiment", {})
        experiment_path = root / str(experiment.get("artifact", ""))
        add(
            "experiment_hash",
            experiment_path.is_file()
            and digest(experiment_path) == experiment.get("sha256")
            and experiment.get("status") == "pass",
        )
        refactor = summary.get("artifact_refactor", {})
        add("active_refactor_smaller", int(refactor.get("byte_delta", 0)) < 0 and int(refactor.get("line_delta", 0)) < 0)
    except Exception as exc:
        errors.append(f"summary inspection: {exc}")

    try:
        status = load(root, "data/rev0075_packet_status_audit.json")
        add("packet_status_pass", status.get("status") == "pass")
        add("packet_status_active_72_of_72", (status.get("active_checks_passed"), status.get("active_checks_total")) == (72, 72))
        add("packet_status_idempotent", status.get("self_reference_stability") == "pass")
        add("packet_status_no_selected_patch", status.get("search_resp_selected_patch") is None)
        add(
            "packet_status_duplicates_measured",
            int(status.get("duplicate_hash_groups", 0)) > 0
            and int(status.get("duplicate_wasted_bytes", 0)) > 0,
        )
    except Exception as exc:
        errors.append(f"packet status inspection: {exc}")

    try:
        ledger = load(root, "data/current_packet_dispositions.json")
        snapshot = load(root, "data/rev0075_packet_dispositions.json")
        by_id = {item.get("packet_id"): item for item in ledger.get("packets", [])}
        search_row = by_id.get("SEARCH-RESP-01A/U-163A", {})
        add("ledger_revision", ledger.get("revision") == REVISION)
        add("ledger_snapshot_equal", ledger == snapshot)
        add("ledger_search_resp_open", search_row.get("status") == "open-defense-in-depth-research")
        add("ledger_search_resp_no_patch", search_row.get("selected_patch") is None)
        add("ledger_search_resp_security_route", search_row.get("security_route") == "not supported by current evidence")
    except Exception as exc:
        errors.append(f"ledger inspection: {exc}")

    try:
        delta = load(root, "data/rev0075_delta_inventory.json")
        add("delta_revision", delta.get("revision") == REVISION)
        add("delta_has_changes", int(delta.get("changed_rows", 0)) > 0)
        add("delta_previous_rev0074", "rev0074" in str(delta.get("previous_archive", "")))
    except Exception as exc:
        errors.append(f"delta inspection: {exc}")

    try:
        duplicates = load(root, "data/rev0075_search_resp_duplicate_groups.json")
        add(
            "duplicate_group_rows_match_status",
            len(duplicates) == int(status.get("duplicate_hash_groups", -1)),
        )
        add(
            "duplicate_waste_matches_status",
            sum(int(row.get("wasted_bytes", 0)) for row in duplicates)
            == int(status.get("duplicate_wasted_bytes", -1)),
        )
        add(
            "duplicate_groups_sorted",
            all(
                int(duplicates[index]["wasted_bytes"])
                >= int(duplicates[index + 1]["wasted_bytes"])
                for index in range(len(duplicates) - 1)
            ),
        )
    except Exception as exc:
        errors.append(f"duplicate inventory inspection: {exc}")

    for relative, expected in ARCHIVE_HASHES.items():
        add(f"archive_hash:{relative.name}", (root / relative).is_file() and digest(root / relative) == expected)

    if (root / MANIFEST).is_file():
        manifest = check_manifest(root, errors)
    elif args.allow_missing_manifest:
        manifest = {"status": "not-yet-generated", "rows": 0}
    else:
        manifest = check_manifest(root, errors)

    files = [path for path in package_files(root) if path not in SELF_OUTPUTS]
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "root": ".",
        "payload_files_excluding_self_outputs_and_manifest": len(files),
        "payload_bytes_excluding_self_outputs_and_manifest": sum((root / path).stat().st_size for path in files),
        "required_paths": len(REQUIRED),
        "missing_required_paths": missing_required,
        "compiled_python_files": len(compile_rows),
        "compile_failures": [row for row in compile_rows if row["status"] != "pass"],
        "forbidden_paths": forbidden,
        "symlinks": symlinks,
        "status_checks": checks,
        "manifest": manifest,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
