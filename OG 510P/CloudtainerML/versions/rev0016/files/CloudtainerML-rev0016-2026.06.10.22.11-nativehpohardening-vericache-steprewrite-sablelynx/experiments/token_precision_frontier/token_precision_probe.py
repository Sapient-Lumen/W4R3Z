#!/usr/bin/env python3
"""Token-vs-precision KV cache frontier toy probe.

This is a cheap falsifier for the question raised by KVarN/SpectrumKV/VaSE-like
work: under a fixed byte budget, is it better to keep fewer tokens accurately or
more tokens at lower precision? The answer should depend on the attention regime,
value outliers, and whether important tokens are visible to the score used for
selection.

The probe builds synthetic K/V caches, queries, and retention policies. It then
compares approximate attention outputs against full fp32 attention while tracking
which tokens were kept, how much attention mass was dropped, and which policies
win under equal memory budgets.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def quantize_symmetric(x: np.ndarray, bits: int, eps: float = 1e-8) -> np.ndarray:
    """Row-wise signed symmetric quantization used only as a toy approximation."""
    if bits >= 32:
        return x.astype(np.float32, copy=True)
    qmax = 2 ** (bits - 1) - 1
    scale = np.max(np.abs(x), axis=1, keepdims=True) / max(qmax, 1)
    scale = np.maximum(scale, eps)
    q = np.clip(np.round(x / scale), -qmax, qmax)
    return (q * scale).astype(np.float32)


def attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, temp: float) -> Tuple[np.ndarray, np.ndarray]:
    logits = (k @ q) / max(temp, 1e-6)
    w = softmax(logits)
    return w @ v, w


def make_world(seed: int, scenario: str, n_tokens: int, dim: int) -> dict:
    rng = np.random.default_rng(seed)
    k = l2norm(rng.normal(size=(n_tokens, dim)).astype(np.float32))
    v = l2norm(0.55 * k + 0.45 * rng.normal(size=(n_tokens, dim)).astype(np.float32))
    age = np.linspace(0.0, 1.0, n_tokens, dtype=np.float32)  # 0 old, 1 recent
    target = int(rng.integers(0, n_tokens // 3))  # usually old enough to pressure recency policies
    q = l2norm(k[target] + 0.03 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    temp = 0.11
    semantic_hint = np.zeros(n_tokens, dtype=np.float32)

    if scenario == "broad_low_precision_ok":
        # Make many partially relevant tokens; coverage matters more than exact bits.
        cluster = rng.choice(n_tokens, size=max(16, n_tokens // 8), replace=False)
        k[cluster] = l2norm(0.70 * q + 0.30 * rng.normal(size=(len(cluster), dim)).astype(np.float32))
        v[cluster] = l2norm(0.65 * v[target] + 0.35 * rng.normal(size=(len(cluster), dim)).astype(np.float32))
        temp = 0.25
        semantic_hint[cluster] = 0.5
    elif scenario == "sharp_quant_sensitive":
        # A precise key determines the answer; quantization error can flip neighbors.
        impostors = rng.choice([i for i in range(n_tokens) if i != target], size=max(8, n_tokens // 32), replace=False)
        k[impostors] = l2norm(0.96 * q + 0.04 * rng.normal(size=(len(impostors), dim)).astype(np.float32))
        v[impostors] = l2norm(-v[target] + 0.10 * rng.normal(size=(len(impostors), dim)).astype(np.float32))
        temp = 0.045
        semantic_hint[target] = 1.0
    elif scenario == "dormant_value_outlier":
        # The target is useful mostly through value magnitude; attention score alone undersells it.
        q = l2norm(0.38 * k[target] + 0.62 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        v[target] *= 8.0
        distractors = rng.choice([i for i in range(n_tokens) if i != target], size=max(12, n_tokens // 16), replace=False)
        k[distractors] = l2norm(0.82 * q + 0.18 * rng.normal(size=(len(distractors), dim)).astype(np.float32))
        semantic_hint[target] = 1.0
        temp = 0.12
    elif scenario == "distractor_value_outlier":
        # Protecting value norm blindly is actively harmful.
        decoys = rng.choice([i for i in range(n_tokens) if i != target], size=max(8, n_tokens // 32), replace=False)
        v[decoys] *= 10.0
        k[decoys] = l2norm(0.10 * q + 0.90 * rng.normal(size=(len(decoys), dim)).astype(np.float32))
        semantic_hint[target] = 1.0
        temp = 0.09
    elif scenario == "recent_anchor_old_payload":
        # One recent token points at an old payload: recency alone gets the signpost but not the payload.
        anchor = n_tokens - 1 - int(rng.integers(0, max(2, n_tokens // 16)))
        k[anchor] = l2norm(0.92 * q + 0.08 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        v[anchor] = l2norm(0.20 * v[target] + 0.80 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        v[target] *= 4.0
        semantic_hint[[anchor, target]] = [0.6, 1.0]
        temp = 0.08
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    return {"k": k.astype(np.float32), "v": v.astype(np.float32), "q": q.astype(np.float32), "age": age, "target": target, "temp": temp, "semantic_hint": semantic_hint}


def choose_by_score(score: np.ndarray, count: int) -> np.ndarray:
    count = int(max(0, min(len(score), count)))
    if count == 0:
        return np.array([], dtype=np.int64)
    return np.argpartition(-score, count - 1)[:count].astype(np.int64)


def policy_plan(policy: str, world: dict, budget_bits: int, dim: int) -> List[Tuple[np.ndarray, int]]:
    k, v, q = world["k"], world["v"], world["q"]
    logits = k @ q
    attention_score = logits - np.min(logits)
    value_score = np.linalg.norm(v, axis=1)
    recency_score = world["age"]
    semantic_hint = world["semantic_hint"]
    n = len(k)

    def capacity(bits: int) -> int:
        # K and V both stored at this precision.
        return max(1, min(n, budget_bits // max(1, (2 * dim * bits))))

    if policy == "few_8bit_attention":
        bits = 8
        return [(choose_by_score(attention_score + 0.02 * recency_score, capacity(bits)), bits)]
    if policy == "more_4bit_attention":
        bits = 4
        return [(choose_by_score(attention_score + 0.02 * recency_score, capacity(bits)), bits)]
    if policy == "many_2bit_attention":
        bits = 2
        return [(choose_by_score(attention_score + 0.02 * recency_score, capacity(bits)), bits)]
    if policy == "recency_4bit":
        bits = 4
        return [(choose_by_score(recency_score, capacity(bits)), bits)]
    if policy == "value_protected_4bit":
        bits = 4
        score = attention_score + 0.45 * (value_score / (np.mean(value_score) + 1e-8))
        return [(choose_by_score(score, capacity(bits)), bits)]
    if policy == "semantic_sponsor_4bit":
        bits = 4
        score = attention_score + 1.25 * semantic_hint + 0.25 * value_score / (np.mean(value_score) + 1e-8)
        return [(choose_by_score(score, capacity(bits)), bits)]
    if policy == "mixed_salience_8_4_2":
        # Spend high precision on top salience, then 4-bit, then 2-bit with remaining budget.
        sal = attention_score + 0.10 * recency_score + 0.10 * value_score / (np.mean(value_score) + 1e-8)
        order = np.argsort(-sal)
        remaining = budget_bits
        groups: List[Tuple[np.ndarray, int]] = []
        used: set[int] = set()
        for bits, frac in [(8, 0.30), (4, 0.40), (2, 1.00)]:
            max_count = int((budget_bits * frac) // max(1, 2 * dim * bits)) if bits != 2 else int(remaining // max(1, 2 * dim * bits))
            picks = []
            for idx in order:
                if idx not in used:
                    picks.append(int(idx))
                    used.add(int(idx))
                    remaining -= 2 * dim * bits
                    if len(picks) >= max_count or remaining < 2 * dim * 2:
                        break
            if picks:
                groups.append((np.array(picks, dtype=np.int64), bits))
        return groups
    if policy == "oracle_target_4bit":
        bits = 4
        count = capacity(bits)
        score = attention_score.copy()
        score[world["target"]] += 1e6
        return [(choose_by_score(score, count), bits)]
    raise ValueError(f"unknown policy: {policy}")


def approx_output(world: dict, groups: List[Tuple[np.ndarray, int]], dim: int) -> dict:
    if not groups:
        return {"output": np.zeros(dim, dtype=np.float32), "kept": np.array([], dtype=np.int64), "bits": np.array([], dtype=np.int64)}
    ks, vs, kept, bit_vec = [], [], [], []
    for idx, bits in groups:
        if len(idx) == 0:
            continue
        kq = quantize_symmetric(world["k"][idx], bits)
        vq = quantize_symmetric(world["v"][idx], bits)
        ks.append(kq)
        vs.append(vq)
        kept.extend([int(i) for i in idx])
        bit_vec.extend([bits] * len(idx))
    if not ks:
        return {"output": np.zeros(dim, dtype=np.float32), "kept": np.array([], dtype=np.int64), "bits": np.array([], dtype=np.int64)}
    k = np.concatenate(ks, axis=0)
    v = np.concatenate(vs, axis=0)
    out, attn = attention(world["q"], k, v, world["temp"])
    return {"output": out, "kept": np.array(kept, dtype=np.int64), "bits": np.array(bit_vec, dtype=np.int64), "attn": attn}


@dataclass
class Row:
    seed: int
    scenario: str
    policy: str
    budget_equiv_4bit_tokens: int
    budget_bits: int
    retained_tokens: int
    mean_bits: float
    target_retained: int
    retained_fraction: float
    dropped_attention_mass: float
    output_rel_error: float
    output_cosine: float
    bytes_used_fraction: float


def eval_policy(seed: int, scenario: str, policy: str, budget_tokens_4bit: int, n_tokens: int, dim: int) -> Row:
    world = make_world(seed, scenario, n_tokens, dim)
    ref_out, ref_attn = attention(world["q"], world["k"], world["v"], world["temp"])
    budget_bits = int(budget_tokens_4bit * 2 * dim * 4)
    groups = policy_plan(policy, world, budget_bits, dim)
    approx = approx_output(world, groups, dim)
    kept = approx["kept"]
    bits = approx["bits"]
    out = approx["output"]
    used_bits = int(sum(2 * dim * int(b) for b in bits))
    kept_set = set(int(i) for i in kept)
    dropped_mass = float(1.0 - np.sum(ref_attn[kept]) if len(kept) else 1.0)
    rel_err = float(np.linalg.norm(out - ref_out) / (np.linalg.norm(ref_out) + 1e-8))
    cos = float(np.dot(out, ref_out) / ((np.linalg.norm(out) * np.linalg.norm(ref_out)) + 1e-8))
    return Row(
        seed=seed,
        scenario=scenario,
        policy=policy,
        budget_equiv_4bit_tokens=budget_tokens_4bit,
        budget_bits=budget_bits,
        retained_tokens=int(len(kept)),
        mean_bits=float(np.mean(bits)) if len(bits) else 0.0,
        target_retained=int(world["target"] in kept_set),
        retained_fraction=float(len(kept) / n_tokens),
        dropped_attention_mass=dropped_mass,
        output_rel_error=rel_err,
        output_cosine=cos,
        bytes_used_fraction=float(used_bits / max(1, budget_bits)),
    )


def summarize(rows: List[Row]) -> dict:
    by = {}
    for scenario in sorted({r.scenario for r in rows}):
        for budget in sorted({r.budget_equiv_4bit_tokens for r in rows}):
            sub_budget = [r for r in rows if r.scenario == scenario and r.budget_equiv_4bit_tokens == budget]
            candidates = []
            for policy in sorted({r.policy for r in sub_budget}):
                sub = [r for r in sub_budget if r.policy == policy]
                rec = {
                    "mean_output_rel_error": float(np.mean([r.output_rel_error for r in sub])),
                    "mean_dropped_attention_mass": float(np.mean([r.dropped_attention_mass for r in sub])),
                    "target_retention_rate": float(np.mean([r.target_retained for r in sub])),
                    "mean_retained_tokens": float(np.mean([r.retained_tokens for r in sub])),
                    "mean_bits": float(np.mean([r.mean_bits for r in sub])),
                }
                by[f"{scenario}/budget{budget}/{policy}"] = rec
                candidates.append((rec["mean_output_rel_error"], policy))
            candidates.sort()
            by[f"{scenario}/budget{budget}/__winner__"] = {"best_policy": candidates[0][1], "best_mean_output_rel_error": float(candidates[0][0])}
    winner_counts: Dict[str, int] = {}
    for k, v in by.items():
        if k.endswith("/__winner__"):
            winner_counts[v["best_policy"]] = winner_counts.get(v["best_policy"], 0) + 1
    return {"row_count": len(rows), "by_scenario_budget_policy": by, "winner_counts": winner_counts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0007_TOKEN_PRECISION_FRONTIER_SMOKE"))
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--n-tokens", type=int, default=256)
    ap.add_argument("--dim", type=int, default=32)
    args = ap.parse_args()
    scenarios = ["broad_low_precision_ok", "sharp_quant_sensitive", "dormant_value_outlier", "distractor_value_outlier", "recent_anchor_old_payload"]
    policies = ["few_8bit_attention", "more_4bit_attention", "many_2bit_attention", "recency_4bit", "value_protected_4bit", "semantic_sponsor_4bit", "mixed_salience_8_4_2", "oracle_target_4bit"]
    budgets = [16, 32, 64]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for scenario in scenarios:
            for budget in budgets:
                for policy in policies:
                    rows.append(eval_policy(seed, scenario, policy, budget, args.n_tokens, args.dim))

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out.with_suffix(".csv")
    json_path = out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in rows)
    payload = {
        "probe": "token_precision_frontier",
        "purpose": "Equal-byte test of fewer high-precision KV tokens vs more low-precision KV tokens under synthetic cache regimes.",
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()} | {"scenarios": scenarios, "policies": policies, "budgets_equiv_4bit_tokens": budgets},
        "summary": summarize(rows),
        "csv": str(csv_path),
        "rows": [asdict(r) for r in rows[:80]],
        "note": "Rows are truncated in JSON; CSV contains all rows.",
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"probe": payload["probe"], "rows": len(rows), "csv": str(csv_path), "json": str(json_path), "winner_counts": payload["summary"]["winner_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
