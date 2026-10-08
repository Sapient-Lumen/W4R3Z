#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_next_action_witness.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_next_action_witness.json'
DOC = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_NEXT_ACTION_WITNESS.md'
CONTROL_PLANE_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_control_plane.json'
EXECUTION_LANES_REPORT = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json'


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


def first_distinct_fallback_command(commands: list[str], selected_command: str) -> str | None:
    for command in commands:
        if command != selected_command:
            return command
    return None


def ordered_unique(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def report_open_path(target: dict[str, object] | None) -> str | None:
    if target is None:
        return None
    path_value = target.get('path')
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.parts[:2] != ('artifacts', 'reports') or path.suffix != '.json':
        return None
    candidate = ROOT / 'docs' / f'{path.stem.upper()}.md'
    if candidate.exists():
        return candidate.relative_to(ROOT).as_posix()
    return None


def report_open_target(target: dict[str, object] | None, *, role_code: str) -> dict[str, object] | None:
    open_path = report_open_path(target)
    if open_path is None:
        return None
    return {'path': open_path, 'role_codes': [role_code]}


def open_target_bytes_sha(target: dict[str, object] | None, *, prefix: str = 'selected_next_command_open_target') -> dict[str, object]:
    defaults = {f'{prefix}_bytes': None, f'{prefix}_sha256': None}
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
        f'{prefix}_sha256': __import__('hashlib').sha256(path.read_bytes()).hexdigest(),
    }


def resolve_selected_command(
    command: str | None,
    *,
    prefix: str = 'selected_next_command_target',
    open_role_code: str = 'selected-next-command-open',
) -> dict[str, object]:
    typed_defaults = {field_name: None for role_fields in TARGET_TYPED_COUNT_FIELDS.get(prefix, {}).values() for field_name in role_fields}
    if not command:
        return {
            'selected_next_command_target': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            f'{prefix}_bytes': None,
            f'{prefix}_sha256': None,
            f'{prefix}_scale_summary': None,
            **typed_defaults,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
        }

    verify_prefixes = ('./grpy ./scripts/test/check_cooperation_benchmark_card_',)
    refresh_prefixes = ('./grpy ./scripts/report/build_cooperation_benchmark_card_',)
    command_kind = None
    stem = None
    for verify_prefix in verify_prefixes:
        if command.startswith(verify_prefix) and command.endswith('.py'):
            command_kind = 'verify'
            stem = command.removeprefix(verify_prefix).removesuffix('.py')
            break
    if stem is None:
        for refresh_prefix in refresh_prefixes:
            if command.startswith(refresh_prefix) and command.endswith('.py --write'):
                command_kind = 'refresh'
                stem = command.removeprefix(refresh_prefix).removesuffix('.py --write')
                break
    if stem is None or command_kind is None:
        return {
            'selected_next_command_target': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            f'{prefix}_bytes': None,
            f'{prefix}_sha256': None,
            f'{prefix}_scale_summary': None,
            **typed_defaults,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
        }
    subject_role_code = REPORT_STEM_TO_ROLE.get(stem)
    label = REPORT_ROLE_TO_LABEL.get(subject_role_code)
    if subject_role_code is None or label is None:
        return {
            'selected_next_command_target': None,
            'selected_next_command_open_path': None,
            'selected_next_command_open_target': None,
            'selected_next_command_open_target_bytes': None,
            'selected_next_command_open_target_sha256': None,
            f'{prefix}_bytes': None,
            f'{prefix}_sha256': None,
            f'{prefix}_scale_summary': None,
            **typed_defaults,
            'selected_next_command_subject_role_code': None,
            'selected_next_command_intent_summary': None,
            'selected_next_command_outcome_summary': None,
            'selected_next_command_effect_code': None,
        }
    if command_kind == 'verify':
        intent_summary = f'Verify {label}.'
        outcome_summary = f'Expect clean validator exit for {label}.'
        effect_code = 'read-only-check'
    else:
        intent_summary = f'Refresh {label}.'
        outcome_summary = f'Expect {label} to be rewritten in place.'
        effect_code = 'in-place-report-rewrite'
    target = {
        'path': f'artifacts/reports/cooperation_benchmark_card_{stem}.json',
        'role_codes': [subject_role_code],
    }
    target_path = ROOT / target['path']
    counts = json.loads(target_path.read_text(encoding='utf-8')).get('counts', {})
    data = {
        'selected_next_command_target': target,
        'selected_next_command_open_path': report_open_path(target),
        'selected_next_command_open_target': report_open_target(target, role_code=open_role_code),
        **open_target_bytes_sha(target),
        f'{prefix}_bytes': target_path.stat().st_size,
        f'{prefix}_sha256': __import__('hashlib').sha256(target_path.read_bytes()).hexdigest(),
        f'{prefix}_scale_summary': REPORT_ROLE_TO_SCALE_SUMMARY.get(subject_role_code, lambda _counts: None)(counts),
        **typed_defaults,
        'selected_next_command_subject_role_code': subject_role_code,
        'selected_next_command_intent_summary': intent_summary,
        'selected_next_command_outcome_summary': outcome_summary,
        'selected_next_command_effect_code': effect_code,
    }
    for field_name, count_key in TARGET_TYPED_COUNT_FIELDS.get(prefix, {}).get(subject_role_code, {}).items():
        data[field_name] = counts.get(count_key)
    return data



