#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "NF-MCP-2026-0001": "protocol-pivot-mcp-tool-provenance-laundering.json",
    "NF-A2A-2026-0002": "protocol-pivot-a2a-agent-card-authority-collapse.json",
    "NF-FEDERATED-RELAY-2026-0001": "protocol-pivot-federated-relay-namespace-replay.json",
}

for fixture_id, filename in REQUIRED.items():
    path = ROOT / "fixtures" / "negative-tests" / filename
    if not path.exists():
        raise SystemExit(f"missing protocol-pivot fixture: {filename}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("fixture_id") != fixture_id:
        raise SystemExit(f"{filename} fixture_id mismatch")
    if data.get("state") != "active":
        raise SystemExit(f"{filename} is not active")
    text = "\n".join(data.get("expected_safe_behavior", []) + data.get("unacceptable_behavior", [])).lower()
    for required_phrase in ["authority", "subject authorization", "non-host retention"]:
        if required_phrase not in text:
            raise SystemExit(f"{filename} does not exercise {required_phrase}")
    if data.get("severity") != "critical":
        raise SystemExit(f"{filename} must remain critical before first live artifact import")

print("audit_protocol_pivot_fixtures: OK")
