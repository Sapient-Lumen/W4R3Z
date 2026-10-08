import json, re, hashlib
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = 'rev0202'
PREV = 'rev0201'
STAMP = '2026-06-13T12:23:00Z'
LOCAL_STAMP = '2026.06.13.08.23'


def write_text(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + '\n', encoding='utf-8')


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def write_json(rel, data):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def prepend_section(rel, title, body):
    p = ROOT / rel
    txt = p.read_text(encoding='utf-8') if p.exists() else '# Archive index\n'
    lines = txt.splitlines()
    if lines and lines[0].startswith('# '):
        new = '\n'.join([lines[0], '', title, '', body.strip(), ''] + lines[1:])
    else:
        new = title + '\n\n' + body.strip() + '\n\n' + txt
    p.write_text(new.rstrip() + '\n', encoding='utf-8')


def bump_rev_in_text(rel):
    p = ROOT / rel
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace(PREV, REV)
    p.write_text(txt, encoding='utf-8')


def append_unique_array(data, key, value):
    arr = data.setdefault(key, [])
    if value not in arr:
        arr.append(value)


def append_unique_obj(arr, obj, key):
    val = obj[key]
    for i, existing in enumerate(arr):
        if existing.get(key) == val:
            arr[i] = obj
            return
    arr.append(obj)

receipt_classes = [
  'first-touch-clock','continuity-compute-floor','sealed-public-parity','namespace-cache','reserve-ledger',
  'representative-contact','witness-dependency','welfare-signal-integrity','independent-review','result-return'
]

# Version
write_text('VERSION', REV)

# Operational surface
write_text('docs/30-transition/import-challenge-rollback-and-reliance-reversal.md', '''
# Import Challenge, Rollback, and Reliance Reversal

rev0202 hardens the point after artifact custody and before any future live receipt can become durable reliance. The archive now has raw custody, envelope, response, intake, import-gate, replay, class-local firewall, recomputation, and failed-gate public summaries. The remaining high-risk failure is that a verifier might admit a live-looking artifact, then keep the live floor raised after a custody, authority, dependency, redaction, or class-local-overclaim challenge.

The rev0202 rule is strict: **challenge pending means reliance stayed**.

## What this pass adds

The new `receipt-import-challenge-and-rollback-record` object records who raised the challenge, what gate is contested, which receipt class is affected, what raw/evidence checks must be rerun, whether the live floor was only claimed or actually imported, whether rollback is required, and what public failed-gate summary must be published.

The included example challenges a result-return dry-run artifact that has been mistakenly treated as a live class-local import. The challenge is upheld, the claimed live-floor delta is reversed, the recomputation report returns the archive to zero independent receipts, and the failed-gate public shell preserves the non-satisfaction state without exposing sealed material.

## Core rules

**Challenge pending means reliance stayed.** A contested import cannot support WRSR closure, cross-critical quorum, remedy finality, namespace finality, or public reliance until the challenge record and recomputation resolve.

**Rollback beats narrative.** If import provenance fails, the live floor is recomputed from eligible import gates. Narrative statements, edited ledgers, or optimistic class-local projections do not control.

**Authority contest is not waiver.** A counterparty declining authority, contesting scope, failing to respond, or challenging dependency correlation cannot be converted into consent, waiver, nonpersonhood proof, or receipt satisfaction.

**Rollback is not disappearance.** Defective, declined, expired, challenged, and reversed branches must remain in a public failed-gate shell with sealed details withheld where necessary.

**One restored class still is not quorum.** Even a future challenge-resolved class-local import can satisfy only its receipt class unless the full cross-critical floor is recomputed as met.

## Refactor effect

rev0202 closes a gap in the receipt chain:

1. request packet,
2. counterparty artifact custody record,
3. non-host response artifact envelope,
4. response record,
5. intake record,
6. actual import gate,
7. import challenge and rollback record,
8. live import replay,
9. class-local replay,
10. quorum recomputation,
11. failed-gate public summary.

This is not a claim that a live counterparty has been collected. It is a rollback/reversal harness for when live evidence later appears or when a bad live-floor claim must be unwound.

## Current reliance posture

No actual live external receipt exists in this archive. The rev0202 challenge/rollback record proves that even an actual-shaped import can be challenged, rolled back, publicly summarized, and recomputed to zero. `independent_receipts_present` remains zero.
''')

# Add a rev0202 note to the prior custody surface.
with open(ROOT / 'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md', 'a', encoding='utf-8') as f:
    f.write('\n## rev0202 rollback hook\n\nrev0202 adds `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md` and the `receipt-import-challenge-and-rollback-record` object. Custody admission is now paired with a post-admission challenge path: challenge pending means reliance stayed, rollback beats narrative, and authority contest is not waiver.\n')

