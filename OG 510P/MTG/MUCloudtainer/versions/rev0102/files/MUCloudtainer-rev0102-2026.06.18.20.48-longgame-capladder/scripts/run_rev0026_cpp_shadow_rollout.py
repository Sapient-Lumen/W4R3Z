from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import outcome_ranker_probe_bundles
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.public_agents import make_public_agent
from src.muc5.mulligan_ranker import make_mulligan_agent

REV = "rev0026"
DATA = ROOT / "data"


def write_csv(path: Path, rows: list[dict] | tuple[dict, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("")
        return
    fieldnames = sorted({k for r in rows for k in r.keys()})
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    all_strategies = outcome_ranker_probe_bundles(DATA / "seed_decks.json")
    # Keep this smoke panel smaller than the full outcome panel but mixed enough
    # to exercise learned/code/public policies and learned/rule mulligans.
    keep_ids = {
        "outcome_fjace",
        "outcome_counter_wall",
        "mlp_fjace",
        "pub_threat_overlord",
        "pub_counter_wall",
        "code_jace60",
    }
    strategies = [s for s in all_strategies if s.strategy_id in keep_ids]
    specs = strategy_pair_specs(strategies, simulator_revision=REV, reps=1, base_seed=26000, max_decisions=500)
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, transition_rows = finalize_cpp_shadow_rollout(prepared)

    game_rows = list(prepared.game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=20)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=4)

    # Promotion gate still gets explicit replay samples.  The shadow rollout is
    # a C++ parity check, not a substitute for deterministic replay artifacts.
    replay_traces = []
    for spec in specs[:8]:
        trace = record_public_decision_trace(
            spec.deck0,
            spec.deck1,
            make_public_agent(spec.agent0),
            make_public_agent(spec.agent1),
            seed=spec.seed,
            transition_seed=spec.seed,
            agent_seed=spec.seed + 1000003,
            starting_player=spec.starting_player,
            starting_life=spec.starting_life,
            max_decisions=spec.max_decisions,
            mulligan_agents=(make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1)),
        )
        trace["trace_id"] = f"{REV}_{spec.game_id}"
        replay_traces.append(trace)
    replay_results = [replay_public_decision_trace(t).as_dict() for t in replay_traces]

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=100, max_truncation_rate=0.10, min_replay_traces=8),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=100, max_truncation_rate=0.10)

    write_csv(DATA / "rev0026_cpp_shadow_rollout_games.csv", game_rows)
    write_csv(DATA / "rev0026_cpp_shadow_rollout_standings.csv", standings)
    write_csv(DATA / "rev0026_cpp_shadow_rollout_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0026_cpp_shadow_rollout_pairwise.csv", pairwise)
    write_csv(DATA / "rev0026_cpp_shadow_rollout_transitions.csv", [r.as_dict() for r in transition_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0026_cpp_shadow_rollout_replay_traces.jsonl")
    (DATA / "rev0026_cpp_shadow_rollout_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    summary = {
        "revision": REV,
        "strategies": [s.as_dict() for s in strategies],
        "strategy_count": len(strategies),
        "spec_count": len(specs),
        "games": len(game_rows),
        "replay_count": len(replay_results),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "promotion_gate": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "rng_contract": {
            "transition_seed": "seed",
            "agent_seed": "seed+1000003",
            "public_payoff_split_rng": True,
        },
    }
    (DATA / "rev0026_cpp_shadow_rollout_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
