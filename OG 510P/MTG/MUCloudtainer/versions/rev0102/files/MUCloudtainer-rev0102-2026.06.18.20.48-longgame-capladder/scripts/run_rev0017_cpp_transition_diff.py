from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from random import Random

import pandas as pd

from src.muc5.action_schema import PASS, Action, activate_jace, cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.cpp_transition import (
    TransitionMicroRecord,
    cpp_transition_tool_status,
    diff_transition_records,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
)
from src.muc5.decision import apply_decision_index, build_decision_frame
from src.muc5.deckspace import DeckVector
from src.muc5.engine import GameState, PendingCombat, PlayerState, StackSpell, apply_action, legal_actions, start_game
from src.muc5.public_agents import make_public_agent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0017"


def _manual_state() -> GameState:
    return GameState(players=[PlayerState(life=20), PlayerState(life=20)], record_log=False, starting_life=20)


def _append_case(cases: list[tuple[str, GameState, Action]], case_id: str, state: GameState, action: Action) -> None:
    legal = legal_actions(state)
    if action not in legal:
        raise AssertionError(f"manual case {case_id} action {action.compact()} not legal; legal={[a.compact() for a in legal]}")
    if not is_supported_transition(state, action):
        raise AssertionError(f"manual case {case_id} unexpectedly unsupported: {action.compact()}")
    cases.append((case_id, state, action))


def directed_cases() -> list[tuple[str, GameState, Action]]:
    cases: list[tuple[str, GameState, Action]] = []

    s = _manual_state()
    s.players[0].hand = Counter({CARD_ISLAND: 1})
    _append_case(cases, "direct_play_island", s, Action("PLAY_ISLAND"))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_JACE: 1})
    s.players[0].islands_untapped = 4
    _append_case(cases, "direct_cast_jace", s, cast(CARD_JACE))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_OVERLORD: 1})
    s.players[0].islands_untapped = 3
    _append_case(cases, "direct_cast_overlord_impending", s, cast(CARD_OVERLORD, mode="impending"))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_OVERLORD: 1})
    s.players[0].islands_untapped = 5
    _append_case(cases, "direct_cast_overlord_full", s, cast(CARD_OVERLORD, mode="full_cost"))

    s = _manual_state()
    s.active_player = 1
    s.frame = "RESPONSE"
    s.priority_player = 0
    s.pre_stack_frame = "MAIN"
    s.stack = [StackSpell(1, 1, CARD_JACE)]
    s.next_spell_id = 2
    s.players[0].hand = Counter({CARD_COUNTERSPELL: 1})
    s.players[0].islands_untapped = 2
    _append_case(cases, "direct_response_counterspell", s, cast(CARD_COUNTERSPELL, target_id=1, target_card=CARD_JACE))

    s = _manual_state()
    s.active_player = 1
    s.frame = "RESPONSE"
    s.priority_player = 0
    s.pre_stack_frame = "MAIN"
    s.stack = [StackSpell(1, 1, CARD_OVERLORD, mode="full_cost")]
    s.next_spell_id = 2
    s.players[0].hand = Counter({CARD_FORCE: 1})
    s.players[0].islands_untapped = 5
    _append_case(cases, "direct_response_force_mana", s, cast(CARD_FORCE, payment="mana", target_id=1, target_card=CARD_OVERLORD))

    s = _manual_state()
    s.active_player = 1
    s.frame = "RESPONSE"
    s.priority_player = 0
    s.pre_stack_frame = "MAIN"
    s.stack = [StackSpell(1, 1, CARD_OVERLORD, mode="full_cost")]
    s.next_spell_id = 2
    s.players[0].hand = Counter({CARD_FORCE: 1, CARD_JACE: 1})
    _append_case(cases, "direct_response_force_pitch_jace", s, cast(CARD_FORCE, payment="pitch", pitch_card=CARD_JACE, target_id=1, target_card=CARD_OVERLORD))

    s = _manual_state()
    s.active_player = 1
    s.frame = "RESPONSE"
    s.priority_player = 0
    s.pre_stack_frame = "MAIN"
    s.stack = [StackSpell(1, 1, CARD_JACE)]
    s.next_spell_id = 2
    s.players[0].life = 1
    s.players[0].hand = Counter({CARD_FORCE: 1, CARD_COUNTERSPELL: 1})
    _append_case(cases, "direct_force_pitch_at_one_life", s, cast(CARD_FORCE, payment="pitch", pitch_card=CARD_COUNTERSPELL, target_id=1, target_card=CARD_JACE))

    for state_name in ("ready", "sick", "tapped"):
        s = _manual_state()
        s.players[0].jace_loyalty = 3
        setattr(s.players[1], f"overlord_{state_name}", 1)
        _append_case(cases, f"direct_jace_minus1_opponent_{state_name}", s, activate_jace("minus1", target_player="opponent", target_state=state_name))

    s = _manual_state()
    s.players[0].jace_loyalty = 1
    s.players[0].overlord_tapped = 1
    _append_case(cases, "direct_jace_minus1_self_tapped_loyalty_zero", s, activate_jace("minus1", target_player="self", target_state="tapped"))

    s = _manual_state()
    _append_case(cases, "direct_pass_main_to_attack", s, PASS)

    s = _manual_state()
    s.frame = "ATTACK"
    _append_case(cases, "direct_pass_attack_to_postcombat", s, PASS)

    s = _manual_state()
    s.frame = "BLOCK"
    s.active_player = 0
    s.pending_combat = PendingCombat(attacker=0, defender=1, to_player=1, to_jace=0)
    s.players[1].overlord_ready = 1
    _append_case(cases, "direct_block_player_attacker", s, Action("BLOCK", {"block_player_attackers": 1, "block_jace_attackers": 0}))

    s = _manual_state()
    s.frame = "BLOCK"
    s.active_player = 0
    s.pending_combat = PendingCombat(attacker=0, defender=1, to_player=1, to_jace=0)
    s.players[1].overlord_ready = 1
    _append_case(cases, "direct_pass_block_take_damage", s, PASS)

    s = _manual_state()
    s.frame = "BLOCK"
    s.active_player = 0
    s.pending_combat = PendingCombat(attacker=0, defender=1, to_player=0, to_jace=1)
    s.players[1].jace_loyalty = 3
    _append_case(cases, "direct_pass_block_jace_dies", s, PASS)

    return cases


