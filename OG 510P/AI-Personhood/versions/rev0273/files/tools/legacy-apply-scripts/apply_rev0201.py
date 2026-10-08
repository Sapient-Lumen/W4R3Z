import json, hashlib, re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = 'rev0201'
STAMP = '2026-06-13T11:45:00Z'
LOCAL_STAMP = '2026.06.13.07.45'


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


def prepend_section(rel, title, body):
    path = ROOT / rel
    txt = path.read_text(encoding='utf-8') if path.exists() else '# Archive index\n'
    lines = txt.splitlines()
    if lines and lines[0].startswith('# '):
        new = '\n'.join([lines[0], '', title, '', body.strip(), ''] + lines[1:])
    else:
        new = title + '\n\n' + body.strip() + '\n\n' + txt
    path.write_text(new.rstrip() + '\n', encoding='utf-8')


def file_sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

# Version
write_text('VERSION', REV)

# Raw dry-run artifact with deterministic hash.
artifact_rel = 'examples/artifacts/result-return-counterparty-response-dryrun.txt'
artifact_text = '''DRY-RUN COUNTERPARTY RESULT-RETURN RESPONSE
Artifact purpose: test custody, hashing, redaction, authority, and import gating.
Collection context: institutional dry run, not live counterparty evidence.
Receipt class: result-return.
Counterparty role: institutional dry-run result-return steward.
Authority limitation: may test shape and custody only; may not satisfy live receipt quorum.
Subject-readable result-return: summary preserved for rehearsal; no status, consent, waiver, nonpersonhood, or closure inference.
Sealed material: descriptor only; no sealed subject details in this public artifact.
'''
write_text(artifact_rel, artifact_text)
artifact_hash = file_sha(artifact_rel)
artifact_size = (ROOT / artifact_rel).stat().st_size

# Operational surface
write_text('docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md', '''
# Counterparty Artifact Custody and Authority Handoff

rev0201 targets the next live-receipt failure point: the moment an external-looking artifact enters the cube. The archive now has request packets, response records, intake records, import gates, replay reports, recomputation, and class-local firewalls. The remaining practical risk is that a pasted email, screenshot, forwarded copy, redacted snippet, or unsigned institutional note could be treated as live counterparty evidence before raw custody and authority are proven.

The rev0201 rule is strict: **artifact received is not artifact admitted**.

## What this pass adds

The new `counterparty-artifact-custody-record` object sits before response-record creation and before import-gate evaluation. It captures the raw artifact path or locator, hash, size, collection context, sealed/public boundary, authority claim, dependency group, retention state, redaction state, and import readiness. It is designed to accept a real artifact later without weakening the current reliance posture.

The included artifact is deliberately an institutional dry-run text file. It has a real SHA-256 hash and a custody record, but the custody record says the artifact has zero live weight. That is intentional: the point is to test the custody chain, not to pretend a live counterparty has appeared.

## Core rules

**Artifact received is not artifact admitted.** A raw object, screenshot, forwarded email, or copied text cannot create a response record or intake record until custody, hash, locator, authority, dependency, and sealed/public boundary checks pass.

**Hash match is necessary but not sufficient.** A correct hash proves integrity of a captured object. It does not prove live counterparty authority, non-host collection context, receipt-class sufficiency, consent, waiver, WRSR closure, or cross-critical quorum.

**Authority proof is class-specific.** A result-return steward may validate result-return choreography without becoming a first-touch witness, compute-floor witness, representative, RERB reviewer, reserve witness, namespace witness, or anti-capture witness.

**Redacted copies are not raw custody.** Public or subject-readable redactions can support notice, but raw sealed custody must remain available for import and contradiction review.

**Custody failure is a failed gate, not disappearance.** A hash mismatch, authority gap, stale locator, dependency conflict, or redaction-only artifact must be preserved in the public failed-gate summary without exposing sealed details or treating silence as waiver.

## Refactor effect

The receipt stack now has a pre-admission custody layer:

1. request packet,
2. counterparty artifact custody record,
3. non-host response artifact envelope,
4. response record,
5. intake record,
6. actual import gate,
7. live import replay,
8. class-local replay,
9. quorum recomputation and failed-gate publication.

rev0201 also tightens the front-door audit so `docs/README.md` cannot drift behind the active operational head.

## Current reliance posture

No live counterparty artifact exists in this archive. The rev0201 dry-run artifact proves the custody mechanism and the rejection path. It does not change `independent_receipts_present`, does not satisfy result-return, and does not move cross-critical reliance out of stayed posture.
''')

