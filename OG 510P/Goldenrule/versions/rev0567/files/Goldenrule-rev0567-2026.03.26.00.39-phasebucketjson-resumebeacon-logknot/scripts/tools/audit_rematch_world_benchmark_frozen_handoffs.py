#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.schema.json'
SEED_BUILDER_SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_seed_example.py'
SECTION_SPECS = [
    {
        'section_path': 'canonicalization_planner_contract',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_canonicalization_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-003', 'SQ-004', 'SQ-005', 'SQ-006', 'SQ-007', 'SQ-008', 'SQ-009', 'SQ-010', 'SQ-011'],
    },
    {
        'section_path': 'winner_triage_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_winner_triage_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-018', 'SQ-019', 'SQ-020', 'SQ-021'],
    },
    {
        'section_path': 'delta_shortlist_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_delta_shortlist_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-022'],
    },
    {
        'section_path': 'paired_ranking_interpretation_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-014', 'SQ-016'],
    },
    {
        'section_path': 'matching_state_interpretation_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_matching_state_interpretation_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-013'],
    },
    {
        'section_path': 'turnover_tempo_interpretation_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-015'],
    },
    {
        'section_path': 'world_semantics_interpretation_handoff',
        'source_path': ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.json',
        'source_kind': 'standalone_handoff_example',
        'linked_question_ids': ['SQ-012'],
    },
    {
        'section_path': 'compact_decision_bundle',
        'source_path': ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json',
        'source_kind': 'standing_decision_contract',
        'linked_question_ids': ['SQ-017', 'SQ-018', 'SQ-019', 'SQ-020', 'SQ-021', 'SQ-022', 'SQ-023', 'SQ-024', 'SQ-025', 'SQ-026'],
    },
]


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _extract_subtree(node: Any, dotted_path: str) -> Any:
    current = node
    for part in dotted_path.split('.'):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f'missing dotted path {dotted_path}')
        current = current[part]
    return copy.deepcopy(current)


def build_receipt(seed: dict[str, Any], seed_path: Path) -> dict[str, Any]:
    seed_builder = _load_module('build_rematch_world_benchmark_seed_example', SEED_BUILDER_SCRIPT)
    rebuilt_seed = seed_builder.build_seed()

    audited_sections: list[dict[str, Any]] = []
    for spec in SECTION_SPECS:
        source_obj = load_json(spec['source_path'])
        seed_subtree = _extract_subtree(seed, spec['section_path'])
        source_sha = _sha256_json(source_obj)
        seed_sha = _sha256_json(seed_subtree)
        audited_sections.append(
            {
                'section_path': spec['section_path'],
                'source_path': _relativize(spec['source_path']),
                'source_kind': spec['source_kind'],
                'linked_question_ids': list(spec['linked_question_ids']),
                'seed_subtree_sha256': seed_sha,
                'source_sha256': source_sha,
                'source_bytes': spec['source_path'].stat().st_size,
                'exact_match': seed_sha == source_sha,
            }
        )

    exact_match_count = sum(1 for row in audited_sections if row['exact_match'])
    mismatch_count = len(audited_sections) - exact_match_count
    seed_sha = _sha256_json(seed)
    rebuilt_seed_sha = _sha256_json(rebuilt_seed)
    rebuilt_matches = seed_sha == rebuilt_seed_sha

    if rebuilt_matches and mismatch_count == 0:
        next_move = (
            'Keep the standing seed frozen, begin fill work from the compact patch path, and rerun this audit whenever any copied handoff or the standing decision contract changes.'
        )
    elif mismatch_count > 0:
        next_move = (
            'Regenerate the drifted standalone handoff examples or rebuild the seed from the current builders before starting new world-dependent fill work.'
        )
    else:
        next_move = (
            'Rebuild the standing seed from scripts/report/build_rematch_world_benchmark_seed_example.py before trusting it as the benchmark fill baseline.'
        )

    return {
        'receipt_kind': 'rematch_world_benchmark_frozen_handoff_audit_receipt',
        'receipt_version': '2026-03-17.rematch_world_benchmark_frozen_handoff_audit_receipt.v1',
        'analysis_script': 'scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py',
        'seed_path': _relativize(seed_path),
        'seed_builder_script': _relativize(SEED_BUILDER_SCRIPT),
        'seed_sha256': seed_sha,
        'rebuilt_seed_sha256': rebuilt_seed_sha,
        'rebuilt_seed_matches_standing_seed': rebuilt_matches,
        'audited_sections': audited_sections,
        'status_counts': {
            'audited_section_count': len(audited_sections),
            'exact_match_count': exact_match_count,
            'mismatch_count': mismatch_count,
            'cited_source_path_count': len({row['source_path'] for row in audited_sections}),
        },
        'archive_posture': {
            'prefer_citation_over_recopy': True,
            'intended_retention_class': 'durable_seed_integrity_receipt',
            'size_discipline_note': 'Carry one tiny rebuild-audit receipt for the frozen copied handoffs instead of reopening or recopying the full seed and its source reports every session.',
        },
        'recommended_next_move': next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit that the standing rematch-world benchmark seed still matches the copied frozen handoff sources and current seed builder.')
    parser.add_argument('seed', nargs='?', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed JSON.')
    parser.add_argument('--output', help='Write the audit receipt to this path instead of stdout.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the standing seed rebuild-matches and every audited section still hash-matches its source.')
    args = parser.parse_args()

    seed_path = Path(args.seed)
    seed = load_json(seed_path)
    receipt = build_receipt(seed, seed_path)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))

    if args.strict and (
        not receipt['rebuilt_seed_matches_standing_seed']
        or receipt['status_counts']['mismatch_count'] != 0
    ):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
