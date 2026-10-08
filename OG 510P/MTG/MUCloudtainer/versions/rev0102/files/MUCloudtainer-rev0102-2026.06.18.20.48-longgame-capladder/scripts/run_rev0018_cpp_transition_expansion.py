from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from random import Random

import pandas as pd

from src.muc5.action_schema import PASS, Action, activate_jace, cast, choose
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
from src.muc5.engine import (
    GameState,
    PendingChoice,
    PendingCombat,
    PlayerState,
    StackSpell,
    apply_action,
    legal_actions,
    start_game,
)
from src.muc5.public_agents import make_public_agent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0018"


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

    # Basic old rev0017-style cases still matter.
    s = _manual_state()
    s.players[0].hand = Counter({CARD_ISLAND: 1})
    _append_case(cases, "direct_play_island", s, Action("PLAY_ISLAND"))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_JACE: 1})
    s.players[0].islands_untapped = 4
    _append_case(cases, "direct_cast_jace", s, cast(CARD_JACE))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_OVERLORD: 1})
    s.players[0].islands_untapped = 5
    _append_case(cases, "direct_cast_overlord_full", s, cast(CARD_OVERLORD, mode="full_cost"))

    s = _manual_state()
    s.players[0].jace_loyalty = 1
    s.players[0].overlord_tapped = 1
    _append_case(cases, "direct_jace_minus1_self_tapped_loyalty_zero", s, activate_jace("minus1", target_player="self", target_state="tapped"))

    s = _manual_state()
    s.players[0].jace_loyalty = 3
    s.players[1].library = [CARD_ISLAND, CARD_FORCE, CARD_JACE]
    _append_case(cases, "direct_jace_plus2_opponent_pending", s, activate_jace("plus2", target_player="opponent"))

    s = _manual_state()
    s.players[0].jace_loyalty = 3
    s.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE]
    _append_case(cases, "direct_jace_zero_brainstorm_pending", s, activate_jace("zero"))

    # RESPONSE pass cases: priority pass and actual stack resolution.
    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 0
    s.pre_stack_frame = "MAIN"
    s.stack = [StackSpell(1, 0, CARD_JACE)]
    s.next_spell_id = 2
    _append_case(cases, "response_pass_priority_to_opponent", s, PASS)

    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 1
    s.pre_stack_frame = "MAIN"
    s.consecutive_passes = 1
    s.stack = [StackSpell(1, 0, CARD_JACE)]
    s.next_spell_id = 2
    _append_case(cases, "response_pass_resolve_jace_clean", s, PASS)

    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 1
    s.pre_stack_frame = "MAIN"
    s.consecutive_passes = 1
    s.stack = [StackSpell(1, 0, CARD_JACE)]
    s.next_spell_id = 2
    s.players[0].jace_loyalty = 7
    s.players[0].jace_used_this_turn = True
    _append_case(cases, "response_pass_resolve_jace_legend_pending", s, PASS)

    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 1
    s.pre_stack_frame = "MAIN"
    s.consecutive_passes = 1
    s.stack = [StackSpell(1, 0, CARD_JACE), StackSpell(2, 1, CARD_COUNTERSPELL, "normal", {"target_id": 1})]
    s.next_spell_id = 3
    _append_case(cases, "response_pass_resolve_counterspell_counter_jace", s, PASS)

    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 1
    s.pre_stack_frame = "MAIN"
    s.consecutive_passes = 1
    s.stack = [StackSpell(1, 0, CARD_OVERLORD, "full_cost")]
    s.next_spell_id = 2
    s.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE]  # top: Jace, then Force
    _append_case(cases, "response_pass_resolve_overlord_full_trigger", s, PASS)

    s = _manual_state()
    s.active_player = 0
    s.frame = "RESPONSE"
    s.priority_player = 1
    s.pre_stack_frame = "MAIN"
    s.consecutive_passes = 1
    s.stack = [StackSpell(1, 0, CARD_OVERLORD, "impending")]
    s.next_spell_id = 2
    s.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE]
    _append_case(cases, "response_pass_resolve_overlord_impending_trigger", s, PASS)

    # Agent-facing choice transitions.
    s = _manual_state()
    s.players[0].hand = Counter({CARD_JACE: 1, CARD_FORCE: 1, CARD_ISLAND: 1})
    s.pending_choice = PendingChoice(0, "discard", {"remaining": 1, "resume": "MAIN", "overlord_triggers_remaining": 0})
    _append_case(cases, "choice_discard_resume_main", s, choose("discard", discard=CARD_ISLAND))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_JACE: 1, CARD_FORCE: 1, CARD_ISLAND: 1})
    s.players[0].library = [CARD_COUNTERSPELL, CARD_OVERLORD, CARD_JACE, CARD_FORCE]
    s.pending_choice = PendingChoice(0, "discard", {"remaining": 1, "resume": "BLOCK_OR_DAMAGE", "overlord_triggers_remaining": 1})
    s.pending_combat = PendingCombat(attacker=0, defender=1, to_player=2, to_jace=0)
    _append_case(cases, "choice_discard_chains_second_attack_trigger", s, choose("discard", discard=CARD_ISLAND))

    s = _manual_state()
    s.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE]
    s.pending_choice = PendingChoice(0, "jace_plus2", {"target_player": 0, "seen_top_card": CARD_FORCE, "resume": "MAIN"})
    _append_case(cases, "choice_jace_plus2_bottom_self", s, choose("jace_plus2", put="bottom"))

    s = _manual_state()
    s.players[0].hand = Counter({CARD_ISLAND: 2, CARD_JACE: 1, CARD_FORCE: 1})
    s.players[0].library = [CARD_COUNTERSPELL, CARD_OVERLORD]
    s.pending_choice = PendingChoice(0, "jace_brainstorm_putback", {"resume": "MAIN"})
    _append_case(cases, "choice_jace_brainstorm_putback_order", s, choose("jace_brainstorm_putback", first_draw=CARD_JACE, second_draw=CARD_ISLAND))

    for keep in ("old", "new"):
        s = _manual_state()
        s.players[0].jace_loyalty = 3
        s.pending_choice = PendingChoice(0, "jace_legend", {"old_loyalty": 9, "old_used": True, "new_loyalty": 3})
        _append_case(cases, f"choice_jace_legend_keep_{keep}", s, choose("jace_legend", keep=keep))

    s = _manual_state()
    s.active_player = 0
    s.players[0].hand = Counter({CARD_ISLAND: 8})
    s.players[1].library = [CARD_COUNTERSPELL, CARD_FORCE]
    s.pending_choice = PendingChoice(0, "cleanup_discard", {"resume": "NEXT_TURN"})
    _append_case(cases, "choice_cleanup_discard_still_over_max", s, choose("cleanup_discard", discard=CARD_ISLAND))

    s = _manual_state()
    s.active_player = 0
    s.players[0].hand = Counter({CARD_ISLAND: 8})
    s.players[1].library = [CARD_COUNTERSPELL, CARD_FORCE]
    s.pending_choice = PendingChoice(0, "cleanup_discard", {"resume": "NEXT_TURN"})
    # Two applications would advance; this one keeps pending because hand goes to 7? Actually after discard 8->7, it advances.
    _append_case(cases, "choice_cleanup_discard_to_next_turn", s, choose("cleanup_discard", discard=CARD_ISLAND))

    # Combat and end-turn transitions now include ATTACK actions and postcombat PASS.
    s = _manual_state()
    s.frame = "ATTACK"
    s.players[0].overlord_ready = 2
    s.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD]
    _append_case(cases, "attack_two_overlords_triggers_pending", s, Action("ATTACK", {"to_player": 2, "to_jace": 0}))

    s = _manual_state()
    s.main_phase = "postcombat"
    s.players[0].impending_1 = 1
    s.players[1].library = [CARD_COUNTERSPELL, CARD_FORCE]
    _append_case(cases, "postcombat_pass_end_turn_awaken_draw", s, PASS)

    return cases


