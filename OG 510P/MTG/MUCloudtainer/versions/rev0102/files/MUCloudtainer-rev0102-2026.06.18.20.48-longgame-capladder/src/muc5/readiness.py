from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from random import Random
from typing import Dict, Iterable, List, Sequence

from .action_schema import Action, PASS, activate_jace, choose
from .cards import (
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
    STARTING_LIFE_OPTIONS,
)
from .decision import build_decision_frame, apply_decision_index
from .deckspace import DeckVector
from .engine import GameState, PlayerState, StackSpell, apply_action, legal_actions, start_game
from .fairness import audit_observation_shape, all_checks_pass
from .invariants import card_conservation_report
from .mulligan import POLICY_LAND_BAND, RuleMulliganAgent
from .payoff import load_seed_decks


@dataclass(frozen=True)
class ScenarioCheck:
    name: str
    passed: bool
    focus: str
    details: Dict[str, object]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FuzzSummary:
    games: int
    decisions: int
    invariant_checks: int
    observation_checks: int
    failures: int
    truncations: int
    terminal_games: int
    seconds: float
    decisions_per_second: float
    seed_base: int
    max_decisions: int
    failure_examples: List[Dict[str, object]]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _scenario(name: str, focus: str, passed: bool, **details: object) -> ScenarioCheck:
    return ScenarioCheck(name=name, focus=focus, passed=bool(passed), details=dict(details))


