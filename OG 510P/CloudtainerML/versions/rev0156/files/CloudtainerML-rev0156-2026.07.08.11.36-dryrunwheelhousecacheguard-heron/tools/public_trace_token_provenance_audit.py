#!/usr/bin/env python3
"""Audit prompt/token provenance semantics in public cached-decode traces.

rev0089 closes an execution-risk gap: a Q/K/V trace can have correct dense
attention parity, correct active-key/position/RoPE/KV-group semantics, and still
be unreplayable because the exact tokenizer inputs are not bound to each row.
This audit builds a dense-parity-valid prefill+cached-decode bundle and proves
the gate accepts its prompt input_ids/attention_mask digests, then forges only
the prompt token-count boundary and proves the gate rejects it without changing
Q/K/V/reference tensors.
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
REV = META.get("revision", "rev0091")
REVUP = str(REV).upper()
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
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            additive = np.where(np.isneginf(mask[b, 0, pos]), -1.0e30, mask[b, 0, pos])
            for h in range(heads):
                kv_head = h // groups
                scores = (k[b, kv_head] @ q[b, h, pos]) * scaling + additive
                out[b, pos, h] = softmax(scores) @ v[b, kv_head]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling, "groups": groups}


def rows_for(cap, case: dict[str, Any], *, phase: str, rotary_ids: np.ndarray, query_start_position: int = 0) -> tuple[tuple, list[int]]:
    rotary_out: list[int] = []
    rows = cap._rows_from_attention_capture(
        q=case["q"],
        k=case["k"],
        v=case["v"],
        out=case["out"],
        attention_mask=case["mask"],
        scaling=case["scaling"],
        layer_id=0,
        prompt_index=0,
        position_policy="all_tokens",
        max_remaining=128,
        num_key_value_groups=case["groups"],
        capture_phase=phase,
        query_start_position=query_start_position,
        rotary_position_ids=rotary_ids,
        rotary_position_out=rotary_out,
    )
    return rows, rotary_out


def merge_rows(a: tuple, b: tuple) -> tuple:
    out = list(a)
    for i in range(14):
        out[i] = out[i] + b[i]
    out[14] = bool(out[14] and b[14])
    out[15] = bool(out[15] or b[15])
    out[16] = max(float(out[16]), float(b[16]))
    return tuple(out)


def kv_fields(gate, heads: list[int] | np.ndarray) -> dict[str, np.ndarray | bool]:
    head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
    row_count = int(head_arr.size)
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


def write_bundle(path: Path, *, cap, gate, forge_prompt_count: bool) -> None:
    prefill = make_case(q_len=3, key_len=3, seed=8801, causal=True)
    decode = make_case(q_len=1, key_len=4, seed=8802, causal=False)
    pre_rows, pre_rope = rows_for(cap, prefill, phase="prefill", rotary_ids=np.asarray([[0, 1, 2]], dtype=np.int64))
    dec_rows, dec_rope = rows_for(cap, decode, phase="decode_cached", rotary_ids=np.asarray([[3]], dtype=np.int64), query_start_position=3)
    rows = merge_rows(pre_rows, dec_rows)
    rotary_ids = pre_rope + dec_rope
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
    kv = kv_fields(gate, heads)
    prompt_token_count = np.asarray([99 if forge_prompt_count else 3], dtype=np.int64)
    prompt_ids_arr = np.asarray(prompt_ids, dtype=np.int64)
    positions_arr = np.asarray(positions, dtype=np.int64)
    phases_arr = np.asarray(phases)
    prompt_input_ids = np.asarray([[101, 102, 103]], dtype=np.int64)
    prompt_attention_mask = np.asarray([[1, 1, 1]], dtype=np.int64)
    prompt_input_ids_sha256 = np.asarray([cap.sha256_int_array(prompt_input_ids)])
    prompt_attention_mask_sha256 = np.asarray([cap.sha256_int_array(prompt_attention_mask)])
    prompt_text_sha256 = np.asarray([cap.sha256_text("token provenance audit prompt")])
    tokenization_settings = {
        "contract": gate.PUBLIC_PROMPT_MANIFEST_CONTRACT,
        "call": {
            "add_special_tokens": True,
            "padding": False,
            "truncation": False,
            "return_attention_mask": True,
            "return_tensors": "pt",
            "chat_template_applied": False,
        },
        "observed_tokenizer": {"class": "AuditTokenizer", "is_fast": False, "padding_side": "right", "truncation_side": "right"},
    }
    tokenization_settings_json = cap._json_canonical_text(tokenization_settings)
    tokenization_settings_sha256 = cap.sha256_text(tokenization_settings_json)
    prompt_manifest = {
        "contract": gate.PUBLIC_PROMPT_MANIFEST_CONTRACT,
        "tokenization_settings": tokenization_settings,
        "prompt_count": 1,
        "prompts": [{
            "prompt_index": 0,
            "text": "token provenance audit prompt",
            "text_sha256": str(prompt_text_sha256[0]),
            "input_ids_sha256": str(prompt_input_ids_sha256[0]),
            "attention_mask_sha256": str(prompt_attention_mask_sha256[0]),
            "token_count": int(prompt_token_count[0]),
            "attention_mask_sum": 3,
        }],
    }
    prompt_manifest_json = cap._json_canonical_text(prompt_manifest)
    prompt_manifest_sha256 = cap.sha256_text(prompt_manifest_json)
    generated_sequence = np.asarray([[101, 102, 103, 201, 202]], dtype=np.int64)
    generated_new_token_ids = generated_sequence[:, 3:]
    generated_sequence_sha256 = np.asarray([cap.sha256_int_array(generated_sequence)])
    generated_new_token_ids_sha256 = np.asarray([cap.sha256_int_array(generated_new_token_ids)])
    generated_new_token_count = np.asarray([int(generated_new_token_ids.shape[-1])], dtype=np.int64)
    generated_sequence_token_count = np.asarray([int(generated_sequence.shape[-1])], dtype=np.int64)
    generation_prompt_prefix_verified = np.asarray([True])
    generation_settings = {
        "contract": gate.PUBLIC_GENERATION_DETERMINISM_CONTRACT,
        "strategy": "greedy",
        "do_sample": False,
        "num_beams": 1,
        "num_return_sequences": 1,
        "max_new_tokens": 2,
        "min_new_tokens": 2,
        "use_cache": True,
        "cache_implementation_contract": gate.PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        "cache_implementation": gate.PUBLIC_REQUIRED_CACHE_IMPLEMENTATION,
        "cache_implementation_source": "explicit_generate_argument",
        "cache_config": None,
        "sampling_disabled": True,
        "exact_new_token_count_required": True,
        "beam_search_disabled": True,
        "temperature_effective": "ignored_do_sample_false",
        "top_k_effective": "ignored_do_sample_false",
        "top_p_effective": "ignored_do_sample_false",
        "position_policy": "all_tokens",
        "pad_token_id": None,
        "eos_token_id_sha256": cap.sha256_json(None),
    }
    generation_config_json = cap._json_canonical_text(generation_settings)
    generation_config_sha256 = cap.sha256_text(generation_config_json)
    generation_determinism_check = gate.verify_generation_determinism_contract(
        generation_config_json=np.asarray([generation_config_json]),
        generation_config_sha256=generation_config_sha256,
        generation_determinism_contract=gate.PUBLIC_GENERATION_DETERMINISM_CONTRACT,
        generation_determinism_verified=True,
        generation_strategy="greedy",
        generation_do_sample=False,
        generation_use_cache=True,
        cache_implementation_contract=gate.PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        generation_cache_implementation=gate.PUBLIC_REQUIRED_CACHE_IMPLEMENTATION,
        generation_cache_implementation_source="explicit_generate_argument",
        generation_cache_config_present=False,
        generation_num_beams=1,
        generation_num_return_sequences=1,
        generation_max_new_tokens=2,
        generation_min_new_tokens=2,
        generation_sampling_disabled=True,
        generation_exact_new_tokens_required=True,
        decode_steps_requested=2,
    )
    token_check = gate.verify_token_provenance_contract(
        prompt_id=prompt_ids_arr,
        position=positions_arr,
        capture_phase=phases_arr,
        prompt_count=1,
        prompt_token_count=prompt_token_count,
        prompt_input_ids_sha256=prompt_input_ids_sha256,
        prompt_attention_mask_sha256=prompt_attention_mask_sha256,
        prompt_text_sha256=prompt_text_sha256,
        decode_steps_requested=2,
    )
    generation_check = gate.verify_generation_token_contract(
        prompt_id=prompt_ids_arr,
        position=positions_arr,
        capture_phase=phases_arr,
        prompt_token_count=prompt_token_count,
        generated_sequence_sha256=generated_sequence_sha256,
        generated_new_token_ids_sha256=generated_new_token_ids_sha256,
        generated_new_token_count=generated_new_token_count,
        generated_sequence_token_count=generated_sequence_token_count,
        generation_prompt_prefix_verified=generation_prompt_prefix_verified,
        decode_steps_requested=2,
    )
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
        rotary_position_id=np.asarray(rotary_ids, dtype=np.int64),
        prompt_id=prompt_ids_arr,
        token_provenance_contract=np.asarray([gate.PUBLIC_TOKEN_PROVENANCE_CONTRACT]),
        token_provenance_verified=np.asarray([True]),
        prompt_count=np.asarray([1], dtype=np.int64),
        prompt_manifest_contract=np.asarray([gate.PUBLIC_PROMPT_MANIFEST_CONTRACT]),
        prompt_manifest_json=np.asarray([prompt_manifest_json]),
        prompt_manifest_sha256=np.asarray([prompt_manifest_sha256]),
        tokenization_settings_json=np.asarray([tokenization_settings_json]),
        tokenization_settings_sha256=np.asarray([tokenization_settings_sha256]),
        tokenization_add_special_tokens=np.asarray([True]),
        tokenization_padding=np.asarray(["false"]),
        tokenization_truncation=np.asarray(["false"]),
        tokenization_return_attention_mask=np.asarray([True]),
        tokenization_return_tensors=np.asarray(["pt"]),
        chat_template_applied=np.asarray([False]),
        tokenizer_class=np.asarray(["AuditTokenizer"]),
        tokenizer_is_fast=np.asarray([False]),
        tokenizer_padding_side=np.asarray(["right"]),
        tokenizer_truncation_side=np.asarray(["right"]),
        prompt_token_count=prompt_token_count,
        prompt_attention_mask_sum=np.asarray([3], dtype=np.int64),
        prompt_input_ids_sha256=prompt_input_ids_sha256,
        prompt_attention_mask_sha256=prompt_attention_mask_sha256,
        prompt_text_sha256=prompt_text_sha256,
        prompt_token_count_min=np.asarray([int(np.min(prompt_token_count))], dtype=np.int64),
        prompt_token_count_max=np.asarray([int(np.max(prompt_token_count))], dtype=np.int64),
        generation_config_json=np.asarray([generation_config_json]),
        generation_config_sha256=np.asarray([generation_config_sha256]),
        generation_determinism_contract=np.asarray([gate.PUBLIC_GENERATION_DETERMINISM_CONTRACT]),
        generation_determinism_verified=np.asarray([bool(generation_determinism_check.get("generation_determinism_verified"))]),
        generation_strategy=np.asarray(["greedy"]),
        generation_do_sample=np.asarray([False]),
        generation_use_cache=np.asarray([True]),
        cache_implementation_contract=np.asarray([gate.PUBLIC_CACHE_IMPLEMENTATION_CONTRACT]),
        generation_cache_implementation=np.asarray([gate.PUBLIC_REQUIRED_CACHE_IMPLEMENTATION]),
        generation_cache_implementation_source=np.asarray(["explicit_generate_argument"]),
        generation_cache_config_present=np.asarray([False]),
        generation_num_beams=np.asarray([1], dtype=np.int64),
        generation_num_return_sequences=np.asarray([1], dtype=np.int64),
        generation_max_new_tokens=np.asarray([2], dtype=np.int64),
        generation_min_new_tokens=np.asarray([2], dtype=np.int64),
        generation_sampling_disabled=np.asarray([True]),
        generation_exact_new_tokens_required=np.asarray([True]),
        generation_token_contract=np.asarray([gate.PUBLIC_GENERATION_TOKEN_CONTRACT]),
        generation_token_provenance_verified=np.asarray([True]),
        generated_sequence_sha256=generated_sequence_sha256,
        generated_new_token_ids_sha256=generated_new_token_ids_sha256,
        generated_new_token_count=generated_new_token_count,
        generated_new_token_count_min=np.asarray([int(np.min(generated_new_token_count))], dtype=np.int64),
        generated_new_token_count_max=np.asarray([int(np.max(generated_new_token_count))], dtype=np.int64),
        generated_new_token_exact_count_verified=np.asarray([bool(generation_check.get("generated_new_token_exact_count_verified"))]),
        generated_sequence_token_count=generated_sequence_token_count,
        generation_prompt_prefix_verified=generation_prompt_prefix_verified,
        capture_phase=phases_arr,
        valid_key_len=valid_key_len,
        active_key_len=active_key_len.astype(np.int64),
        query_len=query_len,
        d_head=np.asarray([int(q.shape[-1])], dtype=np.int64),
        attention_scale=scale,
        score_bias=bias,
        dense_reference_output=np.stack(refs).astype(np.float64),
        trace_claim_version=np.asarray([gate.PUBLIC_TRACE_CLAIM_VERSION]),
        public_pretrained_trace=np.asarray([True]),
        source_type=np.asarray(["public_pretrained_hf"]),
        model_id=np.asarray(["org/model-public-audit"]),
        model_revision=np.asarray(["a" * 40]),
        tokenizer_revision=np.asarray(["b" * 40]),
        code_revision=np.asarray(["not_applicable"]),
        trust_remote_code=np.asarray([False]),
        weights_source=np.asarray(["reviewed source terms"]),
        license=np.asarray(["reviewed license"]),
        schema=np.asarray([gate.PUBLIC_QKV_SCHEMA]),
        capture_tool=np.asarray(["experiments/public_trace_capture/hf_attention_trace_capture.py"]),
        capture_tool_sha256=np.asarray([sha256_file(CAPTURE_PATH)]),
        config_sha256=np.asarray(["c" * 64]),
        generated_from_local_tiny_model=np.asarray([False]),
        uses_random_weights=np.asarray([False]),
        provenance_reviewed=np.asarray([True]),
        attention_backend=np.asarray(["eager"]),
        attention_score_input_stage=np.asarray([gate.PUBLIC_SCORE_INPUT_STAGE]),
        attention_score_inputs_verified=np.asarray([True]),
        score_transform=np.asarray([gate.PUBLIC_SCORE_TRANSFORM]),
        probability_contract=np.asarray([gate.PUBLIC_PROBABILITY_CONTRACT]),
        probability_semantics_verified=np.asarray([True]),
        attention_probability_dtype=np.asarray([gate.PUBLIC_ATTENTION_PROBABILITY_DTYPE]),
        attention_dropout_p=np.asarray([0.0], dtype=np.float64),
        attention_training_state=np.asarray([False]),
        dropout_applied=np.asarray([False]),
        attention_scale_verified=np.asarray([True]),
        score_bias_verified=np.asarray([True]),
        mask_challenge_exercised=np.asarray([True]),
        attention_mask_backend_preserved=np.asarray([True]),
        custom_attention_backend_used=np.asarray([False]),
        capture_phase_contract=np.asarray([gate.PUBLIC_CAPTURE_PHASE_CONTRACT]),
        prefill_phase_present=np.asarray([True]),
        decode_phase_present=np.asarray([True]),
        cache_decode_verified=np.asarray([True]),
        valid_key_len_semantics_verified=np.asarray([True]),
        active_key_len_contract=np.asarray([gate.PUBLIC_ACTIVE_KEY_CONTRACT]),
        active_key_len_semantics_verified=np.asarray([True]),
        kv_group_map_contract=np.asarray([gate.PUBLIC_KV_GROUP_CONTRACT]),
        kv_group_map_verified=np.asarray([bool(kv["kv_group_map_verified"])]),
        gqa_grouped_rows_present=np.asarray([bool(kv["gqa_grouped_rows_present"])]),
        position_contract=np.asarray([gate.PUBLIC_POSITION_CONTRACT]),
        absolute_position_verified=np.asarray([True]),
        rotary_position_contract=np.asarray([gate.PUBLIC_ROTARY_POSITION_CONTRACT]),
        rotary_position_ids_verified=np.asarray([True]),
        rotary_position_ids_present_call_count=np.asarray([2], dtype=np.int64),
        decode_steps_requested=np.asarray([2], dtype=np.int64),
        dense_reference_verified=np.asarray([True]),
        dense_reference_max_abs_error=np.asarray([float(max_err)], dtype=np.float64),
        token_contract_precomputed=np.asarray([bool(token_check.get("token_provenance_verified"))]),
        generation_contract_precomputed=np.asarray([bool(generation_check.get("generation_token_provenance_verified"))]),
        generation_determinism_contract_precomputed=np.asarray([bool(generation_determinism_check.get("generation_determinism_verified"))]),
        runtime_provenance_contract=np.asarray([gate.PUBLIC_RUNTIME_PROVENANCE_CONTRACT]),
        requested_torch_dtype=np.asarray(["float32"]),
        resolved_torch_dtype=np.asarray(["torch.float32"]),
        requested_device_policy=np.asarray(["cpu"]),
        actual_primary_device=np.asarray(["cpu"]),
        model_parameter_dtype_set=np.asarray([json.dumps(["torch.float32"])]),
        model_device_set=np.asarray([json.dumps(["cpu"])]),
        model_parameter_tensor_count=np.asarray([42], dtype=np.int64),
        cuda_available=np.asarray([False]),
        cuda_device_count=np.asarray([0], dtype=np.int64),
        cuda_device_name=np.asarray(["not_available"]),
        cuda_device_capability=np.asarray(["not_available"]),
        timing_clock_contract=np.asarray([gate.PUBLIC_TIMING_CLOCK_CONTRACT]),
        timing_cpu_perf_counter_recorded=np.asarray([True]),
        timing_cuda_synchronized=np.asarray([False]),
        timing_cuda_event_recorded=np.asarray([False]),
        capture_elapsed_seconds=np.asarray([0.01], dtype=np.float64),
        named_hardware_timing_measured=np.asarray([False]),
        runtime_provenance_verified=np.asarray([True]),
    )


def main() -> int:
    cap = load_module(CAPTURE_PATH, "rev0091_capture_for_token_provenance_audit")
    gate = load_module(GATE_PATH, "rev0091_gate_for_token_provenance_audit")
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="cloudtainer_token_prov_") as tmp:
        tmpdir = Path(tmp)
        good = tmpdir / "good_token_provenance.npz"
        forged = tmpdir / "forged_prompt_count.npz"
        write_bundle(good, cap=cap, gate=gate, forge_prompt_count=False)
        write_bundle(forged, cap=cap, gate=gate, forge_prompt_count=True)
        good_contract = gate.verify_qkv_score_contract(good)
        try:
            forged_contract = gate.verify_qkv_score_contract(forged)
            forged_rejected = False
            forged_error = "forged bundle unexpectedly passed"
        except Exception as exc:
            forged_contract = None
            forged_rejected = True
            forged_error = str(exc)
        if good_contract.get("token_provenance_verified") is not True:
            errors.append("good bundle did not verify token provenance")
        if good_contract.get("generation_token_provenance_verified") is not True:
            errors.append("good bundle did not verify generated-token provenance")
        if good_contract.get("computed_dense_reference_max_abs_error", 1.0) > gate.PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            errors.append("good bundle dense parity failed")
        if not forged_rejected:
            errors.append("forged prompt-token boundary was not rejected")
        report = {
            "project": "CloudtainerML",
            "revision": REV,
            "report": "public_trace_token_provenance_audit",
            "status": "pass_with_blockers" if not errors else "fail",
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            "token_provenance_contract": gate.PUBLIC_TOKEN_PROVENANCE_CONTRACT,
            "generation_token_contract": gate.PUBLIC_GENERATION_TOKEN_CONTRACT,
            "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
            "good_bundle_verified": bool(good_contract.get("token_provenance_verified")),
            "good_generation_token_verified": bool(good_contract.get("generation_token_provenance_verified")),
            "good_dense_error": float(good_contract.get("computed_dense_reference_max_abs_error", 0.0)),
            "forged_prompt_count_rejected": bool(forged_rejected),
            "forged_rejection_reason": forged_error,
            "forged_contract_if_unexpectedly_passed": forged_contract,
            "remaining_blockers": [
                "actual_public_pretrained_prefill_plus_cached_decode_generated_token_trace_missing",
                "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
                "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
            ],
            "errors": errors,
            "interpretation": (
                "The gate now rejects a dense-parity-valid cached-decode trace when its row positions cannot be replayed against the exact tokenized prompt boundary. "
                "This prevents an unreplayable Q/K/V bundle from being accepted as public evidence merely because its local attention math matches."
            ),
        }
    (OUT / f"{REVUP}_PUBLIC_TRACE_TOKEN_PROVENANCE_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        f"# Public trace token provenance audit — {REV}",
        "",
        f"**Status:** {report['status']}",
        "",
        report["interpretation"],
        "",
        f"- prompt contract: `{report['token_provenance_contract']}`",
        f"- generation contract: `{report['generation_token_contract']}`",
        f"- good bundle token provenance verified: `{report['good_bundle_verified']}`",
        f"- good bundle generated-token provenance verified: `{report['good_generation_token_verified']}`",
        f"- good dense error: `{report['good_dense_error']}`",
        f"- forged prompt-count bundle rejected: `{report['forged_prompt_count_rejected']}`",
        f"- forged rejection reason: `{report['forged_rejection_reason']}`",
        "",
        "## Remaining blockers",
        "",
    ]
    md.extend(f"- `{b}`" for b in report["remaining_blockers"])
    if errors:
        md.extend(["", "## Errors", ""] + [f"- {e}" for e in errors])
    (OUT / f"{REVUP}_PUBLIC_TRACE_TOKEN_PROVENANCE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": errors, "forged_rejected": forged_rejected}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
