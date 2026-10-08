#!/usr/bin/env python3
"""Entropy-guided head/segment budget toy.

Inspired by EntropyInfer-style claims: head importance is context-dependent,
rigid low-entropy heads and dynamic high-entropy heads should not receive the
same cache/compute budget. This probe constructs synthetic multi-head segment
importance maps and asks which policy preserves useful attention mass under a
fixed segment budget.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["rigid_sparse", "dynamic_shift", "mixed_context", "late_decode_signal", "entropy_trap"]
POLICIES = ["uniform", "offline_head_type", "entropy_adaptive", "entropy_plus_decode", "random", "oracle_dynamic"]


def softmax(x: np.ndarray, temp: float = 1.0) -> np.ndarray:
    z = (x - np.max(x)) / max(temp, 1e-6)
    e = np.exp(z)
    return e / np.sum(e)


def entropy(p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0)
    return float(-np.sum(p * np.log(p)) / np.log(len(p)))


def make_case(seed: int, regime: str, heads: int, segments: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(91000 + seed)
    logits = rng.normal(0, 0.35, size=(heads, segments))
    decode_signal = rng.normal(0, 0.2, size=(heads, segments))
    required = np.zeros((heads, segments), dtype=np.float64)
    head_weight = rng.uniform(0.6, 1.4, size=heads)

    if regime == "rigid_sparse":
        for h in range(heads):
            j = (3 * h + seed) % segments
            logits[h, j] += 5.0
            required[h, j] = 1.0
    elif regime == "dynamic_shift":
        for h in range(heads):
            j = (h * 5 + seed) % segments
            k = (j + rng.integers(3, max(4, segments // 2))) % segments
            logits[h, j] += 1.5
            logits[h, k] += 1.3
            required[h, k] = 1.0
            decode_signal[h, k] += 3.0
    elif regime == "mixed_context":
        for h in range(heads):
            if h % 3 == 0:
                j = (h + seed) % segments
                logits[h, j] += 4.2
                required[h, j] = 1.0
            else:
                js = rng.choice(segments, size=3, replace=False)
                logits[h, js] += rng.uniform(1.0, 2.0, size=3)
                required[h, js] = np.array([0.5, 1.0, 0.7])
    elif regime == "late_decode_signal":
        for h in range(heads):
            early = rng.integers(0, segments // 2)
            late = rng.integers(segments // 2, segments)
            logits[h, early] += 2.5
            logits[h, late] += 0.4  # prefill weak
            decode_signal[h, late] += 4.0
            required[h, late] = 1.0
    elif regime == "entropy_trap":
        # High entropy can be distraction: one low-logit segment matters later.
        for h in range(heads):
            logits[h] += rng.normal(0, 0.15, size=segments)
            decoy = rng.choice(segments, size=4, replace=False)
            logits[h, decoy] += 0.8
            target = (seed + 7 * h) % segments
            logits[h, target] -= 0.2
            decode_signal[h, target] += 3.5
            required[h, target] = 1.0
    else:
        raise ValueError(regime)

    attn = np.vstack([softmax(logits[h]) for h in range(heads)])
    future = np.vstack([softmax(logits[h] + decode_signal[h]) for h in range(heads)])
    return {"attn": attn, "future": future, "required": required, "head_weight": head_weight, "decode_signal": decode_signal}


def allocate(policy: str, case: Dict[str, np.ndarray], budget: int, rng: np.random.Generator) -> np.ndarray:
    attn = case["attn"]
    future = case["future"]
    required = case["required"]
    heads, segments = attn.shape
    keep = np.zeros_like(attn, dtype=bool)

    if policy == "uniform":
        per = max(1, budget // heads)
        for h in range(heads):
            idx = np.argsort(attn[h])[-per:]
            keep[h, idx] = True
    elif policy == "offline_head_type":
        ent = np.array([entropy(attn[h]) for h in range(heads)])
        low = ent < np.median(ent)
        for h in range(heads):
            per = 1 if low[h] else max(1, int(round(budget / heads * 1.4)))
            idx = np.argsort(attn[h])[-per:]
            keep[h, idx] = True
    elif policy == "entropy_adaptive":
        ent = np.array([entropy(attn[h]) for h in range(heads)])
        score = attn * (0.5 + ent[:, None])
        flat = np.argsort(score.reshape(-1))[-budget:]
        keep.reshape(-1)[flat] = True
    elif policy == "entropy_plus_decode":
        ent = np.array([entropy(attn[h]) for h in range(heads)])
        score = 0.65 * attn + 0.35 * future + 0.15 * ent[:, None] * future
        flat = np.argsort(score.reshape(-1))[-budget:]
        keep.reshape(-1)[flat] = True
    elif policy == "random":
        flat = rng.choice(heads * segments, size=min(budget, heads * segments), replace=False)
        keep.reshape(-1)[flat] = True
    elif policy == "oracle_dynamic":
        score = 0.2 * future + 2.0 * required
        flat = np.argsort(score.reshape(-1))[-budget:]
        keep.reshape(-1)[flat] = True
    else:
        raise ValueError(policy)
    return keep


@dataclass
class Row:
    seed: int
    regime: str
    budget: int
    policy: str
    retained_future_mass: float
    retained_required_mass: float
    required_hit_rate: float
    weighted_utility: float
    entropy_mean: float


def eval_one(seed: int, regime: str, budget: int, policy: str, heads: int, segments: int) -> Row:
    rng = np.random.default_rng(93000 + seed + budget)
    c = make_case(seed, regime, heads, segments)
    keep = allocate(policy, c, budget, rng)
    future = c["future"]
    required = c["required"]
    weights = c["head_weight"][:, None]
    retained_future = float(np.sum(future[keep]) / future.shape[0])
    req_total = float(np.sum(required)) or 1.0
    retained_req = float(np.sum(required[keep]) / req_total)
    req_hit = float(np.mean([np.any(keep[h] & (required[h] > 0)) for h in range(heads)]))
    utility = float(np.sum(weights * future * keep) / np.sum(weights * future))
    ent = float(np.mean([entropy(c["attn"][h]) for h in range(heads)]))
    return Row(seed, regime, budget, policy, retained_future, retained_req, req_hit, utility, ent)


def run(seeds: int, heads: int, segments: int, budgets: List[int]) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for budget in budgets:
                for policy in POLICIES:
                    rows.append(eval_one(seed, regime, budget, policy, heads, segments))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.budget), {}).setdefault(r.policy, []).append(r.weighted_utility)
    winners = {}; counts: Dict[str, int] = {}
    practical = {}; pcounts: Dict[str, int] = {}
    for (regime, budget), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get)
        winners[f"{regime}/B{budget}"] = w; counts[w] = counts.get(w, 0) + 1
        practical_means = {p: m for p, m in means.items() if p != "oracle_dynamic"}
        pw = max(practical_means, key=practical_means.get)
        practical[f"{regime}/B{budget}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "weighted_utility", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "Entropy alone should help when head entropy marks uncertainty; decode-conditioned entropy should win late-signal and entropy-trap cases if the toy captures the EntropyInfer motivation.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0011", "probe": "entropy_guided_budget", "config": {"regimes": REGIMES, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader(); w.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=18)
    ap.add_argument("--heads", type=int, default=8)
    ap.add_argument("--segments", type=int, default=32)
    ap.add_argument("--budgets", type=int, nargs="+", default=[16, 32, 64])
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0011_ENTROPY_GUIDED_BUDGET_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0011_ENTROPY_GUIDED_BUDGET_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.heads, args.segments, args.budgets)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
