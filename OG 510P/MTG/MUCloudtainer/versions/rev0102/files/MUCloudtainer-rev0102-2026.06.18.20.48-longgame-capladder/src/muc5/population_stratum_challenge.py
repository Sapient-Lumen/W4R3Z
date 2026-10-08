from __future__ import annotations

from typing import Mapping, Sequence

from .terminal_mechanisms import to_float, to_int


def select_underpowered_candidate_cells(
    gate_rows: Sequence[Mapping[str, object]],
    *,
    min_mean_floor: float = 0.50,
    required_best_policy: str | None = None,
) -> tuple[tuple[str, int], ...]:
    """Select unique size/life strata that look promising but are underpowered.

    This intentionally consumes gate rows, not prose notes.  It lets the next
    run spend fresh games where the previous fine-stratum guard saw a high point
    floor but refused promotion because evidence was too thin.
    """

    selected: set[tuple[str, int]] = set()
    for row in gate_rows:
        if str(row.get("status", "")) != "underpowered_min_games":
            continue
        size_axis = str(row.get("size_axis", ""))
        life = to_int(row.get("starting_life"), 0)
        if not size_axis or life <= 0:
            continue
        if required_best_policy is not None and str(row.get("mean_best_pure_row_policy", "")) != required_best_policy:
            continue
        mean_floor = to_float(row.get("mean_pure_security_value"), float("nan"))
        if mean_floor >= float(min_mean_floor):
            selected.add((size_axis, life))
    return tuple(sorted(selected, key=lambda item: (item[0], item[1])))


def summarize_challenge_gate(gate_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Summarize a targeted stratum challenge in promotion-safe terms."""

    rows = [dict(row) for row in gate_rows]
    statuses: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", ""))
        statuses[status] = statuses.get(status, 0) + 1
    finite_mean_floors = [
        to_float(row.get("mean_pure_security_value"), float("nan"))
        for row in rows
        if row.get("mean_pure_security_value") not in {None, ""}
    ]
    finite_lcbs = [
        to_float(row.get("conservative_pure_security_lcb"), float("nan"))
        for row in rows
        if row.get("conservative_pure_security_lcb") not in {None, ""}
    ]
    finite_widths = [
        to_float(row.get("max_ci_width_observed"), float("nan"))
        for row in rows
        if row.get("max_ci_width_observed") not in {None, ""}
    ]
    finite_mean_floors = [x for x in finite_mean_floors if x == x]
    finite_lcbs = [x for x in finite_lcbs if x == x]
    finite_widths = [x for x in finite_widths if x == x]
    return {
        "rows": len(rows),
        "status_counts": statuses,
        "gate_passed_cells": sum(1 for row in rows if str(row.get("status", "")) == "candidate_promotable"),
        "worst_mean_pure_security_value": min(finite_mean_floors) if finite_mean_floors else None,
        "best_mean_pure_security_value": max(finite_mean_floors) if finite_mean_floors else None,
        "worst_conservative_pure_security_lcb": min(finite_lcbs) if finite_lcbs else None,
        "best_conservative_pure_security_lcb": max(finite_lcbs) if finite_lcbs else None,
        "max_ci_width_observed": max(finite_widths) if finite_widths else None,
    }


__all__ = ["select_underpowered_candidate_cells", "summarize_challenge_gate"]
