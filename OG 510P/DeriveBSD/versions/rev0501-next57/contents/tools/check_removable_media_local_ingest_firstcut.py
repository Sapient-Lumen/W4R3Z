#!/usr/bin/env python3
"""Guardrail for the first-cut removable-media local ingest execution boundary."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def digest(rel: str) -> str:
    obj = load_json(rel)
    data = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return 'sha256:' + hashlib.sha256(data).hexdigest()


errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
view_rel = 'spec/examples/devfs.view.plan.removable-media-local-ingest.json'
mount_rel = 'spec/examples/mount.view.removable-media-local-ingest.json'
import_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'

grant = load_json(grant_rel)
view = load_json(view_rel)
mount_view = load_json(mount_rel)
import_plan = load_json(import_rel)
expected_grant_digest = digest(grant_rel)

if grant.get('device', {}).get('class') != 'block-storage-removable':
    errors.append(f'{grant_rel}: device.class must stay block-storage-removable')
if grant.get('constraints', {}).get('read_only') is not True:
    errors.append(f'{grant_rel}: constraints.read_only must stay true')
if grant.get('constraints', {}).get('session_scope') != 'single-use':
    errors.append(f'{grant_rel}: constraints.session_scope must stay single-use')
if grant.get('constraints', {}).get('quarantine_lane') != 'host-controlled-mount-then-disposable-jail':
    errors.append(f'{grant_rel}: constraints.quarantine_lane must stay host-controlled-mount-then-disposable-jail')

if view.get('target', {}).get('domain_kind') != 'jail':
    errors.append(f'{view_rel}: target.domain_kind must stay jail')
if view.get('baseline') != 'empty':
    errors.append(f'{view_rel}: baseline must stay empty')
if (view.get('inputs') or {}).get('device_attach_grant_digests') != [expected_grant_digest]:
    errors.append(f'{view_rel}: inputs.device_attach_grant_digests must pin the canonical removable-media local-ingest grant example digest')
for rule in view.get('rules', []):
    path = rule.get('path', '')
    for forbidden in ('da', 'ada', 'nda', 'nvd', 'pass', 'cd', 'md'):
        if path.startswith(forbidden):
            errors.append(f'{view_rel}: rules must not expose raw block device nodes ({path}) in the ingest jail first cut')
            break

layers = mount_view.get('layers', [])
if not any(layer.get('mount_point') == '/ingest' and layer.get('access') == 'ro' for layer in layers):
    errors.append(f'{mount_rel}: must expose a read-only /ingest tree')
if not any(layer.get('mount_point') == '/work' and layer.get('access') == 'tmp' for layer in layers):
    errors.append(f'{mount_rel}: must expose scratch space at /work')
if any(layer.get('access') == 'rw' for layer in layers):
    errors.append(f'{mount_rel}: first cut must not include rw layers')

execution = import_plan.get('execution') or {}
if execution.get('isolation') != 'jail' or execution.get('network') != 'none' or execution.get('lifetime') != 'disposable':
    errors.append(f'{import_rel}: execution must stay jail + none + disposable')
if (import_plan.get('origin') or {}).get('source', {}).get('type') != 'usb':
    errors.append(f'{import_rel}: origin.source.type must stay usb')
if import_plan.get('lease_id') != grant.get('lease_id'):
    errors.append(f'{import_rel}: lease_id must stay joined to the canonical removable-media local-ingest grant example')
if 'no raw block device nodes' not in (import_plan.get('notes') or ''):
    errors.append(f'{import_rel}: notes must state that the ingest jail receives no raw block device nodes')

DOC_TOKENS = {
    'adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': [
        'host performs the explicit read-only-first storage attach/mount steps',
        'disposable jail',
        'mounted removable-media tree is projected into the jail via `mount.view`',
        'not a claim that a jail equals a device domain or microVM',
    ],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': [
        'host-controlled explicit read-only mount',
        'disposable no-network ingest jail',
        'no raw block device nodes',
        'first buildable',
    ],
    'docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md': [
        'host-controlled read-only mount',
        '`mount.view`',
        'block-empty',
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'host-controlled read-only mount',
        'disposable no-network jail',
        'mounted tree',
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'mount authority on the host',
        'no raw block-device nodes',
        '`mount.view`',
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'host-controlled read-only mount',
        'disposable no-network jail',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md',
    ],
    'docs/98-archive-hygiene.md': [
        'check_removable_media_local_ingest_firstcut.py',
    ],
    'docs/99-llm-runbook.md': [
        'check_removable_media_local_ingest_firstcut.py',
    ],
    'docs/00-index.md': [
        'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md',
        'check_removable_media_local_ingest_firstcut.py',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-ingest first-cut check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-ingest first-cut check passed')
