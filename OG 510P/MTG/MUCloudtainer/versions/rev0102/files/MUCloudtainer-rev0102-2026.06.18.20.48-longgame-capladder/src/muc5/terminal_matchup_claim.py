from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

from .statgate import hoeffding_interval, wilson_interval


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


def concrete_claim_agenda_from_confirmation(
    confirmation_rows: Sequence[Mapping[str, Any]],
    *,
    top_n: int = 1,
    preferred_labels: Sequence[str] = ("favored_cell_signal",),
) -> list[dict[str, Any]]:
    """Select concrete target/opponent cells for claim-dossier repetitions.

    This is intentionally stricter than the rev0053 confluence agenda.  It
    starts from already-confirmed concrete-cell rows and prefers rows with a
    favored-cell label, high average score, and a stable life split.
    """

    preferred = set(map(str, preferred_labels))
    candidates: list[dict[str, Any]] = []
    for row in confirmation_rows:
        target = str(row.get("target", ""))
        opponent = str(row.get("opponent", ""))
        if not target or not opponent:
            continue
        label = str(row.get("confirmation_label", ""))
        avg_score = _f(row, "avg_score")
        min_score = _f(row, "min_score")
        abs_life_delta = _f(row, "abs_life_delta")
        games = _i(row, "games")
        label_bonus = 0.20 if label in preferred else (0.05 if label else 0.0)
        dossier_priority = avg_score + label_bonus + min(0.05, games / 2000.0) - min(0.08, abs_life_delta * 0.25)
        candidates.append(
            {
                "target": target,
                "opponent": opponent,
                "source_confirmation_label": label,
                "source_games": games,
                "source_avg_score": avg_score,
                "source_min_score": min_score,
                "source_life_delta_high_minus_low": _f(row, "life_delta_high_minus_low"),
                "source_abs_life_delta": abs_life_delta,
                "source_confluence_rank": _i(row, "confluence_rank", 999),
                "dossier_priority": dossier_priority,
                "agenda_source": "rev0053_cell_confirm_confirmation",
            }
        )
    candidates.sort(key=lambda r: (r["dossier_priority"], r["source_avg_score"], -r["source_confluence_rank"]), reverse=True)
    return [dict(row, dossier_rank=i + 1) for i, row in enumerate(candidates[: int(top_n)])]


def _target_score(row: Mapping[str, Any]) -> float | None:
    try:
        value = row.get("focus_target_score")
        if value == "" or value is None:
            return None
        return float(value)
    except Exception:
        return None


def _target_terminal_win(row: Mapping[str, Any]) -> float | None:
    try:
        value = row.get("focus_target_terminal_win")
        if value == "" or value is None:
            return None
        return float(value)
    except Exception:
        return None


def _dim_row(rows: Sequence[Mapping[str, Any]], dims: Mapping[str, Any]) -> dict[str, Any]:
    vals = [v for v in (_target_score(r) for r in rows) if v is not None]
    wins = [v for v in (_target_terminal_win(r) for r in rows) if v is not None]
    n = len(vals)
    mean_score = mean(vals) if vals else 0.0
    terminal_win_rate = mean(wins) if wins else 0.0
    ci = hoeffding_interval(mean_score, n)
    wci = wilson_interval(sum(wins), n)
    truncs = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    return {
        **dict(dims),
        "games": n,
        "mean_score_draw_half": mean_score,
        "score_lcb_95": ci.low,
        "score_ucb_95": ci.high,
        "terminal_win_rate": terminal_win_rate,
        "terminal_win_lcb_95": wci.low,
        "terminal_win_ucb_95": wci.high,
        "truncations": truncs,
        "truncation_rate": truncs / n if n else 0.0,
    }


