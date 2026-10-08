from __future__ import annotations

from random import Random

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_hybrid_compare import collect_matched_hybrid_comparison
from src.muc5.action_hybrid_selector import select_hybrid_action_indices
from src.muc5.decision import apply_decision_index, build_decision_frame
from src.muc5.engine import start_game
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.public_agents import make_public_agent
from src.muc5.strategy_sets import outcome_ranker_probe_bundles


def _first_choice_frame():
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")
    left, right = bundles[0], bundles[1]
    state = start_game(
        left.deck,
        right.deck,
        seed=404001,
        starting_player=0,
        starting_life=20,
        mulligan_agents=(make_mulligan_agent(left.mulligan_policy), make_mulligan_agent(right.mulligan_policy)),
        record_log=False,
    )
    agents = (make_public_agent(left.agent_name), make_public_agent(right.agent_name))
    rng = Random(4040)
    trng = Random(404001)
    for _ in range(100):
        frame = build_decision_frame(state)
        if frame.action_count > 1:
            chosen = agents[frame.player].choose_action_index(frame, rng)
            return frame, int(chosen)
        apply_decision_index(state, frame, 0, trng)
    raise AssertionError("no choice frame found")


def test_hybrid_selector_keeps_behavior_and_stays_budgeted():
    frame, chosen = _first_choice_frame()
    votes = tuple(i for i in range(min(frame.action_count, 3)))
    idxs, reasons, _subset, skip, meta = select_hybrid_action_indices(
        frame,
        chosen,
        votes,
        max_actions_per_frame=0,
        branch_action_budget=4,
        rng=Random(40),
        ranker_revision="rev0034",
    )
    assert not skip
    assert meta is not None
    assert chosen in idxs
    assert len(idxs) <= 4
    assert len(set(idxs)) == len(idxs)
    assert all(0 <= i < frame.action_count for i in idxs)
    assert reasons
    assert any("screen_vote" in reasons.get(i, "") for i in idxs) or frame.action_count <= 1


def test_hybrid_selector_full_menu_keeps_all_when_small():
    frame, chosen = _first_choice_frame()
    idxs, reasons, subset, skip, meta = select_hybrid_action_indices(
        frame,
        chosen,
        (),
        max_actions_per_frame=999,
        branch_action_budget=2,
        rng=Random(41),
    )
    assert not skip
    assert not subset
    assert tuple(idxs) == tuple(range(frame.action_count))
    assert meta is not None
    assert len(reasons) == frame.action_count


def test_collect_matched_hybrid_comparison_smoke():
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")
    specs = build_action_counterfactual_specs(
        bundles[:3],
        life_totals=(20,),
        base_seed=404099,
        max_decisions=180,
        limit_games=3,
    )
    candidates, methods, branches, votes, transitions, summary = collect_matched_hybrid_comparison(
        specs,
        revision="rev0040_test",
        screen_agent_names=("counter_happy", "threat_rush", "patient"),
        max_situations=2,
        max_actions_per_frame=3,
        branch_action_budget=4,
        branch_rollouts_per_action=1,
        branch_max_decisions=120,
        ranker_revision="rev0034",
    )
    assert summary.sampled_situations >= 1
    assert candidates
    assert methods
    assert branches
    assert votes
    assert transitions
    assert summary.cpp_mismatches == 0
    assert {"unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker"}.issubset({str(r["method"]) for r in methods})