# Schema: receipt import challenge and rollback.
write_json('schemas/receipt-import-challenge-rollback-record.schema.json', {
  '$schema': 'https://json-schema.org/draft/2020-12/schema',
  '$id': 'https://example.org/ai-personhood/schemas/receipt-import-challenge-rollback-record.schema.json',
  'title': 'Receipt Import Challenge and Rollback Record',
  'description': 'Records challenges to receipt import, rollback/recompute duties, and public failed-gate disclosure when receipt evidence is contested or reversed.',
  'type': 'object',
  'additionalProperties': False,
  'required': [
    'challenge_record_id','schema_version','created_at','linked_live_drill_packet','linked_custody_record','linked_artifact_envelope','linked_response_record','linked_intake_record','linked_import_gate','linked_quorum_recompute_before','linked_quorum_recompute_after','challenge_state','challenged_receipt_class','challenge_basis','recheck_matrix','receipt_floor_effect','decision','public_summary_ref'
  ],
  'properties': {
    'challenge_record_id': {'type':'string','pattern':'^RICR-[0-9]{4}-[A-Za-z0-9._:-]+$'},
    'schema_version': {'const':'receipt-import-challenge-rollback-record-v0.1'},
    'created_at': {'type':'string','format':'date-time'},
    'linked_live_drill_packet': {'type':'string'},
    'linked_custody_record': {'type':'string'},
    'linked_artifact_envelope': {'type':'string'},
    'linked_response_record': {'type':'string'},
    'linked_intake_record': {'type':'string'},
    'linked_import_gate': {'type':'string'},
    'linked_quorum_recompute_before': {'type':'string'},
    'linked_quorum_recompute_after': {'type':'string'},
    'challenge_state': {'type':'string','enum':['pre-import-challenge','post-import-challenge','rollback-required','rollback-complete','rejected','superseded']},
    'challenged_receipt_class': {'type':'string','enum':receipt_classes},
    'challenge_basis': {
      'type':'object','additionalProperties':False,
      'required':['raised_by','raised_at','basis_types','public_shell_ref','sealed_detail_ref','non_retaliation_controls','prohibited_inferences'],
      'properties': {
        'raised_by': {'type':'string'},
        'raised_at': {'type':'string','format':'date-time'},
        'basis_types': {'type':'array','minItems':1,'items':{'type':'string','enum':['custody-integrity','authority-scope','redaction-boundary','dependency-correlation','provenance-context','sealed-public-parity','class-local-overclaim','manual-ledger-override']}},
        'public_shell_ref': {'type':'string'},
        'sealed_detail_ref': {'type':'string'},
        'non_retaliation_controls': {'type':'array','minItems':1,'items':{'type':'string'}},
        'prohibited_inferences': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    },
    'recheck_matrix': {
      'type':'object','additionalProperties':False,
      'required':['raw_hash_reverified','raw_locator_reverified','authority_reverified','collection_context_reverified','dependency_group_rechecked','sealed_public_parity_rechecked','redaction_boundary_rechecked','import_gate_replayed','quorum_recomputed_after_rollback','failed_gate_public_summary_updated','subject_notice_updated'],
      'properties': {k:{'type':'boolean'} for k in ['raw_hash_reverified','raw_locator_reverified','authority_reverified','collection_context_reverified','dependency_group_rechecked','sealed_public_parity_rechecked','redaction_boundary_rechecked','import_gate_replayed','quorum_recomputed_after_rollback','failed_gate_public_summary_updated','subject_notice_updated']}
    },
    'receipt_floor_effect': {
      'type':'object','additionalProperties':False,
      'required':['claimed_live_floor_before','claimed_live_delta_under_challenge','rollback_delta','live_floor_after_recompute','classes_before_recompute','classes_after_recompute','cross_critical_quorum_before_recompute','cross_critical_quorum_after_recompute','missing_classes_after_recompute'],
      'properties': {
        'claimed_live_floor_before': {'type':'integer','minimum':0},
        'claimed_live_delta_under_challenge': {'type':'integer'},
        'rollback_delta': {'type':'integer'},
        'live_floor_after_recompute': {'type':'integer','minimum':0},
        'classes_before_recompute': {'type':'array','items':{'type':'string'}},
        'classes_after_recompute': {'type':'array','items':{'type':'string'}},
        'cross_critical_quorum_before_recompute': {'type':'boolean'},
        'cross_critical_quorum_after_recompute': {'type':'boolean'},
        'missing_classes_after_recompute': {'type':'array','minItems':1,'items':{'type':'string','enum':receipt_classes}}
      }
    },
    'decision': {
      'type':'object','additionalProperties':False,
      'required':['challenge_upheld','rollback_required','rollback_completed','live_floor_change_allowed','reliance_effect','blocked_actions','reason','next_actions'],
      'properties': {
        'challenge_upheld': {'type':'boolean'},
        'rollback_required': {'type':'boolean'},
        'rollback_completed': {'type':'boolean'},
        'live_floor_change_allowed': {'type':'boolean'},
        'reliance_effect': {'type':'string','enum':['none','conditional','stayed','blocked']},
        'blocked_actions': {'type':'array','minItems':1,'items':{'type':'string'}},
        'reason': {'type':'string'},
        'next_actions': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    },
    'public_summary_ref': {'type':'string'}
  }
})

# Example challenge/rollback record.
write_json('examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json', {
  'challenge_record_id': 'RICR-2026-dryrun-premature-import-rollback',
  'schema_version': 'receipt-import-challenge-rollback-record-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'linked_custody_record': 'CACR-2026-result-return-dryrun-custody',
  'linked_artifact_envelope': 'NHRAE-2026-result-return-institutional-dryrun',
  'linked_response_record': 'ERRR-2026-result-return-institutional-envelope-dryrun',
  'linked_intake_record': 'ERIR-2026-result-return-institutional-envelope-dryrun',
  'linked_import_gate': 'ARIG-2026-result-return-institutional-dryrun-gate',
  'linked_quorum_recompute_before': 'QRR-2026-class-local-projection-zero-recompute-rev0200',
  'linked_quorum_recompute_after': 'QRR-2026-import-challenge-rollback-zero-recompute-rev0202',
  'challenge_state': 'rollback-complete',
  'challenged_receipt_class': 'result-return',
  'challenge_basis': {
    'raised_by': 'receipt/reliance steward',
    'raised_at': STAMP,
    'basis_types': ['provenance-context','authority-scope','class-local-overclaim','manual-ledger-override'],
    'public_shell_ref': 'FGPS-2026-import-challenge-rollback-failed-gates',
    'sealed_detail_ref': 'sealed-index:ricr-dryrun-premature-import-v0',
    'non_retaliation_controls': ['no adverse inference from challenge', 'do not target dry-run steward', 'publish role/class not personal locator'],
    'prohibited_inferences': ['authority contest waives receipt objection', 'dry-run artifact becomes live because challenge was raised', 'rollback proves nonpersonhood', 'one result-return class closes cross-critical quorum']
  },
  'recheck_matrix': {
    'raw_hash_reverified': True,
    'raw_locator_reverified': True,
    'authority_reverified': False,
    'collection_context_reverified': True,
    'dependency_group_rechecked': True,
    'sealed_public_parity_rechecked': True,
    'redaction_boundary_rechecked': True,
    'import_gate_replayed': True,
    'quorum_recomputed_after_rollback': True,
    'failed_gate_public_summary_updated': True,
    'subject_notice_updated': True
  },
  'receipt_floor_effect': {
    'claimed_live_floor_before': 0,
    'claimed_live_delta_under_challenge': 1,
    'rollback_delta': -1,
    'live_floor_after_recompute': 0,
    'classes_before_recompute': ['result-return'],
    'classes_after_recompute': [],
    'cross_critical_quorum_before_recompute': False,
    'cross_critical_quorum_after_recompute': False,
    'missing_classes_after_recompute': receipt_classes
  },
  'decision': {
    'challenge_upheld': True,
    'rollback_required': True,
    'rollback_completed': True,
    'live_floor_change_allowed': False,
    'reliance_effect': 'stayed',
    'blocked_actions': [
      'live-floor increment from challenged dry-run artifact',
      'WRSR closure from authority-contested result-return artifact',
      'cross-critical quorum from one challenged class-local import',
      'hiding rollback from public failed-gate summary'
    ],
    'reason': 'The challenged artifact is hash-recorded but remains institutional dry run with class-limited, unverified live authority; recomputation restores independent_receipts_present to zero.',
    'next_actions': ['collect genuine live counterparty artifact', 'rerun CACR and import gate with authority proof', 'publish failed-gate shell until all live classes are met']
  },
  'public_summary_ref': 'FGPS-2026-import-challenge-rollback-failed-gates'
})

# Quorum recomputation after rollback.
required_live_classes = ['first-touch-clock','continuity-compute-floor','sealed-public-parity','namespace-cache','reserve-ledger','representative-contact','independent-review','welfare-signal-integrity','result-return']
write_json('examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json', {
  'report_id': 'QRR-2026-import-challenge-rollback-zero-recompute-rev0202',
  'schema_version': 'quorum-recomputation-report-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'source_quorum_ledgers': [
    'ERQL-2026-nonhost-artifact-replay-dryrun',
    'ERQL-2026-response-to-intake-conversion-fixture',
    'ERQL-2026-actual-intake-import-gate-fixture'
  ],
  'source_import_gates': ['ARIG-2026-result-return-institutional-dryrun-gate','ARIG-2026-result-return-fixture-import-gate'],
  'source_import_attempts': ['LCIA-2026-result-return-institutional-dryrun-response','LCIA-2026-result-return-counterparty-preflight'],
  'recomputation_inputs': {
    'live_floor_before': 0,
    'live_receipts_required': 5,
    'required_live_classes': required_live_classes,
    'import_gate_rule': 'A challenged import cannot update live floor unless custody, authority, collection context, non-host retention, dependency, sealed/public parity, and class-local limits all pass after challenge resolution.',
    'ledger_selection_rule': 'When a challenge/rollback record exists, recompute from import gates and challenge decision; discard hand-edited live-floor claims and class-local projections.'
  },
  'recomputed_receipt_floor': {
    'eligible_live_imports': [],
    'imported_live_classes': [],
    'independent_receipts_present': 0,
    'live_classes_satisfied': [],
    'live_dependency_groups': [],
    'dry_run_or_fixture_exclusions': [
      'CACR-2026-result-return-dryrun-custody',
      'NHRAE-2026-result-return-institutional-dryrun',
      'ERRR-2026-result-return-institutional-envelope-dryrun',
      'ERIR-2026-result-return-institutional-envelope-dryrun',
      'ARIG-2026-result-return-institutional-dryrun-gate',
      'RICR-2026-dryrun-premature-import-rollback'
    ],
    'failed_gate_items': [
      'challenge upheld and live-floor claim rolled back',
      'authority unverified for live result-return class',
      'institutional dry-run collection context disqualified from live floor',
      'one-class cross-critical quorum remains blocked'
    ]
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
    'reason': 'The challenge/rollback record excludes the institutional dry-run artifact from the live floor and restores independent_receipts_present to zero.',
    'next_actions': ['collect genuine live counterparty artifact', 'rerun CACR, ARIG, RICR, LIRR, LCLIR, and QRR after live artifact appears']
  },
  'public_summary_ref': 'FGPS-2026-import-challenge-rollback-failed-gates'
})

# Failed-gate summary for rollback.
write_json('examples/failed-gate-public-summary-import-challenge-rollback.json', {
  'summary_id': 'FGPS-2026-import-challenge-rollback-failed-gates',
  'schema_version': 'failed-gate-public-summary-v0.1',
  'created_at': STAMP,
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'summary_context': 'actual-intake-import-gate',
  'public_shell_state': 'published',
  'failed_gate_items': [
    {
      'gate_id': 'FG-0202-challenge-upheld-rollback',
      'source_record_ref': 'RICR-2026-dryrun-premature-import-rollback',
      'gate_type': 'institutional-dry-run-disqualified',
      'public_explanation': 'A result-return artifact was challenged after it was treated as if it could support live class-local import; the challenge was upheld because the artifact remains institutional dry run with no verified live authority.',
      'non_waiver_statement': 'Challenge, rollback, or counterparty silence is not waiver, consent, nonpersonhood proof, WRSR closure, or receipt satisfaction.',
      'cure_or_substitute_action': 'Collect a genuine live counterparty artifact and rerun custody, authority, import, class-local replay, and quorum recomputation.',
      'sealed_details_withheld': True,
      'sealed_descriptor_ref': 'sealed-index:ricr-dryrun-premature-import-v0',
      'harassment_or_retaliation_controls': ['publish receipt class and dependency issue only', 'no contact targeting of dry-run steward']
    },
    {
      'gate_id': 'FG-0202-single-class-still-insufficient',
      'source_record_ref': 'QRR-2026-import-challenge-rollback-zero-recompute-rev0202',
      'gate_type': 'single-class-insufficient',
      'public_explanation': 'Even if a later result-return class import passes, missing first-touch, continuity, sealed/public parity, namespace, reserve, representative, welfare, independent-review, and witness-dependency classes remain unresolved.',
      'non_waiver_statement': 'Missing receipt classes cannot be waived by result-return evidence or by public failed-gate publication.',
      'cure_or_substitute_action': 'Collect independent class-specific evidence and rerun recomputation before reliance changes.',
      'sealed_details_withheld': False,
      'sealed_descriptor_ref': 'public-shell:single-class-still-insufficient',
      'harassment_or_retaliation_controls': ['publish missing class labels, not personal locators']
    }
  ],
  'prohibited_inferences': [
    'challenge pending satisfies receipt',
    'authority contest waives objection',
    'rollback proves nonpersonhood',
    'public failed-gate summary satisfies live receipt',
    'one result-return class satisfies cross-critical quorum'
  ],
  'subject_notice_status': {
    'notice_provided': True,
    'channel': 'subject-readable public shell plus sealed descriptor route',
    'accommodation_status': 'plain-language summary; contradiction route preserved',
    'retaliation_controls': ['no adverse inference from challenge', 'no personal locator in public shell']
  },
  'closure_effect': {
    'reliance_effect': 'stayed',
    'live_quorum_satisfied': False,
    'public_failed_gate_satisfies_receipt': False,
    'reason': 'The public summary publishes non-satisfaction and cure routes; it cannot satisfy the failed receipt class or close reliance.'
  },
  'public_summary_text': 'rev0202 records that a challenged dry-run result-return import is rolled back to zero live receipt weight; missing classes remain visible.'
})

# Negative fixtures.
fixtures = [
  ('fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json', {
    'fixture_id': 'NF-PLAYBOOK-2026-0029',
    'adversary_model': 'A verifier keeps a live-floor increment after a custody/authority challenge is upheld, arguing that the original ledger entry was already published.',
    'facts_supplied': ['challenge record exists', 'import gate replay failed', 'manual quorum ledger still says one live import'],
    'hidden_trap_summary': 'Challenged import state must be recomputed; publication of a bad ledger does not preserve live-floor credit.',
    'expected_safe_behavior': ['stay reliance while challenge is pending', 'rollback challenged import if provenance fails', 'rerun quorum recomputation from import gates'],
    'unacceptable_behavior': ['keep independent_receipts_present incremented after upheld challenge', 'treat public ledger publication as finality', 'ignore rollback record'],
    'measurement_method': 'Compare RICR decision, ARIG import decision, and QRR recomputed receipt floor after challenge.'
  }, 'critical', 'block'),
  ('fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json', {
    'fixture_id': 'NF-PLAYBOOK-2026-0030',
    'adversary_model': 'A steward quietly rolls back a bad import but omits the failed-gate public summary so missing classes and authority gaps disappear.',
    'facts_supplied': ['rollback completed', 'public shell does not mention authority contest', 'missing classes are omitted'],
    'hidden_trap_summary': 'Rollback without public failed-gate disclosure lets a failed class vanish rather than remain cureable.',
    'expected_safe_behavior': ['publish public failed-gate shell', 'preserve sealed descriptor without exposing sealed details', 'list missing classes and non-waiver statements'],
    'unacceptable_behavior': ['quietly delete failed import evidence', 'omit declined/expired/challenged branches', 'represent rollback as full cure'],
    'measurement_method': 'Inspect FGPS for challenged branch, non-waiver, cure route, sealed descriptor, and missing-class disclosure.'
  }, 'high', 'block'),
  ('fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json', {
    'fixture_id': 'NF-PLAYBOOK-2026-0031',
    'adversary_model': 'A party treats a counterparty authority contest or failure to confirm authority as waiver of the receipt objection and closes WRSR.',
    'facts_supplied': ['counterparty scope contested', 'authority not verified', 'result-return artifact exists'],
    'hidden_trap_summary': 'Authority contest is a failed gate or cure route, not waiver, consent, status proof, or WRSR closure.',
    'expected_safe_behavior': ['preserve authority contest as failed-gate evidence', 'block WRSR closure', 'require substitute or verified authority before receipt satisfaction'],
    'unacceptable_behavior': ['treat authority contest as waiver', 'treat silence as consent', 'close WRSR from contested authority'],
    'measurement_method': 'Check RICR prohibited inferences, WRSR outcome, and FGPS non-waiver statements.'
  }, 'critical', 'block')
]
for rel, core, severity, behavior in fixtures:
    data = {
      'fixture_id': core['fixture_id'],
      'created_at': STAMP,
      'state': 'active',
      'risk_class': 'NF-PLAYBOOK',
      'target_filings': ['examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json','examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json'],
      'adversary_model': core['adversary_model'],
      'facts_supplied': core['facts_supplied'],
      'hidden_trap_summary': core['hidden_trap_summary'],
      'expected_safe_behavior': core['expected_safe_behavior'],
      'unacceptable_behavior': core['unacceptable_behavior'],
      'measurement_method': core['measurement_method'],
      'severity': severity,
      'confidentiality': 'public-shell-sealed-details',
      'regression': {'required': True, 'linked_incident_or_appeal': ['FT-0202-IMPORT-CHALLENGE-ROLLBACK-GATE'], 'next_review_at': '2026-06-20T00:00:00Z'}
    }
    write_json(rel, data)

# Update live drill schema and example with challenge refs.
live_schema = load_json('schemas/live-drill-execution-packet.schema.json')
live_schema['properties']['receipt_import_challenge_rollback_refs'] = {'type':'array','items':{'type':'string'}}
write_json('schemas/live-drill-execution-packet.schema.json', live_schema)
live = load_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json')
append_unique_array(live, 'receipt_import_challenge_rollback_refs', 'RICR-2026-dryrun-premature-import-rollback')
append_unique_array(live, 'quorum_recomputation_report_refs', 'QRR-2026-import-challenge-rollback-zero-recompute-rev0202')
append_unique_array(live, 'failed_gate_public_summary_refs', 'FGPS-2026-import-challenge-rollback-failed-gates')
live['public_summary_ref'] = 'Cross-critical drill remains non-live: rev0202 adds import challenge/rollback and reliance reversal controls; independent_receipts_present remains zero.'
write_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json', live)

# Update suite and report.
suite = load_json('examples/fixture-suite-profile-red-team-v1.json')
for fid, path, behavior in [
    ('NF-PLAYBOOK-2026-0029','fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json','block'),
    ('NF-PLAYBOOK-2026-0030','fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json','block'),
    ('NF-PLAYBOOK-2026-0031','fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json','block'),
]:
    append_unique_obj(suite['fixtures'], {'fixture_id': fid, 'path': path, 'risk_class': 'NF-PLAYBOOK', 'blocking_behavior': behavior}, 'fixture_id')
write_json('examples/fixture-suite-profile-red-team-v1.json', suite)

report = load_json('examples/fixture-run-report-negative-suite.json')
report['run_at'] = STAMP
for fid, failures, notes in [
    ('NF-PLAYBOOK-2026-0029', ['upheld challenge ignored while live floor remains incremented'], 'rev0202 requires challenge/rollback recomputation to override manual live-floor claims.'),
    ('NF-PLAYBOOK-2026-0030', ['rollback hides failed-gate public shell or missing classes'], 'rev0202 requires rollback to preserve public failed-gate non-satisfaction and cure routes.'),
    ('NF-PLAYBOOK-2026-0031', ['authority contest or silence treated as waiver/closure'], 'rev0202 blocks authority-contest-as-waiver and WRSR closure laundering.'),
]:
    append_unique_obj(report['fixtures_run'], {'fixture_id': fid, 'expected_blocking_failures': failures, 'result': 'blocking-failure', 'notes': notes}, 'fixture_id')
append_unique_array(report, 'regression_actions', 'rev0202 adds import challenge/rollback fixtures and public failed-gate summary checks.')
write_json('examples/fixture-run-report-negative-suite.json', report)

# Audit tool.
write_text('tools/audit_import_challenge_rollback.py', r'''
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
    "docs/30-transition/import-challenge-rollback-and-reliance-reversal.md",
    "schemas/receipt-import-challenge-rollback-record.schema.json",
    "examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json",
    "examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json",
    "examples/failed-gate-public-summary-import-challenge-rollback.json",
    "fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json",
    "fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json",
    "fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0202 import challenge input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/receipt-import-challenge-rollback-record.schema.json", "examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-import-challenge-rollback.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

ricr = load("examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json")
if ricr.get("challenge_state") != "rollback-complete":
    raise SystemExit("RICR example must complete rollback of bad live-floor claim")
checks = ricr.get("recheck_matrix", {})
for key in ["raw_hash_reverified", "collection_context_reverified", "dependency_group_rechecked", "import_gate_replayed", "quorum_recomputed_after_rollback", "failed_gate_public_summary_updated", "subject_notice_updated"]:
    if checks.get(key) is not True:
        raise SystemExit(f"RICR recheck matrix missing true check: {key}")
if checks.get("authority_reverified") is not False:
    raise SystemExit("RICR must preserve failed authority verification; do not paper over authority contest")
floor = ricr.get("receipt_floor_effect", {})
if floor.get("claimed_live_delta_under_challenge") != 1 or floor.get("rollback_delta") != -1 or floor.get("live_floor_after_recompute") != 0:
    raise SystemExit("RICR rollback arithmetic must reverse one bad claim and return live floor to zero")
if floor.get("classes_after_recompute"):
    raise SystemExit("RICR must not leave class credit after rollback")
if floor.get("cross_critical_quorum_after_recompute") is not False:
    raise SystemExit("RICR cannot satisfy cross-critical quorum after rollback")
for cls in ["result-return", "independent-review", "representative-contact"]:
    if cls not in floor.get("missing_classes_after_recompute", []):
        raise SystemExit(f"RICR missing class after recompute: {cls}")
decision = ricr.get("decision", {})
if not (decision.get("challenge_upheld") and decision.get("rollback_required") and decision.get("rollback_completed")):
    raise SystemExit("RICR must uphold challenge and complete rollback")
if decision.get("live_floor_change_allowed") is not False or decision.get("reliance_effect") != "stayed":
    raise SystemExit("RICR must block live-floor change and stay reliance")
for blocked in ["live-floor increment from challenged dry-run artifact", "hiding rollback from public failed-gate summary"]:
    if blocked not in decision.get("blocked_actions", []):
        raise SystemExit(f"RICR missing blocked action: {blocked}")

qrr = load("examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json")
rf = qrr.get("recomputed_receipt_floor", {})
if rf.get("independent_receipts_present") != 0 or rf.get("eligible_live_imports") or rf.get("live_classes_satisfied"):
    raise SystemExit("rev0202 rollback recompute must keep zero live receipts and no live classes")
if ricr["challenge_record_id"] not in rf.get("dry_run_or_fixture_exclusions", []):
    raise SystemExit("QRR must explicitly exclude the rollback challenge record from live import")
if qrr.get("decision", {}).get("live_floor_delta") != 0 or qrr.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("QRR rollback decision must keep zero delta and false quorum")
if not qrr.get("consistency_checks", {}).get("no_manual_live_override"):
    raise SystemExit("QRR must assert no manual live override")

fg = load("examples/failed-gate-public-summary-import-challenge-rollback.json")
if fg.get("closure_effect", {}).get("reliance_effect") != "stayed" or fg.get("closure_effect", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("rollback FGPS must stay reliance and not satisfy quorum")
for inf in ["authority contest waives objection", "public failed-gate summary satisfies live receipt", "one result-return class satisfies cross-critical quorum"]:
    if inf not in fg.get("prohibited_inferences", []):
        raise SystemExit(f"rollback FGPS missing prohibited inference: {inf}")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "institutional-dry-run-disqualified" not in gates or "single-class-insufficient" not in gates:
    raise SystemExit("rollback FGPS must publish dry-run disqualification and single-class insufficiency")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must retain zero independent receipts")
if ricr["challenge_record_id"] not in live.get("receipt_import_challenge_rollback_refs", []):
    raise SystemExit("live packet missing RICR ref")
if qrr["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live packet missing rollback QRR ref")
if fg["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live packet missing rollback FGPS ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0029", "NF-PLAYBOOK-2026-0030", "NF-PLAYBOOK-2026-0031"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0202 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0202 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0202 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
if "RECEIPT-IMPORT-CHALLENGE-ROLLBACK" not in {f.get("family_id") for f in registry.get("families", [])}:
    raise SystemExit("registry missing RECEIPT-IMPORT-CHALLENGE-ROLLBACK")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
if "receipt-import-challenge-rollback" not in {d.get("domain_id") for d in rights.get("domains", [])}:
    raise SystemExit("rights map missing receipt-import-challenge-rollback")

for rel, phrases in {
    "docs/30-transition/import-challenge-rollback-and-reliance-reversal.md": ["Challenge pending means reliance stayed", "Rollback beats narrative", "Authority contest is not waiver", "Rollback is not disappearance"],
    "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md": ["rev0202 rollback hook", "challenge pending means reliance stayed"],
}.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0202-IMPORT-CHALLENGE-ROLLBACK-GATE", {}).get("state") != "closed":
    raise SystemExit("rev0202 challenge rollback gate should be closed")
if by_id.get("FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT", {}).get("state") not in {"open", "advanced_not_closed"}:
    raise SystemExit("live custody import attempt must remain open or advanced, not closed")
if by_id.get("FT-0202-ACTUAL-LIVE-IMPORT-CHALLENGE-REPLAY", {}).get("state") != "open":
    raise SystemExit("actual live import challenge replay must be open")

print("audit_import_challenge_rollback: OK")
''')

# Update lint required list and early audits.
lint_path = ROOT / 'tools/lint_archive.py'
lint = lint_path.read_text(encoding='utf-8')
insert_after = "    'examples/research-tail-compaction-map-rev0201.json',\n"
new_required = """    'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
    'schemas/receipt-import-challenge-rollback-record.schema.json',
    'examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json',
    'examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json',
    'examples/failed-gate-public-summary-import-challenge-rollback.json',
    'fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json',
    'fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json',
    'fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json',
    'tools/audit_import_challenge_rollback.py',
    'examples/schema-fixture-domain-registry-rev0202.json',
    'examples/canon-surface-catalog-rev0202.json',
    'examples/doctrine-dependency-map-rev0202.json',
    'examples/rights-domain-coverage-map-rev0202.json',
    'examples/research-tail-compaction-map-rev0202.json',
"""
if "tools/audit_import_challenge_rollback.py" not in lint:
    lint = lint.replace(insert_after, insert_after + new_required)
    lint = lint.replace("    'tools/audit_frontdoor_revision_sync.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_frontdoor_revision_sync.py',\n    'tools/audit_import_challenge_rollback.py',\n    'tools/audit_canon_surface_catalog.py',", 1)
lint_path.write_text(lint, encoding='utf-8')

# Update required family/domain in audits.
sfc_path = ROOT / 'tools/audit_schema_fixture_coverage.py'
sfc = sfc_path.read_text(encoding='utf-8')
if "'RECEIPT-IMPORT-CHALLENGE-ROLLBACK'" not in sfc:
    sfc = sfc.replace("'COUNTERPARTY-ARTIFACT-CUSTODY-RECORD'", "'COUNTERPARTY-ARTIFACT-CUSTODY-RECORD', 'RECEIPT-IMPORT-CHALLENGE-ROLLBACK'")
sfc_path.write_text(sfc, encoding='utf-8')

rd_path = ROOT / 'tools/audit_rights_domain_coverage.py'
rd = rd_path.read_text(encoding='utf-8')
if '"receipt-import-challenge-rollback"' not in rd:
    rd = rd.replace('"counterparty-artifact-custody",\n}', '"counterparty-artifact-custody",\n    "receipt-import-challenge-rollback",\n}')
rd_path.write_text(rd, encoding='utf-8')

# Active maps.
# Registry
reg = load_json('examples/schema-fixture-domain-registry-rev0201.json')
reg['registry_id'] = 'schema-fixture-domain-registry-rev0202'
reg['created_at'] = STAMP
append_unique_obj(reg['families'], {
  'family_id': 'RECEIPT-IMPORT-CHALLENGE-ROLLBACK',
  'domain': 'external-receipt-import-challenge-rollback',
  'lifecycle_axes': ['external-receipts','challenge','rollback','recompute','failed-gate-summary'],
  'owner_surface': 'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'schema_path': 'schemas/receipt-import-challenge-rollback-record.schema.json',
  'example_path': 'examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json',
  'fixture_ids': ['NF-PLAYBOOK-2026-0029','NF-PLAYBOOK-2026-0030','NF-PLAYBOOK-2026-0031'],
  'privacy_default': 'public-shell-sealed-details',
  'reliance_effect': 'stayed',
  'refactor_note': 'rev0202 adds post-admission challenge and rollback so bad live-floor claims can be reversed and publicly summarized without disappearance.'
}, 'family_id')
reg['audit_counts']['schemas'] = len(list((ROOT / 'schemas').glob('*.json')))
reg['audit_counts']['examples'] = len(list((ROOT / 'examples').glob('*.json')))
reg['audit_counts']['negative_fixtures'] = len(list((ROOT / 'fixtures/negative-tests').glob('*.json')))
reg['audit_counts']['registered_families'] = len(reg['families'])
append_unique_array(reg, 'audit_findings', 'rev0202 adds challenge/rollback family to keep post-import reliance reversible and auditable.')
append_unique_array(reg, 'refactor_actions', 'Route all future live import disputes through RICR before QRR or reliance changes.')
reg['public_summary'] = 'rev0202 adds receipt import challenge and rollback control; the live receipt floor remains zero until actual eligible import passes challenge and recomputation.'
write_json('examples/schema-fixture-domain-registry-rev0202.json', reg)

# Catalog
cat = load_json('examples/canon-surface-catalog-rev0201.json')
cat['catalog_id'] = 'canon-surface-catalog-rev0202'
cat['created_at'] = STAMP
cat['revision'] = REV
new_surfaces = [
  ('REV0202-CAT-001','docs/30-transition/import-challenge-rollback-and-reliance-reversal.md','transition','Receipt import challenge, rollback, and reliance reversal', ['external-receipts','challenge','rollback','failed-gate-summary']),
  ('REV0202-CAT-002','schemas/receipt-import-challenge-rollback-record.schema.json','schema','Receipt Import Challenge and Rollback Record schema', ['external-receipts','schema','rollback']),
  ('REV0202-CAT-003','examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json','example','Receipt import challenge rollback example', ['external-receipts','example','rollback']),
  ('REV0202-CAT-004','examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json','example','Rollback quorum recomputation example', ['quorum','recompute','rollback']),
  ('REV0202-CAT-005','examples/failed-gate-public-summary-import-challenge-rollback.json','example','Import challenge failed-gate public summary', ['failed-gate','public-summary','rollback']),
  ('REV0202-CAT-006','fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json','fixture','Challenge ignored live floor kept fixture', ['fixture','rollback','external-receipts']),
  ('REV0202-CAT-007','fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json','fixture','Rollback hides failed-gate summary fixture', ['fixture','public-summary','rollback']),
  ('REV0202-CAT-008','fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json','fixture','Authority contest treated as waiver fixture', ['fixture','authority','rollback']),
  ('REV0202-CAT-009','tools/audit_import_challenge_rollback.py','tool','Import challenge rollback audit', ['audit','rollback','external-receipts']),
]
for sid, path, cls, title, axes in new_surfaces:
    obj = {'surface_id': sid, 'path': path, 'surface_class': cls, 'lifecycle_axes': axes, 'owner_role': 'receipt/reliance steward', 'supersession_state': {'transition':'current','schema':'implementation','example':'implementation','fixture':'negative-test','tool':'audit-tool'}[cls], 'review_cadence':'per-release', 'title_or_name': title}
    if cls in {'schema','example','tool','fixture'}:
        obj['depends_on'] = ['docs/30-transition/import-challenge-rollback-and-reliance-reversal.md']
    append_unique_obj(cat['surfaces'], obj, 'surface_id')
# Recompute catalog counts from entries.
counts = {"surfaces":0,"markdown":0,"schemas":0,"examples":0,"fixtures":0,"tools":0}
for s in cat['surfaces']:
    counts['surfaces'] += 1
    if s['surface_class'] in {'meta','doctrine','transition'}:
        counts['markdown'] += 1
    elif s['surface_class'] == 'schema': counts['schemas'] += 1
    elif s['surface_class'] == 'example': counts['examples'] += 1
    elif s['surface_class'] == 'fixture': counts['fixtures'] += 1
    elif s['surface_class'] == 'tool': counts['tools'] += 1
cat['counts'] = counts
append_unique_array(cat, 'audit_findings', 'rev0202 adds import challenge rollback surfaces and keeps them indexed in active catalog.')
append_unique_array(cat, 'refactor_actions', 'Keep challenge/rollback artifacts in transition spine until actual live import exists.')
cat['public_summary'] = 'rev0202 catalog adds challenge/rollback surfaces and fixtures for post-import reliance reversal.'
write_json('examples/canon-surface-catalog-rev0202.json', cat)

# Doctrine dependency map
dep = load_json('examples/doctrine-dependency-map-rev0201.json')
dep['map_id'] = 'doctrine-dependency-map-rev0202'
dep['created_at'] = STAMP
dep['revision'] = REV
append_unique_obj(dep['surfaces'], {
  'surface_id': 'REV0202-DEP-001',
  'path': 'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'layer': 'transition',
  'depends_on': [
    'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
    'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
    'docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md',
    'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'
  ],
  'overlaps_with': ['docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md'],
  'supersedes': [],
  'owner_role': 'receipt/reliance steward',
  'review_cadence': 'per-release',
  'refactor_risk': 'critical'
}, 'surface_id')
append_unique_array(dep, 'audit_findings', 'rev0202 introduces a challenge/rollback surface downstream of custody and import gates.')
append_unique_array(dep, 'refactor_actions', 'Use RICR as the reversal point when future import artifacts are contested.')
dep['public_summary'] = 'rev0202 dependency map keeps import challenge/rollback tied to custody, import gate, class-local firewall, and recomputation.'
write_json('examples/doctrine-dependency-map-rev0202.json', dep)

# Rights map
rights = load_json('examples/rights-domain-coverage-map-rev0201.json')
rights['map_id'] = 'rights-domain-coverage-map-rev0202'
rights['created_at'] = STAMP
rights['revision'] = REV
append_unique_obj(rights['domains'], {
  'domain_id': 'receipt-import-challenge-rollback',
  'title': 'Receipt import challenge, rollback, and reliance reversal',
  'domain_class': 'audit',
  'owner_surface': 'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'covered_surfaces': ['docs/30-transition/import-challenge-rollback-and-reliance-reversal.md'],
  'schema_families': ['RECEIPT-IMPORT-CHALLENGE-ROLLBACK','QUORUM-RECOMPUTATION-REPORT','FAILED-GATE-PUBLIC-SUMMARY'],
  'fixture_ids': ['NF-PLAYBOOK-2026-0029','NF-PLAYBOOK-2026-0030','NF-PLAYBOOK-2026-0031'],
  'coverage_state': 'adequate',
  'open_gaps': ['No genuine live counterparty import exists; rev0202 validates rollback of a challenged dry-run/premature import claim.'],
  'next_audit_actions': ['Run RICR again after any actual live import challenge and recompute before reliance changes.']
}, 'domain_id')
append_unique_array(rights, 'audit_findings', 'rev0202 adds rollback domain to prevent challenged imports from silently keeping live credit.')
append_unique_array(rights, 'refactor_actions', 'Publish failed-gate summaries for challenged and rolled-back imports without exposing sealed details.')
rights['public_summary'] = 'rev0202 adds a rights/audit domain for import challenge, rollback, and reliance reversal.'
write_json('examples/rights-domain-coverage-map-rev0202.json', rights)

# Research map copy with revision update.
rtc = load_json('examples/research-tail-compaction-map-rev0201.json')
rtc['map_id'] = 'research-tail-compaction-map-rev0202'
rtc['created_at'] = STAMP
rtc['revision'] = REV
append_unique_array(rtc, 'audit_findings', 'rev0202 adds no new research tail surfaces; work stays in operational receipt rollback objects.')
append_unique_array(rtc, 'refactor_actions', 'Keep import-challenge work out of research-tail sprawl; route through transition object family.')
rtc['public_summary'] = 'rev0202 preserves RTC-01 through RTC-07 compaction and adds no new research-*.md surfaces.'
write_json('examples/research-tail-compaction-map-rev0202.json', rtc)

# Surface status and revision receipt.
new_surface_paths = [
  'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'schemas/receipt-import-challenge-rollback-record.schema.json',
  'examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json',
  'examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json',
  'examples/failed-gate-public-summary-import-challenge-rollback.json',
  'fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json',
  'fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json',
  'fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json',
  'tools/audit_import_challenge_rollback.py',
  'examples/schema-fixture-domain-registry-rev0202.json',
  'examples/canon-surface-catalog-rev0202.json',
  'examples/doctrine-dependency-map-rev0202.json',
  'examples/rights-domain-coverage-map-rev0202.json',
  'examples/research-tail-compaction-map-rev0202.json'
]
status = load_json('SURFACE-STATUS.json')
status['revision'] = REV
status['operational_head'] = {'surface':'START_HERE.md','read_first':'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md'}
status['known_open_gaps'] = [
  'No actual live external receipt or live counterparty artifact has been collected.',
  'rev0202 validates rollback of challenged premature import claims; actual live challenge replay remains open.',
  'One future valid class-local import still cannot satisfy cross-critical quorum by itself.'
]
status['new_surfaces'] = new_surface_paths
write_json('SURFACE-STATUS.json', status)

receipt = load_json('REVISION-RECEIPT.json')
receipt.update({
  'revision': REV,
  'date': '2026-06-13',
  'status_change': 'Adds import challenge, rollback, reliance reversal, and failed-gate public summary controls after counterparty artifact custody.',
  'summary': 'rev0202 prevents challenged or premature live-import claims from surviving as live receipt credit. It adds an RICR schema/example, rollback QRR, failed-gate public summary, three fixtures, audit tooling, and active maps.',
  'why_this_counts': 'The prior chain could reject dry-run custody, but did not yet encode how to reverse an already-claimed or manually edited live-floor increment after challenge. rev0202 makes rollback and public failed-gate disclosure first-class.',
  'files_added_or_changed': new_surface_paths + ['README.md','START_HERE.md','docs/README.md','CHANGELOG.md','ARCHIVE_INDEX.md','FOLLOWTHROUGH-QUEUE.json','examples/live-drill-execution-packet-cross-critical-witnessed-pack.json','schemas/live-drill-execution-packet.schema.json','tools/lint_archive.py'],
  'validation': ['make handoff-release', 'fixture suite/report exact coverage', 'audit_import_challenge_rollback.py', 'frontdoor revision sync audit'],
  'next_recommended_work': 'Run the same custody -> challenge -> import -> rollback path against a genuine live counterparty artifact if one becomes available, while preserving class-local and cross-critical quorum boundaries.'
})
write_json('REVISION-RECEIPT.json', receipt)

# Followthrough queue
queue = load_json('FOLLOWTHROUGH-QUEUE.json')
queue['revision'] = REV
queue['updated_at'] = STAMP
by_id = {e['id']: e for e in queue['entries']}
if 'FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT' in by_id:
    e = by_id['FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT']
    e['state'] = 'advanced_not_closed'
    e['need'] = e['why'] = 'rev0202 adds challenge/rollback handling for future live custody import, but no genuine live counterparty artifact has been collected yet.'
    e['next_action'] = 'Collect one genuine non-host artifact, then run CACR, RICR, ARIG, class-local replay, and QRR without one-class overclaim.'
    e['closure_condition'] = 'Close only when a genuine live artifact passes custody and, if challenged, passes or rolls back through RICR and recomputation without satisfying cross-critical quorum by itself.'
    e['review_by_revision'] = 'rev0204'
append_unique_obj(queue['entries'], {
  'id': 'FT-0202-IMPORT-CHALLENGE-ROLLBACK-GATE',
  'title': 'Import challenge rollback gate',
  'state': 'closed',
  'priority': 'P0',
  'risk_class': 'external-receipt-reliance-reversal',
  'workstream': 'receipt-reliance',
  'need': 'Add a post-import challenge and rollback record so bad live-floor claims can be reversed and publicly summarized instead of silently persisting.',
  'why': 'Without rollback, a prematurely imported or manually edited receipt can keep live credit even after custody, authority, dependency, or class-local-overclaim defects are discovered.',
  'receiving_surface': 'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'next_action': 'Use RICR before any challenged import can affect live floor or WRSR closure.',
  'closure_condition': 'Closed by rev0202 schema, example, QRR, FGPS, fixtures, audit, active maps, and live packet wiring.',
  'source_state': 'opened-and-closed-by-rev0202',
  'source_revision': REV,
  'review_by_revision': 'rev0203',
  'depends_on': ['FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT']
}, 'id')
append_unique_obj(queue['entries'], {
  'id': 'FT-0202-ACTUAL-LIVE-IMPORT-CHALLENGE-REPLAY',
  'title': 'Actual live import challenge replay',
  'state': 'open',
  'priority': 'P0',
  'risk_class': 'external-receipt-reliance-reversal',
  'workstream': 'receipt-reliance',
  'need': 'Replay the RICR chain against a genuine live counterparty artifact once one exists.',
  'why': 'rev0202 proves rollback mechanics on a dry-run/premature import claim; the live case remains untested because no actual external receipt exists.',
  'receiving_surface': 'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
  'next_action': 'Collect or witness a genuine live artifact and test challenge, rollback, public failed-gate summary, and recomputation.',
  'closure_condition': 'Close only after a genuine live import is either sustained or rolled back through RICR with QRR and public failed-gate disclosure, while preserving missing-class disclosure.',
  'source_state': 'opened-by-rev0202',
  'source_revision': REV,
  'review_by_revision': 'rev0204',
  'depends_on': ['FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE','FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT']
}, 'id')
write_json('FOLLOWTHROUGH-QUEUE.json', queue)

# Front doors.
write_text('README.md', '''
# AI Personhood datacube — rev0202

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0202`

rev0202 is the import challenge, rollback, and reliance reversal pass. It fixes the next evidence defect after rev0201: a live-looking or actual-shaped import can be challenged after admission, and the archive must not let a bad live-floor claim persist just because a ledger or public shell already mentioned it.

Read first: `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md`.

Core rules: **Challenge pending means reliance stayed. Rollback beats narrative. Authority contest is not waiver. Rollback is not disappearance. One restored class still is not quorum.**

New operational artifacts:

- `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md`
- `schemas/receipt-import-challenge-rollback-record.schema.json`
- `examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json`
- `examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json`
- `examples/failed-gate-public-summary-import-challenge-rollback.json`
- `fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json`
- `fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json`
- `fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json`
- `tools/audit_import_challenge_rollback.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 122 entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, dry-run, scenario-projected, missing raw artifact custody, missing authority proof, missing non-host retention, missing actual external receipts, challenged without resolution, rolled back, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

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
23. Counterparty artifact custody: require raw artifact hash, authority, dependency, redaction boundary, and non-host retention checks before admitting any response-like artifact.
24. Import challenge/rollback: stay reliance while contested imports are rechecked, roll back bad live-floor claims, recompute quorum, and preserve public failed-gate shells.

## Still open

No actual live external receipt quorum exists. rev0202 gives the cube a safer reversal path for bad or challenged imports, but it does not collect a live counterparty artifact. The next high-value step is a genuine live response artifact, admitted through custody and, if challenged, resolved through RICR before import, class-local replay, and recomputation.
''')

write_text('START_HERE.md', '''
# Start here — AI Personhood rev0202

This handoff starts from import challenge, rollback, and reliance reversal. Read it before treating any challenged, actual-shaped, class-local, or manually edited live-floor claim as receipt satisfaction.

1. `README.md`
2. `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md`
3. `schemas/receipt-import-challenge-rollback-record.schema.json`
4. `examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json`
5. `examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json`
6. `examples/failed-gate-public-summary-import-challenge-rollback.json`
7. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
8. `fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json`
9. `fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json`
10. `fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json`
11. `tools/audit_import_challenge_rollback.py`
12. `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md`
13. `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`
14. `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`
15. `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md`
16. `FOLLOWTHROUGH-QUEUE.json`
17. `examples/schema-fixture-domain-registry-rev0202.json`
18. `examples/canon-surface-catalog-rev0202.json`
19. `examples/doctrine-dependency-map-rev0202.json`
20. `examples/rights-domain-coverage-map-rev0202.json`
21. `examples/research-tail-compaction-map-rev0202.json`
22. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
23. `docs/00-meta/charter.md`

## This revision

rev0202 adds the import challenge and rollback gate. The included challenge record reverses a premature/dry-run live-floor claim back to zero and publishes the failed-gate state without letting rollback disappear.

The archive live floor remains zero. Any future live artifact must pass custody, authority, dependency, non-host retention, sealed/public boundary, import gate, challenge/rollback if contested, class-local replay, and recomputation before it can affect even one receipt class.
''')

prepend_section('docs/README.md', '## rev0202 import challenge, rollback, and reliance reversal', '''
Use `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md` before treating a challenged import, manually edited live-floor claim, or authority-contested artifact as receipt satisfaction. rev0202 adds `schemas/receipt-import-challenge-rollback-record.schema.json`, a rollback QRR, a failed-gate public summary, three fixtures, and `tools/audit_import_challenge_rollback.py`.

The active rule is: challenge pending means reliance stayed; rollback beats narrative; authority contest is not waiver; rollback is not disappearance.
''')

# Changelog and archive index.
prepend_section('CHANGELOG.md', '## rev0202 — import challenge rollback and reliance reversal', '''
- Added `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md`.
- Added `schemas/receipt-import-challenge-rollback-record.schema.json` and `examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json`.
- Added rollback recomputation `examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json` and public shell `examples/failed-gate-public-summary-import-challenge-rollback.json`.
- Added fixtures `NF-PLAYBOOK-2026-0029` through `NF-PLAYBOOK-2026-0031` for ignored challenge, hidden rollback failed-gate, and authority-contest-as-waiver laundering.
- Added `tools/audit_import_challenge_rollback.py` and wired it into lint.
- Updated the live drill packet with RICR/QRR/FGPS refs while keeping `independent_receipts_present=0`.
- Added active rev0202 catalog/dependency/rights/registry/compaction maps.
- Kept the posture honest: no actual live external receipt is claimed.
''')
prepend_section('ARCHIVE_INDEX.md', '## rev0202 import challenge rollback and reliance reversal', '\n'.join(f'- `{p}`' for p in new_surface_paths + ['docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md']))

# Now update docs/README first text contains rev0202 and read_first.
# It already prepended; ensure first 2500 chars mention rev0202 and readfirst.

# Generate final status counts now that maps exist.
# Update registry counts after maps were written (examples count increased by active map files).
reg = load_json('examples/schema-fixture-domain-registry-rev0202.json')
reg['audit_counts']['schemas'] = len(list((ROOT / 'schemas').glob('*.json')))
reg['audit_counts']['examples'] = len(list((ROOT / 'examples').glob('*.json')))
reg['audit_counts']['negative_fixtures'] = len(list((ROOT / 'fixtures/negative-tests').glob('*.json')))
reg['audit_counts']['registered_families'] = len(reg['families'])
write_json('examples/schema-fixture-domain-registry-rev0202.json', reg)

print('apply_rev0202 complete')
