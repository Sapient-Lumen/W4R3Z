#!/usr/bin/env python3
"""tools/publication_coverage_report_card.py

Human-friendly extractor for `hfv.coverage.publication_report` envelopes.

This is a stdlib-only helper intended for **publishable deadline coverage** workflows:
- recompute payload/TBS digests (integrity check)
- print a bounded, copy/pasteable summary of PublicationCoverageReport results

It does *not* verify cryptographic signatures.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest


KIND = "hfv.coverage.publication_report"


def short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def find_report_envelope(packet_dir: Path) -> Path | None:
    return find_envelope_by_kind(packet_dir, KIND)


def _as_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _as_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a digest card for a PublicationCoverageReport envelope")
    ap.add_argument("--envelope", default="", help="Path to a PublicationCoverageReport EvidenceEnvelope JSON")
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
        raise SystemExit(f"Not a PublicationCoverageReport envelope (kind={env.get('kind')!r})")

    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = load_payload_object(env, base_dir)
    payload_obj = payload_obj if isinstance(payload_obj, dict) else {}

    contract_id = str(payload_obj.get("contract_id") or "")
    generated_at = str(payload_obj.get("generated_at") or "")
    window_start = str(payload_obj.get("window_start") or "")
    window_end = str(payload_obj.get("window_end") or "")
    events_total = _as_int(payload_obj.get("events_total"), 0)
    events_satisfied = _as_int(payload_obj.get("events_satisfied"), 0)
    events_missed = _as_int(payload_obj.get("events_missed"), 0)
    miss_rate = _as_float(payload_obj.get("miss_rate"), 0.0)

    per_rule = payload_obj.get("per_rule")
    if not isinstance(per_rule, list):
        per_rule = []

    missed_events = payload_obj.get("missed_events")
    if not isinstance(missed_events, list):
        missed_events = []

    issued_at = str(env.get("issued_at") or "")
    issuer_id = ""
    issuer = env.get("issuer")
    if isinstance(issuer, dict):
        issuer_id = str(issuer.get("issuer_id") or "")

    card_status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("PublicationCoverageReport card")
    print("----------------------------")
    if contract_id:
        print(f"contract_id: {contract_id}")
    if generated_at:
        print(f"generated_at:{generated_at}")
    if window_start or window_end:
        print(f"window:     {window_start} → {window_end}".rstrip())
    print(f"events:     total={events_total} satisfied={events_satisfied} missed={events_missed} miss_rate={miss_rate:.3f}")

    # Bounded rule summary.
    rule_bits: List[str] = []
    for r in per_rule[:8]:
        if not isinstance(r, dict):
            continue
        k = str(r.get("kind") or "").strip()
        t = str(r.get("trigger_id") or "").strip()
        tot = _as_int(r.get("events_total"), 0)
        mis = _as_int(r.get("events_missed"), 0)
        mr = _as_float(r.get("miss_rate"), 0.0)
        if not (k and t):
            continue
        rule_bits.append(f"{t}:{k} {mis}/{tot} ({mr:.2f})")
    if rule_bits:
        more = "" if len(per_rule) <= 8 else f" (+{len(per_rule) - 8} more)"
        print(f"per_rule:   {'; '.join(rule_bits)}{more}")
    else:
        print("per_rule:   (none)")

    # Bounded missed-event preview.
    if missed_events:
        head = []
        for me in missed_events[:5]:
            if not isinstance(me, dict):
                continue
            eid = str(me.get("event_id") or "unknown")
            trig = str(me.get("trigger_id") or "")
            ek = str(me.get("expected_kind") or "")
            dl = str(me.get("deadline") or "")
            head.append(f"{eid}:{trig}:{ek}@{dl}")
        more = "" if len(missed_events) <= 5 else f" (+{len(missed_events) - 5} more)"
        if head:
            print(f"missed:     {', '.join(head)}{more}")
        else:
            print(f"missed:     {len(missed_events)}")
    else:
        print("missed:     (none)")

    if issued_at:
        print(f"issued_at:  {issued_at}")
    if issuer_id:
        print(f"issuer_id:  {issuer_id}")

    print(f"payload_digest:{short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {short_digest(recomputed_tbs)}")
    print(f"status:       {card_status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    return 0 if card_status == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
