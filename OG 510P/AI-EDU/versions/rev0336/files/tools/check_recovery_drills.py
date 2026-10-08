import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'recovery-drills'
SCHEMA_PATH = ROOT / 'schemas' / 'recovery-drill.schema.json'
STATES = {'DR0','DR1','DR2','DR3','DR4','DRX'}
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
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['drill_packet_id','revision','drill_state','related_followthrough_ids','scenarios','no_closure_claim','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['drill_packet_id'].startswith('DR-'): fail(errors, rel, 'drill_packet_id must start DR-')
    if data['drill_state'] not in STATES: fail(errors, rel, 'drill_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    if data.get('no_closure_claim') is not True: fail(errors, rel, 'no_closure_claim must be true')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft and 'FT-0181' not in data['related_followthrough_ids']:
        fail(errors, rel, 'live FT-0181 must be related')
    seen=set()
    for idx,row in enumerate(data.get('scenarios', [])):
        for field in ['scenario_id','trigger','expected_detection_tools','expected_human_artifacts','recovery_action','pass_condition','may_close_ft0181']:
            if field not in row: fail(errors, rel, f'scenarios[{idx}].{field} missing')
        sid=row.get('scenario_id')
        if sid in seen: fail(errors, rel, f'duplicate scenario_id {sid}')
        seen.add(sid)
        if row.get('may_close_ft0181') is True and 'FT-0181' in live_ft:
            fail(errors, rel, f'{sid}: drill cannot close live FT-0181')
        for tool in row.get('expected_detection_tools', []):
            if not (ROOT / tool).exists(): fail(errors, rel, f'{sid}: tool missing {tool}')
            if Path(tool).name not in lint_tool_names: fail(errors, rel, f'{sid}: tool not wired into lint {tool}')
        for p in row.get('expected_human_artifacts', []):
            if not (ROOT / p).exists(): fail(errors, rel, f'{sid}: human artifact missing {p}')
        if 'ft-0181 remains live' not in row.get('pass_condition','').lower():
            fail(errors, rel, f'{sid}: pass_condition must keep FT-0181 live absent real evidence')
    if len(data.get('scenarios', [])) < 8: fail(errors, rel, 'expected at least 8 recovery scenarios')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU recovery drill packet': raise SystemExit('recovery drill schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no recovery drill packets found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('recovery drill validation errors:\n' + '\n'.join(all_errors))
print(f'check_recovery_drills: OK ({len(paths)} packets)')
