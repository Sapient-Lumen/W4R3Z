#!/usr/bin/env python3
"""Guardrail for the packet-capture-session + summary-first-export contract.

Checks that:
- docs keep packet capture as a typed bounded session rather than ad-hoc blob folklore
- incident/export/evidence docs keep summary-first posture visible
- the canonical schema retains the key fields this boundary depends on
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_REQUIREMENTS = {
    "docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md": [
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md",
        "packet.capture.session",
    ],
    "docs/507-packet-capture-session-and-summary-first-export-boundary.md": [
        "summary-first",
        "packet.capture.session",
        "spec/packet.capture.session.schema.json",
        "spec/examples/packet.capture.session.json",
        "docs/251-export-policies-and-support-bundle-portal.md",
        "docs/216-incident-snapshots-and-support-bundles.md",
    ],
    "docs/251-export-policies-and-support-bundle-portal.md": [
        "packet.capture.session",
        "summary-first",
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md",
    ],
    "docs/216-incident-snapshots-and-support-bundles.md": [
        "packet.capture.session",
        "raw packet payloads by default",
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md",
    ],
    "docs/478-evidence-collection-posture-by-profile.md": [
        "packet capture",
        "summary-first",
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "Packet capture sessions + export posture after the raw-packet boundary [DECIDED]",
        "ADR-0097",
    ],
}

SCHEMA = ROOT / "spec" / "packet.capture.session.schema.json"
EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.session.json"


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    problems: list[str] = []

    for rel, needles in DOC_REQUIREMENTS.items():
        txt = _read(rel)
        for needle in needles:
            if needle not in txt:
                problems.append(f"{rel}: missing required text: {needle!r}")

    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except Exception as e:
        problems.append(f"{SCHEMA.name}: invalid JSON ({e})")
        schema = None

    if isinstance(schema, dict):
        props = schema.get("properties") or {}
        req = schema.get("required") or []
        if props.get("kind", {}).get("const") != "packet.capture.session":
            problems.append("packet.capture.session schema: root kind const must be 'packet.capture.session'")
        for key in ["purpose", "scope", "capture", "bounds", "export"]:
            if key not in req:
                problems.append(f"packet.capture.session schema: required must include {key!r}")

        export_props = ((props.get("export") or {}).get("properties") or {})
        default_mode = (((export_props.get("default_mode") or {}).get("enum")) or [])
        if not {"metadata-only", "summary-only"}.issubset(set(default_mode)):
            problems.append("packet.capture.session schema: export.default_mode must allow metadata-only and summary-only")

    try:
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    except Exception as e:
        problems.append(f"{EXAMPLE.name}: invalid JSON ({e})")
        example = None

    if isinstance(example, dict):
        if example.get("kind") != "packet.capture.session":
            problems.append("packet.capture.session example: kind must be 'packet.capture.session'")
        export = example.get("export") or {}
        if export.get("default_mode") not in {"metadata-only", "summary-only"}:
            problems.append("packet.capture.session example: export.default_mode must be metadata-only or summary-only")

    if problems:
        print("Packet-capture session contract FAILED:\n")
        for p in problems:
            print(f"- {p}")
        return 1

    print("Packet-capture session contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
