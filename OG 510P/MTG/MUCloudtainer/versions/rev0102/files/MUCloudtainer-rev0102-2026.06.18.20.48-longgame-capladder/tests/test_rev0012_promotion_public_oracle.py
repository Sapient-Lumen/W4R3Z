from __future__ import annotations

from random import Random

from src.muc5.decision import build_decision_frame
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.oracle_seed import generate_oracle_candidates, mutate_deck
from src.muc5.public_agents import make_public_agent, PublicProfileAgent
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings


def test_public_profile_agent_uses_decision_frame_only():
    deck = DeckVector(40, 20, 8, 6, 4, 2)
    state = start_game(deck, deck, seed=1212, starting_life=20, record_log=False)
    frame = build_decision_frame(state)
    agent = make_public_agent("threat_rush")
    idx = agent.choose_action_index(frame, Random(1))
    assert 0 <= idx < frame.action_count
    assert getattr(agent, "name").startswith("public_")


def test_promotion_gate_rejects_missing_provenance_and_accepts_clean_rows():
    clean = {
        "simulator_revision": "rev0012",
        "strategy0": "a",
        "strategy1": "b",
        "deck0": "da",
        "deck1": "db",
        "agent0": "heuristic",
        "agent1": "heuristic",
        "mulligan0": "land_band",
        "mulligan1": "land_band",
        "starting_life": 20,
        "starting_player": 0,
        "seed": 1,
        "winner": "0",
        "p0_score": 1.0,
        "p1_score": 0.0,
        "p0_terminal_win": 1.0,
        "p1_terminal_win": 0.0,
        "is_nonterminal_draw": False,
        "is_truncation": False,
        "loss_reason": "player_1_life_total_zero_or_less",
        "decisions": 12,
        "reward_convention": "draw_half_reporting_terminal_only_training",
        "interface": "public_decision_frame",
    }
    report = audit_promotion_rows([clean], replay_results=[{"passed": True}], config=PromotionGateConfig(min_rows=1, min_replay_traces=1))
    assert report.passed, report.errors
    bad = dict(clean)
    bad.pop("interface")
    report_bad = audit_promotion_rows([bad], replay_results=[{"passed": True}], config=PromotionGateConfig(min_rows=1, min_replay_traces=1))
    assert not report_bad.passed
    assert any("missing required payoff columns" in e for e in report_bad.errors)


def test_strategy_standings_counts_both_seats():
    rows = [
        {"strategy0": "a", "strategy1": "b", "p0_score": 1.0, "p1_score": 0.0, "p0_terminal_win": 1.0, "p1_terminal_win": 0.0, "is_truncation": False},
        {"strategy0": "b", "strategy1": "a", "p0_score": 0.5, "p1_score": 0.5, "p0_terminal_win": 0.0, "p1_terminal_win": 0.0, "is_truncation": True},
    ]
    standings = strategy_standings(rows)
    a = next(r for r in standings if r["strategy"] == "a")
    assert a["games"] == 2
    assert a["mean_score_draw_half"] == 0.75
    assert a["truncation_rate"] == 0.5


def test_oracle_candidate_generation_is_plausible_and_deterministic():
    base = [DeckVector(40, 20, 8, 6, 4, 2), DeckVector(60, 30, 12, 8, 6, 4)]
    c1 = generate_oracle_candidates(base, seed=7, random_samples=50, mutations_per_base=5, keep=4)
    c2 = generate_oracle_candidates(base, seed=7, random_samples=50, mutations_per_base=5, keep=4)
    assert [c.deck.as_tuple() for c in c1] == [c.deck.as_tuple() for c in c2]
    assert len(c1) == 4
    assert all(c.deck.threats >= 1 and c.deck.interaction >= 1 for c in c1)
    mutated = mutate_deck(base[0], Random(1), steps=3)
    assert mutated.size == base[0].size
    assert sum(mutated.counts().values()) == mutated.size
