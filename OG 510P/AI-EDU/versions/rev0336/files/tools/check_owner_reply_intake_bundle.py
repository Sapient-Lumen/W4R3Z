import csv
import json
import tempfile
import shutil
from pathlib import Path

from intake_owner_reply_csv import bundle_intake
from prepare_ft0181_owner_request_packet import build_packet
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION, build_send_log
from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS, build_status

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv'
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


TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'owner-reply-intake-bundle'
SOURCE_CONTACT_STATUS = TMP / 'source-contact' / 'contact-status.json'


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_source_contact_status() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    packet_dir = TMP / 'source-packet'
    packet = build_packet(
        output_dir=packet_dir,
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        return_date='2026-06-20',
        overwrite=True,
    )
    if not packet.get('ok'):
        raise SystemExit(f'source packet fixture did not build: {packet}')
    send_dir = TMP / 'owner-send-logs' / 'source-send-log'
    send_log = build_send_log(
        output_dir=send_dir,
        packet_manifest=packet_dir / 'packet-manifest.json',
        sent_date='2026-06-13',
        response_due_date='2026-06-20',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        send_channel_class='email',
        owner_route_class='accountable-owner',
        operator_confirmation=SEND_LOG_CONFIRMATION,
        overwrite=True,
    )
    if not send_log.get('ok'):
        raise SystemExit(f'source send-log fixture did not build: {send_log}')
    status = build_status(
        output_dir=SOURCE_CONTACT_STATUS.parent,
        status='sent-awaiting-reply',
        service_label='AIEDU-SR-003 draft reminder pilot',
        owner_role='accountable service owner route',
        source_record_set='owner-maintained local service record set',
        date_range='2026-06-01 through 2026-06-07',
        sent_date='2026-06-13',
        response_due_date='2026-06-20',
        status_date='2026-06-13',
        attempt_count=1,
        operator_confirmation=OPERATOR_CONFIRMATIONS['sent-awaiting-reply'],
        source_artifact=rel(send_dir / 'send-log.json'),
        overwrite=True,
    )
    if not status.get('ok'):
        raise SystemExit(f'source contact-status fixture did not build: {status}')


write_source_contact_status()


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


