#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_control_plane.schema.json'
TITLE = '# Cooperation Benchmark Card Control Plane'
SUBTITLE = (
    'Generated fused status surface for compact cooperation benchmark cards. '
    'This is the one-shot inheritor reentry surface over the inventory, heads, review queue, citation surface, and handoff pack.'
)

EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
FOCUS_SELECTOR_KIND = 'review_item_count_then_warning_reason_count_then_citation_reason_count_then_lineage_id'

REPORTS = [
    ('artifacts/reports/cooperation_benchmark_card_inventory.json', 'inventory-report'),
    ('artifacts/reports/cooperation_benchmark_card_heads.json', 'heads-report'),
    ('artifacts/reports/cooperation_benchmark_card_review_queue.json', 'review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_macro_review_queue.json', 'macro-review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_citation_surface.json', 'citation-surface-report'),
    ('artifacts/reports/cooperation_benchmark_card_handoff_pack.json', 'handoff-pack-report'),
    ('artifacts/reports/cooperation_benchmark_card_execution_lanes.json', 'execution-lanes-report'),
    ('artifacts/reports/cooperation_benchmark_card_taxonomy.json', 'taxonomy-report'),
    ('artifacts/reports/cooperation_benchmark_card_scope_surface.json', 'scope-surface-report'),
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


control_plane_execution_builder = load_module('cooperation_benchmark_card_execution_lanes_builder', EXECUTION_LANES_BUILDER)


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


def focus_sort_key(lineage: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        -int(lineage['review_item_count']),
        -len(lineage['warning_reason_codes']),
        -len(lineage['citation_reason_codes']),
        lineage['lineage_id'],
    )


def focus_summary(lineages: list[dict[str, Any]], row: dict[str, Any]) -> str:
    if row['review_item_count']:
        return 'Inspect this lineage first because it currently carries the highest grouped review pressure.'
    if row['warning_reason_codes'] or row['citation_reason_codes']:
        return 'Inspect this lineage first because it carries the strongest unresolved warning/citation pressure under the stable focus selector.'
    if len(lineages) == 1:
        return 'Only retained lineage present; this is the first inspection target once the ready surface is verified.'
    return 'No live review pressure remains; this lineage is the deterministic first inspection target under the stable focus selector.'


def card_path_lookup(cards: list[dict[str, Any]]) -> dict[str, str]:
    return {card['id']: card['path'] for card in cards}


def rendered_markdown_path(card_path: str | None) -> str | None:
    if not card_path:
        return None
    path = ROOT / card_path
    candidate = path.with_suffix('.md')
    if candidate.exists():
        return candidate.relative_to(ROOT).as_posix()
    return None


def preferred_focus_open_path(
    citation_markdown_path: str | None,
    citation_card_path: str | None,
    operational_card_path: str | None,
) -> str | None:
    for candidate in (citation_markdown_path, citation_card_path, operational_card_path):
        if candidate:
            return candidate
    return None


def ordered_unique_paths(*values: str | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def focus_open_paths(
    primary_open_path: str | None,
    citation_card_path: str | None,
    operational_card_path: str | None,
) -> list[str]:
    citation_markdown_path = rendered_markdown_path(citation_card_path)
    operational_markdown_path = rendered_markdown_path(operational_card_path)
    return ordered_unique_paths(
        primary_open_path,
        citation_markdown_path,
        citation_card_path,
        operational_markdown_path,
        operational_card_path,
    )


def focus_open_targets(
    primary_open_path: str | None,
    citation_card_path: str | None,
    operational_card_path: str | None,
) -> list[dict[str, Any]]:
    citation_markdown_path = rendered_markdown_path(citation_card_path)
    operational_markdown_path = rendered_markdown_path(operational_card_path)
    ordered_candidates = [
        (primary_open_path, 'primary-open'),
        (citation_markdown_path, 'citation-rendered-markdown'),
        (citation_card_path, 'citation-card'),
        (operational_markdown_path, 'operational-rendered-markdown'),
        (operational_card_path, 'operational-card'),
    ]
    targets_by_path: dict[str, dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for path_value, role_code in ordered_candidates:
        if not path_value:
            continue
        target = targets_by_path.get(path_value)
        if target is None:
            target = {'path': path_value, 'role_codes': [role_code]}
            targets_by_path[path_value] = target
            out.append(target)
            continue
        if role_code not in target['role_codes']:
            target['role_codes'].append(role_code)
    return out


def primary_open_target(targets: list[dict[str, Any]]) -> dict[str, Any] | None:
    return targets[0] if targets else None


def render_focus_open_target(target: dict[str, Any] | None) -> str:
    if target is None:
        return 'none'
    return '`' + target['path'] + '` (' + ', '.join('`' + code + '`' for code in target['role_codes']) + ')'


def render_focus_open_targets(targets: list[dict[str, Any]]) -> str:
    if not targets:
        return 'none'
    rendered: list[str] = []
    for row in targets:
        rendered.append(render_focus_open_target(row))
    return '; '.join(rendered)


def collect() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    inventory = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json')
    heads = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json')
    review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json')
    macro_review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_macro_review_queue.json')
    citation_surface = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json')
    handoff_pack = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_handoff_pack.json')
    execution_surface = control_plane_execution_builder.collect()
    scope_surface = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_scope_surface.json')

    citation_entries = {row['lineage_id']: row for row in citation_surface['entries']}
    unresolved_entries = {row['lineage_id']: row for row in citation_surface['unresolved_lineages']}
    macro_groups_by_lineage = {row['lineage_id']: row for row in macro_review_queue['groups']}
    packs_by_lineage = {row['lineage_id']: row for row in handoff_pack['packs']}
    card_paths_by_id = card_path_lookup(inventory['cards'])

    lineages: list[dict[str, Any]] = []
    for lineage in heads['lineages']:
        lineage_id = lineage['lineage_id']
        citation_entry = citation_entries.get(lineage_id)
        unresolved = unresolved_entries.get(lineage_id)
        pack = packs_by_lineage.get(lineage_id)
        review_group = macro_groups_by_lineage.get(lineage_id)
        lineages.append(
            {
                'lineage_id': lineage_id,
                'benchmark_names': lineage['benchmark_names'],
                'operational_head_card_id': lineage['unique_operational_head_id'],
                'citation_head_card_id': lineage['unique_citation_head_id'],
                'warning_reason_codes': lineage['warning_reason_codes'],
                'citation_reason_codes': unresolved['reason_codes'] if unresolved else [],
                'review_item_count': review_group['item_count'] if review_group else 0,
                'review_item_kinds': review_group['item_kinds'] if review_group else [],
                'review_reason_codes': review_group['reason_codes'] if review_group else [],
                'primary_review_command': review_group['primary_review_command'] if review_group else None,
                'review_commands': review_group['review_commands'] if review_group else [],
                'apply_commands': review_group['apply_commands'] if review_group else [],
                'citation_ready': citation_entry is not None,
                'handoff_ready': pack is not None,
                'citation_card_path': citation_entry['card_path'] if citation_entry else None,
                'handoff_pack_id': pack['pack_id'] if pack else None,
            }
        )
    lineages.sort(key=lambda row: row['lineage_id'])

    if lineages:
        focus_row = min(lineages, key=focus_sort_key)
        focus_lineage_id = focus_row['lineage_id']
        focus_summary_text = focus_summary(lineages, focus_row)
        focus_operational_head_card_id = focus_row['operational_head_card_id']
        focus_citation_head_card_id = focus_row['citation_head_card_id']
        focus_operational_head_card_path = card_paths_by_id.get(focus_operational_head_card_id)
        focus_citation_head_card_path = card_paths_by_id.get(focus_citation_head_card_id)
        focus_primary_open_path = preferred_focus_open_path(
            rendered_markdown_path(focus_citation_head_card_path),
            focus_citation_head_card_path,
            focus_operational_head_card_path,
        )
        focus_open_path_family = focus_open_paths(
            focus_primary_open_path,
            focus_citation_head_card_path,
            focus_operational_head_card_path,
        )
        focus_open_target_family = focus_open_targets(
            focus_primary_open_path,
            focus_citation_head_card_path,
            focus_operational_head_card_path,
        )
        focus_primary_open_target = primary_open_target(focus_open_target_family)
        focus_pack = packs_by_lineage.get(focus_lineage_id)
        focus_primary_verify_command = focus_pack['primary_verify_command'] if focus_pack else None
        focus_primary_verify_target = focus_pack['primary_verify_target'] if focus_pack else None
        focus_primary_verify_target_bytes = focus_pack['primary_verify_target_bytes'] if focus_pack else None
        focus_primary_verify_target_sha256 = focus_pack['primary_verify_target_sha256'] if focus_pack else None
        focus_primary_verify_target_citation_entry_count = focus_pack['primary_verify_target_citation_entry_count'] if focus_pack else None
        focus_primary_verify_target_citation_lineage_count = focus_pack['primary_verify_target_citation_lineage_count'] if focus_pack else None
        focus_primary_verify_target_unresolved_lineage_count = focus_pack['primary_verify_target_unresolved_lineage_count'] if focus_pack else None
        focus_primary_verify_target_scale_summary = focus_pack['primary_verify_target_scale_summary'] if focus_pack else None
        focus_primary_verify_subject_role_code = focus_pack['primary_verify_subject_role_code'] if focus_pack else None
        focus_primary_verify_intent_summary = focus_pack['primary_verify_intent_summary'] if focus_pack else None
        focus_primary_verify_outcome_summary = focus_pack['primary_verify_outcome_summary'] if focus_pack else None
        focus_primary_verify_effect_code = focus_pack['primary_verify_effect_code'] if focus_pack else None
        focus_primary_refresh_command = focus_pack['primary_refresh_command'] if focus_pack else None
        focus_primary_refresh_target = focus_pack['primary_refresh_target'] if focus_pack else None
        focus_primary_refresh_target_bytes = focus_pack['primary_refresh_target_bytes'] if focus_pack else None
        focus_primary_refresh_target_sha256 = focus_pack['primary_refresh_target_sha256'] if focus_pack else None
        focus_primary_refresh_target_card_count = focus_pack['primary_refresh_target_card_count'] if focus_pack else None
        focus_primary_refresh_target_verified_delta_receipt_count = focus_pack['primary_refresh_target_verified_delta_receipt_count'] if focus_pack else None
        focus_primary_refresh_target_latest_known_card_count = focus_pack['primary_refresh_target_latest_known_card_count'] if focus_pack else None
        focus_primary_refresh_target_scale_summary = focus_pack['primary_refresh_target_scale_summary'] if focus_pack else None
        focus_primary_refresh_subject_role_code = focus_pack['primary_refresh_subject_role_code'] if focus_pack else None
        focus_primary_refresh_intent_summary = focus_pack['primary_refresh_intent_summary'] if focus_pack else None
        focus_primary_refresh_outcome_summary = focus_pack['primary_refresh_outcome_summary'] if focus_pack else None
        focus_primary_refresh_effect_code = focus_pack['primary_refresh_effect_code'] if focus_pack else None
    else:
        focus_row = None
        focus_lineage_id = None
        focus_summary_text = None
        focus_operational_head_card_id = None
        focus_citation_head_card_id = None
        focus_operational_head_card_path = None
        focus_citation_head_card_path = None
        focus_primary_open_path = None
        focus_open_path_family = []
        focus_open_target_family = []
        focus_primary_open_target = None
        focus_primary_verify_command = None
        focus_primary_verify_target = None
        focus_primary_verify_target_bytes = None
        focus_primary_verify_target_sha256 = None
        focus_primary_verify_target_citation_entry_count = None
        focus_primary_verify_target_citation_lineage_count = None
        focus_primary_verify_target_unresolved_lineage_count = None
        focus_primary_verify_target_scale_summary = None
        focus_primary_verify_subject_role_code = None
        focus_primary_verify_intent_summary = None
        focus_primary_verify_outcome_summary = None
        focus_primary_verify_effect_code = None
        focus_primary_refresh_command = None
        focus_primary_refresh_target = None
        focus_primary_refresh_target_bytes = None
        focus_primary_refresh_target_sha256 = None
        focus_primary_refresh_target_card_count = None
        focus_primary_refresh_target_verified_delta_receipt_count = None
        focus_primary_refresh_target_latest_known_card_count = None
        focus_primary_refresh_target_scale_summary = None
        focus_primary_refresh_subject_role_code = None
        focus_primary_refresh_intent_summary = None
        focus_primary_refresh_outcome_summary = None
        focus_primary_refresh_effect_code = None

    report_bindings = [report_binding(path_str, role) for path_str, role in REPORTS]
    recommended_entrypoints = [
        './grpy ./scripts/report/build_cooperation_benchmark_card_taxonomy.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write',
        './grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write',
        './grpy ./scripts/test/check_cooperation_benchmark_card_taxonomy.py',
        './grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py',
        './grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py',
        './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
    ]
    if macro_review_queue['groups']:
        recommended_next_command = macro_review_queue['groups'][0]['primary_review_command']
    else:
        recommended_next_command = './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py'
    recommended_next_command_lane_id = 'python-integrity'
    for lane in execution_surface['lanes']:
        if lane['lane_id'] == recommended_next_command_lane_id:
            recommended_next_command_available = lane['available']
            break
    else:
        recommended_next_command_available = False

    data = {
        'control_plane_kind': 'cooperation_benchmark_card_control_plane',
        'preferred_for_inheritors': True,
        'inventory_kind': inventory['card_inventory_kind'],
        'heads_register_kind': heads['register_kind'],
        'review_queue_kind': review_queue['queue_kind'],
        'macro_review_queue_kind': macro_review_queue['queue_kind'],
        'execution_surface_kind': execution_surface['execution_surface_kind'],
        'scope_surface_kind': scope_surface['scope_surface_kind'],
        'citation_surface_kind': citation_surface['surface_kind'],
        'handoff_pack_kind': handoff_pack['pack_kind'],
        'verdict': 'needs_review' if review_queue['counts']['total_items'] or citation_surface['counts']['unresolved_lineage_count'] else 'ready',
        'scope_manifest_sha256': scope_surface['scope_manifest_sha256'],
        'focus_selector_kind': FOCUS_SELECTOR_KIND,
        'focus_lineage_id': focus_lineage_id,
        'focus_summary': focus_summary_text,
        'focus_operational_head_card_id': focus_operational_head_card_id,
        'focus_citation_head_card_path': focus_citation_head_card_path,
        'focus_operational_head_card_path': focus_operational_head_card_path,
        'focus_primary_open_path': focus_primary_open_path,
        'focus_primary_open_target': focus_primary_open_target,
        'focus_primary_verify_command': focus_primary_verify_command,
        'focus_primary_verify_target': focus_primary_verify_target,
        'focus_primary_verify_target_bytes': focus_primary_verify_target_bytes,
        'focus_primary_verify_target_sha256': focus_primary_verify_target_sha256,
        'focus_primary_verify_target_citation_entry_count': focus_primary_verify_target_citation_entry_count,
        'focus_primary_verify_target_citation_lineage_count': focus_primary_verify_target_citation_lineage_count,
        'focus_primary_verify_target_unresolved_lineage_count': focus_primary_verify_target_unresolved_lineage_count,
        'focus_primary_verify_target_scale_summary': focus_primary_verify_target_scale_summary,
        'focus_primary_verify_subject_role_code': focus_primary_verify_subject_role_code,
        'focus_primary_verify_intent_summary': focus_primary_verify_intent_summary,
        'focus_primary_verify_outcome_summary': focus_primary_verify_outcome_summary,
        'focus_primary_verify_effect_code': focus_primary_verify_effect_code,
        'focus_primary_refresh_command': focus_primary_refresh_command,
        'focus_primary_refresh_target': focus_primary_refresh_target,
        'focus_primary_refresh_target_bytes': focus_primary_refresh_target_bytes,
        'focus_primary_refresh_target_sha256': focus_primary_refresh_target_sha256,
        'focus_primary_refresh_target_card_count': focus_primary_refresh_target_card_count,
        'focus_primary_refresh_target_verified_delta_receipt_count': focus_primary_refresh_target_verified_delta_receipt_count,
        'focus_primary_refresh_target_latest_known_card_count': focus_primary_refresh_target_latest_known_card_count,
        'focus_primary_refresh_target_scale_summary': focus_primary_refresh_target_scale_summary,
        'focus_primary_refresh_subject_role_code': focus_primary_refresh_subject_role_code,
        'focus_primary_refresh_intent_summary': focus_primary_refresh_intent_summary,
        'focus_primary_refresh_outcome_summary': focus_primary_refresh_outcome_summary,
        'focus_primary_refresh_effect_code': focus_primary_refresh_effect_code,
        'focus_open_paths': focus_open_path_family,
        'focus_open_targets': focus_open_target_family,
        'focus_citation_head_card_id': focus_citation_head_card_id,
        'counts': {
            'lineage_count': len(heads['lineages']),
            'citation_ready_lineage_count': citation_surface['counts']['citation_lineage_count'],
            'unresolved_lineage_count': citation_surface['counts']['unresolved_lineage_count'],
            'review_item_count': review_queue['counts']['total_items'],
            'macro_review_lineage_count': macro_review_queue['counts']['queued_lineage_count'],
            'handoff_ready_lineage_count': handoff_pack['counts']['pack_count'],
            'verified_freeze_receipt_count': inventory['counts']['verified_freeze_receipt_count'],
            'verified_delta_receipt_count': inventory['counts']['verified_delta_receipt_count'],
            'scope_path_count': scope_surface['counts']['path_count'],
            'available_execution_lane_count': execution_surface['counts']['available_lane_count'],
            'blocked_execution_lane_count': execution_surface['counts']['blocked_lane_count'],
        },
        'report_bindings': report_bindings,
        'recommended_entrypoints': recommended_entrypoints,
        'recommended_next_command': recommended_next_command,
        'recommended_next_command_lane_id': recommended_next_command_lane_id,
        'recommended_next_command_available': recommended_next_command_available,
        'lineages': lineages,
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- verdict: `{data['verdict']}`",
        f"- lineage_count: {counts['lineage_count']}",
        f"- citation_ready_lineage_count: {counts['citation_ready_lineage_count']}",
        f"- unresolved_lineage_count: {counts['unresolved_lineage_count']}",
        f"- review_item_count: {counts['review_item_count']}",
        f"- macro_review_lineage_count: {counts['macro_review_lineage_count']}",
        f"- handoff_ready_lineage_count: {counts['handoff_ready_lineage_count']}",
        f"- verified_freeze_receipt_count: {counts['verified_freeze_receipt_count']}",
        f"- verified_delta_receipt_count: {counts['verified_delta_receipt_count']}",
        f"- scope_manifest_sha256: `{data['scope_manifest_sha256']}`",
        f"- scope_path_count: {counts['scope_path_count']}",
        f"- available_execution_lane_count: {counts['available_execution_lane_count']}",
        f"- blocked_execution_lane_count: {counts['blocked_execution_lane_count']}",
        f"- recommended_next_command: `{data['recommended_next_command']}`",
        f"- recommended_next_command_lane_id: `{data['recommended_next_command_lane_id']}`",
        f"- recommended_next_command_available: {str(data['recommended_next_command_available']).lower()}",
        f"- focus_selector_kind: `{data['focus_selector_kind']}`",
        f"- focus_lineage_id: {('`' + data['focus_lineage_id'] + '`') if data['focus_lineage_id'] else 'none'}",
        f"- focus_operational_head_card_id: {('`' + data['focus_operational_head_card_id'] + '`') if data['focus_operational_head_card_id'] else 'none'}",
        f"- focus_operational_head_card_path: {('`' + data['focus_operational_head_card_path'] + '`') if data['focus_operational_head_card_path'] else 'none'}",
        f"- focus_citation_head_card_id: {('`' + data['focus_citation_head_card_id'] + '`') if data['focus_citation_head_card_id'] else 'none'}",
        f"- focus_citation_head_card_path: {('`' + data['focus_citation_head_card_path'] + '`') if data['focus_citation_head_card_path'] else 'none'}",
        f"- focus_primary_open_path: {('`' + data['focus_primary_open_path'] + '`') if data['focus_primary_open_path'] else 'none'}",
        f"- focus_primary_open_target: {render_focus_open_target(data['focus_primary_open_target'])}",
        f"- focus_primary_verify_command: {('`' + data['focus_primary_verify_command'] + '`') if data['focus_primary_verify_command'] else 'none'}",
        f"- focus_primary_verify_target: {render_focus_open_target(data['focus_primary_verify_target'])}",
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
        f"- focus_primary_refresh_target: {render_focus_open_target(data['focus_primary_refresh_target'])}",
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
        f"- focus_open_targets: {render_focus_open_targets(data['focus_open_targets'])}",
        f"- focus_summary: {data['focus_summary'] or 'none'}",
        '',
        '## Lineage summary',
        '',
        '| lineage_id | operational_head | citation_head | citation_ready | handoff_ready | review_items | review_reason_codes | warning_reason_codes | citation_reason_codes |',
        '|---|---|---|---:|---:|---:|---|---|---|',
    ]
    for row in data['lineages']:
        warnings = ', '.join('`' + code + '`' for code in row['warning_reason_codes']) or '—'
        review_codes = ', '.join('`' + code + '`' for code in row['review_reason_codes']) or '—'
        citation_codes = ', '.join('`' + code + '`' for code in row['citation_reason_codes']) or '—'
        lines.append(
            f"| `{row['lineage_id']}` | {('`' + row['operational_head_card_id'] + '`') if row['operational_head_card_id'] else '—'} | "
            f"{('`' + row['citation_head_card_id'] + '`') if row['citation_head_card_id'] else '—'} | "
            f"{str(row['citation_ready']).lower()} | {str(row['handoff_ready']).lower()} | {row['review_item_count']} | {review_codes} | {warnings} | {citation_codes} |"
        )
    lines.extend([
        '',
        '## Report bindings',
        '',
        '| role | path | bytes | sha256 |',
        '|---|---|---:|---|',
    ])
    for row in data['report_bindings']:
        lines.append(f"| `{row['role']}` | `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    lines.extend([
        '',
        '## Recommended entrypoints',
        '',
    ])
    for command in data['recommended_entrypoints']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Per-lineage details', ''])
    for row in data['lineages']:
        lines.append(f"### `{row['lineage_id']}`")
        lines.append('')
        lines.append(f"- benchmark_names: {', '.join('`' + value + '`' for value in row['benchmark_names'])}")
        lines.append(f"- operational_head_card_id: {('`' + row['operational_head_card_id'] + '`') if row['operational_head_card_id'] else 'none'}")
        lines.append(f"- citation_head_card_id: {('`' + row['citation_head_card_id'] + '`') if row['citation_head_card_id'] else 'none'}")
        lines.append(f"- citation_ready: {str(row['citation_ready']).lower()}")
        lines.append(f"- handoff_ready: {str(row['handoff_ready']).lower()}")
        lines.append(f"- review_item_count: {row['review_item_count']}")
        lines.append(f"- review_item_kinds: {', '.join('`' + value + '`' for value in row['review_item_kinds']) if row['review_item_kinds'] else 'none'}")
        lines.append(f"- review_reason_codes: {', '.join('`' + value + '`' for value in row['review_reason_codes']) if row['review_reason_codes'] else 'none'}")
        lines.append(f"- primary_review_command: {('`' + row['primary_review_command'] + '`') if row['primary_review_command'] else 'none'}")
        lines.append(f"- review_commands: {', '.join('`' + value + '`' for value in row['review_commands']) if row['review_commands'] else 'none'}")
        lines.append(f"- apply_commands: {', '.join('`' + value + '`' for value in row['apply_commands']) if row['apply_commands'] else 'none'}")
        lines.append(f"- warning_reason_codes: {', '.join('`' + value + '`' for value in row['warning_reason_codes']) if row['warning_reason_codes'] else 'none'}")
        lines.append(f"- citation_reason_codes: {', '.join('`' + value + '`' for value in row['citation_reason_codes']) if row['citation_reason_codes'] else 'none'}")
        lines.append(f"- citation_card_path: {('`' + row['citation_card_path'] + '`') if row['citation_card_path'] else 'none'}")
        lines.append(f"- handoff_pack_id: {('`' + row['handoff_pack_id'] + '`') if row['handoff_pack_id'] else 'none'}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_control_plane.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-control-plane: wrote {out_md}')
        print(f'cooperation-benchmark-card-control-plane: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-control-plane: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-control-plane: ok ({data['counts']['lineage_count']} lineages)")
    print(f'cooperation-benchmark-card-control-plane: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
