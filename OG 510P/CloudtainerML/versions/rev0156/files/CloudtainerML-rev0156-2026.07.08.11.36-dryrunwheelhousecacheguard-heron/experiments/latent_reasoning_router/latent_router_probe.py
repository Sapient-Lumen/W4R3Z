#!/usr/bin/env python3
"""Token-wise latent/explicit reasoning router toy probe.

Latent-reasoning papers ask whether some intermediate computation can move from
text tokens into continuous states. TARPO-like work adds a token-wise router that
chooses latent vs explicit mode. This probe turns that into a cheap cost/accuracy
control problem: explicit steps are costly but reliable; latent steps are cheap
but sensitive to difficulty/manifold mismatch; stochastic flow-style latent
steps can recover exploration at some cost.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


def make_problem(seed: int, regime: str, steps: int) -> dict:
    rng = np.random.default_rng(seed)
    if regime == "easy_smooth":
        diff = np.clip(rng.normal(0.25, 0.10, size=steps), 0.02, 0.95)
        mismatch = np.clip(rng.normal(0.12, 0.05, size=steps), 0.0, 0.9)
    elif regime == "hard_spikes":
        diff = np.clip(rng.normal(0.32, 0.12, size=steps), 0.02, 0.98)
        spikes = rng.choice(steps, size=max(1, steps // 5), replace=False)
        diff[spikes] = np.clip(diff[spikes] + rng.uniform(0.35, 0.60, size=len(spikes)), 0.02, 0.99)
        mismatch = np.clip(0.15 + 0.45 * (diff > 0.70) + rng.normal(0, 0.08, size=steps), 0.0, 0.95)
    elif regime == "late_brittle":
        ramp = np.linspace(0.10, 0.85, steps)
        diff = np.clip(ramp + rng.normal(0, 0.08, size=steps), 0.02, 0.99)
        mismatch = np.clip(0.10 + 0.65 * (np.arange(steps) > steps * 0.6) + rng.normal(0, 0.06, size=steps), 0.0, 0.98)
    elif regime == "uncertain_but_latent_good":
        diff = np.clip(rng.normal(0.55, 0.20, size=steps), 0.02, 0.98)
        mismatch = np.clip(rng.normal(0.08, 0.04, size=steps), 0.0, 0.4)
    else:
        raise ValueError(regime)
    # Entropy/confidence proxy visible to routers; imperfect signal.
    entropy = np.clip(0.25 + 0.70 * diff + 0.25 * mismatch + rng.normal(0, 0.08, size=steps), 0.0, 1.5)
    return {"difficulty": diff.astype(np.float32), "mismatch": mismatch.astype(np.float32), "entropy": entropy.astype(np.float32)}


def choose_modes(problem: dict, policy: str, budget: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 77)
    d, m, e = problem["difficulty"], problem["mismatch"], problem["entropy"]
    n = len(d)
    if policy == "all_explicit":
        return np.array(["explicit"] * n, dtype=object)
    if policy == "all_latent":
        return np.array(["latent"] * n, dtype=object)
    if policy == "all_flow_latent":
        return np.array(["flow_latent"] * n, dtype=object)
    if policy == "entropy_threshold":
        return np.where(e > 0.78, "explicit", "latent").astype(object)
    if policy == "mismatch_aware":
        return np.where((e + 0.85*m) > 0.85, "explicit", "latent").astype(object)
    if policy == "budget_aware_router":
        # Start latent, spend explicit budget on riskiest steps, use flow latent for medium-risk steps.
        modes = np.array(["latent"] * n, dtype=object)
        risk = 0.65*e + 0.85*m + 0.25*d
        explicit_slots = int(max(0, min(n, budget)))
        flow_slots = int(max(0, min(n - explicit_slots, n * 0.25)))
        order = np.argsort(-risk)
        modes[order[:explicit_slots]] = "explicit"
        modes[order[explicit_slots:explicit_slots+flow_slots]] = "flow_latent"
        return modes
    if policy == "oracle_router":
        modes = np.array(["latent"] * n, dtype=object)
        risk = 0.55*d + 1.10*m
        modes[risk > 0.74] = "explicit"
        modes[(risk > 0.50) & (risk <= 0.74)] = "flow_latent"
        return modes
    if policy == "random_router":
        return rng.choice(["explicit", "latent", "flow_latent"], size=n, p=[0.25, 0.55, 0.20]).astype(object)
    raise ValueError(policy)


@dataclass
class Row:
    seed: int
    regime: str
    policy: str
    steps: int
    budget: float
    total_cost: float
    cost_fraction_vs_explicit: float
    expected_success: float
    catastrophic_failure_proxy: float
    latent_fraction: float
    explicit_fraction: float
    flow_latent_fraction: float
    utility: float


def eval_policy(seed: int, regime: str, policy: str, steps: int, budget: float) -> Row:
    p = make_problem(seed, regime, steps)
    modes = choose_modes(p, policy, budget, seed)
    d, m = p["difficulty"], p["mismatch"]
    probs = []
    cost = 0.0
    for mode, diff, mis in zip(modes, d, m):
        if mode == "explicit":
            probs.append(1.0 - 0.06*diff - 0.02*mis); cost += 1.0
        elif mode == "latent":
            probs.append(1.0 - 0.18*diff - 0.72*mis - 0.18*diff*mis); cost += 0.22
        elif mode == "flow_latent":
            probs.append(1.0 - 0.12*diff - 0.36*mis - 0.08*diff*mis); cost += 0.42
        else:
            raise ValueError(mode)
    probs = np.clip(np.array(probs), 0.01, 0.999)
    log_success = float(np.sum(np.log(probs)))
    expected_success = float(np.exp(log_success))
    catastrophic = float(np.mean(probs < 0.72))
    utility = expected_success - 0.85*(cost/steps) - 0.35*catastrophic
    return Row(seed, regime, policy, steps, budget, cost, cost/steps, expected_success, catastrophic, float(np.mean(modes == "latent")), float(np.mean(modes == "explicit")), float(np.mean(modes == "flow_latent")), utility)


def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for regime in sorted({r.regime for r in rows}):
        for policy in sorted({r.policy for r in rows}):
            sub = [r for r in rows if r.regime == regime and r.policy == policy]
            by[f"{regime}/{policy}"] = {
                "mean_expected_success": float(np.mean([r.expected_success for r in sub])),
                "mean_cost_fraction_vs_explicit": float(np.mean([r.cost_fraction_vs_explicit for r in sub])),
                "mean_catastrophic_failure_proxy": float(np.mean([r.catastrophic_failure_proxy for r in sub])),
                "mean_utility": float(np.mean([r.utility for r in sub])),
                "mean_latent_fraction": float(np.mean([r.latent_fraction for r in sub])),
                "mean_explicit_fraction": float(np.mean([r.explicit_fraction for r in sub])),
            }
    winners = {}
    for regime in sorted({r.regime for r in rows}):
        cand = []
        for policy in sorted({r.policy for r in rows}):
            m = by[f"{regime}/{policy}"]
            cand.append((-m["mean_utility"], policy))
        cand.sort(); winners[regime] = cand[0][1]
    return {"row_count": len(rows), "by_regime_policy": by, "winners": winners, "primary_metric": {"name": "utility", "direction": "higher_is_better"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0008_LATENT_REASONING_ROUTER_SMOKE"))
    ap.add_argument("--seeds", type=int, default=48)
    ap.add_argument("--steps", type=int, default=18)
    args = ap.parse_args()
    regimes = ["easy_smooth", "hard_spikes", "late_brittle", "uncertain_but_latent_good"]
    policies = ["all_explicit", "all_latent", "all_flow_latent", "entropy_threshold", "mismatch_aware", "budget_aware_router", "oracle_router", "random_router"]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for regime in regimes:
            for budget in [2.0, 4.0, 6.0]:
                for policy in policies:
                    rows.append(eval_policy(seed, regime, policy, args.steps, budget))
    out = args.out; out.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = out.with_suffix(".csv"), out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows(asdict(r) for r in rows)
    payload = {"probe": "latent_reasoning_router", "purpose": "Cost/accuracy toy for token-wise latent-vs-explicit reasoning routers.", "config": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}, "rows": [asdict(r) for r in rows], "summary": summarize(rows), "csv": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"]["winners"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
