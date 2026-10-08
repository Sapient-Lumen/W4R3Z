#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

START_HERE_BEGIN = '<!-- BEGIN GENERATED RESTART MIRROR FAMILY -->'
START_HERE_END = '<!-- END GENERATED RESTART MIRROR FAMILY -->'

RESTART_MIRROR_FAMILY_SPECS = [
    {
        'id': 'entry_surfaces',
        'heading': '## Entry surfaces',
        'intro': "These bullets are the human-readable compact mirror of `context-pack.json` `entry_surfaces`; this mirror is lint-enforced because human restart should not have to rediscover the archive's own canonical route anchors from surrounding prose.",
        'kind': 'bullets',
    },
    {
        'id': 'current_release_identity',
        'heading': '## Current release identity',
        'intro': "These bullets are the human-readable compact mirror of `RELEASE-MANIFEST.json` identity fields and should stay in exact lockstep as the archive's current bundle anchor; this mirror is lint-enforced because human restart should not have to recover the live release identity from filenames or open the manifest just to know which bundle head it is in.",
        'kind': 'bullets',
    },
    {
        'id': 'current_revision_delta',
        'heading': '## Current revision delta',
        'intro': "These bullets are the human-readable compact mirror of `REVISION-RECEIPT.json` and should stay in exact lockstep as the archive's current revision rationale; this mirror is lint-enforced because human restart should not have to open the receipt or infer the latest move from the changelog just to know what changed and why it counts.",
        'kind': 'bullets',
    },
    {
        'id': 'reentry_tiers',
        'heading': '## Re-entry tiers',
        'intro': 'These tier lists are the human-readable mirror of `context-pack.json` `restart_tiers` and should stay in exact lockstep.',
        'kind': 'tiers',
    },
    {
        'id': 'current_restart_posture',
        'heading': '## Current restart posture',
        'intro': 'These bullets are the human-readable mirror of `context-pack.json` `current_posture` and should stay in exact lockstep when routing-critical posture changes; this mirror is lint-enforced because parity claims should not remain trust-based.',
        'kind': 'bullets',
    },
    {
        'id': 'public_head_status',
        'heading': '## Public head status',
        'intro': "These bullets are the human-readable compact mirror of `SURFACE-STATUS.json` and should stay in exact lockstep as the archive's public head signal; this mirror is lint-enforced because human restart should not have to infer the archive's live state class and warning line from scattered prose.",
        'kind': 'bullets',
    },
    {
        'id': 'operator_warnings',
        'heading': '## Operator warnings',
        'intro': 'These bullets are the human-readable compact mirror of `context-pack.json` `operator_warnings` and should stay in exact lockstep as the archive\'s high-risk subset; this mirror is lint-enforced because human and machine restart should not diverge on the small set of guardrails most likely to corrupt continuation quality.',
        'kind': 'bullets',
    },
    {
        'id': 'followthrough_and_standby_state',
        'heading': '## Followthrough and standby state',
        'intro': 'These bullets are the human-readable compact mirror of `context-pack.json` `active_queue`, `active_followthrough_count`, and `standby_thresholds`; this mirror is lint-enforced because human reentry should not have to infer whether continuation has live tasks or only dormant reopen conditions.',
        'kind': 'bullets',
    },
    {
        'id': 'assumption_state',
        'heading': '## Assumption state',
        'intro': 'These bullets are the human-readable compact mirror of `context-pack.json` `assumption_state_summary`; this mirror is lint-enforced against both the machine handoff and `ASSUMPTION-LEDGER.json` because human restart should not have to infer whether continuation is running on a small durable standing set or a swollen tactical assumption stack.',
        'kind': 'bullets',
    },
    {
        'id': 'rebuild_commands',
        'heading': '## Rebuild commands',
        'intro': 'These bullets are the human-readable compact mirror of `context-pack.json` `commands`; this mirror is lint-enforced against the machine handoff and the `Makefile` so human restart does not have to reconstruct the tiny rebuild/package sequence from memory.',
        'kind': 'bullets',
    },
    {
        'id': 'priority_restart_open_questions',
        'heading': '## Priority restart open questions',
        'intro': 'These ids are the human-readable compact mirror of `context-pack.json` `priority_open_question_ids` and should stay in exact lockstep; contiguous runs may be expressed as inclusive ranges.',
        'kind': 'oq_ranges',
    },
]


def load_state(root: Path) -> dict:
    return {
        'manifest': json.loads((root / 'RELEASE-MANIFEST.json').read_text()),
        'receipt': json.loads((root / 'REVISION-RECEIPT.json').read_text()),
        'context': json.loads((root / 'context-pack.json').read_text()),
        'status': json.loads((root / 'SURFACE-STATUS.json').read_text()),
    }


def format_revision_delta(receipt: dict) -> list[str]:
    return [
        f"revision: `{receipt.get('revision', '')}`",
        f"previous revision: `{receipt.get('previous_revision', '')}`",
        f"revision kind: `{receipt.get('revision_kind', '')}`",
        f"summary: {receipt.get('summary', '')}",
    ]


def format_entry_surfaces(context: dict) -> list[str]:
    entry = context.get('entry_surfaces', {})
    return [
        f"human restart: `{entry.get('human_restart', '')}`",
        f"machine handoff: `{entry.get('machine_handoff', '')}`",
        f"release identity: `{entry.get('release_identity', '')}`",
        f"revision rationale: `{entry.get('revision_rationale', '')}`",
    ]


