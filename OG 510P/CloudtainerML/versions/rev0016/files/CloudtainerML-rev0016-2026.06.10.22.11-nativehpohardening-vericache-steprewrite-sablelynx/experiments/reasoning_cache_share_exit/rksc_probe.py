#!/usr/bin/env python3
"""Reasoning-cache sharing + early-exit toy.

Inspired by RKSC-style multi-branch reasoning: similar branches can share prefix
cache, and verification can sometimes stop early when confidence/entropy is
stable. This toy simulates branch clusters, hidden-state similarity, answer
confidence, and layer entropy curves; it reports the speed/error tradeoff.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["clean_clusters", "near_miss_branches", "late_divergence", "confidence_trap", "many_small_clusters"]
POLICIES = ["no_share_no_exit", "exact_prefix_only", "similarity_share", "conservative_share", "sim_share_conf_exit", "sim_share_entropy_exit", "oracle_cluster_exit"]


def make_branches(seed: int, regime: str, branches: int, dim: int, layers: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(103000 + seed)
    if regime == "many_small_clusters":
        n_clusters = max(3, branches // 2)
    else:
        n_clusters = 3
    cluster = np.arange(branches) % n_clusters
    rng.shuffle(cluster)
    centers = rng.normal(0, 1, size=(n_clusters, dim))
    centers /= np.linalg.norm(centers, axis=1, keepdims=True) + 1e-9
    noise = {
        "clean_clusters": 0.08,
        "near_miss_branches": 0.22,
        "late_divergence": 0.12,
        "confidence_trap": 0.11,
        "many_small_clusters": 0.13,
    }[regime]
    hidden = centers[cluster] + rng.normal(0, noise, size=(branches, dim))
    hidden /= np.linalg.norm(hidden, axis=1, keepdims=True) + 1e-9
    # exact prefixes are rarer than semantic similarity
    prefix_id = cluster.copy()
    if regime in {"near_miss_branches", "late_divergence"}:
        prefix_id = np.arange(branches)  # no exact reuse anchor
    else:
        prefix_id = cluster * 10 + rng.integers(0, 2, size=branches)
    base_conf = rng.uniform(0.55, 0.92, size=branches)
    if regime == "confidence_trap":
        wrong = rng.choice(branches, size=max(1, branches // 3), replace=False)
        base_conf[wrong] = rng.uniform(0.9, 0.99, size=len(wrong))
    else:
        wrong = rng.choice(branches, size=max(1, branches // 8), replace=False)
    correct = np.ones(branches, dtype=bool); correct[wrong] = False
    entropy = np.zeros((branches, layers), dtype=np.float64)
    for b in range(branches):
        start = rng.uniform(1.2, 2.0)
        end = rng.uniform(0.05, 0.45) if correct[b] else rng.uniform(0.35, 0.95)
        curve = np.linspace(start, end, layers) + rng.normal(0, 0.06, size=layers)
        if regime == "late_divergence" and b % 3 == 0:
            curve[: layers // 2] *= 0.35
            curve[layers // 2 :] += 0.65
        entropy[b] = np.clip(curve, 0.01, 2.5)
    return {"cluster": cluster, "hidden": hidden, "prefix_id": prefix_id, "confidence": base_conf, "correct": correct, "entropy": entropy}


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b.T


def cache_groups(policy: str, data: Dict[str, np.ndarray], threshold: float) -> Tuple[np.ndarray, float]:
    n = len(data["cluster"])
    groups = np.arange(n)
    if policy == "no_share_no_exit":
        return groups, 1.0
    if policy == "exact_prefix_only":
        _, groups = np.unique(data["prefix_id"], return_inverse=True)
        return groups, len(set(groups.tolist())) / n
    if policy in {"similarity_share", "sim_share_conf_exit", "sim_share_entropy_exit"}:
        sim = cosine(data["hidden"], data["hidden"])
        groups = -np.ones(n, dtype=int)
        gid = 0
        for i in range(n):
            if groups[i] >= 0:
                continue
            close = np.where(sim[i] >= threshold)[0]
            groups[close] = gid
            gid += 1
        return groups, gid / n
    if policy == "conservative_share":
        sim = cosine(data["hidden"], data["hidden"])
        groups = -np.ones(n, dtype=int); gid = 0
        for i in range(n):
            if groups[i] >= 0:
                continue
            close = np.where((sim[i] >= threshold + 0.08) & (data["prefix_id"] == data["prefix_id"][i]))[0]
            groups[close] = gid; gid += 1
        return groups, gid / n
    if policy == "oracle_cluster_exit":
        _, groups = np.unique(data["cluster"], return_inverse=True)
        return groups, len(set(groups.tolist())) / n
    raise ValueError(policy)


def exit_fraction(policy: str, data: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    conf = data["confidence"]
    ent = data["entropy"]
    n, layers = ent.shape
    frac = np.ones(n, dtype=np.float64)
    exit_ok = np.ones(n, dtype=bool)
    if policy in {"no_share_no_exit", "exact_prefix_only", "similarity_share", "conservative_share"}:
        return frac, exit_ok
    if policy == "sim_share_conf_exit":
        early = conf >= 0.88
        frac[early] = 0.35
        exit_ok[early] = data["correct"][early] | (conf[early] < 0.95)
        return frac, exit_ok
    if policy == "sim_share_entropy_exit":
        # Exit when entropy stabilizes low for two adjacent layers.
        for i in range(n):
            diffs = np.abs(np.diff(ent[i]))
            candidates = np.where((ent[i, 1:] < 0.55) & (diffs < 0.08))[0]
            if len(candidates):
                layer = int(candidates[0] + 1)
                frac[i] = max(0.25, (layer + 1) / ent.shape[1])
                exit_ok[i] = data["correct"][i] or ent[i, -1] < 0.35
        return frac, exit_ok
    if policy == "oracle_cluster_exit":
        frac[data["correct"]] = 0.32
        frac[~data["correct"]] = 0.9
        return frac, np.ones(n, dtype=bool)
    raise ValueError(policy)


@dataclass
class Row:
    seed: int
    regime: str
    branches: int
    policy: str
    threshold: float
    cache_compute_fraction: float
    verify_compute_fraction: float
    total_compute_fraction: float
    implied_speedup: float
    share_error_rate: float
    early_exit_error_rate: float
    total_error_rate: float
    utility: float


def eval_one(seed: int, regime: str, branches: int, layers: int, dim: int, policy: str, threshold: float) -> Row:
    d = make_branches(seed, regime, branches, dim, layers)
    groups, cache_frac = cache_groups(policy, d, threshold)
    share_bad = np.zeros(branches, dtype=bool)
    for g in set(groups.tolist()):
        idx = np.where(groups == g)[0]
        if len(set(d["cluster"][idx].tolist())) > 1:
            share_bad[idx] = True
    frac, exit_ok = exit_fraction(policy, d)
    verify_frac = float(np.mean(frac))
    total_frac = float(0.55 * cache_frac + 0.45 * verify_frac)
    share_err = float(np.mean(share_bad))
    exit_err = float(np.mean(~exit_ok))
    total_err = float(np.mean(share_bad | (~exit_ok)))
    speedup = float(1.0 / max(total_frac, 1e-9))
    utility = float(speedup - 8.0 * total_err)
    return Row(seed, regime, branches, policy, threshold, cache_frac, verify_frac, total_frac, speedup, share_err, exit_err, total_err, utility)


def run(seeds: int, branches: int, layers: int, dim: int, thresholds: List[float]) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for threshold in thresholds:
                for policy in POLICIES:
                    rows.append(eval_one(seed, regime, branches, layers, dim, policy, threshold))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, float], Dict[str, List[float]]] = {}
    err: Dict[Tuple[str, float], Dict[str, List[float]]] = {}
    for r in rows:
        key = (r.regime, r.threshold)
        by.setdefault(key, {}).setdefault(r.policy, []).append(r.utility)
        err.setdefault(key, {}).setdefault(r.policy, []).append(r.total_error_rate)
    winners = {}; counts: Dict[str, int] = {}
    safe_winners = {}; safe_counts: Dict[str, int] = {}
    for (regime, thr), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get); winners[f"{regime}/T{thr:.2f}"] = w; counts[w] = counts.get(w, 0) + 1
        eligible = {p: means[p] for p in means if p != "oracle_cluster_exit" and float(np.mean(err[(regime, thr)][p])) <= 0.05}
        if not eligible:
            eligible = {p: means[p] for p in means if p != "oracle_cluster_exit"}
        sw = max(eligible, key=eligible.get); safe_winners[f"{regime}/T{thr:.2f}"] = sw; safe_counts[sw] = safe_counts.get(sw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "utility", "direction": "higher_is_better", "winner_field": "safe_winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "safe_winners_excluding_oracle": safe_winners,
        "safe_winner_counts_excluding_oracle": safe_counts,
        "interpretation": "Reasoning-cache sharing is attractive only if similarity thresholds avoid near-miss branch contamination and early exit does not trust high-confidence wrong branches.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0011", "probe": "reasoning_cache_share_exit", "config": {"regimes": REGIMES, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader(); w.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=18)
    ap.add_argument("--branches", type=int, default=18)
    ap.add_argument("--layers", type=int, default=16)
    ap.add_argument("--dim", type=int, default=24)
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.72, 0.82, 0.90])
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0011_REASONING_CACHE_SHARE_EXIT_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0011_REASONING_CACHE_SHARE_EXIT_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.branches, args.layers, args.dim, args.thresholds)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
