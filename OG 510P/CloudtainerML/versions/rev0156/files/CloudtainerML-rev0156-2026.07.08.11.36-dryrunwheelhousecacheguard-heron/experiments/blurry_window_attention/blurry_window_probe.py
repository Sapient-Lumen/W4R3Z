#!/usr/bin/env python3
"""Blurry Window Attention toy probe.

This is a small bounded-memory reconstruction test inspired by Blurry Window
Attention. It does not implement the paper. It compares exact attention, sliding
windows, temporal landmarks, and low-frequency FFT reconstructions on synthetic
histories where old facts may be smooth, periodic, recent, or needle-like.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class Row:
    seed: int
    task: str
    method: str
    seq_len: int
    dim: int
    target: int
    target_age: int
    state_scalars_ratio: float
    output_cosine_vs_full: float
    output_l2_error_vs_full: float
    target_top1_hit: float
    target_mass_or_bin_hit: float
    attention_entropy: float


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8))


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def attn(q: np.ndarray, k: np.ndarray, v: np.ndarray, temp: float = 0.12) -> Tuple[np.ndarray, np.ndarray]:
    w = softmax((k @ q) / max(temp, 1e-6))
    return w @ v, w


def lowfreq_reconstruct(x: np.ndarray, keep: int) -> np.ndarray:
    coeff = np.fft.rfft(x, axis=0)
    out = np.zeros_like(coeff)
    keep = min(keep, coeff.shape[0])
    out[:keep] = coeff[:keep]
    return np.fft.irfft(out, n=x.shape[0], axis=0).real


def make_sequence(seed: int, task: str, seq_len: int, dim: int) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, seq_len, endpoint=False)
    if task == 'smooth_old_fact':
        basis = rng.normal(size=(4, dim))
        k = sum(np.sin(2 * np.pi * (i + 1) * t)[:, None] * basis[i] for i in range(4))
        k += 0.05 * rng.normal(size=(seq_len, dim))
        v = 0.7 * k + 0.3 * rng.normal(size=(seq_len, dim))
        target = int(seq_len * 0.18)
    elif task == 'periodic_fact':
        basis = rng.normal(size=(6, dim))
        k = sum(np.sin(2 * np.pi * (i + 2) * t + rng.uniform(0, 2*np.pi))[:, None] * basis[i] for i in range(6))
        v = sum(np.cos(2 * np.pi * (i + 2) * t)[:, None] * basis[i] for i in range(6))
        k += 0.04 * rng.normal(size=(seq_len, dim))
        v += 0.04 * rng.normal(size=(seq_len, dim))
        target = int(seq_len * 0.31)
    elif task == 'recent_local':
        k = rng.normal(size=(seq_len, dim))
        # Add local smoothness only near the end.
        for i in range(1, seq_len):
            k[i] = 0.82 * k[i-1] + 0.18 * k[i]
        v = 0.6 * k + 0.4 * rng.normal(size=(seq_len, dim))
        target = int(seq_len * 0.92)
    elif task == 'needle_spike':
        k = 0.25 * rng.normal(size=(seq_len, dim))
        v = 0.25 * rng.normal(size=(seq_len, dim))
        target = int(seq_len * 0.22)
        needle_k = l2norm(rng.normal(size=dim))
        needle_v = l2norm(rng.normal(size=dim))
        k[target] = 5.0 * needle_k
        v[target] = 5.0 * needle_v
    elif task == 'mixed_spike_on_smooth':
        basis = rng.normal(size=(3, dim))
        k = sum(np.sin(2 * np.pi * (i + 1) * t)[:, None] * basis[i] for i in range(3))
        v = 0.65 * k + 0.35 * rng.normal(size=(seq_len, dim))
        target = int(seq_len * 0.42)
        k[target] += 4.0 * l2norm(rng.normal(size=dim))
        v[target] += 4.0 * l2norm(rng.normal(size=dim))
    else:
        raise ValueError(task)
    k = l2norm(k)
    v = l2norm(v)
    q = l2norm(k[target] + 0.04 * rng.normal(size=dim))
    return k, v, target, q


def landmark_attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, bins: int, target: int) -> Tuple[np.ndarray, float, float, float]:
    n = k.shape[0]
    edges = np.linspace(0, n, bins + 1, dtype=int)
    lk, lv = [], []
    target_bin = None
    for i in range(bins):
        lo, hi = edges[i], edges[i+1]
        lk.append(np.mean(k[lo:hi], axis=0))
        lv.append(np.mean(v[lo:hi], axis=0))
        if lo <= target < hi:
            target_bin = i
    lk = l2norm(np.array(lk))
    lv = l2norm(np.array(lv))
    out, w = attn(q, lk, lv)
    top_bin = int(np.argmax(w))
    return out, float(top_bin == target_bin), float(w[target_bin]), float(-np.sum(w * np.log(w + 1e-12)))


def run_trial(seed: int, task: str, seq_len: int, dim: int) -> List[Row]:
    k, v, target, q = make_sequence(seed, task, seq_len, dim)
    full_out, full_w = attn(q, k, v)
    full_top = int(np.argmax(full_w))
    rows: List[Row] = []
    full_scalars = 2 * seq_len * dim
    full_entropy = float(-np.sum(full_w * np.log(full_w + 1e-12)))
    rows.append(Row(seed, task, 'full_attention', seq_len, dim, target, seq_len - target, 1.0, 1.0, 0.0, float(full_top == target), float(full_w[target]), full_entropy))

    for wsize in [16, 32, 64]:
        lo = max(0, seq_len - wsize)
        out, ww = attn(q, k[lo:], v[lo:])
        local_top = lo + int(np.argmax(ww))
        in_window = lo <= target < seq_len
        mass = float(ww[target - lo]) if in_window else 0.0
        rows.append(Row(seed, task, f'sliding_window_{wsize}', seq_len, dim, target, seq_len - target,
                        float((2 * wsize * dim) / full_scalars), cosine(out, full_out), float(np.linalg.norm(out-full_out)),
                        float(local_top == target), mass, float(-np.sum(ww * np.log(ww + 1e-12)))))

    for keep in [4, 8, 16, 32]:
        kr = l2norm(lowfreq_reconstruct(k, keep))
        vr = l2norm(lowfreq_reconstruct(v, keep))
        out, ww = attn(q, kr, vr)
        top = int(np.argmax(ww))
        # rfft coefficients are complex; approximate scalar storage as 4 arrays for real/imag K/V.
        state_ratio = float((4 * keep * dim) / full_scalars)
        rows.append(Row(seed, task, f'fft_blurry_{keep}', seq_len, dim, target, seq_len - target,
                        state_ratio, cosine(out, full_out), float(np.linalg.norm(out-full_out)),
                        float(top == target), float(ww[target]), float(-np.sum(ww * np.log(ww + 1e-12)))))

    for bins in [8, 16, 32]:
        out, bin_hit, target_bin_mass, entropy = landmark_attention(q, k, v, bins, target)
        state_ratio = float((2 * bins * dim) / full_scalars)
        rows.append(Row(seed, task, f'temporal_landmarks_{bins}', seq_len, dim, target, seq_len - target,
                        state_ratio, cosine(out, full_out), float(np.linalg.norm(out-full_out)),
                        bin_hit, target_bin_mass, entropy))
    return rows


def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for task in sorted(set(r.task for r in rows)):
        for method in sorted(set(r.method for r in rows)):
            sub = [r for r in rows if r.task == task and r.method == method]
            if not sub:
                continue
            by[f'{task}/{method}'] = {
                'mean_state_scalars_ratio': float(np.mean([r.state_scalars_ratio for r in sub])),
                'mean_output_cosine_vs_full': float(np.mean([r.output_cosine_vs_full for r in sub])),
                'mean_output_l2_error_vs_full': float(np.mean([r.output_l2_error_vs_full for r in sub])),
                'target_top1_hit_rate': float(np.mean([r.target_top1_hit for r in sub])),
                'mean_target_mass_or_bin_hit': float(np.mean([r.target_mass_or_bin_hit for r in sub])),
            }
    return {'row_count': len(rows), 'by_task_method': by}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('artifacts/probe-results/REV0006_BLURRY_WINDOW_SMOKE'))
    ap.add_argument('--seeds', type=int, default=16)
    ap.add_argument('--seq-len', type=int, default=256)
    ap.add_argument('--dim', type=int, default=32)
    args = ap.parse_args()
    tasks = ['smooth_old_fact', 'periodic_fact', 'recent_local', 'needle_spike', 'mixed_spike_on_smooth']
    rows: List[Row] = []
    for seed in range(args.seeds):
        for task in tasks:
            rows.extend(run_trial(seed, task, args.seq_len, args.dim))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = args.out.with_suffix('.csv')
    json_path = args.out.with_suffix('.json')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))
    payload = {
        'probe': 'blurry_window_attention',
        'purpose': 'Bounded-memory reconstruction toy: full attention vs sliding window vs low-frequency/landmark approximations.',
        'csv': str(csv_path),
        'config': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()} | {'tasks': tasks},
        'summary': summarize(rows),
        'interpretation': 'Frequency/landmark memory should help smooth/periodic history and fail on needle spikes; sliding windows should dominate recent-local cases.',
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
