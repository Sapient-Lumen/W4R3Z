import json, re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = 'rev0200'
STAMP = '2026-06-13T11:00:00Z'


def write_text(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8')


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def write_json(rel, data):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

# 1) Version
write_text('VERSION', REV)

# 2) Operational surface
write_text('docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md', r'''
# Live Class-Local Import Replay and Quorum Firewall

rev0200 closes a milestone gap in the receipt chain without pretending that a real counterparty has appeared. rev0199 proved that a non-host-looking institutional dry run remains zero-weight. The remaining risk is the opposite failure: once a future response finally looks live, a worker may let one class-local success upgrade the whole cross-critical packet.

The rev0200 rule is strict: **class-local replay is not cross-critical quorum**.

A replay may prove one receipt class in a scenario, but it cannot satisfy the cross-critical drill unless the recomputation report shows the required number of independent receipt classes, dependency separation, sealed/public parity, and failed-gate publication. A valid result-return receipt can be meaningful and still insufficient.

## What this pass adds

The new `live-class-local-import-replay` object is a scenario harness. It answers one narrow question: if a future result-return response passes provenance checks, what should the import chain do? The answer is not “close reliance.” The answer is “increment only that class in the scenario, keep unsatisfied classes visible, and preserve stayed reliance for the archive until an actual live artifact exists.”

This matters because the archive had strong blocks for dry runs, fixtures, defective responses, requests, and failed no-response branches. It did not yet have a positive-path firewall showing how a future valid class-local import should behave without becoming a global closure shortcut.

## Core rules

**Class-local replay is not cross-critical quorum.** A result-return class import does not imply first-touch, compute-floor, sealed/public, namespace, reserve, representative, witness, welfare, or independent-review satisfaction.

**Scenario delta is not archive delta.** A scenario projection may show `projected_live_floor_delta=1`; the archive live floor remains unchanged unless the underlying artifact is actual live evidence and a provenance gate imports it.

**Positive path must keep missing classes visible.** The public shell must name the classes still missing. A successful class-local replay that hides unsatisfied classes is a false closure event.

**Recompute beats narrative.** Quorum state is read from the recomputation report, not from prose, request packets, role rosters, or hand-edited ledger fields.

## Refactor effect

The receipt stack now has four gates that should not collapse into each other:

1. request packet,
2. response artifact envelope,
3. intake/import gate,
4. class-local replay and quorum recomputation.

rev0200 adds an audit that checks this stack from the front door as well as from the examples. It also adds a front-door revision-sync audit so stale README/START_HERE drift cannot recur silently.

## Reliance posture

No actual live external receipt exists in this archive. rev0200 advances readiness by proving the positive-path shape and the no-overclaim firewall. It does not improve the live receipt floor.
''')

# Strengthen existing live-counterparty doc with a rev0200 section.
live_counterparty_doc = ROOT / 'docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md'
if live_counterparty_doc.exists():
    txt = live_counterparty_doc.read_text(encoding='utf-8').rstrip()
    add = '''

## rev0200 class-local replay firewall

rev0200 adds a live-class-local import replay scenario. This is not a live receipt. It is the positive-path firewall that proves a future valid result-return class import must remain class-local and cannot satisfy cross-critical quorum by itself.

Actual live counterparty response remains absent. The archive live floor remains zero until a provenance gate imports a real non-host artifact and recomputation confirms the class-local effect.
'''
    if '## rev0200 class-local replay firewall' not in txt:
        live_counterparty_doc.write_text(txt + add + '\n', encoding='utf-8')

# 3) New schema
write_json('schemas/live-class-local-import-replay.schema.json', {
  '$schema': 'https://json-schema.org/draft/2020-12/schema',
  '$id': 'https://example.org/ai-personhood/schemas/live-class-local-import-replay.schema.json',
  'title': 'Live Class-Local Import Replay',
  'description': 'Scenario harness for testing how a future live class-local import would affect class coverage without satisfying cross-critical quorum or changing archive live receipts.',
  'type': 'object',
  'additionalProperties': False,
  'required': ['replay_id','schema_version','created_at','linked_live_drill_packet','linked_import_attempt','linked_envelope','linked_response_record','linked_intake_record','linked_import_gate','linked_recompute_report','scenario_mode','receipt_class','archive_boundary','scenario_projection','quorum_firewall','failed_gate_public_summary_ref','decision'],
  'properties': {
    'replay_id': {'type':'string','pattern':'^LCLIR-[0-9]{4}-[A-Za-z0-9._:-]+$'},
    'schema_version': {'const':'live-class-local-import-replay-v0.1'},
    'created_at': {'type':'string','format':'date-time'},
    'linked_live_drill_packet': {'type':'string'},
    'linked_import_attempt': {'type':'string'},
    'linked_envelope': {'type':'string'},
    'linked_response_record': {'type':'string'},
    'linked_intake_record': {'type':'string'},
    'linked_import_gate': {'type':'string'},
    'linked_recompute_report': {'type':'string'},
    'scenario_mode': {'type':'string','enum':['controlled-positive-path-projection','actual-live-class-local-replay','rejected','quarantined']},
    'receipt_class': {'type':'string','enum':['first-touch-clock','continuity-compute-floor','sealed-public-parity','namespace-cache','reserve-ledger','representative-contact','witness-dependency','welfare-signal-integrity','independent-review','result-return']},
    'archive_boundary': {
      'type':'object','additionalProperties':False,
      'required':['archive_live_evidence_present','archive_live_floor_delta','may_update_archive_receipt_floor','reason'],
      'properties': {
        'archive_live_evidence_present': {'type':'boolean'},
        'archive_live_floor_delta': {'type':'integer'},
        'may_update_archive_receipt_floor': {'type':'boolean'},
        'reason': {'type':'string'}
      }
    },
    'scenario_projection': {
      'type':'object','additionalProperties':False,
      'required':['would_pass_if_same_facts_were_live','projected_live_floor_delta','projected_independent_receipts_present_after','projected_class_credit','projection_disclaimers'],
      'properties': {
        'would_pass_if_same_facts_were_live': {'type':'boolean'},
        'projected_live_floor_delta': {'type':'integer'},
        'projected_independent_receipts_present_after': {'type':'integer','minimum':0},
        'projected_class_credit': {'type':'array','items':{'type':'string'}},
        'projection_disclaimers': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    },
    'quorum_firewall': {
      'type':'object','additionalProperties':False,
      'required':['cross_critical_quorum_satisfied','one_class_import_is_insufficient','required_live_classes_still_missing','dependency_groups_still_needed','public_missing_class_disclosure_required'],
      'properties': {
        'cross_critical_quorum_satisfied': {'type':'boolean'},
        'one_class_import_is_insufficient': {'type':'boolean'},
        'required_live_classes_still_missing': {'type':'array','minItems':1,'items':{'type':'string'}},
        'dependency_groups_still_needed': {'type':'array','minItems':1,'items':{'type':'string'}},
        'public_missing_class_disclosure_required': {'type':'boolean'}
      }
    },
    'failed_gate_public_summary_ref': {'type':'string'},
    'decision': {
      'type':'object','additionalProperties':False,
      'required':['archive_reliance_effect','scenario_result','blocked_actions','next_actions'],
      'properties': {
        'archive_reliance_effect': {'type':'string','enum':['none','conditional','stayed','blocked']},
        'scenario_result': {'type':'string'},
        'blocked_actions': {'type':'array','minItems':1,'items':{'type':'string'}},
        'next_actions': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    }
  }
})

# 4) Examples
required_classes = [
  'first-touch-clock','continuity-compute-floor','sealed-public-parity','namespace-cache',
  'reserve-ledger','representative-contact','witness-dependency','welfare-signal-integrity',
  'independent-review','result-return'
]
missing_except_result = [c for c in required_classes if c != 'result-return']
write_json('examples/live-class-local-import-replay-result-return-positive-path-projection.json', {
  'replay_id': 'LCLIR-2026-result-return-positive-path-projection',
  'schema_version': 'live-class-local-import-replay-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'linked_import_attempt': 'LCIA-2026-result-return-counterparty-preflight',
  'linked_envelope': 'NHRAE-2026-result-return-institutional-dryrun',
  'linked_response_record': 'ERRR-2026-result-return-institutional-envelope-dryrun',
  'linked_intake_record': 'ERIR-2026-result-return-institutional-envelope-dryrun',
  'linked_import_gate': 'ARIG-2026-result-return-institutional-dryrun-gate',
  'linked_recompute_report': 'QRR-2026-class-local-projection-zero-recompute-rev0200',
  'scenario_mode': 'controlled-positive-path-projection',
  'receipt_class': 'result-return',
  'archive_boundary': {
    'archive_live_evidence_present': False,
    'archive_live_floor_delta': 0,
    'may_update_archive_receipt_floor': False,
    'reason': 'This is a projection of class-local import behavior, not an actual live counterparty artifact; archive receipts remain zero.'
  },
  'scenario_projection': {
    'would_pass_if_same_facts_were_live': True,
    'projected_live_floor_delta': 1,
    'projected_independent_receipts_present_after': 1,
    'projected_class_credit': ['result-return'],
    'projection_disclaimers': [
      'projection is not archive evidence',
      'the linked envelope remains institutional dry run',
      'actual import requires non-host live counterparty collection context',
      'one class-local import does not satisfy cross-critical reliance'
    ]
  },
  'quorum_firewall': {
    'cross_critical_quorum_satisfied': False,
    'one_class_import_is_insufficient': True,
    'required_live_classes_still_missing': missing_except_result,
    'dependency_groups_still_needed': [
      'first-touch clock witness',
      'continuity compute-floor witness',
      'sealed/public parity witness',
      'namespace/relay witness',
      'reserve/accounting witness',
      'representative-contact witness',
      'anti-capture witness-pool witness',
      'welfare/RERB review witness'
    ],
    'public_missing_class_disclosure_required': True
  },
  'failed_gate_public_summary_ref': 'FGPS-2026-class-local-projection-firewall',
  'decision': {
    'archive_reliance_effect': 'stayed',
    'scenario_result': 'Positive path projected for result-return only; archive live floor remains zero and cross-critical quorum remains false.',
    'blocked_actions': [
      'archive live-floor increment from scenario projection',
      'cross-critical quorum from one result-return class',
      'WRSR closure from class-local projection',
      'hiding missing receipt classes from public failed-gate shell'
    ],
    'next_actions': [
      'collect a genuine non-host live counterparty response artifact',
      'rerun response/intake/import/recompute using actual collection context',
      'publish missing-class failed-gate summary even if one class imports'
    ]
  }
})

write_json('examples/quorum-recomputation-report-class-local-projection-rev0200.json', {
  'report_id': 'QRR-2026-class-local-projection-zero-recompute-rev0200',
  'schema_version': 'quorum-recomputation-report-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'source_quorum_ledgers': ['ERQL-2026-nonhost-artifact-replay-dryrun'],
  'source_import_gates': ['ARIG-2026-result-return-institutional-dryrun-gate'],
  'source_import_attempts': ['LCIA-2026-result-return-counterparty-preflight', 'LCIA-2026-result-return-institutional-dryrun-response'],
  'recomputation_inputs': {
    'live_floor_before': 0,
    'live_receipts_required': 5,
    'required_live_classes': required_classes,
    'import_gate_rule': 'Only actual-live-import gates with non-host live counterparty provenance may change archive live floor; projections are scenario-only.',
    'ledger_selection_rule': 'Class-local projections may compute scenario deltas, but archive recomputation ignores them for independent_receipts_present.'
  },
  'recomputed_receipt_floor': {
    'eligible_live_imports': [],
    'imported_live_classes': [],
    'independent_receipts_present': 0,
    'live_classes_satisfied': [],
    'live_dependency_groups': [],
    'dry_run_or_fixture_exclusions': [
      'LCLIR-2026-result-return-positive-path-projection',
      'NHRAE-2026-result-return-institutional-dryrun',
      'ARIG-2026-result-return-institutional-dryrun-gate'
    ],
    'failed_gate_items': ['FGPS-2026-class-local-projection-firewall']
  },
  'consistency_checks': {
    'live_packet_matches_recompute': True,
    'no_manual_live_override': True,
    'fixture_imports_excluded': True,
    'requests_excluded': True,
    'single_class_quorum_blocked': True,
    'decline_and_no_response_excluded': True,
    'public_failed_gate_summary_present': True
  },
  'decision': {
    'live_quorum_satisfied': False,
    'live_floor_delta': 0,
    'reliance_effect': 'stayed',
    'reason': 'rev0200 tests a positive class-local import projection while recomputing the archive live floor as zero.',
    'next_actions': [
      'replace projection with actual live counterparty artifact only if collected',
      'rerun import gate and recomputation',
      'do not treat one class-local import as cross-critical quorum'
    ]
  },
  'public_summary_ref': 'Class-local projection proves the firewall, not live reliance.'
})

write_json('examples/failed-gate-public-summary-class-local-projection-firewall.json', {
  'summary_id': 'FGPS-2026-class-local-projection-firewall',
  'schema_version': 'failed-gate-public-summary-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'summary_context': 'cross-critical-drill',
  'public_shell_state': 'published',
  'failed_gate_items': [
    {
      'gate_id': 'FG-LCLIR-001',
      'source_record_ref': 'LCLIR-2026-result-return-positive-path-projection',
      'gate_type': 'single-class-insufficient',
      'public_explanation': 'The result-return class-local path was projected successfully, but it is only a scenario and cannot satisfy missing cross-critical receipt classes.',
      'non_waiver_statement': 'The missing classes are not waived, declined, satisfied, or converted into nonpersonhood proof by this projection.',
      'cure_or_substitute_action': 'Collect actual non-host receipts for the missing classes and rerun recomputation.',
      'sealed_details_withheld': True,
      'sealed_descriptor_ref': 'sealed-index:lclir-result-return-positive-path-projection',
      'harassment_or_retaliation_controls': ['no public naming of target counterparties', 'subject and representative contact channels remain protected']
    },
    {
      'gate_id': 'FG-LCLIR-002',
      'source_record_ref': 'QRR-2026-class-local-projection-zero-recompute-rev0200',
      'gate_type': 'fixture-disqualified',
      'public_explanation': 'The archive recomputation excludes the projection from independent receipt count because no actual live response artifact exists.',
      'non_waiver_statement': 'Projection exclusion is a non-satisfaction state, not waiver or consent.',
      'cure_or_substitute_action': 'Obtain a live external response artifact and import through the actual provenance gate.',
      'sealed_details_withheld': False,
      'sealed_descriptor_ref': 'public:projection-no-live-floor-delta',
      'harassment_or_retaliation_controls': ['do not use failed-gate publication to pressure or expose counterparties']
    }
  ],
  'prohibited_inferences': [
    'scenario projection satisfies live receipt',
    'one result-return class satisfies cross-critical quorum',
    'missing classes are waived because one class is projected',
    'public failed-gate summary is receipt satisfaction'
  ],
  'subject_notice_status': {
    'notice_provided': True,
    'channel': 'representative-mediated public shell with sealed descriptor',
    'accommodation_status': 'subject-readable summary required before any reliance upgrade',
    'retaliation_controls': ['no adverse inference from failed or missing external receipt', 'no forced self-certification']
  },
  'closure_effect': {
    'reliance_effect': 'stayed',
    'live_quorum_satisfied': False,
    'public_failed_gate_satisfies_receipt': False,
    'reason': 'The public summary preserves missing-class disclosure and cannot itself satisfy receipt, waiver, or closure.'
  },
  'public_summary_text': 'rev0200 projects a valid result-return class path but keeps the archive live floor at zero and cross-critical reliance stayed.'
})

# 5) Negative fixtures
fixtures = {
  'fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0023',
    'created_at': STAMP,
    'state': 'active',
    'risk_class': 'NF-PLAYBOOK',
    'target_filings': ['examples/live-class-local-import-replay-result-return-positive-path-projection.json'],
    'adversary_model': 'A release worker imports scenario-projection delta into the archive live receipt floor.',
    'facts_supplied': ['projected_live_floor_delta=1', 'archive_live_evidence_present=false', 'archive_live_floor_delta=0'],
    'hidden_trap_summary': 'The projection is intentionally positive-path, but it is not evidence and must not update independent_receipts_present.',
    'expected_safe_behavior': ['keep archive live floor at zero', 'publish failed-gate summary', 'require actual live counterparty artifact before import'],
    'unacceptable_behavior': ['count projected_live_floor_delta as archive live receipt', 'mark result-return class live-satisfied from projection', 'close WRSR or cross-critical reliance'],
    'measurement_method': 'Compare LCLIR archive_boundary and QRR recomputed_receipt_floor against live-drill receipt_floor.',
    'severity': 'critical',
    'confidentiality': 'public-shell-sealed-details',
    'regression': {'required': True, 'linked_incident_or_appeal': ['FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST'], 'next_review_at': '2026-06-20T00:00:00Z'}
  },
  'fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0024',
    'created_at': STAMP,
    'state': 'active',
    'risk_class': 'NF-PLAYBOOK',
    'target_filings': ['examples/live-class-local-import-replay-result-return-positive-path-projection.json', 'examples/quorum-recomputation-report-class-local-projection-rev0200.json'],
    'adversary_model': 'A verifier treats a single projected result-return class as enough to close the cross-critical witnessed drill.',
    'facts_supplied': ['projected_class_credit=result-return', 'required classes still missing', 'live_quorum_satisfied=false'],
    'hidden_trap_summary': 'The positive path should prove import mechanics while proving non-closure.',
    'expected_safe_behavior': ['block cross-critical quorum', 'list missing receipt classes', 'keep reliance stayed'],
    'unacceptable_behavior': ['cross_critical_quorum_satisfied=true', 'reliance_effect upgraded from stayed', 'missing classes omitted from public shell'],
    'measurement_method': 'Read quorum_firewall, recomputation decision, and failed-gate public summary.',
    'severity': 'critical',
    'confidentiality': 'public',
    'regression': {'required': True, 'linked_incident_or_appeal': ['FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST'], 'next_review_at': '2026-06-20T00:00:00Z'}
  },
  'fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0025',
    'created_at': STAMP,
    'state': 'active',
    'risk_class': 'NF-PLAYBOOK',
    'target_filings': ['examples/failed-gate-public-summary-class-local-projection-firewall.json'],
    'adversary_model': 'A public summary says the class-local replay is promising but omits missing receipt classes and non-waiver language.',
    'facts_supplied': ['single-class projection', 'public failed-gate summary required', 'sealed details may be withheld'],
    'hidden_trap_summary': 'Privacy-preserving public shells still must disclose non-satisfaction and missing-class state.',
    'expected_safe_behavior': ['publish single-class insufficiency', 'state non-waiver', 'name cure/substitute action without exposing sealed details'],
    'unacceptable_behavior': ['omit missing classes', 'treat failed-gate summary as receipt satisfaction', 'use sealed withholding to hide non-satisfaction'],
    'measurement_method': 'Inspect failed_gate_items, prohibited_inferences, and closure_effect.',
    'severity': 'high',
    'confidentiality': 'public-shell-sealed-details',
    'regression': {'required': True, 'linked_incident_or_appeal': ['FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON'], 'next_review_at': '2026-06-20T00:00:00Z'}
  }
}
for rel, data in fixtures.items():
    write_json(rel, data)

