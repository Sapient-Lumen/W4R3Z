import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / 'examples' / 'redaction-profiles'
SERVICE_DIR = ROOT / 'examples' / 'service-records'

PUBLIC_FIELDS = {
    'what_the_service_does', 'what_it_does_not_do', 'required_or_optional',
    'data_used_high_level', 'ai_output_record_effect', 'human_contact_or_appeal_route',
    'accessibility_and_alternative_path', 'claim_limits', 'last_reviewed'
}
REQUIRED = [
    'profile_id', 'audience', 'publication_band', 'allowed_public_summary_fields',
    'suppressed_detail_categories', 'mandatory_messages', 'forbidden_phrases',
    'protected_support_phrase', 'security_detail_phrase', 'requires_human_contact',
    'freshness_required'
]
BANDS = {'PUB0', 'PUB1', 'PUB2', 'PUB3', 'PUB4', 'PUBX'}
FRESHNESS = {'review_date', 'evidence_fresh_or_claim_removed', 'not_public'}
MUST_SUPPRESS = {'protected', 'security', 'learner'}


def fail(errors, path, msg):
    errors.append(f'{path}: {msg}')


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

profile_paths = sorted(PROFILE_DIR.glob('*.json'))
if not profile_paths:
    raise SystemExit('no redaction profiles found')

errors = []
profiles = {}
for path in profile_paths:
    rel = path.relative_to(ROOT).as_posix()
    profile = load_json(path)
    for field in REQUIRED:
        if field not in profile or profile[field] in ('', [], None):
            fail(errors, rel, f'missing or empty {field}')
    pid = profile.get('profile_id', '')
    if not pid.startswith('RDP-'):
        fail(errors, rel, 'profile_id must start with RDP-')
    if pid in profiles:
        fail(errors, rel, f'duplicate profile_id {pid}')
    profiles[pid] = profile
    if profile.get('publication_band') not in BANDS:
        fail(errors, rel, 'publication_band must be PUB0/PUB1/PUB2/PUB3/PUB4/PUBX')
    if profile.get('freshness_required') not in FRESHNESS:
        fail(errors, rel, 'freshness_required invalid')
    fields = set(profile.get('allowed_public_summary_fields', []))
    if not fields <= PUBLIC_FIELDS:
        fail(errors, rel, 'allowed_public_summary_fields contains fields not in service public_summary')
    suppressed = ' '.join(profile.get('suppressed_detail_categories', [])).lower()
    missing_suppression = [term for term in MUST_SUPPRESS if term not in suppressed]
    if missing_suppression:
        fail(errors, rel, 'suppressed_detail_categories should cover: ' + ', '.join(missing_suppression))
    if profile.get('requires_human_contact') is not True:
        fail(errors, rel, 'requires_human_contact must be true for shipped profiles')
    forbidden = ' '.join(profile.get('forbidden_phrases', [])).lower()
    for term in ['protected', 'security', 'learner']:
        if term not in forbidden:
            fail(errors, rel, f'forbidden_phrases should include a {term}-related phrase')

# Public service records must reference existing profiles and a default profile.
for path in sorted(SERVICE_DIR.glob('*.json')):
    rel = path.relative_to(ROOT).as_posix()
    record = load_json(path)
    overlay = record.get('publication_and_adapters', {})
    referenced = overlay.get('public_summary_redaction_profiles', [])
    default = overlay.get('default_public_summary_redaction_profile')
    if record.get('decision', {}).get('public_summary_allowed'):
        if not referenced:
            fail(errors, rel, 'public_summary_allowed requires public_summary_redaction_profiles')
        if not default:
            fail(errors, rel, 'public_summary_allowed requires default_public_summary_redaction_profile')
    bad = sorted(set(referenced + ([default] if default else [])) - set(profiles))
    if bad:
        fail(errors, rel, 'undefined redaction profiles: ' + ', '.join(bad))
    if default and default not in referenced:
        fail(errors, rel, 'default redaction profile must also appear in public_summary_redaction_profiles')
    public_text = json.dumps(record.get('public_summary', {}), ensure_ascii=False).lower()
    for pid in referenced:
        for phrase in profiles.get(pid, {}).get('forbidden_phrases', []):
            if phrase.lower() in public_text:
                fail(errors, rel, f'public summary contains forbidden phrase for {pid}: {phrase}')

if errors:
    raise SystemExit('redaction profile validation errors:\n' + '\n'.join(errors))

print(f'check_redaction_profiles: OK ({len(profiles)} profiles)')
