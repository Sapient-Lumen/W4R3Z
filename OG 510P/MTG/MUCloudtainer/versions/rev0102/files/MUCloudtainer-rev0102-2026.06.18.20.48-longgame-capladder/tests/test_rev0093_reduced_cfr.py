from __future__ import annotations

import pytest

from src.muc5.reduced_cfr import (
    BOTTOM_TOP,
    JACE_PLUS2,
    LEAVE_TOP,
    PITCH_ISLAND,
    PITCH_JACE,
    PITCH_NONE,
    ReducedMUCCFRGame,
    ReducedMUCState,
    TabularCFRSolver,
    TOP_BLANK,
    TOP_THREAT,
)


def test_reduced_infosets_preserve_jace_privacy_and_public_order():
    game = ReducedMUCCFRGame()
    p0_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2),
        0,
    )
    p0_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2),
        0,
    )
    assert p0_threat != p0_blank
    assert "known_top=threat" in p0_threat

    p1_bottom_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2, jace_order=BOTTOM_TOP),
        1,
    )
    p1_bottom_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2, jace_order=BOTTOM_TOP),
        1,
    )
    p1_leave_threat = game.information_state_key(
        ReducedMUCState(TOP_THREAT, PITCH_NONE, opening=JACE_PLUS2, jace_order=LEAVE_TOP),
        1,
    )
    p1_leave_blank = game.information_state_key(
        ReducedMUCState(TOP_BLANK, PITCH_NONE, opening=JACE_PLUS2, jace_order=LEAVE_TOP),
        1,
    )
    assert p1_bottom_threat == p1_bottom_blank
    assert p1_leave_threat == p1_leave_blank
    assert "known_top" not in p1_bottom_threat
    assert "jace:bottom_top" in p1_bottom_threat
    assert "jace:leave_top" in p1_leave_threat


def test_reduced_infosets_make_force_pitch_public_without_leaking_jace_top():
    game = ReducedMUCCFRGame()
    island_pitch = game.information_state_key(
        ReducedMUCState(
            TOP_THREAT,
            PITCH_ISLAND,
            opening=JACE_PLUS2,
            jace_order=BOTTOM_TOP,
            pressure_action="cast_threat",
            control_response="force_pitch:Island",
        ),
        1,
    )
    jace_pitch = game.information_state_key(
        ReducedMUCState(
            TOP_BLANK,
            PITCH_JACE,
            opening=JACE_PLUS2,
            jace_order=BOTTOM_TOP,
            pressure_action="cast_threat",
            control_response="force_pitch:Jace",
        ),
        1,
    )
    assert island_pitch != jace_pitch
    assert "force_pitch:Island" in island_pitch
    assert "force_pitch:Jace" in jace_pitch
    assert "known_top" not in island_pitch + jace_pitch


def test_reduced_cfr_converges_and_uses_grouped_imperfect_information_best_response():
    solver = TabularCFRSolver(ReducedMUCCFRGame())
    metrics = solver.train(300, checkpoints=(1, 300))
    assert metrics[0].exploitability > 0.02
    assert metrics[-1].exploitability < 2e-4
    assert metrics[-1].exploitability < metrics[0].exploitability / 100.0
    assert metrics[-1].infosets == 33

    root_no_force = solver.average_strategy()["P0|public=root|private=force=none"]
    assert root_no_force["hold_counter"] > 0.99


def test_reduced_cfr_rejects_infoset_action_set_collisions():
    solver = TabularCFRSolver(ReducedMUCCFRGame())
    state = ReducedMUCState(TOP_THREAT, PITCH_NONE)
    key, _, actions = solver._ensure_infoset(state)
    solver.actions_by_infoset[key] = ("corrupted",)
    with pytest.raises(ValueError, match="imperfect-recall"):
        solver._ensure_infoset(state)
