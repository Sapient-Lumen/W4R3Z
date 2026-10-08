from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from urllib.parse import urlsplit
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from browser_binaries import augment_browser_choice, detect_cft_platform, executable_relpath, latest_local_cft_install, local_cft_installations, version_key

ORIGINAL_HOME = Path(os.environ.get('HOME', str(Path.home())))
DEFAULT_PLAYWRIGHT_BROWSERS_ROOTS = [ORIGINAL_HOME / '.cache' / 'ms-playwright', Path('/home/oai/.cache/ms-playwright')]
PLAYWRIGHT_INSTALL_COMMAND = 'python -m playwright install chromium'
PLAYWRIGHT_INSTALL_WITH_DEPS_COMMAND = 'python -m playwright install --with-deps chromium'
PLAYWRIGHT_INSTALL_DRY_RUN_COMMAND = 'python -m playwright install --dry-run chromium'
PLAYWRIGHT_INSTALL_LIST_COMMAND = 'python -m playwright install --list'
PLAYWRIGHT_SYNC_COMMAND = 'python scripts/playwright-browsers.py sync --package chromium'
PLAYWRIGHT_DOWNLOAD_COMMAND = 'python scripts/playwright-browsers.py sync --package chromium --download'
PLAYWRIGHT_SYNC_WITH_HEADLESS_SHELL_COMMAND = 'python scripts/playwright-browsers.py sync --package chromium --include-headless-shell'
PLAYWRIGHT_DOWNLOAD_WITH_HEADLESS_SHELL_COMMAND = 'python scripts/playwright-browsers.py sync --package chromium --include-headless-shell --download'
PLAYWRIGHT_ENSURE_CHANNEL_READY_COMMAND = 'python scripts/playwright-browsers.py ensure-channel-ready'
PLAYWRIGHT_ENSURE_CHANNEL_READY_WITH_HEADLESS_SHELL_COMMAND = 'python scripts/playwright-browsers.py ensure-channel-ready --include-headless-shell'
PLAYWRIGHT_ALLOW_SYSTEM_ENV = 'GLASSTTY_PLAYWRIGHT_ALLOW_SYSTEM_EXECUTABLE'
PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV = 'GLASSTTY_PLAYWRIGHT_DRY_RUN_TIMEOUT'
PLAYWRIGHT_INSTALL_LIST_TIMEOUT_ENV = 'GLASSTTY_PLAYWRIGHT_INSTALL_LIST_TIMEOUT'
PLAYWRIGHT_DOWNLOAD_TIMEOUT_ENV = 'GLASSTTY_PLAYWRIGHT_DOWNLOAD_TIMEOUT'
PLAYWRIGHT_INSTALLATION_COMPLETE_MARKER = 'INSTALLATION_COMPLETE'
PLAYWRIGHT_BROWSER_NAME = 'chromium'
PLAYWRIGHT_BUNDLED_EXECUTABLE_BINARY = 'chrome'
PLAYWRIGHT_EXTENSION_PACKAGE = 'chromium'
PLAYWRIGHT_EXTENSION_CHANNEL = 'chromium'
PLAYWRIGHT_HEADLESS_SHELL_PACKAGE = 'chromium_headless_shell'
PLAYWRIGHT_PACKAGE_SPECS: dict[str, dict[str, Any]] = {
    PLAYWRIGHT_EXTENSION_PACKAGE: {
        'package_name': PLAYWRIGHT_EXTENSION_PACKAGE,
        'display_name': 'Chrome for Testing',
        'playwright_name': 'chromium',
        'install_prefixes': ('chromium-', 'chromium-cft-'),
        'binary': 'chrome',
        'supports_extension_lane': True,
    },
    PLAYWRIGHT_HEADLESS_SHELL_PACKAGE: {
        'package_name': PLAYWRIGHT_HEADLESS_SHELL_PACKAGE,
        'display_name': 'Chrome Headless Shell',
        'playwright_name': 'chromium-headless-shell',
        'install_prefixes': ('chromium_headless_shell-',),
        'binary': 'chrome-headless-shell',
        'supports_extension_lane': False,
    },
}
DRY_RUN_HEADER_RE = re.compile(r'^(?P<display>.+?)\s+(?P<version>\d+(?:\.\d+)+)\s+\(playwright\s+(?P<playwright_name>[a-z0-9_-]+)\s+v(?P<revision>\d+)\)$', re.IGNORECASE)


class PlaywrightBrowserError(RuntimeError):
    pass


def playwright_import_state() -> dict[str, Any]:
    spec = importlib.util.find_spec('playwright')
    return {
        'available': spec is not None,
        'module_origin': spec.origin if spec else None,
        'import_error': None if spec else 'playwright module is not installed',
    }


def bool_from_env(value: str | None) -> bool:
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}


def playwright_browsers_root(*, env: dict[str, str] | None = None) -> Path:
    env = env or os.environ
    explicit = env.get('PLAYWRIGHT_BROWSERS_PATH')
    if explicit and explicit != '0':
        return Path(explicit).expanduser()
    return DEFAULT_PLAYWRIGHT_BROWSERS_ROOTS[0]


def existing_playwright_browsers_path(*, env: dict[str, str] | None = None) -> Path | None:
    env = env or os.environ
    explicit = env.get('PLAYWRIGHT_BROWSERS_PATH')
    candidates: list[Path] = []
    if explicit and explicit != '0':
        candidates.append(Path(explicit).expanduser())
    seen: set[str] = set()
    for candidate in [*candidates, *DEFAULT_PLAYWRIGHT_BROWSERS_ROOTS]:
        marker = str(candidate)
        if marker in seen:
            continue
        seen.add(marker)
        if candidate.exists():
            return candidate
    return None


def playwright_package_spec(package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE) -> dict[str, Any]:
    try:
        return PLAYWRIGHT_PACKAGE_SPECS[package_name]
    except KeyError as exc:
        raise PlaywrightBrowserError(f'unsupported Playwright browser package: {package_name!r}') from exc


def playwright_binary_for_package(package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE) -> str:
    return str(playwright_package_spec(package_name)['binary'])


def playwright_relpath(package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, *, platform: str | None = None) -> Path:
    return executable_relpath(playwright_binary_for_package(package_name), platform or detect_cft_platform())


def normalize_playwright_package_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().lower().replace('-', '_')
    if cleaned in {'chromium', 'chrome', PLAYWRIGHT_EXTENSION_PACKAGE}:
        return PLAYWRIGHT_EXTENSION_PACKAGE
    if cleaned in {'chromium_headless_shell', 'chrome_headless_shell', 'headless_shell', PLAYWRIGHT_HEADLESS_SHELL_PACKAGE}:
        return PLAYWRIGHT_HEADLESS_SHELL_PACKAGE
    return None


def detect_archive_package(*, archive_path: Path | str, platform: str | None = None) -> str | None:
    archive_path = Path(archive_path).expanduser().resolve()
    platform = platform or detect_cft_platform()
    matches: list[str] = []
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
    for package_name in PLAYWRIGHT_PACKAGE_SPECS:
        rel = str(playwright_relpath(package_name, platform=platform)).replace('\\', '/')
        if rel in names:
            matches.append(package_name)
    if len(matches) == 1:
        return matches[0]
    return None


def playwright_install_name(*, package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, revision: str | None = None, version: str | None = None, label: str | None = None, expected_install_name: str | None = None) -> str:
    spec = playwright_package_spec(package_name)
    prefix = str(spec['install_prefixes'][0])
    if expected_install_name:
        return expected_install_name
    if revision:
        return f'{prefix}{revision}'
    if version:
        version_token = version if package_name == PLAYWRIGHT_EXTENSION_PACKAGE else version.replace('.', '_')
        return f'{prefix}{version_token}'
    if label:
        cleaned = ''.join(ch if ch.isalnum() or ch in {'-', '_', '.'} else '-' for ch in label).strip('-') or 'local'
        if not cleaned.startswith(prefix):
            cleaned = f'{prefix}{cleaned}'
        return cleaned
    return f'{prefix}local'


def _install_sort_key(item: dict[str, Any]) -> tuple[tuple[int, ...], str, str]:
    version = str(item.get('version') or '')
    revision = str(item.get('revision') or '')
    install_name = str(item.get('install_name') or '')
    if version:
        version_sort = version_key(version)
    else:
        version_sort = tuple(-1 for _ in range(4))
    return (version_sort, revision, install_name)


def parse_playwright_install_dry_run(text: str) -> list[dict[str, Any]]:
    packages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            current = None
            continue
        header = DRY_RUN_HEADER_RE.match(stripped)
        if header:
            playwright_name = header.group('playwright_name')
            package_name = normalize_playwright_package_name(playwright_name)
            current = {
                'display_name': header.group('display'),
                'version': header.group('version'),
                'revision': header.group('revision'),
                'playwright_name': playwright_name,
                'package_name': package_name,
                'install_location': None,
                'install_name': None,
                'download_url': None,
                'download_fallbacks': [],
            }
            packages.append(current)
            continue
        if current is None:
            continue
        if stripped.startswith('Install location:'):
            value = stripped.split(':', 1)[1].strip()
            current['install_location'] = value
            current['install_name'] = Path(value).name if value else None
            continue
        if stripped.startswith('Download url:'):
            current['download_url'] = stripped.split(':', 1)[1].strip()
            continue
        if stripped.startswith('Download fallback'):
            current.setdefault('download_fallbacks', []).append(stripped.split(':', 1)[1].strip())
    return [pkg for pkg in packages if pkg.get('package_name') in PLAYWRIGHT_PACKAGE_SPECS]


def resolve_playwright_dry_run_timeout(*, env: dict[str, str] | None = None, timeout: float | None = 30.0) -> float | None:
    env = env or os.environ
    if timeout is not None:
        return timeout
    raw = env.get(PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV)
    if raw is None:
        return 30.0
    value = str(raw).strip().lower()
    if value in {'', 'none', 'null', 'off', 'false'}:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return 30.0


def resolve_playwright_install_list_timeout(*, env: dict[str, str] | None = None, timeout: float | None = 15.0) -> float | None:
    env = env or os.environ
    if timeout is not None:
        return timeout
    raw = env.get(PLAYWRIGHT_INSTALL_LIST_TIMEOUT_ENV)
    if raw is None:
        return 15.0
    value = str(raw).strip().lower()
    if value in {'', 'none', 'null', 'off', 'false'}:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return 15.0


def ensure_playwright_links_dir(root: Path | str) -> dict[str, Any]:
    resolved_root = Path(root).expanduser()
    links_dir = resolved_root / '.links'
    existed = links_dir.exists()
    error: str | None = None
    try:
        links_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # noqa: BLE001
        error = str(exc)
    return {
        'root': str(resolved_root),
        'links_dir': str(links_dir),
        'links_dir_exists': links_dir.exists(),
        'links_dir_created': links_dir.exists() and not existed,
        'error': error,
    }


def playwright_driver_package_path(*, module_origin: str | None = None) -> Path | None:
    origin = module_origin if module_origin is not None else str(playwright_import_state().get('module_origin') or '')
    if not origin:
        return None
    return Path(origin).resolve().parent / 'driver' / 'package'


def playwright_registry_link_name(package_path: Path | str) -> str:
    return hashlib.sha1(str(Path(package_path)).encode('utf-8')).hexdigest()


def playwright_installation_marker_path(install_dir: Path | str) -> Path:
    return Path(install_dir).expanduser() / PLAYWRIGHT_INSTALLATION_COMPLETE_MARKER


def playwright_installation_marker_required(*, package_name: str | None = None, revision: str | None = None) -> bool:
    normalized_package = normalize_playwright_package_name(package_name)
    if normalized_package is None:
        return False
    if normalized_package == PLAYWRIGHT_EXTENSION_PACKAGE:
        try:
            browser_revision = int(str(revision or '').strip())
        except ValueError:
            return True
        return browser_revision >= 786218 or browser_revision < 300000
    return True


