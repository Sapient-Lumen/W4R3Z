#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from build_rust_gap_probe_seed_index import build_index as build_probe_seed_index
from build_rust_gap_witness_queue import build_queue as build_gap_witness_queue

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'
OUT_MD = ROOT / 'docs' / 'RUST_EXTERNAL_TEST_QUEUE.md'

LANE_TARGET = {
    'probe_run': 'crates/gr_engine/tests/probe_run.rs',
    'metamorphic_suite': 'crates/gr_engine/tests/metamorphic_suite.rs',
}


def snake_to_camel(text: str) -> str:
    return ''.join(part.title() for part in text.split('_'))


def to_snake(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '_', text)
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned.lower()


def parse_ref(ref: str) -> tuple[str, int]:
    path, line = ref.rsplit(':', 1)
    return path, int(line)


def load_json(rel_path: str) -> object | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def lane_for_family(family: str) -> str:
    if family == 'metamorphic_kind':
        return 'metamorphic_suite'
    return 'probe_run'


def lift_band(status: str) -> str:
    if status == 'unseen':
        return 'lift_first'
    if status == 'inline_only':
        return 'externalize_now'
    return 'broaden_after_lift'


def wrapper_mode(family: str, seed_path: str | None) -> str:
    if family == 'metamorphic_kind':
        return 'wrap_probe_seed_in_metamorphic_check'
    if seed_path and seed_path.startswith('examples/probes/'):
        return 'load_probe_seed_directly'
    return 'translate_seed_then_load'


def loader_type(lane: str) -> str:
    if lane == 'metamorphic_suite':
        return 'ProbeSpec -> MetamorphicCheckSpec'
    return 'ProbeSpec'


def test_focus(family: str, variant: str) -> str:
    if family == 'assertion_kind':
        return f'deserialize the probe seed, run it, and assert the matchup-level {variant} result reports the expected pass/fail outcome'
    if family == 'noise_kind':
        return f'deserialize the probe seed, run it twice for determinism, and keep one explicit execution check for the {variant} noise surface'
    if family == 'reputation_kind':
        return f'deserialize the probe seed, run it successfully, and keep one explicit execution witness for the {variant} reputation model'
    if family == 'standing_update_rule':
        return f'deserialize the probe seed, run it successfully, and keep one explicit execution witness for the {variant} standing-update rule'
    if family == 'strategy_family':
        return f'deserialize the probe seed, run it successfully, and keep one dedicated external witness for the {variant} strategy family'
    if family == 'termination_kind':
        return f'deserialize the probe seed, run it, and assert the {variant} termination summary fields remain populated and coherent'
    if family == 'metamorphic_kind':
        return f'wrap the probe seed in a MetamorphicCheckSpec, run the suite, and assert the {variant} check survives as an external regression test'
    return f'deserialize the seed and keep one dedicated external Rust witness for the {variant} gap'


def recipe_steps(family: str, variant: str, seed_path: str | None) -> list[str]:
    include_hint = f'use `include_str!("../../{seed_path}")`' if seed_path else 'load the preferred seed fixture'
    if family == 'metamorphic_kind':
        return [
            f'{include_hint} and deserialize it as `ProbeSpec`',
            f'wrap that probe in a one-check `MetamorphicRegistrySpec` using `MetamorphicKind::{snake_to_camel(variant)}`',
            'run `run_metamorphic_suite` and keep the suite check id narrow and fixture-named',
            'assert the suite stays passing and deterministic under the lifted external test',
        ]
    final_assertion = 'assert the lifted test stays narrow, deterministic, and fixture-backed'
    if family == 'assertion_kind':
        final_assertion = f'assert the resulting matchup surfaces the intended `{variant}` outcome explicitly'
    elif family == 'termination_kind':
        final_assertion = 'assert the rounds summary fields stay populated and ordered coherently'
    elif family in {'noise_kind', 'reputation_kind', 'standing_update_rule', 'strategy_family'}:
        final_assertion = f'assert execution succeeds and the `{variant}` seam remains covered by an external test'
    return [
        f'{include_hint} and deserialize it as `ProbeSpec`',
        'run `run_probe` directly in a dedicated external test',
        final_assertion,
    ]


