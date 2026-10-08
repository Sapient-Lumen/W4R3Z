from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.cpp_trace import finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import terminal_clean_yield_ranker_bundles
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows, terminal_clean_by_strategy
from src.muc5.terminal_life_cell_claim import (
    annotate_life_cell_rows,
    focused_life_cell_specs,
    life_cell_dimension_rows,
    life_cell_summary_rows,
)
from src.muc5.terminal_life_cell_replicate import (
    dimension_stability_rows,
    holdout_cell_rows,
    life_cell_replication_agenda,
    life_cell_replication_gate,
    replication_comparison_rows,
)

REV = "rev0056"
CODENAME = "lifecellreplicate-holdoutgate"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
REPS = 24


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


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

    if not eval_specs:
        return [], []
    sample_indices = [0, 1, 2, 3, max(0, len(eval_specs)//2 - 1), len(eval_specs)//2, len(eval_specs)-2, len(eval_specs)-1]
    traces = []
    results = []
    seen = set()
    for idx in sample_indices[: count + 4]:
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
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
        if len(traces) >= count:
            break
    return traces, results


def _label_counts(rows: list[dict[str, object]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        label = str(row.get(key, ""))
        out[label] = out.get(label, 0) + 1
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = terminal_clean_yield_ranker_bundles(DATA / "seed_decks.json")
    prior_cumulative_cells = _read_csv_rows(DATA / "rev0055_life_cell_cumulative_cells.csv")
    agenda = life_cell_replication_agenda(prior_cumulative_cells, top_n_cells=2)
    if not agenda:
        raise SystemExit("no rev0056 life-cell replication agenda selected")

    specs = focused_life_cell_specs(
        strategies,
        agenda,
        simulator_revision=REV,
        reps=REPS,
        base_seed=5656000,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)

    annotated = annotate_life_cell_rows(list(prepared.game_rows), agenda)
    game_rows = mark_terminal_clean_rows(
        annotated,
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    terminal_summary = summarize_terminal_clean_rows(game_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=80)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=20)
    by_strategy = terminal_clean_by_strategy(game_rows)

    current_cells = life_cell_summary_rows(game_rows, agenda)
    current_dimensions = life_cell_dimension_rows(game_rows, agenda)
    holdout_cells = holdout_cell_rows(current_cells)
    comparison_rows = replication_comparison_rows(prior_cumulative_cells, holdout_cells)
    dimension_stability = dimension_stability_rows(current_dimensions)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=160, min_replay_traces=6, max_truncation_rate=0.0),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=160, max_truncation_rate=0.0)
    replication_gate = life_cell_replication_gate(
        game_rows,
        holdout_cells,
        comparison_rows,
        revision=REV,
        cpp_summary=cpp_summary.as_dict(),
        replay_results=replay_results,
        min_raw_rows=160,
        min_holdout_games_per_cell=96,
        require_zero_truncations=True,
    )

    write_csv(DATA / "rev0056_life_cell_replication_agenda.csv", agenda)
    write_csv(DATA / "rev0056_life_cell_replication_games.csv", game_rows)
    write_csv(DATA / "rev0056_life_cell_replication_aggregate.csv", aggregate)
    write_csv(DATA / "rev0056_life_cell_replication_standings.csv", standings)
    write_csv(DATA / "rev0056_life_cell_replication_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0056_life_cell_replication_pairwise.csv", pairwise)
    write_csv(DATA / "rev0056_life_cell_replication_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0056_life_cell_replication_current_cells.csv", current_cells)
    write_csv(DATA / "rev0056_life_cell_replication_holdout_cells.csv", holdout_cells)
    write_csv(DATA / "rev0056_life_cell_replication_comparison.csv", comparison_rows)
    write_csv(DATA / "rev0056_life_cell_replication_dimensions.csv", current_dimensions)
    write_csv(DATA / "rev0056_life_cell_replication_dimension_stability.csv", dimension_stability)
    write_csv(DATA / "rev0056_life_cell_replication_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0056_life_cell_replication_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0056_life_cell_replication_replay_traces.jsonl")
    (DATA / "rev0056_life_cell_replication_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "based_on": "rev0055 cumulative life-cell dossier candidates",
        "strategies": len(strategies),
        "agenda_cells": len(agenda),
        "agenda_rows": agenda,
        "reps": REPS,
        "games": len(game_rows),
        "aggregate_rows": len(aggregate),
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "life_cell_replication_gate": replication_gate,
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "holdout_label_counts": _label_counts(holdout_cells, "holdout_label"),
        "replication_label_counts": _label_counts(comparison_rows, "replication_label"),
        "dimension_stability_label_counts": _label_counts(dimension_stability, "dimension_label"),
        "holdout_cells": holdout_cells,
        "replication_comparison": comparison_rows,
        "notes": [
            "rev0056 runs a seed-disjoint holdout replication block for the rev0055 life-cell claim candidates.",
            "The holdout evidence is compared to prior cumulative evidence; combined evidence is reported but cannot rescue a failed holdout by itself.",
            "No gameplay policy is promoted; this is a claim-hygiene and independent-replication revision.",
        ],
    }
    (DATA / "rev0056_life_cell_replication_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
