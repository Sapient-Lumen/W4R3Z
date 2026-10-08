from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Mapping, Sequence


def _f(row: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = row.get(key, default)
        if value == "" or value is None:
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _i(row: Mapping[str, Any], key: str, default: int = 0) -> int:
    try:
        value = row.get(key, default)
        if value == "" or value is None:
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _claim_bonus(target: str, claim_rows: Sequence[Mapping[str, Any]]) -> float:
    bonus = 0.0
    for row in claim_rows:
        if str(row.get("strategy")) != str(target):
            continue
        label = str(row.get("claim_label") or row.get("deep_claim_label") or "")
        if label in {"robust_candidate", "population_candidate", "deep_robust_signal", "deep_field_signal"}:
            bonus = max(bonus, 0.06)
        elif label in {"life_sensitive_candidate", "deep_life_sensitive_signal"}:
            bonus = max(bonus, 0.04)
        elif label in {"terminal_clean_signal_only"}:
            bonus = max(bonus, 0.02)
        try:
            bonus += min(0.04, max(0.0, float(row.get("meta_rank_mass", 0.0)) * 0.05))
        except Exception:
            pass
    return bonus


def _previous_flip_by_pair(flip_rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], Mapping[str, Any]]:
    return {(str(r.get("target")), str(r.get("opponent"))): r for r in flip_rows}


