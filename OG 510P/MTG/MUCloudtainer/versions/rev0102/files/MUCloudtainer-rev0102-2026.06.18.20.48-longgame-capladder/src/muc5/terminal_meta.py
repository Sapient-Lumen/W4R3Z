from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence

from .metarank import meta_rank_from_aggregate


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


@dataclass(frozen=True)
class TerminalMetaGate:
    """Audit report for meta-rank/league tables built from payoff rows.

    Meta-rank is a useful population lens, but it should not be fed smoke rows
    that still contain max-decision draws or hidden draw-half conventions.  This
    gate is intentionally simple: it checks that every raw payoff row is
    terminal-clean, that the aggregate matrix has enough support, and that the
    rank masses look normalized.
    """

    passed: bool
    raw_rows: int
    aggregate_rows: int
    strategy_count: int
    truncation_rows: int
    terminal_clean_rows: int
    min_aggregate_games: int
    meta_mass_sum: float
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def terminal_meta_gate(
    raw_rows: Sequence[Mapping[str, Any]],
    aggregate_rows: Sequence[Mapping[str, Any]],
    meta_rows: Sequence[Mapping[str, Any]],
    *,
    min_raw_rows: int = 1,
    min_aggregate_games: int = 1,
    require_terminal_clean: bool = True,
) -> TerminalMetaGate:
    errors: list[str] = []
    warnings: list[str] = []
    trunc = 0
    clean = 0
    for idx, row in enumerate(raw_rows):
        is_trunc = _truthy(row.get("is_truncation")) or str(row.get("loss_reason", "")) == "max_decisions_reached"
        terminal_clean = _truthy(row.get("terminal_clean_game", not is_trunc)) and not is_trunc
        trunc += 1 if is_trunc else 0
        clean += 1 if terminal_clean else 0
        if require_terminal_clean and not terminal_clean:
            errors.append(f"row {idx}: non-terminal-clean row in terminal meta table")
            if len(errors) >= 8:
                errors.append("... additional non-terminal-clean rows omitted")
                break
    if len(raw_rows) < min_raw_rows:
        errors.append(f"raw_rows {len(raw_rows)} below min_raw_rows {min_raw_rows}")
    if aggregate_rows:
        min_games = min(int(float(r.get("games", 0))) for r in aggregate_rows)
        if min_games < min_aggregate_games:
            errors.append(f"min aggregate games {min_games} below {min_aggregate_games}")
    else:
        min_games = 0
        errors.append("no aggregate rows")
    strategy_count = len({str(r.get("strategy0")) for r in aggregate_rows} | {str(r.get("strategy1")) for r in aggregate_rows})
    meta_sum = sum(float(r.get("meta_rank_mass", 0.0)) for r in meta_rows if str(r.get("life_scope", "all")) == "all")
    if meta_rows and abs(meta_sum - 1.0) > 1e-6:
        errors.append(f"all-life meta-rank mass sums to {meta_sum:.12f}, not 1.0")
    if strategy_count == 0:
        errors.append("strategy_count is zero")
    if trunc:
        warnings.append(f"{trunc} truncation rows detected; meta-rank should be diagnostic only")
    if not meta_rows:
        warnings.append("no meta rows supplied")
    return TerminalMetaGate(
        passed=not errors,
        raw_rows=int(len(raw_rows)),
        aggregate_rows=int(len(aggregate_rows)),
        strategy_count=int(strategy_count),
        truncation_rows=int(trunc),
        terminal_clean_rows=int(clean),
        min_aggregate_games=int(min_games),
        meta_mass_sum=float(meta_sum),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def terminal_meta_rank_rows(
    aggregate_rows: Sequence[Mapping[str, Any]],
    *,
    life_totals: Sequence[int] = (20, 40),
    selection_strength: float = 12.0,
) -> list[dict[str, Any]]:
    """Meta-rank rows for all-life and life-specific payoff matrices."""

    out: list[dict[str, Any]] = []
    for scope, life in [("all", None)] + [(str(int(l)), int(l)) for l in life_totals]:
        rows = meta_rank_from_aggregate(aggregate_rows, life=life, selection_strength=selection_strength)
        for rank, result in enumerate(rows, 1):
            row = result.as_dict()
            row["life_scope"] = scope
            row["meta_rank"] = rank
            out.append(row)
    return out


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


def life_split_stability_rows(raw_rows: Sequence[Mapping[str, Any]], *, life_totals: Sequence[int] = (20, 40)) -> list[dict[str, Any]]:
    """Seat-symmetric score/win stability between tournament life totals."""

    strategies = sorted({str(r.get("strategy0")) for r in raw_rows} | {str(r.get("strategy1")) for r in raw_rows})
    lives = [int(x) for x in life_totals]
    out: list[dict[str, Any]] = []
    for strategy in strategies:
        row: dict[str, Any] = {"strategy": strategy}
        means: dict[int, float] = {}
        wins: dict[int, float] = {}
        games: dict[int, int] = {}
        for life in lives:
            vals = []
            win_vals = []
            for r in raw_rows:
                if int(r.get("starting_life", -1)) != life:
                    continue
                sc = _score_for_strategy(r, strategy)
                tw = _terminal_win_for_strategy(r, strategy)
                if sc is not None:
                    vals.append(sc)
                    win_vals.append(0.0 if tw is None else tw)
            means[life] = sum(vals) / len(vals) if vals else 0.0
            wins[life] = sum(win_vals) / len(win_vals) if win_vals else 0.0
            games[life] = len(vals)
            row[f"score_life{life}"] = means[life]
            row[f"terminal_win_life{life}"] = wins[life]
            row[f"games_life{life}"] = games[life]
        if len(lives) >= 2:
            lo, hi = lives[0], lives[-1]
            row["score_life_delta_hi_minus_lo"] = means[hi] - means[lo]
            row["terminal_win_delta_hi_minus_lo"] = wins[hi] - wins[lo]
            row["abs_score_life_delta"] = abs(means[hi] - means[lo])
            row["life_bias"] = "life40" if means[hi] > means[lo] + 1e-12 else ("life20" if means[lo] > means[hi] + 1e-12 else "flat")
        out.append(row)
    out.sort(key=lambda r: (r.get("abs_score_life_delta", 0.0), max(r.get("score_life20", 0.0), r.get("score_life40", 0.0))), reverse=True)
    return out


def rank_disagreement_rows(
    standings: Sequence[Mapping[str, Any]],
    stat_standings: Sequence[Mapping[str, Any]],
    meta_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compare mean-score, LCB, and all-life meta-rank orderings."""

    mean_rank = {str(r["strategy"]): int(r.get("rank", i + 1)) for i, r in enumerate(standings)}
    lcb_rank = {str(r["strategy"]): int(r.get("rank_by_lcb", i + 1)) for i, r in enumerate(stat_standings)}
    all_meta = [r for r in meta_rows if str(r.get("life_scope")) == "all"]
    meta_rank = {str(r["strategy"]): int(r.get("meta_rank", i + 1)) for i, r in enumerate(all_meta)}
    meta_mass = {str(r["strategy"]): float(r.get("meta_rank_mass", 0.0)) for r in all_meta}
    strategies = sorted(set(mean_rank) | set(lcb_rank) | set(meta_rank))
    out: list[dict[str, Any]] = []
    for strategy in strategies:
        mr = mean_rank.get(strategy)
        lr = lcb_rank.get(strategy)
        tr = meta_rank.get(strategy)
        ranks = [x for x in (mr, lr, tr) if x is not None]
        spread = max(ranks) - min(ranks) if ranks else 0
        out.append(
            {
                "strategy": strategy,
                "mean_score_rank": mr if mr is not None else "",
                "lcb_rank": lr if lr is not None else "",
                "meta_rank": tr if tr is not None else "",
                "meta_rank_mass": meta_mass.get(strategy, 0.0),
                "rank_spread": spread,
                "disagreement_label": "stable" if spread <= 1 else ("mild" if spread <= 3 else "large"),
            }
        )
    out.sort(key=lambda r: (r["rank_spread"], r["meta_rank_mass"]), reverse=True)
    return out


def claim_ledger_rows(
    standings: Sequence[Mapping[str, Any]],
    stat_standings: Sequence[Mapping[str, Any]],
    meta_rows: Sequence[Mapping[str, Any]],
    life_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compact row per strategy for terminal-clean league summaries.

    This is a human-facing ledger: it says what can be claimed, what is merely a
    signal, and where more games should be spent next.
    """

    by_mean = {str(r["strategy"]): r for r in standings}
    by_lcb = {str(r["strategy"]): r for r in stat_standings}
    by_life = {str(r["strategy"]): r for r in life_rows}
    all_meta = {str(r["strategy"]): r for r in meta_rows if str(r.get("life_scope")) == "all"}
    strategies = sorted(set(by_mean) | set(by_lcb) | set(all_meta) | set(by_life))
    out: list[dict[str, Any]] = []
    for strategy in strategies:
        mean_row = by_mean.get(strategy, {})
        lcb_row = by_lcb.get(strategy, {})
        meta_row = all_meta.get(strategy, {})
        life_row = by_life.get(strategy, {})
        claim_ready = _truthy(lcb_row.get("claim_ready"))
        mean_score = float(mean_row.get("mean_score_draw_half", lcb_row.get("mean_score_draw_half", 0.0)))
        lcb = float(lcb_row.get("score_lcb_95", 0.0))
        mass = float(meta_row.get("meta_rank_mass", 0.0))
        abs_delta = float(life_row.get("abs_score_life_delta", 0.0))
        if not claim_ready:
            label = "needs_more_games"
        elif mean_score >= 0.60 and lcb >= 0.50 and mass >= 0.10:
            label = "robust_candidate"
        elif abs_delta >= 0.15:
            label = "life_sensitive_candidate"
        elif mass >= 0.10:
            label = "population_candidate"
        else:
            label = "terminal_clean_signal_only"
        out.append(
            {
                "strategy": strategy,
                "claim_label": label,
                "claim_ready": bool(claim_ready),
                "mean_score_draw_half": mean_score,
                "score_lcb_95": lcb,
                "meta_rank_mass": mass,
                "meta_rank": meta_row.get("meta_rank", ""),
                "life_bias": life_row.get("life_bias", ""),
                "abs_score_life_delta": abs_delta,
                "games": int(lcb_row.get("games", mean_row.get("games", 0)) or 0),
                "next_eval_hint": "deeper_terminal_clean_payoff" if not claim_ready else ("life_split_reps" if abs_delta >= 0.15 else "meta_pair_reps"),
            }
        )
    out.sort(key=lambda r: (r["claim_ready"], r["meta_rank_mass"], r["score_lcb_95"], r["mean_score_draw_half"]), reverse=True)
    return out
