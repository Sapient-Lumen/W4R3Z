import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / 'BRANCH_FAMILY_INDEX.json'
SCHEMA_PATH = ROOT / 'schemas' / 'branch-family-index.schema.json'
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU branch family index':
    raise SystemExit('branch family schema title mismatch')

payload = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
errors = []

def fail(msg):
    errors.append(msg)

if payload.get('project') != 'AI-EDU':
    fail('project must be AI-EDU')
if payload.get('revision') != receipt['revision']:
    fail('revision does not match REVISION_RECEIPT')
if payload.get('status') != 'branch-family-index':
    fail('status must be branch-family-index')
if payload.get('generated_by') != 'tools/gen_branch_family_index.py':
    fail('generated_by mismatch')

actual = sorted(
    p.relative_to(ROOT).as_posix()
    for p in (ROOT / 'docs' / '20-governance').glob('*.md')
    if re.match(r'^(first|portable|late-relapse)-', p.name)
)

seen = []
families = payload.get('families', [])
family_ids = set()
for family in families:
    fid = family.get('family_id')
    if not fid or fid in family_ids:
        fail(f'duplicate or missing family_id: {fid}')
    family_ids.add(fid)
    paths = family.get('paths', [])
    if family.get('count') != len(paths):
        fail(f'{fid}: count does not match paths')
    if len(paths) != len(set(paths)):
        fail(f'{fid}: duplicate paths')
    for rel in paths:
        seen.append(rel)
        path = ROOT / rel
        if not path.exists():
            fail(f'{fid}: missing path {rel}')
        if not rel.startswith('docs/20-governance/') or not rel.endswith('.md'):
            fail(f'{fid}: path outside branch scope {rel}')
    for field in ['preferred_entry', 'canonical_compression']:
        rel = family.get(field)
        if not rel or not (ROOT / rel).exists():
            fail(f'{fid}: {field} missing or nonexistent: {rel}')
    if family.get('refactor_posture') != 'archive_in_place_with_family_index':
        fail(f'{fid}: refactor_posture must be archive_in_place_with_family_index')
    rule = family.get('new_branch_rule', '').lower()
    for phrase in ['search this family', 'genuinely new material pattern']:
        if phrase not in rule:
            fail(f'{fid}: new_branch_rule missing phrase {phrase}')

if sorted(seen) != actual:
    missing = sorted(set(actual) - set(seen))
    extra = sorted(set(seen) - set(actual))
    if missing:
        fail('missing branch paths: ' + ', '.join(missing))
    if extra:
        fail('extra branch paths: ' + ', '.join(extra))

stats = payload.get('stats', {})
if stats.get('branch_surfaces') != len(actual):
    fail('stats.branch_surfaces mismatch')
if stats.get('families') != len(families):
    fail('stats.families mismatch')
if 'hot_exam_recipient_followup_shells' not in family_ids:
    fail('missing hot_exam_recipient_followup_shells family')
else:
    hot = next(f for f in families if f.get('family_id') == 'hot_exam_recipient_followup_shells')
    if hot.get('count', 0) < 40:
        fail('hot_exam_recipient_followup_shells unexpectedly small')

note = payload.get('maintenance_note', '').lower()
for phrase in ['does not move historical files', 'does not close ft-0181']:
    if phrase not in note:
        fail(f'maintenance_note missing phrase: {phrase}')

if errors:
    raise SystemExit('branch family index validation errors:\n' + '\n'.join(errors))
print(f'check_branch_family_index: OK ({len(actual)} branch surfaces, {len(families)} families)')
