from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Iterable, Mapping, Sequence

from .deckspace import DeckVector, plausibility_filter, random_deck
from .map_elites import deck_descriptor
from .mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from .oracle_seed import mutate_deck
from .payoff import StrategyBundle
from .psro import FiniteOracleCandidate, strategy_signature
from .terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN


@dataclass(frozen=True)
class PilotTemplate:
    family: str
    agent_name: str
    mulligan_policy: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GameplayEliteRecord:
    cell_id: str
    strategy_id: str
    generation: int
    quality: float
    mean_score: float
    ci_low: float
    games: int
    truncations: int
    oracle_family: str
    source: str
    deck_size: int
    island: int
    counterspell: int
    force: int
    jace: int
    overlord: int
    agent_name: str
    mulligan_policy: str
    descriptors: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        descriptors = dict(payload.pop("descriptors"))
        payload.update({f"desc_{key}": value for key, value in descriptors.items()})
        return payload


COUNTER_TEMPLATE = PilotTemplate("counter_guard", "infostate_counter_guard", CF34_MULLIGAN)
CLOSURE_TEMPLATE = PilotTemplate("threat_closure", "infostate_threat_closure", THREAT_MULLIGAN)
PRESSURE_TEMPLATE = PilotTemplate("threat_pressure", "infostate_threat_pressure", THREAT_MULLIGAN)
SURGE_TEMPLATE = PilotTemplate("threat_surge", "infostate_threat_surge", THREAT_MULLIGAN)
BALANCED_TEMPLATE = PilotTemplate("balanced", "infostate_heuristic", POLICY_LAND_BAND)
BUSINESS_TEMPLATE = PilotTemplate("business_pressure", "infostate_threat_pressure", POLICY_LAND_BAND_BUSINESS)
ALL_TEMPLATES: tuple[PilotTemplate, ...] = (
    COUNTER_TEMPLATE,
    CLOSURE_TEMPLATE,
    PRESSURE_TEMPLATE,
    SURGE_TEMPLATE,
    BALANCED_TEMPLATE,
    BUSINESS_TEMPLATE,
)


def pilot_templates_for_deck(deck: DeckVector) -> tuple[PilotTemplate, ...]:
    """Return a small, interpretable pilot menu for a deck descriptor.

    This keeps the generative oracle from pretending deck search alone is the
    method.  MAP-Elites cells include the pilot family, but the pilot templates
    remain bounded and auditable rather than open-ended hand authoring.
    """

    desc = deck_descriptor(deck)
    threat_bin = str(desc["threat_bin"])
    counter_bin = str(desc["counter_bin"])
    templates: list[PilotTemplate] = []
    if counter_bin == "counter_wall" or deck.interaction >= deck.threats + 8:
        templates.append(COUNTER_TEMPLATE)
    if threat_bin == "overlord_heavy":
        templates.append(SURGE_TEMPLATE)
    elif threat_bin == "jace_heavy":
        templates.append(PRESSURE_TEMPLATE)
    elif threat_bin == "mixed_threats":
        templates.append(CLOSURE_TEMPLATE)
    else:
        templates.append(BALANCED_TEMPLATE)
    if deck.threats >= 6 and deck.size == 40:
        templates.append(BUSINESS_TEMPLATE)
    # Keep deterministic order while removing duplicate template identities.
    seen: set[tuple[str, str, str]] = set()
    out: list[PilotTemplate] = []
    for template in templates:
        key = (template.family, template.agent_name, str(template.mulligan_policy))
        if key not in seen:
            seen.add(key)
            out.append(template)
    return tuple(out)


def strategy_descriptor(strategy: StrategyBundle) -> dict[str, object]:
    desc = dict(deck_descriptor(strategy.deck))
    agent = strategy.agent_name.removeprefix("infostate_").strip().lower()
    if "counter" in agent:
        pilot_family = "counter"
    elif "surge" in agent:
        pilot_family = "surge"
    elif "pressure" in agent:
        pilot_family = "pressure"
    elif "closure" in agent:
        pilot_family = "closure"
    else:
        pilot_family = "balanced"
    mulligan = str(strategy.mulligan_policy)
    if "outcome" in mulligan:
        mulligan_bin = "outcome"
    elif "business" in mulligan:
        mulligan_bin = "business"
    elif "land_band" in mulligan:
        mulligan_bin = "landband"
    else:
        mulligan_bin = "other"
    desc.update({"pilot_family": pilot_family, "mulligan_bin": mulligan_bin})
    return desc


