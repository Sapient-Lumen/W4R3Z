from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_yield_collect import collect_yield_screen_online_counterfactuals
from src.muc5.action_yield_screen import (
    load_historical_yield_rows,
    load_yield_screen_model,
    save_yield_screen_model,
    train_yield_screen_model,
)
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.ranker_policy import save_linear_ranker_model, train_linear_action_ranker_from_candidate_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import (
    adaptive_counterfactual_action_ranker_bundles,
    budgeted_counterfactual_action_ranker_bundles,
    disagreement_counterfactual_action_ranker_bundles,
    outcome_ranker_probe_bundles,
    yield_counterfactual_action_ranker_bundles,
)

REV = "rev0047"
CODENAME = "yieldonline-rankerpolicy"
DATA = ROOT / "data"
MODEL_PATH = DATA / "rev0047_counterfactual_action_ranker_model.json"


def _yield_history_paths() -> list[Path]:
    return [
        DATA / "rev0033_action_counterfactual_candidates.csv",
        DATA / "rev0034_action_counterfactual_candidates.csv",
        DATA / "rev0035_action_counterfactual_candidates.csv",
        DATA / "rev0036_adaptive_action_counterfactual_candidates.csv",
        DATA / "rev0038_disagreement_action_counterfactual_candidates.csv",
        DATA / "rev0043_hard_online_racing_candidates.csv",
        DATA / "rev0044_margin_online_racing_candidates.csv",
        DATA / "rev0045_margin_match_candidates.csv",
        DATA / "rev0046_yield_match_candidates.csv",
    ]


def _action_history_paths() -> list[Path]:
    return [
        DATA / "rev0034_action_counterfactual_candidates.csv",
        DATA / "rev0035_action_counterfactual_candidates.csv",
        DATA / "rev0036_adaptive_action_counterfactual_candidates.csv",
        DATA / "rev0038_disagreement_action_counterfactual_candidates.csv",
        DATA / "rev0043_hard_online_racing_candidates.csv",
        DATA / "rev0044_margin_online_racing_candidates.csv",
        DATA / "rev0045_margin_match_candidates.csv",
        DATA / "rev0046_yield_match_candidates.csv",
        DATA / "rev0047_yield_online_candidates.csv",
    ]


def _load_or_train_yield_model():
    path = DATA / "rev0046_yield_screen_model.json"
    if path.exists():
        return load_yield_screen_model(path)
    rows = load_historical_yield_rows(_yield_history_paths())
    model, holdout = train_yield_screen_model(
        rows,
        revision="rev0046_rebuilt_for_rev0047",
        source_files=[p.name for p in _yield_history_paths() if p.exists()],
        seed=46046,
        holdout_fraction=0.30,
        l2=0.35,
    )
    save_yield_screen_model(model, path)
    pd.DataFrame(holdout).to_csv(DATA / "rev0047_rebuilt_yield_model_holdout_eval.csv", index=False)
    return model


