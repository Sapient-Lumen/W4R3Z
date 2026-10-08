#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_PACKET = ROOT / "examples" / f"external-contact-request-packet-{REV}-first-artifact.json"
DEFAULT_OUTPUT = ROOT / "examples" / f"external-contact-rendered-message-{REV}-first-artifact.txt"

REQUIRED_GUARD_TERMS = [
    "not asking",
    "personhood",
    "legal status",
    "trade secrets",
    "raw",
    "hash",
    "private",
    "failed-gate",
    "live-floor",
    "waiver",
    "adverse inference",
]
MAX_BODY_WORDS = 260

FORBIDDEN_PHRASES = [
    "we will count your silence",
    "your silence will be treated",
    "you recognize ai personhood",
    "you agree that this creates custody",
    "this response will satisfy intake",
    "this creates live-floor credit",
    "one boring external artifact",
    "activation, quorum, recompute",
]


def load_packet(path: Path) -> dict:
    packet = json.loads(path.read_text(encoding="utf-8"))
    if packet.get("revision") != REV:
        raise SystemExit(f"packet revision mismatch: expected {REV}, got {packet.get('revision')}")
    if packet.get("no_live_floor_effect") is not True:
        raise SystemExit("packet must have no_live_floor_effect=true")
    locks = packet.get("downstream_locks", {})
    for key in ["response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed", "status_claim_allowed"]:
        if locks.get(key) is not False:
            raise SystemExit(f"packet lock not false: {key}")
    return packet


def render(packet: dict) -> str:
    req = packet["outgoing_request"]
    target = packet["target_counterparty"]
    body = req["body"].strip()
    if len(body.split()) > MAX_BODY_WORDS:
        raise SystemExit(f"rendered contact body too long for first-send handoff: {len(body.split())} words > {MAX_BODY_WORDS}")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    text = f"""To: [select independent non-host counterparty; do not fill inside the public release]\nSubject: {req['subject']}\n\n{body}\n\n---\nDispatch controls for steward before sending:\n- Source packet: examples/external-contact-request-packet-{REV}-first-artifact.json\n- Execution record to update after sending: examples/external-contact-execution-record-{REV}-ready-to-dispatch.json\n- Response triage record to use on silence, decline, ack, or reply: examples/external-contact-response-triage-record-{REV}-pre-dispatch.json\n- Selected counterparty kind: {target['counterparty_kind']}\n- Selected organization/contact is intentionally unresolved in this public render until the steward chooses an independent non-host counterparty.\n- Final body sha256: {digest}\n- Do not attach raw private evidence to this public release. Do not infer custody, intake, import, waiver, adverse inference, status recognition, or live-floor credit from sending, silence, decline, acknowledgement, or reply.\n"""
    lowered = text.lower()
    for term in REQUIRED_GUARD_TERMS:
        if term not in lowered:
            raise SystemExit(f"rendered contact message missing guard term: {term}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            raise SystemExit(f"rendered contact message contains forbidden phrase: {phrase}")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()
    packet_path = Path(args.packet)
    if not packet_path.is_absolute():
        packet_path = (ROOT / packet_path).resolve()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    text = render(load_packet(packet_path))
    if args.check_output:
        existing = out.read_text(encoding="utf-8")
        if existing != text:
            raise SystemExit(f"rendered message mismatch: {out.relative_to(ROOT)}")
        print("render_external_contact_message: OK")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
