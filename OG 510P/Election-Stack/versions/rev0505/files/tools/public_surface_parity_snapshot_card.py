#!/usr/bin/env python3
"""tools/public_surface_parity_snapshot_card.py

Operator-facing digest card for PublicSurfaceParitySnapshot evidence objects.

This tool is stdlib-only and does NOT verify cryptographic signatures.
It recomputes payload and TBS digests (per docs/176) and prints a bounded
summary suitable for copy/paste publication.

Why this exists:
Parity failures are legitimacy failures. During drills/incidents, operators and
monitors need a short, comparable summary that proves what each official surface
served at a point in time (docs/201).
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from envelope_common import tbs_digest_for_envelope
from packet_common import load_json, recompute_payload_digest

KIND = "hfv.public.surface_parity_snapshot"

# Optional helper: if present, we can label publishable anomaly-note codes.
try:
    from surface_anomaly_codes import code_of as _an_code_of, is_known as _an_is_known, severity as _an_severity
except Exception:  # pragma: no cover
    def _an_code_of(note: str) -> str:
        if not isinstance(note, str):
            return ""
        s = note.strip()
        return s.split(":", 1)[0] if s else ""

    def _an_is_known(code: str) -> bool:
        return False

    def _an_severity(code: str) -> str:
        return ""


_ANOM_RE = re.compile(r"^[a-z0-9_]{3,64}$")


def _maybe_anomaly_code(note: str) -> str:
    """Return a likely anomaly code from a notes string, or '' if none.

    We only treat *lowercase snake_case* leading tokens as codes to avoid
    misclassifying freeform human notes.
    """
    if not isinstance(note, str):
        return ""
    s = note.strip()
    if not s:
        return ""
    token = s.split(":", 1)[0].strip()
    if not _ANOM_RE.match(token):
        return ""
    return token


def _short_digest(d: str, head: int = 12, tail: int = 8) -> str:
    if not isinstance(d, str) or not d.startswith("sha256:"):
        return str(d)
    h = d.split(":", 1)[1]
    if len(h) <= head + tail:
        return d
    return f"sha256:{h[:head]}…{h[-tail:]}"


def find_envelope(packet_dir: Path) -> Path | None:
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
            out[cid] = f"{label}:{ident}" if ident else label
    return out


def _load_payload(env: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
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
    return payload


def _parity_key(obs: Dict[str, Any]) -> str:
    """Prefer envelope_payload_sha256 for parity comparisons; fall back to body_sha256."""
    ep = str(obs.get("envelope_payload_sha256") or "").strip()
    if ep.startswith("sha256:"):
        return ep
    b = str(obs.get("body_sha256") or "").strip()
    return b


def _render(env: Dict[str, Any], base_dir: Path, root: Path, max_rows: int) -> int:
    declared_payload = str(env.get("payload_digest") or "")
    declared_tbs = str(env.get("tbs_digest") or "")

    recomputed_payload, payload_note = recompute_payload_digest(env, base_dir)
    recomputed_tbs = tbs_digest_for_envelope(env)

    ok_payload = declared_payload == recomputed_payload
    ok_tbs = declared_tbs == recomputed_tbs

    payload = _load_payload(env, base_dir)

    snapshot_id = str(payload.get("snapshot_id") or "")
    snapshot_version = str(payload.get("snapshot_version") or "")
    observed_at = str(payload.get("observed_at") or "")
    prev = str(payload.get("previous_snapshot_sha256") or "")

    scope = payload.get("election_scope")
    election_id = ""
    jurisdiction = ""
    if isinstance(scope, dict):
        election_id = str(scope.get("election_id") or "")
        jurisdiction = str(scope.get("jurisdiction") or "")

    subject = payload.get("subject")
    surface_kind = ""
    stable_target = ""
    expected_kind = ""
    if isinstance(subject, dict):
        surface_kind = str(subject.get("surface_kind") or "")
        stable_target = str(subject.get("stable_target") or "")
        expected_kind = str(subject.get("expected_envelope_kind") or "")

    observations = payload.get("observations")
    if not isinstance(observations, list):
        observations = []

    # Compute parity status over available observations.
    keys = [_parity_key(o) for o in observations if isinstance(o, dict) and _parity_key(o)]
    uniq = sorted(set(keys))
    parity = "UNKNOWN"
    if len(uniq) == 1 and uniq[0]:
        parity = "PARITY_OK"
    elif len(uniq) > 1:
        parity = "PARITY_MISMATCH"

    status = "OK" if (ok_payload and ok_tbs) else "MISMATCH"

    # Bounded diagnostics for parity/missingness drills.
    digest_groups: Dict[str, List[str]] = {}
    status_counts: Dict[int, int] = {}
    parse_error_channels: List[str] = []
    note_codes: Dict[str, int] = {}
    unknown_note_codes: Dict[str, int] = {}
    kind_mismatches: List[str] = []
    for o in observations:
        if not isinstance(o, dict):
            continue
        cid = str(o.get("channel_id") or "").strip() or "(unknown)"
        k = _parity_key(o)
        if k:
            digest_groups.setdefault(k, []).append(cid)
        hs = o.get("http_status")
        if isinstance(hs, int):
            status_counts[hs] = status_counts.get(hs, 0) + 1
        pe = str(o.get("parse_error") or "").strip()
        if pe:
            parse_error_channels.append(cid)
        note = str(o.get("notes") or "").strip()
        if note:
            c = _maybe_anomaly_code(note)
            if c:
                if _an_is_known(c):
                    note_codes[c] = note_codes.get(c, 0) + 1
                else:
                    unknown_note_codes[c] = unknown_note_codes.get(c, 0) + 1
        ek = str(o.get("envelope_kind") or "").strip()
        if expected_kind and ek and ek != expected_kind:
            kind_mismatches.append(cid)

    names = _load_channel_names(root)

    print("PublicSurfaceParitySnapshot digest card")
    print("-------------------------------------")
    if snapshot_id:
        print(f"snapshot_id:      {snapshot_id}")
    if snapshot_version:
        print(f"snapshot_version: {snapshot_version}")
    if election_id or jurisdiction:
        print(f"scope:            {election_id} / {jurisdiction}")
    if observed_at:
        print(f"observed_at:      {observed_at}")
    if surface_kind or stable_target:
        print(f"subject:          {surface_kind} {stable_target}")
    if expected_kind:
        print(f"expected_kind:    {expected_kind}")
    if prev:
        print(f"previous:         {_short_digest(prev)}")

    print(f"observations:     {len(observations)}")
    print(f"parity:           {parity}")
    if uniq:
        print(f"distinct_digests: {len(uniq)}")
        if len(uniq) <= 5:
            for d in uniq:
                print(f"  - {_short_digest(d)}")
        else:
            for d in uniq[:3]:
                print(f"  - {_short_digest(d)}")
            print(f"  - … (+{len(uniq)-3} more)")

    print(f"payload_digest:   {_short_digest(recomputed_payload)}")
    print(f"tbs_digest:       {_short_digest(recomputed_tbs)}")
    print(f"status:           {status}")

    if not ok_payload:
        print(f"NOTE: declared payload_digest does not match recomputation ({payload_note})", file=sys.stderr)
    if not ok_tbs:
        print("NOTE: declared tbs_digest does not match recomputation", file=sys.stderr)



    # Bounded diagnostics (only when useful).
    if parity == "PARITY_MISMATCH" and digest_groups:
        print("\nDigest groups (bounded)")
        print("---------------------")
        dg_keys = sorted(digest_groups.keys())
        max_groups = 5
        for d in dg_keys[:max_groups]:
            chans = digest_groups.get(d, [])
            labels = [names.get(c, c) for c in chans]
            shown = ", ".join(labels[:6])
            more = "" if len(labels) <= 6 else f" (+{len(labels)-6} more)"
            print(f"- {_short_digest(d)}: {shown}{more}")
        if len(dg_keys) > max_groups:
            print(f"- … (+{len(dg_keys)-max_groups} more digests)")

    if status_counts and (len(status_counts) > 1 or next(iter(status_counts.keys())) != 200):
        print("\nHTTP status distribution")
        print("------------------------")
        for hs, cnt in sorted(status_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]:
            print(f"- {hs}: {cnt}")

    if parse_error_channels:
        uniq_pe = sorted(set(parse_error_channels))
        print("\nParse errors")
        print("-----------")
        shown = ", ".join([names.get(c, c) for c in uniq_pe[:6]])
        more = "" if len(uniq_pe) <= 6 else f" (+{len(uniq_pe)-6} more)"
        print(f"- channels: {shown}{more}")

    if kind_mismatches:
        uniq_km = sorted(set(kind_mismatches))
        print("\nExpected envelope-kind mismatches")
        print("-------------------------------")
        shown = ", ".join([names.get(c, c) for c in uniq_km[:6]])
        more = "" if len(uniq_km) <= 6 else f" (+{len(uniq_km)-6} more)"
        print(f"- channels: {shown}{more}")

    if note_codes or unknown_note_codes:
        print("\nAnomaly note codes (bounded)")
        print("---------------------------")
        for c in sorted(note_codes.keys()):
            sev = _an_severity(c)
            print(f"- {c} ({sev}) x{note_codes[c]}")
        if unknown_note_codes:
            total = sum(unknown_note_codes.values())
            # Avoid printing unknown tokens in a publishable surface; report only the count.
            print(f"- unknown_surface_anomaly_code (FAIL) x{total}")

    if observations:
        print("\nChannel observations")
        print("--------------------")
        tail = observations[-max_rows:]
        for o in tail:
            if not isinstance(o, dict):
                continue
            cid = str(o.get("channel_id") or "")
            label = names.get(cid, cid) if cid else "(unknown)"
            url = str(o.get("url") or "")
            hs = o.get("http_status")
            fetched_at = str(o.get("fetched_at") or "")
            key = _parity_key(o)
            ek = str(o.get("envelope_kind") or "")

            line = f"- {label}"
            if isinstance(hs, int):
                line += f" [{hs}]"
            if ek:
                line += f" {ek}"
            if key:
                line += f" {_short_digest(key)}"
            print(line)
            if fetched_at:
                print(f"  fetched_at: {fetched_at}")
            if url:
                print(f"  url:       {url}")

    # Return non-zero when the envelope itself mismatches; parity mismatch is still a valid snapshot.
    return 0 if status == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a bounded digest card for a PublicSurfaceParitySnapshot evidence object")
    ap.add_argument("--packet", default="", help="Evidence packet directory (searches envelopes/)")
    ap.add_argument("--envelope", default="", help="Path to an EvidenceEnvelope JSON")
    ap.add_argument("--max", type=int, default=6, help="Max channel observations to show (from the end)")
    args = ap.parse_args()

    if bool(args.packet) == bool(args.envelope):
        raise SystemExit("Provide exactly one of --packet or --envelope")

    root = Path(__file__).resolve().parents[1]

    if args.packet:
        pkt = Path(args.packet)
        env_path = find_envelope(pkt)
        if not env_path:
            raise SystemExit("No hfv.public.surface_parity_snapshot envelope found under packet/envelopes")
        env = load_json(env_path)
        if not isinstance(env, dict):
            raise SystemExit("Envelope is not a JSON object")
        if str(env.get("kind") or "").strip() != KIND:
            raise SystemExit(f"Not a PublicSurfaceParitySnapshot envelope (kind={env.get('kind')!r})")
        return _render(env, pkt / "objects", root, max_rows=max(1, args.max))

    env_path = Path(args.envelope)
    env = load_json(env_path)
    if not isinstance(env, dict):
        raise SystemExit("Envelope is not a JSON object")
    if str(env.get("kind") or "").strip() != KIND:
        raise SystemExit(f"Not a PublicSurfaceParitySnapshot envelope (kind={env.get('kind')!r})")
    base_dir = env_path.parent
    return _render(env, base_dir, root, max_rows=max(1, args.max))


if __name__ == "__main__":
    raise SystemExit(main())
