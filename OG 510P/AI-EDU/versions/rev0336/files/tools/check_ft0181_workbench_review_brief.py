#!/usr/bin/env python3
"""Validate FT-0181 workbench-review brief bridge."""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path

from ft0181_validation_fixtures import build_valid_sent_contact_status
from prepare_ft0181_workbench_review_brief import build_review_brief
from run_ft0181_returned_reply_work import build_returned_reply_work

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'scratch' / 'field' / 'ft0181' / 'validation' / 'ft0181-workbench-review-brief'


def fail(msg: str) -> None:
    raise SystemExit(f'check_ft0181_workbench_review_brief: FAIL: {msg}')


def write_contact_status(path: Path) -> Path:
    try:
        return build_valid_sent_contact_status(path, root=ROOT)
    except RuntimeError as exc:
        fail(str(exc))


def write_owner_csv(path: Path) -> Path:
    rows = [
        ['1', 'Selected service / owner path / source / date range', 'AIEDU-SR-003 draft reminder pilot; accountable owner route; owner-maintained local service record set; 2026 spring pilot.', 'no raw/protected data', ''],
        ['2', 'Aggregate workflow counts', '12 aggregate draft reminder candidates, 9 human reviewed, 0 automatic sends; no learner-level rows included.', 'aggregate only', ''],
        ['3', 'Action boundary', 'Draft queue note only; no automatic send; no durable write; no penalty and no grade effect; no protected status inference.', 'authority bounded', ''],
        ['4', 'Fallback / rollback / stop condition', 'Local owner can stop the workflow and roll back draft queue rules; human fallback exists.', 'local rollback owner', ''],
        ['5', 'Workload signal', 'Staff review burden observed as aggregate routing time only; no claim of workload reduction.', 'aggregate signal only', ''],
        ['6', 'Training or use guidance', 'Training guidance tells staff to review drafts manually and keep protected facts local.', 'guidance only', ''],
        ['7', 'Public claim ceiling', 'No claim of learning, safety, access, workload, compliance, scale, or effectiveness is supported.', 'claim ceiling', ''],
        ['8', 'Redaction and owner attestation', 'Owner attests this is real operational material with raw, protected, small-cell, and security material withheld and kept local.', 'redacted owner attestation', ''],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note'])
        writer.writerows(rows)
    return path


if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)
EXTERNAL_CSV_DIR = Path(tempfile.mkdtemp(prefix='ft0181-owner-reply-check-'))

contact = write_contact_status(TMP / 'owner-contact-status' / 'sent' / 'contact-status.json')
csv_path = write_owner_csv(EXTERNAL_CSV_DIR / 'owner-reply.csv')
session = build_returned_reply_work(
    csv_path=csv_path,
    source_contact_status=contact,
    output_dir=TMP / 'sessions' / 'returned-work',
    intake_dir=TMP / 'owner-reply-intakes' / 'proceed',
    seed_dir=TMP / 'owner-reply-workbench-seeds' / 'proceed',
    review_brief_dir=TMP / 'owner-workbench-review-briefs' / 'from-returned-work',
    overwrite=True,
)
if not session.get('ok'):
    fail(f'returned-reply work should prepare a review brief: {session}')
if session.get('session_state') != 'review-brief-created-human-review-required':
    fail(f'returned-reply work should stop at human review with a review brief: {session.get("session_state")}')
brief_result = session.get('review_brief_result') or {}
if brief_result.get('review_effect') != 'does_not_record_review':
    fail('review brief must not record or simulate human review')
brief_path = ROOT / brief_result.get('brief_path', '')
summary_path = ROOT / brief_result.get('summary_path', '')
if not brief_path.exists() or not summary_path.exists():
    fail('review brief artifacts missing')
combined = brief_path.read_text(encoding='utf-8') + '\n' + summary_path.read_text(encoding='utf-8')
for forbidden in ['Draft queue note only', 'Owner attests this is real operational material', '12 aggregate draft reminder candidates']:
    if forbidden in combined:
        fail('review brief must not copy owner answer text: ' + forbidden)
for required in ['make owner-workbench-review', 'DECISION=proceed-decision-board', 'DECISION=reask-owner', 'CONFIRM=human-reviewed-minimized-workbench-record']:
    if required not in combined:
        fail('review brief missing bounded command skeleton: ' + required)

seed_path = ROOT / (session.get('seed_result') or {}).get('seed_path', '')
direct = build_review_brief(seed=seed_path, output_dir=TMP / 'owner-workbench-review-briefs' / 'direct', overwrite=True)
if not direct.get('ok') or direct.get('outcome') != 'WORKBENCH-REVIEW-BRIEF-PREPARED':
    fail(f'direct review brief should build: {direct}')
if direct.get('evidence_state') != 'not_evidence' or direct.get('closure_effect') != 'does_not_close_ft0181':
    fail('direct review brief must preserve not-evidence/no-closure boundary')

try:
    build_review_brief(seed=seed_path, output_dir=ROOT / 'docs' / 'bad-review-brief-output', overwrite=True)
except ValueError as exc:
    if 'WORKBENCH-REVIEW-BRIEF-OUTPUT-BLOCKED' not in str(exc):
        fail(f'archive output should be blocked with the expected outcome, got: {exc}')
else:
    fail('review brief wrote into docs/ unexpectedly')

tampered_dir = TMP / 'owner-reply-workbench-seeds' / 'tampered'
tampered_dir.mkdir(parents=True, exist_ok=True)
tampered_seed = tampered_dir / 'workbench-seed.json'
seed_data = json.loads(seed_path.read_text(encoding='utf-8'))
seed_data['acceptance_state'] = 'ACCEPTED'
tampered_seed.write_text(json.dumps(seed_data, indent=2) + '\n', encoding='utf-8')
try:
    build_review_brief(seed=tampered_seed, output_dir=TMP / 'owner-workbench-review-briefs' / 'tampered', overwrite=True)
except ValueError as exc:
    if 'WORKBENCH-REVIEW-BRIEF-SEED-BLOCKED' not in str(exc):
        fail(f'tampered seed should be seed-blocked, got: {exc}')
else:
    fail('review brief accepted a tampered/accepted seed')

print('check_ft0181_workbench_review_brief: OK')
