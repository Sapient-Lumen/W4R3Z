import csv
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / 'tools'
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import smoke_owner_reply_pipeline

SMOKE_TOOL = ROOT / 'tools' / 'smoke_owner_reply_pipeline.py'
FIXTURE = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
EXPECTED_COLUMNS = ['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note']


def run_smoke(*args):
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        returncode = smoke_owner_reply_pipeline.main(list(map(str, args)))
    return returncode, stdout.getvalue()


if not SMOKE_TOOL.exists():
    raise SystemExit('smoke_owner_reply_pipeline.py missing')
if not FIXTURE.exists():
    raise SystemExit('synthetic smoke fixture missing')

with FIXTURE.open(newline='', encoding='utf-8') as fh:
    rows = list(csv.DictReader(fh))
if not rows or list(rows[0].keys()) != EXPECTED_COLUMNS:
    raise SystemExit('synthetic smoke fixture columns changed')
if [row.get('row_id') for row in rows] != [str(i) for i in range(1, 9)]:
    raise SystemExit('synthetic smoke fixture must preserve eight ordered rows')
joined = ' '.join(row.get('owner_response', '').lower() for row in rows)
for term in ['synthetic smoke fixture', 'not a returned owner packet', 'not src2+ evidence', 'do not claim learning']:
    if term not in joined:
        raise SystemExit(f'synthetic smoke fixture missing safety label: {term}')

returncode, stdout = run_smoke('--json')
if returncode != 0:
    raise SystemExit(f'smoke tool failed on fixture:\nSTDOUT={stdout}')
result = json.loads(stdout)
if not result.get('ok'):
    raise SystemExit(f'smoke result not ok: {result}')
for key in ['source_truth_class', 'fixture_path', 'row_count', 'outcome', 'next_action', 'generated_note_sha256', 'next_artifact', 'claim_ceiling', 'do_not']:
    if key not in result:
        raise SystemExit(f'smoke result missing {key}: {result}')
if result['source_truth_class'] != 'SRC0-SMOKE' or result['outcome'] != 'PROCEED-STAGED':
    raise SystemExit(f'smoke fixture must remain SRC0-SMOKE/PROCEED-STAGED: {result}')
if result['row_count'] != 8:
    raise SystemExit(f'smoke fixture row_count must be 8: {result}')
ceiling = result['claim_ceiling'].lower()
for term in ['not real owner evidence', 'not src2+', 'not closure evidence', 'not a public effectiveness claim']:
    if term not in ceiling:
        raise SystemExit(f'smoke claim ceiling missing {term}: {result}')
if result['next_action'].get('next_artifact') != 'templates/ft0181-proceed-staged-note-template.md':
    raise SystemExit(f'smoke next_action must route through staging template: {result}')

out = Path(tempfile.NamedTemporaryFile(suffix='.md', delete=True).name)
try:
    returncode, stdout = run_smoke('--json', '--output-note', out)
    if returncode != 0 or not out.exists():
        raise SystemExit(f'smoke --output-note failed:\nSTDOUT={stdout}')
    note = out.read_text(encoding='utf-8')
    for term in ['Triage outcome: PROCEED-STAGED', 'not closure evidence', 'not proof of learning', 'Synthetic smoke fixture']:
        if term not in note:
            raise SystemExit(f'smoke output note missing {term}')
finally:
    out.unlink(missing_ok=True)

returncode, stdout = run_smoke('--json', '--output-note', ROOT / 'docs' / '00-meta' / 'forbidden-smoke-note.md')
if returncode != 2:
    raise SystemExit(f'smoke output to docs should return 2, got {returncode}: {stdout}')
blocked_output = json.loads(stdout)
if blocked_output.get('ok') or blocked_output.get('outcome') != 'SMOKE-OUTPUT-BLOCKED':
    raise SystemExit(f'smoke output to archive-controlled dir should be blocked: {blocked_output}')
if (ROOT / 'docs' / '00-meta' / 'forbidden-smoke-note.md').exists():
    raise SystemExit('smoke output block must not create the forbidden docs note')

blocked_rows = [dict(row) for row in rows]
blocked_rows[1]['owner_response'] = 'Full export with learner-level rows and raw LMS telemetry is attached.'
blocked = Path(tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False).name)
try:
    with blocked.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(blocked_rows)
    returncode, stdout = run_smoke('--json', '--csv-path', blocked)
    if returncode != 2:
        raise SystemExit(f'blocked smoke fixture should return 2, got {returncode}: {stdout}')
    blocked_result = json.loads(stdout)
    if blocked_result.get('ok') or blocked_result.get('outcome') != 'BLOCK-OVERBROAD':
        raise SystemExit(f'blocked smoke result should be BLOCK-OVERBROAD: {blocked_result}')
finally:
    blocked.unlink(missing_ok=True)

print('check_owner_reply_pipeline_smoke: OK (synthetic fixture, scratch output, archive-output block, blocked refusal; subprocess-free)')
