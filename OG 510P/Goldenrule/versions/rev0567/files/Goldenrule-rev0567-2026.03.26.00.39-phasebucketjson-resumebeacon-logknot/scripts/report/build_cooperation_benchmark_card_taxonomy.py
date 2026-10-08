#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_taxonomy.schema.json'
TITLE = '# Cooperation Benchmark Card Taxonomy'
SUBTITLE = (
    'Generated registry for the stable compact-card identifiers that appear across inventory, heads, review, '
    'citation, next-action, and execution-lane surfaces. This prevents reason-code / action-kind / lane-id drift '
    'from becoming inheritor guesswork.'
)

REPORTS = [
    ('artifacts/reports/cooperation_benchmark_card_inventory.json', 'inventory-report'),
    ('artifacts/reports/cooperation_benchmark_card_heads.json', 'heads-report'),
    ('artifacts/reports/cooperation_benchmark_card_review_queue.json', 'review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_macro_review_queue.json', 'macro-review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_citation_surface.json', 'citation-surface-report'),
    ('artifacts/reports/cooperation_benchmark_card_execution_lanes.json', 'execution-lanes-report'),
]

CATEGORIES: list[dict[str, Any]] = [
    {
        'category_id': 'inventory_drift_reason_codes',
        'summary': 'Fail-closed receipt drift reasons emitted by the compact-card inventory.',
        'field_refs': [
            'freeze_receipts[].drift_reason_codes',
            'delta_receipts[].drift_reason_codes',
        ],
        'tokens': [
            {'token': 'freeze-card-missing', 'summary': 'The card path recorded in a freeze receipt no longer exists.'},
            {'token': 'freeze-card-sha-drift', 'summary': 'The current card bytes no longer match the retained freeze receipt hash.'},
            {'token': 'freeze-render-missing', 'summary': 'The rendered markdown path recorded in a freeze receipt no longer exists.'},
            {'token': 'freeze-render-sha-drift', 'summary': 'The current rendered markdown bytes no longer match the retained freeze receipt hash.'},
            {'token': 'delta-old-card-missing', 'summary': 'The predecessor card path recorded in a delta receipt no longer exists.'},
            {'token': 'delta-old-card-sha-drift', 'summary': 'The predecessor card bytes no longer match the retained delta receipt hash.'},
            {'token': 'delta-new-card-missing', 'summary': 'The successor card path recorded in a delta receipt no longer exists.'},
            {'token': 'delta-new-card-sha-drift', 'summary': 'The successor card bytes no longer match the retained delta receipt hash.'},
        ],
    },
    {
        'category_id': 'head_warning_reason_codes',
        'summary': 'Lineage-head warnings emitted by the heads register and carried into the control plane.',
        'field_refs': [
            'heads.lineages[].warning_reason_codes',
            'control_plane.lineages[].warning_reason_codes',
        ],
        'tokens': [
            {'token': 'multiple-roots', 'summary': 'The lineage component has more than one root card.'},
            {'token': 'branch-ambiguous', 'summary': 'The lineage component has multiple tips or branching successors.'},
            {'token': 'no-claim-ready-operational-head', 'summary': 'No claim-ready latest-known card can serve as the operational head.'},
            {'token': 'multiple-operational-heads', 'summary': 'More than one claim-ready latest-known card is competing to be the operational head.'},
            {'token': 'latest-operational-head-needs-freeze', 'summary': 'The unique operational head is claim-ready but still lacks a verified freeze receipt.'},
            {'token': 'latest-operational-head-freeze-drift', 'summary': 'The unique operational head only has drifted freeze receipts and needs a fresh guarded freeze.'},
            {'token': 'multiple-citation-heads', 'summary': 'More than one frozen claim-ready latest-known card is competing to be the citation head.'},
        ],
    },
    {
        'category_id': 'citation_reason_codes',
        'summary': 'Reasons a lineage is excluded from the fail-closed citation surface.',
        'field_refs': [
            'citation_surface.unresolved_lineages[].reason_codes',
            'control_plane.lineages[].citation_reason_codes',
            'handoff_pack.unresolved_lineages[].reason_codes',
        ],
        'tokens': [
            {'token': 'no-unique-citation-head', 'summary': 'The lineage does not currently have one unique citation head.'},
            {'token': 'lineage-basis-cycle', 'summary': 'Walking retained delta ancestry for the citation head encountered a cycle.'},
            {'token': 'ambiguous-lineage-basis', 'summary': 'A citation-head predecessor step is not singular, so the retained lineage basis is ambiguous.'},
            {'token': 'multiple-verified-delta-receipts', 'summary': 'More than one verified retained delta receipt claims to advance into the same card.'},
            {'token': 'citation-basis-drift', 'summary': 'A retained delta receipt exists for the lineage basis but no longer matches current card bytes.'},
            {'token': 'missing-lineage-delta-receipt', 'summary': 'A required retained delta receipt is missing from the lineage basis.'},
            {'token': 'multiple-verified-freeze-receipts', 'summary': 'More than one verified freeze receipt claims authority over the same citation head.'},
            {'token': 'missing-verified-freeze-receipt', 'summary': 'No verified freeze receipt currently binds the citation head.'},
        ],
    },
    {
        'category_id': 'review_item_kinds',
        'summary': 'Actionable row kinds emitted by the flat and macro compact-card review queues.',
        'field_refs': [
            'review_queue.items[].item_kind',
            'macro_review_queue.groups[].item_kinds[]',
            'control_plane.lineages[].review_item_kinds',
        ],
        'tokens': [
            {'token': 'readiness_lint', 'summary': 'Schema-valid card still fails claim-readiness lint.'},
            {'token': 'freeze_needed', 'summary': 'Unique operational head needs a guarded freeze to regain a citation head.'},
            {'token': 'topology_review', 'summary': 'Lineage topology or head state blocks a straightforward citation answer.'},
            {'token': 'freeze_drift', 'summary': 'Retained freeze evidence drifted and needs refresh.'},
            {'token': 'delta_drift', 'summary': 'Retained delta-basis evidence drifted and needs refresh.'},
        ],
    },
    {
        'category_id': 'review_reason_codes',
        'summary': 'Reason codes carried by compact-card review items and grouped review lineages.',
        'field_refs': [
            'review_queue.items[].reason_codes',
            'macro_review_queue.groups[].reason_codes',
            'control_plane.lineages[].review_reason_codes',
            'next_action_witness.candidates[].reason_codes',
            'next_action.primary_action.reason_codes',
        ],
        'tokens': [
            {'token': 'claim-not-ready', 'summary': 'Card is still draft-valid rather than claim-ready.'},
            {'token': 'freeze-card-missing', 'summary': 'Freeze receipt points at a missing card.'},
            {'token': 'freeze-card-sha-drift', 'summary': 'Freeze receipt card hash no longer matches current bytes.'},
            {'token': 'freeze-render-missing', 'summary': 'Freeze receipt points at missing rendered markdown.'},
            {'token': 'freeze-render-sha-drift', 'summary': 'Freeze receipt render hash no longer matches current bytes.'},
            {'token': 'delta-old-card-missing', 'summary': 'Delta receipt predecessor card path is missing.'},
            {'token': 'delta-old-card-sha-drift', 'summary': 'Delta receipt predecessor card hash drifted.'},
            {'token': 'delta-new-card-missing', 'summary': 'Delta receipt successor card path is missing.'},
            {'token': 'delta-new-card-sha-drift', 'summary': 'Delta receipt successor card hash drifted.'},
            {'token': 'multiple-roots', 'summary': 'Lineage topology has multiple roots.'},
            {'token': 'branch-ambiguous', 'summary': 'Lineage topology is branch-ambiguous.'},
            {'token': 'no-claim-ready-operational-head', 'summary': 'No claim-ready operational head exists.'},
            {'token': 'multiple-operational-heads', 'summary': 'More than one operational head candidate exists.'},
            {'token': 'latest-operational-head-needs-freeze', 'summary': 'Operational head needs a guarded freeze.'},
            {'token': 'latest-operational-head-freeze-drift', 'summary': 'Operational head only has drifted freeze evidence.'},
            {'token': 'multiple-citation-heads', 'summary': 'More than one citation head candidate exists.'},
            {'token': 'no-unique-citation-head', 'summary': 'Citation surface cannot name one unique citation head.'},
            {'token': 'lineage-basis-cycle', 'summary': 'Citation lineage basis contains a cycle.'},
            {'token': 'ambiguous-lineage-basis', 'summary': 'Citation lineage basis is not singular.'},
            {'token': 'multiple-verified-delta-receipts', 'summary': 'More than one verified delta receipt claims the same successor.'},
            {'token': 'citation-basis-drift', 'summary': 'Citation lineage basis depends on drifted delta evidence.'},
            {'token': 'missing-lineage-delta-receipt', 'summary': 'Citation lineage basis is missing a required delta receipt.'},
            {'token': 'multiple-verified-freeze-receipts', 'summary': 'More than one verified freeze receipt claims the same card.'},
            {'token': 'missing-verified-freeze-receipt', 'summary': 'No verified freeze receipt currently binds the citation head.'},
        ],
    },
    {
        'category_id': 'next_action_kinds',
        'summary': 'Top-level action kinds that can win compact-card first reentry.',
        'field_refs': [
            'next_action.primary_action.action_kind',
            'next_action_witness.candidates[].action_kind',
        ],
        'tokens': [
            {'token': 'review_lineage', 'summary': 'Enter grouped lineage repair work before trusting citation / handoff surfaces.'},
            {'token': 'inspect_unresolved_citation', 'summary': 'Inspect unresolved citation/control-plane state before inheriting claims.'},
            {'token': 'verify_ready_surface', 'summary': 'Verify the ready-state fused surface before proceeding.'},
        ],
    },
    {
        'category_id': 'next_action_priority_keys',
        'summary': 'Stable priority policy inputs for first-reentry selection.',
        'field_refs': [
            'next_action_witness.candidates[].priority_bucket',
            'next_action_witness.candidates[].priority_label',
        ],
        'tokens': [
            {'token': 'delta_drift', 'summary': 'Refresh retained delta-basis evidence first.', 'metadata': {'priority_bucket': 0, 'priority_label': 'refresh-delta-basis'}},
            {'token': 'freeze_drift', 'summary': 'Refresh retained freeze evidence before other work.', 'metadata': {'priority_bucket': 1, 'priority_label': 'refresh-freeze-basis'}},
            {'token': 'freeze_needed', 'summary': 'Guard-freeze the current head once retained evidence is current.', 'metadata': {'priority_bucket': 2, 'priority_label': 'freeze-current-head'}},
            {'token': 'topology_review', 'summary': 'Resolve lineage topology/head ambiguity next.', 'metadata': {'priority_bucket': 3, 'priority_label': 'resolve-lineage-topology'}},
            {'token': 'readiness_lint', 'summary': 'Finish claim-readiness work after structural issues.', 'metadata': {'priority_bucket': 4, 'priority_label': 'finish-claim-readiness'}},
            {'token': 'inspect_unresolved_citation', 'summary': 'Inspect unresolved citation state when no grouped review queue exists.', 'metadata': {'priority_bucket': 5, 'priority_label': 'inspect-unresolved-citation'}},
            {'token': 'verify_ready_surface', 'summary': 'Ready-state verification sits at the lowest urgency bucket.', 'metadata': {'priority_bucket': 90, 'priority_label': 'verify-ready-surface'}},
        ],
    },
    {
        'category_id': 'next_action_selector_kinds',
        'summary': 'Selectors that are allowed to choose the compact-card first command.',
        'field_refs': [
            'next_action_witness.selector_kind',
        ],
        'tokens': [
            {'token': 'priority_bucket_then_candidate_id', 'summary': 'Choose the lowest priority bucket, then break ties by stable candidate id ordering.'},
        ],
    },
    {
        'category_id': 'next_action_selection_statuses',
        'summary': 'Selection outcomes preserved on the primary next-action surface.',
        'field_refs': [
            'next_action.primary_action.selection_status',
        ],
        'tokens': [
            {'token': 'unique-highest-priority', 'summary': 'The chosen candidate was the only candidate in the winning priority bucket.'},
            {'token': 'stable-tie-break', 'summary': 'The chosen candidate won by stable tie-break within the winning priority bucket.'},
        ],
    },
    {
        'category_id': 'next_action_winner_uniqueness',
        'summary': 'Witness-level uniqueness states preserved for the winning next-action bucket.',
        'field_refs': [
            'next_action_witness.winner_uniqueness',
        ],
        'tokens': [
            {'token': 'unique-highest-priority', 'summary': 'The winning bucket had one candidate.'},
            {'token': 'stable-tie-break', 'summary': 'The winning bucket had multiple candidates and the selector chose a stable representative.'},
        ],
    },
    {
        'category_id': 'execution_lane_ids',
        'summary': 'Stable lane identifiers for environment-honest compact-card validation.',
        'field_refs': [
            'execution_lanes.lanes[].lane_id',
            'next_action_witness.selected_command_ladder[].required_lane_id',
            'next_action.primary_action.required_lane_id',
            'next_action.primary_action.command_ladder[].required_lane_id',
            'control_plane.recommended_next_command_lane_id',
        ],
        'tokens': [
            {'token': 'python-integrity', 'summary': 'Surface-integrity lane for report build/check work.'},
            {'token': 'rust-harness', 'summary': 'Deeper engine / harness lane for Rust-backed validation.'},
        ],
    },
    {
        'category_id': 'focus_open_target_role_codes',
        'summary': 'Role codes explaining why a retained path appears in the focus-open target family.',
        'field_refs': [
            'control_plane.focus_open_targets[].role_codes[]',
            'next_action_witness.focus_open_targets[].role_codes[]',
            'next_action.focus_open_targets[].role_codes[]',
        ],
        'tokens': [
            {'token': 'primary-open', 'summary': 'This path is the preferred first retained file to open for the focus lineage.'},
            {'token': 'citation-rendered-markdown', 'summary': 'This path is the rendered markdown companion for the focus citation head.'},
            {'token': 'citation-card', 'summary': 'This path is the machine-readable citation head card.'},
            {'token': 'operational-rendered-markdown', 'summary': 'This path is the rendered markdown companion for the focus operational head.'},
            {'token': 'operational-card', 'summary': 'This path is the machine-readable operational head card.'},
        ],
    },
    {
        'category_id': 'selected_command_open_target_role_codes',
        'summary': 'Role codes explaining why a retained path appears as the selected next-step or first-fallback inspect target.',
        'field_refs': [
            'next_action_witness.selected_next_command_open_target.role_codes[]',
            'next_action_witness.selected_fallback_command_open_target.role_codes[]',
            'next_action_witness.selected_command_ladder[].open_target.role_codes[]',
            'next_action.primary_action.target_open_target.role_codes[]',
            'next_action.primary_action.fallback_open_target.role_codes[]',
            'next_action.primary_action.command_ladder[].open_target.role_codes[]',
        ],
        'tokens': [
            {'token': 'selected-next-command-open', 'summary': 'This path is the preferred retained document to open immediately after the selected next command completes.'},
            {'token': 'selected-fallback-command-open', 'summary': 'This path is the preferred retained document to open immediately after the first fallback command completes.'},
            {'token': 'selected-command-ladder-open', 'summary': 'This path is the retained document to open after a concrete rung in the selected command ladder completes.'},
        ],
    },
    {
        'category_id': 'handoff_pack_entry_target_role_codes',
        'summary': 'Role codes explaining why a retained path appears in the handoff-pack entry target family.',
        'field_refs': [
            'handoff_pack.packs[].entry_targets[].role_codes[]',
        ],
        'tokens': [
            {'token': 'primary-open', 'summary': 'This path is the preferred first retained file to open from the handoff pack.'},
            {'token': 'citation-rendered-markdown', 'summary': 'This path is the rendered markdown companion for the pack citation head.'},
            {'token': 'citation-card', 'summary': 'This path is the machine-readable citation head card in the pack basis.'},
            {'token': 'operational-rendered-markdown', 'summary': 'This path is the rendered markdown companion for the pack operational head.'},
            {'token': 'operational-card', 'summary': 'This path is the machine-readable operational head card in the pack basis.'},
            {'token': 'citation-freeze-receipt', 'summary': 'This path is the verified freeze receipt that binds the pack citation head.'},
        ],
    },
    {
        'category_id': 'focus_primary_command_target_role_codes',
        'summary': 'Role codes explaining what the direct focus verify/refresh command targets are for.',
        'field_refs': [
            'control_plane.focus_primary_verify_target.role_codes[]',
            'control_plane.focus_primary_refresh_target.role_codes[]',
            'next_action_witness.focus_primary_verify_target.role_codes[]',
            'next_action_witness.focus_primary_refresh_target.role_codes[]',
            'next_action.focus_primary_verify_target.role_codes[]',
            'next_action.focus_primary_refresh_target.role_codes[]',
        ],
        'tokens': [
            {'token': 'primary-verify-target', 'summary': 'This retained path is the canonical machine target for the first focus verify command.'},
            {'token': 'primary-refresh-target', 'summary': 'This retained path is the canonical machine target for the first focus refresh command.'},
            {'token': 'citation-surface-report', 'summary': 'This retained path is the citation-surface report.'},
            {'token': 'inventory-report', 'summary': 'This retained path is the compact-card inventory report.'},
        ],
    },
    {
        'category_id': 'handoff_pack_primary_command_target_role_codes',
        'summary': 'Role codes explaining what the direct handoff-pack verify/refresh command targets are for.',
        'field_refs': [
            'handoff_pack.packs[].primary_verify_target.role_codes[]',
            'handoff_pack.packs[].primary_refresh_target.role_codes[]',
        ],
        'tokens': [
            {'token': 'primary-verify-target', 'summary': 'This retained path is the canonical machine target for the first pack verify command.'},
            {'token': 'primary-refresh-target', 'summary': 'This retained path is the canonical machine target for the first pack refresh command.'},
            {'token': 'citation-surface-report', 'summary': 'This retained path is the citation-surface report.'},
            {'token': 'inventory-report', 'summary': 'This retained path is the compact-card inventory report.'},
        ],
    },
    {
        'category_id': 'focus_primary_command_effect_codes',
        'summary': 'Effect codes explaining whether the direct first focus command is read-only or state-changing.',
        'field_refs': [
            'control_plane.focus_primary_verify_effect_code',
            'control_plane.focus_primary_refresh_effect_code',
            'next_action_witness.focus_primary_verify_effect_code',
            'next_action_witness.focus_primary_refresh_effect_code',
            'next_action.focus_primary_verify_effect_code',
            'next_action.focus_primary_refresh_effect_code',
        ],
        'tokens': [
            {'token': 'read-only-check', 'summary': 'This direct first focus command verifies retained artifacts without rewriting them.'},
            {'token': 'in-place-report-rewrite', 'summary': 'This direct first focus command rewrites one retained report in place.'},
        ],
    },
    {
        'category_id': 'handoff_pack_primary_command_effect_codes',
        'summary': 'Effect codes explaining whether the direct handoff-pack first command is read-only or state-changing.',
        'field_refs': [
            'handoff_pack.packs[].primary_verify_effect_code',
            'handoff_pack.packs[].primary_refresh_effect_code',
        ],
        'tokens': [
            {'token': 'read-only-check', 'summary': 'This direct handoff-pack first command verifies retained artifacts without rewriting them.'},
            {'token': 'in-place-report-rewrite', 'summary': 'This direct handoff-pack first command rewrites one retained report in place.'},
        ],
    },
    {
        'category_id': 'execution_blocking_reason_codes',
        'summary': 'Stable blocking reasons for unavailable execution lanes.',
        'field_refs': [
            'execution_lanes.lanes[].blocking_reason_codes',
            'next_action_witness.selected_command_ladder[].required_lane_blocking_reason_codes',
            'next_action.primary_action.required_lane_blocking_reason_codes',
            'next_action.primary_action.command_ladder[].required_lane_blocking_reason_codes',
        ],
        'tokens': [
            {'token': 'python3-missing', 'summary': 'Python 3 is unavailable in the current environment.'},
            {'token': 'python-jsonschema-missing', 'summary': 'The Python jsonschema package is unavailable in the current environment.'},
            {'token': 'rust-exec-missing', 'summary': 'The repo Rust wrapper script is missing from its expected path.'},
            {'token': 'native-cargo-missing', 'summary': 'Native cargo is unavailable in the current environment.'},
            {'token': 'native-rustc-missing', 'summary': 'Native rustc is unavailable in the current environment.'},
            {'token': 'junest-binary-missing', 'summary': 'The JuNest binary is unavailable in the current environment.'},
            {'token': 'junest-home-missing', 'summary': 'The JuNest home directory is unavailable in the current environment.'},
            {'token': 'junest-rust-toolchain-missing', 'summary': 'JuNest is present but does not currently expose a usable Rust toolchain.'},
        ],
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_binding(path_str: str, role: str) -> dict[str, Any]:
    path = ROOT / path_str
    return {
        'path': path_str,
        'role': role,
        'sha256': sha256_file(path),
        'bytes': path.stat().st_size,
    }


def collect() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    category_rows: list[dict[str, Any]] = []
    token_count = 0
    for category in CATEGORIES:
        tokens = sorted(category['tokens'], key=lambda row: row['token'])
        token_count += len(tokens)
        category_rows.append(
            {
                'category_id': category['category_id'],
                'summary': category['summary'],
                'field_refs': category['field_refs'],
                'tokens': tokens,
            }
        )
    data = {
        'taxonomy_kind': 'cooperation_benchmark_card_taxonomy',
        'preferred_for_inheritors': True,
        'counts': {
            'category_count': len(category_rows),
            'token_count': token_count,
        },
        'report_bindings': [report_binding(path_str, role) for path_str, role in REPORTS],
        'categories': category_rows,
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- category_count: {data['counts']['category_count']}",
        f"- token_count: {data['counts']['token_count']}",
        '',
        '## Category summary',
        '',
        '| category_id | tokens | field_refs |',
        '|---|---:|---|',
    ]
    for category in data['categories']:
        lines.append(
            f"| `{category['category_id']}` | {len(category['tokens'])} | {'; '.join('`' + value + '`' for value in category['field_refs'])} |"
        )
    lines.extend(['', '## Category details', ''])
    for category in data['categories']:
        lines.append(f"### `{category['category_id']}`")
        lines.append('')
        lines.append(category['summary'])
        lines.append('')
        lines.append(f"- field_refs: {', '.join('`' + value + '`' for value in category['field_refs'])}")
        lines.append('')
        lines.append('| token | summary | metadata |')
        lines.append('|---|---|---|')
        for token in category['tokens']:
            metadata = token.get('metadata', {})
            metadata_rendered = '—' if not metadata else '`' + json.dumps(metadata, sort_keys=True) + '`'
            lines.append(f"| `{token['token']}` | {token['summary']} | {metadata_rendered} |")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_taxonomy.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_TAXONOMY.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-taxonomy: wrote {out_md}')
        print(f'cooperation-benchmark-card-taxonomy: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-taxonomy: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-taxonomy: ok ({data['counts']['token_count']} tokens)")
    print(f'cooperation-benchmark-card-taxonomy: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
