#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _weight_samples(packet) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for key in packet.WEIGHT_KEYS:
        for value in ['1', '0.5', '2', '0.2', '0.0001', '3.14']:
            weights = {name: '0' for name in packet.WEIGHT_KEYS}
            weights[key] = value
            samples.append(weights)
    for value in ['1', '0.5', '2', '0.2', '0.0001', '3.14']:
        samples.append({key: value for key in packet.WEIGHT_KEYS})
    for split in range(1, len(packet.WEIGHT_KEYS)):
        samples.append(
            {
                key: ('1' if index < split else '0.5')
                for index, key in enumerate(packet.WEIGHT_KEYS)
            }
        )
    rng = random.Random(0)
    scalar_choices = ['0', '1', '0.5', '2', '0.2', '0.0001', '3.14']
    for _ in range(128):
        samples.append({key: rng.choice(scalar_choices) for key in packet.WEIGHT_KEYS})

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for weights in samples:
        signature = tuple(weights[key] for key in packet.WEIGHT_KEYS)
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(weights)
    return unique


def _frontier_test_packets(packet) -> list[dict[str, object]]:
    packets: list[dict[str, object]] = []
    scalar_values = ['0', '1', '0.5', '2', '0.2', '0.0001', '0.000000', '3.14']
    for B in scalar_values:
        for H in scalar_values:
            packets.append(
                {
                    'name': f'coordinates_{B}_{H}',
                    'packet': packet.packet_from_coordinates(B, H),
                }
            )
    for signature in ['MM', 'SM', 'SS']:
        packets.append(
            {
                'name': f'robustness_fixed_{signature}',
                'packet': packet.packet_from_robustness_fixed(*signature),
            }
        )
    for args in [(10, 'M', None), (10, 'S', 'M'), (10, 'S', 'S'), (20, 'S', None), (20, 'M', 'M'), (20, 'M', 'S')]:
        label = 'adaptive_' + '_'.join('none' if value is None else str(value) for value in args)
        packets.append({'name': label, 'packet': packet.packet_from_robustness_adaptive(*args)})
    for args in [('M', 'M'), ('M', 'S'), ('S', 'M'), ('S', 'S')]:
        label = 'strict_' + ''.join(args)
        packets.append({'name': label, 'packet': packet.packet_from_strict_adaptive(*args)})
    for signature in ['MMM', 'SMM', 'SMS', 'SSS', 'TMM', 'SMT', 'STS', 'TTT']:
        packets.append(
            {
                'name': f'exact_checked_cap_{signature}',
                'packet': packet.packet_from_exact_checked_cap_path(*signature),
            }
        )
    for index, weights in enumerate(_weight_samples(packet), start=1):
        packets.append({'name': f'weights_case_{index:03d}', 'packet': packet.packet_from_weights(weights)})

    unique: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in packets:
        fingerprint = packet.packet_semantic_fingerprint(row['packet'])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        unique.append(row)
    return unique