def target_dimension_rows(rows: Sequence[Mapping[str, Any]], agenda: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate target-perspective rows by life, seat, starting player, and totals."""

    agenda_pairs = {(str(a.get("target")), str(a.get("opponent"))) for a in agenda}
    buckets: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pair = (str(row.get("focus_target")), str(row.get("focus_opponent")))
        if pair not in agenda_pairs:
            continue
        target, opponent = pair
        life = _i(row, "starting_life")
        seat = str(row.get("focus_target_seat"))
        sp = str(row.get("starting_player"))
        buckets[(target, opponent, "all", "all", "all")].append(row)
        buckets[(target, opponent, "life", life, "all")].append(row)
        buckets[(target, opponent, "target_seat", seat, "all")].append(row)
        buckets[(target, opponent, "starting_player", sp, "all")].append(row)
        buckets[(target, opponent, "life_x_seat", life, seat)].append(row)
        buckets[(target, opponent, "life_x_starting_player", life, sp)].append(row)

    out: list[dict[str, Any]] = []
    for (target, opponent, dim, value, subvalue), group in sorted(buckets.items(), key=lambda kv: tuple(map(str, kv[0]))):
        out.append(_dim_row(group, {"target": target, "opponent": opponent, "dimension": dim, "value": value, "subvalue": subvalue}))
    return out


def _by_life(target_life_cells: Sequence[Mapping[str, Any]], target: str, opponent: str) -> dict[int, Mapping[str, Any]]:
    out = {}
    for row in target_life_cells:
        if str(row.get("target")) == target and str(row.get("opponent")) == opponent:
            out[_i(row, "starting_life")] = row
    return out


def _dimension_spread(dimension_rows: Sequence[Mapping[str, Any]], target: str, opponent: str, dimension: str) -> float:
    vals = [
        _f(r, "mean_score_draw_half")
        for r in dimension_rows
        if str(r.get("target")) == target and str(r.get("opponent")) == opponent and str(r.get("dimension")) == dimension
    ]
    return max(vals) - min(vals) if len(vals) >= 2 else 0.0


def matchup_claim_rows(
    target_life_cells: Sequence[Mapping[str, Any]],
    dimension_rows: Sequence[Mapping[str, Any]],
    agenda: Sequence[Mapping[str, Any]],
    *,
    life_low: int = 20,
    life_high: int = 40,
    min_total_games: int = 160,
    min_life_games: int = 80,
) -> list[dict[str, Any]]:
    """Build conservative concrete-matchup claim rows from dossier data."""

    out: list[dict[str, Any]] = []
    for item in agenda:
        target = str(item.get("target"))
        opponent = str(item.get("opponent"))
        cells = _by_life(target_life_cells, target, opponent)
        if int(life_low) not in cells or int(life_high) not in cells:
            continue
        lo = cells[int(life_low)]
        hi = cells[int(life_high)]
        games_lo = _i(lo, "games")
        games_hi = _i(hi, "games")
        score_lo = _f(lo, "mean_score_draw_half")
        score_hi = _f(hi, "mean_score_draw_half")
        lcb_lo = _f(lo, "score_lcb_95")
        lcb_hi = _f(hi, "score_lcb_95")
        wins_lo = _f(lo, "terminal_win_rate")
        wins_hi = _f(hi, "terminal_win_rate")
        total_games = games_lo + games_hi
        avg_score = ((score_lo * games_lo) + (score_hi * games_hi)) / total_games if total_games else 0.0
        avg_win = ((wins_lo * games_lo) + (wins_hi * games_hi)) / total_games if total_games else 0.0
        total_lcb = hoeffding_interval(avg_score, total_games).low
        total_ucb = hoeffding_interval(avg_score, total_games).high
        life_delta = score_hi - score_lo
        seat_spread = _dimension_spread(dimension_rows, target, opponent, "target_seat")
        start_spread = _dimension_spread(dimension_rows, target, opponent, "starting_player")
        life_stable = abs(life_delta) <= 0.12
        enough_games = total_games >= int(min_total_games) and games_lo >= int(min_life_games) and games_hi >= int(min_life_games)
        if enough_games and total_lcb > 0.5 and min(score_lo, score_hi) >= 0.58 and life_stable:
            label = "concrete_matchup_claim_candidate"
        elif enough_games and total_lcb > 0.5 and min(score_lo, score_hi) >= 0.55 and not life_stable:
            label = "life_sensitive_matchup_claim_candidate"
        elif enough_games and avg_score >= 0.60 and min(score_lo, score_hi) >= 0.55:
            label = "positive_matchup_watch"
        elif enough_games:
            label = "terminal_clean_signal_only"
        else:
            label = "needs_more_games"
        out.append(
            {
                "target": target,
                "opponent": opponent,
                "games": total_games,
                f"games_life{life_low}": games_lo,
                f"games_life{life_high}": games_hi,
                f"score_life{life_low}": score_lo,
                f"score_life{life_high}": score_hi,
                f"lcb_life{life_low}": lcb_lo,
                f"lcb_life{life_high}": lcb_hi,
                "avg_score": avg_score,
                "avg_terminal_win_rate": avg_win,
                "total_score_lcb_95": total_lcb,
                "total_score_ucb_95": total_ucb,
                "life_delta_high_minus_low": life_delta,
                "abs_life_delta": abs(life_delta),
                "target_seat_score_spread": seat_spread,
                "starting_player_score_spread": start_spread,
                "life_stable": life_stable,
                "claim_label": label,
                "source_dossier_rank": item.get("dossier_rank", ""),
                "source_confirmation_label": item.get("source_confirmation_label", ""),
            }
        )
    out.sort(key=lambda r: (r["claim_label"] == "concrete_matchup_claim_candidate", r["total_score_lcb_95"], r["avg_score"]), reverse=True)
    return out


def matchup_claim_gate(
    rows: Sequence[Mapping[str, Any]],
    claim_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    cpp_summary: Mapping[str, Any],
    min_rows: int = 160,
    require_zero_truncations: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(rows) < min_rows:
        errors.append(f"raw rows {len(rows)} below min_rows {min_rows}")
    truncs = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if require_zero_truncations and truncs:
        errors.append(f"expected zero truncations, saw {truncs}")
    if int(cpp_summary.get("skipped_events", 0)) != 0:
        errors.append(f"C++ skipped events {cpp_summary.get('skipped_events')}")
    if int(cpp_summary.get("mismatches", 0)) != 0:
        errors.append(f"C++ mismatches {cpp_summary.get('mismatches')}")
    claim_candidate_count = sum(1 for r in claim_rows if str(r.get("claim_label")) in {"concrete_matchup_claim_candidate", "life_sensitive_matchup_claim_candidate"})
    if claim_candidate_count == 0:
        warnings.append("no concrete/life-sensitive matchup claim candidate row; dossier is watch/diagnostic only")
    return {
        "revision": revision,
        "passed": not errors,
        "raw_rows": len(rows),
        "claim_rows": len(claim_rows),
        "truncations": truncs,
        "claim_candidate_count": claim_candidate_count,
        "warnings": warnings,
        "errors": errors,
    }
