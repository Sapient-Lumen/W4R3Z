#!/usr/bin/env python3
"""Spectral/linear associative recall probe.

This is a tiny geometry battery for asking when compressed memories can perform
content-addressed retrieval without storing an explicit full cache.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np


def normalize_rows(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def make_problem(seed: int, n_items: int, d_key: int, d_val: int, correlation: float, query_noise: float):
    rng = np.random.default_rng(seed)
    shared = rng.normal(size=(1, d_key)).astype(np.float32)
    unique = rng.normal(size=(n_items, d_key)).astype(np.float32)
    keys = normalize_rows(correlation * shared + math.sqrt(max(1e-6, 1 - correlation ** 2)) * unique)
    values = normalize_rows(rng.normal(size=(n_items, d_val)).astype(np.float32))
    q = normalize_rows(keys + query_noise * rng.normal(size=keys.shape).astype(np.float32))
    return keys, values, q


def top1_from_values(pred: np.ndarray, values: np.ndarray) -> np.ndarray:
    scores = pred @ values.T
    return np.argmax(scores, axis=1)


def exact_attention(keys, values, queries, temperature=24.0):
    logits = temperature * (queries @ keys.T)
    logits = logits - logits.max(axis=1, keepdims=True)
    w = np.exp(logits)
    w = w / (w.sum(axis=1, keepdims=True) + 1e-12)
    return w @ values


def additive_memory(keys, values, queries):
    # Simple linear associative memory. Crosstalk grows when keys are correlated.
    mem = keys.T @ values
    pred = queries @ mem
    return pred


def ridge_memory(keys, values, queries, ridge=1e-2, rank=None):
    d = keys.shape[1]
    gram = keys.T @ keys + ridge * np.eye(d, dtype=np.float32)
    w = np.linalg.solve(gram, keys.T @ values)
    if rank is not None and rank < min(w.shape):
        u, s, vt = np.linalg.svd(w, full_matrices=False)
        w = (u[:, :rank] * s[:rank]) @ vt[:rank, :]
    return queries @ w


def online_delta_memory(keys, values, queries, eta=0.7):
    d_key, d_val = keys.shape[1], values.shape[1]
    w = np.zeros((d_key, d_val), dtype=np.float32)
    for k, v in zip(keys, values):
        pred = k @ w
        w += eta * np.outer(k, v - pred).astype(np.float32)
    return queries @ w


def score_method(name: str, pred: np.ndarray, values: np.ndarray) -> Dict[str, float]:
    got = top1_from_values(pred, values)
    target = np.arange(values.shape[0])
    mse = np.mean((pred - values) ** 2)
    margin_scores = pred @ values.T
    sorted_scores = np.sort(margin_scores, axis=1)
    margin = sorted_scores[:, -1] - sorted_scores[:, -2]
    return {
        'method': name,
        'top1_accuracy': float(np.mean(got == target)),
        'value_mse': float(mse),
        'mean_top_margin': float(np.mean(margin)),
    }


def run_trial(seed: int, n_items: int, d_key: int, d_val: int, correlation: float, query_noise: float, ranks: List[int]):
    keys, values, queries = make_problem(seed, n_items, d_key, d_val, correlation, query_noise)
    rows = []
    methods = {
        'exact_attention': exact_attention(keys, values, queries),
        'additive_linear': additive_memory(keys, values, queries),
        'ridge_full': ridge_memory(keys, values, queries, ridge=1e-2, rank=None),
        'online_delta': online_delta_memory(keys, values, queries),
    }
    for r in ranks:
        methods[f'ridge_rank_{r}'] = ridge_memory(keys, values, queries, ridge=1e-2, rank=r)
    for name, pred in methods.items():
        row = {
            'seed': seed,
            'n_items': n_items,
            'd_key': d_key,
            'd_val': d_val,
            'correlation': correlation,
            'query_noise': query_noise,
        }
        row.update(score_method(name, pred, values))
        if name.startswith('ridge_rank_'):
            row['memory_rank'] = int(name.split('_')[-1])
        elif name == 'ridge_full':
            row['memory_rank'] = min(d_key, d_val)
        elif name == 'exact_attention':
            row['memory_rank'] = n_items
        else:
            row['memory_rank'] = min(d_key, d_val)
        rows.append(row)
    return rows


def aggregate(rows):
    grouped = {}
    for r in rows:
        key = (r['method'], r['n_items'], r['correlation'], r['query_noise'], r['memory_rank'])
        grouped.setdefault(key, []).append(r)
    out = []
    for (method, n_items, corr, noise, rank), rs in grouped.items():
        out.append({
            'method': method,
            'n_items': n_items,
            'correlation': corr,
            'query_noise': noise,
            'memory_rank': rank,
            'n': len(rs),
            'top1_accuracy_mean': float(np.mean([r['top1_accuracy'] for r in rs])),
            'value_mse_mean': float(np.mean([r['value_mse'] for r in rs])),
            'mean_top_margin_mean': float(np.mean([r['mean_top_margin'] for r in rs])),
        })
    out.sort(key=lambda r: (r['n_items'], r['correlation'], r['method'], r['memory_rank']))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true')
    p.add_argument('--out', type=Path, default=Path('spectral-assoc-output.json'))
    p.add_argument('--csv', type=Path, default=None)
    p.add_argument('--seeds', type=int, default=5)
    args = p.parse_args()
    seeds = range(min(args.seeds, 3) if args.quick else args.seeds)
    n_items_list = [32, 96] if args.quick else [32, 64, 128, 256]
    correlations = [0.0, 0.75] if args.quick else [0.0, 0.4, 0.75, 0.9]
    query_noises = [0.05, 0.2] if args.quick else [0.02, 0.05, 0.15, 0.3]
    ranks = [4, 8, 16]
    rows = []
    for seed in seeds:
        for n_items in n_items_list:
            for corr in correlations:
                for noise in query_noises:
                    rows.extend(run_trial(seed, n_items, d_key=32, d_val=32, correlation=corr, query_noise=noise, ranks=ranks))
    result = {
        'probe': 'spectral_assoc_recall',
        'note': 'Synthetic continuous associative recall; not a faithful implementation of a named architecture.',
        'config': {'quick': args.quick, 'seeds': len(list(seeds)), 'n_items_list': n_items_list, 'correlations': correlations, 'query_noises': query_noises, 'ranks': ranks},
        'aggregate': aggregate(rows),
        'rows': rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    if args.csv:
        import csv
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f'wrote {args.out} with {len(rows)} rows')


if __name__ == '__main__':
    main()
