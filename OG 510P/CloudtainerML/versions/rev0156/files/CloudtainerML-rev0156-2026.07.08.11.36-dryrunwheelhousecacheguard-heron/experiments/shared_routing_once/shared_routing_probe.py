#!/usr/bin/env python3
"""Cross-layer shared sparse-routing toy probe.

Inspired by the "You Only Index Once" / cross-layer sparse attention idea: compute
a token-level route once and reuse it across layers to amortize top-k routing.

This probe creates synthetic layer/head support sets and noisy route scores. It
asks when one route can safely serve all layers, and when layer drift makes the
route a hidden quality cliff.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


def make_world(seed: int, scenario: str, layers: int, heads: int, tokens: int, true_k: int) -> dict:
    rng = np.random.default_rng(seed)
    base = set(rng.choice(tokens, size=true_k, replace=False).tolist())
    supports: list[list[set[int]]] = []
    scores = np.zeros((layers, heads, tokens), dtype=np.float32)
    for l in range(layers):
        layer_sets = []
        for h in range(heads):
            s = set(base)
            if scenario == "stable_layers":
                drift = 0.06
            elif scenario == "late_divergence":
                drift = 0.04 + 0.45 * (l / max(1, layers - 1))
            elif scenario == "early_noise_then_consensus":
                drift = 0.55 * (1.0 - l / max(1, layers - 1)) + 0.04
            elif scenario == "alternating_heads":
                drift = 0.08 if (h + l) % 2 == 0 else 0.42
            else:
                raise ValueError(scenario)
            remove_n = min(len(s), int(round(drift * true_k)))
            if remove_n:
                rem = set(rng.choice(list(s), size=remove_n, replace=False).tolist())
                s -= rem
                add_pool = [i for i in range(tokens) if i not in s]
                s |= set(rng.choice(add_pool, size=remove_n, replace=False).tolist())
            layer_sets.append(s)
            # Scores are noisy but elevated on true support.
            sc = rng.normal(0.0, 0.25, size=tokens).astype(np.float32)
            sc[list(s)] += rng.normal(1.25, 0.25, size=len(s)).astype(np.float32)
            # Add scenario-specific misleading route hints.
            if scenario == "early_noise_then_consensus" and l == 0:
                decoys = rng.choice([i for i in range(tokens) if i not in s], size=true_k, replace=False)
                sc[decoys] += 1.10
            if scenario == "late_divergence" and l >= layers - 2:
                decoys = rng.choice([i for i in range(tokens) if i not in s], size=true_k // 2, replace=False)
                sc[decoys] += 0.65
            scores[l, h] = sc
        supports.append(layer_sets)
    return {"supports": supports, "scores": scores}


def topk(score: np.ndarray, k: int) -> set[int]:
    return set(np.argpartition(-score, k - 1)[:k].astype(int).tolist())


def routes(world: dict, method: str, budget: int) -> list[list[set[int]]]:
    scores = world["scores"]
    L, H, T = scores.shape
    out: list[list[set[int]]] = []
    if method == "per_layer_oracle":
        return [[set(world["supports"][l][h]) for h in range(H)] for l in range(L)]
    if method == "per_layer_score":
        return [[topk(scores[l, h], budget) for h in range(H)] for l in range(L)]
    if method == "layer0_once":
        r = [topk(scores[0, h], budget) for h in range(H)]
        return [[set(r[h]) for h in range(H)] for _ in range(L)]
    if method == "mid_once":
        mid = L // 2
        r = [topk(scores[mid, h], budget) for h in range(H)]
        return [[set(r[h]) for h in range(H)] for _ in range(L)]
    if method == "consensus_shared":
        r = []
        for h in range(H):
            avg = np.mean(scores[:, h, :], axis=0)
            r.append(topk(avg, budget))
        return [[set(r[h]) for h in range(H)] for _ in range(L)]
    if method == "two_anchor_shared":
        r0 = [topk(scores[0, h], budget // 2) for h in range(H)]
        r1 = [topk(scores[-1, h], budget - budget // 2) for h in range(H)]
        r = [set(r0[h]) | set(r1[h]) for h in range(H)]
        return [[set(r[h]) for h in range(H)] for _ in range(L)]
    if method == "random_once":
        rng = np.random.default_rng(12345)
        r = [set(rng.choice(T, size=budget, replace=False).astype(int).tolist()) for _ in range(H)]
        return [[set(r[h]) for h in range(H)] for _ in range(L)]
    raise ValueError(method)


@dataclass
class Row:
    seed: int
    scenario: str
    method: str
    layers: int
    heads: int
    tokens: int
    budget: int
    support_recall: float
    support_precision: float
    worst_layer_recall: float
    output_error_proxy: float
    routing_cost_fraction: float
    unacceptable_layer_fraction: float


def eval_method(seed: int, scenario: str, method: str, layers: int, heads: int, tokens: int, true_k: int, budget: int) -> Row:
    w = make_world(seed, scenario, layers, heads, tokens, true_k)
    rs = routes(w, method, budget)
    recalls, precs = [], []
    bad = 0
    for l in range(layers):
        for h in range(heads):
            truth = w["supports"][l][h]
            pred = rs[l][h]
            hit = len(truth & pred)
            rec = hit / max(1, len(truth))
            pre = hit / max(1, len(pred))
            recalls.append(rec); precs.append(pre)
            if rec < 0.65:
                bad += 1
    if method == "per_layer_oracle":
        cost = 1.0
    elif method == "per_layer_score":
        cost = 1.0
    elif method == "two_anchor_shared":
        cost = 2.0 / layers
    else:
        cost = 1.0 / layers
    return Row(
        seed, scenario, method, layers, heads, tokens, budget,
        float(np.mean(recalls)), float(np.mean(precs)), float(np.min(recalls)),
        float(1.0 - np.mean(recalls) + 0.25 * bad / (layers * heads)), cost,
        float(bad / (layers * heads)),
    )


def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for scenario in sorted({r.scenario for r in rows}):
        for method in sorted({r.method for r in rows}):
            sub = [r for r in rows if r.scenario == scenario and r.method == method]
            by[f"{scenario}/{method}"] = {
                "mean_support_recall": float(np.mean([r.support_recall for r in sub])),
                "mean_worst_layer_recall": float(np.mean([r.worst_layer_recall for r in sub])),
                "mean_output_error_proxy": float(np.mean([r.output_error_proxy for r in sub])),
                "mean_routing_cost_fraction": float(np.mean([r.routing_cost_fraction for r in sub])),
                "mean_unacceptable_layer_fraction": float(np.mean([r.unacceptable_layer_fraction for r in sub])),
            }
    winners = {}
    for scenario in sorted({r.scenario for r in rows}):
        cand = []
        for method in sorted({r.method for r in rows}):
            if method == "per_layer_oracle":
                continue
            m = by[f"{scenario}/{method}"]
            score = m["mean_support_recall"] - 0.35*m["mean_unacceptable_layer_fraction"] - 0.10*m["mean_routing_cost_fraction"]
            cand.append((-score, method))
        cand.sort(); winners[scenario] = cand[0][1]
    return {"row_count": len(rows), "by_scenario_method": by, "winners_excluding_oracle": winners, "primary_metric": {"name": "support_recall_minus_bad_layers_and_cost", "direction": "higher_is_better"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0008_SHARED_ROUTING_ONCE_SMOKE"))
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--layers", type=int, default=12)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--tokens", type=int, default=1024)
    ap.add_argument("--true-k", type=int, default=32)
    args = ap.parse_args()
    scenarios = ["stable_layers", "late_divergence", "early_noise_then_consensus", "alternating_heads"]
    methods = ["per_layer_oracle", "per_layer_score", "layer0_once", "mid_once", "consensus_shared", "two_anchor_shared", "random_once"]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for scenario in scenarios:
            for budget in [24, 32, 48]:
                for method in methods:
                    rows.append(eval_method(seed, scenario, method, args.layers, args.heads, args.tokens, args.true_k, budget))
    out = args.out; out.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = out.with_suffix(".csv"), out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows(asdict(r) for r in rows)
    payload = {"probe": "shared_routing_once", "purpose": "When can token sparse-attention routing be computed once and reused across layers?", "config": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}, "rows": [asdict(r) for r in rows], "summary": summarize(rows), "csv": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"]["winners_excluding_oracle"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
