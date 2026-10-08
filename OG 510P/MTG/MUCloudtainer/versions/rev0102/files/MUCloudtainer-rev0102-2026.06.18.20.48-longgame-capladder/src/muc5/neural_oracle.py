from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .deckspace import DeckVector
from .gameplay_map_elites import dedupe_candidates, strategy_descriptor
from .mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from .payoff import StrategyBundle
from .psro import FiniteOracleCandidate, strategy_signature
from .ranker_policy import default_mlp_ranker_model_path, load_mlp_ranker_model

NEURAL_AGENT_NAMES: tuple[str, ...] = (
    "mlp_ranker_rev0023",
    "mlp_ranker_blend_threat_rev0023",
    "mlp_ranker_blend_counter_rev0023",
    "mlp_ranker_blend_patient_rev0023",
)


@dataclass(frozen=True)
class NeuralDeckSource:
    """Deck proposed to a neural-action-ranker oracle.

    The neural branch here is deliberately bounded: the pilot is a frozen JSON
    MLP action ranker, while decks are drawn from current PSRO/population/GME
    evidence.  This answers whether the old neural policy family can act as a
    response oracle before we spend budget on fresh RL training.
    """

    label: str
    deck: DeckVector
    preferred_mulligan: str
    source: str
    priority: float = 0.0

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload.update({f"deck_{key}": value for key, value in self.deck.counts().items()})
        payload["deck_size"] = self.deck.size
        payload["deck_signature"] = self.deck.as_tuple()
        return payload


def neural_model_audit() -> dict[str, object]:
    """Return lightweight integrity facts for the dormant rev0023 MLP model."""

    path = default_mlp_ranker_model_path()
    model = load_mlp_ranker_model(path)
    return {
        "model_path": path.name,
        "model_id": model.model_id,
        "source_revision": model.source_revision,
        "feature_count": len(model.feature_names),
        "hidden_size": model.hidden_size,
        "activation": model.activation,
        "coefficients_finite": all(
            all(float(value) == float(value) for value in row) for row in model.hidden_weights
        )
        and all(float(value) == float(value) for value in model.hidden_bias)
        and all(float(value) == float(value) for value in model.output_weights)
        and float(model.output_bias) == float(model.output_bias),
        "training_summary": dict(model.training_summary or {}),
    }


def _source_from_strategy(strategy: StrategyBundle, *, label: str, priority: float) -> NeuralDeckSource:
    return NeuralDeckSource(
        label=label,
        deck=strategy.deck,
        preferred_mulligan=str(strategy.mulligan_policy),
        source=f"strategy:{strategy.strategy_id}",
        priority=float(priority),
    )


def deck_sources_from_population_and_gme(
    population: Sequence[StrategyBundle],
    admitted: StrategyBundle,
    *,
    gme_archive_path: str | Path,
    gme_limit: int = 8,
) -> list[NeuralDeckSource]:
    """Collect a bounded, deduplicated deck menu for the neural oracle."""

    sources: list[NeuralDeckSource] = [_source_from_strategy(admitted, label="admitted_psro_response", priority=100.0)]
    for index, strategy in enumerate(population, 1):
        sources.append(_source_from_strategy(strategy, label=f"population_{index:02d}", priority=40.0 - index))

    path = Path(gme_archive_path)
    if path.exists():
        rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
        rows.sort(
            key=lambda row: (
                float(row.get("mean_score", row.get("quality", 0.0)) or 0.0),
                float(row.get("ci_low", 0.0) or 0.0),
                -int(float(row.get("truncations", 0) or 0)),
                row.get("strategy_id", ""),
            ),
            reverse=True,
        )
        for index, row in enumerate(rows[: int(gme_limit)], 1):
            deck = DeckVector(
                int(row.get("deck_size", row.get("size", 0))),
                int(row.get("island", row.get("deck_Island", 0))),
                int(row.get("counterspell", row.get("deck_Counterspell", 0))),
                int(row.get("force", row.get("deck_ForceOfWill", 0))),
                int(row.get("jace", row.get("deck_JaceTheMindSculptor", 0))),
                int(row.get("overlord", row.get("deck_OverlordOfTheFloodpits", 0))),
            )
            deck.validate()
            mulligan = str(row.get("mulligan_policy", POLICY_LAND_BAND))
            sources.append(
                NeuralDeckSource(
                    label=f"gme_elite_{index:02d}",
                    deck=deck,
                    preferred_mulligan=mulligan,
                    source=f"rev0095_archive:{row.get('strategy_id', index)}",
                    priority=70.0 - index,
                )
            )

    # Keep the highest-priority provenance for each deck.  Sort by priority so
    # a stable index is not accidentally determined by CSV/file-system order.
    by_deck: dict[tuple[int, int, int, int, int, int], NeuralDeckSource] = {}
    for source in sources:
        key = source.deck.as_tuple()
        incumbent = by_deck.get(key)
        if incumbent is None or (source.priority, source.label) > (incumbent.priority, incumbent.label):
            by_deck[key] = source
    return sorted(by_deck.values(), key=lambda item: (item.priority, item.label), reverse=True)


