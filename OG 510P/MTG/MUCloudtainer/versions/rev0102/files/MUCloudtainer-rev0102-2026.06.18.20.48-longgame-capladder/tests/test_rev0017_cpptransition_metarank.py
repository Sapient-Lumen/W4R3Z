from __future__ import annotations

import copy
from random import Random

import numpy as np

from src.muc5.action_schema import Action, activate_jace, cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.cpp_transition import (
    cpp_transition_tool_status,
    cpp_transition_signatures,
    state_signature,
    transition_record_from_state_action,
)
from src.muc5.engine import GameState, PlayerState, StackSpell, apply_action
from src.muc5.metarank import meta_rank_from_matrix, stationary_distribution


def test_cpp_transition_play_island_matches_python() -> None:
    state = GameState(players=[PlayerState(life=20), PlayerState(life=20)], record_log=False)
    state.players[0].hand[CARD_ISLAND] = 1
    action = Action("PLAY_ISLAND")
    rec = transition_record_from_state_action(state, action, "unit_play_island")
    expected_state = copy.deepcopy(state)
    apply_action(expected_state, action, Random(1), validate=True)
    actual = cpp_transition_signatures([rec], force_build=True)[0]
    assert actual == state_signature(expected_state)


def test_cpp_transition_force_pitch_at_one_life_matches_python() -> None:
    state = GameState(players=[PlayerState(life=1), PlayerState(life=20)], record_log=False)
    state.active_player = 1
    state.frame = "RESPONSE"
    state.priority_player = 0
    state.stack = [StackSpell(1, 1, CARD_JACE)]
    state.next_spell_id = 2
    state.players[0].hand[CARD_FORCE] = 1
    state.players[0].hand[CARD_COUNTERSPELL] = 1
    action = cast(CARD_FORCE, payment="pitch", pitch_card=CARD_COUNTERSPELL, target_id=1, target_card=CARD_JACE)
    rec = transition_record_from_state_action(state, action, "unit_force_pitch_one_life")
    expected_state = copy.deepcopy(state)
    apply_action(expected_state, action, Random(1), validate=True)
    actual = cpp_transition_signatures([rec])[0]
    assert actual == state_signature(expected_state)
    assert "GAME_OVER" in actual


def test_cpp_transition_jace_minus1_target_state_matches_python() -> None:
    state = GameState(players=[PlayerState(life=20), PlayerState(life=20)], record_log=False)
    state.players[0].jace_loyalty = 3
    state.players[1].overlord_tapped = 1
    action = activate_jace("minus1", target_player="opponent", target_state="tapped")
    rec = transition_record_from_state_action(state, action, "unit_jace_minus1_tapped")
    expected_state = copy.deepcopy(state)
    apply_action(expected_state, action, Random(1), validate=True)
    actual = cpp_transition_signatures([rec])[0]
    assert actual == state_signature(expected_state)


def test_cpp_transition_toolchain_status() -> None:
    status = cpp_transition_tool_status(try_build=True)
    assert status.usable
    assert status.source_exists
    assert status.binary_exists


def test_metarank_stationary_distribution_sums_to_one() -> None:
    transition = np.array([[0.8, 0.2], [0.1, 0.9]], dtype=np.float64)
    dist = stationary_distribution(transition)
    assert abs(float(dist.sum()) - 1.0) < 1e-12
    assert dist[1] > dist[0]


def test_metarank_detects_cycle_without_crashing() -> None:
    strategies = ["rock", "paper", "scissors"]
    matrix = np.array(
        [
            [0.5, 0.0, 1.0],
            [1.0, 0.5, 0.0],
            [0.0, 1.0, 0.5],
        ],
        dtype=np.float64,
    )
    result = meta_rank_from_matrix(strategies, matrix, selection_strength=8.0)
    masses = {r.strategy: r.meta_rank_mass for r in result}
    assert set(masses) == set(strategies)
    assert abs(sum(masses.values()) - 1.0) < 1e-12
    assert max(masses.values()) - min(masses.values()) < 1e-6
