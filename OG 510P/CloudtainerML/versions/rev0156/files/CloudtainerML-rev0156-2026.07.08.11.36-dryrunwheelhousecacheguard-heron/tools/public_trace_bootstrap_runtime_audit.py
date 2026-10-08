#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
REQ = ROOT / "artifacts" / "runtime" / f"{REVUP}_public_trace_requirements.txt"
BOOT = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh"
FIRST = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh"
BOOT_ENV = ROOT / "artifacts" / "runtime" / "CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh"
EXT_BUILDER = ROOT / "tools" / "public_trace_external_runner_packet_builder.py"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def req_names(src: str) -> set[str]:
    names: set[str] = set()
    for line in src.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name = re.split(r"[<>=!~\[;\s]", line, maxsplit=1)[0].strip().replace("-", "_")
        if name:
            names.add(name)
    return names


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    req_src = text(REQ)
    boot_src = text(BOOT)
    first_src = text(FIRST)
    builder_src = text(EXT_BUILDER)
    reqs = req_names(req_src)
    for rel, path in [("requirements", REQ), ("bootstrap", BOOT), ("first_trace", FIRST)]:
        if not path.exists():
            errors.append(f"missing_{rel}_file:{path.relative_to(ROOT).as_posix()}")
    for needed in ["torch", "transformers", "huggingface_hub", "safetensors", "numpy", "hf_xet"]:
        if needed not in reqs:
            errors.append(f"requirements_missing:{needed}")
    if "python3 -m pip install -r" in boot_src and ".venv" not in boot_src:
        errors.append("bootstrap_installs_into_ambient_python_instead_of_project_venv")
    for marker in ["-m venv", "CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh", "PUBLIC_TRACE_VENV_DIR", "PYTHONNOUSERSITE", "HF_HUB_DOWNLOAD_TIMEOUT", "HF_HUB_ETAG_TIMEOUT", "PUBLIC_TRACE_CACHE_ROOT", "HF_HOME", "HF_HUB_CACHE", "HF_XET_CACHE", "HF_ASSETS_CACHE", "PUBLIC_TRACE_BOOTSTRAP_DRY_RUN", "PUBLIC_TRACE_WHEELHOUSE", "PIP_FIND_LINKS", "--no-index", "PUBLIC_TRACE_SKIP_PIP_UPGRADE", "public_trace_runtime_import_smoke.py --strict --require-project-venv", '"$VENV_PY" tools/public_trace_runtime_import_smoke.py']:
        if marker not in boot_src:
            errors.append("bootstrap_missing_marker:" + marker)
    for marker in ["source \"$BOOTSTRAP_ENV\"", "BOOTSTRAP_RUNTIME", "public_trace_bootstrap_runtime_audit.py", "runtime_import_smoke", "public_trace_runtime_import_smoke.py"]:
        if marker not in first_src:
            errors.append("first_trace_runner_missing_marker:" + marker)
    if "python3 -m pip install -r artifacts/runtime" in builder_src:
        errors.append("external_runner_builder_still_writes_system_python_bootstrap")
    if "BOOTSTRAP_PUBLIC_TRACE_ENV.sh" not in builder_src:
        warnings.append("external_runner_builder_bootstrap_target_not_obvious")
    boot_env_present = BOOT_ENV.exists()
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Checks that one-command public-trace runtime bootstrap uses a project-local virtualenv whose PATH persists into snapshot and capture phases, that the actual venv Python runs an import/surface smoke before snapshot materialization, and that the active requirements include hf_xet plus slow-link Hugging Face timeout defaults for modern large-file downloads.",
        "requirements_file": REQ.relative_to(ROOT).as_posix(),
        "requirements_seen": sorted(reqs),
        "bootstrap_script": BOOT.relative_to(ROOT).as_posix(),
        "first_trace_runner": FIRST.relative_to(ROOT).as_posix(),
        "bootstrap_env_file": BOOT_ENV.relative_to(ROOT).as_posix(),
        "bootstrap_env_present": boot_env_present,
        "project_venv_contract": "public_trace_project_local_venv_v1",
        "xet_requirement_contract": "hf_hub_xet_large_file_download_v1",
        "download_timeout_contract": "hf_public_snapshot_slow_link_timeout_defaults_v1",
        "runtime_import_smoke_contract": "project_venv_capture_stack_import_surface_smoke_v1",
        "wheelhouse_bootstrap_contract": "optional_public_trace_wheelhouse_no_index_bootstrap_v1",
        "bootstrap_dry_run_contract": "no_pip_no_network_bootstrap_path_probe_v1",
        "runtime_import_smoke_tool": "tools/public_trace_runtime_import_smoke.py",
        "cache_root_contract": "project_local_hf_cache_root_v1",
        "default_public_trace_cache_root": "artifacts/runtime/public-trace-hf-cache",
        "online_basis": [
            {
                "url": "https://peps.python.org/pep-0668/",
                "fact": "PEP 668 says tools should not install into externally managed global Python contexts by default and should guide users toward virtual environments."
            },
            {
                "url": "https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/",
                "fact": "Python packaging docs recommend venv for third-party packages and show project-local .venv usage."
            },
            {
                "url": "https://huggingface.co/docs/hub/en/xet/using-xet-storage",
                "fact": "Hugging Face Xet docs state huggingface_hub >= 0.32 installs hf_xet, while hub 0.30-0.32 needs explicit hf-xet installation."
            },
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
                "fact": "Hugging Face Hub download docs describe hf_xet as an integrated faster download path for Xet-backed large files."
            }
        ],
        "errors": errors,
        "warnings": warnings,
        "decision": "bootstrap_runtime_surface_ok" if not errors else "repair_bootstrap_or_runtime_smoke_before_external_first_trace_attempt",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_BOOTSTRAP_RUNTIME_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace bootstrap runtime audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## What this prevents",
        "",
        "- One-command runner bootstrap disappearing in a child shell before snapshot/capture phases.",
        "- Pip writing into a system/externally-managed Python instead of a project-local environment.",
        "- Large Hugging Face/Xet-backed model download taking the slow/broken path because `hf_xet` is absent or the default Hub download timeout is too short for a 2.2GB file.",
        "- Wasting a snapshot-download/materialization attempt before proving the project-local venv can import the capture stack and Llama eager-attention hook surface.",
        "- Silently writing or reading large Hugging Face/Xet cache material from user-global home state instead of the trace-bound cache root.",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_BOOTSTRAP_RUNTIME_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
