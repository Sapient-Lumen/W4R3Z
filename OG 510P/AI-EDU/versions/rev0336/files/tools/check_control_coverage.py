import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_DIR = ROOT / 'examples' / 'control-coverage'
SCHEMA_PATH = ROOT / 'schemas' / 'control-coverage-matrix.schema.json'
STATES = {'CCM0', 'CCM1', 'CCM2', 'CCM3', 'CCM4', 'CCMX'}
REQUIRED_IFF = {'IFF1', 'IFF2', 'IFF3', 'IFF4', 'IFF5', 'IFF6', 'IFF7', 'IFF8', 'IFF9', 'IFF10'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}

lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}
fixture_classes = set()
for path in (ROOT / 'examples' / 'import-failure-fixtures').glob('*.json'):
    fixture_classes.add(json.loads(path.read_text(encoding='utf-8')).get('fixture_class'))


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
        'matrix_id', 'revision', 'coverage_state', 'related_followthrough_ids',
        'controls', 'negative_fixture_classes_covered', 'release_boundaries', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['matrix_id'].startswith('CCM-'):
        fail(errors, rel, 'matrix_id must start CCM-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if data['coverage_state'] not in STATES:
        fail(errors, rel, 'coverage_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data.get('related_followthrough_ids', []):
        if fid not in ft_ids:
            fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft and 'FT-0181' not in data.get('related_followthrough_ids', []):
        fail(errors, rel, 'live FT-0181 must be covered')

    covered = set(data.get('negative_fixture_classes_covered', []))
    if not REQUIRED_IFF <= covered:
        fail(errors, rel, 'negative_fixture_classes_covered missing: ' + ', '.join(sorted(REQUIRED_IFF - covered)))
    if not fixture_classes <= covered:
        fail(errors, rel, 'fixture classes not covered by matrix: ' + ', '.join(sorted(fixture_classes - covered)))

    row_classes = set()
    seen_ids = set()
    for idx, row in enumerate(data.get('controls', [])):
        prefix = f'controls[{idx}]'
        for field in ['control_id', 'risk', 'fixture_classes', 'validator_files', 'human_artifact_paths', 'negative_fixture_paths', 'closure_effect', 'may_close_ft0181']:
            if field not in row:
                fail(errors, rel, f'{prefix}.{field} missing')
        cid = row.get('control_id')
        if cid in seen_ids:
            fail(errors, rel, f'duplicate control_id {cid}')
        seen_ids.add(cid)
        if not str(cid).startswith('CCM-'):
            fail(errors, rel, f'{prefix}.control_id must start CCM-')
        if row.get('may_close_ft0181') is True and 'FT-0181' in live_ft:
            fail(errors, rel, f'{cid}: cannot close FT-0181 while it is live')
        for cls in row.get('fixture_classes', []):
            row_classes.add(cls)
            if cls not in REQUIRED_IFF:
                fail(errors, rel, f'{cid}: unknown fixture class {cls}')
        for vpath in row.get('validator_files', []):
            if not (ROOT / vpath).exists():
                fail(errors, rel, f'{cid}: validator missing {vpath}')
            if Path(vpath).name not in lint_tool_names:
                fail(errors, rel, f'{cid}: validator not wired into run_lint_suite: {vpath}')
        for hpath in row.get('human_artifact_paths', []):
            if not (ROOT / hpath).exists():
                fail(errors, rel, f'{cid}: human artifact missing {hpath}')
        for fpath in row.get('negative_fixture_paths', []):
            if not (ROOT / fpath).exists():
                fail(errors, rel, f'{cid}: negative fixture missing {fpath}')
        if 'close' in row.get('closure_effect', '').lower() and row.get('may_close_ft0181') is True:
            fail(errors, rel, f'{cid}: closure_effect overclaims control')
    if not REQUIRED_IFF <= row_classes:
        fail(errors, rel, 'control rows do not cover fixture classes: ' + ', '.join(sorted(REQUIRED_IFF - row_classes)))

    boundary_text = ' '.join(data.get('release_boundaries', [])).lower()
    for phrase in ['cannot themselves supply src2+', 'does not close ft-0181', 'not learning or service effectiveness']:
        if phrase not in boundary_text:
            fail(errors, rel, f'release_boundaries missing phrase: {phrase}')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU control coverage matrix':
    raise SystemExit('control coverage schema title mismatch')

paths = sorted(MATRIX_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no control coverage matrices found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('control coverage validation errors:\n' + '\n'.join(all_errors))
print(f'check_control_coverage: OK ({len(paths)} matrices)')
