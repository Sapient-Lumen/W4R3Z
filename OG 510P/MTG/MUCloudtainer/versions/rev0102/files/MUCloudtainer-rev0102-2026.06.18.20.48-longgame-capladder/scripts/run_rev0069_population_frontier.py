#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    counter_threat_population_arms,
    population_cells_from_summary_rows,
    security_rows_from_cells,
)
from src.muc5.response_matrix import SURGE_THREAT_AXIS
from src.muc5.terminal_clean import mark_terminal_clean_rows, summarize_terminal_clean_rows
from src.muc5.terminal_decomposition import sample_transition_rows
from src.muc5.threat_response import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    annotate_threat_response_rows,
    threat_response_mechanism_rows,
    threat_response_specs,
    threat_response_summary_rows,
)

REV = "rev0069"
CODENAME = "populationfrontier-matrixsafety"
DATA = ROOT / "data"
REPS = 1
BASE_SEED = 6969000
TERMINAL_MAX_DECISIONS = 900


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def normalized_existing_response_rows() -> list[dict[str, object]]:
    """Load older response summaries for a completeness audit.

    rev0065 used a shorter closure-axis name.  rev0069 normalizes it to the
    response-matrix closure axis so the counter-policy population audit can see
    whether historical cells are genuinely comparable or missing.
    """

    rows: list[dict[str, object]] = []
    for path in (
        DATA / "rev0065_counter_response_arm_summary.csv",
        DATA / "rev0067_response_matrix_cumulative_arm_summary.csv",
    ):
        for row in read_csv(path):
            fixed = dict(row)
            if fixed.get("threat_policy_axis") == "library_aware_threat_closure":
                fixed["threat_policy_axis"] = CLOSURE_THREAT_AXIS
            rows.append(fixed)
    return rows


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
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
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
    security_rows = security_rows_from_cells(cells, iterations=20000)

    # Also audit what the inherited rev0065-0067 evidence can and cannot answer
    # without running new games.  This documents that rev0069 closes the legacy
    # pressure/surge gap instead of pretending older pairwise summaries did.
    inherited_cells = population_cells_from_summary_rows(
        normalized_existing_response_rows(),
        row_policies=counter_axes,
        column_policies=threat_axes,
    )
    inherited_security_rows = security_rows_from_cells(inherited_cells, iterations=20000)

    write_csv(DATA / "rev0069_population_frontier_games.csv", annotated_rows)
    write_csv(DATA / "rev0069_population_frontier_aggregate.csv", aggregate)
    write_csv(DATA / "rev0069_population_frontier_arm_summary.csv", arm_summary)
    write_csv(DATA / "rev0069_population_frontier_mechanisms.csv", mechanism_rows)
    write_csv(DATA / "rev0069_population_frontier_security.csv", security_rows)
    write_csv(DATA / "rev0069_population_frontier_inherited_completeness.csv", inherited_security_rows)
    write_csv(DATA / "rev0069_population_frontier_cpp_transition_sample.csv", sample_transition_rows(cpp_transition_rows, limit=240))
    dump_json(DATA / "rev0069_population_frontier_arms.json", [arm.as_dict() for arm in arms])

    complete_cells = sum(1 for r in security_rows if r.get("status") == "complete_population_matrix")
    inherited_complete_cells = sum(1 for r in inherited_security_rows if r.get("status") == "complete_population_matrix")
    pure_floors = [float(r["pure_security_value"]) for r in security_rows if r.get("pure_security_value") not in {"", None}]
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "games": len(annotated_rows),
        "arms": len(arms),
        "reps_per_cell": REPS,
        "size_life_cells": len(security_rows),
        "complete_population_cells": complete_cells,
        "inherited_complete_population_cells_before_rev0069_run": inherited_complete_cells,
        "counter_policy_axes": list(counter_axes),
        "threat_policy_axes": list(threat_axes),
        "worst_pure_security_value_observed": min(pure_floors) if pure_floors else None,
        "best_pure_security_value_observed": max(pure_floors) if pure_floors else None,
        "terminal_clean_summary": terminal_summary.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "python_errors": len(prepared.python_errors),
        "truncations": int(sum(1 for r in annotated_rows if str(r.get("is_truncation")).lower() in {"true", "1"})),
        "raw_cpp_transition_rows_generated_but_not_shipped": len(cpp_transition_rows),
        "cpp_transition_sample_rows_shipped": min(240, len(cpp_transition_rows)),
        "scope": "pilot_empirical_game_not_confirmatory_inference",
    }
    dump_json(DATA / "rev0069_population_frontier_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["python_errors"]:
        raise SystemExit(1)
    if summary["cpp_shadow_summary"].get("mismatches"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
