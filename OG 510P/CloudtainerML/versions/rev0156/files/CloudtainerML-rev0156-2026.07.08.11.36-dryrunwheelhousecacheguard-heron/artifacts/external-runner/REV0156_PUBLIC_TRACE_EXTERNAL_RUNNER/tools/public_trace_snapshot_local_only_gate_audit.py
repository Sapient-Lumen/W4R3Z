#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
FAST = ROOT / "tools" / "public_trace_fast_prereq_gate.py"
PREP = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh"
RUN = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"
SMOKE = ROOT / "tools" / "smoke_validate.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    fast_src = read(FAST)
    prep_src = read(PREP)
    run_src = read(RUN)
    smoke_src = read(SMOKE)

    if not FAST.is_file():
        errors.append("missing_public_trace_fast_prereq_gate")
    if "if download_mode:\n        for name in SNAPSHOT_REQUIRED_MODULES" not in fast_src:
        errors.append("fast_gate_requires_snapshot_modules_outside_download_mode")
    if "_not_importable_for_snapshot_materialization" not in fast_src or "SNAPSHOT_REQUIRED_MODULES" not in fast_src:
        errors.append("fast_gate_missing_download_mode_snapshot_module_blocker")
    if "Local-only snapshot verification is import-light" not in fast_src:
        errors.append("fast_gate_missing_local_only_import_light_comment")
    if "capture_runtime_blockers_deferred_until_after_snapshot_materialization" not in fast_src:
        errors.append("fast_gate_missing_snapshot_phase_deferred_capture_runtime_marker")
    if "public_trace_snapshot_local_only_gate_audit.py" not in prep_src:
        errors.append("snapshot_prepare_wrapper_does_not_run_local_only_gate_audit")
    if "public_trace_snapshot_local_only_gate_audit.py" not in run_src:
        errors.append("run_wrapper_does_not_run_local_only_gate_audit")
    if "snapshot_local_only_gate" not in smoke_src:
        errors.append("smoke_validate_does_not_guard_snapshot_local_only_gate")

    # Guard against the exact regression: a future edit that reintroduces an
    # unconditional loop before download_mode is checked.
    unconditional_fragment = "for name in SNAPSHOT_REQUIRED_MODULES:\n        if not modules[name]['present']:\n            hard_blockers.append(f'{name}_not_importable_for_snapshot_materialization')\n    if download_mode:"
    if unconditional_fragment in fast_src:
        errors.append("fast_gate_has_unconditional_snapshot_module_blocker_before_download_mode")

    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Ensures local-only snapshot verification remains import-light and does not hard-require huggingface_hub unless the operator explicitly asks the snapshot phase to download/materialize from the Hub.",
        "risk_closed": "valid_mounted_snapshot_could_be_blocked_before_verification_when_huggingface_hub_is_absent",
        "fast_prereq_gate": FAST.relative_to(ROOT).as_posix(),
        "snapshot_prepare_wrapper": PREP.relative_to(ROOT).as_posix(),
        "run_wrapper": RUN.relative_to(ROOT).as_posix(),
        "source_basis": [
            {
                "url": "https://huggingface.co/docs/transformers/en/installation",
                "fact": "Offline Transformers use requires downloaded/cached files ahead of time; local_files_only/HF_HUB_OFFLINE are for loading after materialization.",
            },
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
                "fact": "snapshot_download is the Hub-client path for repository materialization, while local verification of existing files can be independent of that client.",
            },
            {
                "url": "https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/main",
                "fact": "The pinned TinyLlama model tree exposes concrete files and sizes that can be checked locally once the snapshot is present.",
            },
        ],
        "errors": errors,
        "warnings": warnings,
        "decision": "local_only_snapshot_gate_is_import_light" if not errors else "repair_snapshot_local_only_gate_before_external_runner_use",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_LOCAL_ONLY_GATE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace snapshot local-only gate audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        "## Risk closed",
        "",
        str(audit["risk_closed"]),
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Interpretation", "", str(audit["summary"])])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_LOCAL_ONLY_GATE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
