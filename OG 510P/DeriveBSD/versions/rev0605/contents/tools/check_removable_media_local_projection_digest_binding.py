#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback digest-bound post-detach single-object delivery."""
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
detach_rel = 'spec/examples/device.detach.receipt.removable-media-local-ingest.json'
receipt_rel = 'spec/examples/content.import.receipt.removable-media-local-ingest.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
detach = load_json(detach_rel)
receipt = load_json(receipt_rel)
subject_digest = ((receipt.get('subject') or {}).get('digest'))

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_projection_binding_posture': 'must-bind-worker-delivery-to-preserved-capture-digest-before-later-ops',
    'post_detach_projection_binding_evidence': 'receipt-must-record-worker-delivery-digest-binding',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'must bind to the same preserved selected subject digest',
    'canonical receipt must record that digest-bound continuity explicitly',
    'worker-visible delivery is only synthetic plumbing',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_projection_binding_posture': 'must-bind-worker-delivery-to-preserved-capture-digest-before-later-ops',
        'post_detach_projection_binding_evidence': 'receipt-must-record-worker-delivery-digest-binding',
        'post_detach_projection_source_digest': plan.get('subject', {}).get('digest'),
        'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
for token in (
    'must bind to the preserved selected subject digest',
    'canonical receipt must record that digest-bound delivery explicitly',
    'worker-visible projection path is only plumbing',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_projection_binding_posture': 'digest-bound-to-preserved-capture-before-later-ops',
    'post_detach_projection_source_digest': subject_digest,
    'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
cap = next((o for o in outputs if o.get('role') == 'captured-subject'), None)
if cap is None:
    errors.append(f'{receipt_rel}: outputs must include role=captured-subject')
else:
    for key, value in {
        'projection_path': '/work/input/preserved-subject.bin',
        'projection_source_digest': subject_digest,
        'projection_binding_posture': 'digest-bound-before-worker-ops',
        'projection_binding_evidence': 'receipt-recorded',
    }.items():
        if cap.get(key) != value:
            errors.append(f'{receipt_rel}: captured-subject {key} must stay {value}')
    if cap.get('digest') != subject_digest:
        errors.append(f'{receipt_rel}: captured-subject digest must match subject.digest')

if 'digest-bound-projection' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'digest-bound-projection'")
for token in (
    'bound to the same preserved selected subject digest',
    'receipt records that digest-bound continuity explicitly',
    'synthetic worker-visible delivery',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md': ['single-object delivery stays digest-bound', 'receipt must say that this happened', 'path as self-authenticating'],
    'docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md': ['digest-bound and receipt-evidenced', 'worker-visible projection path or delegated read handle is only execution plumbing', 'receipt records that digest binding explicitly'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['digest-bound projection cut is explicit too', 'must match the preserved selected subject digest before later ops begin'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['digest-bound delivery cut is fixed too', 'docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md'],
    'docs/410-desktop-viability-checklist.md': ['digest-bound delivery cut is fixed too', 'receipt must say that synthetic delivery matched the preserved capture digest'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['digest-bound delivery cut is fixed too', 'must bind to the preserved selected subject digest'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['must stay digest-bound to the preserved capture', 'synthetic delivery path is only plumbing'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md'],
    'docs/110-juicy-os-lessons.md': ['make the later worker prove its one synthetic delivery matches the preserved capture digest', 'not just trust the path'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_projection_digest_binding.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_projection_digest_binding.py'],
    'docs/00-index.md': ['docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md', 'check_removable_media_local_projection_digest_binding.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback projection digest-binding check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback projection digest-binding check passed')
