#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC_LEDGER = ROOT / 'specs' / 'spec_ledger.yaml'
DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.md'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_publication_contract.schema.json'
VALIDATOR_PATH = ROOT / 'scripts' / 'test' / 'check_rematch_world_publication_contract.py'
QUESTION_IDS = [f'SQ-0{i}' for i in range(12, 27)]
ASSUMPTION_BY_QUESTION = {f'SQ-0{i}': f'SA-0{i-1}' for i in range(12, 27)}
WORLD_LAYER = {
    'SQ-012': {
        'contract_section': 'world_semantics_contract',
        'minimal_fields': [
            'world_semantics_contract.role_assignment_policy',
            'world_semantics_contract.asymmetry_trigger_policy',
            'world_semantics_contract.rematch_state_carry_policy',
            'world_semantics_contract.role_swapped_companion_policy',
        ],
        'section_publication_fields': [
            'world_semantics_contract.world_name',
            'world_semantics_contract.role_assignment_policy',
            'world_semantics_contract.asymmetry_trigger_policy',
            'world_semantics_contract.rematch_state_carry_policy',
            'world_semantics_contract.rematch_state_reset_policy',
            'world_semantics_contract.role_swapped_companion_policy',
        ],
        'source_artifacts': [
            'docs/LIBRARY/topics/rematch_role_assignment_is_a_first_class_contract.md',
            'docs/LIBRARY/topics/golden_rule_inheritor_brief.md',
        ],
    },
    'SQ-013': {
        'contract_section': 'matching_state_contract',
        'minimal_fields': [
            'matching_state_contract.rematch_delay_rounds',
            'matching_state_contract.matching_efficiency_model',
            'matching_state_contract.search_state_fields',
            'matching_state_contract.matched_state_fields',
        ],
        'section_publication_fields': [
            'matching_state_contract.rematch_delay_rounds',
            'matching_state_contract.matching_efficiency_model',
            'matching_state_contract.search_state_fields',
            'matching_state_contract.matched_state_fields',
            'matching_state_contract.comparability_note',
        ],
        'source_artifacts': [
            'artifacts/reports/rematch_proxy_matching_friction_snapshot_20260306.json',
            'docs/LIBRARY/topics/rematch_delay_is_not_market_thickness.md',
        ],
    },
    'SQ-014': {
        'contract_section': 'occupancy_accounting_contract',
        'minimal_fields': [
            'occupancy_accounting_contract.policy_rows[*].aggregate_avg_payoff',
            'occupancy_accounting_contract.policy_rows[*].matched_round_share',
            'occupancy_accounting_contract.policy_rows[*].dead_round_share',
            'occupancy_accounting_contract.policy_rows[*].in_match_avg_payoff',
        ],
        'section_publication_fields': [
            'occupancy_accounting_contract.policy_rows[*].policy',
            'occupancy_accounting_contract.policy_rows[*].aggregate_avg_payoff',
            'occupancy_accounting_contract.policy_rows[*].matched_round_share',
            'occupancy_accounting_contract.policy_rows[*].dead_round_share',
            'occupancy_accounting_contract.policy_rows[*].in_match_avg_payoff',
        ],
        'source_artifacts': [
            'artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.json',
            'docs/LIBRARY/topics/rematch_worlds_need_occupancy_accounting.md',
        ],
    },
    'SQ-015': {
        'contract_section': 'turnover_tempo_contract',
        'minimal_fields': [
            'turnover_tempo_contract.policy_rows[*].avg_match_length',
            'turnover_tempo_contract.policy_rows[*].delay_or_search_dead_time',
            'turnover_tempo_contract.policy_rows[*].turnover_metric_label',
        ],
        'section_publication_fields': [
            'turnover_tempo_contract.policy_rows[*].policy',
            'turnover_tempo_contract.policy_rows[*].avg_match_length',
            'turnover_tempo_contract.policy_rows[*].delay_or_search_dead_time',
            'turnover_tempo_contract.policy_rows[*].turnover_metric_label',
        ],
        'source_artifacts': [
            'artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.json',
            'docs/LIBRARY/topics/rematch_delay_tax_scales_with_turnover_tempo.md',
        ],
    },
    'SQ-016': {
        'contract_section': 'paired_ranking_views_contract',
        'minimal_fields': [
            'paired_ranking_views_contract.leaderboard_rows[*].aggregate_rank',
            'paired_ranking_views_contract.leaderboard_rows[*].in_match_rank',
            'paired_ranking_views_contract.leaderboard_rows[*].aggregate_avg_payoff',
            'paired_ranking_views_contract.leaderboard_rows[*].in_match_avg_payoff',
        ],
        'section_publication_fields': [
            'paired_ranking_views_contract.leaderboard_rows[*].policy',
            'paired_ranking_views_contract.leaderboard_rows[*].aggregate_rank',
            'paired_ranking_views_contract.leaderboard_rows[*].in_match_rank',
            'paired_ranking_views_contract.leaderboard_rows[*].aggregate_avg_payoff',
            'paired_ranking_views_contract.leaderboard_rows[*].in_match_avg_payoff',
        ],
        'source_artifacts': [
            'artifacts/reports/rematch_proxy_rank_decomposition_snapshot_20260306.json',
            'docs/LIBRARY/topics/rematch_worlds_need_occupancy_normalized_rankings.md',
        ],
    },
}
SECTION_ORDER = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
    'compact_decision_bundle',
]
SECTION_MIN_SHAPES = {
    'world_semantics_contract': {'required_field_count': 6},
    'matching_state_contract': {'required_field_count': 5},
    'occupancy_accounting_contract': {'policy_row_required_field_count': 5},
    'turnover_tempo_contract': {'policy_row_required_field_count': 4},
    'paired_ranking_views_contract': {'leaderboard_row_required_field_count': 5},
    'compact_decision_bundle': {'required_sections': 3},
}
SECTION_PUBLICATION_FIELDS = {
    **{qid: spec['section_publication_fields'] for qid, spec in WORLD_LAYER.items()},
    'compact_decision_bundle': [
        'compact_decision_bundle.delay_contract',
        'compact_decision_bundle.winner_contract',
        'compact_decision_bundle.delta_contract',
    ],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_spec_entries() -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(SPEC_LEDGER.read_text(encoding='utf-8'))
    return {entry['id']: entry for entry in data}


def build_snapshot() -> dict[str, Any]:
    spec = load_spec_entries()
    decision = load_json(DECISION_CONTRACT)
    decision_rows = {row['question_id']: row for row in decision['question_coverage']}

    rows: list[dict[str, Any]] = []
    for qid in QUESTION_IDS:
        q = spec[qid]
        aid = ASSUMPTION_BY_QUESTION[qid]
        a = spec[aid]
        if qid in WORLD_LAYER:
            layer = WORLD_LAYER[qid]
            row = {
                'question_id': qid,
                'question_summary': q['summary'],
                'linked_assumption_id': aid,
                'linked_assumption_summary': a['summary'],
                'contract_section': layer['contract_section'],
                'minimal_fields': layer['minimal_fields'],
                'section_publication_fields': layer['section_publication_fields'],
                'source_artifacts': layer['source_artifacts'],
                'schema_specified': True,
                'validator_enforced': True,
                'world_benchmark_emitted': False,
                'status': 'world_benchmark_pending',
                'question_exit_gap': 'Need at least one endogenous rematch-world benchmark to emit this section under validation.',
                'assumption_exit_gap': a['exit_criteria'],
            }
        else:
            coverage = decision_rows[qid]
            row = {
                'question_id': qid,
                'question_summary': q['summary'],
                'linked_assumption_id': aid,
                'linked_assumption_summary': a['summary'],
                'contract_section': 'compact_decision_bundle',
                'minimal_fields': coverage['minimal_fields'],
                'section_publication_fields': SECTION_PUBLICATION_FIELDS['compact_decision_bundle'],
                'source_artifacts': coverage['source_reports'],
                'schema_specified': True,
                'validator_enforced': True,
                'world_benchmark_emitted': False,
                'status': 'world_benchmark_pending',
                'question_exit_gap': 'Need at least one endogenous rematch-world benchmark to emit the compact decision bundle under validation.',
                'assumption_exit_gap': a['exit_criteria'],
            }
        rows.append(row)

    section_rows: list[dict[str, Any]] = []
    for section in SECTION_ORDER:
        sec_rows = [row for row in rows if row['contract_section'] == section]
        publication_fields = (
            SECTION_PUBLICATION_FIELDS['compact_decision_bundle']
            if section == 'compact_decision_bundle'
            else next(row['section_publication_fields'] for row in sec_rows)
        )
        section_entry = {
            'contract_section': section,
            'question_ids': [row['question_id'] for row in sec_rows],
            'question_count': len(sec_rows),
            'minimum_shape': SECTION_MIN_SHAPES[section],
            'section_publication_fields': publication_fields,
            'world_benchmark_emitted': False,
        }
        if section == 'compact_decision_bundle':
            section_entry['decision_contract_path'] = DECISION_CONTRACT.relative_to(ROOT).as_posix()
            section_entry['decision_contract_schema_path'] = 'schemas/rematch_decision_contract.schema.json'
            section_entry['decision_contract_validator_path'] = 'scripts/test/check_rematch_decision_contract.py'
        section_rows.append(section_entry)

    world_qids = [qid for qid in QUESTION_IDS if qid in WORLD_LAYER]
    phase3_qids = [qid for qid in QUESTION_IDS if qid not in WORLD_LAYER]
    snapshot = {
        'focus': 'define the first endogenous rematch-world benchmark as one compact publication contract so SG-003 closes by one emission target instead of scattered artifact growth',
        'snapshot_date': '2026-03-16',
        'gap_id': 'SG-003',
        'gap_summary': spec['SG-003']['summary'],
        'publication_contract_shape': {
            'benchmark_kind': 'endogenous_rematch_world_publication_contract',
            'required_sections': SECTION_ORDER,
            'section_count': len(SECTION_ORDER),
            'resolves_question_count': len(rows),
            'post_canonicalization_question_count': len(rows),
            'decision_contract_path': DECISION_CONTRACT.relative_to(ROOT).as_posix(),
            'decision_contract_schema_path': 'schemas/rematch_decision_contract.schema.json',
            'decision_contract_validator_path': 'scripts/test/check_rematch_decision_contract.py',
        },
        'question_rows': rows,
        'section_rows': section_rows,
        'layer_rows': [
            {
                'layer': 'world_semantics_and_matching_state',
                'question_ids': ['SQ-012', 'SQ-013'],
                'section_count': 2,
                'why_it_exists': 'The benchmark must say how roles, rematch state, and matched-vs-searching state are defined before welfare claims are comparable.',
            },
            {
                'layer': 'occupancy_turnover_and_rank_views',
                'question_ids': ['SQ-014', 'SQ-015', 'SQ-016'],
                'section_count': 3,
                'why_it_exists': 'The benchmark must separate aggregate welfare from occupancy and tempo effects before leader claims are interpretable.',
            },
            {
                'layer': 'compact_decision_bundle',
                'question_ids': phase3_qids,
                'section_count': 1,
                'why_it_exists': 'Once the first two layers are explicit, the benchmark should emit the existing delay, winner, and delta bundle unchanged.',
            },
        ],
        'status_counts': {
            'schema_specified_and_validator_enforced': len(rows),
            'world_benchmark_pending': len(rows),
            'newly_schema_specified_world_questions': len(world_qids),
            'decision_bundle_questions': len(phase3_qids),
        },
        'main_findings': [
            'After canonicalization, the remaining rematch-world closure surface collapses to one benchmark artifact family covering SQ-012 through SQ-026.',
            'Five previously narrative-only world-semantics / comparability questions now have one machine-checkable publication target rather than scattered implementor folklore.',
            'The ten phase-3 decision questions should not regrow into separate benchmark subreports; the benchmark should reuse the standing compact decision bundle unchanged.',
        ],
        'recommended_next_move': 'Implement one endogenous rematch-world benchmark that emits these six sections in one retained JSON artifact, then judge SG-003 progress by emitted sections rather than by new proxy analyses.',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'schema_path': SCHEMA_PATH.relative_to(ROOT).as_posix(),
        'validator_path': VALIDATOR_PATH.relative_to(ROOT).as_posix(),
    }
    return snapshot


def render_md(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch world publication contract snapshot — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {snapshot['focus']}")
    lines.append('')
    lines.append('## Main result')
    lines.append(
        f"- After canonicalization, the remaining rematch-world closure surface can be treated as **one benchmark publication contract** with `{snapshot['publication_contract_shape']['section_count']}` sections covering `{snapshot['publication_contract_shape']['resolves_question_count']}` open questions (`SQ-012` through `SQ-026`)."
    )
    lines.append(
        f"- This pass newly makes `{snapshot['status_counts']['newly_schema_specified_world_questions']}` world-semantics / comparability questions machine-checkable instead of leaving them as prose-only inheritor guidance."
    )
    lines.append(
        f"- The standing phase-3 decision bundle remains the long-term retained decision surface for the final `{snapshot['status_counts']['decision_bundle_questions']}` questions; the first real rematch world should emit it unchanged rather than regrowing per-question fanout."
    )
    lines.append('')
    lines.append('## Section layout for the first endogenous rematch benchmark')
    lines.append('| contract section | questions | minimum shape |')
    lines.append('|---|---|---|')
    for row in snapshot['section_rows']:
        min_shape = ', '.join(f"{k}={v}" for k, v in row['minimum_shape'].items())
        lines.append(
            f"| `{row['contract_section']}` | {', '.join(f'`{qid}`' for qid in row['question_ids'])} | {min_shape} |"
        )
    lines.append('')
    lines.append('## Question coverage')
    lines.append('| question | assumption | section | minimal fields | remaining gap |')
    lines.append('|---|---|---|---|---|')
    for row in snapshot['question_rows']:
        lines.append(
            f"| `{row['question_id']}` | `{row['linked_assumption_id']}` | `{row['contract_section']}` | {'<br>'.join(f'`{field}`' for field in row['minimal_fields'])} | one endogenous rematch-world benchmark emission |"
        )
    lines.append('')
    lines.append('## Inheritor guidance')
    lines.append('1. Treat `SQ-012` through `SQ-026` as one post-canonicalization benchmark-emission target, not as fifteen separate archive-growth prompts.')
    lines.append('2. Emit the first five sections to make world semantics / comparability explicit, then reuse the existing compact decision bundle for the last ten questions.')
    lines.append('3. Keep richer derived tables or plots as scratch unless they become standing evidence required by a validator.')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-publication-contract: wrote {OUT_JSON}')
    print(f'rematch-world-publication-contract: wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
