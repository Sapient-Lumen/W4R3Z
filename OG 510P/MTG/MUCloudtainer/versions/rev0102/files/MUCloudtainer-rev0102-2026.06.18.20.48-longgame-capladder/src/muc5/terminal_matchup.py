from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .payoff import StrategyBundle
from .statgate import hoeffding_interval, wilson_interval


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _score_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_score", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_score", 0.0))
    return None


def _terminal_win_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_terminal_win", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_terminal_win", 0.0))
    return None


def life_flip_matchups_from_target_pairs(
    pair_rows: Sequence[Mapping[str, Any]],
    *,
    top_n: int = 4,
    life_low: int = 20,
    life_high: int = 40,
    exclude_self: bool = True,
) -> list[dict[str, Any]]:
    """Select target/opponent cells whose previous score changed most by life total.

    The rev0051 target-pair table is intentionally low-sample.  This helper
    treats it as an agenda generator, not as a truth source: select the biggest
    apparent life splits, then spend a new terminal-clean panel on those cells.
    """

    grouped: dict[tuple[str, str], dict[int, Mapping[str, Any]]] = defaultdict(dict)
    for row in pair_rows:
        target = str(row.get("target"))
        opponent = str(row.get("opponent"))
        if exclude_self and target == opponent:
            continue
        try:
            life = int(row.get("starting_life"))
        except Exception:
            continue
        grouped[(target, opponent)][life] = row

    out: list[dict[str, Any]] = []
    for (target, opponent), by_life in grouped.items():
        if life_low not in by_life or life_high not in by_life:
            continue
        low_row = by_life[life_low]
        high_row = by_life[life_high]
        low_score = float(low_row.get("mean_score_draw_half", 0.0))
        high_score = float(high_row.get("mean_score_draw_half", 0.0))
        delta = high_score - low_score
        out.append(
            {
                "target": target,
                "opponent": opponent,
                "previous_games_life_low": int(float(low_row.get("games", 0))),
                "previous_games_life_high": int(float(high_row.get("games", 0))),
                "previous_score_life_low": low_score,
                "previous_score_life_high": high_score,
                "previous_life_delta_high_minus_low": delta,
                "previous_abs_life_delta": abs(delta),
                "previous_life_bias": "life40" if delta > 1e-12 else ("life20" if delta < -1e-12 else "flat"),
            }
        )
    out.sort(key=lambda r: (r["previous_abs_life_delta"], max(r["previous_score_life_low"], r["previous_score_life_high"])), reverse=True)
    for i, row in enumerate(out, 1):
        row["previous_life_split_rank"] = i
    return out[: int(top_n)]


