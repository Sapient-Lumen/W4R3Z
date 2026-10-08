#!/usr/bin/env python3
"""Validate rev0868 exact digest recovery and ZIP-container hardening."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import warnings
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "scripts").resolve()))
try:
    from build_deterministic_zip import ZipBuildError, build_archive
    from canonical_coverage import compute_coverage, compute_recovery_availability
    from validate_zip_container import ZipContainerError, validate_archive
finally:
    try:
        sys.path.remove(str((ROOT / "scripts").resolve()))
    except ValueError:
        pass

REVISION = "rev0868"
RECOVERED_REL = "sources/ocf_llm/examples/output_credential_demo_v242/credential_digest.txt"
REPORT_REL = "sources/ocf_llm/examples/output_credential_demo_v242/demo_report.json"
EXPECTED_DIGEST = "9027fea3c23dae8180fda581b02836c4f081a730ab2955346b9522d8c9c97ac8"
EXPECTED_LIVE = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 101,
    "canonical_exact_bytes_present": 4885339,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4468,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 14,
}
EXPECTED_RECOVERY = {
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 117,
    "canonical_rehydratable_bytes": 4973440,
    "canonical_unavailable_files": 4469,
    "canonical_unavailable_bytes": 101448550,
    "canonical_missing_files_unresolved": 4468,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_source_rehydratable_files": 14,
}


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
        fail(f"invalid {rel}: {exc}")
    if not isinstance(value, dict):
        fail(f"{rel} must be a JSON object")
    return value


def assert_digest_recovery() -> None:
    report = load_json(REPORT_REL)
    recorded = report.get("credentialDigest")
    if not isinstance(recorded, str) or not recorded.startswith("sha256:"):
        fail("surviving demo report lacks a sha256 credentialDigest")
    expected = (recorded + "\n").encode("utf-8")
    recovered = ROOT / RECOVERED_REL
    if recovered.is_symlink() or not recovered.is_file():
        fail(f"recovered canonical file is absent or unsafe: {RECOVERED_REL}")
    actual = recovered.read_bytes()
    if actual != expected:
        fail("credential_digest.txt is not the exact newline-terminated report digest")
    if len(actual) != 72 or sha256_bytes(actual) != EXPECTED_DIGEST:
        fail("credential_digest.txt does not match the canonical 72-byte SHA-256 identity")

    import csv

    with (ROOT / "INDEX/files.csv").open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("path") == RECOVERED_REL]
    if len(rows) != 1:
        fail("canonical index does not contain exactly one credential_digest.txt row")
    row = rows[0]
    if int(row["size"]) != len(actual) or row["sha256"] != sha256_bytes(actual):
        fail("recovered credential_digest.txt differs from INDEX/files.csv")


def assert_coverage() -> None:
    live = compute_coverage(ROOT)
    for key, expected in EXPECTED_LIVE.items():
        if live.get(key) != expected:
            fail(f"live coverage drift for {key}: {live.get(key)!r} != {expected!r}")
    recovery = compute_recovery_availability(ROOT)
    for key, expected in EXPECTED_RECOVERY.items():
        if recovery.get(key) != expected:
            fail(f"recovery coverage drift for {key}: {recovery.get(key)!r} != {expected!r}")


def _write_structural_zip(path: Path, entries: list[tuple[zipfile.ZipInfo | str, bytes]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name_or_info, payload in entries:
            zf.writestr(name_or_info, payload)


def _expect_rejected(path: Path, needle: str, *, logical_name: str) -> None:
    try:
        validate_archive(
            path,
            logical_archive_name=logical_name,
            require_overlay_manifest=False,
        )
    except ZipContainerError as exc:
        if needle.lower() not in str(exc).lower():
            fail(f"malicious ZIP rejected for wrong reason; wanted {needle!r}, got {exc!r}")
        return
    fail(f"malicious ZIP was accepted; expected rejection containing {needle!r}")


def assert_zip_validator_adversarial_cases(tmp: Path) -> None:
    safe = tmp / "safe-fixture.zip"
    _write_structural_zip(safe, [("safe-fixture/", b""), ("safe-fixture/file.txt", b"ok\n")])
    report = validate_archive(
        safe,
        expected_root="safe-fixture",
        logical_archive_name="safe-fixture.zip",
        require_overlay_manifest=False,
    )
    if report.get("status") != "zip_container_valid" or report.get("file_count") != 1:
        fail("safe structural ZIP fixture did not validate")

    duplicate = tmp / "duplicate.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        _write_structural_zip(
            duplicate,
            [("duplicate/", b""), ("duplicate/file.txt", b"one"), ("duplicate/file.txt", b"two")],
        )
    _expect_rejected(duplicate, "duplicate", logical_name="duplicate.zip")

    traversal = tmp / "traversal.zip"
    _write_structural_zip(traversal, [("traversal/", b""), ("traversal/../escape.txt", b"x")])
    _expect_rejected(traversal, "unsafe", logical_name="traversal.zip")

    collision = tmp / "collision.zip"
    _write_structural_zip(
        collision,
        [("collision/", b""), ("collision/A.txt", b"a"), ("collision/a.txt", b"b")],
    )
    _expect_rejected(collision, "case-folded", logical_name="collision.zip")

    symlink = tmp / "symlink.zip"
    link = zipfile.ZipInfo("symlink/link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    _write_structural_zip(symlink, [("symlink/", b""), (link, b"target")])
    _expect_rejected(symlink, "symlink", logical_name="symlink.zip")

    disagreement = tmp / "header-mismatch.zip"
    _write_structural_zip(disagreement, [("header-mismatch/", b""), ("header-mismatch/a.txt", b"x")])
    with zipfile.ZipFile(disagreement) as zf:
        info = zf.getinfo("header-mismatch/a.txt")
        offset = info.header_offset + 30
    raw = bytearray(disagreement.read_bytes())
    original = b"header-mismatch/a.txt"
    replacement = b"header-mismatch/b.txt"
    if raw[offset : offset + len(original)] != original or len(original) != len(replacement):
        fail("could not prepare local/central header disagreement fixture")
    raw[offset : offset + len(original)] = replacement
    disagreement.write_bytes(raw)
    _expect_rejected(disagreement, "local/central filename disagreement", logical_name="header-mismatch.zip")

    trailing = tmp / "trailing.zip"
    trailing.write_bytes(safe.read_bytes() + b"hidden-trailing-bytes")
    _expect_rejected(trailing, "end-of-central-directory", logical_name="safe-fixture.zip")

    prefixed = tmp / "prefixed.zip"
    prefixed.write_bytes(b"hidden-prefix" + safe.read_bytes())
    _expect_rejected(prefixed, "central-directory", logical_name="safe-fixture.zip")


def _write_mini_bundle(source: Path) -> None:
    (source / "CHECKS").mkdir(parents=True)
    (source / "hello.txt").write_text("hello\n", encoding="utf-8")
    patch_manifest = {
        "archive_name": source.name + ".zip",
        "archive_root": source.name,
        "archive_container_profile": {
            "policy": "ev-safe-zip-v1",
            "expected_root": source.name,
            "validator": "scripts/validate_zip_container.py",
        },
        "created_at_utc": "2026-06-18T07:22:00Z",
        "overlay_revision": "revTEST",
    }
    encoded_patch = json.dumps(patch_manifest, indent=2, sort_keys=True).encode() + b"\n"
    (source / "PATCH_BUNDLE_MANIFEST.json").write_bytes(encoded_patch)
    entries = []
    for rel in ["PATCH_BUNDLE_MANIFEST.json", "hello.txt"]:
        data = (source / rel).read_bytes()
        entries.append({"bytes": len(data), "path": rel, "sha256": sha256_bytes(data)})
    overlay = {
        "created_at_utc": "2026-06-18T07:22:00Z",
        "file_count": len(entries),
        "files": entries,
    }
    overlay_bytes = json.dumps(overlay, indent=2, sort_keys=True).encode() + b"\n"
    (source / "CHECKS/overlay-manifest.json").write_bytes(overlay_bytes)
    (source / "CHECKS/overlay-manifest.sha256").write_text(
        f"{sha256_bytes(overlay_bytes)}  CHECKS/overlay-manifest.json\n",
        encoding="utf-8",
    )


def assert_builder_reproducibility_and_symlink_refusal(tmp: Path) -> None:
    source = tmp / "mini"
    source.mkdir()
    _write_mini_bundle(source)
    first_dir = tmp / "first"
    second_dir = tmp / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "mini.zip"
    second = second_dir / "mini.zip"
    one = build_archive(source, first)
    two = build_archive(source, second)
    if first.read_bytes() != second.read_bytes():
        fail("deterministic ZIP builder produced different bytes from identical input")
    if one.get("archive_sha256") != two.get("archive_sha256"):
        fail("deterministic ZIP builder reports disagree")
    if one.get("embedded_inventory_verified") is not True:
        fail("deterministic ZIP builder did not validate embedded inventory")
    for built in (first, second):
        if stat.S_IMODE(built.stat().st_mode) != 0o644:
            fail(f"deterministic ZIP builder published the wrong filesystem mode: {built}")

    occupied_dir = tmp / "occupied"
    occupied_dir.mkdir()
    occupied = occupied_dir / "mini.zip"
    occupied.write_bytes(b"preserve-existing-output")
    try:
        build_archive(source, occupied)
    except ZipBuildError as exc:
        if "already exists" not in str(exc).lower():
            fail(f"builder rejected occupied output for wrong reason: {exc}")
    else:
        fail("deterministic ZIP builder overwrote an occupied output without --replace")
    if occupied.read_bytes() != b"preserve-existing-output":
        fail("deterministic ZIP builder changed an occupied output")

    bad = tmp / "bad-mini"
    shutil.copytree(source, bad)
    try:
        os.symlink("hello.txt", bad / "link.txt")
    except (OSError, NotImplementedError):
        return
    bad_out_dir = tmp / "bad-out"
    bad_out_dir.mkdir()
    try:
        build_archive(bad, bad_out_dir / "bad-mini.zip")
    except ZipBuildError as exc:
        if "symlink" not in str(exc).lower():
            fail(f"builder rejected symlink fixture for wrong reason: {exc}")
    else:
        fail("deterministic ZIP builder accepted a source-tree symlink")


def assert_manifest_and_prior_gates() -> None:
    manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
    if manifest.get("overlay_revision") != REVISION:
        fail("PATCH_BUNDLE_MANIFEST.json is not rev0868")
    profile = manifest.get("archive_container_profile")
    if not isinstance(profile, dict) or profile.get("policy") != "ev-safe-zip-v1":
        fail("archive container policy is absent")
    if profile.get("expected_root") != ROOT.name:
        fail("archive container expected_root differs from extracted root")
    recovery = manifest.get("deterministic_digest_recovery")
    if not isinstance(recovery, dict) or recovery.get("path") != RECOVERED_REL:
        fail("deterministic digest recovery is not declared")
    if recovery.get("sha256") != EXPECTED_DIGEST or recovery.get("bytes") != 72:
        fail("deterministic digest recovery identity is wrong")

    rights = manifest.get("active_rights_status", {})
    if rights.get("root_license_or_notice_present") is not False:
        fail("root rights blocker changed without an owner decision")
    proofcore = manifest.get("active_proofcore_payload_status", {})
    if proofcore.get("streamfold_full_missing") != 17 or proofcore.get("streamfold_minimum_missing") != 4:
        fail("StreamFold absence boundary changed without payload recovery")

    prior = subprocess.run(
        [sys.executable, "scripts/validate_overlay_history_canonical_recovery_rev0867.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if prior.returncode != 0:
        fail("rev0867 recovery invariant failed: " + (prior.stderr or prior.stdout).strip())


def main() -> int:
    try:
        assert_digest_recovery()
        assert_coverage()
        with tempfile.TemporaryDirectory(prefix="ev-rev0868-zip-tests-") as tmp_text:
            tmp = Path(tmp_text)
            assert_zip_validator_adversarial_cases(tmp)
            assert_builder_reproducibility_and_symlink_refusal(tmp)
        assert_manifest_and_prior_gates()
        transient = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__")]
        transient.extend(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc"))
        if transient:
            fail("transient Python cache paths are present: " + ", ".join(transient[:10]))
        print("digest-recovery-zip-hardening-rev0868: OK")
        return 0
    except ValidationError as exc:
        print(f"digest-recovery-zip-hardening-rev0868: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"digest-recovery-zip-hardening-rev0868: FAIL: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
