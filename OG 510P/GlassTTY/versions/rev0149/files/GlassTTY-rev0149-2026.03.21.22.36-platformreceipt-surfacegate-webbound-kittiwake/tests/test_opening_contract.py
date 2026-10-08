from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('check_opening_contract', ROOT / 'scripts' / 'check_opening_contract.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_opening_surface_conformance = MODULE.build_opening_surface_conformance
capture_opening_surface = MODULE.capture_opening_surface
summarize_capture_history = MODULE.summarize_capture_history


def test_build_opening_surface_conformance_uses_contract_and_startup_doc() -> None:
    payload = build_opening_surface_conformance(root=ROOT)
    assert payload['all_valid'] is True
    assert any(item['path'] == 'README.md' and item['exists'] for item in payload['ordered_reads'])
    assert any(item['command'] == 'python scripts/check-opening-contract.py --pretty' for item in payload['commands'])


def test_capture_opening_surface_writes_root_and_history(tmp_path: Path) -> None:
    (tmp_path / 'docs').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'README.md').write_text('# demo\n', encoding='utf-8')
    (tmp_path / 'STATUS.md').write_text('# status\n', encoding='utf-8')
    (tmp_path / 'REVISION-RECEIPT.json').write_text('{}\n', encoding='utf-8')
    (tmp_path / 'PROJECT_MAP.md').write_text('# map\n', encoding='utf-8')
    (tmp_path / 'docs' / 'operator-startup.md').write_text(
        '\n'.join([
            '1. Read `README.md`.',
            '2. Read `STATUS.md`.',
            '3. Read `REVISION-RECEIPT.json`.',
            '4. Read `PROJECT_MAP.md`.',
            '5. Run `python scripts/doctor.py --pretty`.',
            '6. Run `python scripts/readiness-report.py --pretty`.',
            '7. Run `python scripts/check-opening-contract.py --pretty`.',
        ]) + '\n',
        encoding='utf-8',
    )
    contract = json.loads((ROOT / 'OPENING-CONTRACT.json').read_text(encoding='utf-8'))
    (tmp_path / 'OPENING-CONTRACT.json').write_text(json.dumps(contract, indent=2) + '\n', encoding='utf-8')
    output_dir = tmp_path / 'validation' / 'latest' / 'opening-surface-capture'
    history_path = tmp_path / 'validation' / 'opening-surface-captures.json'
    payload = capture_opening_surface(output_dir=output_dir, history_path=history_path, root=tmp_path)
    assert payload['history_update']['capture_count_after_write'] == 1
    assert (tmp_path / 'OPENING-SURFACE-CONFORMANCE.json').exists()
    assert (output_dir / 'opening-surface-conformance.json').exists()
    assert summarize_capture_history(history_path)['capture_count'] == 1


def test_doctor_exposes_opening_and_truth_surface_commands() -> None:
    output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
    assert output['opening_surface']['commands']['report'] == 'python scripts/check-opening-contract.py --pretty'
    assert output['truth_surface']['commands']['refresh_all'] == 'python scripts/refresh-truth-surfaces.py --pretty'
    assert output['truth_surface_warnings']['commands']['report'] == 'python scripts/truth-surface-warnings.py --pretty'
    assert output['revision_receipt']['commands']['report'] == 'python scripts/check-revision-receipt.py --pretty'
    assert any('OPENING-SURFACE-CONFORMANCE.json' in hint for hint in output['hints'])
    assert any('truth stack' in hint and 'python scripts/refresh-truth-surfaces.py --pretty' in hint for hint in output['hints'])
    assert any('REVISION-RECEIPT.json' in hint for hint in output['hints'])
