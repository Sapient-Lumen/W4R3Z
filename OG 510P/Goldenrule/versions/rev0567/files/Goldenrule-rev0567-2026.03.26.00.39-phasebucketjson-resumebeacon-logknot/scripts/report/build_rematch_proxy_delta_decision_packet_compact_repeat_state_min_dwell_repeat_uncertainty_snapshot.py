#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.md'
REFERENCE_EXPECTED_REPEAT_LOOKUPS_VALUES = [0.15, 0.18, 0.25]
REFERENCE_MINIMUM_GAIN_SHARES = [0.99, 0.95, 0.85]


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
    horizon_metrics = packet.fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=256,
        page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
    )
    uncertainty_rows = []
    for minimum_gain_share in REFERENCE_MINIMUM_GAIN_SHARES:
        uncertainty_rows.append(
            packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty_from_metrics(
                horizon_metrics,
                expected_repeat_lookups_values=REFERENCE_EXPECTED_REPEAT_LOOKUPS_VALUES,
                minimum_gain_share_of_full_dynamic_savings=minimum_gain_share,
            )
        )
    by_share = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in uncertainty_rows}
    return {
        'focus': 'Choose compact repeat-sidecar dwell presets from repeat-uncertainty overlaps so one anchor remains safe even when the archive only knows repeat volume approximately.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'source_frontier_builder': str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'reference_expected_repeat_lookups_values': REFERENCE_EXPECTED_REPEAT_LOOKUPS_VALUES,
        'reference_minimum_gain_shares_of_full_dynamic_savings': REFERENCE_MINIMUM_GAIN_SHARES,
        'headline_findings': {
            'entry_count': horizon_metrics['entry_count'],
            'page_count': horizon_metrics['page_count'],
            'tail_entry_count': horizon_metrics['tail_entry_count'],
            'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
            'ninety_nine_percent_overlap_end_unique_appends': by_share[0.99]['minimum_dwell_overlap_end_unique_appends'],
            'ninety_nine_percent_anchor_minimum_dwell_unique_appends': by_share[0.99]['anchor_minimum_dwell_unique_appends'],
            'ninety_nine_percent_worst_case_gain_share_of_full_dynamic_savings': by_share[0.99]['worst_case_gain_share_of_full_dynamic_savings'],
            'ninety_nine_percent_minimum_selected_transition_count': by_share[0.99]['minimum_selected_transition_count'],
            'ninety_nine_percent_maximum_selected_transition_count': by_share[0.99]['maximum_selected_transition_count'],
            'ninety_five_percent_overlap_end_unique_appends': by_share[0.95]['minimum_dwell_overlap_end_unique_appends'],
            'ninety_five_percent_anchor_minimum_dwell_unique_appends': by_share[0.95]['anchor_minimum_dwell_unique_appends'],
            'ninety_five_percent_anchor_margin_unique_appends': by_share[0.95]['anchor_margin_unique_appends'],
            'ninety_five_percent_worst_case_gain_share_of_full_dynamic_savings': by_share[0.95]['worst_case_gain_share_of_full_dynamic_savings'],
            'ninety_five_percent_minimum_selected_transition_count': by_share[0.95]['minimum_selected_transition_count'],
            'ninety_five_percent_maximum_selected_transition_count': by_share[0.95]['maximum_selected_transition_count'],
            'eighty_five_percent_overlap_end_unique_appends': by_share[0.85]['minimum_dwell_overlap_end_unique_appends'],
            'eighty_five_percent_anchor_minimum_dwell_unique_appends': by_share[0.85]['anchor_minimum_dwell_unique_appends'],
            'eighty_five_percent_anchor_margin_unique_appends': by_share[0.85]['anchor_margin_unique_appends'],
            'eighty_five_percent_worst_case_gain_share_of_full_dynamic_savings': by_share[0.85]['worst_case_gain_share_of_full_dynamic_savings'],
            'eighty_five_percent_minimum_selected_transition_count': by_share[0.85]['minimum_selected_transition_count'],
            'eighty_five_percent_maximum_selected_transition_count': by_share[0.85]['maximum_selected_transition_count'],
            'main_rule': 'when repeat volume is uncertain, choose the midpoint of the widest minimum-dwell overlap that survives the whole repeat band; on the current frontier that means dwell 9 for a robust near-optimal preset and dwell 16 for a broader simplicity-first preset.',
        },
        'uncertainty_rows': uncertainty_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [str(PACKET_PATH.relative_to(ROOT)), str(FRONTIER_BUILDER_PATH.relative_to(ROOT))],
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Minimum-Dwell Repeat-Uncertainty Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- source frontier builder: `{report['source_frontier_builder']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- over the repeat band `{report['reference_expected_repeat_lookups_values'][0]}`–`{report['reference_expected_repeat_lookups_values'][-1]}`, the `0.99`-safe overlap shrinks to dwell `1`–`{findings['ninety_nine_percent_overlap_end_unique_appends']}`; this is the important warning that near-exact tuning is fragile under repeat-budget uncertainty.",
        f"- the robust near-optimal preset is dwell `{findings['ninety_five_percent_anchor_minimum_dwell_unique_appends']}` with a ±`{findings['ninety_five_percent_anchor_margin_unique_appends']}`-append margin; it keeps at least `{findings['ninety_five_percent_worst_case_gain_share_of_full_dynamic_savings']}` of full dynamic savings across the whole band while staying within `{findings['ninety_five_percent_minimum_selected_transition_count']}`–`{findings['ninety_five_percent_maximum_selected_transition_count']}` transitions.",
        f"- the broader simplicity-first preset is dwell `{findings['eighty_five_percent_anchor_minimum_dwell_unique_appends']}` with a ±`{findings['eighty_five_percent_anchor_margin_unique_appends']}`-append margin; it still keeps at least `{findings['eighty_five_percent_worst_case_gain_share_of_full_dynamic_savings']}` of full dynamic savings across the whole band while staying within `{findings['eighty_five_percent_minimum_selected_transition_count']}`–`{findings['eighty_five_percent_maximum_selected_transition_count']}` transitions.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Repeat-uncertainty dwell anchors',
        '| minimum gain share | repeat band | overlap dwell band | anchor dwell | anchor margin | worst-case gain share | transition range |',
        '|---:|---|---|---:|---:|---:|---:|',
    ]
    for row in report['uncertainty_rows']:
        lines.append(f"| {row['minimum_gain_share_of_full_dynamic_savings']} | {row['expected_repeat_lookups_start']}–{row['expected_repeat_lookups_end']} | {row['minimum_dwell_overlap_start_unique_appends']}–{row['minimum_dwell_overlap_end_unique_appends']} | {row['anchor_minimum_dwell_unique_appends']} | {row['anchor_margin_unique_appends']} | {row['worst_case_gain_share_of_full_dynamic_savings']} | {row['minimum_selected_transition_count']}–{row['maximum_selected_transition_count']} |")
    lines.extend(['', '## Anchor details by repeat budget', '| minimum gain share | repeat budget | admissible dwell end | selected transitions at anchor | gain share at anchor | regret vs unbounded dynamic | summary |', '|---:|---:|---:|---:|---:|---:|---|'])
    for row in report['uncertainty_rows']:
        for anchor_row in row['anchor_rows']:
            lines.append(f"| {row['minimum_gain_share_of_full_dynamic_savings']} | {anchor_row['expected_repeat_lookups']} | {anchor_row['admissible_minimum_dwell_end_unique_appends']} | {anchor_row['selected_transition_count']} | {anchor_row['gain_share_of_full_dynamic_savings']} | {anchor_row['regret_vs_unbounded_dynamic']} | {anchor_row['interval_summary']} |")
    lines.extend(['', '## Sources', '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`', '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`'])
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
