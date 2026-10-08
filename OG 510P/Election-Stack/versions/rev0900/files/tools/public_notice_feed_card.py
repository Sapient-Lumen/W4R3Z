#!/usr/bin/env python3
"""tools/public_notice_feed_card.py

Operator-facing digest card for PublicNoticeFeed evidence objects.

This tool is stdlib-only and does NOT verify cryptographic signatures.
It recomputes payload and TBS digests (per docs/176) and prints a bounded
summary suitable for copy/paste publication.

Why this exists:
A PublicNotice feed (docs/200) is meant to be a compact discovery/index surface.
Operators and monitors often want a short, comparable summary: feed ID, sequence,
window size, previous link, and the most recent notice digests.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from envelope_common import tbs_digest_for_envelope
from packet_common import load_json, recompute_payload_digest

KIND = "hfv.public.notice_feed"


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def find_feed_envelope(packet_dir: Path) -> Path | None:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return None
    for p in sorted(env_dir.glob("*.json")):
        try:
            env = load_json(p)
        except Exception:
            continue
        if isinstance(env, dict) and str(env.get("kind") or "").strip() == KIND:
            return p
    return None


def _load_channel_names(root: Path) -> Dict[str, str]:
    """Best-effort mapping from channel_id → short display hint."""
    reg = root / "artifacts" / "registries" / "official-channels.csv"
    if not reg.exists():
        return {}
    out: Dict[str, str] = {}
    with reg.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            cid = (row.get("channel_id") or "").strip()
            ctype = (row.get("channel_type") or "").strip()
            ident = (row.get("identifier") or "").strip()
            if not cid:
                continue
            label = ctype or "channel"
            if ident:
                out[cid] = f"{label}:{ident}"
            else:
                out[cid] = label
    return out


def _fmt_channels(channels: Any, names: Dict[str, str], limit: int = 6) -> str:
    if not isinstance(channels, list) or not channels:
        return ""
    parts: List[str] = []
    for c in channels[:limit]:
        cid = str(c)
        parts.append(names.get(cid, cid))
    more = "" if len(channels) <= limit else f" (+{len(channels) - limit} more)"
    return ", ".join(parts) + more


def _load_payload(env: Dict[str, Any], base_dir: Path) -> Tuple[Dict[str, Any], str]:
    """Return payload dict and the payload_pointer.uri for context."""
    pp = env.get("payload_pointer")
    if not isinstance(pp, dict):
        raise SystemExit("Missing payload_pointer")
    uri = str(pp.get("uri") or "").strip()
    if not uri:
        raise SystemExit("Missing payload_pointer.uri")
    p = base_dir / uri
    if not p.exists():
        raise SystemExit(f"Missing payload object: {uri}")
    payload = load_json(p)
    if not isinstance(payload, dict):
        raise SystemExit("Payload is not a JSON object")
    return payload, uri


def _render(env: Dict[str, Any], base_dir: Path, root: Path, max_rows: int) -> int:
    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload, _ = _load_payload(env, base_dir)

    feed_id = str(payload.get("feed_id") or "")
    feed_version = str(payload.get("feed_version") or "")
    generated_at = str(payload.get("generated_at") or "")
    seq = payload.get("sequence")
    prev = str(payload.get("previous_feed_payload_sha256") or "")

    scope = payload.get("election_scope")
    election_id = ""
    jurisdiction = ""
    if isinstance(scope, dict):
        election_id = str(scope.get("election_id") or "")
        jurisdiction = str(scope.get("jurisdiction") or "")

    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []

    names = _load_channel_names(root)

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    print("PublicNoticeFeed digest card")
    print("-------------------------")
    if feed_id:
        print(f"feed_id:      {feed_id}")
    if feed_version:
        print(f"feed_version: {feed_version}")
    if election_id or jurisdiction:
        print(f"scope:        {election_id} / {jurisdiction}")
    if generated_at:
        print(f"generated_at: {generated_at}")
    if isinstance(seq, int):
        print(f"sequence:     {seq}")
    if prev:
        print(f"previous:     {_short_digest(prev)}")

    print(f"entries:      {len(entries)}")
    print(f"payload_digest:{_short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {_short_digest(recomputed_tbs)}")
    print(f"status:       {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    if entries:
        print("\nMost recent feed entries")
        print("------------------------")
        tail = entries[-max_rows:]
        for e in tail:
            if not isinstance(e, dict):
                continue
            nid = str(e.get("notice_id") or "")
            nd = str(e.get("notice_payload_sha256") or "")
            ntype = str(e.get("notice_type") or "")
            title = str(e.get("title") or "")
            issued_at = str(e.get("issued_at") or "")
            ch = _fmt_channels(e.get("channels"), names)

            line = f"- {_short_digest(nd)}"
            if ntype:
                line += f" [{ntype}]"
            if title:
                line += f" {title}"
            if nid:
                line += f" (id={nid})"
            print(line)
            if issued_at:
                print(f"  issued_at: {issued_at}")
            if ch:
                print(f"  channels:  {ch}")

    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a bounded digest card for a PublicNoticeFeed evidence object")
    ap.add_argument("--packet", default="", help="Evidence packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    ap.add_argument("--max", type=int, default=5, help="Max feed entries to show (from the end)")
    args = ap.parse_args()

    if bool(args.packet) == bool(args.envelope):
        raise SystemExit("Provide exactly one of --packet or --envelope")

    root = Path(__file__).resolve().parents[1]

    if args.packet:
        pkt = Path(args.packet)
        env_path = find_feed_envelope(pkt)
        if not env_path:
            raise SystemExit("No hfv.public.notice_feed envelope found under packet/envelopes")
        env = load_json(env_path)
        if not isinstance(env, dict):
            raise SystemExit("Envelope is not a JSON object")
        if str(env.get("kind") or "").strip() != KIND:
            raise SystemExit(f"Not a PublicNoticeFeed envelope (kind={env.get('kind')!r})")
        return _render(env, pkt / "objects", root, max_rows=max(1, args.max))

    env_path = Path(args.envelope)
    env = load_json(env_path)
    if not isinstance(env, dict):
        raise SystemExit("Envelope is not a JSON object")
    if str(env.get("kind") or "").strip() != KIND:
        raise SystemExit(f"Not a PublicNoticeFeed envelope (kind={env.get('kind')!r})")
    base_dir = env_path.parent
    return _render(env, base_dir, root, max_rows=max(1, args.max))


if __name__ == "__main__":
    raise SystemExit(main())
