#!/usr/bin/env python3
"""rev0064 value-layout speed envelope over the local learned Q/K/V trace packet.

rev0063 showed a small oracle/free-selector QK-included headroom but also found
that sparse value-only accumulation was slower than dense value-only on this CPU
trace.  That result could have been a layout artifact: the rev0063 sparse loop
scanned the whole mask row and branched on every token.

This probe answers a narrower engineering question before adding more selector
machinery: if exact Top-p support were still supplied as a non-deployable oracle,
can value accumulation be made a win by changing only the value-layout/schedule?

Paths compared:
  * dense value-only: contiguous all-token accumulation using dense probabilities.
  * mask-scan sparse: scan all N mask entries and branch into selected values.
  * rank-gather sparse: iterate selected indices in probability-rank order.
  * sorted-gather sparse: iterate selected indices in key-cache order.
  * packed sparse: iterate prepacked selected (prob, value) records contiguously.
  * QK-included sorted/packed sparse: still computes all QK scores and uses an
    oracle support list, but changes the value access schedule.

Every sparse path is an upper bound, not a deployable selector claim: exact Top-p
support comes from the full dense score row, and public/pretrained/GPU claims are
explicitly false.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0064"}
REV = META.get("revision", "rev0064")
REVUP = REV.upper()
STAMP = "2026-06-18T11:32:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_value_layout_envelope"
CPP = ROOT / "experiments" / "trace_packet_value_layout_envelope" / "trace_packet_value_layout_envelope.cpp"
EXE = BUILD_DIR / "trace_packet_value_layout_envelope"
REPEATS = int(os.environ.get("CTML_VALUE_LAYOUT_REPEATS", "6000"))
TARGET_MASS = 0.96
QUALITY_MIN_RATE = 0.99
REGIME_IDS = {"low_support_lt12": 0, "mid_support_12_28": 1, "high_support_ge28": 2}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs: Iterable[float]) -> float | None:
    vals = [float(x) for x in xs]
    return float(statistics.fmean(vals)) if vals else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    return float(vals[int(q * (len(vals) - 1))])


def find_qk_packet() -> Path:
    candidates = sorted((ROOT / "artifacts" / "trace-bundles").glob("REV*_TINY_TRAINED_QK_TRACE_PACKET.npz"), reverse=True)
    for p in candidates:
        if p.name.startswith("REV0062") or p.name.startswith(REVUP):
            return p
    if candidates:
        return candidates[0]
    raise FileNotFoundError("no Q/K/V trace packet found")


def stable_softmax(scores: np.ndarray) -> np.ndarray:
    x = scores.astype(np.float64)
    x = x - np.max(x)
    w = np.exp(np.clip(x, -80.0, 0.0))
    return w / np.sum(w)


def exact_topp_indices(probs: np.ndarray, target: float = TARGET_MASS) -> tuple[np.ndarray, np.ndarray, float]:
    rank_order = np.argsort(-probs).astype(np.uint32)
    chosen: list[int] = []
    total = 0.0
    for idx in rank_order:
        chosen.append(int(idx))
        total += float(probs[int(idx)])
        if total >= target:
            break
    rank = np.array(chosen, dtype=np.uint32)
    sorted_idx = np.array(sorted(chosen), dtype=np.uint32)
    return rank, sorted_idx, total


def prepare_input(packet_path: Path) -> dict[str, Any]:
    z = np.load(packet_path)
    queries = np.asarray(z["queries"], dtype=np.float64)
    keys = np.asarray(z["keys"], dtype=np.float64)
    values = np.asarray(z["values"], dtype=np.float64)
    scores_packet = np.asarray(z["scores"], dtype=np.float64) if "scores" in z.files else None
    regimes_raw = z["regime"] if "regime" in z.files else np.array(["unknown"] * queries.shape[0])
    rows, n, dk = keys.shape
    dv = values.shape[2]
    if queries.shape != (rows, dk) or values.shape[:2] != (rows, n):
        raise ValueError(f"bad packet shapes queries={queries.shape} keys={keys.shape} values={values.shape}")

    probs = np.zeros((rows, n), dtype=np.float64)
    masks = np.zeros((rows, n), dtype=np.uint8)
    rank_lists: list[np.ndarray] = []
    sorted_lists: list[np.ndarray] = []
    offsets = [0]
    selected_counts: list[int] = []
    masses: list[float] = []
    eff_supports: list[float] = []
    max_diff = 0.0

    packed_probs: list[float] = []
    packed_values: list[float] = []
    for r in range(rows):
        scores = keys[r] @ queries[r] / math.sqrt(float(dk))
        if scores_packet is not None:
            max_diff = max(max_diff, float(np.max(np.abs(scores - scores_packet[r]))))
        pr = stable_softmax(scores)
        probs[r] = pr
        rank, sorted_idx, mass = exact_topp_indices(pr, TARGET_MASS)
        rank_lists.append(rank)
        sorted_lists.append(sorted_idx)
        selected_counts.append(int(len(sorted_idx)))
        masses.append(float(mass))
        offsets.append(offsets[-1] + int(len(sorted_idx)))
        masks[r, sorted_idx] = 1
        for i in sorted_idx:
            packed_probs.append(float(pr[int(i)]))
            packed_values.extend(float(x) for x in values[r, int(i), :])
        eff_supports.append(float(math.exp(-float(np.sum(pr * np.log(np.maximum(pr, 1e-30)))))))

    rank_concat = np.concatenate(rank_lists) if rank_lists else np.zeros(0, dtype=np.uint32)
    sorted_concat = np.concatenate(sorted_lists) if sorted_lists else np.zeros(0, dtype=np.uint32)
    offsets_arr = np.asarray(offsets, dtype=np.uint64)
    packed_probs_arr = np.asarray(packed_probs, dtype=np.float64)
    packed_values_arr = np.asarray(packed_values, dtype=np.float64)
    regime_ids = np.array([REGIME_IDS.get(str(r), -1) for r in regimes_raw], dtype=np.int32)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR64")
        f.write(struct.pack("QQQQQ", int(rows), int(n), int(dk), int(dv), int(offsets[-1])))
        f.write(np.ascontiguousarray(queries, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(keys, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(values, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(probs, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(masks, dtype=np.uint8).tobytes(order="C"))
        f.write(offsets_arr.tobytes(order="C"))
        f.write(rank_concat.astype(np.uint32, copy=False).tobytes(order="C"))
        f.write(sorted_concat.astype(np.uint32, copy=False).tobytes(order="C"))
        f.write(packed_probs_arr.tobytes(order="C"))
        f.write(packed_values_arr.tobytes(order="C"))
        f.write(np.ascontiguousarray(regime_ids, dtype=np.int32).tobytes(order="C"))

    packet_manifest_path = packet_path.with_name(packet_path.stem + "_MANIFEST.json")
    packet_manifest = json.loads(packet_manifest_path.read_text(encoding="utf-8")) if packet_manifest_path.exists() else {}
    return {
        "trace_packet": packet_path.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(packet_path),
        "trace_packet_manifest": packet_manifest,
        "rows": int(rows),
        "n_tokens": int(n),
        "d_key": int(dk),
        "d_value": int(dv),
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
        "oracle_topp96_support": {
            "target_mass": TARGET_MASS,
            "support_is_oracle_upper_bound": True,
            "support_is_promotional": False,
            "mean_selected_count": fmean(selected_counts),
            "mean_selected_fraction": fmean(c / n for c in selected_counts),
            "p90_selected_count": pctl(selected_counts, 0.90),
            "mean_exact_mass": fmean(masses),
            "min_exact_mass": float(min(masses)) if masses else None,
            "packed_selected_records": int(offsets[-1]),
            "packed_value_doubles": int(len(packed_values_arr)),
        },
        "trace_summary": {
            "mean_effective_support": fmean(eff_supports),
            "p90_effective_support": pctl(eff_supports, 0.90),
            "regime_counts": {str(k): int(v) for k, v in zip(*np.unique(regimes_raw.astype(str), return_counts=True))},
            "max_qk_score_packet_abs_diff": max_diff,
        },
    }


def compile_native() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        raise RuntimeError("no C++ compiler found")
    cmd = [compiler, "-O3", "-std=c++17", "-march=native", str(CPP), "-o", str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)


def run_native() -> dict[str, Any]:
    compile_native()
    proc = subprocess.run([str(EXE), str(BIN_INPUT), str(REPEATS)], cwd=ROOT, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    timing = native.get("timing", {})
    all_rows = native.get("all_rows", {})
    accounting = native.get("accounting", {})
    qk_packed_speedup = float(timing.get("oracle_topp96_qk_included_packed_speedup_vs_dense", 0.0))
    packed_value_speedup = float(timing.get("packed_sparse_value_only_speedup_vs_dense_value_only", 0.0))
    sorted_value_speedup = float(timing.get("sorted_index_sparse_value_only_speedup_vs_dense_value_only", 0.0))
    build_ms = float(timing.get("packed_layout_build_ms", 0.0))
    packed_ms = float(timing.get("packed_sparse_value_only_ms", 1e-12))
    build_equiv_replays = build_ms / max(1e-12, packed_ms)
    summary = {
        "trace_packet_rows": prep["rows"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "qk_score_computation_measured_for_qk_included_paths": True,
        "oracle_support_upper_bound_measured": True,
        "oracle_topp96_support_is_promotional": False,
        "oracle_topp96_mean_selected_fraction": prep["oracle_topp96_support"]["mean_selected_fraction"],
        "oracle_topp96_quality_rate": all_rows.get("quality_rate"),
        "oracle_topp96_mean_rel_l2": all_rows.get("mean_rel_l2"),
        "oracle_topp96_mean_cosine": all_rows.get("mean_cosine"),
        "mask_scan_value_only_speedup_vs_dense_value_only": timing.get("mask_scan_sparse_value_only_speedup_vs_dense_value_only"),
        "rank_gather_value_only_speedup_vs_dense_value_only": timing.get("rank_index_sparse_value_only_speedup_vs_dense_value_only"),
        "sorted_gather_value_only_speedup_vs_dense_value_only": sorted_value_speedup,
        "packed_value_only_speedup_vs_dense_value_only": packed_value_speedup,
        "oracle_topp96_qk_included_sorted_speedup_vs_dense": timing.get("oracle_topp96_qk_included_sorted_speedup_vs_dense"),
        "oracle_topp96_qk_included_packed_speedup_vs_dense": qk_packed_speedup,
        "packed_layout_build_ms": build_ms,
        "packed_layout_build_equivalent_replays": build_equiv_replays,
        "value_layout_interpretation": (
            "layout-positive upper bound: prepacked selected values beat dense value-only and the qk-included packed oracle path clears dense, but the support/layout are oracle side inputs"
            if packed_value_speedup > 1.0 and qk_packed_speedup > 1.0 else
            "qk-included upper bound clears dense only after value-layout improvement, but packed value-only is not itself faster than dense value-only"
            if qk_packed_speedup > 1.0 else
            "value layout alone does not rescue the sparse path on this CPU trace; even the packed oracle schedule does not clear dense with QK included"
        ),
        "promotion_allowed": False,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "oracle_topp96_support_is_not_deployable_selector",
            "packed_value_layout_is_oracle_side_input",
            "packed_layout_build_cost_not_paid_by_single_query_path",
            "qk_included_sparse_paths_still_compute_all_qk_scores",
        ],
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_TRACE_PACKET_VALUE_LAYOUT_ENVELOPE",
        "created_at": STAMP,
        "measurement_scope": "native CPU value-layout envelope over a local tiny-trained trace packet; oracle upper bound; not public/pretrained; not GPU; not fused; not a deployable sparse selector; packed layout is a non-promotional side input",
        "trace_packet": prep["trace_packet"],
        "trace_packet_sha256": prep["trace_packet_sha256"],
        "trace_packet_manifest": prep["trace_packet_manifest"],
        "input_bin": prep["input_bin"],
        "input_bin_sha256": prep["input_bin_sha256"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "promotion_allowed": False,
        "oracle_topp96_support": prep["oracle_topp96_support"],
        "trace_summary": prep["trace_summary"],
        "native_result": native,
        "summary": summary,
        "claim_boundary": "Only a value-layout/schedule envelope. Exact Top-p support and packed selected values are oracle/non-deployable side inputs. A win here would justify kernel/layout work, not mechanism promotion.",
    }


def write_manifest(artifact: dict[str, Any]) -> None:
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "source": CPP.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(CPP),
        "python_source": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "python_source_sha256": sha256_file(Path(__file__).resolve()),
        "native_input": BIN_INPUT.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(BIN_INPUT),
        "trace_packet": artifact["trace_packet"],
        "trace_packet_sha256": artifact["trace_packet_sha256"],
        "command": f"{sys.executable} experiments/trace_packet_value_layout_envelope/trace_packet_value_layout_envelope.py",
        "created_at": STAMP,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "native_repeats": REPEATS,
        },
        "claim_boundary": "not public/pretrained, not GPU, not fused, not a deployable selector; exact Top-p support and packed values are oracle value-layout upper bounds",
        "promotion_allowed": False,
    }
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    packet = find_qk_packet()
    prep = prepare_input(packet)
    native = run_native()
    artifact = build_artifact(prep, native)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    write_manifest(artifact)
    print(json.dumps({
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "packed_value_speedup": artifact["summary"]["packed_value_only_speedup_vs_dense_value_only"],
        "packed_qk_speedup": artifact["summary"]["oracle_topp96_qk_included_packed_speedup_vs_dense"],
        "promotion_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
