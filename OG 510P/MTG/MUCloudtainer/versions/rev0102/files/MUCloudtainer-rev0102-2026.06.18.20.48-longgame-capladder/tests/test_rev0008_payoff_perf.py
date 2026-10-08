from random import Random

from src.muc5.agents import HeuristicAgent, play_agent_game
from src.muc5.engine import apply_action, legal_actions, start_game
from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.payoff import aggregate_payoff_rows, build_payoff_rows, default_strategy_bundles
from src.muc5.perf import benchmark_agent_games


def test_apply_action_trusted_legal_path_matches_safe_path_for_opening_land():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    safe = start_game(deck, deck, seed=808, mulligan_policy=POLICY_LAND_BAND)
    fast = start_game(deck, deck, seed=808, mulligan_policy=POLICY_LAND_BAND)
    action = next((a for a in legal_actions(safe) if a.kind == "PLAY_ISLAND"), legal_actions(safe)[0])
    apply_action(safe, action, Random(1), validate=True)
    apply_action(fast, action, Random(1), validate=False)
    assert safe.players[0].hand == fast.players[0].hand
    assert safe.players[0].islands_untapped == fast.players[0].islands_untapped
    assert safe.frame == fast.frame


def test_payoff_rows_have_expected_small_shape():
    strategies = default_strategy_bundles("data/seed_decks.json")[:2]
    rows = build_payoff_rows(strategies, life_totals=(20,), reps=1, base_seed=1234, max_decisions=60)
    assert len(rows) == 2 * 2 * 1 * 2 * 1
    assert {r["starting_life"] for r in rows} == {20}
    agg = aggregate_payoff_rows(rows)
    assert len(agg) == 4
    assert all(0.0 <= float(r["p0_mean_score_draw_half"]) <= 1.0 for r in agg)


def test_benchmark_returns_positive_throughput():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    result = benchmark_agent_games(deck, deck, games=2, max_decisions=20, validate_actions=False)
    assert result.games == 2
    assert result.seconds > 0
    assert result.games_per_second > 0


def test_play_agent_game_validate_toggle_runs():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    for validate in (False, True):
        _, result = play_agent_game(deck, deck, HeuristicAgent(), HeuristicAgent(), seed=99, max_decisions=20, validate_actions=validate)
        assert result.decisions >= 1
