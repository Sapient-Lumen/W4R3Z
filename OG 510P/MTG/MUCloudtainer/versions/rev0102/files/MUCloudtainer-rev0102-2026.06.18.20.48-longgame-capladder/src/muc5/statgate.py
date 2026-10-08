from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class Interval:
    low: float
    center: float
    high: float
    n: int
    method: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def wilson_interval(successes: float, n: int, z: float = 1.96) -> Interval:
    """Wilson score interval for a binomial proportion.

    ``successes`` is rounded only by the caller convention. The mathematically
    strict use is integer successes from Bernoulli trials; MUC-5 uses this for
    terminal wins. Draw-half scores should use ``hoeffding_interval`` instead.
    """

    if n <= 0:
        return Interval(0.0, 0.0, 1.0, 0, "wilson")
    p = max(0.0, min(1.0, float(successes) / n))
    denom = 1.0 + (z * z) / n
    centre = (p + (z * z) / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n))
    return Interval(max(0.0, centre - half), centre, min(1.0, centre + half), n, "wilson")


def hoeffding_interval(mean_score: float, n: int, alpha: float = 0.05) -> Interval:
    """Distribution-free confidence interval for bounded [0, 1] rewards.

    This is conservative, but it is safe for draw-half payoff rows because those
    are bounded rewards rather than pure Bernoulli wins.
    """

    if n <= 0:
        return Interval(0.0, 0.0, 1.0, 0, "hoeffding")
    center = max(0.0, min(1.0, float(mean_score)))
    half = math.sqrt(math.log(2.0 / alpha) / (2.0 * n))
    return Interval(max(0.0, center - half), center, min(1.0, center + half), n, "hoeffding")


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _row_score_for_strategy(row: Mapping[str, Any], strategy: str) -> float:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_score", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_score", 0.0))
    raise KeyError(f"strategy {strategy!r} not in row")


def _row_terminal_win_for_strategy(row: Mapping[str, Any], strategy: str) -> float:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_terminal_win", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_terminal_win", 0.0))
    raise KeyError(f"strategy {strategy!r} not in row")


def statistical_standings(
    rows: Sequence[Mapping[str, Any]],
    *,
    alpha: float = 0.05,
    min_games_for_claim: int = 30,
) -> List[Dict[str, Any]]:
    """Standings with uncertainty labels.

    The ranking key is lower confidence bound of the draw-half score, not raw
    mean. That is intentionally conservative for tiny smoke tables.
    """

    scores: Dict[str, List[float]] = defaultdict(list)
    wins: Dict[str, float] = defaultdict(float)
    truncs: Dict[str, int] = defaultdict(int)
    terminal_games: Dict[str, int] = defaultdict(int)
    lives: Dict[str, set[int]] = defaultdict(set)
    agents: Dict[str, set[str]] = defaultdict(set)
    decks: Dict[str, set[str]] = defaultdict(set)
    for row in rows:
        for side in (0, 1):
            s = str(row[f"strategy{side}"])
            scores[s].append(float(row[f"p{side}_score"]))
            wins[s] += float(row.get(f"p{side}_terminal_win", 0.0))
            if not _truthy(row.get("is_nonterminal_draw")):
                terminal_games[s] += 1
            if _truthy(row.get("is_truncation")):
                truncs[s] += 1
            lives[s].add(int(row.get("starting_life", 0)))
            agents[s].add(str(row.get(f"agent{side}", "")))
            decks[s].add(str(row.get(f"deck{side}", "")))

    out: List[Dict[str, Any]] = []
    for strategy, vals in scores.items():
        n = len(vals)
        mean_score = mean(vals) if vals else 0.0
        score_ci = hoeffding_interval(mean_score, n, alpha=alpha)
        win_ci = wilson_interval(wins[strategy], n, z=1.96)
        out.append(
            {
                "strategy": strategy,
                "games": n,
                "mean_score_draw_half": mean_score,
                "score_lcb_95": score_ci.low,
                "score_ucb_95": score_ci.high,
                "terminal_win_rate": wins[strategy] / n if n else 0.0,
                "terminal_win_lcb_95": win_ci.low,
                "terminal_win_ucb_95": win_ci.high,
                "truncation_rate": truncs[strategy] / n if n else 0.0,
                "terminal_game_rate": terminal_games[strategy] / n if n else 0.0,
                "claim_ready": n >= min_games_for_claim and truncs[strategy] == 0,
                "life_totals_seen": ";".join(map(str, sorted(lives[strategy]))),
                "agents": ";".join(sorted(a for a in agents[strategy] if a)),
                "decks": ";".join(sorted(d for d in decks[strategy] if d)),
            }
        )
    out.sort(key=lambda r: (r["score_lcb_95"], r["mean_score_draw_half"], r["terminal_win_lcb_95"]), reverse=True)
    for i, row in enumerate(out, 1):
        row["rank_by_lcb"] = i
    return out


