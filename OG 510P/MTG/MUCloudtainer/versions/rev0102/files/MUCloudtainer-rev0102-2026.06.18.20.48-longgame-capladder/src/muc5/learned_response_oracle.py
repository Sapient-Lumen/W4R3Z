from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Iterable, Mapping, Sequence

from .action_features import action_feature_dict
from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD, OVERLORD_POWER
from .decision import DecisionFrame
from .deckspace import DeckVector
from .gameplay_map_elites import dedupe_candidates, strategy_descriptor
from .mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from .payoff import StrategyBundle
from .psro import FiniteOracleCandidate, strategy_signature
from .public_agents import PublicProfileAgent
from .terminal_decomposition import THREAT_MULLIGAN

LEARNED_RESPONSE_REVISION = "rev0097"
LEARNED_AGENT_PREFIX = "learned_response_rev0097"

LEARNED_FEATURE_NAMES: tuple[str, ...] = (
    "bias",
    "base_profile_score_norm",
    "cast_counterspell",
    "cast_force",
    "cast_jace",
    "cast_overlord",
    "target_premium_spell",
    "target_counter_or_force",
    "counter_targets_own_spell",
    "force_pitch_payment",
    "force_pitch_life_risk",
    "pitch_counterspell",
    "pitch_force",
    "pitch_jace",
    "pitch_overlord",
    "play_island",
    "pass_main",
    "pass_response",
    "jace_plus2",
    "jace_zero",
    "jace_minus1",
    "jace_ultimate",
    "attack_face_pressure",
    "attack_jace_pressure",
    "attack_lethalish",
    "block_face_low_life",
    "block_jace_pressure",
    "choose_discard_island",
    "choose_discard_business",
    "choose_force_pitch_counterspell",
    "choose_force_pitch_force",
    "choose_force_pitch_jace",
    "choose_force_pitch_overlord",
    "choose_jace_plus2_bottom_opp_business",
    "choose_jace_plus2_leave_opp_island",
    "choose_jace_plus2_leave_self_business",
    "choose_jace_plus2_bottom_self_island",
    "brainstorm_putback_islands",
    "brainstorm_putback_business",
    "known_own_top_island_jace_zero",
    "known_own_top_business_jace_zero",
    "known_opp_top_business_fateseal",
    "known_opp_top_island_fateseal",
    "opponent_force_pitches_seen_cast_threat",
    "opponent_library_low_threat",
    "own_library_low_draw_engine",
    "opp_tapped_cast_threat",
)


@dataclass(frozen=True)
class LearnedResponseModel:
    """Small auditable action scorer learned as a response oracle.

    The model is intentionally not a black-box neural controller.  It is a
    registry-backed linear scorer over stable action/context/information-state
    features plus a readable public-profile baseline.  rev0097 learns candidate
    weight vectors by rollout search against the current PSRO support and then
    evaluates them with seed-disjoint gates.
    """

    agent_id: str
    base_profile: str
    weights: Mapping[str, float]
    source: str = "rev0097_rollout_search"
    generation: int = 0
    parent_agent_id: str | None = None
    training_score: float | None = None
    training_games: int = 0

    @property
    def name(self) -> str:
        return self.agent_id

    def normalized_id(self) -> str:
        return normalize_agent_id(self.agent_id)

    def validate(self) -> None:
        if not self.normalized_id().startswith(LEARNED_AGENT_PREFIX):
            raise ValueError(f"learned response agent_id must start with {LEARNED_AGENT_PREFIX!r}: {self.agent_id!r}")
        unknown = set(self.weights) - set(LEARNED_FEATURE_NAMES)
        if unknown:
            raise ValueError(f"unknown learned response feature weights: {sorted(unknown)}")
        for name in LEARNED_FEATURE_NAMES:
            value = float(self.weights.get(name, 0.0))
            if not math.isfinite(value):
                raise ValueError(f"nonfinite weight for {name}: {value}")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "agent_id": self.normalized_id(),
            "base_profile": self.base_profile,
            "weights": {name: float(self.weights.get(name, 0.0)) for name in LEARNED_FEATURE_NAMES},
            "source": self.source,
            "generation": int(self.generation),
            "parent_agent_id": self.parent_agent_id,
            "training_score": self.training_score,
            "training_games": int(self.training_games),
        }


