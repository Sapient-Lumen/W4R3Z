#!/usr/bin/env python3
"""tools/official_channel_directory_card.py

Operator-facing digest card for OfficialChannelDirectory evidence objects.

This tool is stdlib-only and does NOT verify cryptographic signatures.
It recomputes payload and TBS digests (per docs/176) and prints a bounded
summary suitable for copy/paste publication (docs/203, docs/206).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from envelope_common import tbs_digest_for_envelope
from packet_common import find_envelope_by_kind, load_json, load_payload_object, recompute_payload_digest

KIND = "hfv.public.official_channel_directory"


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def _fmt_channel(e: Dict[str, Any]) -> str:
    cid = str(e.get("channel_id") or "").strip()
    ident = str(e.get("identifier") or "").strip()
    url = str(e.get("url") or "").strip()
    ctype = str(e.get("channel_type") or "").strip()

    parts: List[str] = []
    if cid:
        parts.append(cid)
    if ctype:
        parts.append(f"[{ctype}]")
    if ident:
        parts.append(ident)
    line = " ".join(parts).strip()
    if url:
        line += f" → {url}"
    return line or "(invalid channel entry)"


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

    directory_id = str(payload_obj.get("directory_id") or "")
    directory_version = str(payload_obj.get("directory_version") or "")
    generated_at = str(payload_obj.get("generated_at") or "")
    seq = payload_obj.get("sequence")
    prev = str(payload_obj.get("previous_directory_payload_sha256") or "")

    scope = payload_obj.get("election_scope")
    election_id = ""
    jurisdiction = ""
    if isinstance(scope, dict):
        election_id = str(scope.get("election_id") or "")
        jurisdiction = str(scope.get("jurisdiction") or "")

    channels = payload_obj.get("channels")
    if not isinstance(channels, list):
        channels = []

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("OfficialChannelDirectory digest card")
    print("-----------------------------------")
    if directory_id:
        print(f"directory_id:      {directory_id}")
    if directory_version:
        print(f"directory_version: {directory_version}")
    if election_id or jurisdiction:
        print(f"scope:             {election_id} / {jurisdiction}")
    if generated_at:
        print(f"generated_at:      {generated_at}")
    if isinstance(seq, int):
        print(f"sequence:          {seq}")
    if prev:
        print(f"previous:          {_short_digest(prev)}")

    print(f"channels:          {len(channels)}")
    print(f"payload_digest:    {_short_digest(recomputed_payload)}")
    print(f"tbs_digest:        {_short_digest(recomputed_tbs)}")
    print(f"status:            {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    if channels:
        print("\nChannel entries (bounded)")
        print("-------------------------")
        for e in channels[: max(1, max_rows)]:
            if isinstance(e, dict):
                print(f"- {_fmt_channel(e)}")
        if len(channels) > max_rows:
            print(f"  (+{len(channels) - max_rows} more)")

    print("\nSuggested human-postable short form")
    print("----------------------------------")
    did = directory_id or "<directory_id>"
    print(f"OfficialChannelDirectory {did} — {_short_digest(declared_payload)} — verify via packet/envelope receipts")

    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render a bounded digest card for an OfficialChannelDirectory evidence object"
    )
    ap.add_argument("--packet", default="", help="Evidence packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    ap.add_argument("--max", type=int, default=8, help="Max channel entries to show")
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
            raise SystemExit(f"Not an OfficialChannelDirectory envelope (kind={env.get('kind')!r})")
        return _render(env, pkt / "objects", max_rows=max(1, args.max))

    env_path = Path(args.envelope)
    env = load_json(env_path)
    if not isinstance(env, dict):
        raise SystemExit("Envelope is not a JSON object")
    if str(env.get("kind") or "").strip() != KIND:
        raise SystemExit(f"Not an OfficialChannelDirectory envelope (kind={env.get('kind')!r})")
    return _render(env, env_path.parent, max_rows=max(1, args.max))


if __name__ == "__main__":
    raise SystemExit(main())
