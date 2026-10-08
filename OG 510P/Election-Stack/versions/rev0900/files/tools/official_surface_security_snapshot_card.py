#!/usr/bin/env python3
"""tools/official_surface_security_snapshot_card.py

Operator-facing digest card for OfficialSurfaceSecuritySnapshot evidence objects.

This tool is stdlib-only and does NOT verify cryptographic signatures.
It recomputes payload and TBS digests (per docs/176) and prints a bounded
summary suitable for copy/paste publication (docs/199, docs/206).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest

KIND = "hfv.public.surface_security_snapshot"


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def _render(env: Dict[str, Any], base_dir: Path, max_rows: int) -> int:
    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = load_payload_object(env, base_dir)
    if not isinstance(payload_obj, dict):
        raise SystemExit("Payload is not a JSON object")

    snapshot_id = str(payload_obj.get("snapshot_id") or "")
    snapshot_version = str(payload_obj.get("snapshot_version") or "")
    observed_at = str(payload_obj.get("observed_at") or "")
    prev = str(payload_obj.get("previous_snapshot_sha256") or "")

    scope = payload_obj.get("election_scope")
    election_id = ""
    jurisdiction = ""
    if isinstance(scope, dict):
        election_id = str(scope.get("election_id") or "")
        jurisdiction = str(scope.get("jurisdiction") or "")

    target = payload_obj.get("target")
    target = target if isinstance(target, dict) else {}
    primary_domain = str(target.get("primary_domain") or "")
    email_domain = str(target.get("email_domain") or "")

    obs = payload_obj.get("observations")
    if not isinstance(obs, list):
        obs = []

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("OfficialSurfaceSecuritySnapshot digest card")
    print("------------------------------------------")
    if snapshot_id:
        print(f"snapshot_id:      {snapshot_id}")
    if snapshot_version:
        print(f"snapshot_version: {snapshot_version}")
    if election_id or jurisdiction:
        print(f"scope:            {election_id} / {jurisdiction}")
    if primary_domain:
        print(f"primary_domain:   {primary_domain}")
    if email_domain:
        print(f"email_domain:     {email_domain}")
    if observed_at:
        print(f"observed_at:      {observed_at}")
    if prev:
        print(f"previous:         {_short_digest(prev)}")

    print(f"observations:     {len(obs)}")
    print(f"payload_digest:   {_short_digest(recomputed_payload)}")
    print(f"tbs_digest:       {_short_digest(recomputed_tbs)}")
    print(f"status:           {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    if obs:
        print("\nObservations (bounded)")
        print("----------------------")
        for o in obs[: max(1, max_rows)]:
            if not isinstance(o, dict):
                continue
            ctrl = str(o.get("control") or "")
            st = str(o.get("status") or "")
            summary = str(o.get("summary") or "")
            line = f"- {ctrl}" if ctrl else "- (control)"
            if st:
                line += f" [{st}]"
            if summary:
                line += f" {summary}"
            print(line)
        if len(obs) > max_rows:
            print(f"  (+{len(obs) - max_rows} more)")

    print("\nSuggested human-postable short form")
    print("----------------------------------")
    sid = snapshot_id or "<snapshot_id>"
    dom = primary_domain or "<domain>"
    print(f"SurfaceSecuritySnapshot {sid} ({dom}) — {_short_digest(declared_payload)} — verify via packet/envelope receipts")

    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render a bounded digest card for an OfficialSurfaceSecuritySnapshot evidence object"
    )
    ap.add_argument("--packet", default="", help="Evidence packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    ap.add_argument("--max", type=int, default=10, help="Max observations to show")
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
            raise SystemExit(f"Not a SurfaceSecuritySnapshot envelope (kind={env.get('kind')!r})")
        return _render(env, pkt / "objects", max_rows=max(1, args.max))

    env_path = Path(args.envelope)
    env = load_json(env_path)
    if not isinstance(env, dict):
        raise SystemExit("Envelope is not a JSON object")
    if str(env.get("kind") or "").strip() != KIND:
        raise SystemExit(f"Not a SurfaceSecuritySnapshot envelope (kind={env.get('kind')!r})")
    return _render(env, env_path.parent, max_rows=max(1, args.max))


if __name__ == "__main__":
    raise SystemExit(main())
