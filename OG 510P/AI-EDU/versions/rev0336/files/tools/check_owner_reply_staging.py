import csv
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / 'tools'
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import stage_owner_reply_csv

STAGE_TOOL = ROOT / 'tools' / 'stage_owner_reply_csv.py'
TRIAGE_TOOL = ROOT / 'tools' / 'triage_owner_reply_csv.py'
TEMPLATE = ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv'
STAGING_TEMPLATE = ROOT / 'templates' / 'ft0181-proceed-staged-note-template.md'
SMOKE_FIXTURE = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
EXPECTED_COLUMNS = ['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note']

SAFE_RESPONSES = {
    '1': 'AIEDU-SR-003 capped draft-reminder workflow; course operations lead via local course ops mailbox; local reminder queue; 2026-05-01 to 2026-05-31.',
    '2': 'Aggregate counts above local threshold: eligible 120, draft-reminder 43, human-sent 31, discarded 12, fallback/manual route 5, corrections 2, incidents 0.',
    '3': 'Draft-only queue note; no automatic send; no durable write or posting; no penalty or grading effect; no protected-status inference.',
    '4': 'Human fallback is normal staff outreach; rollback owner is course operations lead; incident class labels none; stop if fallback count spikes or any penalty route appears.',
    '5': 'Workload signal unknown for first packet; method not yet instrumented beyond owner estimate.',
    '6': 'Guidance note: staff received short local workflow guidance owned by course operations; no named staff evaluation attached.',
    '7': 'Public claim ceiling: process-only staging note; do not claim learning, safety, access, workload, compliance, scale, or effectiveness.',
    '8': 'Real owner-attested operational aggregate; raw learner data, protected facts, small cells, gradebook rows, messages, and security details were removed, withheld, or kept local.',
}


class Proc:
    def __init__(self, returncode, stdout):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ''


def read_template_rows():
    with TEMPLATE.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    if not rows or set(rows[0].keys()) != set(EXPECTED_COLUMNS):
        raise SystemExit('owner reply template columns changed unexpectedly')
    return rows


def write_fixture(responses):
    rows = read_template_rows()
    for row in rows:
        row['owner_response'] = responses.get(row['row_id'], '')
    handle = tempfile.NamedTemporaryFile('w', newline='', encoding='utf-8', suffix='.csv', delete=False)
    with handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(handle.name)


def run_stage(path, output=None, allow_src0_smoke=False):
    argv = [str(path)]
    if output:
        argv += ['--output', str(output)]
    if allow_src0_smoke:
        argv += ['--allow-src0-smoke']
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        returncode = stage_owner_reply_csv.main(argv)
    return Proc(returncode, stdout.getvalue())


if not STAGE_TOOL.exists():
    raise SystemExit('stage_owner_reply_csv.py missing')
if not TRIAGE_TOOL.exists():
    raise SystemExit('triage_owner_reply_csv.py missing')
if not STAGING_TEMPLATE.exists():
    raise SystemExit('proceed-staged note template missing')
if not SMOKE_FIXTURE.exists():
    raise SystemExit('synthetic smoke fixture missing')

template_text = STAGING_TEMPLATE.read_text(encoding='utf-8').lower()
for term in ['proceed-staged', 'not closure evidence', 'owner packet workbench', 'do not paste', 'ft-0181 remains live']:
    if term not in template_text:
        raise SystemExit(f'staging template missing required term: {term}')

safe_path = write_fixture(SAFE_RESPONSES)
try:
    proc = run_stage(safe_path)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 0:
    raise SystemExit(f'safe staging failed:\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}')
note = proc.stdout
for term in [
    'FT-0181 proceed-staged owner reply note',
    'Triage outcome: PROCEED-STAGED',
    'AIEDU-SR-003',
    'docs/30-operations/ft0181-owner-packet-workbench.md',
    'Source truth class at staging: UNVERIFIED-OWNER-REPLY',
    'Source CSV SHA-256:',
    'not closure evidence',
    'not proof of learning',
    'FT-0181` remains live',
    'Copy only the minimized answers',
]:
    if term not in note:
        raise SystemExit(f'stage output missing required term: {term}\n{note}')