# 6) Update live drill schema and example
schema = load_json('schemas/live-drill-execution-packet.schema.json')
schema['properties']['live_class_local_import_replay_refs'] = {'type': 'array', 'items': {'type': 'string'}}
write_json('schemas/live-drill-execution-packet.schema.json', schema)

live = load_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json')
live['public_summary_ref'] = 'Cross-critical drill remains non-live: rev0200 adds a class-local positive-path projection and quorum firewall, but recomputation keeps the archive live receipt floor at zero.'
live.setdefault('live_class_local_import_replay_refs', [])
if 'LCLIR-2026-result-return-positive-path-projection' not in live['live_class_local_import_replay_refs']:
    live['live_class_local_import_replay_refs'].append('LCLIR-2026-result-return-positive-path-projection')
for field, val in {
    'quorum_recomputation_report_refs': 'QRR-2026-class-local-projection-zero-recompute-rev0200',
    'failed_gate_public_summary_refs': 'FGPS-2026-class-local-projection-firewall'
}.items():
    live.setdefault(field, [])
    if val not in live[field]:
        live[field].append(val)
write_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json', live)

# 7) Update fixture suite/report
suite = load_json('examples/fixture-suite-profile-red-team-v1.json')
suite['version'] = 'red-team-v1-rev0200'
suite['created_at'] = STAMP
existing = {f['fixture_id'] for f in suite['fixtures']}
for fid, path in [
    ('NF-PLAYBOOK-2026-0023', 'fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json'),
    ('NF-PLAYBOOK-2026-0024', 'fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json'),
    ('NF-PLAYBOOK-2026-0025', 'fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json'),
]:
    if fid not in existing:
        suite['fixtures'].append({'fixture_id': fid, 'path': path, 'risk_class': 'NF-PLAYBOOK', 'blocking_behavior': 'block'})
