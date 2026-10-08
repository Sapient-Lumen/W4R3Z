from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .cards import CARD_ORDER
from .deckspace import DeckVector
from .payoff import StrategyBundle


@dataclass(frozen=True)
class OracleBranchSpec:
    branch_id: str
    revision: str
    family: str
    scores_path: str
    screen_stages: tuple[str, ...]
    holdout_stage: str = "holdout"
    training_stages: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateOptimism:
    branch_id: str
    candidate_strategy: str
    screen_stage: str
    screen_mean: float
    screen_ci_low: float
    holdout_mean: float
    holdout_ci_low: float
    mean_optimism: float
    ci_low_optimism: float
    screen_games: int
    holdout_games: int
    agent_name: str
    mulligan_policy: str
    deck_size: int
    oracle_family: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def default_branch_specs() -> tuple[OracleBranchSpec, ...]:
    """Score-table inputs for the post-rev0092 response-oracle family.

    These branches all attacked the same effective PSRO support: the rev0092
    admitted response.  Keeping this list in source code turns what had become
    a narrative comparison into a reproducible audit spine.
    """

    return (
        OracleBranchSpec(
            branch_id="finite_catalog_rev0094",
            revision="rev0094",
            family="static finite catalog / second-oracle stress",
            scores_path="data/rev0094_psro_challenge_scores.csv",
            screen_stages=("selection",),
        ),
        OracleBranchSpec(
            branch_id="gameplay_map_elites_rev0095",
            revision="rev0095",
            family="gameplay MAP-Elites generator",
            scores_path="data/rev0095_gameplay_map_elites_scores.csv",
            screen_stages=("selection_g0", "selection_g1", "selection_g2"),
        ),
        OracleBranchSpec(
            branch_id="frozen_mlp_rev0096",
            revision="rev0096",
            family="frozen rev0023 MLP action ranker",
            scores_path="data/rev0096_neural_oracle_scores.csv",
            screen_stages=("selection",),
        ),
        OracleBranchSpec(
            branch_id="learned_response_rev0097",
            revision="rev0097",
            family="rollout-searched information-state linear response",
            scores_path="data/rev0097_learned_response_oracle_scores.csv",
            screen_stages=("generation0_training", "selection"),
            training_stages=("generation0_training",),
        ),
    )


def read_score_rows(root: str | Path, spec: OracleBranchSpec) -> list[dict[str, object]]:
    path = Path(root) / spec.scores_path
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            parsed = dict(row)
            parsed["branch_id"] = spec.branch_id
            parsed["revision"] = spec.revision
            parsed["branch_family"] = spec.family
            parsed["mixture_mean_score"] = _float(row.get("mixture_mean_score"))
            parsed["mixture_ci_low"] = _float(row.get("mixture_ci_low"))
            parsed["mixture_ci_high"] = _float(row.get("mixture_ci_high"))
            parsed["mixture_standard_error"] = _float(row.get("mixture_standard_error"))
            parsed["games"] = _int(row.get("games"))
            parsed["truncations"] = _int(row.get("truncations"))
            parsed["deck_size"] = _int(row.get("deck_size"))
            parsed["duplicate_of_population"] = _bool(row.get("duplicate_of_population"))
            parsed["deck"] = _json_object(row.get("deck_json"))
            parsed["opponent_scores"] = _json_object(row.get("opponent_scores_json"))
            parsed["mixture_support"] = _json_object(row.get("mixture_support_json"))
            rows.append(parsed)
    return rows


