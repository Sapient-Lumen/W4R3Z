from __future__ import annotations

from dataclasses import dataclass
import re
from random import Random
from typing import Dict, Iterable, List, Tuple

from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD, OVERLORD_POWER
from .decision import DecisionFrame, PublicDecisionAgent, PublicRandomAgent, PublicHeuristicAgent


@dataclass
class PublicProfileAgent:
    """Hidden-information-safe public-frame agent with a named style profile.

    The earlier ``Agent`` interface hands scripted baselines the omniscient
    ``GameState`` object. That is acceptable for debugging, but it is the wrong
    contract for learning methods or promotion gates. PublicProfileAgent sees
    only the DecisionFrame: public/private-correct observation plus legal action
    strings emitted by the referee.

    This class intentionally remains simple. The point is not to encode expert
    MUC theory; it gives payoff tables multiple deterministic, inspectable
    sparring personalities without leaking hidden libraries or opponent hands.
    """

    profile: str = "heuristic"

    @property
    def name(self) -> str:
        return f"public_{self.profile}_rev0012"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = [(self.score_action(frame.observation, action), rng.random(), i) for i, action in enumerate(frame.legal_actions)]
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]

    def score_action(self, obs: Dict[str, object], action: Action) -> float:
        profile = self.profile.lower()
        if profile in {"stall", "turtle", "draw_adversary"}:
            return _stall_public_score(obs, action)
        score = _base_public_score(obs, action)
        frame = str(obs.get("frame", "MAIN"))

        if profile in {"counter_happy", "counterhappy"}:
            if frame == "RESPONSE":
                if action.kind == "CAST":
                    target_card = str(action.params.get("target_card", ""))
                    score += 5.0
                    if target_card in {CARD_JACE, CARD_OVERLORD}:
                        score += 2.0
                    if action.params.get("card") == CARD_COUNTERSPELL:
                        score += 1.0
                elif action.kind == "PASS":
                    score -= 3.0
        elif profile in {"threat_rush", "threatrush"}:
            if frame == "MAIN" and action.kind == "CAST":
                card = str(action.params.get("card", ""))
                if card == CARD_OVERLORD:
                    score += 4.0
                elif card == CARD_JACE:
                    score += 2.5
            if action.kind == "ATTACK":
                score += 3.0
            if frame == "RESPONSE" and action.kind == "CAST":
                target_card = str(action.params.get("target_card", ""))
                if target_card not in {CARD_JACE, CARD_OVERLORD}:
                    score -= 4.0
            if frame == "MAIN" and action.kind == "PASS":
                score -= 1.5
        elif profile in {"threat_closure", "threat_guard", "threat_lethal_guard"}:
            score = _threat_closure_public_score(obs, action)
        elif profile in {"threat_pressure", "threat_response", "threat_jace_pressure", "threat_counter_guard_response"}:
            score = _threat_pressure_public_score(obs, action)
        elif profile in {"threat_surge", "threat_protect", "threat_counterpressure", "threat_face_surge"}:
            score = _threat_surge_public_score(obs, action)
        elif profile in {"counter_guard", "counter_closure", "counter_survival"}:
            score = _counter_guard_public_score(obs, action)
        elif profile in {"counter_life20_stabilizer", "counter_stabilizer", "counter_low_life_closure_guard"}:
            score = _counter_life20_stabilizer_public_score(obs, action)
        elif profile in {"patient", "draw_go", "control"}:
            if frame == "MAIN" and action.kind == "CAST" and action.params.get("card") in {CARD_JACE, CARD_OVERLORD}:
                score -= 2.0
            if frame == "RESPONSE" and action.kind == "PASS":
                score += 0.5
        elif profile not in {"heuristic", "balanced"}:
            raise ValueError(f"unknown public profile {self.profile!r}")
        return score


@dataclass
class PublicInformationStateAgent:
    """Inspectable policy that makes durable information state decision-relevant.

    rev0091 made perfect-recall facts available, but every incumbent profile still
    scored only the compact observation.  This wrapper preserves the established
    profile score and adds a deliberately small, auditable adjustment from known
    top cards and public event history.  It is a calibration policy, not a claim
    that these hand-tuned weights are strategically optimal.
    """

    profile: str = "heuristic"
    information_weight: float = 1.0

    @property
    def name(self) -> str:
        return f"public_infostate_{self.profile}_rev0092"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = [
            (self.score_action(frame, action), rng.random(), index)
            for index, action in enumerate(frame.legal_actions)
        ]
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return scored[0][2]

    def score_action(self, frame: DecisionFrame, action: Action) -> float:
        base = PublicProfileAgent(self.profile).score_action(frame.observation, action)
        return base + float(self.information_weight) * _information_state_adjustment(frame, action)


def _known_top_card(frame: DecisionFrame, target_player: int) -> str | None:
    information = frame.information_state if isinstance(frame.information_state, dict) else {}
    known = information.get("known_top_cards", {})
    if not isinstance(known, dict):
        return None
    value = known.get(str(int(target_player)))
    return None if value is None else str(value)


def _information_state_adjustment(frame: DecisionFrame, action: Action) -> float:
    """Small public/private-history adjustment used by rev0092 calibration agents."""

    viewer = int(frame.player)
    opponent = 1 - viewer
    own_top = _known_top_card(frame, viewer)
    opponent_top = _known_top_card(frame, opponent)
    score = 0.0

    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        raw_target = action.params.get("target_player")
        target = viewer if raw_target == "self" else opponent if raw_target == "opponent" else raw_target
        try:
            target = int(target) if target is not None else None
        except (TypeError, ValueError):
            target = None

        if mode == "zero":
            # Brainstorm is more attractive when persistent knowledge says the
            # natural draw is an Island, and slightly less urgent when a premium
            # interaction/threat card is already known on top.
            if own_top == CARD_ISLAND:
                score += 2.75
            elif own_top in {CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD}:
                score -= 0.75
        elif mode == "plus2" and target == opponent:
            # Do not spend another fateseal merely to re-confirm an Island left
            # on the opponent's library; revisit known business cards aggressively.
            if opponent_top == CARD_ISLAND:
                score -= 3.25
            elif opponent_top in {CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD}:
                score += 1.75
        elif mode == "plus2" and target == viewer:
            if own_top == CARD_ISLAND:
                score += 1.25
            elif own_top in {CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD}:
                score += 0.35

    information = frame.information_state if isinstance(frame.information_state, dict) else {}
    events = information.get("public_events", [])
    if isinstance(events, list) and action.kind == "CAST" and action.params.get("card") in {CARD_JACE, CARD_OVERLORD}:
        opponent_pitch_events = sum(
            1
            for event in events
            if isinstance(event, dict)
            and event.get("kind") == "FORCE_PITCH_PAYMENT"
            and int(event.get("player", -1)) == opponent
        )
        # Each observed pitch is evidence that the opponent spent Force plus a
        # second card.  The adjustment is capped so history cannot dominate the
        # underlying closure/pressure profile.
        score += min(1.5, 0.5 * opponent_pitch_events)

    return score


def _public_zone(obs: Dict[str, object], key: str) -> Dict[str, object]:
    value = obs.get(key)
    return value if isinstance(value, dict) else {}


def _count_hand(obs: Dict[str, object], card: str) -> int:
    hand = obs.get("own_hand")
    if not isinstance(hand, dict):
        return 0
    return int(hand.get(card, 0) or 0)


def _stack_spell_for_action(obs: Dict[str, object], action: Action) -> Dict[str, object]:
    """Return the public stack object targeted by a counter action, if visible."""

    try:
        target_id = int(action.params.get("target_id", -1))
    except (TypeError, ValueError):
        return {}
    stack = obs.get("stack")
    if not isinstance(stack, list):
        return {}
    for item in stack:
        if not isinstance(item, dict):
            continue
        try:
            spell_id = int(item.get("spell_id", -2))
        except (TypeError, ValueError):
            continue
        if spell_id == target_id:
            return item
    return {}


