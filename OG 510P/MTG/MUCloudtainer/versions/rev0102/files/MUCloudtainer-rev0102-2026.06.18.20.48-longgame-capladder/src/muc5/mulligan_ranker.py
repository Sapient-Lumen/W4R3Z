from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .action_schema import Action
from .cards import (
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_ORDER,
    CARD_OVERLORD,
    STARTING_LIFE_OPTIONS,
)
from .mulligan import (
    MULLIGAN_KEEP,
    MULLIGAN_TAKE,
    MulliganAgent,
    MulliganObservation,
    legal_bottom_actions,
    mulligan_bottom,
)

MODEL_NAME = "mulligan_ranker_rev0024"
MODEL_FILENAME = "rev0024_mulligan_ranker_model.json"
OUTCOME_MODEL_NAME = "mulligan_outcome_ranker_rev0027"
OUTCOME_MODEL_FILENAME = "rev0027_mulligan_outcome_ranker_model.json"
COUNTERFACTUAL_MODEL_NAME = "mulligan_counterfactual_ranker_rev0029"
REPEATED_COUNTERFACTUAL_MODEL_NAME = "mulligan_repeated_counterfactual_ranker_rev0030"


def model_path_for_name(name: str) -> Path:
    if name == MODEL_NAME:
        filename = MODEL_FILENAME
    elif name == OUTCOME_MODEL_NAME:
        filename = OUTCOME_MODEL_FILENAME
    else:
        raise ValueError(f"unknown mulligan ranker model name {name!r}")
    return Path(__file__).resolve().parents[2] / "data" / filename


def default_model_path() -> Path:
    return model_path_for_name(MODEL_NAME)


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def mulligan_ranker_feature_names() -> Tuple[str, ...]:
    names: List[str] = [
        "bias",
        "stage_keep_or_mulligan",
        "stage_bottom",
        "mulligans_taken",
        "hand_size",
        "library_count",
        "bottom_remaining",
        "starting_life_20",
        "starting_life_40",
        "deck_size_40",
        "deck_size_60",
        "candidate_in_hand_count",
        "islands_minus_ideal_abs",
        "has_force_and_pitch",
        "has_counterspell_online_hint",
        "has_any_threat",
    ]
    names.extend(f"hand_{c}" for c in CARD_ORDER)
    names.extend(f"hand_frac_{c}" for c in CARD_ORDER)
    names.extend(f"deck_frac_{c}" for c in CARD_ORDER)
    names.extend(f"candidate_{c}" for c in CARD_ORDER)
    return tuple(names)


def _deck_counts_from_obs(obs: MulliganObservation) -> Dict[str, int]:
    counts = getattr(obs, "deck_counts", None) or {}
    return {card: int(counts.get(card, 0) or 0) for card in CARD_ORDER}


def _hand_counts_from_obs(obs: MulliganObservation) -> Dict[str, int]:
    return {card: int((obs.hand or {}).get(card, 0) or 0) for card in CARD_ORDER}