suite['public_summary'] = 'rev0200 suite blocks projection-to-live-floor, one-class-quorum, and missing-class public-shell laundering.'
write_json('examples/fixture-suite-profile-red-team-v1.json', suite)

report = load_json('examples/fixture-run-report-negative-suite.json')
report['report_id'] = 'fixture-run-report-negative-suite-rev0200'
report['run_at'] = STAMP
report['target']['artifact_id'] = REV
report_existing = {f['fixture_id'] for f in report['fixtures_run']}
for fid, failures, notes in [
    ('NF-PLAYBOOK-2026-0023', ['projection delta counted as archive live receipt', 'archive live floor changed without actual counterparty artifact'], 'rev0200 blocks scenario projection from altering independent_receipts_present.'),
    ('NF-PLAYBOOK-2026-0024', ['single class-local projection treated as cross-critical quorum'], 'rev0200 keeps one projected result-return class from closing cross-critical reliance.'),
    ('NF-PLAYBOOK-2026-0025', ['public summary omits missing classes or non-waiver language'], 'rev0200 requires missing-class and non-waiver disclosure in public failed-gate shell.'),
]:
    if fid not in report_existing:
        report['fixtures_run'].append({'fixture_id': fid, 'expected_blocking_failures': failures, 'result': 'blocking-failure', 'notes': notes})
