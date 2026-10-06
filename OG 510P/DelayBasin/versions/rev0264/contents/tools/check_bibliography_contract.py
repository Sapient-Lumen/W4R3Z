import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIB = ROOT / 'docs/00-meta/bibliography.md'
text = BIB.read_text(encoding='utf-8')
pattern = re.compile(r"(^- `REF-(\d{4})` — .*?)(?=^\- `REF-\d{4}` — |\Z)", re.MULTILINE | re.DOTALL)
ids = []
for match in pattern.finditer(text):
    block, rid = match.group(1), match.group(2)
    ids.append(rid)
    if '- URL: ' not in block:
        print(f'bibliography entry REF-{rid} missing URL')
        sys.exit(1)
    if '- Load-bearing use: ' not in block:
        print(f'bibliography entry REF-{rid} missing load-bearing use')
        sys.exit(1)
if not ids:
    print('bibliography missing REF entries')
    sys.exit(1)
if len(ids) != len(set(ids)):
    print('bibliography has duplicate REF ids')
    sys.exit(1)
if ids != sorted(ids):
    print('bibliography REF ids are not in ascending order')
    sys.exit(1)
print('check_bibliography_contract: OK')
