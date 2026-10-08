from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .confidence_floor import FloorSummary, floor_from_estimates
from .deckspace import DeckVector
from .payoff import StrategyBundle
from .psro import PairEstimate, strategy_signature
from .psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population


@dataclass(frozen=True)
class StressPanelEntry:
    """One out-of-distribution opponent used to stress a focal PSRO target.

    The panel is deliberately not a promotion candidate list.  It is a transfer
    and falsification set: branch-frontier candidates, degenerate threat shapes,
    and counter-control shapes that were not part of the original eight-strategy
    confidence floor.
    """

    strategy: StrategyBundle
    stress_family: str
    rationale: str

    def as_dict(self) -> dict[str, object]:
        return {
            **self.strategy.as_dict(),
            "stress_family": self.stress_family,
            "rationale": self.rationale,
            "signature": list(strategy_signature(self.strategy)),
        }


@dataclass(frozen=True)
class TransferStressSummary:
    focal_strategy: str
    panel_size: int
    families: tuple[str, ...]
    total_games: int
    truncations: int
    min_mean_score: float
    min_ci_low: float
    weakest_mean_opponent: str
    weakest_ci_opponent: str
    mean_floor_cleared: bool
    confidence_floor_cleared: bool
    threshold: float = 0.5

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _deck(size: int, island: int, counterspell: int, force: int, jace: int, overlord: int) -> DeckVector:
    deck = DeckVector(size, island, counterspell, force, jace, overlord)
    deck.validate()
    return deck


def _entry(
    strategy_id: str,
    deck_name: str,
    deck: DeckVector,
    agent_name: str,
    mulligan_policy: str,
    stress_family: str,
    rationale: str,
) -> StressPanelEntry:
    return StressPanelEntry(
        strategy=StrategyBundle(
            strategy_id=strategy_id,
            deck_name=deck_name,
            deck=deck,
            agent_name=agent_name,
            mulligan_policy=mulligan_policy,
        ),
        stress_family=stress_family,
        rationale=rationale,
    )


def rev0092_admitted_strategy(root: str | Path) -> StrategyBundle:
    """Return the current admitted PSRO response targeted by rev0094-rev0101."""

    return candidate_by_id(current_oracle_catalog(root), REV0092_ADMITTED_STRATEGY_ID).strategy


