#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback metadata-fidelity floor."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
mount_rel = 'spec/examples/mount.view.removable-media-local-ingest.json'
import_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'

grant = load_json(grant_rel)
mount_view = load_json(mount_rel)
import_plan = load_json(import_rel)

constraints = grant.get('constraints') or {}
if constraints.get('review_identity_posture') != 'path-kind-payload-first':
    errors.append(f'{grant_rel}: constraints.review_identity_posture must stay path-kind-payload-first')
if constraints.get('filesystem_metadata_fidelity') != 'out-of-scope-first-cut':
    errors.append(f'{grant_rel}: constraints.filesystem_metadata_fidelity must stay out-of-scope-first-cut')
for token in ('path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

mount_notes = '\n'.join(mount_view.get('notes') or [])
for token in ('path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'):
    if token not in mount_notes:
        errors.append(f'{mount_rel}: notes missing {token!r}')

classify = None
for op in import_plan.get('operations') or []:
    if op.get('op') == 'classify':
        classify = op
        break
if not classify:
    errors.append(f'{import_rel}: must keep a classify operation')
else:
    params = classify.get('params') or {}
    if params.get('review_identity_posture') != 'path-kind-payload-first':
        errors.append(f'{import_rel}: classify.params.review_identity_posture must stay path-kind-payload-first')
    if params.get('filesystem_metadata_fidelity') != 'out-of-scope-first-cut':
        errors.append(f'{import_rel}: classify.params.filesystem_metadata_fidelity must stay out-of-scope-first-cut')
    if params.get('materialization_metadata_authority') != 'receiver-local-nonauthoritative':
        errors.append(f'{import_rel}: classify.params.materialization_metadata_authority must stay receiver-local-nonauthoritative')

for token in ('path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'):
    if token not in (import_plan.get('notes') or ''):
        errors.append(f'{import_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md': [
        'path/kind/payload-first', 'owner/group fidelity is **out of this lane entirely**', 'receiver-local realization detail'
    ],
    'docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md': [
        'path/kind/payload-first', 'owner/group fidelity is **out of this lane entirely**', 'filesystem-preserving archive format'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'path/kind/payload-first', 'owner/mode/mtime/xattr fidelity out of scope', 'receiver-local realization detail'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `mount_msdosfs(8)`', 'FreeBSD `mount.exfat-fuse(8)`', 'FreeBSD `mount_cd9660(8)`'
    ],
    'docs/110-juicy-os-lessons.md': [
        'owner/mode/mtime/xattr fidelity out of the first lane', 'path/kind/payload-first'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_metadata_fidelity_floor.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_metadata_fidelity_floor.py'],
    'docs/00-index.md': ['docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md', 'check_removable_media_local_metadata_fidelity_floor.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback metadata-fidelity check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback metadata-fidelity check passed')
