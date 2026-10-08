#!/usr/bin/env python3
"""
Entmax Support-Recovery Probe
=============================

A tiny page-selection simulator inspired by EntmaxKV (arXiv:2605.21649).
Softmax has dense tails, so sparse decoding is always approximate.  Sparsemax /
entmax-style attention has exact zeros, so sparse decoding can be exact if the
selected pages contain the support.

This probe uses sparsemax as the simplest exact-zero attention family and compares
candidate-selection policies by support coverage, dropped probability mass, and
output error.  It is deliberately tensor-only and NumPy-only.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

EPS = 1e-9


@dataclass
class EntmaxSupportResult:
    seed: int
    n_tokens: int
    page_size: int
    n_pages_selected: int
    sharpness: float
    distractor_strength: float
    method: str
    support_size: int
    selected_tokens: int
    support_coverage: float
    dropped_mass: float
    output_l2_error: float
    exact_if_support_recovered: int


def softmax(scores: np.ndarray) -> np.ndarray:
    y = scores - np.max(scores)
    e = np.exp(y)
    return e / np.maximum(e.sum(), EPS)


def sparsemax(scores: np.ndarray) -> np.ndarray:
    """Sparsemax projection onto simplex (Martins & Astudillo, 2016)."""
    z = scores - np.mean(scores)
    zs = np.sort(z)[::-1]
    cssv = np.cumsum(zs)
    k = np.arange(1, len(z) + 1)
    cond = 1 + k * zs > cssv
    if not np.any(cond):
        tau = 0.0
    else:
        k_z = int(k[cond][-1])
        tau = (cssv[cond][-1] - 1.0) / k_z
    return np.maximum(z - tau, 0.0)


def make_scores(seed: int, n_tokens: int, page_size: int, sharpness: float, distractor_strength: float) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_pages = n_tokens // page_size
    # Page-level latent relevance plus token-level noise.  A few target pages have
    # tight high scores; distractor pages have high maxima but weaker total support.
    page_signal = rng.normal(scale=0.25, size=n_pages)
    target_pages = rng.choice(n_pages, size=max(1, n_pages // 12), replace=False)
    distractor_pages = rng.choice([p for p in range(n_pages) if p not in set(target_pages)], size=max(1, n_pages // 10), replace=False)
    page_signal[target_pages] += sharpness
    page_signal[distractor_pages] += distractor_strength
    scores = np.repeat(page_signal, page_size) + rng.normal(scale=0.75, size=n_tokens)
    # Create isolated high tokens in distractor pages so page-max can be fooled.
    for p in distractor_pages:
        idx = p * page_size + int(rng.integers(0, page_size))
        scores[idx] += 1.5 * distractor_strength
    values = rng.normal(size=(n_tokens, 24))
    values /= np.maximum(np.linalg.norm(values, axis=1, keepdims=True), EPS)
    return scores, values


def select_tokens(scores: np.ndarray, page_size: int, n_pages_selected: int, method: str, full_probs: np.ndarray) -> np.ndarray:
    n_tokens = len(scores)
    n_pages = n_tokens // page_size
    page_scores = scores.reshape(n_pages, page_size)
    page_probs = full_probs.reshape(n_pages, page_size)
    if method == "oracle_support_pages":
        page_metric = (page_probs > 0).sum(axis=1)
    elif method == "page_max_score":
        page_metric = page_scores.max(axis=1)
    elif method == "page_mean_score":
        page_metric = page_scores.mean(axis=1)
    elif method == "page_lse_score":
        m = page_scores.max(axis=1, keepdims=True)
        page_metric = (m[:, 0] + np.log(np.exp(page_scores - m).sum(axis=1)))
    elif method == "page_mass_proxy":
        # Cheap Gaussian-ish threshold proxy: high mean and low dispersion tend to
        # preserve real sparsemax support better than max-only distractors.
        page_metric = page_scores.mean(axis=1) + 0.35 * page_scores.std(axis=1)
    elif method == "token_topk_budget":
        k = n_pages_selected * page_size
        idx = np.argsort(-scores)[:k]
        mask = np.zeros(n_tokens, dtype=bool)
        mask[idx] = True
        return mask
    elif method == "random_pages":
        rng = np.random.default_rng(abs(hash((float(scores[0]), n_pages_selected))) % (2**32))
        chosen = rng.choice(n_pages, size=n_pages_selected, replace=False)
        mask = np.zeros(n_tokens, dtype=bool)
        for p in chosen:
            mask[p * page_size : (p + 1) * page_size] = True
        return mask
    else:
        raise ValueError(method)
    chosen_pages = np.argsort(-page_metric)[:n_pages_selected]
    mask = np.zeros(n_tokens, dtype=bool)
    for p in chosen_pages:
        mask[p * page_size : (p + 1) * page_size] = True
    return mask


def restricted_attention(scores: np.ndarray, mask: np.ndarray) -> np.ndarray:
    restricted = np.full_like(scores, -1e9, dtype=np.float64)
    restricted[mask] = scores[mask]
    return sparsemax(restricted)


def run_trial(seed: int, n_tokens: int, page_size: int, n_pages_selected: int, sharpness: float, distractor_strength: float) -> Iterable[EntmaxSupportResult]:
    scores, values = make_scores(seed, n_tokens, page_size, sharpness, distractor_strength)
    full_probs = sparsemax(scores)
    full_out = full_probs @ values
    support = full_probs > 1e-8
    support_mass = float(full_probs[support].sum())
    methods = [
        "oracle_support_pages",
        "page_max_score",
        "page_mean_score",
        "page_lse_score",
        "page_mass_proxy",
        "token_topk_budget",
        "random_pages",
    ]
    for method in methods:
        mask = select_tokens(scores, page_size, n_pages_selected, method, full_probs)
        coverage = float((support & mask).sum() / max(1, support.sum()))
        dropped = float(full_probs[~mask].sum() / max(support_mass, EPS))
        approx_probs = restricted_attention(scores, mask)
        approx_out = approx_probs @ values
        err = float(np.linalg.norm(approx_out - full_out))
        yield EntmaxSupportResult(
            seed=seed,
            n_tokens=n_tokens,
            page_size=page_size,
            n_pages_selected=n_pages_selected,
            sharpness=float(sharpness),
            distractor_strength=float(distractor_strength),
            method=method,
            support_size=int(support.sum()),
            selected_tokens=int(mask.sum()),
            support_coverage=coverage,
            dropped_mass=dropped,
            output_l2_error=err,
            exact_if_support_recovered=int(dropped < 1e-8),
        )


def summarize(rows: list[EntmaxSupportResult]) -> Dict[str, object]:
    by_method = {}
    for method in sorted({r.method for r in rows}):
        sub = [r for r in rows if r.method == method]
        by_method[method] = {
            "mean_support_coverage": float(np.mean([r.support_coverage for r in sub])),
            "mean_dropped_mass": float(np.mean([r.dropped_mass for r in sub])),
            "mean_output_l2_error": float(np.mean([r.output_l2_error for r in sub])),
            "exact_rate": float(np.mean([r.exact_if_support_recovered for r in sub])),
        }
    return {
        "probe": "entmax_support_recovery",
        "rows": len(rows),
        "interpretation": "Sparse attention turns cache selection into support recovery. Page policies should be judged by dropped mass, not just top-score recall.",
        "by_method": by_method,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, default=Path("artifacts/probe-results"))
    ap.add_argument("--prefix", type=str, default="REV0005_ENTMAX_SUPPORT_SMOKE")
    ap.add_argument("--seeds", type=int, default=48)
    ap.add_argument("--n-tokens", type=int, default=512)
    ap.add_argument("--page-size", type=int, default=16)
    ap.add_argument("--pages-selected", type=str, default="2,4,8")
    ap.add_argument("--sharpness", type=str, default="1.5,2.5")
    ap.add_argument("--distractor-strength", type=str, default="0.5,1.5")
    args = ap.parse_args()

    rows: list[EntmaxSupportResult] = []
    for seed in range(args.seeds):
        for k_pages in [int(x) for x in args.pages_selected.split(",") if x]:
            for sharp in [float(x) for x in args.sharpness.split(",") if x]:
                for distract in [float(x) for x in args.distractor_strength.split(",") if x]:
                    rows.extend(run_trial(seed, args.n_tokens, args.page_size, k_pages, sharp, distract))

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / f"{args.prefix}.csv"
    json_path = args.outdir / f"{args.prefix}.json"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    summary = summarize(rows)
    summary["csv"] = str(csv_path)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