def sampled_cases(max_games: int = 72, max_cases: int = 10000) -> list[tuple[str, GameState, Action]]:
    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 24, 2, 8, 4, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 28, 14, 10, 4, 4),
    ]
    agents = [make_public_agent("heuristic"), make_public_agent("counter_happy"), make_public_agent("threat_rush"), make_public_agent("patient")]
    rng = Random(18018)
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
                    seed=818000 + game_index,
                    starting_player=game_index % 2,
                    starting_life=life,
                    mulligan_policies=("land_band", "land_band_business"),
                    record_log=False,
                )
                for decision in range(450):
                    if state.winner is not None or len(cases) >= max_cases:
                        break
                    frame = build_decision_frame(state)
                    if frame.action_count <= 0:
                        break
                    agent = [a0, a1][frame.player]
                    action_index = agent.choose_action_index(frame, rng)
                    action = frame.legal_actions[action_index]
                    if is_supported_transition(state, action):
                        pending_kind = state.pending_choice.kind if state.pending_choice is not None else "none"
                        cases.append((f"sample_g{game_index}_d{decision}_{state.frame}_{pending_kind}_{action.kind}", copy.deepcopy(state), action))
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
                "source": "direct" if case_id.startswith(("direct_", "response_", "choice_", "attack_", "postcombat_")) else "sampled",
                "frame": before.frame,
                "main_phase": before.main_phase,
                "pending_choice_kind": "none" if before.pending_choice is None else before.pending_choice.kind,
                "stack_depth": len(before.stack),
                "consecutive_passes": before.consecutive_passes,
                "action_kind": action.kind,
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

    df = pd.DataFrame(rows)
    case_groups = df.groupby(["source", "frame", "pending_choice_kind", "action_kind"], dropna=False).size().reset_index(name="cases")
    summary = {
        "revision": REV,
        "tool_status": cpp_transition_tool_status().as_dict(),
        "total_cases": len(records),
        "directed_cases": int((df["source"] == "direct").sum()),
        "sampled_cases": int((df["source"] == "sampled").sum()),
        "mismatches": len(diffs),
        "action_kinds": sorted(df["action_kind"].unique().tolist()),
        "pending_choice_kinds": sorted(str(x) for x in df["pending_choice_kind"].dropna().unique().tolist()),
        "response_pass_resolution_cases": int(((df["frame"] == "RESPONSE") & (df["action_kind"] == "PASS") & (df["consecutive_passes"] >= 1)).sum()),
        "choice_cases": int((df["action_kind"] == "CHOOSE_FOR_EFFECT").sum()),
        "attack_action_cases": int((df["action_kind"] == "ATTACK").sum()),
        "case_groups": case_groups.to_dict(orient="records"),
        "first_mismatch": diffs[0] if diffs else None,
    }
    (DATA / f"{REV}_cpp_transition_diff_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if diffs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
