#!/usr/bin/env python3
"""Build the FreeBSD backend plan for removable-media local fallback.

This bridges the cloudtainer safe-capture proof to a FreeBSD host backend
without pretending this Linux-ish container mounted a FreeBSD block provider.
The plan is deliberately a dry-run contract: probe with fstyp, mount read-only
with FreeBSD-realized generic flags only, capture one regular file through the
same dirfd/openat no-symlink helper used by the executable harness, unmount, and
then launch the post-detach worker with only preopened descriptors.

Audit correction: `nodev` is no longer part of the active FreeBSD mount
option set. It is recorded only as a not-claimed Linux-shaped assumption, while
`untrusted` is emitted for externally provided media.  Device-node exposure is
handled through post-detach devfs/jail/descriptor controls and by never handing
the mounted tree to the worker.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from removable_media_safe_capture import normalize_member

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-06-04r536"
PLAN_ID = "rm-local-freebsd-backend-plan-20260604-r536"
SCHEMA_REL = "spec/removable.media.local.freebsd.backend.plan.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.freebsd.backend.plan.json"

ALLOWED_FSTYP_RESULTS = ["cd9660", "exfat", "msdosfs", "ufs"]
DENIED_FSTYP_RESULTS = ["geli", "ntfs", "unknown", "zfs"]
CONTRACT_DESIRED_INERTNESS_FLAGS = ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"]
FREEBSD_GENERIC_MOUNT_OPTIONS = ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"]
NOT_GENERIC_FREEBSD_MOUNT_OPTIONS = ["nodev"]
DEFAULT_DEVICE_NODE = "/dev/da0p1"
DEFAULT_SELECTED_MEMBER = "invoice.pdf"
DEFAULT_SESSION_ROOT = "/var/run/derivebsd/removable-media/local-fallback/20260604-r536-demo"
CLOUDTAINER_OS_OBSERVED = "Linux"

_DEVICE_COMPONENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def validate_device_node(device_node: str) -> None:
    if not isinstance(device_node, str):
        raise ValueError("device node must be a string")
    p = PurePosixPath(device_node)
    parts = p.parts
    if not p.is_absolute() or len(parts) < 3 or parts[1] != "dev":
        raise ValueError("device node must be an absolute path naming an entry under /dev")
    # Do not rely on path normalization to make a hostile path safe.  A real
    # apply runner must bind the exact device path it will pass to fstyp/mount;
    # `/dev/./da0`, `/dev/foo/../bar`, and `/dev//da0` are therefore rejected
    # rather than cleaned.
    raw_after_dev = device_node[len("/dev/") :]
    raw_components = raw_after_dev.split("/")
    if any(component in {"", ".", ".."} for component in raw_components):
        raise ValueError("device node path must be absolute-clean without empty/dot/traversal components")
    for component in raw_components:
        if not _DEVICE_COMPONENT_RE.fullmatch(component):
            raise ValueError("device node path contains characters outside the device-safe component set")


def validate_session_root(session_root: str) -> None:
    prefix = "/var/run/derivebsd/removable-media/local-fallback/"
    if not isinstance(session_root, str) or not session_root.startswith(prefix):
        raise ValueError("session root must live under /var/run/derivebsd/removable-media/local-fallback")
    parts = session_root.split("/")[1:]
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("session root must be absolute-clean without empty/dot components")


def normalize_selected_member(member: str) -> str:
    normalized, reason = normalize_member(member)
    if reason:
        raise ValueError(f"selected member rejected: {reason}")
    assert normalized is not None
    return normalized


def mount_adapter_for(fstyp: str) -> dict[str, Any]:
    if fstyp == "exfat":
        return {
            "family": "exfat",
            "strategy": "external-fuse-helper-gated",
            "helper_command_candidates": ["/usr/local/sbin/mount.exfat", "/usr/local/bin/mount.exfat"],
            "helper_must_be_preinstalled": True,
            "helper_digest_pinned_before_use": True,
            "package_install_or_network_fetch_in_lane": False,
            "kernel_module_load_in_lane": "forbidden-until-a-separate-reviewed-boot-profile-enables-fusefs",
            "production_status": "blocked-until-helper-fuse-and-post-mount-flag-semantics-are-verified",
        }
    return {
        "family": fstyp,
        "strategy": "base-system-mount-helper",
        "helper_command_candidates": ["/sbin/mount"],
        "helper_must_be_preinstalled": True,
        "helper_digest_pinned_before_use": True,
        "package_install_or_network_fetch_in_lane": False,
        "kernel_module_load_in_lane": "not-required-by-plan",
        "production_status": "candidate-for-rooted-host-integration-test",
    }


def build_plan(
    *,
    device_node: str = DEFAULT_DEVICE_NODE,
    selected_member: str = DEFAULT_SELECTED_MEMBER,
    claimed_fstyp: str = "exfat",
    session_root: str = DEFAULT_SESSION_ROOT,
) -> dict[str, Any]:
    validate_device_node(device_node)
    validate_session_root(session_root)
    if claimed_fstyp not in ALLOWED_FSTYP_RESULTS:
        raise ValueError(f"filesystem family {claimed_fstyp!r} is not admitted by the local fallback grant")
    normalized_member = normalize_selected_member(selected_member)

    mountpoint = f"{session_root}/mnt"
    work_root = f"{session_root}/work"
    cas_root = f"{session_root}/quarantine-cas"
    derivative_root = f"{session_root}/derivative"
    native_mount_options = ",".join(FREEBSD_GENERIC_MOUNT_OPTIONS)

    return {
        "kind": "removable.media.local.freebsd.backend.plan",
        "schema_version": "0.1",
        "plan_id": PLAN_ID,
        "generated_for_version": VERSION,
        "execution_mode": "dry-run-host-plan-cloudtainer-validated",
        "host_requirements": {
            "required_os": "FreeBSD",
            "cloudtainer_os_observed": CLOUDTAINER_OS_OBSERVED,
            "non_freebsd_apply_mode": "refuse",
            "requires_root_for_real_mount": True,
            "network_required": False,
            "package_install_in_lane": False,
        },
        "inputs": {
            "device_node": device_node,
            "selected_member": selected_member,
            "selected_member_normalized": normalized_member,
            "claimed_fstyp": claimed_fstyp,
            "session_root": session_root,
            "mountpoint": mountpoint,
            "work_root": work_root,
            "cas_root": cas_root,
            "derivative_root": derivative_root,
        },
        "preflight": {
            "device_node_policy": "must-be-existing-device-node-under-dev-not-directory-not-symlink",
            "path_policy": "shared-dirfd-openat-no-symlink-regular-file-before-capture",
            "fstyp_command": ["/usr/sbin/fstyp", device_node],
            "allowed_fstyp_results": ALLOWED_FSTYP_RESULTS,
            "denied_fstyp_results": DENIED_FSTYP_RESULTS,
            "fstyp_result_binding": "observed-result-must-equal-claimed-family-before-mount",
            "mountpoint_policy": "launcher-created-empty-private-0700-directory",
        },
        "mount_admission": {
            "contract_desired_inertness_flags": CONTRACT_DESIRED_INERTNESS_FLAGS,
            "freebsd_generic_mount_options_to_emit": FREEBSD_GENERIC_MOUNT_OPTIONS,
            "not_claimed_as_freebsd_generic_mount_options": NOT_GENERIC_FREEBSD_MOUNT_OPTIONS,
            "nodev_reality_check": "do-not-emit-nodev-as-generic-freebsd-mount8-option; use ro,nosuid,noexec,nosymfollow,untrusted and enforce device-node absence through post-detach devfs/jail/descriptor controls",
            "native_mount_command_template": [
                "/sbin/mount",
                "-t",
                "${observed_fstyp}",
                "-o",
                native_mount_options,
                device_node,
                mountpoint,
            ],
            "exfat_adapter_command_template": [
                "${digest_pinned_mount_exfat_helper}",
                "-o",
                "ro",
                device_node,
                mountpoint,
            ],
            "adapter": mount_adapter_for(claimed_fstyp),
            "post_mount_verification": {
                "command_template": ["/sbin/mount", "-p"],
                "must_observe_read_only": True,
                "must_observe_noexec_nosuid_nosymfollow_where_supported": True,
                "missing_required_semantic": "fail-closed-before-capture",
            },
        },
        "capture_sequence": {
            "phase_order": [
                "probe-fstyp",
                "mount-readonly-private",
                "open-selected-member-no-follow",
                "lstat-fstat-same-object-check",
                "copy-to-work-and-hash",
                "commit-preserved-capture-to-cas",
                "umount-before-worker",
                "launch-post-detach-worker",
            ],
            "selected_member_open": {
                "api_floor": "dirfd-openat-root-pinned-walk-or-equivalent",
                "open_flags": ["O_RDONLY", "O_NOFOLLOW"],
                "ancestor_symlink_policy": "reject-every-component-before-open",
                "leaf_kind": "regular-file-only",
                "lstat_fstat_same_object_required": True,
                "shares_cloudtainer_capture_helper": "tools/removable_media_safe_capture.py",
            },
            "preserved_capture": {
                "locator_template": "quarantine-cas/sha256/<hex>",
                "digest_algorithm": "sha256",
                "verify_after_copy": True,
                "authoritative_before_detach": True,
            },
            "detach": {
                "umount_command_template": ["/sbin/umount", mountpoint],
                "umount_must_complete_before_worker": True,
                "device_node_closed_before_worker": True,
                "mountpoint_not_visible_to_worker": True,
            },
        },
        "post_detach_worker": {
            "launch_mode": "preopened-fds-only",
            "input_delivery": "read-only-fd-to-preserved-capture-or-single-object-projection",
            "output_delivery": "append-only-fd-to-one-empty-derivative-slot",
            "argv_includes_device_node": False,
            "argv_includes_mountpoint": False,
            "env_includes_device_node": False,
            "env_includes_mountpoint": False,
            "cwd": "launcher-owned-empty-scratch-not-mount-not-cas",
            "devfs_visible_devices": [],
            "network_default": "deny-all",
            "capability_floor": "cap_enter-before-tool-mainline-when-running-on-FreeBSD",
        },
        "audit_findings": [
            {
                "finding_id": "nodev-was-overclaimed-as-a-generic-freebsd-mount-flag",
                "severity": "high",
                "correction": "Do not emit nodev through generic FreeBSD mount -o; enforce no device exposure after detach through devfs/jail/descriptor controls and worker invisibility to mount/device paths.",
            },
            {
                "finding_id": "exfat-is-adapter-gated-not-base-kernel-assumed",
                "severity": "medium",
                "correction": "Treat exFAT as a digest-pinned, preinstalled helper lane until mount.exfat/FUSE and post-mount flag semantics are verified on a FreeBSD host.",
            },
        ],
        "result": {
            "status": "planned",
            "apply_mode_status": "not-run-in-cloudtainer",
            "next_host_test": "Run this sequence on FreeBSD with msdosfs and cd9660 media first, then separately qualify exFAT helper semantics.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-node", default=DEFAULT_DEVICE_NODE)
    parser.add_argument("--selected-member", default=DEFAULT_SELECTED_MEMBER)
    parser.add_argument("--claim-fstyp", default="exfat", choices=ALLOWED_FSTYP_RESULTS)
    parser.add_argument("--session-root", default=DEFAULT_SESSION_ROOT)
    parser.add_argument("--write", action="store_true", help=f"write {EXAMPLE_REL}")
    args = parser.parse_args(argv)

    try:
        plan = build_plan(
            device_node=args.device_node,
            selected_member=args.selected_member,
            claimed_fstyp=args.claim_fstyp,
            session_root=args.session_root,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"FreeBSD backend plan rejected input: {exc}", file=sys.stderr)
        return 1

    if args.write:
        out = ROOT / EXAMPLE_REL
        out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE_REL}")
    else:
        print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