def _sample_rows(packet):
    rows = [
        {
            'name': 'oracle_weights_width_one_exception',
            'standalone_packet': packet.packet_from_weights(
                {
                    'w_width': '1',
                    'w_buffer': '0',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '0',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '0',
                }
            ),
            'why': 'the width-only all-atom weight seed is the smallest known counterexample to the old byteframe-always-wins ladder: the packed array `[1,1,0]` is only 7 minified bytes, while the byteframe string takes 8.',
        },
        {
            'name': 'oracle_weights_hazard_one_byteframe_win',
            'standalone_packet': packet.packet_from_weights(
                {
                    'w_width': '0',
                    'w_buffer': '0',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '0',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '1',
                }
            ),
            'why': 'the hazard-only one-hot case still favors byteframes because the packed JSON array has to spell the high-bit mask as `128`, while the byteframe carries the same bytes more compactly.',
        },
        {
            'name': 'oracle_coordinates_sms_byteframe_win',
            'standalone_packet': packet.packet_from_coordinates('0.0001', '1'),
            'why': 'coordinate packets still benefit from removing numeric-array wrapper bytes once both scalar values have already collapsed to atoms.',
        },
        {
            'name': 'exact_checked_cap_path_tie20_byteframe_win',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'why': 'the exact checked-cap tie path shows that the byteframe still wins on the finite non-weight black-box payloads, so the measured override is narrow rather than a rollback of the byteframe tier.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        archive_local = packet.expand_packet(standalone)
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        body_frontier = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        repeat_frontier = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        packed_seed = packet.packet_packed_seed(standalone)
        byte_seed = packet.packet_byte_seed(standalone)
        packed_reference = packet.packet_packed_reference(standalone, known_fingerprints)
        byte_reference = packet.packet_byte_reference(standalone, known_fingerprints)
        row.update(
            {
                'archive_local_packet': packet._archive_localize_packet(archive_local),
                'semantic_fingerprint': fingerprint,
                'packed_seed_packet': packed_seed,
                'byte_seed_packet': byte_seed,
                'packed_reference_packet': packed_reference,
                'byte_reference_packet': byte_reference,
                'packed_seed_bytes': packet.packet_minified_bytes(packed_seed),
                'byte_seed_bytes': packet.packet_minified_bytes(byte_seed),
                'packed_reference_bytes': packet.packet_minified_bytes(packed_reference),
                'byte_reference_bytes': packet.packet_minified_bytes(byte_reference),
                'body_frontier': body_frontier,
                'repeat_frontier': repeat_frontier,
                'zepto_first_write_plan': packet.packet_archive_zepto_write_plan(standalone, []),
                'zepto_repeat_write_plan': packet.packet_archive_zepto_write_plan(standalone, known_fingerprints),
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    sample_rows = _sample_rows(packet)
    test_packets = _frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in test_packets]

    body_winner_counts: dict[str, int] = {}
    repeat_winner_counts: dict[str, int] = {}
    override_rows: list[dict[str, object]] = []
    repeat_override_rows: list[dict[str, object]] = []
    max_override = None

    for row in test_packets:
        standalone = row['packet']
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        frontier = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        repeat_frontier = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        body_winner_counts[frontier['recommended_storage_form']] = body_winner_counts.get(frontier['recommended_storage_form'], 0) + 1
        repeat_winner_counts[repeat_frontier['recommended_storage_form']] = repeat_winner_counts.get(repeat_frontier['recommended_storage_form'], 0) + 1
        if frontier['recommended_storage_form'] != frontier['default_storage_form']:
            override_row = {
                'name': row['name'],
                'mode': standalone['mode'],
                'semantic_fingerprint': fingerprint,
                'recommended_storage_form': frontier['recommended_storage_form'],
                'default_storage_form': frontier['default_storage_form'],
                'bytes_saved_vs_default': frontier['bytes_saved_vs_default'],
                'candidate_minified_bytes': frontier['candidate_minified_bytes'],
            }
            override_rows.append(override_row)
            if max_override is None or override_row['bytes_saved_vs_default'] > max_override['bytes_saved_vs_default']:
                max_override = override_row
        if repeat_frontier['recommended_storage_form'] != repeat_frontier['default_storage_form']:
            repeat_override_rows.append(
                {
                    'name': row['name'],
                    'mode': standalone['mode'],
                    'semantic_fingerprint': fingerprint,
                    'recommended_storage_form': repeat_frontier['recommended_storage_form'],
                    'default_storage_form': repeat_frontier['default_storage_form'],
                    'bytes_saved_vs_default': repeat_frontier['bytes_saved_vs_default'],
                    'candidate_minified_bytes': repeat_frontier['candidate_minified_bytes'],
                }
            )

    if max_override is None:
        raise SystemExit('expected at least one body-frontier override example')

    for row in sample_rows:
        if packet.expand_packed_seed_packet(row['packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"packed-seed expansion mismatch for {row['name']}")
        if packet.expand_byte_seed_packet(row['byte_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"byte-seed expansion mismatch for {row['name']}")
        if packet.resolve_archive_any_reference(row['byte_reference_packet'], known_fingerprints=[row['semantic_fingerprint']]) != row['semantic_fingerprint']:
            raise SystemExit(f"byte-reference resolution mismatch for {row['name']}")
        if row['repeat_frontier']['recommended_storage_form'] != 'byte_reference':
            raise SystemExit(f"expected byte_reference repeat frontier for {row['name']}")

    return {
        'focus': 'Replace the last hardcoded assumption in the local storage ladder with a measured payload-level frontier: choose whichever enabled codec actually minimizes minified bytes for the specific packet instead of assuming byteframes always beat packed seeds.',
        'method_note': 'Loaded the executable decision-packet module, generated a deterministic mixed packet set spanning coordinates, all supported black-box routes/signatures, and a broad weight sample, computed the full first-write and repeat-write candidate frontiers under the current archive codec set, and compared the coarse ladder defaults against the measured minima.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'tested_packet_count': len(test_packets),
            'coarse_default_first_write_storage_form_with_byteframe_codec': packet.packet_body_storage_decision(
                need_standalone_portability=False,
                need_human_readable_packet=False,
                archive_has_core_expander=True,
                archive_has_seed_codebook=True,
                archive_has_seed_microframe_codec=True,
                archive_has_seed_packed_codec=True,
                archive_has_seed_byteframe_codec=True,
            )['recommended_storage_form'],
            'measured_first_write_winner_counts': body_winner_counts,
            'packets_where_measured_frontier_overrides_coarse_default': len(override_rows),
            'modes_with_measured_overrides': sorted({row['mode'] for row in override_rows}),
            'largest_bytes_saved_vs_coarse_default': max_override['bytes_saved_vs_default'],
            'largest_savings_example': max_override['name'],
            'coarse_default_repeat_storage_form_with_byteframe_codec': packet.packet_repeat_storage_decision(
                need_standalone_portability=False,
                archive_has_reference_codebook=True,
                archive_has_reference_microframe_codec=True,
                archive_has_reference_packed_codec=True,
                archive_has_reference_byteframe_codec=True,
            )['recommended_storage_form'],
            'measured_repeat_winner_counts': repeat_winner_counts,
            'repeat_frontier_override_count': len(repeat_override_rows),
            'main_rule': 'treat the ladder as a capability prior, but choose the first-write and repeat-write codec by measured minified bytes for the specific packet; under the current codec stack, the only observed first-write exceptions are tiny oracle-weight packets where packed_seed beats byte_seed by one byte.',
        },
        'sample_packet_rows': sample_rows,
        'frontier_override_examples': override_rows[:8],
        'repeat_frontier_override_examples': repeat_override_rows[:8],
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Frontier Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- tested packet count: `{findings['tested_packet_count']}`.",
        f"- coarse first-write default with the byteframe codec: `{findings['coarse_default_first_write_storage_form_with_byteframe_codec']}`.",
        f"- measured first-write winners: `{json.dumps(findings['measured_first_write_winner_counts'], sort_keys=True)}`.",
        f"- measured first-write overrides of the coarse default: `{findings['packets_where_measured_frontier_overrides_coarse_default']}` packets across modes `{', '.join(findings['modes_with_measured_overrides'])}`.",
        f"- largest measured first-write saving versus the coarse default: `{findings['largest_bytes_saved_vs_coarse_default']}` byte on `{findings['largest_savings_example']}`.",
        f"- coarse repeat default with the byteframe codec: `{findings['coarse_default_repeat_storage_form_with_byteframe_codec']}`.",
        f"- measured repeat winners: `{json.dumps(findings['measured_repeat_winner_counts'], sort_keys=True)}`.",
        f"- measured repeat overrides of the coarse default: `{findings['repeat_frontier_override_count']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative frontier cases',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> packed seed `{row['packed_seed_bytes']}` bytes, byte seed `{row['byte_seed_bytes']}` bytes, packed reference `{row['packed_reference_bytes']}` bytes, byte reference `{row['byte_reference_bytes']}` bytes; first-write frontier picks `{row['body_frontier']['recommended_storage_form']}` and repeat frontier picks `{row['repeat_frontier']['recommended_storage_form']}`. {row['why']}"
        )
    lines.extend([
        '',
        '## Measured override examples',
    ])
    if summary['frontier_override_examples']:
        for row in summary['frontier_override_examples']:
            lines.append(
                f"- `{row['name']}` (`{row['mode']}`) -> coarse default `{row['default_storage_form']}`, measured winner `{row['recommended_storage_form']}`, bytes saved `{row['bytes_saved_vs_default']}`, candidate sizes `{json.dumps(row['candidate_minified_bytes'], sort_keys=True)}`."
            )
    else:
        lines.append('- none.')
    lines.extend([
        '',
        '## Sources',
    ])
    for source in summary['sources']:
        lines.append(f'- `{source}`')
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    summary = _build_summary()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary) + '\n', encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
