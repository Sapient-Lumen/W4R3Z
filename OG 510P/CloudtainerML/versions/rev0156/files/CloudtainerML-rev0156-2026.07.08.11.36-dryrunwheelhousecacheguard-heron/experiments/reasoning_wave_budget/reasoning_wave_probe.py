#!/usr/bin/env python3
"""Reasoning-wave KV budget allocation toy probe.

ReasonAlloc-style papers claim decoding-time KV cache demand is heterogeneous
across layers and heads, and that uniform or monotone/pyramid allocations can
starve reasoning-critical pathways. This probe creates synthetic layer/head/time
utility landscapes and compares simple allocation policies under the same global
cache budget.

It is not a reproduction. It is a small falsifier: can a non-monotone static
layer wave + online head router beat uniform and pyramid baselines in a generated
world where critical demand moves across heads over decoding steps?
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def simplex(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    x = np.maximum(x, 0.0)
    s = np.sum(x)
    return x / (s + eps)


def allocate_integer(weights: np.ndarray, total: int, floor: int = 0) -> np.ndarray:
    """Largest-remainder integer allocation with optional per-entry floor."""
    n = len(weights)
    if total <= 0:
        return np.zeros(n, dtype=np.int64)
    if floor * n > total:
        floor = max(0, total // n)
    remaining = total - floor * n
    w = simplex(weights)
    raw = w * remaining
    base = np.floor(raw).astype(np.int64) + floor
    gap = total - int(np.sum(base))
    if gap > 0:
        frac = raw - np.floor(raw)
        order = np.argsort(-frac)
        base[order[:gap]] += 1
    return base


def make_wave(seed: int, layers: int, heads: int, steps: int) -> dict:
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, layers)
    # Non-monotone layer demand: shallow semantic anchoring + late verifier bump.
    base_wave = 0.35 + 1.15 * np.exp(-((x - 0.16) / 0.18) ** 2) + 1.55 * np.exp(-((x - 0.73) / 0.16) ** 2)
    base_wave += 0.12 * rng.normal(size=layers)
    base_wave = np.maximum(base_wave, 0.05)

    head_affinity = rng.lognormal(mean=0.0, sigma=0.55, size=(layers, heads))
    head_affinity = head_affinity / (np.mean(head_affinity, axis=1, keepdims=True) + 1e-8)

    demand = np.zeros((steps, layers, heads), dtype=np.float32)
    utility = np.zeros_like(demand)
    critical = np.zeros_like(demand, dtype=bool)
    for t in range(steps):
        phase = t / max(1, steps - 1)
        # The "reasoning path" moves from broad/early to late/verifier and back to a final anchor.
        center = 0.12 + 0.68 * np.sin(np.pi * phase) ** 1.25
        dynamic_layer = 0.55 + 1.35 * np.exp(-((x - center) / 0.18) ** 2)
        late_check = 0.55 * np.exp(-((x - (0.78 + 0.06 * np.sin(5 * np.pi * phase))) / 0.10) ** 2)
        layer_need = base_wave * dynamic_layer + late_check
        # A small subset of heads become reasoning-critical at different phases.
        for l in range(layers):
            moving_head = int((t // max(1, steps // heads) + l) % heads)
            secondary = int((moving_head + 1 + (l % 3)) % heads)
            h_need = 0.35 * head_affinity[l] + 0.15 * rng.random(heads)
            h_need[moving_head] += 1.6 + 0.4 * np.sin(2 * np.pi * phase + l)
            h_need[secondary] += 0.7
            demand[t, l] = np.maximum(1.0, 16.0 * layer_need[l] * h_need).astype(np.float32)
            utility[t, l] = simplex(np.sqrt(demand[t, l]) + 0.1 * rng.random(heads))
            # Critical means the head participates in a synthetic reasoning chain this step.
            critical[t, l, moving_head] = True
            if l % 4 == 0:
                critical[t, l, secondary] = True
    return {"base_wave": base_wave.astype(np.float32), "demand": demand, "utility": utility, "critical": critical}


def demand_to_preserved_mass(demand: np.ndarray, budget: np.ndarray, alpha: float = 1.65) -> np.ndarray:
    """Saturating curve: preserving exactly demand gives ~80% of mass."""
    ratio = budget / (demand + 1e-8)
    return (1.0 - np.exp(-alpha * ratio)).astype(np.float32)


def layer_weights_from_policy(policy: str, world: dict, t: int, layers: int) -> np.ndarray:
    demand = world["demand"]
    if policy in {"uniform", "online_head_only"}:
        return np.ones(layers)
    if policy == "pyramid_decreasing":
        return np.linspace(1.6, 0.35, layers)
    if policy == "pyramid_increasing":
        return np.linspace(0.35, 1.6, layers)
    if policy in {"static_reasoning_wave", "reasonalloc_toy"}:
        # Offline calibration: average demand over a small calibration stream.
        return np.mean(np.sum(demand[: max(2, demand.shape[0] // 4)], axis=2), axis=0)
    if policy == "online_layer":
        return np.sum(demand[t], axis=1)
    if policy == "oracle_step":
        return np.sum(demand[t], axis=1)
    raise ValueError(policy)


def head_weights_from_policy(policy: str, world: dict, t: int, layer: int, heads: int) -> np.ndarray:
    demand = world["demand"]
    utility = world["utility"]
    if policy in {"uniform", "pyramid_decreasing", "pyramid_increasing", "static_reasoning_wave", "online_layer"}:
        return np.ones(heads)
    if policy in {"online_head_only", "reasonalloc_toy"}:
        # Online router: utility/redundancy proxy. Demand is not directly known to a real method;
        # this generated utility is a noisy but useful proxy.
        return utility[t, layer] + 0.05
    if policy == "oracle_step":
        return demand[t, layer] + 1e-6
    raise ValueError(policy)


@dataclass
class Row:
    seed: int
    policy: str
    global_budget: int
    step: int
    preserved_mass_mean: float
    preserved_mass_p10: float
    critical_preserved_mass_mean: float
    critical_starvation_rate: float
    layer_starvation_rate: float
    allocated_entropy: float
    success_proxy: float


def eval_policy(seed: int, policy: str, global_budget: int, world: dict, step: int) -> Row:
    demand = world["demand"][step]
    critical = world["critical"][step]
    layers, heads = demand.shape
    lw = layer_weights_from_policy(policy, world, step, layers)
    layer_budget = allocate_integer(lw, global_budget, floor=0)
    budget = np.zeros((layers, heads), dtype=np.float32)
    for l in range(layers):
        hw = head_weights_from_policy(policy, world, step, l, heads)
        budget[l] = allocate_integer(hw, int(layer_budget[l]), floor=0)
    mass = demand_to_preserved_mass(demand, budget)
    critical_mass = mass[critical]
    # Starved if the saturating preserved mass is below a rough usable threshold.
    crit_starve = float(np.mean(critical_mass < 0.62)) if critical_mass.size else 0.0
    layer_need = np.sum(demand, axis=1)
    layer_mass = demand_to_preserved_mass(layer_need, layer_budget.astype(np.float32))
    # Product is too harsh; geometric mean works as a chain-success proxy.
    success = float(np.exp(np.mean(np.log(np.clip(critical_mass, 1e-4, 1.0))))) if critical_mass.size else float(np.mean(mass))
    flat_alloc = budget.reshape(-1)
    p = flat_alloc / (np.sum(flat_alloc) + 1e-8)
    entropy = float(-np.sum(p[p > 0] * np.log2(p[p > 0])) / np.log2(len(p))) if np.sum(flat_alloc) > 0 else 0.0
    return Row(
        seed=seed,
        policy=policy,
        global_budget=global_budget,
        step=step,
        preserved_mass_mean=float(np.mean(mass)),
        preserved_mass_p10=float(np.percentile(mass, 10)),
        critical_preserved_mass_mean=float(np.mean(critical_mass)) if critical_mass.size else 0.0,
        critical_starvation_rate=crit_starve,
        layer_starvation_rate=float(np.mean(layer_mass < 0.62)),
        allocated_entropy=entropy,
        success_proxy=success,
    )


def summarize(rows: List[Row]) -> dict:
    by = {}
    for budget in sorted({r.global_budget for r in rows}):
        candidates = []
        for policy in sorted({r.policy for r in rows}):
            sub = [r for r in rows if r.policy == policy and r.global_budget == budget]
            rec = {
                "mean_success_proxy": float(np.mean([r.success_proxy for r in sub])),
                "mean_critical_starvation_rate": float(np.mean([r.critical_starvation_rate for r in sub])),
                "mean_preserved_mass": float(np.mean([r.preserved_mass_mean for r in sub])),
                "mean_layer_starvation_rate": float(np.mean([r.layer_starvation_rate for r in sub])),
                "mean_allocated_entropy": float(np.mean([r.allocated_entropy for r in sub])),
            }
            by[f"budget{budget}/{policy}"] = rec
            candidates.append((-rec["mean_success_proxy"], rec["mean_critical_starvation_rate"], policy))
        candidates.sort()
        best_policy = candidates[0][2]
        by[f"budget{budget}/__winner__"] = {"best_policy": best_policy, "best_mean_success_proxy": float(-candidates[0][0])}
    winner_counts: Dict[str, int] = {}
    practical_winners: Dict[str, str] = {}
    for key, val in by.items():
        if key.endswith("/__winner__"):
            winner_counts[val["best_policy"]] = winner_counts.get(val["best_policy"], 0) + 1
    for budget in sorted({r.global_budget for r in rows}):
        candidates = []
        for policy in sorted({r.policy for r in rows if r.policy != "oracle_step"}):
            rec = by[f"budget{budget}/{policy}"]
            candidates.append((-rec["mean_success_proxy"], rec["mean_critical_starvation_rate"], policy))
        candidates.sort()
        practical_winners[f"budget{budget}"] = candidates[0][2]
    return {"row_count": len(rows), "by_budget_policy": by, "winner_counts": winner_counts, "practical_winners_excluding_oracle": practical_winners}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0007_REASONING_WAVE_BUDGET_SMOKE"))
    ap.add_argument("--seeds", type=int, default=24)
    ap.add_argument("--layers", type=int, default=18)
    ap.add_argument("--heads", type=int, default=8)
    ap.add_argument("--steps", type=int, default=36)
    args = ap.parse_args()
    policies = ["uniform", "pyramid_decreasing", "pyramid_increasing", "static_reasoning_wave", "online_head_only", "online_layer", "reasonalloc_toy", "oracle_step"]
    budgets = [384, 768, 1152]
    rows: List[Row] = []
    for seed in range(args.seeds):
        world = make_wave(seed, args.layers, args.heads, args.steps)
        for step in range(args.steps):
            for budget in budgets:
                for policy in policies:
                    rows.append(eval_policy(seed, policy, budget, world, step))

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out.with_suffix(".csv")
    json_path = out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in rows)
    payload = {
        "probe": "reasoning_wave_budget",
        "purpose": "Synthetic per-layer/per-head decoding-time KV budget allocation test for uniform vs pyramid vs ReasonAlloc-like hierarchical routing.",
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()} | {"policies": policies, "budgets": budgets},
        "summary": summarize(rows),
        "csv": str(csv_path),
        "rows": [asdict(r) for r in rows[:80]],
        "note": "Rows are truncated in JSON; CSV contains all rows.",
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"probe": payload["probe"], "rows": len(rows), "csv": str(csv_path), "json": str(json_path), "winner_counts": payload["summary"]["winner_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
