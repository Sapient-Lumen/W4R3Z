from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'ARCHIVE_INDEX.md'
index = index_path.read_text(encoding='utf-8')
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
revision = receipt.get('revision')

if f'for {revision}' not in index.split('\n', 5)[0:5][2] if len(index.split('\n', 5)) > 2 else True:
    raise SystemExit(f'ARCHIVE_INDEX header must name current revision {revision}')
if 'Markdown, JSON, Python, CSV, and Makefile surfaces' not in index:
    raise SystemExit('ARCHIVE_INDEX header must describe Markdown, JSON, Python, CSV, and Makefile coverage')

tracked = []
for path in ROOT.rglob('*'):
    if path.is_dir():
        continue
    if any(part in {'__pycache__', 'scratch'} for part in path.parts):
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith('.') or rel.endswith('.zip'):
        continue
    if rel == 'ARCHIVE_INDEX.md':
        continue
    if path.suffix in {'.md', '.json', '.py', '.csv'} or rel == 'Makefile':
        tracked.append(rel)

missing = [rel for rel in sorted(tracked) if f'`{rel}`' not in index]
if missing:
    raise SystemExit('ARCHIVE_INDEX missing tracked paths:\n' + '\n'.join(missing))

print(f'check_archive_index: OK ({len(tracked)} tracked surfaces, header {revision})')
