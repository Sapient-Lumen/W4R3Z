#!/usr/bin/env python3
"""KV Wind Tunnel: tiny pseudo-decode probe for KV-cache quantization.

This is not a faithful implementation of any specific paper. It is a small,
reproducible stress harness for asking whether quantization errors that look
small in a static cache can accumulate when attention outputs feed future
queries.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-12)


def normalize(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x) + eps)


def fwht_last_axis(x: np.ndarray) -> np.ndarray:
    """Fast Walsh-Hadamard transform over the last axis, normalized."""
    y = np.array(x, dtype=np.float32, copy=True)
    n = y.shape[-1]
    if n & (n - 1):
        raise ValueError('Hadamard rotation requires power-of-two last dimension')
    h = 1
    while h < n:
        y = y.reshape(*y.shape[:-1], n // (2 * h), 2, h)
        a = y[..., 0, :].copy()
        b = y[..., 1, :].copy()
        y[..., 0, :] = a + b
        y[..., 1, :] = a - b
        y = y.reshape(*y.shape[:-3], n)
        h *= 2
    return y / math.sqrt(n)


def symmetric_quantize(x: np.ndarray, bits: int, axis=None, eps: float = 1e-8) -> np.ndarray:
    if bits >= 32:
        return x.astype(np.float32, copy=True)
    qmax = (2 ** (bits - 1)) - 1
    if qmax <= 0:
        raise ValueError('bits must be >= 2 for signed symmetric quantization')
    scale = np.max(np.abs(x), axis=axis, keepdims=True) / qmax
    scale = np.maximum(scale, eps)
    q = np.round(x / scale)
    q = np.clip(q, -qmax, qmax)
    return (q * scale).astype(np.float32)


def variance_normalized_quantize(x: np.ndarray, bits: int) -> np.ndarray:
    """Crude two-axis variance normalization, then global quantization.

    This is only an approximation to the *shape* of variance-normalized cache
    quantization ideas: tame row/token and column/channel scale before low-bit
    quantization, then invert the scaling.
    """
    eps = 1e-6
    row = np.sqrt(np.mean(x * x, axis=1, keepdims=True) + eps)
    x1 = x / row
    col = np.sqrt(np.mean(x1 * x1, axis=0, keepdims=True) + eps)
    x2 = x1 / col
    q = symmetric_quantize(x2, bits=bits, axis=None)
    return (q * col * row).astype(np.float32)


def quantize_variant(x: np.ndarray, variant: str, bits: int) -> np.ndarray:
    if variant == 'fp32':
        return x.astype(np.float32, copy=True)
    if variant == 'global':
        return symmetric_quantize(x, bits=bits, axis=None)
    if variant == 'row':
        return symmetric_quantize(x, bits=bits, axis=1)
    if variant == 'col':
        return symmetric_quantize(x, bits=bits, axis=0)
    if variant == 'varnorm':
        return variance_normalized_quantize(x, bits=bits)
    if variant == 'hadamard_global':
        y = fwht_last_axis(x)
        q = symmetric_quantize(y, bits=bits, axis=None)
        return fwht_last_axis(q).astype(np.float32)
    if variant == 'hadamard_row':
        y = fwht_last_axis(x)
        q = symmetric_quantize(y, bits=bits, axis=1)
        return fwht_last_axis(q).astype(np.float32)
    if variant == 'hadamard_varnorm':
        y = fwht_last_axis(x)
        q = variance_normalized_quantize(y, bits=bits)
        return fwht_last_axis(q).astype(np.float32)
    raise ValueError(f'unknown variant: {variant}')


def make_cache(seed: int, n_tokens: int, d_model: int, outlier_strength: float) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    k = rng.normal(0, 1, size=(n_tokens, d_model)).astype(np.float32)
    v = rng.normal(0, 1, size=(n_tokens, d_model)).astype(np.float32)
    # Make a small number of row/token-scale outliers. This stresses token-scale
    # quantization and rotation/normalization tricks.
    n_outliers = max(1, n_tokens // 16)
    idx = rng.choice(n_tokens, size=n_outliers, replace=False)
    scales = np.ones((n_tokens, 1), dtype=np.float32)
    scales[idx] = outlier_strength
    k *= scales
    v *= np.sqrt(scales)
    return k, v


def run_decode(k: np.ndarray, v: np.ndarray, seed: int, steps: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + 100_000)
    d = k.shape[1]
    # Lightweight stable-ish recurrent matrix. Avoid SVD/QR so the probe stays fast.
    wh = rng.normal(0, 1 / math.sqrt(d), size=(d, d)).astype(np.float32) * 0.92
    wo = rng.normal(0, 1 / math.sqrt(d), size=(d, d)).astype(np.float32)
    wq = rng.normal(0, 1 / math.sqrt(d), size=(d, d)).astype(np.float32)
    h = normalize(rng.normal(size=d).astype(np.float32))
    outputs = []
    attns = []
    argmaxes = []
    hs = []
    for t in range(steps):
        q = normalize(wq @ h)
        scores = (k @ q) / math.sqrt(d)
        attn = softmax(scores)
        out = attn @ v
        h = np.tanh(0.72 * (wh @ h) + 0.55 * (wo @ out)).astype(np.float32)
        outputs.append(out.astype(np.float32))
        attns.append(attn.astype(np.float32))
        argmaxes.append(int(np.argmax(attn)))
        hs.append(h.astype(np.float32))
    return {'outputs': np.stack(outputs), 'attns': np.stack(attns), 'argmaxes': np.array(argmaxes), 'hs': np.stack(hs)}


def compare(ref: Dict[str, np.ndarray], test: Dict[str, np.ndarray]) -> Dict[str, float]:
    out_err = np.linalg.norm(ref['outputs'] - test['outputs'], axis=1)
    h_err = np.linalg.norm(ref['hs'] - test['hs'], axis=1)
    tv = 0.5 * np.sum(np.abs(ref['attns'] - test['attns']), axis=1)
    arg_agree = np.mean(ref['argmaxes'] == test['argmaxes'])
    threshold = 1.0
    over = np.flatnonzero(h_err > threshold)
    return {
        'mean_output_l2': float(np.mean(out_err)),
        'max_output_l2': float(np.max(out_err)),
        'final_hidden_l2': float(h_err[-1]),
        'mean_hidden_l2': float(np.mean(h_err)),
        'mean_attention_tv': float(np.mean(tv)),
        'argmax_agreement': float(arg_agree),
        'diverged_step_hidden_l2_gt_1': int(over[0]) if len(over) else None,
    }


def static_cache_errors(k: np.ndarray, v: np.ndarray, kq: np.ndarray, vq: np.ndarray) -> Dict[str, float]:
    def rel_mse(a, b):
        return float(np.mean((a - b) ** 2) / (np.mean(a ** 2) + 1e-12))
    row_scale = np.linalg.norm(k, axis=1) + 1e-9
    row_scale_q = np.linalg.norm(kq, axis=1) + 1e-9
    scale_rel = np.abs(row_scale_q / row_scale - 1.0)
    return {
        'k_rel_mse': rel_mse(k, kq),
        'v_rel_mse': rel_mse(v, vq),
        'k_row_scale_rel_error_mean': float(np.mean(scale_rel)),
        'k_row_scale_rel_error_p95': float(np.percentile(scale_rel, 95)),
        'k_row_scale_rel_error_max': float(np.max(scale_rel)),
    }


def run_trial(seed: int, n_tokens: int, d_model: int, steps: int, outlier_strength: float, variants: Iterable[Tuple[str, int]]):
    k, v = make_cache(seed, n_tokens, d_model, outlier_strength)
    ref = run_decode(k, v, seed, steps)
    rows = []
    for variant, bits in variants:
        if variant == 'fp32':
            kq, vq = k, v
        else:
            kq = quantize_variant(k, variant, bits)
            vq = quantize_variant(v, variant, bits)
        test = run_decode(kq, vq, seed, steps)
        row = {
            'seed': seed,
            'n_tokens': n_tokens,
            'd_model': d_model,
            'steps': steps,
            'outlier_strength': outlier_strength,
            'variant': variant,
            'bits': bits,
            'approx_cache_bits_per_token': int(2 * d_model * (32 if variant == 'fp32' else bits)),
        }
        row.update(static_cache_errors(k, v, kq, vq))
        row.update(compare(ref, test))
        rows.append(row)
    return rows


def aggregate(rows):
    grouped = {}
    for r in rows:
        key = (r['variant'], r['bits'], r['outlier_strength'])
        grouped.setdefault(key, []).append(r)
    out = []
    numeric = [k for k, v in rows[0].items() if isinstance(v, (int, float)) and k not in {'seed'}]
    for (variant, bits, outlier), rs in grouped.items():
        g = {'variant': variant, 'bits': bits, 'outlier_strength': outlier, 'n': len(rs)}
        for k in numeric:
            vals = [r[k] for r in rs if r[k] is not None]
            if vals:
                g[k + '_mean'] = float(np.mean(vals))
        out.append(g)
    out.sort(key=lambda x: (x['outlier_strength'], x['bits'], x['variant']))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true', help='small run suitable for smoke tests')
    p.add_argument('--out', type=Path, default=Path('kv-wind-output.json'))
    p.add_argument('--csv', type=Path, default=None)
    p.add_argument('--seeds', type=int, default=3)
    p.add_argument('--steps', type=int, default=64)
    p.add_argument('--n-tokens', type=int, default=128)
    p.add_argument('--d-model', type=int, default=64)
    args = p.parse_args()
    if args.quick:
        args.seeds = min(args.seeds, 3)
        args.steps = min(args.steps, 48)
        args.n_tokens = min(args.n_tokens, 96)
        args.d_model = min(args.d_model, 64)
    variants = [
        ('fp32', 32),
        ('global', 4), ('row', 4), ('col', 4), ('varnorm', 4), ('hadamard_row', 4), ('hadamard_varnorm', 4),
        ('global', 2), ('row', 2), ('col', 2), ('varnorm', 2), ('hadamard_row', 2), ('hadamard_varnorm', 2),
    ]
    rows = []
    for outlier in ([1.0, 8.0] if args.quick else [1.0, 4.0, 8.0, 16.0]):
        for seed in range(args.seeds):
            rows.extend(run_trial(seed, args.n_tokens, args.d_model, args.steps, outlier, variants))
    result = {
        'probe': 'kv_wind_tunnel',
        'note': 'Synthetic pseudo-decode probe; not a faithful reproduction of any specific KV quantization paper.',
        'config': vars(args) | {'out': str(args.out), 'csv': str(args.csv) if args.csv else None},
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
