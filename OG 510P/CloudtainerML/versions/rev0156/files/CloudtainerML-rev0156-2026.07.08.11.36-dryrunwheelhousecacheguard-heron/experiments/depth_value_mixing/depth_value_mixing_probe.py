#!/usr/bin/env python3
"""Depth-value mixing probe for CloudtainerML.

Inspired by Depth-Attention / cross-layer value mixing (arXiv:2606.05014).
The probe simulates per-token representations across depth and asks whether a
query-conditioned depth mix can recover target information better than using the
last layer or a residual/uniform average.

No language model is trained here. This is a cheap geometry falsifier for:
  "Can selective reuse across depth beat blind residual accumulation when useful
   information is present in earlier layers but later layers drift/noise it?"
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class Config:
    seeds: int = 16
    tokens: int = 256
    depth: int = 12
    dim: int = 40
    scenarios: Tuple[str, ...] = ("monotonic_refine", "midlayer_best", "late_noise", "decoy_layer")


def normalize(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + 1e-9)


def cosine_rows(a: np.ndarray, b: np.ndarray) -> float:
    a = normalize(a)
    b = normalize(b)
    return float(np.mean(np.sum(a * b, axis=-1)))


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))


def entropy(weights: np.ndarray) -> float:
    w = np.clip(weights, 1e-9, 1.0)
    return float(np.mean(-np.sum(w * np.log(w), axis=-1)))


def make_stack(rng: np.random.Generator, cfg: Config, scenario: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return target z [T,D], layer stack h [L,T,D], signal coefficient [L]."""
    z = normalize(rng.normal(size=(cfg.tokens, cfg.dim)))
    shared_drift = normalize(rng.normal(size=(cfg.tokens, cfg.dim)))
    layers = []
    coeffs = []
    for l in range(cfg.depth):
        t = l / max(1, cfg.depth - 1)
        if scenario == "monotonic_refine":
            alpha = 0.35 + 0.65 * t
            noise = 0.75 * (1.0 - t) + 0.08
            drift = 0.10 * t
        elif scenario == "midlayer_best":
            center = 0.45
            alpha = 0.25 + 0.80 * math.exp(-((t - center) ** 2) / 0.035)
            noise = 0.20 + 0.55 * abs(t - center)
            drift = 0.10 + 0.35 * max(0.0, t - center)
        elif scenario == "late_noise":
            alpha = 0.85 - 0.55 * max(0.0, t - 0.45) / 0.55
            noise = 0.16 + 0.90 * max(0.0, t - 0.55)
            drift = 0.05 + 0.45 * max(0.0, t - 0.55)
        elif scenario == "decoy_layer":
            alpha = 0.35 + 0.55 * math.exp(-((t - 0.35) ** 2) / 0.025)
            noise = 0.25 + 0.25 * t
            drift = 0.05
        else:
            raise ValueError(scenario)
        h = alpha * z + drift * shared_drift + noise * rng.normal(size=z.shape) / math.sqrt(cfg.dim)
        if scenario == "decoy_layer" and l == int(0.72 * (cfg.depth - 1)):
            # A sharp but wrong representation that can fool blind/high-norm pooling.
            h = 0.15 * z + 1.50 * normalize(rng.normal(size=z.shape))
        layers.append(h)
        coeffs.append(alpha)
    return z, np.stack(layers, axis=0), np.asarray(coeffs)


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - np.max(x, axis=axis, keepdims=True)
    ex = np.exp(x)
    return ex / np.sum(ex, axis=axis, keepdims=True)


def choose_outputs(z: np.ndarray, h: np.ndarray) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    L, T, D = h.shape
    final = h[-1]
    uniform_w = np.full((T, L), 1.0 / L)
    uniform = np.einsum("tl,ltd->td", uniform_w, h)

    rec = np.exp(np.linspace(-2.0, 0.0, L))
    rec = rec / rec.sum()
    rec_w = np.repeat(rec[None, :], T, axis=0)
    exp_recent = np.einsum("tl,ltd->td", rec_w, h)

    # Query is final representation; keys/values are earlier-depth representations at the same token.
    q = normalize(final)
    k = normalize(np.transpose(h, (1, 0, 2)))  # [T,L,D]
    scores = np.einsum("td,tld->tl", q, k) * math.sqrt(D)
    depth_w = softmax(scores, axis=-1)
    depth_mix = np.einsum("tl,ltd->td", depth_w, h)

    # Same idea but with a small entropy bias toward not over-trusting a single high-norm decoy.
    flat_scores = scores / 2.0
    soft_depth_w = softmax(flat_scores, axis=-1)
    soft_depth_mix = np.einsum("tl,ltd->td", soft_depth_w, h)

    # Oracle upper bound: choose the layer closest to target per token.
    cos = np.einsum("td,ltd->lt", normalize(z), normalize(h))
    idx = np.argmax(cos, axis=0)
    oracle = h[idx, np.arange(T)]
    oracle_w = np.eye(L)[idx]

    return {
        "final_only": (final, np.eye(L)[np.full(T, L - 1)]),
        "uniform_depth_mean": (uniform, uniform_w),
        "exp_recent_depth_mean": (exp_recent, rec_w),
        "query_depth_attention": (depth_mix, depth_w),
        "soft_query_depth_attention": (soft_depth_mix, soft_depth_w),
        "oracle_best_layer": (oracle, oracle_w),
    }


def run(cfg: Config) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for seed in range(cfg.seeds):
        rng = np.random.default_rng(7817 + seed)
        for scenario in cfg.scenarios:
            z, h, coeffs = make_stack(rng, cfg, scenario)
            outputs = choose_outputs(z, h)
            for method, (out, w) in outputs.items():
                rows.append({
                    "seed": seed,
                    "scenario": scenario,
                    "method": method,
                    "cosine_to_target": cosine_rows(out, z),
                    "mse_to_target": mse(out, z),
                    "mean_depth_entropy": entropy(w),
                    "mean_selected_depth": float(np.mean(np.argmax(w, axis=-1))),
                    "best_signal_depth": int(np.argmax(coeffs)),
                })
    return rows


def summarize(rows: List[Dict[str, object]]) -> Dict[str, object]:
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for r in rows:
        grouped.setdefault((str(r["scenario"]), str(r["method"])), []).append(r)
    out = {"row_count": len(rows), "by_scenario_method": {}}
    for (scenario, method), rs in grouped.items():
        out["by_scenario_method"][f"{scenario}/{method}"] = {
            "mean_cosine_to_target": float(np.mean([r["cosine_to_target"] for r in rs])),
            "mean_mse_to_target": float(np.mean([r["mse_to_target"] for r in rs])),
            "mean_depth_entropy": float(np.mean([r["mean_depth_entropy"] for r in rs])),
            "mean_selected_depth": float(np.mean([r["mean_selected_depth"] for r in rs])),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("depth_value_mixing_results.json"))
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--seeds", type=int, default=16)
    args = ap.parse_args()
    cfg = Config(seeds=args.seeds)
    rows = run(cfg)
    payload = {
        "probe": "depth_value_mixing",
        "purpose": "Cheap geometry test for selective cross-layer value reuse.",
        "config": cfg.__dict__,
        "summary": summarize(rows),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    print(json.dumps({"wrote": str(args.out), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
