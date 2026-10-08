#!/usr/bin/env python3
"""Audit explicit generation cache implementation semantics for public cached-decode traces.

rev0101 fixes a remaining runtime drift seam: Hugging Face generation can use
several cache implementations (`dynamic`, `static`, `offloaded`,
`offloaded_static`, `quantized`).  A public trace that only says `use_cache=True`
can still silently inherit a different cache layout from model generation_config
or operator kwargs.  The public trace lane therefore requires an explicit
`cache_implementation="dynamic"` generate argument for score-path evidence; other
cache modes are later timing/baseline lanes.
"""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0101"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_PATH = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE_PATH = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
GEN_AUDIT_PATH = ROOT / "tools" / "public_trace_generation_token_audit.py"

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

def forge_cache_impl(src: Path, dst: Path, impl: str = "static") -> None:
    with np.load(src, allow_pickle=False) as data:
        payload = {k: data[k] for k in data.files}
    # Keep use_cache=True and dense math unchanged; only forge cache implementation metadata.
    payload["generation_cache_implementation"] = np.asarray([impl])
    payload["generation_config_json"] = np.asarray([json.dumps({
        "contract": "greedy_exact_length_cached_decode_generation_config_v3",
        "cache_implementation_contract": "hf_generate_dynamic_cache_v1",
        "cache_implementation": impl,
        "cache_implementation_source": "explicit_generate_argument",
        "cache_config": None,
        "strategy": "greedy",
        "do_sample": False,
        "num_beams": 1,
        "num_return_sequences": 1,
        "max_new_tokens": 2,
        "min_new_tokens": 2,
        "use_cache": True,
        "sampling_disabled": True,
        "exact_new_token_count_required": True,
        "beam_search_disabled": True,
        "temperature_effective": "ignored_do_sample_false",
        "top_k_effective": "ignored_do_sample_false",
        "top_p_effective": "ignored_do_sample_false",
        "position_policy": "all_tokens",
        "pad_token_id": None,
        "eos_token_id_sha256": payload["generation_config_json"][0] if False else "74234e98afe7498fb5daf1f36ac2d5a0e26fd599768c1e537f69ea0fb2c667a9",
    }, sort_keys=True, separators=(",", ":"))])
    import hashlib
    payload["generation_config_sha256"] = np.asarray([hashlib.sha256(str(payload["generation_config_json"][0]).encode("utf-8")).hexdigest()])
    np.savez_compressed(dst, **payload)

def main() -> int:
    cap = load_module(CAPTURE_PATH, "rev0101_capture_for_cache_audit")
    gate = load_module(GATE_PATH, "rev0101_gate_for_cache_audit")
    gen_audit = load_module(GEN_AUDIT_PATH, "rev0101_generation_token_fixture_writer")
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="cloudtainer_cache_impl_") as tmp:
        tmpdir = Path(tmp)
        good = tmpdir / "good_dynamic_cache.npz"
        forged = tmpdir / "forged_static_cache.npz"
        gen_audit.write_bundle(good, cap=cap, gate=gate, forge_generated_count=False)
        forge_cache_impl(good, forged, "static")
        good_contract = gate.verify_qkv_score_contract(good)
        try:
            forged_contract = gate.verify_qkv_score_contract(forged)
            forged_rejected = False
            forged_error = "forged static-cache bundle unexpectedly passed"
        except Exception as exc:
            forged_contract = None
            forged_rejected = True
            forged_error = str(exc)
        if good_contract.get("generation_cache_implementation") != gate.PUBLIC_REQUIRED_CACHE_IMPLEMENTATION:
            errors.append("good bundle did not preserve explicit dynamic cache metadata")
        if not good_contract.get("generation_determinism_verified"):
            errors.append("good bundle determinism was not verified after cache contract patch")
        if not forged_rejected:
            errors.append("forged static-cache metadata was not rejected")
    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "report": "public_trace_cache_implementation_audit",
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "cache_implementation_contract": gate.PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        "required_cache_implementation": gate.PUBLIC_REQUIRED_CACHE_IMPLEMENTATION,
        "good_dynamic_cache_verified": bool(good_contract.get("generation_determinism_verified")),
        "forged_static_cache_rejected": bool(forged_rejected),
        "forged_rejection_reason": forged_error,
        "forged_contract_if_unexpectedly_passed": forged_contract,
        "remaining_blockers": [
            "actual_public_pretrained_prefill_plus_cached_decode_dynamic_cache_trace_missing",
            "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "online_source_basis": [
            {"url": "https://huggingface.co/docs/transformers/en/main_classes/text_generation", "fact": "generate() exposes use_cache and cache_implementation; cache_implementation may be dynamic, static, offloaded, offloaded_static, or quantized."},
            {"url": "https://huggingface.co/docs/transformers/kv_cache", "fact": "Transformers cache strategies include offloaded dynamic/static caches and cache configuration through GenerationConfig or generate()."},
            {"url": "https://huggingface.co/docs/transformers/cache_explanation", "fact": "Cache classes/layers differ in how sequence length is handled and updated, making cache layout part of trace semantics."},
        ],
        "interpretation": "The public trace gate now rejects dense-parity-valid bundles whose only forged field is a non-dynamic generation cache implementation. Static/offloaded/quantized caches remain valid timing/baseline research lanes, but they cannot be the score-path evidence lane until separately contracted.",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_IMPLEMENTATION_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace cache implementation audit — {REVUP}",
        "",
        f"Status: `{report['status']}`  ",
        "Promotion allowed: `false`",
        "",
        report["interpretation"],
        "",
        f"- contract: `{report['cache_implementation_contract']}`",
        f"- required cache implementation: `{report['required_cache_implementation']}`",
        f"- good dynamic-cache bundle verified: `{report['good_dynamic_cache_verified']}`",
        f"- forged static-cache bundle rejected: `{report['forged_static_cache_rejected']}`",
        f"- forged rejection reason: `{report['forged_rejection_reason']}`",
        "",
        "## Remaining blockers",
        "",
    ]
    md.extend(f"- `{b}`" for b in report["remaining_blockers"])
    if errors:
        md.extend(["", "## Errors", ""] + [f"- {e}" for e in errors])
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_IMPLEMENTATION_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": errors, "forged_static_cache_rejected": forged_rejected}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
