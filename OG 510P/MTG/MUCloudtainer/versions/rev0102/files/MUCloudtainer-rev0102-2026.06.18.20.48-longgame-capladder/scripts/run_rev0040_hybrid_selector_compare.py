from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_hybrid_compare import collect_matched_hybrid_comparison
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import outcome_ranker_probe_bundles, disagreement_counterfactual_action_ranker_bundles

REV = "rev0040"
DATA = ROOT / "data"


def _method_pivot(method_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not method_rows:
        return []
    df = pd.DataFrame(method_rows)
    rows: list[dict[str, object]] = []
    for sid, g in df.groupby("situation_id"):
        methods = {str(r["method"]): r for _, r in g.iterrows()}
        required = ("unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker")
        if any(m not in methods for m in required):
            continue
        h = methods["hybrid_vote_diverse_ranker"]
        u = methods["unscreened_budget"]
        s = methods["screened_vote_budget"]
        hv = float(h["method_best_mean_actor_score"])
        uv = float(u["method_best_mean_actor_score"])
        sv = float(s["method_best_mean_actor_score"])
        rows.append({
            "situation_id": sid,
            "action_count": int(h["action_count"]),
            "union_branched_action_count": int(h["union_branched_action_count"]),
            "union_best_actions": h["union_best_actions"],
            "union_best_margin": float(h["union_best_margin"]),
            "label_confidence_proxy": float(h["label_confidence_proxy"]),
            "hybrid_method_best": h["method_best_actions"],
            "unscreened_method_best": u["method_best_actions"],
            "screened_method_best": s["method_best_actions"],
            "hybrid_best_score": hv,
            "unscreened_best_score": uv,
            "screened_best_score": sv,
            "hybrid_minus_unscreened_best_score": hv - uv,
            "hybrid_minus_screened_best_score": hv - sv,
            "hybrid_hits_union_best": int(h["method_hits_union_best"]),
            "unscreened_hits_union_best": int(u["method_hits_union_best"]),
            "screened_hits_union_best": int(s["method_hits_union_best"]),
            "screen_vote_hits_union_best": int(h["screen_vote_hits_union_best"]),
            "behavior_chosen_hits_union_best": int(h["behavior_chosen_hits_union_best"]),
            "hybrid_lost_value_to_union_best": float(h["method_lost_value_to_union_best"]),
            "unscreened_lost_value_to_union_best": float(u["method_lost_value_to_union_best"]),
            "screened_lost_value_to_union_best": float(s["method_lost_value_to_union_best"]),
        })
    return rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    base = outcome_ranker_probe_bundles(DATA / "seed_decks.json")
    try:
        extra = disagreement_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        extra = ()
    behavior_strategies = tuple(base[:4]) + tuple(extra[:4])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=4004000,
        max_decisions=420,
        limit_games=16,
    )
    candidates, method_rows, branch_rows, screen_rows, transitions, summary = collect_matched_hybrid_comparison(
        specs,
        revision=REV,
        max_situations=16,
        max_actions_per_frame=4,
        branch_action_budget=4,
        branch_rollouts_per_action=2,
        branch_max_decisions=320,
        ranker_revision="rev0034",
    )
    pivot = _method_pivot(method_rows)
    write_csv(DATA / "rev0040_hybrid_selector_candidates.csv", candidates)
    write_csv(DATA / "rev0040_hybrid_selector_methods.csv", method_rows)
    write_csv(DATA / "rev0040_hybrid_selector_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0040_hybrid_selector_votes.csv", screen_rows)
    write_csv(DATA / "rev0040_hybrid_selector_cpp_transitions.csv", transitions)
    write_csv(DATA / "rev0040_hybrid_selector_situation_pivot.csv", pivot)

    pivot_df = pd.DataFrame(pivot)
    method_df = pd.DataFrame(method_rows)
    branch_df = pd.DataFrame(branch_rows)
    if not pivot_df.empty:
        decisive = pivot_df[pivot_df["union_best_margin"].astype(float) > 1e-9]
    else:
        decisive = pivot_df
    selector_audit = {
        "candidate_rows": int(len(candidates)),
        "method_rows": int(len(method_rows)),
        "branch_rows": int(len(branch_rows)),
        "screen_vote_rows": int(len(screen_rows)),
        "transition_rows": int(len(transitions)),
        "pivot_rows": int(len(pivot)),
        "decisive_situations": int(len(decisive)),
        "confident_situations_ge_0_50": int((pivot_df["label_confidence_proxy"].astype(float) >= 0.50).sum()) if not pivot_df.empty else 0,
        "hybrid_better_than_unscreened": int((pivot_df["hybrid_minus_unscreened_best_score"].astype(float) > 1e-9).sum()) if not pivot_df.empty else 0,
        "hybrid_worse_than_unscreened": int((pivot_df["hybrid_minus_unscreened_best_score"].astype(float) < -1e-9).sum()) if not pivot_df.empty else 0,
        "hybrid_better_than_screened": int((pivot_df["hybrid_minus_screened_best_score"].astype(float) > 1e-9).sum()) if not pivot_df.empty else 0,
        "hybrid_worse_than_screened": int((pivot_df["hybrid_minus_screened_best_score"].astype(float) < -1e-9).sum()) if not pivot_df.empty else 0,
        "mean_branch_decisions": float(branch_df["branch_decisions"].astype(float).mean()) if not branch_df.empty else 0.0,
        "method_counts": method_df["method"].value_counts().to_dict() if not method_df.empty else {},
    }
    out = {
        "revision": REV,
        "codename": "hybridselector-decisivegate",
        "counterfactual_summary": summary.as_dict(),
        "selector_audit": selector_audit,
        "notes": [
            "This is a selector/label-budget audit, not a promoted policy.",
            "unscreened_budget, screened_vote_budget, and hybrid_vote_diverse_ranker consume the same branch rollout outcomes per situation.",
            "The hybrid selector keeps behavior, limited public-screen votes, diversity representatives, and a cheap rev0034 counterfactual-ranker prior when available.",
            "A method hit means it kept at least one union-best action among the actions actually branched by the union of methods.",
        ],
    }
    (DATA / "rev0040_hybrid_selector_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
