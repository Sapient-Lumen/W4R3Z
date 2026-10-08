from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .counter_response import COUNTER_GUARD_AGENT, GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from .deckspace import DeckVector
from .library_buffer_sweep import scale_deck_to_legal_size
from .payoff import StrategyBundle, load_seed_decks
from .response_matrix import SURGE_THREAT_AXIS, THREAT_SURGE_AGENT
from .statgate import hoeffding_interval
from .terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_MULLIGAN
from .terminal_mechanisms import to_float, to_int
from .threat_closure import THREAT_CLOSURE_AGENT
from .threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS, THREAT_PRESSURE_AGENT, ThreatResponseArm

COUNTER_POPULATION: tuple[tuple[str, str, str], ...] = (
    (
        LEGACY_COUNTER_AXIS,
        CF34_AGENT,
        "Historical CF34 counter ranker that was demoted after closure repair.",
    ),
    (
        GUARDED_COUNTER_AXIS,
        COUNTER_GUARD_AGENT,
        "Public counter_guard policy with ownership, Jace, Force, and library guards.",
    ),
)

THREAT_POPULATION: tuple[tuple[str, str, str], ...] = (
    (
        CLOSURE_THREAT_AXIS,
        THREAT_CLOSURE_AGENT,
        "Library-aware closure baseline, normalized to the target-guarded response-matrix axis.",
    ),
    (
        PRESSURE_THREAT_AXIS,
        THREAT_PRESSURE_AGENT,
        "Jace-pressure threat response from rev0066.",
    ),
    (
        SURGE_THREAT_AXIS,
        THREAT_SURGE_AGENT,
        "Face/protection surge threat response from rev0067.",
    ),
)


@dataclass(frozen=True)
class FictitiousPlayResult:
    row_strategy: tuple[float, ...]
    column_strategy: tuple[float, ...]
    guaranteed_value: float
    exploitability_upper_value: float
    midpoint_value: float
    iterations: int
    solution_method: str = "fictitious_play"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PopulationCell:
    context: tuple[tuple[str, object], ...]
    row_policies: tuple[str, ...]
    column_policies: tuple[str, ...]
    matrix: tuple[tuple[float | None, ...], ...]
    games: tuple[tuple[int, ...], ...]
    complete: bool
    missing_cells: tuple[tuple[str, str], ...]
    min_games: int

    def as_dict(self) -> dict[str, object]:
        return {
            "context": dict(self.context),
            "row_policies": list(self.row_policies),
            "column_policies": list(self.column_policies),
            "matrix": [list(row) for row in self.matrix],
            "games": [list(row) for row in self.games],
            "complete": self.complete,
            "missing_cells": [{"row_policy": r, "column_policy": c} for r, c in self.missing_cells],
            "min_games": self.min_games,
        }


def _bundle(strategy_id: str, deck_name: str, deck: DeckVector, agent: str, mulligan: str) -> StrategyBundle:
    return StrategyBundle(strategy_id, deck_name, deck, agent, mulligan)


def counter_threat_population_arms(seed_decks_path) -> list[ThreatResponseArm]:
    """Build a rectangular counter-policy × threat-policy population panel.

    The rev0065-0067 sequence answered a chain of pairwise questions.  This arm
    generator freezes the named policies into one empirical-game surface so a
    future runner can measure policy population floors rather than adding another
    bespoke duel.  It intentionally reuses ``ThreatResponseArm`` to preserve the
    existing rollout and annotation path.
    """

    decks = load_seed_decks(seed_decks_path)
    counter60 = decks["sixty_counterwall_jace"]
    threat40 = decks["forty_overlord_impending"]
    counter40 = scale_deck_to_legal_size(counter60, 40)
    threat60 = scale_deck_to_legal_size(threat40, 60)

    def counter(size: int, counter_axis: str, agent: str) -> StrategyBundle:
        deck = counter60 if size == 60 else counter40
        deck_name = "sixty_counterwall_jace" if size == 60 else "forty_counterwall_scaled_from60"
        label = "legacy" if counter_axis == LEGACY_COUNTER_AXIS else "guard"
        return _bundle(f"{label}_counter_wall{size}", deck_name, deck, agent, CF34_MULLIGAN)

    def threat(size: int, threat_axis: str, agent: str) -> StrategyBundle:
        deck = threat40 if size == 40 else threat60
        deck_name = "forty_overlord_impending" if size == 40 else "sixty_overlord_scaled_from40"
        label = {
            CLOSURE_THREAT_AXIS: "closure",
            PRESSURE_THREAT_AXIS: "pressure",
            SURGE_THREAT_AXIS: "surge",
        }[threat_axis]
        return _bundle(f"pub_threat{size}_{label}", deck_name, deck, agent, THREAT_MULLIGAN)

    plan = (
        ("A", 40, 40, "40-vs-40 normalized policy-population cell."),
        ("B", 60, 40, "60-vs-40 size-skew policy-population cell."),
        ("C", 60, 60, "60-vs-60 normalized policy-population cell."),
    )
    arms: list[ThreatResponseArm] = []
    for prefix, counter_size, threat_size, question in plan:
        for counter_axis, counter_agent, counter_note in COUNTER_POPULATION:
            counter_label = "legacy" if counter_axis == LEGACY_COUNTER_AXIS else "guard"
            for threat_axis, threat_agent, threat_note in THREAT_POPULATION:
                threat_label = {
                    CLOSURE_THREAT_AXIS: "closure",
                    PRESSURE_THREAT_AXIS: "pressure",
                    SURGE_THREAT_AXIS: "surge",
                }[threat_axis]
                arms.append(
                    ThreatResponseArm(
                        arm_id=f"{prefix}_{counter_label}_vs_{threat_label}_counter{counter_size}_vs_threat{threat_size}",
                        question=question,
                        target=counter(counter_size, counter_axis, counter_agent),
                        opponent=threat(threat_size, threat_axis, threat_agent),
                        counter_policy_axis=counter_axis,
                        threat_policy_axis=threat_axis,
                        size_axis=f"counter{counter_size}_vs_threat{threat_size}",
                        interpretation=f"{counter_note} Opponent axis: {threat_note}",
                    )
                )
    return arms


