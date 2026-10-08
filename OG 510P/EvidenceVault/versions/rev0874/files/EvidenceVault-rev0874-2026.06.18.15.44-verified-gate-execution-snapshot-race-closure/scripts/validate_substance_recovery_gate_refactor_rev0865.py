#!/usr/bin/env python3
"""Validate rev0865 payload recovery, coverage honesty, and immutable gate behavior."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
README_REL = "sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md"
README_SHA = "0f7174a89094f7695b899fad71c2e6d0fb12cd6041734d779aacd8a8bfe400c2"
README_BYTES = 356744
LICENSE_REL = "sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE"
LICENSE_SHA = "0382b0057770ca05e9c350a50aa3b1c1fea84da0bc81d723bf00b9aa841be58a"
LICENSE_BYTES = 12227
EXPECTED_COVERAGE = {
    "indexed_files": 4586,
    "indexed_bytes": 106421990,
    "exact_files": 19,
    "exact_bytes": 4338844,
    "mismatch_files": 17,
    "missing_files": 4550,
    "source_files": 3476,
    "source_exact_files": 1,
}
COMPANIONS = {
    "sources/pact/PACT_workdir/eval_real_registry_scan/out_summary.json": (
        1496,
        "23e281bb8558604ad6edab4e52f510388c3ae362fbedd4bbd096fc9105818ef0",
    ),
    "sources/pact/PACT_workdir/eval_real_registry_scan/scan_servers_readme.py": (
        11221,
        "2ae3f10fdbf92ade1eb759ffde18c087eeb1ac52403ce67610c3dd67d504cec7",
    ),
    "sources/pact/PACT_workdir/eval_real_registry_scan/table_snippet.tex": (
        520,
        "320ed3c4cb3019d8fca79162676c30290934f730bd14901f4f9fb85f9a4711b2",
    ),
}


def fail(message: str) -> None:
    print(f"substance-recovery-gate-refactor-rev0865: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256_file(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    require(path.is_file() and not path.is_symlink(), f"missing JSON: {rel}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")
    require(isinstance(value, dict), f"JSON root must be object: {rel}")
    return value


def canonical_coverage() -> dict[str, Any]:
    with (ROOT / "INDEX/files.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    exact = mismatch = missing = 0
    exact_bytes = indexed_bytes = 0
    source_files = source_exact = 0
    statuses: dict[str, dict[str, Any]] = {}
    for row in rows:
        rel = row["path"]
        size = int(row["size"])
        indexed_bytes += size
        is_source = row.get("category") == "sources"
        if is_source:
            source_files += 1
        target = ROOT / rel
        if not target.is_file() or target.is_symlink():
            status = "missing"
            missing += 1
        else:
            actual_size = target.stat().st_size
            actual_sha = sha256_file(target)
            if actual_size == size and actual_sha == row["sha256"]:
                status = "exact"
                exact += 1
                exact_bytes += size
                if is_source:
                    source_exact += 1
            else:
                status = "mismatch"
                mismatch += 1
        statuses[rel] = {
            "status": status,
            "bytes": size,
            "sha256": row["sha256"],
        }
    return {
        "indexed_files": len(rows),
        "indexed_bytes": indexed_bytes,
        "exact_files": exact,
        "exact_bytes": exact_bytes,
        "mismatch_files": mismatch,
        "missing_files": missing,
        "source_files": source_files,
        "source_exact_files": source_exact,
        "statuses": statuses,
    }


def snapshot_bundle() -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for path in sorted(ROOT.rglob("*")):
        require(not path.is_symlink(), f"bundle contains symlink: {path.relative_to(ROOT)}")
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            result[rel] = (path.stat().st_size, sha256_file(path))
    return result


def run_gate_behavior_tests() -> None:
    forbidden = ROOT / "VALIDATION" / "rev0865-forbidden-in-bundle-report.json"
    forbidden.unlink(missing_ok=True)
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/overlay_gate.py",
            "--list",
            "--report",
            str(forbidden),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        timeout=60,
    )
    require(proc.returncode == 2, "gate did not reject an in-bundle report target")
    require(not forbidden.exists(), "gate created the forbidden in-bundle report")
    require("outside the immutable overlay bundle" in proc.stderr, "gate rejection is not diagnostic")

    before = snapshot_bundle()
    with tempfile.TemporaryDirectory(prefix="ev-rev0865-gate-report-") as temp_dir:
        report = Path(temp_dir) / "selected-check-report.json"
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/overlay_gate.py",
                "--check",
                "overlay-chain",
                "--report",
                str(report),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=240,
        )
        require(proc.returncode == 0, f"selected gate run failed: {proc.stderr or proc.stdout}")
        require(report.is_file() and not report.is_symlink(), "external report was not created")
        require((report.stat().st_mode & 0o777) == 0o644, "external report mode is not 0644")
        data = json.loads(report.read_text(encoding="utf-8"))
        require(data.get("scope") == "selected_checks", "selected run scope is wrong")
        require(data.get("full_gate") is False, "selected run is mislabeled as a full gate")
        require(data.get("integrity_forced") is True, "selected run did not force integrity")
        require(data.get("selected_configured_check_ids") == ["overlay-integrity", "overlay-chain"], "selected check plan is wrong")
        require(data.get("execution_count") == 3, "selected run did not execute integrity pre/main/post")
        phases = [(row.get("id"), row.get("phase"), row.get("status")) for row in data.get("results", [])]
        require(
            phases
            == [
                ("overlay-integrity", "preflight", "pass"),
                ("overlay-chain", "main", "pass"),
                ("overlay-integrity", "postflight", "pass"),
            ],
            f"unexpected gate phases: {phases}",
        )
        require("NOT A FULL GATE" in proc.stdout, "plain selected-check output lacks the partial-scope warning")
    after = snapshot_bundle()
    require(before == after, "gate/report execution mutated the immutable overlay bundle")


def main() -> int:
    require("rev0865" in ROOT.name, "archive root does not identify rev0865")

    readme = ROOT / README_REL
    require(readme.stat().st_size == README_BYTES, "recovered README byte count mismatch")
    require(sha256_file(readme) == README_SHA, "recovered README digest mismatch")
    license_path = ROOT / LICENSE_REL
    require(license_path.stat().st_size == LICENSE_BYTES, "recovered LICENSE byte count mismatch")
    require(sha256_file(license_path) == LICENSE_SHA, "recovered LICENSE digest mismatch")
    license_text = license_path.read_text(encoding="utf-8")
    require(
        "Documentation contributions (excluding specifications) are licensed under CC-BY-4.0."
        in license_text,
        "adjacent LICENSE lacks the documentation term used by the file-level conclusion",
    )
    require("## 📜 License" in readme.read_text(encoding="utf-8"), "README payload content marker missing")

    coverage = canonical_coverage()
    for key, expected in EXPECTED_COVERAGE.items():
        require(coverage[key] == expected, f"canonical coverage {key}: {coverage[key]} != {expected}")
    require(coverage["statuses"][README_REL]["status"] == "exact", "README is not exact in canonical index")
    for rel, (size, digest) in COMPANIONS.items():
        require(coverage["statuses"][rel] == {"status": "missing", "bytes": size, "sha256": digest}, f"companion status changed: {rel}")

    audit = load_json("AUDIT/REPRESENTATION_COVERAGE_GATE_IMMUTABILITY_REV0865.json")
    audit_coverage = audit.get("canonical_index_coverage", {})
    require(audit_coverage.get("indexed_files") == EXPECTED_COVERAGE["indexed_files"], "audit indexed file count mismatch")
    require(audit_coverage.get("exact_present", {}).get("files") == EXPECTED_COVERAGE["exact_files"], "audit exact file count mismatch")
    require(audit_coverage.get("mismatched_present", {}).get("files") == EXPECTED_COVERAGE["mismatch_files"], "audit mismatch count mismatch")
    require(audit_coverage.get("missing", {}).get("files") == EXPECTED_COVERAGE["missing_files"], "audit missing count mismatch")
    require(audit.get("rev0865_payload_recovery", {}).get("rev0865_embedded") is True, "audit does not record embedded README")

    recovery = load_json("RIGHTS/MCP_SERVERS_README_RECOVERY_REV0865.json")
    require(recovery.get("recovered_file", {}).get("sha256") == README_SHA, "recovery evidence README digest mismatch")
    require(recovery.get("file_level_rights", {}).get("license_concluded") == "CC-BY-4.0", "file-level license conclusion missing")
    require(recovery.get("component_effect", {}).get("component_license_concluded") == "NOASSERTION", "PACT aggregate conclusion was broadened")

    ledger = load_json("RIGHTS/component_license_ledger.json")
    require(ledger.get("root_license_or_notice_file_present") is False, "root rights status changed without a root file")
    pact = next((row for row in ledger.get("components", []) if row.get("component_id") == "pact"), None)
    require(isinstance(pact, dict), "PACT component missing from rights ledger")
    require(pact.get("license_concluded") == "NOASSERTION", "PACT component conclusion was over-broadened")
    conclusions = ledger.get("file_level_license_conclusions")
    require(isinstance(conclusions, list) and len(conclusions) == 1, "file-level conclusion list is missing or non-unique")
    require(conclusions[0].get("path") == README_REL and conclusions[0].get("license_concluded") == "CC-BY-4.0", "ledger file-level conclusion mismatch")

    manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
    require(manifest.get("overlay_revision") == "rev0865", "patch bundle revision mismatch")
    require(manifest.get("archive_root") == ROOT.name, "patch bundle archive_root mismatch")
    require(manifest.get("archive_name") == ROOT.name + ".zip", "patch bundle archive_name mismatch")
    profile = manifest.get("representation_profile", {})
    require(profile.get("kind") == "partial_overlay", "representation profile is not partial_overlay")
    require(profile.get("canonical_index_files") == EXPECTED_COVERAGE["indexed_files"], "manifest indexed count mismatch")
    require(profile.get("canonical_exact_files_present") == EXPECTED_COVERAGE["exact_files"], "manifest exact count mismatch")
    require(profile.get("canonical_mismatched_files_present") == EXPECTED_COVERAGE["mismatch_files"], "manifest mismatch count mismatch")
    require(profile.get("canonical_missing_files") == EXPECTED_COVERAGE["missing_files"], "manifest missing count mismatch")
    gate_ids = [row.get("id") for row in manifest.get("gate_checks", [])]
    require(
        gate_ids
        == [
            "overlay-integrity",
            "substance-recovery-gate-refactor-rev0865",
            "overlay-chain",
            "streamfold-archive-search",
        ],
        f"unexpected active gate configuration: {gate_ids}",
    )

    require((ROOT / "README.md").read_text(encoding="utf-8").startswith("# EvidenceVault rev0865"), "README is not current-revision first")
    require((ROOT / "OVERLAY_COMMANDS.md").read_text(encoding="utf-8").startswith("# EvidenceVault rev0865"), "overlay commands are not current-revision first")

    run_gate_behavior_tests()

    print("substance-recovery-gate-refactor-rev0865: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
