#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
MATCHING_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_matching_friction_snapshot_20260306.json'
OCCUPANCY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_matching_state_interpretation_handoff.schema.json'
LINKED_QUESTION_IDS = ['SQ-013']
SEARCH_STATE_FIELDS = ['searching_round_share', 'search_wait_rounds_avg']
MATCHED_STATE_FIELDS = ['matched_round_share', 'current_match_length']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def build_handoff(matching_report: dict[str, Any], occupancy_report: dict[str, Any]) -> dict[str, Any]:
    matching_headline = matching_report['headline_findings']
    occupancy_headline = occupancy_report['headline_findings']
    ranked_mean_delay_tax = matching_report['ranked_mean_delay_tax']
    return {
        'contract_kind': 'rematch_world_benchmark_matching_state_interpretation_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_matching_state_interpretation_handoff.v1',
        'planner_origin': 'copy the current proxy-era matching-friction and occupancy interpretation into the benchmark seed until native rematch worlds can emit matching-state sections directly',
        'matching_friction_report_path': 'artifacts/reports/rematch_proxy_matching_friction_snapshot_20260306.json',
        'matching_friction_report_sha256': sha256_json(matching_report),
        'occupancy_accounting_report_path': 'artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.json',
        'occupancy_accounting_report_sha256': sha256_json(occupancy_report),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'tested_policy_ids': list(occupancy_report['tested_policies']),
        'tested_extortion_values': list(occupancy_report['extortion_levels']),
        'tested_delay_values': list(occupancy_report['delay_levels']),
        'delay_tax_summary': {
            'tested_cells': matching_headline['tested_cells'],
            'all_tested_policy_extortion_cells_are_monotone_in_delay': matching_headline['all_tested_policy_extortion_cells_are_monotone_in_delay'],
            'largest_mean_delay_tax_policy': dict(matching_headline['largest_mean_delay_tax_policy']),
            'smallest_mean_delay_tax_policy': dict(matching_headline['smallest_mean_delay_tax_policy']),
            'ranked_mean_delay_tax': [dict(row) for row in ranked_mean_delay_tax],
        },
        'occupancy_accounting_summary': {
            'tested_cells': occupancy_headline['tested_cells'],
            'matched_share_monotone_nonincreasing_in_all_tested_cells': occupancy_headline['matched_share_monotone_nonincreasing_in_all_tested_cells'],
            'mean_share_component_fraction_of_delay_loss': occupancy_headline['mean_share_component_fraction_of_delay_loss'],
            'min_share_component_fraction_of_delay_loss': occupancy_headline['min_share_component_fraction_of_delay_loss'],
            'max_abs_in_match_payoff_drift_delay0_to_delay2': occupancy_headline['max_abs_in_match_payoff_drift_delay0_to_delay2'],
            'max_abs_identity_gap_across_all_delay_means': occupancy_headline['max_abs_identity_gap_across_all_delay_means'],
        },
        'matching_state_contract_guidance': {
            'matching_efficiency_interpretation_rule': 'Treat exogenous-pool rematch-delay sweeps as delay-tax diagnostics only, not as full matching-market efficiency claims.',
            'comparability_rule': 'Report time spent searching separately from payoff earned while matched so aggregate welfare changes are not mistaken for within-match quality changes.',
            'required_search_state_fields': list(SEARCH_STATE_FIELDS),
            'required_matched_state_fields': list(MATCHED_STATE_FIELDS),
        },
        'upgrade_requirement': 'Replace this copied matching-state interpretation handoff with world-native matching-state sections once endogenous rematch worlds can emit matched-vs-searching state and delay/efficiency semantics directly from real runs.',
        'size_discipline_note': 'Carry only the delay-tax headline, occupancy-loss decomposition headline, the ranked mean delay-tax order, and the minimal matching-state field guidance inside the benchmark seed; keep wider per-cell delay tables in cited reports instead of copying them forward.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact matching-state interpretation handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--matching-report', default=str(MATCHING_PATH), help='Path to the proxy matching-friction snapshot JSON.')
    parser.add_argument('--occupancy-report', default=str(OCCUPANCY_PATH), help='Path to the proxy occupancy-accounting snapshot JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        p = Path(raw)
        return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

    handoff = build_handoff(
        load_json(resolve(args.matching_report)),
        load_json(resolve(args.occupancy_report)),
    )
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'matching_friction_report_sha256': handoff['matching_friction_report_sha256'],
            'occupancy_accounting_report_sha256': handoff['occupancy_accounting_report_sha256'],
            'tested_policy_ids': handoff['tested_policy_ids'],
            'largest_mean_delay_tax_policy': handoff['delay_tax_summary']['largest_mean_delay_tax_policy'],
            'smallest_mean_delay_tax_policy': handoff['delay_tax_summary']['smallest_mean_delay_tax_policy'],
            'mean_share_component_fraction_of_delay_loss': handoff['occupancy_accounting_summary']['mean_share_component_fraction_of_delay_loss'],
            'max_abs_in_match_payoff_drift_delay0_to_delay2': handoff['occupancy_accounting_summary']['max_abs_in_match_payoff_drift_delay0_to_delay2'],
        }
        payload = json.dumps(summary, indent=2, sort_keys=True)
    else:
        payload = json.dumps(handoff, indent=2, sort_keys=True)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + '\n', encoding='utf-8')
        print(output_path.relative_to(ROOT).as_posix())
    else:
        print(payload)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
