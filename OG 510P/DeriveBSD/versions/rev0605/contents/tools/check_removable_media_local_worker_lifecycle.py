#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach worker lifecycle.

The first host-local removable-media fallback must not regress from a bounded,
launcher-supervised one-shot post-detach worker into daemonization, orphaned
helpers, unreviewed subprocess trees, or derivative receipts emitted before the
reviewed worker tree has exited and been reaped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESS_LIFECYCLE_POSTURE = 'launcher-supervised-no-daemon-or-orphan-descendants'
DESCENDANT_POSTURE = 'no-background-descendants-or-unreviewed-subprocesses'
REAP_POSTURE = 'launcher-reaps-entire-worker-tree-before-receipt'
RECEIPT_POSTURE = 'receipt-records-worker-exit-and-descendant-reap'
WORKER_EXIT_POSTURE = 'worker-exit-observed-before-derivative-receipt'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        ("execution", "post_detach_process_lifecycle_posture", PROCESS_LIFECYCLE_POSTURE),
        ("execution", "post_detach_descendant_posture", DESCENDANT_POSTURE),
        ("execution", "post_detach_reap_posture", REAP_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        ("execution", "post_detach_process_lifecycle_posture", PROCESS_LIFECYCLE_POSTURE),
        ("execution", "post_detach_descendant_posture", DESCENDANT_POSTURE),
        ("execution", "post_detach_reap_posture", REAP_POSTURE),
        ("execution", "post_detach_worker_exit_posture", WORKER_EXIT_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        ("constraints", "post_detach_process_lifecycle_posture", PROCESS_LIFECYCLE_POSTURE),
        ("constraints", "post_detach_lifecycle_receipt_posture", RECEIPT_POSTURE),
        ("constraints", "post_detach_descendant_posture", DESCENDANT_POSTURE),
        ("constraints", "post_detach_reap_posture", REAP_POSTURE),
        ("constraints", "post_detach_process_lifecycle_required", True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        ("runtime", "mapping", "post_detach_process_lifecycle_posture", PROCESS_LIFECYCLE_POSTURE),
        ("runtime", "mapping", "post_detach_lifecycle_receipt_posture", RECEIPT_POSTURE),
        ("runtime", "mapping", "post_detach_descendant_posture", DESCENDANT_POSTURE),
        ("runtime", "mapping", "post_detach_reap_posture", REAP_POSTURE),
        ("runtime", "mapping", "post_detach_worker_exit_posture", WORKER_EXIT_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        ("process_lifecycle_posture", PROCESS_LIFECYCLE_POSTURE),
        ("descendant_posture", DESCENDANT_POSTURE),
        ("reap_posture", REAP_POSTURE),
        ("worker_exit_posture", WORKER_EXIT_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_process_lifecycle_posture",
        "post_detach_descendant_posture",
        "post_detach_reap_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_process_lifecycle_posture",
        "post_detach_descendant_posture",
        "post_detach_reap_posture",
        "post_detach_worker_exit_posture",
    ),
    "spec/preopen.map.schema.json": (
        "process_lifecycle_posture",
        "descendant_posture",
        "reap_posture",
        "worker_exit_posture",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md": (
        PROCESS_LIFECYCLE_POSTURE, DESCENDANT_POSTURE, REAP_POSTURE, RECEIPT_POSTURE,
        WORKER_EXIT_POSTURE, "daemon-free", "unreviewed subprocesses",
    ),
    "adrs/ADR-0342-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md": (
        PROCESS_LIFECYCLE_POSTURE, DESCENDANT_POSTURE, REAP_POSTURE, RECEIPT_POSTURE,
        WORKER_EXIT_POSTURE, "daemon", "orphan descendants",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/410-desktop-viability-checklist.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_worker_lifecycle.py", PROCESS_LIFECYCLE_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_worker_lifecycle.py", PROCESS_LIFECYCLE_POSTURE),
    "docs/110-juicy-os-lessons.md": (PROCESS_LIFECYCLE_POSTURE, RECEIPT_POSTURE, REAP_POSTURE),
    "docs/00-index.md": ("ADR-0342", "docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md", PROCESS_LIFECYCLE_POSTURE),
    "README.md": ("ADR-0342", "worker lifecycle", PROCESS_LIFECYCLE_POSTURE),
    "CHANGELOG.md": ("2026-05-18r498", "check_removable_media_local_worker_lifecycle.py", PROCESS_LIFECYCLE_POSTURE),
}

FORBIDDEN_LIFECYCLE_FRAGMENTS = (
    'daemonize-allowed',
    'background-descendants-allowed',
    'unreviewed-subprocesses-allowed',
    'double-fork-allowed',
    'orphan-descendants-allowed',
    'receipt-before-worker-exit',
    'skip-reap',
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
    lifecycle_surface = json.dumps({
        "process_lifecycle_posture": preopen.get("process_lifecycle_posture", ""),
        "descendant_posture": preopen.get("descendant_posture", ""),
        "reap_posture": preopen.get("reap_posture", ""),
        "worker_exit_posture": preopen.get("worker_exit_posture", ""),
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_LIFECYCLE_FRAGMENTS:
        if frag in lifecycle_surface:
            fail(f"preopen map lifecycle surface contains forbidden lifecycle fragment {frag!r}")

    if preopen.get("worker_exit_posture") != WORKER_EXIT_POSTURE:
        fail("preopen map must record worker exit before derivative receipt authority")

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

    print("removable-media local-fallback worker lifecycle check passed")


if __name__ == "__main__":
    main()
