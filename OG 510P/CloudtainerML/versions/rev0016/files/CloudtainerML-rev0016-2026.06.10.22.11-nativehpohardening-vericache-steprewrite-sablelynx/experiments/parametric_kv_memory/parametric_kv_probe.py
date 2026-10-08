#!/usr/bin/env python3
"""Parametric memory vs KV memory toy probe.

Inspired by work that studies document LoRA through KV-cache compression. The
toy separates context-side evidence from adapter-side memory and asks when an
adapter becomes useful as the retained KV evidence shrinks.

It intentionally uses simple stochastic fact recall rather than training a LoRA.
The result should be read as a falsifier for the interaction pattern, not as a
model benchmark.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["cache_intact", "moderate_compression", "aggressive_compression", "zero_context", "conflicting_adapter"]
ADAPTERS = ["none", "raw_ntp_weak", "qa_supervised", "base_encoded_answer_only", "noisy_conflicting"]
POLICIES = ["context_only", "adapter_only", "gated_context_adapter", "adapter_when_cache_miss", "full_cache_oracle"]


@dataclass
class Row:
    seed: int
    regime: str
    adapter: str
    policy: str
    retention: float
    query_count: int
    context_hit_rate: float
    adapter_accuracy: float
    answer_accuracy: float
    rouge_l_proxy: float
    hallucination_rate: float


def regime_retention(regime: str) -> float:
    return {
        "cache_intact": 0.92,
        "moderate_compression": 0.45,
        "aggressive_compression": 0.12,
        "zero_context": 0.0,
        "conflicting_adapter": 0.20,
    }[regime]


def adapter_quality(adapter: str, regime: str) -> Tuple[float, float]:
    # (accuracy if consulted, confidence). QA supervision is stronger than raw
    # next-token context memorization; base-encoded answer-only is strong but only
    # at generation; conflicting adapters can be actively harmful.
    base = {
        "none": (0.0, 0.0),
        "raw_ntp_weak": (0.42, 0.35),
        "qa_supervised": (0.78, 0.72),
        "base_encoded_answer_only": (0.86, 0.62),
        "noisy_conflicting": (0.25, 0.85),
    }[adapter]
    if regime == "conflicting_adapter" and adapter in {"qa_supervised", "base_encoded_answer_only"}:
        return (base[0] - 0.12, base[1])
    if regime == "conflicting_adapter" and adapter == "noisy_conflicting":
        return (0.08, 0.90)
    return base


def simulate(seed: int, regime: str, adapter: str, policy: str, facts: int, queries: int) -> Row:
    rng = np.random.default_rng(23000 + seed)
    retention = regime_retention(regime)
    retained = rng.random(facts) < retention
    # Some facts are hard: context can hold them exactly if retained, adapter has variable success.
    q_ids = rng.integers(0, facts, size=queries)
    in_cache = retained[q_ids]
    ctx_hit = float(np.mean(in_cache))
    a_acc, a_conf = adapter_quality(adapter, regime)
    adapter_correct = rng.random(queries) < a_acc
    # Context answer is near exact when retained, but a little noisy after severe compression.
    context_correct = in_cache & (rng.random(queries) < (0.97 if retention > 0.2 else 0.90))

    if policy == "context_only":
        correct = context_correct
        hallucinate = ~in_cache
    elif policy == "adapter_only":
        correct = adapter_correct
        hallucinate = ~adapter_correct
    elif policy == "gated_context_adapter":
        # Soft gate: trust context when present; trust adapter when context is absent
        # and confidence is high. Conflict regime exposes bad parametric memory.
        use_context = in_cache & (rng.random(queries) < 0.92)
        use_adapter = ~use_context
        correct = (use_context & context_correct) | (use_adapter & adapter_correct)
        hallucinate = use_adapter & ~adapter_correct & (rng.random(queries) < a_conf)
    elif policy == "adapter_when_cache_miss":
        correct = context_correct | ((~in_cache) & adapter_correct)
        hallucinate = (~in_cache) & ~adapter_correct
    elif policy == "full_cache_oracle":
        correct = rng.random(queries) < 0.985
        hallucinate = np.zeros(queries, dtype=bool)
    else:
        raise ValueError(policy)

    acc = float(np.mean(correct))
    # ROUGE-like proxy gives partial credit for weak/raw adapters and wrong-but-related answers.
    partial = np.where(correct, 1.0, 0.18 + 0.30 * a_conf * (policy != "context_only"))
    rouge = float(np.mean(partial))
    return Row(seed, regime, adapter, policy, retention, queries, ctx_hit, a_acc, acc, rouge, float(np.mean(hallucinate)))


def run(seeds: int, facts: int, queries: int) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seeds):
        for regime in REGIMES:
            for adapter in ADAPTERS:
                for policy in POLICIES:
                    rows.append(simulate(seed, regime, adapter, policy, facts, queries))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, str], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.adapter), {}).setdefault(r.policy, []).append(r.rouge_l_proxy)
    winners: Dict[str, str] = {}; counts: Dict[str, int] = {}
    practical: Dict[str, str] = {}; pcounts: Dict[str, int] = {}
    for (regime, adapter), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get); winners[f"{regime}/{adapter}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p != "full_cache_oracle"}
        pw = max(means2, key=means2.get); practical[f"{regime}/{adapter}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "rouge_l_proxy", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "Adapter memory should add little when context KV is intact and become valuable under extreme context compression; conflict regimes test stale/harmful parametric memory.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0010", "probe": "parametric_kv_memory", "config": {"regimes": REGIMES, "adapters": ADAPTERS, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=24)
    ap.add_argument("--facts", type=int, default=400)
    ap.add_argument("--queries", type=int, default=240)
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0010_PARAMETRIC_KV_MEMORY_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0010_PARAMETRIC_KV_MEMORY_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.seeds, args.facts, args.queries)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