def zero_sum_fictitious_play(
    payoff_matrix: Sequence[Sequence[float]],
    *,
    iterations: int = 20000,
) -> FictitiousPlayResult:
    """Approximate a row-player maximin mixture for a small zero-sum matrix.

    Payoffs are row-player draw-half scores.  The routine is deterministic and
    dependency-light; it is intended as a gateable empirical-game diagnostic, not
    a replacement for a full PSRO/CFR stack.  The returned lower and upper values
    expose residual approximation error instead of hiding it behind one scalar.
    """

    matrix = np.asarray(payoff_matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("payoff_matrix must be non-empty and rectangular")
    if not np.isfinite(matrix).all():
        raise ValueError("payoff_matrix contains missing or non-finite values")
    rows, cols = matrix.shape
    row_counts = np.ones(rows, dtype=np.float64)
    col_counts = np.ones(cols, dtype=np.float64)
    for _ in range(int(iterations)):
        col_dist = col_counts / float(col_counts.sum())
        row_payoffs = matrix @ col_dist
        row_choice = int(np.argmax(row_payoffs))
        row_counts[row_choice] += 1.0

        row_dist = row_counts / float(row_counts.sum())
        col_payoffs = row_dist @ matrix
        col_choice = int(np.argmin(col_payoffs))
        col_counts[col_choice] += 1.0
    row_dist = row_counts / float(row_counts.sum())
    col_dist = col_counts / float(col_counts.sum())
    guaranteed = float(np.min(row_dist @ matrix))
    upper = float(np.max(matrix @ col_dist))
    return FictitiousPlayResult(
        row_strategy=tuple(float(x) for x in row_dist),
        column_strategy=tuple(float(x) for x in col_dist),
        guaranteed_value=guaranteed,
        exploitability_upper_value=upper,
        midpoint_value=(guaranteed + upper) / 2.0,
        iterations=int(iterations),
        solution_method="fictitious_play",
    )


def _normalized_context_value(axis: str, value: object) -> object:
    """Normalize context-axis values before grouping CSV and in-memory rows.

    CSV sources represent numeric context axes as strings while freshly computed
    in-memory summaries may carry integers.  Without this normalization, pooled
    population gates can silently split one scientific cell into two rows such
    as ``starting_life=40`` and ``starting_life="40"``.
    """

    if axis in {"starting_life", "target_deck_size", "opponent_deck_size"}:
        parsed = to_int(value, -1)
        return parsed if parsed >= 0 else value
    if isinstance(value, str):
        return value.strip()
    return value


def _validate_payoff_matrix(payoff_matrix: Sequence[Sequence[float]]) -> np.ndarray:
    matrix = np.asarray(payoff_matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("payoff_matrix must be non-empty and rectangular")
    if not np.isfinite(matrix).all():
        raise ValueError("payoff_matrix contains missing or non-finite values")
    return matrix


def _best_two_row_primal(matrix: np.ndarray) -> tuple[float, float]:
    row0 = matrix[0, :]
    row1 = matrix[1, :]
    slopes = row0 - row1
    candidates: set[float] = {0.0, 1.0}
    for j in range(matrix.shape[1]):
        for k in range(j + 1, matrix.shape[1]):
            denom = float(slopes[j] - slopes[k])
            if abs(denom) <= 1e-15:
                continue
            p = float((row1[k] - row1[j]) / denom)
            if -1e-12 <= p <= 1.0 + 1e-12:
                candidates.add(min(1.0, max(0.0, p)))
    best_p = 0.0
    best_value = -float("inf")
    for p in sorted(candidates):
        value = float(np.min(row1 + p * slopes))
        if value > best_value + 1e-15:
            best_p = p
            best_value = value
    return best_p, best_value


def _best_two_row_dual(matrix: np.ndarray) -> tuple[tuple[float, ...], float]:
    cols = matrix.shape[1]
    candidates: list[tuple[float, tuple[float, ...]]] = []

    def add_candidate(weights: Sequence[float]) -> None:
        q = np.asarray(weights, dtype=np.float64)
        if np.any(q < -1e-12):
            return
        total = float(q.sum())
        if total <= 0:
            return
        q = np.maximum(q / total, 0.0)
        q = q / float(q.sum())
        row_payoffs = matrix @ q
        candidates.append((float(np.max(row_payoffs)), tuple(float(x) for x in q)))

    for j in range(cols):
        weights = [0.0] * cols
        weights[j] = 1.0
        add_candidate(weights)

    diffs = matrix[0, :] - matrix[1, :]
    for j in range(cols):
        for k in range(j + 1, cols):
            denom = float(diffs[j] - diffs[k])
            if abs(denom) <= 1e-15:
                continue
            qj = float(-diffs[k] / denom)
            if -1e-12 <= qj <= 1.0 + 1e-12:
                qj = min(1.0, max(0.0, qj))
                weights = [0.0] * cols
                weights[j] = qj
                weights[k] = 1.0 - qj
                add_candidate(weights)

    if not candidates:  # pragma: no cover - defensive; pure candidates always exist.
        weights = tuple(1.0 / cols for _ in range(cols))
        return weights, float(np.max(matrix @ np.asarray(weights)))
    upper, weights = min(candidates, key=lambda item: (item[0], sum(abs(x) > 1e-12 for x in item[1])))
    return weights, upper


def exact_two_row_maximin(payoff_matrix: Sequence[Sequence[float]]) -> FictitiousPlayResult:
    """Solve a 1- or 2-row empirical zero-sum game exactly.

    The current counter/threat population surface has two row policies and three
    threat columns.  Using fictitious play for a promotion gate is unnecessary
    there: the row maximin is the upper envelope of finitely many line
    intersections.  This solver keeps that risk out of the critical path while
    preserving the same result object as the approximate fallback.
    """

    matrix = _validate_payoff_matrix(payoff_matrix)
    rows, cols = matrix.shape
    if rows == 1:
        j = int(np.argmin(matrix[0, :]))
        q = tuple(1.0 if index == j else 0.0 for index in range(cols))
        value = float(matrix[0, j])
        return FictitiousPlayResult(
            row_strategy=(1.0,),
            column_strategy=q,
            guaranteed_value=value,
            exploitability_upper_value=value,
            midpoint_value=value,
            iterations=0,
            solution_method="exact_two_row",
        )
    if rows != 2:
        raise ValueError("exact_two_row_maximin only supports one or two row policies")

    p, lower = _best_two_row_primal(matrix)
    q, upper = _best_two_row_dual(matrix)
    value = (lower + upper) / 2.0 if abs(lower - upper) <= 1e-9 else lower
    return FictitiousPlayResult(
        row_strategy=(float(p), float(1.0 - p)),
        column_strategy=q,
        guaranteed_value=float(lower),
        exploitability_upper_value=float(upper),
        midpoint_value=float(value),
        iterations=0,
        solution_method="exact_two_row",
    )


def _support_enumeration_primal(matrix: np.ndarray, *, tol: float = 1e-10) -> tuple[tuple[float, ...], float]:
    """Enumerate row-player basic feasible solutions for a small zero-sum game."""

    rows, cols = matrix.shape
    best_value = -float("inf")
    best_strategy: tuple[float, ...] | None = None
    for support_size in range(1, min(rows, cols) + 1):
        for row_support in combinations(range(rows), support_size):
            for active_columns in combinations(range(cols), support_size):
                # Unknowns are p[row_support] and v.  Active columns satisfy
                # A[:, j]^T p == v, plus sum(p) == 1.
                lhs = np.zeros((support_size + 1, support_size + 1), dtype=np.float64)
                rhs = np.zeros(support_size + 1, dtype=np.float64)
                for eq, column in enumerate(active_columns):
                    for local_i, row_i in enumerate(row_support):
                        lhs[eq, local_i] = matrix[row_i, column]
                    lhs[eq, support_size] = -1.0
                lhs[support_size, :support_size] = 1.0
                rhs[support_size] = 1.0
                try:
                    solved = np.linalg.solve(lhs, rhs)
                except np.linalg.LinAlgError:
                    continue
                local_p = solved[:support_size]
                value = float(solved[support_size])
                if not (np.isfinite(local_p).all() and np.isfinite(value)):
                    continue
                if np.any(local_p < -tol) or abs(float(local_p.sum()) - 1.0) > 1e-7:
                    continue
                strategy = np.zeros(rows, dtype=np.float64)
                for local_i, row_i in enumerate(row_support):
                    strategy[row_i] = max(0.0, float(local_p[local_i]))
                total = float(strategy.sum())
                if total <= 0.0:
                    continue
                strategy /= total
                column_payoffs = strategy @ matrix
                guarantee = float(np.min(column_payoffs))
                if guarantee < value - 1e-7:
                    continue
                if guarantee > best_value + 1e-12:
                    best_value = guarantee
                    best_strategy = tuple(float(x) for x in strategy)
    if best_strategy is None:  # pragma: no cover - defensive for singular degeneracy only.
        raise ValueError("support enumeration failed to find a primal maximin candidate")
    return best_strategy, best_value


def _support_enumeration_dual(matrix: np.ndarray, *, tol: float = 1e-10) -> tuple[tuple[float, ...], float]:
    """Enumerate column-player basic feasible solutions for a small zero-sum game."""

    rows, cols = matrix.shape
    best_value = float("inf")
    best_strategy: tuple[float, ...] | None = None
    for support_size in range(1, min(rows, cols) + 1):
        for column_support in combinations(range(cols), support_size):
            for active_rows in combinations(range(rows), support_size):
                # Unknowns are q[column_support] and v.  Active rows satisfy
                # A[i, :] q == v, plus sum(q) == 1.
                lhs = np.zeros((support_size + 1, support_size + 1), dtype=np.float64)
                rhs = np.zeros(support_size + 1, dtype=np.float64)
                for eq, row_i in enumerate(active_rows):
                    for local_j, column_j in enumerate(column_support):
                        lhs[eq, local_j] = matrix[row_i, column_j]
                    lhs[eq, support_size] = -1.0
                lhs[support_size, :support_size] = 1.0
                rhs[support_size] = 1.0
                try:
                    solved = np.linalg.solve(lhs, rhs)
                except np.linalg.LinAlgError:
                    continue
                local_q = solved[:support_size]
                value = float(solved[support_size])
                if not (np.isfinite(local_q).all() and np.isfinite(value)):
                    continue
                if np.any(local_q < -tol) or abs(float(local_q.sum()) - 1.0) > 1e-7:
                    continue
                strategy = np.zeros(cols, dtype=np.float64)
                for local_j, column_j in enumerate(column_support):
                    strategy[column_j] = max(0.0, float(local_q[local_j]))
                total = float(strategy.sum())
                if total <= 0.0:
                    continue
                strategy /= total
                row_payoffs = matrix @ strategy
                upper = float(np.max(row_payoffs))
                if upper > value + 1e-7:
                    continue
                if upper < best_value - 1e-12:
                    best_value = upper
                    best_strategy = tuple(float(x) for x in strategy)
    if best_strategy is None:  # pragma: no cover - defensive for singular degeneracy only.
        raise ValueError("support enumeration failed to find a dual minimax candidate")
    return best_strategy, best_value


def exact_support_enumeration_maximin(payoff_matrix: Sequence[Sequence[float]]) -> FictitiousPlayResult:
    """Solve a small rectangular zero-sum empirical game by support enumeration.

    The population surface is currently two rows, where the specialized solver
    above is simpler and easier to audit.  This general small-game path closes a
    future risk: once a third counter policy is added, promotion code should not
    silently fall back to noisy fictitious play when the matrix is still tiny
    enough to solve exactly with basic feasible support enumeration.
    """

    matrix = _validate_payoff_matrix(payoff_matrix)
    rows, cols = matrix.shape
    if rows <= 2:
        return exact_two_row_maximin(matrix)
    if min(rows, cols) > 8:
        raise ValueError("support enumeration is intended for small empirical games")
    row_strategy, lower = _support_enumeration_primal(matrix)
    column_strategy, upper = _support_enumeration_dual(matrix)
    midpoint = (lower + upper) / 2.0
    return FictitiousPlayResult(
        row_strategy=row_strategy,
        column_strategy=column_strategy,
        guaranteed_value=float(lower),
        exploitability_upper_value=float(upper),
        midpoint_value=float(midpoint),
        iterations=0,
        solution_method="exact_support_enumeration",
    )


def zero_sum_maximin(
    payoff_matrix: Sequence[Sequence[float]],
    *,
    iterations: int = 20000,
    max_exact_cells: int = 64,
) -> FictitiousPlayResult:
    matrix = _validate_payoff_matrix(payoff_matrix)
    if matrix.shape[0] <= 2:
        return exact_two_row_maximin(matrix)
    if matrix.size <= int(max_exact_cells) and min(matrix.shape) <= 8:
        return exact_support_enumeration_maximin(matrix)
    return zero_sum_fictitious_play(matrix, iterations=iterations)


def population_hierarchical_familywise_gate_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_policies: Sequence[str],
    column_policies: Sequence[str],
    layers: Sequence[tuple[str, Sequence[str], bool]] = (
        ("global", (), True),
        ("by_life", ("starting_life",), True),
        ("by_size", ("size_axis",), True),
        ("by_size_life", ("size_axis", "starting_life"), False),
    ),
    min_games_per_cell: int = 16,
    max_ci_width: float = 0.50,
    conservative_floor_threshold: float = 0.50,
    alpha: float = 0.05,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Evaluate promotion over several aggregation layers with fail-closed labels.

    A global pool can hide Simpson-style weakness in size or life strata.  This
    helper keeps the broad-pool decision visible while making layer membership
    explicit, so a caller can require mandatory layers to clear before treating a
    policy as promotable.  Optional diagnostic layers are retained in the output
    but do not have to block a preregistered broad decision by themselves.
    """

    material = [dict(row) for row in rows]
    out: list[dict[str, object]] = []
    for layer_name, context_axes, mandatory in layers:
        axes = tuple(context_axes)
        pooled = aggregate_population_summary_rows(material, context_axes=axes)
        gate = population_familywise_gate_rows(
            pooled,
            row_policies=row_policies,
            column_policies=column_policies,
            context_axes=axes,
            min_games_per_cell=min_games_per_cell,
            max_ci_width=max_ci_width,
            conservative_floor_threshold=conservative_floor_threshold,
            alpha=alpha,
            iterations=iterations,
        )
        for row in gate:
            item = dict(row)
            item["hierarchy_layer"] = layer_name
            item["hierarchy_context_axes"] = ";".join(axes) if axes else "<global>"
            item["hierarchy_layer_mandatory"] = bool(mandatory)
            item["hierarchy_source_summary_rows"] = len(material)
            item["hierarchy_pooled_summary_rows"] = len(pooled)
            out.append(item)
    return out


def summarize_population_hierarchical_gate(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Summarize a multi-layer population gate with mandatory-layer semantics."""

    layer_counts: dict[str, int] = {}
    layer_status_counts: dict[str, dict[str, int]] = {}
    mandatory_rows = 0
    mandatory_passed = 0
    diagnostic_rows = 0
    diagnostic_passed = 0
    for row in rows:
        layer = str(row.get("hierarchy_layer", ""))
        status = str(row.get("status", ""))
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        layer_status_counts.setdefault(layer, {})[status] = layer_status_counts.setdefault(layer, {}).get(status, 0) + 1
        if population_gate_bool(row.get("hierarchy_layer_mandatory")):
            mandatory_rows += 1
            if population_gate_bool(row.get("gate_passed")):
                mandatory_passed += 1
        else:
            diagnostic_rows += 1
            if population_gate_bool(row.get("gate_passed")):
                diagnostic_passed += 1
    base = summarize_population_precision_gate(rows)
    base.update(
        {
            "hierarchy_layers": layer_counts,
            "hierarchy_layer_status_counts": layer_status_counts,
            "mandatory_rows": mandatory_rows,
            "mandatory_gate_passed_rows": mandatory_passed,
            "mandatory_all_passed": mandatory_rows > 0 and mandatory_rows == mandatory_passed,
            "diagnostic_rows": diagnostic_rows,
            "diagnostic_gate_passed_rows": diagnostic_passed,
        }
    )
    return base


def population_cells_from_summary_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_axis: str = "counter_policy_axis",
    column_axis: str = "threat_policy_axis",
    context_axes: Sequence[str] = ("size_axis", "starting_life"),
    score_col: str = "target_mean_score_draw_half",
    games_col: str = "games",
    row_policies: Sequence[str] | None = None,
    column_policies: Sequence[str] | None = None,
) -> list[PopulationCell]:
    material = [dict(row) for row in rows]
    if row_policies is None:
        row_policies = sorted({str(row.get(row_axis, "")) for row in material if str(row.get(row_axis, ""))})
    if column_policies is None:
        column_policies = sorted({str(row.get(column_axis, "")) for row in material if str(row.get(column_axis, ""))})
    row_policies_t = tuple(str(x) for x in row_policies)
    column_policies_t = tuple(str(x) for x in column_policies)
    grouped: dict[tuple[tuple[str, object], ...], dict[tuple[str, str], Mapping[str, Any]]] = {}
    for row in material:
        context = tuple((axis, _normalized_context_value(axis, row.get(axis))) for axis in context_axes)
        grouped.setdefault(context, {})[(str(row.get(row_axis, "")), str(row.get(column_axis, "")))] = row
    cells: list[PopulationCell] = []
    for context, lookup in sorted(grouped.items(), key=lambda item: tuple(str(v) for _, v in item[0])):
        matrix: list[list[float | None]] = []
        games: list[list[int]] = []
        missing: list[tuple[str, str]] = []
        positive_games: list[int] = []
        for row_policy in row_policies_t:
            matrix_row: list[float | None] = []
            games_row: list[int] = []
            for column_policy in column_policies_t:
                source = lookup.get((row_policy, column_policy))
                if source is None:
                    matrix_row.append(None)
                    games_row.append(0)
                    missing.append((row_policy, column_policy))
                    continue
                raw_value = source.get(score_col)
                game_count = to_int(source.get(games_col), 0)
                if raw_value in {None, ""} or game_count <= 0:
                    matrix_row.append(None)
                    games_row.append(max(0, game_count))
                    missing.append((row_policy, column_policy))
                    continue
                value = to_float(raw_value, float("nan"))
                if not np.isfinite(value):
                    matrix_row.append(None)
                    games_row.append(max(0, game_count))
                    missing.append((row_policy, column_policy))
                    continue
                matrix_row.append(value)
                games_row.append(game_count)
                positive_games.append(game_count)
            matrix.append(matrix_row)
            games.append(games_row)
        cells.append(
            PopulationCell(
                context=context,
                row_policies=row_policies_t,
                column_policies=column_policies_t,
                matrix=tuple(tuple(row) for row in matrix),
                games=tuple(tuple(row) for row in games),
                complete=not missing,
                missing_cells=tuple(missing),
                min_games=min(positive_games) if positive_games else 0,
            )
        )
    return cells


def security_rows_from_cells(cells: Sequence[PopulationCell], *, iterations: int = 20000) -> list[dict[str, object]]:
    """Summarize worst-case and mixed-strategy floors for each population cell."""

    out: list[dict[str, object]] = []
    for cell in cells:
        context = dict(cell.context)
        base: dict[str, object] = {
            **context,
            "row_policy_count": len(cell.row_policies),
            "column_policy_count": len(cell.column_policies),
            "complete": cell.complete,
            "min_games_per_observed_cell": cell.min_games,
            "missing_cell_count": len(cell.missing_cells),
            "missing_cells": ";".join(f"{r}|{c}" for r, c in cell.missing_cells),
        }
        if not cell.complete:
            base.update(
                {
                    "status": "incomplete_population_matrix",
                    "best_pure_row_policy": "",
                    "pure_security_value": "",
                    "worst_column_against_best_pure": "",
                    "mixed_guaranteed_value": "",
                    "mixed_upper_value": "",
                    "mixed_midpoint_value": "",
                    "row_mixture": "",
                    "column_mixture": "",
                }
            )
            out.append(base)
            continue
        matrix = np.asarray(cell.matrix, dtype=np.float64)
        row_floors = np.min(matrix, axis=1)
        best_i = int(np.argmax(row_floors))
        worst_j = int(np.argmin(matrix[best_i, :]))
        fp = zero_sum_maximin(matrix, iterations=iterations)
        row_mix = ";".join(f"{name}:{mass:.6f}" for name, mass in zip(cell.row_policies, fp.row_strategy) if mass > 1e-6)
        col_mix = ";".join(f"{name}:{mass:.6f}" for name, mass in zip(cell.column_policies, fp.column_strategy) if mass > 1e-6)
        base.update(
            {
                "status": "complete_population_matrix",
                "best_pure_row_policy": cell.row_policies[best_i],
                "pure_security_value": float(row_floors[best_i]),
                "worst_column_against_best_pure": cell.column_policies[worst_j],
                "mixed_guaranteed_value": fp.guaranteed_value,
                "mixed_upper_value": fp.exploitability_upper_value,
                "mixed_midpoint_value": fp.midpoint_value,
                "mixed_solution_method": fp.solution_method,
                "row_mixture": row_mix,
                "column_mixture": col_mix,
            }
        )
        for i, row_policy in enumerate(cell.row_policies):
            base[f"pure_floor_{row_policy}"] = float(row_floors[i])
        out.append(base)
    return out


def aggregate_population_summary_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_axis: str = "counter_policy_axis",
    column_axis: str = "threat_policy_axis",
    context_axes: Sequence[str] = ("starting_life",),
    score_col: str = "target_mean_score_draw_half",
    games_col: str = "games",
    output_score_prefix: str = "target_score",
) -> list[dict[str, object]]:
    """Pool already-audited population summary rows with weighted means.

    This is for power analysis and conservative broad screening when several
    seed-disjoint complete population panels exist but each fine-grained size
    cell is still underpowered.  The caller chooses the pooled context axes; the
    function then recomputes bounded-reward confidence intervals from total games
    instead of letting duplicate keys overwrite one another.
    """

    buckets: dict[tuple[object, ...], dict[str, object]] = {}
    for source in rows:
        row = dict(source)
        row_policy = str(row.get(row_axis, ""))
        column_policy = str(row.get(column_axis, ""))
        if not row_policy or not column_policy:
            continue
        games = to_int(row.get(games_col), 0)
        score = to_float(row.get(score_col), float("nan"))
        if games <= 0 or not np.isfinite(score):
            continue
        context = tuple(_normalized_context_value(axis, row.get(axis)) for axis in context_axes)
        key = context + (row_policy, column_policy)
        if key not in buckets:
            item: dict[str, object] = {axis: _normalized_context_value(axis, row.get(axis)) for axis in context_axes}
            item[row_axis] = row_policy
            item[column_axis] = column_policy
            item["source_rows"] = 0
            item["source_game_rows"] = 0
            item["score_weighted_sum"] = 0.0
            item["source_size_axes"] = set()
            item["source_revisions"] = set()
            buckets[key] = item
        item = buckets[key]
        item["source_rows"] = int(item.get("source_rows", 0)) + 1
        item["source_game_rows"] = int(item.get("source_game_rows", 0)) + games
        item["score_weighted_sum"] = float(item.get("score_weighted_sum", 0.0)) + score * games
        if row.get("size_axis") not in {None, ""}:
            cast_set = item["source_size_axes"]
            assert isinstance(cast_set, set)
            cast_set.add(str(row.get("size_axis")))
        revision = row.get("simulator_revision") or row.get("revision") or row.get("source_revision")
        if revision not in {None, ""}:
            cast_revs = item["source_revisions"]
            assert isinstance(cast_revs, set)
            cast_revs.add(str(revision))

    out: list[dict[str, object]] = []
    for item in buckets.values():
        games = int(item.pop("source_game_rows"))
        weighted = float(item.pop("score_weighted_sum"))
        mean_score = weighted / games if games else float("nan")
        ci = hoeffding_interval(mean_score, games)
        size_axes = item.pop("source_size_axes")
        revisions = item.pop("source_revisions")
        assert isinstance(size_axes, set)
        assert isinstance(revisions, set)
        item["games"] = games
        item[f"{output_score_prefix}_mean_draw_half"] = mean_score
        # Keep the historical column names expected by population_precision_gate_rows.
        item[score_col] = mean_score
        item[f"{output_score_prefix}_lcb_95"] = ci.low
        item[f"{output_score_prefix}_ucb_95"] = ci.high
        item["target_score_lcb_95"] = ci.low
        item["target_score_ucb_95"] = ci.high
        item["pooled_size_axes"] = ";".join(sorted(size_axes))
        item["pooled_source_revisions"] = ";".join(sorted(revisions))
        item["pooling_note"] = "weighted pooled summary row; confidence interval recomputed from total bounded draw-half games"
        out.append(item)
    return sorted(out, key=lambda r: tuple(str(r.get(k, "")) for k in (*context_axes, row_axis, column_axis)))