def run_rules_scenarios() -> List[ScenarioCheck]:
    """Directed referee checks for the current five-card universe.

    These are not exhaustive Magic tests. They are a small oracle suite for the
    rules surfaces that matter most to MUC-5 learning: stack fights, Jace
    choices, Overlord triggers/combat, and card conservation.
    """

    out: List[ScenarioCheck] = []

    # 1. Overlord attack triggers must resolve sequentially, not as draw-all then discard-all.
    p0 = PlayerState(
        life=20,
        library=[CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_ISLAND],
        hand=Counter(),
        overlord_ready=2,
    )
    p1 = PlayerState(life=20, library=[], hand=Counter())
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="ATTACK",
        starting_deck_counts=[
            {CARD_ISLAND: 1, CARD_COUNTERSPELL: 1, CARD_FORCE: 1, CARD_JACE: 1, CARD_OVERLORD: 2},
            {},
        ],
        record_log=False,
    )
    apply_action(state, Action("ATTACK", {"to_player": 2, "to_jace": 0}), Random(10), validate=True)
    first_hand = dict(state.players[0].hand)
    first_library = list(state.players[0].library)
    first_pending = {} if state.pending_choice is None else dict(state.pending_choice.data)
    step1_passed = first_hand == {CARD_ISLAND: 1, CARD_JACE: 1} and first_library == [CARD_COUNTERSPELL, CARD_FORCE] and first_pending.get("overlord_triggers_remaining") == 1
    if state.pending_choice is not None:
        apply_action(state, choose("discard", discard=CARD_ISLAND), Random(10), validate=True)
    step2_pending = {} if state.pending_choice is None else dict(state.pending_choice.data)
    inv = card_conservation_report(state)
    step2_passed = state.pending_choice is not None and state.players[0].hand.get(CARD_FORCE, 0) == 1 and state.players[0].hand.get(CARD_COUNTERSPELL, 0) == 1 and inv.passed
    out.append(
        _scenario(
            "overlord_attack_triggers_sequential",
            "Overlord attack triggers",
            step1_passed and step2_passed,
            first_hand=first_hand,
            first_library=first_library,
            first_pending=first_pending,
            second_pending=step2_pending,
            invariant_errors=inv.errors,
        )
    )

    # 2. Jace -1 should target the tactical state of an actual creature, not an impending non-creature.
    p0 = PlayerState(life=20, hand=Counter(), jace_loyalty=3)
    p1 = PlayerState(life=20, hand=Counter(), overlord_ready=1, overlord_sick=1, overlord_tapped=1, impending_1=1)
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="MAIN",
        starting_deck_counts=[{CARD_JACE: 1}, {CARD_OVERLORD: 4}],
        record_log=False,
    )
    compact = [a.compact() for a in legal_actions(state)]
    has_states = all(any(f"target_state={x}" in c for c in compact) for x in ("ready", "sick", "tapped"))
    apply_action(state, activate_jace("minus1", target_player="opponent", target_state="tapped"), Random(11), validate=True)
    inv = card_conservation_report(state)
    out.append(
        _scenario(
            "jace_minus1_specific_creature_state",
            "Jace target legality",
            has_states and state.players[1].overlord_tapped == 0 and state.players[1].impending_1 == 1 and inv.passed,
            legal_minus1=[c for c in compact if "minus1" in c],
            opponent_overlord_ready=state.players[1].overlord_ready,
            opponent_overlord_sick=state.players[1].overlord_sick,
            opponent_overlord_tapped=state.players[1].overlord_tapped,
            opponent_impending_1=state.players[1].impending_1,
            invariant_errors=inv.errors,
        )
    )

    # 3. Counter war: Force counters Counterspell, then Jace resolves.
    p0 = PlayerState(life=20, hand=Counter(), islands_tapped=4)
    p1 = PlayerState(life=20, hand=Counter(), islands_tapped=2)
    state = GameState(
        players=[p0, p1],
        active_player=0,
        priority_player=0,
        frame="RESPONSE",
        stack=[
            StackSpell(1, 0, CARD_JACE),
            StackSpell(2, 1, CARD_COUNTERSPELL, params={"target_id": 1}),
            StackSpell(3, 0, CARD_FORCE, mode="pitch", params={"target_id": 2}),
        ],
        next_spell_id=4,
        pre_stack_frame="MAIN",
        starting_deck_counts=[{CARD_ISLAND: 4, CARD_JACE: 1, CARD_FORCE: 1}, {CARD_ISLAND: 2, CARD_COUNTERSPELL: 1}],
        record_log=False,
    )
    for _ in range(4):
        apply_action(state, PASS, Random(12), validate=True)
    inv = card_conservation_report(state)
    out.append(
        _scenario(
            "counter_war_force_protects_jace",
            "Stack/counter wars",
            state.players[0].jace_loyalty == 3 and not state.stack and state.players[1].graveyard.get(CARD_COUNTERSPELL, 0) == 1 and inv.passed,
            p0_jace_loyalty=state.players[0].jace_loyalty,
            stack_size=len(state.stack),
            p0_graveyard=dict(state.players[0].graveyard),
            p1_graveyard=dict(state.players[1].graveyard),
            invariant_errors=inv.errors,
        )
    )

    # 4. Force at exactly 1 life is legal, but paying the alternative cost loses before resolution.
    p0 = PlayerState(life=1, hand=Counter({CARD_FORCE: 1, CARD_JACE: 1}), islands_untapped=0)
    p1 = PlayerState(life=20, hand=Counter(), islands_untapped=0)
    state = GameState(
        players=[p0, p1],
        active_player=1,
        priority_player=0,
        frame="RESPONSE",
        stack=[StackSpell(1, 1, CARD_OVERLORD, mode="full_cost")],
        next_spell_id=2,
        pre_stack_frame="MAIN",
        starting_deck_counts=[{CARD_FORCE: 1, CARD_JACE: 1}, {CARD_OVERLORD: 1}],
        record_log=False,
    )
    force_actions = [a for a in legal_actions(state) if a.kind == "CAST" and a.params.get("card") == CARD_FORCE]
    legal_pitch = any(a.params.get("payment") == "pitch" and a.params.get("pitch_card") == CARD_JACE for a in force_actions)
    if legal_pitch:
        action = next(a for a in force_actions if a.params.get("payment") == "pitch" and a.params.get("pitch_card") == CARD_JACE)
        apply_action(state, action, Random(13), validate=True)
    inv = card_conservation_report(state)
    out.append(
        _scenario(
            "force_pitch_at_one_life_loses",
            "Force of Will costs/state-based loss",
            legal_pitch and state.winner == 1 and inv.passed,
            legal_force_actions=[a.compact() for a in force_actions],
            winner=state.winner,
            loss_reason=state.loss_reason,
            p0_life=state.players[0].life,
            invariant_errors=inv.errors,
        )
    )

    # 5. Jace ultimate exiles real library card IDs and shuffles the hand into the new library.
    p0 = PlayerState(life=20, hand=Counter(), jace_loyalty=12)
    p1 = PlayerState(life=20, library=[CARD_ISLAND, CARD_FORCE, CARD_OVERLORD], hand=Counter({CARD_COUNTERSPELL: 1, CARD_JACE: 1}))
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="MAIN",
        starting_deck_counts=[{CARD_JACE: 1}, {CARD_ISLAND: 1, CARD_FORCE: 1, CARD_OVERLORD: 1, CARD_COUNTERSPELL: 1, CARD_JACE: 1}],
        record_log=False,
    )
    apply_action(state, activate_jace("ultimate", target_player="opponent"), Random(14), validate=True)
    inv = card_conservation_report(state)
    out.append(
        _scenario(
            "jace_ultimate_real_card_conservation",
            "Jace ultimate zones",
            inv.passed and state.players[1].exile.get(CARD_ISLAND, 0) == 1 and state.players[1].total_hand() == 0 and state.players[1].total_library() == 2,
            opponent_exile=dict(state.players[1].exile),
            opponent_library_count=state.players[1].total_library(),
            opponent_hand_count=state.players[1].total_hand(),
            invariant_errors=inv.errors,
        )
    )

    return out


