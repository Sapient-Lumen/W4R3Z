#!/usr/bin/env python3
"""CloudtainerML rev0013: CLP-style multi-token acceptance toy.

Not a reproduction. Simulates a backbone LM head plus additional MTP heads. The
paper's design principle is represented by a policy that always accepts the
backbone first token and only uses MTP heads for subsequent tokens, with a small
span-length predictor.
"""
from __future__ import annotations
import argparse, json, random, statistics, time
from pathlib import Path


def simulate(policy: str, regime: str, seed: int, steps: int = 2000, k: int = 4):
    rng = random.Random(seed)
    accepted = 0
    errors = 0
    repetitions = 0
    prev_error = False
    for t in range(steps):
        # First token backbone is much more reliable than MTP head in hard regimes.
        backbone_p = 0.985 if regime != "ambiguous" else 0.955
        mtp_base = {"easy_collocations": 0.93, "normal": 0.78, "ambiguous": 0.62, "repetition_trap": 0.72}[regime]
        if policy == "naive_mtp_first":
            first_ok = rng.random() < (mtp_base - 0.18)
            span = k
        elif policy == "backbone_first_fixed_k":
            first_ok = rng.random() < backbone_p
            span = k
        elif policy == "clp_toy":
            first_ok = rng.random() < backbone_p
            # Tiny span predictor: shortens when ambiguity/repetition risk is high.
            span = {"easy_collocations": 4, "normal": 3, "ambiguous": 2, "repetition_trap": 2}[regime]
            if rng.random() < 0.10: span = max(1, span - 1)
        elif policy == "oracle_length":
            first_ok = rng.random() < backbone_p
            span = {"easy_collocations": 4, "normal": 3, "ambiguous": 1, "repetition_trap": 1}[regime]
        else:
            raise ValueError(policy)
        if not first_ok:
            errors += 1; prev_error = True; accepted += 1; continue
        accepted += 1
        local_prev_error = False
        for j in range(2, span + 1):
            p = mtp_base - 0.08 * (j - 2)
            if regime == "repetition_trap" and (prev_error or local_prev_error):
                p -= 0.25
            ok = rng.random() < p
            accepted += 1
            if not ok:
                errors += 1; local_prev_error = True
                if regime == "repetition_trap": repetitions += 1
            else:
                local_prev_error = False
        prev_error = local_prev_error
    return accepted / steps, errors / max(1, accepted), repetitions / steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/probe-results/REV0013_CLP_MULTITOKEN_ACCEPTANCE_SMOKE.json")
    ap.add_argument("--seeds", type=int, default=64)
    args = ap.parse_args()
    t0 = time.time()
    regimes = ["easy_collocations", "normal", "ambiguous", "repetition_trap"]
    policies = ["naive_mtp_first", "backbone_first_fixed_k", "clp_toy", "oracle_length"]
    rows = []
    for regime in regimes:
        for policy in policies:
            vals = [simulate(policy, regime, 1877*s + 5) for s in range(args.seeds)]
            rows.append({
                "regime": regime,
                "policy": policy,
                "mean_tokens_per_forward": statistics.mean(v[0] for v in vals),
                "mean_error_rate_per_token": statistics.mean(v[1] for v in vals),
                "mean_repetition_proxy": statistics.mean(v[2] for v in vals),
                "runs": args.seeds,
            })
    # Utility penalizes quality failure harshly to make speed/quality frontier visible.
    for r in rows:
        r["speed_quality_utility"] = r["mean_tokens_per_forward"] - 30.0 * r["mean_error_rate_per_token"] - 10.0 * r["mean_repetition_proxy"]
    winners = {}
    for regime in regimes:
        subset = [r for r in rows if r["regime"] == regime]
        winners[regime] = max(subset, key=lambda r: r["speed_quality_utility"])["policy"]
    out = {
        "project": "CloudtainerML",
        "revision": "rev0013",
        "probe": "clp_multitoken_acceptance_smoke",
        "is_paper_reproduction": False,
        "summary": {
            "primary_metric": {"name": "speed_quality_utility", "direction": "higher_is_better"},
            "runtime_seconds": round(time.time() - t0, 4),
            "winners_by_regime": winners,
            "interpretation": "Toy multi-token acceptance test: backbone-first acceptance plus a tiny length predictor can beat naive MTP-first under quality/repetition penalties.",
        },
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(args.out)

if __name__ == "__main__": main()
