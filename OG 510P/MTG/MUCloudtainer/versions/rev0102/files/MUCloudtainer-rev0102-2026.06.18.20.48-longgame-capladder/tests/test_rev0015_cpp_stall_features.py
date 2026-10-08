from __future__ import annotations

import numpy as np

from src.muc5.action_features import action_feature_names, action_feature_vector, frame_action_feature_matrix
from src.muc5.action_schema import Action
from src.muc5.cpp_accel import PROBE_COLUMNS, cpp_toolchain_status, probe_table_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.decision import build_decision_frame
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.probability import deck_probe
from src.muc5.public_agents import make_public_agent


def test_rev0015_cpp_probe_kernel_matches_python_seed() -> None:
    status = cpp_toolchain_status(try_build=True)
    assert status.usable, status.as_dict()
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    row = np.array([deck.as_tuple()], dtype=np.int32)
    out = probe_table_cpp(row)[0]
    p = deck_probe(deck)
    py = np.array([
        p.p_keepable_2_to_5_islands,
        p.p_force_plus_pitch_open7,
        p.p_counterspell_online_turn2_play,
        p.p_overlord_impending_turn3_play,
        p.p_jace_turn4_play,
        p.p_overlord_full_turn5_play,
        p.crude_probe_score,
    ])
    assert len(PROBE_COLUMNS) == 7
    assert float(np.max(np.abs(out - py))) < 1e-12


def test_rev0015_stall_agent_prefers_land_and_pass_over_threats() -> None:
    agent = make_public_agent("stall")
    obs = {"frame": "MAIN", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}}
    assert agent.score_action(obs, Action("PLAY_ISLAND", {})) > agent.score_action(obs, Action("PASS", {}))
    assert agent.score_action(obs, Action("PASS", {})) > agent.score_action(obs, Action("CAST", {"card": "JaceTheMindSculptor"}))
    resp = {"frame": "RESPONSE", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}}
    counter_threat = Action("CAST", {"card": "Counterspell", "target_card": "JaceTheMindSculptor"})
    counter_cspell = Action("CAST", {"card": "Counterspell", "target_card": "Counterspell"})
    assert agent.score_action(resp, counter_threat) > agent.score_action(resp, counter_cspell)


def test_rev0015_action_features_stable_and_frame_matrix() -> None:
    names = action_feature_names()
    vec = action_feature_vector(Action("CAST", {"card": "ForceOfWill", "target_card": "JaceTheMindSculptor", "payment": "pitch", "pitch_card": "OverlordOfTheFloodpits"}), {"frame": "RESPONSE"})
    d = dict(zip(names, vec))
    assert len(names) == len(vec)
    assert d["kind_cast"] == 1.0
    assert d["cast_force"] == 1.0
    assert d["payment_pitch"] == 1.0
    assert d["pitch_overlord"] == 1.0
    assert d["target_jace"] == 1.0

    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=1515, mulligan_policy=POLICY_LAND_BAND, record_log=False)
    frame = build_decision_frame(state)
    mat = frame_action_feature_matrix(frame)
    assert len(mat) == frame.action_count
    assert all(len(row) == len(names) for row in mat)
