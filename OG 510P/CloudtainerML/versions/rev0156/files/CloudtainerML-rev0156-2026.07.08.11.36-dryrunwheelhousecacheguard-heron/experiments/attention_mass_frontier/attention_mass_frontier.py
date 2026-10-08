#!/usr/bin/env python3
"""rev0044 sparse-attention mass/output frontier.

This probe turns the rev0043 one-row-per-compiler benchmark into a frontier:
for the same QK/softmax/V rows, how many value reads are required to retain
80/90/95/98% dense attention mass, and where do fixed Top-K budgets fail?

It is intentionally a bound/diagnostic, not a deployable compiler: Top-p/min-k
uses full score order. Its value is deciding whether a sparse win is even
plausible for a regime before kernel work starts.
"""
from __future__ import annotations

import hashlib
import json
import platform
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0044"}
REV = META.get("revision", "rev0044")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_ATTENTION_MASS_FRONTIER.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    compiler_points_for_row,
    effective_support,
    min_k_for_mass,
    stable_softmax,
    topk_indices,
)
from experiments.attention_row_compiler_benchmark.attention_row_compiler_benchmark import (  # noqa: E402
    BLOCK,
    D,
    DV,
    K,
    N,
    REGIMES,
    SEEDS,
    STEPS,
    make_stream,
)

MASS_TARGETS = (0.80, 0.90, 0.95, 0.98)
BUDGETS = (8, 16, 32, 64, 128, 256, 512)


def mass_key(target: float) -> str:
    return f"{target:.2f}".replace(".", "p")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs):
    xs = list(xs)
    return statistics.fmean(xs) if xs else None