def rev0101_transfer_stress_panel() -> list[StressPanelEntry]:
    """Construct a fixed OOD panel for the admitted PSRO response.

    The panel mixes four branch-frontier controls from rev0094-rev0098 with
    hand-specified degenerate threat and counter-control shapes.  The latter are
    intentionally outside the old response-population ecology; their role is to
    reveal transfer holes, not to claim plausibility or optimality.
    """

    return [
        _entry(
            "ood_branch_learned_jace60",
            "rev0098_learned_frontier_jace60",
            _deck(60, 28, 11, 8, 9, 4),
            "learned_response_rev0097_g1_03",
            "land_band",
            "branch_frontier",
            "best learned-response holdout challenger from rev0098 common-target retest, remeasured with the PSRO target as focal strategy",
        ),
        _entry(
            "ood_branch_gme_pressure40",
            "rev0095_gme_frontier_pressure40",
            _deck(40, 16, 12, 0, 7, 5),
            "infostate_threat_pressure",
            "land_band_business",
            "branch_frontier",
            "best gameplay-MAP-Elites holdout point estimate from rev0095/rev0098",
        ),
        _entry(
            "ood_branch_finite_counterwall40",
            "rev0094_finite_counterwall40",
            _deck(40, 15, 15, 5, 2, 3),
            "infostate_counter_guard",
            "mulligan_outcome_ranker_rev0027",
            "branch_frontier",
            "best finite-catalog stress holdout challenger from rev0094/rev0098",
        ),
        _entry(
            "ood_branch_frozen_mlp_counter60",
            "rev0096_frozen_mlp_counterwall60",
            _deck(60, 25, 21, 4, 5, 5),
            "mlp_ranker_blend_counter_rev0023",
            "land_band_business",
            "branch_frontier",
            "frozen rev0023 neural oracle winner from rev0096/rev0098, retained as a negative-control frontier row",
        ),
        _entry(
            "ood_hyper_overlord40",
            "hyper_overlord_40_no_interaction",
            _deck(40, 20, 0, 0, 0, 20),
            "infostate_threat_surge",
            "land_band",
            "degenerate_threat",
            "extreme threat-density shape absent from the incumbent ecology; asks whether counter-wall target folds to raw closure density",
        ),
        _entry(
            "ood_landtight_overlord40",
            "landtight_overlord_40_low_counter",
            _deck(40, 16, 4, 0, 0, 20),
            "infostate_threat_surge",
            "land_band_business",
            "degenerate_threat",
            "land-tight all-Overlord pressure variant with just enough interaction to perturb simple anti-aggro assumptions",
        ),
        _entry(
            "ood_threatmax60",
            "threatmax_60_mixed",
            _deck(60, 27, 6, 4, 8, 15),
            "infostate_threat_surge",
            "land_band_business",
            "degenerate_threat",
            "large-deck threat-saturation stressor with both Jace and Overlord rather than the old closure/surge seed shapes",
        ),
        _entry(
            "ood_forceheavy_pressure40",
            "forceheavy_pressure_40",
            _deck(40, 17, 10, 8, 3, 2),
            "infostate_threat_pressure",
            "land_band_business",
            "force_pressure",
            "land-light Force-heavy pressure deck outside the admitted target's 60-card counter-wall shape",
        ),
        _entry(
            "ood_counter_jace40",
            "counter_jace_40_no_overlord",
            _deck(40, 15, 20, 0, 5, 0),
            "infostate_counter_guard",
            "land_band_business",
            "counter_control",
            "40-card counter-control/Jace-only axis; probes whether mirror-control closure, not threat density, is the weak transfer face",
        ),
        _entry(
            "ood_force_counter_jace40",
            "force_counter_jace_40_no_overlord",
            _deck(40, 14, 18, 4, 4, 0),
            "infostate_counter_guard",
            "land_band_business",
            "counter_control",
            "Force-enabled 40-card no-Overlord counter-control variant near the rev0100 confidence-floor boundary",
        ),
        _entry(
            "ood_jacecontrol60",
            "jacecontrol_60_no_overlord",
            _deck(60, 28, 20, 4, 8, 0),
            "infostate_threat_pressure",
            "land_band_business",
            "counter_control",
            "60-card Jace-control/no-Overlord variant; early probes suggested this may be a weak transfer axis",
        ),
        _entry(
            "ood_supercounter60",
            "supercounter_60_low_land",
            _deck(60, 20, 30, 4, 3, 3),
            "infostate_counter_guard",
            "land_band_business",
            "counter_control",
            "low-land maximum-counter stressor; intentionally outside plausibility priors to test hard counter-density transfer",
        ),
        _entry(
            "ood_lowland_counter_jace60",
            "lowland_counter_jace_60",
            _deck(60, 25, 30, 0, 5, 0),
            "infostate_counter_guard",
            "land_band_business",
            "counter_control",
            "low-land no-Force counter-control axis with enough Jace to threaten deck-out rather than combat closure",
        ),
    ]


def audit_transfer_stress_panel(
    entries: Sequence[StressPanelEntry],
    *,
    root: str | Path,
    focal: StrategyBundle | None = None,
) -> dict[str, object]:
    """Validate that the stress panel is unique, legal, and outside old support."""

    focal_strategy = focal if focal is not None else rev0092_admitted_strategy(root)
    old_population = current_response_population(Path(root) / "data" / "seed_decks.json")
    old_signatures = {strategy_signature(strategy): strategy.strategy_id for strategy in old_population}
    focal_signature = strategy_signature(focal_strategy)
    seen_ids: set[str] = set()
    seen_signatures: dict[tuple[object, ...], str] = {}
    duplicate_ids: list[str] = []
    duplicate_signatures: list[dict[str, str]] = []
    duplicate_old_population: list[dict[str, str]] = []
    duplicate_focal: list[str] = []
    families: dict[str, int] = {}
    invalid: list[dict[str, str]] = []
    for entry in entries:
        strategy = entry.strategy
        if strategy.strategy_id in seen_ids:
            duplicate_ids.append(strategy.strategy_id)
        seen_ids.add(strategy.strategy_id)
        try:
            strategy.deck.validate()
        except Exception as exc:  # pragma: no cover - defensive, validated at construction
            invalid.append({"strategy_id": strategy.strategy_id, "error": str(exc)})
        signature = strategy_signature(strategy)
        prior = seen_signatures.get(signature)
        if prior is not None:
            duplicate_signatures.append({"strategy_id": strategy.strategy_id, "duplicate_of": prior})
        seen_signatures[signature] = strategy.strategy_id
        old_duplicate = old_signatures.get(signature)
        if old_duplicate is not None:
            duplicate_old_population.append({"strategy_id": strategy.strategy_id, "duplicate_of_population": old_duplicate})
        if signature == focal_signature:
            duplicate_focal.append(strategy.strategy_id)
        families[entry.stress_family] = families.get(entry.stress_family, 0) + 1
    return {
        "schema": "muc5.transfer_stress_panel_audit.v1",
        "passed": not duplicate_ids and not duplicate_signatures and not invalid and not duplicate_focal,
        "entries": len(entries),
        "families": families,
        "duplicate_ids": duplicate_ids,
        "duplicate_signatures": duplicate_signatures,
        "duplicate_old_population": duplicate_old_population,
        "duplicate_focal": duplicate_focal,
        "invalid_decks": invalid,
        "old_population_duplicates_are_warnings": True,
    }


