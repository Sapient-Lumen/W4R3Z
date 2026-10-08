from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from browser_binaries import augment_browser_choice
from native_host_manifest import inspect_manifest_file, inspect_targets, render_manifest, resolve_install_targets, resolve_target_dir
from native_host_report import build_report, build_resolve_targets


def test_resolve_target_dir_knows_linux_targets(tmp_path: Path) -> None:
    home = tmp_path / 'home'
    assert resolve_target_dir('chromium', 'linux', home=home) == home / '.config' / 'chromium' / 'NativeMessagingHosts'
    assert resolve_target_dir('chrome', 'linux', home=home) == home / '.config' / 'google-chrome' / 'NativeMessagingHosts'
    assert resolve_target_dir('chrome-for-testing', 'linux', home=home) == home / '.config' / 'google-chrome-for-testing' / 'NativeMessagingHosts'


def test_resolve_install_targets_auto_prefers_browser_recommendation() -> None:
    cft136 = augment_browser_choice({'source': 'chrome-for-testing', 'path': '/tmp/cft/136.0.7103.92/chrome-linux64/chrome', 'exists': True, 'version': '136.0.7103.92'})
    cft146 = augment_browser_choice({'source': 'chrome-for-testing', 'path': '/tmp/cft/146.0.0.0/chrome-linux64/chrome', 'exists': True, 'version': '146.0.0.0'})
    chromium = augment_browser_choice({'source': 'system-path', 'path': '/usr/bin/chromium', 'exists': True})

    assert resolve_install_targets('auto', browser_choice=cft136)['resolved_targets'] == ['chrome']
    assert resolve_install_targets('auto', browser_choice=cft146)['resolved_targets'] == ['chrome-for-testing']
    assert resolve_install_targets('auto', browser_choice=chromium)['resolved_targets'] == ['chromium']


def test_render_and_inspect_manifest_round_trip(tmp_path: Path) -> None:
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)
    manifest_path = tmp_path / 'com.glasstty.bridge.json'
    manifest_path.write_text(json.dumps(render_manifest(host_path=host, extension_id='abcdefghijklmnopqrstuvwxyzaaaaaa'), indent=2), encoding='utf-8')

    report = inspect_manifest_file(manifest_path, expected_extension_id='abcdefghijklmnopqrstuvwxyzaaaaaa', expected_host_path=host)
    assert report['manifest_exists'] is True
    assert report['manifest_parse_ok'] is True
    assert report['extension_id_match'] is True
    assert report['host_path_match'] is True
    assert report['manifest_host_exists'] is True
    assert report['manifest_host_executable'] is True


def test_inspect_targets_finds_mismatch(tmp_path: Path) -> None:
    home = tmp_path / 'home'
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)
    wrong = tmp_path / 'other-wrapper.sh'
    wrong.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    wrong.chmod(0o755)

    target_dir = resolve_target_dir('chromium', 'linux', home=home)
    target_dir.mkdir(parents=True)
    (target_dir / 'com.glasstty.bridge.json').write_text(json.dumps(render_manifest(host_path=wrong, extension_id='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'), indent=2), encoding='utf-8')

    report = inspect_targets(os_name='linux', extension_id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', expected_host_path=host, home=home)
    chromium = report['chromium']
    assert chromium['manifest_exists'] is True
    assert chromium['extension_id_match'] is False
    assert chromium['host_path_match'] is False


def test_native_host_report_script_surfaces_recommendations() -> None:
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'native-host-report.py')], text=True)
    data = json.loads(output)
    assert data['host_name'] == 'com.glasstty.bridge'
    assert isinstance(data['recommended_targets'], list)
    assert isinstance(data['all_recommended_targets'], list)
    assert isinstance(data['targets'], dict)
    assert 'chromium' in data['targets']


def test_install_native_host_script_auto_target_supports_explicit_home(tmp_path: Path) -> None:
    env = dict(os.environ)
    home = tmp_path / 'home'
    env['HOME'] = str(home)
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)
    subprocess.check_call([
        str(ROOT / 'scripts' / 'install-native-host.sh'),
        '--target',
        'chromium',
        '--os',
        'linux',
        '--extension-id',
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        '--host-exe',
        str(host),
    ], env=env)
    manifest_path = home / '.config' / 'chromium' / 'NativeMessagingHosts' / 'com.glasstty.bridge.json'
    payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert payload['path'] == str(host)
    assert payload['allowed_origins'] == ['chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/']


def test_install_native_host_script_auto_target_uses_browser_recommendation(tmp_path: Path) -> None:
    env = dict(os.environ)
    home = tmp_path / 'home'
    env['HOME'] = str(home)
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)
    subprocess.check_call([
        str(ROOT / 'scripts' / 'install-native-host.sh'),
        '--target',
        'auto',
        '--os',
        'linux',
        '--extension-id',
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        '--host-exe',
        str(host),
    ], env=env)
    manifest_path = home / '.config' / 'chromium' / 'NativeMessagingHosts' / 'com.glasstty.bridge.json'
    assert manifest_path.exists()


def test_native_host_report_browser_bin_overrides_default_choice() -> None:
    payload = build_resolve_targets(
        target='auto',
        all_recommended=False,
        browser_bin='/tmp/chrome-for-testing/146.0.0.0/chrome-linux64/chrome',
    )
    assert payload['resolved_targets'] == ['chrome-for-testing']


