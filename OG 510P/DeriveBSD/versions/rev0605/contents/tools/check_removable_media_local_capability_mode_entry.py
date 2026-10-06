#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback post-detach capability-mode entry timing."""
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

grant = load_json(grant_rel)
plan = load_json(plan_rel)
detach = load_json(detach_rel)
receipt = load_json(receipt_rel)
preopen = load_json(preopen_rel)

CAP_MODE = 'cap-enter-before-tool-code-inherited-by-descendants'
LATE_OPEN = 'no-ambient-absolute-path-open-after-cap-enter'

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_capability_mode_posture': CAP_MODE,
    'post_detach_late_path_open_posture': LATE_OPEN,
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'enter capability mode before handing control to later classify/scan/sanitize tool code',
    'descendants inherit that mode and may not clear it',
    'no ambient absolute-path opens remain after cap_enter',
    'tool that cannot run on the preopened capability set stays out of this first lane',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_capability_mode_posture': CAP_MODE,
        'post_detach_late_path_open_posture': LATE_OPEN,
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
for token in (
    'enter capability mode before handing control to later classify/scan/sanitize tool code',
    'descendants inherit that mode and may not clear it',
    'no ambient absolute-path opens remain after cap_enter',
    'tool that cannot run on the preopened capability set stays out of this first lane',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_capability_mode_posture': CAP_MODE,
    'post_detach_late_path_open_posture': LATE_OPEN,
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

execution = receipt.get('execution') or {}
for key, value in {
    'post_detach_capability_mode_posture': CAP_MODE,
    'post_detach_late_path_open_posture': LATE_OPEN,
}.items():
    if execution.get(key) != value:
        errors.append(f'{receipt_rel}: execution.{key} must stay {value}')
if 'capmode-before-tool-code' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'capmode-before-tool-code'")
for token in (
    'entered capability mode before handing control to later classify/scan/sanitize tool code',
    'descendants inherited that mode and could not clear it',
    'no ambient absolute-path opens remained after cap_enter',
    'tool that could not run on the preopened capability set would have stayed out of this first lane',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

for token in (
    'enters capability mode before handing control to later tool mainline code',
    'After cap_enter no ambient absolute-path opens remain',
    'If a tool cannot run on that preopened capability set after cap_enter, it stays out',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0336-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md': [
        'enters capability mode before mainline and stays there',
        'enter capability mode before handing control to later tool mainline code',
        'tools that cannot run on the preopened capability set stay out of the first lane',
    ],
    'docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md': [
        'enters capability mode before mainline and stays there',
        'capability mode before handing control to later tool code',
        'ambient absolute-path opens after `cap_enter()` stay out',
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'The next capability-mode-entry cut is explicit too',
        'enters capability mode before handing control to later tool mainline code',
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'The next capability-mode-entry cut is fixed too',
        'enters capability mode before handing control to later tool mainline code',
    ],
    'docs/410-desktop-viability-checklist.md': [
        'The next capability-mode-entry cut is fixed too',
        'ambient absolute-path opens stay out after `cap_enter()`',
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'The next capability-mode-entry cut is fixed too',
        'tools that cannot run on the preopened capability set stay out',
    ],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': [
        'enters capability mode before handing control to later tool code',
        'ambient absolute-path opens stay out after `cap_enter()`',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0336-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md',
    ],
    'docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md': [
        'docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md',
        'that open question is now resolved by `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`',
    ],
    'docs/110-juicy-os-lessons.md': [
        'later-tool code should start only after capability mode entry',
        'tools that cannot run on the preopened capability set stay out',
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_capability_mode_entry.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_capability_mode_entry.py'],
    'docs/00-index.md': [
        'docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md',
        'check_removable_media_local_capability_mode_entry.py',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback capability-mode-entry check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback capability-mode-entry check passed')
