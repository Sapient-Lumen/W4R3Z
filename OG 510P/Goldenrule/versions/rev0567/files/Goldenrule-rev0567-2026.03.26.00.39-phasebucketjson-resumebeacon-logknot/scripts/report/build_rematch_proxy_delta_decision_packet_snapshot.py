#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def build_report() -> dict[str, Any]:
    packet = _load_packet_module()

    route_rows = [
        {
            'question_scope': 'robustness_only',
            'available_interface': 'projective_coordinates',
            **packet.recommend_minimal_packet_mode(question_scope='robustness_only', available_interface='projective_coordinates'),
        },
        {
            'question_scope': 'strict_class_only',
            'available_interface': 'weights',
            **packet.recommend_minimal_packet_mode(question_scope='strict_class_only', available_interface='weights'),
        },
        {
            'question_scope': 'robustness_only',
            'available_interface': 'black_box',
            'need_portable_nonprocedural_record': False,
            **packet.recommend_minimal_packet_mode(question_scope='robustness_only', available_interface='black_box'),
        },
        {
            'question_scope': 'robustness_only',
            'available_interface': 'black_box',
            'need_portable_nonprocedural_record': True,
            **packet.recommend_minimal_packet_mode(
                question_scope='robustness_only',
                available_interface='black_box',
                need_portable_nonprocedural_record=True,
            ),
        },
        {
            'question_scope': 'strict_class_only',
            'available_interface': 'black_box',
            **packet.recommend_minimal_packet_mode(question_scope='strict_class_only', available_interface='black_box'),
        },
        {
            'question_scope': 'exact_tie_cap',
            'available_interface': 'black_box',
            **packet.recommend_minimal_packet_mode(question_scope='exact_tie_cap', available_interface='black_box'),
        },
    ]

    sample_packets = {
        'oracle_coordinates_sms': packet.packet_from_coordinates('0.0001', '1'),
        'oracle_weights_smm': packet.packet_from_weights(
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
        'robustness_adaptive_early_stop_material': packet.packet_from_robustness_adaptive(10, 'M'),
        'robustness_fixed_cap_sensitive': packet.packet_from_robustness_fixed('S', 'M'),
        'strict_adaptive_sms': packet.packet_from_strict_adaptive('S', 'M'),
        'exact_checked_cap_path_tie20': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
    }

    sample_rows = []
    for name, packet_payload in sample_packets.items():
        sample_rows.append(
            {
                'name': name,
                'mode': packet_payload['mode'],
                'question_scope': packet_payload['question_scope'],
                'minified_bytes': packet.packet_minified_bytes(packet_payload),
                'result': packet_payload['result'],
                'packet': packet_payload,
            }
        )

    size_map = {row['name']: row['minified_bytes'] for row in sample_rows}

    report = {
        'focus': 'Turn the rematch-proxy decision logic into minimal archive packets so future inheritors can store only the smallest evidence object that answers the actual question.',
        'method_note': 'Started from the executable decision oracle, the question-targeted probe routing contract, the robustness early-stop trees, and the adaptive strict classifier. Encoded one compact packet surface per evidence mode, then compared which packet is minimal for each interface/question pair and how large representative packets are when minified for storage.',
        'headline_findings': {
            'packet_script': 'scripts/analysis/rematch_proxy_delta_decision_packet.py',
            'supported_packet_modes': [
                'oracle_coordinates',
                'oracle_weights',
                'probe_robustness_fixed',
                'probe_robustness_adaptive',
                'probe_strict_adaptive',
                'probe_exact_checked_cap_path',
            ],
            'direct_interfaces_dominate_black_box_when_available': True,
            'leanest_direct_packet_mode': 'oracle_coordinates',
            'leanest_direct_packet_reason': 'if declarations already exist elsewhere, storing (B,H) is smaller than duplicating the full weight vector while still answering every supported question with zero probes',
            'black_box_minimal_mode_for_robustness_when_streaming_routes_are_allowed': 'probe_robustness_adaptive',
            'black_box_minimal_mode_for_robustness_when_portable_fixed_signatures_are_required': 'probe_robustness_fixed',
            'black_box_minimal_mode_for_open_strict_classification': 'probe_strict_adaptive',
            'black_box_minimal_mode_for_exact_tie_cap_or_full_checked_cap_path': 'probe_exact_checked_cap_path',
            'most_archive_friendly_rule': 'store the smallest packet matched to the interface and question; do not archive supersets such as three-cap exact-path packets when direct coordinates or smaller black-box packets already answer the handoff question',
            'representative_minified_packet_sizes': size_map,
            'size_ordering_examples': {
                'oracle_coordinates_lt_oracle_weights': size_map['oracle_coordinates_sms'] < size_map['oracle_weights_smm'],
                'robustness_adaptive_early_stop_lte_robustness_fixed': size_map['robustness_adaptive_early_stop_material'] <= size_map['robustness_fixed_cap_sensitive'],
                'strict_adaptive_lt_exact_checked_cap_path': size_map['strict_adaptive_sms'] < size_map['exact_checked_cap_path_tie20'],
            },
        },
        'route_rows': route_rows,
        'sample_packet_rows': sample_rows,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_oracle_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_robustness_probe_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_decision_packet_snapshot.py',
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    lines = [
        '# Rematch-Proxy Decision Packet Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['headline_findings']['packet_script']}`.",
        f"- supported packet modes: `{report['headline_findings']['supported_packet_modes']}`.",
        f"- leanest direct packet mode: `{report['headline_findings']['leanest_direct_packet_mode']}`.",
        f"- black-box robustness mode (streaming/adaptive): `{report['headline_findings']['black_box_minimal_mode_for_robustness_when_streaming_routes_are_allowed']}`.",
        f"- black-box robustness mode (portable fixed signature): `{report['headline_findings']['black_box_minimal_mode_for_robustness_when_portable_fixed_signatures_are_required']}`.",
        f"- black-box open strict-class mode: `{report['headline_findings']['black_box_minimal_mode_for_open_strict_classification']}`.",
        f"- black-box exact-path / tie-cap mode: `{report['headline_findings']['black_box_minimal_mode_for_exact_tie_cap_or_full_checked_cap_path']}`.",
        f"- archive rule: {report['headline_findings']['most_archive_friendly_rule']}.",
        '',
        '## Representative minified packet sizes',
    ]
    for name, size in report['headline_findings']['representative_minified_packet_sizes'].items():
        lines.append(f'- `{name}` -> `{size}` bytes.')
    lines.extend(['', '## Minimal routing table'])
    for row in report['route_rows']:
        lines.append(
            f"- question `{row['question_scope']}`, interface `{row['available_interface']}`"
            + (f", portable fixed record `{row['need_portable_nonprocedural_record']}`" if 'need_portable_nonprocedural_record' in row else '')
            + f" -> `{row['recommended_mode']}` ({row['why']})."
        )
    lines.extend(['', '## Sample packets'])
    for row in report['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` / mode `{row['mode']}` / `{row['minified_bytes']}` bytes -> result `{_json_text(row['result'])}`."
        )
    lines.extend([
        '',
        '## Why this matters',
        '- direct coordinates now have an explicit compact packet form, so sessions that already cite a declaration do not need to duplicate the full weight vector or archive extra probe traces.',
        '- black-box diagnosis now has separate packet forms for robustness-only, open strict-class, and exact tie-cap/path questions, which keeps the archive from storing more probe symbols than the question actually needs.',
        '',
        '## Sources',
    ])
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
