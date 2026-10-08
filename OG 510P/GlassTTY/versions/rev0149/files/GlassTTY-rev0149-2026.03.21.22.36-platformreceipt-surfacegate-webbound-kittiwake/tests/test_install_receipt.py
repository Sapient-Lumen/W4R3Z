from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / 'scripts' / 'install_receipt.py'
SPEC = importlib.util.spec_from_file_location('install_receipt', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_install_receipt = MODULE.build_install_receipt
capture_install_receipt = MODULE.capture_install_receipt
summarize_capture_history = MODULE.summarize_capture_history


def _doctor_report(*, attach_ready: bool = False, socket_exists: bool = False) -> dict:
    return {
        'project': 'GlassTTY',
        'native_host': {
            'wrapper': {
                'path': str(ROOT / 'scripts' / 'native-host-wrapper.sh'),
                'exists': True,
                'executable': True,
            }
        },
        'profiles': {
            'triage': {
                'best_profile': {
                    'name': 'main',
                    'tier': 'attach-ready' if attach_ready else 'saved',
                    'attach_ready': attach_ready,
                }
            }
        },
        'socket': {'exists': socket_exists},
        'validation': {
            'latest_report': {'exists': True, 'summary': {'complete': True}},
            'commands': {'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume'},
        },
        'fixture_lab': {'latest_smoke_report': {'exists': False}, 'smoke_capture_history': {'capture_count': 0}},
        'playwright': {'extension_launch_plan': {'skip_reason': None}},
    }


def _native_host_report(*, missing_targets: list[str] | None = None, socket_exists: bool = False) -> dict:
    missing_targets = missing_targets if missing_targets is not None else ['chromium']
    return {
        'extension_id': 'abcdefghijklmnopabcdefghijklmnop',
        'all_recommended_targets': ['chromium'],
        'playwright_recommended_targets': ['chromium'],
        'combined_recommended_targets': ['chromium'],
        'combined_recommended_target_status': {
            'ready_targets': [] if missing_targets else ['chromium'],
            'missing_targets': missing_targets,
            'parse_failure_targets': [],
            'extension_id_mismatch_targets': [],
            'host_path_mismatch_targets': [],
        },
        'suggested_install_command': './scripts/install-native-host.sh --target chromium --extension-id abc --host-exe ./scripts/native-host-wrapper.sh',
        'suggested_install_commands': ['./scripts/install-native-host.sh --target chromium --extension-id abc --host-exe ./scripts/native-host-wrapper.sh'],
        'runtime': {
            'socket_path': '/tmp/daemon.sock',
            'socket_exists': socket_exists,
            'lock_path': '/tmp/daemon.lock',
            'lock_exists': False,
            'metadata_path': '/tmp/daemon-broker-owner.json',
            'metadata_exists': False,
            'owner_metadata': None,
        },
    }


def test_build_install_receipt_separates_registration_from_runtime() -> None:
    receipt = build_install_receipt(
        doctor_report=_doctor_report(attach_ready=False, socket_exists=False),
        native_host_report=_native_host_report(missing_targets=['chromium'], socket_exists=False),
    )
    assert receipt['bootstrap']['stage'] == 'native-host-registration-missing'
    assert 'chromium' in (receipt['bootstrap']['primary_blocker'] or '')
    assert receipt['materialization']['native_messaging_permission_declared'] is True
    assert receipt['registration']['suggested_install_command'].startswith('./scripts/install-native-host.sh')


def test_capture_install_receipt_writes_bundle_history_and_diff(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'install-receipt-capture'
    history_path = tmp_path / 'validation' / 'install-receipts.json'

    first = capture_install_receipt(
        output_dir=output_dir,
        history_path=history_path,
        doctor_report=_doctor_report(attach_ready=False, socket_exists=False),
        native_host_report=_native_host_report(missing_targets=['chromium'], socket_exists=False),
        root=tmp_path,
    )
    assert first['history_update']['capture_count_after_write'] == 1
    assert (output_dir / 'install-receipt.json').exists()
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'native-host-report.json').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()

    second = capture_install_receipt(
        output_dir=output_dir,
        history_path=history_path,
        doctor_report=_doctor_report(attach_ready=True, socket_exists=True),
        native_host_report=_native_host_report(missing_targets=[], socket_exists=True),
        root=tmp_path,
    )
    diff = json.loads((output_dir / 'capture-diff.json').read_text(encoding='utf-8'))
    saved = json.loads((output_dir / 'install-receipt.json').read_text(encoding='utf-8'))
    history = summarize_capture_history(history_path)
    assert second['history_update']['capture_count_after_write'] == 2
    assert saved['bootstrap']['stage'] == 'runtime-reachable'
    assert 'bootstrap' in diff['changed_fields']
    assert history['capture_count'] == 2


def test_doctor_exposes_install_receipt_commands_and_hint() -> None:
    output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
    assert output['install_receipt']['commands']['report'] == 'python scripts/install-receipt.py --pretty'
    assert any('install receipt' in hint and 'python scripts/install-receipt.py --pretty' in hint for hint in output['hints'])
