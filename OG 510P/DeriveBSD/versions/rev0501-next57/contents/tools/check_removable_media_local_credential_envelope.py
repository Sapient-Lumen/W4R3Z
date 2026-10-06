#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach worker credential envelope.

The first host-local removable-media fallback must not regress from a launcher-
fixed, unprivileged worker identity to inherited root/operator credentials,
supplementary groups, setuid/setgid or saved-id regain, or any unrecorded
ambient privilege posture after executable/runtime closure review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREDENTIAL_POSTURE = 'launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups'
RECEIPT_POSTURE = 'receipt-records-worker-credential-envelope'
SUPPLEMENTARY_GROUPS_POSTURE = 'no-supplementary-groups'
PRIVILEGE_REGAIN_POSTURE = 'no-setuid-setgid-saved-id-or-ambient-privilege-regain'
WORKER_USER = 'derive-rm-worker'
WORKER_GROUP = 'derive-rm-worker'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        ("execution", "post_detach_credential_posture", CREDENTIAL_POSTURE),
        ("execution", "post_detach_worker_user", WORKER_USER),
        ("execution", "post_detach_worker_group", WORKER_GROUP),
        ("execution", "post_detach_supplementary_groups_posture", SUPPLEMENTARY_GROUPS_POSTURE),
        ("execution", "post_detach_privilege_regain_posture", PRIVILEGE_REGAIN_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        ("execution", "post_detach_credential_posture", CREDENTIAL_POSTURE),
        ("execution", "post_detach_worker_user", WORKER_USER),
        ("execution", "post_detach_worker_group", WORKER_GROUP),
        ("execution", "post_detach_supplementary_groups_posture", SUPPLEMENTARY_GROUPS_POSTURE),
        ("execution", "post_detach_privilege_regain_posture", PRIVILEGE_REGAIN_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        ("constraints", "post_detach_credential_posture", CREDENTIAL_POSTURE),
        ("constraints", "post_detach_credential_receipt_posture", RECEIPT_POSTURE),
        ("constraints", "post_detach_worker_user", WORKER_USER),
        ("constraints", "post_detach_worker_group", WORKER_GROUP),
        ("constraints", "post_detach_supplementary_groups_posture", SUPPLEMENTARY_GROUPS_POSTURE),
        ("constraints", "post_detach_privilege_regain_posture", PRIVILEGE_REGAIN_POSTURE),
        ("constraints", "post_detach_credential_envelope_required", True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        ("runtime", "mapping", "post_detach_credential_posture", CREDENTIAL_POSTURE),
        ("runtime", "mapping", "post_detach_credential_receipt_posture", RECEIPT_POSTURE),
        ("runtime", "mapping", "post_detach_worker_user", WORKER_USER),
        ("runtime", "mapping", "post_detach_worker_group", WORKER_GROUP),
        ("runtime", "mapping", "post_detach_supplementary_groups_posture", SUPPLEMENTARY_GROUPS_POSTURE),
        ("runtime", "mapping", "post_detach_privilege_regain_posture", PRIVILEGE_REGAIN_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        ("credential_posture", CREDENTIAL_POSTURE),
        ("worker_user", WORKER_USER),
        ("worker_group", WORKER_GROUP),
        ("privilege_regain_posture", PRIVILEGE_REGAIN_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_credential_posture",
        "post_detach_worker_user",
        "post_detach_worker_group",
        "post_detach_supplementary_groups_posture",
        "post_detach_privilege_regain_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_credential_posture",
        "post_detach_worker_user",
        "post_detach_worker_group",
        "post_detach_supplementary_groups_posture",
        "post_detach_privilege_regain_posture",
    ),
    "spec/preopen.map.schema.json": (
        "credential_posture",
        "worker_user",
        "worker_group",
        "supplementary_groups",
        "privilege_regain_posture",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md": (
        CREDENTIAL_POSTURE, RECEIPT_POSTURE, SUPPLEMENTARY_GROUPS_POSTURE, PRIVILEGE_REGAIN_POSTURE,
        "credential envelope", "derive-rm-worker:derive-rm-worker", "setuid/setgid",
    ),
    "adrs/ADR-0341-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md": (
        CREDENTIAL_POSTURE, RECEIPT_POSTURE, SUPPLEMENTARY_GROUPS_POSTURE, PRIVILEGE_REGAIN_POSTURE,
        "credential envelope", "saved-ID regain", "derive-rm-worker:derive-rm-worker",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/410-desktop-viability-checklist.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_credential_envelope.py", CREDENTIAL_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_credential_envelope.py", CREDENTIAL_POSTURE),
    "docs/110-juicy-os-lessons.md": (CREDENTIAL_POSTURE, RECEIPT_POSTURE, PRIVILEGE_REGAIN_POSTURE),
    "docs/00-index.md": ("ADR-0341", "docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md", CREDENTIAL_POSTURE),
    "README.md": ("ADR-0341", "credential envelope", CREDENTIAL_POSTURE),
    "CHANGELOG.md": ("2026-05-18r497", "check_removable_media_local_credential_envelope.py", CREDENTIAL_POSTURE),
}

FORBIDDEN_CREDENTIAL_FRAGMENTS = (
    'uid=0',
    'gid=0',
    'wheel',
    'operator',
    'storage-admin',
    'supplementary-groups-inherited',
    'setuid-enabled',
    'setgid-enabled',
    'saved-id-regain-enabled',
    'ambient-privilege-regain-enabled',
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
    if preopen.get("supplementary_groups") != []:
        fail(f"preopen map supplementary_groups must be empty in first lane: {preopen.get('supplementary_groups')!r}")

    credential_surface = json.dumps({
        "credential_posture": preopen.get("credential_posture", ""),
        "worker_user": preopen.get("worker_user", ""),
        "worker_group": preopen.get("worker_group", ""),
        "supplementary_groups": preopen.get("supplementary_groups", []),
        "privilege_regain_posture": preopen.get("privilege_regain_posture", ""),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_CREDENTIAL_FRAGMENTS:
        if frag in credential_surface:
            fail(f"preopen map credential surface contains forbidden credential fragment {frag!r}")

    if preopen.get("worker_user") == preopen.get("worker_group") == "root":
        fail("preopen map worker user/group must not be root")

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

    print("removable-media local-fallback credential envelope check passed")


if __name__ == "__main__":
    main()
