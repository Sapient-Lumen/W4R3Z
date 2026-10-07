#!/usr/bin/env python3
"""Scan release decisions for explicit publish authorizations.

The template checker proves the required shape exists. This checker watches the
actual decision-note history. It passes with zero publish authorizations, and it
fails closed if a decision note says ``Publication action: publish`` but is not a
completed, current, source-hash-bound authorization that matches the freeze lane.
It does not itself authorize publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication_target as pt  # noqa: E402

FIELD_RE = re.compile(r"^\s*-?\s*([^:\n]+):\s*(.*?)\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"<[^>]+>|YYYY\.MM\.DD|YYYY-MM-DD_slug_title|series/\.\.\./paper\.tex|release_queue/(?:evidence_packs|freeze_packets)/<id>/|<dated-publish-decision>")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
PUBLISHED_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+(?:_[a-z0-9]+)*$")
MIN_PDFLATEX_COMPILE_PASSES = 3


def minimum_compile_runs(command: str) -> int:
    """Mirror the freeze-witness compile-pass policy used by the guards."""
    return MIN_PDFLATEX_COMPILE_PASSES if command == "pdflatex" else 1


REQUIRED_FIELDS = [
    "Publication action",
    "Publication date",
    "Source",
    "Source SHA-256",
    "Published name",
    "Published path",
    "Evidence pack manifest",
    "Compile witness",
    "Freeze packet manifest",
    "Queue note",
    "Public citation-head update",
    "Publication receipt",
    "Publication authorized by this completed note",
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_inside(root: pathlib.Path, rel: str) -> pathlib.Path | None:
    if not rel or rel.startswith("/"):
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        # A completed decision may use bullet fields; ignore code examples.
        if in_fence:
            continue
        m = FIELD_RE.match(line)
        if m:
            fields[m.group(1).strip()] = m.group(2).strip().strip("`")
    return fields


def decision_notes(root: pathlib.Path) -> list[pathlib.Path]:
    decisions = root / "release_queue" / "decisions"
    if not decisions.exists():
        return []
    return sorted(p for p in decisions.glob("*.md") if p.name != "README.md")


def report_for_publish_note(root: pathlib.Path, path: pathlib.Path, release: dict[str, Any]) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    fields = parse_fields(text)
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for field in REQUIRED_FIELDS:
        if field not in fields:
            failures.append({"category": "required_field_missing", "field": field})

    for token in sorted(set(PLACEHOLDER_RE.findall("\n".join(f"{k}: {v}" for k, v in fields.items())))):
        failures.append({"category": "placeholder_present", "token": token})

    action = fields.get("Publication action", "")
    if action != "publish":
        failures.append({"category": "publication_action_not_publish", "value": action})

    date = fields.get("Publication date", "")
    if date and not DATE_RE.match(date):
        failures.append({"category": "publication_date_malformed", "value": date})

    source_rel = fields.get("Source", "")
    source_path = rel_inside(root, source_rel)
    source_sha = fields.get("Source SHA-256", "")
    actual_source_sha = ""
    if source_path is None or not source_path.exists() or source_path.suffix != ".tex":
        failures.append({"category": "source_missing_or_not_tex", "source": source_rel})
    else:
        actual_source_sha = sha256_file(source_path)
        if source_sha != actual_source_sha:
            failures.append({"category": "source_sha256_mismatch", "declared": source_sha, "actual": actual_source_sha})
    if source_sha and not SHA_RE.match(source_sha):
        failures.append({"category": "source_sha256_malformed", "value": source_sha})

    published_name = fields.get("Published name", "")
    published_path = fields.get("Published path", "")
    if published_name and not PUBLISHED_NAME_RE.match(published_name):
        failures.append({"category": "published_name_malformed", "value": published_name})
    if date and published_name and not published_name.startswith(date.replace(".", "-") + "_"):
        failures.append({"category": "published_name_date_mismatch", "date": date, "published_name": published_name})
    if published_path:
        if published_path != f"published/{published_name}":
            failures.append({"category": "published_path_name_mismatch", "published_path": published_path, "published_name": published_name})
        if not pt.is_portable_published_path(published_path):
            failures.append({"category": "published_path_not_portable", "published_path": published_path})

    queue_note_rel = fields.get("Queue note", "")
    queue_note_path = rel_inside(root, queue_note_rel)
    allowed_queue_note_prefixes = ("release_queue/published_ready/", "release_queue/published/")
    if queue_note_path is None or not queue_note_path.exists() or not queue_note_rel.startswith(allowed_queue_note_prefixes):
        failures.append({"category": "queue_note_missing_or_not_release_lane", "path": queue_note_rel, "allowed_prefixes": list(allowed_queue_note_prefixes)})
    elif source_rel not in queue_note_path.read_text(encoding="utf-8", errors="replace"):
        warnings.append({"category": "queue_note_does_not_textually_name_source", "path": queue_note_rel, "source": source_rel})

    is_materialized, materialized_receipt_rel, materialized_failures, materialized_warnings = materialized_publication_receipt_report(root, rel, fields)
    if is_materialized:
        failures.extend(materialized_failures)
        warnings.extend(materialized_warnings)
        warnings.append({
            "category": "historical_publish_decision_already_materialized",
            "publication_receipt": materialized_receipt_rel,
            "note": "current release-lane evidence may advance after publication; the receipt, copied source, and copied compile snapshot are authoritative for this historical decision",
        })
        return {
            "decision_note": rel,
            "status": "pass" if not failures else "fail",
            "failure_count": len(failures),
            "warning_count": len(warnings),
            "fields_present": sorted(fields),
            "source_tex": source_rel,
            "source_sha256": source_sha,
            "source_current_sha256": actual_source_sha,
            "published_name": published_name,
            "evidence_pack_manifest": fields.get("Evidence pack manifest", ""),
            "compile_witness": fields.get("Compile witness", ""),
            "freeze_packet_manifest": fields.get("Freeze packet manifest", ""),
            "queue_note": queue_note_rel,
            "historical_materialized": True,
            "materialized_publication_receipt": materialized_receipt_rel,
            "failures": failures,
            "warnings": warnings,
        }

    evidence_rel = fields.get("Evidence pack manifest", "")
    evidence_path = rel_inside(root, evidence_rel)
    if evidence_path is None or not evidence_path.exists():
        failures.append({"category": "evidence_pack_missing_or_escapes_archive", "path": evidence_rel})
    else:
        evidence = load_json(evidence_path)
        if evidence.get("publication_authorized") is not False:
            failures.append({"category": "evidence_pack_publication_authorized_not_false", "value": evidence.get("publication_authorized")})
        if evidence.get("generated_for_revision") != release.get("revision") or evidence.get("checked_bundle") != release.get("bundle"):
            failures.append({"category": "evidence_pack_stale", "revision": evidence.get("generated_for_revision"), "bundle": evidence.get("checked_bundle")})
        if evidence.get("source_tex") != source_rel or evidence.get("source_sha256") != source_sha:
            failures.append({"category": "evidence_pack_not_source_bound", "source": evidence.get("source_tex"), "sha256": evidence.get("source_sha256")})

    compile_rel = fields.get("Compile witness", "")
    compile_path = rel_inside(root, compile_rel)
    if compile_path is None or not compile_path.exists():
        failures.append({"category": "compile_witness_missing_or_escapes_archive", "path": compile_rel})
    else:
        compile_witness = load_json(compile_path)
        compile_details = compile_witness.get("preflight_report", {}).get("details", {}).get("compile", {}) if isinstance(compile_witness.get("preflight_report"), dict) else {}
        if compile_witness.get("publication_authorized") is not False:
            failures.append({"category": "compile_witness_publication_authorized_not_false", "value": compile_witness.get("publication_authorized")})
        if compile_witness.get("generated_for_revision") != release.get("revision") or compile_witness.get("checked_bundle") != release.get("bundle"):
            failures.append({"category": "compile_witness_stale", "revision": compile_witness.get("generated_for_revision"), "bundle": compile_witness.get("checked_bundle")})
        if compile_witness.get("source_tex") != source_rel or compile_witness.get("source_sha256") != source_sha:
            failures.append({"category": "compile_witness_not_source_bound", "source": compile_witness.get("source_tex"), "sha256": compile_witness.get("source_sha256")})
        if compile_witness.get("compile_gate_status") != "pass" or compile_witness.get("preflight_report", {}).get("status") != "pass" or compile_details.get("status") != "pass":
            failures.append({"category": "compile_witness_gate_not_closed", "gate": compile_witness.get("compile_gate_status"), "preflight": compile_witness.get("preflight_report", {}).get("status"), "compile": compile_details.get("status")})
        if compile_details.get("deterministic_pdf_environment") is not True or not compile_details.get("source_date_epoch"):
            failures.append({"category": "compile_witness_missing_deterministic_environment", "source_date_epoch": compile_details.get("source_date_epoch")})
        witness_toolchain = compile_witness.get("toolchain", {}) if isinstance(compile_witness.get("toolchain"), dict) else {}
        command = str(compile_details.get("command", witness_toolchain.get("latex_command", "pdflatex")))
        required_runs = minimum_compile_runs(command)
        if int(compile_details.get("run_count", 0)) < required_runs:
            failures.append({"category": "compile_witness_run_count_below_required", "command": command, "run_count": compile_details.get("run_count"), "minimum_required": required_runs})
        if int(compile_details.get("minimum_required_passes", required_runs)) < required_runs:
            failures.append({"category": "compile_witness_minimum_required_passes_too_low", "command": command, "declared": compile_details.get("minimum_required_passes"), "minimum_required": required_runs})
        if int(compile_details.get("final_warning_count", 999)) != 0:
            failures.append({"category": "compile_witness_final_warnings", "final_warning_count": compile_details.get("final_warning_count")})
        if int(compile_details.get("final_rerun_warning_count", 999)) != 0:
            failures.append({"category": "compile_witness_final_rerun_warnings", "final_rerun_warning_count": compile_details.get("final_rerun_warning_count")})

    freeze_rel = fields.get("Freeze packet manifest", "")
    freeze_path = rel_inside(root, freeze_rel)
    if freeze_path is None or not freeze_path.exists():
        failures.append({"category": "freeze_packet_missing_or_escapes_archive", "path": freeze_rel})
    else:
        freeze_packet = load_json(freeze_path)
        if freeze_packet.get("publication_authorized") is not False:
            failures.append({"category": "freeze_packet_publication_authorized_not_false", "value": freeze_packet.get("publication_authorized")})
        if freeze_packet.get("generated_for_revision") != release.get("revision") or freeze_packet.get("checked_bundle") != release.get("bundle"):
            failures.append({"category": "freeze_packet_stale", "revision": freeze_packet.get("generated_for_revision"), "bundle": freeze_packet.get("checked_bundle")})
        if freeze_packet.get("source_tex") != source_rel or freeze_packet.get("source_sha256") != source_sha:
            failures.append({"category": "freeze_packet_not_source_bound", "source": freeze_packet.get("source_tex"), "sha256": freeze_packet.get("source_sha256")})
        allowed_compile_witness_bindings = {str(freeze_packet.get("compile_witness", "")), str(freeze_packet.get("compile_witness_snapshot", ""))}
        if freeze_packet.get("evidence_pack_manifest") != evidence_rel or compile_rel not in allowed_compile_witness_bindings:
            failures.append({"category": "freeze_packet_binding_mismatch", "evidence": freeze_packet.get("evidence_pack_manifest"), "compile": freeze_packet.get("compile_witness"), "compile_snapshot": freeze_packet.get("compile_witness_snapshot"), "decision_compile_witness": compile_rel})
        snapshot_rel = str(freeze_packet.get("compile_witness_snapshot", ""))
        snapshot_path = rel_inside(root, snapshot_rel)
        snapshot_sha = str(freeze_packet.get("compile_witness_snapshot_sha256", ""))
        if snapshot_path is None or not snapshot_path.exists():
            failures.append({"category": "freeze_packet_compile_snapshot_missing", "path": snapshot_rel})
        else:
            actual_snapshot_sha = sha256_file(snapshot_path)
            if actual_snapshot_sha != snapshot_sha:
                failures.append({"category": "freeze_packet_compile_snapshot_sha256_mismatch", "expected": snapshot_sha, "actual": actual_snapshot_sha})
            snapshot = load_json(snapshot_path)
            snapshot_compile = snapshot.get("preflight_report", {}).get("details", {}).get("compile", {}) if isinstance(snapshot.get("preflight_report"), dict) else {}
            if snapshot.get("source_tex") != source_rel or snapshot.get("source_sha256") != source_sha:
                failures.append({"category": "freeze_packet_compile_snapshot_not_source_bound", "source": snapshot.get("source_tex"), "sha256": snapshot.get("source_sha256")})
            if snapshot.get("generated_for_revision") != release.get("revision") or snapshot.get("checked_bundle") != release.get("bundle"):
                failures.append({"category": "freeze_packet_compile_snapshot_stale", "revision": snapshot.get("generated_for_revision"), "bundle": snapshot.get("checked_bundle")})
            if snapshot.get("compile_gate_status") != "pass" or snapshot.get("preflight_report", {}).get("status") != "pass" or snapshot_compile.get("status") != "pass":
                failures.append({"category": "freeze_packet_compile_snapshot_gate_not_closed", "gate": snapshot.get("compile_gate_status"), "preflight": snapshot.get("preflight_report", {}).get("status"), "compile": snapshot_compile.get("status")})
            snapshot_toolchain = snapshot.get("toolchain", {}) if isinstance(snapshot.get("toolchain"), dict) else {}
            snapshot_command = str(snapshot_compile.get("command", snapshot_toolchain.get("latex_command", "pdflatex")))
            snapshot_required_runs = minimum_compile_runs(snapshot_command)
            if int(snapshot_compile.get("run_count", 0)) < snapshot_required_runs:
                failures.append({"category": "freeze_packet_compile_snapshot_run_count_below_required", "command": snapshot_command, "run_count": snapshot_compile.get("run_count"), "minimum_required": snapshot_required_runs})
            if int(snapshot_compile.get("minimum_required_passes", snapshot_required_runs)) < snapshot_required_runs:
                failures.append({"category": "freeze_packet_compile_snapshot_minimum_required_passes_too_low", "command": snapshot_command, "declared": snapshot_compile.get("minimum_required_passes"), "minimum_required": snapshot_required_runs})
            if int(snapshot_compile.get("final_rerun_warning_count", 999)) != 0:
                failures.append({"category": "freeze_packet_compile_snapshot_final_rerun_warnings", "final_rerun_warning_count": snapshot_compile.get("final_rerun_warning_count")})
            if snapshot_compile.get("deterministic_pdf_environment") is not True or not snapshot_compile.get("source_date_epoch"):
                failures.append({"category": "freeze_packet_compile_snapshot_missing_deterministic_environment", "source_date_epoch": snapshot_compile.get("source_date_epoch")})

    if fields.get("Public citation-head update", "") != "required":
        failures.append({"category": "citation_head_update_field_not_required", "value": fields.get("Public citation-head update", "")})
    if not fields.get("Publication receipt", "").startswith("required"):
        failures.append({"category": "publication_receipt_field_not_required", "value": fields.get("Publication receipt", "")})
    if fields.get("Publication authorized by this completed note", "") != "true":
        failures.append({"category": "completed_note_authorization_field_not_true", "value": fields.get("Publication authorized by this completed note", "")})

    return {
        "decision_note": rel,
        "status": "pass" if not failures else "fail",
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "fields_present": sorted(fields),
        "source_tex": source_rel,
        "source_sha256": source_sha,
        "source_current_sha256": actual_source_sha,
        "published_name": published_name,
        "evidence_pack_manifest": evidence_rel,
        "compile_witness": compile_rel,
        "freeze_packet_manifest": freeze_rel,
        "queue_note": queue_note_rel,
        "failures": failures,
        "warnings": warnings,
    }




def materialized_publication_receipt_report(root: pathlib.Path, decision_rel: str, fields: dict[str, str]) -> tuple[bool, str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Return whether an older publish decision has already been materialized.

    Historical publication decisions are durable evidence, not fresh authority for
    the current release lane.  Once a published entry carries a receipt that
    binds the decision note, source hash, copied source, freeze packet, and
    compile snapshot, later revisions may advance the live evidence/compile
    singleton without making the old decision stale or unsafe.
    """
    warnings: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    published_name = fields.get("Published name", "")
    published_path = fields.get("Published path", "")
    if not published_name or not published_path:
        return False, "", [], []
    receipt_rel = f"{published_path.rstrip('/')}/PUBLICATION_RECEIPT.json"
    receipt_path = rel_inside(root, receipt_rel)
    if receipt_path is None or not receipt_path.exists():
        return False, receipt_rel, [], []
    try:
        receipt = load_json(receipt_path)
    except Exception as exc:  # pragma: no cover - defensive corruption report
        return True, receipt_rel, [{"category": "publication_receipt_unreadable", "path": receipt_rel, "error": str(exc)}], warnings

    expected_pairs = {
        "published_name": fields.get("Published name", ""),
        "published_path": fields.get("Published path", ""),
        "source_tex": fields.get("Source", ""),
        "source_sha256": fields.get("Source SHA-256", ""),
        "decision_note": decision_rel,
        "evidence_pack_manifest": fields.get("Evidence pack manifest", ""),
        "freeze_packet_manifest": fields.get("Freeze packet manifest", ""),
    }
    for key, expected in expected_pairs.items():
        if str(receipt.get(key, "")) != expected:
            failures.append({"category": "publication_receipt_binding_mismatch", "key": key, "expected": expected, "actual": receipt.get(key)})
    if receipt.get("publication_authorized") is not True:
        failures.append({"category": "publication_receipt_not_authorizing_materialized_entry", "value": receipt.get("publication_authorized")})

    published_tex_rel = str(receipt.get("published_tex", ""))
    published_tex_path = rel_inside(root, published_tex_rel)
    if published_tex_path is None or not published_tex_path.exists():
        failures.append({"category": "published_tex_missing_or_escapes_archive", "path": published_tex_rel})
    else:
        published_tex_sha = sha256_file(published_tex_path)
        expected_sha = fields.get("Source SHA-256", "")
        if published_tex_sha != expected_sha or published_tex_sha != receipt.get("published_tex_sha256"):
            failures.append({"category": "published_tex_sha256_mismatch", "path": published_tex_rel, "actual": published_tex_sha, "source_sha256": expected_sha, "receipt_sha256": receipt.get("published_tex_sha256")})

    snapshot_rel = str(receipt.get("published_compile_witness_snapshot", ""))
    snapshot_path = rel_inside(root, snapshot_rel)
    if snapshot_path is None or not snapshot_path.exists():
        failures.append({"category": "published_compile_snapshot_missing_or_escapes_archive", "path": snapshot_rel})
    else:
        snapshot_sha = sha256_file(snapshot_path)
        if snapshot_sha != receipt.get("published_compile_witness_snapshot_sha256"):
            failures.append({"category": "published_compile_snapshot_sha256_mismatch", "path": snapshot_rel, "actual": snapshot_sha, "receipt_sha256": receipt.get("published_compile_witness_snapshot_sha256")})

    compile_rel = fields.get("Compile witness", "")
    if compile_rel and compile_rel != str(receipt.get("compile_witness", "")):
        warnings.append({"category": "decision_compile_witness_field_differs_from_receipt", "decision_compile_witness": compile_rel, "receipt_compile_witness": receipt.get("compile_witness"), "note": "historical receipt remains authoritative for the materialized publication"})
    return True, receipt_rel, failures, warnings

