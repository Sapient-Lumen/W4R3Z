#!/usr/bin/env python3
"""tools/evidence_object_card.py

One-command, operator-friendly "card" renderer for evidence objects.

Given a packet directory (or a single envelope), this tool:
  - identifies the envelope kind
  - dispatches to the appropriate specialized card tool when available
  - otherwise prints a small generic digest card

Rationale:
During drills/incidents, operators should not need to remember which card tool
matches which kind.

This tool is stdlib-only and does NOT verify cryptographic signatures.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from envelope_common import tbs_digest_for_envelope
from packet_common import load_json, recompute_payload_digest


KIND_TO_TOOL = {
    "hfv.public.notice": "public_notice_card.py",
    "hfv.public.notice_feed": "public_notice_feed_card.py",
    "hfv.public.surface_parity_snapshot": "public_surface_parity_snapshot_card.py",
    "hfv.public.official_channel_directory": "official_channel_directory_card.py",
    "hfv.public.well_known_discovery": "well_known_discovery_card.py",
    "hfv.public.surface_security_snapshot": "official_surface_security_snapshot_card.py",
    "hfv.coverage.liveness_beacon": "liveness_beacon_card.py",
    "hfv.coverage.publication_report": "publication_coverage_report_card.py",
    "hfv.verifier.report": "verifier_report_card.py",
    "hfv.verifier.packet_verification_report": "packet_verification_report_card.py",
}


def _list_envelopes(packet_dir: Path) -> list[Path]:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return []
    return sorted(env_dir.glob("*.json"))


def _pick_envelope(packet_dir: Path, prefer_kind: str) -> Path:
    envs = _list_envelopes(packet_dir)
    if not envs:
        raise SystemExit("No envelopes/ directory found under packet")

    by_kind: dict[str, list[Path]] = {}
    for p in envs:
        try:
            k = str(load_json(p).get("kind") or "").strip()
        except Exception:
            continue
        by_kind.setdefault(k, []).append(p)

    if prefer_kind:
        matches = by_kind.get(prefer_kind, [])
        if not matches:
            ks = ", ".join(sorted(k for k in by_kind.keys() if k))
            raise SystemExit(f"No envelope found for kind={prefer_kind!r}. Kinds present: {ks}")
        # Best-effort: if multiple envelopes share the same kind, pick the first
        # deterministically (cards are a bounded, human-facing surface).
        return sorted(matches)[0]

    # If all envelopes share a single kind, pick the first deterministically.
    present_kinds = [k for k in by_kind.keys() if k]
    if len(set(present_kinds)) == 1 and envs:
        return sorted(envs)[0]

    # If only one envelope exists, use it.
    if len(envs) == 1:
        return envs[0]

    # Prefer an operator-facing surface when present.
    preference = [
        "hfv.public.notice",
        "hfv.verifier.packet_verification_report",
        "hfv.verifier.report",
    ]
    for k in preference:
        matches = by_kind.get(k, [])
        if len(matches) == 1:
            return matches[0]

    ks = ", ".join(sorted(k for k in by_kind.keys() if k))
    raise SystemExit(f"Multiple envelopes present; use --kind to choose. Kinds present: {ks}")


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def _generic_card(env: Dict[str, Any], env_path: Path, base_dir: Path) -> int:
    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")
    kind = str(env.get("kind") or "")
    track = str(env.get("track") or "")
    issued_at = str(env.get("issued_at") or "")

    issuer_id = ""
    issuer = env.get("issuer")
    if isinstance(issuer, dict):
        issuer_id = str(issuer.get("issuer_id") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)
    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"
    print("EvidenceEnvelope card (generic)")
    print("----------------------------")
    if kind:
        print(f"kind:        {kind}")
    if track:
        print(f"track:       {track}")
    if issued_at:
        print(f"issued_at:   {issued_at}")
    if issuer_id:
        print(f"issuer_id:   {issuer_id}")
    ps = str(env.get("payload_schema") or "")
    if ps:
        print(f"schema:      {ps}")

    atts = env.get("attachments")
    if isinstance(atts, list) and atts:
        rels = []
        for a in atts[:10]:
            if isinstance(a, dict):
                rel = str(a.get("rel") or "").strip()
                if rel:
                    rels.append(rel)
        more = "" if len(atts) <= 10 else f" (+{len(atts) - 10} more)"
        if rels:
            print(f"attachments: {', '.join(rels)}{more}")
        else:
            print(f"attachments: {len(atts)}")

    print(f"payload_digest:{_short_digest(recomputed_payload)}")
    print(f"tbs_digest:   {_short_digest(recomputed_tbs)}")
    print(f"status:       {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)
    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Render an operator-friendly card for an evidence object")
    ap.add_argument("--packet", default="", help="Packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    ap.add_argument("--kind", default="", help="When using --packet, pick a specific envelope kind")
    ap.add_argument("--list", action="store_true", help="List kinds found under --packet and exit")
    args = ap.parse_args()

    if bool(args.packet) == bool(args.envelope):
        raise SystemExit("Provide exactly one of --packet or --envelope")

    root = Path(__file__).resolve().parents[1]
    tools_dir = root / "tools"

    if args.packet:
        packet_dir = Path(args.packet)
        if args.list:
            envs = _list_envelopes(packet_dir)
            kinds = []
            for p in envs:
                try:
                    kinds.append(str(load_json(p).get("kind") or ""))
                except Exception:
                    continue
            kinds = [k for k in kinds if k.strip()]
            for k in sorted(set(kinds)):
                print(k)
            return 0

        env_path = _pick_envelope(packet_dir, args.kind)
        env = load_json(env_path)
        kind = str(env.get("kind") or "")
        tool = KIND_TO_TOOL.get(kind, "")
        if tool:
            return subprocess.call([sys.executable, str(tools_dir / tool), "--packet", str(packet_dir)])
        return _generic_card(env if isinstance(env, dict) else {}, env_path, packet_dir / "objects")

    # --envelope path
    env_path = Path(args.envelope)
    env = load_json(env_path)
    kind = str(env.get("kind") or "")
    tool = KIND_TO_TOOL.get(kind, "")
    if tool:
        return subprocess.call([sys.executable, str(tools_dir / tool), "--envelope", str(env_path)])
    return _generic_card(env if isinstance(env, dict) else {}, env_path, env_path.parent)


if __name__ == "__main__":
    raise SystemExit(main())