def ensure_playwright_installation_marker(install_dir: Path | str, *, package_name: str | None = None, revision: str | None = None) -> dict[str, Any]:
    resolved_install_dir = Path(install_dir).expanduser().resolve()
    marker_path = playwright_installation_marker_path(resolved_install_dir)
    required = playwright_installation_marker_required(package_name=package_name, revision=revision)
    existed = marker_path.exists()
    error: str | None = None
    if required:
        try:
            resolved_install_dir.mkdir(parents=True, exist_ok=True)
            marker_path.touch(exist_ok=True)
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
    return {
        'install_dir': str(resolved_install_dir),
        'marker_path': str(marker_path),
        'marker_required': required,
        'marker_exists': marker_path.exists(),
        'marker_created': marker_path.exists() and not existed,
        'error': error,
    }


def ensure_playwright_registry_link(root: Path | str, *, package_path: Path | str | None = None, module_origin: str | None = None) -> dict[str, Any]:
    state = ensure_playwright_links_dir(root)
    links_dir = Path(str(state['links_dir']))
    resolved_package_path = Path(package_path).expanduser().resolve() if package_path is not None else playwright_driver_package_path(module_origin=module_origin)
    state.update({
        'registry_package_path': str(resolved_package_path) if resolved_package_path is not None else None,
        'registry_link_name': None,
        'registry_link_path': None,
        'registry_link_exists': False,
        'registry_link_created': False,
        'registry_link_updated': False,
        'registry_link_target': None,
    })
    if state.get('error'):
        return state
    if resolved_package_path is None:
        state['error'] = 'could not resolve Playwright driver package path for cache registry link'
        return state
    if not resolved_package_path.exists():
        state['error'] = f'Playwright driver package path does not exist: {resolved_package_path}'
        return state
    desired_target = str(resolved_package_path)
    link_name = playwright_registry_link_name(resolved_package_path)
    link_path = links_dir / link_name
    state['registry_link_name'] = link_name
    state['registry_link_path'] = str(link_path)
    previous_target: str | None = None
    if link_path.exists():
        try:
            previous_target = link_path.read_text(encoding='utf-8').strip() or None
        except Exception as exc:  # noqa: BLE001
            state['error'] = str(exc)
            return state
    try:
        if previous_target != desired_target:
            link_path.write_text(desired_target, encoding='utf-8')
    except Exception as exc:  # noqa: BLE001
        state['error'] = str(exc)
        return state
    state['registry_link_exists'] = link_path.exists()
    state['registry_link_created'] = link_path.exists() and previous_target is None
    state['registry_link_updated'] = link_path.exists() and previous_target not in {None, desired_target}
    state['registry_link_target'] = desired_target if link_path.exists() else previous_target
    return state