def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    notes = decision_notes(root)
    publish_notes: list[dict[str, Any]] = []
    for path in notes:
        text = path.read_text(encoding="utf-8", errors="replace")
        fields = parse_fields(text)
        if fields.get("Publication action") == "publish":
            publish_notes.append(report_for_publish_note(root, path, release))

    failures: list[dict[str, Any]] = []
    for note in publish_notes:
        if note["status"] != "pass":
            failures.append({"decision_note": note["decision_note"], "category": "publish_decision_not_gate_closed", "failure_count": note["failure_count"], "failures": note["failures"][:20]})

    completed_valid = [note for note in publish_notes if note["status"] == "pass"]
    materialized_valid = []
    for note in completed_valid:
        receipt_path = root / "published" / str(note.get("published_name", "")) / "PUBLICATION_RECEIPT.json"
        if note.get("historical_materialized") is True or receipt_path.exists():
            materialized_valid.append(note)
    active_valid = [note for note in completed_valid if note not in materialized_valid]
    ready_to_execute = len(active_valid) == 1 and not failures
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "decision_scan_type": "explicit_publish_authorization_scan",
        "decision_directory": "release_queue/decisions",
        "publish_decisions": publish_notes,
        "summary": {
            "decision_note_count": len(notes),
            "publish_decision_count": len(publish_notes),
            "valid_publish_decision_count": len(completed_valid),
            "active_publish_decision_count": len(active_valid),
            "checks_failed": len(failures),
            "materialized_publish_decision_count": len(materialized_valid),
            "ready_to_execute_guarded_publication_helper": ready_to_execute,
        },
        "failures": failures[:50],
        "fail_closed_rule": "If any real decision note contains a publish authorization, it must be complete, current, source-hash-bound, and aligned with evidence, compile, and freeze-packet gates before publication can proceed.",
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
