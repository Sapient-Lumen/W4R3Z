#!/usr/bin/env python3
"""IntentKV-style cross-turn intent-aware pruning toy probe.

This probe models an agent session as turns of tokens with intent labels,
tool-result markers, and irrelevant recent noise. A session QueryMemory tracks
cross-turn intent. Policies choose which history tokens survive a fixed KV
budget. We measure whether buried intent-critical tokens survive, whether stale
or adversarial recent tokens crowd them out, and whether slot-map-like pruning
can remain prefix-cache-friendly in spirit.

Synthetic only; useful as a small falsifier for cross-turn memory/pruning ideas.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


def l2norm(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def make_session(seed: int, scenario: str, turns: int, tokens_per_turn: int, dim: int) -> dict:
    rng = np.random.default_rng(seed)
    n = turns * tokens_per_turn
    intents = l2norm(rng.normal(size=(5, dim)).astype(np.float32))
    topic_path = []
    if scenario == "stable_intent":
        topic_path = [1] * turns
    elif scenario == "intent_shift":
        topic_path = [0] * (turns // 2) + [3] * (turns - turns // 2)
    elif scenario == "buried_tool_result":
        topic_path = [2] * turns
    elif scenario == "adversarial_recent_noise":
        topic_path = [4] * max(1, turns - 2) + [0, 0]
    else:
        raise ValueError(scenario)

    emb = np.zeros((n, dim), dtype=np.float32)
    labels = []
    critical = np.zeros(n, dtype=np.float32)
    stale = np.zeros(n, dtype=np.float32)
    tool = np.zeros(n, dtype=np.float32)
    intent_label = np.zeros(n, dtype=np.int64)
    pos = 0
    target_intent = topic_path[-1]
    for t, intent in enumerate(topic_path):
        for j in range(tokens_per_turn):
            noise = rng.normal(size=dim).astype(np.float32)
            vec = 0.65 * intents[intent] + 0.35 * noise
            kind = "context"
            # One buried tool result is critical; one old pre-shift fact is stale.
            if scenario == "buried_tool_result" and t == 1 and j == tokens_per_turn // 2:
                vec = 0.95 * intents[intent] + 0.05 * noise
                critical[pos] = 1.0; tool[pos] = 1.0; kind = "critical_tool"
            elif scenario == "intent_shift" and t == max(0, turns // 2 - 2) and j == tokens_per_turn // 3:
                stale[pos] = 1.0; kind = "stale_old_intent"
            elif intent == target_intent and j in {1, tokens_per_turn - 2} and t < turns - 1:
                critical[pos] = 1.0; kind = "critical_intent"
            if scenario == "adversarial_recent_noise" and t >= turns - 2:
                # Recent irrelevant tokens look locally salient but point at wrong topic.
                vec = 0.90 * intents[0] + 0.10 * noise
                if j % 5 == 0:
                    stale[pos] = 1.0; kind = "recent_decoy"
            emb[pos] = l2norm(vec.reshape(1, -1))[0]
            intent_label[pos] = intent
            labels.append(kind)
            pos += 1
    query = l2norm((0.92 * intents[target_intent] + 0.08 * rng.normal(size=dim).astype(np.float32)).reshape(1, -1))[0]
    age = np.linspace(0.0, 1.0, n, dtype=np.float32)
    # QueryMemory: exponentially decayed summary of user/tool content, plus final query.
    qm = np.zeros(dim, dtype=np.float32)
    for i in range(n):
        decay = 0.94 if labels[i] != "critical_tool" else 0.985
        qm = decay * qm + (1.0 - decay) * emb[i]
    qm = l2norm((0.65 * qm + 0.35 * query).reshape(1, -1))[0]
    return {"emb": emb, "labels": labels, "critical": critical, "stale": stale, "tool": tool, "query": query, "query_memory": qm, "age": age, "target_intent": target_intent, "intent_label": intent_label}


def select(session: dict, policy: str, budget: int, seed: int) -> np.ndarray:
    emb, q, qm, age = session["emb"], session["query"], session["query_memory"], session["age"]
    rng = np.random.default_rng(seed + 313)
    n = len(emb)
    current_score = emb @ q
    memory_score = emb @ qm
    tool_bonus = session["tool"]
    critical_oracle = session["critical"]
    stale_penalty = session["stale"]
    if policy == "full_cache":
        return np.arange(n, dtype=np.int64)
    if policy == "recency":
        score = age
    elif policy == "current_query_only":
        score = current_score + 0.05 * age
    elif policy == "session_query_memory":
        score = memory_score + 0.05 * age + 0.35 * tool_bonus
    elif policy == "intentkv_toy":
        score = 0.55 * current_score + 0.55 * memory_score + 0.07 * age + 0.55 * tool_bonus - 0.35 * stale_penalty
    elif policy == "slotmap_sentinel_toy":
        # Same retention score as intentkv_toy, but enforces a small quota per turn-like region.
        score = 0.50 * current_score + 0.60 * memory_score + 0.15 * tool_bonus - 0.25 * stale_penalty
        regions = np.array_split(np.arange(n), max(1, budget // 8))
        picks: list[int] = []
        quota = max(1, budget // len(regions))
        for region in regions:
            take = min(quota, len(region))
            order = region[np.argsort(-score[region])[:take]]
            picks.extend(int(x) for x in order)
        if len(picks) < budget:
            remaining = [i for i in np.argsort(-score) if int(i) not in set(picks)]
            picks.extend(int(i) for i in remaining[: budget - len(picks)])
        return np.array(picks[:budget], dtype=np.int64)
    elif policy == "oracle_critical":
        score = current_score + 1e3 * critical_oracle - 100.0 * stale_penalty
    elif policy == "random":
        return rng.choice(n, size=min(budget, n), replace=False).astype(np.int64)
    else:
        raise ValueError(policy)
    take = min(budget, n)
    return np.argpartition(-score, take - 1)[:take].astype(np.int64)


@dataclass
class Row:
    seed: int
    scenario: str
    policy: str
    budget: int
    tokens: int
    kept: int
    critical_retention: float
    tool_retention: float
    stale_retention: float
    current_intent_purity: float
    raw_read_fraction: float
    answer_error_proxy: float
    slotmap_fragmentation_proxy: float


def eval_policy(seed: int, scenario: str, policy: str, turns: int, tokens_per_turn: int, dim: int, budget: int) -> Row:
    s = make_session(seed, scenario, turns, tokens_per_turn, dim)
    keep = select(s, policy, budget, seed)
    kept = set(int(i) for i in keep)
    critical_idx = np.where(s["critical"] > 0.5)[0]
    tool_idx = np.where(s["tool"] > 0.5)[0]
    stale_idx = np.where(s["stale"] > 0.5)[0]
    crit_ret = float(sum(int(i in kept) for i in critical_idx) / max(1, len(critical_idx)))
    tool_ret = float(sum(int(i in kept) for i in tool_idx) / max(1, len(tool_idx)))
    stale_ret = float(sum(int(i in kept) for i in stale_idx) / max(1, len(stale_idx)))
    current_purity = float(np.mean(s["intent_label"][keep] == s["target_intent"])) if len(keep) else 0.0
    # Error proxy rewards critical and purity, penalizes stale/low budget. Not an accuracy claim.
    err = float(max(0.0, 1.0 - 0.65 * crit_ret - 0.25 * current_purity + 0.35 * stale_ret))
    sorted_keep = np.sort(keep)
    gaps = np.diff(sorted_keep) if len(sorted_keep) > 1 else np.array([0])
    frag = float(np.mean(gaps > tokens_per_turn)) if len(gaps) else 0.0
    return Row(seed, scenario, policy, budget, turns * tokens_per_turn, len(keep), crit_ret, tool_ret, stale_ret, current_purity, len(keep)/(turns*tokens_per_turn), err, frag)


def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for scenario in sorted({r.scenario for r in rows}):
        for policy in sorted({r.policy for r in rows}):
            sub = [r for r in rows if r.scenario == scenario and r.policy == policy]
            by[f"{scenario}/{policy}"] = {
                "mean_critical_retention": float(np.mean([r.critical_retention for r in sub])),
                "mean_tool_retention": float(np.mean([r.tool_retention for r in sub])),
                "mean_stale_retention": float(np.mean([r.stale_retention for r in sub])),
                "mean_current_intent_purity": float(np.mean([r.current_intent_purity for r in sub])),
                "mean_raw_read_fraction": float(np.mean([r.raw_read_fraction for r in sub])),
                "mean_answer_error_proxy": float(np.mean([r.answer_error_proxy for r in sub])),
                "mean_slotmap_fragmentation_proxy": float(np.mean([r.slotmap_fragmentation_proxy for r in sub])),
            }
    winners = {}
    for scenario in sorted({r.scenario for r in rows}):
        cand = []
        for policy in sorted({r.policy for r in rows}):
            if policy == "full_cache":
                continue
            m = by[f"{scenario}/{policy}"]
            score = m["mean_critical_retention"] + 0.2*m["mean_current_intent_purity"] - 0.5*m["mean_stale_retention"] - 0.2*m["mean_answer_error_proxy"]
            cand.append((-score, policy))
        cand.sort(); winners[scenario] = cand[0][1]
    return {"row_count": len(rows), "by_scenario_policy": by, "winners_excluding_full_cache": winners, "primary_metric": {"name": "critical_retention_purity_minus_stale_error", "direction": "higher_is_better"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0008_INTENT_KV_PRUNING_SMOKE"))
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--turns", type=int, default=9)
    ap.add_argument("--tokens-per-turn", type=int, default=32)
    ap.add_argument("--dim", type=int, default=48)
    args = ap.parse_args()
    scenarios = ["stable_intent", "intent_shift", "buried_tool_result", "adversarial_recent_noise"]
    policies = ["full_cache", "recency", "current_query_only", "session_query_memory", "intentkv_toy", "slotmap_sentinel_toy", "oracle_critical", "random"]
    budgets = [24, 48, 96]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for scenario in scenarios:
            for budget in budgets:
                for policy in policies:
                    rows.append(eval_policy(seed, scenario, policy, args.turns, args.tokens_per_turn, args.dim, budget))
    out = args.out; out.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = out.with_suffix(".csv"), out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows(asdict(r) for r in rows)
    payload = {"probe": "intent_kv_pruning", "purpose": "Cross-turn intent-aware KV pruning toy with buried tool-result and stale-intent traps.", "config": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}, "rows": [asdict(r) for r in rows], "summary": summarize(rows), "csv": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"]["winners_excluding_full_cache"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