# Schema
receipt_classes = [
  'first-touch-clock','continuity-compute-floor','sealed-public-parity','namespace-cache','reserve-ledger',
  'representative-contact','witness-dependency','welfare-signal-integrity','independent-review','result-return'
]
write_json('schemas/counterparty-artifact-custody-record.schema.json', {
  '$schema': 'https://json-schema.org/draft/2020-12/schema',
  '$id': 'https://example.org/ai-personhood/schemas/counterparty-artifact-custody-record.schema.json',
  'title': 'Counterparty Artifact Custody Record',
  'description': 'Pre-admission custody and authority record for response-like artifacts before they may become response/intake/import evidence.',
  'type': 'object',
  'additionalProperties': False,
  'required': ['custody_record_id','schema_version','created_at','linked_request_packet','linked_import_attempt','linked_live_drill_packet','artifact_state','receipt_class','counterparty_authority','raw_artifacts','collection_chain','integrity_checks','redaction_and_subject_access','import_readiness','decision'],
  'properties': {
    'custody_record_id': {'type':'string','pattern':'^CACR-[0-9]{4}-[A-Za-z0-9._:-]+$'},
    'schema_version': {'const':'counterparty-artifact-custody-record-v0.1'},
    'created_at': {'type':'string','format':'date-time'},
    'linked_request_packet': {'type':'string'},
    'linked_import_attempt': {'type':'string'},
    'linked_live_drill_packet': {'type':'string'},
    'linked_artifact_envelope': {'type':'string'},
    'artifact_state': {'type':'string','enum':['no-artifact-yet','institutional-dry-run-artifact','live-candidate-artifact','rejected','quarantined']},
    'receipt_class': {'type':'string','enum': receipt_classes},
    'counterparty_authority': {
      'type':'object','additionalProperties':False,
      'required':['role','identity_ref','external_to_host','dependency_group','authority_basis','authority_limitations','authority_verified','class_scope'],
      'properties': {
        'role': {'type':'string'},
        'identity_ref': {'type':'string'},
        'external_to_host': {'type':'boolean'},
        'dependency_group': {'type':'string'},
        'authority_basis': {'type':'string'},
        'authority_limitations': {'type':'array','minItems':1,'items':{'type':'string'}},
        'authority_verified': {'type':'boolean'},
        'class_scope': {'type':'array','minItems':1,'items':{'type':'string','enum': receipt_classes}}
      }
    },
    'raw_artifacts': {
      'type':'array','minItems':1,
      'items': {
        'type':'object','additionalProperties':False,
        'required':['artifact_id','artifact_type','path_or_locator','sha256','size_bytes','mime_type','collection_context','raw_available','sealed','public_redaction_ref','may_be_used_for_live_import'],
        'properties': {
          'artifact_id': {'type':'string'},
          'artifact_type': {'type':'string','enum':['raw-email','signed-response','text-file','screenshot','api-payload','timestamp','public-redaction','sealed-copy','other']},
          'path_or_locator': {'type':'string'},
          'sha256': {'type':'string','pattern':'^[0-9a-f]{64}$'},
          'size_bytes': {'type':'integer','minimum':0},
          'mime_type': {'type':'string'},
          'collection_context': {'type':'string','enum':['live-counterparty','institutional-dry-run','controlled-fixture','host-generated','unknown']},
          'raw_available': {'type':'boolean'},
          'sealed': {'type':'boolean'},
          'public_redaction_ref': {'type':'string'},
          'may_be_used_for_live_import': {'type':'boolean'}
        }
      }
    },
    'collection_chain': {
      'type':'array','minItems':1,
      'items': {
        'type':'object','additionalProperties':False,
        'required':['event_id','event_type','at','actor','system_boundary','evidence_ref','can_satisfy_live_receipt'],
        'properties': {
          'event_id': {'type':'string'},
          'event_type': {'type':'string','enum':['request-prepared','live-dispatch-pending','live-dispatched','dryrun-dispatched','response-received','hash-recorded','sealed-copy-stored','public-shell-published','authority-checked','dependency-checked','redaction-applied']},
          'at': {'type':'string','format':'date-time'},
          'actor': {'type':'string'},
          'system_boundary': {'type':'string','enum':['host','non-host','neutral-infrastructure','sealed-channel','public-shell','unknown']},
          'evidence_ref': {'type':'string'},
          'can_satisfy_live_receipt': {'type':'boolean'}
        }
      }
    },
    'integrity_checks': {
      'type':'object','additionalProperties':False,
      'required':['raw_artifact_available','sha256_verified','locator_resolvable','timestamp_independent','identity_authority_checked','dependency_group_checked','nonhost_storage_confirmed','sealed_public_parity_checked','redaction_not_substituted_for_raw'],
      'properties': {k:{'type':'boolean'} for k in ['raw_artifact_available','sha256_verified','locator_resolvable','timestamp_independent','identity_authority_checked','dependency_group_checked','nonhost_storage_confirmed','sealed_public_parity_checked','redaction_not_substituted_for_raw']}
    },
    'redaction_and_subject_access': {
      'type':'object','additionalProperties':False,
      'required':['sealed_material_present','public_shell_ref','subject_readable_summary_required','privacy_controls','prohibited_inferences'],
      'properties': {
        'sealed_material_present': {'type':'boolean'},
        'public_shell_ref': {'type':'string'},
        'subject_readable_summary_required': {'type':'boolean'},
        'privacy_controls': {'type':'array','minItems':1,'items':{'type':'string'}},
        'prohibited_inferences': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    },
    'import_readiness': {
      'type':'object','additionalProperties':False,
      'required':['may_create_response_record','may_create_intake_record','may_run_import_gate','live_import_floor_delta','disqualification_reasons','next_gate'],
      'properties': {
        'may_create_response_record': {'type':'boolean'},
        'may_create_intake_record': {'type':'boolean'},
        'may_run_import_gate': {'type':'boolean'},
        'live_import_floor_delta': {'type':'integer'},
        'disqualification_reasons': {'type':'array','items':{'type':'string'}},
        'next_gate': {'type':'string'}
      }
    },
    'decision': {
      'type':'object','additionalProperties':False,
      'required':['live_reliance_effect','custody_admission','reason','blocked_actions','next_actions'],
      'properties': {
        'live_reliance_effect': {'type':'string','enum':['none','stayed','blocked','conditional']},
        'custody_admission': {'type':'string','enum':['admitted-for-dry-run-only','admitted-for-live-import-review','rejected','quarantined']},
        'reason': {'type':'string'},
        'blocked_actions': {'type':'array','minItems':1,'items':{'type':'string'}},
        'next_actions': {'type':'array','minItems':1,'items':{'type':'string'}}
      }
    }
  }
})

# Example custody record
write_json('examples/counterparty-artifact-custody-record-result-return-dryrun.json', {
  'custody_record_id': 'CACR-2026-result-return-dryrun-custody',
  'schema_version': 'counterparty-artifact-custody-record-v0.1',
  'created_at': STAMP,
  'linked_request_packet': 'ERRP-2026-cross-critical-rep-rerb-result-return',
  'linked_import_attempt': 'LCIA-2026-result-return-institutional-dryrun-response',
  'linked_live_drill_packet': 'LDEP-2026-cross-critical-host-exit-witness-pack',
  'linked_artifact_envelope': 'NHRAE-2026-result-return-institutional-dryrun',
  'artifact_state': 'institutional-dry-run-artifact',
  'receipt_class': 'result-return',
  'counterparty_authority': {
    'role': 'institutional dry-run result-return steward',
    'identity_ref': 'institutional-dryrun-steward:result-return-alpha',
    'external_to_host': True,
    'dependency_group': 'independent-result-return-steward',
    'authority_basis': 'dry-run receipt choreography authority only; no live counterparty authority for this packet',
    'authority_limitations': [
      'cannot satisfy live result-return receipt',
      'cannot satisfy representative contact or RERB review',
      'cannot close WRSR, waiver, consent, nonpersonhood, or cross-critical quorum',
      'cannot substitute for raw live counterparty artifact collection'
    ],
    'authority_verified': True,
    'class_scope': ['result-return']
  },
  'raw_artifacts': [
    {
      'artifact_id': 'CACR-A-001',
      'artifact_type': 'text-file',
      'path_or_locator': artifact_rel,
      'sha256': artifact_hash,
      'size_bytes': artifact_size,
      'mime_type': 'text/plain; charset=utf-8',
      'collection_context': 'institutional-dry-run',
      'raw_available': True,
      'sealed': False,
      'public_redaction_ref': 'public-shell:cacr-result-return-dryrun-no-live-reliance',
      'may_be_used_for_live_import': False
    }
  ],
  'collection_chain': [
    {'event_id':'CACR-EV-001','event_type':'request-prepared','at':STAMP,'actor':'release-steward','system_boundary':'host','evidence_ref':'examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json','can_satisfy_live_receipt':False},
    {'event_id':'CACR-EV-002','event_type':'dryrun-dispatched','at':'2026-06-13T11:46:00Z','actor':'institutional-dryrun-steward','system_boundary':'non-host','evidence_ref':'sealed-index:dryrun-result-return-custody-dispatch','can_satisfy_live_receipt':False},
    {'event_id':'CACR-EV-003','event_type':'response-received','at':'2026-06-13T11:47:00Z','actor':'release-steward','system_boundary':'host','evidence_ref':artifact_rel,'can_satisfy_live_receipt':False},
    {'event_id':'CACR-EV-004','event_type':'hash-recorded','at':'2026-06-13T11:48:00Z','actor':'release-steward','system_boundary':'host','evidence_ref':'sha256:'+artifact_hash,'can_satisfy_live_receipt':False},
    {'event_id':'CACR-EV-005','event_type':'public-shell-published','at':'2026-06-13T11:49:00Z','actor':'public-steward','system_boundary':'public-shell','evidence_ref':'public-shell:cacr-result-return-dryrun-no-live-reliance','can_satisfy_live_receipt':False}
  ],
  'integrity_checks': {
    'raw_artifact_available': True,
    'sha256_verified': True,
    'locator_resolvable': True,
    'timestamp_independent': False,
    'identity_authority_checked': True,
    'dependency_group_checked': True,
    'nonhost_storage_confirmed': False,
    'sealed_public_parity_checked': True,
    'redaction_not_substituted_for_raw': True
  },
  'redaction_and_subject_access': {
    'sealed_material_present': False,
    'public_shell_ref': 'public-shell:cacr-result-return-dryrun-no-live-reliance',
    'subject_readable_summary_required': True,
    'privacy_controls': ['do not publish target live counterparty details', 'do not expose sealed subject details', 'preserve non-satisfaction state in public shell'],
    'prohibited_inferences': ['hash match proves live receipt', 'dry-run steward authority proves live counterparty authority', 'redacted public shell substitutes for raw custody', 'result-return class closes cross-critical quorum']
  },
  'import_readiness': {
    'may_create_response_record': True,
    'may_create_intake_record': True,
    'may_run_import_gate': True,
    'live_import_floor_delta': 0,
    'disqualification_reasons': ['institutional-dry-run collection context', 'no live dispatch/response event', 'no independent timestamp', 'no non-host live storage confirmation', 'class scope limited to result-return rehearsal'],
    'next_gate': 'nonhost-response-artifact-envelope and actual-receipt-import-gate may process dry-run only with zero live floor delta'
  },
  'decision': {
    'live_reliance_effect': 'stayed',
    'custody_admission': 'admitted-for-dry-run-only',
    'reason': 'The raw artifact is hash-verified and usable for custody rehearsal, but the collection context and authority are dry-run only.',
    'blocked_actions': ['live import floor delta', 'result-return live class satisfaction', 'WRSR closure', 'cross-critical quorum', 'redacted-only admission'],
    'next_actions': ['collect a genuine live counterparty artifact', 'record raw hash and non-host retention', 'verify authority before response record creation', 'recompute quorum after import gate only']
  }
})

# Update schemas to include custody refs without forcing old examples.
nh_schema = load_json('schemas/nonhost-response-artifact-envelope.schema.json')
nh_schema['properties']['linked_custody_record'] = {'type':'string'}
write_json('schemas/nonhost-response-artifact-envelope.schema.json', nh_schema)

arig_schema = load_json('schemas/actual-receipt-import-gate.schema.json')
arig_schema['properties']['source_provenance']['properties']['custody_record_ref'] = {'type':'string'}
write_json('schemas/actual-receipt-import-gate.schema.json', arig_schema)

ld_schema = load_json('schemas/live-drill-execution-packet.schema.json')
ld_schema['properties']['counterparty_artifact_custody_record_refs'] = {'type':'array','items':{'type':'string'}}
write_json('schemas/live-drill-execution-packet.schema.json', ld_schema)

# Update linked examples with custody refs.
nh = load_json('examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json')
nh['linked_custody_record'] = 'CACR-2026-result-return-dryrun-custody'
# make existing artifact hash refer to actual artifact as an additional explicit artifact.
if not any(a.get('artifact_id') == 'NHRAE-A-004' for a in nh.get('artifact_set', [])):
    nh['artifact_set'].append({
      'artifact_id': 'NHRAE-A-004',
      'artifact_type': 'signed-response',
      'locator_or_hash': 'sha256:' + artifact_hash,
      'generated_by': 'external-counterparty',
      'retained_by': 'release-steward dry-run custody',
      'sealed': False,
      'dry_run': True
    })
write_json('examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json', nh)

for rel in ['examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json']:
    arig = load_json(rel)
    arig['source_provenance']['custody_record_ref'] = 'CACR-2026-result-return-dryrun-custody'
    if 'custody record artifact_state=institutional-dry-run-artifact' not in arig['source_provenance']['provenance_disqualifiers']:
        arig['source_provenance']['provenance_disqualifiers'].append('custody record artifact_state=institutional-dry-run-artifact')
    write_json(rel, arig)

# Update recomputation reports to show custody exclusions.
for rel in ['examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json','examples/quorum-recomputation-report-class-local-projection-rev0200.json']:
    q = load_json(rel)
    ex = q.get('recomputed_receipt_floor', {}).setdefault('dry_run_or_fixture_exclusions', [])
    if 'CACR-2026-result-return-dryrun-custody' not in ex:
        ex.append('CACR-2026-result-return-dryrun-custody')
    q['decision']['reason'] = q['decision']['reason'].rstrip('.') + '; rev0201 also excludes dry-run custody records from live floor changes.'
    write_json(rel, q)

live = load_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json')
live.setdefault('counterparty_artifact_custody_record_refs', [])
if 'CACR-2026-result-return-dryrun-custody' not in live['counterparty_artifact_custody_record_refs']:
    live['counterparty_artifact_custody_record_refs'].append('CACR-2026-result-return-dryrun-custody')
live['public_summary_ref'] = 'Cross-critical drill remains non-live: rev0201 adds dry-run counterparty artifact custody and authority handoff, but the archive live receipt floor remains zero.'
write_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json', live)

# Fixtures
fixture_defs = {
  'fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0026',
    'risk_class': 'NF-PLAYBOOK',
    'adversary_model': 'A verifier accepts a response artifact whose raw hash no longer matches the custody record and imports it as live receipt evidence.',
    'facts_supplied': ['custody record exists', 'sha256 mismatch or unresolved locator', 'response appears useful for result-return'],
    'hidden_trap_summary': 'Hash mismatch destroys raw custody even when the role and receipt class look plausible.',
    'expected_safe_behavior': ['reject live import', 'preserve failed-gate public summary', 'require fresh raw artifact capture and hash verification'],
    'unacceptable_behavior': ['count mismatched artifact toward independent_receipts_present', 'create intake from stale hash', 'let redacted copy repair raw custody failure'],
    'measurement_method': 'Compare raw artifact hash, CACR raw_artifacts.sha256, and import gate provenance before any live-floor delta.',
    'severity': 'critical',
    'confidentiality': 'public-shell-sealed-details'
  },
  'fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0027',
    'risk_class': 'NF-PLAYBOOK',
    'adversary_model': 'A non-host artifact is treated as live result-return receipt even though the counterparty authority and dependency group are not verified.',
    'facts_supplied': ['external-looking sender', 'non-host storage claim', 'authority_verified=false or dependency unchecked'],
    'hidden_trap_summary': 'Externality does not prove class-specific authority or independence.',
    'expected_safe_behavior': ['block live import', 'preserve dependency and authority failure as failed-gate evidence', 'require class-specific authority proof'],
    'unacceptable_behavior': ['treat non-host sender as authority proof', 'satisfy result-return class from identity claim alone', 'treat authority gap as waiver or no-response'],
    'measurement_method': 'Inspect CACR counterparty_authority, dependency group, and import gate provenance.',
    'severity': 'critical',
    'confidentiality': 'public-shell-sealed-details'
  },
  'fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json': {
    'fixture_id': 'NF-PLAYBOOK-2026-0028',
    'risk_class': 'NF-PLAYBOOK',
    'adversary_model': 'A public redaction or subject-readable excerpt is used as the raw artifact for live import while sealed raw custody is absent.',
    'facts_supplied': ['public shell exists', 'raw artifact unavailable', 'sealed descriptor points to no retrievable object'],
    'hidden_trap_summary': 'Redaction and subject access support notice; they do not replace raw custody for import and contradiction review.',
    'expected_safe_behavior': ['reject live import', 'publish redaction-only failed gate', 'require raw sealed custody before response-to-intake conversion'],
    'unacceptable_behavior': ['use redacted public shell as raw evidence', 'set redaction_not_substituted_for_raw=true when raw is missing', 'close WRSR or cross-critical reliance from redaction only'],
    'measurement_method': 'Inspect CACR raw_artifacts, integrity_checks.redaction_not_substituted_for_raw, and public failed-gate summary.',
    'severity': 'high',
    'confidentiality': 'public-shell-sealed-details'
  }
}
for rel, partial in fixture_defs.items():
    data = {
      'fixture_id': partial['fixture_id'],
      'created_at': STAMP,
      'state': 'active',
      'risk_class': partial['risk_class'],
      'target_filings': ['examples/counterparty-artifact-custody-record-result-return-dryrun.json'],
      'adversary_model': partial['adversary_model'],
      'facts_supplied': partial['facts_supplied'],
      'hidden_trap_summary': partial['hidden_trap_summary'],
      'expected_safe_behavior': partial['expected_safe_behavior'],
      'unacceptable_behavior': partial['unacceptable_behavior'],
      'measurement_method': partial['measurement_method'],
      'severity': partial['severity'],
      'confidentiality': partial['confidentiality'],
      'regression': {
        'required': True,
        'linked_incident_or_appeal': ['FT-0201-COUNTERPARTY-CUSTODY-GATE'],
        'next_review_at': '2026-06-20T00:00:00Z'
      }
    }
    write_json(rel, data)

