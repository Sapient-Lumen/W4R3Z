#!/usr/bin/env python3
"""rev0045 mass-certified sparse-attention compiler probe.

rev0044 proved that exact Top-K is not the same as attention-output quality.
This probe asks the next riskier question: can a deployable selector preserve a
specified amount of dense attention mass without reading most values and without
consulting dense outputs?

The tested compilers may use QK scores and score-only softmax mass certificates.
They may not inspect V vectors or dense attention outputs during selection.
The ordered Top-p row is kept as an upper-bound/reference because it uses a full
score sort.  The new candidates are score-threshold/grid, score-histogram, and
block-local widening selectors.
"""
from __future__ import annotations

import hashlib
import json
import platform
import statistics
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0045"}
REV = META.get("revision", "rev0045")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_MASS_CERTIFIED_ATTENTION_COMPILER.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    mass_aware_compiler_points_for_row,
    stable_softmax,
)
from experiments.attention_row_compiler_benchmark.attention_row_compiler_benchmark import (  # noqa: E402
    BLOCK as SYN_BLOCK,
    D as SYN_D,
    DV as SYN_DV,
    K as SYN_K,
    N as SYN_N,
    REGIMES,
    SEEDS,
    STEPS,
    make_stream,
)
from experiments.tiny_transformer_attention_traces.tiny_transformer_attention_trace_probe import (  # noqa: E402
    D_HEAD as TRACE_D_HEAD,
    HEADS,
    K as TRACE_K,
    LAYERS,
    SEED as TRACE_SEED,
    SEQ,
    TRACE_BATCH,
    TRACE_BATCHES,
    make_batch,
    train_model,
)

TARGET_MASS = 0.95
SYN_HIST_BINS = 32
TRACE_HIST_BINS = 16
TRACE_BLOCK = 16


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs: Iterable[float]) -> float | None:
    xs = list(xs)
    return statistics.fmean(xs) if xs else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    xs = sorted(xs)
    if not xs:
        return None
    return float(xs[int(q * (len(xs) - 1))])


def summarize_rows(rows: list[dict]) -> dict:
    by_dataset: dict[str, dict] = {}
    for dataset in sorted({r["dataset"] for r in rows}):
        ds = [r for r in rows if r["dataset"] == dataset]
        compilers = sorted({r["compiler"] for r in ds})
        by_compiler = {}
        for compiler in compilers:
            xs = [r for r in ds if r["compiler"] == compiler]
            by_compiler[compiler] = {
                "row_count": len(xs),
                "mean_selected_count": fmean(float(r["selected_count"]) for r in xs),
                "p90_selected_count": pctl((float(r["selected_count"]) for r in xs), 0.90),
                "mean_value_read_fraction": fmean(float(r["value_read_fraction"]) for r in xs),
                "mean_mass_retained": fmean(float(r["mass_retained"]) for r in xs),
                "mean_attention_rel_l2_error": fmean(float(r["attention_rel_l2_error"]) for r in xs),
                "mean_output_cosine": fmean(float(r["output_cosine"]) for r in xs),
                "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
                "mass_certified_without_values_rate": fmean(float(r["mass_certified_without_values"]) for r in xs),
                "selection_uses_values_rate": fmean(float(r["selection_uses_values"]) for r in xs),
                "selection_uses_dense_output_rate": fmean(float(r["selection_uses_dense_output"]) for r in xs),
                "sort_free_selector_rate": fmean(float(r["sort_free_selector"]) for r in xs),
                "fallback_rate": fmean(float(r.get("fallback") is not None) for r in xs),
                "mean_certificate_error_abs": fmean(float(r["certificate_error_abs"] or 0.0) for r in xs),
                "mean_bytes_touched_est": fmean(float(r["bytes_touched_est"]) for r in xs),
                "mean_selector_passes": fmean(float(r["selector_passes"]) for r in xs),
                "mean_score_read_fraction": fmean(float(r["score_read_fraction"]) for r in xs),
                "mean_topk_hit_rate": fmean(float(r["topk_hit_rate"]) for r in xs),
            }
        by_dataset[dataset] = {
            "row_count": len(ds),
            "compiler_summary": by_compiler,
        }
    return by_dataset


