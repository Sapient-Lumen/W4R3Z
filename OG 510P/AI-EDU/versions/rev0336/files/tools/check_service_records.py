import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / 'schemas' / 'ai-service-record.schema.json'
EXAMPLE_DIR = ROOT / 'examples' / 'service-records'
ADAPTER_DIR = ROOT / 'examples' / 'sector-adapters'
PROFILE_DIR = ROOT / 'examples' / 'redaction-profiles'

AA_ORDER = {f'AA{i}': i for i in range(7)}
REQUIRED_TOP = [
    'schema_version', 'record_id', 'service_name', 'status', 'owners', 'use_case', 'data_map',
    'authority', 'memory', 'evidence_claims', 'construct_and_proof',
    'accessibility_and_protected_support', 'security', 'workload', 'decision',
    'publication_and_adapters', 'public_summary'
]
REQUIRED_OWNERS = ['institutional_owner', 'educational_owner', 'technical_owner', 'support_owner', 'record_owner']
REQUIRED_EVIDENCE = [
    'claim_family', 'claim', 'evidence_grade', 'evidence_source', 'population_or_context',
    'does_not_prove', 'expiry_date', 'early_expiry_triggers', 'owner',
    'renewal_or_repilot_trigger', 'public_claim_to_remove_if_weak'
]
REQUIRED_PUBLIC = [
    'what_the_service_does', 'what_it_does_not_do', 'required_or_optional',
    'data_used_high_level', 'ai_output_record_effect', 'human_contact_or_appeal_route',
    'accessibility_and_alternative_path', 'claim_limits', 'last_reviewed'
]
REQUIRED_DECISION = [
    'decision', 'conditions', 'maximum_allowed_authority', 'maximum_allowed_memory',
    'required_human_coverage', 'required_proof_or_audit', 'stop_triggers',
    'learner_safe_continuity_plan', 'next_review_date', 'public_summary_allowed'
]

REQUIRED_PUBLICATION = [
    'source_record_status', 'source_record_confidence', 'sector_adapter_ids',
    'public_summary_redaction_profiles', 'default_public_summary_redaction_profile',
    'normalization_notes', 'real_record_import_status'
]
SOURCE_STATUS = {
    'realistic_example', 'synthetic_backtest', 'template_only', 'operator_drafted',
    'real_pilot_imported', 'real_pilot_pending'
}
SOURCE_CONFIDENCE = {
    'example_only', 'operator_drafted', 'record_owner_verified',
    'learner_facing_confirmed', 'mixed_or_conflicting'
}
IMPORT_STATUS = {
    'not_applicable_example', 'ready_for_real_import', 'imported_and_verified',
    'imported_needs_review', 'blocked'
}
CLAIM_FAMILIES = {
    'CL-LEARN', 'CL-TASK', 'CL-ACCESS', 'CL-WORKLOAD', 'CL-VALIDITY',
    'CL-SAFETY', 'CL-SECURITY', 'CL-CONTEST', 'CL-COMPLIANCE'
}
EV_GRADES = {f'EV{i}' for i in range(8)}
CE_CODES = {f'CE{i}' for i in range(6)}
M_CODES = {f'M{i}' for i in range(4)}
SEC_CODES = {'SEC0', 'SEC1', 'SEC2', 'SEC3', 'SECX'}
HIGH_STAKES = {
    'gateway_exam', 'professional_gate', 'discipline', 'eligibility', 'public_benefit',
    'accessibility', 'official_record', 'course_credit'
}
PUBLIC_FORBIDDEN = [
    'diagnosis detail', 'disability detail', 'protected fact', 'security exploit',
    'private accommodation', 'learner trace'
]


def fail(errors, path, msg):
    errors.append(f'{path}: {msg}')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0 and all(nonempty(v) for v in value)
    return value is not None


def parse_date(value, errors, path, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, path, f'{field} must be an ISO date: {value!r}')


def require_fields(obj, fields, errors, path, prefix):
    for field in fields:
        if field not in obj or not nonempty(obj[field]):
            fail(errors, path, f'missing or empty {prefix}{field}')


