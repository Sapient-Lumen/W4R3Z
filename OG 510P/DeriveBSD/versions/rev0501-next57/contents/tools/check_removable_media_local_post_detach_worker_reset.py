#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback post-detach fresh-worker posture."""
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

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_execution_posture': 'fresh-worker-before-later-ops',
    'post_detach_ingest_visibility': 'ingest-absent-in-later-worker',
    'post_detach_reference_carryover': 'no-inherited-ingest-fd-cwd-root',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'fresh post-detach worker',
    '/ingest absent',
    'no inherited file-descriptor/current-working-directory/root references',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_execution_posture': 'fresh-worker-before-later-ops',
        'post_detach_ingest_visibility': 'ingest-absent-in-later-worker',
        'post_detach_reference_carryover': 'no-inherited-ingest-fd-cwd-root',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
for token in (
    'fresh post-detach worker',
    '/ingest absent',
    'no inherited file-descriptor/current-working-directory/root references',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

runtime = (detach.get('runtime') or {})
mapping = runtime.get('mapping') or {}
for key, value in {
    'post_detach_execution_posture': 'fresh-worker-before-later-ops',
    'post_detach_ingest_visibility': 'ingest-absent-in-later-worker',
    'post_detach_reference_carryover': 'no-inherited-ingest-fd-cwd-root',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

if 'fresh-worker-after-detach' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'fresh-worker-after-detach'")
for token in (
    'fresh post-detach worker',
    '/ingest absent',
    'no inherited file-descriptor/current-working-directory/root references',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md': ['fresh worker before later ops', '/ingest absent', 'file-descriptor, current-working-directory, root-directory, or jail-root references'],
    'docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md': ['fresh disposable worker', '/ingest is gone from the later worker entirely', 'No live ingest references may carry over'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['post-detach execution cut is explicit too', 'fresh disposable worker after verified capture and detach'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['post-detach worker-reset cut is fixed too', 'docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md'],
    'docs/410-desktop-viability-checklist.md': ['post-detach worker-reset cut is fixed too', 'docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['post-detach worker-reset cut is fixed too', 'fresh disposable worker with /ingest absent'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['fresh worker after detach', '/ingest absent'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md'],
    'docs/110-juicy-os-lessons.md': ['restart later ops in a fresh disposable worker after detach', 'no inherited cwd/root/fd references'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_post_detach_worker_reset.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_post_detach_worker_reset.py'],
    'docs/00-index.md': ['docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md', 'check_removable_media_local_post_detach_worker_reset.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback post-detach fresh-worker check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback post-detach fresh-worker check passed')
