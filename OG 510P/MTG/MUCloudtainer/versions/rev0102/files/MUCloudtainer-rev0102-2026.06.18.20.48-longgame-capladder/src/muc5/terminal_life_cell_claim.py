from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .payoff import StrategyBundle
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


def life_cell_agenda_from_matchup_claim(
    claim_rows: Sequence[Mapping[str, Any]],
    target_life_cells: Sequence[Mapping[str, Any]],
    *,
    top_n_pairs: int = 1,
    life_totals: Sequence[int] = (20, 40),
) -> list[dict[str, Any]]:
    """Turn a concrete matchup dossier into per-life cell agenda rows.

    rev0054 taught us that the cf34/pub_threat claim was life-sensitive.  The
    next honest unit is not a single averaged matchup row; it is a target / opponent
    / life cell.  This helper prefers claim rows that were already dossier candidates
    and then emits one agenda row per life total.
    """

    by_cell: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for row in target_life_cells:
        by_cell[(str(row.get("target")), str(row.get("opponent")), _i(row, "starting_life"))] = row

    ranked_pairs: list[dict[str, Any]] = []
    for row in claim_rows:
        target = str(row.get("target", ""))
        opponent = str(row.get("opponent", ""))
        if not target or not opponent:
            continue
        label = str(row.get("claim_label", ""))
        label_bonus = 0.30 if label == "life_sensitive_matchup_claim_candidate" else (0.20 if label == "concrete_matchup_claim_candidate" else 0.0)
        priority = _f(row, "avg_score") + label_bonus + min(0.10, _f(row, "abs_life_delta") * 0.25) + min(0.05, _f(row, "total_score_lcb_95") * 0.05)
        ranked_pairs.append({
            "target": target,
            "opponent": opponent,
            "source_claim_label": label,
            "source_games": _i(row, "games"),
            "source_avg_score": _f(row, "avg_score"),
            "source_total_score_lcb_95": _f(row, "total_score_lcb_95"),
            "source_life_delta_high_minus_low": _f(row, "life_delta_high_minus_low"),
            "source_abs_life_delta": _f(row, "abs_life_delta"),
            "pair_priority": priority,
        })
    ranked_pairs.sort(key=lambda r: (r["pair_priority"], r["source_avg_score"]), reverse=True)

    agenda: list[dict[str, Any]] = []
    for pair_rank, pair in enumerate(ranked_pairs[: int(top_n_pairs)], 1):
        for life in map(int, life_totals):
            prev = by_cell.get((pair["target"], pair["opponent"], int(life)), {})
            lcb = _f(prev, "score_lcb_95")
            score = _f(prev, "mean_score_draw_half")
            # Prefer the weak side of a life-sensitive claim but still verify the strong side.
            if lcb <= 0.50:
                reason = "needs_life_cell_confirmation"
            elif score >= 0.70:
                reason = "verify_strong_life_cell"
            else:
                reason = "balance_life_cell_context"
            agenda.append({
                **pair,
                "pair_rank": pair_rank,
                "starting_life": int(life),
                "previous_games": _i(prev, "games"),
                "previous_score": score,
                "previous_score_lcb_95": lcb,
                "previous_score_ucb_95": _f(prev, "score_ucb_95"),
                "previous_terminal_win_rate": _f(prev, "terminal_win_rate"),
                "previous_cell_signal": str(prev.get("cell_signal", "")),
                "agenda_reason": reason,
                "agenda_source": "rev0054_matchup_claim_life_cells",
            })
    for i, row in enumerate(agenda, 1):
        row["cell_agenda_rank"] = i
    return agenda


def focused_life_cell_specs(
    strategies: Sequence[StrategyBundle],
    agenda_cells: Sequence[Mapping[str, Any]],
    *,
    simulator_revision: str,
    reps: int = 32,
    base_seed: int = 5555000,
    max_decisions: int = 900,
) -> tuple[CppShadowGameSpec, ...]:
    """Build target/opponent/life-specific terminal-clean game specs."""

    by_id = {s.strategy_id: s for s in strategies}
    specs: list[CppShadowGameSpec] = []
    k = 0
    for cell_index, row in enumerate(agenda_cells):
        target_id = str(row.get("target"))
        opponent_id = str(row.get("opponent"))
        life = _i(row, "starting_life", 20)
        if target_id not in by_id or opponent_id not in by_id:
            continue
        target = by_id[target_id]
        opponent = by_id[opponent_id]
        for target_seat in (0, 1):
            left, right = (target, opponent) if target_seat == 0 else (opponent, target)
            for starting_player in (0, 1):
                for rep in range(int(reps)):
                    specs.append(
                        CppShadowGameSpec(
                            game_id=f"g{k:05d}_c{cell_index:02d}_{target_id}_vs_{opponent_id}_life{life}_seat{target_seat}_sp{starting_player}_r{rep}",
                            strategy0=left.strategy_id,
                            strategy1=right.strategy_id,
                            deck0_name=left.deck_name,
                            deck1_name=right.deck_name,
                            deck0=left.deck,
                            deck1=right.deck,
                            agent0=left.agent_name,
                            agent1=right.agent_name,
                            mulligan0=str(left.mulligan_policy),
                            mulligan1=str(right.mulligan_policy),
                            seed=int(base_seed + k),
                            starting_player=int(starting_player),
                            starting_life=int(life),
                            max_decisions=int(max_decisions),
                            simulator_revision=simulator_revision,
                        )
                    )
                    k += 1
    return tuple(specs)


