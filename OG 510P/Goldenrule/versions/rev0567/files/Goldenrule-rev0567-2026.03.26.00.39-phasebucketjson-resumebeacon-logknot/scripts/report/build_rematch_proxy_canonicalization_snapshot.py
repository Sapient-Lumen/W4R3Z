#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_STEM = ROOT / "artifacts" / "reports" / "rematch_proxy_canonicalization_snapshot_20260306"
EXTORTION_PATH = ROOT / "examples" / "strategies" / "extortion_chi3.json"
GEN_TFT_PATH = ROOT / "examples" / "strategies" / "mem1_generous_tft.json"
PROXY_REPORT_PATH = ROOT / "artifacts" / "reports" / "partner_choice_proxy_snapshot_20260306.json"
MAX_MATCH_ROUNDS = 50
DETERMINISTIC_CODES = ["".join(code) for code in itertools.product("CDE", repeat=5)]
STATE_INDEX = {
    None: 0,
    ("C", "C"): 1,
    ("C", "D"): 2,
    ("D", "C"): 3,
    ("D", "D"): 4,
}
STATE_NAMES = ["p0", "p_cc", "p_cd", "p_dc", "p_dd"]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _opp_support(spec: dict, prev: tuple[str, str] | None) -> tuple[str, ...]:
    if prev is None:
        p = float(spec["p0"])
    else:
        key = {
            ("C", "C"): "p_cc",
            ("C", "D"): "p_cd",
            ("D", "C"): "p_dc",
            ("D", "D"): "p_dd",
        }[prev]
        p = float(spec[key])
    support = []
    if p > 0.0:
        support.append("C")
    if p < 1.0:
        support.append("D")
    return tuple(support)


def _focal_action(code: str, prev: tuple[str, str] | None) -> str:
    return code[STATE_INDEX[prev]]


def _consulted_indices(code: str, opponent: dict) -> set[int]:
    consulted = {0}
    queue: deque[tuple[tuple[str, str] | None, int]] = deque([(None, 0)])
    seen = {None}
    while queue:
        prev, depth = queue.popleft()
        if depth >= MAX_MATCH_ROUNDS:
            continue
        action = _focal_action(code, prev)
        if action == "E":
            continue
        opp_prev = None if prev is None else (prev[1], prev[0])
        for opp_action in _opp_support(opponent, opp_prev):
            next_prev = (action, opp_action)
            consulted.add(STATE_INDEX[next_prev])
            if next_prev not in seen:
                seen.add(next_prev)
                queue.append((next_prev, depth + 1))
    return consulted


def _canonical_pattern(code: str, opponents: list[dict]) -> str:
    consulted: set[int] = set()
    for opponent in opponents:
        consulted |= _consulted_indices(code, opponent)
    return "".join(ch if idx in consulted else "*" for idx, ch in enumerate(code))


def _family_note(pattern: str) -> str:
    if pattern == "E****":
        return "Immediate-exit family: once the first move is Exit, every later parameter is unreachable."
    if pattern == "CE***":
        return "Pool-specific collapse: both current proxy opponents start with C, so a policy that exits after CC never consults later states."
    if pattern == "CCE**":
        return "Leave-after-break family: after first-round CC, any non-CC signal triggers exit before p_dc or p_dd can matter."
    if pattern == "CCC**":
        return "Always-stay-on-C family within the current pool: only cooperative-prefix decisions are reachable under the proxy opponents."
    if pattern == "D**E*":
        return "Defect-first then leave-after-DC family: the current proxy pool starts with C, so the first consulted repair/exit state is p_dc."
    return "Support-distinct family under the current proxy opponent pool."


def _round_obj(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_obj(v) for k, v in obj.items()}
    return obj


