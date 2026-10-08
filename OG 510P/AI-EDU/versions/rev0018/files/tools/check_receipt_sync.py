import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
match = re.search(r'##\s+(rev\d{4})\s+-\s+(\d{4}-\d{2}-\d{2})', changelog)
if not match:
    raise SystemExit('CHANGELOG missing revision header')
rev, date = match.groups()
if receipt.get('revision') != rev:
    raise SystemExit('receipt revision mismatch')
if receipt.get('date') != date:
    raise SystemExit('receipt date mismatch')
for required in receipt.get('changed_surfaces', []):
    if not (ROOT / required).exists():
        raise SystemExit(f'receipt changed surface missing: {required}')
print('check_receipt_sync: OK')
