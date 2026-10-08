#!/usr/bin/env python3
"""Self-test the FT-0181 owner-reply workbench seed utility.

This validator used to shell out to the intake and seed CLIs three times, which
made the owner-reply lane the slowest ordinary cloudtainer loop. It now imports
the same public functions directly while preserving the release assertions.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from ft0181_validation_fixtures import build_valid_sent_contact_status  # noqa: E402
from intake_owner_reply_csv import bundle_intake  # noqa: E402
from seed_owner_packet_workbench import build_seed  # noqa: E402

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


TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'owner-reply-workbench-seed'
SOURCE_CONTACT_STATUS = TMP / 'source-contact' / 'contact-status.json'


def write_source_contact_status() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    try:
        build_valid_sent_contact_status(
            SOURCE_CONTACT_STATUS,
            root=ROOT,
            sent_date='2026-06-13',
            response_due_date='2026-06-20',
            status_date='2026-06-13',
            source_slug='workbench-seed-source-send-log',
        )
    except RuntimeError as exc:
        raise SystemExit(str(exc))


write_source_contact_status()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def cube_python():
    env = os.environ.get('CUBE_PYTHON')
    if env:
        return env
    system = Path('/usr/bin/python3')
    return str(system if system.exists() else Path(sys.executable))


def read_template_rows() -> list[dict[str, str]]:
    with TEMPLATE.open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    if not rows or set(rows[0].keys()) != set(EXPECTED_COLUMNS):
        raise SystemExit('owner reply template columns changed unexpectedly')
    return rows


def write_csv(responses: dict[str, str]) -> Path:
    rows = read_template_rows()
    for row in rows:
        row['owner_response'] = responses.get(row['row_id'], '')
    handle = tempfile.NamedTemporaryFile('w', newline='', encoding='utf-8', suffix='.csv', delete=False)
    with handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(handle.name)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def assert_no_leak(errors: list[str], text: str, context: str) -> None:
    for forbidden in ['eligible 120', 'course operations lead via', 'Human fallback is normal staff outreach', 'raw LMS telemetry is attached']:
        if forbidden in text:
            fail(errors, f'{context} leaked owner answer content: {forbidden}')


errors: list[str] = []

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    safe_path = write_csv(SAFE_RESPONSES)
    try:
        intake_dir = tmp / 'safe-intake'
        intake = bundle_intake(safe_path, intake_dir, SOURCE_CONTACT_STATUS)
    finally:
        safe_path.unlink(missing_ok=True)
    if intake.get('triage_outcome') != 'PROCEED-STAGED':
        fail(errors, f'safe intake should be PROCEED-STAGED: {intake}')
    manifest = load_json(intake_dir / 'bundle-manifest.json')
    if 'bundle_manifest' in manifest.get('artifacts', {}):
        fail(errors, 'bundle manifest must not embed its own stale hash in artifacts.bundle_manifest')
    if 'self_hash_policy' not in manifest:
        fail(errors, 'bundle manifest missing self_hash_policy')

    seed_dir = tmp / 'safe-seed'
    summary = build_seed(intake_dir, seed_dir)
    if summary.get('acceptance_state') != 'NOT_ACCEPTED':
        fail(errors, f'seed must preserve NOT_ACCEPTED state: {summary}')
    seed_path = seed_dir / 'workbench-seed.json'
    if not seed_path.exists():
        fail(errors, 'workbench seed output missing')
    seed_text = seed_path.read_text(encoding='utf-8')
    assert_no_leak(errors, seed_text, 'workbench seed')
    seed = json.loads(seed_text)
    if seed.get('required_next_surface') != 'docs/30-operations/ft0181-owner-packet-workbench.md':
        fail(errors, 'seed must point to owner packet workbench')
    if seed.get('content_minimization', {}).get('copies_owner_answers') is not False:
        fail(errors, 'seed must not copy owner answers')
    if seed.get('content_minimization', {}).get('copies_contact_details') is not False:
        fail(errors, 'seed must not copy contact details')
    if seed.get('content_minimization', {}).get('source_contact_status_revalidated') is not True:
        fail(errors, 'seed must record source contact-status revalidation')
    source_status = seed.get('source_contact_status', {})
    if source_status.get('reference') != SOURCE_CONTACT_STATUS.relative_to(ROOT).as_posix():
        fail(errors, 'seed must preserve the revalidated source contact-status reference')
    if source_status.get('revalidated_for_seed') is not True:
        fail(errors, 'seed source contact-status must be revalidated for seed')
    if source_status.get('claim_effect') != 'none; provenance gate only':
        fail(errors, 'seed source contact-status must remain provenance-only')
    for term in ['not SRC2+ acceptance', 'not custody evidence', 'not closure evidence']:
        if term not in seed.get('claim_ceiling', ''):
            fail(errors, f'seed claim ceiling missing {term}')

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    safe_path = write_csv(SAFE_RESPONSES)
    try:
        intake_dir = tmp / 'tampered-intake'
        intake = bundle_intake(safe_path, intake_dir, SOURCE_CONTACT_STATUS)
    finally:
        safe_path.unlink(missing_ok=True)
    if intake.get('triage_outcome') != 'PROCEED-STAGED':
        fail(errors, 'safe intake failed before tampered-source-clock check')
    manifest_path = intake_dir / 'bundle-manifest.json'
    manifest = load_json(manifest_path)
    manifest.pop('source_contact_status', None)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    try:
        build_seed(intake_dir, tmp / 'tampered-seed')
        fail(errors, 'tampered bundle without source_contact_status should not seed workbench')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('outcome') != 'WORKBENCH-SEED-SOURCE-CLOCK-BLOCKED':
            fail(errors, f'tampered source-clock block missing code: {payload}')

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    safe_path = write_csv(SAFE_RESPONSES)
    try:
        intake_dir = tmp / 'mismatched-intake'
        intake = bundle_intake(safe_path, intake_dir, SOURCE_CONTACT_STATUS)
    finally:
        safe_path.unlink(missing_ok=True)
    if intake.get('triage_outcome') != 'PROCEED-STAGED':
        fail(errors, 'safe intake failed before mismatched-source-clock check')
    manifest_path = intake_dir / 'bundle-manifest.json'
    manifest = load_json(manifest_path)
    manifest['source_contact_status']['response_due_date'] = '2026-06-19'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    try:
        build_seed(intake_dir, tmp / 'mismatched-seed')
        fail(errors, 'bundle with mismatched source_contact_status should not seed workbench')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('outcome') != 'WORKBENCH-SEED-SOURCE-CLOCK-BLOCKED' or 'does not match' not in payload.get('message', ''):
            fail(errors, f'mismatched source-clock block missing reason: {payload}')

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    blocked = dict(SAFE_RESPONSES)
    blocked['2'] = 'Full export with learner-level rows and raw LMS telemetry is attached.'
    blocked_path = write_csv(blocked)
    try:
        intake_dir = tmp / 'blocked-intake'
        intake = bundle_intake(blocked_path, intake_dir, SOURCE_CONTACT_STATUS)
    finally:
        blocked_path.unlink(missing_ok=True)
    if intake.get('triage_outcome') != 'BLOCK-OVERBROAD':
        fail(errors, f'blocked intake should retain BLOCK-OVERBROAD: {intake}')
    try:
        build_seed(intake_dir, tmp / 'blocked-seed')
        fail(errors, 'non-proceed intake bundle must not seed workbench')
    except ValueError as exc:
        if 'Only PROCEED-STAGED' not in str(exc):
            fail(errors, f'non-proceed seed block missing clear reason: {exc}')

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    safe_path = write_csv(SAFE_RESPONSES)
    try:
        intake_dir = tmp / 'safe-intake'
        intake = bundle_intake(safe_path, intake_dir, SOURCE_CONTACT_STATUS)
    finally:
        safe_path.unlink(missing_ok=True)
    if intake.get('triage_outcome') != 'PROCEED-STAGED':
        fail(errors, 'safe intake failed before output-block check')
    try:
        build_seed(intake_dir, ROOT / 'docs' / '00-meta' / 'forbidden-seed')
        fail(errors, 'seed output to docs should be blocked')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('outcome') != 'WORKBENCH-SEED-OUTPUT-BLOCKED':
            fail(errors, f'seed docs block missing code: {payload}')
    if (ROOT / 'docs' / '00-meta' / 'forbidden-seed').exists():
        fail(errors, 'seed output block must not create docs directory')
    try:
        build_seed(intake_dir, ROOT / 'local-owner-reply-workbench-seed')
        fail(errors, 'seed output to nonscratch archive root should be blocked')
    except ValueError as exc:
        payload = json.loads(str(exc))
        if payload.get('outcome') != 'WORKBENCH-SEED-OUTPUT-BLOCKED' or 'archive-nonscratch-output' not in payload.get('output_boundary', ''):
            fail(errors, f'seed nonscratch block missing shared boundary: {payload}')
    if (ROOT / 'local-owner-reply-workbench-seed').exists():
        fail(errors, 'seed nonscratch output block must not create root leakage directory')

if errors:
    raise SystemExit('owner reply workbench seed validation errors:\n' + '\n'.join(errors))
print('check_owner_reply_workbench_seed: OK (source-clock-gated intake, seed revalidation, manifest self-hash avoided, proceed-only seed, no answer/contact leakage, output guard, and NOT_ACCEPTED boundary)')
