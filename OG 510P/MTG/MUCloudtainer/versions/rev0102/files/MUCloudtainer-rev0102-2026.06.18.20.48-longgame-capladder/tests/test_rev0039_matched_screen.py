from __future__ import annotations

from random import Random

from src.muc5.action_screen_compare import _select_screened, _select_unscreened, collect_matched_screen_comparison
from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.strategy_sets import outcome_ranker_probe_bundles
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.public_agents import make_public_agent


def _first_large_or_choice_frame():
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")
    left, right = bundles[0], bundles[1]
    state = start_game(
        left.deck,
        right.deck,
        seed=390391,
        starting_player=0,
        starting_life=20,
        mulligan_agents=(make_mulligan_agent(left.mulligan_policy), make_mulligan_agent(right.mulligan_policy)),
        record_log=False,
    )
    agents = (make_public_agent(left.agent_name), make_public_agent(right.agent_name))
    rng = Random(391)
    trng = Random(390391)
    for _ in range(80):
        frame = build_decision_frame(state)
        if frame.action_count > 1:
            chosen = agents[frame.player].choose_action_index(frame, rng)
            return frame, int(chosen)
        from src.muc5.decision import apply_decision_index
        apply_decision_index(state, frame, 0, trng)
    raise AssertionError("no choice frame found")


def test_screened_selector_keeps_behavior_and_votes_when_budgeted():
    frame, chosen = _first_large_or_choice_frame()
    votes = tuple(i for i in range(min(frame.action_count, 3)))
    idxs, reasons, _subset, _skip = _select_screened(
        frame,
        chosen,
        votes,
        max_actions_per_frame=0,
        branch_action_budget=4,
        rng=Random(1),
    )
    assert chosen in idxs
    assert any(i in idxs for i in votes)
    assert all(0 <= i < frame.action_count for i in idxs)
    assert reasons


def test_unscreened_selector_returns_legal_indices():
    frame, chosen = _first_large_or_choice_frame()
    idxs, reasons, _subset, skip = _select_unscreened(
        frame,
        chosen,
        max_actions_per_frame=0,
        branch_action_budget=4,
        rng=Random(2),
    )
    assert not skip
    assert chosen in idxs
    assert all(0 <= i < frame.action_count for i in idxs)
    assert reasons


def test_collect_matched_screen_comparison_smoke():
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")
    specs = build_action_counterfactual_specs(
        bundles[:3],
        life_totals=(20,),
        base_seed=390399,
        max_decisions=180,
        limit_games=3,
    )
    candidates, methods, branches, votes, transitions, summary = collect_matched_screen_comparison(
        specs,
        revision="rev0039_test",
        screen_agent_names=("counter_happy", "threat_rush", "patient"),
        max_situations=2,
        max_actions_per_frame=3,
        branch_action_budget=4,
        branch_rollouts_per_action=1,
        branch_max_decisions=120,
    )
    assert summary.sampled_situations >= 1
    assert candidates
    assert methods
    assert branches
    assert votes
    assert transitions
    assert summary.cpp_mismatches == 0
