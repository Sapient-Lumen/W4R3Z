#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
RUN_REL = f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"
ONE_SHOT_REL = f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"
STABLE_RUN_REL = "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh"
RUN_PACKET_REL = f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json"
PROMPT_REL = f"artifacts/prompts/{REVUP}_PUBLIC_TRACE_PROMPTS.txt"


def noncomment_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    one_shot = ROOT / ONE_SHOT_REL
    run = ROOT / RUN_REL
    stable_run = ROOT / STABLE_RUN_REL
    prompt_path = ROOT / PROMPT_REL
    run_packet = ROOT / RUN_PACKET_REL
    one_src = read(ONE_SHOT_REL)
    run_src = read(RUN_REL)
    stable_src = read(STABLE_RUN_REL)
    prompts: list[str] = noncomment_lines(prompt_path) if prompt_path.exists() else []
    inline_prompt_args = re.findall(r"--prompt\s+\"", one_src + "\n" + run_src)
    expected_default = f'artifacts/prompts/${{REVUP}}_PUBLIC_TRACE_PROMPTS.txt'
    literal_default = f'artifacts/prompts/{REVUP}_PUBLIC_TRACE_PROMPTS.txt'

    if not stable_run.is_file():
        errors.append("missing_stable_run_wrapper")
    elif f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in stable_src:
        errors.append("stable_run_wrapper_not_targeting_current_revision")
    if not run.is_file():
        errors.append("missing_current_run_wrapper")
    if not one_shot.is_file():
        errors.append("missing_current_one_shot_wrapper")
    if not prompt_path.is_file():
        errors.append("missing_current_prompt_manifest")
    if prompt_path.exists() and len(prompts) < 2:
        errors.append("prompt_manifest_requires_at_least_two_prompts")

    # The rev0125 regression was here: the run wrapper exported PROMPT_MANIFEST
    # to a non-existent .jsonl path, which poisoned the one-shot wrapper even
    # though the one-shot default itself was correct.
    for label, src in [("run", run_src), ("one_shot", one_src)]:
        if f'PROMPT_MANIFEST:-{expected_default}' not in src and f'PROMPT_MANIFEST:-{literal_default}' not in src:
            errors.append(f"{label}_wrapper_prompt_manifest_default_not_current_txt")
        if "PUBLIC_TRACE_PROMPTS.jsonl" in src:
            errors.append(f"{label}_wrapper_still_defaults_to_missing_jsonl_prompt_manifest")

    if '--prompts-file "$PROMPT_MANIFEST"' not in one_src:
        errors.append("one_shot_does_not_pass_PROMPT_MANIFEST_to_capture")
    if inline_prompt_args:
        errors.append("live_wrappers_still_contain_inline_prompt_args")
    if '[[ ! -f "$PROMPT_MANIFEST" ]]' not in one_src and 'PROMPT_MANIFEST does not exist' not in one_src:
        errors.append("one_shot_does_not_fail_fast_on_missing_prompt_manifest")
    if "public_trace_live_prompt_manifest_audit.py" not in run_src:
        errors.append("run_wrapper_does_not_audit_live_prompt_manifest_before_readiness")

    run_prompt_count: Any = None
    run_prompt_manifest_file: Any = None
    if run_packet.exists():
        try:
            packet = json.loads(run_packet.read_text(encoding="utf-8"))
            determinism = packet.get("determinism_contract", {}) if isinstance(packet, dict) else {}
            run_prompt_count = determinism.get("prompt_count")
            run_prompt_manifest_file = determinism.get("prompt_manifest_live_file")
            if run_prompt_count is not None and int(run_prompt_count) != len(prompts):
                errors.append(f"run_packet_prompt_count_{run_prompt_count}_does_not_match_manifest_{len(prompts)}")
            if run_prompt_manifest_file not in {PROMPT_REL, literal_default}:
                errors.append("run_packet_prompt_manifest_live_file_not_current_txt")
        except Exception as exc:
            errors.append("run_packet_prompt_count_unreadable:" + type(exc).__name__)
    else:
        warnings.append("run_packet_missing_when_prompt_manifest_audit_ran")

    status = "pass" if not errors else "fail"
    audit = {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Static audit that the stable/current public-trace wrappers agree on one checked prompt manifest file and that the live capture consumes it instead of hidden inline shell prompt literals.",
        "stable_run_wrapper": STABLE_RUN_REL,
        "run_wrapper": RUN_REL,
        "one_shot_wrapper": ONE_SHOT_REL,
        "prompt_manifest": PROMPT_REL,
        "expected_prompt_manifest_default": expected_default,
        "prompt_count": len(prompts),
        "run_packet_prompt_count": run_prompt_count,
        "run_packet_prompt_manifest_live_file": run_prompt_manifest_file,
        "inline_prompt_arg_count": len(inline_prompt_args),
        "prompts_sha256_inputs_visible": True,
        "errors": errors,
        "warnings": warnings,
        "decision": "stable_run_and_one_shot_prompt_manifest_bound_to_capture" if not errors else "repair_live_prompt_manifest_before_capture",
        "why_it_matters": "A correct one-shot default is insufficient if the parent run wrapper exports PROMPT_MANIFEST to a missing path. The prompt manifest must be a single visible file consumed by the live capture command, or the real trace can fail after all earlier gates pass.",
        "regression_closed": "rev0125_run_wrapper_jsonl_default_would_fail_one_shot_after_readiness",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_LIVE_PROMPT_MANIFEST_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace live prompt manifest audit — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        f"Prompt manifest: `{PROMPT_REL}`  ",
        f"Prompt count: `{len(prompts)}`",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Interpretation", "", audit["why_it_matters"]])
    (OUT / f"{REVUP}_PUBLIC_TRACE_LIVE_PROMPT_MANIFEST_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
