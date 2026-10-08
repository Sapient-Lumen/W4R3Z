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
PKG = str(META.get("package_name", ""))
ARCH = str(META.get("archive_name", ""))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
FILES = [
    ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json",
    ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TINYLLAMA_SOURCE_LOCK.json",
]


def get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def check_file(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return {"path": path.relative_to(ROOT).as_posix(), "exists": False, "errors": ["missing_run_manifest_file"], "warnings": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": path.relative_to(ROOT).as_posix(), "exists": True, "errors": ["json_parse_error:" + repr(exc)], "warnings": []}
    expected = {
        "revision": REV,
        "revision_number": REVNO,
        "revision_int": REVNO,
        "current_revision": REV,
        "current_revision_int": REVNO,
        "package_name": PKG,
        "archive_name": ARCH,
    }
    seen: dict[str, Any] = {}
    for key, value in expected.items():
        if key in data:
            seen[key] = data.get(key)
            if data.get(key) != value:
                errors.append(f"field_mismatch:{key}:expected={value}:actual={data.get(key)}")
    if "TINYLLAMA_PUBLIC_TRACE_RUN_PACKET" in path.name:
        for key in [
            "determinism_contract.prompt_manifest_live_file",
            "environment_preflight.expected_readiness_gate_json",
            "determinism_contract.first_real_trace_one_command_runner",
        ]:
            value = get_path(data, key)
            if isinstance(value, str) and "REV0140" in value:
                errors.append(f"stale_rev0140_path:{key}:{value}")
        dc = data.get("determinism_contract", {}) if isinstance(data.get("determinism_contract"), dict) else {}
        for marker in ["bootstrap_runtime_uses_project_venv", "bootstrap_path_persists_to_following_runner_phases", "hf_xet_requirement_for_modern_hub_large_files", "snapshot_digest_receipt_cache_enabled", "capture_preflight_handoff_skips_duplicate_one_shot_audits", "one_shot_direct_fallback_preserved", "preflight_handoff_audit_required"]:
            if dc.get(marker) is not True:
                errors.append("run_packet_missing_true_marker:" + marker)
        if dc.get("snapshot_digest_receipt_cache_contract") != "stat_bound_model_safetensors_sha256_receipt_v1":
            errors.append("run_packet_missing_digest_receipt_cache_contract")
        if dc.get("capture_preflight_handoff_contract") != "capture_start_preflight_done_selected_snapshot_v1":
            errors.append("run_packet_missing_preflight_handoff_contract")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "exists": True,
        "seen_revision_fields": seen,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    reports = [check_file(p) for p in FILES]
    errors = [e for r in reports for e in r.get("errors", [])]
    warnings = [w for r in reports for w in r.get("warnings", [])]
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": PKG,
        "archive_name": ARCH,
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Guards against a subtle but expensive handoff defect: a current external runner can carry stale revision integers, timestamps, or paths in the run packet/source lock even when the shell aliases are current.",
        "reports": reports,
        "errors": errors,
        "warnings": warnings,
        "decision": "run_manifest_identity_surface_ok" if not errors else "repair_run_packet_or_source_lock_before_external_runner",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUN_MANIFEST_COHERENCE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace run-manifest coherence audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Files checked",
        "",
    ]
    md.extend(f"- `{r['path']}`" for r in reports)
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUN_MANIFEST_COHERENCE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
