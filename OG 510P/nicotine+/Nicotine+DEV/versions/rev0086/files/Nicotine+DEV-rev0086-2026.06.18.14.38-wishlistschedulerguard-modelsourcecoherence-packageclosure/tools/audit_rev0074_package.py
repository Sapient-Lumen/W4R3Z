#!/usr/bin/env python3
"""Fail-closed package coherence audit for rev0074."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
REVISION = "rev0074"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
MANIFEST = Path("handoff/rev0074/MANIFEST.sha256")
SELF_OUTPUTS = {
    Path("data/rev0074_package_preflight.json"),
    Path("evidence/rev0074-package-validation.md"),
}
REQUIRED = (
    Path("README.md"),
    Path("REVISION.txt"),
    Path("docs/START-HERE.md"),
    Path("docs/PB01-CURRENT-DISPOSITION-REV0074.md"),
    Path("docs/PB01-REACHABILITY-AND-COMPATIBILITY-AUDIT-REV0074.md"),
    Path("docs/PB01-ARTIFACT-COHERENCE-REFACTOR-REV0074.md"),
    Path("docs/CLAIM-EVIDENCE-LADDER-REV0074.md"),
    Path("docs/PACKET-DISPOSITION-LEDGER-REV0074.md"),
    Path("docs/SUPERSEDED-PACKET-INDEX-REV0074.md"),
    Path("docs/PACKAGE-COHERENCE-GATE-REV0074.md"),
    Path("data/current_packet_dispositions.json"),
    Path("data/rev0074_packet_dispositions.json"),
    Path("data/rev0074_pb01_disposition_summary.json"),
    Path("data/rev0074_pb01_test_matrix.csv"),
    Path("data/rev0074_pb01_source_invariants.csv"),
    Path("data/rev0074_pb01_reachability_matrix.csv"),
    Path("data/rev0074_pb01_artifact_inventory.csv"),
    Path("data/rev0074_packet_status_audit.json"),
    Path("data/rev0074_delta_inventory.csv"),
    Path("data/rev0074_delta_inventory.json"),
    Path("data/rev0074_package_preflight.json"),
    Path("evidence/rev0074-package-validation.md"),
    Path("evidence/rev0074-pb01-upstream-history.md"),
    Path("evidence/rev0074-pb01-public-overlap.md"),
    Path("evidence/rev0074-packet-status-audit.md"),
    Path("report_drafts/PB01-CURRENT-STATUS-REV0074.md"),
    Path("maintainer_artifacts/pb01/pb01_harness.py"),
    Path("maintainer_artifacts/pb01/test_pb01_current_behavior_witness.py"),
    Path("maintainer_artifacts/pb01/test_pb01_race_compatibility_controls.py"),
    Path("maintainer_artifacts/pb01/test_pb01_rev0038_split_counterexample.py"),
    Path("maintainer_artifacts/pb01/test_pb01_origin_aware_experiment.py"),
    Path("tools/probe_rev0074_pb01_disposition.py"),
    Path("tools/apply_pb01_origin_aware_patch_rev0074.py"),
    Path("tools/audit_rev0074_packet_status.py"),
    Path("tools/build_rev0074_delta_inventory.py"),
    Path("tools/audit_rev0074_package.py"),
    Path("handoff/rev0074/README.md"),
    Path("handoff/rev0074/REVISION-SUMMARY.md"),
    Path("handoff/rev0074/PB01-RESEARCH-DISPOSITION.md"),
)
ARCHIVE_HASHES = {
    Path("docs/archive/rev0073-active-pb01/probe_rev0010_pb01_peer_binding.py"): "9c8ca117d9b485407bb6e5f0fc113cf5065df974672dbb26ff35f9e6563be0da",
    Path("docs/archive/rev0073-active-pb01/test_peer_connection_primary_election_reproducer.py"): "278003b1cab84e79f8a86ef89d09104871f6fc5c0fde4fbd2e91636cc0c93f5a",
    Path("docs/archive/rev0073-active-pb01/test_peer_connection_primary_election_fixed_regression.py"): "5b02cbcab457fb964319dc57d5078d8be9444ca72ae71fe04893f633232fc8bb",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def package_files(root: Path) -> list[Path]:
    return sorted(
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink() and p.relative_to(root) != MANIFEST
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
            value, rel = line.split("  ", 1)
        except ValueError:
            malformed.append(f"line {lineno}")
            continue
        rp = Path(rel)
        if rp in rows:
            malformed.append(f"duplicate {rel}")
        rows[rp] = value
    actual = set(package_files(root))
    listed = set(rows)
    missing = sorted(actual - listed)
    extra = sorted(listed - actual)
    mismatched = sorted(r for r in actual & listed if digest(root / r) != rows[r])
    if malformed: errors.append(f"malformed manifest: {malformed[:5]}")
    if missing: errors.append(f"manifest missing {len(missing)} paths: {missing[:5]}")
    if extra: errors.append(f"manifest extra {len(extra)} paths: {extra[:5]}")
    if mismatched: errors.append(f"manifest mismatches {len(mismatched)} paths: {mismatched[:5]}")
    ok = not (malformed or missing or extra or mismatched)
    return {
        "status": "pass" if ok else "fail",
        "rows": len(rows),
        "missing": [str(x) for x in missing],
        "extra": [str(x) for x in extra],
        "mismatched": [str(x) for x in mismatched],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--allow-missing-manifest", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    missing_required = [str(p) for p in REQUIRED if not (root / p).is_file()]
    if missing_required:
        errors.append(f"missing required paths: {missing_required}")
    revision = (root / "REVISION.txt").read_text(encoding="utf-8").strip() if (root / "REVISION.txt").is_file() else ""
    if revision != REVISION:
        errors.append(f"revision {revision!r} != {REVISION!r}")

    forbidden: list[str] = []
    symlinks: list[str] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if p.is_symlink():
            symlinks.append(str(rel))
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in rel.parts):
            forbidden.append(str(rel))
        elif p.is_file() and p.suffix in {".pyc", ".pyo"}:
            forbidden.append(str(rel))
        elif p.is_dir() and p.name == "pynicotine":
            forbidden.append(str(rel))
        elif p.is_file() and "nicotine-source" in p.name.lower():
            forbidden.append(str(rel))
    if forbidden: errors.append(f"forbidden cache/source paths: {forbidden[:10]}")
    if symlinks: errors.append(f"symlinks: {symlinks[:10]}")

    compile_rows: list[dict[str, str]] = []
    candidates = set(root.glob("tools/*rev0074*.py")) | set(root.glob("maintainer_artifacts/pb01/*.py"))
    for p in sorted(candidates):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        try:
            compile(p.read_text(encoding="utf-8"), str(rel), "exec")
            status, message = "pass", ""
        except Exception as exc:
            status, message = "fail", f"{type(exc).__name__}: {exc}"
            errors.append(f"compile {rel}: {message}")
        compile_rows.append({"path": str(rel), "status": status, "error": message})

    checks: list[dict[str, Any]] = []
    def add(name: str, value: bool) -> None:
        checks.append({"check": name, "pass": bool(value)})
        if not value: errors.append(f"failed check: {name}")

    try:
        summary = load(root, "data/rev0074_pb01_disposition_summary.json")
        add("pb01_summary_pass", summary.get("status") == "pass")
        add("exact_current_ref", summary.get("exact_current_ref_match") is True)
        add("expected_ref", summary.get("expected_ref") == EXPECTED_REF)
        add("classified_12_of_12", (summary.get("test_expectations_passed"), summary.get("test_expectations_total")) == (12, 12))
        add("source_invariants_7_of_7", (summary.get("source_invariants_passed"), summary.get("source_invariants_total")) == (7, 7))
        add("selected_patch_null", summary.get("selected_patch") is None)
        add("upstream_unit_parity", summary.get("upstream_unit_parity") is True)
        units = summary.get("upstream_units", [])
        add("three_unit_states", len(units) == 3)
        add("units_58_pass_1_skip", all((u.get("passed"), u.get("skipped"), u.get("failed"), u.get("status")) == (58, 1, 0, "pass") for u in units))
        add("i18n_exclusion_recorded", all(u.get("i18n_excluded") is True and u.get("msgfmt_available") is False for u in units))
        for row in summary.get("experiments", []):
            p = root / str(row.get("artifact"))
            add(f"experiment_hash:{row.get('state')}", p.is_file() and digest(p) == row.get("sha256") and row.get("status") == "pass")
    except Exception as exc:
        errors.append(f"summary inspection: {exc}")

    try:
        status = load(root, "data/rev0074_packet_status_audit.json")
        add("packet_status_pass", status.get("status") == "pass")
        add("packet_status_active_44_of_44", (status.get("active_checks_passed"), status.get("active_checks_total")) == (44, 44))
        add("packet_status_idempotent", status.get("self_reference_stability") == "pass")
        add("packet_status_no_pb01_patch", status.get("pb01a_selected_patch") is None and status.get("pb01b_selected_patch") is None)
    except Exception as exc:
        errors.append(f"packet status inspection: {exc}")

    try:
        ledger = load(root, "data/current_packet_dispositions.json")
        by_id = {x.get("packet_id"): x for x in ledger.get("packets", [])}
        add("ledger_pb01a_open", by_id.get("PB-01A/U-168", {}).get("status") == "open-protocol-hardening-research")
        add("ledger_pb01b_retired", by_id.get("PB-01B/U-176", {}).get("status") == "retired-as-defect-on-current-evidence")
        add("ledger_pb01_no_selected_patch", by_id.get("PB-01A/U-168", {}).get("selected_patch") is None and by_id.get("PB-01B/U-176", {}).get("selected_patch") is None)
    except Exception as exc:
        errors.append(f"ledger inspection: {exc}")

    try:
        delta = load(root, "data/rev0074_delta_inventory.json")
        add("delta_revision", delta.get("revision") == REVISION)
        add("delta_has_changes", int(delta.get("changed_rows", 0)) > 0)
    except Exception as exc:
        errors.append(f"delta inspection: {exc}")

    for rel, expected in ARCHIVE_HASHES.items():
        add(f"archive_hash:{rel.name}", (root / rel).is_file() and digest(root / rel) == expected)

    if (root / MANIFEST).is_file():
        manifest = check_manifest(root, errors)
    elif args.allow_missing_manifest:
        manifest = {"status": "not-yet-generated", "rows": 0}
    else:
        manifest = check_manifest(root, errors)

    files = [p for p in package_files(root) if p not in SELF_OUTPUTS]
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "root": ".",
        "payload_files_excluding_self_outputs_and_manifest": len(files),
        "payload_bytes_excluding_self_outputs_and_manifest": sum((root / p).stat().st_size for p in files),
        "required_paths": len(REQUIRED),
        "missing_required_paths": missing_required,
        "compiled_python_files": len(compile_rows),
        "compile_failures": [x for x in compile_rows if x["status"] != "pass"],
        "forbidden_paths": forbidden,
        "symlinks": symlinks,
        "status_checks": checks,
        "manifest": manifest,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
