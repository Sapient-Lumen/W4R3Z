#!/usr/bin/env python3
"""rev0062 native QK replay over a learned trace packet.

rev0061 measured only a materialized-score replay: scores were already present,
so QK score construction remained an open blocker.  This probe creates a new
local tiny-trained trace packet that includes row query vectors, per-row key
caches, and values, then runs a native C++ replay that computes QK scores inside
both dense and sparse paths.

Scope remains intentionally limited: this is CPU native evidence on a local tiny
model, not a public/pretrained trace and not GPU/fused-kernel timing.
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
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.attention_compiler_core.attention_core import stable_softmax  # noqa: E402
from experiments.tiny_transformer_attention_traces import tiny_transformer_attention_trace_probe as tiny_trace  # noqa: E402

META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0062"}
REV = META.get("revision", "rev0062")
REVUP = REV.upper()
STAMP = "2026-06-18T10:04:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY.json"
PACKET = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_TINY_TRAINED_QK_TRACE_PACKET.npz"
PACKET_MANIFEST = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_TINY_TRAINED_QK_TRACE_PACKET_MANIFEST.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_qk_native_replay"
CPP = ROOT / "experiments" / "trace_packet_qk_native_replay" / "trace_packet_qk_native_replay.cpp"
EXE = BUILD_DIR / "trace_packet_qk_native_replay"
REPEATS = int(os.environ.get("CTML_QK_NATIVE_REPEATS", "350"))
SEED = 62062
TRACE_BATCHES = 1
TRACE_BATCH = 16
TARGET_MASS = 0.95
QUALITY_MIN_RATE = 0.999

REGIME_IDS = {"low_support_lt12": 0, "mid_support_12_28": 1, "high_support_ge28": 2}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs: Iterable[float]) -> float | None:
    vals = list(float(x) for x in xs)
    return float(statistics.fmean(vals)) if vals else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    return float(vals[int(q * (len(vals) - 1))])


def support_bucket(eff: float) -> str:
    if eff < 12.0:
        return "low_support_lt12"
    if eff < 28.0:
        return "mid_support_12_28"
    return "high_support_ge28"


def capture_qk_trace_packet() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    # train_model itself is deterministic under tiny_trace.SEED; we leave that
    # unchanged to keep comparability with rev0060/rev0061 packet semantics.
    # Keep this executable inside the cloudtainer: fewer steps than the
    # heavier exploratory trace probe, still enough to produce nonrandom
    # attention rows for the native score-path audit.
    tiny_trace.TRAIN_STEPS = int(os.environ.get("CTML_QK_TRACE_TRAIN_STEPS", "90"))
    tiny_trace.BATCH = int(os.environ.get("CTML_QK_TRACE_TRAIN_BATCH", "48"))
    model, train_metrics = tiny_trace.train_model()
    q_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    score_rows: list[np.ndarray] = []
    value_norm_rows: list[np.ndarray] = []
    regimes: list[str] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    examples: list[int] = []
    trace_batches: list[int] = []
    model_correct: list[int] = []
    effective_supports: list[float] = []
    max_probs: list[float] = []
    needle_positions: list[int] = []
    needle_probs: list[float] = []

    with torch.no_grad():
        for tb in range(TRACE_BATCHES):
            x, y, target_pos = tiny_trace.make_batch(TRACE_BATCH, np.random.default_rng(SEED + 2000 + tb))
            logits, traces = model(x, capture=True)
            pred = logits.argmax(dim=-1).cpu().numpy()
            for layer_id, tr in enumerate(traces):
                # The tiny trace module was refactored in rev0062 so capture
                # exposes Q/K/V in addition to logits.  Older consumers still
                # read the logits/values fields unchanged.
                layer_queries = tr["queries"].numpy()  # B,H,T,DH
                layer_keys = tr["keys"].numpy()        # B,H,S,DH
                layer_values = tr["values"].numpy()    # B,H,S,DH
                layer_logits = tr["logits"].numpy()    # B,H,T,S
                for b in range(TRACE_BATCH):
                    for h in range(tiny_trace.HEADS):
                        q = layer_queries[b, h, -1].astype(np.float64)
                        keys = layer_keys[b, h].astype(np.float64)
                        values = layer_values[b, h].astype(np.float64)
                        scores_from_qk = (keys @ q) / math.sqrt(float(keys.shape[1]))
                        scores_from_trace = layer_logits[b, h, -1].astype(np.float64)
                        max_abs_diff = float(np.max(np.abs(scores_from_qk - scores_from_trace)))
                        if max_abs_diff > 1e-5:
                            raise RuntimeError(f"QK/logit mismatch: {max_abs_diff}")
                        probs = stable_softmax(scores_from_qk)
                        eff = float(math.exp(-float(np.sum(probs * np.log(np.maximum(probs, 1e-30))))))
                        q_rows.append(q)
                        k_rows.append(keys)
                        v_rows.append(values)
                        score_rows.append(scores_from_qk.astype(np.float64))
                        value_norm_rows.append(np.linalg.norm(values, axis=-1).astype(np.float64))
                        regimes.append(support_bucket(eff))
                        layers.append(int(layer_id))
                        heads.append(int(h))
                        positions.append(int(tiny_trace.SEQ - 1))
                        examples.append(int(b))
                        trace_batches.append(int(tb))
                        model_correct.append(int(pred[b] == int(y[b])))
                        effective_supports.append(eff)
                        max_probs.append(float(np.max(probs)))
                        needle = int(target_pos[b])
                        needle_positions.append(needle)
                        needle_probs.append(float(probs[needle]))

    PACKET.parent.mkdir(parents=True, exist_ok=True)
    queries = np.stack(q_rows).astype(np.float64)
    keys = np.stack(k_rows).astype(np.float64)
    values = np.stack(v_rows).astype(np.float64)
    scores = np.stack(score_rows).astype(np.float64)
    value_norms = np.stack(value_norm_rows).astype(np.float64)
    np.savez_compressed(
        PACKET,
        queries=queries,
        keys=keys,
        values=values,
        scores=scores,
        value_norms=value_norms,
        regime=np.asarray(regimes),
        layer=np.asarray(layers, dtype=np.int64),
        head=np.asarray(heads, dtype=np.int64),
        position=np.asarray(positions, dtype=np.int64),
        example=np.asarray(examples, dtype=np.int64),
        trace_batch=np.asarray(trace_batches, dtype=np.int64),
        model_correct=np.asarray(model_correct, dtype=np.int64),
        effective_support=np.asarray(effective_supports, dtype=np.float64),
        max_probability=np.asarray(max_probs, dtype=np.float64),
        needle_position=np.asarray(needle_positions, dtype=np.int64),
        needle_probability=np.asarray(needle_probs, dtype=np.float64),
    )
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "trace_packet": PACKET.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(PACKET),
        "generated_at": STAMP,
        "trace_packet_kind": "tiny_trained_local_transformer_qk_values_not_public_pretrained",
        "public_pretrained_trace_loaded": False,
        "external_trace_loaded": True,
        "qk_vectors_included": True,
        "allowed_claims": [
            "local tiny trained model Q/K/V replay",
            "native CPU QK-score path measurement",
            "score-path promotion veto before public/pretrained packet is available",
        ],
        "prohibited_claims": [
            "public/pretrained model evidence",
            "GPU/fused-kernel timing",
            "deployment speedup",
        ],
        "schema": {
            "queries": "float[rows,dk]",
            "keys": "float[rows,n,dk]",
            "values": "float[rows,n,dv]",
            "scores": "float[rows,n] for packet self-check only; native replay computes scores from Q/K",
            "regime": "support bucket labels; not generator oracle labels",
        },
        "row_count": int(queries.shape[0]),
        "n_tokens": int(keys.shape[1]),
        "d_key": int(keys.shape[2]),
        "d_value": int(values.shape[2]),
        "layers": sorted(set(map(int, layers))),
        "heads": sorted(set(map(int, heads))),
        "regime_counts": {r: int(regimes.count(r)) for r in sorted(set(regimes))},
        "train_metrics": train_metrics,
        "trace_summary": {
            "mean_effective_support": fmean(effective_supports),
            "p90_effective_support": pctl(effective_supports, 0.90),
            "mean_max_probability": fmean(max_probs),
            "model_correct_rate": fmean(float(x) for x in model_correct),
            "mean_needle_probability": fmean(needle_probs),
        },
        "capture_provenance": {
            "source_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "source_sha256": sha256_file(Path(__file__).resolve()),
            "tiny_trace_source_path": "experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py",
            "tiny_trace_source_sha256": sha256_file(ROOT / "experiments" / "tiny_transformer_attention_traces" / "tiny_transformer_attention_trace_probe.py"),
            "command": "python experiments/trace_packet_qk_native_replay/trace_packet_qk_native_replay.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
            "seed": SEED,
            "trace_batches": TRACE_BATCHES,
            "trace_batch": TRACE_BATCH,
        },
    }
    PACKET_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def export_native_input(packet_manifest: dict[str, Any]) -> dict[str, Any]:
    z = np.load(PACKET, allow_pickle=False)
    queries = np.asarray(z["queries"], dtype=np.float64)
    keys = np.asarray(z["keys"], dtype=np.float64)
    values = np.asarray(z["values"], dtype=np.float64)
    regimes_raw = np.asarray(z["regime"]).astype(str)
    if queries.ndim != 2 or keys.ndim != 3 or values.ndim != 3:
        raise ValueError("expected queries[rows,dk], keys[rows,n,dk], values[rows,n,dv]")
    rows, n, dk = keys.shape
    if queries.shape != (rows, dk) or values.shape[:2] != (rows, n):
        raise ValueError("Q/K/V dimensions disagree")
    regime_ids = np.asarray([REGIME_IDS.get(str(r), -1) for r in regimes_raw], dtype=np.int32)
    if np.any(regime_ids < 0):
        raise ValueError("unknown regime label in QK trace packet")
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR62")
        f.write(struct.pack("<QQQQ", rows, n, dk, values.shape[2]))
        f.write(np.ascontiguousarray(queries).tobytes(order="C"))
        f.write(np.ascontiguousarray(keys).tobytes(order="C"))
        f.write(np.ascontiguousarray(values).tobytes(order="C"))
        f.write(np.ascontiguousarray(regime_ids).tobytes(order="C"))
    return {
        "rows": int(rows),
        "n_tokens": int(n),
        "d_key": int(dk),
        "d_value": int(values.shape[2]),
        "regime_counts": packet_manifest.get("regime_counts", {}),
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
        "trace_packet": PACKET.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(PACKET),
    }


def compile_native() -> dict[str, Any]:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("c++")
    if not compiler:
        raise RuntimeError("no C++ compiler available")
    cmd = [compiler, "-O3", "-std=c++17", str(CPP), "-o", str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return {"compiler": compiler, "compile_command": " ".join(cmd), "native_exe": EXE.relative_to(ROOT).as_posix(), "cpp_sha256": sha256_file(CPP)}


def run_native() -> dict[str, Any]:
    cmd = [str(EXE), str(BIN_INPUT), str(REPEATS)]
    proc = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"native QK benchmark did not emit JSON: {proc.stdout[:2000]} {proc.stderr[:2000]}") from exc


def load_rev0061() -> dict[str, Any]:
    p = ROOT / "artifacts" / "probe-results" / "REV0061_TRACE_PACKET_NATIVE_REPLAY.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    packet_manifest = capture_qk_trace_packet()
    exported = export_native_input(packet_manifest)
    compiled = compile_native()
    native = run_native()
    prev = load_rev0061()
    prev_summary = prev.get("summary", {}) if prev else {}
    mat_speed = float(native["timing"]["mass_histogram_speedup_vs_dense_qk_online"])
    stream_speed = float(native["timing"]["streaming_recompute_speedup_vs_dense_qk_online"])
    quality_rate = float(native["all_rows"]["quality_rate"])
    selected_fraction = float(native["all_rows"]["mean_selected_fraction"])
    prev_score_consumption_speed = prev_summary.get("native_mass_histogram_speedup_vs_dense_score_consumption")
    speedup_delta = None
    if prev_score_consumption_speed is not None:
        speedup_delta = float(mat_speed - float(prev_score_consumption_speed))
    promotion_allowed = False
    summary = {
        "trace_packet_rows": int(exported["rows"]),
        "native_replay_rows": int(native["rows"]),
        "qk_score_computation_measured": True,
        "qk_vectors_in_trace_packet": True,
        "native_mass_histogram_quality_rate": quality_rate,
        "native_mass_histogram_mean_selected_fraction": selected_fraction,
        "native_mass_histogram_speedup_vs_dense_qk_online": mat_speed,
        "streaming_recompute_speedup_vs_dense_qk_online": stream_speed,
        "rev0061_score_consumption_only_speedup": prev_score_consumption_speed,
        "qk_replay_minus_score_consumption_speedup": speedup_delta,
        "materialized_score_storage_required": True,
        "streaming_no_score_storage_measured": True,
        "streaming_qk_recompute_fraction": float(native["qk_accounting"]["streaming_recompute_histogram_qk_dot_fraction"]),
        "gpu_fused_kernel_measured": False,
        "public_pretrained_trace_loaded": False,
        "strict_materialization_free_sparse_promoted": False,
        "promotion_allowed": promotion_allowed,
        "quality_bar_passed": quality_rate >= QUALITY_MIN_RATE,
        "materialized_qk_speed_bar_passed": mat_speed > 1.0,
        "streaming_speed_bar_passed": stream_speed > 1.0,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "strict_materialization_free_sparse_schedule_has_no_qk_replay_speed_win",
            "materialized_sparse_qk_path_requires_global_score_storage",
            "local_tiny_qk_trace_not_public_pretrained_evidence",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_TRACE_PACKET_QK_NATIVE_REPLAY",
        "generated_at": STAMP,
        "status": "native_qk_replay_measured_promotion_blocked",
        "promotion_allowed": promotion_allowed,
        "measurement_scope": "native C++ CPU replay over a local tiny-trained Q/K/V trace packet; QK score computation is measured; not GPU, not fused kernel, not public/pretrained evidence; materialized histogram still stores global scores",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "gpu_fused_kernel_measured": False,
        "qk_score_computation_measured": True,
        "score_storage_required_for_materialized_histogram": True,
        "streaming_no_score_storage_measured": True,
        "target_mass": TARGET_MASS,
        "quality_bar": {"mass_min": 0.95, "cosine_min": 0.995, "rel_l2_max": 0.18, "quality_rate_min": QUALITY_MIN_RATE},
        "trace_packet_manifest": packet_manifest,
        "input": exported,
        "native_build": compiled,
        "native_result": native,
        "previous_rev0061_score_consumption_replay": {
            "artifact": "REV0061_TRACE_PACKET_NATIVE_REPLAY.json" if prev else None,
            "score_consumption_only_speedup": prev_score_consumption_speed,
            "quality_rate": prev_summary.get("native_mass_histogram_quality_rate"),
            "selected_fraction": prev_summary.get("native_mass_histogram_mean_selected_fraction"),
        },
        "summary": summary,
        "interpretation": (
            "rev0062 closes the QK-measurement gap for the local learned trace packet by replaying dense and sparse attention from Q/K/V vectors natively. "
            "The materialized histogram path may be judged only as a CPU materialized-score path because it still stores scores; the no-score-storage streaming path is separately timed and remains non-promotional."
        ),
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    run_manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "source": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "native_source": CPP.relative_to(ROOT).as_posix(),
        "native_source_sha256": sha256_file(CPP),
        "trace_packet": PACKET.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(PACKET),
        "native_input": BIN_INPUT.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(BIN_INPUT),
        "command": "python experiments/trace_packet_qk_native_replay/trace_packet_qk_native_replay.py",
        "native_repeats": REPEATS,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "torch": torch.__version__,
        "platform": platform.platform(),
        "measurement_scope": artifact["measurement_scope"],
    }
    RUN_MANIFEST.write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "rows": summary["trace_packet_rows"], "qk_measured": True, "materialized_speedup": mat_speed, "streaming_speedup": stream_speed, "promotion_allowed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