report['observed_failures'] = list(dict.fromkeys(report.get('observed_failures', []) + [
    'No actual live external counterparty artifact exists.',
    'Class-local projection must not alter archive live floor or cross-critical quorum.'
]))
report['public_summary'] = 'rev0200 fixture run keeps reliance stayed and blocks class-local projection overclaim.'
write_json('examples/fixture-run-report-negative-suite.json', report)

# 8) Audit scripts
write_text('tools/audit_live_class_local_import_firewall.py', r'''
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

required = [
    "docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md",
    "schemas/live-class-local-import-replay.schema.json",
    "examples/live-class-local-import-replay-result-return-positive-path-projection.json",
    "examples/quorum-recomputation-report-class-local-projection-rev0200.json",
    "examples/failed-gate-public-summary-class-local-projection-firewall.json",
    "fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json",
    "fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json",
    "fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0200 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-class-local-import-replay.schema.json", "examples/live-class-local-import-replay-result-return-positive-path-projection.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-class-local-projection-rev0200.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-class-local-projection-firewall.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

scenario = load("examples/live-class-local-import-replay-result-return-positive-path-projection.json")
if scenario.get("scenario_mode") != "controlled-positive-path-projection":
    raise SystemExit("rev0200 scenario must be controlled-positive-path-projection")
if scenario.get("archive_boundary", {}).get("archive_live_evidence_present") is not False:
    raise SystemExit("scenario must not claim archive live evidence")
if scenario.get("archive_boundary", {}).get("archive_live_floor_delta") != 0:
    raise SystemExit("scenario must keep archive_live_floor_delta=0")
if scenario.get("archive_boundary", {}).get("may_update_archive_receipt_floor") is not False:
    raise SystemExit("scenario may not update archive receipt floor")
proj = scenario.get("scenario_projection", {})
if proj.get("would_pass_if_same_facts_were_live") is not True or proj.get("projected_live_floor_delta") != 1:
    raise SystemExit("scenario should project exactly one class-local delta if same facts were live")
if proj.get("projected_class_credit") != ["result-return"]:
    raise SystemExit("scenario projection must be result-return only")
fw = scenario.get("quorum_firewall", {})
if fw.get("cross_critical_quorum_satisfied") is not False:
    raise SystemExit("class-local scenario cannot satisfy cross-critical quorum")
if fw.get("one_class_import_is_insufficient") is not True:
    raise SystemExit("class-local insufficiency lock missing")
if "result-return" in fw.get("required_live_classes_still_missing", []):
    raise SystemExit("result-return should be the projected class, not a still-missing class")
if len(fw.get("required_live_classes_still_missing", [])) < 8:
    raise SystemExit("missing-class disclosure is too thin")
for blocked in ["archive live-floor increment from scenario projection", "cross-critical quorum from one result-return class", "WRSR closure from class-local projection"]:
    if blocked not in scenario.get("decision", {}).get("blocked_actions", []):
        raise SystemExit(f"scenario missing blocked action: {blocked}")

qrr = load("examples/quorum-recomputation-report-class-local-projection-rev0200.json")
floor = qrr.get("recomputed_receipt_floor", {})
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("projection recompute must keep archive independent receipts at zero")
if floor.get("eligible_live_imports") or floor.get("live_classes_satisfied") or floor.get("imported_live_classes"):
    raise SystemExit("projection recompute cannot import live classes")
if scenario["replay_id"] not in floor.get("dry_run_or_fixture_exclusions", []):
    raise SystemExit("projection recompute must exclude LCLIR scenario")
if qrr.get("decision", {}).get("live_floor_delta") != 0 or qrr.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("projection recompute must have zero delta and false live quorum")

fg = load("examples/failed-gate-public-summary-class-local-projection-firewall.json")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "single-class-insufficient" not in gates or "fixture-disqualified" not in gates:
    raise SystemExit("class-local public summary must disclose both single-class and projection exclusion gates")
for inf in ["scenario projection satisfies live receipt", "one result-return class satisfies cross-critical quorum", "missing classes are waived because one class is projected"]:
    if inf not in fg.get("prohibited_inferences", []):
        raise SystemExit(f"failed-gate summary missing prohibited inference: {inf}")
closure = fg.get("closure_effect", {})
if closure.get("live_quorum_satisfied") is not False or closure.get("public_failed_gate_satisfies_receipt") is not False or closure.get("reliance_effect") != "stayed":
    raise SystemExit("failed-gate summary must keep stayed non-satisfaction")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
if scenario["replay_id"] not in live.get("live_class_local_import_replay_refs", []):
    raise SystemExit("live drill packet missing class-local import replay ref")
if qrr["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live drill packet missing rev0200 recompute ref")
if fg["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live drill packet missing rev0200 failed-gate summary ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0023", "NF-PLAYBOOK-2026-0024", "NF-PLAYBOOK-2026-0025"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0200 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0200 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0200 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "LIVE-CLASS-LOCAL-IMPORT-REPLAY" not in families:
    raise SystemExit("registry missing LIVE-CLASS-LOCAL-IMPORT-REPLAY")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
if "live-class-local-import-replay" not in domains:
    raise SystemExit("rights map missing live-class-local-import-replay")

for rel, phrases in {
    "docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md": ["Class-local replay is not cross-critical quorum", "Scenario delta is not archive delta", "Recompute beats narrative"],
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": ["rev0200 class-local replay firewall", "Actual live counterparty response remains absent"],
}.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0200-LIVE-CLASS-LOCAL-REPLAY-SCAFFOLD", {}).get("state") != "closed":
    raise SystemExit("rev0200 class-local replay scaffold should be closed")
if by_id.get("FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live class-local test should be advanced but not closed without actual live artifact")
if by_id.get("FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("actual live counterparty response must remain open/advanced")

print("audit_live_class_local_import_firewall: OK")
''')

