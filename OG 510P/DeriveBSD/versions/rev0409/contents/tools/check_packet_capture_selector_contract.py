#!/usr/bin/env python3
"""Guardrail for the packet-capture selector/compiler boundary.

Checks that:
- packet.capture.session uses a typed packet.capture.selector instead of a free-form filter string
- canonical examples/docs keep backend filter expressions out of the authoritative review surface
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTOR_SCHEMA = ROOT / "spec" / "packet.capture.selector.schema.json"
SELECTOR_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.selector.json"
SESSION_SCHEMA = ROOT / "spec" / "packet.capture.session.schema.json"
SESSION_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.session.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    selector_schema = load(SELECTOR_SCHEMA)
    if ((selector_schema.get("properties") or {}).get("kind") or {}).get("const") != "packet.capture.selector":
        errors.append("spec/packet.capture.selector.schema.json kind const must be packet.capture.selector")
    for key in ("direction", "families", "transports"):
        if key not in (selector_schema.get("required") or []):
            errors.append(f"spec/packet.capture.selector.schema.json missing required field: {key}")

    session_schema = load(SESSION_SCHEMA)
    capture_props = (((session_schema.get("properties") or {}).get("capture") or {}).get("properties") or {})
    if "filter" in capture_props:
        errors.append("spec/packet.capture.session.schema.json must not expose capture.filter as authoritative field")
    selector_ref = (capture_props.get("selector") or {}).get("$ref")
    if selector_ref != "packet.capture.selector.schema.json":
        errors.append("spec/packet.capture.session.schema.json capture.selector must $ref packet.capture.selector.schema.json")
    capture_req = (((session_schema.get("properties") or {}).get("capture") or {}).get("required") or [])
    if "selector" not in capture_req:
        errors.append("spec/packet.capture.session.schema.json capture.required must include selector")

    selector_example = load(SELECTOR_EXAMPLE)
    if selector_example.get("kind") != "packet.capture.selector":
        errors.append("spec/examples/packet.capture.selector.json kind must be packet.capture.selector")

    session_example = load(SESSION_EXAMPLE)
    cap = session_example.get("capture") or {}
    if "filter" in cap:
        errors.append("spec/examples/packet.capture.session.json capture must not contain free-form filter")
    sel = cap.get("selector") or {}
    if sel.get("kind") != "packet.capture.selector":
        errors.append("spec/examples/packet.capture.session.json capture.selector.kind must be packet.capture.selector")

    docs = {
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md": [
            "typed `packet.capture.selector`",
            "selector posture",
        ],
        "docs/509-packet-capture-selector-compiler-boundary.md": [
            "`packet.capture.selector`",
            "compiled consequences",
            "backend-specific capture-filter expressions are implementation detail",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_selector_contract.py",
            "`packet.capture.selector`",
        ],
        "docs/229-evidence-spine-overview.md": [
            "`packet.capture.selector`",
        ],
    }
    for rel, needles in docs.items():
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in txt:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture selector contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Packet-capture selector contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
