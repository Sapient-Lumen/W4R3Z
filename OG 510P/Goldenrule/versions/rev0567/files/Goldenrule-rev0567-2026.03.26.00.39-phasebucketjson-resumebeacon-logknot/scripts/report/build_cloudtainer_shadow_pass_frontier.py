#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROCESS_DIR = ROOT / 'artifacts' / 'process'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_frontier.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_SHADOW_PASS_FRONTIER.md'

FRONTIER_ANCHORS: list[tuple[str, str, str]] = [
    (
        'doctor_probe',
        'boundary_known',
        'quickly confirms the missing-toolchain boundary before spending time on longer blocked-session work',
    ),
    (
        'test_rust_test_scenario_coverage',
        'maps_contracts_coverage',
        'lands the core static Rust navigation, restart, contract, and scenario-coverage ledgers in one short prefix',
    ),
    (
        'test_rust_seed_loader_readiness',
        'queue_inputs_ready',
        'extends the static prefix through witness, seed, lift-queue, and direct-loader audits so the comeback inputs are current',
    ),
    (
        'test_rust_patch_prefix_frontier',
        'static_comeback_plan_closed',
        'closes the full static Rust comeback planning lane, including patchset, shard, rehearsal, and shard-prefix frontier reports',
    ),
    (
        'update_artifact_buckets',
        'archive_hygiene_synced',
        'refreshes the command and artifact inventories after the static planning lane completes',
    ),
    (
        'grlab_certify_tests',
        'full_shadow_pass',
        'completes the entire blocked-session pass, including the local Python certification lane and final receipt write',
    ),
]


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _latest_receipt() -> Path:
    candidates = sorted(path for path in PROCESS_DIR.glob('cloudtainer_shadow_pass_*.json') if path.name != 'cloudtainer_shadow_pass_checkpoint.json')
    if not candidates:
        raise FileNotFoundError('no cloudtainer shadow-pass receipts found under artifacts/process/')
    return candidates[-1]


def _index_by_step_id(rows: list[dict[str, object]]) -> dict[str, tuple[int, dict[str, object]]]:
    return {str(row['id']): (idx, row) for idx, row in enumerate(rows, start=1)}


def _round(value: float) -> float:
    rounded = round(value, 3)
    return 0.0 if abs(rounded) < 0.0005 else rounded


