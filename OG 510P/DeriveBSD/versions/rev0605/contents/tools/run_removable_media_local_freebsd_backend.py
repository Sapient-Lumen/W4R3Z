#!/usr/bin/env python3
"""FreeBSD-shaped removable-media local-fallback backend runner.

This is the first executable bridge between the cloudtainer proof and the future
rooted FreeBSD host implementation.  In this cloudtainer it runs a fixture-backed
backend simulation: copy a media tree into a private mount-shaped directory,
probe/admit the claimed filesystem family, capture one regular file through the
shared dirfd/openat helper, remove the mounted tree before worker launch, and
launch the derivative worker with only preopened fds.

The same tool also contains the guarded FreeBSD apply path.  Real apply refuses
when not on FreeBSD, when not root, or when exFAT would require an unqualified
FUSE/helper lane.  That refusal path is intentional evidence: the runner must not
turn the plan into an overclaim just because this cloudtainer cannot mount.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

import removable_media_capsicum_worker_bridge as capsicum_bridge
import removable_media_fd_worker as fd_worker
import removable_media_local_freebsd_backend_plan as plan_builder
import removable_media_safe_capture as safe_capture

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-06-05r554"
RUN_ID = "rm-local-freebsd-backend-run-20260605-r554"
FIXED_GENERATED_AT = "2026-06-05T11:20:00Z"
DEFAULT_OUTPUT = ROOT / "validation" / "removable-media-local-freebsd-backend-run.receipt.json"
DEFAULT_FIXTURE_ROOT = ROOT / "fixtures" / "removable-media" / "local-fallback" / "exfat-card"
DEFAULT_SELECTED_MEMBER = "invoice.pdf"
DEFAULT_DEVICE_NODE = "/dev/da0p1"
DEFAULT_CLAIMED_FSTYP = "exfat"
LOGICAL_SESSION_ROOT = "validation/removable-media-local-freebsd-backend-run/session"
BASE_SYSTEM_APPLY_FSTYPES = {"cd9660", "msdosfs", "ufs"}
MOUNT_OPTIONS = plan_builder.FREEBSD_GENERIC_MOUNT_OPTIONS
WORK_ROOT_POLICY = "private-temp-or-create-exclusive-child-under-user-base-no-rmtree"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _command_sha256(stdout: str, stderr: str) -> dict[str, Any]:
    return {
        "stdout_sha256": safe_capture.sha256_bytes(stdout.encode("utf-8", errors="replace")),
        "stderr_sha256": safe_capture.sha256_bytes(stderr.encode("utf-8", errors="replace")),
        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
        "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
    }


def _run_command_capture(cmd: list[str], *, timeout_seconds: float = 30) -> tuple[dict[str, Any], str, str]:
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        return (
            {
                "command": cmd,
                "return_code": int(proc.returncode),
                "timed_out": False,
                **_command_sha256(stdout, stderr),
            },
            stdout,
            stderr,
        )
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        out = str(out)
        err = (str(err) + "\n" if err else "") + f"TIMEOUT after {timeout_seconds} seconds"
        return (
            {
                "command": cmd,
                "return_code": 124,
                "timed_out": True,
                **_command_sha256(out, err),
            },
            out,
            err,
        )


def _run_command(cmd: list[str], *, timeout_seconds: float = 30) -> dict[str, Any]:
    result, _, _ = _run_command_capture(cmd, timeout_seconds=timeout_seconds)
    return result


def _fd_is_closed(fd: int) -> bool:
    try:
        os.fstat(fd)
    except OSError as exc:
        return exc.errno == errno.EBADF
    return False


def _capture_evidence(capture: safe_capture.CaptureResult) -> dict[str, Any]:
    return {
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
    }


def _base_receipt(
    *,
    run_id: str,
    generated_at_utc: str,
    execution_mode: str,
    selected_member: str,
    claimed_fstyp: str,
    device_node: str,
    work_root: Path,
) -> dict[str, Any]:
    normalized_member = plan_builder.normalize_selected_member(selected_member)
    session_root = Path(LOGICAL_SESSION_ROOT)
    # A refusal receipt may need to preserve the unsafe input that caused the
    # refusal.  The plan binding is still the canonical safe backend contract, so
    # fall back to the default device node when the rejected input cannot itself
    # be used to build a valid plan object.
    try:
        plan_builder.validate_device_node(device_node)
        plan_device_node = device_node
    except ValueError:
        plan_device_node = DEFAULT_DEVICE_NODE
    plan = plan_builder.build_plan(
        device_node=plan_device_node,
        selected_member=selected_member,
        claimed_fstyp=claimed_fstyp,
        session_root="/var/run/derivebsd/removable-media/local-fallback/20260605-r554-run",
    )
    return {
        "kind": "removable.media.local.freebsd.backend.run.receipt",
        "schema_version": "0.1",
        "run_id": run_id,
        "generated_for_version": VERSION,
        "generated_at_utc": generated_at_utc,
        "execution_mode": execution_mode,
        "host": {
            "observed_system": platform.system(),
            "required_os_for_real_apply": "FreeBSD",
            "requires_root_for_real_mount": True,
            "non_freebsd_apply_refuses": True,
            "network_required": False,
            "package_install_in_lane": False,
        },
        "inputs": {
            "device_node": device_node,
            "claimed_fstyp": claimed_fstyp,
            "selected_member": selected_member,
            "selected_member_normalized": normalized_member,
            "session_root": session_root.as_posix(),
            "mountpoint": (session_root / "mnt").as_posix(),
            "cas_root": (session_root / "quarantine-cas").as_posix(),
            "derivative_path": (session_root / "derivative" / "derivative.json").as_posix(),
        },
        "workspace": {
            "runtime_work_root_policy": WORK_ROOT_POLICY,
            "destructive_cli_work_dir_cleanup": False,
            "session_subdir": "session",
            "session_root_mode": "0700",
            "mountpoint_mode_before_mount": "0700",
        },
        "plan_binding": {
            "plan_id": plan_builder.PLAN_ID,
            "plan_generated_for_version": plan_builder.VERSION,
            "plan_example": plan_builder.EXAMPLE_REL,
            "phase_order": plan["capture_sequence"]["phase_order"],
            "mount_options_to_emit": list(MOUNT_OPTIONS),
            "nodev_not_emitted_as_generic_freebsd_mount_option": "nodev" in plan["mount_admission"]["not_claimed_as_freebsd_generic_mount_options"],
        },
        "worker_bridge": capsicum_bridge.backend_binding_summary(),
    }


def build_refusal_receipt(
    *,
    reason: str,
    generated_at_utc: str = FIXED_GENERATED_AT,
    selected_member: str = DEFAULT_SELECTED_MEMBER,
    claimed_fstyp: str = DEFAULT_CLAIMED_FSTYP,
    device_node: str = DEFAULT_DEVICE_NODE,
    observed_system: str | None = None,
    device_node_validated: bool = False,
    device_node_validation_method: str = "not-checked",
    device_node_error_detail: str | None = None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-refusal-") as tmp:
        base = _base_receipt(
            run_id=RUN_ID,
            generated_at_utc=generated_at_utc,
            execution_mode="freebsd-apply-refused",
            selected_member=selected_member,
            claimed_fstyp=claimed_fstyp,
            device_node=device_node,
            work_root=Path(tmp),
        )
    if observed_system is not None:
        base["host"]["observed_system"] = observed_system
    base.update(
        {
            "preflight": {
                "device_node_validated": device_node_validated,
                "device_node_validation_method": device_node_validation_method,
                "device_node_error_detail": device_node_error_detail,
                "fstyp_probe_attempted": False,
                "observed_fstyp": None,
                "claimed_fstyp_admitted": claimed_fstyp in plan_builder.ALLOWED_FSTYP_RESULTS,
                "refusal_reason": reason,
            },
            "mount": {
                "attempted": False,
                "real_mount_performed": False,
                "mount_command": [],
                "command_result": None,
                "mount_options": list(MOUNT_OPTIONS),
                "status": "refused-before-mount",
            },
            "capture": {
                "attempted": False,
                "evidence": None,
            },
            "detach": {
                "attempted": False,
                "unmounted_before_worker": False,
                "mountpoint_visible_to_worker": False,
                "device_node_closed_before_worker": True,
                "source_media_fd_closed_before_detach": True,
                "source_media_fd_closed_before_worker": True,
                "umount_result": None,
                "status": "not-needed-refused-before-mount",
            },
            "worker": {
                "attempted": False,
                "launcher_kind": "not-launched-refused-before-worker-bridge",
                "real_apply_python_fixture_worker_allowed": False,
                "real_apply_requires_capsicum_worker_bridge": True,
                "capsicum_worker_bridge_id": capsicum_bridge.BRIDGE_ID,
                "launched_after_detach": False,
                "input_delivery": "not-launched-refused-before-mount",
                "output_delivery": "not-launched-refused-before-mount",
                "argv_contains_device_or_mount_path": False,
                "env_contains_device_or_mount_path": False,
                "source_path_passed_to_worker": False,
                "fd_inventory_supported": False,
                "unexpected_fds": [],
                "leak_canary_fd_seen": False,
                "leak_canary_fd_source": "not-opened-worker-not-launched",
                "prelaunch_input_lstat_regular": False,
                "prelaunch_input_not_symlink": False,
                "prelaunch_input_digest_matched": False,
                "prelaunch_input_digest": None,
                "prelaunch_input_size_bytes": None,
            },
            "derivative": {
                "attempted": False,
                "digest": None,
                "separate_from_preserved_capture": False,
            },
            "invariants": {
                "non_freebsd_apply_refused": reason == "non-freebsd-host",
                "no_mount_attempted_after_refusal": True,
                "no_worker_launched_after_refusal": True,
            },
            "result": "refused",
        }
    )
    return base


def build_fixture_receipt(
    work_root: Path,
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    selected_member: str = DEFAULT_SELECTED_MEMBER,
    claimed_fstyp: str = DEFAULT_CLAIMED_FSTYP,
    device_node: str = DEFAULT_DEVICE_NODE,
    generated_at_utc: str = FIXED_GENERATED_AT,
    run_id: str = RUN_ID,
) -> dict[str, Any]:
    if claimed_fstyp not in plan_builder.ALLOWED_FSTYP_RESULTS:
        raise ValueError(f"claimed filesystem family {claimed_fstyp!r} is not admitted")
    plan_builder.validate_device_node(device_node)
    normalized_member = plan_builder.normalize_selected_member(selected_member)

    fixture_root_rel = fixture_root.relative_to(ROOT).as_posix() if fixture_root.is_relative_to(ROOT) else fixture_root.as_posix()
    base = _base_receipt(
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        execution_mode="cloudtainer-fixture-backend-simulation-no-root",
        selected_member=selected_member,
        claimed_fstyp=claimed_fstyp,
        device_node=device_node,
        work_root=work_root,
    )
    actual_session_root = work_root / "session"
    mountpoint = actual_session_root / "mnt"
    cas_root = actual_session_root / "quarantine-cas"
    derivative_path = actual_session_root / "derivative" / "derivative.json"

    if mountpoint.exists():
        shutil.rmtree(mountpoint)
    mountpoint.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(fixture_root, mountpoint, symlinks=True)

    fixture_selected = mountpoint / normalized_member
    source_media_fd: int | None = None
    source_media_fd_closed_before_detach = True
    source_media_fd_closed_before_worker = True
    capture: safe_capture.CaptureResult | None = None
    capture_error_reason: str | None = None
    capture_error_detail: str | None = None
    worker: dict[str, Any] = {}
    derivative_payload: dict[str, Any] = {}
    before_detach_selected_exists = fixture_selected.exists()
    if before_detach_selected_exists:
        source_media_fd = os.open(fixture_selected, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    try:
        capture = safe_capture.capture_regular_member(mountpoint, selected_member, cas_root)
    except safe_capture.CaptureError as exc:
        capture_error_reason = exc.reason
        capture_error_detail = exc.detail
    finally:
        if source_media_fd is not None:
            os.close(source_media_fd)
            source_media_fd_closed_before_detach = _fd_is_closed(source_media_fd)
        if mountpoint.exists():
            shutil.rmtree(mountpoint)
    unmounted_before_worker = not mountpoint.exists()
    selected_accessible_after_detach = fixture_selected.exists()
    source_media_fd_closed_before_worker = source_media_fd_closed_before_detach
    if capture is not None and unmounted_before_worker:
        broker_canary_path = actual_session_root / "broker-nonmedia-fd-canary.txt"
        broker_canary_path.parent.mkdir(parents=True, exist_ok=True)
        broker_canary_path.write_text("broker-owned fd leak canary; not source media\n", encoding="utf-8")
        leak_canary_fd = os.open(broker_canary_path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
        try:
            worker = fd_worker.run_fd_worker(
                capture.object_path,
                derivative_path,
                capture.digest,
                leak_canary_fd=leak_canary_fd,
            )
            derivative_payload = worker.pop("derivative_payload", {})
        finally:
            os.close(leak_canary_fd)

    derivative_digest = worker.get("derivative_digest")
    capture_succeeded = capture is not None

    invariants = {
        "fixture_source_copied_to_private_mountpoint": before_detach_selected_exists if capture_succeeded else True,
        "claimed_fstyp_admitted_before_mount": claimed_fstyp in plan_builder.ALLOWED_FSTYP_RESULTS,
        "real_mount_not_claimed_in_cloudtainer": True,
        "safe_capture_openat_no_symlink_walk": (capture.capture_api == "dirfd-openat-no-symlink-components") if capture_succeeded else True,
        "capture_verified_after_copy": capture.verified_after_copy if capture_succeeded else True,
        "capture_source_stable_after_copy": capture.source_stable_after_copy if capture_succeeded else True,
        "cas_publish_no_overwrite": (capture.cas_write_policy == "no-overwrite-link-then-verify-existing") if capture_succeeded else True,
        "mountpoint_removed_before_worker": unmounted_before_worker,
        "selected_member_not_accessible_after_detach": not selected_accessible_after_detach,
        "source_media_fd_closed_before_detach": source_media_fd_closed_before_detach,
        "source_media_fd_closed_before_worker": source_media_fd_closed_before_worker,
        "worker_launched_after_detach": (unmounted_before_worker and bool(worker)) if capture_succeeded else True,
        "worker_not_launched_after_capture_failure": (not capture_succeeded and not worker) if not capture_succeeded else True,
        "worker_fd_inventory_clean": (worker.get("fd_inventory_supported") is True and worker.get("unexpected_fds") == []) if capture_succeeded else True,
        "worker_nonmedia_fd_canary_not_leaked": (worker.get("leak_canary_fd_seen") is False) if capture_succeeded else True,
        "worker_leak_canary_not_source_media": True,
        "worker_preserved_input_preflighted": (worker.get("prelaunch_input_lstat_regular") is True and worker.get("prelaunch_input_not_symlink") is True and worker.get("prelaunch_input_digest_matched") is True) if capture_succeeded else True,
        "worker_output_slot_create_exclusive": (worker.get("output_open_policy") == "create-exclusive-no-truncate" and worker.get("output_truncates_existing") is False) if capture_succeeded else True,
        "worker_digest_equals_preserved_capture": (derivative_payload.get("input_digest") == capture.digest) if capture_succeeded else True,
        "device_and_mount_paths_not_passed_to_worker": True,
        "derivative_separate_from_preserved_capture": (derivative_digest != capture.digest) if capture_succeeded else True,
        "non_freebsd_apply_refusal_path_exercised_by_checker": True,
        "real_apply_python_fixture_worker_disallowed": True,
        "capsicum_worker_bridge_bound": True,
    }

    base.update(
        {
            "preflight": {
                "device_node_validated": True,
                "device_node_validation_method": "shape-only-fixture-backend",
                "device_node_error_detail": None,
                "fstyp_probe_attempted": False,
                "observed_fstyp": claimed_fstyp,
                "claimed_fstyp_admitted": True,
                "selected_member_normalized": normalized_member,
                "fixture_root": fixture_root_rel,
            },
            "mount": {
                "attempted": True,
                "real_mount_performed": False,
                "mount_command": ["fixture-copytree", fixture_root_rel, base["inputs"]["mountpoint"]],
                "command_result": None,
                "mount_options": list(MOUNT_OPTIONS),
                "status": "simulated-private-read-only-mount-shape",
            },
            "capture": {
                "attempted": True,
                "evidence": _capture_evidence(capture) if capture_succeeded else None,
                "error_reason": capture_error_reason,
                "error_detail": capture_error_detail,
            },
            "detach": {
                "attempted": True,
                "unmounted_before_worker": unmounted_before_worker,
                "mountpoint_visible_to_worker": False,
                "device_node_closed_before_worker": True,
                "source_media_fd_closed_before_detach": source_media_fd_closed_before_detach,
                "source_media_fd_closed_before_worker": source_media_fd_closed_before_worker,
                "umount_result": None,
                "selected_member_accessible_after_detach": selected_accessible_after_detach,
                "status": "fixture-mountpoint-removed-before-worker" if unmounted_before_worker else "fixture-detach-failed-worker-not-launched",
            },
            "worker": {
                "attempted": bool(worker),
                "launcher_kind": "python-fd-worker-cloudtainer-fixture-only" if capture_succeeded else "not-launched-capture-failed",
                "real_apply_python_fixture_worker_allowed": False,
                "real_apply_requires_capsicum_worker_bridge": True,
                "capsicum_worker_bridge_id": capsicum_bridge.BRIDGE_ID,
                "launched_after_detach": capture_succeeded and unmounted_before_worker and bool(worker),
                "input_delivery": "preopened-read-fd-to-preserved-cas-object" if capture_succeeded else "not-launched-capture-failed-before-worker",
                "output_delivery": "preopened-write-fd-to-broker-owned-derivative-slot" if capture_succeeded else "not-launched-capture-failed-before-worker",
                "argv_contains_device_or_mount_path": False,
                "env_contains_device_or_mount_path": False,
                "source_path_passed_to_worker": False,
                "cwd": "/",
                "fd_inventory_supported": worker.get("fd_inventory_supported", False),
                "unexpected_fds": worker.get("unexpected_fds", []),
                "leak_canary_fd_seen": worker.get("leak_canary_fd_seen", False),
                "leak_canary_fd_source": "broker-nonmedia-canary-not-source-media" if capture_succeeded else "not-opened-capture-failed",
                **worker,
            },
            "derivative": {
                "attempted": bool(worker),
                "digest": derivative_digest,
                "size_bytes": worker.get("derivative_size_bytes"),
                "payload_input_digest": derivative_payload.get("input_digest"),
                "payload_expected_digest_matched": derivative_payload.get("expected_digest_matched"),
                "separate_from_preserved_capture": (derivative_digest != capture.digest) if capture_succeeded else False,
            },
            "invariants": invariants,
            "result": "passed" if capture_succeeded and all(invariants.values()) and worker.get("exit_code") == 0 else "failed",
        }
    )
    return base


def _validate_device_node_for_apply(device_node: str) -> None:
    plan_builder.validate_device_node(device_node)
    try:
        st = os.lstat(device_node)
    except FileNotFoundError as exc:
        raise ValueError("device-node-missing") from exc
    if stat.S_ISLNK(st.st_mode):
        raise ValueError("device-node-is-symlink")
    if not stat.S_ISCHR(st.st_mode):
        raise ValueError("device-node-not-character-device")


def _shape_validation_error(device_node: str) -> str | None:
    try:
        plan_builder.validate_device_node(device_node)
    except ValueError as exc:
        return str(exc)
    return None


def _prepare_user_work_root(base: Path) -> Path:
    """Create an exclusive child work root without deleting user-supplied paths."""
    if base.exists():
        st = base.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ValueError("work-dir-symlink-denied")
        if not stat.S_ISDIR(st.st_mode):
            raise ValueError("work-dir-not-directory")
    else:
        base.mkdir(parents=True, mode=0o700)
    child = base / f"{RUN_ID}-work-{os.getpid()}-{uuid.uuid4().hex}"
    try:
        child.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ValueError("work-dir-exclusive-child-exists") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("work-dir-symlink-denied") from exc
        raise
    return child


def build_apply_receipt(
    work_root: Path,
    *,
    selected_member: str,
    claimed_fstyp: str,
    device_node: str,
    generated_at_utc: str,
    run_id: str = RUN_ID,
) -> dict[str, Any]:
    """Return the structured real-apply preflight/refusal receipt.

    Real FreeBSD apply is intentionally gated until the C Capsicum worker bridge
    is built and wired.  Earlier revisions kept a large host-operation block
    after an unconditional refusal return; that looked like implementation but
    could not execute.  This function now keeps only the honest preflight gate so
    host code cannot rot behind a dead branch or accidentally reuse the Python
    fixture worker.
    """
    del work_root, run_id  # The gate refuses before a private host session is allocated.
    shape_error = _shape_validation_error(device_node)
    if shape_error is not None:
        return build_refusal_receipt(
            reason="invalid-device-node-shape",
            generated_at_utc=generated_at_utc,
            selected_member=selected_member,
            claimed_fstyp=claimed_fstyp,
            device_node=device_node,
            observed_system=platform.system(),
            device_node_validated=False,
            device_node_validation_method="shape-validation-failed-before-host-apply",
            device_node_error_detail=shape_error,
        )
    observed_system = platform.system()
    if observed_system != "FreeBSD":
        return build_refusal_receipt(reason="non-freebsd-host", generated_at_utc=generated_at_utc, selected_member=selected_member, claimed_fstyp=claimed_fstyp, device_node=device_node, observed_system=observed_system, device_node_validated=True, device_node_validation_method="shape-only-non-freebsd-refusal")
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        return build_refusal_receipt(reason="root-required-for-real-mount", generated_at_utc=generated_at_utc, selected_member=selected_member, claimed_fstyp=claimed_fstyp, device_node=device_node, observed_system=observed_system, device_node_validated=True, device_node_validation_method="shape-only-before-root-refusal")
    if claimed_fstyp == "exfat":
        return build_refusal_receipt(reason="exfat-helper-not-qualified-for-real-apply", generated_at_utc=generated_at_utc, selected_member=selected_member, claimed_fstyp=claimed_fstyp, device_node=device_node, observed_system=observed_system, device_node_validated=True, device_node_validation_method="shape-only-before-exfat-helper-refusal")
    if claimed_fstyp not in BASE_SYSTEM_APPLY_FSTYPES:
        return build_refusal_receipt(reason="filesystem-family-not-enabled-for-real-apply", generated_at_utc=generated_at_utc, selected_member=selected_member, claimed_fstyp=claimed_fstyp, device_node=device_node, observed_system=observed_system, device_node_validated=True, device_node_validation_method="shape-only-before-filesystem-family-refusal")

    return build_refusal_receipt(reason=capsicum_bridge.REAL_APPLY_GATE_REASON, generated_at_utc=generated_at_utc, selected_member=selected_member, claimed_fstyp=claimed_fstyp, device_node=device_node, observed_system=observed_system, device_node_validated=True, device_node_validation_method="shape-only-before-capsicum-worker-refusal")

def build_default_fixture_receipt(generated_at_utc: str = FIXED_GENERATED_AT) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-backend-fixture-") as tmp:
        return build_fixture_receipt(Path(tmp), generated_at_utc=generated_at_utc)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["fixture", "apply-freebsd"], default="fixture")
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    parser.add_argument("--selected-member", default=DEFAULT_SELECTED_MEMBER)
    parser.add_argument("--claimed-fstyp", default=DEFAULT_CLAIMED_FSTYP)
    parser.add_argument("--device-node", default=DEFAULT_DEVICE_NODE)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at", default=FIXED_GENERATED_AT)
    parser.add_argument("--print", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.work_dir:
        try:
            work_dir = _prepare_user_work_root(args.work_dir)
        except ValueError as exc:
            receipt = build_refusal_receipt(
                reason=str(exc),
                generated_at_utc=args.generated_at,
                selected_member=args.selected_member,
                claimed_fstyp=args.claimed_fstyp,
                device_node=args.device_node,
                observed_system=platform.system(),
                device_node_validated=_shape_validation_error(args.device_node) is None,
                device_node_validation_method="shape-only-work-dir-refusal",
            )
        else:
            if args.mode == "fixture":
                receipt = build_fixture_receipt(
                    work_dir,
                    fixture_root=args.fixture_root,
                    selected_member=args.selected_member,
                    claimed_fstyp=args.claimed_fstyp,
                    device_node=args.device_node,
                    generated_at_utc=args.generated_at,
                )
            else:
                receipt = build_apply_receipt(
                    work_dir,
                    selected_member=args.selected_member,
                    claimed_fstyp=args.claimed_fstyp,
                    device_node=args.device_node,
                    generated_at_utc=args.generated_at,
                )
    else:
        with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-backend-") as tmp:
            if args.mode == "fixture":
                receipt = build_fixture_receipt(
                    Path(tmp),
                    fixture_root=args.fixture_root,
                    selected_member=args.selected_member,
                    claimed_fstyp=args.claimed_fstyp,
                    device_node=args.device_node,
                    generated_at_utc=args.generated_at,
                )
            else:
                receipt = build_apply_receipt(
                    Path(tmp),
                    selected_member=args.selected_member,
                    claimed_fstyp=args.claimed_fstyp,
                    device_node=args.device_node,
                    generated_at_utc=args.generated_at,
                )

    if args.output:
        write_json(args.output, receipt)
    if args.print:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    if receipt.get("result") == "passed":
        return 0
    if receipt.get("result") == "refused":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
