import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READY_DIR = ROOT / 'examples' / 'import-readiness'
SERVICE_DIR = ROOT / 'examples' / 'service-records'
MAP_DIR = ROOT / 'examples' / 'import-maps'
QUEUE_PATH = ROOT / 'FOLLOWTHROUGH_QUEUE.json'

REQUIRED = [
    'manifest_id', 'title', 'related_followthrough', 'readiness_state', 'source_truth_class',
    'closure_permitted', 'candidate_service_record_ids', 'import_map_ids',
    'source_inventory_required', 'required_before_real_import', 'protected_exclusions',
    'decision_delta_requirements', 'stop_conditions', 'last_reviewed'
]
READINESS = {'IR0', 'IR1', 'IR2', 'IR3', 'IR4', 'IR5', 'IR6', 'IRX'}
SOURCE_CLASSES = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX'}
CLOSURE_SOURCE_CLASSES = {'SRC2', 'SRC3', 'SRC4'}
CLOSURE_STATES = {'IR4', 'IR5', 'IR6'}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def fail(errors, path, message):
    errors.append(f'{path}: {message}')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(nonempty(item) for item in value)
    return value is not None


def parse_iso(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date: {value!r}')


paths = sorted(READY_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no import-readiness manifests found')

records = {}
for path in sorted(SERVICE_DIR.glob('*.json')):
    data = load_json(path)
    records[data.get('record_id')] = path.relative_to(ROOT).as_posix()

maps = {}
for path in sorted(MAP_DIR.glob('*.json')):
    data = load_json(path)
    maps[data.get('map_id')] = path.relative_to(ROOT).as_posix()

queue = load_json(QUEUE_PATH)['items']
queue_state = {item['id']: item.get('state') for item in queue}

errors = []
ids = set()
closure_manifests = []
for path in paths:
    rel = path.relative_to(ROOT).as_posix()
    data = load_json(path)
    for field in REQUIRED:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    mid = data.get('manifest_id', '')
    if not mid.startswith('IMP-READY-'):
        fail(errors, rel, 'manifest_id must start with IMP-READY-')
    if mid in ids:
        fail(errors, rel, f'duplicate manifest_id {mid}')
    ids.add(mid)

    ft = data.get('related_followthrough')
    if ft not in queue_state:
        fail(errors, rel, f'related_followthrough {ft!r} not in FOLLOWTHROUGH_QUEUE')
    if data.get('readiness_state') not in READINESS:
        fail(errors, rel, 'readiness_state must be IR0/IR1/IR2/IR3/IR4/IR5/IR6/IRX')
    if data.get('source_truth_class') not in SOURCE_CLASSES:
        fail(errors, rel, 'source_truth_class must be SRC0/SRC1/SRC2/SRC3/SRC4/SRCX')
    parse_iso(data.get('last_reviewed', ''), errors, rel, 'last_reviewed')

    missing_records = sorted(set(data.get('candidate_service_record_ids', [])) - set(records))
    if missing_records:
        fail(errors, rel, 'unknown candidate_service_record_ids: ' + ', '.join(missing_records))
    missing_maps = sorted(set(data.get('import_map_ids', [])) - set(maps))
    if missing_maps:
        fail(errors, rel, 'unknown import_map_ids: ' + ', '.join(missing_maps))

    protected = ' '.join(data.get('protected_exclusions', [])).lower()
    for term in ['raw learner', 'diagnosis', 'security exploit', 'vendor marketing']:
        if term not in protected:
            fail(errors, rel, 'protected_exclusions should include ' + term)
    deltas = ' '.join(data.get('decision_delta_requirements', [])).lower()
    for term in ['action authority', 'evidence', 'trim', 'ft-0181']:
        if term not in deltas:
            fail(errors, rel, 'decision_delta_requirements should include ' + term)
    stops = ' '.join(data.get('stop_conditions', [])).lower()
    for term in ['protected', 'authority', 'evidence', 'source']:
        if term not in stops:
            fail(errors, rel, 'stop_conditions should include ' + term)

    if data.get('closure_permitted'):
        closure_manifests.append(mid)
        if data.get('source_truth_class') not in CLOSURE_SOURCE_CLASSES:
            fail(errors, rel, 'closure_permitted requires SRC2/SRC3/SRC4')
        if data.get('readiness_state') not in CLOSURE_STATES:
            fail(errors, rel, 'closure_permitted requires IR4/IR5/IR6')
    else:
        if data.get('source_truth_class') in CLOSURE_SOURCE_CLASSES and data.get('readiness_state') in CLOSURE_STATES:
            # Allowed, but should say why closure is still not permitted.
            stops_text = ' '.join(data.get('stop_conditions', [])).lower()
            if 'decision' not in stops_text and 'redaction' not in stops_text and 'owner' not in stops_text:
                fail(errors, rel, 'SRC2+ readiness without closure should name decision/redaction/owner blocker')

if queue_state.get('FT-0181') == 'done' and not closure_manifests:
    fail(errors, 'FOLLOWTHROUGH_QUEUE.json', 'FT-0181 is done but no import-readiness manifest permits closure')
if queue_state.get('FT-0181') == 'queued' and closure_manifests:
    fail(errors, 'FOLLOWTHROUGH_QUEUE.json', 'FT-0181 is queued but an import-readiness manifest permits closure')

if errors:
    raise SystemExit('import-readiness validation errors:\n' + '\n'.join(errors))

print(f'check_import_readiness: OK ({len(paths)} manifests, {len(closure_manifests)} closure-ready)')
