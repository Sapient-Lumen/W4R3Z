from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .population_lineage import source_qualified_game_id
from .terminal_mechanisms import (
    annotate_focus_target_from_seat,
    loser_role,
    loss_loser,
    result_label,
    target_score_from_seat,
    terminal_mechanism,
    to_float,
    to_int,
)

MISMATCH_COLUMNS: tuple[str, ...] = (
    "source_file",
    "source_revision",
    "row_index",
    "cpp_shadow_game_id",
    "source_qualified_game_id",
    "check",
    "expected",
    "observed",
)


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def _float_close(left: Any, right: Any, *, tolerance: float = 1e-12) -> bool:
    return abs(to_float(left, float("nan")) - to_float(right, float("nan"))) <= tolerance


def _score_expected_from_winner(row: Mapping[str, Any], seat: int) -> float | None:
    winner_raw = row.get("winner")
    if winner_raw in {None, ""}:
        if _boolish(row.get("is_nonterminal_draw")):
            return 0.5
        return None
    winner = to_int(winner_raw, -1)
    if winner not in (0, 1):
        return None
    return 1.0 if winner == seat else 0.0


def _add_mismatch(
    mismatches: list[dict[str, object]],
    row: Mapping[str, Any],
    *,
    source_file: str,
    row_index: int,
    check: str,
    expected: Any,
    observed: Any,
) -> None:
    enriched = dict(row)
    if not enriched.get("source_revision"):
        enriched["source_revision"] = enriched.get("simulator_revision") or ""
    mismatches.append(
        {
            "source_file": source_file,
            "source_revision": _string(enriched.get("source_revision") or enriched.get("simulator_revision")),
            "row_index": int(row_index),
            "cpp_shadow_game_id": _string(enriched.get("cpp_shadow_game_id")),
            "source_qualified_game_id": source_qualified_game_id(enriched),
            "check": check,
            "expected": _string(expected),
            "observed": _string(observed),
        }
    )


