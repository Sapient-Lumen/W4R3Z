import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / 'examples' / 'assurance-cases'
SCHEMA_PATH = ROOT / 'schemas' / 'release-assurance-case.schema.json'
STATES = {'AC0', 'AC1', 'AC2', 'AC3', 'AC4', 'ACX'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
live_ft = sorted(item['id'] for item in ft_items if item.get('state') != 'done')


def load_ids(folder, key):
    ids = set()
    if folder.exists():
        for path in folder.glob('*.json'):
            ids.add(json.loads(path.read_text(encoding='utf-8')).get(key))
    return ids

rc_ids = load_ids(ROOT / 'examples' / 'release-candidates', 'candidate_id')
ra_ids = load_ids(ROOT / 'examples' / 'release-audit-manifests', 'manifest_id')
sed_ids = load_ids(ROOT / 'examples' / 'synthetic-example-declarations', 'declaration_id')
px_ids = load_ids(ROOT / 'examples' / 'policy-exceptions', 'exception_id')
cb_ids = load_ids(ROOT / 'examples' / 'real-import-closeouts', 'closeout_id')


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


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
        'case_id', 'revision', 'assurance_state', 'top_claim',
        'live_followthrough_ids', 'release_candidate_ids', 'audit_manifest_ids',
        'synthetic_declaration_ids', 'policy_exception_ids', 'closeout_ids',
        'claim_rows', 'forbidden_claims', 'unresolved_external_blocks',
        'decision', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if not data['case_id'].startswith('AC-'):
        fail(errors, rel, 'case_id must start AC-')
    if data['assurance_state'] not in STATES:
        fail(errors, rel, 'assurance_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if sorted(data.get('live_followthrough_ids', [])) != live_ft:
        fail(errors, rel, 'live_followthrough_ids do not match queue')

    for cid in data.get('release_candidate_ids', []):
        if cid not in rc_ids:
            fail(errors, rel, f'unknown release_candidate_id {cid}')
    for mid in data.get('audit_manifest_ids', []):
        if mid not in ra_ids:
            fail(errors, rel, f'unknown audit_manifest_id {mid}')
    for did in data.get('synthetic_declaration_ids', []):
        if did not in sed_ids:
            fail(errors, rel, f'unknown synthetic_declaration_id {did}')
    for px in data.get('policy_exception_ids', []):
        if px not in px_ids:
            fail(errors, rel, f'unknown policy_exception_id {px}')
    for cb in data.get('closeout_ids', []):
        if cb not in cb_ids:
            fail(errors, rel, f'unknown closeout_id {cb}')

    statuses = []
    for row in data.get('claim_rows', []):
        for field in ['claim_id', 'claim', 'status', 'evidence_paths', 'limit']:
            if field not in row:
                fail(errors, rel, f'claim row missing {field}')
        statuses.append(row.get('status'))
        for ep in row.get('evidence_paths', []):
            if not (ROOT / ep).exists():
                fail(errors, rel, f'evidence path missing: {ep}')
    if 'externally_gated' not in statuses and live_ft:
        fail(errors, rel, 'live external gate requires an externally_gated claim row')
    forbidden = ' '.join(data.get('forbidden_claims', [])).lower()
    for phrase in ['all followthrough closed', 'real pilot import complete', 'examples prove effectiveness']:
        if phrase not in forbidden:
            fail(errors, rel, f'forbidden_claims missing phrase: {phrase}')
    if live_ft and not data.get('unresolved_external_blocks'):
        fail(errors, rel, 'live external gate requires unresolved_external_blocks')
    if live_ft and data.get('assurance_state') in {'AC4'}:
        fail(errors, rel, 'cannot be AC4 while live followthrough remains')
    if 'ready-but-not-closed' not in data.get('top_claim', '').lower():
        fail(errors, rel, 'top_claim must say ready-but-not-closed')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU ready-but-not-closed release assurance case':
    raise SystemExit('release assurance case schema title mismatch')

paths = sorted(CASE_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no release assurance cases found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('release assurance case validation errors:\n' + '\n'.join(all_errors))
print(f'check_release_assurance_cases: OK ({len(paths)} cases)')
