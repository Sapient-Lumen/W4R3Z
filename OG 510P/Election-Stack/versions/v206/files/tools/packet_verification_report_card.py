#!/usr/bin/env python3
"""tools/packet_verification_report_card.py

Human-friendly extractor for `hfv.verifier.packet_verification_report` envelopes.

This is a stdlib-only helper intended for **publishable verifier output** workflows:
- confirm the envelope digests match recomputation (docs/176)
- print a copy/pasteable “packet verification card” suitable for status pages and reports

It does *not* verify cryptographic signatures.

Usage:
  python3 tools/packet_verification_report_card.py --envelope path/to/packet_verification_report.envelope.json

  # or point at a packet dir; the tool will search envelopes/ for a report
  python3 tools/packet_verification_report_card.py --packet artifacts/examples/evidence_packet_packet_verification_report_minimal
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest
from public_surface_pins import compute_pins


KIND = "hfv.verifier.packet_verification_report"


def short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    """Return a human-friendly short form like sha256:aaaaaaaaaaaa…bbbbbbbb."""

    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def find_report_envelope(packet_dir: Path) -> Path | None:
    return find_envelope_by_kind(packet_dir, KIND)


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a digest card for a PacketVerificationReport envelope")
    ap.add_argument("--envelope", default="", help="Path to a PacketVerificationReport EvidenceEnvelope JSON")
    ap.add_argument("--packet", default="", help="Packet directory (searches envelopes/) for a report")
    args = ap.parse_args()

    if bool(args.envelope) == bool(args.packet):
        raise SystemExit("Provide exactly one of --envelope or --packet")

    env_path: Path
    base_dir: Path

    if args.packet:
        packet_dir = Path(args.packet)
        p = find_report_envelope(packet_dir)
        if not p:
            raise SystemExit(f"No {KIND} envelope found under packet/envelopes")
        env_path = p
        base_dir = packet_dir / "objects"
    else:
        env_path = Path(args.envelope)
        base_dir = env_path.parent

    env = load_json(env_path)
    if env.get("kind") != KIND:
        raise SystemExit(f"Not a PacketVerificationReport envelope (kind={env.get('kind')!r})")

    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = load_payload_object(env, base_dir)
    payload_obj = payload_obj if isinstance(payload_obj, dict) else {}

    # Optional comparability pin check (best-effort): if the report declares pins,
    # compare them to this archive's canonical registry bytes.
    local_pins = compute_pins(all_surfaces=False)

    status = str(payload_obj.get("status") or "")
    generated_at = str(payload_obj.get("generated_at") or "")
    packet_dir = str(payload_obj.get("packet_dir") or "")
    report_version = str(payload_obj.get("report_version") or "")
    manifest_sha = str(payload_obj.get("manifest_sha256") or "")
    vlink = str(payload_obj.get("verifier_report_tbs_digest") or "")
    codebook_sha = str(payload_obj.get("verifier_problem_codes_sha256") or "")
    profiles_sha = str(payload_obj.get("verifier_profiles_sha256") or "")
    kinds_sha = str(payload_obj.get("envelope_kinds_sha256") or "")
    problems = payload_obj.get("problems")
    if not isinstance(problems, list):
        problems = []
    problems = [str(x) for x in problems if str(x).strip()]

    tool = payload_obj.get("tool")
    tool_name = tool.get("name") if isinstance(tool, dict) else ""
    tool_version = tool.get("version") if isinstance(tool, dict) else ""

    issued_at = str(env.get("issued_at") or "")
    issuer_id = ""
    issuer = env.get("issuer")
    if isinstance(issuer, dict):
        issuer_id = str(issuer.get("issuer_id") or "")

    card_status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("PacketVerificationReport card")
    print("---------------------------")
    if report_version:
        print(f"report_version:{report_version}")
    if status:
        print(f"status:      {status}")
    if generated_at:
        print(f"generated_at:{generated_at}")
    if packet_dir:
        print(f"packet_id:   {packet_dir}")
    if tool_name or tool_version:
        print(f"tool:        {tool_name} {tool_version}".rstrip())
    if manifest_sha:
        print(f"manifest:    {short_digest(manifest_sha)}")
    if vlink:
        print(f"verifier:    {short_digest(vlink)}")
    if codebook_sha:
        print(f"codebook:    {short_digest(codebook_sha)}")
    if profiles_sha:
        print(f"profiles:    {short_digest(profiles_sha)}")
    if kinds_sha:
        print(f"kind_reg:    {short_digest(kinds_sha)}")
    if issued_at:
        print(f"issued_at:   {issued_at}")
    if issuer_id:
        print(f"issuer_id:   {issuer_id}")

    # Keep bounded: cards are not reports.
    if problems:
        head = problems[:10]
        more = "" if len(problems) <= 10 else f" (+{len(problems) - 10} more)"
        print(f"problems:    {', '.join(head)}{more}")
    else:
        print("problems:    (none)")

    print(f"payload_digest:{short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {short_digest(recomputed_tbs)}")
    print(f"status:       {card_status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    # Emit bounded warnings for pin mismatches (do not fail the card).
    if codebook_sha and local_pins.get("verifier_problem_codes_sha256") and codebook_sha != local_pins["verifier_problem_codes_sha256"]:
        print(
            f"NOTE: verifier_problem_codes_sha256 pin mismatch (report={short_digest(codebook_sha)} local={short_digest(local_pins['verifier_problem_codes_sha256'])})",
            file=sys.stderr,
        )
    if kinds_sha and local_pins.get("envelope_kinds_sha256") and kinds_sha != local_pins["envelope_kinds_sha256"]:
        print(
            f"NOTE: envelope_kinds_sha256 pin mismatch (report={short_digest(kinds_sha)} local={short_digest(local_pins['envelope_kinds_sha256'])})",
            file=sys.stderr,
        )
    if profiles_sha and local_pins.get("verifier_profiles_sha256") and profiles_sha != local_pins["verifier_profiles_sha256"]:
        print(
            f"NOTE: verifier_profiles_sha256 pin mismatch (report={short_digest(profiles_sha)} local={short_digest(local_pins['verifier_profiles_sha256'])})",
            file=sys.stderr,
        )

    return 0 if card_status == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
