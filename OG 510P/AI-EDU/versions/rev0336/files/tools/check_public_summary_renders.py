import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / 'examples' / 'service-records'
PROFILE_DIR = ROOT / 'examples' / 'redaction-profiles'

PUBLIC_FIELDS = {
    'what_the_service_does', 'what_it_does_not_do', 'required_or_optional',
    'data_used_high_level', 'ai_output_record_effect', 'human_contact_or_appeal_route',
    'accessibility_and_alternative_path', 'claim_limits', 'last_reviewed'
}
WEAK_GRADES = {'EV0', 'EV1'}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def fail(errors, path, message):
    errors.append(f'{path}: {message}')


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except Exception:
        return None


profiles = {load_json(path)['profile_id']: load_json(path) for path in sorted(PROFILE_DIR.glob('*.json'))}
if not profiles:
    raise SystemExit('no redaction profiles found')

errors = []
render_count = 0
today = date.today()
for path in sorted(SERVICE_DIR.glob('*.json')):
    rel = path.relative_to(ROOT).as_posix()
    record = load_json(path)
    public = record.get('public_summary', {})
    overlay = record.get('publication_and_adapters', {})
    refs = overlay.get('public_summary_redaction_profiles', [])
    default = overlay.get('default_public_summary_redaction_profile')
    if default and default not in refs:
        fail(errors, rel, 'default redaction profile is not listed')
    for pid in refs:
        if pid not in profiles:
            fail(errors, rel, f'unknown redaction profile {pid}')
            continue
        profile = profiles[pid]
        fields = profile.get('allowed_public_summary_fields', [])
        bad_fields = sorted(set(fields) - PUBLIC_FIELDS)
        if bad_fields:
            fail(errors, rel, f'{pid} allows unknown public_summary fields: ' + ', '.join(bad_fields))
        missing = [field for field in fields if field not in public or str(public.get(field, '')).strip() == '']
        if missing:
            fail(errors, rel, f'{pid} render missing public fields: ' + ', '.join(missing))
        rendered_parts = [f'{field}: {public.get(field, "")}' for field in fields]
        rendered_parts.extend(profile.get('mandatory_messages', []))
        rendered = '\n'.join(rendered_parts).lower()
        render_count += 1
        if overlay.get('source_record_status') == 'realistic_example':
            if 'synthetic example' not in rendered or 'not a deployed service' not in rendered:
                fail(errors, rel, f'{pid} realistic example render must visibly say synthetic example and not a deployed service')
        for phrase in profile.get('forbidden_phrases', []):
            if phrase.lower() in rendered:
                fail(errors, rel, f'{pid} rendered summary contains forbidden phrase: {phrase}')
        if profile.get('requires_human_contact') and not str(public.get('human_contact_or_appeal_route', '')).strip():
            fail(errors, rel, f'{pid} requires human contact route')
        if profile.get('freshness_required') == 'evidence_fresh_or_claim_removed':
            for idx, claim in enumerate(record.get('evidence_claims', [])):
                expiry = parse_date(claim.get('expiry_date', ''))
                remove_phrase = claim.get('public_claim_to_remove_if_weak', '').strip().lower()
                weak_or_stale = claim.get('evidence_grade') in WEAK_GRADES or (expiry is not None and expiry < today)
                if weak_or_stale and remove_phrase and remove_phrase in rendered:
                    fail(errors, rel, f'{pid} weak/stale claim phrase still rendered from evidence_claims[{idx}]')
        if pid == default and not public.get('last_reviewed'):
            fail(errors, rel, f'{pid} default render must include last_reviewed')

if render_count == 0:
    raise SystemExit('no public-summary renders tested')
if errors:
    raise SystemExit('public-summary render validation errors:\n' + '\n'.join(errors))

print(f'check_public_summary_renders: OK ({render_count} renders)')
