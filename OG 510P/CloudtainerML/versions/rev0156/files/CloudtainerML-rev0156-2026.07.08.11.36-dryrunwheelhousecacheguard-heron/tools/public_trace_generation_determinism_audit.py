#!/usr/bin/env python3
"""Audit deterministic generation semantics for public cached-decode traces.

rev0091 retains the replay gap guard that survived generated-token digests: a trace can
bind the emitted token IDs and still fail to identify the generation strategy
that produced those IDs.  In Hugging Face generation, `do_sample=False` with
`num_beams=1` is greedy decoding, while `do_sample=False` with `num_beams>1` is
beam search.  This audit proves the public gate rejects a dense-parity-valid
bundle whose only forgery is the beam-count/strategy metadata.
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
REV = META.get("revision", "rev0091")
REVUP = str(REV).upper()
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


def forge_npz_beam_count(src: Path, dst: Path, forged_num_beams: int = 4) -> None:
    with np.load(src, allow_pickle=False) as data:
        payload = {k: data[k] for k in data.files}
    payload["generation_num_beams"] = np.asarray([int(forged_num_beams)], dtype=np.int64)
    np.savez_compressed(dst, **payload)


def main() -> int:
    cap = load_module(CAPTURE_PATH, "rev0091_capture_for_generation_determinism_audit")
    gate = load_module(GATE_PATH, "rev0091_gate_for_generation_determinism_audit")
    gen_audit = load_module(GEN_AUDIT_PATH, "rev0091_generation_token_audit_fixture_writer")
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="cloudtainer_generation_determinism_") as tmp:
        tmpdir = Path(tmp)
        good = tmpdir / "good_greedy_generation.npz"
        forged = tmpdir / "forged_beam_generation.npz"
        gen_audit.write_bundle(good, cap=cap, gate=gate, forge_generated_count=False)
        forge_npz_beam_count(good, forged, forged_num_beams=4)
        good_contract = gate.verify_qkv_score_contract(good)
        try:
            forged_contract = gate.verify_qkv_score_contract(forged)
            forged_rejected = False
            forged_error = "forged beam-count bundle unexpectedly passed"
        except Exception as exc:
            forged_contract = None
            forged_rejected = True
            forged_error = str(exc)
        if good_contract.get("generation_determinism_verified") is not True:
            errors.append("good bundle did not verify greedy generation determinism")
        if good_contract.get("generation_token_provenance_verified") is not True:
            errors.append("good bundle did not verify generated-token provenance")
        if good_contract.get("computed_dense_reference_max_abs_error", 1.0) > gate.PUBLIC_DENSE_PARITY_MAX_ABS_ERROR:
            errors.append("good bundle dense parity failed")
        if not forged_rejected:
            errors.append("forged beam-count generation metadata was not rejected")
        report = {
            "project": "CloudtainerML",
            "revision": REV,
            "report": "public_trace_generation_determinism_audit",
            "status": "pass_with_blockers" if not errors else "fail",
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
            "generation_determinism_contract": gate.PUBLIC_GENERATION_DETERMINISM_CONTRACT,
            "generation_token_contract": gate.PUBLIC_GENERATION_TOKEN_CONTRACT,
            "good_generation_determinism_verified": bool(good_contract.get("generation_determinism_verified")),
            "good_generation_token_verified": bool(good_contract.get("generation_token_provenance_verified")),
            "good_dense_error": float(good_contract.get("computed_dense_reference_max_abs_error", 0.0)),
            "forged_beam_count_rejected": bool(forged_rejected),
            "forged_rejection_reason": forged_error,
            "forged_contract_if_unexpectedly_passed": forged_contract,
            "remaining_blockers": [
                "actual_public_pretrained_prefill_plus_cached_decode_generation_determinism_trace_missing",
                "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
                "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
            ],
            "errors": errors,
            "interpretation": (
                "The gate now rejects a dense-parity-valid cached-decode trace when the generation metadata indicates beam search or another non-greedy path. "
                "This prevents inherited model generation_config values from masquerading as deterministic greedy replay merely because generated token digests, exact-length counts, and local attention math match."
            ),
        }
    (OUT / f"{REVUP}_PUBLIC_TRACE_GENERATION_DETERMINISM_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        f"# Public trace generation determinism audit — {REV}",
        "",
        f"**Status:** {report['status']}",
        "",
        report["interpretation"],
        "",
        f"- deterministic generation contract: `{report['generation_determinism_contract']}`",
        f"- trace claim version: `{report['trace_claim_version']}`",
        f"- good bundle determinism verified: `{report['good_generation_determinism_verified']}`",
        f"- good bundle generated-token provenance verified: `{report['good_generation_token_verified']}`",
        f"- good dense error: `{report['good_dense_error']}`",
        f"- forged beam-count bundle rejected: `{report['forged_beam_count_rejected']}`",
        f"- forged rejection reason: `{report['forged_rejection_reason']}`",
        "",
        "## Remaining blockers",
        "",
    ]
    md.extend(f"- `{b}`" for b in report["remaining_blockers"])
    if errors:
        md.extend(["", "## Errors", ""] + [f"- {e}" for e in errors])
    (OUT / f"{REVUP}_PUBLIC_TRACE_GENERATION_DETERMINISM_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": errors, "forged_beam_count_rejected": forged_rejected}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
