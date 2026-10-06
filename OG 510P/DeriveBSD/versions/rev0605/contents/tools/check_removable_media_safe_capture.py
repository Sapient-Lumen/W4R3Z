#!/usr/bin/env python3
"""Exercise the dirfd-pinned removable-media capture helper.

This guard keeps the highest-risk first-lane path from regressing to friendly
``Path.resolve`` semantics.  It builds a temporary hostile media tree and proves
that the capture helper admits one regular file while rejecting traversal,
absolute paths, directory subjects, symlink leaves, and symlink ancestors.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import removable_media_safe_capture as safe_capture

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "validation" / "removable-media-safe-capture.receipt.json"
PROBE_ID = "rm-safe-capture-20260604-r536"
FIXED_GENERATED_AT = "2026-06-04T09:45:00Z"
SUBJECT_BYTES = b"DeriveBSD safe capture probe\nThis byte string must be captured through openat, not path resolution.\n"


def make_media_tree(media_root: Path) -> dict[str, bool]:
    (media_root / "safe").mkdir(parents=True)
    (media_root / "safe" / "report.txt").write_bytes(SUBJECT_BYTES)
    (media_root / "safe" / "dir-subject").mkdir()
    symlinks = {"leaf": False, "ancestor": False}
    try:
        os.symlink("report.txt", media_root / "safe" / "link-leaf")
        symlinks["leaf"] = True
    except OSError:
        pass
    try:
        os.symlink("safe", media_root / "linkdir")
        symlinks["ancestor"] = True
    except OSError:
        pass
    if hasattr(os, "mkfifo"):
        try:
            os.mkfifo(media_root / "fifo-subject")
        except OSError:
            pass
    return symlinks


def build_receipt(work_root: Path, generated_at_utc: str = FIXED_GENERATED_AT) -> dict[str, Any]:
    media_root = work_root / "media"
    store_root = work_root / "store"
    symlinks = make_media_tree(media_root)
    capture = safe_capture.capture_regular_member(media_root, "safe/report.txt", store_root)
    recapture = safe_capture.capture_regular_member(media_root, "safe/report.txt", store_root)

    expected_digest = safe_capture.sha256_bytes(SUBJECT_BYTES)
    _, expected_hex = expected_digest.split(":", 1)
    conflict_store = work_root / "conflict-store"
    conflict_obj = conflict_store / "cas" / "sha256" / expected_hex
    conflict_obj.parent.mkdir(parents=True, exist_ok=True)
    conflict_obj.write_bytes(b"corrupt bytes deliberately placed at the expected digest path\n")
    try:
        safe_capture.capture_regular_member(media_root, "safe/report.txt", conflict_store)
        conflict_reason = None
    except safe_capture.CaptureError as exc:
        conflict_reason = exc.reason

    hostile = [
        ("../escape.txt", "non-relative-clean-member-path"),
        ("/absolute/report.txt", "absolute-member-path"),
        ("safe/dir-subject", "directory-subject-denied-in-first-cut"),
        ("safe/link-leaf", "symlink-subject-denied" if symlinks["leaf"] else "missing-member"),
        ("linkdir/report.txt", "symlink-ancestor-denied" if symlinks["ancestor"] else "missing-member"),
        ("fifo-subject", "non-regular-subject-denied" if (media_root / "fifo-subject").exists() else "missing-member"),
        ("missing/report.txt", "missing-member"),
    ]
    rejections = []
    for member, expected in hostile:
        observed = safe_capture.reject_reason(media_root, member)
        rejections.append({
            "member": member,
            "expected_reason": expected,
            "observed_reason": observed,
            "matched": observed == expected,
        })

    try:
        media_root_link = work_root / "media-root-link"
        os.symlink(media_root, media_root_link)
        symlink_media_root_reason = safe_capture.reject_reason(media_root_link, "safe/report.txt")
    except OSError:
        symlink_media_root_reason = "symlink-unavailable"

    invariants = {
        "regular_file_capture_passed": capture.digest == safe_capture.sha256_bytes(SUBJECT_BYTES),
        "dirfd_openat_capture": capture.capture_api == "dirfd-openat-no-symlink-components",
        "root_fd_pinned": capture.root_fd_pinned is True,
        "opened_with_openat": capture.opened_with_openat is True,
        "opened_with_no_follow": capture.opened_with_no_follow is True,
        "lstat_fstat_same_object": capture.lstat_fstat_same_object is True,
        "source_stable_after_copy": capture.source_stable_after_copy is True,
        "verified_after_copy": capture.verified_after_copy is True,
        "cas_first_publish_did_not_preexist": capture.cas_object_preexisted is False,
        "cas_write_policy_no_overwrite": capture.cas_write_policy == "no-overwrite-link-then-verify-existing",
        "cas_idempotent_recapture_verified_existing": recapture.cas_object_preexisted is True and recapture.cas_existing_object_verified is True and recapture.digest == capture.digest,
        "cas_corrupt_existing_object_denied": conflict_reason == "cas-object-digest-mismatch",
        "directory_subject_denied": any(r["member"] == "safe/dir-subject" and r["matched"] for r in rejections),
        "path_traversal_denied": any(r["member"] == "../escape.txt" and r["matched"] for r in rejections),
        "absolute_path_denied": any(r["member"] == "/absolute/report.txt" and r["matched"] for r in rejections),
        "symlink_leaf_denied": any(r["member"] == "safe/link-leaf" and r["matched"] for r in rejections),
        "symlink_ancestor_denied": any(r["member"] == "linkdir/report.txt" and r["matched"] for r in rejections),
        "non_regular_subject_denied": any(r["member"] == "fifo-subject" and r["matched"] for r in rejections),
        "symlink_media_root_denied": symlink_media_root_reason in {"symlink-media-root-denied", "symlink-unavailable"},
        "missing_member_denied": any(r["member"] == "missing/report.txt" and r["matched"] for r in rejections),
    }
    return {
        "kind": "removable.media.local.safe_capture.probe.receipt",
        "schema_version": "0.1",
        "probe_id": PROBE_ID,
        "generated_at_utc": generated_at_utc,
        "tool": "tools/removable_media_safe_capture.py",
        "mode": "cloudtainer-userland-openat-proof-no-real-mount",
        "capture": {
            "selected_member": capture.member,
            "normalized_member": capture.normalized_member,
            "digest": capture.digest,
            "size_bytes": capture.size_bytes,
            "store_locator": capture.store_rel,
            "capture_api": capture.capture_api,
            "root_fd_pinned": capture.root_fd_pinned,
            "opened_with_openat": capture.opened_with_openat,
            "opened_with_no_follow": capture.opened_with_no_follow,
            "ancestor_symlink_policy": capture.ancestor_symlink_policy,
            "leaf_symlink_policy": capture.leaf_symlink_policy,
            "regular_file_only": capture.regular_file_only,
            "lstat_fstat_same_object": capture.lstat_fstat_same_object,
            "source_stable_after_copy": capture.source_stable_after_copy,
            "verified_after_copy": capture.verified_after_copy,
            "cas_write_policy": capture.cas_write_policy,
            "cas_object_preexisted": capture.cas_object_preexisted,
            "cas_existing_object_verified": capture.cas_existing_object_verified,
        },
        "idempotent_recapture": {
            "digest": recapture.digest,
            "cas_write_policy": recapture.cas_write_policy,
            "cas_object_preexisted": recapture.cas_object_preexisted,
            "cas_existing_object_verified": recapture.cas_existing_object_verified,
        },
        "cas_conflict_rejection": {
            "precreated_locator": f"cas/sha256/{expected_hex}",
            "observed_reason": conflict_reason,
            "expected_reason": "cas-object-digest-mismatch",
            "matched": conflict_reason == "cas-object-digest-mismatch",
        },
        "hostile_members_checked": rejections,
        "symlink_media_root_rejection": symlink_media_root_reason,
        "symlink_fixture_created": symlinks,
        "invariants": invariants,
        "result": "passed" if all(invariants.values()) else "failed",
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("kind") != "removable.media.local.safe_capture.probe.receipt":
        errors.append("unexpected kind")
    if obj.get("probe_id") != PROBE_ID:
        errors.append("probe_id must bind r536")
    if obj.get("result") != "passed":
        errors.append("safe-capture probe must pass")
    capture = obj.get("capture", {}) if isinstance(obj.get("capture"), dict) else {}
    if capture.get("capture_api") != "dirfd-openat-no-symlink-components":
        errors.append("capture API must be dirfd/openat-shaped")
    for key in [
        "root_fd_pinned",
        "opened_with_openat",
        "opened_with_no_follow",
        "regular_file_only",
        "lstat_fstat_same_object",
        "source_stable_after_copy",
        "verified_after_copy",
    ]:
        if capture.get(key) is not True:
            errors.append(f"capture.{key} must be true")
    if capture.get("cas_write_policy") != "no-overwrite-link-then-verify-existing":
        errors.append("capture CAS write policy must be no-overwrite link then verify-existing")
    if capture.get("cas_object_preexisted") is not False:
        errors.append("first capture must publish a new CAS object")
    if capture.get("cas_existing_object_verified") is not False:
        errors.append("first capture must not claim an existing CAS object was verified")
    recapture = obj.get("idempotent_recapture", {}) if isinstance(obj.get("idempotent_recapture"), dict) else {}
    if recapture.get("cas_object_preexisted") is not True or recapture.get("cas_existing_object_verified") is not True:
        errors.append("idempotent recapture must verify the pre-existing CAS object instead of overwriting it")
    conflict = obj.get("cas_conflict_rejection", {}) if isinstance(obj.get("cas_conflict_rejection"), dict) else {}
    if conflict.get("observed_reason") != "cas-object-digest-mismatch" or conflict.get("matched") is not True:
        errors.append("corrupt pre-existing CAS object must fail closed with cas-object-digest-mismatch")

    reasons = {
        row.get("member"): row.get("observed_reason")
        for row in obj.get("hostile_members_checked", [])
        if isinstance(row, dict)
    }
    expected = {
        "../escape.txt": "non-relative-clean-member-path",
        "/absolute/report.txt": "absolute-member-path",
        "safe/dir-subject": "directory-subject-denied-in-first-cut",
        "safe/link-leaf": "symlink-subject-denied",
        "linkdir/report.txt": "symlink-ancestor-denied",
        "fifo-subject": "non-regular-subject-denied",
        "missing/report.txt": "missing-member",
    }
    symlinks = obj.get("symlink_fixture_created", {}) if isinstance(obj.get("symlink_fixture_created"), dict) else {}
    if not symlinks.get("leaf"):
        expected["safe/link-leaf"] = "missing-member"
    if not symlinks.get("ancestor"):
        expected["linkdir/report.txt"] = "missing-member"
    if reasons.get("fifo-subject") == "missing-member":
        expected["fifo-subject"] = "missing-member"
    root_reason = obj.get("symlink_media_root_rejection")
    if root_reason not in {"symlink-media-root-denied", "symlink-unavailable"}:
        errors.append(f"symlink media root observed {root_reason!r}, expected fail-closed denial")
    for member, reason in expected.items():
        if reasons.get(member) != reason:
            errors.append(f"{member}: observed {reasons.get(member)!r}, expected {reason!r}")
    invariants = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    for key, value in sorted(invariants.items()):
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def expected_receipt() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="derivebsd-safe-capture-check-") as tmp:
        return build_receipt(Path(tmp), FIXED_GENERATED_AT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help=f"refresh {EXPECTED.relative_to(ROOT)}")
    args = parser.parse_args()

    expected = expected_receipt()
    errors = semantic_errors(expected)
    if errors:
        print("Safe-capture self-check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    if args.write:
        write_json(EXPECTED, expected)
        print(f"wrote {EXPECTED.relative_to(ROOT)}")
        return 0

    if not EXPECTED.exists():
        print(f"Missing safe-capture receipt: {EXPECTED.relative_to(ROOT)}")
        print("Regenerate with: python3 tools/check_removable_media_safe_capture.py --write")
        return 1
    observed = json.loads(EXPECTED.read_text(encoding="utf-8"))
    observed_errors = semantic_errors(observed)
    if observed_errors:
        print("Safe-capture receipt FAILED.")
        for error in observed_errors:
            print("-", error)
        return 1
    if observed != expected:
        print("Safe-capture receipt is stale.")
        print("Regenerate with: python3 tools/check_removable_media_safe_capture.py --write")
        return 1
    print("Removable-media safe-capture check OK")
    print("Probe: dirfd-openat regular-file capture, symlink-root/leaf/ancestor and non-regular rejection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
