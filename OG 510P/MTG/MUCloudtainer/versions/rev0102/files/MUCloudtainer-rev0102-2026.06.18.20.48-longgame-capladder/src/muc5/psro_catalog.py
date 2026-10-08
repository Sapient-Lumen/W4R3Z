from __future__ import annotations

import csv
from pathlib import Path
from typing import Sequence

from .deckspace import DeckVector
from .payoff import StrategyBundle
from .psro import FiniteOracleCandidate, strategy_signature
from .response_matrix import rev0067_response_matrix_arms
from .terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN


CURRENT_RESPONSE_POPULATION_ORDER: tuple[str, ...] = (
    "guard_counter_wall40",
    "guard_counter_wall60",
    "pub_threat40_closure",
    "pub_threat40_pressure",
    "pub_threat40_surge",
    "pub_threat60_closure",
    "pub_threat60_pressure",
    "pub_threat60_surge",
)

REV0092_ADMITTED_STRATEGY_ID = "oracle_map_08_60_mixed_threats_counter_wall"


def current_response_population(seed_decks_path: str | Path) -> list[StrategyBundle]:
    """Return the frozen eight-strategy response ecology used by rev0092+.

    This was originally embedded in a runner script.  Keeping it in package code
    makes later PSRO rounds, stress panels, and tests call the same population
    constructor instead of copying a fragile strategy-order literal.
    """

    by_id: dict[str, StrategyBundle] = {}
    for arm in rev0067_response_matrix_arms(Path(seed_decks_path)):
        by_id.setdefault(arm.target.strategy_id, arm.target)
        by_id.setdefault(arm.opponent.strategy_id, arm.opponent)
    missing = [strategy_id for strategy_id in CURRENT_RESPONSE_POPULATION_ORDER if strategy_id not in by_id]
    if missing:
        raise ValueError(f"missing response-population strategies: {missing}")
    return [by_id[strategy_id] for strategy_id in CURRENT_RESPONSE_POPULATION_ORDER]


def information_upgrade_candidates(population: Sequence[StrategyBundle]) -> list[FiniteOracleCandidate]:
    """Hold deck and mulligan fixed while making rev0091 information usable."""

    out: list[FiniteOracleCandidate] = []
    for strategy in population:
        profile = strategy.agent_name.strip().lower().replace("-", "_")
        out.append(
            FiniteOracleCandidate(
                strategy=StrategyBundle(
                    strategy_id=f"oracle_info_{strategy.strategy_id}",
                    deck_name=strategy.deck_name,
                    deck=strategy.deck,
                    agent_name=f"infostate_{profile}",
                    mulligan_policy=strategy.mulligan_policy,
                ),
                oracle_family="information_state_policy_upgrade",
                source=f"same deck/mulligan as {strategy.strategy_id}; policy consumes durable information state",
            )
        )
    return out


def map_elites_candidates(archive_path: str | Path, limit: int = 8) -> list[FiniteOracleCandidate]:
    """Reuse the old descriptor archive as a finite proposal oracle.

    rev0014 fitness was static, so no archived quality number is treated as game
    evidence.  These are proposals; current gameplay decides whether any is a
    response to the restricted-game mixture.
    """

    rows = list(csv.DictReader(Path(archive_path).open()))
    preferred_keys = [
        ("40", "mixed_threats", "counter_mid"),
        ("40", "overlord_heavy", "counter_mid"),
        ("40", "jace_heavy", "counter_mid"),
        ("40", "mixed_threats", "counter_wall"),
        ("60", "mixed_threats", "counter_mid"),
        ("60", "overlord_heavy", "counter_mid"),
        ("60", "jace_heavy", "counter_mid"),
        ("60", "mixed_threats", "counter_wall"),
    ]
    selected: list[dict[str, str]] = []
    for key in preferred_keys:
        row = next(
            (
                item
                for item in rows
                if (item["deck_size"], item["desc_threat_bin"], item["desc_counter_bin"]) == key
            ),
            None,
        )
        if row is not None:
            selected.append(row)

    out: list[FiniteOracleCandidate] = []
    for index, row in enumerate(selected[:limit], 1):
        deck = DeckVector(
            int(row["deck_size"]),
            int(row["island"]),
            int(row["counterspell"]),
            int(row["force"]),
            int(row["jace"]),
            int(row["overlord"]),
        )
        deck.validate()
        threat_bin = row["desc_threat_bin"]
        counter_bin = row["desc_counter_bin"]
        if counter_bin == "counter_wall":
            profile = "counter_guard"
            mulligan = CF34_MULLIGAN
        elif threat_bin == "overlord_heavy":
            profile = "threat_surge"
            mulligan = THREAT_MULLIGAN
        elif threat_bin == "jace_heavy":
            profile = "threat_pressure"
            mulligan = THREAT_MULLIGAN
        else:
            profile = "threat_closure"
            mulligan = THREAT_MULLIGAN
        strategy_id = f"oracle_map_{index:02d}_{deck.size}_{threat_bin}_{counter_bin}"
        out.append(
            FiniteOracleCandidate(
                strategy=StrategyBundle(
                    strategy_id=strategy_id,
                    deck_name=f"rev0014_cell_{row['cell_id']}",
                    deck=deck,
                    agent_name=f"infostate_{profile}",
                    mulligan_policy=mulligan,
                ),
                oracle_family="static_map_elites_candidate",
                source=(
                    f"rev0014 cell {row['cell_id']} quality={float(row['quality']):.6f}; "
                    "descriptor archive used only for proposal"
                ),
            )
        )
    return out


def current_oracle_catalog(root: str | Path, population: Sequence[StrategyBundle] | None = None) -> list[FiniteOracleCandidate]:
    root_path = Path(root)
    base_population = list(population) if population is not None else current_response_population(root_path / "data" / "seed_decks.json")
    return information_upgrade_candidates(base_population) + map_elites_candidates(root_path / "data" / "rev0014_map_elites_archive.csv")


def candidate_by_id(candidates: Sequence[FiniteOracleCandidate], strategy_id: str) -> FiniteOracleCandidate:
    matches = [candidate for candidate in candidates if candidate.strategy.strategy_id == strategy_id]
    if len(matches) != 1:
        raise ValueError(f"expected one candidate {strategy_id!r}, found {len(matches)}")
    return matches[0]


def incumbent_population_candidates(population: Sequence[StrategyBundle]) -> list[FiniteOracleCandidate]:
    """Expose incumbents as pure-response controls without pretending they expand the population."""

    return [
        FiniteOracleCandidate(
            strategy=strategy,
            oracle_family="incumbent_population_control",
            source="existing population strategy tested as a pure response control",
        )
        for strategy in population
    ]


def duplicate_signatures(population: Sequence[StrategyBundle], candidates: Sequence[FiniteOracleCandidate]) -> dict[str, str]:
    """Return candidate IDs that duplicate a population strategy signature."""

    population_signatures = {strategy_signature(strategy): strategy.strategy_id for strategy in population}
    out: dict[str, str] = {}
    for candidate in candidates:
        duplicate = population_signatures.get(strategy_signature(candidate.strategy))
        if duplicate is not None:
            out[candidate.strategy.strategy_id] = duplicate
    return out
