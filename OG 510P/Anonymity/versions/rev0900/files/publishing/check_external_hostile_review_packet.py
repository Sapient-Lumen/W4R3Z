#!/usr/bin/env python3
"""Verify the external hostile-review packet is current and non-authorizing."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_external_hostile_review_packet as packet_builder  # noqa: E402
import check_hostile_review_vectors as hostile_vectors  # noqa: E402
import check_threat_transfer_matrix as threat_matrix  # noqa: E402

PACKET_JSON = pathlib.Path("release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.json")
PACKET_MD = pathlib.Path("release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_jsonable(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def task_map(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = packet.get("review_tasks", []) if isinstance(packet.get("review_tasks"), list) else []
    return {str(row.get("id")): row for row in tasks if isinstance(row, dict) and row.get("id")}


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    packet_path = root / PACKET_JSON
    md_path = root / PACKET_MD
    if not packet_path.exists():
        return {
            "status": "fail",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "report_kind": "external_hostile_review_packet_check",
            "failures": [{"category": "packet_json_missing", "path": PACKET_JSON.as_posix()}],
            "summary": {"checks_failed": 1},
            "fail_closed_rule": "No external review packet means the State/MUCC/MC-EQ/CPPC external-review gate is not prepared; publication remains blocked.",
        }
    packet = load_json(packet_path)
    expected = packet_builder.build(root)
    if packet != expected:
        failures.append({"category": "packet_not_current", "actual_canonical_sha256": digest_jsonable(packet), "expected_canonical_sha256": digest_jsonable(expected)})

    if packet.get("packet_format") != packet_builder.PACKET_VERSION:
        failures.append({"category": "packet_format_mismatch", "actual": packet.get("packet_format"), "expected": packet_builder.PACKET_VERSION})
    if packet.get("generated_for_revision") != release.get("revision"):
        failures.append({"category": "packet_revision_mismatch", "actual": packet.get("generated_for_revision"), "expected": release.get("revision")})
    if packet.get("checked_bundle") != release.get("bundle"):
        failures.append({"category": "packet_bundle_mismatch", "actual": packet.get("checked_bundle"), "expected": release.get("bundle")})
    if packet.get("publication_authorized") is not False:
        failures.append({"category": "packet_publication_authorized_not_false"})

    signoff = packet.get("external_reviewer_signoff", {}) if isinstance(packet.get("external_reviewer_signoff"), dict) else {}
    if signoff.get("status") != "missing" or signoff.get("signed_digest") is not None:
        failures.append({"category": "packet_improperly_claims_external_signoff", "signoff": signoff})
    if packet.get("external_review_status") != "packet_ready_signoff_missing":
        failures.append({"category": "external_review_status_mismatch", "actual": packet.get("external_review_status")})

    hostile_report = hostile_vectors.check(root)
    transfer_report = threat_matrix.check(root)
    if hostile_report.get("status") != "pass":
        failures.append({"category": "hostile_vector_recompute_not_pass", "status": hostile_report.get("status")})
    if transfer_report.get("status") != "pass":
        failures.append({"category": "threat_transfer_matrix_not_pass", "status": transfer_report.get("status")})
    internal_summary = packet.get("internal_recomputation_summary", {}) if isinstance(packet.get("internal_recomputation_summary"), dict) else {}
    expected_state_vectors = len(hostile_vectors.STATE_VECTOR_IDS)
    expected_mucc_vectors = len(hostile_vectors.MUCC_VECTOR_IDS)
    expected_mceq_vectors = len(hostile_vectors.MCEQ_VECTOR_IDS)
    expected_cppc_vectors = len(hostile_vectors.CPPC_VECTOR_IDS)
    if (internal_summary.get("state_vector_count") != expected_state_vectors
            or internal_summary.get("mucc_vector_count") != expected_mucc_vectors
            or internal_summary.get("mceq_vector_count") != expected_mceq_vectors
            or internal_summary.get("cppc_vector_count") != expected_cppc_vectors):
        failures.append({
            "category": "unexpected_internal_vector_counts",
            "summary": internal_summary,
            "expected_state_vector_count": expected_state_vectors,
            "expected_mucc_vector_count": expected_mucc_vectors,
            "expected_mceq_vector_count": expected_mceq_vectors,
            "expected_cppc_vector_count": expected_cppc_vectors,
        })
    if internal_summary.get("external_reviewer_signoff") != "missing" or internal_summary.get("publication_blocking_external_review") is not True:
        failures.append({"category": "internal_external_boundary_mismatch", "summary": internal_summary})

    tasks = task_map(packet)
    required_tasks = {
        "state_nat_bit_boundary",
        "mucc_contact_floor_arithmetic",
        "mucc_liveness_substitution_boundary",
        "mucc_approximate_equalization_boundary",
        "mucc_necessity_not_sufficiency_boundary",
        "mucc_joint_assumption_sufficiency_ladder",
        "mucc_joint_privacy_nonclaim_boundary",
        "mceq_tv_support_ratio_boundary",
        "mceq_worked_binding_nonclaim",
        "cppc_alert_necessity_sufficiency_boundary",
        "cppc_mechanism_composition_and_artifact_boundary",
        "threat_transfer_nonclaim_boundary",
    }
    missing_tasks = sorted(required_tasks - set(tasks))
    if missing_tasks:
        failures.append({"category": "review_tasks_missing", "missing": missing_tasks})
    if len(tasks) < len(required_tasks):
        failures.append({"category": "too_few_review_tasks", "actual": len(tasks), "minimum": len(required_tasks)})

    threat = packet.get("threat_transfer_target", {}) if isinstance(packet.get("threat_transfer_target"), dict) else {}
    rejected = threat.get("external_rows_to_reject_as_theorem_transfer", []) if isinstance(threat.get("external_rows_to_reject_as_theorem_transfer"), list) else []
    if threat.get("native_theorem_row_count") != 1 or threat.get("external_transfer_authorized_rows") != 0 or len(rejected) != 6:
        failures.append({"category": "threat_transfer_packet_boundary_mismatch", "native": threat.get("native_theorem_row_count"), "external_authorized": threat.get("external_transfer_authorized_rows"), "rejected_count": len(rejected)})

    surface_failures: list[dict[str, Any]] = []
    seen_surfaces: set[str] = set()
    for row in packet.get("required_surfaces", []) if isinstance(packet.get("required_surfaces"), list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            surface_failures.append({"problem": "surface_row_malformed", "row": row})
            continue
        rel = row["path"]
        seen_surfaces.add(rel)
        path = root / rel
        if not path.exists() or not path.is_file():
            surface_failures.append({"path": rel, "problem": "surface_missing"})
            continue
        if row.get("sha256") != sha256_file(path):
            surface_failures.append({"path": rel, "problem": "surface_sha256_mismatch", "declared": row.get("sha256"), "actual": sha256_file(path)})
    for required in [
        "release_queue/HOSTILE_REVIEW_VECTORS.json",
        "release_queue/evidence_packs/2026.06.16-state-dependent-anonymity/STATE_ANONYMITY_CARD.json",
        "release_queue/evidence_packs/2026.06.16-committee-contact-set-privacy-in-anonymous-dht-lookups/MUCC_CONTACT_FLOOR_CARD.json",
        "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex",
        "series/anondht_state_series/paper3_closed_view_auditing_cppc/paper.tex",
        "release_queue/hold/2026.03.17-paper3-closed-view-alert-cap-repair-hold.md",
        "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_receipt.json",
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/materialize_example.py",
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/validate_example.py",
    ]:
        if required not in seen_surfaces:
            surface_failures.append({"path": required, "problem": "required_surface_not_listed"})
    if surface_failures:
        failures.append({"category": "surface_digest_failures", "failures": surface_failures[:20]})

    md_text = md_path.read_text(encoding="utf-8", errors="replace") if md_path.exists() else ""
    for token in [release["revision"], "packet_ready_signoff_missing", "Publication authorized: `false`", "external review"]:
        if token not in md_text:
            failures.append({"category": "packet_markdown_token_missing", "token": token, "path": PACKET_MD.as_posix()})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "external_hostile_review_packet_check",
        "packet_json": PACKET_JSON.as_posix(),
        "packet_md": PACKET_MD.as_posix(),
        "packet_sha256": sha256_file(packet_path) if packet_path.exists() else "",
        "summary": {
            "checks_failed": len(failures),
            "review_tasks": len(tasks),
            "required_surface_count": len(packet.get("required_surfaces", [])) if isinstance(packet.get("required_surfaces"), list) else 0,
            "external_review_status": packet.get("external_review_status"),
            "external_signoff_status": signoff.get("status"),
            "publication_blocking": True,
        },
        "failures": failures[:80],
        "fail_closed_rule": "A current hostile-review packet prepares review but never authorizes publication; missing or stale packet data keeps the external-review gate pending.",
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
