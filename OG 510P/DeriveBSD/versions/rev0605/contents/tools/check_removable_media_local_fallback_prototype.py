#!/usr/bin/env python3
"""Validate the executable removable-media local-fallback prototype receipt."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import run_removable_media_local_fallback_prototype as prototype

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "validation" / "removable-media-local-fallback-prototype-run.receipt.json"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.fallback.prototype.run.receipt", "unexpected kind")
    require(errors, obj.get("prototype_id") == prototype.PROTOTYPE_ID, "prototype_id must bind current executable prototype")
    require(errors, obj.get("result") == "passed", "prototype result must pass")
    require(errors, obj.get("mode_value") == "exercises-real-byte-capture-detach-ordering-and-fd-only-worker-delivery", "mode value must stay executable-substance-shaped")

    source = obj.get("source_fixture", {})
    capture = obj.get("capture", {})
    detach = obj.get("detach", {})
    worker = obj.get("worker", {})
    derivative = obj.get("derivative", {})
    invariants = obj.get("invariants", {})

    require(errors, source.get("selected_member") == "safe/report.txt", "selected fixture subject drifted")
    reasons = {row.get("member"): row.get("reason") for row in source.get("hostile_members_checked", []) if isinstance(row, dict)}
    require(errors, reasons.get("../escape.txt") == "non-relative-clean-member-path", "path traversal must be rejected")
    require(errors, reasons.get("/absolute/report.txt") == "absolute-member-path", "absolute path must be rejected")
    require(errors, reasons.get("dir-subject") == "directory-subject-denied-in-first-cut", "directory subject must be rejected")
    require(errors, reasons.get("link-out") in {"symlink-subject-denied", "missing-member"}, "symlink subject must be rejected or unavailable")
    require(errors, reasons.get("linkdir/report.txt") in {"symlink-ancestor-denied", "missing-member"}, "symlink ancestor must be rejected or unavailable")
    require(errors, reasons.get("fifo-subject") in {"non-regular-subject-denied", "missing-member"}, "non-regular subject must be rejected or unavailable")

    digest = capture.get("digest")
    require(errors, isinstance(digest, str) and digest.startswith("sha256:"), "capture digest must be sha256")
    require(errors, capture.get("subject_kind") == "regular-file", "capture must be regular-file-only")
    require(errors, capture.get("verified_after_copy") is True, "capture copy must be verified")
    require(errors, capture.get("capture_api") == "dirfd-openat-no-symlink-components", "capture must use dirfd/openat no-symlink path walk")
    require(errors, capture.get("opened_with_openat") is True, "capture must open through openat/dir_fd")
    require(errors, capture.get("root_fd_pinned") is True, "capture must pin the media root fd")
    require(errors, capture.get("opened_with_no_follow_when_available") is True, "capture must request no-follow opens when available")
    require(errors, capture.get("ancestor_symlink_policy") == "deny-each-ancestor-by-openat-o_directory-o_nofollow", "capture must deny symlink ancestors")
    require(errors, capture.get("leaf_symlink_policy") == "deny-leaf-by-openat-o_nofollow", "capture must deny symlink leaves")
    require(errors, capture.get("lstat_fstat_same_object") is True, "capture must prove lstat/fstat object stability")
    require(errors, capture.get("store_locator_visibility") == "receipt-only-worker-receives-preopened-fd", "worker must not receive store namespace authority")

    require(errors, detach.get("original_media_root_removed_before_worker") is True, "source media tree must be gone before worker")
    require(errors, detach.get("selected_member_accessible_after_detach") is False, "selected live media path must not survive detach")
    require(errors, detach.get("source_media_fd_closed_before_detach") is True, "source media fd must be closed before detach")
    require(errors, detach.get("source_media_fd_closed_before_worker") is True, "source media fd must be closed before worker launch")
    require(errors, detach.get("post_detach_device_presence_required") is False, "post-detach work must not require device presence")

    require(errors, worker.get("launched_after_detach") is True, "worker must launch after detach")
    require(errors, worker.get("input_delivery") == "preopened-read-fd-to-preserved-cas-object", "worker input must be preopened preserved-copy fd")
    require(errors, worker.get("output_delivery") == "preopened-write-fd-to-broker-owned-derivative-slot", "worker output must be preopened derivative slot")
    require(errors, worker.get("source_path_passed_to_worker") is False, "worker must not receive source path")
    require(errors, worker.get("argv_contains_media_path") is False, "worker argv must not contain media path")
    require(errors, worker.get("env_contains_media_path") is False, "worker env must not contain media path")
    require(errors, worker.get("fd_inventory_supported") is True, "worker must report fd inventory without /proc dependency")
    require(errors, worker.get("prelaunch_input_lstat_regular") is True, "prelaunch input must be lstat-regular before fd delegation")
    require(errors, worker.get("prelaunch_input_not_symlink") is True, "prelaunch input must not be a symlink before fd delegation")
    require(errors, worker.get("prelaunch_input_digest") == digest, "prelaunch input digest must match captured digest")
    require(errors, worker.get("prelaunch_input_digest_matched") is True, "prelaunch input digest check must pass before fd delegation")
    require(errors, worker.get("unexpected_fds") == [], "worker must not see unexpected inherited fds")
    require(errors, worker.get("leak_canary_fd_seen") is False, "worker must not inherit broker non-media fd canary")
    require(errors, worker.get("leak_canary_fd_source") == "broker-nonmedia-canary-not-source-media", "fd leak canary must not be source-media authority")
    require(errors, worker.get("exit_code") == 0, "worker must exit successfully")

    require(errors, derivative.get("payload_input_digest") == digest, "derivative payload must bind captured digest")
    require(errors, derivative.get("payload_expected_digest_matched") is True, "worker must verify expected digest")
    require(errors, derivative.get("separate_from_preserved_capture") is True, "derivative must not overwrite preserved capture")

    for key, value in sorted(invariants.items()):
        require(errors, value is True, f"invariant {key} must be true")
    return errors


def work_dir_policy_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-local-prototype-workdir-") as tmp:
        base = Path(tmp) / "user-base"
        base.mkdir()
        sentinel = base / "keep.txt"
        sentinel.write_text("must survive prototype run\n", encoding="utf-8")
        out = Path(tmp) / "receipt.json"
        import subprocess, sys
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools" / "run_removable_media_local_fallback_prototype.py"),
                "--work-dir",
                str(base),
                "--output",
                str(out),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        require(errors, proc.returncode == 0, f"prototype with user work-dir must pass, rc={proc.returncode}, stderr={proc.stderr[:200]!r}")
        require(errors, sentinel.exists(), "prototype must not delete user-supplied work-dir sentinel")
        children = [p for p in base.iterdir() if p.is_dir()]
        require(errors, len(children) == 1, "prototype must create one private child under user work-dir")
        if out.exists():
            obj = json.loads(out.read_text(encoding="utf-8"))
            require(errors, obj.get("workspace", {}).get("runtime_work_root_policy") == prototype.WORK_ROOT_POLICY, "prototype work-dir receipt must bind no-rmtree policy")
            require(errors, obj.get("workspace", {}).get("destructive_cli_work_dir_cleanup") is False, "prototype work-dir receipt must deny destructive cleanup")
    return errors


def expected_receipt() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-local-prototype-check-") as tmp:
        return prototype.build_receipt(Path(tmp), prototype.FIXED_GENERATED_AT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help=f"refresh {EXAMPLE.relative_to(ROOT)}")
    args = parser.parse_args()

    expected = expected_receipt()
    errors = semantic_errors(expected)
    errors.extend(work_dir_policy_errors())
    if errors:
        print("Removable-media local fallback prototype self-check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    if args.write:
        prototype.write_json(EXAMPLE, expected)
        print(f"wrote {EXAMPLE.relative_to(ROOT)}")
        return 0

    if not EXAMPLE.exists():
        print(f"Missing prototype receipt: {EXAMPLE.relative_to(ROOT)}")
        print("Regenerate with: python3 tools/check_removable_media_local_fallback_prototype.py --write")
        return 1
    observed = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    observed_errors = semantic_errors(observed)
    if observed_errors:
        print("Removable-media local fallback prototype receipt FAILED.")
        for error in observed_errors:
            print("-", error)
        return 1
    if observed != expected:
        print("Removable-media local fallback prototype receipt is stale.")
        print("Regenerate with: python3 tools/check_removable_media_local_fallback_prototype.py --write")
        return 1

    print("Removable-media local fallback prototype check OK")
    print("Prototype: regular file -> verified CAS capture -> source detach -> fd-only post-detach worker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
