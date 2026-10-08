#!/usr/bin/env python3
"""Public/pretrained attention-trace gate and surrogate suite (hardened in rev0076).

The cube's strongest remaining scientific blocker is real public/pretrained
attention traces.  This probe does two concrete things without overclaiming:

1. creates an offline NPZ trace importer/evaluator with explicit schema;
2. runs a deterministic surrogate trace suite to stress selectors across
   retrieval, local, sink, diffuse, and value-tail regimes.

Default output is surrogate-only.  It is a gate and harness, not public model
evidence.  rev0049 fixes a claims bug: an arbitrary external NPZ bundle is not
called public/pretrained unless the caller explicitly declares that provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "attention_compiler_core"))
from attention_core import (  # noqa: E402
    guarded_mass_aware_compiler_points_for_row,
    stable_softmax,
)

try:
    _META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
except Exception:
    _META = {}
REV = _META.get('revision', 'rev0076')
REVUP = REV.upper()
STAMP = _META.get('generated_at') or _META.get('created_at') or 'unknown'
TARGET_MASS = 0.95
N = 128
DV = 32
D_HEAD = 32
FIXED_K = 16
HIST_BINS = 32
BLOCK = 16
VALUE_ERROR_BOUND = 0.18
SEED = 49049
ROWS_PER_REGIME = 48

# Fail before loading obviously wasteful or hostile external bundles. These are
# capsule-ingress limits, not claims about deployable long-context capacity.
MAX_TRACE_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_TRACE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
MAX_TRACE_MEMBERS = 256
MAX_TRACE_ROWS = 16384
MAX_TRACE_TOKENS = 262144
MAX_HEAD_DIM = 2048
MAX_VALUE_DIM = 8192
PUBLIC_DENSE_PARITY_MAX_ABS_ERROR = 1e-5
PUBLIC_SCORE_INPUT_STAGE = "post_model_qk_transforms"
PUBLIC_TRACE_CLAIM_VERSION = "public_trace_claim_v14"
PUBLIC_ACTIVE_KEY_CONTRACT = "mask_derived_active_prefix_v1"
PUBLIC_POSITION_CONTRACT = "absolute_active_key_position_v2"
PUBLIC_KV_GROUP_CONTRACT = "query_to_kv_head_group_map_v1"
PUBLIC_PROBABILITY_CONTRACT = "float32_softmax_no_dropout_v1"
PUBLIC_ROTARY_POSITION_CONTRACT = "runtime_rope_position_ids_v1"
PUBLIC_TOKEN_PROVENANCE_CONTRACT = "prompt_input_ids_attention_mask_digest_v2"
PUBLIC_PROMPT_MANIFEST_CONTRACT = "prompt_text_tokenizer_call_manifest_v1"
PUBLIC_GENERATION_TOKEN_CONTRACT = "generated_sequence_digest_exact_length_v2"
PUBLIC_GENERATION_DETERMINISM_CONTRACT = "greedy_exact_length_cached_decode_generation_config_v3"
PUBLIC_CACHE_IMPLEMENTATION_CONTRACT = "hf_generate_dynamic_cache_v1"
PUBLIC_REQUIRED_CACHE_IMPLEMENTATION = "dynamic"
PUBLIC_RUNTIME_PROVENANCE_CONTRACT = "trace_runtime_device_dtype_timing_v1"
PUBLIC_TIMING_CLOCK_CONTRACT = "synchronized_perf_counter_or_cuda_event_v1"
PUBLIC_RUNTIME_PROVENANCE_FIELDS = [
    "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype", "requested_device_policy",
    "actual_primary_device", "model_parameter_dtype_set", "model_device_set", "model_parameter_tensor_count",
    "cuda_available", "cuda_device_count", "cuda_device_name", "cuda_device_capability",
    "timing_clock_contract", "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized",
    "timing_cuda_event_recorded", "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
]
PUBLIC_ATTENTION_PROBABILITY_DTYPE = "float32"
PUBLIC_QKV_SCHEMA = "qkv_npz_v2"
PUBLIC_SCORE_TRANSFORM = "scaled_dot_product_plus_bias"
PUBLIC_CAPTURE_PHASE_CONTRACT = "prefill_and_cached_decode_v1"


@dataclass(frozen=True)
class TraceRow:
    scores: np.ndarray
    values: np.ndarray
    value_norms: np.ndarray
    d_head: int
    trace_source_type: str
    trace_bundle_id: str
    regime: str
    layer: int
    head: int
    position: int
    row_id: int
    imported_from: str | None = None
    attention_score_input_stage: str | None = None
    attention_score_inputs_verified: bool = False
    attention_scale: float | None = None
    score_bias: np.ndarray | None = None
    score_transform: str | None = None
    probability_contract: str | None = None
    probability_semantics_verified: bool = False
    attention_probability_dtype: str | None = None
    attention_dropout_p: float | None = None
    score_semantics_verified: bool = False
    capture_phase: str | None = None
    valid_key_len: int | None = None
    rotary_position_id: int | None = None
    kv_head: int | None = None
    num_attention_heads: int | None = None
    num_key_value_heads: int | None = None
    num_key_value_groups: int | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()





def validate_npz_resource_limits(path: Path) -> dict:
    """Inspect archive metadata before NumPy allocates arrays."""
    if path.stat().st_size > MAX_TRACE_ARCHIVE_BYTES:
        raise ValueError(f"trace NPZ exceeds compressed ingress limit: {path.stat().st_size} bytes")
    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_TRACE_MEMBERS:
                raise ValueError(f"trace NPZ has too many members: {len(infos)}")
            uncompressed = sum(int(i.file_size) for i in infos)
            if uncompressed > MAX_TRACE_UNCOMPRESSED_BYTES:
                raise ValueError(f"trace NPZ exceeds uncompressed ingress limit: {uncompressed} bytes")
            return {
                "archive_bytes": int(path.stat().st_size),
                "uncompressed_bytes": int(uncompressed),
                "member_count": int(len(infos)),
            }
    except zipfile.BadZipFile as exc:
        raise ValueError(f"trace NPZ is not a valid zip archive: {exc}") from exc


def _is_hex_sha256(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(c in "0123456789abcdefABCDEF" for c in text)


def _is_immutable_revision(value: object) -> bool:
    """Accept full Git commit IDs or explicit SHA-256 content identifiers."""
    text = str(value or "").strip()
    if text.startswith("sha256:"):
        return _is_hex_sha256(text.split(":", 1)[1])
    return (len(text) in {40, 64}) and all(c in "0123456789abcdefABCDEF" for c in text)


def _parse_jsonish_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    text = str(value or "").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass
    return [text]


def verify_runtime_provenance_contract(meta: dict) -> dict:
    out = {"runtime_provenance_present": False, "runtime_provenance_verified": False, "errors": [], "warnings": []}
    missing = [k for k in PUBLIC_RUNTIME_PROVENANCE_FIELDS if k not in meta]
    if missing:
        out["errors"].append("missing runtime provenance fields: " + ", ".join(missing))
        return out
    out["runtime_provenance_present"] = True
    if meta.get("runtime_provenance_contract") != PUBLIC_RUNTIME_PROVENANCE_CONTRACT:
        out["errors"].append(f"runtime_provenance_contract must be {PUBLIC_RUNTIME_PROVENANCE_CONTRACT!r}")
    if str(meta.get("requested_torch_dtype")) not in {"auto", "float32", "float16", "bfloat16"}:
        out["errors"].append("requested_torch_dtype must be explicit auto/float32/float16/bfloat16")
    if not str(meta.get("resolved_torch_dtype", "")).strip():
        out["errors"].append("resolved_torch_dtype must be recorded")
    if str(meta.get("requested_device_policy")) not in {"auto", "cpu", "cuda"}:
        out["errors"].append("requested_device_policy must be explicit auto/cpu/cuda")
    if not str(meta.get("actual_primary_device", "")).strip():
        out["errors"].append("actual_primary_device must be recorded")
    if not _parse_jsonish_list(meta.get("model_parameter_dtype_set")):
        out["errors"].append("model_parameter_dtype_set must be non-empty")
    if not _parse_jsonish_list(meta.get("model_device_set")):
        out["errors"].append("model_device_set must be non-empty")
    try:
        if int(meta.get("model_parameter_tensor_count")) <= 0:
            out["errors"].append("model_parameter_tensor_count must be positive")
    except Exception:
        out["errors"].append("model_parameter_tensor_count must be an integer")
    if not isinstance(meta.get("cuda_available"), bool):
        out["errors"].append("cuda_available must be boolean")
    try:
        if int(meta.get("cuda_device_count")) < 0:
            out["errors"].append("cuda_device_count must be non-negative")
    except Exception:
        out["errors"].append("cuda_device_count must be an integer")
    if meta.get("cuda_available") is True and int(meta.get("cuda_device_count", 0)) <= 0:
        out["errors"].append("cuda_available true requires positive cuda_device_count")
    if meta.get("timing_clock_contract") != PUBLIC_TIMING_CLOCK_CONTRACT:
        out["errors"].append(f"timing_clock_contract must be {PUBLIC_TIMING_CLOCK_CONTRACT!r}")
    if meta.get("timing_cpu_perf_counter_recorded") is not True:
        out["errors"].append("timing_cpu_perf_counter_recorded must be true")
    if not isinstance(meta.get("timing_cuda_synchronized"), bool):
        out["errors"].append("timing_cuda_synchronized must be boolean")
    if not isinstance(meta.get("timing_cuda_event_recorded"), bool):
        out["errors"].append("timing_cuda_event_recorded must be boolean")
    try:
        if float(meta.get("capture_elapsed_seconds")) < 0.0:
            out["errors"].append("capture_elapsed_seconds must be non-negative")
    except Exception:
        out["errors"].append("capture_elapsed_seconds must be numeric")
    if meta.get("named_hardware_timing_measured") is not False:
        out["errors"].append("named_hardware_timing_measured must remain false in trace capture provenance; promotion timing is a separate lane")
    if meta.get("runtime_provenance_verified") is not True:
        out["errors"].append("runtime_provenance_verified must be true")
    out["runtime_provenance_verified"] = not out["errors"]
    return out


def _npz_scalar(data, key: str):
    if key not in data.files:
        return None
    try:
        arr = np.asarray(data[key])
        if arr.size == 0:
            return None
        v = arr.reshape(-1)[0]
        if isinstance(v, bytes):
            return v.decode("utf-8", errors="replace")
        if isinstance(v, np.bytes_):
            return bytes(v).decode("utf-8", errors="replace")
        if isinstance(v, (np.bool_, bool)):
            return bool(v)
        if isinstance(v, (np.integer, int)):
            return int(v)
        if isinstance(v, (np.floating, float)):
            return float(v)
        return str(v)
    except Exception:
        return None


def _broadcast_int_rows(value, rows: int, *, default: int | None = None) -> np.ndarray:
    if value is None:
        if default is None:
            raise ValueError("missing integer row metadata")
        return np.full((rows,), int(default), dtype=np.int64)
    arr = np.asarray(value, dtype=np.int64).reshape(-1)
    if arr.size == 1:
        return np.repeat(arr, rows).astype(np.int64)
    if arr.size != rows:
        raise ValueError(f"expected scalar or {rows} integer metadata values, got {arr.size}")
    return arr.astype(np.int64)


def verify_kv_group_map_contract(*, heads, kv_head, num_attention_heads, num_key_value_heads, num_key_value_groups) -> dict:
    head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
    rows = int(head_arr.size)
    out = {
        "kv_group_map_present": False,
        "kv_group_map_verified": False,
        "gqa_grouped_rows": 0,
        "mha_rows": 0,
        "num_attention_heads_min": None,
        "num_attention_heads_max": None,
        "num_key_value_heads_min": None,
        "num_key_value_heads_max": None,
        "num_key_value_groups_min": None,
        "num_key_value_groups_max": None,
        "errors": [],
    }
    if rows <= 0:
        out["errors"].append("no heads supplied")
        return out
    try:
        kv_arr = _broadcast_int_rows(kv_head, rows)
        qh_arr = _broadcast_int_rows(num_attention_heads, rows)
        kvh_arr = _broadcast_int_rows(num_key_value_heads, rows)
        group_arr = _broadcast_int_rows(num_key_value_groups, rows)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    out["kv_group_map_present"] = True
    out["num_attention_heads_min"] = int(np.min(qh_arr))
    out["num_attention_heads_max"] = int(np.max(qh_arr))
    out["num_key_value_heads_min"] = int(np.min(kvh_arr))
    out["num_key_value_heads_max"] = int(np.max(kvh_arr))
    out["num_key_value_groups_min"] = int(np.min(group_arr))
    out["num_key_value_groups_max"] = int(np.max(group_arr))
    ok = True
    for i, (head, kv, qh, kvh, group) in enumerate(zip(head_arr, kv_arr, qh_arr, kvh_arr, group_arr)):
        h, kh, qn, kvn, g = int(head), int(kv), int(qh), int(kvh), int(group)
        if qn <= 0 or kvn <= 0 or g <= 0:
            out["errors"].append(f"row {i}: non-positive head metadata")
            ok = False
            break
        if qn != kvn * g:
            out["errors"].append(f"row {i}: num_attention_heads must equal num_key_value_heads*num_key_value_groups")
            ok = False
            break
        if h < 0 or h >= qn or kh < 0 or kh >= kvn:
            out["errors"].append(f"row {i}: head or kv_head out of range")
            ok = False
            break
        if kh != h // g:
            out["errors"].append(f"row {i}: kv_head {kh} does not equal head//group {h}//{g}")
            ok = False
            break
        if g > 1:
            out["gqa_grouped_rows"] += 1
        else:
            out["mha_rows"] += 1
    out["kv_group_map_verified"] = bool(ok and out["kv_group_map_present"])
    return out




def verify_rotary_position_contract(*, rotary_position_id, active_position, query_len, capture_phase) -> dict:
    """Verify runtime RoPE position_ids are not collapsed into local row ids.

    `position` remains the active-cache row coordinate used for selector/cost
    analysis.  Llama applies rotary embeddings from runtime `position_ids`; in
    cached generation this may be equal to the active position for ordinary
    dynamic caches or larger for sliding/static windows.  It must never be the
    local q_len=1 index.
    """
    out = {
        "rotary_position_present": False,
        "rotary_position_verified": False,
        "prefill_rotary_rows": 0,
        "decode_rotary_rows": 0,
        "decode_rotary_global_offset_rows": 0,
        "errors": [],
    }
    try:
        rope = np.asarray(rotary_position_id, dtype=np.int64).reshape(-1)
        pos = np.asarray(active_position, dtype=np.int64).reshape(-1)
        ql = np.asarray(query_len, dtype=np.int64).reshape(-1)
        phases = np.asarray(capture_phase).reshape(-1)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    if not (rope.shape == pos.shape == ql.shape == phases.shape):
        out["errors"].append("rotary_position_id, position, query_len, and capture_phase must have identical row shape")
        return out
    if rope.size <= 0:
        out["errors"].append("no rotary rows supplied")
        return out
    out["rotary_position_present"] = True
    ok = True
    for i, (rid, active_pos, q_len, phase) in enumerate(zip(rope, pos, ql, phases)):
        rid_i, pos_i, q_i = int(rid), int(active_pos), int(q_len)
        if rid_i < 0 or pos_i < 0 or q_i <= 0:
            out["errors"].append(f"row {i}: negative/nonpositive rotary metadata")
            ok = False
            break
        phase_text = str(phase)
        if phase_text == "prefill":
            out["prefill_rotary_rows"] += 1
            if rid_i != pos_i:
                out["errors"].append(f"row {i}: prefill rotary_position_id {rid_i} must equal active position {pos_i}")
                ok = False
                break
        elif phase_text == "decode_cached":
            out["decode_rotary_rows"] += 1
            if q_i != 1:
                out["errors"].append(f"row {i}: cached decode rotary row must have query_len=1")
                ok = False
                break
            if rid_i < pos_i:
                out["errors"].append(f"row {i}: rotary_position_id {rid_i} is below active-cache position {pos_i}")
                ok = False
                break
            if rid_i > pos_i:
                out["decode_rotary_global_offset_rows"] += 1
        else:
            out["errors"].append(f"row {i}: unsupported phase {phase_text!r}")
            ok = False
            break
    out["rotary_position_verified"] = bool(ok and out["prefill_rotary_rows"] > 0 and out["decode_rotary_rows"] > 0)
    return out


def _is_hex_sha256_text(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(c in "0123456789abcdefABCDEF" for c in text)


def _string_rows(value: object) -> np.ndarray:
    return np.asarray(value).astype(str).reshape(-1)


def _npz_json_scalar_text(value: object) -> str:
    arr = np.asarray(value).reshape(-1)
    if arr.size != 1:
        raise ValueError("generation_config_json must be a scalar string")
    return str(arr[0])


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json_text(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def verify_prompt_manifest_contract(
    *,
    prompt_manifest_contract,
    prompt_manifest_json,
    prompt_manifest_sha256,
    tokenization_settings_json,
    tokenization_settings_sha256,
    prompt_count,
    prompt_token_count,
    prompt_input_ids_sha256,
    prompt_attention_mask_sha256,
    prompt_text_sha256,
    tokenization_add_special_tokens=True,
    tokenization_padding="false",
    tokenization_truncation="false",
    tokenization_return_attention_mask=True,
    tokenization_return_tensors="pt",
    chat_template_applied=False,
) -> dict:
    """Verify exact prompt text + tokenizer-call manifest for replayability.

    Hashes of input_ids/attention_mask are not enough for a public trace if the
    prompt text and tokenizer call knobs are absent.  This contract binds the
    public NPZ to exact prompt strings and to explicit tokenization settings, so
    an operator can reproduce the same tokenizer output rather than trusting a
    hidden default.
    """
    out = {
        "prompt_manifest_present": False,
        "prompt_manifest_verified": False,
        "prompt_count": None,
        "errors": [],
    }
    try:
        contract = str(prompt_manifest_contract)
        manifest_text = _npz_json_scalar_text(prompt_manifest_json)
        manifest_digest = str(prompt_manifest_sha256)
        settings_text = _npz_json_scalar_text(tokenization_settings_json)
        settings_digest = str(tokenization_settings_sha256)
        pc = int(prompt_count)
        token_counts = np.asarray(prompt_token_count, dtype=np.int64).reshape(-1)
        input_hashes = _string_rows(prompt_input_ids_sha256)
        mask_hashes = _string_rows(prompt_attention_mask_sha256)
        text_hashes = _string_rows(prompt_text_sha256)
        manifest = json.loads(manifest_text)
        settings = json.loads(settings_text)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    out["prompt_manifest_present"] = True
    out["prompt_count"] = pc
    ok = True
    if contract != PUBLIC_PROMPT_MANIFEST_CONTRACT:
        out["errors"].append(f"prompt_manifest_contract must be {PUBLIC_PROMPT_MANIFEST_CONTRACT!r}")
        ok = False
    if not _is_hex_sha256_text(manifest_digest) or _sha256_text(manifest_text) != manifest_digest:
        out["errors"].append("prompt_manifest_sha256 must match prompt_manifest_json")
        ok = False
    if not _is_hex_sha256_text(settings_digest) or _sha256_text(settings_text) != settings_digest:
        out["errors"].append("tokenization_settings_sha256 must match tokenization_settings_json")
        ok = False
    if not isinstance(manifest, dict) or manifest.get("contract") != PUBLIC_PROMPT_MANIFEST_CONTRACT:
        out["errors"].append("prompt_manifest_json must be an object with the required contract")
        ok = False
    if not isinstance(settings, dict) or settings.get("contract") != PUBLIC_PROMPT_MANIFEST_CONTRACT:
        out["errors"].append("tokenization_settings_json must be an object with the required contract")
        ok = False
    if pc <= 0:
        out["errors"].append("prompt_count must be positive")
        ok = False
    if not (token_counts.shape == input_hashes.shape == mask_hashes.shape == text_hashes.shape == (pc,)):
        out["errors"].append("prompt arrays must be [prompt_count]")
        return out
    if not all(_is_hex_sha256_text(x) for x in list(input_hashes) + list(mask_hashes) + list(text_hashes)):
        out["errors"].append("prompt input_ids/attention_mask/text digests must be SHA-256 hex")
        ok = False
    call = settings.get("call", {}) if isinstance(settings, dict) else {}
    expected_call = {
        "add_special_tokens": True,
        "padding": False,
        "truncation": False,
        "return_attention_mask": True,
        "return_tensors": "pt",
        "chat_template_applied": False,
    }
    for key, expected in expected_call.items():
        if call.get(key) != expected:
            out["errors"].append(f"tokenization_settings_json.call[{key!r}] must be {expected!r}")
            ok = False
    if bool(tokenization_add_special_tokens) is not True:
        out["errors"].append("tokenization_add_special_tokens must be true")
        ok = False
    if str(tokenization_padding).lower() not in {"false", "none", "no_padding"}:
        out["errors"].append("tokenization_padding must be false/no_padding")
        ok = False
    if str(tokenization_truncation).lower() not in {"false", "none", "do_not_truncate"}:
        out["errors"].append("tokenization_truncation must be false/do_not_truncate")
        ok = False
    if bool(tokenization_return_attention_mask) is not True:
        out["errors"].append("tokenization_return_attention_mask must be true")
        ok = False
    if str(tokenization_return_tensors) != "pt":
        out["errors"].append("tokenization_return_tensors must be 'pt'")
        ok = False
    if bool(chat_template_applied) is not False:
        out["errors"].append("chat_template_applied must be false for this raw-prompt trace contract")
        ok = False
    prompts = manifest.get("prompts") if isinstance(manifest, dict) else None
    if not isinstance(prompts, list) or len(prompts) != pc:
        out["errors"].append("prompt_manifest_json.prompts must have prompt_count entries")
        return out
    for i, record in enumerate(prompts):
        if not isinstance(record, dict):
            out["errors"].append(f"prompt manifest entry {i} must be an object")
            ok = False
            break
        if int(record.get("prompt_index", -1)) != i:
            out["errors"].append(f"prompt manifest entry {i} has wrong prompt_index")
            ok = False
            break
        text = str(record.get("text", ""))
        if not text:
            out["errors"].append(f"prompt manifest entry {i} has empty text")
            ok = False
            break
        if _sha256_text(text) != str(text_hashes[i]) or record.get("text_sha256") != str(text_hashes[i]):
            out["errors"].append(f"prompt manifest entry {i} text hash mismatch")
            ok = False
            break
        if str(record.get("input_ids_sha256", "")) != str(input_hashes[i]):
            out["errors"].append(f"prompt manifest entry {i} input_ids hash mismatch")
            ok = False
            break
        if str(record.get("attention_mask_sha256", "")) != str(mask_hashes[i]):
            out["errors"].append(f"prompt manifest entry {i} attention_mask hash mismatch")
            ok = False
            break
        if int(record.get("token_count", -1)) != int(token_counts[i]):
            out["errors"].append(f"prompt manifest entry {i} token_count mismatch")
            ok = False
            break
    out["prompt_manifest_verified"] = bool(ok)
    return out


def verify_generation_determinism_contract(
    *,
    generation_config_json,
    generation_config_sha256,
    generation_determinism_contract,
    generation_determinism_verified,
    generation_strategy,
    generation_do_sample,
    generation_use_cache,
    cache_implementation_contract=None,
    generation_cache_implementation=None,
    generation_cache_implementation_source=None,
    generation_cache_config_present=None,
    generation_num_beams,
    generation_num_return_sequences,
    generation_max_new_tokens,
    generation_min_new_tokens,
    generation_sampling_disabled,
    generation_exact_new_tokens_required,
    decode_steps_requested,
) -> dict:
    """Verify greedy single-sequence cached-decode generation replay settings.

    Generated token digests are necessary but not sufficient.  A public trace must
    also prove that the generation call used deterministic greedy decoding.  HF
    generation semantics distinguish greedy (`do_sample=False`, `num_beams=1`)
    from beam search (`do_sample=False`, `num_beams>1`), so the gate rejects
    inherited or forged beam/sampling settings even when Q/K/V dense parity and
    token digests still match.
    """
    out = {
        "generation_determinism_present": False,
        "generation_determinism_verified": False,
        "strategy": None,
        "num_beams": None,
        "num_return_sequences": None,
        "max_new_tokens": None,
        "min_new_tokens": None,
        "errors": [],
    }
    try:
        json_text = _npz_json_scalar_text(generation_config_json)
        digest = str(generation_config_sha256)
        contract = str(generation_determinism_contract)
        self_verified = bool(generation_determinism_verified)
        strategy = str(generation_strategy)
        do_sample = bool(generation_do_sample)
        use_cache = bool(generation_use_cache)
        cache_contract = str(cache_implementation_contract)
        cache_impl = str(generation_cache_implementation)
        cache_source = str(generation_cache_implementation_source)
        cache_config_present = bool(generation_cache_config_present)
        num_beams = int(generation_num_beams)
        num_return_sequences = int(generation_num_return_sequences)
        max_new_tokens = int(generation_max_new_tokens)
        min_new_tokens = int(generation_min_new_tokens)
        sampling_disabled = bool(generation_sampling_disabled)
        exact_new_tokens_required = bool(generation_exact_new_tokens_required)
        decode_steps = int(decode_steps_requested)
        parsed = json.loads(json_text)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    out.update({
        "generation_determinism_present": True,
        "strategy": strategy,
        "num_beams": num_beams,
        "num_return_sequences": num_return_sequences,
        "max_new_tokens": max_new_tokens,
        "min_new_tokens": min_new_tokens,
    })
    ok = True
    if contract != PUBLIC_GENERATION_DETERMINISM_CONTRACT:
        out["errors"].append(f"generation_determinism_contract must be {PUBLIC_GENERATION_DETERMINISM_CONTRACT!r}")
        ok = False
    if self_verified is not True:
        out["errors"].append("generation_determinism_verified must be true")
        ok = False
    if not _is_hex_sha256_text(digest) or _sha256_text(json_text) != digest:
        out["errors"].append("generation_config_sha256 must match generation_config_json")
        ok = False
    if not isinstance(parsed, dict):
        out["errors"].append("generation_config_json must decode to an object")
        return out
    expected_pairs = {
        "contract": PUBLIC_GENERATION_DETERMINISM_CONTRACT,
        "strategy": "greedy",
        "do_sample": False,
        "num_beams": 1,
        "num_return_sequences": 1,
        "max_new_tokens": decode_steps,
        "min_new_tokens": decode_steps,
        "use_cache": True,
        "cache_implementation_contract": PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        "cache_implementation": PUBLIC_REQUIRED_CACHE_IMPLEMENTATION,
        "cache_implementation_source": "explicit_generate_argument",
        "cache_config": None,
        "sampling_disabled": True,
        "beam_search_disabled": True,
        "exact_new_token_count_required": True,
    }
    for key, expected in expected_pairs.items():
        if parsed.get(key) != expected:
            out["errors"].append(f"generation_config_json[{key!r}] must be {expected!r}")
            ok = False
    if strategy != "greedy":
        out["errors"].append("generation_strategy must be 'greedy'")
        ok = False
    if do_sample is not False:
        out["errors"].append("generation_do_sample must be false")
        ok = False
    if use_cache is not True:
        out["errors"].append("generation_use_cache must be true")
        ok = False
    if cache_contract != PUBLIC_CACHE_IMPLEMENTATION_CONTRACT:
        out["errors"].append(f"cache_implementation_contract must be {PUBLIC_CACHE_IMPLEMENTATION_CONTRACT!r}")
        ok = False
    if cache_impl != PUBLIC_REQUIRED_CACHE_IMPLEMENTATION:
        out["errors"].append("generation_cache_implementation must be explicit dynamic cache")
        ok = False
    if cache_source != "explicit_generate_argument":
        out["errors"].append("generation_cache_implementation_source must be explicit_generate_argument")
        ok = False
    if cache_config_present is not False:
        out["errors"].append("generation_cache_config_present must be false for the public trace contract")
        ok = False
    if num_beams != 1:
        out["errors"].append("generation_num_beams must be 1; do_sample=False with num_beams>1 is beam search, not greedy replay")
        ok = False
    if num_return_sequences != 1:
        out["errors"].append("generation_num_return_sequences must be 1")
        ok = False
    if max_new_tokens != decode_steps or max_new_tokens <= 0:
        out["errors"].append("generation_max_new_tokens must equal positive decode_steps_requested")
        ok = False
    if min_new_tokens != decode_steps or min_new_tokens <= 0:
        out["errors"].append("generation_min_new_tokens must equal positive decode_steps_requested")
        ok = False
    if exact_new_tokens_required is not True:
        out["errors"].append("generation_exact_new_tokens_required must be true")
        ok = False
    if sampling_disabled is not True:
        out["errors"].append("generation_sampling_disabled must be true")
        ok = False
    out["generation_determinism_verified"] = bool(ok)
    return out


def verify_token_provenance_contract(
    *,
    prompt_id,
    position,
    capture_phase,
    prompt_count,
    prompt_token_count,
    prompt_input_ids_sha256,
    prompt_attention_mask_sha256,
    prompt_text_sha256,
    decode_steps_requested,
) -> dict:
    """Verify exact tokenizer-input provenance and row/prompt boundary semantics.

    A Q/K/V bundle can reproduce dense attention while still being unreplayable if
    the prompt and tokenizer output are not tied to the rows.  This contract uses
    per-prompt hashes for input_ids, attention_mask, and prompt text, then checks
    that prefill rows lie inside the prompt and cached-decode rows lie within the
    requested generated-token range after the prompt.
    """
    out = {
        "token_provenance_present": False,
        "token_provenance_verified": False,
        "prompt_count": None,
        "prompt_token_count_min": None,
        "prompt_token_count_max": None,
        "prefill_rows_with_prompt_position": 0,
        "decode_rows_after_prompt": 0,
        "errors": [],
    }
    try:
        pid = np.asarray(prompt_id, dtype=np.int64).reshape(-1)
        pos = np.asarray(position, dtype=np.int64).reshape(-1)
        phases = np.asarray(capture_phase).reshape(-1)
        pc = int(prompt_count)
        token_counts = np.asarray(prompt_token_count, dtype=np.int64).reshape(-1)
        input_hashes = _string_rows(prompt_input_ids_sha256)
        mask_hashes = _string_rows(prompt_attention_mask_sha256)
        text_hashes = _string_rows(prompt_text_sha256)
        decode_steps = int(decode_steps_requested)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    if not (pid.shape == pos.shape == phases.shape):
        out["errors"].append("prompt_id, position, and capture_phase must have identical row shape")
        return out
    if pc <= 0:
        out["errors"].append("prompt_count must be positive")
        return out
    if not (token_counts.shape == input_hashes.shape == mask_hashes.shape == text_hashes.shape == (pc,)):
        out["errors"].append("prompt_token_count and prompt hash arrays must be [prompt_count]")
        return out
    out["token_provenance_present"] = True
    out["prompt_count"] = pc
    out["prompt_token_count_min"] = int(np.min(token_counts))
    out["prompt_token_count_max"] = int(np.max(token_counts))
    ok = True
    if np.any(token_counts <= 0):
        out["errors"].append("prompt_token_count must be positive")
        ok = False
    if not all(_is_hex_sha256_text(x) for x in list(input_hashes) + list(mask_hashes) + list(text_hashes)):
        out["errors"].append("prompt input_ids/attention_mask/text digests must be SHA-256 hex")
        ok = False
    for i, (row_prompt, row_pos, row_phase) in enumerate(zip(pid, pos, phases)):
        p_i, pos_i = int(row_prompt), int(row_pos)
        if p_i < 0 or p_i >= pc or pos_i < 0:
            out["errors"].append(f"row {i}: prompt_id or position out of range")
            ok = False
            break
        prompt_len = int(token_counts[p_i])
        phase_text = str(row_phase)
        if phase_text == "prefill":
            if pos_i >= prompt_len:
                out["errors"].append(f"row {i}: prefill position {pos_i} outside prompt token count {prompt_len}")
                ok = False
                break
            out["prefill_rows_with_prompt_position"] += 1
        elif phase_text == "decode_cached":
            if decode_steps <= 0 or pos_i < prompt_len or pos_i >= prompt_len + decode_steps:
                out["errors"].append(f"row {i}: decode position {pos_i} not in generated-token window [{prompt_len}, {prompt_len + decode_steps})")
                ok = False
                break
            out["decode_rows_after_prompt"] += 1
        else:
            out["errors"].append(f"row {i}: unsupported phase {phase_text!r}")
            ok = False
            break
    out["token_provenance_verified"] = bool(ok and out["prefill_rows_with_prompt_position"] > 0 and out["decode_rows_after_prompt"] > 0)
    return out


def verify_generation_token_contract(
    *,
    prompt_id,
    position,
    capture_phase,
    prompt_token_count,
    generated_sequence_sha256,
    generated_new_token_ids_sha256,
    generated_new_token_count,
    generated_sequence_token_count,
    generation_prompt_prefix_verified,
    decode_steps_requested,
) -> dict:
    """Verify exact generated-token provenance for cached-decode rows.

    Prompt hashes alone do not replay the decode path.  For greedy cached
    generation, later decode rows are conditioned on the previous generated
    token IDs.  This check binds the trace to the full generated sequence and
    to the new-token suffix without embedding prompt text in the NPZ.
    """
    out = {
        "generation_token_present": False,
        "generation_token_provenance_verified": False,
        "generated_new_token_count_min": None,
        "generated_new_token_count_max": None,
        "generated_new_token_exact_count_verified": False,
        "decode_rows_inside_generated_suffix": 0,
        "errors": [],
    }
    try:
        pid = np.asarray(prompt_id, dtype=np.int64).reshape(-1)
        pos = np.asarray(position, dtype=np.int64).reshape(-1)
        phases = np.asarray(capture_phase).reshape(-1)
        prompt_counts = np.asarray(prompt_token_count, dtype=np.int64).reshape(-1)
        seq_hashes = _string_rows(generated_sequence_sha256)
        new_hashes = _string_rows(generated_new_token_ids_sha256)
        new_counts = np.asarray(generated_new_token_count, dtype=np.int64).reshape(-1)
        seq_counts = np.asarray(generated_sequence_token_count, dtype=np.int64).reshape(-1)
        prefix_ok = np.asarray(generation_prompt_prefix_verified, dtype=bool).reshape(-1)
        decode_steps = int(decode_steps_requested)
    except Exception as exc:
        out["errors"].append(str(exc))
        return out
    if not (pid.shape == pos.shape == phases.shape):
        out["errors"].append("prompt_id, position, and capture_phase must have identical row shape")
        return out
    prompt_count = int(prompt_counts.size)
    if prompt_count <= 0:
        out["errors"].append("prompt_token_count must have at least one prompt")
        return out
    if not (seq_hashes.shape == new_hashes.shape == new_counts.shape == seq_counts.shape == prefix_ok.shape == (prompt_count,)):
        out["errors"].append("generated sequence hashes/counts/prefix flags must be [prompt_count]")
        return out
    out["generation_token_present"] = True
    out["generated_new_token_count_min"] = int(np.min(new_counts))
    out["generated_new_token_count_max"] = int(np.max(new_counts))
    ok = True
    if decode_steps <= 0:
        out["errors"].append("decode_steps_requested must be positive for generated-token provenance")
        ok = False
    if np.any(prompt_counts <= 0) or np.any(new_counts <= 0):
        out["errors"].append("prompt and generated token counts must be positive")
        ok = False
    exact_count = bool(decode_steps > 0 and np.all(new_counts == decode_steps))
    out["generated_new_token_exact_count_verified"] = exact_count
    if not exact_count:
        out["errors"].append("generated_new_token_count must equal decode_steps_requested for every prompt")
        ok = False
    if np.any(seq_counts != prompt_counts + new_counts):
        out["errors"].append("generated_sequence_token_count must equal prompt_token_count + generated_new_token_count")
        ok = False
    if not bool(np.all(prefix_ok)):
        out["errors"].append("generated sequence did not preserve prompt token prefix")
        ok = False
    if not all(_is_hex_sha256_text(x) for x in list(seq_hashes) + list(new_hashes)):
        out["errors"].append("generated sequence/new-token digests must be SHA-256 hex")
        ok = False
    for i, (row_prompt, row_pos, row_phase) in enumerate(zip(pid, pos, phases)):
        p_i, pos_i = int(row_prompt), int(row_pos)
        if p_i < 0 or p_i >= prompt_count or pos_i < 0:
            out["errors"].append(f"row {i}: prompt_id or position out of range")
            ok = False
            break
        prompt_len = int(prompt_counts[p_i])
        gen_len = int(new_counts[p_i])
        phase_text = str(row_phase)
        if phase_text == "prefill":
            if pos_i >= prompt_len:
                out["errors"].append(f"row {i}: prefill position {pos_i} outside prompt token count {prompt_len}")
                ok = False
                break
        elif phase_text == "decode_cached":
            if pos_i < prompt_len or pos_i >= prompt_len + gen_len:
                out["errors"].append(f"row {i}: decode position {pos_i} outside generated-token suffix [{prompt_len}, {prompt_len + gen_len})")
                ok = False
                break
            out["decode_rows_inside_generated_suffix"] += 1
        else:
            out["errors"].append(f"row {i}: unsupported phase {phase_text!r}")
            ok = False
            break
    out["generation_token_provenance_verified"] = bool(ok and out["decode_rows_inside_generated_suffix"] > 0)
    return out


def inspect_trace_npz_metadata(path: Path | None) -> dict:
    """Return schema + self-attestation metadata from an external trace bundle.

    rev0073 closes a remaining loophole from rev0072: a valid-looking JSON
    provenance manifest must also agree with metadata embedded in the trace NPZ
    itself.  This is not cryptographic proof of public/pretrained origin, but it
    prevents a local fixture or random trace from being promoted by a detached
    manifest alone.  The capture helper now emits these fields.
    """
    out = {
        "status": "not_checked",
        "schema": None,
        "metadata": {},
        "missing_public_self_attestation_fields": [],
        "red_flag_terms": [],
        "errors": [],
        "warnings": [],
        "resource_limits": None,
    }
    if path is None:
        out["status"] = "no_trace_npz"
        out["errors"].append("no trace NPZ supplied")
        return out
    if not path.exists():
        out["status"] = "trace_npz_missing_on_disk"
        out["errors"].append("trace NPZ does not exist")
        return out
    try:
        out["resource_limits"] = validate_npz_resource_limits(path)
        data = np.load(path, allow_pickle=False)
    except Exception as exc:
        out["status"] = "trace_npz_unreadable"
        out["errors"].append(f"could not read NPZ metadata: {exc}")
        return out
    files = set(data.files)
    embedded_schema = _npz_scalar(data, "schema")
    if {"q", "k", "v"}.issubset(files) or {"queries", "keys", "values"}.issubset(files):
        out["schema"] = str(embedded_schema or "qkv_npz_v1")
    elif {"scores", "values"}.issubset(files):
        out["schema"] = str(embedded_schema or "scores_values_npz_v1")
    else:
        out["schema"] = "unknown"
        out["errors"].append("NPZ does not contain q/k/v, queries/keys/values, or scores/values schema")
    metadata_fields = [
        "trace_claim_version", "public_pretrained_trace", "source_type",
        "model_id", "model_load_source", "model_load_source_is_local_path",
        "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype",
        "requested_device_policy", "actual_primary_device", "model_parameter_dtype_set",
        "model_device_set", "model_parameter_tensor_count", "cuda_available", "cuda_device_count",
        "cuda_device_name", "cuda_device_capability", "timing_clock_contract",
        "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized", "timing_cuda_event_recorded",
        "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
        "model_revision", "tokenizer_revision", "code_revision", "trust_remote_code", "weights_source",
        "license", "schema", "capture_tool", "capture_tool_sha256",
        "config_sha256", "generated_from_local_tiny_model", "uses_random_weights",
        "provenance_reviewed", "adapter", "trace_source_type", "d_head",
        "attention_backend", "attention_score_input_stage",
        "attention_score_inputs_verified", "score_transform", "probability_contract", "probability_semantics_verified",
        "attention_probability_dtype", "attention_dropout_p", "attention_training_state", "dropout_applied",
        "attention_scale_verified", "score_bias_verified",
        "mask_challenge_exercised", "attention_mask_backend_preserved", "custom_attention_backend_used",
        "attention_mask_present_call_count", "attention_mask_absent_call_count",
        "capture_phase_contract", "prefill_phase_present", "decode_phase_present", "cache_decode_verified",
        "valid_key_len_semantics_verified", "active_key_len_contract", "active_key_len_semantics_verified",
        "kv_group_map_contract", "kv_group_map_verified", "gqa_grouped_rows_present",
        "position_contract", "absolute_position_verified", "rotary_position_contract", "rotary_position_ids_verified", "rotary_position_ids_present_call_count", "decode_steps_requested",
        "token_provenance_contract", "token_provenance_verified", "prompt_count", "prompt_token_count_min", "prompt_token_count_max", "prompt_manifest_contract", "prompt_manifest_sha256", "tokenization_settings_sha256", "tokenization_add_special_tokens", "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask", "tokenization_return_tensors", "chat_template_applied", "generation_config_json", "generation_config_sha256", "generation_determinism_contract", "generation_determinism_verified", "generation_strategy", "generation_do_sample", "generation_use_cache", "cache_implementation_contract", "generation_cache_implementation", "generation_cache_implementation_source", "generation_cache_config_present", "generation_num_beams", "generation_num_return_sequences", "generation_max_new_tokens", "generation_min_new_tokens", "generation_sampling_disabled", "generation_exact_new_tokens_required", "generation_token_contract", "generation_token_provenance_verified", "generated_new_token_count_min", "generated_new_token_count_max", "generated_new_token_exact_count_verified",
        "dense_reference_verified", "dense_reference_max_abs_error", "preflight_fixture",
    ]
    meta = {}
    for key in metadata_fields:
        value = _npz_scalar(data, key)
        if value is not None:
            meta[key] = value
    try:
        data.close()
    except Exception:
        pass
    out["metadata"] = meta
    required_for_public = [
        "trace_claim_version", "public_pretrained_trace", "source_type",
        "model_id", "model_load_source", "model_load_source_is_local_path",
        "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype",
        "requested_device_policy", "actual_primary_device", "model_parameter_dtype_set",
        "model_device_set", "model_parameter_tensor_count", "cuda_available", "cuda_device_count",
        "cuda_device_name", "cuda_device_capability", "timing_clock_contract",
        "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized", "timing_cuda_event_recorded",
        "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
        "model_revision", "tokenizer_revision", "code_revision", "trust_remote_code",
        "weights_source", "license", "schema", "capture_tool", "capture_tool_sha256",
        "config_sha256", "generated_from_local_tiny_model", "uses_random_weights", "provenance_reviewed",
        "d_head", "attention_backend", "attention_score_input_stage", "attention_score_inputs_verified",
        "score_transform", "probability_contract", "probability_semantics_verified",
        "attention_probability_dtype", "attention_dropout_p", "attention_training_state", "dropout_applied",
        "attention_scale_verified", "score_bias_verified",
        "mask_challenge_exercised", "attention_mask_backend_preserved", "custom_attention_backend_used",
        "capture_phase_contract", "prefill_phase_present", "decode_phase_present", "cache_decode_verified",
        "valid_key_len_semantics_verified", "active_key_len_contract", "active_key_len_semantics_verified",
        "kv_group_map_contract", "kv_group_map_verified", "gqa_grouped_rows_present",
        "position_contract", "absolute_position_verified", "rotary_position_contract", "rotary_position_ids_verified", "rotary_position_ids_present_call_count", "decode_steps_requested",
        "token_provenance_contract", "token_provenance_verified", "prompt_count", "prompt_token_count_min", "prompt_token_count_max", "prompt_manifest_contract", "prompt_manifest_sha256", "tokenization_settings_sha256", "tokenization_add_special_tokens", "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask", "tokenization_return_tensors", "chat_template_applied", "generation_config_json", "generation_config_sha256", "generation_determinism_contract", "generation_determinism_verified", "generation_strategy", "generation_do_sample", "generation_use_cache", "cache_implementation_contract", "generation_cache_implementation", "generation_cache_implementation_source", "generation_cache_config_present", "generation_num_beams", "generation_num_return_sequences", "generation_max_new_tokens", "generation_min_new_tokens", "generation_sampling_disabled", "generation_exact_new_tokens_required", "generation_token_contract", "generation_token_provenance_verified", "generated_new_token_count_min", "generated_new_token_count_max", "generated_new_token_exact_count_verified",
        "dense_reference_verified", "dense_reference_max_abs_error",
    ]
    out["missing_public_self_attestation_fields"] = [k for k in required_for_public if k not in meta]
    text_blob = " ".join(str(meta.get(k, "")) for k in meta).lower()
    red_terms = [t for t in ["fixture", "surrogate", "random", "synthetic", "local_tiny", "preflight"] if t in text_blob]
    if meta.get("preflight_fixture") is True:
        red_terms.append("preflight_fixture")
    out["red_flag_terms"] = sorted(set(red_terms))
    if out["schema"] not in {"qkv_npz_v1", PUBLIC_QKV_SCHEMA, "scores_values_npz_v1"}:
        out["status"] = "schema_invalid"
    elif out["missing_public_self_attestation_fields"]:
        out["status"] = "metadata_missing_public_self_attestation"
    else:
        out["status"] = "metadata_self_attestation_present"
    return out


def verify_qkv_score_contract(path: Path) -> dict:
    """Recompute the declared dense attention output from Q/K/V and score semantics.

    Public qkv_npz_v2 bundles must include explicit per-row attention scale,
    score bias (including mask/bias), and reference dense outputs produced by
    the model/runtime. The gate verifies shape, finiteness, and max-absolute
    parity rather than trusting a boolean label.
    """
    validate_npz_resource_limits(path)
    with np.load(path, allow_pickle=False) as data:
        files = set(data.files)
        if {"q", "k", "v"}.issubset(files):
            q, k, v = (np.asarray(data[x], dtype=np.float64) for x in ("q", "k", "v"))
        elif {"queries", "keys", "values"}.issubset(files):
            q, k, v = (np.asarray(data[x], dtype=np.float64) for x in ("queries", "keys", "values"))
        else:
            raise ValueError("public qkv contract requires q/k/v or queries/keys/values")
        if q.ndim != 2 or k.ndim != 3 or v.ndim != 3:
            raise ValueError("public qkv contract expects q [rows,d], k [rows,n,d], v [rows,n,dv]")
        rows, d_head = q.shape
        if k.shape[:1] != (rows,) or v.shape[:1] != (rows,) or k.shape[1] != v.shape[1] or k.shape[2] != d_head:
            raise ValueError(f"public qkv contract shape mismatch: q={q.shape} k={k.shape} v={v.shape}")
        if not all(name in files for name in ["attention_scale", "score_bias", "dense_reference_output"]):
            missing = [name for name in ["attention_scale", "score_bias", "dense_reference_output"] if name not in files]
            raise ValueError("public qkv contract missing arrays: " + ", ".join(missing))
        scale = np.asarray(data["attention_scale"], dtype=np.float64).reshape(-1)
        if scale.size == 1:
            scale = np.repeat(scale, rows)
        if scale.size != rows or not np.all(np.isfinite(scale)) or np.any(scale <= 0):
            raise ValueError(f"attention_scale must be finite positive scalar or [rows], got {scale.shape}")
        bias = np.asarray(data["score_bias"], dtype=np.float64)
        if bias.shape != (rows, k.shape[1]) or not np.all(np.isfinite(bias)):
            raise ValueError(f"score_bias must be finite [rows,n], got {bias.shape}")
        valid_key_len = None
        active_key_len = None
        valid_key_len_padding_rows = 0
        active_key_len_masked_rows = 0
        active_key_len_contract_verified = False
        position_contract_verified = False
        rotary_position_contract_verified = False
        rotary_position_global_offset_rows = 0
        token_contract: dict[str, object] = {"token_provenance_present": False, "token_provenance_verified": False, "errors": []}
        generation_contract: dict[str, object] = {"generation_token_present": False, "generation_token_provenance_verified": False, "errors": []}
        generation_config_sha256_value = ""
        generation_token_contract_value = ""
        generation_token_verified_value = None
        decode_position_rows = 0
        prefill_position_rows = 0
        if "valid_key_len" in files:
            valid_key_len = np.asarray(data["valid_key_len"], dtype=np.int64).reshape(-1)
            if valid_key_len.shape != (rows,):
                raise ValueError(f"valid_key_len must be int [rows], got {valid_key_len.shape}")
            if np.any(valid_key_len <= 0) or np.any(valid_key_len > k.shape[1]):
                raise ValueError("valid_key_len contains out-of-range physical KV lengths")
            for i, live in enumerate(valid_key_len):
                if int(live) < k.shape[1]:
                    valid_key_len_padding_rows += 1
                    if not np.all(bias[i, int(live):] < -1.0e20):
                        raise ValueError("valid_key_len padded tail is not masked with a finite negative sentinel")
        if "active_key_len" in files:
            if valid_key_len is None:
                raise ValueError("active_key_len requires valid_key_len")
            active_key_len = np.asarray(data["active_key_len"], dtype=np.int64).reshape(-1)
            if active_key_len.shape != (rows,):
                raise ValueError(f"active_key_len must be int [rows], got {active_key_len.shape}")
            ok_active = True
            for i, (active, live) in enumerate(zip(active_key_len, valid_key_len)):
                ai, li = int(active), int(live)
                if ai <= 0 or li <= 0 or ai > li or li > k.shape[1]:
                    ok_active = False
                    break
                if ai < li:
                    active_key_len_masked_rows += 1
                    if not np.all(bias[i, ai:li] < -1.0e20):
                        ok_active = False
                        break
                if li < k.shape[1] and not np.all(bias[i, li:] < -1.0e20):
                    ok_active = False
                    break
            active_key_len_contract_verified = bool(ok_active and active_key_len_masked_rows > 0)
        if {"position", "query_len", "capture_phase", "valid_key_len"}.issubset(files):
            positions = np.asarray(data["position"], dtype=np.int64).reshape(-1)
            query_len = np.asarray(data["query_len"], dtype=np.int64).reshape(-1)
            phases = np.asarray(data["capture_phase"]).reshape(-1)
            if not (positions.shape == query_len.shape == phases.shape == (rows,)):
                raise ValueError("position/query_len/capture_phase arrays must be [rows]")
            active_for_position = active_key_len if active_key_len is not None else (valid_key_len if valid_key_len is not None else np.full(rows, k.shape[1], dtype=np.int64))
            valid_for_position = valid_key_len if valid_key_len is not None else np.full(rows, k.shape[1], dtype=np.int64)
            ok = True
            for pos, q_len, phase, active, live in zip(positions, query_len, phases, active_for_position, valid_for_position):
                pos_i, q_i, active_i, live_i = int(pos), int(q_len), int(active), int(live)
                if live_i <= 0 or active_i <= 0 or active_i > live_i or q_i <= 0 or pos_i < 0 or pos_i >= active_i:
                    ok = False
                    break
                phase_text = str(phase)
                if phase_text == "decode_cached":
                    decode_position_rows += 1
                    if q_i != 1 or pos_i != active_i - 1:
                        ok = False
                        break
                elif phase_text == "prefill":
                    prefill_position_rows += 1
                    if pos_i >= q_i or active_i != pos_i + 1 or live_i < q_i:
                        ok = False
                        break
                else:
                    ok = False
                    break
            position_contract_verified = bool(ok and decode_position_rows > 0 and prefill_position_rows > 0)
        if {"rotary_position_id", "position", "query_len", "capture_phase"}.issubset(files):
            rotary_check = verify_rotary_position_contract(
                rotary_position_id=np.asarray(data["rotary_position_id"], dtype=np.int64),
                active_position=np.asarray(data["position"], dtype=np.int64),
                query_len=np.asarray(data["query_len"], dtype=np.int64),
                capture_phase=np.asarray(data["capture_phase"]),
            )
            rotary_position_contract_verified = bool(rotary_check.get("rotary_position_verified"))
            rotary_position_global_offset_rows = int(rotary_check.get("decode_rotary_global_offset_rows", 0))
        kv_group_map_present = False
        kv_group_map_verified = False
        gqa_grouped_rows = 0
        kv_group_errors: list[str] = []
        kv_group_contract_value = str(_npz_scalar(data, "kv_group_map_contract") or "")
        if {"head", "kv_head", "num_attention_heads", "num_key_value_heads", "num_key_value_groups"}.issubset(files):
            head_ids = np.asarray(data["head"], dtype=np.int64).reshape(-1)
            if head_ids.shape != (rows,):
                raise ValueError(f"head must be int [rows] for KV group verification, got {head_ids.shape}")
            kv_contract = verify_kv_group_map_contract(
                heads=head_ids,
                kv_head=np.asarray(data["kv_head"], dtype=np.int64),
                num_attention_heads=np.asarray(data["num_attention_heads"], dtype=np.int64),
                num_key_value_heads=np.asarray(data["num_key_value_heads"], dtype=np.int64),
                num_key_value_groups=np.asarray(data["num_key_value_groups"], dtype=np.int64),
            )
            kv_group_map_present = bool(kv_contract.get("kv_group_map_present"))
            kv_group_map_verified = bool(kv_contract.get("kv_group_map_verified"))
            gqa_grouped_rows = int(kv_contract.get("gqa_grouped_rows", 0))
            kv_group_errors = list(kv_contract.get("errors", []))
        reference = np.asarray(data["dense_reference_output"], dtype=np.float64)
        if reference.shape != (rows, v.shape[2]) or not np.all(np.isfinite(reference)):
            raise ValueError(f"dense_reference_output must be finite [rows,dv], got {reference.shape}")
        score_transform = str(_npz_scalar(data, "score_transform") or "")
        probability_contract_value = str(_npz_scalar(data, "probability_contract") or "")
        probability_dtype_value = str(_npz_scalar(data, "attention_probability_dtype") or "")
        probability_verified_value = _npz_scalar(data, "probability_semantics_verified")
        dropout_p_value = _npz_scalar(data, "attention_dropout_p")
        training_state_value = _npz_scalar(data, "attention_training_state")
        dropout_applied_value = _npz_scalar(data, "dropout_applied")
        active_key_len_contract_value = str(_npz_scalar(data, "active_key_len_contract") or "")
        position_contract_value = str(_npz_scalar(data, "position_contract") or "")
        rotary_position_contract_value = str(_npz_scalar(data, "rotary_position_contract") or "")
        rotary_position_verified_value = _npz_scalar(data, "rotary_position_ids_verified")
        rotary_position_present_count_value = _npz_scalar(data, "rotary_position_ids_present_call_count")
        if score_transform != PUBLIC_SCORE_TRANSFORM:
            raise ValueError(f"score_transform must be {PUBLIC_SCORE_TRANSFORM!r}")
        if probability_contract_value != PUBLIC_PROBABILITY_CONTRACT:
            raise ValueError(f"probability_contract must be {PUBLIC_PROBABILITY_CONTRACT!r}")
        if probability_dtype_value != PUBLIC_ATTENTION_PROBABILITY_DTYPE:
            raise ValueError(f"attention_probability_dtype must be {PUBLIC_ATTENTION_PROBABILITY_DTYPE!r}")
        if probability_verified_value is not True:
            raise ValueError("probability_semantics_verified must be true")
        try:
            dropout_p_float = float(dropout_p_value)
        except Exception as exc:
            raise ValueError("attention_dropout_p must be numeric") from exc
        if not math.isfinite(dropout_p_float) or abs(dropout_p_float) > 1e-12:
            raise ValueError("attention_dropout_p must be zero for public eager replay")
        if training_state_value is not False:
            raise ValueError("attention_training_state must be false for public eager replay")
        if dropout_applied_value is not False:
            raise ValueError("dropout_applied must be false for public eager replay")
        if rotary_position_contract_value != PUBLIC_ROTARY_POSITION_CONTRACT:
            raise ValueError(f"rotary_position_contract must be {PUBLIC_ROTARY_POSITION_CONTRACT!r}")
        if rotary_position_verified_value is not True:
            raise ValueError("rotary_position_ids_verified must be true")
        try:
            rotary_position_present_count = int(rotary_position_present_count_value)
        except Exception as exc:
            raise ValueError("rotary_position_ids_present_call_count must be an integer") from exc
        if rotary_position_present_count <= 0:
            raise ValueError("runtime RoPE position_ids were not observed by the capture hook")
        if not rotary_position_contract_verified:
            raise ValueError("runtime RoPE position_id contract was not verified")
        token_provenance_contract_value = str(_npz_scalar(data, "token_provenance_contract") or "")
        token_provenance_verified_value = _npz_scalar(data, "token_provenance_verified")
        prompt_count_value = _npz_scalar(data, "prompt_count")
        decode_steps_value = _npz_scalar(data, "decode_steps_requested")
        generation_config_json_value = str(_npz_scalar(data, "generation_config_json") or "")
        generation_config_sha256_value = str(_npz_scalar(data, "generation_config_sha256") or "")
        generation_determinism_contract_value = str(_npz_scalar(data, "generation_determinism_contract") or "")
        generation_determinism_verified_value = _npz_scalar(data, "generation_determinism_verified")
        generation_strategy_value = str(_npz_scalar(data, "generation_strategy") or "")
        generation_do_sample_value = _npz_scalar(data, "generation_do_sample")
        generation_use_cache_value = _npz_scalar(data, "generation_use_cache")
        cache_implementation_contract_value = str(_npz_scalar(data, "cache_implementation_contract") or "")
        generation_cache_implementation_value = str(_npz_scalar(data, "generation_cache_implementation") or "")
        generation_cache_implementation_source_value = str(_npz_scalar(data, "generation_cache_implementation_source") or "")
        generation_cache_config_present_value = _npz_scalar(data, "generation_cache_config_present")
        generation_num_beams_value = _npz_scalar(data, "generation_num_beams")
        generation_num_return_sequences_value = _npz_scalar(data, "generation_num_return_sequences")
        generation_max_new_tokens_value = _npz_scalar(data, "generation_max_new_tokens")
        generation_min_new_tokens_value = _npz_scalar(data, "generation_min_new_tokens")
        generation_sampling_disabled_value = _npz_scalar(data, "generation_sampling_disabled")
        generation_exact_new_tokens_required_value = _npz_scalar(data, "generation_exact_new_tokens_required")
        if token_provenance_contract_value != PUBLIC_TOKEN_PROVENANCE_CONTRACT:
            raise ValueError(f"token_provenance_contract must be {PUBLIC_TOKEN_PROVENANCE_CONTRACT!r}")
        if token_provenance_verified_value is not True:
            raise ValueError("token_provenance_verified must be true")
        if generation_do_sample_value is not False:
            raise ValueError("generation_do_sample must be false for deterministic public trace replay")
        if generation_use_cache_value is not True:
            raise ValueError("generation_use_cache must be true for cached-decode public trace replay")
        if cache_implementation_contract_value != PUBLIC_CACHE_IMPLEMENTATION_CONTRACT:
            raise ValueError(f"cache_implementation_contract must be {PUBLIC_CACHE_IMPLEMENTATION_CONTRACT!r}")
        if generation_cache_implementation_value != PUBLIC_REQUIRED_CACHE_IMPLEMENTATION:
            raise ValueError("generation_cache_implementation must be explicit dynamic cache for public trace replay")
        if generation_cache_implementation_source_value != "explicit_generate_argument":
            raise ValueError("generation_cache_implementation_source must be explicit_generate_argument")
        if generation_cache_config_present_value is not False:
            raise ValueError("generation_cache_config_present must be false for public trace replay")
        generation_determinism_contract = verify_generation_determinism_contract(
            generation_config_json=np.asarray([generation_config_json_value]),
            generation_config_sha256=generation_config_sha256_value,
            generation_determinism_contract=generation_determinism_contract_value,
            generation_determinism_verified=generation_determinism_verified_value,
            generation_strategy=generation_strategy_value,
            generation_do_sample=generation_do_sample_value,
            generation_use_cache=generation_use_cache_value,
            cache_implementation_contract=cache_implementation_contract_value,
            generation_cache_implementation=generation_cache_implementation_value,
            generation_cache_implementation_source=generation_cache_implementation_source_value,
            generation_cache_config_present=generation_cache_config_present_value,
            generation_num_beams=generation_num_beams_value,
            generation_num_return_sequences=generation_num_return_sequences_value,
            generation_max_new_tokens=generation_max_new_tokens_value,
            generation_min_new_tokens=generation_min_new_tokens_value,
            generation_sampling_disabled=generation_sampling_disabled_value,
            generation_exact_new_tokens_required=generation_exact_new_tokens_required_value,
            decode_steps_requested=int(decode_steps_value),
        )
        if not generation_determinism_contract.get("generation_determinism_verified"):
            raise ValueError("generation determinism contract was not verified: " + "; ".join(generation_determinism_contract.get("errors", [])))
        required_prompt_manifest_arrays = {"prompt_manifest_contract", "prompt_manifest_json", "prompt_manifest_sha256", "tokenization_settings_json", "tokenization_settings_sha256", "tokenization_add_special_tokens", "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask", "tokenization_return_tensors", "chat_template_applied"}
        if not required_prompt_manifest_arrays.issubset(files):
            raise ValueError("prompt manifest/tokenization arrays are required: " + ", ".join(sorted(required_prompt_manifest_arrays - files)))
        if not {"prompt_id", "prompt_token_count", "prompt_input_ids_sha256", "prompt_attention_mask_sha256", "prompt_text_sha256"}.issubset(files):
            raise ValueError("token provenance arrays are required: prompt_id, prompt_token_count, prompt_input_ids_sha256, prompt_attention_mask_sha256, prompt_text_sha256")
        prompt_manifest_contract = verify_prompt_manifest_contract(
            prompt_manifest_contract=_npz_scalar(data, "prompt_manifest_contract"),
            prompt_manifest_json=np.asarray(data["prompt_manifest_json"]),
            prompt_manifest_sha256=_npz_scalar(data, "prompt_manifest_sha256"),
            tokenization_settings_json=np.asarray(data["tokenization_settings_json"]),
            tokenization_settings_sha256=_npz_scalar(data, "tokenization_settings_sha256"),
            prompt_count=int(prompt_count_value),
            prompt_token_count=np.asarray(data["prompt_token_count"], dtype=np.int64),
            prompt_input_ids_sha256=np.asarray(data["prompt_input_ids_sha256"]),
            prompt_attention_mask_sha256=np.asarray(data["prompt_attention_mask_sha256"]),
            prompt_text_sha256=np.asarray(data["prompt_text_sha256"]),
            tokenization_add_special_tokens=_npz_scalar(data, "tokenization_add_special_tokens"),
            tokenization_padding=_npz_scalar(data, "tokenization_padding"),
            tokenization_truncation=_npz_scalar(data, "tokenization_truncation"),
            tokenization_return_attention_mask=_npz_scalar(data, "tokenization_return_attention_mask"),
            tokenization_return_tensors=_npz_scalar(data, "tokenization_return_tensors"),
            chat_template_applied=_npz_scalar(data, "chat_template_applied"),
        )
        if not prompt_manifest_contract.get("prompt_manifest_verified"):
            raise ValueError("prompt manifest contract was not verified: " + "; ".join(prompt_manifest_contract.get("errors", [])))
        token_contract = verify_token_provenance_contract(
            prompt_id=np.asarray(data["prompt_id"], dtype=np.int64),
            position=np.asarray(data["position"], dtype=np.int64),
            capture_phase=np.asarray(data["capture_phase"]),
            prompt_count=int(prompt_count_value),
            prompt_token_count=np.asarray(data["prompt_token_count"], dtype=np.int64),
            prompt_input_ids_sha256=np.asarray(data["prompt_input_ids_sha256"]),
            prompt_attention_mask_sha256=np.asarray(data["prompt_attention_mask_sha256"]),
            prompt_text_sha256=np.asarray(data["prompt_text_sha256"]),
            decode_steps_requested=int(decode_steps_value),
        )
        if not token_contract.get("token_provenance_verified"):
            raise ValueError("token provenance contract was not verified: " + "; ".join(token_contract.get("errors", [])))
        generation_token_contract_value = str(_npz_scalar(data, "generation_token_contract") or "")
        generation_token_verified_value = _npz_scalar(data, "generation_token_provenance_verified")
        if generation_token_contract_value != PUBLIC_GENERATION_TOKEN_CONTRACT:
            raise ValueError(f"generation_token_contract must be {PUBLIC_GENERATION_TOKEN_CONTRACT!r}")
        if generation_token_verified_value is not True:
            raise ValueError("generation_token_provenance_verified must be true")
        required_generation_arrays = {"generated_sequence_sha256", "generated_new_token_ids_sha256", "generated_new_token_count", "generated_sequence_token_count", "generation_prompt_prefix_verified"}
        if not required_generation_arrays.issubset(files):
            raise ValueError("generated-token provenance arrays are required: " + ", ".join(sorted(required_generation_arrays)))
        generation_contract = verify_generation_token_contract(
            prompt_id=np.asarray(data["prompt_id"], dtype=np.int64),
            position=np.asarray(data["position"], dtype=np.int64),
            capture_phase=np.asarray(data["capture_phase"]),
            prompt_token_count=np.asarray(data["prompt_token_count"], dtype=np.int64),
            generated_sequence_sha256=np.asarray(data["generated_sequence_sha256"]),
            generated_new_token_ids_sha256=np.asarray(data["generated_new_token_ids_sha256"]),
            generated_new_token_count=np.asarray(data["generated_new_token_count"], dtype=np.int64),
            generated_sequence_token_count=np.asarray(data["generated_sequence_token_count"], dtype=np.int64),
            generation_prompt_prefix_verified=np.asarray(data["generation_prompt_prefix_verified"], dtype=bool),
            decode_steps_requested=int(decode_steps_value),
        )
        if not generation_contract.get("generation_token_provenance_verified"):
            raise ValueError("generated-token provenance contract was not verified: " + "; ".join(generation_contract.get("errors", [])))
        runtime_contract = verify_runtime_provenance_contract({k: _npz_scalar(data, k) for k in PUBLIC_RUNTIME_PROVENANCE_FIELDS})
        if not runtime_contract.get("runtime_provenance_verified"):
            raise ValueError("runtime device/dtype/timing provenance was not verified: " + "; ".join(runtime_contract.get("errors", [])))
    scores = np.einsum("rd,rnd->rn", q, k) * scale[:, None] + bias
    scores32 = np.asarray(scores, dtype=np.float32)
    scores32 -= np.max(scores32, axis=1, keepdims=True)
    probs32 = np.exp(scores32).astype(np.float32)
    probs32 /= np.sum(probs32, axis=1, keepdims=True, dtype=np.float32)
    probs = probs32.astype(np.float64)
    reconstructed = np.einsum("rn,rnd->rd", probs, v)
    per_row_error = np.max(np.abs(reconstructed - reference), axis=1)
    return {
        "rows": int(rows),
        "tokens": int(k.shape[1]),
        "d_head": int(d_head),
        "d_value": int(v.shape[2]),
        "score_transform": score_transform,
        "probability_contract": probability_contract_value,
        "probability_semantics_verified": bool(probability_verified_value),
        "attention_probability_dtype": probability_dtype_value,
        "attention_dropout_p": float(dropout_p_float),
        "valid_key_len_present": bool(valid_key_len is not None),
        "valid_key_len_padding_rows": int(valid_key_len_padding_rows),
        "active_key_len_present": bool(active_key_len is not None),
        "active_key_len_masked_rows": int(active_key_len_masked_rows),
        "active_key_len_contract": active_key_len_contract_value,
        "active_key_len_contract_verified": bool(active_key_len_contract_verified),
        "kv_group_map_present": bool(kv_group_map_present),
        "kv_group_map_contract": kv_group_contract_value,
        "kv_group_map_verified": bool(kv_group_map_verified),
        "gqa_grouped_rows": int(gqa_grouped_rows),
        "kv_group_map_errors": kv_group_errors,
        "position_contract": position_contract_value,
        "position_contract_verified": bool(position_contract_verified),
        "rotary_position_contract": rotary_position_contract_value,
        "rotary_position_contract_verified": bool(rotary_position_contract_verified),
        "rotary_position_global_offset_rows": int(rotary_position_global_offset_rows),
        "token_provenance_contract": str(_npz_scalar(data, "token_provenance_contract") or ""),
        "token_provenance_present": bool(token_contract.get("token_provenance_present")),
        "token_provenance_verified": bool(token_contract.get("token_provenance_verified")),
        "prompt_count": token_contract.get("prompt_count"),
        "prompt_token_count_min": token_contract.get("prompt_token_count_min"),
        "prompt_token_count_max": token_contract.get("prompt_token_count_max"),
        "prefill_rows_with_prompt_position": int(token_contract.get("prefill_rows_with_prompt_position", 0) or 0),
        "decode_rows_after_prompt": int(token_contract.get("decode_rows_after_prompt", 0) or 0),
        "token_provenance_errors": list(token_contract.get("errors", [])),
        "prompt_manifest_contract": str(_npz_scalar(data, "prompt_manifest_contract") or ""),
        "prompt_manifest_present": bool(prompt_manifest_contract.get("prompt_manifest_present")),
        "prompt_manifest_verified": bool(prompt_manifest_contract.get("prompt_manifest_verified")),
        "prompt_manifest_errors": list(prompt_manifest_contract.get("errors", [])),
        "generation_config_sha256": str(generation_config_sha256_value),
        "generation_determinism_contract": str(generation_determinism_contract_value),
        "generation_determinism_verified": bool(generation_determinism_contract.get("generation_determinism_verified")),
        "generation_strategy": str(generation_strategy_value),
        "cache_implementation_contract": str(cache_implementation_contract_value),
        "generation_cache_implementation": str(generation_cache_implementation_value),
        "generation_cache_implementation_source": str(generation_cache_implementation_source_value),
        "generation_cache_config_present": bool(generation_cache_config_present_value),
        "generation_num_beams": int(generation_determinism_contract.get("num_beams") or 0),
        "generation_num_return_sequences": int(generation_determinism_contract.get("num_return_sequences") or 0),
        "generation_max_new_tokens": int(generation_determinism_contract.get("max_new_tokens") or 0),
        "generation_min_new_tokens": int(generation_determinism_contract.get("min_new_tokens") or 0),
        "generation_determinism_errors": list(generation_determinism_contract.get("errors", [])),
        "generation_token_contract": str(generation_token_contract_value),
        "generation_token_provenance_verified": bool(generation_contract.get("generation_token_provenance_verified")),
        "generated_new_token_count_min": generation_contract.get("generated_new_token_count_min"),
        "generated_new_token_count_max": generation_contract.get("generated_new_token_count_max"),
        "generated_new_token_exact_count_verified": bool(generation_contract.get("generated_new_token_exact_count_verified")),
        "decode_rows_inside_generated_suffix": int(generation_contract.get("decode_rows_inside_generated_suffix", 0) or 0),
        "generation_token_errors": list(generation_contract.get("errors", [])),
        "runtime_provenance_contract": str(_npz_scalar(data, "runtime_provenance_contract") or ""),
        "runtime_provenance_verified": bool((runtime_contract if 'runtime_contract' in locals() else {}).get("runtime_provenance_verified", False)),
        "runtime_provenance_errors": list((runtime_contract if 'runtime_contract' in locals() else {}).get("errors", [])),
        "requested_torch_dtype": str(_npz_scalar(data, "requested_torch_dtype") or ""),
        "resolved_torch_dtype": str(_npz_scalar(data, "resolved_torch_dtype") or ""),
        "actual_primary_device": str(_npz_scalar(data, "actual_primary_device") or ""),
        "timing_clock_contract": str(_npz_scalar(data, "timing_clock_contract") or ""),
        "named_hardware_timing_measured": bool(_npz_scalar(data, "named_hardware_timing_measured")),
        "decode_position_rows": int(decode_position_rows),
        "prefill_position_rows": int(prefill_position_rows),
        "computed_dense_reference_max_abs_error": float(np.max(per_row_error)),
        "computed_dense_reference_mean_row_max_abs_error": float(np.mean(per_row_error)),
    }


def validate_public_trace_provenance(provenance_json: Path | None, trace_npz: Path | None) -> dict:
    """Validate whether an external NPZ may be called public/pretrained evidence.

    rev0072 required a provenance manifest. rev0073 tightens the contract by
    cross-checking that manifest against self-attestation metadata embedded in
    the trace bundle.  Schema-valid traces still load as external traces without
    this metadata, but they are not accepted as public/pretrained evidence.
    """
    allowed_sources = {"public_pretrained_hf", "public_pretrained_transformerlens", "public_pretrained_manual_export"}
    npz_status = inspect_trace_npz_metadata(trace_npz)
    status = {
        "accepted": False,
        "status": "missing_provenance_manifest",
        "provenance_json": provenance_json.as_posix() if provenance_json else None,
        "errors": [],
        "warnings": [],
        "npz_metadata_status": npz_status,
        "required_fields": [
            "trace_claim_version", "public_pretrained_trace", "source_type",
            "model_id", "model_load_source", "model_load_source_is_local_path",
            "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype",
            "requested_device_policy", "actual_primary_device", "model_parameter_dtype_set",
            "model_device_set", "model_parameter_tensor_count", "cuda_available", "cuda_device_count",
            "cuda_device_name", "cuda_device_capability", "timing_clock_contract",
            "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized", "timing_cuda_event_recorded",
            "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
            "model_revision", "tokenizer_revision", "code_revision", "trust_remote_code",
            "weights_source", "license", "trace_npz_sha256", "schema", "capture_tool", "capture_tool_sha256",
            "config_sha256", "generated_from_local_tiny_model", "uses_random_weights",
            "provenance_reviewed", "d_head", "attention_backend", "attention_score_input_stage",
            "attention_score_inputs_verified", "score_transform", "probability_contract", "probability_semantics_verified", "attention_probability_dtype", "attention_dropout_p", "attention_training_state", "dropout_applied", "attention_scale_verified", "score_bias_verified",
            "mask_challenge_exercised", "attention_mask_backend_preserved", "custom_attention_backend_used",
            "capture_phase_contract", "prefill_phase_present", "decode_phase_present", "cache_decode_verified",
            "valid_key_len_semantics_verified", "active_key_len_contract", "active_key_len_semantics_verified",
            "kv_group_map_contract", "kv_group_map_verified", "gqa_grouped_rows_present",
            "position_contract", "absolute_position_verified", "rotary_position_contract", "rotary_position_ids_verified", "rotary_position_ids_present_call_count", "decode_steps_requested",
            "token_provenance_contract", "token_provenance_verified", "prompt_count", "prompt_token_count_min", "prompt_token_count_max", "prompt_manifest_contract", "prompt_manifest_sha256", "tokenization_settings_sha256", "tokenization_add_special_tokens", "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask", "tokenization_return_tensors", "chat_template_applied", "generation_config_json", "generation_config_sha256", "generation_determinism_contract", "generation_determinism_verified", "generation_strategy", "generation_do_sample", "generation_use_cache", "cache_implementation_contract", "generation_cache_implementation", "generation_cache_implementation_source", "generation_cache_config_present", "generation_num_beams", "generation_num_return_sequences", "generation_max_new_tokens", "generation_min_new_tokens", "generation_sampling_disabled", "generation_exact_new_tokens_required", "generation_token_contract", "generation_token_provenance_verified", "generated_new_token_count_min", "generated_new_token_count_max", "generated_new_token_exact_count_verified",
            "dense_reference_verified", "dense_reference_max_abs_error",
        ],
    }
    if trace_npz is None:
        status["errors"].append("no external trace NPZ supplied")
        status["status"] = "no_external_trace"
        return status
    if provenance_json is None:
        status["errors"].append("--provenance-json is required for public/pretrained trace claims")
        return status
    if not provenance_json.exists():
        status["errors"].append("provenance manifest does not exist")
        status["status"] = "provenance_manifest_missing_on_disk"
        return status
    try:
        data = json.loads(provenance_json.read_text(encoding="utf-8"))
    except Exception as exc:
        status["errors"].append(f"could not parse provenance JSON: {exc}")
        status["status"] = "provenance_manifest_unparseable"
        return status
    status["manifest"] = {k: data.get(k) for k in status["required_fields"] if k in data}
    for key in status["required_fields"]:
        if key not in data:
            status["errors"].append(f"missing required provenance field: {key}")
    if data.get("trace_claim_version") != PUBLIC_TRACE_CLAIM_VERSION:
        status["errors"].append(f"trace_claim_version must be {PUBLIC_TRACE_CLAIM_VERSION!r}")
    if data.get("public_pretrained_trace") is not True:
        status["errors"].append("manifest public_pretrained_trace must be true")
    if data.get("source_type") not in allowed_sources:
        status["errors"].append("source_type is not an accepted public/pretrained source")
    if not str(data.get("model_id", "")).strip():
        status["errors"].append("model_id is required")
    if not str(data.get("model_load_source", "")).strip():
        status["errors"].append("model_load_source is required so local snapshot paths cannot erase canonical public model identity")
    if not isinstance(data.get("model_load_source_is_local_path"), bool):
        status["errors"].append("model_load_source_is_local_path must be boolean")
    if not _is_immutable_revision(data.get("model_revision")):
        status["errors"].append("model_revision must be an immutable full commit/content hash, not a branch or tag")
    if not _is_immutable_revision(data.get("tokenizer_revision")):
        status["errors"].append("tokenizer_revision must be an immutable full commit/content hash")
    if data.get("trust_remote_code") is True and not _is_immutable_revision(data.get("code_revision")):
        status["errors"].append("code_revision must be immutable when trust_remote_code is true")
    if not str(data.get("weights_source", "")).strip():
        status["errors"].append("weights_source is required")
    if not str(data.get("license", "")).strip():
        status["errors"].append("license/source terms are required")
    if data.get("generated_from_local_tiny_model") is not False:
        status["errors"].append("local tiny/surrogate traces cannot be promoted as public/pretrained")
    if data.get("uses_random_weights") is not False:
        status["errors"].append("random-weight traces cannot be promoted as public/pretrained")
    if data.get("provenance_reviewed") is not True:
        status["errors"].append("provenance_reviewed must be true")
    if str(data.get("schema", "")) != PUBLIC_QKV_SCHEMA:
        status["errors"].append(f"public/pretrained claims require {PUBLIC_QKV_SCHEMA}; older qkv or score-only bundles remain diagnostic")
    if not _is_hex_sha256(data.get("config_sha256")):
        status["errors"].append("config_sha256 must be a hex sha256")
    if data.get("attention_score_input_stage") != PUBLIC_SCORE_INPUT_STAGE:
        status["errors"].append(f"attention_score_input_stage must be {PUBLIC_SCORE_INPUT_STAGE!r}")
    if data.get("attention_score_inputs_verified") is not True:
        status["errors"].append("attention_score_inputs_verified must be true")
    if data.get("score_transform") != PUBLIC_SCORE_TRANSFORM:
        status["errors"].append(f"score_transform must be {PUBLIC_SCORE_TRANSFORM!r}")
    if data.get("probability_contract") != PUBLIC_PROBABILITY_CONTRACT:
        status["errors"].append(f"probability_contract must be {PUBLIC_PROBABILITY_CONTRACT!r}")
    if data.get("probability_semantics_verified") is not True:
        status["errors"].append("probability_semantics_verified must be true")
    if data.get("attention_probability_dtype") != PUBLIC_ATTENTION_PROBABILITY_DTYPE:
        status["errors"].append(f"attention_probability_dtype must be {PUBLIC_ATTENTION_PROBABILITY_DTYPE!r}")
    try:
        if abs(float(data.get("attention_dropout_p"))) > 1e-12:
            status["errors"].append("attention_dropout_p must be zero")
    except Exception:
        status["errors"].append("attention_dropout_p must be numeric")
    if data.get("attention_training_state") is not False:
        status["errors"].append("attention_training_state must be false")
    if data.get("dropout_applied") is not False:
        status["errors"].append("dropout_applied must be false")
    if data.get("attention_scale_verified") is not True:
        status["errors"].append("attention_scale_verified must be true")
    if data.get("score_bias_verified") is not True:
        status["errors"].append("score_bias_verified must be true")
    if data.get("mask_challenge_exercised") is not True:
        status["errors"].append("mask_challenge_exercised must be true so the capture proves causal/padding mask preservation")
    if data.get("attention_mask_backend_preserved") is not True:
        status["errors"].append("attention_mask_backend_preserved must be true")
    if data.get("custom_attention_backend_used") is True:
        status["errors"].append("custom_attention_backend_used must be false unless a matching mask formatter is independently audited")
    if data.get("capture_phase_contract") != PUBLIC_CAPTURE_PHASE_CONTRACT:
        status["errors"].append(f"capture_phase_contract must be {PUBLIC_CAPTURE_PHASE_CONTRACT!r}")
    if data.get("prefill_phase_present") is not True:
        status["errors"].append("prefill_phase_present must be true")
    if data.get("decode_phase_present") is not True:
        status["errors"].append("decode_phase_present must be true so the trace covers cached generation, not only prefill")
    if data.get("cache_decode_verified") is not True:
        status["errors"].append("cache_decode_verified must be true")
    if data.get("valid_key_len_semantics_verified") is not True:
        status["errors"].append("valid_key_len_semantics_verified must be true for mixed prefill/decode context lengths")
    if data.get("active_key_len_contract") != PUBLIC_ACTIVE_KEY_CONTRACT:
        status["errors"].append(f"active_key_len_contract must be {PUBLIC_ACTIVE_KEY_CONTRACT!r}")
    if data.get("active_key_len_semantics_verified") is not True:
        status["errors"].append("active_key_len_semantics_verified must be true; masked causal/static-cache tokens must not be counted as active scored keys")
    if data.get("kv_group_map_contract") != PUBLIC_KV_GROUP_CONTRACT:
        status["errors"].append(f"kv_group_map_contract must be {PUBLIC_KV_GROUP_CONTRACT!r}")
    if data.get("kv_group_map_verified") is not True:
        status["errors"].append("kv_group_map_verified must be true; query-head rows must carry exact KV-head ownership for MHA/GQA/MQA cost accounting")
    if data.get("position_contract") != PUBLIC_POSITION_CONTRACT:
        status["errors"].append(f"position_contract must be {PUBLIC_POSITION_CONTRACT!r}")
    if data.get("absolute_position_verified") is not True:
        status["errors"].append("absolute_position_verified must be true; cached-decode rows must use absolute key positions, not local q_len indices")
    if data.get("rotary_position_contract") != PUBLIC_ROTARY_POSITION_CONTRACT:
        status["errors"].append(f"rotary_position_contract must be {PUBLIC_ROTARY_POSITION_CONTRACT!r}")
    if data.get("rotary_position_ids_verified") is not True:
        status["errors"].append("rotary_position_ids_verified must be true; runtime RoPE position_ids must be exported per row")
    try:
        if int(data.get("rotary_position_ids_present_call_count")) <= 0:
            status["errors"].append("rotary_position_ids_present_call_count must be positive; the capture hook must observe runtime position_ids, not synthesize them silently")
    except Exception:
        status["errors"].append("rotary_position_ids_present_call_count must be a positive integer")
    try:
        if int(data.get("decode_steps_requested")) <= 0:
            status["errors"].append("decode_steps_requested must be positive for public/pretrained trace claims")
    except Exception:
        status["errors"].append("decode_steps_requested must be a positive integer")
    if data.get("token_provenance_contract") != PUBLIC_TOKEN_PROVENANCE_CONTRACT:
        status["errors"].append(f"token_provenance_contract must be {PUBLIC_TOKEN_PROVENANCE_CONTRACT!r}")
    if data.get("token_provenance_verified") is not True:
        status["errors"].append("token_provenance_verified must be true; exact tokenizer input_ids/attention_mask digests must bind rows to prompts")
    try:
        if int(data.get("prompt_count")) <= 0 or int(data.get("prompt_token_count_min")) <= 0 or int(data.get("prompt_token_count_max")) < int(data.get("prompt_token_count_min")):
            status["errors"].append("prompt_count and prompt_token_count min/max must be positive and ordered")
    except Exception:
        status["errors"].append("prompt_count and prompt_token_count min/max must be integers")
    if not _is_hex_sha256_text(data.get("generation_config_sha256")):
        status["errors"].append("generation_config_sha256 must be a SHA-256 hex digest")
    manifest_generation_determinism = verify_generation_determinism_contract(
        generation_config_json=np.asarray([str(data.get("generation_config_json", ""))]),
        generation_config_sha256=str(data.get("generation_config_sha256", "")),
        generation_determinism_contract=str(data.get("generation_determinism_contract", "")),
        generation_determinism_verified=data.get("generation_determinism_verified"),
        generation_strategy=str(data.get("generation_strategy", "")),
        generation_do_sample=data.get("generation_do_sample"),
        generation_use_cache=data.get("generation_use_cache"),
        cache_implementation_contract=data.get("cache_implementation_contract"),
        generation_cache_implementation=data.get("generation_cache_implementation"),
        generation_cache_implementation_source=data.get("generation_cache_implementation_source"),
        generation_cache_config_present=data.get("generation_cache_config_present"),
        generation_num_beams=data.get("generation_num_beams"),
        generation_num_return_sequences=data.get("generation_num_return_sequences"),
        generation_max_new_tokens=data.get("generation_max_new_tokens"),
        generation_min_new_tokens=data.get("generation_min_new_tokens"),
        generation_sampling_disabled=data.get("generation_sampling_disabled"),
        generation_exact_new_tokens_required=data.get("generation_exact_new_tokens_required"),
        decode_steps_requested=data.get("decode_steps_requested"),
    )
    if not manifest_generation_determinism.get("generation_determinism_verified"):
        status["errors"].append("generation determinism contract was not verified in manifest: " + "; ".join(manifest_generation_determinism.get("errors", [])))
    if data.get("generation_do_sample") is not False:
        status["errors"].append("generation_do_sample must be false for deterministic replay")
    if data.get("generation_use_cache") is not True:
        status["errors"].append("generation_use_cache must be true for cached-decode replay")
    if data.get("cache_implementation_contract") != PUBLIC_CACHE_IMPLEMENTATION_CONTRACT:
        status["errors"].append("cache_implementation_contract must identify explicit dynamic-cache contract")
    if data.get("generation_cache_implementation") != PUBLIC_REQUIRED_CACHE_IMPLEMENTATION:
        status["errors"].append("generation_cache_implementation must be dynamic; static/offloaded/quantized caches are timing/baseline lanes")
    if data.get("generation_cache_implementation_source") != "explicit_generate_argument":
        status["errors"].append("generation_cache_implementation_source must be explicit_generate_argument")
    if data.get("generation_cache_config_present") is not False:
        status["errors"].append("generation_cache_config_present must be false")
    try:
        if int(data.get("generation_num_beams")) != 1 or int(data.get("generation_num_return_sequences")) != 1:
            status["errors"].append("generation_num_beams and generation_num_return_sequences must both be 1 for greedy public replay")
        if int(data.get("generation_max_new_tokens")) != int(data.get("decode_steps_requested")):
            status["errors"].append("generation_max_new_tokens must equal decode_steps_requested")
        if int(data.get("generation_min_new_tokens")) != int(data.get("decode_steps_requested")):
            status["errors"].append("generation_min_new_tokens must equal decode_steps_requested")
    except Exception:
        status["errors"].append("generation beam/return/min-max-new-token metadata must be integers")
    if data.get("generation_token_contract") != PUBLIC_GENERATION_TOKEN_CONTRACT:
        status["errors"].append(f"generation_token_contract must be {PUBLIC_GENERATION_TOKEN_CONTRACT!r}")
    if data.get("generation_token_provenance_verified") is not True:
        status["errors"].append("generation_token_provenance_verified must be true; exact generated-token sequence digests must bind cached-decode rows")
    if data.get("generation_exact_new_tokens_required") is not True:
        status["errors"].append("generation_exact_new_tokens_required must be true")
    if data.get("generated_new_token_exact_count_verified") is not True:
        status["errors"].append("generated_new_token_exact_count_verified must be true")
    try:
        if int(data.get("generated_new_token_count_min")) <= 0 or int(data.get("generated_new_token_count_max")) < int(data.get("generated_new_token_count_min")):
            status["errors"].append("generated_new_token_count min/max must be positive and ordered")
        if int(data.get("generated_new_token_count_min")) != int(data.get("decode_steps_requested")) or int(data.get("generated_new_token_count_max")) != int(data.get("decode_steps_requested")):
            status["errors"].append("generated_new_token_count min/max must both equal decode_steps_requested")
    except Exception:
        status["errors"].append("generated_new_token_count min/max must be integers")
    runtime_contract = verify_runtime_provenance_contract(data)
    if not runtime_contract.get("runtime_provenance_verified"):
        status["errors"].append("runtime device/dtype/timing provenance was not verified: " + "; ".join(runtime_contract.get("errors", [])))
    status["runtime_provenance_status"] = runtime_contract
    if data.get("dense_reference_verified") is not True:
        status["errors"].append("dense_reference_verified must be true")
    try:
        dense_err = float(data.get("dense_reference_max_abs_error"))
        if not math.isfinite(dense_err) or dense_err > PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            status["errors"].append(f"dense_reference_max_abs_error must be finite and <= {PUBLIC_DENSE_PARITY_MAX_ABS_ERROR}")
    except Exception:
        status["errors"].append("dense_reference_max_abs_error must be numeric")
    expected_sha = str(data.get("trace_npz_sha256", ""))
    actual_sha = sha256_file(trace_npz) if trace_npz.exists() else None
    status["trace_npz_sha256_actual"] = actual_sha
    if not expected_sha or expected_sha != actual_sha:
        status["errors"].append("trace_npz_sha256 does not match supplied NPZ")
    tool_sha = str(data.get("capture_tool_sha256", ""))
    if not _is_hex_sha256(tool_sha):
        status["errors"].append("capture_tool_sha256 must be a hex sha256")
    capture_tool = str(data.get("capture_tool", ""))
    if capture_tool:
        tool_path = (ROOT / capture_tool) if not Path(capture_tool).is_absolute() else Path(capture_tool)
        if tool_path.exists() and tool_sha and sha256_file(tool_path) != tool_sha:
            status["errors"].append("capture_tool_sha256 does not match capture_tool file in capsule")
        elif not tool_path.exists():
            status["warnings"].append("capture_tool file not present in capsule; hash recorded but not locally cross-checked")

    # rev0073 metadata self-attestation cross-check.
    meta = npz_status.get("metadata", {}) or {}
    if npz_status.get("schema") != data.get("schema"):
        status["errors"].append("NPZ schema does not match manifest schema")
    missing_meta = npz_status.get("missing_public_self_attestation_fields", [])
    if missing_meta:
        status["errors"].append("NPZ missing public self-attestation metadata: " + ", ".join(missing_meta))
    if meta.get("trace_claim_version") != PUBLIC_TRACE_CLAIM_VERSION:
        status["errors"].append(f"NPZ trace_claim_version must be {PUBLIC_TRACE_CLAIM_VERSION!r}")
    if meta.get("public_pretrained_trace") is not True:
        status["errors"].append("NPZ self-attestation public_pretrained_trace must be true")
    if meta.get("source_type") not in allowed_sources:
        status["errors"].append("NPZ self-attestation source_type is not accepted for public/pretrained traces")
    for key in [
        "trace_claim_version", "public_pretrained_trace", "model_id", "model_load_source", "model_load_source_is_local_path",
        "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype",
        "requested_device_policy", "actual_primary_device", "model_parameter_dtype_set",
        "model_device_set", "model_parameter_tensor_count", "cuda_available", "cuda_device_count",
        "cuda_device_name", "cuda_device_capability", "timing_clock_contract",
        "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized", "timing_cuda_event_recorded",
        "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
        "model_revision", "tokenizer_revision", "code_revision", "trust_remote_code",
        "weights_source", "license", "source_type", "schema", "capture_tool", "capture_tool_sha256",
        "config_sha256", "generated_from_local_tiny_model", "uses_random_weights", "provenance_reviewed",
        "d_head", "attention_backend", "attention_score_input_stage", "attention_score_inputs_verified",
        "score_transform", "probability_contract", "probability_semantics_verified",
        "attention_probability_dtype", "attention_dropout_p", "attention_training_state", "dropout_applied",
        "attention_scale_verified", "score_bias_verified",
        "mask_challenge_exercised", "attention_mask_backend_preserved", "custom_attention_backend_used",
        "capture_phase_contract", "prefill_phase_present", "decode_phase_present", "cache_decode_verified",
        "valid_key_len_semantics_verified", "active_key_len_contract", "active_key_len_semantics_verified",
        "kv_group_map_contract", "kv_group_map_verified", "gqa_grouped_rows_present",
        "position_contract", "absolute_position_verified", "rotary_position_contract", "rotary_position_ids_verified", "rotary_position_ids_present_call_count", "decode_steps_requested",
        "token_provenance_contract", "token_provenance_verified", "prompt_count", "prompt_token_count_min", "prompt_token_count_max", "prompt_manifest_contract", "prompt_manifest_sha256", "tokenization_settings_sha256", "tokenization_add_special_tokens", "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask", "tokenization_return_tensors", "chat_template_applied", "generation_config_json", "generation_config_sha256", "generation_determinism_contract", "generation_determinism_verified", "generation_strategy", "generation_do_sample", "generation_use_cache", "cache_implementation_contract", "generation_cache_implementation", "generation_cache_implementation_source", "generation_cache_config_present", "generation_num_beams", "generation_num_return_sequences", "generation_max_new_tokens", "generation_min_new_tokens", "generation_sampling_disabled", "generation_exact_new_tokens_required", "generation_token_contract", "generation_token_provenance_verified", "generated_new_token_count_min", "generated_new_token_count_max", "generated_new_token_exact_count_verified",
        "dense_reference_verified", "dense_reference_max_abs_error",
    ]:
        if key in meta and key in data and str(meta.get(key)) != str(data.get(key)):
            status["errors"].append(f"NPZ self-attestation {key} does not match manifest")
    if meta.get("attention_score_input_stage") != PUBLIC_SCORE_INPUT_STAGE:
        status["errors"].append("NPZ Q/K tensors are not attested as post-model-transform attention score inputs")
    if meta.get("attention_score_inputs_verified") is not True:
        status["errors"].append("NPZ attention score inputs are not verified")
    if meta.get("score_transform") != PUBLIC_SCORE_TRANSFORM:
        status["errors"].append("NPZ score transform is unsupported or unverified")
    if meta.get("probability_contract") != PUBLIC_PROBABILITY_CONTRACT:
        status["errors"].append(f"NPZ probability_contract must be {PUBLIC_PROBABILITY_CONTRACT!r}")
    if meta.get("probability_semantics_verified") is not True:
        status["errors"].append("NPZ probability semantics are not verified")
    if meta.get("attention_probability_dtype") != PUBLIC_ATTENTION_PROBABILITY_DTYPE:
        status["errors"].append(f"NPZ attention_probability_dtype must be {PUBLIC_ATTENTION_PROBABILITY_DTYPE!r}")
    try:
        if abs(float(meta.get("attention_dropout_p"))) > 1e-12:
            status["errors"].append("NPZ attention_dropout_p must be zero")
    except Exception:
        status["errors"].append("NPZ attention_dropout_p is missing or non-numeric")
    if meta.get("attention_training_state") is not False:
        status["errors"].append("NPZ attention_training_state must be false")
    if meta.get("dropout_applied") is not False:
        status["errors"].append("NPZ dropout_applied must be false")
    if meta.get("attention_scale_verified") is not True:
        status["errors"].append("NPZ attention scale is not verified")
    if meta.get("score_bias_verified") is not True:
        status["errors"].append("NPZ score bias/mask is not verified")
    if meta.get("mask_challenge_exercised") is not True:
        status["errors"].append("NPZ did not exercise a causal/padding mask challenge row")
    if meta.get("attention_mask_backend_preserved") is not True:
        status["errors"].append("NPZ did not attest attention-mask backend preservation")
    if meta.get("custom_attention_backend_used") is True:
        status["errors"].append("NPZ used a custom attention backend without accepted mask-interface proof")
    if meta.get("capture_phase_contract") != PUBLIC_CAPTURE_PHASE_CONTRACT:
        status["errors"].append(f"NPZ capture_phase_contract must be {PUBLIC_CAPTURE_PHASE_CONTRACT!r}")
    if meta.get("prefill_phase_present") is not True:
        status["errors"].append("NPZ does not attest prefill phase coverage")
    if meta.get("decode_phase_present") is not True:
        status["errors"].append("NPZ does not attest cached-decode phase coverage")
    if meta.get("cache_decode_verified") is not True:
        status["errors"].append("NPZ cache_decode_verified must be true")
    if meta.get("valid_key_len_semantics_verified") is not True:
        status["errors"].append("NPZ valid_key_len padding/mask semantics are not verified")
    if meta.get("active_key_len_contract") != PUBLIC_ACTIVE_KEY_CONTRACT:
        status["errors"].append(f"NPZ active_key_len_contract must be {PUBLIC_ACTIVE_KEY_CONTRACT!r}")
    if meta.get("active_key_len_semantics_verified") is not True:
        status["errors"].append("NPZ active_key_len semantics are not verified")
    if meta.get("kv_group_map_contract") != PUBLIC_KV_GROUP_CONTRACT:
        status["errors"].append(f"NPZ kv_group_map_contract must be {PUBLIC_KV_GROUP_CONTRACT!r}")
    if meta.get("kv_group_map_verified") is not True:
        status["errors"].append("NPZ KV group map semantics are not verified")
    if meta.get("position_contract") != PUBLIC_POSITION_CONTRACT:
        status["errors"].append(f"NPZ position_contract must be {PUBLIC_POSITION_CONTRACT!r}")
    if meta.get("absolute_position_verified") is not True:
        status["errors"].append("NPZ absolute_position_verified must be true")
    if meta.get("rotary_position_contract") != PUBLIC_ROTARY_POSITION_CONTRACT:
        status["errors"].append(f"NPZ rotary_position_contract must be {PUBLIC_ROTARY_POSITION_CONTRACT!r}")
    if meta.get("rotary_position_ids_verified") is not True:
        status["errors"].append("NPZ rotary_position_ids_verified must be true")
    try:
        if int(meta.get("rotary_position_ids_present_call_count")) <= 0:
            status["errors"].append("NPZ rotary_position_ids_present_call_count must be positive")
    except Exception:
        status["errors"].append("NPZ rotary_position_ids_present_call_count is missing or non-integer")
    try:
        if int(meta.get("decode_steps_requested")) <= 0:
            status["errors"].append("NPZ decode_steps_requested must be positive")
    except Exception:
        status["errors"].append("NPZ decode_steps_requested is missing or non-integer")
    if meta.get("token_provenance_contract") != PUBLIC_TOKEN_PROVENANCE_CONTRACT:
        status["errors"].append(f"NPZ token_provenance_contract must be {PUBLIC_TOKEN_PROVENANCE_CONTRACT!r}")
    if meta.get("token_provenance_verified") is not True:
        status["errors"].append("NPZ token provenance is not verified")
    try:
        if int(meta.get("prompt_count")) <= 0 or int(meta.get("prompt_token_count_min")) <= 0 or int(meta.get("prompt_token_count_max")) < int(meta.get("prompt_token_count_min")):
            status["errors"].append("NPZ prompt_count and prompt_token_count min/max must be positive and ordered")
    except Exception:
        status["errors"].append("NPZ prompt_count/token_count metadata is missing or non-integer")
    if not _is_hex_sha256_text(meta.get("generation_config_sha256")):
        status["errors"].append("NPZ generation_config_sha256 must be SHA-256 hex")
    meta_generation_determinism = verify_generation_determinism_contract(
        generation_config_json=np.asarray([str(meta.get("generation_config_json", ""))]),
        generation_config_sha256=str(meta.get("generation_config_sha256", "")),
        generation_determinism_contract=str(meta.get("generation_determinism_contract", "")),
        generation_determinism_verified=meta.get("generation_determinism_verified"),
        generation_strategy=str(meta.get("generation_strategy", "")),
        generation_do_sample=meta.get("generation_do_sample"),
        generation_use_cache=meta.get("generation_use_cache"),
        generation_num_beams=meta.get("generation_num_beams"),
        generation_num_return_sequences=meta.get("generation_num_return_sequences"),
        generation_max_new_tokens=meta.get("generation_max_new_tokens"),
        generation_min_new_tokens=meta.get("generation_min_new_tokens"),
        generation_sampling_disabled=meta.get("generation_sampling_disabled"),
        generation_exact_new_tokens_required=meta.get("generation_exact_new_tokens_required"),
        decode_steps_requested=meta.get("decode_steps_requested"),
    )
    if not meta_generation_determinism.get("generation_determinism_verified"):
        status["errors"].append("NPZ generation determinism contract was not verified: " + "; ".join(meta_generation_determinism.get("errors", [])))
    if meta.get("generation_do_sample") is not False:
        status["errors"].append("NPZ generation_do_sample must be false")
    if meta.get("generation_use_cache") is not True:
        status["errors"].append("NPZ generation_use_cache must be true")
    try:
        if int(meta.get("generation_num_beams")) != 1 or int(meta.get("generation_num_return_sequences")) != 1:
            status["errors"].append("NPZ generation beam/return sequence metadata must both be 1")
        if int(meta.get("generation_max_new_tokens")) != int(meta.get("decode_steps_requested")):
            status["errors"].append("NPZ generation_max_new_tokens must equal decode_steps_requested")
        if int(meta.get("generation_min_new_tokens")) != int(meta.get("decode_steps_requested")):
            status["errors"].append("NPZ generation_min_new_tokens must equal decode_steps_requested")
    except Exception:
        status["errors"].append("NPZ generation beam/return/max-new-token metadata is missing or non-integer")
    if meta.get("generation_token_contract") != PUBLIC_GENERATION_TOKEN_CONTRACT:
        status["errors"].append(f"NPZ generation_token_contract must be {PUBLIC_GENERATION_TOKEN_CONTRACT!r}")
    if meta.get("generation_token_provenance_verified") is not True:
        status["errors"].append("NPZ generated-token provenance is not verified")
    if meta.get("generation_exact_new_tokens_required") is not True:
        status["errors"].append("NPZ generation_exact_new_tokens_required must be true")
    if meta.get("generated_new_token_exact_count_verified") is not True:
        status["errors"].append("NPZ generated_new_token_exact_count_verified must be true")
    try:
        if int(meta.get("generated_new_token_count_min")) <= 0 or int(meta.get("generated_new_token_count_max")) < int(meta.get("generated_new_token_count_min")):
            status["errors"].append("NPZ generated_new_token_count min/max must be positive and ordered")
        if int(meta.get("generated_new_token_count_min")) != int(meta.get("decode_steps_requested")) or int(meta.get("generated_new_token_count_max")) != int(meta.get("decode_steps_requested")):
            status["errors"].append("NPZ generated_new_token_count min/max must both equal decode_steps_requested")
    except Exception:
        status["errors"].append("NPZ generated_new_token_count metadata is missing or non-integer")
    meta_runtime_contract = verify_runtime_provenance_contract(meta)
    if not meta_runtime_contract.get("runtime_provenance_verified"):
        status["errors"].append("NPZ runtime device/dtype/timing provenance was not verified: " + "; ".join(meta_runtime_contract.get("errors", [])))
    status["runtime_provenance_status"] = meta_runtime_contract
    if meta.get("dense_reference_verified") is not True:
        status["errors"].append("NPZ dense reference parity is not verified")
    try:
        meta_dense_err = float(meta.get("dense_reference_max_abs_error"))
        if not math.isfinite(meta_dense_err) or meta_dense_err > PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            status["errors"].append("NPZ dense reference parity error exceeds tolerance")
    except Exception:
        status["errors"].append("NPZ dense reference parity error is missing or non-numeric")
    if not _is_immutable_revision(meta.get("model_revision")):
        status["errors"].append("NPZ model_revision is not immutable")
    if not _is_immutable_revision(meta.get("tokenizer_revision")):
        status["errors"].append("NPZ tokenizer_revision is not immutable")
    if meta.get("trust_remote_code") is True and not _is_immutable_revision(meta.get("code_revision")):
        status["errors"].append("NPZ code_revision is not immutable for trusted remote code")
    if meta.get("provenance_reviewed") is not True:
        status["errors"].append("NPZ provenance_reviewed must be true")
    if meta.get("generated_from_local_tiny_model") is not False:
        status["errors"].append("NPZ self-attestation marks local tiny/surrogate origin")
    if meta.get("uses_random_weights") is not False:
        status["errors"].append("NPZ self-attestation marks random weights")
    if npz_status.get("red_flag_terms"):
        status["errors"].append("NPZ metadata contains non-public red-flag terms: " + ", ".join(npz_status.get("red_flag_terms", [])))
    try:
        score_contract = verify_qkv_score_contract(trace_npz)
        status["score_contract_verification"] = score_contract
        computed_err = float(score_contract["computed_dense_reference_max_abs_error"])
        claimed_err = float(data.get("dense_reference_max_abs_error"))
        if computed_err > PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            status["errors"].append(f"recomputed dense-reference error {computed_err} exceeds {PUBLIC_DENSE_PARITY_MAX_ABS_ERROR}")
        if claimed_err + 1e-12 < computed_err:
            status["errors"].append("dense_reference_max_abs_error understates recomputed parity error")
        if score_contract.get("valid_key_len_present") is not True:
            status["errors"].append("valid_key_len array is required for public cached-decode trace claims")
        if int(score_contract.get("valid_key_len_padding_rows", 0)) <= 0:
            status["errors"].append("valid_key_len padding mask was not exercised across mixed prefill/decode lengths")
        if score_contract.get("active_key_len_present") is not True:
            status["errors"].append("active_key_len array is required for public cached-decode trace claims")
        if score_contract.get("active_key_len_contract") != PUBLIC_ACTIVE_KEY_CONTRACT or score_contract.get("active_key_len_contract_verified") is not True:
            status["errors"].append("mask-derived active_key_len contract was not verified")
        if int(score_contract.get("active_key_len_masked_rows", 0)) <= 0:
            status["errors"].append("active_key_len did not exercise a masked causal/static-cache row")
        if score_contract.get("kv_group_map_present") is not True:
            status["errors"].append("kv_head/num_attention_heads/num_key_value_heads/num_key_value_groups arrays are required for public trace claims")
        if score_contract.get("kv_group_map_contract") != PUBLIC_KV_GROUP_CONTRACT or score_contract.get("kv_group_map_verified") is not True:
            status["errors"].append("query-head to KV-head group map contract was not verified")
        if score_contract.get("position_contract") != PUBLIC_POSITION_CONTRACT or score_contract.get("position_contract_verified") is not True:
            status["errors"].append("absolute key-position contract was not verified for mixed prefill/decode rows")
        if score_contract.get("rotary_position_contract") != PUBLIC_ROTARY_POSITION_CONTRACT or score_contract.get("rotary_position_contract_verified") is not True:
            status["errors"].append("runtime RoPE position_id contract was not verified for mixed prefill/decode rows")
        if score_contract.get("token_provenance_contract") != PUBLIC_TOKEN_PROVENANCE_CONTRACT or score_contract.get("token_provenance_verified") is not True:
            status["errors"].append("prompt token provenance contract was not verified for mixed prefill/decode rows")
        if score_contract.get("generation_determinism_contract") != PUBLIC_GENERATION_DETERMINISM_CONTRACT or score_contract.get("generation_determinism_verified") is not True:
            status["errors"].append("greedy cached-decode generation determinism contract was not verified")
        if score_contract.get("generation_token_contract") != PUBLIC_GENERATION_TOKEN_CONTRACT or score_contract.get("generation_token_provenance_verified") is not True:
            status["errors"].append("generated-token provenance contract was not verified for cached-decode rows")
    except Exception as exc:
        status["errors"].append(f"qkv score-contract verification failed: {exc}")
    if status["errors"]:
        status["status"] = "public_pretrained_claim_rejected"
        return status
    status["accepted"] = True
    status["status"] = "public_pretrained_claim_accepted_with_manifest_and_npz_self_attestation"
    return status


def fmean(xs: Iterable[float]) -> float | None:
    xs = list(xs)
    return statistics.fmean(xs) if xs else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    xs = sorted(xs)
    if not xs:
        return None
    return float(xs[int(q * (len(xs) - 1))])


def unit(rng: np.random.Generator, d: int) -> np.ndarray:
    x = rng.normal(size=d)
    n = np.linalg.norm(x)
    return x / max(1e-12, n)


def make_values(rng: np.random.Generator, n: int, dv: int, regime: str, scores: np.ndarray) -> np.ndarray:
    values = rng.normal(0.0, 0.35, size=(n, dv)).astype(np.float64)
    # Give high-probability clusters coherent value directions so cosine/output
    # quality reflects whether the selector captures the semantic mass.
    probs = stable_softmax(scores)
    top = np.argsort(-probs)[: max(4, min(24, n // 4))]
    direction = unit(rng, dv)
    values[top] += direction * rng.uniform(0.7, 1.2)
    if regime == "value_tail_outlier":
        # Place several low-probability high-norm directions just below the
        # mass threshold.  They contribute too little probability to be needed
        # for a 0.95 score-mass certificate, but enough p_i ||V_i|| that omitting
        # them can move the dense output substantially.
        low = np.argsort(probs)[: max(4, n // 32)]
        max_score = float(np.max(scores))
        for j, idx in enumerate(low[:4]):
            values[idx] = unit(rng, dv) * (90.0 + 10.0 * j)
            scores[idx] = max_score - rng.uniform(4.45, 4.95)
    elif regime == "sink_plus_local":
        values[:4] += unit(rng, dv) * 1.4
    elif regime == "broad_high_entropy":
        values += rng.normal(0.0, 0.15, size=(n, dv))
    return values


def surrogate_scores(rng: np.random.Generator, regime: str, n: int, row: int) -> np.ndarray:
    pos = int(rng.integers(low=n // 4, high=n))
    scores = rng.normal(0.0, 0.35, size=n).astype(np.float64)
    idx = np.arange(n)
    if regime == "retrieval_peaked":
        center = int(rng.integers(0, n))
        scores += rng.normal(-1.5, 0.15, size=n)
        scores[center] += rng.uniform(6.0, 8.0)
        companions = rng.choice(n, size=3, replace=False)
        scores[companions] += rng.uniform(2.5, 3.5)
    elif regime == "local_window":
        dist = np.abs(idx - pos)
        scores += 4.5 * np.exp(-(dist ** 2) / (2 * rng.uniform(4.0, 9.0) ** 2)) - 1.5
    elif regime == "sink_plus_local":
        dist = np.abs(idx - pos)
        scores += 2.8 * np.exp(-(dist ** 2) / (2 * 8.0 ** 2)) - 1.2
        scores[:4] += rng.uniform(2.0, 3.2)
    elif regime == "multi_peak_induction":
        centers = rng.choice(n, size=5, replace=False)
        scores += rng.normal(-1.0, 0.2, size=n)
        for c in centers:
            scores[c] += rng.uniform(2.4, 4.0)
    elif regime == "broad_high_entropy":
        scores = rng.normal(0.0, 0.12, size=n).astype(np.float64)
    elif regime == "value_tail_outlier":
        scores = rng.normal(-8.0, 0.18, size=n).astype(np.float64)
        center = int(rng.integers(0, n))
        scores[center] = rng.uniform(0.0, 0.3)
        near = rng.choice([i for i in range(n) if i != center], size=8, replace=False)
        scores[near] = rng.normal(-2.0, 0.18, size=8)
    else:
        raise ValueError(f"unknown surrogate regime {regime!r}")
    return scores


def iter_surrogate_rows() -> Iterator[TraceRow]:
    rng = np.random.default_rng(SEED)
    regimes = [
        "retrieval_peaked",
        "local_window",
        "sink_plus_local",
        "multi_peak_induction",
        "broad_high_entropy",
        "value_tail_outlier",
    ]
    rid = 0
    for layer in range(2):
        for head in range(4):
            for regime in regimes:
                for local_id in range(ROWS_PER_REGIME // 8):
                    scores = surrogate_scores(rng, regime, N, rid)
                    values = make_values(rng, N, DV, regime, scores)
                    norms = np.linalg.norm(values, axis=-1)
                    yield TraceRow(
                        scores=scores,
                        values=values,
                        value_norms=norms,
                        d_head=D_HEAD,
                        trace_source_type="surrogate_public_like_offline",
                        trace_bundle_id="rev0049_deterministic_surrogate_trace_suite",
                        regime=regime,
                        layer=layer,
                        head=head,
                        position=int(rng.integers(low=N // 2, high=N)),
                        row_id=rid,
                    )
                    rid += 1


def _optional_label(arr, i: int, default):
    if arr is None:
        return default
    try:
        return arr[i].item() if hasattr(arr[i], "item") else arr[i]
    except Exception:
        return default


def iter_npz_rows(path: Path) -> Iterator[TraceRow]:
    validate_npz_resource_limits(path)
    with np.load(path, allow_pickle=False) as data:
        files = set(data.files)
        metadata_stage = _npz_scalar(data, "attention_score_input_stage")
        metadata_verified = _npz_scalar(data, "attention_score_inputs_verified") is True
        score_transform = str(_npz_scalar(data, "score_transform") or "scaled_dot_product_assumed")
        probability_contract = str(_npz_scalar(data, "probability_contract") or "")
        probability_semantics_verified = _npz_scalar(data, "probability_semantics_verified") is True
        attention_probability_dtype = str(_npz_scalar(data, "attention_probability_dtype") or "")
        attention_dropout_p_raw = _npz_scalar(data, "attention_dropout_p")
        try:
            attention_dropout_p = float(attention_dropout_p_raw) if attention_dropout_p_raw is not None else None
        except Exception:
            attention_dropout_p = None
        attention_training_state = _npz_scalar(data, "attention_training_state")
        dropout_applied = _npz_scalar(data, "dropout_applied")
        score_semantics_verified = bool(
            metadata_verified
            and _npz_scalar(data, "attention_scale_verified") is True
            and _npz_scalar(data, "score_bias_verified") is True
            and score_transform == PUBLIC_SCORE_TRANSFORM
            and probability_contract == PUBLIC_PROBABILITY_CONTRACT
            and probability_semantics_verified is True
            and attention_probability_dtype == PUBLIC_ATTENTION_PROBABILITY_DTYPE
            and attention_dropout_p is not None
            and abs(float(attention_dropout_p)) <= 1e-12
            and attention_training_state is False
            and dropout_applied is False
        )
        attention_scales = None
        score_biases = None
        if {"scores", "values"}.issubset(files):
            scores = np.asarray(data["scores"], dtype=np.float64)
            values = np.asarray(data["values"], dtype=np.float64)
            d_head_raw = _npz_scalar(data, "d_head")
            try:
                d_head = int(d_head_raw)
            except Exception as exc:
                raise ValueError("score/value schema requires positive integer d_head metadata for cost accounting") from exc
            if d_head <= 0 or d_head > MAX_HEAD_DIM:
                raise ValueError(f"score/value d_head out of range: {d_head}")
            attention_scales = np.full(scores.shape[0], np.nan, dtype=np.float64)
            score_biases = None
        elif {"q", "k", "v"}.issubset(files) or {"queries", "keys", "values"}.issubset(files):
            q_name, k_name, v_name = (("q", "k", "v") if {"q", "k", "v"}.issubset(files) else ("queries", "keys", "values"))
            q = np.asarray(data[q_name], dtype=np.float64)
            k = np.asarray(data[k_name], dtype=np.float64)
            values = np.asarray(data[v_name], dtype=np.float64)
            if q.ndim != 2 or k.ndim != 3 or values.ndim != 3:
                raise ValueError("q/k/v schema expects q [rows,d], k [rows,n,d], v [rows,n,dv]")
            if q.shape[0] != k.shape[0] or q.shape[0] != values.shape[0] or k.shape[1] != values.shape[1] or k.shape[2] != q.shape[1]:
                raise ValueError(f"q/k/v shape mismatch: q={q.shape} k={k.shape} v={values.shape}")
            if q.shape[0] <= 0 or k.shape[1] <= 0 or q.shape[1] <= 0 or values.shape[2] <= 0:
                raise ValueError(f"q/k/v arrays must have positive row/token/head dimensions: q={q.shape} k={k.shape} v={values.shape}")
            if q.shape[0] > MAX_TRACE_ROWS or k.shape[1] > MAX_TRACE_TOKENS or q.shape[1] > MAX_HEAD_DIM or values.shape[2] > MAX_VALUE_DIM:
                raise ValueError(f"q/k/v dimensions exceed ingress limits: q={q.shape} k={k.shape} v={values.shape}")
            if not (np.all(np.isfinite(q)) and np.all(np.isfinite(k)) and np.all(np.isfinite(values))):
                raise ValueError("trace q/k/v arrays must be finite")
            d_head = int(q.shape[-1])
            scale_raw = np.asarray(data["attention_scale"], dtype=np.float64).reshape(-1) if "attention_scale" in files else np.asarray([1.0 / math.sqrt(d_head)])
            if scale_raw.size == 1:
                attention_scales = np.repeat(scale_raw, q.shape[0])
            elif scale_raw.size == q.shape[0]:
                attention_scales = scale_raw
            else:
                raise ValueError(f"attention_scale must be scalar or [rows], got {scale_raw.shape}")
            if not np.all(np.isfinite(attention_scales)) or np.any(attention_scales <= 0):
                raise ValueError("attention_scale must be finite and positive")
            score_biases = np.asarray(data["score_bias"], dtype=np.float64) if "score_bias" in files else np.zeros((q.shape[0], k.shape[1]), dtype=np.float64)
            if score_biases.shape != (q.shape[0], k.shape[1]) or not np.all(np.isfinite(score_biases)):
                raise ValueError(f"score_bias must be finite [rows,n], got {score_biases.shape}")
            scores = np.einsum("rd,rnd->rn", q, k) * attention_scales[:, None] + score_biases
        else:
            raise ValueError("NPZ must contain scores+values, q+k+v, or queries+keys+values")
        if scores.ndim != 2 or values.ndim != 3 or scores.shape[0] != values.shape[0] or scores.shape[1] != values.shape[1]:
            raise ValueError("trace arrays must be scores [rows,n], values [rows,n,dv]")
        if scores.shape[0] <= 0 or scores.shape[1] <= 0 or values.shape[2] <= 0:
            raise ValueError("trace arrays must have positive row/token/value dimensions")
        if scores.shape[0] > MAX_TRACE_ROWS or scores.shape[1] > MAX_TRACE_TOKENS or values.shape[2] > MAX_VALUE_DIM:
            raise ValueError(f"trace dimensions exceed ingress limits: scores={scores.shape} values={values.shape}")
        if not (np.all(np.isfinite(scores)) and np.all(np.isfinite(values))):
            raise ValueError("trace scores and values must be finite")
        norms = np.asarray(data["value_norms"], dtype=np.float64) if "value_norms" in files else np.linalg.norm(values, axis=-1)
        if norms.shape != scores.shape or not np.all(np.isfinite(norms)):
            raise ValueError("value_norms must be finite and match scores [rows,n]")
        regimes = np.asarray(data["regime"]) if "regime" in files else None
        layers = np.asarray(data["layer"]) if "layer" in files else None
        heads = np.asarray(data["head"]) if "head" in files else None
        positions = np.asarray(data["position"]) if "position" in files else None
        capture_phases = np.asarray(data["capture_phase"]) if "capture_phase" in files else None
        rotary_position_ids = np.asarray(data["rotary_position_id"], dtype=np.int64).reshape(-1) if "rotary_position_id" in files else None
        valid_key_lens = np.asarray(data["valid_key_len"], dtype=np.int64).reshape(-1) if "valid_key_len" in files else None
        if valid_key_lens is not None and valid_key_lens.shape != (scores.shape[0],):
            raise ValueError(f"valid_key_len must be [rows], got {valid_key_lens.shape}")
        if rotary_position_ids is not None and rotary_position_ids.shape != (scores.shape[0],):
            raise ValueError(f"rotary_position_id must be [rows], got {rotary_position_ids.shape}")
        kv_heads = np.asarray(data["kv_head"], dtype=np.int64).reshape(-1) if "kv_head" in files else None
        num_attention_heads = np.asarray(data["num_attention_heads"], dtype=np.int64).reshape(-1) if "num_attention_heads" in files else None
        num_key_value_heads = np.asarray(data["num_key_value_heads"], dtype=np.int64).reshape(-1) if "num_key_value_heads" in files else None
        num_key_value_groups = np.asarray(data["num_key_value_groups"], dtype=np.int64).reshape(-1) if "num_key_value_groups" in files else None
        for label, arr in [
            ("kv_head", kv_heads),
            ("num_attention_heads", num_attention_heads),
            ("num_key_value_heads", num_key_value_heads),
            ("num_key_value_groups", num_key_value_groups),
        ]:
            if arr is not None and arr.shape not in {(scores.shape[0],), (1,)}:
                raise ValueError(f"{label} must be scalar or [rows], got {arr.shape}")
    for i in range(scores.shape[0]):
        yield TraceRow(
            scores=scores[i],
            values=values[i],
            value_norms=norms[i],
            d_head=d_head,
            trace_source_type="external_npz_trace_bundle",
            trace_bundle_id=path.name,
            regime=str(_optional_label(regimes, i, "external_unspecified")),
            layer=int(_optional_label(layers, i, 0)),
            head=int(_optional_label(heads, i, 0)),
            position=int(_optional_label(positions, i, scores.shape[1] - 1)),
            row_id=i,
            imported_from=path.as_posix(),
            attention_score_input_stage=str(metadata_stage) if metadata_stage is not None else None,
            attention_score_inputs_verified=bool(metadata_verified),
            attention_scale=(float(attention_scales[i]) if attention_scales is not None and np.isfinite(attention_scales[i]) else None),
            score_bias=(score_biases[i] if score_biases is not None else None),
            score_transform=score_transform,
            probability_contract=probability_contract,
            probability_semantics_verified=bool(probability_semantics_verified),
            attention_probability_dtype=attention_probability_dtype,
            attention_dropout_p=attention_dropout_p,
            score_semantics_verified=bool(score_semantics_verified),
            capture_phase=str(_optional_label(capture_phases, i, None)) if capture_phases is not None else None,
            valid_key_len=int(_optional_label(valid_key_lens, i, len(scores[i]))) if valid_key_lens is not None else None,
            rotary_position_id=int(_optional_label(rotary_position_ids, i, 0)) if rotary_position_ids is not None else None,
            kv_head=int(_optional_label(kv_heads, i, 0)) if kv_heads is not None else None,
            num_attention_heads=int(_optional_label(num_attention_heads, i, 0)) if num_attention_heads is not None else None,
            num_key_value_heads=int(_optional_label(num_key_value_heads, i, 0)) if num_key_value_heads is not None else None,
            num_key_value_groups=int(_optional_label(num_key_value_groups, i, 0)) if num_key_value_groups is not None else None,
        )


def evaluate_trace_row(row: TraceRow, public_pretrained_trace_loaded: bool = False) -> list[dict]:
    points = guarded_mass_aware_compiler_points_for_row(
        row.scores,
        row.values,
        row.value_norms,
        d_head=row.d_head,
        fixed_k=min(FIXED_K, len(row.scores)),
        target_mass=TARGET_MASS,
        block=min(BLOCK, len(row.scores)),
        hist_bins=HIST_BINS,
        hist_max_delta=16.0,
        value_error_bound=VALUE_ERROR_BOUND,
        include_ordered_topp=True,
    )
    probs = stable_softmax(row.scores)
    enriched: list[dict] = []
    for p in points:
        p.update({
            "row_kind": "public_trace_gate_attention_row",
            "trace_source_type": row.trace_source_type,
            "trace_bundle_id": row.trace_bundle_id,
            "regime": row.regime,
            "layer": int(row.layer),
            "head": int(row.head),
            "position": int(row.position),
            "row_id": int(row.row_id),
            "imported_from": row.imported_from,
            "N": int(len(row.scores)),
            "DV": int(row.values.shape[-1]),
            "D": int(row.d_head),
            "attention_score_input_stage": row.attention_score_input_stage,
            "attention_score_inputs_verified": bool(row.attention_score_inputs_verified),
            "attention_scale": row.attention_scale,
            "score_transform": row.score_transform,
            "score_semantics_verified": bool(row.score_semantics_verified),
            "capture_phase": row.capture_phase,
            "valid_key_len": row.valid_key_len,
            "rotary_position_id": row.rotary_position_id,
            "kv_head": row.kv_head,
            "num_attention_heads": row.num_attention_heads,
            "num_key_value_heads": row.num_key_value_heads,
            "num_key_value_groups": row.num_key_value_groups,
            "K": int(min(FIXED_K, len(row.scores))),
            "target_mass_policy": TARGET_MASS,
            "max_probability": float(np.max(probs)),
            "entropy_effective_support": float(math.exp(-np.sum(probs * np.log(np.maximum(probs, 1e-30))))),
            "external_trace_loaded": bool(row.trace_source_type == "external_npz_trace_bundle"),
            "public_pretrained_trace_loaded": bool(public_pretrained_trace_loaded),
            "is_surrogate_trace": bool(row.trace_source_type == "surrogate_public_like_offline"),
            "selection_oracle_leakage_detected": bool(p.get("selection_uses_values") or p.get("selection_uses_dense_output")),
        })
        enriched.append(p)
    return enriched


def summarize(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for regime in sorted({r["regime"] for r in rows}):
        rr = [r for r in rows if r["regime"] == regime]
        by_method = {}
        for method in sorted({r["method"] for r in rr}):
            xs = [r for r in rr if r["method"] == method]
            by_method[method] = {
                "row_count": len(xs),
                "mean_selected_count": fmean(float(r["selected_count"]) for r in xs),
                "p90_selected_count": pctl((float(r["selected_count"]) for r in xs), 0.90),
                "mean_value_read_fraction": fmean(float(r["value_read_fraction"]) for r in xs),
                "mean_mass_retained": fmean(float(r["mass_retained"]) for r in xs),
                "mean_attention_rel_l2_error": fmean(float(r["attention_rel_l2_error"]) for r in xs),
                "mean_output_cosine": fmean(float(r["output_cosine"]) for r in xs),
                "quality_bar_rate": fmean(float(r["passes_quality_bar"]) for r in xs),
                "mean_effective_support": fmean(float(r["effective_support"]) for r in xs),
                "oracle_leakage_rows": sum(1 for r in xs if r.get("selection_oracle_leakage_detected")),
                "value_norm_metadata_rate": fmean(float(r.get("selection_uses_value_norms", False)) for r in xs),
                "fallback_rate": fmean(float(r.get("fallback") is not None) for r in xs),
            }
        out[regime] = {"row_count": len(rr), "compiler_summary": by_method}
    return out


def method(summary: dict, regime: str, name: str) -> dict:
    return summary.get(regime, {}).get("compiler_summary", {}).get(name, {})


def run(
    trace_npz: Path | None = None,
    *,
    public_pretrained_trace: bool = False,
    trace_source_label: str | None = None,
    bundle_model_id: str | None = None,
    bundle_license: str | None = None,
    provenance_json: Path | None = None,
) -> dict:
    trace_rows = list(iter_npz_rows(trace_npz)) if trace_npz else list(iter_surrogate_rows())
    external_loaded = trace_npz is not None
    if not external_loaded:
        provenance_status = {"accepted": False, "status": "surrogate_default_no_external_trace", "errors": [], "warnings": []}
    elif public_pretrained_trace:
        provenance_status = validate_public_trace_provenance(provenance_json, trace_npz)
    else:
        provenance_status = {
            "accepted": False,
            "status": "external_nonpublic_trace_provenance_not_evaluated",
            "errors": [],
            "warnings": [],
            "npz_metadata_status": inspect_trace_npz_metadata(trace_npz),
        }
    public_loaded = bool(external_loaded and public_pretrained_trace and provenance_status.get("accepted"))
    rows: list[dict] = []
    for tr in trace_rows:
        rows.extend(evaluate_trace_row(tr, public_pretrained_trace_loaded=public_loaded))
    ds = summarize(rows)
    mass_name = f"mass_histogram_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}"
    exc_name = f"value_norm_exception_mass_{str(TARGET_MASS).replace('.', 'p')}_bins{HIST_BINS}"
    topk_name = f"exact_topk_{FIXED_K}"
    risk_surface = {
        "retrieval_topk_quality_rate": method(ds, "retrieval_peaked", topk_name).get("quality_bar_rate"),
        "retrieval_mass_hist_selected_fraction": method(ds, "retrieval_peaked", mass_name).get("mean_value_read_fraction"),
        "broad_mass_hist_selected_fraction": method(ds, "broad_high_entropy", mass_name).get("mean_value_read_fraction"),
        "broad_mass_hist_quality_rate": method(ds, "broad_high_entropy", mass_name).get("quality_bar_rate"),
        "tail_mass_hist_quality_rate": method(ds, "value_tail_outlier", mass_name).get("quality_bar_rate"),
        "tail_value_norm_exception_quality_rate": method(ds, "value_tail_outlier", exc_name).get("quality_bar_rate"),
        "tail_value_norm_exception_selected_fraction": method(ds, "value_tail_outlier", exc_name).get("mean_value_read_fraction"),
    }
    source_path = Path(__file__).resolve()
    core_path = ROOT / "experiments" / "attention_compiler_core" / "attention_core.py"
    out = {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "public_trace_gate_surrogate",
        "kind": "offline_attention_trace_importer_and_surrogate_suite",
        "generated_at": STAMP,
        "promotion_allowed": False,
        "trace_gate_status": (
            "surrogate_only_importer_ready_public_pretrained_missing"
            if not external_loaded else
            ("external_public_pretrained_npz_loaded_provenance_manifest_accepted" if public_loaded else ("external_npz_loaded_public_claim_rejected_provenance" if public_pretrained_trace else "external_npz_loaded_claims_public_pretrained_false"))
        ),
        "external_trace_loaded": bool(external_loaded),
        "public_pretrained_trace_loaded": bool(public_loaded),
        "is_surrogate_only_default": bool(not external_loaded),
        "external_trace_declaration": {
            "trace_source_label": trace_source_label,
            "bundle_model_id": bundle_model_id,
            "bundle_license": bundle_license,
            "provenance_json": provenance_json.as_posix() if provenance_json else None,
            "provenance_status": provenance_status,
            "declared_public_pretrained_trace": bool(public_pretrained_trace),
            "accepted_as_public_pretrained_trace": bool(public_loaded),
            "note": "External NPZ import proves only schema/evaluator compatibility unless the manifest and embedded metadata also establish immutable model provenance, post-transform Q/K capture, explicit scale/bias/mask score semantics, float32 softmax/no-dropout probability semantics, runtime RoPE position_ids, an exercised mask challenge, and recomputed dense-reference parity. rev0076 rejects raw projection captures, mutable revisions, unverifiable score rules, and wrong head-dimension accounting."
        },
        "external_trace_schema": {
            "npz_scores_values": {"scores": "float[rows,n]", "values": "float[rows,n,dv]", "d_head_required": "positive integer scalar", "value_norms_optional": "float[rows,n]"},
            "npz_qkv_v2_public": {"q_or_queries": "float[rows,d]", "k_or_keys": "float[rows,n,d]", "v_or_values": "float[rows,n,dv]", "attention_scale": "positive float scalar or [rows]", "score_bias": "finite float[rows,n], including mask/bias and padded-tail sentinel", "valid_key_len": "int[rows] live KV length before fixed-context padding", "capture_phase": "prefill or decode_cached per row", "position": "absolute active-key position per row", "rotary_position_id": "runtime RoPE position_id per row", "active_key_len": "int[rows] mask-derived count of scored KV keys", "active_key_len_contract": PUBLIC_ACTIVE_KEY_CONTRACT, "kv_head": "int[rows] compact KV-head owner for each query-head row", "num_attention_heads": "int scalar or [rows] query head count", "num_key_value_heads": "int scalar or [rows] compact KV-head count", "num_key_value_groups": "int scalar or [rows] query heads per KV head", "kv_group_map_contract": PUBLIC_KV_GROUP_CONTRACT, "position_contract": PUBLIC_POSITION_CONTRACT, "rotary_position_contract": PUBLIC_ROTARY_POSITION_CONTRACT, "capture_phase_contract": PUBLIC_CAPTURE_PHASE_CONTRACT, "mask_challenge_exercised": "true for public claims", "attention_mask_backend_preserved": "true for public claims", "score_transform": PUBLIC_SCORE_TRANSFORM, "probability_contract": PUBLIC_PROBABILITY_CONTRACT, "attention_probability_dtype": PUBLIC_ATTENTION_PROBABILITY_DTYPE, "attention_dropout_p": "0.0", "probability_semantics_verified": "true for public claims", "dense_reference_output": "float[rows,dv] from model/runtime", "cost_d_head": "derived from q.shape[-1]"},
            "npz_qkv_v1_diagnostic": "older qkv bundles load with assumed 1/sqrt(d) scale and zero bias but cannot be accepted as public evidence",
            "optional_labels": ["regime", "layer", "head", "position"],
        },
        "selection_contract": "selectors may use QK scores; value-norm guarded selectors may use value-norm metadata; selectors may not inspect V vectors or dense outputs before returning indices",
        "summary": {
            "primary_metric": {"name": "quality_bar_rate_with_value_read_fraction_by_trace_regime", "direction": "higher_quality_lower_reads"},
            "guard_fields": [
                "trace_source_type", "regime", "method", "selected_count", "value_reads", "value_read_fraction",
                "mass_retained", "certified_mass_from_scores", "certificate_error_abs", "attention_rel_l2_error",
                "attention_l2_error", "output_cosine", "qk_dot_products", "score_reads", "score_read_fraction",
                "selector_passes", "threshold_evals", "bytes_touched_est", "selection_uses_values",
                "selection_uses_dense_output", "selection_uses_value_norms", "mass_certificate",
                "mass_certified_without_value_vectors", "selection_oracle_leakage_detected", "passes_quality_bar",
                "external_trace_loaded", "public_pretrained_trace_loaded", "is_surrogate_trace", "effective_support", "entropy_effective_support",
                "D", "attention_score_input_stage", "attention_score_inputs_verified", "attention_scale", "score_transform", "probability_contract", "attention_probability_dtype", "attention_dropout_p", "score_semantics_verified", "capture_phase", "valid_key_len", "position_contract", "absolute_position_verified", "rotary_position_id", "rotary_position_contract", "rotary_position_ids_verified",
            ],
            "trace_row_count": len(trace_rows),
            "result_row_count": len(rows),
            "target_mass": TARGET_MASS,
            "fixed_k": FIXED_K,
            "hist_bins": HIST_BINS,
            "dataset_summary": ds,
            "risk_surface": risk_surface,
            "oracle_leakage_rows": sum(1 for r in rows if r.get("selection_oracle_leakage_detected")),
            "surrogate_regimes": sorted({r["regime"] for r in rows}),
            "trace_source_types": sorted({r["trace_source_type"] for r in rows}),
        },
        "rows": rows,
        "run_provenance": {
            "source_path": source_path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256_file(source_path),
            "core_source_path": core_path.relative_to(ROOT).as_posix(),
            "core_source_sha256": sha256_file(core_path),
            "command": "python experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
            "trace_npz": trace_npz.as_posix() if trace_npz else None,
            "public_pretrained_trace_arg": bool(public_pretrained_trace),
            "trace_source_label": trace_source_label,
            "bundle_model_id": bundle_model_id,
            "bundle_license": bundle_license,
            "provenance_json": provenance_json.as_posix() if provenance_json else None,
            "provenance_status": provenance_status,
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "seed": SEED,
        },
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace-npz", type=Path, default=None, help="optional external NPZ trace bundle")
    ap.add_argument("--public-pretrained-trace", action="store_true", help="declare the external NPZ as real public/pretrained model traces; default false")
    ap.add_argument("--trace-source-label", default=None, help="human label for the trace source, e.g. fixture, local-hf-gpt2")
    ap.add_argument("--bundle-model-id", default=None, help="model identifier if this NPZ came from a model capture")
    ap.add_argument("--bundle-license", default=None, help="license/source note for the trace bundle")
    ap.add_argument("--provenance-json", type=Path, default=None, help="required manifest for accepting an external trace as public/pretrained")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_GATE_SURROGATE.json")
    args = ap.parse_args()
    payload = run(
        args.trace_npz,
        public_pretrained_trace=args.public_pretrained_trace,
        trace_source_label=args.trace_source_label,
        bundle_model_id=args.bundle_model_id,
        bundle_license=args.bundle_license,
        provenance_json=args.provenance_json,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_PUBLIC_TRACE_GATE_SURROGATE_RUN_MANIFEST.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload["run_provenance"], indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["trace_gate_status"],
        "trace_rows": payload["summary"]["trace_row_count"],
        "result_rows": payload["summary"]["result_row_count"],
        "oracle_leakage_rows": payload["summary"]["oracle_leakage_rows"],
        "risk_surface": payload["summary"]["risk_surface"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