@dataclass
class LearnedResponseAgent:
    model: LearnedResponseModel

    @property
    def name(self) -> str:
        return self.model.normalized_id()

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = []
        for index, action in enumerate(frame.legal_actions):
            scored.append((self.score_action(frame, action), rng.random(), index))
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]

    def score_action(self, frame: DecisionFrame, action: Action) -> float:
        features = learned_feature_dict(frame, action, base_profile=self.model.base_profile)
        total = 0.0
        for name in LEARNED_FEATURE_NAMES:
            total += float(self.model.weights.get(name, 0.0)) * float(features.get(name, 0.0))
        return total


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_registry_path() -> Path:
    return project_root() / "data" / "rev0097_learned_response_agent_registry.json"


def normalize_agent_id(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def learned_feature_names() -> tuple[str, ...]:
    return LEARNED_FEATURE_NAMES


def _zone(obs: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = obs.get(key)
    return value if isinstance(value, Mapping) else {}


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _card_is_business(card: str | None) -> bool:
    return card in {CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD}


def _known_top_card(frame: DecisionFrame, target_player: int) -> str | None:
    info = frame.information_state if isinstance(frame.information_state, Mapping) else {}
    known = info.get("known_top_cards", {})
    if not isinstance(known, Mapping):
        return None
    value = known.get(str(int(target_player)))
    return None if value is None else str(value)


def _public_events(frame: DecisionFrame) -> list[Mapping[str, object]]:
    info = frame.information_state if isinstance(frame.information_state, Mapping) else {}
    events = info.get("public_events", [])
    return [event for event in events if isinstance(event, Mapping)] if isinstance(events, list) else []


def _stack_item(obs: Mapping[str, object], target_id: object) -> Mapping[str, object]:
    try:
        wanted = int(target_id)
    except (TypeError, ValueError):
        return {}
    stack = obs.get("stack", [])
    if not isinstance(stack, list):
        return {}
    for item in stack:
        if not isinstance(item, Mapping):
            continue
        try:
            spell_id = int(item.get("spell_id", -99999))
        except (TypeError, ValueError):
            continue
        if spell_id == wanted:
            return item
    return {}


def learned_feature_dict(frame: DecisionFrame, action: Action, *, base_profile: str = "threat_pressure") -> dict[str, float]:
    """Return compact learned-response features for one legal action.

    Features are derived only from the policy-facing ``DecisionFrame`` and the
    action object.  The known-top and event-history terms intentionally use
    ``frame.information_state`` so the learner exercises the rev0091/0092
    imperfect-information contract.
    """

    obs = frame.observation
    public_self = _zone(obs, "public_self")
    public_opp = _zone(obs, "public_opponent")
    starting_life = max(1.0, float(obs.get("starting_life", 20) or 20))
    own_life = float(public_self.get("life", starting_life) or 0.0)
    opp_life = float(public_opp.get("life", starting_life) or 0.0)
    own_library = float(obs.get("own_library_count", public_self.get("library_count", 0)) or 0.0)
    opp_library = float(public_opp.get("library_count", 0) or 0.0)
    opp_tapped = float(public_opp.get("islands_tapped", 0) or 0.0)
    opp_untapped = float(public_opp.get("islands_untapped", 0) or 0.0)
    viewer = int(frame.player)
    opponent = 1 - viewer

    action_features = action_feature_dict(action, obs)
    base_score = PublicProfileAgent(base_profile).score_action(dict(obs), action)
    p = action.params
    kind = action.kind
    target_card = str(p.get("target_card", ""))
    card = str(p.get("card", ""))
    pitch_card = str(p.get("pitch_card", p.get("pitch", "")))
    effect = str(p.get("effect", ""))
    target_item = _stack_item(obs, p.get("target_id"))
    target_controller = target_item.get("controller")
    target_own = False
    try:
        target_own = int(target_controller) == viewer
    except (TypeError, ValueError):
        target_own = False

    own_top = _known_top_card(frame, viewer)
    opp_top = _known_top_card(frame, opponent)
    opponent_pitch_events = sum(
        1
        for event in _public_events(frame)
        if event.get("kind") == "FORCE_PITCH_PAYMENT" and int(event.get("player", -1)) == opponent
    )
    to_player = float(p.get("to_player", 0) or 0)
    to_jace = float(p.get("to_jace", 0) or 0)
    block_player = float(p.get("block_player_attackers", p.get("block_player", 0)) or 0)
    block_jace = float(p.get("block_jace_attackers", p.get("block_jace", 0)) or 0)
    attack_damage = to_player * float(OVERLORD_POWER)
    opp_has_jace = 1.0 if public_opp.get("jace_loyalty") is not None else 0.0
    choice_discard = str(p.get("discard", p.get("card", p.get("pitch_card", ""))))
    pending = obs.get("pending_choice_data", {}) if isinstance(obs.get("pending_choice_data", {}), Mapping) else {}
    seen = str(pending.get("seen_top_card", p.get("seen_card", "")))
    put = str(p.get("put", ""))
    raw_target = pending.get("target_player", p.get("target_player"))
    try:
        choice_target = int(raw_target) if raw_target not in {"self", "opponent", None} else (viewer if raw_target == "self" else opponent if raw_target == "opponent" else -1)
    except (TypeError, ValueError):
        choice_target = -1

    out = {name: 0.0 for name in LEARNED_FEATURE_NAMES}
    out["bias"] = 1.0
    out["base_profile_score_norm"] = max(-2.0, min(12.0, float(base_score))) / 12.0
    out["cast_counterspell"] = action_features["cast_counterspell"]
    out["cast_force"] = action_features["cast_force"]
    out["cast_jace"] = action_features["cast_jace"]
    out["cast_overlord"] = action_features["cast_overlord"]
    out["target_premium_spell"] = 1.0 if kind == "CAST" and target_card in {CARD_JACE, CARD_OVERLORD} else 0.0
    out["target_counter_or_force"] = 1.0 if kind == "CAST" and target_card in {CARD_COUNTERSPELL, CARD_FORCE} else 0.0
    out["counter_targets_own_spell"] = 1.0 if target_own and card in {CARD_COUNTERSPELL, CARD_FORCE} else 0.0
    out["force_pitch_payment"] = 1.0 if kind == "CAST" and card == CARD_FORCE and str(p.get("payment")) == "pitch" else 0.0
    out["force_pitch_life_risk"] = out["force_pitch_payment"] * _clip01(1.0 - own_life / starting_life + (1.0 if own_life <= 1.0 else 0.0))
    out["pitch_counterspell"] = 1.0 if pitch_card == CARD_COUNTERSPELL else 0.0
    out["pitch_force"] = 1.0 if pitch_card == CARD_FORCE else 0.0
    out["pitch_jace"] = 1.0 if pitch_card == CARD_JACE else 0.0
    out["pitch_overlord"] = 1.0 if pitch_card == CARD_OVERLORD else 0.0
    out["play_island"] = action_features["kind_play_island"]
    out["pass_main"] = action_features["is_pass_main"]
    out["pass_response"] = action_features["is_pass_response"]
    out["jace_plus2"] = action_features["jace_plus2"]
    out["jace_zero"] = action_features["jace_zero"]
    out["jace_minus1"] = action_features["jace_minus1"]
    out["jace_ultimate"] = action_features["jace_ultimate"]
    out["attack_face_pressure"] = _clip01(to_player / 4.0) * _clip01(1.0 - opp_life / starting_life + 0.25)
    out["attack_jace_pressure"] = _clip01(to_jace / 4.0) * opp_has_jace
    out["attack_lethalish"] = 1.0 if kind == "ATTACK" and attack_damage > 0 and attack_damage >= opp_life else 0.0
    out["block_face_low_life"] = _clip01(block_player / 4.0) * _clip01(1.0 - own_life / starting_life + 0.25)
    out["block_jace_pressure"] = _clip01(block_jace / 4.0) * (1.0 if public_self.get("jace_loyalty") is not None else 0.0)
    out["choose_discard_island"] = 1.0 if effect in {"discard", "overlord_discard", "cleanup_discard"} and choice_discard == CARD_ISLAND else 0.0
    out["choose_discard_business"] = 1.0 if effect in {"discard", "overlord_discard", "cleanup_discard"} and _card_is_business(choice_discard) else 0.0
    out["choose_force_pitch_counterspell"] = 1.0 if effect == "force_pitch" and choice_discard == CARD_COUNTERSPELL else 0.0
    out["choose_force_pitch_force"] = 1.0 if effect == "force_pitch" and choice_discard == CARD_FORCE else 0.0
    out["choose_force_pitch_jace"] = 1.0 if effect == "force_pitch" and choice_discard == CARD_JACE else 0.0
    out["choose_force_pitch_overlord"] = 1.0 if effect == "force_pitch" and choice_discard == CARD_OVERLORD else 0.0
    out["choose_jace_plus2_bottom_opp_business"] = 1.0 if effect == "jace_plus2" and choice_target == opponent and put == "bottom" and _card_is_business(seen) else 0.0
    out["choose_jace_plus2_leave_opp_island"] = 1.0 if effect == "jace_plus2" and choice_target == opponent and put == "leave" and seen == CARD_ISLAND else 0.0
    out["choose_jace_plus2_leave_self_business"] = 1.0 if effect == "jace_plus2" and choice_target == viewer and put == "leave" and _card_is_business(seen) else 0.0
    out["choose_jace_plus2_bottom_self_island"] = 1.0 if effect == "jace_plus2" and choice_target == viewer and put == "bottom" and seen == CARD_ISLAND else 0.0
    out["brainstorm_putback_islands"] = 1.0 if effect == "jace_brainstorm_putback" and str(p.get("first_draw", "")) == CARD_ISLAND and str(p.get("second_draw", "")) == CARD_ISLAND else 0.0
    out["brainstorm_putback_business"] = 1.0 if effect == "jace_brainstorm_putback" and (_card_is_business(str(p.get("first_draw", ""))) or _card_is_business(str(p.get("second_draw", "")))) else 0.0
    out["known_own_top_island_jace_zero"] = 1.0 if kind == "ACTIVATE_JACE" and str(p.get("mode")) == "zero" and own_top == CARD_ISLAND else 0.0
    out["known_own_top_business_jace_zero"] = 1.0 if kind == "ACTIVATE_JACE" and str(p.get("mode")) == "zero" and _card_is_business(own_top) else 0.0
    out["known_opp_top_business_fateseal"] = 1.0 if kind == "ACTIVATE_JACE" and str(p.get("mode")) == "plus2" and _card_is_business(opp_top) else 0.0
    out["known_opp_top_island_fateseal"] = 1.0 if kind == "ACTIVATE_JACE" and str(p.get("mode")) == "plus2" and opp_top == CARD_ISLAND else 0.0
    out["opponent_force_pitches_seen_cast_threat"] = min(1.0, opponent_pitch_events / 3.0) * (1.0 if kind == "CAST" and card in {CARD_JACE, CARD_OVERLORD} else 0.0)
    out["opponent_library_low_threat"] = _clip01(1.0 - opp_library / 20.0) * (1.0 if kind == "CAST" and card in {CARD_JACE, CARD_OVERLORD} else 0.0)
    out["own_library_low_draw_engine"] = _clip01(1.0 - own_library / 10.0) * (1.0 if (kind == "ACTIVATE_JACE" and str(p.get("mode")) == "zero") or (kind == "CAST" and card == CARD_OVERLORD) else 0.0)
    out["opp_tapped_cast_threat"] = _clip01(opp_tapped / max(1.0, opp_tapped + opp_untapped)) * (1.0 if kind == "CAST" and card in {CARD_JACE, CARD_OVERLORD} else 0.0)
    return out


def load_registry(path: str | Path | None = None) -> dict[str, LearnedResponseModel]:
    source = Path(path) if path is not None else default_registry_path()
    if not source.exists():
        raise FileNotFoundError(f"learned response registry is missing: {source}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    agents = payload.get("agents", {}) if isinstance(payload, Mapping) else {}
    if not isinstance(agents, Mapping):
        raise ValueError("learned response registry must contain an object-valued agents map")
    out: dict[str, LearnedResponseModel] = {}
    for key, row in agents.items():
        if not isinstance(row, Mapping):
            raise ValueError(f"registry row for {key!r} is not an object")
        model = LearnedResponseModel(
            agent_id=normalize_agent_id(str(row.get("agent_id", key))),
            base_profile=str(row.get("base_profile", "threat_pressure")),
            weights={name: float(value) for name, value in dict(row.get("weights", {})).items()},
            source=str(row.get("source", "registry")),
            generation=int(row.get("generation", 0)),
            parent_agent_id=None if row.get("parent_agent_id") is None else str(row.get("parent_agent_id")),
            training_score=None if row.get("training_score") is None else float(row.get("training_score")),
            training_games=int(row.get("training_games", 0) or 0),
        )
        model.validate()
        out[model.normalized_id()] = model
    return out


def write_registry(path: str | Path, models: Sequence[LearnedResponseModel], *, metadata: Mapping[str, object] | None = None) -> None:
    agents = {model.normalized_id(): model.as_dict() for model in models}
    payload = {
        "schema": "muc5.rev0097_learned_response_agent_registry.v1",
        "revision": LEARNED_RESPONSE_REVISION,
        "feature_names": list(LEARNED_FEATURE_NAMES),
        "metadata": dict(metadata or {}),
        "agents": agents,
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_learned_response_agent(name: str) -> LearnedResponseAgent:
    normalized = normalize_agent_id(name)
    registry = load_registry()
    if normalized not in registry:
        raise ValueError(f"learned response agent {name!r} not found in {default_registry_path().name}")
    return LearnedResponseAgent(registry[normalized])


def _template_weights(profile: str) -> dict[str, float]:
    # The template is intentionally conservative.  Rollout search perturbs these
    # weights; the public-profile score remains a strong regularizer so candidates
    # remain interpretable and legal-action-list based.
    weights = {name: 0.0 for name in LEARNED_FEATURE_NAMES}
    weights.update(
        {
            "base_profile_score_norm": 10.0,
            "play_island": 2.0,
            "counter_targets_own_spell": -18.0,
            "target_premium_spell": 2.0,
            "target_counter_or_force": -0.5,
            "force_pitch_life_risk": -3.0,
            "pitch_force": -2.0,
            "pitch_jace": -2.2,
            "pitch_overlord": -1.6,
            "pass_response": -0.6,
            "jace_ultimate": 20.0,
            "attack_lethalish": 6.0,
            "known_own_top_island_jace_zero": 1.5,
            "known_own_top_business_jace_zero": -0.5,
            "known_opp_top_business_fateseal": 1.0,
            "known_opp_top_island_fateseal": -1.0,
            "choose_jace_plus2_bottom_opp_business": 2.5,
            "choose_jace_plus2_leave_opp_island": 2.0,
            "choose_jace_plus2_leave_self_business": 2.2,
            "choose_jace_plus2_bottom_self_island": 2.0,
            "brainstorm_putback_islands": 1.5,
            "brainstorm_putback_business": -2.0,
            "opponent_force_pitches_seen_cast_threat": 1.4,
            "own_library_low_draw_engine": -4.0,
            "opp_tapped_cast_threat": 1.2,
        }
    )
    if profile == "threat_pressure":
        weights.update({"cast_jace": 0.8, "cast_overlord": 1.4, "attack_face_pressure": 2.0, "attack_jace_pressure": 1.2, "pass_main": -0.8})
    elif profile == "threat_surge":
        weights.update({"cast_overlord": 2.0, "attack_face_pressure": 2.8, "attack_jace_pressure": 0.6, "pass_main": -1.2})
    elif profile == "counter_guard":
        weights.update({"cast_counterspell": 1.2, "cast_force": 0.8, "block_face_low_life": 1.4, "block_jace_pressure": 1.0, "pass_main": 0.5})
    return weights


def sampled_learned_models(
    *,
    seed: int = 970970,
    profiles: Sequence[str] = ("threat_pressure", "threat_surge", "counter_guard"),
    generation0_per_profile: int = 4,
    generation1_children: int = 12,
    parent_scores: Mapping[str, float] | None = None,
) -> list[LearnedResponseModel]:
    """Create deterministic rollout-search models.

    Without parent scores this returns generation-0 exploratory samples.  With
    parent scores, it builds generation-1 children around the score-weighted
    average of the best generation-0 vectors.  The caller performs the actual
    gameplay evaluation; this helper keeps vector generation reproducible and
    easy to test.
    """

    rng = Random(int(seed))
    models: list[LearnedResponseModel] = []
    index = 0

    if not parent_scores:
        for profile in profiles:
            base = _template_weights(profile)
            for _ in range(int(generation0_per_profile)):
                index += 1
                weights = {}
                for name in LEARNED_FEATURE_NAMES:
                    scale = 0.45 if name == "base_profile_score_norm" else 1.35
                    weights[name] = float(base.get(name, 0.0)) + rng.gauss(0.0, scale)
                weights["base_profile_score_norm"] = max(5.0, min(14.0, weights["base_profile_score_norm"]))
                models.append(
                    LearnedResponseModel(
                        agent_id=f"{LEARNED_AGENT_PREFIX}_g0_{index:02d}",
                        base_profile=profile,
                        weights=weights,
                        source="generation0_sampled_template_rollout_search",
                        generation=0,
                    )
                )
        return models

    # Build a stable elite mean from scored parents.  Scores <= 0.5 still inform
    # direction weakly, but positive excess receives more mass.
    parent_registry = {model.normalized_id(): model for model in sampled_learned_models(seed=seed, profiles=profiles, generation0_per_profile=generation0_per_profile)}
    ranked = sorted(
        ((float(score), parent_registry[normalize_agent_id(agent_id)]) for agent_id, score in parent_scores.items() if normalize_agent_id(agent_id) in parent_registry),
        key=lambda item: item[0],
        reverse=True,
    )
    if not ranked:
        raise ValueError("parent_scores did not match any generation-0 models")
    elites = ranked[: max(2, min(4, len(ranked)))]
    total_weight = sum(max(0.02, score - 0.35) for score, _model in elites)
    mean_weights: dict[str, float] = {}
    for name in LEARNED_FEATURE_NAMES:
        mean_weights[name] = sum(max(0.02, score - 0.35) * float(model.weights.get(name, 0.0)) for score, model in elites) / total_weight
    profile_scores: dict[str, float] = {}
    for score, model in elites:
        profile_scores[model.base_profile] = profile_scores.get(model.base_profile, 0.0) + max(0.02, score - 0.35)
    elite_profile = max(profile_scores.items(), key=lambda item: (item[1], item[0]))[0]
    parent_id = elites[0][1].normalized_id()
    for child in range(1, int(generation1_children) + 1):
        weights = {}
        for name in LEARNED_FEATURE_NAMES:
            sigma = 0.25 if name == "base_profile_score_norm" else 0.75
            weights[name] = float(mean_weights[name]) + rng.gauss(0.0, sigma)
        weights["base_profile_score_norm"] = max(5.0, min(14.0, weights["base_profile_score_norm"]))
        models.append(
            LearnedResponseModel(
                agent_id=f"{LEARNED_AGENT_PREFIX}_g1_{child:02d}",
                base_profile=elite_profile,
                weights=weights,
                source="generation1_score_weighted_elite_recentered_rollout_search",
                generation=1,
                parent_agent_id=parent_id,
            )
        )
    return models


def learned_deck_sources(
    *,
    gme_archive_path: str | Path,
    limit: int = 4,
) -> list[DeckVector]:
    """Return a bounded deck menu seeded by gameplay evidence."""

    decks: list[DeckVector] = []
    # The rev0095 point-estimate challenger is a useful first source because it
    # came from actual rollout search rather than static deck priors.
    path = Path(gme_archive_path)
    if path.exists():
        rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
        rows.sort(
            key=lambda row: (
                float(row.get("mean_score", row.get("quality", 0.0)) or 0.0),
                float(row.get("ci_low", 0.0) or 0.0),
                row.get("strategy_id", ""),
            ),
            reverse=True,
        )
        for row in rows:
            try:
                deck = DeckVector(
                    int(row.get("deck_size", row.get("size", 0))),
                    int(row.get("island", row.get("deck_Island", 0))),
                    int(row.get("counterspell", row.get("deck_Counterspell", 0))),
                    int(row.get("force", row.get("deck_ForceOfWill", 0))),
                    int(row.get("jace", row.get("deck_JaceTheMindSculptor", 0))),
                    int(row.get("overlord", row.get("deck_OverlordOfTheFloodpits", 0))),
                )
                deck.validate()
            except Exception:
                continue
            if deck.as_tuple() not in {d.as_tuple() for d in decks}:
                decks.append(deck)
            if len(decks) >= int(limit):
                break
    fallback = [
        DeckVector(40, 16, 12, 0, 7, 5),
        DeckVector(60, 25, 21, 4, 5, 5),
        DeckVector(40, 18, 10, 2, 8, 2),
        DeckVector(40, 20, 8, 4, 4, 4),
    ]
    for deck in fallback:
        if deck.as_tuple() not in {d.as_tuple() for d in decks}:
            decks.append(deck)
        if len(decks) >= int(limit):
            break
    return decks[: int(limit)]


def learned_response_candidates(
    models: Sequence[LearnedResponseModel],
    decks: Sequence[DeckVector],
    *,
    max_models: int | None = None,
    max_decks: int | None = None,
    forbidden_signatures: Iterable[tuple[object, ...]] = (),
) -> list[FiniteOracleCandidate]:
    candidates: list[FiniteOracleCandidate] = []
    kept_models = list(models)[: max_models if max_models is not None else len(models)]
    kept_decks = list(decks)[: max_decks if max_decks is not None else len(decks)]
    for model_index, model in enumerate(kept_models, 1):
        for deck_index, deck in enumerate(kept_decks, 1):
            desc = strategy_descriptor(
                StrategyBundle("tmp", "tmp", deck, model.normalized_id(), THREAT_MULLIGAN)
            )
            # The learned scorer is the thing under test; keep mulligan variation bounded.
            mulligans = (POLICY_LAND_BAND_BUSINESS, THREAT_MULLIGAN if THREAT_MULLIGAN != POLICY_LAND_BAND_BUSINESS else POLICY_LAND_BAND)
            for mulligan_index, mulligan in enumerate(mulligans, 1):
                strategy_id = (
                    f"learned_{model.generation}_{model_index:02d}_d{deck_index}_m{mulligan_index}_"
                    f"{deck.size}_{desc['threat_bin']}_{desc['counter_bin']}"
                )
                candidates.append(
                    FiniteOracleCandidate(
                        strategy=StrategyBundle(
                            strategy_id=strategy_id,
                            deck_name=f"rev0097_learned_deck_{deck_index}",
                            deck=deck,
                            agent_name=model.normalized_id(),
                            mulligan_policy=str(mulligan),
                        ),
                        oracle_family="rollout_searched_information_state_linear_response",
                        source=(
                            f"agent={model.normalized_id()}; generation={model.generation}; "
                            f"base_profile={model.base_profile}; deck_index={deck_index}; "
                            "score-vector learned by direct rollout search against current PSRO support"
                        ),
                    )
                )
    return dedupe_candidates(candidates, forbidden_signatures=forbidden_signatures)


def duplicate_candidate_ids(population: Sequence[StrategyBundle], candidates: Sequence[FiniteOracleCandidate]) -> dict[str, str]:
    population_signatures = {strategy_signature(strategy): strategy.strategy_id for strategy in population}
    out: dict[str, str] = {}
    for candidate in candidates:
        duplicate = population_signatures.get(strategy_signature(candidate.strategy))
        if duplicate is not None:
            out[candidate.strategy.strategy_id] = duplicate
    return out
