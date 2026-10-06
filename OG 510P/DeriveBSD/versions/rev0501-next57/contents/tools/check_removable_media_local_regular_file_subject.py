#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback regular-file-only selected-subject floor."""
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
    if params.get('selected_subject_kind') != 'regular-file-only-first-cut':
        errors.append(f'{plan_rel}: classify.params.selected_subject_kind must stay regular-file-only-first-cut')
    if params.get('directory_subject_import_posture') != 'not-in-this-lane':
        errors.append(f'{plan_rel}: classify.params.directory_subject_import_posture must stay not-in-this-lane')

for token in ('selected subject stays regular-file-only in the first cut', 'directories are not selectable import subjects in this lane', 'one selected regular file'):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

constraints = grant.get('constraints') or {}
if constraints.get('selected_subject_kind') != 'regular-file-only-first-cut':
    errors.append(f'{grant_rel}: constraints.selected_subject_kind must stay regular-file-only-first-cut')
if constraints.get('directory_subject_import_posture') != 'not-in-this-lane':
    errors.append(f'{grant_rel}: constraints.directory_subject_import_posture must stay not-in-this-lane')
for token in ('selected subject stays regular-file-only in the first cut', 'directories are not selectable import subjects in this lane'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

if receipt.get('subject', {}).get('filename') != 'invoice.pdf':
    errors.append(f'{receipt_rel}: example subject.filename must stay invoice.pdf')
if receipt.get('result', {}).get('message') is None or 'regular-file-only' not in receipt.get('result', {}).get('message', ''):
    errors.append(f'{receipt_rel}: result.message must mention regular-file-only')
meta_notes = (receipt.get('metadata') or {}).get('notes') or ''
for token in ('regular-file-only', 'directories are not selectable import subjects in this lane'):
    if token not in meta_notes:
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane', 'one selected regular file'
    ],
    'docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane', 'reviewed finite-collection handoff'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects in this lane'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md'
    ],
    'docs/110-juicy-os-lessons.md': [
        'regular-file-only in the first cut', 'directories are not selectable import subjects'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `file(1)`', 'FreeBSD `bsdtar(1)`'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_regular_file_subject.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_regular_file_subject.py'],
    'docs/00-index.md': ['docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md', 'check_removable_media_local_regular_file_subject.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback regular-file-only selected-subject check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback regular-file-only selected-subject check passed')
