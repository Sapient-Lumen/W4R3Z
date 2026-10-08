#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
LEDGER_PATH = ROOT / 'specs' / 'spec_ledger.yaml'
OUT_JSON = REPORTS / 'rematch_decision_contract_snapshot_20260316.json'
OUT_MD = REPORTS / 'rematch_decision_contract_snapshot_20260316.md'

SOURCE_PATHS = {
    'robustness': REPORTS / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json',
    'live_contenders': REPORTS / 'rematch_proxy_live_contenders_snapshot_20260306.json',
    'winner_certification': REPORTS / 'rematch_proxy_winner_certification_snapshot_20260306.json',
    'materiality_gate': REPORTS / 'rematch_proxy_materiality_gate_snapshot_20260306.json',
    'delta_topology': REPORTS / 'rematch_proxy_delta_topology_snapshot_20260306.json',
    'delta_anchor': REPORTS / 'rematch_proxy_delta_anchor_contract_snapshot_20260306.json',
    'question_targeted_probe': REPORTS / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json',
}

QUESTION_FIELDS = {
    'SQ-017': ['delay_contract.robustness_probe_contract', 'delay_contract.extortion_rows[*].predicted_nonnegative_delay_winner_intervals'],
    'SQ-018': ['delay_contract.extortion_rows[*].predicted_nonnegative_delay_live_contender_set', 'delay_contract.extortion_rows[*].strictly_dominated_policies'],
    'SQ-019': ['winner_contract.panel_rows[*].leader_certified_95_ci', 'winner_contract.panel_rows[*].leader_margin_ci_low', 'winner_contract.panel_rows[*].leader_margin_ci_high'],
    'SQ-020': ['winner_contract.panel_rows[*].paired_seed_count', 'winner_contract.panel_rows[*].triage_status'],
    'SQ-021': ['winner_contract.panel_rows[*].smallest_equivalence_delta_supported_90', 'winner_contract.panel_rows[*].largest_material_delta_supported_90'],
    'SQ-022': ['delta_contract.band_rows[*].parent_band_start_delta', 'delta_contract.band_rows[*].parent_band_end_delta', 'delta_contract.band_rows[*].parent_band_width'],
    'SQ-023': ['delta_contract.band_rows[*].budget_cap_additional_paired_seeds', 'delta_contract.band_rows[*].stays_within_budget_cap'],
    'SQ-024': ['delta_contract.band_rows[*].contains_single_point_knife_edge', 'delta_contract.band_rows[*].parent_anchor_buffer_to_nearest_topology_boundary', 'delta_contract.band_rows[*].topology_preserving_anchor_buffer_to_nearest_topology_boundary'],
    'SQ-025': ['delta_contract.band_rows[*].fragmented_parent_band', 'delta_contract.band_rows[*].parent_anchor_delta'],
    'SQ-026': ['delta_contract.band_rows[*].topology_subband_start_delta', 'delta_contract.band_rows[*].topology_subband_end_delta', 'delta_contract.band_rows[*].topology_preserving_anchor_delta'],
}

QUESTION_SECTION = {
    'SQ-017': 'delay_contract',
    'SQ-018': 'delay_contract',
    'SQ-019': 'winner_contract',
    'SQ-020': 'winner_contract',
    'SQ-021': 'winner_contract',
    'SQ-022': 'delta_contract',
    'SQ-023': 'delta_contract',
    'SQ-024': 'delta_contract',
    'SQ-025': 'delta_contract',
    'SQ-026': 'delta_contract',
}

