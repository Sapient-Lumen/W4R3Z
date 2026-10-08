#!/usr/bin/env python3
"""Build release go/no-go, source-review burn-down, and offline-drill reports.

Conservative by design: this tool can support a synthetic research release
verdict, but keeps live-pilot, certification, current-authority, and legal-use
claims behind explicit local evidence gates.
"""
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, json, os, re, sys, tomllib
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = dt.date.fromisoformat(release_date(ROOT))
REG = ROOT / 'artifacts' / 'registries'
REPORTS = ROOT / 'artifacts' / 'reports'
EXAMPLE = ROOT / 'artifacts' / 'examples' / 'example_county_2026_municipal_pilot'
SOURCES = ROOT / 'evidence' / 'lock' / 'external-sources.toml'
CRITERIA = REG / 'release-go-no-go-criteria.csv'

BOUNDARY = ('Synthetic-only release governance output; not live election evidence, not certification, '
            'not an outcome proof, not proof of intent or fraud, not a current-authority determination, and not legal advice.')
SOURCE_BOUNDARY = ('Source burn-down triage is a maintainer queue, not proof that any source is wrong, '
                   'not proof that any voter instruction is current, and not legal advice.')

def release_zip_name() -> str:
    num = int(VERSION[1:])
    return f'The-Election-Stack-rev{num:04d}-YYYY.MM.DD.HH.MM-codename.zip'

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return [{k: (v or '').strip() for k, v in row.items()} for row in csv.DictReader(f)]

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return 'sha256:' + h.hexdigest()

def source_rows() -> list[dict[str, Any]]:
    data = tomllib.loads(SOURCES.read_text(encoding='utf-8'))
    rows = data.get('source')
    return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []

def _date(raw: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(raw)) if raw is not None else None
    except ValueError:
        return None

def _pinned(row: dict[str, Any]) -> bool:
    return bool(re.fullmatch(r'[0-9a-f]{64}', str(row.get('sha256') or '').strip()))

def _tags(row: dict[str, Any]) -> set[str]:
    raw = row.get('tags', [])
    return {str(t).strip() for t in raw if str(t).strip()} if isinstance(raw, list) else set()

def _sort(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (str(r.get('review_by') or '9999-12-31'), str(r.get('id') or '')))

def _examples(rows: list[dict[str, Any]], limit: int = 8) -> str:
    return '; '.join(str(r.get('id') or '').strip() for r in rows[:limit] if str(r.get('id') or '').strip())