def _load_action_candidate_rows(paths: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen = set()
    for path in paths:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "mean_actor_score" not in df.columns or "situation_id" not in df.columns:
            continue
        for row in df.to_dict(orient="records"):
            sid = str(row.get("situation_id", ""))
            idx = str(row.get("action_index", ""))
            key = (path.name, sid, idx)
            if key in seen:
                continue
            seen.add(key)
            row["source_candidate_file"] = path.name
            rows.append(row)
    return rows


def _label_audit(candidate_rows: list[dict[str, object]]) -> dict[str, object]:
    df = pd.DataFrame(candidate_rows)
    if df.empty:
        return {"candidate_rows": 0}
    situations = df.groupby("situation_id")
    margins = situations["situation_best_margin"].first().astype(float)
    conf = situations["label_confidence_proxy"].first().astype(float)
    action_counts = situations["action_count"].first().astype(int)
    branched = situations["branched_action_count"].first().astype(int)
    chosen_best = situations["behavior_chosen_is_best"].max().astype(int)
    decisive = margins > 1e-9
    rollouts = situations.apply(lambda g: int(g["branch_rollouts"].astype(int).sum()))
    return {
        "candidate_rows": int(len(df)),
        "situations": int(len(situations)),
        "decisive_situations": int(decisive.sum()),
        "tie_situations": int((~decisive).sum()),
        "mean_margin": float(margins.mean()) if len(margins) else 0.0,
        "median_margin": float(margins.median()) if len(margins) else 0.0,
        "mean_label_confidence_proxy": float(conf.mean()) if len(conf) else 0.0,
        "behavior_chosen_best_rate": float(chosen_best.mean()) if len(chosen_best) else 0.0,
        "mean_action_count": float(action_counts.mean()) if len(action_counts) else 0.0,
        "mean_branched_action_count": float(branched.mean()) if len(branched) else 0.0,
        "branch_rollouts": int(rollouts.sum()) if len(rollouts) else 0,
        "decisive_per_100_rollouts": float(100.0 * decisive.sum() / max(1, int(rollouts.sum()))) if len(rollouts) else 0.0,
    }


def _record_replay_samples(eval_specs, count: int = 8):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mull(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    sample_indices = [0, 1, 2, 3, max(0, len(eval_specs)//2 - 1), len(eval_specs)//2, len(eval_specs)-2, len(eval_specs)-1]
    replay_traces = []
    replay_results = []
    seen = set()
    for idx in sample_indices[:count + 4]:
        if idx in seen or idx < 0 or idx >= len(eval_specs):
            continue
        seen.add(idx)
        spec = eval_specs[idx]
        trace = record_public_decision_trace(
            spec.deck0,
            spec.deck1,
            agent(spec.agent0),
            agent(spec.agent1),
            seed=int(spec.seed),
            transition_seed=int(spec.seed),
            agent_seed=int(spec.seed) + 1000003,
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            max_decisions=int(spec.max_decisions),
            mulligan_agents=(mull(spec.mulligan0), mull(spec.mulligan1)),
        )
        replay_traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
        if len(replay_traces) >= count:
            break
    return replay_traces, replay_results


def main() -> None:
    DATA.mkdir(exist_ok=True)
    yield_model = _load_or_train_yield_model()

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
    behavior_strategies = tuple(base[:5]) + tuple(dis[:3]) + tuple(bud[:2]) + tuple(ada[:3])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=4704700,
        max_decisions=440,
        limit_games=32,
    )

    cached_collection = (DATA / "rev0047_yield_online_candidates.csv").exists() and (DATA / "rev0047_yield_online_cpp_transitions.csv").exists()
    if cached_collection:
        pool_rows = pd.read_csv(DATA / "rev0047_yield_online_pool.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_pool.csv").exists() else []
        yield_rank_rows = pd.read_csv(DATA / "rev0047_yield_online_rank.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_rank.csv").exists() else []
        selected_rows = pd.read_csv(DATA / "rev0047_yield_online_selected.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_selected.csv").exists() else []
        candidate_rows = pd.read_csv(DATA / "rev0047_yield_online_candidates.csv").to_dict(orient="records")
        branch_rows = pd.read_csv(DATA / "rev0047_yield_online_branch_games.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_branch_games.csv").exists() else []
        allocation_rows = pd.read_csv(DATA / "rev0047_yield_online_allocations.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_allocations.csv").exists() else []
        vote_rows = pd.read_csv(DATA / "rev0047_yield_online_votes.csv").to_dict(orient="records") if (DATA / "rev0047_yield_online_votes.csv").exists() else []
        cpp_rows = pd.read_csv(DATA / "rev0047_yield_online_cpp_transitions.csv").to_dict(orient="records")
        label_audit = _label_audit(candidate_rows)
        collection_summary_dict = {
            "revision": REV,
            "cached_collection": True,
            "pool_rows": len(pool_rows),
            "yield_selected": len(selected_rows),
            "branch_games": len(branch_rows),
            "branch_truncations": int(sum(1 for r in branch_rows if str(r.get("winner")) == "None")),
            "cpp_checked_transitions": int(sum(1 for r in cpp_rows if str(r.get("supported_by_cpp", "True")) in {"True", "true", "1"})),
            "cpp_skipped_transitions": int(sum(1 for r in cpp_rows if str(r.get("supported_by_cpp", "True")) in {"False", "false", "0"})),
            "cpp_mismatches": int(sum(1 for r in cpp_rows if str(r.get("cpp_match", "True")) in {"False", "false", "0"})),
            "decisive_situations": int(label_audit.get("decisive_situations", 0)),
            "decisive_per_100_rollouts": float(label_audit.get("decisive_per_100_rollouts", 0.0)),
        }
    else:
        (
            pool_rows,
            yield_rank_rows,
            selected_rows,
            candidate_rows,
            branch_rows,
            allocation_rows,
            vote_rows,
            cpp_rows,
            collection_summary,
        ) = collect_yield_screen_online_counterfactuals(
            specs,
            yield_model=yield_model,
            revision=REV,
            min_unique_screen_votes=1,
            max_behavior_frames=240,
            candidate_pool_situations=48,
            selected_situations=12,
            high_action_threshold=5,
            max_actions_per_frame=3,
            branch_action_budget=5,
            base_rollouts_per_action=1,
            max_extra_rollouts_per_situation=4,
            adaptive_stop_margin=0.42,
            adaptive_target_confidence=0.58,
            branch_max_decisions=380,
            ranker_revision="rev0034",
            max_per_behavior_game=2,
            budget_rng_seed=47047,
        )
        collection_summary_dict = collection_summary.as_dict()
        write_csv(DATA / "rev0047_yield_online_pool.csv", pool_rows)
        write_csv(DATA / "rev0047_yield_online_rank.csv", yield_rank_rows)
        write_csv(DATA / "rev0047_yield_online_selected.csv", selected_rows)
        write_csv(DATA / "rev0047_yield_online_candidates.csv", candidate_rows)
        write_csv(DATA / "rev0047_yield_online_branch_games.csv", branch_rows)
        write_csv(DATA / "rev0047_yield_online_allocations.csv", allocation_rows)
        write_csv(DATA / "rev0047_yield_online_votes.csv", vote_rows)
        write_csv(DATA / "rev0047_yield_online_cpp_transitions.csv", cpp_rows)
        label_audit = _label_audit(candidate_rows)

    all_training_rows = _load_action_candidate_rows(_action_history_paths())
    model, train_summary, coef_rows, pred_rows = train_linear_action_ranker_from_candidate_rows(
        all_training_rows,
        model_id="counterfactual_linear_ranker_rev0047",
        source_revision=REV,
        seed=47047,
        train_fraction=0.72,
        ridge_alpha=0.70,
        sample_weight_mode="confidence_subset_vote",
    )
    save_linear_ranker_model(model, MODEL_PATH)
    write_csv(DATA / "rev0047_counterfactual_action_ranker_coefficients.csv", coef_rows)
    write_csv(DATA / "rev0047_counterfactual_action_ranker_predictions.csv", pred_rows)

    strategies = yield_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")[:6]
    eval_specs = strategy_pair_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=4747000,
        max_decisions=380,
    )
    cached_eval = (DATA / "rev0047_yield_ranker_games.csv").exists() and (DATA / "rev0047_yield_ranker_cpp_transitions.csv").exists()
    if cached_eval:
        game_rows = pd.read_csv(DATA / "rev0047_yield_ranker_games.csv").to_dict(orient="records")
        cpp_transition_cached = pd.read_csv(DATA / "rev0047_yield_ranker_cpp_transitions.csv").to_dict(orient="records")
        replay_path = DATA / "rev0047_yield_ranker_replay_results.json"
        replay_results = json.loads(replay_path.read_text()) if replay_path.exists() else []
        aggregate = aggregate_payoff_rows(game_rows)
        standings = strategy_standings(game_rows)
        stat_standings = statistical_standings(game_rows, min_games_for_claim=24)
        pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=4)
        cpp_supported_events = int(sum(1 for r in cpp_transition_cached if str(r.get("supported_by_cpp", "True")) in {"True", "true", "1"}))
        cpp_skipped_events = int(sum(1 for r in cpp_transition_cached if str(r.get("supported_by_cpp", "True")) in {"False", "false", "0"}))
        cpp_mismatches = int(sum(1 for r in cpp_transition_cached if str(r.get("cpp_match", "True")) in {"False", "false", "0"}))
    else:
        prepared = prepare_cpp_shadow_rollout(eval_specs, revision=REV)
        cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
        game_rows = list(prepared.game_rows)
        aggregate = aggregate_payoff_rows(game_rows)
        standings = strategy_standings(game_rows)
        stat_standings = statistical_standings(game_rows, min_games_for_claim=24)
        pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=4)
        replay_traces, replay_results = _record_replay_samples(eval_specs, count=8)
        cpp_supported_events = int(cpp_summary.supported_events)
        cpp_skipped_events = int(cpp_summary.skipped_events)
        cpp_mismatches = int(cpp_summary.mismatches)
        write_csv(DATA / "rev0047_yield_ranker_games.csv", game_rows)
        write_csv(DATA / "rev0047_yield_ranker_aggregate.csv", aggregate)
        write_csv(DATA / "rev0047_yield_ranker_standings.csv", standings)
        write_csv(DATA / "rev0047_yield_ranker_stat_standings.csv", stat_standings)
        write_csv(DATA / "rev0047_yield_ranker_pairwise.csv", pairwise)
        write_csv(DATA / "rev0047_yield_ranker_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
        write_trace_jsonl(replay_traces, DATA / "rev0047_yield_ranker_replay_traces.jsonl")
        (DATA / "rev0047_yield_ranker_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=120, min_replay_traces=6, max_truncation_rate=0.25),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=120, max_truncation_rate=0.25)
    write_csv(DATA / "rev0047_yield_ranker_aggregate.csv", aggregate)
    write_csv(DATA / "rev0047_yield_ranker_standings.csv", standings)
    write_csv(DATA / "rev0047_yield_ranker_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0047_yield_ranker_pairwise.csv", pairwise)

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "yield_model_revision": yield_model.revision,
        "collection_summary": collection_summary_dict,
        "label_audit": label_audit,
        "training_rows_total": len(all_training_rows),
        "training_summary": train_summary,
        "payoff_summary": {
            "strategies": len(strategies),
            "games": len(game_rows),
            "aggregate_rows": len(aggregate),
            "truncations": int(sum(1 for r in game_rows if str(r.get("is_truncation", "0")) in {"1", "True", "true"})),
            "cpp_shadow_events": int(cpp_supported_events),
            "cpp_skipped_events": int(cpp_skipped_events),
            "cpp_mismatches": int(cpp_mismatches),
            "replay_samples": len(replay_results),
            "promotion_passed": bool(promotion.passed),
            "statistical_gate_passed": bool(stat_gate.passed),
        },
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "notes": [
            "rev0047 turns the rev0046 label-yield screen into a yield-only online branch-label collector.",
            "A generic linear counterfactual-ranker training helper was added to ranker_policy.py to reduce copy-pasted training blocks.",
            "The rev0047 ranker is trained on the accumulated audited action-counterfactual label corpus plus the new yield-screened rows.",
            "The payoff panel is smoke-scale; no strategic MUC claim should be made from it yet.",
        ],
    }
    (DATA / "rev0047_yield_online_counterfactual_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