def _agent_slug(agent_name: str) -> str:
    return (
        agent_name.removeprefix("mlp_ranker_")
        .removeprefix("mlp_")
        .replace("_rev0023", "")
        .replace("blend_", "")
        .strip("_")
        or "mlp"
    )


def neural_response_candidates(
    deck_sources: Sequence[NeuralDeckSource],
    *,
    agent_names: Sequence[str] = NEURAL_AGENT_NAMES,
    max_decks: int = 6,
    forbidden_signatures: Iterable[tuple[object, ...]] = (),
) -> list[FiniteOracleCandidate]:
    """Generate bounded neural-pilot response candidates from deck sources."""

    candidates: list[FiniteOracleCandidate] = []
    for deck_index, source in enumerate(deck_sources[: int(max_decks)], 1):
        desc = strategy_descriptor(
            StrategyBundle(
                strategy_id=f"tmp_{deck_index}",
                deck_name=source.label,
                deck=source.deck,
                agent_name="infostate_heuristic",
                mulligan_policy=source.preferred_mulligan,
            )
        )
        mulligans = []
        for policy in (source.preferred_mulligan, POLICY_LAND_BAND_BUSINESS, POLICY_LAND_BAND):
            if policy not in mulligans:
                mulligans.append(policy)
        # One preferred mulligan plus one generic business/landband alternative;
        # this tests the neural pilot rather than exploding the mulligan search.
        mulligans = mulligans[:2]
        for agent_name in agent_names:
            for mulligan_index, mulligan in enumerate(mulligans, 1):
                slug = _agent_slug(agent_name)
                strategy_id = (
                    f"neural_{deck_index:02d}_{slug}_m{mulligan_index}_"
                    f"{source.deck.size}_{desc['threat_bin']}_{desc['counter_bin']}"
                )
                strategy = StrategyBundle(
                    strategy_id=strategy_id,
                    deck_name=f"neural_oracle_{source.label}",
                    deck=source.deck,
                    agent_name=agent_name,
                    mulligan_policy=str(mulligan),
                )
                candidates.append(
                    FiniteOracleCandidate(
                        strategy=strategy,
                        oracle_family="frozen_mlp_action_ranker_response",
                        source=(
                            f"deck_source={source.source}; deck_label={source.label}; "
                            f"agent={agent_name}; mulligan={mulligan}; frozen rev0023 MLP action-ranker oracle"
                        ),
                    )
                )
    return dedupe_candidates(candidates, forbidden_signatures=forbidden_signatures)


def candidate_catalog_rows(candidates: Sequence[FiniteOracleCandidate], *, sources: Sequence[NeuralDeckSource]) -> list[dict[str, object]]:
    source_by_deck = {source.deck.as_tuple(): source for source in sources}
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        strategy = candidate.strategy
        source = source_by_deck.get(strategy.deck.as_tuple())
        row = candidate.as_dict()
        row.update({f"desc_{key}": value for key, value in strategy_descriptor(strategy).items()})
        if source is not None:
            row.update({f"source_{key}": value for key, value in source.as_dict().items() if key != "deck"})
        rows.append(row)
    return rows


def duplicate_candidate_ids(population: Sequence[StrategyBundle], candidates: Sequence[FiniteOracleCandidate]) -> dict[str, str]:
    population_signatures = {strategy_signature(strategy): strategy.strategy_id for strategy in population}
    out: dict[str, str] = {}
    for candidate in candidates:
        duplicate = population_signatures.get(strategy_signature(candidate.strategy))
        if duplicate is not None:
            out[candidate.strategy.strategy_id] = duplicate
    return out
