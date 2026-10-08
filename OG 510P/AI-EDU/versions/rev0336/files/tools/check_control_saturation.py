import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'control-saturation'
SCHEMA_PATH = ROOT / 'schemas' / 'control-saturation-review.schema.json'
STATES = {'SAT0','SAT1','SAT2','SAT3','SAT4','SATX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}
lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}

def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')

def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix(); errors=[]
    data = json.loads(path.read_text(encoding='utf-8'))
    required = ['review_id','revision','saturation_state','related_followthrough_ids','new_control_allowed','uncovered_risks','existing_controls_reviewed','blocked_claims','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['review_id'].startswith('SAT-'): fail(errors, rel, 'review_id must start SAT-')
    if data['saturation_state'] not in STATES: fail(errors, rel, 'saturation_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft:
        if 'FT-0181' not in data['related_followthrough_ids']:
            fail(errors, rel, 'live FT-0181 must be related')
        if data['saturation_state'] != 'SAT4':
            fail(errors, rel, 'live FT-0181 release should be in SAT4 maintenance saturation')
        if data['new_control_allowed'] is not False:
            fail(errors, rel, 'new_control_allowed must be false while no uncovered risk is named')
        if data.get('uncovered_risks'):
            fail(errors, rel, 'uncovered_risks must be empty for SAT4 no-new-control state')
    for tool in data.get('existing_controls_reviewed', []):
        if not (ROOT / tool).exists(): fail(errors, rel, f'existing control missing: {tool}')
        elif Path(tool).name not in lint_tool_names: fail(errors, rel, f'existing control not wired into lint: {tool}')
    blocked = ' '.join(data.get('blocked_claims', [])).lower()
    for phrase in ['does not close ft-0181','not real pilot evidence','src2+']:
        if phrase not in blocked: fail(errors, rel, f'blocked_claims missing phrase: {phrase}')
    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU control saturation review':
    raise SystemExit('control saturation schema title mismatch')
paths = sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no control saturation reviews found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('control saturation validation errors:\n' + '\n'.join(all_errors))
print(f'check_control_saturation: OK ({len(paths)} reviews)')
