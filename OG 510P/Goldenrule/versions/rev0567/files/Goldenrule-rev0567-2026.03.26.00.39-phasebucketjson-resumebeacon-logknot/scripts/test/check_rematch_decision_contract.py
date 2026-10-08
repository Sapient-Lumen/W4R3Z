#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_decision_contract.schema.json'
SOURCE_PATHS = [
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_live_contenders_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_materiality_gate_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_anchor_contract_snapshot_20260306.json',
    ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json',
]
EXPECTED_QUESTIONS = [f'SQ-0{i}' for i in range(17, 27)]


def fail(msg: str) -> int:
    print(f'rematch-decision-contract: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    if not REPORT_PATH.exists():
        return fail(f'missing {REPORT_PATH.relative_to(ROOT)}')
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')

    report = load_json(REPORT_PATH)
    schema = load_json(SCHEMA_PATH)
    if not isinstance(report, dict):
        return fail('report root must be object')
    if not isinstance(schema, dict):
        return fail('schema root must be object')

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if report.get('world', {}).get('kind') != 'rematch_proxy_compact_decision_contract':
        return fail('unexpected world.kind')

    question_ids = [row['question_id'] for row in report['question_coverage']]
    if question_ids != EXPECTED_QUESTIONS:
        return fail('question coverage must list SQ-017 through SQ-026 in order')

    if len(report['delay_contract']['extortion_rows']) != 3:
        return fail('expected 3 extortion rows')
    if len(report['winner_contract']['panel_rows']) != 9:
        return fail('expected 9 winner panel rows')
    if len(report['delta_contract']['band_rows']) != 20:
        return fail('expected 20 delta bands')

    component_total = sum(path.stat().st_size for path in SOURCE_PATHS)
    if report['component_report_total_bytes'] != component_total:
        return fail('component_report_total_bytes mismatch')
    if set(report['component_report_bytes']) != {path.relative_to(ROOT).as_posix() for path in SOURCE_PATHS}:
        return fail('component report byte map mismatch')
    if not (0 < report['bundle_vs_components_raw_byte_ratio'] < 1):
        return fail('bundle ratio must be between 0 and 1')

    triage_statuses = {row['triage_status'] for row in report['winner_contract']['panel_rows']}
    if 'certified_practical_tie' not in triage_statuses or 'certified_material_leader' not in triage_statuses:
        return fail('winner contract must expose both practical ties and material leaders')

    improved_buffers = [
        row for row in report['delta_contract']['band_rows']
        if row['topology_preserving_anchor_buffer_to_nearest_topology_boundary'] > row['parent_anchor_buffer_to_nearest_topology_boundary']
    ]
    if not improved_buffers:
        return fail('delta contract should include at least one buffer-improving topology anchor')

    print(
        f"rematch-decision-contract: ok ({len(question_ids)} questions, {report['bundle_json_bytes']} bundle bytes, {component_total} component bytes)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
