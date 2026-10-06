#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach ambient inputs.

The first host-local removable-media fallback must not regress from a launcher-
sealed, receipt-visible ambient-input envelope into a worker that lets wall-clock
time, timezone state, host entropy, randomness, hostname, kernel/sysctl facts,
locale, or machine identity become hidden derivative input authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMBIENT_INPUT_POSTURE = 'launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity'
AMBIENT_RECEIPT_POSTURE = 'receipt-records-ambient-input-envelope-and-launcher-owned-timestamps'
CLOCK_POSTURE = 'worker-wall-clock-and-timezone-not-derivative-authority'
RANDOMNESS_POSTURE = 'no-worker-randomness-or-host-entropy-as-derivative-input'
HOST_IDENTITY_POSTURE = 'hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_ambient_input_posture"), AMBIENT_INPUT_POSTURE),
        (("execution", "post_detach_ambient_input_receipt_posture"), AMBIENT_RECEIPT_POSTURE),
        (("execution", "post_detach_clock_posture"), CLOCK_POSTURE),
        (("execution", "post_detach_randomness_posture"), RANDOMNESS_POSTURE),
        (("execution", "post_detach_host_identity_posture"), HOST_IDENTITY_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_ambient_input_posture"), AMBIENT_INPUT_POSTURE),
        (("execution", "post_detach_ambient_input_receipt_posture"), AMBIENT_RECEIPT_POSTURE),
        (("execution", "post_detach_clock_posture"), CLOCK_POSTURE),
        (("execution", "post_detach_randomness_posture"), RANDOMNESS_POSTURE),
        (("execution", "post_detach_host_identity_posture"), HOST_IDENTITY_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_ambient_input_posture"), AMBIENT_INPUT_POSTURE),
        (("constraints", "post_detach_ambient_input_receipt_posture"), AMBIENT_RECEIPT_POSTURE),
        (("constraints", "post_detach_clock_posture"), CLOCK_POSTURE),
        (("constraints", "post_detach_randomness_posture"), RANDOMNESS_POSTURE),
        (("constraints", "post_detach_host_identity_posture"), HOST_IDENTITY_POSTURE),
        (("constraints", "post_detach_ambient_input_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_ambient_input_posture"), AMBIENT_INPUT_POSTURE),
        (("runtime", "mapping", "post_detach_ambient_input_receipt_posture"), AMBIENT_RECEIPT_POSTURE),
        (("runtime", "mapping", "post_detach_clock_posture"), CLOCK_POSTURE),
        (("runtime", "mapping", "post_detach_randomness_posture"), RANDOMNESS_POSTURE),
        (("runtime", "mapping", "post_detach_host_identity_posture"), HOST_IDENTITY_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("ambient_input_posture",), AMBIENT_INPUT_POSTURE),
        (("ambient_input_receipt_posture",), AMBIENT_RECEIPT_POSTURE),
        (("clock_posture",), CLOCK_POSTURE),
        (("randomness_posture",), RANDOMNESS_POSTURE),
        (("host_identity_posture",), HOST_IDENTITY_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_ambient_input_posture",
        "post_detach_ambient_input_receipt_posture",
        "post_detach_clock_posture",
        "post_detach_randomness_posture",
        "post_detach_host_identity_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_ambient_input_posture",
        "post_detach_ambient_input_receipt_posture",
        "post_detach_clock_posture",
        "post_detach_randomness_posture",
        "post_detach_host_identity_posture",
    ),
    "spec/preopen.map.schema.json": (
        "ambient_input_posture",
        "ambient_input_receipt_posture",
        "clock_posture",
        "randomness_posture",
        "host_identity_posture",
    ),
}

TEXT_REQUIREMENTS = {
    'docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md': (
        AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE,
        RANDOMNESS_POSTURE, HOST_IDENTITY_POSTURE, "wall-clock", "host entropy",
        "hostname", "kernel/sysctl", "locale", "machine identity",
    ),
    'adrs/ADR-0345-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md': (
        AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE,
        RANDOMNESS_POSTURE, HOST_IDENTITY_POSTURE, "wall-clock", "host entropy",
        "kernel/sysctl", "locale", "machine identity",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/410-desktop-viability-checklist.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_ambient_input_envelope.py", AMBIENT_INPUT_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_ambient_input_envelope.py", AMBIENT_INPUT_POSTURE),
    "docs/110-juicy-os-lessons.md": (AMBIENT_INPUT_POSTURE, AMBIENT_RECEIPT_POSTURE, CLOCK_POSTURE),
    "docs/00-index.md": (
        "ADR-0345",
        'docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md',
        AMBIENT_INPUT_POSTURE,
    ),
    "README.md": ("ADR-0345", "ambient-input", AMBIENT_INPUT_POSTURE),
    "CHANGELOG.md": ('2026-05-18r501', "check_removable_media_local_ambient_input_envelope.py", AMBIENT_INPUT_POSTURE),
}

FORBIDDEN_AMBIENT_FRAGMENTS = (
    "worker-wall-clock-authority",
    "timezone-derived-output-allowed",
    "host-randomness-allowed",
    "urandom-derivative-input",
    "hostname-derived-output-allowed",
    "sysctl-host-profile-input",
    "locale-host-default-authority",
    "machine-id-ordinary-input",
    "receipt-omits-ambient-inputs",
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
        "ambient_input_posture": preopen.get("ambient_input_posture", ""),
        "ambient_input_receipt_posture": preopen.get("ambient_input_receipt_posture", ""),
        "clock_posture": preopen.get("clock_posture", ""),
        "randomness_posture": preopen.get("randomness_posture", ""),
        "host_identity_posture": preopen.get("host_identity_posture", ""),
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_AMBIENT_FRAGMENTS:
        if frag in surface:
            fail(f"preopen map ambient-input surface contains forbidden fragment {frag!r}")

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

    print("removable-media local-fallback ambient-input envelope check passed")


if __name__ == "__main__":
    main()
