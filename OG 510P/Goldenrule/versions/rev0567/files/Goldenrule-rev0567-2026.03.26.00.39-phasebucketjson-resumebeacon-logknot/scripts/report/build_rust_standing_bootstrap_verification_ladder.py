#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DELTA_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_standing_bootstrap_delta.json'
EXECUTION_CARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_card.json'
EXTERNAL_QUEUE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_verification_ladder.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_verification_ladder.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER.md'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _affected_rows(delta: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, Any]]:
    by_test = {entry['proposed_test_name']: entry for entry in queue['entries']}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for seed in delta['seeds']:
        for queue_row in seed['queue_rows']:
            test_name = queue_row['proposed_test_name']
            if test_name in seen:
                continue
            entry = by_test[test_name]
            rows.append(
                {
                    'family': queue_row['family'],
                    'variant': queue_row['variant'],
                    'seed_path': seed['seed_path'],
                    'probe_id': seed['probe_id'],
                    'update_rule': seed['update_rule'],
                    'proposed_test_name': test_name,
                    'future_cargo_hint': entry['future_cargo_hint'],
                    'target_lane': entry['target_lane'],
                    'target_test_file': entry['target_test_file'],
                    'lift_band': entry['lift_band'],
                    'test_focus': entry['test_focus'],
                    'trace_only': seed['classification'] == 'trace_only',
                    'mean_stats_invariant': bool(seed['mean_stats_invariant']),
                    'first_standing_diff_round': seed['trace_delta']['first_standing_diff_round'],
                }
            )
            seen.add(test_name)
    rows.sort(key=lambda row: (row['seed_path'], row['family'], row['variant'], row['proposed_test_name']))
    return rows


