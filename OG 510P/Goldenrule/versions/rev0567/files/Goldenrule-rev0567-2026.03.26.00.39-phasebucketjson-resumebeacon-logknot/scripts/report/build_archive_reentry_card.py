#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_reentry_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_REENTRY_CARD.md'
RECOVERY_JSON = REPORTS / 'cloudtainer_rust_recovery_card.json'
COMEBACK_EXEC_JSON = REPORTS / 'rust_comeback_execution_card.json'
PACKAGE_CUT_JSON = REPORTS / 'archive_package_cut_card.json'
SIZE_JSON = REPORTS / 'archive_size_guardrail_card.json'
TRIAGE_JSON = REPORTS / 'archive_byte_triage_card.json'
HANDOFF_PACK_JSON = REPORTS / 'archive_handoff_pack.json'
ZIP_DIGEST_JSON = REPORTS / 'archive_zip_digest_card.json'
ZIP_SIZE_TRUTH_JSON = REPORTS / 'archive_zip_size_truth_card.json'
CHANGELOG = ROOT / 'CHANGELOG.md'

ROOT_RE = re.compile(
    r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$'
)
CHANGELOG_RE = re.compile(r'^## rev(?P<revision>\d+) - (?P<date>\d{4}-\d{2}-\d{2})$')


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path.relative_to(ROOT).as_posix())
    return json.loads(path.read_text(encoding='utf-8'))


def _parse_root_identity() -> dict[str, Any]:
    match = ROOT_RE.match(ROOT.name)
    if not match:
        raise RuntimeError(f'root name does not match archive naming pattern: {ROOT.name}')
    stamp = match.group('stamp')
    return {
        'root_name': ROOT.name,
        'revision': int(match.group('revision')),
        'revision_label': f"rev{match.group('revision')}",
        'timestamp_compact': stamp,
        'timestamp_iso_minute': f"{stamp[0:4]}-{stamp[5:7]}-{stamp[8:10]}T{stamp[11:13]}:{stamp[14:16]}",
        'descriptor_slug': match.group('descriptor'),
    }


def _load_changelog_chain() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in CHANGELOG.read_text(encoding='utf-8').splitlines():
        match = CHANGELOG_RE.match(line.strip())
        if not match:
            continue
        rows.append(
            {
                'revision': int(match.group('revision')),
                'revision_label': f"rev{match.group('revision')}",
                'date': match.group('date'),
            }
        )
    if not rows:
        raise RuntimeError('no changelog revision headings found')
    return rows


