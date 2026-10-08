#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
DEFAULT_CANDIDATE = DEFAULT_SEED
WORLD_SECTION_ROWS = [
    {
        'prefix': 'world_semantics_contract',
        'mutation_kind': 'world_section_fill',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-012'],
        'reason': 'Fill the world semantics section in place rather than opening separate semantics sidecars.',
    },
    {
        'prefix': 'matching_state_contract',
        'mutation_kind': 'world_section_fill',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-013'],
        'reason': 'Bind rematch delay and matched-vs-search state directly inside the retained benchmark artifact.',
    },
    {
        'prefix': 'occupancy_accounting_contract.policy_rows',
        'mutation_kind': 'world_section_fill',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-014'],
        'reason': 'Permit row additions and metric fills inside occupancy accounting without growing separate retained sidecars.',
    },
    {
        'prefix': 'turnover_tempo_contract.policy_rows',
        'mutation_kind': 'world_section_fill',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-015'],
        'reason': 'Permit row additions and metric fills inside turnover tempo without mutating copied decision-contract state.',
    },
    {
        'prefix': 'paired_ranking_views_contract.leaderboard_rows',
        'mutation_kind': 'world_section_fill',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-016'],
        'reason': 'Permit leaderboard row expansion while keeping the benchmark as one retained artifact.',
    },
]
ALLOWED_MUTABLE_PREFIX_ROWS = [
    {
        'prefix': 'artifact_state',
        'mutation_kind': 'metadata_transition',
        'required_change_for_publishable': True,
        'linked_question_ids': [],
        'reason': 'A publishable benchmark must transition from seed_template to filled_benchmark.',
    },
    {
        'prefix': 'benchmark_id',
        'mutation_kind': 'metadata_binding',
        'required_change_for_publishable': True,
        'linked_question_ids': [],
        'reason': 'The retained artifact should be bound to one concrete endogenous rematch benchmark identifier.',
    },
    {
        'prefix': 'section_status.world_semantics_contract',
        'mutation_kind': 'section_status_flip',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-012'],
        'reason': 'The world semantics section must flip from pending_fill to filled at publication time.',
    },
    {
        'prefix': 'section_status.matching_state_contract',
        'mutation_kind': 'section_status_flip',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-013'],
        'reason': 'The matching-state section must flip from pending_fill to filled at publication time.',
    },
    {
        'prefix': 'section_status.occupancy_accounting_contract',
        'mutation_kind': 'section_status_flip',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-014'],
        'reason': 'The occupancy-accounting section must flip from pending_fill to filled at publication time.',
    },
    {
        'prefix': 'section_status.turnover_tempo_contract',
        'mutation_kind': 'section_status_flip',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-015'],
        'reason': 'The turnover-tempo section must flip from pending_fill to filled at publication time.',
    },
    {
        'prefix': 'section_status.paired_ranking_views_contract',
        'mutation_kind': 'section_status_flip',
        'required_change_for_publishable': True,
        'linked_question_ids': ['SQ-016'],
        'reason': 'The paired-ranking section must flip from pending_fill to filled at publication time.',
    },
    *WORLD_SECTION_ROWS,
]
FROZEN_PREFIX_ROWS = [
    {
        'prefix': 'artifact_version',
        'frozen_kind': 'metadata_version_lock',
        'reason': 'The filled artifact should complete the standing seed contract rather than silently redefining its version.',
    },
    {
        'prefix': 'benchmark_kind',
        'frozen_kind': 'metadata_identity_lock',
        'reason': 'The benchmark kind should remain the standing endogenous rematch benchmark contract.',
    },
    {
        'prefix': 'publication_contract_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Publication-contract pointers should remain frozen so the retained artifact stays anchored to one standing benchmark contract.',
    },
    {
        'prefix': 'publication_contract_schema_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Publication-contract pointers should remain frozen so the retained artifact stays anchored to one standing benchmark contract.',
    },
    {
        'prefix': 'publication_contract_validator_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Publication-contract pointers should remain frozen so the retained artifact stays anchored to one standing benchmark contract.',
    },
    {
        'prefix': 'decision_contract_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Decision-contract pointers should remain frozen so phase-3 semantics do not drift during world fill work.',
    },
    {
        'prefix': 'decision_contract_schema_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Decision-contract pointers should remain frozen so phase-3 semantics do not drift during world fill work.',
    },
    {
        'prefix': 'decision_contract_validator_path',
        'frozen_kind': 'contract_pointer_lock',
        'reason': 'Decision-contract pointers should remain frozen so phase-3 semantics do not drift during world fill work.',
    },
    {
        'prefix': 'required_sections',
        'frozen_kind': 'shape_lock',
        'reason': 'The benchmark should preserve the standing six-section publication shape.',
    },
    {
        'prefix': 'recommended_fill_order',
        'frozen_kind': 'workflow_lock',
        'reason': 'The seed already encodes the intended compact fill order; later notes should not rewrite it ad hoc.',
    },
    {
        'prefix': 'section_status.canonicalization_planner_contract',
        'frozen_kind': 'status_lock',
        'reason': 'The copied canonicalization planner handoff should remain marked as copied_from_bridge_contract.',
    },
    {
        'prefix': 'section_status.world_semantics_interpretation_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied world-semantics interpretation handoff should remain marked as copied_from_sq012_contract.',
    },
    {
        'prefix': 'world_semantics_interpretation_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied world-semantics interpretation handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'canonicalization_planner_contract',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied canonicalization planner handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.winner_triage_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied winner triage handoff should remain marked as copied_from_proxy_winner_triage_contract.',
    },
    {
        'prefix': 'winner_triage_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied winner triage handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.delta_shortlist_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied delta shortlist handoff should remain marked as copied_from_publishability_contract.',
    },
    {
        'prefix': 'delta_shortlist_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied delta shortlist handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.paired_ranking_interpretation_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied paired-ranking interpretation handoff should remain marked as copied_from_proxy_rank_interpretation_contract.',
    },
    {
        'prefix': 'paired_ranking_interpretation_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied paired-ranking interpretation handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.matching_state_interpretation_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied matching-state interpretation handoff should remain marked as copied_from_proxy_matching_interpretation_contract.',
    },
    {
        'prefix': 'matching_state_interpretation_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied matching-state interpretation handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.turnover_tempo_interpretation_handoff',
        'frozen_kind': 'status_lock',
        'reason': 'The copied turnover-tempo interpretation handoff should remain marked as copied_from_proxy_turnover_tempo_contract.',
    },
    {
        'prefix': 'turnover_tempo_interpretation_handoff',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied turnover-tempo interpretation handoff is frozen and must not drift while world-dependent fields are being filled.',
    },
    {
        'prefix': 'section_status.compact_decision_bundle',
        'frozen_kind': 'status_lock',
        'reason': 'The copied compact decision bundle should remain marked as copied_from_standing_contract.',
    },
    {
        'prefix': 'compact_decision_bundle',
        'frozen_kind': 'copied_contract_lock',
        'reason': 'The copied compact decision bundle is frozen and must not be edited while world-dependent fields are being filled.',
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_completion_gate_module() -> Any:
    path = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_completion_gate.py'
    spec = importlib.util.spec_from_file_location('rematch_world_benchmark_completion_gate', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load completion gate module from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _flatten(node: Any, path: str = '') -> dict[str, Any]:
    rows: dict[str, Any] = {}
    if isinstance(node, dict):
        if not node:
            rows[path] = {}
            return rows
        for key, value in node.items():
            child = f'{path}.{key}' if path else key
            rows.update(_flatten(value, child))
        return rows
    if isinstance(node, list):
        if not node:
            rows[path] = []
            return rows
        for idx, value in enumerate(node):
            child = f'{path}[{idx}]'
            rows.update(_flatten(value, child))
        return rows
    rows[path] = node
    return rows


def _path_matches_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f'{prefix}.') or path.startswith(f'{prefix}[')


def _matching_rule(path: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in rows:
        if _path_matches_prefix(path, row['prefix']):
            return row
    return None


def inspect_candidate_mutations(candidate: dict[str, Any], seed: dict[str, Any], decision_contract: dict[str, Any]) -> dict[str, Any]:
    completion_gate = _load_completion_gate_module()
    candidate_flat = _flatten(candidate)
    seed_flat = _flatten(seed)
    changed_paths = sorted(path for path in set(seed_flat) | set(candidate_flat) if seed_flat.get(path) != candidate_flat.get(path))

    allowed_rows: list[dict[str, Any]] = []
    forbidden_rows: list[dict[str, Any]] = []
    for path in changed_paths:
        matching_row = _matching_rule(path, ALLOWED_MUTABLE_PREFIX_ROWS)
        if matching_row is not None:
            allowed_rows.append(
                {
                    'path': path,
                    'matched_prefix': matching_row['prefix'],
                    'mutation_kind': matching_row['mutation_kind'],
                    'linked_question_ids': matching_row['linked_question_ids'],
                }
            )
            continue
        frozen = _matching_rule(path, FROZEN_PREFIX_ROWS)
        forbidden_rows.append(
            {
                'path': path,
                'matched_frozen_prefix': frozen['prefix'] if frozen else None,
                'frozen_kind': frozen['frozen_kind'] if frozen else 'unclassified_frozen_surface',
                'reason': frozen['reason'] if frozen else 'Changed path lies outside the seed edit surface and should remain frozen.',
            }
        )

    unchanged_required_rows = []
    for row in ALLOWED_MUTABLE_PREFIX_ROWS:
        if row['required_change_for_publishable'] and not any(_path_matches_prefix(path, row['prefix']) for path in changed_paths):
            unchanged_required_rows.append(
                {
                    'prefix': row['prefix'],
                    'mutation_kind': row['mutation_kind'],
                    'linked_question_ids': row['linked_question_ids'],
                    'reason': row['reason'],
                }
            )

    completion = completion_gate.summarize_completion_status(candidate, decision_contract)
    return {
        'mutation_surface_ok': not forbidden_rows,
        'completion_ready': completion['completion_ready'],
        'changed_path_rows': allowed_rows,
        'forbidden_changed_path_rows': forbidden_rows,
        'unchanged_required_mutation_rows': unchanged_required_rows,
        'allowed_decision_null_rows': completion['allowed_decision_null_rows'],
        'status_counts': {
            'changed_path_count': len(changed_paths),
            'allowed_changed_path_count': len(allowed_rows),
            'forbidden_changed_path_count': len(forbidden_rows),
            'unchanged_required_mutation_prefix_count': len(unchanged_required_rows),
            'allowed_decision_null_count': completion['status_counts']['allowed_decision_null_count'],
            'blocking_fill_slot_count': completion['status_counts']['blocking_slot_count'],
        },
        'completion_gate_summary': completion,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Guard the edit surface of a rematch-world benchmark so only seed-designated prefixes mutate during fill work.')
    parser.add_argument('artifact', nargs='?', default=str(DEFAULT_CANDIDATE), help='Path to the candidate benchmark artifact to inspect.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed artifact.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--json', action='store_true', help='Emit the full mutation summary as JSON.')
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    seed_path = Path(args.seed)
    decision_path = Path(args.decision_contract)

    artifact = load_json(artifact_path)
    seed = load_json(seed_path)
    decision = load_json(decision_path)
    summary = inspect_candidate_mutations(artifact, seed, decision)
    summary['artifact_path'] = artifact_path.resolve().relative_to(ROOT).as_posix() if artifact_path.resolve().is_relative_to(ROOT) else str(artifact_path)
    summary['seed_path'] = seed_path.resolve().relative_to(ROOT).as_posix() if seed_path.resolve().is_relative_to(ROOT) else str(seed_path)
    summary['decision_contract_path'] = decision_path.resolve().relative_to(ROOT).as_posix() if decision_path.resolve().is_relative_to(ROOT) else str(decision_path)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    mutation_state = 'edit-surface-ok' if summary['mutation_surface_ok'] else 'edit-surface-violation'
    completion_state = 'publication-ready' if summary['completion_ready'] else 'not-ready'
    print(
        'rematch-world-benchmark-mutation-guard: '
        f"{mutation_state}, {completion_state} "
        f"({summary['status_counts']['allowed_changed_path_count']} allowed changed paths, "
        f"{summary['status_counts']['forbidden_changed_path_count']} forbidden changed paths, "
        f"{summary['status_counts']['blocking_fill_slot_count']} remaining fill blockers)"
    )
    return 0 if summary['mutation_surface_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