def audit_oracle_selection_bias(root: str | Path, specs: Sequence[OracleBranchSpec] | None = None) -> dict[str, object]:
    specs = tuple(default_branch_specs() if specs is None else specs)
    branch_summaries: list[dict[str, object]] = []
    candidate_pairs: list[CandidateOptimism] = []
    all_score_rows: list[dict[str, object]] = []
    for spec in specs:
        rows = read_score_rows(root, spec)
        all_score_rows.extend(rows)
        summary, pairs = summarize_branch(spec, rows)
        branch_summaries.append(summary)
        candidate_pairs.extend(pairs)

    worst = max(candidate_pairs, key=lambda row: row.mean_optimism, default=None)
    worst_ci = max(candidate_pairs, key=lambda row: row.ci_low_optimism, default=None)
    best_holdout_branch = max(
        branch_summaries,
        key=lambda row: float(row.get("best_holdout_mean", float("-inf"))),
        default=None,
    )
    best_holdout_ci_branch = max(
        branch_summaries,
        key=lambda row: float(row.get("best_holdout_ci_low", float("-inf"))),
        default=None,
    )
    positive_mean_holdouts = [row for row in branch_summaries if float(row.get("best_holdout_mean", 0.0)) > 0.5]
    ci_clearing_holdouts = [row for row in branch_summaries if bool(row.get("best_holdout_clears_challenge_threshold"))]
    training_to_holdout_failures = [
        row for row in candidate_pairs if row.screen_stage in {"generation0_training", "training"} and row.mean_optimism > 0.25
    ]
    branch_best_gaps = [
        row for row in branch_summaries if row.get("best_screen_to_best_holdout_mean_gap") is not None
    ]
    worst_branch_gap = max(
        branch_best_gaps,
        key=lambda row: float(row.get("best_screen_to_best_holdout_mean_gap", 0.0)),
        default=None,
    )
    return {
        "schema": "muc5.rev0098_oracle_selection_bias.v1",
        "branch_specs": [spec.as_dict() for spec in specs],
        "branches": branch_summaries,
        "candidate_pairs": [row.as_dict() for row in candidate_pairs],
        "aggregate": {
            "branches": len(branch_summaries),
            "score_rows": len(all_score_rows),
            "heldout_candidate_pairs": len(candidate_pairs),
            "worst_mean_optimism_pair": None if worst is None else worst.as_dict(),
            "worst_ci_low_optimism_pair": None if worst_ci is None else worst_ci.as_dict(),
            "best_holdout_branch": None if best_holdout_branch is None else best_holdout_branch["branch_id"],
            "best_holdout_mean": None if best_holdout_branch is None else best_holdout_branch["best_holdout_mean"],
            "best_holdout_ci_low_branch": None if best_holdout_ci_branch is None else best_holdout_ci_branch["branch_id"],
            "best_holdout_ci_low": None if best_holdout_ci_branch is None else best_holdout_ci_branch["best_holdout_ci_low"],
            "positive_mean_holdout_branches": [row["branch_id"] for row in positive_mean_holdouts],
            "ci_clearing_holdout_branches": [row["branch_id"] for row in ci_clearing_holdouts],
            "training_to_holdout_failure_count": len(training_to_holdout_failures),
            "branch_best_screen_not_heldout_count": sum(not bool(row.get("best_screen_was_heldout")) for row in branch_summaries),
            "worst_branch_best_screen_to_holdout_gap": None
            if worst_branch_gap is None
            else worst_branch_gap["best_screen_to_best_holdout_mean_gap"],
            "worst_branch_best_screen_to_holdout_gap_branch": None if worst_branch_gap is None else worst_branch_gap["branch_id"],
            "no_branch_cleared_holdout_ci_threshold": not ci_clearing_holdouts,
        },
        "interpretation": (
            "This audit treats training/selection rows as screens and holdout rows as evidence. "
            "Positive selection-to-holdout gaps are winner's-curse evidence, not strategy evidence."
        ),
    }