def build_report() -> dict[str, Any]:
    delta = _load(DELTA_REPORT)
    execution = _load(EXECUTION_CARD_REPORT)
    queue = _load(EXTERNAL_QUEUE_REPORT)
    affected_rows = _affected_rows(delta, queue)
    final_state = next(plan for plan in execution['state_plans'] if plan['state_id'] == 'final_full')
    exact_commands = [row['future_cargo_hint'] for row in affected_rows]
    stages = [
        {
            'stage_id': 'dedicated_bootstrap_guard',
            'kind': 'exact_test_file',
            'rationale': 'Run the dedicated bootstrap regression file first. It is the most direct proof that round-0 standing now honors declared world bootstrap values.',
            'what_it_proves': 'The narrow repair plus dedicated guard landed and the round-0 standing seam is closed on the exact simple-standing seeds.',
            'commands': ['cargo test -p gr_engine --test probe_standing_bootstrap -- --exact'],
        },
        {
            'stage_id': 'standing_affected_probe_rows',
            'kind': 'exact_external_witnesses',
            'rationale': 'Then run only the three exact external witnesses whose queue rows map to the currently affected bootstrap semantics. This is the cheapest direct end-to-end confirmation that the repaired seam still preserves external execution witnesses for simple-standing, image-scoring, and standing-norm rows.',
            'what_it_proves': 'Every currently affected queue row still executes as an external Rust witness after the bootstrap repair.',
            'commands': exact_commands,
        },
        {
            'stage_id': 'probe_lane_smoke',
            'kind': 'broader_lane_smoke',
            'rationale': 'Only after the focused exact witnesses are green should you broaden to the whole probe_run lane.',
            'what_it_proves': 'The bootstrap fix did not leave a broader probe_run regression outside the directly affected standing rows.',
            'commands': ['cargo test -p gr_engine --test probe_run'],
        },
    ]
    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                DELTA_REPORT.relative_to(ROOT).as_posix(),
                EXECUTION_CARD_REPORT.relative_to(ROOT).as_posix(),
                EXTERNAL_QUEUE_REPORT.relative_to(ROOT).as_posix(),
            ],
            'tool_path': TOOL_PATH.relative_to(ROOT).as_posix(),
        },
        'summary': {
            'final_state_precondition': 'final_full',
            'expected_final_combined_hash': execution['summary']['canonical_final_combined_hash'],
            'affected_queue_row_count': len(affected_rows),
            'affected_seed_count': delta['summary']['affected_unique_seed_count'],
            'exact_probe_run_command_count': len(exact_commands),
            'verification_stage_count': len(stages),
            'all_affected_rows_trace_only': all(row['trace_only'] for row in affected_rows),
            'all_affected_rows_mean_stats_invariant': all(row['mean_stats_invariant'] for row in affected_rows),
            'tool_invocation': 'python3 scripts/tools/emit_rust_standing_bootstrap_verification_ladder.py --target-root . --json',
        },
        'affected_rows': affected_rows,
        'stages': stages,
        'precondition_policy': {
            'summary': 'Emit the ladder only from the proved final bootstrap/comeback state. Otherwise, fail closed and route the user back to the execution-plan tool so apply sequencing happens before verification sequencing.',
            'check_command': 'python3 scripts/tools/emit_rust_standing_bootstrap_execution_plan.py --target-root . --json',
        },
        'headline_findings': [
            'The bootstrap seam only touches three current comeback queue rows, so the first Rust-capable inheritor does not need to pay for a full-lane smoke immediately just to verify the repair.',
            'A minimal standing-focused verification success path now exists: dedicated `probe_standing_bootstrap` first, then the three exact affected `probe_run` witnesses, then broader `probe_run` smoke.',
            'Those three exact `probe_run` witnesses correspond one-for-one to the queue rows exposed by the blocked-session delta report: `simple_standing`, `image_scoring`, and `standing_norm`.',
            'Because the delta remains trace-only and mean-stat invariant on the blocked-session oracle surface, this ladder is scoped to proving repaired standing initialization and preserved external execution witnesses, not to re-proving every unaffected lane first.',
        ],
        'final_state_reference': {
            'state_id': final_state['state_id'],
            'verification_commands': final_state['verification_commands'],
            'route_kind': final_state['route_kind'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Verification Ladder',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_verification_ladder.py`. This gives the first Rust-capable inheritor the smallest post-apply verification sequence for the repaired simple-standing bootstrap seam: it gates on the exact proved final bootstrap/comeback state, starts with the dedicated seam guard, then runs only the exact external witnesses whose queue rows are semantically affected before broadening to whole-lane smoke.',
        '',
        '## Snapshot',
        '',
        f"- final_state_precondition: `{s['final_state_precondition']}`",
        f"- expected_final_combined_hash: `{s['expected_final_combined_hash']}`",
        f"- affected_queue_row_count: `{s['affected_queue_row_count']}`",
        f"- affected_seed_count: `{s['affected_seed_count']}`",
        f"- exact_probe_run_command_count: `{s['exact_probe_run_command_count']}`",
        f"- verification_stage_count: `{s['verification_stage_count']}`",
        f"- all_affected_rows_trace_only: `{str(s['all_affected_rows_trace_only']).lower()}`",
        f"- all_affected_rows_mean_stats_invariant: `{str(s['all_affected_rows_mean_stats_invariant']).lower()}`",
        f"- tool invocation: `{s['tool_invocation']}`",
        '',
        '## Why this exists',
        '',
    ]
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## Affected external witnesses',
        '',
        '| family | variant | seed | exact witness |',
        '|---|---|---|---|',
    ])
    for row in report['affected_rows']:
        lines.append(
            f"| `{row['family']}` | `{row['variant']}` | `{row['seed_path']}` | `{row['future_cargo_hint']}` |"
        )
    lines.extend([
        '',
        '## Verification ladder',
        '',
        'Precondition: run the execution-plan tool first. This ladder is only valid after the checkout is already recognized as `final_full` and matches the exact final 4-file bootstrap/comeback hash.',
        '',
    ])
    for idx, stage in enumerate(report['stages'], start=1):
        lines.extend([
            f"### Stage {idx} — `{stage['stage_id']}`",
            '',
            f"- kind: `{stage['kind']}`",
            f"- rationale: {stage['rationale']}",
            f"- what_it_proves: {stage['what_it_proves']}",
            '',
            '**Commands**',
            '',
        ])
        for cmd in stage['commands']:
            lines.append(f"- `{cmd}`")
        lines.append('')
    lines.extend([
        '## Safe operational reading',
        '',
        '1. Do not use this ladder on a non-final bootstrap branch state; let the execution-plan tool finish routing apply steps first.',
        '2. Run the dedicated `probe_standing_bootstrap` file before any broader smoke because it is the cheapest exact proof that round-0 standing now honors declared world bootstrap values.',
        '3. Run the three exact affected `probe_run` witnesses next; they are the only current external queue rows whose semantics intersect the bootstrap seam.',
        '4. Broaden to `cargo test -p gr_engine --test probe_run` only after those focused witnesses are green.',
        '',
        '## Final-state reference',
        '',
        f"- route_kind at final state: `{report['final_state_reference']['route_kind']}`",
        '- final-state verification commands already recorded by the execution card:',
    ])
    for cmd in report['final_state_reference']['verification_commands']:
        lines.append(f"  - `{cmd}`")
    lines.append('')
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-verification-ladder: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-verification-ladder: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-verification-ladder: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-verification-ladder: ok minimal final-state verification ladder matches delta-affected queue rows')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build_report()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown)


if __name__ == '__main__':
    raise SystemExit(main())
