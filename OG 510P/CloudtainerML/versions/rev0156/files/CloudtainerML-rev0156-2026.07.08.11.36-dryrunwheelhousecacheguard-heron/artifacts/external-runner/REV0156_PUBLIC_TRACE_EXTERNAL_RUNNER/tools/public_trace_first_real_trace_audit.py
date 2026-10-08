#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0140"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "140"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
TRACE_ROOT = ROOT / "artifacts" / "trace-bundles"
PROBE_ROOT = ROOT / "artifacts" / "probe-results"

REQUIRED_SURFACE = [
    "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
    "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
    "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
    f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
    f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
    f"artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
    "tools/public_trace_first_real_trace_audit.py",
    "tools/current_live_script_dependency_audit.py",
    "tools/public_trace_external_runner_packet_builder.py",
]
EXPECTED_OUTPUTS = {
    "trace_npz": f"artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz",
    "provenance_json": f"artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json",
    "gate_json": f"artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json",
    "evaluation_receipt": f"artifacts/probe-results/{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
    "selector_entry_receipt": f"artifacts/probe-results/{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json",
    "handoff_dir_manifest": f"artifacts/trace-bundles/{REVUP}_PUBLIC_TRACE_HANDOFF/PUBLIC_TRACE_HANDOFF_MANIFEST.json",
    "handoff_zip": f"artifacts/trace-bundles/{REVUP}_PUBLIC_TRACE_HANDOFF.zip",
}
RESEARCH_BASIS = [
    {
        "source": "Hugging Face Hub download guide",
        "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
        "observed": "snapshot_download supports a specific full-length commit hash and filtering/local-folder/dry-run flows; see retrieved lines 117-170 and 202-226 in the session research.",
        "implication": "The first-trace path should be a runnable packet with an explicit snapshot-preparation phase, not a narrative-only handoff.",
    },
    {
        "source": "Transformers attention backend docs",
        "url": "https://huggingface.co/docs/transformers/en/attention_interface",
        "observed": "Backend mask conventions differ; eager adds a float mask to scores while SDPA/Flash/Flex consume different conventions.",
        "implication": "The trace command must keep ATTENTION_IMPLEMENTATION=eager and treat fused backends as separate timing lanes after the trace exists.",
    },
    {
        "source": "Safetensors docs",
        "url": "https://huggingface.co/docs/safetensors/index",
        "observed": "Safetensors is a safe/fast tensor storage format and supports partial metadata/tensor access.",
        "implication": "Format validity is not enough for public evidence; this cube still requires explicit file SHA-256 binding for model.safetensors.",
    },
    {
        "source": "Artisan artifact-evaluation paper",
        "url": "https://arxiv.org/abs/2602.10046",
        "observed": "The paper frames reproduction as executable scripts and reports successful reproduction-script generation plus error discovery.",
        "implication": "A first-trace one-command runner is higher value than another registry page.",
    },
    {
        "source": "LLM-for-SE reproducibility crisis paper",
        "url": "https://arxiv.org/abs/2512.00651",
        "observed": "Recent study reports persistent gaps in environment, versioning, model/access/legal, and execution fidelity.",
        "implication": "The runner should produce status receipts and keep the license/source/snapshot boundaries explicit.",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def write_audit(name: str, audit: dict[str, Any]) -> None:
    (OUT / f"{REVUP}_{name}.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [f"# {name.replace('_', ' ').title()} — {REVUP}", "", f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "", audit.get("summary", ""), ""]
    if audit.get("errors") is not None:
        md += ["## Errors", ""] + ([f"- `{e}`" for e in audit["errors"]] if audit["errors"] else ["- none"])
    if audit.get("warnings") is not None:
        md += ["", "## Warnings", ""] + ([f"- `{w}`" for w in audit["warnings"]] if audit["warnings"] else ["- none"])
    if audit.get("missing_outputs") is not None:
        md += ["", "## Missing outputs", ""] + ([f"- `{m}`" for m in audit["missing_outputs"]] if audit["missing_outputs"] else ["- none"])
    if audit.get("present_outputs") is not None:
        md += ["", "## Present outputs", ""] + ([f"- `{p}`" for p in audit["present_outputs"]] if audit["present_outputs"] else ["- none"])
    md += ["", "## Decision", "", str(audit.get("decision", ""))]
    (OUT / f"{REVUP}_{name}.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")


def surface_audit() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    missing = [rel for rel in REQUIRED_SURFACE if not rel_exists(rel)]
    errors.extend("missing_first_trace_surface:" + rel for rel in missing)
    executable_missing: list[str] = []
    for rel in REQUIRED_SURFACE:
        if rel.endswith(".sh") and rel_exists(rel):
            p = ROOT / rel
            if not os.access(p, os.X_OK):
                executable_missing.append(rel)
    errors.extend("first_trace_script_not_executable:" + rel for rel in executable_missing)
    stable = read("artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh")
    one_command = read(f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh")
    run_current = read("artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh")
    builder = read("tools/public_trace_external_runner_packet_builder.py")
    if f"{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh" not in stable:
        errors.append("stable_first_trace_alias_does_not_exec_current_revision_script")
    for marker in [
        "BOOTSTRAP_RUNTIME",
        "PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
        "ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1",
        "public_trace_first_real_trace_audit.py --mode status",
        "public_trace_first_real_trace_audit.py --mode surface",
    ]:
        if marker not in one_command:
            errors.append("one_command_missing_marker:" + marker)
    if "REV0139" in one_command or "rev0139" in one_command:
        errors.append("one_command_contains_stale_rev0139_reference")
    if f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in run_current:
        errors.append("stable_public_trace_alias_not_moved_to_current_revision")
    builder_markers = [
        ("RUN_FIRST_REAL_TRACE.sh", "RUN_FIRST_REAL_TRACE.sh"),
        ("RUN_CURRENT_FIRST_REAL_TRACE.sh", "RUN_CURRENT_FIRST_REAL_TRACE.sh"),
        ("current_revision_first_trace_script", f"artifacts/capture-kit/{{REVUP}}_FIRST_REAL_TRACE_ONE_COMMAND.sh"),
    ]
    for label, marker in builder_markers:
        if marker not in builder:
            errors.append("external_runner_builder_missing_first_trace_marker:" + label)
    if "RUN_FIRST_REAL_TRACE.sh" not in builder:
        warnings.append("external packet may still require manual three-phase operation")
    status_outputs = {k: {"path": v, "present": rel_exists(v)} for k, v in EXPECTED_OUTPUTS.items()}
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Audits the active first-real-trace runner surface added to avoid another doctrine-only turn: one command must bootstrap optionally, prepare/hash the snapshot only when allowed, force local-only capture, and write blocker-first status receipts on failure or success.",
        "required_surface": REQUIRED_SURFACE,
        "status_outputs": status_outputs,
        "research_basis": RESEARCH_BASIS,
        "errors": errors,
        "warnings": warnings,
        "decision": "first_trace_one_command_surface_ready" if not errors else "repair_first_trace_runner_surface_before_external_use",
    }
    write_audit("PUBLIC_TRACE_FIRST_REAL_TRACE_SURFACE_AUDIT", audit)
    return audit


def unique_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out

def status_audit(runner_exit_code: int | None, last_phase: str | None) -> dict[str, Any]:
    def load_first_existing(candidates: list[Path]) -> tuple[str | None, dict[str, Any] | None]:
        for candidate in candidates:
            if candidate.exists():
                try:
                    return candidate.relative_to(ROOT).as_posix(), json.loads(candidate.read_text(encoding="utf-8"))
                except Exception as exc:
                    return candidate.relative_to(ROOT).as_posix(), {"read_error": repr(exc)}
        return None, None

    phase_candidates: dict[str, list[Path]] = {
        "runtime_requirement_lock": [OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.json"],
        "common_env_contract": [OUT / f"{REVUP}_PUBLIC_TRACE_COMMON_ENV_CONTRACT_AUDIT.json"],
        "first_trace_surface": [OUT / f"{REVUP}_PUBLIC_TRACE_FIRST_REAL_TRACE_SURFACE_AUDIT.json"],
        "run_manifest_coherence": [OUT / f"{REVUP}_PUBLIC_TRACE_RUN_MANIFEST_COHERENCE_AUDIT.json"],
        "bootstrap_runtime_audit": [OUT / f"{REVUP}_PUBLIC_TRACE_BOOTSTRAP_RUNTIME_AUDIT.json"],
        "cache_root_contract": [OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_ROOT_CONTRACT_AUDIT.json"],
        "snapshot_digest_receipt_cache": [OUT / f"{REVUP}_SNAPSHOT_DIGEST_RECEIPT_CACHE_AUDIT.json"],
        "snapshot_download_plan_gate": [OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN_AUDIT.json", OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN_GATE_AUDIT.json"],
        "offline_quarantine": [OUT / f"{REVUP}_PUBLIC_TRACE_OFFLINE_QUARANTINE_AUDIT.json"],
        "live_script_dependency": [OUT / f"{REVUP}_CURRENT_LIVE_SCRIPT_DEPENDENCY_AUDIT.json"],
        "runtime_import_smoke": [OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.json"],
        "bootstrap_runtime": [OUT / f"{REVUP}_PUBLIC_TRACE_BOOTSTRAP_RUNTIME_AUDIT.json", OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.json"],
        "bootstrap_runtime_dry_run": [OUT / f"{REVUP}_PUBLIC_TRACE_BOOTSTRAP_RUNTIME_AUDIT.json", OUT / f"{REVUP}_PUBLIC_TRACE_CACHE_DUPLICATION_GUARD_AUDIT.json"],
        "prepare_snapshot": [OUT / f"{REVUP}_HF_SNAPSHOT_MATERIALIZER.json", OUT / f"{REVUP}_PUBLIC_TRACE_FAST_PREREQ_GATE.json", OUT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.json"],
        "capture_local_only": [OUT / f"{REVUP}_PUBLIC_TRACE_CAPTURE_START_PREFLIGHT_REPORT.json", OUT / f"{REVUP}_PUBLIC_TRACE_READINESS_GATE.json", OUT / f"{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json"],
        "final_status": [OUT / f"{REVUP}_PUBLIC_TRACE_CURRENT_TRACE_LANE_AUDIT.json"],
    }
    phase_receipt_path, phase_receipt = load_first_existing(phase_candidates.get(str(last_phase), []))
    outputs = {}
    present_outputs: list[str] = []
    missing_outputs: list[str] = []
    for label, rel in EXPECTED_OUTPUTS.items():
        p = ROOT / rel
        item = {"path": rel, "present": p.exists()}
        if p.exists() and p.is_file():
            item.update({"bytes": p.stat().st_size, "sha256": sha256_file(p)})
        outputs[label] = item
        if p.exists():
            present_outputs.append(rel)
        else:
            missing_outputs.append(rel)
    snapshot_env = ROOT / "artifacts/runtime/CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh"
    status = "real_trace_receipts_complete" if not missing_outputs and (runner_exit_code in (0, None)) else "blocked_here"
    blockers = []
    if str(last_phase) == "bootstrap_runtime_dry_run":
        blockers.append("bootstrap_dry_run_only_no_capture_attempted")
    if missing_outputs:
        blockers.append("first_real_trace_outputs_missing")
    if runner_exit_code not in (0, None):
        blockers.append(f"runner_exit_code_{runner_exit_code}")
    phase_blockers: list[str] = []
    phase_errors: list[str] = []
    phase_status = None
    if phase_receipt and isinstance(phase_receipt, dict):
        phase_status = phase_receipt.get("status")
        for key in ["blockers", "errors", "missing", "hard_blockers"]:
            values = phase_receipt.get(key, [])
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, str):
                        (phase_errors if key == "errors" else phase_blockers).append(item)
        nested = phase_receipt.get("modules")
        if isinstance(nested, dict):
            for name, rec in nested.items():
                if isinstance(rec, dict) and rec.get("present") is False:
                    phase_blockers.append(f"{name}_not_present_in_runtime_python")
    phase_blockers = unique_strings(phase_blockers)
    phase_errors = unique_strings(phase_errors)
    for blocker in phase_blockers:
        blockers.append(f"phase_{last_phase}:{blocker}")
    for err in phase_errors:
        blockers.append(f"phase_{last_phase}_error:{err}")
    if not snapshot_env.exists():
        blockers.append("capture_env_not_written_or_not_carried_forward")

    first_blocker_candidate = None
    if str(last_phase) == "bootstrap_runtime_dry_run":
        first_blocker_candidate = "bootstrap_runtime_dry_run_only"
    elif phase_blockers:
        first_blocker_candidate = f"{last_phase}:{phase_blockers[0]}"
    elif phase_errors:
        first_blocker_candidate = f"{last_phase}:error:{phase_errors[0]}"
    elif runner_exit_code not in (0, None):
        first_blocker_candidate = f"runner_exit_code_{runner_exit_code}"
    elif missing_outputs:
        first_blocker_candidate = "first_real_trace_outputs_missing"
    elif not snapshot_env.exists():
        first_blocker_candidate = "capture_env_not_written_or_not_carried_forward"

    operator_action = "continue_to_replay_and_named_hardware_timing"
    if first_blocker_candidate:
        if "transformers_not_present" in first_blocker_candidate:
            operator_action = "run BOOTSTRAP_RUNTIME=1 or install the pinned runtime requirements in the project venv, then rerun RUN_FIRST_REAL_TRACE.sh"
        elif str(last_phase) == "bootstrap_runtime_dry_run":
            operator_action = "dry run passed; rerun without PUBLIC_TRACE_BOOTSTRAP_DRY_RUN, optionally with PUBLIC_TRACE_WHEELHOUSE for offline/no-index package installs"
        elif str(last_phase) == "bootstrap_runtime":
            operator_action = "run PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/${REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh; then run BOOTSTRAP_RUNTIME=1 after the requirement path and venv target resolve"
        elif str(last_phase) == "prepare_snapshot":
            operator_action = "fix the snapshot preparation/materialization receipt before attempting capture"
        elif str(last_phase) == "capture_local_only":
            operator_action = "fix the selected-snapshot/local-only capture preflight receipt before running the one-shot capture"
        else:
            operator_action = "fix the first receipt-backed blocker before adding doctrine or registry work"
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": status == "real_trace_receipts_complete",
        "gpu_fused_kernel_measured": False,
        "summary": "Status receipt for the first real TinyLlama trace runner. REV0156 keeps this receipt blocker-first: it names the likely failed phase receipt, first_blocker_candidate, and operator_action. It does not claim evidence unless the trace, provenance, gate, evaluation receipt, selector receipt, and handoff archive all exist.",
        "runner_exit_code": runner_exit_code,
        "last_phase": last_phase,
        "capture_env_present": snapshot_env.exists(),
        "phase_receipt_path": phase_receipt_path,
        "phase_receipt_status": phase_status,
        "phase_receipt_blockers": phase_blockers,
        "phase_receipt_errors": phase_errors,
        "first_blocker_candidate": first_blocker_candidate,
        "operator_action": operator_action,
        "outputs": outputs,
        "present_outputs": present_outputs,
        "missing_outputs": missing_outputs,
        "blockers": unique_strings(blockers),
        "errors": [],
        "warnings": ["status_receipt_is_not_promotion_evidence_without_named_hardware_timing"],
        "decision": "promote_to_selector_timing_only_after_independent_replay" if status == "real_trace_receipts_complete" else "fix_first_blocker_candidate_before_more_doctrine",
    }
    write_audit("PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS", audit)
    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["surface", "status", "both"], default="both")
    ap.add_argument("--runner-exit-code", type=int, default=None)
    ap.add_argument("--last-phase", default=None)
    args = ap.parse_args()
    result: dict[str, Any] = {}
    if args.mode in {"surface", "both"}:
        result["surface"] = surface_audit()
    if args.mode in {"status", "both"}:
        result["status"] = status_audit(args.runner_exit_code, args.last_phase)
    print(json.dumps({k: v["status"] for k, v in result.items()}, indent=2))
    return 0 if all(v["status"] in {"pass", "blocked_here", "real_trace_receipts_complete"} for v in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
