#!/usr/bin/env python3
"""tools/well_known_discovery_card.py

Operator-facing digest card for WellKnownElectionStackDiscovery evidence objects.

This tool is stdlib-only and does NOT verify cryptographic signatures.
It recomputes payload and TBS digests (per docs/176) and prints a bounded
summary suitable for copy/paste publication (docs/204, docs/206).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest

KIND = "hfv.public.well_known_discovery"


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def _render(env: Dict[str, Any], base_dir: Path) -> int:
    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = load_payload_object(env, base_dir)
    if not isinstance(payload_obj, dict):
        raise SystemExit("Payload is not a JSON object")

    discovery_id = str(payload_obj.get("discovery_id") or "")
    discovery_version = str(payload_obj.get("discovery_version") or "")
    generated_at = str(payload_obj.get("generated_at") or "")
    primary_domain = str(payload_obj.get("primary_domain") or "")
    seq = payload_obj.get("sequence")
    prev = str(payload_obj.get("previous_discovery_payload_sha256") or "")

    scope = payload_obj.get("election_scope")
    election_id = ""
    jurisdiction = ""
    if isinstance(scope, dict):
        election_id = str(scope.get("election_id") or "")
        jurisdiction = str(scope.get("jurisdiction") or "")

    pointers = payload_obj.get("pointers")
    pointers = pointers if isinstance(pointers, dict) else {}

    ocd = str(pointers.get("official_channel_directory_payload_sha256") or "")
    pnf = str(pointers.get("public_notice_feed_payload_sha256") or "")
    cix = str(pointers.get("closeout_index_payload_sha256") or "")

    status_url = str(pointers.get("status_board_url") or "")
    feed_url = str(pointers.get("public_notice_feed_url") or "")
    dir_url = str(pointers.get("official_channel_directory_url") or "")

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("Well-known discovery digest card")
    print("-------------------------------")
    if primary_domain:
        print(f"primary_domain:    {primary_domain}")
    if discovery_id:
        print(f"discovery_id:      {discovery_id}")
    if discovery_version:
        print(f"discovery_version: {discovery_version}")
    if election_id or jurisdiction:
        print(f"scope:             {election_id} / {jurisdiction}")
    if generated_at:
        print(f"generated_at:      {generated_at}")
    if isinstance(seq, int):
        print(f"sequence:          {seq}")
    if prev:
        print(f"previous:          {_short_digest(prev)}")

    if ocd:
        print(f"directory_digest:  {_short_digest(ocd)}")
    if pnf:
        print(f"feed_digest:       {_short_digest(pnf)}")
    if cix:
        print(f"closeout_digest:   {_short_digest(cix)}")

    if status_url:
        print(f"status_board_url:  {status_url}")
    if feed_url:
        print(f"feed_url:          {feed_url}")
    if dir_url:
        print(f"directory_url:     {dir_url}")

    print(f"payload_digest:    {_short_digest(recomputed_payload)}")
    print(f"tbs_digest:        {_short_digest(recomputed_tbs)}")
    print(f"status:            {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    print("\nSuggested human-postable short form")
    print("----------------------------------")
    pd = primary_domain or "<primary_domain>"
    line = f"/.well-known/election-stack.json ({pd}) — {_short_digest(declared_payload)}"
    if ocd:
        line += f" — dir {_short_digest(ocd)}"
    if pnf:
        line += f" — feed {_short_digest(pnf)}"
    line += " — verify via packet/envelope receipts"
    print(line)

    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render a bounded digest card for a WellKnownElectionStackDiscovery evidence object"
    )
    ap.add_argument("--packet", default="", help="Evidence packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    args = ap.parse_args()

    if bool(args.packet) == bool(args.envelope):
        raise SystemExit("Provide exactly one of --packet or --envelope")

    if args.packet:
        pkt = Path(args.packet)
        env_path = find_envelope_by_kind(pkt, KIND)
        if not env_path:
            raise SystemExit(f"No {KIND} envelope found under packet/envelopes")
        env = load_json(env_path)
        if not isinstance(env, dict):
            raise SystemExit("Envelope is not a JSON object")
        if str(env.get("kind") or "").strip() != KIND:
            raise SystemExit(f"Not a WellKnownDiscovery envelope (kind={env.get('kind')!r})")
        return _render(env, pkt / "objects")

    env_path = Path(args.envelope)
    env = load_json(env_path)
    if not isinstance(env, dict):
        raise SystemExit("Envelope is not a JSON object")
    if str(env.get("kind") or "").strip() != KIND:
        raise SystemExit(f"Not a WellKnownDiscovery envelope (kind={env.get('kind')!r})")
    return _render(env, env_path.parent)


if __name__ == "__main__":
    raise SystemExit(main())
