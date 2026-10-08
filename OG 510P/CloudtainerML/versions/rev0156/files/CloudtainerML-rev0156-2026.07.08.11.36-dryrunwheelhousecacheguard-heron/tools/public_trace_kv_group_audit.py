#!/usr/bin/env python3
"""Audit explicit GQA/MQA query-head to KV-head ownership in public traces.

rev0085 fixes a cost/accounting blind spot: dense Q/K/V parity can pass while a
trace labels compact KV-head ownership incorrectly.  Llama-family grouped-query
attention stores fewer K/V heads than query heads and logically expands K/V per
query group during attention.  A public trace therefore needs an explicit
query-head -> compact-KV-head map so selector and cache accounting do not count
per-query row copies as independent KV-cache storage.
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
REV = META.get("revision", "rev0085")
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


def make_gqa_case(*, q_len: int, key_len: int, seed: int, causal: bool, active_len: int | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch, heads, kv_heads, d_head, d_value = 1, 4, 2, 6, 5
    groups = heads // kv_heads
    q = rng.normal(0.0, 0.35, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scaling = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    if causal:
        for pos in range(q_len):
            if pos + 1 < key_len:
                mask[:, :, pos, pos + 1 :] = -np.inf
    if active_len is not None:
        if active_len <= 0 or active_len > key_len:
            raise ValueError("active_len must be within the physical key width")
        mask[:, :, :, active_len:] = -np.inf
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            additive = np.where(np.isneginf(mask[b, 0, pos]), -1.0e30, mask[b, 0, pos])
            for h in range(heads):
                kv_head = h // groups
                scores = (k[b, kv_head] @ q[b, h, pos]) * scaling + additive
                out[b, pos, h] = softmax(scores) @ v[b, kv_head]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling, "heads": heads, "kv_heads": kv_heads, "groups": groups}


def rows_for(cap, case: dict[str, Any], *, phase: str, policy: str, query_start_position: int | None = None) -> tuple:
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
        max_remaining=128,
        num_key_value_groups=case["groups"],
        capture_phase=phase,
        query_start_position=query_start_position,
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


def kv_group_arrays(gate, heads: list[int] | np.ndarray, *, forge_map: bool) -> dict[str, Any]:
    head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
    row_count = int(head_arr.shape[0])
    num_attention_heads_value = 4
    num_key_value_heads_value = 2
    groups_value = num_attention_heads_value // num_key_value_heads_value
    kv_head = (head_arr // groups_value).astype(np.int64)
    if forge_map:
        # Same dense row tensors, wrong compact KV owner for heads 2 and 3.
        # This recreates the dangerous case: math parity still passes, but cache
        # ownership/cost accounting is false.
        kv_head = kv_head.copy()
        kv_head[head_arr >= 2] = 0
    num_attention_heads = np.full((row_count,), num_attention_heads_value, dtype=np.int64)
    num_key_value_heads = np.full((row_count,), num_key_value_heads_value, dtype=np.int64)
    num_key_value_groups = np.full((row_count,), groups_value, dtype=np.int64)
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
        "contract": verification,
        "kv_group_map_verified": bool(verification.get("kv_group_map_verified")),
        "gqa_grouped_rows_present": bool(int(verification.get("gqa_grouped_rows", 0)) > 0 or groups_value > 1),
    }


def write_bundle(path: Path, rows: tuple, *, cap, gate, forge_map: bool) -> dict[str, Any]:
    q_rows, k_rows, v_rows, scale_rows, bias_rows, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, _bias_ok, _mask_seen, max_err = rows
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
    positions_arr = np.asarray(positions, dtype=np.int64)
    ref = np.stack(refs).astype(np.float64)
    valid_key_len_ok = cap._valid_key_len_padding_verified(bias, valid_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(positions_arr, valid_key_len, query_len, phases, active_key_len)
    kv = kv_group_arrays(gate, heads, forge_map=forge_map)
    decode_present = any(str(p) == "decode_cached" for p in phases)
    prefill_present = any(str(p) == "prefill" for p in phases)
    meta = {
        "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
        "public_pretrained_trace": True,
        "source_type": "public_pretrained_hf",
        "model_id": "org/model-public-placeholder",
        "model_revision": "1" * 40,
        "tokenizer_revision": "2" * 40,
        "code_revision": "not_applicable",
        "trust_remote_code": False,
        "weights_source": "reviewed-source-url-placeholder",
        "license": "reviewed-source-terms-placeholder",
        "schema": gate.PUBLIC_QKV_SCHEMA,
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_PATH),
        "config_sha256": "3" * 64,
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
    if forge_map:
        # Simulate an unsafe self-attestation attempt: the bundle claims the
        # contract, but the row-level kv_head array is forged.  The public gate
        # must recompute from arrays rather than trust this boolean.
        meta["kv_group_map_verified"] = True
        meta["gqa_grouped_rows_present"] = True
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
    prov["trace_npz_sha256"] = sha256_file(path)
    prov["d_head"] = int(q.shape[-1])
    prov["adapter"] = "hf_llama_eager_post_transform_attention_forward"
    prov["kv_head_unique_serialized"] = sorted({int(x) for x in np.asarray(kv["kv_head"]).tolist()})
    prov["num_attention_heads_min"] = int(np.min(kv["num_attention_heads"]))
    prov["num_key_value_heads_min"] = int(np.min(kv["num_key_value_heads"]))
    prov["num_key_value_groups_min"] = int(np.min(kv["num_key_value_groups"]))
    prov["forged_map"] = bool(forge_map)
    return prov


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cap = load_module(CAPTURE_PATH, "cloudtainer_capture_kv_group")
    gate = load_module(GATE_PATH, "cloudtainer_gate_kv_group")

    prefill_case = make_gqa_case(q_len=4, key_len=4, seed=850841, causal=True)
    decode_case = make_gqa_case(q_len=1, key_len=6, seed=850842, causal=False, active_len=5)
    prefill = rows_for(cap, prefill_case, phase="prefill", policy="last_and_mid")
    decode = rows_for(cap, decode_case, phase="decode_cached", policy="all_tokens", query_start_position=4)
    rows = merge_rows(prefill, decode)

    q_rows, _k_rows, _v_rows, _scale_rows, bias_rows, _refs, _regimes, _layers, heads, positions, _prompt_ids, phases, valid_key_lens, query_lens, bias_ok, mask_seen, max_err = rows
    head_arr = np.asarray(heads, dtype=np.int64)
    expected_kv_head = (head_arr // 2).astype(np.int64)
    groups_exercised = sorted({(int(h), int(kv)) for h, kv in zip(head_arr.tolist(), expected_kv_head.tolist())})
    if not bias_ok or not mask_seen:
        errors.append("GQA fixture lost finite mask challenge")
    if float(max_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append(f"dense parity too large in GQA fixture: {max_err}")
    if set(expected_kv_head.tolist()) != {0, 1}:
        errors.append("fixture did not exercise both compact KV heads")
    if not any(str(p) == "decode_cached" for p in phases) or not any(str(p) == "prefill" for p in phases):
        errors.append("fixture did not include both prefill and cached-decode rows")

    gate_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="ctml_kv_group_audit_") as tmp:
        tmpdir = Path(tmp)
        good_npz = tmpdir / "kv_group_good.npz"
        good_prov = tmpdir / "kv_group_good.provenance.json"
        good_manifest = write_bundle(good_npz, rows, cap=cap, gate=gate, forge_map=False)
        good_prov.write_text(json.dumps(good_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        good_validation = gate.validate_public_trace_provenance(good_prov, good_npz)
        good_score = good_validation.get("score_contract_verification") or {}
        gate_results["gqa_bundle"] = {
            "accepted": bool(good_validation.get("accepted")),
            "status": good_validation.get("status"),
            "errors": good_validation.get("errors", []),
            "kv_group_map_verified": good_score.get("kv_group_map_verified"),
            "gqa_grouped_rows": good_score.get("gqa_grouped_rows"),
            "dense_reference_max_abs_error": good_score.get("computed_dense_reference_max_abs_error"),
        }
        if good_validation.get("accepted") is not True:
            errors.append("gate did not accept the correctly mapped GQA bundle")

        bad_npz = tmpdir / "kv_group_forged_bad.npz"
        bad_prov = tmpdir / "kv_group_forged_bad.provenance.json"
        bad_manifest = write_bundle(bad_npz, rows, cap=cap, gate=gate, forge_map=True)
        bad_prov.write_text(json.dumps(bad_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_validation = gate.validate_public_trace_provenance(bad_prov, bad_npz)
        bad_score = bad_validation.get("score_contract_verification") or {}
        bad_errors = bad_validation.get("errors", [])
        gate_results["forged_kv_head_bundle"] = {
            "accepted": bool(bad_validation.get("accepted")),
            "status": bad_validation.get("status"),
            "errors": bad_errors,
            "kv_group_map_verified": bad_score.get("kv_group_map_verified"),
            "kv_group_map_errors": bad_score.get("kv_group_map_errors"),
            "dense_reference_max_abs_error": bad_score.get("computed_dense_reference_max_abs_error"),
        }
        if bad_validation.get("accepted") is True:
            errors.append("gate accepted a forged query-head to KV-head map")
        if not any("kv" in str(e).lower() or "group" in str(e).lower() for e in bad_errors):
            errors.append("forged KV-map rejection did not mention KV/group semantics")

    dense_same_but_kv_rejected = bool(
        not gate_results.get("forged_kv_head_bundle", {}).get("accepted")
        and gate_results.get("forged_kv_head_bundle", {}).get("dense_reference_max_abs_error") is not None
        and float(gate_results.get("forged_kv_head_bundle", {}).get("dense_reference_max_abs_error")) <= getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5)
    )

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_kv_group_audit",
        "generated_at": META.get("generated_at"),
        "status": "fail" if errors else "pass_with_blockers",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": {
            "mixed_rows_checked": int(len(q_rows)),
            "head_to_kv_groups_exercised": [{"head": h, "kv_head": kv} for h, kv in groups_exercised],
            "gqa_heads": 4,
            "compact_kv_heads": 2,
            "query_heads_per_kv_head": 2,
            "temporary_gqa_bundle_accepted_by_gate": bool(gate_results.get("gqa_bundle", {}).get("accepted")),
            "temporary_forged_kv_map_rejected_by_gate": not bool(gate_results.get("forged_kv_head_bundle", {}).get("accepted")),
            "dense_math_same_but_kv_map_rejected": dense_same_but_kv_rejected,
        },
        "gate_results": gate_results,
        "research_sources": [
            {
                "url": "https://huggingface.co/docs/transformers/en/model_doc/llama2",
                "finding": "The Llama configuration uses num_key_value_heads to distinguish MHA, MQA, and GQA.",
            },
            {
                "url": "https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py",
                "finding": "Transformers' Llama eager attention applies repeat_kv to expand compact K/V heads to query heads before scoring.",
            },
            {
                "url": "https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html",
                "finding": "PyTorch SDPA exposes enable_gqa, making grouped KV semantics a current runtime concern rather than a historical notation detail.",
            },
            {
                "url": "https://dev-discuss.pytorch.org/t/added-grouped-query-attention-to-scaled-dot-product-attention-api/2340",
                "finding": "PyTorch's GQA discussion distinguishes materialized repeat_interleave behavior from optimized kernels, so trace/cost accounting should represent KV ownership instead of assuming duplicated storage.",
            },
        ],
        "blockers": [
            "no_actual_public_pretrained_hf_checkpoint_trace_in_this_capsule",
            "gpu_fused_kernel_timing_still_missing",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "rev0085 moves the public trace gate from dense math alone toward cache-ownership semantics: a row bundle can now pass only if each query-head row carries a verified compact KV-head owner and head-count/group-size metadata. "
            "The audit rejects a forged GQA map even though the recomputed dense attention output is unchanged, which protects later sparse/cost claims from overcounting duplicated per-query K/V rows as independent KV-cache storage."
        ),
    }
    out_json = OUT / f"{REVUP}_PUBLIC_TRACE_KV_GROUP_AUDIT.json"
    out_md = OUT / f"{REVUP}_PUBLIC_TRACE_KV_GROUP_AUDIT.md"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(
        f"# Public trace KV group audit — {REV}\n\n"
        f"**Status:** {report['status']}\n\n"
        f"{report['interpretation']}\n\n"
        f"Rows checked: {report['summary']['mixed_rows_checked']}\n\n"
        f"Head→KV groups exercised: {report['summary']['head_to_kv_groups_exercised']}\n\n"
        f"Correct GQA bundle accepted: {report['summary']['temporary_gqa_bundle_accepted_by_gate']}\n\n"
        f"Forged KV-map bundle rejected while dense math still matched: {report['summary']['dense_math_same_but_kv_map_rejected']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
