#!/usr/bin/env python3
"""Tiny stochastic tree-search / backtracking probe.

Inspired by work claiming agentic transformers can learn a two-head DFS-like
normal form: one head tracks previous actions, another detects failures and
triggers backtracking. This probe is not a transformer reproduction; it is a
cheap environment and policy battery to decide whether this lane deserves a
trained tiny policy later.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["uniform_goal", "ranked_goal", "deceptive_prefix", "sparse_reward", "deep_generalization"]
POLICIES = ["random_walk", "greedy_no_backtrack", "failure_head_only", "action_head_only", "dfs_two_head", "ranked_dfs", "oracle_path"]


def make_goal(seed: int, regime: str, depth: int, branch: int) -> Tuple[Tuple[int, ...], np.ndarray]:
    rng = np.random.default_rng(115000 + seed)
    prior = np.ones(branch, dtype=np.float64) / branch
    if regime == "ranked_goal":
        prior = np.linspace(branch, 1, branch, dtype=np.float64); prior /= prior.sum()
    elif regime == "deceptive_prefix":
        prior = np.array([0.55] + [(0.45 / (branch - 1))] * (branch - 1)) if branch > 1 else np.ones(1)
    elif regime == "deep_generalization":
        prior = np.linspace(branch, 1, branch, dtype=np.float64); prior /= prior.sum()
    path = []
    for d in range(depth):
        if regime == "deceptive_prefix" and d == 0:
            p = prior.copy(); p[0] = 0.08; p /= p.sum()
        else:
            p = prior
        path.append(int(rng.choice(branch, p=p)))
    return tuple(path), prior


def simulate(seed: int, regime: str, policy: str, depth: int, branch: int, max_steps: int) -> Tuple[bool, int, float, float]:
    rng = np.random.default_rng(117000 + seed)
    goal, prior = make_goal(seed, regime, depth, branch)
    stack: List[Tuple[Tuple[int, ...], List[int]]] = [(tuple(), [])]
    current: Tuple[int, ...] = tuple()
    tried: Dict[Tuple[int, ...], set[int]] = {}
    failures_seen = 0
    backtracks = 0

    for step in range(1, max_steps + 1):
        if current == goal:
            return True, step, failures_seen / max(1, step), backtracks / max(1, step)
        if len(current) == depth:
            failures_seen += 1
            if policy in {"greedy_no_backtrack", "failure_head_only"}:
                current = tuple()
            else:
                current = current[:-1]
                backtracks += 1
            continue

        if policy == "oracle_path":
            a = goal[len(current)]
        elif policy == "random_walk":
            a = int(rng.integers(0, branch))
        elif policy == "greedy_no_backtrack":
            a = int(np.argmax(prior))
        elif policy == "failure_head_only":
            # Notices failure but loses the path/action trace; restarts and repeats too often.
            a = int(np.argmax(prior)) if rng.random() < 0.75 else int(rng.integers(0, branch))
        elif policy == "action_head_only":
            # Tracks what was tried locally but fails to interpret terminal failure reliably.
            seen = tried.setdefault(current, set())
            choices = [a for a in range(branch) if a not in seen]
            a = choices[0] if choices else int(rng.integers(0, branch))
            seen.add(a)
            if len(current) == depth - 1 and rng.random() < 0.35:
                tried[current] = set()  # forget failure meaning
        elif policy == "dfs_two_head":
            seen = tried.setdefault(current, set())
            choices = [a for a in range(branch) if a not in seen]
            if choices:
                a = choices[0]
                seen.add(a)
            else:
                current = current[:-1]
                backtracks += 1
                continue
        elif policy == "ranked_dfs":
            seen = tried.setdefault(current, set())
            order = list(np.argsort(-prior))
            choices = [a for a in order if a not in seen]
            if choices:
                a = choices[0]
                seen.add(a)
            else:
                current = current[:-1]
                backtracks += 1
                continue
        else:
            raise ValueError(policy)

        current = current + (int(a),)
        # Deceptive feedback: wrong prefix is only revealed at leaf for sparse regimes.
        if regime != "sparse_reward" and len(current) < depth and current != goal[: len(current)] and policy in {"dfs_two_head", "ranked_dfs"}:
            failures_seen += 1
            current = current[:-1]
            backtracks += 1
    return False, max_steps, failures_seen / max(1, max_steps), backtracks / max(1, max_steps)


@dataclass
class Row:
    seed: int
    regime: str
    policy: str
    depth: int
    branch: int
    max_steps: int
    success: float
    steps_used: int
    failure_trace_rate: float
    backtrack_rate: float
    efficiency: float


def eval_one(seed: int, regime: str, policy: str, depth: int, branch: int, max_steps: int) -> Row:
    ok, steps, fail_rate, back_rate = simulate(seed, regime, policy, depth, branch, max_steps)
    efficiency = float((1.0 if ok else 0.0) * max_steps / max(steps, 1))
    return Row(seed, regime, policy, depth, branch, max_steps, float(ok), steps, fail_rate, back_rate, efficiency)


def run(seeds: int, depths: List[int], branch: int, max_steps_mult: int) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for depth in depths:
                max_steps = max_steps_mult * (branch ** min(depth, 5))
                for policy in POLICIES:
                    rows.append(eval_one(seed, regime, policy, depth, branch, max_steps))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.depth), {}).setdefault(r.policy, []).append(r.efficiency)
    winners = {}; counts: Dict[str, int] = {}
    non_oracle = {}; ncounts: Dict[str, int] = {}
    for (regime, depth), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get); winners[f"{regime}/D{depth}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p != "oracle_path"}
        nw = max(means2, key=means2.get); non_oracle[f"{regime}/D{depth}"] = nw; ncounts[nw] = ncounts.get(nw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "efficiency", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": non_oracle,
        "winner_counts_excluding_oracle": ncounts,
        "interpretation": "If two-head DFS/ranked DFS dominate at deeper trees, the lane deserves a tiny policy-gradient or imitation-trained transformer; if random/greedy match them, the task is too weak.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0011", "probe": "agentic_dfs_search", "config": {"regimes": REGIMES, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader(); w.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--depths", type=int, nargs="+", default=[2, 3, 4, 5])
    ap.add_argument("--branch", type=int, default=3)
    ap.add_argument("--max-steps-mult", type=int, default=4)
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0011_AGENTIC_DFS_SEARCH_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0011_AGENTIC_DFS_SEARCH_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.depths, args.branch, args.max_steps_mult)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
