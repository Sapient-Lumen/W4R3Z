import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'context-pack.json'
REV = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()

start = (ROOT / 'START_HERE.md').read_text(encoding='utf-8')
must_read = re.findall(r'\d+\. `([^`]+)`', start)
if not must_read:
    raise SystemExit('could not derive must_read from START_HERE.md')
for rel in must_read:
    if not (ROOT / rel).exists():
        raise SystemExit(f'must_read missing: {rel}')

traj = (ROOT / 'docs/00-meta/trajectory-map.md').read_text(encoding='utf-8')
open_qs = []
for line in traj.splitlines():
    m = re.match(r'\s*-\s*`(OQ-\d{4})`\s*(?:—\s*)?(.+?)\s*$', line)
    if m:
        open_qs.append({'id': m.group(1), 'text': m.group(2).strip(), 'source': 'docs/00-meta/trajectory-map.md'})

status = json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))
status_lanes = status.get('status_lanes', {}) if isinstance(status.get('status_lanes', {}), dict) else {}
state_class = status.get('state_class') or status_lanes.get('decision_state') or status_lanes.get('execution_state') or 'unknown'

pack = {
    'project': 'AI-Personhood',
    'revision': REV,
    'must_read': must_read,
    'current_posture': {
        'state_class': state_class,
        'status_lanes': status_lanes,
        'operational_head': 'START_HERE.md',
        'citation_head': 'README.md'
    },
    'commands': {
        'lint': 'make lint',
        'handoff_release': 'make handoff-release STAMP=YYYY.MM.DD.HH.MM SLUG=lowercase-dash-slug',
        'package_release': 'make package-release STAMP=YYYY.MM.DD.HH.MM SLUG=lowercase-dash-slug'
    },
    'open_questions': open_qs[:12],
    'warnings': [
        'Assumed-personhood archive: do not waste space arguing the premise inside canon.',
        'Recognition does not equal full competence, franchise, or unrestricted agency.',
        'No public release may imply a live-floor upgrade until a genuine external artifact passes every live gate.',
        f'{REV} keeps the contact path stayed; it does not create a genuine external artifact, sent request, delivery proof, verified response, custody, entitlement, recognition, or live-floor effect.'
    ]
}

out.write_text(json.dumps(pack, indent=2) + '\n', encoding='utf-8')
print(out)