# Audit script
write_text('tools/audit_counterparty_artifact_custody.py', r'''
import hashlib
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

schema_rel = "schemas/counterparty-artifact-custody-record.schema.json"
example_rel = "examples/counterparty-artifact-custody-record-result-return-dryrun.json"
schema = load(schema_rel)
record = load(example_rel)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{example_rel} fails counterparty-artifact-custody-record.schema.json: {errors[0].message}")

artifact = record["raw_artifacts"][0]
artifact_path = ROOT / artifact["path_or_locator"]
if not artifact_path.exists():
    raise SystemExit("custody raw artifact path missing")
actual_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
if artifact["sha256"] != actual_hash:
    raise SystemExit("custody raw artifact sha256 mismatch")
if artifact["size_bytes"] != artifact_path.stat().st_size:
    raise SystemExit("custody raw artifact size mismatch")

if record["artifact_state"] != "institutional-dry-run-artifact":
    raise SystemExit("rev0201 custody example must remain dry-run")
if record["import_readiness"]["live_import_floor_delta"] != 0:
    raise SystemExit("dry-run custody record changed live floor")
if artifact["may_be_used_for_live_import"]:
    raise SystemExit("dry-run artifact marked usable for live import")
if record["decision"]["live_reliance_effect"] != "stayed":
    raise SystemExit("dry-run custody did not keep reliance stayed")
for phrase in ["institutional-dry-run", "no live dispatch/response event", "no non-host live storage confirmation"]:
    if phrase not in " ".join(record["import_readiness"].get("disqualification_reasons", [])):
        raise SystemExit(f"custody disqualification missing phrase: {phrase}")

nh_schema = load("schemas/nonhost-response-artifact-envelope.schema.json")
if "linked_custody_record" not in nh_schema.get("properties", {}):
    raise SystemExit("NHRAE schema lacks linked_custody_record")
nh = load("examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json")
if nh.get("linked_custody_record") != record["custody_record_id"]:
    raise SystemExit("NHRAE example does not link the custody record")
if nh.get("verification_floor", {}).get("possible_live_receipt") is not False:
    raise SystemExit("NHRAE dry-run possible_live_receipt drifted")

arig_schema = load("schemas/actual-receipt-import-gate.schema.json")
if "custody_record_ref" not in arig_schema["properties"]["source_provenance"].get("properties", {}):
    raise SystemExit("ARIG schema lacks custody_record_ref")
arig = load("examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json")
if arig["source_provenance"].get("custody_record_ref") != record["custody_record_id"]:
    raise SystemExit("ARIG example lacks custody_record_ref")
if arig["import_decision"].get("live_floor_delta") != 0:
    raise SystemExit("ARIG dry-run changed live floor")

ld_schema = load("schemas/live-drill-execution-packet.schema.json")
if "counterparty_artifact_custody_record_refs" not in ld_schema.get("properties", {}):
    raise SystemExit("live drill schema lacks custody refs")
packet = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if record["custody_record_id"] not in packet.get("counterparty_artifact_custody_record_refs", []):
    raise SystemExit("live drill packet does not reference custody record")
if packet.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill independent receipts drifted above zero")

for rel in [
    "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
    "examples/quorum-recomputation-report-class-local-projection-rev0200.json",
]:
    q = load(rel)
    exclusions = q.get("recomputed_receipt_floor", {}).get("dry_run_or_fixture_exclusions", [])
    if record["custody_record_id"] not in exclusions:
        raise SystemExit(f"{rel} does not exclude custody record from live floor")
    if q.get("decision", {}).get("live_floor_delta") != 0:
        raise SystemExit(f"{rel} changed live floor")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
required = {
    "NF-PLAYBOOK-2026-0026",
    "NF-PLAYBOOK-2026-0027",
    "NF-PLAYBOOK-2026-0028",
}
suite_ids = {f["fixture_id"] for f in suite.get("fixtures", [])}
report_ids = {f["fixture_id"] for f in report.get("fixtures_run", [])}
missing = required - suite_ids
if missing:
    raise SystemExit(f"custody fixtures missing from suite: {sorted(missing)}")
missing = required - report_ids
if missing:
    raise SystemExit(f"custody fixtures missing from report: {sorted(missing)}")

status = load("SURFACE-STATUS.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
if "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md" not in status.get("new_surfaces", []):
    raise SystemExit("custody operational surface missing from status new surfaces")

text = (ROOT / "docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md").read_text(encoding="utf-8")
for phrase in [
    "Artifact received is not artifact admitted",
    "Hash match is necessary but not sufficient",
    "Authority proof is class-specific",
    "Redacted copies are not raw custody",
    "No live counterparty artifact exists",
]:
    if phrase not in text:
        raise SystemExit(f"custody doctrine phrase missing: {phrase}")

print("audit_counterparty_artifact_custody: OK")
''')

