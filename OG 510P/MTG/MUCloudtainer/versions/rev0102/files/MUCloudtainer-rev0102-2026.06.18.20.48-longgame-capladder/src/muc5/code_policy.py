from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

from .action_schema import Action
from .cards import (
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
    OVERLORD_POWER,
)
from .decision import DecisionFrame, PublicDecisionAgent

ScoreFn = Callable[[Mapping[str, object], Action], float]


def _public_zone(obs: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = obs.get(key)
    return value if isinstance(value, Mapping) else {}


def _own_hand(obs: Mapping[str, object]) -> Mapping[str, int]:
    value = obs.get("own_hand")
    return value if isinstance(value, Mapping) else {}


def _hand_count(obs: Mapping[str, object], card: str) -> int:
    return int(_own_hand(obs).get(card, 0) or 0)


def _frame(obs: Mapping[str, object]) -> str:
    return str(obs.get("frame", "MAIN"))


def _starting_life(obs: Mapping[str, object]) -> float:
    return float(obs.get("starting_life", 20) or 20)


def _life(obs: Mapping[str, object], who: str) -> float:
    zone = _public_zone(obs, "public_self" if who == "self" else "public_opponent")
    return float(zone.get("life", _starting_life(obs)) or _starting_life(obs))


def _untapped(obs: Mapping[str, object], who: str = "self") -> int:
    zone = _public_zone(obs, "public_self" if who == "self" else "public_opponent")
    return int(zone.get("islands_untapped", 0) or 0)


def _jace_loyalty(obs: Mapping[str, object], who: str) -> int | None:
    zone = _public_zone(obs, "public_self" if who == "self" else "public_opponent")
    value = zone.get("jace_loyalty")
    return None if value is None else int(value)


def _overlord_count(obs: Mapping[str, object], who: str, *, include_tapped: bool = True) -> int:
    zone = _public_zone(obs, "public_self" if who == "self" else "public_opponent")
    total = int(zone.get("overlord_ready", 0) or 0) + int(zone.get("overlord_sick", 0) or 0)
    if include_tapped:
        total += int(zone.get("overlord_tapped", 0) or 0)
    return total


def _base_material_score(obs: Mapping[str, object], action: Action) -> float:
    """Small shared prior for readable code policies.

    This helper is intentionally public-observation only. Code policies should
    compose helpers like this rather than reaching for GameState. It keeps future
    LLM- or human-written policies readable and lintable.
    """

    if action.kind == "PLAY_ISLAND":
        return 8.0
    if action.kind == "PASS":
        return 0.5 + 0.1 * _untapped(obs)
    if action.kind == "CAST":
        card = str(action.params.get("card", ""))
        if card == CARD_JACE:
            return 6.0 - (1.5 if _jace_loyalty(obs, "self") is not None else 0.0) - 1.0 * _overlord_count(obs, "opponent")
        if card == CARD_OVERLORD:
            mode = str(action.params.get("mode", "full_cost"))
            return 6.2 if mode == "impending" else 6.6
        if card == CARD_COUNTERSPELL:
            target = str(action.params.get("target_card", ""))
            return 9.0 if target in {CARD_JACE, CARD_OVERLORD} else 5.0
        if card == CARD_FORCE:
            target = str(action.params.get("target_card", ""))
            pitch = str(action.params.get("pitch_card", action.params.get("pitch", "")))
            pitch_penalty = {CARD_COUNTERSPELL: 1.6, CARD_FORCE: 2.2, CARD_JACE: 2.8, CARD_OVERLORD: 2.5}.get(pitch, 2.0)
            life_fraction = _life(obs, "self") / max(1.0, _starting_life(obs))
            return (10.5 if target in {CARD_JACE, CARD_OVERLORD} else 5.5) - pitch_penalty - 0.8 / max(0.1, life_fraction)
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        if mode == "ultimate":
            return 80.0
        if mode == "minus1":
            return 8.0
        if mode == "zero":
            return 5.5
        if mode == "plus2":
            return 4.0
    if action.kind == "ATTACK":
        return 4.5 * int(action.params.get("to_jace", 0) or 0) + 3.5 * int(action.params.get("to_player", 0) or 0)
    if action.kind == "BLOCK":
        own_life = _life(obs, "self")
        danger = own_life <= max(float(OVERLORD_POWER), 0.25 * _starting_life(obs))
        return (5.5 if danger else 2.5) * int(action.params.get("block_player_attackers", 0) or 0) + 4.5 * int(action.params.get("block_jace_attackers", 0) or 0)
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        discard = str(action.params.get("discard", action.params.get("card", "")))
        if effect in {"discard", "overlord_discard", "cleanup_discard"}:
            discard_preference = {CARD_ISLAND: 5.0, CARD_OVERLORD: 3.4, CARD_JACE: 2.6, CARD_FORCE: 1.8, CARD_COUNTERSPELL: 1.3}
            return discard_preference.get(discard, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "new" else 3.0
    return 0.0


def score_jace_lock(obs: Mapping[str, object], action: Action) -> float:
    """Readable policy: resolve/protect Jace, use Jace as the main win plan."""

    score = _base_material_score(obs, action)
    frame = _frame(obs)
    own_jace = _jace_loyalty(obs, "self")
    opp_jace = _jace_loyalty(obs, "opponent")
    opp_overlords = _overlord_count(obs, "opponent")

    if action.kind == "CAST" and action.params.get("card") == CARD_JACE:
        score += 4.0 if own_jace is None else 0.5
        if _untapped(obs, "opponent") < 2:
            score += 2.0
    if frame == "RESPONSE" and action.kind == "CAST":
        target = str(action.params.get("target_card", ""))
        if target == CARD_JACE:
            score += 5.0
        elif target == CARD_OVERLORD and own_jace is not None:
            score += 3.5
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        if mode == "ultimate":
            score += 100.0
        elif mode == "minus1" and opp_overlords:
            score += 6.0
        elif mode == "plus2" and opp_overlords == 0:
            score += 2.0
        elif mode == "zero" and _hand_count(obs, CARD_ISLAND) >= 2:
            score += 1.0
    if action.kind == "ATTACK":
        if opp_jace is not None:
            score += 6.0 * int(action.params.get("to_jace", 0) or 0)
            score -= 1.0 * int(action.params.get("to_player", 0) or 0)
    if action.kind == "BLOCK" and own_jace is not None:
        score += 3.0 * int(action.params.get("block_jace_attackers", 0) or 0)
    return score


def score_overlord_clock(obs: Mapping[str, object], action: Action) -> float:
    """Readable policy: deploy Overlord pressure and convert life totals to a clock."""

    score = _base_material_score(obs, action)
    frame = _frame(obs)
    starting_life = _starting_life(obs)
    opp_life = _life(obs, "opponent")
    opp_jace = _jace_loyalty(obs, "opponent")
    face_pressure = 1.0 - opp_life / max(1.0, starting_life)

    if action.kind == "CAST" and action.params.get("card") == CARD_OVERLORD:
        mode = str(action.params.get("mode", "full_cost"))
        score += 5.0 if mode == "impending" else 4.0
        if opp_jace is not None and mode != "impending":
            score += 2.5
    if frame == "RESPONSE" and action.kind == "CAST":
        target = str(action.params.get("target_card", ""))
        if target == CARD_JACE:
            score += 4.0
        elif target == CARD_OVERLORD:
            score += 1.5
        else:
            score -= 2.5
    if action.kind == "ATTACK":
        to_player = int(action.params.get("to_player", 0) or 0)
        to_jace = int(action.params.get("to_jace", 0) or 0)
        score += (4.0 + 5.0 * face_pressure + (2.0 if starting_life <= 20 else 0.0)) * to_player
        if opp_jace is not None:
            score += 3.5 * to_jace
    if action.kind == "ACTIVATE_JACE":
        if str(action.params.get("mode", "")) == "zero":
            score += 1.0
        elif str(action.params.get("mode", "")) == "plus2":
            score -= 1.0
    return score


def score_force_conservative(obs: Mapping[str, object], action: Action) -> float:
    """Readable policy: value cards/life highly; use Force only for major threats."""

    score = _base_material_score(obs, action)
    frame = _frame(obs)
    own_life = _life(obs, "self")
    starting_life = _starting_life(obs)
    if frame == "RESPONSE" and action.kind == "PASS":
        score += 2.0
    if action.kind == "CAST" and action.params.get("card") == CARD_FORCE:
        target = str(action.params.get("target_card", ""))
        payment = str(action.params.get("payment", ""))
        if target not in {CARD_JACE, CARD_OVERLORD}:
            score -= 7.0
        if payment != "mana":
            score -= 3.0
            if own_life <= max(2.0, 0.15 * starting_life):
                score -= 20.0
    if action.kind == "CAST" and action.params.get("card") == CARD_COUNTERSPELL:
        score += 1.5
    if action.kind == "CAST" and action.params.get("card") == CARD_JACE:
        score += 1.0 if _untapped(obs) >= 0 else 0.0
    return score


def score_jace_ultimator(obs: Mapping[str, object], action: Action) -> float:
    """Readable policy: force Jace loyalty upward to stress ultimate transitions.

    This is primarily a coverage/test policy, not a strong MUC player. It exists
    so the replay and C++ differential harnesses see Jace ultimate often enough
    to keep RNG/shuffle transport under audit. It uses only the public
    DecisionFrame observation.
    """

    score = _base_material_score(obs, action)
    if action.kind == "PLAY_ISLAND":
        return score + 100.0
    if action.kind == "CAST" and action.params.get("card") == CARD_JACE:
        return score + 90.0
    if action.kind == "CAST" and action.params.get("card") in {CARD_COUNTERSPELL, CARD_FORCE}:
        target = str(action.params.get("target_card", ""))
        return score + (70.0 if target == CARD_JACE else 10.0)
    if action.kind == "ACTIVATE_JACE":
        mode = str(action.params.get("mode", ""))
        if mode == "ultimate":
            return 1000.0
        if mode == "plus2":
            # Prefer fatesealing opponent to create eventual deck-pressure, but
            # self-target is still better than Brainstorm for coverage.
            return 250.0 if action.params.get("target_player") == "opponent" else 200.0
        if mode == "minus1":
            return 30.0
        if mode == "zero":
            return -20.0
    if action.kind == "CHOOSE_FOR_EFFECT":
        effect = str(action.params.get("effect", ""))
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            seen = str(pending.get("seen_top_card", "")) if isinstance(pending, Mapping) else ""
            put = str(action.params.get("put", ""))
            # Bottom opponent business, leave opponent Island; do the inverse if
            # self-targeting happened.
            viewer = int(obs.get("player", 0) or 0)
            target = int(pending.get("target_player", viewer) or viewer) if isinstance(pending, Mapping) else viewer
            business = seen in {CARD_JACE, CARD_OVERLORD, CARD_FORCE, CARD_COUNTERSPELL}
            if target == viewer:
                return 20.0 if (put == "bottom" and seen == CARD_ISLAND) or (put == "leave" and business) else 5.0
            return 20.0 if (put == "bottom" and business) or (put == "leave" and seen == CARD_ISLAND) else 5.0
        if effect == "jace_legend":
            return 12.0 if action.params.get("keep") == "old" else 3.0
    if action.kind == "PASS":
        return 1.0
    return score


BUILTIN_CODE_POLICIES: Dict[str, ScoreFn] = {
    "code_jace_lock_rev0013": score_jace_lock,
    "code_overlord_clock_rev0013": score_overlord_clock,
    "code_force_conservative_rev0013": score_force_conservative,
    "code_jace_ultimator_rev0020": score_jace_ultimator,
}


@dataclass(frozen=True)
class ReadableCodePolicyAgent:
    """A CSRO-style public policy wrapper for human-readable Python score code.

    This is deliberately not a general arbitrary-code loader. The near-term goal
    is to make generated or hand-written policy code inspectable, reproducible,
    and promotion-gated inside the cloudtainer. Future sandpeople can add a new
    score function to ``BUILTIN_CODE_POLICIES`` or load code under a stricter
    sandbox, but tournament code should still pass only ``DecisionFrame``.
    """

    policy_id: str
    score_fn: ScoreFn

    @property
    def name(self) -> str:
        return self.policy_id

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = [(float(self.score_fn(frame.observation, action)), rng.random(), idx) for idx, action in enumerate(frame.legal_actions)]
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]


def make_code_policy_agent(policy_id: str) -> ReadableCodePolicyAgent:
    normalized = policy_id.strip().lower().replace("-", "_")
    if normalized not in BUILTIN_CODE_POLICIES:
        raise ValueError(f"unknown code policy {policy_id!r}; expected one of {sorted(BUILTIN_CODE_POLICIES)}")
    return ReadableCodePolicyAgent(normalized, BUILTIN_CODE_POLICIES[normalized])


def code_policy_catalog() -> List[Dict[str, str]]:
    return [
        {
            "policy_id": "code_jace_lock_rev0013",
            "summary": "Resolve/protect Jace; prioritize Jace ultimate and Jace defense.",
        },
        {
            "policy_id": "code_overlord_clock_rev0013",
            "summary": "Deploy Overlord pressure and convert life totals into a clock.",
        },
        {
            "policy_id": "code_force_conservative_rev0013",
            "summary": "Use Force sparingly; prefer Counterspell and protect life/cards.",
        },
        {
            "policy_id": "code_jace_ultimator_rev0020",
            "summary": "Coverage/test policy that ramps Jace loyalty and exercises Jace ultimate shuffle transitions.",
        },
    ]


def smoke_lint_code_policy(agent: PublicDecisionAgent, frames: Sequence[DecisionFrame]) -> Tuple[bool, List[str]]:
    """Small non-security lint for public-frame policy objects.

    Python cannot be made safe merely by linting. This check only verifies the
    promotion-facing contract: the agent accepts DecisionFrame objects, returns
    in-range action indices, and does not mutate frame-visible legal actions.
    """

    errors: List[str] = []
    rng = Random(1313)
    for i, frame in enumerate(frames):
        before = frame.legal_action_strings
        try:
            idx = int(agent.choose_action_index(frame, rng))
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"frame {i}: choose_action_index raised {type(exc).__name__}: {exc}")
            continue
        if not 0 <= idx < frame.action_count:
            errors.append(f"frame {i}: index {idx} outside action_count {frame.action_count}")
        if frame.legal_action_strings != before:
            errors.append(f"frame {i}: policy mutated legal action strings")
    return not errors, errors