def load_playwright_browsers_json(package_path: Path | str) -> dict[str, Any]:
    resolved_package_path = Path(package_path).expanduser().resolve()
    browsers_json_path = resolved_package_path / 'browsers.json'
    report: dict[str, Any] = {
        'package_path': str(resolved_package_path),
        'browsers_json_path': str(browsers_json_path),
        'package_exists': resolved_package_path.exists(),
        'browsers_json_exists': browsers_json_path.exists(),
        'ok': False,
        'error': None,
        'browsers': [],
    }
    if not resolved_package_path.exists():
        report['error'] = f'Playwright package path does not exist: {resolved_package_path}'
        return report
    if not browsers_json_path.exists():
        report['error'] = f'Playwright browsers.json is missing: {browsers_json_path}'
        return report
    try:
        payload = json.loads(browsers_json_path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        return report
    browsers = payload.get('browsers') if isinstance(payload, dict) else None
    if not isinstance(browsers, list):
        report['error'] = f'Playwright browsers.json at {browsers_json_path} does not contain a browsers list'
        return report
    report['ok'] = True
    report['browsers'] = browsers
    return report


def referenced_playwright_browsers_for_package(root: Path | str, *, package_path: Path | str, platform: str | None = None) -> dict[str, Any]:
    resolved_root = Path(root).expanduser().resolve()
    resolved_platform = platform or detect_cft_platform()
    package_report = load_playwright_browsers_json(package_path)
    entries: list[dict[str, Any]] = []
    if package_report.get('ok'):
        for browser in package_report.get('browsers') or []:
            if not isinstance(browser, dict):
                continue
            package_name = normalize_playwright_package_name(str(browser.get('name') or ''))
            if package_name not in PLAYWRIGHT_PACKAGE_SPECS:
                continue
            revision = str(browser.get('revision') or '') or None
            version = str(browser.get('browserVersion') or '') or None
            install_name = playwright_install_name(package_name=package_name, revision=revision, version=version)
            install_dir = resolved_root / install_name
            executable = install_dir / playwright_relpath(package_name, platform=resolved_platform)
            marker_path = playwright_installation_marker_path(install_dir)
            marker_required = playwright_installation_marker_required(package_name=package_name, revision=revision)
            entries.append({
                'browser_name': browser.get('name'),
                'package_name': package_name,
                'display_name': playwright_package_spec(package_name)['display_name'],
                'revision': revision,
                'version': version,
                'install_name': install_name,
                'browser_path': str(install_dir),
                'browser_path_exists': install_dir.exists(),
                'executable': str(executable),
                'executable_exists': executable.exists(),
                'marker_path': str(marker_path),
                'marker_required': marker_required,
                'marker_exists': marker_path.exists(),
                'reference_dir': str(package_report['package_path']),
            })
    return {
        **package_report,
        'root': str(resolved_root),
        'platform': resolved_platform,
        'recognized_browser_entries': entries,
    }


def aggregate_playwright_browser_ownership(recognized_browser_entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    ownership_by_path: dict[str, dict[str, Any]] = {}
    for item in recognized_browser_entries:
        browser_path_raw = str(item.get('browser_path') or '').strip()
        if not browser_path_raw:
            continue
        browser_path = str(Path(browser_path_raw).resolve())
        owner = {
            'reference_dir': item.get('reference_dir'),
            'link_name': item.get('link_name'),
            'link_path': item.get('link_path'),
            'is_current_driver_package': bool(item.get('is_current_driver_package')),
        }
        aggregated = ownership_by_path.setdefault(browser_path, {
            'browser_path': browser_path,
            'install_name': str(item.get('install_name') or Path(browser_path).name),
            'package_name': item.get('package_name'),
            'display_name': item.get('display_name'),
            'revision': item.get('revision'),
            'version': item.get('version'),
            'browser_path_exists': bool(item.get('browser_path_exists')),
            'executable': item.get('executable'),
            'executable_exists': bool(item.get('executable_exists')),
            'marker_path': item.get('marker_path'),
            'marker_required': bool(item.get('marker_required')),
            'marker_exists': bool(item.get('marker_exists')),
            'owners': [],
        })
        if owner not in aggregated['owners']:
            aggregated['owners'].append(owner)
        aggregated['browser_path_exists'] = aggregated['browser_path_exists'] or bool(item.get('browser_path_exists'))
        aggregated['executable_exists'] = aggregated['executable_exists'] or bool(item.get('executable_exists'))
        aggregated['marker_exists'] = aggregated['marker_exists'] or bool(item.get('marker_exists'))
    ownership = list(ownership_by_path.values())
    for item in ownership:
        owners = list(item.get('owners') or [])
        current_owner_count = sum(1 for owner in owners if owner.get('is_current_driver_package'))
        item['owner_count'] = len(owners)
        item['current_driver_owner_count'] = current_owner_count
        item['owned_by_current_driver'] = current_owner_count > 0
        item['owned_only_by_foreign_clients'] = bool(owners) and current_owner_count == 0
        item['multi_client'] = len(owners) > 1
    ownership.sort(key=_install_sort_key, reverse=True)
    return ownership


def inspect_playwright_registry(root: Path | str, *, platform: str | None = None, module_origin: str | None = None) -> dict[str, Any]:
    resolved_root = Path(root).expanduser().resolve()
    resolved_platform = platform or detect_cft_platform()
    links_dir = resolved_root / '.links'
    current_package_path = playwright_driver_package_path(module_origin=module_origin)
    current_package_target = str(current_package_path.resolve()) if current_package_path is not None and current_package_path.exists() else None
    entries: list[dict[str, Any]] = []
    recognized_browser_entries: list[dict[str, Any]] = []
    broken_links: list[dict[str, Any]] = []
    if links_dir.exists():
        for link_path in sorted(links_dir.iterdir()):
            if not link_path.is_file():
                continue
            raw_target: str | None = None
            target_path: Path | None = None
            try:
                raw_target = link_path.read_text(encoding='utf-8').strip() or None
                target_path = Path(raw_target).expanduser().resolve() if raw_target else None
            except Exception as exc:  # noqa: BLE001
                entry = {
                    'link_name': link_path.name,
                    'link_path': str(link_path),
                    'target_path': None,
                    'target_exists': False,
                    'is_current_driver_package': False,
                    'error': str(exc),
                    'recognized_browser_entries': [],
                }
                entries.append(entry)
                broken_links.append(entry)
                continue
            package_report = referenced_playwright_browsers_for_package(resolved_root, package_path=target_path, platform=resolved_platform) if target_path is not None else {
                'ok': False,
                'error': 'registry link is empty',
                'package_path': None,
                'browsers_json_path': None,
                'package_exists': False,
                'browsers_json_exists': False,
                'recognized_browser_entries': [],
            }
            is_current_driver_package = bool(current_package_target and target_path and str(target_path) == current_package_target)
            entry_browser_entries: list[dict[str, Any]] = []
            for browser_entry in package_report.get('recognized_browser_entries') or []:
                if not isinstance(browser_entry, dict):
                    continue
                enriched = dict(browser_entry)
                enriched['link_name'] = link_path.name
                enriched['link_path'] = str(link_path)
                enriched['is_current_driver_package'] = is_current_driver_package
                entry_browser_entries.append(enriched)
            entry = {
                'link_name': link_path.name,
                'link_path': str(link_path),
                'target_path': str(target_path) if target_path is not None else raw_target,
                'target_exists': bool(target_path and target_path.exists()),
                'is_current_driver_package': is_current_driver_package,
                'error': package_report.get('error'),
                'package_exists': package_report.get('package_exists'),
                'browsers_json_exists': package_report.get('browsers_json_exists'),
                'recognized_browser_entries': entry_browser_entries,
            }
            entries.append(entry)
            recognized_browser_entries.extend(entry_browser_entries)
            if entry.get('error'):
                broken_links.append(entry)
    current_link_name = playwright_registry_link_name(current_package_target) if current_package_target else None
    browser_ownership = aggregate_playwright_browser_ownership(recognized_browser_entries)
    return {
        'root': str(resolved_root),
        'platform': resolved_platform,
        'links_dir': str(links_dir),
        'links_dir_exists': links_dir.exists(),
        'entries': entries,
        'recognized_browser_entries': recognized_browser_entries,
        'browser_ownership': browser_ownership,
        'broken_links': broken_links,
        'current_driver_package_path': current_package_target,
        'current_driver_link_name': current_link_name,
        'current_driver_linked': any(entry.get('is_current_driver_package') for entry in entries),
    }


def audit_playwright_cache(*, root: Path | str, env: dict[str, str] | None = None, platform: str | None = None, install_list: dict[str, Any] | None = None, prepared_install_list: dict[str, Any] | None = None, registry_report: dict[str, Any] | None = None) -> dict[str, Any]:
    resolved_root = Path(root).expanduser().resolve()
    resolved_platform = platform or detect_cft_platform()
    env = dict(env or os.environ)
    env['PLAYWRIGHT_BROWSERS_PATH'] = str(resolved_root)
    install_list_report = install_list if isinstance(install_list, dict) else playwright_install_list(env=env, root=resolved_root, ensure_links=False)
    prepared_install_list_report = prepared_install_list if isinstance(prepared_install_list, dict) else None
    registry = registry_report if isinstance(registry_report, dict) else inspect_playwright_registry(resolved_root, platform=resolved_platform)
    current_package = current_playwright_package_browsers(root=resolved_root, platform=resolved_platform)
    local_installations = local_playwright_browser_installations(root=resolved_root, platform=resolved_platform)
    local_by_path = {str(Path(item['install_dir']).resolve()): item for item in local_installations}
    browser_ownership = list(registry.get('browser_ownership') or [])
    ownership_by_path = {str(Path(item['browser_path']).resolve()): item for item in browser_ownership if item.get('browser_path')}
    registered_browser_entries = list(registry.get('recognized_browser_entries') or [])
    registered_by_path = {str(Path(item['browser_path']).resolve()): item for item in registered_browser_entries}
    install_list_entries = [entry for group in (install_list_report.get('groups') or []) for entry in (group.get('browser_entries') or []) if isinstance(entry, dict)]
    install_list_paths = {str(Path(entry['browser_path']).resolve()) for entry in install_list_entries if entry.get('browser_path')}

    shadow_installs: list[dict[str, Any]] = []
    foreign_only_installs: list[dict[str, Any]] = []
    multi_client_installs: list[dict[str, Any]] = []
    gc_retained_installs: list[dict[str, Any]] = []
    gc_candidate_installs: list[dict[str, Any]] = []
    for path, item in local_by_path.items():
        ownership = ownership_by_path.get(path)
        enriched = {
            **item,
            'owner_count': ownership.get('owner_count', 0) if ownership else 0,
            'current_driver_owner_count': ownership.get('current_driver_owner_count', 0) if ownership else 0,
            'owned_by_current_driver': ownership.get('owned_by_current_driver', False) if ownership else False,
            'owned_only_by_foreign_clients': ownership.get('owned_only_by_foreign_clients', False) if ownership else False,
            'install_list_visible': path in install_list_paths,
        }
        retained = bool(ownership and ownership.get('browser_path_exists') and (not ownership.get('marker_required') or ownership.get('marker_exists')))
        if retained:
            gc_retained_installs.append(enriched)
        else:
            gc_candidate_installs.append(enriched)
        if not ownership:
            shadow_installs.append(enriched)
            continue
        if ownership.get('owned_only_by_foreign_clients'):
            foreign_only_installs.append(enriched)
        if ownership.get('multi_client'):
            multi_client_installs.append(enriched)

    marker_missing_installs = [item for item in local_installations if item.get('marker_required') and not item.get('marker_exists')]
    stale_registered_browsers = [item for item in registered_browser_entries if not item.get('browser_path_exists')]
    marker_missing_registered_browsers = [item for item in registered_browser_entries if item.get('browser_path_exists') and item.get('marker_required') and not item.get('marker_exists')]
    unlisted_registered_browsers = [item for path, item in registered_by_path.items() if path not in install_list_paths and item.get('browser_path_exists')]
    installed_shadow_paths = {str(Path(item['install_dir']).resolve()) for item in shadow_installs}
    install_list_shadow_entries = [entry for entry in install_list_entries if str(Path(entry['browser_path']).resolve()) in installed_shadow_paths]
    current_unlinked_existing_browsers: list[dict[str, Any]] = []
    for entry in current_package.get('recognized_browser_entries') or []:
        if not entry.get('browser_path_exists'):
            continue
        path = str(Path(str(entry.get('browser_path'))).resolve())
        ownership = ownership_by_path.get(path)
        if ownership and ownership.get('owned_by_current_driver'):
            continue
        current_unlinked_existing_browsers.append({
            **entry,
            'owner_count': ownership.get('owner_count', 0) if ownership else 0,
            'current_driver_owner_count': ownership.get('current_driver_owner_count', 0) if ownership else 0,
            'owned_by_other_clients': bool(ownership and ownership.get('owner_count')),
            'install_list_visible': path in install_list_paths,
        })

    notes: list[str] = []
    if shadow_installs:
        notes.append(f'{len(shadow_installs)} on-disk Playwright browser install(s) are not referenced by any registry package link, so raw upstream install --list will ignore them and future install runs may garbage-collect them unless they are registered or PLAYWRIGHT_SKIP_BROWSER_GC=1 is set.')
    if current_unlinked_existing_browsers:
        notes.append(f'{len(current_unlinked_existing_browsers)} current-package browser install(s) exist on disk without the current Playwright package link; raw install --list and stale-browser ownership are therefore being driven by other clients or by no client at all.')
    if foreign_only_installs:
        notes.append(f'{len(foreign_only_installs)} on-disk Playwright browser install(s) are currently retained only by non-current Playwright package links; GlassTTY would need to repair the current registry link before treating that cache root as self-owned.')
    if marker_missing_registered_browsers:
        notes.append(f'{len(marker_missing_registered_browsers)} Playwright-recognized browser install(s) are missing INSTALLATION_COMPLETE, so a future Playwright install may treat them as stale and delete them unless the marker is restored or PLAYWRIGHT_SKIP_BROWSER_GC=1 is set.')
    elif marker_missing_installs:
        notes.append(f'{len(marker_missing_installs)} on-disk Playwright browser install(s) are missing INSTALLATION_COMPLETE, so they are vulnerable to future Playwright stale-browser cleanup unless the marker is restored or PLAYWRIGHT_SKIP_BROWSER_GC=1 is set.')
    if registry.get('broken_links'):
        notes.append(f'{len(registry.get("broken_links") or [])} Playwright registry link(s) are broken and may be removed by a future install run.')
    if stale_registered_browsers:
        notes.append(f'{len(stale_registered_browsers)} registry-tracked browser path(s) are missing on disk; Playwright will keep listing only existing paths and may clean the broken registrations during install.')
    if gc_candidate_installs:
        notes.append(f"{len(gc_candidate_installs)} local Playwright browser install(s) would currently be eligible for upstream stale-browser removal under Playwright's marker/link rules.")
    if not install_list_report.get('stdout') and install_list_report.get('returncode') == 0 and local_installations and not registered_browser_entries:
        notes.append('raw playwright install --list returned successfully with empty output while local browser directories exist; this cache root currently has no Playwright-recognized package references.')
    if install_list_report.get('returncode') != 0 and current_unlinked_existing_browsers:
        notes.append('The raw install --list view is currently unhealthy enough that GlassTTY would need to prepare the cache or repair the current package link before upstream tooling can enumerate browsers reliably.')

    return {
        'root': str(resolved_root),
        'platform': resolved_platform,
        'playwright_skip_browser_gc': bool_from_env(env.get('PLAYWRIGHT_SKIP_BROWSER_GC')),
        'install_list': install_list_report,
        'prepared_install_list': prepared_install_list_report,
        'registry': registry,
        'current_package': current_package,
        'local_installations': local_installations,
        'browser_ownership': browser_ownership,
        'shadow_installs': shadow_installs,
        'foreign_only_installs': foreign_only_installs,
        'multi_client_installs': multi_client_installs,
        'current_unlinked_existing_browsers': current_unlinked_existing_browsers,
        'gc_retained_installs': gc_retained_installs,
        'gc_candidate_installs': gc_candidate_installs,
        'marker_missing_installs': marker_missing_installs,
        'stale_registered_browsers': stale_registered_browsers,
        'marker_missing_registered_browsers': marker_missing_registered_browsers,
        'unlisted_registered_browsers': unlisted_registered_browsers,
        'install_list_shadow_entries': install_list_shadow_entries,
        'counts': {
            'local_installations': len(local_installations),
            'registered_browser_entries': len(registered_browser_entries),
            'browser_ownership_entries': len(browser_ownership),
            'shadow_installs': len(shadow_installs),
            'foreign_only_installs': len(foreign_only_installs),
            'multi_client_installs': len(multi_client_installs),
            'current_unlinked_existing_browsers': len(current_unlinked_existing_browsers),
            'gc_candidate_installs': len(gc_candidate_installs),
            'gc_retained_installs': len(gc_retained_installs),
            'marker_missing_installs': len(marker_missing_installs),
            'marker_missing_registered_browsers': len(marker_missing_registered_browsers),
            'broken_links': len(registry.get('broken_links') or []),
            'stale_registered_browsers': len(stale_registered_browsers),
            'unlisted_registered_browsers': len(unlisted_registered_browsers),
            'install_list_shadow_entries': len(install_list_shadow_entries),
        },
        'notes': notes,
    }


def current_playwright_package_browsers(*, root: Path | str, package_path: Path | str | None = None, platform: str | None = None, module_origin: str | None = None) -> dict[str, Any]:
    resolved_package_path = Path(package_path).expanduser().resolve() if package_path is not None else playwright_driver_package_path(module_origin=module_origin)
    if resolved_package_path is None:
        return {
            'ok': False,
            'error': 'could not resolve Playwright driver package path for current package browser expectations',
            'package_path': None,
            'recognized_browser_entries': [],
        }
    return referenced_playwright_browsers_for_package(root, package_path=resolved_package_path, platform=platform)


def plan_playwright_cache_repair(*, root: Path | str, env: dict[str, str] | None = None, platform: str | None = None, package_path: Path | str | None = None, audit_report: dict[str, Any] | None = None, install_list: dict[str, Any] | None = None) -> dict[str, Any]:
    resolved_root = Path(root).expanduser().resolve()
    resolved_platform = platform or detect_cft_platform()
    env = dict(env or os.environ)
    env['PLAYWRIGHT_BROWSERS_PATH'] = str(resolved_root)
    if isinstance(audit_report, dict):
        audit = audit_report
    else:
        audit = audit_playwright_cache(root=resolved_root, env=env, platform=resolved_platform, install_list=install_list)
    current_package = current_playwright_package_browsers(root=resolved_root, package_path=package_path, platform=resolved_platform)
    current_link_repair_needed = bool(current_package.get('package_path')) and not bool((audit.get('registry') or {}).get('current_driver_linked'))
    expected_by_package: dict[str, list[dict[str, Any]]] = {}
    for entry in current_package.get('recognized_browser_entries') or []:
        package_name = str(entry.get('package_name') or '')
        if package_name:
            expected_by_package.setdefault(package_name, []).append(entry)

    repairable_shadow_installs: list[dict[str, Any]] = []
    blocked_shadow_installs: list[dict[str, Any]] = []
    for shadow in audit.get('shadow_installs') or []:
        shadow_package = str(shadow.get('package_name') or '')
        candidates: list[dict[str, Any]] = []
        blocked_reason = 'no-current-package-match'
        for expected in expected_by_package.get(shadow_package, []):
            match_reasons: list[str] = []
            expected_install_name = str(expected.get('install_name') or '')
            if not expected_install_name or shadow.get('install_name') == expected_install_name:
                continue
            shadow_expected = str((shadow.get('metadata') or {}).get('expected_install_name') or '')
            if shadow_expected and shadow_expected == expected_install_name:
                match_reasons.append('expected-install-name')
            shadow_revision = str(shadow.get('revision') or '')
            expected_revision = str(expected.get('revision') or '')
            if shadow_revision and expected_revision and shadow_revision == expected_revision:
                match_reasons.append('revision-match')
            shadow_version = str(shadow.get('version') or '')
            expected_version = str(expected.get('version') or '')
            if shadow_version and expected_version and shadow_version == expected_version:
                match_reasons.append('version-match')
            if not match_reasons:
                blocked_reason = 'metadata-does-not-match-current-package'
                continue
            target_dir = resolved_root / expected_install_name
            candidates.append({
                'kind': 'align-shadow-install',
                'package_name': shadow_package,
                'package_display_name': shadow.get('package_display_name'),
                'source_install_name': shadow.get('install_name'),
                'source_install_dir': shadow.get('install_dir'),
                'source_metadata_path': shadow.get('metadata_path'),
                'target_install_name': expected_install_name,
                'target_install_dir': str(target_dir),
                'expected_entry': expected,
                'match_reasons': match_reasons,
                'target_exists': target_dir.exists(),
                'target_conflict': target_dir.exists() and str(target_dir.resolve()) != str(Path(str(shadow.get('install_dir'))).resolve()),
            })
        if len(candidates) == 1:
            repairable_shadow_installs.append(candidates[0])
        else:
            blocked_shadow_installs.append({
                'install_name': shadow.get('install_name'),
                'install_dir': shadow.get('install_dir'),
                'package_name': shadow_package,
                'reason': 'ambiguous-current-package-match' if len(candidates) > 1 else blocked_reason,
                'candidates': candidates,
            })

    broken_link_repairs = [{
        'kind': 'remove-broken-link',
        'link_name': item.get('link_name'),
        'link_path': item.get('link_path'),
        'target_path': item.get('target_path'),
        'error': item.get('error'),
    } for item in (audit.get('registry') or {}).get('broken_links') or []]
    missing_marker_repairs = [{
        'kind': 'write-installation-marker',
        'install_name': item.get('install_name'),
        'install_dir': item.get('install_dir'),
        'package_name': item.get('package_name'),
        'package_display_name': item.get('package_display_name'),
        'revision': item.get('revision'),
        'marker_path': item.get('marker_path'),
    } for item in audit.get('marker_missing_installs') or []]
    notes: list[str] = []
    if current_link_repair_needed:
        notes.append('The current Playwright driver package is not linked into this cache root yet, so raw install --list and stale-browser ownership may still be driven by other clients or fail outright until the current registry link is restored.')
    if repairable_shadow_installs:
        notes.append(f'{len(repairable_shadow_installs)} shadow install(s) can be aligned to the current Playwright package names without re-downloading the browser.')
    if broken_link_repairs:
        notes.append(f'{len(broken_link_repairs)} broken Playwright registry link(s) can be removed safely.')
    if missing_marker_repairs:
        notes.append(f'{len(missing_marker_repairs)} on-disk Playwright install(s) can be protected from stale-browser cleanup by restoring INSTALLATION_COMPLETE.')
    if blocked_shadow_installs:
        notes.append(f'{len(blocked_shadow_installs)} shadow install(s) do not match the current Playwright package expectations closely enough for automatic repair.')
    recommended_apply_command = f'python scripts/playwright-browsers.py repair --root {resolved_root} --apply --align-shadow-installs --prune-broken-links --write-missing-markers --pretty'
    return {
        'root': str(resolved_root),
        'platform': resolved_platform,
        'audit': audit,
        'current_package': current_package,
        'repairable_shadow_installs': repairable_shadow_installs,
        'blocked_shadow_installs': blocked_shadow_installs,
        'broken_link_repairs': broken_link_repairs,
        'missing_marker_repairs': missing_marker_repairs,
        'counts': {
            'current_link_repairs': 1 if current_link_repair_needed else 0,
            'repairable_shadow_installs': len(repairable_shadow_installs),
            'blocked_shadow_installs': len(blocked_shadow_installs),
            'broken_link_repairs': len(broken_link_repairs),
            'missing_marker_repairs': len(missing_marker_repairs),
        },
        'notes': notes,
        'recommended_apply_command': recommended_apply_command,
    }


def repair_playwright_cache(*, root: Path | str, env: dict[str, str] | None = None, platform: str | None = None, package_path: Path | str | None = None, align_shadow_installs: bool = False, prune_broken_links: bool = False, write_missing_markers: bool = False, apply: bool = False) -> dict[str, Any]:
    resolved_root = Path(root).expanduser().resolve()
    resolved_platform = platform or detect_cft_platform()
    env = dict(env or os.environ)
    env['PLAYWRIGHT_BROWSERS_PATH'] = str(resolved_root)
    if apply and not align_shadow_installs and not prune_broken_links and not write_missing_markers:
        align_shadow_installs = True
        prune_broken_links = True
        write_missing_markers = True
    plan = plan_playwright_cache_repair(root=resolved_root, env=env, platform=resolved_platform, package_path=package_path)
    results: list[dict[str, Any]] = []
    changed = False
    ok = True
    aligned_path_map: dict[str, str] = {}

    if apply:
        registry_link_state = ensure_playwright_registry_link(resolved_root, package_path=package_path)
        results.append({'kind': 'ensure-current-registry-link', 'ok': not bool(registry_link_state.get('error')), 'changed': bool(registry_link_state.get('links_dir_created') or registry_link_state.get('registry_link_created') or registry_link_state.get('registry_link_updated')), 'state': registry_link_state})
        changed = changed or bool(results[-1]['changed'])
        ok = ok and results[-1]['ok']

    if apply and prune_broken_links:
        for item in plan.get('broken_link_repairs') or []:
            link_path = Path(str(item.get('link_path')))
            result: dict[str, Any] = {'kind': 'remove-broken-link', 'link_name': item.get('link_name'), 'link_path': str(link_path), 'ok': False, 'changed': False, 'error': None}
            try:
                if link_path.exists():
                    link_path.unlink()
                    result['changed'] = True
                result['ok'] = True
            except Exception as exc:  # noqa: BLE001
                result['error'] = str(exc)
                ok = False
            results.append(result)
            changed = changed or bool(result['changed'])

    if apply and align_shadow_installs:
        for item in plan.get('repairable_shadow_installs') or []:
            source_dir = Path(str(item.get('source_install_dir')))
            target_dir = Path(str(item.get('target_install_dir')))
            result = {
                'kind': 'align-shadow-install',
                'source_install_name': item.get('source_install_name'),
                'source_install_dir': str(source_dir),
                'target_install_name': item.get('target_install_name'),
                'target_install_dir': str(target_dir),
                'match_reasons': list(item.get('match_reasons') or []),
                'ok': False,
                'changed': False,
                'error': None,
            }
            try:
                if not source_dir.exists():
                    raise PlaywrightBrowserError(f'shadow install directory is missing: {source_dir}')
                if target_dir.exists() and source_dir.resolve() != target_dir.resolve():
                    raise PlaywrightBrowserError(f'target Playwright install already exists: {target_dir}')
                if source_dir.resolve() != target_dir.resolve():
                    target_dir.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_dir), str(target_dir))
                    result['changed'] = True
                aligned_path_map[str(source_dir.resolve())] = str(target_dir.resolve())
                metadata_path = target_dir / 'install.json'
                metadata_payload: dict[str, Any] = {}
                if metadata_path.exists():
                    try:
                        payload = json.loads(metadata_path.read_text(encoding='utf-8'))
                        if isinstance(payload, dict):
                            metadata_payload = payload
                    except json.JSONDecodeError:
                        metadata_payload = {}
                metadata_payload['install_name'] = item.get('target_install_name')
                metadata_payload['expected_install_name'] = item.get('target_install_name')
                metadata_payload['package_name'] = item.get('package_name')
                metadata_payload['repair_action'] = 'aligned-shadow-install'
                if item.get('source_install_name') != item.get('target_install_name'):
                    metadata_payload['repaired_from_install_name'] = item.get('source_install_name')
                if 'source' not in metadata_payload:
                    metadata_payload['source'] = 'cache-repair'
                metadata_path.write_text(json.dumps(metadata_payload, indent=2) + '\n', encoding='utf-8')
                result['ok'] = True
            except Exception as exc:  # noqa: BLE001
                result['error'] = str(exc)
                ok = False
            results.append(result)
            changed = changed or bool(result['changed'])

    if apply and write_missing_markers:
        for item in plan.get('missing_marker_repairs') or []:
            original_install_dir = Path(str(item.get('install_dir')))
            resolved_install_dir = Path(aligned_path_map.get(str(original_install_dir.resolve()), str(original_install_dir)))
            marker_state = ensure_playwright_installation_marker(
                resolved_install_dir,
                package_name=str(item.get('package_name') or '') or None,
                revision=str(item.get('revision') or '') or None,
            )
            result = {
                'kind': 'write-installation-marker',
                'install_name': item.get('install_name'),
                'install_dir': str(resolved_install_dir),
                'marker_path': marker_state.get('marker_path'),
                'ok': not bool(marker_state.get('error')),
                'changed': bool(marker_state.get('marker_created')),
                'error': marker_state.get('error'),
                'state': marker_state,
            }
            ok = ok and result['ok']
            results.append(result)
            changed = changed or bool(result['changed'])

    post_audit = audit_playwright_cache(root=resolved_root, env=env, platform=resolved_platform) if apply else None
    return {
        'root': str(resolved_root),
        'platform': resolved_platform,
        'dry_run': not apply,
        'applied': apply,
        'requested_actions': {
            'align_shadow_installs': align_shadow_installs,
            'prune_broken_links': prune_broken_links,
            'write_missing_markers': write_missing_markers,
        },
        'ok': ok,
        'changed': changed,
        'plan': plan,
        'results': results,
        'post_audit': post_audit,
    }