def population_familywise_interval_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_axis: str = "counter_policy_axis",
    column_axis: str = "threat_policy_axis",
    context_axes: Sequence[str] = ("size_axis", "starting_life"),
    mean_col: str = "target_mean_score_draw_half",
    games_col: str = "games",
    row_policies: Sequence[str] | None = None,
    column_policies: Sequence[str] | None = None,
    alpha: float = 0.05,
    lcb_col: str = "target_score_lcb_familywise",
    ucb_col: str = "target_score_ucb_familywise",
) -> list[dict[str, object]]:
    """Recompute simultaneous matrix-cell intervals with a Bonferroni alpha split.

    Earlier population summaries store ordinary per-cell 95% Hoeffding bounds.
    A promotion gate, however, asks a matrix-level question: every row-policy ×
    column-policy estimate in the same context has to be reliable at once.  This
    helper leaves the source rows intact but adds familywise lower/upper columns
    using ``alpha / (row_count * column_count)`` within each context matrix.  It
    therefore prevents future near-threshold candidates from benefiting from an
    unadjusted per-cell interval when several cells were inspected together.
    """

    material = [dict(row) for row in rows]
    if alpha <= 0.0 or alpha >= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    if row_policies is None:
        row_values = {str(row.get(row_axis, "")) for row in material if str(row.get(row_axis, ""))}
        row_policies = tuple(sorted(row_values))
    if column_policies is None:
        col_values = {str(row.get(column_axis, "")) for row in material if str(row.get(column_axis, ""))}
        column_policies = tuple(sorted(col_values))
    family_cell_count = max(1, len(tuple(row_policies)) * len(tuple(column_policies)))
    per_cell_alpha = float(alpha) / float(family_cell_count)

    out: list[dict[str, object]] = []
    for source in material:
        row = dict(source)
        games = to_int(row.get(games_col), 0)
        mean_score = to_float(row.get(mean_col), float("nan"))
        if games > 0 and np.isfinite(mean_score):
            ci = hoeffding_interval(mean_score, games, alpha=per_cell_alpha)
            row[lcb_col] = ci.low
            row[ucb_col] = ci.high
        else:
            row[lcb_col] = ""
            row[ucb_col] = ""
        row["interval_adjustment"] = "bonferroni_matrix_familywise"
        row["interval_family_alpha"] = float(alpha)
        row["interval_per_cell_alpha"] = per_cell_alpha
        row["interval_family_cell_count"] = family_cell_count
        row["interval_family_context_axes"] = ";".join(context_axes) if context_axes else "<global>"
        out.append(row)
    return out


