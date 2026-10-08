import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
errors = []

if changelog.count('# Changelog') != 1:
    errors.append('CHANGELOG must contain exactly one # Changelog title')
first_nonblank = next((line for line in changelog.splitlines() if line.strip()), '')
if first_nonblank != '# Changelog':
    errors.append('CHANGELOG title must be the first nonblank line')

headers = re.findall(r'^##\s+(rev\d{4})\s+-\s+(\d{4}-\d{2}-\d{2})\s*$', changelog, flags=re.MULTILINE)
if not headers:
    errors.append('CHANGELOG missing revision headers')
else:
    current = receipt.get('revision')
    date = receipt.get('date')
    previous = receipt.get('previous_revision')
    if headers[0] != (current, date):
        errors.append(f'first revision header {headers[0]} does not match receipt {(current, date)}')
    revisions = [rev for rev, _ in headers]
    dupes = sorted({rev for rev in revisions if revisions.count(rev) > 1})
    if dupes:
        errors.append('duplicate CHANGELOG revision headings: ' + ', '.join(dupes))
    if revisions.count(current) != 1:
        errors.append(f'current revision {current} must occur exactly once')
    if previous and revisions.count(previous) != 1:
        errors.append(f'previous revision {previous} must occur exactly once')

for required in receipt.get('changed_surfaces', []):
    if not (ROOT / required).exists():
        errors.append(f'receipt changed surface missing: {required}')

if errors:
    raise SystemExit('receipt/changelog sync errors:\n' + '\n'.join(errors))
print('check_receipt_sync: OK')
