from pathlib import Path

from src.muc5.action_counterfactual import build_action_counterfactual_specs, collect_action_counterfactuals
from src.muc5.public_agents import make_public_agent
from src.muc5.strategy_sets import outcome_ranker_probe_bundles

ROOT = Path(__file__).resolve().parents[1]


def test_action_counterfactual_collector_small_smoke():
    strategies = outcome_ranker_probe_bundles(ROOT / "data" / "seed_decks.json")[:2]
    specs = build_action_counterfactual_specs(strategies, life_totals=(20,), base_seed=990000, limit_games=2, max_decisions=120)
    candidates, branches, transitions, summary = collect_action_counterfactuals(
        specs,
        revision="test",
        max_situations=2,
        max_actions_per_frame=8,
        branch_rollouts_per_action=1,
        branch_max_decisions=80,
    )
    assert summary.sampled_situations >= 1
    assert len(candidates) == summary.candidate_actions
    assert len(branches) == summary.branch_games
    assert summary.cpp_mismatches == 0
    assert summary.cpp_skipped_transitions == 0
    assert transitions


def test_counterfactual_ranker_factory_loads_after_rev0033_script():
    model = ROOT / "data" / "rev0033_counterfactual_action_ranker_model.json"
    if not model.exists():
        return
    agent = make_public_agent("counterfactual_linear_ranker_rev0033")
    assert agent.name == "counterfactual_linear_ranker_rev0033"


def test_cpp_combat_jace_exact_minus_one_sentinel_guard():
    from collections import Counter
    from random import Random
    import copy
    from src.muc5.cards import CARD_ISLAND, CARD_JACE
    from src.muc5.cpp_transition import cpp_transition_signatures, state_signature, transition_record_from_state_action
    from src.muc5.decision import apply_decision_index, build_decision_frame
    from src.muc5.engine import GameState, PendingChoice, PendingCombat, PlayerState

    p0 = PlayerState(life=20, hand=Counter({CARD_ISLAND: 1}))
    p1 = PlayerState(life=20, hand=Counter(), jace_loyalty=4, jace_used_this_turn=True)
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="ATTACK",
        main_phase="precombat",
        pending_choice=PendingChoice(0, "discard", {"remaining": 1, "resume": "BLOCK_OR_DAMAGE", "overlord_triggers_remaining": 0}),
        pending_combat=PendingCombat(attacker=0, defender=1, to_player=0, to_jace=1),
        record_log=False,
    )
    frame = build_decision_frame(state)
    assert frame.legal_actions[0].compact() == "CHOOSE_FOR_EFFECT(discard=Island, effect=discard)"
    pre = copy.deepcopy(state)
    action = apply_decision_index(state, frame, 0, Random(1))
    assert state.players[1].jace_loyalty is None
    assert state.players[1].jace_used_this_turn is False
    assert state.players[1].graveyard[CARD_JACE] == 1
    rec = transition_record_from_state_action(pre, action, "jace_exact_minus_one")
    assert cpp_transition_signatures([rec], force_build=True)[0] == state_signature(state)
