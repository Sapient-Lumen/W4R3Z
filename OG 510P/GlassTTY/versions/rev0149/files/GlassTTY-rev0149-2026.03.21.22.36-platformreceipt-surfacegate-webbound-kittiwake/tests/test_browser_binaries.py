from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from browser_binaries import (
    augment_browser_choice,
    detect_cft_platform,
    discover_browser_executable,
    install_cft_asset,
    latest_local_cft_install,
    local_cft_installations,
    resolve_cft_channel_asset,
)


def test_detect_cft_platform_for_linux() -> None:
    assert detect_cft_platform(system='linux', machine='x86_64') == 'linux64'


def test_latest_local_cft_install_picks_highest_version(tmp_path: Path) -> None:
    for version in ('136.0.7103.1', '137.0.1.2'):
        target = tmp_path / version / 'chrome-linux64'
        target.mkdir(parents=True)
        browser = target / 'chrome'
        browser.write_text('', encoding='utf-8')
    installs = local_cft_installations(root=tmp_path, platform='linux64')
    assert installs[0]['version'] == '137.0.1.2'
    latest = latest_local_cft_install(root=tmp_path, platform='linux64')
    assert latest is not None
    assert latest['version'] == '137.0.1.2'


def test_resolve_cft_channel_asset_chooses_platform_specific_url() -> None:
    catalog = {
        'channels': {
            'Stable': {
                'version': '136.0.7103.92',
                'revision': '1234567',
                'downloads': {
                    'chrome': [
                        {'platform': 'linux64', 'url': 'https://example.test/linux.zip'},
                        {'platform': 'mac-x64', 'url': 'https://example.test/mac.zip'},
                    ]
                },
            }
        }
    }
    asset = resolve_cft_channel_asset(catalog, channel='stable', binary='chrome', platform='linux64')
    assert asset['version'] == '136.0.7103.92'
    assert asset['url'] == 'https://example.test/linux.zip'


def test_install_cft_asset_extracts_local_archive(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('chrome-linux64/chrome', '#!/bin/sh\necho chrome\n')
    asset = {
        'version': '136.0.7103.92',
        'binary': 'chrome',
        'platform': 'linux64',
        'url': archive.as_uri(),
        'source': 'test',
    }
    result = install_cft_asset(asset=asset, root=tmp_path / 'cft')
    executable = Path(result['executable'])
    assert executable.exists()
    assert executable.read_text(encoding='utf-8').startswith('#!/bin/sh')
    metadata = json.loads((Path(result['install_dir']) / 'install.json').read_text(encoding='utf-8'))
    assert metadata['version'] == '136.0.7103.92'


def test_discover_browser_executable_prefers_local_cft(tmp_path: Path) -> None:
    browser = tmp_path / 'browsers' / 'chrome-for-testing' / '136.0.7103.92' / 'chrome-linux64' / 'chrome'
    browser.parent.mkdir(parents=True)
    browser.write_text('', encoding='utf-8')
    choice = discover_browser_executable(env={'GLASSTTY_HOME': str(tmp_path)})
    assert choice['source'] == 'chrome-for-testing'
    assert choice['path'] == str(browser)


def test_chrome_for_testing_script_inspect_reports_local_install(tmp_path: Path) -> None:
    browser = tmp_path / '136.0.7103.92' / 'chrome-linux64' / 'chrome'
    browser.parent.mkdir(parents=True)
    browser.write_text('', encoding='utf-8')
    output = subprocess.check_output([
        sys.executable,
        str(ROOT / 'scripts' / 'chrome-for-testing.py'),
        'inspect',
        '--root',
        str(tmp_path),
    ], text=True)
    data = json.loads(output)
    assert data['latest_local_install']['executable'] == str(browser)


def test_chrome_for_testing_script_local_executable_exit_code(tmp_path: Path) -> None:
    cmd = [sys.executable, str(ROOT / 'scripts' / 'chrome-for-testing.py'), 'local-executable', '--root', str(tmp_path)]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    assert completed.returncode == 1


def test_augment_browser_choice_uses_chrome_target_for_current_cft() -> None:
    choice = augment_browser_choice({'source': 'chrome-for-testing', 'path': '/tmp/cft/136.0.7103.92/chrome-linux64/chrome', 'version': '136.0.7103.92', 'exists': True})
    assert choice['browser_family'] == 'chrome-for-testing'
    assert choice['native_messaging_targets'] == ['chrome']
    assert 'Chrome for Testing 136.0.7103.92 still uses Google Chrome native-messaging locations' in choice['native_messaging_notes'][0]


def test_augment_browser_choice_uses_cft_target_after_split() -> None:
    choice = augment_browser_choice({'source': 'chrome-for-testing', 'path': '/tmp/cft/146.0.0.0/chrome-linux64/chrome', 'version': '146.0.0.0', 'exists': True})
    assert choice['native_messaging_targets'] == ['chrome-for-testing']


def test_discover_browser_executable_explicit_cft_path_infers_targets(tmp_path: Path) -> None:
    browser = tmp_path / 'browsers' / 'chrome-for-testing' / '136.0.7103.92' / 'chrome-linux64' / 'chrome'
    browser.parent.mkdir(parents=True)
    browser.write_text('', encoding='utf-8')
    choice = discover_browser_executable(env={'GLASSTTY_CHROMIUM_BIN': str(browser)})
    assert choice['browser_family'] == 'chrome-for-testing'
    assert choice['version'] == '136.0.7103.92'
    assert choice['native_messaging_targets'] == ['chrome']
