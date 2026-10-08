#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(REV.replace("rev", ""))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

CAPTURE_HELPER = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
RUN_WRAPPER = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"
ONE_SHOT = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"
FIRST_REAL = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh"
COMMON_ENV = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"
PREFLIGHT = ROOT / "tools" / "public_trace_capture_start_preflight_report.py"

REQUIRED_ENV = [
    "HF_HUB_OFFLINE=1",
    "TRANSFORMERS_OFFLINE=1",
    "HF_HUB_DISABLE_TELEMETRY=1",
    "HF_HUB_DISABLE_IMPLICIT_TOKEN=1",
    "HF_HUB_DISABLE_UPDATE_CHECK=1",
]
CONTRACT = "hf_transformers_offline_env_before_runtime_import_v1"

RESEARCH_BASIS = [
    {
        "url": "https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables",
        "observed_web_run": "turn240500view4 lines 87-88; turn895090view1 lines 169-178 and 196-206",
        "fact": "huggingface_hub reads environment variables at import time; HF_HUB_OFFLINE prevents HTTP calls and skips the usual cache freshness request; HF_HUB_DISABLE_IMPLICIT_TOKEN and telemetry/update controls are relevant privacy/no-network guards.",
    },
    {
        "url": "https://huggingface.co/docs/transformers/en/installation",
        "observed_web_run": "turn895090view3 lines 210-233",
        "fact": "Transformers offline use requires downloaded/cached files ahead of time and can use HF_HUB_OFFLINE plus local_files_only=True from a local directory.",
    },
    {
        "url": "https://huggingface.co/docs/transformers/en/main_classes/model",
        "observed_web_run": "turn895090view2 lines 236-263",
        "fact": "from_pretrained accepts local directory paths, local_files_only, and immutable revisions; public capture should bind to the digest-verified local path after snapshot preparation.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/package_reference/file_download",
        "observed_web_run": "turn240500view3 lines 220-235 and 265-272",
        "fact": "snapshot_download returns a local snapshot path and can raise IncompleteSnapshotError when cached requested files are missing; metadata exposes file size/xet details for materialization but capture should not perform that network step.",
    },
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has_all_env(text: str) -> bool:
    return all(item in text for item in REQUIRED_ENV)

def sources_common_env(text: str) -> bool:
    return "${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh" in text or f"{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh" in text

def effective_shell_text(text: str) -> str:
    common = read(COMMON_ENV)
    return text + ("\n" + common if sources_common_env(text) else "")


def order_ok(text: str, first: str, second: str) -> bool:
    a = text.find(first)
    b = text.find(second)
    return a >= 0 and b >= 0 and a < b


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    helper = read(CAPTURE_HELPER)
    run = read(RUN_WRAPPER)
    one = read(ONE_SHOT)
    first = read(FIRST_REAL)
    common = read(COMMON_ENV)
    run_eff = effective_shell_text(run)
    one_eff = effective_shell_text(one)
    first_eff = effective_shell_text(first)
    preflight = read(PREFLIGHT)

    if "import os" not in helper:
        errors.append("capture_helper_missing_os_import_for_env_quarantine")
    if "def _enforce_capture_network_quarantine" not in helper:
        errors.append("capture_helper_missing_offline_quarantine_function")
    if CONTRACT not in helper:
        errors.append("capture_helper_missing_offline_quarantine_contract")
    if not order_ok(helper, "capture_network_quarantine = _enforce_capture_network_quarantine", "torch, transformers, AutoModelForCausalLM, AutoTokenizer = _import_runtime()"):
        errors.append("capture_helper_does_not_set_offline_quarantine_before_runtime_import")
    if "local_files_only=local_only" not in helper:
        errors.append("capture_helper_does_not_pass_local_files_only_to_from_pretrained")
    if "args.public_pretrained_trace and not capture_network_quarantine.get(\"set_before_runtime_import\")" not in helper:
        errors.append("public_capture_does_not_fail_if_quarantine_is_after_import")
    if "capture_offline_quarantine_contract" not in helper:
        errors.append("capture_helper_provenance_does_not_record_quarantine_contract")

    for label, text, eff in [("run_wrapper", run, run_eff), ("one_shot", one, one_eff)]:
        if not sources_common_env(text):
            errors.append(f"{label}_does_not_source_common_env")
        if not has_all_env(eff):
            errors.append(f"{label}_missing_required_offline_env_exports")
        if "export ALLOW_DOWNLOAD=0" not in eff:
            errors.append(f"{label}_does_not_force_allow_download_zero")
        if "--allow-download" in text:
            errors.append(f"{label}_passes_allow_download_to_capture_helper")
        if CONTRACT not in eff:
            errors.append(f"{label}_missing_quarantine_contract_marker")

    if not sources_common_env(first):
        errors.append("first_real_trace_runner_does_not_source_common_env")
    if not has_all_env(first_eff):
        errors.append("first_real_trace_runner_capture_phase_missing_inline_offline_env")
    if "ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1" not in first:
        errors.append("first_real_trace_runner_does_not_force_local_only_capture_phase")
    if CONTRACT not in preflight:
        errors.append("capture_start_preflight_env_does_not_export_quarantine_contract")
    if not has_all_env(preflight):
        errors.append("capture_start_preflight_env_missing_offline_exports")

    prepare = read(ROOT / "artifacts" / "capture-kit" / f"{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh")
    if "HF_HUB_OFFLINE=1" in prepare:
        warnings.append("prepare_snapshot_sets_hf_hub_offline_even_though_it_is_the_allowed_download_phase")

    status = "pass" if not errors else "fail"
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Verifies that the evidence-capture phase is network-quarantined after snapshot preparation: wrappers force ALLOW_DOWNLOAD=0, set Hugging Face/Transformers offline/privacy env controls, and the Python capture helper applies the controls before importing HF runtime while still using local_files_only=True.",
        "contract": CONTRACT,
        "required_env": REQUIRED_ENV,
        "checked_files": {
            "capture_helper": str(CAPTURE_HELPER.relative_to(ROOT)),
            "run_wrapper": str(RUN_WRAPPER.relative_to(ROOT)),
            "one_shot": str(ONE_SHOT.relative_to(ROOT)),
            "first_real": str(FIRST_REAL.relative_to(ROOT)),
            "common_env": str(COMMON_ENV.relative_to(ROOT)),
            "capture_start_preflight": str(PREFLIGHT.relative_to(ROOT)),
        },
        "research_basis": RESEARCH_BASIS,
        "common_env_sourced_by_wrappers": {"run_wrapper": sources_common_env(run), "one_shot": sources_common_env(one), "first_real": sources_common_env(first)},
        "errors": errors,
        "warnings": warnings,
        "decision": "offline_quarantined_capture_surface_ok" if not errors else "repair_capture_network_quarantine_before_first_real_trace",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_OFFLINE_QUARANTINE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace offline quarantine audit — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Why this is the priority",
        "",
        "The first real trace needs one allowed network phase to materialize the reviewed snapshot, then a strict evidence phase that cannot silently reach the Hub, use an implicit token, or resolve a different cache object. This hardens that boundary without adding a new registry layer.",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    md.extend(["", "## Research basis", ""])
    for item in RESEARCH_BASIS:
        md.append(f"- {item['fact']} Source: {item['url']}")
    (OUT / f"{REVUP}_PUBLIC_TRACE_OFFLINE_QUARANTINE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
