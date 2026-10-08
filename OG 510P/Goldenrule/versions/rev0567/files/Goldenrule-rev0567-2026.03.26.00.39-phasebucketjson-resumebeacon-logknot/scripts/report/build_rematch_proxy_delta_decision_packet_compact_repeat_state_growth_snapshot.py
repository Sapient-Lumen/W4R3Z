#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.md'
MAX_UNIQUE_APPENDS = 256


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



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
    baseline_rows = {row['kind']: row for row in growth['baseline_rows']}
    event_rows = growth['event_rows']
    page_birth_rows = [row for row in event_rows if 'new_page_birth' in row['event_kinds']]
    cliff_rows = [row for row in event_rows if 'route_block_bitmap_cliff' in row['event_kinds']]
    flip_rows = [row for row in event_rows if 'filter_route_state_order_flip' in row['event_kinds']]

    first_page_birth = page_birth_rows[0]
    route_cheaper_rows = [row for row in flip_rows if row['filter_minus_route_compact_state_bytes'] > 0]
    filter_cheaper_rows = [row for row in flip_rows if row['filter_minus_route_compact_state_bytes'] < 0]
    first_route_state_flip = route_cheaper_rows[0]
    first_route_bitmap_cliff = cliff_rows[0]
    second_route_state_flip = route_cheaper_rows[1]
    second_route_bitmap_cliff = cliff_rows[1]

    return {
        'focus': 'Expose the exact compact-repeat sidecar growth cliffs under novel appends so future sessions can combine repeat-budget decisions with the next state-jump horizon.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'max_unique_appends': MAX_UNIQUE_APPENDS,
        'headline_findings': {
            'entry_count': growth['entry_count'],
            'page_count': growth['page_count'],
            'tail_entry_count': growth['tail_entry_count'],
            'route_block_bitmap_len': growth['route_block_bitmap_len'],
            'baseline_filters_compact_state_bytes': baseline_rows['paged_catalog_with_filters']['compact_state_bytes'],
            'baseline_filters_extra_sidecar_state_bytes': baseline_rows['paged_catalog_with_filters']['extra_sidecar_state_bytes'],
            'baseline_route_blocks_compact_state_bytes': baseline_rows['paged_catalog_with_route_blocks']['compact_state_bytes'],
            'baseline_route_blocks_extra_sidecar_state_bytes': baseline_rows['paged_catalog_with_route_blocks']['extra_sidecar_state_bytes'],
            'baseline_filter_minus_route_compact_state_bytes': baseline_rows['paged_catalog_with_filters']['compact_state_bytes'] - baseline_rows['paged_catalog_with_route_blocks']['compact_state_bytes'],
            'first_page_birth_unique_appends': first_page_birth['unique_append_count'],
            'first_page_birth_filter_sidecar_delta_bytes': first_page_birth['filters_extra_sidecar_state_bytes'] - baseline_rows['paged_catalog_with_filters']['extra_sidecar_state_bytes'],
            'first_route_state_flip_unique_appends': first_route_state_flip['unique_append_count'],
            'first_route_state_flip_page_count': first_route_state_flip['page_count'],
            'first_route_state_flip_filter_minus_route_compact_state_bytes': first_route_state_flip['filter_minus_route_compact_state_bytes'],
            'first_route_bitmap_cliff_unique_appends': first_route_bitmap_cliff['unique_append_count'],
            'first_route_bitmap_cliff_page_count': first_route_bitmap_cliff['page_count'],
            'first_route_bitmap_cliff_route_sidecar_delta_bytes': first_route_bitmap_cliff['route_blocks_extra_sidecar_state_bytes'] - first_page_birth['route_blocks_extra_sidecar_state_bytes'],
            'first_route_bitmap_cliff_filter_minus_route_compact_state_bytes': first_route_bitmap_cliff['filter_minus_route_compact_state_bytes'],
            'route_blocks_state_cheaper_interval_before_first_cliff': {
                'start_unique_appends': first_route_state_flip['unique_append_count'],
                'end_unique_appends': first_route_bitmap_cliff['unique_append_count'] - 1,
            },
            'second_route_state_flip_unique_appends': second_route_state_flip['unique_append_count'],
            'second_route_bitmap_cliff_unique_appends': second_route_bitmap_cliff['unique_append_count'],
            'main_rule': 'repeat-budget thresholds are necessary but incomplete: once a sidecar is justified at all, track both the next page-birth count and the next route-block bitmap cliff because route blocks can temporarily become cheaper than filters on pure compact state before the next bitmap-width jump resets that advantage.',
        },
        'event_rows': event_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Growth Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- baseline filtered state is `{findings['baseline_filters_compact_state_bytes']}` bytes (`{findings['baseline_filters_extra_sidecar_state_bytes']}` extra sidecar bytes), while baseline route-block state is `{findings['baseline_route_blocks_compact_state_bytes']}` bytes (`{findings['baseline_route_blocks_extra_sidecar_state_bytes']}` extra sidecar bytes), so filters start ahead by `{abs(findings['baseline_filter_minus_route_compact_state_bytes'])}` bytes.",
        f"- the next new page appears after `{findings['first_page_birth_unique_appends']}` novel appends, and that page birth adds exactly `{findings['first_page_birth_filter_sidecar_delta_bytes']}` filter-sidecar bytes while leaving route-block sidecar bytes flat inside the current bitmap band.",
        f"- route blocks first become state-cheaper than filters after `{findings['first_route_state_flip_unique_appends']}` novel appends at page count `{findings['first_route_state_flip_page_count']}`, where route blocks lead by `{findings['first_route_state_flip_filter_minus_route_compact_state_bytes']}` compact-state bytes.",
        f"- that temporary state advantage lasts for unique-append counts `{findings['route_blocks_state_cheaper_interval_before_first_cliff']['start_unique_appends']}` through `{findings['route_blocks_state_cheaper_interval_before_first_cliff']['end_unique_appends']}` under the current bitmap band.",
        f"- the first route-block bitmap cliff arrives after `{findings['first_route_bitmap_cliff_unique_appends']}` novel appends at page count `{findings['first_route_bitmap_cliff_page_count']}`, where route blocks jump by `{findings['first_route_bitmap_cliff_route_sidecar_delta_bytes']}` sidecar bytes and filters retake the state lead by `{abs(findings['first_route_bitmap_cliff_filter_minus_route_compact_state_bytes'])}` bytes.",
        f"- the same sawtooth repeats later: route blocks become state-cheaper again after `{findings['second_route_state_flip_unique_appends']}` novel appends, then lose that edge again at the next bitmap cliff after `{findings['second_route_bitmap_cliff_unique_appends']}` appends.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Event rows',
    ]
    for row in report['event_rows']:
        lines.append(
            f"- appends `{row['unique_append_count']}` -> events `{row['event_kinds']}`; entries `{row['entry_count']}`, pages `{row['page_count']}`, tail `{row['tail_entry_count']}`, bitmap bytes `{row['route_block_bitmap_len']}`, filters `{row['filters_compact_state_bytes']}`, route blocks `{row['route_blocks_compact_state_bytes']}`, filter-minus-route `{row['filter_minus_route_compact_state_bytes']}`."
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