class Proc:
    def __init__(self, returncode, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_intake(path, output_dir=None, source_contact_status=SOURCE_CONTACT_STATUS):
    try:
        result = bundle_intake(Path(path), Path(output_dir) if output_dir else None, source_contact_status)
        return Proc(0, json.dumps(result, indent=2) + '\n')
    except ValueError as exc:
        return Proc(2, str(exc) + '\n')


def assert_no_leak(text, context):
    for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached']:
        if forbidden in text:
            raise SystemExit(f'{context} leaked owner answer content: {forbidden}')


if not SMOKE_FIXTURE.exists():
    raise SystemExit('synthetic smoke fixture missing')

safe_path = write_csv(SAFE_RESPONSES)
try:
    proc = run_intake(safe_path, tempfile.mkdtemp(), source_contact_status=None)
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2 or 'INTAKE-SOURCE-PROVENANCE-BLOCKED' not in proc.stdout:
    raise SystemExit(f'intake without source provenance should block: {proc.stdout}')

with tempfile.TemporaryDirectory() as tmp:
    safe_path = write_csv(SAFE_RESPONSES)
    out_dir = Path(tmp) / 'safe-intake'
    try:
        proc = run_intake(safe_path, out_dir)
    finally:
        safe_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise SystemExit(f'safe intake failed:\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}')
    summary = json.loads(proc.stdout)
    if summary.get('triage_outcome') != 'PROCEED-STAGED':
        raise SystemExit(f'safe intake should proceed-staged: {summary}')
    for name in ['receipt.json', 'triage.json', 'proceed-staged.md', 'bundle-manifest.json']:
        if not (out_dir / name).exists():
            raise SystemExit(f'safe intake missing output {name}')
    receipt_text = (out_dir / 'receipt.json').read_text(encoding='utf-8')
    triage_text = (out_dir / 'triage.json').read_text(encoding='utf-8')
    manifest_text = (out_dir / 'bundle-manifest.json').read_text(encoding='utf-8')
    assert_no_leak(receipt_text, 'receipt')
    assert_no_leak(triage_text, 'triage')
    assert_no_leak(manifest_text, 'manifest')
    manifest = json.loads(manifest_text)
    if manifest.get('bundle_type') != 'FT-0181-owner-reply-local-intake-bundle':
        raise SystemExit('manifest bundle_type mismatch')
    if manifest.get('content_minimization', {}).get('archive_controlled_output_allowed') is not False:
        raise SystemExit('manifest must forbid archive-controlled output')
    if manifest.get('claim_ceiling', '').lower().count('not ') < 4:
        raise SystemExit('manifest claim ceiling too weak')
    if manifest.get('source_contact_status', {}).get('reference') != SOURCE_CONTACT_STATUS.relative_to(ROOT).as_posix():
        raise SystemExit('manifest must preserve the active source contact-status reference')
    if manifest.get('content_minimization', {}).get('source_contact_status_required') is not True:
        raise SystemExit('manifest must record source-contact-status/post-readout-context provenance gate')
    stage_text = (out_dir / 'proceed-staged.md').read_text(encoding='utf-8')
    for term in ['PROCEED-STAGED', 'Source CSV SHA-256:', 'not closure evidence']:
        if term not in stage_text:
            raise SystemExit(f'stage note missing {term}')

with tempfile.TemporaryDirectory() as tmp:
    blocked = dict(SAFE_RESPONSES)
    blocked['2'] = 'Full export with learner-level rows and raw LMS telemetry is attached.'
    blocked_path = write_csv(blocked)
    out_dir = Path(tmp) / 'blocked-intake'
    try:
        proc = run_intake(blocked_path, out_dir)
    finally:
        blocked_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise SystemExit(f'blocked intake should route locally rather than fail: {proc.stdout} {proc.stderr}')
    summary = json.loads(proc.stdout)
    if summary.get('triage_outcome') != 'BLOCK-OVERBROAD':
        raise SystemExit(f'blocked intake should retain BLOCK-OVERBROAD: {summary}')
    if (out_dir / 'proceed-staged.md').exists():
        raise SystemExit('blocked intake must not create proceed-staged note')
    if not (out_dir / 'outcome-note.md').exists():
        raise SystemExit('blocked intake must create local outcome note')
    assert_no_leak((out_dir / 'receipt.json').read_text(encoding='utf-8'), 'blocked receipt')
    assert_no_leak((out_dir / 'bundle-manifest.json').read_text(encoding='utf-8'), 'blocked manifest')
    if 'local routing artifact' not in (out_dir / 'outcome-note.md').read_text(encoding='utf-8'):
        raise SystemExit('blocked outcome note missing local routing boundary')

proc = run_intake(SMOKE_FIXTURE)
if proc.returncode != 2:
    raise SystemExit(f'smoke intake should be blocked, got {proc.returncode}: {proc.stdout}')
for term in ['SRC0-RECEIPT-BLOCKED', 'SRC0-SMOKE', 'make owner-reply-smoke']:
    if term not in proc.stdout:
        raise SystemExit(f'smoke intake block missing {term}: {proc.stdout}')

with tempfile.TemporaryDirectory() as tmp:
    out_dir = Path(tmp) / 'template-intake-should-not-exist'
    proc = run_intake(TEMPLATE, out_dir)
    if proc.returncode != 2:
        raise SystemExit(f'archive-controlled template intake should be blocked, got {proc.returncode}: {proc.stdout}')
    for term in ['RETURNED-CSV-SOURCE-BLOCKED', 'SRC0-CONTROLLED-ARCHIVE', 'make owner-field-next']:
        if term not in proc.stdout:
            raise SystemExit(f'template intake source block missing {term}: {proc.stdout}')
    if out_dir.exists():
        raise SystemExit('template intake source block must not create an output directory')

safe_path = write_csv(SAFE_RESPONSES)
try:
    proc = run_intake(safe_path, ROOT / 'docs' / '00-meta' / 'forbidden-intake-bundle')
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'intake output to docs should be blocked, got {proc.returncode}: {proc.stdout}')
if (ROOT / 'docs' / '00-meta' / 'forbidden-intake-bundle').exists():
    raise SystemExit('intake output block must not create docs directory')
if 'INTAKE-OUTPUT-BLOCKED' not in proc.stdout:
    raise SystemExit(f'intake docs block missing code: {proc.stdout}')

safe_path = write_csv(SAFE_RESPONSES)
try:
    proc = run_intake(safe_path, ROOT / 'local-owner-reply-intake')
finally:
    safe_path.unlink(missing_ok=True)
if proc.returncode != 2:
    raise SystemExit(f'intake output to nonscratch archive root should be blocked, got {proc.returncode}: {proc.stdout}')
if (ROOT / 'local-owner-reply-intake').exists():
    raise SystemExit('intake nonscratch output block must not create root leakage directory')
if 'archive-nonscratch-output' not in proc.stdout:
    raise SystemExit(f'intake nonscratch block missing shared boundary: {proc.stdout}')

print('check_owner_reply_intake_bundle: OK (subprocess-free receipt/triage/stage bundle, source-contact-status/post-readout-context provenance gate, block routing, smoke/control-source block, archive-output block, and no metadata leakage)')
