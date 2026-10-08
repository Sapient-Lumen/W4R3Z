from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import mapelite_ranker_variant_bundles

REV = "rev0022"
DATA = ROOT / "data"


def same_deck_pilot_summary(rows):
    scores = defaultdict(list)
    for row in rows:
        scores[(str(row["deck0"]), str(row["agent0"]))].append(float(row["p0_score"]))
        scores[(str(row["deck1"]), str(row["agent1"]))].append(float(row["p1_score"]))
    out = []
    for (deck_name, agent), vals in sorted(scores.items()):
        out.append({"deck_name": deck_name, "agent": agent, "games": len(vals), "mean_score_draw_half": sum(vals) / len(vals) if vals else 0.0})
    out.sort(key=lambda r: (r["deck_name"], -r["mean_score_draw_half"], r["agent"]))
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = mapelite_ranker_variant_bundles(DATA / "rev0014_map_elites_archive.csv", limit_cells=3)
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2322000, max_decisions=540)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_games.csv", rows)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_aggregate.csv", aggregate_payoff_rows(rows))
    standings = strategy_standings(rows)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_standings.csv", standings)
    same_deck = same_deck_pilot_summary(rows)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_same_deck_pilots.csv", same_deck)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_pairwise.csv", pairwise)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_stat_standings.csv", stat_stand)
    stat_gate = audit_statistical_gate(rows, stat_stand, pairwise, min_raw_rows=len(rows), max_truncation_rate=0.10)

    sample_specs = [(0, 1, 20, 0), (2, 3, 20, 1), (4, 5, 40, 0), (6, 7, 40, 1), (8, 9, 20, 0), (10, 11, 40, 1)]
    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(sample_specs):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=3322000 + t,
            transition_seed=4322000 + t,
            agent_seed=5322000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=540,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_mapelite_variant_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_mapelite_ranker_variants_replay_traces.jsonl")
    (DATA / f"{REV}_mapelite_ranker_variants_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")

    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / f"{REV}_mapelite_ranker_variants_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / f"{REV}_mapelite_ranker_variants_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )

    summary = {
        "revision": REV,
        "strategy_count": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(aggregate_payoff_rows(rows)),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "top_standings": standings[:8],
        "same_deck_pilot_summary": same_deck[:12],
    }
    (DATA / f"{REV}_mapelite_ranker_variants_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
