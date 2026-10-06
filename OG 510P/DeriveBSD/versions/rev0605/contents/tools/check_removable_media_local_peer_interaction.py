#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach peer interaction.

The first host-local removable-media fallback must not regress from a launcher-
isolated, receipt-visible post-detach worker into a worker that can be controlled
or observed through ambient same-UID peers, parent sessions, procfs/ptrace/ktrace,
or unreviewed IPC surfaces.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PEER_POSTURE = 'launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc'
PEER_RECEIPT_POSTURE = 'receipt-records-peer-isolation-and-signal-policy'
SIGNAL_POSTURE = 'launcher-only-signal-control-no-peer-or-session-control'
IPC_POSTURE = 'no-unreviewed-ipc-sockets-shm-pipes-or-procfs'
PROCFS_POSTURE = 'procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_peer_interaction_posture"), PEER_POSTURE),
        (("execution", "post_detach_peer_interaction_receipt_posture"), PEER_RECEIPT_POSTURE),
        (("execution", "post_detach_signal_posture"), SIGNAL_POSTURE),
        (("execution", "post_detach_ipc_posture"), IPC_POSTURE),
        (("execution", "post_detach_procfs_posture"), PROCFS_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_peer_interaction_posture"), PEER_POSTURE),
        (("execution", "post_detach_peer_interaction_receipt_posture"), PEER_RECEIPT_POSTURE),
        (("execution", "post_detach_signal_posture"), SIGNAL_POSTURE),
        (("execution", "post_detach_ipc_posture"), IPC_POSTURE),
        (("execution", "post_detach_procfs_posture"), PROCFS_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_peer_interaction_posture"), PEER_POSTURE),
        (("constraints", "post_detach_peer_interaction_receipt_posture"), PEER_RECEIPT_POSTURE),
        (("constraints", "post_detach_signal_posture"), SIGNAL_POSTURE),
        (("constraints", "post_detach_ipc_posture"), IPC_POSTURE),
        (("constraints", "post_detach_procfs_posture"), PROCFS_POSTURE),
        (("constraints", "post_detach_peer_interaction_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_peer_interaction_posture"), PEER_POSTURE),
        (("runtime", "mapping", "post_detach_peer_interaction_receipt_posture"), PEER_RECEIPT_POSTURE),
        (("runtime", "mapping", "post_detach_signal_posture"), SIGNAL_POSTURE),
        (("runtime", "mapping", "post_detach_ipc_posture"), IPC_POSTURE),
        (("runtime", "mapping", "post_detach_procfs_posture"), PROCFS_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("peer_interaction_posture",), PEER_POSTURE),
        (("peer_interaction_receipt_posture",), PEER_RECEIPT_POSTURE),
        (("signal_posture",), SIGNAL_POSTURE),
        (("ipc_posture",), IPC_POSTURE),
        (("procfs_posture",), PROCFS_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_peer_interaction_posture",
        "post_detach_peer_interaction_receipt_posture",
        "post_detach_signal_posture",
        "post_detach_ipc_posture",
        "post_detach_procfs_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_peer_interaction_posture",
        "post_detach_peer_interaction_receipt_posture",
        "post_detach_signal_posture",
        "post_detach_ipc_posture",
        "post_detach_procfs_posture",
    ),
    "spec/preopen.map.schema.json": (
        "peer_interaction_posture",
        "peer_interaction_receipt_posture",
        "signal_posture",
        "ipc_posture",
        "procfs_posture",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md": (
        PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE, IPC_POSTURE,
        PROCFS_POSTURE, "same-UID peers", "procfs/ptrace/ktrace", "unreviewed IPC",
    ),
    "adrs/ADR-0344-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md": (
        PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE, IPC_POSTURE,
        PROCFS_POSTURE, "same-UID peers", "debug hooks",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/410-desktop-viability-checklist.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_peer_interaction.py", PEER_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_peer_interaction.py", PEER_POSTURE),
    "docs/110-juicy-os-lessons.md": (PEER_POSTURE, PEER_RECEIPT_POSTURE, SIGNAL_POSTURE),
    "docs/00-index.md": (
        "ADR-0344",
        "docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md",
        PEER_POSTURE,
    ),
    "README.md": ("ADR-0344", "peer-interaction", PEER_POSTURE),
    "CHANGELOG.md": ("2026-05-18r500", "check_removable_media_local_peer_interaction.py", PEER_POSTURE),
}

FORBIDDEN_PEER_FRAGMENTS = (
    "ambient-ptrace-allowed",
    "same-uid-peer-control-allowed",
    "parent-session-signal-control-allowed",
    "unreviewed-ipc-allowed",
    "procfs-visible-by-default",
    "ktrace-debug-hook-ordinary-lane",
    "receipt-omits-peer-isolation",
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
            except KeyError as exc:
                fail(f"{rel} missing {'.'.join(path)}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(path)} = {actual!r}, expected {expected!r}")

    preopen = load_json("spec/examples/preopen.map.removable-media-local-ingest-post-detach.json")
    surface = json.dumps({
        "peer_interaction_posture": preopen.get("peer_interaction_posture", ""),
        "peer_interaction_receipt_posture": preopen.get("peer_interaction_receipt_posture", ""),
        "signal_posture": preopen.get("signal_posture", ""),
        "ipc_posture": preopen.get("ipc_posture", ""),
        "procfs_posture": preopen.get("procfs_posture", ""),
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_PEER_FRAGMENTS:
        if frag in surface:
            fail(f"preopen map peer-interaction surface contains forbidden fragment {frag!r}")

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

    print("removable-media local-fallback peer-interaction check passed")


if __name__ == "__main__":
    main()