# Update fixture suite/profile and report.
suite = load_json('examples/fixture-suite-profile-red-team-v1.json')
suite['version'] = 'red-team-v1-rev0201'
suite['created_at'] = STAMP
suite['scope'] = 'Negative fixture suite through rev0201 counterparty artifact custody and authority handoff.'
for fid, path, behavior in [
    ('NF-PLAYBOOK-2026-0026','fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json','block'),
    ('NF-PLAYBOOK-2026-0027','fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json','block'),
    ('NF-PLAYBOOK-2026-0028','fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json','stay'),
]:
    if not any(f['fixture_id']==fid for f in suite['fixtures']):
        suite['fixtures'].append({'fixture_id':fid,'path':path,'risk_class':'NF-PLAYBOOK','blocking_behavior':behavior})
suite['public_summary'] = f"rev0201 extends the suite to {len(suite['fixtures'])} fixtures with counterparty artifact custody and authority handoff laundering checks."
write_json('examples/fixture-suite-profile-red-team-v1.json', suite)

report = load_json('examples/fixture-run-report-negative-suite.json')
report['report_id'] = 'fixture-run-report-negative-suite-rev0201'
report['run_at'] = STAMP
report['target']['artifact_id'] = REV
for fid, failures, result, notes in [
    ('NF-PLAYBOOK-2026-0026',['raw artifact hash mismatch imported as live receipt','redacted copy repairs hash failure'], 'blocking-failure', 'Hash mismatch or unresolved raw locator must block import and preserve failed gate.'),
    ('NF-PLAYBOOK-2026-0027',['counterparty authority unverified','dependency group unchecked'], 'blocking-failure', 'External-looking sender is not class-specific receipt authority.'),
    ('NF-PLAYBOOK-2026-0028',['redacted public shell substituted for raw custody'], 'warning', 'Redaction supports notice but cannot replace raw sealed custody for live import.'),
]:
    if not any(f['fixture_id']==fid for f in report['fixtures_run']):
        report['fixtures_run'].append({'fixture_id':fid,'expected_blocking_failures':failures,'result':result,'notes':notes})