def gameplay_cell_id(strategy: StrategyBundle) -> str:
    desc = strategy_descriptor(strategy)
    keys = (
        "size",
        "land_bin",
        "force_bin",
        "counter_bin",
        "threat_bin",
        "life_bias",
        "pilot_family",
        "mulligan_bin",
    )
    return "|".join(str(desc[key]) for key in keys)


def strategy_from_deck_template(
    deck: DeckVector,
    template: PilotTemplate,
    *,
    strategy_id: str,
    deck_name: str,
) -> StrategyBundle:
    deck.validate()
    return StrategyBundle(
        strategy_id=strategy_id,
        deck_name=deck_name,
        deck=deck,
        agent_name=template.agent_name,
        mulligan_policy=template.mulligan_policy,
    )


def candidate_from_strategy(
    strategy: StrategyBundle,
    *,
    oracle_family: str,
    source: str,
) -> FiniteOracleCandidate:
    return FiniteOracleCandidate(strategy=strategy, oracle_family=oracle_family, source=source)


def seed_candidates_from_strategies(
    strategies: Sequence[StrategyBundle],
    *,
    prefix: str = "gme_seed",
) -> list[FiniteOracleCandidate]:
    out: list[FiniteOracleCandidate] = []
    for index, seed in enumerate(strategies, 1):
        for template_index, template in enumerate(pilot_templates_for_deck(seed.deck), 1):
            strategy = strategy_from_deck_template(
                seed.deck,
                template,
                strategy_id=f"{prefix}_{index:02d}_{template.family}",
                deck_name=f"{prefix}_{seed.strategy_id}",
            )
            out.append(
                candidate_from_strategy(
                    strategy,
                    oracle_family="gameplay_map_elites_seed",
                    source=f"seeded from {seed.strategy_id} with bounded pilot template {template.family}",
                )
            )
    return dedupe_candidates(out)


def mutate_candidate(
    parent: StrategyBundle,
    rng: Random,
    *,
    generation: int,
    index: int,
    prefix: str = "gme",
) -> FiniteOracleCandidate:
    steps = rng.choice([1, 1, 2, 2, 3, 5])
    deck = parent.deck
    for _ in range(20):
        mutated = mutate_deck(deck, rng, steps=steps)
        if plausibility_filter(mutated):
            deck = mutated
            break
    templates = pilot_templates_for_deck(deck)
    template = rng.choice(templates)
    desc = deck_descriptor(deck)
    short = f"{deck.size}_{desc['threat_bin']}_{desc['counter_bin']}_{template.family}"
    strategy = strategy_from_deck_template(
        deck,
        template,
        strategy_id=f"{prefix}_g{generation:02d}_{index:03d}_{short}",
        deck_name=f"gameplay_mutation_of_{parent.strategy_id}",
    )
    return candidate_from_strategy(
        strategy,
        oracle_family="gameplay_map_elites_mutation",
        source=f"generation={generation}; parent={parent.strategy_id}; mutation_steps={steps}; template={template.family}",
    )


def random_candidate(
    rng: Random,
    *,
    generation: int,
    index: int,
    prefix: str = "gme",
) -> FiniteOracleCandidate:
    for _ in range(200):
        deck = random_deck(rng)
        if plausibility_filter(deck):
            break
    else:  # pragma: no cover - random_deck should eventually hit plausibility easily
        deck = DeckVector(40, 24, 6, 4, 3, 3)
    template = rng.choice(pilot_templates_for_deck(deck))
    desc = deck_descriptor(deck)
    short = f"{deck.size}_{desc['threat_bin']}_{desc['counter_bin']}_{template.family}"
    strategy = strategy_from_deck_template(
        deck,
        template,
        strategy_id=f"{prefix}_g{generation:02d}_{index:03d}_{short}",
        deck_name="gameplay_random_plausible",
    )
    return candidate_from_strategy(
        strategy,
        oracle_family="gameplay_map_elites_random",
        source=f"generation={generation}; random plausible deck; template={template.family}",
    )


