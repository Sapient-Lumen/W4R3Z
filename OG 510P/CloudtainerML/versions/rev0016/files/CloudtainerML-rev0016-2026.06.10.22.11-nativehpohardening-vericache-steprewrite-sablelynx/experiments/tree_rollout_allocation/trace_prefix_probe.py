#!/usr/bin/env python3
"""CloudtainerML rev0013: TRACE-style prefix rollout allocation toy.

Not a reproduction. It creates synthetic ReAct-style rollout trees where only some
intermediate prefixes have high contrast in terminal outcomes. The probe compares
uniform rollouts, root-level allocation, prefix contrast allocation, and an oracle.
"""
from __future__ import annotations
import argparse, json, math, random, statistics, time
from pathlib import Path
from typing import Dict, List, Tuple


def sigmoid(x: float) -> float: return 1 / (1 + math.exp(-x))


def make_tree(rng: random.Random, regime: str, roots: int = 12, depth: int = 4, branch: int = 3):
    nodes = []
    for r in range(roots):
        root_skill = rng.gauss(0, 1)
        for p in range(branch ** depth):
            # prefix id is synthetic path index; contrast changes by regime.
            path_hash = (p * 1103515245 + r * 12345) & 0xFFFF
            local = ((path_hash % 17) - 8) / 8
            if regime == "root_contrast":
                logit = 1.3 * root_skill + 0.15 * local
            elif regime == "prefix_contrast":
                logit = 0.15 * root_skill + 1.4 * local
            elif regime == "late_trap":
                logit = 0.4 * root_skill + (1.8 if (p % 11 == 0) else -0.4) + rng.gauss(0, 0.2)
            else:  # mixed
                logit = 0.75 * root_skill + 0.75 * local + rng.gauss(0, 0.15)
            prob = sigmoid(logit)
            prefix_depth = 1 + (p % depth)
            nodes.append({"root": r, "path": p, "prefix_depth": prefix_depth, "p_success": prob})
    return nodes


def sample_reward(rng: random.Random, p: float) -> int:
    return int(rng.random() < p)


def allocate(policy: str, nodes: List[Dict], budget: int, rng: random.Random):
    if policy == "uniform":
        return [rng.choice(nodes) for _ in range(budget)]
    if policy == "root_level":
        roots = sorted(set(n["root"] for n in nodes))
        root_scores = {r: statistics.mean(n["p_success"] for n in nodes if n["root"] == r) for r in roots}
        weights = [abs(root_scores[r] - 0.5) + 0.05 for r in roots]
        chosen = []
        for _ in range(budget):
            r = rng.choices(roots, weights=weights)[0]
            chosen.append(rng.choice([n for n in nodes if n["root"] == r]))
        return chosen
    if policy == "prefix_contrast":
        # Allocate to prefixes closest to 0.5 success probability: maximum reward contrast.
        weights = [1.0 / (0.03 + abs(n["p_success"] - 0.5)) for n in nodes]
        return rng.choices(nodes, weights=weights, k=budget)
    if policy == "oracle_mixed_terminal":
        # Upper anchor: knows exact bernoulli variance p(1-p).
        weights = [n["p_success"] * (1 - n["p_success"]) + 1e-6 for n in nodes]
        return rng.choices(nodes, weights=weights, k=budget)
    raise ValueError(policy)


def run(policy: str, regime: str, seed: int, budget: int):
    rng = random.Random(seed)
    nodes = make_tree(rng, regime)
    selected = allocate(policy, nodes, budget, rng)
    rewards = [sample_reward(rng, n["p_success"]) for n in selected]
    # Contrast is high when both successes and failures appear in sampled continuations.
    mean = statistics.mean(rewards) if rewards else 0
    contrast = mean * (1 - mean)
    unique_roots = len(set(n["root"] for n in selected))
    unique_prefixes = len(set((n["root"], n["path"]) for n in selected))
    return contrast, mean, unique_roots, unique_prefixes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/probe-results/REV0013_TRACE_PREFIX_ROLLOUT_SMOKE.json")
    ap.add_argument("--seeds", type=int, default=80)
    args = ap.parse_args()
    t0 = time.time()
    regimes = ["root_contrast", "prefix_contrast", "late_trap", "mixed"]
    policies = ["uniform", "root_level", "prefix_contrast", "oracle_mixed_terminal"]
    budgets = [24, 48, 96]
    rows = []
    for regime in regimes:
        for budget in budgets:
            for policy in policies:
                vals = [run(policy, regime, 1009*s + budget, budget) for s in range(args.seeds)]
                rows.append({
                    "regime": regime,
                    "budget": budget,
                    "policy": policy,
                    "mean_reward_contrast": statistics.mean(v[0] for v in vals),
                    "mean_success_rate": statistics.mean(v[1] for v in vals),
                    "mean_unique_roots": statistics.mean(v[2] for v in vals),
                    "mean_unique_prefixes": statistics.mean(v[3] for v in vals),
                    "runs": args.seeds,
                })
    winners = {}
    for regime in regimes:
        for budget in budgets:
            subset = [r for r in rows if r["regime"] == regime and r["budget"] == budget]
            winners[f"{regime}@{budget}"] = max(subset, key=lambda r: r["mean_reward_contrast"])["policy"]
    out = {
        "project": "CloudtainerML",
        "revision": "rev0013",
        "probe": "trace_prefix_rollout_smoke",
        "is_paper_reproduction": False,
        "summary": {
            "primary_metric": {"name": "mean_reward_contrast", "direction": "higher_is_better"},
            "runtime_seconds": round(time.time() - t0, 4),
            "winners_by_regime_budget": winners,
            "interpretation": "Toy TRACE-like allocation asks whether prefix-level contrast beats root-only budget allocation when terminal outcome rewards are sparse.",
        },
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(args.out)

if __name__ == "__main__": main()