QUESTION_SOURCES = {
    'SQ-017': [SOURCE_PATHS['robustness'], SOURCE_PATHS['live_contenders']],
    'SQ-018': [SOURCE_PATHS['live_contenders']],
    'SQ-019': [SOURCE_PATHS['winner_certification']],
    'SQ-020': [SOURCE_PATHS['winner_certification'], SOURCE_PATHS['materiality_gate']],
    'SQ-021': [SOURCE_PATHS['materiality_gate']],
    'SQ-022': [SOURCE_PATHS['materiality_gate'], SOURCE_PATHS['delta_topology']],
    'SQ-023': [SOURCE_PATHS['delta_anchor']],
    'SQ-024': [SOURCE_PATHS['delta_topology'], SOURCE_PATHS['delta_anchor']],
    'SQ-025': [SOURCE_PATHS['delta_topology'], SOURCE_PATHS['delta_anchor']],
    'SQ-026': [SOURCE_PATHS['delta_topology'], SOURCE_PATHS['delta_anchor']],
}


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_ledger_questions() -> dict[str, str]:
    rows = json.loads((ROOT / 'docs' / 'spec_evidence_links.json').read_text(encoding='utf-8')) if False else None
    del rows
    import yaml  # local import to keep startup cheap

    entries = yaml.safe_load(LEDGER_PATH.read_text(encoding='utf-8'))
    return {
        str(row['id']): str(row['summary'])
        for row in entries
        if str(row.get('id', '')).startswith('SQ-') and 17 <= int(str(row['id']).split('-')[1]) <= 26
    }


def _triage_status(materiality_row: dict[str, object]) -> str:
    classes = materiality_row['delta_classifications']
    if '0.01' in classes and classes['0.01'] == 'practical_tie':
        return 'certified_practical_tie' if materiality_row['leader_certified_95_ci'] else 'uncertified'
    return 'certified_material_leader' if materiality_row['leader_certified_95_ci'] else 'uncertified'