def required_lane_for_command(command: str | None) -> str | None:
    if not command:
        return None
    if command.startswith('./grpy '):
        return 'python-integrity'
    if command.startswith('make ') or command.startswith('./scripts/test/run_harness.sh') or 'rust_exec.sh' in command:
        return 'rust-harness'
    return None


def required_lane_row(lane_id: str | None, execution_lanes: dict[str, object]) -> dict[str, object] | None:
    if lane_id is None:
        return None
    lanes = execution_lanes.get('lanes', [])
    if not isinstance(lanes, list):
        return None
    lane = next((row for row in lanes if isinstance(row, dict) and row.get('lane_id') == lane_id), None)
    return lane if isinstance(lane, dict) else None


def required_lane_available(lane_id: str | None, execution_lanes: dict[str, object]) -> bool | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    available = lane.get('available')
    return available if isinstance(available, bool) else None


def required_lane_summary(lane_id: str | None, execution_lanes: dict[str, object]) -> str | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    summary = lane.get('summary')
    return summary if isinstance(summary, str) else None


def required_lane_blocking_reason_codes(lane_id: str | None, execution_lanes: dict[str, object]) -> list[str] | None:
    lane = required_lane_row(lane_id, execution_lanes)
    if lane is None:
        return None
    codes = lane.get('blocking_reason_codes')
    if not isinstance(codes, list) or any(not isinstance(code, str) for code in codes):
        return None
    return codes


def ladder_target_typed_counts(target: dict[str, object] | None) -> dict[str, object]:
    if target is None:
        return {}
    path_value = target.get('path')
    role_codes = target.get('role_codes') or []
    if not isinstance(path_value, str) or not role_codes:
        return {}
    target_path = ROOT / path_value
    if not target_path.exists():
        return {}
    primary_role = role_codes[0]
    field_map = LADDER_TARGET_TYPED_COUNT_FIELDS.get(primary_role)
    if not field_map:
        return {}
    counts = json.loads(target_path.read_text(encoding='utf-8')).get('counts', {})
    return {field_name: counts.get(count_key) for field_name, count_key in field_map.items()}