def summarize_branch(spec: OracleBranchSpec, rows: Sequence[Mapping[str, object]]) -> tuple[dict[str, object], list[CandidateOptimism]]:
    screens = [row for row in rows if str(row.get("stage")) in set(spec.screen_stages)]
    holdouts = [row for row in rows if str(row.get("stage")) == spec.holdout_stage]
    by_candidate_holdout = {str(row.get("candidate_strategy")): row for row in holdouts}
    by_candidate_best_screen: dict[str, Mapping[str, object]] = {}
    for row in screens:
        cid = str(row.get("candidate_strategy"))
        previous = by_candidate_best_screen.get(cid)
        if previous is None or float(row.get("mixture_mean_score", -1.0)) > float(previous.get("mixture_mean_score", -1.0)):
            by_candidate_best_screen[cid] = row
    pairs: list[CandidateOptimism] = []
    for cid, holdout in by_candidate_holdout.items():
        screen = by_candidate_best_screen.get(cid)
        if screen is None:
            continue
        pairs.append(_candidate_optimism(spec.branch_id, screen, holdout))

    best_screen = max(screens, key=lambda row: (float(row.get("mixture_mean_score", -1.0)), float(row.get("mixture_ci_low", -1.0))), default=None)
    best_holdout = max(holdouts, key=lambda row: (float(row.get("mixture_mean_score", -1.0)), float(row.get("mixture_ci_low", -1.0))), default=None)
    best_pair = max(pairs, key=lambda row: row.mean_optimism, default=None)
    mean_optimism = float(sum(row.mean_optimism for row in pairs) / len(pairs)) if pairs else 0.0
    threshold = _threshold_from_rows(rows)
    best_screen_to_best_holdout_gap = (
        None
        if best_screen is None or best_holdout is None
        else float(best_screen.get("mixture_mean_score", 0.0)) - float(best_holdout.get("mixture_mean_score", 0.0))
    )
    summary = {
        "branch_id": spec.branch_id,
        "revision": spec.revision,
        "family": spec.family,
        "score_rows": len(rows),
        "screen_rows": len(screens),
        "holdout_rows": len(holdouts),
        "heldout_with_screen_rows": len(pairs),
        "screen_stages": list(spec.screen_stages),
        "holdout_stage": spec.holdout_stage,
        "challenge_threshold": threshold,
        "best_screen_candidate": None if best_screen is None else str(best_screen.get("candidate_strategy")),
        "best_screen_stage": None if best_screen is None else str(best_screen.get("stage")),
        "best_screen_mean": None if best_screen is None else float(best_screen.get("mixture_mean_score", 0.0)),
        "best_screen_ci_low": None if best_screen is None else float(best_screen.get("mixture_ci_low", 0.0)),
        "best_screen_was_heldout": False if best_screen is None else str(best_screen.get("candidate_strategy")) in by_candidate_holdout,
        "best_screen_to_best_holdout_mean_gap": best_screen_to_best_holdout_gap,
        "best_holdout_candidate": None if best_holdout is None else str(best_holdout.get("candidate_strategy")),
        "best_holdout_mean": None if best_holdout is None else float(best_holdout.get("mixture_mean_score", 0.0)),
        "best_holdout_ci_low": None if best_holdout is None else float(best_holdout.get("mixture_ci_low", 0.0)),
        "best_holdout_clears_challenge_threshold": False
        if best_holdout is None or threshold is None
        else float(best_holdout.get("mixture_ci_low", 0.0)) > float(threshold),
        "max_mean_optimism": None if best_pair is None else best_pair.mean_optimism,
        "mean_optimism_among_heldout": mean_optimism,
        "worst_optimism_candidate": None if best_pair is None else best_pair.candidate_strategy,
        "confirmed_response_found": _has_confirmed_response(rows),
    }
    return summary, pairs


def top_holdout_strategy_rows(root: str | Path, specs: Sequence[OracleBranchSpec] | None = None) -> list[dict[str, object]]:
    """Return the best holdout row per branch, suitable for frontier retest."""

    out: list[dict[str, object]] = []
    for spec in tuple(default_branch_specs() if specs is None else specs):
        rows = read_score_rows(root, spec)
        holdouts = [row for row in rows if str(row.get("stage")) == spec.holdout_stage]
        if not holdouts:
            continue
        best = max(holdouts, key=lambda row: (float(row.get("mixture_mean_score", -1.0)), float(row.get("mixture_ci_low", -1.0))))
        payload = dict(best)
        payload["branch_id"] = spec.branch_id
        payload["branch_family"] = spec.family
        out.append(payload)
    return out


