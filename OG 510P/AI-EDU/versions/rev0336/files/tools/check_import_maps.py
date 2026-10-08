import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / 'examples' / 'import-maps'
REQUIRED_TOP = {
    'owners', 'use_case', 'data_map', 'authority', 'memory', 'evidence_claims',
    'construct_and_proof', 'accessibility_and_protected_support', 'security',
    'workload', 'decision', 'publication_and_adapters', 'public_summary'
}
REQUIRED = [
    'map_id', 'source_system', 'source_owner', 'source_truth_class', 'target_schema_version',
    'field_mappings', 'manual_review_fields', 'do_not_import_fields', 'redaction_before_commit',
    'stop_conditions', 'decision_delta_questions'
]
SOURCE_CLASSES={'SRC0','SRC1','SRC2','SRC3','SRC4','SRCX'}

def fail(errors, path, msg):
    errors.append(f'{path}: {msg}')

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

paths=sorted(MAP_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no import maps found')
errors=[]
ids=set()
for path in paths:
    rel=path.relative_to(ROOT).as_posix()
    data=load_json(path)
    for field in REQUIRED:
        if field not in data or data[field] in ('', [], {}, None):
            fail(errors, rel, f'missing or empty {field}')
    mid=data.get('map_id','')
    if not mid.startswith('IMP-MAP-'):
        fail(errors, rel, 'map_id must start with IMP-MAP-')
    if mid in ids:
        fail(errors, rel, f'duplicate map_id {mid}')
    ids.add(mid)
    if data.get('source_truth_class') not in SOURCE_CLASSES:
        fail(errors, rel, 'source_truth_class must be SRC0/SRC1/SRC2/SRC3/SRC4/SRCX')
    if data.get('target_schema_version') != '1.1':
        fail(errors, rel, 'target_schema_version must be 1.1')
    mapped=set(data.get('field_mappings',{}))
    missing=sorted(REQUIRED_TOP-mapped)
    if missing:
        fail(errors, rel, 'field_mappings missing top-level targets: '+', '.join(missing))
    do_not=' '.join(data.get('do_not_import_fields',[])).lower()
    for term in ['raw learner', 'diagnosis', 'security exploit', 'vendor marketing']:
        if term not in do_not:
            fail(errors, rel, 'do_not_import_fields should include '+term)
    stops=' '.join(data.get('stop_conditions',[])).lower()
    for term in ['protected', 'authority', 'evidence']:
        if term not in stops:
            fail(errors, rel, 'stop_conditions should include '+term+' risk')

if errors:
    raise SystemExit('import map validation errors:\n'+'\n'.join(errors))
print(f'check_import_maps: OK ({len(paths)} maps)')
