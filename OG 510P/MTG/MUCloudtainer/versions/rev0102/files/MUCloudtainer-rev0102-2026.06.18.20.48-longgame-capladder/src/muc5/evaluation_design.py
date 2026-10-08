from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class BalancedPairCell:
    """One cell in the standard MUC-5 focal-pair evaluation design.

    Every empirical focal-vs-opponent estimate used by the PSRO/oracle path
    should cover both physical seats and both play/draw roles.  Keeping the
    design in one helper prevents subtle drift between scripts.
    """

    starting_life: int
    rep: int
    orientation: int
    starting_player: int

    @property
    def focal_player(self) -> int:
        return 0 if int(self.orientation) == 0 else 1

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["focal_player"] = self.focal_player
        return payload


def balanced_pair_cells(life_totals: Sequence[int], reps: int) -> tuple[BalancedPairCell, ...]:
    """Return the canonical balanced design: life × rep × seat × start.

    The returned order is stable because deterministic seeds downstream include
    the same fields.  The function rejects empty/invalid designs rather than
    letting scripts silently emit one-sided evidence.
    """

    if not life_totals:
        raise ValueError("life_totals cannot be empty")
    if int(reps) <= 0:
        raise ValueError("reps must be positive")
    cells: list[BalancedPairCell] = []
    for life in life_totals:
        for rep in range(int(reps)):
            for orientation in (0, 1):
                for starting_player in (0, 1):
                    cells.append(
                        BalancedPairCell(
                            starting_life=int(life),
                            rep=int(rep),
                            orientation=int(orientation),
                            starting_player=int(starting_player),
                        )
                    )
    return tuple(cells)


def expected_games_per_pair(life_totals: Sequence[int], reps: int) -> int:
    return len(balanced_pair_cells(life_totals, reps))


def audit_balanced_focal_rows(
    rows: Iterable[Mapping[str, object]],
    *,
    expected_life_totals: Sequence[int] | None = None,
    expected_reps: int | None = None,
) -> dict[str, object]:
    """Audit whether focal-pair rows obey the standard seat/start design.

    This validates *design integrity*, not strategic truth.  It catches missing
    orientations, missing starting-player rows, malformed focal-player labels,
    duplicate cells, and score values outside [0, 1].  It also reports aggregate
    seat/start gaps so sampling asymmetry is visible before matrix solving.
    """

    material = [dict(row) for row in rows]
    required = {"stage", "focal_strategy", "opponent_strategy", "starting_life", "rep", "orientation", "starting_player", "focal_player", "score"}
    malformed: list[dict[str, object]] = []
    groups: dict[tuple[object, ...], set[tuple[int, int]]] = defaultdict(set)
    duplicates: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    orientation_counts = {"0": 0, "1": 0}
    starting_player_counts = {"0": 0, "1": 0}
    focal_player_counts = {"0": 0, "1": 0}
    scores_by_focal_seat = {0: [], 1: []}  # type: ignore[var-annotated]
    scores_by_focal_start = {"starts": [], "draws": []}  # type: ignore[var-annotated]

    for index, row in enumerate(material):
        missing = sorted(required - set(row.keys()))
        if missing:
            malformed.append({"index": index, "reason": "missing_required_keys", "missing": missing})
            continue
        try:
            orientation = int(row["orientation"])
            starting_player = int(row["starting_player"])
            focal_player = int(row["focal_player"])
            score = float(row["score"])
            starting_life = int(row["starting_life"])
            rep = int(row["rep"])
        except (TypeError, ValueError):
            malformed.append({"index": index, "reason": "unparseable_numeric_fields"})
            continue
        expected_focal_player = 0 if orientation == 0 else 1
        if orientation not in (0, 1) or starting_player not in (0, 1) or focal_player not in (0, 1):
            malformed.append({"index": index, "reason": "nonbinary_orientation_start_or_focal_player"})
            continue
        if focal_player != expected_focal_player:
            malformed.append(
                {
                    "index": index,
                    "reason": "focal_player_does_not_match_orientation",
                    "orientation": orientation,
                    "focal_player": focal_player,
                    "expected_focal_player": expected_focal_player,
                }
            )
            continue
        if score < 0.0 or score > 1.0:
            malformed.append({"index": index, "reason": "score_outside_unit_interval", "score": score})
            continue
        group = (row["stage"], row["focal_strategy"], row["opponent_strategy"], starting_life, rep)
        cell_key = (*group, orientation, starting_player)
        if cell_key in seen:
            duplicates.append({"index": index, "cell_key": [str(part) for part in cell_key]})
        seen.add(cell_key)
        groups[group].add((orientation, starting_player))
        orientation_counts[str(orientation)] += 1
        starting_player_counts[str(starting_player)] += 1
        focal_player_counts[str(focal_player)] += 1
        scores_by_focal_seat[focal_player].append(score)
        if starting_player == focal_player:
            scores_by_focal_start["starts"].append(score)
        else:
            scores_by_focal_start["draws"].append(score)

    expected_cells = {(0, 0), (0, 1), (1, 0), (1, 1)}
    incomplete_groups = [
        {
            "stage": str(group[0]),
            "focal_strategy": str(group[1]),
            "opponent_strategy": str(group[2]),
            "starting_life": group[3],
            "rep": group[4],
            "present": sorted([list(cell) for cell in cells]),
            "missing": sorted([list(cell) for cell in expected_cells - cells]),
        }
        for group, cells in groups.items()
        if cells != expected_cells
    ]

    life_set = sorted({int(row["starting_life"]) for row in material if "starting_life" in row})
    rep_set = sorted({int(row["rep"]) for row in material if "rep" in row}) if material else []
    expected_life_ok = True if expected_life_totals is None else life_set == sorted(int(x) for x in expected_life_totals)
    expected_reps_ok = True if expected_reps is None else rep_set == list(range(int(expected_reps)))

    seat0_mean = _mean(scores_by_focal_seat[0])
    seat1_mean = _mean(scores_by_focal_seat[1])
    start_mean = _mean(scores_by_focal_start["starts"])
    draw_mean = _mean(scores_by_focal_start["draws"])
    passed = (
        len(material) > 0
        and not malformed
        and not duplicates
        and not incomplete_groups
        and orientation_counts["0"] == orientation_counts["1"]
        and starting_player_counts["0"] == starting_player_counts["1"]
        and focal_player_counts["0"] == focal_player_counts["1"]
        and expected_life_ok
        and expected_reps_ok
    )
    return {
        "schema": "muc5.balanced_focal_row_audit.v1",
        "passed": passed,
        "rows": len(material),
        "groups": len(groups),
        "orientation_counts": orientation_counts,
        "starting_player_counts": starting_player_counts,
        "focal_player_counts": focal_player_counts,
        "life_totals": life_set,
        "rep_values": rep_set,
        "expected_life_totals_ok": expected_life_ok,
        "expected_reps_ok": expected_reps_ok,
        "malformed_rows": malformed[:20],
        "malformed_count": len(malformed),
        "duplicate_cells": duplicates[:20],
        "duplicate_count": len(duplicates),
        "incomplete_groups": incomplete_groups[:20],
        "incomplete_group_count": len(incomplete_groups),
        "focal_seat_score_means": {"seat0": seat0_mean, "seat1": seat1_mean, "seat1_minus_seat0": None if seat0_mean is None or seat1_mean is None else seat1_mean - seat0_mean},
        "focal_start_score_means": {"starts": start_mean, "draws": draw_mean, "starts_minus_draws": None if start_mean is None or draw_mean is None else start_mean - draw_mean},
    }


