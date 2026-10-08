#!/usr/bin/env python3
"""PCAF-style sparse successor memory toy probe.

Motivated by Parallel Causal Associative Fields (PCAF): write local successor
records into hash buckets, retrieve a bounded candidate set for the current
query, form a sparse cache distribution, and mix it with a local model through a
learned gate.

This is not a reproduction. It is a cheap CloudtainerML falsifier:
  * Can bounded hash retrieval preserve old content-addressed successor records?
  * When do collisions, updates, and recent local decoys break it?
  * Does a simple gate help or just hide retrieval failures?
"""
from __future__ import annotations

import argparse
import csv
import json
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


def attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, temp: float = 0.08) -> tuple[np.ndarray, np.ndarray]:
    w = softmax((k @ q) / temp)
    return w @ v, w


def make_world(seed: int, scenario: str, n_records: int, dim: int) -> dict:
    rng = np.random.default_rng(seed)
    k = l2norm(rng.normal(size=(n_records, dim)).astype(np.float32))
    v = l2norm(0.55 * k + 0.45 * rng.normal(size=(n_records, dim)).astype(np.float32))
    age = np.linspace(0.0, 1.0, n_records, dtype=np.float32)
    target = int(rng.integers(0, max(4, n_records // 4)))
    q = l2norm(k[target] + 0.035 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    local_hint = np.zeros(n_records, dtype=np.float32)
    temp = 0.08

    if scenario == "clean_old_successor":
        local_hint[-16:] = 0.2
    elif scenario == "noisy_bucket_collision":
        decoys = rng.choice([i for i in range(n_records) if i != target], size=max(24, n_records // 12), replace=False)
        k[decoys] = l2norm(0.78 * q + 0.22 * rng.normal(size=(len(decoys), dim)).astype(np.float32))
        v[decoys] = l2norm(-v[target] + 0.25 * rng.normal(size=(len(decoys), dim)).astype(np.float32))
        local_hint[decoys] = 0.3
        temp = 0.06
    elif scenario == "recurring_entity_update":
        # Old target has a recent correction. Hash retrieval must avoid returning stale sibling only.
        correction = int(n_records - 1 - rng.integers(0, max(4, n_records // 16)))
        k[correction] = l2norm(0.93 * q + 0.07 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        v[correction] = l2norm(0.75 * v[target] + 0.25 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        local_hint[correction] = 1.0
        target = correction
        q = l2norm(k[target] + 0.035 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        temp = 0.07
    elif scenario == "rare_old_fact_vs_recent_noise":
        recent = np.arange(max(0, n_records - max(32, n_records // 8)), n_records)
        k[recent] = l2norm(0.45 * q + 0.55 * rng.normal(size=(len(recent), dim)).astype(np.float32))
        v[recent] = l2norm(-0.5 * v[target] + 0.5 * rng.normal(size=(len(recent), dim)).astype(np.float32))
        local_hint[recent] = 0.8
        temp = 0.055
    else:
        raise ValueError(scenario)

    return {"k": k.astype(np.float32), "v": v.astype(np.float32), "q": q.astype(np.float32), "target": target, "age": age, "local_hint": local_hint, "temp": temp}


def hash_bits(x: np.ndarray, planes: np.ndarray) -> np.ndarray:
    return (x @ planes.T >= 0).astype(np.uint8)


def hamming(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.sum(a != b, axis=1)


def select_candidates(world: dict, method: str, budget: int, seed: int, hash_bits_count: int) -> np.ndarray:
    k, q, age = world["k"], world["q"], world["age"]
    rng = np.random.default_rng(seed + 9173)
    n, dim = k.shape
    score = k @ q
    if method == "full_attention":
        return np.arange(n, dtype=np.int64)
    if method == "local_window":
        return np.arange(max(0, n - budget), n, dtype=np.int64)
    if method == "semantic_topk_oracle":
        return np.argpartition(-score, min(budget, n) - 1)[:budget].astype(np.int64)
    if method == "random_budget":
        return rng.choice(n, size=min(budget, n), replace=False).astype(np.int64)
    if method in {"pcaf_hash", "pcaf_hash_gate", "hash_plus_recency"}:
        planes = l2norm(rng.normal(size=(hash_bits_count, dim)).astype(np.float32))
        kb = hash_bits(k, planes)
        qb = hash_bits(q.reshape(1, -1), planes)[0]
        dist = hamming(kb, qb).astype(np.float32)
        if method == "hash_plus_recency":
            dist = dist - 0.35 * age  # tie-break toward recent records without losing bucket shape
        order = np.argsort(dist)
        return order[: min(budget, n)].astype(np.int64)
    raise ValueError(method)


@dataclass
class Row:
    seed: int
    scenario: str
    method: str
    n_records: int
    dim: int
    budget: int
    hash_bits: int
    candidate_count: int
    target_in_candidates: int
    target_rank_in_candidates: int
    dropped_full_attention_mass: float
    output_rel_error_vs_full: float
    target_value_cosine: float
    exact_success: float
    gate_weight: float
    read_fraction: float


def eval_method(seed: int, scenario: str, method: str, n_records: int, dim: int, budget: int, hash_bits_count: int) -> Row:
    world = make_world(seed, scenario, n_records, dim)
    k, v, q = world["k"], world["v"], world["q"]
    target = int(world["target"])
    full_out, full_w = attention(q, k, v, world["temp"])
    cand = select_candidates(world, method, budget, seed, hash_bits_count)
    out, w = attention(q, k[cand], v[cand], world["temp"])
    gate = 1.0
    if method == "pcaf_hash_gate":
        # Confidence proxy: high if best candidate is sharply aligned. Mix with local recent output otherwise.
        max_score = float(np.max(k[cand] @ q)) if len(cand) else -1.0
        gate = float(1.0 / (1.0 + np.exp(-18.0 * (max_score - 0.62))))
        recent = np.arange(max(0, n_records - min(budget, n_records)), n_records, dtype=np.int64)
        local_out, _ = attention(q, k[recent], v[recent], max(world["temp"], 0.11))
        out = gate * out + (1.0 - gate) * local_out
    kept = set(int(i) for i in cand)
    order = np.argsort(-(k[cand] @ q)) if len(cand) else np.array([], dtype=np.int64)
    rank = 0
    if target in kept:
        inv = {int(cand[o]): int(r + 1) for r, o in enumerate(order)}
        rank = inv[target]
    rel = float(np.linalg.norm(out - full_out) / (np.linalg.norm(full_out) + 1e-8))
    cos = float(np.dot(out, v[target]) / ((np.linalg.norm(out) * np.linalg.norm(v[target])) + 1e-8))
    dropped = float(1.0 - np.sum(full_w[cand])) if len(cand) else 1.0
    return Row(
        seed=seed,
        scenario=scenario,
        method=method,
        n_records=n_records,
        dim=dim,
        budget=budget,
        hash_bits=hash_bits_count,
        candidate_count=int(len(cand)),
        target_in_candidates=int(target in kept),
        target_rank_in_candidates=rank,
        dropped_full_attention_mass=dropped,
        output_rel_error_vs_full=rel,
        target_value_cosine=cos,
        exact_success=float(target in kept and rank <= 3 and cos > 0.55),
        gate_weight=gate,
        read_fraction=float(len(cand) / n_records),
    )


def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for scenario in sorted({r.scenario for r in rows}):
        for method in sorted({r.method for r in rows}):
            sub = [r for r in rows if r.scenario == scenario and r.method == method]
            if not sub:
                continue
            by[f"{scenario}/{method}"] = {
                "mean_exact_success": float(np.mean([r.exact_success for r in sub])),
                "mean_target_in_candidates": float(np.mean([r.target_in_candidates for r in sub])),
                "mean_output_rel_error_vs_full": float(np.mean([r.output_rel_error_vs_full for r in sub])),
                "mean_dropped_full_attention_mass": float(np.mean([r.dropped_full_attention_mass for r in sub])),
                "mean_read_fraction": float(np.mean([r.read_fraction for r in sub])),
                "mean_gate_weight": float(np.mean([r.gate_weight for r in sub])),
            }
    winners = {}
    for scenario in sorted({r.scenario for r in rows}):
        candidates = []
        for method in sorted({r.method for r in rows}):
            m = by[f"{scenario}/{method}"]
            if method == "full_attention":
                continue
            score = m["mean_exact_success"] - 0.20 * m["mean_output_rel_error_vs_full"] - 0.05 * m["mean_read_fraction"]
            candidates.append((-score, method))
        candidates.sort()
        winners[scenario] = candidates[0][1]
    return {
        "row_count": len(rows),
        "by_scenario_method": by,
        "winners_excluding_full_attention": winners,
        "primary_metric": {
            "name": "mean_exact_success_minus_error_cost",
            "direction": "higher_is_better",
            "winner_field": "winners_excluding_full_attention",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0008_PCAF_SPARSE_MEMORY_SMOKE"))
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--n-records", type=int, default=512)
    ap.add_argument("--dim", type=int, default=48)
    args = ap.parse_args()
    scenarios = ["clean_old_successor", "noisy_bucket_collision", "recurring_entity_update", "rare_old_fact_vs_recent_noise"]
    methods = ["full_attention", "local_window", "semantic_topk_oracle", "pcaf_hash", "pcaf_hash_gate", "hash_plus_recency", "random_budget"]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for scenario in scenarios:
            for budget in [16, 32, 64]:
                for hbits in [8, 10]:
                    for method in methods:
                        rows.append(eval_method(seed, scenario, method, args.n_records, args.dim, budget, hbits))
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = out.with_suffix(".csv"), out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows(asdict(r) for r in rows)
    payload = {
        "probe": "pcaf_sparse_memory",
        "purpose": "Bounded hash/successor sparse memory vs full/local attention on synthetic long-context recall.",
        "config": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
        "rows": [asdict(r) for r in rows],
        "summary": summarize(rows),
        "csv": str(csv_path),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"]["winners_excluding_full_attention"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
