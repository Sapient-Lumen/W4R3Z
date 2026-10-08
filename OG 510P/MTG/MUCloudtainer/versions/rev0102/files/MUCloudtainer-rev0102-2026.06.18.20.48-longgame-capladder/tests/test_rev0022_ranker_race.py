from random import Random

from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.payoff import load_seed_decks
from src.muc5.public_agents import make_public_agent
from src.muc5.ranker_policy import BlendedLinearRankerAgent, load_default_blended_ranker_agent, load_default_linear_ranker_agent
from src.muc5.strategy_sets import mapelite_ranker_variant_bundles, ranker_mixed_strategy_bundles, ranker_race_benchmarks, ranker_race_candidates


def test_blended_ranker_factory_returns_public_agent():
    agent = make_public_agent("ranker_blend_threat_rev0022")
    assert isinstance(agent, BlendedLinearRankerAgent)
    assert agent.profile == "threat_rush"
    assert agent.name == "ranker_blend_threat_rush_rev0022"


def test_ranker_blend_chooses_legal_index_on_opening_frame():
    decks = load_seed_decks("data/seed_decks.json")
    state = start_game(decks["forty_force_jace_pressure"], decks["sixty_counterwall_jace"], seed=22022, record_log=False)
    frame = build_decision_frame(state)
    agent = load_default_blended_ranker_agent("counter_happy")
    idx = agent.choose_action_index(frame, Random(22022))
    assert 0 <= idx < frame.action_count


def test_ranker_race_strategy_sets_have_unique_ids():
    mixed = ranker_mixed_strategy_bundles("data/seed_decks.json")
    candidates = ranker_race_candidates("data/seed_decks.json")
    benchmarks = ranker_race_benchmarks("data/seed_decks.json")
    assert len({b.strategy_id for b in mixed}) == len(mixed)
    assert len(candidates) == 6
    assert len(benchmarks) == 6
    assert any("ranker" in b.agent_name for b in candidates)
    assert any(b.agent_name.startswith("code_") for b in benchmarks)


def test_mapelite_ranker_variants_group_same_decks():
    bundles = mapelite_ranker_variant_bundles("data/rev0014_map_elites_archive.csv", limit_cells=2)
    assert len(bundles) == 8
    deck_groups = {}
    for b in bundles:
        deck_groups.setdefault(b.deck.as_tuple(), set()).add(b.agent_name)
    assert len(deck_groups) == 2
    for agents in deck_groups.values():
        assert "linear_ranker_rev0021" in agents
        assert "ranker_blend_threat_rev0022" in agents
        assert "code_overlord_clock_rev0013" in agents
        assert "counter_happy" in agents
