import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [
    p for p in ROOT.rglob('*.json')
    if '__pycache__' not in p.parts and 'scratch' not in p.parts
]
for path in paths:
    json.loads(path.read_text(encoding='utf-8'))
print(f'check_json: OK ({len(paths)} json files)')
