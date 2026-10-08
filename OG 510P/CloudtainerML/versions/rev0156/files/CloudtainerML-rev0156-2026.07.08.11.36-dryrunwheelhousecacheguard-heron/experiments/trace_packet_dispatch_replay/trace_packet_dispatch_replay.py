#!/usr/bin/env python3
"""rev0060 trace-packet dispatch replay.

rev0059 correctly blocked fused/materialization-free promotion on synthetic native
CPU schedule rows, but one major blocker remained: the dispatch gate had not yet
been exercised on a replayable model-trace packet.  This probe creates an
offline trace-evidence packet from a locally trained tiny transformer, evaluates
it through the existing trace gate, and replays dispatch rules over the packet.

The packet is deliberately **not** public/pretrained evidence.  It is an E2.95
replay harness and learned-trace stress test: a future TransformerLens/HF capture
can be dropped into the same NPZ+manifest contract, but no current output may
promote public/pretrained or GPU/fused-kernel claims.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.attention_compiler_core.attention_core import stable_softmax  # noqa: E402
from experiments.public_trace_gate_surrogate import public_trace_gate_surrogate as trace_gate  # noqa: E402
from experiments.tiny_transformer_attention_traces import tiny_transformer_attention_trace_probe as tiny_trace  # noqa: E402

META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0060"}
REV = META.get("revision", "rev0060")
REVUP = REV.upper()
STAMP = "2026-06-18T08:35:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_DISPATCH_REPLAY.json"
GATE_OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_PUBLIC_GATE_EVAL.json"
PACKET = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_TINY_TRAINED_TRACE_PACKET.npz"
PACKET_MANIFEST = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_TINY_TRAINED_TRACE_PACKET_MANIFEST.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_PACKET_DISPATCH_REPLAY_RUN_MANIFEST.json"

SEED = 60060
TRACE_BATCHES = 2
TRACE_BATCH = 16
TARGET_MASS = 0.95
MAX_SPARSE_SELECTED_FRACTION = 0.80
MAX_STRICT_QK_FRACTION = 1.10
QUALITY_MIN_RATE = 0.999
# rev0057 measured this CPU primitive ratio for router-dimension QK versus
# sequential value accumulation.  It is still a proxy for this trace packet, so
# every claim keeps CPU/non-GPU scope.
CPU_MEASURED_QK_WEIGHT = 1.0629108065025776
VALUE_WEIGHT = 1.0
SCORE_MEMORY_UNIT = 0.05  # deliberately small; keeps score storage visible without dominating.


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs: Iterable[float]) -> float | None:
    vals = list(xs)
    return float(statistics.fmean(vals)) if vals else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    return vals[int(q * (len(vals) - 1))]


def support_bucket(eff: float) -> str:
    if eff < 12.0:
        return "low_support_lt12"
    if eff < 28.0:
        return "mid_support_12_28"
    return "high_support_ge28"


def capture_tiny_trace_packet() -> dict[str, Any]:
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    model, train_metrics = tiny_trace.train_model()
    scores_rows: list[np.ndarray] = []
    values_rows: list[np.ndarray] = []
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
                layer_logits = tr["logits"].numpy()  # B,H,T,S
                layer_values = tr["values"].numpy()  # B,H,S,DH
                for b in range(TRACE_BATCH):
                    for h in range(tiny_trace.HEADS):
                        scores = layer_logits[b, h, -1].astype(np.float64)
                        values = layer_values[b, h].astype(np.float64)
                        probs = stable_softmax(scores)
                        eff = float(math.exp(-float(np.sum(probs * np.log(np.maximum(probs, 1e-30))))))
                        scores_rows.append(scores)
                        values_rows.append(values)
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
    scores = np.stack(scores_rows).astype(np.float64)
    values = np.stack(values_rows).astype(np.float64)
    value_norms = np.stack(value_norm_rows).astype(np.float64)
    np.savez_compressed(
        PACKET,
        scores=scores,
        values=values,
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
    info = {
        "project": "CloudtainerML",
        "revision": REV,
        "trace_packet": PACKET.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(PACKET),
        "generated_at": STAMP,
        "trace_packet_kind": "tiny_trained_local_transformer_qkv_scores_values_not_public_pretrained",
        "public_pretrained_trace_loaded": False,
        "external_trace_loaded": True,
        "allowed_claims": [
            "schema-compatible external trace replay",
            "local tiny trained model trace stress test",
            "dispatch and claim-gate exercise before public/pretrained packet is available",
        ],
        "prohibited_claims": [
            "public/pretrained model evidence",
            "GPU/fused-kernel timing",
            "deployment speedup",
        ],
        "schema": {
            "scores": "float[rows,n]",
            "values": "float[rows,n,dv]",
            "value_norms": "float[rows,n]",
            "regime": "support bucket labels; not generator oracle labels",
        },
        "row_count": int(scores.shape[0]),
        "n_tokens": int(scores.shape[1]),
        "d_value": int(values.shape[-1]),
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
            "command": "python experiments/trace_packet_dispatch_replay/trace_packet_dispatch_replay.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
            "seed": SEED,
            "trace_batches": TRACE_BATCHES,
            "trace_batch": TRACE_BATCH,
        },
    }
    PACKET_MANIFEST.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return info


def method_name(prefix: str) -> str:
    return f"{prefix}_{str(TARGET_MASS).replace('.', 'p')}_bins32"


def group_gate_rows(gate_payload: dict[str, Any]) -> dict[tuple[Any, ...], dict[str, dict[str, Any]]]:
    groups: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in gate_payload.get("rows", []):
        key = (r.get("row_id"), r.get("layer"), r.get("head"), r.get("position"), r.get("regime"))
        groups[key][r.get("method")] = r
    return groups


def cost_units(qk_dots: float, value_reads: float, score_writes: float = 0.0, score_reads: float = 0.0, qk_weight: float = CPU_MEASURED_QK_WEIGHT) -> float:
    return float(qk_weight * qk_dots + VALUE_WEIGHT * value_reads + SCORE_MEMORY_UNIT * (score_writes + score_reads))


def candidate_from_row(kind: str, method_row: dict[str, Any], n: int, *, streaming: bool = False, value_norm_sidecar: bool = False) -> dict[str, Any]:
    selected = float(method_row.get("selected_count", method_row.get("value_reads", n)))
    if kind == "dense_online_one_pass":
        qk = n
        score_writes = 0
        score_reads = 0
        selected = n
        quality = True
        materializes = False
    elif streaming:
        # Streaming/recompute schedule: max/hist/select+accumulate scans avoid
        # global score storage but repeat QK-like work.  This mirrors rev0058's
        # materialization-free schedule tax in counted form for learned traces.
        qk = 3 * n
        score_writes = 0
        score_reads = 0
        quality = bool(method_row.get("passes_quality_bar"))
        materializes = False
    else:
        qk = n
        score_writes = n
        score_reads = n
        quality = bool(method_row.get("passes_quality_bar"))
        materializes = True
    c = cost_units(qk, selected, score_writes, score_reads)
    return {
        "candidate": kind,
        "method": method_row.get("method", kind),
        "n_tokens": int(n),
        "selected_count": int(round(selected)),
        "selected_fraction": float(selected / max(1, n)),
        "qk_dot_products": int(qk),
        "qk_fraction_vs_dense": float(qk / max(1, n)),
        "score_memory_writes": int(score_writes),
        "score_memory_reads": int(score_reads),
        "materializes_scores": bool(materializes),
        "materialization_free_streaming": bool(streaming),
        "uses_value_norm_sidecar": bool(value_norm_sidecar),
        "quality_bar_pass": bool(quality),
        "mass_retained": float(method_row.get("mass_retained", 1.0)),
        "output_cosine": float(method_row.get("output_cosine", 1.0)),
        "attention_rel_l2_error": float(method_row.get("attention_rel_l2_error", 0.0)),
        "selection_uses_values": bool(method_row.get("selection_uses_values", False)),
        "selection_uses_dense_output": bool(method_row.get("selection_uses_dense_output", False)),
        "selection_uses_value_norms": bool(method_row.get("selection_uses_value_norms", False)),
        "cost_units_cpu_measured_proxy": float(c),
    }


def vetoes_for(cand: dict[str, Any], dense_cost: float, *, require_no_score_storage: bool, require_sparse: bool, require_speed: bool, require_low_qk_fraction: bool) -> list[str]:
    vetoes: list[str] = []
    if cand["selection_uses_values"] or cand["selection_uses_dense_output"]:
        vetoes.append("oracle_selection_leakage")
    if not cand["quality_bar_pass"]:
        vetoes.append("quality_bar_failed")
    if require_no_score_storage and cand["materializes_scores"]:
        vetoes.append("global_score_storage_required")
    if require_sparse and cand["selected_fraction"] > MAX_SPARSE_SELECTED_FRACTION:
        vetoes.append("near_dense_value_reads")
    if require_speed and cand["cost_units_cpu_measured_proxy"] >= dense_cost:
        vetoes.append("not_faster_than_dense_under_cpu_measured_proxy")
    if require_low_qk_fraction and cand["qk_fraction_vs_dense"] > MAX_STRICT_QK_FRACTION:
        vetoes.append("qk_schedule_tax_too_high_for_fused_claim")
    return vetoes


def choose_policy(policy: str, cands: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dense = cands["dense_online_one_pass"]
    dense_cost = dense["cost_units_cpu_measured_proxy"]
    if policy == "score_storage_allowed_cpu_gate":
        cand_names = ["materialized_mass_histogram"]
        kwargs = dict(require_no_score_storage=False, require_sparse=True, require_speed=True, require_low_qk_fraction=False)
    elif policy == "strict_materialization_free_gate":
        cand_names = ["streaming_mass_histogram"]
        kwargs = dict(require_no_score_storage=True, require_sparse=True, require_speed=True, require_low_qk_fraction=True)
    elif policy == "value_norm_sidecar_materialized_gate":
        cand_names = ["materialized_value_norm_exception"]
        kwargs = dict(require_no_score_storage=False, require_sparse=True, require_speed=True, require_low_qk_fraction=False)
    else:
        raise ValueError(policy)
    accepted: list[tuple[str, dict[str, Any], list[str]]] = []
    rejected: list[dict[str, Any]] = []
    for name in cand_names:
        cand = cands[name]
        veto = vetoes_for(cand, dense_cost, **kwargs)
        if veto:
            rejected.append({"candidate": name, "vetoes": veto, "cost_units": cand["cost_units_cpu_measured_proxy"], "selected_fraction": cand["selected_fraction"], "qk_fraction_vs_dense": cand["qk_fraction_vs_dense"]})
        else:
            accepted.append((name, cand, []))
    if accepted:
        name, chosen, _ = min(accepted, key=lambda x: x[1]["cost_units_cpu_measured_proxy"])
        fallback = False
        vetoes = []
    else:
        name, chosen = "dense_online_one_pass", dense
        fallback = True
        vetoes = rejected[0]["vetoes"] if rejected else ["no_candidate"]
    return {
        "policy": policy,
        "chosen_candidate": name,
        "fallback_to_dense": bool(fallback),
        "vetoes": vetoes,
        "rejected_candidates": rejected,
        "chosen_cost_units": chosen["cost_units_cpu_measured_proxy"],
        "dense_cost_units": dense_cost,
        "speedup_vs_dense_cost_proxy": float(dense_cost / max(1e-12, chosen["cost_units_cpu_measured_proxy"])),
        "chosen_selected_fraction": chosen["selected_fraction"],
        "chosen_qk_fraction_vs_dense": chosen["qk_fraction_vs_dense"],
        "chosen_quality_bar_pass": chosen["quality_bar_pass"],
        "chosen_materializes_scores": chosen["materializes_scores"],
        "chosen_materialization_free_streaming": chosen["materialization_free_streaming"],
    }


def summarize_decisions(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    policies = sorted({d["policy"] for d in decisions})
    for policy in policies:
        xs = [d for d in decisions if d["policy"] == policy]
        sparse = [d for d in xs if d["chosen_candidate"] != "dense_online_one_pass"]
        by_regime: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for d in xs:
            by_regime[str(d["regime"])].append(d)
        out[policy] = {
            "rows": len(xs),
            "sparse_row_count": len(sparse),
            "sparse_row_rate": float(len(sparse) / max(1, len(xs))),
            "aggregate_speedup_vs_dense_cost_proxy": float(fmean(d["dense_cost_units"] for d in xs) / max(1e-12, fmean(d["chosen_cost_units"] for d in xs))),
            "mean_chosen_selected_fraction": fmean(d["chosen_selected_fraction"] for d in xs),
            "mean_chosen_qk_fraction_vs_dense": fmean(d["chosen_qk_fraction_vs_dense"] for d in xs),
            "materialized_sparse_row_count": sum(1 for d in sparse if d["chosen_materializes_scores"]),
            "streaming_sparse_row_count": sum(1 for d in sparse if d["chosen_materialization_free_streaming"]),
            "sparse_rows_by_regime": {reg: sum(1 for d in rows if d["chosen_candidate"] != "dense_online_one_pass") for reg, rows in by_regime.items()},
            "quality_pass_rate": fmean(float(d["chosen_quality_bar_pass"]) for d in xs),
            "top_vetoes": sorted({v for d in xs for v in d.get("vetoes", [])}),
        }
    return out


def run() -> dict[str, Any]:
    start = time.perf_counter()
    packet_manifest = capture_tiny_trace_packet()
    gate_payload = trace_gate.run(
        PACKET,
        public_pretrained_trace=False,
        trace_source_label="rev0060_tiny_trained_trace_packet_not_public_pretrained",
        bundle_model_id="local_tiny_trained_transformer_not_public_or_pretrained",
        bundle_license="internal generated diagnostic trace packet",
    )
    # The imported helper is from rev0049 and keeps its own internal revision;
    # the current artifact wraps it and records rev0060 in the packet/replay layer.
    gate_payload["revision"] = REV
    gate_payload["generated_at"] = STAMP
    GATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    GATE_OUT.write_text(json.dumps(gate_payload, indent=2) + "\n", encoding="utf-8")

    groups = group_gate_rows(gate_payload)
    mass_name = method_name("mass_histogram")
    sidecar_name = method_name("value_norm_exception_mass")
    decisions: list[dict[str, Any]] = []
    row_checks: list[dict[str, Any]] = []
    for key, methods in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        row_id, layer, head, position, regime = key
        dense_row = methods.get("full_dense")
        mass_row = methods.get(mass_name)
        sidecar_row = methods.get(sidecar_name)
        if not dense_row or not mass_row or not sidecar_row:
            continue
        n = int(dense_row.get("N", packet_manifest["n_tokens"]))
        dense = candidate_from_row("dense_online_one_pass", dense_row, n)
        mat = candidate_from_row("materialized_mass_histogram", mass_row, n, streaming=False)
        stream = candidate_from_row("streaming_mass_histogram", mass_row, n, streaming=True)
        sidecar = candidate_from_row("materialized_value_norm_exception", sidecar_row, n, streaming=False, value_norm_sidecar=True)
        cands = {
            "dense_online_one_pass": dense,
            "materialized_mass_histogram": mat,
            "streaming_mass_histogram": stream,
            "materialized_value_norm_exception": sidecar,
        }
        row_meta = {
            "row_id": int(row_id),
            "layer": int(layer),
            "head": int(head),
            "position": int(position),
            "regime": str(regime),
            "N": n,
            "external_trace_loaded": bool(mass_row.get("external_trace_loaded")),
            "public_pretrained_trace_loaded": bool(mass_row.get("public_pretrained_trace_loaded")),
            "is_surrogate_trace": bool(mass_row.get("is_surrogate_trace")),
            "mass_hist_selected_fraction": mat["selected_fraction"],
            "mass_hist_quality_bar_pass": mat["quality_bar_pass"],
            "mass_hist_cost_speedup_vs_dense_proxy": dense["cost_units_cpu_measured_proxy"] / max(1e-12, mat["cost_units_cpu_measured_proxy"]),
            "streaming_hist_cost_speedup_vs_dense_proxy": dense["cost_units_cpu_measured_proxy"] / max(1e-12, stream["cost_units_cpu_measured_proxy"]),
            "sidecar_cost_speedup_vs_dense_proxy": dense["cost_units_cpu_measured_proxy"] / max(1e-12, sidecar["cost_units_cpu_measured_proxy"]),
        }
        row_checks.append(row_meta)
        for policy in ["score_storage_allowed_cpu_gate", "strict_materialization_free_gate", "value_norm_sidecar_materialized_gate"]:
            d = choose_policy(policy, cands)
            d.update(row_meta)
            decisions.append(d)

    policy_summary = summarize_decisions(decisions)
    strict = policy_summary.get("strict_materialization_free_gate", {})
    storage = policy_summary.get("score_storage_allowed_cpu_gate", {})
    sidecar = policy_summary.get("value_norm_sidecar_materialized_gate", {})
    public_true_rows = sum(1 for d in decisions if d.get("public_pretrained_trace_loaded"))
    oracle_leak_rows = sum(1 for r in gate_payload.get("rows", []) if r.get("selection_uses_values") or r.get("selection_uses_dense_output") or r.get("selection_oracle_leakage_detected"))

    summary = {
        "promotion_allowed": False,
        "primary_claim": "A replayable learned trace packet now exercises the dispatch gate, but strict materialization-free sparse attention still promotes zero rows under counted QK schedule tax and CPU-measured proxy costs.",
        "trace_packet_rows": packet_manifest["row_count"],
        "trace_packet_regime_counts": packet_manifest["regime_counts"],
        "external_trace_loaded": True,
        "public_pretrained_trace_loaded": False,
        "public_pretrained_rows": public_true_rows,
        "oracle_leakage_rows": oracle_leak_rows,
        "strict_materialization_free_sparse_row_count": int(strict.get("sparse_row_count", 0)),
        "strict_materialization_free_sparse_row_rate": strict.get("sparse_row_rate"),
        "strict_materialization_free_aggregate_speedup_vs_dense_cost_proxy": strict.get("aggregate_speedup_vs_dense_cost_proxy"),
        "score_storage_allowed_sparse_row_rate": storage.get("sparse_row_rate"),
        "score_storage_allowed_aggregate_speedup_vs_dense_cost_proxy": storage.get("aggregate_speedup_vs_dense_cost_proxy"),
        "score_storage_allowed_not_fused_claim": True,
        "value_norm_sidecar_sparse_row_rate": sidecar.get("sparse_row_rate"),
        "learned_trace_dispatch_gate_missing_closed": True,
        "public_trace_blocker_closed": False,
        "gpu_fused_kernel_blocker_closed": False,
        "materialization_free_sparse_schedule_has_no_learned_trace_speed_win": int(strict.get("sparse_row_count", 0)) == 0,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "strict_materialization_free_sparse_schedule_has_no_learned_trace_speed_win",
            "materialized_sparse_cpu_path_requires_global_score_storage",
            "value_norm_sidecar_kernel_path_missing",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_TRACE_PACKET_DISPATCH_REPLAY",
        "probe": "trace_packet_dispatch_replay",
        "kind": "learned_trace_packet_dispatch_replay_and_claim_gate",
        "evidence_tier": "E2p95_local_learned_trace_packet_replay_not_public_pretrained_not_gpu",
        "generated_at": STAMP,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "gpu_fused_kernel_measured": False,
        "external_trace_loaded": True,
        "trace_source_type": "tiny_trained_local_transformer_trace_packet_not_public_pretrained",
        "measurement_scope": "offline learned-trace dispatch replay with CPU-measured proxy cost; not GPU timing, not a fused CUDA/Triton kernel, and not public/pretrained traces",
        "trace_packet": {
            "npz": PACKET.relative_to(ROOT).as_posix(),
            "manifest": PACKET_MANIFEST.relative_to(ROOT).as_posix(),
            "npz_sha256": sha256_file(PACKET),
            "manifest_sha256": sha256_file(PACKET_MANIFEST),
        },
        "trace_gate_eval": {
            "artifact": GATE_OUT.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(GATE_OUT),
            "trace_gate_status": gate_payload.get("trace_gate_status"),
            "external_trace_loaded": gate_payload.get("external_trace_loaded"),
            "public_pretrained_trace_loaded": gate_payload.get("public_pretrained_trace_loaded"),
        },
        "configuration": {
            "target_mass": TARGET_MASS,
            "max_sparse_selected_fraction": MAX_SPARSE_SELECTED_FRACTION,
            "max_strict_qk_fraction": MAX_STRICT_QK_FRACTION,
            "cpu_measured_qk_weight_from_rev0057": CPU_MEASURED_QK_WEIGHT,
            "value_weight": VALUE_WEIGHT,
            "score_memory_unit_proxy": SCORE_MEMORY_UNIT,
            "quality_min_rate": QUALITY_MIN_RATE,
        },
        "policy_summary": policy_summary,
        "dispatch_decisions": decisions,
        "row_checks_sample": row_checks[:64],
        "summary": summary,
        "run_provenance": {
            "source_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "source_sha256": sha256_file(Path(__file__).resolve()),
            "trace_gate_source_path": "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
            "trace_gate_source_sha256": sha256_file(ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"),
            "tiny_trace_source_path": "experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py",
            "tiny_trace_source_sha256": sha256_file(ROOT / "experiments" / "tiny_transformer_attention_traces" / "tiny_transformer_attention_trace_probe.py"),
            "command": "python experiments/trace_packet_dispatch_replay/trace_packet_dispatch_replay.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
            "seed": SEED,
            "wall_seconds": time.perf_counter() - start,
        },
    }
    return artifact


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(payload["run_provenance"], indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "pass",
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "trace_packet": PACKET.relative_to(ROOT).as_posix(),
        "trace_rows": payload["summary"]["trace_packet_rows"],
        "strict_materialization_free_sparse_row_count": payload["summary"]["strict_materialization_free_sparse_row_count"],
        "score_storage_allowed_sparse_row_rate": payload["summary"]["score_storage_allowed_sparse_row_rate"],
        "public_pretrained_trace_loaded": payload["summary"]["public_pretrained_trace_loaded"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
