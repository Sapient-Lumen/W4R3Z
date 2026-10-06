#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback ingest member-kind floor."""
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
if constraints.get('walk_posture') != 'physical-root-pinned':
    errors.append(f'{grant_rel}: constraints.walk_posture must stay physical-root-pinned')
if constraints.get('allowed_member_kinds') != ['regular-file', 'directory']:
    errors.append(f'{grant_rel}: constraints.allowed_member_kinds must stay regular-file + directory only')
if constraints.get('unsupported_member_kind_action') != 'fail-closed':
    errors.append(f'{grant_rel}: constraints.unsupported_member_kind_action must stay fail-closed')
if constraints.get('hardlink_topology_posture') != 'not-preserved-first-cut':
    errors.append(f'{grant_rel}: constraints.hardlink_topology_posture must stay not-preserved-first-cut')
for token in ('physical and root-pinned', 'regular files plus explicit directories', 'symlink/device/FIFO/socket', 'hardlink topology'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

mount_notes = '\n'.join(mount_view.get('notes') or [])
for token in ('physical and root-pinned', 'regular files plus explicit directories', 'symlink/device/FIFO/socket', 'Hardlink topology is not preserved'):
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
    if params.get('walk_posture') != 'physical-root-pinned':
        errors.append(f'{import_rel}: classify.params.walk_posture must stay physical-root-pinned')
    if params.get('allowed_member_kinds') != ['regular-file', 'directory']:
        errors.append(f'{import_rel}: classify.params.allowed_member_kinds must stay regular-file + directory only')
    if params.get('unsupported_member_kind_action') != 'fail-closed':
        errors.append(f'{import_rel}: classify.params.unsupported_member_kind_action must stay fail-closed')
    if params.get('hardlink_topology_posture') != 'not-preserved-first-cut':
        errors.append(f'{import_rel}: classify.params.hardlink_topology_posture must stay not-preserved-first-cut')

for token in ('physical and root-pinned', 'regular files plus explicit directories', 'symlink/device/FIFO/socket semantics', 'hardlink topology'):
    if token not in (import_plan.get('notes') or ''):
        errors.append(f'{import_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md': [
        'physical', 'root-pinned', 'regular files', 'explicit directories', 'symlinks are not part of the first cut', 'hardlink topology is not preserved'
    ],
    'docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md': [
        'physical and root-pinned', 'regular files plus explicit directories', 'symlink/device/FIFO/socket semantics', 'does not preserve hardlink topology'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'physical and root-pinned beneath `/ingest`', 'regular files plus explicit directories only', 'symlink/device/FIFO/socket semantics fail closed'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'physical and root-pinned beneath `/ingest`', 'regular files plus explicit directories only', 'hardlink topology stays out of scope in the first cut'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'physical and root-pinned beneath `/ingest`', 'regular files plus explicit directories only', 'hardlink topology stays out of scope in the first cut'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'physical and root-pinned beneath `/ingest`', 'regular files plus explicit directories only', 'hardlink topology stays out of scope in the first cut'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `fts(3)`', 'FreeBSD `openat(2)`'
    ],
    'docs/110-juicy-os-lessons.md': [
        'physical and root-pinned beneath `/ingest`', 'regular-files-plus-explicit-directories only', 'hardlink topology out of scope in the first cut'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_member_kind_floor.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_member_kind_floor.py'],
    'docs/00-index.md': ['docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md', 'check_removable_media_local_member_kind_floor.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback member-kind floor check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback member-kind floor check passed')
