#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0077")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
ART = ROOT / "artifacts" / "probe-results" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT.json"
MAN = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_RUN_MANIFEST.json"
RUNNER = ROOT / "experiments" / "post_transform_trace_contract" / "post_transform_trace_contract.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not ART.exists():
        subprocess.run([sys.executable, RUNNER.relative_to(ROOT).as_posix()], cwd=ROOT, check=False)
    if not ART.exists():
        errors.append("missing " + ART.relative_to(ROOT).as_posix())
        artifact = {}
        summary = {}
    else:
        artifact = load(ART)
        summary = artifact.get("summary", {})
    if not MAN.exists():
        errors.append("missing " + MAN.relative_to(ROOT).as_posix())
        manifest = {}
    else:
        manifest = load(MAN)

    if artifact:
        if artifact.get("revision") != REV:
            errors.append("artifact revision mismatch")
        if artifact.get("promotion_allowed") is not False:
            errors.append("artifact overclaims promotion")
        if artifact.get("public_pretrained_trace_loaded") is not False:
            errors.append("synthetic contract overclaims public/pretrained trace")
        if artifact.get("gpu_fused_kernel_measured") is not False:
            errors.append("synthetic contract overclaims GPU/fused timing")
        if not str(artifact.get("status", "")).startswith("pass"):
            errors.append("contract artifact status is not pass")
        required_true = [
            "post_transform_contract_within_tolerance",
            "raw_projection_contract_rejected_or_out_of_tolerance",
            "finite_score_bias",
            "nonzero_finite_bias_exercised",
            "gate_external_nonpublic_loaded",
            "gate_actual_d_head_propagated",
            "gate_result_row_count_positive",
            "synthetic_public_claim_rejected",
            "public_attempt_error_mentions_npz_self_attestation",
        ]
        for key in required_true:
            if summary.get(key) is not True:
                errors.append(f"summary {key} missing or false")
        if int(summary.get("row_count", 0)) < 50:
            errors.append("insufficient row coverage")
        if int(summary.get("prompt_count", 0)) < 3:
            errors.append("insufficient prompt coverage")
        if int(summary.get("position_count", 0)) < 6:
            errors.append("insufficient position coverage")
        if int(summary.get("layer_count", 0)) < 3:
            errors.append("insufficient layer coverage")
        if int(summary.get("head_count", 0)) < 2:
            errors.append("insufficient head coverage")
        if int(summary.get("d_head", 0)) != 16:
            errors.append("unexpected d_head; audit expects contract fixture D=16")
        if float(summary.get("post_transform_dense_reference_max_abs_error", 1.0)) > 1e-12:
            errors.append("post-transform dense replay is not exact")
        if float(summary.get("raw_projection_against_post_reference_max_abs_error", 0.0)) <= 1e-5:
            errors.append("raw projection negative control did not exceed public tolerance")
        gate = artifact.get("gate_nonpublic_replay", {})
        if gate.get("evaluated_d_heads") != [16]:
            errors.append("gate did not propagate D=16")
        if gate.get("trace_row_count") != summary.get("row_count"):
            errors.append("gate row count does not match contract rows")
        if gate.get("oracle_leakage_rows") is None or int(gate.get("oracle_leakage_rows")) != 0:
            errors.append("oracle leakage rows detected")
        public_attempt = artifact.get("forged_public_claim_attempt", {})
        if public_attempt.get("accepted_as_public_pretrained_trace") is True:
            errors.append("forged public manifest was accepted")
        for name, info in artifact.get("bundles", {}).items():
            path = ROOT / info.get("path", "")
            if not path.exists():
                errors.append(f"missing bundle {name}: {info.get('path')}")
            elif info.get("sha256") != sha256_file(path):
                errors.append(f"bundle sha mismatch: {name}")
    if manifest:
        if manifest.get("artifact_sha256") and ART.exists() and manifest.get("artifact_sha256") != sha256_file(ART):
            errors.append("run manifest artifact hash mismatch")
        source_files = manifest.get("source_files", {})
        runner_rel = RUNNER.relative_to(ROOT).as_posix()
        if source_files.get(runner_rel) != sha256_file(RUNNER):
            errors.append("run manifest runner hash mismatch")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "post_transform_trace_contract_audit",
        "generated_at": META.get("generated_at"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "artifact": ART.relative_to(ROOT).as_posix(),
        "errors": errors,
        "warnings": warnings,
        "key_metrics": summary,
        "interpretation": (
            "The rev0077 contract harness provides substantive adapter progress: post-transform Q/K/V plus explicit scale and finite score bias replays exactly, "
            "raw projection Q/K fails against that same reference, and the gate treats the bundle as non-public while rejecting a forged public claim. It is synthetic contract evidence, not pretrained-model evidence."
        ),
    }
    (OUT / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_AUDIT.md").write_text(
        f"# Post-transform trace contract audit — {REV}\n\n**Status: {report['status']}**\n\n{report['interpretation']}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
