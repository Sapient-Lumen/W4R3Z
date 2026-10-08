import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX_DIR = ROOT / 'examples' / 'policy-exceptions'
SCHEMA_PATH = ROOT / 'schemas' / 'policy-exception-record.schema.json'
STATES = {'PX0', 'PX1', 'PX2', 'PX3', 'PX4', 'PXX'}
NON_WAIVABLE = ['SRC2+', 'protected-route', 'action-authority', 'public-summary', 'no-fake-real-import']

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        return date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')
        return None


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'exception_id', 'revision', 'exception_state', 'active',
        'affected_followthrough_ids', 'affected_surfaces', 'requested_waiver',
        'non_waivable_controls_checked', 'accountable_owner', 'start_date',
        'expiry_date', 'learner_facing_effect', 'public_summary_effect',
        'rollback_route', 'decision', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if not data['exception_id'].startswith('PX-'):
        fail(errors, rel, 'exception_id must start PX-')
    if data['exception_state'] not in STATES:
        fail(errors, rel, 'exception_state invalid')
    start = parse_date(data['start_date'], errors, rel, 'start_date')
    expiry = parse_date(data['expiry_date'], errors, rel, 'expiry_date')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if start and expiry and expiry < start:
        fail(errors, rel, 'expiry_date must not precede start_date')

    for ft in data.get('affected_followthrough_ids', []):
        if ft not in ft_ids:
            fail(errors, rel, f'unknown affected_followthrough_id {ft}')
    for surface in data.get('affected_surfaces', []):
        if not (ROOT / surface).exists():
            fail(errors, rel, f'affected surface missing: {surface}')

    checked = ' '.join(data.get('non_waivable_controls_checked', [])).lower()
    for phrase in NON_WAIVABLE:
        if phrase.lower() not in checked:
            fail(errors, rel, f'non_waivable_controls_checked missing {phrase}')

    requested = data.get('requested_waiver', '').lower()
    prohibited_requested = any(term in requested for term in ['src2+', 'protected-route', 'no-fake', 'public summary evidence'])
    if data.get('active') and prohibited_requested:
        fail(errors, rel, 'active exception may not request a non-waivable control')
    if data.get('active') and data.get('exception_state') != 'PX2':
        fail(errors, rel, 'active exception must be PX2')
    if not data.get('active') and data.get('exception_state') == 'PX2':
        fail(errors, rel, 'PX2 exception must be active')
    if data.get('active') and 'none' in data.get('accountable_owner', '').lower():
        fail(errors, rel, 'active exception must have accountable owner')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU policy exception record':
    raise SystemExit('policy exception schema title mismatch')

paths = sorted(EX_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no policy exception records found')

all_errors = []
active = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('active'):
        active += 1
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('policy exception validation errors:\n' + '\n'.join(all_errors))
print(f'check_policy_exceptions: OK ({len(paths)} records, {active} active)')
