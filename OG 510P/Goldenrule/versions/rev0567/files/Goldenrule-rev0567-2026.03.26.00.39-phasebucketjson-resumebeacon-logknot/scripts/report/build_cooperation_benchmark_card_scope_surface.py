#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_scope_surface.schema.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_scope_surface.json'
OUT_MD = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md'
TITLE = '# Cooperation Benchmark Card Scope Surface'
SUBTITLE = (
    'Generated canonical boundary manifest for the compact cooperation-benchmark-card subsystem. '
    'This surface answers which files constitute the compact-card stack, which of those files are generated, '
    'and which paths are intentionally self-elided to avoid recursive hashing.'
)

BOUNDARY_RULES = [
    {
        'rule_id': 'compact-card-boundary-is-explicit',
        'summary': 'Treat only the paths named here as the compact-card subsystem boundary; do not infer extra scope from nearby repo layout or agent prose.',
    },
    {
        'rule_id': 'generated-vs-source-stays-typed',
        'summary': 'Keep source contracts (schemas, builders, validators, doctrine, examples, tooling) distinct from generated reports/docs so inheritors know what to edit versus what to rebuild.',
    },
    {
        'rule_id': 'self-entries-are-path-only',
        'summary': 'The scope surface includes its own generated report/doc paths, but marks them self-elided so the manifest stays exact without recursive hash dependency.',
    },
]

