import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RC_DIR = ROOT / 'examples' / 'release-candidates'
SCHEMA_PATH = ROOT / 'schemas' / 'release-candidate-state.schema.json'
STATES = {'RC0', 'RC1', 'RC2', 'RC3', 'RC4', 'RC5', 'RCX'}


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
        return len(value) > 0 and all(nonempty(v) for v in value)
    return value is not None


receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
open_ft = sorted([item['id'] for item in ft_items if item.get('state') != 'done'])
receipt_live = sorted(receipt.get('live_followthrough', []))
lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'candidate_id', 'revision', 'title', 'state', 'allowed_to_ship',
        'claims_all_followthrough_closed', 'open_followthrough_ids',
        'externally_gated_followthrough_ids', 'required_lint_checks',
        'no_fake_import_assertion', 'unresolved_blocks', 'next_unblocker', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    if not data['candidate_id'].startswith('RC-'):
        fail(errors, rel, 'candidate_id must start RC-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, f'revision {data["revision"]} does not match receipt {receipt["revision"]}')
    if data['state'] not in STATES:
        fail(errors, rel, 'state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    if sorted(data['open_followthrough_ids']) != open_ft:
        fail(errors, rel, 'open_followthrough_ids do not match FOLLOWTHROUGH_QUEUE live items')
    if receipt_live != open_ft:
        fail(errors, rel, 'REVISION_RECEIPT live_followthrough does not match queue live items')

    gated = sorted(data.get('externally_gated_followthrough_ids', []))
    ungated = sorted(set(open_ft) - set(gated))
    if data.get('allowed_to_ship') and ungated:
        fail(errors, rel, 'allowed_to_ship with ungated open items: ' + ', '.join(ungated))
    if open_ft and data.get('claims_all_followthrough_closed'):
        fail(errors, rel, 'cannot claim all followthrough closed while live items remain')
    if 'FT-0181' in open_ft and data.get('no_fake_import_assertion') is not True:
        fail(errors, rel, 'FT-0181 open requires no_fake_import_assertion=true')
    if data.get('allowed_to_ship') and data.get('state') not in {'RC3', 'RC4', 'RC5'}:
        fail(errors, rel, 'allowed_to_ship requires RC3, RC4, or RC5')
    if data.get('allowed_to_ship') and not data.get('unresolved_blocks'):
        fail(errors, rel, 'allowed_to_ship with open external gate must name unresolved blocks')
    if not nonempty(data.get('next_unblocker')):
        fail(errors, rel, 'next_unblocker must be nonempty')

    for tool in data.get('required_lint_checks', []):
        if tool not in lint_tool_names:
            fail(errors, rel, f'required lint check not wired into run_lint_suite.py: {tool}')
        if not (ROOT / 'tools' / tool).exists():
            fail(errors, rel, f'required lint check file missing: {tool}')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU release candidate state':
    raise SystemExit('release candidate schema title mismatch')

paths = sorted(RC_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no release candidate records found')

all_errors = []
ship = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('allowed_to_ship'):
        ship += 1
    all_errors.extend(validate(path))

if ship == 0:
    all_errors.append('no release candidate is allowed_to_ship')

if all_errors:
    raise SystemExit('release candidate state validation errors:\n' + '\n'.join(all_errors))
print(f'check_release_candidate_state: OK ({len(paths)} candidates, {ship} allowed-to-ship)')
