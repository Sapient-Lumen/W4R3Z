#!/usr/bin/env python3
"""Build the release maintainer handoff pack.

This is a bounded, deterministic summary of the current archive's release
state. It is not a substitute for running the full release gate, and it is not
live election evidence. It tells a maintainer what is current, what is still
synthetic, which source-review queue is hot, and which generated pilot outputs
should be reviewed before publication.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
from release_context import release_date

RELEASE_DATE = dt.date.fromisoformat(release_date(ROOT))
OUTDIR = ROOT / "artifacts" / "reports"
EXAMPLE = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
REG = ROOT / "artifacts" / "registries"
SOURCES = ROOT / "evidence" / "lock" / "external-sources.toml"
SCRIPTS = ROOT / "scripts"

BOUNDARY = (
    "Release maintainer handoff only; synthetic rehearsal outputs are not live election evidence, "
    "not certification, not outcome proof, not proof of intent or fraud, and not legal advice."
)

SOURCE_NON_CLAIM = (
    "Source-review triage says which references need maintainer review; it is not proof that any source is wrong, "
    "not a live authority decision, and not legal advice."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def import_release_steps() -> Any:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import release_gate_steps  # type: ignore

    return release_gate_steps


def source_rows() -> list[dict[str, Any]]:
    data = tomllib.loads(SOURCES.read_text(encoding="utf-8"))
    rows = data.get("source")
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def _date_or_none(raw: Any) -> dt.date | None:
    if raw is None:
        return None
    try:
        return dt.date.fromisoformat(str(raw))
    except ValueError:
        return None


def _is_pinned(row: dict[str, Any]) -> bool:
    sha = str(row.get("sha256") or "").strip()
    return bool(re.fullmatch(r"[0-9a-f]{64}", sha))


def _example_ids(rows: list[dict[str, Any]], limit: int = 10) -> str:
    return "; ".join(str(r.get("id") or "").strip() for r in rows[:limit] if str(r.get("id") or "").strip())


def build_source_triage() -> dict[str, Any]:
    rows = source_rows()
    due_cutoff = RELEASE_DATE + dt.timedelta(days=30)
    groups: dict[str, list[dict[str, Any]]] = {
        "pinned": [],
        "unpinned_expired_review": [],
        "unpinned_due_within_30_days": [],
        "unpinned_due_later": [],
        "unpinned_missing_review_by": [],
        "special_case_high_risk_due_within_30_days": [],
        "official_websites_due_within_30_days": [],
    }

    for row in rows:
        tags = {str(t).strip() for t in row.get("tags", []) if str(t).strip()}
        pinned = _is_pinned(row)
        review_by = _date_or_none(row.get("review_by"))
        if pinned:
            groups["pinned"].append(row)
            continue
        if review_by is None:
            groups["unpinned_missing_review_by"].append(row)
            continue
        if review_by < RELEASE_DATE:
            groups["unpinned_expired_review"].append(row)
        elif review_by <= due_cutoff:
            groups["unpinned_due_within_30_days"].append(row)
            if "special_case_high_risk" in tags:
                groups["special_case_high_risk_due_within_30_days"].append(row)
            if "official_websites" in tags:
                groups["official_websites_due_within_30_days"].append(row)
        else:
            groups["unpinned_due_later"].append(row)

    category_actions = {
        "pinned": "No immediate review required; keep pinned byte hash and citation role stable.",
        "unpinned_expired_review": "Release-blocking until refreshed, pinned, demoted, or replaced.",
        "unpinned_due_within_30_days": "Schedule source refresh or pinning before relying on these as current authority.",
        "unpinned_due_later": "Keep in ordinary source-review queue.",
        "unpinned_missing_review_by": "Release-blocking hygiene issue; add review_by or pin durable bytes.",
        "special_case_high_risk_due_within_30_days": "Prioritize before voter-facing high-risk special-case use.",
        "official_websites_due_within_30_days": "Prioritize official-site refresh where current public instructions may change.",
    }
    rows_out: list[dict[str, Any]] = []
    for category in [
        "pinned",
        "unpinned_expired_review",
        "unpinned_due_within_30_days",
        "unpinned_due_later",
        "unpinned_missing_review_by",
        "special_case_high_risk_due_within_30_days",
        "official_websites_due_within_30_days",
    ]:
        values = sorted(groups[category], key=lambda r: (str(r.get("review_by") or "9999-12-31"), str(r.get("id") or "")))
        rows_out.append({
            "category": category,
            "count": len(values),
            "example_source_ids": _example_ids(values),
            "recommended_action": category_actions[category],
            "non_claims": SOURCE_NON_CLAIM,
        })

    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE.isoformat(),
        "source_count": len(rows),
        "pinned_count": len(groups["pinned"]),
        "unpinned_count": len(rows) - len(groups["pinned"]),
        "expired_review_count": len(groups["unpinned_expired_review"]),
        "due_within_30_days_count": len(groups["unpinned_due_within_30_days"]),
        "missing_review_by_count": len(groups["unpinned_missing_review_by"]),
        "triage_rows": rows_out,
        "boundary": SOURCE_NON_CLAIM,
    }


def build_handoff() -> dict[str, Any]:
    scenario = load_json(EXAMPLE / "scenario.json")
    smoke = load_json(EXAMPLE / "smoke-report.json")
    evidence_map = load_json(EXAMPLE / "evidence-map.json")
    trust = load_json(EXAMPLE / "trust-recovery-matrix.json")
    human = load_json(EXAMPLE / "human-review-matrix.json")
    scorecard = load_json(EXAMPLE / "evaluator-scorecard.json")
    negative = load_json(EXAMPLE / "negative-control-report.json")
    local_intake = load_json(OUTDIR / "local-pilot-intake-matrix.json")
    redaction = load_json(OUTDIR / "redaction-publication-matrix.json")
    accessibility = load_json(OUTDIR / "accessibility-language-matrix.json")
    custody = load_json(OUTDIR / "evidence-custody-provenance-matrix.json")
    independent = load_json(OUTDIR / "independent-review-matrix.json")
    live_workqueue = load_json(EXAMPLE / "live-closeout-workqueue.json")
    live_intake = load_json(EXAMPLE / "live-closeout-evidence-intake-status.json")
    rev = VERSION.removeprefix("v").zfill(4)
    full_drill = load_json(OUTDIR / f"mission-kernel-full-drill-replay-audit-rev{rev}.json")
    ballot_accounting = load_json(OUTDIR / f"ballot-accounting-reconciliation-rev{rev}.json")
    event_log_reconciliation = load_json(OUTDIR / f"election-event-log-reconciliation-rev{rev}.json")
    steps = import_release_steps()
    source_triage = build_source_triage()
    handoff_rows = read_csv(REG / "release-maintainer-handoff.csv")

    key_artifacts = [
        "artifacts/examples/example_county_2026_municipal_pilot/scenario.json",
        "artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json",
        "artifacts/examples/example_county_2026_municipal_pilot/smoke-report.json",
        "artifacts/examples/example_county_2026_municipal_pilot/evaluator-scorecard.json",
        "artifacts/examples/example_county_2026_municipal_pilot/negative-control-report.json",
        "artifacts/examples/example_county_2026_municipal_pilot/public-negative-control-summary.md",
        "artifacts/reports/source-review-triage.json",
        "artifacts/reports/source-review-triage.csv",
        "artifacts/reports/local-pilot-intake-matrix.json",
        "artifacts/reports/local-pilot-gap-burndown.json",
        "artifacts/reports/local-pilot-no-go-notice.md",
        "artifacts/reports/redaction-publication-matrix.json",
        "artifacts/reports/redaction-publication-no-go-notice.md",
        "artifacts/reports/accessibility-language-matrix.json",
        "artifacts/reports/accessibility-language-no-go-notice.md",
        "artifacts/reports/evidence-custody-provenance-matrix.json",
        "artifacts/reports/evidence-custody-no-go-notice.md",
        "artifacts/reports/independent-review-matrix.json",
        "artifacts/reports/independent-review-no-go-notice.md",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-workqueue.json",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-workqueue.csv",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-intake-template.json",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-submission-empty.json",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json",
        "artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.csv",
        "artifacts/examples/example_county_2026_municipal_pilot/public-live-closeout-intake-status.md",
        "docs/930-operator-evidence-submitter-and-nonproduction-drill.md",
        "tools/mission_kernel_evidence_submitter.py",
        "scripts/check_mission_kernel_evidence_submitter.py",
        "schemas/MissionKernelEvidenceSubmission.json",
        "docs/931-full-mission-kernel-drill-replay-and-intake-boundary-audit.md",
        "tools/mission_kernel_full_drill_replay.py",
        "scripts/check_mission_kernel_full_drill_replay.py",
        "artifacts/reports/mission-kernel-live-workqueue-rev" + VERSION.removeprefix("v").zfill(4) + ".json",
        "artifacts/reports/mission-kernel-live-evidence-intake-rev" + VERSION.removeprefix("v").zfill(4) + ".json",
        "artifacts/reports/mission-kernel-full-drill-replay-audit-rev" + VERSION.removeprefix("v").zfill(4) + ".json",
        "artifacts/examples/example_county_2026_municipal_pilot/public-full-closeout-drill-replay.md",
        "tools/ballot_accounting_reconciler.py",
        "scripts/check_ballot_accounting_reconciler.py",
        "artifacts/reports/ballot-accounting-reconciliation-rev" + VERSION.removeprefix("v").zfill(4) + ".json",
        "artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-accounting-minimal.json",
        "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-ballot-accounting-reconciliation.md",
        "tools/election_event_log_reconciler.py",
        "scripts/check_election_event_log_reconciler.py",
        "artifacts/reports/election-event-log-reconciliation-rev" + VERSION.removeprefix("v").zfill(4) + ".json",
        "artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json",
        "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-election-event-log-reconciliation.md",
    ]
    present_artifacts = [p for p in key_artifacts if (ROOT / p).exists()]

    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE.isoformat(),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "scenario_id": scenario.get("scenario_id"),
        "boundary": BOUNDARY,
        "release_gate_inventory": {
            "child_steps": len(steps.CHECK_STEP_NAMES),
            "final_manifest_step": steps.MANIFEST_STEP_NAME,
            "documented_by": "docs/162-release-and-ci-evidence-pipeline.md",
        },
        "current_outputs": {
            "scenario_archive_version": scenario.get("archive_version"),
            "packet_count": evidence_map.get("packet_count"),
            "smoke_status": smoke.get("status"),
            "scorecard_status": scorecard.get("status"),
            "scorecard_total_points": scorecard.get("total_points"),
            "scorecard_max_points": scorecard.get("max_points"),
            "negative_control_status": negative.get("status"),
            "negative_control_fixture_count": negative.get("fixture_count"),
            "trust_recovery_modes": trust.get("row_count"),
            "human_review_scenarios": human.get("scenario_count"),
            "local_pilot_decision": local_intake.get("decision"),
            "local_pilot_requirement_count": local_intake.get("requirement_count"),
            "local_pilot_missing_live_evidence_count": local_intake.get("missing_live_evidence_count"),
            "redaction_publication_decision": redaction.get("decision"),
            "redaction_policy_count": redaction.get("policy_count"),
            "redaction_missing_local_approval_count": redaction.get("missing_local_approval_count"),
            "accessibility_language_decision": accessibility.get("decision"),
            "accessibility_language_policy_count": accessibility.get("policy_count"),
            "accessibility_language_missing_local_approval_count": accessibility.get("missing_local_approval_count"),
            "custody_provenance_decision": custody.get("decision"),
            "custody_provenance_policy_count": custody.get("policy_count"),
            "custody_provenance_missing_record_count": custody.get("missing_local_custody_record_count"),
            "independent_review_decision": independent.get("decision"),
            "independent_review_policy_count": independent.get("policy_count"),
            "independent_review_missing_evidence_count": independent.get("missing_independent_review_evidence_count"),
            "mission_kernel_live_workqueue_decision": live_workqueue.get("decision"),
            "mission_kernel_live_workqueue_items": live_workqueue.get("work_item_count"),
            "mission_kernel_live_workqueue_critical_items": live_workqueue.get("critical_work_item_count"),
            "mission_kernel_live_evidence_intake_decision": live_intake.get("decision"),
            "mission_kernel_live_evidence_intake_missing_items": live_intake.get("missing_live_evidence_item_count"),
            "mission_kernel_live_evidence_intake_live_objects": live_intake.get("live_evidence_object_count"),
            "mission_kernel_live_evidence_intake_valid_live_objects": live_intake.get("valid_live_evidence_object_count"),
            "mission_kernel_live_evidence_intake_drill_objects": live_intake.get("drill_evidence_object_count"),
            "mission_kernel_live_evidence_intake_valid_drill_objects": live_intake.get("valid_drill_evidence_object_count"),
            "mission_kernel_full_drill_decision": full_drill.get("decision"),
            "mission_kernel_full_drill_work_items": full_drill.get("work_item_count"),
            "mission_kernel_full_drill_complete_items": full_drill.get("complete_drill_item_count"),
            "mission_kernel_full_drill_required_classes": full_drill.get("required_evidence_class_count"),
            "mission_kernel_full_drill_valid_drill_objects": full_drill.get("valid_drill_evidence_object_count"),
            "mission_kernel_full_drill_live_objects": full_drill.get("live_evidence_object_count"),
            "mission_kernel_full_drill_leak_count": full_drill.get("local_path_leak_count"),
            "mission_kernel_full_drill_overclaim_count": full_drill.get("live_overclaim_term_count"),
            "ballot_accounting_reconciliation_decision": ballot_accounting.get("decision"),
            "ballot_accounting_reconciliation_rows": (ballot_accounting.get("counts") or {}).get("contest_accounting_row_count"),
            "ballot_accounting_reconciliation_errors": (ballot_accounting.get("counts") or {}).get("error_count"),
            "ballot_accounting_no_live_custody_claim": ballot_accounting.get("no_live_custody_claim"),
            "event_log_reconciliation_decision": event_log_reconciliation.get("decision"),
            "event_log_reconciliation_events": (event_log_reconciliation.get("counts") or {}).get("event_count"),
            "event_log_reconciliation_errors": (event_log_reconciliation.get("counts") or {}).get("error_count"),
            "event_log_missing_required_roles": (event_log_reconciliation.get("counts") or {}).get("missing_required_role_count"),
            "event_log_no_live_eel_claim": event_log_reconciliation.get("no_live_election_event_log_claim"),
        },
        "source_review_triage": {
            "source_count": source_triage["source_count"],
            "pinned_count": source_triage["pinned_count"],
            "unpinned_count": source_triage["unpinned_count"],
            "expired_review_count": source_triage["expired_review_count"],
            "due_within_30_days_count": source_triage["due_within_30_days_count"],
            "missing_review_by_count": source_triage["missing_review_by_count"],
            "report_ref": "artifacts/reports/source-review-triage.json",
        },
        "maintainer_handoff_actions": handoff_rows,
        "key_artifact_digests": [
            {"path": p, "sha256": sha256_file(ROOT / p)} for p in present_artifacts
        ],
        "residual_non_live_items": [
            "No live pilot deployment evidence is claimed in this release.",
            "External review, MAPT, TTR, witness-health, and admissibility rows remain pre-pilot placeholders unless a live row says otherwise.",
            "Synthetic Example County packets exercise verifier and handoff behavior only.",
            "Source-review triage identifies review pressure but does not certify a source as current authority.",
            "Local pilot intake remains no-go until jurisdiction-specific authority, source, privacy, retention, review, and legal evidence is added.",
            "Public release of local evidence remains no-go until redaction review and local approval are recorded.",
            "Voter-facing public release remains no-go until accessibility, language-access, plain-language, fallback, and human-help review are recorded.",
            "Live field-evidence reliance remains no-go until custody/provenance capture, transfer, access, public-derivative, chain-gap, and disposition records are recorded.",
            "Independent-validation and live-pilot claims remain no-go until reviewer scope, conflict disclosures, transcripts, dissent routes, public summary approval, and remediation/retest records are recorded.",
            "Mission-kernel live-closeout workqueue rows remain blocked until authorized local evidence, digests, approvals, redaction/public-boundary review, and retention/disposition records are supplied.",
            "The shipped live-evidence intake submission is deliberately empty; zero live evidence objects and zero non-production drill objects are present in this synthetic archive.",
            "The evidence submitter drill hashes temporary external records only to test plumbing; drill success is not live closeout evidence or authorization.",
            "The full mission-kernel drill replay completes all seven workqueue rows and twenty-eight evidence-class objects in non-production mode while preserving zero live evidence objects and zero live-readiness claims.",
            "The synthetic ballot-accounting reconciliation checks BD/CVR count completeness but is not live custody evidence, certification, or outcome proof.",
            "The synthetic election-event log reconciliation binds replay artifacts by digest and time order but is not live EEL evidence, full NIST EEL/CDF conformance, certification, or outcome proof.",
        ],
    }


def triage_csv_rows(triage: dict[str, Any]) -> list[dict[str, str]]:
    out = []
    for row in triage.get("triage_rows", []):
        out.append({
            "category": str(row.get("category") or ""),
            "count": str(row.get("count") or 0),
            "example_source_ids": str(row.get("example_source_ids") or ""),
            "recommended_action": str(row.get("recommended_action") or ""),
            "non_claims": str(row.get("non_claims") or ""),
        })
    return out


def handoff_markdown(handoff: dict[str, Any], triage: dict[str, Any]) -> str:
    outputs = handoff["current_outputs"]
    gate = handoff["release_gate_inventory"]
    source = handoff["source_review_triage"]
    lines = [
        "# Release maintainer handoff pack",
        "",
        "**Synthetic example only. This is not live election evidence, not certification, and not legal advice.**",
        "",
        f"Archive version: `{handoff['archive_version']}`  ",
        f"Release date: `{handoff['release_date']}`  ",
        f"Scenario: `{handoff['scenario_id']}`",
        "",
        "## Boundary",
        "",
        BOUNDARY,
        "",
        "## Current synthetic outputs",
        "",
        f"- Packet smoke status: `{outputs['smoke_status']}` across `{outputs['packet_count']}` packets.",
        f"- Evaluator scorecard: `{outputs['scorecard_status']}` `{outputs['scorecard_total_points']}/{outputs['scorecard_max_points']}`.",
        f"- Negative controls: `{outputs['negative_control_status']}` across `{outputs['negative_control_fixture_count']}` expected-failure fixtures.",
        f"- Trust-recovery modes: `{outputs['trust_recovery_modes']}`.",
        f"- Human-review scenarios: `{outputs['human_review_scenarios']}`.",
        f"- Local pilot intake: `{outputs['local_pilot_decision']}` with `{outputs['local_pilot_missing_live_evidence_count']}` missing live-evidence rows.",
        f"- Redaction/publication gate: `{outputs['redaction_publication_decision']}` with `{outputs['redaction_missing_local_approval_count']}` missing approval rows.",
        f"- Accessibility/language gate: `{outputs['accessibility_language_decision']}` with `{outputs['accessibility_language_missing_local_approval_count']}` missing approval rows.",
        f"- Custody/provenance gate: `{outputs['custody_provenance_decision']}` with `{outputs['custody_provenance_missing_record_count']}` missing custody-record rows.",
        f"- Independent-review/conflict gate: `{outputs['independent_review_decision']}` with `{outputs['independent_review_missing_evidence_count']}` missing review-evidence rows.",
        f"- Mission-kernel live-closeout workqueue: `{outputs['mission_kernel_live_workqueue_decision']}` with `{outputs['mission_kernel_live_workqueue_critical_items']}` critical blocker rows and `{outputs['mission_kernel_live_workqueue_items']}` total rows.",
        f"- Mission-kernel live-evidence intake: `{outputs['mission_kernel_live_evidence_intake_decision']}` with `{outputs['mission_kernel_live_evidence_intake_live_objects']}` live objects, `{outputs.get('mission_kernel_live_evidence_intake_drill_objects', 0)}` drill objects, and `{outputs['mission_kernel_live_evidence_intake_missing_items']}` missing work items.",
        f"- Full mission-kernel non-production drill replay: `{outputs['mission_kernel_full_drill_decision']}` with `{outputs['mission_kernel_full_drill_complete_items']}/{outputs['mission_kernel_full_drill_work_items']}` work items complete, `{outputs['mission_kernel_full_drill_valid_drill_objects']}` valid drill objects, `{outputs['mission_kernel_full_drill_required_classes']}` required evidence classes, and `{outputs['mission_kernel_full_drill_live_objects']}` live objects.",
        f"- Ballot-accounting reconciliation: `{outputs['ballot_accounting_reconciliation_decision']}` with `{outputs['ballot_accounting_reconciliation_rows']}` contest accounting rows and `{outputs['ballot_accounting_reconciliation_errors']}` errors; live custody claim: `{outputs['ballot_accounting_no_live_custody_claim'] is False}`.",
        f"- Election-event log reconciliation: `{outputs['event_log_reconciliation_decision']}` with `{outputs['event_log_reconciliation_events']}` event rows, `{outputs['event_log_reconciliation_errors']}` errors, and `{outputs['event_log_missing_required_roles']}` missing required roles; live EEL claim: `{outputs['event_log_no_live_eel_claim'] is False}`.",
        "",
        "## Release-gate inventory",
        "",
        f"- Child steps: `{gate['child_steps']}` plus final `{gate['final_manifest_step']}` manifest check/write step.",
        "- The handoff pack is a maintainer summary; run `python3 scripts/release_gate.py` for the authoritative gate.",
        "",
        "## Source-review pressure",
        "",
        f"- Sources total: `{source['source_count']}`.",
        f"- Pinned: `{source['pinned_count']}`.",
        f"- Unpinned: `{source['unpinned_count']}`.",
        f"- Expired review windows at release date: `{source['expired_review_count']}`.",
        f"- Due within 30 days: `{source['due_within_30_days_count']}`.",
        "",
        "## Handoff actions",
        "",
    ]
    for row in handoff.get("maintainer_handoff_actions", []):
        lines.append(f"- `{row['handoff_id']}` / `{row['phase']}`: {row['trigger']} → {row['owner']}.")
    lines.extend([
        "",
        "## Residual non-live items",
        "",
    ])
    for item in handoff.get("residual_non_live_items", []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Source triage categories",
        "",
    ])
    for row in triage.get("triage_rows", []):
        lines.append(f"- `{row['category']}`: `{row['count']}` — {row['recommended_action']}")
    lines.extend([
        "",
        "## Operator commands",
        "",
        "```bash",
        "python3 tools/release_maintainer_handoff_pack.py --json",
        "python3 scripts/check_release_maintainer_handoff.py",
        "```",
        "",
    ])
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    triage = build_source_triage()
    # Write source-triage outputs first so the handoff digest list can include
    # the exact report files shipped in this release.
    (OUTDIR / "source-review-triage.json").write_text(json.dumps(triage, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (OUTDIR / "source-review-triage.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["category", "count", "example_source_ids", "recommended_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(triage_csv_rows(triage))
    handoff = build_handoff()
    (OUTDIR / "release-maintainer-handoff.json").write_text(json.dumps(handoff, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    (OUTDIR / "release-maintainer-handoff.md").write_text(handoff_markdown(handoff, triage), encoding="utf-8")
    return {"handoff": handoff, "source_triage": triage}


def build_output() -> dict[str, Any]:
    return {"handoff": build_handoff(), "source_triage": build_source_triage()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic release maintainer handoff files")
    ap.add_argument("--json", action="store_true", help="Print release maintainer handoff JSON")
    args = ap.parse_args()
    out = write_outputs() if args.write else build_output()
    if args.json:
        print(json.dumps(out["handoff"], sort_keys=True, separators=(",", ":")))
    else:
        h = out["handoff"]
        s = h["source_review_triage"]
        print(
            f"PASS: release maintainer handoff ({h['archive_version']}, "
            f"gate_steps={h['release_gate_inventory']['child_steps']}, "
            f"expired_sources={s['expired_review_count']}, due30={s['due_within_30_days_count']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
