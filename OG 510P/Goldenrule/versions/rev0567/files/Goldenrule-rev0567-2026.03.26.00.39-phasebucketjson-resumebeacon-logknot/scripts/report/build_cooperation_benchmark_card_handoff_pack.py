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
INVENTORY_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_inventory.py'
HEADS_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_heads.py'
CITATION_SURFACE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_citation_surface.py'
REVIEW_QUEUE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_review_queue.py'
MACRO_REVIEW_QUEUE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_macro_review_queue.py'
EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
SCOPE_SURFACE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_scope_surface.py'
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_handoff_pack.schema.json'
DELTA_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_delta_receipt.schema.json'
FREEZE_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_freeze_receipt.schema.json'
CARD_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card.schema.json'
INVENTORY_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_inventory.schema.json'

inventory_builder = load_module('cooperation_benchmark_card_inventory_builder', INVENTORY_BUILDER)
heads_builder = load_module('cooperation_benchmark_card_heads_builder', HEADS_BUILDER)
citation_surface_builder = load_module('cooperation_benchmark_card_citation_surface_builder', CITATION_SURFACE_BUILDER)
review_queue_builder = load_module('cooperation_benchmark_card_review_queue_builder', REVIEW_QUEUE_BUILDER)
macro_review_queue_builder = load_module('cooperation_benchmark_card_macro_review_queue_builder', MACRO_REVIEW_QUEUE_BUILDER)
execution_lanes_builder = load_module('cooperation_benchmark_card_execution_lanes_builder', EXECUTION_LANES_BUILDER)
scope_surface_builder = load_module('cooperation_benchmark_card_scope_surface_builder', SCOPE_SURFACE_BUILDER)

