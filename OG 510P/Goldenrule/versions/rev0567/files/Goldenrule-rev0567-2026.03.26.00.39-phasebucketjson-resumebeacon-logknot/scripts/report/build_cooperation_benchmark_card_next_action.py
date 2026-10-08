#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
CONTROL_PLANE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_control_plane.py'
WITNESS_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_next_action_witness.py'
EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_next_action.schema.json'
TITLE = '# Cooperation Benchmark Card Next Action'
SUBTITLE = (
    'Generated first-reentry surface for compact cooperation benchmark cards. '
    'This takes the fused control plane plus the arbitration witness and emits one typed next command '
    'for inheritors who need an authoritative repair-or-verify answer.'
)

control_plane_builder = load_module('cooperation_benchmark_card_control_plane_builder', CONTROL_PLANE_BUILDER)
witness_builder = load_module('cooperation_benchmark_card_next_action_witness_builder', WITNESS_BUILDER)
execution_lanes_builder = load_module('cooperation_benchmark_card_execution_lanes_builder', EXECUTION_LANES_BUILDER)

REPORTS = [
    ('artifacts/reports/cooperation_benchmark_card_control_plane.json', 'control-plane-report'),
    ('artifacts/reports/cooperation_benchmark_card_macro_review_queue.json', 'macro-review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_next_action_witness.json', 'next-action-witness-report'),
    ('artifacts/reports/cooperation_benchmark_card_execution_lanes.json', 'execution-lanes-report'),
]




LADDER_TARGET_TYPED_COUNT_FIELDS = {
    'inventory-report': {
        'target_card_count': 'card_count',
        'target_verified_delta_receipt_count': 'verified_delta_receipt_count',
        'target_latest_known_card_count': 'latest_known_card_count',
    },
    'heads-report': {
        'target_lineage_count': 'lineage_count',
        'target_unique_citation_head_count': 'unique_citation_head_count',
        'target_unique_operational_head_count': 'unique_operational_head_count',
    },
    'review-queue-report': {
        'target_total_items': 'total_items',
        'target_freeze_needed_item_count': 'freeze_needed_item_count',
        'target_topology_review_item_count': 'topology_review_item_count',
    },
    'macro-review-queue-report': {
        'target_lineage_count': 'lineage_count',
        'target_queued_lineage_count': 'queued_lineage_count',
        'target_total_item_count': 'total_item_count',
    },
    'citation-surface-report': {
        'target_citation_entry_count': 'citation_entry_count',
        'target_citation_lineage_count': 'citation_lineage_count',
        'target_unresolved_lineage_count': 'unresolved_lineage_count',
    },
    'control-plane-report': {
        'target_lineage_count': 'lineage_count',
        'target_review_item_count': 'review_item_count',
        'target_unresolved_lineage_count': 'unresolved_lineage_count',
    },
    'execution-lanes-report': {
        'target_available_lane_count': 'available_lane_count',
        'target_blocked_lane_count': 'blocked_lane_count',
    },
    'handoff-pack-report': {
        'target_pack_count': 'pack_count',
        'target_total_file_count': 'total_file_count',
        'target_unresolved_lineage_count': 'unresolved_lineage_count',
    },
}

