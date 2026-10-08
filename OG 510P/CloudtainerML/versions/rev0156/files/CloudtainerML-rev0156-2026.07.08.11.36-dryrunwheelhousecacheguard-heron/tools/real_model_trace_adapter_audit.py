#!/usr/bin/env python3
from __future__ import annotations

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
CAPTURE = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def make_fixture(cap) -> dict[str, Any]:
    rng = np.random.default_rng(79079)
    batch, heads, kv_heads, q_len, key_len, d_head, d_value = 1, 4, 2, 3, 3, 8, 5
    q = rng.normal(size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scale = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    for pos in range(q_len):
        if pos + 1 < key_len:
            mask[:, :, pos, pos + 1 :] = -np.inf  # exercise causal masking and -inf sentinel conversion
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    groups = heads // kv_heads
    for b in range(batch):
        for pos in range(q_len):
            for head in range(heads):
                kv_head = head // groups
                scores = (k[b, kv_head] @ q[b, head, pos]) * scale + mask[b, 0, pos]
                weights = np.exp(scores - np.max(scores))
                weights = weights / np.sum(weights)
                out[b, pos, head] = weights @ v[b, kv_head]
    rows = cap._rows_from_attention_capture(
        q=q,
        k=k,
        v=v,
        out=out,
        attention_mask=mask,
        scaling=scale,
        layer_id=7,
        prompt_index=2,
        position_policy="all_tokens",
        max_remaining=100,
        num_key_value_groups=groups,
        capture_phase="prefill",
    )
    rq, rk, rv, rs, rb, rr, rg, rl, rh, rp, rpid, phases, valid_key_lens, query_lens, finite, mask_seen, err = rows
    score_bias = np.stack(rb).astype(np.float64)
    valid_key_len = np.asarray(valid_key_lens, dtype=np.int64)
    active_key_len = cap._active_key_lengths_from_bias(score_bias, valid_key_len)
    active_key_len_ok = cap._active_key_len_semantics_verified(score_bias, valid_key_len, active_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(np.asarray(rp, dtype=np.int64), valid_key_len, np.asarray(query_lens, dtype=np.int64), phases, active_key_len)
    head_arr = np.asarray(rh, dtype=np.int64)
    kv_head = (head_arr // groups).astype(np.int64)
    num_attention_heads = np.full((len(rh),), heads, dtype=np.int64)
    num_key_value_heads = np.full((len(rh),), kv_heads, dtype=np.int64)
    num_key_value_groups = np.full((len(rh),), groups, dtype=np.int64)
    kv_group_contract = cap._kv_group_semantics_verified(
        head_arr, kv_head, num_attention_heads, num_key_value_heads, num_key_value_groups
    )
    trace = {
        "q": np.stack(rq).astype(np.float64),
        "k": np.stack(rk).astype(np.float64),
        "v": np.stack(rv).astype(np.float64),
        "attention_scale": np.concatenate(rs).astype(np.float64),
        "score_bias": score_bias,
        "dense_reference_output": np.stack(rr).astype(np.float64),
        "regime": np.asarray(rg),
        "layer": np.asarray(rl, dtype=np.int64),
        "head": head_arr,
        "kv_head": kv_head,
        "num_attention_heads": num_attention_heads,
        "num_key_value_heads": num_key_value_heads,
        "num_key_value_groups": num_key_value_groups,
        "position": np.asarray(rp, dtype=np.int64),
        "prompt_id": np.asarray(rpid, dtype=np.int64),
        "capture_phase": np.asarray(phases),
        "valid_key_len": valid_key_len,
        "active_key_len": active_key_len,
        "query_len": np.asarray(query_lens, dtype=np.int64),
        "d_head": np.asarray([d_head], dtype=np.int64),
        "schema": np.asarray([cap.PUBLIC_QKV_SCHEMA]),
        "score_transform": np.asarray([cap.PUBLIC_SCORE_TRANSFORM]),
        "probability_contract": np.asarray([cap.PUBLIC_PROBABILITY_CONTRACT]),
        "probability_semantics_verified": np.asarray([True]),
        "attention_probability_dtype": np.asarray([cap.PUBLIC_ATTENTION_PROBABILITY_DTYPE]),
        "attention_dropout_p": np.asarray([0.0], dtype=np.float64),
        "attention_training_state": np.asarray([False]),
        "dropout_applied": np.asarray([False]),
        "attention_score_input_stage": np.asarray([cap.PUBLIC_SCORE_INPUT_STAGE]),
        "attention_score_inputs_verified": np.asarray([True]),
        "attention_scale_verified": np.asarray([True]),
        "score_bias_verified": np.asarray([True]),
        "mask_challenge_exercised": np.asarray([True]),
        "attention_mask_backend_preserved": np.asarray([True]),
        "custom_attention_backend_used": np.asarray([False]),
        "dense_reference_verified": np.asarray([True]),
        "capture_phase_contract": np.asarray(["prefill_fixture_only_v1"]),
        "prefill_phase_present": np.asarray([True]),
        "decode_phase_present": np.asarray([False]),
        "cache_decode_verified": np.asarray([False]),
        "valid_key_len_semantics_verified": np.asarray([cap._valid_key_len_padding_verified(score_bias, valid_key_len)]),
        "active_key_len_contract": np.asarray([cap.PUBLIC_ACTIVE_KEY_CONTRACT]),
        "active_key_len_semantics_verified": np.asarray([active_key_len_ok]),
        "kv_group_map_contract": np.asarray([cap.PUBLIC_KV_GROUP_CONTRACT]),
        "kv_group_map_verified": np.asarray([kv_group_contract]),
        "gqa_grouped_rows_present": np.asarray([groups > 1]),
        "position_contract": np.asarray([cap.PUBLIC_POSITION_CONTRACT]),
        "absolute_position_verified": np.asarray([absolute_position_ok]),
        "decode_steps_requested": np.asarray([0], dtype=np.int64),
        "dense_reference_max_abs_error": np.asarray([float(err)], dtype=np.float64),
    }
    return {
        "trace": trace,
        "row_count": len(rq),
        "finite_bias": finite,
        "mask_challenge_exercised": bool(mask_seen),
        "sentinel_bias_present": bool(np.any(trace["score_bias"] < -1.0e20)),
        "max_abs_error": float(err),
        "phases": sorted({str(x) for x in phases}),
        "valid_key_len_min": int(min(valid_key_lens)),
        "valid_key_len_max": int(max(valid_key_lens)),
        "active_key_len_min": int(np.min(active_key_len)),
        "active_key_len_max": int(np.max(active_key_len)),
        "active_key_len_semantics_verified": bool(active_key_len_ok),
        "kv_group_map_verified": bool(kv_group_contract),
        "gqa_grouped_rows_present": bool(groups > 1),
        "kv_head_unique": sorted({int(x) for x in kv_head.tolist()}),
        "num_attention_heads": int(heads),
        "num_key_value_heads": int(kv_heads),
        "num_key_value_groups": int(groups),
        "absolute_position_verified": bool(absolute_position_ok),
    }


class _FakeAttentionRegistry:
    def __init__(self):
        def original_registry(*args, **kwargs):
            return "original_registry"
        self.original_registry = original_registry
        self._global_mapping: dict[str, Any] = {"eager": original_registry}

    def register(self, key: str, value: Any) -> None:
        self._global_mapping[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._global_mapping[key]

    def __delitem__(self, key: str) -> None:
        del self._global_mapping[key]

    def get_interface(self, key: str, default: Any) -> Any:
        return self._global_mapping.get(key, default)


class _FakeConfig:
    def __init__(self):
        self._attn_implementation = "sdpa"


class _FakeModel:
    def __init__(self):
        self.config = _FakeConfig()


class _FakeLlamaModule:
    def __init__(self):
        def original(*args, **kwargs):
            return "original"
        self.eager_attention_forward = original
        self.ALL_ATTENTION_FUNCTIONS = _FakeAttentionRegistry()


def make_registry_fixture(cap) -> dict[str, Any]:
    fake_mod = _FakeLlamaModule()
    fake_model = _FakeModel()

    def wrapped(*args, **kwargs):
        return "wrapped"

    restore, status = cap._install_llama_attention_capture_wrapper(fake_mod, fake_model, wrapped)
    selected = fake_mod.ALL_ATTENTION_FUNCTIONS.get_interface(fake_model.config._attn_implementation, fake_mod.eager_attention_forward)
    before_restore = {
        "selected_is_wrapped": selected is wrapped,
        "module_patch_is_wrapped": fake_mod.eager_attention_forward is wrapped,
        "config_backend": fake_model.config._attn_implementation,
        "eager_registry_overridden": fake_mod.ALL_ATTENTION_FUNCTIONS._global_mapping.get("eager") is wrapped,
        "custom_backend_absent": "cloudtainer_trace_eager" not in fake_mod.ALL_ATTENTION_FUNCTIONS._global_mapping,
        "attention_mask_backend_preserved": bool(status.get("attention_mask_backend_preserved")),
        "custom_attention_backend_used": bool(status.get("custom_attention_backend_used")),
        "status": status,
    }
    restore()
    after_restore = {
        "module_restored": fake_mod.eager_attention_forward is not wrapped,
        "config_restored": fake_model.config._attn_implementation == "sdpa",
        "eager_registry_restored": fake_mod.ALL_ATTENTION_FUNCTIONS._global_mapping.get("eager") is fake_mod.ALL_ATTENTION_FUNCTIONS.original_registry,
        "custom_backend_absent": "cloudtainer_trace_eager" not in fake_mod.ALL_ATTENTION_FUNCTIONS._global_mapping,
    }
    return {"before_restore": before_restore, "after_restore": after_restore}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cap = load_module("hf_attention_trace_capture_rev0085", CAPTURE)
    gate = load_module("public_trace_gate_surrogate_rev0085", GATE)
    cap_source = CAPTURE.read_text(encoding="utf-8")

    constants_match = {
        "PUBLIC_SCORE_INPUT_STAGE": getattr(cap, "PUBLIC_SCORE_INPUT_STAGE", None) == getattr(gate, "PUBLIC_SCORE_INPUT_STAGE", None),
        "PUBLIC_TRACE_CLAIM_VERSION": getattr(cap, "PUBLIC_TRACE_CLAIM_VERSION", None) == getattr(gate, "PUBLIC_TRACE_CLAIM_VERSION", None),
        "PUBLIC_QKV_SCHEMA": getattr(cap, "PUBLIC_QKV_SCHEMA", None) == getattr(gate, "PUBLIC_QKV_SCHEMA", None),
        "PUBLIC_SCORE_TRANSFORM": getattr(cap, "PUBLIC_SCORE_TRANSFORM", None) == getattr(gate, "PUBLIC_SCORE_TRANSFORM", None),
        "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR": getattr(cap, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", None) == getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", None),
        "PUBLIC_CAPTURE_PHASE_CONTRACT": getattr(cap, "PUBLIC_CAPTURE_PHASE_CONTRACT", None) == getattr(gate, "PUBLIC_CAPTURE_PHASE_CONTRACT", None),
        "PUBLIC_ACTIVE_KEY_CONTRACT": getattr(cap, "PUBLIC_ACTIVE_KEY_CONTRACT", None) == getattr(gate, "PUBLIC_ACTIVE_KEY_CONTRACT", None),
        "PUBLIC_POSITION_CONTRACT": getattr(cap, "PUBLIC_POSITION_CONTRACT", None) == getattr(gate, "PUBLIC_POSITION_CONTRACT", None),
        "PUBLIC_KV_GROUP_CONTRACT": getattr(cap, "PUBLIC_KV_GROUP_CONTRACT", None) == getattr(gate, "PUBLIC_KV_GROUP_CONTRACT", None),
    }
    for name, ok in constants_match.items():
        if not ok:
            errors.append(f"capture/gate constant mismatch: {name}")

    required_text = {
        "verified_llama_adapter": "_capture_llama_eager_post_transform_style" in cap_source,
        "post_rope_intercept": "eager_attention_forward" in cap_source and ("after RoPE" in cap_source or "post-transform" in cap_source),
        "dense_reference_export": "dense_reference_output=dense_reference_output" in cap_source,
        "public_parity_tolerance_gate": "<= PUBLIC_DENSE_PARITY_MAX_ABS_ERROR" in cap_source,
        "llama_before_raw_projection": (
            "capture = _capture_llama_eager_post_transform_style" in cap_source
            and "capture = _capture_gpt2_style" in cap_source
            and cap_source.find("capture = _capture_llama_eager_post_transform_style") < cap_source.find("capture = _capture_gpt2_style")
        ),
        "multi_prompt_inputs": "--prompts-file" in cap_source and "action=\"append\"" in cap_source,
        "position_policy_inputs": "--position-policy" in cap_source and "last_and_mid" in cap_source and "all_tokens" in cap_source,
        "attention_interface_eager_override": "_install_llama_attention_capture_wrapper" in cap_source and "backend_name = \"eager\"" in cap_source,
        "mask_backend_preservation_exported": "attention_mask_backend_preserved" in cap_source and "custom_attention_backend_used" in cap_source,
        "mask_challenge_required": "mask_challenge_exercised" in cap_source and "score_inputs_scale_bias_mask_challenge" in cap_source,
        "capture_backend_exported": "attention_interface_backend" in cap_source and "attention_interface_registry_wrapper_installed" in cap_source,
        "cached_decode_cli_present": "--decode-steps" in cap_source and "model.generate(" in cap_source and "use_cache=True" in cap_source,
        "phase_contract_exported": "capture_phase_contract" in cap_source and "prefill_phase_present" in cap_source and "decode_phase_present" in cap_source,
        "valid_key_len_exported": "valid_key_len" in cap_source and "_valid_key_len_padding_verified" in cap_source,
        "active_key_len_exported": "active_key_len" in cap_source and "_active_key_len_semantics_verified" in cap_source and "PUBLIC_ACTIVE_KEY_CONTRACT" in cap_source,
        "absolute_position_exported": "position_contract" in cap_source and "absolute_position_verified" in cap_source and "_absolute_position_semantics_verified" in cap_source,
        "decode_position_not_local_zero": "query_start_position" in cap_source and "key_len - q_len" in cap_source,
        "kv_group_map_exported": "kv_head" in cap_source and "num_key_value_heads" in cap_source and "PUBLIC_KV_GROUP_CONTRACT" in cap_source,
        "probability_semantics_exported": "PUBLIC_PROBABILITY_CONTRACT" in cap_source and "attention_probability_dtype" in cap_source and "attention_dropout_p" in cap_source,
    }
    for name, ok in required_text.items():
        if not ok:
            errors.append(f"missing adapter implementation feature: {name}")

    try:
        fixture_raw = make_fixture(cap)
        fixture = {
            "row_count": fixture_raw["row_count"],
            "finite_bias": fixture_raw["finite_bias"],
            "max_abs_error": fixture_raw["max_abs_error"],
            "mask_challenge_exercised": fixture_raw["mask_challenge_exercised"],
            "sentinel_bias_present": fixture_raw["sentinel_bias_present"],
            "phases": fixture_raw.get("phases", []),
            "valid_key_len_min": fixture_raw.get("valid_key_len_min"),
            "valid_key_len_max": fixture_raw.get("valid_key_len_max"),
            "active_key_len_min": fixture_raw.get("active_key_len_min"),
            "active_key_len_max": fixture_raw.get("active_key_len_max"),
            "active_key_len_semantics_verified": fixture_raw.get("active_key_len_semantics_verified"),
            "kv_group_map_verified": fixture_raw.get("kv_group_map_verified"),
            "gqa_grouped_rows_present": fixture_raw.get("gqa_grouped_rows_present"),
            "kv_head_unique": fixture_raw.get("kv_head_unique"),
            "num_attention_heads": fixture_raw.get("num_attention_heads"),
            "num_key_value_heads": fixture_raw.get("num_key_value_heads"),
            "num_key_value_groups": fixture_raw.get("num_key_value_groups"),
            "absolute_position_verified": fixture_raw.get("absolute_position_verified"),
            "probability_contract": str(fixture_raw["trace"].get("probability_contract", [""])[0]),
            "probability_semantics_verified": bool(fixture_raw["trace"].get("probability_semantics_verified", [False])[0]),
        }
        if fixture["row_count"] != 12:
            errors.append(f"fixture row count expected 12, got {fixture['row_count']}")
        if not fixture["finite_bias"]:
            errors.append("fixture finite/sentinel bias check failed")
        if not fixture["mask_challenge_exercised"]:
            errors.append("fixture did not exercise causal mask challenge")
        if not fixture["sentinel_bias_present"]:
            errors.append("fixture did not preserve negative-infinity mask as finite sentinel")
        if fixture["max_abs_error"] > getattr(cap, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
            errors.append(f"fixture dense parity too large: {fixture['max_abs_error']}")
        if not fixture.get("active_key_len_semantics_verified"):
            errors.append("fixture active_key_len semantics were not verified")
        if not fixture.get("kv_group_map_verified"):
            errors.append("fixture query-head to KV-head group map was not verified")
        if not fixture.get("gqa_grouped_rows_present"):
            errors.append("fixture did not exercise grouped-query KV sharing rows")
        if not fixture.get("absolute_position_verified"):
            errors.append("fixture absolute active-key position semantics were not verified")
        with tempfile.TemporaryDirectory() as td:
            npz_path = Path(td) / "verified_llama_post_transform_fixture.npz"
            np.savez_compressed(npz_path, **fixture_raw["trace"])
            score_contract = gate.verify_qkv_score_contract(npz_path)
        score_contract = jsonable(score_contract)
        if score_contract["computed_dense_reference_max_abs_error"] > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
            errors.append("gate score-contract verification failed on verified fixture")
        if score_contract.get("kv_group_map_verified") is not True:
            errors.append("gate score-contract did not verify fixture KV group map")
        if score_contract.get("probability_contract") != getattr(gate, "PUBLIC_PROBABILITY_CONTRACT", None):
            errors.append("gate score-contract did not verify probability semantics contract")
    except Exception as exc:
        fixture = {"error": str(exc)}
        score_contract = None
        errors.append(f"adapter/gate fixture failed: {exc}")

    try:
        registry_fixture = make_registry_fixture(cap)
        before = registry_fixture.get("before_restore", {})
        after = registry_fixture.get("after_restore", {})
        for key in ["selected_is_wrapped", "module_patch_is_wrapped", "eager_registry_overridden", "custom_backend_absent", "attention_mask_backend_preserved"]:
            if before.get(key) is not True:
                errors.append(f"attention registry wrapper fixture failed before restore: {key}")
        if before.get("custom_attention_backend_used") is not False:
            errors.append("attention registry wrapper used a custom backend")
        for key in ["module_restored", "config_restored", "eager_registry_restored", "custom_backend_absent"]:
            if after.get(key) is not True:
                errors.append(f"attention registry wrapper fixture failed after restore: {key}")
    except Exception as exc:
        registry_fixture = {"error": str(exc)}
        errors.append(f"attention registry wrapper fixture failed: {exc}")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "real_model_trace_adapter_audit",
        "generated_at": META.get("generated_at"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "adapter_scope": "HF Llama eager attention post-transform capture path; requires local/cached or allowed-download public model to produce actual evidence",
        "constants_match": constants_match,
        "implementation_features": required_text,
        "fixture": fixture,
        "registry_wrapper_fixture": registry_fixture,
        "gate_score_contract": score_contract,
        "remaining_blockers": [
            "not_executed_against_public_pretrained_checkpoint_in_this_capsule",
            "transformers_dependency_absent_in_validation_environment" if not _transformers_available() else "public_checkpoint_not_supplied",
            "gpu_fused_kernel_timing_still_missing",
            "must_execute_against_real_public_model_with_mask_challenge_rows",
            "must_execute_with_decode_steps_positive_and_cache_decode_verified",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "rev0085 hardens the real-model trace adapter around the cached-decode seam: prefill-only rows can no longer self-promote. "
            "The adapter still overrides the built-in eager registry key, preserves the eager mask backend, requires an exercised mask-challenge row, exports scale/bias/dense_reference_output, and now requires --decode-steps coverage with valid_key_len padding plus mask-derived active_key_len semantics before a public checkpoint can pass the gate."
        ),
    }
    out_json = OUT / f"{REVUP}_REAL_MODEL_TRACE_ADAPTER_AUDIT.json"
    out_md = OUT / f"{REVUP}_REAL_MODEL_TRACE_ADAPTER_AUDIT.md"
    out_json.write_text(json.dumps(jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(
        f"# Real-model trace adapter audit — {REV}\n\n"
        f"**Status:** {report['status']}\n\n"
        f"{report['interpretation']}\n\n"
        f"Rows in pure mask-challenge adapter/gate fixture: {report.get('fixture', {}).get('row_count', 'n/a')}\n\n"
        "Remaining blocker: run the helper against an immutable public/pretrained HF checkpoint and keep promotion blocked until the gate accepts the bundle and named-hardware timing exists.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


def _transformers_available() -> bool:
    try:
        import transformers  # noqa: F401
        return True
    except Exception:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