def _targets_own_spell(obs: Dict[str, object], action: Action) -> bool:
    """Whether a Counterspell/Force action points at the current player's spell.

    The legal menu permits countering your own spell. That can occasionally be a
    real Magic tactic, but in the current public baseline profiles it was almost
    always accidental self-sabotage because the scorers valued only target card
    name, not target controller.  This helper keeps ownership checks centralized.
    """

    item = _stack_spell_for_action(obs, action)
    if not item:
        return False
    try:
        return int(item.get("controller", -999)) == int(obs.get("player", -1))
    except (TypeError, ValueError):
        return False


def _threat_closure_public_score(obs: Dict[str, object], action: Action) -> float:
    """Threat profile with explicit library/closure guards.

    rev0062 exposed that ``threat_rush`` often died to its own Overlord/Jace
    draw engine even against all-Island opponents.  This profile is intentionally
    still simple and public-information-only, but it treats own library count as
    a real tactical resource: do not declare attacks or use draw engines that can
    self-deck before damage, and prefer the smallest lethal attack that survives
    its own attack triggers.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    own_library = int(obs.get("own_library_count", public_self.get("library_count", 0)) or 0)
    opp_life = float(public_opp.get("life", obs.get("starting_life", 20)) or 0)
    own_life = float(public_self.get("life", obs.get("starting_life", 20)) or 0)
    own_hand_size = int(public_self.get("hand_count", 0) or 0)
    own_overlords = int(public_self.get("overlord_ready", 0) or 0) + int(public_self.get("overlord_sick", 0) or 0) + int(public_self.get("overlord_tapped", 0) or 0)
    own_ready_overlords = int(public_self.get("overlord_ready", 0) or 0)
    opp_overlords = int(public_opp.get("overlord_ready", 0) or 0) + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)

    if action.kind == "PLAY_ISLAND":
        return 120.0
    if action.kind == "PASS":
        # Passing in attack is fine when every attack would self-deck; passing in
        # main is a fallback after land/cast decisions.
        return 25.0 if frame == "ATTACK" else 2.0
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        attackers = to_player + to_jace
        draw_cost = 2 * attackers
        if attackers <= 0:
            return 0.0
        if own_library < draw_cost:
            return -1000.0 - attackers
        damage = OVERLORD_POWER * to_player
        post_trigger_library = own_library - draw_cost
        score = 90.0 + 8.0 * damage + 2.0 * to_jace - 0.5 * draw_cost
        if damage >= opp_life:
            # Prefer the smallest lethal packet that will survive the attack-trigger
            # draws.  Overkill matters because every extra attacker draws two.
            score += 500.0 - 6.0 * attackers - 0.5 * max(0.0, damage - opp_life)
        if post_trigger_library <= 4:
            score -= 25.0 * (5 - post_trigger_library)
        return score
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card == CARD_OVERLORD:
            # Overlord ETB/impending trigger draws two then discards one.  Avoid
            # turning a threat into an immediate empty-library loss or spending
            # the last library buffer on redundant bodies when existing attackers
            # can already close.
            if own_library < 2:
                return -900.0
            ready_lethal_attackers = int((opp_life + OVERLORD_POWER - 1) // OVERLORD_POWER)
            if own_ready_overlords >= ready_lethal_attackers and own_library >= 2 * ready_lethal_attackers:
                return -120.0
            if own_overlords * OVERLORD_POWER >= opp_life and own_library <= 12:
                return -80.0
            mode = str(action.params.get("mode", "full_cost"))
            base = 95.0 if mode == "full_cost" else 80.0
            if own_library <= 10 and own_overlords > 0:
                base -= 20.0 * (11 - own_library)
            elif own_library <= 5:
                base -= 30.0 * (6 - own_library)
            return base
        if card == CARD_JACE:
            # Jace is support, not the primary close plan in the threat shell.
            return 20.0 if opp_overlords else 8.0
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            if _targets_own_spell(obs, action):
                return -850.0
            target = str(action.params.get("target_card", ""))
            if target in {CARD_JACE, CARD_OVERLORD}:
                return 70.0 if own_life > 2 else 55.0
            return 8.0
        return 0.0
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        target = str(action.params.get("target_player", ""))
        if mode == "ultimate":
            return 1000.0 if target == "opponent" else -1000.0
        if mode == "minus1":
            return 120.0 if action.params.get("target_player") == "opponent" else 5.0
        if mode == "plus2":
            return 30.0 if target == "opponent" else 8.0
        if mode == "zero":
            if own_library < 5:
                return -800.0
            # Brainstorm digs, but it costs a draw burst and was a major self-deck
            # vector in the life-40 threat-shell audit.
            return 18.0 - max(0, 10 - own_library) * 4.0 - max(0, own_hand_size - 5)
        return 0.0
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        return 8.0 * block_player + 4.0 * block_jace
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            # Preserve lands and Overlords for closure; Jace/counters are expendable
            # against inert controls.  The response policy still uses counters when
            # they matter.
            values = {CARD_JACE: 9.0, CARD_COUNTERSPELL: 7.0, CARD_FORCE: 6.0, CARD_ISLAND: 2.0, CARD_OVERLORD: 1.0}
            return values.get(card, 0.0)
        if effect == "force_pitch":
            values = {CARD_JACE: 8.0, CARD_COUNTERSPELL: 5.0, CARD_OVERLORD: 3.0, CARD_FORCE: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_OVERLORD, CARD_ISLAND}
            return 5.0 if (put == "leave" and business) or (put == "bottom" and not business) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_JACE: 5.0, CARD_COUNTERSPELL: 4.0, CARD_FORCE: 3.0, CARD_ISLAND: 1.0, CARD_OVERLORD: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "old" else 3.0
        return 0.0
    return 0.0



def _threat_pressure_public_score(obs: Dict[str, object], action: Action) -> float:
    """Threat response tuned against the public ``counter_guard`` candidate.

    ``threat_closure`` fixed the obvious overdraw bugs from ``threat_rush``, but
    rev0065 showed that ``counter_guard`` could still win by baiting repeated
    Overlord/Jace churn and by letting a resolved Jace become a long-game engine.
    This profile stays public-information-only: it attacks opposing Jace more
    aggressively, counters opposing Jace/Overlord with higher priority, and stops
    spending additional two-card Overlord draw triggers once existing attackers or
    a library buffer should be conserved.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    own_library = int(obs.get("own_library_count", public_self.get("library_count", 0)) or 0)
    opp_life = float(public_opp.get("life", obs.get("starting_life", 20)) or 0)
    own_life = float(public_self.get("life", obs.get("starting_life", 20)) or 0)
    own_hand_size = int(public_self.get("hand_count", 0) or 0)
    own_overlords = int(public_self.get("overlord_ready", 0) or 0) + int(public_self.get("overlord_sick", 0) or 0) + int(public_self.get("overlord_tapped", 0) or 0)
    own_ready_overlords = int(public_self.get("overlord_ready", 0) or 0)
    opp_overlords = int(public_opp.get("overlord_ready", 0) or 0) + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)
    opp_ready_overlords = int(public_opp.get("overlord_ready", 0) or 0)
    opp_jace_raw = public_opp.get("jace_loyalty")
    opp_jace_loyalty = None if opp_jace_raw is None else int(opp_jace_raw)
    starting_life = float(obs.get("starting_life", 20) or 20)

    if action.kind == "PLAY_ISLAND":
        return 125.0
    if action.kind == "PASS":
        if frame == "ATTACK":
            return 28.0
        if frame == "RESPONSE":
            return 10.0
        # After one or more bodies are online, conserving library is often better
        # than walking another Overlord ETB trigger into Counterspell/Force.
        if own_overlords > 0 and own_library <= 14:
            return 46.0
        return 5.0
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        attackers = to_player + to_jace
        draw_cost = 2 * attackers
        if attackers <= 0:
            return 0.0
        if own_library < draw_cost:
            return -1100.0 - attackers
        damage = OVERLORD_POWER * to_player
        jace_damage = OVERLORD_POWER * to_jace
        post_trigger_library = own_library - draw_cost
        score = 88.0 + 9.0 * damage + 3.0 * to_jace - 0.7 * draw_cost
        if damage >= opp_life:
            score += 620.0 - 6.0 * attackers - 0.5 * max(0.0, damage - opp_life)
        elif opp_jace_loyalty is not None and to_jace > 0:
            # A live opposing Jace is counter_guard's best long-game tool.  When
            # player lethal is unavailable, removing Jace beats modest face damage.
            score += 170.0 + 32.0 * to_jace
            if jace_damage >= opp_jace_loyalty:
                score += 270.0 - 3.0 * max(0, jace_damage - opp_jace_loyalty)
            if opp_jace_loyalty >= 8:
                score += 55.0
        if post_trigger_library <= 5:
            score -= 30.0 * (6 - post_trigger_library)
        return score
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card == CARD_OVERLORD:
            if own_library < 2:
                return -950.0
            ready_lethal_attackers = int((opp_life + OVERLORD_POWER - 1) // OVERLORD_POWER)
            jace_kill_attackers = int(((opp_jace_loyalty or 0) + OVERLORD_POWER - 1) // OVERLORD_POWER) if opp_jace_loyalty is not None else 0
            useful_attackers_needed = max(ready_lethal_attackers if opp_life > 0 else 0, jace_kill_attackers)
            if own_ready_overlords >= ready_lethal_attackers and own_library >= 2 * ready_lethal_attackers:
                return -150.0
            if own_overlords > 0 and own_library <= 14 and own_ready_overlords >= min(max(1, useful_attackers_needed), own_overlords + 1):
                return -180.0
            if own_library <= 8 and own_overlords > 0:
                return -220.0
            mode = str(action.params.get("mode", "full_cost"))
            base = 102.0 if mode == "full_cost" else 82.0
            if opp_jace_loyalty is not None and own_ready_overlords < max(1, jace_kill_attackers):
                base += 22.0
            if own_library <= 12:
                base -= 12.0 * (13 - own_library)
            return base
        if card == CARD_JACE:
            if opp_jace_loyalty is not None:
                return 32.0
            return 26.0 if opp_overlords else 10.0
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            if _targets_own_spell(obs, action):
                return -875.0
            target = str(action.params.get("target_card", ""))
            if target == CARD_JACE:
                return 125.0
            if target == CARD_OVERLORD:
                return 100.0 if own_life > max(2.0, 0.08 * starting_life) else 70.0
            if target in {CARD_COUNTERSPELL, CARD_FORCE}:
                return 28.0
            return 8.0
        return 0.0
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        target = str(action.params.get("target_player", ""))
        if mode == "ultimate":
            return 1000.0 if target == "opponent" else -1000.0
        if mode == "minus1":
            if action.params.get("target_player") == "opponent":
                return 95.0 + 18.0 * opp_ready_overlords + 6.0 * opp_overlords
            return 5.0
        if mode == "plus2":
            return 64.0 if target == "opponent" else 16.0
        if mode == "zero":
            if own_library < 12:
                return -820.0
            return 12.0 - max(0, own_hand_size - 4) * 2.0
        return 0.0
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        lethalish = own_life <= OVERLORD_POWER * max(1, opp_ready_overlords)
        return (70.0 if lethalish else 34.0) * block_player + 18.0 * block_jace
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            overlord_discard = 1.0 if own_overlords <= 0 else (7.0 if own_library <= 12 else 3.0)
            values = {CARD_JACE: 9.5, CARD_COUNTERSPELL: 7.5, CARD_FORCE: 6.5, CARD_ISLAND: 2.5, CARD_OVERLORD: overlord_discard}
            return values.get(card, 0.0)
        if effect == "force_pitch":
            values = {CARD_JACE: 8.0, CARD_COUNTERSPELL: 5.0, CARD_OVERLORD: 3.0, CARD_FORCE: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_OVERLORD, CARD_ISLAND}
            return 5.0 if (put == "leave" and business) or (put == "bottom" and not business) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_JACE: 5.0, CARD_COUNTERSPELL: 4.0, CARD_FORCE: 3.0, CARD_ISLAND: 1.0, CARD_OVERLORD: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "old" else 3.0
        return 0.0
    return 0.0


def _threat_surge_public_score(obs: Dict[str, object], action: Action) -> float:
    """Threat response tuned for counter-heavy shells without hidden-state access.

    ``threat_pressure`` repaired overdraw and attacked opposing Jace, but rev0066
    left open whether it was still too patient against ``counter_guard``.  Surge
    is the sharper anti-control hypothesis: spend interaction to protect threat
    spells in stack fights, put damage on the player when it is safe, and use Jace
    mostly as support rather than as another draw engine.  It remains a public
    profile; it sees the same DecisionFrame observation as the other guarded
    policies.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    starting_life = float(obs.get("starting_life", 20) or 20)
    own_life = float(public_self.get("life", starting_life) or starting_life)
    opp_life = float(public_opp.get("life", starting_life) or starting_life)
    own_library = int(obs.get("own_library_count", public_self.get("library_count", 0)) or 0)
    own_hand_size = int(public_self.get("hand_count", 0) or 0)
    own_ready_overlords = int(public_self.get("overlord_ready", 0) or 0)
    own_overlords = own_ready_overlords + int(public_self.get("overlord_sick", 0) or 0) + int(public_self.get("overlord_tapped", 0) or 0)
    opp_ready_overlords = int(public_opp.get("overlord_ready", 0) or 0)
    opp_overlords = opp_ready_overlords + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)
    opp_jace_raw = public_opp.get("jace_loyalty")
    opp_jace_loyalty = None if opp_jace_raw is None else int(opp_jace_raw)
    own_jace_raw = public_self.get("jace_loyalty")
    own_jace_loyalty = None if own_jace_raw is None else int(own_jace_raw)
    untapped = int(public_self.get("islands_untapped", 0) or 0)

    if action.kind == "PLAY_ISLAND":
        return 130.0
    if action.kind == "PASS":
        if frame == "RESPONSE":
            return 4.0
        if frame == "ATTACK":
            # Passing attack is acceptable only when no safe pressure exists.
            return 8.0
        if own_overlords > 0 and own_library <= 8:
            return 48.0
        if own_overlords > 0 and untapped >= 2:
            # Leave mana up after sticking a body; counter_guard wins long stack
            # fights when the threat pilot spends every main-phase resource.
            return 24.0
        return 2.0
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        attackers = to_player + to_jace
        if attackers <= 0:
            return 0.0
        draw_cost = 2 * attackers
        if own_library < draw_cost:
            return -1200.0 - attackers
        damage = OVERLORD_POWER * to_player
        jace_damage = OVERLORD_POWER * to_jace
        post_library = own_library - draw_cost
        score = 94.0 + 14.0 * damage + 7.0 * to_jace - 0.9 * draw_cost
        if damage >= opp_life:
            # Minimal lethal face attack is the top priority; every extra attacker
            # is another two-card draw trigger.
            score += 760.0 - 9.0 * attackers - max(0.0, damage - opp_life)
        elif opp_jace_loyalty is not None and to_jace > 0:
            score += 90.0 + 18.0 * to_jace
            if jace_damage >= opp_jace_loyalty:
                score += 190.0 - 3.0 * max(0, jace_damage - opp_jace_loyalty)
            if opp_jace_loyalty >= 8:
                score += 85.0
        elif to_player > 0 and own_library >= 12:
            # Against counter_guard, pressure matters; do not always wait for a
            # guaranteed lethal packet if library is healthy.
            score += 55.0
        if post_library <= 5:
            score -= 42.0 * (6 - post_library)
        return score
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card == CARD_OVERLORD:
            if own_library < 2:
                return -980.0
            ready_lethal_attackers = int((opp_life + OVERLORD_POWER - 1) // OVERLORD_POWER)
            jace_kill_attackers = int(((opp_jace_loyalty or 0) + OVERLORD_POWER - 1) // OVERLORD_POWER) if opp_jace_loyalty is not None else 0
            useful_attackers_needed = max(1, ready_lethal_attackers, jace_kill_attackers)
            if own_ready_overlords >= ready_lethal_attackers and own_library >= 2 * ready_lethal_attackers:
                return -170.0
            if own_overlords >= useful_attackers_needed and own_library <= 14:
                return -210.0
            if own_library <= 6 and own_overlords > 0:
                return -260.0
            mode = str(action.params.get("mode", "full_cost"))
            base = 118.0 if mode == "full_cost" else 94.0
            if own_overlords == 0:
                base += 32.0
            if opp_jace_loyalty is not None and own_ready_overlords < max(1, jace_kill_attackers):
                base += 24.0
            if own_library <= 12:
                base -= 10.0 * (13 - own_library)
            return base
        if card == CARD_JACE:
            if own_jace_loyalty is not None:
                return -65.0
            # Jace is useful if the opponent already has pressure, but the surge
            # plan should not tap out for Jace before presenting a body.
            return 44.0 + 10.0 * opp_overlords - (26.0 if own_overlords == 0 else 0.0)
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            if _targets_own_spell(obs, action):
                return -900.0
            target = str(action.params.get("target_card", ""))
            if target in {CARD_COUNTERSPELL, CARD_FORCE}:
                # Stack-fight protection is the main delta from threat_pressure.
                return 178.0 if card == CARD_COUNTERSPELL else 156.0
            if target == CARD_JACE:
                return 132.0
            if target == CARD_OVERLORD:
                return 112.0 if own_life > max(2.0, 0.08 * starting_life) else 80.0
            return 8.0
        return 0.0
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        target = str(action.params.get("target_player", ""))
        if mode == "ultimate":
            return 1000.0 if target == "opponent" else -1000.0
        if mode == "minus1":
            if action.params.get("target_player") == "opponent":
                return 112.0 + 22.0 * opp_ready_overlords + 6.0 * opp_overlords
            return 5.0
        if mode == "plus2":
            return 58.0 if target == "opponent" else 18.0
        if mode == "zero":
            if own_library < 15:
                return -850.0
            return 8.0 - max(0, own_hand_size - 4) * 2.0
        return 0.0
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        lethalish = own_life <= OVERLORD_POWER * max(1, opp_ready_overlords)
        return (82.0 if lethalish else 36.0) * block_player + 20.0 * block_jace
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            overlord_discard = 0.8 if own_overlords <= 1 else (8.5 if own_library <= 10 else 3.5)
            values = {CARD_JACE: 10.0, CARD_COUNTERSPELL: 6.8, CARD_FORCE: 4.5, CARD_ISLAND: 2.2, CARD_OVERLORD: overlord_discard}
            return values.get(card, 0.0)
        if effect == "force_pitch":
            values = {CARD_JACE: 9.0, CARD_COUNTERSPELL: 5.5, CARD_OVERLORD: 2.5, CARD_FORCE: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_OVERLORD, CARD_FORCE, CARD_COUNTERSPELL}
            return 5.0 if (put == "leave" and business) or (put == "bottom" and not business) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_JACE: 6.0, CARD_ISLAND: 3.0, CARD_COUNTERSPELL: 2.0, CARD_FORCE: 1.5, CARD_OVERLORD: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "old" else 3.0
        return 0.0
    return 0.0

def _counter_guard_public_score(obs: Dict[str, object], action: Action) -> float:
    """Counter profile with explicit closure and library guards.

    rev0064 showed that the old counter-wall edge collapsed against the guarded
    ``threat_closure`` pilot.  This profile is not a new oracle; it is a public-
    information-only response policy that fixes the obvious counter-side mistakes
    before deciding the counter shell is dead: protect library buffer, counter only
    high-value public spells, and turn Jace into a tempo/ultimate plan rather than
    a low-library Brainstorm engine.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    starting_life = float(obs.get("starting_life", 20) or 20)
    own_life = float(public_self.get("life", starting_life) or starting_life)
    opp_life = float(public_opp.get("life", starting_life) or starting_life)
    own_library = int(obs.get("own_library_count", public_self.get("library_count", 0)) or 0)
    own_hand = obs.get("own_hand") if isinstance(obs.get("own_hand"), dict) else {}
    own_hand_size = int(public_self.get("hand_count", sum(int(v or 0) for v in own_hand.values())) or 0)
    own_jace = public_self.get("jace_loyalty")
    opp_jace = public_opp.get("jace_loyalty")
    own_ready_overlords = int(public_self.get("overlord_ready", 0) or 0)
    own_overlords = own_ready_overlords + int(public_self.get("overlord_sick", 0) or 0) + int(public_self.get("overlord_tapped", 0) or 0)
    opp_ready_overlords = int(public_opp.get("overlord_ready", 0) or 0)
    opp_overlords = opp_ready_overlords + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)
    untapped = int(public_self.get("islands_untapped", 0) or 0)

    if action.kind == "PLAY_ISLAND":
        return 130.0
    if action.kind == "PASS":
        if frame == "RESPONSE":
            return 12.0
        if frame == "ATTACK":
            return 10.0
        # Draw-go is a real counter plan, especially with untapped Islands.
        return 18.0 + min(8.0, 0.6 * untapped)
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            if _targets_own_spell(obs, action):
                return -875.0
            target = str(action.params.get("target_card", ""))
            target_value = {
                CARD_OVERLORD: 130.0,
                CARD_JACE: 95.0,
                CARD_COUNTERSPELL: 40.0,
                CARD_FORCE: 35.0,
            }.get(target, 8.0)
            if card == CARD_COUNTERSPELL:
                # Prefer hard counter over Force when both are legal.
                return target_value + 15.0
            pitch = str(action.params.get("pitch_card", action.params.get("pitch", "")))
            pitch_penalty = {
                CARD_OVERLORD: 8.0,
                CARD_JACE: 14.0,
                CARD_FORCE: 18.0,
                CARD_COUNTERSPELL: 22.0,
            }.get(pitch, 12.0)
            life_penalty = 35.0 if own_life <= max(2.0, 0.08 * starting_life) else 4.0 * max(0.0, 1.0 - own_life / max(1.0, starting_life))
            return target_value - pitch_penalty - life_penalty
        if card == CARD_JACE:
            if own_jace is not None:
                return -80.0
            # A resolved Jace is the counter deck's real proactive plan, but do not
            # tap out into ready lethal pressure unless life is still buffered.
            board_penalty = 10.0 * opp_ready_overlords + 3.0 * opp_overlords
            life_pressure = max(0.0, 1.0 - own_life / max(1.0, starting_life))
            return 78.0 - board_penalty - 18.0 * life_pressure
        if card == CARD_OVERLORD:
            if own_library < 3:
                return -500.0
            # The counter deck's singleton Overlord is a finisher, not a churn engine.
            mode = str(action.params.get("mode", "full_cost"))
            base = 42.0 if mode == "full_cost" else 30.0
            if opp_life <= OVERLORD_POWER * max(1, own_ready_overlords + 1):
                base += 18.0
            if own_library <= 8:
                base -= 10.0 * (9 - own_library)
            return base
        return 0.0
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        target = str(action.params.get("target_player", ""))
        if mode == "ultimate":
            return 1000.0 if target == "opponent" else -1000.0
        if mode == "minus1":
            # Bounce ready attackers first; this is the cleanest anti-closure tempo.
            if action.params.get("target_player") == "opponent":
                return 170.0 + 25.0 * opp_ready_overlords + 8.0 * opp_overlords
            return 5.0
        if mode == "plus2":
            # Fateseal the threat pilot when possible; self +2 is fallback loyalty.
            return 105.0 if target == "opponent" else 24.0
        if mode == "zero":
            if own_library < 7:
                return -800.0
            # Brainstorm is allowed as a reload when hand is depleted, but it is no
            # longer a default low-library churn action.
            return 34.0 - 4.0 * max(0, own_hand_size - 4) - 3.0 * max(0, 12 - own_library)
        return 0.0
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        attackers = to_player + to_jace
        if attackers <= 0:
            return 0.0
        draw_cost = 2 * attackers
        if own_library < draw_cost:
            return -900.0 - attackers
        damage = OVERLORD_POWER * to_player
        score = 18.0 + 12.0 * to_jace + 10.0 * damage - 0.8 * draw_cost
        if damage >= opp_life:
            score += 420.0 - 4.0 * attackers
        if own_library - draw_cost <= 5:
            score -= 20.0 * (6 - (own_library - draw_cost))
        return score
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        lethalish = own_life <= OVERLORD_POWER * max(1, opp_ready_overlords)
        return (80.0 if lethalish else 38.0) * block_player + 20.0 * block_jace
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            # Higher score means more willing to discard.  Preserve counters/Jace,
            # throw away redundant mana and the singleton Overlord if it is not the
            # immediate plan.
            island_count = int(own_hand.get(CARD_ISLAND, 0) or 0)
            values = {
                CARD_ISLAND: 8.0 if island_count >= 3 else 4.0,
                CARD_OVERLORD: 6.0,
                CARD_FORCE: 2.0,
                CARD_JACE: 1.5,
                CARD_COUNTERSPELL: 1.0,
            }
            return values.get(card, 0.0)
        if effect == "force_pitch":
            values = {CARD_OVERLORD: 9.0, CARD_JACE: 5.5, CARD_FORCE: 3.0, CARD_COUNTERSPELL: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            target_player = pending.get("target_player", action.params.get("target_player"))
            try:
                target_player_int = int(target_player)
            except (TypeError, ValueError):
                target_player_int = -1
            viewer = int(obs.get("player", 0) or 0)
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_OVERLORD, CARD_JACE, CARD_FORCE, CARD_COUNTERSPELL}
            if target_player_int == viewer:
                return 8.0 if (put == "leave" and business) or (put == "bottom" and seen == CARD_ISLAND) else 1.0
            return 8.0 if (put == "bottom" and business) or (put == "leave" and seen == CARD_ISLAND) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_ISLAND: 5.0, CARD_OVERLORD: 4.0, CARD_JACE: 2.0, CARD_FORCE: 1.2, CARD_COUNTERSPELL: 0.6}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 5.0 if action.params.get("keep") == "old" else 3.0
        return 0.0
    return 0.0


