import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contracts = json.loads((ROOT / 'CUBE_SURFACE_CONTRACTS.json').read_text(encoding='utf-8'))
surfaces = json.loads((ROOT / 'SURFACES.json').read_text(encoding='utf-8'))
rows = {row['path']: row for row in surfaces['surfaces']}
priority = [row for row in contracts['contracts'] if row.get('required_quality') == 'human-curated']

missing = [row['path'] for row in priority if row['path'] not in rows]
if missing:
    raise SystemExit('priority surface missing from SURFACES.json:\n' + '\n'.join(missing))

not_curated = [
    row['path'] for row in priority
    if rows[row['path']].get('classification_quality') != 'human-curated'
]
if not_curated:
    raise SystemExit('priority surfaces not human-curated:\n' + '\n'.join(not_curated))

required_fields = ['type', 'lifecycle', 'authority', 'owner', 'evidence_level', 'portability']
empty = []
for contract in priority:
    surface = rows[contract['path']]
    for field in required_fields:
        val = surface.get(field)
        if val == '' or val == [] or val is None:
            empty.append(f'{contract["path"]}: {field}')
if empty:
    raise SystemExit('priority surface has empty classification fields:\n' + '\n'.join(empty))

print(f'check_surface_priority_curation: OK ({len(priority)} contract-backed priority rows)')
