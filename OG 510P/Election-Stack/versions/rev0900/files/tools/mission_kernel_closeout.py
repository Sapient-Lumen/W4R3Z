#!/usr/bin/env python3
"""Build the synthetic Example County mission-kernel closeout index.

This is a forward-motion artifact, not a doctrine note: it maps the seven mission
kernel elements to actual packet evidence, owner roles, and live blockers.  Its
purpose is to show exactly what the current synthetic cube can replay and what
still blocks any live-pilot or public-release claim.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

from example_county_common import DEFAULT_SCENARIO, ROOT, load_json
from release_context import archive_version, release_date

OUTDIR = DEFAULT_SCENARIO.parent
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
REPORT = ROOT / "artifacts" / "reports" / f"mission-kernel-closeout-gaps-rev{REV}.json"
INDEX = OUTDIR / "mission-kernel-closeout-index.json"
PUBLIC = OUTDIR / "public-mission-kernel-closeout.md"

NON_CLAIMS = [
    "Synthetic example only; not live election evidence.",
    "Does not prove that an election outcome is correct.",
    "Does not replace canvass, audit, certification, recount, statutory retention, public-records, or court process.",
    "Does not authorize live pilot, public release, production signing, current voter instruction, or legal reliance.",
]


def evidence_map() -> dict[str, Any]:
    path = OUTDIR / "evidence-map.json"
    if not path.exists():
        raise SystemExit("missing evidence-map.json; run tools/example_county_output_pack.py --write first")
    return load_json(path)


def packet_index(evidence: dict[str, Any]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for phase in evidence.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        for p in phase.get("packets") or []:
            if not isinstance(p, dict):
                continue
            kind = str(p.get("kind") or "")
            if kind:
                out[kind] = {
                    "path": str(p.get("path") or ""),
                    "kind": kind,
                    "manifest_sha256": str(p.get("manifest_sha256") or ""),
                    "verification_status": str(p.get("verification_status") or ""),
                }
    return out


def packet_refs(index: dict[str, dict[str, str]], kinds: list[str], purpose: str) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for kind in kinds:
        row = index.get(kind)
        if not row:
            continue
        refs.append({
            "ref_type": "packet",
            "path": row["path"],
            "kind": row["kind"],
            "manifest_sha256": row["manifest_sha256"],
            "verification_status": row["verification_status"],
            "purpose": purpose,
        })
    return refs


def static_ref(ref_type: str, path: str, purpose: str) -> dict[str, str]:
    return {"ref_type": ref_type, "path": path, "purpose": purpose}


def count_duplicate_verify_packet_defs() -> int:
    count = 0
    for rel in ["tools/example_county_pilot_smoke.py", "tools/example_county_output_pack.py"]:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "verify_packet":
                count += 1
    return count


def build_closeout() -> dict[str, Any]:
    scenario = load_json(DEFAULT_SCENARIO)
    evidence = evidence_map()
    idx = packet_index(evidence)
    closeout_id = f"MKC-EXAMPLE-COUNTY-2026-MUNI-rev{REV}"
    generated_at = release_date(ROOT) + "T00:00:00Z"

    elements = [
        {
            "element_id": "K01_AUTHORIZED_ELECTION_DEFINITION",
            "mission_element": "Authorized election definition, official channels, and election parameters are bound before downstream evidence relies on them.",
            "status": "SYNTHETIC_REPLAY_PASS",
            "owner_role": "jurisdiction authority liaison",
            "evidence_refs": packet_refs(idx, [
                "hfv.public.official_channel_directory",
                "hfv.public.well_known_discovery",
                "hfv.public.notice_signing_keyset",
                "hfv.election.parameters_bundle",
            ], "bootstrap official channels and election definition for the synthetic scenario"),
            "closure_test": "A local adopter must supply a signed authority-scope adoption record, approved official-channel roster, and election definition export whose digests match the closeout packet.",
            "live_blockers": ["no named jurisdiction adoption record", "no locally approved official-channel roster", "no production election definition export"],
            "linked_proof_obligations": ["PO-003", "PO-004"],
            "linked_claims": ["CLM-004", "CLM-005"],
            "linked_hazards": ["HZ-004", "HZ-006"],
            "linked_risks": ["R13", "R19"],
        },
        {
            "element_id": "K02_BALLOT_ACCOUNTING_AND_CUSTODY",
            "mission_element": "Ballot accounting, reporting-unit completeness, custody anchors, and preservation boundaries are present before result claims are interpreted.",
            "status": "SYNTHETIC_PARTIAL",
            "owner_role": "custody and ballot accounting lead",
            "evidence_refs": packet_refs(idx, [
                "hfv.results.closeout_index",
                "hfv.results.cross_register_consistency_report",
            ], "synthetic closeout and aggregate consistency evidence only") + [
                static_ref("report", f"artifacts/reports/ballot-accounting-reconciliation-rev{REV}.json", "synthetic K02/K03 reconciliation between ballot-accounting ledger and BD/CVR counts; not live custody evidence"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-accounting-minimal.json", "synthetic ballot-accounting ledger fixture used by the reconciliation seam"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-ballot-accounting-reconciliation.md", "public non-custody boundary for the ballot-accounting reconciliation"),
                static_ref("report", f"artifacts/reports/election-event-log-reconciliation-rev{REV}.json", "synthetic event-chain witness that digest-binds accounting/replay artifacts; not live EEL evidence"),
                static_ref("report", "artifacts/reports/evidence-custody-provenance-matrix.json", "current no-go matrix for live custody/provenance reliance"),
                static_ref("template", "artifacts/templates/evidence-custody-provenance-worksheet.md", "worksheet required before live field evidence can be relied on"),
            ],
            "closure_test": "Every reporting unit must have ballot accounting totals, custody transfer/seal records, public/private derivative separation, and disposition records linked by digest.",
            "live_blockers": ["no real ballot-accounting export", "no live ballot-accounting reconciliation transcript from jurisdiction bytes", "no scanned or signed custody transfer records", "no local records-custodian approval", "synthetic closeout payload uses placeholder custody digests"],
            "linked_proof_obligations": ["PO-109"],
            "linked_claims": ["CLM-011"],
            "linked_hazards": ["HZ-003", "HZ-010"],
            "linked_risks": ["R1", "R21", "R67"],
        },
        {
            "element_id": "K03_STANDARDIZED_RESULTS_EXPORTS",
            "mission_element": "Standardized results/CVR-facing exports and release packages are content-addressed and independently replayable.",
            "status": "SYNTHETIC_REPLAY_PASS",
            "owner_role": "results export and verifier lead",
            "evidence_refs": packet_refs(idx, [
                "hfv.results.release_package",
                "hfv.results.closeout_index",
                "hfv.results.cross_register_consistency_report",
            ], "replayable synthetic results packet set") + [
                static_ref("report", f"artifacts/reports/cdf-export-replay-report-rev{REV}.json", "primary executable synthetic BD/CVR/ERR replay bridge and negative controls; not full NIST CDF conformance"),
                static_ref("report", f"artifacts/reports/cdf-independent-replay-verifier-rev{REV}.json", "separate synthetic verifier transcript that recomputes totals without importing the primary adapter"),
                static_ref("report", f"artifacts/reports/ballot-accounting-reconciliation-rev{REV}.json", "synthetic accounting reconciliation proving replayed CVR rows are checked against reporting-unit ballot counts"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/canonical-results-object-from-cdf.json", "CRO derived from synthetic CDF minimal projection replay"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json", "synthetic EEL-style chain binding CDF/accounting/replay artifacts by digest and time order"),
                static_ref("report", f"artifacts/reports/election-event-log-reconciliation-rev{REV}.json", "event-chain reconciliation report with broken-hash/digest/timestamp/missing-role negative controls"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-election-event-log-reconciliation.md", "public non-live/non-conformance boundary for the synthetic event-chain witness"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-cdf-independent-verifier.md", "public non-conformance boundary for the independent synthetic verifier transcript"),
            ],
            "closure_test": "A jurisdiction must provide actual CVR/results exports and an adapter transcript proving the closeout packet was reproduced from those bytes, not hand-authored examples; the current fixture proves only the replay seam, independent synthetic transcript, event-chain witness, and negative controls.",
            "live_blockers": ["no real CVR export", "no real election-results export", "no jurisdiction-system adapter transcript", "synthetic projection is not full NIST CDF/EEL conformance"],
            "linked_proof_obligations": ["PO-004", "PO-106"],
            "linked_claims": ["CLM-003", "CLM-008"],
            "linked_hazards": ["HZ-003"],
            "linked_risks": ["R23", "R53"],
        },
        {
            "element_id": "K04_AUDIT_RECOUNT_ADJUDICATION",
            "mission_element": "Audit, recount, adjudication, cure, and dispute evidence are captured as first-class closeout inputs rather than narrative afterthoughts.",
            "status": "LIVE_BLOCKED_MISSING_EVIDENCE",
            "owner_role": "audit adjudication and dispute lead",
            "evidence_refs": [
                static_ref("registry", "artifacts/registries/human-review-handoff-playbook.csv", "review routing scaffold"),
                static_ref("registry", "artifacts/registries/trust-recovery-playbook.csv", "failure and recovery scaffold"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/human-review-matrix.json", "synthetic reviewer routing output"),
            ],
            "closure_test": "At least one live or independently observed drill must attach audit/recount/adjudication records, dissent, reviewer signoff, remedy, and closeout status to the packet.",
            "live_blockers": ["no completed live audit drill", "no recount/adjudication artifact", "no dispute-to-remedy transcript", "no independent reviewer signoff"],
            "linked_proof_obligations": ["PO-109"],
            "linked_claims": ["CLM-011"],
            "linked_hazards": ["HZ-011", "HZ-012"],
            "linked_risks": ["R1", "R19", "R73"],
        },
        {
            "element_id": "K05_AUTHENTICATED_OFFICIAL_NOTICES",
            "mission_element": "Official notices, corrections, publication contracts, feeds, and parity evidence are digest-bound and replayable.",
            "status": "SYNTHETIC_REPLAY_PASS",
            "owner_role": "public notice and accessibility lead",
            "evidence_refs": packet_refs(idx, [
                "hfv.public.notice",
                "hfv.public.notice_feed",
                "hfv.publication.contract",
                "hfv.publication.compliance",
                "hfv.public_surface.parity_snapshot",
                "hfv.public_surface.security_snapshot",
                "hfv.liveness.beacon",
            ], "public notice and public-surface synthetic packet set") + [
                static_ref("report", "artifacts/reports/accessibility-language-matrix.json", "current no-go matrix for public voter-facing release"),
            ],
            "closure_test": "Public release requires local approval plus accessibility, language access, redaction, plain-language, and fallback/help review records.",
            "live_blockers": ["no local public-release approval", "no accessibility/language signoff", "no redaction signoff"],
            "linked_proof_obligations": ["PO-004", "PO-107", "PO-110"],
            "linked_claims": ["CLM-005", "CLM-009", "CLM-012"],
            "linked_hazards": ["HZ-002", "HZ-003"],
            "linked_risks": ["R7", "R31", "R58"],
        },
        {
            "element_id": "K06_INDEPENDENT_VERIFIER_DISAGREEMENT_FAILURE",
            "mission_element": "Independent verifier outputs include success, expected failure, disagreement, and non-certification boundaries.",
            "status": "SYNTHETIC_REPLAY_PASS",
            "owner_role": "independent verification coordinator",
            "evidence_refs": packet_refs(idx, [
                "hfv.verifier.report",
                "hfv.verifier.packet_verification_report",
            ], "published verifier outputs") + [
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/negative-control-report.json", "expected-failure verifier regression evidence"),
                static_ref("report", f"artifacts/reports/cdf-independent-replay-verifier-rev{REV}.json", "synthetic independent replay transcript for exported-result total agreement"),
                static_ref("report", f"artifacts/reports/ballot-accounting-reconciliation-rev{REV}.json", "synthetic reconciliation transcript for ballot-accounting and CVR count agreement"),
                static_ref("report", f"artifacts/reports/election-event-log-reconciliation-rev{REV}.json", "synthetic event-chain transcript linking replay/accounting outputs by digest"),
                static_ref("report", "artifacts/reports/independent-review-matrix.json", "current no-go matrix for independent-review claims"),
            ],
            "closure_test": "Two outside reviewers must run the verifier from a clean checkout, disclose conflicts/scope, publish transcripts, and preserve dissent/remediation records.",
            "live_blockers": ["no outside verifier transcript", "no conflict disclosures", "no public independent-review summary approval"],
            "linked_proof_obligations": ["PO-002", "PO-106"],
            "linked_claims": ["CLM-002", "CLM-007", "CLM-008"],
            "linked_hazards": ["HZ-001", "HZ-002"],
            "linked_risks": ["R9", "R14", "R63"],
        },
        {
            "element_id": "K07_INCIDENT_DISPUTE_REMEDY_CLOSEOUT",
            "mission_element": "Incidents, disputes, remedies, after-action records, and final closeout are linked to exact evidence bytes and human decisions.",
            "status": "SYNTHETIC_PARTIAL",
            "owner_role": "incident remedy and records lead",
            "evidence_refs": packet_refs(idx, [
                "hfv.incident.key_compromise_event",
                "hfv.incident.after_action_report",
                "hfv.results.closeout_index",
            ], "synthetic incident and closeout packet set") + [
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/court-packet-index.csv", "preservation-oriented packet index"),
                static_ref("report", "artifacts/examples/example_county_2026_municipal_pilot/failure-handoff-index.csv", "failure routing output"),
            ],
            "closure_test": "Each incident/dispute must have a trigger, evidence packet, owner decision, remedy, public/private boundary, reviewer dissent route, and final closeout status.",
            "live_blockers": ["no live incident/dispute transcript", "no local remedy owner approval", "no retention/disposition record"],
            "linked_proof_obligations": ["PO-109"],
            "linked_claims": ["CLM-011"],
            "linked_hazards": ["HZ-011", "HZ-012"],
            "linked_risks": ["R19", "R73", "R88"],
        },
    ]

    blockers = [
        {"blocker_id":"MKB-001","priority":"critical","owner_role":"jurisdiction authority liaison","kernel_element_ids":["K01_AUTHORIZED_ELECTION_DEFINITION"],"missing_evidence":"signed local authority-scope adoption record and official-channel roster","next_artifact":"local authority adoption packet","closure_test":"local election official approves scope, election id, channels, and source precedence by digest"},
        {"blocker_id":"MKB-002","priority":"critical","owner_role":"custody and ballot accounting lead","kernel_element_ids":["K02_BALLOT_ACCOUNTING_AND_CUSTODY"],"missing_evidence":"real ballot accounting totals plus custody transfer/seal records","next_artifact":"ballot accounting and custody evidence packet","closure_test":"every reporting unit has ballot counts, custody anchors, exceptions, and disposition records"},
        {"blocker_id":"MKB-003","priority":"critical","owner_role":"results export and verifier lead","kernel_element_ids":["K03_STANDARDIZED_RESULTS_EXPORTS"],"missing_evidence":"real CVR/results/event-log exports and adapter replay transcript","next_artifact":"standards-based export replay and event-chain packet","closure_test":"independent verifier recomputes closeout outputs from jurisdiction export bytes and digest-bound event rows"},
        {"blocker_id":"MKB-004","priority":"critical","owner_role":"audit adjudication and dispute lead","kernel_element_ids":["K04_AUDIT_RECOUNT_ADJUDICATION"],"missing_evidence":"audit/recount/adjudication and dispute-to-remedy records","next_artifact":"audit adjudication remedy packet","closure_test":"at least one observed drill closes from issue through remedy and reviewer signoff"},
        {"blocker_id":"MKB-005","priority":"critical","owner_role":"independent verification coordinator","kernel_element_ids":["K06_INDEPENDENT_VERIFIER_DISAGREEMENT_FAILURE"],"missing_evidence":"external reviewer transcripts, conflicts, dissent, remediation, and retest record","next_artifact":"independent review transcript packet","closure_test":"two independent reviewers reproduce packet verdicts and publish bounded summaries"},
        {"blocker_id":"MKB-006","priority":"high","owner_role":"public notice and accessibility lead","kernel_element_ids":["K05_AUTHENTICATED_OFFICIAL_NOTICES"],"missing_evidence":"redaction, accessibility, language-access, plain-language, and fallback approval","next_artifact":"public release approval packet","closure_test":"local approval records exist before any voter-facing publication claim"},
        {"blocker_id":"MKB-007","priority":"high","owner_role":"incident remedy and records lead","kernel_element_ids":["K07_INCIDENT_DISPUTE_REMEDY_CLOSEOUT"],"missing_evidence":"live incident/dispute closeout and retention/disposition evidence","next_artifact":"incident remedy closeout packet","closure_test":"dispute or incident record carries trigger, owner, remedy, dissent, and disposition"},
    ]

    dup_count = count_duplicate_verify_packet_defs()
    return {
        "archive_version": VERSION,
        "scenario_id": scenario.get("scenario_id"),
        "closeout_id": closeout_id,
        "mission_kernel_version": "1.0",
        "generated_at": generated_at,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "readiness_verdict": "SYNTHETIC_REPLAY_PASS_LIVE_NO_GO",
        "kernel_elements": elements,
        "highest_risk_blockers": blockers,
        "refactor_audit": {
            "status": "PASS" if dup_count == 0 else "FAIL",
            "shared_helper": "tools/example_county_common.py",
            "consumers": [
                "tools/example_county_pilot_smoke.py",
                "tools/example_county_output_pack.py",
                "tools/mission_kernel_closeout.py",
            ],
            "duplicated_verify_packet_functions_after_refactor": dup_count,
            "notes": "Packet iteration and observer verification for the Example County path are centralized in one helper to prevent output-pack/smoke/closeout drift.",
        },
        "non_claims": NON_CLAIMS,
    }


def public_text(closeout: dict[str, Any]) -> str:
    lines = [
        "# Example County mission-kernel closeout",
        "",
        "**Synthetic example only. This is not live election evidence.**",
        "",
        f"Scenario: `{closeout['scenario_id']}`  ",
        f"Archive version: `{closeout['archive_version']}`  ",
        f"Verdict: `{closeout['readiness_verdict']}`",
        "",
        "This file names the seven mission-kernel elements, the synthetic evidence currently wired to each one, and the live blockers that must close before any pilot, public-release, production-authority, or voter-instruction claim.",
        "",
        "## Kernel status",
        "",
    ]
    for element in closeout.get("kernel_elements") or []:
        refs = element.get("evidence_refs") or []
        lines.append(f"- `{element['element_id']}` — `{element['status']}`; owner role: {element['owner_role']}; evidence refs: {len(refs)}; live blockers: {len(element.get('live_blockers') or [])}.")
    lines += [
        "",
        "## Highest-risk next work",
        "",
    ]
    for blocker in closeout.get("highest_risk_blockers") or []:
        lines.append(f"- `{blocker['blocker_id']}` ({blocker['priority']}): {blocker['next_artifact']} — {blocker['closure_test']}")
    lines += [
        "",
        "## Boundary",
        "",
        "This closeout does not prove that an election outcome is correct. It does not replace canvass, audit, certification, recount, statutory retention, public-records, or court process. It is live no-go until local authority, custody, export, audit/adjudication, independent-review, public-release, and remedy/retention evidence exists.",
        "",
    ]
    return "\n".join(lines)


def report_from(closeout: dict[str, Any]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    for e in closeout.get("kernel_elements") or []:
        statuses[str(e.get("status") or "")] = statuses.get(str(e.get("status") or ""), 0) + 1
    critical = [b for b in closeout.get("highest_risk_blockers") or [] if b.get("priority") == "critical"]
    return {
        "archive_version": closeout["archive_version"],
        "scenario_id": closeout["scenario_id"],
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "readiness_verdict": closeout["readiness_verdict"],
        "kernel_element_count": len(closeout.get("kernel_elements") or []),
        "status_counts": statuses,
        "highest_risk_blocker_count": len(closeout.get("highest_risk_blockers") or []),
        "critical_blocker_count": len(critical),
        "next_artifacts": [b.get("next_artifact") for b in closeout.get("highest_risk_blockers") or []],
        "refactor_audit": closeout.get("refactor_audit"),
        "non_claims": closeout.get("non_claims") or [],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write mission-kernel closeout files")
    ap.add_argument("--json", action="store_true", help="print closeout JSON")
    args = ap.parse_args()

    closeout = build_closeout()
    report = report_from(closeout)
    if args.write:
        INDEX.write_text(json.dumps(closeout, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        PUBLIC.write_text(public_text(closeout), encoding="utf-8")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(closeout, sort_keys=True, separators=(",", ":")))
    else:
        print(f"mission-kernel-closeout version={VERSION} verdict={closeout['readiness_verdict']} blockers={len(closeout['highest_risk_blockers'])}")
    return 0 if closeout.get("readiness_verdict") == "SYNTHETIC_REPLAY_PASS_LIVE_NO_GO" and (closeout.get("refactor_audit") or {}).get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
