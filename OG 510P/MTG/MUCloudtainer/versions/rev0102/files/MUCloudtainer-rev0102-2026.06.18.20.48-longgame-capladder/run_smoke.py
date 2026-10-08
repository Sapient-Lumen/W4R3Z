from __future__ import annotations

from random import Random

from src.muc5.agents import HeuristicAgent, RandomAgent, play_agent_game
from src.muc5.gametable import MUC5GameTable, SeatSpec
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.constructors import random_search, toy_static_scorer
from src.muc5.deckspace import DeckVector, deck_count, random_deck, stratified_buckets, total_deck_count
from src.muc5.env import MUC5SlotEnv
from src.muc5.invariants import card_conservation_report
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.engine import legal_actions as engine_legal_actions, play_random_game, start_game
from src.muc5.probability import deck_probe
from src.muc5.tournament import standard_life_configs
from src.muc5.rules_kernel import DecisionState, PlayerPublic, SpellOnStack, demo_state, legal_actions as kernel_legal_actions


def main() -> None:
    print("MUC-5 smoke check rev0015")
    print("40-card deck vectors:", deck_count(40))
    print("60-card deck vectors:", deck_count(60))
    print("total deck vectors:", total_deck_count())

    rng = Random(42)
    d = random_deck(rng)
    print("sample deck:", d)
    print("sample buckets:", stratified_buckets(d))

    print("\nlegacy legal-kernel main-phase actions:")
    for a in kernel_legal_actions(demo_state()):
        print(" -", a.compact())

    response_state = DecisionState(
        player_to_act=1,
        active_player=0,
        frame="RESPONSE_TO_SPELL",
        hand={CARD_ISLAND: 0, CARD_COUNTERSPELL: 1, CARD_FORCE: 2, CARD_JACE: 1, CARD_OVERLORD: 0},
        public_self=PlayerPublic(life=20, islands_untapped=2, islands_tapped=2, library_count=33, hand_count_public=4),
        public_opp=PlayerPublic(life=20, islands_untapped=0, islands_tapped=4, library_count=33, hand_count_public=4),
        stack=[SpellOnStack(controller=0, card=CARD_JACE), SpellOnStack(controller=0, card=CARD_OVERLORD)],
    )
    print("\nresponse legal actions against two spells on stack:")
    for a in kernel_legal_actions(response_state):
        print(" -", a.compact())

    seed_deck = DeckVector(40, 24, 6, 4, 3, 3)
    print("\nprobability probe for seed deck:")
    print(deck_probe(seed_deck))

    print("\nrev0005 engine opening state legal actions:")
    state = start_game(seed_deck, seed_deck, seed=11)
    print("frame:", state.frame, "main_phase:", state.main_phase)
    for a in engine_legal_actions(state):
        print(" -", a.compact())

    print("\nslot env observation at 40 life with land-band mulligan:")
    env = MUC5SlotEnv(seed_deck, seed_deck, max_action_slots=64, max_decisions=50, starting_life=40, mulligan_policy=POLICY_LAND_BAND)
    obs = env.reset(seed=13)
    print("starting_life:", obs.raw["starting_life"], "feature_len:", len(obs.feature_vector), "legal_slots:", sum(obs.action_mask))
    print("mulligan_log:", env.state.mulligan_log if env.state is not None else None)
    print("conservation:", card_conservation_report(env.state).passed if env.state is not None else None)
    print("legal strings:", obs.action_strings[:6])

    print("\nstandard life configs:")
    for cfg in standard_life_configs():
        print(" -", cfg.as_dict())

    print("\nrandom-engine game smoke:")
    game = play_random_game(seed_deck, seed_deck, seed=12, max_decisions=300, starting_life=40, mulligan_policy=POLICY_LAND_BAND)
    print("winner:", game.winner, "reason:", game.loss_reason, "log_events:", len(game.log))
    print("last_log_events:")
    for line in game.log[-8:]:
        print(" -", line)

    print("\nheuristic-vs-random game smoke:")
    hgame, hres = play_agent_game(seed_deck, seed_deck, HeuristicAgent(), RandomAgent(), seed=14, max_decisions=120, mulligan_policy=POLICY_LAND_BAND)
    print("winner:", hres.winner, "reason:", hres.loss_reason, "decisions:", hres.decisions, "log_events:", hres.log_events)
    print("last_log_events:")
    for line in hgame.log[-8:]:
        print(" -", line)

    print("\nrev0007 assistant gametable smoke:")
    table = MUC5GameTable(
        seed_deck,
        seed_deck,
        seats=(SeatSpec.external(), SeatSpec.from_agent_name("threat_rush")),
        seed=77,
        starting_life=20,
        mulligan_policy=POLICY_LAND_BAND,
        max_decisions=40,
    ).start()
    snap = table.snapshot()
    print("external_to_act:", snap.external_to_act, "legal_actions:", snap.legal_actions[:5])
    print("render_head:")
    for line in table.render_markdown(transcript_tail=4).splitlines()[:10]:
        print(" -", line)

    print("\ntoy constructor top 3 from 200 random samples:")
    result = random_search(toy_static_scorer, samples=200, seed=9)
    for deck, score in result.candidates[:3]:
        print(f" - {score:.3f}", deck)


if __name__ == "__main__":
    main()
