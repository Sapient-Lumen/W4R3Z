from __future__ import annotations

from random import Random

from src.muc5.cpp_legal import cpp_legal_menus, cpp_legal_tool_status, legal_record_from_state
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.payoff import load_seed_decks
from src.muc5.sequential_race import load_mapelite_bundles


def test_cpp_legal_menu_main_phase_matches_python_seed_state() -> None:
    decks = load_seed_decks("data/seed_decks.json")
    state = start_game(decks["forty_force_jace_pressure"], decks["sixty_overlord_heavy"], seed=1601, record_log=False)
    frame = build_decision_frame(state)
    menu = cpp_legal_menus([legal_record_from_state(state)], force_build=True)[0]
    assert menu == frame.legal_action_strings
    assert "PASS" in menu


def test_cpp_legal_menu_response_force_pitch_matches_python() -> None:
    decks = load_seed_decks("data/seed_decks.json")
    state = start_game(decks["forty_force_jace_pressure"], decks["sixty_overlord_heavy"], seed=1602, record_log=False)
    # Construct a small direct stack state using legal engine actions to avoid
    # relying on a brittle hand shuffle.
    p0 = state.players[0]
    p1 = state.players[1]
    p0.hand.clear()
    p0.hand["JaceTheMindSculptor"] = 1
    p0.islands_untapped = 4
    p1.hand.clear()
    p1.hand["ForceOfWill"] = 1
    p1.hand["JaceTheMindSculptor"] = 1
    p1.life = 20
    state.active_player = 0
    state.frame = "MAIN"
    from src.muc5.engine import apply_action
    from src.muc5.action_schema import cast

    apply_action(state, cast("JaceTheMindSculptor"), Random(1), validate=True)
    # The caster gets the first response window in this compressed priority
    # model; pass once so the opponent can respond with Force.
    from src.muc5.action_schema import PASS

    apply_action(state, PASS, Random(1), validate=True)
    frame = build_decision_frame(state)
    menu = cpp_legal_menus([legal_record_from_state(state)])[0]
    assert menu == frame.legal_action_strings
    assert any("payment=pitch" in a for a in menu)


def test_cpp_legal_tool_status_builds() -> None:
    status = cpp_legal_tool_status(try_build=True)
    assert status.source_exists
    assert status.binary_exists
    assert status.usable
    assert status.gpp


def test_sequential_race_loads_mapelite_candidates() -> None:
    bundles = load_mapelite_bundles("data/rev0014_map_elites_archive.csv", limit=3)
    assert len(bundles) == 3
    assert all(b.deck.size in {40, 60} for b in bundles)
    assert all(b.strategy_id.startswith("mapelite_") for b in bundles)