def validate_record(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    record = json.loads(path.read_text(encoding='utf-8'))

    require_fields(record, REQUIRED_TOP, errors, rel, '')
    if errors:
        return errors

    if record.get('schema_version') != '1.1':
        fail(errors, rel, 'schema_version must be 1.1')

    require_fields(record['owners'], REQUIRED_OWNERS, errors, rel, 'owners.')
    require_fields(record['decision'], REQUIRED_DECISION, errors, rel, 'decision.')
    require_fields(record['publication_and_adapters'], REQUIRED_PUBLICATION, errors, rel, 'publication_and_adapters.')
    require_fields(record['public_summary'], REQUIRED_PUBLIC, errors, rel, 'public_summary.')

    adapter_ids = set()
    if ADAPTER_DIR.exists():
        adapter_ids = {json.loads(path.read_text(encoding='utf-8')).get('adapter_id') for path in ADAPTER_DIR.glob('*.json')}
    profile_ids = set()
    if PROFILE_DIR.exists():
        profile_ids = {json.loads(path.read_text(encoding='utf-8')).get('profile_id') for path in PROFILE_DIR.glob('*.json')}
    publication = record['publication_and_adapters']
    if publication.get('source_record_status') not in SOURCE_STATUS:
        fail(errors, rel, 'publication_and_adapters.source_record_status invalid')
    if publication.get('source_record_confidence') not in SOURCE_CONFIDENCE:
        fail(errors, rel, 'publication_and_adapters.source_record_confidence invalid')
    if publication.get('real_record_import_status') not in IMPORT_STATUS:
        fail(errors, rel, 'publication_and_adapters.real_record_import_status invalid')
    bad_adapters = sorted(set(publication.get('sector_adapter_ids', [])) - adapter_ids)
    if bad_adapters:
        fail(errors, rel, 'undefined sector adapters: ' + ', '.join(bad_adapters))
    bad_profiles = sorted(set(publication.get('public_summary_redaction_profiles', [])) - profile_ids)
    default_profile = publication.get('default_public_summary_redaction_profile')
    if default_profile and default_profile not in profile_ids:
        bad_profiles.append(default_profile)
    if bad_profiles:
        fail(errors, rel, 'undefined public-summary redaction profiles: ' + ', '.join(sorted(set(bad_profiles))))
    if default_profile and default_profile not in publication.get('public_summary_redaction_profiles', []):
        fail(errors, rel, 'publication_and_adapters.default_public_summary_redaction_profile must be listed in public_summary_redaction_profiles')
    if publication.get('source_record_status') == 'realistic_example' and publication.get('source_record_confidence') != 'example_only':
        fail(errors, rel, 'realistic examples must use source_record_confidence=example_only')


    authority = record['authority']
    max_aa = authority.get('max_action_authority')
    decision_aa = record['decision'].get('maximum_allowed_authority')
    for field, code in [('authority.max_action_authority', max_aa), ('decision.maximum_allowed_authority', decision_aa)]:
        if code not in AA_ORDER:
            fail(errors, rel, f'{field} must be AA0-AA6')
    if max_aa in AA_ORDER and decision_aa in AA_ORDER and AA_ORDER[decision_aa] < AA_ORDER[max_aa]:
        fail(errors, rel, 'decision.maximum_allowed_authority is below authority.max_action_authority')

    if record['memory'].get('max_memory_class') not in M_CODES:
        fail(errors, rel, 'memory.max_memory_class must be M0-M3')
    if record['construct_and_proof'].get('cognitive_effort_budget') not in CE_CODES:
        fail(errors, rel, 'construct_and_proof.cognitive_effort_budget must be CE0-CE5')
    if record['security'].get('sec_level') not in SEC_CODES:
        fail(errors, rel, 'security.sec_level must be SEC0/SEC1/SEC2/SEC3/SECX')

    parse_date(record['security'].get('red_team_or_abuse_test_date', ''), errors, rel, 'security.red_team_or_abuse_test_date')
    parse_date(record['decision'].get('next_review_date', ''), errors, rel, 'decision.next_review_date')
    parse_date(record['public_summary'].get('last_reviewed', ''), errors, rel, 'public_summary.last_reviewed')

    evidence = record.get('evidence_claims', [])
    if not isinstance(evidence, list) or not evidence:
        fail(errors, rel, 'evidence_claims must be a non-empty list')
    for idx, claim in enumerate(evidence):
        require_fields(claim, REQUIRED_EVIDENCE, errors, rel, f'evidence_claims[{idx}].')
        if claim.get('claim_family') not in CLAIM_FAMILIES:
            fail(errors, rel, f'evidence_claims[{idx}].claim_family invalid')
        if claim.get('evidence_grade') not in EV_GRADES:
            fail(errors, rel, f'evidence_claims[{idx}].evidence_grade invalid')
        parse_date(claim.get('expiry_date', ''), errors, rel, f'evidence_claims[{idx}].expiry_date')
        if claim.get('claim_family') in {'CL-LEARN', 'CL-ACCESS', 'CL-WORKLOAD', 'CL-VALIDITY'}:
            if claim.get('evidence_grade') in {'EV0', 'EV1'} and 'remove' not in claim.get('public_claim_to_remove_if_weak', '').lower():
                # Soft rule: weak core claims must name a public phrase to remove, not just a vague concern.
                if len(claim.get('public_claim_to_remove_if_weak', '')) < 8:
                    fail(errors, rel, f'evidence_claims[{idx}] weak claim lacks removable public phrase')

    # High-risk records need human owner, contestability, and fallback.
    stakes = set(record['use_case'].get('highest_stakes_touched', []))
    record_effect = ' '.join([
        authority.get('record_bearing_effects', ''),
        record['public_summary'].get('ai_output_record_effect', ''),
    ]).lower()
    high_stakes = bool(stakes & HIGH_STAKES) or any(k in record_effect for k in ['record', 'grade', 'credit', 'aid', 'eligibility', 'standing'])
    if high_stakes:
        if not nonempty(record['owners'].get('record_owner')):
            fail(errors, rel, 'high-stakes record requires owners.record_owner')
        if not nonempty(record['construct_and_proof'].get('contest_or_reconsideration_route')):
            fail(errors, rel, 'high-stakes record requires contest_or_reconsideration_route')
        if not nonempty(record['decision'].get('learner_safe_continuity_plan')):
            fail(errors, rel, 'high-stakes record requires learner_safe_continuity_plan')

    # AA3+ requires rollback, abuse testing, and incident reconstruction.
    if max_aa in AA_ORDER and AA_ORDER[max_aa] >= 3:
        for field in [
            ('authority.rollback_route', authority.get('rollback_route')),
            ('security.red_team_or_abuse_test_date', record['security'].get('red_team_or_abuse_test_date')),
            ('security.incident_reconstruction_without_surveillance', record['security'].get('incident_reconstruction_without_surveillance')),
        ]:
            if not nonempty(field[1]):
                fail(errors, rel, f'AA3+ record requires {field[0]}')

    # Protected support requires owner and non-misuse boundary.
    support = record['accessibility_and_protected_support']
    if record['memory'].get('max_memory_class') == 'M3' or 'accessibility' in stakes:
        if not nonempty(support.get('protected_route_owner')):
            fail(errors, rel, 'protected support requires protected_route_owner')
        if not nonempty(support.get('non_misuse_boundary')):
            fail(errors, rel, 'protected support requires non_misuse_boundary')

    if record['decision'].get('public_summary_allowed'):
        if not record['publication_and_adapters'].get('public_summary_redaction_profiles'):
            fail(errors, rel, 'public_summary_allowed requires public_summary_redaction_profiles')
        public_text = json.dumps(record['public_summary']).lower()
        for phrase in PUBLIC_FORBIDDEN:
            if phrase in public_text:
                fail(errors, rel, f'public summary contains forbidden protected/security phrase: {phrase}')

    if not record['decision'].get('stop_triggers'):
        fail(errors, rel, 'decision.stop_triggers must not be empty')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU AI service record':
    raise SystemExit('schema title mismatch')

paths = sorted(EXAMPLE_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no example service records found')

all_errors = []
for path in paths:
    all_errors.extend(validate_record(path))

if all_errors:
    raise SystemExit('service record validation errors:\n' + '\n'.join(all_errors))

print(f'check_service_records: OK ({len(paths)} example records)')
