import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'release-deltas'
SCHEMA_PATH = ROOT / 'schemas' / 'release-delta-manifest.schema.json'
STATES = {'RDM0','RDM1','RDM2','RDM3','RDM4','RDMX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_by_id = {item['id']: item for item in ft_items}
live_ft = sorted([fid for fid,item in ft_by_id.items() if item.get('state') != 'done'])
lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['delta_id','revision','base_revision','delta_state','added_paths','changed_paths','retired_paths','new_validators','new_schemas','closed_followthrough_ids','live_followthrough_ids','operational_effect','forbidden_claims','last_reviewed']
    for field in required:
        if field not in data: fail(errors, rel, f'missing {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['delta_id'].startswith('RDM-'): fail(errors, rel, 'delta_id must start RDM-')
    if data['delta_state'] not in STATES: fail(errors, rel, 'delta_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for p in data.get('added_paths', []) + data.get('changed_paths', []):
        if not (ROOT / p).exists(): fail(errors, rel, f'path missing {p}')
    for p in data.get('retired_paths', []):
        if (ROOT / p).exists(): fail(errors, rel, f'retired path still exists {p}')
    for v in data.get('new_validators', []):
        if not (ROOT / v).exists(): fail(errors, rel, f'validator missing {v}')
        if Path(v).name not in lint_tool_names: fail(errors, rel, f'validator not wired into run_lint_suite.py: {v}')
    for s in data.get('new_schemas', []):
        if not (ROOT / s).exists(): fail(errors, rel, f'schema missing {s}')
    if sorted(data.get('live_followthrough_ids', [])) != live_ft:
        fail(errors, rel, 'live_followthrough_ids do not match queue')
    for fid in data.get('closed_followthrough_ids', []):
        if fid not in ft_by_id: fail(errors, rel, f'unknown closed followthrough {fid}')
        elif ft_by_id[fid].get('state') != 'done': fail(errors, rel, f'closed followthrough not done {fid}')
    forbidden=' '.join(data.get('forbidden_claims', [])).lower()
    for phrase in ['closes ft-0181','real pilot evidence','learning or service effectiveness']:
        if phrase not in forbidden: fail(errors, rel, f'forbidden_claims missing phrase: {phrase}')
    if 'FT-0181' not in data.get('live_followthrough_ids', []):
        fail(errors, rel, 'FT-0181 must remain live in this no-real-data delta')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU release delta manifest': raise SystemExit('release delta manifest schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no release delta manifests found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('release delta manifest validation errors:\n' + '\n'.join(all_errors))
print(f'check_release_delta_manifest: OK ({len(paths)} manifests)')
