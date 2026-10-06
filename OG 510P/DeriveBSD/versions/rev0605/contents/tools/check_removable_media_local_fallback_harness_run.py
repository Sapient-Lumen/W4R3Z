#!/usr/bin/env python3
"""Validate and replay the removable-media local-fallback cloudtainer harness.

This guard is intentionally executable: it runs the tiny first-lane harness
against fixture bytes, compares the generated run record to the canonical
example, and verifies negative cases for filesystem admission and path escape.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import removable_media_local_fallback_harness as harness
from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.fallback.harness.run.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.fallback.harness.run.json"
INVALID_REL = "spec/examples/invalid/removable-media/local-fallback-harness/ambient-ingest-visible.json"
EXPECTED_OUTPUT_ROOT = ROOT / "validation" / "removable-media-local-fallback-harness" / "expected"

DOC_TOKENS = {
    "CHANGELOG.md": [
        "2026-06-04r536",
        "removable.media.local.fallback.harness.run",
        "tools/removable_media_local_fallback_harness.py",
        "tools/check_removable_media_local_fallback_harness_run.py",
    ],
    "README.md": ["2026-06-04r536", "removable-media local-fallback harness", "tools/removable_media_local_fallback_harness.py"],
    "docs/00-index.md": ["2026-06-04r536", "docs/current/removable-media-local-fallback-harness.md"],
    "docs/current/removable-media-local-fallback-harness.md": [
        "removable.media.local.fallback.harness.run",
        "capture-first",
        "post-detach worker",
        "validation/removable-media-local-fallback-harness/expected",
    ],
}


def validate_schema(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA_REL)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    plan = load_json(ROOT, "spec/examples/content.import.plan.removable-media-local-ingest.json")
    receipt = load_json(ROOT, "spec/examples/content.import.receipt.removable-media-local-ingest.json")
    detach = load_json(ROOT, "spec/examples/device.detach.receipt.removable-media-local-ingest.json")

    observed = obj.get("capture", {}).get("observed_subject_digest")
    plan_digest = plan.get("subject", {}).get("digest")
    if observed != plan_digest:
        errors.append("harness observed digest must equal content import plan subject digest")
    if obj.get("capture", {}).get("plan_subject_digest") != observed:
        errors.append("harness plan_subject_digest must equal observed digest")
    if obj.get("capture", {}).get("observed_size_bytes") != plan.get("subject", {}).get("size_bytes"):
        errors.append("harness observed size must equal content import plan subject size")
    path_capture = obj.get("capture", {}).get("path_capture", {})
    if path_capture.get("capture_api") != "dirfd-openat-no-symlink-components":
        errors.append("harness capture must use dirfd/openat no-symlink path walk")
    for key in ["root_fd_pinned", "opened_with_openat", "opened_with_no_follow", "regular_file_only", "lstat_fstat_same_object", "source_stable_after_copy", "verified_after_copy"]:
        if path_capture.get(key) is not True:
            errors.append(f"harness capture path_capture.{key} must be true")
    if path_capture.get("ancestor_symlink_policy") != "deny-each-ancestor-by-openat-o_directory-o_nofollow":
        errors.append("harness capture must deny symlink ancestors")
    if path_capture.get("leaf_symlink_policy") != "deny-leaf-by-openat-o_nofollow":
        errors.append("harness capture must deny symlink leaves")
    if receipt.get("subject", {}).get("digest") != observed:
        errors.append("content import receipt subject digest must equal harness observed digest")
    if obj.get("detach_gate", {}).get("projection_source_digest") != observed:
        errors.append("detach projection source digest must equal harness observed digest")
    if (detach.get("runtime", {}).get("mapping") or {}).get("post_detach_projection_source_digest") != observed:
        errors.append("device detach receipt projection source digest must equal harness observed digest")
    if obj.get("post_detach_worker", {}).get("single_object_projection_digest") != observed:
        errors.append("post-detach worker projection digest must equal harness observed digest")
    if obj.get("post_detach_worker", {}).get("ingest_mount_visible") is not False:
        errors.append("post-detach worker must not see ingest mount")
    if obj.get("post_detach_worker", {}).get("media_mount_visible") is not False:
        errors.append("post-detach worker must not see media mount")
    if obj.get("post_detach_worker", {}).get("device_nodes_visible") != []:
        errors.append("post-detach worker must not see device nodes")
    if obj.get("post_detach_worker", {}).get("network_socket_descriptors") != []:
        errors.append("post-detach worker must not inherit socket descriptors")
    if obj.get("derivative", {}).get("source_digest") != observed:
        errors.append("derivative source digest must equal preserved capture digest")
    if obj.get("derivative", {}).get("sha256") == observed:
        errors.append("derivative digest must be separate from preserved capture digest")
    if obj.get("derivative", {}).get("body_bytes_copied") is not False:
        errors.append("metadata-only harness derivative must not copy body bytes")
    return errors


def check_evidence_files(obj: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    by_role = {row.get("role"): row for row in obj.get("evidence_files", []) if isinstance(row, dict)}
    if set(by_role) != {"preserved-capture", "sanitized-derivative-summary"}:
        errors.append("evidence_files must have preserved-capture and sanitized-derivative-summary roles")
        return errors
    for row in by_role.values():
        rel = row.get("path")
        if not isinstance(rel, str):
            errors.append(f"{row.get('role')}: evidence path missing")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"{row.get('role')}: missing evidence file {path}")
            continue
        digest = harness.sha256_file(path)
        if digest != row.get("sha256"):
            errors.append(f"{row.get('role')}: digest {digest} != {row.get('sha256')}")
        if path.stat().st_size != row.get("size_bytes"):
            errors.append(f"{row.get('role')}: size {path.stat().st_size} != {row.get('size_bytes')}")
    return errors


def expect_build_failure(description: str, expected_token: str, **overrides: Any) -> str | None:
    """Exercise fail-closed cases without spawning a fresh interpreter per case."""
    params: dict[str, Any] = {
        "fixture_root": harness.DEFAULT_FIXTURE_ROOT,
        "selected_path": harness.DEFAULT_SELECTED_PATH,
        "output_dir": EXPECTED_OUTPUT_ROOT,
        "output_root_label": "validation/removable-media-local-fallback-harness/expected",
        "claimed_filesystem": harness.DEFAULT_CLAIMED_FS,
        "device_id": harness.DEFAULT_DEVICE_ID,
        "run_id": harness.DEFAULT_RUN_ID,
        "write_files": False,
    }
    params.update(overrides)
    try:
        harness.build_run(**params)
    except Exception as exc:  # noqa: BLE001
        if expected_token not in str(exc):
            return f"negative harness case {description!r} missing {expected_token!r}: {exc}"
        return None
    return f"negative harness case {description!r} unexpectedly passed"


def require_doc_tokens(errors: list[str]) -> None:
    for rel, tokens in DOC_TOKENS.items():
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel}: missing token {token!r}")


def main() -> int:
    errors: list[str] = []
    observed = load_json(ROOT, EXAMPLE_REL)

    schema_errors = validate_schema(observed)
    if schema_errors:
        errors.extend(f"schema: {msg}" for msg in schema_errors[:20])
    errors.extend(semantic_errors(observed))
    errors.extend(check_evidence_files(observed, EXPECTED_OUTPUT_ROOT))

    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-harness-") as td:
        out = Path(td)
        generated = harness.build_run(
            fixture_root=harness.DEFAULT_FIXTURE_ROOT,
            selected_path=harness.DEFAULT_SELECTED_PATH,
            output_dir=out,
            output_root_label="validation/removable-media-local-fallback-harness/expected",
            claimed_filesystem=harness.DEFAULT_CLAIMED_FS,
            device_id=harness.DEFAULT_DEVICE_ID,
            run_id=harness.DEFAULT_RUN_ID,
            write_files=True,
        )
        if generated != observed:
            errors.append("harness replay output differs from canonical spec example")
        errors.extend(check_evidence_files(generated, out))

    invalid = load_json(ROOT, INVALID_REL)
    invalid_schema_errors = validate_schema(invalid)
    invalid_semantic_errors = semantic_errors(invalid)
    if not invalid_schema_errors and not invalid_semantic_errors:
        errors.append(f"{INVALID_REL}: expected invalid fixture to fail schema or semantic checks")

    fs_error = expect_build_failure("unknown filesystem family", "filesystem family", claimed_filesystem="unknown")
    if fs_error:
        errors.append(fs_error)
    path_error = expect_build_failure("path traversal", "non-relative-clean-member-path", selected_path="../invoice.pdf")
    if path_error:
        errors.append(path_error)

    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-harness-negative-") as td:
        neg_root = Path(td) / "media"
        neg_root.mkdir()
        (neg_root / "invoice.pdf").mkdir()
        dir_error = expect_build_failure("directory subject", "directory-subject-denied-in-first-cut", fixture_root=neg_root)
        if dir_error:
            errors.append(dir_error)

    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-harness-symlink-") as td:
        neg_root = Path(td) / "media"
        real_dir = neg_root / "real"
        real_dir.mkdir(parents=True)
        (real_dir / "invoice.pdf").write_bytes((ROOT / "fixtures" / "removable-media" / "local-fallback" / "exfat-card" / "invoice.pdf").read_bytes())
        if hasattr(os, "symlink"):
            os.symlink(real_dir, neg_root / "linkdir")
            symlink_error = expect_build_failure(
                "symlink ancestor",
                "symlink-ancestor-denied",
                fixture_root=neg_root,
                selected_path="linkdir/invoice.pdf",
            )
            if symlink_error:
                errors.append(symlink_error)

    require_doc_tokens(errors)

    if errors:
        print("removable-media local-fallback harness run check FAILED.")
        for err in errors:
            print(f"- {err}")
        return 1

    print("removable-media local-fallback harness run check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
