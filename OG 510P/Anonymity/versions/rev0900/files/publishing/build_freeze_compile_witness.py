#!/usr/bin/env python3
"""Build or carry forward the non-authorizing compile witness for the freeze target.

A current deterministic witness is preferred.  In a TeX-equipped environment the
builder runs release_preflight.py with SOURCE_DATE_EPOCH.  If the local TeX
binary is unavailable, the builder may carry forward a prior source-hash-bound
clean compile as evidence while explicitly keeping the publication compile gate
pending.  This avoids silently relabeling stale compile evidence as current.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Any

MIN_PDFLATEX_COMPILE_PASSES = 3

def minimum_compile_runs(command: str) -> int:
    return MIN_PDFLATEX_COMPILE_PASSES if command == "pdflatex" else 1

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_release_readiness as rr  # noqa: E402

PREFIX = "Anonymity: "


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()



def toolchain_version_record(command: str) -> dict[str, str]:
    path = shutil.which(command)
    if not path:
        return {"version_line": "", "version_output_sha256": ""}
    try:
        proc = subprocess.run([command, "--version"], text=True, capture_output=True, timeout=5)
        output = proc.stdout if proc.stdout else proc.stderr
    except Exception:
        output = ""
    return {
        "version_line": output.splitlines()[0][:200] if output.splitlines() else "",
        "version_output_sha256": hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest() if output else "",
    }

def freeze_date_from_manifest(release_manifest: dict[str, Any]) -> str:
    parts = str(release_manifest.get("timestamp", "YYYY.MM.DD")).split(".")
    return ".".join(parts[:3]) if len(parts) >= 3 else "YYYY.MM.DD"


def source_date_epoch_from_manifest(release_manifest: dict[str, Any]) -> str:
    """Derive a deterministic SOURCE_DATE_EPOCH from RELEASE_MANIFEST.timestamp.

    The timestamp is intentionally interpreted as UTC for reproducibility; it is
    not used as a legal publication time.
    """
    raw = str(release_manifest.get("timestamp", ""))
    try:
        when = dt.datetime.strptime(raw, "%Y.%m.%d.%H.%M").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        when = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    return str(int(when.timestamp()))


def short_title(title: str) -> str:
    return title[len(PREFIX):] if title.startswith(PREFIX) else title


def evidence_manifest_for_source(root: pathlib.Path, source: str, source_sha: str) -> tuple[str, str]:
    """Return (manifest_rel, pack_root_rel) for the selected source."""
    registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
    if not registry_path.exists():
        raise RuntimeError("no EVIDENCE_PACK_REGISTRY.json; build evidence pack first")
    registry = load_json(registry_path)
    if registry.get("publication_authorized") is not False:
        raise RuntimeError("evidence registry must be non-authorizing")
    for entry in registry.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("source_tex") != source or entry.get("source_sha256") != source_sha:
            continue
        manifest_rel = str(entry.get("manifest", ""))
        manifest_path = root / manifest_rel
        if not manifest_path.exists():
            raise RuntimeError(f"evidence manifest missing: {manifest_rel}")
        manifest = load_json(manifest_path)
        if manifest.get("source_tex") != source or manifest.get("source_sha256") != source_sha:
            raise RuntimeError("evidence manifest is not source/hash bound")
        pack_root = str(manifest.get("evidence_pack_root") or pathlib.Path(manifest_rel).parent.as_posix())
        return manifest_rel, pack_root
    raise RuntimeError(f"no attached evidence pack for selected source: {source}")


def run_compile_preflight(
    root: pathlib.Path,
    *,
    freeze_date: str,
    title: str,
    source: str,
    source_sha: str,
    evidence_pack_root: str,
    latex_command: str,
    source_date_epoch: str,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-B",
        "publishing/release_preflight.py",
        "--root",
        ".",
        "--date",
        freeze_date,
        "--title",
        short_title(title),
        "--source",
        source,
        "--expected-source-sha256",
        source_sha,
        "--evidence-mode",
        "require",
        "--evidence-pack",
        evidence_pack_root,
        "--compile",
        "--latex-command",
        latex_command,
        "--source-date-epoch",
        source_date_epoch,
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, timeout=90)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "problems": ["release_preflight.py did not emit JSON"],
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
    report["command"] = " ".join(cmd[1:])
    report["returncode"] = proc.returncode
    if proc.returncode != 0 and report.get("status") == "pass":
        report["status"] = "fail"
        report.setdefault("problems", []).append(f"release_preflight.py returned {proc.returncode}")
    return report


def compile_report_from_witness(witness: dict[str, Any]) -> dict[str, Any]:
    preflight = witness.get("preflight_report", {}) if isinstance(witness.get("preflight_report"), dict) else {}
    details = preflight.get("details", {}) if isinstance(preflight.get("details"), dict) else {}
    compile_report = details.get("compile", {}) if isinstance(details.get("compile"), dict) else {}
    return compile_report


def witness_has_clean_compile_evidence(witness: dict[str, Any], *, source: str, source_sha: str, evidence_manifest: str, freeze_date: str) -> bool:
    if witness.get("publication_authorized") is not False:
        return False
    if witness.get("source_tex") != source or witness.get("source_sha256") != source_sha:
        return False
    if witness.get("evidence_pack_manifest") != evidence_manifest:
        return False
    preflight = witness.get("preflight_report", {}) if isinstance(witness.get("preflight_report"), dict) else {}
    compile_report = compile_report_from_witness(witness)
    if preflight.get("status") != "pass" or preflight.get("problems"):
        return False
    command = str(compile_report.get("command", (witness.get("toolchain", {}) if isinstance(witness.get("toolchain"), dict) else {}).get("latex_command", "pdflatex")))
    required_runs = minimum_compile_runs(command)
    if int(compile_report.get("run_count", 0)) < required_runs:
        return False
    if compile_report.get("status") != "pass" or int(compile_report.get("final_warning_count", 999)) != 0 or int(compile_report.get("final_rerun_warning_count", 999)) != 0:
        return False
    if not compile_report.get("output_pdf_sha256") or int(compile_report.get("output_pdf_bytes", 0)) <= 0:
        return False
    prospective = str(preflight.get("prospective_published_name", ""))
    if not prospective.startswith(freeze_date + " - "):
        return False
    return True


def reusable_current_witness(
    root: pathlib.Path,
    *,
    release: dict[str, Any],
    source: str,
    source_sha: str,
    evidence_manifest: str,
    latex_command: str,
    freeze_date: str,
    source_date_epoch: str,
) -> dict[str, Any] | None:
    path = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    if not path.exists():
        return None
    try:
        witness = load_json(path)
    except Exception:
        return None
    if witness.get("generated_for_revision") != release.get("revision"):
        return None
    if witness.get("checked_bundle") != release.get("bundle"):
        return None
    if not witness_has_clean_compile_evidence(witness, source=source, source_sha=source_sha, evidence_manifest=evidence_manifest, freeze_date=freeze_date):
        return None
    toolchain = witness.get("toolchain", {}) if isinstance(witness.get("toolchain"), dict) else {}
    if toolchain.get("latex_command") != latex_command:
        return None
    version_record = toolchain_version_record(latex_command)
    if toolchain.get("version_line") != version_record.get("version_line") or toolchain.get("version_output_sha256") != version_record.get("version_output_sha256"):
        return None
    compile_report = compile_report_from_witness(witness)
    gate = witness.get("compile_gate_status", "pass")
    if gate == "pass" and str(toolchain.get("source_date_epoch", "")) != source_date_epoch:
        return None
    return {
        "status": "pass",
        "written": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "mode": "reused_current_witness",
        "compile_gate_status": gate,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "source_tex": source,
        "source_sha256": source_sha,
        "output_pdf_sha256": compile_report.get("output_pdf_sha256"),
        "output_pdf_bytes": compile_report.get("output_pdf_bytes"),
        "final_warning_count": compile_report.get("final_warning_count"),
        "final_rerun_warning_count": compile_report.get("final_rerun_warning_count"),
        "run_count": compile_report.get("run_count"),
        "minimum_required_passes": compile_report.get("minimum_required_passes"),
    }


def carry_forward_previous_witness(
    root: pathlib.Path,
    *,
    release: dict[str, Any],
    source: str,
    source_sha: str,
    title: str,
    evidence_manifest: str,
    latex_command: str,
    freeze_date: str,
    source_date_epoch: str,
    reason: str,
) -> dict[str, Any] | None:
    path = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    if not path.exists():
        return None
    try:
        old = load_json(path)
    except Exception:
        return None
    if not witness_has_clean_compile_evidence(old, source=source, source_sha=source_sha, evidence_manifest=evidence_manifest, freeze_date=freeze_date):
        return None
    old_compile = compile_report_from_witness(old)
    old_toolchain = old.get("toolchain", {}) if isinstance(old.get("toolchain"), dict) else {}
    witness = {
        "version": 3,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "witness_type": "carried_forward_source_bound_clean_latex_compile_witness",
        "compile_gate_status": "pending_current_toolchain_refresh",
        "compiled_for_revision": old.get("generated_for_revision"),
        "compiled_bundle": old.get("checked_bundle"),
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "evidence_pack_manifest": evidence_manifest,
        "toolchain": {
            "latex_command": latex_command,
            "latex_command_path": old_toolchain.get("latex_command_path"),
            "current_latex_command_path": shutil.which(latex_command),
            "version_line": old_toolchain.get("version_line", ""),
            "version_output_sha256": old_toolchain.get("version_output_sha256", ""),
            "current_version_line": toolchain_version_record(latex_command).get("version_line", ""),
            "current_version_output_sha256": toolchain_version_record(latex_command).get("version_output_sha256", ""),
            "run_count": old_compile.get("run_count"),
            "source_date_epoch": source_date_epoch,
            "source_date_epoch_required_for_current_gate": True,
            "deterministic_pdf_environment_required_for_current_gate": True,
            "note": "Clean compile evidence was carried forward because the selected source hash is unchanged, but the current publication compile gate remains pending until a TeX-equipped environment refreshes the witness with SOURCE_DATE_EPOCH.",
        },
        "preflight_report": old.get("preflight_report", {}),
        "carried_forward_reason": reason,
        "non_authorization_notice": "This carried-forward compile evidence does not close the current clean-compile publication gate; it documents a prior source-bound clean compile only.",
    }
    path.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "pass",
        "written": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "mode": "carried_forward_previous_source_bound_witness",
        "compile_gate_status": witness["compile_gate_status"],
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "compiled_for_revision": witness["compiled_for_revision"],
        "source_tex": source,
        "source_sha256": source_sha,
        "output_pdf_sha256": old_compile.get("output_pdf_sha256"),
        "output_pdf_bytes": old_compile.get("output_pdf_bytes"),
        "final_warning_count": old_compile.get("final_warning_count"),
        "final_rerun_warning_count": old_compile.get("final_rerun_warning_count"),
        "run_count": old_compile.get("run_count"),
        "minimum_required_passes": old_compile.get("minimum_required_passes"),
        "reason": reason,
    }


def write_pending_unstaged_witness(
    root: pathlib.Path,
    *,
    release: dict[str, Any],
    source: str,
    source_sha: str,
    title: str,
    latex_command: str,
    reason: str,
) -> dict[str, Any]:
    """Bind the singleton witness to the recommendation without fabricating a compile.

    Evidence attachment is now an explicit operator action.  When queue order
    advances to an unstaged source, rebuild records a pending witness rather
    than auto-creating an evidence pack and freeze packet.  This keeps the
    control surface current while preventing registry/file growth from being
    mistaken for substantive review progress.
    """
    version_record = toolchain_version_record(latex_command)
    witness = {
        "version": 4,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "witness_type": "pending_unstaged_source_no_compile_attempt",
        "compile_gate_status": "pending_evidence_pack_attachment",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "evidence_pack_manifest": "",
        "toolchain": {
            "latex_command": latex_command,
            "latex_command_path": shutil.which(latex_command),
            "version_line": version_record.get("version_line", ""),
            "version_output_sha256": version_record.get("version_output_sha256", ""),
            "run_count": 0,
            "minimum_required_passes": minimum_compile_runs(latex_command),
            "source_date_epoch": source_date_epoch_from_manifest(release),
            "deterministic_pdf_environment": False,
            "note": "No compile was attempted because the selected queue source has no explicitly attached evidence lane.",
        },
        "preflight_report": {
            "status": "pending",
            "problems": [],
            "warnings": [reason],
            "details": {"compile": {"status": "not_run", "run_count": 0}},
        },
        "pending_reason": reason,
        "non_authorization_notice": "This pending witness blocks freeze and publication; it does not claim compile evidence.",
    }
    out = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    out.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "pass",
        "written": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "mode": "pending_unstaged_source_no_compile_attempt",
        "compile_gate_status": witness["compile_gate_status"],
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "source_tex": source,
        "source_sha256": source_sha,
        "reason": reason,
    }


def build(root: pathlib.Path, latex_command: str, *, force_compile: bool = False) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    readiness = rr.check(root)
    recommendation = readiness.get("next_release_recommendation", {}) if isinstance(readiness.get("next_release_recommendation"), dict) else {}
    if recommendation.get("status") != "static_pass_candidate_available":
        raise RuntimeError("no static-pass next release recommendation available")

    source = str(recommendation.get("source_tex", ""))
    source_sha = str(recommendation.get("source_sha256", ""))
    title = str(recommendation.get("title", ""))
    if not source or not source_sha or not title:
        raise RuntimeError("next-release recommendation is incomplete")
    source_path = root / source
    if not source_path.exists():
        raise RuntimeError(f"selected source missing: {source}")
    actual_sha = sha256_file(source_path)
    if actual_sha != source_sha:
        raise RuntimeError(f"selected source hash drift: {source_sha} != {actual_sha}")

    try:
        evidence_manifest, evidence_pack_root = evidence_manifest_for_source(root, source, source_sha)
    except RuntimeError as exc:
        return write_pending_unstaged_witness(
            root,
            release=release,
            source=source,
            source_sha=source_sha,
            title=title,
            latex_command=latex_command,
            reason=str(exc),
        )
    freeze_date = freeze_date_from_manifest(release)
    source_date_epoch = source_date_epoch_from_manifest(release)

    if not force_compile:
        reused = reusable_current_witness(
            root,
            release=release,
            source=source,
            source_sha=source_sha,
            evidence_manifest=evidence_manifest,
            latex_command=latex_command,
            freeze_date=freeze_date,
            source_date_epoch=source_date_epoch,
        )
        if reused is not None:
            return reused

    latex_path = shutil.which(latex_command)
    version_record = toolchain_version_record(latex_command)
    if latex_path is None:
        carried = carry_forward_previous_witness(
            root,
            release=release,
            source=source,
            source_sha=source_sha,
            title=title,
            evidence_manifest=evidence_manifest,
            latex_command=latex_command,
            freeze_date=freeze_date,
            source_date_epoch=source_date_epoch,
            reason=f"{latex_command} not found on PATH; carried forward prior source-bound clean compile evidence and reopened the current compile gate",
        )
        if carried is not None:
            return carried
        raise RuntimeError(f"{latex_command} not found on PATH and no source-bound prior witness could be carried forward")

    preflight = run_compile_preflight(
        root,
        freeze_date=freeze_date,
        title=title,
        source=source,
        source_sha=source_sha,
        evidence_pack_root=evidence_pack_root,
        latex_command=latex_command,
        source_date_epoch=source_date_epoch,
    )
    compile_report = preflight.get("details", {}).get("compile", {}) if isinstance(preflight.get("details"), dict) else {}
    if preflight.get("status") != "pass" or preflight.get("problems"):
        raise RuntimeError("compile preflight did not pass: " + json.dumps(preflight.get("problems", []))[:500])
    command = str(compile_report.get("command", latex_command))
    required_runs = minimum_compile_runs(command)
    if int(compile_report.get("run_count", 0)) < required_runs:
        raise RuntimeError(f"compile report used {compile_report.get('run_count')} {command} passes; required at least {required_runs}")
    if compile_report.get("status") != "pass" or int(compile_report.get("final_warning_count", 999)) != 0 or int(compile_report.get("final_rerun_warning_count", 999)) != 0:
        raise RuntimeError("compile report is not clean")

    witness = {
        "version": 3,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "witness_type": "source_bound_deterministic_clean_latex_compile_in_temporary_copy",
        "compile_gate_status": "pass",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "evidence_pack_manifest": evidence_manifest,
        "toolchain": {
            "latex_command": latex_command,
            "latex_command_path": latex_path,
            "version_line": version_record.get("version_line", ""),
            "version_output_sha256": version_record.get("version_output_sha256", ""),
            "run_count": compile_report.get("run_count"),
            "minimum_required_passes": compile_report.get("minimum_required_passes"),
            "final_rerun_warning_count": compile_report.get("final_rerun_warning_count"),
            "source_date_epoch": source_date_epoch,
            "deterministic_pdf_environment": True,
            "note": "The generated PDF was compiled in a temporary directory with SOURCE_DATE_EPOCH and is intentionally not shipped in the source-first archive.",
        },
        "preflight_report": preflight,
        "non_authorization_notice": "This compile witness resolves only the clean-compile freeze gate. It does not publish the paper or authorize publication.",
    }
    out = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    out.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "pass",
        "written": "release_queue/FREEZE_COMPILE_WITNESS.json",
        "mode": "compiled_current_deterministic_witness",
        "compile_gate_status": "pass",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "source_tex": source,
        "source_sha256": source_sha,
        "output_pdf_sha256": compile_report.get("output_pdf_sha256"),
        "output_pdf_bytes": compile_report.get("output_pdf_bytes"),
        "final_warning_count": compile_report.get("final_warning_count"),
        "final_rerun_warning_count": compile_report.get("final_rerun_warning_count"),
        "run_count": compile_report.get("run_count"),
        "minimum_required_passes": compile_report.get("minimum_required_passes"),
        "source_date_epoch": source_date_epoch,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--latex-command", default="pdflatex", choices=["pdflatex", "latexmk"])
    parser.add_argument("--force-compile", action="store_true", help="ignore a current clean witness and re-run LaTeX")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    try:
        report = build(root, args.latex_command, force_compile=args.force_compile)
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
