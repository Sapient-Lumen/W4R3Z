#!/usr/bin/env python3
"""CloudtainerML rev0013: toy Centaur/autoresearch HPO probe.

Inspired by the autoresearch/Centaur paper, but not a reproduction. The probe
simulates small training-code HPO with an OOM cliff and compares:
- random search
- stateless domain heuristic proposals ("agent_only")
- diagonal CMA-ish state tracker
- TPE-ish elite sampler
- centaur_toy: CMA-ish state plus occasional domain heuristic proposals

The question is whether sharing optimizer state with a domain-prior proposer beats
either alone in a tiny CPU setting.
"""
from __future__ import annotations

import argparse, json, math, random, statistics, time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

Param = Tuple[float, float, float, float]  # log_lr, dropout, width_norm, depth_norm


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe(p: Param) -> Param:
    lr, dr, w, d = p
    return (clamp(lr, -5.5, -1.0), clamp(dr, 0.0, 0.6), clamp(w, 0.0, 1.0), clamp(d, 0.0, 1.0))


def objective(p: Param, rng: random.Random, landscape: str) -> Tuple[float, bool]:
    """Returns score higher_is_better and oom flag."""
    lr, dr, w, d = safe(p)
    # OOM cliff: large width+depth with high LR often fails.
    oom_pressure = 0.62 * w + 0.55 * d + 0.08 * max(0.0, lr + 3.0)
    oom = oom_pressure > (0.92 if landscape != "tight_memory" else 0.78)
    if oom:
        return -10.0 - 3.0 * (oom_pressure - 0.75), True
    centers = {
        "smooth": (-3.25, 0.10, 0.58, 0.48),
        "rugged": (-3.85, 0.22, 0.74, 0.35),
        "tight_memory": (-3.10, 0.07, 0.44, 0.40),
        "domain_shift": (-4.20, 0.30, 0.36, 0.82),
    }
    c = centers[landscape]
    # Anisotropic basin plus mild interactions/ruggedness.
    loss = (
        1.5 * (lr - c[0]) ** 2
        + 3.2 * (dr - c[1]) ** 2
        + 1.8 * (w - c[2]) ** 2
        + 1.6 * (d - c[3]) ** 2
        + 0.45 * (w * d - c[2] * c[3]) ** 2
    )
    if landscape == "rugged":
        loss += 0.13 * math.sin(11 * w + 3 * lr) + 0.10 * math.sin(13 * d)
    if landscape == "domain_shift":
        loss += 0.25 * max(0.0, 0.18 - dr)  # domain prior underestimates dropout here
    score = -loss + rng.gauss(0.0, 0.015)
    return score, False


def random_param(rng: random.Random) -> Param:
    return (rng.uniform(-5.5, -1.0), rng.uniform(0.0, 0.6), rng.random(), rng.random())


def domain_prior(rng: random.Random, landscape_hint: str | None = None) -> Param:
    # Pretend "LLM domain knowledge": conservative memory, moderate LR, low dropout.
    if landscape_hint == "tight_memory":
        base = (-3.25, 0.08, 0.42, 0.42)
    else:
        base = (-3.35, 0.10, 0.55, 0.42)
    return safe(tuple(base[i] + rng.gauss(0, [0.45, 0.08, 0.13, 0.13][i]) for i in range(4)))  # type: ignore


@dataclass
class Trial:
    p: Param
    score: float
    oom: bool