def build_report() -> dict[str, object]:
    receipt_path = _latest_receipt()
    receipt = _read_json(receipt_path)
    rows = list(receipt.get('steps') or [])
    if not rows:
        raise ValueError(f'{receipt_path.relative_to(ROOT).as_posix()} has no steps')

    total_duration = sum(float(row.get('duration_seconds', 0.0)) for row in rows)
    by_id = _index_by_step_id(rows)

    lane_totals: dict[str, float] = {}
    cumulative = 0.0
    cumulative_rows: list[dict[str, object]] = []
    for idx, row in enumerate(rows, start=1):
        duration = float(row.get('duration_seconds', 0.0))
        lane = str(row['lane'])
        lane_totals[lane] = lane_totals.get(lane, 0.0) + duration
        cumulative += duration
        cumulative_rows.append(
            {
                'step_index': idx,
                'id': str(row['id']),
                'lane': lane,
                'duration_seconds': _round(duration),
                'cumulative_seconds': _round(cumulative),
                'remaining_seconds': _round(total_duration - cumulative),
                'status': str(row['status']),
            }
        )

    frontiers: list[dict[str, object]] = []
    for step_id, label, rationale in FRONTIER_ANCHORS:
        if step_id not in by_id:
            raise ValueError(f'frontier anchor missing from latest receipt: {step_id}')
        step_index, row = by_id[step_id]
        prefix = cumulative_rows[step_index - 1]
        frontiers.append(
            {
                'label': label,
                'step_index': step_index,
                'step_id': step_id,
                'lane': str(row['lane']),
                'rationale': rationale,
                'cumulative_seconds': prefix['cumulative_seconds'],
                'remaining_seconds': prefix['remaining_seconds'],
                'cumulative_fraction': round(prefix['cumulative_seconds'] / total_duration, 5) if total_duration else 0.0,
            }
        )

    heaviest_steps = sorted(
        (
            {
                'step_index': idx,
                'step_id': str(row['id']),
                'lane': str(row['lane']),
                'duration_seconds': _round(float(row.get('duration_seconds', 0.0))),
                'status': str(row['status']),
            }
            for idx, row in enumerate(rows, start=1)
        ),
        key=lambda item: (-float(item['duration_seconds']), int(item['step_index'])),
    )[:5]

    recommended_budget_prefixes = [
        {
            'label': 'short_budget',
            'frontier_label': 'maps_contracts_coverage',
            'why_choose_it': 'best short-run prefix when you need the static navigation and contract ledgers but not the full comeback patch lane',
            'command': 'make cloudtainer-shadow-pass-short',
            'resume_command': 'make cloudtainer-shadow-pass-resume',
        },
        {
            'label': 'medium_budget',
            'frontier_label': 'queue_inputs_ready',
            'why_choose_it': 'best medium-run prefix when you also want the comeback queue and seed-loader audits refreshed',
            'command': 'make cloudtainer-shadow-pass-medium',
            'resume_command': 'make cloudtainer-shadow-pass-resume',
        },
        {
            'label': 'long_budget',
            'frontier_label': 'static_comeback_plan_closed',
            'why_choose_it': 'best long-run prefix when you want the full static Rust comeback plan refreshed before resuming later for inventory and Python lanes',
            'command': 'make cloudtainer-shadow-pass-long',
            'resume_command': 'make cloudtainer-shadow-pass-resume',
        },
    ]

    return {
        'metadata': {
            'inventory_version': '2026-03-23.cloudtainer_shadow_pass_frontier.v2',
            'source_receipt': receipt_path.relative_to(ROOT).as_posix(),
            'source_receipt_version': receipt.get('receipt_version'),
            'profile': receipt.get('profile'),
        },
        'summary': {
            'step_count': len(rows),
            'total_duration_seconds': _round(total_duration),
            'decision': receipt.get('decision'),
            'receipt_created_at_utc': receipt.get('created_at_utc'),
            'receipt_completed_at_utc': receipt.get('completed_at_utc'),
            'resumed_from_checkpoint': bool((receipt.get('checkpointing') or {}).get('resumed_from_checkpoint')),
            'initial_completed_rows': int((receipt.get('checkpointing') or {}).get('initial_completed_rows', 0)),
        },
        'lane_totals': [
            {
                'lane': lane,
                'duration_seconds': _round(duration),
                'duration_fraction': round(duration / total_duration, 5) if total_duration else 0.0,
            }
            for lane, duration in sorted(lane_totals.items(), key=lambda item: (-item[1], item[0]))
        ],
        'recommended_budget_prefixes': recommended_budget_prefixes,
        'frontiers': frontiers,
        'heaviest_steps': heaviest_steps,
        'steps': cumulative_rows,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    lane_totals = report['lane_totals']
    frontiers = report['frontiers']
    heaviest_steps = report['heaviest_steps']
    budget_prefixes = report['recommended_budget_prefixes']

    frontier_by_label = {str(entry['label']): entry for entry in frontiers}

    lines = [
        '# Cloudtainer Shadow Pass Frontier',
        '',
        'Generated by `scripts/report/build_cloudtainer_shadow_pass_frontier.py`. This turns the latest full blocked-session receipt into a time-budgeting map so a future inheritor can choose a good stopping prefix before relying on checkpoint/resume.',
        '',
        '## Summary',
        '',
        f"- source receipt: `{report['metadata']['source_receipt']}`",
        f"- total step count: `{summary['step_count']}`",
        f"- total duration: `{summary['total_duration_seconds']}` seconds",
        f"- decision: `{summary['decision']}`",
        f"- resumed_from_checkpoint: `{str(summary['resumed_from_checkpoint']).lower()}`",
        f"- initial_completed_rows before resume: `{summary['initial_completed_rows']}`",
        '',
        '## Lane totals',
        '',
    ]
    for lane in lane_totals:
        lines.append(
            f"- `{lane['lane']}`: `{lane['duration_seconds']}` seconds ({round(float(lane['duration_fraction']) * 100, 2)}% of the full pass)"
        )

    lines.extend([
        '',
        '## Recommended budgeting prefixes',
        '',
    ])
    for entry in budget_prefixes:
        frontier = frontier_by_label[str(entry['frontier_label'])]
        lines.extend([
            f"### {entry['label']}",
            '',
            f"- stop after step `{frontier['step_index']}` (`{frontier['step_id']}`)",
            f"- cumulative duration: `{frontier['cumulative_seconds']}` seconds",
            f"- remaining duration if resumed later: `{frontier['remaining_seconds']}` seconds",
            f"- command: `{entry['command']}`",
            f"- resume later with: `{entry['resume_command']}`",
            f"- why: {entry['why_choose_it']}",
            '',
        ])

    lines.extend([
        '## Frontier checkpoints',
        '',
    ])
    for frontier in frontiers:
        lines.extend([
            f"### {frontier['label']}",
            '',
            f"- step `{frontier['step_index']}` / `{summary['step_count']}`: `{frontier['step_id']}`",
            f"- lane: `{frontier['lane']}`",
            f"- cumulative duration: `{frontier['cumulative_seconds']}` seconds",
            f"- remaining duration: `{frontier['remaining_seconds']}` seconds",
            f"- share of full pass: `{round(float(frontier['cumulative_fraction']) * 100, 2)}`%",
            f"- rationale: {frontier['rationale']}",
            '',
        ])

    lines.extend([
        '## Heaviest steps',
        '',
    ])
    for step in heaviest_steps:
        lines.append(
            f"- step `{step['step_index']}` `{step['step_id']}` (`{step['lane']}`): `{step['duration_seconds']}` seconds"
        )

    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a frontier report for budgeting interrupted cloudtainer shadow-pass runs.')
    parser.add_argument('--write', action='store_true', help='write the JSON and Markdown report artifacts')
    args = parser.parse_args()

    try:
        report = build_report()
    except Exception as exc:  # pragma: no cover
        print(f'cloudtainer-shadow-pass-frontier: error: {exc}', file=sys.stderr)
        return 1

    md = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'cloudtainer-shadow-pass-frontier: wrote {OUT_JSON.relative_to(ROOT).as_posix()} and {OUT_MD.relative_to(ROOT).as_posix()}')
    else:
        print(
            'cloudtainer-shadow-pass-frontier: ok '
            f"(source={report['metadata']['source_receipt']}, total_duration_seconds={report['summary']['total_duration_seconds']}, frontiers={len(report['frontiers'])})"
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
