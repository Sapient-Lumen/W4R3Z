from __future__ import annotations

from pathlib import Path

import pytest

from src.muc5.action_schema import PLAY_ISLAND
from src.muc5.agents import CounterHappyAgent, ThreatRushAgent, make_agent
from src.muc5.deckspace import DeckVector
from src.muc5.gametable import MUC5GameTable, SeatSpec, load_table, save_table


def sample_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_gametable_stops_at_external_seat_and_renders_menu() -> None:
    table = MUC5GameTable(
        sample_deck(),
        sample_deck(),
        seats=(SeatSpec.external(), SeatSpec.from_agent_name("heuristic")),
        seed=101,
        starting_life=20,
        mulligan_policy="land_band",
    ).start()
    assert table.external_to_act()
    snap = table.snapshot()
    assert snap.perspective_player == 0
    assert snap.legal_actions
    rendered = table.render_markdown()
    assert "## Legal actions" in rendered
    assert "Opponent hand:" not in rendered


def test_external_action_applies_and_table_remains_serializable(tmp_path: Path) -> None:
    table = MUC5GameTable(
        sample_deck(),
        sample_deck(),
        seats=(SeatSpec.external(), SeatSpec.from_agent_name("random")),
        seed=102,
        starting_life=40,
        mulligan_policy="land_band",
    ).start()
    actions = table.legal_menu()
    # Prefer playing an Island when available, otherwise any legal action is fine.
    idx = next((i for i, a in enumerate(actions) if a == PLAY_ISLAND), 0)
    snap = table.apply_external_action(idx)
    assert snap.turn_number >= 1
    path = tmp_path / "table.pkl"
    save_table(table, path)
    loaded = load_table(path)
    assert loaded.snapshot().starting_life == 40
    assert loaded.snapshot().legal_actions == table.snapshot().legal_actions


def test_gametable_rejects_action_when_not_external_to_act() -> None:
    table = MUC5GameTable(
        sample_deck(),
        sample_deck(),
        seats=(SeatSpec.from_agent_name("heuristic"), SeatSpec.from_agent_name("random")),
        seed=103,
        max_decisions=8,
    ).start()
    assert not table.external_to_act()
    with pytest.raises(RuntimeError):
        table.apply_external_action(0)


def test_agent_factory_exposes_rev0007_sparring_agents() -> None:
    assert isinstance(make_agent("counter_happy"), CounterHappyAgent)
    assert isinstance(make_agent("threat_rush"), ThreatRushAgent)
    with pytest.raises(ValueError):
        make_agent("unknown_agent")
