from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_hard_frame import collect_hard_frame_hybrid_comparison
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import (
    outcome_ranker_probe_bundles,
    disagreement_counterfactual_action_ranker_bundles,
    budgeted_counterfactual_action_ranker_bundles,
    adaptive_counterfactual_action_ranker_bundles,
)

REV = "rev0041"
DATA = ROOT / "data"


def _method_pivot(method_rows: list[dict[str, object]], selected_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not method_rows:
        return []
    df = pd.DataFrame(method_rows)
    selected = {str(r["situation_id"]): r for r in selected_rows}
    rows: list[dict[str, object]] = []
    for sid, g in df.groupby("situation_id"):
        methods = {str(r["method"]): r for _, r in g.iterrows()}
        required = ("unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker")
        if any(m not in methods for m in required):
            continue
        h = methods["hybrid_vote_diverse_ranker"]
        u = methods["unscreened_budget"]
        s = methods["screened_vote_budget"]
        sr = selected.get(str(sid), {})
        hv = float(h["method_best_mean_actor_score"])
        uv = float(u["method_best_mean_actor_score"])
        sv = float(s["method_best_mean_actor_score"])
        rows.append({
            "situation_id": sid,
            "action_count": int(h["action_count"]),
            "union_branched_action_count": int(h["union_branched_action_count"]),
            "screen_score": float(sr.get("screen_score", h.get("screen_score", 0.0))),
            "screen_reason": str(sr.get("screen_reason", h.get("screen_reason", ""))),
            "screen_unique_votes": int(sr.get("screen_unique_votes", 0)),
            "screen_vote_entropy_proxy": float(sr.get("screen_vote_entropy_proxy", 0.0)),
            "profile_spread": float(sr.get("profile_spread", 0.0)),
            "ranker_spread": float(sr.get("ranker_spread", 0.0)),
            "high_action_bonus": float(sr.get("high_action_bonus", 0.0)),
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
        dis = disagreement_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        dis = ()
    try:
        bud = budgeted_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        bud = ()
    try:
        ada = adaptive_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        ada = ()
    behavior_strategies = tuple(base[:4]) + tuple(dis[:3]) + tuple(bud[:2]) + tuple(ada[:2])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=4104100,
        max_decisions=420,
        limit_games=22,
    )
    selected, candidates, method_rows, branch_rows, screen_rows, transitions, summary = collect_hard_frame_hybrid_comparison(
        specs,
        revision=REV,
        max_behavior_frames=180,
        max_situations=12,
        high_action_threshold=5,
        max_actions_per_frame=3,
        branch_action_budget=5,
        branch_rollouts_per_action=2,
        branch_max_decisions=320,
        ranker_revision="rev0034",
        max_per_behavior_game=2,
    )
    pivot = _method_pivot(method_rows, selected)
    write_csv(DATA / "rev0041_hard_frame_selected.csv", selected)
    write_csv(DATA / "rev0041_hard_frame_candidates.csv", candidates)
    write_csv(DATA / "rev0041_hard_frame_methods.csv", method_rows)
    write_csv(DATA / "rev0041_hard_frame_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0041_hard_frame_votes.csv", screen_rows)
    write_csv(DATA / "rev0041_hard_frame_cpp_transitions.csv", transitions)
    write_csv(DATA / "rev0041_hard_frame_pivot.csv", pivot)

    pivot_df = pd.DataFrame(pivot)
    selected_df = pd.DataFrame(selected)
    branch_df = pd.DataFrame(branch_rows)
    method_df = pd.DataFrame(method_rows)
    decisive = pivot_df[pivot_df["union_best_margin"].astype(float) > 1e-9] if not pivot_df.empty else pivot_df
    audit = {
        "selected_rows": int(len(selected)),
        "candidate_rows": int(len(candidates)),
        "method_rows": int(len(method_rows)),
        "branch_rows": int(len(branch_rows)),
        "screen_vote_rows": int(len(screen_rows)),
        "transition_rows": int(len(transitions)),
        "pivot_rows": int(len(pivot)),
        "high_action_selected": int((selected_df["action_count"].astype(int) >= 5).sum()) if not selected_df.empty else 0,
        "mean_selected_action_count": float(selected_df["action_count"].astype(float).mean()) if not selected_df.empty else 0.0,
        "mean_selected_screen_score": float(selected_df["screen_score"].astype(float).mean()) if not selected_df.empty else 0.0,
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
        "codename": "hardframe-hybridlabelaudit",
        "hard_frame_summary": summary.as_dict(),
        "selector_audit": audit,
        "notes": [
            "This is a label-selector audit, not a promoted gameplay policy.",
            "Frames are queued by public-only hard-frame signals: action count, public-policy disagreement, profile-score spread, and previous-ranker spread.",
            "Branch labels are still generated by the offline referee from true state copies; gameplay agents never receive the hidden state.",
            "The goal is to find positions where branch budget binds and where selector mistakes are visible.",
        ],
    }
    (DATA / "rev0041_hard_frame_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
