#!/usr/bin/env python3
"""Supervised memory transition toy probe.

A tiny analogue of Supervised Memory Training (SMT): first create teacher labels
for the sufficient memory state at every timestep, then learn a one-step memory
updater from those labels. This avoids unrolled credit assignment in the toy and
lets us compare supervised transitions to recency buffers and noisy recurrent
updates.

Task: streams of key/value updates followed by random future key queries. The
sufficient state is the latest value for every key.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REGIMES = ["short_delays", "long_delays", "bursty_overwrites", "sparse_queries", "noisy_events"]
POLICIES = ["zero_memory", "recency_buffer", "noisy_recurrent_proxy", "ridge_supervised_update", "teacher_state_oracle"]


def one_hot(i: int, n: int) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64); x[i] = 1.0; return x


def make_sequence(seed: int, regime: str, keys: int, values: int, length: int, query_n: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(63000 + seed)
    if regime == "short_delays":
        update_prob = 0.65
    elif regime == "long_delays":
        update_prob = 0.28
    elif regime == "bursty_overwrites":
        update_prob = 0.78
    elif regime == "sparse_queries":
        update_prob = 0.45
    elif regime == "noisy_events":
        update_prob = 0.55
    else:
        raise ValueError(regime)
    events = []
    state = np.zeros(keys, dtype=np.int64)
    states = []
    hot_key = rng.integers(0, keys)
    for t in range(length):
        if regime == "bursty_overwrites" and rng.random() < 0.65:
            k = hot_key if rng.random() < 0.75 else rng.integers(0, keys)
        else:
            k = rng.integers(0, keys)
        if rng.random() < update_prob:
            v = rng.integers(0, values)
            if regime == "noisy_events" and rng.random() < 0.18:
                # No-op masquerading as an update; teacher ignores via mask.
                mask = 0
            else:
                mask = 1
                state[k] = v
        else:
            v = 0; mask = 0
        events.append((k, v, mask))
        states.append(state.copy())
    q_times = rng.choice(np.arange(max(2, length // 4), length), size=query_n, replace=True)
    q_keys = rng.integers(0, keys, size=query_n)
    q_answers = np.array([states[t][k] for t, k in zip(q_times, q_keys)], dtype=np.int64)
    return {"events": np.array(events, dtype=np.int64), "states": np.array(states, dtype=np.int64), "q_times": q_times.astype(np.int64), "q_keys": q_keys.astype(np.int64), "q_answers": q_answers}


def state_features(state: np.ndarray, values: int) -> np.ndarray:
    # One-hot latest value for each key flattened.
    out = np.zeros((len(state), values), dtype=np.float64)
    out[np.arange(len(state)), state] = 1.0
    return out.reshape(-1)


def event_features(event: np.ndarray, keys: int, values: int) -> np.ndarray:
    k, v, mask = map(int, event)
    return np.concatenate([one_hot(k, keys), one_hot(v, values), np.array([float(mask)])])



def transition_features(state: np.ndarray, event: np.ndarray, keys: int, values: int) -> np.ndarray:
    """Features that make the supervised one-step update linearly learnable.

    The teacher label gives the target memory at every timestep; these features
    encode "copy previous value unless this key is updated" plus an explicit
    update slot. This is the toy analogue of making memory labels available
    before training an updater.
    """
    k, v, mask = map(int, event)
    prev = state_features(state, values).reshape(keys, values)
    copy_part = prev.copy()
    update_part = np.zeros_like(copy_part)
    if mask:
        copy_part[k, :] = 0.0
        update_part[k, v] = 1.0
    return np.concatenate([copy_part.reshape(-1), update_part.reshape(-1), np.array([float(mask)])])

def build_training(seeds: int, regimes: List[str], keys: int, values: int, length: int) -> Tuple[np.ndarray, np.ndarray]:
    xs = []; ys = []
    for seed in range(seeds):
        for regime in regimes:
            seq = make_sequence(seed, regime, keys, values, length, query_n=8)
            prev = np.zeros(keys, dtype=np.int64)
            for event, st in zip(seq["events"], seq["states"]):
                xs.append(transition_features(prev, event, keys, values))
                ys.append(state_features(st, values))
                prev = st
    return np.vstack(xs), np.vstack(ys)


def ridge_fit(x: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    xtx = x.T @ x + lam * np.eye(x.shape[1])
    return np.linalg.solve(xtx, x.T @ y)


def rollout_policy(policy: str, seq: Dict[str, np.ndarray], keys: int, values: int, W: np.ndarray | None, buffer: int, rng: np.random.Generator) -> np.ndarray:
    length = len(seq["events"])
    pred_states = np.zeros((length, keys), dtype=np.int64)
    if policy == "teacher_state_oracle":
        return seq["states"].copy()
    mem = np.zeros(keys, dtype=np.int64)
    recent: List[Tuple[int, int, int]] = []
    for t, event in enumerate(seq["events"]):
        k, v, mask = map(int, event)
        if policy == "zero_memory":
            mem = np.zeros(keys, dtype=np.int64)
        elif policy == "recency_buffer":
            recent.append((k, v, mask)); recent = recent[-buffer:]
            mem = np.zeros(keys, dtype=np.int64)
            for kk, vv, mm in recent:
                if mm:
                    mem[kk] = vv
        elif policy == "noisy_recurrent_proxy":
            if mask and rng.random() > 0.18:
                mem[k] = v
            # Recency/gradient-noise proxy: old keys randomly decay under long streams.
            if rng.random() < 0.04:
                mem[rng.integers(0, keys)] = 0
        elif policy == "ridge_supervised_update":
            assert W is not None
            feat = transition_features(mem, event, keys, values)
            pred = feat @ W
            mem = np.argmax(pred.reshape(keys, values), axis=1).astype(np.int64)
        else:
            raise ValueError(policy)
        pred_states[t] = mem
    return pred_states


@dataclass
class Row:
    seed: int
    regime: str
    policy: str
    buffer: int
    state_accuracy: float
    query_accuracy: float
    overwrite_accuracy: float
    memory_mse: float


def eval_policy(seed: int, regime: str, policy: str, keys: int, values: int, length: int, query_n: int, W: np.ndarray | None, buffer: int) -> Row:
    rng = np.random.default_rng(75000 + seed + buffer)
    seq = make_sequence(10_000 + seed, regime, keys, values, length, query_n)
    pred = rollout_policy(policy, seq, keys, values, W, buffer, rng)
    true = seq["states"]
    state_acc = float(np.mean(pred == true))
    answers = np.array([pred[t, k] for t, k in zip(seq["q_times"], seq["q_keys"])], dtype=np.int64)
    query_acc = float(np.mean(answers == seq["q_answers"]))
    events = seq["events"]
    overwrite_mask = events[:, 2] == 1
    overwrite_acc = float(np.mean(pred[overwrite_mask] == true[overwrite_mask])) if np.any(overwrite_mask) else state_acc
    mse = float(np.mean((pred - true) ** 2) / max(1, values ** 2))
    return Row(seed, regime, policy, buffer, state_acc, query_acc, overwrite_acc, mse)


def run(train_seeds: int, test_seeds: int, keys: int, values: int, length: int, query_n: int, buffers: List[int]) -> List[Row]:
    x, y = build_training(train_seeds, REGIMES, keys, values, length)
    W = ridge_fit(x, y, lam=1e-3)
    rows: List[Row] = []
    for seed in range(test_seeds):
        for regime in REGIMES:
            for buffer in buffers:
                for policy in POLICIES:
                    rows.append(eval_policy(seed, regime, policy, keys, values, length, query_n, W, buffer))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[Tuple[str, int], Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault((r.regime, r.buffer), {}).setdefault(r.policy, []).append(r.query_accuracy)
    winners: Dict[str, str] = {}; counts: Dict[str, int] = {}
    practical: Dict[str, str] = {}; pcounts: Dict[str, int] = {}
    for (regime, buffer), pols in by.items():
        means = {p: float(np.mean(v)) for p, v in pols.items()}
        w = max(means, key=means.get); winners[f"{regime}/B{buffer}"] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p != "teacher_state_oracle"}
        pw = max(means2, key=means2.get); practical[f"{regime}/B{buffer}"] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "query_accuracy", "direction": "higher_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "Supervised one-step transition labels win if they keep long-delay and overwrite facts without unrolled credit assignment; recency buffers should only win short-delay regimes.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {"project": "CloudtainerML", "revision": "rev0010", "probe": "smt_transition_training", "config": {"regimes": REGIMES, "policies": POLICIES}, "summary": summarize(rows), "rows": [asdict(r) for r in rows]}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows([asdict(r) for r in rows])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-seeds", type=int, default=12)
    ap.add_argument("--test-seeds", type=int, default=12)
    ap.add_argument("--keys", type=int, default=10)
    ap.add_argument("--values", type=int, default=6)
    ap.add_argument("--length", type=int, default=96)
    ap.add_argument("--query-n", type=int, default=64)
    ap.add_argument("--buffers", type=int, nargs="+", default=[4, 12, 32])
    ap.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0010_SMT_TRANSITION_SMOKE.json"))
    ap.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0010_SMT_TRANSITION_SMOKE.csv"))
    args = ap.parse_args()
    rows = run(args.train_seeds, args.test_seeds, args.keys, args.values, args.length, args.query_n, args.buffers)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
