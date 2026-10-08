#!/usr/bin/env python3
"""tools/compare_public_surface_parity_snapshots.py

Compare two PublicSurfaceParitySnapshot payloads (or packets containing them).

Why this exists:
Parity snapshots are designed to be publishable and comparable, but operators
often need a *tight* way to answer:
  - "What changed between snapshot A and snapshot B?"
  - "Did a split-view resolve, worsen, or move between channels?"

This tool is deliberately bounded:
- stdlib-only
- compares digest/status fields (no bodies)
- emits a short, card-like summary by default

Inputs:
- --a / --b may be either:
  - a packet directory containing an envelope of kind `hfv.public.surface_parity_snapshot`, OR
  - a JSON file that is either:
      * a parity snapshot payload, OR
      * an envelope whose payload resolves to a parity snapshot payload.

Exit codes:
- 0: no differences detected
- 3: differences detected
- 2: parse/load error

"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple




try:
    from tools.compact_notes import extract_compact_context as _extract_compact_context, diff_req as _diff_req_compact
except Exception:
    from compact_notes import extract_compact_context as _extract_compact_context, diff_req as _diff_req_compact


KIND = "hfv.public.surface_parity_snapshot"


def _extract_notes_context_struct(notes: Any) -> Tuple[str, Dict[str, str], str, str]:
    """Return (canonical_context, req_dict, vary, age) extracted from notes."""

    return _extract_compact_context(notes)


def _diff_req(a: Dict[str, str], b: Dict[str, str]) -> List[Dict[str, str]]:
    return _diff_req_compact(a, b)


def _load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _is_envelope(obj: Any) -> bool:
    return isinstance(obj, dict) and ("payload_inline" in obj or "payload_pointer" in obj) and "canonicalization" in obj


def _load_payload_from_envelope(env: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    try:
        from tools.packet_common import load_payload_object
    except Exception:
        from packet_common import load_payload_object

    payload = load_payload_object(env, base_dir)
    if not isinstance(payload, dict):
        raise SystemExit("Envelope payload did not resolve to a JSON object")
    return payload


def load_snapshot(path: Path) -> Tuple[Dict[str, Any], str]:
    """Return (payload, label) for a parity snapshot."""

    if path.is_dir():
        try:
            from tools.packet_common import find_envelope_by_kind, load_json
        except Exception:
            from packet_common import find_envelope_by_kind, load_json

        env_path = find_envelope_by_kind(path, KIND)
        if not env_path:
            raise SystemExit(f"No {KIND} envelope found under {path}/envelopes")
        env = load_json(env_path)
        if not isinstance(env, dict):
            raise SystemExit("Envelope JSON is not an object")
        payload = _load_payload_from_envelope(env, env_path.parent)
        return payload, str(path)

    # File path.
    obj = _load_json(path)
    if _is_envelope(obj):
        env = obj
        payload = _load_payload_from_envelope(env, path.parent)
        return payload, str(path)

    if not isinstance(obj, dict):
        raise SystemExit("Snapshot JSON is not an object")
    return obj, str(path)


@dataclass
class ChannelObs:
    channel_id: str
    http_status: Optional[int]
    body_sha256: str
    envelope_kind: str
    envelope_payload_sha256: str
    envelope_tbs_sha256: str
    notes_context: str
    notes_req: Dict[str, str]
    notes_vary: str
    notes_age: str


def _norm_str(v: Any) -> str:
    return str(v or "").strip()


def _norm_int(v: Any) -> Optional[int]:
    try:
        if v is None or v == "":
            return None
        return int(v)
    except Exception:
        return None


def _extract_notes_context(notes: Any) -> str:
    canon, _, _, _ = _extract_notes_context_struct(notes)
    return canon



def index_observations(payload: Dict[str, Any]) -> Dict[str, ChannelObs]:
    obs = payload.get("observations")
    if not isinstance(obs, list):
        return {}

    out: Dict[str, ChannelObs] = {}
    for o in obs:
        if not isinstance(o, dict):
            continue
        cid = _norm_str(o.get("channel_id"))
        if not cid:
            continue
        canon, req, vary, age = _extract_notes_context_struct(o.get("notes"))
        out[cid] = ChannelObs(
            channel_id=cid,
            http_status=_norm_int(o.get("http_status")),
            body_sha256=_norm_str(o.get("body_sha256")),
            envelope_kind=_norm_str(o.get("envelope_kind")),
            envelope_payload_sha256=_norm_str(o.get("envelope_payload_sha256")),
            envelope_tbs_sha256=_norm_str(o.get("envelope_tbs_sha256")),
            notes_context=canon,
            notes_req=req,
            notes_vary=vary,
            notes_age=age,
        )
    return out


def subject_fingerprint(payload: Dict[str, Any]) -> str:
    subj = payload.get("subject")
    if not isinstance(subj, dict):
        return ""
    # Tight fingerprint: kind + stable target + expected envelope kind.
    return "|".join(
        [
            _norm_str(subj.get("surface_kind")),
            _norm_str(subj.get("stable_target")),
            _norm_str(subj.get("expected_envelope_kind")),
        ]
    )


def compare(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    a_subj = subject_fingerprint(a)
    b_subj = subject_fingerprint(b)

    ia = index_observations(a)
    ib = index_observations(b)

    channels = sorted(set(ia.keys()) | set(ib.keys()))
    diffs: List[Dict[str, Any]] = []

    for cid in channels:
        oa = ia.get(cid)
        ob = ib.get(cid)
        if oa is None:
            diffs.append({"channel_id": cid, "change": "added_in_b"})
            continue
        if ob is None:
            diffs.append({"channel_id": cid, "change": "removed_in_b"})
            continue

        delta: Dict[str, Any] = {"channel_id": cid, "change": "modified"}
        changed = False

        for field in [
            "http_status",
            "body_sha256",
            "envelope_kind",
            "envelope_payload_sha256",
            "envelope_tbs_sha256",
            "notes_context",
        ]:
            va = getattr(oa, field)
            vb = getattr(ob, field)
            if va != vb:
                changed = True
                delta[field] = {"a": va, "b": vb}

        if changed:
            # If compact context changed, also surface a tight key-level delta.
            if "notes_context" in delta:
                req_delta = _diff_req(oa.notes_req, ob.notes_req)
                if req_delta:
                    delta["notes_context"]["req_delta"] = req_delta
                if oa.notes_vary != ob.notes_vary:
                    delta["notes_context"]["vary"] = {"a": oa.notes_vary, "b": ob.notes_vary}
                if oa.notes_age != ob.notes_age:
                    delta["notes_context"]["age"] = {"a": oa.notes_age, "b": ob.notes_age}

            diffs.append(delta)

    contexts_changed = sum(1 for d in diffs if d.get("change") == "modified" and "notes_context" in d)

    return {
        "subject_match": a_subj == b_subj and a_subj != "",
        "subject_a": a_subj,
        "subject_b": b_subj,
        "diffs": diffs,
        "summary": {
            "channels_total": len(channels),
            "channels_changed": len(diffs),
            "channels_context_changed": contexts_changed,
        },
    }


def _short(s: str, n: int = 18) -> str:
    s = str(s or "")
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


def render_card(result: Dict[str, Any], label_a: str, label_b: str) -> str:
    lines: List[str] = []
    lines.append("PublicSurfaceParitySnapshot compare")
    lines.append(f"A: {label_a}")
    lines.append(f"B: {label_b}")

    if not result.get("subject_match"):
        lines.append("subject: MISMATCH")
        sa = str(result.get("subject_a") or "")
        sb = str(result.get("subject_b") or "")
        if sa or sb:
            lines.append(f"  A: {_short(sa, 80)}")
            lines.append(f"  B: {_short(sb, 80)}")
    else:
        lines.append("subject: match")

    s = result.get("summary") or {}
    lines.append(
        "channels: "
        + f"total={int(s.get('channels_total') or 0)} "
        + f"changed={int(s.get('channels_changed') or 0)} "
        + f"context_changed={int(s.get('channels_context_changed') or 0)}"
    )

    diffs = result.get("diffs") or []
    if not diffs:
        lines.append("diff: none")
        return "\n".join(lines) + "\n"

    # Bound the printed detail: show up to 12 channel deltas.
    lines.append("diff:")
    for d in diffs[:12]:
        cid = str(d.get("channel_id") or "")
        ch = str(d.get("change") or "")
        if ch != "modified":
            lines.append(f"  - {cid}: {ch}")
            continue

        # Prefer the most salient field for the first line.
        key = "envelope_payload_sha256" if "envelope_payload_sha256" in d else "body_sha256"
        if key in d:
            a = d[key].get("a")
            b = d[key].get("b")
            lines.append(f"  - {cid}: {key} {str(a)[:16]}… -> {str(b)[:16]}…")
        elif "http_status" in d:
            a = d["http_status"].get("a")
            b = d["http_status"].get("b")
            lines.append(f"  - {cid}: http_status {a} -> {b}")
        else:
            lines.append(f"  - {cid}: modified")        # If request-context/variance hints changed, show a key-level delta (bounded).
        if "notes_context" in d:
            ctx = d["notes_context"] or {}
            a = str(ctx.get("a") or "")
            b = str(ctx.get("b") or "")

            # Prefer key-level diffs if present.
            pieces: List[str] = []
            for item in (ctx.get("req_delta") or [])[:6]:
                k = str(item.get("k") or "")
                va = str(item.get("a") or "")
                vb = str(item.get("b") or "")
                if k:
                    pieces.append(f"{k}:{_short(va, 20)}→{_short(vb, 20)}")

            vdelta = ctx.get("vary") or {}
            if vdelta.get("a") != vdelta.get("b") and (vdelta.get("a") or vdelta.get("b")):
                pieces.append(f"vary:{_short(str(vdelta.get('a') or ''), 16)}→{_short(str(vdelta.get('b') or ''), 16)}")

            adelta = ctx.get("age") or {}
            if adelta.get("a") != adelta.get("b") and (adelta.get("a") or adelta.get("b")):
                pieces.append(f"age:{_short(str(adelta.get('a') or ''), 8)}→{_short(str(adelta.get('b') or ''), 8)}")

            if pieces:
                lines.append("      context: " + "; ".join(pieces))
            elif a or b:
                lines.append(f"      context: {_short(a, 64)} -> {_short(b, 64)}")

    if len(diffs) > 12:
        lines.append(f"  ... ({len(diffs) - 12} more)")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two PublicSurfaceParitySnapshot payloads/packets")
    ap.add_argument("--a", required=True, help="Snapshot A (packet dir or json file)")
    ap.add_argument("--b", required=True, help="Snapshot B (packet dir or json file)")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    args = ap.parse_args()

    try:
        a, label_a = load_snapshot(Path(args.a))
        b, label_b = load_snapshot(Path(args.b))
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        return 2

    result = compare(a, b)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_card(result, label_a, label_b))

    diffs = result.get("diffs") or []
    return 0 if not diffs else 3


if __name__ == "__main__":
    raise SystemExit(main())