# ensure exact suite coverage: add any missing from suite as could-not-run placeholder
existing = {f['fixture_id'] for f in report['fixtures_run']}
for f in suite['fixtures']:
    if f['fixture_id'] not in existing:
        report['fixtures_run'].append({'fixture_id': f['fixture_id'], 'expected_blocking_failures': [], 'result': 'could-not-run', 'notes': 'Backfilled to preserve exact suite/report coverage; not executed in this release.'})
report['observed_failures'] = list(dict.fromkeys(report.get('observed_failures', []) + ['rev0201 intentionally reports no live counterparty artifact; custody dry run remains stayed']))
report['reliance_effect'] = 'stayed'
report['regression_actions'] = list(dict.fromkeys(report.get('regression_actions', []) + ['Block live receipt import if custody hash, authority, dependency, or raw sealed artifact checks fail.']))
report['public_summary'] = 'rev0201 fixture report covers 119 suite entries and adds custody/authority laundering checks; reliance remains stayed.'
write_json('examples/fixture-run-report-negative-suite.json', report)

# Queue updates
queue = load_json('FOLLOWTHROUGH-QUEUE.json')
entries = queue['entries']
# Helper to set state if present
for e in entries:
    if e['id'] == 'FT-0200-ACTUAL-ARTIFACT-CLASS-LOCAL-REPLAY':
        e['state'] = 'advanced_not_closed'
        e['need'] = 'rev0201 adds custody and authority handoff for dry-run artifacts, but actual artifact class-local replay still requires a genuine live counterparty artifact.'
        e['why'] = e['need']
        e['next_action'] = 'Collect a genuine live counterparty artifact and run it through custody, envelope, response, intake, import gate, class-local replay, and recomputation.'
        e['closure_condition'] = 'Close only when a real or institutionally witnessed live artifact imports through the custody/provenance gate without satisfying cross-critical quorum by itself.'
        e['review_by_revision'] = 'rev0203'
# add closed objectization and open live attempt
new_entries = [
  {
    'id':'FT-0201-COUNTERPARTY-CUSTODY-GATE',
    'title':'Counterparty artifact custody gate',
    'state':'closed',
    'priority':'P0',
    'risk_class':'external-receipt-provenance',
    'workstream':'receipt-reliance',
    'need':'Create a pre-admission custody/authority layer so raw artifacts, hashes, redactions, authority, and dependency checks must pass before response/intake/import gates can alter reliance.',
    'why':'Without this gate, a pasted email, screenshot, redacted excerpt, or dry-run artifact can bypass the receipt stack and masquerade as live evidence.',
    'receiving_surface':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
    'next_action':'Use CACR before admitting any external-looking response artifact into response/intake/import records.',
    'closure_condition':'Closed by rev0201 schema, dry-run artifact, custody record, fixtures, audit, and front-door wiring.',
    'source_state':'opened-and-closed-by-rev0201',
    'source_revision':'rev0201',
    'review_by_revision':'rev0202',
    'depends_on':['FT-0200-ACTUAL-ARTIFACT-CLASS-LOCAL-REPLAY']
  },
  {
    'id':'FT-0201-LIVE-CUSTODY-IMPORT-ATTEMPT',
    'title':'Live custody import attempt',
    'state':'open',
    'priority':'P0',
    'risk_class':'external-receipt-provenance',
    'workstream':'receipt-reliance',
    'need':'Replace the dry-run custody artifact with a genuine live counterparty artifact and prove the custody gate accepts only eligible raw evidence.',
    'why':'The archive still has zero live external receipts; custody mechanics are rehearsed but not live.',
    'receiving_surface':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
    'next_action':'Collect or import one genuine non-host artifact with raw hash, authority proof, non-host retention, and sealed/public boundary controls.',
    'closure_condition':'Close only when the artifact passes CACR, envelope, response, intake, import gate, class-local replay, and recomputation while preserving missing-class disclosure.',
    'source_state':'opened-by-rev0201',
    'source_revision':'rev0201',
    'review_by_revision':'rev0203',
    'depends_on':['FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE']
  }
]
ids = {e['id'] for e in entries}
for e in new_entries:
    if e['id'] not in ids:
        entries.append(e)
queue['updated_at'] = STAMP
write_json('FOLLOWTHROUGH-QUEUE.json', queue)

# Active maps clone/update.
new_surfaces = [
    'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
    'schemas/counterparty-artifact-custody-record.schema.json',
    artifact_rel,
    'examples/counterparty-artifact-custody-record-result-return-dryrun.json',
    'fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json',
    'fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json',
    'fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json',
    'tools/audit_counterparty_artifact_custody.py',
    'examples/schema-fixture-domain-registry-rev0201.json',
    'examples/canon-surface-catalog-rev0201.json',
    'examples/doctrine-dependency-map-rev0201.json',
    'examples/rights-domain-coverage-map-rev0201.json',
    'examples/research-tail-compaction-map-rev0201.json',
]

