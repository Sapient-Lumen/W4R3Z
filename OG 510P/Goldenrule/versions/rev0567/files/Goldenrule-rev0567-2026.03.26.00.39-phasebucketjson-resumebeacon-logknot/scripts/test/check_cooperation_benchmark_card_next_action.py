#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_next_action.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md'
WITNESS_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action_witness.json'
EXECUTION_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-next-action: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'next action builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    if not WITNESS_REPORT.exists():
        return fail(f'missing report {WITNESS_REPORT.relative_to(ROOT)}')
    if not EXECUTION_REPORT.exists():
        return fail(f'missing report {EXECUTION_REPORT.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    witness = json.loads(WITNESS_REPORT.read_text(encoding='utf-8'))
    execution = json.loads(EXECUTION_REPORT.read_text(encoding='utf-8'))
    if data.get('action_surface_kind') != 'cooperation_benchmark_card_next_action':
        return fail('unexpected action_surface_kind')
    if data.get('control_plane_kind') != 'cooperation_benchmark_card_control_plane':
        return fail('unexpected control_plane_kind')
    if data.get('macro_review_queue_kind') != 'cooperation_benchmark_card_macro_review_queue':
        return fail('unexpected macro_review_queue_kind')
    if data.get('witness_kind') != 'cooperation_benchmark_card_next_action_witness':
        return fail('unexpected witness_kind')
    if data.get('execution_surface_kind') != 'cooperation_benchmark_card_execution_lanes':
        return fail('unexpected execution_surface_kind')
    if data.get('focus_selector_kind') != witness.get('focus_selector_kind'):
        return fail('focus_selector_kind does not match witness')
    if data.get('focus_lineage_id') != witness.get('focus_lineage_id'):
        return fail('focus_lineage_id does not match witness')
    if data.get('focus_summary') != witness.get('focus_summary'):
        return fail('focus_summary does not match witness')
    if data.get('focus_operational_head_card_path') != witness.get('focus_operational_head_card_path'):
        return fail('focus_operational_head_card_path does not match witness')
    if data.get('focus_citation_head_card_path') != witness.get('focus_citation_head_card_path'):
        return fail('focus_citation_head_card_path does not match witness')
    if data.get('focus_primary_open_path') != witness.get('focus_primary_open_path'):
        return fail('focus_primary_open_path does not match witness')
    if data.get('focus_primary_open_target') != witness.get('focus_primary_open_target'):
        return fail('focus_primary_open_target does not match witness')
    if data.get('focus_primary_verify_command') != witness.get('focus_primary_verify_command'):
        return fail('focus_primary_verify_command does not match witness')
    if data.get('focus_primary_verify_target_bytes') != witness.get('focus_primary_verify_target_bytes'):
        return fail('focus_primary_verify_target_bytes does not match witness')
    if data.get('focus_primary_verify_target_sha256') != witness.get('focus_primary_verify_target_sha256'):
        return fail('focus_primary_verify_target_sha256 does not match witness')
    if data.get('focus_primary_verify_target_citation_entry_count') != witness.get('focus_primary_verify_target_citation_entry_count'):
        return fail('focus_primary_verify_target_citation_entry_count does not match witness')
    if data.get('focus_primary_verify_target_citation_lineage_count') != witness.get('focus_primary_verify_target_citation_lineage_count'):
        return fail('focus_primary_verify_target_citation_lineage_count does not match witness')
    if data.get('focus_primary_verify_target_unresolved_lineage_count') != witness.get('focus_primary_verify_target_unresolved_lineage_count'):
        return fail('focus_primary_verify_target_unresolved_lineage_count does not match witness')
    if data.get('focus_primary_verify_target_scale_summary') != witness.get('focus_primary_verify_target_scale_summary'):
        return fail('focus_primary_verify_target_scale_summary does not match witness')
    if data.get('focus_primary_verify_intent_summary') != witness.get('focus_primary_verify_intent_summary'):
        return fail('focus_primary_verify_intent_summary does not match witness')
    if data.get('focus_primary_verify_outcome_summary') != witness.get('focus_primary_verify_outcome_summary'):
        return fail('focus_primary_verify_outcome_summary does not match witness')
    if data.get('focus_primary_verify_effect_code') != witness.get('focus_primary_verify_effect_code'):
        return fail('focus_primary_verify_effect_code does not match witness')
    if data.get('focus_primary_refresh_command') != witness.get('focus_primary_refresh_command'):
        return fail('focus_primary_refresh_command does not match witness')
    if data.get('focus_primary_refresh_target_bytes') != witness.get('focus_primary_refresh_target_bytes'):
        return fail('focus_primary_refresh_target_bytes does not match witness')
    if data.get('focus_primary_refresh_target_sha256') != witness.get('focus_primary_refresh_target_sha256'):
        return fail('focus_primary_refresh_target_sha256 does not match witness')
    if data.get('focus_primary_refresh_target_card_count') != witness.get('focus_primary_refresh_target_card_count'):
        return fail('focus_primary_refresh_target_card_count does not match witness')
    if data.get('focus_primary_refresh_target_verified_delta_receipt_count') != witness.get('focus_primary_refresh_target_verified_delta_receipt_count'):
        return fail('focus_primary_refresh_target_verified_delta_receipt_count does not match witness')
    if data.get('focus_primary_refresh_target_latest_known_card_count') != witness.get('focus_primary_refresh_target_latest_known_card_count'):
        return fail('focus_primary_refresh_target_latest_known_card_count does not match witness')
    if data.get('focus_primary_refresh_target_scale_summary') != witness.get('focus_primary_refresh_target_scale_summary'):
        return fail('focus_primary_refresh_target_scale_summary does not match witness')
    if data.get('focus_primary_refresh_intent_summary') != witness.get('focus_primary_refresh_intent_summary'):
        return fail('focus_primary_refresh_intent_summary does not match witness')
    if data.get('focus_primary_refresh_outcome_summary') != witness.get('focus_primary_refresh_outcome_summary'):
        return fail('focus_primary_refresh_outcome_summary does not match witness')
    if data.get('focus_primary_refresh_effect_code') != witness.get('focus_primary_refresh_effect_code'):
        return fail('focus_primary_refresh_effect_code does not match witness')
    if data.get('focus_open_paths') != witness.get('focus_open_paths'):
        return fail('focus_open_paths do not match witness')
    if data.get('focus_open_targets') != witness.get('focus_open_targets'):
        return fail('focus_open_targets do not match witness')
    if len(data.get('report_bindings', [])) < 3:
        return fail('expected at least three report_bindings')
    if len(data.get('entrypoint_commands', [])) < 5:
        return fail('expected at least five entrypoint_commands')
    if len(data.get('verification_commands', [])) < 4:
        return fail('expected at least four verification_commands')
    primary = data.get('primary_action', {})
    if primary.get('selected_via_witness_candidate_id') != witness.get('selected_candidate_id'):
        return fail('primary action does not match witness selection')
    if primary.get('id') != witness.get('selected_candidate_id'):
        return fail('primary action id should equal selected witness candidate id')
    if primary.get('next_command') != witness.get('selected_next_command'):
        return fail('primary action next_command does not match witness')
    if primary.get('target') != witness.get('selected_next_command_target'):
        return fail('primary action target does not match witness')
    if primary.get('fallback_command') != witness.get('selected_fallback_command'):
        return fail('primary action fallback_command does not match witness')
    if primary.get('fallback_target') != witness.get('selected_fallback_command_target'):
        return fail('primary action fallback_target does not match witness')
    if primary.get('fallback_subject_role_code') != witness.get('selected_fallback_command_subject_role_code'):
        return fail('primary action fallback_subject_role_code does not match witness')
    if primary.get('fallback_intent_summary') != witness.get('selected_fallback_command_intent_summary'):
        return fail('primary action fallback_intent_summary does not match witness')
    if primary.get('fallback_outcome_summary') != witness.get('selected_fallback_command_outcome_summary'):
        return fail('primary action fallback_outcome_summary does not match witness')
    if primary.get('fallback_effect_code') != witness.get('selected_fallback_command_effect_code'):
        return fail('primary action fallback_effect_code does not match witness')
    if primary.get('fallback_open_path') != witness.get('selected_fallback_command_open_path'):
        return fail('primary action fallback_open_path does not match witness')
    if primary.get('fallback_open_target') != witness.get('selected_fallback_command_open_target'):
        return fail('primary action fallback_open_target does not match witness')
    if primary.get('fallback_open_target_bytes') != witness.get('selected_fallback_command_open_target_bytes'):
        return fail('primary action fallback_open_target_bytes does not match witness')
    if primary.get('fallback_open_target_sha256') != witness.get('selected_fallback_command_open_target_sha256'):
        return fail('primary action fallback_open_target_sha256 does not match witness')
    if primary.get('fallback_target_bytes') != witness.get('selected_fallback_command_target_bytes'):
        return fail('primary action fallback_target_bytes does not match witness')
    if primary.get('fallback_target_sha256') != witness.get('selected_fallback_command_target_sha256'):
        return fail('primary action fallback_target_sha256 does not match witness')
    if primary.get('fallback_target_scale_summary') != witness.get('selected_fallback_command_target_scale_summary'):
        return fail('primary action fallback_target_scale_summary does not match witness')
    if primary.get('fallback_target_citation_entry_count') != witness.get('selected_fallback_command_target_citation_entry_count'):
        return fail('primary action fallback_target_citation_entry_count does not match witness')
    if primary.get('fallback_target_citation_lineage_count') != witness.get('selected_fallback_command_target_citation_lineage_count'):
        return fail('primary action fallback_target_citation_lineage_count does not match witness')
    if primary.get('fallback_target_unresolved_lineage_count') != witness.get('selected_fallback_command_target_unresolved_lineage_count'):
        return fail('primary action fallback_target_unresolved_lineage_count does not match witness')
    if primary.get('target_bytes') != witness.get('selected_next_command_target_bytes'):
        return fail('primary action target_bytes does not match witness')
    if primary.get('target_sha256') != witness.get('selected_next_command_target_sha256'):
        return fail('primary action target_sha256 does not match witness')
    if primary.get('target_scale_summary') != witness.get('selected_next_command_target_scale_summary'):
        return fail('primary action target_scale_summary does not match witness')
    if primary.get('target_lineage_count') != witness.get('selected_next_command_target_lineage_count'):
        return fail('primary action target_lineage_count does not match witness')
    if primary.get('target_review_item_count') != witness.get('selected_next_command_target_review_item_count'):
        return fail('primary action target_review_item_count does not match witness')
    if primary.get('target_unresolved_lineage_count') != witness.get('selected_next_command_target_unresolved_lineage_count'):
        return fail('primary action target_unresolved_lineage_count does not match witness')
    if primary.get('subject_role_code') != witness.get('selected_next_command_subject_role_code'):
        return fail('primary action subject_role_code does not match witness')
    if primary.get('intent_summary') != witness.get('selected_next_command_intent_summary'):
        return fail('primary action intent_summary does not match witness')
    if primary.get('outcome_summary') != witness.get('selected_next_command_outcome_summary'):
        return fail('primary action outcome_summary does not match witness')
    if primary.get('effect_code') != witness.get('selected_next_command_effect_code'):
        return fail('primary action effect_code does not match witness')
    if primary.get('target_open_path') != witness.get('selected_next_command_open_path'):
        return fail('primary action target_open_path does not match witness')
    if primary.get('target_open_target') != witness.get('selected_next_command_open_target'):
        return fail('primary action target_open_target does not match witness')
    if primary.get('target_open_target_bytes') != witness.get('selected_next_command_open_target_bytes'):
        return fail('primary action target_open_target_bytes does not match witness')
    if primary.get('target_open_target_sha256') != witness.get('selected_next_command_open_target_sha256'):
        return fail('primary action target_open_target_sha256 does not match witness')
    if primary.get('selection_status') != witness.get('winner_uniqueness'):
        return fail('primary action selection_status does not match witness')
    selected_witness = next(row for row in witness['candidates'] if row['selected'])
    if primary.get('action_kind') != selected_witness.get('action_kind'):
        return fail('primary action action_kind does not match witness')
    if primary.get('summary') != selected_witness.get('summary'):
        return fail('primary action summary does not match witness')
    if primary.get('lineage_id') != selected_witness.get('lineage_id'):
        return fail('primary action lineage_id does not match witness')
    if primary.get('fallback_commands') != selected_witness.get('fallback_commands'):
        return fail('primary action fallback_commands do not match witness')
    if primary.get('command_ladder') != witness.get('selected_command_ladder'):
        return fail('primary action command_ladder does not match witness')
    if not primary.get('command_ladder') or primary['command_ladder'][0].get('command') != primary.get('next_command'):
        return fail('primary action command_ladder must start with next_command')
    for row in primary.get('command_ladder', []):
        lane_id = row.get('required_lane_id')
        if lane_id is not None:
            ladder_lane = next((lane for lane in execution['lanes'] if lane['lane_id'] == lane_id), None)
            if ladder_lane is None:
                return fail('primary action command_ladder required_lane_id missing from execution lanes')
            if row.get('required_lane_available') != ladder_lane.get('available'):
                return fail('primary action command_ladder required_lane_available does not match execution lanes')
            if row.get('required_lane_summary') != ladder_lane.get('summary'):
                return fail('primary action command_ladder required_lane_summary does not match execution lanes')
            if row.get('required_lane_blocking_reason_codes') != ladder_lane.get('blocking_reason_codes'):
                return fail('primary action command_ladder required_lane_blocking_reason_codes does not match execution lanes')
        elif row.get('required_lane_available') is not None:
            return fail('primary action command_ladder required_lane_available must be null when required_lane_id is null')
        elif row.get('required_lane_summary') is not None or row.get('required_lane_blocking_reason_codes') is not None:
            return fail('primary action command_ladder required_lane_summary and required_lane_blocking_reason_codes must be null when required_lane_id is null')
    lane_id = primary.get('required_lane_id')
    if lane_id is None:
        return fail('primary action required_lane_id must be present')
    lane = next((row for row in execution['lanes'] if row['lane_id'] == lane_id), None)
    if lane is None:
        return fail('primary action required_lane_id missing from execution lanes')
    if primary.get('required_lane_available') != lane.get('available'):
        return fail('primary action required_lane_available does not match execution lanes')
    if primary.get('required_lane_summary') != lane.get('summary'):
        return fail('primary action required_lane_summary does not match execution lanes')
    if primary.get('required_lane_blocking_reason_codes') != lane.get('blocking_reason_codes'):
        return fail('primary action required_lane_blocking_reason_codes do not match execution lanes')
    print('cooperation-benchmark-card-next-action: ok')
    print(f'cooperation-benchmark-card-next-action: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
