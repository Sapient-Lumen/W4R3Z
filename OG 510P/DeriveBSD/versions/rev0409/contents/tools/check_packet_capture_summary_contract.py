#!/usr/bin/env python3
"""Guardrail for the packet-capture-summary review-surface contract.

Checks that:
- packet capture has a dedicated summary artifact distinct from net-flow-summary
- the canonical example points back to packet.capture.session by digest
- export/incident/evidence docs keep packet.capture.summary visible as the normal review/share surface
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_SCHEMA = ROOT / "spec" / "packet.capture.summary.schema.json"
SUMMARY_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.summary.json"
SESSION_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.session.json"
SESSION_SCHEMA = ROOT / "spec" / "packet.capture.session.schema.json"


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(jcs_bytes(obj)).hexdigest()


def main() -> int:
    errors: list[str] = []

    schema = load_json(SUMMARY_SCHEMA)
    props = schema.get("properties") or {}
    if props.get("kind", {}).get("const") != "packet.capture.summary":
        errors.append("spec/packet.capture.summary.schema.json kind const must be packet.capture.summary")
    if props.get("authority_semantics", {}).get("const") != "packet-capture-summary-evidence-only":
        errors.append("spec/packet.capture.summary.schema.json authority_semantics const must be packet-capture-summary-evidence-only")
    for key in ("session", "window", "protocol_totals", "top_conversations", "artifacts"):
        if key not in (schema.get("required") or []):
            errors.append(f"spec/packet.capture.summary.schema.json missing required field: {key}")

    session_schema = load_json(SESSION_SCHEMA)
    sk = ((((session_schema.get("properties") or {}).get("export") or {}).get("properties") or {}).get("summary_kind") or {}).get("const")
    if sk != "packet.capture.summary":
        errors.append("spec/packet.capture.session.schema.json export.summary_kind must be packet.capture.summary")

    session_example = load_json(SESSION_EXAMPLE)
    summary_example = load_json(SUMMARY_EXAMPLE)
    if summary_example.get("kind") != "packet.capture.summary":
        errors.append("spec/examples/packet.capture.summary.json kind must be packet.capture.summary")
    if summary_example.get("authority_semantics") != "packet-capture-summary-evidence-only":
        errors.append("spec/examples/packet.capture.summary.json authority_semantics must be packet-capture-summary-evidence-only")
    session_ref = summary_example.get("session") or {}
    if session_ref.get("kind") != "packet.capture.session":
        errors.append("spec/examples/packet.capture.summary.json session.kind must be packet.capture.session")
    expected_session_digest = digest(session_example)
    if session_ref.get("digest") != expected_session_digest:
        errors.append("spec/examples/packet.capture.summary.json session.digest must match computed digest of spec/examples/packet.capture.session.json")

    verdict = ((summary_example.get("artifacts") or {}).get("export_verdict"))
    if verdict not in {"metadata-only-default", "summary-only-default", "raw-export-exception-approved", "raw-export-forbidden"}:
        errors.append("spec/examples/packet.capture.summary.json artifacts.export_verdict must be a valid export verdict")

    docs = {
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md": [
            "`packet.capture.summary`",
            "`net-flow-summary` remains the separate learn/audit artifact",
            "`spec/packet.capture.summary.schema.json`",
        ],
        "docs/508-packet-capture-summary-review-surface-boundary.md": [
            "`packet.capture.summary`",
            "evidence-only",
            "`packet.capture.session`",
            "`net-flow-summary`",
        ],
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "`packet.capture.summary`",
            "raw packet bytes should remain an explicit stronger exception",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "`packet.capture.summary`",
            "raw packet payloads by default",
        ],
        "docs/229-evidence-spine-overview.md": [
            "`packet.capture.summary`",
            "`packet.capture.session`",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "`packet.capture.summary`",
            "ADR-0098",
        ],
    }
    for rel, needles in docs.items():
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in txt:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture summary contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Packet-capture summary contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
