#!/usr/bin/env python3
"""Validate rev0870 exact OCF recoveries and descriptor-bound coverage reads."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    import canonical_coverage as coverage
    import recover_indexed_low_entropy_constants_rev0870 as recovery_engine
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass

REVISION = "rev0870"
RECOVERED: dict[str, bytes] = {
    "sources/ocf_llm/examples/discovery_sdt_demo_v247/output.txt": b"hello SDT\n",
    "sources/ocf_llm/examples/dsc_summary_v1.json": b'{"n":64,"x":0}',
    "sources/ocf_llm/examples/dsc_buc_summary_v1.json": b'{"n":64,"x":0}',
    "sources/ocf_llm/examples/dsc_cbb_summary_v1.json": b'{"n":128,"x":0}',
}
EXPECTED_COVERAGE = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 107,
    "canonical_exact_bytes_present": 4885396,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4462,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 20,
}
EXPECTED_RECOVERY = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_at_path_exact_files": 107,
    "canonical_at_path_exact_bytes": 4885396,
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 123,
    "canonical_rehydratable_bytes": 4973497,
    "canonical_unavailable_files": 4463,
    "canonical_unavailable_bytes": 101448493,
    "canonical_mismatched_files_recoverable": 16,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_missing_files_recoverable": 0,
    "canonical_missing_files_unresolved": 4462,
    "canonical_source_files": 3476,
    "canonical_source_rehydratable_files": 20,
}


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_manifest() -> dict:
    try:
        value = json.loads((ROOT / "PATCH_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read PATCH_BUNDLE_MANIFEST.json: {exc}")
    if not isinstance(value, dict):
        fail("PATCH_BUNDLE_MANIFEST.json must be an object")
    return value


def assert_exact_recoveries() -> None:
    rows = {row["path"]: row for row in coverage.load_index(ROOT)}
    for rel, expected in RECOVERED.items():
        row = rows.get(rel)
        digest = hashlib.sha256(expected).hexdigest()
        if row is None or row["size"] != len(expected) or row["sha256"] != digest:
            fail(f"recipe does not equal canonical index identity: {rel}")
        try:
            snap = coverage.snapshot_regular_file(ROOT, rel, f"rev0870 recovery {rel}", capture_bytes=True)
        except Exception as exc:
            fail(f"cannot snapshot recovered path {rel}: {exc}")
        if snap["bytes"] != expected or snap["size"] != len(expected) or snap["sha256"] != digest:
            fail(f"recovered bytes are not exact: {rel}")

    report = recovery_engine.verify_recipes(ROOT, write=False)
    if report.get("recovered_files") != 4 or report.get("recovered_bytes") != 53:
        fail("recovery engine did not verify the exact four-file, 53-byte set")
    if {item.get("status") for item in report.get("files", [])} != {"already_exact"}:
        fail("recovery engine unexpectedly attempted to write the live bundle")


def assert_live_profiles() -> tuple[dict, dict]:
    """Preserve rev0870 invariants while allowing later exact recoveries."""
    live, recovery = coverage.compute_profiles(ROOT, include_paths=True)
    fixed_coverage = (
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_mismatched_files_present",
        "canonical_source_files",
    )
    for key in fixed_coverage:
        if live.get(key) != EXPECTED_COVERAGE[key]:
            fail(f"later revision changed fixed rev0870 coverage invariant {key}")
    monotonic_coverage = {
        "canonical_exact_files_present": "up",
        "canonical_exact_bytes_present": "up",
        "canonical_missing_files": "down",
        "canonical_source_exact_files_present": "up",
    }
    for key, direction in monotonic_coverage.items():
        actual = live.get(key)
        baseline = EXPECTED_COVERAGE[key]
        if not isinstance(actual, int) or (direction == "up" and actual < baseline) or (direction == "down" and actual > baseline):
            fail(f"later revision regressed rev0870 coverage invariant {key}: {actual!r} vs {baseline!r}")
    if live["canonical_exact_files_present"] + live["canonical_mismatched_files_present"] + live["canonical_missing_files"] != live["canonical_index_files"]:
        fail("later revision coverage no longer conserves canonical index rows")

    fixed_recovery = (
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_recovery_object_files",
        "canonical_recovery_object_bytes",
        "canonical_mismatched_files_recoverable",
        "canonical_mismatched_files_unresolved",
        "canonical_missing_files_recoverable",
        "canonical_source_files",
    )
    for key in fixed_recovery:
        if recovery.get(key) != EXPECTED_RECOVERY[key]:
            fail(f"later revision changed fixed rev0870 recovery invariant {key}")
    monotonic_recovery = {
        "canonical_at_path_exact_files": "up",
        "canonical_at_path_exact_bytes": "up",
        "canonical_rehydratable_files": "up",
        "canonical_rehydratable_bytes": "up",
        "canonical_unavailable_files": "down",
        "canonical_unavailable_bytes": "down",
        "canonical_missing_files_unresolved": "down",
        "canonical_source_rehydratable_files": "up",
    }
    for key, direction in monotonic_recovery.items():
        actual = recovery.get(key)
        baseline = EXPECTED_RECOVERY[key]
        if not isinstance(actual, int) or (direction == "up" and actual < baseline) or (direction == "down" and actual > baseline):
            fail(f"later revision regressed rev0870 recovery invariant {key}: {actual!r} vs {baseline!r}")
    return live, recovery


def assert_duplicate_hash_frontier_exhausted(live: dict, recovery: dict) -> None:
    rows = coverage.load_index(ROOT)
    by_path = {row["path"]: row for row in rows}
    available_paths = set(live["paths"]["exact"]) | set(recovery["paths"]["recovery_objects"])
    available_hashes = {by_path[path]["sha256"] for path in available_paths}
    unresolved = set(recovery["paths"]["unresolved_missing"]) | set(
        recovery["paths"]["unresolved_mismatches"]
    )
    candidates = sorted(path for path in unresolved if by_path[path]["sha256"] in available_hashes)
    if candidates:
        fail("unmaterialized canonical paths still share available exact identities: " + ", ".join(candidates[:10]))


def expect_coverage_error(callable_obj, phrase: str) -> None:
    try:
        callable_obj()
    except coverage.CoverageError as exc:
        if phrase and phrase not in str(exc).lower():
            fail(f"snapshot race rejected for the wrong reason: {exc}")
    else:
        fail("descriptor-bound snapshot accepted an adversarial path mutation")


def assert_descriptor_snapshot_guards() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0870-coverage-") as tmp_text:
        tmp = Path(tmp_text)
        root = tmp / "root"
        root.mkdir()
        target = root / "payload.bin"
        original = b"A" * (coverage.CHUNK_SIZE + 257)
        target.write_bytes(original)
        stable = coverage.snapshot_regular_file(root, "payload.bin", "stable fixture")
        if stable["size"] != len(original) or stable["sha256"] != hashlib.sha256(original).hexdigest():
            fail("stable descriptor-bound snapshot produced the wrong identity")

        if hasattr(os, "symlink"):
            alias = tmp / "alias"
            try:
                os.symlink(root, alias)
                expect_coverage_error(lambda: coverage.prepare_root(alias), "symlink")
            except (OSError, NotImplementedError):
                pass

        original_iter = coverage._iter_file_chunks
        replacement = root / "replacement.bin"

        def replacing_iterator(handle):
            first = handle.read(coverage.CHUNK_SIZE)
            if first:
                yield first
            replacement.write_bytes(b"B" * len(original))
            os.replace(replacement, target)
            while True:
                chunk = handle.read(coverage.CHUNK_SIZE)
                if not chunk:
                    return
                yield chunk

        coverage._iter_file_chunks = replacing_iterator
        try:
            expect_coverage_error(
                lambda: coverage.snapshot_regular_file(root, "payload.bin", "replacement fixture"),
                "changed",
            )
        finally:
            coverage._iter_file_chunks = original_iter

        target.write_bytes(original)

        def mutating_iterator(handle):
            first = handle.read(coverage.CHUNK_SIZE)
            if first:
                yield first
            with target.open("r+b") as writer:
                writer.seek(len(original) - 1)
                writer.write(b"Z")
                writer.flush()
                os.fsync(writer.fileno())
            while True:
                chunk = handle.read(coverage.CHUNK_SIZE)
                if not chunk:
                    return
                yield chunk

        coverage._iter_file_chunks = mutating_iterator
        try:
            expect_coverage_error(
                lambda: coverage.snapshot_regular_file(root, "payload.bin", "in-place mutation fixture"),
                "changed while",
            )
        finally:
            coverage._iter_file_chunks = original_iter


def assert_recovery_writer_no_clobber() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0870-writer-") as tmp_text:
        root = Path(tmp_text)
        rel = "nested/value.txt"
        recovery_engine._write_absent(root, rel, b"first")
        if (root / rel).read_bytes() != b"first":
            fail("no-clobber writer did not materialize exact bytes")
        try:
            recovery_engine._write_absent(root, rel, b"second")
        except recovery_engine.RecoveryError:
            pass
        else:
            fail("no-clobber writer overwrote an existing path")
        if (root / rel).read_bytes() != b"first":
            fail("no-clobber refusal changed existing bytes")
        if hasattr(os, "symlink"):
            outside = root / "outside"
            outside.mkdir()
            linked = root / "linked"
            try:
                os.symlink(outside, linked)
                try:
                    recovery_engine._write_absent(root, "linked/escape.txt", b"bad")
                except (OSError, recovery_engine.RecoveryError):
                    pass
                else:
                    fail("recovery writer followed a symlinked parent")
                if (outside / "escape.txt").exists():
                    fail("recovery writer escaped through a symlinked parent")
            except (OSError, NotImplementedError):
                pass


def assert_manifest_boundaries() -> None:
    manifest = load_manifest()
    revision = manifest.get("overlay_revision")
    if not isinstance(revision, str) or not revision.startswith("rev") or not revision[3:].isdigit() or int(revision[3:]) < 870:
        fail("PATCH_BUNDLE_MANIFEST.json predates rev0870")
    block = manifest.get("hash_oracle_low_entropy_recovery")
    if not isinstance(block, dict):
        fail("hash_oracle_low_entropy_recovery block is absent")
    if block.get("paths") != list(RECOVERED) or block.get("total_files") != 4 or block.get("total_bytes") != 53:
        fail("manifest rev0870 recovery identity is stale")
    live, recovery = coverage.compute_profiles(ROOT)
    differences = coverage.compare_profile(live, manifest.get("representation_profile", {}))
    if differences:
        fail("manifest representation profile is not current: " + "; ".join(differences))
    differences = coverage.compare_recovery_profile(recovery, manifest.get("recovery_profile", {}))
    if differences:
        fail("manifest recovery profile is not current: " + "; ".join(differences))
    rights = manifest.get("active_rights_status", {})
    if rights.get("root_license_or_notice_present") is not False:
        fail("root rights blocker changed without an owner decision")
    payloads = manifest.get("active_proofcore_payload_status", {})
    if payloads.get("streamfold_full_missing") != 17 or payloads.get("streamfold_minimum_missing") != 4:
        fail("StreamFold absence boundary changed without exact payload recovery")


def assert_inherited_rev0869_boundaries() -> None:
    """Recheck the inherited bytes and demonstrated local-extra exploit cheaply.

    The complete rev0869 builder/reproducibility suite remains independently
    runnable and is executed once during release validation. Recursively running
    that entire historical suite inside every current gate added about 32 seconds
    without increasing coverage of rev0870's changed code.
    """
    validator_path = SCRIPTS / "validate_constant_recovery_zip_snapshot_rev0869.py"
    spec = importlib.util.spec_from_file_location("ev_rev0869_validator", validator_path)
    if spec is None or spec.loader is None:
        fail("cannot load inherited rev0869 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.assert_exact_constant_recoveries()
        module.assert_manifest_boundaries()
        with tempfile.TemporaryDirectory(prefix="ev-rev0870-inherited-zip-") as tmp_text:
            module.assert_local_only_extra_field_rejected(Path(tmp_text))
    except Exception as exc:
        fail(f"bounded rev0869 invariant regression: {exc}")


def assert_no_transients() -> None:
    transients = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__")]
    transients.extend(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc"))
    if transients:
        fail("transient Python cache paths are present: " + ", ".join(transients[:10]))


def main() -> int:
    try:
        assert_exact_recoveries()
        live, recovery = assert_live_profiles()
        assert_duplicate_hash_frontier_exhausted(live, recovery)
        assert_descriptor_snapshot_guards()
        assert_recovery_writer_no_clobber()
        assert_manifest_boundaries()
        assert_inherited_rev0869_boundaries()
        assert_no_transients()
        print("hash-oracle-recovery-coverage-snapshot-rev0870: OK")
        return 0
    except (ValidationError, coverage.CoverageError, recovery_engine.RecoveryError) as exc:
        print(f"hash-oracle-recovery-coverage-snapshot-rev0870: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"hash-oracle-recovery-coverage-snapshot-rev0870: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
