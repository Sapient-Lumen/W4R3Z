#!/usr/bin/env python3
"""Validate rev0871 exact digest recovery and shared materialization safety."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    import canonical_coverage as coverage
    import recover_indexed_embedded_evidence_rev0871 as recovery
    import safe_materialize as safe
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass

EXPECTED = {
    "sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_1.digest.txt": b"sha256:11253b6b6409e9a925e0d43fd01721ee900525ef4b044a894fdda0641daf7ba0\n",
    "sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_2.digest.txt": b"sha256:875622af0b1c8944d1e068386324a89fd6e1972feda9e860a3c09eba133bc3b2\n",
}
EXPECTED_COVERAGE = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 109,
    "canonical_exact_bytes_present": 4885540,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4460,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 22,
}
EXPECTED_RECOVERY = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_at_path_exact_files": 109,
    "canonical_at_path_exact_bytes": 4885540,
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 125,
    "canonical_rehydratable_bytes": 4973641,
    "canonical_unavailable_files": 4461,
    "canonical_unavailable_bytes": 101448349,
    "canonical_mismatched_files_recoverable": 16,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_missing_files_recoverable": 0,
    "canonical_missing_files_unresolved": 4460,
    "canonical_source_files": 3476,
    "canonical_source_rehydratable_files": 22,
}


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def expect_materialization_error(call, phrase: str = "") -> None:
    try:
        call()
    except safe.MaterializationError as exc:
        if phrase and phrase.lower() not in str(exc).lower():
            fail(f"materialization failed for the wrong reason: {exc}")
    else:
        fail("unsafe materialization unexpectedly succeeded")


def assert_exact_recoveries() -> None:
    rows = {row["path"]: row for row in coverage.load_index(ROOT)}
    for rel, data in EXPECTED.items():
        digest = hashlib.sha256(data).hexdigest()
        row = rows.get(rel)
        if row is None or row["size"] != len(data) or row["sha256"] != digest:
            fail(f"recipe/index identity mismatch: {rel}")
        snap = coverage.snapshot_regular_file(ROOT, rel, f"rev0871 recovery {rel}", capture_bytes=True)
        if snap["bytes"] != data or snap["sha256"] != digest or snap["size"] != len(data):
            fail(f"recovered bytes are not exact: {rel}")
    report = recovery.verify_recipes(ROOT, write=False)
    if report.get("recovered_files") != 2 or report.get("recovered_bytes") != 144:
        fail("embedded-evidence recovery engine did not verify the exact two-file set")
    if {row.get("status") for row in report.get("files", [])} != {"already_exact"}:
        fail("embedded-evidence recovery engine unexpectedly wrote the live tree")


def assert_live_profiles_and_manifest() -> None:
    live, recoverable = coverage.compute_profiles(ROOT)
    for key, expected in EXPECTED_COVERAGE.items():
        if live.get(key) != expected:
            fail(f"coverage mismatch for {key}: {live.get(key)!r} != {expected!r}")
    for key, expected in EXPECTED_RECOVERY.items():
        if recoverable.get(key) != expected:
            fail(f"recovery mismatch for {key}: {recoverable.get(key)!r} != {expected!r}")
    manifest = json.loads((ROOT / "PATCH_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("overlay_revision") != "rev0871":
        fail("patch-bundle manifest is not rev0871")
    differences = coverage.compare_profile(live, manifest.get("representation_profile", {}))
    if differences:
        fail("manifest representation profile is stale: " + "; ".join(differences))
    differences = coverage.compare_recovery_profile(recoverable, manifest.get("recovery_profile", {}))
    if differences:
        fail("manifest recovery profile is stale: " + "; ".join(differences))
    block = manifest.get("embedded_evidence_digest_recovery")
    if not isinstance(block, dict) or block.get("paths") != list(EXPECTED) or block.get("total_bytes") != 144:
        fail("manifest embedded-evidence recovery block is stale")


def assert_shared_writer_guards() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0871-materialize-") as tmp_text:
        tmp = Path(tmp_text)
        root = tmp / "root"
        root.mkdir()
        rel = "nested/value.bin"
        data = b"exact materialization bytes\n"
        digest = hashlib.sha256(data).hexdigest()
        first = safe.materialize_exact_bytes(root, rel, data, expected_sha256=digest)
        if first.status != "written" or (root / rel).read_bytes() != data:
            fail("shared writer did not materialize exact bytes")
        if stat.S_IMODE((root / rel).stat().st_mode) != 0o644:
            fail("shared writer did not normalize file mode to 0644")
        second = safe.materialize_exact_bytes(root, rel, data, expected_sha256=digest)
        if second.status != "already_exact":
            fail("shared writer did not accept an independently verified exact race winner")
        expect_materialization_error(
            lambda: safe.materialize_exact_bytes(root, rel, b"different"), "overwrite"
        )
        if (root / rel).read_bytes() != data:
            fail("no-clobber refusal changed pre-existing bytes")

        expect_materialization_error(
            lambda: safe.materialize_exact_bytes(root, "../escape", b"bad"), "clean relative"
        )
        if hasattr(os, "symlink"):
            outside = tmp / "outside"
            outside.mkdir()
            linked_parent = root / "linked"
            os.symlink(outside, linked_parent)
            expect_materialization_error(
                lambda: safe.materialize_exact_bytes(root, "linked/escape.txt", b"bad"),
                "symlinked or non-directory",
            )
            if (outside / "escape.txt").exists():
                fail("shared writer escaped through a symlinked parent")

            external = tmp / "external.txt"
            external.write_bytes(b"protected")
            target_link = root / "target-link"
            os.symlink(external, target_link)
            expect_materialization_error(
                lambda: safe.materialize_exact_bytes(root, "target-link", b"bad"), "unsafe"
            )
            if external.read_bytes() != b"protected":
                fail("shared writer changed a symlink target")

            root_alias = tmp / "root-alias"
            os.symlink(root, root_alias)
            expect_materialization_error(
                lambda: safe.materialize_exact_bytes(root_alias, "alias.txt", b"bad"), "symlink"
            )

        # Force the race branch: first inspection says absent while O_EXCL sees
        # a pre-existing mismatch. Cleanup must not unlink that protected file.
        race_rel = "race.txt"
        race_path = root / race_rel
        race_path.write_bytes(b"protected race winner")
        original_inspect = safe._inspect_at
        calls = {"count": 0}

        def forged_first_inspection(parent_fd: int, name: str, rel_text: str):
            calls["count"] += 1
            if calls["count"] == 1:
                return "missing", None, None
            return original_inspect(parent_fd, name, rel_text)

        safe._inspect_at = forged_first_inspection
        try:
            expect_materialization_error(
                lambda: safe.materialize_exact_bytes(root, race_rel, b"new bytes"), "appeared"
            )
        finally:
            safe._inspect_at = original_inspect
        if race_path.read_bytes() != b"protected race winner":
            fail("O_EXCL race refusal deleted or changed the pre-existing target")


def assert_recovery_tools_share_boundary() -> None:
    expected_tools = (
        "scripts/recover_indexed_files_from_patches.py",
        "scripts/recover_indexed_versions_from_overlay_history.py",
        "scripts/recover_indexed_low_entropy_constants_rev0870.py",
        "scripts/recover_indexed_embedded_evidence_rev0871.py",
    )
    forbidden = ("NamedTemporaryFile", "tempfile.mkstemp", "os.link(")
    for rel in expected_tools:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "safe_materialize" not in text:
            fail(f"recovery tool does not use shared materialization boundary: {rel}")
        for token in forbidden:
            if token in text:
                fail(f"recovery tool retains a duplicate publication primitive {token}: {rel}")
    helper = (ROOT / "scripts/safe_materialize.py").read_text(encoding="utf-8")
    for required in ("O_EXCL", "follow_symlinks=False", "created_identity", "os.fsync"):
        if required not in helper:
            fail(f"shared writer is missing required control: {required}")


def assert_inherited_rev0870_boundaries() -> None:
    validator_path = SCRIPTS / "validate_hash_oracle_recovery_coverage_snapshot_rev0870.py"
    spec = importlib.util.spec_from_file_location("ev_rev0870_validator", validator_path)
    if spec is None or spec.loader is None:
        fail("cannot load inherited rev0870 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.assert_exact_recoveries()
        live, recoverable = module.assert_live_profiles()
        module.assert_duplicate_hash_frontier_exhausted(live, recoverable)
        module.assert_descriptor_snapshot_guards()
        module.assert_recovery_writer_no_clobber()
        module.assert_manifest_boundaries()
        module.assert_inherited_rev0869_boundaries()
    except Exception as exc:
        fail(f"bounded rev0870 invariant regression: {exc}")


def assert_remaining_boundaries() -> None:
    manifest = json.loads((ROOT / "PATCH_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    rights = manifest.get("active_rights_status", {})
    payloads = manifest.get("active_proofcore_payload_status", {})
    if rights.get("root_license_or_notice_present") is not False:
        fail("root rights state changed without owner approval")
    if payloads.get("streamfold_full_missing") != 17 or payloads.get("streamfold_minimum_missing") != 4:
        fail("StreamFold absence boundary changed without exact payload bytes")
    if EXPECTED_COVERAGE["canonical_mismatched_files_present"] != 17 or EXPECTED_RECOVERY["canonical_mismatched_files_unresolved"] != 1:
        fail("root README mismatch boundary was accidentally reclassified")


def assert_no_transients() -> None:
    transients = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__")]
    transients.extend(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc"))
    if transients:
        fail("transient Python cache paths are present: " + ", ".join(transients[:10]))


def main() -> int:
    try:
        assert_exact_recoveries()
        assert_live_profiles_and_manifest()
        assert_shared_writer_guards()
        assert_recovery_tools_share_boundary()
        assert_inherited_rev0870_boundaries()
        assert_remaining_boundaries()
        assert_no_transients()
        print("embedded-digest-recovery-safe-materialization-rev0871: OK")
        return 0
    except (ValidationError, recovery.RecoveryError, coverage.CoverageError, safe.MaterializationError) as exc:
        print(f"embedded-digest-recovery-safe-materialization-rev0871: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"embedded-digest-recovery-safe-materialization-rev0871: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
