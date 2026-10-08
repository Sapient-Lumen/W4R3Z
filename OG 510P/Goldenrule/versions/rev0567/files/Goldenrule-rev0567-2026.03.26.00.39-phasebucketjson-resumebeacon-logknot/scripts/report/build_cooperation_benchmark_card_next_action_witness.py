#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import shlex
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
MACRO_REVIEW_QUEUE_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_macro_review_queue.py'
EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_next_action_witness.schema.json'
TITLE = '# Cooperation Benchmark Card Next Action Witness'
SUBTITLE = (
    'Generated arbitration witness for compact-card first reentry. '
    'This preserves the live candidate family, winning priority bucket, tie set, stable selector, '
    'and current focus lineage so the recommended next command does not silently become more authoritative than its evidence.'
)

control_plane_builder = load_module('cooperation_benchmark_card_control_plane_builder', CONTROL_PLANE_BUILDER)
macro_review_queue_builder = load_module('cooperation_benchmark_card_macro_review_queue_builder', MACRO_REVIEW_QUEUE_BUILDER)
execution_lanes_builder = load_module('cooperation_benchmark_card_execution_lanes_builder', EXECUTION_LANES_BUILDER)

REPORTS = [
    ('artifacts/reports/cooperation_benchmark_card_control_plane.json', 'control-plane-report'),
    ('artifacts/reports/cooperation_benchmark_card_macro_review_queue.json', 'macro-review-queue-report'),
    ('artifacts/reports/cooperation_benchmark_card_execution_lanes.json', 'execution-lanes-report'),
]


REPORT_STEM_TO_ROLE = {
    'inventory': 'inventory-report',
    'heads': 'heads-report',
    'review_queue': 'review-queue-report',
    'macro_review_queue': 'macro-review-queue-report',
    'citation_surface': 'citation-surface-report',
    'control_plane': 'control-plane-report',
    'execution_lanes': 'execution-lanes-report',
    'handoff_pack': 'handoff-pack-report',
}

REPORT_ROLE_TO_LABEL = {
    'inventory-report': 'inventory report',
    'heads-report': 'heads report',
    'review-queue-report': 'review queue report',
    'macro-review-queue-report': 'macro review queue report',
    'citation-surface-report': 'citation surface report',
    'control-plane-report': 'control plane report',
    'execution-lanes-report': 'execution lanes report',
    'handoff-pack-report': 'handoff pack report',
}


REPORT_ROLE_TO_SCALE_SUMMARY = {
    'inventory-report': lambda counts: (
        f"Inventory report with card_count={counts['card_count']}, "
        f"verified_delta_receipt_count={counts['verified_delta_receipt_count']}, "
        f"latest_known_card_count={counts['latest_known_card_count']}."
    ),
    'heads-report': lambda counts: (
        f"Heads report with lineage_count={counts['lineage_count']}, "
        f"unique_citation_head_count={counts['unique_citation_head_count']}, "
        f"unique_operational_head_count={counts['unique_operational_head_count']}."
    ),
    'review-queue-report': lambda counts: (
        f"Review queue report with total_items={counts['total_items']}, "
        f"freeze_needed_item_count={counts['freeze_needed_item_count']}, "
        f"topology_review_item_count={counts['topology_review_item_count']}."
    ),
    'macro-review-queue-report': lambda counts: (
        f"Macro review queue report with lineage_count={counts['lineage_count']}, "
        f"queued_lineage_count={counts['queued_lineage_count']}, "
        f"total_item_count={counts['total_item_count']}."
    ),
    'citation-surface-report': lambda counts: (
        f"Citation surface report with citation_entry_count={counts['citation_entry_count']}, "
        f"citation_lineage_count={counts['citation_lineage_count']}, "
        f"unresolved_lineage_count={counts['unresolved_lineage_count']}."
    ),
    'control-plane-report': lambda counts: (
        f"Control plane report with lineage_count={counts['lineage_count']}, "
        f"review_item_count={counts['review_item_count']}, "
        f"unresolved_lineage_count={counts['unresolved_lineage_count']}."
    ),
    'execution-lanes-report': lambda counts: (
        f"Execution lanes report with available_lane_count={counts['available_lane_count']}, "
        f"blocked_lane_count={counts['blocked_lane_count']}."
    ),
    'handoff-pack-report': lambda counts: (
        f"Handoff pack report with pack_count={counts['pack_count']}, "
        f"total_file_count={counts['total_file_count']}, "
        f"unresolved_lineage_count={counts['unresolved_lineage_count']}."
    ),
}