def _group_cell_rows(cell_rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in cell_rows:
        target = str(row.get("target"))
        opponent = str(row.get("opponent"))
        if not target or not opponent:
            continue
        groups[(target, opponent)].append(row)
    return groups


def cell_confluence_agenda_from_retest(
    cell_rows: Sequence[Mapping[str, Any]],
    flip_rows: Sequence[Mapping[str, Any]] = (),
    claim_rows: Sequence[Mapping[str, Any]] = (),
    *,
    top_n: int = 3,
    life_low: int = 20,
    life_high: int = 40,
) -> list[dict[str, Any]]:
    """Select concrete target/opponent cells for deeper terminal-clean retesting.

    rev0052 showed that dramatic life splits softened.  This helper deliberately
    changes agenda shape: prefer concrete cells that remain good or strategically
    surprising after the retest, not cells that merely had old noisy life splits.
    """

    previous_flip = _previous_flip_by_pair(flip_rows)
    out: list[dict[str, Any]] = []
    for (target, opponent), rows in _group_cell_rows(cell_rows).items():
        by_life = {_i(r, "starting_life"): r for r in rows}
        if int(life_low) not in by_life or int(life_high) not in by_life:
            continue
        lo = by_life[int(life_low)]
        hi = by_life[int(life_high)]
        score_lo = _f(lo, "mean_score_draw_half")
        score_hi = _f(hi, "mean_score_draw_half")
        lcb_lo = _f(lo, "score_lcb_95")
        lcb_hi = _f(hi, "score_lcb_95")
        games_lo = _i(lo, "games")
        games_hi = _i(hi, "games")
        avg_score = (score_lo + score_hi) / 2.0
        min_score = min(score_lo, score_hi)
        max_score = max(score_lo, score_hi)
        life_delta = score_hi - score_lo
        any_favored = str(lo.get("cell_signal")) == "favored" or str(hi.get("cell_signal")) == "favored"
        both_favored = str(lo.get("cell_signal")) == "favored" and str(hi.get("cell_signal")) == "favored"
        prior = previous_flip.get((target, opponent), {})
        old_label = str(prior.get("life_flip_label", ""))
        stability_bonus = 0.05 if abs(life_delta) <= 0.10 else 0.0
        confluence_score = (
            avg_score
            + (0.12 if both_favored else 0.0)
            + (0.07 if any_favored else 0.0)
            + (0.04 if min_score >= 0.55 else 0.0)
            + stability_bonus
            + _claim_bonus(target, claim_rows)
            - min(0.08, abs(life_delta) * 0.10)
        )
        if both_favored:
            reason = "both_lives_favored"
        elif any_favored:
            reason = "one_life_favored"
        elif avg_score >= 0.58:
            reason = "high_average_watch"
        elif abs(life_delta) >= 0.12:
            reason = "remaining_life_split_watch"
        else:
            reason = "control_watch"
        out.append(
            {
                "target": target,
                "opponent": opponent,
                "previous_matchup_index": str(lo.get("matchup_index", "")),
                f"previous_score_life{life_low}": score_lo,
                f"previous_score_life{life_high}": score_hi,
                f"previous_lcb_life{life_low}": lcb_lo,
                f"previous_lcb_life{life_high}": lcb_hi,
                f"previous_games_life{life_low}": games_lo,
                f"previous_games_life{life_high}": games_hi,
                "previous_avg_score": avg_score,
                "previous_min_score": min_score,
                "previous_max_score": max_score,
                "previous_life_delta_high_minus_low": life_delta,
                "previous_abs_life_delta": abs(life_delta),
                "previous_cell_signal_life_low": str(lo.get("cell_signal", "")),
                "previous_cell_signal_life_high": str(hi.get("cell_signal", "")),
                "previous_life_flip_label": old_label,
                "confluence_score": confluence_score,
                "agenda_reason": reason,
                "agenda_source": "rev0052_target_life_cells_plus_claim_context",
            }
        )
    out.sort(key=lambda r: (float(r["confluence_score"]), float(r["previous_avg_score"]), -float(r["previous_abs_life_delta"])), reverse=True)
    for rank, row in enumerate(out, 1):
        row["confluence_rank"] = rank
    return out[: int(top_n)]


def cell_confirmation_rows(
    cell_rows: Sequence[Mapping[str, Any]],
    agenda_rows: Sequence[Mapping[str, Any]],
    *,
    life_low: int = 20,
    life_high: int = 40,
) -> list[dict[str, Any]]:
    """Aggregate deeper target/life cells into a cell-confirmation table."""

    agenda_by_pair = {(str(r.get("target")), str(r.get("opponent"))): r for r in agenda_rows}
    groups = _group_cell_rows(cell_rows)
    out: list[dict[str, Any]] = []
    for (target, opponent), rows in groups.items():
        by_life = {_i(r, "starting_life"): r for r in rows}
        if int(life_low) not in by_life or int(life_high) not in by_life:
            continue
        lo = by_life[int(life_low)]
        hi = by_life[int(life_high)]
        score_lo = _f(lo, "mean_score_draw_half")
        score_hi = _f(hi, "mean_score_draw_half")
        lcb_lo = _f(lo, "score_lcb_95")
        lcb_hi = _f(hi, "score_lcb_95")
        ucb_lo = _f(lo, "score_ucb_95")
        ucb_hi = _f(hi, "score_ucb_95")
        games_lo = _i(lo, "games")
        games_hi = _i(hi, "games")
        avg_score = (score_lo + score_hi) / 2.0
        min_score = min(score_lo, score_hi)
        life_delta = score_hi - score_lo
        both_lcb_over_half = lcb_lo > 0.5 and lcb_hi > 0.5
        any_lcb_over_half = lcb_lo > 0.5 or lcb_hi > 0.5
        both_mean_over_60 = score_lo >= 0.60 and score_hi >= 0.60
        any_mean_over_65 = score_lo >= 0.65 or score_hi >= 0.65
        if both_lcb_over_half and both_mean_over_60:
            label = "confirmed_stable_favored"
        elif any_lcb_over_half and avg_score >= 0.60:
            label = "favored_cell_signal"
        elif ucb_lo < 0.5 and ucb_hi < 0.5:
            label = "confirmed_unfavored"
        elif abs(life_delta) >= 0.20 and avg_score >= 0.55:
            label = "life_sensitive_watch"
        elif avg_score >= 0.55:
            label = "field_watch"
        else:
            label = "uncertain_watch"
        agenda = agenda_by_pair.get((target, opponent), {})
        prev_avg = _f(agenda, "previous_avg_score")
        prev_delta = _f(agenda, "previous_life_delta_high_minus_low")
        out.append(
            {
                "target": target,
                "opponent": opponent,
                "games": games_lo + games_hi,
                f"games_life{life_low}": games_lo,
                f"games_life{life_high}": games_hi,
                f"score_life{life_low}": score_lo,
                f"score_life{life_high}": score_hi,
                f"lcb_life{life_low}": lcb_lo,
                f"lcb_life{life_high}": lcb_hi,
                f"ucb_life{life_low}": ucb_lo,
                f"ucb_life{life_high}": ucb_hi,
                "avg_score": avg_score,
                "min_score": min_score,
                "life_delta_high_minus_low": life_delta,
                "abs_life_delta": abs(life_delta),
                "life_bias": "life40" if life_delta > 1e-12 else ("life20" if life_delta < -1e-12 else "flat"),
                "previous_avg_score": prev_avg if agenda else "",
                "avg_score_shift_vs_previous": "" if not agenda else avg_score - prev_avg,
                "previous_life_delta_high_minus_low": prev_delta if agenda else "",
                "life_delta_shift_vs_previous": "" if not agenda else life_delta - prev_delta,
                "agenda_reason": str(agenda.get("agenda_reason", "")),
                "confluence_rank": agenda.get("confluence_rank", ""),
                "confirmation_label": label,
            }
        )
    out.sort(key=lambda r: (str(r.get("confirmation_label")) not in {"confirmed_stable_favored", "favored_cell_signal"}, -float(r.get("avg_score", 0.0))))
    return out


@dataclass(frozen=True)
class CellConfirmationGate:
    passed: bool
    revision: str
    rows: int
    agenda_cells: int
    confirmation_rows: int
    truncations: int
    cpp_mismatches: int
    cpp_skipped: int
    min_cell_games: int
    favored_or_confirmed_cells: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def cell_confirmation_gate(
    rows: Sequence[Mapping[str, Any]],
    agenda_rows: Sequence[Mapping[str, Any]],
    confirmation_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    cpp_summary: Mapping[str, Any] | None = None,
    min_rows: int = 250,
    min_cell_games: int = 48,
) -> CellConfirmationGate:
    errors: list[str] = []
    warnings: list[str] = []
    if len(rows) < int(min_rows):
        errors.append(f"raw_rows {len(rows)} below min_rows {min_rows}")
    truncations = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if truncations:
        errors.append(f"{truncations} truncation rows in cell-confirmation panel")
    if len(agenda_rows) < 2:
        warnings.append("cell-confirmation agenda has fewer than two cells")
    small = [r for r in confirmation_rows if _i(r, "games_life20") < int(min_cell_games) or _i(r, "games_life40") < int(min_cell_games)]
    if small:
        errors.append(f"{len(small)} confirmation cells below min_cell_games per life {min_cell_games}")
    cpp_mismatches = int((cpp_summary or {}).get("mismatches", 0))
    cpp_skipped = int((cpp_summary or {}).get("skipped_events", 0))
    if cpp_mismatches:
        errors.append(f"C++ shadow mismatches: {cpp_mismatches}")
    if cpp_skipped:
        errors.append(f"C++ skipped events: {cpp_skipped}")
    favored = sum(1 for r in confirmation_rows if str(r.get("confirmation_label")) in {"confirmed_stable_favored", "favored_cell_signal"})
    if favored == 0:
        warnings.append("no favored/confirmed concrete cells in this panel")
    min_games = min((_i(r, "games_life20") for r in confirmation_rows), default=0)
    if confirmation_rows:
        min_games = min(min_games, min((_i(r, "games_life40") for r in confirmation_rows), default=0))
    return CellConfirmationGate(
        passed=not errors,
        revision=str(revision),
        rows=len(rows),
        agenda_cells=len(agenda_rows),
        confirmation_rows=len(confirmation_rows),
        truncations=truncations,
        cpp_mismatches=cpp_mismatches,
        cpp_skipped=cpp_skipped,
        min_cell_games=min_games,
        favored_or_confirmed_cells=favored,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
