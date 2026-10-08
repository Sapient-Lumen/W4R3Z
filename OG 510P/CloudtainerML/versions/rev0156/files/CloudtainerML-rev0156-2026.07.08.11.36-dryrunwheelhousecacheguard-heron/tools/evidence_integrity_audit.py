#!/usr/bin/env python3
from __future__ import annotations

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

POST = ROOT / "artifacts" / "probe-results" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT.json"
POST_AUD = OUT / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_AUDIT.json"
PRE = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
PRE_AUD = OUT / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_AUDIT.json"
MIS = OUT / f"{REVUP}_MISSION_WASTE_TRACE_FIDELITY_AUDIT.json"
CUR = OUT / f"{REVUP}_CURRENT_SCIENTIFIC_RUN_AUDIT.json"
LIN = OUT / f"{REVUP}_REVISION_LINEAGE_STATIC_AUDIT.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    runners = [
        (POST, "experiments/post_transform_trace_contract/post_transform_trace_contract.py"),
        (POST_AUD, "tools/post_transform_trace_contract_audit.py"),
        (PRE, "experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py"),
        (PRE_AUD, "tools/public_trace_acceptance_preflight_audit.py"),
        (MIS, "tools/mission_trace_fidelity_audit.py"),
        (LIN, "tools/revision_lineage_static_audit.py"),
        (CUR, "tools/current_scientific_run_audit.py"),
    ]
    for path, cmd in runners:
        if not path.exists():
            subprocess.run([sys.executable, cmd], cwd=ROOT, check=False)
    for path, _ in runners:
        if not path.exists():
            errors.append("missing " + path.relative_to(ROOT).as_posix())

    post = load(POST) if POST.exists() else {}
    post_aud = load(POST_AUD) if POST_AUD.exists() else {}
    pre = load(PRE) if PRE.exists() else {}
    pre_aud = load(PRE_AUD) if PRE_AUD.exists() else {}
    mis = load(MIS) if MIS.exists() else {}
    lin = load(LIN) if LIN.exists() else {}
    cur = load(CUR) if CUR.exists() else {}

    if post_aud and post_aud.get("status") != "pass":
        errors.append("post-transform contract audit failed")
    if pre_aud and pre_aud.get("status") != "pass":
        errors.append("preflight audit failed")
    if mis and mis.get("status") != "pass_with_blockers":
        errors.append("mission audit failed")
    if lin and lin.get("status") not in {"pass", "pass_with_debt"}:
        errors.append("revision lineage audit failed")
    if lin and lin.get("summary", {}).get("protected_public_trace_surfaces_safe") != 6:
        errors.append("public-trace historical lineage quarantine incomplete")
    if cur and cur.get("status") != "pass":
        errors.append("current scientific audit failed")

    for artifact, label in [(post, "post-transform contract"), (pre, "public trace preflight")]:
        if artifact:
            for key in ["promotion_allowed", "public_pretrained_trace_loaded", "gpu_fused_kernel_measured"]:
                if artifact.get(key) is not False:
                    errors.append(f"{label} {key} overclaim")
    ps = post.get("summary", {})
    if ps:
        for key in ["post_transform_contract_within_tolerance", "raw_projection_contract_rejected_or_out_of_tolerance", "synthetic_public_claim_rejected"]:
            if ps.get(key) is not True:
                errors.append(key + " not proven")
        if float(ps.get("post_transform_dense_reference_max_abs_error", 1.0)) > 1e-12:
            errors.append("post-transform dense replay not exact")
    pres = pre.get("summary", {})
    if pres:
        if pres.get("public_pretrained_trace_loaded_any_case") is not False:
            errors.append("fixture promoted as public in some preflight case")
        if pres.get("all_cases_passed") is not True:
            errors.append("preflight matrix did not pass")
        for key in ["raw_projection_public_claim_rejected", "actual_q_head_dimension_propagated", "score_semantics_required", "dense_reference_recomputed", "forged_dense_reference_rejected", "immutable_model_revision_enforced", "immutable_tokenizer_revision_enforced"]:
            if pres.get(key) is not True:
                errors.append(key + " not proven")
    if mis:
        if mis.get("promotion_allowed") is not False:
            errors.append("mission audit promoted lane")
        if mis.get("surface_coherence", {}).get("status") != "pass":
            errors.append("critical entry surfaces incoherent")
        if mis.get("trace_fidelity", {}).get("status") != "pass":
            errors.append("trace fidelity static checks failed")

    status = "pass_with_blockers" if not errors else "fail"
    interpretation = (
        "Evidence integrity passes with blockers because rev0077 adds executable post-transform adapter semantics while preserving the claim boundary: "
        "synthetic fixtures remain non-public, forged public provenance is rejected, the inherited 16-case preflight still passes, no GPU/fused result is claimed, and sparse-attention promotion stays false."
    )
    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "evidence_integrity_audit",
        "generated_at": META.get("generated_at"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "errors": errors,
        "warnings": warnings,
        "current_artifacts": [p.relative_to(ROOT).as_posix() for p in [POST, POST_AUD, PRE, PRE_AUD, MIS, LIN, CUR] if p.exists()],
        "remaining_blockers": META.get("known_remaining_blockers", []),
        "interpretation": interpretation,
    }
    (OUT / f"{REVUP}_EVIDENCE_INTEGRITY_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / f"{REVUP}_EVIDENCE_INTEGRITY_AUDIT.md").write_text(
        f"# Evidence integrity audit — {REV}\n\n**Status: {status}**\n\n{interpretation}\n", encoding="utf-8"
    )
    print(json.dumps({"status": status, "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