def pctl(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[int(q * (len(xs) - 1))]


def summarize(rows: list[dict]) -> dict:
    by_regime: dict[str, dict] = {}
    for regime in REGIMES:
        xs = [r for r in rows if r["regime"] == regime and r["row_kind"] == "mass_frontier"]
        by_regime[regime] = {
            "mean_effective_support": fmean(r["effective_support"] for r in xs),
            "p90_effective_support": pctl([r["effective_support"] for r in xs], 0.90),
            "mean_min_k_for_mass_0p95": fmean(r["min_k_for_mass_0p95"] for r in xs),
            "p90_min_k_for_mass_0p95": pctl([r["min_k_for_mass_0p95"] for r in xs], 0.90),
            "mean_topk32_mass": fmean(r["topk_32_mass"] for r in xs),
            "topk32_pass_rate_mass_0p95": fmean(float(r["topk_32_mass"] >= 0.95) for r in xs),
            "share_min_k_0p95_le_4xK": fmean(float(r["min_k_for_mass_0p95"] <= 4 * K) for r in xs),
            "share_min_k_0p95_le_8xK": fmean(float(r["min_k_for_mass_0p95"] <= 8 * K) for r in xs),
        }
    frontier_rows = [r for r in rows if r["row_kind"] == "compiler_frontier_point"]
    methods = sorted({r["method"] for r in frontier_rows})
    method_summary = {}
    for m in methods:
        xs = [r for r in frontier_rows if r["method"] == m]
        method_summary[m] = {
            "mean_selected_count": fmean(r["selected_count"] for r in xs),
            "mean_mass_retained": fmean(r["mass_retained"] for r in xs),
            "mean_attention_rel_l2_error": fmean(r["attention_rel_l2_error"] for r in xs),
            "mean_output_cosine": fmean(r["output_cosine"] for r in xs),
            "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
            "mean_bytes_touched_est": fmean(r["bytes_touched_est"] for r in xs),
        }
    mass_rows = [r for r in rows if r["row_kind"] == "mass_frontier"]
    return {
        "row_count_mass_frontier": len(mass_rows),
        "row_count_compiler_points": len(frontier_rows),
        "overall": {
            "mean_effective_support": fmean(r["effective_support"] for r in mass_rows),
            "p90_effective_support": pctl([r["effective_support"] for r in mass_rows], 0.90),
            "mean_min_k_for_mass_0p90": fmean(r["min_k_for_mass_0p90"] for r in mass_rows),
            "mean_min_k_for_mass_0p95": fmean(r["min_k_for_mass_0p95"] for r in mass_rows),
            "p90_min_k_for_mass_0p95": pctl([r["min_k_for_mass_0p95"] for r in mass_rows], 0.90),
            "mean_min_k_for_mass_0p98": fmean(r["min_k_for_mass_0p98"] for r in mass_rows),
            "mean_topk32_mass": fmean(r["topk_32_mass"] for r in mass_rows),
            "topk32_pass_rate_mass_0p95": fmean(float(r["topk_32_mass"] >= 0.95) for r in mass_rows),
            "share_min_k_0p95_le_4xK": fmean(float(r["min_k_for_mass_0p95"] <= 4 * K) for r in mass_rows),
            "share_min_k_0p95_le_8xK": fmean(float(r["min_k_for_mass_0p95"] <= 8 * K) for r in mass_rows),
        },
        "by_regime": by_regime,
        "method_summary": method_summary,
    }


def run() -> dict:
    rows: list[dict] = []
    for regime in REGIMES:
        for seed in SEEDS:
            for row in make_stream(regime, seed):
                probs = stable_softmax(row.scores)
                topk_mass = {}
                for b in BUDGETS:
                    topk_mass[f"topk_{b}_mass"] = float(np.sum(probs[topk_indices(row.scores, min(b, N))]))
                mass_row = {
                    "row_kind": "mass_frontier",
                    "regime": regime,
                    "seed": seed,
                    "step": row.step,
                    "N": N,
                    "D": D,
                    "DV": DV,
                    "K": K,
                    "block": BLOCK,
                    "dense_entropy": -float(np.sum(probs * np.log(np.maximum(probs, 1e-30)))),
                    "effective_support": effective_support(probs),
                    "max_probability": float(np.max(probs)),
                    "top1_to_top32_mass_ratio": float(np.max(probs) / max(1e-12, topk_mass["topk_32_mass"])),
                    **topk_mass,
                }
                for target in MASS_TARGETS:
                    key = mass_key(target)
                    mass_row[f"min_k_for_mass_{key}"] = int(min_k_for_mass(probs, target))
                mass_row["sparse_potential_0p95_under_4xK"] = bool(mass_row["min_k_for_mass_0p95"] <= 4 * K)
                mass_row["sparse_potential_0p95_under_8xK"] = bool(mass_row["min_k_for_mass_0p95"] <= 8 * K)
                rows.append(mass_row)
                for point in compiler_points_for_row(row.scores, row.values, D, budgets=BUDGETS, p_targets=MASS_TARGETS):
                    point.update({
                        "row_kind": "compiler_frontier_point",
                        "regime": regime,
                        "seed": seed,
                        "step": row.step,
                        "N": N,
                        "D": D,
                        "DV": DV,
                        "K": K,
                        "block": BLOCK,
                    })
                    rows.append(point)
    summary = summarize(rows)
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "attention_mass_frontier",
        "kind": "python_attention_frontier_benchmark",
        "evidence_tier": "E2_synthetic_attention_output_frontier",
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_path": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "core_source_path": "experiments/attention_compiler_core/attention_core.py",
            "core_source_sha256": sha256_file(ROOT / "experiments/attention_compiler_core/attention_core.py"),
            "row_generator_source_path": "experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py",
            "row_generator_source_sha256": sha256_file(ROOT / "experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py"),
            "command": "python experiments/attention_mass_frontier/attention_mass_frontier.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "seed_policy": {"seeds": SEEDS, "steps": STEPS, "N": N, "D": D, "DV": DV, "K": K, "mass_targets": MASS_TARGETS, "budgets": BUDGETS},
        },
        "summary": {
            "primary_metric": {"name": "min_k_for_mass_0p95", "direction": "lower_is_better"},
            "guard_fields": [
                "effective_support", "min_k_for_mass_0p90", "min_k_for_mass_0p95", "min_k_for_mass_0p98",
                "topk_32_mass", "sparse_potential_0p95_under_4xK", "selected_count", "mass_retained",
                "attention_rel_l2_error", "output_cosine", "value_reads", "qk_dot_products", "bytes_touched_est", "passes_quality_bar",
            ],
            **summary,
            "interpretation": "This is a frontier/veto probe: if min_k_for_mass_0p95 is hundreds of tokens, a K=32 exact selector is structurally unable to preserve dense attention output no matter how clever the Top-K certifier is.",
        },
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT.relative_to(ROOT)),
        "mass_rows": payload["summary"]["row_count_mass_frontier"],
        "compiler_points": payload["summary"]["row_count_compiler_points"],
        "overall": payload["summary"]["overall"],
    }, indent=2))


if __name__ == "__main__":
    main()
