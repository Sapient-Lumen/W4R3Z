from __future__ import annotations

from random import Random
from collections import Counter

from src.muc5.deckspace import DeckVector
from src.muc5.engine import deck_to_library, start_game_from_pregame_state
from src.muc5.invariants import card_conservation_report
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.opening_counterfactual import make_forced_branch, run_opening_counterfactual_panel, CounterfactualPairSpec


def test_start_game_from_explicit_pregame_state_conserves_cards() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    library0 = deck_to_library(deck, Random(11))
    library1 = deck_to_library(deck, Random(17))
    hand0 = Counter(library0.pop() for _ in range(7))
    hand1 = Counter(library1.pop() for _ in range(7))
    state = start_game_from_pregame_state(deck, deck, library0=library0, hand0=hand0, library1=library1, hand1=hand1, starting_life=20, record_log=False)
    report = card_conservation_report(state)
    assert report.passed, report.errors
    assert state.frame == "MAIN"
    assert state.starting_deck_counts == [deck.counts(), deck.counts()]


def test_forced_first_mulligan_branches_same_initial_library() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    library = deck_to_library(deck, Random(101))
    keep = make_forced_branch(branch="keep", initial_library=library, agent=POLICY_LAND_BAND, player=0, seed=202, starting_life=20, deck_counts=deck.counts())
    mull = make_forced_branch(branch="mulligan", initial_library=library, agent=POLICY_LAND_BAND, player=0, seed=202, starting_life=20, deck_counts=deck.counts())
    assert keep.mulligans_taken == 0
    assert mull.mulligans_taken >= 1
    assert keep.kept_hand_size == 7
    assert mull.kept_hand_size <= 6
    assert tuple(library) != mull.library


def test_tiny_counterfactual_panel_runs_and_cpp_checks() -> None:
    deck0 = DeckVector(40, 24, 6, 4, 3, 3)
    deck1 = DeckVector(40, 23, 5, 5, 2, 5)
    spec = CounterfactualPairSpec(
        pair_id="tiny",
        deck0_name="d0",
        deck1_name="d1",
        deck0=deck0,
        deck1=deck1,
        agent0="threat_rush",
        agent1="counter_happy",
        fallback_mulligan0=POLICY_LAND_BAND,
        mulligan1=POLICY_LAND_BAND,
        starting_life=20,
        starting_player=0,
        seed=99001,
        max_decisions=120,
    )
    result = run_opening_counterfactual_panel([spec])
    assert len(result.branch_rows) == 2
    assert len(result.paired_rows) == 1
    assert result.summary["cpp_mismatches"] == 0
    assert result.summary["skipped_cpp_events"] == 0