def focused_life_matchup_specs(
    strategies: Sequence[StrategyBundle],
    matchups: Sequence[Mapping[str, Any]],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 8,
    base_seed: int = 5200000,
    max_decisions: int = 900,
) -> tuple[CppShadowGameSpec, ...]:
    """Build a target/opponent schedule for life-split retests.

    For each target/opponent cell, the target is seated as p0 and p1 for every
    life total.  Scores are later aggregated from the target's perspective.
    """

    by_id = {s.strategy_id: s for s in strategies}
    specs: list[CppShadowGameSpec] = []
    k = 0
    seen_specs: set[tuple[str, str, int, int, int]] = set()
    for matchup_index, row in enumerate(matchups):
        target_id = str(row.get("target"))
        opponent_id = str(row.get("opponent"))
        if target_id not in by_id or opponent_id not in by_id:
            continue
        target = by_id[target_id]
        opponent = by_id[opponent_id]
        for life in map(int, life_totals):
            for target_seat in (0, 1):
                left, right = (target, opponent) if target_seat == 0 else (opponent, target)
                for starting_player in (0, 1):
                    for rep in range(int(reps)):
                        # The tuple includes matchup index so mirrored target/opponent agendas can intentionally
                        # rerun the same physical pairing under different target-perspective labels.
                        key = (matchup_index, target_seat, int(life), int(starting_player), int(rep))
                        if key in seen_specs:
                            continue
                        seen_specs.add(key)
                        specs.append(
                            CppShadowGameSpec(
                                game_id=f"g{k:05d}_m{matchup_index:02d}_{target_id}_vs_{opponent_id}_life{int(life)}_seat{target_seat}_sp{starting_player}_r{rep}",
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


def annotate_life_matchup_rows(rows: Sequence[Mapping[str, Any]], matchups: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Add target/opponent focus metadata to game rows by parsing C++ game ids."""

    out: list[dict[str, Any]] = []
    for row in rows:
        r = dict(row)
        gid = str(r.get("cpp_shadow_game_id", ""))
        # game_id format: g00000_m00_target_vs_opponent_life20_...
        parts = gid.split("_")
        matchup_index = None
        if len(parts) >= 2 and parts[1].startswith("m"):
            try:
                matchup_index = int(parts[1][1:])
            except ValueError:
                matchup_index = None
        if matchup_index is not None and 0 <= matchup_index < len(matchups):
            target = str(matchups[matchup_index].get("target"))
            opponent = str(matchups[matchup_index].get("opponent"))
            r["focus_matchup_index"] = matchup_index
            r["focus_target"] = target
            r["focus_opponent"] = opponent
            r["focus_target_seat"] = 0 if str(r.get("strategy0")) == target else (1 if str(r.get("strategy1")) == target else "")
            sc = _score_for_strategy(r, target)
            tw = _terminal_win_for_strategy(r, target)
            r["focus_target_score"] = "" if sc is None else sc
            r["focus_target_terminal_win"] = "" if tw is None else tw
        else:
            r["focus_matchup_index"] = ""
            r["focus_target"] = ""
            r["focus_opponent"] = ""
            r["focus_target_seat"] = ""
            r["focus_target_score"] = ""
            r["focus_target_terminal_win"] = ""
        out.append(r)
    return out


def target_life_cell_rows(rows: Sequence[Mapping[str, Any]], matchups: Sequence[Mapping[str, Any]], *, life_totals: Sequence[int] = (20, 40)) -> list[dict[str, Any]]:
    buckets: dict[tuple[int, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        try:
            idx = int(row.get("focus_matchup_index"))
        except Exception:
            continue
        target = str(row.get("focus_target"))
        opponent = str(row.get("focus_opponent"))
        if not target or not opponent:
            continue
        life = int(row.get("starting_life", 0))
        buckets[(idx, target, opponent, life)].append(row)

    out: list[dict[str, Any]] = []
    previous_by_key = {(int(i), int(life)): m for i, m in enumerate(matchups) for life in map(int, life_totals)}
    for (idx, target, opponent, life), group in sorted(buckets.items()):
        vals = [float(r.get("focus_target_score", 0.0)) for r in group]
        wins = [float(r.get("focus_target_terminal_win", 0.0)) for r in group]
        n = len(vals)
        score = mean(vals) if vals else 0.0
        ci = hoeffding_interval(score, n)
        wci = wilson_interval(sum(wins), n)
        prev = matchups[idx] if 0 <= idx < len(matchups) else {}
        prev_score = prev.get("previous_score_life_low") if int(life) == int(life_totals[0]) else prev.get("previous_score_life_high")
        out.append(
            {
                "matchup_index": idx,
                "target": target,
                "opponent": opponent,
                "starting_life": int(life),
                "games": n,
                "mean_score_draw_half": score,
                "score_lcb_95": ci.low,
                "score_ucb_95": ci.high,
                "terminal_win_rate": mean(wins) if wins else 0.0,
                "terminal_win_lcb_95": wci.low,
                "previous_mean_score_draw_half": "" if prev_score is None else float(prev_score),
                "score_shift_vs_previous": "" if prev_score is None else score - float(prev_score),
                "cell_signal": "favored" if ci.low > 0.5 else ("unfavored" if ci.high < 0.5 else "uncertain"),
            }
        )
    out.sort(key=lambda r: (r["matchup_index"], r["starting_life"]))
    return out


def life_flip_retest_rows(cell_rows: Sequence[Mapping[str, Any]], previous_matchups: Sequence[Mapping[str, Any]], *, life_low: int = 20, life_high: int = 40) -> list[dict[str, Any]]:
    by_key: dict[tuple[int, str, str], dict[int, Mapping[str, Any]]] = defaultdict(dict)
    for row in cell_rows:
        by_key[(int(row.get("matchup_index")), str(row.get("target")), str(row.get("opponent")))][int(row.get("starting_life"))] = row

    out: list[dict[str, Any]] = []
    for (idx, target, opponent), by_life in sorted(by_key.items()):
        if life_low not in by_life or life_high not in by_life:
            continue
        lo = by_life[life_low]
        hi = by_life[life_high]
        score_lo = float(lo.get("mean_score_draw_half", 0.0))
        score_hi = float(hi.get("mean_score_draw_half", 0.0))
        delta = score_hi - score_lo
        prev = previous_matchups[idx] if 0 <= idx < len(previous_matchups) else {}
        prev_delta = float(prev.get("previous_life_delta_high_minus_low", 0.0)) if prev else 0.0
        games = int(lo.get("games", 0)) + int(hi.get("games", 0))
        row = {
            "matchup_index": idx,
            "target": target,
            "opponent": opponent,
            "games": games,
            f"score_life{life_low}": score_lo,
            f"score_life{life_high}": score_hi,
            "life_delta_high_minus_low": delta,
            "abs_life_delta": abs(delta),
            "life_bias": "life40" if delta > 1e-12 else ("life20" if delta < -1e-12 else "flat"),
            "previous_life_delta_high_minus_low": prev_delta,
            "previous_abs_life_delta": abs(prev_delta),
            "delta_shift_vs_previous": delta - prev_delta,
            "same_delta_sign_as_previous": (delta == 0.0 and prev_delta == 0.0) or (delta > 0 and prev_delta > 0) or (delta < 0 and prev_delta < 0),
            "life_flip_label": _life_flip_label(delta, prev_delta, games),
        }
        out.append(row)
    out.sort(key=lambda r: (r["abs_life_delta"], r["games"]), reverse=True)
    return out


def _life_flip_label(delta: float, prev_delta: float, games: int) -> str:
    if games < 32:
        return "needs_more_games"
    if abs(delta) >= 0.25 and ((delta > 0 and prev_delta > 0) or (delta < 0 and prev_delta < 0)):
        return "confirmed_life_split_signal"
    if abs(delta) >= 0.20:
        return "new_or_changed_life_split_signal"
    if abs(prev_delta) >= 0.25 and abs(delta) < 0.15:
        return "previous_life_split_softened"
    return "watchlist"


@dataclass(frozen=True)
class LifeFlipGate:
    passed: bool
    revision: str
    rows: int
    matchups: int
    truncations: int
    cpp_mismatches: int
    cpp_skipped: int
    min_cell_games: int
    confirmed_or_changed_signals: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def life_flip_gate(
    rows: Sequence[Mapping[str, Any]],
    cell_rows: Sequence[Mapping[str, Any]],
    flip_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    cpp_summary: Mapping[str, Any] | None = None,
    min_rows: int = 128,
    min_cell_games: int = 16,
) -> LifeFlipGate:
    errors: list[str] = []
    warnings: list[str] = []
    if len(rows) < min_rows:
        errors.append(f"raw_rows {len(rows)} below min_rows {min_rows}")
    truncations = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if truncations:
        errors.append(f"{truncations} truncation rows in life-flip panel")
    small_cells = [r for r in cell_rows if int(r.get("games", 0)) < min_cell_games]
    if small_cells:
        errors.append(f"{len(small_cells)} target/life cells below min_cell_games {min_cell_games}")
    cpp_mismatches = int((cpp_summary or {}).get("mismatches", 0))
    cpp_skipped = int((cpp_summary or {}).get("skipped_events", 0))
    if cpp_mismatches:
        errors.append(f"C++ shadow mismatches: {cpp_mismatches}")
    if cpp_skipped:
        errors.append(f"C++ skipped events: {cpp_skipped}")
    signal_count = sum(1 for r in flip_rows if str(r.get("life_flip_label")) in {"confirmed_life_split_signal", "new_or_changed_life_split_signal"})
    if signal_count == 0:
        warnings.append("no confirmed/changed life-split signals in this retest")
    return LifeFlipGate(
        passed=not errors,
        revision=str(revision),
        rows=len(rows),
        matchups=len(flip_rows),
        truncations=truncations,
        cpp_mismatches=cpp_mismatches,
        cpp_skipped=cpp_skipped,
        min_cell_games=min((int(r.get("games", 0)) for r in cell_rows), default=0),
        confirmed_or_changed_signals=signal_count,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
