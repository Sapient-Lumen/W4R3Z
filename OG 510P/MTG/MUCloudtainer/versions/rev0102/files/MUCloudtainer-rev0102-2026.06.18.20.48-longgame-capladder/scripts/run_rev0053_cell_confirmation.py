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
from src.muc5.terminal_matchup import annotate_life_matchup_rows, focused_life_matchup_specs, life_flip_retest_rows, target_life_cell_rows
from src.muc5.terminal_cell_confirm import cell_confluence_agenda_from_retest, cell_confirmation_gate, cell_confirmation_rows

REV = "rev0053"
CODENAME = "cellconfirm-confluencegate"
DATA = ROOT / "data"
TERMINAL_MAX_DECISIONS = 900
REPS = 12
TOP_N = 3


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
        traces.append(trace)
        results.append(replay_public_decision_trace(trace).as_dict())
        if len(traces) >= count:
            break
    return traces, results


def main() -> None:
    DATA.mkdir(exist_ok=True)
    strategies = terminal_clean_yield_ranker_bundles(DATA / "seed_decks.json")
    rev0052_cells = _read_csv_rows(DATA / "rev0052_life_flip_target_life_cells.csv")
    rev0052_flips = _read_csv_rows(DATA / "rev0052_life_flip_retest.csv")
    claim_rows = _read_csv_rows(DATA / "rev0050_terminal_meta_claim_ledger.csv") + _read_csv_rows(DATA / "rev0051_deep_claim_target_summary.csv") + _read_csv_rows(DATA / "rev0051_deep_claim_claim_ledger.csv")

    agenda = cell_confluence_agenda_from_retest(
        rev0052_cells,
        rev0052_flips,
        claim_rows,
        top_n=TOP_N,
        life_low=20,
        life_high=40,
    )
    if not agenda:
        raise SystemExit("no rev0053 cell-confirmation agenda selected")

    specs = focused_life_matchup_specs(
        strategies,
        agenda,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=REPS,
        base_seed=5353000,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )

    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)

    annotated = annotate_life_matchup_rows(list(prepared.game_rows), agenda)
    game_rows = mark_terminal_clean_rows(
        annotated,
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    terminal_summary = summarize_terminal_clean_rows(game_rows, revision=REV, max_decisions=TERMINAL_MAX_DECISIONS)
    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=48)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=12)
    by_strategy = terminal_clean_by_strategy(game_rows)
    target_cells = target_life_cell_rows(game_rows, agenda, life_totals=(20, 40))
    confirmation = cell_confirmation_rows(target_cells, agenda, life_low=20, life_high=40)
    flip_retest = life_flip_retest_rows(target_cells, agenda, life_low=20, life_high=40)

    replay_traces, replay_results = _record_replay_samples(specs, count=8)
    prepared_trace = prepare_public_traces_for_cpp(replay_traces, revision=REV)
    cpp_trace_summary, cpp_trace_rows = finalize_cpp_trace_batch(prepared_trace)

    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=250, min_replay_traces=6, max_truncation_rate=0.0),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=250, max_truncation_rate=0.0)
    confirm_gate = cell_confirmation_gate(
        game_rows,
        agenda,
        confirmation,
        revision=REV,
        cpp_summary=cpp_summary.as_dict(),
        min_rows=250,
        min_cell_games=48,
    )

    write_csv(DATA / "rev0053_cell_confirm_agenda.csv", agenda)
    write_csv(DATA / "rev0053_cell_confirm_games.csv", game_rows)
    write_csv(DATA / "rev0053_cell_confirm_aggregate.csv", aggregate)
    write_csv(DATA / "rev0053_cell_confirm_standings.csv", standings)
    write_csv(DATA / "rev0053_cell_confirm_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0053_cell_confirm_pairwise.csv", pairwise)
    write_csv(DATA / "rev0053_cell_confirm_by_strategy.csv", by_strategy)
    write_csv(DATA / "rev0053_cell_confirm_target_life_cells.csv", target_cells)
    write_csv(DATA / "rev0053_cell_confirm_confirmation.csv", confirmation)
    write_csv(DATA / "rev0053_cell_confirm_life_retest.csv", flip_retest)
    write_csv(DATA / "rev0053_cell_confirm_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_csv(DATA / "rev0053_cell_confirm_cpp_trace_rows.csv", [r.as_dict() for r in cpp_trace_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0053_cell_confirm_replay_traces.jsonl")
    (DATA / "rev0053_cell_confirm_replay_results.json").write_text(json.dumps(replay_results, indent=2))

    labels: dict[str, int] = {}
    for row in confirmation:
        labels[str(row.get("confirmation_label"))] = labels.get(str(row.get("confirmation_label")), 0) + 1

    summary = {
        "revision": REV,
        "codename": CODENAME,
        "based_on": "rev0052 concrete target/life cell retests plus rev0050/rev0051 claim context",
        "strategies": len(strategies),
        "agenda_cells": len(agenda),
        "agenda_rows": agenda,
        "reps": REPS,
        "games": len(game_rows),
        "aggregate_rows": len(aggregate),
        "target_life_cell_rows": len(target_cells),
        "confirmation_rows": len(confirmation),
        "max_decisions": TERMINAL_MAX_DECISIONS,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "promotion": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cell_confirmation_gate": confirm_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "cpp_trace_summary": cpp_trace_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(sum(1 for r in replay_results if r.get("passed") is True)),
        "confirmation_label_counts": labels,
        "top_confirmation_rows": confirmation[:10],
        "life_retest_rows": flip_retest,
        "notes": [
            "rev0053 treats rev0052 target/life cells as a concrete-cell agenda, not as proof.",
            "The selection prioritizes cells that still looked favored or high-value after life-split softening, then retests them terminal-clean with both target seats, both starting-player positions, both life totals, replay samples, and C++ shadow checks.",
            "No gameplay policy is promoted here.  This is a concrete-cell confirmation and confluence-gate revision.",
        ],
    }
    (DATA / "rev0053_cell_confirm_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
