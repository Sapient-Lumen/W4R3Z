#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach runtime dependency closure.

A digest-pinned executable is not enough if dynamic loader/library/interpreter
resolution can still come from ambient host or removable-media state. The first
host-local removable-media fallback must keep runtime dependency closure identity
launcher-pinned, digest-recorded, and loader-path-free.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_POSTURE = 'launcher-pinned-runtime-dependency-closure-no-ambient-loader-search'
RECEIPT_POSTURE = 'receipt-records-runtime-dependency-closure-digest'
LOADER_POSTURE = 'no-ld-library-path-cwd-or-media-derived-loader-inputs'
CLOSURE_DIGEST = 'sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        ("execution", "post_detach_runtime_dependency_posture", RUNTIME_POSTURE),
        ("execution", "post_detach_runtime_dependency_closure_digest", CLOSURE_DIGEST),
        ("execution", "post_detach_dynamic_loader_posture", LOADER_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        ("execution", "post_detach_runtime_dependency_posture", RUNTIME_POSTURE),
        ("execution", "post_detach_runtime_dependency_closure_digest", CLOSURE_DIGEST),
        ("execution", "post_detach_dynamic_loader_posture", LOADER_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        ("constraints", "post_detach_runtime_dependency_posture", RUNTIME_POSTURE),
        ("constraints", "post_detach_runtime_dependency_receipt_posture", RECEIPT_POSTURE),
        ("constraints", "post_detach_dynamic_loader_posture", LOADER_POSTURE),
        ("constraints", "post_detach_runtime_dependency_closure_digest_required", True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        ("runtime", "mapping", "post_detach_runtime_dependency_posture", RUNTIME_POSTURE),
        ("runtime", "mapping", "post_detach_runtime_dependency_receipt_posture", RECEIPT_POSTURE),
        ("runtime", "mapping", "post_detach_runtime_dependency_closure_digest", CLOSURE_DIGEST),
        ("runtime", "mapping", "post_detach_dynamic_loader_posture", LOADER_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        ("runtime_dependency_posture", RUNTIME_POSTURE),
        ("runtime_dependency_closure_digest", CLOSURE_DIGEST),
        ("dynamic_loader_posture", LOADER_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_runtime_dependency_posture",
        "post_detach_runtime_dependency_closure_digest",
        "post_detach_dynamic_loader_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_runtime_dependency_posture",
        "post_detach_runtime_dependency_closure_digest",
        "post_detach_dynamic_loader_posture",
    ),
    "spec/preopen.map.schema.json": (
        "runtime_dependency_posture",
        "runtime_dependency_closure_digest",
        "dynamic_loader_posture",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md": (
        RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE, "runtime dependency closure", "LD_LIBRARY_PATH", "dynamic loader",
    ),
    "adrs/ADR-0340-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md": (
        RUNTIME_POSTURE, LOADER_POSTURE, "runtime dependency closure", "LD_LIBRARY_PATH", "host package state",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/410-desktop-viability-checklist.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_runtime_dependency_closure.py", RUNTIME_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_runtime_dependency_closure.py", RUNTIME_POSTURE),
    "docs/110-juicy-os-lessons.md": (RUNTIME_POSTURE, RECEIPT_POSTURE, LOADER_POSTURE),
    "docs/00-index.md": ("ADR-0340", "docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md", RUNTIME_POSTURE),
    "README.md": ("ADR-0340", "runtime dependency closure", RUNTIME_POSTURE),
    "CHANGELOG.md": ("2026-05-18r496", "check_removable_media_local_runtime_dependency_closure.py", RUNTIME_POSTURE),
}

FORBIDDEN_LOADER_FRAGMENTS = (
    "LD_LIBRARY_PATH=",
    "LD_PRELOAD=",
    "loader-search-enabled",
    "host-global-loader-hints",
    "media-derived-library-path",
    "cwd-library-lookup",
    "/ingest/lib",
)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def main() -> None:
    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for req in reqs:
            *path, expected = req
            try:
                actual = nested_value(obj, path)
            except KeyError as exc:
                fail(f"{rel} missing {'.'.join(path)}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(path)} = {actual!r}, expected {expected!r}")

    preopen = json.loads((ROOT / "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json").read_text(encoding="utf-8"))
    env_allowlist = preopen.get("environment_allowlist", [])
    forbidden_env = [name for name in env_allowlist if name.startswith("LD_") or name in ('DYLD_LIBRARY_PATH', 'LIBPATH')]
    if forbidden_env:
        fail(f"preopen map environment_allowlist contains loader-affecting variables: {forbidden_env}")

    loader_surface = json.dumps({
        "environment_allowlist": env_allowlist,
        "runtime_dependency_posture": preopen.get("runtime_dependency_posture", ""),
        "runtime_dependency_closure_digest": preopen.get("runtime_dependency_closure_digest", ""),
        "dynamic_loader_posture": preopen.get("dynamic_loader_posture", ""),
        "notes": preopen.get("notes", []),
    }, sort_keys=True)
    for frag in FORBIDDEN_LOADER_FRAGMENTS:
        if frag in loader_surface:
            fail(f"preopen map runtime loader surface contains forbidden loader fragment {frag!r}")

    if not preopen.get("runtime_dependency_closure_digest", "").startswith("sha256:"):
        fail("preopen map runtime_dependency_closure_digest must be sha256-shaped")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for field in fields:
            if f'"{field}"' not in text:
                fail(f"{rel} missing schema field {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    print("removable-media local-fallback runtime dependency closure check passed")


if __name__ == "__main__":
    main()
