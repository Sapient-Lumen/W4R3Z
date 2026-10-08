#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_taxonomy.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_taxonomy.json'


def fail(message: str) -> int:
    print(f'cooperation-benchmark-card-taxonomy-check: {message}', file=sys.stderr)
    return 1


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def extract_current_tokens() -> dict[str, set[str]]:
    inventory = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json')
    heads = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json')
    review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json')
    macro_review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_macro_review_queue.json')
    citation_surface = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json')
    control_plane = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_control_plane.json')
    next_action = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action.json')
    witness = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action_witness.json')
    execution_lanes = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json')
    handoff_pack = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_handoff_pack.json')

    out: dict[str, set[str]] = {
        'inventory_drift_reason_codes': set(),
        'head_warning_reason_codes': set(),
        'citation_reason_codes': set(),
        'review_item_kinds': set(),
        'review_reason_codes': set(),
        'next_action_kinds': set(),
        'next_action_priority_keys': set(),
        'next_action_selector_kinds': set(),
        'next_action_selection_statuses': set(),
        'next_action_winner_uniqueness': set(),
        'focus_open_target_role_codes': set(),
        'handoff_pack_entry_target_role_codes': set(),
        'focus_primary_command_target_role_codes': set(),
        'handoff_pack_primary_command_target_role_codes': set(),
        'execution_lane_ids': set(),
        'execution_blocking_reason_codes': set(),
    }
    for receipt in inventory['freeze_receipts']:
        out['inventory_drift_reason_codes'].update(receipt.get('drift_reason_codes', []))
    for receipt in inventory['delta_receipts']:
        out['inventory_drift_reason_codes'].update(receipt.get('drift_reason_codes', []))
    for row in heads['lineages']:
        out['head_warning_reason_codes'].update(row.get('warning_reason_codes', []))
    for row in citation_surface['unresolved_lineages']:
        out['citation_reason_codes'].update(row.get('reason_codes', []))
    for row in review_queue['items']:
        out['review_item_kinds'].add(row['item_kind'])
        out['review_reason_codes'].update(row.get('reason_codes', []))
    for row in macro_review_queue['groups']:
        out['review_item_kinds'].update(row.get('item_kinds', []))
        out['review_reason_codes'].update(row.get('reason_codes', []))
    out['next_action_kinds'].add(next_action['primary_action']['action_kind'])
    out['next_action_kinds'].update(row['action_kind'] for row in witness['candidates'])
    out['next_action_selector_kinds'].add(witness['selector_kind'])
    out['next_action_selection_statuses'].add(next_action['primary_action']['selection_status'])
    out['next_action_winner_uniqueness'].add(witness['winner_uniqueness'])
    priority_label_to_key = {
        'refresh-delta-basis': 'delta_drift',
        'refresh-freeze-basis': 'freeze_drift',
        'freeze-current-head': 'freeze_needed',
        'resolve-lineage-topology': 'topology_review',
        'finish-claim-readiness': 'readiness_lint',
        'inspect-unresolved-citation': 'inspect_unresolved_citation',
        'verify-ready-surface': 'verify_ready_surface',
    }
    out['next_action_priority_keys'].update(
        priority_label_to_key[row['priority_label']]
        for row in witness['candidates']
    )
    for row in control_plane.get('focus_open_targets', []):
        out['focus_open_target_role_codes'].update(row.get('role_codes', []))
    for row in witness.get('focus_open_targets', []):
        out['focus_open_target_role_codes'].update(row.get('role_codes', []))
    for row in next_action.get('focus_open_targets', []):
        out['focus_open_target_role_codes'].update(row.get('role_codes', []))
    for target_key in ['focus_primary_verify_target', 'focus_primary_refresh_target']:
        target = control_plane.get(target_key)
        if target:
            out['focus_primary_command_target_role_codes'].update(target.get('role_codes', []))
        target = witness.get(target_key)
        if target:
            out['focus_primary_command_target_role_codes'].update(target.get('role_codes', []))
        target = next_action.get(target_key)
        if target:
            out['focus_primary_command_target_role_codes'].update(target.get('role_codes', []))
    for pack in handoff_pack.get('packs', []):
        for row in pack.get('entry_targets', []):
            out['handoff_pack_entry_target_role_codes'].update(row.get('role_codes', []))
        for target_key in ['primary_verify_target', 'primary_refresh_target']:
            target = pack.get(target_key)
            if target:
                out['handoff_pack_primary_command_target_role_codes'].update(target.get('role_codes', []))
    for lane in execution_lanes['lanes']:
        out['execution_lane_ids'].add(lane['lane_id'])
        out['execution_blocking_reason_codes'].update(lane.get('blocking_reason_codes', []))
    out['execution_lane_ids'].add(next_action['primary_action']['required_lane_id'])
    for row in witness.get('selected_command_ladder', []):
        lane_id = row.get('required_lane_id')
        if lane_id:
            out['execution_lane_ids'].add(lane_id)
    for row in next_action.get('primary_action', {}).get('command_ladder', []):
        lane_id = row.get('required_lane_id')
        if lane_id:
            out['execution_lane_ids'].add(lane_id)
    return out


def main() -> int:
    if not REPORT_PATH.exists():
        return fail(f'missing taxonomy report at {REPORT_PATH.relative_to(ROOT)}')
    builder = load_module('cooperation_benchmark_card_taxonomy_builder', TAXONOMY_BUILDER)
    expected = builder.collect()
    current = load_json(REPORT_PATH)
    if current != expected:
        return fail('taxonomy report drift detected; run build_cooperation_benchmark_card_taxonomy.py --write')

    categories = current['categories']
    category_ids = [row['category_id'] for row in categories]
    if len(category_ids) != len(set(category_ids)):
        return fail('category_id values must be unique')

    registry = {row['category_id']: {item['token'] for item in row['tokens']} for row in categories}
    for row in categories:
        tokens = [item['token'] for item in row['tokens']]
        if len(tokens) != len(set(tokens)):
            return fail(f"duplicate token in category {row['category_id']}")

    required_categories = {
        'inventory_drift_reason_codes',
        'head_warning_reason_codes',
        'citation_reason_codes',
        'review_item_kinds',
        'review_reason_codes',
        'next_action_kinds',
        'next_action_priority_keys',
        'next_action_selector_kinds',
        'next_action_selection_statuses',
        'next_action_winner_uniqueness',
        'focus_open_target_role_codes',
        'handoff_pack_entry_target_role_codes',
        'focus_primary_command_target_role_codes',
        'handoff_pack_primary_command_target_role_codes',
        'execution_lane_ids',
        'execution_blocking_reason_codes',
    }
    missing_categories = sorted(required_categories - set(category_ids))
    if missing_categories:
        return fail(f'missing required taxonomy categories: {missing_categories}')

    current_tokens = extract_current_tokens()
    for category_id, tokens in current_tokens.items():
        missing = sorted(tokens - registry.get(category_id, set()))
        if missing:
            return fail(f'unregistered live tokens for {category_id}: {missing}')

    if current['counts']['category_count'] != len(categories):
        return fail('category_count does not match categories length')
    token_count = sum(len(row['tokens']) for row in categories)
    if current['counts']['token_count'] != token_count:
        return fail('token_count does not match token total')

    print(f"cooperation-benchmark-card-taxonomy-check: ok ({current['counts']['token_count']} tokens)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