if '| 1 |' not in note or '| 8 |' not in note:
    raise SystemExit('stage output must preserve eight row slots')

proc = run_stage(SMOKE_FIXTURE)
if proc.returncode != 2:
    raise SystemExit(f'synthetic smoke fixture should be blocked by normal staging CLI, got {proc.returncode}: {proc.stdout}')
for term in ['SRC0-STAGING-BLOCKED', 'SRC0-SMOKE', 'smoke_owner_reply_pipeline.py', 'not real owner evidence']:
    if term not in proc.stdout:
        raise SystemExit(f'synthetic staging block missing {term}: {proc.stdout}')

proc = run_stage(SMOKE_FIXTURE, allow_src0_smoke=True)
if proc.returncode != 0:
    raise SystemExit(f'smoke harness opt-in staging should succeed for plumbing note: {proc.stdout} {proc.stderr}')
for term in ['Source truth class at staging: SRC0-SMOKE', 'Synthetic smoke fixture', 'not a returned owner packet', 'must not be copied']:
    if term not in proc.stdout:
        raise SystemExit(f'allow-src0-smoke note missing {term}: {proc.stdout}')

proc = run_stage(TEMPLATE)
if proc.returncode != 2:
    raise SystemExit(f'archive-controlled template staging should be blocked, got {proc.returncode}: {proc.stdout}')
for term in ['RETURNED-CSV-SOURCE-BLOCKED', 'SRC0-CONTROLLED-ARCHIVE', 'make owner-field-next']:
    if term not in proc.stdout:
        raise SystemExit(f'template staging source block missing {term}: {proc.stdout}')

blocked = dict(SAFE_RESPONSES)
blocked['2'] = 'Full export with learner-level rows and raw LMS telemetry is attached.'
blocked_path = write_fixture(blocked)
try:
    proc = run_stage(blocked_path)
finally:
    blocked_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'blocked staging should return 2, got {proc.returncode}: {proc.stdout}')
for term in ['BLOCK-OVERBROAD', 'next_action', 'Only PROCEED-STAGED']:
    if term not in proc.stdout:
        raise SystemExit(f'blocked staging output missing {term}: {proc.stdout}')

safe_path = write_fixture(SAFE_RESPONSES)
out = Path(tempfile.NamedTemporaryFile(suffix='.md', delete=True).name)
try:
    proc = run_stage(safe_path, out)
    if proc.returncode != 0 or not out.exists():
        raise SystemExit(f'--output staging failed: {proc.stdout} {proc.stderr}')
    written = out.read_text(encoding='utf-8')
    if 'PROCEED-STAGED' not in written or 'Generated triage summary' not in written:
        raise SystemExit('--output staging note missing expected content')
finally:
    safe_path.unlink(missing_ok=True)
    out.unlink(missing_ok=True)

safe_path = write_fixture(SAFE_RESPONSES)
try:
    proc = run_stage(safe_path, ROOT / 'docs' / '00-meta' / 'forbidden-proceed-staged.md')
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'staging output to docs should return 2, got {proc.returncode}: {proc.stdout}')
if (ROOT / 'docs' / '00-meta' / 'forbidden-proceed-staged.md').exists():
    raise SystemExit('staging output block must not create docs staging note')
if 'STAGING-OUTPUT-BLOCKED' not in proc.stdout:
    raise SystemExit(f'staging docs block missing code: {proc.stdout}')

safe_path = write_fixture(SAFE_RESPONSES)
leak_out = ROOT / 'local-proceed-staged.md'
try:
    proc = run_stage(safe_path, leak_out)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'staging output to nonscratch archive root should return 2, got {proc.returncode}: {proc.stdout}')
if leak_out.exists():
    raise SystemExit('staging nonscratch output block must not create root leakage file')
if 'archive-nonscratch-output' not in proc.stdout:
    raise SystemExit(f'staging nonscratch block missing shared boundary: {proc.stdout}')

print('check_owner_reply_staging: OK (safe staging note, smoke/control-source block, blocked refusal, --output path, archive-output block; subprocess-free)')