def test_native_host_report_recommended_target_status_marks_missing_targets(tmp_path: Path) -> None:
    home = tmp_path / 'home'
    payload = build_report(os_name='linux', extension_id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', host_exe=str(tmp_path / 'missing-wrapper.sh'), browser_bin='/usr/bin/chromium', home=home)
    status = payload['recommended_target_status']
    assert status['primary_target'] == 'chromium'
    assert status['primary_target_ready'] is False
    assert 'chromium' in status['missing_targets']


def test_native_host_report_combines_playwright_and_default_browser_targets(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / 'home'
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)

    def fake_discover_playwright_browser_install():
        return {
            'available': True,
            'launch_strategy': 'bundled-executable',
            'bundled_executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
            'bundled_install': {
                'executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
                'package_name': 'chromium',
                'version': '145.0.7632.6',
                'source': 'cache-scan',
                'install_name': 'chromium-1208',
            },
        }

    def fake_playwright_extension_launch_plan(*, browser_install=None):
        return {'strategy': 'bundled-executable', 'browser_choice': {'native_messaging_targets': ['chromium']}, 'required_native_messaging_targets': ['chromium']}

    monkeypatch.setattr('native_host_report.discover_playwright_browser_install', fake_discover_playwright_browser_install)
    monkeypatch.setattr('native_host_report.playwright_extension_launch_plan', fake_playwright_extension_launch_plan)

    payload = build_report(os_name='linux', extension_id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', host_exe=str(host), browser_bin='/tmp/chrome-for-testing/146.0.0.0/chrome-linux64/chrome', home=home)
    assert payload['recommended_targets'] == ['chrome-for-testing']
    assert payload['playwright_recommended_targets'] == ['chromium']
    assert payload['combined_recommended_targets'] == ['chromium', 'chrome-for-testing']


def test_build_resolve_targets_playwright_scope_prefers_playwright_targets(monkeypatch) -> None:
    def fake_discover_playwright_browser_install():
        return {'available': True}

    def fake_playwright_extension_launch_plan(*, browser_install=None):
        return {'strategy': 'bundled-executable'}

    def fake_playwright_browser_choice(browser_install, *, launch_plan=None):
        return {'native_messaging_targets': ['chromium']}

    monkeypatch.setattr('native_host_report.discover_playwright_browser_install', fake_discover_playwright_browser_install)
    monkeypatch.setattr('native_host_report.playwright_extension_launch_plan', fake_playwright_extension_launch_plan)
    monkeypatch.setattr('native_host_report.playwright_browser_choice', fake_playwright_browser_choice)

    payload = build_resolve_targets(
        target='playwright',
        all_recommended=False,
        browser_bin='/tmp/chrome-for-testing/146.0.0.0/chrome-linux64/chrome',
    )
    assert payload['selection_mode'] == 'playwright-browser'
    assert payload['resolved_targets'] == ['chromium']
    assert payload['default_browser_targets'] == ['chrome-for-testing']
    assert payload['playwright_targets'] == ['chromium']
    assert payload['combined_targets'] == ['chromium', 'chrome-for-testing']


def test_build_resolve_targets_combined_scope_unions_playwright_and_default(monkeypatch) -> None:
    def fake_discover_playwright_browser_install():
        return {'available': True}

    def fake_playwright_extension_launch_plan(*, browser_install=None):
        return {'strategy': 'bundled-executable'}

    def fake_playwright_browser_choice(browser_install, *, launch_plan=None):
        return {'native_messaging_targets': ['chromium']}

    monkeypatch.setattr('native_host_report.discover_playwright_browser_install', fake_discover_playwright_browser_install)
    monkeypatch.setattr('native_host_report.playwright_extension_launch_plan', fake_playwright_extension_launch_plan)
    monkeypatch.setattr('native_host_report.playwright_browser_choice', fake_playwright_browser_choice)

    payload = build_resolve_targets(
        target='combined',
        all_recommended=False,
        browser_bin='/tmp/chrome-for-testing/146.0.0.0/chrome-linux64/chrome',
    )
    assert payload['selection_mode'] == 'combined-browser-matrix'
    assert payload['resolved_targets'] == ['chromium', 'chrome-for-testing']


def test_native_host_report_prefers_single_combined_install_command_when_targets_diverge(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / 'home'
    host = tmp_path / 'native-host-wrapper.sh'
    host.write_text('#!/usr/bin/env bash\n', encoding='utf-8')
    host.chmod(0o755)

    def fake_discover_playwright_browser_install():
        return {'available': True}

    def fake_playwright_extension_launch_plan(*, browser_install=None):
        return {'strategy': 'bundled-executable'}

    def fake_playwright_browser_choice(browser_install, *, launch_plan=None):
        return {'native_messaging_targets': ['chromium']}

    monkeypatch.setattr('native_host_report.discover_playwright_browser_install', fake_discover_playwright_browser_install)
    monkeypatch.setattr('native_host_report.playwright_extension_launch_plan', fake_playwright_extension_launch_plan)
    monkeypatch.setattr('native_host_report.playwright_browser_choice', fake_playwright_browser_choice)

    payload = build_report(os_name='linux', extension_id='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', host_exe=str(host), browser_bin='/tmp/chrome-for-testing/146.0.0.0/chrome-linux64/chrome', home=home)
    assert payload['combined_recommended_targets'] == ['chromium', 'chrome-for-testing']
    assert payload['suggested_install_command'] == f'./scripts/install-native-host.sh --target combined --extension-id aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --host-exe {host}'
    assert payload['suggested_install_matrix_command'] == payload['suggested_install_command']
    assert payload['suggested_install_commands'] == [
        f'./scripts/install-native-host.sh --target chromium --extension-id aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --host-exe {host}',
        f'./scripts/install-native-host.sh --target chrome-for-testing --extension-id aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --host-exe {host}',
    ]
