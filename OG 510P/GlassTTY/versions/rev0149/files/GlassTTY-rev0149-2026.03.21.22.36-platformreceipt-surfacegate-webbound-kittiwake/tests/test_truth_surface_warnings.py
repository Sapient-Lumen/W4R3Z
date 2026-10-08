from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('truth_surface_warnings', ROOT / 'scripts' / 'truth_surface_warnings.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_truth_surface_warnings = MODULE.build_truth_surface_warnings
capture_truth_surface_warnings = MODULE.capture_truth_surface_warnings


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_build_truth_surface_warnings_prioritizes_foreign_root_and_missing_citation(tmp_path: Path) -> None:
    root = tmp_path
    opening_dir = root / 'validation' / 'latest' / 'opening-surface-capture'
    _write_json(opening_dir / 'opening-surface-conformance.json', {'root': str(root), 'all_valid': False, 'warning_count': 1})
    _write_json(root / 'validation' / 'opening-surface-captures.json', {'captures': [{'captured_at': '2026-03-20T00:00:00Z', 'output_dir': 'validation/latest/opening-surface-capture', 'warning_count': 1}]})

    foreign_dir = root / 'validation' / 'latest' / 'support-surface-capture'
    _write_json(foreign_dir / 'support-surface.json', {'root': '/tmp/old-root'})
    _write_json(root / 'validation' / 'support-surface-captures.json', {'captures': [{'captured_at': '2026-03-20T01:00:00Z', 'output_dir': 'validation/latest/support-surface-capture', 'contract_error_count': 0, 'surface_count': 1}]})

    payload = build_truth_surface_warnings(root=root)
    assert payload['counts']['warning_count'] >= 2
    assert payload['warnings'][0]['severity'] == 'error'
    assert 'different archive root' in ' '.join(item['message'] for item in payload['warnings'])


def test_capture_truth_surface_warnings_writes_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'truth-surface-warnings'
    payload = capture_truth_surface_warnings(output_dir=output_dir, root=tmp_path)
    assert (output_dir / 'truth-surface-warnings.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['commands']['report'] == 'python scripts/truth-surface-warnings.py --pretty'
