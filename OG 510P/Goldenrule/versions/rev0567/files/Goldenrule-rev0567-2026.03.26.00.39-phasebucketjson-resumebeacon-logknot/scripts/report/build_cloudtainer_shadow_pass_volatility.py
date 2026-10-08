#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROCESS_DIR = ROOT / 'artifacts' / 'process'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_volatility.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_SHADOW_PASS_VOLATILITY.md'

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


def _mean(values: list[float]) -> float:
    return _round(sum(values) / len(values)) if values else 0.0


def _cv(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0.0:
        return 0.0
    return _round(float(statistics.pstdev(values)) / mean)


def _classify(*, sample_count: int, spread_seconds: float, cv_fraction: float) -> str:
    if sample_count < 2:
        return 'single_sample'
    if spread_seconds <= 0.15 and cv_fraction <= 0.03:
        return 'stable'
    if spread_seconds <= 1.0 and cv_fraction <= 0.10:
        return 'watch'
    return 'jittery'


def _receipt_rows(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    steps = list(payload.get('steps') or [])
    duration_by_id: dict[str, float] = {}
    lane_by_id: dict[str, str] = {}
    lane_totals: dict[str, float] = {}
    step_ids: list[str] = []
    total_duration = 0.0
    for step in steps:
        duration = float(step.get('duration_seconds', 0.0) or 0.0)
        total_duration += duration
        step_id = str(step['id'])
        step_ids.append(step_id)
        duration_by_id[step_id] = duration
        lane = str(step['lane'])
        lane_by_id[step_id] = lane
        lane_totals[lane] = lane_totals.get(lane, 0.0) + duration
    summary_counts = payload.get('summary_counts') or {}
    return {
        'path': path.relative_to(ROOT).as_posix(),
        'filename': path.name,
        'decision': payload.get('decision'),
        'step_count': len(steps),
        'step_ids': step_ids,
        'duration_by_id': {step_id: _round(value) for step_id, value in duration_by_id.items()},
        'lane_by_id': lane_by_id,
        'lane_totals': {lane: _round(value) for lane, value in sorted(lane_totals.items())},
        'total_duration_seconds': _round(total_duration),
        'pass_count': int(summary_counts.get('pass_count', 0) or 0),
        'blocked_count': int(summary_counts.get('blocked_count', 0) or 0),
        'fail_count': int(summary_counts.get('fail_count', 0) or 0),
    }


def build_report() -> dict[str, Any]:
    receipt_paths = sorted(path for path in PROCESS_DIR.glob('cloudtainer_shadow_pass_*.json') if path.name != 'cloudtainer_shadow_pass_checkpoint.json')
    if not receipt_paths:
        raise FileNotFoundError('no cloudtainer shadow-pass receipts found under artifacts/process/')

    timeline = [_receipt_rows(path) for path in receipt_paths]
    max_step_count = max(entry['step_count'] for entry in timeline)
    current_profile = [entry for entry in timeline if entry['step_count'] == max_step_count]
    latest_entry = timeline[-1]

    decision_counts: dict[str, int] = {}
    for entry in current_profile:
        decision = str(entry['decision'])
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    lane_names = sorted({lane for entry in current_profile for lane in entry['lane_totals']})
    lane_stats: list[dict[str, Any]] = []
    for lane in lane_names:
        values = [float(entry['lane_totals'].get(lane, 0.0)) for entry in current_profile]
        spread = _round(max(values) - min(values)) if values else 0.0
        cv = _cv(values)
        lane_stats.append(
            {
                'lane': lane,
                'sample_count': len(values),
                'mean_seconds': _mean(values),
                'median_seconds': _median(values),
                'min_seconds': _round(min(values)) if values else 0.0,
                'max_seconds': _round(max(values)) if values else 0.0,
                'spread_seconds': spread,
                'cv_fraction': cv,
                'volatility_class': _classify(sample_count=len(values), spread_seconds=spread, cv_fraction=cv),
            }
        )

    step_stats: list[dict[str, Any]] = []
    for step_id in latest_entry['step_ids']:
        values = [float(entry['duration_by_id'][step_id]) for entry in current_profile if step_id in entry['duration_by_id']]
        spread = _round(max(values) - min(values)) if values else 0.0
        cv = _cv(values)
        step_stats.append(
            {
                'step_id': step_id,
                'lane': str(latest_entry['lane_by_id'].get(step_id, 'unknown')),
                'sample_count': len(values),
                'mean_seconds': _mean(values),
                'median_seconds': _median(values),
                'min_seconds': _round(min(values)) if values else 0.0,
                'max_seconds': _round(max(values)) if values else 0.0,
                'spread_seconds': spread,
                'cv_fraction': cv,
                'volatility_class': _classify(sample_count=len(values), spread_seconds=spread, cv_fraction=cv),
            }
        )

    frontier_by_step = {step_id: label for step_id, label in FRONTIER_STEP_LABELS}
    frontier_stats = [
        {
            'label': frontier_by_step[str(entry['step_id'])],
            **entry,
        }
        for entry in step_stats
        if str(entry['step_id']) in frontier_by_step
    ]

    top_jittery_steps = sorted(
        (entry for entry in step_stats if entry['volatility_class'] == 'jittery'),
        key=lambda entry: (-float(entry['cv_fraction']), -float(entry['spread_seconds']), str(entry['step_id'])),
    )[:8]
    top_watch_steps = sorted(
        (entry for entry in step_stats if entry['volatility_class'] == 'watch'),
        key=lambda entry: (-float(entry['spread_seconds']), -float(entry['mean_seconds']), str(entry['step_id'])),
    )[:8]
    most_stable_nontrivial = sorted(
        (entry for entry in step_stats if entry['volatility_class'] == 'stable' and float(entry['mean_seconds']) >= 1.0),
        key=lambda entry: (float(entry['cv_fraction']), float(entry['spread_seconds']), -float(entry['mean_seconds']), str(entry['step_id'])),
    )[:8]

    return {
        'metadata': {
            'inventory_version': '2026-03-23.cloudtainer_shadow_pass_volatility.v1',
            'source_dir': PROCESS_DIR.relative_to(ROOT).as_posix(),
        },
        'summary': {
            'receipt_count': len(timeline),
            'current_profile_receipt_count': len(current_profile),
            'current_profile_step_count': max_step_count,
            'latest_receipt': latest_entry['path'],
            'latest_decision': latest_entry['decision'],
            'decision_mix_current_profile': [
                {'decision': decision, 'count': count}
                for decision, count in sorted(decision_counts.items())
            ],
            'current_profile_total_duration_min_seconds': _round(min(float(entry['total_duration_seconds']) for entry in current_profile)),
            'current_profile_total_duration_median_seconds': _median([float(entry['total_duration_seconds']) for entry in current_profile]),
            'current_profile_total_duration_max_seconds': _round(max(float(entry['total_duration_seconds']) for entry in current_profile)),
            'current_profile_total_duration_cv_fraction': _cv([float(entry['total_duration_seconds']) for entry in current_profile]),
        },
        'current_profile_lane_stats': lane_stats,
        'frontier_step_stats': frontier_stats,
        'top_jittery_steps': top_jittery_steps,
        'top_watch_steps': top_watch_steps,
        'most_stable_nontrivial_steps': most_stable_nontrivial,
        'step_stats': step_stats,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lane_stats = report['current_profile_lane_stats']
    frontier_stats = report['frontier_step_stats']
    top_jittery = report['top_jittery_steps']
    top_watch = report['top_watch_steps']
    most_stable = report['most_stable_nontrivial_steps']

    decision_mix = ', '.join(f"`{entry['decision']}` x{entry['count']}" for entry in summary['decision_mix_current_profile'])
    lines = [
        '# Cloudtainer Shadow Pass Volatility',
        '',
        'Generated by `scripts/report/build_cloudtainer_shadow_pass_volatility.py`. This turns the current-profile shadow-pass receipts into a compact trust map so a future inheritor can tell which timing rows are stable enough to budget tightly and which ones deserve slack.',
        '',
        '## Summary',
        '',
        f"- receipt count: `{summary['receipt_count']}`",
        f"- current-profile receipt count: `{summary['current_profile_receipt_count']}`",
        f"- current-profile step count: `{summary['current_profile_step_count']}`",
        f"- latest receipt: `{summary['latest_receipt']}`",
        f"- current-profile decision mix: {decision_mix}",
        f"- current-profile total duration range: `{summary['current_profile_total_duration_min_seconds']}` .. `{summary['current_profile_total_duration_max_seconds']}` seconds (median `{summary['current_profile_total_duration_median_seconds']}`, cv `{summary['current_profile_total_duration_cv_fraction']}`)",
        '',
        '## Lane volatility',
        '',
    ]
    for lane in lane_stats:
        lines.append(
            f"- `{lane['lane']}`: class `{lane['volatility_class']}`, mean `{lane['mean_seconds']}`s, range `{lane['min_seconds']}` .. `{lane['max_seconds']}`s, spread `{lane['spread_seconds']}`s, cv `{lane['cv_fraction']}`"
        )

    lines.extend([
        '',
        '## Frontier anchor stability',
        '',
    ])
    for entry in frontier_stats:
        lines.append(
            f"- `{entry['label']}` / `{entry['step_id']}`: class `{entry['volatility_class']}`, mean `{entry['mean_seconds']}`s, range `{entry['min_seconds']}` .. `{entry['max_seconds']}`s, spread `{entry['spread_seconds']}`s, cv `{entry['cv_fraction']}`"
        )

    lines.extend([
        '',
        '## Most jittery steps',
        '',
    ])
    for entry in top_jittery:
        lines.append(
            f"- `{entry['step_id']}` (`{entry['lane']}`): mean `{entry['mean_seconds']}`s, spread `{entry['spread_seconds']}`s, cv `{entry['cv_fraction']}`"
        )
    if not top_jittery:
        lines.append('- none')

    lines.extend([
        '',
        '## Watch-list steps',
        '',
    ])
    for entry in top_watch:
        lines.append(
            f"- `{entry['step_id']}` (`{entry['lane']}`): mean `{entry['mean_seconds']}`s, spread `{entry['spread_seconds']}`s, cv `{entry['cv_fraction']}`"
        )
    if not top_watch:
        lines.append('- none')

    lines.extend([
        '',
        '## Most stable nontrivial steps',
        '',
    ])
    for entry in most_stable:
        lines.append(
            f"- `{entry['step_id']}` (`{entry['lane']}`): mean `{entry['mean_seconds']}`s, spread `{entry['spread_seconds']}`s, cv `{entry['cv_fraction']}`"
        )
    if not most_stable:
        lines.append('- none')

    lines.extend([
        '',
        '## Reading guide',
        '',
        '- Treat `stable` rows as the safest timing anchors when budgeting a short or medium shadow pass.',
        '- Treat `watch` rows as normal but buffer-worthy; they usually stay within the same general budget class but can move enough to matter near a wrapper ceiling.',
        '- Treat `jittery` rows as soft estimates and keep extra headroom around them, especially in `archive_hygiene` and late Python lanes.',
    ])
    return '\n'.join(lines) + '\n'


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_markdown(report), encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build a volatility map for current-profile cloudtainer shadow-pass receipts.')
    parser.add_argument('--write', action='store_true', help='write the generated report to artifacts/reports and docs/')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
