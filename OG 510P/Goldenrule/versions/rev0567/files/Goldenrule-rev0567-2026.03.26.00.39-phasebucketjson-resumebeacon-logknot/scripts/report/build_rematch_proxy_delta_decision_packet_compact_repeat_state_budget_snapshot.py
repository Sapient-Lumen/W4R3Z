#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.md'

BUDGET_CANDIDATES = (0.0, 0.1, 0.2, 0.5, 0.7, 1.0, 2.0, 4.0, 8.0, 16.0)


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
    metrics = packet.fingerprint_catalog_compact_repeat_state_metrics(pages)
    rows = metrics['rows']

    break_even = {
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

    budget_rows = []
    for budget in BUDGET_CANDIDATES:
        recommendation = packet.recommend_fingerprint_catalog_compact_repeat_state(
            pages,
            expected_repeat_lookups=budget,
        )
        budget_rows.append(recommendation)

    return {
        'focus': 'Choose compact repeat sidecars by expected repeat budget instead of inheriting the strongest sidecar unconditionally once the archive starts preserving paged raw-digest catalogs.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'compact_repeat_state_kinds': list(packet.COMPACT_REPEAT_STATE_KINDS),
        'headline_findings': {
            'entry_count': metrics['entry_count'],
            'page_count': metrics['page_count'],
            'paged_catalog_only_compact_state_bytes': rows['paged_catalog_only']['compact_state_bytes'],
            'paged_catalog_only_average_repeat_lookup_bytes': rows['paged_catalog_only']['average_repeat_lookup_bytes'],
            'filters_compact_state_bytes': rows['paged_catalog_with_filters']['compact_state_bytes'],
            'filters_average_repeat_lookup_bytes': rows['paged_catalog_with_filters']['average_repeat_lookup_bytes'],
            'route_blocks_compact_state_bytes': rows['paged_catalog_with_route_blocks']['compact_state_bytes'],
            'route_blocks_average_repeat_lookup_bytes': rows['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'],
            'filters_state_delta_vs_paged_catalog_only': rows['paged_catalog_with_filters']['compact_state_bytes'] - rows['paged_catalog_only']['compact_state_bytes'],
            'route_blocks_state_delta_vs_filters': rows['paged_catalog_with_route_blocks']['compact_state_bytes'] - rows['paged_catalog_with_filters']['compact_state_bytes'],
            'filters_lookup_savings_vs_paged_catalog_only': round(rows['paged_catalog_only']['average_repeat_lookup_bytes'] - rows['paged_catalog_with_filters']['average_repeat_lookup_bytes'], 6),
            'route_blocks_lookup_savings_vs_filters': round(rows['paged_catalog_with_filters']['average_repeat_lookup_bytes'] - rows['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'], 6),
            'break_even_repeat_lookups': break_even,
            'main_rule': 'keep no extra sidecar when expected repeats stay below the measured filters threshold, add aligned page filters once repeats exceed that tiny threshold, and add route blocks once the archive expects at least about one repeat per current catalog because the extra route-block state already pays for itself.',
        },
        'state_rows': [rows[kind] for kind in packet.COMPACT_REPEAT_STATE_KINDS],
        'budget_rows': budget_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Budget Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- live compact page size: `{report['default_page_size']}` across `{findings['page_count']}` pages for `{findings['entry_count']}` semantic fingerprints.",
        f"- paged catalog only: `{findings['paged_catalog_only_compact_state_bytes']}` compact-state bytes and `{findings['paged_catalog_only_average_repeat_lookup_bytes']}` average repeat-lookup bytes.",
        f"- paged catalog + filters: `{findings['filters_compact_state_bytes']}` compact-state bytes and `{findings['filters_average_repeat_lookup_bytes']}` average repeat-lookup bytes.",
        f"- paged catalog + route blocks: `{findings['route_blocks_compact_state_bytes']}` compact-state bytes and `{findings['route_blocks_average_repeat_lookup_bytes']}` average repeat-lookup bytes.",
        f"- filters add only `{findings['filters_state_delta_vs_paged_catalog_only']}` bytes of state while saving `{findings['filters_lookup_savings_vs_paged_catalog_only']}` repeat-lookup bytes on average, so they break even after `{findings['break_even_repeat_lookups']['paged_catalog_only_to_filters']}` expected repeats.",
        f"- route blocks add only `{findings['route_blocks_state_delta_vs_filters']}` bytes beyond filters while saving `{findings['route_blocks_lookup_savings_vs_filters']}` more repeat-lookup bytes on average, so they break even after `{findings['break_even_repeat_lookups']['filters_to_route_blocks']}` expected repeats.",
        f"- direct jump from bare pages to route blocks breaks even after `{findings['break_even_repeat_lookups']['paged_catalog_only_to_route_blocks']}` expected repeats.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## State rows',
    ]
    for row in report['state_rows']:
        lines.append(
            f"- `{row['kind']}`: compact state `{row['compact_state_bytes']}` bytes, avg repeat lookup `{row['average_repeat_lookup_bytes']}`, avg false-positive pages `{row['average_false_positive_pages_before_hit']}`, one-repeat objective `{row['combined_state_plus_one_repeat_objective']}`."
        )
    lines.extend([
        '',
        '## Budget rows',
    ])
    for row in report['budget_rows']:
        winner = row['recommended_state_kind']
        lines.append(
            f"- expected repeats `{row['expected_repeat_lookups']}` -> `{winner}` with combined objective `{row['combined_objective']}`; candidates `{json.dumps(row['candidates'])}`."
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
