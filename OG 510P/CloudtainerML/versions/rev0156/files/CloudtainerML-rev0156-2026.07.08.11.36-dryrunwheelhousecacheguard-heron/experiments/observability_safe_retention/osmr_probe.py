#!/usr/bin/env python3
"""Observability-safe memory retention toy probe.

Inspired by observability-safe memory retention work: retain a bounded set of
memory items using only online-observable features, while evaluation reveals
future utility, stale risk, reacquisition delay, and redundancy costs.

The point is not to reproduce the paper. It is a cheap falsifier for a core
claim: retention policies that look good on immediate salience can be brittle
when future queries, stale facts, and reacquisition costs are delayed and only
partly observable.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

TOPICS = np.array(["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"])
SCENARIOS = ["aligned", "dormant_future", "stale_salience", "redundant_burst", "topic_shift"]
POLICIES = [
    "random",
    "recency",
    "online_salience",
    "online_diversity",
    "risk_aware_oas",
    "stale_averse",
    "offline_oracle",
]


def zscore(x: np.ndarray) -> np.ndarray:
    return (x - float(np.mean(x))) / (float(np.std(x)) + 1e-8)


def choose_top(score: np.ndarray, budget: int) -> np.ndarray:
    budget = max(0, min(len(score), int(budget)))
    if budget == 0:
        return np.array([], dtype=np.int64)
    return np.argpartition(-score, budget - 1)[:budget].astype(np.int64)


def make_stream(seed: int, scenario: str, n_items: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    topic = rng.integers(0, len(TOPICS), size=n_items)
    time = np.arange(n_items, dtype=np.float32) / max(1, n_items - 1)
    reliability = rng.beta(5.0, 2.0, size=n_items).astype(np.float32)
    novelty = rng.beta(2.0, 4.0, size=n_items).astype(np.float32)
    reacquire_cost = rng.gamma(2.0, 0.7, size=n_items).astype(np.float32)
    stale_risk = rng.beta(1.5, 6.0, size=n_items).astype(np.float32)
    future_queries = rng.poisson(1.2, size=n_items).astype(np.float32)
    evidence_value = rng.lognormal(mean=0.0, sigma=0.35, size=n_items).astype(np.float32)
    observed_salience = (0.55 * future_queries + 0.25 * evidence_value + 0.15 * reliability + rng.normal(0, 0.55, n_items)).astype(np.float32)

    if scenario == "aligned":
        observed_salience += 0.7 * zscore(future_queries)
    elif scenario == "dormant_future":
        # A low-observed cluster becomes important later. Offline oracle sees it;
        # online policies need to infer it from reliability/reacquisition/novelty.
        dormant_topic = int(rng.integers(0, len(TOPICS)))
        mask = topic == dormant_topic
        future_queries[mask] += rng.poisson(5.0, size=int(mask.sum()))
        observed_salience[mask] -= 2.0 + rng.random(int(mask.sum()))
        reacquire_cost[mask] += 2.0
        novelty[mask] += 0.4
    elif scenario == "stale_salience":
        # Salient old items become costly if kept as-is.
        stale_topic = int(rng.integers(0, len(TOPICS)))
        mask = (topic == stale_topic) & (time < 0.55)
        observed_salience[mask] += 3.0
        stale_risk[mask] += 0.85
        future_queries[mask] *= 0.25
    elif scenario == "redundant_burst":
        burst_topic = int(rng.integers(0, len(TOPICS)))
        mask = (topic == burst_topic) & (time > 0.40) & (time < 0.75)
        observed_salience[mask] += 1.8
        novelty[mask] *= 0.20
        # Utility saturates: many duplicates, one or two are enough.
        future_queries[mask] += 1.0
    elif scenario == "topic_shift":
        early = time < 0.50
        late_topics = rng.choice(len(TOPICS), size=3, replace=False)
        future_queries[early] *= 0.35
        future_queries[np.isin(topic, late_topics) & ~early] += 2.5
        observed_salience[early] += 1.0
        observed_salience[np.isin(topic, late_topics) & ~early] += 0.25
    else:
        raise ValueError(scenario)

    stale_risk = np.clip(stale_risk, 0.0, 1.0)
    novelty = np.clip(novelty, 0.0, 1.0)
    future_utility = future_queries * evidence_value * reliability
    return {
        "topic": topic.astype(np.int64),
        "time": time.astype(np.float32),
        "reliability": reliability.astype(np.float32),
        "novelty": novelty.astype(np.float32),
        "reacquire_cost": reacquire_cost.astype(np.float32),
        "stale_risk": stale_risk.astype(np.float32),
        "future_queries": future_queries.astype(np.float32),
        "evidence_value": evidence_value.astype(np.float32),
        "observed_salience": observed_salience.astype(np.float32),
        "future_utility": future_utility.astype(np.float32),
    }


def policy_select(policy: str, world: Dict[str, np.ndarray], budget: int, rng: np.random.Generator) -> np.ndarray:
    n = len(world["time"])
    if policy == "random":
        return rng.choice(n, size=min(budget, n), replace=False).astype(np.int64)
    if policy == "recency":
        return choose_top(world["time"], budget)
    if policy == "online_salience":
        score = zscore(world["observed_salience"]) + 0.10 * zscore(world["time"])
        return choose_top(score, budget)
    if policy == "stale_averse":
        score = zscore(world["observed_salience"]) + 0.25 * zscore(world["reacquire_cost"]) - 1.20 * zscore(world["stale_risk"])
        return choose_top(score, budget)
    if policy == "risk_aware_oas":
        # OAS-style: score uses only online features, not future utility.
        score = (
            0.80 * zscore(world["observed_salience"])
            + 0.55 * zscore(world["reacquire_cost"])
            + 0.45 * zscore(world["novelty"])
            + 0.35 * zscore(world["reliability"])
            - 0.85 * zscore(world["stale_risk"])
            + 0.12 * zscore(world["time"])
        )
        return choose_top(score, budget)
    if policy == "online_diversity":
        base = zscore(world["observed_salience"]) + 0.35 * zscore(world["novelty"]) - 0.45 * zscore(world["stale_risk"])
        picked: List[int] = []
        used_topics: set[int] = set()
        order = list(np.argsort(-base))
        # One pass: prefer new topics.
        for idx in order:
            if len(picked) >= budget:
                break
            t = int(world["topic"][idx])
            if t not in used_topics:
                picked.append(int(idx)); used_topics.add(t)
        # Fill leftovers by score.
        for idx in order:
            if len(picked) >= budget:
                break
            if int(idx) not in picked:
                picked.append(int(idx))
        return np.array(picked, dtype=np.int64)
    if policy == "offline_oracle":
        # Not online-observable: upper anchor only.
        score = zscore(world["future_utility"]) + 0.45 * zscore(world["reacquire_cost"]) - 0.85 * zscore(world["stale_risk"])
        return choose_top(score, budget)
    raise ValueError(policy)


def evaluate(world: Dict[str, np.ndarray], retained: np.ndarray, budget: int) -> Dict[str, float]:
    retained_set = set(int(i) for i in retained)
    if len(retained) == 0:
        return {"score": 0.0, "utility_retained": 0.0, "stale_penalty": 0.0, "reacquire_penalty": float(np.sum(world["future_queries"] * world["reacquire_cost"]))}
    ret = np.zeros(len(world["time"]), dtype=bool)
    ret[retained] = True
    utility_retained = float(np.sum(world["future_utility"][ret]))
    stale_penalty = float(np.sum(world["stale_risk"][ret] * np.maximum(0.0, world["observed_salience"][ret]) * 0.8))
    reacquire_penalty = float(np.sum((~ret) * world["future_queries"] * world["reacquire_cost"] * 0.18))
    # Duplicate cost: extra items from same topic yield diminishing returns.
    duplicate_cost = 0.0
    for t in np.unique(world["topic"][ret]):
        cnt = int(np.sum(world["topic"][ret] == t))
        if cnt > 1:
            duplicate_cost += 0.15 * (cnt - 1) ** 1.25
    score = utility_retained - stale_penalty - reacquire_penalty - duplicate_cost
    return {
        "score": score,
        "utility_retained": utility_retained,
        "stale_penalty": stale_penalty,
        "reacquire_penalty": reacquire_penalty,
        "duplicate_cost": float(duplicate_cost),
        "topic_coverage": float(len(np.unique(world["topic"][ret])) / len(TOPICS)),
        "future_utility_fraction": float(utility_retained / (np.sum(world["future_utility"]) + 1e-8)),
        "online_observable": 0.0 if "oracle" in "" else 1.0,
    }


@dataclass
class Row:
    seed: int
    scenario: str
    budget: int
    policy: str
    online_feasible: int
    score: float
    utility_retained: float
    stale_penalty: float
    reacquire_penalty: float
    duplicate_cost: float
    topic_coverage: float
    future_utility_fraction: float


def run(seed_count: int, n_items: int, budgets: List[int]) -> List[Row]:
    rows: List[Row] = []
    for seed in range(seed_count):
        rng = np.random.default_rng(10_000 + seed)
        for scenario in SCENARIOS:
            world = make_stream(seed=seed, scenario=scenario, n_items=n_items)
            for budget in budgets:
                for policy in POLICIES:
                    retained = policy_select(policy, world, budget, rng)
                    metrics = evaluate(world, retained, budget)
                    rows.append(Row(
                        seed=seed,
                        scenario=scenario,
                        budget=budget,
                        policy=policy,
                        online_feasible=0 if policy == "offline_oracle" else 1,
                        score=float(metrics["score"]),
                        utility_retained=float(metrics["utility_retained"]),
                        stale_penalty=float(metrics["stale_penalty"]),
                        reacquire_penalty=float(metrics["reacquire_penalty"]),
                        duplicate_cost=float(metrics["duplicate_cost"]),
                        topic_coverage=float(metrics["topic_coverage"]),
                        future_utility_fraction=float(metrics["future_utility_fraction"]),
                    ))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.scenario, r.budget), {}).setdefault(r.policy, []).append(r.score)
    winners: Dict[str, str] = {}
    winners_online: Dict[str, str] = {}
    counts: Dict[str, int] = {}
    online_counts: Dict[str, int] = {}
    for (scenario, budget), pols in sorted(by.items()):
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        winner = max(means, key=means.get)
        key = f"{scenario}/B{budget}"
        winners[key] = winner
        counts[winner] = counts.get(winner, 0) + 1
        online_means = {p: m for p, m in means.items() if p != "offline_oracle"}
        ow = max(online_means, key=online_means.get)
        winners_online[key] = ow
        online_counts[ow] = online_counts.get(ow, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "score", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": winners_online,
        "winner_counts_excluding_oracle": online_counts,
        "interpretation": "Offline oracle is an upper anchor. If risk_aware_oas or online_diversity beats raw salience under dormant/stale/redundant regimes, the delayed-cost framing is worth keeping.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {
        "project": "CloudtainerML",
        "revision": "rev0009",
        "probe": "observability_safe_retention",
        "config": {"scenarios": SCENARIOS, "policies": POLICIES},
        "summary": summarize(rows),
        "rows": [asdict(r) for r in rows],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=8)
    p.add_argument("--n-items", type=int, default=128)
    p.add_argument("--budgets", type=int, nargs="+", default=[8, 16, 32])
    p.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0009_OBSERVABILITY_SAFE_RETENTION_SMOKE.json"))
    p.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0009_OBSERVABILITY_SAFE_RETENTION_SMOKE.csv"))
    args = p.parse_args()
    rows = run(args.seeds, args.n_items, args.budgets)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
