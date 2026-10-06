#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback inert mount posture."""
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
if constraints.get('required_mount_flags') != ['ro', 'nodev', 'nosuid', 'noexec', 'nosymfollow']:
    errors.append(f'{grant_rel}: constraints.required_mount_flags must stay the reviewed inert-mount tuple')
if constraints.get('mount_flag_posture') != 'fail-closed-if-unavailable':
    errors.append(f'{grant_rel}: constraints.mount_flag_posture must stay fail-closed-if-unavailable')
if constraints.get('mounted_tree_posture') != 'inert-input-only':
    errors.append(f'{grant_rel}: constraints.mounted_tree_posture must stay inert-input-only')
if constraints.get('side_effect_metadata_posture') != 'bytes-only-no-autorun':
    errors.append(f'{grant_rel}: constraints.side_effect_metadata_posture must stay bytes-only-no-autorun')
notes = constraints.get('notes') or ''
for token in ('ro/nodev/nosuid/noexec/nosymfollow', 'inert input only'):
    if token not in notes:
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

mount_notes = '\n'.join(mount_view.get('notes') or [])
for token in ('inert input only', 'not a direct execution or document-open source', 'ro/nodev/nosuid/noexec/nosymfollow', 'fails closed'):
    if token not in mount_notes:
        errors.append(f'{mount_rel}: notes missing {token!r}')

import_notes = import_plan.get('notes') or ''
for token in ('inert input only', 'no direct host-open or execution from the mounted tree'):
    if token not in import_notes:
        errors.append(f'{import_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md': [
        '`nodev`', '`nosuid`', '`noexec`', '`nosymfollow`', 'inert input', 'bytes, not instructions'
    ],
    'docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md': [
        '`ro,nodev,nosuid,noexec,nosymfollow`', 'inert input only', 'fails closed', '`autorun.inf`'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'required hardening tuple `ro,nodev,nosuid,noexec,nosymfollow`', 'mounted tree stays inert input only'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        '`ro,nodev,nosuid,noexec,nosymfollow`', 'inert input only'
    ],
    'docs/410-desktop-viability-checklist.md': [
        '`ro,nodev,nosuid,noexec,nosymfollow`', 'treat the mounted tree as inert input only'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        '`ro,nodev,nosuid,noexec,nosymfollow`', 'side-effect launch metadata stays bytes only'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `mount(8)`', '`noexec`', '`nosuid`', '`nosymfollow`'
    ],
    'docs/110-juicy-os-lessons.md': [
        '`ro,nodev,nosuid,noexec,nosymfollow`', 'side-effect launch metadata on the medium as bytes'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_mount_hardening.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_mount_hardening.py'],
    'docs/00-index.md': ['docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md', 'check_removable_media_local_mount_hardening.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback mount-hardening check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback mount-hardening check passed')