def population_familywise_gate_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_policies: Sequence[str],
    column_policies: Sequence[str],
    context_axes: Sequence[str] = ("size_axis", "starting_life"),
    mean_col: str = "target_mean_score_draw_half",
    games_col: str = "games",
    min_games_per_cell: int = 16,
    max_ci_width: float = 0.50,
    conservative_floor_threshold: float = 0.50,
    alpha: float = 0.05,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Run the population gate with simultaneous matrix-family confidence bounds."""

    annotated = population_familywise_interval_rows(
        rows,
        context_axes=context_axes,
        mean_col=mean_col,
        games_col=games_col,
        row_policies=row_policies,
        column_policies=column_policies,
        alpha=alpha,
    )
    gate_rows = population_precision_gate_rows(
        annotated,
        row_policies=row_policies,
        column_policies=column_policies,
        context_axes=context_axes,
        mean_col=mean_col,
        lcb_col="target_score_lcb_familywise",
        ucb_col="target_score_ucb_familywise",
        games_col=games_col,
        min_games_per_cell=min_games_per_cell,
        max_ci_width=max_ci_width,
        conservative_floor_threshold=conservative_floor_threshold,
        iterations=iterations,
    )
    family_cell_count = max(1, len(tuple(row_policies)) * len(tuple(column_policies)))
    per_cell_alpha = float(alpha) / float(family_cell_count)
    for row in gate_rows:
        row["interval_adjustment"] = "bonferroni_matrix_familywise"
        row["interval_family_alpha"] = float(alpha)
        row["interval_per_cell_alpha"] = per_cell_alpha
        row["interval_family_cell_count"] = family_cell_count
    return gate_rows

def population_precision_gate_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_policies: Sequence[str],
    column_policies: Sequence[str],
    context_axes: Sequence[str] = ("size_axis", "starting_life"),
    mean_col: str = "target_mean_score_draw_half",
    lcb_col: str = "target_score_lcb_95",
    ucb_col: str = "target_score_ucb_95",
    games_col: str = "games",
    min_games_per_cell: int = 16,
    max_ci_width: float = 0.50,
    conservative_floor_threshold: float = 0.50,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Fail-closed promotion gate for a complete empirical-game population.

    The ordinary security rows use point estimates.  This gate builds the same
    rectangular matrix three times: mean, lower confidence bound, and upper
    confidence bound.  It can therefore distinguish a complete but noisy panel
    from a candidate that has enough games and a conservative lower-bound floor.
    """

    material = [dict(row) for row in rows]
    mean_cells = population_cells_from_summary_rows(
        material,
        row_policies=row_policies,
        column_policies=column_policies,
        context_axes=context_axes,
        score_col=mean_col,
        games_col=games_col,
    )
    lcb_by_context = {
        cell.context: cell
        for cell in population_cells_from_summary_rows(
            material,
            row_policies=row_policies,
            column_policies=column_policies,
            context_axes=context_axes,
            score_col=lcb_col,
            games_col=games_col,
        )
    }
    ucb_by_context = {
        cell.context: cell
        for cell in population_cells_from_summary_rows(
            material,
            row_policies=row_policies,
            column_policies=column_policies,
            context_axes=context_axes,
            score_col=ucb_col,
            games_col=games_col,
        )
    }

    out: list[dict[str, object]] = []
    for mean_cell in mean_cells:
        context = dict(mean_cell.context)
        lcb_cell = lcb_by_context.get(mean_cell.context)
        ucb_cell = ucb_by_context.get(mean_cell.context)
        complete = bool(mean_cell.complete and lcb_cell and lcb_cell.complete and ucb_cell and ucb_cell.complete)
        base: dict[str, object] = {
            **context,
            "row_policy_count": len(mean_cell.row_policies),
            "column_policy_count": len(mean_cell.column_policies),
            "complete": complete,
            "min_games_per_observed_cell": mean_cell.min_games,
            "required_min_games_per_cell": int(min_games_per_cell),
            "max_allowed_ci_width": float(max_ci_width),
            "conservative_floor_threshold": float(conservative_floor_threshold),
            "missing_cell_count": len(mean_cell.missing_cells),
            "missing_cells": ";".join(f"{r}|{c}" for r, c in mean_cell.missing_cells),
        }
        if not complete or lcb_cell is None or ucb_cell is None:
            base.update(
                {
                    "status": "incomplete_population_matrix",
                    "gate_passed": False,
                    "mean_pure_security_value": "",
                    "conservative_pure_security_lcb": "",
                    "mixed_mean_guaranteed_value": "",
                    "mixed_lcb_guaranteed_value": "",
                    "max_ci_width_observed": "",
                    "conservative_best_pure_row_policy": "",
                    "mean_best_pure_row_policy": "",
                    "blocking_reason": "missing_or_invalid_population_cell",
                }
            )
            out.append(base)
            continue

        mean_matrix = np.asarray(mean_cell.matrix, dtype=np.float64)
        lcb_matrix = np.asarray(lcb_cell.matrix, dtype=np.float64)
        ucb_matrix = np.asarray(ucb_cell.matrix, dtype=np.float64)
        if not (np.isfinite(mean_matrix).all() and np.isfinite(lcb_matrix).all() and np.isfinite(ucb_matrix).all()):
            base.update(
                {
                    "status": "incomplete_population_matrix",
                    "gate_passed": False,
                    "mean_pure_security_value": "",
                    "conservative_pure_security_lcb": "",
                    "mixed_mean_guaranteed_value": "",
                    "mixed_lcb_guaranteed_value": "",
                    "max_ci_width_observed": "",
                    "conservative_best_pure_row_policy": "",
                    "mean_best_pure_row_policy": "",
                    "blocking_reason": "non_finite_population_matrix",
                }
            )
            out.append(base)
            continue

        mean_row_floors = np.min(mean_matrix, axis=1)
        lcb_row_floors = np.min(lcb_matrix, axis=1)
        best_mean_i = int(np.argmax(mean_row_floors))
        best_lcb_i = int(np.argmax(lcb_row_floors))
        mean_fp = zero_sum_maximin(mean_matrix, iterations=iterations)
        lcb_fp = zero_sum_maximin(lcb_matrix, iterations=iterations)
        ci_widths = ucb_matrix - lcb_matrix
        max_width = float(np.max(ci_widths))
        min_games_ok = int(mean_cell.min_games) >= int(min_games_per_cell)
        precision_ok = max_width <= float(max_ci_width)
        conservative_floor = float(lcb_row_floors[best_lcb_i])
        floor_ok = conservative_floor >= float(conservative_floor_threshold)
        if not min_games_ok:
            status = "underpowered_min_games"
            blocking = "min_games_per_cell_below_preregistered_floor"
        elif not precision_ok:
            status = "precision_target_not_met"
            blocking = "confidence_interval_width_too_wide"
        elif not floor_ok:
            status = "quarantined_low_security_floor"
            blocking = "conservative_floor_below_threshold"
        else:
            status = "candidate_promotable"
            blocking = ""
        base.update(
            {
                "status": status,
                "gate_passed": status == "candidate_promotable",
                "mean_best_pure_row_policy": mean_cell.row_policies[best_mean_i],
                "mean_pure_security_value": float(mean_row_floors[best_mean_i]),
                "conservative_best_pure_row_policy": mean_cell.row_policies[best_lcb_i],
                "conservative_pure_security_lcb": conservative_floor,
                "mixed_mean_guaranteed_value": mean_fp.guaranteed_value,
                "mixed_mean_upper_value": mean_fp.exploitability_upper_value,
                "mixed_lcb_guaranteed_value": lcb_fp.guaranteed_value,
                "mixed_lcb_upper_value": lcb_fp.exploitability_upper_value,
                "mixed_solution_method": lcb_fp.solution_method if lcb_fp.solution_method == mean_fp.solution_method else f"{mean_fp.solution_method};{lcb_fp.solution_method}",
                "max_ci_width_observed": max_width,
                "min_games_ok": min_games_ok,
                "precision_ok": precision_ok,
                "conservative_floor_ok": floor_ok,
                "blocking_reason": blocking,
            }
        )
        for i, row_policy in enumerate(mean_cell.row_policies):
            base[f"mean_floor_{row_policy}"] = float(mean_row_floors[i])
            base[f"lcb_floor_{row_policy}"] = float(lcb_row_floors[i])
        out.append(base)
    return out




