#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback preserved-capture posture."""
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
    'captured_subject_preservation_posture': 'preserve-verified-capture-as-separate-evidence',
    'captured_subject_mutation_posture': 'no-in-place-overwrite-of-captured-subject',
    'later_output_relationship_posture': 'separate-derivative-from-preserved-capture',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'preserved evidence',
    'may not rewrite that capture in place',
    'separate derivative from the preserved capture',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'captured_subject_preservation_posture': 'preserve-verified-capture-as-separate-evidence',
        'captured_subject_mutation_posture': 'no-in-place-overwrite-of-captured-subject',
        'later_output_relationship_posture': 'separate-derivative-from-preserved-capture',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
if (ops[3].get('params') or {}).get('input_path') != '/work/input/preserved-subject.bin':
    errors.append(f"{plan_rel}: sanitize params.input_path must stay '/work/input/preserved-subject.bin'")
if (ops[3].get('params') or {}).get('captured_subject_mutation_posture') != 'forbidden':
    errors.append(f"{plan_rel}: sanitize params.captured_subject_mutation_posture must stay 'forbidden'")
if 'preserved capture remains exact evidence' not in (plan.get('notes') or ''):
    errors.append(f"{plan_rel}: notes missing 'preserved capture remains exact evidence'")

outputs = receipt.get('outputs') or []
subject_digest = ((receipt.get('subject') or {}).get('digest'))
cap = next((o for o in outputs if o.get('role') == 'captured-subject'), None)
san = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if cap is None:
    errors.append(f'{receipt_rel}: outputs must include role=captured-subject')
else:
    if cap.get('digest') != subject_digest:
        errors.append(f'{receipt_rel}: captured-subject digest must match subject.digest')
    if cap.get('path') == '/work/capture/subject.bin':
        errors.append(f"{receipt_rel}: captured-subject path may not stay disposable /work/capture authority")
if san is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    if san.get('source_digest') != subject_digest:
        errors.append(f'{receipt_rel}: sanitized-derivative source_digest must match subject.digest')
    if san.get('relationship') != 'derived-from-captured-subject':
        errors.append(f"{receipt_rel}: sanitized-derivative relationship must stay 'derived-from-captured-subject'")
    if san.get('path') == cap.get('path'):
        errors.append(f'{receipt_rel}: sanitized-derivative path must stay separate from preserved capture path')

if 'preserved-capture-separate-derivative' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'preserved-capture-separate-derivative'")
for token in (
    'preserved as exact evidence',
    'did not rewrite that capture in place',
    'separate derivative from the preserved capture',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md': ['verified capture remains preserved exact evidence', 'Later operations may not rewrite the preserved capture in place', 'Later outputs are separate derivatives from the preserved capture'],
    'docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md': ['preserved evidence', 'may not rewrite the preserved capture in place', 'separate derivatives from the preserved capture'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['preserved-capture cut is explicit too', 'sanitize output is a separate derivative from the preserved capture'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['preserved-capture cut is fixed too', 'docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md'],
    'docs/410-desktop-viability-checklist.md': ['preserved-capture cut is fixed too', 'docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['preserved-capture cut is fixed too', 'sanitize output becomes a separate derivative from the preserved capture'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['preserved exact evidence', 'later outputs stay separate derivatives from that preserved capture'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md'],
    'docs/110-juicy-os-lessons.md': ['preserve the verified capture as exact evidence and forbid in-place rewrite by later ops', 'docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_preserved_capture.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_preserved_capture.py'],
    'docs/00-index.md': ['docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md', 'check_removable_media_local_preserved_capture.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback preserved-capture check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback preserved-capture check passed')
