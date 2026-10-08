from __future__ import annotations

from random import Random

from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD, CARD_ORDER
from src.muc5.mulligan import MULLIGAN_KEEP, mulligan_bottom
from src.muc5.mulligan_outcome_training import candidate_rows_from_mulligan_event, outcome_weight_for_mulligan
from src.muc5.mulligan_ranker import OUTCOME_MODEL_NAME, load_mulligan_ranker_model, make_mulligan_agent, model_path_for_name, mulligan_ranker_feature_names
from src.muc5.payoff import load_seed_decks
from src.muc5.strategy_sets import mulligan_outcome_gate_bundles
from src.muc5.engine import start_game


def _event(stage: str = "keep_or_mulligan", action: str | None = None) -> dict[str, object]:
    hand = {
        CARD_ISLAND: 3,
        CARD_COUNTERSPELL: 1,
        CARD_FORCE: 1,
        CARD_JACE: 1,
        CARD_OVERLORD: 1,
    }
    deck = {
        CARD_ISLAND: 24,
        CARD_COUNTERSPELL: 6,
        CARD_FORCE: 4,
        CARD_JACE: 3,
        CARD_OVERLORD: 3,
    }
    row: dict[str, object] = {
        "player": 0,
        "agent_name": "mulligan_rule_land_band",
        "stage": stage,
        "action": action or MULLIGAN_KEEP.compact(),
        "mulligans_taken": 0 if stage == "keep_or_mulligan" else 1,
        "hand_size": 7,
        "bottom_remaining": 0 if stage == "keep_or_mulligan" else 1,
        "starting_life": 20,
    }
    for card in CARD_ORDER:
        row[f"hand_{card}"] = hand.get(card, 0)
        row[f"deck_{card}"] = deck.get(card, 0)
    return row


def test_mulligan_outcome_candidate_rows_keep_and_bottom() -> None:
    keep_rows, bottom_rows, event_summary = candidate_rows_from_mulligan_event(
        _event(), game_index=0, event_index=0, winner=0, terminal=True, strategy_id="sample"
    )
    assert len(keep_rows) == 1
    assert not bottom_rows
    assert keep_rows[0]["label_keep"] == 1
    assert keep_rows[0]["outcome_weight"] == 1.0
    assert event_summary["weight"] == 1.0

    bottom_action = mulligan_bottom(CARD_OVERLORD).compact()
    keep_rows, bottom_rows, _ = candidate_rows_from_mulligan_event(
        _event("bottom", bottom_action), game_index=1, event_index=0, winner=1, terminal=True, strategy_id="sample"
    )
    assert not keep_rows
    assert len(bottom_rows) == 5
    assert sum(int(r["label_bottom"]) for r in bottom_rows) == 1
    assert all(name in bottom_rows[0] for name in mulligan_ranker_feature_names()[:5])


def test_outcome_weight_does_not_reward_truncation() -> None:
    assert outcome_weight_for_mulligan(1.0, terminal=True) == 1.0
    assert outcome_weight_for_mulligan(0.0, terminal=True) > 0.0
    assert outcome_weight_for_mulligan(0.5, terminal=False) == 0.0


def test_rev0027_outcome_mulligan_agent_loads_and_chooses_legal() -> None:
    model_path = model_path_for_name(OUTCOME_MODEL_NAME)
    assert model_path.exists()
    model = load_mulligan_ranker_model(model_path)
    assert len(model.feature_names) == len(mulligan_ranker_feature_names())
    agent = make_mulligan_agent(OUTCOME_MODEL_NAME)
    decks = load_seed_decks("data/seed_decks.json")
    state = start_game(
        decks["forty_force_jace_pressure"],
        decks["forty_overlord_impending"],
        seed=270270,
        mulligan_agents=(agent, "keep_always"),
        record_log=False,
    )
    assert state.mulligan_log[0]["policy_name"] == OUTCOME_MODEL_NAME
    assert len(state.mulligan_decision_log) >= 1


def test_rev0027_strategy_panel_has_five_mulligan_policies_per_shell() -> None:
    bundles = mulligan_outcome_gate_bundles("data/seed_decks.json")
    assert len(bundles) == 15
    assert OUTCOME_MODEL_NAME in {str(b.mulligan_policy) for b in bundles}
    suffixes = {b.strategy_id.rsplit("_", 1)[-1] for b in bundles}
    assert suffixes == {"keep", "band", "business", "pseudo", "outcome"}