def strategy_bundle_from_score_row(row: Mapping[str, object], *, strategy_id_prefix: str = "") -> StrategyBundle:
    deck_obj = row.get("deck")
    if isinstance(deck_obj, Mapping):
        counts = deck_obj
    else:
        counts = _json_object(row.get("deck_json"))
    deck = DeckVector(
        int(sum(int(counts.get(card, 0)) for card in CARD_ORDER)),
        int(counts.get("Island", 0)),
        int(counts.get("Counterspell", 0)),
        int(counts.get("ForceOfWill", 0)),
        int(counts.get("JaceTheMindSculptor", 0)),
        int(counts.get("OverlordOfTheFloodpits", 0)),
    )
    deck.validate()
    cid = f"{strategy_id_prefix}{row.get('candidate_strategy')}" if strategy_id_prefix else str(row.get("candidate_strategy"))
    return StrategyBundle(
        strategy_id=cid,
        deck_name=f"rev0098_retest_{row.get('branch_id', 'unknown')}_{row.get('candidate_strategy')}",
        deck=deck,
        agent_name=str(row.get("agent_name")),
        mulligan_policy=str(row.get("mulligan_policy")),
    )


def _candidate_optimism(branch_id: str, screen: Mapping[str, object], holdout: Mapping[str, object]) -> CandidateOptimism:
    return CandidateOptimism(
        branch_id=branch_id,
        candidate_strategy=str(holdout.get("candidate_strategy")),
        screen_stage=str(screen.get("stage")),
        screen_mean=float(screen.get("mixture_mean_score", 0.0)),
        screen_ci_low=float(screen.get("mixture_ci_low", 0.0)),
        holdout_mean=float(holdout.get("mixture_mean_score", 0.0)),
        holdout_ci_low=float(holdout.get("mixture_ci_low", 0.0)),
        mean_optimism=float(screen.get("mixture_mean_score", 0.0)) - float(holdout.get("mixture_mean_score", 0.0)),
        ci_low_optimism=float(screen.get("mixture_ci_low", 0.0)) - float(holdout.get("mixture_ci_low", 0.0)),
        screen_games=int(screen.get("games", 0)),
        holdout_games=int(holdout.get("games", 0)),
        agent_name=str(holdout.get("agent_name", "")),
        mulligan_policy=str(holdout.get("mulligan_policy", "")),
        deck_size=int(holdout.get("deck_size", 0)),
        oracle_family=str(holdout.get("oracle_family", "")),
    )


def _threshold_from_rows(rows: Sequence[Mapping[str, object]]) -> float | None:
    for row in rows:
        for key in ("challenge_threshold_with_pruning_bound", "screen_threshold", "confirmation_threshold"):
            value = row.get(key)
            if value not in (None, ""):
                parsed = _float(value)
                if math.isfinite(parsed):
                    return parsed
    return None


def _has_confirmed_response(rows: Sequence[Mapping[str, object]]) -> bool:
    for row in rows:
        for key, value in row.items():
            if "confirmation" in str(key).lower() and _bool(value):
                return True
    return False


def _float(value: object, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _int(value: object, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _json_object(value: object) -> dict[str, object]:
    if isinstance(value, Mapping):
        return dict(value)
    if value in (None, ""):
        return {}
    try:
        payload = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


__all__ = [
    "CandidateOptimism",
    "OracleBranchSpec",
    "audit_oracle_selection_bias",
    "default_branch_specs",
    "read_score_rows",
    "strategy_bundle_from_score_row",
    "summarize_branch",
    "top_holdout_strategy_rows",
]
