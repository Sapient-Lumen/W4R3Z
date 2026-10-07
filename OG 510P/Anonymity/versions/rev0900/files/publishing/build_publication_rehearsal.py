#!/usr/bin/env python3
"""Build a non-authorizing publication rehearsal certificate.

The rehearsal ties together queue readiness, evidence pack, compile witness,
freeze packet, decision template, publication boundary, and packaging status. It
is not a publication receipt and does not create a public head.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_entry(root: pathlib.Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {"path": rel, "exists": path.exists(), "sha256": sha256_file(path) if path.exists() else ""}


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    plan = load_json(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json")
    readiness = load_json(root / "reports" / "release_readiness_audit.json")
    evidence = load_json(root / "reports" / "evidence_pack_integrity.json")
    compile_witness = load_json(root / "reports" / "freeze_compile_witness.json")
    freeze_packet = load_json(root / "reports" / "freeze_packet_integrity.json")
    boundary = load_json(root / "reports" / "publication_boundary.json")
    decision_template = load_json(root / "reports" / "publication_decision_template.json")
    packaging = load_json(root / "reports" / "archive_packaging_recipe.json")
    toolchain = load_json(root / "reports" / "freeze_toolchain.json") if (root / "reports" / "freeze_toolchain.json").exists() else {}

    failures: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    selected = plan.get("selected_source", {}) if isinstance(plan.get("selected_source"), dict) else {}
    source = str(selected.get("source_tex", ""))
    source_sha = str(selected.get("source_sha256", ""))
    prospective_target = str(selected.get("prospective_target", ""))

    for name, report in [
        ("release_readiness", readiness),
        ("evidence_pack_integrity", evidence),
        ("freeze_compile_witness", compile_witness),
        ("freeze_packet_integrity", freeze_packet),
        ("publication_boundary", boundary),
        ("publication_decision_template", decision_template),
        ("archive_packaging_recipe", packaging),
        ("freeze_toolchain", toolchain),
    ]:
        if report and report.get("status") != "pass":
            failures.append({"category": "surface_not_pass", "surface": name, "status": report.get("status")})
        if report and report.get("generated_for_revision") not in {None, release["revision"]}:
            failures.append({"category": "surface_revision_mismatch", "surface": name, "revision": report.get("generated_for_revision"), "current": release["revision"]})
        if report and report.get("checked_bundle") not in {None, release["bundle"]}:
            failures.append({"category": "surface_bundle_mismatch", "surface": name, "bundle": report.get("checked_bundle"), "current": release["bundle"]})
        if report and report.get("publication_authorized") is True:
            failures.append({"category": "surface_authorizes_publication", "surface": name})

    if plan.get("publication_authorized") is not False:
        failures.append({"category": "freeze_plan_publication_authorized_not_false"})
    existing_new_heads = int(boundary.get("summary", {}).get("new_post_policy_anonymity_head_count", 0) or 0)
    if prospective_target and (root / prospective_target).exists():
        failures.append({"category": "prospective_target_already_exists", "target": prospective_target})
    if source and (root / source).exists() and sha256_file(root / source) != source_sha:
        failures.append({"category": "selected_source_hash_drift", "source": source, "expected": source_sha, "actual": sha256_file(root / source)})

    gates = plan.get("gates", []) if isinstance(plan.get("gates"), list) else []
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        if gate.get("blocking", True) and gate.get("status") != "pass":
            blockers.append({"gate": gate.get("name"), "status": gate.get("status"), "detail": gate.get("detail")})
    if decision_template.get("publication_authorized") is not False:
        failures.append({"category": "decision_template_publication_authorized_not_false"})

    source_binding = {
        "source_tex": source,
        "source_sha256": source_sha,
        "source_current_sha256": sha256_file(root / source) if source and (root / source).exists() else "",
        "decision_note": selected.get("decision_note"),
        "prospective_target": prospective_target,
    }

    bound_surfaces = [
        file_entry(root, "release_queue/NEXT_RELEASE_FREEZE_PLAN.json"),
        file_entry(root, "release_queue/EVIDENCE_PACK_REGISTRY.json"),
        file_entry(root, "release_queue/FREEZE_COMPILE_WITNESS.json"),
        file_entry(root, "release_queue/FREEZE_PACKET_REGISTRY.json"),
        file_entry(root, "release_queue/PUBLICATION_DECISION_TEMPLATE.md"),
        file_entry(root, "reports/release_readiness_audit.json"),
        file_entry(root, "reports/evidence_pack_integrity.json"),
        file_entry(root, "reports/freeze_compile_witness.json"),
        file_entry(root, "reports/freeze_packet_integrity.json"),
        file_entry(root, "reports/publication_boundary.json"),
        file_entry(root, "reports/archive_packaging_recipe.json"),
    ]

    readiness_status = "ready_for_explicit_publication_decision" if not failures and not blockers else "not_ready_pending_blocking_gates"
    if compile_witness.get("compile_gate_status") != "pass":
        readiness_status = "not_ready_pending_compile_refresh_and_manual_gates"

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "rehearsal_type": "non_authorizing_publication_dry_run",
        "readiness_status": readiness_status,
        "source_binding": source_binding,
        "compile_gate_status": compile_witness.get("compile_gate_status"),
        "toolchain_gate_status": toolchain.get("toolchain_gate_status"),
        "blocking_gates": blockers,
        "bound_surfaces": bound_surfaces,
        "summary": {
            "surface_failures": len(failures),
            "blocking_gate_count": len(blockers),
            "bound_surface_count": len(bound_surfaces),
            "publication_authorized": False,
            "existing_new_post_policy_anonymity_head_count": existing_new_heads,
        },
        "failures": failures[:50],
        "fail_closed_rule": "A pass here means the rehearsal is internally consistent; it does not authorize publication, especially while blocking gates remain.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="reports/publication_rehearsal.json")
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
