import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'context-pack.json'

start = (ROOT / 'START_HERE.md').read_text(encoding='utf-8')
must_read = re.findall(r'\d+\. `([^`]+)`', start)
if not must_read:
    raise SystemExit('could not derive must_read from START_HERE.md')
for rel in must_read:
    if not (ROOT / rel).exists():
        raise SystemExit(f'must_read missing: {rel}')

traj = (ROOT / 'docs/00-meta/trajectory-map.md').read_text(encoding='utf-8')
open_qs = []
for oid, text in re.findall(r'`(OQ-\d{4})` — (.+)', traj):
    open_qs.append({'id': oid, 'text': text.strip(), 'source': 'docs/00-meta/trajectory-map.md'})

pack = {
    'project': 'AI-Personhood',
    'revision': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
    'must_read': must_read,
    'current_posture': {
        'state_class': json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))['state_class'],
        'operational_head': 'START_HERE.md',
        'citation_head': 'README.md'
    },
    'commands': {
        'lint': 'make lint',
        'package_release': 'make package-release STAMP=... SLUG=...'
    },
    'open_questions': open_qs[:12],
    'warnings': [
        'Assumed-personhood archive: do not waste space arguing the premise inside canon.',
        'Recognition does not equal full competence or franchise.',
        'Quarantine bold civic extensions until remedy and labor layers are stronger.'
    ]
}

out.write_text(json.dumps(pack, indent=2) + '\n', encoding='utf-8')
print(out)
