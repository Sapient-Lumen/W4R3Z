import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'release-invariants'
SCHEMA_PATH = ROOT / 'schemas' / 'release-invariant.schema.json'
STATES = {'INV0','INV1','INV2','INV3','INV4','INVX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}
lint_tool_names = {Path(row['path']).name for row in json.loads((ROOT / 'CUBE_TOOLCHAIN_REGISTRY.json').read_text(encoding='utf-8'))['lint_order']}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['invariant_record_id','revision','invariant_state','related_followthrough_ids','release_claim','invariants','forbidden_states','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['invariant_record_id'].startswith('INV-'): fail(errors, rel, 'invariant_record_id must start INV-')
    if data['invariant_state'] not in STATES: fail(errors, rel, 'invariant_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft and 'FT-0181' not in data['related_followthrough_ids']:
        fail(errors, rel, 'live FT-0181 must be related')
    seen=set()
    for idx,row in enumerate(data['invariants']):
        prefix=f'invariants[{idx}]'
        for field in ['id','statement','validator_files','evidence_paths','failure_action','may_close_ft0181']:
            if field not in row: fail(errors, rel, f'{prefix}.{field} missing')
        rid=row.get('id')
        if rid in seen: fail(errors, rel, f'duplicate invariant id {rid}')
        seen.add(rid)
        if row.get('may_close_ft0181') is True and 'FT-0181' in live_ft:
            fail(errors, rel, f'{rid}: invariant cannot close live FT-0181')
        for v in row.get('validator_files', []):
            if not (ROOT / v).exists(): fail(errors, rel, f'{rid}: validator missing {v}')
            if Path(v).name not in lint_tool_names: fail(errors, rel, f'{rid}: validator not wired into run_lint_suite: {v}')
        for p in row.get('evidence_paths', []):
            if not (ROOT / p).exists(): fail(errors, rel, f'{rid}: evidence path missing {p}')
    forbidden=' '.join(data.get('forbidden_states', [])).lower()
    for phrase in ['real pilot evidence', 'ft-0181', 'waive']:
        if phrase not in forbidden: fail(errors, rel, f'forbidden_states missing phrase: {phrase}')
    claim=data.get('release_claim','').lower()
    if 'ready-but-not-closed' not in claim or 'src2+' not in claim:
        fail(errors, rel, 'release_claim must name ready-but-not-closed and SRC2+')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU release invariant record': raise SystemExit('release invariant schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no release invariant records found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('release invariant validation errors:\n' + '\n'.join(all_errors))
print(f'check_release_invariants: OK ({len(paths)} records)')
