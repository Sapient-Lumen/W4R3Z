#!/usr/bin/env python3
"""rev0046 value-norm stress probe for sparse attention compilers.

rev0045 made score-only mass certificates honest: selectors preserved a target
amount of attention probability without reading V or dense outputs.  This probe
checks the next riskiest assumption: mass retained is only an output-quality
proxy when value vectors are not adversarially large in the omitted tail.

The new metadata-guarded selector is allowed to read per-token value norms, not
value vectors or dense outputs.  That is a stricter and more deployable claim
than using V during selection, but it exposes an explicit metadata cost and
sidecar requirement.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0046"}
REV = META.get("revision", "rev0046")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_VALUE_NORM_GUARDED_ATTENTION_STRESS.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_VALUE_NORM_STRESS_RUN_MANIFEST.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    bytes_touched_est,
    evaluate_selection_result,
    exact_topk_selection,
    full_dense_selection,
    histogram_mass_selection,
    ordered_topp_selection,
    stable_softmax,
    value_norm_exception_mass_selection,
    value_norm_guarded_histogram_selection,
)

SEEDS = [9201, 9202, 9203, 9204]
ROWS_PER_REGIME = 18
N = 512
D_HEAD = 64
D_VALUE = 64
FIXED_K = 32
TARGET_MASS = 0.95
HIST_BINS = 32
VALUE_BOUND = 0.15
EXCEPTION_CAP = 48
REGIMES = [
    "bounded_peaked",
    "broad_bounded",
    "single_tail_value_spike",
    "multi_tail_value_spikes",
    "plateau_with_value_outlier",
]


@dataclass(frozen=True)
class StressRow:
    regime: str
    seed: int
    row: int
    scores: np.ndarray
    values: np.ndarray
    outlier_indices: tuple[int, ...]
    expected_failure_mode: str


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


def unit_random_values(rng: np.random.Generator, n: int = N, d: int = D_VALUE) -> np.ndarray:
    v = rng.normal(0.0, 1.0, size=(n, d)).astype(np.float64)
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.maximum(norms, 1e-12)


def peaked_scores(rng: np.random.Generator, high_count: int = 24) -> np.ndarray:
    scores = rng.normal(0.0, 0.08, size=N).astype(np.float64)
    high = rng.choice(N, size=high_count, replace=False)
    scores[high] = 6.0 + rng.normal(0.0, 0.15, size=high_count)
    return scores


def make_row(regime: str, seed: int, row: int) -> StressRow:
    rng = np.random.default_rng(seed * 1009 + row * 9176 + hash(regime) % 100000)
    values = unit_random_values(rng)
    outliers: list[int] = []
    expected = "bounded values; mass should be a reasonable output proxy"

    if regime == "bounded_peaked":
        scores = peaked_scores(rng, high_count=24)
    elif regime == "broad_bounded":
        scores = rng.normal(0.0, 0.22, size=N).astype(np.float64)
        expected = "broad attention; mass target is honest but expensive"
    elif regime == "single_tail_value_spike":
        scores = peaked_scores(rng, high_count=24)
        probs = stable_softmax(scores)
        top = set(np.argsort(-scores)[:64].tolist())
        tail_candidates = [i for i in np.argsort(probs)[: N // 2] if int(i) not in top]
        idx = int(tail_candidates[row % len(tail_candidates)])
        scores[idx] = min(scores[idx], 0.0)
        direction = np.zeros(D_VALUE, dtype=np.float64)
        direction[0] = 1.0
        # Probability is tiny but norm is large enough that p_i ||V_i|| matters.
        values[idx] = direction * (4200.0 + 200.0 * (row % 3))
        outliers = [idx]
        expected = "mass-only selectors can retain >=0.95 probability and still drop a high-norm tail value"
    elif regime == "multi_tail_value_spikes":
        scores = peaked_scores(rng, high_count=28)
        probs = stable_softmax(scores)
        top = set(np.argsort(-scores)[:80].tolist())
        candidates = [int(i) for i in np.argsort(probs)[: N // 2] if int(i) not in top]
        chosen = candidates[:4]
        for j, idx in enumerate(chosen):
            basis = np.zeros(D_VALUE, dtype=np.float64)
            basis[j % D_VALUE] = 1.0
            scores[idx] = min(scores[idx], -0.2 - 0.05 * j)
            values[idx] = basis * (1700.0 + 120.0 * j)
        outliers = chosen
        expected = "several low-probability value spikes require discontiguous metadata exceptions"
    elif regime == "plateau_with_value_outlier":
        scores = rng.normal(0.0, 0.03, size=N).astype(np.float64)
        plateau = rng.choice(N, size=N // 3, replace=False)
        scores[plateau] += 1.1 + rng.normal(0.0, 0.02, size=len(plateau))
        low = [i for i in range(N) if i not in set(plateau)]
        idx = int(low[row % len(low)])
        direction = np.zeros(D_VALUE, dtype=np.float64)
        direction[3] = 1.0
        values[idx] = direction * 640.0
        outliers = [idx]
        expected = "plateau scores cause wide mass selection; a value outlier still demands a guard"
    else:
        raise ValueError(regime)
    return StressRow(regime, seed, row, scores, values, tuple(outliers), expected)


def selected_contains_outliers(selection, outliers: tuple[int, ...]) -> float | None:
    if not outliers:
        return None
    selected = set(map(int, selection.selected))
    return float(sum(1 for i in outliers if i in selected) / len(outliers))


def evaluate_row(sr: StressRow) -> list[dict]:
    norms = np.linalg.norm(sr.values, axis=1)
    selectors = [
        ("full_dense", full_dense_selection(sr.scores)),
        (f"exact_topk_{FIXED_K}", exact_topk_selection(sr.scores, FIXED_K)),
        (f"ordered_topp_{str(TARGET_MASS).replace('.', 'p')}_bound", ordered_topp_selection(sr.scores, TARGET_MASS)),
        (f"mass_histogram_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}", histogram_mass_selection(sr.scores, TARGET_MASS, bins=HIST_BINS, max_delta=16.0)),
        (f"value_norm_guarded_histogram_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}", value_norm_guarded_histogram_selection(sr.scores, norms, TARGET_MASS, bins=HIST_BINS, max_delta=16.0, absolute_error_bound=VALUE_BOUND)),
        (f"value_norm_exception_mass_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}", value_norm_exception_mass_selection(sr.scores, norms, TARGET_MASS, bins=HIST_BINS, max_delta=16.0, absolute_error_bound=VALUE_BOUND, exception_cap=EXCEPTION_CAP)),
    ]
    probs = stable_softmax(sr.scores)
    out: list[dict] = []
    for label, sel in selectors:
        m = evaluate_selection_result(sr.scores, sr.values, sel, d_head=D_HEAD, method_label=label, target_mass=TARGET_MASS)
        m.update({
            "row_id": f"{sr.regime}:{sr.seed}:{sr.row}",
            "row_kind": "value_norm_guarded_attention_stress_row",
            "dataset": "value_norm_guarded_stress",
            "regime": sr.regime,
            "seed": int(sr.seed),
            "row": int(sr.row),
            "N": N,
            "D": D_HEAD,
            "DV": D_VALUE,
            "K": FIXED_K,
            "target_mass_policy": TARGET_MASS,
            "value_norm_error_bound_target": VALUE_BOUND,
            "exception_cap": EXCEPTION_CAP,
            "outlier_count": int(len(sr.outlier_indices)),
            "outlier_indices": list(map(int, sr.outlier_indices[:8])),
            "outlier_probability_mass": float(sum(probs[i] for i in sr.outlier_indices)),
            "outlier_weighted_value_norm": float(sum(probs[i] * norms[i] for i in sr.outlier_indices)),
            "outlier_recall": selected_contains_outliers(sel, sr.outlier_indices),
            "expected_failure_mode": sr.expected_failure_mode,
            "value_read_fraction": float(m["value_reads"] / N),
            "score_read_fraction": float(m["score_reads"] / N),
            "metadata_read_fraction": float(m.get("metadata_reads", 0) / N),
            "selection_contract_class": "score_only" if not m.get("selection_uses_value_norms") else "score_plus_value_norm_metadata",
        })
        # Include value-norm metadata bytes in a separate estimate rather than
        # hiding them inside value reads; these are scalar sidecar reads, not V.
        m["bytes_touched_plus_norm_metadata_est"] = int(m["bytes_touched_est"] + 4 * int(m.get("metadata_reads", 0)))
        out.append(m)
    return out


def summarize(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for regime in sorted({r["regime"] for r in rows}):
        rs = [r for r in rows if r["regime"] == regime]
        compilers = sorted({r["compiler"] for r in rs})
        out[regime] = {"row_count": len({r["row_id"] for r in rs}), "compiler_summary": {}}
        for c in compilers:
            xs = [r for r in rs if r["compiler"] == c]
            out[regime]["compiler_summary"][c] = {
                "row_count": len(xs),
                "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
                "mean_selected_count": fmean(float(r["selected_count"]) for r in xs),
                "p90_selected_count": pctl((float(r["selected_count"]) for r in xs), 0.90),
                "mean_value_read_fraction": fmean(float(r["value_read_fraction"]) for r in xs),
                "mean_metadata_read_fraction": fmean(float(r["metadata_read_fraction"]) for r in xs),
                "mean_mass_retained": fmean(float(r["mass_retained"]) for r in xs),
                "mean_attention_rel_l2_error": fmean(float(r["attention_rel_l2_error"]) for r in xs),
                "mean_output_cosine": fmean(float(r["output_cosine"]) for r in xs),
                "mean_value_norm_bound": fmean(float(r.get("value_error_bound_from_scores_and_norms") or 0.0) for r in xs),
                "value_norm_bound_pass_rate": fmean(float(r.get("passes_value_norm_bound", False)) for r in xs),
                "outlier_recall_rate": fmean(float(r["outlier_recall"]) for r in xs if r["outlier_recall"] is not None),
                "selection_uses_values_rate": fmean(float(r["selection_uses_values"]) for r in xs),
                "selection_uses_dense_output_rate": fmean(float(r["selection_uses_dense_output"]) for r in xs),
                "selection_uses_value_norms_rate": fmean(float(r["selection_uses_value_norms"]) for r in xs),
                "mean_bytes_touched_plus_norm_metadata_est": fmean(float(r["bytes_touched_plus_norm_metadata_est"]) for r in xs),
                "fallback_rate": fmean(float(r.get("fallback") is not None) for r in xs),
            }
    return out


def compare_failure_repairs(rows: list[dict]) -> dict:
    by_id: dict[str, dict[str, dict]] = {}
    for r in rows:
        by_id.setdefault(r["row_id"], {})[r["compiler"]] = r
    mass_label = f"mass_histogram_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}"
    guard_label = f"value_norm_guarded_histogram_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}"
    exc_label = f"value_norm_exception_mass_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}"
    mass_only_failures = []
    exception_repairs = []
    guard_repairs = []
    for row_id, comp in by_id.items():
        mass = comp.get(mass_label)
        if not mass:
            continue
        if mass["mass_retained"] >= TARGET_MASS and not mass["passes_quality_bar"]:
            mass_only_failures.append(row_id)
            exc = comp.get(exc_label)
            guard = comp.get(guard_label)
            if exc and exc["passes_quality_bar"]:
                exception_repairs.append(row_id)
            if guard and guard["passes_quality_bar"]:
                guard_repairs.append(row_id)
    return {
        "mass_only_rows_with_target_mass_but_bad_output": len(mass_only_failures),
        "value_norm_exception_repairs": len(exception_repairs),
        "value_norm_guarded_histogram_repairs": len(guard_repairs),
        "mass_only_failure_row_examples": mass_only_failures[:8],
        "repair_rate_exception_given_mass_failure": len(exception_repairs) / max(1, len(mass_only_failures)),
        "repair_rate_guarded_histogram_given_mass_failure": len(guard_repairs) / max(1, len(mass_only_failures)),
    }


def run() -> dict:
    rows: list[dict] = []
    for regime in REGIMES:
        for seed in SEEDS:
            for row in range(ROWS_PER_REGIME):
                rows.extend(evaluate_row(make_row(regime, seed, row)))
    regime_summary = summarize(rows)
    repairs = compare_failure_repairs(rows)
    leakage = [r for r in rows if r.get("selection_uses_values") or r.get("selection_uses_dense_output")]
    metadata_rows = [r for r in rows if r.get("selection_uses_value_norms")]
    summary = {
        "primary_metric": {
            "name": "repair_rate_exception_given_mass_failure",
            "direction": "higher_is_better_under_metadata_read_budget",
        },
        "target_mass": TARGET_MASS,
        "value_norm_error_bound_target": VALUE_BOUND,
        "selection_contract": "mass-only selectors may use scores only; value-norm guarded selectors may use scores plus scalar value-norm metadata, never value vectors or dense outputs",
        "guard_fields": [
            "mass_retained", "attention_rel_l2_error", "output_cosine", "passes_quality_bar",
            "selection_uses_values", "selection_uses_dense_output", "selection_uses_value_norms",
            "value_norm_reads", "metadata_reads", "metadata_read_fraction", "value_error_bound_from_scores_and_norms",
            "passes_value_norm_bound", "outlier_weighted_value_norm", "outlier_recall", "bytes_touched_plus_norm_metadata_est",
        ],
        "regime_summary": regime_summary,
        "failure_repair_summary": repairs,
        "selection_oracle_leakage_rows": len(leakage),
        "metadata_guarded_rows": len(metadata_rows),
        "interpretation": "Mass retention is not an output certificate under value-norm tail risk. Scalar value-norm metadata can repair many adversarial outlier rows without reading V vectors, but it changes the compiler contract and adds a sidecar/kernel requirement.",
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "value_norm_guarded_attention_stress",
        "kind": "python_value_norm_guarded_attention_stress",
        "evidence_tier": "E2p75_value_norm_tail_risk_stress",
        "run_provenance": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "source_path": str(Path(__file__).relative_to(ROOT)),
            "source_sha256": sha256_file(Path(__file__)),
            "core_source_path": "experiments/attention_compiler_core/attention_core.py",
            "core_source_sha256": sha256_file(ROOT / "experiments/attention_compiler_core/attention_core.py"),
            "command": "python experiments/value_norm_guarded_attention/value_norm_guarded_attention.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "seed_policy": {"seeds": SEEDS, "rows_per_regime": ROWS_PER_REGIME, "regimes": REGIMES},
        },
        "summary": summary,
        "rows": rows,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "run": "value_norm_guarded_attention_stress",
        "artifact": str(OUT.relative_to(ROOT)),
        "artifact_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "source": str(Path(__file__).relative_to(ROOT)),
        "source_sha256": payload["run_provenance"]["source_sha256"],
        "command": payload["run_provenance"]["command"],
        "platform": payload["run_provenance"]["platform"],
        "seed_policy": payload["run_provenance"]["seed_policy"],
    }
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT.relative_to(ROOT)),
        "mass_only_failures": payload["summary"]["failure_repair_summary"]["mass_only_rows_with_target_mass_but_bad_output"],
        "exception_repairs": payload["summary"]["failure_repair_summary"]["value_norm_exception_repairs"],
        "oracle_leakage_rows": payload["summary"]["selection_oracle_leakage_rows"],
    }, indent=2))


if __name__ == "__main__":
    main()
