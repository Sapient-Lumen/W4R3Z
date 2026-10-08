#!/usr/bin/env python3
"""Dormant-token sponsorship probe.

A symbolic proxy for semantic sponsorship / transactional attention. Values such
as credentials, IDs, constants, or config strings can receive near-zero direct
attention for a long time, then become essential. Pure score-based eviction has
no reason to keep them. Sponsorship keeps value-bearing neighbors when an anchor
pattern is retained or detected.
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


def make_context(seed: int, n_tokens: int, n_pairs: int, distractor_anchor_rate: float, value_attention: float) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    # token types: 0 ordinary, 1 anchor, 2 value, 3 distractor-anchor
    typ = np.zeros(n_tokens, dtype=np.int64)
    occupied = np.zeros(n_tokens, dtype=bool)
    candidate = np.arange(2, n_tokens - 2)
    anchors = []
    for _ in range(n_pairs):
        available = candidate[~occupied[candidate] & ~occupied[candidate + 1]]
        if available.size == 0:
            break
        a = int(rng.choice(available))
        typ[a] = 1
        typ[a + 1] = 2
        occupied[a] = occupied[a + 1] = True
        anchors.append(a)
    anchors = np.array(sorted(anchors), dtype=np.int64)
    n_distractors = int(distractor_anchor_rate * n_tokens)
    free = np.where(~occupied)[0]
    if free.size:
        d = rng.choice(free, size=min(n_distractors, free.size), replace=False)
        typ[d] = 3

    target_anchor = int(rng.choice(anchors)) if anchors.size else -1
    target_value = target_anchor + 1 if target_anchor >= 0 else -1

    # Attention-like scores: anchors get some structural score, values remain dormant.
    attention = rng.exponential(scale=1.0, size=n_tokens).astype(np.float64)
    attention[typ == 1] += rng.uniform(0.4, 1.1, size=np.sum(typ == 1))
    attention[typ == 3] += rng.uniform(0.2, 0.8, size=np.sum(typ == 3))
    attention[typ == 2] = value_attention * rng.uniform(0.5, 1.5, size=np.sum(typ == 2))
    # Recency proxy.
    recency = np.linspace(0.0, 1.0, n_tokens)
    return {
        'typ': typ,
        'anchors': anchors,
        'target_anchor': np.array([target_anchor], dtype=np.int64),
        'target_value': np.array([target_value], dtype=np.int64),
        'attention': attention,
        'recency': recency,
    }


def retain(problem: Dict[str, np.ndarray], budget: int, policy: str, sponsor_window: int, sponsor_false_positive: float, rng: np.random.Generator) -> np.ndarray:
    typ = problem['typ']
    n = typ.size
    attention = problem['attention']
    retained = np.zeros(n, dtype=bool)
    if policy == 'attention_topk':
        retained[topk(attention, budget)] = True
    elif policy == 'recency_topk':
        retained[topk(problem['recency'], budget)] = True
    elif policy == 'anchor_only':
        anchor_score = attention.copy()
        anchor_score[typ == 1] += 2.0
        retained[topk(anchor_score, budget)] = True
    elif policy == 'semantic_sponsor':
        sponsored = np.zeros(n, dtype=bool)
        anchors = np.where(typ == 1)[0]
        for a in anchors:
            lo, hi = max(0, a), min(n, a + sponsor_window + 1)
            sponsored[lo:hi] = True
        # Some distractors look like anchors; this tests sponsorship overhead.
        false = np.where(typ == 3)[0]
        if false.size and sponsor_false_positive > 0:
            chosen = false[rng.random(false.size) < sponsor_false_positive]
            for a in chosen:
                lo, hi = max(0, a), min(n, a + sponsor_window + 1)
                sponsored[lo:hi] = True
        sponsor_idx = np.where(sponsored)[0]
        # Prefer true anchors and values, then high attention filler.
        sponsor_priority = attention[sponsor_idx].copy()
        sponsor_priority[typ[sponsor_idx] == 1] += 4.0
        sponsor_priority[typ[sponsor_idx] == 2] += 4.0
        first = sponsor_idx[topk(sponsor_priority, min(budget, sponsor_idx.size))]
        retained[first] = True
        if retained.sum() < budget:
            filler = attention.copy()
            filler[retained] = -np.inf
            retained[topk(filler, budget - int(retained.sum()))] = True
    elif policy == 'oracle_target':
        target_value = int(problem['target_value'][0])
        target_anchor = int(problem['target_anchor'][0])
        if target_anchor >= 0:
            retained[target_anchor] = True
        if target_value >= 0 and budget >= 2:
            retained[target_value] = True
        if retained.sum() < budget:
            filler = attention.copy()
            filler[retained] = -np.inf
            retained[topk(filler, budget - int(retained.sum()))] = True
    else:
        raise ValueError(policy)
    return retained


def run(args) -> Dict[str, object]:
    budgets = [int(x) for x in args.budgets.split(',')]
    policies = ['attention_topk', 'recency_topk', 'anchor_only', 'semantic_sponsor', 'oracle_target']
    rows: List[Dict[str, object]] = []
    for seed in range(args.seeds):
        rng = np.random.default_rng(seed + 1000)
        problem = make_context(seed, args.n_tokens, args.n_pairs, args.distractor_anchor_rate, args.value_attention)
        target_value = int(problem['target_value'][0])
        for budget in budgets:
            for policy in policies:
                retained = retain(problem, budget, policy, args.sponsor_window, args.sponsor_false_positive, rng)
                typ = problem['typ']
                rows.append({
                    'seed': seed,
                    'budget': budget,
                    'policy': policy,
                    'target_value_retained': float(target_value >= 0 and bool(retained[target_value])),
                    'target_anchor_retained': float(int(problem['target_anchor'][0]) >= 0 and bool(retained[int(problem['target_anchor'][0])])),
                    'any_value_retained_fraction': float(np.sum(retained & (typ == 2)) / max(1, np.sum(typ == 2))),
                    'anchor_retained_fraction': float(np.sum(retained & (typ == 1)) / max(1, np.sum(typ == 1))),
                    'ordinary_retained_fraction': float(np.sum(retained & (typ == 0)) / max(1, np.sum(typ == 0))),
                    'retained_count': int(retained.sum()),
                })
    aggregate = []
    for policy in policies:
        for budget in budgets:
            rs = [r for r in rows if r['policy'] == policy and r['budget'] == budget]
            aggregate.append({
                'policy': policy,
                'budget': budget,
                'n': len(rs),
                'target_value_retention_rate': float(np.mean([r['target_value_retained'] for r in rs])),
                'target_anchor_retention_rate': float(np.mean([r['target_anchor_retained'] for r in rs])),
                'value_retained_fraction_mean': float(np.mean([r['any_value_retained_fraction'] for r in rs])),
                'anchor_retained_fraction_mean': float(np.mean([r['anchor_retained_fraction'] for r in rs])),
                'ordinary_retained_fraction_mean': float(np.mean([r['ordinary_retained_fraction'] for r in rs])),
            })
    return {
        'probe': 'dormant_sponsorship',
        'note': 'Synthetic dormant-token retention; semantic_sponsor protects value-bearing neighbors of anchors.',
        'config': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
        'aggregate': aggregate,
        'rows': rows,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true')
    p.add_argument('--out', type=Path, default=Path('dormant-sponsorship-output.json'))
    p.add_argument('--csv', type=Path, default=None)
    p.add_argument('--seeds', type=int, default=50)
    p.add_argument('--n-tokens', type=int, default=4096)
    p.add_argument('--n-pairs', type=int, default=20)
    p.add_argument('--budgets', type=str, default='8,16,32,64,128')
    p.add_argument('--distractor-anchor-rate', type=float, default=0.015)
    p.add_argument('--value-attention', type=float, default=1e-4)
    p.add_argument('--sponsor-window', type=int, default=1)
    p.add_argument('--sponsor-false-positive', type=float, default=0.15)
    args = p.parse_args()
    if args.quick:
        args.seeds = min(args.seeds, 16)
        args.n_tokens = 2048
        args.n_pairs = 12
        args.budgets = '8,16,32,64'
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
