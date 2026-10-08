from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_segment import build_nochoice_segment_specs, run_nochoice_segment_cpp_panel_batched
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import mapelite_mulligan_variant_bundles

REV = "rev0032"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = mapelite_mulligan_variant_bundles(DATA / "rev0014_map_elites_archive.csv", limit_cells=2)
    specs = build_nochoice_segment_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=3200000,
        max_decisions=520,
        limit_pairs=96,
    )
    game_rows, segment_rows, segment_summary = run_nochoice_segment_cpp_panel_batched(specs, revision=REV)

    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=32)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=4)

    # Replay a small deterministic sample for promotion-gate provenance.  This
    # intentionally samples across the same segment-shadow specs but uses the
    # public trace/replay path rather than trusting the segment checker alone.
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

    replay_traces = []
    replay_results = []
    sample_indices = [0, 1, 2, 3, max(0, len(specs)//2 - 1), len(specs)//2, len(specs)-2, len(specs)-1]
    seen = set()
    for idx in sample_indices:
        if idx in seen or idx < 0 or idx >= len(specs):
            continue
        seen.add(idx)
        spec = specs[idx]
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

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=96, min_replay_traces=6, max_truncation_rate=0.20),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=96, max_truncation_rate=0.20)

    write_csv(DATA / "rev0032_segment_shadow_games.csv", game_rows)
    write_csv(DATA / "rev0032_segment_shadow_aggregate.csv", aggregate)
    write_csv(DATA / "rev0032_segment_shadow_standings.csv", standings)
    write_csv(DATA / "rev0032_segment_shadow_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0032_segment_shadow_pairwise.csv", pairwise)
    write_csv(DATA / "rev0032_segment_shadow_segments.csv", segment_rows)
    write_trace_jsonl(replay_traces, DATA / "rev0032_segment_shadow_replay_traces.jsonl")
    (DATA / "rev0032_segment_shadow_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    # Segment histograms and same-deck comparison diagnostics.
    hist = {}
    for row in segment_rows:
        key = str(row.get("length"))
        hist[key] = hist.get(key, 0) + 1
    by_deck = {}
    for row in standings:
        # Strategy ids begin with mevXX; this preserves the construction shell.
        strategy = str(row["strategy"])
        shell = strategy.split("_", 1)[0]
        by_deck.setdefault(shell, []).append(row)
    same_deck = []
    for shell, rows in sorted(by_deck.items()):
        for r in sorted(rows, key=lambda x: float(x["mean_score_draw_half"]), reverse=True):
            rr = dict(r)
            rr["mapelite_shell"] = shell
            same_deck.append(rr)
    write_csv(DATA / "rev0032_segment_shadow_same_deck.csv", same_deck)

    payload = {
        "revision": REV,
        "codename": "segmentshadow-maprace",
        "strategy_count": len(strategies),
        "spec_count": len(specs),
        "games": len(game_rows),
        "aggregate_rows": len(aggregate),
        "segments": len(segment_rows),
        "segment_summary": segment_summary.as_dict(),
        "segment_length_histogram": dict(sorted(hist.items(), key=lambda kv: int(kv[0]))),
        "promotion_gate": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "cpp_segment_mismatches": segment_summary.cpp_segment_mismatches,
        "cpp_skipped_events": segment_summary.skipped_events,
        "truncations": segment_summary.truncations,
        "batch_cpp_invocations": 1,
        "notes": [
            "Python remains semantic authority; C++ checks no-choice forced segments in one batched finalization pass.",
            "MAP-Elites construction shells are crossed with public/code/learned gameplay pilots and learned mulligan policies.",
            "Smoke-scale standings are diagnostic, not MUC theory claims.",
        ],
    }
    (DATA / "rev0032_segment_shadow_summary.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