def population_column_frontier_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_policies: Sequence[str],
    column_policies: Sequence[str],
    row_axis: str = "counter_policy_axis",
    column_axis: str = "threat_policy_axis",
    context_axes: Sequence[str] = ("size_axis", "starting_life"),
    mean_col: str = "target_mean_score_draw_half",
    games_col: str = "games",
    min_games_per_cell: int = 24,
    max_ci_width: float = 0.60,
    conservative_floor_threshold: float = 0.50,
    alpha: float = 0.05,
) -> list[dict[str, object]]:
    """Resolve each opponent/threat column before collapsing to one floor.

    Population maximin rows are useful but terse: one bad column can be hidden
    behind a single scalar.  This helper keeps the same familywise uncertainty
    contract as the promotion gate, then asks a diagnostic question for every
    opponent column in every context: does the current counter-policy population
    contain *any* credible answer to this threat?  The answer may be different
    for each threat column; the goal is diagnosis and prioritization, not broad
    promotion.
    """

    annotated = population_familywise_interval_rows(
        rows,
        row_axis=row_axis,
        column_axis=column_axis,
        context_axes=context_axes,
        mean_col=mean_col,
        games_col=games_col,
        row_policies=row_policies,
        column_policies=column_policies,
        alpha=alpha,
    )
    by_key: dict[tuple[tuple[tuple[str, object], ...], str], dict[str, Mapping[str, object]]] = {}
    contexts: set[tuple[tuple[str, object], ...]] = set()
    for row in annotated:
        context = tuple((axis, _normalized_context_value(axis, row.get(axis))) for axis in context_axes)
        contexts.add(context)
        column = str(row.get(column_axis, ""))
        row_policy = str(row.get(row_axis, ""))
        if not column or not row_policy:
            continue
        by_key.setdefault((context, column), {})[row_policy] = row

    out: list[dict[str, object]] = []
    row_policy_t = tuple(str(policy) for policy in row_policies)
    column_policy_t = tuple(str(policy) for policy in column_policies)
    ordered_contexts = sorted(contexts, key=lambda context: tuple(str(value) for _axis, value in context))
    for context in ordered_contexts:
        for column in column_policy_t:
            lookup = by_key.get((context, column), {})
            base: dict[str, object] = {
                **dict(context),
                column_axis: column,
                "row_policy_count": len(row_policy_t),
                "column_policy_count": len(column_policy_t),
                "frontier_family_cell_count": max(1, len(row_policy_t) * len(column_policy_t)),
                "frontier_family_alpha": float(alpha),
                "frontier_per_cell_alpha": float(alpha) / float(max(1, len(row_policy_t) * len(column_policy_t))),
                "required_min_games_per_cell": int(min_games_per_cell),
                "max_allowed_ci_width": float(max_ci_width),
                "conservative_floor_threshold": float(conservative_floor_threshold),
            }
            missing = [policy for policy in row_policy_t if policy not in lookup]
            values: list[tuple[str, float, float, float, int, float]] = []
            for policy in row_policy_t:
                row = lookup.get(policy)
                if row is None:
                    continue
                games = to_int(row.get(games_col), 0)
                mean = to_float(row.get(mean_col), float("nan"))
                lcb = to_float(row.get("target_score_lcb_familywise"), float("nan"))
                ucb = to_float(row.get("target_score_ucb_familywise"), float("nan"))
                width = ucb - lcb if np.isfinite(lcb) and np.isfinite(ucb) else float("nan")
                if games <= 0 or not (np.isfinite(mean) and np.isfinite(lcb) and np.isfinite(ucb) and np.isfinite(width)):
                    missing.append(policy)
                    continue
                values.append((policy, mean, lcb, ucb, games, width))

            if missing or len(values) != len(row_policy_t):
                base.update(
                    {
                        "complete": False,
                        "status": "incomplete_opponent_column",
                        "column_answer_passed": False,
                        "blocking_reason": "missing_or_invalid_counter_policy_cell",
                        "missing_row_policies": ";".join(sorted(set(missing))),
                        "min_games_per_observed_cell": min((item[4] for item in values), default=0),
                        "max_ci_width_observed": "",
                        "best_response_row_policy_by_mean": "",
                        "best_response_mean": "",
                        "best_response_row_policy_by_lcb": "",
                        "best_response_lcb": "",
                        "best_response_ucb": "",
                    }
                )
                out.append(base)
                continue

            min_games = min(item[4] for item in values)
            max_width = max(item[5] for item in values)
            best_mean = max(values, key=lambda item: (item[1], item[2], item[0]))
            best_lcb = max(values, key=lambda item: (item[2], item[1], item[0]))
            min_games_ok = min_games >= int(min_games_per_cell)
            precision_ok = max_width <= float(max_ci_width)
            floor_ok = best_lcb[2] >= float(conservative_floor_threshold)
            if not min_games_ok:
                status = "underpowered_min_games"
                blocking = "min_games_per_cell_below_preregistered_floor"
            elif not precision_ok:
                status = "precision_target_not_met"
                blocking = "confidence_interval_width_too_wide"
            elif not floor_ok:
                status = "no_credible_counter_answer_for_threat_column"
                blocking = "best_response_lcb_below_threshold"
            else:
                status = "candidate_counter_answer_for_threat_column"
                blocking = ""
            base.update(
                {
                    "complete": True,
                    "status": status,
                    "column_answer_passed": status == "candidate_counter_answer_for_threat_column",
                    "blocking_reason": blocking,
                    "missing_row_policies": "",
                    "min_games_per_observed_cell": int(min_games),
                    "max_ci_width_observed": float(max_width),
                    "min_games_ok": bool(min_games_ok),
                    "precision_ok": bool(precision_ok),
                    "conservative_floor_ok": bool(floor_ok),
                    "best_response_row_policy_by_mean": best_mean[0],
                    "best_response_mean": float(best_mean[1]),
                    "best_response_row_policy_by_lcb": best_lcb[0],
                    "best_response_lcb": float(best_lcb[2]),
                    "best_response_ucb": float(best_lcb[3]),
                    "mean_minus_lcb_gap": float(best_lcb[1] - best_lcb[2]),
                }
            )
            for policy, mean, lcb, ucb, games, width in values:
                safe = policy.replace("-", "_")
                base[f"mean_{safe}"] = float(mean)
                base[f"lcb_{safe}"] = float(lcb)
                base[f"ucb_{safe}"] = float(ucb)
                base[f"games_{safe}"] = int(games)
                base[f"ci_width_{safe}"] = float(width)
            out.append(base)
    return out

