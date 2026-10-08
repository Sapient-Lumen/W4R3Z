#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from build_rust_gap_witness_queue import build_queue

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_gap_probe_seed_index.json'
OUT_MD = ROOT / 'docs' / 'RUST_GAP_PROBE_SEED_INDEX.md'


def parse_witness_ref(ref: str) -> tuple[str, int]:
    path, line = ref.rsplit(':', 1)
    return path, int(line)


def load_example_id(rel_path: str) -> str | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    example_id = payload.get('id')
    if isinstance(example_id, str) and example_id.strip():
        return example_id.strip()
    return None


def classify_seed_mode(row: dict[str, object]) -> str:
    example_witnesses = [parse_witness_ref(ref)[0] for ref in row['example_witnesses']]
    if any(path.startswith('examples/probes/') for path in example_witnesses):
        return 'probe_seed_ready'
    if int(row['witness_counts']['example']) > 0:
        return 'example_seed_only'
    if row['readiness'] == 'source_ready':
        return 'source_only'
    if row['readiness'] == 'doc_ready':
        return 'design_only'
    return 'no_witness'


def choose_preferred_seed(row: dict[str, object]) -> dict[str, object] | None:
    refs = [parse_witness_ref(ref) for ref in row['example_witnesses']]
    if not refs:
        return None
    preferred = None
    for rel_path, line in refs:
        if rel_path.startswith('examples/probes/'):
            preferred = (rel_path, line)
            break
    if preferred is None:
        preferred = refs[0]
    rel_path, line = preferred
    return {
        'path': rel_path,
        'line': line,
        'example_id': load_example_id(rel_path),
    }


def lift_hint(seed_mode: str, family: str) -> str:
    if seed_mode == 'probe_seed_ready':
        return 'lift the probe example into a dedicated external Rust regression test before expanding its assertion surface'
    if seed_mode == 'example_seed_only':
        if family == 'strategy_family':
            return 'wrap the nearby strategy example in a one-matchup probe example, then promote it into an external Rust test'
        return 'wrap the nearby world/strategy example in a one-matchup probe example before adding the external Rust test'
    if seed_mode == 'source_only':
        return 'encode the first explicit example seed, then promote it into an external Rust test'
    if seed_mode == 'design_only':
        return 'translate the design semantic into a concrete example seed before wiring a Rust test'
    return 'create the first explicit example seed and external Rust test anchor'


