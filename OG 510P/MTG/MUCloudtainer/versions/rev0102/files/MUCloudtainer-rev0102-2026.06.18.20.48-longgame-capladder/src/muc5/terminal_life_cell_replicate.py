from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Mapping, Sequence

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


def life_cell_replication_agenda(
    cumulative_cell_rows: Sequence[Mapping[str, Any]],
    *,
    top_n_cells: int = 2,
) -> list[dict[str, Any]]:
    """Select life-specific cells for an independent holdout replication block.

    rev0055 elevated two life cells for the same target/opponent pair.  The next
    honest step is not to average more rows into the same dossier immediately; it is
    to run a seed-disjoint holdout block and compare the new evidence to the prior
    cumulative cell row.
    """

    candidates: list[dict[str, Any]] = []
    for row in cumulative_cell_rows:
        target = str(row.get("target", ""))
        opponent = str(row.get("opponent", ""))
        life = _i(row, "starting_life", 0)
        if not target or not opponent or life not in (20, 40):
            continue
        games = _i(row, "games")
        score = _f(row, "mean_score_draw_half")
        lcb = _f(row, "score_lcb_95")
        label = str(row.get("cell_signal", ""))
        label_bonus = 0.30 if label == "life_cell_claim_candidate" else (0.10 if label == "positive_life_cell_watch" else 0.0)
        # Prefer cells that are both promising and already have enough context to
        # deserve a holdout check.  Life 20 is not given special treatment; the
        # evidence row must earn its slot.
        priority = label_bonus + score + max(0.0, lcb - 0.5) + min(0.05, games / 10000.0)
        candidates.append({
            "target": target,
            "opponent": opponent,
            "starting_life": int(life),
            "prior_games": games,
            "prior_score": score,
            "prior_score_lcb_95": lcb,
            "prior_score_ucb_95": _f(row, "score_ucb_95"),
            "prior_terminal_win_rate": _f(row, "terminal_win_rate"),
            "prior_terminal_win_lcb_95": _f(row, "terminal_win_lcb_95"),
            "prior_terminal_win_ucb_95": _f(row, "terminal_win_ucb_95"),
            "prior_cell_signal": label,
            "agenda_priority": priority,
            "agenda_reason": "independent_holdout_replication",
            "agenda_source": "rev0055_life_cell_cumulative_cells",
        })
    candidates.sort(key=lambda r: (r["agenda_priority"], r["prior_score_lcb_95"], r["prior_score"]), reverse=True)
    out = candidates[: int(top_n_cells)]
    for idx, row in enumerate(out, 1):
        row["replication_agenda_rank"] = idx
    return out