TITLE = '# Cooperation Benchmark Card Handoff Pack'
SUBTITLE = (
    'Generated minimal citation handoff manifest for compact cooperation-card lineages. '
    'Each pack is fail-closed to one unique current citation head and carries the exact ancestry basis, '
    'file hashes, and local verification / refresh commands needed by inheritors.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def manifest_file(path_str: str, role: str) -> dict[str, Any]:
    path = ROOT / path_str
    return {
        'path': path_str,
        'role': role,
        'sha256': sha256_file(path),
        'bytes': path.stat().st_size,
    }


def entry_targets(
    primary_open_path: str,
    citation_head_card_path: str,
    operational_head_card_path: str,
    freeze_receipt_path: str,
) -> list[dict[str, Any]]:
    ordered_targets = [
        (primary_open_path, 'primary-open'),
        (primary_open_path, 'citation-rendered-markdown'),
        (primary_open_path, 'operational-rendered-markdown'),
        (citation_head_card_path, 'citation-card'),
        (operational_head_card_path, 'operational-card'),
        (freeze_receipt_path, 'citation-freeze-receipt'),
    ]
    by_path: dict[str, dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for path_value, role_code in ordered_targets:
        target = by_path.get(path_value)
        if target is None:
            target = {'path': path_value, 'role_codes': [role_code]}
            by_path[path_value] = target
            out.append(target)
            continue
        if role_code not in target['role_codes']:
            target['role_codes'].append(role_code)
    return out


def primary_entry_target(targets: list[dict[str, Any]]) -> dict[str, Any] | None:
    return targets[0] if targets else None


def command_target(path: str, primary_role: str, retained_role: str) -> dict[str, Any]:
    return {
        'path': path,
        'role_codes': [primary_role, retained_role],
    }


def file_bytes_by_path(files: list[dict[str, Any]]) -> dict[str, int]:
    return {row['path']: int(row['bytes']) for row in files}


def file_sha256_by_path(files: list[dict[str, Any]]) -> dict[str, str]:
    return {row['path']: str(row['sha256']) for row in files}


def target_subject_role_code(target: dict[str, Any] | None, primary_role: str) -> str | None:
    if target is None:
        return None
    for code in target.get('role_codes', []):
        if code != primary_role:
            return code
    return None


def command_intent_summary(command_kind: str, subject_role_code: str | None) -> str | None:
    summaries = {
        ('verify', 'citation-surface-report'): 'Verify citation surface report.',
        ('refresh', 'inventory-report'): 'Refresh inventory report.',
    }
    return summaries.get((command_kind, subject_role_code))


def command_outcome_summary(command_kind: str, subject_role_code: str | None) -> str | None:
    summaries = {
        ('verify', 'citation-surface-report'): 'Expect clean validator exit for citation surface report.',
        ('refresh', 'inventory-report'): 'Expect inventory report to be rewritten in place.',
    }
    return summaries.get((command_kind, subject_role_code))


def command_effect_code(command_kind: str, subject_role_code: str | None) -> str | None:
    codes = {
        ('verify', 'citation-surface-report'): 'read-only-check',
        ('refresh', 'inventory-report'): 'in-place-report-rewrite',
    }
    return codes.get((command_kind, subject_role_code))


def command_target_scale_summary(command_kind: str, citation_counts: dict[str, Any], inventory_counts: dict[str, Any]) -> str | None:
    if command_kind == 'verify':
        return (
            'Citation surface report with '
            f"citation_entry_count={citation_counts['citation_entry_count']}, "
            f"citation_lineage_count={citation_counts['citation_lineage_count']}, "
            f"unresolved_lineage_count={citation_counts['unresolved_lineage_count']}."
        )
    if command_kind == 'refresh':
        return (
            'Inventory report with '
            f"card_count={inventory_counts['card_count']}, "
            f"verified_delta_receipt_count={inventory_counts['verified_delta_receipt_count']}, "
            f"latest_known_card_count={inventory_counts['latest_known_card_count']}."
        )
    return None


def render_entry_target(target: dict[str, Any] | None) -> str:
    if target is None:
        return 'none'
    return '`' + target['path'] + '` (' + ', '.join('`' + code + '`' for code in target['role_codes']) + ')'


def render_entry_targets(targets: list[dict[str, Any]]) -> str:
    if not targets:
        return 'none'
    return '; '.join(render_entry_target(row) for row in targets)


def build_ordered_basis(citation_head_card_id: str, cards_by_id: dict[str, dict[str, Any]], delta_by_new_card_id: dict[str, dict[str, Any]]) -> tuple[list[str], list[str], int, int]:
    ancestry_card_ids: list[str] = []
    delta_receipt_paths: list[str] = []
    claim_surface_change_count = 0
    metadata_only_change_count = 0
    seen: set[str] = set()
    current_id = citation_head_card_id

    while True:
        if current_id in seen:
            raise RuntimeError(f'cycle detected while resolving ancestry for {citation_head_card_id}')
        seen.add(current_id)
        current = cards_by_id[current_id]
        ancestry_card_ids.append(current_id)
        predecessors = current['predecessor_card_ids']
        if not predecessors:
            break
        if len(predecessors) != 1:
            raise RuntimeError(
                f'lineage basis for {citation_head_card_id} is ambiguous; '
                f'{current_id} has {len(predecessors)} predecessors'
            )
        receipt = delta_by_new_card_id.get(current_id)
        if receipt is None:
            raise RuntimeError(f'missing verified incoming delta receipt for {current_id}')
        delta_receipt_paths.append(receipt['path'])
        if receipt['claim_surface_changed']:
            claim_surface_change_count += 1
        else:
            metadata_only_change_count += 1
        current_id = predecessors[0]

    ancestry_card_ids.reverse()
    delta_receipt_paths.reverse()
    return ancestry_card_ids, delta_receipt_paths, claim_surface_change_count, metadata_only_change_count


def collect() -> dict[str, Any]:
    inventory = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json')
    heads = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_heads.json')
    citation_surface = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_citation_surface.json')
    review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_review_queue.json')
    macro_review_queue = load_json(ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_macro_review_queue.json')
    execution_lanes = execution_lanes_builder.collect()
    scope_surface = scope_surface_builder.collect()
    handoff_schema = load_json(SCHEMA_PATH)
    for schema in [handoff_schema, load_json(INVENTORY_SCHEMA_PATH), load_json(DELTA_SCHEMA_PATH), load_json(FREEZE_SCHEMA_PATH), load_json(CARD_SCHEMA_PATH)]:
        jsonschema.Draft202012Validator.check_schema(schema)

    cards_by_id = {row['id']: row for row in inventory['cards']}
    lineages_by_id = {row['lineage_id']: row for row in heads['lineages']}
    delta_by_new_card_id: dict[str, dict[str, Any]] = {}
    for row in inventory['delta_receipts']:
        if not row.get('matches_current_surface'):
            continue
        delta_by_new_card_id[row['new_card_id']] = row
    macro_groups_by_lineage = {row['lineage_id']: row for row in macro_review_queue['groups']}

    packs: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    citation_surface_report_path = 'artifacts/reports/cooperation_benchmark_card_citation_surface.json'
    inventory_report_path = 'artifacts/reports/cooperation_benchmark_card_inventory.json'
    heads_report_path = 'artifacts/reports/cooperation_benchmark_card_heads.json'
    review_queue_report_path = 'artifacts/reports/cooperation_benchmark_card_review_queue.json'
    macro_review_queue_report_path = 'artifacts/reports/cooperation_benchmark_card_macro_review_queue.json'
    execution_lanes_report_path = 'artifacts/reports/cooperation_benchmark_card_execution_lanes.json'
    taxonomy_report_path = 'artifacts/reports/cooperation_benchmark_card_taxonomy.json'
    scope_report_path = 'artifacts/reports/cooperation_benchmark_card_scope_surface.json'

    for entry in citation_surface['entries']:
        lineage = lineages_by_id[entry['lineage_id']]
        citation_head_card_id = entry['card_id']
        operational_head_card_id = lineage['unique_operational_head_id'] or citation_head_card_id
        ancestry_card_ids, delta_receipt_paths, claim_surface_change_count, metadata_only_change_count = build_ordered_basis(
            citation_head_card_id,
            cards_by_id,
            delta_by_new_card_id,
        )

        files: list[dict[str, Any]] = []
        seen_paths: set[str] = set()

        def add_file(path_str: str, role: str) -> None:
            if path_str in seen_paths:
                return
            seen_paths.add(path_str)
            files.append(manifest_file(path_str, role))

        for idx, card_id in enumerate(ancestry_card_ids):
            add_file(cards_by_id[card_id]['path'], 'citation-card' if card_id == citation_head_card_id else 'lineage-basis-card')
            if idx < len(delta_receipt_paths):
                add_file(delta_receipt_paths[idx], 'lineage-delta-receipt')
        add_file(entry['rendered_markdown_path'], 'citation-rendered-markdown')
        add_file(entry['freeze_receipt_path'], 'citation-freeze-receipt')
        add_file(entry['card_schema_path'], 'card-schema')
        add_file('schemas/cooperation_benchmark_card_delta_receipt.schema.json', 'delta-receipt-schema')
        add_file('schemas/cooperation_benchmark_card_freeze_receipt.schema.json', 'freeze-receipt-schema')
        add_file(entry['freeze_tool_path'], 'card-tool')
        add_file(citation_surface_report_path, 'citation-surface-report')
        add_file(inventory_report_path, 'inventory-report')
        add_file(heads_report_path, 'heads-report')
        add_file(review_queue_report_path, 'review-queue-report')
        add_file(macro_review_queue_report_path, 'macro-review-queue-report')
        add_file(execution_lanes_report_path, 'execution-lanes-report')
        add_file(taxonomy_report_path, 'taxonomy-report')
        add_file(scope_report_path, 'scope-surface-report')

        files.sort(key=lambda row: (row['role'], row['path']))
        citation_head_card_path = entry['card_path']
        operational_head_card_path = cards_by_id[operational_head_card_id]['path']
        primary_open_path = entry['rendered_markdown_path'] or citation_head_card_path or operational_head_card_path
        pack_entry_targets = entry_targets(
            primary_open_path,
            citation_head_card_path,
            operational_head_card_path,
            entry['freeze_receipt_path'],
        )
        primary_open_target = primary_entry_target(pack_entry_targets)
        must_read_paths = [
            'docs/BENCHMARK_PROGRAM.md',
            primary_open_path,
            citation_head_card_path,
            entry['freeze_receipt_path'],
            'docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md',
            'docs/COOPERATION_BENCHMARK_CARD_HEADS.md',
            'docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md',
            'docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md',
            'docs/COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md',
            'docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md',
            'docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md',
            'docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md',
            'docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md',
            'docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md',
        ]
        verify_commands = [
            './grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_macro_review_queue.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action_witness.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_taxonomy.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py',
            f"./grpy ./scripts/tools/cooperation_benchmark_card.py render {entry['card_path']}",
        ]
        refresh_commands = [
            './grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_heads.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_taxonomy.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write',
        ]
        primary_verify_command = verify_commands[0]
        primary_refresh_command = refresh_commands[0]
        primary_verify_target = command_target(citation_surface_report_path, 'primary-verify-target', 'citation-surface-report')
        primary_refresh_target = command_target(inventory_report_path, 'primary-refresh-target', 'inventory-report')
        bytes_by_path = file_bytes_by_path(files)
        sha256_by_path = file_sha256_by_path(files)
        primary_verify_target_bytes = bytes_by_path.get(citation_surface_report_path)
        primary_refresh_target_bytes = bytes_by_path.get(inventory_report_path)
        primary_verify_target_sha256 = sha256_by_path.get(citation_surface_report_path)
        primary_refresh_target_sha256 = sha256_by_path.get(inventory_report_path)
        primary_verify_target_citation_entry_count = citation_surface['counts']['citation_entry_count']
        primary_verify_target_citation_lineage_count = citation_surface['counts']['citation_lineage_count']
        primary_verify_target_unresolved_lineage_count = citation_surface['counts']['unresolved_lineage_count']
        primary_refresh_target_card_count = inventory['counts']['card_count']
        primary_refresh_target_verified_delta_receipt_count = inventory['counts']['verified_delta_receipt_count']
        primary_refresh_target_latest_known_card_count = inventory['counts']['latest_known_card_count']
        primary_verify_target_scale_summary = command_target_scale_summary('verify', citation_surface['counts'], inventory['counts'])
        primary_refresh_target_scale_summary = command_target_scale_summary('refresh', citation_surface['counts'], inventory['counts'])
        primary_verify_subject_role_code = target_subject_role_code(primary_verify_target, 'primary-verify-target')
        primary_refresh_subject_role_code = target_subject_role_code(primary_refresh_target, 'primary-refresh-target')
        primary_verify_intent_summary = command_intent_summary('verify', primary_verify_subject_role_code)
        primary_verify_outcome_summary = command_outcome_summary('verify', primary_verify_subject_role_code)
        primary_verify_effect_code = command_effect_code('verify', primary_verify_subject_role_code)
        primary_refresh_intent_summary = command_intent_summary('refresh', primary_refresh_subject_role_code)
        primary_refresh_outcome_summary = command_outcome_summary('refresh', primary_refresh_subject_role_code)
        primary_refresh_effect_code = command_effect_code('refresh', primary_refresh_subject_role_code)
        pack = {
            'pack_id': f"cooperation-benchmark-card-handoff:{entry['lineage_id']}:{citation_head_card_id}",
            'lineage_id': entry['lineage_id'],
            'benchmark_name': entry['benchmark_name'],
            'citation_head_card_id': citation_head_card_id,
            'citation_head_card_path': citation_head_card_path,
            'operational_head_card_id': operational_head_card_id,
            'operational_head_card_path': operational_head_card_path,
            'primary_open_path': primary_open_path,
            'primary_open_target': primary_open_target,
            'entry_targets': pack_entry_targets,
            'ancestry_card_ids': ancestry_card_ids,
            'delta_receipt_paths': delta_receipt_paths,
            'claim_surface_change_count': claim_surface_change_count,
            'metadata_only_change_count': metadata_only_change_count,
            'must_read_paths': must_read_paths,
            'primary_verify_command': primary_verify_command,
            'primary_verify_target': primary_verify_target,
            'primary_verify_target_bytes': primary_verify_target_bytes,
            'primary_verify_target_sha256': primary_verify_target_sha256,
            'primary_verify_target_citation_entry_count': primary_verify_target_citation_entry_count,
            'primary_verify_target_citation_lineage_count': primary_verify_target_citation_lineage_count,
            'primary_verify_target_unresolved_lineage_count': primary_verify_target_unresolved_lineage_count,
            'primary_verify_target_scale_summary': primary_verify_target_scale_summary,
            'primary_verify_subject_role_code': primary_verify_subject_role_code,
            'primary_verify_intent_summary': primary_verify_intent_summary,
            'primary_verify_outcome_summary': primary_verify_outcome_summary,
            'primary_verify_effect_code': primary_verify_effect_code,
            'verify_commands': verify_commands,
            'primary_refresh_command': primary_refresh_command,
            'primary_refresh_target': primary_refresh_target,
            'primary_refresh_target_bytes': primary_refresh_target_bytes,
            'primary_refresh_target_sha256': primary_refresh_target_sha256,
            'primary_refresh_target_card_count': primary_refresh_target_card_count,
            'primary_refresh_target_verified_delta_receipt_count': primary_refresh_target_verified_delta_receipt_count,
            'primary_refresh_target_latest_known_card_count': primary_refresh_target_latest_known_card_count,
            'primary_refresh_target_scale_summary': primary_refresh_target_scale_summary,
            'primary_refresh_subject_role_code': primary_refresh_subject_role_code,
            'primary_refresh_intent_summary': primary_refresh_intent_summary,
            'primary_refresh_outcome_summary': primary_refresh_outcome_summary,
            'primary_refresh_effect_code': primary_refresh_effect_code,
            'refresh_commands': refresh_commands,
            'basis_manifest_sha256': canonical_sha256(files),
            'file_count': len(files),
            'pack_bytes': sum(row['bytes'] for row in files),
            'files': files,
        }
        packs.append(pack)

    unresolved_lineage_ids = {row['lineage_id'] for row in citation_surface['unresolved_lineages']}
    for lineage_id in sorted(unresolved_lineage_ids):
        macro_group = macro_groups_by_lineage.get(lineage_id)
        reason_codes = []
        for row in citation_surface['unresolved_lineages']:
            if row['lineage_id'] == lineage_id:
                reason_codes = row['reason_codes']
                break
        unresolved.append(
            {
                'lineage_id': lineage_id,
                'reason_codes': reason_codes,
                'primary_review_command': macro_group['primary_review_command'] if macro_group else './grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write',
                'review_commands': macro_group['review_commands'] if macro_group else ['./grpy ./scripts/report/build_cooperation_benchmark_card_macro_review_queue.py --write'],
                'apply_commands': macro_group['apply_commands'] if macro_group else [],
            }
        )

    packs.sort(key=lambda row: row['lineage_id'])
    unresolved.sort(key=lambda row: row['lineage_id'])
    data = {
        'pack_kind': 'cooperation_benchmark_card_handoff_pack',
        'citation_surface_kind': citation_surface['surface_kind'],
        'inventory_kind': inventory['card_inventory_kind'],
        'heads_register_kind': heads['register_kind'],
        'review_queue_kind': review_queue['queue_kind'],
        'macro_review_queue_kind': macro_review_queue['queue_kind'],
        'execution_surface_kind': execution_lanes['execution_surface_kind'],
        'scope_surface_kind': scope_surface['scope_surface_kind'],
        'scope_manifest_sha256': scope_surface['scope_manifest_sha256'],
        'counts': {
            'lineage_count': len(heads['lineages']),
            'pack_count': len(packs),
            'unresolved_lineage_count': len(unresolved),
            'total_file_count': sum(row['file_count'] for row in packs),
            'total_bytes': sum(row['pack_bytes'] for row in packs),
        },
        'packs': packs,
        'unresolved_lineages': unresolved,
    }
    jsonschema.validate(data, handoff_schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- lineage_count: {counts['lineage_count']}",
        f"- pack_count: {counts['pack_count']}",
        f"- unresolved_lineage_count: {counts['unresolved_lineage_count']}",
        f"- total_file_count: {counts['total_file_count']}",
        f"- total_bytes: {counts['total_bytes']}",
        f"- scope_manifest_sha256: `{data['scope_manifest_sha256']}`",
        '',
    ]
    if data['packs']:
        lines.extend([
            '## Packs',
            '',
            '| lineage_id | citation_head | ancestry_cards | delta_receipts | file_count | pack_bytes | basis_manifest_sha256 |',
            '|---|---|---:|---:|---:|---:|---|',
        ])
        for row in data['packs']:
            lines.append(
                f"| `{row['lineage_id']}` | `{row['citation_head_card_id']}` | {len(row['ancestry_card_ids'])} | {len(row['delta_receipt_paths'])} | {row['file_count']} | {row['pack_bytes']} | `{row['basis_manifest_sha256']}` |"
            )
        lines.extend(['', '## Per-pack details', ''])
        for row in data['packs']:
            lines.append(f"### `{row['lineage_id']}`")
            lines.append('')
            lines.append(f"- pack_id: `{row['pack_id']}`")
            lines.append(f"- benchmark_name: `{row['benchmark_name']}`")
            lines.append(f"- citation_head_card_id: `{row['citation_head_card_id']}`")
            lines.append(f"- citation_head_card_path: `{row['citation_head_card_path']}`")
            lines.append(f"- operational_head_card_id: `{row['operational_head_card_id']}`")
            lines.append(f"- operational_head_card_path: `{row['operational_head_card_path']}`")
            lines.append(f"- primary_open_path: `{row['primary_open_path']}`")
            lines.append(f"- primary_open_target: {render_entry_target(row['primary_open_target'])}")
            lines.append(f"- entry_targets: {render_entry_targets(row['entry_targets'])}")
            lines.append(f"- ancestry_card_ids: {', '.join('`' + value + '`' for value in row['ancestry_card_ids'])}")
            lines.append(f"- delta_receipt_paths: {', '.join('`' + value + '`' for value in row['delta_receipt_paths']) if row['delta_receipt_paths'] else 'none'}")
            lines.append(f"- claim_surface_change_count: {row['claim_surface_change_count']}")
            lines.append(f"- metadata_only_change_count: {row['metadata_only_change_count']}")
            lines.append(f"- basis_manifest_sha256: `{row['basis_manifest_sha256']}`")
            lines.append('- must_read_paths:')
            for path in row['must_read_paths']:
                lines.append(f"  - `{path}`")
            lines.append(f"- primary_verify_command: `{row['primary_verify_command']}`")
            lines.append(f"- primary_verify_target: {render_entry_target(row['primary_verify_target'])}")
            lines.append(f"- primary_verify_target_bytes: {row['primary_verify_target_bytes']}")
            lines.append(f"- primary_verify_target_sha256: `{row['primary_verify_target_sha256']}`")
            lines.append(f"- primary_verify_target_citation_entry_count: {row['primary_verify_target_citation_entry_count']}")
            lines.append(f"- primary_verify_target_citation_lineage_count: {row['primary_verify_target_citation_lineage_count']}")
            lines.append(f"- primary_verify_target_unresolved_lineage_count: {row['primary_verify_target_unresolved_lineage_count']}")
            lines.append(f"- primary_verify_target_scale_summary: {row['primary_verify_target_scale_summary']}")
            lines.append(f"- primary_verify_subject_role_code: `{row['primary_verify_subject_role_code']}`")
            lines.append(f"- primary_verify_intent_summary: {row['primary_verify_intent_summary']}")
            lines.append(f"- primary_verify_outcome_summary: {row['primary_verify_outcome_summary']}")
            lines.append('- verify_commands:')
            for command in row['verify_commands']:
                lines.append(f'  - `{command}`')
            lines.append(f"- primary_refresh_command: `{row['primary_refresh_command']}`")
            lines.append(f"- primary_refresh_target: {render_entry_target(row['primary_refresh_target'])}")
            lines.append(f"- primary_refresh_target_bytes: {row['primary_refresh_target_bytes']}")
            lines.append(f"- primary_refresh_target_sha256: `{row['primary_refresh_target_sha256']}`")
            lines.append(f"- primary_refresh_target_card_count: {row['primary_refresh_target_card_count']}")
            lines.append(f"- primary_refresh_target_verified_delta_receipt_count: {row['primary_refresh_target_verified_delta_receipt_count']}")
            lines.append(f"- primary_refresh_target_latest_known_card_count: {row['primary_refresh_target_latest_known_card_count']}")
            lines.append(f"- primary_refresh_target_scale_summary: {row['primary_refresh_target_scale_summary']}")
            lines.append(f"- primary_refresh_subject_role_code: `{row['primary_refresh_subject_role_code']}`")
            lines.append(f"- primary_refresh_intent_summary: {row['primary_refresh_intent_summary']}")
            lines.append(f"- primary_refresh_outcome_summary: {row['primary_refresh_outcome_summary']}")
            lines.append('- refresh_commands:')
            for command in row['refresh_commands']:
                lines.append(f'  - `{command}`')
            lines.append('- files:')
            for file_row in row['files']:
                lines.append(
                    f"  - `{file_row['path']}` ({file_row['role']}, {file_row['bytes']} bytes, sha256 `{file_row['sha256']}`)"
                )
            lines.append('')
    if data['unresolved_lineages']:
        lines.extend(['## Unresolved lineages', ''])
        for row in data['unresolved_lineages']:
            lines.append(f"- `{row['lineage_id']}`: {', '.join(row['reason_codes'])}; primary review `{row['primary_review_command']}`")
            lines.append(f"  - review_commands: {', '.join('`' + value + '`' for value in row['review_commands'])}")
            lines.append(f"  - apply_commands: {', '.join('`' + value + '`' for value in row['apply_commands']) if row['apply_commands'] else 'none'}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_handoff_pack.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-handoff-pack: wrote {out_md}')
        print(f'cooperation-benchmark-card-handoff-pack: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-handoff-pack: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-handoff-pack: ok ({data['counts']['pack_count']} packs)")
    print(f'cooperation-benchmark-card-handoff-pack: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