def build_index() -> dict[str, object]:
    report = build_queue()
    queue = report['priority_queue']
    entries: list[dict[str, object]] = []
    counts = {
        'probe_seed_ready': 0,
        'example_seed_only': 0,
        'source_only': 0,
        'design_only': 0,
        'no_witness': 0,
    }
    for row in queue:
        seed_mode = classify_seed_mode(row)
        counts[seed_mode] += 1
        preferred_seed = choose_preferred_seed(row)
        entries.append(
            {
                'family': row['family'],
                'variant': row['variant'],
                'status': row['status'],
                'readiness': row['readiness'],
                'seed_mode': seed_mode,
                'contract_count': row['contract_count'],
                'sample_contract_ids': list(row['sample_contract_ids']),
                'preferred_seed': preferred_seed,
                'example_witnesses': list(row['example_witnesses']),
                'lift_hint': lift_hint(seed_mode, str(row['family'])),
            }
        )

    entries.sort(
        key=lambda row: (
            {'probe_seed_ready': 0, 'example_seed_only': 1, 'source_only': 2, 'design_only': 3, 'no_witness': 4}[str(row['seed_mode'])],
            {'unseen': 0, 'inline_only': 1, 'sparse': 2}[str(row['status'])],
            str(row['family']),
            str(row['variant']),
        )
    )
    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_gap_probe_seed_index.v1',
            'crate': 'gr_engine',
            'source_report': 'artifacts/reports/rust_gap_witness_queue.json',
        },
        'summary': {
            'queue_entries': len(entries),
            **counts,
            'probe_seed_paths': sorted(
                {
                    entry['preferred_seed']['path']
                    for entry in entries
                    if entry['preferred_seed'] is not None and entry['seed_mode'] == 'probe_seed_ready'
                }
            ),
        },
        'entries': entries,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    entries = report['entries']
    lines = [
        '# Rust Gap Probe Seed Index',
        '',
        'Generated by `scripts/report/build_rust_gap_probe_seed_index.py`. This is the compact handoff index for blocked-Rust sessions that need self-contained probe examples, not just source mentions, for the current weak scenario rows.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- queue_entries: {summary['queue_entries']}",
        f"- probe_seed_ready: {summary['probe_seed_ready']}",
        f"- example_seed_only: {summary['example_seed_only']}",
        f"- source_only: {summary['source_only']}",
        f"- design_only: {summary['design_only']}",
        f"- no_witness: {summary['no_witness']}",
        '',
        '## Probe-seed queue',
        '',
        'Rows in `probe_seed_ready` already have a self-contained `examples/probes/*.json` anchor that a later Rust-capable inheritor can lift almost directly into an external regression test.',
        '',
        '| family | variant | status | seed mode | preferred seed | lift hint |',
        '|---|---|---|---|---|---|',
    ]
    for entry in entries:
        preferred_seed = entry['preferred_seed']
        if preferred_seed is None:
            seed_label = '—'
        else:
            rel_path = preferred_seed['path']
            example_id = preferred_seed.get('example_id') or 'no-id'
            seed_label = f"`{rel_path}` (`{example_id}`)"
        lines.append(
            f"| `{entry['family']}` | `{entry['variant']}` | `{entry['status']}` | `{entry['seed_mode']}` | {seed_label} | {entry['lift_hint']} |"
        )

    lines.extend(
        [
            '',
            '## Detailed entries',
            '',
        ]
    )

    for entry in entries:
        lines.extend(
            [
                f"### `{entry['family']}` / `{entry['variant']}`",
                '',
                f"- status: `{entry['status']}`",
                f"- readiness: `{entry['readiness']}`",
                f"- seed_mode: `{entry['seed_mode']}`",
                f"- contract_count: {entry['contract_count']}",
            ]
        )
        if entry['sample_contract_ids']:
            joined = ', '.join(f"`{item}`" for item in entry['sample_contract_ids'])
            lines.append(f"- sample_contract_ids: {joined}")
        else:
            lines.append('- sample_contract_ids: —')
        preferred_seed = entry['preferred_seed']
        if preferred_seed is None:
            lines.append('- preferred_seed: —')
        else:
            example_id = preferred_seed.get('example_id') or 'no-id'
            lines.append(
                f"- preferred_seed: `{preferred_seed['path']}` line {preferred_seed['line']} (`id={example_id}`)"
            )
        if entry['example_witnesses']:
            joined = ', '.join(f"`{item}`" for item in entry['example_witnesses'])
            lines.append(f"- example_witnesses: {joined}")
        else:
            lines.append('- example_witnesses: —')
        lines.append(f"- lift_hint: {entry['lift_hint']}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build a compact probe-seed index for weak Rust scenario rows.')
    parser.add_argument('--write', action='store_true', help='write outputs instead of diff-checking them')
    args = parser.parse_args(argv)

    report = build_index()
    md = render_markdown(report)
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'

    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'rust-gap-probe-seed-index: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-gap-probe-seed-index: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = []
    if not OUT_JSON.exists():
        missing.append(OUT_JSON.relative_to(ROOT).as_posix())
    if not OUT_MD.exists():
        missing.append(OUT_MD.relative_to(ROOT).as_posix())
    if missing:
        for path in missing:
            print(f'rust-gap-probe-seed-index: missing {path}', file=sys.stderr)
        return 1

    current_json = OUT_JSON.read_text(encoding='utf-8')
    current_md = OUT_MD.read_text(encoding='utf-8')
    if current_json != js or current_md != md:
        print('rust-gap-probe-seed-index: outputs are stale; run with --write', file=sys.stderr)
        return 1

    print(
        'rust-gap-probe-seed-index: ok '
        f"({report['summary']['queue_entries']} entries, {report['summary']['probe_seed_ready']} probe_seed_ready)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
