#!/usr/bin/env python3
"""CloudtainerML rev0042 canonical sparse compiler benchmark.

One shared score stream is passed through multiple hard-mask compilers. The goal
is not to declare a winner; it is to expose the exactness/cost frontier under a
single data generator so future lanes stop comparing unrelated toys.
"""
from __future__ import annotations
import hashlib
import json
import math
import platform
import random
import statistics
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
REV = "rev0042"
OUT = ROOT / "artifacts" / "probe-results" / "REV0042_CANONICAL_SPARSE_COMPILER_BENCHMARK.json"
N = 2048
K = 32
BLOCK = 64
STEPS = 20
SEEDS = [13, 29, 47, 61, 83, 101]
REGIMES = ["stable", "slow_drift", "bursty", "phase_shift", "flat"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def topk(scores: list[float], k: int = K) -> list[int]:
    return sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]


def softmax(scores: list[float]) -> list[float]:
    m = max(scores)
    ex = [math.exp(min(50.0, s - m)) for s in scores]
    z = sum(ex)
    return [e / z for e in ex]


def make_stream(regime: str, seed: int) -> list[list[float]]:
    rng = random.Random(seed)
    base = [rng.gauss(0, 1) for _ in range(N)]
    hot = [(seed * 17 + i * 97) % N for i in range(K)]
    rows: list[list[float]] = []
    for t in range(STEPS):
        rho = {"stable": 0.965, "slow_drift": 0.895, "bursty": 0.70, "phase_shift": 0.62, "flat": 0.80}[regime]
        x: list[float] = []
        for i in range(N):
            structural = 0.72 * math.cos((i - (seed + t * 3)) * 0.003) + 0.42 * math.cos((i % 257) * 0.017 + t * 0.03)
            noise = rng.gauss(0, 0.40)
            if t == 0:
                val = base[i] + structural + noise
            else:
                val = rho * rows[-1][i] + (1 - rho) * (base[i] + structural + noise)
            x.append(val)
        if regime == "stable":
            for h in hot: x[h] += 3.25
        elif regime == "slow_drift":
            for h in hot: x[(h + t * 7) % N] += 3.05
        elif regime == "bursty" and t % 4 == 1:
            for j in range(24): x[(seed * 13 + t * 151 + j * 59) % N] += 4.35
        elif regime == "phase_shift" and t > STEPS // 2:
            for j in range(32): x[(seed * 19 + j * 83 + N // 2) % N] += 4.0
        elif regime == "flat":
            x = [0.32 * v + rng.gauss(0, 0.58) for v in x]
        rows.append(x)
    return rows


@dataclass
class Pick:
    selected: list[int]
    exact_certified: bool
    fallback: bool
    fallback_reason: str
    candidate_count: int
    full_score_reads: int
    candidate_reads: int
    passes: int
    comparisons_est: int
    compiler_notes: str


def exact_heap(scores: list[float], prev: list[int] | None = None) -> Pick:
    return Pick(topk(scores), True, False, "none", K, N, K, 1, N * math.ceil(math.log2(K)), "full scan heap exact baseline")


def threshold_0p5(scores: list[float], prev: list[int] | None = None) -> Pick:
    # Fixed logistic threshold after z-normalizing the score row. This is intentionally brittle.
    mu = statistics.fmean(scores); sd = statistics.pstdev(scores) or 1.0
    selected = [i for i, s in enumerate(scores) if 1 / (1 + math.exp(-(s - mu) / sd)) >= 0.5]
    if len(selected) > K:
        selected = sorted(selected, key=lambda i: scores[i], reverse=True)[:K]
    return Pick(selected, False, False, "none", len(selected), 2 * N, len(selected), 2, len(selected) * math.ceil(math.log2(max(2, K))), "fixed threshold; not exact-certified")


def topp_0p92(scores: list[float], prev: list[int] | None = None) -> Pick:
    p = softmax(scores)
    order = sorted(range(N), key=lambda i: p[i], reverse=True)
    mass = 0.0; selected = []
    for i in order:
        selected.append(i); mass += p[i]
        if mass >= 0.92 or len(selected) >= 4 * K: break
    selected = sorted(selected, key=lambda i: scores[i], reverse=True)[:K]
    return Pick(selected, False, False, "none", len(selected), N, len(selected), 1, N * math.ceil(math.log2(N)), "Top-p candidate mass then top-K truncation; not exact-certified")


def hybrid_threshold_topk(scores: list[float], prev: list[int] | None = None) -> Pick:
    mu = statistics.fmean(scores); sd = statistics.pstdev(scores) or 1.0
    th = mu + 1.35 * sd
    cand = [i for i, s in enumerate(scores) if s >= th]
    if len(cand) < K:
        return exact_heap(scores)
    cand = sorted(cand, key=lambda i: scores[i], reverse=True)[:min(len(cand), 6 * K)]
    selected = cand[:K]
    # Not certified because omitted scores between cap and K could beat selected if cap truncates.
    return Pick(selected, False, len(cand) > 6 * K, "candidate_cap_truncated" if len(cand) > 6 * K else "none", len(cand), 2 * N, len(cand), 2, len(cand) * math.ceil(math.log2(max(2, K))), "threshold candidate then budgeted Top-K")


def block_index_certified(scores: list[float], prev: list[int] | None = None) -> Pick:
    blocks = [(b, max(scores[b:b + BLOCK])) for b in range(0, N, BLOCK)]
    # Select enough blocks to cover a 4K token budget, then certify by omitted-block max.
    selected_blocks = sorted(blocks, key=lambda x: x[1], reverse=True)[: max(1, (4 * K) // BLOCK)]
    block_ids = {b for b, _ in selected_blocks}
    cand = [i for b in block_ids for i in range(b, min(N, b + BLOCK))]
    cand_sorted = sorted(cand, key=lambda i: scores[i], reverse=True)
    selected = cand_sorted[:K]
    kth = scores[selected[-1]] if selected else -1e300
    omitted_block_max = max((mx for b, mx in blocks if b not in block_ids), default=-1e300)
    certified = kth >= omitted_block_max
    if not certified:
        fb = exact_heap(scores)
        fb.fallback = True; fb.fallback_reason = "omitted_block_max_above_kth"; fb.candidate_count = len(cand); fb.full_score_reads += N
        fb.compiler_notes = "block index failed certification and paid exact fallback"
        return fb
    return Pick(selected, True, False, "none", len(cand), N, len(cand), 1, len(blocks) + len(cand) * math.ceil(math.log2(K)), "block max index with kth-vs-omitted-block certifier")


def temporal_gvr_certified(scores: list[float], prev: list[int] | None = None) -> Pick:
    if not prev:
        fb = exact_heap(scores); fb.fallback = True; fb.fallback_reason = "no_previous_exact_topk"; return fb
    vals = [scores[i] for i in prev]
    prev_min = min(vals); prev_mean = statistics.fmean(vals); spread = max(0.05, prev_mean - prev_min)
    th = prev_min - 0.42 * (spread + 0.16)
    cand = []; omitted_max = -1e300
    for i, s in enumerate(scores):
        if s >= th: cand.append(i)
        elif s > omitted_max: omitted_max = s
    if len(cand) < K:
        fb = exact_heap(scores); fb.fallback = True; fb.fallback_reason = "candidate_underflow"; fb.candidate_count = len(cand); fb.full_score_reads += N; return fb
    if len(cand) > 8 * K:
        fb = exact_heap(scores); fb.fallback = True; fb.fallback_reason = "candidate_over_cap"; fb.candidate_count = len(cand); fb.full_score_reads += N; return fb
    selected = sorted(cand, key=lambda i: scores[i], reverse=True)[:K]
    kth = scores[selected[-1]]
    if kth < omitted_max:
        fb = exact_heap(scores); fb.fallback = True; fb.fallback_reason = "kth_below_omitted_max"; fb.candidate_count = len(cand); fb.full_score_reads += N; return fb
    return Pick(selected, True, False, "none", len(cand), N, len(cand), 1, len(cand) * math.ceil(math.log2(K)), "temporal threshold with kth-vs-omitted-max certifier")


COMPILERS: dict[str, Callable[[list[float], list[int] | None], Pick]] = {
    "exact_heap": exact_heap,
    "threshold_0p5": threshold_0p5,
    "topp_0p92": topp_0p92,
    "hybrid_threshold_topk": hybrid_threshold_topk,
    "block_index_certified": block_index_certified,
    "temporal_gvr_certified": temporal_gvr_certified,
}


def cost_proxy(p: Pick) -> float:
    return 0.000018 * p.full_score_reads + 0.000042 * p.candidate_reads + 0.00000035 * p.comparisons_est + 0.085 * p.passes + 0.06 * int(p.fallback)


def run() -> dict:
    rows = []
    timing_ns: dict[str, list[int]] = {name: [] for name in COMPILERS}
    for regime in REGIMES:
        for seed in SEEDS:
            stream = make_stream(regime, seed)
            prev_exact: list[int] | None = None
            for step, scores in enumerate(stream):
                truth = set(topk(scores))
                picks = {}
                for name, fn in COMPILERS.items():
                    t0_ns = time.perf_counter_ns()
                    pick = fn(scores, prev_exact)
                    elapsed_ns = time.perf_counter_ns() - t0_ns
                    timing_ns[name].append(elapsed_ns)
                    hit = len(set(pick.selected) & truth)
                    exact = hit == K
                    c = cost_proxy(pick)
                    score = 1.9 * (hit / K) - 0.72 * c - 0.75 * (1 - hit / K) + 0.06 * int(pick.exact_certified) - 0.08 * int(pick.fallback)
                    rows.append({
                        "regime": regime,
                        "seed": seed,
                        "step": step,
                        "compiler": name,
                        "exact": exact,
                        "hit": hit,
                        "misses": K - hit,
                        "exact_certified": pick.exact_certified,
                        "fallback": pick.fallback,
                        "fallback_reason": pick.fallback_reason,
                        "candidate_count": pick.candidate_count,
                        "full_score_reads": pick.full_score_reads,
                        "candidate_reads": pick.candidate_reads,
                        "passes": pick.passes,
                        "comparisons_est": pick.comparisons_est,
                        "bytes_touched_est": 8 * (pick.full_score_reads + pick.candidate_reads),
                        "elapsed_ns_python": elapsed_ns,
                        "cost_proxy": c,
                        "score": score,
                        "compiler_notes": pick.compiler_notes,
                    })
                    picks[name] = (score, pick)
                prev_exact = list(truth)
    # Add per-problem regret after all rows are present.
    by_key: dict[tuple, float] = {}
    for r in rows:
        key = (r["regime"], r["seed"], r["step"])
        by_key[key] = max(by_key.get(key, -1e300), r["score"])
    for r in rows:
        r["regret"] = by_key[(r["regime"], r["seed"], r["step"])] - r["score"]

    summary = {}
    for name in COMPILERS:
        rs = [r for r in rows if r["compiler"] == name]
        summary[name] = {
            "exact_rate": sum(r["exact"] for r in rs) / len(rs),
            "certified_rate": sum(r["exact_certified"] for r in rs) / len(rs),
            "fallback_rate": sum(r["fallback"] for r in rs) / len(rs),
            "mean_candidate_count": statistics.fmean(r["candidate_count"] for r in rs),
            "mean_full_score_reads": statistics.fmean(r["full_score_reads"] for r in rs),
            "mean_cost_proxy": statistics.fmean(r["cost_proxy"] for r in rs),
            "mean_elapsed_ns_python": statistics.fmean(r["elapsed_ns_python"] for r in rs),
            "median_elapsed_ns_python": statistics.median(r["elapsed_ns_python"] for r in rs),
            "mean_bytes_touched_est": statistics.fmean(r["bytes_touched_est"] for r in rs),
            "mean_regret": statistics.fmean(r["regret"] for r in rs),
            "mean_score": statistics.fmean(r["score"] for r in rs),
        }
    winner_counts: dict[str, int] = {name: 0 for name in COMPILERS}
    for key in by_key:
        candidates = [r for r in rows if (r["regime"], r["seed"], r["step"]) == key]
        winner = max(candidates, key=lambda r: r["score"])["compiler"]
        winner_counts[winner] += 1

    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "canonical_sparse_compiler_benchmark",
        "kind": "python_mechanism_benchmark",
        "source_ids": ["SRC-0348", "SRC-0356", "SRC-0357", "SRC-0362"],
        "cell_ids": ["CELL-350", "CELL-354"],
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "command": "python experiments/canonical_sparse_compiler_benchmark/canonical_sparse_compiler_benchmark.py",
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_implementation": platform.python_implementation(),
            "timing_method": "time.perf_counter_ns around each Python compiler call; named-platform microbenchmark, not a kernel-speed claim",
            "seed_policy": {"seeds": SEEDS, "steps": STEPS, "N": N, "K": K, "block": BLOCK},
        },
        "summary": {
            "primary_metric": {"name": "score", "direction": "higher_is_better"},
            "compiler_summary": summary,
            "winner_counts": winner_counts,
            "guard_fields": ["exact", "exact_certified", "fallback", "fallback_reason", "candidate_count", "full_score_reads", "candidate_reads", "passes", "comparisons_est", "bytes_touched_est", "elapsed_ns_python", "cost_proxy", "regret"],
            "timing_caveat": "elapsed_ns_python is a named-platform Python microbenchmark for relative audit pressure only. It is not a sparse attention kernel speed claim.",
            "interpretation": "One score stream now runs through threshold, Top-p, hybrid, block-index, temporal-GVR, and exact-heap compilers. Exactness/certification, byte/read estimates, and named-platform Python timing are visible on the same rows instead of spread across unrelated toys.",
        },
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