def parse_playwright_install_list(text: str) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('Playwright version:'):
            version = stripped.split(':', 1)[1].strip()
            current = {
                'playwright_version': version,
                'browser_paths': [],
                'reference_dirs': [],
                'browser_entries': [],
            }
            groups.append(current)
            section = None
            continue
        if current is None:
            continue
        if stripped == 'Browsers:':
            section = 'browser_paths'
            continue
        if stripped == 'References:':
            section = 'reference_dirs'
            continue
        if section in {'browser_paths', 'reference_dirs'} and line.startswith('    '):
            current[section].append(stripped)
    for group in groups:
        browser_entries: list[dict[str, Any]] = []
        for browser_path in group.get('browser_paths') or []:
            install_name = Path(browser_path).name
            normalized_package = None
            for possible in PLAYWRIGHT_PACKAGE_SPECS:
                spec = playwright_package_spec(possible)
                if any(install_name.startswith(prefix) for prefix in spec['install_prefixes']):
                    normalized_package = possible
                    break
            browser_entries.append({
                'browser_path': browser_path,
                'install_name': install_name,
                'package_name': normalized_package,
                'display_name': playwright_package_spec(normalized_package)['display_name'] if normalized_package else None,
            })
        group['browser_entries'] = browser_entries
    return groups


def playwright_install_list(*, env: dict[str, str] | None = None, root: Path | None = None, python_executable: str | None = None, timeout: float | None = None, ensure_links: bool = True) -> dict[str, Any]:
    env = dict(env or os.environ)
    state = playwright_import_state()
    resolved_root = (root or Path(env.get('PLAYWRIGHT_BROWSERS_PATH') or playwright_browsers_root(env=env))).expanduser()
    env['PLAYWRIGHT_BROWSERS_PATH'] = str(resolved_root)
    resolved_timeout = resolve_playwright_install_list_timeout(env=env, timeout=timeout)
    driver_package_path = playwright_driver_package_path(module_origin=state.get('module_origin'))
    raw_links_dir = resolved_root / '.links'
    raw_link_name = playwright_registry_link_name(driver_package_path) if driver_package_path is not None else None
    raw_link_path = raw_links_dir / raw_link_name if raw_link_name is not None else None
    links_state = ensure_playwright_registry_link(resolved_root, package_path=driver_package_path) if ensure_links else {
        'root': str(resolved_root),
        'links_dir': str(raw_links_dir),
        'links_dir_exists': raw_links_dir.exists(),
        'links_dir_created': False,
        'registry_package_path': str(driver_package_path) if driver_package_path is not None else None,
        'registry_link_name': raw_link_name,
        'registry_link_path': str(raw_link_path) if raw_link_path is not None else None,
        'registry_link_exists': bool(raw_link_path and raw_link_path.exists()),
        'registry_link_created': False,
        'registry_link_updated': False,
        'registry_link_target': str(driver_package_path) if driver_package_path is not None else None,
        'error': None,
    }
    command = [python_executable or sys.executable, '-m', 'playwright', 'install', '--list']
    report: dict[str, Any] = {
        'available': bool(state['available']),
        'module_origin': state['module_origin'],
        'import_error': state['import_error'],
        'command': command,
        'root': str(resolved_root),
        'ok': False,
        'returncode': None,
        'stdout': '',
        'stderr': '',
        'groups': [],
        'timeout_seconds': resolved_timeout,
        'timed_out': False,
        'error': links_state.get('error'),
        'links_state': links_state,
        'ensure_links': ensure_links,
    }
    if not state['available']:
        return report
    if links_state.get('error'):
        return report
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=resolved_timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        report['timed_out'] = True
        report['stdout'] = exc.stdout or ''
        report['stderr'] = exc.stderr or ''
        report['error'] = f'playwright install --list timed out after {resolved_timeout} seconds'
        return report
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        return report
    report['returncode'] = result.returncode
    report['stdout'] = result.stdout
    report['stderr'] = result.stderr
    report['ok'] = result.returncode == 0
    combined_error_text = result.stderr or result.stdout
    if result.returncode != 0 and combined_error_text:
        report['error'] = combined_error_text.strip().splitlines()[-1]
    if result.returncode == 0:
        report['groups'] = parse_playwright_install_list(result.stdout)
        report['error'] = None
    return report


