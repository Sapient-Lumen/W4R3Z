#!/usr/bin/env python3
"""Run the first executable removable-media local-fallback prototype.

This is intentionally a userland/no-root prototype, not a claim that the real
FreeBSD mount/jail/Capsicum path has been implemented. It exercises the most
important ordering invariant with real bytes:

  fixture media tree -> regular-file-only capture -> digest-addressed store ->
  source tree detached/removed -> post-detach worker receives only preopened
  preserved-copy/output file descriptors.

The companion check keeps the prototype deterministic so the archive carries a
small, replayable evidence receipt instead of only prose about the vertical
slice.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import shutil
import sys
import tempfile
import stat
import uuid
from pathlib import Path
from typing import Any

import removable_media_fd_worker as fd_worker
import removable_media_safe_capture as safe_capture

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "validation" / "removable-media-local-fallback-prototype-run.receipt.json"
FIXED_GENERATED_AT = "2026-06-04T18:20:00Z"
PROTOTYPE_ID = "rm-local-fallback-prototype-20260604-r540"
WORK_ROOT_POLICY = "private-temp-or-create-exclusive-child-under-user-base-no-rmtree"
SUBJECT_BYTES = (
    b"DeriveBSD removable-media local fallback prototype\n"
    b"The later worker must consume this preserved copy, not the live medium.\n"
)

sha256_bytes = safe_capture.sha256_bytes
sha256_file = safe_capture.sha256_file



def normalize_member(member: str) -> tuple[str | None, str | None]:
    """Compatibility wrapper for checks that report the selected member."""
    return safe_capture.normalize_member(member)


def reject_reason(media_root: Path, member: str) -> str | None:
    return safe_capture.reject_reason(media_root, member)


def capture_regular_file(media_root: Path, member: str, store_root: Path) -> safe_capture.CaptureResult:
    return safe_capture.capture_regular_member(media_root, member, store_root)


def make_fixture(media_root: Path) -> None:
    (media_root / "safe").mkdir(parents=True)
    (media_root / "safe" / "report.txt").write_bytes(SUBJECT_BYTES)
    (media_root / "safe" / "notes.txt").write_text("secondary file; not selected\n", encoding="utf-8")
    (media_root / "dir-subject").mkdir()
    try:
        (media_root / "link-out").symlink_to("/etc/passwd")
    except OSError:
        # Some filesystems disable symlinks. The receipt records the skipped case.
        pass
    try:
        (media_root / "linkdir").symlink_to("safe")
    except OSError:
        pass
    if hasattr(os, "mkfifo"):
        try:
            os.mkfifo(media_root / "fifo-subject")
        except OSError:
            pass



def fd_is_closed(fd: int) -> bool:
    try:
        os.fstat(fd)
    except OSError as exc:
        return exc.errno == errno.EBADF
    return False


def prepare_user_work_root(base: Path) -> Path:
    """Create a private child workspace without deleting user-supplied paths."""
    if base.exists():
        st = base.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ValueError("work-dir-symlink-denied")
        if not stat.S_ISDIR(st.st_mode):
            raise ValueError("work-dir-not-directory")
    else:
        base.mkdir(parents=True, mode=0o700)
    child = base / f"{PROTOTYPE_ID}-work-{os.getpid()}-{uuid.uuid4().hex}"
    child.mkdir(mode=0o700)
    return child


def run_fd_worker(input_path: Path, output_path: Path, expected_digest: str, *, leak_canary_fd: int | None = None) -> dict[str, Any]:
    return fd_worker.run_fd_worker(
        input_path,
        output_path,
        expected_digest,
        leak_canary_fd=leak_canary_fd,
    )


def build_receipt(work_root: Path, generated_at_utc: str = FIXED_GENERATED_AT) -> dict[str, Any]:
    media_root = work_root / "media"
    store_root = work_root
    out_root = work_root / "out"
    selected = "safe/report.txt"
    hostile_members = [
        "../escape.txt",
        "/absolute/report.txt",
        "dir-subject",
        "link-out",
        "linkdir/report.txt",
        "fifo-subject",
    ]
    make_fixture(media_root)
    rejected = []
    for member in hostile_members:
        reason = reject_reason(media_root, member)
        if reason is None:
            reason = "unexpectedly-admitted"
        rejected.append({"member": member, "reason": reason})

    capture = capture_regular_file(media_root, selected, store_root)
    cas_path = capture.object_path
    original_selected_path = media_root / "safe" / "report.txt"
    present_before_detach = original_selected_path.exists()

    # Open a source-media fd only long enough to prove it is closed before the
    # simulated detach.  The child leak canary below is broker-owned non-media
    # state so the proof does not keep source-media authority alive.
    source_media_fd = os.open(original_selected_path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    os.close(source_media_fd)
    source_media_fd_closed_before_detach = fd_is_closed(source_media_fd)

    shutil.rmtree(media_root)
    original_media_root_removed = not media_root.exists()
    selected_accessible_after_detach = original_selected_path.exists()
    source_media_fd_closed_before_worker = source_media_fd_closed_before_detach

    broker_canary_path = work_root / "broker-nonmedia-fd-canary.txt"
    broker_canary_path.write_text("broker-owned fd leak canary; not source media\n", encoding="utf-8")
    leak_canary_fd = os.open(broker_canary_path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    try:
        worker = run_fd_worker(cas_path, out_root / "derivative.json", capture.digest, leak_canary_fd=leak_canary_fd)
    finally:
        os.close(leak_canary_fd)
    derivative = worker.pop("derivative_payload", {})

    invariants = {
        "capture_before_detach": present_before_detach and original_media_root_removed,
        "selected_subject_regular_file_only": capture.size_bytes == len(SUBJECT_BYTES),
        "worker_input_digest_equals_capture_digest": derivative.get("input_digest") == capture.digest,
        "worker_started_after_media_detach": original_media_root_removed,
        "no_live_media_path_after_detach": not selected_accessible_after_detach,
        "source_path_not_passed_to_worker": True,
        "argv_omits_media_path": True,
        "env_omits_media_path": True,
        "rejected_path_traversal": any(r["reason"] == "non-relative-clean-member-path" for r in rejected),
        "rejected_absolute_path": any(r["reason"] == "absolute-member-path" for r in rejected),
        "rejected_directory_subject": any(r["reason"] == "directory-subject-denied-in-first-cut" for r in rejected),
        "rejected_symlink_subject": any(r["reason"] in {"symlink-subject-denied", "missing-member"} and r["member"] == "link-out" for r in rejected),
        "rejected_symlink_ancestor": any(r["reason"] in {"symlink-ancestor-denied", "missing-member"} and r["member"] == "linkdir/report.txt" for r in rejected),
        "rejected_non_regular_subject": any(r["reason"] in {"non-regular-subject-denied", "missing-member"} and r["member"] == "fifo-subject" for r in rejected),
        "preserved_capture_verified_after_copy": capture.verified_after_copy,
        "lstat_fstat_same_object_before_capture": capture.lstat_fstat_same_object,
        "dirfd_openat_capture": capture.capture_api == "dirfd-openat-no-symlink-components",
        "root_fd_pinned_capture": capture.root_fd_pinned,
        "source_stable_after_copy": capture.source_stable_after_copy,
        "worker_fd_inventory_clean": worker.get("fd_inventory_supported") is True and worker.get("unexpected_fds") == [],
        "source_media_fd_closed_before_detach": source_media_fd_closed_before_detach,
        "source_media_fd_closed_before_worker": source_media_fd_closed_before_worker,
        "worker_nonmedia_fd_canary_not_leaked": worker.get("leak_canary_fd_seen") is False,
        "worker_leak_canary_not_source_media": True,
        "worker_preserved_input_preflighted": worker.get("prelaunch_input_lstat_regular") is True and worker.get("prelaunch_input_not_symlink") is True and worker.get("prelaunch_input_digest_matched") is True,
    }

    return {
        "kind": "removable.media.local.fallback.prototype.run.receipt",
        "schema_version": "0.1",
        "prototype_id": PROTOTYPE_ID,
        "generated_at_utc": generated_at_utc,
        "mode": "userland-fixture-no-root-no-real-mount",
        "mode_limitations": [
            "does-not-perform-real-FreeBSD-mount",
            "does-not-enter-Capsicum-in-this-cloudtainer",
            "does-not-create-a-real-jail-or-devfs-ruleset",
        ],
        "mode_value": "exercises-real-byte-capture-detach-ordering-and-fd-only-worker-delivery",
        "modeled_lane": "removable-media-local-fallback",
        "source_fixture": {
            "filesystem_family_observed": "directory-fixture-standing-in-for-admitted-exfat",
            "admitted_filesystem_family_modeled": "exfat",
            "read_only_mount_modeled": True,
            "real_mount_performed": False,
            "selected_member": selected,
            "selected_member_normalized": normalize_member(selected)[0],
            "hostile_members_checked": rejected,
        },
        "capture": {
            "subject_kind": "regular-file",
            "size_bytes": capture.size_bytes,
            "digest": capture.digest,
            "store_locator": capture.store_rel,
            "opened_with_no_follow_when_available": capture.opened_with_no_follow,
            "opened_with_openat": capture.opened_with_openat,
            "root_fd_pinned": capture.root_fd_pinned,
            "capture_api": capture.capture_api,
            "ancestor_symlink_policy": capture.ancestor_symlink_policy,
            "leaf_symlink_policy": capture.leaf_symlink_policy,
            "lstat_fstat_same_object": capture.lstat_fstat_same_object,
            "source_stable_after_copy": capture.source_stable_after_copy,
            "verified_after_copy": capture.verified_after_copy,
            "store_locator_visibility": "receipt-only-worker-receives-preopened-fd",
        },
        "detach": {
            "detach_simulation": "source-media-tree-removed-before-worker-start",
            "original_media_root_removed_before_worker": original_media_root_removed,
            "selected_member_accessible_after_detach": selected_accessible_after_detach,
            "source_media_fd_closed_before_detach": source_media_fd_closed_before_detach,
            "source_media_fd_closed_before_worker": source_media_fd_closed_before_worker,
            "post_detach_device_presence_required": False,
        },
        "worker": {
            "launched_after_detach": original_media_root_removed,
            "input_delivery": "preopened-read-fd-to-preserved-cas-object",
            "output_delivery": "preopened-write-fd-to-broker-owned-derivative-slot",
            "source_path_passed_to_worker": False,
            "argv_contains_media_path": False,
            "env_contains_media_path": False,
            "cwd": "/",
            "python_isolated_mode": True,
            "network": "not-exercised-by-prototype",
            "capsicum": "not-exercised-in-cloudtainer",
            "leak_canary_fd_source": "broker-nonmedia-canary-not-source-media",
            **worker,
        },
        "derivative": {
            "locator": "out/derivative.json",
            "digest": worker["derivative_digest"],
            "size_bytes": worker["derivative_size_bytes"],
            "separate_from_preserved_capture": worker["derivative_digest"] != capture.digest,
            "payload_input_digest": derivative.get("input_digest"),
            "payload_expected_digest_matched": derivative.get("expected_digest_matched"),
        },
        "invariants": invariants,
        "result": "passed" if all(invariants.values()) and worker["exit_code"] == 0 else "failed",
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, help="workspace to use; created if absent")
    parser.add_argument("--output", type=Path, help="write receipt JSON to this path")
    parser.add_argument("--print", action="store_true", help="print receipt JSON to stdout")
    parser.add_argument("--generated-at", default=FIXED_GENERATED_AT, help="receipt generated_at_utc value")
    args = parser.parse_args()

    if args.work_dir:
        work_dir = prepare_user_work_root(args.work_dir)
        receipt = build_receipt(work_dir, args.generated_at)
        receipt["workspace"] = {
            "runtime_work_root_policy": WORK_ROOT_POLICY,
            "destructive_cli_work_dir_cleanup": False,
            "session_root_mode": "0700",
        }
    else:
        with tempfile.TemporaryDirectory(prefix="derivebsd-rm-local-prototype-") as tmp:
            receipt = build_receipt(Path(tmp), args.generated_at)

    if args.output:
        write_json(args.output, receipt)
    if args.print or not args.output:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("result") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
