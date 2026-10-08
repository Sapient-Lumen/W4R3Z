#!/usr/bin/env python3
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[1]
required = [
    'README.md',
    'START_HERE.md',
    'ARCHIVE_INDEX.md',
    'RELEASE-MANIFEST.json',
    'REVISION-RECEIPT.json',
    'context-pack.json',
    'docs/00-meta/bibliography.md',
    'docs/20-constitution/claim-registry.md',
    'docs/20-constitution/open-question-registry.md',
]

errors = []
for rel in required:
    if not (root / rel).exists():
        errors.append(f'missing required file: {rel}')

for bad in root.rglob('*.pdf'):
    errors.append(f'pdf retained in archive: {bad.relative_to(root)}')

bib = (root / 'docs/00-meta/bibliography.md').read_text()
ids = [line.split('`')[1] for line in bib.splitlines() if line.startswith('- `REF-')]
if len(ids) != len(set(ids)):
    errors.append('duplicate bibliography ids found')

try:
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
    receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text())
    context = json.loads((root / 'context-pack.json').read_text())
    status = json.loads((root / 'SURFACE-STATUS.json').read_text())
    if manifest['revision'] != receipt['revision']:
        errors.append('manifest and receipt revision mismatch')
    if manifest['revision'] != context['revision']:
        errors.append('manifest and context revision mismatch')
    if manifest['revision'] != status['revision']:
        errors.append('manifest and surface-status revision mismatch')
    expected_prefix = f"Theory-of-Everything-{manifest['revision']}-{manifest['timestamp']}-"
    if not manifest['bundle'].startswith(expected_prefix):
        errors.append('bundle name does not match manifest revision/timestamp prefix')
except Exception as e:
    errors.append(f'json parse failure: {e}')

if errors:
    print('LINT FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)

print('LINT OK')
