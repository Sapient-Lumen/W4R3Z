import csv
import json
import tempfile
from pathlib import Path

from ft0181_field_guards import output_allowed
from receipt_owner_reply_csv import build_receipt

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_TOOL = ROOT / 'tools' / 'receipt_owner_reply_csv.py'
TEMPLATE = ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv'
SMOKE_FIXTURE = ROOT / 'fixtures' / 'owner-reply-pipeline' / 'ft0181-proceed-staged-smoke.csv'
EXPECTED_COLUMNS = ['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note']

SAFE_RESPONSES = {
    '1': 'AIEDU-SR-003 capped draft-reminder workflow; course operations lead; local reminder queue; 2026-05-01 to 2026-05-31.',
    '2': 'Aggregate counts above local threshold: eligible 120, draft-reminder 43, human-sent 31, discarded 12, fallback/manual route 5, corrections 2, incidents 0.',
    '3': 'Draft-only queue note; no automatic send; no durable write or posting; no penalty or grading effect; no protected-status inference.',
    '4': 'Human fallback is normal staff outreach; rollback owner is course operations lead; incident class labels none; stop if fallback count spikes or any penalty route appears.',
    '5': 'Workload signal unknown for first packet; method not yet instrumented beyond owner estimate.',
    '6': 'Guidance note: staff received short local workflow guidance owned by course operations; no named staff evaluation attached.',
    '7': 'Public claim ceiling: process-only staging note; do not claim learning, safety, access, workload, compliance, scale, or effectiveness.',
    '8': 'Real owner-attested operational aggregate; raw learner data, protected facts, small cells, gradebook rows, messages, and security details were removed, withheld, or kept local.',
}


class Proc:
    def __init__(self, returncode, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def read_template_rows():
    with TEMPLATE.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    if not rows or set(rows[0].keys()) != set(EXPECTED_COLUMNS):
        raise SystemExit('owner reply template columns changed unexpectedly')
    return rows


def write_csv(responses):
    rows = read_template_rows()
    for row in rows:
        row['owner_response'] = responses.get(row['row_id'], '')
    handle = tempfile.NamedTemporaryFile('w', newline='', encoding='utf-8', suffix='.csv', delete=False)
    with handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(handle.name)


def run_receipt(path, output=None, allow_src0_smoke=False):
    try:
        receipt = build_receipt(Path(path), allow_src0_smoke=allow_src0_smoke)
        text = json.dumps(receipt, indent=2) + '\n'
        if output:
            out = Path(output)
            out = out if out.is_absolute() else ROOT / out
            allowed, output_boundary = output_allowed(out, archive_root=ROOT)
            if not allowed:
                raise ValueError(json.dumps({
                    'ok': False,
                    'outcome': 'RECEIPT-OUTPUT-BLOCKED',
                    'output_boundary': output_boundary,
                    'message': 'Owner-reply receipts are local/scratch metadata and cannot be written into the release archive outside scratch or to controlled release surfaces.',
                    'claim_ceiling': receipt['claim_ceiling'],
                }, indent=2))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding='utf-8')
            return Proc(0, out.as_posix() + '\n')
        return Proc(0, text)
    except ValueError as exc:
        return Proc(2, str(exc) + '\n')


if not RECEIPT_TOOL.exists():
    raise SystemExit('receipt_owner_reply_csv.py missing')
if not SMOKE_FIXTURE.exists():
    raise SystemExit('synthetic smoke fixture missing')

safe_path = write_csv(SAFE_RESPONSES)
try:
    proc = run_receipt(safe_path)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 0:
    raise SystemExit(f'safe receipt failed:\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}')
receipt = json.loads(proc.stdout)
if receipt.get('receipt_type') != 'FT-0181-owner-reply-local-receipt':
    raise SystemExit('receipt_type mismatch')
if receipt.get('source_truth_class') != 'UNVERIFIED-OWNER-REPLY':
    raise SystemExit(f'wrong source_truth_class: {receipt}')
if receipt.get('triage', {}).get('outcome') != 'PROCEED-STAGED':
    raise SystemExit(f'safe receipt should triage PROCEED-STAGED: {receipt}')