def _feature_dict(obs: MulliganObservation, candidate_card: str | None = None) -> Dict[str, float]:
    hand = _hand_counts_from_obs(obs)
    deck = _deck_counts_from_obs(obs)
    hand_total = max(1, sum(hand.values()))
    deck_total = max(1, sum(deck.values()) or (sum(hand.values()) + int(obs.library_count)))
    starting_life = int(getattr(obs, "starting_life", 20) or 20)
    candidate_count = hand.get(candidate_card or "", 0)
    nonland_blue = sum(hand[c] for c in (CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD))
    has_force_and_pitch = 1.0 if hand[CARD_FORCE] > 0 and nonland_blue >= 2 else 0.0
    has_counterspell_online_hint = 1.0 if hand[CARD_COUNTERSPELL] > 0 and hand[CARD_ISLAND] >= 2 else 0.0
    has_any_threat = 1.0 if hand[CARD_JACE] + hand[CARD_OVERLORD] > 0 else 0.0
    out: Dict[str, float] = {
        "bias": 1.0,
        "stage_keep_or_mulligan": 1.0 if obs.stage == "keep_or_mulligan" else 0.0,
        "stage_bottom": 1.0 if obs.stage == "bottom" else 0.0,
        "mulligans_taken": float(obs.mulligans_taken),
        "hand_size": float(obs.hand_size),
        "library_count": float(obs.library_count),
        "bottom_remaining": float(obs.bottom_remaining),
        "starting_life_20": 1.0 if starting_life == 20 else 0.0,
        "starting_life_40": 1.0 if starting_life == 40 else 0.0,
        "deck_size_40": 1.0 if deck_total <= 40 else 0.0,
        "deck_size_60": 1.0 if deck_total > 40 else 0.0,
        "candidate_in_hand_count": float(candidate_count),
        "islands_minus_ideal_abs": abs(float(hand[CARD_ISLAND]) - 3.0),
        "has_force_and_pitch": has_force_and_pitch,
        "has_counterspell_online_hint": has_counterspell_online_hint,
        "has_any_threat": has_any_threat,
    }
    for card in CARD_ORDER:
        out[f"hand_{card}"] = float(hand[card])
        out[f"hand_frac_{card}"] = float(hand[card]) / float(hand_total)
        out[f"deck_frac_{card}"] = float(deck.get(card, 0)) / float(deck_total)
        out[f"candidate_{card}"] = 1.0 if candidate_card == card else 0.0
    return out


def mulligan_ranker_feature_vector(obs: MulliganObservation, candidate_card: str | None = None, feature_names: Sequence[str] | None = None) -> Tuple[float, ...]:
    names = tuple(feature_names or mulligan_ranker_feature_names())
    fd = _feature_dict(obs, candidate_card)
    return tuple(float(fd.get(name, 0.0)) for name in names)


