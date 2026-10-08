import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'public-claim-lexicons'
SCHEMA_PATH = ROOT / 'schemas' / 'public-claim-lexicon.schema.json'
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}
live_ft = {item['id'] for item in ft_items if item.get('state') != 'done'}

def fail(errors, rel, msg): errors.append(f'{rel}: {msg}')
def parse_date(value, errors, rel, field):
    try: date.fromisoformat(value)
    except Exception: fail(errors, rel, f'{field} must be ISO date')

def validate(path: Path):
    rel=path.relative_to(ROOT).as_posix(); errors=[]
    data=json.loads(path.read_text(encoding='utf-8'))
    required=['lexicon_id','revision','related_followthrough_ids','allowed_phrases','conditional_phrases','forbidden_phrases_before_ft0181_close','repair_action','last_reviewed']
    for field in required:
        if field not in data or data[field] in ('', [], None): fail(errors, rel, f'missing or empty {field}')
    if errors: return errors
    if data['revision'] != receipt['revision']: fail(errors, rel, 'revision does not match receipt')
    if not data['lexicon_id'].startswith('PCL-'): fail(errors, rel, 'lexicon_id must start PCL-')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for fid in data['related_followthrough_ids']:
        if fid not in ft_ids: fail(errors, rel, f'unknown followthrough id {fid}')
    if 'FT-0181' in live_ft and 'FT-0181' not in data['related_followthrough_ids']:
        fail(errors, rel, 'live FT-0181 must be related')
    allowed=' '.join(data.get('allowed_phrases', [])).lower()
    forbidden=' '.join(data.get('forbidden_phrases_before_ft0181_close', [])).lower()
    conditional=' '.join(data.get('conditional_phrases', [])).lower()
    for phrase in ['ready-but-not-closed','not real pilot evidence','src2+']:
        if phrase not in allowed: fail(errors, rel, f'allowed_phrases missing phrase: {phrase}')
    for phrase in ['proves learning','ft-0181 closed','safe to scale','evidence complete']:
        if phrase not in forbidden: fail(errors, rel, f'forbidden phrases missing: {phrase}')
    if 'learning' not in conditional or 'workload' not in conditional:
        fail(errors, rel, 'conditional phrases must cover learning and workload claims')
    if 'recovery drill' not in data.get('repair_action','').lower():
        fail(errors, rel, 'repair_action must mention recovery drill')
    return errors

schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU public claim lexicon': raise SystemExit('public claim lexicon schema title mismatch')
paths=sorted(DIR.glob('*.json'))
if not paths: raise SystemExit('no public claim lexicons found')
all_errors=[]
for path in paths: all_errors.extend(validate(path))
if all_errors: raise SystemExit('public claim lexicon validation errors:\n' + '\n'.join(all_errors))
print(f'check_public_claim_lexicons: OK ({len(paths)} lexicons)')