def run_public_decision_fuzz(
    seed_decks_path: str | Path,
    *,
    games: int = 300,
    max_decisions: int = 250,
    seed_base: int = 10000,
) -> FuzzSummary:
    """Random DecisionFrame rollout fuzzer.

    This deliberately uses the public DecisionFrame path, not the legacy trusted
    GameState agent path. It checks invariants and public observation redaction
    after every applied action.
    """

    rng = Random(seed_base)
    decks = list(load_seed_decks(seed_decks_path).values())
    policies = [POLICY_LAND_BAND]
    failures: List[Dict[str, object]] = []
    decisions = 0
    invariant_checks = 0
    observation_checks = 0
    truncations = 0
    terminal_games = 0
    t0 = time.perf_counter()
    for game_idx in range(games):
        deck0 = rng.choice(decks)
        deck1 = rng.choice(decks)
        life = rng.choice(tuple(STARTING_LIFE_OPTIONS))
        starting_player = rng.randrange(2)
        state = start_game(
            deck0,
            deck1,
            seed=seed_base + game_idx,
            starting_player=starting_player,
            starting_life=life,
            mulligan_agents=(RuleMulliganAgent(rng.choice(policies)), RuleMulliganAgent(rng.choice(policies))),
            record_log=False,
        )
        for step in range(max_decisions):
            inv = card_conservation_report(state)
            invariant_checks += 1
            if not inv.passed:
                failures.append({"game": game_idx, "step": step, "kind": "card_conservation", "errors": inv.errors[:5]})
                break
            obs_checks = audit_observation_shape(state, 0) + audit_observation_shape(state, 1)
            observation_checks += len(obs_checks)
            if not all_checks_pass(obs_checks):
                failures.append({"game": game_idx, "step": step, "kind": "observation_shape", "failed": [c.as_dict() for c in obs_checks if not c.passed][:5]})
                break
            if state.winner is not None:
                terminal_games += 1
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                failures.append({"game": game_idx, "step": step, "kind": "no_legal_actions", "frame": state.frame})
                break
            action_index = rng.randrange(frame.action_count)
            apply_decision_index(state, frame, action_index, rng)
            decisions += 1
        else:
            truncations += 1
    seconds = max(1e-12, time.perf_counter() - t0)
    return FuzzSummary(
        games=games,
        decisions=decisions,
        invariant_checks=invariant_checks,
        observation_checks=observation_checks,
        failures=len(failures),
        truncations=truncations,
        terminal_games=terminal_games,
        seconds=seconds,
        decisions_per_second=decisions / seconds,
        seed_base=seed_base,
        max_decisions=max_decisions,
        failure_examples=failures[:10],
    )


def write_json(path: str | Path, payload: object) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True))