def build_source_burndown() -> dict[str, Any]:
    rows = source_rows()
    c7 = RELEASE_DATE + dt.timedelta(days=7)
    c14 = RELEASE_DATE + dt.timedelta(days=14)
    c30 = RELEASE_DATE + dt.timedelta(days=30)
    pinned, unpinned, expired, missing, due7, due14, due30, later = ([] for _ in range(8))
    for r in rows:
        if _pinned(r):
            pinned.append(r); continue
        unpinned.append(r)
        d = _date(r.get('review_by'))
        if d is None: missing.append(r)
        elif d < RELEASE_DATE: expired.append(r)
        elif d <= c30:
            due30.append(r)
            if d <= c7: due7.append(r)
            if d <= c14: due14.append(r)
        else: later.append(r)
    def tagged(*tags: str) -> list[dict[str, Any]]:
        want = set(tags)
        return [r for r in due30 if _tags(r).intersection(want)]
    out: list[dict[str, Any]] = []
    def add(i: str, lane: str, typ: str, vals: list[dict[str, Any]], priority: str, due_by: str, action: str) -> None:
        vals = _sort(vals)
        out.append({'lane_id': i, 'lane': lane, 'lane_type': typ, 'priority': priority, 'due_by': due_by,
                    'count': len(vals), 'example_source_ids': _examples(vals), 'maintainer_action': action,
                    'non_claims': SOURCE_BOUNDARY})
    add('SRB-001','expired_unpinned_review_windows','blocking_disjoint',expired,'blocker',RELEASE_DATE.isoformat(),'Refresh, pin, demote, or replace before release; any nonzero count blocks publication.')
    add('SRB-002','missing_review_by','blocking_disjoint',missing,'blocker',RELEASE_DATE.isoformat(),'Add review_by or pin durable bytes before release; any nonzero count blocks publication.')
    add('SRB-003','due_within_7_days','disjoint_deadline_window',due7,'urgent',c7.isoformat(),'Review or pin these first because they become stale before a one-week maintainer cycle completes.')
    add('SRB-004','due_within_14_days','overlapping_deadline_window',due14,'high',c14.isoformat(),'Review the two-week queue; includes the one-week lane, so do not sum with SRB-003.')
    add('SRB-005','due_within_30_days','disjoint_release_window',due30,'high',c30.isoformat(),'Refresh or pin before relying on these references for current public authority.')
    add('SRB-006','official_websites_due_within_30_days','overlapping_tag_lane',tagged('official_websites'),'high',c30.isoformat(),'Prioritize official-site references used by voter-facing surfaces.')
    add('SRB-007','accessibility_due_within_30_days','overlapping_tag_lane',tagged('accessibility','wcag','wai','aria'),'high',c30.isoformat(),'Prioritize accessibility and language-access references before public-facing output refresh.')
    add('SRB-008','election_authority_due_within_30_days','overlapping_tag_lane',tagged('eac','nist','cisa','ncsl','nass','vvsg','certification'),'high',c30.isoformat(),'Refresh election-authority and election-security references before using them as current guidance.')
    add('SRB-009','ai_governance_due_within_30_days','overlapping_tag_lane',tagged('ai','copilot'),'medium',c30.isoformat(),'Refresh AI-use references before public-message controls are treated as current.')
    add('SRB-010','unpinned_due_later','disjoint_future_queue',later,'normal','after_'+c30.isoformat(),'Keep in ordinary review queue; do not treat as pinned evidence.')
    add('SRB-011','pinned_sources','disjoint_pinned',pinned,'normal','n/a','Keep pinned byte hash and citation role stable; refresh only when source role changes.')
    return {'archive_version': VERSION, 'release_date': RELEASE_DATE.isoformat(), 'source_count': len(rows),
            'pinned_count': len(pinned), 'unpinned_count': len(unpinned), 'expired_review_count': len(expired),
            'missing_review_by_count': len(missing), 'due_within_7_days_count': len(due7),
            'due_within_14_days_count': len(due14), 'due_within_30_days_count': len(due30),
            'official_websites_due_within_30_days_count': len(tagged('official_websites')),
            'accessibility_due_within_30_days_count': len(tagged('accessibility','wcag','wai','aria')),
            'election_authority_due_within_30_days_count': len(tagged('eac','nist','cisa','ncsl','nass','vvsg','certification')),
            'ai_governance_due_within_30_days_count': len(tagged('ai','copilot')), 'rows': out,
            'boundary': SOURCE_BOUNDARY, 'lane_counting_note': 'Some tag lanes overlap deadline lanes; use lane_type before summing counts.'}

