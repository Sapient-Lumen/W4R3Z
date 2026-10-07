#!/usr/bin/env python3
"""Verify non-public release freeze packet integrity.

The checker treats the per-packet compile-witness snapshot as the durable compile
binding.  The live singleton witness may be regenerated as the freeze lane moves;
that should not silently change the evidence attached to an already materialized
freeze packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

MIN_PDFLATEX_COMPILE_PASSES = 3

def minimum_compile_runs(command: str) -> int:
    return MIN_PDFLATEX_COMPILE_PASSES if command == "pdflatex" else 1


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


def compile_details(snapshot: dict[str, Any]) -> dict[str, Any]:
    preflight = snapshot.get("preflight_report") if isinstance(snapshot.get("preflight_report"), dict) else {}
    details = preflight.get("details") if isinstance(preflight.get("details"), dict) else {}
    comp = details.get("compile") if isinstance(details.get("compile"), dict) else {}
    return comp


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    registry_path = root / "release_queue" / "FREEZE_PACKET_REGISTRY.json"
    evidence_report = load_json(root / "reports" / "evidence_pack_integrity.json") if (root / "reports" / "evidence_pack_integrity.json").exists() else {}
    compile_report = load_json(root / "reports" / "freeze_compile_witness.json") if (root / "reports" / "freeze_compile_witness.json").exists() else {}
    plan = load_json(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json") if (root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json").exists() else {}
    published_freeze_packet_manifests: dict[str, str] = {}
    published_root = root / "published"
    if published_root.exists():
        for receipt_path in published_root.glob("*/PUBLICATION_RECEIPT.json"):
            try:
                receipt = load_json(receipt_path)
            except Exception:
                continue
            manifest_rel = str(receipt.get("freeze_packet_manifest", ""))
            if manifest_rel:
                published_freeze_packet_manifests[manifest_rel] = receipt_path.relative_to(root).as_posix()
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    entry_reports: list[dict[str, Any]] = []

    if not registry_path.exists():
        return {
            "status": "pass",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "registry_present": False,
            "entries": [],
            "summary": {"registry_entry_count": 0, "materialized_entry_count": 0, "unregistered_packet_dir_count": 0, "checks_failed": 0},
            "fail_closed_rule": "No freeze-packet registry means no staged freeze packet exists; publication remains blocked by the execution gate.",
        }

    registry = load_json(registry_path)
    if registry.get("publication_authorized") is not False:
        failures.append({"category": "registry_publication_authorized_not_false"})
    if registry.get("generated_for_revision") != release["revision"]:
        failures.append({"category": "registry_revision_mismatch", "registry": registry.get("generated_for_revision"), "current": release["revision"]})
    if registry.get("checked_bundle") != release["bundle"]:
        failures.append({"category": "registry_bundle_mismatch", "registry": registry.get("checked_bundle"), "current": release["bundle"]})

    registered_manifests = {str(entry.get("manifest", "")) for entry in registry.get("entries", []) if isinstance(entry, dict)}
    packet_root = root / "release_queue" / "freeze_packets"
    actual_manifests = {p.relative_to(root).as_posix() for p in packet_root.glob("*/FREEZE_PACKET_MANIFEST.json")} if packet_root.exists() else set()
    unregistered = sorted(actual_manifests - registered_manifests)
    for rel in unregistered:
        failures.append({"category": "unregistered_freeze_packet_manifest", "path": rel})

    for entry in registry.get("entries", []):
        if not isinstance(entry, dict):
            failures.append({"category": "malformed_registry_entry", "entry": repr(entry)[:200]})
            continue
        entry_failures: list[dict[str, Any]] = []
        entry_warnings: list[dict[str, Any]] = []
        manifest_rel = str(entry.get("manifest", ""))
        manifest_path = rel_inside(root, manifest_rel)
        manifest: dict[str, Any] = {}
        snapshot_rel = str(entry.get("compile_witness_snapshot", ""))
        snapshot_sha = str(entry.get("compile_witness_snapshot_sha256", ""))
        snapshot: dict[str, Any] = {}
        target_rel_for_publication = str(entry.get("prospective_target", ""))
        target_receipt_path = rel_inside(root, target_rel_for_publication.rstrip("/") + "/PUBLICATION_RECEIPT.json") if target_rel_for_publication else None
        published_receipt = published_freeze_packet_manifests.get(manifest_rel)
        is_historical_published_packet = bool(published_receipt or (target_receipt_path is not None and target_receipt_path.exists()))

        if manifest_path is None or not manifest_path.exists():
            entry_failures.append({"category": "manifest_missing_or_escapes_archive", "path": manifest_rel})
        else:
            manifest = load_json(manifest_path)
            if manifest.get("publication_authorized") is not False:
                entry_failures.append({"category": "manifest_publication_authorized_not_false"})
            if manifest.get("generated_for_revision") != release["revision"] or manifest.get("checked_bundle") != release["bundle"]:
                if is_historical_published_packet:
                    entry_warnings.append({
                        "category": "historical_manifest_revision_or_bundle_mismatch",
                        "manifest_revision": manifest.get("generated_for_revision"),
                        "manifest_bundle": manifest.get("checked_bundle"),
                        "current_revision": release["revision"],
                        "current_bundle": release["bundle"],
                        "publication_receipt": published_receipt or (target_receipt_path.relative_to(root).as_posix() if target_receipt_path is not None and target_receipt_path.exists() else ""),
                        "note": "published freeze packets are historical evidence; their manifest remains bound to the publication revision",
                    })
                else:
                    entry_failures.append({"category": "manifest_revision_or_bundle_mismatch", "manifest_revision": manifest.get("generated_for_revision"), "manifest_bundle": manifest.get("checked_bundle")})
            for key in ["freeze_packet_id", "source_tex", "source_sha256", "title", "decision_note", "prospective_target", "evidence_pack_manifest", "compile_witness", "compile_witness_snapshot", "compile_witness_snapshot_sha256"]:
                if str(manifest.get(key, "")) != str(entry.get(key, "")):
                    if key == "decision_note" and is_historical_published_packet and str(entry.get(key, "")).startswith("release_queue/published/") and str(manifest.get(key, "")).startswith("release_queue/published_ready/"):
                        entry_warnings.append({
                            "category": "historical_queue_note_moved_after_freeze",
                            "entry_decision_note": entry.get(key),
                            "manifest_decision_note": manifest.get(key),
                            "publication_receipt": published_receipt or (target_receipt_path.relative_to(root).as_posix() if target_receipt_path is not None and target_receipt_path.exists() else ""),
                            "note": "the freeze packet remains bound to the original published-ready decision note; the registry tracks the later published queue-note location",
                        })
                        continue
                    entry_failures.append({"category": "entry_manifest_mismatch", "key": key, "entry": entry.get(key), "manifest": manifest.get(key)})
            snapshot_rel = str(manifest.get("compile_witness_snapshot", snapshot_rel))
            snapshot_sha = str(manifest.get("compile_witness_snapshot_sha256", snapshot_sha))

            source_rel = str(entry.get("source_tex", ""))
            source_path = rel_inside(root, source_rel)
            if source_path is None or not source_path.exists():
                entry_failures.append({"category": "source_missing_or_escapes_archive", "source_tex": source_rel})
            else:
                actual_source_sha = sha256_file(source_path)
                if actual_source_sha != entry.get("source_sha256") or actual_source_sha != manifest.get("source_sha256"):
                    entry_failures.append({"category": "source_sha256_mismatch", "actual": actual_source_sha, "entry": entry.get("source_sha256"), "manifest": manifest.get("source_sha256")})

            frozen_source_rel = str(manifest.get("frozen_source_path", ""))
            frozen_source_path = rel_inside(root, frozen_source_rel)
            if frozen_source_path is None or not frozen_source_path.exists():
                entry_failures.append({"category": "frozen_source_missing_or_escapes_archive", "path": frozen_source_rel})
            else:
                frozen_sha = sha256_file(frozen_source_path)
                if frozen_sha != manifest.get("frozen_source_sha256") or frozen_sha != entry.get("source_sha256"):
                    entry_failures.append({"category": "frozen_source_sha256_mismatch", "path": frozen_source_rel, "actual": frozen_sha, "manifest": manifest.get("frozen_source_sha256"), "source": entry.get("source_sha256")})

            for digest_key, rel_key in [
                ("evidence_pack_manifest_sha256", "evidence_pack_manifest"),
                ("freeze_plan_sha256", "freeze_plan"),
            ]:
                rel = str(manifest.get(rel_key, ""))
                path = rel_inside(root, rel)
                if path is None or not path.exists():
                    entry_failures.append({"category": "bound_surface_missing_or_escapes_archive", "path": rel, "role": rel_key})
                    continue
                actual = sha256_file(path)
                if actual != manifest.get(digest_key):
                    if is_historical_published_packet and rel_key == "freeze_plan":
                        entry_warnings.append({
                            "category": "historical_freeze_plan_has_moved",
                            "path": rel,
                            "expected": manifest.get(digest_key),
                            "actual": actual,
                            "publication_receipt": published_receipt or target_receipt_path.relative_to(root).as_posix(),
                            "note": "published packets are bound to their stored manifest and compile snapshot; the live next-release freeze plan may advance",
                        })
                    else:
                        entry_failures.append({"category": "bound_surface_sha256_mismatch", "path": rel, "expected": manifest.get(digest_key), "actual": actual})

            snapshot_path = rel_inside(root, snapshot_rel)
            if snapshot_path is None or not snapshot_path.exists():
                entry_failures.append({"category": "compile_witness_snapshot_missing_or_escapes_archive", "path": snapshot_rel})
            else:
                actual_snapshot_sha = sha256_file(snapshot_path)
                if actual_snapshot_sha != snapshot_sha:
                    entry_failures.append({"category": "compile_witness_snapshot_sha256_mismatch", "path": snapshot_rel, "expected": snapshot_sha, "actual": actual_snapshot_sha})
                snapshot = load_json(snapshot_path)
                if snapshot.get("publication_authorized") is not False:
                    entry_failures.append({"category": "compile_witness_snapshot_publication_authorized_not_false", "value": snapshot.get("publication_authorized")})
                if snapshot.get("generated_for_revision") != manifest.get("generated_for_revision") or snapshot.get("checked_bundle") != manifest.get("checked_bundle"):
                    entry_failures.append({"category": "compile_witness_snapshot_revision_or_bundle_mismatch", "snapshot_revision": snapshot.get("generated_for_revision"), "snapshot_bundle": snapshot.get("checked_bundle"), "manifest_revision": manifest.get("generated_for_revision"), "manifest_bundle": manifest.get("checked_bundle")})
                if snapshot.get("source_tex") != entry.get("source_tex") or snapshot.get("source_sha256") != entry.get("source_sha256"):
                    entry_failures.append({"category": "compile_witness_snapshot_not_source_bound", "snapshot_source": snapshot.get("source_tex"), "snapshot_sha": snapshot.get("source_sha256")})
                if str(snapshot.get("compile_gate_status", "")) != str(manifest.get("compile_gate_status", "")):
                    entry_failures.append({"category": "compile_witness_snapshot_gate_mismatch", "snapshot": snapshot.get("compile_gate_status"), "manifest": manifest.get("compile_gate_status")})
                comp = compile_details(snapshot)
                if snapshot.get("compile_gate_status") == "pass":
                    if snapshot.get("preflight_report", {}).get("status") != "pass" or comp.get("status") != "pass":
                        entry_failures.append({"category": "compile_witness_snapshot_preflight_or_compile_not_pass", "preflight": snapshot.get("preflight_report", {}).get("status"), "compile": comp.get("status")})
                    snap_toolchain = snapshot.get("toolchain", {}) if isinstance(snapshot.get("toolchain"), dict) else {}
                    command = str(comp.get("command", snap_toolchain.get("latex_command", "pdflatex")))
                    required_runs = minimum_compile_runs(command)
                    if int(comp.get("run_count", 0)) < required_runs:
                        entry_failures.append({"category": "compile_witness_snapshot_run_count_below_required", "command": command, "run_count": comp.get("run_count"), "minimum_required": required_runs})
                    if int(comp.get("minimum_required_passes", required_runs)) < required_runs:
                        entry_failures.append({"category": "compile_witness_snapshot_minimum_required_passes_too_low", "command": command, "declared": comp.get("minimum_required_passes"), "minimum_required": required_runs})
                    if int(comp.get("final_warning_count", 999)) != 0:
                        entry_failures.append({"category": "compile_witness_snapshot_final_warnings", "final_warning_count": comp.get("final_warning_count")})
                    if int(comp.get("final_rerun_warning_count", 999)) != 0:
                        entry_failures.append({"category": "compile_witness_snapshot_final_rerun_warnings", "final_rerun_warning_count": comp.get("final_rerun_warning_count")})
                    if comp.get("deterministic_pdf_environment") is not True or not comp.get("source_date_epoch"):
                        entry_failures.append({"category": "compile_witness_snapshot_missing_deterministic_environment", "source_date_epoch": comp.get("source_date_epoch")})
                    if not snap_toolchain.get("version_line") or not snap_toolchain.get("version_output_sha256"):
                        entry_failures.append({"category": "compile_witness_snapshot_missing_toolchain_fingerprint"})
                    if manifest.get("compile_output_pdf_sha256") and comp.get("output_pdf_sha256") and manifest.get("compile_output_pdf_sha256") != comp.get("output_pdf_sha256"):
                        entry_failures.append({"category": "compile_output_pdf_sha256_mismatch", "manifest": manifest.get("compile_output_pdf_sha256"), "snapshot": comp.get("output_pdf_sha256")})

            live_rel = str(manifest.get("compile_witness", ""))
            live_path = rel_inside(root, live_rel)
            if live_path is None or not live_path.exists():
                entry_warnings.append({"category": "live_compile_witness_missing", "path": live_rel, "note": "packet snapshot remains authoritative"})
            else:
                live_sha = sha256_file(live_path)
                if manifest.get("compile_witness_sha256_at_freeze") and live_sha != manifest.get("compile_witness_sha256_at_freeze"):
                    entry_warnings.append({"category": "live_compile_witness_has_moved", "path": live_rel, "sha256_at_freeze": manifest.get("compile_witness_sha256_at_freeze"), "current_sha256": live_sha, "note": "packet snapshot remains authoritative"})

            seen_snapshot_role = False
            for row in manifest.get("packet_paths", []):
                if not isinstance(row, dict):
                    entry_failures.append({"category": "malformed_packet_path_row", "row": repr(row)[:200]})
                    continue
                rel = str(row.get("path", ""))
                path = rel_inside(root, rel)
                if path is None or not path.exists():
                    entry_failures.append({"category": "packet_path_missing_or_escapes_archive", "path": rel})
                    continue
                actual = sha256_file(path)
                if actual != row.get("sha256"):
                    entry_failures.append({"category": "packet_path_sha256_mismatch", "path": rel, "expected": row.get("sha256"), "actual": actual})
                root_prefix = str(manifest.get("freeze_packet_root", "")).rstrip("/") + "/"
                if root_prefix != "/" and not rel.startswith(root_prefix):
                    entry_failures.append({"category": "packet_path_outside_packet_root", "path": rel, "root": manifest.get("freeze_packet_root")})
                if row.get("role") == "source_bound_compile_witness_snapshot":
                    seen_snapshot_role = True
            if not seen_snapshot_role:
                entry_failures.append({"category": "compile_witness_snapshot_not_listed_in_packet_paths"})

            if evidence_report.get("status") != "pass":
                entry_failures.append({"category": "evidence_integrity_report_not_pass", "status": evidence_report.get("status")})
            if compile_report.get("status") == "pass" and compile_report.get("selected_source") == entry.get("source_tex"):
                if compile_report.get("selected_source_sha256") != entry.get("source_sha256"):
                    entry_failures.append({"category": "current_compile_report_sha_mismatch", "compile_sha": compile_report.get("selected_source_sha256"), "entry_sha": entry.get("source_sha256")})
                if manifest.get("compile_gate_status") and manifest.get("compile_gate_status") != compile_report.get("compile_gate_status"):
                    entry_warnings.append({"category": "current_compile_report_gate_differs_from_packet_snapshot", "manifest": manifest.get("compile_gate_status"), "compile_report": compile_report.get("compile_gate_status")})
            selected = plan.get("selected_source") if isinstance(plan.get("selected_source"), dict) else {}
            if selected and (selected.get("source_tex") != entry.get("source_tex") or selected.get("source_sha256") != entry.get("source_sha256")):
                entry_warnings.append({"category": "current_freeze_plan_points_elsewhere", "plan_source": selected.get("source_tex"), "plan_sha": selected.get("source_sha256"), "note": "packet snapshot remains source-bound"})
            target_rel = str(entry.get("prospective_target", ""))
            if target_rel and (root / target_rel).exists():
                if is_historical_published_packet:
                    entry_warnings.append({
                        "category": "prospective_target_now_published",
                        "target": target_rel,
                        "publication_receipt": published_receipt or (target_receipt_path.relative_to(root).as_posix() if target_receipt_path is not None and target_receipt_path.exists() else ""),
                        "note": "the packet is now historical publication evidence rather than a pending freeze packet",
                    })
                else:
                    entry_failures.append({"category": "prospective_target_already_exists_in_published", "target": target_rel})

        entry_report = {
            "freeze_packet_id": entry.get("freeze_packet_id"),
            "source_tex": entry.get("source_tex"),
            "source_sha256": entry.get("source_sha256"),
            "manifest": manifest_rel,
            "compile_witness_snapshot": snapshot_rel,
            "compile_witness_snapshot_sha256": snapshot_sha,
            "status": "pass" if not entry_failures else "fail",
            "failure_count": len(entry_failures),
            "warning_count": len(entry_warnings),
            "failures": entry_failures,
            "warnings": entry_warnings,
        }
        entry_reports.append(entry_report)
        failures.extend({"entry": entry.get("freeze_packet_id"), **failure} for failure in entry_failures)
        warnings.extend({"entry": entry.get("freeze_packet_id"), **warning} for warning in entry_warnings)

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "registry_present": True,
        "registry_path": "release_queue/FREEZE_PACKET_REGISTRY.json",
        "entries": entry_reports,
        "summary": {
            "registry_entry_count": len(registry.get("entries", [])),
            "materialized_entry_count": sum(1 for row in registry.get("entries", []) if isinstance(row, dict) and row.get("status") == "materialized_non_public_freeze_packet"),
            "unregistered_packet_dir_count": len(unregistered),
            "checks_failed": len(failures),
            "nonblocking_finding_count": len(warnings),
        },
        "failures": failures[:50],
        "nonblocking_findings": warnings[:50],
        "fail_closed_rule": "If freeze-packet snapshot integrity fails, publication execution remains blocked and the staged packet must not be used; historical published-packet drift of live planning surfaces is recorded as nonblocking finding debt.",
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