def format_release_identity(manifest: dict) -> list[str]:
    return [
        f"revision: `{manifest.get('revision', '')}`",
        f"timestamp: `{manifest.get('timestamp', '')}`",
        f"slug: `{manifest.get('slug', '')}`",
        f"bundle: `{manifest.get('bundle', '')}`",
    ]


def format_surface_status(status: dict) -> list[str]:
    return [
        f"state class: `{status.get('state_class', '')}`",
        f"followthrough state: `{status.get('followthrough_state', '')}`",
        f"durable status surface: `{status.get('durable_status_surface', '')}`",
        f"warning: {status.get('warning', '')}",
    ]


def format_queue_and_standby(context: dict) -> list[str]:
    out = [
        f"active queue: `{context.get('active_queue', '')}`",
        f"active followthrough count: `{context.get('active_followthrough_count', 0)}`",
    ]
    thresholds = context.get('standby_thresholds', [])
    if thresholds:
        for item in thresholds:
            out.append(
                f"standby threshold `{item.get('id', '')}` (`{item.get('assumption_id', '')}`, `{item.get('claim', '')}`) — {item.get('rule', '')}"
            )
    else:
        out.append('standby thresholds: none')
    return out


def format_assumption_state(context: dict) -> list[str]:
    summary = context.get('assumption_state_summary', {})
    standby_ids = summary.get('standby_threshold_ids', [])
    standby_text = ', '.join(f'`{item}`' for item in standby_ids) if standby_ids else 'none'
    return [
        f"active assumption count: `{summary.get('active_count', 0)}`",
        f"standby threshold count: `{summary.get('standby_threshold_count', 0)}`",
        f"standby threshold assumptions: {standby_text}",
    ]


def compress_oq_ids(ids: list[str]) -> list[str]:
    if not ids:
        return []
    out = []
    start = prev = None
    for oid in ids:
        num = int(oid.split('-')[1])
        if start is None:
            start = prev = num
            continue
        if num == prev + 1:
            prev = num
            continue
        out.append(_format_oq_range(start, prev))
        start = prev = num
    out.append(_format_oq_range(start, prev))
    return out


def _format_oq_range(start: int, end: int) -> str:
    if start == end:
        return f'`OQ-{start:04d}`'
    return f'`OQ-{start:04d}`–`OQ-{end:04d}`'


def render_lines_for_spec(spec: dict, state: dict) -> list[str]:
    manifest = state['manifest']
    receipt = state['receipt']
    context = state['context']
    status = state['status']
    section_id = spec['id']

    if section_id == 'entry_surfaces':
        return [f'- {item}' for item in format_entry_surfaces(context)]
    if section_id == 'current_release_identity':
        return [f'- {item}' for item in format_release_identity(manifest)]
    if section_id == 'current_revision_delta':
        return [f'- {item}' for item in format_revision_delta(receipt)]
    if section_id == 'reentry_tiers':
        lines = ['### 10-minute reopen']
        lines.extend(f'{i}. `{item}`' for i, item in enumerate(context.get('restart_tiers', {}).get('reopen_10min', []), start=1))
        lines.append('')
        lines.append('### 30-minute continuation')
        continuation = context.get('restart_tiers', {}).get('continuation_30min', [])
        start_num = len(context.get('restart_tiers', {}).get('reopen_10min', [])) + 1
        lines.extend(f'{i}. `{item}`' for i, item in enumerate(continuation, start=start_num))
        return lines
    if section_id == 'current_restart_posture':
        return [f'- {item}' for item in context.get('current_posture', [])]
    if section_id == 'public_head_status':
        return [f'- {item}' for item in format_surface_status(status)]
    if section_id == 'operator_warnings':
        return [f'- {item}' for item in context.get('operator_warnings', [])]
    if section_id == 'followthrough_and_standby_state':
        return [f'- {item}' for item in format_queue_and_standby(context)]
    if section_id == 'assumption_state':
        return [f'- {item}' for item in format_assumption_state(context)]
    if section_id == 'rebuild_commands':
        return [f'- {item}' for item in context.get('commands', [])]
    if section_id == 'priority_restart_open_questions':
        lines = [f'- {item}' for item in compress_oq_ids(context.get('priority_open_question_ids', []))]
        lines.append('')
        lines.append('Standby-only cosmology / measure questions `OQ-0018`–`OQ-0021` stay outside this default restart slice unless that lane is touched directly.')
        return lines
    raise KeyError(f'unknown restart mirror section id: {section_id}')


def render_generated_restart_mirror_block(state: dict) -> str:
    chunks: list[str] = []
    for spec in RESTART_MIRROR_FAMILY_SPECS:
        lines = [spec['heading'], spec['intro'], '']
        lines.extend(render_lines_for_spec(spec, state))
        chunks.append('\n'.join(lines).rstrip())
    body = '\n\n'.join(chunks).rstrip() + '\n'
    return f'{START_HERE_BEGIN}\n{body}{START_HERE_END}'


def extract_generated_restart_mirror_block(text: str) -> str:
    start = text.find(START_HERE_BEGIN)
    end = text.find(START_HERE_END)
    if start == -1 or end == -1 or end < start:
        raise ValueError('generated restart mirror block markers missing or malformed')
    end += len(START_HERE_END)
    return text[start:end]


def replace_generated_restart_mirror_block(text: str, rendered_block: str) -> str:
    current = extract_generated_restart_mirror_block(text)
    return text.replace(current, rendered_block)