LADDER_TARGET_COUNT_RENDER_ORDER = [
    'target_card_count',
    'target_verified_delta_receipt_count',
    'target_latest_known_card_count',
    'target_lineage_count',
    'target_unique_citation_head_count',
    'target_unique_operational_head_count',
    'target_total_items',
    'target_freeze_needed_item_count',
    'target_topology_review_item_count',
    'target_queued_lineage_count',
    'target_total_item_count',
    'target_citation_entry_count',
    'target_citation_lineage_count',
    'target_review_item_count',
    'target_unresolved_lineage_count',
    'target_available_lane_count',
    'target_blocked_lane_count',
    'target_pack_count',
    'target_total_file_count',
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_binding(path_str: str, role: str) -> dict[str, Any]:
    path = ROOT / path_str
    return {
        'path': path_str,
        'role': role,
        'sha256': sha256_file(path),
        'bytes': path.stat().st_size,
    }


def lane_row(execution_lanes: dict[str, Any], lane_id: str | None) -> dict[str, Any] | None:
    if lane_id is None:
        return None
    lane = next((row for row in execution_lanes.get('lanes', []) if row.get('lane_id') == lane_id), None)
    return lane if isinstance(lane, dict) else None


def collect() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    control_plane = control_plane_builder.collect()
    witness = witness_builder.collect()
    execution_lanes = execution_lanes_builder.collect()
    selected = next(row for row in witness['candidates'] if row['selected'])
    required_lane_id = witness['selected_command_ladder'][0]['required_lane_id'] if witness.get('selected_command_ladder') else None
    required_lane = lane_row(execution_lanes, required_lane_id)
    required_lane_available = required_lane.get('available') if required_lane is not None else None
    required_lane_summary = required_lane.get('summary') if required_lane is not None else None
    required_lane_blocking_reason_codes = required_lane.get('blocking_reason_codes') if required_lane is not None else None

    data = {
        'action_surface_kind': 'cooperation_benchmark_card_next_action',
        'control_plane_kind': control_plane['control_plane_kind'],
        'macro_review_queue_kind': control_plane['macro_review_queue_kind'],
        'witness_kind': witness['witness_kind'],
        'execution_surface_kind': execution_lanes['execution_surface_kind'],
        'status': control_plane['verdict'],
        'focus_selector_kind': witness['focus_selector_kind'],
        'focus_lineage_id': witness['focus_lineage_id'],
        'focus_summary': witness['focus_summary'],
        'focus_operational_head_card_path': witness['focus_operational_head_card_path'],
        'focus_citation_head_card_path': witness['focus_citation_head_card_path'],
        'focus_primary_open_path': witness['focus_primary_open_path'],
        'focus_primary_open_target': witness['focus_primary_open_target'],
        'focus_primary_verify_command': witness['focus_primary_verify_command'],
        'focus_primary_verify_target': witness['focus_primary_verify_target'],
        'focus_primary_verify_target_bytes': witness['focus_primary_verify_target_bytes'],
        'focus_primary_verify_target_sha256': witness['focus_primary_verify_target_sha256'],
        'focus_primary_verify_target_citation_entry_count': witness['focus_primary_verify_target_citation_entry_count'],
        'focus_primary_verify_target_citation_lineage_count': witness['focus_primary_verify_target_citation_lineage_count'],
        'focus_primary_verify_target_unresolved_lineage_count': witness['focus_primary_verify_target_unresolved_lineage_count'],
        'focus_primary_verify_target_scale_summary': witness['focus_primary_verify_target_scale_summary'],
        'focus_primary_verify_subject_role_code': witness['focus_primary_verify_subject_role_code'],
        'focus_primary_verify_intent_summary': witness['focus_primary_verify_intent_summary'],
        'focus_primary_verify_outcome_summary': witness['focus_primary_verify_outcome_summary'],
        'focus_primary_verify_effect_code': witness['focus_primary_verify_effect_code'],
        'focus_primary_refresh_command': witness['focus_primary_refresh_command'],
        'focus_primary_refresh_target': witness['focus_primary_refresh_target'],
        'focus_primary_refresh_target_bytes': witness['focus_primary_refresh_target_bytes'],
        'focus_primary_refresh_target_sha256': witness['focus_primary_refresh_target_sha256'],
        'focus_primary_refresh_target_card_count': witness['focus_primary_refresh_target_card_count'],
        'focus_primary_refresh_target_verified_delta_receipt_count': witness['focus_primary_refresh_target_verified_delta_receipt_count'],
        'focus_primary_refresh_target_latest_known_card_count': witness['focus_primary_refresh_target_latest_known_card_count'],
        'focus_primary_refresh_target_scale_summary': witness['focus_primary_refresh_target_scale_summary'],
        'focus_primary_refresh_subject_role_code': witness['focus_primary_refresh_subject_role_code'],
        'focus_primary_refresh_intent_summary': witness['focus_primary_refresh_intent_summary'],
        'focus_primary_refresh_outcome_summary': witness['focus_primary_refresh_outcome_summary'],
        'focus_primary_refresh_effect_code': witness['focus_primary_refresh_effect_code'],
        'focus_open_paths': witness['focus_open_paths'],
        'focus_open_targets': witness['focus_open_targets'],
        'report_bindings': [report_binding(path_str, role) for path_str, role in REPORTS],
        'entrypoint_commands': [
            './grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write',
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py',
        ],
        'verification_commands': [
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action_witness.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
        ],
        'primary_action': {
            'id': selected['candidate_id'],
            'action_kind': selected['action_kind'],
            'summary': selected['summary'],
            'lineage_id': selected['lineage_id'],
            'reason_codes': selected['reason_codes'],
            'next_command': selected['next_command'],
            'target': witness['selected_next_command_target'],
            'fallback_command': witness['selected_fallback_command'],
            'fallback_target': witness['selected_fallback_command_target'],
            'fallback_subject_role_code': witness['selected_fallback_command_subject_role_code'],
            'fallback_intent_summary': witness['selected_fallback_command_intent_summary'],
            'fallback_outcome_summary': witness['selected_fallback_command_outcome_summary'],
            'fallback_effect_code': witness['selected_fallback_command_effect_code'],
            'fallback_open_path': witness['selected_fallback_command_open_path'],
            'fallback_open_target': witness['selected_fallback_command_open_target'],
            'fallback_open_target_bytes': witness['selected_fallback_command_open_target_bytes'],
            'fallback_open_target_sha256': witness['selected_fallback_command_open_target_sha256'],
            'fallback_target_bytes': witness['selected_fallback_command_target_bytes'],
            'fallback_target_sha256': witness['selected_fallback_command_target_sha256'],
            'fallback_target_scale_summary': witness['selected_fallback_command_target_scale_summary'],
            'fallback_target_citation_entry_count': witness['selected_fallback_command_target_citation_entry_count'],
            'fallback_target_citation_lineage_count': witness['selected_fallback_command_target_citation_lineage_count'],
            'fallback_target_unresolved_lineage_count': witness['selected_fallback_command_target_unresolved_lineage_count'],
            'target_bytes': witness['selected_next_command_target_bytes'],
            'target_sha256': witness['selected_next_command_target_sha256'],
            'target_scale_summary': witness['selected_next_command_target_scale_summary'],
            'target_lineage_count': witness['selected_next_command_target_lineage_count'],
            'target_review_item_count': witness['selected_next_command_target_review_item_count'],
            'target_unresolved_lineage_count': witness['selected_next_command_target_unresolved_lineage_count'],
            'subject_role_code': witness['selected_next_command_subject_role_code'],
            'intent_summary': witness['selected_next_command_intent_summary'],
            'outcome_summary': witness['selected_next_command_outcome_summary'],
            'effect_code': witness['selected_next_command_effect_code'],
            'target_open_path': witness['selected_next_command_open_path'],
            'target_open_target': witness['selected_next_command_open_target'],
            'target_open_target_bytes': witness['selected_next_command_open_target_bytes'],
            'target_open_target_sha256': witness['selected_next_command_open_target_sha256'],
            'command_ladder': witness['selected_command_ladder'],
            'fallback_commands': selected['fallback_commands'],
            'selected_via_witness_candidate_id': witness['selected_candidate_id'],
            'selection_status': witness['winner_uniqueness'],
            'required_lane_id': required_lane_id,
            'required_lane_available': required_lane_available,
            'required_lane_summary': required_lane_summary,
            'required_lane_blocking_reason_codes': required_lane_blocking_reason_codes,
        },
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    primary = data['primary_action']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- status: `{data['status']}`",
        f"- primary_action.id: `{primary['id']}`",
        f"- primary_action.action_kind: `{primary['action_kind']}`",
        f"- primary_action.lineage_id: {('`' + primary['lineage_id'] + '`') if primary['lineage_id'] else 'none'}",
        f"- primary_action.selection_status: `{primary['selection_status']}`",
        f"- primary_action.required_lane_id: {( '`' + primary['required_lane_id'] + '`') if primary['required_lane_id'] else 'none'}",
        f"- primary_action.required_lane_available: {str(primary['required_lane_available']).lower() if primary['required_lane_available'] is not None else 'none'}",
        f"- primary_action.required_lane_summary: {primary['required_lane_summary'] or 'none'}",
        f"- primary_action.required_lane_blocking_reason_codes: {', '.join('`' + code + '`' for code in primary['required_lane_blocking_reason_codes']) if primary['required_lane_blocking_reason_codes'] else 'none'}",
        f"- next_command: `{primary['next_command']}`",
        f"- primary_action.target: {control_plane_builder.render_focus_open_target(primary['target'])}",
        f"- primary_action.target_open_path: {('`' + primary['target_open_path'] + '`') if primary['target_open_path'] else 'none'}",
        f"- primary_action.target_open_target: {control_plane_builder.render_focus_open_target(primary['target_open_target'])}",
        f"- primary_action.target_open_target_bytes: {primary['target_open_target_bytes'] if primary['target_open_target_bytes'] is not None else 'none'}",
        f"- primary_action.target_open_target_sha256: {('`' + primary['target_open_target_sha256'] + '`') if primary['target_open_target_sha256'] else 'none'}",
        f"- primary_action.fallback_command: {('`' + primary['fallback_command'] + '`') if primary['fallback_command'] else 'none'}",
        f"- primary_action.fallback_target: {control_plane_builder.render_focus_open_target(primary['fallback_target'])}",
        f"- primary_action.fallback_open_path: {('`' + primary['fallback_open_path'] + '`') if primary['fallback_open_path'] else 'none'}",
        f"- primary_action.fallback_open_target: {control_plane_builder.render_focus_open_target(primary['fallback_open_target'])}",
        f"- primary_action.fallback_open_target_bytes: {primary['fallback_open_target_bytes'] if primary['fallback_open_target_bytes'] is not None else 'none'}",
        f"- primary_action.fallback_open_target_sha256: {('`' + primary['fallback_open_target_sha256'] + '`') if primary['fallback_open_target_sha256'] else 'none'}",
        f"- primary_action.command_ladder_length: {len(primary['command_ladder'])}",
        f"- primary_action.fallback_subject_role_code: {('`' + primary['fallback_subject_role_code'] + '`') if primary['fallback_subject_role_code'] else 'none'}",
        f"- primary_action.fallback_intent_summary: {primary['fallback_intent_summary'] or 'none'}",
        f"- primary_action.fallback_outcome_summary: {primary['fallback_outcome_summary'] or 'none'}",
        f"- primary_action.fallback_effect_code: {('`' + primary['fallback_effect_code'] + '`') if primary['fallback_effect_code'] else 'none'}",
        f"- primary_action.fallback_target_bytes: {primary['fallback_target_bytes'] if primary['fallback_target_bytes'] is not None else 'none'}",
        f"- primary_action.fallback_target_sha256: {('`' + primary['fallback_target_sha256'] + '`') if primary['fallback_target_sha256'] else 'none'}",
        f"- primary_action.fallback_target_scale_summary: {primary['fallback_target_scale_summary'] or 'none'}",
        f"- primary_action.fallback_target_citation_entry_count: {primary['fallback_target_citation_entry_count'] if primary['fallback_target_citation_entry_count'] is not None else 'none'}",
        f"- primary_action.fallback_target_citation_lineage_count: {primary['fallback_target_citation_lineage_count'] if primary['fallback_target_citation_lineage_count'] is not None else 'none'}",
        f"- primary_action.fallback_target_unresolved_lineage_count: {primary['fallback_target_unresolved_lineage_count'] if primary['fallback_target_unresolved_lineage_count'] is not None else 'none'}",
        f"- primary_action.target_bytes: {primary['target_bytes'] if primary['target_bytes'] is not None else 'none'}",
        f"- primary_action.target_sha256: {('`' + primary['target_sha256'] + '`') if primary['target_sha256'] else 'none'}",
        f"- primary_action.target_scale_summary: {primary['target_scale_summary'] or 'none'}",
        f"- primary_action.target_lineage_count: {primary['target_lineage_count'] if primary['target_lineage_count'] is not None else 'none'}",
        f"- primary_action.target_review_item_count: {primary['target_review_item_count'] if primary['target_review_item_count'] is not None else 'none'}",
        f"- primary_action.target_unresolved_lineage_count: {primary['target_unresolved_lineage_count'] if primary['target_unresolved_lineage_count'] is not None else 'none'}",
        f"- primary_action.subject_role_code: {('`' + primary['subject_role_code'] + '`') if primary['subject_role_code'] else 'none'}",
        f"- primary_action.intent_summary: {primary['intent_summary'] or 'none'}",
        f"- primary_action.outcome_summary: {primary['outcome_summary'] or 'none'}",
        f"- primary_action.effect_code: {('`' + primary['effect_code'] + '`') if primary['effect_code'] else 'none'}",
        f"- focus_selector_kind: `{data['focus_selector_kind']}`",
        f"- focus_lineage_id: {('`' + data['focus_lineage_id'] + '`') if data['focus_lineage_id'] else 'none'}",
        f"- focus_operational_head_card_path: {('`' + data['focus_operational_head_card_path'] + '`') if data['focus_operational_head_card_path'] else 'none'}",
        f"- focus_citation_head_card_path: {('`' + data['focus_citation_head_card_path'] + '`') if data['focus_citation_head_card_path'] else 'none'}",
        f"- focus_primary_open_path: {('`' + data['focus_primary_open_path'] + '`') if data['focus_primary_open_path'] else 'none'}",
        f"- focus_primary_open_target: {control_plane_builder.render_focus_open_target(data['focus_primary_open_target'])}",
        f"- focus_primary_verify_command: {('`' + data['focus_primary_verify_command'] + '`') if data['focus_primary_verify_command'] else 'none'}",
        f"- focus_primary_verify_target: {control_plane_builder.render_focus_open_target(data['focus_primary_verify_target'])}",
        f"- focus_primary_verify_target_bytes: {data['focus_primary_verify_target_bytes'] if data['focus_primary_verify_target_bytes'] is not None else 'none'}",
        f"- focus_primary_verify_target_sha256: {('`' + data['focus_primary_verify_target_sha256'] + '`') if data['focus_primary_verify_target_sha256'] else 'none'}",
        f"- focus_primary_verify_target_citation_entry_count: {data['focus_primary_verify_target_citation_entry_count'] if data['focus_primary_verify_target_citation_entry_count'] is not None else 'none'}",
        f"- focus_primary_verify_target_citation_lineage_count: {data['focus_primary_verify_target_citation_lineage_count'] if data['focus_primary_verify_target_citation_lineage_count'] is not None else 'none'}",
        f"- focus_primary_verify_target_unresolved_lineage_count: {data['focus_primary_verify_target_unresolved_lineage_count'] if data['focus_primary_verify_target_unresolved_lineage_count'] is not None else 'none'}",
        f"- focus_primary_verify_target_scale_summary: {data['focus_primary_verify_target_scale_summary'] or 'none'}",
        f"- focus_primary_verify_subject_role_code: {('`' + data['focus_primary_verify_subject_role_code'] + '`') if data['focus_primary_verify_subject_role_code'] else 'none'}",
        f"- focus_primary_verify_intent_summary: {data['focus_primary_verify_intent_summary'] or 'none'}",
        f"- focus_primary_verify_outcome_summary: {data['focus_primary_verify_outcome_summary'] or 'none'}",
        f"- focus_primary_verify_effect_code: {('`' + data['focus_primary_verify_effect_code'] + '`') if data['focus_primary_verify_effect_code'] else 'none'}",
        f"- focus_primary_refresh_command: {('`' + data['focus_primary_refresh_command'] + '`') if data['focus_primary_refresh_command'] else 'none'}",
        f"- focus_primary_refresh_target: {control_plane_builder.render_focus_open_target(data['focus_primary_refresh_target'])}",
        f"- focus_primary_refresh_target_bytes: {data['focus_primary_refresh_target_bytes'] if data['focus_primary_refresh_target_bytes'] is not None else 'none'}",
        f"- focus_primary_refresh_target_sha256: {('`' + data['focus_primary_refresh_target_sha256'] + '`') if data['focus_primary_refresh_target_sha256'] else 'none'}",
        f"- focus_primary_refresh_target_card_count: {data['focus_primary_refresh_target_card_count'] if data['focus_primary_refresh_target_card_count'] is not None else 'none'}",
        f"- focus_primary_refresh_target_verified_delta_receipt_count: {data['focus_primary_refresh_target_verified_delta_receipt_count'] if data['focus_primary_refresh_target_verified_delta_receipt_count'] is not None else 'none'}",
        f"- focus_primary_refresh_target_latest_known_card_count: {data['focus_primary_refresh_target_latest_known_card_count'] if data['focus_primary_refresh_target_latest_known_card_count'] is not None else 'none'}",
        f"- focus_primary_refresh_target_scale_summary: {data['focus_primary_refresh_target_scale_summary'] or 'none'}",
        f"- focus_primary_refresh_subject_role_code: {('`' + data['focus_primary_refresh_subject_role_code'] + '`') if data['focus_primary_refresh_subject_role_code'] else 'none'}",
        f"- focus_primary_refresh_intent_summary: {data['focus_primary_refresh_intent_summary'] or 'none'}",
        f"- focus_primary_refresh_outcome_summary: {data['focus_primary_refresh_outcome_summary'] or 'none'}",
        f"- focus_primary_refresh_effect_code: {('`' + data['focus_primary_refresh_effect_code'] + '`') if data['focus_primary_refresh_effect_code'] else 'none'}",
        f"- focus_open_targets: {control_plane_builder.render_focus_open_targets(data['focus_open_targets'])}",
        f"- focus_summary: {data['focus_summary'] or 'none'}",
        '',
        '## Primary action',
        '',
        f"- summary: {primary['summary']}",
        f"- target: {control_plane_builder.render_focus_open_target(primary['target'])}",
        f"- target_open_path: {('`' + primary['target_open_path'] + '`') if primary['target_open_path'] else 'none'}",
        f"- target_open_target: {control_plane_builder.render_focus_open_target(primary['target_open_target'])}",
        f"- target_open_target_bytes: {primary['target_open_target_bytes'] if primary['target_open_target_bytes'] is not None else 'none'}",
        f"- target_open_target_sha256: {('`' + primary['target_open_target_sha256'] + '`') if primary['target_open_target_sha256'] else 'none'}",
        f"- target_bytes: {primary['target_bytes'] if primary['target_bytes'] is not None else 'none'}",
        f"- target_sha256: {('`' + primary['target_sha256'] + '`') if primary['target_sha256'] else 'none'}",
        f"- target_scale_summary: {primary['target_scale_summary'] or 'none'}",
        f"- target_lineage_count: {primary['target_lineage_count'] if primary['target_lineage_count'] is not None else 'none'}",
        f"- target_review_item_count: {primary['target_review_item_count'] if primary['target_review_item_count'] is not None else 'none'}",
        f"- target_unresolved_lineage_count: {primary['target_unresolved_lineage_count'] if primary['target_unresolved_lineage_count'] is not None else 'none'}",
        f"- subject_role_code: {('`' + primary['subject_role_code'] + '`') if primary['subject_role_code'] else 'none'}",
        f"- intent_summary: {primary['intent_summary'] or 'none'}",
        f"- outcome_summary: {primary['outcome_summary'] or 'none'}",
        f"- effect_code: {('`' + primary['effect_code'] + '`') if primary['effect_code'] else 'none'}",
        f"- fallback_target: {control_plane_builder.render_focus_open_target(primary['fallback_target'])}",
        f"- fallback_open_path: {('`' + primary['fallback_open_path'] + '`') if primary['fallback_open_path'] else 'none'}",
        f"- fallback_open_target: {control_plane_builder.render_focus_open_target(primary['fallback_open_target'])}",
        f"- fallback_open_target_bytes: {primary['fallback_open_target_bytes'] if primary['fallback_open_target_bytes'] is not None else 'none'}",
        f"- fallback_open_target_sha256: {('`' + primary['fallback_open_target_sha256'] + '`') if primary['fallback_open_target_sha256'] else 'none'}",
        f"- fallback_target_bytes: {primary['fallback_target_bytes'] if primary['fallback_target_bytes'] is not None else 'none'}",
        f"- fallback_target_sha256: {('`' + primary['fallback_target_sha256'] + '`') if primary['fallback_target_sha256'] else 'none'}",
        f"- fallback_target_scale_summary: {primary['fallback_target_scale_summary'] or 'none'}",
        f"- fallback_target_citation_entry_count: {primary['fallback_target_citation_entry_count'] if primary['fallback_target_citation_entry_count'] is not None else 'none'}",
        f"- fallback_target_citation_lineage_count: {primary['fallback_target_citation_lineage_count'] if primary['fallback_target_citation_lineage_count'] is not None else 'none'}",
        f"- fallback_target_unresolved_lineage_count: {primary['fallback_target_unresolved_lineage_count'] if primary['fallback_target_unresolved_lineage_count'] is not None else 'none'}",
        f"- reason_codes: {', '.join('`' + code + '`' for code in primary['reason_codes']) or 'none'}",
        f"- selected_via_witness_candidate_id: `{primary['selected_via_witness_candidate_id']}`",
        '- fallback_commands:',
    ]
    for command in primary['fallback_commands']:
        lines.append(f"  - `{command}`")
    lines.extend(['', '## Primary action command ladder', ''])
    for row in primary['command_ladder']:
        lines.extend([
            f"### Step {row['position']}",
            '',
            f"- command: `{row['command']}`",
            f"- required_lane_id: {( '`' + row['required_lane_id'] + '`') if row['required_lane_id'] else 'none'}",
            f"- required_lane_available: {str(row['required_lane_available']).lower() if row['required_lane_available'] is not None else 'none'}",
            f"- required_lane_summary: {row['required_lane_summary'] or 'none'}",
            f"- required_lane_blocking_reason_codes: {', '.join('`' + code + '`' for code in row['required_lane_blocking_reason_codes']) if row['required_lane_blocking_reason_codes'] else 'none'}",
            f"- target: {control_plane_builder.render_focus_open_target(row['target'])}",
            f"- open_path: {( '`' + row['open_path'] + '`') if row['open_path'] else 'none'}",
            f"- open_target: {control_plane_builder.render_focus_open_target(row['open_target'])}",
            f"- open_target_bytes: {row['open_target_bytes'] if row['open_target_bytes'] is not None else 'none'}",
            f"- open_target_sha256: {( '`' + row['open_target_sha256'] + '`') if row['open_target_sha256'] else 'none'}",
            f"- target_bytes: {row['target_bytes'] if row['target_bytes'] is not None else 'none'}",
            f"- target_sha256: {( '`' + row['target_sha256'] + '`') if row['target_sha256'] else 'none'}",
            f"- target_scale_summary: {row['target_scale_summary'] or 'none'}",
            *[
                f"- {field_name}: {row[field_name] if row[field_name] is not None else 'none'}"
                for field_name in LADDER_TARGET_COUNT_RENDER_ORDER
                if field_name in row
            ],
            f"- subject_role_code: {( '`' + row['subject_role_code'] + '`') if row['subject_role_code'] else 'none'}",
            f"- intent_summary: {row['intent_summary'] or 'none'}",
            f"- outcome_summary: {row['outcome_summary'] or 'none'}",
            f"- effect_code: {( '`' + row['effect_code'] + '`') if row['effect_code'] else 'none'}",
            '',
        ])
    lines.extend(['## Entrypoint commands', ''])
    for command in data['entrypoint_commands']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Verification commands', ''])
    for command in data['verification_commands']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Report bindings', '', '| role | path | bytes | sha256 |', '|---|---|---:|---|'])
    for row in data['report_bindings']:
        lines.append(f"| `{row['role']}` | `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-next-action: wrote {out_md}')
        print(f'cooperation-benchmark-card-next-action: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-next-action: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-next-action: ok ({data['primary_action']['id']})")
    print(f'cooperation-benchmark-card-next-action: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
