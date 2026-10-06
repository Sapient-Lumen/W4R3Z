#!/usr/bin/env python3
"""Guardrail for the packet-capture local-artifact metadata/retention boundary.

Checks that:
- bounded capture sessions declare a reviewable local-retention budget
- packet-capture summaries classify local raw-artifact metadata posture and retention deadline
- the canonical example stays on the strict `packet-records-only` lane and respects the session retention budget
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION_SCHEMA = ROOT / "spec" / "packet.capture.session.schema.json"
SESSION_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.session.json"
SUMMARY_SCHEMA = ROOT / "spec" / "packet.capture.summary.schema.json"
SUMMARY_EXAMPLE = ROOT / "spec" / "examples" / "packet.capture.summary.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> int:
    errors: list[str] = []

    session_schema = load_json(SESSION_SCHEMA)
    retention = (session_schema.get("properties") or {}).get("retention") or {}
    retention_props = retention.get("properties") or {}
    if "max_local_retention_seconds" not in retention_props:
        errors.append("spec/packet.capture.session.schema.json retention.max_local_retention_seconds missing")
    if "local_storage" not in (retention.get("required") or []):
        errors.append("spec/packet.capture.session.schema.json retention.required must include local_storage")
    if "max_local_retention_seconds" not in (retention.get("required") or []):
        errors.append("spec/packet.capture.session.schema.json retention.required must include max_local_retention_seconds")

    summary_schema = load_json(SUMMARY_SCHEMA)
    artifacts = ((((summary_schema.get("properties") or {}).get("artifacts") or {}).get("properties") or {}).get("local_capture_artifacts") or {})
    items = artifacts.get("items") or {}
    for key in ("metadata_posture", "retention_until"):
        if key not in (items.get("required") or []):
            errors.append(f"spec/packet.capture.summary.schema.json local_capture_artifacts items missing required field: {key}")
    posture_enum = (((items.get("properties") or {}).get("metadata_posture") or {}).get("enum") or [])
    expected = {"packet-records-only", "sideband-metadata-present", "decryption-material-present"}
    if set(posture_enum) != expected:
        errors.append("spec/packet.capture.summary.schema.json metadata_posture enum must match the canonical three-state vocabulary")

    session_example = load_json(SESSION_EXAMPLE)
    summary_example = load_json(SUMMARY_EXAMPLE)
    retention_ex = session_example.get("retention") or {}
    budget = retention_ex.get("max_local_retention_seconds")
    if not isinstance(budget, int) or budget < 1:
        errors.append("spec/examples/packet.capture.session.json retention.max_local_retention_seconds must be a positive integer")

    ended_at = parse_ts(((summary_example.get("window") or {}).get("ended_at") or "1970-01-01T00:00:00Z"))
    for idx, art in enumerate(((summary_example.get("artifacts") or {}).get("local_capture_artifacts") or [])):
        if art.get("metadata_posture") != "packet-records-only":
            errors.append(f"spec/examples/packet.capture.summary.json local_capture_artifacts[{idx}].metadata_posture must stay on packet-records-only in the canonical example")
        if "retention_until" not in art:
            errors.append(f"spec/examples/packet.capture.summary.json local_capture_artifacts[{idx}] missing retention_until")
            continue
        try:
            retention_until = parse_ts(art["retention_until"])
            if isinstance(budget, int) and retention_until > ended_at + __import__("datetime").timedelta(seconds=budget):
                errors.append("spec/examples/packet.capture.summary.json retention_until must not exceed window.ended_at + session retention budget")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid retention_until in packet.capture.summary example: {exc}")

    docs = {
        "docs/507-packet-capture-session-and-summary-first-export-boundary.md": [
            "max_local_retention_seconds",
            "opaque local evidence",
        ],
        "docs/508-packet-capture-summary-review-surface-boundary.md": [
            "metadata_posture",
            "retention_until",
            "packet-records-only",
        ],
        "docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md": [
            "metadata_posture",
            "retention_until",
            "packet-records-only",
            "decryption-material-present",
        ],
        "docs/251-export-policies-and-support-bundle-portal.md": [
            "decryption-material-present",
            "sideband-metadata-present",
        ],
        "docs/216-incident-snapshots-and-support-bundles.md": [
            "metadata_posture",
            "packet-records-only",
        ],
        "docs/229-evidence-spine-overview.md": [
            "metadata_posture",
            "retention_until",
        ],
        "docs/99-llm-runbook.md": [
            "tools/check_packet_capture_artifact_contract.py",
            "metadata_posture",
        ],
    }
    for rel, needles in docs.items():
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in txt:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        print("Packet-capture local artifact contract FAILED:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Packet-capture local artifact contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
