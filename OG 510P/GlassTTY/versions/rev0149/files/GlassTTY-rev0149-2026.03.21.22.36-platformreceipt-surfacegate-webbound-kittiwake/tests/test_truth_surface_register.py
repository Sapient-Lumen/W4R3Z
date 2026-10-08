from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('truth_surface_register', ROOT / 'scripts' / 'truth_surface_register.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_truth_surface_register = MODULE.build_truth_surface_register
capture_truth_surface_register = MODULE.capture_truth_surface_register


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_truth_surface_register_flags_foreign_root_and_tracks_citation_heads(tmp_path: Path) -> None:
    root = tmp_path
    # opening surface current-root + valid
    opening_dir = root / 'validation' / 'latest' / 'opening-surface-capture'
    _write_json(opening_dir / 'opening-surface-conformance.json', {'root': str(root), 'all_valid': True})
    _write_json(root / 'validation' / 'opening-surface-captures.json', {'captures': [{'captured_at': '2026-03-20T00:00:00Z', 'output_dir': 'validation/latest/opening-surface-capture', 'warning_count': 0}]})
    # support surface latest is foreign-root, earlier one is current-root clean
    current_support_dir = root / 'validation' / 'current-support'
    foreign_support_dir = root / 'validation' / 'foreign-support'
    _write_json(current_support_dir / 'support-surface.json', {'root': str(root)})
    _write_json(foreign_support_dir / 'support-surface.json', {'root': '/tmp/old-root'})
    _write_json(root / 'validation' / 'support-surface-captures.json', {'captures': [
        {'captured_at': '2026-03-20T00:00:00Z', 'output_dir': 'validation/current-support', 'contract_error_count': 0, 'surface_count': 1},
        {'captured_at': '2026-03-21T00:00:00Z', 'output_dir': 'validation/foreign-support', 'contract_error_count': 0, 'surface_count': 1},
    ]})
    # install receipt current-root
    install_dir = root / 'validation' / 'latest' / 'install-receipt-capture'
    _write_json(install_dir / 'install-receipt.json', {'root': str(root), 'bootstrap': {'stage': 'native-host-registration-missing'}})
    _write_json(root / 'validation' / 'install-receipts.json', {'captures': [{'captured_at': '2026-03-20T00:00:00Z', 'output_dir': 'validation/latest/install-receipt-capture'}]})
    register = build_truth_surface_register(root=root)
    families = {item['family_key']: item for item in register['families']}
    assert families['opening_surface']['citation_head']['captured_at'] == '2026-03-20T00:00:00Z'
    assert families['support_surface']['latest_operational_head']['payload_root_is_current'] is False
    assert families['support_surface']['latest_current_root_head']['captured_at'] == '2026-03-20T00:00:00Z'
    assert 'different archive root' in families['support_surface']['warnings'][0]
    assert register['counts']['families_whose_latest_head_points_at_foreign_root'] >= 1


def test_capture_truth_surface_register_writes_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'truth-surface-register'
    payload = capture_truth_surface_register(output_dir=output_dir, root=tmp_path)
    assert (output_dir / 'truth-surface-register.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['family_count'] >= 1
