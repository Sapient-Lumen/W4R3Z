#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback closed-world post-detach descriptor set."""
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
preopen_rel = 'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json'
plan_schema_rel = 'spec/content.import.plan.schema.json'
receipt_schema_rel = 'spec/content.import.receipt.schema.json'
preopen_schema_rel = 'spec/preopen.map.schema.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
detach = load_json(detach_rel)
receipt = load_json(receipt_rel)
preopen = load_json(preopen_rel)
plan_schema = load_json(plan_schema_rel)
receipt_schema = load_json(receipt_schema_rel)
preopen_schema = load_json(preopen_schema_rel)

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_descriptor_set_posture': 'reviewed-fds-only-no-extra-inherited-descriptors',
    'post_detach_stdio_posture': 'stdin-null-stdout-stderr-launcher-owned-observation-only',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'close or spawn-closefrom every non-reviewed descriptor',
    'reviewed post-detach set stays closed-world',
    'stdin stays inert null/empty input only',
    'stdout/stderr stay launcher-owned observation channels or reviewed append-only log sinks',
    'no parent TTY/session socket',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

plan_exec = plan.get('execution') or {}
for key, value in {
    'post_detach_capability_mode_posture': 'cap-enter-before-tool-code-inherited-by-descendants',
    'post_detach_late_path_open_posture': 'no-ambient-absolute-path-open-after-cap-enter',
    'post_detach_descriptor_set_posture': 'reviewed-fds-only-no-extra-inherited-descriptors',
    'post_detach_stdio_posture': 'stdin-null-stdout-stderr-launcher-owned-observation-only',
}.items():
    if plan_exec.get(key) != value:
        errors.append(f'{plan_rel}: execution.{key} must stay {value}')
for token in (
    'inherits only the reviewed descriptor set',
    'closes or spawn-closefroms every non-reviewed descriptor',
    'stdin stays inert null/empty input only',
    'stdout/stderr stay launcher-owned observation channels or reviewed append-only log sinks',
    'no parent TTY/session socket',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = ((detach.get('runtime') or {}).get('mapping') or {})
for key, value in {
    'post_detach_descriptor_set_posture': 'reviewed-fds-only-no-extra-inherited-descriptors',
    'post_detach_stdio_posture': 'stdin-null-stdout-stderr-launcher-owned-observation-only',
    'post_detach_fd_closure_posture': 'closefrom-or-spawn-closefrom-before-tool-handoff',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

receipt_exec = receipt.get('execution') or {}
for key, value in {
    'post_detach_capability_mode_posture': 'cap-enter-before-tool-code-inherited-by-descendants',
    'post_detach_late_path_open_posture': 'no-ambient-absolute-path-open-after-cap-enter',
    'post_detach_descriptor_set_posture': 'reviewed-fds-only-no-extra-inherited-descriptors',
    'post_detach_stdio_posture': 'stdin-null-stdout-stderr-launcher-owned-observation-only',
}.items():
    if receipt_exec.get(key) != value:
        errors.append(f'{receipt_rel}: execution.{key} must stay {value}')
if 'closed-world-reviewed-fds' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'closed-world-reviewed-fds'")
if 'launcher-owned-stdio' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'launcher-owned-stdio'")
for token in (
    'inherited only the reviewed descriptor set',
    'closed or spawn-closefromed every non-reviewed descriptor',
    'stdin stayed inert null/empty input only',
    'stdout/stderr stayed launcher-owned observation channels or reviewed append-only log sinks',
    'no parent TTY/session socket',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

for key, value in {
    'descriptor_set_posture': 'reviewed-fds-only-no-extra-inherited-descriptors',
    'closefrom_posture': 'closefrom-or-spawn-closefrom-before-tool-handoff',
    'stdio_posture': 'stdin-null-stdout-stderr-launcher-owned-observation-only',
}.items():
    if preopen.get(key) != value:
        errors.append(f'{preopen_rel}: {key} must stay {value}')
for token in (
    'descriptor set stays closed-world',
    'closes or spawn-closefroms every non-reviewed descriptor',
    'stdin stays inert null/empty input only',
    'stdout/stderr stay launcher-owned observation channels or reviewed append-only log sinks',
    'no parent TTY/session socket',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

for rel, schema, prop in (
    (plan_schema_rel, plan_schema, ('properties', 'execution', 'properties')),
    (receipt_schema_rel, receipt_schema, ('properties', 'execution', 'properties')),
):
    node = schema
    for key in prop:
        node = node[key]
    for field in ('post_detach_descriptor_set_posture', 'post_detach_stdio_posture'):
        if field not in node:
            errors.append(f'{rel}: execution must define {field}')
node = preopen_schema['properties']
for field in ('descriptor_set_posture', 'closefrom_posture', 'stdio_posture'):
    if field not in node:
        errors.append(f'{preopen_schema_rel}: properties must define {field}')

DOC_TOKENS = {
    'adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md': [
        'reviewed descriptor set stays closed-world',
        'close or spawn-closefrom all non-reviewed descriptors',
        'stdio stays launcher-owned and non-parent-session-shaped',
        '`stdin` stays inert null/empty input only',
        '`stdout` and `stderr` may exist only as launcher-owned observation channels or reviewed append-only log sinks',
    ],
    'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md': [
        'descriptor set crossing that boundary is closed-world',
        'close or spawn-closefrom all non-reviewed descriptors',
        'stdio stays launcher-owned and non-parent-session-shaped',
        '`stdin` stays inert null/empty input only',
        '`stdout` and `stderr` may exist only as launcher-owned observation channels or reviewed append-only log sinks',
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'closed-world-descriptor-set cut is explicit too',
        'launcher closes or spawn-closefroms every non-reviewed descriptor before handoff',
        '`stdin` stays inert null/empty input only',
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'closed-world-descriptor-set cut is fixed too',
        'launcher closes or spawn-closefroms every non-reviewed descriptor before handoff',
        'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
    ],
    'docs/410-desktop-viability-checklist.md': [
        'closed-world-descriptor-set cut is fixed too',
        'launcher closes or spawn-closefroms every non-reviewed descriptor before handoff',
        'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'closed-world-descriptor-set cut is fixed too',
        'launcher closes or spawn-closefroms every non-reviewed descriptor before handoff',
        'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
    ],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': [
        'descriptor set closed-world',
        'spawn-closefroming every non-reviewed descriptor before handoff',
        'stdout/stderr launcher-owned observation channels or reviewed append-only log sinks',
        'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
        'closes or spawn-closefroms every non-reviewed descriptor before handoff',
    ],
    'docs/110-juicy-os-lessons.md': [
        'the reviewed post-detach descriptor set should stay closed-world',
        'close or spawn-closefrom every non-reviewed descriptor before handoff',
        'stdout`/`stderr` should stay launcher-owned observation channels or reviewed append-only log sinks',
    ],
    'docs/32-curated-references.md': [
        'closefrom(2)',
        'posix_spawn_file_actions_addclosefrom_np(3)',
        'fexecve(2)',
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_closed_world_descriptor_set.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_closed_world_descriptor_set.py'],
    'docs/00-index.md': [
        'docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md',
        'check_removable_media_local_closed_world_descriptor_set.py',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback closed-world descriptor-set check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback closed-world descriptor-set check passed')
