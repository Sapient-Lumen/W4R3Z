#!/usr/bin/env python3
"""tools/liveness_beacon_card.py

Human-friendly extractor for `hfv.coverage.liveness_beacon` envelopes.

Purpose:
- recompute envelope payload + TBS digests and make drift obvious
- print a compact, copy/pasteable summary suitable for a status page, incident note,
  or to pair with `PublicSurfaceParitySnapshot` during stale-pointer disputes.

This tool is stdlib-only and does NOT verify cryptographic signatures.

Usage:
  python tools/liveness_beacon_card.py --packet artifacts/examples/evidence_packet_liveness_beacon_minimal
  python tools/liveness_beacon_card.py --envelope path/to/liveness_beacon.envelope.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from envelope_common import tbs_digest_for_envelope
from packet_common import load_payload_object as pc_load_payload_object
from packet_common import recompute_payload_digest as pc_recompute_payload_digest


def short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def find_beacon_envelope(packet_dir: Path) -> Optional[Path]:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return None
    for p in sorted(env_dir.glob("*.json")):
        try:
            env = load_json(p)
        except Exception:
            continue
        if env.get("kind") == "hfv.coverage.liveness_beacon":
            return p
    return None


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


def _fmt_age_seconds(age: Any) -> str:
    try:
        if age is None:
            return ""
        if isinstance(age, bool):
            return ""
        a = float(age)
        if a < 0:
            return ""
        if a < 120:
            return f"{int(a)}s"
        if a < 7200:
            return f"{int(a // 60)}m"
        return f"{int(a // 3600)}h"
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a digest card for a LivenessBeacon envelope")
    ap.add_argument("--envelope", default="", help="Path to a LivenessBeacon EvidenceEnvelope JSON")
    ap.add_argument("--packet", default="", help="Packet directory (searches envelopes/) for a beacon")
    args = ap.parse_args()

    if bool(args.envelope) == bool(args.packet):
        raise SystemExit("Provide exactly one of --envelope or --packet")

    env_path: Path
    base_dir: Path

    if args.packet:
        packet_dir = Path(args.packet)
        p = find_beacon_envelope(packet_dir)
        if not p:
            raise SystemExit("No hfv.coverage.liveness_beacon envelope found under packet/envelopes")
        env_path = p
        base_dir = packet_dir / "objects"
    else:
        env_path = Path(args.envelope)
        base_dir = env_path.parent

    env = load_json(env_path)
    if env.get("kind") != "hfv.coverage.liveness_beacon":
        raise SystemExit(f"Not a LivenessBeacon envelope (kind={env.get('kind')!r})")

    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = pc_recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs
    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)

    payload_obj = pc_load_payload_object(env, base_dir)
    payload_obj = payload_obj if isinstance(payload_obj, dict) else {}

    generated_at = str(payload_obj.get("generated_at") or env.get("issued_at") or "")
    election_scope = str(payload_obj.get("election_scope") or "")
    seq = payload_obj.get("sequence")
    prev = str(payload_obj.get("previous_beacon_payload_sha256") or "")

    watchers = payload_obj.get("watchers")
    watchers_list: list[str] = []
    if isinstance(watchers, list):
        watchers_list = [str(x) for x in watchers if str(x).strip()]

    vantage = payload_obj.get("vantage")
    vantage_s = ""
    if isinstance(vantage, dict):
        parts = []
        for k in ["asn", "country", "region", "provider", "network"]:
            v = str(vantage.get(k) or "").strip()
            if v:
                parts.append(f"{k}={v}")
        vantage_s = ", ".join(parts)

    obs = payload_obj.get("observations")
    obs_list: list[dict[str, Any]] = []
    if isinstance(obs, list):
        obs_list = [x for x in obs if isinstance(x, dict)]

    # Sort observations by surface then observed_at.
    def _key(o: dict[str, Any]) -> tuple[str, str]:
        return (str(o.get("surface") or ""), str(o.get("observed_at") or ""))

    obs_list = sorted(obs_list, key=_key)

    # Build compact per-surface summary.
    lines: list[str] = []
    for o in obs_list[:40]:
        surface = str(o.get("surface") or "")
        result = str(o.get("result") or "")
        http_status = o.get("http_status")
        hs = ""
        if http_status is not None and str(http_status).strip():
            hs = f" {http_status}"  # leading space

        pd = str(o.get("payload_sha256") or "")
        pd_s = short_digest(f"sha256:{pd}" if pd and not pd.startswith("sha256:") else pd)
        if pd_s and pd_s != "":
            pd_s = f" {pd_s}"

        headers = o.get("headers")
        header_bits: list[str] = []
        if isinstance(headers, dict):
            etag = str(headers.get("etag") or "").strip()
            cc = str(headers.get("cache_control") or "").strip()
            age_s = _fmt_age_seconds(headers.get("age_seconds"))
            lm = str(headers.get("last_modified") or "").strip()
            if etag:
                header_bits.append(f"etag={etag}")
            if age_s:
                header_bits.append(f"age={age_s}")
            if lm:
                header_bits.append(f"lm={lm}")
            # Cache-Control can be long; keep only the first chunk.
            if cc:
                cc_short = cc
                if len(cc_short) > 60:
                    cc_short = cc_short[:57] + "…"
                header_bits.append(f"cc={cc_short}")

        hb = (" | " + "; ".join(header_bits)) if header_bits else ""

        # Prefer url_hint if present to avoid printing long URLs.
        url_hint = str(o.get("url_hint") or "").strip()
        ubit = f" [{url_hint}]" if url_hint else ""

        lines.append(f"- {surface}: {result}{hs}{pd_s}{ubit}{hb}")

    # Render card
    print("LivenessBeacon digest card")
    print("------------------------")
    if election_scope:
        print(f"scope:       {election_scope}")
    if isinstance(seq, int) or (isinstance(seq, str) and str(seq).strip()):
        print(f"sequence:    {seq}")
    if generated_at:
        print(f"generated_at:{generated_at}")
    if watchers_list:
        w = ", ".join(watchers_list[:6])
        more = "" if len(watchers_list) <= 6 else f" (+{len(watchers_list)-6} more)"
        print(f"watchers:    {w}{more}")
    if vantage_s:
        print(f"vantage:     {vantage_s}")
    if prev:
        print(f"previous:    {short_digest('sha256:'+prev if prev and not prev.startswith('sha256:') else prev)}")

    print(f"payload_digest:{short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {short_digest(recomputed_tbs)}")
    print(f"status:       {status}")

    if lines:
        print("\nobservations:")
        for ln in lines:
            print(ln)
        if len(obs_list) > 40:
            print(f"- … (+{len(obs_list)-40} more)")

    return 0 if status == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
