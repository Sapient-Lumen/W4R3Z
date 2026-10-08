#!/usr/bin/env python3
"""Validate rev0867 historical canonical recovery and live-surface truth controls."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUDIT_REL = "AUDIT/OVERLAY_HISTORY_CANONICAL_RECOVERY_REV0867.json"
EXPECTED_LIVE = {
    "kind": "partial_overlay",
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 100,
    "canonical_exact_bytes_present": 4885267,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4469,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 13,
}
EXPECTED_RECOVERY = {
    "kind": "partial_recovery_overlay",
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_at_path_exact_files": 100,
    "canonical_at_path_exact_bytes": 4885267,
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 116,
    "canonical_rehydratable_bytes": 4973368,
    "canonical_unavailable_files": 4470,
    "canonical_unavailable_bytes": 101448622,
    "canonical_mismatched_files_recoverable": 16,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_missing_files_recoverable": 0,
    "canonical_missing_files_unresolved": 4469,
    "canonical_source_files": 3476,
    "canonical_source_rehydratable_files": 13,
    "recovery_inventory": "RECOVERY/canonical-index/inventory.json",
}


class ValidationError(RuntimeError):
    pass


def debug_stage(label: str) -> None:
    if os.environ.get("EV_VALIDATION_DEBUG") == "1":
        print(f"rev0867-debug: {label}", file=sys.stderr, flush=True)


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"missing or unsafe JSON file: {rel}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {rel}: {exc}")
    if not isinstance(value, dict):
        fail(f"{rel} must contain an object")
    return value


def run(command: list[str], expected_rc: int = 0) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
    )
    if proc.returncode != expected_rc:
        fail(
            f"command returned {proc.returncode}, expected {expected_rc}: {command!r}; "
            f"stdout={proc.stdout[-2000:]!r} stderr={proc.stderr[-2000:]!r}"
        )
    return proc


def run_json(command: list[str], expected_rc: int = 0) -> dict[str, Any]:
    proc = run(command, expected_rc)
    try:
        value = json.loads(proc.stdout)
    except Exception as exc:
        fail(f"command did not emit JSON: {command!r}: {exc}; stdout={proc.stdout[-2000:]!r}")
    if not isinstance(value, dict):
        fail(f"command JSON is not an object: {command!r}")
    return value


def copy_index(target: Path) -> None:
    (target / "INDEX").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "INDEX/files.csv", target / "INDEX/files.csv")


def validate_external_materialization() -> None:
    tool = str(ROOT / "scripts/recover_indexed_versions_from_overlay_history.py")
    base = [sys.executable, tool, "--inventory-only", "--json"]
    with tempfile.TemporaryDirectory(prefix="ev-history-write-") as tmp:
        target = Path(tmp)
        copy_index(target)
        first = run_json(base + ["--target-root", str(target), "--write", "--require-present"])
        if first.get("files_written") != 16 or first.get("status") != "all_recovery_objects_present":
            fail(f"external recovery did not write all 16 objects: {first}")
        second = run_json(base + ["--target-root", str(target), "--write", "--require-present"])
        if second.get("files_written") != 0 or second.get("status") != "all_recovery_objects_present":
            fail(f"external recovery is not idempotent: {second}")

    inventory = load_json("RECOVERY/canonical-index/inventory.json")
    sentinel_rel = inventory["entries"][0]["path"]
    with tempfile.TemporaryDirectory(prefix="ev-history-conflict-") as tmp:
        target = Path(tmp)
        copy_index(target)
        sentinel = target / sentinel_rel
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_bytes(b"preserve-this-nonmatching-file\n")
        result = run_json(base + ["--target-root", str(target), "--write"])
        counts = result.get("candidate_status_counts", {})
        if result.get("files_written") != 15 or counts.get("mismatch") != 1:
            fail(f"no-clobber materialization report drifted: {result}")
        if sentinel.read_bytes() != b"preserve-this-nonmatching-file\n":
            fail("materializer overwrote a non-matching target")
        strict = run_json(
            base + ["--target-root", str(target), "--fail-on-mismatch"],
            expected_rc=1,
        )
        if strict.get("status") != "candidate_target_conflict":
            fail(f"strict conflict policy did not fail explicitly: {strict}")

    with tempfile.TemporaryDirectory(prefix="ev-history-symlink-") as tmp, tempfile.TemporaryDirectory(
        prefix="ev-history-outside-"
    ) as outside_tmp:
        target = Path(tmp)
        outside = Path(outside_tmp)
        copy_index(target)
        (target / "AUDIT").symlink_to(outside, target_is_directory=True)
        proc = run(base + ["--target-root", str(target), "--write"], expected_rc=1)
        if "symlink" not in (proc.stderr + proc.stdout).lower():
            fail("symlink ancestry rejection was not explicit")
        if any(outside.rglob("*")):
            fail("materializer wrote through rejected symlink ancestry")

    overlap = run_json(base + ["--target-root", str(ROOT)], expected_rc=1)
    if "overlap" not in str(overlap.get("error", "")).lower():
        fail(f"bundle-overlap target was not rejected: {overlap}")


def validate_semantic_surface_audit(audit: dict[str, Any]) -> None:
    release = load_json("RELEASE_MANIFEST.json")
    if release.get("revision") != "rev0826":
        fail("historical release manifest revision drifted")
    sbom = load_json("SBOM/EvidenceVault-file-inventory.spdx.json")
    if sbom.get("name") != "EvidenceVault rev0826 file inventory" or len(sbom.get("files", [])) != 4585:
        fail("historical SPDX inventory identity/count drifted")
    manifest_rows = sum(1 for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines() if line.strip())
    if manifest_rows != 4588:
        fail(f"historical canonical manifest row count drifted: {manifest_rows}")
    dedupe = (ROOT / "DEDUPE_REPORT.md").read_text(encoding="utf-8")
    for text in ("Files scanned: **4584**", "Unique blobs by SHA-256: **4124**", "Duplicate copies: **460**"):
        if text not in dedupe:
            fail(f"historical dedupe declaration drifted: {text}")
    if (ROOT / "scripts/build_dedupe_report.py").exists() or (ROOT / "scripts/validate_dedupe_report.py").exists():
        fail("audit must be updated if dedupe generator/validator become present")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    refs = sorted(set(re.findall(r"(?<![A-Za-z0-9_.-])(scripts/[A-Za-z0-9_./-]+\.(?:py|sh))", makefile)))
    missing = [rel for rel in refs if not (ROOT / rel).is_file()]
    if len(refs) != 47 or len(missing) != 42:
        fail(f"canonical Makefile surface drifted: refs={len(refs)} missing={len(missing)}")
    surface = audit.get("semantic_surface_audit", {})
    if surface.get("live_overlay_authority") != "CHECKS/overlay-manifest.json plus PATCH_BUNDLE_MANIFEST.json":
        fail("audit does not name the live overlay authority")
    live_regular_files = sum(1 for path in ROOT.rglob("*") if path.is_file() and not path.is_symlink())
    if live_regular_files in {4584, 4585, 4588}:
        fail("historical canonical counts unexpectedly equal the live overlay file count")


def main() -> int:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import canonical_coverage
        import overlay_gate
        import recover_indexed_versions_from_overlay_history as history

        debug_stage("load-audit")
        audit = load_json(AUDIT_REL)
        if audit.get("status") != "exact_historical_versions_materialized_and_surface_roles_disambiguated":
            fail("audit status is not the expected completed state")

        debug_stage("discover-history")
        discovered, history_metrics = history.discover_historical_versions(ROOT)
        if len(discovered) != 16 or sum(row.size for row in discovered.values()) != 88101:
            fail(f"historical recovery totals drifted: {history_metrics}")
        unresolved = history_metrics.get("unresolved", [])
        if len(unresolved) != 1 or unresolved[0].get("path") != "README.md":
            fail(f"README.md is not the sole unresolved mismatch: {unresolved}")
        debug_stage("verify-inventory")
        stored, stored_metrics = history.verify_inventory(ROOT, discovered=discovered)
        if stored_metrics.get("recovery_object_files") != 16 or stored_metrics.get("recovery_object_bytes") != 88101:
            fail(f"stored recovery totals drifted: {stored_metrics}")
        if audit.get("substantive_recovery", {}).get("entries") != load_json("RECOVERY/canonical-index/inventory.json").get("entries"):
            fail("audit recovery entries differ from the content-addressed inventory")

        debug_stage("coverage")
        live = canonical_coverage.compute_coverage(ROOT)
        recovery = canonical_coverage.compute_recovery_availability(ROOT)
        manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
        current_revision = manifest.get("overlay_revision")
        if current_revision == "rev0867":
            if live != EXPECTED_LIVE:
                fail(f"at-path canonical coverage drifted: {live}")
            for key, expected in EXPECTED_RECOVERY.items():
                if recovery.get(key) != expected:
                    fail(f"recovery availability drift for {key}: {recovery.get(key)!r} != {expected!r}")
        else:
            # This validator protects rev0867's historical objects in later overlays.
            # Later exact byte recovery may improve live totals, so require the
            # rev0867 floor and conservation identities rather than freezing all
            # future revisions at rev0867's representation counts.
            fixed_live = {
                "kind": "partial_overlay",
                "canonical_index_files": 4586,
                "canonical_index_bytes": 106421990,
                "canonical_source_files": 3476,
            }
            for key, expected in fixed_live.items():
                if live.get(key) != expected:
                    fail(f"later-overlay fixed live invariant drift for {key}: {live.get(key)!r} != {expected!r}")
            floors = {
                "canonical_exact_files_present": 100,
                "canonical_exact_bytes_present": 4885267,
                "canonical_source_exact_files_present": 13,
            }
            for key, floor in floors.items():
                if not isinstance(live.get(key), int) or live[key] < floor:
                    fail(f"later overlay regressed below rev0867 live floor for {key}: {live.get(key)!r} < {floor}")
            if live.get("canonical_mismatched_files_present", 10**9) > 17:
                fail("later overlay increased present-path canonical mismatches above the rev0867 ceiling")
            if live.get("canonical_missing_files", 10**9) > 4469:
                fail("later overlay increased canonical missing files above the rev0867 ceiling")
            if (
                live.get("canonical_exact_files_present", 0)
                + live.get("canonical_mismatched_files_present", 0)
                + live.get("canonical_missing_files", 0)
                != live.get("canonical_index_files")
            ):
                fail("later-overlay live coverage no longer conserves the canonical index row count")
            fixed_recovery = {
                "kind": "partial_recovery_overlay",
                "canonical_index_files": 4586,
                "canonical_index_bytes": 106421990,
                "canonical_recovery_object_files": 16,
                "canonical_recovery_object_bytes": 88101,
                "canonical_mismatched_files_recoverable": 16,
                "canonical_missing_files_recoverable": 0,
                "canonical_source_files": 3476,
                "recovery_inventory": "RECOVERY/canonical-index/inventory.json",
            }
            for key, expected in fixed_recovery.items():
                if recovery.get(key) != expected:
                    fail(f"later-overlay fixed recovery invariant drift for {key}: {recovery.get(key)!r} != {expected!r}")
            recovery_floors = {
                "canonical_at_path_exact_files": 100,
                "canonical_at_path_exact_bytes": 4885267,
                "canonical_rehydratable_files": 116,
                "canonical_rehydratable_bytes": 4973368,
                "canonical_source_rehydratable_files": 13,
            }
            for key, floor in recovery_floors.items():
                if not isinstance(recovery.get(key), int) or recovery[key] < floor:
                    fail(f"later overlay regressed below rev0867 recovery floor for {key}: {recovery.get(key)!r} < {floor}")
            if recovery.get("canonical_unavailable_files", 10**9) > 4470:
                fail("later overlay increased unavailable canonical files above the rev0867 ceiling")
            if recovery.get("canonical_unavailable_bytes", 10**18) > 101448622:
                fail("later overlay increased unavailable canonical bytes above the rev0867 ceiling")
            if recovery.get("canonical_mismatched_files_unresolved", 10**9) > 1:
                fail("later overlay increased unresolved present-path mismatches above the rev0867 ceiling")
            if recovery.get("canonical_missing_files_unresolved", 10**9) > 4469:
                fail("later overlay increased unresolved missing files above the rev0867 ceiling")
        differences = canonical_coverage.compare_profile(live, manifest.get("representation_profile", {}))
        if differences:
            fail("manifest representation profile is stale: " + "; ".join(differences))
        differences = canonical_coverage.compare_recovery_profile(recovery, manifest.get("recovery_profile", {}))
        if differences:
            fail("manifest recovery profile is stale: " + "; ".join(differences))

        debug_stage("gate-list")
        listed = run_json([sys.executable, str(ROOT / "scripts/overlay_gate.py"), "--list", "--json"])
        if listed.get("representation_profile", {}).get("live_verified") is not True:
            fail("primary gate did not live-verify at-path representation")
        if listed.get("recovery_profile", {}).get("live_verified") is not True:
            fail("primary gate did not live-verify recovery availability")
        forged = json.loads(json.dumps(manifest))
        forged["recovery_profile"]["canonical_rehydratable_files"] += 1
        forged["recovery_profile"]["canonical_unavailable_files"] -= 1
        try:
            overlay_gate._load_recovery_profile(forged)
        except overlay_gate.GateError as exc:
            if "does not match live recovery availability" not in str(exc):
                fail(f"forged recovery profile failed for the wrong reason: {exc}")
        else:
            fail("primary gate accepted a forged recovery profile")

        debug_stage("semantic-audit")
        validate_semantic_surface_audit(audit)
        debug_stage("external-materialization")
        validate_external_materialization()
        debug_stage("external-materialization-done")

        debug_stage("prior-recovery")
        prior = load_json("AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.json")
        prior_rows = prior.get("recovered_files", [])
        if not isinstance(prior_rows, list) or len(prior_rows) != 81:
            fail("rev0866 recovery audit no longer pins 81 recovered files")
        import hashlib
        for row in prior_rows:
            path = ROOT / row["path"]
            if (
                not path.is_file()
                or path.stat().st_size != row["bytes"]
                or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]
            ):
                fail(f"rev0866 recovered file drifted: {row['path']}")
        rights = manifest.get("active_rights_status", {})
        if rights.get("root_license_or_notice_present") is not False:
            fail("root rights blocker was changed without an owner decision")
        proofcore = manifest.get("active_proofcore_payload_status", {})
        if proofcore.get("streamfold_full_missing") != 17 or proofcore.get("streamfold_minimum_missing") != 4:
            fail("StreamFold absence boundary drifted without payload recovery")

        debug_stage("done")
        print("overlay-history-canonical-recovery-rev0867: OK")
        return 0
    except ValidationError as exc:
        print(f"overlay-history-canonical-recovery-rev0867: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"overlay-history-canonical-recovery-rev0867: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
