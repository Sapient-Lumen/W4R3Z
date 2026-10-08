from pathlib import Path

from src.muc5.population_replay_guard import (
    annotate_policy_identity_rows,
    compare_replay_row,
    deck_from_row,
    policy_identity_coverage_rows,
    policy_runtime_identity,
    replay_spec_from_game_row,
    sample_rows_by_source,
)


ROOT = Path(__file__).resolve().parents[1]


def _game_row(**overrides):
    row = {
        "source_revision": "revtest",
        "simulator_revision": "revtest",
        "strategy0": "guard_counter_wall40",
        "strategy1": "pub_threat40_closure",
        "deck0": "forty_counterwall_scaled_from60",
        "deck1": "forty_overlord_impending",
        "agent0": "counter_guard",
        "agent1": "threat_closure",
        "mulligan0": "mulligan_outcome_ranker_rev0027",
        "mulligan1": "land_band_business",
        "starting_life": "20",
        "starting_player": "1",
        "seed": "12345",
        "target_seat": "0",
        "target_deck_size": "40",
        "target_island_count": "21",
        "target_counterspell_count": "10",
        "target_force_count": "5",
        "target_jace_count": "3",
        "target_overlord_count": "1",
        "opponent_deck_size": "40",
        "opponent_island_count": "21",
        "opponent_counterspell_count": "7",
        "opponent_force_count": "4",
        "opponent_jace_count": "2",
        "opponent_overlord_count": "6",
        "terminal_clean_max_decisions": "900",
        "cpp_shadow_game_id": "gtest",
        "winner": "0",
        "p0_score": "1.0",
        "p1_score": "0.0",
        "p0_terminal_win": "1.0",
        "p1_terminal_win": "0.0",
        "is_truncation": "False",
        "loss_reason": "player_1_life_total_zero_or_less",
        "decisions": "123",
        "turn_number": "11",
        "focus_target_score": "1.0",
        "focus_target_result": "target_win",
        "focus_terminal_mechanism": "life_total",
        "focus_terminal_loser_role": "opponent",
        "counter_policy_axis": "public_counter_guard",
        "threat_policy_axis": "library_aware_threat_closure_targetguarded",
        "size_axis": "counter40_vs_threat40",
    }
    row.update(overrides)
    return row


def test_replay_spec_from_game_row_reconstructs_decks_and_orientation():
    row = _game_row()
    target_deck = deck_from_row(row, "target")
    assert target_deck.as_tuple() == (40, 21, 10, 5, 3, 1)
    spec = replay_spec_from_game_row(row, replay_revision="rev0089")
    assert spec.deck0.as_tuple() == target_deck.as_tuple()
    assert spec.deck1.as_tuple() == (40, 21, 7, 4, 2, 6)
    assert spec.agent0 == "counter_guard"
    assert spec.starting_player == 1
    assert spec.max_decisions == 900

    flipped = replay_spec_from_game_row(_game_row(target_seat="1"), replay_revision="rev0089")
    assert flipped.deck0.as_tuple() == (40, 21, 7, 4, 2, 6)
    assert flipped.deck1.as_tuple() == (40, 21, 10, 5, 3, 1)


def test_compare_replay_row_fails_closed_on_terminal_or_focus_drift():
    stored = _game_row()
    replay = {
        "winner": "0",
        "p0_score": 1.0,
        "p1_score": 0.0,
        "p0_terminal_win": 1.0,
        "p1_terminal_win": 0.0,
        "is_truncation": False,
        "loss_reason": "player_1_life_total_zero_or_less",
        "decisions": 123,
        "turn_number": 11,
    }
    assert compare_replay_row(stored, replay)["exact_terminal_replay_match"] is True

    drifted = dict(replay, loss_reason="player_0_attempted_to_draw_from_empty_library", winner="1", p0_score=0.0, p1_score=1.0)
    result = compare_replay_row(stored, drifted)
    assert result["exact_terminal_replay_match"] is False
    assert result["mismatch_count"] >= 3
    assert "focus_terminal_mechanism" in result["mismatch_fields"]


def test_policy_identity_annotation_and_coverage_contract():
    runtime = policy_runtime_identity(ROOT)
    rows = [_game_row(), _game_row(seed="22222")]
    coverage_before = policy_identity_coverage_rows(rows, runtime_digest=str(runtime["digest"]))
    assert coverage_before[0]["missing_policy_runtime_digest_rows"] == 2

    annotated = annotate_policy_identity_rows(rows, root=ROOT)
    assert all(row["policy_identity_schema"] == "muc5.policy_replay_guard.v1" for row in annotated)
    assert len({row["policy_pair_digest"] for row in annotated}) == 1
    coverage_after = policy_identity_coverage_rows(annotated, runtime_digest=str(runtime["digest"]))
    assert coverage_after[0]["all_rows_have_policy_digest"] is True


def test_sample_rows_by_source_is_even_and_source_qualified():
    rows_a = [{"seed": i, "source_revision": ""} for i in range(10)]
    rows_b = [{"seed": i} for i in range(3)]
    sampled = sample_rows_by_source((("revA", rows_a), ("revB", rows_b)), max_per_source=4)
    assert [row["seed"] for row in sampled[:4]] == [0, 3, 6, 9]
    assert len(sampled) == 7
    assert {row["source_revision"] for row in sampled} == {"revA", "revB"}
