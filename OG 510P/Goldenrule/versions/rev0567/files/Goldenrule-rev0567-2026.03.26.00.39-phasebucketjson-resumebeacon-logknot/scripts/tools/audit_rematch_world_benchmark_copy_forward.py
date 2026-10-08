#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_SEED_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
SECTION_SPECS = [
    {'section_path': 'canonicalization_planner_contract', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-003', 'SQ-004', 'SQ-005', 'SQ-006', 'SQ-007', 'SQ-008', 'SQ-009', 'SQ-010', 'SQ-011']},
    {'section_path': 'winner_triage_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-018', 'SQ-019', 'SQ-020', 'SQ-021']},
    {'section_path': 'delta_shortlist_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-022']},
    {'section_path': 'paired_ranking_interpretation_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-014', 'SQ-016']},
    {'section_path': 'matching_state_interpretation_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-013']},
    {'section_path': 'turnover_tempo_interpretation_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-015']},
    {'section_path': 'world_semantics_interpretation_handoff', 'source_kind': 'standing_seed', 'linked_question_ids': ['SQ-012']},
    {'section_path': 'compact_decision_bundle', 'source_kind': 'standing_decision_contract', 'linked_question_ids': ['SQ-017', 'SQ-018', 'SQ-019', 'SQ-020', 'SQ-021', 'SQ-022', 'SQ-023', 'SQ-024', 'SQ-025', 'SQ-026']},
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _extract_subtree(node: Any, dotted_path: str) -> Any:
    current = node
    for part in dotted_path.split('.'):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f'missing dotted path {dotted_path}')
        current = current[part]
    return copy.deepcopy(current)


def build_receipt(
    artifact: dict[str, Any],
    artifact_path: Path,
    seed: dict[str, Any],
    seed_path: Path,
    seed_audit: dict[str, Any],
    seed_audit_path: Path,
    decision_contract: dict[str, Any],
    decision_contract_path: Path,
) -> dict[str, Any]:
    audited_sections: list[dict[str, Any]] = []
    for spec in SECTION_SPECS:
        artifact_subtree = _extract_subtree(artifact, spec['section_path'])
        if spec['source_kind'] == 'standing_seed':
            source_obj = _extract_subtree(seed, spec['section_path'])
            source_path = seed_path
        else:
            source_obj = decision_contract
            source_path = decision_contract_path
        artifact_sha = _sha256_json(artifact_subtree)
        source_sha = _sha256_json(source_obj)
        audited_sections.append({
            'section_path': spec['section_path'],
            'source_path': _relativize(source_path),
            'source_kind': spec['source_kind'],
            'linked_question_ids': list(spec['linked_question_ids']),
            'artifact_subtree_sha256': artifact_sha,
            'source_sha256': source_sha,
            'exact_match': artifact_sha == source_sha,
        })
    exact_match_count = sum(1 for row in audited_sections if row['exact_match'])
    mismatch_count = len(audited_sections) - exact_match_count
    if mismatch_count == 0:
        next_move = 'Retain this tiny copy-forward audit beside the compiled artifact and cite the frozen seed audit receipt for the standalone handoff provenance chain.'
    else:
        next_move = 'Do not publish yet; rebuild the compiled artifact from the standing seed or compact patch until every copied handoff and the compact decision bundle match their expected source again.'
    return {
        'receipt_kind': 'rematch_world_benchmark_copy_forward_audit_receipt',
        'receipt_version': '2026-03-17.rematch_world_benchmark_copy_forward_audit_receipt.v1',
        'analysis_script': 'scripts/tools/audit_rematch_world_benchmark_copy_forward.py',
        'artifact_path': _relativize(artifact_path),
        'artifact_sha256': _sha256_json(artifact),
        'seed_path': _relativize(seed_path),
        'seed_sha256': _sha256_json(seed),
        'seed_frozen_handoff_audit_path': _relativize(seed_audit_path),
        'seed_frozen_handoff_audit_sha256': _sha256_json(seed_audit),
        'audited_sections': audited_sections,
        'status_counts': {
            'audited_section_count': len(audited_sections),
            'exact_match_count': exact_match_count,
            'mismatch_count': mismatch_count,
        },
        'archive_posture': {
            'prefer_citation_over_recopy': True,
            'intended_retention_class': 'durable_copy_forward_integrity_receipt',
            'size_discipline_note': 'Carry one small copy-forward receipt for the compiled artifact and rely on the frozen seed audit for standalone handoff provenance instead of duplicating all source digests again.',
        },
        'recommended_next_move': next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit that a filled rematch-world benchmark artifact preserved all copied frozen handoffs and the compact decision bundle unchanged.')
    parser.add_argument('artifact', nargs='?', default=str(DEFAULT_ARTIFACT), help='Path to a compiled benchmark artifact JSON.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed JSON.')
    parser.add_argument('--seed-audit', default=str(DEFAULT_SEED_AUDIT), help='Path to the frozen seed handoff audit receipt JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--output', help='Write the audit receipt to this path instead of stdout.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless every audited copied section matches exactly.')
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    seed_path = Path(args.seed)
    seed_audit_path = Path(args.seed_audit)
    decision_contract_path = Path(args.decision_contract)

    receipt = build_receipt(
        artifact=load_json(artifact_path),
        artifact_path=artifact_path,
        seed=load_json(seed_path),
        seed_path=seed_path,
        seed_audit=load_json(seed_audit_path),
        seed_audit_path=seed_audit_path,
        decision_contract=load_json(decision_contract_path),
        decision_contract_path=decision_contract_path,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))

    if args.strict and receipt['status_counts']['mismatch_count'] != 0:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
