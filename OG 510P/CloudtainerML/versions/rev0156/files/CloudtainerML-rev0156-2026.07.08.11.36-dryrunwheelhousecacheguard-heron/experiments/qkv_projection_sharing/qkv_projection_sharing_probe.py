#!/usr/bin/env python3
"""QKV projection-sharing probe for CloudtainerML.

This is a tensor-only wind tunnel for the question raised by
"Do Transformers Need Three Projections?" (arXiv:2606.04032): when can K and V
be represented by the same projection without wrecking attention outputs?

It does not train a language model. It creates teacher Q/K/V projections under
several geometry regimes, least-squares-fits tied-projection variants, and logs
attention-output fidelity plus attention-map directionality. The cheap question is:
  "Is K=V benign only when teacher K and V spaces are already aligned?"
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


@dataclass(frozen=True)
class Config:
    seeds: int = 8
    tokens: int = 96
    d_model: int = 48
    d_head: int = 24
    trials_per_regime: int = 6


def stable_softmax(scores: np.ndarray) -> np.ndarray:
    scores = scores - np.max(scores, axis=-1, keepdims=True)
    ex = np.exp(scores)
    return ex / np.sum(ex, axis=-1, keepdims=True)


def rel_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    return float(np.dot(av, bv) / ((np.linalg.norm(av) * np.linalg.norm(bv)) + 1e-12))


def row_kl(p: np.ndarray, q: np.ndarray) -> float:
    eps = 1e-9
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    return float(np.mean(np.sum(p * (np.log(p) - np.log(q)), axis=-1)))


def asymmetry(scores: np.ndarray) -> float:
    return float(np.linalg.norm(scores - scores.T) / (np.linalg.norm(scores) + 1e-12))


def fit_shared(X: np.ndarray, targets: Iterable[np.ndarray]) -> np.ndarray:
    """Least-squares projection W minimizing sum ||XW - target_i||^2."""
    ys = list(targets)
    x_big = np.concatenate([X for _ in ys], axis=0)
    y_big = np.concatenate(ys, axis=0)
    w, *_ = np.linalg.lstsq(x_big, y_big, rcond=1e-5)
    return w


def make_teacher(rng: np.random.Generator, cfg: Config, regime: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Correlated-token context: rank bottlenecks make the experiment less trivial than IID noise.
    latent_rank = cfg.d_model // 3
    z = rng.normal(size=(cfg.tokens, latent_rank))
    mix = rng.normal(size=(latent_rank, cfg.d_model)) / math.sqrt(latent_rank)
    X = z @ mix + 0.15 * rng.normal(size=(cfg.tokens, cfg.d_model))
    X = (X - X.mean(axis=0, keepdims=True)) / (X.std(axis=0, keepdims=True) + 1e-6)

    Wq = rng.normal(size=(cfg.d_model, cfg.d_head)) / math.sqrt(cfg.d_model)
    Wk = rng.normal(size=(cfg.d_model, cfg.d_head)) / math.sqrt(cfg.d_model)

    if regime == "aligned_kv":
        Wv = Wk + 0.12 * rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
    elif regime == "semi_aligned_kv":
        Wv = 0.55 * Wk + 0.45 * rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
    elif regime == "low_rank_common_kv":
        a = rng.normal(size=(cfg.d_model, cfg.d_head // 3)) / math.sqrt(cfg.d_model)
        bk = rng.normal(size=(cfg.d_head // 3, cfg.d_head)) / math.sqrt(cfg.d_head // 3)
        bv = bk + 0.20 * rng.normal(size=bk.shape) / math.sqrt(cfg.d_head // 3)
        Wk = a @ bk + 0.04 * rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
        Wv = a @ bv + 0.04 * rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
    elif regime == "orthogonal_kv":
        raw = rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
        # Remove projection onto Wk's flattened direction to make K/V spaces disagree.
        wkf = Wk.reshape(-1)
        rf = raw.reshape(-1)
        raw = (rf - wkf * (np.dot(rf, wkf) / (np.dot(wkf, wkf) + 1e-12))).reshape(Wk.shape)
        Wv = raw / (np.std(raw) + 1e-6) / math.sqrt(cfg.d_model)
    elif regime == "qk_aligned_but_v_distinct":
        Wq = Wk + 0.08 * rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
        Wv = rng.normal(size=Wk.shape) / math.sqrt(cfg.d_model)
    else:
        raise ValueError(f"unknown regime {regime}")
    return X, Wq, Wk, Wv


def attend(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    scores = Q @ K.T / math.sqrt(Q.shape[-1])
    p = stable_softmax(scores)
    return p @ V, p, scores


def run_once(seed: int, trial: int, regime: str, cfg: Config) -> List[Dict[str, object]]:
    rng = np.random.default_rng(seed * 1009 + trial * 37 + hash(regime) % 997)
    X, Wq, Wk, Wv = make_teacher(rng, cfg, regime)
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    teacher_out, teacher_p, teacher_scores = attend(Q, K, V)

    variants: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, float, str]] = {}
    variants["teacher_full_qkv"] = (Q, K, V, 1.0, "3 separate projections; stores K and V")

    Wkv = fit_shared(X, [K, V])
    KVs = X @ Wkv
    variants["share_kv_fit"] = (Q, KVs, KVs, 0.5, "K=V; one cached stream")

    Wqk = fit_shared(X, [Q, K])
    QKs = X @ Wqk
    variants["share_qk_fit"] = (QKs, QKs, V, 1.0, "Q=K; cache unchanged, symmetric score risk")

    Wqv = fit_shared(X, [Q, V])
    QVs = X @ Wqv
    variants["share_qv_fit"] = (QVs, K, QVs, 1.0, "Q=V; fewer weights, cache not halved")

    Wall = fit_shared(X, [Q, K, V])
    ALL = X @ Wall
    variants["share_all_fit"] = (ALL, ALL, ALL, 0.5, "Q=K=V; smallest projection family")

    rows: List[Dict[str, object]] = []
    for name, (q, k, v, cache_factor, note) in variants.items():
        out, p, scores = attend(q, k, v)
        rows.append({
            "seed": seed,
            "trial": trial,
            "regime": regime,
            "variant": name,
            "kv_cache_factor_vs_full": cache_factor,
            "output_rel_error": rel_error(out, teacher_out),
            "output_cosine": cosine(out, teacher_out),
            "attention_kl_to_teacher": row_kl(teacher_p, p),
            "score_asymmetry": asymmetry(scores),
            "teacher_score_asymmetry": asymmetry(teacher_scores),
            "note": note,
        })
    return rows


def summarize(rows: List[Dict[str, object]]) -> Dict[str, object]:
    summary: Dict[str, object] = {"row_count": len(rows), "by_regime_variant": {}}
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for r in rows:
        grouped.setdefault((str(r["regime"]), str(r["variant"])), []).append(r)
    for (regime, variant), rs in grouped.items():
        key = f"{regime}/{variant}"
        summary["by_regime_variant"][key] = {
            "mean_output_rel_error": float(np.mean([r["output_rel_error"] for r in rs])),
            "mean_output_cosine": float(np.mean([r["output_cosine"] for r in rs])),
            "mean_attention_kl_to_teacher": float(np.mean([r["attention_kl_to_teacher"] for r in rs])),
            "mean_score_asymmetry": float(np.mean([r["score_asymmetry"] for r in rs])),
            "kv_cache_factor_vs_full": float(rs[0]["kv_cache_factor_vs_full"]),
        }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("qkv_projection_sharing_results.json"))
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--tokens", type=int, default=96)
    ap.add_argument("--d-model", type=int, default=48)
    ap.add_argument("--d-head", type=int, default=24)
    args = ap.parse_args()
    cfg = Config(seeds=args.seeds, tokens=args.tokens, d_model=args.d_model, d_head=args.d_head)
    regimes = ["aligned_kv", "semi_aligned_kv", "low_rank_common_kv", "orthogonal_kv", "qk_aligned_but_v_distinct"]
    rows: List[Dict[str, object]] = []
    for seed in range(cfg.seeds):
        for trial in range(cfg.trials_per_regime):
            for regime in regimes:
                rows.extend(run_once(seed, trial, regime, cfg))

    payload = {
        "probe": "qkv_projection_sharing",
        "purpose": "Cheap falsifier for Q/K/V projection-sharing geometry; not an LM reproduction.",
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
            w.writeheader()
            w.writerows(rows)
    print(json.dumps({"wrote": str(args.out), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
