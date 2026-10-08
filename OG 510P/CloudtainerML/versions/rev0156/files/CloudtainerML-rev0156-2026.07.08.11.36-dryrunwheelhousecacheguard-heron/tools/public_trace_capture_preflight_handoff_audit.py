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

RUN = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"
ONE = ROOT / "artifacts" / "capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"
STABLE = ROOT / "artifacts" / "capture-kit" / "RUN_CURRENT_PUBLIC_TRACE.sh"
CONTRACT = "capture_start_preflight_done_selected_snapshot_v1"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def main() -> int:
    run = read(RUN)
    one = read(ONE)
    stable = read(STABLE)
    errors: list[str] = []
    warnings: list[str] = []
    required_run_markers = [
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1",
        f"PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT=\"{CONTRACT}\"",
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV=\"$CAPTURE_ENV\"",
        "tools/public_trace_capture_preflight_handoff_audit.py",
        "exec bash \"$HERE/${REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh\"",
    ]
    for marker in required_run_markers:
        if marker not in run:
            errors.append("run_wrapper_missing_marker:" + marker)
    required_one_markers = [
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE:-0",
        CONTRACT,
        "Direct one-shot execution path",
        "source \"$CAPTURE_ENV\"",
        "tools/public_trace_capture_preflight_handoff_audit.py",
        "tools/current_live_script_dependency_audit.py",
        "public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only",
    ]
    for marker in required_one_markers:
        if marker not in one:
            errors.append("one_shot_missing_marker:" + marker)
    if f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in stable:
        errors.append("stable_alias_not_current_run_wrapper")
    if run.find("PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1") < run.find("python3 tools/public_trace_handoff_builder_audit.py"):
        errors.append("handoff_flag_set_before_front_gate_audits_complete")
    if one.count("public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only") != 1:
        errors.append("one_shot_should_keep_exactly_one_direct_fallback_capture_start_preflight")
    if run.count("public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only") != 1:
        errors.append("run_wrapper_should_keep_exactly_one_capture_start_preflight")
    runtime_env = {
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE": os.environ.get("PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE"),
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT": os.environ.get("PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT"),
        "PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV": os.environ.get("PUBLIC_TRACE_CAPTURE_PREFLIGHT_ENV"),
        "LOCAL_SNAPSHOT_DIR_present": bool(os.environ.get("LOCAL_SNAPSHOT_DIR")),
    }
    if runtime_env["PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE"] == "1" and runtime_env["PUBLIC_TRACE_CAPTURE_PREFLIGHT_CONTRACT"] != CONTRACT:
        errors.append("runtime_handoff_flag_contract_mismatch")
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Prevents the active public-trace wrapper from paying the same import-light capture-start and static handoff gates twice. The stable wrapper now hands an explicit done/contract/env flag into the one-shot; the one-shot still preserves its full direct fallback path for forensic replay.",
        "risk_closed": "duplicated live-run preflight stack could waste operator time and obscure the first true runtime/snapshot blocker",
        "contract": CONTRACT,
        "checked_files": [
            RUN.relative_to(ROOT).as_posix(),
            ONE.relative_to(ROOT).as_posix(),
            STABLE.relative_to(ROOT).as_posix(),
        ],
        "runtime_env_seen": runtime_env,
        "errors": errors,
        "warnings": warnings,
        "decision": "preflight_handoff_refactor_ok" if not errors else "repair_preflight_handoff_before_capture",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_CAPTURE_PREFLIGHT_HANDOFF_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace capture preflight handoff audit — {REVUP}",
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
    md.extend(["", "## Runtime handoff seen", "", "```json", json.dumps(runtime_env, indent=2), "```", ""])
    (OUT / f"{REVUP}_PUBLIC_TRACE_CAPTURE_PREFLIGHT_HANDOFF_AUDIT.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
