#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

COMMON_ENV = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"
ACTIVE_SHELLS = [
    COMMON_ENV,
    ROOT / "artifacts" / "capture-kit" / f"{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
    ROOT / "artifacts" / "capture-kit" / f"{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
    ROOT / "artifacts" / "capture-kit" / f"{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
    ROOT / "artifacts" / "capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
    ROOT / "artifacts" / "capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
]
BOOT_ENV = ROOT / "artifacts" / "runtime" / "CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh"
RUN_PACKET = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json"
SOURCE_LOCK = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TINYLLAMA_SOURCE_LOCK.json"
DEFAULT_REL = "artifacts/runtime/public-trace-hf-cache"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def shell_report(path: Path) -> dict[str, Any]:
    src = read(path)
    common_src = read(COMMON_ENV)
    sources_common_env = "${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh" in src or f"{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh" in src
    effective_src = src + ("\n" + common_src if sources_common_env and path != COMMON_ENV else "")
    markers = [
        "PUBLIC_TRACE_CACHE_ROOT",
        DEFAULT_REL,
        "HF_HOME",
        "HF_HUB_CACHE",
        "HF_XET_CACHE",
        "HF_ASSETS_CACHE",
        "mkdir -p \"$HF_HOME\" \"$HF_HUB_CACHE\" \"$HF_XET_CACHE\" \"$HF_ASSETS_CACHE\"",
    ]
    missing = [m for m in markers if m not in effective_src]
    return {
        "path": rel(path),
        "exists": path.exists(),
        "cache_contract_markers_present": not missing,
        "sources_common_env": sources_common_env,
        "missing_markers": missing,
    }


def json_contract(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "exists": False, "has_cache_contract": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": rel(path), "exists": True, "parse_error": type(exc).__name__ + ": " + repr(exc), "has_cache_contract": False}
    text = json.dumps(data, sort_keys=True)
    return {
        "path": rel(path),
        "exists": True,
        "has_cache_contract": "project_local_hf_cache_root_v1" in text,
        "mentions_default_cache_root": DEFAULT_REL in text,
    }


def env_snapshot() -> dict[str, Any]:
    keys = ["PUBLIC_TRACE_CACHE_ROOT", "HF_HOME", "HF_HUB_CACHE", "HF_XET_CACHE", "HF_ASSETS_CACHE"]
    return {k: os.environ.get(k) for k in keys if os.environ.get(k) is not None}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    reports = [shell_report(p) for p in ACTIVE_SHELLS]
    for rep in reports:
        if not rep["exists"]:
            errors.append("missing_active_cache_contract_shell:" + rep["path"])
        for marker in rep["missing_markers"]:
            errors.append(f"{rep['path']} missing cache-root marker: {marker}")
    boot_src = read(BOOT_ENV)
    boot_env_markers = ["PUBLIC_TRACE_CACHE_ROOT", "HF_HOME", "HF_HUB_CACHE", "HF_XET_CACHE", "HF_ASSETS_CACHE"]
    boot_env_missing = []
    if BOOT_ENV.exists():
        boot_env_missing = [m for m in boot_env_markers if m not in boot_src]
        for marker in boot_env_missing:
            errors.append(f"{rel(BOOT_ENV)} missing persisted cache env marker: {marker}")
    else:
        warnings.append("bootstrap_env_not_yet_generated_here")
    run_packet_contract = json_contract(RUN_PACKET)
    source_lock_contract = json_contract(SOURCE_LOCK)
    for item in [run_packet_contract, source_lock_contract]:
        if item.get("exists") and not item.get("has_cache_contract"):
            errors.append(f"{item['path']} missing project_local_hf_cache_root_v1 contract")
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Verifies that the active first-trace, snapshot, bootstrap, and capture surfaces default Hugging Face/Transformers/Xet caches to a project-local root instead of silently relying on user-global ~/.cache state. Operators can still override PUBLIC_TRACE_CACHE_ROOT or individual HF_* variables, but the default path is trace-bound and easier to delete or move.",
        "cache_root_contract": "project_local_hf_cache_root_v1",
        "default_public_trace_cache_root": DEFAULT_REL,
        "environment_when_audit_ran": env_snapshot(),
        "common_env": rel(COMMON_ENV),
        "active_shell_reports": reports,
        "bootstrap_env_file": rel(BOOT_ENV),
        "bootstrap_env_present": BOOT_ENV.exists(),
        "bootstrap_env_missing_markers": boot_env_missing,
        "run_packet_contract": run_packet_contract,
        "source_lock_contract": source_lock_contract,
        "online_basis": [
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables",
                "fact": "huggingface_hub reads environment variables at import time and defines HF_HOME, HF_HUB_CACHE, HF_XET_CACHE, and timeout controls; therefore runner scripts must export cache paths before importing Hugging Face libraries.",
                "observed_lines_from_web_run": "turn193120view0 lines 81-110 and 132-147",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/installation",
                "fact": "Transformers caches Hub models under HF_HUB_CACHE/HF_HOME and offline use requires the files to be downloaded/cached ahead of time; capture should therefore bind to an explicit cache/snapshot location.",
                "observed_lines_from_web_run": "turn193120view2 lines 198-229",
            },
            {
                "url": "https://huggingface.co/docs/hub/en/xet/index",
                "fact": "Hugging Face Hub stores large model files via pointer-backed large-file storage, making Xet cache placement part of the first-trace disk and cleanup contract.",
                "observed_lines_from_web_run": "turn193120view3 lines 100-109",
            },
        ],
        "risks_reduced": [
            "global_hf_cache_pollution_or_hidden_success",
            "runner_reproduction_depending_on_untracked_user_home_state",
            "xet_chunk_cache_written_outside_trace_bound_directory",
            "future_package_or_cleanup_confusion_after_large_snapshot_materialization",
        ],
        "errors": errors,
        "warnings": warnings,
        "decision": "cache_root_contract_ready" if not errors else "repair_cache_root_contract_before_first_trace_attempt",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_ROOT_CONTRACT_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace cache-root contract audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        f"Default cache root: `{DEFAULT_REL}`",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    md.extend(["", "## Interpretation", "", "This is not a new registry layer. It removes a concrete completion risk: a successful first trace should not secretly depend on whichever Hugging Face cache happened to exist in a user home directory, and a failed/materialized run should be easy to clean without guessing where 2GB+ of model/Xet chunks went."])
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_ROOT_CONTRACT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