def _counter_life20_stabilizer_public_score(obs: Dict[str, object], action: Action) -> float:
    """Targeted public counter profile for the rev0082 deficient fine cell.

    The rev0082 rescue envelope identified one upper-bound-impossible cell for
    the current two-policy counter set: 40-card counter shell, life 20, against
    the library-aware closure threat.  This profile is deliberately narrow and
    public-information-only.  It tests whether a more defensive life-20 counter
    style can repair that cell before we spend another broad complete-panel run:
    counter Overlord/Jace, keep mana up, use Jace mostly as removal/lock, avoid
    voluntary library churn, and block face damage more aggressively than the
    ordinary ``counter_guard``.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    starting_life = float(obs.get("starting_life", 20) or 20)
    own_life = float(public_self.get("life", starting_life) or starting_life)
    opp_life = float(public_opp.get("life", starting_life) or starting_life)
    own_library = int(obs.get("own_library_count", public_self.get("library_count", 0)) or 0)
    own_hand = obs.get("own_hand") if isinstance(obs.get("own_hand"), dict) else {}
    own_hand_size = int(public_self.get("hand_count", sum(int(v or 0) for v in own_hand.values())) or 0)
    own_jace = public_self.get("jace_loyalty")
    opp_jace = public_opp.get("jace_loyalty")
    own_ready_overlords = int(public_self.get("overlord_ready", 0) or 0)
    opp_ready_overlords = int(public_opp.get("overlord_ready", 0) or 0)
    opp_overlords = opp_ready_overlords + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)
    untapped = int(public_self.get("islands_untapped", 0) or 0)
    life_pressure = max(0.0, 1.0 - own_life / max(1.0, starting_life))

    if action.kind == "PLAY_ISLAND":
        return 140.0
    if action.kind == "PASS":
        if frame == "RESPONSE":
            # Passing stack interaction is acceptable only when no public high-value
            # spell is available to counter.
            return 9.0
        if frame == "ATTACK":
            return 12.0
        # In the deficient life-20 cell, tapping out too early often matters more
        # than developing a slow engine.  Reward draw-go, especially with counter
        # mana up and pressure on board.
        return 30.0 + 1.2 * untapped + 8.0 * opp_overlords + 15.0 * life_pressure
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            if _targets_own_spell(obs, action):
                return -900.0
            target = str(action.params.get("target_card", ""))
            if target == CARD_OVERLORD:
                target_value = 175.0 + 30.0 * life_pressure
            elif target == CARD_JACE:
                target_value = 120.0
            elif target in {CARD_COUNTERSPELL, CARD_FORCE}:
                # Fight only stack battles that protect Jace/tempo, not every random
                # exchange.  This keeps interaction for the next Overlord.
                target_value = 34.0
            else:
                target_value = 6.0
            if card == CARD_COUNTERSPELL:
                return target_value + 20.0
            pitch = str(action.params.get("pitch_card", action.params.get("pitch", "")))
            pitch_penalty = {
                CARD_OVERLORD: 5.0,
                CARD_JACE: 20.0,
                CARD_FORCE: 22.0,
                CARD_COUNTERSPELL: 26.0,
            }.get(pitch, 14.0)
            fatal_life_penalty = 80.0 if own_life <= 1 else (28.0 if own_life <= 3 else 5.0 * life_pressure)
            return target_value - pitch_penalty - fatal_life_penalty
        if card == CARD_JACE:
            if own_jace is not None:
                return -90.0
            # Cast Jace as a stabilizer when a bounce/fateseal plan is needed, but
            # avoid tapping out into ready lethal pressure in the fragile life-20 cell.
            if opp_ready_overlords > 0 and untapped < 4:
                return 18.0 - 20.0 * life_pressure
            return 58.0 - 7.0 * opp_overlords - 20.0 * life_pressure
        if card == CARD_OVERLORD:
            if own_library < 6:
                return -600.0
            # Singleton Overlord is almost never the repair for this cell.  Use it
            # only as an already-safe close, not as another draw trigger into death.
            mode = str(action.params.get("mode", "full_cost"))
            base = 24.0 if mode == "full_cost" else 12.0
            if own_ready_overlords > 0 and OVERLORD_POWER * own_ready_overlords >= opp_life:
                base += 60.0
            return base - 12.0 * life_pressure - max(0, 10 - own_library) * 8.0
        return 0.0
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        target = str(action.params.get("target_player", ""))
        if mode == "ultimate":
            return 1000.0 if target == "opponent" else -1000.0
        if mode == "minus1":
            if action.params.get("target_player") == "opponent":
                return 210.0 + 45.0 * opp_ready_overlords + 18.0 * opp_overlords + 20.0 * life_pressure
            return 4.0
        if mode == "plus2":
            return 120.0 if target == "opponent" else 20.0
        if mode == "zero":
            if own_library < 12:
                return -850.0
            return 14.0 - 5.0 * max(0, own_hand_size - 4) - 5.0 * life_pressure
        return 0.0
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        attackers = to_player + to_jace
        if attackers <= 0:
            return 0.0
        draw_cost = 2 * attackers
        if own_library < draw_cost:
            return -950.0 - attackers
        damage = OVERLORD_POWER * to_player
        score = 8.0 + 14.0 * to_jace + 8.0 * damage - 1.5 * draw_cost
        if damage >= opp_life:
            score += 480.0 - 5.0 * attackers
        if own_library - draw_cost <= 7:
            score -= 25.0 * (8 - (own_library - draw_cost))
        return score
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        lethalish = own_life <= OVERLORD_POWER * max(1, opp_ready_overlords)
        return (110.0 if lethalish else 64.0 + 30.0 * life_pressure) * block_player + 18.0 * block_jace
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            island_count = int(own_hand.get(CARD_ISLAND, 0) or 0)
            values = {
                CARD_ISLAND: 8.5 if island_count >= 4 else 3.5,
                CARD_OVERLORD: 9.0,
                CARD_FORCE: 2.5,
                CARD_JACE: 2.0,
                CARD_COUNTERSPELL: 1.0,
            }
            return values.get(card, 0.0)
        if effect == "force_pitch":
            values = {CARD_OVERLORD: 10.0, CARD_JACE: 6.0, CARD_FORCE: 3.0, CARD_COUNTERSPELL: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            target_player = pending.get("target_player", action.params.get("target_player"))
            try:
                target_player_int = int(target_player)
            except (TypeError, ValueError):
                target_player_int = -1
            viewer = int(obs.get("player", 0) or 0)
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_OVERLORD, CARD_JACE, CARD_FORCE, CARD_COUNTERSPELL}
            if target_player_int == viewer:
                return 8.0 if (put == "leave" and business) or (put == "bottom" and seen == CARD_ISLAND) else 1.0
            return 10.0 if (put == "bottom" and business) or (put == "leave" and seen == CARD_ISLAND) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_ISLAND: 5.5, CARD_OVERLORD: 4.5, CARD_JACE: 2.5, CARD_FORCE: 1.4, CARD_COUNTERSPELL: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 5.0 if action.params.get("keep") == "old" else 3.0
        return 0.0
    return 0.0

def _stall_public_score(obs: Dict[str, object], action: Action) -> float:
    """Adversarial public policy for reward/truncation testing.

    This is deliberately not a good Magic player. It plays Islands, refuses to
    advance its own win condition, counters public threats when possible, blocks
    to prolong the game, and prefers PASS otherwise.  Its purpose is to expose
    whether draw-half reporting, max-decision truncation, or tournament gates can
    be exploited by non-winning behavior.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    starting_life = float(obs.get("starting_life", 20) or 20)
    own_life = float(public_self.get("life", starting_life) or starting_life)

    if action.kind == "PLAY_ISLAND":
        return 100.0
    if action.kind == "PASS":
        return 30.0 if frame in {"MAIN", "RESPONSE"} else 10.0
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        target = str(action.params.get("target_card", ""))
        if card in {CARD_COUNTERSPELL, CARD_FORCE}:
            # Stall cares about preventing public engines/threats, not fighting
            # every stack object.  Force is discounted when life is low or pitch
            # cost is expensive.
            base = 80.0 if target in {CARD_JACE, CARD_OVERLORD} else 15.0
            if card == CARD_FORCE:
                pitch = str(action.params.get("pitch_card", ""))
                pitch_penalty = {CARD_FORCE: 8.0, CARD_JACE: 6.0, CARD_OVERLORD: 6.0, CARD_COUNTERSPELL: 4.0}.get(pitch, 5.0)
                life_penalty = 12.0 if own_life <= max(2.0, 0.10 * starting_life) else 0.0
                return base - pitch_penalty - life_penalty
            return base
        # Do not proactively cast Jace or Overlord; the point is to test stall.
        return -100.0
    if action.kind == "ATTACK":
        return -100.0
    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        return 60.0 * block_player + 30.0 * block_jace
    if action.kind == "ACTIVATE_JACE":
        # A resolved Jace is not part of the stall plan, but if it exists, use
        # low-risk loyalty rather than winning quickly. This keeps the policy
        # intentionally adversarial for truncation tests.
        mode = str(action.params.get("mode", ""))
        return {"plus2": 20.0, "zero": 8.0, "minus1": 35.0, "ultimate": -50.0}.get(mode, 0.0)
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            # Throw away proactive threats first; preserve Islands/counters.
            values = {CARD_OVERLORD: 10.0, CARD_JACE: 9.0, CARD_FORCE: 4.0, CARD_COUNTERSPELL: 3.0, CARD_ISLAND: 1.0}
            return values.get(card, 0.0)
        if effect == "force_pitch":
            # Prefer pitching proactive cards, preserve Counterspell when possible.
            values = {CARD_OVERLORD: 8.0, CARD_JACE: 7.0, CARD_FORCE: 4.0, CARD_COUNTERSPELL: 1.0}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            # If somehow using Jace +2, bottom opponent business / keep own blanks.
            pending = obs.get("pending_choice_data", {}) or {}
            target = int(pending.get("target_player", action.params.get("target_player", 0)) or 0)
            viewer = int(obs.get("player", 0) or 0)
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            put = str(action.params.get("put", ""))
            business = seen in {CARD_JACE, CARD_OVERLORD, CARD_FORCE, CARD_COUNTERSPELL}
            if target == viewer:
                return 5.0 if (put == "leave" and seen == CARD_ISLAND) or (put == "bottom" and business) else 1.0
            return 5.0 if (put == "bottom" and business) or (put == "leave" and seen == CARD_ISLAND) else 1.0
        return 0.0
    return 0.0

