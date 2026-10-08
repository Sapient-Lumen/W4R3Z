#!/usr/bin/env python3
"""Dynamic state-merging probe for CloudtainerML.

Inspired by Dynamic Linear Attention (arXiv:2606.10650) and nearby bounded-memory
linear-attention work. It creates non-stationary sequences with stable spans and
sharp transitions, then compares fixed blocks against dynamic drift-aware adjacent
state merging under a fixed memory-state budget.

The cheap question is:
  "Can content-aware boundaries preserve transition information better than fixed
   block summaries at the same number of states?"
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class State:
    start: int
    end: int
    count: int
    mean: np.ndarray
    sse: float
    info_sum: float


@dataclass(frozen=True)
class Config:
    seeds: int = 12
    length: int = 768
    dim: int = 24
    segments: int = 12
    budgets: Tuple[int, ...] = (16, 24, 32, 48, 64)


def make_sequence(rng: np.random.Generator, cfg: Config) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Variable-length segments with sharp jumps; transition tokens matter disproportionately.
    raw = rng.dirichlet(np.ones(cfg.segments) * 1.4)
    lengths = np.maximum(12, np.round(raw * cfg.length).astype(int))
    while lengths.sum() > cfg.length:
        i = int(np.argmax(lengths)); lengths[i] -= 1
    while lengths.sum() < cfg.length:
        i = int(rng.integers(0, cfg.segments)); lengths[i] += 1

    centers = []
    c = rng.normal(size=cfg.dim)
    for _ in range(cfg.segments):
        jump = rng.normal(size=cfg.dim)
        jump = jump / (np.linalg.norm(jump) + 1e-9)
        c = 0.55 * c + 2.5 * jump
        centers.append(c.copy())
    centers = np.asarray(centers)

    xs, labels, transition_mask = [], [], []
    pos = 0
    for s, L in enumerate(lengths):
        for j in range(L):
            local = j / max(1, L - 1)
            # Transitions have extra curvature and higher information density.
            edge = min(j, L - 1 - j) < max(2, int(0.08 * L))
            curvature = 0.0
            if s + 1 < cfg.segments and local > 0.75:
                curvature = (local - 0.75) / 0.25
            center = (1 - curvature) * centers[s] + curvature * centers[min(s + 1, cfg.segments - 1)]
            x = center + 0.18 * rng.normal(size=cfg.dim)
            xs.append(x); labels.append(s); transition_mask.append(edge or curvature > 0.0)
            pos += 1
    X = np.asarray(xs)
    X = (X - X.mean(axis=0, keepdims=True)) / (X.std(axis=0, keepdims=True) + 1e-6)
    return X, np.asarray(labels), np.asarray(transition_mask, dtype=bool)


def summarize_state(X: np.ndarray, start: int, end: int, info: np.ndarray | None = None) -> State:
    chunk = X[start:end]
    mean = chunk.mean(axis=0)
    sse = float(np.sum((chunk - mean) ** 2))
    if info is None:
        info_sum = float(end - start)
    else:
        info_sum = float(np.sum(info[start:end]))
    return State(start=start, end=end, count=end - start, mean=mean, sse=sse, info_sum=info_sum)


def reconstruct(states: List[State], n: int, dim: int) -> np.ndarray:
    out = np.zeros((n, dim))
    for st in states:
        out[st.start:st.end] = st.mean
    return out


def fixed_blocks(X: np.ndarray, budget: int) -> List[State]:
    n = len(X)
    bounds = np.linspace(0, n, budget + 1).round().astype(int)
    states = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b > a:
            states.append(summarize_state(X, int(a), int(b)))
    return states


def recency_highres(X: np.ndarray, budget: int) -> List[State]:
    n = len(X)
    tail_states = max(1, int(budget * 0.6))
    prefix_states = budget - tail_states
    split = int(n * 0.65)
    states = []
    if prefix_states > 0:
        bounds = np.linspace(0, split, prefix_states + 1).round().astype(int)
        states += [summarize_state(X, int(a), int(b)) for a, b in zip(bounds[:-1], bounds[1:]) if b > a]
    bounds = np.linspace(split, n, tail_states + 1).round().astype(int)
    states += [summarize_state(X, int(a), int(b)) for a, b in zip(bounds[:-1], bounds[1:]) if b > a]
    return states


def merge_pair(X: np.ndarray, states: List[State], i: int, info: np.ndarray | None) -> List[State]:
    merged = summarize_state(X, states[i].start, states[i + 1].end, info)
    return states[:i] + [merged] + states[i + 2:]


def dynamic_drift_merge(X: np.ndarray, budget: int, drift_quantile: float = 0.72) -> List[State]:
    # Token information = representation drift from previous token.
    drift = np.zeros(len(X))
    drift[1:] = np.linalg.norm(np.diff(X, axis=0), axis=-1)
    threshold = float(np.quantile(drift[1:], drift_quantile))

    bounds = [0]
    running_mean = X[0].copy()
    running_count = 1
    max_len = max(8, len(X) // max(1, budget // 2))
    for t in range(1, len(X)):
        proposed = (running_mean * running_count + X[t]) / (running_count + 1)
        hetero = float(np.linalg.norm(X[t] - running_mean))
        if (drift[t] > threshold and hetero > threshold) or running_count >= max_len:
            bounds.append(t)
            running_mean = X[t].copy(); running_count = 1
        else:
            running_mean = proposed; running_count += 1
    bounds.append(len(X))
    states = [summarize_state(X, bounds[i], bounds[i + 1], drift) for i in range(len(bounds) - 1) if bounds[i + 1] > bounds[i]]

    # Capacity-bounded adjacent merging: merge the pair that adds the least extra SSE per information density.
    while len(states) > budget:
        costs = []
        for i in range(len(states) - 1):
            merged = summarize_state(X, states[i].start, states[i + 1].end, drift)
            added_sse = merged.sse - states[i].sse - states[i + 1].sse
            info_density = (states[i].info_sum + states[i + 1].info_sum) / max(1, states[i].count + states[i + 1].count)
            costs.append(added_sse / (1e-6 + info_density))
        idx = int(np.argmin(costs))
        states = merge_pair(X, states, idx, drift)
    return states


def random_adjacent_merge(X: np.ndarray, budget: int, rng: np.random.Generator) -> List[State]:
    # Begin with small chunks then randomly merge adjacent chunks down to budget.
    chunk = max(4, len(X) // (budget * 3))
    states = [summarize_state(X, a, min(len(X), a + chunk)) for a in range(0, len(X), chunk)]
    while len(states) > budget:
        idx = int(rng.integers(0, len(states) - 1))
        states = merge_pair(X, states, idx, None)
    return states


def boundary_f1(states: List[State], labels: np.ndarray, tolerance: int = 4) -> Tuple[float, float, float]:
    true = set(np.where(labels[1:] != labels[:-1])[0] + 1)
    pred = set(st.start for st in states[1:])
    if not pred and not true:
        return 1.0, 1.0, 1.0
    hit = 0
    used = set()
    for p in pred:
        near = [t for t in true if abs(t - p) <= tolerance and t not in used]
        if near:
            used.add(near[0]); hit += 1
    precision = hit / max(1, len(pred))
    recall = hit / max(1, len(true))
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    return float(precision), float(recall), float(f1)


def metrics(X: np.ndarray, labels: np.ndarray, transition_mask: np.ndarray, states: List[State]) -> Dict[str, float]:
    R = reconstruct(states, len(X), X.shape[1])
    p, r, f = boundary_f1(states, labels)
    return {
        "states": float(len(states)),
        "overall_mse": float(np.mean((X - R) ** 2)),
        "transition_mse": float(np.mean((X[transition_mask] - R[transition_mask]) ** 2)),
        "stable_mse": float(np.mean((X[~transition_mask] - R[~transition_mask]) ** 2)),
        "boundary_precision": p,
        "boundary_recall": r,
        "boundary_f1": f,
    }


def run(cfg: Config) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for seed in range(cfg.seeds):
        rng = np.random.default_rng(9901 + seed)
        X, labels, transition_mask = make_sequence(rng, cfg)
        for budget in cfg.budgets:
            policies = {
                "fixed_uniform_blocks": fixed_blocks(X, budget),
                "recency_highres_blocks": recency_highres(X, budget),
                "dynamic_drift_merge": dynamic_drift_merge(X, budget),
                "random_adjacent_merge": random_adjacent_merge(X, budget, rng),
            }
            for name, states in policies.items():
                row = {"seed": seed, "budget": budget, "policy": name}
                row.update(metrics(X, labels, transition_mask, states))
                rows.append(row)
    return rows


def summarize(rows: List[Dict[str, object]]) -> Dict[str, object]:
    grouped: Dict[Tuple[int, str], List[Dict[str, object]]] = {}
    for r in rows:
        grouped.setdefault((int(r["budget"]), str(r["policy"])), []).append(r)
    out = {"row_count": len(rows), "by_budget_policy": {}}
    for (budget, policy), rs in grouped.items():
        out["by_budget_policy"][f"budget={budget}/{policy}"] = {
            "mean_overall_mse": float(np.mean([r["overall_mse"] for r in rs])),
            "mean_transition_mse": float(np.mean([r["transition_mse"] for r in rs])),
            "mean_boundary_f1": float(np.mean([r["boundary_f1"] for r in rs])),
            "mean_states": float(np.mean([r["states"] for r in rs])),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("dynamic_state_merging_results.json"))
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--seeds", type=int, default=12)
    args = ap.parse_args()
    cfg = Config(seeds=args.seeds)
    rows = run(cfg)
    payload = {
        "probe": "dynamic_state_merging",
        "purpose": "Cheap simulator for content-aware bounded memory state construction.",
        "config": cfg.__dict__,
        "summary": summarize(rows),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    print(json.dumps({"wrote": str(args.out), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
