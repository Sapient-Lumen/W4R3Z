#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
TURNOVER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.schema.json'
LINKED_QUESTION_IDS = ['SQ-015']
REQUIRED_POLICY_ROW_FIELDS = ['avg_match_length', 'delay_or_search_dead_time', 'turnover_metric_label']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _tested_policy_ids(turnover_report: dict[str, Any]) -> list[str]:
    return sorted({str(row['policy']) for row in turnover_report['scenario_rows']})


def _tested_extortion_values(turnover_report: dict[str, Any]) -> list[int]:
    return sorted({int(row['extortion']) for row in turnover_report['scenario_rows']})


def _tested_delay_values(turnover_report: dict[str, Any]) -> list[int]:
    return sorted({int(row['delay']) for row in turnover_report['scenario_rows']})


def build_handoff(turnover_report: dict[str, Any]) -> dict[str, Any]:
    headline = turnover_report['headline_findings']
    return {
        'contract_kind': 'rematch_world_benchmark_turnover_tempo_interpretation_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_turnover_tempo_interpretation_handoff.v1',
        'planner_origin': 'copy the current proxy-era turnover-tempo interpretation into the benchmark seed until native rematch worlds can emit world-owned persistence and delay-normalization sections directly',
        'turnover_tempo_report_path': 'artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.json',
        'turnover_tempo_report_sha256': sha256_json(turnover_report),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'tested_policy_ids': _tested_policy_ids(turnover_report),
        'tested_extortion_values': _tested_extortion_values(turnover_report),
        'tested_delay_values': _tested_delay_values(turnover_report),
        'tempo_scaling_summary': {
            'scenario_means_checked': headline['scenario_means_checked'],
            'mean_abs_prediction_error': headline['mean_abs_prediction_error'],
            'max_abs_prediction_error': headline['max_abs_prediction_error'],
            'rms_prediction_error': headline['rms_prediction_error'],
            'highest_churn_delay2_cell': dict(headline['highest_churn_delay2_cell']),
            'lowest_churn_delay2_cell': dict(headline['lowest_churn_delay2_cell']),
            'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': headline['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
            'interpretation': headline['interpretation'],
        },
        'turnover_tempo_contract_guidance': {
            'comparability_rule': 'Do not compare fixed-delay rematch worlds or policies without also reporting a persistence or turnover metric, because the same nominal delay taxes short-lived matches more often than long-lived ones.',
            'turnover_metric_requirement_rule': 'Every benchmark policy row should pair the delay or search-dead-time field with avg_match_length or an equivalent turnover-rate metric so delay penalties can be normalized across worlds.',
            'persistence_boundary_rule': 'Keep persistence and search dead-time as separate first-class fields; a fixed delay knob is not a complete description of rematch friction when partnership tempo differs.',
            'required_policy_row_fields': list(REQUIRED_POLICY_ROW_FIELDS),
        },
        'upgrade_requirement': 'Replace this copied turnover-tempo interpretation handoff with world-native persistence and delay-normalization sections once endogenous rematch benchmarks can emit tempo-aware turnover metrics directly from real runs.',
        'size_discipline_note': 'Carry only the tempo-scaling headline, the two anchor cells, and the minimal turnover-field guidance inside the benchmark seed; keep wider per-scenario tempo rows in the cited proxy report instead of copying them forward.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact turnover-tempo interpretation handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--turnover-report', default=str(TURNOVER_PATH), help='Path to the proxy turnover-tempo snapshot JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        p = Path(raw)
        return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

    handoff = build_handoff(load_json(resolve(args.turnover_report)))
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'turnover_tempo_report_sha256': handoff['turnover_tempo_report_sha256'],
            'tested_policy_ids': handoff['tested_policy_ids'],
            'tested_extortion_values': handoff['tested_extortion_values'],
            'tested_delay_values': handoff['tested_delay_values'],
            'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
            'mean_abs_prediction_error': handoff['tempo_scaling_summary']['mean_abs_prediction_error'],
            'max_abs_prediction_error': handoff['tempo_scaling_summary']['max_abs_prediction_error'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = resolve(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-turnover-tempo-interpretation-handoff: wrote {out.relative_to(ROOT).as_posix()}')
        return 0
    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
