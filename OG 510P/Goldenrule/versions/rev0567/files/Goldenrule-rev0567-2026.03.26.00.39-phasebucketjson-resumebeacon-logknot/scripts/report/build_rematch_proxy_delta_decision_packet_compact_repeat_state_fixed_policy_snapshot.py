#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.md'
FOCAL_EXPECTED_REPEAT_LOOKUPS = 0.18
REFERENCE_EXPECTED_REPEAT_LOOKUPS = [0.1, 0.18, 0.2, 0.3, 0.5, 0.7]
MAX_UNIQUE_APPENDS = 256


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def _fixed_row(plan: dict[str, object], state_kind: str) -> dict[str, object]:
    return next(row for row in plan['fixed_rows'] if row['state_kind'] == state_kind)



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    horizon_metrics = packet.fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=MAX_UNIQUE_APPENDS,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )
    focal_plan = packet.recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=FOCAL_EXPECTED_REPEAT_LOOKUPS,
    )
    reference_budget_rows = []
    for expected_repeat_lookups in REFERENCE_EXPECTED_REPEAT_LOOKUPS:
        plan = packet.recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_from_metrics(
            horizon_metrics,
            expected_repeat_lookups=expected_repeat_lookups,
        )
        reference_budget_rows.append({
            'expected_repeat_lookups': expected_repeat_lookups,
            'dynamic_transition_count': plan['dynamic_transition_count'],
            'dynamic_state_counts': plan['dynamic_state_counts'],
            'best_fixed_state_kind': plan['best_fixed_state_kind'],
            'best_fixed_regret_vs_dynamic': plan['best_fixed_regret_vs_dynamic'],
            'transition_penalty_break_even_per_switch_bytes': plan['transition_penalty_break_even_per_switch_bytes'],
            'exact_dynamic_match': plan['best_fixed_regret_vs_dynamic'] == 0.0,
        })

    focal_route_blocks = _fixed_row(focal_plan, 'paged_catalog_with_route_blocks')
    focal_filters = _fixed_row(focal_plan, 'paged_catalog_with_filters')
    focal_paged_only = _fixed_row(focal_plan, 'paged_catalog_only')

    return {
        'focus': 'Measure when a single fixed compact repeat sidecar is good enough over a novel-append horizon so the archive can trade sidecar churn against explicit regret instead of always chasing every staging interval.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'max_unique_appends': MAX_UNIQUE_APPENDS,
        'focal_expected_repeat_lookups': FOCAL_EXPECTED_REPEAT_LOOKUPS,
        'reference_expected_repeat_lookups': REFERENCE_EXPECTED_REPEAT_LOOKUPS,
        'headline_findings': {
            'entry_count': focal_plan['entry_count'],
            'page_count': focal_plan['page_count'],
            'tail_entry_count': focal_plan['tail_entry_count'],
            'route_block_bitmap_len': focal_plan['route_block_bitmap_len'],
            'focal_dynamic_transition_count': focal_plan['dynamic_transition_count'],
            'focal_dynamic_state_counts': focal_plan['dynamic_state_counts'],
            'focal_best_fixed_state_kind': focal_plan['best_fixed_state_kind'],
            'focal_best_fixed_regret_vs_dynamic': focal_plan['best_fixed_regret_vs_dynamic'],
            'focal_best_fixed_regret_share_of_dynamic_objective': focal_plan['best_fixed_regret_share_of_dynamic_objective'],
            'focal_transition_penalty_break_even_per_switch_bytes': focal_plan['transition_penalty_break_even_per_switch_bytes'],
            'focal_route_blocks_regret_vs_dynamic': focal_route_blocks['regret_vs_dynamic'],
            'focal_filters_regret_vs_dynamic': focal_filters['regret_vs_dynamic'],
            'focal_paged_catalog_only_regret_vs_dynamic': focal_paged_only['regret_vs_dynamic'],
            'first_exact_route_block_budget': next(
                row['expected_repeat_lookups']
                for row in reference_budget_rows
                if row['best_fixed_state_kind'] == 'paged_catalog_with_route_blocks' and row['exact_dynamic_match']
            ),
            'main_rule': 'when compact repeat-sidecar transitions are operationally costly, compare their average per-switch cost against the measured fixed-policy regret; once switch cost clears that break-even line, keep the best fixed sidecar instead of replaying every upgrade and downgrade band.',
        },
        'focal_plan': focal_plan,
        'reference_budget_rows': reference_budget_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Fixed-Policy Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- over the next `{report['max_unique_appends']}` novel appends at a focal budget of `{report['focal_expected_repeat_lookups']}` expected repeats, the fully staged dynamic planner uses `{findings['focal_dynamic_transition_count']}` sidecar transitions with state counts `{findings['focal_dynamic_state_counts']}`.",
        f"- the best fixed sidecar at that focal budget is `{findings['focal_best_fixed_state_kind']}` with regret `{findings['focal_best_fixed_regret_vs_dynamic']}` bytes versus the fully dynamic schedule, only `{findings['focal_best_fixed_regret_share_of_dynamic_objective']}` of the dynamic cumulative objective.",
        f"- that means the dynamic schedule only buys about `{findings['focal_transition_penalty_break_even_per_switch_bytes']}` bytes per transition on average before a fixed policy becomes cheaper overall.",
        f"- at the same focal budget, always-on route blocks lose only `{findings['focal_route_blocks_regret_vs_dynamic']}` bytes to the full dynamic schedule, while always-on filters lose `{findings['focal_filters_regret_vs_dynamic']}` and bare pages lose `{findings['focal_paged_catalog_only_regret_vs_dynamic']}`.",
        f"- by `{findings['first_exact_route_block_budget']}` expected repeats, always-on route blocks already match the full dynamic schedule exactly across the whole horizon.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Focal fixed-policy rows',
        '| fixed state | cumulative objective | regret vs dynamic | regret per append state | regret share of dynamic objective | exact dynamic match |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for row in report['focal_plan']['fixed_rows']:
        lines.append(
            f"| `{row['state_kind']}` | {row['cumulative_objective']} | {row['regret_vs_dynamic']} | {row['regret_per_append_state']} | {row['regret_share_of_dynamic_objective']} | {str(row['exact_dynamic_match']).lower()} |"
        )
    lines.extend([
        '',
        '## Reference budgets',
        '| expected repeats | dynamic transitions | dynamic state counts | best fixed state | regret vs dynamic | break-even bytes per switch | exact fixed match |',
        '|---:|---:|---|---|---:|---:|---:|',
    ])
    for row in report['reference_budget_rows']:
        lines.append(
            f"| {row['expected_repeat_lookups']} | {row['dynamic_transition_count']} | `{row['dynamic_state_counts']}` | `{row['best_fixed_state_kind']}` | {row['best_fixed_regret_vs_dynamic']} | {row['transition_penalty_break_even_per_switch_bytes']} | {str(row['exact_dynamic_match']).lower()} |"
        )
    lines.extend([
        '',
        '## Sources',
        '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
        '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`',
    ])
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
