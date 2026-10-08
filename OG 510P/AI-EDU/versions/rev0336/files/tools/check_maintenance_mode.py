import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'maintenance-mode'
SCHEMA_PATH = ROOT / 'schemas' / 'maintenance-mode-state.schema.json'
STATES = {'MM0','MM1','MM2','MM3','MM4','MMX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: return date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')
        return None

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['maintenance_id','revision','maintenance_state','related_followthrough_ids','release_candidate','expiry_date','refresh_triggers','closure_allowed','next_actions','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['maintenance_id'].startswith('MM-'): fail(errors, rel, 'maintenance_id must start MM-')
    if data['maintenance_state'] not in STATES: fail(errors, rel, 'maintenance_state invalid')
    expiry=parse_date(data['expiry_date'], errors, rel, 'expiry_date')
    reviewed=parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if expiry and reviewed and expiry <= reviewed: fail(errors, rel, 'expiry_date must be after last_reviewed')
    if not (ROOT / data['release_candidate']).exists(): fail(errors, rel, 'release_candidate missing')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft:
        if 'FT-0181' not in data['related_followthrough_ids']: fail(errors, rel, 'live FT-0181 must be related')
        if data['closure_allowed'] is not False: fail(errors, rel, 'closure_allowed must be false while FT-0181 is live')
        if data['maintenance_state'] not in {'MM1','MM2','MM3'}: fail(errors, rel, 'live FT-0181 maintenance state must be MM1-MM3')
    triggers=' '.join(data.get('refresh_triggers', [])).lower()
    for phrase in ['src2+', 'public summary', 'policy exception']:
        if phrase not in triggers: fail(errors, rel, f'refresh_triggers missing phrase: {phrase}')
    actions=' '.join(data.get('next_actions', [])).lower()
    if 'keep ft-0181 live' not in actions: fail(errors, rel, 'next_actions must keep FT-0181 live')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU maintenance mode state': raise SystemExit('maintenance mode schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no maintenance mode states found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('maintenance mode validation errors:\n' + '\n'.join(all_errors))
print(f'check_maintenance_mode: OK ({len(paths)} states)')