def pair_symmetry_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Summarize seat/start balance per focal-opponent pair."""

    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("stage")), str(row.get("focal_strategy")), str(row.get("opponent_strategy")))].append(dict(row))
    out: list[dict[str, object]] = []
    for (stage, focal, opponent), items in sorted(grouped.items()):
        seat0 = [float(row["score"]) for row in items if int(row.get("focal_player", -1)) == 0]
        seat1 = [float(row["score"]) for row in items if int(row.get("focal_player", -1)) == 1]
        starts = [float(row["score"]) for row in items if int(row.get("focal_player", -1)) == int(row.get("starting_player", -2))]
        draws = [float(row["score"]) for row in items if int(row.get("focal_player", -1)) != int(row.get("starting_player", -2))]
        seat0_mean = _mean(seat0)
        seat1_mean = _mean(seat1)
        start_mean = _mean(starts)
        draw_mean = _mean(draws)
        out.append(
            {
                "stage": stage,
                "focal_strategy": focal,
                "opponent_strategy": opponent,
                "rows": len(items),
                "seat0_rows": len(seat0),
                "seat1_rows": len(seat1),
                "focal_starts_rows": len(starts),
                "focal_draws_rows": len(draws),
                "seat0_mean": seat0_mean,
                "seat1_mean": seat1_mean,
                "seat1_minus_seat0": None if seat0_mean is None or seat1_mean is None else seat1_mean - seat0_mean,
                "focal_starts_mean": start_mean,
                "focal_draws_mean": draw_mean,
                "focal_starts_minus_draws": None if start_mean is None or draw_mean is None else start_mean - draw_mean,
            }
        )
    return out


def _mean(values: Sequence[float]) -> float | None:
    return None if not values else float(sum(values) / len(values))


__all__ = [
    "BalancedPairCell",
    "audit_balanced_focal_rows",
    "balanced_pair_cells",
    "expected_games_per_pair",
    "pair_symmetry_rows",
]
