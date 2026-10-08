#!/usr/bin/env python3
"""Sliding-window HIST positional-signal toy probe.

A June 2026 theory paper argues that finite sliding-window generation can break
permutation symmetry even without positional encodings: the window update reveals
which token left the window. This probe does not prove universality; it tests the
small operational signal.

Given histogram_before, incoming token, and histogram_after, the outgoing token is
recoverable by delta arithmetic. We compare exact delta, noisy/quantized delta,
and static histogram baselines on synthetic streams.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


def make_stream(seed: int, regime: str, length: int, alphabet: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if regime == "iid_balanced":
        return rng.integers(0, alphabet, size=length, dtype=np.int64)
    if regime == "bursty_runs":
        xs = []
        while len(xs) < length:
            tok = int(rng.integers(0, alphabet))
            run = int(rng.integers(2, 9))
            xs.extend([tok] * run)
        return np.array(xs[:length], dtype=np.int64)
    if regime == "low_entropy_cycles":
        base = np.arange(alphabet, dtype=np.int64)
        xs = np.tile(base, int(np.ceil(length / alphabet)))[:length]
        noise = rng.random(length) < 0.08
        xs[noise] = rng.integers(0, alphabet, size=int(np.sum(noise)))
        return xs
    if regime == "adversarial_same_hist":
        # Many windows share similar histograms but differ in order.
        block = np.repeat(np.arange(alphabet, dtype=np.int64), 2)
        xs = []
        while len(xs) < length:
            b = block.copy(); rng.shuffle(b); xs.extend(b.tolist())
        return np.array(xs[:length], dtype=np.int64)
    raise ValueError(regime)


def hist(tokens: np.ndarray, alphabet: int) -> np.ndarray:
    return np.bincount(tokens, minlength=alphabet).astype(np.float32)


@dataclass
class Row:
    seed: int
    regime: str
    method: str
    alphabet: int
    window: int
    steps: int
    outgoing_accuracy: float
    order_bit_accuracy: float
    invalid_delta_rate: float
    state_reconstruction_error: float


def eval_method(seed: int, regime: str, method: str, alphabet: int, window: int, length: int) -> Row:
    rng = np.random.default_rng(seed + 99)
    xs = make_stream(seed, regime, length, alphabet)
    correct = 0
    bits = 0
    invalid = 0
    recon_err = []
    current = hist(xs[:window], alphabet)
    rec_hist = current.copy()
    for t in range(window, length):
        incoming = int(xs[t])
        true_out = int(xs[t-window])
        before = current.copy()
        after = current.copy()
        after[true_out] -= 1.0
        after[incoming] += 1.0
        if method == "delta_exact":
            delta = before.copy(); delta[incoming] += 1.0; delta -= after
            pred = int(np.argmax(delta))
        elif method == "delta_int8_noisy":
            scale = max(1.0, float(np.max(before))) / 127.0
            qb = np.round(before / scale).astype(np.int16)
            qa = np.round(after / scale).astype(np.int16)
            delta = qb.astype(np.float32); delta[incoming] += round(1.0 / scale); delta -= qa.astype(np.float32)
            delta += rng.normal(0, 0.10, size=alphabet)
            pred = int(np.argmax(delta))
            invalid += int(np.max(delta) < 0.4)
        elif method == "static_hist_mode":
            pred = int(np.argmax(before))
        elif method == "static_hist_minority":
            pred = int(np.argmin(before))
        elif method == "random":
            pred = int(rng.integers(0, alphabet))
        else:
            raise ValueError(method)
        correct += int(pred == true_out)
        bits += int((pred < incoming) == (true_out < incoming))
        # State update using the predicted outgoing token. Delta methods should preserve
        # the histogram; static baselines drift when their outgoing guess is wrong.
        rec_hist[pred] -= 1.0
        rec_hist[incoming] += 1.0
        recon_err.append(float(np.mean(np.abs(rec_hist - after)) / max(1.0, window)))
        current = after
    steps = length - window
    return Row(seed, regime, method, alphabet, window, steps, correct / steps, bits / steps, invalid / steps, float(np.mean(recon_err)))

def summarize(rows: List[Row]) -> dict:
    by: Dict[str, dict] = {}
    for regime in sorted({r.regime for r in rows}):
        for method in sorted({r.method for r in rows}):
            sub = [r for r in rows if r.regime == regime and r.method == method]
            by[f"{regime}/{method}"] = {
                "mean_outgoing_accuracy": float(np.mean([r.outgoing_accuracy for r in sub])),
                "mean_order_bit_accuracy": float(np.mean([r.order_bit_accuracy for r in sub])),
                "mean_invalid_delta_rate": float(np.mean([r.invalid_delta_rate for r in sub])),
                "mean_state_reconstruction_error": float(np.mean([r.state_reconstruction_error for r in sub])),
            }
    winners = {}
    for regime in sorted({r.regime for r in rows}):
        cand = []
        for method in sorted({r.method for r in rows}):
            m = by[f"{regime}/{method}"]
            cand.append((-m["mean_outgoing_accuracy"], method))
        cand.sort(); winners[regime] = cand[0][1]
    return {"row_count": len(rows), "by_regime_method": by, "winners": winners, "primary_metric": {"name": "outgoing_accuracy", "direction": "higher_is_better"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/probe-results/REV0008_HIST_WINDOW_ORDER_SMOKE"))
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--length", type=int, default=512)
    args = ap.parse_args()
    regimes = ["iid_balanced", "bursty_runs", "low_entropy_cycles", "adversarial_same_hist"]
    methods = ["delta_exact", "delta_int8_noisy", "static_hist_mode", "static_hist_minority", "random"]
    rows: List[Row] = []
    for seed in range(args.seeds):
        for regime in regimes:
            for alphabet in [4, 8, 16]:
                for window in [8, 16, 32]:
                    for method in methods:
                        rows.append(eval_method(seed, regime, method, alphabet, window, args.length))
    out = args.out; out.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = out.with_suffix(".csv"), out.with_suffix(".json")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader(); writer.writerows(asdict(r) for r in rows)
    payload = {"probe": "hist_window_order", "purpose": "Operational positional signal from sliding-window histogram updates without explicit positional encoding.", "config": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()}, "rows": [asdict(r) for r in rows], "summary": summarize(rows), "csv": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"]["winners"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