def _render_markdown(report: dict) -> str:
    lines = [
        "# Rematch-Proxy Canonicalization Snapshot (2026-03-06)",
        "",
        "Method:",
        f"- analyzed all `{report['counts']['raw_codes']}` deterministic `memory_one_exit` codes against the current proxy opponent pool",
        "- canonicalized each code by the decision parameters that are support-reachable before exit across `extortion_chi3_v1` and `mem1_generous_tft_v1`",
        f"- match horizon for reachability = `{report['world']['max_match_rounds']}` rounds",
        "- this is a structural support analysis, not a Monte Carlo ranking pass",
        "",
        "Main finding:",
        f"- Raw search space `{report['counts']['raw_codes']}` collapses to `{report['counts']['canonical_families']}` support-distinct families in the current rematch proxy.",
        f"- That is a `{report['counts']['reduction_percent']:.1f}%` shrink in raw deterministic search volume before scoring.",
        f"- The largest collapse is immediate exit: `{report['largest_families'][0]['pattern']}` covers `{report['largest_families'][0]['size']}` raw codes.",
        f"- The compact handoff baseline family `{report['handoff']['canonical_pattern']}` covers `{report['handoff']['family_size']}` raw codes, so search should canonicalize it rather than rediscovering nine aliases.",
        "",
        "Largest canonical families:",
    ]
    for entry in report['largest_families']:
        lines.append(f"- `{entry['pattern']}` — size `{entry['size']}` — representative `{entry['representative']}` — {entry['note']}")
    lines.extend([
        "",
        "Top candidate patterns already present in the proxy report:",
    ])
    for entry in report['candidate_patterns']:
        lines.append(
            f"- `{entry['code']}` -> `{entry['canonical_pattern']}`; proxy mean `{entry['proxy_mean_overall']:.6f}`, proxy min `{entry['proxy_min_overall']:.6f}`"
        )
    lines.extend([
        "",
        "Interpretation:",
        "- The previous `CCE**` hint was real but incomplete: the current proxy opponent pool compresses the full deterministic space much more aggressively than one family alone suggests.",
        "- This compression is pool-specific because both current proxy opponents start with cooperation. If a future endogenous world adds suspicious or noisy entrants, some wildcard states may become reachable again.",
        "- The implementor consequence is concrete: perform genotype-to-phenotype canonicalization before optimization in rematch-enabled worlds, or the search will waste budget on aliases.",
        "",
        "Immediate implementor implication:",
        "- The next engine-supported rematch world should expose a canonicalization hook or post-processor for unreachable exit-tail parameters, with `CCEEE` kept as the human-readable representative of the `CCE**` family.",
    ])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    extortion = _read_json(EXTORTION_PATH)
    generous_tft = _read_json(GEN_TFT_PATH)
    proxy_report = _read_json(PROXY_REPORT_PATH)
    opponents = [extortion, generous_tft]

    families: dict[str, list[str]] = defaultdict(list)
    for code in DETERMINISTIC_CODES:
        families[_canonical_pattern(code, opponents)].append(code)

    largest = []
    for pattern, members in sorted(families.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]:
        largest.append(
            {
                "pattern": pattern,
                "size": len(members),
                "representative": sorted(members)[0],
                "note": _family_note(pattern),
                "members_sample": sorted(members)[:5],
            }
        )

    top_codes: list[str] = []
    for section in ("top_balanced_nice_candidates", "top_proxy_candidates"):
        for entry in proxy_report.get(section, []):
            code = entry["code"]
            if code not in top_codes:
                top_codes.append(code)

    candidate_patterns = []
    for code in top_codes:
        metric_source = next(
            entry
            for section in ("top_balanced_nice_candidates", "top_proxy_candidates")
            for entry in proxy_report.get(section, [])
            if entry["code"] == code
        )
        candidate_patterns.append(
            {
                "code": code,
                "canonical_pattern": _canonical_pattern(code, opponents),
                "proxy_mean_overall": float(metric_source["proxy_mean_overall"]),
                "proxy_min_overall": float(metric_source["proxy_min_overall"]),
            }
        )

    cce_family = sorted(families["CCE**"])
    report = {
        "world": {
            "kind": "partner_choice_proxy_canonicalization",
            "description": "Support reachability collapse for deterministic memory_one_exit strategies in the current focal leave/rematch proxy.",
            "opponents": [extortion["id"], generous_tft["id"]],
            "max_match_rounds": MAX_MATCH_ROUNDS,
        },
        "summary": "The current proxy opponent pool compresses 243 deterministic memory_one_exit codes into 63 support-distinct families, so rematch-enabled search should canonicalize unreachable exit-tail parameters before optimization.",
        "counts": {
            "raw_codes": len(DETERMINISTIC_CODES),
            "canonical_families": len(families),
            "reduction_percent": 100.0 * (1.0 - (len(families) / len(DETERMINISTIC_CODES))),
            "compression_ratio": len(DETERMINISTIC_CODES) / len(families),
        },
        "largest_families": largest,
        "handoff": {
            "canonical_pattern": "CCE**",
            "family_size": len(cce_family),
            "family_members": cce_family,
            "recommended_representative": "CCEEE",
            "recommended_strategy_id": "mem1_exit_after_break_v1",
        },
        "candidate_patterns": candidate_patterns,
        "parameter_order": STATE_NAMES,
        "notes": [
            "This is a support-reachability collapse under the current proxy pool, not a universal quotient over all possible opponents.",
            "Both current proxy opponents start with cooperation, which is why families like CE*** collapse more than they would in a pool that contains suspicious starters.",
            "The result is still directly useful for search budgeting and result deduplication in the current tranche.",
        ],
    }

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(_round_obj(report), indent=2) + "\n", encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(_round_obj(report)), encoding='utf-8')
    print(f"wrote {REPORT_STEM.with_suffix('.json')}")
    print(f"wrote {REPORT_STEM.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