def proposed_test_name(variant: str, family: str, band: str) -> str:
    variant_part = to_snake(variant)
    family_part = to_snake(family)
    band_part = to_snake(band)
    return f'lift_{variant_part}_{family_part}_{band_part}_seed'


def cargo_hint(lane: str, test_name: str) -> str:
    target = 'probe_run' if lane == 'probe_run' else 'metamorphic_suite'
    return f'cargo test -p gr_engine --test {target} {test_name} -- --exact'


def build_queue() -> dict[str, object]:
    seed_report = build_probe_seed_index()
    witness_report = build_gap_witness_queue()
    witness_map = {
        (str(row['family']), str(row['variant'])): row
        for row in witness_report['priority_queue']
    }

    entries: list[dict[str, object]] = []
    lane_counts: dict[str, int] = {'probe_run': 0, 'metamorphic_suite': 0}
    band_counts: dict[str, int] = {'lift_first': 0, 'externalize_now': 0, 'broaden_after_lift': 0}
    wrapper_counts: dict[str, int] = {
        'load_probe_seed_directly': 0,
        'wrap_probe_seed_in_metamorphic_check': 0,
        'translate_seed_then_load': 0,
    }

    for seed_entry in seed_report['entries']:
        family = str(seed_entry['family'])
        variant = str(seed_entry['variant'])
        status = str(seed_entry['status'])
        preferred_seed = seed_entry.get('preferred_seed')
        seed_path = None if preferred_seed is None else str(preferred_seed['path'])
        witness_row = witness_map[(family, variant)]
        lane = lane_for_family(family)
        band = lift_band(status)
        wrapper = wrapper_mode(family, seed_path)
        test_name = proposed_test_name(variant, family, band)
        entry = {
            'family': family,
            'variant': variant,
            'status': status,
            'lift_band': band,
            'seed_mode': str(seed_entry['seed_mode']),
            'preferred_seed': preferred_seed,
            'loader_type': loader_type(lane),
            'wrapper_mode': wrapper,
            'target_lane': lane,
            'target_test_file': LANE_TARGET[lane],
            'proposed_test_name': test_name,
            'future_cargo_hint': cargo_hint(lane, test_name),
            'test_focus': test_focus(family, variant),
            'recipe_steps': recipe_steps(family, variant, seed_path),
            'sample_contract_ids': list(seed_entry['sample_contract_ids']),
            'rust_source_anchor': witness_row['rust_source_witnesses'][0] if witness_row['rust_source_witnesses'] else None,
            'rust_test_anchor': witness_row['rust_test_witnesses'][0] if witness_row['rust_test_witnesses'] else None,
            'command_hint': witness_row['command_hint'],
        }
        entries.append(entry)
        lane_counts[lane] += 1
        band_counts[band] += 1
        wrapper_counts[wrapper] += 1

    entries.sort(
        key=lambda row: (
            {'lift_first': 0, 'externalize_now': 1, 'broaden_after_lift': 2}[str(row['lift_band'])],
            {'probe_run': 0, 'metamorphic_suite': 1}[str(row['target_lane'])],
            str(row['family']),
            str(row['variant']),
        )
    )
    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_external_test_queue.v1',
            'crate': 'gr_engine',
            'source_reports': [
                'artifacts/reports/rust_gap_probe_seed_index.json',
                'artifacts/reports/rust_gap_witness_queue.json',
            ],
        },
        'summary': {
            'queue_entries': len(entries),
            'lane_counts': lane_counts,
            'lift_band_counts': band_counts,
            'wrapper_mode_counts': wrapper_counts,
            'fixture_backed_entries': sum(1 for entry in entries if entry['preferred_seed'] is not None),
        },
        'entries': entries,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    entries = report['entries']
    lines = [
        '# Rust External Test Queue',
        '',
        'Generated by `scripts/report/build_rust_external_test_queue.py`. This is the compact handoff queue that turns the weak-scenario seed surface into concrete first external Rust test placements for a later Rust-capable inheritor.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- queue_entries: {summary['queue_entries']}",
        f"- fixture_backed_entries: {summary['fixture_backed_entries']}",
        f"- probe_run entries: {summary['lane_counts']['probe_run']}",
        f"- metamorphic_suite entries: {summary['lane_counts']['metamorphic_suite']}",
        f"- lift_first: {summary['lift_band_counts']['lift_first']}",
        f"- externalize_now: {summary['lift_band_counts']['externalize_now']}",
        f"- broaden_after_lift: {summary['lift_band_counts']['broaden_after_lift']}",
        '',
        '## Queue',
        '',
        'Treat this as the first compiled comeback plan once `cargo` returns: each row names the seed to lift, the likely external test lane, and the narrow recipe that keeps the lifted test fixture-backed instead of re-invented from scratch.',
        '',
        '| family | variant | band | lane | target file | preferred seed | proposed test |',
        '|---|---|---|---|---|---|---|',
    ]
    for entry in entries:
        preferred_seed = entry['preferred_seed']
        seed_label = '—'
        if preferred_seed is not None:
            seed_label = f"`{preferred_seed['path']}`"
        lines.append(
            f"| `{entry['family']}` | `{entry['variant']}` | `{entry['lift_band']}` | `{entry['target_lane']}` | `{entry['target_test_file']}` | {seed_label} | `{entry['proposed_test_name']}` |"
        )

    lines.extend([
        '',
        '## Detailed entries',
        '',
    ])
    for entry in entries:
        lines.extend([
            f"### `{entry['family']}` / `{entry['variant']}`",
            '',
            f"- status: `{entry['status']}`",
            f"- lift_band: `{entry['lift_band']}`",
            f"- seed_mode: `{entry['seed_mode']}`",
            f"- target_lane: `{entry['target_lane']}`",
            f"- target_test_file: `{entry['target_test_file']}`",
            f"- proposed_test_name: `{entry['proposed_test_name']}`",
            f"- loader_type: `{entry['loader_type']}`",
            f"- wrapper_mode: `{entry['wrapper_mode']}`",
            f"- test_focus: {entry['test_focus']}",
        ])
        preferred_seed = entry['preferred_seed']
        if preferred_seed is None:
            lines.append('- preferred_seed: —')
        else:
            seed_id = preferred_seed.get('example_id') or 'no-id'
            lines.append(
                f"- preferred_seed: `{preferred_seed['path']}` line {preferred_seed['line']} (`id={seed_id}`)"
            )
        lines.append(f"- future_cargo_hint: `{entry['future_cargo_hint']}`")
        if entry['rust_source_anchor']:
            lines.append(f"- rust_source_anchor: `{entry['rust_source_anchor']}`")
        else:
            lines.append('- rust_source_anchor: —')
        if entry['rust_test_anchor']:
            lines.append(f"- rust_test_anchor: `{entry['rust_test_anchor']}`")
        else:
            lines.append('- rust_test_anchor: —')
        if entry['sample_contract_ids']:
            lines.append('- sample_contract_ids: ' + ', '.join(f"`{item}`" for item in entry['sample_contract_ids']))
        else:
            lines.append('- sample_contract_ids: —')
        lines.append(f"- command_hint: `{entry['command_hint']}`")
        lines.append('- recipe_steps:')
        for step in entry['recipe_steps']:
            lines.append(f'  - {step}')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build a compact external-test lift queue for weak Rust scenario rows.')
    parser.add_argument('--write', action='store_true', help='write outputs instead of diff-checking them')
    args = parser.parse_args(argv)

    report = build_queue()
    md = render_markdown(report)
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'

    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'rust-external-test-queue: wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'rust-external-test-queue: wrote {OUT_MD.relative_to(ROOT)}')
        return 0

    missing = []
    if not OUT_JSON.exists():
        missing.append(OUT_JSON.relative_to(ROOT).as_posix())
    if not OUT_MD.exists():
        missing.append(OUT_MD.relative_to(ROOT).as_posix())
    if missing:
        for path in missing:
            print(f'rust-external-test-queue: missing {path}', file=sys.stderr)
        return 1

    current_json = OUT_JSON.read_text(encoding='utf-8')
    current_md = OUT_MD.read_text(encoding='utf-8')
    if current_json != js or current_md != md:
        print('rust-external-test-queue: outputs are stale; run with --write', file=sys.stderr)
        return 1

    print(
        'rust-external-test-queue: ok '
        f"({report['summary']['queue_entries']} entries, {report['summary']['lane_counts']['probe_run']} probe_run lanes)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
