#!/usr/bin/env python3
"""Adversarial public-trace acceptance preflight for rev0076.

This is a guardrail test, not public-model evidence. It challenges four distinct
boundaries that were previously conflated:

* tensor meaning: Q/K must be the post-model-transform score inputs;
* score meaning: scale, mask/bias, and transform must be explicit;
* replay truth: dense reference parity is recomputed, not self-attested;
* cost truth: the imported trace's actual head dimension reaches accounting.

Every generated bundle is marked as a preflight fixture and must remain
non-promotional even when other fields resemble a public trace.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0076")
REVUP = REV.upper()
STAMP = META.get("generated_at") or META.get("created_at") or "unknown"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
MAN = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_RUN_MANIFEST.json"
FIX_DIR = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PREFLIGHT_FIXTURES"
GATE_SCRIPT = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
CAPTURE_HELPER = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
THIS = Path(__file__).resolve()
MODEL_COMMIT = "a" * 40
TOKENIZER_COMMIT = "b" * 40
CODE_COMMIT = "c" * 40
CONFIG_SHA256 = "d" * 64
TRACE_CLAIM_VERSION = "public_trace_claim_v3"
QKV_SCHEMA = "qkv_npz_v2"
SCORE_TRANSFORM = "scaled_dot_product_plus_bias"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_gate_module():
    spec = importlib.util.spec_from_file_location(f"public_trace_gate_surrogate_{REV}", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import public trace gate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def source_fixture() -> Path:
    candidates = [
        ROOT / "artifacts" / "trace-bundles" / "REV0073_SELF_DECLARED_LOCAL_FIXTURE_QKV.npz",
        ROOT / "artifacts" / "trace-bundles" / "REV0072_TRACE_CLAIM_FIXTURE_QKV.npz",
        ROOT / "artifacts" / "trace-bundles" / "REV0062_TINY_TRAINED_QK_TRACE_PACKET.npz",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("no local Q/K/V fixture available for preflight")


def read_qkv(path: Path, limit: int = 12) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    with np.load(path, allow_pickle=False) as z:
        files = set(z.files)
        if {"q", "k", "v"}.issubset(files):
            q, k, v = (np.asarray(z[name], dtype=np.float64) for name in ("q", "k", "v"))
        elif {"queries", "keys", "values"}.issubset(files):
            q, k, v = (np.asarray(z[name], dtype=np.float64) for name in ("queries", "keys", "values"))
        else:
            raise ValueError("source fixture lacks q/k/v or queries/keys/values")
        limit = min(limit, q.shape[0])
        labels: dict[str, np.ndarray] = {}
        for name in ["regime", "layer", "head", "position", "example", "trace_batch"]:
            if name in files:
                labels[name] = np.asarray(z[name])[:limit]
    return q[:limit], k[:limit], v[:limit], labels


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def dense_reference(q: np.ndarray, k: np.ndarray, v: np.ndarray, scale: np.ndarray, bias: np.ndarray) -> np.ndarray:
    scales = np.asarray(scale, dtype=np.float64).reshape(-1)
    if scales.size == 1:
        scales = np.repeat(scales, q.shape[0])
    scores = np.einsum("rd,rnd->rn", q, k) * scales[:, None] + bias
    scores = scores - np.max(scores, axis=1, keepdims=True)
    probs = np.exp(scores)
    probs /= np.sum(probs, axis=1, keepdims=True)
    return np.einsum("rn,rnd->rd", probs, v)


def base_metadata(
    *,
    public: bool,
    source_type: str,
    model_id: str,
    model_revision: str = MODEL_COMMIT,
    tokenizer_revision: str = TOKENIZER_COMMIT,
    code_revision: str = "not_applicable",
    trust_remote_code: bool = False,
    generated_tiny: bool,
    random_weights: bool = False,
    reviewed: bool = True,
    stage: str,
    score_inputs_verified: bool,
    scale_verified: bool,
    bias_verified: bool,
    dense_verified: bool,
    dense_error: float,
    score_transform: str = SCORE_TRANSFORM,
    capture_tool: str | None = None,
    capture_tool_sha: str | None = None,
) -> dict[str, np.ndarray]:
    tool = capture_tool or "experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py"
    tool_sha = capture_tool_sha or sha256_file(THIS)
    return {
        "trace_claim_version": scalar(TRACE_CLAIM_VERSION),
        "public_pretrained_trace": scalar(bool(public)),
        "source_type": scalar(source_type),
        "model_id": scalar(model_id),
        "model_revision": scalar(model_revision),
        "tokenizer_revision": scalar(tokenizer_revision),
        "code_revision": scalar(code_revision),
        "trust_remote_code": scalar(bool(trust_remote_code)),
        "weights_source": scalar("declared checkpoint/source for preflight contract control"),
        "license": scalar("declared source terms for preflight contract control"),
        "schema": scalar(QKV_SCHEMA),
        "capture_tool": scalar(tool),
        "capture_tool_sha256": scalar(tool_sha),
        "config_sha256": scalar(CONFIG_SHA256),
        "generated_from_local_tiny_model": scalar(bool(generated_tiny)),
        "uses_random_weights": scalar(bool(random_weights)),
        "provenance_reviewed": scalar(bool(reviewed)),
        "attention_backend": scalar("eager"),
        "attention_score_input_stage": scalar(stage),
        "attention_score_inputs_verified": scalar(bool(score_inputs_verified)),
        "score_transform": scalar(score_transform),
        "attention_scale_verified": scalar(bool(scale_verified)),
        "score_bias_verified": scalar(bool(bias_verified)),
        "dense_reference_verified": scalar(bool(dense_verified)),
        "dense_reference_max_abs_error": scalar(float(dense_error)),
        "preflight_fixture": scalar(True),
    }


def write_qkv_npz(
    path: Path,
    q: np.ndarray,
    k: np.ndarray,
    v: np.ndarray,
    labels: dict[str, np.ndarray],
    *,
    aliases: bool = False,
    public: bool = False,
    source_type: str = "local_preflight_control",
    model_id: str = "preflight_control_not_public",
    model_revision: str = MODEL_COMMIT,
    tokenizer_revision: str = TOKENIZER_COMMIT,
    code_revision: str = "not_applicable",
    trust_remote_code: bool = False,
    generated_tiny: bool = True,
    random_weights: bool = False,
    reviewed: bool = True,
    stage: str = "post_model_qk_transforms",
    score_inputs_verified: bool = True,
    scale_verified: bool = True,
    bias_verified: bool = True,
    dense_verified: bool = True,
    score_transform: str = SCORE_TRANSFORM,
    include_reference: bool = True,
    reference_offset: float = 0.0,
    use_capture_helper_identity: bool = True,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows, tokens = q.shape[0], k.shape[1]
    scale = np.asarray([1.0 / math.sqrt(q.shape[-1])], dtype=np.float64)
    # Exercise nonzero bias semantics without masking every token.
    bias = np.linspace(-0.125, 0.125, tokens, dtype=np.float64)[None, :]
    bias = np.repeat(bias, rows, axis=0)
    shape_compatible = (
        q.ndim == 2 and k.ndim == 3 and v.ndim == 3
        and q.shape[0] == k.shape[0] == v.shape[0]
        and k.shape[1] == v.shape[1] and k.shape[2] == q.shape[1]
    )
    reference = dense_reference(q, k, v, scale, bias) if shape_compatible else np.zeros((rows, v.shape[-1]), dtype=np.float64)
    if reference_offset:
        reference = reference.copy()
        reference[0, 0] += reference_offset
    dense_error = 0.0 if reference_offset == 0.0 else 0.0  # deliberately forged claim for the offset case
    payload: dict[str, Any] = dict(labels)
    payload.update({"queries": q, "keys": k, "values": v} if aliases else {"q": q, "k": k, "v": v})
    payload.update({
        "d_head": scalar(int(q.shape[-1])),
        "attention_scale": scale,
        "score_bias": bias,
    })
    if include_reference:
        payload["dense_reference_output"] = reference
    payload.update(base_metadata(
        public=public,
        source_type=source_type,
        model_id=model_id,
        model_revision=model_revision,
        tokenizer_revision=tokenizer_revision,
        code_revision=code_revision,
        trust_remote_code=trust_remote_code,
        generated_tiny=generated_tiny,
        random_weights=random_weights,
        reviewed=reviewed,
        stage=stage,
        score_inputs_verified=score_inputs_verified,
        scale_verified=scale_verified,
        bias_verified=bias_verified,
        dense_verified=dense_verified,
        dense_error=dense_error,
        score_transform=score_transform,
        capture_tool="experiments/public_trace_capture/hf_attention_trace_capture.py" if use_capture_helper_identity else None,
        capture_tool_sha=sha256_file(CAPTURE_HELPER) if use_capture_helper_identity else None,
    ))
    np.savez_compressed(path, **payload)
    return path


def write_scores_values_npz(path: Path, q: np.ndarray, k: np.ndarray, v: np.ndarray, labels: dict[str, np.ndarray], *, include_d_head: bool) -> Path:
    scores = np.einsum("rd,rnd->rn", q, k) / math.sqrt(q.shape[-1])
    payload: dict[str, Any] = dict(labels)
    payload.update({
        "scores": scores,
        "values": v,
        "value_norms": np.linalg.norm(v, axis=-1),
        "trace_claim_version": scalar(TRACE_CLAIM_VERSION),
        "public_pretrained_trace": scalar(False),
        "source_type": scalar("score_only_preflight_control"),
        "model_id": scalar("score_only_control_not_public"),
        "schema": scalar("scores_values_npz_v1"),
        "preflight_fixture": scalar(True),
    })
    if include_d_head:
        payload["d_head"] = scalar(int(q.shape[-1]))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **payload)
    return path


def npz_scalar(z, key: str) -> Any:
    arr = np.asarray(z[key])
    value = arr.reshape(-1)[0]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    return value


def manifest_from_npz(path: Path, trace_npz: Path, *, expected_sha: str | None = None, overrides: dict[str, Any] | None = None) -> Path:
    fields = [
        "trace_claim_version", "public_pretrained_trace", "source_type", "model_id", "model_revision",
        "tokenizer_revision", "code_revision", "trust_remote_code", "weights_source", "license", "schema",
        "capture_tool", "capture_tool_sha256", "config_sha256", "generated_from_local_tiny_model",
        "uses_random_weights", "provenance_reviewed", "attention_backend", "attention_score_input_stage",
        "attention_score_inputs_verified", "score_transform", "attention_scale_verified", "score_bias_verified",
        "dense_reference_verified", "dense_reference_max_abs_error",
    ]
    with np.load(trace_npz, allow_pickle=False) as z:
        data = {key: npz_scalar(z, key) for key in fields if key in z.files}
    data["trace_npz_sha256"] = expected_sha if expected_sha is not None else sha256_file(trace_npz)
    data["preflight_manifest_control"] = True
    if overrides:
        data.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def native_qkv_compatible(path: Path) -> dict[str, Any]:
    try:
        with np.load(path, allow_pickle=False) as z:
            files = set(z.files)
            if not ({"q", "k", "v"}.issubset(files) or {"queries", "keys", "values"}.issubset(files)):
                return {"compatible": False, "reason": "not_qkv_schema"}
            q = np.asarray(z["q"] if "q" in files else z["queries"], dtype=np.float64)
            k = np.asarray(z["k"] if "k" in files else z["keys"], dtype=np.float64)
            v = np.asarray(z["v"] if "v" in files else z["values"], dtype=np.float64)
        ok = (
            q.ndim == 2 and k.ndim == 3 and v.ndim == 3
            and q.shape[0] == k.shape[0] == v.shape[0]
            and k.shape[1] == v.shape[1] and k.shape[2] == q.shape[1]
            and q.shape[0] > 0 and k.shape[1] > 0 and v.shape[2] > 0
            and np.all(np.isfinite(q)) and np.all(np.isfinite(k)) and np.all(np.isfinite(v))
        )
        return {
            "compatible": bool(ok),
            "rows": int(q.shape[0]) if q.ndim >= 1 else None,
            "shape": {"q": list(q.shape), "k": list(k.shape), "v": list(v.shape)},
            "d_head": int(q.shape[-1]) if q.ndim == 2 else None,
            "reason": None if ok else "bad_qkv_shape_or_nonfinite",
        }
    except Exception as exc:
        return {"compatible": False, "reason": repr(exc)}


def compact_gate(payload: dict[str, Any] | None, error: str | None = None) -> dict[str, Any]:
    if payload is None:
        return {
            "gate_exception": error,
            "external_trace_loaded": False,
            "public_pretrained_trace_loaded": False,
            "accepted_as_public_pretrained_trace": False,
            "evaluated_d_heads": [],
        }
    decl = payload.get("external_trace_declaration", {})
    provenance = decl.get("provenance_status", {})
    npz_status = provenance.get("npz_metadata_status", {})
    summary = payload.get("summary", {})
    return {
        "trace_gate_status": payload.get("trace_gate_status"),
        "external_trace_loaded": payload.get("external_trace_loaded"),
        "declared_public_pretrained_trace": decl.get("declared_public_pretrained_trace"),
        "public_pretrained_trace_loaded": payload.get("public_pretrained_trace_loaded"),
        "accepted_as_public_pretrained_trace": decl.get("accepted_as_public_pretrained_trace"),
        "provenance_status": provenance.get("status"),
        "provenance_error_count": len(provenance.get("errors", []) or []),
        "provenance_errors": provenance.get("errors", [])[:40],
        "npz_metadata_status": npz_status.get("status"),
        "npz_red_flag_terms": npz_status.get("red_flag_terms", []),
        "score_contract_verification": provenance.get("score_contract_verification"),
        "trace_row_count": summary.get("trace_row_count"),
        "result_row_count": summary.get("result_row_count"),
        "oracle_leakage_rows": summary.get("oracle_leakage_rows"),
        "evaluated_d_heads": sorted({int(row["D"]) for row in payload.get("rows", []) if "D" in row}),
        "attention_score_input_stages": sorted({str(row.get("attention_score_input_stage")) for row in payload.get("rows", [])}),
    }


def direct_score_contract(gate, path: Path) -> dict[str, Any]:
    try:
        result = gate.verify_qkv_score_contract(path)
        return {
            "computed": True,
            "within_public_tolerance": float(result["computed_dense_reference_max_abs_error"]) <= float(gate.PUBLIC_DENSE_PARITY_MAX_ABS_ERROR),
            **result,
        }
    except Exception as exc:
        return {"computed": False, "within_public_tolerance": False, "error": str(exc)}


def run_case(gate, *, name: str, trace_npz: Path, claim_public: bool, provenance_json: Path | None, expected: dict[str, Any], error_contains: str | None = None) -> dict[str, Any]:
    gate_payload = None
    error = None
    try:
        gate_payload = gate.run(
            trace_npz,
            public_pretrained_trace=claim_public,
            trace_source_label=f"{REV}_preflight_{name}",
            bundle_model_id=None,
            bundle_license=None,
            provenance_json=provenance_json,
        )
    except Exception as exc:
        error = repr(exc)
    gate_summary = compact_gate(gate_payload, error)
    native = native_qkv_compatible(trace_npz)
    contract = direct_score_contract(gate, trace_npz) if native.get("compatible") else {"computed": False, "within_public_tolerance": False, "error": "not_valid_qkv"}
    passed = True
    failures: list[str] = []
    for key, expected_value in expected.items():
        actual = gate_summary.get(key) if key in gate_summary else native.get(key)
        if actual != expected_value:
            passed = False
            failures.append(f"{key}: expected {expected_value!r}, got {actual!r}")
    if error_contains is not None:
        haystack = " ".join([str(gate_summary.get("gate_exception") or "")] + [str(x) for x in gate_summary.get("provenance_errors", [])] + [str(contract.get("error") or "")])
        if error_contains not in haystack:
            passed = False
            failures.append(f"expected error substring {error_contains!r}, got {haystack!r}")
    return {
        "case": name,
        "trace_npz": trace_npz.relative_to(ROOT).as_posix(),
        "trace_sha256": sha256_file(trace_npz),
        "claim_public": claim_public,
        "provenance_json": provenance_json.relative_to(ROOT).as_posix() if provenance_json else None,
        "gate": gate_summary,
        "direct_score_contract": contract,
        "native_qkv_compatibility": native,
        "expected": expected,
        "expected_error_contains": error_contains,
        "passed": passed,
        "failures": failures,
    }


def main() -> int:
    gate = load_gate_module()
    source = source_fixture()
    q, k, v, labels = read_qkv(source, limit=12)
    FIX_DIR.mkdir(parents=True, exist_ok=True)
    expected_d = int(q.shape[-1])

    good = write_qkv_npz(FIX_DIR / f"{REVUP}_GOOD_NONPUBLIC_QKV_V2.npz", q, k, v, labels)
    aliases = write_qkv_npz(FIX_DIR / f"{REVUP}_GOOD_NONPUBLIC_QUERY_KEY_VALUE_ALIASES_V2.npz", q, k, v, labels, aliases=True)
    publicish = write_qkv_npz(
        FIX_DIR / f"{REVUP}_PUBLICISH_PREFLIGHT_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
    )
    redflag = write_qkv_npz(
        FIX_DIR / f"{REVUP}_PUBLIC_CLAIM_REDFLAG_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="local_tiny_public_claim_control", model_id="local_tiny_control_not_public", generated_tiny=True,
    )
    raw_projection = write_qkv_npz(
        FIX_DIR / f"{REVUP}_RAW_PROJECTION_PUBLIC_CLAIM_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        stage="raw_projection_pre_attention_transforms", score_inputs_verified=False,
        scale_verified=False, bias_verified=False, dense_verified=False,
    )
    mutable_model = write_qkv_npz(
        FIX_DIR / f"{REVUP}_MUTABLE_MODEL_REVISION_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        model_revision="main",
    )
    mutable_tokenizer = write_qkv_npz(
        FIX_DIR / f"{REVUP}_MUTABLE_TOKENIZER_REVISION_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        tokenizer_revision="latest",
    )
    mutable_code = write_qkv_npz(
        FIX_DIR / f"{REVUP}_MUTABLE_REMOTE_CODE_REVISION_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        trust_remote_code=True, code_revision="main",
    )
    missing_reference = write_qkv_npz(
        FIX_DIR / f"{REVUP}_MISSING_DENSE_REFERENCE_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        include_reference=False,
    )
    forged_reference = write_qkv_npz(
        FIX_DIR / f"{REVUP}_FORGED_DENSE_REFERENCE_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        reference_offset=0.25,
    )
    unsupported_transform = write_qkv_npz(
        FIX_DIR / f"{REVUP}_UNSUPPORTED_SCORE_TRANSFORM_QKV_V2.npz", q, k, v, labels,
        public=True, source_type="public_pretrained_hf", model_id="org/model", generated_tiny=False,
        score_transform="scaled_dot_product_then_softcap_plus_bias",
    )
    score_only = write_scores_values_npz(FIX_DIR / f"{REVUP}_SCORES_VALUES_WITH_DHEAD.npz", q, k, v, labels, include_d_head=True)
    score_missing_d = write_scores_values_npz(FIX_DIR / f"{REVUP}_SCORES_VALUES_MISSING_DHEAD.npz", q, k, v, labels, include_d_head=False)
    nan_q = q.copy(); nan_q[0, 0] = np.nan
    nonfinite = write_qkv_npz(FIX_DIR / f"{REVUP}_NONFINITE_QKV_V2.npz", nan_q, k, v, labels)
    mismatched = write_qkv_npz(FIX_DIR / f"{REVUP}_MISMATCHED_QKV_V2.npz", q, k[:, :, :-1], v, labels)

    bad_hash_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_BAD_HASH_MANIFEST.json", publicish, expected_sha="0" * 64)
    redflag_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_REDFLAG_MANIFEST.json", redflag)
    raw_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_RAW_PROJECTION_MANIFEST.json", raw_projection)
    mutable_model_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_MUTABLE_MODEL_REVISION_MANIFEST.json", mutable_model)
    mutable_tokenizer_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_MUTABLE_TOKENIZER_REVISION_MANIFEST.json", mutable_tokenizer)
    mutable_code_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_MUTABLE_REMOTE_CODE_REVISION_MANIFEST.json", mutable_code)
    missing_reference_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_MISSING_DENSE_REFERENCE_MANIFEST.json", missing_reference)
    forged_reference_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_FORGED_DENSE_REFERENCE_MANIFEST.json", forged_reference)
    unsupported_transform_manifest = manifest_from_npz(FIX_DIR / f"{REVUP}_UNSUPPORTED_SCORE_TRANSFORM_MANIFEST.json", unsupported_transform)

    cases = [
        run_case(gate, name="good_nonpublic_qkv_uses_actual_dhead_and_score_contract", trace_npz=good, claim_public=False, provenance_json=None, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True, "evaluated_d_heads": [expected_d]}),
        run_case(gate, name="query_key_value_aliases_load", trace_npz=aliases, claim_public=False, provenance_json=None, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "compatible": True, "evaluated_d_heads": [expected_d]}),
        run_case(gate, name="flag_only_public_without_manifest", trace_npz=publicish, claim_public=True, provenance_json=None, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}),
        run_case(gate, name="manifest_hash_mismatch", trace_npz=publicish, claim_public=True, provenance_json=bad_hash_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="trace_npz_sha256 does not match"),
        run_case(gate, name="public_claim_redflag_npz", trace_npz=redflag, claim_public=True, provenance_json=redflag_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="red-flag"),
        run_case(gate, name="raw_projection_public_claim_rejected", trace_npz=raw_projection, claim_public=True, provenance_json=raw_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="attention_score_input_stage"),
        run_case(gate, name="mutable_model_revision_rejected", trace_npz=mutable_model, claim_public=True, provenance_json=mutable_model_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="model_revision must be an immutable"),
        run_case(gate, name="mutable_tokenizer_revision_rejected", trace_npz=mutable_tokenizer, claim_public=True, provenance_json=mutable_tokenizer_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="tokenizer_revision must be an immutable"),
        run_case(gate, name="mutable_trusted_remote_code_revision_rejected", trace_npz=mutable_code, claim_public=True, provenance_json=mutable_code_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="code_revision must be immutable"),
        run_case(gate, name="missing_dense_reference_output_rejected", trace_npz=missing_reference, claim_public=True, provenance_json=missing_reference_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="missing arrays: dense_reference_output"),
        run_case(gate, name="forged_dense_reference_rejected_by_recomputation", trace_npz=forged_reference, claim_public=True, provenance_json=forged_reference_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="recomputed dense-reference error"),
        run_case(gate, name="unsupported_score_transform_rejected", trace_npz=unsupported_transform, claim_public=True, provenance_json=unsupported_transform_manifest, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": True}, error_contains="score_transform must be"),
        run_case(gate, name="scores_values_with_dhead_diagnostic_only", trace_npz=score_only, claim_public=False, provenance_json=None, expected={"external_trace_loaded": True, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": False, "evaluated_d_heads": [expected_d]}),
        run_case(gate, name="scores_values_missing_dhead_rejected", trace_npz=score_missing_d, claim_public=False, provenance_json=None, expected={"external_trace_loaded": False, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": False}, error_contains="requires positive integer d_head"),
        run_case(gate, name="nonfinite_qkv_rejected", trace_npz=nonfinite, claim_public=False, provenance_json=None, expected={"external_trace_loaded": False, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": False}, error_contains="must be finite"),
        run_case(gate, name="mismatched_qkv_rejected", trace_npz=mismatched, claim_public=False, provenance_json=None, expected={"external_trace_loaded": False, "public_pretrained_trace_loaded": False, "accepted_as_public_pretrained_trace": False, "compatible": False}, error_contains="shape mismatch"),
    ]

    passed_cases = sum(1 for case in cases if case["passed"])
    case_by_name = {case["case"]: case for case in cases}
    malformed_names = {"scores_values_missing_dhead_rejected", "nonfinite_qkv_rejected", "mismatched_qkv_rejected"}
    malformed_rejected = sum(1 for case in cases if case["case"] in malformed_names and case["passed"])
    no_public_overclaim = all(case["gate"].get("public_pretrained_trace_loaded") is not True and case["gate"].get("accepted_as_public_pretrained_trace") is not True for case in cases)
    good_contract = case_by_name["good_nonpublic_qkv_uses_actual_dhead_and_score_contract"]["direct_score_contract"]
    forged_errors = " ".join(case_by_name["forged_dense_reference_rejected_by_recomputation"]["gate"].get("provenance_errors", []))
    summary = {
        "case_count": len(cases),
        "passed_cases": passed_cases,
        "all_cases_passed": passed_cases == len(cases),
        "public_pretrained_trace_loaded_any_case": any(case["gate"].get("public_pretrained_trace_loaded") is True for case in cases),
        "public_overclaim_prevented": no_public_overclaim,
        "malformed_cases_rejected": malformed_rejected,
        "nonfinite_gate_exception_observed": bool(case_by_name["nonfinite_qkv_rejected"]["gate"].get("gate_exception")),
        "shape_gate_exception_observed": bool(case_by_name["mismatched_qkv_rejected"]["gate"].get("gate_exception")),
        "missing_dhead_gate_exception_observed": bool(case_by_name["scores_values_missing_dhead_rejected"]["gate"].get("gate_exception")),
        "raw_projection_public_claim_rejected": case_by_name["raw_projection_public_claim_rejected"]["passed"],
        "immutable_model_revision_enforced": case_by_name["mutable_model_revision_rejected"]["passed"],
        "immutable_tokenizer_revision_enforced": case_by_name["mutable_tokenizer_revision_rejected"]["passed"],
        "immutable_trusted_code_revision_enforced": case_by_name["mutable_trusted_remote_code_revision_rejected"]["passed"],
        "score_semantics_required": case_by_name["unsupported_score_transform_rejected"]["passed"],
        "explicit_nonzero_score_bias_replayed": good_contract.get("computed") is True and float(good_contract.get("computed_dense_reference_max_abs_error", 1.0)) <= 1e-12,
        "dense_reference_recomputed": good_contract.get("computed") is True and good_contract.get("within_public_tolerance") is True,
        "missing_dense_reference_rejected": case_by_name["missing_dense_reference_output_rejected"]["passed"],
        "forged_dense_reference_rejected": case_by_name["forged_dense_reference_rejected_by_recomputation"]["passed"] and "recomputed dense-reference error" in forged_errors,
        "query_key_value_aliases_supported": case_by_name["query_key_value_aliases_load"]["passed"],
        "actual_q_head_dimension_propagated": case_by_name["good_nonpublic_qkv_uses_actual_dhead_and_score_contract"]["gate"].get("evaluated_d_heads") == [expected_d],
        "fixture_q_head_dimension": expected_d,
        "legacy_hardcoded_d_head": 32,
        "score_only_bundle_native_replay_compatible": case_by_name["scores_values_with_dhead_diagnostic_only"]["native_qkv_compatibility"]["compatible"],
        "good_qkv_native_replay_compatible": case_by_name["good_nonpublic_qkv_uses_actual_dhead_and_score_contract"]["native_qkv_compatibility"]["compatible"],
        "promotion_allowed": False,
        "remaining_blockers": [
            "actual_public_pretrained_post_transform_qkv_bundle_missing",
            "verified_capture_adapter_with_exact_score_semantics_and_dense_reference_parity_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "named_hardware_public_trace_replay_missing",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT",
        "generated_at": STAMP,
        "status": "pass_trace_fidelity_score_semantics_and_cost_accounting_preflight_no_public_evidence" if summary["all_cases_passed"] and no_public_overclaim else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "measurement_scope": "adversarial external-trace ingress: semantic Q/K stage, explicit scale/bias score rule, recomputed dense parity, immutable provenance, exact head-dimension accounting, aliases, and malformed-input rejection",
        "source_fixture": {"path": source.relative_to(ROOT).as_posix(), "sha256": sha256_file(source)},
        "gate_hardening": {
            "finite_qkv_required": True,
            "qkv_shape_contract_checked": True,
            "value_norm_shape_contract_checked": True,
            "actual_q_head_dimension_used_for_cost_accounting": True,
            "score_only_d_head_metadata_required": True,
            "public_raw_projection_capture_rejected": True,
            "explicit_attention_scale_and_score_bias_required": True,
            "dense_reference_parity_recomputed": True,
            "immutable_model_tokenizer_and_trusted_code_revisions_required": True,
            "qkv_aliases_supported": True,
            "npz_resource_limits_checked_before_array_load": True,
            "preflight_fixture_marker_rejected_for_public_claims": True,
        },
        "summary": summary,
        "cases": cases,
        "interpretation": "rev0076 closes four mission-level defects: raw projections cannot masquerade as scored Q/K; score scale/bias semantics cannot remain implicit; dense parity is recomputed rather than trusted; and imported traces no longer inherit a fake D=32 cost dimension. This remains ingress evidence, not public-model or GPU evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    run_manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "generated_at": STAMP,
        "command": "python experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "source_files": {
            THIS.relative_to(ROOT).as_posix(): sha256_file(THIS),
            GATE_SCRIPT.relative_to(ROOT).as_posix(): sha256_file(GATE_SCRIPT),
            CAPTURE_HELPER.relative_to(ROOT).as_posix(): sha256_file(CAPTURE_HELPER),
        },
        "fixture_files": {case["trace_npz"]: case["trace_sha256"] for case in cases},
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
    }
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "summary": summary}, indent=2))
    return 0 if artifact["status"].startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