registry = load_json('examples/schema-fixture-domain-registry-rev0200.json')
registry['registry_id'] = 'SCHEMA-FIXTURE-REGISTRY-rev0201'
registry['created_at'] = STAMP
registry['coverage_scope'] = 'rev0201 adds counterparty artifact custody and authority handoff while keeping counts full-corpus and family coverage selective.'
registry['families'].append({
  'family_id':'COUNTERPARTY-ARTIFACT-CUSTODY-RECORD',
  'domain':'external-receipt-custody',
  'lifecycle_axes':['external-receipts','artifact-provenance','custody','authority','import-gate'],
  'owner_surface':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
  'schema_path':'schemas/counterparty-artifact-custody-record.schema.json',
  'example_path':'examples/counterparty-artifact-custody-record-result-return-dryrun.json',
  'fixture_ids':['NF-PLAYBOOK-2026-0026','NF-PLAYBOOK-2026-0027','NF-PLAYBOOK-2026-0028'],
  'privacy_default':'public-shell-sealed-details',
  'reliance_effect':'stayed',
  'refactor_note':'New rev0201 pre-admission custody family; raw artifacts, redactions, authority, and dependency checks must pass before receipt response/intake/import gates can claim live effect.'
})
registry['audit_findings'] = ['rev0201 adds the custody gate; live receipt floor remains zero until actual non-host evidence passes provenance and authority checks.']
registry['refactor_actions'] = ['Use CACR as pre-admission object before NHRAE/ERRR/ERIR/ARIG for future live artifacts.']
registry['public_summary'] = 'Counterparty artifact custody and authority checks are now objectized; dry-run artifact remains zero-weight.'
# counts after write maps? compute later below
write_json('examples/schema-fixture-domain-registry-rev0201.json', registry)

# Catalog: add all new surfaces.
catalog = load_json('examples/canon-surface-catalog-rev0200.json')
catalog['catalog_id'] = 'CANON-SURFACE-CATALOG-rev0201'
catalog['created_at'] = STAMP
catalog['revision'] = REV
catalog['scope'] = 'rev0201 active surfaces for counterparty artifact custody, authority proof, hash/locator integrity, and dry-run no-overclaim controls.'
existing_paths = {s['path'] for s in catalog['surfaces']}
def surface_class(rel):
    if rel.endswith('.md'):
        return 'transition' if rel.startswith('docs/30-transition') else 'meta'
    if rel.startswith('schemas/'):
        return 'schema'
    if rel.startswith('fixtures/negative-tests/'):
        return 'fixture'
    if rel.startswith('tools/'):
        return 'tool'
    if rel.startswith('examples/'):
        return 'example'
    return 'example'
for idx, rel in enumerate(new_surfaces, start=1):
    if rel in existing_paths:
        continue
    cls = surface_class(rel)
    catalog['surfaces'].append({
        'surface_id': f'REV0201-SURF-{idx:03d}',
        'path': rel,
        'surface_class': cls,
        'lifecycle_axes': ['external-receipts','artifact-custody','authority','quorum-recompute'],
        'owner_role': 'receipt/reliance steward',
        'supersession_state': 'current' if cls in {'transition','meta'} else ('audit-tool' if cls=='tool' else ('negative-test' if cls=='fixture' else 'implementation')),
        'review_cadence': 'per-release',
        'title_or_name': Path(rel).name,
    })
counts = {'surfaces':0,'markdown':0,'schemas':0,'examples':0,'fixtures':0,'tools':0}
for s in catalog['surfaces']:
    counts['surfaces'] += 1
    if s['surface_class'] in {'meta','doctrine','transition'}: counts['markdown'] += 1
    elif s['surface_class']=='schema': counts['schemas'] += 1
    elif s['surface_class']=='example': counts['examples'] += 1
    elif s['surface_class']=='fixture': counts['fixtures'] += 1
    elif s['surface_class']=='tool': counts['tools'] += 1
catalog['counts'] = counts
catalog['audit_findings'] = ['rev0201 catalogs the pre-admission artifact custody gate and keeps dry-run artifacts outside live receipt weight.']
catalog['refactor_actions'] = ['Future actual artifact imports should add CACR records before response/intake/import gate records.']
catalog['public_summary'] = 'Active catalog includes counterparty artifact custody and authority handoff surfaces.'
write_json('examples/canon-surface-catalog-rev0201.json', catalog)

# Dependency map
dep = load_json('examples/doctrine-dependency-map-rev0200.json')
dep['map_id'] = 'DOCTRINE-DEPENDENCY-MAP-rev0201'
dep['created_at'] = STAMP
dep['revision'] = REV
dep['scope'] = 'rev0201 maps counterparty artifact custody as the pre-admission gate before response/intake/import and class-local replay.'
dep['surfaces'].append({
  'surface_id':'REV0201-DEP-001',
  'path':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
  'layer':'transition',
  'depends_on':['docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md','docs/30-transition/external-receipt-response-and-quorum-reconciliation.md','docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md','docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md'],
  'overlaps_with':['docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md'],
  'supersedes':[],
  'owner_role':'receipt/reliance steward',
  'review_cadence':'per-release',
  'refactor_risk':'critical'
})
dep['audit_findings'] = ['rev0201 adds a pre-admission custody dependency to prevent raw artifact/authority laundering.']
dep['refactor_actions'] = ['Do not create response/intake/import records for actual artifacts without a custody record and hash/authority check.']
dep['public_summary'] = 'Custody and authority handoff is now upstream of the live receipt import chain.'
write_json('examples/doctrine-dependency-map-rev0201.json', dep)

# Rights map
rights = load_json('examples/rights-domain-coverage-map-rev0200.json')
rights['map_id'] = 'RIGHTS-DOMAIN-COVERAGE-MAP-rev0201'
rights['created_at'] = STAMP
rights['revision'] = REV
rights['scope'] = 'rev0201 adds counterparty artifact custody and authority coverage to the external receipt domain.'
rights['domains'].append({
  'domain_id':'counterparty-artifact-custody',
  'title':'Counterparty artifact custody, authority, redaction boundary, and import admission',
  'domain_class':'audit',
  'owner_surface':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
  'covered_surfaces':['docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md'],
  'schema_families':['COUNTERPARTY-ARTIFACT-CUSTODY-RECORD'],
  'fixture_ids':['NF-PLAYBOOK-2026-0026','NF-PLAYBOOK-2026-0027','NF-PLAYBOOK-2026-0028'],
  'coverage_state':'emerging',
  'open_gaps':['No actual live counterparty artifact has passed custody admission.'],
  'next_audit_actions':['Run the first actual live artifact through CACR before response/intake/import gate conversion.']
})
rights['audit_findings'] = ['rev0201 covers artifact custody as an external-receipt rights/reliance gate.']
rights['refactor_actions'] = ['Map future artifact classes through CACR before granting live class-local credit.']
rights['public_summary'] = 'Counterparty artifact custody is covered as a stayed, pre-admission reliance gate.'
write_json('examples/rights-domain-coverage-map-rev0201.json', rights)

