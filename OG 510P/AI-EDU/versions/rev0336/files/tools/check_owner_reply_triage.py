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

import triage_owner_reply_csv

TOOL = ROOT / 'tools' / 'triage_owner_reply_csv.py'
TEMPLATE = ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv'
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


def read_template_rows():
    with TEMPLATE.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    if not rows or set(rows[0].keys()) != set(EXPECTED_COLUMNS):
        raise SystemExit('template columns changed unexpectedly')
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


def run_tool(path):
    """Exercise the CLI main path without spawning a subprocess.

    The earlier version of this check forked the triage CLI for every case.
    In this cloudtainer that was slow and occasionally left stale validators.
    Direct main() invocation keeps the same JSON/return-code contract while
    avoiding process churn in the highest-traffic owner-reply lane.
    """
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        returncode = triage_owner_reply_csv.main([str(path), '--json'])
    if returncode not in {0, 2}:
        raise SystemExit(f'triage tool failed unexpectedly: rc={returncode}\nSTDOUT={stdout.getvalue()}')
    return json.loads(stdout.getvalue())


def assert_outcome(label, responses, expected, next_artifact=None):
    path = write_fixture(responses)
    try:
        result = run_tool(path)
    finally:
        path.unlink(missing_ok=True)
    if result.get('outcome') != expected:
        raise SystemExit(f'{label}: expected {expected}, got {result}')
    next_action = result.get('next_action') or {}
    if next_action.get('outcome') != expected:
        raise SystemExit(f'{label}: next_action outcome mismatch: {result}')
    if not next_action.get('summary') or not next_action.get('ceiling'):
        raise SystemExit(f'{label}: next_action missing summary or ceiling: {result}')
    if next_artifact and next_action.get('next_artifact') != next_artifact:
        raise SystemExit(f'{label}: expected next_artifact {next_artifact}, got {result}')


assert_outcome('blank template', {}, 'NO-OWNER-PACKET', 'templates/ft0181-triage-outcome-note-template.md')
assert_outcome('safe staged packet', SAFE_RESPONSES, 'PROCEED-STAGED', 'templates/ft0181-proceed-staged-note-template.md')
protected = dict(SAFE_RESPONSES)
protected['2'] = 'Counts split by accommodation / IEP status and discipline flag are included.'
assert_outcome('protected packet', protected, 'BLOCK-PROTECTED')
over = dict(SAFE_RESPONSES)
over['2'] = 'Owner can only provide the full export with learner-level rows and raw LMS telemetry.'
assert_outcome('overbroad packet', over, 'BLOCK-OVERBROAD')
auth = dict(SAFE_RESPONSES)
auth['3'] = 'The system automatically sends reminders and may update the course record.'
assert_outcome('authority packet', auth, 'BLOCK-AUTHORITY')
claim = dict(SAFE_RESPONSES)
claim['7'] = 'This proves learning gains and is ready to scale.'
assert_outcome('unsupported claim packet', claim, 'BLOCK-EVIDENCE', 'templates/ft0181-triage-outcome-note-template.md')
small_cell = dict(SAFE_RESPONSES)
small_cell['2'] = 'Eligible 120, draft reminders 43, accommodation subgroup n=3, small-cell table included.'
assert_outcome('small-cell packet', small_cell, 'BLOCK-PROTECTED', 'templates/ft0181-triage-outcome-note-template.md')
vendor = dict(SAFE_RESPONSES)
vendor['4'] = 'Fallback requires vendor action alone and there is no local rollback.'
assert_outcome('vendor-only rollback packet', vendor, 'BLOCK-AUTHORITY', 'templates/ft0181-triage-outcome-note-template.md')
reask = dict(SAFE_RESPONSES)
reask['5'] = ''
assert_outcome('one-row clarification packet', reask, 'RE-ASK-ONCE', 'templates/ft0181-owner-reask-once-message.md')
smoke_fixture = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
smoke_result = run_tool(smoke_fixture)
if smoke_result.get('outcome') != 'BLOCK-EVIDENCE' or smoke_result.get('is_real_packet') is not False:
    raise SystemExit(f'smoke fixture should be blocked by normal triage, got {smoke_result}')

archive_template_result = run_tool(TEMPLATE)
if archive_template_result.get('outcome') != 'BLOCK-EVIDENCE' or archive_template_result.get('source_truth_class') != 'SRC0-CONTROLLED-ARCHIVE':
    raise SystemExit(f'archive-controlled template CSV should be blocked by direct triage, got {archive_template_result}')
if 'archive-controlled' not in ' '.join(archive_template_result.get('reasons', [])).lower():
    raise SystemExit(f'archive-controlled template block should name the source boundary: {archive_template_result}')

print('check_owner_reply_triage: OK (blank, staged, protected, overbroad, authority, claim, small-cell, vendor-only rollback, re-ask, smoke/control-source blocks; subprocess-free)')
