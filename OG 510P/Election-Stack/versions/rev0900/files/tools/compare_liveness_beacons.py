#!/usr/bin/env python3
"""tools/compare_liveness_beacons.py

Compare two LivenessBeacon payloads (or packets containing them).

Why this exists:
Liveness beacons are a bounded “missingness” surface for public pointers.
Operators frequently need a *tight* answer to:
  - "Did reachability/freshness change between beacon A and B?"
  - "Did a stale-pointer symptom resolve or move between surfaces?"

This tool is deliberately bounded:
- stdlib-first
- compares only digest/status/freshness fields (no bodies)
- emits a short, card-like summary by default

Inputs:
- --a / --b may be either:
  - a packet directory containing an envelope of kind `hfv.coverage.liveness_beacon`, OR
  - a JSON file that is either:
      * a beacon payload, OR
      * an EvidenceEnvelope whose payload resolves to a beacon payload.

Exit codes:
- 0: no differences detected
- 3: differences detected
- 2: parse/load error

"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


KIND = "hfv.coverage.liveness_beacon"

_NOTE_CODE_RE = re.compile(r"^[a-z0-9_]{3,64}$")


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


def load_beacon(path: Path) -> Tuple[Dict[str, Any], str]:
    """Return (payload, label) for a liveness beacon."""

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

    obj = _load_json(path)
    if _is_envelope(obj):
        payload = _load_payload_from_envelope(obj, path.parent)
        return payload, str(path)

    if not isinstance(obj, dict):
        raise SystemExit("Beacon JSON is not an object")
    return obj, str(path)


def _norm_str(v: Any) -> str:
    return str(v or "").strip()


def _norm_int(v: Any) -> Optional[int]:
    try:
        if v is None or v == "":
            return None
        return int(v)
    except Exception:
        return None


def _note_code(notes: Any) -> str:
    s = _norm_str(notes)
    if not s:
        return ""
    head = s.split(":", 1)[0].split(None, 1)[0].strip()
    if _NOTE_CODE_RE.fullmatch(head):
        return head
    return ""


@dataclass
class SurfaceObs:
    surface: str
    result: str
    http_status: Optional[int]
    payload_sha256: str
    etag: str
    cache_control: str
    age_seconds: Optional[int]
    last_modified: str
    note_code: str
    obs_count: int


def _pick_latest(observations: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], int]:
    """Pick a representative observation for a surface.

    If multiple observations exist for the same surface, pick the one with the
    lexicographically greatest observed_at (best-effort), and return (obs, count).
    """

    if not observations:
        return {}, 0
    if len(observations) == 1:
        return observations[0], 1

    def key(o: Dict[str, Any]) -> str:
        return _norm_str(o.get("observed_at"))

    obs = sorted(observations, key=key)[-1]
    return obs, len(observations)


def index_observations(payload: Dict[str, Any]) -> Dict[str, SurfaceObs]:
    obs = payload.get("observations")
    if not isinstance(obs, list):
        return {}

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for o in obs:
        if not isinstance(o, dict):
            continue
        s = _norm_str(o.get("surface"))
        if not s:
            continue
        grouped.setdefault(s, []).append(o)

    out: Dict[str, SurfaceObs] = {}
    for surface, items in grouped.items():
        o, count = _pick_latest(items)
        headers = o.get("headers") if isinstance(o, dict) else None
        if not isinstance(headers, dict):
            headers = {}
        out[surface] = SurfaceObs(
            surface=surface,
            result=_norm_str(o.get("result")),
            http_status=_norm_int(o.get("http_status")),
            payload_sha256=_norm_str(o.get("payload_sha256")),
            etag=_norm_str(headers.get("etag")),
            cache_control=_norm_str(headers.get("cache_control")),
            age_seconds=_norm_int(headers.get("age_seconds")),
            last_modified=_norm_str(headers.get("last_modified")),
            note_code=_note_code(o.get("notes")),
            obs_count=count,
        )

    return out


def scope_fingerprint(payload: Dict[str, Any]) -> str:
    scope = payload.get("election_scope")
    if not isinstance(scope, dict):
        return ""
    return "|".join([_norm_str(scope.get("election_id")), _norm_str(scope.get("jurisdiction"))])


def watchers_set(payload: Dict[str, Any]) -> set[str]:
    w = payload.get("watchers")
    if not isinstance(w, list):
        return set()
    return {str(x).strip() for x in w if str(x).strip()}


def compare(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    a_scope = scope_fingerprint(a)
    b_scope = scope_fingerprint(b)

    wa = watchers_set(a)
    wb = watchers_set(b)

    ia = index_observations(a)
    ib = index_observations(b)

    surfaces = sorted(set(ia.keys()) | set(ib.keys()))
    diffs: List[Dict[str, Any]] = []

    for s in surfaces:
        oa = ia.get(s)
        ob = ib.get(s)
        if oa is None:
            diffs.append({"surface": s, "change": "added_in_b"})
            continue
        if ob is None:
            diffs.append({"surface": s, "change": "removed_in_b"})
            continue

        delta: Dict[str, Any] = {"surface": s, "change": "modified"}
        changed = False

        for field in [
            "result",
            "http_status",
            "payload_sha256",
            "etag",
            "cache_control",
            "age_seconds",
            "last_modified",
            "note_code",
            "obs_count",
        ]:
            va = getattr(oa, field)
            vb = getattr(ob, field)
            if va != vb:
                changed = True
                delta[field] = {"a": va, "b": vb}

        if changed:
            diffs.append(delta)

    return {
        "scope_match": a_scope == b_scope and a_scope != "",
        "scope_a": a_scope,
        "scope_b": b_scope,
        "watchers": {
            "a_count": len(wa),
            "b_count": len(wb),
            "added_in_b": sorted(wb - wa),
            "removed_in_b": sorted(wa - wb),
        },
        "diffs": diffs,
        "summary": {
            "surfaces_total": len(surfaces),
            "surfaces_changed": len(diffs),
        },
    }


def _short(s: str, n: int = 18) -> str:
    s = str(s or "")
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


def render_card(result: Dict[str, Any], label_a: str, label_b: str) -> str:
    lines: List[str] = []
    lines.append("LivenessBeacon compare")
    lines.append(f"A: {label_a}")
    lines.append(f"B: {label_b}")

    if not result.get("scope_match"):
        lines.append("scope: MISMATCH")
        sa = str(result.get("scope_a") or "")
        sb = str(result.get("scope_b") or "")
        if sa or sb:
            lines.append(f"  A: {_short(sa, 80)}")
            lines.append(f"  B: {_short(sb, 80)}")
    else:
        lines.append("scope: match")

    w = result.get("watchers") or {}
    add = w.get("added_in_b") or []
    rem = w.get("removed_in_b") or []
    lines.append(f"watchers: a={int(w.get('a_count') or 0)} b={int(w.get('b_count') or 0)}")
    if add:
        lines.append(f"  + {', '.join([_short(x, 40) for x in add[:6]])}{' …' if len(add) > 6 else ''}")
    if rem:
        lines.append(f"  - {', '.join([_short(x, 40) for x in rem[:6]])}{' …' if len(rem) > 6 else ''}")

    s = result.get("summary") or {}
    lines.append(
        f"surfaces: total={int(s.get('surfaces_total') or 0)} changed={int(s.get('surfaces_changed') or 0)}"
    )

    diffs = result.get("diffs") or []
    if not diffs:
        lines.append("diff: none")
        return "\n".join(lines) + "\n"

    lines.append("diff:")
    for d in diffs[:12]:
        surface = str(d.get("surface") or "")
        ch = str(d.get("change") or "")
        if ch != "modified":
            lines.append(f"  - {surface}: {ch}")
            continue

        # Prefer the most salient field for one-line output.
        if "result" in d:
            a = d["result"].get("a")
            b = d["result"].get("b")
            lines.append(f"  - {surface}: result {a} -> {b}")
            continue
        if "payload_sha256" in d:
            a = d["payload_sha256"].get("a")
            b = d["payload_sha256"].get("b")
            lines.append(f"  - {surface}: payload {str(a)[:16]}… -> {str(b)[:16]}…")
            continue
        if "etag" in d:
            a = d["etag"].get("a")
            b = d["etag"].get("b")
            lines.append(f"  - {surface}: etag {str(a)[:16]}… -> {str(b)[:16]}…")
            continue
        if "http_status" in d:
            a = d["http_status"].get("a")
            b = d["http_status"].get("b")
            lines.append(f"  - {surface}: http_status {a} -> {b}")
            continue
        lines.append(f"  - {surface}: modified")

    if len(diffs) > 12:
        lines.append(f"  ... ({len(diffs) - 12} more)")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two LivenessBeacon payloads or packets")
    ap.add_argument("--a", required=True, help="Path to packet dir or JSON file (A)")
    ap.add_argument("--b", required=True, help="Path to packet dir or JSON file (B)")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = ap.parse_args()

    try:
        pa = Path(args.a)
        pb = Path(args.b)
        a, la = load_beacon(pa)
        b, lb = load_beacon(pb)
        result = compare(a, b)
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        return 2

    if args.json:
        print(json.dumps({"a": la, "b": lb, "result": result}, indent=2, sort_keys=True))
    else:
        print(render_card(result, la, lb), end="")

    return 3 if (result.get("diffs") or []) else 0


if __name__ == "__main__":
    raise SystemExit(main())
