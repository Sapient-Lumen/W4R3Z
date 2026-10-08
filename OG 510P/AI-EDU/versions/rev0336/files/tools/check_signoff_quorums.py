import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUORUM_DIR = ROOT / 'examples' / 'signoff-quorums'
SCHEMA_PATH = ROOT / 'schemas' / 'signoff-quorum.schema.json'
STATES = {'SQ0', 'SQ1', 'SQ2', 'SQ3', 'SQX'}
REQUIRED_ROLES = {
    'record_owner', 'educational_evaluator', 'protected_route_reviewer',
    'security_reviewer', 'public_summary_reviewer', 'archive_maintainer'
}
NON_WAIVABLE_PHRASES = ['src2+', 'protected-route', 'source-status', 'action-authority', 'public-summary', 'no-fake']

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}


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


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'quorum_id', 'revision', 'quorum_state', 'related_followthrough_ids',
        'closure_permitted', 'required_roles', 'conflict_attestations',
        'non_waivable_controls', 'missing_for_closure', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors
    if not data['quorum_id'].startswith('SQ-'):
        fail(errors, rel, 'quorum_id must start SQ-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if data['quorum_state'] not in STATES:
        fail(errors, rel, 'quorum_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data.get('related_followthrough_ids', []):
        if fid not in ft_ids:
            fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft and data.get('closure_permitted') is True:
        fail(errors, rel, 'cannot permit closure while FT-0181 remains live')
    if 'FT-0181' in live_ft and data.get('quorum_state') == 'SQ3':
        fail(errors, rel, 'cannot be SQ3 while FT-0181 remains live')

    roles = {row.get('role') for row in data.get('required_roles', [])}
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        fail(errors, rel, 'missing required roles: ' + ', '.join(missing_roles))
    for row in data.get('required_roles', []):
        if row.get('required_for_closure') is not True:
            fail(errors, rel, f'{row.get("role")}: required_for_closure must be true')
        if row.get('may_be_vendor_only') is not False:
            fail(errors, rel, f'{row.get("role")}: may_be_vendor_only must be false')
        if not nonempty(row.get('current_status')):
            fail(errors, rel, f'{row.get("role")}: current_status missing')

    controls_text = ' '.join(data.get('non_waivable_controls', [])).lower()
    for phrase in NON_WAIVABLE_PHRASES:
        if phrase not in controls_text:
            fail(errors, rel, f'non_waivable_controls missing phrase: {phrase}')
    if live_ft and not data.get('missing_for_closure'):
        fail(errors, rel, 'live FT requires missing_for_closure reasons')
    missing_text = ' '.join(data.get('missing_for_closure', [])).lower()
    if 'src2+' not in missing_text or 'closeout' not in missing_text:
        fail(errors, rel, 'missing_for_closure must mention SRC2+ and closeout')
    for att in data.get('conflict_attestations', []):
        if not nonempty(att.get('attestation_id')) or not nonempty(att.get('role')):
            fail(errors, rel, 'conflict attestation missing id or role')
        if att.get('conflict_disclosed') not in {True, False}:
            fail(errors, rel, f'{att.get("attestation_id")}: conflict_disclosed must be boolean')
        if not nonempty(att.get('attestation')):
            fail(errors, rel, f'{att.get("attestation_id")}: attestation missing')
    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU human signoff quorum':
    raise SystemExit('signoff quorum schema title mismatch')

paths = sorted(QUORUM_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no signoff quorums found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('signoff quorum validation errors:\n' + '\n'.join(all_errors))
print(f'check_signoff_quorums: OK ({len(paths)} quorums)')
