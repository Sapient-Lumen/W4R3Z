import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
surfaces_path = ROOT / 'SURFACES.json'
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
payload = json.loads(surfaces_path.read_text(encoding='utf-8'))

required_root = {'project', 'schema_surface', 'status', 'axes', 'surfaces', 'stats'}
missing_root = sorted(required_root - payload.keys())
if missing_root:
    raise SystemExit('SURFACES.json missing root keys: ' + ', '.join(missing_root))

if payload['project'] != 'AI-EDU':
    raise SystemExit('SURFACES.json project must be AI-EDU')

if payload.get('last_full_backfill_revision') != receipt.get('revision'):
    raise SystemExit('SURFACES.json last_full_backfill_revision does not match REVISION_RECEIPT revision')

required_fields = {
    'path', 'title', 'type', 'actor', 'stakes', 'sector', 'function', 'risk_family',
    'memory_state', 'proof_state', 'lifecycle', 'authority', 'owner', 'evidence_level',
    'portability', 'followthrough', 'open_questions', 'tags', 'primary_tags', 'mentioned_tags', 'classification_quality'
}

surfaces = payload['surfaces']
paths = []
for idx, row in enumerate(surfaces):
    missing = sorted(required_fields - row.keys())
    if missing:
        raise SystemExit(f'surface row {idx} missing fields: ' + ', '.join(missing))
    rel = row['path']
    paths.append(rel)
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f'surface path does not exist: {rel}')
    if path.suffix != '.md':
        raise SystemExit(f'surface path must be Markdown: {rel}')
    for field in ['actor', 'stakes', 'sector', 'function', 'risk_family', 'memory_state', 'proof_state', 'evidence_level', 'followthrough', 'open_questions', 'tags', 'primary_tags', 'mentioned_tags']:
        if not isinstance(row[field], list):
            raise SystemExit(f'{rel}: {field} must be a list')
    for field in ['title', 'type', 'lifecycle', 'authority', 'owner', 'portability', 'classification_quality']:
        if not isinstance(row[field], str) or not row[field].strip():
            raise SystemExit(f'{rel}: {field} must be a non-empty string')
    if not set(row.get('primary_tags', [])).issubset(set(row.get('tags', []))):
        raise SystemExit(f'{rel}: primary_tags must be a subset of tags')
    if not set(row.get('mentioned_tags', [])).issubset(set(row.get('tags', []))):
        raise SystemExit(f'{rel}: mentioned_tags must be a subset of tags')
    if set(row.get('primary_tags', [])) & set(row.get('mentioned_tags', [])):
        raise SystemExit(f'{rel}: primary_tags and mentioned_tags must not overlap')

if len(paths) != len(set(paths)):
    dupes = sorted({p for p in paths if paths.count(p) > 1})
    raise SystemExit('duplicate SURFACES paths: ' + ', '.join(dupes))

actual_md = sorted(
    p.relative_to(ROOT).as_posix()
    for p in ROOT.rglob('*.md')
    if '__pycache__' not in p.parts and 'scratch' not in p.parts
)
indexed = sorted(paths)
missing = sorted(set(actual_md) - set(indexed))
extra = sorted(set(indexed) - set(actual_md))
if missing:
    raise SystemExit('SURFACES missing Markdown paths:\n' + '\n'.join(missing))
if extra:
    raise SystemExit('SURFACES contains non-Markdown or absent paths:\n' + '\n'.join(extra))

ft_ids = {item['id'] for item in json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']}
oq_text = (ROOT / 'docs/20-governance/open-question-registry.md').read_text(encoding='utf-8')
oq_ids = set(re.findall(r'##\s+(OQ-\d{4})\b', oq_text))
for row in surfaces:
    bad_ft = sorted(set(row['followthrough']) - ft_ids)
    bad_oq = sorted(set(row['open_questions']) - oq_ids)
    if bad_ft:
        raise SystemExit(f"{row['path']}: undefined followthrough refs: " + ', '.join(bad_ft))
    if bad_oq:
        raise SystemExit(f"{row['path']}: undefined open-question refs: " + ', '.join(bad_oq))

stats = payload.get('stats', {})
if stats.get('markdown_surfaces') != len(surfaces):
    raise SystemExit('SURFACES stats.markdown_surfaces does not match row count')

print(f'check_surfaces: OK ({len(surfaces)} markdown surfaces)')