def _base_public_score(obs: Dict[str, object], action: Action) -> float:
    """Small public-info baseline scorer, duplicated to avoid state leakage.

    It is deliberately rough. It should be good enough to create non-random
    games and bad enough that future oracles/evolution have something to beat.
    """

    frame = str(obs.get("frame", "MAIN"))
    public_self = _public_zone(obs, "public_self")
    public_opp = _public_zone(obs, "public_opponent")
    starting_life = float(obs.get("starting_life", 20) or 20)
    own_life = float(public_self.get("life", starting_life) or starting_life)
    opp_life = float(public_opp.get("life", starting_life) or starting_life)
    untapped = int(public_self.get("islands_untapped", 0) or 0)
    opp_jace = public_opp.get("jace_loyalty")
    own_jace = public_self.get("jace_loyalty")
    opp_overlords = int(public_opp.get("overlord_ready", 0) or 0) + int(public_opp.get("overlord_sick", 0) or 0) + int(public_opp.get("overlord_tapped", 0) or 0)
    own_overlords = int(public_self.get("overlord_ready", 0) or 0) + int(public_self.get("overlord_sick", 0) or 0) + int(public_self.get("overlord_tapped", 0) or 0)

    if action.kind == "PASS":
        if frame == "MAIN":
            return 1.0 + min(3.0, untapped * 0.15)
        if frame == "RESPONSE":
            return 0.5
        return 0.0

    if action.kind == "PLAY_ISLAND":
        return 9.0

    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card == CARD_COUNTERSPELL:
            target = str(action.params.get("target_card", ""))
            return 11.0 if target in {CARD_JACE, CARD_OVERLORD} else 7.0
        if card == CARD_FORCE:
            target = str(action.params.get("target_card", ""))
            pitch = str(action.params.get("pitch_card", action.params.get("pitch", "")))
            life_pressure = max(0.0, 1.0 - own_life / max(1.0, starting_life))
            pitch_penalty = {CARD_FORCE: 3.0, CARD_JACE: 2.5, CARD_OVERLORD: 2.0, CARD_COUNTERSPELL: 1.2}.get(pitch, 1.5)
            return (12.0 if target in {CARD_JACE, CARD_OVERLORD} else 6.5) - pitch_penalty - 2.0 * life_pressure
        if card == CARD_JACE:
            # Jace is better when not already present and when board pressure is low.
            return 7.0 - (2.0 if own_jace is not None else 0.0) - 1.2 * opp_overlords
        if card == CARD_OVERLORD:
            mode = str(action.params.get("mode", "normal"))
            face_pressure = 1.0 - (opp_life / max(1.0, starting_life))
            return (6.0 if mode == "impending" else 6.8) + 2.0 * face_pressure - (1.0 if opp_jace is not None else 0.0)
        return 0.0

    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        if mode == "minus1":
            target_state = str(action.params.get("target_state", ""))
            return 10.0 if target_state in {"ready", "tapped"} else 8.0
        if mode == "ultimate":
            return 100.0
        if mode == "zero":
            return 6.0
        if mode == "plus2":
            return 5.0 if own_overlords == 0 else 4.0
        return 0.0

    if action.kind == "ATTACK":
        to_jace = int(action.params.get("to_jace", 0) or 0)
        to_player = int(action.params.get("to_player", 0) or 0)
        return 5.0 * to_jace + (4.0 + (2.0 if starting_life <= 20 else 0.5)) * to_player

    if action.kind == "BLOCK":
        block_player = int(action.params.get("block_player_attackers", action.params.get("block_player", 0)) or 0)
        block_jace = int(action.params.get("block_jace_attackers", action.params.get("block_jace", 0)) or 0)
        if own_life <= max(5.0, 0.25 * starting_life):
            return 5.0 * block_player + 3.0 * block_jace
        return 3.5 * block_jace + 2.0 * block_player

    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        card = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            values = {CARD_ISLAND: 0.5, CARD_OVERLORD: 2.0, CARD_JACE: 2.6, CARD_FORCE: 3.0, CARD_COUNTERSPELL: 2.5}
            return 6.0 - values.get(card, 1.0)
        if effect == "force_pitch":
            values = {CARD_COUNTERSPELL: 4.0, CARD_OVERLORD: 3.0, CARD_JACE: 2.0, CARD_FORCE: 1.5}
            return values.get(card, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            seen = str(pending.get("seen_top_card", action.params.get("seen_card", "")))
            target = int(pending.get("target_player", action.params.get("target_player", 0)) or 0)
            put = str(action.params.get("put", ""))
            viewer = int(obs.get("player", 0) or 0)
            good_for_target = seen in {CARD_JACE, CARD_OVERLORD, CARD_FORCE, CARD_COUNTERSPELL}
            if target == viewer:
                return 4.0 if (put == "leave" and good_for_target) or (put == "bottom" and seen == CARD_ISLAND) else 1.0
            return 4.0 if (put == "bottom" and good_for_target) or (put == "leave" and seen == CARD_ISLAND) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            putback_value = {CARD_ISLAND: 4.0, CARD_OVERLORD: 2.5, CARD_JACE: 2.0, CARD_FORCE: 1.0, CARD_COUNTERSPELL: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "new" else 3.0
        return 0.0

    return 0.0


def make_public_agent(name: str) -> PublicDecisionAgent:
    normalized = name.strip().lower().replace("-", "_")
    if normalized.startswith("code_"):
        from .code_policy import make_code_policy_agent
        return make_code_policy_agent(normalized)
    if normalized in {"random", "public_random", "public_random_rev0009"}:
        return PublicRandomAgent()
    if normalized in {"legacy_heuristic", "public_legacy_heuristic", "public_heuristic_rev0009_exact"}:
        return PublicHeuristicAgent()
    if normalized in {"heuristic", "balanced", "public_heuristic", "public_heuristic_rev0009"}:
        return PublicProfileAgent("heuristic")
    if normalized in {"counter_happy", "counterhappy", "public_counter_happy"}:
        return PublicProfileAgent("counter_happy")
    if normalized in {"threat_rush", "threatrush", "public_threat_rush"}:
        return PublicProfileAgent("threat_rush")
    if normalized in {"threat_closure", "threat_guard", "threat_lethal_guard", "public_threat_closure"}:
        return PublicProfileAgent("threat_closure")
    if normalized in {"threat_pressure", "threat_response", "threat_jace_pressure", "threat_counter_guard_response", "public_threat_pressure"}:
        return PublicProfileAgent("threat_pressure")
    if normalized in {"threat_surge", "threat_protect", "threat_counterpressure", "threat_face_surge", "public_threat_surge"}:
        return PublicProfileAgent("threat_surge")
    if normalized in {"counter_guard", "counter_closure", "counter_survival", "public_counter_guard"}:
        return PublicProfileAgent("counter_guard")
    if normalized in {"counter_life20_stabilizer", "counter_stabilizer", "counter_low_life_closure_guard", "public_counter_life20_stabilizer"}:
        return PublicProfileAgent("counter_life20_stabilizer")
    if normalized in {"patient", "draw_go", "control"}:
        return PublicProfileAgent("patient")
    if normalized in {"stall", "turtle", "draw_adversary", "public_stall", "public_stall_rev0015"}:
        return PublicProfileAgent("stall")
    info_aliases = {
        "infostate_heuristic": "heuristic",
        "info_heuristic": "heuristic",
        "public_infostate_heuristic_rev0092": "heuristic",
        "infostate_counter_guard": "counter_guard",
        "info_counter_guard": "counter_guard",
        "public_infostate_counter_guard_rev0092": "counter_guard",
        "infostate_threat_closure": "threat_closure",
        "info_threat_closure": "threat_closure",
        "public_infostate_threat_closure_rev0092": "threat_closure",
        "infostate_threat_pressure": "threat_pressure",
        "info_threat_pressure": "threat_pressure",
        "public_infostate_threat_pressure_rev0092": "threat_pressure",
        "infostate_threat_surge": "threat_surge",
        "info_threat_surge": "threat_surge",
        "public_infostate_threat_surge_rev0092": "threat_surge",
    }
    if normalized in info_aliases:
        return PublicInformationStateAgent(info_aliases[normalized])
    if normalized in {"linear_ranker_rev0021", "ranker_rev0021", "action_ranker_rev0021"}:
        from .ranker_policy import load_default_linear_ranker_agent
        return load_default_linear_ranker_agent()
    if normalized in {"ranker_blend_threat_rev0022", "ranker_threat_rev0022", "ranker_blend_threat_rush_rev0022"}:
        from .ranker_policy import load_default_blended_ranker_agent
        return load_default_blended_ranker_agent("threat_rush")
    if normalized in {"ranker_blend_counter_rev0022", "ranker_counter_rev0022", "ranker_blend_counter_happy_rev0022"}:
        from .ranker_policy import load_default_blended_ranker_agent
        return load_default_blended_ranker_agent("counter_happy")
    if normalized in {"ranker_blend_patient_rev0022", "ranker_patient_rev0022", "ranker_blend_control_rev0022"}:
        from .ranker_policy import load_default_blended_ranker_agent
        return load_default_blended_ranker_agent("patient")
    if normalized in {"mlp_ranker_rev0023", "mlp_action_ranker_rev0023", "mlp_ranker"}:
        from .ranker_policy import load_default_mlp_ranker_agent
        return load_default_mlp_ranker_agent()
    if normalized in {"mlp_ranker_blend_threat_rev0023", "mlp_blend_threat_rev0023", "mlp_ranker_blend_threat_rush_rev0023"}:
        from .ranker_policy import load_default_blended_mlp_ranker_agent
        return load_default_blended_mlp_ranker_agent("threat_rush")
    if normalized in {"mlp_ranker_blend_counter_rev0023", "mlp_blend_counter_rev0023", "mlp_ranker_blend_counter_happy_rev0023"}:
        from .ranker_policy import load_default_blended_mlp_ranker_agent
        return load_default_blended_mlp_ranker_agent("counter_happy")
    if normalized in {"mlp_ranker_blend_patient_rev0023", "mlp_blend_patient_rev0023", "mlp_ranker_blend_control_rev0023"}:
        from .ranker_policy import load_default_blended_mlp_ranker_agent
        return load_default_blended_mlp_ranker_agent("patient")
    if normalized in {"outcome_linear_ranker_rev0025", "outcome_ranker_rev0025", "outcome_weighted_ranker_rev0025"}:
        from .ranker_policy import load_default_outcome_ranker_agent
        return load_default_outcome_ranker_agent()
    if normalized in {"outcome_ranker_blend_threat_rev0025", "outcome_blend_threat_rev0025", "outcome_ranker_blend_threat_rush_rev0025"}:
        from .ranker_policy import load_default_blended_outcome_ranker_agent
        return load_default_blended_outcome_ranker_agent("threat_rush")
    if normalized in {"outcome_ranker_blend_counter_rev0025", "outcome_blend_counter_rev0025", "outcome_ranker_blend_counter_happy_rev0025"}:
        from .ranker_policy import load_default_blended_outcome_ranker_agent
        return load_default_blended_outcome_ranker_agent("counter_happy")
    if normalized in {"outcome_ranker_blend_patient_rev0025", "outcome_blend_patient_rev0025", "outcome_ranker_blend_control_rev0025"}:
        from .ranker_policy import load_default_blended_outcome_ranker_agent
        return load_default_blended_outcome_ranker_agent("patient")
    if normalized in {"counterfactual_linear_ranker_rev0033", "counterfactual_ranker_rev0033", "action_counterfactual_ranker_rev0033"}:
        from .ranker_policy import load_default_counterfactual_ranker_agent
        return load_default_counterfactual_ranker_agent()
    if normalized in {"counterfactual_ranker_blend_threat_rev0033", "counterfactual_blend_threat_rev0033", "counterfactual_ranker_blend_threat_rush_rev0033"}:
        from .ranker_policy import load_default_blended_counterfactual_ranker_agent
        return load_default_blended_counterfactual_ranker_agent("threat_rush")
    if normalized in {"counterfactual_ranker_blend_counter_rev0033", "counterfactual_blend_counter_rev0033", "counterfactual_ranker_blend_counter_happy_rev0033"}:
        from .ranker_policy import load_default_blended_counterfactual_ranker_agent
        return load_default_blended_counterfactual_ranker_agent("counter_happy")
    if normalized in {"counterfactual_ranker_blend_patient_rev0033", "counterfactual_blend_patient_rev0033", "counterfactual_ranker_blend_control_rev0033"}:
        from .ranker_policy import load_default_blended_counterfactual_ranker_agent
        return load_default_blended_counterfactual_ranker_agent("patient")
    if normalized in {"counterfactual_linear_ranker_rev0034", "counterfactual_ranker_rev0034", "action_counterfactual_ranker_rev0034"}:
        from .ranker_policy import load_counterfactual_ranker_agent
        return load_counterfactual_ranker_agent("rev0034", name="counterfactual_linear_ranker_rev0034")
    if normalized in {"counterfactual_ranker_blend_threat_rev0034", "counterfactual_blend_threat_rev0034", "counterfactual_ranker_blend_threat_rush_rev0034"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0034", "threat_rush", name="counterfactual_ranker_blend_threat_rev0034")
    if normalized in {"counterfactual_ranker_blend_counter_rev0034", "counterfactual_blend_counter_rev0034", "counterfactual_ranker_blend_counter_happy_rev0034"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0034", "counter_happy", name="counterfactual_ranker_blend_counter_rev0034")
    if normalized in {"counterfactual_ranker_blend_patient_rev0034", "counterfactual_blend_patient_rev0034", "counterfactual_ranker_blend_control_rev0034"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0034", "patient", name="counterfactual_ranker_blend_patient_rev0034")
    if normalized in {"counterfactual_linear_ranker_rev0035", "counterfactual_ranker_rev0035", "budgeted_counterfactual_ranker_rev0035"}:
        from .ranker_policy import load_counterfactual_ranker_agent
        return load_counterfactual_ranker_agent("rev0035", name="counterfactual_linear_ranker_rev0035")
    if normalized in {"counterfactual_ranker_blend_threat_rev0035", "counterfactual_blend_threat_rev0035", "budgeted_counterfactual_ranker_blend_threat_rev0035"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0035", "threat_rush", name="counterfactual_ranker_blend_threat_rev0035")
    if normalized in {"counterfactual_ranker_blend_counter_rev0035", "counterfactual_blend_counter_rev0035", "budgeted_counterfactual_ranker_blend_counter_rev0035"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0035", "counter_happy", name="counterfactual_ranker_blend_counter_rev0035")
    if normalized in {"counterfactual_ranker_blend_patient_rev0035", "counterfactual_blend_patient_rev0035", "budgeted_counterfactual_ranker_blend_patient_rev0035"}:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        return load_blended_counterfactual_ranker_agent("rev0035", "patient", name="counterfactual_ranker_blend_patient_rev0035")

    # Generic counterfactual-ranker aliases for future revisions.  This keeps
    # each new offline action-counterfactual model from requiring a hard-coded
    # factory block as long as it follows the standard JSON path:
    # data/<rev>_counterfactual_action_ranker_model.json.
    match = re.fullmatch(r"(?:counterfactual_linear_ranker|counterfactual_ranker|action_counterfactual_ranker|adaptive_counterfactual_ranker)_(rev\d{4})", normalized)
    if match:
        from .ranker_policy import load_counterfactual_ranker_agent
        rev = match.group(1)
        return load_counterfactual_ranker_agent(rev, name=f"counterfactual_linear_ranker_{rev}")
    match = re.fullmatch(r"(?:counterfactual_ranker_blend|counterfactual_blend|adaptive_counterfactual_ranker_blend)_(threat|threat_rush|counter|counter_happy|patient|control)_(rev\d{4})", normalized)
    if match:
        from .ranker_policy import load_blended_counterfactual_ranker_agent
        raw_profile, rev = match.group(1), match.group(2)
        profile = {"threat": "threat_rush", "threat_rush": "threat_rush", "counter": "counter_happy", "counter_happy": "counter_happy", "patient": "patient", "control": "patient"}[raw_profile]
        short = {"threat_rush": "threat", "counter_happy": "counter", "patient": "patient"}[profile]
        return load_blended_counterfactual_ranker_agent(rev, profile, name=f"counterfactual_ranker_blend_{short}_{rev}")
    match = re.fullmatch(r"learned_response_rev0097_g[01]_\d{2}", normalized)
    if match:
        from .learned_response_oracle import load_learned_response_agent
        return load_learned_response_agent(normalized)

    raise ValueError("unknown public agent name {!r}".format(name))
