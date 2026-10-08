#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CONTRACT = "hf_snapshot_download_dry_run_byte_budget_v1"


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def pos(text: str, needle: str) -> int:
    return text.find(needle)


def load_json(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    tool_rel = "tools/public_trace_snapshot_download_plan.py"
    tool = ROOT / tool_rel
    if not tool.exists():
        errors.append("missing_snapshot_download_plan_tool")
    else:
        text = tool.read_text(encoding="utf-8", errors="replace")
        for marker in ["snapshot_download", "dry_run=True", "bytes_to_download", "cache_filesystem_free_bytes", CONTRACT]:
            if marker not in text:
                errors.append("download_plan_tool_missing_marker:" + marker)

    prepare_rel = f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh"
    first_rel = f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh"
    builder_rel = "tools/public_trace_external_runner_packet_builder.py"
    prepare = read(prepare_rel)
    first = read(first_rel)
    builder = read(builder_rel)
    if not prepare:
        errors.append("missing_current_snapshot_prepare_script")
    else:
        plan_pos = pos(prepare, "tools/public_trace_snapshot_download_plan.py")
        materializer_pos = pos(prepare, "tools/hf_snapshot_materializer.py --download")
        if plan_pos < 0:
            errors.append("snapshot_prepare_missing_download_plan_call")
        if materializer_pos < 0:
            errors.append("snapshot_prepare_missing_download_materializer_call")
        if plan_pos >= 0 and materializer_pos >= 0 and plan_pos > materializer_pos:
            errors.append("snapshot_prepare_runs_download_plan_after_materializer")
        if "PUBLIC_TRACE_SKIP_DOWNLOAD_PLAN" not in prepare:
            errors.append("snapshot_prepare_missing_explicit_download_plan_skip_escape_hatch")
        if "--strict" not in prepare[plan_pos:plan_pos + 200] if plan_pos >= 0 else True:
            errors.append("snapshot_prepare_download_plan_not_strict")
    if not first:
        errors.append("missing_current_first_real_trace_script")
    elif "tools/public_trace_snapshot_download_plan_gate_audit.py" not in first:
        errors.append("first_real_trace_missing_static_download_plan_gate_audit")
    if "tools/public_trace_snapshot_download_plan_gate_audit.py" not in prepare:
        errors.append("snapshot_prepare_missing_static_download_plan_gate_audit")
    if "tools/public_trace_snapshot_download_plan.py" not in builder or "tools/public_trace_snapshot_download_plan_gate_audit.py" not in builder:
        errors.append("external_runner_builder_does_not_require_download_plan_tools")
    if "snapshot_download_plan" not in builder:
        warnings.append("external_runner_builder_summary_does_not_mention_download_plan")

    req = read(f"artifacts/runtime/{REVUP}_public_trace_requirements.txt")
    if "huggingface_hub" not in req and "huggingface-hub" not in req:
        errors.append("runtime_requirements_missing_huggingface_hub_for_dry_run")
    if "hf_xet" not in req and "hf-xet" not in req:
        errors.append("runtime_requirements_missing_hf_xet_for_large_snapshot_path")

    packet = load_json(f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json")
    det = packet.get("determinism_contract", {}) if isinstance(packet.get("determinism_contract"), dict) else {}
    if det.get("snapshot_download_plan_gate_required_before_materialization") is not True:
        errors.append("run_packet_missing_download_plan_gate_marker")
    if det.get("snapshot_download_plan_contract") != CONTRACT:
        errors.append("run_packet_missing_download_plan_contract")

    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Static audit that the first-real-trace snapshot preparation path performs a strict Hugging Face dry-run/byte-budget plan before any large snapshot materialization.",
        "contract": CONTRACT,
        "checked": {
            "tool": tool_rel,
            "snapshot_prepare_script": prepare_rel,
            "first_real_trace_script": first_rel,
            "external_runner_builder": builder_rel,
            "requirements": f"artifacts/runtime/{REVUP}_public_trace_requirements.txt",
            "run_packet": f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json",
        },
        "errors": errors,
        "warnings": warnings,
        "decision": "download_plan_gate_wired_before_materialization" if not errors else "repair_download_plan_gate_before_snapshot_attempt",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace snapshot download-plan gate audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
