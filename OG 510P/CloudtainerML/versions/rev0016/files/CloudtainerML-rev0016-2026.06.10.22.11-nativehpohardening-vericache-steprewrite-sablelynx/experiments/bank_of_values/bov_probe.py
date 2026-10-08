#!/usr/bin/env python3
"""Bank-of-Values toy probe.

Question: When do context-free token/value lookup vectors help attention preserve
identity better than residual-stream-derived context-dependent values?

The probe creates synthetic attention lookups. Keys identify the target token.
Values are either:
  * ctx_value: token identity plus context drift/noise/scrambling,
  * bank_value: static token lookup vector,
  * hybrid: learned-ish convex mix of bank and context values.
Two tasks are measured:
  * identity_recall: retrieve the target token's stable identity vector.
  * context_attribute: retrieve a contextual attribute that only ctx_value carries.
This is not a reproduction of BoV; it is a falsifier harness for the intuition.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass
class Row:
    seed: int
    seq_len: int
    dim: int
    target: int
    context_noise: float
    context_signal: float
    attention_temp: float
    method: str
    identity_cosine: float
    identity_mse: float
    context_cosine: float
    context_mse: float
    attention_entropy: float
    max_attention: float


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8))


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / np.sum(e)


def one_trial(seed: int, seq_len: int, dim: int, context_noise: float, context_signal: float, attention_temp: float) -> list[Row]:
    rng = np.random.default_rng(seed)
    # Token lookup table: stable token identity / original-token memory.
    bank = l2norm(rng.normal(size=(seq_len, dim)))

    # Key space is close to identity vectors but not identical. Query points to target.
    keys = l2norm(bank + 0.12 * rng.normal(size=(seq_len, dim)))
    target = int(rng.integers(0, seq_len))
    query = l2norm(keys[target] + 0.08 * rng.normal(size=dim))
    logits = (keys @ query) / max(attention_temp, 1e-6)
    weights = softmax(logits)

    # Context features represent residual-stream information that may be useful for a
    # context_attribute task but can also drift away from token identity.
    attr_basis = l2norm(rng.normal(size=(seq_len, dim)))
    context_values = bank + context_signal * attr_basis + context_noise * rng.normal(size=(seq_len, dim))
    context_values = l2norm(context_values)

    # Oracle targets for the two tasks.
    identity_target = bank[target]
    context_target = l2norm(bank[target] + context_signal * attr_basis[target])

    methods = {
        'ctx_value_only': context_values,
        'bank_value_only': bank,
        'hybrid_25_bank': l2norm(0.25 * bank + 0.75 * context_values),
        'hybrid_50_bank': l2norm(0.50 * bank + 0.50 * context_values),
        'hybrid_75_bank': l2norm(0.75 * bank + 0.25 * context_values),
    }

    rows = []
    entropy = float(-np.sum(weights * np.log(weights + 1e-12)))
    max_attn = float(np.max(weights))
    for method, values in methods.items():
        out = weights @ values
        rows.append(Row(
            seed=seed,
            seq_len=seq_len,
            dim=dim,
            target=target,
            context_noise=context_noise,
            context_signal=context_signal,
            attention_temp=attention_temp,
            method=method,
            identity_cosine=cosine(out, identity_target),
            identity_mse=float(np.mean((out - identity_target) ** 2)),
            context_cosine=cosine(out, context_target),
            context_mse=float(np.mean((out - context_target) ** 2)),
            attention_entropy=entropy,
            max_attention=max_attn,
        ))
    return rows


def summarize(rows: list[Row]) -> dict:
    methods = sorted(set(r.method for r in rows))
    summary = {'rows': len(rows), 'methods': {}}
    for m in methods:
        subset = [r for r in rows if r.method == m]
        summary['methods'][m] = {
            'identity_cosine_mean': float(np.mean([r.identity_cosine for r in subset])),
            'context_cosine_mean': float(np.mean([r.context_cosine for r in subset])),
            'identity_mse_mean': float(np.mean([r.identity_mse for r in subset])),
            'context_mse_mean': float(np.mean([r.context_mse for r in subset])),
        }
    # Who wins each task by mean cosine?
    summary['identity_winner'] = max(methods, key=lambda m: summary['methods'][m]['identity_cosine_mean'])
    summary['context_winner'] = max(methods, key=lambda m: summary['methods'][m]['context_cosine_mean'])
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('artifacts/probe-results/REV0006_BANK_OF_VALUES_SMOKE'))
    ap.add_argument('--seeds', type=int, default=24)
    ap.add_argument('--seq-len', type=int, default=96)
    ap.add_argument('--dim', type=int, default=48)
    ap.add_argument('--attention-temp', type=float, default=0.16)
    args = ap.parse_args()

    rows: list[Row] = []
    noises = [0.0, 0.1, 0.25, 0.5, 1.0]
    signals = [0.0, 0.25, 0.75, 1.5]
    for seed in range(args.seeds):
        for noise in noises:
            for signal in signals:
                rows.extend(one_trial(seed, args.seq_len, args.dim, noise, signal, args.attention_temp))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix('.csv')
    json_path = args.out.with_suffix('.json')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))
    summary = summarize(rows)
    summary.update({
        'probe': 'bank_of_values',
        'csv': str(csv_path),
        'interpretation': 'BoV-like static values should win identity preservation when context drift/noise is high; context values should win when the requested attribute is truly contextual.',
    })
    json_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