def build_snapshot() -> dict[str, object]:
    robustness = _load_json(SOURCE_PATHS['robustness'])
    live = _load_json(SOURCE_PATHS['live_contenders'])
    winner = _load_json(SOURCE_PATHS['winner_certification'])
    material = _load_json(SOURCE_PATHS['materiality_gate'])
    topology = _load_json(SOURCE_PATHS['delta_topology'])
    anchor = _load_json(SOURCE_PATHS['delta_anchor'])
    qprobe = _load_json(SOURCE_PATHS['question_targeted_probe'])
    question_summaries = _load_ledger_questions()

    material_rows = {
        (int(row['delay']), int(row['extortion'])): row
        for row in material['panel_rows']
    }
    winner_panel_rows: list[dict[str, object]] = []
    for row in winner['panel_rows']:
        key = (int(row['delay']), int(row['extortion']))
        material_row = material_rows[key]
        winner_panel_rows.append(
            {
                'delay': row['delay'],
                'extortion': row['extortion'],
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_certified_95_ci': row['leader_certified_95_ci'],
                'leader_margin': row['leader_margin'],
                'leader_margin_ci_low': row['leader_margin_ci_low'],
                'leader_margin_ci_high': row['leader_margin_ci_high'],
                'paired_seed_count': row['paired_seed_count'],
                'smallest_equivalence_delta_supported_90': material_row['smallest_equivalence_delta_supported_90'],
                'largest_material_delta_supported_90': material_row['largest_material_delta_supported_90'],
                'triage_status': _triage_status(material_row),
                'delta_classifications': material_row['delta_classifications'],
            }
        )

    delay_headlines = [
        f"Robustness triage collapses strict hazard-normalized cap paths to {robustness['headline_findings']['robustness_triage_class_count_when_w_hazard_gt_0']} classes and still needs only {robustness['headline_findings']['minimum_nonadaptive_probe_count_for_universal_robustness_triage']} fixed probes.",
        f"The most practical portable delay-robustness probe contract is {robustness['headline_findings']['unique_minimal_nonadaptive_probe_caps']}.",
        f"Across the tested delay band, {live['headline_findings']['leaders_observed_anywhere_in_tested_band']} leaders appear anywhere and only {live['headline_findings']['tested_leader_flips_across_adjacent_delays']} adjacent-delay leader flips are observed.",
        'Live contenders and dead contenders can therefore be published as compact extortion-indexed sets plus tested winner intervals instead of a bulky all-policy crossover matrix.',
    ]

    winner_headlines = [
        f"Winner certification currently covers {winner['headline_findings']['certified_leaders_95_ci']} of {winner['headline_findings']['tested_panels']} tested panels at 95% CI.",
        f"The smallest certified leader lower bound is {winner['headline_findings']['smallest_certified_leader_margin_ci_low']}.",
        f"Materiality gating exposes practical ties separately from simulation-noise uncertainty; the supported practical-equivalence window ranges from {material['headline_findings']['smallest_equivalence_delta_supported_panel']['smallest_equivalence_delta_supported_90']} to {material['headline_findings']['largest_equivalence_delta_supported_panel']['smallest_equivalence_delta_supported_90']} across tested panels.",
    ]

    delta_headlines = [
        f"The current proxy yields {topology['headline_findings']['total_parent_bands']} budget-admissible parent delta bands, of which {topology['headline_findings']['fragmented_parent_band_count']} are fragmented.",
        f"Every band in the anchor contract stays within budget cap ({anchor['headline_findings']['topology_preserving_anchor_within_budget_cap_count']} / {anchor['headline_findings']['parent_band_count']}).",
        f"Topology-preserving anchors improve boundary buffer in {anchor['headline_findings']['topology_preserving_anchor_improves_buffer_count']} parent bands, so a compact anchor row is enough to publish no-knife-edge guidance without storing full topology grids.",
        f"Question-targeted probe routing shows the portable overturn-risk contract can stay at {qprobe['headline_findings']['unique_fixed_signature_for_overturn_risk']} and reserve the tail witness for narrower exact-path questions.",
    ]

    extortion_rows = []
    for row in live['extortion_rows']:
        extortion_rows.append(
            {
                'extortion': row['extortion'],
                'predicted_nonnegative_delay_live_contender_set': row['predicted_nonnegative_delay_live_contender_set'],
                'predicted_nonnegative_delay_winner_intervals': row['predicted_nonnegative_delay_winner_intervals'],
                'strictly_dominated_policies': row['strictly_dominated_policies'],
                'tested_band_leader_flips': row['tested_band_leader_flips'],
                'tested_band_pairwise_flips_between_delay0_and_delay2': row['tested_band_pairwise_flips_between_delay0_and_delay2'],
                'tested_band_panel_rows': [
                    {
                        'delay': panel['delay'],
                        'leader': panel['leader'],
                        'runner_up': panel['runner_up'],
                        'leader_gap': panel['leader_gap'],
                    }
                    for panel in row['tested_band_panel_rows']
                ],
            }
        )

    band_rows = []
    for row in anchor['band_rows']:
        band_rows.append(
            {
                'budget_cap_additional_paired_seeds': row['budget_cap_additional_paired_seeds'],
                'parent_band_start_delta': row['parent_band_start_delta'],
                'parent_band_end_delta': row['parent_band_end_delta'],
                'parent_band_width': row['parent_band_width'],
                'fragmented_parent_band': row['fragmented_parent_band'],
                'contains_single_point_knife_edge': row['contains_single_point_knife_edge'],
                'parent_anchor_delta': row['parent_anchor']['delta'],
                'parent_anchor_topology_code': row['parent_anchor']['topology_code'],
                'parent_anchor_counts': row['parent_anchor']['counts'],
                'parent_anchor_buffer_to_nearest_topology_boundary': row['parent_anchor']['buffer_to_nearest_topology_boundary'],
                'topology_preserving_anchor_delta': row['topology_preserving_anchor']['delta'],
                'topology_subband_start_delta': row['topology_preserving_anchor']['topology_subband_start_delta'],
                'topology_subband_end_delta': row['topology_preserving_anchor']['topology_subband_end_delta'],
                'topology_subband_width': row['topology_preserving_anchor']['topology_subband_width'],
                'topology_preserving_anchor_topology_code': row['topology_preserving_anchor']['topology_code'],
                'topology_preserving_anchor_counts': row['topology_preserving_anchor']['counts'],
                'topology_preserving_anchor_buffer_to_nearest_topology_boundary': row['topology_preserving_anchor']['buffer_to_nearest_topology_boundary'],
                'buffer_gain_vs_parent': row['topology_preserving_anchor']['buffer_gain_vs_parent'],
                'same_counts_as_parent': row['topology_preserving_anchor']['same_counts_as_parent'],
                'stays_within_budget_cap': row['topology_preserving_anchor']['stays_within_budget_cap'],
            }
        )

    snapshot: dict[str, object] = {
        'focus': 'collapse the final SG-003 rematch decision backlog to one compact machine-checkable contract surface instead of keeping separate reports for each winner, delay, and delta subquestion',
        'snapshot_date': '2026-03-16',
        'world': {
            'kind': 'rematch_proxy_compact_decision_contract',
            'description': 'Compact phase-3 rematch decision contract assembled from the current exogenous-pool leave/rematch proxy.',
            'tested_delay_levels': [0, 1, 2],
            'tested_extortion_levels': [20, 50, 80],
            'panel_count': len(winner_panel_rows),
            'budget_band_count': len(band_rows),
        },
        'question_coverage': [
            {
                'question_id': qid,
                'question_summary': question_summaries[qid],
                'contract_section': QUESTION_SECTION[qid],
                'minimal_fields': QUESTION_FIELDS[qid],
                'source_reports': [path.relative_to(ROOT).as_posix() for path in QUESTION_SOURCES[qid]],
            }
            for qid in sorted(QUESTION_FIELDS)
        ],
        'delay_contract': {
            'headline_findings': delay_headlines,
            'robustness_probe_contract': {
                'robustness_triage_class_count_when_w_hazard_gt_0': robustness['headline_findings']['robustness_triage_class_count_when_w_hazard_gt_0'],
                'minimum_nonadaptive_probe_count_for_universal_robustness_triage': robustness['headline_findings']['minimum_nonadaptive_probe_count_for_universal_robustness_triage'],
                'unique_minimal_nonadaptive_probe_caps': robustness['headline_findings']['unique_minimal_nonadaptive_probe_caps'],
                'minimum_adaptive_worst_case_probe_count_for_universal_robustness_triage': robustness['headline_findings']['minimum_adaptive_worst_case_probe_count_for_universal_robustness_triage'],
                'adaptive_best_case_probe_count_for_universal_robustness_triage': robustness['headline_findings']['adaptive_best_case_probe_count_for_universal_robustness_triage'],
                'most_practical_probe_contract': robustness['headline_findings']['most_practical_probe_contract'],
            },
            'extortion_rows': extortion_rows,
            'source_reports': [
                SOURCE_PATHS['robustness'].relative_to(ROOT).as_posix(),
                SOURCE_PATHS['live_contenders'].relative_to(ROOT).as_posix(),
                SOURCE_PATHS['question_targeted_probe'].relative_to(ROOT).as_posix(),
            ],
        },
        'winner_contract': {
            'headline_findings': winner_headlines,
            'panel_rows': winner_panel_rows,
            'source_reports': [
                SOURCE_PATHS['winner_certification'].relative_to(ROOT).as_posix(),
                SOURCE_PATHS['materiality_gate'].relative_to(ROOT).as_posix(),
            ],
        },
        'delta_contract': {
            'headline_findings': delta_headlines,
            'band_rows': band_rows,
            'source_reports': [
                SOURCE_PATHS['delta_topology'].relative_to(ROOT).as_posix(),
                SOURCE_PATHS['delta_anchor'].relative_to(ROOT).as_posix(),
                SOURCE_PATHS['question_targeted_probe'].relative_to(ROOT).as_posix(),
            ],
        },
        'component_report_bytes': {
            path.relative_to(ROOT).as_posix(): path.stat().st_size
            for path in SOURCE_PATHS.values()
        },
        'component_report_total_bytes': sum(path.stat().st_size for path in SOURCE_PATHS.values()),
        'analysis_script': 'scripts/report/build_rematch_decision_contract_snapshot.py',
    }
    raw = json.dumps(snapshot, sort_keys=True)
    snapshot['bundle_json_bytes'] = len(raw.encode('utf-8'))
    snapshot['bundle_vs_components_raw_byte_ratio'] = round(
        snapshot['bundle_json_bytes'] / snapshot['component_report_total_bytes'], 6
    )
    return snapshot