def resolve_playwright_download_timeout(*, env: dict[str, str] | None = None, timeout: float | None = 120.0) -> float | None:
    env = env or os.environ
    if timeout is not None:
        return timeout
    raw = env.get(PLAYWRIGHT_DOWNLOAD_TIMEOUT_ENV)
    if raw is None:
        return 120.0
    value = str(raw).strip().lower()
    if value in {'', 'none', 'null', 'off', 'false'}:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return 120.0


def playwright_package_download_urls(package: dict[str, Any] | None) -> list[str]:
    urls: list[str] = []
    if not isinstance(package, dict):
        return urls
    candidates: list[Any] = [package.get('download_url')]
    fallbacks = package.get('download_fallbacks')
    if isinstance(fallbacks, list):
        candidates.extend(fallbacks)
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        value = candidate.strip()
        if value and value not in urls:
            urls.append(value)
    return urls


def _playwright_download_filename(*, package_name: str, url: str) -> str:
    parsed = urlsplit(url)
    name = Path(parsed.path).name or f'{package_name}.zip'
    if not name.endswith('.zip'):
        name = f'{name}.zip'
    return name


def download_playwright_browser_archive(*, expected_package: dict[str, Any], package_name: str | None = None, archive_path: Path | None = None, download_dir: Path | None = None, env: dict[str, str] | None = None, force: bool = False, timeout: float | None = None) -> dict[str, Any]:
    resolved_package = normalize_playwright_package_name(package_name or str(expected_package.get('package_name') or ''))
    if not resolved_package:
        raise PlaywrightBrowserError(f'could not resolve Playwright browser package from expected package: {expected_package!r}')
    urls = playwright_package_download_urls(expected_package)
    resolved_timeout = resolve_playwright_download_timeout(env=env, timeout=timeout)
    report: dict[str, Any] = {
        'ok': False,
        'skipped': False,
        'package_name': resolved_package,
        'download_urls': urls,
        'attempts': [],
        'archive_path': None,
        'source_url': None,
        'timeout_seconds': resolved_timeout,
        'error': None,
        'temporary_archive': False,
    }
    if not urls:
        report['error'] = 'no download URL was available for this Playwright browser package'
        return report

    if archive_path is None:
        filename = _playwright_download_filename(package_name=resolved_package, url=urls[0])
        if download_dir is not None:
            target_dir = Path(download_dir).expanduser()
            target_dir.mkdir(parents=True, exist_ok=True)
            archive_path = target_dir / filename
        else:
            fd, tmp_name = tempfile.mkstemp(prefix=f'glasstty-{resolved_package}-', suffix=f'-{filename}')
            os.close(fd)
            archive_path = Path(tmp_name)
            try:
                archive_path.unlink()
            except OSError:
                pass
            report['temporary_archive'] = True
    archive_path = Path(archive_path).expanduser().resolve()
    report['archive_path'] = str(archive_path)

    if archive_path.exists() and not force and not report['temporary_archive']:
        report['ok'] = True
        report['skipped'] = True
        report['reason'] = 'already-downloaded'
        report['source_url'] = urls[0]
        return report

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = archive_path.with_name(f'{archive_path.name}.partial')
    for url in urls:
        attempt: dict[str, Any] = {'url': url, 'ok': False}
        report['attempts'].append(attempt)
        try:
            if partial_path.exists():
                partial_path.unlink()
            with urllib.request.urlopen(url, timeout=resolved_timeout) as response, partial_path.open('wb') as handle:
                shutil.copyfileobj(response, handle)
            partial_path.replace(archive_path)
            if not zipfile.is_zipfile(archive_path):
                raise PlaywrightBrowserError(f'downloaded file is not a zip archive: {archive_path}')
        except Exception as exc:  # noqa: BLE001
            attempt['error'] = str(exc)
            attempt['error_type'] = type(exc).__name__
            report['error'] = str(exc)
            try:
                if partial_path.exists():
                    partial_path.unlink()
                if archive_path.exists() and not zipfile.is_zipfile(archive_path):
                    archive_path.unlink()
            except OSError:
                pass
            continue
        attempt['ok'] = True
        report['ok'] = True
        report['source_url'] = url
        report['error'] = None
        return report

    report['error'] = report['error'] or 'failed to download Playwright browser archive'
    return report


def playwright_install_dry_run(*, env: dict[str, str] | None = None, python_executable: str | None = None, timeout: float | None = None) -> dict[str, Any]:
    env = env or os.environ
    state = playwright_import_state()
    resolved_timeout = resolve_playwright_dry_run_timeout(env=env, timeout=timeout)
    command = [python_executable or sys.executable, '-m', 'playwright', 'install', '--dry-run', 'chromium']
    report: dict[str, Any] = {
        'available': bool(state['available']),
        'module_origin': state['module_origin'],
        'import_error': state['import_error'],
        'command': command,
        'ok': False,
        'returncode': None,
        'stdout': '',
        'stderr': '',
        'packages': [],
        'timeout_seconds': resolved_timeout,
        'timed_out': False,
        'error': None,
    }
    if not state['available']:
        return report
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=resolved_timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        report['timed_out'] = True
        report['stdout'] = exc.stdout or ''
        report['stderr'] = exc.stderr or ''
        report['error'] = f'playwright install --dry-run timed out after {resolved_timeout} seconds'
        return report
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        return report
    report['returncode'] = result.returncode
    report['stdout'] = result.stdout
    report['stderr'] = result.stderr
    report['ok'] = result.returncode == 0
    if result.returncode != 0 and result.stderr:
        report['error'] = result.stderr.strip().splitlines()[-1]
    report['packages'] = parse_playwright_install_dry_run(result.stdout) if result.returncode == 0 else []
    return report


