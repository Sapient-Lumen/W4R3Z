#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback single-selected-subject floor."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


errors: list[str] = []

plan_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'
receipt_rel = 'spec/examples/content.import.receipt.removable-media-local-ingest.json'
grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'

plan = load_json(plan_rel)
receipt = load_json(receipt_rel)
grant = load_json(grant_rel)

classify = None
for op in plan.get('operations') or []:
    if op.get('op') == 'classify':
        classify = op
        break
if not classify:
    errors.append(f'{plan_rel}: must keep a classify operation')
else:
    params = classify.get('params') or {}
    if params.get('selection_width') != 'single-selected-subject-only-first-cut':
        errors.append(f'{plan_rel}: classify.params.selection_width must stay single-selected-subject-only-first-cut')
    if params.get('multi_member_review_import_posture') != 'later-explicit-lane-required':
        errors.append(f'{plan_rel}: classify.params.multi_member_review_import_posture must stay later-explicit-lane-required')

for token in ('single-selected-subject only', 'direct multi-member review/import is out of scope in the first cut', 'deterministic consequence of processing that one selected subject'):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

constraints = grant.get('constraints') or {}
if constraints.get('selection_width') != 'single-selected-subject-only-first-cut':
    errors.append(f'{grant_rel}: constraints.selection_width must stay single-selected-subject-only-first-cut')
if constraints.get('multi_member_review_import_posture') != 'later-explicit-lane-required':
    errors.append(f'{grant_rel}: constraints.multi_member_review_import_posture must stay later-explicit-lane-required')
for token in ('single-selected-subject only', 'direct multi-member review/import is out of scope in the first cut'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

if receipt.get('subject', {}).get('filename') != 'invoice.pdf':
    errors.append(f'{receipt_rel}: example subject.filename must stay invoice.pdf')
if receipt.get('result', {}).get('message') is None or 'single-selected-subject' not in receipt.get('result', {}).get('message', ''):
    errors.append(f'{receipt_rel}: result.message must mention single-selected-subject')
if len(receipt.get('outputs') or []) < 1:
    errors.append(f'{receipt_rel}: outputs must stay non-empty')
meta_notes = (receipt.get('metadata') or {}).get('notes') or ''
for token in ('single-selected-subject only', 'later explicit lane'):
    if token not in meta_notes:
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md': [
        'single-selected-subject only', 'direct multi-member review/import is out of scope in the first cut', 'deterministic consequence of processing that one selected subject'
    ],
    'docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md': [
        'single-selected-subject only', 'direct multi-member review/import is out of scope in the first cut', 'content.import.receipt.outputs[]'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'single-selected-subject only', 'direct multi-member review/import is out of scope in the first cut'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'single-selected-subject only', 'later explicit lane'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'single-selected-subject only', 'later explicit lane'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'single-selected-subject only', 'later explicit lane'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md'
    ],
    'docs/110-juicy-os-lessons.md': [
        'single-selected-subject only', 'multi-member review/import'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_single_subject.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_single_subject.py'],
    'docs/00-index.md': ['docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md', 'check_removable_media_local_single_subject.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback single-selected-subject check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback single-selected-subject check passed')
