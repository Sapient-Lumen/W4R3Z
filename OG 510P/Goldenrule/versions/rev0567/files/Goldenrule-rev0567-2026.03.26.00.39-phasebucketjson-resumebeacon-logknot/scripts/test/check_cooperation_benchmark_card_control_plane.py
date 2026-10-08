#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_control_plane.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_control_plane.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md'
EXECUTION_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json'
SCOPE_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_scope_surface.json'
HANDOFF_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_handoff_pack.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-control-plane: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'control plane builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    if not EXECUTION_REPORT.exists():
        return fail(f'missing report {EXECUTION_REPORT.relative_to(ROOT)}')
    if not SCOPE_REPORT.exists():
        return fail(f'missing report {SCOPE_REPORT.relative_to(ROOT)}')
    if not HANDOFF_REPORT.exists():
        return fail(f'missing report {HANDOFF_REPORT.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    execution = json.loads(EXECUTION_REPORT.read_text(encoding='utf-8'))
    scope = json.loads(SCOPE_REPORT.read_text(encoding='utf-8'))
    handoff = json.loads(HANDOFF_REPORT.read_text(encoding='utf-8'))
    if data.get('control_plane_kind') != 'cooperation_benchmark_card_control_plane':
        return fail('unexpected control_plane_kind')
    if data.get('preferred_for_inheritors') is not True:
        return fail('preferred_for_inheritors should be true')
    if data.get('inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected inventory_kind')
    if data.get('heads_register_kind') != 'cooperation_benchmark_card_heads_register':
        return fail('unexpected heads_register_kind')
    if data.get('review_queue_kind') != 'cooperation_benchmark_card_review_queue':
        return fail('unexpected review_queue_kind')
    if data.get('macro_review_queue_kind') != 'cooperation_benchmark_card_macro_review_queue':
        return fail('unexpected macro_review_queue_kind')
    if data.get('citation_surface_kind') != 'cooperation_benchmark_card_citation_surface':
        return fail('unexpected citation_surface_kind')
    if data.get('handoff_pack_kind') != 'cooperation_benchmark_card_handoff_pack':
        return fail('unexpected handoff_pack_kind')
    if data.get('execution_surface_kind') != 'cooperation_benchmark_card_execution_lanes':
        return fail('unexpected execution_surface_kind')
    if data.get('scope_surface_kind') != 'cooperation_benchmark_card_scope_surface':
        return fail('unexpected scope_surface_kind')
    if data.get('scope_manifest_sha256') != scope.get('scope_manifest_sha256'):
        return fail('scope_manifest_sha256 does not match scope surface')
    if data.get('focus_selector_kind') != 'review_item_count_then_warning_reason_count_then_citation_reason_count_then_lineage_id':
        return fail('unexpected focus_selector_kind')
    counts = data.get('counts', {})
    lineages = data.get('lineages', [])
    if counts.get('lineage_count') != len(lineages):
        return fail('lineage_count does not match lineages length')
    if counts.get('citation_ready_lineage_count') != sum(1 for row in lineages if row.get('citation_ready')):
        return fail('citation_ready_lineage_count does not match lineages')
    if counts.get('handoff_ready_lineage_count') != sum(1 for row in lineages if row.get('handoff_ready')):
        return fail('handoff_ready_lineage_count does not match lineages')
    if counts.get('macro_review_lineage_count') != sum(1 for row in lineages if row.get('review_item_count')):
        return fail('macro_review_lineage_count does not match lineages')
    if counts.get('review_item_count') != sum(int(row.get('review_item_count', 0)) for row in lineages):
        return fail('review_item_count does not match lineages')
    unresolved = sum(1 for row in lineages if row.get('citation_reason_codes'))
    if counts.get('unresolved_lineage_count') != unresolved:
        return fail('unresolved_lineage_count does not match lineages')
    if data.get('verdict') == 'ready' and (counts.get('review_item_count') or counts.get('unresolved_lineage_count')):
        return fail('ready verdict should not have review items or unresolved lineages')
    if data.get('verdict') == 'needs_review' and not (counts.get('review_item_count') or counts.get('unresolved_lineage_count')):
        return fail('needs_review verdict should have review items or unresolved lineages')
    if len(data.get('report_bindings', [])) < 8:
        return fail('expected at least eight report_bindings')
    if len(data.get('recommended_entrypoints', [])) < 6:
        return fail('expected at least six recommended_entrypoints')
    if not data.get('recommended_next_command'):
        return fail('missing recommended_next_command')
    lane = next((row for row in execution['lanes'] if row['lane_id'] == data.get('recommended_next_command_lane_id')), None)
    if lane is None:
        return fail('recommended_next_command_lane_id missing from execution lanes')
    if data.get('recommended_next_command_available') != lane.get('available'):
        return fail('recommended_next_command_available does not match execution lanes')
    if counts.get('scope_path_count') != scope['counts']['path_count']:
        return fail('scope_path_count does not match scope surface')
    if counts.get('available_execution_lane_count') != execution['counts']['available_lane_count']:
        return fail('available_execution_lane_count does not match execution lanes')
    if counts.get('blocked_execution_lane_count') != execution['counts']['blocked_lane_count']:
        return fail('blocked_execution_lane_count does not match execution lanes')
    focus_lineage_id = data.get('focus_lineage_id')
    if lineages:
        lineage_ids = {row['lineage_id'] for row in lineages}
        if focus_lineage_id not in lineage_ids:
            return fail('focus_lineage_id must name a retained lineage')
        focus_row = next(row for row in lineages if row['lineage_id'] == focus_lineage_id)
        if data.get('focus_operational_head_card_id') != focus_row.get('operational_head_card_id'):
            return fail('focus_operational_head_card_id does not match focus lineage')
        focus_pack = next((row for row in handoff['packs'] if row['lineage_id'] == focus_lineage_id), None)
        if focus_pack is None:
            if data.get('focus_primary_verify_command') is not None:
                return fail('focus_primary_verify_command should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_target') is not None:
                return fail('focus_primary_verify_target should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_target_bytes') is not None:
                return fail('focus_primary_verify_target_bytes should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_target_sha256') is not None:
                return fail('focus_primary_verify_target_sha256 should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_target_citation_entry_count') is not None:
                return fail('focus_primary_verify_target_citation_entry_count should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_target_scale_summary') is not None:
                return fail('focus_primary_verify_target_scale_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_subject_role_code') is not None:
                return fail('focus_primary_verify_subject_role_code should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_intent_summary') is not None:
                return fail('focus_primary_verify_intent_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_outcome_summary') is not None:
                return fail('focus_primary_verify_outcome_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_verify_effect_code') is not None:
                return fail('focus_primary_verify_effect_code should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_command') is not None:
                return fail('focus_primary_refresh_command should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_target') is not None:
                return fail('focus_primary_refresh_target should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_target_bytes') is not None:
                return fail('focus_primary_refresh_target_bytes should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_target_sha256') is not None:
                return fail('focus_primary_refresh_target_sha256 should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_target_card_count') is not None:
                return fail('focus_primary_refresh_target_card_count should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_target_scale_summary') is not None:
                return fail('focus_primary_refresh_target_scale_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_subject_role_code') is not None:
                return fail('focus_primary_refresh_subject_role_code should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_intent_summary') is not None:
                return fail('focus_primary_refresh_intent_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_outcome_summary') is not None:
                return fail('focus_primary_refresh_outcome_summary should be null when no focus handoff pack exists')
            if data.get('focus_primary_refresh_effect_code') is not None:
                return fail('focus_primary_refresh_effect_code should be null when no focus handoff pack exists')
        else:
            if data.get('focus_primary_verify_command') != focus_pack.get('primary_verify_command'):
                return fail('focus_primary_verify_command does not match focus handoff pack')
            if data.get('focus_primary_verify_target') != focus_pack.get('primary_verify_target'):
                return fail('focus_primary_verify_target does not match focus handoff pack')
            if data.get('focus_primary_verify_target_bytes') != focus_pack.get('primary_verify_target_bytes'):
                return fail('focus_primary_verify_target_bytes does not match focus handoff pack')
            if data.get('focus_primary_verify_target_sha256') != focus_pack.get('primary_verify_target_sha256'):
                return fail('focus_primary_verify_target_sha256 does not match focus handoff pack')
            if data.get('focus_primary_verify_target_citation_entry_count') != focus_pack.get('primary_verify_target_citation_entry_count'):
                return fail('focus_primary_verify_target_citation_entry_count does not match focus handoff pack')
            if data.get('focus_primary_verify_target_citation_lineage_count') != focus_pack.get('primary_verify_target_citation_lineage_count'):
                return fail('focus_primary_verify_target_citation_lineage_count does not match focus handoff pack')
            if data.get('focus_primary_verify_target_unresolved_lineage_count') != focus_pack.get('primary_verify_target_unresolved_lineage_count'):
                return fail('focus_primary_verify_target_unresolved_lineage_count does not match focus handoff pack')
            if data.get('focus_primary_verify_target_scale_summary') != focus_pack.get('primary_verify_target_scale_summary'):
                return fail('focus_primary_verify_target_scale_summary does not match focus handoff pack')
            if data.get('focus_primary_verify_subject_role_code') != focus_pack.get('primary_verify_subject_role_code'):
                return fail('focus_primary_verify_subject_role_code does not match focus handoff pack')
            if data.get('focus_primary_verify_intent_summary') != focus_pack.get('primary_verify_intent_summary'):
                return fail('focus_primary_verify_intent_summary does not match focus handoff pack')
            if data.get('focus_primary_verify_outcome_summary') != focus_pack.get('primary_verify_outcome_summary'):
                return fail('focus_primary_verify_outcome_summary does not match focus handoff pack')
            if data.get('focus_primary_verify_effect_code') != focus_pack.get('primary_verify_effect_code'):
                return fail('focus_primary_verify_effect_code does not match focus handoff pack')
            if data.get('focus_primary_refresh_command') != focus_pack.get('primary_refresh_command'):
                return fail('focus_primary_refresh_command does not match focus handoff pack')
            if data.get('focus_primary_refresh_target') != focus_pack.get('primary_refresh_target'):
                return fail('focus_primary_refresh_target does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_bytes') != focus_pack.get('primary_refresh_target_bytes'):
                return fail('focus_primary_refresh_target_bytes does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_sha256') != focus_pack.get('primary_refresh_target_sha256'):
                return fail('focus_primary_refresh_target_sha256 does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_card_count') != focus_pack.get('primary_refresh_target_card_count'):
                return fail('focus_primary_refresh_target_card_count does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_verified_delta_receipt_count') != focus_pack.get('primary_refresh_target_verified_delta_receipt_count'):
                return fail('focus_primary_refresh_target_verified_delta_receipt_count does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_latest_known_card_count') != focus_pack.get('primary_refresh_target_latest_known_card_count'):
                return fail('focus_primary_refresh_target_latest_known_card_count does not match focus handoff pack')
            if data.get('focus_primary_refresh_target_scale_summary') != focus_pack.get('primary_refresh_target_scale_summary'):
                return fail('focus_primary_refresh_target_scale_summary does not match focus handoff pack')
            if data.get('focus_primary_refresh_subject_role_code') != focus_pack.get('primary_refresh_subject_role_code'):
                return fail('focus_primary_refresh_subject_role_code does not match focus handoff pack')
            if data.get('focus_primary_refresh_intent_summary') != focus_pack.get('primary_refresh_intent_summary'):
                return fail('focus_primary_refresh_intent_summary does not match focus handoff pack')
            if data.get('focus_primary_refresh_outcome_summary') != focus_pack.get('primary_refresh_outcome_summary'):
                return fail('focus_primary_refresh_outcome_summary does not match focus handoff pack')
            if data.get('focus_primary_refresh_effect_code') != focus_pack.get('primary_refresh_effect_code'):
                return fail('focus_primary_refresh_effect_code does not match focus handoff pack')
        if data.get('focus_citation_head_card_id') != focus_row.get('citation_head_card_id'):
            return fail('focus_citation_head_card_id does not match focus lineage')
        if data.get('focus_operational_head_card_path') is not None and not str(data['focus_operational_head_card_path']).endswith('.json'):
            return fail('focus_operational_head_card_path should name a json card path when present')
        if data.get('focus_citation_head_card_path') is not None and not str(data['focus_citation_head_card_path']).endswith('.json'):
            return fail('focus_citation_head_card_path should name a json card path when present')
        primary_open = data.get('focus_primary_open_path')
        allowed_open_paths = {value for value in [data.get('focus_citation_head_card_path'), data.get('focus_operational_head_card_path')] if value}
        citation_path = data.get('focus_citation_head_card_path')
        operational_path = data.get('focus_operational_head_card_path')
        if citation_path:
            allowed_open_paths.add(str(Path(citation_path).with_suffix('.md')))
        if operational_path:
            allowed_open_paths.add(str(Path(operational_path).with_suffix('.md')))
        if primary_open is not None and primary_open not in allowed_open_paths:
            return fail('focus_primary_open_path must be derived from focus citation/operational paths')
        if primary_open is not None and not (ROOT / primary_open).exists():
            return fail('focus_primary_open_path must exist when present')
        focus_open_paths = data.get('focus_open_paths', [])
        if primary_open is not None and (not focus_open_paths or focus_open_paths[0] != primary_open):
            return fail('focus_open_paths must start with focus_primary_open_path when present')
        if any(path_value not in allowed_open_paths for path_value in focus_open_paths):
            return fail('focus_open_paths must be derived from focus citation/operational paths')
        if len(focus_open_paths) != len(set(focus_open_paths)):
            return fail('focus_open_paths must stay unique')
        if any(not (ROOT / path_value).exists() for path_value in focus_open_paths):
            return fail('focus_open_paths must exist when present')
        focus_primary_open_target = data.get('focus_primary_open_target')
        focus_open_targets = data.get('focus_open_targets', [])
        allowed_role_codes = {
            'primary-open',
            'citation-rendered-markdown',
            'citation-card',
            'operational-rendered-markdown',
            'operational-card',
        }
        if primary_open is None and focus_primary_open_target is not None:
            return fail('focus_primary_open_target should be null when focus_primary_open_path is null')
        if primary_open is not None and focus_primary_open_target != (focus_open_targets[0] if focus_open_targets else None):
            return fail('focus_primary_open_target must equal first focus_open_targets entry when present')
        if [row.get('path') for row in focus_open_targets] != focus_open_paths:
            return fail('focus_open_targets paths must exactly match focus_open_paths in order')
        if any(not row.get('role_codes') for row in focus_open_targets):
            return fail('focus_open_targets must carry at least one role code per path')
        if any(any(code not in allowed_role_codes for code in row.get('role_codes', [])) for row in focus_open_targets):
            return fail('focus_open_targets must use known role codes')
        if primary_open is not None and (not focus_open_targets or 'primary-open' not in focus_open_targets[0].get('role_codes', [])):
            return fail('first focus_open_targets entry must carry primary-open when focus_primary_open_path is present')
        if any(len(row.get('role_codes', [])) != len(set(row.get('role_codes', []))) for row in focus_open_targets):
            return fail('focus_open_targets role_codes must stay unique per path')
        if not data.get('focus_summary'):
            return fail('focus_summary must be present when lineages exist')
    else:
        if focus_lineage_id is not None:
            return fail('focus_lineage_id should be null when no lineages exist')
        if data.get('focus_summary') is not None:
            return fail('focus_summary should be null when no lineages exist')
        if data.get('focus_operational_head_card_path') is not None:
            return fail('focus_operational_head_card_path should be null when no lineages exist')
        if data.get('focus_citation_head_card_path') is not None:
            return fail('focus_citation_head_card_path should be null when no lineages exist')
        if data.get('focus_primary_open_path') is not None:
            return fail('focus_primary_open_path should be null when no lineages exist')
        if data.get('focus_primary_open_target') is not None:
            return fail('focus_primary_open_target should be null when no lineages exist')
        if data.get('focus_primary_verify_target') is not None:
            return fail('focus_primary_verify_target should be null when no lineages exist')
        if data.get('focus_primary_verify_target_citation_entry_count') is not None:
            return fail('focus_primary_verify_target_citation_entry_count should be null when no lineages exist')
        if data.get('focus_primary_verify_target_citation_lineage_count') is not None:
            return fail('focus_primary_verify_target_citation_lineage_count should be null when no lineages exist')
        if data.get('focus_primary_verify_target_unresolved_lineage_count') is not None:
            return fail('focus_primary_verify_target_unresolved_lineage_count should be null when no lineages exist')
        if data.get('focus_primary_verify_target_scale_summary') is not None:
            return fail('focus_primary_verify_target_scale_summary should be null when no lineages exist')
        if data.get('focus_primary_verify_effect_code') is not None:
            return fail('focus_primary_verify_effect_code should be null when no lineages exist')
        if data.get('focus_primary_verify_subject_role_code') is not None:
            return fail('focus_primary_verify_subject_role_code should be null when no lineages exist')
        if data.get('focus_primary_refresh_target') is not None:
            return fail('focus_primary_refresh_target should be null when no lineages exist')
        if data.get('focus_primary_refresh_target_card_count') is not None:
            return fail('focus_primary_refresh_target_card_count should be null when no lineages exist')
        if data.get('focus_primary_refresh_target_verified_delta_receipt_count') is not None:
            return fail('focus_primary_refresh_target_verified_delta_receipt_count should be null when no lineages exist')
        if data.get('focus_primary_refresh_target_latest_known_card_count') is not None:
            return fail('focus_primary_refresh_target_latest_known_card_count should be null when no lineages exist')
        if data.get('focus_primary_refresh_target_scale_summary') is not None:
            return fail('focus_primary_refresh_target_scale_summary should be null when no lineages exist')
        if data.get('focus_primary_refresh_effect_code') is not None:
            return fail('focus_primary_refresh_effect_code should be null when no lineages exist')
        if data.get('focus_primary_refresh_subject_role_code') is not None:
            return fail('focus_primary_refresh_subject_role_code should be null when no lineages exist')
        if data.get('focus_open_paths') != []:
            return fail('focus_open_paths should be empty when no lineages exist')
        if data.get('focus_open_targets') != []:
            return fail('focus_open_targets should be empty when no lineages exist')
    for row in lineages:
        if row.get('primary_review_command') and row['primary_review_command'] not in row.get('review_commands', []):
            return fail('primary_review_command must appear in review_commands')
    print('cooperation-benchmark-card-control-plane: ok')
    print(f'cooperation-benchmark-card-control-plane: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