def summarize_population_column_frontier(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Compact status summary for opponent-column frontier audits."""

    status_counts: dict[str, int] = {}
    layer_status_counts: dict[str, dict[str, int]] = {}
    by_threat: dict[str, dict[str, int]] = {}
    lcbs: list[float] = []
    widths: list[float] = []
    for row in rows:
        status = str(row.get("status", ""))
        threat = str(row.get("threat_policy_axis", ""))
        layer = str(row.get("hierarchy_layer", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
        if layer:
            layer_status_counts.setdefault(layer, {})[status] = layer_status_counts.setdefault(layer, {}).get(status, 0) + 1
        if threat:
            by_threat.setdefault(threat, {})[status] = by_threat.setdefault(threat, {}).get(status, 0) + 1
        lcb = to_float(row.get("best_response_lcb"), float("nan"))
        width = to_float(row.get("max_ci_width_observed"), float("nan"))
        if np.isfinite(lcb):
            lcbs.append(lcb)
        if np.isfinite(width):
            widths.append(width)
    passed = sum(1 for row in rows if population_gate_bool(row.get("column_answer_passed")))
    worst_row = None
    finite_rows = [row for row in rows if np.isfinite(to_float(row.get("best_response_lcb"), float("nan")))]
    if finite_rows:
        worst_row = min(finite_rows, key=lambda row: to_float(row.get("best_response_lcb"), float("nan")))
    return {
        "rows": len(rows),
        "column_answer_passed_rows": passed,
        "status_counts": status_counts,
        "hierarchy_layer_status_counts": layer_status_counts,
        "threat_status_counts": by_threat,
        "worst_best_response_lcb": min(lcbs) if lcbs else None,
        "best_best_response_lcb": max(lcbs) if lcbs else None,
        "max_ci_width_observed": max(widths) if widths else None,
        "worst_threat_policy_axis": None if worst_row is None else worst_row.get("threat_policy_axis"),
        "worst_hierarchy_layer": None if worst_row is None else worst_row.get("hierarchy_layer"),
        "worst_size_axis": None if worst_row is None else worst_row.get("size_axis"),
        "worst_starting_life": None if worst_row is None else worst_row.get("starting_life"),
        "worst_best_response_row_policy": None if worst_row is None else worst_row.get("best_response_row_policy_by_lcb"),
    }


def population_column_rescue_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    row_policies: Sequence[str],
    conservative_floor_threshold: float = 0.50,
) -> list[dict[str, object]]:
    """Classify failed opponent-column frontiers by rescue path.

    ``population_column_frontier_rows`` answers whether the current counter
    population contains a familywise-certified answer to each named threat
    column.  For planning, a failed column still needs a sharper interpretation:
    is an existing counter policy already above threshold on its point estimate
    and merely uncertified, or do even optimistic upper bounds fail to reach the
    target?  This helper reuses the per-policy familywise columns emitted by the
    frontier audit and returns fail-closed rescue labels instead of collapsing
    every failure into one generic ``no credible answer`` bucket.
    """

    policy_names = tuple(str(policy) for policy in row_policies)
    out: list[dict[str, object]] = []
    threshold = float(conservative_floor_threshold)
    for source in rows:
        row = dict(source)
        base: dict[str, object] = {
            key: row.get(key, "")
            for key in (
                "hierarchy_layer",
                "hierarchy_context_axes",
                "hierarchy_layer_mandatory",
                "size_axis",
                "starting_life",
                "threat_policy_axis",
                "status",
                "column_answer_passed",
                "blocking_reason",
                "min_games_per_observed_cell",
                "max_ci_width_observed",
            )
            if key in row
        }
        base["conservative_floor_threshold"] = threshold

        values: list[tuple[str, float, float, float, int]] = []
        missing: list[str] = []
        for policy in policy_names:
            safe = policy.replace("-", "_")
            mean = to_float(row.get(f"mean_{safe}"), float("nan"))
            lcb = to_float(row.get(f"lcb_{safe}"), float("nan"))
            ucb = to_float(row.get(f"ucb_{safe}"), float("nan"))
            games = to_int(row.get(f"games_{safe}"), 0)
            if games <= 0 or not (np.isfinite(mean) and np.isfinite(lcb) and np.isfinite(ucb)):
                missing.append(policy)
                continue
            values.append((policy, mean, lcb, ucb, games))

        if missing or len(values) != len(policy_names) or not population_gate_bool(row.get("complete")):
            base.update(
                {
                    "rescue_status": "incomplete_rescue_envelope",
                    "rescue_action": "repair_missing_or_invalid_frontier_cells_before_interpreting_rescue_path",
                    "missing_row_policies": ";".join(sorted(set(missing))),
                    "existing_counter_certified": False,
                    "ucb_rescue_possible": False,
                    "best_lcb_policy": "",
                    "best_mean_policy": "",
                    "best_ucb_policy": "",
                    "best_lcb": "",
                    "best_mean": "",
                    "best_ucb": "",
                    "mean_gap_to_threshold": "",
                    "ucb_gap_to_threshold": "",
                    "best_mean_margin_over_second": "",
                }
            )
            out.append(base)
            continue

        best_lcb = max(values, key=lambda item: (item[2], item[1], item[0]))
        best_mean = max(values, key=lambda item: (item[1], item[2], item[0]))
        best_ucb = max(values, key=lambda item: (item[3], item[1], item[0]))
        sorted_means = sorted(values, key=lambda item: item[1], reverse=True)
        second_mean = sorted_means[1][1] if len(sorted_means) > 1 else float("nan")
        mean_margin = best_mean[1] - second_mean if np.isfinite(second_mean) else float("nan")
        if best_lcb[2] >= threshold:
            rescue_status = "existing_counter_certified"
            rescue_action = "eligible_existing_counter_answer_already_clears_conservative_floor"
        elif best_ucb[3] < threshold:
            rescue_status = "current_counter_set_deficient_even_by_upper_bound"
            rescue_action = "add_or_repair_counter_policy_before_spending_more_sampling_on_this_cell"
        elif best_mean[1] >= threshold:
            rescue_status = "certification_limited_existing_counter_candidate"
            rescue_action = "more_seed_disjoint_complete_panel_sampling_could_certify_existing_counter"
        else:
            rescue_status = "mean_below_threshold_but_upper_bound_allows_rescue"
            rescue_action = "new_counter_policy_likely_higher_priority_than_more_sampling_alone"
        base.update(
            {
                "rescue_status": rescue_status,
                "rescue_action": rescue_action,
                "existing_counter_certified": rescue_status == "existing_counter_certified",
                "ucb_rescue_possible": best_ucb[3] >= threshold,
                "best_lcb_policy": best_lcb[0],
                "best_mean_policy": best_mean[0],
                "best_ucb_policy": best_ucb[0],
                "best_lcb": float(best_lcb[2]),
                "best_mean": float(best_mean[1]),
                "best_ucb": float(best_ucb[3]),
                "mean_gap_to_threshold": float(best_mean[1] - threshold),
                "ucb_gap_to_threshold": float(best_ucb[3] - threshold),
                "best_mean_margin_over_second": float(mean_margin) if np.isfinite(mean_margin) else "",
                "min_games_across_policies": min(item[4] for item in values),
            }
        )
        for policy, mean, lcb, ucb, games in values:
            safe = policy.replace("-", "_")
            base[f"rescue_mean_{safe}"] = float(mean)
            base[f"rescue_lcb_{safe}"] = float(lcb)
            base[f"rescue_ucb_{safe}"] = float(ucb)
            base[f"rescue_games_{safe}"] = int(games)
        out.append(base)
    return out


def summarize_population_column_rescue(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Summarize rescue-envelope labels with mandatory-layer accounting."""

    status_counts: dict[str, int] = {}
    layer_status_counts: dict[str, dict[str, int]] = {}
    threat_status_counts: dict[str, dict[str, int]] = {}
    mandatory_rows = 0
    mandatory_counter_set_deficient = 0
    mandatory_certification_limited = 0
    mandatory_mean_below_rescuable = 0
    ucb_gaps: list[float] = []
    mean_gaps: list[float] = []
    for row in rows:
        status = str(row.get("rescue_status", ""))
        layer = str(row.get("hierarchy_layer", ""))
        threat = str(row.get("threat_policy_axis", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
        if layer:
            layer_status_counts.setdefault(layer, {})[status] = layer_status_counts.setdefault(layer, {}).get(status, 0) + 1
        if threat:
            threat_status_counts.setdefault(threat, {})[status] = threat_status_counts.setdefault(threat, {}).get(status, 0) + 1
        if population_gate_bool(row.get("hierarchy_layer_mandatory")):
            mandatory_rows += 1
            if status == "current_counter_set_deficient_even_by_upper_bound":
                mandatory_counter_set_deficient += 1
            elif status == "certification_limited_existing_counter_candidate":
                mandatory_certification_limited += 1
            elif status == "mean_below_threshold_but_upper_bound_allows_rescue":
                mandatory_mean_below_rescuable += 1
        ucb_gap = to_float(row.get("ucb_gap_to_threshold"), float("nan"))
        mean_gap = to_float(row.get("mean_gap_to_threshold"), float("nan"))
        if np.isfinite(ucb_gap):
            ucb_gaps.append(ucb_gap)
        if np.isfinite(mean_gap):
            mean_gaps.append(mean_gap)
    weakest_row = None
    finite_rows = [row for row in rows if np.isfinite(to_float(row.get("ucb_gap_to_threshold"), float("nan")))]
    if finite_rows:
        weakest_row = min(finite_rows, key=lambda row: to_float(row.get("ucb_gap_to_threshold"), float("nan")))
    return {
        "rows": len(rows),
        "rescue_status_counts": status_counts,
        "hierarchy_layer_rescue_status_counts": layer_status_counts,
        "threat_rescue_status_counts": threat_status_counts,
        "mandatory_rows": mandatory_rows,
        "mandatory_current_counter_set_deficient_rows": mandatory_counter_set_deficient,
        "mandatory_certification_limited_rows": mandatory_certification_limited,
        "mandatory_mean_below_rescuable_rows": mandatory_mean_below_rescuable,
        "existing_counter_certified_rows": sum(1 for row in rows if population_gate_bool(row.get("existing_counter_certified"))),
        "ucb_rescue_possible_rows": sum(1 for row in rows if population_gate_bool(row.get("ucb_rescue_possible"))),
        "min_ucb_gap_to_threshold": min(ucb_gaps) if ucb_gaps else None,
        "max_ucb_gap_to_threshold": max(ucb_gaps) if ucb_gaps else None,
        "min_mean_gap_to_threshold": min(mean_gaps) if mean_gaps else None,
        "max_mean_gap_to_threshold": max(mean_gaps) if mean_gaps else None,
        "weakest_ucb_threat_policy_axis": None if weakest_row is None else weakest_row.get("threat_policy_axis"),
        "weakest_ucb_hierarchy_layer": None if weakest_row is None else weakest_row.get("hierarchy_layer"),
        "weakest_ucb_size_axis": None if weakest_row is None else weakest_row.get("size_axis"),
        "weakest_ucb_starting_life": None if weakest_row is None else weakest_row.get("starting_life"),
        "weakest_ucb_best_policy": None if weakest_row is None else weakest_row.get("best_ucb_policy"),
    }

def population_gate_bool(value: object) -> bool:
    """Parse boolean-like gate fields without treating CSV strings as truthy.

    Gate rows are sometimes summarized immediately as Python dictionaries and
    sometimes after a CSV round trip.  The latter turns ``False`` into the
    non-empty string ``"False"``; using ``bool(value)`` would count that as a
    passed cell.  Promotion accounting must fail closed on unknown text.
    """

    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "passed", "pass"}:
            return True
        if normalized in {"false", "0", "no", "n", "", "failed", "fail"}:
            return False
    return False


def summarize_population_precision_gate(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
    finite_lcbs = [
        float(row["conservative_pure_security_lcb"])
        for row in rows
        if row.get("conservative_pure_security_lcb") not in {"", None}
    ]
    finite_widths = [float(row["max_ci_width_observed"]) for row in rows if row.get("max_ci_width_observed") not in {"", None}]
    return {
        "rows": len(rows),
        "gate_passed_cells": sum(1 for row in rows if population_gate_bool(row.get("gate_passed"))),
        "status_counts": status_counts,
        "worst_conservative_pure_security_lcb": min(finite_lcbs) if finite_lcbs else None,
        "best_conservative_pure_security_lcb": max(finite_lcbs) if finite_lcbs else None,
        "max_ci_width_observed": max(finite_widths) if finite_widths else None,
    }


__all__ = [
    "COUNTER_POPULATION",
    "THREAT_POPULATION",
    "FictitiousPlayResult",
    "PopulationCell",
    "aggregate_population_summary_rows",
    "counter_threat_population_arms",
    "population_cells_from_summary_rows",
    "population_hierarchical_familywise_gate_rows",
    "population_column_frontier_rows",
    "population_column_rescue_rows",
    "population_precision_gate_rows",
    "population_familywise_gate_rows",
    "population_familywise_interval_rows",
    "security_rows_from_cells",
    "summarize_population_hierarchical_gate",
    "summarize_population_column_frontier",
    "summarize_population_column_rescue",
    "summarize_population_precision_gate",
    "population_gate_bool",
    "_normalized_context_value",
    "exact_two_row_maximin",
    "exact_support_enumeration_maximin",
    "zero_sum_fictitious_play",
    "zero_sum_maximin",
]
