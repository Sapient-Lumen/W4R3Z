import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_DIR = ROOT / 'examples' / 'real-import-closeouts'
SCHEMA_PATH = ROOT / 'schemas' / 'real-import-closeout.schema.json'
SRC_ORDER = {'SRC0': 0, 'SRC1': 1, 'SRC2': 2, 'SRC3': 3, 'SRC4': 4, 'SRCX': -1}
CB_ORDER = {'CB0': 0, 'CB1': 1, 'CB2': 2, 'CB3': 3, 'CB4': 4, 'CB5': 5, 'CB6': 6, 'CBX': -1}


def load_ids(folder, key):
    ids = set()
    if folder.exists():
        for path in folder.glob('*.json'):
            ids.add(json.loads(path.read_text(encoding='utf-8')).get(key))
    return ids

manifest_ids = load_ids(ROOT / 'examples' / 'import-readiness', 'manifest_id')
acceptance_ids = load_ids(ROOT / 'examples' / 'real-import-acceptance', 'acceptance_id')
release_ids = load_ids(ROOT / 'examples' / 'release-candidates', 'candidate_id')
service_ids = load_ids(ROOT / 'examples' / 'service-records', 'record_id')
lifecycle_ids = load_ids(ROOT / 'examples' / 'service-lifecycle-decisions', 'decision_id')
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_state = {item['id']: item.get('state') for item in ft_items}


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


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'closeout_id', 'title', 'related_followthrough', 'closeout_state',
        'source_truth_class', 'closure_permitted', 'referenced_manifest_ids',
        'referenced_acceptance_ids', 'referenced_release_candidate_ids',
        'candidate_service_record_ids', 'lifecycle_decision_ids', 'decision_delta_summary',
        'public_summary_actions', 'evaluator_independence_attestation', 'unresolved_blocks',
        'decision', 'last_reviewed'
    ]
    for field in required:
        if field not in data:
            fail(errors, rel, f'missing {field}')
    if errors:
        return errors

    for field in ['closeout_id', 'title', 'related_followthrough', 'closeout_state', 'source_truth_class', 'decision', 'last_reviewed']:
        if not nonempty(data.get(field)):
            fail(errors, rel, f'empty {field}')
    if errors:
        return errors

    if not data['closeout_id'].startswith('CB-'):
        fail(errors, rel, 'closeout_id must start CB-')
    if data['related_followthrough'] not in ft_state:
        fail(errors, rel, 'related_followthrough not found')
    if data['closeout_state'] not in CB_ORDER:
        fail(errors, rel, 'closeout_state invalid')
    if data['source_truth_class'] not in SRC_ORDER:
        fail(errors, rel, 'source_truth_class invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    for mid in data.get('referenced_manifest_ids', []):
        if mid not in manifest_ids:
            fail(errors, rel, f'unknown referenced_manifest_id {mid}')
    for aid in data.get('referenced_acceptance_ids', []):
        if aid not in acceptance_ids:
            fail(errors, rel, f'unknown referenced_acceptance_id {aid}')
    for cid in data.get('referenced_release_candidate_ids', []):
        if cid not in release_ids:
            fail(errors, rel, f'unknown referenced_release_candidate_id {cid}')
    for rid in data.get('candidate_service_record_ids', []):
        if rid not in service_ids:
            fail(errors, rel, f'unknown candidate_service_record_id {rid}')
    for lid in data.get('lifecycle_decision_ids', []):
        if lid not in lifecycle_ids:
            fail(errors, rel, f'unknown lifecycle_decision_id {lid}')

    if not data.get('decision_delta_summary'):
        fail(errors, rel, 'decision_delta_summary must be nonempty')
    if not data.get('public_summary_actions'):
        fail(errors, rel, 'public_summary_actions must be nonempty')
    attestation = data.get('evaluator_independence_attestation', '').lower()
    if 'reviewer' not in attestation and 'review' not in attestation:
        fail(errors, rel, 'evaluator_independence_attestation must mention review/reviewer separation')

    if data.get('closure_permitted'):
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, 'closure requires source_truth_class SRC2 or stronger')
        if CB_ORDER.get(data['closeout_state'], -1) < 5:
            fail(errors, rel, 'closure requires closeout_state CB5 or CB6')
        if data.get('unresolved_blocks'):
            fail(errors, rel, 'closure requires no unresolved blocks')
        if not data.get('candidate_service_record_ids'):
            fail(errors, rel, 'closure requires candidate_service_record_ids')
        if not data.get('lifecycle_decision_ids'):
            fail(errors, rel, 'closure requires lifecycle_decision_ids')
    else:
        if data.get('related_followthrough') == 'FT-0181' and not data.get('unresolved_blocks'):
            fail(errors, rel, 'non-closure FT-0181 closeout must name unresolved blocks')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU real import closeout board minutes':
    raise SystemExit('real import closeout schema title mismatch')

paths = sorted(CLOSEOUT_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no real import closeout records found')

all_errors = []
closure_ready = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('closure_permitted'):
        closure_ready += 1
    all_errors.extend(validate(path))

if ft_state.get('FT-0181') == 'done' and closure_ready == 0:
    all_errors.append('FT-0181 is done but no closeout board permits closure')

if all_errors:
    raise SystemExit('real import closeout validation errors:\n' + '\n'.join(all_errors))
print(f'check_real_import_closeouts: OK ({len(paths)} closeouts, {closure_ready} closure-ready)')
