#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from build_rust_external_test_queue import build_queue

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_seed_loader_readiness.json'
OUT_MD = ROOT / 'docs' / 'RUST_SEED_LOADER_READINESS.md'


def load_json(path: str) -> object | None:
    full = ROOT / path
    if not full.exists():
        return None
    try:
        return json.loads(full.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def classify_probe_seed(path: str | None) -> dict[str, object]:
    if path is None:
        return {
            'loadability': 'missing_seed',
            'probe_id': None,
            'matchup_count': 0,
            'null_strategy_slots': 0,
        }
    payload = load_json(path)
    if not isinstance(payload, dict):
        return {
            'loadability': 'non_json_or_missing',
            'probe_id': None,
            'matchup_count': 0,
            'null_strategy_slots': 0,
        }
    probe_id = payload.get('id') if isinstance(payload.get('id'), str) else None
    if 'world' not in payload or 'matchups' not in payload:
        return {
            'loadability': 'not_probe_shape',
            'probe_id': probe_id,
            'matchup_count': 0,
            'null_strategy_slots': 0,
        }
    matchups = payload.get('matchups')
    if not isinstance(matchups, list) or not matchups:
        return {
            'loadability': 'not_probe_shape',
            'probe_id': probe_id,
            'matchup_count': 0,
            'null_strategy_slots': 0,
        }
    null_slots = 0
    for matchup in matchups:
        if not isinstance(matchup, dict):
            return {
                'loadability': 'not_probe_shape',
                'probe_id': probe_id,
                'matchup_count': len(matchups),
                'null_strategy_slots': null_slots,
            }
        for slot in ('strategy_a', 'strategy_b'):
            strategy = matchup.get(slot)
            if strategy is None:
                null_slots += 1
                continue
            if not isinstance(strategy, dict):
                return {
                    'loadability': 'not_probe_shape',
                    'probe_id': probe_id,
                    'matchup_count': len(matchups),
                    'null_strategy_slots': null_slots,
                }
    loadability = 'direct_probe_ready' if null_slots == 0 else 'probe_template_requires_fill'
    return {
        'loadability': loadability,
        'probe_id': probe_id,
        'matchup_count': len(matchups),
        'null_strategy_slots': null_slots,
    }


def wrapper_requires_direct_seed(wrapper_mode: str) -> bool:
    return wrapper_mode in {'load_probe_seed_directly', 'wrap_probe_seed_in_metamorphic_check'}


def action_for(loadability: str, wrapper_mode: str) -> str:
    if loadability == 'direct_probe_ready':
        if wrapper_mode == 'wrap_probe_seed_in_metamorphic_check':
            return 'safe to wrap directly in a one-check metamorphic registry'
        return 'safe to load directly as ProbeSpec in the external Rust test'
    if loadability == 'probe_template_requires_fill':
        return 'fill null strategy slots before treating this seed as a direct ProbeSpec fixture'
    if loadability == 'not_probe_shape':
        return 'translate the seed into a one-probe fixture before lifting it into an external Rust test'
    return 'replace or regenerate the preferred seed before lifting this queue row'


def build_report() -> dict[str, object]:
    queue = build_queue()
    entries: list[dict[str, object]] = []
    counts = {
        'direct_probe_ready': 0,
        'probe_template_requires_fill': 0,
        'not_probe_shape': 0,
        'non_json_or_missing': 0,
        'missing_seed': 0,
        'direct_wrapper_ok': 0,
        'direct_wrapper_mismatch': 0,
    }
    for row in queue['entries']:
        preferred = row.get('preferred_seed')
        seed_path = None if preferred is None else str(preferred['path'])
        seed_info = classify_probe_seed(seed_path)
        loadability = str(seed_info['loadability'])
        counts[loadability] += 1
        wrapper_mode = str(row['wrapper_mode'])
        requires_direct = wrapper_requires_direct_seed(wrapper_mode)
        wrapper_ok = (not requires_direct) or loadability == 'direct_probe_ready'
        counts['direct_wrapper_ok' if wrapper_ok else 'direct_wrapper_mismatch'] += 1
        entries.append({
            'family': row['family'],
            'variant': row['variant'],
            'target_lane': row['target_lane'],
            'lift_band': row['lift_band'],
            'wrapper_mode': wrapper_mode,
            'preferred_seed': preferred,
            'loadability': loadability,
            'probe_id': seed_info['probe_id'],
            'matchup_count': seed_info['matchup_count'],
            'null_strategy_slots': seed_info['null_strategy_slots'],
            'wrapper_ok': wrapper_ok,
            'action_hint': action_for(loadability, wrapper_mode),
        })
    entries.sort(key=lambda row: (0 if row['wrapper_ok'] else 1, 0 if row['loadability'] == 'direct_probe_ready' else 1, row['family'], row['variant']))
    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_seed_loader_readiness.v1',
            'source_report': 'artifacts/reports/rust_external_test_queue.json',
            'crate': 'gr_engine',
        },
        'summary': {
            'queue_entries': len(entries),
            **counts,
        },
        'entries': entries,
    }


