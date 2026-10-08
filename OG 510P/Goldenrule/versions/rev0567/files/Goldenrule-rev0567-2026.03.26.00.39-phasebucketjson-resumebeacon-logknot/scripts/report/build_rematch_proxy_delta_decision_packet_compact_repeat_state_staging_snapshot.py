#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.md'
EXPECTED_REPEAT_LOOKUPS = 0.18
MAX_UNIQUE_APPENDS = 256


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def _break_even_rows(packet, metrics: dict[str, object]) -> dict[str, float | None]:
    rows = metrics['rows']
    return {
        'paged_catalog_only_to_filters': packet.compact_repeat_state_break_even_repeat_lookups(
            rows['paged_catalog_only']['compact_state_bytes'],
            rows['paged_catalog_only']['average_repeat_lookup_bytes'],
            rows['paged_catalog_with_filters']['compact_state_bytes'],
            rows['paged_catalog_with_filters']['average_repeat_lookup_bytes'],
        ),
        'filters_to_route_blocks': packet.compact_repeat_state_break_even_repeat_lookups(
            rows['paged_catalog_with_filters']['compact_state_bytes'],
            rows['paged_catalog_with_filters']['average_repeat_lookup_bytes'],
            rows['paged_catalog_with_route_blocks']['compact_state_bytes'],
            rows['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'],
        ),
        'paged_catalog_only_to_route_blocks': packet.compact_repeat_state_break_even_repeat_lookups(
            rows['paged_catalog_only']['compact_state_bytes'],
            rows['paged_catalog_only']['average_repeat_lookup_bytes'],
            rows['paged_catalog_with_route_blocks']['compact_state_bytes'],
            rows['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'],
        ),
    }



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    growth = packet.fingerprint_catalog_compact_repeat_state_growth_events(
        pages,
        max_unique_appends=MAX_UNIQUE_APPENDS,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )
    growth_event_kinds = {row['unique_append_count']: row['event_kinds'] for row in growth['event_rows']}
    sample_unique_appends = [0] + [row['unique_append_count'] for row in growth['event_rows']]
    threshold_rows = []
    for unique_append_count in sample_unique_appends:
        projected_pages = packet.project_fingerprint_catalog_pages(
            pages,
            unique_append_count=unique_append_count,
            page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        )
        metrics = packet.fingerprint_catalog_compact_repeat_state_metrics(projected_pages)
        recommendation = packet.recommend_fingerprint_catalog_compact_repeat_state_from_metrics(
            metrics,
            expected_repeat_lookups=EXPECTED_REPEAT_LOOKUPS,
        )
        threshold_rows.append({
            'unique_append_count': unique_append_count,
            'page_count': metrics['page_count'],
            'tail_entry_count': packet.fingerprint_catalog_page_entry_count(projected_pages[-1]),
            'route_block_bitmap_len': packet._fingerprint_catalog_route_block_bitmap_len(metrics['page_count']),
            'event_kinds': growth_event_kinds.get(unique_append_count, []),
            'break_even_repeat_lookups': _break_even_rows(packet, metrics),
            'recommended_state_kind_at_expected_repeat_budget': recommendation['recommended_state_kind'],
        })
    staging = packet.fingerprint_catalog_compact_repeat_state_budget_staging_plan(
        pages,
        expected_repeat_lookups=EXPECTED_REPEAT_LOOKUPS,
        max_unique_appends=MAX_UNIQUE_APPENDS,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )
    interval_rows = staging['interval_rows']
    first_route_interval = next(row for row in interval_rows if row['recommended_state_kind'] == 'paged_catalog_with_route_blocks')
    page_reentry_interval = next(
        row for row in interval_rows
        if row['recommended_state_kind'] == 'paged_catalog_only' and row['start_unique_appends'] >= 100
    )
    filter_reentry_after_cliff = next(
        row for row in interval_rows
        if row['recommended_state_kind'] == 'paged_catalog_with_filters' and row['start_unique_appends'] > page_reentry_interval['end_unique_appends']
    )
    second_route_interval = [row for row in interval_rows if row['recommended_state_kind'] == 'paged_catalog_with_route_blocks'][1]
    final_filter_interval = interval_rows[-1]

    return {
        'focus': 'Expose exact sidecar-churn intervals at a marginal repeat budget so future sessions can downgrade compact repeat sidecars after bitmap cliffs instead of treating sidecars as monotone archive growth.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'expected_repeat_lookups': EXPECTED_REPEAT_LOOKUPS,
        'max_unique_appends': MAX_UNIQUE_APPENDS,
        'headline_findings': {
            'entry_count': staging['entry_count'],
            'page_count': staging['page_count'],
            'tail_entry_count': staging['tail_entry_count'],
            'route_block_bitmap_len': staging['route_block_bitmap_len'],
            'interval_count': len(interval_rows),
            'baseline_break_even_repeat_lookups': threshold_rows[0]['break_even_repeat_lookups'],
            'first_filter_interval': {
                'start_unique_appends': interval_rows[1]['start_unique_appends'],
                'end_unique_appends': interval_rows[1]['end_unique_appends'],
            },
            'first_route_interval': {
                'start_unique_appends': first_route_interval['start_unique_appends'],
                'end_unique_appends': first_route_interval['end_unique_appends'],
            },
            'bitmap_cliff_page_reentry_interval': {
                'start_unique_appends': page_reentry_interval['start_unique_appends'],
                'end_unique_appends': page_reentry_interval['end_unique_appends'],
            },
            'filter_reentry_after_first_cliff': {
                'start_unique_appends': filter_reentry_after_cliff['start_unique_appends'],
                'end_unique_appends': filter_reentry_after_cliff['end_unique_appends'],
            },
            'second_route_interval': {
                'start_unique_appends': second_route_interval['start_unique_appends'],
                'end_unique_appends': second_route_interval['end_unique_appends'],
            },
            'final_filter_interval': {
                'start_unique_appends': final_filter_interval['start_unique_appends'],
                'end_unique_appends': final_filter_interval['end_unique_appends'],
            },
            'main_rule': 'for marginal repeat budgets, compact repeat sidecars should be staged with both upgrades and downgrades: route blocks can become optimal across late pre-cliff bands, then lose that status exactly at the next bitmap cliff, with bare pages or filters temporarily retaking the lead.',
        },
        'threshold_rows': threshold_rows,
        'interval_rows': interval_rows,
        'transition_rows': staging['transition_rows'],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Staging Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- marginal planning budget in this snapshot: `{report['expected_repeat_lookups']}` expected repeat lookups before the next archive-local rewrite decision.",
        f"- baseline repeat thresholds are `{findings['baseline_break_even_repeat_lookups']}`.",
        f"- filters first pay off for appends `{findings['first_filter_interval']['start_unique_appends']}` through `{findings['first_filter_interval']['end_unique_appends']}`.",
        f"- route blocks first become the best compact state for appends `{findings['first_route_interval']['start_unique_appends']}` through `{findings['first_route_interval']['end_unique_appends']}`.",
        f"- the first bitmap cliff causes a bare-page reentry at appends `{findings['bitmap_cliff_page_reentry_interval']['start_unique_appends']}` through `{findings['bitmap_cliff_page_reentry_interval']['end_unique_appends']}`.",
        f"- filters retake the lead immediately after that cliff for appends `{findings['filter_reentry_after_first_cliff']['start_unique_appends']}` through `{findings['filter_reentry_after_first_cliff']['end_unique_appends']}`.",
        f"- route blocks regain the lead across the next late-band window at appends `{findings['second_route_interval']['start_unique_appends']}` through `{findings['second_route_interval']['end_unique_appends']}` before filters return again for `{findings['final_filter_interval']['start_unique_appends']}` through `{findings['final_filter_interval']['end_unique_appends']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Threshold rows',
    ]
    for row in report['threshold_rows']:
        lines.append(
            f"- appends `{row['unique_append_count']}` -> pages `{row['page_count']}`, tail `{row['tail_entry_count']}`, bitmap bytes `{row['route_block_bitmap_len']}`, events `{row['event_kinds']}`, thresholds `{row['break_even_repeat_lookups']}`, winner at `{report['expected_repeat_lookups']}` repeats: `{row['recommended_state_kind_at_expected_repeat_budget']}`."
        )
    lines.extend([
        '',
        '## Exact staging intervals',
    ])
    for row in report['interval_rows']:
        lines.append(
            f"- `{row['recommended_state_kind']}` for appends `{row['start_unique_appends']}`–`{row['end_unique_appends']}`; page band `{row['start_page_count']}`–`{row['end_page_count']}`, tail counts `{row['start_tail_entry_count']}`–`{row['end_tail_entry_count']}`, bitmap bytes `{row['start_route_block_bitmap_len']}`–`{row['end_route_block_bitmap_len']}`."
        )
    lines.extend([
        '',
        '## Transition rows',
    ])
    for row in report['transition_rows']:
        lines.append(
            f"- appends `{row['unique_append_count']}`: `{row['from_state_kind']}` -> `{row['to_state_kind']}` at page `{row['page_count']}` tail `{row['tail_entry_count']}` bitmap bytes `{row['route_block_bitmap_len']}` with thresholds `{row['break_even_repeat_lookups']}`."
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
