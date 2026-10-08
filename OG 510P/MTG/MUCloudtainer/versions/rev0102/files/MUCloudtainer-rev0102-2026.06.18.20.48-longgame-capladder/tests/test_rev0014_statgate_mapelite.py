from __future__ import annotations

from src.muc5.action_schema import Action
from src.muc5.cards import CARD_FORCE, CARD_JACE
from src.muc5.deckspace import DeckVector
from src.muc5.map_elites import build_static_map_elites_archive, deck_descriptor
from src.muc5.public_agents import PublicProfileAgent
from src.muc5.statgate import hoeffding_interval, pairwise_stat_rows, statistical_standings, wilson_interval
from src.muc5.strategy_sets import statgate_probe_strategy_bundles


def test_public_profile_uses_engine_parameter_names_for_force_and_block():
    agent = PublicProfileAgent("heuristic")
    obs = {"frame": "RESPONSE", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}, "own_hand": {}}
    pitch_force = Action("CAST", {"card": CARD_FORCE, "target_card": CARD_JACE, "payment": "pitch", "pitch_card": CARD_FORCE})
    pitch_jace = Action("CAST", {"card": CARD_FORCE, "target_card": CARD_JACE, "payment": "pitch", "pitch_card": CARD_JACE})
    # Jace is still a valuable pitch card, but Force should be penalized more by the profile table.
    assert agent.score_action(obs, pitch_jace) > agent.score_action(obs, pitch_force)

    block_obs = {"frame": "BLOCK", "starting_life": 20, "public_self": {"life": 3}, "public_opponent": {}, "own_hand": {}}
    block_none = Action("BLOCK", {"block_player_attackers": 0, "block_jace_attackers": 0})
    block_face = Action("BLOCK", {"block_player_attackers": 1, "block_jace_attackers": 0})
    assert agent.score_action(block_obs, block_face) > agent.score_action(block_obs, block_none)


def test_statgate_intervals_and_rows():
    w = wilson_interval(7, 10)
    assert 0.0 <= w.low <= w.center <= w.high <= 1.0
    h = hoeffding_interval(0.75, 20)
    assert 0.0 <= h.low <= 0.75 <= h.high <= 1.0
    rows = []
    for i in range(12):
        rows.append({
            "strategy0": "a",
            "strategy1": "b",
            "starting_life": 20,
            "agent0": "x",
            "agent1": "y",
            "deck0": "d0",
            "deck1": "d1",
            "p0_score": 1.0 if i < 9 else 0.0,
            "p1_score": 0.0 if i < 9 else 1.0,
            "p0_terminal_win": 1.0 if i < 9 else 0.0,
            "p1_terminal_win": 0.0 if i < 9 else 1.0,
            "is_nonterminal_draw": False,
            "is_truncation": False,
        })
    standings = statistical_standings(rows, min_games_for_claim=1)
    assert standings[0]["strategy"] == "a"
    pair_rows = pairwise_stat_rows(rows, min_games_for_claim=1)
    assert len(pair_rows) == 1
    assert pair_rows[0]["games"] == 12


def test_map_elites_archive_smoke():
    seed = DeckVector(40, 22, 7, 5, 4, 2)
    desc = deck_descriptor(seed)
    assert desc["size"] == 40
    assert "land_bin" in desc and "life_bias" in desc
    cells = build_static_map_elites_archive([seed], random_samples=40, mutations_per_seed=10, seed=99)
    assert cells
    assert all(c.quality >= 0 for c in cells)


def test_strategy_set_refactor_contains_public_and_code_bundles(tmp_path):
    # Use the real seed deck file through the script-facing API in a tiny assertion.
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    bundles = statgate_probe_strategy_bundles(root / "data" / "seed_decks.json")
    assert len(bundles) == 8
    assert any(b.agent_name.startswith("code_") for b in bundles)
    assert any(b.agent_name == "patient" for b in bundles)
