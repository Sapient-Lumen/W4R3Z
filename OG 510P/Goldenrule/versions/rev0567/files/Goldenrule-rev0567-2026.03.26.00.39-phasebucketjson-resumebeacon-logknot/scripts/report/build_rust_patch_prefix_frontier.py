#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_patch_prefix_frontier.json'
OUT_MD = ROOT / 'docs' / 'RUST_PATCH_PREFIX_FRONTIER.md'
SHARDS_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'
QUEUE_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'


BAND_ORDER = {
    'lift_first': 0,
    'externalize_now': 1,
    'broaden_after_lift': 2,
}


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _entry_key(row: dict[str, object]) -> tuple[str, str, str]:
    return (str(row['variant']), str(row['target_lane']), str(row['proposed_test_name']))


def _milestone_record(prefix_index: int, label: str, rationale: str) -> dict[str, object]:
    return {
        'prefix_index': prefix_index,
        'label': label,
        'rationale': rationale,
    }


def build_report() -> dict[str, object]:
    required = [SHARDS_JSON, QUEUE_JSON]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError('missing required source artifact(s): ' + ', '.join(missing))

    shards_report = _read_json(SHARDS_JSON)
    queue_report = _read_json(QUEUE_JSON)
    queue_entries = list(queue_report['entries'])
    total_queue_rows = len(queue_entries)
    total_lift_first_rows = sum(1 for row in queue_entries if row['lift_band'] == 'lift_first')
    total_probe_run_rows = sum(1 for row in queue_entries if row['target_lane'] == 'probe_run')

    cumulative_row_keys: set[tuple[str, str, str]] = set()
    cumulative_variants: set[str] = set()
    cumulative_tests: set[str] = set()
    cumulative_helpers: set[str] = set()
    cumulative_target_files: set[str] = set()
    cumulative_lanes: set[str] = set()
    cumulative_lift_band_counts = {
        'lift_first': 0,
        'externalize_now': 0,
        'broaden_after_lift': 0,
    }
    cumulative_lane_counts = {
        'probe_run': 0,
        'metamorphic_suite': 0,
    }
    cumulative_added_lines = 0
    cumulative_patch_bytes = 0

    prefixes: list[dict[str, object]] = []
    milestones: list[dict[str, object]] = []
    all_lift_first_prefix = None
    all_probe_run_prefix = None
    first_externalize_prefix = None
    full_closure_prefix = None
    best_marginal_prefix = None
    best_marginal_ratio = -1.0

    for entry in shards_report['entries']:
        rows = list(entry['rows'])
        shard_row_keys = {_entry_key(row) for row in rows}
        new_row_keys = sorted(shard_row_keys - cumulative_row_keys)
        cumulative_row_keys.update(shard_row_keys)
        cumulative_variants.update(str(row['variant']) for row in rows)
        cumulative_tests.update(str(name) for name in entry['test_names'])
        cumulative_helpers.update(str(name) for name in entry['helper_names'])
        cumulative_target_files.update(str(path) for path in entry['target_files'])
        cumulative_lanes.update(str(name) for name in entry['lanes'])
        cumulative_added_lines += int(entry['added_lines'])
        cumulative_patch_bytes += int(entry['patch_bytes'])

        for row in rows:
            cumulative_lift_band_counts[str(row['lift_band'])] += 1
            cumulative_lane_counts[str(row['target_lane'])] += 1

        marginal_new_rows = len(new_row_keys)
        marginal_ratio = (marginal_new_rows / int(entry['added_lines'])) if int(entry['added_lines']) else 0.0
        if marginal_ratio > best_marginal_ratio:
            best_marginal_ratio = marginal_ratio
            best_marginal_prefix = int(entry['series_index'])

        milestone_labels: list[str] = []
        if first_externalize_prefix is None and cumulative_lift_band_counts['externalize_now'] > 0:
            first_externalize_prefix = int(entry['series_index'])
            milestone_labels.append('first externalize-now row available')
            milestones.append(_milestone_record(first_externalize_prefix, 'first_externalize_now', 'first prefix that includes any row tagged `externalize_now`'))
        if all_lift_first_prefix is None and cumulative_lift_band_counts['lift_first'] == total_lift_first_rows:
            all_lift_first_prefix = int(entry['series_index'])
            milestone_labels.append('all lift-first rows covered')
            milestones.append(_milestone_record(all_lift_first_prefix, 'all_lift_first_rows', 'first prefix that covers every `lift_first` queue row'))
        if all_probe_run_prefix is None and cumulative_lane_counts['probe_run'] == total_probe_run_rows:
            all_probe_run_prefix = int(entry['series_index'])
            milestone_labels.append('all probe-run rows covered')
            milestones.append(_milestone_record(all_probe_run_prefix, 'all_probe_run_rows', 'first prefix that covers every `probe_run` queue row'))
        if full_closure_prefix is None and len(cumulative_row_keys) == total_queue_rows:
            full_closure_prefix = int(entry['series_index'])
            milestone_labels.append('full weak-row closure')
            milestones.append(_milestone_record(full_closure_prefix, 'full_queue_closure', 'first prefix that covers every current weak-row comeback entry'))

        prefixes.append({
            'prefix_index': int(entry['series_index']),
            'latest_patch_path': str(entry['patch_path']),
            'latest_seed_path': str(entry['seed_path']),
            'latest_bundle_strategy': str(entry['bundle_strategy']),
            'latest_lane_mix': str(entry['lane_mix']),
            'latest_lift_bands': list(entry['lift_bands']),
            'marginal_new_rows': marginal_new_rows,
            'marginal_rows_per_added_line': round(marginal_ratio, 5),
            'marginal_variants': sorted(str(row['variant']) for row in rows),
            'milestones_hit': milestone_labels,
            'cumulative': {
                'rows_covered': len(cumulative_row_keys),
                'rows_remaining': total_queue_rows - len(cumulative_row_keys),
                'rows_coverage_fraction': round(len(cumulative_row_keys) / total_queue_rows, 5) if total_queue_rows else 0.0,
                'lift_band_counts': dict(cumulative_lift_band_counts),
                'target_lane_counts': dict(cumulative_lane_counts),
                'variant_count': len(cumulative_variants),
                'variants': sorted(cumulative_variants),
                'test_count': len(cumulative_tests),
                'helper_count': len(cumulative_helpers),
                'target_file_count': len(cumulative_target_files),
                'target_files': sorted(cumulative_target_files),
                'lane_count': len(cumulative_lanes),
                'lanes': sorted(cumulative_lanes),
                'added_lines': cumulative_added_lines,
                'patch_bytes': cumulative_patch_bytes,
            },
        })

    stop_points = []
    if prefixes:
        stop_points.append({
            'label': 'quick_foothold',
            'prefix_index': 1,
            'why_stop_here': 'lands the first external Rust witness with the smallest helper/test surface',
            'rows_covered': prefixes[0]['cumulative']['rows_covered'],
            'added_lines': prefixes[0]['cumulative']['added_lines'],
        })
    if all_lift_first_prefix is not None:
        pref = prefixes[all_lift_first_prefix - 1]
        stop_points.append({
            'label': 'lift_first_closure',
            'prefix_index': all_lift_first_prefix,
            'why_stop_here': 'covers every row tagged `lift_first`, which is the cleanest first comeback plateau',
            'rows_covered': pref['cumulative']['rows_covered'],
            'added_lines': pref['cumulative']['added_lines'],
        })
    if all_probe_run_prefix is not None and all_probe_run_prefix != all_lift_first_prefix:
        pref = prefixes[all_probe_run_prefix - 1]
        stop_points.append({
            'label': 'probe_lane_closure',
            'prefix_index': all_probe_run_prefix,
            'why_stop_here': 'covers every current `probe_run` row, but only at the same final dual-lane shard that also lands the last metamorphic witness',
            'rows_covered': pref['cumulative']['rows_covered'],
            'added_lines': pref['cumulative']['added_lines'],
        })
    if full_closure_prefix is not None:
        pref = prefixes[full_closure_prefix - 1]
        stop_points.append({
            'label': 'full_closure',
            'prefix_index': full_closure_prefix,
            'why_stop_here': 'covers all current weak-row comeback entries, including the final dual-lane shard',
            'rows_covered': pref['cumulative']['rows_covered'],
            'added_lines': pref['cumulative']['added_lines'],
        })

    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_patch_prefix_frontier.v1',
            'crate': 'gr_engine',
            'source_reports': [
                SHARDS_JSON.relative_to(ROOT).as_posix(),
                QUEUE_JSON.relative_to(ROOT).as_posix(),
            ],
        },
        'summary': {
            'prefix_count': len(prefixes),
            'total_queue_rows': total_queue_rows,
            'all_lift_first_prefix': all_lift_first_prefix,
            'first_externalize_now_prefix': first_externalize_prefix,
            'all_probe_run_prefix': all_probe_run_prefix,
            'full_closure_prefix': full_closure_prefix,
            'best_marginal_prefix': best_marginal_prefix,
            'best_marginal_rows_per_added_line': round(best_marginal_ratio, 5),
        },
        'stop_points': stop_points,
        'milestones': milestones,
        'prefixes': prefixes,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    stop_points = report['stop_points']
    prefixes = report['prefixes']
    lines = [
        '# Rust Patch Prefix Frontier',
        '',
        'Generated by `scripts/report/build_rust_patch_prefix_frontier.py`. This turns the ordered shard series into a set of quantified stopping points so a future Rust-capable inheritor can choose a partial comeback landing intentionally instead of treating every patch prefix as equally valuable.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- prefix_count: {summary['prefix_count']}",
        f"- total_queue_rows: {summary['total_queue_rows']}",
        f"- first_externalize_now_prefix: {summary['first_externalize_now_prefix']}",
        f"- all_lift_first_prefix: {summary['all_lift_first_prefix']}",
        f"- all_probe_run_prefix: {summary['all_probe_run_prefix']}",
        f"- full_closure_prefix: {summary['full_closure_prefix']}",
        f"- best_marginal_prefix: {summary['best_marginal_prefix']}",
        f"- best_marginal_rows_per_added_line: {summary['best_marginal_rows_per_added_line']}",
        '',
        '## Recommended stop points',
        '',
    ]
    for stop in stop_points:
        lines.extend([
            f"- `{stop['label']}` → prefix `{stop['prefix_index']}` ({stop['rows_covered']} rows, {stop['added_lines']} added lines): {stop['why_stop_here']}",
        ])
    lines.extend([
        '',
        '## Prefix frontier',
        '',
        '| Prefix | Latest shard | Rows covered | Rows remaining | Added lines | Marginal rows/line | Milestones |',
        '| --- | --- | ---: | ---: | ---: | ---: | --- |',
    ])
    for prefix in prefixes:
        latest = Path(str(prefix['latest_seed_path'])).name
        cumulative = prefix['cumulative']
        milestones = '<br>'.join(prefix['milestones_hit']) if prefix['milestones_hit'] else '—'
        lines.append(
            f"| {prefix['prefix_index']} | `{latest}` | {cumulative['rows_covered']} | {cumulative['rows_remaining']} | {cumulative['added_lines']} | {prefix['marginal_rows_per_added_line']:.5f} | {milestones} |"
        )

    lines.extend([
        '',
        '## Prefix details',
        '',
    ])
    for prefix in prefixes:
        cumulative = prefix['cumulative']
        lines.extend([
            f"### Prefix {prefix['prefix_index']} — `{Path(str(prefix['latest_seed_path'])).name}`",
            '',
            f"- latest_patch_path: `{prefix['latest_patch_path']}`",
            f"- latest_bundle_strategy: `{prefix['latest_bundle_strategy']}`",
            f"- latest_lane_mix: `{prefix['latest_lane_mix']}`",
            f"- latest_lift_bands: {', '.join(prefix['latest_lift_bands'])}",
            f"- marginal_new_rows: {prefix['marginal_new_rows']}",
            f"- marginal_rows_per_added_line: {prefix['marginal_rows_per_added_line']:.5f}",
            f"- cumulative_rows_covered: {cumulative['rows_covered']} / {summary['total_queue_rows']}",
            f"- cumulative_added_lines: {cumulative['added_lines']}",
            f"- cumulative_patch_bytes: {cumulative['patch_bytes']}",
            f"- cumulative_lift_band_counts: `lift_first={cumulative['lift_band_counts']['lift_first']}`, `externalize_now={cumulative['lift_band_counts']['externalize_now']}`, `broaden_after_lift={cumulative['lift_band_counts']['broaden_after_lift']}`",
            f"- cumulative_target_lane_counts: `probe_run={cumulative['target_lane_counts']['probe_run']}`, `metamorphic_suite={cumulative['target_lane_counts']['metamorphic_suite']}`",
            f"- cumulative_variants: {', '.join(cumulative['variants'])}",
            f"- milestones_hit: {', '.join(prefix['milestones_hit']) if prefix['milestones_hit'] else 'none'}",
            '',
        ])
    return '\n'.join(lines).rstrip() + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build a quantified stopping-point frontier for the blocked-Rust external-test patch shard series.')
    parser.add_argument('--write', action='store_true', help='write outputs instead of diff-checking them')
    args = parser.parse_args(argv)

    report = build_report()
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'
    md = render_markdown(report)

    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'rust-patch-prefix-frontier: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-patch-prefix-frontier: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = [p.relative_to(ROOT).as_posix() for p in [OUT_JSON, OUT_MD] if not p.exists()]
    if missing:
        for rel in missing:
            print(f'rust-patch-prefix-frontier: missing {rel}', file=sys.stderr)
        return 1

    drift = False
    for path, expected in [(OUT_JSON, js), (OUT_MD, md)]:
        current = path.read_text(encoding='utf-8')
        if current != expected:
            print(f'rust-patch-prefix-frontier: drift detected in {path.relative_to(ROOT)}; run with --write', file=sys.stderr)
            drift = True
    if drift:
        return 1

    print(f"rust-patch-prefix-frontier: ok ({report['summary']['prefix_count']} prefixes)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
