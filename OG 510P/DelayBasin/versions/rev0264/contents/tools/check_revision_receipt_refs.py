import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
bib = (ROOT / 'docs/00-meta/bibliography.md').read_text(encoding='utf-8')
ids = set(re.findall(r'REF-(\d{4})', bib))
refs = receipt.get('refs_used')
if not isinstance(refs, list) or not refs:
    raise SystemExit('receipt refs_used must be a non-empty list')
seen = set()
for ref in refs:
    m = re.fullmatch(r'docs/00-meta/bibliography\.md#ref-(\d{4})', ref)
    if not m:
        raise SystemExit(f'invalid receipt bibliography ref format: {ref}')
    rid = m.group(1)
    if rid not in ids:
        raise SystemExit(f'receipt refs_used points to missing bibliography entry: {ref}')
    if ref in seen:
        raise SystemExit(f'duplicate receipt bibliography ref: {ref}')
    seen.add(ref)
print('check_revision_receipt_refs: OK')
