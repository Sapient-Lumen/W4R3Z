#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
COMMON = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"
BOOT = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh"


def run_shell(src: str, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    proc = subprocess.run(["bash", "-lc", src], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=merged, timeout=30)
    return {"returncode": proc.returncode, "stdout_tail": proc.stdout[-1600:], "stderr_tail": proc.stderr[-1600:]}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    common_src = COMMON.read_text(encoding="utf-8", errors="replace") if COMMON.exists() else ""
    boot_src = BOOT.read_text(encoding="utf-8", errors="replace") if BOOT.exists() else ""
    for marker in ["HF_HUB_DISABLE_SYMLINKS", "PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION", "can duplicate large Hub files"]:
        if marker not in common_src:
            errors.append("common_env_missing_cache_duplication_guard_marker:" + marker)
    for marker in ["PUBLIC_TRACE_BOOTSTRAP_DRY_RUN", "PUBLIC_TRACE_WHEELHOUSE", "--no-index", "PIP_FIND_LINKS", "PUBLIC_TRACE_SKIP_PIP_UPGRADE"]:
        if marker not in boot_src:
            errors.append("bootstrap_missing_runtime_install_marker:" + marker)
    default_probe = run_shell(f'ROOT="$PWD" REVUP="{REVUP}" PUBLIC_TRACE_COMMON_ENV_MODE=base source "artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"')
    if default_probe["returncode"] != 0:
        errors.append("common_env_default_source_failed:" + default_probe["stderr_tail"])
    blocked_probe = run_shell(f'ROOT="$PWD" REVUP="{REVUP}" PUBLIC_TRACE_COMMON_ENV_MODE=base source "artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"', {"HF_HUB_DISABLE_SYMLINKS": "1", "PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION": "0"})
    if blocked_probe["returncode"] == 0:
        errors.append("hf_hub_disable_symlinks_not_blocked_without_explicit_override")
    if "can duplicate large Hub files" not in (blocked_probe["stderr_tail"] + blocked_probe["stdout_tail"]):
        errors.append("cache_duplication_blocker_message_missing")
    allowed_probe = run_shell(f'ROOT="$PWD" REVUP="{REVUP}" PUBLIC_TRACE_COMMON_ENV_MODE=base source "artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh"', {"HF_HUB_DISABLE_SYMLINKS": "1", "PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION": "1"})
    if allowed_probe["returncode"] != 0:
        errors.append("explicit_cache_duplication_override_failed:" + allowed_probe["stderr_tail"])
    dry_probe = run_shell(f'PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh')
    if dry_probe["returncode"] != 0:
        errors.append("bootstrap_dry_run_script_failed:" + dry_probe["stderr_tail"])
    if "bootstrap dry run ok" not in dry_probe["stdout_tail"]:
        errors.append("bootstrap_dry_run_did_not_report_ok")
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Guards two high-risk/wasteful operational edges before the first real TinyLlama trace: bootstrap dry-run must be safe/no-pip, and HF_HUB_DISABLE_SYMLINKS must not silently duplicate large Hub snapshot files unless the operator explicitly opts in.",
        "common_env_script": COMMON.relative_to(ROOT).as_posix(),
        "bootstrap_script": BOOT.relative_to(ROOT).as_posix(),
        "default_source_probe": default_probe,
        "symlink_duplication_blocked_probe": blocked_probe,
        "symlink_duplication_allowed_probe": allowed_probe,
        "bootstrap_dry_run_probe": dry_probe,
        "online_basis": [
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables",
                "fact": "The Hub docs state environment variables are read at import time and document HF_HUB_DISABLE_SYMLINKS as causing huge files to be duplicated or moved into snapshot directories.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/installation",
                "fact": "Transformers offline mode requires downloaded/cached files ahead of time, so cache layout and no-network capture behavior must be settled before import/capture.",
            },
        ],
        "errors": errors,
        "warnings": warnings,
        "decision": "dryrun_and_cache_duplication_guard_ready" if not errors else "repair_bootstrap_or_cache_duplication_guard_before_external_first_trace",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_DUPLICATION_GUARD_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace cache duplication guard audit — {REVUP}",
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
    (OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_DUPLICATION_GUARD_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
