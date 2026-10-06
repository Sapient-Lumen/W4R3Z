#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach persistent state.

The first host-local removable-media fallback must not regress from a
receipt-visible persistent-state-absent worker into a worker that can use
user home directories, host caches, config/state/history stores, crash dumps,
license/tool databases, reusable temp directories, or leftover scratch as
hidden derivative input authority or side-output authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERSISTENT_STATE_POSTURE = 'persistent-state-absent-no-home-cache-or-host-state-writes'
PERSISTENT_RECEIPT_POSTURE = 'receipt-records-persistent-state-absence-and-scratch-cleanup'
SCRATCH_POSTURE = 'launcher-created-empty-scratch-nonauthoritative'
SCRATCH_CLEANUP_POSTURE = 'scratch-destroyed-before-derivative-receipt'
CACHE_CONFIG_POSTURE = 'no-user-home-cache-config-or-history-state'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_persistent_state_posture"), PERSISTENT_STATE_POSTURE),
        (("execution", "post_detach_persistent_state_receipt_posture"), PERSISTENT_RECEIPT_POSTURE),
        (("execution", "post_detach_scratch_posture"), SCRATCH_POSTURE),
        (("execution", "post_detach_scratch_cleanup_posture"), SCRATCH_CLEANUP_POSTURE),
        (("execution", "post_detach_cache_config_posture"), CACHE_CONFIG_POSTURE),
        (("operations", 0, "params", "post_detach_persistent_state_posture"), PERSISTENT_STATE_POSTURE),
        (("operations", 0, "params", "post_detach_scratch_cleanup_posture"), SCRATCH_CLEANUP_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_persistent_state_posture"), PERSISTENT_STATE_POSTURE),
        (("execution", "post_detach_persistent_state_receipt_posture"), PERSISTENT_RECEIPT_POSTURE),
        (("execution", "post_detach_scratch_posture"), SCRATCH_POSTURE),
        (("execution", "post_detach_scratch_cleanup_posture"), SCRATCH_CLEANUP_POSTURE),
        (("execution", "post_detach_cache_config_posture"), CACHE_CONFIG_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_persistent_state_posture"), PERSISTENT_STATE_POSTURE),
        (("constraints", "post_detach_persistent_state_receipt_posture"), PERSISTENT_RECEIPT_POSTURE),
        (("constraints", "post_detach_scratch_posture"), SCRATCH_POSTURE),
        (("constraints", "post_detach_scratch_cleanup_posture"), SCRATCH_CLEANUP_POSTURE),
        (("constraints", "post_detach_cache_config_posture"), CACHE_CONFIG_POSTURE),
        (("constraints", "post_detach_persistent_state_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_persistent_state_posture"), PERSISTENT_STATE_POSTURE),
        (("runtime", "mapping", "post_detach_persistent_state_receipt_posture"), PERSISTENT_RECEIPT_POSTURE),
        (("runtime", "mapping", "post_detach_scratch_posture"), SCRATCH_POSTURE),
        (("runtime", "mapping", "post_detach_scratch_cleanup_posture"), SCRATCH_CLEANUP_POSTURE),
        (("runtime", "mapping", "post_detach_cache_config_posture"), CACHE_CONFIG_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("persistent_state_posture",), PERSISTENT_STATE_POSTURE),
        (("persistent_state_receipt_posture",), PERSISTENT_RECEIPT_POSTURE),
        (("scratch_posture",), SCRATCH_POSTURE),
        (("scratch_cleanup_posture",), SCRATCH_CLEANUP_POSTURE),
        (("cache_config_posture",), CACHE_CONFIG_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_persistent_state_posture",
        "post_detach_persistent_state_receipt_posture",
        "post_detach_scratch_posture",
        "post_detach_scratch_cleanup_posture",
        "post_detach_cache_config_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_persistent_state_posture",
        "post_detach_persistent_state_receipt_posture",
        "post_detach_scratch_posture",
        "post_detach_scratch_cleanup_posture",
        "post_detach_cache_config_posture",
    ),
    "spec/preopen.map.schema.json": (
        "persistent_state_posture",
        "persistent_state_receipt_posture",
        "scratch_posture",
        "scratch_cleanup_posture",
        "cache_config_posture",
    ),
}

TEXT_REQUIREMENTS = {
    'docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md': (
        PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_POSTURE,
        SCRATCH_CLEANUP_POSTURE, CACHE_CONFIG_POSTURE, "$HOME", "XDG", "crash dumps",
        "reusable temporary", "scratch cleanup",
    ),
    'adrs/ADR-0347-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md': (
        PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_POSTURE,
        SCRATCH_CLEANUP_POSTURE, CACHE_CONFIG_POSTURE, "$HOME", "cache", "history",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/410-desktop-viability-checklist.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_persistent_state.py", PERSISTENT_STATE_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_persistent_state.py", PERSISTENT_STATE_POSTURE),
    "docs/110-juicy-os-lessons.md": (PERSISTENT_STATE_POSTURE, PERSISTENT_RECEIPT_POSTURE, SCRATCH_CLEANUP_POSTURE),
    "docs/00-index.md": ("ADR-0347", 'docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md', PERSISTENT_STATE_POSTURE),
    "README.md": ("ADR-0347", "persistent-state", PERSISTENT_STATE_POSTURE),
    "CHANGELOG.md": ("2026-05-18r503", "check_removable_media_local_persistent_state.py", PERSISTENT_STATE_POSTURE),
}

FORBIDDEN_PERSISTENT_FRAGMENTS = (
    "home-cache-allowed",
    "host-state-writes-allowed",
    "persistent-tool-cache-ordinary-lane",
    "reusable-scratch-allowed",
    "scratch-cleanup-best-effort",
    "receipt-omits-scratch-cleanup",
    "xdg-cache-home-authority",
    "tool-history-authority",
    "crash-dump-side-output",
)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def main() -> None:
    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = load_json(rel)
        for path, expected in reqs:
            try:
                actual = nested_value(obj, path)
            except (KeyError, IndexError, TypeError) as exc:
                fail(f"{rel} missing {'.'.join(map(str, path))}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(map(str, path))} = {actual!r}, expected {expected!r}")

    preopen = load_json("spec/examples/preopen.map.removable-media-local-ingest-post-detach.json")
    entries = preopen.get("entries", [])
    if any(e.get("kind") == "dir" for e in entries):
        fail("preopen map must not add directory authority while asserting scratch/persistent-state absence in this first lane")
    surface = json.dumps({
        "persistent_state_posture": preopen.get("persistent_state_posture", ""),
        "persistent_state_receipt_posture": preopen.get("persistent_state_receipt_posture", ""),
        "scratch_posture": preopen.get("scratch_posture", ""),
        "scratch_cleanup_posture": preopen.get("scratch_cleanup_posture", ""),
        "cache_config_posture": preopen.get("cache_config_posture", ""),
        "entries": entries,
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_PERSISTENT_FRAGMENTS:
        if frag in surface:
            fail(f"preopen map persistent-state surface contains forbidden fragment {frag!r}")
    entry_paths = [str(e.get("path", "")) for e in entries]
    for host_path in ("/home", "/root", "/var/cache", "/var/tmp", "/tmp", "/usr/local/etc", "/etc"):
        if any(path == host_path or path.startswith(host_path + "/") for path in entry_paths):
            fail(f"preopen map persistent-state surface must not expose host persistent path {host_path!r}")

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

    print("removable-media local-fallback persistent-state check passed")


if __name__ == "__main__":
    main()