def propose_tpe(rng: random.Random, trials: List[Trial]) -> Param:
    good = sorted([t for t in trials if not t.oom], key=lambda t: t.score, reverse=True)[: max(2, len(trials)//5)]
    if len(good) < 2:
        return random_param(rng)
    dims = list(zip(*(t.p for t in good)))
    vals = []
    for xs in dims:
        mu = statistics.mean(xs)
        sd = max(0.04, statistics.pstdev(xs) + 0.03)
        vals.append(rng.gauss(mu, sd))
    return safe(tuple(vals))  # type: ignore


def propose_cma_diag(rng: random.Random, trials: List[Trial], sigma_floor: float = 0.035) -> Param:
    good = sorted([t for t in trials if not t.oom], key=lambda t: t.score, reverse=True)[: max(3, len(trials)//4)]
    if len(good) < 3:
        return random_param(rng)
    weights = [math.exp(t.score - good[0].score) for t in good]
    sw = sum(weights)
    mu = [sum(w * t.p[i] for w, t in zip(weights, good)) / sw for i in range(4)]
    sd = []
    for i in range(4):
        var = sum(w * (t.p[i] - mu[i]) ** 2 for w, t in zip(weights, good)) / sw
        sd.append(max(sigma_floor, math.sqrt(var) + 0.02))
    return safe(tuple(rng.gauss(mu[i], sd[i]) for i in range(4)))  # type: ignore


def run_method(method: str, landscape: str, seed: int, budget: int = 80) -> Dict[str, object]:
    rng = random.Random(seed)
    trials: List[Trial] = []
    best = -1e9
    oom_count = 0
    best_curve = []
    for step in range(budget):
        if method == "random":
            p = random_param(rng)
        elif method == "agent_only":
            p = domain_prior(rng, "tight_memory" if landscape == "tight_memory" else None)
        elif method == "tpe_toy":
            p = propose_tpe(rng, trials)
        elif method == "cma_diag_toy":
            p = propose_cma_diag(rng, trials)
        elif method == "centaur_toy":
            if step < 8 or (step % 5 == 0):
                # Domain prior gets to see an interpretable hint: current OOM rate.
                hint = "tight_memory" if (oom_count > 0.2 * max(1, step) or landscape == "tight_memory") else None
                p = domain_prior(rng, hint)
            else:
                p = propose_cma_diag(rng, trials, sigma_floor=0.025)
        else:
            raise ValueError(method)
        score, oom = objective(p, rng, landscape)
        trials.append(Trial(p, score, oom))
        oom_count += int(oom)
        best = max(best, score)
        best_curve.append(best)
    return {"method": method, "landscape": landscape, "seed": seed, "best_score": best, "oom_rate": oom_count / budget, "best_curve": best_curve}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/probe-results/REV0013_CENTAUR_HPO_STATE_SMOKE.json")
    ap.add_argument("--seeds", type=int, default=24)
    args = ap.parse_args()
    t0 = time.time()
    methods = ["random", "agent_only", "tpe_toy", "cma_diag_toy", "centaur_toy"]
    landscapes = ["smooth", "rugged", "tight_memory", "domain_shift"]
    rows = []
    for landscape in landscapes:
        for method in methods:
            runs = [run_method(method, landscape, 991 * s + 17, 80) for s in range(args.seeds)]
            rows.append({
                "landscape": landscape,
                "method": method,
                "mean_best_score": statistics.mean(r["best_score"] for r in runs),
                "median_best_score": statistics.median(r["best_score"] for r in runs),
                "mean_oom_rate": statistics.mean(r["oom_rate"] for r in runs),
                "runs": args.seeds,
            })
    winners = {}
    for landscape in landscapes:
        subset = [r for r in rows if r["landscape"] == landscape]
        winners[landscape] = max(subset, key=lambda r: r["mean_best_score"])["method"]
    out = {
        "project": "CloudtainerML",
        "revision": "rev0013",
        "probe": "centaur_hpo_state_smoke",
        "is_paper_reproduction": False,
        "summary": {
            "primary_metric": {"name": "mean_best_score", "direction": "higher_is_better"},
            "runtime_seconds": round(time.time() - t0, 4),
            "winners_by_landscape": winners,
            "interpretation": "Toy HPO asks whether optimizer state plus domain-prior proposals beats stateless heuristic or classical toy optimizers alone under OOM cliffs.",
        },
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(args.out)

if __name__ == "__main__":
    main()
