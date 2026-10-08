from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class MetaRankResult:
    strategy: str
    meta_rank_mass: float
    mean_row_score: float
    mean_pair_advantage: float
    support_games_min: int
    life_scope: str
    selection_strength: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def payoff_matrix_from_aggregate(
    rows: Sequence[Mapping[str, object]],
    *,
    life: int | None = None,
    score_col: str = "p0_mean_score_draw_half",
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Build row-player payoff and support matrices from aggregate payoff rows.

    ``matrix[i, j]`` is the expected draw-half score for strategy i seated as
    player 0 against strategy j seated as player 1. Missing cells are filled by
    antisymmetry when the reverse cell exists, then by 0.5 as an explicit
    unknown/neutral default. This is a ranking adapter, not a claim generator;
    statistical gates should still sit upstream.
    """

    filtered = [r for r in rows if life is None or int(r.get("starting_life", -1)) == int(life)]
    strategies = sorted({str(r["strategy0"]) for r in filtered} | {str(r["strategy1"]) for r in filtered})
    idx = {s: i for i, s in enumerate(strategies)}
    n = len(strategies)
    sums = np.zeros((n, n), dtype=np.float64)
    counts = np.zeros((n, n), dtype=np.float64)
    games = np.zeros((n, n), dtype=np.int64)
    for row in filtered:
        i = idx[str(row["strategy0"])]
        j = idx[str(row["strategy1"])]
        score = float(row.get(score_col, row.get("p0_score", 0.5)))
        g = int(float(row.get("games", 1)))
        sums[i, j] += score * max(1, g)
        counts[i, j] += max(1, g)
        games[i, j] += max(1, g)
    matrix = np.full((n, n), 0.5, dtype=np.float64)
    mask = counts > 0
    matrix[mask] = sums[mask] / counts[mask]
    for i in range(n):
        for j in range(n):
            if i == j and not mask[i, j]:
                matrix[i, j] = 0.5
            elif not mask[i, j] and mask[j, i]:
                matrix[i, j] = 1.0 - matrix[j, i]
    return strategies, matrix, games


def stationary_distribution(transition: np.ndarray, *, tol: float = 1e-12, max_iter: int = 10000) -> np.ndarray:
    n = transition.shape[0]
    if n == 0:
        return np.array([], dtype=np.float64)
    dist = np.full(n, 1.0 / n, dtype=np.float64)
    for _ in range(max_iter):
        nxt = dist @ transition
        if np.max(np.abs(nxt - dist)) < tol:
            return nxt / max(1e-300, float(np.sum(nxt)))
        dist = nxt
    return dist / max(1e-300, float(np.sum(dist)))


def meta_rank_from_matrix(
    strategies: Sequence[str],
    matrix: np.ndarray,
    support_games: np.ndarray | None = None,
    *,
    selection_strength: float = 12.0,
    mutation_floor: float = 1e-3,
    life_scope: str = "all",
) -> list[MetaRankResult]:
    """Compute a small-game meta-rank via pairwise replacement dynamics.

    This is an Alpha-Rank-inspired adapter, not a full OpenSpiel Alpha-Rank
    implementation. A transition from resident i to challenger j is more likely
    when j performs better against i than i performs against j. The stationary
    distribution is useful for seeing cycles or robust population mass, while
    upstream promotion/statistical gates decide whether the table is claimable.
    """

    n = len(strategies)
    if n == 0:
        return []
    trans = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        weights = []
        js = []
        for j in range(n):
            if i == j:
                continue
            diff = float(matrix[j, i] - matrix[i, j])
            # Stable logistic replacement weight, plus a tiny mutation floor so
            # the chain stays ergodic for smoke tables with exact ties.
            z = max(-60.0, min(60.0, selection_strength * diff))
            w = mutation_floor + 1.0 / (1.0 + math.exp(-z))
            weights.append(w)
            js.append(j)
        total = sum(weights)
        if total <= 0:
            trans[i, i] = 1.0
        else:
            leave = min(0.95, total / (total + n))
            trans[i, i] = 1.0 - leave
            for j, w in zip(js, weights):
                trans[i, j] = leave * w / total
    mass = stationary_distribution(trans)
    support = support_games if support_games is not None else np.zeros_like(matrix, dtype=np.int64)
    results: list[MetaRankResult] = []
    for i, s in enumerate(strategies):
        opp = [j for j in range(n) if j != i]
        mean_row = float(np.mean(matrix[i, opp])) if opp else 0.5
        advs = [float(matrix[i, j] - matrix[j, i]) for j in opp]
        mean_adv = float(np.mean(advs)) if advs else 0.0
        positive_support = support[i, :][support[i, :] > 0]
        min_support = int(np.min(positive_support)) if positive_support.size else 0
        results.append(
            MetaRankResult(
                strategy=s,
                meta_rank_mass=float(mass[i]),
                mean_row_score=mean_row,
                mean_pair_advantage=mean_adv,
                support_games_min=min_support,
                life_scope=life_scope,
                selection_strength=float(selection_strength),
            )
        )
    results.sort(key=lambda r: (r.meta_rank_mass, r.mean_pair_advantage, r.mean_row_score), reverse=True)
    return results


def meta_rank_from_aggregate(
    rows: Sequence[Mapping[str, object]],
    *,
    life: int | None = None,
    selection_strength: float = 12.0,
) -> list[MetaRankResult]:
    strategies, matrix, support = payoff_matrix_from_aggregate(rows, life=life)
    return meta_rank_from_matrix(
        strategies,
        matrix,
        support,
        selection_strength=selection_strength,
        life_scope="all" if life is None else str(life),
    )
