#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_snapshot_20260307.json'
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    report = _load_json(REPORT_PATH)
    packet = _load_packet_module()

    assert report['focus'] == (
        'Turn the rematch-proxy decision logic into minimal archive packets so future inheritors can store only the smallest evidence object that answers the actual question.'
    )
    findings = report['headline_findings']
    assert findings['packet_script'] == 'scripts/analysis/rematch_proxy_delta_decision_packet.py'
    assert findings['supported_packet_modes'] == [
        'oracle_coordinates',
        'oracle_weights',
        'probe_robustness_fixed',
        'probe_robustness_adaptive',
        'probe_strict_adaptive',
        'probe_exact_checked_cap_path',
    ]
    assert findings['direct_interfaces_dominate_black_box_when_available'] is True
    assert findings['leanest_direct_packet_mode'] == 'oracle_coordinates'
    assert findings['black_box_minimal_mode_for_robustness_when_streaming_routes_are_allowed'] == 'probe_robustness_adaptive'
    assert findings['black_box_minimal_mode_for_robustness_when_portable_fixed_signatures_are_required'] == 'probe_robustness_fixed'
    assert findings['black_box_minimal_mode_for_open_strict_classification'] == 'probe_strict_adaptive'
    assert findings['black_box_minimal_mode_for_exact_tie_cap_or_full_checked_cap_path'] == 'probe_exact_checked_cap_path'
    assert findings['most_archive_friendly_rule'] == (
        'store the smallest packet matched to the interface and question; do not archive supersets such as three-cap exact-path packets when direct coordinates or smaller black-box packets already answer the handoff question'
    )

    route_rows = report['route_rows']
    assert route_rows == [
        {
            'question_scope': 'robustness_only',
            'available_interface': 'projective_coordinates',
            'recommended_mode': 'oracle_coordinates',
            'why': 'direct (B,H) coordinates answer every supported question with zero probes',
        },
        {
            'question_scope': 'strict_class_only',
            'available_interface': 'weights',
            'recommended_mode': 'oracle_weights',
            'why': 'declared weights answer every supported question with zero probes',
        },
        {
            'question_scope': 'robustness_only',
            'available_interface': 'black_box',
            'need_portable_nonprocedural_record': False,
            'recommended_mode': 'probe_robustness_adaptive',
            'why': 'robustness-only black-box diagnosis can stop after one probe in the robust cases and otherwise needs only one follow-up probe',
        },
        {
            'question_scope': 'robustness_only',
            'available_interface': 'black_box',
            'need_portable_nonprocedural_record': True,
            'recommended_mode': 'probe_robustness_fixed',
            'why': 'portable nonprocedural storage should record the exact [10,20] signature for universal robustness triage',
        },
        {
            'question_scope': 'strict_class_only',
            'available_interface': 'black_box',
            'recommended_mode': 'probe_strict_adaptive',
            'why': 'strict class separation needs only the adaptive 10000 -> (10 after M, 20 after S) tree when ties do not need to be recorded',
        },
        {
            'question_scope': 'exact_tie_cap',
            'available_interface': 'black_box',
            'recommended_mode': 'probe_exact_checked_cap_path',
            'why': 'exact checked-cap paths and tie-cap identification require the full fixed signature on [10,20,10000]',
        },
    ]

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    assert packet.packet_from_coordinates('0.0001', '1') == sample_rows['oracle_coordinates_sms']['packet']
    assert packet.packet_from_weights(
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
    ) == sample_rows['oracle_weights_smm']['packet']
    assert packet.packet_from_robustness_adaptive(10, 'M') == sample_rows['robustness_adaptive_early_stop_material']['packet']
    assert packet.packet_from_robustness_fixed('S', 'M') == sample_rows['robustness_fixed_cap_sensitive']['packet']
    assert packet.packet_from_strict_adaptive('S', 'M') == sample_rows['strict_adaptive_sms']['packet']
    assert packet.packet_from_exact_checked_cap_path('S', 'T', 'S') == sample_rows['exact_checked_cap_path_tie20']['packet']

    sizes = findings['representative_minified_packet_sizes']
    assert sizes['oracle_coordinates_sms'] == packet.packet_minified_bytes(sample_rows['oracle_coordinates_sms']['packet'])
    assert sizes['oracle_weights_smm'] == packet.packet_minified_bytes(sample_rows['oracle_weights_smm']['packet'])
    assert sizes['strict_adaptive_sms'] == packet.packet_minified_bytes(sample_rows['strict_adaptive_sms']['packet'])
    assert sizes['exact_checked_cap_path_tie20'] == packet.packet_minified_bytes(sample_rows['exact_checked_cap_path_tie20']['packet'])
    assert sizes['oracle_coordinates_sms'] < sizes['oracle_weights_smm']
    assert sizes['strict_adaptive_sms'] < sizes['exact_checked_cap_path_tie20']
    assert sizes['robustness_adaptive_early_stop_material'] <= sizes['robustness_fixed_cap_sensitive']

    tie20 = packet.packet_from_exact_checked_cap_path('S', 'T', 'S')
    assert tie20['result']['closure_label'] == 'TIE_tau20'
    assert tie20['result']['strict_path_class'] is None
    assert tie20['result']['robustness_class'] == 'boundary_tie_at_cap_20'

    recommendation = packet.recommend_minimal_packet_mode(question_scope='exact_tie_cap', available_interface='black_box')
    assert recommendation == {
        'recommended_mode': 'probe_exact_checked_cap_path',
        'why': 'exact checked-cap paths and tie-cap identification require the full fixed signature on [10,20,10000]',
    }

    print('decision-packets: ok')


if __name__ == '__main__':
    main()
