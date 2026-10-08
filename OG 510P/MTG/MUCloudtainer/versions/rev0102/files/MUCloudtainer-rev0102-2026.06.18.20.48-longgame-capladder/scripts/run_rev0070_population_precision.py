#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, sample_prepared_cpp_shadow_rollout
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    counter_threat_population_arms,
    population_cells_from_summary_rows,
    population_precision_gate_rows,
    security_rows_from_cells,
    summarize_population_precision_gate,
)
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.threat_response import (
    annotate_threat_response_rows,
    threat_response_mechanism_rows,
    threat_response_specs,
    threat_response_summary_rows,
)

REV = "rev0070"
CODENAME = "populationprecision-evidencebridge"
DATA = ROOT / "data"
REPS = 2
BASE_SEED = 7070000
TERMINAL_MAX_DECISIONS = 900
MIN_GAMES_PER_CELL = 8
MAX_CI_WIDTH = 0.60
CONSERVATIVE_FLOOR_THRESHOLD = 0.50
MAX_CPP_SHADOW_RECORDS = 30000


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    arms = counter_threat_population_arms(DATA / "seed_decks.json")
    specs, meta = threat_response_specs(
        arms,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=REPS,
        base_seed=BASE_SEED,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    prepared = prepare_cpp_shadow_rollout(specs, revision=REV)
    raw_transition_events = len(prepared.transition_rows)
    shadow_prepared = sample_prepared_cpp_shadow_rollout(prepared, max_records=MAX_CPP_SHADOW_RECORDS)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(shadow_prepared)
    game_rows = mark_terminal_clean_rows(
        list(prepared.game_rows),
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
        strict=False,
    )
    annotated_rows = annotate_threat_response_rows(game_rows, meta)
    terminal_summary = summarize_terminal_clean_rows(
        annotated_rows,
        revision=REV,
        max_decisions=TERMINAL_MAX_DECISIONS,
    )
    arm_summary = threat_response_summary_rows(annotated_rows)
    mechanism_rows = threat_response_mechanism_rows(annotated_rows)
    aggregate = aggregate_payoff_rows(annotated_rows)

    counter_axes = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
    threat_axes = tuple(axis for axis, _agent, _note in THREAT_POPULATION)
    cells = population_cells_from_summary_rows(
        arm_summary,
        row_policies=counter_axes,
        column_policies=threat_axes,
    )
    security_rows = security_rows_from_cells(cells, iterations=30000)
    precision_rows = population_precision_gate_rows(
        arm_summary,
        row_policies=counter_axes,
        column_policies=threat_axes,
        min_games_per_cell=MIN_GAMES_PER_CELL,
        max_ci_width=MAX_CI_WIDTH,
        conservative_floor_threshold=CONSERVATIVE_FLOOR_THRESHOLD,
        iterations=30000,
    )
    precision_summary = summarize_population_precision_gate(precision_rows)

    write_csv(DATA / "rev0070_population_precision_games.csv", annotated_rows)
    write_csv(DATA / "rev0070_population_precision_aggregate.csv", aggregate)
    write_csv(DATA / "rev0070_population_precision_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0070_population_precision_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0070_population_precision_security.csv", security_rows)
    write_csv(DATA / "rev0070_population_precision_gate.csv", precision_rows)
    write_csv(DATA / "rev0070_population_precision_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=360))
    dump_json(DATA / "rev0070_population_precision_arms.json", [arm.as_dict() for arm in arms])

    complete_cells = sum(1 for r in security_rows if r.get("status") == "complete_population_matrix")
    pure_floors = [float(r["pure_security_value"]) for r in security_rows if r.get("pure_security_value") not in {"", None}]
    conservative_lcbs = [
        float(r["conservative_pure_security_lcb"])
        for r in precision_rows
        if r.get("conservative_pure_security_lcb") not in {"", None}
    ]
    max_widths = [
        float(r["max_ci_width_observed"])
        for r in precision_rows
        if r.get("max_ci_width_observed") not in {"", None}
    ]
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "games": len(annotated_rows),
        "arms": len(arms),
        "reps_per_cell": REPS,
        "min_games_per_population_cell": min(int(r.get("min_games_per_observed_cell", 0) or 0) for r in security_rows),
        "gate_min_games_per_cell": MIN_GAMES_PER_CELL,
        "gate_max_ci_width": MAX_CI_WIDTH,
        "gate_conservative_floor_threshold": CONSERVATIVE_FLOOR_THRESHOLD,
        "size_life_cells": len(security_rows),
        "complete_population_cells": complete_cells,
        "counter_policy_axes": list(counter_axes),
        "threat_policy_axes": list(threat_axes),
        "worst_pure_security_value_observed": min(pure_floors) if pure_floors else None,
        "best_pure_security_value_observed": max(pure_floors) if pure_floors else None,
        "worst_conservative_pure_security_lcb": min(conservative_lcbs) if conservative_lcbs else None,
        "best_conservative_pure_security_lcb": max(conservative_lcbs) if conservative_lcbs else None,
        "max_ci_width_observed": max(max_widths) if max_widths else None,
        "precision_gate_summary": precision_summary,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "raw_cpp_transition_rows_generated_but_not_shipped": raw_transition_events,
        "cpp_shadow_records_checked": len(shadow_prepared.records),
        "cpp_shadow_record_cap": MAX_CPP_SHADOW_RECORDS,
        "cpp_transition_sample_rows_shipped": min(360, len(cpp_transition_rows)),
        "scope": "replicated_population_precision_gate_not_claim_promotion",
    }
    dump_json(DATA / "rev0070_population_precision_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["python_errors"]:
        raise SystemExit(1)
    if summary["truncations"]:
        raise SystemExit(1)
    if summary["cpp_shadow_summary"].get("mismatches"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
