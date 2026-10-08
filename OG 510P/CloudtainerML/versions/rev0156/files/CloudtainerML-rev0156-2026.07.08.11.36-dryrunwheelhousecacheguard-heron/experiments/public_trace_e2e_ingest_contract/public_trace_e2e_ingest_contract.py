#!/usr/bin/env python3
"""Frozen historical rev0073 public trace end-to-end ingest contract.

The highest-priority lane is actual public/pretrained trace capture. This probe
cannot create that evidence in an offline CPU capsule without transformers or a
cached public model. Instead it closes the next dangerous loophole: a detached
JSON manifest could lie about a local fixture. rev0073 requires NPZ-embedded
self-attestation from the capture helper and cross-checks it against the JSON
manifest before a trace may be labeled public/pretrained.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_RUNNER = True
ORIGINAL_REV = "rev0073"
REV = ORIGINAL_REV
REVUP = REV.upper()
STAMP = "2026-06-18T18:06:00-04:00"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT.json"
MAN = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT_RUN_MANIFEST.json"
BUNDLE_DIR = ROOT / "artifacts" / "trace-bundles"
FORGED_MANIFEST = BUNDLE_DIR / f"{REVUP}_FORGED_PUBLIC_MANIFEST_FOR_LEGACY_FIXTURE.json"
SELF_FIXTURE = BUNDLE_DIR / f"{REVUP}_SELF_DECLARED_LOCAL_FIXTURE_QKV.npz"
SELF_FORGED_MANIFEST = BUNDLE_DIR / f"{REVUP}_FORGED_PUBLIC_MANIFEST_FOR_SELF_DECLARED_FIXTURE.json"
TEMPLATE = BUNDLE_DIR / f"{REVUP}_PUBLIC_PRETRAINED_TRACE_PROVENANCE_TEMPLATE.json"
GATE_SCRIPT = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
CAPTURE_HELPER = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_gate_module():
    spec = importlib.util.spec_from_file_location("public_trace_gate_surrogate_rev0073", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load public trace gate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def module_status(name: str) -> dict[str, Any]:
    try:
        mod = __import__(name)
        return {"available": True, "version": str(getattr(mod, "__version__", "unknown"))}
    except Exception as exc:
        return {"available": False, "error": repr(exc)}


def capture_environment() -> dict[str, Any]:
    torch_status = module_status("torch")
    cuda_available = False
    if torch_status.get("available"):
        try:
            import torch  # type: ignore
            cuda_available = bool(torch.cuda.is_available())
        except Exception:
            cuda_available = False
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hub = hf_home / "hub"
    cached_models = []
    if hub.exists():
        cached_models = [p.name for p in hub.glob("models--*")][:20]
    return {
        "torch": torch_status,
        "transformers": module_status("transformers"),
        "transformer_lens": module_status("transformer_lens"),
        "cuda_available": cuda_available,
        "hf_home": hf_home.as_posix(),
        "hf_hub_exists": hub.exists(),
        "cached_model_count_sampled": len(cached_models),
        "cached_models_sample": cached_models,
        "capture_helper_present": CAPTURE_HELPER.exists(),
        "capture_helper_sha256": sha256_file(CAPTURE_HELPER) if CAPTURE_HELPER.exists() else None,
    }


def source_fixture() -> Path:
    candidates = [
        BUNDLE_DIR / "REV0072_TRACE_CLAIM_FIXTURE_QKV.npz",
        BUNDLE_DIR / "REV0062_TINY_TRAINED_QK_TRACE_PACKET.npz",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("no local Q/K/V fixture found")


def as_qkv_arrays(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    z = np.load(path, allow_pickle=False)
    if {"q", "k", "v"}.issubset(set(z.files)):
        q = np.asarray(z["q"], dtype=np.float64)
        k = np.asarray(z["k"], dtype=np.float64)
        v = np.asarray(z["v"], dtype=np.float64)
    elif {"queries", "keys", "values"}.issubset(set(z.files)):
        q = np.asarray(z["queries"], dtype=np.float64)
        k = np.asarray(z["keys"], dtype=np.float64)
        v = np.asarray(z["values"], dtype=np.float64)
    else:
        raise ValueError("fixture lacks q/k/v or queries/keys/values")
    limit = min(32, q.shape[0])
    labels: dict[str, np.ndarray] = {}
    for name in ["regime", "layer", "head", "position", "example", "trace_batch"]:
        if name in z.files:
            labels[name] = z[name][:limit]
    return q[:limit], k[:limit], v[:limit], labels


def old_manifest_only_would_accept(manifest: dict[str, Any], trace_sha: str) -> bool:
    required = [
        "trace_claim_version", "public_pretrained_trace", "source_type",
        "model_id", "weights_source", "license", "trace_npz_sha256",
        "schema", "capture_tool", "capture_tool_sha256",
        "generated_from_local_tiny_model", "uses_random_weights", "provenance_reviewed",
    ]
    allowed = {"public_pretrained_hf", "public_pretrained_transformerlens", "public_pretrained_manual_export"}
    return (
        all(k in manifest for k in required)
        and manifest.get("public_pretrained_trace") is True
        and manifest.get("source_type") in allowed
        and bool(str(manifest.get("model_id", "")).strip())
        and bool(str(manifest.get("weights_source", "")).strip())
        and bool(str(manifest.get("license", "")).strip())
        and manifest.get("trace_npz_sha256") == trace_sha
        and manifest.get("schema") in {"qkv_npz_v1", "scores_values_npz_v1"}
        and manifest.get("generated_from_local_tiny_model") is False
        and manifest.get("uses_random_weights") is False
        and manifest.get("provenance_reviewed") is True
        and isinstance(manifest.get("capture_tool_sha256"), str)
        and len(manifest.get("capture_tool_sha256")) == 64
    )


def write_manifest(path: Path, trace_npz: Path, *, model_id: str, source_type: str = "public_pretrained_hf", public: bool = True, generated_tiny: bool = False, random_weights: bool = False, reviewed: bool = True) -> dict[str, Any]:
    manifest = {
        "trace_claim_version": "public_trace_claim_v1",
        "public_pretrained_trace": bool(public),
        "source_type": source_type,
        "model_id": model_id,
        "weights_source": "declared pretrained checkpoint from a public model hub",
        "license": "declared-open-model-license-placeholder-for-contract-test",
        "trace_npz_sha256": sha256_file(trace_npz),
        "schema": "qkv_npz_v1",
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_HELPER),
        "generated_from_local_tiny_model": bool(generated_tiny),
        "uses_random_weights": bool(random_weights),
        "provenance_reviewed": bool(reviewed),
        "contract_test_note": "This is a rev0073 contract-control manifest, not public evidence.",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def make_self_declared_local_fixture(src: Path) -> dict[str, Any]:
    q, k, v, labels = as_qkv_arrays(src)
    SELF_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        SELF_FIXTURE,
        q=q,
        k=k,
        v=v,
        **labels,
        trace_claim_version=np.asarray(["public_trace_claim_v1"]),
        public_pretrained_trace=np.asarray([False]),
        source_type=np.asarray(["local_fixture_from_tiny_trained_trace"]),
        model_id=np.asarray(["local_tiny_transformer_fixture_not_public"]),
        weights_source=np.asarray(["local synthetic training run"]),
        license=np.asarray(["not applicable; fixture only"]),
        schema=np.asarray(["qkv_npz_v1"]),
        capture_tool=np.asarray(["experiments/public_trace_e2e_ingest_contract/public_trace_e2e_ingest_contract.py"]),
        capture_tool_sha256=np.asarray([sha256_file(Path(__file__).resolve())]),
        generated_from_local_tiny_model=np.asarray([True]),
        uses_random_weights=np.asarray([False]),
        provenance_reviewed=np.asarray([True]),
    )
    return {
        "path": SELF_FIXTURE.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(SELF_FIXTURE),
        "rows": int(q.shape[0]),
        "n": int(k.shape[1]),
        "d": int(q.shape[-1]),
        "dv": int(v.shape[-1]),
    }


def write_template() -> dict[str, Any]:
    template = {
        "trace_claim_version": "public_trace_claim_v1",
        "public_pretrained_trace": True,
        "source_type": "public_pretrained_hf",
        "model_id": "<public Hugging Face model id or local path tied to a public checkpoint>",
        "weights_source": "<URL or exact source for pretrained weights>",
        "license": "<model license/source terms>",
        "trace_npz_sha256": "<sha256 of captured NPZ>",
        "schema": "qkv_npz_v1",
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_HELPER),
        "generated_from_local_tiny_model": False,
        "uses_random_weights": False,
        "provenance_reviewed": True,
        "required_command_shape": "python experiments/public_trace_capture/hf_attention_trace_capture.py --model <model> --out artifacts/trace-bundles/<name>.npz --provenance-out artifacts/trace-bundles/<name>.provenance.json --public-pretrained-trace --weights-source <source> --license <license> --provenance-reviewed",
        "next_replay_command_shape": "python experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py --trace-npz <npz> --public-pretrained-trace --provenance-json <manifest>",
    }
    TEMPLATE.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": TEMPLATE.relative_to(ROOT).as_posix(), "sha256": sha256_file(TEMPLATE)}


def compact_case(payload: dict[str, Any]) -> dict[str, Any]:
    decl = payload.get("external_trace_declaration", {})
    ps = decl.get("provenance_status", {})
    npz = ps.get("npz_metadata_status", {})
    summ = payload.get("summary", {})
    return {
        "trace_gate_status": payload.get("trace_gate_status"),
        "external_trace_loaded": payload.get("external_trace_loaded"),
        "public_pretrained_trace_loaded": payload.get("public_pretrained_trace_loaded"),
        "accepted_as_public_pretrained_trace": decl.get("accepted_as_public_pretrained_trace"),
        "provenance_status": ps.get("status"),
        "provenance_error_count": len(ps.get("errors", []) or []),
        "provenance_errors": ps.get("errors", [])[:10],
        "npz_metadata_status": npz.get("status"),
        "npz_red_flag_terms": npz.get("red_flag_terms", []),
        "missing_public_self_attestation_fields": npz.get("missing_public_self_attestation_fields", []),
        "trace_row_count": summ.get("trace_row_count"),
        "result_row_count": summ.get("result_row_count"),
        "oracle_leakage_rows": summ.get("oracle_leakage_rows"),
        "trace_source_types": summ.get("trace_source_types"),
    }


def main() -> int:
    gate = load_gate_module()
    env = capture_environment()
    src = source_fixture()
    src_sha = sha256_file(src)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    forged = write_manifest(FORGED_MANIFEST, src, model_id="gpt2")
    legacy_would_accept = old_manifest_only_would_accept(forged, src_sha)
    forged_result = compact_case(gate.run(src, public_pretrained_trace=True, trace_source_label="rev0073_legacy_fixture_forged_public_manifest", bundle_model_id="gpt2", bundle_license=forged["license"], provenance_json=FORGED_MANIFEST))

    self_info = make_self_declared_local_fixture(src)
    self_forged = write_manifest(SELF_FORGED_MANIFEST, SELF_FIXTURE, model_id="gpt2")
    self_result = compact_case(gate.run(SELF_FIXTURE, public_pretrained_trace=True, trace_source_label="rev0073_self_declared_local_fixture_forged_public_manifest", bundle_model_id="gpt2", bundle_license=self_forged["license"], provenance_json=SELF_FORGED_MANIFEST))
    external_control = compact_case(gate.run(SELF_FIXTURE, public_pretrained_trace=False, trace_source_label="rev0073_self_declared_fixture_schema_only", bundle_model_id="local_fixture", bundle_license="not_public", provenance_json=None))
    template = write_template()

    capture_executable_here = bool(env["torch"].get("available") and env["transformers"].get("available") and env.get("cached_model_count_sampled", 0) > 0)
    summary = {
        "public_pretrained_trace_loaded": False,
        "promotion_allowed": False,
        "capture_executable_in_this_capsule": capture_executable_here,
        "blocked_reason": None if capture_executable_here else "no transformers package and no sampled local Hugging Face model cache in this capsule",
        "legacy_manifest_only_contract_would_have_accepted_forged_fixture": legacy_would_accept,
        "rev0073_rejected_forged_legacy_fixture_by_npz_self_attestation": forged_result["public_pretrained_trace_loaded"] is False and forged_result["provenance_status"] == "public_pretrained_claim_rejected",
        "rev0073_rejected_self_declared_local_fixture": self_result["public_pretrained_trace_loaded"] is False and self_result["provenance_status"] == "public_pretrained_claim_rejected",
        "schema_only_external_trace_still_loads_without_public_claim": external_control["external_trace_loaded"] is True and external_control["public_pretrained_trace_loaded"] is False,
        "oracle_leakage_rows_total": sum(int(x.get("oracle_leakage_rows") or 0) for x in [forged_result, self_result, external_control]),
        "public_capture_contract_ready": True,
        "next_substantive_step": "run the updated capture helper in an environment with transformers and a cached public pretrained model, emit the paired NPZ + provenance JSON, then run the public trace gate and native QK replay on that bundle",
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_PUBLIC_TRACE_E2E_INGEST_CONTRACT",
        "generated_at": STAMP,
        "measurement_scope": "end-to-end public/pretrained trace ingest contract and local environment readiness; no public/pretrained model was captured in this offline capsule",
        "capture_environment": env,
        "source_fixture": {"path": src.relative_to(ROOT).as_posix(), "sha256": src_sha},
        "self_declared_local_fixture": self_info,
        "manifest_controls": {
            "forged_legacy_fixture_manifest": {"path": FORGED_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256_file(FORGED_MANIFEST), "legacy_manifest_only_would_accept": legacy_would_accept},
            "forged_self_declared_fixture_manifest": {"path": SELF_FORGED_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256_file(SELF_FORGED_MANIFEST)},
            "public_pretrained_manifest_template": template,
        },
        "cases": {
            "forged_public_manifest_on_legacy_fixture": forged_result,
            "forged_public_manifest_on_self_declared_local_fixture": self_result,
            "schema_only_external_control": external_control,
        },
        "summary": summary,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "interpretation": "rev0073 makes the public/pretrained trace path more executable and harder to fake: the capture helper now emits NPZ self-attestation plus JSON provenance, and the gate rejects detached manifests that try to promote old/local fixtures. The actual public/pretrained trace bundle remains missing in this capsule.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "generated_at": STAMP,
        "command": "python experiments/public_trace_e2e_ingest_contract/public_trace_e2e_ingest_contract.py",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "source_files": {
            str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__).resolve()),
            str(GATE_SCRIPT.relative_to(ROOT)): sha256_file(GATE_SCRIPT),
            str(CAPTURE_HELPER.relative_to(ROOT)): sha256_file(CAPTURE_HELPER),
        },
        "inputs": {
            src.relative_to(ROOT).as_posix(): src_sha,
            FORGED_MANIFEST.relative_to(ROOT).as_posix(): sha256_file(FORGED_MANIFEST),
            SELF_FIXTURE.relative_to(ROOT).as_posix(): sha256_file(SELF_FIXTURE),
            SELF_FORGED_MANIFEST.relative_to(ROOT).as_posix(): sha256_file(SELF_FORGED_MANIFEST),
            TEMPLATE.relative_to(ROOT).as_posix(): sha256_file(TEMPLATE),
        },
        "artifact_sha256": sha256_file(OUT),
        "promotion_allowed": False,
    }
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