def render_markdown(report: dict[str, object]) -> str:
    s = report['summary']
    lines = [
        '# Rust Seed Loader Readiness',
        '',
        'Generated by `scripts/report/build_rust_seed_loader_readiness.py`. This is the compact audit that checks whether the preferred seeds in the external Rust lift queue are directly loadable as `ProbeSpec` fixtures, instead of merely mentioning the right variant.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- queue_entries: {s['queue_entries']}",
        f"- direct_probe_ready: {s['direct_probe_ready']}",
        f"- probe_template_requires_fill: {s['probe_template_requires_fill']}",
        f"- not_probe_shape: {s['not_probe_shape']}",
        f"- non_json_or_missing: {s['non_json_or_missing']}",
        f"- missing_seed: {s['missing_seed']}",
        f"- direct_wrapper_ok: {s['direct_wrapper_ok']}",
        f"- direct_wrapper_mismatch: {s['direct_wrapper_mismatch']}",
        '',
        '## Queue seed audit',
        '',
        '| family | variant | wrapper | preferred seed | loadability | wrapper ok |',
        '|---|---|---|---|---|---|',
    ]
    for entry in report['entries']:
        preferred = entry['preferred_seed']
        seed_label = '—' if preferred is None else f"`{preferred['path']}`"
        lines.append(f"| `{entry['family']}` | `{entry['variant']}` | `{entry['wrapper_mode']}` | {seed_label} | `{entry['loadability']}` | `{str(entry['wrapper_ok']).lower()}` |")
    lines.extend(['', '## Detailed entries', ''])
    for entry in report['entries']:
        lines.extend([
            f"### `{entry['family']}` / `{entry['variant']}`",
            '',
            f"- target_lane: `{entry['target_lane']}`",
            f"- lift_band: `{entry['lift_band']}`",
            f"- wrapper_mode: `{entry['wrapper_mode']}`",
            f"- loadability: `{entry['loadability']}`",
            f"- wrapper_ok: `{str(entry['wrapper_ok']).lower()}`",
        ])
        preferred = entry['preferred_seed']
        if preferred is None:
            lines.append('- preferred_seed: —')
        else:
            lines.append(f"- preferred_seed: `{preferred['path']}` line {preferred['line']} (`id={preferred.get('example_id') or 'no-id'}`)")
        lines.append(f"- probe_id: `{entry['probe_id'] or '—'}`")
        lines.append(f"- matchup_count: {entry['matchup_count']}")
        lines.append(f"- null_strategy_slots: {entry['null_strategy_slots']}")
        lines.append(f"- action_hint: {entry['action_hint']}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Audit whether the preferred seeds in the Rust external-test queue are directly loadable.')
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
        print(f'rust-seed-loader-readiness: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-seed-loader-readiness: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = []
    if not OUT_JSON.exists():
        missing.append(OUT_JSON.relative_to(ROOT).as_posix())
    if not OUT_MD.exists():
        missing.append(OUT_MD.relative_to(ROOT).as_posix())
    if missing:
        for item in missing:
            print(f'rust-seed-loader-readiness: missing {item}', file=sys.stderr)
        return 1

    if OUT_JSON.read_text(encoding='utf-8') != js or OUT_MD.read_text(encoding='utf-8') != md:
        print('rust-seed-loader-readiness: outputs are stale; run with --write', file=sys.stderr)
        return 1

    print('rust-seed-loader-readiness: ok ' f"({report['summary']['queue_entries']} entries, {report['summary']['direct_probe_ready']} direct_probe_ready)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