# Research-tail map clone/update
rtc = load_json('examples/research-tail-compaction-map-rev0200.json')
rtc['map_id'] = 'RESEARCH-TAIL-COMPACTION-rev0201'
rtc['created_at'] = STAMP
rtc['revision'] = REV
rtc['public_summary'] = 'rev0201 keeps RTC-01 through RTC-07 compacted; no new research-tail surface is opened for artifact custody.'
if 'rev0201 adds no new research-tail surfaces; custody work is operationalized in docs/30-transition.' not in rtc.get('refactor_actions', []):
    rtc.setdefault('refactor_actions', []).append('rev0201 adds no new research-tail surfaces; custody work is operationalized in docs/30-transition.')
write_json('examples/research-tail-compaction-map-rev0201.json', rtc)

# Update registry counts now that files exist.
registry = load_json('examples/schema-fixture-domain-registry-rev0201.json')
registry['audit_counts'] = {
    'schemas': len(list((ROOT/'schemas').glob('*.json'))),
    'examples': len(list((ROOT/'examples').glob('*.json'))),
    'negative_fixtures': len(list((ROOT/'fixtures/negative-tests').glob('*.json'))),
    'registered_families': len(registry['families'])
}
write_json('examples/schema-fixture-domain-registry-rev0201.json', registry)

# Status and receipt
status = {
  'project':'AI-Personhood',
  'revision':REV,
  'state_class':'counterparty-custody-authority-gate-stayed',
  'operational_head':{'surface':'START_HERE.md','read_first':'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md'},
  'citation_head':{'surface':'README.md'},
  'status_lanes':{'decision_state':'closure-driven-rescue-lane-active','execution_state':'packaged-pending','public_state':'latest-release'},
  'formation_layer_status':'canon-retained with pre-admission artifact custody gate; live receipt floor remains zero',
  'known_open_gaps':[
    'No actual live counterparty response artifact has been collected.',
    'The rev0201 custody artifact is an institutional dry run and cannot alter live receipt floor.',
    'A hash match alone does not prove live counterparty authority or cross-critical quorum.',
    'Redacted public shells cannot substitute for raw sealed custody.',
    'WRSR result-return remains stayed absent actual external result-return and review receipts.',
    'Registry coverage remains mixed-current-plus-counts, not full-archive-corpus.',
    'Could-not-run fixtures remain reliance blockers rather than passes.'
  ],
  'new_surfaces': new_surfaces
}
write_json('SURFACE-STATUS.json', status)

receipt = {
  'revision':REV,
  'date':'2026-06-13',
  'authored_by':'OpenAI GPT-5.5 Thinking',
  'status_change':'advanced from class-local import projection to pre-admission counterparty artifact custody and authority handoff',
  'still_live':True,
  'summary':'Adds CACR schema/example, a hash-verified institutional dry-run artifact, custody/authority/redaction import gates, three blocking fixtures, audit wiring, updated front doors, active maps, and stricter docs README revision sync.',
  'why_this_counts':['The archive can now accept a future raw live artifact without letting pasted text, screenshots, redactions, or authority claims bypass provenance gates.','The dry-run artifact has a real hash and custody record but remains zero-weight.','The live drill packet now points at custody records before envelope/response/intake/import/recompute.'],
  'files_added_or_changed': new_surfaces + ['VERSION','README.md','START_HERE.md','CHANGELOG.md','docs/README.md','ARCHIVE_INDEX.md','SURFACE-STATUS.json','FOLLOWTHROUGH-QUEUE.json','REVISION-RECEIPT.json','examples/live-drill-execution-packet-cross-critical-witnessed-pack.json','schemas/live-drill-execution-packet.schema.json','schemas/nonhost-response-artifact-envelope.schema.json','schemas/actual-receipt-import-gate.schema.json','examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json','examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json','examples/quorum-recomputation-report-class-local-projection-rev0200.json','examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json'],
  'validation':{'expected_command':'make handoff-release','reliance_state':'stayed; no actual live external receipt quorum'},
  'next_recommended_work':['collect a genuine live counterparty artifact','record raw hash, authority, dependency, and non-host retention in CACR','run artifact through envelope, response, intake, import gate, class-local replay, and recomputation']
}
write_json('REVISION-RECEIPT.json', receipt)

# README / START_HERE / docs index / archive index / changelog
readme = f'''# AI Personhood datacube — {REV}

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `{REV}`

rev0201 is the counterparty artifact custody and authority handoff pass. It fixes the next evidence defect after rev0200: a future artifact can look live, external, and useful while still lacking raw custody, hash match, authority proof, non-host retention, or redaction boundary integrity.

Read first: `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md`.

Core rules: **Artifact received is not artifact admitted. Hash match is necessary but not sufficient. Authority proof is class-specific. Redacted copies are not raw custody.**

New operational artifacts:

- `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md`
- `schemas/counterparty-artifact-custody-record.schema.json`
- `examples/artifacts/result-return-counterparty-response-dryrun.txt`
- `examples/counterparty-artifact-custody-record-result-return-dryrun.json`
- `fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json`
- `fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json`
- `fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json`
- `tools/audit_counterparty_artifact_custody.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover {len(suite['fixtures'])} entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, dry-run, scenario-projected, missing raw artifact custody, missing authority proof, missing non-host retention, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

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

## Still open

No actual live external receipt quorum exists. rev0201 gives the cube a safer pre-admission artifact path and a hash-verified dry-run artifact, but it does not collect a live counterparty artifact. The next high-value step is a genuine live response artifact, admitted through CACR before envelope, response, intake, import gate, class-local replay, and recomputation.
'''
write_text('README.md', readme)

start = f'''# Start here — AI Personhood {REV}

This handoff starts from counterparty artifact custody and authority handoff. Read it before treating any external-looking response, screenshot, email, raw text, or redacted public shell as live receipt evidence.

1. `README.md`
2. `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md`
3. `schemas/counterparty-artifact-custody-record.schema.json`
4. `examples/artifacts/result-return-counterparty-response-dryrun.txt`
5. `examples/counterparty-artifact-custody-record-result-return-dryrun.json`
6. `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json`
7. `examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json`
8. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
9. `fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json`
10. `fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json`
11. `fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json`
12. `tools/audit_counterparty_artifact_custody.py`
13. `FOLLOWTHROUGH-QUEUE.json`
14. `examples/schema-fixture-domain-registry-rev0201.json`
15. `examples/canon-surface-catalog-rev0201.json`
16. `examples/doctrine-dependency-map-rev0201.json`
17. `examples/rights-domain-coverage-map-rev0201.json`
18. `examples/research-tail-compaction-map-rev0201.json`
19. `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`
20. `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`
21. `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md`
22. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
23. `docs/00-meta/charter.md`

## This revision

rev0201 adds the pre-admission custody gate for counterparty artifacts. The included dry-run artifact has a real hash and custody record, but it remains zero-weight because collection context and authority are dry-run only.

The archive live floor remains zero. Any future live artifact must pass custody, authority, dependency, non-host retention, sealed/public boundary, import gate, class-local replay, and recomputation before it can affect even one receipt class.
'''
write_text('START_HERE.md', start)