def build_offline_drill() -> dict[str, Any]:
    return {'archive_version': VERSION, 'release_date': RELEASE_DATE.isoformat(), 'synthetic_only': True, 'boundary': BOUNDARY,
            'steps': [
                {'step_id':'OVD-001','command':f'python3 scripts/verify_release_zip.py /path/to/{release_zip_name()}','expected_result':'PASS release ZIP verified; version and manifest counts match the carrier.','evidence_output':'terminal transcript or release maintainer handoff record'},
                {'step_id':'OVD-002','command':f'python3 scripts/extract_release_zip.py /path/to/{release_zip_name()} /tmp/election-stack-{VERSION}-extract','expected_result':'PASS safe extraction into a new concrete directory; no symlink or traversal side effects.','evidence_output':'extractor transcript plus extracted tree path'},
                {'step_id':'OVD-003','command':f'python3 scripts/verify_manifest.py /tmp/election-stack-{VERSION}-extract','expected_result':'PASS extracted tree matches MANIFEST.sha256.','evidence_output':'manifest-verifier transcript'},
                {'step_id':'OVD-004','command':'python3 tools/example_county_output_pack.py --json','expected_result':f'PASS JSON reports the current {VERSION} synthetic scenario and packet count.','evidence_output':'artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json'},
                {'step_id':'OVD-005','command':'python3 tools/example_county_negative_control_runner.py --json','expected_result':'PASS only when temporary tampered packets fail with expected public problem codes.','evidence_output':'artifacts/examples/example_county_2026_municipal_pilot/negative-control-report.json'},
                {'step_id':'OVD-006','command':'python3 tools/release_go_no_go_pack.py --json','expected_result':'GO for synthetic release; NO-GO for live pilot, certification, current-authority, and legal-use claims.','evidence_output':'artifacts/reports/release-go-no-go-decision.json'},
                {'step_id':'OVD-007','command':'python3 tools/redaction_publication_pack.py --json','expected_result':'PASS JSON reports the current synthetic redaction/publication no-go matrix and policy count.','evidence_output':'artifacts/reports/redaction-publication-matrix.json'},
                {'step_id':'OVD-008','command':'python3 tools/accessibility_language_pack.py --json','expected_result':'PASS JSON reports the current synthetic accessibility/language publication no-go matrix and policy count.','evidence_output':'artifacts/reports/accessibility-language-matrix.json'},
                {'step_id':'OVD-009','command':'python3 tools/evidence_custody_provenance_pack.py --json','expected_result':'PASS JSON reports the current synthetic custody/provenance no-go matrix and policy count.','evidence_output':'artifacts/reports/evidence-custody-provenance-matrix.json'},
                {'step_id':'OVD-010','command':'python3 tools/independent_review_conflict_pack.py --json','expected_result':'PASS JSON reports the current synthetic independent-review/conflict no-go matrix and policy count.','evidence_output':'artifacts/reports/independent-review-matrix.json'},
                {'step_id':'OVD-011','command':'python3 tools/adopter_authority_capture_pack.py --json','expected_result':'PASS JSON reports quarantined state/local rows as missing adopter capture with promotion blocked.','evidence_output':'artifacts/reports/adopter-authority-capture-matrix.json'},
                {'step_id':'OVD-012','command':'python3 tools/adopter_capture_record_validator.py --json','expected_result':'PASS JSON reports capture-record fixtures, expected negative failures, and zero shape-valid promotion approvals.','evidence_output':'artifacts/reports/adopter-capture-record-validation-report.json'},
                {'step_id':'OVD-013','command':'python3 tools/mission_kernel_live_evidence_intake.py --json','expected_result':'PASS JSON reports the current live-evidence intake as no-go with zero shipped live objects.','evidence_output':'artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json'},
                {'step_id':'OVD-014','command':'python3 scripts/check_mission_kernel_evidence_submitter.py','expected_result':'PASS non-production drill hashes external temporary records, rejects governed synthetic-tree paths, and reports zero live evidence objects.','evidence_output':'release-gate slice transcript'},
                {'step_id':'OVD-015','command':'python3 scripts/check_mission_kernel_full_drill_replay.py','expected_result':'PASS full seven-work-item non-production drill replay digest-binds every required evidence class, reports zero live objects, and makes no live-readiness claim.','evidence_output':'artifacts/reports/mission-kernel-full-drill-replay-audit-rev' + VERSION.removeprefix('v').zfill(4) + '.json'},
                {'step_id':'OVD-016','command':'python3 scripts/check_cdf_export_replay.py','expected_result':'PASS synthetic BD/CVR/ERR minimal projection replay recomputes option totals, emits a CRO, and negative controls fail on mismatch/unknown ID/overvote without claiming full NIST conformance.','evidence_output':'artifacts/reports/cdf-export-replay-report-rev' + VERSION.removeprefix('v').zfill(4) + '.json'},
                {'step_id':'OVD-017','command':'python3 scripts/check_cdf_independent_replay_verifier.py','expected_result':'PASS separately implemented synthetic verifier recomputes BD/CVR/ERR totals, agrees with the primary replay report and CRO, and negative controls fail on mismatch/unknown ID/overvote/report drift/CRO drift without claiming full NIST conformance or external review.','evidence_output':'artifacts/reports/cdf-independent-replay-verifier-rev' + VERSION.removeprefix('v').zfill(4) + '.json'},
                {'step_id':'OVD-018','command':'python3 scripts/check_ballot_accounting_reconciler.py','expected_result':'PASS synthetic ballot-accounting ledger reconciles to BD/CVR reporting-unit counts, contest selection slots, undervotes, and overvote rows; negative controls fail on count drift, undervote drift, and unknown units without claiming live custody evidence.','evidence_output':'artifacts/reports/ballot-accounting-reconciliation-rev' + VERSION.removeprefix('v').zfill(4) + '.json'},
                {'step_id':'OVD-019','command':'python3 scripts/check_election_event_log_reconciler.py','expected_result':'PASS synthetic event-chain witness digest-binds BD/CVR/ERR/accounting, replay reports, CRO, and public boundary outputs; negative controls fail on broken previous hashes, digest drift, timestamp regression, and missing required roles without claiming live EEL/CDF conformance.','evidence_output':'artifacts/reports/election-event-log-reconciliation-rev' + VERSION.removeprefix('v').zfill(4) + '.json'},
                {'step_id':'OVD-020','command':'python3 scripts/release_gate.py --from check_release_go_no_go_pack.py --to check_release_go_no_go_pack.py','expected_result':'PASS go/no-go registry, reports, source burn-down, and public boundary language are fresh.','evidence_output':'release-gate slice transcript'},
            ]}

def _criteria_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for r in rows: counts[r.get('decision','')] = counts.get(r.get('decision',''),0)+1
    return {'criteria_count': len(rows), 'decision_counts': counts,
            'go_synthetic_count': counts.get('GO_SYNTHETIC_RELEASE',0),
            'no_go_live_or_claim_count': sum(counts.get(k,0) for k in ['NO_GO_LIVE_PILOT','NO_GO_CERTIFICATION','NO_GO_LEGAL_USE','NO_GO_CURRENT_AUTHORITY']),
            'conditional_review_count': counts.get('CONDITIONAL_REVIEW',0)}

