#!/usr/bin/env python3
"""Render the selected-counterparty first-contact message as an unsent .eml draft.

This deliberately creates only a draft/control artifact. It is not dispatch,
not transport proof, and cannot start a response/no-response clock.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_PACKET = ROOT / "examples" / f"external-contact-request-packet-{REV}-first-artifact.json"
DEFAULT_CARD = ROOT / "examples" / f"external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json"
DEFAULT_OUTPUT = ROOT / "examples" / f"external-contact-mail-ready-draft-{REV}-aiid-not-sent.eml"

MAX_BODY_WORDS = 260

FORBIDDEN = [
    "x-ai-personhood-draft-state: sent",
    "x-ai-personhood-response-clock: open",
    "this message was sent",
    "transport proof captured",
    "creates custody",
    "creates live-floor credit",
    "one boring external artifact",
    "activation, quorum, recompute",
]
REQUIRED_BODY_TERMS = [
    "not asking you to endorse ai personhood",
    "not be treated as waiver",
    "not custody, intake, import, live-floor credit",
]


def load(rel_or_path: Path) -> dict:
    return json.loads(rel_or_path.read_text(encoding="utf-8"))


def render(packet: dict, card: dict) -> str:
    req = packet["outgoing_request"]
    selected = card["selected_candidate"]
    body = req["body"].strip()
    if len(body.split()) > MAX_BODY_WORDS:
        raise SystemExit(f"mail-ready body too long for first-send handoff: {len(body.split())} words > {MAX_BODY_WORDS}")
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if body_hash != card["message_binding"]["final_outgoing_body_sha256"]:
        raise SystemExit("mail-ready draft body hash does not match dispatch authorization card")
    if req["subject"] != card["message_binding"]["subject"]:
        raise SystemExit("mail-ready draft subject does not match dispatch authorization card")
    if selected.get("channel_type") != "public-email":
        raise SystemExit("mail-ready .eml draft requires selected public-email channel")
    recipient = selected["public_channel_locator"]
    text = f"""X-AI-Personhood-Draft-State: NOT-SENT
X-AI-Personhood-Authorization-Card: examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json
X-AI-Personhood-Send-Proof-Record: examples/external-contact-send-proof-record-{REV}-no-transport-proof.json
X-AI-Personhood-Body-SHA256: {body_hash}
X-AI-Personhood-Send-Blockers: human_signature_missing;sender_authority_missing;send_time_locator_recheck_missing;raw_reply_vault_root_missing;private_vault_root_missing;send_time_hash_recompute_missing;transport_proof_missing
X-AI-Personhood-Clock-Guard: draft_may_not_start_response_clock
To: {recipient}
Subject: {req['subject']}
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

{body}
"""
    lowered = text.lower()
    for term in REQUIRED_BODY_TERMS:
        if term not in lowered:
            raise SystemExit(f"mail-ready draft missing body guard term: {term}")
    for phrase in FORBIDDEN:
        if phrase in lowered:
            raise SystemExit(f"mail-ready draft contains forbidden phrase: {phrase}")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--card", default=str(DEFAULT_CARD))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()
    packet_path = Path(args.packet)
    if not packet_path.is_absolute():
        packet_path = (ROOT / packet_path).resolve()
    card_path = Path(args.card)
    if not card_path.is_absolute():
        card_path = (ROOT / card_path).resolve()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    packet = load(packet_path)
    card = load(card_path)
    if packet.get("revision") != REV or card.get("revision") != REV:
        raise SystemExit("mail-ready draft inputs must be current revision")
    if packet.get("no_live_floor_effect") is not True or card.get("no_live_floor_effect") is not True:
        raise SystemExit("mail-ready draft inputs must be no-floor")
    text = render(packet, card)
    if args.check_output:
        existing = out.read_text(encoding="utf-8")
        if existing != text:
            raise SystemExit(f"mail-ready draft mismatch: {out.relative_to(ROOT)}")
        print("render_external_contact_mail_ready_draft: OK")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