def compiler_rankings(rows: list[dict], dataset: str) -> list[dict]:
    ds = [r for r in rows if r["dataset"] == dataset]
    compilers = sorted({r["compiler"] for r in ds})
    out = []
    for c in compilers:
        xs = [r for r in ds if r["compiler"] == c]
        out.append({
            "compiler": c,
            "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
            "mean_selected_count": fmean(float(r["selected_count"]) for r in xs),
            "mean_mass_retained": fmean(float(r["mass_retained"]) for r in xs),
            "mean_output_cosine": fmean(float(r["output_cosine"]) for r in xs),
            "sort_free_selector_rate": fmean(float(r["sort_free_selector"]) for r in xs),
            "mass_certified_without_values_rate": fmean(float(r["mass_certified_without_values"]) for r in xs),
        })
    return sorted(out, key=lambda x: (-(x["quality_bar_rate"] or 0.0), x["mean_selected_count"] or 10**9, x["compiler"]))


def collect_synthetic_rows() -> list[dict]:
    rows: list[dict] = []
    for regime in REGIMES:
        for seed in SEEDS:
            for row in make_stream(regime, seed):
                points = mass_aware_compiler_points_for_row(
                    row.scores,
                    row.values,
                    d_head=SYN_D,
                    fixed_k=SYN_K,
                    target_mass=TARGET_MASS,
                    block=SYN_BLOCK,
                    hist_bins=SYN_HIST_BINS,
                    hist_max_delta=16.0,
                )
                probs = stable_softmax(row.scores)
                for p in points:
                    p.update({
                        "row_kind": "mass_certified_synthetic_row",
                        "dataset": "synthetic_attention_rows",
                        "regime": regime,
                        "seed": int(seed),
                        "step": int(row.step),
                        "N": SYN_N,
                        "D": SYN_D,
                        "DV": SYN_DV,
                        "K": SYN_K,
                        "block": SYN_BLOCK,
                        "target_mass_policy": TARGET_MASS,
                        "max_probability": float(np.max(probs)),
                    })
                    rows.append(p)
    return rows


def collect_tiny_trace_rows(train_metrics: dict, model) -> list[dict]:
    rows: list[dict] = []
    with torch.no_grad():
        for tb in range(TRACE_BATCHES):
            x, y, target_pos = make_batch(TRACE_BATCH, np.random.default_rng(TRACE_SEED + 2500 + tb))
            logits, traces = model(x, capture=True)
            pred = logits.argmax(dim=-1).cpu().numpy()
            y_np = y.cpu().numpy()
            batch_acc = float(np.mean(pred == y_np))
            for layer_id, tr in enumerate(traces):
                layer_logits = tr["logits"].numpy()
                layer_values = tr["values"].numpy()
                for b in range(TRACE_BATCH):
                    for h in range(HEADS):
                        scores = layer_logits[b, h, -1].astype(np.float64)
                        values = layer_values[b, h].astype(np.float64)
                        probs = stable_softmax(scores)
                        points = mass_aware_compiler_points_for_row(
                            scores,
                            values,
                            d_head=TRACE_D_HEAD,
                            fixed_k=TRACE_K,
                            target_mass=TARGET_MASS,
                            block=TRACE_BLOCK,
                            hist_bins=TRACE_HIST_BINS,
                            hist_max_delta=16.0,
                        )
                        needle = int(target_pos[b])
                        for p in points:
                            sel_set = set()  # selected indices are not stored; infer only needle via mass certificate row is enough? no
                            # Reconstruct selected needle status for diagnostics from compiler-specific sparse row is not available here.
                            # Instead expose the needle probability and model correctness; value/output metrics remain the primary guard.
                            p.update({
                                "row_kind": "mass_certified_tiny_trace_row",
                                "dataset": "tiny_trained_transformer_trace_rows",
                                "trace_batch": int(tb),
                                "example": int(b),
                                "layer": int(layer_id),
                                "head": int(h),
                                "N": SEQ,
                                "D": TRACE_D_HEAD,
                                "DV": TRACE_D_HEAD,
                                "K": TRACE_K,
                                "block": TRACE_BLOCK,
                                "target_mass_policy": TARGET_MASS,
                                "needle_position": needle,
                                "needle_probability": float(probs[needle]),
                                "max_probability": float(np.max(probs)),
                                "model_correct": bool(pred[b] == int(y_np[b])),
                                "model_accuracy_snapshot": batch_acc,
                                "training_eval_accuracy": train_metrics.get("eval_accuracy"),
                            })
                            rows.append(p)
    return rows


