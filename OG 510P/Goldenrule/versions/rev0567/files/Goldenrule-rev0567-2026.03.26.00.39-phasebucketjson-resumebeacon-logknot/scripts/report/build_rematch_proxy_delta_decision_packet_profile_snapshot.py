#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_profile_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_profile_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sample_rows(packet):
    rows = [
        {
            'name': 'oracle_coordinates_sms',
            'standalone_packet': packet.packet_from_coordinates('0.0001', '1'),
            'archive_local_packet': packet.packet_from_coordinates('0.0001', '1', archive_local=True),
            'why': 'leanest declaration-first packet; ideal for long-lived archive storage when the shared profile registry is already present',
        },
        {
            'name': 'oracle_weights_smm',
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
            'archive_local_packet': packet.packet_from_weights(
                {
                    'w_width': '0',
                    'w_buffer': '0',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '0',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '1',
                },
                archive_local=True,
            ),
            'why': 'the weight packet repeats the same provenance but also carries a larger evidence block, so the profile-ref savings are still substantial',
        },
        {
            'name': 'strict_adaptive_sms',
            'standalone_packet': packet.packet_from_strict_adaptive('S', 'M'),
            'archive_local_packet': packet.packet_from_strict_adaptive('S', 'M', archive_local=True),
            'why': 'the open strict-class packet is already compact, so it exposes the pure provenance overhead most clearly',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'tie-cap packets are the justified escalation case; the profile ref keeps even this larger boundary packet tighter inside the archive',
        },
    ]
    for row in rows:
        row['standalone_bytes'] = packet.packet_minified_bytes(row['standalone_packet'])
        row['archive_local_bytes'] = packet.packet_minified_bytes(row['archive_local_packet'])
        row['bytes_saved'] = row['standalone_bytes'] - row['archive_local_bytes']
        row['fraction_saved'] = round(row['bytes_saved'] / row['standalone_bytes'], 6)
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    profile_registry = packet.archive_local_profile_registry()
    rows = _sample_rows(packet)

    if list(profile_registry) != [packet.ARCHIVE_LOCAL_PROFILE_REF]:
        raise SystemExit('unexpected archive-local profile registry contents')
    for row in rows:
        expanded = packet.expand_archive_local_packet(row['archive_local_packet'])
        if expanded != row['standalone_packet']:
            raise SystemExit(f"archive-local round-trip mismatch for {row['name']}")
        if row['bytes_saved'] <= 0:
            raise SystemExit(f"expected positive byte savings for {row['name']}")

    best = max(rows, key=lambda row: row['fraction_saved'])
    storage_rule_local = packet.packet_storage_decision(need_standalone_portability=False)
    storage_rule_portable = packet.packet_storage_decision(need_standalone_portability=True)

    return {
        'focus': 'Replace repeated per-packet provenance with a shared archive-local citation profile so decision packets stay reconstructable without paying the full provenance byte cost every time.',
        'method_note': 'Loaded the executable decision-packet module, generated representative standalone and archive-local packets, verified archive-local round-trip expansion back to the canonical standalone form, and measured minified byte savings.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'archive_local_packet_kind': packet.ARCHIVE_LOCAL_PACKET_KIND,
            'standalone_packet_kind': packet.PACKET_KIND,
            'archive_local_profile_ref': packet.ARCHIVE_LOCAL_PROFILE_REF,
            'profile_registry_size': len(profile_registry),
            'default_in_archive_storage_form': storage_rule_local['recommended_storage_form'],
            'portable_storage_form': storage_rule_portable['recommended_storage_form'],
            'best_fraction_saved_example': best['name'],
            'best_fraction_saved': best['fraction_saved'],
            'shared_profile_replaces_repeated_fields': ['contract_version', 'checked_caps', 'oracle_script', 'decision_oracle_snapshot', 'question_targeted_probe_snapshot'],
            'main_rule': 'inside this archive, store archive-local packets by default and expand to standalone packets only when the packet must travel without the profile registry',
        },
        'profile_registry': profile_registry,
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Profile Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- archive-local packet kind: `{findings['archive_local_packet_kind']}`.",
        f"- shared profile ref: `{findings['archive_local_profile_ref']}`.",
        f"- default in-archive storage form: `{findings['default_in_archive_storage_form']}`.",
        f"- portable storage form: `{findings['portable_storage_form']}`.",
        f"- best measured byte-savings fraction: `{findings['best_fraction_saved']}` on `{findings['best_fraction_saved_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Shared archive-local profile',
    ]
    for ref, profile in summary['profile_registry'].items():
        lines.append(f"- `{ref}` -> `{json.dumps(profile, sort_keys=True)}`.")
    lines.extend([
        '',
        '## Representative byte savings',
    ])
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> standalone `{row['standalone_bytes']}` bytes, archive-local `{row['archive_local_bytes']}` bytes, saved `{row['bytes_saved']}` bytes (`{row['fraction_saved']}`); {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- the packet layer is now aligned with the archive policy of citing shared evidence instead of repeating the same provenance block in every stored decision object.',
        '- inheritors can still reconstruct a portable standalone packet exactly, but the archive no longer pays that byte cost until portability is actually required.',
        '',
        '## Sources',
    ])
    for src in summary['sources']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()