def audit_population_score_orientation_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_file: str = "",
    start_index: int = 0,
    tolerance: float = 1e-12,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Audit target-perspective score/result/mechanism columns in raw games.

    The population gate is only meaningful if target score orientation is stable
    across seat flips.  This check recomputes focus fields from raw p0/p1 score,
    target seat, winner, and terminal loss reason, then compares them to the
    stored columns.  It is intentionally row-level and fail-closed: malformed
    seats, unbounded scores, missing focus columns, or inconsistent terminal
    flags become explicit mismatches.
    """

    mismatches: list[dict[str, object]] = []
    target_seats: Counter[int] = Counter()
    mechanisms: Counter[str] = Counter()
    results: Counter[str] = Counter()
    score_values: Counter[str] = Counter()
    source_revisions: Counter[str] = Counter()
    terminal_status: Counter[str] = Counter()
    terminal_loss_roles: Counter[str] = Counter()

    for offset, raw in enumerate(rows):
        row = dict(raw)
        row_index = int(start_index + offset)
        if not row.get("source_revision"):
            row["source_revision"] = row.get("simulator_revision") or ""
        source_revisions[_string(row.get("source_revision"))] += 1
        seat = to_int(row.get("target_seat"), -1)
        target_seats[seat] += 1
        terminal_status[_string(row.get("terminal_clean_status"))] += 1

        if seat not in (0, 1):
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="target_seat_valid", expected="0_or_1", observed=row.get("target_seat"))
            continue

        expected_score = target_score_from_seat(row, seat)
        expected_result = result_label(expected_score)
        expected_loser = loss_loser(_string(row.get("loss_reason")))
        expected_loser_role = loser_role(expected_loser, seat)
        expected_mechanism = terminal_mechanism(_string(row.get("loss_reason")))
        expected_library_win = bool(expected_score > 0.5 and expected_mechanism == "library_out" and expected_loser_role == "opponent")
        expected_life_win = bool(expected_score > 0.5 and expected_mechanism == "life_total" and expected_loser_role == "opponent")

        recomputed = annotate_focus_target_from_seat(row)
        mechanisms[expected_mechanism] += 1
        results[expected_result] += 1
        score_values[f"{expected_score:.1f}"] += 1
        terminal_loss_roles[expected_loser_role] += 1

        if to_int(row.get("focus_target_seat"), -999) != seat:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_target_seat", expected=seat, observed=row.get("focus_target_seat"))
        if not _float_close(row.get("focus_target_score"), expected_score, tolerance=tolerance):
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_target_score", expected=expected_score, observed=row.get("focus_target_score"))
        if _string(row.get("focus_target_result")) != expected_result:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_target_result", expected=expected_result, observed=row.get("focus_target_result"))
        if _string(row.get("focus_terminal_mechanism")) != expected_mechanism:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_terminal_mechanism", expected=expected_mechanism, observed=row.get("focus_terminal_mechanism"))
        observed_loser = "" if row.get("focus_terminal_loser") in {None, ""} else to_int(row.get("focus_terminal_loser"), -1)
        expected_loser_value: object = "" if expected_loser is None else int(expected_loser)
        if observed_loser != expected_loser_value:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_terminal_loser", expected=expected_loser_value, observed=row.get("focus_terminal_loser"))
        if _string(row.get("focus_terminal_loser_role")) != expected_loser_role:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_terminal_loser_role", expected=expected_loser_role, observed=row.get("focus_terminal_loser_role"))
        if _boolish(row.get("focus_is_library_out_win")) != expected_library_win:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_is_library_out_win", expected=expected_library_win, observed=row.get("focus_is_library_out_win"))
        if _boolish(row.get("focus_is_life_total_win")) != expected_life_win:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="focus_is_life_total_win", expected=expected_life_win, observed=row.get("focus_is_life_total_win"))

        # Cross-check the central helper did not diverge from the explicit expectations.
        if not _float_close(recomputed.get("focus_target_score"), expected_score, tolerance=tolerance):
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="central_helper_focus_target_score", expected=expected_score, observed=recomputed.get("focus_target_score"))

        if not (0.0 <= to_float(row.get("p0_score"), float("nan")) <= 1.0):
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="p0_score_bounded", expected="0..1", observed=row.get("p0_score"))
        if not (0.0 <= to_float(row.get("p1_score"), float("nan")) <= 1.0):
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="p1_score_bounded", expected="0..1", observed=row.get("p1_score"))
        score_sum = to_float(row.get("p0_score"), 0.0) + to_float(row.get("p1_score"), 0.0)
        if abs(score_sum - 1.0) > tolerance:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="score_sum", expected="1.0", observed=score_sum)
        winner_expected_score = _score_expected_from_winner(row, seat)
        if winner_expected_score is not None and abs(expected_score - winner_expected_score) > tolerance:
            _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="winner_score_orientation", expected=winner_expected_score, observed=expected_score)
        if expected_loser is not None and row.get("winner") not in {None, ""}:
            winner = to_int(row.get("winner"), -1)
            if winner == expected_loser:
                _add_mismatch(mismatches, row, source_file=source_file, row_index=row_index, check="winner_not_loser", expected=f"not {expected_loser}", observed=winner)

    summary = {
        "rows": len(rows),
        "mismatches": len(mismatches),
        "passed": len(mismatches) == 0,
        "source_revisions": dict(sorted(source_revisions.items())),
        "target_seat_counts": {str(k): v for k, v in sorted(target_seats.items())},
        "expected_result_counts": dict(sorted(results.items())),
        "expected_terminal_mechanism_counts": dict(sorted(mechanisms.items())),
        "expected_terminal_loser_role_counts": dict(sorted(terminal_loss_roles.items())),
        "expected_score_counts": dict(sorted(score_values.items())),
        "terminal_clean_status_counts": dict(sorted(terminal_status.items())),
        "mismatch_counts": dict(sorted(Counter(_string(m["check"]) for m in mismatches).items())),
        "target_seat_0_rows": target_seats.get(0, 0),
        "target_seat_1_rows": target_seats.get(1, 0),
    }
    return mismatches, summary


def audit_population_score_orientation_sources(
    source_rows: Sequence[tuple[str, Sequence[Mapping[str, Any]]]],
) -> dict[str, object]:
    """Audit several raw population-game sources and return merged diagnostics."""

    all_mismatches: list[dict[str, object]] = []
    by_source: list[dict[str, object]] = []
    aggregate_rows: list[Mapping[str, Any]] = []
    start = 0
    for source_file, rows in source_rows:
        mismatches, summary = audit_population_score_orientation_rows(rows, source_file=source_file, start_index=start)
        summary_row = dict(summary)
        summary_row["source_file"] = source_file
        by_source.append(summary_row)
        all_mismatches.extend(mismatches)
        aggregate_rows.extend(rows)
        start += len(rows)

    _, aggregate_summary = audit_population_score_orientation_rows(aggregate_rows, source_file="ALL", start_index=0)
    aggregate_summary.update(
        {
            "sources": len(source_rows),
            "source_files": [source for source, _rows in source_rows],
            "by_source": by_source,
            "passed": aggregate_summary.get("passed") is True and all(row.get("passed") is True for row in by_source),
            "mismatches": len(all_mismatches),
        }
    )
    return {"summary": aggregate_summary, "by_source": by_source, "mismatches": all_mismatches}


__all__ = [
    "MISMATCH_COLUMNS",
    "audit_population_score_orientation_rows",
    "audit_population_score_orientation_sources",
]
