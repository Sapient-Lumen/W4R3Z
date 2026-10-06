#!/usr/bin/env python3
"""Validate the FreeBSD backend plan for removable-media local fallback."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import removable_media_local_freebsd_backend_plan as plan_builder
from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.freebsd.backend.plan.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.freebsd.backend.plan.json"
INVALID_DIR = ROOT / "spec" / "examples" / "invalid" / "removable-media" / "freebsd-backend-plan"
DOC_TOKENS = {
    "README.md": ["2026-06-04r536", "FreeBSD backend plan", "ro,nosuid,noexec,nosymfollow,untrusted"],
    "docs/00-index.md": ["2026-06-04r536", "docs/current/removable-media-local-fallback-freebsd-backend-plan.md"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_fallback_freebsd_backend_plan.py", "untrusted"],
    "docs/current/removable-media-local-fallback-freebsd-backend-plan.md": [
        "removable.media.local.freebsd.backend.plan",
        "fstyp",
        "untrusted",
        "mount.exfat",
        "tools/removable_media_safe_capture.py",
    ],
}


def validate_schema(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA_REL)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.backend.plan", "wrong kind")
    require(errors, obj.get("plan_id") == plan_builder.PLAN_ID, "plan_id must bind r536")
    require(errors, obj.get("generated_for_version") == plan_builder.VERSION, "generated_for_version must bind r536")

    preflight = obj.get("preflight", {})
    mount = obj.get("mount_admission", {})
    sequence = obj.get("capture_sequence", {})
    worker = obj.get("post_detach_worker", {})
    host = obj.get("host_requirements", {})
    inputs = obj.get("inputs", {})

    require(errors, host.get("required_os") == "FreeBSD", "backend plan must target FreeBSD")
    require(errors, host.get("non_freebsd_apply_mode") == "refuse", "non-FreeBSD apply mode must refuse")
    require(errors, host.get("network_required") is False, "backend plan must not require network")
    require(errors, host.get("package_install_in_lane") is False, "backend plan must not install packages in lane")

    require(errors, preflight.get("fstyp_command", [None])[0] == "/usr/sbin/fstyp", "preflight must probe with /usr/sbin/fstyp")
    require(errors, preflight.get("fstyp_command", [None, None])[1] == inputs.get("device_node"), "fstyp must bind the selected device node")
    require(errors, set(preflight.get("allowed_fstyp_results", [])) == set(plan_builder.ALLOWED_FSTYP_RESULTS), "allowed fstyp set drifted")
    require(errors, "unknown" in preflight.get("denied_fstyp_results", []), "unknown filesystem must fail closed")
    require(errors, preflight.get("path_policy") == "shared-dirfd-openat-no-symlink-regular-file-before-capture", "backend must share the safe-capture path policy")

    desired = mount.get("contract_desired_inertness_flags", [])
    emitted = mount.get("freebsd_generic_mount_options_to_emit", [])
    not_generic = mount.get("not_claimed_as_freebsd_generic_mount_options", [])
    native_cmd = mount.get("native_mount_command_template", [])
    require(errors, "nodev" not in desired, "active desired inertness must not keep Linux-style nodev as a mount flag")
    require(errors, "untrusted" in desired, "active desired inertness must include FreeBSD untrusted")
    require(errors, "nodev" not in emitted, "FreeBSD generic mount options must not claim nodev")
    require(errors, not_generic == ["nodev"], "nodev must be explicitly marked not claimed as a FreeBSD generic mount option")
    require(errors, len(native_cmd) >= 5 and "nodev" not in str(native_cmd[4]).split(","), "native mount command must not emit nodev")
    require(errors, set(emitted) == {"ro", "nosuid", "noexec", "nosymfollow", "untrusted"}, "FreeBSD-emitted mount options should be ro,nosuid,noexec,nosymfollow,untrusted")

    adapter = mount.get("adapter", {})
    if inputs.get("claimed_fstyp") == "exfat":
        require(errors, adapter.get("strategy") == "external-fuse-helper-gated", "exfat must be external-helper gated")
        require(errors, adapter.get("package_install_or_network_fetch_in_lane") is False, "exfat helper cannot be installed/fetched in lane")
        require(errors, "blocked-until" in adapter.get("production_status", ""), "exfat production status must stay blocked until helper semantics are verified")
        require(errors, any("mount.exfat" in x for x in adapter.get("helper_command_candidates", [])), "exfat adapter must name mount.exfat helper candidates")

    phases = sequence.get("phase_order", [])
    require(errors, phases[-2:] == ["umount-before-worker", "launch-post-detach-worker"], "umount must precede worker launch")
    detach = sequence.get("detach", {})
    require(errors, detach.get("umount_must_complete_before_worker") is True, "detach must complete before worker")
    require(errors, detach.get("device_node_closed_before_worker") is True, "device node must be closed before worker")
    require(errors, detach.get("mountpoint_not_visible_to_worker") is True, "mountpoint must be invisible to worker")

    selected_open = sequence.get("selected_member_open", {})
    require(errors, selected_open.get("api_floor") == "dirfd-openat-root-pinned-walk-or-equivalent", "selected member open must be dirfd/openat root pinned")
    require(errors, set(selected_open.get("open_flags", [])) >= {"O_RDONLY", "O_NOFOLLOW"}, "selected member open must include O_RDONLY and O_NOFOLLOW")
    require(errors, selected_open.get("ancestor_symlink_policy") == "reject-every-component-before-open", "symlink ancestors must be rejected")
    require(errors, selected_open.get("leaf_kind") == "regular-file-only", "first backend lane must stay regular-file-only")
    require(errors, selected_open.get("shares_cloudtainer_capture_helper") == "tools/removable_media_safe_capture.py", "backend plan must point at safe-capture helper")

    for key in ["argv_includes_device_node", "argv_includes_mountpoint", "env_includes_device_node", "env_includes_mountpoint"]:
        require(errors, worker.get(key) is False, f"post-detach worker must not carry {key}")
    require(errors, worker.get("devfs_visible_devices") == [], "post-detach worker must see no devfs devices")
    require(errors, worker.get("network_default") == "deny-all", "post-detach worker network must be deny-all")
    require(errors, worker.get("launch_mode") == "preopened-fds-only", "worker launch mode must be fd-only")

    findings = {f.get("finding_id") for f in obj.get("audit_findings", []) if isinstance(f, dict)}
    require(errors, "nodev-was-overclaimed-as-a-generic-freebsd-mount-flag" in findings, "nodev audit finding must remain visible")
    require(errors, "exfat-is-adapter-gated-not-base-kernel-assumed" in findings, "exfat helper audit finding must remain visible")
    return errors


def check_builder_replay(observed: dict[str, Any]) -> list[str]:
    expected = plan_builder.build_plan()
    if expected != observed:
        return ["builder output differs from canonical FreeBSD backend plan example"]
    return []


def check_input_rejections() -> list[str]:
    errors: list[str] = []
    cases = [
        ({"selected_member": "../invoice.pdf"}, "selected member rejected"),
        ({"selected_member": "/invoice.pdf"}, "selected member rejected"),
        ({"claimed_fstyp": "ntfs"}, "not admitted"),
        ({"device_node": "/tmp/da0"}, "device node"),
        ({"session_root": "/tmp/session"}, "session root"),
    ]
    for kwargs, token in cases:
        try:
            plan_builder.build_plan(**kwargs)
        except Exception as exc:  # noqa: BLE001
            if token not in str(exc):
                errors.append(f"negative builder case {kwargs!r} produced unexpected error: {exc}")
        else:
            errors.append(f"negative builder case {kwargs!r} unexpectedly passed")
    return errors


def check_invalid_fixtures() -> list[str]:
    errors: list[str] = []
    if not INVALID_DIR.exists():
        return [f"missing invalid fixture directory {INVALID_DIR.relative_to(ROOT)}"]
    paths = sorted(INVALID_DIR.glob("*.json"))
    if len(paths) < 3:
        errors.append("expected at least three FreeBSD backend negative fixtures")
    for path in paths:
        obj = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = validate_schema(obj)
        semantic = semantic_errors(obj)
        if not schema_errors and not semantic:
            errors.append(f"{path.relative_to(ROOT)} unexpectedly passed schema and semantic checks")
    return errors


def check_doc_tokens() -> list[str]:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel} missing token {token!r}")
    return errors


def main() -> int:
    observed = load_json(ROOT, EXAMPLE_REL)
    errors = validate_schema(observed) + semantic_errors(observed) + check_builder_replay(observed)
    errors.extend(check_input_rejections())
    errors.extend(check_invalid_fixtures())
    errors.extend(check_doc_tokens())
    if errors:
        print("removable-media FreeBSD backend plan check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("removable-media FreeBSD backend plan check OK")
    print("Backend plan: fstyp -> FreeBSD-realized read-only mount flags -> safe capture -> umount -> fd-only worker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
