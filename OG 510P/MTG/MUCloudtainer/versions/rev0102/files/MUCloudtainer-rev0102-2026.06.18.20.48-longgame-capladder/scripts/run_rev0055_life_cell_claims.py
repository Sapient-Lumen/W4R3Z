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
    cumulative_life_cell_rows,
    focused_life_cell_specs,
    life_cell_agenda_from_matchup_claim,
    life_cell_claim_gate,
    life_cell_dimension_rows,
    life_cell_summary_rows,
)

REV = "rev0055"
CODENAME = "lifecellconfirm-terminaldossier"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
REPS = 32


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
    prev_claims = _read_csv_rows(DATA / "rev0054_matchup_claim_claim_rows.csv")
    prev_life_cells = _read_csv_rows(DATA / "rev0054_matchup_claim_target_life_cells.csv")
    prev_game_rows = _read_csv_rows(DATA / "rev0054_matchup_claim_games.csv")
    agenda = life_cell_agenda_from_matchup_claim(prev_claims, prev_life_cells, top_n_pairs=1, life_totals=(20, 40))
    if not agenda:
        raise SystemExit("no rev0055 life-cell agenda selected")

    specs = focused_life_cell_specs(
        strategies,
        agenda,
        simulator_revision=REV,
        reps=REPS,
        base_seed=5555000,
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
    cumulative_cells = cumulative_life_cell_rows(prev_game_rows, game_rows, agenda)
    cumulative_dimensions = life_cell_dimension_rows([*prev_game_rows, *game_rows], agenda)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=240, min_replay_traces=6, max_truncation_rate=0.0),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=240, max_truncation_rate=0.0)
    cell_gate = life_cell_claim_gate(
        game_rows,
        current_cells,
        cumulative_cells,
        revision=REV,
        cpp_summary=cpp_summary.as_dict(),
        min_rows=240,
        min_new_cell_games=120,
        min_cumulative_cell_games=200,
        require_zero_truncations=True,
    )

    write_csv(DATA / "rev0055_life_cell_agenda.csv", agenda)
    write_csv(DATA / "rev0055_life_cell_games.csv", game_rows)
    write_csv(DATA / "rev0055_life_cell_aggregate.csv", aggregate)
    write_csv(DATA / "rev0055_life_cell_standings.csv", standings)
    write_csv(DATA / "rev0055_life_cell_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0055_life_cell_pairwise.csv", pairwise)
    write_csv(DATA / "rev0055_life_cell_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0055_life_cell_current_cells.csv", current_cells)
    write_csv(DATA / "rev0055_life_cell_current_dimensions.csv", current_dimensions)
    write_csv(DATA / "rev0055_life_cell_cumulative_cells.csv", cumulative_cells)
    write_csv(DATA / "rev0055_life_cell_cumulative_dimensions.csv", cumulative_dimensions)
    write_csv(DATA / "rev0055_life_cell_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0055_life_cell_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0055_life_cell_replay_traces.jsonl")
    (DATA / "rev0055_life_cell_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "based_on": "rev0054 life-sensitive concrete matchup dossier",
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
        "life_cell_claim_gate": cell_gate,
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "current_cell_signal_counts": _label_counts(current_cells, "cell_signal"),
        "cumulative_cell_signal_counts": _label_counts(cumulative_cells, "cell_signal"),
        "current_cells": current_cells,
        "cumulative_cells": cumulative_cells,
        "notes": [
            "rev0055 decomposes the rev0054 life-sensitive matchup claim into separate target/opponent/life cells.",
            "It adds terminal-clean reps for both life-20 and life-40 cells, then reports both current-only and cumulative-with-rev0054 cell evidence.",
            "No gameplay policy is promoted; this is a life-cell claim hygiene and dossier refinement revision.",
        ],
    }
    (DATA / "rev0055_life_cell_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
