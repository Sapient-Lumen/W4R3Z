#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0077")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

POST_REL = f"artifacts/probe-results/{REVUP}_POST_TRANSFORM_TRACE_CONTRACT.json"
POST_AUD_REL = f"artifacts/audit/{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_AUDIT.json"
POST_MAN_REL = f"artifacts/run-manifests/{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_RUN_MANIFEST.json"
PRE_REL = f"artifacts/probe-results/{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
PRE_AUD_REL = f"artifacts/audit/{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_AUDIT.json"
MIS_REL = f"artifacts/audit/{REVUP}_MISSION_WASTE_TRACE_FIDELITY_AUDIT.json"
LIN_REL = f"artifacts/audit/{REVUP}_REVISION_LINEAGE_STATIC_AUDIT.json"

RUNNERS = [
    (POST_REL, "experiments/post_transform_trace_contract/post_transform_trace_contract.py"),
    (POST_AUD_REL, "tools/post_transform_trace_contract_audit.py"),
    (PRE_REL, "experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py"),
    (PRE_AUD_REL, "tools/public_trace_acceptance_preflight_audit.py"),
    (MIS_REL, "tools/mission_trace_fidelity_audit.py"),
    (LIN_REL, "tools/revision_lineage_static_audit.py"),
]
SRC_RELS = [
    "experiments/post_transform_trace_contract/post_transform_trace_contract.py",
    "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "tools/post_transform_trace_contract_audit.py",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def ensure_outputs() -> None:
    for rel, cmd in RUNNERS:
        if not (ROOT / rel).exists():
            subprocess.run([sys.executable, cmd], cwd=ROOT, check=False)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    ensure_outputs()
    for rel, _ in RUNNERS:
        if not (ROOT / rel).exists():
            errors.append("missing " + rel)
    if not (ROOT / POST_MAN_REL).exists():
        errors.append("missing " + POST_MAN_REL)

    post = load(POST_REL) if (ROOT / POST_REL).exists() else {}
    post_aud = load(POST_AUD_REL) if (ROOT / POST_AUD_REL).exists() else {}
    pre = load(PRE_REL) if (ROOT / PRE_REL).exists() else {}
    pre_aud = load(PRE_AUD_REL) if (ROOT / PRE_AUD_REL).exists() else {}
    mis = load(MIS_REL) if (ROOT / MIS_REL).exists() else {}
    lin = load(LIN_REL) if (ROOT / LIN_REL).exists() else {}
    post_man = load(POST_MAN_REL) if (ROOT / POST_MAN_REL).exists() else {}

    ps = post.get("summary", {})
    if post_aud and post_aud.get("status") != "pass":
        errors.append("post-transform contract audit failed")
    if pre_aud and pre_aud.get("status") != "pass":
        errors.append("public trace preflight audit failed")
    if mis and mis.get("status") != "pass_with_blockers":
        errors.append("mission/trace fidelity audit failed")
    if lin and lin.get("status") not in {"pass", "pass_with_debt"}:
        errors.append("revision lineage audit failed")
    if lin and lin.get("summary", {}).get("protected_public_trace_surfaces_safe") != 6:
        errors.append("historical public-trace surfaces are not fully pinned")

    if post:
        if post.get("revision") != REV:
            errors.append("post artifact revision mismatch")
        if post.get("promotion_allowed") is not False or post.get("public_pretrained_trace_loaded") is not False or post.get("gpu_fused_kernel_measured") is not False:
            errors.append("post artifact evidence overclaim")
        for key in [
            "post_transform_contract_within_tolerance", "raw_projection_contract_rejected_or_out_of_tolerance",
            "finite_score_bias", "nonzero_finite_bias_exercised", "gate_external_nonpublic_loaded",
            "gate_actual_d_head_propagated", "gate_result_row_count_positive", "synthetic_public_claim_rejected",
        ]:
            if ps.get(key) is not True:
                errors.append(key + " missing")
        if int(ps.get("row_count", 0)) < 50:
            errors.append("post-transform row coverage too small")
        if float(ps.get("raw_projection_against_post_reference_max_abs_error", 0.0)) <= 1e-5:
            errors.append("raw projection negative control too weak")
    if pre:
        s = pre.get("summary", {})
        if s.get("all_cases_passed") is not True or s.get("public_overclaim_prevented") is not True:
            errors.append("rev0077 inherited preflight did not pass")
        if s.get("actual_q_head_dimension_propagated") is not True:
            errors.append("preflight D accounting regression")

    if post_man:
        srcs = post_man.get("source_files", {})
        for rel in SRC_RELS[:2]:
            if rel not in srcs:
                errors.append("run manifest missing source hash: " + rel)
            elif srcs[rel] != sha256_file(ROOT / rel):
                errors.append("source hash mismatch: " + rel)
        if post_man.get("artifact_sha256") and (ROOT / POST_REL).exists() and post_man.get("artifact_sha256") != sha256_file(ROOT / POST_REL):
            errors.append("post artifact hash mismatch in run manifest")

    interpretation = (
        "The current executable evidence is no longer only ingress governance: rev0077 adds a deterministic post-transform trace contract harness. "
        "It proves exact replay from post-transform Q/K/V with explicit scale and finite causal score bias, proves raw projection Q/K cannot reproduce the same reference, and confirms the existing gate treats it as non-public synthetic evidence. "
        "It still does not improve sparse-attention quality or speed and does not justify promotion without real public-model capture or named-hardware execution."
    )
    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "current_scientific_run_audit",
        "generated_at": META.get("generated_at"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "current_artifacts": [POST_REL, POST_AUD_REL, PRE_REL, PRE_AUD_REL, MIS_REL, LIN_REL],
        "key_metrics": ps,
        "errors": errors,
        "warnings": warnings,
        "interpretation": interpretation,
    }
    (OUT / f"{REVUP}_CURRENT_SCIENTIFIC_RUN_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / f"{REVUP}_CURRENT_SCIENTIFIC_RUN_AUDIT.md").write_text(
        f"# Current scientific run audit — {REV}\n\n**Status: {report['status']}**\n\n{interpretation}\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
