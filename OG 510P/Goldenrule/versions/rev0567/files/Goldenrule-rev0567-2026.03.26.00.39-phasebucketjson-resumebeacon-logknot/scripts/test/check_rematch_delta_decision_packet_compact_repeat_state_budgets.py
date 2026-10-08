#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_budget_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_budget_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt
    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == 274
    assert report['default_page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['compact_repeat_state_kinds'] == list(packet.COMPACT_REPEAT_STATE_KINDS)

    findings = report['headline_findings']
    assert findings['entry_count'] == 274
    assert findings['page_count'] == 18
    assert findings['paged_catalog_only_compact_state_bytes'] == 11770
    assert findings['paged_catalog_only_average_repeat_lookup_bytes'] == 6214.708029
    assert findings['filters_compact_state_bytes'] == 12653
    assert findings['filters_average_repeat_lookup_bytes'] == 1467.306569
    assert findings['route_blocks_compact_state_bytes'] == 12891
    assert findings['route_blocks_average_repeat_lookup_bytes'] == 1101.153285
    assert findings['filters_state_delta_vs_paged_catalog_only'] == 883
    assert findings['route_blocks_state_delta_vs_filters'] == 238
    assert findings['filters_lookup_savings_vs_paged_catalog_only'] == 4747.40146
    assert findings['route_blocks_lookup_savings_vs_filters'] == 366.153284
    assert findings['break_even_repeat_lookups'] == {
        'paged_catalog_only_to_filters': 0.185996,
        'filters_to_route_blocks': 0.650001,
        'paged_catalog_only_to_route_blocks': 0.219221,
    }

    state_rows = {row['kind']: row for row in report['state_rows']}
    assert state_rows['paged_catalog_only']['combined_state_plus_one_repeat_objective'] == 17984.708029
    assert state_rows['paged_catalog_with_filters']['average_false_positive_pages_before_hit'] == 0.510949
    assert state_rows['paged_catalog_with_route_blocks']['combined_state_plus_one_repeat_objective'] == 13992.153285

    budget_rows = {row['expected_repeat_lookups']: row for row in report['budget_rows']}
    assert budget_rows[0.0]['recommended_state_kind'] == 'paged_catalog_only'
    assert budget_rows[0.2]['recommended_state_kind'] == 'paged_catalog_with_filters'
    assert budget_rows[0.5]['recommended_state_kind'] == 'paged_catalog_with_filters'
    assert budget_rows[0.7]['recommended_state_kind'] == 'paged_catalog_with_route_blocks'
    assert budget_rows[1.0]['recommended_state_kind'] == 'paged_catalog_with_route_blocks'
    assert budget_rows[16.0]['combined_objective'] == 30509.45256

    print('compact repeat-state budget snapshot is internally consistent')


if __name__ == '__main__':
    main()
