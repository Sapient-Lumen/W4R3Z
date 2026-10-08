from __future__ import annotations

from random import Random

from src.muc5.agents import play_public_agent_game
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.deckspace import DeckVector
from src.muc5.replay import state_fingerprint
from src.muc5.strategy_sets import outcome_ranker_probe_bundles


class _BurnUltimator:
    name = "burn_ultimator_test"

    def __init__(self, burn: int = 0) -> None:
        self.burn = burn

    def choose_action_index(self, frame, rng: Random) -> int:
        for _ in range(self.burn):
            rng.random()
        prefs = [
            lambda a: a.kind == "PLAY_ISLAND",
            lambda a: a.kind == "ACTIVATE_JACE" and a.params.get("mode") == "ultimate" and a.params.get("target_player") == "opponent",
            lambda a: a.kind == "ACTIVATE_JACE" and a.params.get("mode") == "plus2" and a.params.get("target_player") == "opponent",
            lambda a: a.kind == "CAST" and a.params.get("card") == "JaceTheMindSculptor",
            lambda a: a.kind == "CHOOSE_FOR_EFFECT" and a.params.get("effect") == "jace_plus2" and a.params.get("put") == "bottom",
            lambda a: a.kind == "CHOOSE_FOR_EFFECT" and a.params.get("effect") == "jace_legend" and a.params.get("keep") == "old",
            lambda a: a.kind == "PASS",
        ]
        for pred in prefs:
            for i, action in enumerate(frame.legal_actions):
                if pred(action):
                    return i
        return 0


class _BurnPass:
    name = "burn_pass_test"

    def __init__(self, burn: int = 0) -> None:
        self.burn = burn

    def choose_action_index(self, frame, rng: Random) -> int:
        for _ in range(self.burn):
            rng.random()
        for i, action in enumerate(frame.legal_actions):
            if action.kind == "PLAY_ISLAND":
                return i
        for i, action in enumerate(frame.legal_actions):
            if action.kind == "PASS":
                return i
        return 0


def test_public_game_splits_policy_rng_from_transition_rng() -> None:
    deck0 = DeckVector(40, 35, 0, 0, 5, 0)
    deck1 = DeckVector(40, 25, 5, 0, 5, 5)
    state0, result0 = play_public_agent_game(deck0, deck1, _BurnUltimator(0), _BurnPass(0), seed=4321, starting_player=0, max_decisions=220, record_log=False)
    state1, result1 = play_public_agent_game(deck0, deck1, _BurnUltimator(1000), _BurnPass(1000), seed=4321, starting_player=0, max_decisions=220, record_log=False)
    assert result0.winner == result1.winner == 0
    assert result0.loss_reason == result1.loss_reason == "player_1_attempted_to_draw_from_empty_library"
    # The game includes Jace ultimate shuffle traffic; consuming extra agent RNG
    # must not perturb transition RNG or final hidden library/zone fingerprints.
    assert state_fingerprint(state0) == state_fingerprint(state1)


def test_cpp_shadow_rollout_smoke_has_zero_mismatches() -> None:
    strategies = outcome_ranker_probe_bundles("data/seed_decks.json")[:2]
    specs = strategy_pair_specs(strategies, simulator_revision="rev0026-test", life_totals=(20,), reps=1, base_seed=26200, max_decisions=200)
    prepared = prepare_cpp_shadow_rollout(specs, revision="rev0026-test")
    summary, rows = finalize_cpp_shadow_rollout(prepared)
    assert summary.games == len(specs)
    assert summary.events > 0
    assert summary.supported_events == summary.events
    assert summary.mismatches == 0
    assert summary.python_errors == 0
    assert rows and all(r.cpp_match is True for r in rows if r.supported_by_cpp)
