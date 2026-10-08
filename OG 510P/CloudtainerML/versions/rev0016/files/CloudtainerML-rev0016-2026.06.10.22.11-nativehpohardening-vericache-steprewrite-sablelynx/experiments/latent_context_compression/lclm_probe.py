#!/usr/bin/env python3
"""Latent-context compression toy probe.

A cheap synthetic analogue of encoder-decoder context compression / LCLM-style
"skim compressed context, then expand relevant spans on demand" behavior.

We generate long contexts as chunks of key-value facts. Compression policies
store a few latent summaries per chunk. At query time, compressed summaries can
be used alone or to select chunks for raw expansion. This lets us test when
latent context compression is a real alternative to raw KV retention, at toy
scale and without training a language model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

SCENARIOS = ["aligned_chunks", "diffuse_target", "adversarial_summary", "late_needle", "multi_fact_bridge"]
POLICIES = [
    "compressed_mean_only",
    "compressed_extreme_only",
    "compressed_then_expand_top1",
    "compressed_then_expand_top2",
    "random_expand_top1",
    "uniform_sparse_raw",
    "oracle_expand_chunk",
    "full_raw_oracle",
]


def l2norm(x: np.ndarray, axis: int = -1) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + 1e-8)


def softmax(x: np.ndarray) -> np.ndarray:
    y = x - np.max(x)
    e = np.exp(y)
    return e / (np.sum(e) + 1e-12)


def attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, temp: float = 0.09) -> Tuple[np.ndarray, np.ndarray]:
    logits = (k @ q) / max(temp, 1e-8)
    w = softmax(logits)
    return w @ v, w


def make_context(seed: int, scenario: str, n_chunks: int, chunk_size: int, dim: int) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    n = n_chunks * chunk_size
    base_topics = l2norm(rng.normal(size=(n_chunks, dim)).astype(np.float32))
    k = np.zeros((n, dim), dtype=np.float32)
    v = np.zeros((n, dim), dtype=np.float32)
    chunk_id = np.repeat(np.arange(n_chunks), chunk_size)
    for c in range(n_chunks):
        sl = slice(c * chunk_size, (c + 1) * chunk_size)
        k[sl] = l2norm(0.55 * base_topics[c] + 0.45 * rng.normal(size=(chunk_size, dim)).astype(np.float32))
        v[sl] = l2norm(0.45 * base_topics[c] + 0.55 * rng.normal(size=(chunk_size, dim)).astype(np.float32))
    target_chunk = int(rng.integers(0, n_chunks))
    target_offset = int(rng.integers(0, chunk_size))
    target = target_chunk * chunk_size + target_offset
    bridge = None

    if scenario == "aligned_chunks":
        q = l2norm(k[target] + 0.04 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    elif scenario == "diffuse_target":
        target_chunk = int(rng.integers(0, n_chunks))
        target = target_chunk * chunk_size + int(rng.integers(0, chunk_size))
        # Make the chunk mean poor: every fact in target chunk points in different directions.
        sl = slice(target_chunk * chunk_size, (target_chunk + 1) * chunk_size)
        k[sl] = l2norm(rng.normal(size=(chunk_size, dim)).astype(np.float32))
        v[sl] = l2norm(rng.normal(size=(chunk_size, dim)).astype(np.float32))
        q = l2norm(k[target] + 0.03 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    elif scenario == "adversarial_summary":
        target_chunk = int(rng.integers(0, n_chunks))
        decoy_chunk = (target_chunk + int(rng.integers(1, n_chunks))) % n_chunks
        target = target_chunk * chunk_size + int(rng.integers(0, chunk_size))
        q = l2norm(k[target] + 0.03 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        # Decoy chunk has mean near query but individual values contradict target.
        sl = slice(decoy_chunk * chunk_size, (decoy_chunk + 1) * chunk_size)
        k[sl] = l2norm(0.82 * q + 0.18 * rng.normal(size=(chunk_size, dim)).astype(np.float32))
        v[sl] = l2norm(-v[target] + 0.10 * rng.normal(size=(chunk_size, dim)).astype(np.float32))
    elif scenario == "late_needle":
        target_chunk = n_chunks - 1
        target = target_chunk * chunk_size + int(rng.integers(0, chunk_size))
        special = l2norm(rng.normal(size=dim).astype(np.float32)).reshape(-1)
        k[target] = special
        v[target] = l2norm(rng.normal(size=dim).astype(np.float32)).reshape(-1)
        q = l2norm(special + 0.02 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
    elif scenario == "multi_fact_bridge":
        # Query needs two chunks; success means output close to average of two raw fact values.
        target_chunk = int(rng.integers(0, n_chunks - 1))
        bridge_chunk = (target_chunk + int(rng.integers(1, n_chunks))) % n_chunks
        target = target_chunk * chunk_size + int(rng.integers(0, chunk_size))
        bridge = bridge_chunk * chunk_size + int(rng.integers(0, chunk_size))
        q = l2norm(0.58 * k[target] + 0.42 * k[bridge] + 0.03 * rng.normal(size=dim).astype(np.float32)).reshape(-1)
        v[target] = l2norm(v[target] + v[bridge]).reshape(-1)
    else:
        raise ValueError(scenario)

    return {"k": k, "v": v, "q": q.astype(np.float32), "chunk_id": chunk_id, "target": target, "target_chunk": target_chunk, "bridge": bridge}


def chunk_summaries(k: np.ndarray, v: np.ndarray, n_chunks: int, chunk_size: int, mode: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    sk: List[np.ndarray] = []
    sv: List[np.ndarray] = []
    sid: List[int] = []
    for c in range(n_chunks):
        sl = slice(c * chunk_size, (c + 1) * chunk_size)
        kc = k[sl]
        vc = v[sl]
        if mode == "mean":
            sk.append(l2norm(np.mean(kc, axis=0)).reshape(-1))
            sv.append(l2norm(np.mean(vc, axis=0)).reshape(-1))
            sid.append(c)
        elif mode == "extreme":
            m = l2norm(np.mean(kc, axis=0)).reshape(-1)
            # Keep a single representative far from the mean to preserve needles.
            idx = int(np.argmax(np.linalg.norm(kc - m[None, :], axis=1)))
            sk.append(kc[idx]); sv.append(vc[idx]); sid.append(c)
        elif mode == "mean_plus_extreme":
            m = l2norm(np.mean(kc, axis=0)).reshape(-1)
            idx = int(np.argmax(np.linalg.norm(kc - m[None, :], axis=1)))
            sk.extend([m, kc[idx]]); sv.extend([l2norm(np.mean(vc, axis=0)).reshape(-1), vc[idx]]); sid.extend([c, c])
        else:
            raise ValueError(mode)
    return np.stack(sk).astype(np.float32), np.stack(sv).astype(np.float32), np.array(sid, dtype=np.int64)


def policy_output(policy: str, world: Dict[str, object], n_chunks: int, chunk_size: int, dim: int, rng: np.random.Generator) -> Dict[str, object]:
    k = world["k"]; v = world["v"]; q = world["q"]
    assert isinstance(k, np.ndarray) and isinstance(v, np.ndarray) and isinstance(q, np.ndarray)
    target_chunk = int(world["target_chunk"])
    full_out, full_w = attention(q, k, v)
    if policy == "full_raw_oracle":
        return {"out": full_out, "selected_chunks": list(range(n_chunks)), "raw_tokens_used": n_chunks * chunk_size, "latent_tokens_used": 0}
    if policy == "uniform_sparse_raw":
        idx = np.arange(0, n_chunks * chunk_size, max(1, chunk_size // 2 + 1))[:n_chunks]
        out, _ = attention(q, k[idx], v[idx])
        return {"out": out, "selected_chunks": sorted(set((idx // chunk_size).tolist())), "raw_tokens_used": int(len(idx)), "latent_tokens_used": 0}
    if policy == "random_expand_top1":
        c = int(rng.integers(0, n_chunks))
        idx = np.arange(c * chunk_size, (c + 1) * chunk_size)
        out, _ = attention(q, k[idx], v[idx])
        return {"out": out, "selected_chunks": [c], "raw_tokens_used": int(len(idx)), "latent_tokens_used": n_chunks}
    if policy == "oracle_expand_chunk":
        chunks = [target_chunk]
        if world.get("bridge") is not None:
            chunks.append(int(world["bridge"]) // chunk_size)
        idx = np.concatenate([np.arange(c * chunk_size, (c + 1) * chunk_size) for c in sorted(set(chunks))])
        out, _ = attention(q, k[idx], v[idx])
        return {"out": out, "selected_chunks": sorted(set(chunks)), "raw_tokens_used": int(len(idx)), "latent_tokens_used": 0}

    mode = "mean" if "mean" in policy or "expand" in policy else "extreme"
    if policy in {"compressed_then_expand_top1", "compressed_then_expand_top2"}:
        sk, sv, sid = chunk_summaries(k, v, n_chunks, chunk_size, "mean_plus_extreme")
    else:
        sk, sv, sid = chunk_summaries(k, v, n_chunks, chunk_size, mode)
    lat_out, lat_w = attention(q, sk, sv)
    if policy in {"compressed_mean_only", "compressed_extreme_only"}:
        return {"out": lat_out, "selected_chunks": [], "raw_tokens_used": 0, "latent_tokens_used": int(len(sk))}
    if policy == "compressed_then_expand_top1":
        top = np.argsort(-lat_w)[:1]
    elif policy == "compressed_then_expand_top2":
        top = np.argsort(-lat_w)[:2]
    else:
        raise ValueError(policy)
    chunks = sorted(set(int(sid[i]) for i in top))
    idx = np.concatenate([np.arange(c * chunk_size, (c + 1) * chunk_size) for c in chunks])
    out, _ = attention(q, k[idx], v[idx])
    return {"out": out, "selected_chunks": chunks, "raw_tokens_used": int(len(idx)), "latent_tokens_used": int(len(sk))}


@dataclass
class Row:
    seed: int
    scenario: str
    n_chunks: int
    chunk_size: int
    policy: str
    target_chunk_hit: int
    output_rel_error: float
    output_cosine: float
    raw_tokens_used: int
    latent_tokens_used: int
    effective_token_budget: int
    compression_ratio_vs_full_raw: float


def run(seeds: int, n_chunks: int, chunk_size: int, dim: int) -> List[Row]:
    rows: List[Row] = []
    full_tokens = n_chunks * chunk_size
    for seed in range(seeds):
        rng = np.random.default_rng(30_000 + seed)
        for scenario in SCENARIOS:
            world = make_context(seed, scenario, n_chunks, chunk_size, dim)
            ref, _ = attention(world["q"], world["k"], world["v"])
            for policy in POLICIES:
                got = policy_output(policy, world, n_chunks, chunk_size, dim, rng)
                out = got["out"]
                err = float(np.linalg.norm(out - ref) / (np.linalg.norm(ref) + 1e-8))
                cos = float(np.dot(out, ref) / ((np.linalg.norm(out) * np.linalg.norm(ref)) + 1e-8))
                raw_used = int(got["raw_tokens_used"])
                lat_used = int(got["latent_tokens_used"])
                # Count latent tokens as cheaper than raw tokens but not free.
                eff = raw_used + int(math.ceil(0.25 * lat_used))
                rows.append(Row(
                    seed=seed,
                    scenario=scenario,
                    n_chunks=n_chunks,
                    chunk_size=chunk_size,
                    policy=policy,
                    target_chunk_hit=1 if int(world["target_chunk"]) in set(got["selected_chunks"]) or policy == "full_raw_oracle" else 0,
                    output_rel_error=err,
                    output_cosine=cos,
                    raw_tokens_used=raw_used,
                    latent_tokens_used=lat_used,
                    effective_token_budget=eff,
                    compression_ratio_vs_full_raw=float(eff / full_tokens),
                ))
    return rows


def summarize(rows: List[Row]) -> Dict[str, object]:
    by: Dict[str, Dict[str, List[float]]] = {}
    for r in rows:
        by.setdefault(r.scenario, {}).setdefault(r.policy, []).append(r.output_rel_error)
    winners: Dict[str, str] = {}
    practical: Dict[str, str] = {}
    counts: Dict[str, int] = {}
    pcounts: Dict[str, int] = {}
    for scenario, pols in by.items():
        means = {p: float(np.mean(vals)) for p, vals in pols.items()}
        w = min(means, key=means.get); winners[scenario] = w; counts[w] = counts.get(w, 0) + 1
        means2 = {p: m for p, m in means.items() if p not in {"full_raw_oracle", "oracle_expand_chunk"}}
        pw = min(means2, key=means2.get); practical[scenario] = pw; pcounts[pw] = pcounts.get(pw, 0) + 1
    return {
        "row_count": len(rows),
        "primary_metric": {"name": "output_rel_error", "direction": "lower_is_better", "winner_field": "winners_excluding_oracle"},
        "winners": winners,
        "winner_counts": counts,
        "winners_excluding_oracle": practical,
        "winner_counts_excluding_oracle": pcounts,
        "interpretation": "If compressed-then-expand beats compressed-only, latent context should be tested as a router/skim layer rather than as a full replacement for raw evidence.",
    }


def write(rows: List[Row], out_json: Path, out_csv: Path) -> None:
    payload = {
        "project": "CloudtainerML",
        "revision": "rev0009",
        "probe": "latent_context_compression",
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
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--n-chunks", type=int, default=32)
    p.add_argument("--chunk-size", type=int, default=16)
    p.add_argument("--dim", type=int, default=48)
    p.add_argument("--out-json", type=Path, default=Path("artifacts/probe-results/REV0009_LATENT_CONTEXT_COMPRESSION_SMOKE.json"))
    p.add_argument("--out-csv", type=Path, default=Path("artifacts/probe-results/REV0009_LATENT_CONTEXT_COMPRESSION_SMOKE.csv"))
    args = p.parse_args()
    rows = run(args.seeds, args.n_chunks, args.chunk_size, args.dim)
    write(rows, args.out_json, args.out_csv)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