def build_command_ladder(selected_command: str, fallback_commands: list[str], execution_lanes: dict[str, object]) -> list[dict[str, object]]:
    ladder_commands = ordered_unique([selected_command] + [command for command in fallback_commands if command != selected_command])
    entries: list[dict[str, object]] = []
    for position, command in enumerate(ladder_commands, start=1):
        semantics = resolve_selected_command(command, open_role_code='selected-command-ladder-open')
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


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-next-action-witness: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return fail(proc.stderr.strip() or proc.stdout.strip() or 'next action witness builder failed')
    if not REPORT.exists():
        return fail(f'missing report {REPORT.relative_to(ROOT)}')
    if not DOC.exists():
        return fail(f'missing doc {DOC.relative_to(ROOT)}')
    if not CONTROL_PLANE_REPORT.exists():
        return fail(f'missing report {CONTROL_PLANE_REPORT.relative_to(ROOT)}')
    if not EXECUTION_LANES_REPORT.exists():
        return fail(f'missing report {EXECUTION_LANES_REPORT.relative_to(ROOT)}')
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    control_plane = json.loads(CONTROL_PLANE_REPORT.read_text(encoding='utf-8'))
    execution_lanes = json.loads(EXECUTION_LANES_REPORT.read_text(encoding='utf-8'))
    if data.get('witness_kind') != 'cooperation_benchmark_card_next_action_witness':
        return fail('unexpected witness_kind')
    if data.get('control_plane_kind') != 'cooperation_benchmark_card_control_plane':
        return fail('unexpected control_plane_kind')
    if data.get('macro_review_queue_kind') != 'cooperation_benchmark_card_macro_review_queue':
        return fail('unexpected macro_review_queue_kind')
    if data.get('selector_kind') != 'priority_bucket_then_candidate_id':
        return fail('unexpected selector_kind')
    if data.get('focus_selector_kind') != 'review_item_count_then_warning_reason_count_then_citation_reason_count_then_lineage_id':
        return fail('unexpected focus_selector_kind')
    candidates = data.get('candidates', [])
    if data.get('candidate_count') != len(candidates):
        return fail('candidate_count does not match candidates length')
    if not candidates:
        return fail('expected at least one candidate')
    selected = [row for row in candidates if row.get('selected')]
    if len(selected) != 1:
        return fail('expected exactly one selected candidate')
    selected_row = selected[0]
    if data.get('selected_candidate_id') != selected_row.get('candidate_id'):
        return fail('selected_candidate_id does not match selected candidate')
    if data.get('selected_next_command') != selected_row.get('next_command'):
        return fail('selected_next_command does not match selected candidate')
    expected_selected = resolve_selected_command(data['selected_next_command'])
    expected_command_ladder = build_command_ladder(selected_row.get('next_command'), selected_row.get('fallback_commands', []), execution_lanes)
    if data.get('selected_next_command_target') != expected_selected['selected_next_command_target']:
        return fail('selected_next_command_target does not match selected next command')
    if data.get('selected_next_command_target_bytes') != expected_selected['selected_next_command_target_bytes']:
        return fail('selected_next_command_target_bytes does not match selected next command')
    if data.get('selected_next_command_target_sha256') != expected_selected['selected_next_command_target_sha256']:
        return fail('selected_next_command_target_sha256 does not match selected next command')
    if data.get('selected_next_command_target_scale_summary') != expected_selected['selected_next_command_target_scale_summary']:
        return fail('selected_next_command_target_scale_summary does not match selected next command')
    if data.get('selected_next_command_target_lineage_count') != expected_selected['selected_next_command_target_lineage_count']:
        return fail('selected_next_command_target_lineage_count does not match selected next command')
    if data.get('selected_next_command_target_review_item_count') != expected_selected['selected_next_command_target_review_item_count']:
        return fail('selected_next_command_target_review_item_count does not match selected next command')
    if data.get('selected_next_command_target_unresolved_lineage_count') != expected_selected['selected_next_command_target_unresolved_lineage_count']:
        return fail('selected_next_command_target_unresolved_lineage_count does not match selected next command')
    if data.get('selected_next_command_subject_role_code') != expected_selected['selected_next_command_subject_role_code']:
        return fail('selected_next_command_subject_role_code does not match selected next command')
    if data.get('selected_next_command_intent_summary') != expected_selected['selected_next_command_intent_summary']:
        return fail('selected_next_command_intent_summary does not match selected next command')
    if data.get('selected_next_command_outcome_summary') != expected_selected['selected_next_command_outcome_summary']:
        return fail('selected_next_command_outcome_summary does not match selected next command')
    if data.get('selected_next_command_effect_code') != expected_selected['selected_next_command_effect_code']:
        return fail('selected_next_command_effect_code does not match selected next command')
    if data.get('selected_next_command_open_target') != expected_selected['selected_next_command_open_target']:
        return fail('selected_next_command_open_target does not match selected next command')
    if data.get('selected_command_ladder') != expected_command_ladder:
        return fail('selected_command_ladder does not match selected command semantics')
    if not data.get('selected_command_ladder'):
        return fail('selected_command_ladder must contain at least one step')
    if data['selected_command_ladder'][0].get('command') != data.get('selected_next_command'):
        return fail('selected_command_ladder must start with selected_next_command')
    expected_fallback_command = first_distinct_fallback_command(selected_row.get('fallback_commands', []), selected_row.get('next_command'))
    if data.get('selected_fallback_command') != expected_fallback_command:
        return fail('selected_fallback_command does not match first distinct fallback command')
    expected_fallback = resolve_selected_command(
        expected_fallback_command,
        prefix='selected_fallback_command_target',
        open_role_code='selected-fallback-command-open',
    )
    if data.get('selected_fallback_command_target') != expected_fallback['selected_next_command_target']:
        return fail('selected_fallback_command_target does not match selected fallback command')
    if data.get('selected_fallback_command_subject_role_code') != expected_fallback['selected_next_command_subject_role_code']:
        return fail('selected_fallback_command_subject_role_code does not match selected fallback command')
    if data.get('selected_fallback_command_intent_summary') != expected_fallback['selected_next_command_intent_summary']:
        return fail('selected_fallback_command_intent_summary does not match selected fallback command')
    if data.get('selected_fallback_command_outcome_summary') != expected_fallback['selected_next_command_outcome_summary']:
        return fail('selected_fallback_command_outcome_summary does not match selected fallback command')
    if data.get('selected_fallback_command_effect_code') != expected_fallback['selected_next_command_effect_code']:
        return fail('selected_fallback_command_effect_code does not match selected fallback command')
    if data.get('selected_fallback_command_open_target') != expected_fallback['selected_next_command_open_target']:
        return fail('selected_fallback_command_open_target does not match selected fallback command')
    if data.get('selected_fallback_command_open_target_bytes') != expected_fallback['selected_next_command_open_target_bytes']:
        return fail('selected_fallback_command_open_target_bytes does not match selected fallback command')
    if data.get('selected_fallback_command_open_target_sha256') != expected_fallback['selected_next_command_open_target_sha256']:
        return fail('selected_fallback_command_open_target_sha256 does not match selected fallback command')
    if data.get('selected_fallback_command_target_bytes') != expected_fallback['selected_fallback_command_target_bytes']:
        return fail('selected_fallback_command_target_bytes does not match selected fallback command')
    if data.get('selected_fallback_command_target_sha256') != expected_fallback['selected_fallback_command_target_sha256']:
        return fail('selected_fallback_command_target_sha256 does not match selected fallback command')
    if data.get('selected_fallback_command_target_scale_summary') != expected_fallback['selected_fallback_command_target_scale_summary']:
        return fail('selected_fallback_command_target_scale_summary does not match selected fallback command')
    if data.get('selected_fallback_command_target_citation_entry_count') != expected_fallback['selected_fallback_command_target_citation_entry_count']:
        return fail('selected_fallback_command_target_citation_entry_count does not match selected fallback command')
    if data.get('selected_fallback_command_target_citation_lineage_count') != expected_fallback['selected_fallback_command_target_citation_lineage_count']:
        return fail('selected_fallback_command_target_citation_lineage_count does not match selected fallback command')
    if data.get('selected_fallback_command_target_unresolved_lineage_count') != expected_fallback['selected_fallback_command_target_unresolved_lineage_count']:
        return fail('selected_fallback_command_target_unresolved_lineage_count does not match selected fallback command')
    if expected_fallback_command is not None:
        if len(data['selected_command_ladder']) < 2 or data['selected_command_ladder'][1].get('command') != expected_fallback_command:
            return fail('selected_command_ladder second step must match selected_fallback_command when present')
    for index, row in enumerate(data.get('selected_command_ladder', []), start=1):
        if row.get('position') != index:
            return fail('selected_command_ladder positions must be sequential starting at 1')
        open_target = row.get('open_target')
        if open_target is not None and open_target.get('role_codes') != ['selected-command-ladder-open']:
            return fail('selected_command_ladder open targets must carry selected-command-ladder-open role code')
        lane_id = row.get('required_lane_id')
        if lane_id is not None:
            lane = next((lane for lane in execution_lanes.get('lanes', []) if lane.get('lane_id') == lane_id), None)
            if lane is None:
                return fail('selected_command_ladder required_lane_id must exist in execution lanes when present')
            if row.get('required_lane_available') != lane.get('available'):
                return fail('selected_command_ladder required_lane_available must match execution lanes')
            if row.get('required_lane_summary') != lane.get('summary'):
                return fail('selected_command_ladder required_lane_summary must match execution lanes')
            if row.get('required_lane_blocking_reason_codes') != lane.get('blocking_reason_codes'):
                return fail('selected_command_ladder required_lane_blocking_reason_codes must match execution lanes')
        elif row.get('required_lane_available') is not None:
            return fail('selected_command_ladder required_lane_available must be null when required_lane_id is null')
        elif row.get('required_lane_summary') is not None or row.get('required_lane_blocking_reason_codes') is not None:
            return fail('selected_command_ladder required_lane_summary and required_lane_blocking_reason_codes must be null when required_lane_id is null')
    selected_next_open_path = data.get('selected_next_command_open_path')
    selected_next_open_target = data.get('selected_next_command_open_target')
    if selected_next_open_path is None and selected_next_open_target is not None:
        return fail('selected_next_command_open_target should be null when selected_next_command_open_path is null')
    if selected_next_open_path is not None:
        if not (ROOT / selected_next_open_path).exists():
            return fail('selected_next_command_open_path must exist when present')
        if selected_next_open_target is None:
            return fail('selected_next_command_open_target must be present when selected_next_command_open_path is present')
        if selected_next_open_target.get('path') != selected_next_open_path:
            return fail('selected_next_command_open_target path must match selected_next_command_open_path')
        if selected_next_open_target.get('role_codes') != ['selected-next-command-open']:
            return fail('selected_next_command_open_target must carry selected-next-command-open role code')
        open_path = ROOT / selected_next_open_path
        if data.get('selected_next_command_open_target_bytes') != open_path.stat().st_size:
            return fail('selected_next_command_open_target_bytes must match selected_next_command_open_path bytes')
        if data.get('selected_next_command_open_target_sha256') != __import__('hashlib').sha256(open_path.read_bytes()).hexdigest():
            return fail('selected_next_command_open_target_sha256 must match selected_next_command_open_path sha256')
        if data.get('selected_next_command_open_target_bytes') is not None and data['selected_next_command_open_target_bytes'] < 1:
            return fail('selected_next_command_open_target_bytes must be positive when present')
        if data.get('selected_next_command_open_target_sha256') is not None and len(data['selected_next_command_open_target_sha256']) != 64:
            return fail('selected_next_command_open_target_sha256 must be 64 hex chars when present')
    selected_fallback_open_path = data.get('selected_fallback_command_open_path')
    selected_fallback_open_target = data.get('selected_fallback_command_open_target')
    if selected_fallback_open_path is None and selected_fallback_open_target is not None:
        return fail('selected_fallback_command_open_target should be null when selected_fallback_command_open_path is null')
    if selected_fallback_open_path is not None:
        if not (ROOT / selected_fallback_open_path).exists():
            return fail('selected_fallback_command_open_path must exist when present')
        if selected_fallback_open_target is None:
            return fail('selected_fallback_command_open_target must be present when selected_fallback_command_open_path is present')
        if selected_fallback_open_target.get('path') != selected_fallback_open_path:
            return fail('selected_fallback_command_open_target path must match selected_fallback_command_open_path')
        if selected_fallback_open_target.get('role_codes') != ['selected-fallback-command-open']:
            return fail('selected_fallback_command_open_target must carry selected-fallback-command-open role code')
        open_path = ROOT / selected_fallback_open_path
        if data.get('selected_fallback_command_open_target_bytes') != open_path.stat().st_size:
            return fail('selected_fallback_command_open_target_bytes must match selected_fallback_command_open_path bytes')
        if data.get('selected_fallback_command_open_target_sha256') != __import__('hashlib').sha256(open_path.read_bytes()).hexdigest():
            return fail('selected_fallback_command_open_target_sha256 must match selected_fallback_command_open_path sha256')
        if data.get('selected_fallback_command_open_target_bytes') is not None and data['selected_fallback_command_open_target_bytes'] < 1:
            return fail('selected_fallback_command_open_target_bytes must be positive when present')
        if data.get('selected_fallback_command_open_target_sha256') is not None and len(data['selected_fallback_command_open_target_sha256']) != 64:
            return fail('selected_fallback_command_open_target_sha256 must be 64 hex chars when present')
    tie_set_ids = data.get('tie_set_candidate_ids', [])
    if data.get('selected_candidate_id') not in tie_set_ids:
        return fail('selected candidate must appear in tie set')
    candidate_ids = {row['candidate_id'] for row in candidates}
    if not set(tie_set_ids).issubset(candidate_ids):
        return fail('tie set contains unknown candidate ids')
    winning_bucket = data.get('winning_priority_bucket')
    tie_rows = [row for row in candidates if row['candidate_id'] in tie_set_ids]
    if len(tie_rows) != data.get('winning_candidate_count'):
        return fail('winning_candidate_count does not match tie set size')
    if any(row['priority_bucket'] != winning_bucket for row in tie_rows):
        return fail('tie set candidates must share winning priority bucket')
    if min(tie_set_ids) != data.get('selected_candidate_id'):
        return fail('selected candidate should be lexicographically smallest in tie set')
    expected_uniqueness = 'unique-highest-priority' if len(tie_rows) == 1 else 'stable-tie-break'
    if data.get('winner_uniqueness') != expected_uniqueness:
        return fail('winner_uniqueness does not match tie set size')
    if len(data.get('report_bindings', [])) < 2:
        return fail('expected at least two report_bindings')
    if data.get('candidate_count') and data.get('focus_summary') is None:
        return fail('focus_summary should be present when candidates exist')
    primary_open = data.get('focus_primary_open_path')
    allowed_open_paths = {value for value in [data.get('focus_citation_head_card_path'), data.get('focus_operational_head_card_path')] if value}
    citation_path = data.get('focus_citation_head_card_path')
    operational_path = data.get('focus_operational_head_card_path')
    if citation_path:
        allowed_open_paths.add(str(Path(citation_path).with_suffix('.md')))
    if operational_path:
        allowed_open_paths.add(str(Path(operational_path).with_suffix('.md')))
    if primary_open is not None and primary_open not in allowed_open_paths:
        return fail('focus_primary_open_path must be derived from witness focus paths')
    if primary_open is not None and not (ROOT / primary_open).exists():
        return fail('focus_primary_open_path must exist when present')
    focus_open_paths = data.get('focus_open_paths', [])
    if primary_open is not None and (not focus_open_paths or focus_open_paths[0] != primary_open):
        return fail('focus_open_paths must start with focus_primary_open_path when present')
    if any(path_value not in allowed_open_paths for path_value in focus_open_paths):
        return fail('focus_open_paths must be derived from witness focus paths')
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
    if data.get('focus_primary_verify_subject_role_code') not in (None, 'citation-surface-report'):
        return fail('focus_primary_verify_subject_role_code must be null or citation-surface-report')
    if data.get('focus_primary_verify_target_bytes') != control_plane.get('focus_primary_verify_target_bytes'):
        return fail('focus_primary_verify_target_bytes does not match control plane')
    if data.get('focus_primary_verify_target_bytes') is not None and data['focus_primary_verify_target_bytes'] < 1:
        return fail('focus_primary_verify_target_bytes must be positive when present')
    if data.get('focus_primary_verify_target_sha256') != control_plane.get('focus_primary_verify_target_sha256'):
        return fail('focus_primary_verify_target_sha256 does not match control plane')
    if data.get('focus_primary_verify_target_sha256') is not None and len(data['focus_primary_verify_target_sha256']) != 64:
        return fail('focus_primary_verify_target_sha256 must be 64 hex chars when present')
    if data.get('focus_primary_verify_target_citation_entry_count') != control_plane.get('focus_primary_verify_target_citation_entry_count'):
        return fail('focus_primary_verify_target_citation_entry_count does not match control plane')
    if data.get('focus_primary_verify_target_citation_lineage_count') != control_plane.get('focus_primary_verify_target_citation_lineage_count'):
        return fail('focus_primary_verify_target_citation_lineage_count does not match control plane')
    if data.get('focus_primary_verify_target_unresolved_lineage_count') != control_plane.get('focus_primary_verify_target_unresolved_lineage_count'):
        return fail('focus_primary_verify_target_unresolved_lineage_count does not match control plane')
    if data.get('focus_primary_verify_target_scale_summary') != control_plane.get('focus_primary_verify_target_scale_summary'):
        return fail('focus_primary_verify_target_scale_summary does not match control plane')
    if data.get('focus_primary_verify_target_citation_entry_count') is not None and data['focus_primary_verify_target_citation_entry_count'] < 1:
        return fail('focus_primary_verify_target_citation_entry_count must be positive when present')
    if data.get('focus_primary_verify_target_citation_lineage_count') is not None and data['focus_primary_verify_target_citation_lineage_count'] < 1:
        return fail('focus_primary_verify_target_citation_lineage_count must be positive when present')
    if data.get('focus_primary_verify_target_unresolved_lineage_count') is not None and data['focus_primary_verify_target_unresolved_lineage_count'] < 0:
        return fail('focus_primary_verify_target_unresolved_lineage_count must be non-negative when present')
    if data.get('focus_primary_verify_intent_summary') not in (None, 'Verify citation surface report.'):
        return fail('focus_primary_verify_intent_summary must be null or the citation-surface verify summary')
    if data.get('focus_primary_verify_outcome_summary') not in (None, 'Expect clean validator exit for citation surface report.'):
        return fail('focus_primary_verify_outcome_summary must be null or the citation-surface verify outcome summary')
    if data.get('focus_primary_verify_effect_code') not in (None, 'read-only-check'):
        return fail('focus_primary_verify_effect_code must be null or read-only-check')
    if data.get('focus_primary_refresh_subject_role_code') not in (None, 'inventory-report'):
        return fail('focus_primary_refresh_subject_role_code must be null or inventory-report')
    if data.get('focus_primary_refresh_target_bytes') != control_plane.get('focus_primary_refresh_target_bytes'):
        return fail('focus_primary_refresh_target_bytes does not match control plane')
    if data.get('focus_primary_refresh_target_bytes') is not None and data['focus_primary_refresh_target_bytes'] < 1:
        return fail('focus_primary_refresh_target_bytes must be positive when present')
    if data.get('focus_primary_refresh_target_sha256') != control_plane.get('focus_primary_refresh_target_sha256'):
        return fail('focus_primary_refresh_target_sha256 does not match control plane')
    if data.get('focus_primary_refresh_target_sha256') is not None and len(data['focus_primary_refresh_target_sha256']) != 64:
        return fail('focus_primary_refresh_target_sha256 must be 64 hex chars when present')
    if data.get('focus_primary_refresh_target_card_count') != control_plane.get('focus_primary_refresh_target_card_count'):
        return fail('focus_primary_refresh_target_card_count does not match control plane')
    if data.get('focus_primary_refresh_target_verified_delta_receipt_count') != control_plane.get('focus_primary_refresh_target_verified_delta_receipt_count'):
        return fail('focus_primary_refresh_target_verified_delta_receipt_count does not match control plane')
    if data.get('focus_primary_refresh_target_latest_known_card_count') != control_plane.get('focus_primary_refresh_target_latest_known_card_count'):
        return fail('focus_primary_refresh_target_latest_known_card_count does not match control plane')
    if data.get('focus_primary_refresh_target_scale_summary') != control_plane.get('focus_primary_refresh_target_scale_summary'):
        return fail('focus_primary_refresh_target_scale_summary does not match control plane')
    if data.get('focus_primary_refresh_target_card_count') is not None and data['focus_primary_refresh_target_card_count'] < 1:
        return fail('focus_primary_refresh_target_card_count must be positive when present')
    if data.get('focus_primary_refresh_target_verified_delta_receipt_count') is not None and data['focus_primary_refresh_target_verified_delta_receipt_count'] < 0:
        return fail('focus_primary_refresh_target_verified_delta_receipt_count must be non-negative when present')
    if data.get('focus_primary_refresh_target_latest_known_card_count') is not None and data['focus_primary_refresh_target_latest_known_card_count'] < 0:
        return fail('focus_primary_refresh_target_latest_known_card_count must be non-negative when present')
    if data.get('focus_primary_refresh_intent_summary') not in (None, 'Refresh inventory report.'):
        return fail('focus_primary_refresh_intent_summary must be null or the inventory refresh summary')
    if data.get('focus_primary_refresh_outcome_summary') not in (None, 'Expect inventory report to be rewritten in place.'):
        return fail('focus_primary_refresh_outcome_summary must be null or the inventory refresh outcome summary')
    if data.get('focus_primary_refresh_effect_code') not in (None, 'in-place-report-rewrite'):
        return fail('focus_primary_refresh_effect_code must be null or in-place-report-rewrite')
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
    print('cooperation-benchmark-card-next-action-witness: ok')
    print(f'cooperation-benchmark-card-next-action-witness: validated {REPORT.relative_to(ROOT)} and {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