def expected_playwright_browser_packages(*, env: dict[str, str] | None = None, dry_run_report: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    report = dry_run_report if isinstance(dry_run_report, dict) else playwright_install_dry_run(env=env)
    return list(report.get('packages') or [])


def expected_playwright_package(*, package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, env: dict[str, str] | None = None, dry_run_report: dict[str, Any] | None = None) -> dict[str, Any] | None:
    normalized = normalize_playwright_package_name(package_name) or package_name
    for package in expected_playwright_browser_packages(env=env, dry_run_report=dry_run_report):
        if package.get('package_name') == normalized:
            return package
    return None


def local_cft_install_for_version(*, version: str, package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, cft_root: Path | None = None, platform: str | None = None) -> dict[str, Any] | None:
    normalized = normalize_playwright_package_name(package_name) or package_name
    binary = playwright_binary_for_package(normalized)
    for item in local_cft_installations(binary=binary, platform=platform, root=cft_root):
        if item.get('version') == version:
            return item
    return None


def _archive_package_map(archive_paths: Iterable[Path | str], *, platform: str) -> dict[str, Path]:
    package_map: dict[str, Path] = {}
    for raw in archive_paths:
        archive_path = Path(raw).expanduser().resolve()
        package_name = detect_archive_package(archive_path=archive_path, platform=platform)
        if not package_name:
            raise PlaywrightBrowserError(f'could not detect Playwright browser package for archive: {archive_path}')
        if package_name in package_map and package_map[package_name] != archive_path:
            raise PlaywrightBrowserError(f'multiple archives were provided for Playwright package {package_name!r}: {package_map[package_name]} and {archive_path}')
        package_map[package_name] = archive_path
    return package_map


def resolve_sync_playwright_package_names(*, package_names: Iterable[str] | None = None, include_headless_shell: bool = False) -> list[str]:
    resolved: list[str] = []
    for raw in package_names or [PLAYWRIGHT_EXTENSION_PACKAGE]:
        normalized = normalize_playwright_package_name(raw)
        if not normalized:
            raise PlaywrightBrowserError(f'unsupported Playwright browser package: {raw!r}')
        if normalized not in resolved:
            resolved.append(normalized)
    if include_headless_shell and PLAYWRIGHT_HEADLESS_SHELL_PACKAGE not in resolved:
        resolved.append(PLAYWRIGHT_HEADLESS_SHELL_PACKAGE)
    return resolved


def sync_playwright_browser_packages(*, root: Path | None = None, cft_root: Path | None = None, env: dict[str, str] | None = None, platform: str | None = None, package_names: Iterable[str] | None = None, include_headless_shell: bool = False, archive_paths: Iterable[Path | str] | None = None, force: bool = False, expected_packages: Iterable[dict[str, Any]] | None = None, download_missing: bool = False, download_dir: Path | None = None, download_timeout: float | None = None) -> dict[str, Any]:
    base_env = dict(os.environ)
    if env:
        base_env.update(env)
    platform = platform or detect_cft_platform()
    root = (root or playwright_browsers_root(env=base_env)).expanduser()
    root_env = {**base_env, 'PLAYWRIGHT_BROWSERS_PATH': str(root)}
    requested_packages = resolve_sync_playwright_package_names(package_names=package_names, include_headless_shell=include_headless_shell)
    archive_map = _archive_package_map(archive_paths or [], platform=platform)
    expected_packages = list(expected_packages) if expected_packages is not None else expected_playwright_browser_packages(env=root_env)
    expected_by_name = {str(item.get('package_name')): item for item in expected_packages if item.get('package_name')}

    results: list[dict[str, Any]] = []
    ok = True
    changed = False
    for package_name in requested_packages:
        expected = expected_by_name.get(package_name)
        result: dict[str, Any] = {
            'package_name': package_name,
            'package_display_name': playwright_package_spec(package_name)['display_name'],
            'expected_package': expected,
            'archive_path': str(archive_map[package_name]) if package_name in archive_map else None,
            'local_cft_install': None,
            'aligned_install': None,
            'ok': False,
            'changed': False,
            'action': None,
            'notes': [],
        }
        results.append(result)
        notes: list[str] = result['notes']
        if not expected:
            result['action'] = 'missing-expected-package'
            notes.append('Current Playwright dry-run output did not report this package.')
            ok = False
            continue
        aligned_install = latest_local_playwright_browser_install(
            root=root,
            env=root_env,
            platform=platform,
            package_name=package_name,
            expected_install_name=str(expected.get('install_name') or '') or None,
        )
        result['aligned_install'] = aligned_install
        if aligned_install and aligned_install.get('install_name') == expected.get('install_name'):
            marker_state = ensure_playwright_installation_marker(
                Path(str(aligned_install.get('install_dir'))),
                package_name=package_name,
                revision=str(aligned_install.get('revision') or expected.get('revision') or '') or None,
            )
            result['registry_link_state'] = ensure_playwright_registry_link(root)
            result['marker_state'] = marker_state
            result['ok'] = True
            result['action'] = 'already-aligned'
            notes.append(f"Aligned cache already exists at {aligned_install.get('install_name')}.")
            continue

        archive_path = archive_map.get(package_name)
        if archive_path is not None:
            sync_result = install_playwright_browser_archive(
                archive_path=archive_path,
                root=root,
                platform=platform,
                force=force,
                metadata={
                    'version': expected.get('version'),
                    'revision': expected.get('revision'),
                    'source': 'archive-sync',
                },
                package_name=package_name,
                env=root_env,
            )
            result['sync_result'] = sync_result
            result['ok'] = bool(sync_result.get('ok'))
            result['changed'] = not bool(sync_result.get('skipped'))
            result['action'] = 'archive-sync' if result['changed'] else 'archive-sync-skipped'
            changed = changed or result['changed']
            notes.append(f"Imported local archive into {sync_result.get('install_name')}.")
            continue

        local_cft = local_cft_install_for_version(
            version=str(expected.get('version') or ''),
            package_name=package_name,
            cft_root=cft_root.expanduser() if isinstance(cft_root, Path) else cft_root,
            platform=platform,
        )
        result['local_cft_install'] = local_cft
        if local_cft is not None:
            sync_result = import_cft_into_playwright_cache(
                version=str(expected.get('version')),
                cft_root=cft_root,
                playwright_root=root,
                platform=platform,
                force=force,
                package_name=package_name,
                env=root_env,
            )
            result['sync_result'] = sync_result
            result['ok'] = bool(sync_result.get('ok'))
            result['changed'] = not bool(sync_result.get('skipped'))
            result['action'] = 'cft-sync' if result['changed'] else 'cft-sync-skipped'
            changed = changed or result['changed']
            notes.append(f"Imported local Chrome for Testing install into {sync_result.get('install_name')}.")
            continue

        if download_missing:
            download_result = download_playwright_browser_archive(
                expected_package=expected,
                package_name=package_name,
                download_dir=download_dir,
                env=root_env,
                force=force,
                timeout=download_timeout,
            )
            result['download_result'] = download_result
            if download_result.get('ok'):
                try:
                    sync_result = install_playwright_browser_archive(
                        archive_path=Path(str(download_result['archive_path'])),
                        root=root,
                        platform=platform,
                        force=force,
                        metadata={
                            'version': expected.get('version'),
                            'revision': expected.get('revision'),
                            'source': 'download-sync',
                            'download_url': download_result.get('source_url'),
                        },
                        package_name=package_name,
                        env=root_env,
                    )
                except Exception as exc:  # noqa: BLE001
                    result['action'] = 'archive-error'
                    notes.append(f'Downloaded browser archive could not be imported: {exc}')
                    result['error'] = str(exc)
                    ok = False
                else:
                    result['sync_result'] = sync_result
                    result['ok'] = bool(sync_result.get('ok'))
                    result['changed'] = not bool(sync_result.get('skipped'))
                    result['action'] = 'download-sync' if result['changed'] else 'download-sync-skipped'
                    changed = changed or result['changed']
                    notes.append(f"Downloaded Playwright archive from {download_result.get('source_url')} into {sync_result.get('install_name')}.")
                finally:
                    if download_result.get('temporary_archive'):
                        try:
                            Path(str(download_result['archive_path'])).unlink(missing_ok=True)
                        except OSError:
                            pass
                if result['action'] in {'download-sync', 'download-sync-skipped'}:
                    continue
                continue
            else:
                result['action'] = 'download-error'
                notes.append('No matching local archive or same-version local Chrome for Testing install is available, and direct download failed.')
                if download_result.get('error'):
                    notes.append(f"download error: {download_result.get('error')}")
                ok = False
                continue

        result['action'] = 'missing-source'
        notes.append('No matching local archive or same-version local Chrome for Testing install is available for this package.')
        ok = False

    return {
        'ok': ok,
        'changed': changed,
        'root': str(root),
        'platform': platform,
        'requested_packages': requested_packages,
        'expected_packages': expected_packages,
        'results': results,
    }


def ensure_playwright_channel_ready(*, root: Path | None = None, cft_root: Path | None = None, env: dict[str, str] | None = None, platform: str | None = None, include_headless_shell: bool = False, archive_paths: Iterable[Path | str] | None = None, force: bool = False, download_missing: bool = False, download_dir: Path | None = None, download_timeout: float | None = None) -> dict[str, Any]:
    base_env = dict(os.environ)
    if env:
        base_env.update(env)
    platform = platform or detect_cft_platform()
    root = (root or playwright_browsers_root(env=base_env)).expanduser()
    root_env = {**base_env, 'PLAYWRIGHT_BROWSERS_PATH': str(root)}

    raw_install_list = playwright_install_list(env=root_env, root=root, ensure_links=False)
    registry_raw = inspect_playwright_registry(root, platform=platform)
    cache_audit = audit_playwright_cache(root=root, env=root_env, platform=platform, install_list=raw_install_list, registry_report=registry_raw)
    prepared_install_list = playwright_install_list(env=root_env, root=root, ensure_links=True)
    discovered_before = discover_playwright_browser_install(env=root_env, install_list=prepared_install_list)
    repair_plan_before = plan_playwright_cache_repair(root=root, env=root_env, platform=platform, audit_report=cache_audit, install_list=raw_install_list)
    launch_plan_before = playwright_extension_launch_plan(env=root_env, browser_install=discovered_before, repair_plan=repair_plan_before)

    report: dict[str, Any] = {
        'root': str(root),
        'platform': platform,
        'include_headless_shell': include_headless_shell,
        'archive_paths': [str(Path(item)) for item in archive_paths or []],
        'download_missing': download_missing,
        'download_dir': str(download_dir) if download_dir is not None else None,
        'download_timeout': download_timeout,
        'before': {
            'raw_install_list': raw_install_list,
            'registry_raw': registry_raw,
            'cache_audit': cache_audit,
            'repair_plan': repair_plan_before,
            'prepared_install_list': prepared_install_list,
            'discovered_browser_install': discovered_before,
            'extension_launch_plan': launch_plan_before,
        },
        'repair_result': None,
        'sync_result': None,
        'after': None,
        'changed': False,
        'ok': False,
        'already_channel_ready': bool(launch_plan_before.get('channel_ready')),
        'notes': [],
    }
    notes: list[str] = report['notes']

    repair_needed = bool(any((repair_plan_before.get('counts') or {}).values()))
    if repair_needed:
        repair_result = repair_playwright_cache(
            root=root,
            env=root_env,
            platform=platform,
            align_shadow_installs=True,
            prune_broken_links=True,
            write_missing_markers=True,
            apply=True,
        )
        report['repair_result'] = repair_result
        report['changed'] = report['changed'] or bool(repair_result.get('changed'))
        notes.append('Applied Playwright cache repair before package sync.')
    else:
        notes.append('No Playwright cache repair was needed before package sync.')

    sync_result = sync_playwright_browser_packages(
        root=root,
        cft_root=cft_root,
        env=root_env,
        platform=platform,
        package_names=[PLAYWRIGHT_EXTENSION_PACKAGE],
        include_headless_shell=include_headless_shell,
        archive_paths=archive_paths,
        force=force,
        download_missing=download_missing,
        download_dir=download_dir,
        download_timeout=download_timeout,
    )
    report['sync_result'] = sync_result
    report['changed'] = report['changed'] or bool(sync_result.get('changed'))
    notes.append('Ran Playwright package sync for the extension lane.')

    raw_install_list_after = playwright_install_list(env=root_env, root=root, ensure_links=False)
    registry_raw_after = inspect_playwright_registry(root, platform=platform)
    cache_audit_after = audit_playwright_cache(root=root, env=root_env, platform=platform, install_list=raw_install_list_after, registry_report=registry_raw_after)
    prepared_install_list_after = playwright_install_list(env=root_env, root=root, ensure_links=True)
    discovered_after = discover_playwright_browser_install(env=root_env, install_list=prepared_install_list_after)
    repair_plan_after = plan_playwright_cache_repair(root=root, env=root_env, platform=platform, audit_report=cache_audit_after, install_list=raw_install_list_after)
    launch_plan_after = playwright_extension_launch_plan(env=root_env, browser_install=discovered_after, repair_plan=repair_plan_after)
    report['after'] = {
        'raw_install_list': raw_install_list_after,
        'registry_raw': registry_raw_after,
        'cache_audit': cache_audit_after,
        'repair_plan': repair_plan_after,
        'prepared_install_list': prepared_install_list_after,
        'discovered_browser_install': discovered_after,
        'extension_launch_plan': launch_plan_after,
    }
    report['ok'] = bool((report.get('repair_result') or {'ok': True}).get('ok', True)) and bool(sync_result.get('ok')) and bool(launch_plan_after.get('channel_ready'))
    if launch_plan_after.get('channel_ready'):
        notes.append('Playwright persistent extension lane is now channel-ready.')
    else:
        notes.append('Playwright persistent extension lane is still not channel-ready after repair/sync.')
    return report


def local_playwright_browser_installations(*, root: Path | None = None, env: dict[str, str] | None = None, platform: str | None = None, package_name: str | None = None) -> list[dict[str, Any]]:
    root = (root or playwright_browsers_root(env=env)).expanduser()
    platform = platform or detect_cft_platform()
    normalized_package = normalize_playwright_package_name(package_name)
    installs: list[dict[str, Any]] = []
    if not root.exists():
        return installs
    packages = [normalized_package] if normalized_package else list(PLAYWRIGHT_PACKAGE_SPECS)
    for candidate in root.iterdir():
        if not candidate.is_dir():
            continue
        matched_package: str | None = None
        for possible in packages:
            spec = playwright_package_spec(possible)
            if any(candidate.name.startswith(prefix) for prefix in spec['install_prefixes']):
                matched_package = possible
                break
        if not matched_package:
            continue
        executable = candidate / playwright_relpath(matched_package, platform=platform)
        if not executable.exists():
            continue
        metadata_path = candidate / 'install.json'
        marker_path = playwright_installation_marker_path(candidate)
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            try:
                payload = json.loads(metadata_path.read_text(encoding='utf-8'))
                if isinstance(payload, dict):
                    metadata = payload
            except json.JSONDecodeError:
                metadata = {}
        installs.append({
            'browser_name': PLAYWRIGHT_BROWSER_NAME,
            'package_name': matched_package,
            'package_display_name': playwright_package_spec(matched_package)['display_name'],
            'platform': platform,
            'root': str(root),
            'install_name': candidate.name,
            'install_dir': str(candidate),
            'executable': str(executable),
            'metadata_path': str(metadata_path) if metadata_path.exists() else None,
            'marker_path': str(marker_path),
            'marker_exists': marker_path.exists(),
            'marker_required': playwright_installation_marker_required(package_name=matched_package, revision=str(metadata.get('revision') or '') or None),
            'version': metadata.get('version'),
            'revision': metadata.get('revision'),
            'source': metadata.get('source') or 'cache-scan',
            'metadata': metadata,
            'exists': True,
        })
    installs.sort(key=_install_sort_key, reverse=True)
    return installs


def _preferred_install(installs: list[dict[str, Any]], *, expected_install_name: str | None = None) -> dict[str, Any] | None:
    if not installs:
        return None
    if expected_install_name:
        for item in installs:
            if item.get('install_name') == expected_install_name:
                return item
    return installs[0]


def latest_local_playwright_browser_install(*, root: Path | None = None, env: dict[str, str] | None = None, platform: str | None = None, package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, expected_install_name: str | None = None) -> dict[str, Any] | None:
    installs = local_playwright_browser_installations(root=root, env=env, platform=platform, package_name=package_name)
    return _preferred_install(installs, expected_install_name=expected_install_name)


def playwright_browser_choice(browser_install: dict[str, Any] | None, *, launch_plan: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not isinstance(browser_install, dict):
        return None
    plan = launch_plan if isinstance(launch_plan, dict) else None
    strategy = (plan or {}).get('strategy') or browser_install.get('launch_strategy')
    if strategy == 'system-executable' and browser_install.get('system_chromium'):
        return augment_browser_choice({'source': 'system-path', 'path': browser_install.get('system_chromium'), 'exists': Path(str(browser_install.get('system_chromium'))).exists()})
    install = browser_install.get('bundled_install') if isinstance(browser_install.get('bundled_install'), dict) else None
    executable = None
    if isinstance(install, dict):
        executable = install.get('executable')
    if not executable:
        executable = browser_install.get('bundled_executable')
    if not executable:
        return None
    version = None
    source = None
    package_name = None
    notes: list[str] = []
    if isinstance(install, dict):
        version = install.get('version')
        source = install.get('source')
        package_name = install.get('package_name')
    if not version:
        expected = browser_install.get('expected_browser_package') if isinstance(browser_install.get('expected_browser_package'), dict) else None
        if isinstance(expected, dict):
            version = expected.get('version')
    if not source:
        source = 'playwright-cache'
    if not package_name:
        package_name = PLAYWRIGHT_EXTENSION_PACKAGE
    executable_exists = Path(str(executable)).exists()
    if source == 'chrome-for-testing-import':
        choice = augment_browser_choice({'source': 'chrome-for-testing', 'path': executable, 'exists': executable_exists, 'version': version})
        choice.setdefault('native_messaging_notes', [])
        choice['native_messaging_notes'] = list(choice.get('native_messaging_notes') or []) + ['Playwright persistent launch is using a Chrome-for-Testing-imported executable, so native-host install targets must follow that browser family/version instead of assuming Chromium.']
    else:
        choice = {
            'source': 'playwright-bundled',
            'path': str(executable),
            'exists': executable_exists,
            'version': version,
            'browser_family': 'chromium',
            'native_messaging_targets': ['chromium'],
            'native_messaging_primary_target': 'chromium',
            'native_messaging_notes': ['Playwright extension docs recommend the bundled Chromium persistent-context lane for side-loaded extensions.'],
        }
    choice['playwright_package_name'] = package_name
    choice['playwright_launch_strategy'] = strategy
    choice['playwright_install_source'] = source
    if isinstance(install, dict) and install.get('install_name'):
        choice['playwright_install_name'] = install.get('install_name')
    return choice


def discover_playwright_browser_install(*, env: dict[str, str] | None = None, playwright_available: bool | None = None, import_error: str | None = None, module_origin: str | None = None, dry_run: dict[str, Any] | None = None, dry_run_timeout: float | None = None, install_list: dict[str, Any] | None = None, install_list_timeout: float | None = None) -> dict[str, Any]:
    env = env or os.environ
    state = playwright_import_state()
    dry_run_report = dry_run if isinstance(dry_run, dict) else playwright_install_dry_run(env=env, timeout=dry_run_timeout)
    list_report = install_list if isinstance(install_list, dict) else playwright_install_list(env=env, timeout=install_list_timeout)
    browsers_root = existing_playwright_browsers_path(env=env)
    expected_browser_package = next((pkg for pkg in (dry_run_report.get('packages') or []) if pkg.get('package_name') == PLAYWRIGHT_EXTENSION_PACKAGE), None)
    expected_headless_shell_package = next((pkg for pkg in (dry_run_report.get('packages') or []) if pkg.get('package_name') == PLAYWRIGHT_HEADLESS_SHELL_PACKAGE), None)
    latest = latest_local_playwright_browser_install(root=browsers_root, env=env, package_name=PLAYWRIGHT_EXTENSION_PACKAGE, expected_install_name=expected_browser_package.get('install_name') if isinstance(expected_browser_package, dict) else None) if browsers_root else None
    headless_shell_install = latest_local_playwright_browser_install(root=browsers_root, env=env, package_name=PLAYWRIGHT_HEADLESS_SHELL_PACKAGE, expected_install_name=expected_headless_shell_package.get('install_name') if isinstance(expected_headless_shell_package, dict) else None) if browsers_root else None
    system_chromium = shutil.which('chromium') or shutil.which('google-chrome')
    candidate_count = len(local_playwright_browser_installations(root=browsers_root, env=env, package_name=PLAYWRIGHT_EXTENSION_PACKAGE)) if browsers_root else 0
    notes: list[str] = []
    if dry_run_report.get('timed_out'):
        notes.append(f"Playwright dry-run metadata timed out after {dry_run_report.get('timeout_seconds')} seconds; continuing with cache scan and system-browser discovery.")
    elif dry_run_report.get('error') and not dry_run_report.get('ok'):
        notes.append(f"Playwright dry-run metadata was unavailable: {dry_run_report.get('error')}")
    if isinstance(list_report, dict) and isinstance(list_report.get('links_state'), dict) and list_report['links_state'].get('links_dir_created'):
        notes.append(f"Prepared {list_report['links_state'].get('links_dir')} so Playwright install --list can inspect an otherwise empty cache root without failing on ENOENT.")
    if isinstance(list_report, dict) and list_report.get('timed_out'):
        notes.append(f"Playwright install --list timed out after {list_report.get('timeout_seconds')} seconds.")
    elif isinstance(list_report, dict) and list_report.get('error') and not list_report.get('ok'):
        notes.append(f"Playwright install --list was unavailable: {list_report.get('error')}")
    launch_strategy = 'bundled-executable' if latest else ('system-executable' if system_chromium else None)
    report = {
        'available': state['available'] if playwright_available is None else playwright_available,
        'module_origin': state['module_origin'] if module_origin is None else module_origin,
        'import_error': state['import_error'] if import_error is None else import_error,
        'browsers_path': str(browsers_root) if browsers_root else None,
        'bundled_executable': latest.get('executable') if latest else None,
        'bundled_executable_exists': bool(latest and latest.get('executable') and Path(str(latest['executable'])).exists()),
        'bundled_install': latest,
        'headless_shell_install': headless_shell_install,
        'candidate_count': candidate_count,
        'system_chromium': system_chromium,
        'launch_strategy': launch_strategy,
        'dry_run': dry_run_report,
        'install_list': list_report,
        'expected_packages': dry_run_report.get('packages') or [],
        'expected_browser_package': expected_browser_package,
        'expected_headless_shell_package': expected_headless_shell_package,
        'dry_run_timeout_seconds': dry_run_report.get('timeout_seconds'),
        'discovery_notes': notes,
    }
    report['extension_browser_choice'] = playwright_browser_choice(report)
    report['required_native_messaging_targets'] = list((report['extension_browser_choice'] or {}).get('native_messaging_targets') or [])
    return report


def install_playwright_browser_archive(*, archive_path: Path | str, root: Path | None = None, install_name: str | None = None, platform: str | None = None, force: bool = False, metadata: dict[str, Any] | None = None, package_name: str | None = PLAYWRIGHT_EXTENSION_PACKAGE, env: dict[str, str] | None = None) -> dict[str, Any]:
    archive_path = Path(archive_path).expanduser().resolve()
    if not archive_path.exists():
        raise PlaywrightBrowserError(f'archive does not exist: {archive_path}')
    root = (root or playwright_browsers_root(env=env)).expanduser()
    platform = platform or detect_cft_platform()
    resolved_package = normalize_playwright_package_name(package_name)
    if package_name in {None, 'auto'} or resolved_package is None:
        resolved_package = detect_archive_package(archive_path=archive_path, platform=platform)
    if not resolved_package:
        raise PlaywrightBrowserError(f'could not detect Playwright browser package for archive: {archive_path}')
    metadata = dict(metadata or {})
    expected_package = expected_playwright_package(package_name=resolved_package, env=env)
    rel = playwright_relpath(resolved_package, platform=platform)
    install_name = install_name or playwright_install_name(
        package_name=resolved_package,
        revision=str(metadata.get('revision') or '') or None,
        version=str(metadata.get('version') or '') or None,
        label=archive_path.stem,
        expected_install_name=str(expected_package.get('install_name') or '') or None,
    )
    install_dir = root / install_name
    executable = install_dir / rel
    if executable.exists() and not force:
        marker_state = ensure_playwright_installation_marker(install_dir, package_name=resolved_package, revision=str(metadata.get('revision') or '') or None)
        registry_link_state = ensure_playwright_registry_link(install_dir.parent)
        return {
            'ok': True,
            'skipped': True,
            'reason': 'already-installed',
            'package_name': resolved_package,
            'install_name': install_name,
            'install_dir': str(install_dir),
            'executable': str(executable),
            'archive_path': str(archive_path),
            'marker_state': marker_state,
            'registry_link_state': registry_link_state,
        }
    if install_dir.exists() and force:
        shutil.rmtree(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='glasstty-pw-') as tmp_name:
        tmp_dir = Path(tmp_name)
        tmp_archive = tmp_dir / archive_path.name
        shutil.copy2(archive_path, tmp_archive)
        with zipfile.ZipFile(tmp_archive) as archive:
            archive.extractall(install_dir)
    if not executable.exists():
        raise PlaywrightBrowserError(f'imported Playwright browser archive does not contain expected executable: {executable}')
    try:
        executable.chmod(executable.stat().st_mode | 0o111)
    except OSError:
        pass
    metadata_path = install_dir / 'install.json'
    metadata_payload = {
        'browser_name': PLAYWRIGHT_BROWSER_NAME,
        'package_name': resolved_package,
        'binary': playwright_binary_for_package(resolved_package),
        'platform': platform,
        'install_name': install_name,
        'archive_path': str(archive_path),
        'expected_install_name': expected_package.get('install_name') if isinstance(expected_package, dict) else None,
        **metadata,
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2) + '\n', encoding='utf-8')
    marker_state = ensure_playwright_installation_marker(install_dir, package_name=resolved_package, revision=str(metadata_payload.get('revision') or '') or None)
    registry_link_state = ensure_playwright_registry_link(install_dir.parent)
    return {
        'ok': True,
        'skipped': False,
        'package_name': resolved_package,
        'install_name': install_name,
        'install_dir': str(install_dir),
        'executable': str(executable),
        'metadata_path': str(metadata_path),
        'archive_path': str(archive_path),
        'platform': platform,
        'metadata': metadata_payload,
        'marker_state': marker_state,
        'registry_link_state': registry_link_state,
    }


def import_cft_into_playwright_cache(*, version: str = 'latest', cft_root: Path | None = None, playwright_root: Path | None = None, platform: str | None = None, force: bool = False, package_name: str = PLAYWRIGHT_EXTENSION_PACKAGE, env: dict[str, str] | None = None) -> dict[str, Any]:
    platform = platform or detect_cft_platform()
    cft_root = cft_root.expanduser() if isinstance(cft_root, Path) else cft_root
    resolved_package = normalize_playwright_package_name(package_name) or PLAYWRIGHT_EXTENSION_PACKAGE
    source_binary = playwright_binary_for_package(resolved_package)
    if version == 'latest':
        source_install = latest_local_cft_install(binary=source_binary, platform=platform, root=cft_root)
    else:
        source_install = None
        for item in local_cft_installations(binary=source_binary, platform=platform, root=cft_root):
            if item.get('version') == version:
                source_install = item
                break
    if not source_install:
        raise PlaywrightBrowserError(f'no local Chrome for Testing install found for version={version!r} package={resolved_package!r} platform={platform!r}')
    source_dir = Path(str(source_install['install_dir']))
    expected_package = expected_playwright_package(package_name=resolved_package, env=env)
    install_name = playwright_install_name(
        package_name=resolved_package,
        revision=str(source_install.get('revision') or '') or None,
        version=str(source_install.get('version') or '') or None,
        expected_install_name=str(expected_package.get('install_name') or '') or None,
    )
    install_dir = (playwright_root or playwright_browsers_root(env=env)).expanduser() / install_name
    executable = install_dir / playwright_relpath(resolved_package, platform=platform)
    if executable.exists() and not force:
        marker_state = ensure_playwright_installation_marker(install_dir, package_name=resolved_package, revision=str(source_install.get('revision') or '') or None)
        registry_link_state = ensure_playwright_registry_link(install_dir.parent)
        return {
            'ok': True,
            'skipped': True,
            'reason': 'already-installed',
            'package_name': resolved_package,
            'install_name': install_name,
            'install_dir': str(install_dir),
            'executable': str(executable),
            'source_install_dir': str(source_dir),
            'marker_state': marker_state,
            'registry_link_state': registry_link_state,
        }
    if install_dir.exists() and force:
        shutil.rmtree(install_dir)
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, install_dir, dirs_exist_ok=False)
    if not executable.exists():
        raise PlaywrightBrowserError(f'imported Chrome for Testing install did not produce expected executable: {executable}')
    metadata_path = install_dir / 'install.json'
    metadata_payload = {
        'browser_name': PLAYWRIGHT_BROWSER_NAME,
        'package_name': resolved_package,
        'binary': source_binary,
        'platform': platform,
        'install_name': install_name,
        'expected_install_name': expected_package.get('install_name') if isinstance(expected_package, dict) else None,
        'version': source_install.get('version'),
        'revision': source_install.get('revision'),
        'source': 'chrome-for-testing-import',
        'source_install_dir': str(source_dir),
        'source_executable': source_install.get('executable'),
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2) + '\n', encoding='utf-8')
    try:
        executable.chmod(executable.stat().st_mode | 0o111)
    except OSError:
        pass
    marker_state = ensure_playwright_installation_marker(install_dir, package_name=resolved_package, revision=str(metadata_payload.get('revision') or '') or None)
    registry_link_state = ensure_playwright_registry_link(install_dir.parent)
    return {
        'ok': True,
        'skipped': False,
        'package_name': resolved_package,
        'install_name': install_name,
        'install_dir': str(install_dir),
        'executable': str(executable),
        'metadata_path': str(metadata_path),
        'source_install_dir': str(source_dir),
        'platform': platform,
        'metadata': metadata_payload,
        'marker_state': marker_state,
        'registry_link_state': registry_link_state,
    }


