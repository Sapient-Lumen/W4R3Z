from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .population_frontier import aggregate_population_summary_rows, population_familywise_gate_rows
from .terminal_mechanisms import to_float, to_int


@dataclass(frozen=True)
class HoeffdingWidthTarget:
    alpha: float
    max_width: float
    required_games: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def hoeffding_full_width(n: int, *, alpha: float = 0.05) -> float:
    """Return the full two-sided Hoeffding interval width for bounded [0, 1] rewards."""

    if n <= 0:
        return 1.0
    if alpha <= 0.0 or alpha >= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    return 2.0 * math.sqrt(math.log(2.0 / float(alpha)) / (2.0 * int(n)))


def required_games_for_hoeffding_width(max_width: float, *, alpha: float = 0.05) -> int:
    """Smallest n whose Hoeffding full width is no larger than ``max_width``."""

    width = float(max_width)
    if width <= 0.0:
        raise ValueError("max_width must be positive")
    if alpha <= 0.0 or alpha >= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    return int(math.ceil((2.0 * math.log(2.0 / float(alpha))) / (width * width)))


def complete_panel_games_per_cell_for_axes(context_axes: Sequence[str]) -> int:
    """Games added to each row-policy × column-policy cell by one complete population rep.

    ``threat_response_specs`` adds one game for each target seat and starting
    player.  Thus one rep contributes four games to a fine size/life cell.  When
    a layer pools over life or size, the contribution multiplies by the number of
    hidden population axes that were pooled.
    """

    axes = set(str(axis) for axis in context_axes)
    per_rep = 4
    if "starting_life" not in axes:
        per_rep *= 2
    if "size_axis" not in axes:
        per_rep *= 3
    return per_rep


def _context_key(row: Mapping[str, object], axes: Sequence[str]) -> tuple[object, ...]:
    return tuple(row.get(axis, "") for axis in axes)


def population_precision_power_ladder_rows(
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
    min_games_per_cell: int = 24,
    max_ci_width: float = 0.60,
    conservative_floor_threshold: float = 0.50,
    alpha: float = 0.05,
    iterations: int = 20000,
) -> list[dict[str, object]]:
    """Quantify how far each hierarchy layer is from the precision target.

    This is a power/allocation audit, not a promotion gate.  It uses the same
    aggregation and gate functions as promotion, then adds a closed-form
    Hoeffding game-count target and the equivalent number of future complete
    panel reps.  The result turns vague labels like ``precision_target_not_met``
    or ``underpowered_min_games`` into a concrete executable ladder.
    """

    material = [dict(row) for row in rows]
    if alpha <= 0.0 or alpha >= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    family_cell_count = max(1, len(tuple(row_policies)) * len(tuple(column_policies)))
    per_cell_alpha = float(alpha) / float(family_cell_count)
    required_for_width = required_games_for_hoeffding_width(max_ci_width, alpha=per_cell_alpha)
    required_games = max(int(min_games_per_cell), int(required_for_width))

    out: list[dict[str, object]] = []
    for layer_name, axes_raw, mandatory in layers:
        axes = tuple(str(axis) for axis in axes_raw)
        pooled = aggregate_population_summary_rows(material, context_axes=axes)
        gate_rows = population_familywise_gate_rows(
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
        pooled_by_context = {}
        for row in pooled:
            pooled_by_context.setdefault(_context_key(row, axes), []).append(row)
        gate_by_context = {_context_key(row, axes): row for row in gate_rows}
        games_per_rep = complete_panel_games_per_cell_for_axes(axes)
        contexts = sorted(set(pooled_by_context) | set(gate_by_context), key=lambda key: tuple(str(x) for x in key))
        for context in contexts:
            cell_rows = pooled_by_context.get(context, [])
            games_values = [to_int(row.get("games"), 0) for row in cell_rows if to_int(row.get("games"), 0) > 0]
            min_games = min(games_values) if games_values else 0
            additional = max(0, required_games - int(min_games))
            reps_needed = int(math.ceil(additional / float(games_per_rep))) if additional else 0
            projected_min = int(min_games) + int(reps_needed) * int(games_per_rep)
            gate = gate_by_context.get(context, {})
            item = {
                "hierarchy_layer": layer_name,
                "hierarchy_context_axes": ";".join(axes) if axes else "<global>",
                "hierarchy_layer_mandatory": bool(mandatory),
                "context_key": "|".join(str(x) for x in context) if context else "<global>",
                "current_status": gate.get("status", "missing_gate_context"),
                "current_blocking_reason": gate.get("blocking_reason", ""),
                "current_min_games_per_cell": int(min_games),
                "required_min_games_per_cell": int(min_games_per_cell),
                "required_games_for_width": int(required_for_width),
                "effective_required_games_per_cell": int(required_games),
                "additional_games_per_cell_needed": int(additional),
                "complete_panel_games_per_rep_per_cell": int(games_per_rep),
                "complete_panel_reps_needed": int(reps_needed),
                "projected_min_games_after_reps": int(projected_min),
                "current_hoeffding_width_at_min_games": hoeffding_full_width(int(min_games), alpha=per_cell_alpha) if min_games else 1.0,
                "projected_hoeffding_width_after_reps": hoeffding_full_width(int(projected_min), alpha=per_cell_alpha) if projected_min else 1.0,
                "interval_family_alpha": float(alpha),
                "interval_per_cell_alpha": float(per_cell_alpha),
                "interval_family_cell_count": int(family_cell_count),
            }
            for axis, value in zip(axes, context):
                item[axis] = value
            for field in (
                "conservative_pure_security_lcb",
                "mean_pure_security_value",
                "max_ci_width_observed",
                "gate_passed",
            ):
                if field in gate:
                    value = gate.get(field)
                    item[f"current_{field}"] = value
            out.append(item)
    return out


def summarize_power_ladder_rows(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    layer_counts: dict[str, int] = {}
    max_reps = 0
    mandatory_max = 0
    precision_blocked = 0
    underpowered = 0
    for row in rows:
        layer = str(row.get("hierarchy_layer", ""))
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        reps = to_int(row.get("complete_panel_reps_needed"), 0)
        max_reps = max(max_reps, reps)
        if str(row.get("hierarchy_layer_mandatory", "")).lower() == "true" or row.get("hierarchy_layer_mandatory") is True:
            mandatory_max = max(mandatory_max, reps)
        status = str(row.get("current_status", ""))
        if status == "precision_target_not_met":
            precision_blocked += 1
        if status == "underpowered_min_games":
            underpowered += 1
    finite_widths = [to_float(row.get("current_max_ci_width_observed"), float("nan")) for row in rows]
    finite_widths = [value for value in finite_widths if np.isfinite(value)]
    return {
        "rows": len(rows),
        "layer_counts": dict(sorted(layer_counts.items())),
        "max_complete_panel_reps_needed": int(max_reps),
        "mandatory_max_complete_panel_reps_needed": int(mandatory_max),
        "precision_blocked_rows": int(precision_blocked),
        "underpowered_rows": int(underpowered),
        "max_current_ci_width_observed": max(finite_widths) if finite_widths else None,
    }


__all__ = [
    "HoeffdingWidthTarget",
    "complete_panel_games_per_cell_for_axes",
    "hoeffding_full_width",
    "population_precision_power_ladder_rows",
    "required_games_for_hoeffding_width",
    "summarize_power_ladder_rows",
]
