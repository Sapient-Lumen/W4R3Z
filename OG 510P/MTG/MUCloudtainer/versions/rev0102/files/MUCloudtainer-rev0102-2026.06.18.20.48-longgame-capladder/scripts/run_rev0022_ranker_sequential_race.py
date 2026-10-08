from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.sequential_race import race_candidates
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import ranker_race_benchmarks, ranker_race_candidates

REV = "rev0022"
DATA = ROOT / "data"


def _trace_specs(candidates, opponents):
    # Touch the main policy families without requiring a full trace corpus.
    pairs = [
        (candidates[0], opponents[0], 20, 0),
        (candidates[1], opponents[1], 20, 1),
        (candidates[2], opponents[2], 40, 0),
        (candidates[3], opponents[3], 40, 1),
        (candidates[4], opponents[4], 20, 0),
        (candidates[5], opponents[5], 40, 1),
        (opponents[0], candidates[2], 20, 1),
        (opponents[3], candidates[1], 40, 0),
    ]
    return pairs


def main() -> None:
    DATA.mkdir(exist_ok=True)
    candidates = ranker_race_candidates(DATA / "seed_decks.json")
    opponents = ranker_race_benchmarks(DATA / "seed_decks.json")

    rows, stages, candidate_standings = race_candidates(
        candidates,
        opponents,
        simulator_revision=REV,
        stage_reps=(1, 2),
        base_seed=2222000,
        max_decisions=540,
        eliminate_after_games=48,
        slack=0.015,
    )
    write_csv(DATA / f"{REV}_ranker_race_games.csv", rows)
    write_csv(DATA / f"{REV}_ranker_race_aggregate.csv", aggregate_payoff_rows(rows))
    write_csv(DATA / f"{REV}_ranker_race_standings.csv", strategy_standings(rows))
    write_csv(DATA / f"{REV}_ranker_race_candidate_standings.csv", candidate_standings)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=8)
    write_csv(DATA / f"{REV}_ranker_race_pairwise.csv", pairwise)
    stages_payload = [s.as_dict() for s in stages]
    (DATA / f"{REV}_ranker_race_stages.json").write_text(json.dumps(stages_payload, indent=2, sort_keys=True), encoding="utf-8")

    stat_stand = statistical_standings(rows, min_games_for_claim=48)
    write_csv(DATA / f"{REV}_ranker_race_stat_standings.csv", stat_stand)
    stat_gate = audit_statistical_gate(rows, stat_stand, pairwise, min_raw_rows=len(rows), max_truncation_rate=0.10)

    traces = []
    replay_results = []
    for t, (left, right, life, starting_player) in enumerate(_trace_specs(candidates, opponents)):
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=3222000 + t,
            transition_seed=4222000 + t,
            agent_seed=5222000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=540,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_race_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_ranker_race_replay_traces.jsonl")
    (DATA / f"{REV}_ranker_race_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")

    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / f"{REV}_ranker_race_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / f"{REV}_ranker_race_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )

    candidate_ids = {c.strategy_id for c in candidates}
    ranker_ids = {c.strategy_id for c in candidates if "ranker" in c.agent_name or c.agent_name.startswith("linear_ranker")}
    summary = {
        "revision": REV,
        "candidate_count": len(candidates),
        "opponent_count": len(opponents),
        "raw_games": len(rows),
        "stage_count": len(stages),
        "stages": stages_payload,
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "candidate_ids": sorted(candidate_ids),
        "ranker_candidate_ids": sorted(ranker_ids),
        "top_candidate_standings": candidate_standings[:6],
        "top_stat_standings": stat_stand[:8],
    }
    (DATA / f"{REV}_ranker_race_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