if receipt.get('content_minimization', {}).get('raw_owner_answers_copied') is not False:
    raise SystemExit('receipt must not copy raw owner answers')
for forbidden in ['eligible 120', 'course operations lead', 'human fallback is normal staff outreach']:
    if forbidden in proc.stdout:
        raise SystemExit(f'receipt leaked owner answer content: {forbidden}')
for required in ['sha256', 'row_count', 'owner_response_nonempty_count', 'Local receipt only', 'ft0181_status']:
    if required not in proc.stdout:
        raise SystemExit(f'receipt output missing {required}')

proc = run_receipt(SMOKE_FIXTURE)
if proc.returncode != 2:
    raise SystemExit(f'smoke fixture receipt should be blocked, got {proc.returncode}: {proc.stdout}')
for term in ['SRC0-RECEIPT-BLOCKED', 'SRC0-SMOKE', 'make owner-reply-smoke']:
    if term not in proc.stdout:
        raise SystemExit(f'smoke receipt block missing {term}: {proc.stdout}')

proc = run_receipt(TEMPLATE)
if proc.returncode != 2:
    raise SystemExit(f'archive-controlled template receipt should be blocked, got {proc.returncode}: {proc.stdout}')
for term in ['RETURNED-CSV-SOURCE-BLOCKED', 'SRC0-CONTROLLED-ARCHIVE', 'make owner-field-next']:
    if term not in proc.stdout:
        raise SystemExit(f'template receipt source block missing {term}: {proc.stdout}')

safe_path = write_csv(SAFE_RESPONSES)
out = Path(tempfile.NamedTemporaryFile(suffix='.json', delete=True).name)
try:
    proc = run_receipt(safe_path, out)
    if proc.returncode != 0 or not out.exists():
        raise SystemExit(f'--output receipt failed: {proc.stdout} {proc.stderr}')
    written = json.loads(out.read_text(encoding='utf-8'))
    if written.get('triage', {}).get('outcome') != 'PROCEED-STAGED':
        raise SystemExit('written receipt lost triage outcome')
finally:
    safe_path.unlink(missing_ok=True)
    out.unlink(missing_ok=True)

safe_path = write_csv(SAFE_RESPONSES)
forbidden_out = ROOT / 'docs' / '00-meta' / 'forbidden-owner-reply-receipt.json'
try:
    proc = run_receipt(safe_path, forbidden_out)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'receipt output to docs should return 2, got {proc.returncode}: {proc.stdout}')
if forbidden_out.exists():
    raise SystemExit('receipt output block must not create docs receipt')
if 'RECEIPT-OUTPUT-BLOCKED' not in proc.stdout:
    raise SystemExit(f'receipt docs block missing code: {proc.stdout}')

safe_path = write_csv(SAFE_RESPONSES)
leak_out = ROOT / 'local-owner-reply-receipt.json'
try:
    proc = run_receipt(safe_path, leak_out)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'receipt output to nonscratch archive root should return 2, got {proc.returncode}: {proc.stdout}')
if leak_out.exists():
    raise SystemExit('receipt nonscratch output block must not create root leakage file')
if 'archive-nonscratch-output' not in proc.stdout:
    raise SystemExit(f'receipt nonscratch block missing shared boundary: {proc.stdout}')

blocked = dict(SAFE_RESPONSES)
blocked['2'] = 'Full export with learner-level rows and raw LMS telemetry is attached.'
blocked_path = write_csv(blocked)
try:
    proc = run_receipt(blocked_path)
finally:
    blocked_path.unlink(missing_ok=True)
if proc.returncode != 0:
    raise SystemExit(f'blocked-content receipt should still produce metadata receipt: {proc.stdout}')
blocked_receipt = json.loads(proc.stdout)
if blocked_receipt.get('triage', {}).get('outcome') != 'BLOCK-OVERBROAD':
    raise SystemExit(f'blocked receipt should retain BLOCK-OVERBROAD triage: {blocked_receipt}')
if 'Full export' in proc.stdout or 'learner-level rows' in proc.stdout:
    raise SystemExit('blocked receipt leaked blocked owner response content')

print('check_owner_reply_receipt: OK (subprocess-free local receipt, content minimization, smoke/control-source block, output block, and blocked-content metadata)')