TARGET_TYPED_COUNT_FIELDS = {
    'selected_next_command_target': {
        'control-plane-report': {
            'selected_next_command_target_lineage_count': 'lineage_count',
            'selected_next_command_target_review_item_count': 'review_item_count',
            'selected_next_command_target_unresolved_lineage_count': 'unresolved_lineage_count',
        },
    },
    'selected_fallback_command_target': {
        'citation-surface-report': {
            'selected_fallback_command_target_citation_entry_count': 'citation_entry_count',
            'selected_fallback_command_target_citation_lineage_count': 'citation_lineage_count',
            'selected_fallback_command_target_unresolved_lineage_count': 'unresolved_lineage_count',
        },
    },
}

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


PRIORITY_BUCKETS = {
    'delta_drift': (0, 'refresh-delta-basis'),
    'freeze_drift': (1, 'refresh-freeze-basis'),
    'freeze_needed': (2, 'freeze-current-head'),
    'topology_review': (3, 'resolve-lineage-topology'),
    'readiness_lint': (4, 'finish-claim-readiness'),
    'inspect_unresolved_citation': (5, 'inspect-unresolved-citation'),
    'verify_ready_surface': (90, 'verify-ready-surface'),
}


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


def ordered_unique(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def first_distinct_fallback_command(commands: list[str], selected_command: str) -> str | None:
    for command in commands:
        if command != selected_command:
            return command
    return None


def fallback_command() -> str:
    return './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write'


def report_open_path(target: dict[str, Any] | None) -> str | None:
    if target is None:
        return None
    path_value = target.get('path')
    if not path_value:
        return None
    path = Path(path_value)
    if path.parts[:2] != ('artifacts', 'reports') or path.suffix != '.json':
        return None
    candidate = ROOT / 'docs' / f'{path.stem.upper()}.md'
    if candidate.exists():
        return candidate.relative_to(ROOT).as_posix()
    return None


def report_open_target(target: dict[str, Any] | None, *, role_code: str) -> dict[str, Any] | None:
    open_path = report_open_path(target)
    if open_path is None:
        return None
    return {
        'path': open_path,
        'role_codes': [role_code],
    }


def open_target_bytes_sha(target: dict[str, Any] | None, *, prefix: str = 'selected_next_command_open_target') -> dict[str, Any]:
    defaults = {
        f'{prefix}_bytes': None,
        f'{prefix}_sha256': None,
    }
    if target is None:
        return defaults
    open_path = report_open_path(target)
    if open_path is None:
        return defaults
    path = ROOT / open_path
    if not path.exists():
        return defaults
    return {
        f'{prefix}_bytes': path.stat().st_size,
        f'{prefix}_sha256': sha256_file(path),
    }


def command_target_bytes_sha_scale_and_counts(target: dict[str, Any] | None, *, prefix: str = 'selected_next_command_target') -> dict[str, Any]:
    typed_defaults = {field_name: None for role_fields in TARGET_TYPED_COUNT_FIELDS.get(prefix, {}).values() for field_name in role_fields}
    defaults = {
        f'{prefix}_bytes': None,
        f'{prefix}_sha256': None,
        f'{prefix}_scale_summary': None,
        **typed_defaults,
    }
    if target is None:
        return defaults
    path = ROOT / target['path']
    if not path.exists():
        return defaults
    role_codes = target.get('role_codes') or []
    primary_role = role_codes[0] if role_codes else None
    counts: dict[str, Any] = {}
    summary = None
    if primary_role in REPORT_ROLE_TO_SCALE_SUMMARY or primary_role in TARGET_TYPED_COUNT_FIELDS.get(prefix, {}):
        try:
            counts = load_json(path).get('counts', {})
        except Exception:
            counts = {}
    if primary_role in REPORT_ROLE_TO_SCALE_SUMMARY and counts:
        try:
            summary = REPORT_ROLE_TO_SCALE_SUMMARY[primary_role](counts)
        except Exception:
            summary = None
    data = {
        f'{prefix}_bytes': path.stat().st_size,
        f'{prefix}_sha256': sha256_file(path),
        f'{prefix}_scale_summary': summary,
        **typed_defaults,
    }
    for field_name, count_key in TARGET_TYPED_COUNT_FIELDS.get(prefix, {}).get(primary_role, {}).items():
        data[field_name] = counts.get(count_key)
    return data



def command_target_and_semantics(command: str | None, *, open_role_code: str = 'selected-next-command-open') -> dict[str, Any]:
    if not command:
        return {
            'selected_next_command_target': None,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            'selected_next_command_target_bytes': None,
            'selected_next_command_target_sha256': None,
            'selected_next_command_target_scale_summary': None,
            'selected_next_command_target_lineage_count': None,
            'selected_next_command_target_review_item_count': None,
            'selected_next_command_target_unresolved_lineage_count': None,
        }
    parts = shlex.split(command)
    if len(parts) < 2 or parts[0] != './grpy':
        return {
            'selected_next_command_target': None,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            'selected_next_command_target_bytes': None,
            'selected_next_command_target_sha256': None,
            'selected_next_command_target_scale_summary': None,
            'selected_next_command_target_lineage_count': None,
            'selected_next_command_target_review_item_count': None,
            'selected_next_command_target_unresolved_lineage_count': None,
        }
    script = parts[1]
    command_kind: str | None = None
    stem: str | None = None
    if script.startswith('./scripts/test/check_cooperation_benchmark_card_') and script.endswith('.py'):
        command_kind = 'verify'
        stem = script.removeprefix('./scripts/test/check_cooperation_benchmark_card_').removesuffix('.py')
    elif script.startswith('./scripts/report/build_cooperation_benchmark_card_') and script.endswith('.py'):
        command_kind = 'refresh'
        stem = script.removeprefix('./scripts/report/build_cooperation_benchmark_card_').removesuffix('.py')
    if stem is None or command_kind is None:
        return {
            'selected_next_command_target': None,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            'selected_next_command_target_bytes': None,
            'selected_next_command_target_sha256': None,
            'selected_next_command_target_scale_summary': None,
            'selected_next_command_target_lineage_count': None,
            'selected_next_command_target_review_item_count': None,
            'selected_next_command_target_unresolved_lineage_count': None,
        }
    subject_role_code = REPORT_STEM_TO_ROLE.get(stem)
    label = REPORT_ROLE_TO_LABEL.get(subject_role_code)
    if subject_role_code is None or label is None:
        return {
            'selected_next_command_target': None,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_target_bytes': None,
            'selected_next_command_target_sha256': None,
            'selected_next_command_target_scale_summary': None,
            'selected_next_command_target_lineage_count': None,
            'selected_next_command_target_review_item_count': None,
            'selected_next_command_target_unresolved_lineage_count': None,
        }
    target = {
        'path': f'artifacts/reports/cooperation_benchmark_card_{stem}.json',
        'role_codes': [subject_role_code],
    }
    if command_kind == 'verify':
        intent_summary = f'Verify {label}.'
        outcome_summary = f'Expect clean validator exit for {label}.'
        effect_code = 'read-only-check'
    else:
        intent_summary = f'Refresh {label}.'
        outcome_summary = f'Expect {label} to be rewritten in place.'
        effect_code = 'in-place-report-rewrite'
    return {
        'selected_next_command_target': target,
        'selected_next_command_subject_role_code': subject_role_code,
        'selected_next_command_intent_summary': intent_summary,
        'selected_next_command_outcome_summary': outcome_summary,
        'selected_next_command_effect_code': effect_code,
        'selected_next_command_open_path': report_open_path(target),
        'selected_next_command_open_target': report_open_target(target, role_code=open_role_code),
        **open_target_bytes_sha(target),
        **command_target_bytes_sha_scale_and_counts(target),
    }


def fallback_command_and_semantics(command: str | None) -> dict[str, Any]:
    data = command_target_and_semantics(command, open_role_code='selected-fallback-command-open')
    return {
        'selected_fallback_command_target': data['selected_next_command_target'],
        'selected_fallback_command_subject_role_code': data['selected_next_command_subject_role_code'],
        'selected_fallback_command_intent_summary': data['selected_next_command_intent_summary'],
        'selected_fallback_command_outcome_summary': data['selected_next_command_outcome_summary'],
        'selected_fallback_command_effect_code': data['selected_next_command_effect_code'],
        'selected_fallback_command_open_path': data['selected_next_command_open_path'],
        'selected_fallback_command_open_target': report_open_target(data['selected_next_command_target'], role_code='selected-fallback-command-open'),
        **open_target_bytes_sha(data['selected_next_command_target'], prefix='selected_fallback_command_open_target'),
        **command_target_bytes_sha_scale_and_counts(data['selected_next_command_target'], prefix='selected_fallback_command_target'),
    }



def required_lane_for_command(command: str | None) -> str | None:
    if not command:
        return None
    if command.startswith('./grpy '):
        return 'python-integrity'
    if command.startswith('make ') or command.startswith('./scripts/test/run_harness.sh') or 'rust_exec.sh' in command:
        return 'rust-harness'
    return None


def required_lane_row(lane_id: str | None, execution_lanes: dict[str, Any]) -> dict[str, Any] | None:
    if lane_id is None:
        return None
    lane = next((row for row in execution_lanes.get('lanes', []) if row.get('lane_id') == lane_id), None)
    return lane if isinstance(lane, dict) else None


def required_lane_available(lane_id: str | None, execution_lanes: dict[str, Any]) -> bool | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    available = lane.get('available')
    return available if isinstance(available, bool) else None


def required_lane_summary(lane_id: str | None, execution_lanes: dict[str, Any]) -> str | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    summary = lane.get('summary')
    return summary if isinstance(summary, str) else None


def required_lane_blocking_reason_codes(lane_id: str | None, execution_lanes: dict[str, Any]) -> list[str] | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    codes = lane.get('blocking_reason_codes')
    if not isinstance(codes, list) or any(not isinstance(code, str) for code in codes):
        return None
    return codes


def ladder_target_typed_counts(target: dict[str, Any] | None) -> dict[str, Any]:
    if target is None:
        return {}
    path = ROOT / target['path']
    if not path.exists():
        return {}
    role_codes = target.get('role_codes') or []
    primary_role = role_codes[0] if role_codes else None
    field_map = LADDER_TARGET_TYPED_COUNT_FIELDS.get(primary_role)
    if not field_map:
        return {}
    try:
        counts = load_json(path).get('counts', {})
    except Exception:
        counts = {}
    return {field_name: counts.get(count_key) for field_name, count_key in field_map.items()}


def command_ladder_entries(selected_command: str, fallback_commands: list[str], execution_lanes: dict[str, Any]) -> list[dict[str, Any]]:
    ladder_commands = ordered_unique([selected_command] + [command for command in fallback_commands if command != selected_command])
    entries: list[dict[str, Any]] = []
    for position, command in enumerate(ladder_commands, start=1):
        semantics = command_target_and_semantics(command, open_role_code='selected-command-ladder-open')
        lane_id = required_lane_for_command(command)
        entries.append({
            'position': position,
            'command': command,
            'required_lane_id': lane_id,
            'required_lane_available': required_lane_available(lane_id, execution_lanes),
            'required_lane_summary': required_lane_summary(lane_id, execution_lanes),
            'required_lane_blocking_reason_codes': required_lane_blocking_reason_codes(lane_id, execution_lanes),
            'subject_role_code': semantics['selected_next_command_subject_role_code'],
            'intent_summary': semantics['selected_next_command_intent_summary'],
            'outcome_summary': semantics['selected_next_command_outcome_summary'],
            'effect_code': semantics['selected_next_command_effect_code'],
            'target': semantics['selected_next_command_target'],
            'target_bytes': semantics['selected_next_command_target_bytes'],
            'target_sha256': semantics['selected_next_command_target_sha256'],
            'target_scale_summary': semantics['selected_next_command_target_scale_summary'],
            **ladder_target_typed_counts(semantics['selected_next_command_target']),
            'open_path': semantics['selected_next_command_open_path'],
            'open_target': semantics['selected_next_command_open_target'],
            'open_target_bytes': semantics['selected_next_command_open_target_bytes'],
            'open_target_sha256': semantics['selected_next_command_open_target_sha256'],
        })
    return entries


def ready_candidate() -> dict[str, Any]:
    action_kind = 'verify_ready_surface'
    bucket, label = PRIORITY_BUCKETS[action_kind]
    fallback_commands = [
        './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
        './grpy ./scripts/test/check_cooperation_benchmark_card_citation_surface.py',
        './grpy ./scripts/test/check_cooperation_benchmark_card_handoff_pack.py',
        fallback_command(),
    ]
    return {
        'candidate_id': action_kind,
        'action_kind': action_kind,
        'priority_bucket': bucket,
        'priority_label': label,
        'summary': 'Compact-card citation and handoff surfaces are ready; verify the current fused surface before proceeding.',
        'lineage_id': None,
        'reason_codes': [],
        'next_command': './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
        'fallback_commands': ordered_unique(fallback_commands),
        'selected': False,
    }


def unresolved_candidate(lineage: dict[str, Any]) -> dict[str, Any]:
    action_kind = 'inspect_unresolved_citation'
    bucket, label = PRIORITY_BUCKETS[action_kind]
    lineage_id = lineage['lineage_id']
    reason_codes = ordered_unique(list(lineage.get('citation_reason_codes', [])) + list(lineage.get('warning_reason_codes', [])))
    review_commands = ordered_unique(
        [value for value in [lineage.get('primary_review_command')] + list(lineage.get('review_commands', [])) + [
            './grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write',
            fallback_command(),
        ] if value]
    )
    return {
        'candidate_id': f'inspect-unresolved:{lineage_id}',
        'action_kind': action_kind,
        'priority_bucket': bucket,
        'priority_label': label,
        'summary': 'Inspect unresolved citation/control-plane state for this lineage before trusting inherited citation answers.',
        'lineage_id': lineage_id,
        'reason_codes': reason_codes,
        'next_command': review_commands[0],
        'fallback_commands': review_commands,
        'selected': False,
    }


def review_candidate(group: dict[str, Any]) -> dict[str, Any]:
    priority_kind = group['item_kinds'][0]
    bucket, label = PRIORITY_BUCKETS.get(priority_kind, (99, priority_kind.replace('_', '-')))
    summaries = {
        'delta_drift': 'Refresh retained delta-basis evidence for this lineage before treating the current citation basis as trustworthy.',
        'freeze_drift': 'Refresh retained freeze evidence for this lineage because the bound card/render surface drifted.',
        'freeze_needed': 'Guard-freeze the current claim-ready operational head so the lineage regains a current citation head.',
        'topology_review': 'Resolve lineage topology / head ambiguity before trusting compact-card citation or handoff state.',
        'readiness_lint': 'Finish claim-readiness work so this lineage can participate in compact-card citation / freeze surfaces.',
    }
    return {
        'candidate_id': f"review-lineage:{group['lineage_id']}",
        'action_kind': 'review_lineage',
        'priority_bucket': bucket,
        'priority_label': label,
        'summary': summaries.get(priority_kind, 'Review grouped compact-card repair work for this lineage.'),
        'lineage_id': group['lineage_id'],
        'reason_codes': group['reason_codes'],
        'next_command': group['primary_review_command'],
        'fallback_commands': ordered_unique(group['review_commands'] + group['apply_commands'] + [fallback_command()]),
        'selected': False,
    }


def collect() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    control_plane = control_plane_builder.collect()
    macro_review_queue = macro_review_queue_builder.collect()
    execution_lanes = execution_lanes_builder.collect()

    candidates: list[dict[str, Any]] = []
    if macro_review_queue['groups']:
        candidates.extend(review_candidate(group) for group in macro_review_queue['groups'])
    elif control_plane['verdict'] == 'ready':
        candidates.append(ready_candidate())
    else:
        unresolved_lineages = [
            lineage for lineage in control_plane['lineages']
            if lineage.get('citation_reason_codes') or lineage.get('warning_reason_codes')
        ]
        if unresolved_lineages:
            candidates.extend(unresolved_candidate(lineage) for lineage in unresolved_lineages)
        else:
            candidates.append(
                {
                    'candidate_id': 'inspect-control-plane',
                    'action_kind': 'inspect_unresolved_citation',
                    'priority_bucket': PRIORITY_BUCKETS['inspect_unresolved_citation'][0],
                    'priority_label': PRIORITY_BUCKETS['inspect_unresolved_citation'][1],
                    'summary': 'Refresh and inspect the compact-card control plane because review pressure exists without a grouped lineage queue.',
                    'lineage_id': None,
                    'reason_codes': [],
                    'next_command': fallback_command(),
                    'fallback_commands': ordered_unique([
                        fallback_command(),
                        './grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write',
                        './grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write',
                    ]),
                    'selected': False,
                }
            )

    candidates.sort(key=lambda row: (row['priority_bucket'], row['candidate_id']))
    winner = candidates[0]
    winning_bucket = winner['priority_bucket']
    tie_set = [row for row in candidates if row['priority_bucket'] == winning_bucket]
    selected_candidate_id = min(row['candidate_id'] for row in tie_set)
    for row in candidates:
        row['selected'] = row['candidate_id'] == selected_candidate_id
    selected = next(row for row in candidates if row['selected'])

    selected_command = command_target_and_semantics(selected['next_command'])
    selected_fallback = first_distinct_fallback_command(selected['fallback_commands'], selected['next_command'])
    fallback_semantics = fallback_command_and_semantics(selected_fallback)
    selected_command_ladder = command_ladder_entries(selected['next_command'], selected['fallback_commands'], execution_lanes)

    data = {
        'witness_kind': 'cooperation_benchmark_card_next_action_witness',
        'control_plane_kind': control_plane['control_plane_kind'],
        'macro_review_queue_kind': macro_review_queue['queue_kind'],
        'selector_kind': 'priority_bucket_then_candidate_id',
        'focus_selector_kind': control_plane['focus_selector_kind'],
        'focus_lineage_id': control_plane['focus_lineage_id'],
        'focus_summary': control_plane['focus_summary'],
        'focus_operational_head_card_path': control_plane['focus_operational_head_card_path'],
        'focus_citation_head_card_path': control_plane['focus_citation_head_card_path'],
        'focus_primary_open_path': control_plane['focus_primary_open_path'],
        'focus_primary_open_target': control_plane['focus_primary_open_target'],
        'focus_primary_verify_command': control_plane['focus_primary_verify_command'],
        'focus_primary_verify_target': control_plane['focus_primary_verify_target'],
        'focus_primary_verify_target_bytes': control_plane['focus_primary_verify_target_bytes'],
        'focus_primary_verify_target_sha256': control_plane['focus_primary_verify_target_sha256'],
        'focus_primary_verify_target_citation_entry_count': control_plane['focus_primary_verify_target_citation_entry_count'],
        'focus_primary_verify_target_citation_lineage_count': control_plane['focus_primary_verify_target_citation_lineage_count'],
        'focus_primary_verify_target_unresolved_lineage_count': control_plane['focus_primary_verify_target_unresolved_lineage_count'],
        'focus_primary_verify_target_scale_summary': control_plane['focus_primary_verify_target_scale_summary'],
        'focus_primary_verify_subject_role_code': control_plane['focus_primary_verify_subject_role_code'],
        'focus_primary_verify_intent_summary': control_plane['focus_primary_verify_intent_summary'],
        'focus_primary_verify_outcome_summary': control_plane['focus_primary_verify_outcome_summary'],
        'focus_primary_verify_effect_code': control_plane['focus_primary_verify_effect_code'],
        'focus_primary_refresh_command': control_plane['focus_primary_refresh_command'],
        'focus_primary_refresh_target': control_plane['focus_primary_refresh_target'],
        'focus_primary_refresh_target_bytes': control_plane['focus_primary_refresh_target_bytes'],
        'focus_primary_refresh_target_sha256': control_plane['focus_primary_refresh_target_sha256'],
        'focus_primary_refresh_target_card_count': control_plane['focus_primary_refresh_target_card_count'],
        'focus_primary_refresh_target_verified_delta_receipt_count': control_plane['focus_primary_refresh_target_verified_delta_receipt_count'],
        'focus_primary_refresh_target_latest_known_card_count': control_plane['focus_primary_refresh_target_latest_known_card_count'],
        'focus_primary_refresh_target_scale_summary': control_plane['focus_primary_refresh_target_scale_summary'],
        'focus_primary_refresh_subject_role_code': control_plane['focus_primary_refresh_subject_role_code'],
        'focus_primary_refresh_intent_summary': control_plane['focus_primary_refresh_intent_summary'],
        'focus_primary_refresh_outcome_summary': control_plane['focus_primary_refresh_outcome_summary'],
        'focus_primary_refresh_effect_code': control_plane['focus_primary_refresh_effect_code'],
        'focus_open_paths': control_plane['focus_open_paths'],
        'focus_open_targets': control_plane['focus_open_targets'],
        'control_plane_verdict': control_plane['verdict'],
        'fallback_command': fallback_command(),
        'candidate_count': len(candidates),
        'winning_priority_bucket': winning_bucket,
        'winning_priority_label': selected['priority_label'],
        'winning_candidate_count': len(tie_set),
        'winner_uniqueness': 'unique-highest-priority' if len(tie_set) == 1 else 'stable-tie-break',
        'selected_candidate_id': selected_candidate_id,
        'selected_next_command': selected['next_command'],
        'selected_next_command_target': selected_command['selected_next_command_target'],
        'selected_next_command_target_bytes': selected_command['selected_next_command_target_bytes'],
        'selected_next_command_target_sha256': selected_command['selected_next_command_target_sha256'],
        'selected_next_command_target_scale_summary': selected_command['selected_next_command_target_scale_summary'],
        'selected_next_command_target_lineage_count': selected_command['selected_next_command_target_lineage_count'],
        'selected_next_command_target_review_item_count': selected_command['selected_next_command_target_review_item_count'],
        'selected_next_command_target_unresolved_lineage_count': selected_command['selected_next_command_target_unresolved_lineage_count'],
        'selected_next_command_subject_role_code': selected_command['selected_next_command_subject_role_code'],
        'selected_next_command_intent_summary': selected_command['selected_next_command_intent_summary'],
        'selected_next_command_outcome_summary': selected_command['selected_next_command_outcome_summary'],
        'selected_next_command_effect_code': selected_command['selected_next_command_effect_code'],
        'selected_next_command_open_path': selected_command['selected_next_command_open_path'],
        'selected_next_command_open_target': selected_command['selected_next_command_open_target'],
        'selected_next_command_open_target_bytes': selected_command['selected_next_command_open_target_bytes'],
        'selected_next_command_open_target_sha256': selected_command['selected_next_command_open_target_sha256'],
        'selected_fallback_command': selected_fallback,
        'selected_fallback_command_target': fallback_semantics['selected_fallback_command_target'],
        'selected_fallback_command_subject_role_code': fallback_semantics['selected_fallback_command_subject_role_code'],
        'selected_fallback_command_intent_summary': fallback_semantics['selected_fallback_command_intent_summary'],
        'selected_fallback_command_outcome_summary': fallback_semantics['selected_fallback_command_outcome_summary'],
        'selected_fallback_command_effect_code': fallback_semantics['selected_fallback_command_effect_code'],
        'selected_fallback_command_open_path': fallback_semantics['selected_fallback_command_open_path'],
        'selected_fallback_command_open_target': fallback_semantics['selected_fallback_command_open_target'],
        'selected_fallback_command_open_target_bytes': fallback_semantics['selected_fallback_command_open_target_bytes'],
        'selected_fallback_command_open_target_sha256': fallback_semantics['selected_fallback_command_open_target_sha256'],
        'selected_fallback_command_target_bytes': fallback_semantics['selected_fallback_command_target_bytes'],
        'selected_fallback_command_target_sha256': fallback_semantics['selected_fallback_command_target_sha256'],
        'selected_fallback_command_target_scale_summary': fallback_semantics['selected_fallback_command_target_scale_summary'],
        'selected_fallback_command_target_citation_entry_count': fallback_semantics['selected_fallback_command_target_citation_entry_count'],
        'selected_fallback_command_target_citation_lineage_count': fallback_semantics['selected_fallback_command_target_citation_lineage_count'],
        'selected_fallback_command_target_unresolved_lineage_count': fallback_semantics['selected_fallback_command_target_unresolved_lineage_count'],
        'selected_command_ladder': selected_command_ladder,
        'tie_set_candidate_ids': [row['candidate_id'] for row in tie_set],
        'report_bindings': [report_binding(path_str, role) for path_str, role in REPORTS],
        'candidates': candidates,
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- control_plane_verdict: `{data['control_plane_verdict']}`",
        f"- candidate_count: {data['candidate_count']}",
        f"- winning_priority_bucket: {data['winning_priority_bucket']}",
        f"- winning_priority_label: `{data['winning_priority_label']}`",
        f"- winning_candidate_count: {data['winning_candidate_count']}",
        f"- winner_uniqueness: `{data['winner_uniqueness']}`",
        f"- selected_candidate_id: `{data['selected_candidate_id']}`",
        f"- selected_next_command: `{data['selected_next_command']}`",
        f"- selected_next_command_target: {control_plane_builder.render_focus_open_target(data['selected_next_command_target'])}",
        f"- selected_next_command_open_path: {('`' + data['selected_next_command_open_path'] + '`') if data['selected_next_command_open_path'] else 'none'}",
        f"- selected_next_command_open_target: {control_plane_builder.render_focus_open_target(data['selected_next_command_open_target'])}",
        f"- selected_next_command_open_target_bytes: {data['selected_next_command_open_target_bytes'] if data['selected_next_command_open_target_bytes'] is not None else 'none'}",
        f"- selected_next_command_open_target_sha256: {('`' + data['selected_next_command_open_target_sha256'] + '`') if data['selected_next_command_open_target_sha256'] else 'none'}",
        f"- selected_fallback_command: {('`' + data['selected_fallback_command'] + '`') if data['selected_fallback_command'] else 'none'}",
        f"- selected_fallback_command_target: {control_plane_builder.render_focus_open_target(data['selected_fallback_command_target'])}",
        f"- selected_fallback_command_subject_role_code: {('`' + data['selected_fallback_command_subject_role_code'] + '`') if data['selected_fallback_command_subject_role_code'] else 'none'}",
        f"- selected_fallback_command_intent_summary: {data['selected_fallback_command_intent_summary'] or 'none'}",
        f"- selected_fallback_command_outcome_summary: {data['selected_fallback_command_outcome_summary'] or 'none'}",
        f"- selected_fallback_command_effect_code: {('`' + data['selected_fallback_command_effect_code'] + '`') if data['selected_fallback_command_effect_code'] else 'none'}",
        f"- selected_fallback_command_open_path: {('`' + data['selected_fallback_command_open_path'] + '`') if data['selected_fallback_command_open_path'] else 'none'}",
        f"- selected_fallback_command_open_target: {control_plane_builder.render_focus_open_target(data['selected_fallback_command_open_target'])}",
        f"- selected_fallback_command_open_target_bytes: {data['selected_fallback_command_open_target_bytes'] if data['selected_fallback_command_open_target_bytes'] is not None else 'none'}",
        f"- selected_fallback_command_open_target_sha256: {('`' + data['selected_fallback_command_open_target_sha256'] + '`') if data['selected_fallback_command_open_target_sha256'] else 'none'}",
        f"- selected_fallback_command_target_bytes: {data['selected_fallback_command_target_bytes'] if data['selected_fallback_command_target_bytes'] is not None else 'none'}",
        f"- selected_fallback_command_target_sha256: {('`' + data['selected_fallback_command_target_sha256'] + '`') if data['selected_fallback_command_target_sha256'] else 'none'}",
        f"- selected_fallback_command_target_scale_summary: {data['selected_fallback_command_target_scale_summary'] or 'none'}",
        f"- selected_fallback_command_target_citation_entry_count: {data['selected_fallback_command_target_citation_entry_count'] if data['selected_fallback_command_target_citation_entry_count'] is not None else 'none'}",
        f"- selected_fallback_command_target_citation_lineage_count: {data['selected_fallback_command_target_citation_lineage_count'] if data['selected_fallback_command_target_citation_lineage_count'] is not None else 'none'}",
        f"- selected_fallback_command_target_unresolved_lineage_count: {data['selected_fallback_command_target_unresolved_lineage_count'] if data['selected_fallback_command_target_unresolved_lineage_count'] is not None else 'none'}",
        f"- selected_next_command_target_bytes: {data['selected_next_command_target_bytes'] if data['selected_next_command_target_bytes'] is not None else 'none'}",
        f"- selected_next_command_target_sha256: {('`' + data['selected_next_command_target_sha256'] + '`') if data['selected_next_command_target_sha256'] else 'none'}",
        f"- selected_next_command_target_scale_summary: {data['selected_next_command_target_scale_summary'] or 'none'}",
        f"- selected_next_command_target_lineage_count: {data['selected_next_command_target_lineage_count'] if data['selected_next_command_target_lineage_count'] is not None else 'none'}",
        f"- selected_next_command_target_review_item_count: {data['selected_next_command_target_review_item_count'] if data['selected_next_command_target_review_item_count'] is not None else 'none'}",
        f"- selected_next_command_target_unresolved_lineage_count: {data['selected_next_command_target_unresolved_lineage_count'] if data['selected_next_command_target_unresolved_lineage_count'] is not None else 'none'}",
        f"- selected_next_command_subject_role_code: {('`' + data['selected_next_command_subject_role_code'] + '`') if data['selected_next_command_subject_role_code'] else 'none'}",
        f"- selected_next_command_intent_summary: {data['selected_next_command_intent_summary'] or 'none'}",
        f"- selected_next_command_outcome_summary: {data['selected_next_command_outcome_summary'] or 'none'}",
        f"- selected_next_command_effect_code: {('`' + data['selected_next_command_effect_code'] + '`') if data['selected_next_command_effect_code'] else 'none'}",
        f"- fallback_command: `{data['fallback_command']}`",
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
        '## Selected command ladder',
        '',
    ]
    for row in data['selected_command_ladder']:
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
    lines.extend([
        '## Candidate summary',
        '',
        '| candidate_id | action_kind | priority_bucket | lineage_id | selected | reason_codes | next_command |',
        '|---|---|---:|---|---:|---|---|',
    ])
    for row in data['candidates']:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['action_kind']}` | {row['priority_bucket']} | "
            f"{('`' + row['lineage_id'] + '`') if row['lineage_id'] else '—'} | {str(row['selected']).lower()} | "
            f"{', '.join('`' + code + '`' for code in row['reason_codes']) or '—'} | `{row['next_command']}` |"
        )
    lines.extend(['', '## Tie set', ''])
    for candidate_id in data['tie_set_candidate_ids']:
        lines.append(f'- `{candidate_id}`')
    lines.extend(['', '## Report bindings', '', '| role | path | bytes | sha256 |', '|---|---|---:|---|'])
    for row in data['report_bindings']:
        lines.append(f"| `{row['role']}` | `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    lines.extend(['', '## Candidate details', ''])
    for row in data['candidates']:
        lines.append(f"### `{row['candidate_id']}`")
        lines.append('')
        lines.append(f"- action_kind: `{row['action_kind']}`")
        lines.append(f"- priority_bucket: {row['priority_bucket']}")
        lines.append(f"- priority_label: `{row['priority_label']}`")
        lines.append(f"- selected: {str(row['selected']).lower()}")
        lines.append(f"- lineage_id: {('`' + row['lineage_id'] + '`') if row['lineage_id'] else 'none'}")
        lines.append(f"- summary: {row['summary']}")
        lines.append(f"- next_command: `{row['next_command']}`")
        lines.append(f"- reason_codes: {', '.join('`' + code + '`' for code in row['reason_codes']) or 'none'}")
        lines.append('- fallback_commands:')
        for command in row['fallback_commands']:
            lines.append(f"  - `{command}`")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action_witness.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-next-action-witness: wrote {out_md}')
        print(f'cooperation-benchmark-card-next-action-witness: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-next-action-witness: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-next-action-witness: ok ({data['candidate_count']} candidates)")
    print(f'cooperation-benchmark-card-next-action-witness: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
