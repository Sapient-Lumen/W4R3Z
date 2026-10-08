#!/usr/bin/env python3
"""Single-pass latent KV compactor toy probe.

A tiny analogue of Perceiver-style KV cache compaction: compact a full token KV
memory into a fixed number of latent slots in one pass, then answer future
queries from the compacted memory. The probe contrasts query-independent
compaction with query-aware top-k and full attention.

The hard case is an isolated needle: latent averaging can preserve cluster
structure while erasing rare but decisive tokens.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["clustered_topics", "isolated_needle", "many_small_facts", "topic_shift", "value_outliers"]
METHODS = ["full_attention", "random_tokens", "attention_topk", "centroid_slots", "still_latent_slots", "hybrid_latent_plus_topk"]


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-12)


def topk(x: np.ndarray, k: int) -> np.ndarray:
    k = max(1, min(int(k), len(x)))
    return np.argpartition(-x, k - 1)[:k].astype(np.int64)


def unit_rows(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-12)


def make_world(seed: int, regime: str, tokens: int, dim: int, clusters: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(42000 + seed)
    centers = unit_rows(rng.normal(size=(clusters, dim)))
    labels = rng.integers(0, clusters, size=tokens)
    k = centers[labels] + 0.28 * rng.normal(size=(tokens, dim))
    k = unit_rows(k).astype(np.float32)
    v = centers[labels] + 0.35 * rng.normal(size=(tokens, dim))
    critical = rng.choice(tokens, size=max(3, tokens // 32), replace=False)

    if regime == "isolated_needle":
        needle_dir = unit_rows(rng.normal(size=(1, dim)))[0]
        k[critical] = unit_rows(needle_dir + 0.05 * rng.normal(size=(len(critical), dim)))
        v[critical] = 3.0 * needle_dir + 0.05 * rng.normal(size=(len(critical), dim))
    elif regime == "many_small_facts":
        for i in critical:
            vec = unit_rows(rng.normal(size=(1, dim)))[0]
            k[i] = vec; v[i] = vec + 0.2 * rng.normal(size=dim)
    elif regime == "topic_shift":
        labels[: tokens // 2] = rng.integers(0, clusters // 2, size=tokens // 2)
        labels[tokens // 2 :] = rng.integers(clusters // 2, clusters, size=tokens - tokens // 2)
        k = unit_rows(centers[labels] + 0.22 * rng.normal(size=(tokens, dim))).astype(np.float32)
        v = centers[labels] + 0.25 * rng.normal(size=(tokens, dim))
        critical = np.arange(tokens // 2, tokens // 2 + max(3, tokens // 32))
    elif regime == "value_outliers":
        v[critical] *= 4.0
    # clustered_topics keeps default.
    return {"k": k.astype(np.float32), "v": v.astype(np.float32), "centers": centers.astype(np.float32), "critical": critical.astype(np.int64)}


def full_output(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
    a = softmax(k @ q * 5.0)
    return a @ v


def compact_centroids(k: np.ndarray, v: np.ndarray, slots: int, iters: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(99 + slots + len(k))
    c = k[rng.choice(len(k), size=slots, replace=False)].copy()
    for _ in range(iters):
        sim = k @ c.T
        lab = np.argmax(sim, axis=1)
        for j in range(slots):
            mask = lab == j
            if np.any(mask):
                c[j] = np.mean(k[mask], axis=0)
        c = c / (np.linalg.norm(c, axis=1, keepdims=True) + 1e-12)
    sim = k @ c.T
    lab = np.argmax(sim, axis=1)
    cv = np.zeros((slots, v.shape[1]), dtype=np.float64)
    for j in range(slots):
        mask = lab == j
        if np.any(mask):
            weights = softmax(sim[mask, j] * 2.0)
            cv[j] = weights @ v[mask]
    return c.astype(np.float32), cv.astype(np.float32)


def compact_still(k: np.ndarray, v: np.ndarray, slots: int) -> Tuple[np.ndarray, np.ndarray]:
    # Query-independent latent slots: deterministic low-discrepancy anchors from
    # a random projection of the key cloud. Each latent cross-attends the full KV.
    rng = np.random.default_rng(777 + slots + k.shape[1])
    anchors = unit_rows(rng.normal(size=(slots, k.shape[1])))
    scores = anchors @ k.T * 4.0
    weights = np.apply_along_axis(softmax, 1, scores)
    ck = weights @ k
    ck = unit_rows(ck)
    cv = weights @ v
    return ck.astype(np.float32), cv.astype(np.float32)


def method_output(method: str, q: np.ndarray, k: np.ndarray, v: np.ndarray, slots: int, rng: np.random.Generator) -> np.ndarray:
    if method == "full_attention":
        return full_output(q, k, v)
    if method == "random_tokens":
        idx = rng.choice(len(k), size=slots, replace=False)
        return full_output(q, k[idx], v[idx])
    if method == "attention_topk":
        idx = topk(k @ q, slots)
        return full_output(q, k[idx], v[idx])
    if method == "centroid_slots":
        ck, cv = compact_centroids(k, v, slots)
        return full_output(q, ck, cv)
    if method == "still_latent_slots":
        ck, cv = compact_still(k, v, slots)
        return full_output(q, ck, cv)
    if method == "hybrid_latent_plus_topk":
        local = max(1, slots // 3)
        latent_slots = max(1, slots - local)
        ck, cv = compact_still(k, v, latent_slots)
        idx = topk(k @ q, local)
        return full_output(q, np.concatenate([ck, k[idx]], axis=0), np.concatenate([cv, v[idx]], axis=0))
    raise ValueError(method)


@dataclass
class Row:
    seed: int
    regime: str
    slots: int
    method: str
    query_type: str
    reconstruction_error: float
    cosine_to_full: float
    critical_hit_proxy: float


def eval_rows(seed: int, regime: str, slots: int, tokens: int, dim: int, clusters: int, queries: int) -> List[Row]:
    rng = np.random.default_rng(51000 + seed + slots)
    world = make_world(seed, regime, tokens, dim, clusters)
    k, v, centers, critical = world["k"], world["v"], world["centers"], world["critical"]
    rows: List[Row] = []
    query_bank = []
    for _ in range(queries // 2):
        query_bank.append(("topic", centers[rng.integers(0, len(centers))] + 0.15 * rng.normal(size=dim)))
    for i in critical[: max(1, queries - len(query_bank))]:
        query_bank.append(("critical", k[int(i)] + 0.05 * rng.normal(size=dim)))
    for qtype, qraw in query_bank:
        q = qraw / (np.linalg.norm(qraw) + 1e-12)
        y = full_output(q, k, v)
        yn = np.linalg.norm(y) + 1e-12
        critical_mass_full = float(np.sum(softmax(k @ q * 5.0)[critical]))
        for method in METHODS:
            yh = method_output(method, q, k, v, slots, rng)
            err = float(np.linalg.norm(y - yh) / yn)
            cos = float(np.dot(y, yh) / ((np.linalg.norm(y) + 1e-12) * (np.linalg.norm(yh) + 1e-12)))
            # If full attention would need critical tokens, did the method reconstruct that output?
            crit_proxy = float((critical_mass_full > 0.25) and (cos > 0.85))
            rows.append(Row(seed, regime, slots, method, qtype, err, cos, crit_proxy))
    return rows


def run(seeds: int, tokens: int, dim: int, clusters: int, slots_list: List[int], queries: int) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for slots in slots_list:
                rows.extend(eval_rows(seed, regime, slots, tokens, dim, clusters, queries))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int, str], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.slots, r.query_type), {}).setdefault(r.method, []).append(r.reconstruction_error)
    winners: Dict[str, str] = {}; counts: Dict[str, int] = {}
    practical: Dict[str, str] = {}; pcounts: Dict[str, int] = {}
    for (regime, slots, qt), methods in by.items():
        means = {m: float(np.mean(v)) for m, v in methods.items()}
        w = min(means, key=means.get); winners[f"{regime}/S{slots}/{qt}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {m: e for m, e in means.items() if m != "full_attention"}
        pw = min(means2, key=means2.get); practical[f"{regime}/S{slots}/{qt}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "reconstruction_error", "direction": "lower_is_better", "winner_field": "winners_excluding_full_attention"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_full_attention": practical,
        "winner_counts_excluding_full_attention": pcounts,
        "interpretation": "One-pass latent compaction should beat random tokens on cluster structure but can erase isolated needles unless hybridized with query-aware top-k.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0010", "probe": "still_compactor", "config": {"regimes": REGIMES, "methods": METHODS}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--tokens", type=int, default=160)
    ap.add_argument("--dim", type=int, default=40)
    ap.add_argument("--clusters", type=int, default=8)
    ap.add_argument("--slots-list", type=int, nargs="+", default=[8, 16, 32])
    ap.add_argument("--queries", type=int, default=10)
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0010_STILL_COMPACTOR_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0010_STILL_COMPACTOR_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.tokens, args.dim, args.clusters, args.slots_list, args.queries)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
