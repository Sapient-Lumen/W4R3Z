#!/usr/bin/env python3
"""Verify that release-freeze preflight warnings are explicitly resolved."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_warning(text: str) -> str:
    lowered = text.lower()
    if "evidence pack" in lowered or "artifact-governance" in lowered:
        return "artifact_governance_evidence_pack"
    return "unclassified_warning"


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    plan = load_json(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json")
    evidence_report = load_json(root / "reports" / "evidence_pack_integrity.json")
    evidence_registry = load_json(root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json")
    failures: list[dict[str, Any]] = []
    resolutions: list[dict[str, Any]] = []

    if plan.get("generated_for_revision") != release["revision"] or plan.get("checked_bundle") != release["bundle"]:
        failures.append({"category": "freeze_plan_revision_or_bundle_mismatch"})
    if plan.get("publication_authorized") is not False:
        failures.append({"category": "freeze_plan_publication_authorized_not_false"})

    direct = plan.get("direct_preflight", {}) if isinstance(plan.get("direct_preflight"), dict) else {}
    selected = plan.get("selected_source", {}) if isinstance(plan.get("selected_source"), dict) else {}
    gates = {row.get("name"): row for row in plan.get("gates", []) if isinstance(row, dict)}
    evidence_gate = plan.get("evidence_gate", {}) if isinstance(plan.get("evidence_gate"), dict) else {}
    warnings = [str(w) for w in direct.get("warnings", []) if str(w).strip()]

    source = str(selected.get("source_tex", ""))
    source_sha = str(selected.get("source_sha256", ""))
    registry_entries = evidence_registry.get("entries", []) if isinstance(evidence_registry.get("entries"), list) else []
    registry_match = next((row for row in registry_entries if isinstance(row, dict) and row.get("source_tex") == source and row.get("source_sha256") == source_sha), None)
    evidence_report_ok = evidence_report.get("status") == "pass" and evidence_report.get("generated_for_revision") == release["revision"] and evidence_report.get("checked_bundle") == release["bundle"]

    for warning in warnings:
        kind = classify_warning(warning)
        row: dict[str, Any] = {"warning": warning, "classification": kind, "status": "unresolved"}
        if kind == "artifact_governance_evidence_pack":
            attached_ok = (
                direct.get("details", {}).get("artifact_governance_likely") is True
                and gates.get("evidence_pack_resolution", {}).get("status") == "pass"
                and evidence_gate.get("status") == "attached_evidence_pack"
                and bool(evidence_gate.get("evidence_pack_manifest"))
                and bool(registry_match)
                and evidence_report_ok
            )
            deferred_ok = (
                direct.get("details", {}).get("artifact_governance_likely") is True
                and gates.get("evidence_pack_resolution", {}).get("status") == "pending"
                and evidence_gate.get("status") == "pending_attach_or_waive"
                and evidence_gate.get("publication_blocking_until_resolved") is True
                and not evidence_gate.get("evidence_pack_manifest")
                and not registry_match
                and plan.get("publication_authorized") is False
            )
            row.update({
                "resolution": "attached source-bound evidence pack" if attached_ok else "deferred at explicit publication-blocking evidence gate" if deferred_ok else "",
                "evidence_pack_manifest": evidence_gate.get("evidence_pack_manifest", ""),
                "publication_blocking": bool(deferred_ok),
                "status": "resolved" if attached_ok else "deferred" if deferred_ok else "unresolved",
            })
        if row["status"] not in {"resolved", "deferred"}:
            failures.append({"category": "freeze_preflight_warning_unresolved", "warning": warning, "classification": kind})
        resolutions.append(row)

    if direct.get("status") != "pass" or direct.get("problems"):
        failures.append({"category": "direct_preflight_not_static_pass", "status": direct.get("status"), "problems": direct.get("problems")})

    summary = {
        "checks_failed": len(failures),
        "preflight_notice_count": len(warnings),
        "resolved_notice_count": sum(1 for row in resolutions if row.get("status") == "resolved"),
        "deferred_blocking_notice_count": sum(1 for row in resolutions if row.get("status") == "deferred"),
        "unresolved_notice_count": sum(1 for row in resolutions if row.get("status") == "unresolved"),
        "artifact_governance_notice_count": sum(1 for row in resolutions if row.get("classification") == "artifact_governance_evidence_pack"),
        "selected_source": source,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "freeze_plan": "release_queue/NEXT_RELEASE_FREEZE_PLAN.json",
        "preflight_notice_resolutions": resolutions,
        "failures": failures[:50],
        "summary": summary,
        "fail_closed_rule": "If a static freeze preflight warning is neither resolved nor preserved as an explicit publication-blocking pending gate, default to no publication.",
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
