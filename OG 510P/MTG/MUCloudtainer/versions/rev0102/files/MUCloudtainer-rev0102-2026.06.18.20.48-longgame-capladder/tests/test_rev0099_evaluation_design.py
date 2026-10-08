from __future__ import annotations

from src.muc5.evaluation_design import audit_balanced_focal_rows, balanced_pair_cells, expected_games_per_pair, pair_symmetry_rows
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.psro_catalog import current_response_population


def test_balanced_pair_cells_cover_life_rep_seat_and_start() -> None:
    cells = balanced_pair_cells((20, 40), reps=3)
    assert len(cells) == expected_games_per_pair((20, 40), 3) == 24
    assert {(cell.orientation, cell.starting_player) for cell in cells if cell.starting_life == 20 and cell.rep == 0} == {
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    }
    assert {cell.focal_player for cell in cells} == {0, 1}


def test_balanced_focal_row_audit_detects_missing_orientation() -> None:
    rows = [
        {
            "stage": "unit",
            "focal_strategy": "a",
            "opponent_strategy": "b",
            "starting_life": 20,
            "rep": 0,
            "orientation": 0,
            "starting_player": 0,
            "focal_player": 0,
            "score": 1.0,
        }
    ]
    audit = audit_balanced_focal_rows(rows, expected_life_totals=(20,), expected_reps=1)
    assert audit["passed"] is False
    assert audit["incomplete_group_count"] == 1


def test_empirical_evaluator_emits_canonical_balanced_rows() -> None:
    population = current_response_population("data/seed_decks.json")
    focal = population[0]
    opponent = population[2]
    config = EmpiricalEvaluationConfig(life_totals=(20,), reps=1, max_decisions=80, base_seed=999099)
    estimate, rows = EmpiricalGameEvaluator().evaluate_focal_pair(focal, opponent, config, stage="unit_rev0099_balance")
    assert estimate.games == 4
    audit = audit_balanced_focal_rows(rows, expected_life_totals=(20,), expected_reps=1)
    assert audit["passed"] is True
    pair_rows = pair_symmetry_rows(rows)
    assert len(pair_rows) == 1
    assert pair_rows[0]["seat0_rows"] == pair_rows[0]["seat1_rows"] == 2
    assert pair_rows[0]["focal_starts_rows"] == pair_rows[0]["focal_draws_rows"] == 2
