#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_handoff_pack.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_handoff_pack.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md'
SCOPE_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_scope_surface.json'
CITATION_SURFACE_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json'
INVENTORY_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-handoff-pack: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'handoff pack builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    if not SCOPE_REPORT.exists():
        return fail(f'missing report {SCOPE_REPORT.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    scope = json.loads(SCOPE_REPORT.read_text(encoding='utf-8'))
    citation_surface = json.loads(CITATION_SURFACE_REPORT.read_text(encoding='utf-8'))
    inventory = json.loads(INVENTORY_REPORT.read_text(encoding='utf-8'))
    expected_verify_scale_summary = (
        'Citation surface report with '
        f"citation_entry_count={citation_surface['counts']['citation_entry_count']}, "
        f"citation_lineage_count={citation_surface['counts']['citation_lineage_count']}, "
        f"unresolved_lineage_count={citation_surface['counts']['unresolved_lineage_count']}."
    )
    expected_refresh_scale_summary = (
        'Inventory report with '
        f"card_count={inventory['counts']['card_count']}, "
        f"verified_delta_receipt_count={inventory['counts']['verified_delta_receipt_count']}, "
        f"latest_known_card_count={inventory['counts']['latest_known_card_count']}."
    )
    if data.get('pack_kind') != 'cooperation_benchmark_card_handoff_pack':
        return fail('unexpected pack_kind')
    if data.get('citation_surface_kind') != 'cooperation_benchmark_card_citation_surface':
        return fail('unexpected citation_surface_kind')
    if data.get('inventory_kind') != 'cooperation_benchmark_card_inventory':
        return fail('unexpected inventory_kind')
    if data.get('heads_register_kind') != 'cooperation_benchmark_card_heads_register':
        return fail('unexpected heads_register_kind')
    if data.get('review_queue_kind') != 'cooperation_benchmark_card_review_queue':
        return fail('unexpected review_queue_kind')
    if data.get('macro_review_queue_kind') != 'cooperation_benchmark_card_macro_review_queue':
        return fail('unexpected macro_review_queue_kind')
    if data.get('execution_surface_kind') != 'cooperation_benchmark_card_execution_lanes':
        return fail('unexpected execution_surface_kind')
    if data.get('scope_surface_kind') != 'cooperation_benchmark_card_scope_surface':
        return fail('unexpected scope_surface_kind')
    if data.get('scope_manifest_sha256') != scope.get('scope_manifest_sha256'):
        return fail('scope_manifest_sha256 does not match scope surface')
    packs = data.get('packs', [])
    counts = data.get('counts', {})
    if counts.get('pack_count') != len(packs):
        return fail('pack_count does not match packs length')
    if counts.get('unresolved_lineage_count') != len(data.get('unresolved_lineages', [])):
        return fail('unresolved_lineage_count does not match unresolved_lineages length')
    if counts.get('total_file_count') != sum(row.get('file_count', 0) for row in packs):
        return fail('total_file_count does not match pack file counts')
    if counts.get('total_bytes') != sum(row.get('pack_bytes', 0) for row in packs):
        return fail('total_bytes does not match pack bytes')
    for row in packs:
        if row['citation_head_card_id'] != row['operational_head_card_id']:
            return fail('pack emitted for citation head that is not the operational head')
        if not row['must_read_paths']:
            return fail('pack missing must_read_paths')
        if row['must_read_paths'][0] != 'docs/BENCHMARK_PROGRAM.md':
            return fail('pack must_read_paths should start with docs/BENCHMARK_PROGRAM.md')
        if row['must_read_paths'][1] != row['primary_open_path']:
            return fail('pack must_read_paths should place primary_open_path second')
        if row['citation_head_card_path'] != row['operational_head_card_path']:
            return fail('pack emitted for citation head path that is not the operational head path')
        if row['citation_head_card_path'] not in row['must_read_paths']:
            return fail('pack missing citation_head_card_path in must_read_paths')
        if row['primary_open_path'] not in row['must_read_paths']:
            return fail('pack missing primary_open_path in must_read_paths')
        primary_open_target = row.get('primary_open_target')
        entry_targets = row.get('entry_targets', [])
        allowed_role_codes = {
            'primary-open',
            'citation-rendered-markdown',
            'operational-rendered-markdown',
            'citation-card',
            'operational-card',
            'citation-freeze-receipt',
        }
        if not entry_targets:
            return fail('pack missing entry_targets')
        if primary_open_target != entry_targets[0]:
            return fail('pack primary_open_target must equal first entry_targets entry')
        if entry_targets[0].get('path') != row['primary_open_path']:
            return fail('pack entry_targets should start with primary_open_path')
        if 'primary-open' not in entry_targets[0].get('role_codes', []):
            return fail('first entry_target must carry primary-open')
        entry_paths = [target.get('path') for target in entry_targets]
        if len(entry_paths) != len(set(entry_paths)):
            return fail('pack entry_targets paths should stay unique')
        if any(path not in row['must_read_paths'] for path in entry_paths):
            return fail('pack entry_targets must be present in must_read_paths')
        if any(any(code not in allowed_role_codes for code in target.get('role_codes', [])) for target in entry_targets):
            return fail('pack entry_targets must use known role codes')
        if any(len(target.get('role_codes', [])) != len(set(target.get('role_codes', []))) for target in entry_targets):
            return fail('pack entry_targets role_codes must stay unique per path')
        if 'docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md' not in row['must_read_paths']:
            return fail('pack missing scope surface doc in must_read_paths')
        if not row['verify_commands'] or not row['refresh_commands']:
            return fail('pack missing verify or refresh commands')
        if row.get('primary_verify_command') != row['verify_commands'][0]:
            return fail('pack primary_verify_command must equal first verify_commands entry')
        if row.get('primary_verify_target') != {'path': 'artifacts/reports/cooperation_benchmark_card_citation_surface.json', 'role_codes': ['primary-verify-target', 'citation-surface-report']}:
            return fail('pack primary_verify_target must point at the citation-surface report')
        verify_file = next((file_row for file_row in row['files'] if file_row['path'] == 'artifacts/reports/cooperation_benchmark_card_citation_surface.json'), None)
        if verify_file is None:
            return fail('pack files missing citation-surface report for primary_verify_target_bytes')
        if row.get('primary_verify_target_bytes') != verify_file.get('bytes'):
            return fail('pack primary_verify_target_bytes must match the retained citation-surface report bytes')
        if row.get('primary_verify_target_sha256') != verify_file.get('sha256'):
            return fail('pack primary_verify_target_sha256 must match the retained citation-surface report sha256')
        if row.get('primary_verify_target_citation_entry_count') != citation_surface['counts']['citation_entry_count']:
            return fail('pack primary_verify_target_citation_entry_count must match citation surface citation_entry_count')
        if row.get('primary_verify_target_citation_lineage_count') != citation_surface['counts']['citation_lineage_count']:
            return fail('pack primary_verify_target_citation_lineage_count must match citation surface citation_lineage_count')
        if row.get('primary_verify_target_unresolved_lineage_count') != citation_surface['counts']['unresolved_lineage_count']:
            return fail('pack primary_verify_target_unresolved_lineage_count must match citation surface unresolved_lineage_count')
        if row.get('primary_verify_target_scale_summary') != expected_verify_scale_summary:
            return fail('pack primary_verify_target_scale_summary must summarize citation surface scale')
        if row.get('primary_verify_subject_role_code') != 'citation-surface-report':
            return fail('pack primary_verify_subject_role_code must name the citation-surface report role')
        if row.get('primary_verify_intent_summary') != 'Verify citation surface report.':
            return fail('pack primary_verify_intent_summary must summarize the citation-surface verify step')
        if row.get('primary_verify_outcome_summary') != 'Expect clean validator exit for citation surface report.':
            return fail('pack primary_verify_outcome_summary must summarize the citation-surface verify outcome')
        if row.get('primary_verify_effect_code') != 'read-only-check':
            return fail('pack primary_verify_effect_code must classify the citation-surface verify step as read-only')
        if row.get('primary_refresh_command') != row['refresh_commands'][0]:
            return fail('pack primary_refresh_command must equal first refresh_commands entry')
        if row.get('primary_refresh_target') != {'path': 'artifacts/reports/cooperation_benchmark_card_inventory.json', 'role_codes': ['primary-refresh-target', 'inventory-report']}:
            return fail('pack primary_refresh_target must point at the inventory report')
        refresh_file = next((file_row for file_row in row['files'] if file_row['path'] == 'artifacts/reports/cooperation_benchmark_card_inventory.json'), None)
        if refresh_file is None:
            return fail('pack files missing inventory report for primary_refresh_target_bytes')
        if row.get('primary_refresh_target_bytes') != refresh_file.get('bytes'):
            return fail('pack primary_refresh_target_bytes must match the retained inventory report bytes')
        if row.get('primary_refresh_target_sha256') != refresh_file.get('sha256'):
            return fail('pack primary_refresh_target_sha256 must match the retained inventory report sha256')
        if row.get('primary_refresh_target_card_count') != inventory['counts']['card_count']:
            return fail('pack primary_refresh_target_card_count must match inventory card_count')
        if row.get('primary_refresh_target_verified_delta_receipt_count') != inventory['counts']['verified_delta_receipt_count']:
            return fail('pack primary_refresh_target_verified_delta_receipt_count must match inventory verified_delta_receipt_count')
        if row.get('primary_refresh_target_latest_known_card_count') != inventory['counts']['latest_known_card_count']:
            return fail('pack primary_refresh_target_latest_known_card_count must match inventory latest_known_card_count')
        if row.get('primary_refresh_target_scale_summary') != expected_refresh_scale_summary:
            return fail('pack primary_refresh_target_scale_summary must summarize inventory scale')
        if row.get('primary_refresh_subject_role_code') != 'inventory-report':
            return fail('pack primary_refresh_subject_role_code must name the inventory-report role')
        if row.get('primary_refresh_intent_summary') != 'Refresh inventory report.':
            return fail('pack primary_refresh_intent_summary must summarize the inventory refresh step')
        if row.get('primary_refresh_outcome_summary') != 'Expect inventory report to be rewritten in place.':
            return fail('pack primary_refresh_outcome_summary must summarize the inventory refresh outcome')
        if row.get('primary_refresh_effect_code') != 'in-place-report-rewrite':
            return fail('pack primary_refresh_effect_code must classify the inventory refresh step as a retained-report rewrite')
        if row['file_count'] != len(row['files']):
            return fail('file_count does not match files length')
        if len(row['ancestry_card_ids']) != len(set(row['ancestry_card_ids'])):
            return fail('ancestry_card_ids should be unique')
        if row['delta_receipt_paths'] and len(row['ancestry_card_ids']) != len(row['delta_receipt_paths']) + 1:
            return fail('ancestry_card_ids should be one longer than delta_receipt_paths')
        if row['claim_surface_change_count'] + row['metadata_only_change_count'] != len(row['delta_receipt_paths']):
            return fail('delta change counts do not match delta receipt paths length')
        paths = [file_row['path'] for file_row in row['files']]
        if len(paths) != len(set(paths)):
            return fail('pack files should not repeat paths')
        if row['citation_head_card_path'] not in paths:
            return fail('pack files missing citation_head_card_path')
        if row['operational_head_card_path'] not in paths:
            return fail('pack files missing operational_head_card_path')
        if row['primary_open_path'] not in paths:
            return fail('pack files missing primary_open_path')
    for row in data.get('unresolved_lineages', []):
        if row['primary_review_command'] not in row['review_commands']:
            return fail('unresolved lineage primary_review_command must appear in review_commands')
    print('cooperation-benchmark-card-handoff-pack: ok')
    print(f'cooperation-benchmark-card-handoff-pack: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
