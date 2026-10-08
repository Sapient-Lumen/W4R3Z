import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

assumptions = {item['id'] for item in json.loads((ROOT / 'ASSUMPTION_LEDGER.json').read_text(encoding='utf-8'))['items']}
followthrough = {item['id'] for item in json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']}
open_questions = set(re.findall(r'^##\s+(OQ-\d{4})\b', (ROOT / 'docs/20-governance/open-question-registry.md').read_text(encoding='utf-8'), flags=re.MULTILINE))
bibliography = set(re.findall(r'^##\s+(B\d+)\b', (ROOT / 'docs/00-meta/bibliography.md').read_text(encoding='utf-8'), flags=re.MULTILINE))

patterns = {
    'AS': (re.compile(r'\bAS-\d{4}\b'), assumptions),
    'FT': (re.compile(r'\bFT-\d{4}\b'), followthrough),
    'OQ': (re.compile(r'\bOQ-\d{4}\b'), open_questions),
    # Bibliography ids are two or more digits, so burden bands such as B0/B1/B2/B3 are ignored.
    'B': (re.compile(r'(?<![A-Z0-9-])B\d{2,3}\b'), bibliography),
}

errors = []
scan_paths = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.md', '.json'}]
for path in scan_paths:
    if any(part in {'__pycache__'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT).as_posix()
    for namespace, (regex, defined) in patterns.items():
        for match in regex.finditer(text):
            token = match.group(0)
            if token not in defined:
                line = text.count('\n', 0, match.start()) + 1
                errors.append(f'{rel}:{line}: undefined {namespace} reference {token}')

if errors:
    raise SystemExit('semantic reference errors:\n' + '\n'.join(errors))

print('check_semantic_refs: OK')
