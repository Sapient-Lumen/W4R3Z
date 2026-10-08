#!/usr/bin/env python3
"""Region-wipeout cache retention probe.

This is a symbolic/tensor proxy for the failure mode described by region-aware
KV cache papers: token-level top-k competition can keep high-scoring tokens from
one currently salient region while deleting entire earlier reasoning regions.

The simulator creates a long context divided into regions. Each region contains
vital tokens that will be needed at the final query. Decode-time attention mass
moves through regions with jitter. Policies compress the cache to K tokens. A
trial succeeds only if every required region retains at least one vital token.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    z = x - np.max(x)
    e = np.exp(z)
    return e / (np.sum(e) + 1e-12)


def topk_indices(scores: np.ndarray, k: int) -> np.ndarray:
    if k >= scores.size:
        return np.arange(scores.size)
    if k <= 0:
        return np.array([], dtype=np.int64)
    idx = np.argpartition(scores, -k)[-k:]
    return idx[np.argsort(scores[idx])[::-1]]


def allocate_quota(mass: np.ndarray, budget: int, min_quota: int) -> np.ndarray:
    n = mass.size
    if budget <= 0:
        return np.zeros(n, dtype=np.int64)
    quota = np.zeros(n, dtype=np.int64)
    if budget >= n * min_quota:
        quota[:] = min_quota
        rem = budget - int(quota.sum())
    else:
        chosen = topk_indices(mass, budget)
        quota[chosen] = 1
        return quota
    if rem <= 0:
        return quota
    frac = mass / (mass.sum() + 1e-12)
    raw = frac * rem
    add = np.floor(raw).astype(np.int64)
    quota += add
    spare = budget - int(quota.sum())
    if spare > 0:
        order = np.argsort(raw - add)[::-1]
        quota[order[:spare]] += 1
    return quota


def make_trial(seed: int, n_regions: int, tokens_per_region: int, vital_per_region: int, steps: int, jitter: float, focus_strength: float) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = n_regions * tokens_per_region
    region = np.repeat(np.arange(n_regions), tokens_per_region)
    pos_in_region = np.tile(np.arange(tokens_per_region), n_regions)

    # Vital tokens are spread inside each region; they are the proof-state/evidence
    # that later queries require. Their direct scores are not always dominant.
    vital_mask = np.zeros(n, dtype=bool)
    for r in range(n_regions):
        start = r * tokens_per_region
        choices = rng.choice(tokens_per_region, size=vital_per_region, replace=False)
        vital_mask[start + choices] = True

    # A moving decode focus: mass concentrates on a few current regions, then drifts.
    # This makes global top-k vulnerable to wiping out older/quiet regions.
    cumulative_region_mass = np.zeros(n_regions, dtype=np.float64)
    ema_region_mass = np.ones(n_regions, dtype=np.float64) / n_regions
    ema_alpha = 0.72
    for t in range(steps):
        center = int(np.floor((t / max(1, steps - 1)) * (n_regions - 1)))
        dist = np.abs(np.arange(n_regions) - center)
        logits = -0.9 * dist + rng.normal(0, jitter, size=n_regions)
        logits[center] += focus_strength
        step_mass = softmax(logits)
        cumulative_region_mass += step_mass
        ema_region_mass = ema_alpha * ema_region_mass + (1 - ema_alpha) * step_mass

    cumulative_region_mass /= max(1, steps)
    # Token scores have region mass, local salience, recency-ish local bias, and noise.
    local_salience = rng.lognormal(mean=0.0, sigma=0.6, size=n)
    local_salience *= 1.0 + 0.05 * (pos_in_region / max(1, tokens_per_region - 1))
    scores = cumulative_region_mass[region] * local_salience
    scores += 0.015 * rng.random(n)
    scores[vital_mask] *= rng.uniform(4.0, 6.0, size=vital_mask.sum())
    recency = region + 0.02 * pos_in_region

    return {
        'region': region,
        'vital_mask': vital_mask,
        'scores': scores.astype(np.float64),
        'recency': recency.astype(np.float64),
        'ema_region_mass': ema_region_mass.astype(np.float64),
        'cumulative_region_mass': cumulative_region_mass.astype(np.float64),
    }


def retain_by_policy(problem: Dict[str, np.ndarray], budget: int, policy: str, n_regions: int) -> np.ndarray:
    scores = problem['scores']
    region = problem['region']
    vital = problem['vital_mask']
    retained = np.zeros(scores.size, dtype=bool)
    if policy == 'global_topk':
        retained[topk_indices(scores, budget)] = True
    elif policy == 'recency_topk':
        retained[topk_indices(problem['recency'], budget)] = True
    elif policy == 'even_region_quota':
        quota = np.zeros(n_regions, dtype=np.int64)
        base = budget // n_regions
        quota[:] = base
        quota[: budget - base * n_regions] += 1
        for r, q in enumerate(quota):
            idx = np.where(region == r)[0]
            retained[idx[topk_indices(scores[idx], int(q))]] = True
    elif policy == 'mass_segmented':
        quota = allocate_quota(problem['ema_region_mass'], budget, min_quota=1)
        for r, q in enumerate(quota):
            idx = np.where(region == r)[0]
            retained[idx[topk_indices(scores[idx], int(q))]] = True
    elif policy == 'vital_oracle':
        # Upper bound: keep vital tokens first, then fill by score.
        vital_idx = np.where(vital)[0]
        if vital_idx.size <= budget:
            retained[vital_idx] = True
            left = budget - vital_idx.size
            if left > 0:
                filler_scores = scores.copy()
                filler_scores[retained] = -np.inf
                retained[topk_indices(filler_scores, left)] = True
        else:
            # If budget cannot hold all vital tokens, keep one per region when possible.
            chosen = []
            for r in range(n_regions):
                idx = np.where((region == r) & vital)[0]
                if idx.size:
                    chosen.append(idx[np.argmax(scores[idx])])
            chosen = np.array(chosen[:budget], dtype=np.int64)
            retained[chosen] = True
    else:
        raise ValueError(f'unknown policy: {policy}')
    return retained


def score_retention(problem: Dict[str, np.ndarray], retained: np.ndarray, n_regions: int) -> Dict[str, float]:
    region = problem['region']
    vital = problem['vital_mask']
    vital_regions = []
    retained_regions = []
    for r in range(n_regions):
        has_vital = bool(np.any(vital[region == r]))
        has_retained_vital = bool(np.any(vital[retained & (region == r)]))
        if has_vital:
            vital_regions.append(r)
            if has_retained_vital:
                retained_regions.append(r)
    coverage = len(retained_regions) / max(1, len(vital_regions))
    empty_regions = sum(1 for r in range(n_regions) if not np.any(retained[region == r]))
    return {
        'all_required_regions_retained': float(coverage == 1.0),
        'required_region_coverage': float(coverage),
        'empty_region_fraction': float(empty_regions / n_regions),
        'retained_vital_fraction': float(np.sum(retained & vital) / max(1, np.sum(vital))),
    }


def run(args) -> Dict[str, object]:
    budgets = [int(x) for x in args.budgets.split(',')]
    policies = ['global_topk', 'recency_topk', 'even_region_quota', 'mass_segmented', 'vital_oracle']
    rows: List[Dict[str, object]] = []
    for seed in range(args.seeds):
        for n_regions in args.regions:
            for budget in budgets:
                problem = make_trial(
                    seed=seed,
                    n_regions=n_regions,
                    tokens_per_region=args.tokens_per_region,
                    vital_per_region=args.vital_per_region,
                    steps=args.steps,
                    jitter=args.jitter,
                    focus_strength=args.focus_strength,
                )
                for policy in policies:
                    retained = retain_by_policy(problem, budget, policy, n_regions)
                    row = {
                        'seed': seed,
                        'n_regions': n_regions,
                        'tokens_per_region': args.tokens_per_region,
                        'vital_per_region': args.vital_per_region,
                        'steps': args.steps,
                        'budget': budget,
                        'policy': policy,
                    }
                    row.update(score_retention(problem, retained, n_regions))
                    rows.append(row)
    aggregate = []
    keys = sorted({(r['policy'], r['n_regions'], r['budget']) for r in rows})
    for policy, n_regions, budget in keys:
        rs = [r for r in rows if r['policy'] == policy and r['n_regions'] == n_regions and r['budget'] == budget]
        aggregate.append({
            'policy': policy,
            'n_regions': n_regions,
            'budget': budget,
            'n': len(rs),
            'success_rate': float(np.mean([r['all_required_regions_retained'] for r in rs])),
            'coverage_mean': float(np.mean([r['required_region_coverage'] for r in rs])),
            'empty_region_fraction_mean': float(np.mean([r['empty_region_fraction'] for r in rs])),
            'retained_vital_fraction_mean': float(np.mean([r['retained_vital_fraction'] for r in rs])),
        })
    return {
        'probe': 'region_wipeout_cache',
        'note': 'Symbolic proxy for region wipe-out; success requires at least one vital token from every required region.',
        'config': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
        'aggregate': aggregate,
        'rows': rows,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true')
    p.add_argument('--out', type=Path, default=Path('region-wipeout-output.json'))
    p.add_argument('--csv', type=Path, default=None)
    p.add_argument('--seeds', type=int, default=25)
    p.add_argument('--budgets', type=str, default='8,16,32,64')
    p.add_argument('--regions', type=int, nargs='*', default=[6, 10])
    p.add_argument('--tokens-per-region', type=int, default=64)
    p.add_argument('--vital-per-region', type=int, default=2)
    p.add_argument('--steps', type=int, default=48)
    p.add_argument('--jitter', type=float, default=0.55)
    p.add_argument('--focus-strength', type=float, default=1.4)
    args = p.parse_args()
    if args.quick:
        args.seeds = min(args.seeds, 8)
        args.budgets = '8,16,32'
        args.regions = [6, 10]
        args.tokens_per_region = 48
        args.steps = 32
    result = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open('w', newline='', encoding='utf-8') as f:
            if result['rows']:
                w = csv.DictWriter(f, fieldnames=list(result['rows'][0].keys()))
                w.writeheader()
                w.writerows(result['rows'])
    print(f"wrote {args.out} with {len(result['rows'])} rows")


if __name__ == '__main__':
    main()
