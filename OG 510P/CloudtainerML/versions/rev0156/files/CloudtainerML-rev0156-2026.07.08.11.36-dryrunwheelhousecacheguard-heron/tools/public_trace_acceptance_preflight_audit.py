#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0076")
REVUP = REV.upper()
ART = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not ART.exists():
        subprocess.run([sys.executable, "experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py"], cwd=ROOT, check=False)
    if not ART.exists():
        errors.append("missing " + ART.relative_to(ROOT).as_posix())
        art, summary = {}, {}
    else:
        art = load(ART)
        summary = art.get("summary", {})

    if art:
        if art.get("revision") != REV:
            errors.append("artifact revision mismatch")
        if art.get("promotion_allowed") is not False:
            errors.append("preflight artifact promoted unexpectedly")
        if art.get("public_pretrained_trace_loaded") is not False:
            errors.append("preflight overclaims public/pretrained trace")
        if art.get("gpu_fused_kernel_measured") is not False:
            errors.append("preflight overclaims GPU/fused timing")
        required_true = [
            "all_cases_passed", "public_overclaim_prevented", "nonfinite_gate_exception_observed",
            "shape_gate_exception_observed", "missing_dhead_gate_exception_observed",
            "good_qkv_native_replay_compatible", "raw_projection_public_claim_rejected",
            "actual_q_head_dimension_propagated", "query_key_value_aliases_supported",
            "immutable_model_revision_enforced", "immutable_tokenizer_revision_enforced",
            "immutable_trusted_code_revision_enforced", "score_semantics_required",
            "explicit_nonzero_score_bias_replayed", "dense_reference_recomputed",
            "missing_dense_reference_rejected", "forged_dense_reference_rejected",
        ]
        for key in required_true:
            if summary.get(key) is not True:
                errors.append(f"{key} not proven")
        if summary.get("score_only_bundle_native_replay_compatible") is not False:
            errors.append("score-only bundle incorrectly marked native Q/K/V compatible")
        if summary.get("public_pretrained_trace_loaded_any_case") is not False:
            errors.append("some fixture was promoted as public/pretrained")
        case_count = int(summary.get("case_count", 0))
        if case_count < 16 or int(summary.get("passed_cases", 0)) != case_count:
            errors.append("sixteen-case-or-larger matrix did not fully pass")
        if int(summary.get("malformed_cases_rejected", 0)) < 3:
            errors.append("malformed fixture rejection coverage below three cases")
        if int(summary.get("fixture_q_head_dimension", -1)) != 12:
            errors.append("fixture q head dimension not observed as 12")
        if int(summary.get("legacy_hardcoded_d_head", -1)) != 32:
            warnings.append("legacy hardcoded dimension marker changed")
        for case in art.get("cases", []):
            if not case.get("passed"):
                errors.append("case failed: " + case.get("case", "unknown") + " " + str(case.get("failures")))
            gate = case.get("gate_result") or case.get("gate") or {}
            if gate.get("accepted_as_public_pretrained_trace") is True:
                errors.append("fixture accepted as public/pretrained: " + case.get("case", "unknown"))

    interpretation = (
        "rev0076 passes only if external trace ingress is fail-closed on malformed data, mutable provenance, "
        "raw pre-transform projections, missing or unsupported score semantics, and forged dense references; "
        "the imported trace's true d_head must also reach cost accounting. This is guardrail evidence, not a public-model or GPU result."
    )
    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_acceptance_preflight_audit",
        "generated_at": META.get("generated_at"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "errors": errors,
        "warnings": warnings,
        "key_metrics": summary,
        "interpretation": interpretation,
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_AUDIT.md").write_text(
        f"# Public trace acceptance preflight audit — {REV}\n\n**Status: {report['status']}**\n\n{interpretation}\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