def holdout_cell_rows(cell_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Normalize current-only life-cell summary rows into holdout terminology."""

    out: list[dict[str, Any]] = []
    for row in cell_rows:
        games = _i(row, "games")
        score = _f(row, "mean_score_draw_half")
        lcb = _f(row, "score_lcb_95")
        ucb = _f(row, "score_ucb_95")
        if games >= 96 and lcb > 0.5 and score >= 0.58:
            label = "holdout_replicated_candidate"
        elif games >= 96 and score >= 0.55:
            label = "holdout_positive_watch"
        elif games >= 96 and ucb < 0.5:
            label = "holdout_contradicted"
        else:
            label = "holdout_uncertain"
        out.append({
            "target": str(row.get("target", "")),
            "opponent": str(row.get("opponent", "")),
            "starting_life": _i(row, "starting_life"),
            "holdout_games": games,
            "holdout_score": score,
            "holdout_score_lcb_95": lcb,
            "holdout_score_ucb_95": ucb,
            "holdout_terminal_win_rate": _f(row, "terminal_win_rate"),
            "holdout_terminal_win_lcb_95": _f(row, "terminal_win_lcb_95"),
            "holdout_terminal_win_ucb_95": _f(row, "terminal_win_ucb_95"),
            "holdout_truncations": _i(row, "truncations"),
            "holdout_label": label,
        })
    return out


def replication_comparison_rows(
    prior_rows: Sequence[Mapping[str, Any]],
    holdout_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compare prior cumulative cell evidence against a seed-disjoint holdout block."""

    prior = {(str(r.get("target")), str(r.get("opponent")), _i(r, "starting_life")): r for r in prior_rows}
    out: list[dict[str, Any]] = []
    for hold in holdout_rows:
        key = (str(hold.get("target")), str(hold.get("opponent")), _i(hold, "starting_life"))
        prev = prior.get(key, {})
        prior_games = _i(prev, "games")
        prior_score = _f(prev, "mean_score_draw_half")
        hold_games = _i(hold, "holdout_games")
        hold_score = _f(hold, "holdout_score")
        total_games = prior_games + hold_games
        combined_score = ((prior_score * prior_games) + (hold_score * hold_games)) / total_games if total_games else 0.0
        ci = hoeffding_interval(combined_score, total_games)
        # Treat the holdout as a replication only when it is independently positive;
        # the combined row is reported, but cannot rescue a failed holdout by itself.
        hold_label = str(hold.get("holdout_label", ""))
        if hold_label == "holdout_replicated_candidate" and ci.low > 0.5:
            label = "replicated_life_cell_claim_candidate"
        elif hold_label == "holdout_positive_watch" and combined_score >= 0.58 and ci.low > 0.5:
            label = "soft_replicated_life_cell_watch"
        elif hold_label == "holdout_contradicted":
            label = "holdout_contradiction"
        else:
            label = "replication_uncertain"
        out.append({
            "target": key[0],
            "opponent": key[1],
            "starting_life": key[2],
            "prior_games": prior_games,
            "prior_score": prior_score,
            "prior_score_lcb_95": _f(prev, "score_lcb_95"),
            "prior_score_ucb_95": _f(prev, "score_ucb_95"),
            "prior_cell_signal": str(prev.get("cell_signal", "")),
            "holdout_games": hold_games,
            "holdout_score": hold_score,
            "holdout_score_lcb_95": _f(hold, "holdout_score_lcb_95"),
            "holdout_score_ucb_95": _f(hold, "holdout_score_ucb_95"),
            "holdout_label": hold_label,
            "holdout_minus_prior_score": hold_score - prior_score,
            "combined_games": total_games,
            "combined_score": combined_score,
            "combined_score_lcb_95": ci.low,
            "combined_score_ucb_95": ci.high,
            "replication_label": label,
        })
    return out


def dimension_stability_rows(dimension_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Summarize seat/start imbalance inside each target/opponent/life cell."""

    buckets: dict[tuple[str, str, int, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in dimension_rows:
        dim = str(row.get("dimension", ""))
        if dim in {"target_seat", "starting_player"}:
            buckets[(str(row.get("target")), str(row.get("opponent")), _i(row, "starting_life"), dim)].append(row)
    out: list[dict[str, Any]] = []
    for (target, opponent, life, dim), group in sorted(buckets.items()):
        if len(group) < 2:
            continue
        scores = [_f(r, "mean_score_draw_half") for r in group]
        games = sum(_i(r, "games") for r in group)
        spread = max(scores) - min(scores)
        if spread >= 0.25:
            label = "dimension_instability_watch"
        elif spread >= 0.15:
            label = "dimension_mild_instability"
        else:
            label = "dimension_stable_smoke"
        out.append({
            "target": target,
            "opponent": opponent,
            "starting_life": int(life),
            "dimension": dim,
            "values": ";".join(str(r.get("value")) for r in group),
            "games": games,
            "score_min": min(scores),
            "score_max": max(scores),
            "score_spread": spread,
            "dimension_label": label,
        })
    return out


def life_cell_replication_gate(
    raw_rows: Sequence[Mapping[str, Any]],
    holdout_rows: Sequence[Mapping[str, Any]],
    comparison_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    cpp_summary: Mapping[str, Any],
    replay_results: Sequence[Mapping[str, Any]] = (),
    min_raw_rows: int = 160,
    min_holdout_games_per_cell: int = 96,
    require_zero_truncations: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(raw_rows) < int(min_raw_rows):
        errors.append(f"raw rows {len(raw_rows)} below min_raw_rows {min_raw_rows}")
    truncs = sum(1 for r in raw_rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if require_zero_truncations and truncs:
        errors.append(f"expected zero truncations, saw {truncs}")
    if int(cpp_summary.get("skipped_events", 0)) != 0:
        errors.append(f"C++ skipped events {cpp_summary.get('skipped_events')}")
    if int(cpp_summary.get("mismatches", 0)) != 0:
        errors.append(f"C++ mismatches {cpp_summary.get('mismatches')}")
    small = [r for r in holdout_rows if _i(r, "holdout_games") < int(min_holdout_games_per_cell)]
    if small:
        errors.append(f"{len(small)} holdout cells below min_holdout_games_per_cell {min_holdout_games_per_cell}")
    if replay_results:
        failed = [r for r in replay_results if r.get("passed") is not True]
        if failed:
            errors.append(f"{len(failed)} replay sample failures")
    replicated = sum(1 for r in comparison_rows if str(r.get("replication_label")) == "replicated_life_cell_claim_candidate")
    soft = sum(1 for r in comparison_rows if str(r.get("replication_label")) == "soft_replicated_life_cell_watch")
    contrad = sum(1 for r in comparison_rows if str(r.get("replication_label")) == "holdout_contradiction")
    if replicated == 0:
        warnings.append("no holdout cell crossed the strict replicated_life_cell_claim_candidate threshold")
    if contrad:
        warnings.append(f"{contrad} holdout contradiction rows observed")
    return {
        "revision": revision,
        "passed": not errors,
        "raw_rows": len(raw_rows),
        "holdout_cells": len(holdout_rows),
        "comparison_rows": len(comparison_rows),
        "truncations": truncs,
        "replicated_claim_cells": replicated,
        "soft_replicated_watch_cells": soft,
        "holdout_contradictions": contrad,
        "errors": errors,
        "warnings": warnings,
    }