def build_report() -> dict[str, Any]:
    identity = _parse_root_identity()
    changelog_chain = _load_changelog_chain()
    latest = changelog_chain[-1]
    previous = changelog_chain[-2] if len(changelog_chain) >= 2 else None

    recovery = _load_json(RECOVERY_JSON)
    comeback_exec = _load_json(COMEBACK_EXEC_JSON)
    package_cut = _load_json(PACKAGE_CUT_JSON)
    size = _load_json(SIZE_JSON)
    triage = _load_json(TRIAGE_JSON)
    handoff_pack = _load_json(HANDOFF_PACK_JSON)
    zip_digest = _load_json(ZIP_DIGEST_JSON)
    zip_size_truth = _load_json(ZIP_SIZE_TRUTH_JSON)

    recovery_summary = recovery['summary']
    bridge = recovery['current_bridge']
    quick_plateau = next(row for row in comeback_exec['plateau_cards'] if row['label'] == 'quick_foothold')
    full_plateau = next(row for row in comeback_exec['plateau_cards'] if row['label'] == 'full_closure')

    changelog_alignment = {
        'aligned_to_root': latest['revision'] == identity['revision'],
        'latest_recorded_revision': latest,
        'immediate_predecessor_revision': previous,
        'root_vs_latest_delta': identity['revision'] - latest['revision'],
        'chain_tail': [
            {
                'revision_label': row['revision_label'],
                'date': row['date'],
            }
            for row in changelog_chain[-7:]
        ],
    }

    blocked_role = {
        'role': 'blocked_cloudtainer_operator',
        'primary_open_doc': 'docs/CLOUDTAINER_RUST_RECOVERY_CARD.md',
        'current_state_code': recovery_summary['current_state_code'],
        'mode': bridge['mode'],
        'reason': bridge['reason'],
        'primary_command': bridge['next_commands'][0],
        'followup_commands': bridge['next_commands'][1:],
        'preferred_lane_id': recovery_summary['preferred_lane_id'],
        'blocking_reason_codes': recovery_summary['blocking_reason_codes'],
        'budget_seconds': recovery_summary['blocked_session_fallback_buffered_seconds'],
    }

    rust_role = {
        'role': 'first_rust_capable_implementor',
        'primary_open_doc': 'docs/RUST_COMEBACK_EXECUTION_CARD.md',
        'primary_apply_hint': quick_plateau['apply_hint'],
        'primary_exact_witness_command': quick_plateau['new_exact_witness_commands'][0],
        'lane_smoke_command': quick_plateau['lane_smoke_commands'][0],
        'quick_foothold_prefix': quick_plateau['prefix_index'],
        'full_closure_prefix': full_plateau['prefix_index'],
        'full_closure_dual_lane': full_plateau['latest_lane_mix'] == 'dual_lane',
        'final_dual_lane_shard_path': comeback_exec['summary']['final_dual_lane_shard_path'],
        'refresh_command': bridge['first_machine_quick_foothold']['refresh_command'],
    }

    package_role = {
        'role': 'package_cut_steward',
        'primary_open_doc': 'docs/ARCHIVE_PACKAGE_CUT_CARD.md',
        'primary_settle_command': 'make settle-archive-truth',
        'package_boundary_ready': size['package_hygiene']['package_boundary_ready'],
        'primary_gate_command': package_cut['refresh_sequence'][0]['command'],
        'inventory_commands': [row['command'] for row in package_cut['refresh_sequence'][1:4]],
        'fixed_point_pair': package_cut['settle_rule']['fixed_point_pair'],
        'final_validation_commands': package_cut['settle_rule']['validation_commands'],
        'diet_first_open_doc': 'docs/ARCHIVE_BYTE_TRIAGE_CARD.md',
        'external_resume_open_doc': 'docs/ARCHIVE_ZIP_AUTHORITY_CARD.md',
        'external_resume_resolver_command': 'python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path',
        'external_digest_open_doc': 'docs/ARCHIVE_ZIP_DIGEST_CARD.md',
        'external_digest_sha256_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256',
        'external_digest_size_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes',
        'external_digest_verify_command': 'python3 scripts/tools/verify_authoritative_archive_zip.py',
        'external_size_truth_open_doc': 'docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md',
        'external_size_truth_verify_command': 'make test-archive-zip-size-truth-card',
        'external_size_truth_proxy_bytes': zip_size_truth['current_internal_proxy']['approx_revision_zip_bytes'],
        'selected_zip_digest_stable': zip_digest['selected_zip']['embedded_digest_stable'],
        'selected_zip_sha256': zip_digest['selected_zip']['embedded_sha256'],
        'handoff_pack_open_doc': 'docs/ARCHIVE_HANDOFF_PACK.md',
        'handoff_pack_verify_command': 'make test-archive-handoff-pack',
        'handoff_pack_integrity_command': 'python3 scripts/tools/verify_archive_handoff_pack.py',
        'handoff_pack_refresh_command': 'make update-archive-handoff-pack',
        'revision_planner_open_doc': 'docs/ARCHIVE_REVISION_CUT_CARD.md',
        'revision_planner_command': 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug',
        'canonical_cut_command': 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"',
        'diet_first_paths': [row['path'] for row in triage['cap_first_markdown_pack']],
        'pdf_count': size['package_hygiene']['pdf_count'],
        'scratch_file_count': size['package_hygiene']['scratch_file_count'],
    }

    headline_findings = [
        (
            f"Current archive head is `{identity['root_name']}` and the changelog head is "
            f"`{latest['revision_label']}` on {latest['date']}; alignment={changelog_alignment['aligned_to_root']}."
        ),
        (
            f"This cloudtainer remains `{blocked_role['current_state_code']}` with mode=`{blocked_role['mode']}`, so the "
            f"local first move is `{blocked_role['primary_command']}` rather than more in-place Rust recovery poking."
        ),
        (
            f"The first Rust-capable foothold is still one apply + one exact witness: `{rust_role['primary_apply_hint']}` then "
            f"`{rust_role['primary_exact_witness_command']}`."
        ),
        (
            f"The final Rust comeback closure still requires the dual-lane shard `{rust_role['final_dual_lane_shard_path']}`, "
            f"so full probe closure and full queue closure coincide at prefix {rust_role['full_closure_prefix']}."
        ),
        (
            f"Package-cut posture remains ready={package_role['package_boundary_ready']} with pdf_count={package_role['pdf_count']} "
            f"and scratch_file_count={package_role['scratch_file_count']}; the canonical settle wrapper is "
            f"`{package_role['primary_settle_command']}`, the external reopen resolver is "
            f"`{package_role['external_resume_resolver_command']}`, the normalized next-name planner is "
            f"`{package_role['revision_planner_command']}`, the canonical cutter is "
            f"`{package_role['canonical_cut_command']}`, and the first byte-diet open target stays `{package_role['diet_first_open_doc']}`."
        ),
    ]

    return {
        'card': 'archive_reentry_card',
        'snapshot_date': size.get('snapshot_date', '2026-03-23'),
        'archive_identity': identity,
        'changelog_alignment': changelog_alignment,
        'headline_findings': headline_findings,
        'roles': [blocked_role, rust_role, package_role],
        'blocked_cloudtainer_role': blocked_role,
        'first_rust_machine_role': rust_role,
        'package_cut_role': package_role,
        'metadata': {
            'source_reports': [
                RECOVERY_JSON.relative_to(ROOT).as_posix(),
                COMEBACK_EXEC_JSON.relative_to(ROOT).as_posix(),
                PACKAGE_CUT_JSON.relative_to(ROOT).as_posix(),
                SIZE_JSON.relative_to(ROOT).as_posix(),
                TRIAGE_JSON.relative_to(ROOT).as_posix(),
                HANDOFF_PACK_JSON.relative_to(ROOT).as_posix(),
                ZIP_SIZE_TRUTH_JSON.relative_to(ROOT).as_posix(),
            ],
            'source_docs': [
                'docs/CLOUDTAINER_RUST_RECOVERY_CARD.md',
                'docs/RUST_COMEBACK_EXECUTION_CARD.md',
                'docs/ARCHIVE_PACKAGE_CUT_CARD.md',
                'docs/ARCHIVE_HANDOFF_PACK.md',
                'docs/ARCHIVE_ZIP_AUTHORITY_CARD.md',
                'docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md',
                'docs/ARCHIVE_REVISION_CUT_CARD.md',
                'docs/ARCHIVE_BYTE_TRIAGE_CARD.md',
                'CHANGELOG.md',
            ],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    identity = report['archive_identity']
    align = report['changelog_alignment']
    blocked = report['blocked_cloudtainer_role']
    rust = report['first_rust_machine_role']
    package = report['package_cut_role']

    lines: list[str] = [
        '# Archive Reentry Card',
        '',
        'Compact reentry pointer for future inheritors: identify the current archive head, confirm whether the changelog head agrees, and give one primary open target plus first commands for the blocked cloudtainer, the first Rust-capable machine, and the final package cut.',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Current archive head',
        '',
        f"- root_name: `{identity['root_name']}`",
        f"- revision_label: `{identity['revision_label']}`",
        f"- timestamp_iso_minute: `{identity['timestamp_iso_minute']}`",
        f"- descriptor_slug: `{identity['descriptor_slug']}`",
        f"- changelog_aligned_to_root: `{align['aligned_to_root']}`",
        f"- latest_recorded_revision: `{align['latest_recorded_revision']['revision_label']}` ({align['latest_recorded_revision']['date']})",
    ])
    if align['immediate_predecessor_revision'] is not None:
        prev = align['immediate_predecessor_revision']
        lines.append(f"- immediate_predecessor_revision: `{prev['revision_label']}` ({prev['date']})")
    lines.extend([
        '',
        'Recent changelog chain tail:',
        '',
    ])
    for row in align['chain_tail']:
        lines.append(f"- `{row['revision_label']}` ({row['date']})")
    lines.extend([
        '',
        '## Blocked cloudtainer role',
        '',
        f"- primary_open_doc: `{blocked['primary_open_doc']}`",
        f"- current_state_code: `{blocked['current_state_code']}`",
        f"- mode: `{blocked['mode']}`",
        f"- primary_command: `{blocked['primary_command']}`",
        f"- budget_seconds: `{blocked['budget_seconds']}`",
        f"- preferred_lane_id: `{blocked['preferred_lane_id']}`",
        f"- blocking_reason_codes: `{', '.join(blocked['blocking_reason_codes'])}`",
        f"- reason: {blocked['reason']}",
        '- followup_commands:',
    ])
    for cmd in blocked['followup_commands']:
        lines.append(f'  - `{cmd}`')
    lines.extend([
        '',
        '## First Rust-capable machine role',
        '',
        f"- primary_open_doc: `{rust['primary_open_doc']}`",
        f"- quick_foothold_prefix: `{rust['quick_foothold_prefix']}`",
        f"- primary_apply_hint: `{rust['primary_apply_hint']}`",
        f"- primary_exact_witness_command: `{rust['primary_exact_witness_command']}`",
        f"- lane_smoke_command: `{rust['lane_smoke_command']}`",
        f"- refresh_command: `{rust['refresh_command']}`",
        f"- final_dual_lane_shard_path: `{rust['final_dual_lane_shard_path']}`",
        f"- full_closure_prefix: `{rust['full_closure_prefix']}`",
        f"- full_closure_dual_lane: `{rust['full_closure_dual_lane']}`",
        '',
        '## Package-cut steward role',
        '',
        f"- primary_open_doc: `{package['primary_open_doc']}`",
        f"- primary_settle_command: `{package['primary_settle_command']}`",
        f"- handoff_pack_open_doc: `{package['handoff_pack_open_doc']}`",
        f"- handoff_pack_verify_command: `{package['handoff_pack_verify_command']}`",
        f"- handoff_pack_integrity_command: `{package['handoff_pack_integrity_command']}`",
        f"- handoff_pack_refresh_command: `{package['handoff_pack_refresh_command']}`",
        f"- external_digest_verify_command: `{package['external_digest_verify_command']}`",
        f"- revision_planner_open_doc: `{package['revision_planner_open_doc']}`",
        f"- revision_planner_command: `{package['revision_planner_command']}`",
        f"- canonical_cut_command: `{package['canonical_cut_command']}`",
        f"- package_boundary_ready: `{package['package_boundary_ready']}`",
        f"- primary_gate_command: `{package['primary_gate_command']}`",
        '- inventory_commands:',
    ])
    for cmd in package['inventory_commands']:
        lines.append(f'  - `{cmd}`')
    lines.append('- fixed_point_pair:')
    for cmd in package['fixed_point_pair']:
        lines.append(f'  - `{cmd}`')
    lines.append('- final_validation_commands:')
    for cmd in package['final_validation_commands']:
        lines.append(f'  - `{cmd}`')
    lines.extend([
        f"- diet_first_open_doc: `{package['diet_first_open_doc']}`",
        '- diet_first_paths:',
    ])
    for path in package['diet_first_paths']:
        lines.append(f'  - `{path}`')
    lines.extend([
        '',
        '## Source surfaces',
        '',
    ])
    for path in report['metadata']['source_reports']:
        lines.append(f'- `{path}`')
    for path in report['metadata']['source_docs']:
        lines.append(f'- `{path}`')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the report json and markdown doc')
    args = parser.parse_args()

    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True)
    markdown = render_markdown(report)

    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(text + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown, encoding='utf-8')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