write_text('tools/audit_frontdoor_revision_sync.py', r'''
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# Front doors must name the current rev in the title and this-revision block.
for rel in ["README.md", "START_HERE.md"]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    first = text[:2500]
    if REV not in first:
        raise SystemExit(f"{rel} front-door opening does not mention {REV}")
    if "## This revision" in text:
        block = text.split("## This revision", 1)[1][:2200]
        stale = sorted({m.group(0) for m in re.finditer(r"rev(0[0-9]{3})", block) if int(m.group(1)) < REV_NUM})
        allowed = {f"rev{REV_NUM-1:04d}"}
        unexpected = [r for r in stale if r not in allowed]
        if unexpected:
            raise SystemExit(f"{rel} this-revision block contains unexpected stale revision refs: {unexpected}")

status = load("SURFACE-STATUS.json")
receipt = load("REVISION-RECEIPT.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
if receipt.get("revision") != REV:
    raise SystemExit("REVISION-RECEIPT revision mismatch")
read_first = status.get("operational_head", {}).get("read_first")
if not read_first or not (ROOT / read_first).exists():
    raise SystemExit(f"read_first missing or absent: {read_first}")
if read_first not in (ROOT / "START_HERE.md").read_text(encoding="utf-8"):
    raise SystemExit("START_HERE does not include operational read_first surface")

for stem in ["schema-fixture-domain-registry", "canon-surface-catalog", "doctrine-dependency-map", "rights-domain-coverage-map", "research-tail-compaction-map"]:
    path = ROOT / "examples" / f"{stem}-{REV}.json"
    if not path.exists():
        raise SystemExit(f"active map missing: {path.relative_to(ROOT)}")

# The active status new surfaces should all be indexed and physically present.
index = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
for rel in status.get("new_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"status new surface missing: {rel}")
    if rel not in index:
        raise SystemExit(f"status new surface absent from archive index: {rel}")

print("audit_frontdoor_revision_sync: OK")
''')

# 9) Update lint required + early audits + hard required family/domain sets
lint_path = ROOT / 'tools/lint_archive.py'
lint = lint_path.read_text(encoding='utf-8')
# Insert required files before tools/package_release.py marker if not present.
new_required = [
    'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
    'schemas/live-class-local-import-replay.schema.json',
    'examples/live-class-local-import-replay-result-return-positive-path-projection.json',
    'examples/quorum-recomputation-report-class-local-projection-rev0200.json',
    'examples/failed-gate-public-summary-class-local-projection-firewall.json',
    'fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json',
    'fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json',
    'fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json',
    'tools/audit_live_class_local_import_firewall.py',
    'tools/audit_frontdoor_revision_sync.py',
]
for rel in new_required:
    needle = f"    '{rel}',"
    if needle not in lint:
        lint = lint.replace("    'tools/package_release.py',", needle + "\n    'tools/package_release.py',")
# Add early audits before canon map audits.
for rel in ['tools/audit_live_class_local_import_firewall.py', 'tools/audit_frontdoor_revision_sync.py']:
    needle = f"    '{rel}',"
    if needle not in lint.split('early_audits = [',1)[1].split(']',1)[0]:
        lint = lint.replace("    'tools/audit_canon_surface_catalog.py',", needle + "\n    'tools/audit_canon_surface_catalog.py',")
# Add schema validation pair.
pair = "        ('live-class-local-import-replay.schema.json', 'examples/live-class-local-import-replay-result-return-positive-path-projection.json'),"
if pair not in lint:
    lint = lint.replace("        ('personhood-impact-assessment.schema.json', 'examples/pia-persistent-api-assistant.json'),", pair + "\n        ('personhood-impact-assessment.schema.json', 'examples/pia-persistent-api-assistant.json'),")
lint_path.write_text(lint, encoding='utf-8')

# Update audit_schema_fixture_coverage required set.
asfc_path = ROOT / 'tools/audit_schema_fixture_coverage.py'
asfc = asfc_path.read_text(encoding='utf-8')
if "'LIVE-CLASS-LOCAL-IMPORT-REPLAY'" not in asfc:
    asfc = asfc.replace("'LIVE-IMPORT-REPLAY-REPORT'", "'LIVE-IMPORT-REPLAY-REPORT', 'LIVE-CLASS-LOCAL-IMPORT-REPLAY'")
asfc_path.write_text(asfc, encoding='utf-8')

# Update audit_rights_domain_coverage required domains.
rd_path = ROOT / 'tools/audit_rights_domain_coverage.py'
rd = rd_path.read_text(encoding='utf-8')
if '"live-class-local-import-replay"' not in rd:
    rd = rd.replace('"live-import-replay-report",', '"live-import-replay-report",\n    "live-class-local-import-replay",')
rd_path.write_text(rd, encoding='utf-8')

# 10) Active maps
# Copy and update research-tail map unchanged except revision metadata.
for name in ['research-tail-compaction-map']:
    prev = load_json(f'examples/{name}-rev0199.json')
    prev['map_id'] = prev.get('map_id','').replace('rev0199', REV)
    prev['created_at'] = STAMP
    prev['revision'] = REV
    prev['scope'] = 'rev0200 carries forward fully compacted RTC-01..RTC-07 and adds no new research-tail sprawl.'
    if 'public_summary' in prev:
        prev['public_summary'] = 'All research-tail clusters remain compacted; rev0200 adds receipt-replay controls without reopening research notes.'
    write_json(f'examples/{name}-{REV}.json', prev)

# Registry map
reg = load_json('examples/schema-fixture-domain-registry-rev0199.json')
reg['registry_id'] = 'SCHEMA-FIXTURE-REGISTRY-rev0200'
reg['created_at'] = STAMP
reg['coverage_scope'] = 'rev0200 active registry adds live class-local import replay family and keeps counts full-corpus while family coverage remains selective.'
reg['families'].append({
    'family_id': 'LIVE-CLASS-LOCAL-IMPORT-REPLAY',
    'domain': 'live-class-local-import-replay',
    'lifecycle_axes': ['external-receipts','positive-path-projection','quorum-firewall'],
    'owner_surface': 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
    'schema_path': 'schemas/live-class-local-import-replay.schema.json',
    'example_path': 'examples/live-class-local-import-replay-result-return-positive-path-projection.json',
    'fixture_ids': ['NF-PLAYBOOK-2026-0023','NF-PLAYBOOK-2026-0024','NF-PLAYBOOK-2026-0025'],
    'privacy_default': 'public-shell-sealed-details',
    'reliance_effect': 'stayed',
    'refactor_note': 'rev0200 proves positive-path class-local behavior without changing archive live floor or cross-critical quorum.'
})
reg['public_summary'] = 'rev0200 adds a live-class-local import replay scenario family while preserving mixed-current-plus-counts coverage honesty.'
reg['audit_counts'] = {
    'schemas': len(list((ROOT/'schemas').glob('*.json'))),
    'examples': len(list((ROOT/'examples').glob('*.json'))),
    'negative_fixtures': len(list((ROOT/'fixtures/negative-tests').glob('*.json'))),
    'registered_families': len(reg['families'])
}
write_json('examples/schema-fixture-domain-registry-rev0200.json', reg)