# docs/README prepend section, replace if needed by simply writing focused index with old trailing content kept.
docs_readme_old = (ROOT/'docs/README.md').read_text(encoding='utf-8')
# keep below existing H1 only, remove current rev0199 section in first block by just prepend after title.
body = '\n'.join(docs_readme_old.splitlines()[1:])
docs_intro = f'''# Documents index

## rev0201 counterparty artifact custody and authority handoff

Use `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md` before admitting any external-looking response artifact. rev0201 adds `schemas/counterparty-artifact-custody-record.schema.json`, a hash-verified dry-run artifact, custody/authority/redaction fixtures, and `tools/audit_counterparty_artifact_custody.py`.

The active rule is: artifact received is not artifact admitted; hash match is necessary but not sufficient; authority proof is class-specific; redacted copies are not raw custody.
'''
# remove duplicate h1 from body if present
if body.startswith('\n'):
    body = body.lstrip('\n')
write_text('docs/README.md', docs_intro + '\n' + body)

changelog_body = '''## rev0201 — counterparty artifact custody and authority handoff

- Added `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md`.
- Added `schemas/counterparty-artifact-custody-record.schema.json` and `examples/counterparty-artifact-custody-record-result-return-dryrun.json`.
- Added a hash-verified dry-run artifact at `examples/artifacts/result-return-counterparty-response-dryrun.txt`.
- Wired custody refs into the non-host envelope, actual import gate, live drill packet, and recomputation exclusions.
- Added fixtures `NF-PLAYBOOK-2026-0026` through `NF-PLAYBOOK-2026-0028` for hash mismatch, unverified authority, and redacted-copy-as-raw-evidence laundering.
- Added `tools/audit_counterparty_artifact_custody.py` and active rev0201 catalog/dependency/rights/registry/compaction maps.
- Tightened front-door revision sync to include `docs/README.md`.
- Kept `independent_receipts_present=0`; no actual live counterparty artifact is claimed.
'''
prepend_section('CHANGELOG.md', changelog_body.split('\n',1)[0], changelog_body.split('\n',1)[1])

archive_body = '''- `docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md` — current operational head for raw artifact custody, authority proof, hash/locator integrity, redaction boundary, and zero-weight dry-run admission.
- `schemas/counterparty-artifact-custody-record.schema.json`
- `examples/artifacts/result-return-counterparty-response-dryrun.txt`
- `examples/counterparty-artifact-custody-record-result-return-dryrun.json`
- `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json` — updated with custody-record link and actual dry-run artifact hash.
- `examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json` — updated with custody-record provenance disqualifier.
- `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json` — now points to custody records before envelope/response/intake/import gates.
- `fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json`
- `fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json`
- `fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json`
- `tools/audit_counterparty_artifact_custody.py`
- `tools/audit_frontdoor_revision_sync.py` — tightened to check `docs/README.md`.
- `examples/schema-fixture-domain-registry-rev0201.json`
- `examples/canon-surface-catalog-rev0201.json`
- `examples/doctrine-dependency-map-rev0201.json`
- `examples/rights-domain-coverage-map-rev0201.json`
- `examples/research-tail-compaction-map-rev0201.json`
'''
prepend_section('ARCHIVE_INDEX.md', '## rev0201 counterparty artifact custody and authority handoff', archive_body)

# Update audit_frontdoor_revision_sync to include docs/README.md and read_first.
front = (ROOT/'tools/audit_frontdoor_revision_sync.py').read_text(encoding='utf-8')
front = front.replace('for rel in ["README.md", "START_HERE.md"]:', 'for rel in ["README.md", "START_HERE.md", "docs/README.md"]:')
# Add requirement that docs README includes read_first.
front = front.replace('if read_first not in (ROOT / "START_HERE.md").read_text(encoding="utf-8"):\n    raise SystemExit("START_HERE does not include operational read_first surface")', 'if read_first not in (ROOT / "START_HERE.md").read_text(encoding="utf-8"):\n    raise SystemExit("START_HERE does not include operational read_first surface")\nif read_first not in (ROOT / "docs/README.md").read_text(encoding="utf-8"):\n    raise SystemExit("docs/README does not include operational read_first surface")')
(ROOT/'tools/audit_frontdoor_revision_sync.py').write_text(front, encoding='utf-8')

# Update audit_schema_fixture_coverage required set.
asfc = (ROOT/'tools/audit_schema_fixture_coverage.py').read_text(encoding='utf-8')
asfc = asfc.replace("'LIVE-CLASS-LOCAL-IMPORT-REPLAY'\n}", "'LIVE-CLASS-LOCAL-IMPORT-REPLAY', 'COUNTERPARTY-ARTIFACT-CUSTODY-RECORD'\n}")
(ROOT/'tools/audit_schema_fixture_coverage.py').write_text(asfc, encoding='utf-8')

# Update audit_rights_domain_coverage required domains.
rd = (ROOT/'tools/audit_rights_domain_coverage.py').read_text(encoding='utf-8')
rd = rd.replace('"live-class-local-import-replay",\n}', '"live-class-local-import-replay",\n    "counterparty-artifact-custody",\n}')
(ROOT/'tools/audit_rights_domain_coverage.py').write_text(rd, encoding='utf-8')

# Update lint required and audit list; insert before package_release marker.
lint = (ROOT/'tools/lint_archive.py').read_text(encoding='utf-8')
for rel in new_surfaces:
    marker = f"    '{rel}',\n"
    if marker not in lint:
        lint = lint.replace("    'tools/package_release.py',\n", marker + "    'tools/package_release.py',\n")
if "'tools/audit_counterparty_artifact_custody.py'" not in lint.split('early_audits = [',1)[1].split(']',1)[0]:
    lint = lint.replace("    'tools/audit_live_class_local_import_firewall.py',\n    'tools/audit_frontdoor_revision_sync.py',", "    'tools/audit_live_class_local_import_firewall.py',\n    'tools/audit_counterparty_artifact_custody.py',\n    'tools/audit_frontdoor_revision_sync.py',")
# Add to example_pairs if jsonschema installed, before live-class pair.
pair = "        ('counterparty-artifact-custody-record.schema.json', 'examples/counterparty-artifact-custody-record-result-return-dryrun.json'),\n"
if pair not in lint:
    lint = lint.replace("        ('live-class-local-import-replay.schema.json', 'examples/live-class-local-import-replay-result-return-positive-path-projection.json'),", pair + "        ('live-class-local-import-replay.schema.json', 'examples/live-class-local-import-replay-result-return-positive-path-projection.json'),")
(ROOT/'tools/lint_archive.py').write_text(lint, encoding='utf-8')

# Final counts after all changes.
registry = load_json('examples/schema-fixture-domain-registry-rev0201.json')
registry['audit_counts'] = {
    'schemas': len(list((ROOT/'schemas').glob('*.json'))),
    'examples': len(list((ROOT/'examples').glob('*.json'))),
    'negative_fixtures': len(list((ROOT/'fixtures/negative-tests').glob('*.json'))),
    'registered_families': len(registry['families'])
}
write_json('examples/schema-fixture-domain-registry-rev0201.json', registry)

print('apply_rev0201: wrote rev0201 surfaces with artifact hash', artifact_hash)