def build_decision(source: dict[str, Any], offline: dict[str, Any]) -> dict[str, Any]:
    rows = read_csv(CRITERIA)
    smoke = load_json(EXAMPLE / 'smoke-report.json'); score = load_json(EXAMPLE / 'evaluator-scorecard.json')
    negative = load_json(EXAMPLE / 'negative-control-report.json'); handoff = load_json(REPORTS / 'release-maintainer-handoff.json')
    local = load_json(REPORTS / 'local-pilot-intake-matrix.json')
    redaction = load_json(REPORTS / 'redaction-publication-matrix.json')
    accessibility = load_json(REPORTS / 'accessibility-language-matrix.json')
    custody = load_json(REPORTS / 'evidence-custody-provenance-matrix.json')
    independent = load_json(REPORTS / 'independent-review-matrix.json')
    adopter_capture = load_json(REPORTS / 'adopter-authority-capture-matrix.json')
    capture_validation = load_json(REPORTS / 'adopter-capture-record-validation-report.json')
    live_intake = load_json(EXAMPLE / 'live-closeout-evidence-intake-status.json')
    rev = VERSION.removeprefix('v').zfill(4)
    full_drill = load_json(REPORTS / f'mission-kernel-full-drill-replay-audit-rev{rev}.json')
    cdf_replay = load_json(REPORTS / f'cdf-export-replay-report-rev{rev}.json')
    cdf_independent = load_json(REPORTS / f'cdf-independent-replay-verifier-rev{rev}.json')
    ballot_accounting = load_json(REPORTS / f'ballot-accounting-reconciliation-rev{rev}.json')
    event_log_reconciliation = load_json(REPORTS / f'election-event-log-reconciliation-rev{rev}.json')
    cdf_dir = EXAMPLE / 'cdf'
    refs = [REPORTS/'release-maintainer-handoff.json', REPORTS/'local-pilot-intake-matrix.json', REPORTS/'local-pilot-no-go-notice.md', REPORTS/'redaction-publication-matrix.json', REPORTS/'redaction-publication-no-go-notice.md', REPORTS/'accessibility-language-matrix.json', REPORTS/'accessibility-language-no-go-notice.md', REPORTS/'evidence-custody-provenance-matrix.json', REPORTS/'evidence-custody-no-go-notice.md', REPORTS/'independent-review-matrix.json', REPORTS/'independent-review-no-go-notice.md', REPORTS/'adopter-authority-capture-matrix.json', REPORTS/'adopter-authority-capture-summary.json', REPORTS/'adopter-capture-record-validation-report.json', EXAMPLE/'live-closeout-evidence-intake-status.json', EXAMPLE/'live-closeout-evidence-submission-empty.json', REPORTS/f'mission-kernel-full-drill-replay-audit-rev{rev}.json', EXAMPLE/'public-full-closeout-drill-replay.md', REPORTS/f'cdf-export-replay-report-rev{rev}.json', REPORTS/f'cdf-independent-replay-verifier-rev{rev}.json', REPORTS/f'ballot-accounting-reconciliation-rev{rev}.json', REPORTS/f'election-event-log-reconciliation-rev{rev}.json', cdf_dir/'election-event-log-minimal.json', cdf_dir/'public-election-event-log-reconciliation.md', cdf_dir/'ballot-accounting-minimal.json', cdf_dir/'public-ballot-accounting-reconciliation.md', cdf_dir/'canonical-results-object-from-cdf.json', cdf_dir/'cdf-mapping-manifest.json', cdf_dir/'public-cdf-export-replay.md', cdf_dir/'public-cdf-independent-verifier.md', EXAMPLE/'evidence-map.json', EXAMPLE/'evaluator-scorecard.json', EXAMPLE/'negative-control-report.json', CRITERIA]
    return {'archive_version': VERSION, 'release_date': RELEASE_DATE.isoformat(), 'decision_id': f'RGN-{VERSION}',
            'topline_decision':'GO_SYNTHETIC_RELEASE_ONLY',
            'live_pilot_decision':'NO_GO_LIVE_PILOT_WITHOUT_LOCAL_INTAKE_REDACTION_REVIEW_ACCESSIBILITY_LANGUAGE_REVIEW_CUSTODY_PROVENANCE_INDEPENDENT_REVIEW_EXTERNAL_REVIEW_SOURCE_REFRESH_AND_LEDGER_EVIDENCE',
            'certification_decision':'NO_GO_CERTIFICATION_CLAIMS',
            'current_authority_decision':'NO_GO_CURRENT_AUTHORITY_WITHOUT_SOURCE_REFRESH_OR_PINNING',
            'legal_use_decision':'NO_GO_LEGAL_USE_WITHOUT_COUNSEL_REVIEWED_JURISDICTION_WORKSHEET',
            'synthetic_only': True, 'no_live_deployment_claim': True, 'boundary': BOUNDARY,
            'current_signals': {'scenario_id': smoke.get('scenario_id'), 'smoke_status': smoke.get('status'),
                                'scorecard_status': score.get('status'), 'scorecard_total_points': score.get('total_points'),
                                'scorecard_max_points': score.get('max_points'), 'negative_control_status': negative.get('status'),
                                'negative_control_fixture_count': negative.get('fixture_count'),
                                'release_maintainer_handoff_version': handoff.get('archive_version'),
                                'local_pilot_intake_decision': local.get('decision'),
                                'local_pilot_missing_live_evidence_count': local.get('missing_live_evidence_count'),
                                'source_due_within_30_days_count': source.get('due_within_30_days_count'),
                                'source_expired_review_count': source.get('expired_review_count'),
                                'redaction_publication_decision': redaction.get('decision'),
                                'redaction_missing_local_approval_count': redaction.get('missing_local_approval_count'),
                                'accessibility_language_decision': accessibility.get('decision'),
                                'accessibility_language_missing_local_approval_count': accessibility.get('missing_local_approval_count'),
                                'custody_provenance_decision': custody.get('decision'),
                                'custody_provenance_missing_record_count': custody.get('missing_local_custody_record_count'),
                                'independent_review_decision': independent.get('decision'),
                                'independent_review_missing_evidence_count': independent.get('missing_independent_review_evidence_count'),
                                'adopter_capture_missing_count': adopter_capture.get('missing_capture_count'),
                                'adopter_capture_quarantined_source_count': adopter_capture.get('quarantined_source_count'),
                                'capture_record_fixture_count': capture_validation.get('record_count'),
                                'capture_record_negative_fixture_count': capture_validation.get('negative_fixture_count'),
                                'capture_record_expectation_failure_count': capture_validation.get('expectation_failure_count'),
                                'capture_record_valid_promotion_allowed_count': capture_validation.get('valid_promotion_allowed_count'),
                                'mission_kernel_live_evidence_intake_decision': live_intake.get('decision'),
                                'mission_kernel_live_evidence_intake_live_object_count': live_intake.get('live_evidence_object_count'),
                                'mission_kernel_live_evidence_intake_drill_object_count': live_intake.get('drill_evidence_object_count'),
                                'mission_kernel_live_evidence_intake_valid_drill_object_count': live_intake.get('valid_drill_evidence_object_count'),
                                'mission_kernel_live_evidence_intake_missing_item_count': live_intake.get('missing_live_evidence_item_count'),
                                'mission_kernel_full_drill_decision': full_drill.get('decision'),
                                'mission_kernel_full_drill_work_item_count': full_drill.get('work_item_count'),
                                'mission_kernel_full_drill_complete_item_count': full_drill.get('complete_drill_item_count'),
                                'mission_kernel_full_drill_required_evidence_class_count': full_drill.get('required_evidence_class_count'),
                                'mission_kernel_full_drill_valid_drill_object_count': full_drill.get('valid_drill_evidence_object_count'),
                                'mission_kernel_full_drill_live_object_count': full_drill.get('live_evidence_object_count'),
                                'mission_kernel_full_drill_leak_count': full_drill.get('local_path_leak_count'),
                                'mission_kernel_full_drill_overclaim_count': full_drill.get('live_overclaim_term_count'),
                                'cdf_export_replay_decision': cdf_replay.get('decision'),
                                'cdf_export_replay_comparison_row_count': (cdf_replay.get('counts') or {}).get('comparison_row_count'),
                                'cdf_export_replay_error_count': (cdf_replay.get('counts') or {}).get('error_count'),
                                'cdf_export_replay_cvr_record_count': (cdf_replay.get('counts') or {}).get('cvr_record_count'),
                                'cdf_export_replay_no_full_nist_conformance_claim': cdf_replay.get('no_full_nist_conformance_claim'),
                                'cdf_independent_replay_decision': cdf_independent.get('decision'),
                                'cdf_independent_replay_comparison_row_count': (cdf_independent.get('counts') or {}).get('comparison_row_count'),
                                'cdf_independent_replay_error_count': (cdf_independent.get('counts') or {}).get('error_count'),
                                'cdf_independent_replay_cvr_record_count': (cdf_independent.get('counts') or {}).get('cvr_record_count'),
                                'cdf_independent_replay_no_full_nist_conformance_claim': cdf_independent.get('no_full_nist_conformance_claim'),
                                'cdf_independent_replay_primary_agrees': cdf_independent.get('primary_report_agrees'),
                                'cdf_independent_replay_cro_agrees': cdf_independent.get('cro_agrees'),
                                'ballot_accounting_reconciliation_decision': ballot_accounting.get('decision'),
                                'ballot_accounting_reconciliation_error_count': (ballot_accounting.get('counts') or {}).get('error_count'),
                                'ballot_accounting_reconciliation_row_count': (ballot_accounting.get('counts') or {}).get('contest_accounting_row_count'),
                                'ballot_accounting_reconciliation_cvr_record_count': (ballot_accounting.get('counts') or {}).get('cvr_record_count'),
                                'ballot_accounting_reconciliation_no_live_custody_claim': ballot_accounting.get('no_live_custody_claim'),
                                'event_log_reconciliation_decision': event_log_reconciliation.get('decision'),
                                'event_log_reconciliation_event_count': (event_log_reconciliation.get('counts') or {}).get('event_count'),
                                'event_log_reconciliation_error_count': (event_log_reconciliation.get('counts') or {}).get('error_count'),
                                'event_log_reconciliation_missing_required_role_count': (event_log_reconciliation.get('counts') or {}).get('missing_required_role_count'),
                                'event_log_reconciliation_no_live_eel_claim': event_log_reconciliation.get('no_live_election_event_log_claim')},
            'criteria_summary': _criteria_summary(rows), 'criteria_rows': rows,
            'source_burndown_ref':'artifacts/reports/source-review-burndown-plan.json',
            'offline_drill_ref':'artifacts/reports/offline-verification-drill-plan.md',
            'local_pilot_intake_ref':'artifacts/reports/local-pilot-intake-matrix.json',
            'redaction_publication_ref':'artifacts/reports/redaction-publication-matrix.json',
            'accessibility_language_ref':'artifacts/reports/accessibility-language-matrix.json',
            'custody_provenance_ref':'artifacts/reports/evidence-custody-provenance-matrix.json',
            'independent_review_ref':'artifacts/reports/independent-review-matrix.json',
            'adopter_authority_capture_ref':'artifacts/reports/adopter-authority-capture-matrix.json',
            'adopter_capture_record_validation_ref':'artifacts/reports/adopter-capture-record-validation-report.json',
            'mission_kernel_live_evidence_intake_ref':'artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json',
            'mission_kernel_full_drill_replay_ref':'artifacts/reports/mission-kernel-full-drill-replay-audit-rev' + VERSION.removeprefix('v').zfill(4) + '.json',
            'mission_kernel_full_drill_public_ref':'artifacts/examples/example_county_2026_municipal_pilot/public-full-closeout-drill-replay.md',
            'cdf_export_replay_ref':'artifacts/reports/cdf-export-replay-report-rev' + VERSION.removeprefix('v').zfill(4) + '.json',
            'cdf_independent_replay_ref':'artifacts/reports/cdf-independent-replay-verifier-rev' + VERSION.removeprefix('v').zfill(4) + '.json',
            'ballot_accounting_reconciliation_ref':'artifacts/reports/ballot-accounting-reconciliation-rev' + VERSION.removeprefix('v').zfill(4) + '.json',
            'event_log_reconciliation_ref':'artifacts/reports/election-event-log-reconciliation-rev' + VERSION.removeprefix('v').zfill(4) + '.json',
            'event_log_fixture_ref':'artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json',
            'output_hashes': {str(p.relative_to(ROOT)): sha256_file(p) for p in refs if p.exists()},
            'non_claims':['This decision record does not certify any election system or election outcome.',
                          'This decision record does not transform synthetic Example County outputs into live deployment evidence.',
                          'This decision record does not determine current voter instructions or legal rights.',
                          'This decision record does not certify accessibility conformance or language-access compliance.',
                          'This decision record does not certify chain of custody or court admissibility.',
                          'This decision record does not create third-party validation or authorize live-system testing.',
                          'This decision record does not treat empty generated intake templates or non-production drills as live evidence.',
                          'This decision record does not treat the full mission-kernel non-production drill replay as live evidence, jurisdiction authorization, certification, or current voter instruction.',
                          'This decision record does not treat the synthetic CDF minimal projection replay as full NIST CDF conformance, live jurisdiction export evidence, certification, or outcome proof.',
                          'This decision record does not treat the separate synthetic CDF verifier as external independent review, full NIST CDF conformance, live jurisdiction export evidence, certification, or outcome proof.',
                          'This decision record does not treat the synthetic ballot-accounting reconciliation as live custody evidence, public-records authorization, certification, or outcome proof.',
                          'This decision record does not treat the synthetic election-event-chain reconciliation as live EEL evidence, full NIST EEL/CDF conformance, the NIST CDF Test Method, certification, or outcome proof.',
                          'This decision record does not replace statutory certification, audits, recounts, contests, or court procedure.']}