@dataclass(frozen=True)
class LinearMulliganRankerModel:
    model_id: str
    feature_names: Tuple[str, ...]
    keep_weights: Tuple[float, ...]
    keep_intercept: float
    bottom_weights: Tuple[float, ...]
    bottom_intercept: float
    source_revision: str
    training_summary: Mapping[str, object]

    def keep_logit(self, obs: MulliganObservation) -> float:
        xs = mulligan_ranker_feature_vector(obs, None, self.feature_names)
        return float(self.keep_intercept + sum(w * x for w, x in zip(self.keep_weights, xs)))

    def bottom_score(self, obs: MulliganObservation, card: str) -> float:
        xs = mulligan_ranker_feature_vector(obs, card, self.feature_names)
        return float(self.bottom_intercept + sum(w * x for w, x in zip(self.bottom_weights, xs)))

    def to_json(self) -> Dict[str, object]:
        return {
            "schema": "muc5.linear_mulligan_ranker.v1",
            "model_id": self.model_id,
            "feature_names": list(self.feature_names),
            "keep_weights": list(self.keep_weights),
            "keep_intercept": float(self.keep_intercept),
            "bottom_weights": list(self.bottom_weights),
            "bottom_intercept": float(self.bottom_intercept),
            "source_revision": self.source_revision,
            "training_summary": dict(self.training_summary),
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> "LinearMulliganRankerModel":
        if payload.get("schema") != "muc5.linear_mulligan_ranker.v1":
            raise ValueError(f"unexpected mulligan ranker schema {payload.get('schema')!r}")
        feature_names = tuple(str(x) for x in payload["feature_names"])  # type: ignore[index]
        keep_weights = tuple(float(x) for x in payload["keep_weights"])  # type: ignore[index]
        bottom_weights = tuple(float(x) for x in payload["bottom_weights"])  # type: ignore[index]
        if len(feature_names) != len(keep_weights) or len(feature_names) != len(bottom_weights):
            raise ValueError("mulligan ranker feature/weight length mismatch")
        return cls(
            model_id=str(payload["model_id"]),
            feature_names=feature_names,
            keep_weights=keep_weights,
            keep_intercept=float(payload["keep_intercept"]),
            bottom_weights=bottom_weights,
            bottom_intercept=float(payload["bottom_intercept"]),
            source_revision=str(payload.get("source_revision", "unknown")),
            training_summary=payload.get("training_summary", {}),  # type: ignore[arg-type]
        )


def save_mulligan_ranker_model(model: LinearMulliganRankerModel, path: str | Path) -> None:
    Path(path).write_text(json.dumps(model.to_json(), indent=2, sort_keys=True), encoding="utf-8")


def load_mulligan_ranker_model(path: str | Path | None = None) -> LinearMulliganRankerModel:
    p = Path(path) if path is not None else default_model_path()
    return LinearMulliganRankerModel.from_json(json.loads(p.read_text(encoding="utf-8")))


@dataclass
class LinearMulliganRankerAgent:
    model: LinearMulliganRankerModel
    name: str = MODEL_NAME
    keep_threshold: float = 0.0

    def choose_mulligan_action(self, obs: MulliganObservation, legal: Sequence[Action], rng: Random) -> Action:
        if obs.stage == "keep_or_mulligan":
            if MULLIGAN_TAKE not in legal:
                return MULLIGAN_KEEP
            # Later mulligans get harsher: a slightly negative logit can still be
            # a keep when the hand will be small after bottoming.
            threshold = self.keep_threshold - 0.35 * float(obs.mulligans_taken)
            return MULLIGAN_KEEP if self.model.keep_logit(obs) >= threshold else MULLIGAN_TAKE
        if obs.stage == "bottom":
            best: Tuple[float, float, Action] | None = None
            for action in legal:
                card = str(action.params.get("card", ""))
                score = self.model.bottom_score(obs, card)
                item = (score, rng.random() * 1e-9, action)
                if best is None or item > best:
                    best = item
            if best is None:
                raise ValueError("no legal bottom actions")
            return best[2]
        raise ValueError(f"unknown mulligan observation stage {obs.stage!r}")


def make_mulligan_agent(name_or_agent: str | MulliganAgent | object | None) -> MulliganAgent:
    """Factory for standard and learned mulligan agents.

    This function intentionally lives outside ``mulligan.py`` so the base rules
    surface remains small. ``mulligan.mulligan_agent_from_policy`` imports this
    lazily when it sees a nonstandard string.
    """

    from .mulligan import RuleMulliganAgent, MULLIGAN_POLICY_NAMES

    if hasattr(name_or_agent, "choose_mulligan_action"):
        return name_or_agent  # type: ignore[return-value]
    if name_or_agent is None or str(name_or_agent) in MULLIGAN_POLICY_NAMES:
        return RuleMulliganAgent(name_or_agent)  # type: ignore[arg-type]
    name = str(name_or_agent)
    if name.startswith("mulligan_rule_"):
        # Replay traces store explicit agent names; accept the rule-agent name
        # as a stable alias for the underlying policy string.  This keeps
        # learned and rule mulligan agents replayable through one factory.
        policy_name = name[len("mulligan_rule_") :]
        if policy_name in MULLIGAN_POLICY_NAMES:
            return RuleMulliganAgent(policy_name)
    if name == MODEL_NAME:
        return LinearMulliganRankerAgent(load_mulligan_ranker_model(), name=MODEL_NAME)
    if name == OUTCOME_MODEL_NAME:
        return LinearMulliganRankerAgent(load_mulligan_ranker_model(model_path_for_name(OUTCOME_MODEL_NAME)), name=OUTCOME_MODEL_NAME)
    if name == COUNTERFACTUAL_MODEL_NAME:
        from .mulligan_counterfactual import load_counterfactual_mulligan_agent
        return load_counterfactual_mulligan_agent()
    if name == REPEATED_COUNTERFACTUAL_MODEL_NAME:
        from .mulligan_counterfactual import load_repeated_counterfactual_mulligan_agent
        return load_repeated_counterfactual_mulligan_agent()
    raise ValueError(f"unknown mulligan agent/policy {name_or_agent!r}")


# --------------------------- pseudo-oracle training helpers ---------------------------


def opening_hand_quality(hand: Mapping[str, int], deck_counts: Mapping[str, int], starting_life: int, mulligans_taken: int) -> float:
    islands = int(hand.get(CARD_ISLAND, 0) or 0)
    counters = int(hand.get(CARD_COUNTERSPELL, 0) or 0)
    forces = int(hand.get(CARD_FORCE, 0) or 0)
    jaces = int(hand.get(CARD_JACE, 0) or 0)
    overlords = int(hand.get(CARD_OVERLORD, 0) or 0)
    nonland_blue = counters + forces + jaces + overlords
    score = 0.0
    # Mana: MUC-5 needs Islands but can flood; seven-Island hands are not good.
    score += 1.25 * min(islands, 3)
    score -= 1.65 * max(0, 2 - islands)
    score -= 0.85 * max(0, islands - 5)
    score -= 0.45 * max(0, islands - 4)
    # Interaction and Force reliability.
    score += 1.15 * min(counters, 2) + 0.45 * max(0, counters - 2)
    score += 0.95 * min(forces, 2) + 0.25 * max(0, forces - 2)
    if forces > 0:
        score += 1.10 if nonland_blue >= 2 else -0.75
        if starting_life == 20:
            score -= 0.18 * forces
    # Threats: 40-life games get a small Jace/long-game nudge; 20-life games
    # give Overlord pressure slightly more opening value.
    score += (1.25 if starting_life == 40 else 1.05) * min(jaces, 2) - 0.35 * max(0, jaces - 2)
    score += (1.25 if starting_life == 20 else 1.00) * min(overlords, 2) - 0.30 * max(0, overlords - 2)
    if jaces + overlords == 0:
        score -= 0.65
    if counters + forces == 0:
        score -= 0.85
    # Already-taken mulligans make future hand size smaller; reward merely
    # functional hands more as mulligans accumulate.
    score += 0.25 * mulligans_taken if islands >= 2 and nonland_blue >= 1 else -0.35 * mulligans_taken
    # Deck composition context: land-light decks should value functional Island
    # counts more; threat-light decks should keep scarce threats.
    deck_total = max(1, sum(int(v) for v in deck_counts.values()))
    land_frac = float(deck_counts.get(CARD_ISLAND, 0) or 0) / deck_total
    threat_frac = float((deck_counts.get(CARD_JACE, 0) or 0) + (deck_counts.get(CARD_OVERLORD, 0) or 0)) / deck_total
    if land_frac < 0.55 and islands >= 2:
        score += 0.35
    if threat_frac < 0.16 and jaces + overlords >= 1:
        score += 0.25
    return float(score)


def oracle_keep_label(hand: Mapping[str, int], deck_counts: Mapping[str, int], starting_life: int, mulligans_taken: int) -> int:
    q = opening_hand_quality(hand, deck_counts, starting_life, mulligans_taken)
    # Threshold drops after each mulligan because the alternative is a smaller
    # final hand.  This is a pseudo-oracle, not a gameplay truth claim.
    threshold = {0: 5.05, 1: 4.35, 2: 3.65}.get(int(mulligans_taken), 3.05)
    return 1 if q >= threshold else 0


def oracle_bottom_card(hand: Mapping[str, int], deck_counts: Mapping[str, int], starting_life: int, mulligans_taken: int, bottom_remaining: int) -> str:
    current = Counter({c: int(hand.get(c, 0) or 0) for c in CARD_ORDER})
    best_card = None
    best_score = None
    for card in CARD_ORDER:
        if current.get(card, 0) <= 0:
            continue
        trial = Counter(current)
        trial[card] -= 1
        if trial[card] <= 0:
            del trial[card]
        # Bottom the card whose removal leaves the best remaining hand.  Add tiny
        # deterministic tie weights so labels are stable.
        score = opening_hand_quality(trial, deck_counts, starting_life, mulligans_taken)
        score += {CARD_ISLAND: 0.004, CARD_OVERLORD: 0.003, CARD_JACE: 0.002, CARD_FORCE: 0.001, CARD_COUNTERSPELL: 0.0}.get(card, 0.0)
        if best_score is None or score > best_score:
            best_score = score
            best_card = card
    if best_card is None:
        raise ValueError("cannot choose bottom card from empty hand")
    return best_card


def counts_to_library(counts: Mapping[str, int]) -> List[str]:
    cards: List[str] = []
    for card in CARD_ORDER:
        cards.extend([card] * int(counts.get(card, 0) or 0))
    return cards


def draw7_from_counts(counts: Mapping[str, int], rng: Random) -> Counter[str]:
    deck = counts_to_library(counts)
    rng.shuffle(deck)
    hand = Counter()
    for _ in range(min(7, len(deck))):
        hand[deck.pop()] += 1
    return hand


def make_training_observation(
    *,
    player: int,
    stage: str,
    hand: Mapping[str, int],
    deck_counts: Mapping[str, int],
    starting_life: int,
    mulligans_taken: int,
    bottom_remaining: int = 0,
) -> MulliganObservation:
    library_count = max(0, int(sum(deck_counts.values())) - int(sum(hand.values())))
    return MulliganObservation(
        player=player,
        stage=stage,
        mulligans_taken=int(mulligans_taken),
        hand={card: int(hand.get(card, 0) or 0) for card in CARD_ORDER if int(hand.get(card, 0) or 0) > 0},
        hand_size=int(sum(hand.values())),
        library_count=library_count,
        bottom_remaining=int(bottom_remaining),
        starting_life=int(starting_life),
        deck_counts={card: int(deck_counts.get(card, 0) or 0) for card in CARD_ORDER},
    )


def generate_mulligan_training_rows(deck_counts_list: Sequence[Mapping[str, int]], *, samples_per_deck_life: int = 900, seed: int = 24024) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rng = Random(seed)
    keep_rows: List[Dict[str, object]] = []
    bottom_rows: List[Dict[str, object]] = []
    row_id = 0
    for d_idx, deck_counts in enumerate(deck_counts_list):
        deck_counts = {card: int(deck_counts.get(card, 0) or 0) for card in CARD_ORDER}
        for life in STARTING_LIFE_OPTIONS:
            for sample in range(samples_per_deck_life):
                hand = draw7_from_counts(deck_counts, rng)
                for mulligans_taken in (0, 1, 2, 3):
                    obs = make_training_observation(
                        player=0,
                        stage="keep_or_mulligan",
                        hand=hand,
                        deck_counts=deck_counts,
                        starting_life=int(life),
                        mulligans_taken=mulligans_taken,
                    )
                    label = oracle_keep_label(obs.hand, deck_counts, int(life), mulligans_taken)
                    fd = dict(zip(mulligan_ranker_feature_names(), mulligan_ranker_feature_vector(obs)))
                    keep_rows.append({
                        "example_id": row_id,
                        "deck_index": d_idx,
                        "sample": sample,
                        "starting_life": life,
                        "mulligans_taken": mulligans_taken,
                        "label_keep": label,
                        **fd,
                    })
                    row_id += 1
                # Bottom labels from hands that kept after one to three mulligans.
                for mulligans_taken in (1, 2, 3):
                    current = Counter(hand)
                    for bottom_remaining in range(mulligans_taken, 0, -1):
                        obs = make_training_observation(
                            player=0,
                            stage="bottom",
                            hand=current,
                            deck_counts=deck_counts,
                            starting_life=int(life),
                            mulligans_taken=mulligans_taken,
                            bottom_remaining=bottom_remaining,
                        )
                        chosen = oracle_bottom_card(obs.hand, deck_counts, int(life), mulligans_taken, bottom_remaining)
                        for action in legal_bottom_actions(current):
                            card = str(action.params["card"])
                            fd = dict(zip(mulligan_ranker_feature_names(), mulligan_ranker_feature_vector(obs, card)))
                            bottom_rows.append({
                                "example_id": row_id,
                                "deck_index": d_idx,
                                "sample": sample,
                                "starting_life": life,
                                "mulligans_taken": mulligans_taken,
                                "bottom_remaining": bottom_remaining,
                                "candidate_card": card,
                                "label_bottom": 1 if card == chosen else 0,
                                **fd,
                            })
                        current[chosen] -= 1
                        if current[chosen] <= 0:
                            del current[chosen]
                        row_id += 1
    return keep_rows, bottom_rows
