#!/usr/bin/env python3
"""Value-outlier eviction probe.

Toy proxy for observations that some value states have unusually large norms and
that losing them can destabilize long reasoning. This probe asks whether a tiny
policy that protects large-value outliers while sampling diverse remaining cache
entries dominates pure attention top-k under a fixed budget.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np


def topk(scores: np.ndarray, k: int) -> np.ndarray:
    if k >= scores.size:
        return np.arange(scores.size)
    if k <= 0:
        return np.array([], dtype=np.int64)
    idx = np.argpartition(scores, -k)[-k:]
    return idx[np.argsort(scores[idx])[::-1]]


def weighted_sample_without_replacement(rng: np.random.Generator, weights: np.ndarray, k: int) -> np.ndarray:
    weights = np.maximum(weights, 0).astype(np.float64) + 1e-12
    k = min(k, weights.size)
    if k <= 0:
        return np.array([], dtype=np.int64)
    # Gumbel top-k trick.
    g = -np.log(-np.log(rng.random(weights.size) + 1e-12) + 1e-12)
    score = np.log(weights) + g
    return topk(score, k)


def make_problem(seed: int, n_tokens: int, n_segments: int, critical_rate: float, value_boost: float, attention_noise: float) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    segment = np.repeat(np.arange(n_segments), int(np.ceil(n_tokens / n_segments)))[:n_tokens]
    attention = rng.gamma(shape=1.4, scale=1.0, size=n_tokens).astype(np.float64)
    value_norm = rng.lognormal(mean=0.0, sigma=0.45, size=n_tokens).astype(np.float64)
    n_critical = max(1, int(n_tokens * critical_rate))
    critical = np.zeros(n_tokens, dtype=bool)
    # Critical tokens are segment-balanced but attention-quiet.
    choices = []
    for s in range(n_segments):
        idx = np.where(segment == s)[0]
        if idx.size:
            choices.append(int(rng.choice(idx)))
    while len(choices) < n_critical:
        choices.append(int(rng.integers(0, n_tokens)))
    choices = np.array(sorted(set(choices))[:n_critical], dtype=np.int64)
    critical[choices] = True
    value_norm[critical] *= value_boost
    attention[critical] *= attention_noise
    recurrence = rng.random(n_tokens)
    recurrence[critical] += 2.0
    return {'segment': segment, 'attention': attention, 'value_norm': value_norm, 'critical': critical, 'recurrence': recurrence}


def retain(problem: Dict[str, np.ndarray], budget: int, policy: str, rng: np.random.Generator, protect_fraction: float) -> np.ndarray:
    attention = problem['attention']
    value_norm = problem['value_norm']
    n = attention.size
    retained = np.zeros(n, dtype=bool)
    if policy == 'attention_topk':
        retained[topk(attention, budget)] = True
    elif policy == 'value_norm_topk':
        retained[topk(value_norm, budget)] = True
    elif policy == 'stochastic_attention':
        retained[weighted_sample_without_replacement(rng, attention, budget)] = True
    elif policy == 'diverse_segment_topk':
        segment = problem['segment']
        segs = np.unique(segment)
        quota = max(1, budget // max(1, len(segs)))
        for s in segs:
            idx = np.where(segment == s)[0]
            retained[idx[topk(attention[idx], quota)]] = True
        if retained.sum() < budget:
            fill = attention.copy(); fill[retained] = -np.inf
            retained[topk(fill, budget - int(retained.sum()))] = True
        elif retained.sum() > budget:
            keep = topk(attention * retained, budget)
            retained[:] = False; retained[keep] = True
    elif policy == 'vase_toy':
        protected_budget = max(1, int(round(budget * protect_fraction)))
        protect = topk(value_norm, protected_budget)
        retained[protect] = True
        left = budget - int(retained.sum())
        if left > 0:
            weights = attention.copy()
            # Encourage diversity and do not resample protected tokens.
            weights[retained] = 0
            segment = problem['segment']
            seg_counts = np.bincount(segment[retained], minlength=int(segment.max()) + 1)
            weights = weights / (1.0 + seg_counts[segment])
            retained[weighted_sample_without_replacement(rng, weights, left)] = True
    elif policy == 'critical_oracle':
        critical = problem['critical']
        crit_idx = np.where(critical)[0]
        retained[crit_idx[topk(value_norm[crit_idx], min(budget, crit_idx.size))]] = True
        if retained.sum() < budget:
            fill = attention.copy(); fill[retained] = -np.inf
            retained[topk(fill, budget - int(retained.sum()))] = True
    else:
        raise ValueError(policy)
    return retained


def run(args) -> Dict[str, object]:
    budgets = [int(x) for x in args.budgets.split(',')]
    policies = ['attention_topk', 'value_norm_topk', 'stochastic_attention', 'diverse_segment_topk', 'vase_toy', 'critical_oracle']
    rows: List[Dict[str, object]] = []
    for seed in range(args.seeds):
        problem = make_problem(seed, args.n_tokens, args.n_segments, args.critical_rate, args.value_boost, args.critical_attention_noise)
        for budget in budgets:
            for policy in policies:
                rng = np.random.default_rng(seed * 1009 + budget * 17 + len(policy))
                retained = retain(problem, budget, policy, rng, args.protect_fraction)
                critical = problem['critical']
                segment = problem['segment']
                critical_segments = set(segment[critical].tolist())
                kept_critical_segments = set(segment[retained & critical].tolist())
                rows.append({
                    'seed': seed,
                    'budget': budget,
                    'policy': policy,
                    'critical_retention_rate': float(np.sum(retained & critical) / max(1, np.sum(critical))),
                    'all_critical_retained': float(np.all(retained[critical])),
                    'critical_segment_coverage': float(len(kept_critical_segments) / max(1, len(critical_segments))),
                    'mean_value_norm_retained': float(np.mean(problem['value_norm'][retained])) if retained.any() else 0.0,
                    'segment_diversity': float(len(np.unique(segment[retained])) / args.n_segments) if retained.any() else 0.0,
                })
    aggregate = []
    for policy in policies:
        for budget in budgets:
            rs = [r for r in rows if r['policy'] == policy and r['budget'] == budget]
            aggregate.append({
                'policy': policy,
                'budget': budget,
                'n': len(rs),
                'critical_retention_rate_mean': float(np.mean([r['critical_retention_rate'] for r in rs])),
                'all_critical_retained_rate': float(np.mean([r['all_critical_retained'] for r in rs])),
                'critical_segment_coverage_mean': float(np.mean([r['critical_segment_coverage'] for r in rs])),
                'segment_diversity_mean': float(np.mean([r['segment_diversity'] for r in rs])),
            })
    return {'probe': 'value_outlier_eviction', 'note': 'Synthetic value-outlier retention and diversity probe.', 'config': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}, 'aggregate': aggregate, 'rows': rows}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true')
    p.add_argument('--out', type=Path, default=Path('value-outlier-output.json'))
    p.add_argument('--csv', type=Path, default=None)
    p.add_argument('--seeds', type=int, default=40)
    p.add_argument('--n-tokens', type=int, default=2048)
    p.add_argument('--n-segments', type=int, default=16)
    p.add_argument('--critical-rate', type=float, default=0.006)
    p.add_argument('--value-boost', type=float, default=18.0)
    p.add_argument('--critical-attention-noise', type=float, default=0.05)
    p.add_argument('--budgets', type=str, default='16,32,64,128')
    p.add_argument('--protect-fraction', type=float, default=0.35)
    args = p.parse_args()
    if args.quick:
        args.seeds = min(args.seeds, 12)
        args.n_tokens = 1024
        args.n_segments = 12
        args.budgets = '16,32,64'
    result = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open('w', newline='', encoding='utf-8') as f:
            if result['rows']:
                w = csv.DictWriter(f, fieldnames=list(result['rows'][0].keys()))
                w.writeheader(); w.writerows(result['rows'])
    print(f"wrote {args.out} with {len(result['rows'])} rows")


if __name__ == '__main__':
    main()
