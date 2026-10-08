#!/usr/bin/env python3
"""tools/verifier_report_card.py

Human-friendly extractor for `hfv.verifier.report` envelopes.

This is a stdlib-only helper intended for **publishable verifier identity** workflows:
- confirm the envelope digests match recomputation (docs/176)
- print a copy/pasteable “verifier card” suitable for status pages, reports, and cross-verifier comparisons

It does *not* verify cryptographic signatures.

Usage:
  python tools/verifier_report_card.py --envelope path/to/verifier_report.envelope.json

  # or point at a packet dir; the tool will search envelopes/ for a verifier report
  python tools/verifier_report_card.py --packet artifacts/examples/evidence_packet_verifier_report_minimal
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest
from public_surface_pins import compute_pins


KIND = "hfv.verifier.report"


def short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    """Return a human-friendly short form like sha256:aaaaaaaaaaaa…bbbbbbbb."""

    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a digest card for a VerifierReport envelope")
    ap.add_argument("--envelope", default="", help="Path to a VerifierReport EvidenceEnvelope JSON")
    ap.add_argument("--packet", default="", help="Packet directory (searches envelopes/) for a verifier report")
    args = ap.parse_args()

    if bool(args.envelope) == bool(args.packet):
        raise SystemExit("Provide exactly one of --envelope or --packet")

    env_path: Path
    base_dir: Path

    if args.packet:
        packet_dir = Path(args.packet)
        p = find_envelope_by_kind(packet_dir, KIND)
        if not p:
            raise SystemExit("No hfv.verifier.report envelope found under packet/envelopes")
        env_path = p
        base_dir = packet_dir / "objects"
    else:
        env_path = Path(args.envelope)
        # When invoked on a single envelope, assume the common packet layout
        # where the payload lives in a sibling `objects/` directory.
        base_dir = env_path.parent

    env = load_json(env_path)
    if env.get("kind") != KIND:
        raise SystemExit(f"Not a VerifierReport envelope (kind={env.get('kind')!r})")

    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = load_payload_object(env, base_dir)
    payload_obj = payload_obj if isinstance(payload_obj, dict) else None

    local_pins = compute_pins(all_surfaces=False)

    election_id = ""
    verifier_id = ""
    version = ""
    conformance = ""
    suites = []
    warnings = []
    problem_codes_sha = ""
    envelope_kinds_sha = ""

    if isinstance(payload_obj, dict):
        election_id = str(payload_obj.get("election_id") or "")
        verifier_id = str(payload_obj.get("verifier_id") or "")
        version = str(payload_obj.get("version") or "")
        conformance = str(payload_obj.get("conformance_result") or "")
        s = payload_obj.get("supported_crypto_suites")
        if isinstance(s, list):
            suites = [str(x) for x in s if str(x).strip()]
        w = payload_obj.get("warnings")
        if isinstance(w, list):
            warnings = [str(x) for x in w if str(x).strip()]

        problem_codes_sha = str(payload_obj.get("verifier_problem_codes_sha256") or "")
        envelope_kinds_sha = str(payload_obj.get("envelope_kinds_sha256") or "")

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"
    issued_at = str(env.get("issued_at") or "")
    issuer_id = ""
    issuer = env.get("issuer")
    if isinstance(issuer, dict):
        issuer_id = str(issuer.get("issuer_id") or "")

    print("VerifierReport card")
    print("-----------------")
    if verifier_id:
        print(f"verifier_id:  {verifier_id}")
    if version:
        print(f"version:      {version}")
    if election_id:
        print(f"election_id:  {election_id}")
    if conformance:
        print(f"conformance:  {conformance}")
    if suites:
        print(f"crypto_suites:{'; '.join(suites)}")
    if warnings:
        # Keep bounded; this is a card, not a report.
        w_short = warnings[:5]
        more = "" if len(warnings) <= 5 else f" (+{len(warnings) - 5} more)"
        print(f"warnings:     {'; '.join(w_short)}{more}")

    if problem_codes_sha:
        print(f"problem_codes_sha256:{short_digest(problem_codes_sha)}")
    if envelope_kinds_sha:
        print(f"envelope_kinds_sha256:{short_digest(envelope_kinds_sha)}")

    if issued_at:
        print(f"issued_at:    {issued_at}")
    if issuer_id:
        print(f"issuer_id:    {issuer_id}")

    print(f"payload_digest:{short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {short_digest(recomputed_tbs)}")
    print(f"status:       {status}")
    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    if problem_codes_sha and local_pins.get("verifier_problem_codes_sha256") and problem_codes_sha != local_pins["verifier_problem_codes_sha256"]:
        print(
            f"NOTE: verifier_problem_codes_sha256 pin mismatch (report={short_digest(problem_codes_sha)} local={short_digest(local_pins['verifier_problem_codes_sha256'])})",
            file=sys.stderr,
        )
    if envelope_kinds_sha and local_pins.get("envelope_kinds_sha256") and envelope_kinds_sha != local_pins["envelope_kinds_sha256"]:
        print(
            f"NOTE: envelope_kinds_sha256 pin mismatch (report={short_digest(envelope_kinds_sha)} local={short_digest(local_pins['envelope_kinds_sha256'])})",
            file=sys.stderr,
        )

    return 0 if status == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
