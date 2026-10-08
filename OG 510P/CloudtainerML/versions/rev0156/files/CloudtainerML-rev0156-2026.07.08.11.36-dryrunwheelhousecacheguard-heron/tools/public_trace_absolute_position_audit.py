#!/usr/bin/env python3
"""Audit absolute row-position semantics for cached-decode trace bundles.

rev0083 fixes a concrete trace-identity hazard: q_len=1 cached-decode rows were
previously exportable with local query position 0, even though they attend at an
absolute position inside a longer live KV cache. Dense score parity alone cannot
catch that bug because position labels do not enter the QK dot product. This
audit proves the gate accepts a mixed bundle with absolute key positions and
rejects a same-math bundle whose decode rows are relabeled with local positions.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0083")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_PATH = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE_PATH = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def softmax(scores: np.ndarray) -> np.ndarray:
    shifted = scores - np.max(scores)
    exps = np.exp(shifted)
    return exps / np.sum(exps)


def make_case(*, q_len: int, key_len: int, seed: int, causal: bool) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch, heads, kv_heads, d_head, d_value = 1, 2, 1, 4, 3
    q = rng.normal(0.0, 0.35, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scaling = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    if causal:
        for pos in range(q_len):
            if pos + 1 < key_len:
                mask[:, :, pos, pos + 1 :] = -np.inf
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            for h in range(heads):
                additive = np.where(np.isneginf(mask[b, 0, pos]), -1.0e30, mask[b, 0, pos])
                scores = (k[b, 0] @ q[b, h, pos]) * scaling + additive
                out[b, pos, h] = softmax(scores) @ v[b, 0]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling}


def rows_for(cap, case: dict[str, Any], *, phase: str, policy: str) -> tuple:
    return cap._rows_from_attention_capture(
        q=case["q"],
        k=case["k"],
        v=case["v"],
        out=case["out"],
        attention_mask=case["mask"],
        scaling=case["scaling"],
        layer_id=0,
        prompt_index=0,
        position_policy=policy,
        max_remaining=64,
        num_key_value_groups=2,
        capture_phase=phase,
    )


def merge_rows(*row_sets: tuple) -> tuple:
    out = list(row_sets[0])
    for rows in row_sets[1:]:
        for i in range(14):
            out[i] = out[i] + rows[i]
        out[14] = bool(out[14] and rows[14])
        out[15] = bool(out[15] or rows[15])
        out[16] = max(float(out[16]), float(rows[16]))
    return tuple(out)


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def kv_group_fields(gate, heads: list[int] | np.ndarray) -> dict[str, Any]:
    """Return row-level GQA ownership metadata for synthetic Llama fixtures.

    The existing fixture calls _rows_from_attention_capture with
    num_key_value_groups=2, so both query heads share one compact K/V head.
    Public trace validation must carry this ownership explicitly; otherwise
    downstream cost/cache analysis can count duplicated per-query K/V rows as
    independent KV-cache storage.
    """
    head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
    row_count = int(head_arr.shape[0])
    num_attention_heads_value = int(max(1, int(np.max(head_arr)) + 1)) if row_count else 1
    num_key_value_heads_value = 1
    num_key_value_groups_value = max(1, num_attention_heads_value // num_key_value_heads_value)
    num_attention_heads = np.full((row_count,), num_attention_heads_value, dtype=np.int64)
    num_key_value_heads = np.full((row_count,), num_key_value_heads_value, dtype=np.int64)
    num_key_value_groups = np.full((row_count,), num_key_value_groups_value, dtype=np.int64)
    kv_head = (head_arr // num_key_value_groups_value).astype(np.int64)
    verification = gate.verify_kv_group_map_contract(
        heads=head_arr,
        kv_head=kv_head,
        num_attention_heads=num_attention_heads,
        num_key_value_heads=num_key_value_heads,
        num_key_value_groups=num_key_value_groups,
    )
    return {
        "kv_head": kv_head,
        "num_attention_heads": num_attention_heads,
        "num_key_value_heads": num_key_value_heads,
        "num_key_value_groups": num_key_value_groups,
        "kv_group_map_verified": bool(verification.get("kv_group_map_verified")),
        "gqa_grouped_rows_present": bool(int(verification.get("gqa_grouped_rows", 0)) > 0),
    }


def write_bundle(path: Path, rows: tuple, *, cap, gate, corrupt_decode_positions: bool) -> dict[str, Any]:
    q_rows, k_rows, v_rows, scale_rows, bias_rows, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, _bias_ok, _mask_seen, max_err = rows
    positions_arr = np.asarray(positions, dtype=np.int64)
    if corrupt_decode_positions:
        positions_arr = positions_arr.copy()
        for i, phase in enumerate(phases):
            if str(phase) == "decode_cached":
                positions_arr[i] = 0  # the old local-q-index bug: dense math still passes, row identity is wrong
    valid_key_len = np.asarray(valid_key_lens, dtype=np.int64)
    query_len = np.asarray(query_lens, dtype=np.int64)
    max_key_len = int(np.max(valid_key_len))
    q = np.stack(q_rows).astype(np.float64)
    k = cap._pad_3d_rows(k_rows, width=max_key_len).astype(np.float64)
    v = cap._pad_3d_rows(v_rows, width=max_key_len).astype(np.float64)
    scale = np.concatenate(scale_rows).astype(np.float64)
    bias = cap._pad_2d_rows(bias_rows, width=max_key_len, fill=cap.PUBLIC_MASK_SENTINEL).astype(np.float64)
    active_key_len = cap._active_key_lengths_from_bias(bias, valid_key_len)
    active_key_len_ok = cap._active_key_len_semantics_verified(bias, valid_key_len, active_key_len)
    ref = np.stack(refs).astype(np.float64)
    valid_key_len_ok = cap._valid_key_len_padding_verified(bias, valid_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(positions_arr, valid_key_len, query_len, phases, active_key_len)
    decode_present = any(str(p) == "decode_cached" for p in phases)
    prefill_present = any(str(p) == "prefill" for p in phases)
    kv = kv_group_fields(gate, heads)
    meta = {
        "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
        "public_pretrained_trace": True,
        "source_type": "public_pretrained_hf",
        "model_id": "org/model-public-placeholder",
        "model_revision": "8" * 40,
        "tokenizer_revision": "9" * 40,
        "code_revision": "not_applicable",
        "trust_remote_code": False,
        "weights_source": "reviewed-source-url-placeholder",
        "license": "reviewed-source-terms-placeholder",
        "schema": gate.PUBLIC_QKV_SCHEMA,
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_PATH),
        "config_sha256": "7" * 64,
        "generated_from_local_tiny_model": False,
        "uses_random_weights": False,
        "provenance_reviewed": True,
        "attention_backend": "eager",
        "attention_score_input_stage": gate.PUBLIC_SCORE_INPUT_STAGE,
        "attention_score_inputs_verified": True,
        "score_transform": gate.PUBLIC_SCORE_TRANSFORM,
        "probability_contract": gate.PUBLIC_PROBABILITY_CONTRACT,
        "probability_semantics_verified": True,
        "attention_probability_dtype": gate.PUBLIC_ATTENTION_PROBABILITY_DTYPE,
        "attention_dropout_p": 0.0,
        "attention_training_state": False,
        "dropout_applied": False,
        "attention_scale_verified": True,
        "score_bias_verified": True,
        "mask_challenge_exercised": bool(any(np.any(np.asarray(row) < -1.0e20) for row in bias_rows)),
        "attention_mask_backend_preserved": True,
        "custom_attention_backend_used": False,
        "capture_phase_contract": gate.PUBLIC_CAPTURE_PHASE_CONTRACT,
        "prefill_phase_present": bool(prefill_present),
        "decode_phase_present": bool(decode_present),
        "cache_decode_verified": bool(decode_present and any(int(q_len) == 1 and int(vkl) > 1 for q_len, vkl in zip(query_lens, valid_key_lens))),
        "valid_key_len_semantics_verified": bool(valid_key_len_ok),
        "active_key_len_contract": gate.PUBLIC_ACTIVE_KEY_CONTRACT,
        "active_key_len_semantics_verified": bool(active_key_len_ok),
        "kv_group_map_contract": gate.PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": bool(kv["kv_group_map_verified"]),
        "gqa_grouped_rows_present": bool(kv["gqa_grouped_rows_present"]),
        "position_contract": gate.PUBLIC_POSITION_CONTRACT,
        "absolute_position_verified": bool(absolute_position_ok),
        "decode_steps_requested": 2,
        "dense_reference_verified": True,
        "dense_reference_max_abs_error": float(max_err),
    }
    np.savez_compressed(
        path,
        q=q,
        k=k,
        v=v,
        regime=np.asarray(regimes),
        layer=np.asarray(layers, dtype=np.int64),
        head=np.asarray(heads, dtype=np.int64),
        kv_head=kv["kv_head"],
        num_attention_heads=kv["num_attention_heads"],
        num_key_value_heads=kv["num_key_value_heads"],
        num_key_value_groups=kv["num_key_value_groups"],
        position=positions_arr,
        prompt_id=np.asarray(prompt_ids, dtype=np.int64),
        capture_phase=np.asarray(phases),
        valid_key_len=valid_key_len,
        active_key_len=active_key_len.astype(np.int64),
        query_len=query_len,
        d_head=np.asarray([int(q.shape[-1])], dtype=np.int64),
        attention_scale=scale,
        score_bias=bias,
        dense_reference_output=ref,
        **{name: scalar(value) for name, value in meta.items()},
    )
    prov = dict(meta)
    # Simulate a false self-attestation attempt for the corrupt case: the NPZ and
    # manifest both claim the public contract, but the gate must recompute from
    # arrays and catch the local q_len position label.
    if corrupt_decode_positions:
        prov["absolute_position_verified"] = True
        with np.load(path, allow_pickle=False) as loaded:
            arrays = {name: loaded[name] for name in loaded.files}
        arrays["absolute_position_verified"] = scalar(True)
        np.savez_compressed(path, **arrays)
    prov["trace_npz_sha256"] = sha256_file(path)
    prov["d_head"] = int(q.shape[-1])
    prov["adapter"] = "hf_llama_eager_post_transform_attention_forward"
    return prov


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cap = load_module(CAPTURE_PATH, "cloudtainer_capture_absolute_position")
    gate = load_module(GATE_PATH, "cloudtainer_gate_absolute_position")

    prefill = rows_for(cap, make_case(q_len=4, key_len=4, seed=830831, causal=True), phase="prefill", policy="last_and_mid")
    decode = rows_for(cap, make_case(q_len=1, key_len=6, seed=830832, causal=False), phase="decode_cached", policy="all_tokens")
    rows = merge_rows(prefill, decode)
    q_rows, _k_rows, _v_rows, _scale_rows, bias_rows, _refs, _regimes, _layers, _heads, positions, _prompt_ids, phases, valid_key_lens, query_lens, bias_ok, mask_seen, max_err = rows
    valid_key_len_arr = np.asarray(valid_key_lens, dtype=np.int64)
    active_key_len_arr = cap._active_key_lengths_from_bias(cap._pad_2d_rows(bias_rows, width=int(np.max(valid_key_len_arr)), fill=cap.PUBLIC_MASK_SENTINEL), valid_key_len_arr)
    abs_ok = cap._absolute_position_semantics_verified(np.asarray(positions, dtype=np.int64), valid_key_len_arr, np.asarray(query_lens, dtype=np.int64), phases, active_key_len_arr)
    decode_position_pairs = [
        {"position": int(pos), "valid_key_len": int(vkl), "active_key_len": int(akl), "query_len": int(q_len)}
        for pos, vkl, akl, q_len, phase in zip(positions, valid_key_lens, active_key_len_arr, query_lens, phases)
        if str(phase) == "decode_cached"
    ]
    if not bias_ok or not mask_seen:
        errors.append("absolute-position fixture lost finite mask challenge")
    if not abs_ok:
        errors.append("good fixture did not satisfy absolute-position semantics")
    if float(max_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append(f"dense parity too large in absolute-position fixture: {max_err}")
    if not all(item["position"] == item["active_key_len"] - 1 and item["query_len"] == 1 for item in decode_position_pairs):
        errors.append("decode rows are not labeled at the absolute last active KV position")

    gate_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="ctml_abspos_audit_") as tmp:
        tmpdir = Path(tmp)
        good_npz = tmpdir / "absolute_good.npz"
        good_prov = tmpdir / "absolute_good.provenance.json"
        good_manifest = write_bundle(good_npz, rows, cap=cap, gate=gate, corrupt_decode_positions=False)
        good_prov.write_text(json.dumps(good_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        good_validation = gate.validate_public_trace_provenance(good_prov, good_npz)
        good_score = good_validation.get("score_contract_verification") or {}
        gate_results["absolute_position_bundle"] = {
            "accepted": bool(good_validation.get("accepted")),
            "status": good_validation.get("status"),
            "errors": good_validation.get("errors", []),
            "position_contract_verified": good_score.get("position_contract_verified"),
            "decode_position_rows": good_score.get("decode_position_rows"),
        }
        if good_validation.get("accepted") is not True:
            errors.append("gate did not accept the absolute-position mixed bundle")

        bad_npz = tmpdir / "local_position_bad.npz"
        bad_prov = tmpdir / "local_position_bad.provenance.json"
        bad_manifest = write_bundle(bad_npz, rows, cap=cap, gate=gate, corrupt_decode_positions=True)
        bad_prov.write_text(json.dumps(bad_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_validation = gate.validate_public_trace_provenance(bad_prov, bad_npz)
        bad_errors = bad_validation.get("errors", [])
        bad_score = bad_validation.get("score_contract_verification") or {}
        gate_results["local_decode_position_bundle"] = {
            "accepted": bool(bad_validation.get("accepted")),
            "status": bad_validation.get("status"),
            "errors": bad_errors,
            "dense_reference_max_abs_error": bad_score.get("computed_dense_reference_max_abs_error"),
            "position_contract_verified": bad_score.get("position_contract_verified"),
        }
        if bad_validation.get("accepted") is True:
            errors.append("gate accepted a cached-decode bundle with local q_len position labels")
        if not any("position" in str(e).lower() for e in bad_errors):
            errors.append("local-position rejection did not mention position semantics")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_absolute_position_audit",
        "generated_at": META.get("generated_at"),
        "status": "fail" if errors else "pass_with_blockers",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": {
            "mixed_rows_checked": int(len(q_rows)),
            "absolute_position_semantics_verified": bool(abs_ok),
            "decode_position_pairs": decode_position_pairs,
            "temporary_absolute_bundle_accepted_by_gate": bool(gate_results.get("absolute_position_bundle", {}).get("accepted")),
            "temporary_local_position_bundle_rejected_by_gate": not bool(gate_results.get("local_decode_position_bundle", {}).get("accepted")),
            "dense_math_same_but_position_label_rejected": bool(
                not gate_results.get("local_decode_position_bundle", {}).get("accepted")
                and gate_results.get("local_decode_position_bundle", {}).get("dense_reference_max_abs_error", 1.0) is not None
                and float(gate_results.get("local_decode_position_bundle", {}).get("dense_reference_max_abs_error", 1.0)) <= getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5)
            ),
        },
        "gate_results": gate_results,
        "research_sources": [
            {
                "url": "https://huggingface.co/docs/transformers/en/cache_explanation",
                "finding": "Cached attention combines current and past KV so decode rows have a short query and a longer live KV cache; row identity must refer to the live cache position.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/kv_cache",
                "finding": "DynamicCache grows during generation, while static/sliding caches can alter live-length behavior; trace metadata must preserve row position and valid length explicitly.",
            },
            {
                "url": "https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/disagg-serving.md",
                "finding": "Production serving distinguishes context/prefill and generation/decode phases and tracks KV exchange/request identity, raising the bar for phase/position provenance.",
            },
        ],
        "blockers": [
            "actual_public_pretrained_prefill_plus_cached_decode_bundle_missing",
            "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "rev0083 prevents a dense-parity blind spot: cached-decode rows must export absolute key positions. "
            "The gate now rejects a bundle whose Q/K/V/scale/bias/reference math is still correct but whose decode row is labeled with the local q_len=1 index. "
            "This is row-identity hardening, not public-model evidence."
        ),
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_ABSOLUTE_POSITION_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# Public trace absolute-position audit — {REV}",
        "",
        f"**Status:** {report['status']}",
        "",
        report["interpretation"],
        "",
        "## What was exercised",
        "",
        f"- mixed rows checked: `{report['summary']['mixed_rows_checked']}`",
        f"- absolute position semantics verified: `{report['summary']['absolute_position_semantics_verified']}`",
        f"- gate accepts temporary absolute-position bundle: `{report['summary']['temporary_absolute_bundle_accepted_by_gate']}`",
        f"- gate rejects local decode-position bundle: `{report['summary']['temporary_local_position_bundle_rejected_by_gate']}`",
        f"- dense math same but position label rejected: `{report['summary']['dense_math_same_but_position_label_rejected']}`",
        "",
        "## Remaining blockers",
        "",
    ]
    lines.extend(f"- `{b}`" for b in report["blockers"])
    lines.extend([
        "",
        "## Research inputs",
        "",
        "- Hugging Face cache explanation documentation",
        "- Hugging Face KV cache documentation",
        "- TensorRT-LLM disaggregated serving documentation",
        "",
    ])
    (OUT / f"{REVUP}_PUBLIC_TRACE_ABSOLUTE_POSITION_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
