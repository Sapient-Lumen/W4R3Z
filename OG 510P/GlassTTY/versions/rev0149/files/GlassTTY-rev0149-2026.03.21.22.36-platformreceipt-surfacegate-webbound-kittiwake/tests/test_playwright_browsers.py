from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import zipfile
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import playwright_browsers as pb
from playwright_browsers import (
    PLAYWRIGHT_HEADLESS_SHELL_PACKAGE,
    PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV,
    audit_playwright_cache,
    ensure_playwright_links_dir,
    ensure_playwright_registry_link,
    expected_playwright_package,
    discover_playwright_browser_install,
    inspect_playwright_registry,
    download_playwright_browser_archive,
    ensure_playwright_channel_ready,
    import_cft_into_playwright_cache,
    install_playwright_browser_archive,
    latest_local_playwright_browser_install,
    local_playwright_browser_installations,
    parse_playwright_install_dry_run,
    parse_playwright_install_list,
    plan_playwright_cache_repair,
    playwright_browser_choice,
    playwright_extension_launch_plan,
    playwright_install_list,
    repair_playwright_cache,
    sync_playwright_browser_packages,
)


def make_browser_archive(path: Path) -> None:
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('chrome-linux64/chrome', '#!/bin/sh\necho chromium\n')


def make_headless_shell_archive(path: Path) -> None:
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('chrome-headless-shell-linux64/chrome-headless-shell', '#!/bin/sh\necho headless\n')


def make_shadow_playwright_install(root: Path, *, install_name: str, version: str, revision: str | None = None, source: str = 'manual-copy') -> Path:
    shadow = root / install_name
    (shadow / 'chrome-linux64').mkdir(parents=True)
    (shadow / 'chrome-linux64' / 'chrome').write_text('#!/bin/sh\necho shadow\n', encoding='utf-8')
    payload: dict[str, str] = {'version': version, 'source': source}
    if revision:
        payload['revision'] = revision
    (shadow / 'install.json').write_text(json.dumps(payload) + '\n', encoding='utf-8')
    return shadow


def make_fake_playwright_package(package_dir: Path, *, version: str, revision: str, browser_name: str = 'chromium') -> Path:
    package_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        'comment': 'test package',
        'browsers': [
            {
                'name': browser_name,
                'revision': revision,
                'browserVersion': version,
                'installByDefault': True,
                'title': 'Chrome for Testing',
            }
        ],
    }
    (package_dir / 'browsers.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    (package_dir / 'package.json').write_text(json.dumps({'name': 'playwright-test-driver', 'version': '1.0.0'}, indent=2) + '\n', encoding='utf-8')
    return package_dir


def make_fake_playwright_module(base: Path, *, version: str = '145.0.7632.6', revision: str = '1208') -> tuple[Path, Path]:
    pkg = base / 'playwright'
    driver_pkg = pkg / 'driver' / 'package'
    make_fake_playwright_package(driver_pkg, version=version, revision=revision)
    (pkg / '__init__.py').write_text('__all__ = []\n', encoding='utf-8')
    script = 'import os, sys\nfrom pathlib import Path\n\nROOT = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache" / "ms-playwright"))).expanduser()\nDRIVER = Path(__file__).resolve().parent / "driver" / "package"\n\nif sys.argv[1:4] == ["install", "--dry-run", "chromium"]:\n    print("Chrome for Testing __VERSION__ (playwright chromium v__REVISION__)")\n    print("  Install location:    " + str(ROOT / "chromium-__REVISION__"))\n    print("  Download url:        https://cdn.playwright.dev/chrome-for-testing-public/__VERSION__/linux64/chrome-linux64.zip")\n    raise SystemExit(0)\n\nif sys.argv[1:3] == ["install", "--list"]:\n    print("Playwright version: 1.53.0")\n    print("  Browsers:")\n    if ROOT.exists():\n        for item in sorted(ROOT.iterdir()):\n            if item.is_dir() and item.name.startswith(("chromium-", "chromium-cft-", "chromium_headless_shell-")):\n                print(f"    {item}")\n    print("  References:")\n    print(f"    {DRIVER}")\n    raise SystemExit(0)\n\nraise SystemExit(2)\n'
    script = script.replace('__VERSION__', version).replace('__REVISION__', revision)
    (pkg / '__main__.py').write_text(script, encoding='utf-8')
    return base, pkg / '__init__.py'


def test_install_playwright_browser_archive_extracts_local_zip(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    result = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        install_name='chromium-local-145.0.7632.6',
        metadata={'version': '145.0.7632.6', 'source': 'archive-import'},
    )
    executable = Path(result['executable'])
    assert executable.exists()
    assert executable.read_text(encoding='utf-8').startswith('#!/bin/sh')
    metadata = json.loads((Path(result['install_dir']) / 'install.json').read_text(encoding='utf-8'))
    assert metadata['version'] == '145.0.7632.6'
    assert metadata['source'] == 'archive-import'
    assert Path(str(result['marker_state']['marker_path'])).exists()
    assert result['registry_link_state']['registry_link_exists'] is True


def test_local_playwright_browser_installations_sort_by_version(tmp_path: Path) -> None:
    for version in ('144.0.0.0', '145.0.7632.6'):
        install_dir = tmp_path / f'chromium-cft-{version}'
        (install_dir / 'chrome-linux64').mkdir(parents=True)
        (install_dir / 'chrome-linux64' / 'chrome').write_text('', encoding='utf-8')
        (install_dir / 'install.json').write_text(json.dumps({'version': version}) + '\n', encoding='utf-8')
    installs = local_playwright_browser_installations(root=tmp_path, platform='linux64')
    assert installs[0]['version'] == '145.0.7632.6'
    assert latest_local_playwright_browser_install(root=tmp_path, platform='linux64')['version'] == '145.0.7632.6'


def test_import_cft_into_playwright_cache_copies_latest_install(tmp_path: Path) -> None:
    cft_root = tmp_path / 'cft'
    cft_dir = cft_root / '146.0.7680.66' / 'chrome-linux64'
    cft_dir.mkdir(parents=True)
    (cft_dir / 'chrome').write_text('#!/bin/sh\necho cft\n', encoding='utf-8')
    result = import_cft_into_playwright_cache(cft_root=cft_root, playwright_root=tmp_path / 'pw', platform='linux64')
    executable = Path(result['executable'])
    assert executable.exists()
    metadata = json.loads(Path(result['metadata_path']).read_text(encoding='utf-8'))
    assert metadata['version'] == '146.0.7680.66'
    assert metadata['source'] == 'chrome-for-testing-import'
    assert Path(str(result['marker_state']['marker_path'])).exists()


def test_discover_playwright_browser_install_reports_imported_bundle(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path,
        install_name='chromium-cft-145.0.7632.6',
        metadata={'version': '145.0.7632.6', 'source': 'archive-import'},
    )
    install = discover_playwright_browser_install(env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path)}, playwright_available=True, import_error=None)
    assert install['bundled_executable_exists'] is True
    assert install['bundled_install']['source'] == 'archive-import'
    assert install['launch_strategy'] == 'bundled-executable'


