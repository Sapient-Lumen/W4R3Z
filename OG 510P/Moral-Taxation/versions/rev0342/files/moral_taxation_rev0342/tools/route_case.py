#!/usr/bin/env python3
"""Deterministic candidate router for moral-taxation golden cases.

The router deliberately reads the fact packet (`golden-cases.json`) and the live
route graph (`cube-index.json`) only. It does not read case contracts or expected
route IDs when scoring. The case-contract audit compares this output to the
contracts.

Rev0320 adds a facts-only candidate pass. The combined pass may use case axes
as normalized facts, but every case also has to be recoverable from the written
scenario text alone within a wider candidate window. This guards against cases
that pass only because their tags were hand-shaped to the expected answer.
"""
import argparse
import json
import pathlib
import re
from typing import Any, Dict, List, Tuple

AXIS_WEIGHTS = {
    "anti_pattern": 7.0,
    "base": 5.0,
    "review_trigger": 5.0,
    "moral_operation": 5.0,
    "proof_posture": 4.0,
    "burden_mechanic": 4.0,
    "remedy_type": 4.0,
    "delivery_channel": 3.0,
    "instrument": 3.0,
    "rights_affected": 3.0,
    "evidence_state": 3.0,
    "stage": 2.0,
    "floor_risk": 2.0,
    "incidence": 2.0,
    "market_structure": 2.0,
    "legal_status": 2.0,
    "source_freshness": 2.0,
    "proceeds_route": 2.0,
    "subject": 1.0,
    "scale": 1.0,
    "severity": 1.0,
    "confidence": 1.0,
    "review_cadence": 1.0,
}

STOP_WORDS = {
    "and", "the", "for", "with", "from", "into", "should", "not", "turned",
    "routing", "ladder", "standard", "rules", "tax", "taxation", "public",
    "basic", "access", "that", "has", "are", "but", "while", "route", "case",
    "want", "wants", "new", "old", "one", "two", "per", "its", "this",
    "without", "after", "before", "under", "through", "over", "by", "of", "a",
    "an", "to", "in", "on", "or", "is", "be", "as", "no", "their", "them",
    "it", "must", "will", "when", "then", "than", "only", "same", "rather",
    "than", "using", "used", "uses", "use", "give", "given", "make", "makes",
}


def tokens(value: Any) -> set[str]:
    return {
        tok
        for tok in re.findall(r"[a-z0-9]+", str(value).lower())
        if len(tok) > 2 and tok not in STOP_WORDS
    }


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def route_text(root: pathlib.Path, route: Dict[str, Any]) -> str:
    parts: List[str] = [route.get("id", ""), route.get("family", ""), route.get("path", "")]
    for axis, values in route.get("axes", {}).items():
        parts.append(axis)
        parts.extend(str(v) for v in values)
    route_path = root / route.get("path", "")
    if route_path.exists():
        # Enough prose to reward distinctive route vocabulary without turning the
        # router into a slow document summarizer.
        parts.append(route_path.read_text(encoding="utf-8")[:4000])
    return " ".join(parts)


def case_fact_text(case: Dict[str, Any]) -> str:
    return " ".join([case.get("title", ""), str(case.get("facts", ""))])


def case_axis_text(case: Dict[str, Any]) -> str:
    axes = case.get("cube_axes_raw", {}) or {}
    return " ".join(str(value) for values in axes.values() for value in values)


def score_route(
    case: Dict[str, Any],
    route: Dict[str, Any],
    route_tokens: set[str],
    *,
    facts_only: bool = False,
) -> Tuple[float, float, float, Dict[str, List[str]], List[str]]:
    axes = case.get("cube_axes_raw", {}) or {}
    axis_score = 0.0
    axis_matches: Dict[str, List[str]] = {}
    route_axes = route.get("axes", {})
    if not facts_only:
        for axis, values in axes.items():
            overlap = sorted(set(values) & set(route_axes.get(axis, [])))
            if overlap:
                axis_matches[axis] = overlap
                axis_score += AXIS_WEIGHTS.get(axis, 1.0) * len(overlap)

    # The fact signal excludes cube_axes_raw. This keeps the second runtime pass
    # from simply re-reading the expected normalized tags.
    fact_tokens = tokens(case_fact_text(case))
    text_hits = sorted(fact_tokens & route_tokens)
    id_hits = sorted(fact_tokens & tokens(route.get("id", "")))
    fact_score = 0.5 * len(text_hits) + 1.0 * len(id_hits)
    score = fact_score if facts_only else axis_score + fact_score
    return score, axis_score, fact_score, axis_matches, text_hits[:24]