def playwright_extension_launch_plan(*, env: dict[str, str] | None = None, browser_install: dict[str, Any] | None = None, repair_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    env = env or os.environ
    browser_install = browser_install or discover_playwright_browser_install(env=env)
    allow_system_executable = bool_from_env(env.get(PLAYWRIGHT_ALLOW_SYSTEM_ENV))
    bundled_install = browser_install.get('bundled_install') if isinstance(browser_install, dict) else None
    expected_browser_package = browser_install.get('expected_browser_package') if isinstance(browser_install, dict) else None
    repair_counts = repair_plan.get('counts') if isinstance(repair_plan, dict) else {}
    repair_apply_command = repair_plan.get('recommended_apply_command') if isinstance(repair_plan, dict) and any((repair_counts or {}).values()) else None
    plan: dict[str, Any] = {
        'available': bool(browser_install.get('available')),
        'import_error': browser_install.get('import_error'),
        'browser_install': browser_install,
        'requires_bundled_chromium': True,
        'requires_playwright_browser_package': True,
        'required_package_name': PLAYWRIGHT_EXTENSION_PACKAGE,
        'recommended_install_command': PLAYWRIGHT_INSTALL_COMMAND,
        'recommended_install_with_deps_command': PLAYWRIGHT_INSTALL_WITH_DEPS_COMMAND,
        'recommended_dry_run_command': PLAYWRIGHT_INSTALL_DRY_RUN_COMMAND,
        'recommended_install_list_command': PLAYWRIGHT_INSTALL_LIST_COMMAND,
        'recommended_import_command': None,
        'recommended_sync_command': PLAYWRIGHT_SYNC_COMMAND,
        'recommended_download_command': PLAYWRIGHT_DOWNLOAD_COMMAND,
        'recommended_sync_with_headless_shell_command': PLAYWRIGHT_SYNC_WITH_HEADLESS_SHELL_COMMAND,
        'recommended_download_with_headless_shell_command': PLAYWRIGHT_DOWNLOAD_WITH_HEADLESS_SHELL_COMMAND,
        'recommended_realign_command': None,
        'recommended_repair_then_sync_command': None,
        'recommended_ensure_channel_ready_command': PLAYWRIGHT_ENSURE_CHANNEL_READY_COMMAND,
        'recommended_ensure_channel_ready_with_headless_shell_command': PLAYWRIGHT_ENSURE_CHANNEL_READY_WITH_HEADLESS_SHELL_COMMAND,
        'recommended_channel_ready_command': None,
        'allow_system_executable': allow_system_executable,
        'strategy': None,
        'channel_ready': False,
        'cache_alignment_status': None,
        'cache_alignment_reason': None,
        'supported': False,
        'risky_fallback': False,
        'skip_reason': None,
        'notes': [],
    }
    notes: list[str] = plan['notes']

    def set_realign_commands(*, primary: str | None = None) -> None:
        repair_then_sync = None
        if repair_apply_command:
            repair_then_sync = f"{repair_apply_command} && {plan['recommended_sync_command']}"
            plan['recommended_repair_then_sync_command'] = repair_then_sync
        ensure_primary = plan.get('recommended_ensure_channel_ready_command') or PLAYWRIGHT_ENSURE_CHANNEL_READY_COMMAND
        plan['recommended_realign_command'] = primary or ensure_primary or repair_apply_command or plan['recommended_sync_command'] or plan['recommended_download_command'] or plan['recommended_install_command'] or plan['recommended_import_command']
        plan['recommended_channel_ready_command'] = ensure_primary or repair_then_sync or plan['recommended_realign_command']

    if not browser_install.get('available'):
        plan['skip_reason'] = 'playwright-unavailable'
        plan['cache_alignment_status'] = 'playwright-unavailable'
        plan['cache_alignment_reason'] = 'Playwright import is unavailable.'
        notes.append('Playwright import is unavailable, so the persistent-context extension lane cannot run.')
        return plan
    if browser_install.get('bundled_executable_exists'):
        aligned_bundle = bool(
            isinstance(expected_browser_package, dict)
            and isinstance(bundled_install, dict)
            and bundled_install.get('package_name') == PLAYWRIGHT_EXTENSION_PACKAGE
            and bundled_install.get('install_name') == expected_browser_package.get('install_name')
        )
        if aligned_bundle:
            plan['strategy'] = 'playwright-channel'
            plan['supported'] = True
            plan['channel_ready'] = True
            plan['channel'] = PLAYWRIGHT_EXTENSION_CHANNEL
            plan['cache_alignment_status'] = 'aligned'
            plan['cache_alignment_reason'] = f"Cached Playwright browser install {expected_browser_package.get('install_name')} matches the current expected package name."
            notes.append('Playwright extension testing will prefer the documented `channel="chromium"` persistent-context lane for headless extension runs when the cache matches the current expected Playwright package.')
            notes.append(f"The cached browser matches the current Playwright package name ({expected_browser_package.get('install_name')}).")
        else:
            plan['strategy'] = 'bundled-executable'
            plan['supported'] = True
            plan['cache_alignment_status'] = 'cache-install-name-drift'
            cached_name = bundled_install.get('install_name') if isinstance(bundled_install, dict) else None
            expected_name = expected_browser_package.get('install_name') if isinstance(expected_browser_package, dict) else None
            if cached_name and expected_name:
                plan['cache_alignment_reason'] = f'Cached Playwright install {cached_name} does not match the current expected package name {expected_name}.'
            else:
                plan['cache_alignment_reason'] = 'A cached Playwright browser is available, but it does not line up with the current expected package identity for the channel-based extension lane.'
            notes.append('Playwright extension testing will launch the cached Playwright browser package directly from the Playwright cache.')
            if isinstance(expected_browser_package, dict) and bundled_install:
                notes.append(f"The cached browser uses {bundled_install.get('install_name')} while current Playwright expects {expected_browser_package.get('install_name')}; GlassTTY will keep using explicit executable_path until the cache is realigned.")
            set_realign_commands(primary=repair_apply_command or plan['recommended_sync_command'] or plan['recommended_download_command'] or plan['recommended_install_command'])
            if plan.get('recommended_channel_ready_command'):
                notes.append(f"Channel-ready cache alignment command: {plan['recommended_channel_ready_command']}")
        if isinstance(bundled_install, dict) and bundled_install.get('source') == 'chrome-for-testing-import':
            notes.append('This cached Playwright browser package was imported from a local Chrome for Testing install, which makes the persistent lane usable even when `python -m playwright install chromium` cannot reach the network.')
        elif isinstance(bundled_install, dict) and bundled_install.get('source') not in {None, 'cache-scan'}:
            notes.append(f"Cached browser source: {bundled_install.get('source')}")
        browser_choice = playwright_browser_choice(browser_install, launch_plan=plan)
        plan['browser_choice'] = browser_choice
        plan['required_native_messaging_targets'] = list((browser_choice or {}).get('native_messaging_targets') or [])
        return plan
    if browser_install.get('system_chromium') and allow_system_executable:
        plan['strategy'] = 'system-executable'
        plan['supported'] = False
        plan['risky_fallback'] = True
        plan['cache_alignment_status'] = 'system-browser-fallback'
        plan['cache_alignment_reason'] = 'GlassTTY is using the opt-in system-browser fallback instead of a Playwright-managed browser package.'
        set_realign_commands(primary=plan['recommended_sync_command'] or plan['recommended_download_command'] or plan['recommended_install_command'])
        notes.append('Using a system Chromium executable for Playwright extension tests is a best-effort fallback and is not the recommended Playwright path for side-loaded extensions.')
        if plan.get('recommended_channel_ready_command'):
            notes.append(f"To return to the documented channel-based extension lane, realign the cache with: {plan['recommended_channel_ready_command']}")
        browser_choice = playwright_browser_choice(browser_install, launch_plan=plan)
        plan['browser_choice'] = browser_choice
        plan['required_native_messaging_targets'] = list((browser_choice or {}).get('native_messaging_targets') or [])
        return plan
    if browser_install.get('system_chromium'):
        plan['skip_reason'] = 'missing-bundled-chromium'
        plan['cache_alignment_status'] = 'missing-bundled-browser'
        plan['cache_alignment_reason'] = 'No Playwright-managed browser package is present yet, so the persistent extension lane would have to fall back to a system browser.'
        notes.append('System Chromium is present, but GlassTTY is skipping the Playwright persistent lane by default because Playwright extension docs recommend the Playwright-managed browser package for side-loaded extensions.')
        notes.append(f'Set {PLAYWRIGHT_ALLOW_SYSTEM_ENV}=1 to attempt the best-effort system-browser fallback anyway.')
        notes.append('If network installs are blocked, align the Playwright cache with a local archive or a same-version local Chrome for Testing install, or try the direct-download sync lane.')
        plan['recommended_import_command'] = 'python scripts/playwright-browsers.py import-cft --package chromium --version latest'
        set_realign_commands(primary=plan['recommended_sync_command'] or plan['recommended_download_command'] or plan['recommended_import_command'] or plan['recommended_install_command'])
        if plan.get('recommended_channel_ready_command'):
            notes.append(f"Channel-ready cache bootstrap command: {plan['recommended_channel_ready_command']}")
        return plan
    plan['skip_reason'] = 'no-playwright-browser'
    plan['cache_alignment_status'] = 'no-playwright-browser'
    plan['cache_alignment_reason'] = 'No cached Playwright browser package or system Chromium executable is available for the persistent extension lane.'
    notes.append('No cached Playwright browser package or system Chromium executable is available for the persistent extension lane.')
    notes.append("The direct-download sync lane can bootstrap the expected Playwright archive when the environment can reach Playwright's browser CDN.")
    plan['recommended_import_command'] = 'python scripts/playwright-browsers.py import-archive --package chromium --archive /path/to/chrome-linux64.zip'
    plan['browser_choice'] = None
    plan['required_native_messaging_targets'] = []
    set_realign_commands(primary=plan['recommended_sync_command'] or plan['recommended_download_command'] or plan['recommended_import_command'] or plan['recommended_install_command'])
    if plan.get('recommended_channel_ready_command'):
        notes.append(f"Channel-ready cache bootstrap command: {plan['recommended_channel_ready_command']}")
    return plan
