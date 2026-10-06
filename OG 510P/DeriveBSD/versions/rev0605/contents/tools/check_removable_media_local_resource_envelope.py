#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach resource envelope.

The first host-local removable-media fallback must not regress from a bounded,
launcher-enforced one-shot post-detach worker into unbounded CPU, wall-clock,
memory, process, descriptor, scratch, or derivative-output consumption. Resource
limit hits must fail closed rather than minting authoritative derivative output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ENVELOPE_POSTURE = 'launcher-enforced-resource-envelope-no-unbounded-worker-consumption'
RESOURCE_RECEIPT_POSTURE = 'receipt-records-resource-envelope-and-observed-usage'
RESOURCE_FAILURE_POSTURE = 'resource-limit-hit-fails-closed-no-derivative-authority'
OUTPUT_BOUND_POSTURE = 'declared-derivative-output-size-bound-before-receipt'

LIMIT_KEYS = (
    'cpu_time_seconds',
    'wall_clock_seconds',
    'memory_bytes',
    'open_files',
    'processes',
    'scratch_bytes',
    'derivative_output_bytes',
)
USAGE_KEYS = (
    'cpu_time_seconds',
    'wall_clock_seconds',
    'peak_memory_bytes',
    'peak_open_files',
    'processes',
    'scratch_bytes',
    'derivative_output_bytes',
)

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_resource_envelope_posture"), RESOURCE_ENVELOPE_POSTURE),
        (("execution", "post_detach_resource_receipt_posture"), RESOURCE_RECEIPT_POSTURE),
        (("execution", "post_detach_resource_failure_posture"), RESOURCE_FAILURE_POSTURE),
        (("execution", "post_detach_output_bound_posture"), OUTPUT_BOUND_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_resource_envelope_posture"), RESOURCE_ENVELOPE_POSTURE),
        (("execution", "post_detach_resource_receipt_posture"), RESOURCE_RECEIPT_POSTURE),
        (("execution", "post_detach_resource_failure_posture"), RESOURCE_FAILURE_POSTURE),
        (("execution", "post_detach_output_bound_posture"), OUTPUT_BOUND_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_resource_envelope_posture"), RESOURCE_ENVELOPE_POSTURE),
        (("constraints", "post_detach_resource_receipt_posture"), RESOURCE_RECEIPT_POSTURE),
        (("constraints", "post_detach_resource_failure_posture"), RESOURCE_FAILURE_POSTURE),
        (("constraints", "post_detach_output_bound_posture"), OUTPUT_BOUND_POSTURE),
        (("constraints", "post_detach_resource_envelope_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_resource_envelope_posture"), RESOURCE_ENVELOPE_POSTURE),
        (("runtime", "mapping", "post_detach_resource_receipt_posture"), RESOURCE_RECEIPT_POSTURE),
        (("runtime", "mapping", "post_detach_resource_failure_posture"), RESOURCE_FAILURE_POSTURE),
        (("runtime", "mapping", "post_detach_output_bound_posture"), OUTPUT_BOUND_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("resource_envelope_posture",), RESOURCE_ENVELOPE_POSTURE),
        (("resource_receipt_posture",), RESOURCE_RECEIPT_POSTURE),
        (("resource_failure_posture",), RESOURCE_FAILURE_POSTURE),
        (("output_bound_posture",), OUTPUT_BOUND_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_resource_envelope_posture",
        "post_detach_resource_receipt_posture",
        "post_detach_resource_failure_posture",
        "post_detach_output_bound_posture",
        "post_detach_resource_limits",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_resource_envelope_posture",
        "post_detach_resource_receipt_posture",
        "post_detach_resource_failure_posture",
        "post_detach_output_bound_posture",
        "post_detach_resource_limits",
        "post_detach_observed_resource_usage",
    ),
    "spec/preopen.map.schema.json": (
        "resource_envelope_posture",
        "resource_receipt_posture",
        "resource_failure_posture",
        "output_bound_posture",
        "resource_limits",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md": (
        RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE,
        OUTPUT_BOUND_POSTURE, "CPU time", "wall-clock", "derivative-output bytes",
    ),
    "adrs/ADR-0343-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md": (
        RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE,
        OUTPUT_BOUND_POSTURE, "unbounded", "observed usage",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/410-desktop-viability-checklist.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_resource_envelope.py", RESOURCE_ENVELOPE_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_resource_envelope.py", RESOURCE_ENVELOPE_POSTURE),
    "docs/110-juicy-os-lessons.md": (RESOURCE_ENVELOPE_POSTURE, RESOURCE_RECEIPT_POSTURE, RESOURCE_FAILURE_POSTURE),
    "docs/00-index.md": ("ADR-0343", "docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md", RESOURCE_ENVELOPE_POSTURE),
    "README.md": ("ADR-0343", "resource envelope", RESOURCE_ENVELOPE_POSTURE),
    "CHANGELOG.md": ("2026-05-18r499", "check_removable_media_local_resource_envelope.py", RESOURCE_ENVELOPE_POSTURE),
}

FORBIDDEN_RESOURCE_FRAGMENTS = (
    'unbounded-worker-consumption-allowed',
    'resource-limits-host-default-only',
    'resource-limit-hit-may-succeed',
    'unbounded-derivative-output',
    'partial-output-authoritative-after-timeout',
    'tool-self-limits-only',
)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def require_limits(rel: str, obj, path: tuple[str, ...]) -> None:
    limits = nested_value(obj, path)
    if not isinstance(limits, dict):
        fail(f"{rel} {'.'.join(path)} must be an object")
    missing = [k for k in LIMIT_KEYS if k not in limits]
    if missing:
        fail(f"{rel} {'.'.join(path)} missing limits {missing}")
    for key in LIMIT_KEYS:
        val = limits[key]
        if not isinstance(val, int) or val <= 0:
            fail(f"{rel} {'.'.join(path)}.{key} must be a positive integer")
    if limits['processes'] != 1:
        fail(f"{rel} {'.'.join(path)}.processes must stay 1 in the first lane")
    if limits['derivative_output_bytes'] <= 0:
        fail(f"{rel} derivative output bound must be positive")


def require_usage(rel: str, obj, path: tuple[str, ...]) -> None:
    usage = nested_value(obj, path)
    if not isinstance(usage, dict):
        fail(f"{rel} {'.'.join(path)} must be an object")
    missing = [k for k in USAGE_KEYS if k not in usage]
    if missing:
        fail(f"{rel} {'.'.join(path)} missing usage keys {missing}")
    for key in USAGE_KEYS:
        val = usage[key]
        if not isinstance(val, int) or val < 0:
            fail(f"{rel} {'.'.join(path)}.{key} must be a non-negative integer")


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

    for rel, path in (
        ("spec/examples/content.import.plan.removable-media-local-ingest.json", ("execution", "post_detach_resource_limits")),
        ("spec/examples/content.import.receipt.removable-media-local-ingest.json", ("execution", "post_detach_resource_limits")),
        ("spec/examples/device.detach.receipt.removable-media-local-ingest.json", ("runtime", "mapping", "post_detach_resource_limits")),
        ("spec/examples/preopen.map.removable-media-local-ingest-post-detach.json", ("resource_limits",)),
    ):
        require_limits(rel, load_json(rel), path)

    for rel, path in (
        ("spec/examples/content.import.receipt.removable-media-local-ingest.json", ("execution", "post_detach_observed_resource_usage")),
        ("spec/examples/device.detach.receipt.removable-media-local-ingest.json", ("runtime", "mapping", "post_detach_observed_resource_usage")),
    ):
        require_usage(rel, load_json(rel), path)

    preopen = load_json("spec/examples/preopen.map.removable-media-local-ingest-post-detach.json")
    surface = json.dumps({
        "resource_envelope_posture": preopen.get("resource_envelope_posture", ""),
        "resource_receipt_posture": preopen.get("resource_receipt_posture", ""),
        "resource_failure_posture": preopen.get("resource_failure_posture", ""),
        "output_bound_posture": preopen.get("output_bound_posture", ""),
        "resource_limits": preopen.get("resource_limits", {}),
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_RESOURCE_FRAGMENTS:
        if frag in surface:
            fail(f"preopen map resource surface contains forbidden fragment {frag!r}")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for field in fields:
            if f'"{field}"' not in text:
                fail(f"{rel} missing schema field {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    print('removable-media local-fallback resource-envelope check passed')


if __name__ == '__main__':
    main()
