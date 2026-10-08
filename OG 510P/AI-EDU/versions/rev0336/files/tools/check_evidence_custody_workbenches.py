import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'evidence-custody'
SCHEMA_PATH = ROOT / 'schemas' / 'evidence-custody-workbench.schema.json'
STAGES = {'CUST0','CUST1','CUST2','CUST3','CUST4','CUST5','CUSTX'}
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}
ft_ids = {item['id'] for item in ft_items}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['custody_id','revision','custody_stage','related_followthrough_ids','source_packet_class','raw_data_committed','protected_fields_policy','security_payload_policy','derived_artifacts','may_close_ft0181','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['custody_id'].startswith('CUST-'): fail(errors, rel, 'custody_id must start CUST-')
    if data['custody_stage'] not in STAGES: fail(errors, rel, 'custody_stage invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft:
        if 'FT-0181' not in data['related_followthrough_ids']: fail(errors, rel, 'live FT-0181 must be related')
        if data['may_close_ft0181'] is not False: fail(errors, rel, 'may_close_ft0181 must be false while no real source exists')
    if data.get('raw_data_committed') is not False:
        fail(errors, rel, 'raw_data_committed must be false for public archive custody workbench')
    text = ' '.join([data.get('source_packet_class',''), data.get('protected_fields_policy',''), data.get('security_payload_policy','')]).lower()
    for phrase in ['protected', 'security', 'no src2+']:
        if phrase not in text: fail(errors, rel, f'custody policies missing phrase: {phrase}')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU evidence custody workbench': raise SystemExit('evidence custody schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no evidence custody workbenches found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('evidence custody validation errors:\n' + '\n'.join(all_errors))
print(f'check_evidence_custody_workbenches: OK ({len(paths)} workbenches)')
