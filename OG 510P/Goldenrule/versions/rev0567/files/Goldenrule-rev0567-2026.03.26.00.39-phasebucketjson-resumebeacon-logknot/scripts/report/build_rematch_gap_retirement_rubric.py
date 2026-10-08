#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC_LEDGER = ROOT / 'specs' / 'spec_ledger.yaml'
DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_gap_retirement_rubric_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_gap_retirement_rubric_snapshot_20260316.md'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_gap_retirement_rubric.schema.json'
VALIDATOR_PATH = ROOT / 'scripts' / 'test' / 'check_rematch_gap_retirement_rubric.py'
QUESTION_IDS = [f'SQ-0{i}' for i in range(17, 27)]
ASSUMPTION_BY_QUESTION = {f'SQ-0{i}': f'SA-0{i-1}' for i in range(17, 26 + 1)}
SECTION_FIELD_MAP = {
    'delay_contract': [
        'delay_contract.robustness_probe_contract',
        'delay_contract.extortion_rows[*].predicted_nonnegative_delay_live_contender_set',
        'delay_contract.extortion_rows[*].predicted_nonnegative_delay_winner_intervals',
        'delay_contract.extortion_rows[*].strictly_dominated_policies',
        'delay_contract.extortion_rows[*].tested_band_panel_rows',
    ],
    'winner_contract': [
        'winner_contract.panel_rows[*].leader_certified_95_ci',
        'winner_contract.panel_rows[*].leader_margin',
        'winner_contract.panel_rows[*].leader_margin_ci_low',
        'winner_contract.panel_rows[*].leader_margin_ci_high',
        'winner_contract.panel_rows[*].paired_seed_count',
        'winner_contract.panel_rows[*].triage_status',
        'winner_contract.panel_rows[*].smallest_equivalence_delta_supported_90',
        'winner_contract.panel_rows[*].largest_material_delta_supported_90',
    ],
    'delta_contract': [
        'delta_contract.band_rows[*].parent_band_start_delta',
        'delta_contract.band_rows[*].parent_band_end_delta',
        'delta_contract.band_rows[*].parent_band_width',
        'delta_contract.band_rows[*].budget_cap_additional_paired_seeds',
        'delta_contract.band_rows[*].stays_within_budget_cap',
        'delta_contract.band_rows[*].contains_single_point_knife_edge',
        'delta_contract.band_rows[*].parent_anchor_delta',
        'delta_contract.band_rows[*].parent_anchor_buffer_to_nearest_topology_boundary',
        'delta_contract.band_rows[*].topology_subband_start_delta',
        'delta_contract.band_rows[*].topology_subband_end_delta',
        'delta_contract.band_rows[*].topology_preserving_anchor_delta',
        'delta_contract.band_rows[*].topology_preserving_anchor_buffer_to_nearest_topology_boundary',
    ],
}
SECTION_MIN_COUNTS = {
    'delay_contract': {'extortion_rows': 3},
    'winner_contract': {'panel_rows': 9},
    'delta_contract': {'band_rows': 20},
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_spec_entries() -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(SPEC_LEDGER.read_text(encoding='utf-8'))
    return {entry['id']: entry for entry in data}


def build_snapshot() -> dict[str, Any]:
    spec = load_spec_entries()
    contract = load_json(DECISION_CONTRACT)
    question_coverage = {row['question_id']: row for row in contract['question_coverage']}

    rows: list[dict[str, Any]] = []
    for qid in QUESTION_IDS:
        q = spec[qid]
        aid = ASSUMPTION_BY_QUESTION[qid]
        a = spec[aid]
        coverage = question_coverage[qid]
        section = coverage['contract_section']
        row = {
            'question_id': qid,
            'question_summary': q['summary'],
            'linked_assumption_id': aid,
            'linked_assumption_summary': a['summary'],
            'contract_section': section,
            'section_minimum_shape': SECTION_MIN_COUNTS[section],
            'minimal_fields': coverage['minimal_fields'],
            'section_publication_fields': SECTION_FIELD_MAP[section],
            'schema_specified': True,
            'validator_enforced': True,
            'proxy_emitted': True,
            'world_benchmark_emitted': False,
            'status': 'world_benchmark_pending',
            'question_exit_gap': 'Need at least one endogenous rematch-world benchmark to emit this same compact section under schema validation.',
            'assumption_exit_gap': a['exit_criteria'],
            'source_reports': coverage['source_reports'],
        }
        rows.append(row)

    section_rows: dict[str, list[dict[str, Any]]] = {s: [] for s in SECTION_FIELD_MAP}
    for row in rows:
        section_rows[row['contract_section']].append(row)

    source_reports = sorted(contract['component_report_bytes'])
    component_total_bytes = int(contract['component_report_total_bytes'])
    bundle_json_bytes = int(contract['bundle_json_bytes'])
    ratio = round(bundle_json_bytes / component_total_bytes, 6)

    snapshot = {
        'focus': 'turn the phase-3 SG-003 bundle into an explicit retirement rubric so future sessions stop adding proxy fanout without closing the gap',
        'snapshot_date': '2026-03-16',
        'gap_id': 'SG-003',
        'gap_summary': spec['SG-003']['summary'],
        'decision_contract_path': DECISION_CONTRACT.relative_to(ROOT).as_posix(),
        'decision_contract_schema_path': SCHEMA_PATH.relative_to(ROOT).as_posix().replace('rematch_gap_retirement_rubric.schema.json', 'rematch_decision_contract.schema.json'),
        'decision_contract_validator_path': (ROOT / 'scripts' / 'test' / 'check_rematch_decision_contract.py').relative_to(ROOT).as_posix(),
        'rubric_schema_path': SCHEMA_PATH.relative_to(ROOT).as_posix(),
        'rubric_validator_path': VALIDATOR_PATH.relative_to(ROOT).as_posix(),
        'question_rows': rows,
        'status_counts': {
            'schema_specified_and_validator_enforced': len(rows),
            'proxy_emitted': len(rows),
            'world_benchmark_pending': sum(1 for row in rows if not row['world_benchmark_emitted']),
        },
        'section_status': [
            {
                'contract_section': section,
                'question_ids': [row['question_id'] for row in sec_rows],
                'question_count': len(sec_rows),
                'section_publication_fields': SECTION_FIELD_MAP[section],
                'world_benchmark_emitted': any(row['world_benchmark_emitted'] for row in sec_rows),
            }
            for section, sec_rows in section_rows.items()
        ],
        'closure_order': [
            'keep the compact decision contract as the standing schema/report surface',
            'enforce the contract with validators rather than manual narrative checks',
            'emit the same compact contract from at least one endogenous rematch-world benchmark',
        ],
        'archive_size_reason': {
            'component_report_paths': source_reports,
            'component_report_total_bytes': component_total_bytes,
            'bundle_json_bytes': bundle_json_bytes,
            'bundle_vs_components_raw_byte_ratio': ratio,
            'why_it_matters': 'The archive already has a compact proxy contract; the missing retirement step is world benchmark emission, not more proxy-level report fanout.',
        },
        'recommended_next_move': 'Build one endogenous rematch-world benchmark emission that emits the existing compact decision contract unchanged, then treat richer per-question proxy expansions as scratch unless they become standing evidence.',
    }
    return snapshot


def render_md(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch gap retirement rubric — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {snapshot['focus']}")
    lines.append('')
    lines.append('## Main result')
    lines.append(
        f"- The archive now has the full compact phase-3 decision contract for `SQ-017` through `SQ-026`, but all `{snapshot['status_counts']['world_benchmark_pending']}` question exits still hinge on one missing step: **an endogenous rematch-world benchmark must emit the same compact contract**."
    )
    lines.append(
        f"- The proxy-side contract is already compact enough to keep: `{snapshot['archive_size_reason']['bundle_json_bytes']}` bundle bytes versus `{snapshot['archive_size_reason']['component_report_total_bytes']}` bytes across the source component reports (`{snapshot['archive_size_reason']['bundle_vs_components_raw_byte_ratio']}` share)."
    )
    lines.append('- Therefore the backlog should now collapse by **world emission**, not by adding more proxy-only report variants.')
    lines.append('')
    lines.append('## Retirement status by question')
    lines.append('| question | linked assumption | section | proxy contract | remaining gap |')
    lines.append('|---|---|---|---|---|')
    for row in snapshot['question_rows']:
        lines.append(
            f"| `{row['question_id']}` | `{row['linked_assumption_id']}` | `{row['contract_section']}` | schema+validator+proxy emitted | one endogenous rematch-world benchmark emission |"
        )
    lines.append('')
    lines.append('## Section-level publication surfaces')
    for sec in snapshot['section_status']:
        lines.append(f"### `{sec['contract_section']}`")
        lines.append('')
        lines.append(f"Questions: {', '.join(f'`{q}`' for q in sec['question_ids'])}")
        lines.append('')
        for field in sec['section_publication_fields']:
            lines.append(f"- `{field}`")
        lines.append('')
    lines.append('## Inheritor guidance')
    lines.append('1. Do not grow the archive with additional proxy-only phase-3 reports unless they change the standing contract.')
    lines.append('2. Reuse the existing compact decision bundle fields exactly when the first endogenous rematch-world benchmark lands.')
    lines.append('3. Count `SG-003` phase-3 progress by world-emitted contract sections, not by the number of new proxy derivations.')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-gap-retirement-rubric: wrote {OUT_JSON}')
    print(f'rematch-gap-retirement-rubric: wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
