from __future__ import annotations

import re
from collections import Counter, defaultdict
from statistics import mean, median
from typing import Any, Iterable, Mapping, Sequence

from .statgate import hoeffding_interval, wilson_interval


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def loss_loser(loss_reason: str | None) -> int | None:
    """Return the player index named in a terminal loss reason, if present."""

    match = re.search(r"player_([01])_", loss_reason or "")
    return int(match.group(1)) if match else None


def terminal_mechanism(loss_reason: str | None) -> str:
    """Map engine loss reasons into stable, reportable mechanism buckets."""

    lr = loss_reason or ""
    if "draw_from_empty_library" in lr:
        return "library_out"
    if "life_total_zero_or_less" in lr or "zero_or_less" in lr:
        return "life_total"
    if "max_decisions_reached" in lr or "truncation" in lr:
        return "truncation"
    if lr:
        return "other_terminal"
    return "unknown"


def result_label(score: Any) -> str:
    value = to_float(score, 0.5)
    if value > 0.5:
        return "target_win"
    if value < 0.5:
        return "target_loss"
    return "target_draw"


def loser_role(loser: int | None, target_seat: int | str | None) -> str:
    if loser is None:
        return "unknown"
    try:
        seat = int(target_seat)  # type: ignore[arg-type]
    except Exception:
        return "unknown"
    return "target" if loser == seat else "opponent"


def annotate_target_mechanism(
    row: Mapping[str, Any],
    *,
    target_score_key: str = "focus_target_score",
    target_seat_key: str = "focus_target_seat",
    prefix: str = "focus",
) -> dict[str, Any]:
    """Add target-perspective terminal mechanism columns without changing source fields."""

    out = dict(row)
    loss_reason = str(out.get("loss_reason", ""))
    loser = loss_loser(loss_reason)
    target_score = to_float(out.get(target_score_key), 0.5)
    out[f"{prefix}_target_result"] = result_label(target_score)
    out[f"{prefix}_terminal_mechanism"] = terminal_mechanism(loss_reason)
    out[f"{prefix}_terminal_loser"] = "" if loser is None else int(loser)
    out[f"{prefix}_terminal_loser_role"] = loser_role(loser, out.get(target_seat_key))
    out[f"{prefix}_is_library_out_win"] = bool(
        target_score > 0.5
        and out[f"{prefix}_terminal_mechanism"] == "library_out"
        and out[f"{prefix}_terminal_loser_role"] == "opponent"
    )
    out[f"{prefix}_is_life_total_win"] = bool(
        target_score > 0.5
        and out[f"{prefix}_terminal_mechanism"] == "life_total"
        and out[f"{prefix}_terminal_loser_role"] == "opponent"
    )
    return out



def target_score_from_seat(row: Mapping[str, Any], target_seat: int | str | None) -> float:
    """Return the target-perspective score implied by a player seat.

    Population and response-matrix runners alternate the target between player 0
    and player 1 to balance seat/start-player effects.  This helper is the
    single orientation primitive: target score must be the score column owned by
    the normalized target seat, not whatever player happened to be listed first.
    """

    seat = to_int(target_seat, -1)
    if seat not in (0, 1):
        return 0.5
    return to_float(row.get("p0_score" if seat == 0 else "p1_score"), 0.5)


def annotate_focus_target_from_seat(
    row: Mapping[str, Any],
    *,
    target_seat_key: str = "target_seat",
    focus_target_seat_key: str = "focus_target_seat",
    focus_target_score_key: str = "focus_target_score",
) -> dict[str, Any]:
    """Add focus target seat/score/mechanism fields from one canonical orientation.

    Older scripts hand-rolled ``p0_score if target_seat == 0 else p1_score``.
    Keeping that logic here makes later audits and population runners share the
    same target-perspective contract.
    """

    out = dict(row)
    seat = to_int(out.get(target_seat_key), -1)
    out[focus_target_seat_key] = seat
    out[focus_target_score_key] = target_score_from_seat(out, seat)
    return annotate_target_mechanism(
        out,
        target_score_key=focus_target_score_key,
        target_seat_key=focus_target_seat_key,
        prefix="focus",
    )

