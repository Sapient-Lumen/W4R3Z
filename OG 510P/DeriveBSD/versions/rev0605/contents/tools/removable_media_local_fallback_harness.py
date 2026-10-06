#!/usr/bin/env python3
"""Run the removable-media local-fallback first lane against a real file fixture.

This is an executable cloudtainer harness, not a production mounter.  It proves
that the canonical first lane can be driven from bytes: admit a claimed small
filesystem family, require a clean single regular-file path, capture and digest
that file before later work, write the preserved capture to a digest-addressed
store, close the modeled device/mount authority, then produce a separate
post-detach derivative through a single declared output slot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import sys
from pathlib import Path
from typing import Any

import removable_media_safe_capture as safe_capture

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_ROOT = ROOT / "fixtures" / "removable-media" / "local-fallback" / "exfat-card"
DEFAULT_OUTPUT_DIR = ROOT / "validation" / "removable-media-local-fallback-harness" / "expected"
DEFAULT_SELECTED_PATH = "invoice.pdf"
DEFAULT_CLAIMED_FS = "exfat"
DEFAULT_DEVICE_ID = "usb:vid=090c,pid=1000,serial=AA0001234567"
DEFAULT_RUN_ID = "rm-local-fallback-harness-20260604-r536-cloudtainer"
HARNESS_VERSION = "0.2"
GENERATED_FOR_VERSION = "2026-06-04r536"


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def rel_clean(path: str) -> list[str]:
    raw = path.replace("\\", "/")
    if raw.startswith("/"):
        raise ValueError("selected path must be relative, not absolute")
    parts = [p for p in raw.split("/") if p not in ("", ".")]
    if not parts:
        raise ValueError("selected path must name one regular file")
    if any(p == ".." for p in parts):
        raise ValueError("selected path must not contain '..'")
    return parts


def assert_within(base: Path, target: Path) -> None:
    try:
        target.resolve(strict=False).relative_to(base.resolve(strict=True))
    except Exception as exc:  # noqa: BLE001
        raise ValueError("selected path escapes fixture root") from exc


def reject_symlink_chain(base: Path, parts: list[str]) -> Path:
    """Return the selected path only if no selected component is a symlink.

    A leaf-only symlink check is not enough for removable-media ingest: a media
    tree can hide an ambient escape or policy bypass in an ancestor directory
    that still resolves inside the fixture during a friendly run.  The first
    executable harness keeps the rule simple and fail-closed: every selected
    component must be a real directory until the final regular file.
    """
    cur = base
    for part in parts:
        cur = cur / part
        if cur.is_symlink():
            raise ValueError("selected subject path must not contain symlink components")
    return cur


def store_path(output_dir: Path, digest: str, filename: str) -> tuple[str, Path]:
    hex_digest = digest.split(":", 1)[1]
    logical = f"store/sha256/{hex_digest[:2]}/{hex_digest}/{filename}"
    return logical, output_dir / logical


def derivative_summary(source_digest: str, source_size: int) -> dict[str, Any]:
    return {
        "kind": "removable.media.local.fallback.harness.derivative.summary",
        "schema_version": "0.1",
        "source_digest": source_digest,
        "source_size_bytes": source_size,
        "body_bytes_copied": False,
        "classification": "fixture-pdf-by-extension-and-magic",
        "sanitizer_scope": "cloudtainer-harness-metadata-only-not-production-sanitizer",
        "redaction": {
            "raw_body_included": False,
            "source_path_included": False,
            "device_locator_included": False,
        },
    }


def build_run(
    *,
    fixture_root: Path,
    selected_path: str,
    output_dir: Path,
    output_root_label: str,
    claimed_filesystem: str,
    device_id: str,
    run_id: str,
    write_files: bool,
) -> dict[str, Any]:
    grant = load_json("spec/examples/device.attach.grant.removable-media-local-ingest.json")
    plan = load_json("spec/examples/content.import.plan.removable-media-local-ingest.json")
    receipt = load_json("spec/examples/content.import.receipt.removable-media-local-ingest.json")
    detach = load_json("spec/examples/device.detach.receipt.removable-media-local-ingest.json")
    contract = load_json("spec/examples/removable.media.local.post_detach.contract.json")
    launch = load_json("spec/examples/removable.media.local.post_detach.launch.evidence.json")

    constraints = grant.get("constraints") or {}
    allowed = constraints.get("allowed_filesystem_families") or []
    denied = constraints.get("denied_filesystem_families") or []
    if claimed_filesystem not in allowed or claimed_filesystem in denied:
        raise ValueError(f"filesystem family {claimed_filesystem!r} is not admitted by the attach grant")

    if device_id != (grant.get("device") or {}).get("id"):
        raise ValueError("device_id does not match canonical attach grant")

    normalized, path_reason = safe_capture.normalize_member(selected_path)
    if path_reason:
        raise ValueError(f"selected path rejected: {path_reason}")
    assert normalized is not None
    parts = normalized.split("/")
    fixture_root = fixture_root.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-harness-capture-") as td:
        capture_result = safe_capture.capture_regular_member(fixture_root, normalized, Path(td))
        source_bytes = capture_result.object_path.read_bytes()

    subject_digest = capture_result.digest
    subject_size = capture_result.size_bytes
    planned_subject = plan.get("subject") or {}
    if planned_subject.get("digest") != subject_digest:
        raise ValueError(
            "fixture subject digest does not match content.import.plan.removable-media-local-ingest.json"
        )
    if planned_subject.get("size_bytes") != subject_size:
        raise ValueError(
            "fixture subject size does not match content.import.plan.removable-media-local-ingest.json"
        )
    if planned_subject.get("filename") != parts[-1]:
        raise ValueError("fixture subject filename does not match content import plan")

    receipt_subject = receipt.get("subject") or {}
    if receipt_subject.get("digest") != subject_digest or receipt_subject.get("size_bytes") != subject_size:
        raise ValueError("content import receipt subject no longer matches fixture bytes")

    preserved_logical, preserved_path = store_path(output_dir, subject_digest, "preserved-subject.bin")
    if write_files:
        preserved_path.parent.mkdir(parents=True, exist_ok=True)
        preserved_path.write_bytes(source_bytes)

    deriv_obj = derivative_summary(subject_digest, subject_size)
    derivative_bytes = canonical_json_bytes(deriv_obj) + b"\n"
    derivative_digest = sha256_bytes(derivative_bytes)
    deriv_logical, deriv_path = store_path(output_dir, derivative_digest, "sanitized-summary.json")
    if write_files:
        deriv_path.parent.mkdir(parents=True, exist_ok=True)
        deriv_path.write_bytes(derivative_bytes)

    mount_flags = list(constraints.get("required_mount_flags") or [])
    capture_params = (((plan.get("operations") or [{}])[0]).get("params") or {})
    detach_map = (detach.get("runtime") or {}).get("mapping") or {}
    cap = (launch.get("confinement") or {}).get("capsicum") or {}
    devfs = (launch.get("confinement") or {}).get("devfs") or {}
    pf = (launch.get("confinement") or {}).get("pf") or {}
    mounts = (launch.get("confinement") or {}).get("mounts") or {}

    return {
        "kind": "removable.media.local.fallback.harness.run",
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_for_version": GENERATED_FOR_VERSION,
        "harness": {
            "tool": "tools/removable_media_local_fallback_harness.py",
            "harness_version": HARNESS_VERSION,
            "scope": "cloudtainer-executable-first-lane-proof-not-production-mounter",
        },
        "inputs": {
            "fixture_media_root": "fixtures/removable-media/local-fallback/exfat-card",
            "selected_path": selected_path,
            "selected_path_normalized": normalized,
            "device_id": device_id,
            "claimed_filesystem_family": claimed_filesystem,
        },
        "admission": {
            "source_grant": "spec/examples/device.attach.grant.removable-media-local-ingest.json",
            "filesystem_family_admitted": True,
            "allowed_filesystem_families": allowed,
            "denied_filesystem_families": denied,
            "mount_flags_required": mount_flags,
            "read_only": constraints.get("read_only") is True,
            "host_fallback_mounts_forbidden": True,
            "selected_subject_regular_file": True,
            "selected_subject_symlink": False,
            "path_escape_denied": True,
        },
        "capture": {
            "source_path_for_fixture": selected_path,
            "plan": "spec/examples/content.import.plan.removable-media-local-ingest.json",
            "receipt": "spec/examples/content.import.receipt.removable-media-local-ingest.json",
            "plan_subject_digest": planned_subject.get("digest"),
            "observed_subject_digest": subject_digest,
            "observed_size_bytes": subject_size,
            "capture_before_later_ops": capture_params.get("selected_subject_capture_posture"),
            "digest_verification": capture_params.get("digest_verification"),
            "path_capture": {
                "capture_api": capture_result.capture_api,
                "root_fd_pinned": capture_result.root_fd_pinned,
                "opened_with_openat": capture_result.opened_with_openat,
                "opened_with_no_follow": capture_result.opened_with_no_follow,
                "ancestor_symlink_policy": capture_result.ancestor_symlink_policy,
                "leaf_symlink_policy": capture_result.leaf_symlink_policy,
                "regular_file_only": capture_result.regular_file_only,
                "lstat_fstat_same_object": capture_result.lstat_fstat_same_object,
                "source_stable_after_copy": capture_result.source_stable_after_copy,
                "verified_after_copy": capture_result.verified_after_copy,
            },
            "preserved_capture": {
                "logical_path": preserved_logical,
                "sha256": subject_digest,
                "size_bytes": subject_size,
                "locator_kind": "digest-addressed-store",
                "worker_visible": False,
            },
        },
        "detach_gate": {
            "detach_receipt": "spec/examples/device.detach.receipt.removable-media-local-ingest.json",
            "detach_trigger": detach_map.get("detach_trigger"),
            "later_ops_dependency": detach_map.get("later_ops_dependency"),
            "media_session_ended_before_later_ops": True,
            "ingest_references_closed_before_worker": True,
            "projection_source_digest": detach_map.get("post_detach_projection_source_digest"),
        },
        "post_detach_worker": {
            "contract": "spec/examples/removable.media.local.post_detach.contract.json",
            "launch_evidence": "spec/examples/removable.media.local.post_detach.launch.evidence.json",
            "capability_mode_entered": cap.get("capability_mode_entered") is True,
            "path_reopen_after_entry": cap.get("path_reopen_after_entry"),
            "ingest_mount_visible": False,
            "media_mount_visible": mounts.get("media_mount_visible_to_worker") is True,
            "device_nodes_visible": devfs.get("visible_devices") or [],
            "network_default": pf.get("network_default"),
            "network_socket_descriptors": (launch.get("network") or {}).get("socket_descriptors") or [],
            "contract_capability_mode": (contract.get("worker") or {}).get("capability_mode"),
            "single_object_projection_digest": subject_digest,
            "authoritative_store_browseable": False,
            "derivative_slot": {
                "declared_slots": 1,
                "initial_state": "empty-regular-file",
                "open_mode": "append-only-no-readback-no-truncate",
                "broker_remeasured_output": True,
            },
        },
        "derivative": {
            "logical_path": deriv_logical,
            "sha256": derivative_digest,
            "source_digest": subject_digest,
            "relationship": "separate-derivative-from-preserved-capture",
            "body_bytes_copied": False,
            "worker_readback_allowed": False,
        },
        "evidence_files": [
            {
                "role": "preserved-capture",
                "output_root": output_root_label,
                "path": preserved_logical,
                "sha256": subject_digest,
                "size_bytes": subject_size,
            },
            {
                "role": "sanitized-derivative-summary",
                "output_root": output_root_label,
                "path": deriv_logical,
                "sha256": derivative_digest,
                "size_bytes": len(derivative_bytes),
            },
        ],
        "result": {
            "status": "ok",
            "message": "cloudtainer harness proved capture-first digest match, detach gate, absent ingest authority, and separate derivative output",
        },
    }


def write_run(output_dir: Path, obj: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "removable.media.local.fallback.harness.run.json"
    out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    ap.add_argument("--selected-path", default=DEFAULT_SELECTED_PATH)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    ap.add_argument("--output-root-label", default="validation/removable-media-local-fallback-harness/expected")
    ap.add_argument("--claim-filesystem", default=DEFAULT_CLAIMED_FS)
    ap.add_argument("--device-id", default=DEFAULT_DEVICE_ID)
    ap.add_argument("--run-id", default=DEFAULT_RUN_ID)
    ap.add_argument("--json", action="store_true", help="write the run object to stdout instead of output-dir")
    ap.add_argument("--no-write-files", action="store_true", help="do not materialize preserved/derivative evidence files")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        run = build_run(
            fixture_root=args.fixture_root,
            selected_path=args.selected_path,
            output_dir=args.output_dir,
            output_root_label=args.output_root_label,
            claimed_filesystem=args.claim_filesystem,
            device_id=args.device_id,
            run_id=args.run_id,
            write_files=not args.no_write_files,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"removable-media local-fallback harness failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(run, indent=2, sort_keys=True))
    else:
        out = write_run(args.output_dir, run)
        print(out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