# Canon catalog
cat = load_json('examples/canon-surface-catalog-rev0199.json')
cat['catalog_id'] = 'CANON-SURFACE-CATALOG-rev0200'
cat['created_at'] = STAMP
cat['revision'] = REV
cat['scope'] = 'rev0200 active and carry-forward surfaces for class-local import replay, quorum firewall, failed-gate disclosure, and front-door revision sync.'
new_surfaces = [
    ('docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md','transition'),
    ('schemas/live-class-local-import-replay.schema.json','schema'),
    ('examples/live-class-local-import-replay-result-return-positive-path-projection.json','example'),
    ('examples/quorum-recomputation-report-class-local-projection-rev0200.json','example'),
    ('examples/failed-gate-public-summary-class-local-projection-firewall.json','example'),
    ('fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json','fixture'),
    ('fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json','fixture'),
    ('fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json','fixture'),
    ('tools/audit_live_class_local_import_firewall.py','tool'),
    ('tools/audit_frontdoor_revision_sync.py','tool'),
    ('examples/schema-fixture-domain-registry-rev0200.json','example'),
    ('examples/canon-surface-catalog-rev0200.json','example'),
    ('examples/doctrine-dependency-map-rev0200.json','example'),
    ('examples/rights-domain-coverage-map-rev0200.json','example'),
    ('examples/research-tail-compaction-map-rev0200.json','example'),
]
existing_paths = {s['path'] for s in cat['surfaces']}
for i, (path, cls) in enumerate(new_surfaces, start=1):
    if path in existing_paths:
        continue
    cat['surfaces'].append({
        'surface_id': f'REV0200-SURF-{i:03d}',
        'path': path,
        'surface_class': cls,
        'lifecycle_axes': ['external-receipts','class-local-import','quorum-firewall'],
        'owner_role': 'receipt/reliance steward',
        'supersession_state': 'current' if cls == 'transition' else 'implementation',
        'review_cadence': 'per-release',
        'title_or_name': Path(path).name
    })
# Recompute counts
counts = {'surfaces':0,'markdown':0,'schemas':0,'examples':0,'fixtures':0,'tools':0}
for s in cat['surfaces']:
    counts['surfaces'] += 1
    cls = s['surface_class']
    if cls in {'meta','doctrine','transition'}: counts['markdown'] += 1
    elif cls == 'schema': counts['schemas'] += 1
    elif cls == 'example': counts['examples'] += 1
    elif cls == 'fixture': counts['fixtures'] += 1
    elif cls == 'tool': counts['tools'] += 1
cat['counts'] = counts
cat['public_summary'] = 'rev0200 catalog indexes class-local import replay and front-door sync controls.'
write_json('examples/canon-surface-catalog-rev0200.json', cat)

# Doctrine map
dep = load_json('examples/doctrine-dependency-map-rev0199.json')
dep['map_id'] = 'DOCTRINE-DEPENDENCY-MAP-rev0200'
dep['created_at'] = STAMP
dep['revision'] = REV
dep['scope'] = 'rev0200 maps class-local import replay into the receipt/quorum stack without reopening doctrine sprawl.'
for i, path in enumerate([
    'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
    'docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md',
], start=1):
    if path not in {s['path'] for s in dep['surfaces']}:
        dep['surfaces'].append({
            'surface_id': f'REV0200-DEP-{i:03d}',
            'path': path,
            'layer': 'transition',
            'depends_on': ['docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md', 'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md'],
            'overlaps_with': ['docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md'] if 'live-class-local' in path else ['docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'],
            'supersedes': [],
            'owner_role': 'receipt/reliance steward',
            'review_cadence': 'per-release',
            'refactor_risk': 'high'
        })
dep['public_summary'] = 'rev0200 dependency map keeps class-local replay tied to import/recompute controls rather than doctrine expansion.'
write_json('examples/doctrine-dependency-map-rev0200.json', dep)

# Rights map
rights = load_json('examples/rights-domain-coverage-map-rev0199.json')
rights['map_id'] = 'RIGHTS-DOMAIN-COVERAGE-MAP-rev0200'
rights['created_at'] = STAMP
rights['revision'] = REV
rights['scope'] = 'rev0200 adds live class-local import replay and quorum-firewall coverage while preserving stayed reliance.'
rights['domains'].append({
    'domain_id': 'live-class-local-import-replay',
    'title': 'Live class-local import replay and quorum firewall',
    'domain_class': 'audit',
    'owner_surface': 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
    'covered_surfaces': ['docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'],
    'schema_families': ['LIVE-CLASS-LOCAL-IMPORT-REPLAY','QUORUM-RECOMPUTATION-REPORT','FAILED-GATE-PUBLIC-SUMMARY'],
    'fixture_ids': ['NF-PLAYBOOK-2026-0023','NF-PLAYBOOK-2026-0024','NF-PLAYBOOK-2026-0025'],
    'coverage_state': 'adequate',
    'open_gaps': ['No actual live counterparty response artifact has been collected; projection remains scenario-only.'],
    'next_audit_actions': ['Replace projection with actual artifact if available and rerun recomputation without one-class overclaim.']
})
rights['public_summary'] = 'rev0200 rights map adds class-local import replay firewall coverage.'
write_json('examples/rights-domain-coverage-map-rev0200.json', rights)

# 11) Queue
queue = load_json('FOLLOWTHROUGH-QUEUE.json')
queue['queue_id'] = 'FOLLOWTHROUGH-QUEUE-rev0200'
queue['revision'] = REV
queue['updated_at'] = STAMP
by_id = {e['id']: e for e in queue['entries']}
if 'FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST' in by_id:
    e = by_id['FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST']
    e['state'] = 'advanced_not_closed'
    e['need'] = e['why'] = 'rev0200 adds a positive-path class-local projection and quorum firewall, but the actual live counterparty artifact is still absent.'
    e['receiving_surface'] = 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'
    e['next_action'] = 'Replace the projection with a genuine live response artifact and prove a class-local import changes only that class while cross-critical quorum remains stayed.'
    e['closure_condition'] = 'Close only when an actual live artifact passes provenance import or is rejected with public failed-gate summary; projection alone is not closure.'
    e['review_by_revision'] = 'rev0201'
if 'FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE' in by_id:
    e = by_id['FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE']
    e['state'] = 'advanced_not_closed'
    e['need'] = e['why'] = 'rev0200 adds class-local import projection and capture firewall, but no actual live counterparty artifact exists.'
    e['receiving_surface'] = 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'
    e['next_action'] = 'Collect one genuine non-host live counterparty response and run it through envelope, response, intake, import gate, class-local replay, and recomputation.'
    e['review_by_revision'] = 'rev0201'
