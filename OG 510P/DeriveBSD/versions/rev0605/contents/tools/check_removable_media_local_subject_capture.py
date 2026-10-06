#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback selected-subject capture posture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
plan_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'
receipt_rel = 'spec/examples/content.import.receipt.removable-media-local-ingest.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
receipt = load_json(receipt_rel)

constraints = grant.get('constraints') or {}
for key, value in {
    'selected_subject_capture_posture': 'required-before-noncapture-ops',
    'captured_subject_consumer_posture': 'later-ops-read-work-capture-only',
    'capture_failure_posture': 'fail-closed-no-partial-import',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'capture-first into disposable /work staging',
    'live mounted /ingest path',
    'digest mismatch fails closed',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'source_path': '/ingest/invoice.pdf',
        'destination_path': '/work/stage/subject.bin',
        'selected_subject_capture_posture': 'required-before-noncapture-ops',
        'post_capture_consumption': 'later-ops-read-work-capture-only',
        'digest_verification': 'must-match-planned-subject-digest-before-later-ops',
        'capture_failure_posture': 'fail-closed-no-partial-import',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
classify = next((op for op in ops if op.get('op') == 'classify'), None)
if not classify:
    errors.append(f'{plan_rel}: classify operation missing')
else:
    params = classify.get('params') or {}
    if params.get('input_path') != '/work/input/preserved-subject.bin':
        errors.append(f"{plan_rel}: classify.params.input_path must stay '/work/input/preserved-subject.bin'")
    if 'input_root' in params:
        errors.append(f'{plan_rel}: classify.params.input_root must not reappear in canonical example')
for token in (
    'capture-first into disposable /work staging',
    'live mounted /ingest path',
    'digest mismatch fails closed',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

rops = receipt.get('operations') or []
if not rops or rops[0].get('op') != 'capture':
    errors.append(f'{receipt_rel}: first operation must stay capture')
else:
    if rops[0].get('status') != 'ok':
        errors.append(f'{receipt_rel}: capture status must stay ok')
    if rops[0].get('tool') != 'import.capture':
        errors.append(f"{receipt_rel}: capture tool must stay 'import.capture'")
    if rops[0].get('output_digest') != (receipt.get('subject') or {}).get('digest'):
        errors.append(f'{receipt_rel}: capture output_digest must match subject.digest')
if 'capture-first' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'capture-first'")
for token in (
    'captured into disposable /work staging',
    'live mounted /ingest path',
    'digest mismatch would have failed closed',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md': ['capture that exact subject into `/work`', 'Later operations in this first lane consume the captured file', 'digest'],
    'docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md': ['first non-browsing step must capture that exact subject into `/work`', 'later operations consume the captured bytes', 'digest verification'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['capture-first cut is explicit too', 'later operations consume the captured file'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['capture-first cut is fixed too', 'spec/examples/content.import.receipt.removable-media-local-ingest.json'],
    'docs/410-desktop-viability-checklist.md': ['capture-first cut is fixed too', 'docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['capture-first into `/work`', 'live mounted path'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['capture-first into disposable `/work` staging', 'later operations consuming the live mounted path'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md'],
    'docs/110-juicy-os-lessons.md': ['capture the exact selected subject into /work first', 'live mounted path'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_subject_capture.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_subject_capture.py'],
    'docs/00-index.md': ['docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md', 'check_removable_media_local_subject_capture.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback subject-capture check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback subject-capture check passed')
