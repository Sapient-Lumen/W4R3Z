#!/usr/bin/env python3
"""
Tensor Cache L1/L2 Probe
========================

A small associative-recall simulator inspired by Tensor Cache
(arXiv:2605.22884).  Sliding-window attention forgets evicted tokens.  Tensor
Cache writes evicted K/V pairs into a fixed outer-product memory A so a later
query can still read approximate evidence via q^T A.

This probe compares:
  * full softmax attention over all tokens
  * sliding-window attention only
  * per-token outer-product L2 memory
  * normalized outer-product L2 memory
  * chunk-mean L2 memory, which intentionally introduces spurious cross terms

It emits CSV + JSON.  It uses only NumPy.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

EPS = 1e-8


@dataclass
class TensorCacheResult:
    seed: int
    n_pairs: int
    d_key: int
    noise: float
    window: int
    chunk: int
    decay: float
    method: str
    target_in_window: bool
    correct: int
    target_rank: int
    target_score: float
    output_l2_error_vs_full: float
    output_cosine_vs_full: float


def normalize(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), EPS)


def softmax(x: np.ndarray, beta: float = 8.0) -> np.ndarray:
    y = beta * x
    y = y - y.max()
    e = np.exp(y)
    return e / np.maximum(e.sum(), EPS)


def make_memory(seed: int, n_pairs: int, d_key: int, noise: float) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray]:
    rng = np.random.default_rng(seed)
    keys = normalize(rng.normal(size=(n_pairs, d_key)))
    # Values are identity codes; exact retrieval is argmax over token id.
    values = np.eye(n_pairs, dtype=np.float64)
    # Make target usually outside small recent windows.
    target = int(rng.integers(low=0, high=max(1, n_pairs // 2)))
    query = normalize(keys[target] + noise * rng.normal(size=d_key))
    return keys, values, target, query


def full_attention(keys: np.ndarray, values: np.ndarray, query: np.ndarray) -> np.ndarray:
    weights = softmax(keys @ query)
    return weights @ values


def sliding_attention(keys: np.ndarray, values: np.ndarray, query: np.ndarray, window: int) -> np.ndarray:
    kk = keys[-window:]
    vv = values[-window:]
    weights = softmax(kk @ query)
    out = np.zeros(values.shape[1])
    out[-window:] = weights
    # Because values are identity, vv projection is equivalent to positions.  The
    # explicit version below keeps the function obvious if values are changed.
    return weights @ vv


def tensor_memory_per_token(keys: np.ndarray, values: np.ndarray, window: int, decay: float) -> np.ndarray:
    d_key = keys.shape[1]
    d_val = values.shape[1]
    a = np.zeros((d_key, d_val), dtype=np.float64)
    for k, v in zip(keys[:-window], values[:-window]):
        a = decay * a + np.outer(k, v)
    return a


def tensor_memory_chunk_mean(keys: np.ndarray, values: np.ndarray, window: int, decay: float, chunk: int) -> np.ndarray:
    d_key = keys.shape[1]
    d_val = values.shape[1]
    a = np.zeros((d_key, d_val), dtype=np.float64)
    old_k = keys[:-window]
    old_v = values[:-window]
    for start in range(0, len(old_k), chunk):
        kk = old_k[start : start + chunk]
        vv = old_v[start : start + chunk]
        if len(kk) == 0:
            continue
        # Intentional shortcut: mean key outer mean value, scaled by count.  This
        # is cheap but creates cross-token mixtures.
        a = (decay ** len(kk)) * a + len(kk) * np.outer(kk.mean(axis=0), vv.mean(axis=0))
    return a


def l2_read(a: np.ndarray, query: np.ndarray) -> np.ndarray:
    out = query @ a
    return out


def normalized_l2_read(keys: np.ndarray, values: np.ndarray, window: int, query: np.ndarray, decay: float) -> np.ndarray:
    # Positive feature map version of linear attention.  This makes the memory
    # less sign-cancelling and provides a normalization scalar.
    phi_k = np.maximum(keys[:-window], 0.0) + 0.1
    phi_q = np.maximum(query, 0.0) + 0.1
    a = np.zeros((keys.shape[1], values.shape[1]))
    z = np.zeros(keys.shape[1])
    for k, v in zip(phi_k, values[:-window]):
        a = decay * a + np.outer(k, v)
        z = decay * z + k
    return (phi_q @ a) / max(float(phi_q @ z), EPS)


def rank_of_target(out: np.ndarray, target: int) -> int:
    order = np.argsort(-out)
    return int(np.where(order == target)[0][0]) + 1


def score_output(out: np.ndarray, full: np.ndarray, target: int) -> Tuple[int, int, float, float, float]:
    pred = int(np.argmax(out))
    err = float(np.linalg.norm(out - full))
    cos = float((out @ full) / max(EPS, np.linalg.norm(out) * np.linalg.norm(full)))
    return int(pred == target), rank_of_target(out, target), float(out[target]), err, cos


def run_trial(seed: int, n_pairs: int, d_key: int, noise: float, window: int, chunk: int, decay: float) -> Iterable[TensorCacheResult]:
    keys, values, target, query = make_memory(seed, n_pairs, d_key, noise)
    full = full_attention(keys, values, query)
    target_in_window = target >= n_pairs - window

    methods: Dict[str, np.ndarray] = {}
    methods["full_attention"] = full
    methods["sliding_window"] = sliding_attention(keys, values, query, window)
    a = tensor_memory_per_token(keys, values, window, decay)
    methods["l2_outer_per_token"] = l2_read(a, query)
    methods["l2_outer_normed"] = normalized_l2_read(keys, values, window, query, decay)
    a_chunk = tensor_memory_chunk_mean(keys, values, window, decay, chunk)
    methods["l2_chunk_mean_shortcut"] = l2_read(a_chunk, query)
    # Simple fusion: if the window has a strong score, trust it; otherwise combine.
    l1 = methods["sliding_window"]
    l2 = methods["l2_outer_per_token"]
    methods["l1_l2_half_fusion"] = 0.5 * l1 + 0.5 * l2

    for name, out in methods.items():
        correct, rank, target_score, err, cos = score_output(out, full, target)
        yield TensorCacheResult(
            seed=seed,
            n_pairs=n_pairs,
            d_key=d_key,
            noise=float(noise),
            window=window,
            chunk=chunk,
            decay=float(decay),
            method=name,
            target_in_window=bool(target_in_window),
            correct=correct,
            target_rank=rank,
            target_score=target_score,
            output_l2_error_vs_full=err,
            output_cosine_vs_full=cos,
        )


def summarize(rows: list[TensorCacheResult]) -> Dict[str, object]:
    by_method = {}
    for method in sorted({r.method for r in rows}):
        sub = [r for r in rows if r.method == method]
        by_method[method] = {
            "accuracy": float(np.mean([r.correct for r in sub])),
            "mean_target_rank": float(np.mean([r.target_rank for r in sub])),
            "mean_output_l2_error_vs_full": float(np.mean([r.output_l2_error_vs_full for r in sub])),
            "mean_output_cosine_vs_full": float(np.mean([r.output_cosine_vs_full for r in sub])),
        }
    return {
        "probe": "tensor_cache_l1_l2",
        "rows": len(rows),
        "interpretation": "If L2 per-token writes recover old targets that sliding windows forget, Tensor Cache is worth escalating into a trainable tiny block. If chunk_mean collapses, the spurious-cross-term warning is visible in miniature.",
        "by_method": by_method,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, default=Path("artifacts/probe-results"))
    ap.add_argument("--prefix", type=str, default="REV0005_TENSOR_CACHE_L2_SMOKE")
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--n-pairs", type=str, default="64,128")
    ap.add_argument("--d-keys", type=str, default="16,32,64")
    ap.add_argument("--noises", type=str, default="0.02,0.12")
    ap.add_argument("--windows", type=str, default="8,16")
    ap.add_argument("--chunk", type=int, default=8)
    ap.add_argument("--decay", type=float, default=0.995)
    args = ap.parse_args()

    rows: list[TensorCacheResult] = []
    for seed in range(args.seeds):
        for n_pairs in [int(x) for x in args.n_pairs.split(",") if x]:
            for d_key in [int(x) for x in args.d_keys.split(",") if x]:
                for noise in [float(x) for x in args.noises.split(",") if x]:
                    for window in [int(x) for x in args.windows.split(",") if x]:
                        if window >= n_pairs:
                            continue
                        rows.extend(run_trial(seed, n_pairs, d_key, noise, window, args.chunk, args.decay))

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / f"{args.prefix}.csv"
    json_path = args.outdir / f"{args.prefix}.json"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    summary = summarize(rows)
    summary["csv"] = str(csv_path)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
