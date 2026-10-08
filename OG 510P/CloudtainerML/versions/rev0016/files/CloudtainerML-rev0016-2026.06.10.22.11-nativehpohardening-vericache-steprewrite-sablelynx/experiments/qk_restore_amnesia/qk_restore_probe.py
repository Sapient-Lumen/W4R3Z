#!/usr/bin/env python3
"""QK-restore attention-amnesia toy probe.

Inspired by claims that CoT fine-tuning can damage long-range recall in hybrid
models by changing Q/K routing, and that restoring Q/K from a pre-SFT checkpoint
can recover retrieval while keeping other parameters. This toy creates caches
where old semantic targets compete with recent local decoys, then evaluates
score families that stand in for pre-SFT QK, post-SFT local-biased QK, restored
QK, and a Procrustes-like compromise.

The probe is intentionally tiny and synthetic: it tests the shape of the claim,
not the paper's implementation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def random_orthogonal(rng: np.random.Generator, dim: int, strength: float) -> np.ndarray:
    a = rng.normal(size=(dim, dim))
    q, _ = np.linalg.qr(a)
    return l2norm((1 - strength) * np.eye(dim) + strength * q, axis=0).astype(np.float32)


def make_case(seed: int, regime: str, n_tokens: int, dim: int) -> dict:
    rng = np.random.default_rng(seed)
    k_base = l2norm(rng.normal(size=(n_tokens, dim)).astype(np.float32))
    v = l2norm(0.60 * k_base + 0.40 * rng.normal(size=(n_tokens, dim)).astype(np.float32))
    target = int(rng.integers(0, max(4, n_tokens // 4)))
    local = int(n_tokens - 1 - rng.integers(0, max(2, n_tokens // 12)))
    q_sem = l2norm(k_base[target] + 0.04 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    # Local decoy is plausible for short-range CoT but wrong for long-range recall.
    k_base[local] = l2norm(0.72 * q_sem + 0.28 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    v[local] = l2norm(-v[target] + 0.10 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    distractors = rng.choice([i for i in range(n_tokens) if i not in {target, local}], size=max(8, n_tokens // 32), replace=False)
    k_base[distractors] = l2norm(0.35 * q_sem + 0.65 * rng.normal(size=(len(distractors), dim)).astype(np.float32))

    if regime == "clean_recall":
        local_bias = 0.35
        drift = 0.16
    elif regime == "cot_local_bias":
        local_bias = 1.55
        drift = 0.42
    elif regime == "hard_decoy":
        local_bias = 2.30
        drift = 0.50
        k_base[local] = l2norm(0.86 * q_sem + 0.14 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    else:
        raise ValueError(regime)

    rot_post = random_orthogonal(rng, dim, drift)
    age = np.linspace(0.0, 1.0, n_tokens, dtype=np.float32)
    local_kernel = np.exp(-((1.0 - age) / 0.13) ** 2).astype(np.float32)
    return {"k_base": k_base.astype(np.float32), "v": v.astype(np.float32), "q_sem": q_sem.astype(np.float32), "target": target, "local": local, "rot_post": rot_post, "local_kernel": local_kernel, "local_bias": local_bias}


def score(case: dict, method: str) -> np.ndarray:
    k = case["k_base"]
    q = case["q_sem"]
    local = case["local_kernel"]
    if method == "pre_sft_qk":
        return k @ q + 0.10 * local
    if method == "post_sft_local_qk":
        rp = case["rot_post"]
        return (k @ rp) @ (rp.T @ q) + case["local_bias"] * local
    if method == "qk_restore":
        return k @ q + 0.10 * local
    if method == "procrustes_compromise":
        rp = case["rot_post"]
        post_scores = (k @ rp) @ (rp.T @ q)
        pre_scores = k @ q
        return 0.72 * pre_scores + 0.28 * post_scores + 0.38 * local
    if method == "local_only_ablation":
        return local
    raise ValueError(method)


@dataclass
class Row:
    seed: int
    regime: str
    method: str
    n_tokens: int
    target_rank: int
    local_rank: int
    target_top1: int
    local_top1: int
    target_attention_mass: float
    local_attention_mass: float
    output_rel_error: float
    output_cosine: float
    long_recall_success: float
    local_reasoning_proxy: float


def eval_method(seed: int, regime: str, method: str, n_tokens: int, dim: int) -> Row:
    case = make_case(seed, regime, n_tokens, dim)
    ref_scores = score(case, "pre_sft_qk")
    ref_w = softmax(ref_scores / 0.08)
    ref_out = ref_w @ case["v"]
    s = score(case, method)
    w = softmax(s / 0.08)
    out = w @ case["v"]
    order = np.argsort(-s)
    target = int(case["target"])
    local = int(case["local"])
    target_rank = int(np.where(order == target)[0][0] + 1)
    local_rank = int(np.where(order == local)[0][0] + 1)
    rel = float(np.linalg.norm(out - ref_out) / (np.linalg.norm(ref_out) + 1e-8))
    cos = float(np.dot(out, ref_out) / ((np.linalg.norm(out) * np.linalg.norm(ref_out)) + 1e-8))
    return Row(
        seed=seed,
        regime=regime,
        method=method,
        n_tokens=n_tokens,
        target_rank=target_rank,
        local_rank=local_rank,
        target_top1=int(order[0] == target),
        local_top1=int(order[0] == local),
        target_attention_mass=float(w[target]),
        local_attention_mass=float(w[local]),
        output_rel_error=rel,
        output_cosine=cos,
        long_recall_success=float(target_rank <= 3 and w[target] > w[local]),
        local_reasoning_proxy=float(w[local]),
    )


def summarize(rows: List[Row]) -> dict:
    by = {}
    for regime in sorted({r.regime for r in rows}):
        for method in sorted({r.method for r in rows}):
            sub = [r for r in rows if r.regime == regime and r.method == method]
            by[f"{regime}/{method}"] = {
                "mean_long_recall_success": float(np.mean([r.long_recall_success for r in sub])),
                "mean_target_rank": float(np.mean([r.target_rank for r in sub])),
                "mean_target_attention_mass": float(np.mean([r.target_attention_mass for r in sub])),
                "mean_local_attention_mass": float(np.mean([r.local_attention_mass for r in sub])),
                "mean_output_rel_error": float(np.mean([r.output_rel_error for r in sub])),
                "mean_local_reasoning_proxy": float(np.mean([r.local_reasoning_proxy for r in sub])),
            }
    # Pareto-ish score: recall high, output error low, local proxy not zero.
    winners = {}
    practical_winners = {}
    for regime in sorted({r.regime for r in rows}):
        candidates = []
        practical = []
        for method in sorted({r.method for r in rows}):
            rec = by[f"{regime}/{method}"]
            score_v = rec["mean_long_recall_success"] - 0.15 * rec["mean_output_rel_error"] + 0.05 * min(rec["mean_local_reasoning_proxy"], 0.3)
            candidates.append((-score_v, method))
            if method != "pre_sft_qk":
                practical.append((-score_v, method))
        candidates.sort()
        practical.sort()
        winners[regime] = candidates[0][1]
        practical_winners[regime] = practical[0][1]
    return {"row_count": len(rows), "by_regime_method": by, "winners": winners, "practical_winners_excluding_pre_sft": practical_winners}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0007_QK_RESTORE_AMNESIA_SMOKE"))
    ap.add_argument("--seeds", type=int, default=48)
    ap.add_argument("--n-tokens", type=int, default=512)
    ap.add_argument("--dim", type=int, default=48)
    args = ap.parse_args()
    regimes = ["clean_recall", "cot_local_bias", "hard_decoy"]
    methods = ["pre_sft_qk", "post_sft_local_qk", "qk_restore", "procrustes_compromise", "local_only_ablation"]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for regime in regimes:
            for method in methods:
                rows.append(eval_method(seed, regime, method, args.n_tokens, args.dim))
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out.with_suffix(".csv")
    json_path = out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in rows)
    payload = {
        "probe": "qk_restore_amnesia",
        "purpose": "Toy test of Q/K routing restoration after local-biased tuning damages long-range recall.",
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()} | {"regimes": regimes, "methods": methods},
        "summary": summarize(rows),
        "csv": str(csv_path),
        "rows": [asdict(r) for r in rows[:80]],
        "note": "Rows are truncated in JSON; CSV contains all rows.",
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"probe": payload["probe"], "rows": len(rows), "csv": str(csv_path), "json": str(json_path), "winners": payload["summary"]["winners"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