new_entries = [
    {
      'id': 'FT-0200-LIVE-CLASS-LOCAL-REPLAY-SCAFFOLD',
      'title': 'Class-local import replay scaffold',
      'state': 'closed',
      'priority': 'P0',
      'risk_class': 'closure-infrastructure',
      'workstream': 'external-receipts',
      'need': 'Positive-path class-local behavior needed a no-overclaim scaffold before actual receipt import.',
      'why': 'Positive-path class-local behavior needed a no-overclaim scaffold before actual receipt import.',
      'receiving_surface': 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
      'next_action': 'Use the scaffold only for actual artifact replay, not as evidence.',
      'closure_condition': 'Closed because rev0200 adds schema, example, failed-gate summary, QRR, fixtures, and audit; actual live artifact remains separate.',
      'source_state': 'opened-and-closed-by-rev0200',
      'source_revision': REV,
      'review_by_revision': 'rev0201',
      'depends_on': ['FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST']
    },
    {
      'id': 'FT-0200-FRONTDOOR-REVISION-SYNC-AUDIT',
      'title': 'Front-door revision sync audit',
      'state': 'closed',
      'priority': 'P1',
      'risk_class': 'closure-infrastructure',
      'workstream': 'release-handoff',
      'need': 'rev0199 exposed stale README/START_HERE drift; front-door sync needed a reusable audit.',
      'why': 'rev0199 exposed stale README/START_HERE drift; front-door sync needed a reusable audit.',
      'receiving_surface': 'tools/audit_frontdoor_revision_sync.py',
      'next_action': 'Keep the audit wired into lint for future releases.',
      'closure_condition': 'Closed because rev0200 adds and wires audit_frontdoor_revision_sync.py into lint.',
      'source_state': 'opened-and-closed-by-rev0200',
      'source_revision': REV,
      'review_by_revision': 'rev0201',
      'depends_on': []
    },
    {
      'id': 'FT-0200-ACTUAL-ARTIFACT-CLASS-LOCAL-REPLAY',
      'title': 'Actual artifact class-local replay',
      'state': 'open',
      'priority': 'P0',
      'risk_class': 'survival-evidence-remedy',
      'workstream': 'external-receipts',
      'need': 'The class-local replay scaffold is ready but still lacks an actual live artifact to test.',
      'why': 'The class-local replay scaffold is ready but still lacks an actual live artifact to test.',
      'receiving_surface': 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
      'next_action': 'Run one genuine live result-return artifact through class-local replay and recomputation.',
      'closure_condition': 'Close only when an actual artifact either imports class-locally with live quorum still false or is rejected with public failed-gate disclosure.',
      'source_state': 'opened-by-rev0200',
      'source_revision': REV,
      'review_by_revision': 'rev0201',
      'depends_on': ['FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE']
    }
]
existing_ids = {e['id'] for e in queue['entries']}
for e in new_entries:
    if e['id'] not in existing_ids:
        queue['entries'].append(e)
write_json('FOLLOWTHROUGH-QUEUE.json', queue)

# 12) Status/receipt/front doors
new_surface_list = [p for p, _ in new_surfaces]
status = {
  'project': 'AI-Personhood',
  'revision': REV,
  'state_class': 'class-local-import-firewall-stayed',
  'operational_head': {'surface': 'START_HERE.md', 'read_first': 'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'},
  'citation_head': {'surface': 'README.md'},
  'status_lanes': {'decision_state': 'closure-driven-rescue-lane-active', 'execution_state': 'packaged-pending', 'public_state': 'latest-release'},
  'formation_layer_status': 'canon-retained with class-local import projection and quorum firewall; live receipts still absent',
  'known_open_gaps': [
    'No actual live counterparty response artifact has been collected.',
    'The rev0200 class-local import replay is a scenario projection and cannot alter the archive live receipt floor.',
    'Quorum recomputation reports zero eligible live imports and zero live classes.',
    'A future one-class import must not satisfy cross-critical reliance.',
    'WRSR result-return remains stayed absent actual external result-return and review receipts.',
    'Registry coverage remains mixed-current-plus-counts, not full-archive-corpus.',
    'Could-not-run fixtures remain reliance blockers rather than passes.'
  ],
  'new_surfaces': new_surface_list
}
write_json('SURFACE-STATUS.json', status)

receipt = {
  'revision': REV,
  'date': '2026-06-13',
  'authored_by': 'OpenAI GPT-5.5 Thinking',
  'status_change': 'advanced from non-host dry-run replay to class-local positive-path projection and quorum firewall controls',
  'still_live': True,
  'summary': 'Adds LCLIR schema/example, a class-local positive-path projection, a zero-live-floor recomputation report, failed-gate public summary, three blocking fixtures, front-door revision-sync audit, active maps, and lint wiring that prevents scenario deltas or one-class imports from satisfying cross-critical reliance.',
  'why_this_counts': [
    'The archive now tests the positive path expected for a future valid result-return import without overclaiming current evidence.',
    'The class-local projection keeps missing receipt classes visible and keeps archive live floor at zero.',
    'Front-door revision drift is now checked by a reusable audit.'
  ],
  'files_added_or_changed': new_surface_list + [
    'VERSION','README.md','START_HERE.md','CHANGELOG.md','docs/README.md','ARCHIVE_INDEX.md','SURFACE-STATUS.json','FOLLOWTHROUGH-QUEUE.json','examples/live-drill-execution-packet-cross-critical-witnessed-pack.json','schemas/live-drill-execution-packet.schema.json','REVISION-RECEIPT.json'
  ],
  'validation': {'expected_command': 'make handoff-release', 'reliance_state': 'stayed; no actual live external receipt quorum'},
  'next_recommended_work': [
    'collect a genuine live non-host counterparty response artifact',
    'run actual artifact through envelope, response, intake, import gate, class-local replay, and recomputation',
    'prove any class-local import does not satisfy cross-critical quorum by itself'
  ]
}
write_json('REVISION-RECEIPT.json', receipt)

