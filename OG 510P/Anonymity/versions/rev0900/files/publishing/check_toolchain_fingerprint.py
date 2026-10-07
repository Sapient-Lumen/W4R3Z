#!/usr/bin/env python3
"""Verify that clean TeX evidence is bound to the live pdflatex fingerprint."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Any


COMPILE_EVIDENCE_SURFACES: tuple[dict[str, str], ...] = (
    {"label": "freeze_compile_witness", "path": "release_queue/FREEZE_COMPILE_WITNESS.json", "kind": "freeze"},
    {"label": "release_lane_compile_smoke", "path": "reports/queue_compile_smoke.json", "kind": "pdflatex"},
    {"label": "hold_compile_triage", "path": "release_queue/HOLD_COMPILE_TRIAGE.json", "kind": "pdflatex"},
    {"label": "unqueued_compile_triage", "path": "release_queue/UNQUEUED_COMPILE_TRIAGE.json", "kind": "pdflatex"},
    {"label": "published_compile_triage", "path": "published/PUBLISHED_COMPILE_TRIAGE.json", "kind": "pdflatex"},
    {"label": "auxiliary_tex_compile_triage", "path": "index/AUXILIARY_TEX_COMPILE_TRIAGE.json", "kind": "pdflatex"},
)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def command_version_record(command: str) -> dict[str, Any]:
    path = shutil.which(command)
    if not path:
        return {"command": command, "available": False, "path": "", "version_line": "", "version_output_sha256": ""}
    try:
        proc = subprocess.run([command, "--version"], text=True, capture_output=True, timeout=5)
        output = proc.stdout if proc.stdout else proc.stderr
    except Exception:
        output = ""
    return {
        "command": command,
        "available": True,
        "path": path,
        "version_line": output.splitlines()[0][:200] if output.splitlines() else "",
        "version_output_sha256": hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest() if output else "",
    }


def compile_report_from_witness(witness: dict[str, Any]) -> dict[str, Any]:
    preflight = witness.get("preflight_report", {}) if isinstance(witness.get("preflight_report"), dict) else {}
    details = preflight.get("details", {}) if isinstance(preflight.get("details"), dict) else {}
    return details.get("compile", {}) if isinstance(details.get("compile"), dict) else {}


def surface_toolchain(surface: dict[str, Any], kind: str) -> dict[str, Any]:
    toolchain = surface.get("toolchain", {}) if isinstance(surface.get("toolchain"), dict) else {}
    if kind == "freeze":
        return {
            "latex_command": toolchain.get("latex_command", "pdflatex"),
            "path": toolchain.get("latex_command_path", ""),
            "version_line": toolchain.get("version_line", ""),
            "version_output_sha256": toolchain.get("version_output_sha256", ""),
            "toolchain_available": bool(toolchain.get("latex_command_path")),
        }
    return {
        "latex_command": toolchain.get("latex_command", "pdflatex"),
        "path": toolchain.get("pdflatex_path", ""),
        "version_line": toolchain.get("pdflatex_version_line", ""),
        "version_output_sha256": toolchain.get("pdflatex_version_output_sha256", ""),
        "toolchain_available": bool(toolchain.get("toolchain_available")),
    }




def pending_freeze_noncompile(surface: dict[str, Any]) -> bool:
    preflight = surface.get("preflight_report", {}) if isinstance(surface.get("preflight_report"), dict) else {}
    details = preflight.get("details", {}) if isinstance(preflight.get("details"), dict) else {}
    compile_row = details.get("compile", {}) if isinstance(details.get("compile"), dict) else {}
    toolchain = surface.get("toolchain", {}) if isinstance(surface.get("toolchain"), dict) else {}
    return (
        surface.get("witness_type") == "pending_unstaged_source_no_compile_attempt"
        and surface.get("compile_gate_status") == "pending_evidence_pack_attachment"
        and int(toolchain.get("run_count", -1) or 0) == 0
        and compile_row.get("status") == "not_run"
        and int(compile_row.get("run_count", -1) or 0) == 0
        and surface.get("publication_authorized") is False
    )

def surface_clean(surface: dict[str, Any], kind: str) -> bool:
    if kind == "freeze":
        return str(surface.get("compile_gate_status", "")) == "pass"
    summary = surface.get("summary", {}) if isinstance(surface.get("summary"), dict) else {}
    return (
        surface.get("status") == "pass"
        and int(summary.get("targets_failed", 0) or 0) == 0
        and int(summary.get("final_unresolved_warning_hits_total", 0) or 0) == 0
        and int(summary.get("final_rerun_warning_hits_total", 0) or 0) == 0
    )


def negative_control_results(current: dict[str, Any]) -> list[dict[str, Any]]:
    def mismatch(row: dict[str, Any]) -> bool:
        return not row.get("toolchain_available") or row.get("path") != current.get("path") or row.get("version_line") != current.get("version_line") or row.get("version_output_sha256") != current.get("version_output_sha256")

    controls = [
        ("missing_path", {"toolchain_available": True, "path": "", "version_line": current.get("version_line", ""), "version_output_sha256": current.get("version_output_sha256", "")}),
        ("path_mismatch", {"toolchain_available": True, "path": "/not/the/live/pdflatex", "version_line": current.get("version_line", ""), "version_output_sha256": current.get("version_output_sha256", "")}),
        ("missing_version_line", {"toolchain_available": True, "path": current.get("path", ""), "version_line": "", "version_output_sha256": current.get("version_output_sha256", "")}),
        ("missing_version_digest", {"toolchain_available": True, "path": current.get("path", ""), "version_line": current.get("version_line", ""), "version_output_sha256": ""}),
        ("digest_mismatch", {"toolchain_available": True, "path": current.get("path", ""), "version_line": current.get("version_line", ""), "version_output_sha256": "0" * 64}),
        ("unavailable_toolchain", {"toolchain_available": False, "path": current.get("path", ""), "version_line": current.get("version_line", ""), "version_output_sha256": current.get("version_output_sha256", "")}),
    ]
    rows = []
    for name, fake in controls:
        detected = mismatch(fake)
        rows.append({"name": name, "status": "pass" if detected else "fail", "expected_failure_detected": detected})
    return rows


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    toolchain_report = load_json(root / "reports" / "freeze_toolchain.json")
    witness_report = load_json(root / "reports" / "freeze_compile_witness.json")
    witness = load_json(root / "release_queue" / "FREEZE_COMPILE_WITNESS.json")
    failures: list[dict[str, Any]] = []

    for label, obj in [("freeze_toolchain", toolchain_report), ("freeze_compile_witness_report", witness_report), ("freeze_compile_witness", witness)]:
        if obj.get("generated_for_revision") != release["revision"] or obj.get("checked_bundle") != release["bundle"]:
            failures.append({"category": "revision_or_bundle_mismatch", "surface": label, "revision": obj.get("generated_for_revision"), "bundle": obj.get("checked_bundle")})
        if obj.get("publication_authorized") is not False:
            failures.append({"category": "publication_authorized_not_false", "surface": label})

    witness_toolchain = witness.get("toolchain", {}) if isinstance(witness.get("toolchain"), dict) else {}
    latex_command = str(witness_toolchain.get("latex_command", "pdflatex"))
    current = command_version_record(latex_command)
    report_rows = {str(row.get("command")): row for row in toolchain_report.get("commands", []) if isinstance(row, dict)}
    report_row = report_rows.get(latex_command, {})
    compile_report = compile_report_from_witness(witness)
    compile_gate_status = str(witness.get("compile_gate_status", witness_report.get("compile_gate_status", "")))

    if compile_gate_status == "pass":
        if not current.get("available"):
            failures.append({"category": "compile_gate_pass_but_current_toolchain_unavailable", "latex_command": latex_command})
        if witness_toolchain.get("latex_command_path") != current.get("path"):
            failures.append({"category": "witness_toolchain_path_mismatch", "witness": witness_toolchain.get("latex_command_path"), "current": current.get("path")})
        if witness_report.get("toolchain", {}).get("current_latex_command_path") != current.get("path"):
            failures.append({"category": "report_toolchain_path_mismatch", "report": witness_report.get("toolchain", {}).get("current_latex_command_path"), "current": current.get("path")})
        for key in ["version_line", "version_output_sha256"]:
            if not witness_toolchain.get(key):
                failures.append({"category": "witness_toolchain_fingerprint_missing", "field": key})
            elif witness_toolchain.get(key) != current.get(key):
                failures.append({"category": "witness_toolchain_fingerprint_mismatch", "field": key, "witness": witness_toolchain.get(key), "current": current.get(key)})
            if report_row.get(key) != current.get(key):
                failures.append({"category": "freeze_toolchain_report_fingerprint_mismatch", "field": key, "report": report_row.get(key), "current": current.get(key)})
        if compile_report.get("deterministic_pdf_environment") is not True or not compile_report.get("source_date_epoch"):
            failures.append({"category": "compile_report_missing_deterministic_environment"})

    compile_surface_results: list[dict[str, Any]] = []
    path_missing = 0
    fingerprint_missing = 0
    fingerprint_mismatch = 0
    surface_fail_count = 0
    for spec in COMPILE_EVIDENCE_SURFACES:
        rel_path = spec["path"]
        surf_path = root / rel_path
        if not surf_path.exists():
            surface_fail_count += 1
            path_missing += 1
            failures.append({"category": "compile_surface_missing", "surface": spec["label"], "path": rel_path})
            continue
        surface = load_json(surf_path)
        if surface.get("generated_for_revision") != release["revision"] or surface.get("checked_bundle") != release["bundle"]:
            surface_fail_count += 1
            failures.append({"category": "compile_surface_revision_or_bundle_mismatch", "surface": spec["label"], "revision": surface.get("generated_for_revision"), "bundle": surface.get("checked_bundle")})
        if surface.get("publication_authorized") is not False:
            surface_fail_count += 1
            failures.append({"category": "compile_surface_authorization_not_false", "surface": spec["label"]})
        pending_noncompile = spec["kind"] == "freeze" and pending_freeze_noncompile(surface)
        if not surface_clean(surface, spec["kind"]) and not pending_noncompile:
            surface_fail_count += 1
            failures.append({"category": "compile_surface_not_clean_pass", "surface": spec["label"], "status": surface.get("status"), "compile_gate_status": surface.get("compile_gate_status")})
        st = surface_toolchain(surface, spec["kind"])
        missing_fields = [key for key in ("path", "version_line", "version_output_sha256") if not st.get(key)]
        if not st.get("toolchain_available") or missing_fields:
            surface_fail_count += 1
            fingerprint_missing += 1
            failures.append({"category": "compile_surface_fingerprint_missing", "surface": spec["label"], "missing_fields": missing_fields, "toolchain_available": st.get("toolchain_available")})
        elif st.get("path") != current.get("path") or st.get("version_line") != current.get("version_line") or st.get("version_output_sha256") != current.get("version_output_sha256"):
            surface_fail_count += 1
            fingerprint_mismatch += 1
            failures.append({"category": "compile_surface_fingerprint_mismatch", "surface": spec["label"], "surface_toolchain": st, "current_toolchain": current})
        compile_surface_results.append({
            "surface": spec["label"],
            "path": rel_path,
            "evidence_state": "pending_noncompile_publication_blocking" if pending_noncompile else "compile_pass",
            "status": "pass" if not missing_fields and st.get("toolchain_available") and st.get("path") == current.get("path") and st.get("version_output_sha256") == current.get("version_output_sha256") else "fail",
            "toolchain_path": st.get("path", ""),
            "version_line": st.get("version_line", ""),
            "version_output_sha256": st.get("version_output_sha256", ""),
        })

    negative_controls = negative_control_results(current)
    negative_failures = [row for row in negative_controls if row.get("status") != "pass"]
    failures.extend({"category": "negative_control_not_detected", "name": row.get("name")} for row in negative_failures)

    command_fingerprints = []
    for command in sorted({"pdflatex", "latexmk", latex_command}):
        current_record = command_version_record(command)
        reported = report_rows.get(command, {})
        command_fingerprints.append({
            "command": command,
            "available": current_record.get("available"),
            "current_path": current_record.get("path"),
            "reported_path": reported.get("path", ""),
            "version_line": current_record.get("version_line", ""),
            "version_output_sha256": current_record.get("version_output_sha256", ""),
            "reported_version_output_sha256": reported.get("version_output_sha256", ""),
        })

    summary = {
        "checks_failed": len(failures),
        "compile_gate_status": compile_gate_status,
        "latex_command": latex_command,
        "toolchain_available": bool(current.get("available")),
        "fingerprint_required": compile_gate_status == "pass",
        "fingerprint_present": bool(witness_toolchain.get("version_line") and witness_toolchain.get("version_output_sha256")),
        "command_fingerprint_count": len(command_fingerprints),
        "compile_surface_fingerprint_expected_count": len(COMPILE_EVIDENCE_SURFACES),
        "compile_surface_fingerprint_count": len(compile_surface_results),
        "compile_surface_fingerprint_fail_count": surface_fail_count,
        "compile_surface_path_missing_count": path_missing,
        "compile_surface_fingerprint_missing_count": fingerprint_missing,
        "compile_surface_fingerprint_mismatch_count": fingerprint_mismatch,
        "negative_control_count": len(negative_controls),
        "negative_control_failed_count": len(negative_failures),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "freeze_toolchain_report": "reports/freeze_toolchain.json",
        "compile_witness": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "compile_evidence_surfaces": compile_surface_results,
        "negative_controls": negative_controls,
        "command_fingerprints": command_fingerprints,
        "summary": summary,
        "failures": failures[:50],
        "fail_closed_rule": "Every actual compile receipt must bind the live pdflatex fingerprint; a truthful pending noncompile witness may pass integrity only while its publication gate remains explicitly blocked. Detector negative controls must catch stale or missing fingerprints.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