def build_output() -> dict[str, Any]:
    source = build_source_burndown(); offline = build_offline_drill(); decision = build_decision(source, offline)
    return {'decision': decision, 'source_burndown': source, 'offline_drill': offline}

def decision_md(d: dict[str, Any], s: dict[str, Any]) -> str:
    sig = d['current_signals']
    lines = ['# Release go/no-go decision record','',f"Archive version: `{d['archive_version']}`  ",f"Release date: `{d['release_date']}`  ",
             'Synthetic-only. This is not live election evidence, not certification, not outcome proof, not proof of intent or fraud, not current-authority determination, and not legal advice.','',
             '## Topline','',f"- Synthetic research release: `{d['topline_decision']}`.",f"- Live pilot use: `{d['live_pilot_decision']}`.",
             f"- Certification claims: `{d['certification_decision']}`.",f"- Current public-authority reliance: `{d['current_authority_decision']}`.",
             f"- Legal/court use: `{d['legal_use_decision']}`.",'','## Current signals','',f"- Scenario: `{sig['scenario_id']}`.",
             f"- Synthetic smoke: `{sig['smoke_status']}`.",f"- Evaluator scorecard: `{sig['scorecard_status']}` `{sig['scorecard_total_points']}/{sig['scorecard_max_points']}`.",
             f"- Negative controls: `{sig['negative_control_status']}` across `{sig['negative_control_fixture_count']}` fixtures.",
             f"- Local pilot intake: `{sig['local_pilot_intake_decision']}` with `{sig['local_pilot_missing_live_evidence_count']}` missing live-evidence rows.",
             f"- Redaction/publication gate: `{sig['redaction_publication_decision']}` with `{sig['redaction_missing_local_approval_count']}` missing approval rows.",
             f"- Accessibility/language gate: `{sig['accessibility_language_decision']}` with `{sig['accessibility_language_missing_local_approval_count']}` missing approval rows.",
             f"- Custody/provenance gate: `{sig['custody_provenance_decision']}` with `{sig['custody_provenance_missing_record_count']}` missing custody-record rows.",
             f"- Independent-review/conflict gate: `{sig['independent_review_decision']}` with `{sig['independent_review_missing_evidence_count']}` missing review-evidence rows.",
             f"- Adopter source-authority capture: `{sig['adopter_capture_missing_count']}` missing captures across `{sig['adopter_capture_quarantined_source_count']}` quarantined state/local rows.",
             f"- Capture-record validator fixtures: `{sig['capture_record_fixture_count']}` fixtures, `{sig['capture_record_negative_fixture_count']}` negative, `{sig['capture_record_expectation_failure_count']}` expectation failures, `{sig['capture_record_valid_promotion_allowed_count']}` valid promotions.",
             f"- Mission-kernel live-evidence intake: `{sig['mission_kernel_live_evidence_intake_decision']}` with `{sig['mission_kernel_live_evidence_intake_live_object_count']}` live objects, `{sig.get('mission_kernel_live_evidence_intake_drill_object_count', 0)}` drill objects, and `{sig['mission_kernel_live_evidence_intake_missing_item_count']}` missing work items.",
             f"- Full mission-kernel non-production drill replay: `{sig['mission_kernel_full_drill_decision']}` with `{sig['mission_kernel_full_drill_complete_item_count']}/{sig['mission_kernel_full_drill_work_item_count']}` work items complete, `{sig['mission_kernel_full_drill_valid_drill_object_count']}` valid drill objects, `{sig['mission_kernel_full_drill_required_evidence_class_count']}` required evidence classes, and `{sig['mission_kernel_full_drill_live_object_count']}` live objects.",
             f"- CDF export replay bridge: `{sig['cdf_export_replay_decision']}` across `{sig['cdf_export_replay_comparison_row_count']}` comparison rows and `{sig['cdf_export_replay_cvr_record_count']}` synthetic CVR records; full NIST conformance claim: `{sig['cdf_export_replay_no_full_nist_conformance_claim'] is False}`.",
             f"- Independent CDF replay verifier: `{sig['cdf_independent_replay_decision']}` across `{sig['cdf_independent_replay_comparison_row_count']}` comparison rows and `{sig['cdf_independent_replay_cvr_record_count']}` synthetic CVR records; primary-report agreement: `{sig['cdf_independent_replay_primary_agrees']}`; CRO agreement: `{sig['cdf_independent_replay_cro_agrees']}`; full NIST conformance claim: `{sig['cdf_independent_replay_no_full_nist_conformance_claim'] is False}`.",
             f"- Ballot-accounting reconciliation: `{sig['ballot_accounting_reconciliation_decision']}` across `{sig['ballot_accounting_reconciliation_row_count']}` contest accounting rows and `{sig['ballot_accounting_reconciliation_cvr_record_count']}` synthetic CVR records; live custody claim: `{sig['ballot_accounting_reconciliation_no_live_custody_claim'] is False}`.",
             f"- Election-event log reconciliation: `{sig['event_log_reconciliation_decision']}` across `{sig['event_log_reconciliation_event_count']}` event rows; missing required roles: `{sig['event_log_reconciliation_missing_required_role_count']}`; live EEL claim: `{sig['event_log_reconciliation_no_live_eel_claim'] is False}`.",
             f"- Source reviews expired at release date: `{sig['source_expired_review_count']}`.",f"- Unpinned sources due within 30 days: `{sig['source_due_within_30_days_count']}`.",'','## Decision criteria','']
    lines += [f"- `{r['criterion_id']}` / `{r['decision']}` — {r['requirement']}" for r in d['criteria_rows']]
    lines += ['', '## Source-review burn-down snapshot','',f"- Sources: `{s['source_count']}`.",f"- Pinned: `{s['pinned_count']}`.",f"- Unpinned: `{s['unpinned_count']}`.",
              f"- Due within 7 days: `{s['due_within_7_days_count']}`.",f"- Due within 14 days: `{s['due_within_14_days_count']}`.",
              f"- Due within 30 days: `{s['due_within_30_days_count']}`.",f"- Official websites due within 30 days: `{s['official_websites_due_within_30_days_count']}`.",'',
              '## Required before live promotion','', '- Complete local-pilot intake requirements with jurisdiction-specific evidence, named owners, and authority boundaries.',
              '- Replace synthetic Example County outputs with jurisdiction-specific artifacts.',
              '- Complete redaction/publication review before public release of local evidence-derived artifacts.',
              '- Complete accessibility/language, plain-language, fallback, and human-help review before voter-facing public release.',
              '- Complete custody/provenance records before treating local packets as field evidence.',
              '- Complete independent-review/conflict disclosures, reviewer scope, transcripts, dissent routes, and remediation/retest records before third-party-validation or live-pilot claims.',
              '- Refresh or pin current-authority sources before voter-facing reliance.', '- Add valid adopter capture records and human approvals before promoting quarantined state/local xrefs into public-answer guidance.', '- Populate live drill, external-review, witness-health, MAPT, TTR, and admissibility ledgers.',
              '- Obtain local counsel and election-office review before court, public-records, or legal-use claims.', '- Run an offline verification drill and preserve its transcript.','']
    return '\n'.join(lines)