def render_md(report: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append('# Rematch decision contract snapshot — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Why this bundle matters')
    lines.append(
        f"- The current phase-3 decision surface spans `{len(report['component_report_bytes'])}` component JSON reports totaling `{report['component_report_total_bytes']}` bytes, while this compact bundle serializes to `{report['bundle_json_bytes']}` bytes (`{report['bundle_vs_components_raw_byte_ratio']}` share)."
    )
    lines.append('- The bundle covers `SQ-017` through `SQ-026` with one machine-checkable surface instead of separate delay, winner, and delta artifacts.')
    lines.append('')
    lines.append('## Question coverage')
    lines.append('| question | section | minimal fields |')
    lines.append('|---|---|---|')
    for row in report['question_coverage']:
        lines.append(f"| `{row['question_id']}` | `{row['contract_section']}` | {', '.join(f'`{item}`' for item in row['minimal_fields'])} |")
    lines.append('')
    lines.append('## Delay contract')
    for item in report['delay_contract']['headline_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('| extortion | live contenders | tested leader flips | pairwise flips delay0→2 |')
    lines.append('|---:|---|---:|---:|')
    for row in report['delay_contract']['extortion_rows']:
        lines.append(
            f"| {row['extortion']} | {', '.join(f'`{policy}`' for policy in row['predicted_nonnegative_delay_live_contender_set'])} | {row['tested_band_leader_flips']} | {row['tested_band_pairwise_flips_between_delay0_and_delay2']} |"
        )
    lines.append('')
    lines.append('## Winner contract')
    for item in report['winner_contract']['headline_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('| extortion | delay | leader | runner-up | certified 95% | triage | eq delta 90 | material delta 90 |')
    lines.append('|---:|---:|---|---|---|---|---:|---:|')
    for row in report['winner_contract']['panel_rows']:
        lines.append(
            f"| {row['extortion']} | {row['delay']} | `{row['leader']}` | `{row['runner_up']}` | `{row['leader_certified_95_ci']}` | `{row['triage_status']}` | {row['smallest_equivalence_delta_supported_90']} | {row['largest_material_delta_supported_90']} |"
        )
    lines.append('')
    lines.append('## Delta contract')
    for item in report['delta_contract']['headline_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('| budget cap | parent band | fragmented | knife-edge | parent buffer | topology anchor | topology buffer |')
    lines.append('|---:|---|---|---|---:|---:|---:|')
    for row in report['delta_contract']['band_rows']:
        lines.append(
            f"| {row['budget_cap_additional_paired_seeds']} | `{row['parent_band_start_delta']}`–`{row['parent_band_end_delta']}` | `{row['fragmented_parent_band']}` | `{row['contains_single_point_knife_edge']}` | {row['parent_anchor_buffer_to_nearest_topology_boundary']} | {row['topology_preserving_anchor_delta']} | {row['topology_preserving_anchor_buffer_to_nearest_topology_boundary']} |"
        )
    lines.append('')
    lines.append('## Inheritor guidance')
    lines.append('1. When phase-3 rematch worlds arrive, emit this compact bundle first and treat the older component reports as optional derivation scratch.')
    lines.append('2. Keep the compact bundle machine-checkable and stable enough for schema validation, then hang any richer exploratory grids off temporary scratch rather than long-term archive state.')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    report = build_snapshot()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-decision-contract: wrote {OUT_JSON}')
    print(f'rematch-decision-contract: wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
