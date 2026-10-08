#!/usr/bin/env python3
"""Audit exact prompt manifest and tokenizer-call replay contract.

rev0102 closes a practical evidence gap left by prompt/token digests alone.  A
public Q/K/V trace must expose the exact prompt strings and explicit tokenizer
call knobs that produced the input_ids/attention_mask digests.  Otherwise the
trace can be dense-parity-valid but unreplayable by a later operator.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0102"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_PATH = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE_PATH = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
TOKEN_AUDIT_PATH = ROOT / "tools" / "public_trace_token_provenance_audit.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_forged_manifest_bundle(src: Path, dst: Path, *, cap) -> str:
    with np.load(src, allow_pickle=False) as data:
        arrays: dict[str, Any] = {name: data[name] for name in data.files}
    manifest_text = str(np.asarray(arrays["prompt_manifest_json"]).reshape(-1)[0])
    manifest = json.loads(manifest_text)
    # Recompute the manifest digest after changing only the prompt text.  This
    # proves the gate checks manifest content against prompt_text_sha256 and does
    # not merely trust prompt_manifest_sha256.
    manifest["prompts"][0]["text"] = "token provenance audit prompt with a forged text body"
    forged_text = cap._json_canonical_text(manifest)
    arrays["prompt_manifest_json"] = np.asarray([forged_text])
    arrays["prompt_manifest_sha256"] = np.asarray([sha256_text(forged_text)])
    np.savez_compressed(dst, **arrays)
    return forged_text


def main() -> int:
    cap = load_module(CAPTURE_PATH, f"{REVUP.lower()}_capture_for_prompt_manifest_audit")
    gate = load_module(GATE_PATH, f"{REVUP.lower()}_gate_for_prompt_manifest_audit")
    token_audit = load_module(TOKEN_AUDIT_PATH, f"{REVUP.lower()}_token_audit_helper_for_prompt_manifest")
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="cloudtainer_prompt_manifest_") as tmp:
        tmpdir = Path(tmp)
        good = tmpdir / "good_prompt_manifest.npz"
        forged = tmpdir / "forged_prompt_manifest_text.npz"
        token_audit.write_bundle(good, cap=cap, gate=gate, forge_prompt_count=False)
        good_contract = gate.verify_qkv_score_contract(good)
        forged_text = save_forged_manifest_bundle(good, forged, cap=cap)
        try:
            forged_contract = gate.verify_qkv_score_contract(forged)
            forged_rejected = False
            forged_error = "forged prompt manifest unexpectedly passed"
        except Exception as exc:
            forged_contract = None
            forged_rejected = True
            forged_error = str(exc)
        if good_contract.get("prompt_manifest_verified") is not True:
            errors.append("good bundle did not verify prompt manifest")
        if good_contract.get("token_provenance_verified") is not True:
            errors.append("good bundle did not verify token provenance")
        if good_contract.get("computed_dense_reference_max_abs_error", 1.0) > gate.PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            errors.append("good bundle dense parity failed")
        if not forged_rejected:
            errors.append("forged prompt manifest text was not rejected")
        report = {
            "project": "CloudtainerML",
            "revision": REV,
            "report": "public_trace_prompt_manifest_audit",
            "status": "pass_with_blockers" if not errors else "fail",
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            "prompt_manifest_contract": gate.PUBLIC_PROMPT_MANIFEST_CONTRACT,
            "token_provenance_contract": gate.PUBLIC_TOKEN_PROVENANCE_CONTRACT,
            "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
            "good_prompt_manifest_verified": bool(good_contract.get("prompt_manifest_verified")),
            "good_token_provenance_verified": bool(good_contract.get("token_provenance_verified")),
            "good_dense_error": float(good_contract.get("computed_dense_reference_max_abs_error", 0.0)),
            "forged_prompt_manifest_rejected": bool(forged_rejected),
            "forged_rejection_reason": forged_error,
            "forged_manifest_json_sha256": sha256_text(forged_text),
            "blockers": [
                "actual_public_pretrained_prompt_manifest_trace_missing",
                "transformers_runtime_and_tinyllama_snapshot_still_required_for_real_capture",
            ],
            "errors": errors,
            "warnings": [],
            "interpretation": (
                "Prompt/token digests now have a replayable public manifest: exact prompt text, explicit tokenizer-call knobs, and tokenizer surface facts must agree with input_ids/attention_mask/text hashes. The forged manifest keeps dense Q/K/V parity and a valid manifest digest but changes the prompt text, and the gate rejects it."
            ),
        }
    (OUT / f"{REVUP}_PUBLIC_TRACE_PROMPT_MANIFEST_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    (OUT / f"{REVUP}_PUBLIC_TRACE_PROMPT_MANIFEST_AUDIT.md").write_text(
        f"# Public trace prompt manifest audit — {REVUP}\n\n"
        f"Status: `{report['status']}`  \nPromotion allowed: `false`\n\n"
        f"## Result\n\n"
        f"- good prompt manifest verified: `{report['good_prompt_manifest_verified']}`\n"
        f"- forged prompt manifest rejected: `{report['forged_prompt_manifest_rejected']}`\n"
        f"- forged rejection reason: `{report['forged_rejection_reason']}`\n\n"
        f"## Interpretation\n\n{report['interpretation']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "errors": errors, "forged_rejected": forged_rejected}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
