#!/usr/bin/env python3
"""
FadeMem hierarchy toy probe for CloudtainerML.

This is not a reproduction of FadeMem. It is a cheap falsifier for the
multiscale-memory claim: under a fixed cache budget, dense-near / sparse-far
summaries should preserve recent fine detail while keeping old coarse anchors.

The synthetic stream has three subspaces:
  coarse: persistent scene/identity component
  mid: slowly drifting component
  fine: fast-changing local detail
plus optional rare early anchor spikes. Policies turn a long history into a
small set of intervals. Each interval stores the mean representation and the
attention mass covered by that interval; missing intervals have zero mass.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np

EPS = 1e-12


@dataclass(frozen=True)
class Interval:
    start: int
    end: int  # exclusive
    label: str

    @property
    def width(self) -> int:
        return self.end - self.start


def l2_normalize(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + EPS)


def generate_stream(seed: int, tokens: int, dims: int, anchor_strength: float) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    assert dims % 4 == 0, "dims should be divisible by 4"
    cdim = dims // 4
    mdim = dims // 4
    fdim = dims - cdim - mdim

    coarse_basis = l2_normalize(rng.normal(size=(4, cdim)), axis=1)
    scene_ids = np.zeros(tokens, dtype=np.int64)
    # Few long segments with stable identity. Boundaries jitter by seed.
    boundaries = [0]
    cursor = 0
    while cursor < tokens:
        step = int(rng.integers(max(16, tokens // 8), max(24, tokens // 3)))
        cursor = min(tokens, cursor + step)
        boundaries.append(cursor)
    for i, (s, e) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        scene_ids[s:e] = i % len(coarse_basis)
    coarse = coarse_basis[scene_ids] + 0.03 * rng.normal(size=(tokens, cdim))

    mid = np.zeros((tokens, mdim))
    mid[0] = rng.normal(size=mdim)
    for t in range(1, tokens):
        mid[t] = 0.965 * mid[t - 1] + 0.18 * rng.normal(size=mdim)
    mid = l2_normalize(mid, axis=1)

    fine = np.zeros((tokens, fdim))
    fine[0] = rng.normal(size=fdim)
    for t in range(1, tokens):
        fine[t] = 0.18 * fine[t - 1] + 0.98 * rng.normal(size=fdim)
    fine = l2_normalize(fine, axis=1)

    X = np.concatenate([coarse, mid, fine], axis=1).astype(np.float64)
    X = l2_normalize(X, axis=1)

    # Rare early anchors: old details that are semantically important even if distant.
    anchor_times = sorted(set([max(1, tokens // 11), max(2, tokens // 5)]))
    anchor_vec = np.zeros(dims, dtype=np.float64)
    # Put anchor energy mostly in fine dims so mean consolidation can dilute it.
    anchor_vec[-fdim:] = l2_normalize(rng.normal(size=fdim)) * anchor_strength
    for t in anchor_times:
        X[t] = l2_normalize(X[t] + anchor_vec)

    masks = {
        "coarse": np.r_[np.ones(cdim), np.zeros(mdim + fdim)].astype(bool),
        "mid": np.r_[np.zeros(cdim), np.ones(mdim), np.zeros(fdim)].astype(bool),
        "fine": np.r_[np.zeros(cdim + mdim), np.ones(fdim)].astype(bool),
        "all": np.ones(dims, dtype=bool),
    }
    return {"X": X, "anchor_times": np.array(anchor_times), "masks": masks}


def weights_for_regime(regime: str, tokens: int, anchor_times: np.ndarray) -> np.ndarray:
    idx = np.arange(tokens)
    age = (tokens - 1) - idx
    if regime == "coarse_global":
        # Long-range low-frequency context: almost uniform with slight recency.
        w = 0.7 * np.ones(tokens) / tokens + 0.3 * np.exp(-age / max(1.0, tokens / 3))
    elif regime == "fine_recent":
        w = np.exp(-age / max(1.0, tokens / 24))
    elif regime == "mixed_multiscale":
        w = 0.45 * np.ones(tokens) / tokens + 0.55 * np.exp(-age / max(1.0, tokens / 10))
    elif regime == "old_anchor_pin":
        center = int(anchor_times[0]) if len(anchor_times) else max(1, tokens // 10)
        sigma = max(1.0, tokens / 80)
        w = 0.12 * np.exp(-age / max(1.0, tokens / 8)) + 0.88 * np.exp(-0.5 * ((idx - center) / sigma) ** 2)
    elif regime == "two_anchor_recall":
        w = 0.05 * np.exp(-age / max(1.0, tokens / 12))
        sigma = max(1.0, tokens / 85)
        for center in anchor_times:
            w += 0.475 * np.exp(-0.5 * ((idx - int(center)) / sigma) ** 2)
    else:
        raise ValueError(f"unknown regime: {regime}")
    w = np.maximum(w, 0)
    return w / (w.sum() + EPS)


def full_intervals(tokens: int, budget: int) -> List[Interval]:
    return [Interval(i, i + 1, "singleton") for i in range(tokens)]


def sliding_window(tokens: int, budget: int) -> List[Interval]:
    start = max(0, tokens - budget)
    return [Interval(i, i + 1, "recent") for i in range(start, tokens)]


def first_plus_recent(tokens: int, budget: int) -> List[Interval]:
    if budget <= 1:
        return [Interval(0, 1, "first")]
    recent_n = min(tokens - 1, budget - 1)
    start = max(1, tokens - recent_n)
    intervals = [Interval(0, 1, "first")]
    intervals.extend(Interval(i, i + 1, "recent") for i in range(start, tokens))
    return intervals[:budget]


def uniform_blocks(tokens: int, budget: int) -> List[Interval]:
    edges = np.linspace(0, tokens, num=budget + 1)
    ints = []
    last = 0
    for i in range(budget):
        s = int(round(edges[i]))
        e = int(round(edges[i + 1]))
        s = max(last, min(tokens - 1, s))
        e = max(s + 1, min(tokens, e))
        ints.append(Interval(s, e, "uniform_block"))
        last = e
    return ints


def fademem_power(tokens: int, budget: int, exponent: float = 2.2, anchor: bool = False) -> List[Interval]:
    # Age 0 is newest. Polynomial spacing gives narrow bins near the present and
    # wider bins in the distant past. Intervals partition the full history.
    if budget <= 0:
        return []
    reserve = 1 if anchor and budget > 1 else 0
    bins = budget - reserve
    max_age = tokens
    age_edges = np.unique(np.round((np.linspace(0.0, 1.0, bins + 1) ** exponent) * max_age).astype(int))
    age_edges[0] = 0
    if age_edges[-1] != max_age:
        age_edges = np.r_[age_edges, max_age]
    # If rounding collapsed bins, fill by uniform fallback.
    if len(age_edges) - 1 < bins:
        age_edges = np.unique(np.round(np.linspace(0, max_age, bins + 1)).astype(int))
    intervals: List[Interval] = []
    for a0, a1 in zip(age_edges[:-1], age_edges[1:]):
        if a1 <= a0:
            continue
        # Convert age interval [a0,a1) from recent to time interval [tokens-a1, tokens-a0)
        s = max(0, tokens - int(a1))
        e = min(tokens, tokens - int(a0))
        if s < e:
            intervals.append(Interval(s, e, "fademem_block"))
    intervals = sorted(intervals, key=lambda x: x.start)
    if anchor:
        # Split first token out as a global anchor; adjust/skip overlapping first block.
        anchored = [Interval(0, 1, "first_anchor")]
        for it in intervals:
            s, e = it.start, it.end
            if e <= 1:
                continue
            if s == 0:
                s = 1
            if s < e:
                anchored.append(Interval(s, e, it.label))
        intervals = anchored
    # Merge or trim to exact-ish budget if rounding made too many bins.
    while len(intervals) > budget:
        # Merge the two oldest non-anchor intervals.
        best = None
        for i in range(len(intervals) - 1):
            if intervals[i].label == "first_anchor":
                continue
            best = i
            break
        if best is None:
            intervals = intervals[:budget]
            break
        a, b = intervals[best], intervals[best + 1]
        intervals[best:best + 2] = [Interval(a.start, b.end, "merged_trim")]
    return intervals


def oracle_anchor_recent(tokens: int, budget: int, anchor_times: np.ndarray) -> List[Interval]:
    chosen = set(int(x) for x in anchor_times[: max(0, budget // 4)])
    recent_budget = max(0, budget - len(chosen))
    chosen.update(range(max(0, tokens - recent_budget), tokens))
    return [Interval(i, i + 1, "oracle_anchor_or_recent") for i in sorted(chosen)][:budget]


POLICIES: Dict[str, Callable[[int, int, np.ndarray], List[Interval]]] = {
    "full_cache": lambda t, b, a: full_intervals(t, b),
    "sliding_window": lambda t, b, a: sliding_window(t, b),
    "first_plus_recent": lambda t, b, a: first_plus_recent(t, b),
    "uniform_blocks": lambda t, b, a: uniform_blocks(t, b),
    "fademem_power": lambda t, b, a: fademem_power(t, b, exponent=2.2, anchor=False),
    "fademem_anchor_power": lambda t, b, a: fademem_power(t, b, exponent=2.2, anchor=True),
    "oracle_anchor_recent": lambda t, b, a: oracle_anchor_recent(t, b, a),
}


def approximate_output(X: np.ndarray, weights: np.ndarray, intervals: List[Interval]) -> Tuple[np.ndarray, float, float]:
    out = np.zeros(X.shape[1], dtype=np.float64)
    covered_mass = 0.0
    weighted_width = 0.0
    for it in intervals:
        s, e = it.start, it.end
        mass = float(weights[s:e].sum())
        if mass <= 0:
            continue
        summary = X[s:e].mean(axis=0)
        out += mass * summary
        covered_mass += mass
        weighted_width += mass * it.width
    return out, covered_mass, weighted_width


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + EPS))


def run_probe(
    seeds: Iterable[int],
    tokens_list: Iterable[int],
    budgets: Iterable[int],
    dims: int,
    anchor_strength: float,
) -> Dict[str, object]:
    regimes = ["coarse_global", "fine_recent", "mixed_multiscale", "old_anchor_pin", "two_anchor_recall"]
    rows: List[Dict[str, object]] = []
    for seed in seeds:
        for tokens in tokens_list:
            stream = generate_stream(seed, tokens=tokens, dims=dims, anchor_strength=anchor_strength)
            X = stream["X"]
            anchor_times = stream["anchor_times"]
            masks = stream["masks"]
            for regime in regimes:
                weights = weights_for_regime(regime, tokens, anchor_times)
                full = weights @ X
                for budget in budgets:
                    if budget > tokens:
                        continue
                    for policy_name, fn in POLICIES.items():
                        intervals = fn(tokens, budget, anchor_times)
                        approx, coverage_mass, weighted_width = approximate_output(X, weights, intervals)
                        row = {
                            "seed": seed,
                            "tokens": tokens,
                            "budget": budget,
                            "budget_fraction": budget / tokens,
                            "regime": regime,
                            "policy": policy_name,
                            "interval_count": len(intervals),
                            "coverage_mass": coverage_mass,
                            "weighted_interval_width": weighted_width,
                            "output_mse": float(np.mean((approx - full) ** 2)),
                            "output_rel_error": float(np.linalg.norm(approx - full) / (np.linalg.norm(full) + EPS)),
                            "output_cosine": cosine(approx, full),
                        }
                        for mask_name, mask in masks.items():
                            row[f"{mask_name}_rel_error"] = float(
                                np.linalg.norm((approx - full)[mask]) / (np.linalg.norm(full[mask]) + EPS)
                            )
                        rows.append(row)
    summary: Dict[str, object] = {"row_count": len(rows), "by_regime_policy": {}, "best_policy_by_regime_budget": {}, "best_compressed_policy_by_regime_budget": {}}
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    grouped_budget: Dict[Tuple[str, int, str], List[Dict[str, object]]] = {}
    for r in rows:
        grouped.setdefault((str(r["regime"]), str(r["policy"])), []).append(r)
        grouped_budget.setdefault((str(r["regime"]), int(r["budget"]), str(r["policy"])), []).append(r)
    for (regime, policy), rs in sorted(grouped.items()):
        summary["by_regime_policy"][f"{regime}/{policy}"] = {
            "mean_output_rel_error": float(np.mean([r["output_rel_error"] for r in rs])),
            "mean_output_cosine": float(np.mean([r["output_cosine"] for r in rs])),
            "mean_coverage_mass": float(np.mean([r["coverage_mass"] for r in rs])),
            "mean_weighted_interval_width": float(np.mean([r["weighted_interval_width"] for r in rs])),
            "mean_coarse_rel_error": float(np.mean([r["coarse_rel_error"] for r in rs])),
            "mean_fine_rel_error": float(np.mean([r["fine_rel_error"] for r in rs])),
        }
    for regime in regimes:
        for budget in budgets:
            candidates = []
            for policy in POLICIES:
                rs = grouped_budget.get((regime, budget, policy), [])
                if rs:
                    candidates.append((float(np.mean([r["output_rel_error"] for r in rs])), policy))
            if candidates:
                candidates.sort()
                summary["best_policy_by_regime_budget"][f"{regime}/B{budget}"] = {
                    "best_policy": candidates[0][1],
                    "mean_output_rel_error": candidates[0][0],
                }
                compressed = [c for c in candidates if c[1] != "full_cache"]
                if compressed:
                    summary["best_compressed_policy_by_regime_budget"][f"{regime}/B{budget}"] = {
                        "best_policy": compressed[0][1],
                        "mean_output_rel_error": compressed[0][0],
                    }
    return {
        "probe": "hierarchical_fademem_cache",
        "purpose": "Cheap multiscale-cache falsifier: dense-near/sparse-far memory vs flat eviction/summarization.",
        "config": {
            "seeds": list(seeds),
            "tokens_list": list(tokens_list),
            "budgets": list(budgets),
            "dims": dims,
            "anchor_strength": anchor_strength,
            "policies": list(POLICIES.keys()),
        },
        "summary": summary,
        "rows": rows,
    }


def write_csv(rows: List[Dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0006_FADEMEM_HIERARCHY_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0006_FADEMEM_HIERARCHY_SMOKE.csv"))
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--dims", type=int, default=48)
    ap.add_argument("--anchor-strength", type=float, default=3.0)
    args = ap.parse_args()
    result = run_probe(
        seeds=range(args.seeds),
        tokens_list=[256, 512, 1024],
        budgets=[16, 32, 64],
        dims=args.dims,
        anchor_strength=args.anchor_strength,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(result["rows"], args.out_csv)  # type: ignore[arg-type]
    print(json.dumps({"wrote": str(args.out_json), "rows": result["summary"]["row_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
