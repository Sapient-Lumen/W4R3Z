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
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
COMMON = Path(f"artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh")
ACTIVE = [
    Path(f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh"),
    Path(f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh"),
    Path(f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"),
    Path(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"),
    Path(f"artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh"),
]


def read(rel: Path) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    common_text = read(COMMON)
    if not (ROOT / COMMON).is_file():
        errors.append("missing_common_public_trace_env_script:" + COMMON.as_posix())
    required_common_markers = [
        "PUBLIC_TRACE_COMMON_ENV_MODE",
        "HF_HOME=",
        "HF_HUB_CACHE=",
        "HF_XET_CACHE=",
        "HF_ASSETS_CACHE=",
        "HF_HUB_OFFLINE=1",
        "TRANSFORMERS_OFFLINE=1",
        "PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt",
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "HF_HUB_DOWNLOAD_TIMEOUT",
        "HF_HUB_ETAG_TIMEOUT",
        "HF_HUB_DISABLE_SYMLINKS",
        "PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION",
        "can duplicate large Hub files",
    ]
    for marker in required_common_markers:
        if marker not in common_text:
            errors.append("common_env_missing_marker:" + marker)
    reports: list[dict[str, Any]] = []
    for rel in ACTIVE:
        text = read(rel)
        sources_common = '${REVUP}_COMMON_PUBLIC_TRACE_ENV.sh' in text and 'source "$HERE/' in text
        mode = None
        m = re.search(r'PUBLIC_TRACE_COMMON_ENV_MODE="([a-z_]+)"', text)
        if m:
            mode = m.group(1)
        reports.append({"script": rel.as_posix(), "exists": (ROOT / rel).is_file(), "sources_common_env": sources_common, "mode": mode})
        if not (ROOT / rel).is_file():
            errors.append("missing_active_common_env_consumer:" + rel.as_posix())
        if not sources_common:
            errors.append("active_script_does_not_source_common_env:" + rel.as_posix())
    for rel in [Path(f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"), Path(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh")]:
        text = read(rel)
        if 'PUBLIC_TRACE_COMMON_ENV_MODE="capture"' not in text:
            errors.append("capture_script_not_in_capture_common_env_mode:" + rel.as_posix())
    all_active_text = "\n".join(read(rel) for rel in ACTIVE)
    duplicate_sensitive_exports = [
        'export HF_HOME="${HF_HOME:-$PUBLIC_TRACE_CACHE_ROOT/hf-home}"',
        'export MODEL_ID="${MODEL_ID:-TinyLlama/TinyLlama-1.1B-Chat-v1.0}"',
        'export PROMPT_MANIFEST="${PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt}"',
        'export TRANSFORMERS_OFFLINE=1',
    ]
    for marker in duplicate_sensitive_exports:
        if marker in all_active_text:
            errors.append("duplicated_common_env_export_outside_common_script:" + marker)
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Ensures active public-trace wrappers source one common Hugging Face/model/offline environment contract before Python runtime imports, instead of drifting through copy-pasted cache and offline exports; also blocks accidental no-symlink cache duplication for large Hub snapshots unless explicitly approved.",
        "common_env_script": COMMON.as_posix(),
        "consumer_reports": reports,
        "errors": errors,
        "warnings": warnings,
        "decision": "common_public_trace_env_contract_ok" if not errors else "repair_common_public_trace_env_before_capture",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_COMMON_ENV_CONTRACT_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace common-env contract audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Consumer scripts",
        "",
    ]
    md.extend(f"- `{r['script']}` mode=`{r['mode']}` sources_common=`{r['sources_common_env']}`" for r in reports)
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_COMMON_ENV_CONTRACT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
