#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json'
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_anchor_contract_snapshot_20260306'


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _find_parent_topology_subband(parent_row: dict) -> dict:
    parent_delta = float(parent_row['parent_anchor_delta'])
    parent_code = str(parent_row['parent_anchor_topology_code'])
    matches = [
        sub
        for sub in parent_row['topology_subbands']
        if float(sub['start_delta']) - 1e-12 <= parent_delta <= float(sub['end_delta']) + 1e-12
    ]
    same_code = [sub for sub in matches if str(sub['topology_code']) == parent_code]
    if same_code:
        return same_code[0]
    if matches:
        return matches[0]
    raise SystemExit(
        'no topology subband contains parent anchor '
        f"cap={parent_row['budget_cap_additional_paired_seeds']} delta={parent_delta}"
    )


def _build_report(topology_report: dict) -> dict:
    band_rows = []
    same_topology = 0
    same_counts = 0
    within_cap = 0
    same_exact_budget = 0
    improved_buffer = 0
    non_improving_rows: list[dict] = []

    for parent_row in topology_report['band_rows']:
        parent_band = _find_parent_topology_subband(parent_row)
        parent_anchor_buffer = float(parent_row['parent_anchor_buffer_to_nearest_topology_boundary'])
        stable_buffer = float(parent_band['stability_anchor_buffer_to_nearest_topology_boundary'])
        stable_budget = int(parent_band['stability_anchor_total_additional_paired_seeds'])
        budget_cap = int(parent_row['budget_cap_additional_paired_seeds'])
        parent_budget = int(parent_row['parent_anchor_total_additional_paired_seeds'])
        same_topology_as_parent = str(parent_band['topology_code']) == str(parent_row['parent_anchor_topology_code'])
        same_counts_as_parent = parent_band['counts'] == parent_row['parent_anchor_counts']
        stays_within_budget_cap = stable_budget <= budget_cap
        same_exact_additional = stable_budget == parent_budget
        buffer_gain = round(stable_buffer - parent_anchor_buffer, 6)

        if same_topology_as_parent:
            same_topology += 1
        if same_counts_as_parent:
            same_counts += 1
        if stays_within_budget_cap:
            within_cap += 1
        if same_exact_additional:
            same_exact_budget += 1
        if buffer_gain > 0:
            improved_buffer += 1
        else:
            non_improving_rows.append(
                {
                    'budget_cap_additional_paired_seeds': budget_cap,
                    'parent_band_start_delta': float(parent_row['parent_band_start_delta']),
                    'parent_band_end_delta': float(parent_row['parent_band_end_delta']),
                    'parent_anchor_delta': float(parent_row['parent_anchor_delta']),
                }
            )

        band_rows.append(
            {
                'budget_cap_additional_paired_seeds': budget_cap,
                'parent_band_start_delta': float(parent_row['parent_band_start_delta']),
                'parent_band_end_delta': float(parent_row['parent_band_end_delta']),
                'parent_band_width': float(parent_row['parent_band_width']),
                'fragmented_parent_band': int(parent_row['topology_subband_count']) > 1,
                'contains_single_point_knife_edge': bool(parent_row['contains_single_point_knife_edge']),
                'parent_anchor': {
                    'delta': float(parent_row['parent_anchor_delta']),
                    'topology_code': str(parent_row['parent_anchor_topology_code']),
                    'counts': parent_row['parent_anchor_counts'],
                    'buffer_to_nearest_topology_boundary': parent_anchor_buffer,
                    'total_additional_paired_seeds': parent_budget,
                },
                'topology_preserving_anchor': {
                    'delta': float(parent_band['stability_anchor_delta']),
                    'topology_subband_start_delta': float(parent_band['start_delta']),
                    'topology_subband_end_delta': float(parent_band['end_delta']),
                    'topology_subband_width': float(parent_band['width']),
                    'topology_code': str(parent_band['topology_code']),
                    'counts': parent_band['counts'],
                    'buffer_to_nearest_topology_boundary': stable_buffer,
                    'buffer_gain_vs_parent': buffer_gain,
                    'total_additional_paired_seeds': stable_budget,
                    'same_topology_as_parent': same_topology_as_parent,
                    'same_counts_as_parent': same_counts_as_parent,
                    'same_exact_additional_paired_seeds_as_parent': same_exact_additional,
                    'stays_within_budget_cap': stays_within_budget_cap,
                },
            }
        )

    report = {
        'focus': 'Convert each budget-admissible rematch delta band into a machine-checkable interior anchor that preserves the inherited parent topology while reducing hidden boundary fragility.',
        'headline_findings': {
            'parent_band_count': len(band_rows),
            'fragmented_parent_band_count': sum(1 for row in band_rows if row['fragmented_parent_band']),
            'parent_anchor_zero_topology_buffer_count': sum(
                1 for row in band_rows
                if row['parent_anchor']['buffer_to_nearest_topology_boundary'] == 0.0
            ),
            'topology_preserving_anchor_improves_buffer_count': improved_buffer,
            'topology_preserving_anchor_same_topology_count': same_topology,
            'topology_preserving_anchor_same_counts_count': same_counts,
            'topology_preserving_anchor_within_budget_cap_count': within_cap,
            'topology_preserving_anchor_same_exact_additional_seed_count': same_exact_budget,
            'only_non_improving_band': non_improving_rows[0] if non_improving_rows else None,
        },
        'method_note': 'For each parent admissible band from the delta-topology snapshot, located the topology-stable subband that contains the inherited parent anchor and then replaced that anchor with the subband midpoint already reported as its stability anchor. This preserves the parent topology/label summary while moving the published anchor into the interior whenever possible.',
        'band_rows': band_rows,
        'source_report': str(TOPOLOGY_PATH.relative_to(ROOT)),
        'source_script': 'scripts/report/build_rematch_proxy_delta_anchor_contract_snapshot.py',
    }
    return report


