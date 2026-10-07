#!/usr/bin/env python3
"""Audit evidence-pack obligations for queue items without authorizing publication.

This report is intentionally non-promotional.  It classifies Candidate and
Published-ready sources that appear to make artifact/provenance/evidence claims
and states whether a publication freeze would need either a minimal evidence
pack or an explicit waiver.  Because queued items are not being published, an
unsatisfied evidence decision is not a report failure; it becomes a freeze gate
for the selected target.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_release_readiness as rr  # noqa: E402
import check_evidence_pack_integrity as epi  # noqa: E402

MINIMAL_EVIDENCE_PACK_POLICY = {
    "rule": "Before publication, a source that likely makes artifact-governance claims must attach a minimal evidence pack or carry an explicit waiver in the publication decision.",
    "attachment_minimum": [
        "source_tex_sha256",
        "evidence_pack_manifest_or_manifest_excerpt",
        "declared evidence-pack paths resolved inside the archive",
        "validator or audit report when the source cites a validator/audit surface",
        "publication decision note naming the evidence-pack resolution",
    ],
    "waiver_minimum": [
        "waiver_id",
        "decision_note",
        "reason",
        "scope of waived evidence-pack obligation",
    ],
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_item(item: dict[str, Any], attached_by_source: dict[str, dict[str, Any]]) -> dict[str, Any]:
    details = item.get("details", {}) if isinstance(item.get("details"), dict) else {}
    likely = bool(details.get("artifact_governance_likely"))
    warnings = item.get("warnings", []) if isinstance(item.get("warnings"), list) else []
    warning_categories = sorted({str(w.get("category", "")) for w in warnings if isinstance(w, dict)})
    attached = attached_by_source.get(str(item.get("source_tex", "")))
    source_sha = details.get("source_sha256")
    attached_matches_source = bool(attached and attached.get("source_sha256") == source_sha and attached.get("status") == "pass")
    if likely and attached_matches_source:
        freeze_resolution = "attached_evidence_pack"
        freeze_gate_status = "attached_non_public_freeze_evidence"
    elif likely:
        freeze_resolution = "attach_evidence_pack_or_record_explicit_waiver"
        freeze_gate_status = "required_if_selected_for_publication"
    else:
        freeze_resolution = "not_required_by_heuristic"
        freeze_gate_status = "not_applicable"
    return {
        "item_id": item.get("item_id", ""),
        "queue_state": item.get("queue_state", ""),
        "source_tex": item.get("source_tex", ""),
        "title": item.get("title", ""),
        "decision_note": item.get("decision_note", ""),
        "source_sha256": details.get("source_sha256"),
        "artifact_governance_likely": likely,
        "release_readiness": item.get("release_readiness", ""),
        "evidence_warning_present": "evidence_pack_review_needed" in warning_categories,
        "freeze_gate_status": freeze_gate_status,
        "required_freeze_resolution": freeze_resolution,
        "evidence_pack_attached": attached_matches_source,
        "evidence_pack_id": attached.get("evidence_pack_id") if attached_matches_source else "",
        "evidence_pack_manifest": attached.get("manifest") if attached_matches_source else "",
    }


def check(root: pathlib.Path) -> dict[str, Any]:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    readiness = rr.check(root)
    integrity = epi.check(root)
    attached_by_source = {
        str(entry.get("source_tex")): entry
        for entry in integrity.get("entries", [])
        if entry.get("status") == "pass" and entry.get("source_tex")
    }
    items = [classify_item(item, attached_by_source) for item in readiness.get("items", [])]

    state_counts: collections.Counter[str] = collections.Counter(str(item.get("queue_state", "")) for item in items)
    needed_by_state: collections.Counter[str] = collections.Counter(str(item.get("queue_state", "")) for item in items if item.get("artifact_governance_likely"))
    missing_warning = [item for item in items if item.get("artifact_governance_likely") and not item.get("evidence_warning_present")]

    recommendation = readiness.get("next_release_recommendation", {}) if isinstance(readiness.get("next_release_recommendation"), dict) else {}
    recommended_source = recommendation.get("source_tex")
    selected = next((item for item in items if item.get("source_tex") == recommended_source), None)
    if selected and selected.get("artifact_governance_likely") and selected.get("evidence_pack_attached"):
        next_gate = {
            "status": "attached_evidence_pack",
            "source_tex": selected.get("source_tex"),
            "title": selected.get("title"),
            "source_sha256": selected.get("source_sha256"),
            "publication_blocking_until_resolved": False,
            "required_resolution": selected.get("required_freeze_resolution"),
            "evidence_pack_id": selected.get("evidence_pack_id"),
            "evidence_pack_manifest": selected.get("evidence_pack_manifest"),
        }
    elif selected and selected.get("artifact_governance_likely"):
        next_gate = {
            "status": "pending_attach_or_waive",
            "source_tex": selected.get("source_tex"),
            "title": selected.get("title"),
            "source_sha256": selected.get("source_sha256"),
            "publication_blocking_until_resolved": True,
            "required_resolution": selected.get("required_freeze_resolution"),
        }
    elif selected:
        next_gate = {
            "status": "not_required_by_heuristic",
            "source_tex": selected.get("source_tex"),
            "title": selected.get("title"),
            "source_sha256": selected.get("source_sha256"),
            "publication_blocking_until_resolved": False,
            "required_resolution": "not_required_by_heuristic",
        }
    else:
        next_gate = {
            "status": "no_selected_source",
            "publication_blocking_until_resolved": False,
            "required_resolution": "none",
        }

    failures: list[dict[str, Any]] = []
    if readiness.get("status") != "pass":
        failures.append({"category": "release_readiness_not_pass", "detail": readiness.get("status")})
    if integrity.get("status") != "pass":
        failures.append({"category": "evidence_pack_integrity_not_pass", "detail": integrity.get("status"), "failures": integrity.get("failures", [])[:10]})
    if missing_warning:
        failures.append({"category": "missing_evidence_warning_on_likely_source", "count": len(missing_warning), "detail": [item.get("source_tex") for item in missing_warning[:20]]})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "publication_authorized": False,
        "policy": MINIMAL_EVIDENCE_PACK_POLICY,
        "items": items,
        "summary": {
            "checked_item_count": len(items),
            "state_counts": dict(sorted(state_counts.items())),
            "artifact_governance_likely_count": sum(1 for item in items if item.get("artifact_governance_likely")),
            "artifact_governance_likely_by_state": dict(sorted(needed_by_state.items())),
            "missing_evidence_warning_count": len(missing_warning),
            "freeze_gate_required_if_selected_count": sum(1 for item in items if item.get("freeze_gate_status") in {"required_if_selected_for_publication", "attached_non_public_freeze_evidence"}),
            "evidence_pack_attached_count": sum(1 for item in items if item.get("evidence_pack_attached")),
            "evidence_pack_integrity_status": integrity.get("status"),
        },
        "next_release_evidence_gate": next_gate,
        "failures": failures,
        "fail_closed_rule": "This audit does not publish anything. If its status fails, do not publish; if a selected source has a pending evidence gate, attach evidence or record a waiver before freeze.",
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
