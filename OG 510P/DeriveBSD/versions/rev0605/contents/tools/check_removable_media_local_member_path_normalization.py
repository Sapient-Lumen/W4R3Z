#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback member-path normalization floor."""
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
if constraints.get('member_path_normalization') != 'relative-clean-nfc':
    errors.append(f'{grant_rel}: constraints.member_path_normalization must stay relative-clean-nfc')
if constraints.get('member_path_collision_action') != 'fail-closed':
    errors.append(f'{grant_rel}: constraints.member_path_collision_action must stay fail-closed')
if constraints.get('member_path_repair_posture') != 'no-silent-auto-rename':
    errors.append(f'{grant_rel}: constraints.member_path_repair_posture must stay no-silent-auto-rename')
for token in ('relative-clean Unicode NFC', 'normalization collisions fail closed', 'no silent auto-rename'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

mount_notes = '\n'.join(mount_view.get('notes') or [])
for token in ('relative-clean Unicode NFC', 'normalization collisions fail closed', 'no silent auto-rename'):
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
    if params.get('member_path_normalization') != 'relative-clean-nfc':
        errors.append(f'{import_rel}: classify.params.member_path_normalization must stay relative-clean-nfc')
    if params.get('member_path_collision_action') != 'fail-closed':
        errors.append(f'{import_rel}: classify.params.member_path_collision_action must stay fail-closed')
    if params.get('member_path_repair_posture') != 'no-silent-auto-rename':
        errors.append(f'{import_rel}: classify.params.member_path_repair_posture must stay no-silent-auto-rename')

for token in ('relative-clean Unicode NFC', 'normalization collisions fail closed', 'no silent auto-rename'):
    if token not in (import_plan.get('notes') or ''):
        errors.append(f'{import_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md': [
        'Unicode NFC', '`/` is the only separator', 'fail closed', 'does not silently auto-rename'
    ],
    'docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md': [
        'relative-clean Unicode NFC', 'collision-fail-closed', 'no silent auto-rename', '`/` is the only separator'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'relative-clean Unicode NFC text', 'normalization collisions fail closed', 'no silent auto-rename or source-prefix repair'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'relative-clean Unicode NFC text', 'normalization collisions fail closed', 'no silent auto-rename or source-prefix repair'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'relative-clean Unicode NFC text', 'normalization collisions fail closed', 'no silent auto-rename or source-prefix repair'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'relative-clean Unicode NFC text', 'normalization collisions fail closed', 'no silent auto-rename or source-prefix repair'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `mount_msdosfs(8)`', 'FreeBSD `mount.exfat-fuse(8)`', 'FreeBSD `mount_cd9660(8)`'
    ],
    'docs/110-juicy-os-lessons.md': [
        'relative-clean Unicode NFC', 'collision-fail-closed', 'no silent auto-rename or source-prefix repair'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_member_path_normalization.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_member_path_normalization.py'],
    'docs/00-index.md': ['docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md', 'check_removable_media_local_member_path_normalization.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback member-path normalization check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback member-path normalization check passed')
