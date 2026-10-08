#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
MIN_DWELL_REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.md'
REFERENCE_MINIMUM_GAIN_SHARES = [0.99, 0.95, 0.85, 0.0]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    min_dwell_report = json.loads(MIN_DWELL_REPORT_PATH.read_text())
    frontier = {
        'frontier_rows': min_dwell_report['frontier_rows'],
        'max_unique_appends': min_dwell_report['max_unique_appends'],
        'entry_count': min_dwell_report['headline_findings']['entry_count'],
        'page_count': min_dwell_report['headline_findings']['page_count'],
        'tail_entry_count': min_dwell_report['headline_findings']['tail_entry_count'],
        'route_block_bitmap_len': min_dwell_report['headline_findings']['route_block_bitmap_len'],
    }
    anchor_rows = []
    for minimum_gain_share in REFERENCE_MINIMUM_GAIN_SHARES:
        anchor = packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
            frontier,
            minimum_gain_share_of_full_dynamic_savings=minimum_gain_share,
        )
        anchor_rows.append(anchor)

    anchors_by_share = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in anchor_rows}
    findings = min_dwell_report['headline_findings']
    return {
        'focus': 'Choose robust compact repeat-sidecar dwell presets by anchoring on the midpoint of the widest admissible gain plateau instead of living on a fragile threshold edge.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'source_min_dwell_report': str(MIN_DWELL_REPORT_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': min_dwell_report['deterministic_frontier_packet_count'],
        'default_page_size': min_dwell_report['default_page_size'],
        'max_unique_appends': min_dwell_report['max_unique_appends'],
        'focal_expected_repeat_lookups': min_dwell_report['focal_expected_repeat_lookups'],
        'reference_minimum_gain_shares_of_full_dynamic_savings': REFERENCE_MINIMUM_GAIN_SHARES,
        'headline_findings': {
            'entry_count': findings['entry_count'],
            'page_count': findings['page_count'],
            'tail_entry_count': findings['tail_entry_count'],
            'route_block_bitmap_len': findings['route_block_bitmap_len'],
            'frontier_regime_count': findings['frontier_regime_count'],
            'ninety_nine_percent_anchor_minimum_dwell_unique_appends': anchors_by_share[0.99]['anchor_minimum_dwell_unique_appends'],
            'ninety_nine_percent_anchor_margin_unique_appends': anchors_by_share[0.99]['anchor_margin_unique_appends'],
            'ninety_five_percent_anchor_minimum_dwell_unique_appends': anchors_by_share[0.95]['anchor_minimum_dwell_unique_appends'],
            'ninety_five_percent_anchor_margin_unique_appends': anchors_by_share[0.95]['anchor_margin_unique_appends'],
            'ninety_five_percent_anchor_transition_count': anchors_by_share[0.95]['selected_transition_count'],
            'ninety_five_percent_anchor_gain_share_of_full_dynamic_savings': anchors_by_share[0.95]['gain_share_of_full_dynamic_savings'],
            'eighty_five_percent_anchor_minimum_dwell_unique_appends': anchors_by_share[0.85]['anchor_minimum_dwell_unique_appends'],
            'eighty_five_percent_anchor_margin_unique_appends': anchors_by_share[0.85]['anchor_margin_unique_appends'],
            'eighty_five_percent_anchor_transition_count': anchors_by_share[0.85]['selected_transition_count'],
            'zero_percent_anchor_minimum_dwell_unique_appends': anchors_by_share[0.0]['anchor_minimum_dwell_unique_appends'],
            'zero_percent_anchor_margin_unique_appends': anchors_by_share[0.0]['anchor_margin_unique_appends'],
            'main_rule': 'pick the midpoint of the widest minimum-dwell plateau that still preserves the gain share you care about; on the current frontier that means dwell 13 for near-optimal behavior and dwell 33 for the simpler three-transition policy.',
        },
        'anchor_rows': anchor_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(MIN_DWELL_REPORT_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Minimum-Dwell Anchor Snapshot — 2026-03-07',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- source minimum-dwell report: `{report['source_min_dwell_report']}`.",
        f"- live compact catalog starts at `{findings['entry_count']}` fingerprints across `{findings['page_count']}` pages with tail count `{findings['tail_entry_count']}` and route-block bitmap width `{findings['route_block_bitmap_len']}` bytes.",
        f"- the minimum-dwell frontier still has only `{findings['frontier_regime_count']}` schedule plateaus.",
        f"- to keep at least `0.99` of the dynamic savings, anchor dwell at `{findings['ninety_nine_percent_anchor_minimum_dwell_unique_appends']}`; that sits `{findings['ninety_nine_percent_anchor_margin_unique_appends']}` appends away from either plateau edge.",
        f"- to keep at least `0.95` of the dynamic savings, anchor dwell at `{findings['ninety_five_percent_anchor_minimum_dwell_unique_appends']}`; that keeps `{findings['ninety_five_percent_anchor_gain_share_of_full_dynamic_savings']}` of the full dynamic savings with `{findings['ninety_five_percent_anchor_transition_count']}` transitions and a ±`{findings['ninety_five_percent_anchor_margin_unique_appends']}`-append safety margin.",
        f"- to keep at least `0.85` of the dynamic savings, anchor dwell at `{findings['eighty_five_percent_anchor_minimum_dwell_unique_appends']}`; that collapses to `{findings['eighty_five_percent_anchor_transition_count']}` transitions with a ±`{findings['eighty_five_percent_anchor_margin_unique_appends']}`-append safety margin.",
        f"- if robustness matters more than savings, the widest plateau overall is fixed route blocks: anchor dwell `{findings['zero_percent_anchor_minimum_dwell_unique_appends']}` with a ±`{findings['zero_percent_anchor_margin_unique_appends']}`-append margin.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Gain-share dwell anchors',
        '| minimum gain share | anchor dwell | anchor margin | dwell plateau | selected transitions | actual interval dwell | gain share | regret vs unbounded dynamic | summary |',
        '|---:|---:|---:|---|---:|---:|---:|---:|---|',
    ]
    for row in report['anchor_rows']:
        lines.append(
            f"| {row['minimum_gain_share_of_full_dynamic_savings']} | {row['anchor_minimum_dwell_unique_appends']} | {row['anchor_margin_unique_appends']} | {row['minimum_dwell_start_unique_appends']}–{row['minimum_dwell_end_unique_appends']} | {row['selected_transition_count']} | {row['minimum_interval_dwell_unique_appends']} | {row['gain_share_of_full_dynamic_savings']} | {row['regret_vs_unbounded_dynamic']} | {row['interval_summary']} |"
        )
    lines.extend([
        '',
        '## Sources',
        '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
        '- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json`',
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