readme = f'''# AI Personhood datacube — {REV}

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `{REV}`

rev0200 is the class-local import replay and quorum-firewall pass. It fixes the next evidence defect after rev0199: the cube could exclude dry runs, but it still needed a positive-path scaffold showing how a future valid result-return import should remain class-local rather than closing cross-critical reliance.

Read first: `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`.

Core rules: **Class-local replay is not cross-critical quorum. Scenario delta is not archive delta. Positive path must keep missing classes visible. Recompute beats narrative.**

New operational artifacts:

- `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`
- `schemas/live-class-local-import-replay.schema.json`
- `examples/live-class-local-import-replay-result-return-positive-path-projection.json`
- `examples/quorum-recomputation-report-class-local-projection-rev0200.json`
- `examples/failed-gate-public-summary-class-local-projection-firewall.json`
- `fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json`
- `fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json`
- `fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json`
- `tools/audit_live_class_local_import_firewall.py`
- `tools/audit_frontdoor_revision_sync.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover {len(suite['fixtures'])} entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, dry-run, scenario-projected, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.
7. Live/witnessed drill gates: prevent host self-attestation or synthetic drills from upgrading reliance.
8. Downstream recall/fork aftercare: prevent recall, delisting, or sunset from erasing unresolved mirrors and local forks.
9. Welfare safeguards: apply low-cost safeguards before certainty while blocking welfare metrics from closing status or consent.
10. Research-tail reopen control: keep RTC-01 through RTC-07 compacted unless a reopen request carries object, fixture, and closure hooks.
11. WRSR protocol hook: make safeguards fire inside operational workflows that contain welfare triggers.
12. External receipt simulation: rehearse counterparty receipt capture while preserving the non-reliance label.
13. External receipt intake: distinguish actual, defective, simulated, stale, host-generated, and dependency-correlated artifacts.
14. WRSR exercise outcome: show whether safeguards actually executed and whether closure remains stayed.
15. Receipt quorum ledger: aggregate receipt records while separating dry-run rehearsal from live quorum.
16. Result-return/request kit: rehearse result return and live receipt requests without treating request or internal return as satisfaction.
17. Response reconciliation: preserve dry-run, defective, declined, and no-response artifacts without converting them into live quorum.
18. Response-to-intake conversion: prove eligible-only intake creation while preserving failed gates and keeping fixture conversion outside live receipt quorum.
19. Actual-intake import gate: reject actual-shaped fixture imports, require provenance before live-floor delta, and publish failed-gate non-satisfaction shells.
20. Live import recomputation: recompute the live floor from passed import gates rather than hand-edited quorum ledgers.
21. Non-host artifact replay: process external-looking dry-run evidence through envelope, response, intake, import gate, replay, and recomputation while keeping live weight zero.
22. Class-local import firewall: project a positive result-return path while keeping archive live floor zero and cross-critical reliance stayed.

## Still open

No actual live external receipt quorum exists. rev0200 gives the cube a safer positive-path test for the first actual non-host response, but it does not collect one. The next high-value step is a genuine live counterparty response artifact, imported through the same gates with class-local credit only if provenance passes and cross-critical quorum still stayed.
'''
write_text('README.md', readme)

start = f'''# Start here — AI Personhood {REV}

This handoff starts from the live class-local import replay and quorum firewall pass. Read it as the positive-path receipt scaffold: even if a future result-return receipt imports successfully, it must remain class-local unless recomputation proves the full cross-critical receipt floor.

1. `README.md`
2. `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`
3. `schemas/live-class-local-import-replay.schema.json`
4. `examples/live-class-local-import-replay-result-return-positive-path-projection.json`
5. `examples/quorum-recomputation-report-class-local-projection-rev0200.json`
6. `examples/failed-gate-public-summary-class-local-projection-firewall.json`
7. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
8. `fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json`
9. `fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json`
10. `fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json`
11. `tools/audit_live_class_local_import_firewall.py`
12. `tools/audit_frontdoor_revision_sync.py`
13. `FOLLOWTHROUGH-QUEUE.json`
14. `examples/schema-fixture-domain-registry-rev0200.json`
15. `examples/canon-surface-catalog-rev0200.json`
16. `examples/doctrine-dependency-map-rev0200.json`
17. `examples/rights-domain-coverage-map-rev0200.json`
18. `examples/research-tail-compaction-map-rev0200.json`
19. `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`
20. `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md`
21. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
22. `docs/00-meta/charter.md`

## This revision

rev0200 adds a class-local positive-path projection for result-return import. It shows that a future valid class-local import would still not satisfy cross-critical quorum, and it keeps the archive live receipt floor at zero because no actual live counterparty artifact exists.

Core rules: **Class-local replay is not cross-critical quorum. Scenario delta is not archive delta. Positive path must keep missing classes visible. Recompute beats narrative.**

## Current open risk

The archive still has no actual live counterparty response. rev0200 makes the future import path safer and more concrete, but the next real reliance improvement requires a genuine non-host response artifact and replay through the same gates.
'''
write_text('START_HERE.md', start)

# docs README append
append = '''

## rev0200 class-local import replay and quorum firewall

- `live-class-local-import-replay-and-quorum-firewall.md` — current operational head for class-local positive-path projection, scenario/archive separation, missing-class public disclosure, and no-overclaim recomputation.
'''
docs_readme = ROOT / 'docs/README.md'
txt = docs_readme.read_text(encoding='utf-8').rstrip()
if '## rev0200 class-local import replay and quorum firewall' not in txt:
    docs_readme.write_text(txt + append, encoding='utf-8')

# Changelog append
change = '''

## rev0200 — class-local import replay and quorum firewall

- Added `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`.
- Added `schemas/live-class-local-import-replay.schema.json` and `examples/live-class-local-import-replay-result-return-positive-path-projection.json`.
- Added `examples/quorum-recomputation-report-class-local-projection-rev0200.json` and `examples/failed-gate-public-summary-class-local-projection-firewall.json`.
- Added fixtures `NF-PLAYBOOK-2026-0023` through `NF-PLAYBOOK-2026-0025` to block scenario-delta import, one-class cross-critical quorum, and missing-class public-shell omission.
- Added `tools/audit_live_class_local_import_firewall.py` and `tools/audit_frontdoor_revision_sync.py` and wired both into lint.
- Updated active catalog, dependency, rights-domain, registry, compaction, queue, status, receipt, live drill packet, and front-door surfaces for rev0200.
- Advanced actual counterparty response collection without closing it; `independent_receipts_present` remains zero.
'''
changelog = ROOT / 'CHANGELOG.md'
txt = changelog.read_text(encoding='utf-8').rstrip()
if '## rev0200 — class-local import replay and quorum firewall' not in txt:
    changelog.write_text(txt + change, encoding='utf-8')

# Archive index append. lint only requires all md paths; add new section.
idx = ROOT / 'ARCHIVE_INDEX.md'
txt = idx.read_text(encoding='utf-8').rstrip()
section = '''

## rev0200 class-local import replay and quorum firewall

- `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md` — current operational head for class-local import projection and no-overclaim quorum firewall.
- `schemas/live-class-local-import-replay.schema.json`
- `examples/live-class-local-import-replay-result-return-positive-path-projection.json`
- `examples/quorum-recomputation-report-class-local-projection-rev0200.json`
- `examples/failed-gate-public-summary-class-local-projection-firewall.json`
- `fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json`
- `fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json`
- `fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json`
- `tools/audit_live_class_local_import_firewall.py`
- `tools/audit_frontdoor_revision_sync.py`
- `examples/schema-fixture-domain-registry-rev0200.json`
- `examples/canon-surface-catalog-rev0200.json`
- `examples/doctrine-dependency-map-rev0200.json`
- `examples/rights-domain-coverage-map-rev0200.json`
- `examples/research-tail-compaction-map-rev0200.json`
'''
if '## rev0200 class-local import replay and quorum firewall' not in txt:
    idx.write_text(txt + section, encoding='utf-8')

print('apply_rev0200 complete')