CATEGORY_SPECS: list[dict[str, Any]] = [
    {
        'category_id': 'example-lineage-artifacts',
        'summary': 'Worked example cards, rendered markdown, and retained receipts that exercise the compact-card lineage machinery.',
        'paths': [
            ('examples/snapshots/cooperation_benchmark_card_example.json', 'example-card', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example.md', 'example-rendered-markdown', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example.freeze_receipt.json', 'example-freeze-receipt', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example.delta_receipt.json', 'example-delta-receipt', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example_v2.json', 'example-card', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example_v2.md', 'example-rendered-markdown', 'source', 'hashed'),
            ('examples/snapshots/cooperation_benchmark_card_example_v2.freeze_receipt.json', 'example-freeze-receipt', 'source', 'hashed'),
        ],
    },
    {
        'category_id': 'tooling-and-schemas',
        'summary': 'Compact-card wrapper/tool entrypoints plus the schema contracts for cards, receipts, and inheritor surfaces.',
        'paths': [
            ('grpy', 'python-wrapper', 'source', 'hashed'),
            ('scripts/tools/cooperation_benchmark_card.py', 'card-tool', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_delta_receipt.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_freeze_receipt.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_heads_register.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_review_queue.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_inventory.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_citation_surface.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_handoff_pack.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_macro_review_queue.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_control_plane.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_next_action_witness.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_next_action.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_execution_lanes.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_taxonomy.schema.json', 'schema', 'source', 'hashed'),
            ('schemas/cooperation_benchmark_card_scope_surface.schema.json', 'schema', 'source', 'hashed'),
        ],
    },
    {
        'category_id': 'report-builders',
        'summary': 'Builders that regenerate the compact-card reports and generated docs.',
        'paths': [
            ('scripts/report/build_cooperation_benchmark_card_inventory.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_heads.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_review_queue.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_citation_surface.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_handoff_pack.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_macro_review_queue.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_control_plane.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_next_action_witness.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_next_action.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_execution_lanes.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_taxonomy.py', 'report-builder', 'source', 'hashed'),
            ('scripts/report/build_cooperation_benchmark_card_scope_surface.py', 'report-builder', 'source', 'hashed'),
        ],
    },
    {
        'category_id': 'validators',
        'summary': 'Compact-card validators that keep the subsystem contracts and durable command doctrine machine-checkable.',
        'paths': [
            ('scripts/test/check_cooperation_benchmark_card_schema.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_tooling.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_readiness_lint.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_freeze_receipt.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_delta_receipt.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_inventory.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_heads.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_review_queue.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_citation_surface.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_handoff_pack.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_macro_review_queue.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_control_plane.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_next_action_witness.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_next_action.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_execution_lanes.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_taxonomy.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_program_compact_card_command_surface.py', 'validator', 'source', 'hashed'),
            ('scripts/test/check_cooperation_benchmark_card_scope_surface.py', 'validator', 'source', 'hashed'),
        ],
    },
    {
        'category_id': 'generated-docs',
        'summary': 'Generated human-readable surfaces that mirror the compact-card report layer.',
        'paths': [
            ('docs/COOPERATION_BENCHMARK_CARD_INVENTORY.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_HEADS.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_REVIEW_QUEUE.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_CITATION_SURFACE.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_HANDOFF_PACK.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_MACRO_REVIEW_QUEUE.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_TAXONOMY.md', 'generated-doc', 'generated', 'path-only'),
            ('docs/COOPERATION_BENCHMARK_CARD_SCOPE_SURFACE.md', 'generated-doc', 'generated', 'self-elided'),
        ],
    },
    {
        'category_id': 'generated-reports',
        'summary': 'Generated machine-readable surfaces that constitute the compact-card control plane.',
        'paths': [
            ('artifacts/reports/cooperation_benchmark_card_inventory.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_heads.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_review_queue.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_citation_surface.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_handoff_pack.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_macro_review_queue.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_control_plane.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_next_action_witness.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_next_action.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_execution_lanes.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_taxonomy.json', 'generated-report', 'generated', 'path-only'),
            ('artifacts/reports/cooperation_benchmark_card_scope_surface.json', 'generated-report', 'generated', 'self-elided'),
        ],
    },
    {
        'category_id': 'program-doctrine',
        'summary': 'Program doctrine and topic notes that explain why the compact-card surfaces exist and how inheritors should interpret them.',
        'paths': [
            ('docs/BENCHMARK_PROGRAM.md', 'program-doctrine', 'source', 'hashed'),
            ('docs/LIBRARY/README.md', 'library-index', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_machine_checkable_compact_card_schema_and_worked_example.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scaffold_and_canonical_renderer_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_distinguish_draft_valid_cards_from_claim_ready_cards_via_readiness_lint.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_freeze_receipt_for_claim_ready_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_canonical_delta_receipt_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_compact_inventory_and_lineage_register_for_cards_and_receipts.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_head_register_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_freezing_compact_cards_against_stale_operational_heads.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_actionable_review_queue_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fail_closed_citation_surface_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_retained_delta_receipts_no_longer_match_current_card_bytes.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fused_control_plane_surface_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_deterministic_focus_lineage_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_primary_focus_open_path_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_ordered_focus_open_paths_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_focus_open_targets_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_head_card_paths_and_a_primary_open_path_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_entry_targets_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_open_targets_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_focus_primary_verify_and_refresh_targets_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_commands_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_verify_and_refresh_targets_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_subject_role_codes_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_intent_summaries_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_outcome_summaries_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_effect_codes_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_bytes_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_sha256s_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_target_citation_entry_counts_and_primary_refresh_target_card_counts_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_primary_verify_and_refresh_target_semantic_counts_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_scale_summaries_in_handoff_packs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_commands_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_subject_role_codes_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_intent_summaries_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_outcome_summaries_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_effect_codes_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_bytes_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_sha256s_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_target_citation_entry_counts_and_focus_primary_refresh_target_card_counts_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_focus_primary_verify_and_refresh_target_semantic_counts_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_scale_summaries_for_compact_card_reentry.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_targets_and_semantics_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_audit_fields_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_semantic_counts_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_targets_and_semantics_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_audit_fields_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_semantic_counts_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_open_paths_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_selected_command_open_targets_for_compact_card_next_action_surfaces.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_wrapper_normalized_compact_card_commands_in_durable_program_docs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_preserve_interpreter_continuity_when_compact_card_validators_spawn_builders.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_grouped_macro_review_queue_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_typed_next_action_surface_for_compact_cards.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_arbitration_witness_for_compact_card_next_action_selection.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_execution_lane_surface_for_compact_card_handoffs.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_taxonomy_registry_for_compact_card_reason_codes_action_kinds_and_execution_lanes.md', 'topic-note', 'source', 'hashed'),
            ('docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scope_surface_for_compact_card_subsystem_boundaries.md', 'topic-note', 'source', 'hashed'),
        ],
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def manifest_entry(path_str: str, role: str, stage: str, integrity_mode: str) -> dict[str, Any]:
    path = ROOT / path_str
    if integrity_mode == 'self-elided':
        return {
            'path': path_str,
            'role': role,
            'stage': stage,
            'integrity_mode': integrity_mode,
            'bytes': None,
            'sha256': None,
        }
    if not path.exists():
        raise FileNotFoundError(path)
    if integrity_mode == 'path-only':
        return {
            'path': path_str,
            'role': role,
            'stage': stage,
            'integrity_mode': integrity_mode,
            'bytes': None,
            'sha256': None,
        }
    return {
        'path': path_str,
        'role': role,
        'stage': stage,
        'integrity_mode': integrity_mode,
        'bytes': path.stat().st_size,
        'sha256': sha256_file(path),
    }


def collect() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    categories: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for spec in CATEGORY_SPECS:
        rows: list[dict[str, Any]] = []
        for path_str, role, stage, integrity_mode in spec['paths']:
            if path_str in seen_paths:
                raise RuntimeError(f'duplicate scope path {path_str}')
            seen_paths.add(path_str)
            row = manifest_entry(path_str, role, stage, integrity_mode)
            rows.append(row)
            manifest_rows.append({
                'category_id': spec['category_id'],
                'path': path_str,
                'role': role,
                'stage': stage,
                'integrity_mode': integrity_mode,
            })
        categories.append({
            'category_id': spec['category_id'],
            'summary': spec['summary'],
            'path_count': len(rows),
            'paths': rows,
        })

    counts = {
        'category_count': len(categories),
        'path_count': sum(row['path_count'] for row in categories),
        'source_path_count': sum(1 for row in manifest_rows if row['stage'] == 'source'),
        'generated_path_count': sum(1 for row in manifest_rows if row['stage'] == 'generated'),
        'hashed_path_count': sum(1 for row in manifest_rows if row['integrity_mode'] == 'hashed'),
        'path_only_path_count': sum(1 for row in manifest_rows if row['integrity_mode'] == 'path-only'),
        'self_elided_path_count': sum(1 for row in manifest_rows if row['integrity_mode'] == 'self-elided'),
    }

    data = {
        'scope_surface_kind': 'cooperation_benchmark_card_scope_surface',
        'preferred_for_subsystem_boundary': True,
        'subsystem_id': 'compact-cooperation-benchmark-card-stack',
        'summary': (
            'Canonical scope manifest for the compact-card subsystem: examples, schemas, builders, validators, generated docs/reports, and governing doctrine, '
            "with path-only generated members and self-elided entries for the scope surface's own generated outputs."
        ),
        'scope_manifest_sha256': canonical_sha256(manifest_rows),
        'counts': counts,
        'boundary_rules': BOUNDARY_RULES,
        'verification_commands': [
            './grpy ./scripts/test/check_cooperation_benchmark_card_scope_surface.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py',
        ],
        'refresh_commands': [
            './grpy ./scripts/report/build_cooperation_benchmark_card_scope_surface.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write',
        ],
        'categories': categories,
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
        f"- subsystem_id: `{data['subsystem_id']}`",
        f"- scope_manifest_sha256: `{data['scope_manifest_sha256']}`",
        f"- category_count: {counts['category_count']}",
        f"- path_count: {counts['path_count']}",
        f"- source_path_count: {counts['source_path_count']}",
        f"- generated_path_count: {counts['generated_path_count']}",
        f"- hashed_path_count: {counts['hashed_path_count']}",
        f"- path_only_path_count: {counts['path_only_path_count']}",
        f"- self_elided_path_count: {counts['self_elided_path_count']}",
        '',
        '## Boundary rules',
        '',
    ]
    for row in data['boundary_rules']:
        lines.append(f"- `{row['rule_id']}` — {row['summary']}")
    lines.extend([
        '',
        '## Category summary',
        '',
        '| category_id | path_count | summary |',
        '|---|---:|---|',
    ])
    for row in data['categories']:
        lines.append(f"| `{row['category_id']}` | {row['path_count']} | {row['summary']} |")
    lines.extend(['', '## Verification commands', ''])
    for command in data['verification_commands']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Refresh commands', ''])
    for command in data['refresh_commands']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Category details', ''])
    for category in data['categories']:
        lines.append(f"### `{category['category_id']}`")
        lines.append('')
        lines.append(category['summary'])
        lines.append('')
        lines.append('| path | role | stage | integrity_mode | bytes | sha256 |')
        lines.append('|---|---|---|---|---:|---|')
        for row in category['paths']:
            lines.append(
                f"| `{row['path']}` | `{row['role']}` | `{row['stage']}` | `{row['integrity_mode']}` | "
                f"{row['bytes'] if row['bytes'] is not None else '—'} | {('`' + row['sha256'] + '`') if row['sha256'] else '—'} |"
            )
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not OUT_MD.exists():
        OUT_MD.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-scope-surface: wrote {OUT_MD}')
        print(f'cooperation-benchmark-card-scope-surface: wrote {OUT_JSON}')
        return 0
    current_md = OUT_MD.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-scope-surface: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-scope-surface: ok ({data['counts']['path_count']} paths)")
    print(f'cooperation-benchmark-card-scope-surface: wrote {OUT_JSON}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