def _render_markdown(report: dict) -> str:
    findings = report['headline_findings']
    rows = report['band_rows']
    cap10_low = next(
        row for row in rows
        if row['budget_cap_additional_paired_seeds'] == 10 and abs(row['parent_band_start_delta'] - 0.00538) < 1e-9
    )
    lines = [
        '# Rematch-Proxy Delta Anchor Contract Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the existing topology-stable admissible-band report',
        '- for each parent band, located the topology-stable subband that contains the inherited parent anchor',
        '- replaced that boundary-biased parent anchor with the midpoint of the containing topology-stable subband',
        '- recorded whether the replacement preserved topology, preserved counts, preserved exact additional paired seeds, and stayed under the same declared budget cap',
        '',
        'Main findings:',
        f"- there are `{findings['parent_band_count']}` admissible parent bands, of which `{findings['fragmented_parent_band_count']}` split into multiple topology-stable subbands.",
        f"- `{findings['parent_anchor_zero_topology_buffer_count']}` inherited parent anchors sit exactly on a topology boundary (`buffer = 0`).",
        f"- replacing each parent anchor by its topology-preserving interior midpoint improves topology buffer in `{findings['topology_preserving_anchor_improves_buffer_count']}` / `{findings['parent_band_count']}` bands.",
        f"- the replacement preserves parent topology in `{findings['topology_preserving_anchor_same_topology_count']}` / `{findings['parent_band_count']}` bands, preserves parent counts in `{findings['topology_preserving_anchor_same_counts_count']}` / `{findings['parent_band_count']}` bands, and stays within the same declared cap in `{findings['topology_preserving_anchor_within_budget_cap_count']}` / `{findings['parent_band_count']}` bands.",
        f"- exact additional paired seeds stay unchanged in only `{findings['topology_preserving_anchor_same_exact_additional_seed_count']}` / `{findings['parent_band_count']}` bands, so exact cost is not the right anchoring objective once a band has already been declared admissible.",
        f"- focal example: the cap-10 low-delta band `{cap10_low['parent_band_start_delta']:.5f}..{cap10_low['parent_band_end_delta']:.5f}` moves from parent anchor `{cap10_low['parent_anchor']['delta']:.5f}` (buffer `{cap10_low['parent_anchor']['buffer_to_nearest_topology_boundary']:.5f}`) to topology-preserving anchor `{cap10_low['topology_preserving_anchor']['delta']:.5f}` (buffer `{cap10_low['topology_preserving_anchor']['buffer_to_nearest_topology_boundary']:.5f}`) without changing the parent topology code `{cap10_low['parent_anchor']['topology_code']}`.",
        '',
        'Interpretation:',
        '- A min-cost parent anchor is often just the leftmost admissible gridpoint, not a scientifically privileged SESOI. Publishing it as if it were the right anchor launders avoidable boundary fragility into the archive.',
        '- The compact repair is simple: once an admissible parent band exists, normalize any published scalar anchor to the midpoint of the topology-stable subband that actually carries the reported panel-label summary.',
        '',
        'Implementor rule:',
        '- If a rematch benchmark emits one scalar delta anchor per admissible parent band, emit the topology-preserving interior anchor instead of the raw parent-band anchor, and publish its buffer gain to the nearest topology boundary.',
    ]
    return '\n'.join(lines)


def main() -> int:
    topology_report = _read_json(TOPOLOGY_PATH)
    report = _build_report(topology_report)
    REPORT_STEM.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(report) + '\n', encoding='utf-8')
    print(f"wrote {REPORT_STEM.with_suffix('.json')} and {REPORT_STEM.with_suffix('.md')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
