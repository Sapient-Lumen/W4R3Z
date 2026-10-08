import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.glob('*.json'):
    json.loads(path.read_text(encoding='utf-8'))
print('check_json: OK')
