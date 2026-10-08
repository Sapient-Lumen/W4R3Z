#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_delta_shortlist_handoff.schema.json'
STRICT_PROFILE_NAME = 'family4_width0p0010_hazard1000_sub0p01'
BROADER_PROFILE_NAME = 'family4_width0p0010_hazard1000'
LINKED_QUESTION_IDS = ['SQ-022', 'SQ-023', 'SQ-024', 'SQ-025', 'SQ-026']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _profile_by_name(report: dict[str, Any], profile_name: str) -> dict[str, Any]:
    for row in report['guardrail_profiles']:
        if row['profile_name'] == profile_name:
            return row
    raise KeyError(f'missing profile {profile_name}')


def _compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'topology_code': row['topology_code'],
        'counts': dict(row['counts']),
        'covered_budget_caps': list(row['covered_budget_caps']),
        'shared_core_start_delta': row['shared_core_start_delta'],
        'shared_core_end_delta': row['shared_core_end_delta'],
        'shared_core_width': row['shared_core_width'],
        'shared_core_anchor_delta': row['shared_core_anchor_delta'],
        'shared_core_anchor_buffer_to_boundary': row['shared_core_anchor_buffer_to_boundary'],
        'min_separation_to_hazard_band_for_additional_budget_cap_1000': row['min_separation_to_hazard_band_for_additional_budget_cap_1000'],
        'min_separation_to_knife_edge_delta': row['min_separation_to_knife_edge_delta'],
    }


def build_handoff(publishability_report: dict[str, Any], decision_contract: dict[str, Any]) -> dict[str, Any]:
    strict_profile = _profile_by_name(publishability_report, STRICT_PROFILE_NAME)
    broader_profile = _profile_by_name(publishability_report, BROADER_PROFILE_NAME)
    first_row = strict_profile['candidate_rows'][0]
    return {
        'contract_kind': 'rematch_world_benchmark_delta_shortlist_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_delta_shortlist_handoff.v1',
        'planner_origin': 'copy the strict proxy-era publishable delta shortlist into the benchmark seed until native rematch worlds can emit their own SESOI-band shortlist',
        'publishability_report_path': 'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
        'publishability_report_sha256': sha256_json(publishability_report),
        'decision_contract_path': 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json',
        'decision_contract_sha256': sha256_json(decision_contract),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'declared_budget_family_caps': list(first_row['covered_budget_caps']),
        'strict_profile': {
            'profile_name': strict_profile['profile_name'],
            'minimum_covered_budget_cap_count': strict_profile['minimum_covered_budget_cap_count'],
            'minimum_shared_core_width': strict_profile['minimum_shared_core_width'],
            'requires_no_overlap_with_hazard_band_for_additional_budget_cap': strict_profile['requires_no_overlap_with_hazard_band_for_additional_budget_cap'],
            'sub_0p01_only': strict_profile['sub_0p01_only'],
            'candidate_count': strict_profile['candidate_count'],
        },
        'primary_shortlist_rows': [_compact_row(row) for row in strict_profile['candidate_rows']],
        'broader_profile_candidate_count': broader_profile['candidate_count'],
        'upgrade_requirement': 'Replace this copied shortlist handoff with world-native SESOI-band outputs once endogenous rematch benchmarks can emit practical-margin frontiers, budget-admissible bands, and topology-stable anchors directly.',
        'size_discipline_note': 'Carry only the strict shortlist rows and source digests inside the benchmark seed; keep wider ladder tables, hazard maps, and cap-by-cap band inventories scratch-only or in cited reports.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact delta-shortlist handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--publishability-report', default=str(PUBLISHABILITY_PATH), help='Path to the proxy delta publishability snapshot JSON.')
    parser.add_argument('--decision-contract', default=str(DECISION_CONTRACT_PATH), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    publishability_path = Path(args.publishability_report)
    if not publishability_path.is_absolute():
        publishability_path = (ROOT / publishability_path).resolve()
    decision_path = Path(args.decision_contract)
    if not decision_path.is_absolute():
        decision_path = (ROOT / decision_path).resolve()

    publishability_report = load_json(publishability_path)
    decision_contract = load_json(decision_path)
    handoff = build_handoff(publishability_report, decision_contract)
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'publishability_report_path': publishability_path.relative_to(ROOT).as_posix() if publishability_path.is_relative_to(ROOT) else str(publishability_path),
            'publishability_report_sha256': handoff['publishability_report_sha256'],
            'decision_contract_sha256': handoff['decision_contract_sha256'],
            'primary_shortlist_count': len(handoff['primary_shortlist_rows']),
            'declared_budget_family_caps': handoff['declared_budget_family_caps'],
            'primary_anchor_deltas': [row['shared_core_anchor_delta'] for row in handoff['primary_shortlist_rows']],
            'broader_profile_candidate_count': handoff['broader_profile_candidate_count'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-delta-shortlist-handoff: wrote {output_path.relative_to(ROOT).as_posix()}')
        return 0

    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
