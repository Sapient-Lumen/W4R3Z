#!/usr/bin/env python3
"""Forecast sparse routing toy probe.

A tiny analogue of SparDA-style decoupled sparse attention: a Forecast signal
predicts which KV blocks the next layer will need, so selection/prefetch can be
computed ahead of the actual Query. We simulate layer/head support sets and
compare forecast routing to shared-once, current-query, and oracle selectors.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["stable_layers", "late_divergence", "query_noisy_forecast_clean", "alternating_heads", "topic_jump"]
POLICIES = ["random", "shared_once_first_layer", "previous_layer_reuse", "current_query_selector", "forecast_next_layer", "hybrid_forecast_query", "oracle_next_layer"]


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def choose(score: np.ndarray, k: int) -> np.ndarray:
    k = max(0, min(len(score), int(k)))
    if k == 0:
        return np.array([], dtype=np.int64)
    return np.argpartition(-score, k - 1)[:k].astype(np.int64)


def make_supports(seed: int, regime: str, layers: int, heads: int, blocks: int, support_k: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    centers = rng.integers(0, blocks, size=(heads,))
    true = np.zeros((layers, heads, blocks), dtype=np.float32)
    for h in range(heads):
        center = int(centers[h])
        for l in range(layers):
            if regime == "stable_layers":
                c = center + rng.integers(-2, 3)
            elif regime == "late_divergence":
                c = center + (0 if l < layers // 2 else (h + 1) * blocks // (heads + 1)) + rng.integers(-3, 4)
            elif regime == "query_noisy_forecast_clean":
                c = center + int(3 * np.sin(l + h)) + rng.integers(-1, 2)
            elif regime == "alternating_heads":
                c = (center if (l + h) % 2 == 0 else blocks - center - 1) + rng.integers(-2, 3)
            elif regime == "topic_jump":
                jump = (l // 2) * (blocks // max(2, layers))
                c = center + jump + rng.integers(-4, 5)
            else:
                raise ValueError(regime)
            c %= blocks
            dist = np.minimum(np.abs(np.arange(blocks) - c), blocks - np.abs(np.arange(blocks) - c))
            true[l, h] = np.exp(-(dist ** 2) / (2 * (support_k * 0.85) ** 2))
            # Add a few sparse remote facts.
            remote = rng.choice(blocks, size=max(1, support_k // 3), replace=False)
            true[l, h, remote] += rng.random(len(remote)) * 0.7
            true[l, h] = softmax(true[l, h] * 5.0)
    # Query scores are noisy observations of same-layer support.
    qnoise = 0.20 if regime != "query_noisy_forecast_clean" else 0.80
    query_score = true + rng.normal(0, qnoise / blocks, size=true.shape).astype(np.float32)
    # Forecast sees a smoothed transition signal intended for next-layer support.
    forecast_score = np.zeros_like(true)
    for l in range(layers):
        if l < layers - 1:
            noise = 0.18 if regime != "late_divergence" else 0.28
            forecast_score[l] = true[l + 1] + rng.normal(0, noise / blocks, size=(heads, blocks)).astype(np.float32)
        else:
            forecast_score[l] = true[l] + rng.normal(0, 0.25 / blocks, size=(heads, blocks)).astype(np.float32)
    return {"true": true, "query_score": query_score, "forecast_score": forecast_score}


def select(policy: str, world: Dict[str, np.ndarray], layer: int, head: int, budget: int, rng: np.random.Generator) -> np.ndarray:
    true = world["true"]; q = world["query_score"]; f = world["forecast_score"]
    blocks = true.shape[-1]
    if policy == "random":
        return rng.choice(blocks, size=budget, replace=False).astype(np.int64)
    if policy == "shared_once_first_layer":
        return choose(q[0, head], budget)
    if policy == "previous_layer_reuse":
        return choose(q[max(0, layer - 1), head], budget)
    if policy == "current_query_selector":
        # Uses current-layer query score to guess next-layer needs. Good when layer supports are stable.
        return choose(q[layer, head], budget)
    if policy == "forecast_next_layer":
        return choose(f[layer, head], budget)
    if policy == "hybrid_forecast_query":
        return choose(0.65 * f[layer, head] + 0.35 * q[layer, head], budget)
    if policy == "oracle_next_layer":
        nxt = min(layer + 1, true.shape[0] - 1)
        return choose(true[nxt, head], budget)
    raise ValueError(policy)


@dataclass
class Row:
    seed: int
    regime: str
    layer: int
    head: int
    budget: int
    policy: str
    support_recall: float
    mass_recall: float
    wasted_fraction: float
    js_divergence_proxy: float


def eval_row(seed: int, regime: str, layer: int, head: int, budget: int, policy: str, world: Dict[str, np.ndarray], support_k: int, rng: np.random.Generator) -> Row:
    true = world["true"]
    target_layer = min(layer + 1, true.shape[0] - 1)
    target_score = true[target_layer, head]
    target_support = set(choose(target_score, support_k).tolist())
    picked = set(select(policy, world, layer, head, budget, rng).tolist())
    hit = len(target_support & picked) / max(1, len(target_support))
    mass = float(np.sum(target_score[list(picked)])) if picked else 0.0
    wasted = 1.0 - len(target_support & picked) / max(1, len(picked))
    # Cheap distribution mismatch: dropped target mass plus extra low-mass picks.
    js_proxy = float((1.0 - mass) + 0.25 * wasted)
    return Row(seed, regime, layer, head, budget, policy, float(hit), mass, float(wasted), js_proxy)


def run(seeds: int, layers: int, heads: int, blocks: int, support_k: int, budgets: List[int]) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        rng = np.random.default_rng(50_000 + seed)
        for regime in REGIMES:
            world = make_supports(seed, regime, layers, heads, blocks, support_k)
            for budget in budgets:
                for layer in range(layers - 1):
                    for head in range(heads):
                        for policy in POLICIES:
                            rows.append(eval_row(seed, regime, layer, head, budget, policy, world, support_k, rng))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.budget), {}).setdefault(r.policy, []).append(r.mass_recall)
    winners: Dict[str, str] = {}
    practical: Dict[str, str] = {}
    counts: Dict[str, int] = {}
    pcounts: Dict[str, int] = {}
    for (regime, budget), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get)
        winners[f"{regime}/B{budget}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p != "oracle_next_layer"}
        pw = max(means2, key=means2.get)
        practical[f"{regime}/B{budget}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "mass_recall", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "Forecast routing is worth training if it beats same-layer query selection when layer support drifts or query scores are noisy; if shared_once wins, routing can be amortized.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {
        "project": "CloudtainerML",
        "revision": "rev0009",
        "probe": "forecast_sparse_routing",
        "config": {"regimes": REGIMES, "policies": POLICIES},
        "summary": summarize(rows),
        "rows": [asdict(r) for r in rows],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=6)
    p.add_argument("--layers", type=int, default=6)
    p.add_argument("--heads", type=int, default=6)
    p.add_argument("--blocks", type=int, default=128)
    p.add_argument("--support-k", type=int, default=12)
    p.add_argument("--budgets", type=int, nargs="+", default=[8, 16, 24])
    p.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0009_FORECAST_SPARSE_ROUTING_SMOKE.json"))
    p.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0009_FORECAST_SPARSE_ROUTING_SMOKE.csv"))
    args = p.parse_args()
    rows = run(args.seeds, args.layers, args.heads, args.blocks, args.support_k, args.budgets)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