def mechanism_profile_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    group_keys: Sequence[str] = ("starting_life",),
    target_score_key: str = "focus_target_score",
    target_seat_key: str = "focus_target_seat",
    prefix: str = "focus",
) -> list[dict[str, Any]]:
    """Count target result x terminal mechanism x loser role by arbitrary groups."""

    counts: Counter[tuple[Any, ...]] = Counter()
    totals: Counter[tuple[Any, ...]] = Counter()
    for raw in rows:
        row = annotate_target_mechanism(raw, target_score_key=target_score_key, target_seat_key=target_seat_key, prefix=prefix)
        group = tuple(row.get(k, "") for k in group_keys)
        key = group + (
            row[f"{prefix}_target_result"],
            row[f"{prefix}_terminal_mechanism"],
            row[f"{prefix}_terminal_loser_role"],
        )
        counts[key] += 1
        totals[group] += 1
    out: list[dict[str, Any]] = []
    for key, n in sorted(counts.items()):
        group = key[: len(group_keys)]
        row = {k: v for k, v in zip(group_keys, group)}
        row.update(
            {
                "target_result": key[len(group_keys)],
                "terminal_mechanism": key[len(group_keys) + 1],
                "terminal_loser_role": key[len(group_keys) + 2],
                "games": int(n),
                "share_of_group": 0.0 if totals[group] == 0 else n / totals[group],
            }
        )
        out.append(row)
    return out


def target_summary_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    group_keys: Sequence[str],
    target_score_key: str = "focus_target_score",
    target_seat_key: str = "focus_target_seat",
    prefix: str = "focus",
) -> list[dict[str, Any]]:
    """Summarize target-perspective score, terminal mechanisms, and pace by group."""

    buckets: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for raw in rows:
        row = annotate_target_mechanism(raw, target_score_key=target_score_key, target_seat_key=target_seat_key, prefix=prefix)
        buckets[tuple(row.get(k, "") for k in group_keys)].append(row)

    out: list[dict[str, Any]] = []
    for group, group_rows in sorted(buckets.items()):
        n = len(group_rows)
        scores = [to_float(r.get(target_score_key), 0.5) for r in group_rows]
        wins = sum(1 for s in scores if s > 0.5)
        losses = sum(1 for s in scores if s < 0.5)
        draws = n - wins - losses
        truncs = sum(1 for r in group_rows if truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
        library_win = sum(1 for r in group_rows if truthy(r.get(f"{prefix}_is_library_out_win")))
        life_win = sum(1 for r in group_rows if truthy(r.get(f"{prefix}_is_life_total_win")))
        opp_library_losses = sum(
            1
            for r in group_rows
            if r.get(f"{prefix}_terminal_mechanism") == "library_out" and r.get(f"{prefix}_terminal_loser_role") == "opponent"
        )
        target_library_losses = sum(
            1
            for r in group_rows
            if r.get(f"{prefix}_terminal_mechanism") == "library_out" and r.get(f"{prefix}_terminal_loser_role") == "target"
        )
        decisions = [to_int(r.get("decisions"), 0) for r in group_rows]
        turns = [to_int(r.get("turn_number"), 0) for r in group_rows]
        mean_score = mean(scores) if scores else 0.0
        score_ci = hoeffding_interval(mean_score, n)
        win_ci = wilson_interval(wins, n)
        row = {k: v for k, v in zip(group_keys, group)}
        row.update(
            {
                "games": int(n),
                "target_mean_score_draw_half": mean_score,
                "target_score_lcb_95": score_ci.low,
                "target_score_ucb_95": score_ci.high,
                "target_terminal_win_rate": wins / n if n else 0.0,
                "target_terminal_win_lcb_95": win_ci.low,
                "target_terminal_win_ucb_95": win_ci.high,
                "target_terminal_wins": int(wins),
                "target_terminal_losses": int(losses),
                "target_draws": int(draws),
                "truncations": int(truncs),
                "truncation_rate": truncs / n if n else 0.0,
                "target_library_out_wins": int(library_win),
                "target_life_total_wins": int(life_win),
                "opponent_library_out_losses": int(opp_library_losses),
                "target_library_out_losses": int(target_library_losses),
                "library_out_win_share": library_win / wins if wins else 0.0,
                "mean_decisions": mean(decisions) if decisions else 0.0,
                "median_decisions": median(decisions) if decisions else 0.0,
                "mean_turn_number": mean(turns) if turns else 0.0,
                "median_turn_number": median(turns) if turns else 0.0,
            }
        )
        out.append(row)
    return out


def mechanism_counts(rows: Iterable[Mapping[str, Any]], *, mechanism_key: str = "focus_terminal_mechanism") -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts[str(row.get(mechanism_key, ""))] += 1
    return dict(sorted(counts.items()))