def summarize_transfer_stress(
    focal_strategy: str,
    entries: Sequence[StressPanelEntry],
    estimates: Sequence[PairEstimate],
    *,
    threshold: float = 0.5,
) -> TransferStressSummary:
    if not estimates:
        raise ValueError("at least one transfer-stress estimate is required")
    by_id = {entry.strategy.strategy_id: entry for entry in entries}
    missing = [estimate.opponent_strategy for estimate in estimates if estimate.opponent_strategy not in by_id]
    if missing:
        raise ValueError(f"estimates contain opponents not in stress panel: {missing}")
    floor: FloorSummary = floor_from_estimates(focal_strategy, estimates, threshold=threshold)
    families = tuple(sorted({entry.stress_family for entry in entries}))
    return TransferStressSummary(
        focal_strategy=focal_strategy,
        panel_size=len(entries),
        families=families,
        total_games=floor.total_games,
        truncations=floor.truncations,
        min_mean_score=floor.min_mean_score,
        min_ci_low=floor.min_ci_low,
        weakest_mean_opponent=floor.weakest_mean_opponent,
        weakest_ci_opponent=floor.weakest_ci_opponent,
        mean_floor_cleared=bool(floor.min_mean_score > float(threshold) and floor.truncations == 0),
        confidence_floor_cleared=bool(floor.passed_over_half_by_ci_low),
        threshold=float(threshold),
    )


def estimate_panel_rows(estimates: Sequence[PairEstimate], entries: Sequence[StressPanelEntry], *, stage: str) -> list[dict[str, object]]:
    by_id = {entry.strategy.strategy_id: entry for entry in entries}
    rows: list[dict[str, object]] = []
    for estimate in estimates:
        entry = by_id[estimate.opponent_strategy]
        payload = estimate.as_dict()
        payload.update(
            {
                "stage": stage,
                "stress_family": entry.stress_family,
                "rationale": entry.rationale,
                "opponent_agent_name": entry.strategy.agent_name,
                "opponent_mulligan_policy": str(entry.strategy.mulligan_policy),
                "opponent_deck_size": entry.strategy.deck.size,
                "score_excess_over_half": float(estimate.mean_score - 0.5),
                "ci_low_excess_over_half": float(estimate.ci_low - 0.5),
            }
        )
        rows.append(payload)
    rows.sort(key=lambda row: (str(row["stress_family"]), float(row["mean_score"]), str(row["opponent_strategy"])))
    return rows


def family_summary_rows(estimates: Sequence[PairEstimate], entries: Sequence[StressPanelEntry], *, threshold: float = 0.5) -> list[dict[str, object]]:
    by_id = {entry.strategy.strategy_id: entry for entry in entries}
    groups: dict[str, list[PairEstimate]] = {}
    for estimate in estimates:
        groups.setdefault(by_id[estimate.opponent_strategy].stress_family, []).append(estimate)
    rows: list[dict[str, object]] = []
    for family, group in sorted(groups.items()):
        floor = floor_from_estimates("family_focal", group, threshold=threshold)
        rows.append(
            {
                "stress_family": family,
                "opponents": len(group),
                "games": floor.total_games,
                "truncations": floor.truncations,
                "min_mean_score": floor.min_mean_score,
                "min_ci_low": floor.min_ci_low,
                "weakest_mean_opponent": floor.weakest_mean_opponent,
                "weakest_ci_opponent": floor.weakest_ci_opponent,
                "mean_floor_cleared": bool(floor.min_mean_score > threshold and floor.truncations == 0),
                "confidence_floor_cleared": floor.passed_over_half_by_ci_low,
            }
        )
    return rows


__all__ = [
    "StressPanelEntry",
    "TransferStressSummary",
    "audit_transfer_stress_panel",
    "estimate_panel_rows",
    "family_summary_rows",
    "rev0092_admitted_strategy",
    "rev0101_transfer_stress_panel",
    "summarize_transfer_stress",
]
