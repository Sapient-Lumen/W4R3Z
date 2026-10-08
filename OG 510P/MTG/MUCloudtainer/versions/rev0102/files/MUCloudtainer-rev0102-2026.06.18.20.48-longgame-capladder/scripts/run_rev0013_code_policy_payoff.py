from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.code_policy import code_policy_catalog, make_code_policy_agent, smoke_lint_code_policy
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.payoff import StrategyBundle, aggregate_payoff_rows, load_seed_decks, write_csv
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.public_agents import make_public_agent

REV = "rev0013"


def code_policy_strategy_bundles(seed_decks_path: Path) -> list[StrategyBundle]:
    decks = load_seed_decks(seed_decks_path)
    return [
        StrategyBundle("pub_fjace_bal", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "heuristic", POLICY_LAND_BAND),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "code_jace_lock_rev0013", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_clock_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "code_overlord_clock_rev0013", POLICY_LAND_BAND),
        StrategyBundle("code_force_sixty", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "code_force_conservative_rev0013", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("code_jace_60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
    ]


def build_lint_frames(seed_decks_path: Path):
    decks = load_seed_decks(seed_decks_path)
    samples = []
    for i, deck_name in enumerate(["forty_force_jace_pressure", "forty_overlord_impending", "sixty_counterwall_jace"]):
        state = start_game(decks[deck_name], decks[deck_name], seed=13130 + i, starting_life=20 if i != 2 else 40, record_log=False)
        samples.append(build_decision_frame(state))
    return samples


def main() -> None:
    data = ROOT / "data"
    decks_path = data / "seed_decks.json"
    strategies = code_policy_strategy_bundles(decks_path)
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, base_seed=131300, max_decisions=500)
    games_path = data / "rev0013_code_policy_payoff_games.csv"
    agg_path = data / "rev0013_code_policy_payoff_aggregate.csv"
    standings_path = data / "rev0013_code_policy_payoff_standings.csv"
    write_csv(games_path, rows)
    write_csv(agg_path, aggregate_payoff_rows(rows))
    standings = strategy_standings(rows)
    write_csv(standings_path, standings)

    frames = build_lint_frames(decks_path)
    lint_rows = []
    for item in code_policy_catalog():
        agent = make_code_policy_agent(item["policy_id"])
        ok, errors = smoke_lint_code_policy(agent, frames)
        lint_rows.append({"policy_id": item["policy_id"], "ok": ok, "errors": "; ".join(errors), "summary": item["summary"]})
    write_csv(data / "rev0013_code_policy_lint.csv", lint_rows)

    sample_specs = [(0, 2, 20, 0), (2, 3, 20, 1), (4, 0, 40, 0), (5, 1, 40, 1), (3, 4, 20, 0), (2, 5, 40, 1)]
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
            seed=23130 + t,
            transition_seed=33130 + t,
            agent_seed=43130 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=500,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, data / "rev0013_code_policy_replay_traces.jsonl")
    (data / "rev0013_code_policy_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True))

    gate = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), min_replay_traces=len(replay_results)),
    )
    summary = {
        "revision": REV,
        "games": len(rows),
        "strategies": len(strategies),
        "aggregate_rows": len(list(aggregate_payoff_rows(rows))),
        "standings_rows": len(standings),
        "replay_samples": len(replay_results),
        "promotion_gate": gate.as_dict(),
        "code_policy_catalog": code_policy_catalog(),
        "lint_rows": lint_rows,
        "top_standings": standings[:6],
    }
    (data / "rev0013_code_policy_payoff_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
