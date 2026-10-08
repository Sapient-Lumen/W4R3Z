#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_catalog_page_size_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    builder = _load_module(REPORT_BUILDER_PATH, 'catalog_page_size_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt
    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == 274
    assert report['headline_findings']['page_size_candidates'] == list(packet.FILTERED_FINGERPRINT_CATALOG_PAGE_SIZE_CANDIDATES) == [8, 16, 32, 64, 128]
    assert report['headline_findings']['default_page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['headline_findings']['legacy_page_size'] == 64
    assert report['headline_findings']['best_lookup_page_size'] == 8
    assert report['headline_findings']['best_power_of_two_combined_objective_page_size'] == 16
    assert report['headline_findings']['best_power_of_two_combined_objective_value'] == 14120.306569
    assert report['headline_findings']['default_full_compact_state_bytes'] == 12653
    assert report['headline_findings']['legacy_full_compact_state_bytes'] == 11960
    assert report['headline_findings']['default_minus_legacy_compact_state_bytes'] == 693
    assert report['headline_findings']['default_average_repeat_lookup_bytes_with_filters'] == 1467.306569
    assert report['headline_findings']['legacy_average_repeat_lookup_bytes_with_filters'] == 3850.540146
    assert report['headline_findings']['default_lookup_bytes_saved_vs_legacy'] == 2383.233577
    assert report['headline_findings']['default_lookup_savings_share_vs_legacy'] == 0.618935

    rows = {row['page_size']: row for row in report['candidate_rows']}
    assert rows[8]['average_repeat_lookup_bytes_with_filters'] == 1379.390511
    assert rows[8]['full_compact_state_bytes'] == 13571
    assert rows[16]['page_count'] == 18
    assert rows[16]['page_bytes'] == [686] * 17 + [89]
    assert rows[16]['page_filter_bytes'] == [48] * 18
    assert rows[16]['combined_state_plus_lookup_objective'] == 14120.306569
    assert rows[64]['page_count'] == 5
    assert rows[64]['page_bytes'] == [2734, 2734, 2734, 2734, 772]
    assert rows[128]['average_false_positive_pages_before_hit'] == 0.244526

    print('decision-packet-catalog-page-sizes: ok')


if __name__ == '__main__':
    main()
