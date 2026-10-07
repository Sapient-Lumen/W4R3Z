#!/usr/bin/env python3
"""Verify the source-bound compile witness for the freeze target.

The report distinguishes between a safe witness surface and a closed publication
compile gate.  A carried-forward source-bound clean compile may be safe to ship
as historical evidence, but it does not close the current publication gate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import sys
from typing import Any

MIN_PDFLATEX_COMPILE_PASSES = 3

def minimum_compile_runs(command: str) -> int:
    return MIN_PDFLATEX_COMPILE_PASSES if command == "pdflatex" else 1

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_release_readiness as rr  # noqa: E402


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_date_epoch_from_manifest(release_manifest: dict[str, Any]) -> str:
    raw = str(release_manifest.get("timestamp", ""))
    try:
        when = dt.datetime.strptime(raw, "%Y.%m.%d.%H.%M").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        when = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    return str(int(when.timestamp()))


def compile_report_from_witness(witness: dict[str, Any]) -> dict[str, Any]:
    preflight = witness.get("preflight_report", {}) if isinstance(witness.get("preflight_report"), dict) else {}
    details = preflight.get("details", {}) if isinstance(preflight.get("details"), dict) else {}
    return details.get("compile", {}) if isinstance(details.get("compile"), dict) else {}


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    readiness = rr.check(root)
    recommendation = readiness.get("next_release_recommendation", {}) if isinstance(readiness.get("next_release_recommendation"), dict) else {}
    witness_path = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    failures: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    expected_epoch = source_date_epoch_from_manifest(release)

    if recommendation.get("status") != "static_pass_candidate_available":
        failures.append({"category": "no_static_pass_recommendation", "recommendation": recommendation})
        expected_source = None
        expected_sha = None
    else:
        expected_source = recommendation.get("source_tex")
        expected_sha = recommendation.get("source_sha256")

    witness: dict[str, Any] = {}
    compile_report: dict[str, Any] = {}
    toolchain: dict[str, Any] = {}
    gate_status = "missing"
    clean_compile_evidence = False
    deterministic_compile_evidence = False
    carried_forward = False
    pending_unstaged = False
    current_latex_path = None

    if not witness_path.exists():
        pending.append({"category": "compile_witness_missing", "path": "release_queue/FREEZE_COMPILE_WITNESS.json"})
        gate_status = "pending_missing_witness"
    else:
        witness = load_json(witness_path)
        compile_report = compile_report_from_witness(witness)
        toolchain = witness.get("toolchain", {}) if isinstance(witness.get("toolchain"), dict) else {}
        current_latex_path = shutil.which(str(toolchain.get("latex_command", "pdflatex")))
        gate_status = str(witness.get("compile_gate_status", "pass"))
        carried_forward = "carried_forward" in str(witness.get("witness_type", ""))
        pending_unstaged = witness.get("witness_type") == "pending_unstaged_source_no_compile_attempt"

        if witness.get("publication_authorized") is not False:
            failures.append({"category": "witness_publication_authorized_not_false"})
        if witness.get("generated_for_revision") != release["revision"]:
            failures.append({"category": "witness_revision_mismatch", "witness": witness.get("generated_for_revision"), "current": release["revision"]})
        if witness.get("checked_bundle") != release["bundle"]:
            failures.append({"category": "witness_bundle_mismatch", "witness": witness.get("checked_bundle"), "current": release["bundle"]})
        if expected_source and witness.get("source_tex") != expected_source:
            failures.append({"category": "witness_source_mismatch", "expected": expected_source, "actual": witness.get("source_tex")})
        if expected_sha and witness.get("source_sha256") != expected_sha:
            failures.append({"category": "witness_source_sha_mismatch", "expected": expected_sha, "actual": witness.get("source_sha256")})
        if expected_source:
            src = root / str(expected_source)
            if not src.exists():
                failures.append({"category": "source_missing", "source_tex": expected_source})
            else:
                actual = sha256_file(src)
                if actual != expected_sha or actual != witness.get("source_sha256"):
                    failures.append({"category": "current_source_sha_mismatch", "actual": actual, "recommendation": expected_sha, "witness": witness.get("source_sha256")})

        if pending_unstaged:
            gate_status = "pending_evidence_pack_attachment"
            pending.append({
                "category": "unstaged_source_waiting_for_explicit_evidence_attachment",
                "source_tex": expected_source,
                "reason": witness.get("pending_reason", "selected source has no staged evidence lane"),
            })
            if witness.get("evidence_pack_manifest") not in {"", None}:
                failures.append({"category": "pending_unstaged_witness_claims_evidence_manifest", "path": witness.get("evidence_pack_manifest")})
            if witness.get("preflight_report", {}).get("details", {}).get("compile", {}).get("status") not in {"not_run", None}:
                failures.append({"category": "pending_unstaged_witness_claims_compile_attempt"})
        else:
            preflight = witness.get("preflight_report", {}) if isinstance(witness.get("preflight_report"), dict) else {}
            if preflight.get("status") != "pass" or preflight.get("problems"):
                failures.append({"category": "compile_preflight_not_pass", "status": preflight.get("status"), "problems": preflight.get("problems")})
            if compile_report.get("status") != "pass":
                failures.append({"category": "compile_report_not_pass", "compile_status": compile_report.get("status"), "detail": compile_report.get("detail")})
            compile_command = str(compile_report.get("command", toolchain.get("latex_command", "pdflatex")))
            required_runs = minimum_compile_runs(compile_command)
            if int(compile_report.get("run_count", 0)) < required_runs:
                failures.append({"category": "compile_run_count_below_required", "command": compile_command, "run_count": compile_report.get("run_count"), "minimum_required": required_runs})
            if int(compile_report.get("minimum_required_passes", required_runs)) < required_runs:
                failures.append({"category": "compile_minimum_required_passes_too_low", "command": compile_command, "declared": compile_report.get("minimum_required_passes"), "minimum_required": required_runs})
            if int(toolchain.get("run_count", 0)) < required_runs:
                failures.append({"category": "toolchain_run_count_below_required", "command": compile_command, "run_count": toolchain.get("run_count"), "minimum_required": required_runs})
            if int(compile_report.get("final_warning_count", 999)) != 0:
                failures.append({"category": "final_compile_warnings_present", "final_warning_count": compile_report.get("final_warning_count"), "warnings": compile_report.get("warnings")})
            if int(compile_report.get("final_rerun_warning_count", 999)) != 0:
                failures.append({"category": "final_compile_rerun_warnings_present", "final_rerun_warning_count": compile_report.get("final_rerun_warning_count"), "warnings": compile_report.get("final_rerun_warnings")})
            if not compile_report.get("output_pdf_sha256") or int(compile_report.get("output_pdf_bytes", 0)) <= 0:
                failures.append({"category": "missing_output_pdf_digest_or_size", "compile_report": compile_report})
            else:
                clean_compile_evidence = True

            evidence_manifest = witness.get("evidence_pack_manifest")
            if not evidence_manifest or not (root / str(evidence_manifest)).exists():
                failures.append({"category": "evidence_pack_manifest_missing", "path": evidence_manifest})
            expected_date = ".".join(str(release.get("timestamp", "")).split(".")[:3])
            expected_date_slug = expected_date.replace(".", "-")
            prospective = str(preflight.get("prospective_published_name", ""))
            legacy_date_match = prospective.startswith(expected_date + " - ")
            portable_date_match = prospective.startswith(expected_date_slug + "_")
            if expected_date and not (legacy_date_match or portable_date_match):
                failures.append({"category": "preflight_date_mismatch", "expected_date": expected_date, "expected_date_slug": expected_date_slug, "prospective_published_name": prospective})

            compile_epoch = str(compile_report.get("source_date_epoch", ""))
            tool_epoch = str(toolchain.get("source_date_epoch", ""))
            deterministic_compile_evidence = bool(compile_report.get("deterministic_pdf_environment") is True and compile_epoch == expected_epoch and tool_epoch == expected_epoch)
            if gate_status == "pass" and not deterministic_compile_evidence:
                failures.append({"category": "current_compile_gate_requires_deterministic_source_date_epoch", "expected_source_date_epoch": expected_epoch, "compile_report_epoch": compile_epoch, "toolchain_epoch": tool_epoch})
            if carried_forward:
                gate_status = "pending_current_toolchain_refresh"
                pending.append({
                    "category": "carried_forward_compile_evidence",
                    "compiled_for_revision": witness.get("compiled_for_revision"),
                    "compiled_bundle": witness.get("compiled_bundle"),
                    "reason": witness.get("carried_forward_reason"),
                })
            elif gate_status != "pass":
                pending.append({"category": "compile_gate_not_closed", "compile_gate_status": gate_status})
            if current_latex_path is None:
                warnings.append({"category": "latex_toolchain_unavailable", "latex_command": toolchain.get("latex_command", "pdflatex")})

    report_status = "pass" if not failures else "fail"
    return {
        "status": report_status,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "witness_path": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "selected_source": expected_source,
        "selected_source_sha256": expected_sha,
        "witness_revision": witness.get("generated_for_revision"),
        "witness_bundle": witness.get("checked_bundle"),
        "witness_source": witness.get("source_tex"),
        "witness_source_sha256": witness.get("source_sha256"),
        "witness_type": witness.get("witness_type"),
        "compile_gate_status": gate_status,
        "publication_blocking_until_refreshed": bool(gate_status != "pass"),
        "expected_source_date_epoch": expected_epoch,
        "toolchain": {
            "latex_command": toolchain.get("latex_command", "pdflatex"),
            "recorded_latex_command_path": toolchain.get("latex_command_path"),
            "current_latex_command_path": current_latex_path,
            "version_line": toolchain.get("version_line", ""),
            "version_output_sha256": toolchain.get("version_output_sha256", ""),
            "source_date_epoch": toolchain.get("source_date_epoch"),
        },
        "compile": compile_report,
        "pending": pending[:50],
        "warnings": warnings[:50],
        "summary": {
            "checks_failed": len(failures),
            "pending_items": len(pending),
            "witness_present": witness_path.exists(),
            "witness_current_revision": bool(witness.get("generated_for_revision") == release["revision"] and witness.get("checked_bundle") == release["bundle"]),
            "source_bound": bool(expected_source and witness.get("source_tex") == expected_source and witness.get("source_sha256") == expected_sha),
            "clean_final_compile": bool(clean_compile_evidence and int(compile_report.get("final_warning_count", 999)) == 0 and int(compile_report.get("final_rerun_warning_count", 999)) == 0),
            "deterministic_compile_evidence": deterministic_compile_evidence,
            "compile_run_count": compile_report.get("run_count"),
            "minimum_required_passes": compile_report.get("minimum_required_passes"),
            "final_rerun_warning_count": compile_report.get("final_rerun_warning_count"),
            "compile_gate_closed": bool(gate_status == "pass" and report_status == "pass"),
            "carried_forward": carried_forward,
            "pending_unstaged_source": pending_unstaged,
        },
        "failures": failures[:50],
        "fail_closed_rule": "A missing, stale, or carried-forward compile witness may be safe evidence but does not close the current publication compile gate unless compile_gate_status is pass.",
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
