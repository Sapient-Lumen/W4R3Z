#!/usr/bin/env python3
"""Guardrail for first-cut removable-media local-fallback filesystem admission."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


errors: list[str] = []

profile_rel = 'spec/examples/device.profile.removable-media-local-ingest.exfat.json'
grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
mount_rel = 'spec/examples/mount.view.removable-media-local-ingest.json'
import_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'

profile = load_json(profile_rel)
grant = load_json(grant_rel)
mount_view = load_json(mount_rel)
import_plan = load_json(import_rel)

risk_tags = profile.get('risk_tags') or []
for tag in ('removable-media', 'filesystem-parsed', 'local-fallback-ingest', 'quarantine-first'):
    if tag not in risk_tags:
        errors.append(f'{profile_rel}: risk_tags must include {tag!r}')
if profile.get('class') != 'storage':
    errors.append(f'{profile_rel}: class must stay storage')
if 'fstyp' not in (profile.get('notes') or '') or 'exfat' not in (profile.get('notes') or ''):
    errors.append(f'{profile_rel}: notes must mention fstyp and exfat for the canonical admitted example')

constraints = grant.get('constraints') or {}
if constraints.get('probe_tool') != 'fstyp':
    errors.append(f'{grant_rel}: constraints.probe_tool must stay fstyp')
if constraints.get('allowed_filesystem_families') != ['msdosfs', 'exfat', 'ufs', 'cd9660']:
    errors.append(f'{grant_rel}: constraints.allowed_filesystem_families must stay the first-cut finite allowlist')
if constraints.get('denied_filesystem_families') != ['ext2fs', 'ntfs', 'zfs', 'geli', 'unknown']:
    errors.append(f'{grant_rel}: constraints.denied_filesystem_families must stay the first-cut deny set')
if 'small reviewed filesystem-family set' not in (constraints.get('notes') or ''):
    errors.append(f'{grant_rel}: constraints.notes must mention the small reviewed filesystem-family set')

layers = mount_view.get('layers') or []
ingest_layers = [layer for layer in layers if layer.get('mount_point') == '/ingest']
if len(ingest_layers) != 1:
    errors.append(f'{mount_rel}: must contain exactly one /ingest layer')
else:
    src = ingest_layers[0].get('source_ref') or ''
    if 'fstyp=exfat' not in src:
        errors.append(f'{mount_rel}: /ingest source_ref must pin the canonical admitted example family fstyp=exfat')
notes = '\n'.join(mount_view.get('notes') or [])
if 'allowlist remains finite' not in notes:
    errors.append(f'{mount_rel}: notes must say the first allowlist remains finite')

if 'fstyp admits exfat under a finite allowlist' not in (import_plan.get('notes') or ''):
    errors.append(f'{import_rel}: notes must mention fstyp admits exfat under a finite allowlist')

DOC_TOKENS = {
    'adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md': [
        'fstyp', '`msdosfs`', '`exfat`', '`ufs`', '`cd9660`', '`ext2fs`', '`ntfs`', '`zfs`', '`geli`'
    ],
    'docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md': [
        'probe with `fstyp`', '`msdosfs`', '`exfat`', '`ufs`', '`cd9660`', '`ext2fs`', '`ntfs`', '`zfs`', '`geli`', 'fail closed'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'host-side `fstyp` probe against a finite allowlist', '`msdosfs`, `exfat`, `ufs`, and `cd9660`'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'probe the medium with `fstyp` before mount', '`msdosfs`, `exfat`, `ufs`, `cd9660`'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'probe with `fstyp` before mount', '`ext2fs`, `ntfs`, `zfs`, `geli`, and unknown probe results fail closed'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'host must probe with `fstyp`', '`msdosfs`, `exfat`, `ufs`, and `cd9660`'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `fstyp(8)`', 'FreeBSD `mount.exfat-fuse(8)`', 'FreeBSD `mount_msdosfs(8)`', 'FreeBSD `mount_nullfs(8)`'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_fs_admission.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_fs_admission.py'],
    'docs/110-juicy-os-lessons.md': ['probe with `fstyp`', '`ext2fs`, `ntfs`, `zfs`, `geli`, and unknown probe results'],
    'docs/00-index.md': ['docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md', 'check_removable_media_local_fs_admission.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback filesystem-admission check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback filesystem-admission check passed')