def test_playwright_extension_launch_plan_recommends_offline_import() -> None:
    plan = playwright_extension_launch_plan(
        env={},
        browser_install={
            'available': True,
            'import_error': None,
            'bundled_executable_exists': False,
            'system_chromium': '/usr/bin/chromium',
        },
    )
    assert plan['skip_reason'] == 'missing-bundled-chromium'
    assert 'import-cft' in (plan['recommended_import_command'] or '')


def test_playwright_browsers_script_import_archive_and_inspect(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    fake_site, _ = make_fake_playwright_module(tmp_path / 'fake-site')
    env = dict(os.environ)
    env['PYTHONPATH'] = str(fake_site) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    subprocess.check_call([
        sys.executable,
        str(ROOT / 'scripts' / 'playwright-browsers.py'),
        'import-archive',
        '--archive',
        str(archive),
        '--root',
        str(tmp_path / 'pw'),
        '--install-name',
        'chromium-local-145.0.7632.6',
        '--version',
        '145.0.7632.6',
    ], env=env)
    output = subprocess.check_output([
        sys.executable,
        str(ROOT / 'scripts' / 'playwright-browsers.py'),
        'inspect',
        '--root',
        str(tmp_path / 'pw'),
    ], text=True, env=env)
    data = json.loads(output)
    assert data['latest_local_install']['version'] == '145.0.7632.6'
    assert data['discovered_browser_install']['bundled_executable_exists'] is True
    assert 'extension_launch_plan' in data
    assert data['extension_launch_plan']['cache_alignment_status'] in {'aligned', 'cache-install-name-drift'}


def test_chrome_for_testing_script_install_accepts_archive_path(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    output = subprocess.check_output([
        sys.executable,
        str(ROOT / 'scripts' / 'chrome-for-testing.py'),
        'install',
        '--archive-path',
        str(archive),
        '--root',
        str(tmp_path / 'cft'),
        '--version',
        '145.0.7632.6',
        '--pretty',
    ], text=True)
    data = json.loads(output)
    assert Path(data['executable']).exists()
    assert data['version'] == '145.0.7632.6'


DRY_RUN_SAMPLE = """Chrome for Testing 145.0.7632.6 (playwright chromium v1208)
  Install location:    /home/oai/.cache/ms-playwright/chromium-1208
  Download url:        https://cdn.playwright.dev/chrome-for-testing-public/145.0.7632.6/linux64/chrome-linux64.zip

Chrome Headless Shell 145.0.7632.6 (playwright chromium-headless-shell v1208)
  Install location:    /home/oai/.cache/ms-playwright/chromium_headless_shell-1208
  Download url:        https://cdn.playwright.dev/chrome-for-testing-public/145.0.7632.6/linux64/chrome-headless-shell-linux64.zip
"""


def test_parse_playwright_install_dry_run_reports_browser_packages() -> None:
    packages = parse_playwright_install_dry_run(DRY_RUN_SAMPLE)
    assert packages[0]['package_name'] == 'chromium'
    assert packages[0]['install_name'] == 'chromium-1208'
    assert packages[1]['package_name'] == 'chromium_headless_shell'
    assert packages[1]['install_name'] == 'chromium_headless_shell-1208'

LIST_SAMPLE = """
Playwright version: 1.53.0
  Browsers:
    /home/oai/.cache/ms-playwright/chromium-1208
    /home/oai/.cache/ms-playwright/chromium_headless_shell-1208
  References:
    /opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package
"""


def test_parse_playwright_install_list_reports_versions_and_packages() -> None:
    groups = parse_playwright_install_list(LIST_SAMPLE)
    assert groups[0]['playwright_version'] == '1.53.0'
    assert groups[0]['browser_entries'][0]['package_name'] == 'chromium'
    assert groups[0]['browser_entries'][1]['package_name'] == 'chromium_headless_shell'
    assert groups[0]['reference_dirs'] == ['/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package']


def test_ensure_playwright_links_dir_creates_missing_links_directory(tmp_path: Path) -> None:
    report = ensure_playwright_links_dir(tmp_path / 'pw')
    assert report['links_dir_exists'] is True
    assert report['links_dir_created'] is True
    assert (tmp_path / 'pw' / '.links').is_dir()


def test_ensure_playwright_registry_link_creates_missing_link_file(tmp_path: Path) -> None:
    package_dir = tmp_path / 'driver-package'
    package_dir.mkdir()
    report = ensure_playwright_registry_link(tmp_path / 'pw', package_path=package_dir)
    assert report['registry_link_exists'] is True
    assert report['registry_link_created'] is True
    assert Path(str(report['registry_link_path'])).read_text(encoding='utf-8') == str(package_dir.resolve())




def test_audit_playwright_cache_reports_shadow_installs(tmp_path: Path) -> None:
    shadow = tmp_path / 'pw' / 'chromium-shadow-145.0.7632.6'
    (shadow / 'chrome-linux64').mkdir(parents=True)
    (shadow / 'chrome-linux64' / 'chrome').write_text('#!/bin/sh\necho shadow\n', encoding='utf-8')
    (shadow / 'install.json').write_text(json.dumps({'version': '145.0.7632.6', 'source': 'manual-copy'}) + '\n', encoding='utf-8')
    report = audit_playwright_cache(root=tmp_path / 'pw', env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')}, platform='linux64')
    assert report['counts']['shadow_installs'] == 1
    assert report['shadow_installs'][0]['install_name'] == 'chromium-shadow-145.0.7632.6'
    assert report['install_list']['returncode'] != 0
    assert report['install_list']['ensure_links'] is False
    assert report['notes']


def test_audit_playwright_cache_reports_missing_installation_marker(tmp_path: Path) -> None:
    install_dir = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name='chromium-shadow-145.0.7632.6',
        version='145.0.7632.6',
        revision='1208',
    )
    report = audit_playwright_cache(root=tmp_path / 'pw', env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')}, platform='linux64')
    assert install_dir.exists()
    assert report['counts']['marker_missing_installs'] == 1
    assert report['marker_missing_installs'][0]['install_name'] == 'chromium-shadow-145.0.7632.6'
    assert any('INSTALLATION_COMPLETE' in note for note in report['notes'])


def test_audit_playwright_cache_reports_broken_registry_link(tmp_path: Path) -> None:
    links_dir = tmp_path / 'pw' / '.links'
    links_dir.mkdir(parents=True)
    (links_dir / 'broken-link').write_text(str(tmp_path / 'missing-package'), encoding='utf-8')
    report = audit_playwright_cache(root=tmp_path / 'pw', env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')}, platform='linux64')
    assert report['counts']['broken_links'] >= 1
    assert any(item['link_name'] == 'broken-link' for item in report['registry']['broken_links'])


def test_playwright_install_list_raw_reports_missing_links_without_mutating_cache(tmp_path: Path) -> None:
    report = playwright_install_list(root=tmp_path / 'pw', timeout=5, ensure_links=False)
    assert report['returncode'] != 0
    assert report['ensure_links'] is False
    assert report['links_state']['links_dir_exists'] is False
    assert not (tmp_path / 'pw' / '.links').exists()


def test_audit_playwright_cache_reports_foreign_only_current_link_gap(tmp_path: Path) -> None:
    expected = expected_playwright_package(package_name='chromium')
    assert expected is not None
    install_dir = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name=str(expected['install_name']),
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    (install_dir / 'INSTALLATION_COMPLETE').touch()
    foreign_package = make_fake_playwright_package(
        tmp_path / 'foreign-package',
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    ensure_playwright_registry_link(tmp_path / 'pw', package_path=foreign_package)
    raw_install_list = playwright_install_list(root=tmp_path / 'pw', ensure_links=False)
    registry_raw = inspect_playwright_registry(tmp_path / 'pw', platform='linux64')
    prepared_install_list = playwright_install_list(root=tmp_path / 'pw', ensure_links=True)
    report = audit_playwright_cache(
        root=tmp_path / 'pw',
        env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
        platform='linux64',
        install_list=raw_install_list,
        prepared_install_list=prepared_install_list,
        registry_report=registry_raw,
    )
    assert raw_install_list['returncode'] == 0
    assert raw_install_list['links_state']['registry_link_exists'] is False
    assert report['registry']['current_driver_linked'] is False
    assert report['counts']['foreign_only_installs'] == 1
    assert report['counts']['current_unlinked_existing_browsers'] == 1
    assert report['counts']['gc_retained_installs'] == 1
    assert report['prepared_install_list']['links_state']['registry_link_created'] is True
    assert any('current-package browser install' in note for note in report['notes'])


def test_plan_playwright_cache_repair_reports_current_link_gap(tmp_path: Path) -> None:
    expected = expected_playwright_package(package_name='chromium')
    assert expected is not None
    install_dir = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name=str(expected['install_name']),
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    (install_dir / 'INSTALLATION_COMPLETE').touch()
    foreign_package = make_fake_playwright_package(
        tmp_path / 'foreign-package',
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    ensure_playwright_registry_link(tmp_path / 'pw', package_path=foreign_package)
    report = plan_playwright_cache_repair(root=tmp_path / 'pw', env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')}, platform='linux64')
    assert report['counts']['current_link_repairs'] == 1
    assert any('not linked into this cache root yet' in note for note in report['notes'])


def test_plan_playwright_cache_repair_reports_repairable_shadow_install(tmp_path: Path) -> None:
    expected = expected_playwright_package(package_name='chromium')
    assert expected is not None
    shadow = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name='chromium-shadow-145.0.7632.6',
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    report = plan_playwright_cache_repair(root=tmp_path / 'pw', env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')}, platform='linux64')
    assert shadow.exists()
    assert report['counts']['repairable_shadow_installs'] == 1
    candidate = report['repairable_shadow_installs'][0]
    assert candidate['source_install_name'] == 'chromium-shadow-145.0.7632.6'
    assert candidate['target_install_name'] == expected['install_name']
    assert 'revision-match' in candidate['match_reasons']


def test_repair_playwright_cache_aligns_shadow_install_and_prunes_broken_link(tmp_path: Path) -> None:
    expected = expected_playwright_package(package_name='chromium')
    assert expected is not None
    shadow = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name='chromium-shadow-145.0.7632.6',
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    links_dir = tmp_path / 'pw' / '.links'
    links_dir.mkdir(parents=True, exist_ok=True)
    broken_link = links_dir / 'broken-link'
    broken_link.write_text(str(tmp_path / 'missing-package'), encoding='utf-8')
    result = repair_playwright_cache(
        root=tmp_path / 'pw',
        env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
        platform='linux64',
        apply=True,
        align_shadow_installs=True,
        prune_broken_links=True,
        write_missing_markers=True,
    )
    assert result['ok'] is True
    assert result['changed'] is True
    aligned_dir = tmp_path / 'pw' / str(expected['install_name'])
    assert aligned_dir.exists()
    assert not shadow.exists()
    assert not broken_link.exists()
    metadata = json.loads((aligned_dir / 'install.json').read_text(encoding='utf-8'))
    assert metadata['install_name'] == expected['install_name']
    assert metadata['repair_action'] == 'aligned-shadow-install'
    assert (aligned_dir / 'INSTALLATION_COMPLETE').exists()
    raw = subprocess.run(
        [sys.executable, '-m', 'playwright', 'install', '--list'],
        env={**dict(os.environ), 'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
        capture_output=True,
        text=True,
        check=False,
    )
    assert raw.returncode == 0
    assert str(aligned_dir) in raw.stdout


def test_repair_playwright_cache_writes_missing_installation_marker(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    install = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        metadata={'version': '145.0.7632.6', 'revision': '1208', 'source': 'archive-import'},
    )
    marker_path = Path(str(install['marker_state']['marker_path']))
    marker_path.unlink()
    result = repair_playwright_cache(
        root=tmp_path / 'pw',
        env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
        platform='linux64',
        apply=True,
        write_missing_markers=True,
    )
    assert result['ok'] is True
    assert any(item.get('kind') == 'write-installation-marker' and item.get('changed') for item in result['results'])
    assert marker_path.exists()


def test_playwright_install_list_prepares_cache_root(tmp_path: Path) -> None:
    report = playwright_install_list(root=tmp_path / 'pw', timeout=5)
    assert report['returncode'] == 0
    assert report['links_state']['links_dir_exists'] is True
    assert report['links_state']['registry_link_exists'] is True
    assert (tmp_path / 'pw' / '.links').is_dir()


def test_install_archive_registers_cache_for_raw_playwright_install_list(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    result = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        metadata={'version': '145.0.7632.6', 'revision': '1208', 'source': 'archive-import'},
        env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
    )
    raw = subprocess.run(
        [sys.executable, '-m', 'playwright', 'install', '--list'],
        env={**dict(os.environ), 'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw')},
        capture_output=True,
        text=True,
        check=False,
    )
    assert raw.returncode == 0
    assert str(Path(result['install_dir'])) in raw.stdout
    assert 'Playwright version:' in raw.stdout


def test_install_archive_skip_still_repairs_registry_link(tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    first = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        metadata={'version': '145.0.7632.6', 'revision': '1208', 'source': 'archive-import'},
    )
    registry_link_path = Path(str(first['registry_link_state']['registry_link_path']))
    registry_link_path.unlink()
    second = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        metadata={'version': '145.0.7632.6', 'revision': '1208', 'source': 'archive-import'},
    )
    assert second['skipped'] is True
    assert second['marker_state']['marker_exists'] is True
    assert second['registry_link_state']['registry_link_exists'] is True


def test_import_cft_skip_still_repairs_installation_marker(tmp_path: Path) -> None:
    cft_root = tmp_path / 'cft'
    cft_dir = cft_root / '146.0.7680.66' / 'chrome-linux64'
    cft_dir.mkdir(parents=True)
    (cft_dir / 'chrome').write_text('#!/bin/sh\necho cft\n', encoding='utf-8')
    first = import_cft_into_playwright_cache(cft_root=cft_root, playwright_root=tmp_path / 'pw', platform='linux64')
    marker_path = Path(str(first['marker_state']['marker_path']))
    marker_path.unlink()
    second = import_cft_into_playwright_cache(cft_root=cft_root, playwright_root=tmp_path / 'pw', platform='linux64')
    assert second['skipped'] is True
    assert second['marker_state']['marker_exists'] is True
    assert marker_path.exists()


def test_sync_playwright_browser_packages_already_aligned_repairs_marker(monkeypatch, tmp_path: Path) -> None:
    install_dir = tmp_path / 'pw' / 'chromium-1208' / 'chrome-linux64'
    install_dir.mkdir(parents=True)
    (install_dir / 'chrome').write_text('#!/bin/sh\necho chrome\n', encoding='utf-8')
    (install_dir.parent / 'install.json').write_text(json.dumps({'version': '145.0.7632.6', 'revision': '1208', 'source': 'archive-import'}) + '\n', encoding='utf-8')
    monkeypatch.setitem(
        sync_playwright_browser_packages.__globals__,
        'expected_playwright_browser_packages',
        lambda **kwargs: [
            {
                'package_name': 'chromium',
                'install_name': 'chromium-1208',
                'version': '145.0.7632.6',
                'revision': '1208',
            },
        ],
    )
    report = sync_playwright_browser_packages(root=tmp_path / 'pw', platform='linux64')
    result = report['results'][0]
    assert result['action'] == 'already-aligned'
    assert result['marker_state']['marker_exists'] is True
    assert (install_dir.parent / 'INSTALLATION_COMPLETE').exists()


def test_install_playwright_browser_archive_prefers_expected_install_name(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    monkeypatch.setitem(install_playwright_browser_archive.__globals__, 'expected_playwright_package', lambda **kwargs: {'install_name': 'chromium-1208'})
    result = install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path / 'pw',
        metadata={'version': '145.0.7632.6', 'source': 'archive-import'},
    )
    assert result['install_name'] == 'chromium-1208'


def test_import_cft_into_playwright_cache_uses_expected_playwright_install_name(monkeypatch, tmp_path: Path) -> None:
    cft_root = tmp_path / 'cft'
    cft_dir = cft_root / '146.0.7680.66' / 'chrome-linux64'
    cft_dir.mkdir(parents=True)
    (cft_dir / 'chrome').write_text('#!/bin/sh\necho cft\n', encoding='utf-8')
    monkeypatch.setitem(import_cft_into_playwright_cache.__globals__, 'expected_playwright_package', lambda **kwargs: {'install_name': 'chromium-1208'})
    result = import_cft_into_playwright_cache(cft_root=cft_root, playwright_root=tmp_path / 'pw', platform='linux64')
    assert result['install_name'] == 'chromium-1208'


def test_local_playwright_browser_installations_support_headless_shell_package(tmp_path: Path) -> None:
    install_dir = tmp_path / 'chromium_headless_shell-1208' / 'chrome-headless-shell-linux64'
    install_dir.mkdir(parents=True)
    (install_dir / 'chrome-headless-shell').write_text('', encoding='utf-8')
    installs = local_playwright_browser_installations(root=tmp_path, platform='linux64', package_name=PLAYWRIGHT_HEADLESS_SHELL_PACKAGE)
    assert installs[0]['package_name'] == 'chromium_headless_shell'


def test_sync_playwright_browser_packages_uses_archives_for_expected_packages(monkeypatch, tmp_path: Path) -> None:
    chrome_archive = tmp_path / 'chrome-linux64.zip'
    headless_archive = tmp_path / 'chrome-headless-shell-linux64.zip'
    make_browser_archive(chrome_archive)
    make_headless_shell_archive(headless_archive)
    monkeypatch.setitem(
        sync_playwright_browser_packages.__globals__,
        'expected_playwright_browser_packages',
        lambda **kwargs: [
            {
                'package_name': 'chromium',
                'install_name': 'chromium-1208',
                'version': '145.0.7632.6',
                'revision': '1208',
            },
            {
                'package_name': 'chromium_headless_shell',
                'install_name': 'chromium_headless_shell-1208',
                'version': '145.0.7632.6',
                'revision': '1208',
            },
        ],
    )

    report = sync_playwright_browser_packages(
        root=tmp_path / 'pw',
        platform='linux64',
        include_headless_shell=True,
        archive_paths=[chrome_archive, headless_archive],
    )

    assert report['ok'] is True
    actions = {item['package_name']: item['action'] for item in report['results']}
    assert actions['chromium'] == 'archive-sync'
    assert actions['chromium_headless_shell'] == 'archive-sync'
    assert (tmp_path / 'pw' / 'chromium-1208' / 'chrome-linux64' / 'chrome').exists()
    assert (tmp_path / 'pw' / 'chromium_headless_shell-1208' / 'chrome-headless-shell-linux64' / 'chrome-headless-shell').exists()


def test_sync_playwright_browser_packages_uses_same_version_local_cft(monkeypatch, tmp_path: Path) -> None:
    cft_root = tmp_path / 'cft'
    chrome_dir = cft_root / '145.0.7632.6' / 'chrome-linux64'
    shell_dir = cft_root / '145.0.7632.6' / 'chrome-headless-shell-linux64'
    chrome_dir.mkdir(parents=True)
    shell_dir.mkdir(parents=True)
    (chrome_dir / 'chrome').write_text('#!/bin/sh\necho chrome\n', encoding='utf-8')
    (shell_dir / 'chrome-headless-shell').write_text('#!/bin/sh\necho shell\n', encoding='utf-8')
    monkeypatch.setitem(
        sync_playwright_browser_packages.__globals__,
        'expected_playwright_browser_packages',
        lambda **kwargs: [
            {
                'package_name': 'chromium',
                'install_name': 'chromium-1208',
                'version': '145.0.7632.6',
                'revision': '1208',
            },
            {
                'package_name': 'chromium_headless_shell',
                'install_name': 'chromium_headless_shell-1208',
                'version': '145.0.7632.6',
                'revision': '1208',
            },
        ],
    )

    report = sync_playwright_browser_packages(
        root=tmp_path / 'pw',
        cft_root=cft_root,
        platform='linux64',
        include_headless_shell=True,
    )

    assert report['ok'] is True
    actions = {item['package_name']: item['action'] for item in report['results']}
    assert actions['chromium'] == 'cft-sync'
    assert actions['chromium_headless_shell'] == 'cft-sync'
    assert (tmp_path / 'pw' / 'chromium-1208' / 'chrome-linux64' / 'chrome').exists()
    assert (tmp_path / 'pw' / 'chromium_headless_shell-1208' / 'chrome-headless-shell-linux64' / 'chrome-headless-shell').exists()


def test_playwright_install_dry_run_reports_timeout(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(kwargs.get('args') or args[0], kwargs.get('timeout') or 1.5, output='partial stdout', stderr='partial stderr')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    from playwright_browsers import playwright_install_dry_run

    report = playwright_install_dry_run(env={PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV: '1.5'}, timeout=None)
    assert report['timed_out'] is True
    assert report['stdout'] == 'partial stdout'
    assert report['stderr'] == 'partial stderr'
    assert 'timed out' in (report['error'] or '')


def test_discover_playwright_browser_install_survives_dry_run_timeout_with_cached_bundle(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path,
        install_name='chromium-cft-145.0.7632.6',
        metadata={'version': '145.0.7632.6', 'source': 'archive-import'},
    )
    monkeypatch.setitem(
        discover_playwright_browser_install.__globals__,
        'playwright_install_dry_run',
        lambda **kwargs: {
            'available': True,
            'module_origin': '/tmp/playwright',
            'import_error': None,
            'command': ['python', '-m', 'playwright', 'install', '--dry-run', 'chromium'],
            'ok': False,
            'returncode': None,
            'stdout': '',
            'stderr': '',
            'packages': [],
            'timeout_seconds': 1.5,
            'timed_out': True,
            'error': 'playwright install --dry-run timed out after 1.5 seconds',
        },
    )
    install = discover_playwright_browser_install(env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path)}, playwright_available=True, import_error=None, dry_run_timeout=1.5)
    assert install['bundled_executable_exists'] is True
    assert install['launch_strategy'] == 'bundled-executable'
    assert install['dry_run']['timed_out'] is True
    assert install['discovery_notes']


def test_discover_playwright_browser_install_includes_install_list_report(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / 'chrome-linux64.zip'
    make_browser_archive(archive)
    install_playwright_browser_archive(
        archive_path=archive,
        root=tmp_path,
        install_name='chromium-1208',
        metadata={'version': '145.0.7632.6', 'source': 'archive-import'},
    )
    monkeypatch.setitem(
        discover_playwright_browser_install.__globals__,
        'playwright_install_list',
        lambda **kwargs: {
            'ok': True,
            'groups': parse_playwright_install_list(LIST_SAMPLE),
            'links_state': {'links_dir_created': True, 'links_dir': str(tmp_path / '.links')},
            'timeout_seconds': 5,
            'timed_out': False,
            'error': None,
        },
    )
    monkeypatch.setitem(
        discover_playwright_browser_install.__globals__,
        'playwright_install_dry_run',
        lambda **kwargs: {
            'available': True,
            'module_origin': '/tmp/playwright',
            'import_error': None,
            'command': ['python', '-m', 'playwright', 'install', '--dry-run', 'chromium'],
            'ok': False,
            'returncode': None,
            'stdout': '',
            'stderr': '',
            'packages': [],
            'timeout_seconds': 1.5,
            'timed_out': True,
            'error': 'playwright install --dry-run timed out after 1.5 seconds',
        },
    )
    install = discover_playwright_browser_install(env={'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path)}, playwright_available=True, import_error=None)
    assert install['install_list']['groups'][0]['playwright_version'] == '1.53.0'
    assert any('install --list' in note for note in install['discovery_notes'])


@contextmanager
def serve_directory(root: Path):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f'http://{host}:{port}'
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_download_playwright_browser_archive_uses_fallback_url(tmp_path: Path) -> None:
    server_root = tmp_path / 'server'
    server_root.mkdir()
    archive = server_root / 'chrome-linux64.zip'
    make_browser_archive(archive)
    expected = {
        'package_name': 'chromium',
        'install_name': 'chromium-1208',
        'download_url': '',
        'download_fallbacks': [],
    }
    with serve_directory(server_root) as base_url:
        expected['download_url'] = f'{base_url}/missing.zip'
        expected['download_fallbacks'] = [f'{base_url}/chrome-linux64.zip']
        result = download_playwright_browser_archive(
            expected_package=expected,
            download_dir=tmp_path / 'downloads',
            timeout=5,
        )
    assert result['ok'] is True
    assert result['source_url'] == expected['download_fallbacks'][0]
    assert Path(result['archive_path']).exists()
    assert result['attempts'][0]['ok'] is False
    assert result['attempts'][1]['ok'] is True


def test_sync_playwright_browser_packages_downloads_expected_package(monkeypatch, tmp_path: Path) -> None:
    server_root = tmp_path / 'server'
    server_root.mkdir()
    archive = server_root / 'chrome-linux64.zip'
    make_browser_archive(archive)
    with serve_directory(server_root) as base_url:
        monkeypatch.setitem(
            sync_playwright_browser_packages.__globals__,
            'expected_playwright_browser_packages',
            lambda **kwargs: [
                {
                    'package_name': 'chromium',
                    'install_name': 'chromium-1208',
                    'version': '145.0.7632.6',
                    'revision': '1208',
                    'download_url': f'{base_url}/chrome-linux64.zip',
                    'download_fallbacks': [],
                },
            ],
        )
        report = sync_playwright_browser_packages(
            root=tmp_path / 'pw',
            platform='linux64',
            download_missing=True,
            download_dir=tmp_path / 'downloads',
            download_timeout=5,
        )

    assert report['ok'] is True
    result = report['results'][0]
    assert result['action'] == 'download-sync'
    assert Path(result['sync_result']['executable']).exists()
    metadata = json.loads(Path(result['sync_result']['metadata_path']).read_text(encoding='utf-8'))
    assert metadata['source'] == 'download-sync'
    assert metadata['download_url'] == f'{base_url}/chrome-linux64.zip'


def test_sync_playwright_browser_packages_reports_download_error(monkeypatch, tmp_path: Path) -> None:
    server_root = tmp_path / 'server'
    server_root.mkdir()
    with serve_directory(server_root) as base_url:
        monkeypatch.setitem(
            sync_playwright_browser_packages.__globals__,
            'expected_playwright_browser_packages',
            lambda **kwargs: [
                {
                    'package_name': 'chromium',
                    'install_name': 'chromium-1208',
                    'version': '145.0.7632.6',
                    'revision': '1208',
                    'download_url': f'{base_url}/missing.zip',
                    'download_fallbacks': [],
                },
            ],
        )
        report = sync_playwright_browser_packages(
            root=tmp_path / 'pw',
            platform='linux64',
            download_missing=True,
            download_dir=tmp_path / 'downloads',
            download_timeout=5,
        )

    assert report['ok'] is False
    result = report['results'][0]
    assert result['action'] == 'download-error'
    assert result['download_result']['attempts']
    assert result['download_result']['attempts'][0]['ok'] is False
    assert result['download_result']['error']


def test_download_playwright_browser_archive_rejects_non_zip_payload(tmp_path: Path) -> None:
    server_root = tmp_path / 'server'
    server_root.mkdir()
    (server_root / 'chrome-linux64.zip').write_text('not really a zip', encoding='utf-8')
    expected = {
        'package_name': 'chromium',
        'install_name': 'chromium-1208',
        'download_url': '',
        'download_fallbacks': [],
    }
    with serve_directory(server_root) as base_url:
        expected['download_url'] = f'{base_url}/chrome-linux64.zip'
        result = download_playwright_browser_archive(
            expected_package=expected,
            download_dir=tmp_path / 'downloads',
            timeout=5,
        )
    assert result['ok'] is False
    assert 'not a zip archive' in (result['error'] or '')
    assert not Path(result['archive_path']).exists()


def test_playwright_browser_choice_defaults_to_chromium_targets_for_bundled_cache() -> None:
    choice = playwright_browser_choice({
        'launch_strategy': 'bundled-executable',
        'bundled_executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
        'bundled_install': {
            'executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
            'package_name': 'chromium',
            'version': '145.0.7632.6',
            'source': 'cache-scan',
            'install_name': 'chromium-1208',
        },
    })
    assert choice['browser_family'] == 'chromium'
    assert choice['native_messaging_targets'] == ['chromium']


def test_playwright_browser_choice_respects_cft_imported_bundle_targets() -> None:
    choice = playwright_browser_choice({
        'launch_strategy': 'bundled-executable',
        'bundled_executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
        'bundled_install': {
            'executable': '/tmp/pw/chromium-1208/chrome-linux64/chrome',
            'package_name': 'chromium',
            'version': '146.0.7680.66',
            'source': 'chrome-for-testing-import',
            'install_name': 'chromium-1208',
        },
    })
    assert choice['browser_family'] == 'chrome-for-testing'
    assert choice['native_messaging_targets'] == ['chrome-for-testing']


def test_ensure_playwright_channel_ready_repairs_and_syncs_drifted_cache(monkeypatch, tmp_path: Path) -> None:
    fake_site, module_origin = make_fake_playwright_module(tmp_path / 'fake-site')
    monkeypatch.setattr(pb, 'playwright_import_state', lambda: {'available': True, 'module_origin': str(module_origin), 'import_error': None})
    env = {'PLAYWRIGHT_BROWSERS_PATH': str(tmp_path / 'pw'), 'PYTHONPATH': str(fake_site)}
    expected = expected_playwright_package(package_name='chromium', env=env)
    assert expected is not None
    shadow = make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name='chromium-shadow-145.0.7632.6',
        version=str(expected['version']),
        revision=str(expected['revision']),
    )
    report = ensure_playwright_channel_ready(
        root=tmp_path / 'pw',
        env=env,
        platform='linux64',
    )
    assert shadow.exists() is False
    assert report['ok'] is True
    assert report['changed'] is True
    assert report['before']['extension_launch_plan']['channel_ready'] is False
    assert report['after']['extension_launch_plan']['channel_ready'] is True
    assert report['after']['extension_launch_plan']['strategy'] == 'playwright-channel'
    assert (tmp_path / 'pw' / str(expected['install_name']) / 'INSTALLATION_COMPLETE').exists()


def test_playwright_browsers_script_ensure_channel_ready_reports_channel_ready(tmp_path: Path) -> None:
    fake_site, _ = make_fake_playwright_module(tmp_path / 'fake-site')
    env = dict(os.environ)
    env['PYTHONPATH'] = str(fake_site) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    make_shadow_playwright_install(
        tmp_path / 'pw',
        install_name='chromium-shadow-145.0.7632.6',
        version='145.0.7632.6',
        revision='1208',
    )
    output = subprocess.check_output([
        sys.executable,
        str(ROOT / 'scripts' / 'playwright-browsers.py'),
        'ensure-channel-ready',
        '--root',
        str(tmp_path / 'pw'),
    ], text=True, env=env)
    data = json.loads(output)
    assert data['ok'] is True
    assert data['after']['extension_launch_plan']['channel_ready'] is True
    assert data['after']['extension_launch_plan']['strategy'] == 'playwright-channel'

