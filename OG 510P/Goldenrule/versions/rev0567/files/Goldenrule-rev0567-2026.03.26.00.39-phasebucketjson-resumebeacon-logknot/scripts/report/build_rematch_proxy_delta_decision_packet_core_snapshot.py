#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_core_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_core_snapshot_20260307.md'


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
            'why': 'the declaration-first coordinates packet exposes the cleanest minimal semantic seed: just `(B,H)` plus mode.',
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
            'why': 'the weight packet shows that even when evidence is larger, the archive can drop derived fields and deterministic result fields from the durable body.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'standalone_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'archive_local_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
            'why': 'adaptive black-box packets keep only the observed route in the semantic core, not the derived robustness label.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'even the justified escalation case can keep only the exact checked-cap signature as the long-lived body seed.',
        },
    ]
    for row in rows:
        standalone = row['standalone_packet']
        archive_local = row['archive_local_packet']
        semantic_core = packet.packet_semantic_core(standalone)
        compact_first_write = packet.packet_archive_compact_write_plan(standalone, [])
        compact_repeat_write = packet.packet_archive_compact_write_plan(semantic_core, [packet.packet_semantic_fingerprint(standalone)])
        human_first_write = packet.packet_archive_compact_write_plan(standalone, [], need_human_readable_packet=True)
        row['semantic_core_packet'] = semantic_core
        row['semantic_fingerprint'] = packet.packet_semantic_fingerprint(semantic_core)
        row['standalone_bytes'] = packet.packet_minified_bytes(standalone)
        row['archive_local_bytes'] = packet.packet_minified_bytes(archive_local)
        row['semantic_core_bytes'] = packet.packet_minified_bytes(semantic_core)
        row['reference_bytes'] = packet.packet_minified_bytes(packet.packet_reference(standalone))
        row['archive_local_to_core_bytes_saved'] = row['archive_local_bytes'] - row['semantic_core_bytes']
        row['standalone_to_core_bytes_saved'] = row['standalone_bytes'] - row['semantic_core_bytes']
        row['core_then_reference_bytes'] = row['semantic_core_bytes'] + row['reference_bytes']
        row['archive_local_then_reference_bytes'] = row['archive_local_bytes'] + row['reference_bytes']
        row['compact_first_write_plan'] = compact_first_write
        row['compact_repeat_write_plan'] = compact_repeat_write
        row['human_readable_first_write_plan'] = human_first_write
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_semantic_core_packet(row['semantic_core_packet']) != row['standalone_packet']:
            raise SystemExit(f"semantic-core standalone expansion mismatch for {row['name']}")
        if packet.expand_semantic_core_packet(row['semantic_core_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"semantic-core archive-local expansion mismatch for {row['name']}")
        if packet.expand_packet(row['semantic_core_packet']) != row['standalone_packet']:
            raise SystemExit(f"expand_packet semantic-core mismatch for {row['name']}")
        if row['archive_local_to_core_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive archive-local to semantic-core byte savings for {row['name']}")
        if row['compact_first_write_plan']['recommended_write_kind'] != 'semantic_core_body':
            raise SystemExit(f"expected semantic_core_body first write for {row['name']}")
        if row['compact_repeat_write_plan']['recommended_write_kind'] != 'reference':
            raise SystemExit(f"expected reference repeat write for {row['name']}")
        if row['human_readable_first_write_plan']['recommended_write_kind'] != 'archive_local_body':
            raise SystemExit(f"expected archive_local_body human-readable first write for {row['name']}")

    best = max(rows, key=lambda row: row['archive_local_to_core_bytes_saved'])
    machine_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
    )
    human_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=True,
        archive_has_core_expander=True,
    )
    portable = packet.packet_body_storage_decision(
        need_standalone_portability=True,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
    )

    return {
        'focus': 'Store one semantic core per new rematch decision, then reconstruct archive-local or standalone packets on demand, so even first writes avoid deterministic packet boilerplate.',
        'method_note': 'Loaded the executable decision-packet module, converted representative packets into semantic cores, verified lossless expansion back to both standalone and archive-local packet forms, and measured minified byte savings for first-write storage.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'semantic_core_kind': packet.SEMANTIC_CORE_KIND,
            'semantic_core_contract_version': packet.SEMANTIC_CORE_CONTRACT_VERSION,
            'default_machine_storage_form': machine_default['recommended_storage_form'],
            'default_human_readable_storage_form': human_default['recommended_storage_form'],
            'portable_storage_form': portable['recommended_storage_form'],
            'best_archive_local_to_core_savings_example': best['name'],
            'best_archive_local_to_core_bytes_saved': best['archive_local_to_core_bytes_saved'],
            'main_rule': 'for long-lived in-archive storage, keep one semantic core per fingerprint and materialize archive-local packets only when a directly readable packet view is needed',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Semantic-Core Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- semantic core kind: `{findings['semantic_core_kind']}`.",
        f"- semantic core contract version: `{findings['semantic_core_contract_version']}`.",
        f"- default machine-oriented in-archive storage form: `{findings['default_machine_storage_form']}`.",
        f"- default human-readable in-archive storage form: `{findings['default_human_readable_storage_form']}`.",
        f"- portable storage form: `{findings['portable_storage_form']}`.",
        f"- best measured archive-local to semantic-core saving: `{findings['best_archive_local_to_core_bytes_saved']}` bytes on `{findings['best_archive_local_to_core_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative first-write savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> standalone `{row['standalone_bytes']}` bytes, archive-local `{row['archive_local_bytes']}` bytes, semantic core `{row['semantic_core_bytes']}` bytes, reference `{row['reference_bytes']}` bytes; shrinking the first durable body from archive-local to semantic core saves `{row['archive_local_to_core_bytes_saved']}` bytes, and the compact first write stores `{row['compact_first_write_plan']['recommended_write_kind']}`. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- profile refs solved repeated provenance, and fingerprints solved repeat bodies; semantic cores now shrink the one body the archive still needs to keep for a new decision.',
        '- archive-local packets remain useful as a human-readable materialized view, but they no longer need to be the smallest durable object in the archive.',
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
