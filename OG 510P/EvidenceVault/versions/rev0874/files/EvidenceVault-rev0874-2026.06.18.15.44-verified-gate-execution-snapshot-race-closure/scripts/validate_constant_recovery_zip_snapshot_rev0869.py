#!/usr/bin/env python3
"""Validate rev0869 exact empty-array recoveries and ZIP build-boundary fixes."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    import build_deterministic_zip as zip_builder
    from build_deterministic_zip import ZipBuildError, build_archive
    from canonical_coverage import compute_profiles
    from validate_zip_container import ZipContainerError, validate_archive
    from validate_digest_recovery_zip_hardening_rev0868 import (
        assert_builder_reproducibility_and_symlink_refusal,
        assert_zip_validator_adversarial_cases,
    )
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass

REVISION = "rev0869"
EMPTY_ARRAY = b"[]"
EMPTY_ARRAY_SHA256 = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
RECOVERED = (
    "sources/ocf_llm/examples/refused_set_empty_v1.json",
    "sources/pact/PACT_workdir/eval_real_registry_semantic_scan/out/violations.json",
)
EXPECTED_COVERAGE = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 103,
    "canonical_exact_bytes_present": 4885343,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4466,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 16,
}
EXPECTED_RECOVERY = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_at_path_exact_files": 103,
    "canonical_at_path_exact_bytes": 4885343,
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 119,
    "canonical_rehydratable_bytes": 4973444,
    "canonical_unavailable_files": 4467,
    "canonical_unavailable_bytes": 101448546,
    "canonical_mismatched_files_recoverable": 16,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_missing_files_recoverable": 0,
    "canonical_missing_files_unresolved": 4466,
    "canonical_source_files": 3476,
    "canonical_source_rehydratable_files": 16,
}
EOCD = struct.Struct("<IHHHHIIH")


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(rel: str) -> dict:
    try:
        value = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read {rel}: {exc}")
    if not isinstance(value, dict):
        fail(f"{rel} must be a JSON object")
    return value


def index_rows() -> dict[str, dict[str, str]]:
    with (ROOT / "INDEX/files.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["path"]: row for row in csv.DictReader(handle)}
    if len(rows) != 4586:
        fail(f"canonical index row count changed unexpectedly: {len(rows)}")
    return rows


def assert_exact_constant_recoveries() -> None:
    rows = index_rows()
    for rel in RECOVERED:
        row = rows.get(rel)
        if row is None:
            fail(f"recovered path is absent from canonical index: {rel}")
        if int(row["size"]) != len(EMPTY_ARRAY) or row["sha256"] != EMPTY_ARRAY_SHA256:
            fail(f"canonical index identity is not the expected empty JSON array: {rel}")
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            fail(f"recovered path is not a regular file: {rel}")
        data = path.read_bytes()
        if data != EMPTY_ARRAY or sha256_bytes(data) != EMPTY_ARRAY_SHA256:
            fail(f"recovered bytes differ from exact canonical identity: {rel}")
        try:
            parsed = json.loads(data.decode("utf-8"))
        except Exception as exc:
            fail(f"recovered JSON is invalid for {rel}: {exc}")
        if parsed != []:
            fail(f"recovered JSON is not an empty array: {rel}")


def current_overlay_number() -> int:
    revision = load_json("PATCH_BUNDLE_MANIFEST.json").get("overlay_revision")
    if not isinstance(revision, str) or not revision.startswith("rev") or not revision[3:].isdigit():
        fail("PATCH_BUNDLE_MANIFEST.json has an invalid overlay_revision")
    return int(revision[3:])


def assert_live_coverage() -> None:
    coverage, recovery = compute_profiles(ROOT)
    revision_number = current_overlay_number()
    if revision_number == 869:
        for key, expected in EXPECTED_COVERAGE.items():
            if coverage.get(key) != expected:
                fail(f"live coverage mismatch for {key}: {coverage.get(key)!r} != {expected!r}")
        for key, expected in EXPECTED_RECOVERY.items():
            if recovery.get(key) != expected:
                fail(f"live recovery mismatch for {key}: {recovery.get(key)!r} != {expected!r}")
        return
    if revision_number < 869:
        fail(f"rev0869 invariant validator cannot run on older revision rev{revision_number:04d}")

    fixed_coverage = (
        "canonical_index_files",
        "canonical_index_bytes",
        "canonical_mismatched_files_present",
        "canonical_source_files",
    )
    for key in fixed_coverage:
        if coverage.get(key) != EXPECTED_COVERAGE[key]:
            fail(f"later-revision coverage changed fixed rev0869 invariant {key}")
    monotonic_coverage = {
        "canonical_exact_files_present": "at_least",
        "canonical_exact_bytes_present": "at_least",
        "canonical_missing_files": "at_most",
        "canonical_source_exact_files_present": "at_least",
    }
    for key, direction in monotonic_coverage.items():
        actual = coverage.get(key)
        baseline = EXPECTED_COVERAGE[key]
        if not isinstance(actual, int) or (direction == "at_least" and actual < baseline) or (direction == "at_most" and actual > baseline):
            fail(f"later-revision coverage regressed rev0869 invariant {key}: {actual!r} vs {baseline!r}")
    if coverage["canonical_exact_files_present"] + coverage["canonical_mismatched_files_present"] + coverage["canonical_missing_files"] != coverage["canonical_index_files"]:
        fail("later-revision canonical coverage counts do not conserve the index")

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
            fail(f"later-revision recovery changed fixed rev0869 invariant {key}")
    at_least = (
        "canonical_at_path_exact_files",
        "canonical_at_path_exact_bytes",
        "canonical_rehydratable_files",
        "canonical_rehydratable_bytes",
        "canonical_source_rehydratable_files",
    )
    for key in at_least:
        if recovery.get(key, -1) < EXPECTED_RECOVERY[key]:
            fail(f"later-revision recovery regressed rev0869 invariant {key}")
    at_most = (
        "canonical_unavailable_files",
        "canonical_unavailable_bytes",
        "canonical_missing_files_unresolved",
    )
    for key in at_most:
        if recovery.get(key, 10**30) > EXPECTED_RECOVERY[key]:
            fail(f"later-revision recovery regressed rev0869 invariant {key}")
    if recovery["canonical_rehydratable_files"] + recovery["canonical_unavailable_files"] != recovery["canonical_index_files"]:
        fail("later-revision recovery file counts do not conserve the index")
    if recovery["canonical_rehydratable_bytes"] + recovery["canonical_unavailable_bytes"] != recovery["canonical_index_bytes"]:
        fail("later-revision recovery byte counts do not conserve the index")


def write_structural_zip(path: Path, root: str) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(root + "/", b"")
        zf.writestr(root + "/file.txt", b"ok")


def inject_local_unicode_path_extra(source: Path, target: Path, member_name: str) -> None:
    """Add a local-header-only 0x7075 path alias and repair the EOCD offset."""
    with zipfile.ZipFile(source) as zf:
        offset = zf.getinfo(member_name).header_offset
    raw = bytearray(source.read_bytes())
    filename_length = struct.unpack_from("<H", raw, offset + 26)[0]
    extra_length = struct.unpack_from("<H", raw, offset + 28)[0]
    if extra_length != 0:
        fail("local-only extra-field fixture unexpectedly starts with a local extra field")
    alternate = b"../escape.txt"
    payload = bytes([1]) + struct.pack(
        "<I", zlib.crc32(member_name.encode("utf-8")) & 0xFFFFFFFF
    ) + alternate
    extra = struct.pack("<HH", 0x7075, len(payload)) + payload
    insert_at = offset + 30 + filename_length
    raw[offset + 28 : offset + 30] = struct.pack("<H", len(extra))
    raw = raw[:insert_at] + extra + raw[insert_at:]
    eocd_offset = len(raw) - EOCD.size
    fields = list(EOCD.unpack(raw[eocd_offset : eocd_offset + EOCD.size]))
    if fields[0] != 0x06054B50:
        fail("could not locate EOCD in local-extra adversarial fixture")
    fields[6] += len(extra)
    raw[eocd_offset : eocd_offset + EOCD.size] = EOCD.pack(*fields)
    target.write_bytes(raw)


def assert_local_only_extra_field_rejected(tmp: Path) -> None:
    safe = tmp / "local-extra.zip"
    write_structural_zip(safe, "local-extra")
    malicious = tmp / "mutated-local-extra.zip"
    inject_local_unicode_path_extra(safe, malicious, "local-extra/file.txt")
    # Python's central-directory view remains safe, proving this is specifically
    # a local/central semantic split rather than an ordinary unsafe member name.
    with zipfile.ZipFile(malicious) as zf:
        if zf.namelist() != ["local-extra/", "local-extra/file.txt"]:
            fail("adversarial local-extra fixture changed the central-directory names")
        if zf.getinfo("local-extra/file.txt").extra:
            fail("adversarial extra field leaked into the central directory")
    try:
        validate_archive(
            malicious,
            logical_archive_name="local-extra.zip",
            require_overlay_manifest=False,
        )
    except ZipContainerError as exc:
        text = str(exc).lower()
        if "unsupported local extra field" not in text or "0x7075" not in text:
            fail(f"local-only path alias rejected for the wrong reason: {exc}")
    else:
        fail("validator accepted a local-header-only Unicode path alias")


def write_mini_bundle(source: Path, hello: bytes = b"hello\n") -> None:
    (source / "CHECKS").mkdir(parents=True)
    (source / "hello.txt").write_bytes(hello)
    patch_manifest = {
        "archive_name": source.name + ".zip",
        "archive_root": source.name,
        "archive_container_profile": {
            "policy": "ev-safe-zip-v1",
            "expected_root": source.name,
            "validator": "scripts/validate_zip_container.py",
        },
        "created_at_utc": "2026-06-18T09:02:00Z",
        "overlay_revision": "revTEST",
    }
    patch_bytes = json.dumps(patch_manifest, indent=2, sort_keys=True).encode() + b"\n"
    (source / "PATCH_BUNDLE_MANIFEST.json").write_bytes(patch_bytes)
    entries = []
    for rel in ["PATCH_BUNDLE_MANIFEST.json", "hello.txt"]:
        data = (source / rel).read_bytes()
        entries.append({"bytes": len(data), "path": rel, "sha256": sha256_bytes(data)})
    overlay = {
        "created_at_utc": "2026-06-18T09:02:00Z",
        "file_count": len(entries),
        "files": entries,
    }
    overlay_bytes = json.dumps(overlay, indent=2, sort_keys=True).encode() + b"\n"
    (source / "CHECKS/overlay-manifest.json").write_bytes(overlay_bytes)
    (source / "CHECKS/overlay-manifest.sha256").write_text(
        f"{sha256_bytes(overlay_bytes)}  CHECKS/overlay-manifest.json\n",
        encoding="utf-8",
    )


def expect_build_rejected_after_capture(tmp: Path, mutation: str) -> None:
    source = tmp / f"mini-{mutation}"
    source.mkdir()
    write_mini_bundle(source)
    output_dir = tmp / f"out-{mutation}"
    output_dir.mkdir()
    output = output_dir / (source.name + ".zip")
    original_capture = zip_builder._capture_snapshot
    fired = False

    def capture_then_mutate(root: Path):
        nonlocal fired
        snapshot = original_capture(root)
        if not fired:
            fired = True
            if mutation == "same-size-content":
                (root / "hello.txt").write_bytes(b"jello\n")
            elif mutation == "added-file":
                (root / "late.txt").write_text("late\n", encoding="utf-8")
            elif mutation == "symlink-swap":
                victim = root / "hello.txt"
                victim.unlink()
                os.symlink("PATCH_BUNDLE_MANIFEST.json", victim)
            else:
                fail(f"unknown mutation fixture: {mutation}")
        return snapshot

    zip_builder._capture_snapshot = capture_then_mutate
    try:
        try:
            build_archive(source, output)
        except ZipBuildError as exc:
            text = str(exc).lower()
            if "snapshot" not in text and "symlink" not in text and "regular file" not in text:
                fail(f"builder rejected {mutation} for the wrong reason: {exc}")
        else:
            fail(f"builder published an archive after {mutation} source mutation")
    finally:
        zip_builder._capture_snapshot = original_capture
    if output.exists():
        fail(f"builder left a published output after rejecting {mutation}")


def assert_snapshot_builder_guards(tmp: Path) -> None:
    source = tmp / "snapshot-mini"
    source.mkdir()
    write_mini_bundle(source)
    outdir = tmp / "snapshot-out"
    outdir.mkdir()
    report = build_archive(source, outdir / "snapshot-mini.zip")
    digest = report.get("source_snapshot_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        fail("builder report lacks a source snapshot SHA-256")
    if report.get("source_snapshot_reverified_before_publication") is not True:
        fail("builder report does not confirm pre-publication snapshot revalidation")
    if report.get("published_inode_and_bytes_reverified") is not True:
        fail("builder report does not confirm published-inode and byte revalidation")
    if report.get("source_snapshot_files") != 4:
        fail("builder report has the wrong source snapshot file count")
    for mutation in ("same-size-content", "added-file"):
        expect_build_rejected_after_capture(tmp, mutation)
    if hasattr(os, "symlink"):
        try:
            expect_build_rejected_after_capture(tmp, "symlink-swap")
        except (OSError, NotImplementedError):
            pass


def assert_manifest_boundaries() -> None:
    manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
    revision_number = current_overlay_number()
    if revision_number < 869:
        fail("PATCH_BUNDLE_MANIFEST.json predates rev0869")
    recovery = manifest.get("deterministic_constant_recovery")
    if not isinstance(recovery, dict):
        fail("deterministic_constant_recovery is absent")
    if recovery.get("paths") != list(RECOVERED):
        fail("deterministic constant recovery paths are wrong")
    if recovery.get("bytes_per_file") != 2 or recovery.get("sha256") != EMPTY_ARRAY_SHA256:
        fail("deterministic constant recovery identity is wrong")
    profile = manifest.get("archive_container_profile")
    if not isinstance(profile, dict):
        fail("archive_container_profile is absent")
    required = profile.get("required_properties")
    if not isinstance(required, list):
        fail("archive_container_profile.required_properties is absent")
    joined = " ".join(str(item).lower() for item in required)
    for phrase in ("extra field", "source snapshot"):
        if phrase not in joined:
            fail(f"archive profile does not declare {phrase!r} hardening")
    rights = manifest.get("active_rights_status", {})
    if rights.get("root_license_or_notice_present") is not False:
        fail("root rights blocker changed without an owner decision")
    proofcore = manifest.get("active_proofcore_payload_status", {})
    if proofcore.get("streamfold_full_missing") != 17 or proofcore.get("streamfold_minimum_missing") != 4:
        fail("StreamFold absence boundary changed without payload recovery")


def assert_inherited_history_recovery() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_overlay_history_canonical_recovery_rev0867.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        fail("rev0867 historical recovery invariant failed: " + (result.stderr or result.stdout).strip())


def main() -> int:
    try:
        assert_exact_constant_recoveries()
        assert_live_coverage()
        with tempfile.TemporaryDirectory(prefix="ev-rev0869-tests-") as tmp_text:
            tmp = Path(tmp_text)
            # Retain the complete rev0868 adversarial and deterministic-builder suite.
            assert_zip_validator_adversarial_cases(tmp)
            prior_builder_tmp = tmp / "prior-builder"
            prior_builder_tmp.mkdir()
            assert_builder_reproducibility_and_symlink_refusal(prior_builder_tmp)
            assert_local_only_extra_field_rejected(tmp)
            snapshot_tmp = tmp / "snapshot"
            snapshot_tmp.mkdir()
            assert_snapshot_builder_guards(snapshot_tmp)
        assert_manifest_boundaries()
        assert_inherited_history_recovery()
        transient = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__")]
        transient.extend(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc"))
        if transient:
            fail("transient Python cache paths are present: " + ", ".join(transient[:10]))
        print("constant-recovery-zip-snapshot-rev0869: OK")
        return 0
    except ValidationError as exc:
        print(f"constant-recovery-zip-snapshot-rev0869: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"constant-recovery-zip-snapshot-rev0869: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