def pairwise_stat_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    alpha: float = 0.05,
    min_games_for_claim: int = 8,
) -> List[Dict[str, Any]]:
    """Pair/life-level uncertainty rows from raw payoff games."""

    buckets: Dict[Tuple[str, str, int], List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[(str(row["strategy0"]), str(row["strategy1"]), int(row["starting_life"]))].append(row)

    out: List[Dict[str, Any]] = []
    for (s0, s1, life), group in sorted(buckets.items()):
        n = len(group)
        mean_score = sum(float(r["p0_score"]) for r in group) / n if n else 0.0
        terminal_wins = sum(float(r.get("p0_terminal_win", 0.0)) for r in group)
        truncs = sum(1 for r in group if _truthy(r.get("is_truncation")))
        score_ci = hoeffding_interval(mean_score, n, alpha=alpha)
        win_ci = wilson_interval(terminal_wins, n)
        if score_ci.low > 0.5:
            label = "p0_favored"
        elif score_ci.high < 0.5:
            label = "p1_favored"
        else:
            label = "uncertain"
        out.append(
            {
                "strategy0": s0,
                "strategy1": s1,
                "starting_life": life,
                "games": n,
                "p0_mean_score_draw_half": mean_score,
                "p0_score_lcb_95": score_ci.low,
                "p0_score_ucb_95": score_ci.high,
                "p0_terminal_win_rate": terminal_wins / n if n else 0.0,
                "p0_terminal_win_lcb_95": win_ci.low,
                "p0_terminal_win_ucb_95": win_ci.high,
                "truncation_rate": truncs / n if n else 0.0,
                "claim_label": label,
                "claim_ready": n >= min_games_for_claim and truncs == 0 and label != "uncertain",
            }
        )
    return out


@dataclass(frozen=True)
class StatisticalGateReport:
    passed: bool
    row_count: int
    strategy_count: int
    pair_count: int
    claim_ready_strategy_count: int
    claim_ready_pair_count: int
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def audit_statistical_gate(
    rows: Sequence[Mapping[str, Any]],
    standings: Sequence[Mapping[str, Any]],
    pair_rows: Sequence[Mapping[str, Any]],
    *,
    min_raw_rows: int = 1,
    max_truncation_rate: float = 0.10,
) -> StatisticalGateReport:
    errors: List[str] = []
    warnings: List[str] = []
    row_count = len(rows)
    if row_count < min_raw_rows:
        errors.append(f"row_count {row_count} below min_raw_rows {min_raw_rows}")
    if rows:
        truncs = sum(1 for r in rows if _truthy(r.get("is_truncation")))
        trunc_rate = truncs / len(rows)
        if trunc_rate > max_truncation_rate:
            errors.append(f"truncation_rate {trunc_rate:.3f} exceeds {max_truncation_rate:.3f}")
        elif trunc_rate:
            warnings.append(f"truncation_rate {trunc_rate:.3f}; treat draw-half scores as reporting only")
    if standings:
        prev = float("inf")
        for i, row in enumerate(standings):
            cur = float(row.get("score_lcb_95", 0.0))
            if cur > prev + 1e-12:
                errors.append(f"standings row {i} not sorted by score_lcb_95")
            prev = cur
    strategy_count = len(standings)
    pair_count = len(pair_rows)
    ready_strats = sum(1 for r in standings if _truthy(r.get("claim_ready")))
    ready_pairs = sum(1 for r in pair_rows if _truthy(r.get("claim_ready")))
    if ready_strats == 0:
        warnings.append("no strategy has enough clean samples for a claim-ready standing")
    if ready_pairs == 0:
        warnings.append("no pair/life cell has enough clean samples for a claim-ready matchup claim")
    return StatisticalGateReport(
        passed=not errors,
        row_count=row_count,
        strategy_count=strategy_count,
        pair_count=pair_count,
        claim_ready_strategy_count=ready_strats,
        claim_ready_pair_count=ready_pairs,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def read_csv_rows(path: str | Path) -> List[Dict[str, str]]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))