def sampled_cases(max_games: int = 48, max_cases: int = 5000) -> list[tuple[str, GameState, Action]]:
    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 24, 2, 8, 4, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
    ]
    agents = [make_public_agent("heuristic"), make_public_agent("counter_happy"), make_public_agent("threat_rush"), make_public_agent("patient")]
    rng = Random(17017)
    cases: list[tuple[str, GameState, Action]] = []
    game_index = 0
    for life in (20, 40):
        for d0 in decks:
            for d1 in decks:
                if game_index >= max_games:
                    return cases
                a0 = agents[game_index % len(agents)]
                a1 = agents[(game_index + 1) % len(agents)]
                state = start_game(
                    d0,
                    d1,
                    seed=71000 + game_index,
                    starting_player=game_index % 2,
                    starting_life=life,
                    mulligan_policies=("land_band", "land_band_business"),
                    record_log=False,
                )
                for decision in range(300):
                    if state.winner is not None or len(cases) >= max_cases:
                        break
                    frame = build_decision_frame(state)
                    if frame.action_count <= 0:
                        break
                    agent = [a0, a1][frame.player]
                    action_index = agent.choose_action_index(frame, rng)
                    action = frame.legal_actions[action_index]
                    if is_supported_transition(state, action):
                        cases.append((f"sample_g{game_index}_d{decision}_{action.kind}", copy.deepcopy(state), action))
                    apply_decision_index(state, frame, action_index, rng)
                game_index += 1
    return cases


def make_records_and_expected(cases: list[tuple[str, GameState, Action]]) -> tuple[list[TransitionMicroRecord], list[str], list[dict[str, object]]]:
    records: list[TransitionMicroRecord] = []
    expected: list[str] = []
    rows: list[dict[str, object]] = []
    for case_id, before, action in cases:
        after = copy.deepcopy(before)
        apply_action(after, action, Random(999), validate=True)
        records.append(transition_record_from_state_action(before, action, case_id))
        expected.append(state_signature(after))
        rows.append(
            {
                "case_id": case_id,
                "source": "direct" if case_id.startswith("direct_") else "sampled",
                "frame": before.frame,
                "main_phase": before.main_phase,
                "action": action.compact(),
                "actor": before.current_player(),
                "supported": True,
            }
        )
    return records, expected, rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    cases = directed_cases() + sampled_cases()
    records, expected, rows = make_records_and_expected(cases)
    diffs = diff_transition_records(records, expected)

    cases_csv = DATA / f"{REV}_cpp_transition_cases.csv"
    pd.DataFrame(rows).to_csv(cases_csv, index=False)
    mismatches_path = DATA / f"{REV}_cpp_transition_mismatches.json"
    mismatches_path.write_text(json.dumps(diffs[:50], indent=2), encoding="utf-8")

    action_counts = pd.DataFrame(rows).groupby(["source", "frame"]).size().reset_index(name="cases").to_dict(orient="records")
    summary = {
        "revision": REV,
        "tool_status": cpp_transition_tool_status().as_dict(),
        "total_cases": len(records),
        "directed_cases": sum(1 for r in rows if r["source"] == "direct"),
        "sampled_cases": sum(1 for r in rows if r["source"] == "sampled"),
        "mismatches": len(diffs),
        "action_kinds": sorted(set(r["action"].split("(")[0] for r in rows)),
        "case_groups": action_counts,
        "first_mismatch": diffs[0] if diffs else None,
    }
    (DATA / f"{REV}_cpp_transition_diff_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if diffs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
