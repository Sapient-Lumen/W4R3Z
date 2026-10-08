#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROCESS_DIR = ROOT / 'artifacts' / 'process'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_history.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_SHADOW_PASS_HISTORY.md'

FRONTIER_STEP_LABELS: list[tuple[str, str]] = [
    ('doctor_probe', 'boundary_known'),
    ('test_rust_test_scenario_coverage', 'maps_contracts_coverage'),
    ('test_rust_seed_loader_readiness', 'queue_inputs_ready'),
    ('test_rust_patch_prefix_frontier', 'static_comeback_plan_closed'),
    ('update_artifact_buckets', 'archive_hygiene_synced'),
    ('grlab_certify_tests', 'full_shadow_pass'),
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _round(value: float) -> float:
    rounded = round(value, 3)
    return 0.0 if abs(rounded) < 0.0005 else rounded


def _median(values: list[float]) -> float:
    return _round(float(statistics.median(values))) if values else 0.0


def _receipt_rows(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    steps = list(payload.get('steps') or [])
    total_duration = 0.0
    cumulative_by_id: dict[str, float] = {}
    duration_by_id: dict[str, float] = {}
    lane_by_id: dict[str, str] = {}
    lane_totals: dict[str, float] = {}
    step_ids: list[str] = []
    for step in steps:
        duration = float(step.get('duration_seconds', 0.0) or 0.0)
        total_duration += duration
        step_id = str(step['id'])
        step_ids.append(step_id)
        cumulative_by_id[step_id] = total_duration
        duration_by_id[step_id] = duration
        lane = str(step['lane'])
        lane_by_id[step_id] = lane
        lane_totals[lane] = lane_totals.get(lane, 0.0) + duration
    summary_counts = payload.get('summary_counts') or {}
    checkpointing = payload.get('checkpointing') or {}
    return {
        'path': path.relative_to(ROOT).as_posix(),
        'filename': path.name,
        'receipt_version': int(payload.get('receipt_version', 0) or 0),
        'created_at_utc': payload.get('created_at_utc'),
        'completed_at_utc': payload.get('completed_at_utc'),
        'decision': payload.get('decision'),
        'step_count': len(steps),
        'step_ids': step_ids,
        'total_duration_seconds': _round(total_duration),
        'lane_totals': {lane: _round(value) for lane, value in sorted(lane_totals.items())},
        'cumulative_by_id': {step_id: _round(value) for step_id, value in cumulative_by_id.items()},
        'duration_by_id': {step_id: _round(value) for step_id, value in duration_by_id.items()},
        'lane_by_id': lane_by_id,
        'pass_count': int(summary_counts.get('pass_count', 0) or 0),
        'blocked_count': int(summary_counts.get('blocked_count', 0) or 0),
        'fail_count': int(summary_counts.get('fail_count', 0) or 0),
        'resumed_from_checkpoint': bool(checkpointing.get('resumed_from_checkpoint')),
        'initial_completed_rows': int(checkpointing.get('initial_completed_rows', 0) or 0),
    }


def build_report() -> dict[str, Any]:
    receipt_paths = sorted(path for path in PROCESS_DIR.glob('cloudtainer_shadow_pass_*.json') if path.name != 'cloudtainer_shadow_pass_checkpoint.json')
    if not receipt_paths:
        raise FileNotFoundError('no cloudtainer shadow-pass receipts found under artifacts/process/')

    timeline = [_receipt_rows(path) for path in receipt_paths]
    max_step_count = max(entry['step_count'] for entry in timeline)
    current_profile = [entry for entry in timeline if entry['step_count'] == max_step_count]
    first_entry = timeline[0]
    latest_entry = timeline[-1]
    first_ids = list(first_entry['step_ids'])
    latest_ids = list(latest_entry['step_ids'])
    added_vs_first = [step_id for step_id in latest_ids if step_id not in first_ids]
    removed_vs_first = [step_id for step_id in first_ids if step_id not in latest_ids]

    growth_events: list[dict[str, Any]] = []
    previous_ids: list[str] = []
    for entry in timeline:
        new_ids = [step_id for step_id in entry['step_ids'] if step_id not in previous_ids]
        retired_ids = [step_id for step_id in previous_ids if step_id not in entry['step_ids']]
        growth_events.append(
            {
                'receipt': entry['path'],
                'step_count': entry['step_count'],
                'new_step_ids_vs_previous': new_ids,
                'retired_step_ids_vs_previous': retired_ids,
            }
        )
        previous_ids = list(entry['step_ids'])

    current_profile_durations = [float(entry['total_duration_seconds']) for entry in current_profile]
    lane_ranges: list[dict[str, Any]] = []
    lane_names = sorted({lane for entry in current_profile for lane in entry['lane_totals']})
    for lane in lane_names:
        values = [float(entry['lane_totals'].get(lane, 0.0)) for entry in current_profile]
        lane_ranges.append(
            {
                'lane': lane,
                'sample_count': len(values),
                'min_seconds': _round(min(values)),
                'median_seconds': _median(values),
                'max_seconds': _round(max(values)),
            }
        )

    frontier_ranges: list[dict[str, Any]] = []
    for step_id, label in FRONTIER_STEP_LABELS:
        values = [float(entry['cumulative_by_id'][step_id]) for entry in current_profile if step_id in entry['cumulative_by_id']]
        if not values:
            continue
        frontier_ranges.append(
            {
                'label': label,
                'step_id': step_id,
                'sample_count': len(values),
                'min_seconds': _round(min(values)),
                'median_seconds': _median(values),
                'max_seconds': _round(max(values)),
                'spread_seconds': _round(max(values) - min(values)),
            }
        )

    recurring_heaviest: list[dict[str, Any]] = []
    for step_id in latest_ids:
        samples = [float(entry['duration_by_id'][step_id]) for entry in current_profile if step_id in entry['duration_by_id']]
        if not samples:
            continue
        recurring_heaviest.append(
            {
                'step_id': step_id,
                'lane': str(latest_entry['lane_by_id'].get(step_id, 'unknown')),
                'sample_count': len(samples),
                'mean_seconds': _round(sum(samples) / len(samples)),
                'median_seconds': _median(samples),
                'max_seconds': _round(max(samples)),
            }
        )
    recurring_heaviest.sort(key=lambda entry: (-float(entry['mean_seconds']), str(entry['step_id'])))
    recurring_heaviest = recurring_heaviest[:8]

    profile_growth_summary = {
        'first_receipt': first_entry['path'],
        'latest_receipt': latest_entry['path'],
        'first_step_count': first_entry['step_count'],
        'latest_step_count': latest_entry['step_count'],
        'added_step_ids_vs_first': added_vs_first,
        'removed_step_ids_vs_first': removed_vs_first,
    }

    receipt_timeline = []
    for entry, event in zip(timeline, growth_events):
        receipt_timeline.append(
            {
                'receipt': entry['path'],
                'receipt_version': entry['receipt_version'],
                'step_count': entry['step_count'],
                'total_duration_seconds': entry['total_duration_seconds'],
                'decision': entry['decision'],
                'pass_count': entry['pass_count'],
                'blocked_count': entry['blocked_count'],
                'fail_count': entry['fail_count'],
                'resumed_from_checkpoint': entry['resumed_from_checkpoint'],
                'initial_completed_rows': entry['initial_completed_rows'],
                'new_step_ids_vs_previous': event['new_step_ids_vs_previous'],
                'retired_step_ids_vs_previous': event['retired_step_ids_vs_previous'],
            }
        )

    return {
        'metadata': {
            'inventory_version': '2026-03-23.cloudtainer_shadow_pass_history.v1',
            'source_dir': PROCESS_DIR.relative_to(ROOT).as_posix(),
        },
        'summary': {
            'receipt_count': len(timeline),
            'current_profile_receipt_count': len(current_profile),
            'current_profile_step_count': max_step_count,
            'earliest_receipt': first_entry['path'],
            'latest_receipt': latest_entry['path'],
            'latest_receipt_version': latest_entry['receipt_version'],
            'latest_decision': latest_entry['decision'],
            'latest_resumed_from_checkpoint': latest_entry['resumed_from_checkpoint'],
            'latest_initial_completed_rows': latest_entry['initial_completed_rows'],
            'current_profile_duration_min_seconds': _round(min(current_profile_durations)),
            'current_profile_duration_median_seconds': _median(current_profile_durations),
            'current_profile_duration_max_seconds': _round(max(current_profile_durations)),
        },
        'profile_growth': profile_growth_summary,
        'receipt_timeline': receipt_timeline,
        'current_profile_lane_ranges': lane_ranges,
        'current_profile_frontier_ranges': frontier_ranges,
        'recurring_heaviest_steps': recurring_heaviest,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    growth = report['profile_growth']
    timeline = report['receipt_timeline']
    lane_ranges = report['current_profile_lane_ranges']
    frontier_ranges = report['current_profile_frontier_ranges']
    heaviest = report['recurring_heaviest_steps']

    lines = [
        '# Cloudtainer Shadow Pass History',
        '',
        'Generated by `scripts/report/build_cloudtainer_shadow_pass_history.py`. This compresses the evolution of the blocked-session shadow pass so a future inheritor can see which receipt family is current, how much the pass widened over time, and which time-budget cutpoints stay stable across completed receipts.',
        '',
        '## Summary',
        '',
        f"- receipt count: `{summary['receipt_count']}`",
        f"- current-profile receipt count: `{summary['current_profile_receipt_count']}`",
        f"- current profile step count: `{summary['current_profile_step_count']}`",
        f"- earliest receipt: `{summary['earliest_receipt']}`",
        f"- latest receipt: `{summary['latest_receipt']}`",
        f"- current-profile duration range: `{summary['current_profile_duration_min_seconds']}` .. `{summary['current_profile_duration_max_seconds']}` seconds (median `{summary['current_profile_duration_median_seconds']}`)",
        f"- latest receipt resumed from checkpoint: `{str(summary['latest_resumed_from_checkpoint']).lower()}` (initial completed rows `{summary['latest_initial_completed_rows']}`)",
        '',
        '## Profile growth',
        '',
        f"- first recorded profile width: `{growth['first_step_count']}` steps",
        f"- latest recorded profile width: `{growth['latest_step_count']}` steps",
        f"- steps added versus first receipt: `{len(growth['added_step_ids_vs_first'])}`",
        f"- steps retired versus first receipt: `{len(growth['removed_step_ids_vs_first'])}`",
        '',
    ]
    if growth['added_step_ids_vs_first']:
        lines.append(f"- added families: `{', '.join(growth['added_step_ids_vs_first'])}`")
    if growth['removed_step_ids_vs_first']:
        lines.append(f"- retired early-only steps: `{', '.join(growth['removed_step_ids_vs_first'])}`")

    lines.extend([
        '',
        '## Receipt timeline',
        '',
    ])
    for entry in timeline:
        lines.append(f"### {Path(str(entry['receipt'])).name}")
        lines.append('')
        lines.append(
            f"- steps: `{entry['step_count']}` | duration: `{entry['total_duration_seconds']}` seconds | decision: `{entry['decision']}` | counts: `pass={entry['pass_count']} blocked={entry['blocked_count']} fail={entry['fail_count']}`"
        )
        lines.append(
            f"- resumed_from_checkpoint: `{str(entry['resumed_from_checkpoint']).lower()}` | initial_completed_rows: `{entry['initial_completed_rows']}`"
        )
        if entry['new_step_ids_vs_previous']:
            lines.append(f"- new versus previous receipt: `{', '.join(entry['new_step_ids_vs_previous'])}`")
        if entry['retired_step_ids_vs_previous']:
            lines.append(f"- retired versus previous receipt: `{', '.join(entry['retired_step_ids_vs_previous'])}`")
        lines.append('')

    lines.extend([
        '## Stable frontier ranges across current-profile receipts',
        '',
    ])
    for entry in frontier_ranges:
        lines.append(
            f"- `{entry['label']}` (`{entry['step_id']}`): `{entry['min_seconds']}` .. `{entry['max_seconds']}` seconds across `{entry['sample_count']}` completed receipts (median `{entry['median_seconds']}`, spread `{entry['spread_seconds']}`)"
        )

    lines.extend([
        '',
        '## Current-profile lane ranges',
        '',
    ])
    for entry in lane_ranges:
        lines.append(
            f"- `{entry['lane']}`: `{entry['min_seconds']}` .. `{entry['max_seconds']}` seconds across `{entry['sample_count']}` completed receipts (median `{entry['median_seconds']}`)"
        )

    lines.extend([
        '',
        '## Recurring heavy steps in the current profile',
        '',
    ])
    for entry in heaviest:
        lines.append(
            f"- `{entry['step_id']}` (`{entry['lane']}`): mean `{entry['mean_seconds']}` seconds, median `{entry['median_seconds']}`, max `{entry['max_seconds']}` across `{entry['sample_count']}` completed receipts"
        )

    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the generated JSON and Markdown artifacts')
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.write:
        OUT_JSON.write_text(rendered, encoding='utf-8')
        OUT_MD.write_text(render_markdown(report), encoding='utf-8')
        print(f'cloudtainer-shadow-pass-history: wrote {OUT_MD}')
        print(f'cloudtainer-shadow-pass-history: wrote {OUT_JSON}')
        return 0

    expected_json = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    if report != expected_json:
        raise SystemExit('cloudtainer-shadow-pass-history: report drift detected; run with --write')
    expected_md = OUT_MD.read_text(encoding='utf-8')
    actual_md = render_markdown(report)
    if actual_md != expected_md:
        raise SystemExit('cloudtainer-shadow-pass-history: markdown drift detected; run with --write')
    print(f"cloudtainer-shadow-pass-history: ok ({summary_line(report)})")
    return 0


def summary_line(report: dict[str, Any]) -> str:
    summary = report['summary']
    return (
        f"receipts={summary['receipt_count']} current_profile={summary['current_profile_receipt_count']} "
        f"step_count={summary['current_profile_step_count']}"
    )


if __name__ == '__main__':
    raise SystemExit(main())