def offline_md(o: dict[str, Any]) -> str:
    lines = ['# Offline verification drill plan','',f"Archive version: `{o['archive_version']}`  ",'Synthetic-only. This drill plan is not live election evidence, not certification, and not legal advice.','',
             'The goal is to prove that a reviewer can verify the carrier ZIP, safely extract it, recheck the manifest, and inspect the synthetic Example County outputs without network access.','','## Steps','']
    for st in o['steps']:
        lines += [f"### `{st['step_id']}`",'', '```bash', st['command'], '```','', f"Expected result: {st['expected_result']}",'',f"Evidence output: {st['evidence_output']}",'']
    return '\n'.join(lines)

def write_outputs() -> dict[str, Any]:
    out = build_output(); REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS/'release-go-no-go-decision.json').write_text(json.dumps(out['decision'], sort_keys=True, separators=(',', ':'))+'\n', encoding='utf-8')
    (REPORTS/'release-go-no-go-decision.md').write_text(decision_md(out['decision'], out['source_burndown']), encoding='utf-8')
    (REPORTS/'source-review-burndown-plan.json').write_text(json.dumps(out['source_burndown'], sort_keys=True, separators=(',', ':'))+'\n', encoding='utf-8')
    with (REPORTS/'source-review-burndown-plan.csv').open('w', encoding='utf-8', newline='') as f:
        fields = ['lane_id','lane','lane_type','priority','due_by','count','example_source_ids','maintainer_action','non_claims']
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out['source_burndown']['rows'])
    (REPORTS/'offline-verification-drill-plan.md').write_text(offline_md(out['offline_drill']), encoding='utf-8')
    return out

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); ap.add_argument('--json', action='store_true')
    args = ap.parse_args(); out = write_outputs() if args.write else build_output()
    if args.json: print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        d=out['decision']; s=out['source_burndown']; print(f"decision={d['topline_decision']} live={d['live_pilot_decision']} due30={s['due_within_30_days_count']} version={d['archive_version']}")
    return 0
if __name__ == '__main__': raise SystemExit(main())
