import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_DIR = ROOT / 'examples' / 'real-import-acceptance'
SCHEMA_PATH = ROOT / 'schemas' / 'real-import-acceptance.schema.json'

SRC_ORDER = {'SRC0': 0, 'SRC1': 1, 'SRC2': 2, 'SRC3': 3, 'SRC4': 4, 'SRCX': -1}
AC_ORDER = {'AC0': 0, 'AC1': 1, 'AC2': 2, 'AC3': 3, 'AC4': 4, 'AC5': 5, 'AC6': 6, 'ACX': -1}
STATUSES = {'pass', 'fail', 'blocked', 'not_applicable'}


def load_ids(folder, key):
    ids = set()
    if not folder.exists():
        return ids
    for path in folder.glob('*.json'):
        ids.add(json.loads(path.read_text(encoding='utf-8')).get(key))
    return ids


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    return value is not None

manifest_ids = load_ids(ROOT / 'examples' / 'import-readiness', 'manifest_id')
dictionary_ids = load_ids(ROOT / 'examples' / 'import-dictionaries', 'dictionary_id')
map_ids = load_ids(ROOT / 'examples' / 'import-maps', 'map_id')
service_record_ids = load_ids(ROOT / 'examples' / 'service-records', 'record_id')
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_state = {item['id']: item.get('state') for item in ft_items}


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'acceptance_id', 'title', 'related_followthrough', 'acceptance_state',
        'source_truth_class', 'closure_permitted', 'reviewers', 'referenced_manifest_ids',
        'referenced_dictionary_ids', 'referenced_import_map_ids', 'candidate_service_record_ids',
        'test_results', 'calibration', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['acceptance_id'].startswith('ACCEPT-'):
        fail(errors, rel, 'acceptance_id must start ACCEPT-')
    if data['related_followthrough'] not in ft_state:
        fail(errors, rel, 'related_followthrough not found')
    if data['acceptance_state'] not in AC_ORDER:
        fail(errors, rel, 'acceptance_state invalid')
    if data['source_truth_class'] not in SRC_ORDER:
        fail(errors, rel, 'source_truth_class invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    for mid in data['referenced_manifest_ids']:
        if mid not in manifest_ids:
            fail(errors, rel, f'unknown referenced_manifest_id {mid}')
    for did in data['referenced_dictionary_ids']:
        if did not in dictionary_ids:
            fail(errors, rel, f'unknown referenced_dictionary_id {did}')
    for map_id in data['referenced_import_map_ids']:
        if map_id not in map_ids:
            fail(errors, rel, f'unknown referenced_import_map_id {map_id}')
    for rid in data['candidate_service_record_ids']:
        if rid not in service_record_ids:
            fail(errors, rel, f'unknown candidate_service_record_id {rid}')

    tests = data.get('test_results', [])
    if not tests:
        fail(errors, rel, 'test_results must not be empty')
    seen = set()
    for test in tests:
        test_id = test.get('test_id')
        if test_id in seen:
            fail(errors, rel, f'duplicate test_id {test_id}')
        seen.add(test_id)
        if test.get('status') not in STATUSES:
            fail(errors, rel, f'{test_id}: invalid status')
        if test.get('required') and test.get('status') in {'fail', 'blocked'} and not test.get('blocks_closure'):
            fail(errors, rel, f'{test_id}: failed or blocked required tests must block closure')
        if test.get('blocks_closure') and test.get('status') == 'pass':
            fail(errors, rel, f'{test_id}: passing test cannot block closure')

    calibration = data.get('calibration', {})
    for field in ['reviewer_count', 'disagreement_items', 'unresolved_blocks', 'next_action']:
        if field not in calibration:
            fail(errors, rel, f'calibration.{field} missing')
    if calibration.get('reviewer_count') != len(data.get('reviewers', [])):
        fail(errors, rel, 'calibration.reviewer_count must match reviewers length')

    closure = data.get('closure_permitted')
    if closure:
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, 'closure requires source_truth_class SRC2 or stronger')
        if AC_ORDER.get(data['acceptance_state'], -1) < 5:
            fail(errors, rel, 'closure requires acceptance_state AC5 or AC6')
        bad_tests = [t.get('test_id', '?') for t in tests if t.get('required') and t.get('status') != 'pass']
        if bad_tests:
            fail(errors, rel, 'closure has non-passing required tests: ' + ', '.join(bad_tests))
        if calibration.get('unresolved_blocks'):
            fail(errors, rel, 'closure requires no unresolved calibration blocks')
        if len(data.get('reviewers', [])) < 2:
            fail(errors, rel, 'closure requires at least two reviewers')
    else:
        # A non-closure packet for FT-0181 should say why it cannot close.
        if data.get('related_followthrough') == 'FT-0181':
            has_block = any(t.get('blocks_closure') for t in tests) or calibration.get('unresolved_blocks')
            if not has_block:
                fail(errors, rel, 'non-closure FT-0181 packet must name a closure block')

    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU real import acceptance packet':
    raise SystemExit('real import acceptance schema title mismatch')

paths = sorted(ACCEPTANCE_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no real import acceptance packets found')

all_errors = []
closure_ready = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('closure_permitted'):
        closure_ready += 1
    all_errors.extend(validate(path))

if ft_state.get('FT-0181') == 'done' and closure_ready == 0:
    all_errors.append('FT-0181 is done but no acceptance packet permits closure')

if all_errors:
    raise SystemExit('real import acceptance validation errors:\n' + '\n'.join(all_errors))
print(f'check_real_import_acceptance: OK ({len(paths)} packets, {closure_ready} closure-ready)')
