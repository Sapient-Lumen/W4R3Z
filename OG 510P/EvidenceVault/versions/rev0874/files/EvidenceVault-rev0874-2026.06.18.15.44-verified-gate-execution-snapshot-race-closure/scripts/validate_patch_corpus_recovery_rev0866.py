#!/usr/bin/env python3
"""Validate rev0866 exact patch-corpus recovery and live-coverage controls."""
from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CURRENT_PATCH = "rev0865-to-rev0866-overlay.patch"
TAIL_PATCH_RE = re.compile(r"^rev(?P<from>\d{4})-to-rev\d{4}-overlay\.patch$")
AUDIT_REL = "AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.json"
EXPECTED_METRICS = {
    "patch_files_scanned": 27,
    "patch_sections_scanned": 1038,
    "contiguous_new_side_streams": 616,
    "indexed_contiguous_new_side_streams": 129,
    "exact_index_verified_candidate_paths": 88,
}
EXPECTED_COVERAGE = {
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


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def clean_rel(text: Any, label: str) -> str:
    if not isinstance(text, str) or not text or "\x00" in text or "\\" in text:
        fail(f"{label} must be a non-empty POSIX relative path")
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        fail(f"{label} is unsafe: {text!r}")
    return path.as_posix()


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / clean_rel(rel, "JSON path")
    if path.is_symlink() or not path.is_file():
        fail(f"missing or unsafe JSON file: {rel}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {rel}: {exc}")
    if not isinstance(value, dict):
        fail(f"{rel} must contain a JSON object")
    return value


def run_json(command: list[str], *, expected_rc: int = 0) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    if proc.returncode != expected_rc:
        fail(
            f"command returned {proc.returncode}, expected {expected_rc}: {command!r}; "
            f"stdout={proc.stdout[-2000:]!r} stderr={proc.stderr[-2000:]!r}"
        )
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        fail(f"command did not emit JSON: {command!r}: {exc}; stdout={proc.stdout[-2000:]!r}")
    if not isinstance(payload, dict):
        fail(f"command JSON must be an object: {command!r}")
    return payload


def copy_index(target: Path) -> None:
    (target / "INDEX").mkdir(parents=True)
    shutil.copy2(ROOT / "INDEX/files.csv", target / "INDEX/files.csv")



def historical_tail_patch_names() -> list[str]:
    """Exclude rev0866's own edge and all later edges from its frozen corpus."""
    names: list[str] = []
    for path in sorted((ROOT / "PATCHES").glob("*.patch")):
        match = TAIL_PATCH_RE.fullmatch(path.name)
        if match is not None and int(match.group("from")) >= 865:
            names.append(path.name)
    if CURRENT_PATCH not in names:
        fail(f"historical current patch is absent: {CURRENT_PATCH}")
    return names

def validate_external_recovery() -> None:
    recovery = str(ROOT / "scripts/recover_indexed_files_from_patches.py")
    base = [sys.executable, recovery]
    for patch_name in historical_tail_patch_names():
        base.extend(["--exclude-patch", patch_name])
    base.append("--json")
    with tempfile.TemporaryDirectory(prefix="ev-recovery-write-") as tmp_text:
        target = Path(tmp_text)
        copy_index(target)
        first = run_json(base + ["--target-root", str(target), "--write", "--require-present"])
        if first.get("files_written") != 88 or first.get("status") != "all_exact_candidates_present":
            fail(f"external exact recovery did not write all 88 candidates: {first}")
        second = run_json(base + ["--target-root", str(target), "--write", "--require-present"])
        if second.get("files_written") != 0 or second.get("status") != "all_exact_candidates_present":
            fail(f"external recovery is not idempotent: {second}")

    with tempfile.TemporaryDirectory(prefix="ev-recovery-mismatch-") as tmp_text:
        target = Path(tmp_text)
        copy_index(target)
        sentinel_rel = "AUDIT/GATE_DIAGNOSTICS_REFACTOR_REV0836.json"
        sentinel = target / sentinel_rel
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"do-not-overwrite\n")
        result = run_json(base + ["--target-root", str(target), "--write"])
        counts = result.get("candidate_status_counts", {})
        if result.get("files_written") != 87 or counts.get("mismatch") != 1 or counts.get("missing") != 0:
            fail(f"no-clobber mismatch test returned unexpected report: {result}")
        if sentinel.read_bytes() != b"do-not-overwrite\n":
            fail("recovery tool overwrote a non-matching existing file")
        strict = run_json(
            base + ["--target-root", str(target), "--fail-on-mismatch"],
            expected_rc=1,
        )
        if strict.get("status") != "candidate_target_conflict":
            fail(f"--fail-on-mismatch did not expose conflict: {strict}")

    with tempfile.TemporaryDirectory(prefix="ev-recovery-symlink-") as tmp_text, tempfile.TemporaryDirectory(
        prefix="ev-recovery-outside-"
    ) as outside_text:
        target = Path(tmp_text)
        outside = Path(outside_text)
        copy_index(target)
        (target / "AUDIT").symlink_to(outside, target_is_directory=True)
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            base[:-1] + ["--target-root", str(target), "--write", "--json"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
        if proc.returncode == 0 or "symlink" not in proc.stderr.lower():
            fail(f"symlink traversal was not rejected: rc={proc.returncode} stderr={proc.stderr!r}")
        if any(outside.rglob("*")):
            fail("symlink rejection occurred after writing outside the target root")


def main() -> int:
    try:
        import canonical_coverage
        import overlay_gate
        import recover_indexed_files_from_patches as recovery

        audit = load_json(AUDIT_REL)
        if audit.get("status") != "substantive_exact_recovery_complete_for_preexisting_patch_candidates":
            fail("audit status is not the expected completed recovery state")

        current_patch_path = ROOT / "PATCHES" / CURRENT_PATCH
        if current_patch_path.is_symlink() or not current_patch_path.is_file():
            fail(f"current overlay patch is absent or unsafe: PATCHES/{CURRENT_PATCH}")

        tail_patch_names = historical_tail_patch_names()
        candidates, metrics = recovery.discover_candidates(
            ROOT, exclude_patch_names=tail_patch_names
        )
        for key, value in EXPECTED_METRICS.items():
            if metrics.get(key) != value:
                fail(f"pre-rev0866 patch metric drift for {key}: {metrics.get(key)!r} != {value}")
        if (
            metrics.get("patch_files_available") != 27 + len(tail_patch_names)
            or metrics.get("patch_files_excluded") != len(tail_patch_names)
        ):
            fail(f"historical tail-patch exclusion accounting is wrong: {metrics}")

        recovered_rows = audit.get("recovered_files")
        already_rows = audit.get("already_exact_candidates")
        divergent_rows = audit.get("revision_divergent_candidates_not_overwritten")
        if not isinstance(recovered_rows, list) or len(recovered_rows) != 81:
            fail("audit must pin exactly 81 recovered rows")
        if not isinstance(already_rows, list) or len(already_rows) != 2:
            fail("audit must pin exactly 2 already-exact candidates")
        if not isinstance(divergent_rows, list) or len(divergent_rows) != 5:
            fail("audit must pin exactly 5 revision-divergent candidates")

        partitions: dict[str, set[str]] = {}
        for label, rows in (
            ("recovered", recovered_rows),
            ("already", already_rows),
            ("divergent", divergent_rows),
        ):
            paths: set[str] = set()
            for index, row in enumerate(rows):
                if not isinstance(row, dict):
                    fail(f"{label} row {index} is not an object")
                rel = clean_rel(row.get("path"), f"{label} row {index} path")
                if rel in paths:
                    fail(f"duplicate {label} path: {rel}")
                paths.add(rel)
                candidate = candidates.get(rel)
                if candidate is None:
                    fail(f"audit path is not recoverable from the preexisting patch corpus: {rel}")
                if row.get("bytes") != candidate.size or row.get("sha256") != candidate.sha256:
                    fail(f"audit candidate identity drift: {rel}")
                if row.get("origins") != sorted(candidate.origins):
                    fail(f"audit recovery-origin drift for {rel}: {candidate.origins}")
                if label == "recovered" and not all(
                    origin.startswith("PATCHES/rev0826-to-rev0840-cumulative.patch:")
                    for origin in candidate.origins
                ):
                    fail(f"recovered path lacks the pinned cumulative-patch origin: {rel}")
            partitions[label] = paths
        if any(partitions[a] & partitions[b] for a, b in (("recovered", "already"), ("recovered", "divergent"), ("already", "divergent"))):
            fail("candidate disposition partitions overlap")
        if set(candidates) != partitions["recovered"] | partitions["already"] | partitions["divergent"]:
            fail("audit candidate partitions do not exactly cover the 88-path candidate set")

        for rel in sorted(partitions["recovered"] | partitions["already"]):
            if recovery.candidate_status(ROOT, candidates[rel]) != "exact":
                fail(f"expected exact recovered candidate is not exact: {rel}")
        for rel in sorted(partitions["divergent"]):
            if recovery.candidate_status(ROOT, candidates[rel]) != "mismatch":
                fail(f"revision-divergent candidate was overwritten or disappeared: {rel}")

        source_recovered = [row for row in recovered_rows if row.get("source_payload")]
        if len(source_recovered) != 12 or sum(int(row["bytes"]) for row in source_recovered) != 13568:
            fail("source recovery count or bytes drifted")
        if sum(int(row["bytes"]) for row in recovered_rows) != 546423:
            fail("total recovered byte count drifted")
        for row in recovered_rows:
            rel = row["path"]
            if rel.endswith(".json"):
                try:
                    json.loads((ROOT / rel).read_text(encoding="utf-8"))
                except Exception as exc:
                    fail(f"recovered JSON payload is invalid: {rel}: {exc}")

        live = canonical_coverage.compute_coverage(ROOT)
        fixed = (
            "kind",
            "canonical_index_files",
            "canonical_index_bytes",
            "canonical_mismatched_files_present",
            "canonical_source_files",
        )
        for key in fixed:
            if live.get(key) != EXPECTED_COVERAGE[key]:
                fail(f"later revision changed fixed rev0866 coverage invariant {key}")
        monotonic = {
            "canonical_exact_files_present": "up",
            "canonical_exact_bytes_present": "up",
            "canonical_missing_files": "down",
            "canonical_source_exact_files_present": "up",
        }
        for key, direction in monotonic.items():
            actual = live.get(key)
            baseline = EXPECTED_COVERAGE[key]
            if not isinstance(actual, int) or (direction == "up" and actual < baseline) or (direction == "down" and actual > baseline):
                fail(f"later revision regressed rev0866 coverage invariant {key}: {actual!r} vs {baseline!r}")
        if audit.get("coverage_after") != EXPECTED_COVERAGE:
            fail("historical rev0866 audit coverage_after drifted")
        manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
        differences = canonical_coverage.compare_profile(live, manifest.get("representation_profile", {}))
        if differences:
            fail("manifest representation profile is stale: " + "; ".join(differences))

        listed = run_json([sys.executable, str(ROOT / "scripts/overlay_gate.py"), "--list", "--json"])
        if listed.get("representation_profile", {}).get("live_verified") is not True:
            fail("primary gate did not mark representation profile as live-verified")
        forged = json.loads(json.dumps(manifest))
        forged["representation_profile"]["canonical_exact_files_present"] += 1
        forged["representation_profile"]["canonical_missing_files"] -= 1
        try:
            overlay_gate._load_representation_profile(forged)
        except overlay_gate.GateError as exc:
            if "does not match live canonical coverage" not in str(exc):
                fail(f"forged profile failed for the wrong reason: {exc}")
        else:
            fail("primary gate accepted a forged representation profile")

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        refs = sorted(
            set(
                re.findall(
                    r"(?<![A-Za-z0-9_.-])(scripts/[A-Za-z0-9_./-]+\.(?:py|sh))",
                    makefile,
                )
            )
        )
        missing_refs = [rel for rel in refs if not (ROOT / rel).is_file()]
        command_audit = audit.get("canonical_makefile_command_surface_audit", {})
        if len(refs) != 47 or len(missing_refs) != 42:
            fail(f"Makefile command-surface counts drifted: refs={len(refs)} missing={len(missing_refs)}")
        if command_audit.get("missing_paths") != missing_refs:
            fail("audit missing Makefile command paths do not match live tree")
        if command_audit.get("missing_paths_recovered_this_revision") != []:
            fail("audit incorrectly claims a missing Makefile command was recovered")

        rights = manifest.get("active_rights_status", {})
        if rights.get("root_license_or_notice_present") is not False:
            fail("historical RIGHTS/NOTICE.draft was incorrectly promoted to a root notice")
        if manifest.get("active_publication_status") != "publication_blocked_pending_root_and_component_rights_decisions":
            fail("publication blocker changed without a rights decision")

        validate_external_recovery()
        print("patch-corpus-recovery-rev0866: OK")
        return 0
    except ValidationError as exc:
        print(f"patch-corpus-recovery-rev0866: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"patch-corpus-recovery-rev0866: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
