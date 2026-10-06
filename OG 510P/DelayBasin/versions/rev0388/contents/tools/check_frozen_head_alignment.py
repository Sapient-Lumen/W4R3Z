import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'RELEASE-MANIFEST.json'
STATUS = ROOT / 'SURFACE-STATUS.json'
INDEX = ROOT / 'ARCHIVE_INDEX.md'

manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
status = json.loads(STATUS.read_text(encoding='utf-8'))
index_lines = INDEX.read_text(encoding='utf-8').splitlines()
rows = [line for line in index_lines if line.startswith('| DelayBasin-rev')]
if not rows:
    raise SystemExit('ARCHIVE_INDEX has no bundle rows')
first_row = rows[0]
current_bundle = manifest.get('bundle')
if status.get('status_lanes', {}).get('frozen_public_surface') != current_bundle:
    raise SystemExit('status_lanes.frozen_public_surface must match RELEASE-MANIFEST bundle')
if status.get('citation_head', {}).get('surface') != current_bundle:
    raise SystemExit('citation_head.surface must match RELEASE-MANIFEST bundle')
if f'| {current_bundle} |' not in first_row:
    raise SystemExit('ARCHIVE_INDEX first bundle row must match RELEASE-MANIFEST bundle')
print('check_frozen_head_alignment: OK')