def run() -> dict:
    torch.set_num_threads(1)
    synthetic_rows = collect_synthetic_rows()
    model, train_metrics = train_model()
    trace_rows = collect_tiny_trace_rows(train_metrics, model)
    rows = synthetic_rows + trace_rows
    by_dataset = summarize_rows(rows)
    mass_certified_labels = [
        "mass_delta_grid_0p95",
        "mass_histogram_0p95_bins32",
        "mass_histogram_0p95_bins16",
        "block_topb_certified_0p95",
    ]
    certified_rows = [r for r in rows if r["compiler"] in mass_certified_labels or r["compiler"].startswith("mass_") or r["compiler"].startswith("block_topb")]
    oracle_leakage = [r for r in certified_rows if r.get("selection_uses_values") or r.get("selection_uses_dense_output") or not r.get("mass_certified_without_values")]
    summary = {
        "primary_metric": {"name": "quality_bar_rate_at_target_mass_0p95", "direction": "higher_is_better_under_low_value_reads"},
        "target_mass": TARGET_MASS,
        "selection_contract": "selectors may use QK scores and score-only mass certificates; selectors may not inspect V vectors or dense attention outputs; value reads are counted after selection",
        "guard_fields": [
            "selected_count", "value_reads", "value_read_fraction", "mass_retained", "certified_mass_from_scores",
            "certificate_error_abs", "attention_rel_l2_error", "attention_l2_error", "output_cosine",
            "qk_dot_products", "score_reads", "score_read_fraction", "selector_passes", "threshold_evals",
            "bytes_touched_est", "sort_free_selector", "selection_uses_values", "selection_uses_dense_output",
            "mass_certificate", "mass_certified_without_values", "fallback", "passes_quality_bar", "topk_hit_rate",
        ],
        "train_metrics": train_metrics,
        "dataset_summary": by_dataset,
        "rankings": {
            "synthetic_attention_rows": compiler_rankings(rows, "synthetic_attention_rows"),
            "tiny_trained_transformer_trace_rows": compiler_rankings(rows, "tiny_trained_transformer_trace_rows"),
        },
        "oracle_leakage_rows": len(oracle_leakage),
        "mass_certified_candidate_rows": len(certified_rows),
        "mass_certified_candidate_oracle_free": len(oracle_leakage) == 0,
        "interpretation": "rev0045 adds deployable score-only mass-certified selectors. Ordered Top-p remains the value-read bound; histogram/delta/block compilers test how much of that quality can be retained without a global Top-p sort and without any value/output oracle.",
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "mass_certified_attention_compiler",
        "kind": "python_mass_certified_attention_compiler_benchmark",
        "evidence_tier": "E2p5_mass_certified_attention_compiler_on_synthetic_and_tiny_traces",
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_path": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "core_source_path": "experiments/attention_compiler_core/attention_core.py",
            "core_source_sha256": sha256_file(ROOT / "experiments/attention_compiler_core/attention_core.py"),
            "row_generator_source_path": "experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py",
            "row_generator_source_sha256": sha256_file(ROOT / "experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py"),
            "trace_source_path": "experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py",
            "trace_source_sha256": sha256_file(ROOT / "experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py"),
            "command": "python experiments/mass_certified_attention_compiler/mass_certified_attention_compiler.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "seed_policy": {
                "synthetic_seeds": SEEDS,
                "synthetic_steps": STEPS,
                "synthetic_regimes": REGIMES,
                "trace_seed": TRACE_SEED,
                "trace_batches": TRACE_BATCHES,
                "trace_batch": TRACE_BATCH,
                "target_mass": TARGET_MASS,
                "synthetic_hist_bins": SYN_HIST_BINS,
                "trace_hist_bins": TRACE_HIST_BINS,
            },
        },
        "summary": summary,
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    compact = {
        "artifact": str(OUT.relative_to(ROOT)),
        "target_mass": TARGET_MASS,
        "train_metrics": payload["summary"]["train_metrics"],
        "synthetic_top_ranked": payload["summary"]["rankings"]["synthetic_attention_rows"][:4],
        "trace_top_ranked": payload["summary"]["rankings"]["tiny_trained_transformer_trace_rows"][:4],
        "oracle_leakage_rows": payload["summary"]["oracle_leakage_rows"],
    }
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
