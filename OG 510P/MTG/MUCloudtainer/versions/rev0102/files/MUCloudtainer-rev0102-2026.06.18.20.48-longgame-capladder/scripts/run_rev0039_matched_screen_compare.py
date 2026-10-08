from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_screen_compare import collect_matched_screen_comparison
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import outcome_ranker_probe_bundles, disagreement_counterfactual_action_ranker_bundles

REV = "rev0039"
DATA = ROOT / "data"


def _method_pivot(method_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not method_rows:
        return []
    df = pd.DataFrame(method_rows)
    rows = []
    for sid, g in df.groupby("situation_id"):
        methods = {str(r["method"]): r for _, r in g.iterrows()}
        screen = methods.get("screened_vote_budget")
        uns = methods.get("unscreened_budget")
        if screen is None or uns is None:
            continue
        rows.append({
            "situation_id": sid,
            "action_count": int(screen["action_count"]),
            "union_branched_action_count": int(screen["union_branched_action_count"]),
            "union_best_actions": screen["union_best_actions"],
            "union_best_margin": float(screen["union_best_margin"]),
            "label_confidence_proxy": float(screen["label_confidence_proxy"]),
            "screened_method_best": screen["method_best_actions"],
            "unscreened_method_best": uns["method_best_actions"],
            "screened_best_score": float(screen["method_best_mean_actor_score"]),
            "unscreened_best_score": float(uns["method_best_mean_actor_score"]),
            "screened_minus_unscreened_best_score": float(screen["method_best_mean_actor_score"]) - float(uns["method_best_mean_actor_score"]),
            "screened_hits_union_best": int(screen["method_hits_union_best"]),
            "unscreened_hits_union_best": int(uns["method_hits_union_best"]),
            "screen_vote_hits_union_best": int(screen["screen_vote_hits_union_best"]),
            "behavior_chosen_hits_union_best": int(screen["behavior_chosen_hits_union_best"]),
            "screened_lost_value_to_union_best": float(screen["method_lost_value_to_union_best"]),
            "unscreened_lost_value_to_union_best": float(uns["method_lost_value_to_union_best"]),
        })
    return rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    base = outcome_ranker_probe_bundles(DATA / "seed_decks.json")
    # Include newer counterfactual policies only as behavior-game sources; the
    # audit does not promote a new policy.  Keeping a mixed behavior set tends to
    # expose more disagreement frames than a single baseline pair.
    try:
        extra = disagreement_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        extra = ()
    behavior_strategies = tuple(base[:4]) + tuple(extra[:4])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=3903900,
        max_decisions=420,
        limit_games=14,
    )
    candidates, method_rows, branch_rows, screen_rows, transitions, summary = collect_matched_screen_comparison(
        specs,
        revision=REV,
        max_situations=14,
        max_actions_per_frame=4,
        branch_action_budget=3,
        branch_rollouts_per_action=2,
        branch_max_decisions=320,
    )
    pivot = _method_pivot(method_rows)
    write_csv(DATA / "rev0039_matched_screen_candidates.csv", candidates)
    write_csv(DATA / "rev0039_matched_screen_methods.csv", method_rows)
    write_csv(DATA / "rev0039_matched_screen_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0039_matched_screen_votes.csv", screen_rows)
    write_csv(DATA / "rev0039_matched_screen_cpp_transitions.csv", transitions)
    write_csv(DATA / "rev0039_matched_screen_situation_pivot.csv", pivot)

    method_df = pd.DataFrame(method_rows)
    pivot_df = pd.DataFrame(pivot)
    branch_df = pd.DataFrame(branch_rows)
    label_audit = {
        "candidate_rows": int(len(candidates)),
        "method_rows": int(len(method_rows)),
        "branch_rows": int(len(branch_rows)),
        "screen_vote_rows": int(len(screen_rows)),
        "transition_rows": int(len(transitions)),
        "pivot_rows": int(len(pivot)),
        "decisive_situations": int((pivot_df["union_best_margin"].astype(float) > 1e-9).sum()) if not pivot_df.empty else 0,
        "confident_situations_ge_0_50": int((pivot_df["label_confidence_proxy"].astype(float) >= 0.50).sum()) if not pivot_df.empty else 0,
        "screened_better_situations": int((pivot_df["screened_minus_unscreened_best_score"].astype(float) > 1e-9).sum()) if not pivot_df.empty else 0,
        "unscreened_better_situations": int((pivot_df["screened_minus_unscreened_best_score"].astype(float) < -1e-9).sum()) if not pivot_df.empty else 0,
        "tied_situations": int((pivot_df["screened_minus_unscreened_best_score"].astype(float).abs() <= 1e-9).sum()) if not pivot_df.empty else 0,
        "mean_screened_minus_unscreened_best_score": float(pivot_df["screened_minus_unscreened_best_score"].astype(float).mean()) if not pivot_df.empty else 0.0,
        "mean_branch_decisions": float(branch_df["branch_decisions"].astype(float).mean()) if not branch_df.empty else 0.0,
        "method_counts": method_df["method"].value_counts().to_dict() if not method_df.empty else {},
    }
    out = {
        "revision": REV,
        "codename": "screenmatch-labelaudit",
        "counterfactual_summary": summary.as_dict(),
        "label_audit": label_audit,
        "notes": [
            "This is a label-budget audit, not a new promoted policy.",
            "Both methods consume the same branch rollout outcomes for each sampled public situation.",
            "screened_vote_budget prioritizes public-policy screen votes when legal menus exceed the branch budget.",
            "unscreened_budget uses the older behavior-chosen-plus-diversity budget selector without vote priority.",
        ],
    }
    (DATA / "rev0039_matched_screen_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