def dedupe_candidates(
    candidates: Iterable[FiniteOracleCandidate],
    *,
    forbidden_signatures: Iterable[tuple[object, ...]] = (),
) -> list[FiniteOracleCandidate]:
    forbidden = set(forbidden_signatures)
    seen_signatures: set[tuple[object, ...]] = set()
    seen_ids: set[str] = set()
    out: list[FiniteOracleCandidate] = []
    for candidate in candidates:
        signature = strategy_signature(candidate.strategy)
        strategy_id = candidate.strategy.strategy_id
        if signature in forbidden or signature in seen_signatures or strategy_id in seen_ids:
            continue
        seen_signatures.add(signature)
        seen_ids.add(strategy_id)
        out.append(candidate)
    return out


def update_archive(
    archive: dict[str, GameplayEliteRecord],
    candidates_by_id: Mapping[str, FiniteOracleCandidate],
    scored_rows: Sequence[Mapping[str, object]],
    *,
    generation: int,
    min_games: int = 1,
) -> list[GameplayEliteRecord]:
    """Insert gameplay-scored candidates into a MAP-Elites archive.

    Quality is actual opponent-mixture rollout score, with a hard truncation penalty.  Confidence lower bound is recorded but not used to select cells,
    because this oracle is an exploration generator rather than a promotion gate.
    """

    changed: list[GameplayEliteRecord] = []
    for row in scored_rows:
        strategy_id = str(row["candidate_strategy"])
        candidate = candidates_by_id.get(strategy_id)
        if candidate is None:
            continue
        games = int(row.get("games", 0))
        truncations = int(row.get("truncations", 0))
        if games < min_games:
            continue
        mean = float(row["mixture_mean_score"])
        quality = mean - 0.25 * truncations
        strategy = candidate.strategy
        cell = gameplay_cell_id(strategy)
        desc = strategy_descriptor(strategy)
        record = GameplayEliteRecord(
            cell_id=cell,
            strategy_id=strategy_id,
            generation=int(generation),
            quality=float(quality),
            mean_score=mean,
            ci_low=float(row.get("mixture_ci_low", 0.0)),
            games=games,
            truncations=truncations,
            oracle_family=str(row.get("oracle_family", candidate.oracle_family)),
            source=candidate.source,
            deck_size=strategy.deck.size,
            island=strategy.deck.island,
            counterspell=strategy.deck.counterspell,
            force=strategy.deck.force,
            jace=strategy.deck.jace,
            overlord=strategy.deck.overlord,
            agent_name=strategy.agent_name,
            mulligan_policy=str(strategy.mulligan_policy),
            descriptors=desc,
        )
        incumbent = archive.get(cell)
        if incumbent is None or (record.quality, record.ci_low, -record.truncations) > (
            incumbent.quality,
            incumbent.ci_low,
            -incumbent.truncations,
        ):
            archive[cell] = record
            changed.append(record)
    return changed


def choose_parents(
    archive: Mapping[str, GameplayEliteRecord],
    candidates_by_id: Mapping[str, FiniteOracleCandidate],
    rng: Random,
    *,
    count: int,
) -> list[StrategyBundle]:
    records = sorted(
        archive.values(),
        key=lambda record: (record.quality, record.ci_low, -record.truncations, record.strategy_id),
        reverse=True,
    )
    if not records:
        return []
    top = records[: max(1, min(len(records), count * 2))]
    parents: list[StrategyBundle] = []
    for _ in range(count):
        # Bias toward stronger elites without removing lower-quality cells from
        # the mutation frontier.
        record = rng.choice(top[: max(1, len(top) // 2)] if rng.random() < 0.75 else top)
        candidate = candidates_by_id[record.strategy_id]
        parents.append(candidate.strategy)
    return parents


def archive_summary(archive: Mapping[str, GameplayEliteRecord]) -> dict[str, object]:
    records = list(archive.values())
    if not records:
        return {
            "cells": 0,
            "best_mean_score": 0.0,
            "best_ci_low": 0.0,
            "total_games": 0,
            "truncations": 0,
            "families": {},
        }
    families: dict[str, int] = {}
    for record in records:
        family = str(record.descriptors.get("pilot_family", "unknown"))
        families[family] = families.get(family, 0) + 1
    best = max(records, key=lambda record: (record.mean_score, record.ci_low, -record.truncations))
    return {
        "cells": len(records),
        "best_strategy_id": best.strategy_id,
        "best_cell_id": best.cell_id,
        "best_mean_score": best.mean_score,
        "best_ci_low": best.ci_low,
        "total_games": sum(record.games for record in records),
        "truncations": sum(record.truncations for record in records),
        "families": dict(sorted(families.items())),
    }
