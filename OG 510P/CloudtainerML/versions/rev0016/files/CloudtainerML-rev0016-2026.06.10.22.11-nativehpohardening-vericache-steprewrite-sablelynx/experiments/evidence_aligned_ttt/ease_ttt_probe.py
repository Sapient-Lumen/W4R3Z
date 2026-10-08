#!/usr/bin/env python3
"""Evidence-aligned test-time training toy probe.

This is a tiny analogue of EASE-TTT: retrieval does not replace the full
context. Instead, retrieved evidence is converted into a soft attention target
and used to update only a query-side vector. The base chunk memory stays fixed.

The probe asks whether a few query-vector updates can move mass onto true
evidence in regimes with lexical decoys, scattered evidence, or stale priors.
It is a symbolic/tensor falsifier, not a reproduction of the paper.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["clean_retrieval", "lexical_decoys", "scattered_evidence", "stale_prior", "weak_retriever"]
POLICIES = [
    "full_context_base",
    "retrieval_only_topk",
    "random_qttt",
    "ease_ttt_topk",
    "ease_ttt_softmix",
    "oracle_evidence_ttt",
]


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-12)


def topk(x: np.ndarray, k: int) -> np.ndarray:
    k = max(0, min(int(k), len(x)))
    if k == 0:
        return np.array([], dtype=np.int64)
    return np.argpartition(-x, k - 1)[:k].astype(np.int64)


def unit(x: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(x))
    return x / (n + 1e-12)


def make_world(seed: int, regime: str, chunks: int, dim: int, evidence_n: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(9100 + seed)
    q_true = unit(rng.normal(size=dim))
    stale = unit(rng.normal(size=dim))
    chunks_x = rng.normal(0, 0.85, size=(chunks, dim)).astype(np.float32)
    evidence = rng.choice(chunks, size=evidence_n, replace=False)
    decoy_n = max(evidence_n, chunks // 10)
    decoys = np.array([i for i in rng.choice(chunks, size=decoy_n * 2, replace=False) if i not in set(evidence)][:decoy_n], dtype=np.int64)

    # True evidence vectors point toward the answer/query direction, but how easy
    # they are for lexical retrieval varies by regime.
    for i in evidence:
        chunks_x[i] += (2.2 if regime != "weak_retriever" else 1.1) * q_true + rng.normal(0, 0.2, dim)
    for i in decoys:
        chunks_x[i] += (2.6 if regime in {"lexical_decoys", "stale_prior"} else 1.2) * q_true + rng.normal(0, 0.35, dim)

    if regime == "scattered_evidence":
        # Evidence is individually faint; the answer emerges from several chunks.
        chunks_x[evidence] = rng.normal(0, 0.95, size=(len(evidence), dim)) + 1.35 * q_true
        chunks_x[decoys] += 1.65 * q_true
    if regime == "stale_prior":
        # The base query starts biased toward an obsolete topic.
        q_base = unit(0.45 * q_true + 1.10 * stale + rng.normal(0, 0.15, dim))
        chunks_x[decoys] += 2.0 * stale
    else:
        q_base = unit(0.80 * q_true + rng.normal(0, 0.45 if regime == "weak_retriever" else 0.25, dim))

    # Retrieval score is a noisy external evidence localization signal. Decoys can
    # look good lexically even when they are not answer-bearing.
    ret = chunks_x @ q_true
    ret += rng.normal(0, 0.55 if regime != "weak_retriever" else 1.20, size=chunks)
    if regime == "lexical_decoys":
        ret[decoys] += 2.0
    if regime == "stale_prior":
        ret += 0.65 * (chunks_x @ stale)
    if regime == "clean_retrieval":
        ret[evidence] += 2.5
    return {"chunks": chunks_x.astype(np.float32), "q_base": q_base.astype(np.float32), "q_true": q_true.astype(np.float32), "evidence": evidence.astype(np.int64), "decoys": decoys.astype(np.int64), "retrieval": ret.astype(np.float32)}


def evidence_mass(q: np.ndarray, chunks_x: np.ndarray, evidence: np.ndarray, temperature: float = 3.0) -> Tuple[float, float, np.ndarray]:
    a = softmax((chunks_x @ q) * temperature)
    mass = float(np.sum(a[evidence]))
    rank = np.argsort(-a)
    first_rank = min(int(np.where(rank == int(e))[0][0]) for e in evidence)
    return mass, float(first_rank), a


def adapt_query(q0: np.ndarray, chunks_x: np.ndarray, target: np.ndarray, steps: int, lr: float, temperature: float = 3.0) -> np.ndarray:
    q = q0.astype(np.float64).copy()
    x = chunks_x.astype(np.float64)
    for _ in range(steps):
        pred = softmax((x @ q) * temperature)
        grad = temperature * ((target - pred) @ x)
        q = q + lr * grad
        q = unit(q)
    return q.astype(np.float32)


@dataclass
class Row:
    seed: int
    regime: str
    retrieval_k: int
    steps: int
    policy: str
    evidence_mass: float
    first_evidence_rank: float
    hit_at_k: float
    answer_accuracy: float
    decoy_mass: float


def evaluate(seed: int, regime: str, retrieval_k: int, steps: int, policy: str, chunks: int, dim: int, evidence_n: int) -> Row:
    world = make_world(seed, regime, chunks, dim, evidence_n)
    x = world["chunks"]; q0 = world["q_base"]; evidence = world["evidence"]; decoys = world["decoys"]; retrieval = world["retrieval"]
    retrieved = topk(retrieval, retrieval_k)
    rng = np.random.default_rng(100_000 + seed + retrieval_k + steps)

    if policy == "full_context_base":
        q = q0
        allowed = np.arange(chunks)
    elif policy == "retrieval_only_topk":
        # No query adaptation; answer with a renormalized retrieved slice.
        q = q0
        allowed = retrieved
    elif policy == "random_qttt":
        target = np.ones(chunks, dtype=np.float64) * 1e-4
        target[rng.choice(chunks, size=retrieval_k, replace=False)] = 1.0
        target = target / target.sum()
        q = adapt_query(q0, x, target, steps=steps, lr=0.12)
        allowed = np.arange(chunks)
    elif policy == "ease_ttt_topk":
        target = np.ones(chunks, dtype=np.float64) * 1e-4
        target[retrieved] = 1.0
        target = target / target.sum()
        q = adapt_query(q0, x, target, steps=steps, lr=0.12)
        allowed = np.arange(chunks)
    elif policy == "ease_ttt_softmix":
        target = softmax(retrieval / (np.std(retrieval) + 1e-6))
        # Keep low but nonzero mass outside selected spans, like soft attention supervision.
        mask = np.zeros(chunks); mask[retrieved] = 1.0
        target = 0.8 * (target * mask / (np.sum(target * mask) + 1e-12)) + 0.2 * target
        q = adapt_query(q0, x, target, steps=steps, lr=0.10)
        allowed = np.arange(chunks)
    elif policy == "oracle_evidence_ttt":
        target = np.ones(chunks, dtype=np.float64) * 1e-4
        target[evidence] = 1.0
        target = target / target.sum()
        q = adapt_query(q0, x, target, steps=steps, lr=0.12)
        allowed = np.arange(chunks)
    else:
        raise ValueError(policy)

    if len(allowed) == chunks:
        mass, first_rank, attn = evidence_mass(q, x, evidence)
        decoy_mass = float(np.sum(attn[decoys]))
        hit = len(set(topk(attn, retrieval_k).tolist()) & set(evidence.tolist())) / max(1, len(evidence))
    else:
        logits = (x[allowed] @ q) * 3.0
        a_slice = softmax(logits)
        attn = np.zeros(chunks, dtype=np.float64); attn[allowed] = a_slice
        mass = float(np.sum(attn[evidence])); decoy_mass = float(np.sum(attn[decoys]))
        rank = np.argsort(-attn)
        first_rank = min(int(np.where(rank == int(e))[0][0]) for e in evidence)
        hit = len(set(allowed.tolist()) & set(evidence.tolist())) / max(1, len(evidence))
    # Accuracy proxy: enough evidence mass and not dominated by decoys.
    acc = float((mass > 0.35) and (mass > 0.85 * decoy_mass))
    return Row(seed, regime, retrieval_k, steps, policy, float(mass), float(first_rank), float(hit), acc, float(decoy_mass))


def run(seeds: int, chunks: int, dim: int, evidence_n: int, retrieval_ks: List[int], steps_list: List[int]) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for k in retrieval_ks:
                for steps in steps_list:
                    for policy in POLICIES:
                        rows.append(evaluate(seed, regime, k, steps, policy, chunks, dim, evidence_n))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    groups: Dict[Tuple[str, int, int], Dict[str, List[float]]] = {}
    for r in rows:
        groups.setdefault((r.regime, r.retrieval_k, r.steps), {}).setdefault(r.policy, []).append(r.answer_accuracy)
    winners: Dict[str, str] = {}; counts: Dict[str, int] = {}
    practical: Dict[str, str] = {}; pcounts: Dict[str, int] = {}
    for (regime, k, steps), pols in groups.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get); winners[f"{regime}/K{k}/S{steps}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p != "oracle_evidence_ttt"}
        pw = max(means2, key=means2.get); practical[f"{regime}/K{k}/S{steps}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "answer_accuracy", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "If evidence-aligned query updates beat retrieval-only and random qTTT, retrieval is acting as supervision for context access rather than merely context pruning.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0010", "probe": "evidence_aligned_ttt", "config": {"regimes": REGIMES, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--chunks", type=int, default=72)
    ap.add_argument("--dim", type=int, default=48)
    ap.add_argument("--evidence-n", type=int, default=3)
    ap.add_argument("--retrieval-ks", type=int, nargs="+", default=[4, 8, 16])
    ap.add_argument("--steps-list", type=int, nargs="+", default=[1, 3, 6])
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0010_EVIDENCE_ALIGNED_TTT_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0010_EVIDENCE_ALIGNED_TTT_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.chunks, args.dim, args.evidence_n, args.retrieval_ks, args.steps_list)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
