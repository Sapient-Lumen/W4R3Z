#!/usr/bin/env python3
"""CloudtainerML attention-row sparse compiler benchmark.

This probe closes the largest remaining evidence gap from rev0042/rev0043: sparse
compilers are no longer scored only on Top-K membership over synthetic score
streams. Each method is applied to actual QK-derived attention rows and is
judged by its dense-softmax/V output error, retained attention mass, value-read
cost, Top-K exactness, and measured Python call timing.

The benchmark remains synthetic and CPU/Python. It is evidence tier E2:
attention-output workload evidence, not a sparse attention kernel speed claim.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0044"}
REV = META.get("revision", "rev0044")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_ATTENTION_ROW_COMPILER_BENCHMARK.json"
N = 1024
D = 32
DV = 16
K = 32
BLOCK = 64
STEPS = 12
SEEDS = [17, 31, 47, 59, 73, 89]
REGIMES = [
    "local_band",
    "retrieval_needle",
    "distractor_plateau",
    "phase_shift",
    "flat_low_margin",
    "block_alias",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_softmax(x: np.ndarray) -> np.ndarray:
    y = x - float(np.max(x))
    e = np.exp(np.clip(y, -80.0, 80.0))
    z = float(np.sum(e))
    return e / z if z > 0 else np.full_like(x, 1.0 / len(x), dtype=np.float64)


def topk_indices(scores: np.ndarray, k: int = K) -> np.ndarray:
    if k >= len(scores):
        return np.argsort(-scores)
    part = np.argpartition(-scores, k - 1)[:k]
    return part[np.argsort(-scores[part])]


def normalize_rows(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(1e-9, np.linalg.norm(x, axis=1, keepdims=True))


@dataclass
class AttentionRow:
    regime: str
    seed: int
    step: int
    scores: np.ndarray
    values: np.ndarray
    dense_probs: np.ndarray
    dense_out: np.ndarray
    local_window: np.ndarray
    note: str


@dataclass
class Pick:
    selected: np.ndarray
    exact_topk_certified: bool
    fallback: bool
    fallback_reason: str
    candidate_count: int
    qk_dot_products: int
    score_reads: int
    candidate_score_reads: int
    value_reads: int
    softmax_terms: int
    passes: int
    comparisons_est: int
    compiler_notes: str


def make_stream(regime: str, seed: int) -> list[AttentionRow]:
    rng = np.random.default_rng(seed)
    token_pos = np.arange(N, dtype=np.float64)
    base_keys = normalize_rows(rng.normal(0.0, 1.0, size=(N, D)))
    # Values mix random content with a weak positional signal so output error is
    # not equivalent to probability-mass error.
    values = rng.normal(0.0, 0.55, size=(N, DV))
    values[:, 0] += np.sin(token_pos * 0.019)
    values[:, 1] += np.cos(token_pos * 0.013)
    values[:, 2] += (token_pos % BLOCK) / BLOCK - 0.5
    rows: list[AttentionRow] = []
    prev_q = normalize_rows(rng.normal(0.0, 1.0, size=(1, D)))[0]
    for step in range(STEPS):
        keys = np.array(base_keys, copy=True)
        vals = np.array(values, copy=True)
        local_center = N - 1 - min(N // 4, step * 11)
        local_band = np.exp(-np.maximum(0.0, local_center - token_pos) / 74.0)
        local_band *= (token_pos <= local_center)
        local_window = np.arange(max(0, local_center - 127), local_center + 1, dtype=np.int64)

        q = 0.72 * prev_q + 0.28 * normalize_rows(rng.normal(0.0, 1.0, size=(1, D)))[0]
        note = "base_qk_row"

        if regime == "local_band":
            q = 0.62 * q + 0.38 * base_keys[local_center]
            vals[local_window, 3] += 0.18
            note = "local recency-biased row"
        elif regime == "retrieval_needle":
            targets = np.array([(seed * 37 + step * 43 + j * 149) % (N - 160) for j in range(6)], dtype=np.int64)
            q = 0.26 * q + 0.74 * normalize_rows(np.mean(base_keys[targets], axis=0, keepdims=True))[0]
            vals[targets, 4:8] += np.array([1.3, -0.9, 0.7, -0.4])
            note = "remote retrieval needles with distinctive values"
        elif regime == "distractor_plateau":
            targets = np.array([(seed * 19 + step * 23 + j * 131) % N for j in range(8)], dtype=np.int64)
            distractors = np.array([(seed * 97 + step * 17 + j * 61) % N for j in range(72)], dtype=np.int64)
            proto = normalize_rows(np.mean(base_keys[targets], axis=0, keepdims=True))[0]
            keys[targets] = normalize_rows(0.55 * keys[targets] + 0.45 * proto)
            keys[distractors] = normalize_rows(0.72 * keys[distractors] + 0.28 * proto)
            q = 0.22 * q + 0.78 * proto
            vals[targets, 8:12] += np.array([1.1, -1.0, 0.8, -0.6])
            vals[distractors, 8:12] += np.array([-0.35, 0.28, -0.20, 0.18])
            note = "many near-top distractors with different values"
        elif regime == "phase_shift":
            a = np.array([(seed * 11 + j * 83) % N for j in range(10)], dtype=np.int64)
            b = np.array([(N // 2 + seed * 13 + j * 79) % N for j in range(10)], dtype=np.int64)
            active = a if step < STEPS // 2 else b
            q = 0.30 * q + 0.70 * normalize_rows(np.mean(base_keys[active], axis=0, keepdims=True))[0]
            vals[active, 5] += 0.9
            note = "temporal active set changes halfway"
        elif regime == "flat_low_margin":
            # Deliberately low-temperature row: Top-K identity is unstable and
            # retaining enough mass may require a much wider sparse set.
            q = normalize_rows(0.38 * q + 0.62 * rng.normal(0.0, 1.0, size=D)[None, :])[0]
            vals[:, 6] += 0.08 * rng.normal(0.0, 1.0, size=N)
            note = "flat low-margin row where exact Top-K is not enough"
        elif regime == "block_alias":
            target_block = (seed + 3 * step) % (N // BLOCK)
            alias_blocks = [(target_block + off) % (N // BLOCK) for off in (5, 11, 17)]
            target_ids = np.arange(target_block * BLOCK, (target_block + 1) * BLOCK, dtype=np.int64)
            proto = normalize_rows(np.mean(base_keys[target_ids[::8]], axis=0, keepdims=True))[0]
            q = 0.25 * q + 0.75 * proto
            for b in alias_blocks:
                ids = np.arange(b * BLOCK, (b + 1) * BLOCK, dtype=np.int64)
                keys[ids] = normalize_rows(0.80 * keys[ids] + 0.20 * proto)
                vals[ids, 9] -= 0.18
            vals[target_ids, 9] += 0.28
            note = "block summary aliasing against similar non-target blocks"

        q = q / max(1e-9, float(np.linalg.norm(q)))
        prev_q = q
        scores = (keys @ q) * math.sqrt(D)
        if regime in {"local_band", "block_alias"}:
            scores = scores + 0.42 * local_band
        if regime == "flat_low_margin":
            scores = 0.42 * scores + rng.normal(0.0, 0.035, size=N)
        dense_probs = stable_softmax(scores)
        dense_out = dense_probs @ vals
        rows.append(AttentionRow(regime, seed, step, scores.astype(np.float64), vals.astype(np.float64), dense_probs, dense_out, local_window, note))
    return rows


def dense_full(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    selected = np.arange(len(row.scores), dtype=np.int64)
    return Pick(selected, True, False, "none", N, N, N, N, N, N, 1, N, "dense full softmax/V exact output baseline")


def exact_topk_sparse(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    sel = topk_indices(row.scores, K)
    return Pick(sel, True, False, "none", K, N, N, K, K, K, 1, int(N * math.ceil(math.log2(K))), "full-score exact Top-K sparse attention; exact selector, approximate output")


def local_window_128(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    sel = row.local_window.astype(np.int64)
    return Pick(sel, False, False, "none", len(sel), len(sel), len(sel), len(sel), len(sel), len(sel), 1, len(sel), "cheap local-window baseline; no global exactness")


def threshold_mu_1p3sd(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    s = row.scores
    th = float(np.mean(s) + 1.3 * (np.std(s) or 1.0))
    cand = np.flatnonzero(s >= th)
    fallback = False
    reason = "none"
    if len(cand) < K:
        cand = topk_indices(s, K)
        fallback = True
        reason = "threshold_underflow_topk_fill"
    elif len(cand) > 6 * K:
        cand = cand[np.argsort(-s[cand])[: 6 * K]]
        fallback = True
        reason = "threshold_cap_truncated"
    return Pick(cand.astype(np.int64), False, fallback, reason, len(cand), N, N, len(cand), len(cand), len(cand), 2, int(len(cand) * math.ceil(math.log2(max(2, K)))), "z-threshold sparse set; output judged against dense")


def topp_0p95(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    order = np.argsort(-row.scores)
    mass = 0.0
    keep: list[int] = []
    for i in order:
        keep.append(int(i))
        mass += float(row.dense_probs[i])
        if mass >= 0.95:
            break
    sel = np.array(keep, dtype=np.int64)
    return Pick(sel, False, False, "none", len(sel), N, N, len(sel), len(sel), len(sel), 1, int(N * math.ceil(math.log2(N))), "Uncapped Top-p 0.95 using full dense probability order; high quality but often too wide/expensive")


def blockmax_4block_certified(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    s = row.scores
    block_count = N // BLOCK
    block_max = np.array([float(np.max(s[b * BLOCK : (b + 1) * BLOCK])) for b in range(block_count)])
    block_ids = np.argsort(-block_max)[:4]
    cand = np.concatenate([np.arange(b * BLOCK, (b + 1) * BLOCK, dtype=np.int64) for b in block_ids])
    selected_topk = cand[np.argsort(-s[cand])[:K]]
    kth = float(np.min(s[selected_topk]))
    omitted = [b for b in range(block_count) if b not in set(int(x) for x in block_ids)]
    omitted_max = max([float(block_max[b]) for b in omitted], default=-1e300)
    certified = kth >= omitted_max
    fallback = False
    reason = "none"
    if not certified:
        selected_topk = topk_indices(s, K)
        fallback = True
        reason = "omitted_block_max_above_kth_topk_fallback"
    # Use top-K inside selected blocks for deployment, not the whole block, so we
    # measure output loss from a common K-sized sparse contract.
    return Pick(selected_topk.astype(np.int64), bool(certified), fallback, reason, len(cand), N, N, len(cand), len(selected_topk), len(selected_topk), 1, int(block_count + len(cand) * math.ceil(math.log2(K))), "block-max candidate set with kth-vs-omitted-block certifier; falls back to exact Top-K")


def temporal_gvr_certified(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    s = row.scores
    if prev is None or len(prev) < K:
        sel = topk_indices(s, K)
        return Pick(sel, True, True, "no_previous_exact_topk", K, N, N, K, K, K, 1, int(N * math.ceil(math.log2(K))), "first row exact fallback")
    vals = s[prev]
    prev_min = float(np.min(vals))
    prev_mean = float(np.mean(vals))
    spread = max(0.05, prev_mean - prev_min)
    th = prev_min - 0.42 * (spread + 0.16)
    cand = np.flatnonzero(s >= th)
    omitted_max = float(np.max(s[s < th])) if np.any(s < th) else -1e300
    if len(cand) < K:
        sel = topk_indices(s, K)
        return Pick(sel, True, True, "candidate_underflow_topk_fallback", len(cand), N, N, len(cand), K, K, 1, int(N * math.ceil(math.log2(K))), "temporal threshold underflow fallback")
    if len(cand) > 8 * K:
        sel = topk_indices(s, K)
        return Pick(sel, True, True, "candidate_over_cap_topk_fallback", len(cand), N, N, len(cand), K, K, 1, int(N * math.ceil(math.log2(K))), "temporal threshold over-cap fallback")
    sel = cand[np.argsort(-s[cand])[:K]]
    kth = float(np.min(s[sel]))
    if kth < omitted_max:
        sel = topk_indices(s, K)
        return Pick(sel, True, True, "kth_below_omitted_max_topk_fallback", len(cand), N, N, len(cand), K, K, 1, int(N * math.ceil(math.log2(K))), "temporal certifier failed fallback")
    return Pick(sel.astype(np.int64), True, False, "none", len(cand), N, N, len(cand), K, K, 1, int(len(cand) * math.ceil(math.log2(K))), "temporal threshold with kth-vs-omitted-max Top-K certifier")


def prev_only_reuse(row: AttentionRow, prev: np.ndarray | None) -> Pick:
    if prev is None or len(prev) == 0:
        sel = row.local_window[-K:].astype(np.int64)
        reason = "no_previous_use_local_tail"
    else:
        sel = prev[:K].astype(np.int64)
        reason = "none"
    return Pick(sel, False, False, reason, len(sel), len(sel), len(sel), len(sel), len(sel), len(sel), 0, len(sel), "very cheap previous-index reuse; deliberately uncertified")


COMPILERS: dict[str, Callable[[AttentionRow, np.ndarray | None], Pick]] = {
    "dense_full": dense_full,
    "exact_topk_sparse": exact_topk_sparse,
    "local_window_128": local_window_128,
    "threshold_mu_1p3sd": threshold_mu_1p3sd,
    "topp_0p95": topp_0p95,
    "blockmax_4block_certified": blockmax_4block_certified,
    "temporal_gvr_certified": temporal_gvr_certified,
    "prev_only_reuse": prev_only_reuse,
}


def sparse_output(row: AttentionRow, selected: np.ndarray) -> tuple[np.ndarray, float, float]:
    if len(selected) == 0:
        return np.zeros_like(row.dense_out), 0.0, 0.0
    selected = np.unique(selected.astype(np.int64))
    p = stable_softmax(row.scores[selected])
    out = p @ row.values[selected]
    mass = float(np.sum(row.dense_probs[selected]))
    dense_entropy = -float(np.sum(row.dense_probs * np.log(np.maximum(row.dense_probs, 1e-30))))
    return out, mass, dense_entropy


def row_metrics(row: AttentionRow, pick: Pick, truth_topk: np.ndarray, elapsed_ns: int) -> dict:
    selected = np.unique(pick.selected.astype(np.int64))
    out, mass, dense_entropy = sparse_output(row, selected)
    dense_norm = float(np.linalg.norm(row.dense_out))
    err = float(np.linalg.norm(out - row.dense_out))
    rel = err / max(1.0e-9, dense_norm)
    denom = max(1e-12, float(np.linalg.norm(out)) * dense_norm)
    cosine = float(np.dot(out, row.dense_out) / denom) if denom > 0 else 0.0
    cosine = max(-1.0, min(1.0, cosine))
    topk_hit = len(set(map(int, selected)) & set(map(int, truth_topk)))
    topk_exact = topk_hit == min(K, len(selected)) and len(selected) == K and set(map(int, selected)) == set(map(int, truth_topk))
    bytes_touched = 4 * (pick.score_reads + pick.candidate_score_reads + pick.value_reads * DV + pick.qk_dot_products * D)
    cost_proxy = (
        0.000010 * pick.qk_dot_products
        + 0.000004 * pick.score_reads
        + 0.000009 * pick.value_reads * DV
        + 0.0000004 * pick.comparisons_est
        + 0.050 * pick.passes
        + 0.045 * int(pick.fallback)
    )
    quality_score = max(0.0, cosine) + 0.62 * mass - 0.72 * min(2.5, rel) - 0.020 * math.log1p(max(0, len(selected) - K)) - 0.11 * cost_proxy
    return {
        "selected_count": int(len(selected)),
        "topk_hit": int(topk_hit),
        "topk_hit_rate": float(topk_hit / K),
        "topk_exact": bool(topk_exact),
        "exact_topk_certified": bool(pick.exact_topk_certified),
        "fallback": bool(pick.fallback),
        "fallback_reason": pick.fallback_reason,
        "candidate_count": int(pick.candidate_count),
        "qk_dot_products": int(pick.qk_dot_products),
        "score_reads": int(pick.score_reads),
        "candidate_score_reads": int(pick.candidate_score_reads),
        "value_reads": int(pick.value_reads),
        "softmax_terms": int(pick.softmax_terms),
        "passes": int(pick.passes),
        "comparisons_est": int(pick.comparisons_est),
        "bytes_touched_est": int(bytes_touched),
        "elapsed_ns_python": int(elapsed_ns),
        "dense_attention_output_norm": dense_norm,
        "attention_l2_error": err,
        "attention_rel_l2_error": rel,
        "output_cosine": cosine,
        "mass_retained": mass,
        "dense_entropy": dense_entropy,
        "quality_score": quality_score,
        "passes_quality_bar": bool(cosine >= 0.995 and mass >= 0.95 and rel <= 0.18),
        "compiler_notes": pick.compiler_notes,
    }


def summarize(rows: list[dict]) -> tuple[dict, dict, dict]:
    by: dict[str, list[dict]] = {name: [] for name in COMPILERS}
    for r in rows:
        by[r["compiler"]].append(r)
    summary: dict[str, dict] = {}
    for name, xs in by.items():
        if not xs:
            continue
        summary[name] = {
            "mean_quality_score": statistics.fmean(x["quality_score"] for x in xs),
            "mean_attention_rel_l2_error": statistics.fmean(x["attention_rel_l2_error"] for x in xs),
            "p90_attention_rel_l2_error": sorted(x["attention_rel_l2_error"] for x in xs)[int(0.90 * (len(xs) - 1))],
            "mean_output_cosine": statistics.fmean(x["output_cosine"] for x in xs),
            "mean_mass_retained": statistics.fmean(x["mass_retained"] for x in xs),
            "mean_topk_hit_rate": statistics.fmean(x["topk_hit_rate"] for x in xs),
            "quality_bar_rate": statistics.fmean(float(x["passes_quality_bar"]) for x in xs),
            "fallback_rate": statistics.fmean(float(x["fallback"]) for x in xs),
            "mean_selected_count": statistics.fmean(x["selected_count"] for x in xs),
            "mean_value_reads": statistics.fmean(x["value_reads"] for x in xs),
            "mean_qk_dot_products": statistics.fmean(x["qk_dot_products"] for x in xs),
            "mean_elapsed_ns_python": statistics.fmean(x["elapsed_ns_python"] for x in xs),
            "mean_bytes_touched_est": statistics.fmean(x["bytes_touched_est"] for x in xs),
        }
    winner_counts = {name: 0 for name in COMPILERS}
    sparse_quality_winner_counts = {name: 0 for name in COMPILERS if name != "dense_full"}
    group_keys = sorted({(r["regime"], r["seed"], r["step"]) for r in rows})
    for key in group_keys:
        group = [r for r in rows if (r["regime"], r["seed"], r["step"]) == key]
        winner_counts[max(group, key=lambda r: r["quality_score"])["compiler"]] += 1
        sparse = [r for r in group if r["compiler"] != "dense_full"]
        sparse_quality_winner_counts[max(sparse, key=lambda r: r["quality_score"])["compiler"]] += 1
    regime_summary: dict[str, dict] = {}
    for regime in REGIMES:
        regime_summary[regime] = {}
        for name in COMPILERS:
            xs = [r for r in rows if r["regime"] == regime and r["compiler"] == name]
            regime_summary[regime][name] = {
                "mean_rel_l2": statistics.fmean(x["attention_rel_l2_error"] for x in xs),
                "mean_mass": statistics.fmean(x["mass_retained"] for x in xs),
                "quality_bar_rate": statistics.fmean(float(x["passes_quality_bar"]) for x in xs),
            }
    return summary, winner_counts, {"sparse_quality_winner_counts": sparse_quality_winner_counts, "regime_summary": regime_summary}


def run() -> dict:
    rows: list[dict] = []
    for regime in REGIMES:
        for seed in SEEDS:
            prev_exact: np.ndarray | None = None
            for row in make_stream(regime, seed):
                truth = topk_indices(row.scores, K)
                for name, fn in COMPILERS.items():
                    t0 = time.perf_counter_ns()
                    pick = fn(row, prev_exact)
                    elapsed = time.perf_counter_ns() - t0
                    m = row_metrics(row, pick, truth, elapsed)
                    m.update({
                        "regime": regime,
                        "seed": seed,
                        "step": row.step,
                        "compiler": name,
                        "row_note": row.note,
                        "N": N,
                        "D": D,
                        "DV": DV,
                        "K": K,
                        "block": BLOCK,
                    })
                    rows.append(m)
                prev_exact = truth
    summary, winner_counts, extra = summarize(rows)
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "attention_row_compiler_benchmark",
        "kind": "python_attention_workload_benchmark",
        "evidence_tier": "E2_synthetic_attention_output_workload",
        "source_ids": ["SRC-0348", "SRC-0356", "SRC-0357", "SRC-0362"],
        "cell_ids": ["CELL-350", "CELL-354"],
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "command": "python experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "timing_method": "time.perf_counter_ns around each Python selector call; attention output is evaluated with NumPy dense softmax/V reference; not a kernel speed claim",
            "seed_policy": {"seeds": SEEDS, "steps": STEPS, "N": N, "D": D, "DV": DV, "K": K, "block": BLOCK},
        },
        "summary": {
            "primary_metric": {"name": "quality_score", "direction": "higher_is_better"},
            "score_source": "scores are generated as QK dot products plus explicit positional/logit biases where noted; outputs are dense softmax(scores) @ V versus sparse softmax(scores[selected]) @ V",
            "compiler_summary": summary,
            "winner_counts": winner_counts,
            **extra,
            "guard_fields": [
                "attention_rel_l2_error",
                "attention_l2_error",
                "output_cosine",
                "mass_retained",
                "dense_attention_output_norm",
                "topk_hit_rate",
                "topk_exact",
                "exact_topk_certified",
                "selected_count",
                "value_reads",
                "qk_dot_products",
                "bytes_touched_est",
                "elapsed_ns_python",
                "fallback",
                "fallback_reason",
                "quality_score",
            ],
            "interpretation": f"{REV} reruns the attention-output test. Sparse compilers are now penalized when exact Top-K preservation does not preserve dense softmax/V output. This is synthetic E2 evidence and still leaves kernel timing and real model traces as blockers.",
        },
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT.relative_to(ROOT)),
        "rows": len(payload["rows"]),
        "winner_counts": payload["summary"]["winner_counts"],
        "sparse_quality_winner_counts": payload["summary"]["sparse_quality_winner_counts"],
        "compiler_summary": payload["summary"]["compiler_summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
