#!/usr/bin/env python3
"""tools/surface_anomaly_rollup.py

Bounded rollup for publishable surface anomaly-note codes.

Why:
- The archive encourages small, publishable monitoring artifacts (docs/201, docs/210).
- Notes fields can carry stable anomaly codes (docs/SURFACE_ANOMALY_CODES.md).
- Operators often need a tight answer to: "What anomalies are showing up across these inputs?"

Design constraints:
- stdlib-only
- hashes / codes only (never prints bodies)
- bounded output by default

Inputs:
- positional PATH(s) may be:
  - JSON files (payloads or EvidenceEnvelopes)
  - packet directories (containing envelopes/ + objects/)

Exit codes:
- 0: ran successfully
- 2: load/parse error
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


KIND_LIVENESS = "hfv.coverage.liveness_beacon"
KIND_PARITY = "hfv.public.surface_parity_snapshot"

_NOTE_CODE_RE = re.compile(r"^[a-z0-9_]{3,64}$")


def _norm_str(v: Any) -> str:
    return str(v or "").strip()


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


def _find_packet_envelopes(packet_dir: Path) -> List[Tuple[Path, Dict[str, Any]]]:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return []
    out: List[Tuple[Path, Dict[str, Any]]] = []
    for p in sorted(env_dir.glob("*.json")):
        try:
            obj = _load_json(p)
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append((p, obj))
    return out


def _note_code(notes: Any) -> str:
    s = _norm_str(notes)
    if not s:
        return ""
    head = s.split(":", 1)[0].split(None, 1)[0].strip()
    if _NOTE_CODE_RE.fullmatch(head):
        return head
    return ""


@dataclass
class Hit:
    kind: str
    code: str
    surface: str  # liveness: surface; parity: subject.surface_kind (best-effort)
    where: str


def _extract_hits_from_payload(payload: Dict[str, Any], where: str) -> Tuple[List[Hit], int]:
    """Return (hits, observation_count)."""

    obs = payload.get("observations")
    if not isinstance(obs, list):
        return [], 0

    # Heuristic kind detection when not provided.
    kind = ""
    if obs and isinstance(obs[0], dict) and "surface" in obs[0]:
        kind = KIND_LIVENESS
    elif obs and isinstance(obs[0], dict) and "channel_id" in obs[0]:
        kind = KIND_PARITY

    # For parity snapshots, prefer subject.surface_kind for grouping.
    surface_group = ""
    subj = payload.get("subject")
    if isinstance(subj, dict):
        surface_group = _norm_str(subj.get("surface_kind"))

    hits: List[Hit] = []
    for o in obs:
        if not isinstance(o, dict):
            continue
        code = _note_code(o.get("notes"))
        if not code:
            continue

        surface = ""
        if kind == KIND_LIVENESS:
            surface = _norm_str(o.get("surface"))
        elif kind == KIND_PARITY:
            surface = surface_group
        else:
            # Unknown-ish payload; pick the most plausible field.
            surface = _norm_str(o.get("surface")) or surface_group

        hits.append(Hit(kind=kind or "unknown", code=code, surface=surface, where=where))

    return hits, len([o for o in obs if isinstance(o, dict)])


def _scan_path(path: Path) -> Tuple[List[Hit], int]:
    """Return (hits, observation_count)."""

    hits: List[Hit] = []
    obs_count = 0

    if path.is_dir():
        # Treat as a packet dir if it contains envelopes/.
        for env_path, env in _find_packet_envelopes(path):
            k = _norm_str(env.get("kind"))
            if k not in {KIND_LIVENESS, KIND_PARITY}:
                continue
            payload = _load_payload_from_envelope(env, path / "objects")
            h, n = _extract_hits_from_payload(payload, where=str(env_path.relative_to(path)))
            hits.extend(h)
            obs_count += n
        return hits, obs_count

    # File.
    obj = _load_json(path)
    if _is_envelope(obj):
        env = obj
        payload = _load_payload_from_envelope(env, path.parent)
        h, n = _extract_hits_from_payload(payload, where=str(path))
        return h, n

    if not isinstance(obj, dict):
        return [], 0
    h, n = _extract_hits_from_payload(obj, where=str(path))
    return h, n


def _load_known_codes() -> set[str]:
    try:
        from tools.surface_anomaly_codes import CODES
    except Exception:
        from surface_anomaly_codes import CODES
    return set(CODES.keys())


def rollup(hits: List[Hit], obs_count: int) -> Dict[str, Any]:
    known = _load_known_codes()

    by_code: Dict[str, Dict[str, Any]] = {}
    unknown = 0
    for h in hits:
        code = h.code
        if code not in known:
            unknown += 1
            code = "unknown_surface_anomaly_code"

        ent = by_code.setdefault(
            code,
            {
                "code": code,
                "count": 0,
                "kinds": {},
                "surfaces": {},
            },
        )
        ent["count"] += 1
        ent["kinds"][h.kind] = int(ent["kinds"].get(h.kind, 0)) + 1
        if h.surface:
            ent["surfaces"][h.surface] = int(ent["surfaces"].get(h.surface, 0)) + 1

    codes_sorted = sorted(by_code.values(), key=lambda e: (-int(e.get("count") or 0), str(e.get("code") or "")))
    return {
        "summary": {
            "observations_total": obs_count,
            "note_codes_total": len(hits),
            "distinct_codes": len(by_code),
            "unknown_codes": unknown,
        },
        "codes": codes_sorted,
    }


def render_card(result: Dict[str, Any], inputs: List[str], max_codes: int = 12) -> str:
    s = result.get("summary") or {}
    lines: List[str] = []
    lines.append("Surface anomaly rollup")
    if inputs:
        lines.append("inputs:")
        for i in inputs[:8]:
            lines.append(f"  - {i}")
        if len(inputs) > 8:
            lines.append(f"  ... ({len(inputs) - 8} more)")

    lines.append(
        f"observations: total={int(s.get('observations_total') or 0)} with_code={int(s.get('note_codes_total') or 0)} "
        f"distinct_codes={int(s.get('distinct_codes') or 0)} unknown={int(s.get('unknown_codes') or 0)}"
    )

    codes = result.get("codes") or []
    if not codes:
        lines.append("codes: none")
        return "\n".join(lines) + "\n"

    lines.append("codes:")
    for e in codes[:max_codes]:
        code = str(e.get("code") or "")
        count = int(e.get("count") or 0)
        kinds = e.get("kinds") or {}
        surfaces = e.get("surfaces") or {}
        # Tight one-liner: counts + top surface.
        top_surface = ""
        if isinstance(surfaces, dict) and surfaces:
            top_surface = sorted(surfaces.items(), key=lambda kv: (-int(kv[1]), kv[0]))[0][0]
        kind_hint = ""
        if isinstance(kinds, dict) and kinds:
            # show the most common kind.
            k0 = sorted(kinds.items(), key=lambda kv: (-int(kv[1]), kv[0]))[0]
            kind_hint = f"{k0[0]}:{int(k0[1])}"
        tail = ", ".join([x for x in [kind_hint, (f"top_surface={top_surface}" if top_surface else "")] if x])
        lines.append(f"  - {code}: {count}" + (f" ({tail})" if tail else ""))

    if len(codes) > max_codes:
        lines.append(f"  ... ({len(codes) - max_codes} more)")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Roll up surface anomaly-note codes from packets or JSON payloads")
    ap.add_argument("paths", nargs="+", help="packet dirs or JSON files")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--max-codes", type=int, default=12, help="max codes to render in card output")
    args = ap.parse_args()

    inputs: List[str] = [str(p) for p in args.paths]
    all_hits: List[Hit] = []
    obs_total = 0

    try:
        for s in args.paths:
            p = Path(s)
            h, n = _scan_path(p)
            all_hits.extend(h)
            obs_total += n
        result = rollup(all_hits, obs_total)
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        return 2

    if args.json:
        print(json.dumps({"inputs": inputs, "result": result}, indent=2, sort_keys=True))
    else:
        print(render_card(result, inputs, max_codes=int(args.max_codes)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
