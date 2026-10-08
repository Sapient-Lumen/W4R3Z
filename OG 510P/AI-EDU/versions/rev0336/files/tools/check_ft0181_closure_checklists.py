import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'closure-checklists'
SCHEMA_PATH = ROOT / 'schemas' / 'ft0181-closure-evidence-checklist.schema.json'
STATES = {'CL0','CL1','CL2','CL3','CL4','CLX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_by_id={item['id']: item for item in ft_items}
live_ft={item['id'] for item in ft_items if item.get('state') != 'done'}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['checklist_id','revision','checklist_state','related_followthrough_ids','closure_ready','evidence_items','missing_required_evidence','available_preimport_controls','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['checklist_id'].startswith('CL-'): fail(errors, rel, 'checklist_id must start CL-')
    if data['checklist_state'] not in STATES: fail(errors, rel, 'checklist_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_by_id: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft:
        if data.get('closure_ready') is not False: fail(errors, rel, 'FT-0181 live requires closure_ready=false')
        if data.get('checklist_state') == 'CL4': fail(errors, rel, 'FT-0181 live cannot be CL4')
        if 'FT-0181' not in data['related_followthrough_ids']: fail(errors, rel, 'live FT-0181 must be related')
    required_types=set()
    for idx,row in enumerate(data.get('evidence_items', [])):
        for field in ['item_id','evidence_type','required_for_closure','current_status','artifact_paths','closure_condition','may_close_ft0181_now']:
            if field not in row: fail(errors, rel, f'evidence_items[{idx}].{field} missing')
        required_types.add(row.get('evidence_type'))
        if row.get('may_close_ft0181_now') is True and 'FT-0181' in live_ft:
            fail(errors, rel, f'{row.get("item_id")}: may_close_ft0181_now cannot be true while live')
        for p in row.get('artifact_paths', []):
            if not (ROOT / p).exists(): fail(errors, rel, f'{row.get("item_id")}: artifact path missing {p}')
    must_include={'minimized SRC2+ owner-reviewed real pilot packet','decision-delta log','closeout-board minutes','signoff quorum and conflict attestation'}
    missing=' '.join(data.get('missing_required_evidence', [])).lower()
    for phrase in ['src2+', 'decision-delta', 'closeout', 'signoff', 'end-of-window', 'post-readout']:
        if phrase not in missing: fail(errors, rel, f'missing_required_evidence must mention {phrase}')
    controls=' '.join(data.get('available_preimport_controls', [])).lower()
    for phrase in ['negative fixtures','synthetic examples','policy exception','control coverage','end-of-window readout','post-readout action']:
        if phrase not in controls: fail(errors, rel, f'available_preimport_controls must mention {phrase}')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU FT-0181 closure evidence checklist': raise SystemExit('closure checklist schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no FT-0181 closure checklists found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('FT-0181 closure checklist validation errors:\n' + '\n'.join(all_errors))
print(f'check_ft0181_closure_checklists: OK ({len(paths)} checklists, 0 closure-ready)')
