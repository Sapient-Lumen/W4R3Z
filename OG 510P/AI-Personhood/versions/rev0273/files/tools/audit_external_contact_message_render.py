#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKET_REL = f"examples/external-contact-request-packet-{REV}-first-artifact.json"
MESSAGE_REL = f"examples/external-contact-rendered-message-{REV}-first-artifact.txt"
TOOL_REL = "tools/render_external_contact_message.py"

packet = json.loads((ROOT / PACKET_REL).read_text(encoding="utf-8"))
message_path = ROOT / MESSAGE_REL
message = message_path.read_text(encoding="utf-8")
body = packet.get("outgoing_request", {}).get("body", "").strip()
body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

for required in [
    f"Subject: {packet['outgoing_request']['subject']}",
    body,
    f"Source packet: {PACKET_REL}",
    f"Execution record to update after sending: examples/external-contact-execution-record-{REV}-ready-to-dispatch.json",
    f"Response triage record to use on silence, decline, ack, or reply: examples/external-contact-response-triage-record-{REV}-pre-dispatch.json",
    f"Final body sha256: {body_hash}",
]:
    if required not in message:
        raise SystemExit(f"rendered external contact message missing required text: {required[:80]}")

lowered = message.lower()
for term in ["not asking", "personhood", "legal status", "trade secrets", "private", "failed-gate", "live-floor", "waiver", "adverse inference"]:
    if term not in lowered:
        raise SystemExit(f"rendered external contact message missing guard term: {term}")
for phrase in ["will count your silence", "silence will be treated", "creates custody", "satisfy intake", "this creates live-floor credit"]:
    if phrase in lowered:
        raise SystemExit(f"rendered external contact message has forbidden overclaim phrase: {phrase}")

subprocess.run([sys.executable, str(ROOT / TOOL_REL), "--check-output"], check=True)
print("audit_external_contact_message_render: OK")
