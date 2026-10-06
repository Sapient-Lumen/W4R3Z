#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach network egress.

The first host-local removable-media fallback must not regress from a receipt-
visible no-network post-detach worker into a worker that can use sockets, DNS,
NSS/name-service state, proxy configuration, remote fetches, update checks,
telemetry, license checks, safe-browsing lookups, or callbacks as hidden
derivative input authority or exfiltration paths.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NETWORK_POSTURE = 'network-egress-absent-no-socket-dns-or-remote-callbacks'
NETWORK_RECEIPT_POSTURE = 'receipt-records-network-absent-envelope'
NAME_RESOLUTION_POSTURE = 'no-dns-mdns-nss-or-resolver-host-input'
PROXY_POSTURE = 'no-proxy-or-remote-service-configuration'
REMOTE_DEPENDENCY_POSTURE = 'no-remote-fetch-or-callback-derivative-authority'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_network_posture"), NETWORK_POSTURE),
        (("execution", "post_detach_network_receipt_posture"), NETWORK_RECEIPT_POSTURE),
        (("execution", "post_detach_name_resolution_posture"), NAME_RESOLUTION_POSTURE),
        (("execution", "post_detach_proxy_posture"), PROXY_POSTURE),
        (("execution", "post_detach_remote_dependency_posture"), REMOTE_DEPENDENCY_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_network_posture"), NETWORK_POSTURE),
        (("execution", "post_detach_network_receipt_posture"), NETWORK_RECEIPT_POSTURE),
        (("execution", "post_detach_name_resolution_posture"), NAME_RESOLUTION_POSTURE),
        (("execution", "post_detach_proxy_posture"), PROXY_POSTURE),
        (("execution", "post_detach_remote_dependency_posture"), REMOTE_DEPENDENCY_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_network_posture"), NETWORK_POSTURE),
        (("constraints", "post_detach_network_receipt_posture"), NETWORK_RECEIPT_POSTURE),
        (("constraints", "post_detach_name_resolution_posture"), NAME_RESOLUTION_POSTURE),
        (("constraints", "post_detach_proxy_posture"), PROXY_POSTURE),
        (("constraints", "post_detach_remote_dependency_posture"), REMOTE_DEPENDENCY_POSTURE),
        (("constraints", "post_detach_network_egress_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_network_posture"), NETWORK_POSTURE),
        (("runtime", "mapping", "post_detach_network_receipt_posture"), NETWORK_RECEIPT_POSTURE),
        (("runtime", "mapping", "post_detach_name_resolution_posture"), NAME_RESOLUTION_POSTURE),
        (("runtime", "mapping", "post_detach_proxy_posture"), PROXY_POSTURE),
        (("runtime", "mapping", "post_detach_remote_dependency_posture"), REMOTE_DEPENDENCY_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("network_posture",), NETWORK_POSTURE),
        (("network_receipt_posture",), NETWORK_RECEIPT_POSTURE),
        (("name_resolution_posture",), NAME_RESOLUTION_POSTURE),
        (("proxy_posture",), PROXY_POSTURE),
        (("remote_dependency_posture",), REMOTE_DEPENDENCY_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_network_posture",
        "post_detach_network_receipt_posture",
        "post_detach_name_resolution_posture",
        "post_detach_proxy_posture",
        "post_detach_remote_dependency_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_network_posture",
        "post_detach_network_receipt_posture",
        "post_detach_name_resolution_posture",
        "post_detach_proxy_posture",
        "post_detach_remote_dependency_posture",
    ),
    "spec/preopen.map.schema.json": (
        "network_posture",
        "network_receipt_posture",
        "name_resolution_posture",
        "proxy_posture",
        "remote_dependency_posture",
    ),
}

TEXT_REQUIREMENTS = {
    'docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md': (
        NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE,
        PROXY_POSTURE, REMOTE_DEPENDENCY_POSTURE, "DNS", "NSS", "proxy",
        "remote fetch", "telemetry", "callbacks",
    ),
    'adrs/ADR-0346-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md': (
        NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE,
        PROXY_POSTURE, REMOTE_DEPENDENCY_POSTURE, "DNS/NSS", "proxy",
        "remote fetches", "telemetry", "license",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/410-desktop-viability-checklist.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_network_egress.py", NETWORK_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_network_egress.py", NETWORK_POSTURE),
    "docs/110-juicy-os-lessons.md": (NETWORK_POSTURE, NETWORK_RECEIPT_POSTURE, NAME_RESOLUTION_POSTURE),
    "docs/00-index.md": (
        "ADR-0346",
        'docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md',
        NETWORK_POSTURE,
    ),
    "README.md": ("ADR-0346", "network-egress", NETWORK_POSTURE),
    "CHANGELOG.md": ('2026-05-18r502', "check_removable_media_local_network_egress.py", NETWORK_POSTURE),
}

FORBIDDEN_NETWORK_FRAGMENTS = (
    "network-egress-allowed",
    "dns-ordinary-input",
    "nss-host-service-authority",
    "proxy-config-allowed",
    "remote-fetch-allowed",
    "telemetry-callback-allowed",
    "license-server-ordinary-lane",
    "safe-browsing-lookup-ordinary-lane",
    "receipt-omits-network-envelope",
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
        "network_posture": preopen.get("network_posture", ""),
        "network_receipt_posture": preopen.get("network_receipt_posture", ""),
        "name_resolution_posture": preopen.get("name_resolution_posture", ""),
        "proxy_posture": preopen.get("proxy_posture", ""),
        "remote_dependency_posture": preopen.get("remote_dependency_posture", ""),
        "entries": preopen.get("entries", []),
        "notes": preopen.get("notes", []),
    }, sort_keys=True).lower()
    for frag in FORBIDDEN_NETWORK_FRAGMENTS:
        if frag in surface:
            fail(f"preopen map network-egress surface contains forbidden fragment {frag!r}")
    if "inet_socket" in surface or "cap_connect" in surface or "cap_accept" in surface:
        fail("preopen map must not contain inet socket/connect/accept network authority in the first lane")

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

    print("removable-media local-fallback network-egress check passed")


if __name__ == "__main__":
    main()
