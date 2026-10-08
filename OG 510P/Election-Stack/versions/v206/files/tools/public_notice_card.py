#!/usr/bin/env python3
"""tools/public_notice_card.py

Human-friendly extractor for `hfv.public.notice` envelopes.

This is a stdlib-only helper intended for **comms-as-evidence** workflows:
- confirm the envelope digests match recomputation (docs/176)
- print a copy/pasteable "digest card" suitable for status pages and social posts

It does *not* verify cryptographic signatures.

Usage:
  python tools/public_notice_card.py --envelope path/to/public_notice.envelope.json

  # or point at a packet dir; the tool will search envelopes/ for a notice
  python tools/public_notice_card.py --packet artifacts/examples/evidence_packet_public_notice
"""

from __future__ import annotations

import argparse
import json
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from envelope_common import tbs_digest_for_envelope
from packet_common import load_payload_object as pc_load_payload_object
from packet_common import recompute_payload_digest as pc_recompute_payload_digest


def short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    """Return a human-friendly short form like sha256:aaaaaaaaaaaa…bbbbbbbb."""

    if not d.startswith("sha256:"):
        return d
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))



def _parse_rfc3339(dt: str) -> datetime | None:
    if not isinstance(dt, str) or not dt.strip():
        return None
    t = dt.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        out = datetime.fromisoformat(t)
        if out.tzinfo is None:
            out = out.replace(tzinfo=timezone.utc)
        return out
    except Exception:
        return None



def load_known_channel_ids() -> set[str]:
    """Best-effort load of canonical channel IDs (registry may contain placeholders)."""

    root = Path(__file__).resolve().parents[1]
    reg = root / "artifacts" / "registries" / "official-channels.csv"
    if not reg.exists():
        return set()
    try:
        with reg.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            out: set[str] = set()
            for row in r:
                cid = (row.get("channel_id") or "").strip()
                if cid:
                    out.add(cid)
            return out
    except Exception:
        return set()


def load_channel_registry() -> Dict[str, Dict[str, str]]:
    """Load the official channels registry (best-effort).

    Returns a mapping channel_id -> row dict (including url/identifier/type).
    """

    root = Path(__file__).resolve().parents[1]
    reg = root / "artifacts" / "registries" / "official-channels.csv"
    out: Dict[str, Dict[str, str]] = {}
    if not reg.exists():
        return out
    try:
        with reg.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                cid = (row.get('channel_id') or '').strip()
                if not cid:
                    continue
                out[cid] = {k: (v or '').strip() for k, v in row.items() if isinstance(k, str)}
    except Exception:
        return {}
    return out