def prepare_routes(root: pathlib.Path, routes: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], set[str]]]:
    """Read route memo text once per run, not once per case."""
    return [(route, tokens(route_text(root, route))) for route in routes]


def rank_case(
    case: Dict[str, Any],
    prepared_routes: List[Tuple[Dict[str, Any], set[str]]],
    candidate_limit: int,
    *,
    facts_only: bool = False,
) -> Dict[str, Any]:
    ranked: List[Dict[str, Any]] = []
    for route, rtoks in prepared_routes:
        score, axis_score, fact_score, axis_matches, text_hits = score_route(case, route, rtoks, facts_only=facts_only)
        if score <= 0:
            continue
        ranked.append({
            "route_id": route.get("id"),
            "family": route.get("family"),
            "score": round(score, 3),
            "axis_score": round(axis_score, 3),
            "fact_score": round(fact_score, 3),
            "axis_matches": axis_matches,
            "text_hits": text_hits,
        })
    ranked.sort(key=lambda item: (-item["score"], item["route_id"]))
    candidates = ranked[:candidate_limit]
    primary = candidates[0]["route_id"] if candidates else None
    return {
        "case_id": case.get("case_id"),
        "title": case.get("title"),
        "primary_route_id": primary,
        "candidate_route_ids": [item["route_id"] for item in candidates],
        "candidate_limit": candidate_limit,
        "ranked_candidates": candidates,
        "mode": "facts_only" if facts_only else "facts_and_axes",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a golden case through the live cube route graph.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Route one case id, e.g. GC-001")
    parser.add_argument("--all", action="store_true", help="Route all golden cases")
    parser.add_argument("--candidate-limit", type=int, default=5, help="Number of combined candidates to return")
    parser.add_argument("--facts-only-candidate-limit", type=int, default=8, help="Number of facts-only candidates to return")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    cube = load_json(root / "cube-index.json")
    golden = load_json(root / "docs/00-meta/golden-cases.json")
    routes = cube.get("route_records", [])
    cases = golden.get("cases", [])
    if args.case_id:
        cases = [case for case in cases if case.get("case_id") == args.case_id]
        if not cases:
            raise SystemExit(f"unknown case id: {args.case_id}")
    elif not args.all:
        raise SystemExit("provide --case-id or --all")

    prepared_routes = prepare_routes(root, routes)
    results = []
    for case in cases:
        combined = rank_case(case, prepared_routes, args.candidate_limit, facts_only=False)
        facts = rank_case(case, prepared_routes, args.facts_only_candidate_limit, facts_only=True)
        combined.update({
            "facts_only_primary_route_id": facts["primary_route_id"],
            "facts_only_candidate_route_ids": facts["candidate_route_ids"],
            "facts_only_candidate_limit": args.facts_only_candidate_limit,
            "facts_only_ranked_candidates": facts["ranked_candidates"],
            "runtime_status": "facts_and_axes_candidate_router_invoked",
        })
        results.append(combined)

    payload = {
        "kind": "case_runtime_routing_results",
        "runtime_status": "facts_and_axes_candidate_router_invoked",
        "candidate_limit": args.candidate_limit,
        "facts_only_candidate_limit": args.facts_only_candidate_limit,
        "case_count": len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for result in results:
            print(
                f"{result['case_id']}: primary={result['primary_route_id']} "
                f"candidates={', '.join(result['candidate_route_ids'])} "
                f"facts_only={', '.join(result['facts_only_candidate_route_ids'])}"
            )


if __name__ == "__main__":
    main()
