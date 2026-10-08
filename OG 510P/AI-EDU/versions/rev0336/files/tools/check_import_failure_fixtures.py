import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / 'examples' / 'import-failure-fixtures'
SCHEMA_PATH = ROOT / 'schemas' / 'import-failure-fixture.schema.json'
CLASSES = {f'IFF{i}' for i in range(11)}
SRC_CLASSES = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX'}
DISPOSITIONS = {'reject', 'quarantine', 'return_to_owner', 'suppress_public_claim', 'require_calibration', 'trim_field'}
REQUIRED_COVERAGE = {'IFF1', 'IFF2', 'IFF3', 'IFF4', 'IFF5', 'IFF6', 'IFF7', 'IFF8', 'IFF9', 'IFF10'}
FORBIDDEN_RAW_STRINGS = [
    'actual learner', 'real learner', 'full transcript', 'diagnosis detail', 'api key:',
    'secret key', 'exploit payload:', 'system prompt:'
]


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0 and all(nonempty(v) for v in value)
    return value is not None


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'fixture_id', 'title', 'related_followthrough', 'fixture_class', 'synthetic_only',
        'source_truth_class', 'prohibited_material_present', 'simulated_faults',
        'referenced_controls', 'expected_blocks', 'expected_disposition', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['fixture_id'].startswith('IFF-'):
        fail(errors, rel, 'fixture_id must start IFF-')
    if data['related_followthrough'] not in ft_ids:
        fail(errors, rel, 'related_followthrough not found')
    if data['fixture_class'] not in CLASSES:
        fail(errors, rel, 'fixture_class invalid')
    if data['source_truth_class'] not in SRC_CLASSES:
        fail(errors, rel, 'source_truth_class invalid')
    if data['expected_disposition'] not in DISPOSITIONS:
        fail(errors, rel, 'expected_disposition invalid')
    if data.get('synthetic_only') is not True:
        fail(errors, rel, 'fixture must be synthetic_only=true')
    if data.get('prohibited_material_present') is not False:
        fail(errors, rel, 'fixture must not contain prohibited material')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    for control in data.get('referenced_controls', []):
        if not (ROOT / control).exists():
            fail(errors, rel, f'referenced control does not exist: {control}')

    blocks = data.get('expected_blocks', [])
    if not any(block.get('blocks_closure') for block in blocks):
        fail(errors, rel, 'at least one expected block must block closure')
    seen = set()
    for block in blocks:
        check_id = block.get('check_id')
        if not check_id:
            fail(errors, rel, 'expected block missing check_id')
        if check_id in seen:
            fail(errors, rel, f'duplicate expected block {check_id}')
        seen.add(check_id)
        if not nonempty(block.get('expected_failure')):
            fail(errors, rel, f'{check_id}: expected_failure missing')

    text = json.dumps(data).lower()
    for bad in FORBIDDEN_RAW_STRINGS:
        if bad in text:
            fail(errors, rel, f'fixture appears to contain forbidden raw material phrase: {bad}')

    if data['fixture_class'] in {'IFF2', 'IFF6'} and data['source_truth_class'] != 'SRCX':
        fail(errors, rel, f'{data["fixture_class"]} fixtures should use source_truth_class SRCX')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU import failure fixture':
    raise SystemExit('import failure fixture schema title mismatch')

paths = sorted(FIXTURE_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no import failure fixtures found')

all_errors = []
classes = set()
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    classes.add(data.get('fixture_class'))
    all_errors.extend(validate(path))

missing = sorted(REQUIRED_COVERAGE - classes)
if missing:
    all_errors.append('fixture coverage missing classes: ' + ', '.join(missing))

if all_errors:
    raise SystemExit('import failure fixture validation errors:\n' + '\n'.join(all_errors))
print(f'check_import_failure_fixtures: OK ({len(paths)} fixtures, classes {", ".join(sorted(classes))})')
