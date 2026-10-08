import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICT_DIR = ROOT / 'examples' / 'import-dictionaries'
SCHEMA_PATH = ROOT / 'schemas' / 'pilot-source-data-dictionary.schema.json'

STATES = {'DDICT0', 'DDICT1', 'DDICT2', 'DDICT3', 'DDICT4', 'DDICTX'}
SRC_CLASSES = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX'}
ACTIONS = {'map', 'abstract', 'keep_local', 'quarantine', 'ignore'}
SENSITIVITY = {'public', 'internal', 'protected', 'security', 'unknown'}
OWNER_ROLES = {'record_owner', 'support_owner', 'security_owner', 'assessment_owner', 'service_owner', 'none'}


def fail(errors, path, msg):
    errors.append(f'{path}: {msg}')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    return value is not None


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'dictionary_id', 'title', 'source_system', 'source_owner', 'source_truth_class',
        'dictionary_state', 'target_schema_version', 'field_entries', 'owner_review',
        'stop_conditions', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['dictionary_id'].startswith('DDICT-'):
        fail(errors, rel, 'dictionary_id must start DDICT-')
    if data['source_truth_class'] not in SRC_CLASSES:
        fail(errors, rel, 'source_truth_class invalid')
    if data['dictionary_state'] not in STATES:
        fail(errors, rel, 'dictionary_state invalid')
    if data['target_schema_version'] != '1.1':
        fail(errors, rel, 'target_schema_version must be 1.1')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    review = data.get('owner_review', {})
    for field in ['reviewed_by_role', 'review_status', 'review_notes']:
        if field not in review or not nonempty(review[field]):
            fail(errors, rel, f'owner_review.{field} missing')
    if review.get('review_status') not in {'template_only', 'owner_review_needed', 'owner_reviewed', 'blocked'}:
        fail(errors, rel, 'owner_review.review_status invalid')

    entries = data.get('field_entries', [])
    if not isinstance(entries, list) or not entries:
        fail(errors, rel, 'field_entries must be non-empty list')
        return errors

    has_protected_exclusion = False
    has_security_exclusion = False
    has_mapping = False
    for idx, entry in enumerate(entries):
        prefix = f'field_entries[{idx}]'
        for field in ['source_field', 'meaning', 'sensitivity', 'import_action', 'target_field', 'decision_relevance', 'owner_review_required', 'notes']:
            if field not in entry:
                fail(errors, rel, f'{prefix}.{field} missing')
        sensitivity = entry.get('sensitivity')
        action = entry.get('import_action')
        if sensitivity not in SENSITIVITY:
            fail(errors, rel, f'{prefix}.sensitivity invalid')
        if action not in ACTIONS:
            fail(errors, rel, f'{prefix}.import_action invalid')
        if entry.get('owner_review_required') not in OWNER_ROLES:
            fail(errors, rel, f'{prefix}.owner_review_required invalid')
        if action in {'map', 'abstract'} and not entry.get('target_field', '').strip():
            fail(errors, rel, f'{prefix}.target_field required for map/abstract')
        if action == 'map':
            has_mapping = True
        if sensitivity == 'protected' and action in {'quarantine', 'keep_local', 'abstract'}:
            has_protected_exclusion = True
        if sensitivity == 'security' and action in {'quarantine', 'keep_local', 'abstract'}:
            has_security_exclusion = True
        if sensitivity in {'protected', 'security'} and action == 'map':
            fail(errors, rel, f'{prefix} protected/security fields may not map directly')
        if sensitivity == 'unknown' and action in {'map', 'abstract'}:
            fail(errors, rel, f'{prefix} unknown fields may not map or abstract')

    if not has_mapping:
        fail(errors, rel, 'dictionary must include at least one mapped field')
    if not has_protected_exclusion:
        fail(errors, rel, 'dictionary must include at least one protected exclusion or local handling example')
    if not has_security_exclusion:
        fail(errors, rel, 'dictionary must include at least one security exclusion or local handling example')
    if not data.get('stop_conditions'):
        fail(errors, rel, 'stop_conditions must not be empty')

    if data['source_truth_class'] in {'SRC2', 'SRC3', 'SRC4'} and review.get('review_status') != 'owner_reviewed':
        fail(errors, rel, 'SRC2+ dictionaries require owner_review.review_status=owner_reviewed')
    if data['dictionary_state'] in {'DDICT2', 'DDICT3'} and data['source_truth_class'] == 'SRC0':
        fail(errors, rel, 'SRC0 dictionary cannot claim DDICT2/DDICT3')

    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU pilot source data dictionary':
    raise SystemExit('pilot source data dictionary schema title mismatch')

paths = sorted(DICT_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no import data dictionaries found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))
if all_errors:
    raise SystemExit('import data dictionary validation errors:\n' + '\n'.join(all_errors))
print(f'check_import_data_dictionaries: OK ({len(paths)} dictionaries)')
