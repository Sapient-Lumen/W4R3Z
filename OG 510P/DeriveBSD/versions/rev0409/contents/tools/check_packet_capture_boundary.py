#!/usr/bin/env python3
"""Guardrail for the packet-capture / raw-socket / fast-packet-I/O boundary.

This checker keeps DeriveBSD's stronger raw-packet lane wired:
- docs must keep packet capture / raw sockets distinct from ordinary `net-egress-policy`
- flight recorder docs must not silently become packet-capture baselines
- netmap/VALE must remain an explicit default-off acceleration/dataplane lane
- profile/device docs must point at the same fixed boundary
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SUBSTRINGS = {
    "docs/201-network-egress-as-capability.md": [
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
        "stronger lane",
    ],
    "docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md": [
        "not a packet-capture baseline",
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
    ],
    "docs/384-kernel-extensibility-bpf-and-jit-risk.md": [
        "raw packet authority",
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
    ],
    "docs/400-netgraph-and-netmap-as-derived-network-fabrics.md": [
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
        "default-off",
    ],
    "docs/459-outbound-network-posture-by-profile.md": [
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
        "raw packet visibility",
    ],
    "docs/476-device-authority-posture-by-profile.md": [
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
    ],
    "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md": [
        "`net-flow-receipt`",
        "`net-dns-query-receipt`",
        "`net-flow-summary`",
        "/dev/bpf",
        "netmap/VALE",
        "not a subsystem expansion",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0096",
        "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md",
    ],
}

FORBIDDEN_SUBSTRINGS = {
    "docs/201-network-egress-as-capability.md": [
        "Do we want separate grant types for “raw sockets / packet capture”",
        'Do we want separate grant types for "raw sockets / packet capture"',
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in REQUIRED_SUBSTRINGS.items():
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in txt:
                errors.append(f"{rel} missing required text: {needle}")
    for rel, needles in FORBIDDEN_SUBSTRINGS.items():
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle in txt:
                errors.append(f"{rel} still contains forbidden stale text: {needle}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Packet-capture boundary contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