def _score_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return _f(row, "p0_score")
    if str(row.get("strategy1")) == strategy:
        return _f(row, "p1_score")
    return None


def _terminal_win_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return _f(row, "p0_terminal_win")
    if str(row.get("strategy1")) == strategy:
        return _f(row, "p1_terminal_win")
    return None


def annotate_life_cell_rows(rows: Sequence[Mapping[str, Any]], agenda_cells: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Add target-perspective metadata to rows generated by focused_life_cell_specs."""

    out: list[dict[str, Any]] = []
    for row in rows:
        r = dict(row)
        gid = str(r.get("cpp_shadow_game_id", ""))
        parts = gid.split("_")
        cell_index = None
        if len(parts) >= 2 and parts[1].startswith("c"):
            try:
                cell_index = int(parts[1][1:])
            except Exception:
                cell_index = None
        if cell_index is not None and 0 <= cell_index < len(agenda_cells):
            agenda = agenda_cells[cell_index]
            target = str(agenda.get("target"))
            opponent = str(agenda.get("opponent"))
            score = _score_for_strategy(r, target)
            win = _terminal_win_for_strategy(r, target)
            r["focus_cell_index"] = cell_index
            r["focus_target"] = target
            r["focus_opponent"] = opponent
            r["focus_target_seat"] = 0 if str(r.get("strategy0")) == target else (1 if str(r.get("strategy1")) == target else "")
            r["focus_target_score"] = "" if score is None else score
            r["focus_target_terminal_win"] = "" if win is None else win
            r["focus_cell_agenda_reason"] = str(agenda.get("agenda_reason", ""))
        else:
            r["focus_cell_index"] = ""
            r["focus_target"] = ""
            r["focus_opponent"] = ""
            r["focus_target_seat"] = ""
            r["focus_target_score"] = ""
            r["focus_target_terminal_win"] = ""
            r["focus_cell_agenda_reason"] = ""
        out.append(r)
    return out


def life_cell_summary_rows(rows: Sequence[Mapping[str, Any]], agenda_cells: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate target-perspective rows by target/opponent/life."""

    previous = {(str(a.get("target")), str(a.get("opponent")), _i(a, "starting_life")): a for a in agenda_cells}
    buckets: dict[tuple[str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        target = str(row.get("focus_target", ""))
        opponent = str(row.get("focus_opponent", ""))
        if not target or not opponent:
            continue
        buckets[(target, opponent, _i(row, "starting_life"))].append(row)
    out: list[dict[str, Any]] = []
    for (target, opponent, life), group in sorted(buckets.items()):
        vals = [v for v in (_target_score(r) for r in group) if v is not None]
        wins = [v for v in (_target_terminal_win(r) for r in group) if v is not None]
        n = len(vals)
        score = mean(vals) if vals else 0.0
        win_rate = mean(wins) if wins else 0.0
        ci = hoeffding_interval(score, n)
        wci = wilson_interval(sum(wins), n)
        truncs = sum(1 for r in group if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
        prev = previous.get((target, opponent, int(life)), {})
        if n >= 160 and ci.low > 0.5 and score >= 0.58:
            signal = "life_cell_claim_candidate"
        elif n >= 120 and score >= 0.58:
            signal = "positive_life_cell_watch"
        elif n >= 120 and ci.high < 0.5:
            signal = "negative_life_cell_signal"
        else:
            signal = "uncertain_life_cell"
        out.append({
            "target": target,
            "opponent": opponent,
            "starting_life": int(life),
            "games": n,
            "mean_score_draw_half": score,
            "score_lcb_95": ci.low,
            "score_ucb_95": ci.high,
            "terminal_win_rate": win_rate,
            "terminal_win_lcb_95": wci.low,
            "terminal_win_ucb_95": wci.high,
            "truncations": truncs,
            "truncation_rate": truncs / n if n else 0.0,
            "previous_games": _i(prev, "previous_games"),
            "previous_score": _f(prev, "previous_score"),
            "previous_score_lcb_95": _f(prev, "previous_score_lcb_95"),
            "score_shift_vs_previous": "" if not prev else score - _f(prev, "previous_score"),
            "agenda_reason": str(prev.get("agenda_reason", "")),
            "cell_signal": signal,
        })
    return out


def life_cell_dimension_rows(rows: Sequence[Mapping[str, Any]], agenda_cells: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate target-perspective rows by life plus seat/start dimensions."""

    agenda_keys = {(str(a.get("target")), str(a.get("opponent")), _i(a, "starting_life")) for a in agenda_cells}
    buckets: dict[tuple[str, str, int, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        target = str(row.get("focus_target", ""))
        opponent = str(row.get("focus_opponent", ""))
        life = _i(row, "starting_life")
        if (target, opponent, life) not in agenda_keys:
            continue
        seat = str(row.get("focus_target_seat"))
        sp = str(row.get("starting_player"))
        buckets[(target, opponent, life, "all", "all")].append(row)
        buckets[(target, opponent, life, "target_seat", seat)].append(row)
        buckets[(target, opponent, life, "starting_player", sp)].append(row)
    out: list[dict[str, Any]] = []
    for (target, opponent, life, dim, value), group in sorted(buckets.items()):
        vals = [v for v in (_target_score(r) for r in group) if v is not None]
        wins = [v for v in (_target_terminal_win(r) for r in group) if v is not None]
        n = len(vals)
        score = mean(vals) if vals else 0.0
        ci = hoeffding_interval(score, n)
        wci = wilson_interval(sum(wins), n)
        out.append({
            "target": target,
            "opponent": opponent,
            "starting_life": int(life),
            "dimension": dim,
            "value": value,
            "games": n,
            "mean_score_draw_half": score,
            "score_lcb_95": ci.low,
            "score_ucb_95": ci.high,
            "terminal_win_rate": mean(wins) if wins else 0.0,
            "terminal_win_lcb_95": wci.low,
            "terminal_win_ucb_95": wci.high,
        })
    return out


def cumulative_life_cell_rows(previous_rows: Sequence[Mapping[str, Any]], new_rows: Sequence[Mapping[str, Any]], agenda_cells: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate previous dossier rows plus new life-cell reps."""

    return life_cell_summary_rows([*previous_rows, *new_rows], agenda_cells)


def life_cell_claim_gate(
    rows: Sequence[Mapping[str, Any]],
    cell_rows: Sequence[Mapping[str, Any]],
    cumulative_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    cpp_summary: Mapping[str, Any],
    min_rows: int = 240,
    min_new_cell_games: int = 120,
    min_cumulative_cell_games: int = 200,
    require_zero_truncations: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if len(rows) < int(min_rows):
        errors.append(f"raw rows {len(rows)} below min_rows {min_rows}")
    truncs = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if require_zero_truncations and truncs:
        errors.append(f"expected zero truncations, saw {truncs}")
    if int(cpp_summary.get("skipped_events", 0)) != 0:
        errors.append(f"C++ skipped events {cpp_summary.get('skipped_events')}")
    if int(cpp_summary.get("mismatches", 0)) != 0:
        errors.append(f"C++ mismatches {cpp_summary.get('mismatches')}")
    small_new = [r for r in cell_rows if _i(r, "games") < int(min_new_cell_games)]
    small_cum = [r for r in cumulative_rows if _i(r, "games") < int(min_cumulative_cell_games)]
    if small_new:
        errors.append(f"{len(small_new)} new cell rows below min_new_cell_games {min_new_cell_games}")
    if small_cum:
        errors.append(f"{len(small_cum)} cumulative cell rows below min_cumulative_cell_games {min_cumulative_cell_games}")
    claim_cells = sum(1 for r in cumulative_rows if str(r.get("cell_signal")) == "life_cell_claim_candidate")
    if claim_cells == 0:
        warnings.append("no cumulative life cell crossed the life_cell_claim_candidate threshold")
    return {
        "revision": revision,
        "passed": not errors,
        "raw_rows": len(rows),
        "new_cell_rows": len(cell_rows),
        "cumulative_cell_rows": len(cumulative_rows),
        "truncations": truncs,
        "claim_cell_count": claim_cells,
        "errors": errors,
        "warnings": warnings,
    }