def find_notice_envelope(packet_dir: Path) -> Optional[Path]:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return None
    for p in sorted(env_dir.glob("*.json")):
        try:
            env = load_json(p)
        except Exception:
            continue
        if env.get("kind") == "hfv.public.notice":
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a digest card for a PublicNotice envelope")
    ap.add_argument("--envelope", default="", help="Path to a PublicNotice EvidenceEnvelope JSON")
    ap.add_argument("--packet", default="", help="Packet directory (searches envelopes/) for a notice")
    args = ap.parse_args()

    if bool(args.envelope) == bool(args.packet):
        raise SystemExit("Provide exactly one of --envelope or --packet")

    env_path: Path
    base_dir: Path

    if args.packet:
        packet_dir = Path(args.packet)
        p = find_notice_envelope(packet_dir)
        if not p:
            raise SystemExit("No hfv.public.notice envelope found under packet/envelopes")
        env_path = p
        base_dir = packet_dir / "objects"
    else:
        env_path = Path(args.envelope)
        # When invoked on a single envelope, assume the common packet layout
        # where the payload lives in a sibling `objects/` directory.
        base_dir = env_path.parent

    env = load_json(env_path)
    if env.get("kind") != "hfv.public.notice":
        raise SystemExit(f"Not a PublicNotice envelope (kind={env.get('kind')!r})")

    declared_payload = env.get("payload_digest", "")
    declared_tbs = env.get("tbs_digest", "")

    recomputed_payload, payload_note = pc_recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload_obj = pc_load_payload_object(env, base_dir)
    payload_obj = payload_obj if isinstance(payload_obj, dict) else None

    notice_id = ""
    title = ""
    notice_type = ""
    correction_of = ""
    supersedes = ""
    next_update_at = ""
    channels = []
    issued_at = env.get("issued_at", "")
    if isinstance(payload_obj, dict):
        notice_id = str(payload_obj.get("notice_id", ""))
        title = str(payload_obj.get("title", ""))
        notice_type = str(payload_obj.get("notice_type", ""))
        correction_of = str(payload_obj.get("correction_of_notice_id") or payload_obj.get("correction_of") or "")
        supersedes = str(payload_obj.get("supersedes_notice_id") or "")
        next_update_at = str(payload_obj.get("next_update_at") or "")
        ch = payload_obj.get("channels", [])
        if isinstance(ch, list):
            channels = [str(x) for x in ch if str(x).strip()]

    channel_registry = load_channel_registry()
    known_channel_ids = set(channel_registry.keys()) or load_known_channel_ids()
    unknown_channels = [c for c in channels if known_channel_ids and c not in known_channel_ids]

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"
    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)
    print("PublicNotice digest card")
    print("----------------------")
    if notice_id:
        print(f"notice_id:   {notice_id}")
    if notice_type:
        print(f"type:        {notice_type}")
    if correction_of:
        print(f"corrects:    {correction_of}")
    if title:
        print(f"title:       {title}")
    if issued_at:
        print(f"issued_at:   {issued_at}")
    if supersedes:
        print(f"supersedes:  {supersedes}")
    if next_update_at:
        print(f"next_update: {next_update_at}")
    if channels:
        print(f"channels:   {'; '.join(channels)}")
        if channel_registry:
            resolved = []
            for c in channels:
                row = channel_registry.get(c, {}) if isinstance(channel_registry, dict) else {}
                url = (row.get('url') or '').strip() if isinstance(row, dict) else ''
                if url:
                    resolved.append(f"{c}→{url}")
            if resolved:
                print(f"channel_urls:{' ; '.join(resolved)}")
        if unknown_channels:
            print(
                f"WARNING: unknown channel IDs (not in official-channels.csv): {', '.join(unknown_channels)}",
                file=sys.stderr,
            )
    if correction_of and notice_type and notice_type != "correction":
        print("WARNING: correction_of_notice_id present but notice_type != correction", file=sys.stderr)
    if notice_type == "correction" and not correction_of:
        print("WARNING: notice_type==correction but correction_of_notice_id is missing", file=sys.stderr)
    if next_update_at and issued_at:
        dt_i = _parse_rfc3339(str(issued_at))
        dt_n = _parse_rfc3339(str(next_update_at))
        if dt_i and dt_n and dt_n < dt_i:
            print("WARNING: next_update_at precedes issued_at", file=sys.stderr)
    print(f"payload:     {declared_payload}  ({'OK' if ok_payload else 'MISMATCH'})")
    print(f"tbs:         {declared_tbs}  ({'OK' if ok_tbs else 'MISMATCH'})")
    print("")
    print("Suggested human-postable short form")
    print("----------------------------------")
    # Keep this intentionally tiny; the full digests remain above.
    nid = notice_id or "<notice_id>"
    extra = ""
    if notice_type:
        extra = f" ({notice_type})"
    if notice_type == "correction" and correction_of:
        extra += f" corrects {correction_of}"
    line = f"PublicNotice {nid}{extra} — {short_digest(declared_payload)}"
    if next_update_at:
        line += f" — next update by {next_update_at}"
    line += " — verify via packet/envelope receipts"
    print(line)
    print("")
    print(f"status: {status}")
    return 0 if status == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
